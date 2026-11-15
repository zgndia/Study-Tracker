"""JSON-backed persistence for Study Tracker progress and settings."""

import json
import math
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .study_logic import DEFAULT_RATE, MAX_MINUTES


def get_data_dir() -> Path:
    """Return the per-user application data directory."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif os.environ.get("XDG_DATA_HOME"):
        base = Path(os.environ["XDG_DATA_HOME"])
    elif os.name == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    return base / "stdt"


def get_data_file() -> Path:
    return get_data_dir() / "progress.json"


def get_settings_file() -> Path:
    return get_data_dir() / "settings.json"


def _atomic_write_json(destination: Path, data: dict[str, Any]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    temporary.replace(destination)


def save_start_date(start_date: date, path: Path | None = None) -> None:
    """Persist the progression start date as JSON, using an atomic replace."""
    destination = path or get_data_file()
    _atomic_write_json(destination, {"start_date": start_date.isoformat()})


def load_start_date(path: Path | None = None) -> date:
    """Load progress, initializing it to today if no valid save exists."""
    source = path or get_data_file()
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
        return date.fromisoformat(data["start_date"])
    except FileNotFoundError:
        start_date = datetime.now().date()
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        print("Warning: saved progress could not be read; starting from today.")
        start_date = datetime.now().date()
    save_start_date(start_date, source)
    return start_date


def _validated_settings(data: dict[str, Any] | None = None) -> dict[str, int | float]:
    """Return settings merged with defaults and validated for safe use."""
    values: dict[str, Any] = {
        "rate": DEFAULT_RATE,
        "target_minutes": MAX_MINUTES,
    }
    if isinstance(data, dict):
        values.update(data)

    try:
        rate = float(values["rate"])
        target_minutes = int(values["target_minutes"])
    except (TypeError, ValueError, OverflowError):
        return {"rate": DEFAULT_RATE, "target_minutes": MAX_MINUTES}

    if not math.isfinite(rate) or not 0 < rate <= 1 or target_minutes < 1:
        return {"rate": DEFAULT_RATE, "target_minutes": MAX_MINUTES}
    return {"rate": rate, "target_minutes": target_minutes}


def load_settings(path: Path | None = None) -> dict[str, int | float]:
    """Load user settings, falling back to the built-in defaults."""
    source = path or get_settings_file()
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _validated_settings()
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        print("Warning: saved settings could not be read; using default settings.")
        return _validated_settings()
    return _validated_settings(data)


def save_settings(settings: dict[str, Any], path: Path | None = None) -> None:
    """Save validated user settings without changing progression data."""
    validated = _validated_settings(settings)
    # Reject invalid values instead of silently persisting defaults.
    try:
        rate = float(settings["rate"])
        target_minutes = int(settings["target_minutes"])
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Settings must include a valid rate and target_minutes.") from exc
    if not math.isfinite(rate) or not 0 < rate <= 1:
        raise ValueError("Rate must be greater than 0 and no more than 100%.")
    if target_minutes < 1:
        raise ValueError("Target must be at least 1 minute.")

    destination = path or get_settings_file()
    _atomic_write_json(destination, validated)

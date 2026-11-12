"""JSON-backed persistence for Study Tracker progress."""
import json
import os
from datetime import date, datetime
from pathlib import Path


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


def save_start_date(start_date: date, path: Path | None = None) -> None:
    """Persist the progression start date as JSON, using an atomic replace."""
    destination = path or get_data_file()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps({"start_date": start_date.isoformat()}, indent=4) + "\n", encoding="utf-8")
    temporary.replace(destination)


def load_start_date(path: Path | None = None) -> date:
    """Load progress, initializing it to today if no valid save exists."""
    source = path or get_data_file()
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
        return date.fromisoformat(data["start_date"])
    except FileNotFoundError:
        start_date = datetime.now().date()
    except (OSError, ValueError, TypeError, KeyError):
        print("Warning: saved progress could not be read; starting from today.")
        start_date = datetime.now().date()
    save_start_date(start_date, source)
    return start_date

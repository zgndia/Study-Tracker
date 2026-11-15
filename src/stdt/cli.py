"""Command-line interface for stdt."""

import argparse
import os
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

from . import __version__
from .storage import load_settings, load_start_date, save_settings, save_start_date
from .study_logic import (
    QUESTIONS_PER_HOUR,
    format_time,
    get_daily_target,
    get_days_to_target,
    get_intensity,
    get_study_goals,
)

ASCII_FILE = Path(__file__).with_name("ascii.txt")

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _NoColor:
        def __getattr__(self, _name: str) -> str:
            return ""
    Fore = Style = _NoColor()


_ASSIGNMENT_RE = re.compile(r"(?:^|[,;\s]+)([a-zA-Z_][a-zA-Z0-9_-]*)\s*=")
_DURATION_RE = re.compile(r"^(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?$", re.IGNORECASE)


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def get_progress_day(
    start_date: date,
    today: date | None = None,
    target_minutes: int = 360,
    rate: float = 0.06,
) -> int:
    """Return the current day, capped at the day the configured goal is reached."""
    today = today or date.today()
    elapsed_day = max(1, (today - start_date).days + 1)
    return min(elapsed_day, get_days_to_target(target_minutes, rate))


def confirm(prompt: str) -> bool:
    """Ask a Y/n question. Empty input means yes."""
    answer = input(f"{prompt} [Y/n]: ").strip().lower()
    return answer in {"", "y", "yes"}


def draw_progress_bar(percent: int, width: int = 20) -> str:
    percent = max(0, min(100, int(percent)))
    filled = round(width * percent / 100)
    return f"[{'█' * filled}{'░' * (width - filled)}] {percent}%"


def show_dashboard(start_date: date, settings: dict[str, int | float] | None = None) -> None:
    settings = settings or load_settings()
    target_minutes = int(settings["target_minutes"])
    rate = float(settings["rate"])
    today = date.today()
    day = get_progress_day(start_date, today, target_minutes, rate)
    target_day = get_days_to_target(target_minutes, rate)
    lecture_minutes, question_count, question_minutes, total = get_study_goals(
        day, target_minutes=target_minutes, rate=rate
    )
    clear_screen()
    try:
        print(Fore.BLUE + ASCII_FILE.read_text(encoding="utf-8") + Style.RESET_ALL)
    except OSError:
        pass
    width = 58
    print(Fore.CYAN + "╔" + "═" * (width - 2) + "╗")
    print(f"║ {'STUDY TRACKER':<{width - 4}} ║")
    print(f"║ {'Date: ' + today.strftime('%b %d, %Y'):<{width - 4}} ║")
    print("╠" + "═" * (width - 2) + "╣")
    print(f"║ {'Progression day: ' + str(day) + ' / ' + str(target_day):<{width - 4}} ║")
    print("╟" + "─" * (width - 2) + "╢")
    print(f"║ {'TODAY’S STUDY GOAL':<{width - 4}} ║")
    print(f"║ {'Intensity: ' + draw_progress_bar(get_intensity(day, target_minutes, rate)):<{width - 4}} ║")
    print("╟" + "─" * (width - 2) + "╢")
    print(f"║ {'Lectures:  ' + format_time(lecture_minutes):<{width - 4}} ║")
    print(f"║ {'Questions: ' + str(question_count) + ' (' + format_time(question_minutes) + ')':<{width - 4}} ║")
    print(f"║ {'Total:     ' + format_time(total):<{width - 4}} ║")
    print("╚" + "═" * (width - 2) + "╝\n")
    print(f"{Fore.GREEN}[b]{Style.RESET_ALL} Go back one day  {Fore.YELLOW}[r]{Style.RESET_ALL} Reset progress  {Fore.RED}[q]{Style.RESET_ALL} Quit")
    print(f"Settings: maximum {format_time(target_minutes)} per day | rate {rate * 100:g}%")
    print("Going back one day lowers the progression target; it does not erase study history.")


def go_back(start_date: date) -> date:
    settings = load_settings()
    current_day = get_progress_day(
        start_date,
        target_minutes=int(settings["target_minutes"]),
        rate=float(settings["rate"]),
    )
    if current_day <= 1:
        print("You're already on day 1. Progress cannot go back any further.")
        return start_date
    if not confirm(f"Move from day {current_day} back to day {current_day - 1}?"):
        print("Progress unchanged.")
        return start_date
    updated = start_date + timedelta(days=1)
    save_start_date(updated)
    print(f"Progress moved back to day {current_day - 1}.")
    return updated


def reset_progress() -> date | None:
    if not confirm("Reset your progression to day 1? This changes the saved start date."):
        print("Reset cancelled.")
        return None
    new_start = date.today()
    save_start_date(new_start)
    print("Progress reset to day 1.")
    return new_start


def run_menu() -> int:
    start_date = load_start_date()
    settings = load_settings()
    while True:
        show_dashboard(start_date, settings)
        choice = input("\nSelect an option: ").strip().lower()
        if choice in {"q", "quit", "exit"}:
            print("Study Tracker closed.")
            return 0
        if choice in {"b", "back"}:
            start_date = go_back(start_date)
            input("Press Enter to continue...")
        elif choice in {"r", "reset"}:
            updated = reset_progress()
            if updated is not None:
                start_date = updated
            input("Press Enter to continue...")
        else:
            print("Unknown input. Choose b, r, or q.")
            input("Press Enter to continue...")


def parse_rate(value: str) -> float:
    """Parse a rate such as '10%' or '0.1' into a decimal rate."""
    cleaned = value.strip().strip("\"'").strip()
    try:
        rate = float(cleaned[:-1]) / 100 if cleaned.endswith("%") else float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Invalid rate {value!r}. Use a percentage such as 10% or a decimal such as 0.1.") from exc
    if not 0 < rate <= 1:
        raise ValueError("Rate must be greater than 0 and no more than 100% (for example, 10% or 0.1).")
    return rate


def parse_duration(value: str) -> int:
    """Parse durations such as '6h', '6h 30m', '6h, 30m', or '30m'."""
    cleaned = value.strip().strip("\"'").strip().replace(",", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    match = _DURATION_RE.fullmatch(cleaned)
    if not match or not any(part is not None for part in match.groups()):
        raise ValueError(
            f"Invalid target {value!r}. Use hours/minutes such as 6h, 6h 30m, 6h, 30m, or 30m."
        )
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    total = hours * 60 + minutes
    if total < 1:
        raise ValueError("Target must be at least 1 minute.")
    return total


def parse_setting_overrides(tokens: Sequence[str]) -> dict[str, int | float]:
    """Parse one or more key=value overrides from command-line tokens.

    The parser intentionally accepts both comma-separated and space-separated
    assignments, including durations containing spaces or commas.
    """
    text = " ".join(tokens).strip()
    if not text:
        raise ValueError("No settings supplied. Example: stdt -e rate=10%, target=6h.")

    matches = list(_ASSIGNMENT_RE.finditer(text))
    if not matches:
        raise ValueError("Settings must use key=value syntax, for example rate=10% or target=6h.")
    if text[:matches[0].start()].strip(" ,;\t"):
        raise ValueError(f"Unexpected text before the first setting: {text[:matches[0].start()]!r}.")

    parsed: dict[str, int | float] = {}
    for index, match in enumerate(matches):
        key = match.group(1).lower()
        value_start = match.end()
        value_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = text[value_start:value_end].strip(" ,;\t\"'")
        if not value:
            raise ValueError(f"Missing value for setting {key!r}.")
        if key in parsed:
            raise ValueError(f"Setting {key!r} was provided more than once.")
        if key == "rate":
            parsed[key] = parse_rate(value)
        elif key == "target":
            parsed["target_minutes"] = parse_duration(value)
        else:
            raise ValueError(f"Unknown setting {key!r}. Available settings: rate, target.")

    return parsed


def show_settings(settings: dict[str, int | float]) -> None:
    print("Study Tracker settings:")
    print(f"  Study increase rate: {float(settings['rate']) * 100:g}%")
    print(f"  Maximum daily target: {format_time(int(settings['target_minutes']))}")


def edit_settings(tokens: Sequence[str]) -> int:
    try:
        updates = parse_setting_overrides(tokens)
        settings = load_settings()
        settings.update(updates)
        save_settings(settings)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2
    print("Settings updated.")
    show_settings(settings)
    return 0


def show_preview(settings: dict[str, int | float]) -> None:
    """Print the plan through the first day the target is reached."""
    target_minutes = int(settings["target_minutes"])
    rate = float(settings["rate"])
    print("STUDY PLAN PREVIEW")
    print(f"Maximum daily target: {format_time(target_minutes)} | Study increase rate: {rate * 100:g}%")
    final_day = get_days_to_target(target_minutes, rate)
    print(f"Question estimate: {QUESTIONS_PER_HOUR} questions/hour (about {60 / QUESTIONS_PER_HOUR:.1f} minutes each)")
    print()
    header = f"{'Day':>3}  {'Lectures':>9}  {'Questions (time)':>16}  {'Total':>9}"
    print(header)
    print("-" * len(header))
    for day in range(1, final_day + 1):
        lecture_minutes, question_count, question_minutes, total = get_study_goals(
            day, target_minutes=target_minutes, rate=rate
        )
        questions_display = f"{question_count} ({format_time(question_minutes)})"
        print(
            f"{day:>3}  {format_time(lecture_minutes):>9}  "
            f"{questions_display:>16}  {format_time(total):>9}"
        )
    print("\nPreview only. Your saved settings and progression have not been changed.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stdt", description="A terminal-based study tracker.")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("-b", "--back", action="store_true", help="go back one progression day")
    actions.add_argument("-r", "--reset", action="store_true", help="reset progression to day 1")
    actions.add_argument(
        "-e", "--edit", nargs=argparse.REMAINDER, metavar="SETTING=VALUE",
        help='save settings, e.g. stdt -e rate="10%%", target="6h 30m"',
    )
    actions.add_argument(
        "--preview", nargs="*", metavar="SETTING=VALUE",
        help='preview the progression through the target, optionally with temporary overrides, e.g. --preview target="6h"',
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.edit is not None:
        return edit_settings(args.edit)

    if args.preview is not None:
        settings = load_settings()
        if args.preview:
            try:
                settings.update(parse_setting_overrides(args.preview))
            except ValueError as exc:
                print(f"Error: {exc}")
                return 2
        show_preview(settings)
        return 0

    if not args.back and not args.reset:
        return run_menu()

    start_date = load_start_date()
    if args.back:
        go_back(start_date)
    else:
        reset_progress()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

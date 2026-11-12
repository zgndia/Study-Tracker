"""Command-line interface for stdt."""
import argparse
import os
from datetime import date, timedelta
from pathlib import Path

from . import __version__
from .storage import load_start_date, save_start_date
from .study_logic import PROGRESSION_DAYS, format_time, get_intensity, get_study_goals

ASCII_FILE = Path(__file__).with_name("ascii.txt")

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _NoColor:
        def __getattr__(self, _name: str) -> str:
            return ""
    Fore = Style = _NoColor()


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def get_progress_day(start_date: date, today: date | None = None) -> int:
    today = today or date.today()
    return max(1, min(PROGRESSION_DAYS, (today - start_date).days + 1))


def confirm(prompt: str) -> bool:
    """Ask a Y/n question. Empty input means yes."""
    answer = input(f"{prompt} [Y/n]: ").strip().lower()
    return answer in {"", "y", "yes"}


def draw_progress_bar(percent: int, width: int = 20) -> str:
    percent = max(0, min(100, int(percent)))
    filled = round(width * percent / 100)
    return f"[{'█' * filled}{'░' * (width - filled)}] {percent}%"


def show_dashboard(start_date: date) -> None:
    today = date.today()
    day = get_progress_day(start_date, today)
    lecture_minutes, question_count, question_minutes, total = get_study_goals(day)
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
    print(f"║ {'Progression day: ' + str(day) + ' / ' + str(PROGRESSION_DAYS):<{width - 4}} ║")
    print("╟" + "─" * (width - 2) + "╢")
    print(f"║ {'TODAY’S STUDY GOAL':<{width - 4}} ║")
    print(f"║ {'Intensity: ' + draw_progress_bar(get_intensity(day)):<{width - 4}} ║")
    print("╟" + "─" * (width - 2) + "╢")
    print(f"║ {'Lectures:  ' + format_time(lecture_minutes):<{width - 4}} ║")
    print(f"║ {'Questions: ' + str(question_count) + ' (' + format_time(question_minutes) + ')':<{width - 4}} ║")
    print(f"║ {'Total:     ' + format_time(total):<{width - 4}} ║")
    print("╚" + "═" * (width - 2) + "╝\n")
    print(f"{Fore.GREEN}[b]{Style.RESET_ALL} Go back one day  {Fore.YELLOW}[r]{Style.RESET_ALL} Reset progress  {Fore.RED}[q]{Style.RESET_ALL} Quit")
    print("Going back one day lowers the progression target; it does not erase study history.")


def go_back(start_date: date) -> date:
    current_day = get_progress_day(start_date)
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
    while True:
        show_dashboard(start_date)
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stdt", description="A terminal-based study tracker.")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("-b", "--back", action="store_true", help="go back one progression day")
    actions.add_argument("-r", "--reset", action="store_true", help="reset progression to day 1")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.back and not args.reset:
        return run_menu()
    start_date = load_start_date()
    if args.back:
        go_back(start_date)
    else:
        reset_progress()
    return 0

"""Terminal-based Study Tracker."""

import os
from datetime import datetime, timedelta
from pathlib import Path

from study_logic import MAX_MINUTES, PROGRESSION_DAYS, get_intensity, get_study_goals, format_time

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _NoColor:
        def __getattr__(self, _name):
            return ""
    Fore = Style = _NoColor()


# Set this to datetime(YEAR, MONTH, DAY) to enable an exam countdown.
EXAM_DATE = None

STATE_DIR = Path.home() / "Documents" / "Python" / "Studying"
STATE_FILE = STATE_DIR / "streak_date.txt"
ASCII_FILE = Path(__file__).with_name("ascii.txt")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def load_ascii():
    try:
        return ASCII_FILE.read_text(encoding="utf-8")
    except OSError:
        return ""


def load_start_date():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            return datetime.strptime(STATE_FILE.read_text(encoding="utf-8").strip(), "%Y-%m-%d")
        except (ValueError, OSError):
            print("Saved progress could not be read; starting from today.")
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    save_start_date(start)
    return start


def save_start_date(start_date):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(start_date.strftime("%Y-%m-%d"), encoding="utf-8")


def get_progress_day(start_date, today=None):
    today = today or datetime.now()
    elapsed = (today.date() - start_date.date()).days
    return max(1, min(PROGRESSION_DAYS, elapsed + 1))


def format_exam_countdown(today):
    if EXAM_DATE is None:
        return "No exam date configured"
    days = (EXAM_DATE.date() - today.date()).days
    if days < 0:
        return "Exam date has passed"
    if days == 0:
        return "Exam is today"
    return f"{days} days until exam"


def draw_progress_bar(percent, width=20):
    percent = max(0, min(100, int(percent)))
    filled = round(width * percent / 100)
    return f"[{'█' * filled}{'░' * (width - filled)}] {percent}%"


def show_dashboard(start_date):
    today = datetime.now()
    day = get_progress_day(start_date, today)
    lecture_minutes, question_count, question_minutes, total = get_study_goals(day)
    intensity = get_intensity(day)

    clear_screen()
    ascii_art = load_ascii()
    if ascii_art:
        print(Fore.BLUE + ascii_art + Style.RESET_ALL)

    width = 58
    print(Fore.CYAN + "╔" + "═" * (width - 2) + "╗")
    print(f"║ {'STUDY TRACKER':<{width - 4}} ║")
    print(f"║ {'Date: ' + today.strftime('%b %d, %Y'):<{width - 4}} ║")
    print("╠" + "═" * (width - 2) + "╣")
    print(f"║ {'Progression day: ' + str(day) + ' / ' + str(PROGRESSION_DAYS):<{width - 4}} ║")
    print(f"║ {'Exam: ' + format_exam_countdown(today):<{width - 4}} ║")
    print("╟" + "─" * (width - 2) + "╢")
    print(f"║ {'TODAY’S STUDY GOAL':<{width - 4}} ║")
    print(f"║ {'Intensity: ' + draw_progress_bar(intensity):<{width - 4}} ║")
    print("╟" + "─" * (width - 2) + "╢")
    print(f"║ {'Lectures:  ' + format_time(lecture_minutes):<{width - 4}} ║")
    print(f"║ {'Questions: ' + str(question_count) + ' (' + format_time(question_minutes) + ')':<{width - 4}} ║")
    print(f"║ {'Total:     ' + format_time(total):<{width - 4}} ║")
    print("╚" + "═" * (width - 2) + "╝")
    print()
    print(f"{Fore.GREEN}[b]{Style.RESET_ALL} Go back one day  "
          f"{Fore.YELLOW}[r]{Style.RESET_ALL} Reset progress  "
          f"{Fore.RED}[q]{Style.RESET_ALL} Quit")
    print("Going back one day lowers the progression target by one day; it does not erase study history.")


def rollback_one_day(start_date):
    current_day = get_progress_day(start_date)
    if current_day <= 1:
        print("You're already on day 1. Progress cannot go back any further.")
        input("Press Enter to continue...")
        return start_date

    answer = input(
        f"Move from day {current_day} back to day {current_day - 1}? [y/N]: "
    ).strip().lower()
    if answer not in {"y", "yes"}:
        print("Progress unchanged.")
        input("Press Enter to continue...")
        return start_date

    # Moving the start date forward by one day makes the derived progression day
    # decrease by one. This persists across restarts and can be repeated.
    updated_start = start_date + timedelta(days=1)
    save_start_date(updated_start)
    print(f"Progress moved back to day {current_day - 1}.")
    input("Press Enter to continue...")
    return updated_start


def reset_progress():
    answer = input("Reset your progression to day 1? This changes the saved start date. [y/N]: ").strip().lower()
    if answer in {"y", "yes"}:
        new_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        save_start_date(new_start)
        print("Progress reset to day 1.")
        input("Press Enter to continue...")
        return new_start
    print("Reset cancelled.")
    input("Press Enter to continue...")
    return None


def main():
    start_date = load_start_date()
    while True:
        show_dashboard(start_date)
        choice = input("\nSelect an option: ").strip().lower()

        if choice in {"q", "quit", "exit"}:
            print("Study Tracker closed.")
            break
        if choice in {"b", "back"}:
            start_date = rollback_one_day(start_date)
        elif choice in {"r", "reset"}:
            updated = reset_progress()
            if updated is not None:
                start_date = updated
        else:
            print("Unknown option. Choose b, r, or q.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()

"""Interactive study-goal forecaster."""

from .storage import load_settings
from .study_logic import format_time, get_days_to_target, get_intensity, get_study_goals


def main() -> int:
    settings = load_settings()
    target_minutes = int(settings["target_minutes"])
    rate = float(settings["rate"])
    final_day = get_days_to_target(target_minutes, rate)
    print("--- STUDY GOAL FORECASTER ---")
    print(f"Progression reaches its {format_time(target_minutes)} maximum on day {final_day}.")
    print(f"Current study increase rate: {rate * 100:g}%.")
    print(f"Enter a day number from 1 to {final_day}. Type 'q' to close.\n")
    while True:
        value = input("Target Day > ").strip().lower()
        if value in {"q", "quit", "exit"}:
            print("Forecaster closed.")
            return 0
        try:
            day = int(value)
        except ValueError:
            print("Invalid input. Please enter a whole number.")
            continue
        if not 1 <= day <= final_day:
            print(f"Please enter a day between 1 and {final_day}.")
            continue
        lecture_minutes, question_count, question_minutes, total = get_study_goals(
            day, target_minutes=target_minutes, rate=rate
        )
        print(f"\n[ RESULTS FOR DAY {day} ]")
        print(f"Intensity: {get_intensity(day, target_minutes, rate)}%")
        print(f"Lectures:  {format_time(lecture_minutes)}")
        print(f"Questions: {question_count} ({format_time(question_minutes)})")
        print(f"Total:     {format_time(total)}")
        print("-" * 30 + "\n")


if __name__ == "__main__":
    raise SystemExit(main())

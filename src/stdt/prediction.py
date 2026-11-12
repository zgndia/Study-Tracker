"""Interactive study-goal forecaster."""

from .study_logic import PROGRESSION_DAYS, format_time, get_intensity, get_study_goals


def main() -> int:
    print("--- STUDY GOAL FORECASTER ---")
    print(f"Progression reaches its 6-hour maximum on day {PROGRESSION_DAYS}.")
    print(f"Enter a day number from 1 to {PROGRESSION_DAYS}. Type 'q' to close.\n")

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
        if not 1 <= day <= PROGRESSION_DAYS:
            print(f"Please enter a day between 1 and {PROGRESSION_DAYS}.")
            continue
        lecture_minutes, question_count, question_minutes, total = get_study_goals(day)
        print(f"\n[ RESULTS FOR DAY {day} ]")
        print(f"Intensity: {get_intensity(day)}%")
        print(f"Lectures:  {format_time(lecture_minutes)}")
        print(f"Questions: {question_count} questions ({format_time(question_minutes)})")
        print(f"Total:     {format_time(total)}")
        print("-" * 30 + "\n")


if __name__ == "__main__":
    raise SystemExit(main())

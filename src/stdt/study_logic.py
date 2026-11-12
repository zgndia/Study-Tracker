"""Study-goal progression calculations."""
import math

PROGRESSION_DAYS = 60
START_MINUTES = 28
MAX_MINUTES = 360
LOGISTIC_RATE = 0.06
LOGISTIC_MIDPOINT = 35


def _logistic(day: int) -> float:
    return 1.0 / (1.0 + math.exp(-LOGISTIC_RATE * (day - LOGISTIC_MIDPOINT)))


_START_CURVE = _logistic(1)
_END_CURVE = _logistic(PROGRESSION_DAYS)


def get_daily_target(day: int) -> int:
    """Return the target study minutes for a progression day (1..60)."""
    day = max(1, min(int(day), PROGRESSION_DAYS))
    if day == 1:
        return START_MINUTES
    if day == PROGRESSION_DAYS:
        return MAX_MINUTES
    progress = (_logistic(day) - _START_CURVE) / (_END_CURVE - _START_CURVE)
    target = START_MINUTES + progress * (MAX_MINUTES - START_MINUTES)
    return max(START_MINUTES, min(MAX_MINUTES, round(target)))


def get_study_goals(day: int) -> tuple[int, int, int, int]:
    """Return (lecture_minutes, question_count, question_minutes, total)."""
    total = get_daily_target(day)
    if day <= 1:
        return 15, 5, 13, 28
    question_minutes = round(total * (8.325 / 18.325))
    lecture_minutes = total - question_minutes
    question_count = round(question_minutes / 2.5)
    return lecture_minutes, question_count, question_minutes, total


def get_intensity(day: int) -> int:
    """Return the daily target as a percentage of the six-hour ceiling."""
    return round(get_daily_target(day) / MAX_MINUTES * 100)


def format_time(total_minutes: int) -> str:
    hours, minutes = divmod(int(total_minutes), 60)
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"

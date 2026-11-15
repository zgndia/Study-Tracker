"""Study-goal progression calculations."""

import math

# Kept as a compatibility constant for integrations built against older
# versions. Progression is no longer limited to 60 days; its length depends
# on the configured rate and target.
PROGRESSION_DAYS = 60
START_MINUTES = 28
MAX_MINUTES = 360
DEFAULT_RATE = 0.06
# Backwards-compatible name retained for callers that imported it directly.
LOGISTIC_RATE = DEFAULT_RATE

# Planning estimate: one question takes about 1.2 minutes on average.
QUESTIONS_PER_HOUR = 50
QUESTION_TIME_SHARE = 1 / 3


def get_daily_target(
    day: int,
    target_minutes: int = MAX_MINUTES,
    rate: float = DEFAULT_RATE,
) -> int:
    """Return the daily study target for ``day`` using compound growth.

    Day one starts at 28 minutes (or at the configured ceiling when that is
    lower). Each day thereafter compounds the previous day's unrounded target:

        study_time = study_time + (rate * study_time)

    This is equivalent to ``start * (1 + rate) ** (day - 1)``. The value is
    rounded to the nearest minute for display and capped at the configured
    target. The progression is not restricted to a fixed number of days.
    """
    day = max(1, int(day))
    target_minutes = max(1, int(target_minutes))
    rate = float(rate)
    if not math.isfinite(rate) or rate < 0:
        raise ValueError("Rate must be a finite, non-negative number.")

    start_minutes = min(START_MINUTES, target_minutes)
    if day == 1 or start_minutes >= target_minutes or rate == 0:
        return start_minutes

    try:
        exact_target = start_minutes * math.pow(1.0 + rate, day - 1)
    except OverflowError:
        return target_minutes
    if exact_target >= target_minutes:
        return target_minutes
    return max(start_minutes, round(exact_target))


def get_days_to_target(
    target_minutes: int = MAX_MINUTES,
    rate: float = DEFAULT_RATE,
) -> int:
    """Return the first progression day whose displayed target reaches goal."""
    target_minutes = max(1, int(target_minutes))
    rate = float(rate)
    start_minutes = min(START_MINUTES, target_minutes)
    if start_minutes >= target_minutes:
        return 1
    if not math.isfinite(rate) or rate <= 0:
        raise ValueError("Rate must be a finite number greater than zero.")

    # Estimate the exact mathematical crossing, then adjust for minute
    # rounding so that the returned day is the first day shown at the goal.
    crossing = math.ceil(math.log(target_minutes / start_minutes) / math.log1p(rate)) + 1
    day = max(1, crossing)
    while day > 1 and get_daily_target(day - 1, target_minutes, rate) >= target_minutes:
        day -= 1
    while get_daily_target(day, target_minutes, rate) < target_minutes:
        day += 1
    return day


def get_study_goals(
    day: int,
    target_minutes: int = MAX_MINUTES,
    rate: float = DEFAULT_RATE,
) -> tuple[int, int, int, int]:
    """Return (lecture_minutes, question_count, question_minutes, total)."""
    day = max(1, int(day))
    total = get_daily_target(day, target_minutes=target_minutes, rate=rate)

    # Preserve the initial onboarding split used by the original schedule.
    if day == 1 and target_minutes >= START_MINUTES:
        return 15, 5, 13, total

    question_minutes = round(total * QUESTION_TIME_SHARE)
    lecture_minutes = total - question_minutes
    question_count = round(question_minutes * QUESTIONS_PER_HOUR / 60)
    return lecture_minutes, question_count, question_minutes, total


def get_intensity(
    day: int,
    target_minutes: int = MAX_MINUTES,
    rate: float = DEFAULT_RATE,
) -> int:
    """Return the daily target as a percentage of the configured ceiling."""
    ceiling = max(1, int(target_minutes))
    return round(get_daily_target(day, ceiling, rate) / ceiling * 100)


def format_time(total_minutes: int) -> str:
    """Format a minute count as a readable hours/minutes string."""
    hours, minutes = divmod(int(total_minutes), 60)
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"

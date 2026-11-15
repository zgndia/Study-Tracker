"""A small terminal-based study tracker."""

__version__ = "1.0.0"

from .storage import (
    get_data_dir,
    get_data_file,
    get_settings_file,
    load_settings,
    load_start_date,
    save_settings,
    save_start_date,
)
from .study_logic import (
    MAX_MINUTES,
    PROGRESSION_DAYS,
    QUESTIONS_PER_HOUR,
    format_time,
    get_daily_target,
    get_days_to_target,
    get_intensity,
    get_study_goals,
)

get_start_date = load_start_date

__all__ = [
    "MAX_MINUTES",
    "PROGRESSION_DAYS",
    "QUESTIONS_PER_HOUR",
    "format_time",
    "get_daily_target",
    "get_days_to_target",
    "get_data_dir",
    "get_data_file",
    "get_settings_file",
    "get_intensity",
    "get_start_date",
    "get_study_goals",
    "load_settings",
    "load_start_date",
    "save_settings",
    "save_start_date",
]

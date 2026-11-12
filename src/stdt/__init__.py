"""A small terminal-based study tracker."""
__version__ = "1.0.0"

from .storage import get_data_dir, get_data_file, load_start_date, save_start_date
from .study_logic import MAX_MINUTES, PROGRESSION_DAYS, format_time, get_daily_target, get_intensity, get_study_goals

get_start_date = load_start_date

__all__ = [
    "MAX_MINUTES", "PROGRESSION_DAYS", "format_time", "get_daily_target",
    "get_data_dir", "get_data_file", "get_intensity", "get_start_date",
    "get_study_goals", "load_start_date", "save_start_date",
]

# Study Tracker

A terminal-based study tracker with a gradual 60-day study-goal progression.

## Requirements

- Python 3.10 or newer
- No required third-party packages (colors are optional; install with `python -m pip install colorama`)

## Run

```bash
python study.py
```

Forecast a specific day:

```bash
python studyprediction.py
```

## Progression

- Day 1 starts at 28 minutes.
- The daily target follows a normalized logistic curve.
- Day 60 reaches the 360-minute (6-hour) ceiling.
- Intensity is the daily target divided by 360 minutes.

## Progress controls

- `b`: Move progression back by one day. Confirm with `y` to lower the target for the current day. This can be repeated, but never moves earlier than day 1.
- `r`: Reset progression to day 1.
- `q`: Quit.

Progress is saved in `~/Documents/Python/Studying/streak_date.txt` (the folder is created automatically). The `ascii.txt` file is loaded from the project folder.

The exam countdown is disabled by default because the original repository's hardcoded exam date had already passed. Set `EXAM_DATE` in `study.py` to a future `datetime(YEAR, MONTH, DAY)` to enable it.

# stdt — Study Tracker

A lightweight, installable terminal study tracker. It preserves the original 60-day normalized logistic progression and stores progress in a per-user JSON file.

## Requirements

- Python 3.10 or newer
- No required third-party dependencies
- Optional colors: `py -m pip install "stdt[color]"`

## Install on Windows

Extract the project, open a terminal in its folder, and run:

```powershell
py -m pip install --user .
```

This installs the `stdt` command into your user Python Scripts directory. To make it callable from any terminal location, ensure that directory is on your Windows PATH. You can find your user base with `py -m site --user-base`; the Scripts directory is the `Scripts` folder inside that location. Add that full path to your user PATH once, then reopen your terminal.

For development, use `py -m pip install --user -e .` instead.

## Commands

```text
stdt              Open the interactive main menu
stdt -b            Go back one progression day
stdt --back        Same as -b
stdt -r            Reset progression to day 1
stdt --reset       Same as -r
stdt --version     Print installed version
stdt --help        Show command help
stdt-predict       Open the original study-goal forecaster
```

Both `--back` and `--reset` ask for confirmation with `[Y/n]`. Press **Enter** or type `y` to confirm; type `n` to cancel. Yes is the default. The interactive menu also supports `b`, `r`, and `q`.

## Data location

On Windows, progress is stored at `%APPDATA%\\stdt\\progress.json` (typically `C:\\Users\\<you>\\AppData\\Roaming\\stdt\\progress.json`). On macOS it is stored in `~/Library/Application Support/stdt/progress.json`. On Linux it uses `$XDG_DATA_HOME/stdt/progress.json`, falling back to `~/.local/share/stdt/progress.json`.

Example JSON:

```json
{
    "start_date": "2026-11-12"
}
```

## Import from Python

```python
import stdt

print(stdt.get_daily_target(10))
print(stdt.get_study_goals(10))
print(stdt.get_data_file())
print(stdt.load_start_date())
```

## Progression

- Day 1 starts at 28 minutes.
- The daily target follows a normalized logistic curve.
- Day 60 reaches the 360-minute (6-hour) ceiling.
- Intensity is the daily target divided by 360 minutes.

"""Generate the default study-time progression graph with Matplotlib.

Run from the repository root:
    python scripts/generate_progression_graph.py
"""

from pathlib import Path
import sys

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stdt.study_logic import DEFAULT_RATE, MAX_MINUTES, format_time, get_daily_target, get_days_to_target


def main() -> None:
    final_day = get_days_to_target(MAX_MINUTES, DEFAULT_RATE)
    days = list(range(1, final_day + 1))
    study_hours = [get_daily_target(day, MAX_MINUTES, DEFAULT_RATE) / 60 for day in days]

    figure, axis = plt.subplots(figsize=(10, 5.5))
    axis.plot(days, study_hours, marker="o", markersize=3, linewidth=2)
    axis.set_title("Study Time Progression — Default Settings")
    axis.set_xlabel("Day")
    axis.set_ylabel("Daily study time (hours)")
    axis.set_xlim(1, final_day)
    axis.set_ylim(0, MAX_MINUTES / 60 * 1.08)
    axis.grid(True, alpha=0.3)
    axis.annotate(
        f"Target reached: {format_time(MAX_MINUTES)} on day {final_day}",
        xy=(final_day, MAX_MINUTES / 60),
        xytext=(-12, -28),
        textcoords="offset points",
        ha="right",
        va="top",
    )
    figure.tight_layout()

    output = ROOT / "docs" / "default_progression.png"
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)
    print(f"Generated {output.relative_to(ROOT)}")
    print(f"Defaults: {DEFAULT_RATE:.0%} daily compound growth, {format_time(MAX_MINUTES)} maximum, {final_day} days")


if __name__ == "__main__":
    main()

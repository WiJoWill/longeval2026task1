"""Plot a cleaner timeline for the selected 2/5/1 threshold option."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "adaptive_monitor" / "outputs" / "threshold_search" / "option_c_2_5_1_timeline.png"

UPDATE_WEEKS = [
    "2025-05-12",
    "2025-05-19",
    "2025-06-02",
    "2025-06-09",
    "2025-06-16",
    "2025-06-30",
    "2025-07-07",
    "2025-10-13",
]

UPDATE_REASON_LABELS = {
    "2025-05-12": "V",
    "2025-05-19": "V",
    "2025-06-02": "V",
    "2025-06-09": "V",
    "2025-06-16": "V",
    "2025-06-30": "V",
    "2025-07-07": "V",
    "2025-10-13": "S+V",
}

SNAPSHOT_PERIODS = [
    ("Snapshot 1", "2025-03-01", "2025-05-31", "#F3F4F6"),
    ("Snapshot 2", "2025-06-01", "2025-08-31", "#E0F2FE"),
    ("Snapshot 3", "2025-09-01", "2025-11-30", "#ECFCCB"),
]

THRESHOLD_LABELS = [
    "staleness = 0.80",
    "coverage = 0.03",
    "temp gap = 20d",
    "velocity = 3.0x",
    "baseline = 4w",
]


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def _snapshot_name(date_str: str) -> str:
    for name, start, end, _ in SNAPSHOT_PERIODS:
        if start <= date_str <= end:
            return name
    return "Outside"


def main() -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available; skipping plot generation")
        return

    update_dates = [_parse_date(value) for value in UPDATE_WEEKS]
    counts = Counter(_snapshot_name(value) for value in UPDATE_WEEKS)

    fig = plt.figure(figsize=(14, 6.2), facecolor="#FCFCF9")
    ax = fig.add_axes([0.07, 0.20, 0.86, 0.55], facecolor="#FCFCF9")

    for name, start, end, color in SNAPSHOT_PERIODS:
        ax.axvspan(_parse_date(start), _parse_date(end), ymin=0.16, ymax=0.84, color=color, ec="none", zorder=0)

    baseline_y = 0.5
    ax.hlines(baseline_y, _parse_date("2025-03-01"), _parse_date("2025-11-30"), color="#1F2937", linewidth=1.6, zorder=1)

    for i, dt in enumerate(update_dates):
        date_key = UPDATE_WEEKS[i]
        y = baseline_y + (0.11 if i % 2 == 0 else -0.11)
        ax.vlines(dt, baseline_y, y, color="#FB7185", linewidth=1.6, zorder=2)
        ax.scatter(dt, y, s=90, color="#FB7185", edgecolor="#ffffff", linewidth=1.8, zorder=3)
        ax.text(
            dt,
            y + (0.055 if y > baseline_y else -0.07),
            dt.strftime("%b %d"),
            ha="center",
            va="center",
            fontsize=9,
            color="#111827",
            zorder=4,
        )
        ax.text(
            dt,
            baseline_y,
            UPDATE_REASON_LABELS[date_key],
            ha="center",
            va="center",
            fontsize=8.5,
            color="#ffffff",
            weight="bold",
            bbox={"boxstyle": "round,pad=0.22", "facecolor": "#0F172A", "edgecolor": "#0F172A"},
            zorder=5,
        )

    for name, start, end, _ in SNAPSHOT_PERIODS:
        midpoint = _parse_date(start) + (_parse_date(end) - _parse_date(start)) / 2
        ax.text(
            midpoint,
            0.82,
            f"{name}\n{counts.get(name, 0)} updates",
            ha="center",
            va="center",
            fontsize=12,
            color="#0F172A",
            weight="bold",
        )

    ax.set_ylim(0.18, 0.88)
    ax.set_yticks([])
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#CBD5E1")
    ax.tick_params(axis="x", labelsize=10, colors="#475569")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_xlim(_parse_date("2025-03-01"), _parse_date("2025-11-30"))

    fig.text(0.07, 0.90, "Adaptive Update Timeline", fontsize=22, weight="bold", color="#0F172A")

    chip_x = 0.07
    for label in THRESHOLD_LABELS:
        fig.text(
            chip_x,
            0.10,
            label,
            fontsize=9.5,
            color="#334155",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "#F8FAFC", "edgecolor": "#CBD5E1"},
        )
        chip_x += 0.12 if "velocity" not in label else 0.11

    fig.text(
        0.07,
        0.045,
        "Update weeks: May 12, May 19, Jun 02, Jun 09, Jun 16, Jun 30, Jul 07, Oct 13",
        fontsize=10,
        color="#475569",
    )
    fig.text(
        0.07,
        0.015,
        "Reason codes: V = velocity trigger, S+V = stale coverage plus velocity trigger",
        fontsize=9.5,
        color="#64748B",
    )

    fig.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

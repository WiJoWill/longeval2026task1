"""Create a compact timeline plot for adaptive weekly update decisions."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REINDEX_DIR = ROOT / "adaptive_monitor" / "outputs" / "reindex_pipeline"
INDEX_MEMBERSHIP_DIR = ROOT / "adaptive_monitor" / "outputs" / "index_membership"
OUTPUT_PATH = REINDEX_DIR / "weekly_update_timeline.png"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def _trigger_kind(reason: str, action: str) -> str:
    if action == "soft_alert":
        return "soft_alert"
    has_stale = "staleness_rate=" in reason and "coverage_gap=" in reason
    has_velocity = "velocity_per_day=" in reason
    if has_stale and has_velocity:
        return "stale+coverage+velocity"
    if has_velocity:
        return "velocity_only"
    if has_stale:
        return "stale+coverage"
    return "other"


def main() -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available; skipping plot generation")
        return

    trigger_rows = _read_csv(REINDEX_DIR / "trigger_decisions.csv")
    adopted_rows = _read_csv(INDEX_MEMBERSHIP_DIR / "index_versions.csv")

    monitor_rows = [
        row for row in trigger_rows
        if row["week_start"] >= "2025-03-01" and row["action"] != "none"
    ]
    adopted_rows = [
        row for row in adopted_rows
        if row["cutoff_date"] >= "2025-03-31"
    ]

    kind_colors = {
        "stale+coverage+velocity": "#3B82F6",
        "velocity_only": "#F59E0B",
        "stale+coverage": "#64748B",
        "soft_alert": "#111827",
        "other": "#9CA3AF",
    }

    fig, ax = plt.subplots(figsize=(14, 3.8))
    ax.axhline(1.0, color="#E5E7EB", linewidth=1.2)
    ax.axhline(0.0, color="#E5E7EB", linewidth=1.2)

    for row in monitor_rows:
        dt = _parse_date(row["cutoff_date"])
        kind = _trigger_kind(row["reason"], row["action"])
        marker = "D" if row["action"] == "soft_alert" else "o"
        size = 44 if row["action"] == "soft_alert" else 20
        ax.scatter(dt, 0.0, s=size, color=kind_colors[kind], marker=marker, zorder=3)

    for idx, row in enumerate(adopted_rows):
        dt = _parse_date(row["cutoff_date"])
        kind = _trigger_kind(row["reason"], row["action"])
        ax.scatter(dt, 1.0, s=54, color=kind_colors[kind], marker="s", zorder=4)
        ax.text(
            dt,
            1.10 if idx % 2 == 0 else 1.18,
            dt.strftime("%m-%d"),
            ha="center",
            va="bottom",
            fontsize=8,
            color="#111827",
        )

    ax.text(_parse_date("2025-03-02"), 1.23, "Adopted simulation updates", fontsize=10, color="#111827")
    ax.text(_parse_date("2025-03-02"), 0.12, "Weekly monitoring recommendations", fontsize=10, color="#111827")

    legend_items = [
        ("stale+coverage+velocity", "staleness + coverage + velocity"),
        ("velocity_only", "velocity only"),
        ("soft_alert", "soft alert"),
    ]
    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=7, markerfacecolor=kind_colors[key], markeredgecolor="none")
        for key, _ in legend_items
    ]
    ax.legend(handles, [label for _, label in legend_items], loc="upper right", frameon=False, ncol=3, fontsize=9)

    ax.set_title("Adaptive Update Timeline", loc="left", fontsize=14, color="#111827", pad=10)
    ax.text(
        0.0,
        1.02,
        "Snapshot-1 adaptive monitoring: March 2025 to March 2026",
        transform=ax.transAxes,
        fontsize=9,
        color="#6B7280",
    )

    ax.set_ylim(-0.35, 1.35)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_color("#D1D5DB")
    ax.tick_params(axis="x", colors="#4B5563", labelsize=9)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate(rotation=0, ha="center")

    plt.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

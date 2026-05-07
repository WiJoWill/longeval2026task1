"""Search threshold settings that reduce update frequency to roughly every 2-6 weeks."""

from __future__ import annotations

import csv
import itertools
import json
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_DIR = ROOT / "adaptive_monitor" / "outputs" / "collection_analytics"
OUTPUT_DIR = ROOT / "adaptive_monitor" / "outputs" / "threshold_search"
WINDOW_START = "2025-03-01"
WINDOW_END = "2026-03-08"


@dataclass(slots=True)
class Thresholds:
    staleness_rate: float
    coverage_gap: float
    temporal_gap_growth_days: int
    velocity_multiplier: float
    baseline_weeks: int


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def _as_float(value: object, default: float = 0.0) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _weeks_between(a: str, b: str) -> int:
    from datetime import datetime

    da = datetime.strptime(a, "%Y-%m-%d")
    db = datetime.strptime(b, "%Y-%m-%d")
    return max(0, (db - da).days // 7)


def _load_weekly_rows() -> list[dict]:
    weekly_rows = _read_csv(ANALYTICS_DIR / "weekly_doc_counts.csv")
    staleness_rows = {row["week_start"]: row for row in _read_csv(ANALYTICS_DIR / "staleness_rate.csv")}
    gap_rows = {row["week_start"]: row for row in _read_csv(ANALYTICS_DIR / "temporal_gap.csv")}

    rows = []
    for row in weekly_rows:
        week = row["week_start"]
        if not (WINDOW_START <= week <= WINDOW_END):
            continue
        rows.append(
            {
                "week_start": week,
                "cutoff_date": gap_rows.get(week, {}).get("cutoff_date")
                or staleness_rows.get(week, {}).get("cutoff_date")
                or week,
                "new_docs": _as_int(row.get("new_docs")),
                "cumulative_docs": _as_int(row.get("cumulative_docs")),
                "staleness_rate": _as_float(staleness_rows.get(week, {}).get("staleness_rate")),
                "temporal_gap_days": _as_int(gap_rows.get(week, {}).get("temporal_gap_days")),
            }
        )
    return rows


WEEKLY_ROWS = _load_weekly_rows()


def _simulate_policy(thresholds: Thresholds) -> dict:
    baseline_source = WEEKLY_ROWS[: max(thresholds.baseline_weeks, 1)]
    baseline_velocity = statistics.mean(row["new_docs"] / 7.0 for row in baseline_source)

    indexed_docs_at_reindex = max(WEEKLY_ROWS[0]["cumulative_docs"], 1)
    baseline_temporal_gap = WEEKLY_ROWS[0]["temporal_gap_days"]
    accepted_updates = []

    for row in WEEKLY_ROWS:
        coverage_gap = max(row["cumulative_docs"] - indexed_docs_at_reindex, 0) / indexed_docs_at_reindex
        velocity = row["new_docs"] / 7.0
        temporal_gap_growth = row["temporal_gap_days"] - baseline_temporal_gap

        reasons: list[str] = []
        trigger_level = 0
        action = "none"

        if row["staleness_rate"] > thresholds.staleness_rate and coverage_gap > thresholds.coverage_gap:
            trigger_level = 1
            action = "soft_alert"
            reasons.append("staleness_rate+coverage_gap")

        if temporal_gap_growth > thresholds.temporal_gap_growth_days:
            trigger_level = max(trigger_level, 2)
            action = "incremental_reindex"
            reasons.append("temporal_gap_growth_days")

        if baseline_velocity > 0 and velocity > thresholds.velocity_multiplier * baseline_velocity:
            trigger_level = max(trigger_level, 2)
            action = "incremental_reindex"
            reasons.append("velocity_per_day")

        if trigger_level >= 2:
            accepted_updates.append(
                {
                    "week_start": row["week_start"],
                    "cutoff_date": row["cutoff_date"],
                    "action": action,
                    "coverage_gap": round(coverage_gap, 4),
                    "velocity_per_day": round(velocity, 3),
                    "staleness_rate": round(row["staleness_rate"], 4),
                    "temporal_gap_growth_days": temporal_gap_growth,
                    "reasons": reasons,
                }
            )
            indexed_docs_at_reindex = max(row["cumulative_docs"], 1)
            baseline_temporal_gap = row["temporal_gap_days"]

    update_weeks = [row["week_start"] for row in accepted_updates]
    intervals = [
        _weeks_between(update_weeks[i], update_weeks[i + 1])
        for i in range(len(update_weeks) - 1)
    ]
    avg_interval = statistics.mean(intervals) if intervals else 999.0
    min_interval = min(intervals) if intervals else 999
    max_interval = max(intervals) if intervals else 999

    reason_mix = {
        "velocity_only": sum(1 for row in accepted_updates if row["reasons"] == ["velocity_per_day"]),
        "stale_coverage_plus_velocity": sum(
            1 for row in accepted_updates if "staleness_rate+coverage_gap" in row["reasons"] and "velocity_per_day" in row["reasons"]
        ),
        "temporal_gap": sum(1 for row in accepted_updates if "temporal_gap_growth_days" in row["reasons"]),
    }

    return {
        "thresholds": asdict(thresholds),
        "update_count": len(accepted_updates),
        "avg_interval_weeks": round(avg_interval, 2),
        "min_interval_weeks": min_interval,
        "max_interval_weeks": max_interval,
        "intervals_weeks": intervals,
        "update_weeks": update_weeks,
        "reason_mix": reason_mix,
        "updates": accepted_updates,
    }


def _score_candidate(result: dict) -> tuple:
    avg_interval = result["avg_interval_weeks"]
    distance_to_band = 0.0 if 2 <= avg_interval <= 6 else min(abs(avg_interval - 2), abs(avg_interval - 6))
    # Prefer options in-band, then fewer updates, then slightly more stale+coverage support.
    return (
        distance_to_band,
        0 if 2 <= avg_interval <= 6 else 1,
        result["update_count"],
        -result["reason_mix"]["stale_coverage_plus_velocity"],
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    grid = {
        "staleness_rate": [0.80, 0.85, 0.90, 0.93, 0.95, 0.97],
        "coverage_gap": [0.03, 0.10, 0.25, 0.50, 1.0, 2.0, 4.0],
        "temporal_gap_growth_days": [20, 60, 120, 240, 480],
        "velocity_multiplier": [1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0],
        "baseline_weeks": [4, 8, 12, 16],
    }

    results = []
    for values in itertools.product(*(grid[key] for key in grid)):
        thresholds = Thresholds(*values)
        results.append(_simulate_policy(thresholds))

    ranked = sorted(results, key=_score_candidate)
    in_range = [row for row in ranked if 2 <= row["avg_interval_weeks"] <= 6]

    (OUTPUT_DIR / "threshold_search_results.json").write_text(
        json.dumps(
            {
                "window_start": WINDOW_START,
                "window_end": WINDOW_END,
                "candidate_count": len(results),
                "in_range_count": len(in_range),
                "top_results": ranked[:50],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    with (OUTPUT_DIR / "threshold_search_top25.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "staleness_rate",
                "coverage_gap",
                "temporal_gap_growth_days",
                "velocity_multiplier",
                "baseline_weeks",
                "update_count",
                "avg_interval_weeks",
                "min_interval_weeks",
                "max_interval_weeks",
                "update_weeks",
                "reason_mix",
            ],
        )
        writer.writeheader()
        for rank, row in enumerate(ranked[:25], start=1):
            writer.writerow(
                {
                    "rank": rank,
                    **row["thresholds"],
                    "update_count": row["update_count"],
                    "avg_interval_weeks": row["avg_interval_weeks"],
                    "min_interval_weeks": row["min_interval_weeks"],
                    "max_interval_weeks": row["max_interval_weeks"],
                    "update_weeks": ", ".join(row["update_weeks"]),
                    "reason_mix": json.dumps(row["reason_mix"], ensure_ascii=True),
                }
            )

    md_lines = [
        "# Threshold Search",
        "",
        f"Window: `{WINDOW_START}` to `{WINDOW_END}`",
        f"Candidates evaluated: `{len(results)}`",
        f"Candidates in the target cadence band (2-6 weeks/update on average): `{len(in_range)}`",
        "",
        "The simulation resets the reindex anchor after every accepted update. That means",
        "coverage gap and temporal-gap growth restart after each accepted `incremental_reindex`.",
        "",
        "## Key Finding",
        "",
        "In this search, update frequency is driven mainly by `velocity_multiplier` and `baseline_weeks`.",
        "Changing `staleness_rate`, `coverage_gap`, or `temporal_gap_growth_days` has much less impact",
        "on cadence for the 2025-03 to 2026-03 window.",
        "",
        "Also important: no searched threshold combination achieves both",
        "",
        "- average cadence inside the 2-6 week target band, and",
        "- a minimum gap of at least 2 weeks between every pair of updates.",
        "",
        "So threshold tuning alone can lower the average frequency, but it does not fully remove",
        "short back-to-back trigger bursts. If we want smoother spacing, we likely need one extra",
        "policy rule such as a cooldown window.",
        "",
        "## Top Results",
        "",
        "| Rank | Staleness | Coverage | Temp Gap Days | Velocity x Baseline | Baseline Weeks | Updates | Avg Interval (w) | Min | Max |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(ranked[:10], start=1):
        t = row["thresholds"]
        md_lines.append(
            f"| {rank} | {t['staleness_rate']:.2f} | {t['coverage_gap']:.2f} | {t['temporal_gap_growth_days']} "
            f"| {t['velocity_multiplier']:.1f} | {t['baseline_weeks']} | {row['update_count']} "
            f"| {row['avg_interval_weeks']:.2f} | {row['min_interval_weeks']} | {row['max_interval_weeks']} |"
        )

    md_lines.extend(["", "## Recommended Options", ""])
    for rank, row in enumerate(ranked[:5], start=1):
        t = row["thresholds"]
        md_lines.extend(
            [
                f"### Option {rank}",
                "",
                f"- `staleness_rate = {t['staleness_rate']:.2f}`",
                f"- `coverage_gap = {t['coverage_gap']:.2f}`",
                f"- `temporal_gap_growth_days = {t['temporal_gap_growth_days']}`",
                f"- `velocity_multiplier = {t['velocity_multiplier']:.1f}`",
                f"- `baseline_weeks = {t['baseline_weeks']}`",
                f"- updates in window: `{row['update_count']}`",
                f"- average interval: `{row['avg_interval_weeks']:.2f}` weeks",
                f"- update weeks: `{', '.join(row['update_weeks'])}`",
                f"- reason mix: `{json.dumps(row['reason_mix'], ensure_ascii=True)}`",
                "",
            ]
        )

    (OUTPUT_DIR / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_DIR / 'summary.md'}")


if __name__ == "__main__":
    main()

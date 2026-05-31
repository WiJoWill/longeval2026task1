"""Build a markdown timeline for weekly adaptive-update decisions."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REINDEX_DIR = ROOT / "adaptive_monitor" / "outputs" / "reindex_pipeline"
INDEX_MEMBERSHIP_DIR = ROOT / "adaptive_monitor" / "outputs" / "index_membership"
OUTPUT_PATH = REINDEX_DIR / "weekly_update_timeline.md"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _triggered_metrics(reason: str) -> str:
    metrics: list[str] = []
    if "staleness_rate=" in reason:
        metrics.append("staleness_rate")
    if "coverage_gap=" in reason:
        metrics.append("coverage_gap")
    if "velocity_per_day=" in reason:
        metrics.append("velocity_per_day")
    if "temporal_gap_growth_days=" in reason:
        metrics.append("temporal_gap_growth_days")
    if "rank_stability_drop" in reason:
        metrics.append("rank_stability_drop")
    return ", ".join(metrics) if metrics else "none"


def _load_latest_manifest() -> dict:
    runs_dir = REINDEX_DIR / "runs"
    manifests = sorted(runs_dir.glob("*/manifest.json"))
    if not manifests:
        return {}
    return _read_json(manifests[-1])


def build_markdown() -> str:
    trigger_rows = _read_csv(REINDEX_DIR / "trigger_decisions.csv")
    index_rows = _read_csv(INDEX_MEMBERSHIP_DIR / "index_versions.csv")
    latest_manifest = _load_latest_manifest()

    trigger_rows_2025 = [
        row for row in trigger_rows
        if row["week_start"] >= "2025-03-01" and row["action"] != "none"
    ]
    adopted_rows = [row for row in index_rows if row["cutoff_date"] >= "2025-03-31"]

    lines = [
        "# Weekly Update Timeline",
        "",
        "This note consolidates the adaptive-monitoring outputs into a single weekly timeline.",
        "It separates the simulated updates we actually adopted in the March-May 2025 study from",
        "the weekly trigger recommendations produced by the monitoring pipeline.",
        "",
        "## Trigger Rules Used in the Current Timeline",
        "",
        "These rules come from the thresholds recorded in the latest planning manifest:",
        "",
        "- `soft_alert` if `staleness_rate > 0.8` and `coverage_gap > 0.03`",
        "- `incremental_reindex` if `velocity_per_day > 1.5 x baseline_velocity_per_day`",
        "- `incremental_reindex` if `temporal_gap_growth_days > 20`",
        "- `full_rebuild` if `rank_stability_drop > 0.2` for 3 consecutive periods",
        "",
        "For the current outputs, the practical triggers are almost entirely:",
        "",
        "- `velocity_per_day` spikes",
        "- `staleness_rate + coverage_gap` together",
        "",
        "No current weekly decision is triggered by:",
        "",
        "- `temporal_gap_growth_days`",
        "- `rank_stability_drop`",
        "",
        "Important note:",
        "",
        "- Timeline A is the published-date simulation we used for the March-May 2025 adaptive-index study.",
        "- Timeline B is the weekly monitoring recommendation stream emitted by the current reindex pipeline outputs.",
        "- The latest planning manifest records `date_field=updatedDate`, so treat Timeline B as the current monitoring-plan view, not as the exact same date semantics as Timeline A.",
        "",
        "## Timeline A: Simulated Updates We Actually Adopted",
        "",
        "Source: `adaptive_monitor/outputs/index_membership/index_versions.csv`",
        "",
        "| Update Timing | Index Version | Action | Trigger Level | Triggered Metrics | Why Update Was Needed |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]

    for row in adopted_rows:
        lines.append(
            f"| {row['cutoff_date']} | {row['index_id']} | {row['action']} | {row['trigger_level']} "
            f"| {_triggered_metrics(row['reason'])} | {row['reason']} |"
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "In the simulated March-May 2025 setup we start from a March baseline index and then",
            "adopt weekly incremental updates through `2025-06-01`. Early April and early May updates",
            "are triggered by both `staleness_rate + coverage_gap` and `velocity_per_day`; late May and",
            "June updates are triggered mainly by velocity spikes alone.",
            "",
            "## Timeline B: Weekly Monitoring Recommendations",
            "",
            "Source: `adaptive_monitor/outputs/reindex_pipeline/trigger_decisions.csv`",
            "",
            "This is the longer weekly recommendation stream for the same monitoring logic.",
            "It shows which week would have required an update even when we were not running a full",
            "retrieval evaluation.",
            "",
            "| Week Start | Cutoff | Action | Trigger Level | Triggered Metrics | Weekly New Docs | Velocity/Day | Staleness | Coverage Gap | Why Update Was Needed |",
            "| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )

    for row in trigger_rows_2025:
        lines.append(
            f"| {row['week_start']} | {row['cutoff_date']} | {row['action']} | {row['trigger_level']} "
            f"| {_triggered_metrics(row['reason'])} | {row['weekly_new_docs']} | {row['velocity_per_day']} "
            f"| {row['staleness_rate']} | {row['index_coverage_gap']} | {row['reason']} |"
        )

    lines.extend(
        [
            "",
            "## Timeline Readout",
            "",
            "1. `2025-03-03` to `2025-05-11`: weekly updates are repeatedly triggered by all three signals.",
            "   `staleness_rate` is already above 0.8, `coverage_gap` is far above 0.03, and document",
            "   velocity is much higher than the baseline.",
            "2. `2025-05-12` to `2025-09-08`: updates are still required every week, but the direct cause",
            "   is mostly `velocity_per_day`. Staleness drops below 0.8 for part of this span, so the",
            "   soft-alert condition is not always active, but the ingestion rate alone keeps triggering",
            "   incremental reindexing.",
            "3. `2025-09-15` onward: both trigger families are active again. `staleness_rate` climbs back",
            "   above 0.8 while `coverage_gap` remains extremely large, and velocity still stays above the",
            "   baseline multiplier in most weeks.",
            "4. `2026-03-02` is the latest planning result: the newest manifest selects a `soft_alert`",
            "   rather than an `incremental_reindex`, because by that week the velocity spike has fallen",
            "   below the multiplier threshold, while `staleness_rate + coverage_gap` remain above the",
            "   soft-alert boundary.",
            "",
            "## Latest Planned Decision",
            "",
        ]
    )

    if latest_manifest:
        selected = latest_manifest.get("selected_decision", {})
        lines.extend(
            [
                f"- Run manifest: `{latest_manifest.get('run_id', '')}`",
                f"- Planned at: `{latest_manifest.get('created_at', '')}`",
                f"- Selected monitoring week: `{selected.get('week_start', '')}`",
                f"- Selected cutoff: `{selected.get('cutoff_date', '')}`",
                f"- Selected action: `{selected.get('action', '')}`",
                f"- Trigger level: `{selected.get('trigger_level', '')}`",
                f"- Triggered metrics: `{_triggered_metrics(selected.get('reason', ''))}`",
                f"- Reason: `{selected.get('reason', '')}`",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_PATH.write_text(build_markdown(), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

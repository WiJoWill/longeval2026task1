"""Cost-aware temporal drift update policy.

This module turns monitored retrieval drift signals into an update action. It
is intentionally side-effect free: it does not rebuild indexes or promote
systems. The output can be consumed by ``reindex_pipeline.py`` or used in a
report as the policy layer on top of metric monitoring.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "adaptive_monitor" / "outputs" / "drift_policy"


@dataclass(slots=True)
class DriftThresholds:
    ndcg_l1_drop: float = 0.03
    ndcg_l2_drop: float = 0.05
    ndcg_l3_drop: float = 0.10
    recall_l1_drop: float = 0.02
    recall_l2_drop: float = 0.04
    recall_l3_drop: float = 0.08
    penetration_l1_drop: float = 0.03
    penetration_l2_drop: float = 0.07
    penetration_l3_drop: float = 0.12
    retention_l1_drop: float = 0.03
    retention_l2_drop: float = 0.07
    retention_l3_drop: float = 0.12
    coverage_l1_drop: float = 0.03
    coverage_l2_drop: float = 0.07
    coverage_l3_drop: float = 0.12
    vocabulary_l1_rise: float = 0.05
    vocabulary_l2_rise: float = 0.10
    vocabulary_l3_rise: float = 0.20


@dataclass(slots=True)
class DriftSignals:
    period: str = ""
    ndcg_10_drop: float | None = None
    recall_100_drop: float | None = None
    new_doc_penetration_drop: float | None = None
    old_relevant_retention_drop: float | None = None
    lexical_coverage_drop: float | None = None
    dense_coverage_drop: float | None = None
    vocabulary_drift_rise: float | None = None
    update_cost_level: int = 1


@dataclass(slots=True)
class DriftPolicyDecision:
    period: str
    severity_level: int
    action: str
    rationale: str
    signal_levels: dict[str, int] = field(default_factory=dict)
    validation_gates: list[str] = field(default_factory=list)


def _ratio(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        ratio = float(value)
    except (TypeError, ValueError):
        return None
    if abs(ratio) >= 1.0 and abs(ratio) <= 100.0:
        return ratio / 100.0
    return ratio


def _level(value: float | None, l1: float, l2: float, l3: float) -> int:
    if value is None:
        return 0
    if value > l3:
        return 3
    if value >= l2:
        return 2
    if value >= l1:
        return 1
    return 0


def _cost_level(value: int | str | float | None) -> int:
    if value is None or value == "":
        return 1
    if isinstance(value, str):
        normalized = value.strip().lower()
        labels = {
            "low": 1,
            "cheap": 1,
            "acceptable": 1,
            "medium": 2,
            "moderate": 2,
            "high": 3,
            "expensive": 3,
            "extreme": 3,
        }
        if normalized in labels:
            return labels[normalized]
    try:
        return min(max(int(float(value)), 1), 3)
    except (TypeError, ValueError):
        return 1


def signal_levels(signals: DriftSignals, thresholds: DriftThresholds | None = None) -> dict[str, int]:
    thresholds = thresholds or DriftThresholds()
    return {
        "ndcg_10_drift": _level(
            signals.ndcg_10_drop,
            thresholds.ndcg_l1_drop,
            thresholds.ndcg_l2_drop,
            thresholds.ndcg_l3_drop,
        ),
        "recall_100_drift": _level(
            signals.recall_100_drop,
            thresholds.recall_l1_drop,
            thresholds.recall_l2_drop,
            thresholds.recall_l3_drop,
        ),
        "new_doc_penetration": _level(
            signals.new_doc_penetration_drop,
            thresholds.penetration_l1_drop,
            thresholds.penetration_l2_drop,
            thresholds.penetration_l3_drop,
        ),
        "old_relevant_retention": _level(
            signals.old_relevant_retention_drop,
            thresholds.retention_l1_drop,
            thresholds.retention_l2_drop,
            thresholds.retention_l3_drop,
        ),
        "lexical_coverage": _level(
            signals.lexical_coverage_drop,
            thresholds.coverage_l1_drop,
            thresholds.coverage_l2_drop,
            thresholds.coverage_l3_drop,
        ),
        "dense_coverage": _level(
            signals.dense_coverage_drop,
            thresholds.coverage_l1_drop,
            thresholds.coverage_l2_drop,
            thresholds.coverage_l3_drop,
        ),
        "vocabulary_drift": _level(
            signals.vocabulary_drift_rise,
            thresholds.vocabulary_l1_rise,
            thresholds.vocabulary_l2_rise,
            thresholds.vocabulary_l3_rise,
        ),
    }


def choose_drift_update(
    signals: DriftSignals,
    thresholds: DriftThresholds | None = None,
) -> DriftPolicyDecision:
    levels = signal_levels(signals, thresholds)
    severity = max(levels.values(), default=0)
    cost = _cost_level(signals.update_cost_level)
    gates = [
        "nDCG@10 must improve on recent temporal validation queries",
        "Recall@100 must not regress beyond Level 1",
        "Old-relevant retention must not collapse after freshness changes",
        "Promote only through a shadow run; keep rollback artifacts",
    ]

    action = "observe"
    rationale = "all monitored drift signals are within thresholds"

    if severity == 0:
        return DriftPolicyDecision(signals.period, severity, action, rationale, levels, gates)

    ndcg = levels["ndcg_10_drift"]
    recall = levels["recall_100_drift"]
    new_doc = levels["new_doc_penetration"]
    old_doc = levels["old_relevant_retention"]
    lexical = levels["lexical_coverage"]
    dense = levels["dense_coverage"]
    vocab = levels["vocabulary_drift"]

    if severity >= 3 and cost >= 3:
        return DriftPolicyDecision(
            period=signals.period,
            severity_level=severity,
            action="cheap_mitigation_then_defer_heavy_update",
            rationale="Level 3 drift is present but update cost is high; apply reversible mitigation first",
            signal_levels=levels,
            validation_gates=gates,
        )

    if recall >= 2 and dense >= 2:
        action = "reencode_new_docs_and_rebuild_ann"
        rationale = "Recall@100 and dense coverage both drifted, indicating dense first-stage aging"
    elif recall >= 2 and lexical >= 2:
        action = "update_bm25_stats_and_query_expansion"
        rationale = "Recall@100 and lexical coverage both drifted, indicating lexical mismatch"
    elif ndcg >= 2 and recall <= 1:
        action = "tune_fusion_or_rerank"
        rationale = "nDCG@10 drifted while Recall@100 is stable, so the candidate pool is likely adequate"
    elif new_doc >= 2 and old_doc <= 1:
        action = "increase_freshness_or_novelty"
        rationale = "new-document penetration is low while old relevant retention is stable"
    elif old_doc >= 2:
        action = "increase_history_boost_or_temporal_smoothing"
        rationale = "old stable relevant documents are being lost"
    elif vocab >= 2:
        action = "update_router_expansion_or_dense_emphasis"
        rationale = "vocabulary drift suggests scientific terminology has shifted"
    elif severity >= 3:
        action = "full_rebuild_or_retrain"
        rationale = "system-level drift exceeds Level 3 thresholds and update cost is acceptable"
    else:
        action = "cheap_parameter_tuning"
        rationale = "only Level 1 drift is present; use reversible parameter changes first"

    return DriftPolicyDecision(signals.period, severity, action, rationale, levels, gates)


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and "rows" in payload:
            payload = payload["rows"]
        if not isinstance(payload, list):
            raise ValueError(f"JSON input must be a list or contain a rows list: {path}")
        return [dict(row) for row in payload]
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _signals_from_row(row: dict[str, Any]) -> DriftSignals:
    return DriftSignals(
        period=str(row.get("period") or row.get("week_start") or row.get("split_name") or ""),
        ndcg_10_drop=_ratio(row.get("ndcg_10_drop") or row.get("ndcg_drop")),
        recall_100_drop=_ratio(row.get("recall_100_drop") or row.get("recall_drop")),
        new_doc_penetration_drop=_ratio(row.get("new_doc_penetration_drop")),
        old_relevant_retention_drop=_ratio(row.get("old_relevant_retention_drop")),
        lexical_coverage_drop=_ratio(row.get("lexical_coverage_drop")),
        dense_coverage_drop=_ratio(row.get("dense_coverage_drop")),
        vocabulary_drift_rise=_ratio(row.get("vocabulary_drift_rise") or row.get("vocabulary_drift")),
        update_cost_level=_cost_level(row.get("update_cost_level") or row.get("update_cost")),
    )


def write_drift_policy_decisions(decisions: list[DriftPolicyDecision], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [asdict(decision) for decision in decisions]
    json_path = output_dir / "drift_policy_decisions.json"
    csv_path = output_dir / "drift_policy_decisions.csv"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    if rows:
        flat_rows = []
        for row in rows:
            flat = dict(row)
            flat["signal_levels"] = json.dumps(flat["signal_levels"], sort_keys=True)
            flat["validation_gates"] = " | ".join(flat["validation_gates"])
            flat_rows.append(flat)
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(flat_rows[0].keys()))
            writer.writeheader()
            writer.writerows(flat_rows)
    return csv_path, json_path


def run_policy_file(input_path: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[DriftPolicyDecision]:
    decisions = [choose_drift_update(_signals_from_row(row)) for row in _read_rows(input_path)]
    write_drift_policy_decisions(decisions, output_dir)
    return decisions


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify temporal drift and choose update actions.")
    parser.add_argument("--input", required=True, help="CSV or JSON rows containing drift signal columns.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    decisions = run_policy_file(Path(args.input), Path(args.output_dir))
    latest = decisions[-1] if decisions else None
    print(f"Wrote {len(decisions)} drift policy decisions to {args.output_dir}")
    if latest is not None:
        print(
            f"Latest decision: level={latest.severity_level} action={latest.action} "
            f"period={latest.period} reason={latest.rationale}"
        )


if __name__ == "__main__":
    main()

from __future__ import annotations

import unittest

from adaptive_monitor.drift_policy import DriftSignals, _signals_from_row, choose_drift_update


class DriftPolicyTest(unittest.TestCase):
    def test_ndcg_drop_with_stable_recall_tunes_ranking_layer(self) -> None:
        decision = choose_drift_update(
            DriftSignals(
                period="validation_recent",
                ndcg_10_drop=0.06,
                recall_100_drop=0.01,
                update_cost_level=1,
            )
        )

        self.assertEqual(decision.severity_level, 2)
        self.assertEqual(decision.action, "tune_fusion_or_rerank")

    def test_recall_and_dense_drift_rebuilds_dense_candidates(self) -> None:
        decision = choose_drift_update(
            DriftSignals(
                period="validation_recent",
                recall_100_drop=0.05,
                dense_coverage_drop=0.08,
                update_cost_level=2,
            )
        )

        self.assertEqual(decision.severity_level, 2)
        self.assertEqual(decision.action, "reencode_new_docs_and_rebuild_ann")

    def test_recall_and_lexical_drift_updates_lexical_layer(self) -> None:
        decision = choose_drift_update(
            DriftSignals(
                period="validation_recent",
                recall_100_drop=0.05,
                lexical_coverage_drop=0.08,
                update_cost_level=2,
            )
        )

        self.assertEqual(decision.action, "update_bm25_stats_and_query_expansion")

    def test_low_new_doc_penetration_increases_freshness(self) -> None:
        decision = choose_drift_update(
            DriftSignals(
                period="validation_recent",
                new_doc_penetration_drop=0.08,
                old_relevant_retention_drop=0.01,
                update_cost_level=1,
            )
        )

        self.assertEqual(decision.action, "increase_freshness_or_novelty")

    def test_old_relevant_retention_loss_adds_history_boost(self) -> None:
        decision = choose_drift_update(
            DriftSignals(
                period="validation_recent",
                new_doc_penetration_drop=0.08,
                old_relevant_retention_drop=0.08,
                update_cost_level=1,
            )
        )

        self.assertEqual(decision.action, "increase_history_boost_or_temporal_smoothing")

    def test_high_cost_level_three_uses_reversible_mitigation(self) -> None:
        decision = choose_drift_update(
            DriftSignals(
                period="validation_recent",
                recall_100_drop=0.11,
                dense_coverage_drop=0.13,
                update_cost_level=3,
            )
        )

        self.assertEqual(decision.severity_level, 3)
        self.assertEqual(decision.action, "cheap_mitigation_then_defer_heavy_update")

    def test_percent_inputs_are_normalized(self) -> None:
        signals = _signals_from_row(
            {
                "period": "validation_recent",
                "ndcg_drop": "6",
                "recall_drop": "1",
                "update_cost": "low",
            }
        )
        decision = choose_drift_update(signals)

        self.assertEqual(decision.action, "tune_fusion_or_rerank")


if __name__ == "__main__":
    unittest.main()

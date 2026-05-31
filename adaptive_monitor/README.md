# adaptive_monitor

Monitoring and daily-split evaluation for the chosen production model: `custom_lexical_fulltext` (BM25 full text).

Does NOT modify any other folder. Reuses existing source code from `src/` and configs from `configs/`.

## Scripts

### `collection_analytics.py`
Runs from document metadata only. No run.txt required.

Outputs:
- `outputs/collection_analytics/daily_doc_counts.csv` — new docs and cumulative count per day
- `outputs/collection_analytics/weekly_doc_counts.csv` — same, aggregated by week
- `outputs/collection_analytics/staleness_rate.csv` — Doc Staleness Rate per weekly cutoff
- `outputs/collection_analytics/temporal_gap.csv` — Temporal Gap per weekly cutoff
- `outputs/collection_analytics/summary.json` — top-level summary stats

Run:
    python adaptive_monitor/collection_analytics.py

### `trigger_decision.py`
Reads `collection_analytics.py` outputs and computes weekly reindex trigger decisions.

Implemented trigger rules:
- Level 1 soft alert:
  - `Doc Staleness Rate > 15%`
  - and `Index Coverage Gap > 5%`
- Level 2 incremental reindex candidate:
  - `Temporal Gap growth > 30 days`
  - or `New Doc Velocity > 2x baseline`
- Level 3 full rebuild candidate:
  - optional `rank_stability_drop > 20%` for 3 consecutive periods, if a rank-stability CSV is supplied

Outputs:
- `outputs/reindex_pipeline/trigger_decisions.csv`
- `outputs/reindex_pipeline/trigger_decisions.json`

Run:
    python adaptive_monitor/trigger_decision.py

### `drift_policy.py`
Reads retrieval-quality drift signals and chooses a cost-aware update action.
This is the policy layer for the monitoring table:

| Signal | Level 1 | Level 2 | Level 3 | Main action |
| --- | --- | --- | --- | --- |
| nDCG@10 drift | 3-5% drop | 5-10% drop | >10% drop | tune fusion/rerank |
| Recall@100 drift | 2-4% drop | 4-8% drop | >8% drop | update first-stage retrieval |
| New-doc penetration | small drop | clear drop | sustained drop | freshness/novelty boost |
| Old-relevant retention | small drop | clear drop | broad drop | history boost/temporal smoothing |
| Lexical coverage drift | local | query class | broad | BM25 stats/query expansion |
| Dense coverage drift | local | query class | broad | re-encode/rebuild ANN |
| Vocabulary drift | rising | clear rise | burst | router/expansion/dense emphasis |
| Update cost | acceptable | high | extreme | defer heavy update when possible |

Expected input is CSV or JSON rows with any of these columns:

- `period`
- `ndcg_10_drop` or `ndcg_drop`
- `recall_100_drop` or `recall_drop`
- `new_doc_penetration_drop`
- `old_relevant_retention_drop`
- `lexical_coverage_drop`
- `dense_coverage_drop`
- `vocabulary_drift_rise` or `vocabulary_drift`
- `update_cost_level` or `update_cost`

Drop/rise values can be ratios (`0.06`) or percentages (`6`). The script writes:

- `outputs/drift_policy/drift_policy_decisions.csv`
- `outputs/drift_policy/drift_policy_decisions.json`

Run:
    python adaptive_monitor/drift_policy.py --input path/to/drift_signals.csv

### `reindex_pipeline.py`
Runs the adaptive reindex pipeline around the trigger decisions.

Default mode is plan-only. It writes a manifest and does not touch live indexes:

    python adaptive_monitor/reindex_pipeline.py --mode plan

Build mode creates a shadow index under:

    adaptive_monitor/outputs/reindex_pipeline/runs/<run_id>/shadow_indexes/

Run:
    python adaptive_monitor/reindex_pipeline.py --mode build --last-reindex-week 2025-03-03

For Level 2 decisions, build mode now uses an incremental lexical path by default:

1. build a delta PyTerrier index for documents with `date_field` after `--last-reindex-week`
2. merge the live canonical index and delta index into the shadow index
3. write an incremental manifest under `runs/<run_id>/incremental/`

The incremental path is implemented for lexical PyTerrier pipelines. Use
`--full-rebuild` to build a complete shadow index instead:

    python adaptive_monitor/reindex_pipeline.py --mode build --full-rebuild

Promotion is explicit and disabled by default:

    python adaptive_monitor/reindex_pipeline.py --mode build --last-reindex-week 2025-03-03 --promote

Notes:
- Level 1 only logs a soft alert unless `--force-build` is passed.
- Dense Qwen indexes are treated as Level 3 only unless `--force-build` is passed.
- Incremental lexical reindexing builds and merges a delta index; it does not mutate the live index in place.

### `daily_split_eval.py`
Requires `outputs/custom_lexical_fulltext/snapshot-1-train/run.txt`.
Computes nDCG@10, MAP, Recall@100, Recall@1000 for each cumulative daily window.

Run:
    python adaptive_monitor/daily_split_eval.py --step-days 7

To regenerate the run file first:
    python scripts/run_baseline.py \
        --config configs/custom_lexical_fulltext.yaml \
        --snapshot-id snapshot-1 \
        --train-snapshot1

## What each script tells you

| Script | Tells you |
| --- | --- |
| `collection_analytics.py` | How fast new documents arrive, how stale the index becomes over time |
| `trigger_decision.py` | Which weekly cutoffs cross Level 1/2/3 reindex thresholds |
| `drift_policy.py` | Which metric drift pattern happened and the cheapest sufficient update action |
| `reindex_pipeline.py` | Plans or builds a shadow reindex run from the latest actionable trigger |
| `daily_split_eval.py` | How nDCG@10 and recall change as more documents are added to the evaluation window |

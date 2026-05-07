# Update Strategy Summary

This folder consolidates the final update-strategy discussion into one place.

Files in this folder:

- `README.md`
- `option_c_2_5_1_timeline.png`
- `qrel_freshness_distribution.png`

## 1. Update Strategy

The current update policy is a **weekly monitoring policy** with two practical
incremental-update triggers:

- `velocity_per_day`
  - update when weekly document-ingestion velocity is much higher than the baseline rate
- `staleness_rate + coverage_gap`
  - update when the collection has become sufficiently stale and the index has drifted far enough from the live collection

The current parameterization is:

- `staleness_rate = 0.80`
- `coverage_gap = 0.03`
- `temporal_gap_growth_days = 20`
- `velocity_multiplier = 3.0`
- `baseline_weeks = 4`

Operationally, this means:

- monitor the collection weekly
- issue an incremental update when velocity is unusually high
- also issue an incremental update when staleness and coverage drift are jointly high

In the final selected timeline, the practical trigger pattern is simple:

- the first `7` updates are triggered by `velocity_per_day`
- the final update is triggered by `staleness_rate + coverage_gap + velocity_per_day`

## 2. Why This Can Only Be Discussed Qualitatively

We can describe and simulate the update policy, but we cannot treat the current
March-May 2025 setup as a clean **quantitative backtest** of whether updating was
better than not updating.

The main reason is the qrel freshness structure:

- `100 / 100` train queries with dated relevant documents already have their latest
  judged-relevant document **before `2025-03-01`**
- `100 / 100` also have their latest dated relevant document on or before
  `2025-03-31`

So during the March-May 2025 update window:

- reindexing does **not** expose new judged-relevant answers for these queries
- it mostly adds more candidate documents that act as distractors

That is why the update-policy discussion here must be read as:

- a **qualitative monitoring and scheduling analysis**
- not a clean causal effectiveness backtest

The supporting freshness plot is:

- `qrel_freshness_distribution.png`

And the core interpretation is:

- judged-relevant answers are already in the corpus before the update window
- later updates mainly change retrieval difficulty, not relevance availability

This also matches the daily cumulative evaluation behavior we observed on the same
100-query set:

- as more later documents are admitted, retrieval quality drifts downward rather
  than benefiting from newly available judged-relevant content

## 3. Current Parameters

The current monitoring thresholds are:

| Parameter | Value | Meaning |
| --- | ---: | --- |
| `staleness_rate` | `0.80` | stale-doc fraction threshold for the soft-alert branch |
| `coverage_gap` | `0.03` | minimum index drift required together with staleness |
| `temporal_gap_growth_days` | `20` | temporal-gap growth threshold |
| `velocity_multiplier` | `3.0` | update when weekly velocity exceeds `3.0 x` the baseline |
| `baseline_weeks` | `4` | use the first four weekly windows to estimate baseline ingestion velocity |

Interpretation:

- `baseline_weeks = 4` means the baseline ingestion rate is estimated from the
  first four weekly windows
- `velocity_multiplier = 3.0` means an incremental update is triggered when the
  current weekly ingestion velocity exceeds `3.0 x` that baseline

## 4. Final Update Timeline and Discussion

For the final selected weekly strategy, the update distribution across the three
snapshot-aligned periods is:

- `snapshot-1` (`2025-03-01` to `2025-05-31`): `2` updates
- `snapshot-2` (`2025-06-01` to `2025-08-31`): `5` updates
- `snapshot-3` (`2025-09-01` to `2025-11-30`): `1` update

So the final pattern is:

- `2 / 5 / 1`

The final update weeks are:

- `2025-05-12`
- `2025-05-19`
- `2025-06-02`
- `2025-06-09`
- `2025-06-16`
- `2025-06-30`
- `2025-07-07`
- `2025-10-13`

Per-update reasons:

| Update Week | Trigger Reason |
| --- | --- |
| `2025-05-12` | `velocity_per_day` |
| `2025-05-19` | `velocity_per_day` |
| `2025-06-02` | `velocity_per_day` |
| `2025-06-09` | `velocity_per_day` |
| `2025-06-16` | `velocity_per_day` |
| `2025-06-30` | `velocity_per_day` |
| `2025-07-07` | `velocity_per_day` |
| `2025-10-13` | `staleness_rate + coverage_gap + velocity_per_day` |

The timeline figure in this folder is:

- `option_c_2_5_1_timeline.png`

Discussion:

- update activity is concentrated in the middle period
- the strategy is therefore **not** evenly distributed across the three periods
- most of the timeline is dominated by ingestion velocity rather than by temporal-gap growth
- the late-period update appears only once, when stale coverage and velocity are both active again

In short:

- the current system should be understood as a **weekly qualitative monitoring policy**
- the present qrels do not support a clean quantitative claim that these updates
  improve relevance effectiveness
- the final operational picture is a `2 / 5 / 1` update timeline, driven mostly by
  velocity spikes

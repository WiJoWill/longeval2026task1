# Threshold Search

Window: `2025-03-01` to `2026-03-08`
Candidates evaluated: `8400`
Candidates in the target cadence band (2-6 weeks/update on average): `1890`

The simulation resets the reindex anchor after every accepted update. That means
coverage gap and temporal-gap growth restart after each accepted `incremental_reindex`.

## Key Finding

In this search, update frequency is driven mainly by `velocity_multiplier` and `baseline_weeks`.
Changing `staleness_rate`, `coverage_gap`, or `temporal_gap_growth_days` has much less impact
on cadence for the 2025-03 to 2026-03 window.

Also important: no searched threshold combination achieves both

- average cadence inside the 2-6 week target band, and
- a minimum gap of at least 2 weeks between every pair of updates.

So threshold tuning alone can lower the average frequency, but it does not fully remove
short back-to-back trigger bursts. If we want smoother spacing, we likely need one extra
policy rule such as a cooldown window.

## Top Results

| Rank | Staleness | Coverage | Temp Gap Days | Velocity x Baseline | Baseline Weeks | Updates | Avg Interval (w) | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.80 | 0.03 | 20 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 2 | 0.80 | 0.03 | 60 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 3 | 0.80 | 0.03 | 120 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 4 | 0.80 | 0.03 | 240 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 5 | 0.80 | 0.03 | 480 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 6 | 0.80 | 0.10 | 20 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 7 | 0.80 | 0.10 | 60 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 8 | 0.80 | 0.10 | 120 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 9 | 0.80 | 0.10 | 240 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |
| 10 | 0.80 | 0.10 | 480 | 4.0 | 4 | 5 | 4.75 | 1 | 14 |

## Recommended Options

### Option 1

- `staleness_rate = 0.80`
- `coverage_gap = 0.03`
- `temporal_gap_growth_days = 20`
- `velocity_multiplier = 4.0`
- `baseline_weeks = 4`
- updates in window: `5`
- average interval: `4.75` weeks
- update weeks: `2025-06-02, 2025-06-16, 2025-06-30, 2025-07-07, 2025-10-13`
- reason mix: `{"velocity_only": 4, "stale_coverage_plus_velocity": 1, "temporal_gap": 0}`

### Option 2

- `staleness_rate = 0.80`
- `coverage_gap = 0.03`
- `temporal_gap_growth_days = 60`
- `velocity_multiplier = 4.0`
- `baseline_weeks = 4`
- updates in window: `5`
- average interval: `4.75` weeks
- update weeks: `2025-06-02, 2025-06-16, 2025-06-30, 2025-07-07, 2025-10-13`
- reason mix: `{"velocity_only": 4, "stale_coverage_plus_velocity": 1, "temporal_gap": 0}`

### Option 3

- `staleness_rate = 0.80`
- `coverage_gap = 0.03`
- `temporal_gap_growth_days = 120`
- `velocity_multiplier = 4.0`
- `baseline_weeks = 4`
- updates in window: `5`
- average interval: `4.75` weeks
- update weeks: `2025-06-02, 2025-06-16, 2025-06-30, 2025-07-07, 2025-10-13`
- reason mix: `{"velocity_only": 4, "stale_coverage_plus_velocity": 1, "temporal_gap": 0}`

### Option 4

- `staleness_rate = 0.80`
- `coverage_gap = 0.03`
- `temporal_gap_growth_days = 240`
- `velocity_multiplier = 4.0`
- `baseline_weeks = 4`
- updates in window: `5`
- average interval: `4.75` weeks
- update weeks: `2025-06-02, 2025-06-16, 2025-06-30, 2025-07-07, 2025-10-13`
- reason mix: `{"velocity_only": 4, "stale_coverage_plus_velocity": 1, "temporal_gap": 0}`

### Option 5

- `staleness_rate = 0.80`
- `coverage_gap = 0.03`
- `temporal_gap_growth_days = 480`
- `velocity_multiplier = 4.0`
- `baseline_weeks = 4`
- updates in window: `5`
- average interval: `4.75` weeks
- update weeks: `2025-06-02, 2025-06-16, 2025-06-30, 2025-07-07, 2025-10-13`
- reason mix: `{"velocity_only": 4, "stale_coverage_plus_velocity": 1, "temporal_gap": 0}`

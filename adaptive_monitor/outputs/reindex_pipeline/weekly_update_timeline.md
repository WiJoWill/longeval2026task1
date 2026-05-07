# Weekly Update Timeline

This note consolidates the adaptive-monitoring outputs into a single weekly timeline.
It separates the simulated updates we actually adopted in the March-May 2025 study from
the weekly trigger recommendations produced by the monitoring pipeline.

## Trigger Rules Used in the Current Timeline

These rules come from the thresholds recorded in the latest planning manifest:

- `soft_alert` if `staleness_rate > 0.8` and `coverage_gap > 0.03`
- `incremental_reindex` if `velocity_per_day > 1.5 x baseline_velocity_per_day`
- `incremental_reindex` if `temporal_gap_growth_days > 20`
- `full_rebuild` if `rank_stability_drop > 0.2` for 3 consecutive periods

For the current outputs, the practical triggers are almost entirely:

- `velocity_per_day` spikes
- `staleness_rate + coverage_gap` together

No current weekly decision is triggered by:

- `temporal_gap_growth_days`
- `rank_stability_drop`

Important note:

- Timeline A is the published-date simulation we used for the March-May 2025 adaptive-index study.
- Timeline B is the weekly monitoring recommendation stream emitted by the current reindex pipeline outputs.
- The latest planning manifest records `date_field=updatedDate`, so treat Timeline B as the current monitoring-plan view, not as the exact same date semantics as Timeline A.

## Timeline A: Simulated Updates We Actually Adopted

Source: `adaptive_monitor/outputs/index_membership/index_versions.csv`

| Update Timing | Index Version | Action | Trigger Level | Triggered Metrics | Why Update Was Needed |
| --- | --- | --- | ---: | --- | --- |
| 2025-03-31 | idx_20250331_march_baseline | march_baseline | 0 | none | publishedDate <= March cutoff |
| 2025-04-06 | idx_20250406_incremental_reindex | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | staleness_rate=0.8891>0.8000 and coverage_gap=1628.8368>0.0300; velocity_per_day=773.43>1.50x baseline=11.25 |
| 2025-04-13 | idx_20250413_incremental_reindex | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | staleness_rate=0.8661>0.8000 and coverage_gap=1669.3640>0.0300; velocity_per_day=1383.71>1.50x baseline=11.25 |
| 2025-04-20 | idx_20250420_incremental_reindex | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | staleness_rate=0.8523>0.8000 and coverage_gap=1704.0042>0.0300; velocity_per_day=1182.71>1.50x baseline=11.25 |
| 2025-04-27 | idx_20250427_incremental_reindex | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | staleness_rate=0.8373>0.8000 and coverage_gap=1739.1674>0.0300; velocity_per_day=1200.57>1.50x baseline=11.25 |
| 2025-05-04 | idx_20250504_incremental_reindex | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | staleness_rate=0.8355>0.8000 and coverage_gap=1748.9331>0.0300; velocity_per_day=333.43>1.50x baseline=11.25 |
| 2025-05-11 | idx_20250511_incremental_reindex | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | staleness_rate=0.8095>0.8000 and coverage_gap=1813.8368>0.0300; velocity_per_day=2216.00>1.50x baseline=11.25 |
| 2025-05-18 | idx_20250518_incremental_reindex | incremental_reindex | 2 | velocity_per_day | velocity_per_day=3055.14>1.50x baseline=11.25 |
| 2025-05-25 | idx_20250525_incremental_reindex | incremental_reindex | 2 | velocity_per_day | velocity_per_day=2549.43>1.50x baseline=11.25 |
| 2025-06-01 | idx_20250601_incremental_reindex | incremental_reindex | 2 | velocity_per_day | velocity_per_day=1318.00>1.50x baseline=11.25 |

Interpretation:
In the simulated March-May 2025 setup we start from a March baseline index and then
adopt weekly incremental updates through `2025-06-01`. Early April and early May updates
are triggered by both `staleness_rate + coverage_gap` and `velocity_per_day`; late May and
June updates are triggered mainly by velocity spikes alone.

## Timeline B: Weekly Monitoring Recommendations

Source: `adaptive_monitor/outputs/reindex_pipeline/trigger_decisions.csv`

This is the longer weekly recommendation stream for the same monitoring logic.
It shows which week would have required an update even when we were not running a full
retrieval evaluation.

| Week Start | Cutoff | Action | Trigger Level | Triggered Metrics | Weekly New Docs | Velocity/Day | Staleness | Coverage Gap | Why Update Was Needed |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| 2025-03-03 | 2025-03-09 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 5116 | 730.857 | 0.9277 | 1531.76569 | staleness_rate=0.9277>0.8000 and coverage_gap=1531.7657>0.0300; velocity_per_day=730.86>1.50x baseline=11.25 |
| 2025-03-10 | 2025-03-16 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 6576 | 939.429 | 0.9131 | 1559.280335 | staleness_rate=0.9131>0.8000 and coverage_gap=1559.2803>0.0300; velocity_per_day=939.43>1.50x baseline=11.25 |
| 2025-03-17 | 2025-03-23 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 2935 | 419.286 | 0.9059 | 1571.560669 | staleness_rate=0.9059>0.8000 and coverage_gap=1571.5607>0.0300; velocity_per_day=419.29>1.50x baseline=11.25 |
| 2025-03-24 | 2025-03-30 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 8275 | 1182.143 | 0.8931 | 1606.1841 | staleness_rate=0.8931>0.8000 and coverage_gap=1606.1841>0.0300; velocity_per_day=1182.14>1.50x baseline=11.25 |
| 2025-03-31 | 2025-04-06 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 5414 | 773.429 | 0.8891 | 1628.83682 | staleness_rate=0.8891>0.8000 and coverage_gap=1628.8368>0.0300; velocity_per_day=773.43>1.50x baseline=11.25 |
| 2025-04-07 | 2025-04-13 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 9686 | 1383.714 | 0.8661 | 1669.364017 | staleness_rate=0.8661>0.8000 and coverage_gap=1669.3640>0.0300; velocity_per_day=1383.71>1.50x baseline=11.25 |
| 2025-04-14 | 2025-04-20 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 8279 | 1182.714 | 0.8523 | 1704.004184 | staleness_rate=0.8523>0.8000 and coverage_gap=1704.0042>0.0300; velocity_per_day=1182.71>1.50x baseline=11.25 |
| 2025-04-21 | 2025-04-27 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 8404 | 1200.571 | 0.8373 | 1739.167364 | staleness_rate=0.8373>0.8000 and coverage_gap=1739.1674>0.0300; velocity_per_day=1200.57>1.50x baseline=11.25 |
| 2025-04-28 | 2025-05-04 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 2334 | 333.429 | 0.8355 | 1748.933054 | staleness_rate=0.8355>0.8000 and coverage_gap=1748.9331>0.0300; velocity_per_day=333.43>1.50x baseline=11.25 |
| 2025-05-05 | 2025-05-11 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 15512 | 2216.0 | 0.8095 | 1813.83682 | staleness_rate=0.8095>0.8000 and coverage_gap=1813.8368>0.0300; velocity_per_day=2216.00>1.50x baseline=11.25 |
| 2025-05-12 | 2025-05-18 | incremental_reindex | 2 | velocity_per_day | 21386 | 3055.143 | 0.7817 | 1903.317992 | velocity_per_day=3055.14>1.50x baseline=11.25 |
| 2025-05-19 | 2025-05-25 | incremental_reindex | 2 | velocity_per_day | 17846 | 2549.429 | 0.7509 | 1977.987448 | velocity_per_day=2549.43>1.50x baseline=11.25 |
| 2025-05-26 | 2025-06-01 | incremental_reindex | 2 | velocity_per_day | 9226 | 1318.0 | 0.7495 | 2016.589958 | velocity_per_day=1318.00>1.50x baseline=11.25 |
| 2025-06-02 | 2025-06-08 | incremental_reindex | 2 | velocity_per_day | 27222 | 3888.857 | 0.7237 | 2130.48954 | velocity_per_day=3888.86>1.50x baseline=11.25 |
| 2025-06-09 | 2025-06-15 | incremental_reindex | 2 | velocity_per_day | 21978 | 3139.714 | 0.7028 | 2222.447699 | velocity_per_day=3139.71>1.50x baseline=11.25 |
| 2025-06-16 | 2025-06-22 | incremental_reindex | 2 | velocity_per_day | 49952 | 7136.0 | 0.657 | 2431.451883 | velocity_per_day=7136.00>1.50x baseline=11.25 |
| 2025-06-23 | 2025-06-29 | incremental_reindex | 2 | velocity_per_day | 13496 | 1928.0 | 0.6453 | 2487.920502 | velocity_per_day=1928.00>1.50x baseline=11.25 |
| 2025-06-30 | 2025-07-06 | incremental_reindex | 2 | velocity_per_day | 23381 | 3340.143 | 0.6297 | 2585.748954 | velocity_per_day=3340.14>1.50x baseline=11.25 |
| 2025-07-07 | 2025-07-13 | incremental_reindex | 2 | velocity_per_day | 30827 | 4403.857 | 0.6225 | 2714.732218 | velocity_per_day=4403.86>1.50x baseline=11.25 |
| 2025-07-14 | 2025-07-20 | incremental_reindex | 2 | velocity_per_day | 11864 | 1694.857 | 0.6181 | 2764.372385 | velocity_per_day=1694.86>1.50x baseline=11.25 |
| 2025-07-21 | 2025-07-27 | incremental_reindex | 2 | velocity_per_day | 10236 | 1462.286 | 0.6222 | 2807.200837 | velocity_per_day=1462.29>1.50x baseline=11.25 |
| 2025-07-28 | 2025-08-03 | incremental_reindex | 2 | velocity_per_day | 7465 | 1066.429 | 0.6176 | 2838.435146 | velocity_per_day=1066.43>1.50x baseline=11.25 |
| 2025-08-04 | 2025-08-10 | incremental_reindex | 2 | velocity_per_day | 10647 | 1521.0 | 0.6308 | 2882.983264 | velocity_per_day=1521.00>1.50x baseline=11.25 |
| 2025-08-11 | 2025-08-17 | incremental_reindex | 2 | velocity_per_day | 6038 | 862.571 | 0.6508 | 2908.246862 | velocity_per_day=862.57>1.50x baseline=11.25 |
| 2025-08-18 | 2025-08-24 | incremental_reindex | 2 | velocity_per_day | 4031 | 575.857 | 0.6773 | 2925.112971 | velocity_per_day=575.86>1.50x baseline=11.25 |
| 2025-08-25 | 2025-08-31 | incremental_reindex | 2 | velocity_per_day | 4113 | 587.571 | 0.6815 | 2942.322176 | velocity_per_day=587.57>1.50x baseline=11.25 |
| 2025-09-01 | 2025-09-07 | incremental_reindex | 2 | velocity_per_day | 1037 | 148.143 | 0.7181 | 2946.661088 | velocity_per_day=148.14>1.50x baseline=11.25 |
| 2025-09-08 | 2025-09-14 | incremental_reindex | 2 | velocity_per_day | 2911 | 415.857 | 0.7497 | 2958.841004 | velocity_per_day=415.86>1.50x baseline=11.25 |
| 2025-09-15 | 2025-09-21 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 2258 | 322.571 | 0.8057 | 2968.288703 | staleness_rate=0.8057>0.8000 and coverage_gap=2968.2887>0.0300; velocity_per_day=322.57>1.50x baseline=11.25 |
| 2025-09-22 | 2025-09-28 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 8206 | 1172.286 | 0.8276 | 3002.623431 | staleness_rate=0.8276>0.8000 and coverage_gap=3002.6234>0.0300; velocity_per_day=1172.29>1.50x baseline=11.25 |
| 2025-09-29 | 2025-10-05 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 10424 | 1489.143 | 0.8478 | 3046.238494 | staleness_rate=0.8478>0.8000 and coverage_gap=3046.2385>0.0300; velocity_per_day=1489.14>1.50x baseline=11.25 |
| 2025-10-06 | 2025-10-12 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 12802 | 1828.857 | 0.8653 | 3099.803347 | staleness_rate=0.8653>0.8000 and coverage_gap=3099.8033>0.0300; velocity_per_day=1828.86>1.50x baseline=11.25 |
| 2025-10-13 | 2025-10-19 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 30411 | 4344.429 | 0.8537 | 3227.046025 | staleness_rate=0.8537>0.8000 and coverage_gap=3227.0460>0.0300; velocity_per_day=4344.43>1.50x baseline=11.25 |
| 2025-10-20 | 2025-10-26 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 2236 | 319.429 | 0.8626 | 3236.401674 | staleness_rate=0.8626>0.8000 and coverage_gap=3236.4017>0.0300; velocity_per_day=319.43>1.50x baseline=11.25 |
| 2025-10-27 | 2025-11-02 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 4110 | 587.143 | 0.8711 | 3253.598326 | staleness_rate=0.8711>0.8000 and coverage_gap=3253.5983>0.0300; velocity_per_day=587.14>1.50x baseline=11.25 |
| 2025-11-03 | 2025-11-09 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 10112 | 1444.571 | 0.8725 | 3295.90795 | staleness_rate=0.8725>0.8000 and coverage_gap=3295.9079>0.0300; velocity_per_day=1444.57>1.50x baseline=11.25 |
| 2025-11-10 | 2025-11-16 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 1243 | 177.571 | 0.8815 | 3301.108787 | staleness_rate=0.8815>0.8000 and coverage_gap=3301.1088>0.0300; velocity_per_day=177.57>1.50x baseline=11.25 |
| 2025-11-17 | 2025-11-23 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 5191 | 741.571 | 0.8795 | 3322.828452 | staleness_rate=0.8795>0.8000 and coverage_gap=3322.8285>0.0300; velocity_per_day=741.57>1.50x baseline=11.25 |
| 2025-11-24 | 2025-11-30 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 1315 | 187.857 | 0.8845 | 3328.330544 | staleness_rate=0.8845>0.8000 and coverage_gap=3328.3305>0.0300; velocity_per_day=187.86>1.50x baseline=11.25 |
| 2025-12-01 | 2025-12-07 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 3999 | 571.286 | 0.8818 | 3345.062762 | staleness_rate=0.8818>0.8000 and coverage_gap=3345.0628>0.0300; velocity_per_day=571.29>1.50x baseline=11.25 |
| 2025-12-08 | 2025-12-14 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 3048 | 435.429 | 0.8815 | 3357.8159 | staleness_rate=0.8815>0.8000 and coverage_gap=3357.8159>0.0300; velocity_per_day=435.43>1.50x baseline=11.25 |
| 2025-12-15 | 2025-12-21 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 11958 | 1708.286 | 0.8709 | 3407.849372 | staleness_rate=0.8709>0.8000 and coverage_gap=3407.8494>0.0300; velocity_per_day=1708.29>1.50x baseline=11.25 |
| 2025-12-22 | 2025-12-28 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 10887 | 1555.286 | 0.8709 | 3453.401674 | staleness_rate=0.8709>0.8000 and coverage_gap=3453.4017>0.0300; velocity_per_day=1555.29>1.50x baseline=11.25 |
| 2025-12-29 | 2026-01-04 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 12421 | 1774.429 | 0.8677 | 3505.372385 | staleness_rate=0.8677>0.8000 and coverage_gap=3505.3724>0.0300; velocity_per_day=1774.43>1.50x baseline=11.25 |
| 2026-01-05 | 2026-01-11 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 7328 | 1046.857 | 0.8763 | 3536.033473 | staleness_rate=0.8763>0.8000 and coverage_gap=3536.0335>0.0300; velocity_per_day=1046.86>1.50x baseline=11.25 |
| 2026-01-12 | 2026-01-18 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 7520 | 1074.286 | 0.904 | 3567.497908 | staleness_rate=0.9040>0.8000 and coverage_gap=3567.4979>0.0300; velocity_per_day=1074.29>1.50x baseline=11.25 |
| 2026-01-19 | 2026-01-25 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 11874 | 1696.286 | 0.8973 | 3617.179916 | staleness_rate=0.8973>0.8000 and coverage_gap=3617.1799>0.0300; velocity_per_day=1696.29>1.50x baseline=11.25 |
| 2026-01-26 | 2026-02-01 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 3471 | 495.857 | 0.8957 | 3631.702929 | staleness_rate=0.8957>0.8000 and coverage_gap=3631.7029>0.0300; velocity_per_day=495.86>1.50x baseline=11.25 |
| 2026-02-02 | 2026-02-08 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 1358 | 194.0 | 0.9057 | 3637.384937 | staleness_rate=0.9057>0.8000 and coverage_gap=3637.3849>0.0300; velocity_per_day=194.00>1.50x baseline=11.25 |
| 2026-02-09 | 2026-02-15 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 136 | 19.429 | 0.907 | 3637.953975 | staleness_rate=0.9070>0.8000 and coverage_gap=3637.9540>0.0300; velocity_per_day=19.43>1.50x baseline=11.25 |
| 2026-02-16 | 2026-02-22 | incremental_reindex | 2 | staleness_rate, coverage_gap, velocity_per_day | 188 | 26.857 | 0.9128 | 3638.740586 | staleness_rate=0.9128>0.8000 and coverage_gap=3638.7406>0.0300; velocity_per_day=26.86>1.50x baseline=11.25 |
| 2026-03-02 | 2026-03-08 | soft_alert | 1 | staleness_rate, coverage_gap | 4 | 0.571 | 0.9184 | 3638.757322 | staleness_rate=0.9184>0.8000 and coverage_gap=3638.7573>0.0300 |

## Timeline Readout

1. `2025-03-03` to `2025-05-11`: weekly updates are repeatedly triggered by all three signals.
   `staleness_rate` is already above 0.8, `coverage_gap` is far above 0.03, and document
   velocity is much higher than the baseline.
2. `2025-05-12` to `2025-09-08`: updates are still required every week, but the direct cause
   is mostly `velocity_per_day`. Staleness drops below 0.8 for part of this span, so the
   soft-alert condition is not always active, but the ingestion rate alone keeps triggering
   incremental reindexing.
3. `2025-09-15` onward: both trigger families are active again. `staleness_rate` climbs back
   above 0.8 while `coverage_gap` remains extremely large, and velocity still stays above the
   baseline multiplier in most weeks.
4. `2026-03-02` is the latest planning result: the newest manifest selects a `soft_alert`
   rather than an `incremental_reindex`, because by that week the velocity spike has fallen
   below the multiplier threshold, while `staleness_rate + coverage_gap` remain above the
   soft-alert boundary.

## Latest Planned Decision

- Run manifest: `20260417T061252Z`
- Planned at: `20260417T061252Z`
- Selected monitoring week: `2026-03-02`
- Selected cutoff: `2026-03-08`
- Selected action: `soft_alert`
- Trigger level: `1`
- Triggered metrics: `staleness_rate, coverage_gap`
- Reason: `staleness_rate=0.9184>0.8000 and coverage_gap=3638.7573>0.0300`

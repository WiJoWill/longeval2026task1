# Update Distribution Summary

Assumed snapshot-aligned periods:

- `snapshot-1`: `2025-03-01` to `2025-05-31`
- `snapshot-2`: `2025-06-01` to `2025-08-31`
- `snapshot-3`: `2025-09-01` to `2025-11-30`

## Final Timeline

The final weekly update timeline used here contains `8` updates across the three
snapshot periods, with distribution:

- `snapshot-1`: `2` updates
- `snapshot-2`: `5` updates
- `snapshot-3`: `1` update

So the snapshot-level pattern is:

- `2 / 5 / 1`

## Update Weeks

- `2025-05-12`
- `2025-05-19`
- `2025-06-02`
- `2025-06-09`
- `2025-06-16`
- `2025-06-30`
- `2025-07-07`
- `2025-10-13`

## Update Reasons

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

## Reading

This means the update activity is concentrated in the middle period
(`2025-06-01` to `2025-08-31`), with a lighter presence in the first and third
periods.

In compact form:

- early period: `2`
- middle period: `5`
- late period: `1`
- trigger pattern: first `7` updates are velocity-driven; the final update is driven by both stale coverage and velocity

## Files

- timeline figure: `option_c_2_5_1_timeline.png`
- threshold summary table: `summary.md`

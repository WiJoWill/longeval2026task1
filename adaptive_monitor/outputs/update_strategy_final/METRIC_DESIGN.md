# Metric Design Notes

This note summarizes the metric-design discussion behind the current weekly
update strategy.

The metrics here are **monitoring metrics**, not final retrieval-effectiveness
metrics. Their role is to tell us when the collection or the index appears to be
drifting enough that an update should be considered.

## Design Goal

The core design problem is:

- we want a weekly update policy
- but we do **not** have fresh qrels every week
- so we cannot drive updates directly from weekly relevance effectiveness

That means the update policy has to be built from **proxy signals**.

The practical design goals are:

- detect when the indexed collection is lagging behind the live collection
- detect when document ingestion spikes make the current index stale faster than usual
- separate "collection changed a lot" from "collection changed only a little"
- keep the metrics simple enough to compute every week

## One-Page Table

| Metric | Why We Designed It | If It Triggers, The Problem Is | Main Risk If Overused |
| --- | --- | --- | --- |
| `velocity_per_day` | detect sudden ingestion bursts | the corpus changed very fast this week | can cause too many updates during high-ingestion periods |
| `staleness_rate` | measure how old the indexed content mix has become | too much of the index is stale | can stay high for long periods in accumulated collections |
| `coverage_gap` | measure how far the index has drifted from the live corpus size | the index is under-covering the live collection | can look permanently large if the anchor is old |
| `temporal_gap_growth_days` | compare time-lag against the baseline state | the collection time profile is worsening relative to baseline | less decisive than velocity in the current setup |
| `staleness_rate + coverage_gap` | catch structural drift rather than a one-week burst | the index is both too old and too incomplete | still needs judgment if the collection is structurally historical |

## Metrics We Use

The current policy mainly relies on these monitoring metrics:

1. `velocity_per_day`
2. `staleness_rate`
3. `coverage_gap`
4. `temporal_gap_growth_days`

In the current final policy, the first three matter most in practice.

## 1. `velocity_per_day`

Definition:

- weekly new documents divided by `7`

Why we designed it:

- this is the most direct signal of how fast the collection is changing right now
- a sudden ingestion spike means the current index can become outdated very quickly
- it is cheap to compute and easy to interpret

What problem it is trying to catch:

- the corpus is expanding much faster than the recent baseline
- even if the current index is still usable, it may become obsolete soon if we do nothing

What it means when this metric is high:

- a large update wave has arrived
- the collection changed faster than normal
- the index may soon underrepresent newly ingested content

What can go wrong if we rely on it too much:

- it can fire repeatedly during high-ingestion periods
- it may recommend updates even when the newly added documents do not help the current qrels
- this is exactly why velocity-heavy policies can become update-happy

## 2. `staleness_rate`

Definition:

- the fraction of documents considered stale under the chosen stale-age rule

Why we designed it:

- we need a direct notion of how old the indexed content mix has become
- raw document counts alone do not tell us whether the index is dominated by old material
- this metric gives a compact age-health view of the indexed collection

What problem it is trying to catch:

- the indexed document set is too old relative to the current monitoring week
- even without a huge ingestion spike, the collection may have aged into a stale state

What it means when this metric is high:

- too much of the indexed content now falls on the old side of the age threshold
- the index is increasingly dominated by stale material

What can go wrong if we rely on it too much:

- in a historically accumulated collection, staleness can stay high for long periods
- once it becomes high, it may keep signaling trouble even when weekly growth is modest
- by itself it is too blunt, so we pair it with `coverage_gap`

## 3. `coverage_gap`

Definition:

- the amount of collection growth since the last indexed anchor, normalized by the index size at that anchor

Why we designed it:

- we need a direct measure of how far the live collection has drifted from the indexed collection
- document velocity is local to one week; coverage gap tracks accumulated drift
- this helps distinguish a small transient spike from a sustained indexing lag

What problem it is trying to catch:

- the index no longer covers enough of what is now in the live collection
- the mismatch between indexed state and current collection state has become too large

What it means when this metric is high:

- many documents have arrived since the last effective index anchor
- the index is representing only a shrinking fraction of the live corpus

What can go wrong if we rely on it too much:

- if the anchor is old, coverage gap can remain huge for a long time
- this can make the policy look permanently overdue for updates
- that is why it works better as a joint condition with `staleness_rate`, not as a standalone trigger

## 4. `temporal_gap_growth_days`

Definition:

- how much the temporal gap has grown relative to the baseline temporal gap

Why we designed it:

- this was meant to capture whether the collection's mean document date is falling farther behind the monitoring time
- unlike raw staleness, it tracks movement relative to a baseline state

What problem it is trying to catch:

- the document-time center of mass is drifting backward relative to where we started
- the collection may be aging in a structurally meaningful way

What it means when this metric is high:

- the effective age lag has grown materially
- the collection-time profile is worse than the baseline profile

What can go wrong if we rely on it too much:

- in the current outputs, this metric is not the practical driver
- it is less informative than velocity for sharp bursts
- it is also less directly actionable than coverage gap for accumulated drift

In the final current timeline, this metric does not end up being the decisive trigger.

## Why These Metrics Work Better Together

Each metric corresponds to a different failure mode:

- `velocity_per_day`: sudden weekly ingestion shock
- `staleness_rate`: too much old material in the indexed mix
- `coverage_gap`: accumulated divergence from the live corpus
- `temporal_gap_growth_days`: worsening time-lag relative to baseline

The design principle is:

- use `velocity_per_day` for burst detection
- use `staleness_rate + coverage_gap` together for structural drift detection

This is why the current policy effectively behaves like:

- update on strong ingestion bursts
- also update when the index is both stale and under-covering the live collection

## What "Falling Under" a Metric Means

In practical reading:

- if a week falls under `velocity_per_day`, the problem is:
  - the corpus changed very fast this week
- if a week falls under `staleness_rate`, the problem is:
  - too much of the indexed collection is old
- if a week falls under `coverage_gap`, the problem is:
  - the index has drifted too far away from the live collection size
- if a week falls under `staleness_rate + coverage_gap`, the problem is:
  - the index is both too old and too incomplete
- if a week falls under `temporal_gap_growth_days`, the problem is:
  - the time-lag profile is materially worse than the baseline

That is the intended semantics of the trigger logic.

## Final Interpretation

The current update policy should be understood as a **proxy-based monitoring
system**:

- it does not claim to directly measure weekly retrieval effectiveness
- it measures collection drift and update pressure
- it turns those signals into a practical weekly update recommendation

In the current final timeline, the dominant issue is:

- repeated `velocity_per_day` spikes

And the main structural backup condition is:

- `staleness_rate + coverage_gap`

So the metric design is intentionally split between:

- burst-sensitive change detection
- slower structural drift detection

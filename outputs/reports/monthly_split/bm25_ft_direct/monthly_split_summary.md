# Snapshot-1 Month Split Evaluation

| Split | Date Field | Months | Queries | Docs | nDCG@10 | nDCG@1000 | MAP | Recall@100 | Recall@1000 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| march_only | publishedDate | 3 | 74 | 173031 | 0.2942 | 0.3173 | 0.2676 | 0.4527 | 0.4595 |
| march_april | publishedDate | 3,4 | 92 | 343421 | 0.3091 | 0.3505 | 0.2718 | 0.5580 | 0.5906 |
| march_april_may | publishedDate | 3,4,5 | 96 | 525293 | 0.3374 | 0.4039 | 0.3012 | 0.5995 | 0.6525 |
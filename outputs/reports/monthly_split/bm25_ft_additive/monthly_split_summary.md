# Snapshot-1 Month Split Evaluation

| Split | Date Field | Months | Queries | Docs | nDCG@10 | nDCG@1000 | MAP | Recall@100 | Recall@1000 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| march_only | publishedDate | 3 | 74 | 173031 | 0.2382 | 0.2678 | 0.2042 | 0.4527 | 0.4595 |
| march_april | publishedDate | 3,4 | 92 | 343421 | 0.2290 | 0.2888 | 0.1922 | 0.5580 | 0.5906 |
| march_april_may | publishedDate | 3,4,5 | 96 | 525293 | 0.2501 | 0.3396 | 0.2161 | 0.5995 | 0.6525 |
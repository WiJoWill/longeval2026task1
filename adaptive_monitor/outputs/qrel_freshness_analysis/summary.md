# Qrel Freshness Analysis

This report checks whether `snapshot-1-train` queries still gain new judged-relevant
documents during the March-May 2025 adaptive reindexing window.

## Headline

- Queries with dated relevant docs: `100`
- Total relevant docs: `1087`
- Relevant docs with parsed `publishedDate`: `1012`
- Relevant docs missing parsed `publishedDate`: `75`
- Queries whose latest dated relevant doc is before `2025-03-01`: `100` / `100`
- Queries whose latest dated relevant doc is on or before `2025-03-31`: `100` / `100`
- Queries whose latest 5 relevant docs are all before `2025-03-01`: `100` / `100`

Interpretation:
For the dated portion of the qrels, every query already has all of its judged-relevant
documents before the March 2025 evaluation window starts. Reindexing through March,
April, and May therefore does not expose new judged-relevant answers for these queries;
it mostly enlarges the candidate set with additional non-relevant competitors.

## Latest Relevant Date Examples

| Query ID | Relevant Docs | Dated | Missing Date | Latest Relevant Published Date | Query Text |
| --- | ---: | ---: | ---: | --- | --- |
| 072f1af47be326cbe50092e56576c209 | 16 | 16 | 0 | 2025-02-23 | character narrative analysis in animated series |
| 1f50741d080a161ff0cde0b31cfd685e | 7 | 7 | 0 | 2025-02-01 | extracurricular activities |
| cc613b02ecdaf8f4e2e025008eb8680c | 5 | 5 | 0 | 2025-01-31 | ai in education |
| 9e8e1070b5a2631b490a235c3e49eea8 | 12 | 8 | 4 | 2025-01-21 | socio-economic status |
| 32dcf5f64658b023229d877bf4a86084 | 10 | 10 | 0 | 2025-01-21 | cyberbullying |
| c5090df276f619e3516a862007a521d3 | 17 | 17 | 0 | 2025-01-18 | the long-term development of athletes |
| d606782194b6084ebfe957206e386d01 | 34 | 34 | 0 | 2025-01-01 | progesterone supplementation menopause |
| b5add364fa0fea003903862eb30c4ba1 | 6 | 6 | 0 | 2024-12-31 | marketing and ai |
| 721f5289656546b698a36571b2d86c4b | 34 | 34 | 0 | 2024-12-31 | cold chain logistics for pharmaceuticals |
| f86f41648ba908f4c469ef17802f0511 | 13 | 13 | 0 | 2024-12-08 | school marketing services |

## Latest Relevant Month Distribution

| Month | Query Count |
| --- | ---: |
| 2009-01 | 1 |
| 2010-01 | 1 |
| 2012-01 | 1 |
| 2012-09 | 1 |
| 2013-09 | 1 |
| 2013-11 | 2 |
| 2016-01 | 1 |
| 2016-07 | 1 |
| 2017-01 | 4 |
| 2017-02 | 1 |
| 2017-06 | 1 |
| 2017-09 | 1 |
| 2017-11 | 1 |
| 2018-01 | 2 |
| 2018-04 | 1 |
| 2019-01 | 3 |
| 2019-07 | 2 |
| 2019-10 | 1 |
| 2020-01 | 2 |
| 2020-03 | 2 |
| 2020-06 | 1 |
| 2020-07 | 1 |
| 2021-01 | 1 |
| 2021-06 | 1 |
| 2021-09 | 1 |
| 2021-11 | 1 |
| 2022-01 | 1 |
| 2022-04 | 1 |
| 2022-05 | 1 |
| 2022-06 | 2 |
| 2022-07 | 1 |
| 2022-12 | 1 |
| 2023-01 | 1 |
| 2023-04 | 1 |
| 2023-06 | 1 |
| 2023-07 | 2 |
| 2023-08 | 1 |
| 2023-09 | 2 |
| 2023-12 | 2 |
| 2024-01 | 6 |
| 2024-03 | 2 |
| 2024-04 | 1 |
| 2024-05 | 4 |
| 2024-06 | 4 |
| 2024-07 | 5 |
| 2024-08 | 2 |
| 2024-09 | 2 |
| 2024-10 | 2 |
| 2024-11 | 6 |
| 2024-12 | 6 |
| 2025-01 | 5 |
| 2025-02 | 2 |

## Top-5 Latest Relevant Docs Distribution

Definition: for each query, sort its dated relevant documents by `publishedDate` descending
and take the latest five. This captures the freshest judged-relevant evidence available
to that query before the March-May 2025 reindex window.

| Month | Count Across Query Top-5 Sets |
| --- | ---: |
| 1941-01 | 1 |
| 2005-09 | 1 |
| 2005-12 | 1 |
| 2006-01 | 2 |
| 2007-01 | 1 |
| 2009-01 | 1 |
| 2009-03 | 1 |
| 2010-01 | 3 |
| 2010-11 | 1 |
| 2011-01 | 2 |
| 2011-04 | 1 |
| 2011-09 | 2 |
| 2011-11 | 2 |
| 2012-01 | 4 |
| 2012-03 | 1 |
| 2012-04 | 3 |
| 2012-06 | 2 |
| 2012-07 | 1 |
| 2012-09 | 1 |
| 2013-01 | 4 |
| 2013-02 | 2 |
| 2013-05 | 1 |
| 2013-06 | 1 |
| 2013-07 | 1 |
| 2013-09 | 2 |
| 2013-11 | 2 |
| 2014-01 | 2 |
| 2014-10 | 1 |
| 2015-01 | 4 |
| 2015-04 | 1 |
| 2015-06 | 1 |
| 2016-01 | 10 |
| 2016-03 | 2 |
| 2016-04 | 3 |
| 2016-06 | 1 |
| 2016-07 | 1 |
| 2016-08 | 1 |
| 2016-09 | 1 |
| 2016-10 | 1 |
| 2016-11 | 1 |
| 2016-12 | 1 |
| 2017-01 | 9 |
| 2017-02 | 1 |
| 2017-04 | 1 |
| 2017-05 | 2 |
| 2017-06 | 3 |
| 2017-07 | 1 |
| 2017-09 | 2 |
| 2017-10 | 1 |
| 2017-11 | 1 |
| 2017-12 | 1 |
| 2018-01 | 12 |
| 2018-03 | 1 |
| 2018-04 | 2 |
| 2018-05 | 2 |
| 2018-06 | 2 |
| 2018-08 | 2 |
| 2018-10 | 1 |
| 2019-01 | 13 |
| 2019-02 | 3 |
| 2019-03 | 2 |
| 2019-04 | 1 |
| 2019-05 | 2 |
| 2019-07 | 3 |
| 2019-10 | 2 |
| 2019-11 | 1 |
| 2019-12 | 6 |
| 2020-01 | 10 |
| 2020-02 | 1 |
| 2020-03 | 3 |
| 2020-04 | 3 |
| 2020-05 | 3 |
| 2020-06 | 2 |
| 2020-07 | 2 |
| 2020-09 | 1 |
| 2020-11 | 1 |
| 2020-12 | 1 |
| 2021-01 | 13 |
| 2021-04 | 5 |
| 2021-05 | 3 |
| 2021-06 | 1 |
| 2021-08 | 2 |
| 2021-09 | 3 |
| 2021-10 | 1 |
| 2021-11 | 1 |
| 2021-12 | 3 |
| 2022-01 | 11 |
| 2022-03 | 4 |
| 2022-04 | 4 |
| 2022-05 | 4 |
| 2022-06 | 3 |
| 2022-07 | 2 |
| 2022-10 | 3 |
| 2022-11 | 1 |
| 2022-12 | 2 |
| 2023-01 | 11 |
| 2023-02 | 3 |
| 2023-03 | 1 |
| 2023-04 | 4 |
| 2023-05 | 2 |
| 2023-06 | 8 |
| 2023-07 | 3 |
| 2023-08 | 1 |
| 2023-09 | 5 |
| 2023-10 | 1 |
| 2023-11 | 5 |
| 2023-12 | 11 |
| 2024-01 | 20 |
| 2024-03 | 3 |
| 2024-04 | 3 |
| 2024-05 | 8 |
| 2024-06 | 15 |
| 2024-07 | 10 |
| 2024-08 | 3 |
| 2024-09 | 4 |
| 2024-10 | 4 |
| 2024-11 | 8 |
| 2024-12 | 9 |
| 2025-01 | 7 |
| 2025-02 | 2 |

## Per-Query Top-5 Latest Relevant Dates

| Query ID | Top-5 Latest Relevant Dates | Query Text |
| --- | --- | --- |
| 072f1af47be326cbe50092e56576c209 | 2025-02-23, 2024-12-19, 2023-09-29, 2022-10-14, 2022-01-20 | character narrative analysis in animated series |
| 0b155c7fdc95ddd69962e106dfaed576 | 2017-01-01, 2016-10-01, 2015-01-01, 2013-07-18, 2012-04-01 | wagner soldier |
| 0e8e69ebcd11bc70aeb0102176cbf69b | 2024-05-15, 2020-01-01, 2019-01-01, 2013-02-26, 2013-01-01 | fish based paper |
| 10fdb11b13fff4b822ddc239ad6f3969 | 2024-12-01, 2023-01-01, 2022-01-01, 2020-11-20, 2020-04-22 | vegetarian protein |
| 1200cc678dce697633576f9941994baa | 2020-07-03, 2020-01-01, 2019-01-01, 2019-01-01, 2018-01-01 | psychology human behavior |
| 123cf37ccef0961a82918ad95c391866 | 2024-09-10, 2023-06-30, 2023-04-21, 2021-09-22, 2021-08-01 | library marketing and social media |
| 14d317d015117766bee743c1503b9307 | 2024-05-10 | remote working |
| 161820e44e7022cf44fd99a59bce5792 | 2024-12-01, 2024-11-13, 2024-08-27, 2024-01-01, 2023-12-19 | zero trust security in cybersecurity |
| 19a43a2b512e5ddd5e1b336c958b892e | 2023-01-01, 2022-04-15 | lgbtq youth tiktok |
| 1a2f5d355af40cba5cc9ad1ffddd114e | 2023-08-01, 2023-05-01, 2022-03-28, 2022-01-01, 2019-07-01 | pirineos |
| 1c6ca51a558f678acf1b1d1a8b145f54 | 2024-07-01, 2021-05-01, 2020-01-24, 2018-01-01 | teacher and student relationship |
| 1f4a02148d3138e7a04d14cca49f0f4e | 2024-01-01, 2021-01-01, 2019-05-22, 2018-06-18, 2017-05-01 | privacy by design |
| 1f50741d080a161ff0cde0b31cfd685e | 2025-02-01, 2024-05-01, 2023-12-01, 2020-12-01, 2017-01-01 | extracurricular activities |
| 21e8c323e168b0813eff14fdac972f1f | 2021-09-02, 2021-09-01, 2020-07-31 | online education bangladesh |
| 23b98abd4686855f0ed05c6d1a01e2b9 | 2023-07-06, 2021-01-01, 2020-01-01, 2019-03-17, 2019-01-01 | sources of academic stress |
| 25affb391b5a4052cc6750a79fd6162f | 2017-06-01 | proper generalized decomposition |
| 27d5a858b54377ad38312dc515812683 | 2010-01-01 | teenage pregnancy |
| 286b151fe9f88f9457878c2655e4f2da | 2024-11-12, 2024-10-29, 2024-06-30, 2024-01-01, 2023-11-15 | university research and sustainable development goals |
| 2d885b04956ddd2e729af5d7e6f50384 | 2023-07-31, 2018-01-16, 2018-01-01, 2017-06-26, 2016-01-01 | relationship between student engagement and academic outcomes |
| 2eff8040c4e28557c51361ab9b8db57d | 2023-09-01, 2019-12-29, 2019-12-29, 2019-11-30, 2019-10-02 | zero trust security in cse |

## Files

- `per_query_latest_relevant_dates.csv`
- `per_query_top5_latest_relevant_dates.csv`
- `qrel_freshness_summary.json`
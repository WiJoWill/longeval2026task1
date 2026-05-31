# Snapshot-1 Train Comparison Across All Current Models

Total current models in this report: `20`

Model families:
- 5 base models
- 3 fusion models
- 6 temporal models
- 6 temporal_citation models

## DCTR Results

| Method | Family | nDCG@10 | nDCG@1000 | MAP | Recall@100 | Recall@1000 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| bm25_ft_direct | temporal | 0.3588 | 0.5295 | 0.3123 | 0.7731 | 0.9245 |
| custom_lexical_fulltext_temporal | temporal | 0.3588 | 0.5295 | 0.3123 | 0.7731 | 0.9245 |
| custom_lexical_fulltext_temporal_citation | temporal_citation | 0.3588 | 0.5295 | 0.3123 | 0.7731 | 0.9245 |
| bm25_ft_additive | temporal_citation | 0.3312 | 0.5088 | 0.2863 | 0.7394 | 0.9245 |
| bm25_ft_router | temporal_citation | 0.3311 | 0.5087 | 0.2861 | 0.7394 | 0.9245 |
| custom_lexical_fulltext | base | 0.3302 | 0.5077 | 0.2853 | 0.7394 | 0.9245 |
| bm25_ft_citation_only | temporal_citation | 0.3302 | 0.5077 | 0.2853 | 0.7394 | 0.9245 |
| custom_title_abstract_rerank | base | 0.3222 | 0.4821 | 0.2777 | 0.6952 | 0.8581 |
| rrf_bm25_ft_dense_ta | fusion | 0.3175 | 0.5173 | 0.2749 | 0.7806 | 0.9667 |
| official_pyterrier_dense_temporal | temporal | 0.3069 | 0.4629 | 0.2551 | 0.6400 | 0.8613 |
| rrf_bm25_ta_bm25_ft_dense_ta | fusion | 0.3028 | 0.5084 | 0.2572 | 0.7870 | 0.9806 |
| official_pyterrier | base | 0.2922 | 0.4564 | 0.2573 | 0.6836 | 0.8581 |
| official_pyterrier_dense | base | 0.2820 | 0.4483 | 0.2378 | 0.6390 | 0.8613 |
| custom_title_abstract_rm3 | base | 0.2781 | 0.4510 | 0.2402 | 0.6559 | 0.8701 |
| custom_title_abstract_rerank_temporal | temporal | 0.2680 | 0.4307 | 0.2354 | 0.5447 | 0.8581 |
| rrf_bm25_ta_dense_ta | fusion | 0.2665 | 0.4544 | 0.2203 | 0.6701 | 0.9023 |
| custom_title_abstract_rerank_temporal_citation | temporal_citation | 0.2543 | 0.4194 | 0.2220 | 0.5451 | 0.8581 |
| custom_title_abstract_rm3_temporal | temporal | 0.0154 | 0.1842 | 0.0144 | 0.0433 | 0.8701 |
| official_pyterrier_temporal | temporal | 0.0053 | 0.1750 | 0.0084 | 0.0298 | 0.8581 |
| official_pyterrier_temporal_citation | temporal_citation | 0.0046 | 0.1749 | 0.0085 | 0.0298 | 0.8581 |

## RAW Results

| Method | Family | nDCG@10 | nDCG@1000 | MAP | Recall@100 | Recall@1000 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| bm25_ft_direct | temporal | 0.3932 | 0.5734 | 0.3169 | 0.7665 | 0.9205 |
| custom_lexical_fulltext_temporal | temporal | 0.3932 | 0.5734 | 0.3169 | 0.7665 | 0.9205 |
| custom_lexical_fulltext_temporal_citation | temporal_citation | 0.3932 | 0.5734 | 0.3169 | 0.7665 | 0.9205 |
| bm25_ft_additive | temporal_citation | 0.3657 | 0.5515 | 0.2909 | 0.7324 | 0.9205 |
| bm25_ft_router | temporal_citation | 0.3656 | 0.5514 | 0.2906 | 0.7324 | 0.9205 |
| bm25_ft_citation_only | temporal_citation | 0.3637 | 0.5504 | 0.2899 | 0.7324 | 0.9205 |
| custom_lexical_fulltext | base | 0.3637 | 0.5504 | 0.2899 | 0.7324 | 0.9205 |
| rrf_bm25_ft_dense_ta | fusion | 0.3532 | 0.5648 | 0.2887 | 0.7741 | 0.9609 |
| official_pyterrier_dense_temporal | temporal | 0.3397 | 0.5042 | 0.2612 | 0.6349 | 0.8555 |
| custom_title_abstract_rerank | base | 0.3373 | 0.5152 | 0.2750 | 0.6836 | 0.8561 |
| rrf_bm25_ta_bm25_ft_dense_ta | fusion | 0.3343 | 0.5563 | 0.2714 | 0.7873 | 0.9747 |
| official_pyterrier | base | 0.3310 | 0.5034 | 0.2658 | 0.6831 | 0.8561 |
| official_pyterrier_dense | base | 0.3106 | 0.4875 | 0.2402 | 0.6379 | 0.8555 |
| custom_title_abstract_rm3 | base | 0.3074 | 0.4934 | 0.2469 | 0.6534 | 0.8688 |
| rrf_bm25_ta_dense_ta | fusion | 0.2993 | 0.4988 | 0.2330 | 0.6666 | 0.8990 |
| custom_title_abstract_rerank_temporal | temporal | 0.2869 | 0.4639 | 0.2375 | 0.5477 | 0.8561 |
| custom_title_abstract_rerank_temporal_citation | temporal_citation | 0.2712 | 0.4516 | 0.2230 | 0.5497 | 0.8561 |
| custom_title_abstract_rm3_temporal | temporal | 0.0129 | 0.2009 | 0.0107 | 0.0377 | 0.8688 |
| official_pyterrier_temporal_citation | temporal_citation | 0.0056 | 0.1949 | 0.0090 | 0.0304 | 0.8561 |
| official_pyterrier_temporal | temporal | 0.0055 | 0.1948 | 0.0089 | 0.0304 | 0.8561 |

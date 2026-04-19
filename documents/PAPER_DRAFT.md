# Improving Scientific Retrieval over Evolving Collections:
# Baseline Fusion, Temporal Reranking, and Update Triggers for LongEval-Sci

This is a working draft for our paper. It currently focuses on four core sections:

1. Introduction
2. Related Work
3. Methodology
4. Results

The update-trigger analysis is intentionally left as a marked placeholder for the next round of work.

## Title Candidates

- `Temporal-Aware Retrieval Adaptation for Longitudinal Scientific Search`
- `Improving LongEval-Sci Retrieval with Fusion, Reranking, and Temporal Update Signals`
- `From Strong Baselines to Temporal Robustness: Scientific Retrieval over Evolving Collections`

Working title:

> Improving Scientific Retrieval over Evolving Collections: Baseline Fusion, Temporal Reranking, and Update Triggers for LongEval-Sci

## 1. Introduction

### Bullet Outline

- Scientific search is longitudinal rather than static.
- Retrieval quality can change when new documents arrive, terminology shifts, or user needs become more time-sensitive.
- LongEval-Sci frames this explicitly through evolving snapshots of a scientific collection.
- In the 2026 setup, `snapshot-1` is the practical development snapshot, while later snapshots represent future retrieval conditions.
- Our current study asks three questions:
- How much can we improve over the official BM25 and dense baselines with non-temporal methods such as fusion, RM3, and reranking?
- Do lightweight temporal reranking features improve robustness under month-level collection growth?
- What signals might later support a decision about when a retrieval system should be updated?
- Current implemented contributions:
- strong baseline comparison across lexical, dense, fusion, expansion, reranking, and temporal variants
- month-based internal protocol over `snapshot-1`
- temporal robustness reporting with RI / DRI / ER / ARP / MARP
- Planned but not yet complete:
- update-trigger policy analysis for deciding when to refresh retrieval components

### Draft Prose

Scientific retrieval systems operate over collections that evolve continuously rather than over a single fixed corpus. New papers are published, terminology changes, topics mature, and user needs shift from foundational background search to current or rapidly changing evidence needs. A retrieval pipeline that is strong at one point in time may therefore become less reliable as the collection changes. Longitudinal evaluation is important precisely because it separates strong one-shot effectiveness from sustained robustness under collection growth.

LongEval-Sci 2026 Task 1 offers a useful setting for studying this problem. The benchmark provides three temporal snapshots of a scientific corpus and exposes `snapshot-1` as the main supervised development condition through training queries and qrels. In our work, we treat `snapshot-1 train` as the primary development split and use later conditions in two ways: first, as official future-facing evaluation settings when available, and second, through an internal month-based protocol within `snapshot-1` that simulates temporal drift without requiring repeated expensive reindexing.

Our current study is organized around two implemented stages and one planned stage. The first stage strengthens non-temporal baselines through lexical retrieval, dense retrieval, reciprocal rank fusion, RM3 query expansion, and reranking. The second stage adds temporal-aware reranking as a lightweight overlay using document-time metadata, query temporal intent, and citation-derived temporal features. The third stage, which is not yet complete, will study update-trigger policies for deciding when an IR system should remain unchanged, when temporal overlays are sufficient, and when larger refresh actions are warranted.

At this stage, our main contribution is an empirical baseline study for LongEval-Sci that compares a broad family of reusable retrieval enhancements while keeping first-stage indexing deliberately small and stable. We additionally provide a month-based evaluation protocol and a temporal robustness analysis that begins to connect raw retrieval effectiveness to longitudinal system behavior.

## 2. Related Work

### Bullet Outline

- LongEval studies retrieval under evolving collections rather than static ranking only.
- Prior LongEval analysis showed that raw effectiveness and temporal robustness can disagree.
- Scientific retrieval in LongEval remains sensitive to snapshot shifts.
- Official 2026 scientific baselines include:
- PyTerrier BM25
- PyTerrier dense retrieval with Qwen embeddings
- Prior scientific retrieval work suggests:
- BM25 over strong document fields remains highly competitive
- dense retrieval plus reranking can add semantic gains
- rank fusion, expansion, and incremental overlays are practical alternatives to end-to-end retraining
- OpenWebSearch motivates:
- RM3 / reformulation
- fusion over existing rankings
- query-intent-aware strategy variation
- temporal retrieval literature motivates:
- time-aware reranking
- temporal relevance as a complement to semantic relevance
- future update-trigger reasoning

### Draft Prose

LongEval treats retrieval as a longitudinal problem rather than a single static ranking task. Earlier overview results from the benchmark highlighted an important point for model development: methods that are strongest on raw effectiveness measures are not always the most stable under temporal change. This distinction is especially relevant in scientific retrieval, where ranking behavior can be sensitive to snapshot shifts as newer documents enter the collection and relevance patterns evolve over time.

Within scientific retrieval, both lexical and dense baselines remain important reference points. The official LongEval-Sci baselines use a PyTerrier BM25 pipeline and a PyTerrier dense pipeline based on Qwen embeddings. Prior work in scientific search also suggests that document representation matters substantially: title-and-abstract views often support compact and semantically focused retrieval, while full text can provide stronger lexical coverage. This motivates our decision to keep both title+abstract and full-text retrieval views in our experimental design.

Our non-temporal improvements are influenced by work on fusion, query expansion, and reranking. Reciprocal Rank Fusion is attractive because it combines heterogeneous rankers without assuming score comparability. RM3-style pseudo-relevance feedback remains a standard lexical reformulation technique for improving recall under vocabulary mismatch. OpenWebSearch’s LongEval system further motivates a design philosophy based on incremental overlays over strong first-stage rankings rather than repeated full-system replacement: reformulate queries, fuse complementary rankings, and add routing or reranking only where it helps.

Temporal retrieval work provides the bridge to our second stage. The broader literature suggests that semantic relevance alone is insufficient for queries that imply recency, change, or evolving evidence. Instead of rebuilding indices for each temporal condition, a practical alternative is to add temporal awareness as a reranking layer over existing retrieval results. That view aligns well with the current LongEval-Sci setup and naturally leads to our longer-term question of when a retrieval system should be updated at all. We retain that update-trigger perspective as a reserved section of the paper because it is central to the larger research agenda, even though it is not yet fully implemented in this draft.

## 3. Methodology

### Bullet Outline

- Data and protocol:
- LongEval-Sci 2026 Task 1
- three snapshots spanning March-May, June-August, and September-November 2025
- `snapshot-1 train` used for development
- raw and DCTR qrels used when available
- Canonical first-stage representations:
- title+abstract lexical index
- full-text lexical index
- official dense title+abstract retrieval
- Phase 1: non-temporal baselines
- `official_pyterrier`
- `official_pyterrier_dense`
- `custom_lexical_fulltext`
- `custom_title_abstract_rm3`
- `custom_title_abstract_rerank`
- Phase 1 extensions:
- RRF over existing run files, not new indices
- main fusion variants:
- BM25 TA + Dense TA
- BM25 FT + Dense TA
- BM25 TA + BM25 FT + Dense TA
- Phase 2: temporal overlays
- temporal intent categories
- metadata features using `publishedDate` as primary field
- `createdDate` fallback if needed
- `updatedDate` disabled by default because it often falls outside the useful development window
- citation-aware temporal features from OpenCitations
- temporal overlays reuse existing runs and do not rebuild first-stage indices
- Evaluation:
- whole-train effectiveness on `snapshot-1 train`
- month-growth evaluation using cumulative `march_only`, `march_april`, `march_april_may`
- temporal change metrics relative to `official_pyterrier`
- Reserved future subsection:
- update-trigger policy and timing of system refresh

### Draft Prose

We use the LongEval-Sci 2026 Task 1 collection and organize our implementation around a conservative development protocol. `snapshot-1 train` is treated as the main supervised setting for model design, while later conditions are reserved for temporal evaluation. To keep the system maintainable, we intentionally limit first-stage indexing to two lexical text views and one official dense view: a title+abstract lexical index, a full-text lexical index, and the official dense title+abstract retrieval backend. Subsequent improvements are implemented as overlays on top of those first-stage artifacts rather than as repeated reindexing experiments.

Our first phase focuses on non-temporal baseline improvement. We start from the official lexical PyTerrier BM25 baseline and the official dense Qwen baseline, then add three custom variants: a full-text lexical model, a title+abstract RM3 expansion model, and a title+abstract reranking model. These provide complementary design points for testing document field choice, query reformulation, and neural reranking. We further build run-level RRF fusion systems by combining existing run outputs instead of modifying retrieval backends. In this setup, RRF serves as a cheap fusion layer over BM25 title+abstract, BM25 full text, and dense title+abstract runs.

Our second phase adds temporal-aware reranking as a lightweight overlay. Temporal features are computed relative to the active evaluation cutoff, with `publishedDate` used as the primary temporal field and `createdDate` retained as a fallback when publication metadata is missing. We disable `updatedDate` by default because it frequently falls outside the intended development window and introduces misleading recency signals. The temporal overlay combines query temporal intent, document age and freshness features, and optionally citation-derived temporal signals computed from the local OpenCitations graph. Importantly, these temporal methods are applied after retrieval, allowing us to reuse existing indices and run files instead of rebuilding first-stage retrieval structures.

To evaluate both effectiveness and robustness, we use three complementary protocols. The first is standard whole-train evaluation on `snapshot-1 train`, reported with nDCG@10, nDCG@1000, MAP, Recall@100, and Recall@1000. The second is a cumulative month-growth evaluation over `snapshot-1`, using `march_only`, `march_april`, and `march_april_may` as internal temporal conditions. This protocol simulates corpus growth without requiring month-specific reindexing. The third is a temporal change analysis that computes RI, DRI, ER, ARP, and MARP relative to the BM25 pivot system. Together, these three views let us distinguish absolute effectiveness from temporal stability.

We intentionally leave one methodology component as future work: the timing of system updates. Our intended third phase will treat update decisions as an operational policy problem, asking when a system should do nothing, apply a fusion or temporal overlay, refresh an index, or retrain a reranker. The current draft reserves space for this analysis but does not yet present a completed trigger model.

## 4. Results

### Bullet Outline

- Whole-train `snapshot-1 train` results currently cover 16 models.
- Best base model on DCTR:
- `custom_lexical_fulltext` with `nDCG@10 = 0.3302`
- Strongest reranking-only base:
- `custom_title_abstract_rerank` with `nDCG@10 = 0.3222`
- Best fusion model on whole-train DCTR:
- `rrf_bm25_ft_dense_ta` with `nDCG@10 = 0.3175`
- highest Recall@1000 among compared strong systems:
- `rrf_bm25_ta_bm25_ft_dense_ta` with `Recall@1000 = 0.9806`
- Best temporal sibling on whole-train DCTR:
- `official_pyterrier_dense_temporal` with `nDCG@10 = 0.3069`
- Citation-aware temporal models remain mixed:
- `custom_title_abstract_rerank_temporal_citation` is best among them with `nDCG@10 = 0.2543`
- Monthly growth:
- `rrf_bm25_ft_dense_ta` is best on all three cumulative month splits
- `official_pyterrier_dense_temporal` is the strongest temporal sibling under month growth
- Temporal change:
- absolute month-growth winners are not always the most pivot-stable
- `official_pyterrier_dense_temporal` stays relatively close to the BM25 pivot on long transition DRI
- several lexical temporal overlays are too aggressive and collapse whole-train effectiveness
- Reserved future discussion:
- update-trigger analysis will connect these robustness changes to system refresh decisions later

### Draft Prose

Our current experiments cover 16 models across four families: five base systems, five temporal sibling systems, three citation-aware temporal systems, and three RRF fusion systems. On whole-train DCTR evaluation, the strongest base model is `custom_lexical_fulltext`, which reaches an nDCG@10 of 0.3302. This result reinforces the importance of document field choice in LongEval-Sci: a strong lexical full-text representation remains difficult to beat. The strongest purely reranking-oriented base system is `custom_title_abstract_rerank`, which reaches 0.3222 nDCG@10 and remains competitive across multiple metrics.

Among fusion approaches, the most effective whole-train system is `rrf_bm25_ft_dense_ta`, which achieves 0.3175 nDCG@10 and substantially improves recall. The three-way fusion variant `rrf_bm25_ta_bm25_ft_dense_ta` does not surpass the best full-text lexical baseline on nDCG@10, but it yields the highest Recall@1000 at 0.9806. This suggests that fusion is especially effective as a coverage-enhancing mechanism, even when it does not always produce the best top-rank precision. In contrast, the `rrf_bm25_ta_dense_ta` variant underperforms the full-text-aware alternatives, indicating that full-text lexical evidence remains an important ingredient in this collection.

The temporal results are more mixed. The strongest temporal sibling on whole-train DCTR is `official_pyterrier_dense_temporal`, with nDCG@10 = 0.3069. This shows that temporal reranking can be useful when applied over the dense baseline, but the same effect does not transfer uniformly across model families. Several lexical temporal overlays remain far too aggressive, leading to severe drops in whole-train effectiveness. Citation-aware temporal reranking also produces uneven results: `custom_title_abstract_rerank_temporal_citation` is the strongest citation-enhanced model at 0.2543 nDCG@10, yet it still falls short of its non-citation temporal sibling and well below the strongest non-temporal baselines.

The month-growth evaluation highlights a second important lesson: the strongest system in absolute terms is not always the most stable relative to the BM25 pivot. On the cumulative `march_only`, `march_april`, and `march_april_may` evaluations, `rrf_bm25_ft_dense_ta` is the best model by nDCG@10 on all three splits, reaching 0.2732, 0.2849, and 0.2930 respectively. However, temporal change analysis shows that some methods with strong absolute month-level scores still diverge more from the BM25 pivot than others. For example, `official_pyterrier_dense_temporal` remains comparatively close to the pivot on the longest `march_only -> march_april_may` transition, while several other systems achieve stronger absolute scores at the cost of larger DRI values. This supports the central LongEval intuition that raw effectiveness and temporal robustness should be analyzed separately rather than treated as the same objective.

Finally, the current results also tell us what not to overclaim. Our temporal layer is promising but not yet mature, especially for lexical branches. The strongest overall systems are still non-temporal full-text and fusion-based methods, while temporal reranking helps selectively rather than universally. This makes the next step especially clear: we need a better understanding of when temporal adaptation is worth applying at all. That question naturally leads to the reserved update-trigger section, where future work will connect retrieval degradation, instability, and corpus drift to concrete system refresh decisions.

## Reserved Section for Next Round

The following section is intentionally not expanded yet, but the paper should later include it:

- **Update-Trigger Analysis**

Planned focus:

- when a retrieval system should remain unchanged
- when a lightweight overlay such as RRF or temporal reranking is sufficient
- when a full retrieval refresh or retraining step is justified

Planned signals:

- performance proxies
- retrieval instability
- corpus drift
- temporal mismatch between query type and top-ranked evidence

This section should become the bridge from descriptive longitudinal evaluation to operational retrieval adaptation.

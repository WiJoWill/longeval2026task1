"""Evaluate BM25 full-text baseline + 4 temporal overlay modes on snapshot-1 monthly splits."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from longeval_sci.baselines.runner import clone_for_train_eval
from longeval_sci.config import load_config
from longeval_sci.evaluation.monthly_split import evaluate_month_split, write_month_split_outputs
from longeval_sci.io.dataset import load_dataset_bundle
from longeval_sci.io.trec import read_trec_results, write_trec_run
from longeval_sci.temporal.rerank import temporal_rerank_results
from longeval_sci.utils.logging import configure_logging
from longeval_sci.utils.paths import ensure_parent

SNAPSHOT_ID = "snapshot-1"
DATE_FIELD = "publishedDate"
MONTHLY_SPLITS = [
    {"name": "march_only", "months": [3]},
    {"name": "march_april", "months": [3, 4]},
    {"name": "march_april_may", "months": [3, 4, 5]},
]
TEMPORAL_MODES = {
    "bm25_ft_direct": "configs/custom_title_abstract_rerank_temporal.yaml",
    "bm25_ft_citation_only": "configs/custom_title_abstract_rerank_citation_only.yaml",
    "bm25_ft_additive": "configs/custom_title_abstract_rerank_additive.yaml",
    "bm25_ft_router": "configs/custom_title_abstract_rerank_router.yaml",
}


def _apply_overlay(
    run_name: str,
    config_path: str,
    bm25_run_path: Path,
    bundle,
    qrels_variant: str,
) -> Path:
    config = load_config(config_path)
    config = clone_for_train_eval(config, qrels_variant=qrels_variant)
    config.run_name = run_name

    out_run_path = ROOT / "outputs" / run_name / f"{SNAPSHOT_ID}-train" / "run.txt"
    if out_run_path.exists():
        print(f"  [reuse] {run_name}: {out_run_path}")
        return out_run_path

    results = read_trec_results(bm25_run_path)
    reranked = temporal_rerank_results(results=results, bundle=bundle, config=config)
    ensure_parent(out_run_path)
    write_trec_run(reranked, out_run_path)
    print(f"  [done]  {run_name}: {out_run_path}")
    return out_run_path


def _eval_monthly_splits(
    run_name: str,
    run_path: Path,
    dataset_config,
    metrics: list[str],
    output_root: Path,
) -> None:
    results = []
    per_query_by_split: dict[str, list] = {}
    for split in MONTHLY_SPLITS:
        result, per_query_rows = evaluate_month_split(
            dataset_config=dataset_config,
            snapshot_id=SNAPSHOT_ID,
            run_path=run_path,
            metrics=metrics,
            date_field=DATE_FIELD,
            months=split["months"],
            split_name=split["name"],
        )
        results.append(result)
        per_query_by_split[split["name"]] = per_query_rows
        print(f"    {split['name']}: nDCG@10={result.metrics.get('ndcg_cut_10', 0):.4f}")
    output_dir = output_root / run_name
    write_month_split_outputs(results, per_query_by_split, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare BM25 + 4 temporal modes on monthly splits.")
    parser.add_argument(
        "--bm25-run",
        default="outputs/custom_lexical_fulltext/snapshot-1-train/run.txt",
        help="Path to existing BM25 full-text run file.",
    )
    parser.add_argument("--qrels-variant", default="dctr", choices=["dctr", "raw"])
    parser.add_argument(
        "--output-root",
        default="outputs/reports/monthly_split",
        help="Root for per-model monthly split reports.",
    )
    args = parser.parse_args()

    configure_logging()
    bm25_run_path = ROOT / args.bm25_run if not Path(args.bm25_run).is_absolute() else Path(args.bm25_run)
    if not bm25_run_path.exists():
        raise FileNotFoundError(f"BM25 run not found: {bm25_run_path}")

    output_root = Path(args.output_root)

    # Load dataset bundle once (shared across all modes)
    base_config = clone_for_train_eval(
        load_config("configs/custom_lexical_fulltext.yaml"),
        qrels_variant=args.qrels_variant,
    )
    bundle = load_dataset_bundle(base_config.dataset, SNAPSHOT_ID)
    metrics = base_config.metrics

    # BM25 baseline (no overlay)
    print("\n[1/5] BM25 baseline (no overlay)")
    _eval_monthly_splits("bm25_fulltext", bm25_run_path, base_config.dataset, metrics, output_root)

    # 4 temporal modes
    for i, (run_name, config_path) in enumerate(TEMPORAL_MODES.items(), start=2):
        print(f"\n[{i}/5] {run_name}")
        out_run = _apply_overlay(run_name, config_path, bm25_run_path, bundle, args.qrels_variant)
        # Use base dataset config (same queries/qrels) for evaluation
        _eval_monthly_splits(run_name, out_run, base_config.dataset, metrics, output_root)

    print(f"\nAll done. Reports in {output_root}/")
    print("Run `python scripts/build_monthly_split_summary.py` to aggregate.")


if __name__ == "__main__":
    main()

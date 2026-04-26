"""Build canonical first-stage indices for one baseline config."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from longeval_sci.baselines.runner import build_required_indices, clone_for_train_eval
from longeval_sci.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Build canonical indices required by a baseline config.")
    parser.add_argument("--config", required=True, help="Path to the baseline YAML config.")
    parser.add_argument("--snapshot-id", action="append", help="Limit indexing to one snapshot. Can be passed multiple times.")
    parser.add_argument("--train-snapshot1", action="store_true", help="Switch to snapshot-1 train mode before building.")
    parser.add_argument("--qrels-variant", default="dctr", choices=["dctr", "raw"], help="Qrels variant for train mode.")
    parser.add_argument("--batch-size", type=int, help="Override runtime batch size for embedding/reranking index builders.")
    parser.add_argument("--pyterrier-memory-mb", type=int, help="Override PyTerrier JVM heap size in MB.")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.train_snapshot1:
        config = clone_for_train_eval(config, qrels_variant=args.qrels_variant)
    if args.snapshot_id:
        config.dataset.snapshot_ids = args.snapshot_id
    if args.batch_size is not None:
        config.runtime.batch_size = args.batch_size
    if args.pyterrier_memory_mb is not None:
        config.runtime.pyterrier_memory_mb = args.pyterrier_memory_mb
    build_required_indices(config)


if __name__ == "__main__":
    main()

"""Analyze how fresh snapshot-1-train qrel documents are relative to the March-May 2025 window.

This answers a specific question for the adaptive reindexing setup:
if all judged-relevant documents for the train queries were already published before
the evaluation window begins, then reindexing through March-May 2025 mostly adds
non-relevant competitors rather than new relevant answers.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from longeval_sci.baselines.runner import clone_for_train_eval
from longeval_sci.config import load_config
from longeval_sci.io.dataset import load_dataset_bundle

CONFIG_PATH = ROOT / "configs" / "custom_lexical_fulltext.yaml"
SNAPSHOT_ID = "snapshot-1"
DATE_FIELD = "publishedDate"
WINDOW_START = datetime(2025, 3, 1, tzinfo=UTC)
MARCH_END = datetime(2025, 3, 31, 23, 59, 59, tzinfo=UTC)
APRIL_END = datetime(2025, 4, 30, 23, 59, 59, tzinfo=UTC)
MAY_END = datetime(2025, 5, 31, 23, 59, 59, tzinfo=UTC)


def _parse_dt(value: object) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


def _load_bundle():
    config = clone_for_train_eval(load_config(str(CONFIG_PATH)))
    bundle = load_dataset_bundle(config.dataset, SNAPSHOT_ID)
    if bundle.qrels is None:
        raise RuntimeError("No qrels found for snapshot-1-train.")
    return bundle


def analyze() -> tuple[list[dict], dict, list[dict]]:
    bundle = _load_bundle()
    doc_dates = {
        doc.doc_id: _parse_dt(doc.metadata.get(DATE_FIELD))
        for doc in bundle.documents
    }

    per_query_rows: list[dict] = []
    latest_months = Counter()
    top5_latest_months = Counter()
    total_relevant_docs = 0
    total_dated_relevant_docs = 0
    total_missing_date_docs = 0
    top5_rows: list[dict] = []

    for query in bundle.queries:
        docrels = bundle.qrels.get(query.query_id, {})
        relevant_doc_ids = [doc_id for doc_id, rel in docrels.items() if rel > 0]
        if not relevant_doc_ids:
            continue

        total_relevant_docs += len(relevant_doc_ids)
        dated = []
        missing = 0
        for doc_id in relevant_doc_ids:
            dt = doc_dates.get(doc_id)
            if dt is None:
                missing += 1
            else:
                dated.append(dt)
        total_dated_relevant_docs += len(dated)
        total_missing_date_docs += missing

        if not dated:
            continue

        latest_five = sorted(dated, reverse=True)[:5]
        earliest = min(dated)
        latest = max(dated)
        latest_months[latest.strftime("%Y-%m")] += 1
        for dt in latest_five:
            top5_latest_months[dt.strftime("%Y-%m")] += 1
        per_query_rows.append(
            {
                "query_id": query.query_id,
                "query_text": query.text,
                "relevant_doc_count": len(relevant_doc_ids),
                "dated_relevant_doc_count": len(dated),
                "missing_date_relevant_doc_count": missing,
                "earliest_relevant_published_date": earliest.date().isoformat(),
                "latest_relevant_published_date": latest.date().isoformat(),
                "all_relevant_docs_by_window_start": latest < WINDOW_START,
                "all_relevant_docs_by_march_end": latest <= MARCH_END,
                "all_relevant_docs_by_april_end": latest <= APRIL_END,
                "all_relevant_docs_by_may_end": latest <= MAY_END,
            }
        )
        top5_rows.append(
            {
                "query_id": query.query_id,
                "query_text": query.text,
                "top5_latest_relevant_dates": ", ".join(dt.date().isoformat() for dt in latest_five),
                "top5_latest_relevant_months": ", ".join(dt.strftime("%Y-%m") for dt in latest_five),
                "top5_latest_all_before_window_start": all(dt < WINDOW_START for dt in latest_five),
            }
        )

    per_query_rows.sort(
        key=lambda row: (
            row["latest_relevant_published_date"],
            row["query_id"],
        ),
        reverse=True,
    )

    total_queries = len(per_query_rows)
    summary = {
        "total_queries_with_relevant_docs": total_queries,
        "total_relevant_docs": total_relevant_docs,
        "total_dated_relevant_docs": total_dated_relevant_docs,
        "total_missing_date_relevant_docs": total_missing_date_docs,
        "queries_with_all_relevant_docs_by_window_start": sum(
            1 for row in per_query_rows if row["all_relevant_docs_by_window_start"]
        ),
        "queries_with_all_relevant_docs_by_march_end": sum(
            1 for row in per_query_rows if row["all_relevant_docs_by_march_end"]
        ),
        "queries_with_all_relevant_docs_by_april_end": sum(
            1 for row in per_query_rows if row["all_relevant_docs_by_april_end"]
        ),
        "queries_with_all_relevant_docs_by_may_end": sum(
            1 for row in per_query_rows if row["all_relevant_docs_by_may_end"]
        ),
        "latest_relevant_doc_month_distribution": dict(sorted(latest_months.items())),
        "top5_latest_relevant_doc_month_distribution": dict(sorted(top5_latest_months.items())),
        "queries_whose_latest_5_relevant_docs_are_all_before_window_start": sum(
            1 for row in top5_rows if row["top5_latest_all_before_window_start"]
        ),
        "window_start": WINDOW_START.date().isoformat(),
        "window_end": MAY_END.date().isoformat(),
        "date_field": DATE_FIELD,
        "snapshot_id": SNAPSHOT_ID,
    }
    top5_rows.sort(key=lambda row: row["query_id"])
    return per_query_rows, summary, top5_rows


def write_outputs(rows: list[dict], summary: dict, top5_rows: list[dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "per_query_latest_relevant_dates.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    top5_csv_path = output_dir / "per_query_top5_latest_relevant_dates.csv"
    with top5_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(top5_rows[0].keys()))
        writer.writeheader()
        writer.writerows(top5_rows)

    json_path = output_dir / "qrel_freshness_summary.json"
    json_path.write_text(
        json.dumps({"summary": summary, "per_query": rows, "per_query_top5_latest": top5_rows}, indent=2),
        encoding="utf-8",
    )

    latest_examples = rows[:10]
    md_lines = [
        "# Qrel Freshness Analysis",
        "",
        "This report checks whether `snapshot-1-train` queries still gain new judged-relevant",
        "documents during the March-May 2025 adaptive reindexing window.",
        "",
        "## Headline",
        "",
        f"- Queries with dated relevant docs: `{summary['total_queries_with_relevant_docs']}`",
        f"- Total relevant docs: `{summary['total_relevant_docs']}`",
        f"- Relevant docs with parsed `{DATE_FIELD}`: `{summary['total_dated_relevant_docs']}`",
        f"- Relevant docs missing parsed `{DATE_FIELD}`: `{summary['total_missing_date_relevant_docs']}`",
        f"- Queries whose latest dated relevant doc is before `{summary['window_start']}`: `{summary['queries_with_all_relevant_docs_by_window_start']}` / `{summary['total_queries_with_relevant_docs']}`",
        f"- Queries whose latest dated relevant doc is on or before `2025-03-31`: `{summary['queries_with_all_relevant_docs_by_march_end']}` / `{summary['total_queries_with_relevant_docs']}`",
        f"- Queries whose latest 5 relevant docs are all before `{summary['window_start']}`: `{summary['queries_whose_latest_5_relevant_docs_are_all_before_window_start']}` / `{summary['total_queries_with_relevant_docs']}`",
        "",
        "Interpretation:",
        "For the dated portion of the qrels, every query already has all of its judged-relevant",
        "documents before the March 2025 evaluation window starts. Reindexing through March,",
        "April, and May therefore does not expose new judged-relevant answers for these queries;",
        "it mostly enlarges the candidate set with additional non-relevant competitors.",
        "",
        "## Latest Relevant Date Examples",
        "",
        "| Query ID | Relevant Docs | Dated | Missing Date | Latest Relevant Published Date | Query Text |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in latest_examples:
        md_lines.append(
            f"| {row['query_id']} | {row['relevant_doc_count']} | {row['dated_relevant_doc_count']} "
            f"| {row['missing_date_relevant_doc_count']} | {row['latest_relevant_published_date']} | "
            f"{row['query_text'].replace('|', '/')} |"
        )

    md_lines.extend(
        [
            "",
            "## Latest Relevant Month Distribution",
            "",
            "| Month | Query Count |",
            "| --- | ---: |",
        ]
    )
    for month, count in summary["latest_relevant_doc_month_distribution"].items():
        md_lines.append(f"| {month} | {count} |")

    md_lines.extend(
        [
            "",
            "## Top-5 Latest Relevant Docs Distribution",
            "",
            "Definition: for each query, sort its dated relevant documents by `publishedDate` descending",
            "and take the latest five. This captures the freshest judged-relevant evidence available",
            "to that query before the March-May 2025 reindex window.",
            "",
            "| Month | Count Across Query Top-5 Sets |",
            "| --- | ---: |",
        ]
    )
    for month, count in summary["top5_latest_relevant_doc_month_distribution"].items():
        md_lines.append(f"| {month} | {count} |")

    md_lines.extend(
        [
            "",
            "## Per-Query Top-5 Latest Relevant Dates",
            "",
            "| Query ID | Top-5 Latest Relevant Dates | Query Text |",
            "| --- | --- | --- |",
        ]
    )
    for row in top5_rows[:20]:
        md_lines.append(
            f"| {row['query_id']} | {row['top5_latest_relevant_dates']} | {row['query_text'].replace('|', '/')} |"
        )

    md_lines.extend(
        [
            "",
            "## Files",
            "",
            "- `per_query_latest_relevant_dates.csv`",
            "- `per_query_top5_latest_relevant_dates.csv`",
            "- `qrel_freshness_summary.json`",
        ]
    )

    (output_dir / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")


def write_plots(summary: dict, output_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available; skipping plot generation")
        return

    latest_dist = summary["latest_relevant_doc_month_distribution"]
    top5_dist = summary["top5_latest_relevant_doc_month_distribution"]

    months = sorted(set(latest_dist) | set(top5_dist))
    latest_values = [latest_dist.get(month, 0) for month in months]
    top5_values = [top5_dist.get(month, 0) for month in months]

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True, gridspec_kw={"height_ratios": [1, 1.4]})

    axes[0].bar(months, latest_values, color="#4C78A8")
    axes[0].set_ylabel("Queries")
    axes[0].set_title("Latest Relevant Doc Month Per Query")
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].bar(months, top5_values, color="#F58518")
    axes[1].set_ylabel("Top-5 Doc Count")
    axes[1].set_title("Top-5 Latest Relevant Docs Month Distribution")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].set_xlabel("Published Month")

    tick_step = max(1, len(months) // 14)
    ticks = list(range(0, len(months), tick_step))
    axes[1].set_xticks([months[i] for i in ticks])
    axes[1].tick_params(axis="x", rotation=45)

    fig.suptitle(
        "Snapshot-1 Train Qrel Freshness Relative to the 2025-03-01 to 2025-05-31 Reindex Window",
        fontsize=14,
    )
    fig.tight_layout()
    fig.savefig(output_dir / "qrel_freshness_distribution.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    output_dir = ROOT / "adaptive_monitor" / "outputs" / "qrel_freshness_analysis"
    rows, summary, top5_rows = analyze()
    write_outputs(rows, summary, top5_rows, output_dir)
    write_plots(summary, output_dir)
    print(f"Outputs written to {output_dir}")
    print(f"Queries with dated relevant docs: {summary['total_queries_with_relevant_docs']}")
    print(
        "Queries whose latest dated relevant doc is before 2025-03-01: "
        f"{summary['queries_with_all_relevant_docs_by_window_start']}"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Benchmark the v4 extraction pipeline on a document corpus.

Runs extract_pdf() on each document and reports quality metrics.

Usage:
    uv run python scripts/benchmark_corpus.py
    uv run python scripts/benchmark_corpus.py --only 2232,2233
    uv run python scripts/benchmark_corpus.py --budget 2.0
"""

import sys
import time
from pathlib import Path

from agentic_mbse.extraction.pipeline import PipelineConfig, extract_pdf

LITERATURE = Path("/home/reid/1cfe/literature")

DOCS = [
    # (id, glob pattern) — order: smallest/simplest first
    ("2241", "Eester et al*"),
    ("2238", "Lampe and Manheimer*"),
    ("2233", "Araiinejad*"),
    ("2232", "Handley*"),
    ("2235", "_.pdf"),
    ("2236", "_.pdf"),
    ("2237", "LA-UR*"),
]


def find_pdf(doc_id: str, pattern: str) -> Path | None:
    doc_dir = LITERATURE / doc_id
    pdfs = [p for p in doc_dir.glob(pattern) if p.suffix == ".pdf"]
    if not pdfs:
        pdfs = [p for p in doc_dir.glob("*.pdf") if "Zone.Identifier" not in p.name]
    return pdfs[0] if pdfs else None


def main():
    # Parse flags
    only_ids = None
    budget = 0.0
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i].startswith("--only="):
            only_ids = set(args[i].split("=", 1)[1].split(","))
        elif args[i] == "--only" and i + 1 < len(args):
            only_ids = set(args[i + 1].split(","))
            i += 1
        elif args[i].startswith("--budget="):
            budget = float(args[i].split("=", 1)[1])
        elif args[i] == "--budget" and i + 1 < len(args):
            budget = float(args[i + 1])
            i += 1
        elif args[i] in ("--help", "-h"):
            print("Usage: benchmark_corpus.py [--only ID,...] [--budget USD]")
            print("  --only ID,...   Run only these document IDs")
            print("  --budget USD    Claude budget per document (default: 0.0 = offline)")
            return
        i += 1

    print("=" * 70)
    print("PDF Extraction v4 — Corpus Benchmark")
    if only_ids:
        print(f"  (running only: {', '.join(sorted(only_ids))})")
    print(f"  Claude budget: ${budget:.2f}/doc")
    print("=" * 70)

    config = PipelineConfig(claude_budget_usd=budget)
    results = []

    for doc_id, pattern in DOCS:
        if only_ids and doc_id not in only_ids:
            continue
        pdf = find_pdf(doc_id, pattern)
        if pdf is None:
            print(f"  SKIP  {doc_id}: no PDF found")
            continue

        print(f"\n  [{doc_id}] {pdf.name}")

        t0 = time.monotonic()
        result = extract_pdf(pdf, config=config)
        elapsed = time.monotonic() - t0

        if result.error:
            print(f"    FAIL: {result.error}")
            results.append((doc_id, pdf.name, "FAIL", 0, 0, 0, elapsed, 0.0))
            continue

        m = result.metrics
        print(f"    chars: {m.char_count:,}")
        print(f"    headings: {m.heading_count}  table_rows: {m.table_row_count}")
        print(f"    source: {result.source}")
        if result.total_cost_usd > 0:
            print(f"    cost: ${result.total_cost_usd:.4f}")
        print(f"    time: {elapsed:.1f}s")

        results.append((
            doc_id,
            pdf.name,
            "OK",
            m.heading_count,
            m.table_row_count,
            m.char_count,
            elapsed,
            result.total_cost_usd,
        ))

    # Summary table
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(
        f"{'ID':<6} {'Status':<6} {'Headings':>8} {'TblRows':>8} "
        f"{'Chars':>10} {'Cost':>8} {'Time':>6}"
    )
    print("-" * 58)
    for doc_id, name, status, headings, tbl_rows, chars, elapsed, cost in results:
        cost_str = f"${cost:.3f}" if cost > 0 else "-"
        print(
            f"{doc_id:<6} {status:<6} {headings:>8} {tbl_rows:>8} "
            f"{chars:>10,} {cost_str:>8} {elapsed:>5.1f}s"
        )
    print("-" * 58)
    total_time = sum(r[6] for r in results)
    total_cost = sum(r[7] for r in results)
    cost_str = f"${total_cost:.3f}" if total_cost > 0 else "-"
    print(f"{'TOTAL':<6} {'':6} {'':>8} {'':>8} {'':>10} {cost_str:>8} {total_time:>5.1f}s")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Benchmark the full extraction pipeline on the 7-doc corpus.

Runs all documents in a SINGLE process so the GMFT model loads once
(~24s) instead of once per document.

Usage:
    uv run python scripts/benchmark_corpus.py
"""

import time
from pathlib import Path

from agentic_mbse.extraction.base import (
    ExtractionResult,
    get_output_dir,
    write_summary,
)
from agentic_mbse.extraction.index import generate_index
from agentic_mbse.extraction.quality_gates import detect_problems

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

PER_DOC_TIMEOUT = 180  # seconds


def find_pdf(doc_id: str, pattern: str) -> Path | None:
    doc_dir = LITERATURE / doc_id
    pdfs = [p for p in doc_dir.glob(pattern) if p.suffix == ".pdf"]
    if not pdfs:
        pdfs = [p for p in doc_dir.glob("*.pdf") if "Zone.Identifier" not in p.name]
    return pdfs[0] if pdfs else None


def extract_one(pdf_path: Path) -> tuple[ExtractionResult, float]:
    """Run full extraction (pymupdf + postprocess) on one PDF."""
    from agentic_mbse.cli.extract_cli import _run_extraction

    output_dir = get_output_dir(pdf_path)
    t0 = time.monotonic()
    result = _run_extraction(pdf_path, output_dir, "pymupdf", timeout=PER_DOC_TIMEOUT)
    elapsed = time.monotonic() - t0
    if result.success:
        write_summary(pdf_path, output_dir, result, "pymupdf")
    return result, elapsed


def run_layer2(md_text: str, pdf_path: Path, problems: list) -> tuple[str, int, float]:
    """Run GMFT table enhancement. Returns (updated_md, tables_fixed, elapsed)."""
    table_problems = [p for p in problems if p.region_type == "table"]
    if not table_problems:
        return md_text, 0, 0.0

    try:
        from agentic_mbse.extraction.table_extraction import enhance_tables
    except ImportError:
        print("    GMFT not installed, skipping Layer 2")
        return md_text, 0, 0.0

    t0 = time.monotonic()
    md_text, remaining = enhance_tables(md_text, pdf_path, table_problems)
    elapsed = time.monotonic() - t0
    fixed = len(table_problems) - len(remaining)
    return md_text, fixed, elapsed


def main():
    import sys

    # Parse --only flag: e.g. --only 2232,2233,2238
    only_ids = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only_ids = set(arg.split("=", 1)[1].split(","))
        elif arg == "--only" and sys.argv.index(arg) + 1 < len(sys.argv):
            only_ids = set(sys.argv[sys.argv.index(arg) + 1].split(","))

    print("=" * 70)
    print("PDF Extraction v2 — Corpus Benchmark")
    if only_ids:
        print(f"  (running only: {', '.join(sorted(only_ids))})")
    print("=" * 70)

    # Pre-warm GMFT model so the first doc isn't penalized
    print("\nPre-loading GMFT model...")
    t_model = time.monotonic()
    try:
        from agentic_mbse.extraction.table_extraction import (
            _get_detector,
            _get_formatter,
        )
        _get_detector()
        _get_formatter()
        print(f"  GMFT model loaded in {time.monotonic() - t_model:.1f}s")
    except ImportError:
        print("  GMFT not installed — Layer 2 will be skipped")

    print()
    results = []

    for doc_id, pattern in DOCS:
        if only_ids and doc_id not in only_ids:
            continue
        pdf = find_pdf(doc_id, pattern)
        if pdf is None:
            print(f"  SKIP  {doc_id}: no PDF found")
            continue

        print(f"  [{doc_id}] {pdf.name}")

        # Step 1: Extract (pymupdf + postprocess)
        result, t_extract = extract_one(pdf)
        if not result.success:
            print(f"    FAIL: {result.error}")
            results.append((doc_id, pdf.name, "FAIL", 0, 0, 0, t_extract))
            continue

        print(f"    extracted: {result.char_count:,} chars, {result.image_count} images ({t_extract:.1f}s)")

        # Step 2: Quality detection
        md_text = result.markdown_path.read_text()
        problems = detect_problems(md_text)
        n_table = sum(1 for p in problems if p.region_type == "table")
        n_eq = sum(1 for p in problems if p.region_type == "equation")
        print(f"    problems: {n_table} tables, {n_eq} equations")

        # Step 3: GMFT table enhancement
        md_text, tables_fixed, t_gmft = run_layer2(md_text, pdf, problems)
        if tables_fixed > 0:
            result.markdown_path.write_text(md_text)
            print(f"    GMFT fixed: {tables_fixed} tables ({t_gmft:.1f}s)")
        elif n_table > 0:
            print(f"    GMFT fixed: 0/{n_table} tables ({t_gmft:.1f}s)")

        # Step 4: Index generation
        idx = generate_index(result.markdown_path, summarize=False, force=True)
        sections = 0
        if idx:
            for line in idx.read_text().splitlines():
                if line.startswith("section_count:"):
                    sections = int(line.split(":")[1].strip())
                    break
        print(f"    index: {sections} sections")

        pipe_lines = sum(1 for line in md_text.splitlines() if line.strip().startswith("|"))
        total_time = t_extract + t_gmft

        results.append((doc_id, pdf.name, "OK", sections, tables_fixed, pipe_lines, total_time))
        print(f"    total: {total_time:.1f}s")
        print()

    # Summary table
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"{'ID':<6} {'Status':<6} {'Sections':>8} {'GMFT Fixed':>10} {'Pipe Lines':>10} {'Time':>6}")
    print("-" * 52)
    for doc_id, name, status, sections, fixed, pipes, elapsed in results:
        print(f"{doc_id:<6} {status:<6} {sections:>8} {fixed:>10} {pipes:>10} {elapsed:>5.1f}s")
    print("-" * 52)
    total_time = sum(r[6] for r in results)
    total_fixed = sum(r[4] for r in results)
    print(f"{'TOTAL':<6} {'':6} {'':>8} {total_fixed:>10} {'':>10} {total_time:>5.1f}s")


if __name__ == "__main__":
    main()

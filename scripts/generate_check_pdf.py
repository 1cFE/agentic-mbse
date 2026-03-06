#!/usr/bin/env python3
"""Generate the built-in check corpus PDFs from real test corpus papers.

Extracts a small set of pages from large corpus PDFs to create compact test
files that exercise all pipeline probes.  Run once, check in results:

    uv run python scripts/generate_check_pdf.py

Output:
    src/agentic_mbse/extraction/check_corpus/test_features.pdf  (tables + headings)
    src/agentic_mbse/extraction/check_corpus/arxiv_probe.pdf    (arXiv ID + math)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pymupdf  # type: ignore[import-untyped]

# Resolve paths relative to repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = REPO_ROOT / "tests" / "corpus" / "pdfs"
OUTPUT_DIR = REPO_ROOT / "src" / "agentic_mbse" / "extraction" / "check_corpus"


def generate_test_features() -> Path:
    """Extract table-rich pages from hsu_2020.pdf for table probes.

    hsu_2020.pdf has real data tables (fusion power parameters, cost
    accounts) that produce substantive pipe-row markdown.  Extracts
    page 0 (headings) plus the best table pages.
    """
    from agentic_mbse.extraction.check import select_pages
    from agentic_mbse.extraction.pymupdf_backend import extract_pages

    source = CORPUS_DIR / "hsu_2020.pdf"
    assert source.exists(), f"Source PDF not found: {source}"

    # Run heuristics to find best pages
    pages = extract_pages(source)
    selected = select_pages(pages)
    print(f"  hsu_2020.pdf: {len(pages)} pages")
    print(f"    headings page: {selected.headings}")
    print(f"    tables page: {selected.tables}")

    # Build page set (deduplicated, sorted)
    keep = {0}  # always include page 0 for headings
    if selected.tables is not None:
        keep.add(selected.tables)
    keep_sorted = sorted(keep)
    print(f"    keeping pages: {keep_sorted}")

    # Extract pages with pymupdf
    doc = pymupdf.open(str(source))
    doc.select(keep_sorted)
    out_path = OUTPUT_DIR / "test_features.pdf"
    doc.save(str(out_path), garbage=4, deflate=True)
    doc.close()

    size_kb = out_path.stat().st_size / 1024
    print(f"    saved: {out_path.name} ({size_kb:.0f} KB, {len(keep_sorted)} pages)")

    # Validate: re-run heuristics on the output PDF
    validation_pages = extract_pages(out_path)
    validation_selected = select_pages(validation_pages)
    assert validation_selected.tables is not None, (
        "VALIDATION FAILED: test_features.pdf has no table pages — "
        "select_pages() found no pipe rows"
    )
    print(f"    validation: tables on page {validation_selected.tables} OK")

    return out_path


def generate_arxiv_probe() -> Path:
    """Extract pages 0+2 from paischer_2025.pdf for arXiv + math probes.

    Page 0 contains the arXiv ID (exercises detect_arxiv_id).
    Page 2 has math content with garble score 4.0 (exercises Claude
    math re-extraction probe).
    """
    from agentic_mbse.extraction.check import select_pages
    from agentic_mbse.extraction.pandoc_convert import detect_arxiv_id
    from agentic_mbse.extraction.pymupdf_backend import extract_pages

    source = CORPUS_DIR / "paischer_2025.pdf"
    assert source.exists(), f"Source PDF not found: {source}"

    doc = pymupdf.open(str(source))
    print(f"  paischer_2025.pdf: {len(doc)} pages")

    # Page 0 = arXiv ID, page 2 = math content (garble score 4.0)
    doc.select([0, 2])
    out_path = OUTPUT_DIR / "arxiv_probe.pdf"
    doc.save(str(out_path), garbage=4, deflate=True)
    doc.close()

    size_kb = out_path.stat().st_size / 1024
    print(f"    saved: {out_path.name} ({size_kb:.0f} KB, 2 pages)")

    # Validate: detect_arxiv_id must find the ID
    arxiv_id = detect_arxiv_id(out_path)
    assert arxiv_id is not None, (
        "VALIDATION FAILED: arxiv_probe.pdf does not contain a detectable arXiv ID"
    )
    print(f"    validation: arXiv ID = {arxiv_id} OK")

    # Validate: math page detected
    validation_pages = extract_pages(out_path)
    validation_selected = select_pages(validation_pages)
    if validation_selected.math is not None:
        print(f"    validation: math on page {validation_selected.math} OK")
    else:
        print("    validation: WARNING — no math-garbled page found in output")

    return out_path


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating check corpus PDFs...")
    print()

    features_path = generate_test_features()
    print()
    arxiv_path = generate_arxiv_probe()

    # Summary
    total_kb = (features_path.stat().st_size + arxiv_path.stat().st_size) / 1024
    print()
    print(f"Total corpus size: {total_kb:.0f} KB")
    assert total_kb < 1024, f"Corpus too large: {total_kb:.0f} KB > 1024 KB limit"
    print("Done. Check in the generated PDFs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

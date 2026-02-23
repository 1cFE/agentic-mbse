#!/usr/bin/env python3
"""H1: pymupdf4llm + GMFT table replacement pipeline.

Composition: Run pymupdf4llm (best_v1 config) on full doc. Run GMFT on full doc.
For pages where pymupdf4llm's tables are missing or broken, replace with GMFT
tables (after false-positive filtering).

Usage:
    python tests/corpus/pipelines/h1_pymupdf_gmft.py
    python tests/corpus/pipelines/h1_pymupdf_gmft.py --slugs hawker_2020,hsu_2020
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics import compute_metrics
from shared import (
    BEST_V1_PARAMS,
    GmftTable,
    PageDecision,
    PageResult,
    count_real_table_rows,
    extract_gmft_pages,
    extract_pymupdf_pages,
    filter_gmft_tables,
    get_pdf_path,
    has_br_in_tables,
    has_col_headers,
    insert_tables_at_end,
    load_papers,
    replace_tables,
    strip_pipe_tables,
    save_config,
    save_pipeline_result,
    score_and_print,
)

# Default: 4-paper dev set
DEV_SET = ["hawker_2020", "hsu_2020", "hansen_2025", "paischer_2025"]
RUN_NAME = "h1"


def decide_page(
    page: PageResult,
    gmft_tables: list[GmftTable] | None,
) -> tuple[str, PageDecision]:
    """Decide what to do with a single page's tables.

    Decision logic (in priority order):
    1. pymupdf has tables AND GMFT has tables → prefer GMFT (more accurate)
    2. pymupdf has false tables (ColN headers) with no GMFT → strip false tables
    3. pymupdf has <br> tables with no GMFT → strip broken tables
    4. pymupdf has no real tables, GMFT has tables → append GMFT
    5. Otherwise → keep as-is

    Returns:
        (final_markdown, decision)
    """
    pymupdf_rows = count_real_table_rows(page.markdown)
    has_br = has_br_in_tables(page.markdown)
    has_col = has_col_headers(page.markdown)

    # Filter GMFT tables for false positives
    filtered_tables: list[GmftTable] = []
    filter_reasons: list[str] = []
    if gmft_tables:
        filtered_tables, filter_reasons = filter_gmft_tables(gmft_tables, page.page_num)

    gmft_rows = sum(t.num_rows for t in filtered_tables) if filtered_tables else 0

    def _details():
        return {
            "pymupdf_real_table_rows": pymupdf_rows,
            "pymupdf_has_br": has_br,
            "pymupdf_has_col_headers": has_col,
            "gmft_tables_raw": len(gmft_tables) if gmft_tables else 0,
            "gmft_tables_filtered": len(filtered_tables),
            "gmft_rows": gmft_rows,
        }

    # --- Decision logic ---

    # Case 1: Both have tables → prefer GMFT (it's more accurate on tables)
    if pymupdf_rows > 0 and filtered_tables:
        decision = PageDecision(
            page_num=page.page_num,
            action="gmft_replace",
            reasons=[
                f"both tools have tables; replacing pymupdf ({pymupdf_rows} rows) "
                f"with GMFT ({gmft_rows} rows in {len(filtered_tables)} tables)",
                *filter_reasons,
            ],
            details=_details(),
        )
        return replace_tables(page.markdown, filtered_tables), decision

    # Case 2: pymupdf has false tables (ColN headers), no GMFT → strip
    if has_col and not filtered_tables:
        decision = PageDecision(
            page_num=page.page_num,
            action="strip_false",
            reasons=[
                f"pymupdf4llm has ColN auto-headers ({pymupdf_rows} rows) — "
                f"likely diagram/figure, stripping",
                *filter_reasons,
            ],
            details=_details(),
        )
        return strip_pipe_tables(page.markdown), decision

    # Case 3: pymupdf has <br> in tables, no GMFT → strip broken tables
    if has_br and not filtered_tables:
        decision = PageDecision(
            page_num=page.page_num,
            action="strip_broken",
            reasons=[
                f"pymupdf4llm tables have <br> artifacts ({pymupdf_rows} rows), "
                f"no GMFT replacement available — stripping",
                *filter_reasons,
            ],
            details=_details(),
        )
        return strip_pipe_tables(page.markdown), decision

    # Case 4: pymupdf has no real tables, GMFT has tables → append GMFT
    if pymupdf_rows == 0 and filtered_tables:
        decision = PageDecision(
            page_num=page.page_num,
            action="gmft_append",
            reasons=[
                f"pymupdf4llm has 0 real table rows, "
                f"GMFT has {gmft_rows} rows in {len(filtered_tables)} tables",
                *filter_reasons,
            ],
            details=_details(),
        )
        return insert_tables_at_end(page.markdown, filtered_tables), decision

    # Case 5: Keep as-is
    reasons = []
    if pymupdf_rows > 0:
        reasons.append(f"pymupdf4llm tables OK ({pymupdf_rows} rows, no issues)")
    elif not gmft_tables:
        reasons.append("no tables detected by either tool")
    elif not filtered_tables:
        reasons.append(
            f"pymupdf4llm has 0 tables; GMFT had {len(gmft_tables)} "
            f"but all filtered as false positives"
        )
        reasons.extend(filter_reasons)
    else:
        reasons.append("no action needed")

    decision = PageDecision(
        page_num=page.page_num,
        action="keep",
        reasons=reasons,
        details=_details(),
    )
    return page.markdown, decision


def run_h1(slug: str) -> None:
    """Run H1 pipeline on a single paper."""
    pdf_path = get_pdf_path(slug)
    if pdf_path is None:
        print(f"  SKIP {slug}: PDF not found")
        return

    print(f"\n{'='*60}")
    print(f"  {slug} ({pdf_path.name})")
    print(f"{'='*60}")

    # Step 1: Extract with pymupdf4llm (per page)
    start = time.time()
    print(f"  pymupdf4llm extracting...", end=" ", flush=True)
    pages = extract_pymupdf_pages(pdf_path)
    pymupdf_elapsed = time.time() - start
    print(f"{pymupdf_elapsed:.1f}s ({len(pages)} pages)")

    # Step 2: Extract tables with GMFT
    print(f"  GMFT extracting...", end=" ", flush=True)
    gmft_start = time.time()
    gmft_pages = extract_gmft_pages(pdf_path)
    gmft_elapsed = time.time() - gmft_start
    gmft_total_tables = sum(len(t) for t in gmft_pages.values())
    print(f"{gmft_elapsed:.1f}s ({gmft_total_tables} tables on {len(gmft_pages)} pages)")

    # Step 3: Per-page decision and merge
    print(f"  Merging...")
    final_pages = []
    decisions = []

    for page in pages:
        gmft_tables = gmft_pages.get(page.page_num)
        md, decision = decide_page(page, gmft_tables)
        final_pages.append(md)
        decisions.append(decision)

        # Log non-trivial decisions
        if decision.action != "keep" or any("REJECT" in r for r in decision.reasons):
            print(f"    page {page.page_num}: {decision.action} — {decision.reasons[0]}")

    # Step 4: Assemble final document
    full_markdown = "\n".join(final_pages)
    total_elapsed = time.time() - start

    # Step 5: Score against ground truth
    metrics = compute_metrics(full_markdown, total_elapsed)
    print(f"\n  Metrics: {metrics.heading_count} headings, "
          f"{metrics.table_row_count} table rows, "
          f"{metrics.char_count} chars, "
          f"{total_elapsed:.1f}s")

    scores = score_and_print(slug, metrics)

    # Step 6: Save results
    save_pipeline_result(
        run_name=RUN_NAME,
        slug=slug,
        markdown=full_markdown,
        elapsed=total_elapsed,
        decisions=decisions,
        extra_data={
            "pymupdf_elapsed": pymupdf_elapsed,
            "gmft_elapsed": gmft_elapsed,
            "total_elapsed": total_elapsed,
            "gmft_total_tables_raw": gmft_total_tables,
            "pages_with_gmft_action": sum(
                1 for d in decisions if d.action != "keep"
            ),
        },
    )


def main():
    parser = argparse.ArgumentParser(description="H1: pymupdf4llm + GMFT table replacement")
    parser.add_argument(
        "--slugs",
        type=str,
        default=",".join(DEV_SET),
        help="Comma-separated paper slugs (default: 4-paper dev set)",
    )
    args = parser.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",")]

    print(f"H1 Pipeline: pymupdf4llm + GMFT table replacement")
    print(f"Papers: {', '.join(slugs)}")

    # Save config
    save_config(RUN_NAME, {
        "pipeline": "h1_pymupdf_gmft",
        "description": "pymupdf4llm best_v1 + GMFT table replacement with false-positive filter",
        "pymupdf_config": "best_v1 (CompositeHeaderDetector, lines, ignore_code)",
        "gmft_config": "default",
        "filter": "confidence >= 0.98, avg_cell_length <= 80, no single-row-many-col",
        "slugs": slugs,
    })

    for slug in slugs:
        run_h1(slug)

    print(f"\n{'='*60}")
    print(f"  Done. Results in runs/pipeline_h1/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

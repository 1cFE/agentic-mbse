#!/usr/bin/env python3
"""H5: Quality-gated multi-layer pipeline.

Composes H1 (GMFT table replacement) and H3 (Claude equation repair) into a
single quality-gated pipeline that routes each page to the appropriate
enhancement based on quality assessment.

Routing logic (prefer free over paid per FR-13):
  1. Table anomaly ONLY (no math) → GMFT replacement (free, from H1)
  2. Math garbling (± table anomaly) → Claude vision replacement (fixes both)
  3. Low text density → Claude vision replacement
  4. No issues → keep pymupdf4llm output

When a page needs BOTH table fix and math fix, Claude handles it via full-page
replacement (Claude finds tables accurately — see Stage 1D findings).

Usage:
    python tests/corpus/pipelines/h5_quality_gated.py
    python tests/corpus/pipelines/h5_quality_gated.py --slugs hawker_2020,paischer_2025
    python tests/corpus/pipelines/h5_quality_gated.py --dry-run
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics import compute_metrics
from quality_gate import (
    PageAssessment,
    assess_heading_anomaly,
    assess_page_quality,
    prioritize_pages,
)
from h1_pymupdf_gmft import decide_page as h1_decide_page
from h3_pymupdf_claude_eq import (
    BUDGET_PER_DOC_USD,
    COST_PER_PAGE_USD,
    MAX_CLAUDE_PAGES,
    DEFAULT_PROMPT,
    extract_page_with_claude,
)
from shared import (
    CORPUS_DIR,
    PageDecision,
    extract_gmft_pages,
    extract_pymupdf_pages,
    filter_gmft_tables,
    get_pdf_path,
    load_papers,
    replace_tables,
    save_config,
    save_pipeline_result,
    score_and_print,
)

import json

# Default: 4-paper dev set
DEV_SET = ["hawker_2020", "hsu_2020", "hansen_2025", "paischer_2025"]
RUN_NAME = "h5"


def run_h5(
    slug: str,
    prompt_text: str,
    model: str = "sonnet",
    dry_run: bool = False,
) -> None:
    """Run H5 quality-gated pipeline on a single paper."""
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

    # Step 3: Run quality gate on each page
    print(f"  Quality gate assessing...")
    assessments: list[PageAssessment] = []
    for page in pages:
        assessment = assess_page_quality(page.markdown, page.page_num)
        assessments.append(assessment)

    # Step 3b: Document-level heading anomaly check
    total_headings = sum(
        1 for page in pages
        for line in page.markdown.split("\n")
        if line.startswith("#") and len(line) > 1 and line.lstrip("#")[0:1] in (" ", "\t")
    )
    heading_anomaly, heading_reasons = assess_heading_anomaly(total_headings, len(pages))
    if heading_anomaly:
        print(f"  HEADING ANOMALY (doc-level): {heading_reasons[0]}")
        # Heading anomaly boosts severity of all Claude-flagged pages
        # (Claude replacement improves headings as a side effect)
        for a in assessments:
            if a.needs_claude:
                a.severity += 0.5
                a.reasons.append(f"HEADING: {heading_reasons[0]} (boost)")

    # Step 4: Route decisions
    #   - Table-only issues → GMFT (free)
    #   - Math/density issues → Claude (paid, budget-constrained)
    #   - Both table + math → Claude (handles both via full-page replacement)

    # Determine Claude pages (budget enforcement)
    claude_pages_list = prioritize_pages(assessments, MAX_CLAUDE_PAGES)
    claude_pages_set = set(claude_pages_list)
    flagged_claude = sum(1 for a in assessments if a.needs_claude)
    flagged_gmft = sum(1 for a in assessments if a.needs_gmft and not a.needs_claude)

    print(f"\n  Routing summary:")
    print(f"    GMFT-only pages: {flagged_gmft}")
    print(f"    Claude pages: {len(claude_pages_list)} (of {flagged_claude} flagged)")
    if claude_pages_list:
        est_cost = len(claude_pages_list) * COST_PER_PAGE_USD
        print(f"    Estimated Claude cost: ${est_cost:.2f}")

    # Log per-page routing
    for a in assessments:
        if a.needs_claude or a.needs_gmft:
            route = []
            if a.page_num in claude_pages_set:
                route.append("CLAUDE")
            elif a.needs_claude:
                route.append("CLAUDE(skipped-budget)")
            if a.needs_gmft and a.page_num not in claude_pages_set:
                route.append("GMFT")
            elif a.needs_gmft:
                route.append("(gmft-superseded-by-claude)")
            print(
                f"    page {a.page_num}: {'+'.join(route)} "
                f"(severity={a.severity:.1f}) — {a.reasons[0]}"
            )

    if dry_run:
        print(f"\n  [DRY RUN] Skipping extraction")
        return

    # Step 5: Execute Claude re-extraction for flagged pages
    page_costs: list[dict] = []
    claude_results: dict[int, str] = {}

    if claude_pages_list:
        print(f"\n  Claude vision re-extracting {len(claude_pages_list)} pages...")
        for page_num in claude_pages_list:
            print(f"    page {page_num}... ", end="", flush=True)
            try:
                md, cost = extract_page_with_claude(
                    slug, page_num, prompt_text, model=model
                )
                claude_results[page_num] = md
                page_costs.append(cost)
                print(
                    f"{cost['wall_clock_seconds']:.1f}s | "
                    f"${cost['total_cost_usd']:.3f}"
                )
            except Exception as e:
                print(f"ERROR: {e}")
                page_costs.append({
                    "page_num": page_num,
                    "total_cost_usd": 0,
                    "error": str(e),
                })

    # Step 6: Merge all enhancements
    print(f"\n  Merging...")
    final_pages = []
    decisions = []

    for page in pages:
        assessment = assessments[page.page_num]
        gmft_tables = gmft_pages.get(page.page_num)

        # Route 1: Claude replacement (handles math + tables + headings)
        if page.page_num in claude_results:
            final_pages.append(claude_results[page.page_num])
            decision = PageDecision(
                page_num=page.page_num,
                action="claude_replace",
                reasons=[
                    "Claude vision re-extraction (full page replacement)",
                    *[f"  {r}" for r in assessment.reasons],
                ],
                details={
                    "route": "claude",
                    "math_garble_score": assessment.math_garble_score,
                    "severity": assessment.severity,
                    "also_had_table_anomaly": assessment.table_anomaly,
                },
            )
            print(f"    page {page.page_num}: claude_replace")

        # Route 2: GMFT table replacement (table anomaly only, no Claude needed)
        elif assessment.needs_gmft and not assessment.needs_claude:
            md, h1_decision = h1_decide_page(page, gmft_tables)
            final_pages.append(md)
            decision = PageDecision(
                page_num=page.page_num,
                action=f"gmft_{h1_decision.action}",
                reasons=[
                    f"GMFT table fix (quality gate: {assessment.reasons[0]})",
                    *h1_decision.reasons,
                ],
                details={
                    "route": "gmft",
                    "h1_action": h1_decision.action,
                    **h1_decision.details,
                },
            )
            if h1_decision.action != "keep":
                print(f"    page {page.page_num}: gmft_{h1_decision.action}")

        # Route 3: GMFT table replacement (Claude flagged but budget-skipped)
        elif assessment.needs_gmft and assessment.needs_claude:
            # Claude was needed but budget didn't allow — still do GMFT for tables
            md, h1_decision = h1_decide_page(page, gmft_tables)
            final_pages.append(md)
            decision = PageDecision(
                page_num=page.page_num,
                action=f"gmft_{h1_decision.action}",
                reasons=[
                    f"Claude flagged but budget-skipped; GMFT table fix applied",
                    *[f"  {r}" for r in assessment.reasons],
                    *h1_decision.reasons,
                ],
                details={
                    "route": "gmft_fallback",
                    "claude_skipped": True,
                    "h1_action": h1_decision.action,
                    **h1_decision.details,
                },
            )
            if h1_decision.action != "keep":
                print(f"    page {page.page_num}: gmft_{h1_decision.action} (claude budget-skipped)")

        # Route 4: Keep as-is (no issues, or unflagged)
        else:
            # Still run H1 logic for pages with GMFT tables that quality gate
            # didn't flag (H1 has its own detection for table issues)
            md, h1_decision = h1_decide_page(page, gmft_tables)
            final_pages.append(md)
            decision = PageDecision(
                page_num=page.page_num,
                action=h1_decision.action if h1_decision.action != "keep" else "keep",
                reasons=h1_decision.reasons if h1_decision.action != "keep" else ["no issues detected"],
                details={
                    "route": "h1_passthrough" if h1_decision.action != "keep" else "keep",
                    **h1_decision.details,
                },
            )
            if h1_decision.action != "keep":
                print(f"    page {page.page_num}: h1_{h1_decision.action}")

        decisions.append(decision)

    # Step 7: Assemble final document
    full_markdown = "\n".join(final_pages)
    total_elapsed = time.time() - start

    # Step 8: Cost summary
    total_claude_cost = sum(c.get("total_cost_usd", 0) for c in page_costs)
    total_claude_time = sum(c.get("wall_clock_seconds", 0) for c in page_costs)

    print(f"\n  Claude cost: ${total_claude_cost:.3f} "
          f"({len(claude_results)} pages, {total_claude_time:.1f}s)")

    # Step 9: Score against ground truth
    metrics = compute_metrics(full_markdown, total_elapsed)
    print(f"  Metrics: {metrics.heading_count} headings, "
          f"{metrics.table_row_count} table rows, "
          f"{metrics.char_count} chars, "
          f"{total_elapsed:.1f}s")

    scores = score_and_print(slug, metrics)

    # Step 10: Save results
    cost_summary = {
        "total_claude_cost_usd": total_claude_cost,
        "total_claude_time_seconds": total_claude_time,
        "claude_pages_extracted": len(claude_results),
        "claude_pages_flagged": flagged_claude,
        "gmft_only_pages": flagged_gmft,
        "per_page_costs": page_costs,
        "model": model,
    }

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
            **cost_summary,
        },
    )

    # Save dedicated cost.json
    cost_path = CORPUS_DIR / "runs" / f"pipeline_{RUN_NAME}" / slug / "cost.json"
    cost_path.write_text(json.dumps(cost_summary, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="H5: Quality-gated multi-layer pipeline (GMFT tables + Claude equations)"
    )
    parser.add_argument(
        "--slugs",
        type=str,
        default=",".join(DEV_SET),
        help="Comma-separated paper slugs (default: 4-paper dev set)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="sonnet",
        help="Claude model to use (default: sonnet)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show routing decisions without calling Claude",
    )
    args = parser.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",")]

    print(f"H5 Pipeline: Quality-gated multi-layer (GMFT + Claude)")
    print(f"Papers: {', '.join(slugs)}")
    print(f"Budget: ${BUDGET_PER_DOC_USD:.2f}/doc ({MAX_CLAUDE_PAGES} pages max)")
    if args.dry_run:
        print(f"MODE: DRY RUN (no Claude calls)")

    # Load extraction prompt
    prompt_text = DEFAULT_PROMPT.read_text().strip()

    # Save config
    save_config(RUN_NAME, {
        "pipeline": "h5_quality_gated",
        "description": "Quality-gated: pymupdf4llm + GMFT tables + Claude vision equations",
        "composition": "H1 (GMFT tables) + H3 (Claude equations) composed via quality gate",
        "routing": {
            "table_anomaly_only": "GMFT replacement (free)",
            "math_garbling": "Claude vision (full page replacement)",
            "both_table_and_math": "Claude vision (handles both)",
            "low_text_density": "Claude vision",
            "no_issues": "keep pymupdf4llm or apply H1 table logic",
        },
        "budget_per_doc_usd": BUDGET_PER_DOC_USD,
        "max_claude_pages": MAX_CLAUDE_PAGES,
        "slugs": slugs,
        "dry_run": args.dry_run,
    })

    for slug in slugs:
        run_h5(slug, prompt_text, model=args.model, dry_run=args.dry_run)

    print(f"\n{'='*60}")
    print(f"  Done. Results in runs/pipeline_h5/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""H3: pymupdf4llm + Claude vision re-extraction for math-garbled pages.

Composition: Run pymupdf4llm (best_v1 config) on full doc. Run quality gate
on each page. For pages flagged with math garbling, re-extract with Claude
pure vision (1 page per call, extract_baseline.txt prompt). Replace pymupdf4llm
output with Claude output for flagged pages.

Per Stage 1D findings:
- Pure vision only (no supplemental text — it doesn't help and costs 22% more)
- Full page replacement (Claude rewrites entire pages regardless of prompt)
- General extract_baseline.txt prompt (focused prompts don't improve quality)

Usage:
    python tests/corpus/pipelines/h3_pymupdf_claude_eq.py
    python tests/corpus/pipelines/h3_pymupdf_claude_eq.py --slugs hawker_2020,paischer_2025
    python tests/corpus/pipelines/h3_pymupdf_claude_eq.py --dry-run  # Show what would be flagged
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics import compute_metrics
from quality_gate import PageAssessment, assess_page_quality, prioritize_pages
from shared import (
    CORPUS_DIR,
    PageDecision,
    extract_pymupdf_pages,
    get_pdf_path,
    load_papers,
    save_config,
    save_pipeline_result,
    score_and_print,
)

# Default: 4-paper dev set
DEV_SET = ["hawker_2020", "hsu_2020", "hansen_2025", "paischer_2025"]
RUN_NAME = "h3"

# Budget: ~$2/doc at ~$0.078/page = ~25 pages max
BUDGET_PER_DOC_USD = 2.00
COST_PER_PAGE_USD = 0.078
MAX_CLAUDE_PAGES = int(BUDGET_PER_DOC_USD / COST_PER_PAGE_USD)  # 25

# Paths
PAGE_IMAGES_DIR = CORPUS_DIR / "page_images"
PROMPTS_DIR = CORPUS_DIR / "prompts"
DEFAULT_PROMPT = PROMPTS_DIR / "extract_baseline.txt"


# ---------------------------------------------------------------------------
# Claude integration (reuses pattern from claude_extract_experiment.py)
# ---------------------------------------------------------------------------


def get_page_image(slug: str, page_num: int) -> Path | None:
    """Get the pre-rendered page image for a specific page.

    Args:
        slug: Paper slug.
        page_num: 0-indexed page number.

    Returns:
        Path to page image, or None if not found.
    """
    img_dir = PAGE_IMAGES_DIR / slug
    # Images are named page_001.png (1-indexed)
    img_path = img_dir / f"page_{page_num + 1:03d}.png"
    return img_path if img_path.exists() else None


def invoke_claude(
    prompt: str,
    model: str = "sonnet",
    timeout: int = 300,
) -> dict:
    """Invoke claude -p with a prompt piped via stdin.

    Returns parsed JSON response.
    Raises RuntimeError on failure or timeout.
    """
    # Must unset CLAUDECODE to avoid nested session guard
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    cmd = [
        "claude", "-p",
        "--model", model,
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--no-session-persistence",
        "--allowedTools", "Read",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude -p timed out after {timeout}s")

    if result.returncode != 0:
        stderr = result.stderr[:500] if result.stderr else "(no stderr)"
        raise RuntimeError(f"claude -p failed (rc={result.returncode}): {stderr}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"claude -p returned non-JSON output: {result.stdout[:300]}"
        )

    return data


def extract_page_with_claude(
    slug: str,
    page_num: int,
    prompt_text: str,
    model: str = "sonnet",
    timeout: int = 300,
) -> tuple[str, dict]:
    """Re-extract a single page using Claude pure vision.

    Args:
        slug: Paper slug.
        page_num: 0-indexed page number.
        prompt_text: Extraction prompt (extract_baseline.txt content).
        model: Claude model to use.
        timeout: Timeout per call in seconds.

    Returns:
        (markdown, cost_data) — extracted markdown and cost info.

    Raises:
        RuntimeError: If image not found or Claude fails.
    """
    img_path = get_page_image(slug, page_num)
    if img_path is None:
        raise RuntimeError(
            f"No page image for {slug} page {page_num}. "
            f"Run tests/corpus/scripts/render_pages.sh first."
        )

    # Build prompt: reference image by absolute path for Claude's Read tool
    prompt = (
        f"Read the image file at {img_path.resolve()} and extract its content.\n\n"
        f"{prompt_text}"
    )

    start = time.time()
    response = invoke_claude(prompt, model=model, timeout=timeout)
    elapsed = time.time() - start

    markdown = response.get("result", "")
    if not markdown:
        raise RuntimeError(f"claude -p returned empty result for {slug} page {page_num}")

    cost_data = {
        "page_num": page_num,
        "total_cost_usd": response.get("total_cost_usd", 0),
        "input_tokens": response.get("usage", {}).get("input_tokens", 0),
        "output_tokens": response.get("usage", {}).get("output_tokens", 0),
        "wall_clock_seconds": elapsed,
        "model": response.get("model", model),
    }

    return markdown, cost_data


# ---------------------------------------------------------------------------
# H3 pipeline
# ---------------------------------------------------------------------------


def run_h3(
    slug: str,
    prompt_text: str,
    model: str = "sonnet",
    dry_run: bool = False,
) -> None:
    """Run H3 pipeline on a single paper."""
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

    # Step 2: Run quality gate on each page
    print(f"  Quality gate assessing...")
    assessments: list[PageAssessment] = []
    for page in pages:
        assessment = assess_page_quality(page.markdown, page.page_num)
        assessments.append(assessment)
        if assessment.needs_claude or assessment.needs_gmft:
            flags = []
            if assessment.needs_claude:
                flags.append("CLAUDE")
            if assessment.needs_gmft:
                flags.append("GMFT")
            print(
                f"    page {page.page_num}: {' + '.join(flags)} "
                f"(severity={assessment.severity:.1f}) — "
                f"{assessment.reasons[0] if assessment.reasons else 'no reason'}"
            )

    # Step 3: Determine which pages to send to Claude (budget enforcement)
    claude_pages = prioritize_pages(assessments, MAX_CLAUDE_PAGES)
    flagged_count = sum(1 for a in assessments if a.needs_claude)

    print(f"\n  Quality gate summary: {flagged_count} pages flagged for Claude")
    if flagged_count > MAX_CLAUDE_PAGES:
        print(
            f"  Budget cap: {MAX_CLAUDE_PAGES} pages max "
            f"(${BUDGET_PER_DOC_USD:.2f} at ${COST_PER_PAGE_USD:.3f}/page)"
        )
        print(f"  Selected top {len(claude_pages)} by severity: {claude_pages}")
    elif claude_pages:
        print(f"  Pages to re-extract: {claude_pages}")
        est_cost = len(claude_pages) * COST_PER_PAGE_USD
        print(f"  Estimated cost: ${est_cost:.2f}")
    else:
        print(f"  No pages need Claude re-extraction")

    if dry_run:
        print(f"\n  [DRY RUN] Skipping Claude extraction")
        return

    # Step 4: Re-extract flagged pages with Claude vision
    page_costs: list[dict] = []
    claude_results: dict[int, str] = {}  # page_num -> markdown

    if claude_pages:
        print(f"\n  Claude vision re-extracting {len(claude_pages)} pages...")
        for page_num in claude_pages:
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

    # Step 5: Merge — replace pymupdf4llm pages with Claude output where available
    print(f"\n  Merging...")
    final_pages = []
    decisions = []

    for page in pages:
        assessment = assessments[page.page_num]

        if page.page_num in claude_results:
            # Use Claude output for this page
            final_pages.append(claude_results[page.page_num])
            decision = PageDecision(
                page_num=page.page_num,
                action="claude_replace",
                reasons=[
                    f"Claude vision re-extraction (full page replacement)",
                    *[f"  {r}" for r in assessment.reasons],
                ],
                details={
                    "math_garble_score": assessment.math_garble_score,
                    "severity": assessment.severity,
                    "needs_claude": assessment.needs_claude,
                },
            )
            print(f"    page {page.page_num}: claude_replace — {assessment.reasons[0]}")
        else:
            # Keep pymupdf4llm output
            final_pages.append(page.markdown)
            reasons = []
            if assessment.needs_claude and page.page_num not in claude_pages:
                reasons.append(
                    f"flagged but not selected (budget limit, severity={assessment.severity:.1f})"
                )
            elif not assessment.needs_claude:
                if assessment.reasons:
                    reasons.extend(assessment.reasons)
                else:
                    reasons.append("no issues detected")
            decision = PageDecision(
                page_num=page.page_num,
                action="keep",
                reasons=reasons if reasons else ["no issues detected"],
                details={
                    "math_garble_score": assessment.math_garble_score,
                    "severity": assessment.severity,
                },
            )

        decisions.append(decision)

    # Step 6: Assemble final document
    full_markdown = "\n".join(final_pages)
    total_elapsed = time.time() - start

    # Step 7: Cost summary
    total_claude_cost = sum(c.get("total_cost_usd", 0) for c in page_costs)
    total_claude_time = sum(c.get("wall_clock_seconds", 0) for c in page_costs)

    print(f"\n  Claude cost: ${total_claude_cost:.3f} "
          f"({len(claude_results)} pages, {total_claude_time:.1f}s)")

    # Step 8: Score against ground truth
    metrics = compute_metrics(full_markdown, total_elapsed)
    print(f"  Metrics: {metrics.heading_count} headings, "
          f"{metrics.table_row_count} table rows, "
          f"{metrics.char_count} chars, "
          f"{total_elapsed:.1f}s")

    scores = score_and_print(slug, metrics)

    # Step 9: Save results
    cost_summary = {
        "total_claude_cost_usd": total_claude_cost,
        "total_claude_time_seconds": total_claude_time,
        "claude_pages_extracted": len(claude_results),
        "claude_pages_flagged": flagged_count,
        "claude_pages_budget_cap": MAX_CLAUDE_PAGES,
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
            "total_elapsed": total_elapsed,
            **cost_summary,
        },
    )

    # Save dedicated cost.json (matches claude_extract_experiment.py format)
    cost_path = CORPUS_DIR / "runs" / f"pipeline_{RUN_NAME}" / slug / "cost.json"
    cost_path.write_text(json.dumps(cost_summary, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="H3: pymupdf4llm + Claude vision for math-garbled pages"
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
        help="Show quality gate results without calling Claude",
    )
    args = parser.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",")]

    print(f"H3 Pipeline: pymupdf4llm + Claude vision (math-garbled pages)")
    print(f"Papers: {', '.join(slugs)}")
    print(f"Budget: ${BUDGET_PER_DOC_USD:.2f}/doc ({MAX_CLAUDE_PAGES} pages max)")
    if args.dry_run:
        print(f"MODE: DRY RUN (no Claude calls)")

    # Load extraction prompt
    prompt_text = DEFAULT_PROMPT.read_text().strip()

    # Save config
    save_config(RUN_NAME, {
        "pipeline": "h3_pymupdf_claude_eq",
        "description": "pymupdf4llm best_v1 + Claude vision re-extraction for math-garbled pages",
        "pymupdf_config": "best_v1 (CompositeHeaderDetector, lines, ignore_code)",
        "claude_config": {
            "model": args.model,
            "prompt": "extract_baseline.txt",
            "mode": "pure vision (no supplemental text)",
            "pages_per_call": 1,
        },
        "quality_gate": {
            "math_garble_threshold": 1.0,
            "budget_per_doc_usd": BUDGET_PER_DOC_USD,
            "max_claude_pages": MAX_CLAUDE_PAGES,
        },
        "slugs": slugs,
        "dry_run": args.dry_run,
    })

    for slug in slugs:
        run_h3(slug, prompt_text, model=args.model, dry_run=args.dry_run)

    print(f"\n{'='*60}")
    print(f"  Done. Results in runs/pipeline_h3/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

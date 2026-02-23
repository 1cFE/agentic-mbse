#!/usr/bin/env python3
"""H6: Pandoc shortcut for arXiv papers.

For papers with arXiv HTML available, convert via Pandoc with Stage 1B best
config (strip <figure> tags, pandoc -f html-native_divs-native_spans -t
markdown-header_attributes --wrap=none). Falls back to H5 PDF pipeline if
no arXiv HTML.

Usage:
    python tests/corpus/pipelines/h6_pandoc_shortcut.py --slugs paischer_2025
    python tests/corpus/pipelines/h6_pandoc_shortcut.py  # runs all dev-set papers
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics import compute_metrics
from shared import (
    CORPUS_DIR,
    PAPERS_JSONL,
    PageDecision,
    load_papers,
    save_config,
    save_pipeline_result,
    score_and_print,
)

# Default: 4-paper dev set
DEV_SET = ["hawker_2020", "hsu_2020", "hansen_2025", "paischer_2025"]
RUN_NAME = "h6"

REPO_ROOT = CORPUS_DIR.parent.parent


# ---------------------------------------------------------------------------
# arXiv detection and HTML retrieval
# ---------------------------------------------------------------------------


def get_arxiv_info(slug: str) -> tuple[str | None, Path | None]:
    """Get arXiv ID and HTML path from papers.jsonl.

    Returns:
        (arxiv_id, html_path) — both None if not an arXiv paper.
    """
    papers = load_papers([slug])
    if not papers:
        return None, None

    paper = papers[0]
    arxiv_id = paper.get("arxiv_id")
    html_rel = paper.get("html_path")

    if arxiv_id is None or html_rel is None:
        return arxiv_id, None

    html_path = REPO_ROOT / html_rel
    if html_path.exists():
        return arxiv_id, html_path

    return arxiv_id, None


# ---------------------------------------------------------------------------
# Pandoc conversion (Stage 1B best config)
# ---------------------------------------------------------------------------


def preprocess_html(html: str) -> str:
    """Pre-process arXiv HTML before Pandoc conversion.

    Strips <figure> tags (so tables inside convert properly) and CSS
    transform wrappers (LaTeXML scaling artifacts).
    """
    # Strip <figure> tags but keep inner content
    html = re.sub(r"<figure[^>]*>", "", html)
    html = html.replace("</figure>", "")

    # Strip CSS transform wrappers (LaTeXML artifacts)
    html = re.sub(r'<div class="ltx_inline-block[^"]*ltx_transformed_outer[^>]*>', "", html)
    html = re.sub(r'<span class="ltx_transformed_inner[^>]*>', "", html)

    return html


def postprocess_markdown(md: str) -> str:
    """Post-process Pandoc markdown output.

    Cleans up LaTeXML artifacts that Pandoc doesn't handle.
    """
    # Strip \hspace{0pt} noise from LaTeXML
    md = md.replace("\\hspace{0pt}", "")

    # Strip HTML comment artifacts
    md = re.sub(r"`<!-- -->`\{=html\}", "", md)

    return md


def run_pandoc(html_path: Path) -> tuple[str, float]:
    """Run Pandoc with Stage 1B best configuration.

    Args:
        html_path: Path to (possibly pre-processed) HTML file.

    Returns:
        (markdown_output, elapsed_seconds)

    Raises:
        RuntimeError: If Pandoc fails.
    """
    cmd = [
        "pandoc",
        str(html_path),
        "-f", "html-native_divs-native_spans",
        "-t", "markdown-header_attributes",
        "--wrap=none",
        "--markdown-headings=atx",
    ]

    start = time.time()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        raise RuntimeError(
            f"Pandoc failed (rc={result.returncode}): {result.stderr[:500]}"
        )

    return result.stdout, elapsed


# ---------------------------------------------------------------------------
# H6 pipeline
# ---------------------------------------------------------------------------


def run_h6(slug: str) -> None:
    """Run H6 pipeline on a single paper."""
    print(f"\n{'='*60}")
    print(f"  {slug}")
    print(f"{'='*60}")

    start = time.time()

    # Step 1: Check for arXiv HTML
    arxiv_id, html_path = get_arxiv_info(slug)

    if arxiv_id is None:
        print(f"  No arXiv ID — skipping (would fall back to H5 PDF pipeline)")
        decision = PageDecision(
            page_num=-1,
            action="fallback_h5",
            reasons=["No arXiv ID in papers.jsonl"],
        )
        save_pipeline_result(
            run_name=RUN_NAME,
            slug=slug,
            markdown="",
            elapsed=0,
            decisions=[decision],
            extra_data={"path": "fallback_h5", "reason": "no arxiv_id"},
        )
        return

    if html_path is None:
        print(f"  arXiv ID {arxiv_id} found but HTML not downloaded — skipping")
        decision = PageDecision(
            page_num=-1,
            action="fallback_h5",
            reasons=[f"arXiv ID {arxiv_id} but HTML not at expected path"],
        )
        save_pipeline_result(
            run_name=RUN_NAME,
            slug=slug,
            markdown="",
            elapsed=0,
            decisions=[decision],
            extra_data={"path": "fallback_h5", "reason": "html_not_found", "arxiv_id": arxiv_id},
        )
        return

    print(f"  arXiv ID: {arxiv_id}")
    print(f"  HTML: {html_path}")

    # Step 2: Pre-process HTML
    print(f"  Pre-processing HTML...", end=" ", flush=True)
    raw_html = html_path.read_text(encoding="utf-8")
    processed_html = preprocess_html(raw_html)
    print(f"done ({len(raw_html):,} → {len(processed_html):,} chars)")

    # Step 3: Run Pandoc
    print(f"  Running Pandoc...", end=" ", flush=True)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(processed_html)
        tmp_path = Path(f.name)

    try:
        markdown, pandoc_elapsed = run_pandoc(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"{pandoc_elapsed:.2f}s")

    # Step 4: Post-process markdown
    markdown = postprocess_markdown(markdown)

    total_elapsed = time.time() - start

    # Step 5: Score against ground truth
    metrics = compute_metrics(markdown, total_elapsed)
    print(f"  Metrics: {metrics.heading_count} headings, "
          f"{metrics.table_row_count} table rows, "
          f"{metrics.char_count} chars")

    scores = score_and_print(slug, metrics)

    # Step 6: Save results
    decision = PageDecision(
        page_num=-1,
        action="pandoc_convert",
        reasons=[
            f"arXiv HTML via Pandoc (ID: {arxiv_id})",
            f"Pre-processed: stripped <figure> tags and CSS transform wrappers",
            f"Post-processed: stripped \\hspace{{0pt}} and HTML comment artifacts",
        ],
        details={
            "arxiv_id": arxiv_id,
            "html_path": str(html_path),
            "html_size": len(raw_html),
            "processed_size": len(processed_html),
            "pandoc_elapsed": pandoc_elapsed,
        },
    )

    save_pipeline_result(
        run_name=RUN_NAME,
        slug=slug,
        markdown=markdown,
        elapsed=total_elapsed,
        decisions=[decision],
        extra_data={
            "path": "pandoc",
            "arxiv_id": arxiv_id,
            "pandoc_elapsed": pandoc_elapsed,
            "total_elapsed": total_elapsed,
            "cost": 0.0,
        },
    )


def main():
    parser = argparse.ArgumentParser(
        description="H6: Pandoc shortcut for arXiv papers"
    )
    parser.add_argument(
        "--slugs",
        type=str,
        default=",".join(DEV_SET),
        help="Comma-separated paper slugs (default: 4-paper dev set)",
    )
    args = parser.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",")]

    print(f"H6 Pipeline: Pandoc shortcut for arXiv papers")
    print(f"Papers: {', '.join(slugs)}")

    # Save config
    save_config(RUN_NAME, {
        "pipeline": "h6_pandoc_shortcut",
        "description": "Pandoc arXiv HTML conversion with Stage 1B best config",
        "pandoc_config": {
            "from": "html-native_divs-native_spans",
            "to": "markdown-header_attributes",
            "wrap": "none",
            "headings": "atx",
        },
        "preprocessing": "strip <figure> tags, CSS transform wrappers",
        "postprocessing": "strip \\hspace{0pt}, HTML comment artifacts",
        "slugs": slugs,
    })

    for slug in slugs:
        run_h6(slug)

    print(f"\n{'='*60}")
    print(f"  Done. Results in runs/pipeline_h6/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

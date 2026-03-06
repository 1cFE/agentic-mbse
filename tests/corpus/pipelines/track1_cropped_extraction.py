#!/usr/bin/env python3
"""Track 1: Claude cropped-image table extraction.

Sends cropped table images (from Track 0) to Claude with a table-specific
extraction prompt. Measures accuracy vs ground truth, cost per table,
and compares against GMFT DataFrame extraction.

Usage:
    python tests/corpus/pipelines/track1_cropped_extraction.py --dry-run
    python tests/corpus/pipelines/track1_cropped_extraction.py --slugs hawker_2020
    python tests/corpus/pipelines/track1_cropped_extraction.py --slugs hawker_2020,hsu_2020
    python tests/corpus/pipelines/track1_cropped_extraction.py --detector both
"""

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared import CORPUS_DIR, RUNS_DIR, count_real_table_rows, load_papers
from metrics import load_ground_truth

SPIKE_SET = [
    "hawker_2020",
    "hsu_2020",
    "hansen_2025",
    "paischer_2025",
    "aries_cost_account",
]
RUN_NAME = "table_spike_track1"
TRACK0_RUN = "table_spike_track0"

PROMPTS_DIR = CORPUS_DIR / "prompts"
TABLE_PROMPT_FILE = PROMPTS_DIR / "extract_table_cropped.txt"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class TableExtractionResult:
    """Result of Claude extracting one table from a cropped image."""

    slug: str
    page_num: int
    table_idx: int
    detector: str  # "gmft" or "pymupdf"
    image_path: str  # Relative to track0 output dir
    image_width: int
    image_height: int
    # GMFT comparison data
    gmft_rows: int | None  # From GMFT DataFrame (None if pymupdf-only)
    gmft_markdown: str | None
    # Claude extraction results
    claude_markdown: str | None  # None if dry-run or error
    claude_rows: int  # Row count from Claude's output
    # Cost tracking
    input_tokens: int
    output_tokens: int
    total_cost_usd: float
    wall_clock_seconds: float
    model: str
    # Status
    error: str | None = None


# ---------------------------------------------------------------------------
# Claude integration (adapted from h3_pymupdf_claude_eq.py)
# ---------------------------------------------------------------------------


def invoke_claude(prompt: str, model: str = "sonnet", timeout: int = 300) -> dict:
    """Invoke claude -p with a prompt piped via stdin.

    Returns parsed JSON response.
    """
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


def extract_table_with_claude(
    image_abs_path: Path,
    prompt_text: str,
    model: str = "sonnet",
    timeout: int = 300,
) -> tuple[str, dict]:
    """Send a cropped table image to Claude for extraction.

    Returns:
        (markdown_table, cost_data)
    """
    prompt = (
        f"Read the image file at {image_abs_path} and extract its content.\n\n"
        f"{prompt_text}"
    )

    start = time.time()
    response = invoke_claude(prompt, model=model, timeout=timeout)
    elapsed = time.time() - start

    markdown = response.get("result", "")
    if not markdown:
        raise RuntimeError(f"claude -p returned empty result")

    cost_data = {
        "total_cost_usd": response.get("total_cost_usd", 0),
        "input_tokens": response.get("usage", {}).get("input_tokens", 0),
        "output_tokens": response.get("usage", {}).get("output_tokens", 0),
        "wall_clock_seconds": elapsed,
        "model": response.get("model", model),
    }

    return markdown, cost_data


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------


def load_manifest(slug: str) -> list[dict]:
    """Load images_manifest.json from Track 0 output."""
    manifest_path = RUNS_DIR / TRACK0_RUN / slug / "images_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Track 0 manifest not found: {manifest_path}\n"
            f"Run track0_detection.py first."
        )
    return json.loads(manifest_path.read_text())


def select_tables(manifest: list[dict], detector: str = "gmft") -> list[dict]:
    """Select which tables to send to Claude.

    Args:
        manifest: Full manifest from Track 0.
        detector: "gmft" (default), "pymupdf", or "both".

    Returns:
        List of non-filtered table entries matching the detector criteria.
    """
    selected = []
    for entry in manifest:
        # Skip filtered tables
        if entry.get("filtered", False):
            continue

        if detector == "both":
            selected.append(entry)
        elif entry["detector"] == detector:
            selected.append(entry)

    return selected


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run_track1(
    slug: str,
    prompt_text: str,
    model: str = "sonnet",
    detector: str = "gmft",
    dry_run: bool = False,
) -> list[TableExtractionResult]:
    """Run Track 1 on a single paper."""
    print(f"\n{'='*60}")
    print(f"  {slug}")
    print(f"{'='*60}")

    # Load Track 0 manifest
    try:
        manifest = load_manifest(slug)
    except FileNotFoundError as e:
        print(f"  SKIP: {e}")
        return []

    tables = select_tables(manifest, detector=detector)
    if not tables:
        print(f"  No tables to process (detector={detector})")
        return []

    track0_dir = RUNS_DIR / TRACK0_RUN / slug
    output_dir = RUNS_DIR / RUN_NAME / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Tables to extract: {len(tables)} (detector={detector})")

    # Load ground truth for comparison
    gt_map = load_ground_truth()
    gt = gt_map.get(slug)
    gt_table_rows = gt.expected_metric_table_rows if gt else None

    results: list[TableExtractionResult] = []

    for entry in tables:
        page_num = entry["page_num"]
        table_idx = entry["table_idx"]
        det = entry["detector"]
        img_rel = entry["image_path"]
        img_abs = track0_dir / img_rel

        tag = f"p{page_num:03d}_t{table_idx} ({det})"

        # GMFT comparison data
        gmft_rows = entry.get("num_rows")
        gmft_md = entry.get("markdown")

        if dry_run:
            print(f"    {tag}: {img_abs.name} ({entry['image_width']}x{entry['image_height']}px) [DRY RUN]")
            results.append(TableExtractionResult(
                slug=slug,
                page_num=page_num,
                table_idx=table_idx,
                detector=det,
                image_path=img_rel,
                image_width=entry["image_width"],
                image_height=entry["image_height"],
                gmft_rows=gmft_rows,
                gmft_markdown=gmft_md,
                claude_markdown=None,
                claude_rows=0,
                input_tokens=0,
                output_tokens=0,
                total_cost_usd=0,
                wall_clock_seconds=0,
                model=model,
            ))
            continue

        print(f"    {tag}: ", end="", flush=True)

        try:
            claude_md, cost = extract_table_with_claude(
                img_abs.resolve(), prompt_text, model=model
            )
            claude_rows = count_real_table_rows(claude_md)

            # Save Claude's output
            md_filename = f"table_p{page_num:03d}_t{table_idx}_claude.md"
            (output_dir / md_filename).write_text(claude_md)

            print(
                f"{cost['wall_clock_seconds']:.1f}s | "
                f"${cost['total_cost_usd']:.4f} | "
                f"Claude={claude_rows}r"
                f"{f' GMFT={gmft_rows}r' if gmft_rows is not None else ''}"
            )

            results.append(TableExtractionResult(
                slug=slug,
                page_num=page_num,
                table_idx=table_idx,
                detector=det,
                image_path=img_rel,
                image_width=entry["image_width"],
                image_height=entry["image_height"],
                gmft_rows=gmft_rows,
                gmft_markdown=gmft_md,
                claude_markdown=claude_md,
                claude_rows=claude_rows,
                input_tokens=cost["input_tokens"],
                output_tokens=cost["output_tokens"],
                total_cost_usd=cost["total_cost_usd"],
                wall_clock_seconds=cost["wall_clock_seconds"],
                model=cost["model"],
            ))

        except Exception as e:
            print(f"ERROR: {e}")
            results.append(TableExtractionResult(
                slug=slug,
                page_num=page_num,
                table_idx=table_idx,
                detector=det,
                image_path=img_rel,
                image_width=entry["image_width"],
                image_height=entry["image_height"],
                gmft_rows=gmft_rows,
                gmft_markdown=gmft_md,
                claude_markdown=None,
                claude_rows=0,
                input_tokens=0,
                output_tokens=0,
                total_cost_usd=0,
                wall_clock_seconds=0,
                model=model,
                error=str(e),
            ))

    if not dry_run and results:
        # Save results
        results_data = [asdict(r) for r in results]
        # Strip large markdown fields from results.json for readability
        results_summary = []
        for r in results_data:
            summary = {k: v for k, v in r.items() if k not in ("gmft_markdown", "claude_markdown")}
            results_summary.append(summary)
        (output_dir / "results.json").write_text(
            json.dumps(results_summary, indent=2) + "\n"
        )

        # Comparison table
        comparison = {
            "slug": slug,
            "gt_expected_table_rows": gt_table_rows,
            "tables": [],
        }
        total_claude_rows = 0
        total_gmft_rows = 0
        total_cost = 0.0
        total_time = 0.0

        for r in results:
            total_claude_rows += r.claude_rows
            if r.gmft_rows is not None:
                total_gmft_rows += r.gmft_rows
            total_cost += r.total_cost_usd
            total_time += r.wall_clock_seconds

            comparison["tables"].append({
                "page": r.page_num,
                "table_idx": r.table_idx,
                "detector": r.detector,
                "claude_rows": r.claude_rows,
                "gmft_rows": r.gmft_rows,
                "cost_usd": r.total_cost_usd,
                "image_size": f"{r.image_width}x{r.image_height}",
            })

        comparison["totals"] = {
            "claude_total_rows": total_claude_rows,
            "gmft_total_rows": total_gmft_rows,
            "total_cost_usd": total_cost,
            "total_time_seconds": total_time,
            "table_count": len(results),
            "errors": sum(1 for r in results if r.error),
        }

        (output_dir / "comparison.json").write_text(
            json.dumps(comparison, indent=2) + "\n"
        )

        # Print summary
        print(f"\n  Summary for {slug}:")
        print(f"    Tables extracted: {len(results)}")
        print(f"    Claude total rows: {total_claude_rows}")
        print(f"    GMFT total rows:   {total_gmft_rows}")
        if gt_table_rows:
            print(f"    GT expected rows:  {gt_table_rows}")
        print(f"    Total cost: ${total_cost:.4f}")
        print(f"    Total time: {total_time:.1f}s")
        if total_cost > 0 and len(results) > 0:
            print(f"    Avg cost/table: ${total_cost / len(results):.4f}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Track 1: Claude cropped-image table extraction"
    )
    parser.add_argument(
        "--slugs",
        type=str,
        default=",".join(SPIKE_SET),
        help=f"Comma-separated paper slugs (default: {','.join(SPIKE_SET)})",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="sonnet",
        help="Claude model to use (default: sonnet)",
    )
    parser.add_argument(
        "--detector",
        type=str,
        default="gmft",
        choices=["gmft", "pymupdf", "both"],
        help="Which detector's tables to extract (default: gmft)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be sent without calling Claude",
    )
    args = parser.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",")]

    print(f"Track 1: Claude Cropped-Image Table Extraction")
    print(f"Papers: {', '.join(slugs)}")
    print(f"Detector: {args.detector}")
    print(f"Model: {args.model}")
    if args.dry_run:
        print(f"MODE: DRY RUN (no Claude calls)")

    # Load prompt
    prompt_text = TABLE_PROMPT_FILE.read_text().strip()

    all_results: list[TableExtractionResult] = []
    for slug in slugs:
        results = run_track1(
            slug, prompt_text,
            model=args.model,
            detector=args.detector,
            dry_run=args.dry_run,
        )
        all_results.extend(results)

    # Cross-paper summary
    if all_results and not args.dry_run:
        print(f"\n{'='*60}")
        print(f"  Cross-Paper Summary")
        print(f"{'='*60}")

        gt_map = load_ground_truth()

        print(f"  {'Slug':<25} {'Tables':>6} {'Claude':>7} {'GMFT':>6} {'GT':>5} {'Cost':>8} {'Time':>6}")
        print(f"  {'-'*25} {'-'*6} {'-'*7} {'-'*6} {'-'*5} {'-'*8} {'-'*6}")

        by_slug: dict[str, list[TableExtractionResult]] = {}
        for r in all_results:
            by_slug.setdefault(r.slug, []).append(r)

        grand_cost = 0.0
        grand_time = 0.0

        for slug, results in by_slug.items():
            claude_rows = sum(r.claude_rows for r in results)
            gmft_rows = sum(r.gmft_rows or 0 for r in results)
            cost = sum(r.total_cost_usd for r in results)
            wall = sum(r.wall_clock_seconds for r in results)
            gt = gt_map.get(slug)
            gt_rows = gt.expected_metric_table_rows if gt else None

            grand_cost += cost
            grand_time += wall

            print(
                f"  {slug:<25} {len(results):>6} {claude_rows:>7} "
                f"{gmft_rows:>6} {str(gt_rows or '?'):>5} "
                f"${cost:>7.4f} {wall:>5.1f}s"
            )

        print(f"  {'-'*25} {'-'*6} {'-'*7} {'-'*6} {'-'*5} {'-'*8} {'-'*6}")
        print(
            f"  {'TOTAL':<25} {len(all_results):>6} "
            f"{sum(r.claude_rows for r in all_results):>7} "
            f"{sum(r.gmft_rows or 0 for r in all_results):>6} "
            f"{'':>5} "
            f"${grand_cost:>7.4f} {grand_time:>5.1f}s"
        )

    # Save cross-paper summary
    if all_results and not args.dry_run:
        summary_dir = RUNS_DIR / RUN_NAME
        summary_dir.mkdir(parents=True, exist_ok=True)
        cross_summary = []
        by_slug = {}
        for r in all_results:
            by_slug.setdefault(r.slug, []).append(r)
        for slug, results in by_slug.items():
            cross_summary.append({
                "slug": slug,
                "table_count": len(results),
                "claude_total_rows": sum(r.claude_rows for r in results),
                "gmft_total_rows": sum(r.gmft_rows or 0 for r in results),
                "total_cost_usd": sum(r.total_cost_usd for r in results),
                "total_time_seconds": sum(r.wall_clock_seconds for r in results),
                "errors": sum(1 for r in results if r.error),
            })
        (summary_dir / "cross_paper_summary.json").write_text(
            json.dumps(cross_summary, indent=2) + "\n"
        )

    print(f"\n{'='*60}")
    print(f"  Done. Results in runs/{RUN_NAME}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

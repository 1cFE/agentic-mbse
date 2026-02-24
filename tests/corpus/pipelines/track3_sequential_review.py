#!/usr/bin/env python3
"""Track 3: Sequential multi-pass — Claude reviews GMFT output with table image.

Sends Claude both the GMFT-extracted markdown table AND the cropped table image.
Claude acts as a reviewer/corrector rather than an independent extractor.
Measures accuracy vs ground truth and checks for reasoning leakage.

Usage:
    python tests/corpus/pipelines/track3_sequential_review.py --dry-run
    python tests/corpus/pipelines/track3_sequential_review.py --slugs hawker_2020
    python tests/corpus/pipelines/track3_sequential_review.py
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared import CORPUS_DIR, RUNS_DIR, count_real_table_rows
from metrics import load_ground_truth

SPIKE_SET = [
    "hawker_2020",
    "hsu_2020",
    "hansen_2025",
    "paischer_2025",
    "aries_cost_account",
]
RUN_NAME = "table_spike_track3"
TRACK0_RUN = "table_spike_track0"
TRACK1_RUN = "table_spike_track1"

PROMPTS_DIR = CORPUS_DIR / "prompts"
REVIEW_PROMPT_FILE = PROMPTS_DIR / "review_table.txt"

# Reasoning leakage detection patterns
LEAKAGE_PATTERNS = [
    re.compile(r"\bI notice\b", re.IGNORECASE),
    re.compile(r"\bI can see\b", re.IGNORECASE),
    re.compile(r"\bLooking at\b", re.IGNORECASE),
    re.compile(r"\bIt appears\b", re.IGNORECASE),
    re.compile(r"\bThe table\b", re.IGNORECASE),
    re.compile(r"\bHere is\b", re.IGNORECASE),
    re.compile(r"\bCorrected\b", re.IGNORECASE),
    re.compile(r"\bNote:\b", re.IGNORECASE),
    re.compile(r"\bChanges?\b.*:", re.IGNORECASE),
    re.compile(r"^[^|].*[a-zA-Z]{10,}", re.MULTILINE),  # Long non-table text lines
]


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ReviewResult:
    """Result of Claude reviewing one GMFT-extracted table."""

    slug: str
    page_num: int
    table_idx: int
    image_path: str
    # Input data
    gmft_markdown: str
    gmft_rows: int
    # Track 1 comparison (independent Claude)
    track1_claude_rows: int | None
    # Review output
    reviewed_markdown: str | None
    reviewed_rows: int
    # Leakage detection
    has_leakage: bool
    leakage_matches: list[str]
    # Cost tracking
    input_tokens: int
    output_tokens: int
    total_cost_usd: float
    wall_clock_seconds: float
    model: str
    # Status
    error: str | None = None


# ---------------------------------------------------------------------------
# Claude integration
# ---------------------------------------------------------------------------


def invoke_claude(prompt: str, model: str = "sonnet", timeout: int = 300) -> dict:
    """Invoke claude -p with a prompt piped via stdin."""
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


def review_table_with_claude(
    image_abs_path: Path,
    gmft_markdown: str,
    prompt_template: str,
    model: str = "sonnet",
    timeout: int = 300,
) -> tuple[str, dict]:
    """Send GMFT table + cropped image to Claude for review/correction.

    Returns:
        (reviewed_markdown, cost_data)
    """
    # Fill in the template
    review_text = prompt_template.replace("{gmft_markdown}", gmft_markdown)

    # Build prompt with image reference
    prompt = (
        f"Read the image file at {image_abs_path} and then follow these instructions:\n\n"
        f"{review_text}"
    )

    start = time.time()
    response = invoke_claude(prompt, model=model, timeout=timeout)
    elapsed = time.time() - start

    markdown = response.get("result", "")
    if not markdown:
        raise RuntimeError("claude -p returned empty result")

    cost_data = {
        "total_cost_usd": response.get("total_cost_usd", 0),
        "input_tokens": response.get("usage", {}).get("input_tokens", 0),
        "output_tokens": response.get("usage", {}).get("output_tokens", 0),
        "wall_clock_seconds": elapsed,
        "model": response.get("model", model),
    }

    return markdown, cost_data


def detect_leakage(text: str) -> tuple[bool, list[str]]:
    """Check for reasoning leakage (non-table commentary) in Claude's output.

    Returns (has_leakage, list of matched patterns).
    """
    matches = []
    for pattern in LEAKAGE_PATTERNS:
        if pattern.search(text):
            matches.append(pattern.pattern)
    return bool(matches), matches


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_reviewable_tables(slug: str) -> list[dict]:
    """Load tables that have GMFT markdown + images for review.

    Returns list of dicts with keys:
        page_num, table_idx, gmft_markdown, gmft_rows, image_abs_path,
        track1_claude_rows
    """
    # Load Track 0 manifest
    manifest_path = RUNS_DIR / TRACK0_RUN / slug / "images_manifest.json"
    if not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text())

    track0_dir = RUNS_DIR / TRACK0_RUN / slug

    # Load Track 1 results for comparison
    track1_results_path = RUNS_DIR / TRACK1_RUN / slug / "results.json"
    track1_by_key: dict[tuple[int, int], int] = {}
    if track1_results_path.exists():
        track1_results = json.loads(track1_results_path.read_text())
        for r in track1_results:
            if not r.get("error"):
                track1_by_key[(r["page_num"], r["table_idx"])] = r["claude_rows"]

    tables = []
    for entry in manifest:
        if entry["detector"] != "gmft":
            continue
        if entry.get("filtered", False):
            continue
        gmft_md = entry.get("markdown")
        if gmft_md is None:
            continue  # GMFT DataFrame extraction failed — can't review

        img_path = track0_dir / entry["image_path"]
        if not img_path.exists():
            continue

        key = (entry["page_num"], entry["table_idx"])
        tables.append({
            "page_num": entry["page_num"],
            "table_idx": entry["table_idx"],
            "gmft_markdown": gmft_md,
            "gmft_rows": count_real_table_rows(gmft_md),
            "image_abs_path": img_path.resolve(),
            "track1_claude_rows": track1_by_key.get(key),
        })

    return tables


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run_track3(
    slug: str,
    prompt_template: str,
    model: str = "sonnet",
    dry_run: bool = False,
) -> list[ReviewResult]:
    """Run Track 3 sequential review on a single paper."""
    print(f"\n{'='*60}")
    print(f"  {slug}")
    print(f"{'='*60}")

    tables = load_reviewable_tables(slug)
    if not tables:
        print(f"  No reviewable tables found (need GMFT markdown + image)")
        return []

    output_dir = RUNS_DIR / RUN_NAME / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Reviewable tables: {len(tables)}")

    gt_map = load_ground_truth()
    gt = gt_map.get(slug)
    gt_rows = gt.expected_metric_table_rows if gt else None

    results: list[ReviewResult] = []

    for entry in tables:
        page_num = entry["page_num"]
        table_idx = entry["table_idx"]
        tag = f"p{page_num:03d}_t{table_idx}"

        if dry_run:
            print(
                f"    {tag}: GMFT {entry['gmft_rows']}r, "
                f"Track1 {entry['track1_claude_rows'] or '?'}r [DRY RUN]"
            )
            results.append(ReviewResult(
                slug=slug,
                page_num=page_num,
                table_idx=table_idx,
                image_path=str(entry["image_abs_path"]),
                gmft_markdown=entry["gmft_markdown"],
                gmft_rows=entry["gmft_rows"],
                track1_claude_rows=entry["track1_claude_rows"],
                reviewed_markdown=None,
                reviewed_rows=0,
                has_leakage=False,
                leakage_matches=[],
                input_tokens=0,
                output_tokens=0,
                total_cost_usd=0,
                wall_clock_seconds=0,
                model=model,
            ))
            continue

        print(f"    {tag}: ", end="", flush=True)

        try:
            reviewed_md, cost = review_table_with_claude(
                entry["image_abs_path"],
                entry["gmft_markdown"],
                prompt_template,
                model=model,
            )
            reviewed_rows = count_real_table_rows(reviewed_md)
            has_leakage, leakage_matches = detect_leakage(reviewed_md)

            # Save reviewed output
            md_filename = f"table_p{page_num:03d}_t{table_idx}_reviewed.md"
            (output_dir / md_filename).write_text(reviewed_md)

            leakage_tag = " LEAKAGE!" if has_leakage else ""
            t1_rows = entry['track1_claude_rows']
            t1_tag = f" (Track1={t1_rows}r)" if t1_rows else ""
            print(
                f"{cost['wall_clock_seconds']:.1f}s | "
                f"${cost['total_cost_usd']:.4f} | "
                f"GMFT={entry['gmft_rows']}r → Reviewed={reviewed_rows}r"
                f"{t1_tag}{leakage_tag}"
            )

            results.append(ReviewResult(
                slug=slug,
                page_num=page_num,
                table_idx=table_idx,
                image_path=str(entry["image_abs_path"]),
                gmft_markdown=entry["gmft_markdown"],
                gmft_rows=entry["gmft_rows"],
                track1_claude_rows=entry["track1_claude_rows"],
                reviewed_markdown=reviewed_md,
                reviewed_rows=reviewed_rows,
                has_leakage=has_leakage,
                leakage_matches=leakage_matches,
                input_tokens=cost["input_tokens"],
                output_tokens=cost["output_tokens"],
                total_cost_usd=cost["total_cost_usd"],
                wall_clock_seconds=cost["wall_clock_seconds"],
                model=cost["model"],
            ))

        except Exception as e:
            print(f"ERROR: {e}")
            results.append(ReviewResult(
                slug=slug,
                page_num=page_num,
                table_idx=table_idx,
                image_path=str(entry["image_abs_path"]),
                gmft_markdown=entry["gmft_markdown"],
                gmft_rows=entry["gmft_rows"],
                track1_claude_rows=entry["track1_claude_rows"],
                reviewed_markdown=None,
                reviewed_rows=0,
                has_leakage=False,
                leakage_matches=[],
                input_tokens=0,
                output_tokens=0,
                total_cost_usd=0,
                wall_clock_seconds=0,
                model=model,
                error=str(e),
            ))

    if not dry_run and results:
        # Save results (strip large markdown fields for readability)
        results_summary = []
        for r in results:
            d = asdict(r)
            del d["gmft_markdown"]
            del d["reviewed_markdown"]
            results_summary.append(d)
        (output_dir / "results.json").write_text(
            json.dumps(results_summary, indent=2) + "\n"
        )

        # Comparison
        total_gmft = sum(r.gmft_rows for r in results)
        total_reviewed = sum(r.reviewed_rows for r in results)
        total_track1 = sum(r.track1_claude_rows or 0 for r in results)
        total_cost = sum(r.total_cost_usd for r in results)
        total_time = sum(r.wall_clock_seconds for r in results)
        leakage_count = sum(1 for r in results if r.has_leakage)

        comparison = {
            "slug": slug,
            "gt_expected_table_rows": gt_rows,
            "tables_reviewed": len(results),
            "gmft_total_rows": total_gmft,
            "reviewed_total_rows": total_reviewed,
            "track1_claude_total_rows": total_track1,
            "total_cost_usd": total_cost,
            "total_time_seconds": total_time,
            "leakage_count": leakage_count,
            "errors": sum(1 for r in results if r.error),
            "per_table": [
                {
                    "page": r.page_num,
                    "table_idx": r.table_idx,
                    "gmft_rows": r.gmft_rows,
                    "reviewed_rows": r.reviewed_rows,
                    "track1_rows": r.track1_claude_rows,
                    "cost_usd": r.total_cost_usd,
                    "has_leakage": r.has_leakage,
                }
                for r in results
            ],
        }
        (output_dir / "comparison.json").write_text(
            json.dumps(comparison, indent=2) + "\n"
        )

        # Print summary
        print(f"\n  Summary:")
        print(f"    Tables reviewed:       {len(results)}")
        print(f"    GMFT total rows:       {total_gmft}")
        print(f"    Reviewed total rows:   {total_reviewed}")
        print(f"    Track 1 Claude rows:   {total_track1}")
        if gt_rows:
            print(f"    GT expected rows:      {gt_rows}")
        print(f"    Total cost:            ${total_cost:.4f}")
        print(f"    Reasoning leakage:     {leakage_count}/{len(results)} tables")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Track 3: Sequential review — Claude corrects GMFT with table image"
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
        "--dry-run",
        action="store_true",
        help="Show what would be reviewed without calling Claude",
    )
    args = parser.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",")]

    print(f"Track 3: Sequential Review (Claude corrects GMFT)")
    print(f"Papers: {', '.join(slugs)}")
    print(f"Model: {args.model}")
    if args.dry_run:
        print(f"MODE: DRY RUN (no Claude calls)")

    prompt_template = REVIEW_PROMPT_FILE.read_text().strip()

    all_results: list[ReviewResult] = []
    for slug in slugs:
        results = run_track3(
            slug, prompt_template,
            model=args.model,
            dry_run=args.dry_run,
        )
        all_results.extend(results)

    # Cross-paper summary
    if all_results and not args.dry_run:
        print(f"\n{'='*60}")
        print(f"  Cross-Paper Summary")
        print(f"{'='*60}")
        print(f"  {'Slug':<25} {'Tbls':>4} {'GMFT':>5} {'Rev':>5} {'T1':>5} {'GT':>5} {'Cost':>8} {'Leak':>4}")
        print(f"  {'-'*25} {'-'*4} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*8} {'-'*4}")

        gt_map = load_ground_truth()
        by_slug: dict[str, list[ReviewResult]] = {}
        for r in all_results:
            by_slug.setdefault(r.slug, []).append(r)

        cross_summary = []
        for slug, results in by_slug.items():
            gt = gt_map.get(slug)
            gt_str = str(gt.expected_metric_table_rows) if gt and gt.expected_metric_table_rows else "?"
            gmft = sum(r.gmft_rows for r in results)
            rev = sum(r.reviewed_rows for r in results)
            t1 = sum(r.track1_claude_rows or 0 for r in results)
            cost = sum(r.total_cost_usd for r in results)
            leak = sum(1 for r in results if r.has_leakage)

            print(
                f"  {slug:<25} {len(results):>4} {gmft:>5} {rev:>5} "
                f"{t1:>5} {gt_str:>5} ${cost:>7.4f} {leak:>4}"
            )

            cross_summary.append({
                "slug": slug,
                "tables_reviewed": len(results),
                "gmft_total_rows": gmft,
                "reviewed_total_rows": rev,
                "track1_total_rows": t1,
                "total_cost_usd": cost,
                "leakage_count": leak,
            })

        summary_dir = RUNS_DIR / RUN_NAME
        summary_dir.mkdir(parents=True, exist_ok=True)
        (summary_dir / "cross_paper_summary.json").write_text(
            json.dumps(cross_summary, indent=2) + "\n"
        )

    print(f"\n{'='*60}")
    print(f"  Done. Results in runs/{RUN_NAME}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

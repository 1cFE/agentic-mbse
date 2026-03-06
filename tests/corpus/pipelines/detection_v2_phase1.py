#!/usr/bin/env python3
"""Detection v2 Phase 1: Test lowered GMFT confidence threshold.

Uses existing Track 0 detection data (all 26 raw detections on aries_cost_account).
Sends the 7 recovered real tables (conf 0.90-0.98) to Claude for extraction.
Compares row counts against original Track 1 results.

Usage:
    python tests/corpus/pipelines/detection_v2_phase1.py
    python tests/corpus/pipelines/detection_v2_phase1.py --dry-run
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared import CORPUS_DIR, RUNS_DIR

TRACK0_DIR = RUNS_DIR / "table_spike_track0" / "aries_cost_account"
TRACK1_DIR = RUNS_DIR / "table_spike_track1" / "aries_cost_account"
OUTPUT_DIR = RUNS_DIR / "detection_v2" / "phase1_threshold"

# Pages visually confirmed as FALSE POSITIVES (not tables)
CONFIRMED_FP_PAGES = {33, 42, 48, 60, 65}
# Page 91 is caught by single-row filter (1 row, 10 cols) — layout artifact
LAYOUT_ARTIFACT_PAGES = {91}

PROMPT_PATH = CORPUS_DIR / "prompts" / "extract_table_cropped.txt"


def load_track0_manifest():
    """Load Track 0 images manifest for GMFT detections."""
    manifest_path = TRACK0_DIR / "images_manifest.json"
    data = json.loads(manifest_path.read_text())
    return [d for d in data if d["detector"] == "gmft"]


def load_track1_results():
    """Load Track 1 Claude extraction results for comparison."""
    results_path = TRACK1_DIR / "results.json"
    if results_path.exists():
        return json.loads(results_path.read_text())
    return {}


def invoke_claude(prompt_text: str, image_path: Path) -> tuple[str, dict]:
    """Send image + prompt to Claude and return (response_text, cost_data).

    Uses the same approach as track1_cropped_extraction.py:
    - Unset CLAUDECODE env var to allow nested invocation
    - Tell Claude to Read the image file, then apply the prompt
    """
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    full_prompt = (
        f"Read the image file at {image_path.resolve()} and extract its content.\n\n"
        f"{prompt_text}"
    )

    cmd = [
        "claude", "-p",
        "--model", "sonnet",
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--no-session-persistence",
        "--allowedTools", "Read",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return "ERROR: timeout", {}

    if result.returncode != 0:
        return f"ERROR: {result.stderr[:300]}", {}

    try:
        response = json.loads(result.stdout)
        text = response.get("result", "")
        cost_data = {
            "input_tokens": response.get("usage", {}).get("input_tokens", 0),
            "output_tokens": response.get("usage", {}).get("output_tokens", 0),
            "total_cost_usd": response.get("total_cost_usd", 0),
        }
        return text, cost_data
    except json.JSONDecodeError:
        return result.stdout, {}


def count_pipe_rows(text: str) -> int:
    """Count lines with >= 2 pipe characters."""
    return sum(1 for line in text.split("\n") if line.count("|") >= 2)


def main():
    parser = argparse.ArgumentParser(description="Detection v2 Phase 1: Threshold test")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without calling Claude")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = load_track0_manifest()
    prompt = PROMPT_PATH.read_text().strip()

    # Categorize all GMFT detections
    original_kept = []     # Passed 0.98 filter (original Track 0/1)
    recovered = []         # Would be recovered by lowering threshold
    still_filtered = []    # Still filtered (FPs, layout artifacts)

    for entry in manifest:
        page = entry["page_num"]
        conf = entry["confidence"]
        was_filtered = entry["filtered"]

        if page in LAYOUT_ARTIFACT_PAGES:
            still_filtered.append(entry)
        elif page in CONFIRMED_FP_PAGES:
            if was_filtered:
                still_filtered.append(entry)
            else:
                # p42, p48 passed 0.98 but are FPs — Claude catches these
                original_kept.append(entry)
        elif was_filtered:
            # Was filtered at 0.98 but is a real table
            recovered.append(entry)
        else:
            original_kept.append(entry)

    print("=" * 60)
    print("  Detection v2 Phase 1: GMFT Threshold Analysis")
    print("=" * 60)
    print()
    print(f"  Original (0.98 filter):  {len(original_kept)} kept")
    print(f"  Recovered (0.90-0.98):   {len(recovered)} tables")
    print(f"  Still filtered (FP/art): {len(still_filtered)} rejected")
    print()

    print("  RECOVERED TABLES (conf 0.90-0.98, visually confirmed real):")
    for entry in sorted(recovered, key=lambda x: x["page_num"]):
        page = entry["page_num"]
        conf = entry["confidence"]
        rows = entry["num_rows"]
        cols = entry["num_cols"]
        img = entry["image_path"]
        print(f"    p{page:3d}  conf={conf:.3f}  rows={rows}  cols={cols}  {img}")

    print()
    print("  STILL FILTERED (confirmed false positives / artifacts):")
    for entry in sorted(still_filtered, key=lambda x: x["page_num"]):
        page = entry["page_num"]
        conf = entry["confidence"]
        reason = entry.get("filter_reason", "visual FP")
        print(f"    p{page:3d}  conf={conf:.3f}  reason={reason}")

    if args.dry_run:
        print(f"\n  [DRY RUN] Would send {len(recovered)} images to Claude for extraction.")
        print(f"  Estimated cost: ~$0.076 x {len(recovered)} = ~${0.076 * len(recovered):.2f}")
        return

    # Send recovered tables to Claude for extraction
    print()
    print("=" * 60)
    print("  Extracting recovered tables with Claude...")
    print("=" * 60)

    results = []
    total_cost = 0.0

    for entry in sorted(recovered, key=lambda x: x["page_num"]):
        page = entry["page_num"]
        conf = entry["confidence"]
        img_path = TRACK0_DIR / entry["image_path"]

        print(f"\n  p{page} (conf={conf:.3f})...", end=" ", flush=True)
        start = time.time()

        response, cost_data = invoke_claude(prompt, img_path)
        elapsed = time.time() - start

        rows = count_pipe_rows(response)
        input_tokens = cost_data.get("input_tokens", 0)
        output_tokens = cost_data.get("output_tokens", 0)
        cost = cost_data.get("total_cost_usd", 0)
        if cost == 0 and input_tokens > 0:
            cost = (input_tokens * 3.0 / 1_000_000) + (output_tokens * 15.0 / 1_000_000)
        total_cost += cost

        is_table = rows > 0
        status = f"{rows} rows" if is_table else "NOT A TABLE"
        print(f"{elapsed:.1f}s — {status} (${cost:.3f})")

        # Save extracted table
        if is_table:
            md_path = OUTPUT_DIR / f"table_p{page:03d}_t0_claude.md"
            md_path.write_text(response)

        results.append({
            "page": page,
            "confidence": conf,
            "image_path": entry["image_path"],
            "claude_rows": rows,
            "is_table": is_table,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "elapsed": elapsed,
            "gmft_df_rows": entry["num_rows"],
            "gmft_df_cols": entry["num_cols"],
        })

    # Save results
    (OUTPUT_DIR / "results.json").write_text(json.dumps(results, indent=2) + "\n")

    # Summary
    recovered_tp = sum(1 for r in results if r["is_table"])
    recovered_fp = sum(1 for r in results if not r["is_table"])
    recovered_rows = sum(r["claude_rows"] for r in results)

    # Load Track 1 for comparison
    track1_data = load_track1_results()

    print()
    print("=" * 60)
    print("  Phase 1 Results Summary")
    print("=" * 60)
    print()
    print(f"  Recovered tables sent to Claude:    {len(results)}")
    print(f"  Claude confirmed as tables (TP):    {recovered_tp}")
    print(f"  Claude rejected as non-tables (FP): {recovered_fp}")
    print(f"  Total rows from recovered tables:   {recovered_rows}")
    print(f"  Total cost:                         ${total_cost:.3f}")
    print()

    # Original Track 1 on aries: 15 detections → 162 rows (13 TP, 2 FP)
    original_tp = 13  # From findings.md
    original_rows = 162  # From findings.md
    gt_tables = 28
    gt_rows = 280

    new_tp = original_tp + recovered_tp
    new_rows = original_rows + recovered_rows
    print(f"  DETECTION RECALL COMPARISON:")
    print(f"    Original (0.98):  {original_tp}/{gt_tables} tables = {original_tp/gt_tables*100:.0f}% recall")
    print(f"    New (no conf):    {new_tp}/{gt_tables} tables = {new_tp/gt_tables*100:.0f}% recall")
    print(f"    Improvement:      +{recovered_tp} tables (+{recovered_tp/gt_tables*100:.0f}%)")
    print()
    print(f"  ROW COVERAGE COMPARISON:")
    print(f"    Original rows:    {original_rows}/{gt_rows} = {original_rows/gt_rows*100:.0f}%")
    print(f"    New rows:         {new_rows}/{gt_rows} = {new_rows/gt_rows*100:.0f}%")
    print(f"    Improvement:      +{recovered_rows} rows")
    print()
    print(f"  REMAINING GAP:")
    print(f"    Undetected tables: {gt_tables - new_tp} (GMFT finds nothing at any confidence)")
    print(f"    Missing rows:      {gt_rows - new_rows}")

    # Save summary
    summary = {
        "original_tp": original_tp,
        "original_rows": original_rows,
        "recovered_tp": recovered_tp,
        "recovered_fp": recovered_fp,
        "recovered_rows": recovered_rows,
        "new_tp": new_tp,
        "new_rows": new_rows,
        "gt_tables": gt_tables,
        "gt_rows": gt_rows,
        "new_recall_tables": new_tp / gt_tables,
        "new_recall_rows": new_rows / gt_rows,
        "total_cost": total_cost,
        "confirmed_fp_pages": sorted(CONFIRMED_FP_PAGES),
        "layout_artifact_pages": sorted(LAYOUT_ARTIFACT_PAGES),
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()

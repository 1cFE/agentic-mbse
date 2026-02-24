#!/usr/bin/env python3
"""Track 2: Independent multi-pass vote/resolve between GMFT and Claude.

Loads GMFT DataFrame markdown (from Track 0 manifest) and Claude cropped-image
markdown (from Track 1 output). For tables where both exist, implements two
resolution strategies and scores against ground truth.

No Claude API calls — this is pure comparison logic.

Usage:
    python tests/corpus/pipelines/track2_vote_resolve.py
    python tests/corpus/pipelines/track2_vote_resolve.py --slugs hawker_2020
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared import RUNS_DIR, count_real_table_rows
from metrics import load_ground_truth

SPIKE_SET = [
    "hawker_2020",
    "hsu_2020",
    "hansen_2025",
    "paischer_2025",
    "aries_cost_account",
]
RUN_NAME = "table_spike_track2"
TRACK0_RUN = "table_spike_track0"
TRACK1_RUN = "table_spike_track1"


# ---------------------------------------------------------------------------
# Markdown table parsing
# ---------------------------------------------------------------------------


def parse_pipe_table(markdown: str) -> list[list[str]]:
    """Parse a markdown pipe table into a list of rows, each a list of cells.

    Returns all rows including header and separator.
    Separator rows are included but marked with cells like '---'.
    """
    rows = []
    for line in markdown.strip().split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        if line.count("|") < 2:
            continue
        # Split on | and strip whitespace
        cells = [c.strip() for c in line.split("|")]
        # Remove empty first/last cells from leading/trailing |
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        rows.append(cells)
    return rows


def is_separator_row(cells: list[str]) -> bool:
    """Check if a parsed row is a separator (|---|---|---|)."""
    return all(re.match(r"^[-:]+$", c.strip()) for c in cells if c.strip())


def get_data_rows(parsed: list[list[str]]) -> list[list[str]]:
    """Extract just data rows (not header, not separator) from parsed table."""
    if len(parsed) < 3:
        return parsed  # Not a well-formed table
    # Typically: row 0 = header, row 1 = separator, rest = data
    data = []
    for row in parsed[2:]:  # Skip header + separator
        if not is_separator_row(row):
            data.append(row)
    return data


# ---------------------------------------------------------------------------
# Resolution strategies
# ---------------------------------------------------------------------------


def resolve_prefer_higher_rows(gmft_md: str, claude_md: str) -> tuple[str, str]:
    """Strategy A: Prefer whichever table has more rows.

    Returns (chosen_markdown, reason).
    """
    gmft_rows = count_real_table_rows(gmft_md)
    claude_rows = count_real_table_rows(claude_md)

    if claude_rows > gmft_rows:
        return claude_md, f"Claude has more rows ({claude_rows} > {gmft_rows})"
    elif gmft_rows > claude_rows:
        return gmft_md, f"GMFT has more rows ({gmft_rows} > {claude_rows})"
    else:
        # Tie — prefer Claude (accuracy ceiling from Phase 2 results)
        return claude_md, f"Tie ({claude_rows} rows each), defaulting to Claude"


def resolve_cell_level(gmft_md: str, claude_md: str) -> tuple[str, str, dict]:
    """Strategy B: Cell-level comparison, prefer Claude when disagreement.

    Parses both tables, compares cell by cell. When cells disagree, uses
    Claude's value. If tables have different row counts, falls back to
    preferring Claude (it has the accuracy ceiling).

    Returns (resolved_markdown, reason, details).
    """
    gmft_parsed = parse_pipe_table(gmft_md)
    claude_parsed = parse_pipe_table(claude_md)

    gmft_data = get_data_rows(gmft_parsed)
    claude_data = get_data_rows(claude_parsed)

    details = {
        "gmft_total_rows": len(gmft_parsed),
        "claude_total_rows": len(claude_parsed),
        "gmft_data_rows": len(gmft_data),
        "claude_data_rows": len(claude_data),
        "cells_compared": 0,
        "cells_agree": 0,
        "cells_disagree": 0,
    }

    # If different row counts, can't do cell-level comparison — prefer Claude
    if len(gmft_data) != len(claude_data):
        details["fallback"] = "different row counts"
        return (
            claude_md,
            f"Different data row counts (GMFT={len(gmft_data)}, Claude={len(claude_data)}), preferring Claude",
            details,
        )

    # Compare cell by cell on data rows
    disagreements = []
    for r_idx, (g_row, c_row) in enumerate(zip(gmft_data, claude_data)):
        max_cols = max(len(g_row), len(c_row))
        for c_idx in range(max_cols):
            g_val = g_row[c_idx].strip() if c_idx < len(g_row) else ""
            c_val = c_row[c_idx].strip() if c_idx < len(c_row) else ""
            details["cells_compared"] += 1

            # Normalize for comparison (strip whitespace, lowercase)
            g_norm = re.sub(r"\s+", " ", g_val.lower().strip())
            c_norm = re.sub(r"\s+", " ", c_val.lower().strip())

            if g_norm == c_norm:
                details["cells_agree"] += 1
            else:
                details["cells_disagree"] += 1
                disagreements.append({
                    "row": r_idx,
                    "col": c_idx,
                    "gmft": g_val,
                    "claude": c_val,
                })

    details["disagreements"] = disagreements

    if not disagreements:
        return (
            claude_md,  # Identical content — use Claude's formatting
            f"Tables agree on all {details['cells_compared']} cells",
            details,
        )

    # Disagreements exist — prefer Claude (it has higher accuracy from Phase 2)
    agree_pct = details["cells_agree"] / details["cells_compared"] * 100 if details["cells_compared"] else 0
    return (
        claude_md,
        f"{len(disagreements)} cell disagreements out of {details['cells_compared']} "
        f"({agree_pct:.0f}% agree), preferring Claude",
        details,
    )


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_table_pairs(slug: str) -> list[dict]:
    """Load matched GMFT + Claude table pairs for a paper.

    Returns list of dicts with keys:
        page_num, table_idx, gmft_markdown, claude_markdown,
        gmft_rows, claude_rows, image_path
    """
    # Load Track 0 manifest for GMFT data
    manifest_path = RUNS_DIR / TRACK0_RUN / slug / "images_manifest.json"
    if not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text())

    # Index GMFT tables by (page_num, table_idx)
    gmft_by_key: dict[tuple[int, int], dict] = {}
    for entry in manifest:
        if entry["detector"] == "gmft" and not entry.get("filtered", False):
            key = (entry["page_num"], entry["table_idx"])
            gmft_by_key[key] = entry

    # Load Track 1 Claude results
    track1_dir = RUNS_DIR / TRACK1_RUN / slug
    results_path = track1_dir / "results.json"
    if not results_path.exists():
        return []
    results = json.loads(results_path.read_text())

    # Match pairs
    pairs = []
    for r in results:
        if r.get("error"):
            continue
        key = (r["page_num"], r["table_idx"])
        gmft_entry = gmft_by_key.get(key)
        if gmft_entry is None:
            continue

        gmft_md = gmft_entry.get("markdown")
        if gmft_md is None:
            continue  # GMFT DataFrame extraction failed

        # Load Claude's markdown from file
        claude_md_path = track1_dir / f"table_p{r['page_num']:03d}_t{r['table_idx']}_claude.md"
        if not claude_md_path.exists():
            continue
        claude_md = claude_md_path.read_text().strip()
        if not claude_md or count_real_table_rows(claude_md) == 0:
            continue  # Claude returned non-table (e.g., "no table to extract")

        pairs.append({
            "page_num": r["page_num"],
            "table_idx": r["table_idx"],
            "gmft_markdown": gmft_md,
            "claude_markdown": claude_md,
            "gmft_rows": count_real_table_rows(gmft_md),
            "claude_rows": count_real_table_rows(claude_md),
            "image_path": r["image_path"],
        })

    return pairs


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run_track2(slug: str) -> dict | None:
    """Run Track 2 vote/resolve on a single paper."""
    print(f"\n{'='*60}")
    print(f"  {slug}")
    print(f"{'='*60}")

    pairs = load_table_pairs(slug)
    if not pairs:
        print(f"  No matched table pairs found")
        return None

    print(f"  Matched pairs: {len(pairs)} tables with both GMFT and Claude output")

    output_dir = RUNS_DIR / RUN_NAME / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    gt_map = load_ground_truth()
    gt = gt_map.get(slug)
    gt_rows = gt.expected_metric_table_rows if gt else None

    # Strategy A: Prefer higher row count
    strategy_a = []
    for pair in pairs:
        resolved_md, reason = resolve_prefer_higher_rows(
            pair["gmft_markdown"], pair["claude_markdown"]
        )
        resolved_rows = count_real_table_rows(resolved_md)
        chose = "claude" if resolved_md == pair["claude_markdown"] else "gmft"
        strategy_a.append({
            "page_num": pair["page_num"],
            "table_idx": pair["table_idx"],
            "gmft_rows": pair["gmft_rows"],
            "claude_rows": pair["claude_rows"],
            "resolved_rows": resolved_rows,
            "chosen": chose,
            "reason": reason,
        })
        print(f"    p{pair['page_num']:03d}_t{pair['table_idx']} [A]: {reason} → chose {chose}")

    # Strategy B: Cell-level comparison
    strategy_b = []
    for pair in pairs:
        resolved_md, reason, details = resolve_cell_level(
            pair["gmft_markdown"], pair["claude_markdown"]
        )
        resolved_rows = count_real_table_rows(resolved_md)
        chose = "claude" if resolved_md == pair["claude_markdown"] else "gmft"
        strategy_b.append({
            "page_num": pair["page_num"],
            "table_idx": pair["table_idx"],
            "gmft_rows": pair["gmft_rows"],
            "claude_rows": pair["claude_rows"],
            "resolved_rows": resolved_rows,
            "chosen": chose,
            "reason": reason,
            "cells_compared": details.get("cells_compared", 0),
            "cells_agree": details.get("cells_agree", 0),
            "cells_disagree": details.get("cells_disagree", 0),
        })
        print(f"    p{pair['page_num']:03d}_t{pair['table_idx']} [B]: {reason}")

    # Compute totals
    totals = {
        "slug": slug,
        "pairs": len(pairs),
        "gt_expected_table_rows": gt_rows,
        "gmft_total_rows": sum(p["gmft_rows"] for p in pairs),
        "claude_total_rows": sum(p["claude_rows"] for p in pairs),
        "strategy_a_total_rows": sum(r["resolved_rows"] for r in strategy_a),
        "strategy_b_total_rows": sum(r["resolved_rows"] for r in strategy_b),
        "strategy_a_chose_claude": sum(1 for r in strategy_a if r["chosen"] == "claude"),
        "strategy_a_chose_gmft": sum(1 for r in strategy_a if r["chosen"] == "gmft"),
        "strategy_b_chose_claude": sum(1 for r in strategy_b if r["chosen"] == "claude"),
        "strategy_b_chose_gmft": sum(1 for r in strategy_b if r["chosen"] == "gmft"),
        "strategy_b_total_cells_compared": sum(r["cells_compared"] for r in strategy_b),
        "strategy_b_total_cells_agree": sum(r["cells_agree"] for r in strategy_b),
        "strategy_b_total_cells_disagree": sum(r["cells_disagree"] for r in strategy_b),
    }

    print(f"\n  Summary:")
    print(f"    GMFT total rows:       {totals['gmft_total_rows']}")
    print(f"    Claude total rows:     {totals['claude_total_rows']}")
    print(f"    Strategy A total rows: {totals['strategy_a_total_rows']}")
    print(f"    Strategy B total rows: {totals['strategy_b_total_rows']}")
    if gt_rows:
        print(f"    GT expected rows:      {gt_rows}")
    print(f"    Strategy A chose: Claude={totals['strategy_a_chose_claude']}, GMFT={totals['strategy_a_chose_gmft']}")
    print(f"    Strategy B chose: Claude={totals['strategy_b_chose_claude']}, GMFT={totals['strategy_b_chose_gmft']}")
    if totals["strategy_b_total_cells_compared"] > 0:
        agree_pct = totals["strategy_b_total_cells_agree"] / totals["strategy_b_total_cells_compared"] * 100
        print(
            f"    Cell agreement: {totals['strategy_b_total_cells_agree']}"
            f"/{totals['strategy_b_total_cells_compared']} ({agree_pct:.0f}%)"
        )

    # Save outputs
    (output_dir / "strategy_a_results.json").write_text(
        json.dumps(strategy_a, indent=2) + "\n"
    )
    (output_dir / "strategy_b_results.json").write_text(
        json.dumps(strategy_b, indent=2) + "\n"
    )
    (output_dir / "comparison.json").write_text(
        json.dumps(totals, indent=2) + "\n"
    )

    return totals


def main():
    parser = argparse.ArgumentParser(
        description="Track 2: Vote/resolve between GMFT and Claude table extractions"
    )
    parser.add_argument(
        "--slugs",
        type=str,
        default=",".join(SPIKE_SET),
        help=f"Comma-separated paper slugs (default: {','.join(SPIKE_SET)})",
    )
    args = parser.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",")]

    print(f"Track 2: Vote/Resolve (GMFT vs Claude)")
    print(f"Papers: {', '.join(slugs)}")
    print(f"No Claude API calls — pure comparison logic")

    all_totals = []
    for slug in slugs:
        result = run_track2(slug)
        if result:
            all_totals.append(result)

    # Cross-paper summary
    if all_totals:
        print(f"\n{'='*60}")
        print(f"  Cross-Paper Summary")
        print(f"{'='*60}")
        print(f"  {'Slug':<25} {'Pairs':>5} {'GMFT':>5} {'Claude':>6} {'St.A':>5} {'St.B':>5} {'GT':>5}")
        print(f"  {'-'*25} {'-'*5} {'-'*5} {'-'*6} {'-'*5} {'-'*5} {'-'*5}")

        for t in all_totals:
            gt_str = str(t["gt_expected_table_rows"]) if t["gt_expected_table_rows"] else "?"
            print(
                f"  {t['slug']:<25} {t['pairs']:>5} "
                f"{t['gmft_total_rows']:>5} {t['claude_total_rows']:>6} "
                f"{t['strategy_a_total_rows']:>5} {t['strategy_b_total_rows']:>5} "
                f"{gt_str:>5}"
            )

        # Save cross-paper summary
        summary_dir = RUNS_DIR / RUN_NAME
        (summary_dir / "cross_paper_summary.json").write_text(
            json.dumps(all_totals, indent=2) + "\n"
        )

    print(f"\n{'='*60}")
    print(f"  Done. Results in runs/{RUN_NAME}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Comparison report for test corpus extraction quality.

This script generates a human-readable comparison table showing baseline vs current
extraction metrics for all papers in the test corpus. It highlights quality regressions
and provides actionable feedback.

Usage:
    python tests/corpus/compare.py
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add parent directory to path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))

from metrics import ExtractionMetrics  # type: ignore[import-not-found]


@dataclass
class ComparisonRow:
    """A single row in the comparison table."""

    slug: str
    baseline: ExtractionMetrics
    current: ExtractionMetrics

    def format_delta(self, baseline_val: int, current_val: int) -> str:
        """Format a metric delta as a string with sign and flag for regressions.

        Returns strings like:
            "11→14 (+3)" for improvement
            "0→0 (=)" for no change
            "102→66 (-35%)" for moderate regression
            "137→0 (!!!)" for severe regression (>35% loss or 100% loss)
        """
        if baseline_val == current_val:
            return f"{baseline_val}→{current_val} (=)"

        delta = current_val - baseline_val

        # Compute percentage if baseline is non-zero
        if baseline_val > 0:
            pct = (delta / baseline_val) * 100
            # Flag severe regressions
            if pct <= -100:
                # Complete loss
                return f"{baseline_val}→{current_val} (!!!)"
            elif pct <= -35:
                # >35% loss - flag as severe
                return f"{baseline_val}→{current_val} (!!!)"
            elif delta < 0:
                # Any other loss - show percentage
                return f"{baseline_val}→{current_val} ({pct:+.0f}%)"
            else:
                # Improvement - show absolute delta
                return f"{baseline_val}→{current_val} ({delta:+d})"
        else:
            # Baseline was zero - just show absolute delta
            return f"{baseline_val}→{current_val} ({delta:+d})"

    def format_chars(self, baseline_val: int, current_val: int) -> str:
        """Format character counts as compact strings (60k, 286k, etc.)."""
        baseline_k = baseline_val // 1000
        current_k = current_val // 1000

        if baseline_k == current_k:
            return f"{baseline_k}k→{current_k}k (=)"

        delta = current_val - baseline_val
        if baseline_val > 0:
            pct = (delta / baseline_val) * 100
            if abs(pct) < 1:
                # <1% change - treat as equal
                return f"{baseline_k}k→{current_k}k (~)"
            else:
                return f"{baseline_k}k→{current_k}k ({pct:+.1f}%)"
        else:
            return f"{baseline_k}k→{current_k}k"

    def has_regression(self) -> bool:
        """Check if this row has any severe regressions."""
        regression_threshold = -35.0  # -35% = severe loss

        # Check headings
        if self.baseline.heading_count > 0:
            heading_pct = (
                (self.current.heading_count - self.baseline.heading_count)
                / self.baseline.heading_count
                * 100
            )
            if heading_pct <= regression_threshold:
                return True

        # Check tables
        if self.baseline.table_row_count > 0:
            table_pct = (
                (self.current.table_row_count - self.baseline.table_row_count)
                / self.baseline.table_row_count
                * 100
            )
            if table_pct <= regression_threshold:
                return True

        # Check character count (content loss)
        if self.baseline.char_count > 0:
            char_pct = (
                (self.current.char_count - self.baseline.char_count)
                / self.baseline.char_count
                * 100
            )
            if char_pct <= -10.0:  # >10% content loss is concerning
                return True

        return False

    def describe_regressions(self) -> list[str]:
        """Generate human-readable descriptions of regressions."""
        regressions = []

        # Headings
        if self.baseline.heading_count > 0:
            heading_pct = (
                (self.current.heading_count - self.baseline.heading_count)
                / self.baseline.heading_count
                * 100
            )
            if heading_pct <= -35.0:
                regressions.append(
                    f"headings dropped from {self.baseline.heading_count} "
                    f"to {self.current.heading_count} ({heading_pct:.0f}%)"
                )

        # Tables
        if self.baseline.table_row_count > 0:
            table_pct = (
                (self.current.table_row_count - self.baseline.table_row_count)
                / self.baseline.table_row_count
                * 100
            )
            if table_pct <= -35.0:
                if self.current.table_row_count == 0:
                    regressions.append(
                        f"tables completely lost (was {self.baseline.table_row_count} rows)"
                    )
                else:
                    regressions.append(
                        f"tables dropped from {self.baseline.table_row_count} "
                        f"to {self.current.table_row_count} rows ({table_pct:.0f}%)"
                    )

        # Character count
        if self.baseline.char_count > 0:
            char_pct = (
                (self.current.char_count - self.baseline.char_count)
                / self.baseline.char_count
                * 100
            )
            if char_pct <= -10.0:
                regressions.append(
                    f"content shrank from {self.baseline.char_count // 1000}k "
                    f"to {self.current.char_count // 1000}k chars ({char_pct:.1f}%)"
                )

        return regressions


def load_papers() -> list[dict[str, Any]]:
    """Load paper registry from papers.jsonl."""
    papers = []
    papers_path = Path(__file__).parent / "papers.jsonl"

    with papers_path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                papers.append(json.loads(line))

    return papers


def load_metrics(slug: str, subdir: str) -> ExtractionMetrics | None:
    """Load metrics.json for a given paper slug and subdir (baseline/current).

    Returns None if file doesn't exist.
    """
    metrics_path = Path(__file__).parent / subdir / slug / "metrics.json"
    if not metrics_path.exists():
        return None

    with metrics_path.open() as f:
        data = json.load(f)

    return ExtractionMetrics.from_dict(data)


def generate_comparison_report() -> str:
    """Generate the full comparison report as a string."""
    papers = load_papers()
    rows = []

    # Load metrics for all papers
    for paper in papers:
        slug = paper["slug"]
        baseline = load_metrics(slug, "baseline")
        current = load_metrics(slug, "current")

        if baseline is None:
            print(f"Warning: No baseline metrics for {slug}", flush=True)
            continue
        if current is None:
            print(f"Warning: No current metrics for {slug}", flush=True)
            continue

        rows.append(ComparisonRow(slug=slug, baseline=baseline, current=current))

    if not rows:
        return "ERROR: No comparison data available. Run pytest with --run-corpus first."

    # Build the report
    lines = []
    lines.append("# Test Corpus Extraction Comparison")
    lines.append("")
    lines.append("Comparing baseline (fusion-tea) vs current (agentic-mbse) extractions.")
    lines.append("")

    # Table header
    lines.append(
        "| Document              | Headings      | Tables        | Chars         | Time    |"
    )
    lines.append(
        "|----------------------|---------------|---------------|---------------|---------|"
    )

    # Table rows
    for row in rows:
        # Pad slug to 20 chars
        slug_padded = row.slug.ljust(20)

        headings_str = row.format_delta(row.baseline.heading_count, row.current.heading_count)
        tables_str = row.format_delta(row.baseline.table_row_count, row.current.table_row_count)
        chars_str = row.format_chars(row.baseline.char_count, row.current.char_count)

        # Format time
        if row.current.extraction_time_seconds > 0:
            time_str = f"{row.current.extraction_time_seconds:.1f}s"
        else:
            time_str = "?"

        lines.append(
            f"| {slug_padded} | {headings_str:13} | {tables_str:13} | {chars_str:13} | {time_str:7} |"
        )

    # Regressions section
    regressions = []
    for row in rows:
        if row.has_regression():
            regressions.append((row.slug, row.describe_regressions()))

    if regressions:
        lines.append("")
        lines.append("## REGRESSIONS")
        lines.append("")
        for slug, issues in regressions:
            lines.append(f"**{slug}**:")
            for issue in issues:
                lines.append(f"  - {issue}")
            lines.append("")
    else:
        lines.append("")
        lines.append("✅ No quality regressions detected!")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point - generate and print comparison report."""
    report = generate_comparison_report()
    print(report)


if __name__ == "__main__":
    main()

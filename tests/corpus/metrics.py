"""Test corpus metrics computation.

This module provides metrics computation for extraction quality measurement.
Metrics are computed on whole-document markdown output and can be compared
across baseline and current extractions to detect quality regressions.
"""

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class ExtractionMetrics:
    """Quality metrics for a single document extraction."""

    char_count: int
    heading_count: int
    heading_by_level: dict[int, int]  # {2: 5, 3: 12, ...}
    table_row_count: int  # Lines matching |...|...|
    math_symbol_count: int
    figure_ref_count: int
    extraction_time_seconds: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExtractionMetrics":
        """Create from dictionary (for loading from JSON)."""
        return cls(**data)


def compute_metrics(markdown: str, elapsed: float = 0.0) -> ExtractionMetrics:
    """Compute extraction quality metrics from markdown text.

    This function counts various quality indicators in the markdown output:
    - Character count (total content volume)
    - Heading count and distribution by level (document structure)
    - Table row count (data extraction quality)
    - Math symbol count (equation preservation)
    - Figure reference count (figure extraction)

    Args:
        markdown: The markdown text to analyze
        elapsed: Extraction time in seconds (default 0.0 if unknown)

    Returns:
        ExtractionMetrics with all computed metrics
    """
    char_count = len(markdown)

    # Count headings by level
    heading_by_level: dict[int, int] = {}
    for line in markdown.split("\n"):
        if line.startswith("#"):
            # Count number of # symbols at start
            level = len(line) - len(line.lstrip("#"))
            if level > 0 and (level >= len(line) or line[level] in (" ", "\t")):
                heading_by_level[level] = heading_by_level.get(level, 0) + 1

    heading_count = sum(heading_by_level.values())

    # Count table rows (lines with at least two pipe separators)
    table_row_count = 0
    for line in markdown.split("\n"):
        # Count pipes in line
        if line.count("|") >= 2:
            table_row_count += 1

    # Count math symbols (Unicode mathematical operators and symbols)
    # Common ranges: U+2200-U+22FF (Mathematical Operators)
    #                U+2100-U+214F (Letterlike Symbols)
    #                U+27C0-U+27EF (Miscellaneous Mathematical Symbols-A)
    math_symbols = set()
    for char in markdown:
        code = ord(char)
        # Mathematical Operators
        if 0x2200 <= code <= 0x22FF:
            math_symbols.add(char)
        # Letterlike Symbols (ℂ, ℕ, ℝ, etc.)
        elif 0x2100 <= code <= 0x214F:
            math_symbols.add(char)
        # Miscellaneous Mathematical Symbols-A
        elif 0x27C0 <= code <= 0x27EF:
            math_symbols.add(char)
        # Greek letters (often used in equations)
        elif 0x0370 <= code <= 0x03FF:
            math_symbols.add(char)

    math_symbol_count = len(math_symbols)

    # Count figure references (case-insensitive)
    # Matches: "Figure 1", "Fig. 2", "figure 3", etc.
    figure_ref_pattern = re.compile(r"\b(?:figure|fig\.?)\s+\d+", re.IGNORECASE)
    figure_ref_count = len(figure_ref_pattern.findall(markdown))

    return ExtractionMetrics(
        char_count=char_count,
        heading_count=heading_count,
        heading_by_level=heading_by_level,
        table_row_count=table_row_count,
        math_symbol_count=math_symbol_count,
        figure_ref_count=figure_ref_count,
        extraction_time_seconds=elapsed,
    )


def compare_metrics(baseline: ExtractionMetrics, current: ExtractionMetrics) -> dict[str, Any]:
    """Compare two sets of metrics and compute deltas.

    This function computes absolute and percentage differences between
    baseline and current metrics. Negative deltas indicate regressions
    (quality loss), positive deltas indicate improvements.

    Args:
        baseline: Baseline metrics (ground truth)
        current: Current metrics (to compare against baseline)

    Returns:
        Dictionary with deltas and regression flags:
        {
            "char_count_delta": int,
            "char_count_pct": float,
            "heading_count_delta": int,
            "heading_count_pct": float,
            "table_row_count_delta": int,
            "table_row_count_pct": float,
            "math_symbol_count_delta": int,
            "math_symbol_count_pct": float,
            "figure_ref_count_delta": int,
            "figure_ref_count_pct": float,
            "time_delta": float,
            "time_pct": float,
            "has_regression": bool,  # True if any metric lost >10%
        }
    """
    result: dict[str, Any] = {}

    # Helper to compute delta and percentage
    def compute_delta(name: str, baseline_val: int | float, current_val: int | float):
        delta = current_val - baseline_val
        pct = (delta / baseline_val * 100) if baseline_val > 0 else 0.0
        result[f"{name}_delta"] = delta
        result[f"{name}_pct"] = pct

    compute_delta("char_count", baseline.char_count, current.char_count)
    compute_delta("heading_count", baseline.heading_count, current.heading_count)
    compute_delta("table_row_count", baseline.table_row_count, current.table_row_count)
    compute_delta("math_symbol_count", baseline.math_symbol_count, current.math_symbol_count)
    compute_delta("figure_ref_count", baseline.figure_ref_count, current.figure_ref_count)
    compute_delta("time", baseline.extraction_time_seconds, current.extraction_time_seconds)

    # Detect regressions (>10% loss on any key metric)
    regression_threshold = -10.0  # -10% = loss
    has_regression = (
        result["char_count_pct"] < regression_threshold
        or result["heading_count_pct"] < regression_threshold
        or result["table_row_count_pct"] < regression_threshold
    )
    result["has_regression"] = has_regression

    return result


if __name__ == "__main__":
    # Test metrics computation on a sample markdown file
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python metrics.py <markdown_file>")
        sys.exit(1)

    markdown_path = Path(sys.argv[1])
    if not markdown_path.exists():
        print(f"Error: File not found: {markdown_path}")
        sys.exit(1)

    markdown = markdown_path.read_text()
    metrics = compute_metrics(markdown)

    print(json.dumps(metrics.to_dict(), indent=2))

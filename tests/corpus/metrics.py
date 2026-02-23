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


@dataclass
class GroundTruth:
    """Human-verified ground truth for a corpus document."""

    slug: str
    pages: int
    headings: int | None
    heading_levels: dict[int, int] | None
    data_tables: int | None
    table_data_rows: int | None
    expected_metric_table_rows: int | None
    display_equations: int | None
    has_inline_math: bool | None
    notes: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GroundTruth":
        """Create from dictionary (for loading from JSONL)."""
        # Convert string keys to int for heading_levels
        hl = data.get("heading_levels")
        if hl is not None:
            hl = {int(k): v for k, v in hl.items()}
        return cls(
            slug=data["slug"],
            pages=data["pages"],
            headings=data.get("headings"),
            heading_levels=hl,
            data_tables=data.get("data_tables"),
            table_data_rows=data.get("table_data_rows"),
            expected_metric_table_rows=data.get("expected_metric_table_rows"),
            display_equations=data.get("display_equations"),
            has_inline_math=data.get("has_inline_math"),
            notes=data.get("notes", ""),
        )


def load_ground_truth(path: Path | None = None) -> dict[str, GroundTruth]:
    """Load ground truth from JSONL file.

    Args:
        path: Path to ground_truth.jsonl. Defaults to tests/corpus/ground_truth.jsonl.

    Returns:
        Dictionary mapping slug to GroundTruth.
    """
    import json

    if path is None:
        path = Path(__file__).parent / "ground_truth.jsonl"
    result = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                data = json.loads(line)
                gt = GroundTruth.from_dict(data)
                result[gt.slug] = gt
    return result


@dataclass
class AccuracyScore:
    """Accuracy score for one method on one dimension against ground truth."""

    detected: int
    ground_truth: int
    delta: int  # detected - ground_truth (positive = over-detection)
    error_pct: float  # abs(delta) / ground_truth * 100
    category: str  # "exact", "close" (<=10%), "over", "under", "miss" (0 detected)


def score_against_ground_truth(
    metrics: ExtractionMetrics, gt: GroundTruth
) -> dict[str, AccuracyScore | None]:
    """Score extraction metrics against human-verified ground truth.

    Computes accuracy scores for headings and table rows by comparing
    the tool's metric output against the expected values from ground truth.

    Args:
        metrics: Extraction metrics from a tool run.
        gt: Human-verified ground truth for the same document.

    Returns:
        Dictionary with keys "headings" and "table_rows", each mapping to
        an AccuracyScore or None if ground truth is not available for that dimension.
    """
    result: dict[str, AccuracyScore | None] = {"headings": None, "table_rows": None}

    if gt.headings is not None:
        delta = metrics.heading_count - gt.headings
        error_pct = (abs(delta) / gt.headings * 100) if gt.headings > 0 else (
            0.0 if metrics.heading_count == 0 else 100.0
        )
        if delta == 0:
            cat = "exact"
        elif error_pct <= 10:
            cat = "close"
        elif metrics.heading_count == 0 and gt.headings > 0:
            cat = "miss"
        elif delta > 0:
            cat = "over"
        else:
            cat = "under"
        result["headings"] = AccuracyScore(
            detected=metrics.heading_count,
            ground_truth=gt.headings,
            delta=delta,
            error_pct=error_pct,
            category=cat,
        )

    if gt.expected_metric_table_rows is not None:
        expected = gt.expected_metric_table_rows
        delta = metrics.table_row_count - expected
        error_pct = (abs(delta) / expected * 100) if expected > 0 else (
            0.0 if metrics.table_row_count == 0 else 100.0
        )
        if delta == 0:
            cat = "exact"
        elif error_pct <= 10:
            cat = "close"
        elif metrics.table_row_count == 0 and expected > 0:
            cat = "miss"
        elif delta > 0:
            cat = "over"
        else:
            cat = "under"
        result["table_rows"] = AccuracyScore(
            detected=metrics.table_row_count,
            ground_truth=expected,
            delta=delta,
            error_pct=error_pct,
            category=cat,
        )

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

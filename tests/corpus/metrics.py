"""Test corpus metrics computation.

Canonical implementation lives in agentic_mbse.extraction.metrics.
This module re-exports for backward compatibility with experiment scripts.
"""

from pathlib import Path
from typing import Any

from agentic_mbse.extraction.metrics import (
    AccuracyScore,  # noqa: F401 — intentional re-export
    ExtractionMetrics,
    GroundTruth,
    compute_metrics,
    score_against_ground_truth,  # noqa: F401 — intentional re-export
)
from agentic_mbse.extraction.metrics import (
    load_ground_truth as _load_ground_truth,
)

# Convenience wrapper: default path for corpus ground truth
_DEFAULT_GT_PATH = Path(__file__).parent / "ground_truth.jsonl"


def load_ground_truth(path: Path | None = None) -> dict[str, GroundTruth]:
    """Load ground truth with default path to corpus JSONL."""
    return _load_ground_truth(path or _DEFAULT_GT_PATH)


def compare_metrics(baseline: ExtractionMetrics, current: ExtractionMetrics) -> dict[str, Any]:
    """Compare two sets of metrics and compute deltas.

    NOTE: Not promoted to production metrics.py. Kept here for experiment
    scripts. If needed in production later, copy the implementation from
    the git history of this file (pre-shim conversion).

    Args:
        baseline: Baseline metrics (ground truth)
        current: Current metrics (to compare against baseline)

    Returns:
        Dictionary with deltas and regression flags.
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

"""Integration tests for sysml_checks refactoring.

These tests compare Level 2/3 output against pre-refactor baseline
to ensure no regression in validation behavior.
"""

import re
import subprocess
from pathlib import Path

MODELS_PATH = Path("tests/fixtures/sample_models")
BASELINE_DIR = Path("tests/test_validation/baselines")


def _run_check(module: str) -> str:
    """Run a validation module and return its output."""
    result = subprocess.run(
        ["python", "-m", f"agentic_mbse.validation.{module}", str(MODELS_PATH)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )
    return result.stdout + result.stderr


def _extract_metrics(output: str) -> dict:
    """Extract key metrics from check output.

    Returns a dict with:
    - issue_count: total issues found
    - key_patterns: list of important patterns detected
    - success: whether check passed (✅) or failed (❌)
    """
    metrics = {
        "issue_count": 0,
        "key_patterns": [],
        "success": "✅" in output,
    }

    # Extract issue count
    issue_match = re.search(r"Issues found: (\d+)", output)
    if issue_match:
        metrics["issue_count"] = int(issue_match.group(1))

    # Extract circular dependencies count
    circular_match = re.search(r"Circular dependencies: (\d+)", output)
    if circular_match:
        metrics["circular_deps"] = int(circular_match.group(1))

    # Extract specific metric values
    for pattern in [
        r"Unused definitions: (\d+)",
        r"Unbound inputs: (\d+)",
        r"Undefined bindings: (\d+)",
        r"Placeholder bindings: (\d+)",
        r"Orphaned elements: (\d+)",
    ]:
        match = re.search(pattern, output)
        if match:
            key = pattern.split(":")[0].replace(r"\d+", "").strip()
            metrics[key] = int(match.group(1))

    # Extract issue types
    if "Unused calc def:" in output:
        metrics["key_patterns"].append("unused_calc_def")
    if "Unbound input" in output:
        metrics["key_patterns"].append("unbound_input")
    if "Circular dependency" in output:
        metrics["key_patterns"].append("circular_dependency")
    if "WARN:" in output:
        metrics["key_patterns"].append("warnings")

    return metrics


def test_level2_output_matches_baseline():
    """Level 2 structural checks produce same output as baseline.

    Input: Run Level 2 checks on models/
    Output: Issue counts and key patterns match pre-refactor baseline
    """
    baseline_path = BASELINE_DIR / "level2_baseline.txt"
    if not baseline_path.exists():
        raise FileNotFoundError(
            f"Baseline not found: {baseline_path}. Run Phase 1 setup to capture baselines first."
        )

    baseline = baseline_path.read_text()
    current = _run_check("level2_structure")

    baseline_metrics = _extract_metrics(baseline)
    current_metrics = _extract_metrics(current)

    # Compare issue count
    assert current_metrics["issue_count"] == baseline_metrics["issue_count"], (
        f"Issue count changed: baseline={baseline_metrics['issue_count']}, "
        f"current={current_metrics['issue_count']}"
    )

    # Compare success status
    assert current_metrics["success"] == baseline_metrics["success"], (
        f"Success status changed: baseline={baseline_metrics['success']}, "
        f"current={current_metrics['success']}"
    )

    # Compare key patterns detected
    assert set(current_metrics["key_patterns"]) == set(baseline_metrics["key_patterns"]), (
        f"Key patterns changed: baseline={baseline_metrics['key_patterns']}, "
        f"current={current_metrics['key_patterns']}"
    )


def test_level3_output_matches_baseline():
    """Level 3 dataflow checks produce same output as baseline.

    Input: Run Level 3 checks on models/
    Output: Cycle detection matches pre-refactor baseline
    """
    baseline_path = BASELINE_DIR / "level3_baseline.txt"
    if not baseline_path.exists():
        raise FileNotFoundError(
            f"Baseline not found: {baseline_path}. Run Phase 1 setup to capture baselines first."
        )

    baseline = baseline_path.read_text()
    current = _run_check("level3_dataflow")

    baseline_metrics = _extract_metrics(baseline)
    current_metrics = _extract_metrics(current)

    # Compare circular dependency count
    assert current_metrics.get("circular_deps", 0) == baseline_metrics.get("circular_deps", 0), (
        f"Circular dependency count changed: "
        f"baseline={baseline_metrics.get('circular_deps', 0)}, "
        f"current={current_metrics.get('circular_deps', 0)}"
    )

    # Compare success status
    assert current_metrics["success"] == baseline_metrics["success"], (
        f"Success status changed: baseline={baseline_metrics['success']}, "
        f"current={current_metrics['success']}"
    )


def test_baseline_files_exist():
    """Verify baseline files exist and contain expected content."""
    level2_baseline = BASELINE_DIR / "level2_baseline.txt"
    level3_baseline = BASELINE_DIR / "level3_baseline.txt"

    assert level2_baseline.exists(), "Level 2 baseline missing"
    assert level3_baseline.exists(), "Level 3 baseline missing"

    level2_content = level2_baseline.read_text()
    level3_content = level3_baseline.read_text()

    # Verify baselines contain expected headers
    assert "Level 2: Structural Completeness" in level2_content
    assert "Level 3: Dataflow Integrity" in level3_content

    # Verify baselines captured actual results (not empty)
    assert "Found" in level2_content
    assert "Found" in level3_content

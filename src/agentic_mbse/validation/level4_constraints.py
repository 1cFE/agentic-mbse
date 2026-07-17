#!/usr/bin/env python3
"""
Level 4: Constraint Coverage

Reports metrics on constraint coverage.
Does NOT evaluate constraint values (that's handled by syside/TEAx).
"""

import sys
from typing import Any

from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts
from agentic_mbse.sysml.executable_profile import evaluate_profile
from agentic_mbse.sysml.syside_adapter import (
    EXCLUDED_CONSTRAINT_TYPES,
    SysideAdapter,
)

try:
    from .common import (
        EXIT_FAILURE,
        EXIT_SUCCESS,
        QualityCheckResult,
        discover_sysml_files,
        load_sysml_model,
        print_header,
        print_result,
    )
except ImportError:
    # Handle direct execution
    from common import (
        EXIT_FAILURE,
        EXIT_SUCCESS,
        QualityCheckResult,
        discover_sysml_files,
        load_sysml_model,
        print_header,
        print_result,
    )


def eligibility_coverage_metrics(model: Any) -> dict:
    """
    CONSTRAINT-EXEC Item 3: executable-assertion eligibility, replacing the old 0%
    attribute-coverage placeholder (`check_constraint_coverage`, which never parsed a predicate).

    Runs the executable profile over the model's constraint facts and reports how many asserted
    constraints (inline/definition-typed) are admitted, blocked, or unassessed (satisfy /
    require-assume / plain). The denominator is executable asserts (admit + block) over total
    asserts, per spec's Open Questions — unassessed is reported as its own line, not folded into
    the percentage.

    The eligibility block carries its own denominator ("Constraint usages assessed
    (incl. satisfy)") because the extraction sweep classifies every ConstraintUsage,
    including SatisfyRequirementUsage, while the legacy "Total constraints" count
    excludes the requirement subtree (Item 4 semantics, EXCLUDED_CONSTRAINT_TYPES).
    Eligible + Ineligible + Unassessed always sums to this denominator, not to
    "Total constraints".

    Returns:
        Metrics dict: assessed denominator, eligibility admit/block/unassessed counts,
        and the admit-rate percentage.
    """
    facts = extract_constraint_facts(model)
    result = evaluate_profile(facts)

    asserted = result.admitted_count + result.blocked_count
    admit_rate = (result.admitted_count / asserted * 100) if asserted > 0 else 100

    return {
        "Constraint usages assessed (incl. satisfy)": len(result.decisions),
        "Eligible (admitted)": result.admitted_count,
        "Ineligible (blocked)": result.blocked_count,
        "Unassessed (satisfy/require/plain)": result.unassessed_count,
        "Eligibility rate": f"{admit_rate:.1f}%",
    }


def analyze_constraints(models_path: str) -> QualityCheckResult:
    """
    Analyze constraint coverage

    Returns metrics, does NOT evaluate constraint values
    """
    print_header("Constraint Coverage", 4)

    # Discover and load model
    files = discover_sysml_files(models_path)
    if not files:
        return QualityCheckResult(
            level=4,
            level_name="Constraint Coverage",
            success=True,
            warnings=["No SysML files found"],
        )

    print(f"Found {len(files)} SysML files")

    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=4,
            level_name="Constraint Coverage",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # Count constraints — row 6 (Item 4): sweep ConstraintUsage subtypes so
    # `assert` is counted, excluding requirement-side usages (mirror row 1).
    constraints = list(
        SysideAdapter.elements_of_type(
            model,
            "ConstraintUsage",
            include_subtypes=True,
            exclude=EXCLUDED_CONSTRAINT_TYPES,
        )
    )
    total_constraints = len(constraints)

    # Count constraint definitions
    constraint_defs = list(SysideAdapter.elements_of_type(model, "ConstraintDefinition"))

    # Merge metrics
    metrics = {
        "Total constraints": total_constraints,
        "ConstraintUsage": total_constraints,
        "ConstraintDefinition": len(constraint_defs),
    }
    metrics.update(eligibility_coverage_metrics(model))

    return QualityCheckResult(
        level=4,
        level_name="Constraint Coverage",
        success=True,  # Informational only
        metrics=metrics,
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Level 4: Constraint Satisfaction")
    parser.add_argument("path", nargs="?", default="models", help="Path to models directory")
    args = parser.parse_args()

    result = analyze_constraints(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

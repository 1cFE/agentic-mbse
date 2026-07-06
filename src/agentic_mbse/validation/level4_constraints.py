#!/usr/bin/env python3
"""
Level 4: Constraint Coverage

Reports metrics on constraint coverage.
Does NOT evaluate constraint values (that's handled by syside/TEAx).
"""

import sys
from typing import Any

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
        get_element_location,
        get_qualified_name,
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
        get_element_location,
        get_qualified_name,
        load_sysml_model,
        print_header,
        print_result,
    )


def check_constraint_coverage(model: Any) -> tuple[list[str], dict]:
    """
    Calculate constraint coverage: which attributes are constrained.

    Returns:
        (unconstrained_attributes, metrics) tuple
    """
    # Get all attributes
    attributes = list(SysideAdapter.elements_of_type(model, "AttributeUsage"))

    # Get all constraints (needed for constraint coverage calculation)
    _constraints = list(SysideAdapter.elements_of_type(model, "ConstraintUsage"))

    # Build set of attributes referenced in constraints
    # Placeholder: This would need to parse constraint expressions
    # to find which attributes are referenced
    # For now, we'll report 0% coverage as a starting point
    constrained_attrs = set()

    # Find unconstrained attributes
    unconstrained = []
    for attr in attributes:
        attr_name = get_qualified_name(attr)
        if attr_name not in constrained_attrs:
            location = get_element_location(attr)
            unconstrained.append(f"{attr_name} at {location}")

    total = len(attributes)
    constrained_count = len(constrained_attrs)
    coverage_pct = (constrained_count / total * 100) if total > 0 else 100

    metrics = {
        "Total attributes": total,
        "Constrained": constrained_count,
        "Unconstrained": len(unconstrained),
        "Coverage": f"{coverage_pct:.1f}%",
    }

    return unconstrained, metrics


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

    # Constraint coverage analysis (absorbed from old L5)
    unconstrained, coverage_metrics = check_constraint_coverage(model)

    # Build warnings from unconstrained attributes
    warnings = []
    for attr in unconstrained[:10]:
        warnings.append(f"Unconstrained attribute: {attr}")
    if len(unconstrained) > 10:
        warnings.append(f"... and {len(unconstrained) - 10} more")

    # Merge metrics
    metrics = {
        "Total constraints": total_constraints,
        "ConstraintUsage": total_constraints,
        "ConstraintDefinition": len(constraint_defs),
    }
    metrics.update(coverage_metrics)

    return QualityCheckResult(
        level=4,
        level_name="Constraint Coverage",
        success=True,  # Informational only
        warnings=warnings,
        metrics=metrics,
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Level 4: Constraint Satisfaction")
    parser.add_argument(
        "path", nargs="?", default="models", help="Path to models directory"
    )
    args = parser.parse_args()

    result = analyze_constraints(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

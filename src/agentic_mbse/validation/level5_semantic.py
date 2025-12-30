#!/usr/bin/env python3
"""
Level 5: Semantic Consistency

Analyzes coverage: which attributes are constrained, which aren't.
Does NOT validate constraint values (models contain knowledge, scripts analyze structure).
"""

import sys
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

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


def check_unit_consistency(model: Any) -> list[str]:
    """
    Check that units flow correctly through calculations

    Returns:
        List of unit inconsistency issues
    """
    issues = []

    # Placeholder - needs full implementation
    # Would need to:
    # 1. Get all calculations
    # 2. Extract input/output attributes with units
    # 3. Check unit consistency via dimensional analysis
    # This requires parsing attribute units from SysML which is complex

    return issues


def check_constraint_coverage(model: Any) -> tuple[list[str], dict]:
    """
    Calculate constraint coverage: which attributes are constrained

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

    # Could enhance by:
    # 1. Traversing constraint.owned_elements
    # 2. Finding FeatureReferenceExpression elements
    # 3. Extracting attribute references
    # This is complex and requires deep SysMLv2 AST understanding

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


def validate_semantic(models_path: str) -> QualityCheckResult:
    """Validate semantic consistency"""
    print_header("Semantic Consistency", 5)

    files = discover_sysml_files(models_path)
    if not files:
        return QualityCheckResult(
            level=5,
            level_name="Semantic Consistency",
            success=True,
            warnings=["No SysML files found"],
        )

    print(f"Found {len(files)} SysML files")

    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=5,
            level_name="Semantic Consistency",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # Run checks
    unit_issues = check_unit_consistency(model)
    unconstrained, coverage_metrics = check_constraint_coverage(model)

    # Show first 10 unconstrained attributes as warnings
    warnings = unconstrained[:10]
    if len(unconstrained) > 10:
        warnings.append(
            f"... and {len(unconstrained) - 10} more unconstrained attributes"
        )

    return QualityCheckResult(
        level=5,
        level_name="Semantic Consistency",
        success=len(unit_issues) == 0,  # Pass if no unit issues
        issues=unit_issues,
        warnings=warnings,
        metrics=coverage_metrics,
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Level 5: Semantic Consistency")
    parser.add_argument(
        "path", nargs="?", default="models", help="Path to models directory"
    )
    args = parser.parse_args()

    result = validate_semantic(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

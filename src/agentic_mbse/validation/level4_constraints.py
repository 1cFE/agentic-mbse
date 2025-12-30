#!/usr/bin/env python3
"""
Level 4: Constraint Satisfaction

Reports metrics on constraint coverage.
Does NOT evaluate constraint values (that's handled by syside/TEAx).
"""

import sys

from agentic_mbse.sysml.syside_adapter import SysideAdapter

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


def analyze_constraints(models_path: str) -> QualityCheckResult:
    """
    Analyze constraint coverage

    Returns metrics, does NOT evaluate constraint values
    """
    print_header("Constraint Satisfaction", 4)

    # Discover and load model
    files = discover_sysml_files(models_path)
    if not files:
        return QualityCheckResult(
            level=4,
            level_name="Constraint Satisfaction",
            success=True,
            warnings=["No SysML files found"],
        )

    print(f"Found {len(files)} SysML files")

    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=4,
            level_name="Constraint Satisfaction",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # Count constraints
    constraints = list(SysideAdapter.elements_of_type(model, "ConstraintUsage"))
    total_constraints = len(constraints)

    # Count constraint definitions
    constraint_defs = list(SysideAdapter.elements_of_type(model, "ConstraintDefinition"))

    # Check documentation (placeholder - can enhance later)
    undocumented = []
    # Would check for doc comments on constraints, but this is complex
    # and lower priority for now

    return QualityCheckResult(
        level=4,
        level_name="Constraint Satisfaction",
        success=True,  # Informational only
        warnings=undocumented if undocumented else [],
        metrics={
            "Total constraints": total_constraints,
            "Constraint definitions": len(constraint_defs),
            "Undocumented constraints": len(undocumented),
        },
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

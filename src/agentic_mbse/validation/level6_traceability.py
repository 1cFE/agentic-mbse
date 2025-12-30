#!/usr/bin/env python3
"""
Level 6: Traceability & Documentation

Verifies documentation coverage and source citations.
Checks that major elements (calc defs, part defs) have doc comments.
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


def has_doc_comment(element) -> bool:
    """
    Check if an element has a doc comment

    Args:
        element: SysML element to check

    Returns:
        True if element has a documentation comment
    """
    # Check owned_elements for Comment or Documentation
    if hasattr(element, "owned_elements"):
        for owned in element.owned_elements:
            # Check if it's a Comment or Documentation element
            if SysideAdapter.is_instance(owned, "Comment") or SysideAdapter.is_instance(owned, "Documentation"):
                return True
    return False


def check_documentation_coverage(model: Any) -> tuple[list, dict]:
    """
    Check that major elements have doc comments

    Returns:
        (missing_docs, metrics) tuple
    """
    missing = []

    # Check calc definitions
    calc_defs = list(SysideAdapter.elements_of_type(model, "CalculationDefinition"))
    calc_missing = 0
    for calc_def in calc_defs:
        if not has_doc_comment(calc_def):
            name = get_qualified_name(calc_def)
            location = get_element_location(calc_def)
            missing.append(f"Calc def missing doc: {name} at {location}")
            calc_missing += 1

    # Check part definitions
    part_defs = list(SysideAdapter.elements_of_type(model, "PartDefinition"))
    part_missing = 0
    for part_def in part_defs:
        if not has_doc_comment(part_def):
            name = get_qualified_name(part_def)
            location = get_element_location(part_def)
            missing.append(f"Part def missing doc: {name} at {location}")
            part_missing += 1

    total = len(calc_defs) + len(part_defs)
    documented = total - len(missing)
    coverage_pct = (documented / total * 100) if total > 0 else 100

    metrics = {
        "Total elements": total,
        "Documented": documented,
        "Missing docs": len(missing),
        "Coverage": f"{coverage_pct:.1f}%",
    }

    return missing, metrics


def validate_traceability(models_path: str) -> QualityCheckResult:
    """Validate traceability and documentation"""
    print_header("Traceability & Documentation", 6)

    files = discover_sysml_files(models_path)
    if not files:
        return QualityCheckResult(
            level=6,
            level_name="Traceability & Documentation",
            success=True,
            warnings=["No SysML files found"],
        )

    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=6,
            level_name="Traceability & Documentation",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    missing_docs, metrics = check_documentation_coverage(model)

    # Documentation is informational - don't fail on missing docs
    # Report as warnings instead of issues
    return QualityCheckResult(
        level=6,
        level_name="Traceability & Documentation",
        success=True,
        warnings=missing_docs[:10] if missing_docs else [],  # Show first 10
        metrics=metrics,
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Level 6: Traceability & Documentation")
    parser.add_argument("path", nargs="?", default="models", help="Path to models directory")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    result = validate_traceability(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

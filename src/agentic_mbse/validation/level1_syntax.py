#!/usr/bin/env python3
"""
Level 1: Syntax Validation

Validates that all SysML models parse without syntax errors using syside.

Reuses and extends scripts/test_sysml_parsing.py
"""

import sys

from agentic_mbse.sysml.syside_adapter import DiagnosticSeverity, SysideAdapter

# Handle both package import and direct script execution
try:
    from .common import (
        EXIT_FAILURE,
        EXIT_SUCCESS,
        QualityCheckResult,
        discover_sysml_files,
        print_header,
        print_result,
    )
except ImportError:
    from common import (
        EXIT_FAILURE,
        EXIT_SUCCESS,
        QualityCheckResult,
        discover_sysml_files,
        print_header,
        print_result,
    )


def validate_syntax(models_path: str) -> QualityCheckResult:
    """
    Validate syntax of all SysML files

    Args:
        models_path: Path to models directory

    Returns:
        QualityCheckResult with diagnostics
    """
    print_header("Syntax Validation", 1)

    # Discover files
    files = discover_sysml_files(models_path)
    print(f"Found {len(files)} SysML files")

    if not files:
        return QualityCheckResult(
            level=1,
            level_name="Syntax Validation",
            success=True,
            warnings=["No SysML files found"],
        )

    # Load model using syside
    try:
        model, diagnostics = SysideAdapter.load_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=1,
            level_name="Syntax Validation",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # Extract errors from diagnostics
    # Level 1 is ONLY about syntax (parser errors), not semantic validation
    issues = []
    warnings = []

    # Only check parser diagnostics for syntax errors
    for diag in diagnostics.parser:
        msg = f"{diag.filename}:{diag.line}:{diag.col} - {diag.message}"

        if diag.severity == DiagnosticSeverity.Error:
            issues.append(msg)
        elif diag.severity == DiagnosticSeverity.Warning:
            warnings.append(msg)

    success = len(issues) == 0

    return QualityCheckResult(
        level=1,
        level_name="Syntax Validation",
        success=success,
        issues=issues,
        warnings=warnings,
        metrics={
            "Files checked": len(files),
            "Errors": len(issues),
            "Warnings": len(warnings),
        },
    )


def main() -> int:
    """Entry point for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Level 1: Syntax Validation")
    parser.add_argument(
        "path", nargs="?", default="models", help="Path to models directory"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    result = validate_syntax(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Level 3: Dataflow Integrity

Validates dependency structure and detects circular imports.
"""

import sys
from collections import defaultdict
from typing import Any

from agentic_mbse.sysml.graph import detect_cycles
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


def build_dependency_graph(model: Any) -> dict[str, list[str]]:
    """
    Build package import dependency graph

    Returns:
        Dict mapping package name to list of imported packages
    """
    graph = defaultdict(list)

    # Get all imports in the model
    for element in SysideAdapter.elements_of_type(model, "Import"):
        try:
            # Get the document/package this import is in
            doc = element.document
            if not doc or not hasattr(doc, "url"):
                continue

            doc_name = str(doc.url)

            # Try to get the imported namespace
            if hasattr(element, "imported_namespace") and element.imported_namespace:  # type: ignore
                target = element.imported_namespace  # type: ignore
                # Get qualified name of imported element
                if hasattr(target, "qualified_name"):
                    imported_name = str(target.qualified_name)
                    # Extract package part (before ::)
                    if "::" in imported_name:
                        imported_pkg = imported_name.split("::")[0]
                    else:
                        imported_pkg = imported_name

                    # Skip standard library imports
                    if imported_pkg and imported_pkg not in [
                        "ScalarValues",
                        "SI",
                        "ISQ",
                    ]:
                        graph[doc_name].append(imported_pkg)
        except Exception:
            # Skip imports we can't resolve
            pass

    return dict(graph)


# NOTE: detect_cycles is now imported from agentic_mbse.sysml.graph
# Old local implementation removed as part of Effort 4 refactoring


def validate_dataflow(models_path: str) -> QualityCheckResult:
    """Validate dataflow integrity"""
    print_header("Dataflow Integrity", 3)

    files = discover_sysml_files(models_path)
    if not files:
        return QualityCheckResult(
            level=3,
            level_name="Dataflow Integrity",
            success=True,
            warnings=["No SysML files found"],
        )

    print(f"Found {len(files)} SysML files")

    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=3,
            level_name="Dataflow Integrity",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # Build dependency graph and detect cycles
    graph = build_dependency_graph(model)
    cycle_paths = detect_cycles(graph)  # Returns List[List[str]]

    # Format cycles for display (agentic_mbse.sysml returns raw paths)
    issues = [f"Circular dependency: {' → '.join(cycle)}" for cycle in cycle_paths]
    success = len(issues) == 0

    return QualityCheckResult(
        level=3,
        level_name="Dataflow Integrity",
        success=success,
        issues=issues,
        metrics={
            "Documents analyzed": len(graph),
            "Circular dependencies": len(cycle_paths),
        },
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Level 3: Dataflow Integrity")
    parser.add_argument("path", nargs="?", default="models", help="Path to models directory")
    args = parser.parse_args()

    result = validate_dataflow(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

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

    # Get all imports in the model. Row 5 (Item 4): `Import` is abstract — every
    # import is a concrete MembershipImport or NamespaceImport — so an exact-type
    # query matched nothing and the graph was always empty. Sweep subtypes.
    for element in SysideAdapter.elements_of_type(
        model, "Import", include_subtypes=True
    ):
        try:
            # Source node = the package that OWNS this import. Keying the graph by
            # the importing package's qualified name (not the document URL) is what
            # makes cycle detection actually work: an edge PkgA -> PkgB is only a
            # back-edge to a PkgB -> PkgA edge if both endpoints live in the same
            # (package) namespace. With URL keys and package-name values the two
            # never matched, so no cycle could ever be found (row 5).
            owner_ns = getattr(element, "import_owning_namespace", None)
            source_pkg = getattr(owner_ns, "qualified_name", None)
            if not source_pkg:
                continue
            source_pkg = str(source_pkg).split("::")[0]

            # Resolve the imported target's qualified name. NamespaceImport
            # (`import Pkg::*`) exposes imported_namespace; MembershipImport
            # (`import Pkg::Item`) exposes imported_membership.member_element.
            # The old guard checked only imported_namespace, so it silently
            # skipped every MembershipImport (row 5 secondary bug).
            target = getattr(element, "imported_namespace", None)
            if target is None:
                membership = getattr(element, "imported_membership", None)
                target = getattr(membership, "member_element", None)
            if target is None or not hasattr(target, "qualified_name"):
                continue

            imported_name = str(target.qualified_name)
            # Extract package part (before ::)
            if "::" in imported_name:
                imported_pkg = imported_name.split("::")[0]
            else:
                imported_pkg = imported_name

            # Skip standard library imports and self-imports.
            if (
                imported_pkg
                and imported_pkg != source_pkg
                and imported_pkg not in ["ScalarValues", "SI", "ISQ"]
            ):
                graph[source_pkg].append(imported_pkg)
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
    parser.add_argument(
        "path", nargs="?", default="models", help="Path to models directory"
    )
    args = parser.parse_args()

    result = validate_dataflow(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

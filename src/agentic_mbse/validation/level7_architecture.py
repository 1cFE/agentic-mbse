#!/usr/bin/env python3
"""
Level 7: Architectural Integrity

Validates system architecture using optional manifest.
If manifest missing, warns but passes.
"""

import sys
from pathlib import Path
from typing import Any

import yaml

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
    from common import (
        EXIT_FAILURE,
        EXIT_SUCCESS,
        QualityCheckResult,
        discover_sysml_files,
        load_sysml_model,
        print_header,
        print_result,
    )


def load_manifest(design_path: Path) -> dict | None:
    """
    Load design manifest if exists

    Args:
        design_path: Path to design directory (e.g., models/designs/design_model/)

    Returns:
        Manifest dict or None if not found
    """
    manifest_path = design_path / "manifest.yaml"

    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load manifest: {e}")
        return None


def check_subsystem_composition(model: Any, manifest: dict) -> list[str]:
    """
    Check that expected subsystems are present in system.sysml

    Args:
        model: Loaded SysML model
        manifest: Design manifest with expected_subsystems

    Returns:
        List of missing subsystems
    """
    expected = manifest.get("expected_subsystems", [])
    missing = []

    # Find all part usages in the model
    part_usages = list(SysideAdapter.elements_of_type(model, "PartUsage"))

    # Get names of all parts
    part_names = set()
    for part in part_usages:
        if hasattr(part, "name") and part.name:
            part_names.add(part.name)

    # Check if each expected subsystem exists
    for subsystem in expected:
        # Check if any part name matches the expected subsystem name
        if subsystem not in part_names:
            missing.append(subsystem)

    return missing


def validate_architecture(models_path: str) -> QualityCheckResult:
    """Validate architectural integrity"""
    print_header("Architectural Integrity", 7)

    # Try to find manifest in designs directories
    designs_path = Path(models_path) / "designs"

    if not designs_path.exists():
        return QualityCheckResult(
            level=7,
            level_name="Architectural Integrity",
            success=True,
            warnings=["No designs/ directory found"],
        )

    # Look for manifests in design directories
    manifests_found = list(designs_path.glob("*/manifest.yaml"))

    if not manifests_found:
        return QualityCheckResult(
            level=7,
            level_name="Architectural Integrity",
            success=True,
            warnings=["No manifests found (optional)"],
        )

    # Load model
    files = discover_sysml_files(models_path)
    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=7,
            level_name="Architectural Integrity",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # Check each design with manifest
    issues = []
    for manifest_path in manifests_found:
        manifest = load_manifest(manifest_path.parent)
        if manifest:
            missing = check_subsystem_composition(model, manifest)
            for subsystem in missing:
                issues.append(f"Missing subsystem '{subsystem}' in {manifest_path.parent.name}")

    return QualityCheckResult(
        level=7,
        level_name="Architectural Integrity",
        success=len(issues) == 0,
        issues=issues,
        metrics={
            "Manifests checked": len(manifests_found),
            "Missing subsystems": len(issues),
        },
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Level 7: Architectural Integrity")
    parser.add_argument("path", nargs="?", default="models", help="Path to models directory")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    result = validate_architecture(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

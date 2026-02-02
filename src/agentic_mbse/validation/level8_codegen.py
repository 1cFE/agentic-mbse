#!/usr/bin/env python3
"""
Level 8: Codegen Readiness

Validates that SysML models meet all requirements for successful code generation.
Catches codegen-specific issues early with actionable error messages.

Checks:
1. Qualified names - calc defs and usages have valid qualified_name (FR-2, FR-3)
2. Calc def structure - at least one output, direction markers (FR-4, FR-5)
3. Binding formats - REFERENCE uses ::, CHAIN uses . (FR-6)
4. Design attr completeness - design attrs have values or bindings (FR-7)
5. Design attr extractability - expressions produce numeric defaults (FR-8)
"""

import sys
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.expression import evaluate_true_static_expression
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import (
    Severity,
    ValidationCode,
    ValidationIssue,
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


def check_qualified_names(model: Any) -> list[ValidationIssue]:
    """
    Validate all calc defs and usages have valid qualified names.

    Checks:
    - FR-2: Calc defs have non-empty qualified_name
    - FR-3: Calc usages have EQN-derivable qualified names

    Returns:
        List of ValidationIssue for invalid qualified names
    """
    issues: list[ValidationIssue] = []

    # Check CalculationDefinitions (FR-2)
    try:
        calc_defs = list(SysideAdapter.elements_of_type(model, "CalculationDefinition"))
    except Exception:
        calc_defs = []

    for calc_def in calc_defs:
        try:
            qname = calc_def.qualified_name
            element_name = str(calc_def.name) if hasattr(calc_def, "name") else "<unnamed>"

            if not qname or str(qname).strip() == "":
                issues.append(
                    ValidationIssue(
                        level=8,
                        severity=Severity.ERROR,
                        code=ValidationCode.L8_MISSING_QUALIFIED_NAME,
                        message=f"Calc def '{element_name}' has no qualified_name",
                        element_name=element_name,
                        location=get_element_location(calc_def),
                        suggestion="Ensure calc def is in a named package",
                    )
                )
            else:
                # Validate format: must have :: separator or be simple name
                qname_str = str(qname)
                if " " in qname_str or qname_str.startswith("::"):
                    issues.append(
                        ValidationIssue(
                            level=8,
                            severity=Severity.ERROR,
                            code=ValidationCode.L8_INVALID_QUALIFIED_NAME,
                            message=f"Calc def '{element_name}' has malformed qualified_name: '{qname_str}'",
                            element_name=element_name,
                            location=get_element_location(calc_def),
                            suggestion="Qualified names should be Package::Element format",
                        )
                    )
        except AttributeError:
            element_name = getattr(calc_def, "name", "<unnamed>")
            issues.append(
                ValidationIssue(
                    level=8,
                    severity=Severity.ERROR,
                    code=ValidationCode.L8_MISSING_QUALIFIED_NAME,
                    message=f"Calc def '{element_name}' missing qualified_name attribute",
                    element_name=str(element_name),
                    location=get_element_location(calc_def),
                )
            )

    # Check CalculationUsages (FR-3: EQN derivability)
    try:
        calc_usages = list(SysideAdapter.elements_of_type(model, "CalculationUsage"))
    except Exception:
        calc_usages = []

    for calc_usage in calc_usages:
        try:
            qname = calc_usage.qualified_name
            element_name = str(getattr(calc_usage, "name", "<unnamed>"))

            if not qname or str(qname).strip() == "":
                issues.append(
                    ValidationIssue(
                        level=8,
                        severity=Severity.ERROR,
                        code=ValidationCode.L8_MISSING_QUALIFIED_NAME,
                        message=f"Calc usage '{element_name}' has no qualified_name",
                        element_name=element_name,
                        location=get_element_location(calc_usage),
                        suggestion="Ensure calc usage is in a named package/part",
                    )
                )
            else:
                # FR-3: Validate EQN derivability per ADR-001
                # EQN format: Package__Part__CalcUsage (uses __ separator)
                qname_str = str(qname)
                # Check that qualified name can be split into valid segments
                if "::" in qname_str:
                    segments = qname_str.split("::")
                    # Each segment must be a valid Python identifier for EQN derivation
                    for segment in segments:
                        if not segment or " " in segment or segment.startswith("_"):
                            issues.append(
                                ValidationIssue(
                                    level=8,
                                    severity=Severity.ERROR,
                                    code=ValidationCode.L8_INVALID_QUALIFIED_NAME,
                                    message=f"Calc usage '{qname_str}' has invalid segment '{segment}' - cannot derive EQN",
                                    element_name=qname_str,
                                    location=get_element_location(calc_usage),
                                    suggestion="Segments must be valid identifiers (no spaces, leading underscores)",
                                )
                            )
                            break
        except AttributeError:
            element_name = str(getattr(calc_usage, "name", "<unnamed>"))
            issues.append(
                ValidationIssue(
                    level=8,
                    severity=Severity.ERROR,
                    code=ValidationCode.L8_MISSING_QUALIFIED_NAME,
                    message=f"Calc usage '{element_name}' missing qualified_name attribute",
                    element_name=element_name,
                    location=get_element_location(calc_usage),
                )
            )

    return issues


def check_calc_def_structure(model: Any) -> list[ValidationIssue]:
    """
    Validate calc def parameter structure.

    Checks:
    - FR-4: At least one output parameter (direction = Out/Return)
    - FR-5: Input parameters have direction markers

    Returns:
        List of ValidationIssue for structural problems
    """
    issues: list[ValidationIssue] = []

    try:
        calc_defs = list(SysideAdapter.elements_of_type(model, "CalculationDefinition"))
    except Exception:
        calc_defs = []

    for calc_def in calc_defs:
        try:
            name = get_qualified_name(calc_def)
            location = get_element_location(calc_def)

            # Get owned members (parameters)
            if not hasattr(calc_def, "owned_members"):
                continue

            has_output = False
            params_without_direction: list[str] = []

            for member in calc_def.owned_members:
                # Check if it's a parameter (AttributeUsage or Feature with direction)
                # In SysML v2, parameters are typically AttributeUsage or similar
                if not hasattr(member, "name"):
                    continue

                member_name = str(member.name) if member.name else "<unnamed>"

                # Check direction attribute
                # SysML v2 has In, Inout, Out directions only
                # The 'return' keyword creates Out direction
                if hasattr(member, "direction") and member.direction:
                    direction_str = str(member.direction).lower()
                    if "out" in direction_str or "inout" in direction_str:
                        has_output = True
                else:
                    # Check if this looks like a parameter (has a type)
                    # Skip if it's not a parameter-like element
                    if hasattr(member, "typing"):
                        params_without_direction.append(member_name)

            # FR-4: Must have at least one output
            if not has_output:
                issues.append(
                    ValidationIssue(
                        level=8,
                        severity=Severity.ERROR,
                        code=ValidationCode.L8_CALC_DEF_NO_OUTPUT,
                        message=f"Calc def '{name}' has no output parameters",
                        element_name=name,
                        location=location,
                        suggestion="Add 'out' or 'return' parameter to calc def",
                    )
                )

            # FR-5: Warn about missing direction markers (WARNING not ERROR)
            if params_without_direction:
                issues.append(
                    ValidationIssue(
                        level=8,
                        severity=Severity.WARNING,
                        code=ValidationCode.L8_CALC_DEF_NO_DIRECTION,
                        message=f"Calc def '{name}' has parameters without direction: {params_without_direction}",
                        element_name=name,
                        location=location,
                        suggestion="Add 'in' or 'out' direction to parameters",
                    )
                )

        except Exception:
            continue  # Skip unparseable elements

    return issues


def _extract_chain_path(expr: Any) -> str | None:
    """Extract dotted path from FeatureChainExpression."""
    try:
        # Navigate AST to build instance.attribute path
        parts = []
        if hasattr(expr, "target_feature") and expr.target_feature:
            for feat in expr.target_feature:
                if hasattr(feat, "name") and feat.name:
                    parts.append(str(feat.name))
        return ".".join(parts) if parts else None
    except Exception:
        return None


def _extract_reference_path(expr: Any) -> str | None:
    """Extract qualified path from FeatureReferenceExpression."""
    try:
        # Get referent's qualified name
        if hasattr(expr, "referent") and expr.referent:
            ref = expr.referent
            if hasattr(ref, "qualified_name") and ref.qualified_name:
                return str(ref.qualified_name)
        return None
    except Exception:
        return None


def check_binding_formats(
    model: Any,
) -> tuple[list[ValidationIssue], int]:
    """
    Validate binding path formats match expected patterns.

    Checks:
    - FR-6: REFERENCE bindings use :: separator (or simple names)
    - FR-6: CHAIN bindings use . separator

    Returns:
        Tuple of (list of ValidationIssue, count of bindings validated)
    """
    issues: list[ValidationIssue] = []
    bindings_checked = 0

    try:
        calc_usages = list(SysideAdapter.elements_of_type(model, "CalculationUsage"))
    except Exception:
        calc_usages = []

    for calc_usage in calc_usages:
        try:
            usage_name = get_qualified_name(calc_usage)

            # Check for owned_members attribute
            if not hasattr(calc_usage, "owned_members"):
                continue

            # Get bindings from owned_members with feature_value_expression
            for member in calc_usage.owned_members:
                if not hasattr(member, "feature_value_expression"):
                    continue
                expr = member.feature_value_expression
                if not expr:
                    continue

                bindings_checked += 1
                param_name = str(member.name) if hasattr(member, "name") and member.name else "<unnamed>"

                # Determine binding type using SysideAdapter
                # FeatureChainExpression = instance.attribute path
                if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
                    # CHAIN binding - should use . separator in source_path
                    source_path = _extract_chain_path(expr)
                    if source_path and "::" in source_path:
                        issues.append(
                            ValidationIssue(
                                level=8,
                                severity=Severity.ERROR,
                                code=ValidationCode.L8_INVALID_BINDING_FORMAT,
                                message=f"CHAIN binding '{param_name}' in '{usage_name}' uses '::' separator (expected '.')",
                                element_name=usage_name,
                                location=get_element_location(calc_usage),
                                suggestion="Use instance.attribute format for chain bindings",
                            )
                        )

                # FeatureReferenceExpression = pkg::element path
                elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
                    # REFERENCE binding - should use :: separator (or be simple name)
                    source_path = _extract_reference_path(expr)
                    if source_path and "." in source_path and "::" not in source_path:
                        # Has dots but no :: - likely wrong format
                        issues.append(
                            ValidationIssue(
                                level=8,
                                severity=Severity.ERROR,
                                code=ValidationCode.L8_INVALID_BINDING_FORMAT,
                                message=f"REFERENCE binding '{param_name}' in '{usage_name}' uses '.' separator (expected '::')",
                                element_name=usage_name,
                                location=get_element_location(calc_usage),
                                suggestion="Use Package::Element format for reference bindings",
                            )
                        )

        except Exception:
            continue

    return issues, bindings_checked


def check_design_attr_completeness(
    model: Any,
    design_path_filter: str | None = "designs",
) -> tuple[list[ValidationIssue], int]:
    """
    Validate design attributes have values or EXPOSE bindings.

    Checks:
    - FR-7: Design attrs in designs/ have feature_value_expression or binding
    - FR-8: Design attrs with values produce extractable numeric defaults

    Args:
        model: Parsed SysML model
        design_path_filter: Path component to filter files by. Only attributes
            in files whose path contains this component are checked. Use None
            or empty string to check all files.

    Returns:
        Tuple of (list of ValidationIssue, count of design attrs checked)
    """
    issues: list[ValidationIssue] = []
    attrs_checked = 0

    try:
        attrs = list(SysideAdapter.elements_of_type(model, "AttributeUsage"))
    except Exception:
        attrs = []

    for attr in attrs:
        try:
            # Filter to models/designs/ directory only (proper path handling)
            doc = attr.document
            if not doc or not hasattr(doc, "url"):
                continue
            doc_path = Path(str(doc.url))
            # Filter by path component if specified
            if design_path_filter:
                if design_path_filter not in doc_path.parts:
                    continue  # Skip non-matching files

            # Skip attributes inside calc usages (those are bindings, not design attrs)
            owner = attr.owner if hasattr(attr, "owner") else None
            if owner:
                # Check if owner is a CalculationUsage
                try:
                    if SysideAdapter.is_instance(owner, "CalculationUsage"):
                        continue
                except Exception:
                    pass

            attrs_checked += 1
            attr_name = get_qualified_name(attr)
            location = get_element_location(attr)

            # Check for feature_value_expression (literal or binding)
            has_value = (
                hasattr(attr, "feature_value_expression")
                and attr.feature_value_expression is not None
            )

            # Check extractability — can codegen get a numeric default?
            if has_value:
                try:
                    evaluate_true_static_expression(attr.feature_value_expression)
                except (ValueError, TypeError) as e:
                    issues.append(
                        ValidationIssue(
                            level=8,
                            severity=Severity.ERROR,
                            code=ValidationCode.L8_DESIGN_ATTR_UNEXTRACTABLE,
                            message=(
                                f"Design attribute '{attr_name}' has expression but codegen "
                                f"cannot extract a numeric default: {e}"
                            ),
                            element_name=attr_name,
                            location=location,
                            suggestion=(
                                "Ensure the attribute value is a literal number or "
                                "static arithmetic expression (no feature references)"
                            ),
                        )
                    )

            if not has_value:
                issues.append(
                    ValidationIssue(
                        level=8,
                        severity=Severity.ERROR,
                        code=ValidationCode.L8_DESIGN_ATTR_INCOMPLETE,
                        message=f"Design attribute '{attr_name}' has no value or binding",
                        element_name=attr_name,
                        location=location,
                        suggestion="Add '= <value>' or bind to calc output",
                    )
                )

        except Exception:
            continue

    return issues, attrs_checked


def validate_codegen_readiness(
    models_path: str,
    design_path_filter: str | None = "designs",
) -> QualityCheckResult:
    """
    Main entry point for Level 8 validation.

    Args:
        models_path: Path to models directory
        design_path_filter: Path component to filter design attribute checks.
            Only files whose path contains this component are checked.
            Use None or empty string to check all files.

    Returns:
        QualityCheckResult with codegen readiness issues
    """
    print_header("Codegen Readiness", 8)

    # Discover SysML files
    try:
        files = discover_sysml_files(models_path)
    except ValueError as e:
        return QualityCheckResult(
            level=8,
            level_name="Codegen Readiness",
            success=False,
            issues=[str(e)],
        )

    if not files:
        return QualityCheckResult(
            level=8,
            level_name="Codegen Readiness",
            success=True,
            warnings=["No SysML files found"],
            metrics={"Files checked": 0},
        )

    # Load model
    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=8,
            level_name="Codegen Readiness",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # Run all checks
    all_issues: list[ValidationIssue] = []

    # Count elements for metrics
    try:
        num_calc_defs = len(list(SysideAdapter.elements_of_type(model, "CalculationDefinition")))
    except Exception:
        num_calc_defs = 0

    try:
        num_calc_usages = len(list(SysideAdapter.elements_of_type(model, "CalculationUsage")))
    except Exception:
        num_calc_usages = 0

    # Check 1: Qualified names (FR-2, FR-3)
    qname_issues = check_qualified_names(model)
    all_issues.extend(qname_issues)

    # Check 2: Calc def structure (FR-4, FR-5)
    structure_issues = check_calc_def_structure(model)
    all_issues.extend(structure_issues)

    # Check 3: Binding formats (FR-6)
    binding_issues, num_bindings = check_binding_formats(model)
    all_issues.extend(binding_issues)

    # Check 4: Design attr completeness (FR-7)
    design_attr_issues, num_design_attrs = check_design_attr_completeness(
        model, design_path_filter=design_path_filter
    )
    all_issues.extend(design_attr_issues)

    # Build result
    # CORRECT: Only ERRORs cause failure, WARNINGs do not
    success = not any(i.severity == Severity.ERROR for i in all_issues)

    result = QualityCheckResult(
        level=8,
        level_name="Codegen Readiness",
        success=success,
        metrics={
            "Calc defs checked": num_calc_defs,
            "Calc usages checked": num_calc_usages,
            "Bindings validated": num_bindings,
            "Design attrs checked": num_design_attrs,
            "L8_MISSING_QUALIFIED_NAME": len(
                [i for i in all_issues if i.code == ValidationCode.L8_MISSING_QUALIFIED_NAME]
            ),
            "L8_INVALID_QUALIFIED_NAME": len(
                [i for i in all_issues if i.code == ValidationCode.L8_INVALID_QUALIFIED_NAME]
            ),
            "L8_CALC_DEF_NO_OUTPUT": len(
                [i for i in all_issues if i.code == ValidationCode.L8_CALC_DEF_NO_OUTPUT]
            ),
            "L8_CALC_DEF_NO_DIRECTION": len(
                [i for i in all_issues if i.code == ValidationCode.L8_CALC_DEF_NO_DIRECTION]
            ),
            "L8_INVALID_BINDING_FORMAT": len(
                [i for i in all_issues if i.code == ValidationCode.L8_INVALID_BINDING_FORMAT]
            ),
            "L8_DESIGN_ATTR_INCOMPLETE": len(
                [i for i in all_issues if i.code == ValidationCode.L8_DESIGN_ATTR_INCOMPLETE]
            ),
            "L8_DESIGN_ATTR_UNEXTRACTABLE": len(
                [i for i in all_issues if i.code == ValidationCode.L8_DESIGN_ATTR_UNEXTRACTABLE]
            ),
        },
    )

    # Add all issues using add_issue for backward compatibility
    for issue in all_issues:
        result.add_issue(issue)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python level8_codegen_readiness.py <models_path>")
        sys.exit(EXIT_FAILURE)

    models_path = sys.argv[1]
    result = validate_codegen_readiness(models_path)
    print_result(result)
    sys.exit(EXIT_SUCCESS if result.success else EXIT_FAILURE)

#!/usr/bin/env python3
"""
Level 2: Structural Completeness

Validates that all model elements are properly connected and used.

Checks:
1. All calc defs in library/ are instantiated somewhere
2. All calc instance inputs are bound (placeholder for now)
3. No orphaned model elements (placeholder for now)
"""

import sys
from typing import Any

from agentic_mbse.sysml.binding import classify_binding, extract_bindings
from agentic_mbse.sysml.reference_use import ExactReferenceUse, resolved_referent
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import (
    BindingType,
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


def check_unused_definitions(model: Any) -> list[ValidationIssue]:
    """
    Check for calc defs in library/ that are never instantiated

    Returns:
        List of ValidationIssue for unused definitions
    """
    issues: list[ValidationIssue] = []

    # Get all calc definitions from library/
    library_defs = []

    # Iterate through all elements of type CalculationDefinition
    for element in SysideAdapter.elements_of_type(model, "CalculationDefinition"):
        # Check if this definition is in library/
        try:
            doc = element.document
            if doc and hasattr(doc, "url"):
                doc_path = str(doc.url)
                if "library/" in doc_path:
                    library_defs.append(element)
        except Exception:
            # Skip elements we can't access
            continue

    # Get all calc usages (instances)
    usages = list(SysideAdapter.elements_of_type(model, "CalculationUsage"))

    used_types = set()

    for usage in usages:
        # Get the calc definition this usage references
        if hasattr(usage, "calculation_definition") and usage.calculation_definition:
            used_types.add(get_qualified_name(usage.calculation_definition))

    # Find unused definitions
    for calc_def in library_defs:
        def_name = get_qualified_name(calc_def)
        if def_name not in used_types:
            location = get_element_location(calc_def)
            issues.append(
                ValidationIssue(
                    level=2,
                    severity=Severity.WARNING,
                    code=ValidationCode.UNUSED_DEFINITION,
                    message=f"Unused calc def: {def_name}",
                    element_name=def_name,
                    location=location,
                )
            )

    return issues


def check_unbound_inputs(model: Any) -> list[ValidationIssue]:
    """
    Check for calc instance inputs that are not bound or bound to undefined attributes.

    Uses agentic_mbse.sysml.binding for all analysis - no legacy fallbacks.

    Checks:
    1. Unbound inputs (no binding at all) → ERROR
    2. Literal bindings (placeholder values) → WARNING
    3. Undefined bindings (bound to attr without value) → ERROR

    Args:
        model: Loaded SysML model from syside

    Returns:
        List of ValidationIssue with ERRORs and WARNINGs
    """
    issues: list[ValidationIssue] = []

    calc_usages = list(SysideAdapter.elements_of_type(model, "CalculationUsage"))

    for calc_usage in calc_usages:
        try:
            calc_def = calc_usage.calculation_definition
            if not calc_def:
                continue

            input_features = _extract_input_features(calc_def)
            bindings = extract_bindings(calc_usage)

            # Build lookup for bindings by param name
            binding_map = {b.param_name: b for b in bindings}

            for input_feat in input_features:
                input_name = input_feat.name if hasattr(input_feat, "name") else "<unnamed>"

                # Skip optional inputs (have defaults)
                if _has_default_value(input_feat):
                    continue

                binding = binding_map.get(input_name)

                # CHECK 1: Is input bound?
                if binding is None or not binding.is_bound:
                    location = get_element_location(calc_usage)
                    calc_name = get_qualified_name(calc_usage)
                    issues.append(
                        ValidationIssue(
                            level=2,
                            severity=Severity.ERROR,
                            code=ValidationCode.UNBOUND_INPUT,
                            message=f"Unbound input '{input_name}' in calc '{calc_name}'",
                            element_name=calc_name,
                            location=location,
                        )
                    )
                    continue

                # CHECK 2: Is binding to literal?
                if binding.is_literal:
                    location = get_element_location(calc_usage)
                    calc_name = get_qualified_name(calc_usage)
                    issues.append(
                        ValidationIssue(
                            level=2,
                            severity=Severity.WARNING,
                            code=ValidationCode.LITERAL_BINDING,
                            message=(
                                f"Input '{input_name}' bound to literal value in calc "
                                f"'{calc_name}' - consider binding to attribute or calc output"
                            ),
                            element_name=calc_name,
                            location=location,
                        )
                    )
                    continue

                # CHECK 3: Do ALL binding targets have values?
                for use in binding.reference_uses:
                    # An indexed use has no exact target, so this check has nothing to
                    # ask about it; the closed boundary refuses it before generation.
                    if not isinstance(use, ExactReferenceUse):
                        continue
                    leaf = use.path.leaf
                    if not leaf.declares_value:
                        location = get_element_location(calc_usage)
                        calc_name = get_qualified_name(calc_usage)
                        target_name = leaf.qualified_name or leaf.element_name
                        issues.append(
                            ValidationIssue(
                                level=2,
                                severity=Severity.ERROR,
                                code=ValidationCode.UNDEFINED_BINDING,
                                message=(
                                    f"Input '{input_name}' in calc '{calc_name}' "
                                    f"bound to undefined attribute '{target_name}'"
                                ),
                                element_name=calc_name,
                                location=location,
                            )
                        )

        except Exception:
            # Skip calc usages we can't analyze
            continue

    return issues


def _extract_input_features(calc_def: Any) -> list[Any]:
    """
    Extract input features from calculation definition.

    Traverses calc_def.owned_members to find Feature elements
    (AttributeUsage or ReferenceUsage) with input direction (not Out/Return).

    Args:
        calc_def: CalculationDefinition element

    Returns:
        List of input feature elements
    """
    inputs = []

    if not hasattr(calc_def, "owned_members"):
        return inputs

    for member in calc_def.owned_members:
        # Check if this is a feature (attribute or reference)
        # Note: calc def parameters can be ReferenceUsage or AttributeUsage
        if not (
            SysideAdapter.is_instance(member, "AttributeUsage") or SysideAdapter.is_instance(member, "ReferenceUsage")
        ):
            continue

        # Check direction - determine if input or output
        is_output = False
        if hasattr(member, "direction"):
            direction_str = str(member.direction)
            # Output directions: "Out", "Return"
            if "Out" in direction_str or "Return" in direction_str:
                is_output = True

        if not is_output:
            # Assume input (In direction or no direction specified)
            inputs.append(member)

    return inputs


def _has_default_value(feature: Any) -> bool:
    """
    Check if feature has a default value expression.

    Checks for feature_value_expression attribute.

    Args:
        feature: Feature element to check

    Returns:
        True if feature has default value, False otherwise
    """
    # Check for feature value expression (default value in calc def)
    if hasattr(feature, "feature_value_expression") and feature.feature_value_expression:
        return True

    # Future enhancement: Check for default_value property if exists
    # if hasattr(feature, "default_value") and feature.default_value:
    #     return True

    return False


def check_self_named_bindings(model: Any) -> list[ValidationIssue]:
    """
    C1 (Item 12): flag every self-named input binding.

    A binding whose right-hand side resolves to the calc's own input parameter
    (`in P = P`) dead-ends: the intended outer value never reaches the input.
    Every such binding is a modeling error.

    The comparison is referent identity, mirroring codegen's SRC-01 rule
    (``extraction/source_evidence.py::is_self_binding``): the value
    expression's resolved referent element is compared with the bound parameter
    member itself. A name comparison is wrong in one direction — it also
    flagged the supported owner-qualified form ``in x = owner::x``, whose
    referent is the owner's attribute and not the parameter (F-2,
    self-binding-replacement Phase 1).

    There is no same-named-outer-feature exemption. The check used to suppress the
    diagnostic when the enclosing part carried an attribute or sibling calc output
    named `P`, on the theory that the outer feature would be resolved downstream.
    Exact elaboration never does that: D-4 [OWNER-VERBATIM 2026-08-05] — "Never
    reinterpret a self-binding as an outer reference" — and the lifecycle contract's
    blocking-diagnostics clause and violation table put `SI_SELF_BINDING` in the
    blocking set unconditionally. A validator that stayed silent on a shape the
    generator refuses was telling the author the model was fine when it was not.

    Returns:
        List of ValidationIssue (ERROR), one per self-named binding.
    """
    issues: list[ValidationIssue] = []

    for calc_usage in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        try:
            calc_def = calc_usage.calculation_definition
            if not calc_def:
                continue

            input_params = {
                str(feat.name)
                for feat in _extract_input_features(calc_def)
                if getattr(feat, "name", None)
            }

            for member in getattr(calc_usage, "owned_members", None) or []:
                param_name = str(getattr(member, "name", "") or "")
                if param_name not in input_params:
                    continue
                expr = getattr(member, "feature_value_expression", None)
                if classify_binding(expr) != BindingType.REFERENCE:
                    continue
                # Self-named: the RHS reference's resolved referent IS the bound
                # parameter member. An unresolved referent is a load error, not
                # a self-binding this check can establish.
                referent = resolved_referent(expr)
                if referent is None:
                    continue
                if SysideAdapter.element_id(referent) != SysideAdapter.element_id(member):
                    continue

                calc_name = get_qualified_name(calc_usage)
                issues.append(
                    ValidationIssue(
                        level=2,
                        severity=Severity.ERROR,
                        code=ValidationCode.L2_SELF_NAMED_BINDING,
                        message=(
                            f"Input '{param_name}' in calc '{calc_name}' binds to a "
                            f"same-named reference that resolves to the calc's own parameter, "
                            f"so the binding dead-ends. A same-named feature in the enclosing "
                            f"scope does not rescue it — the binding is never reinterpreted as "
                            f"an outer reference. Bind the outer feature by a distinct path"
                        ),
                        element_name=calc_name,
                        location=get_element_location(calc_usage),
                    )
                )
        except Exception as error:  # noqa: BLE001 — surfaced as a finding, never swallowed
            # An inspection failure leaves this usage UNVERIFIED. Reporting it as
            # an ERROR keeps the run honest: a SysIDE or adapter regression must
            # read as a failed check, not as a clean model (audit F4).
            issues.append(
                ValidationIssue(
                    level=2,
                    severity=Severity.ERROR,
                    code=ValidationCode.L2_CHECK_UNVERIFIABLE,
                    message=(
                        f"self-named-binding check could not inspect calc usage "
                        f"'{_safe_display_name(calc_usage)}': "
                        f"{type(error).__name__}: {error}. The usage is unverified; "
                        f"treat this as a check failure, not a clean result"
                    ),
                    element_name=_safe_display_name(calc_usage),
                )
            )

    return issues


def _safe_display_name(element: Any) -> str:
    """A best-effort name for an element that may itself refuse inspection."""
    try:
        return str(get_qualified_name(element) or getattr(element, "name", None) or repr(element))
    except Exception:  # noqa: BLE001 — naming only; the failure is already being reported
        return "<unnameable element>"


def check_orphaned_elements(model: Any) -> list[ValidationIssue]:
    """
    Check for model elements not reachable from entry points

    This is a simplified check - full implementation would need to:
    1. Identify entry points (system.sysml, top-level packages)
    2. Build reachability graph from entry points
    3. Report elements not in graph

    Returns:
        List of ValidationIssue for orphaned elements
    """
    # For now, return empty - this is complex and lower priority
    # Can be enhanced in future iterations
    return []


def validate_structure(models_path: str) -> QualityCheckResult:
    """
    Validate structural completeness

    Args:
        models_path: Path to models directory

    Returns:
        QualityCheckResult with structural issues
    """
    print_header("Structural Completeness", 2)

    # Discover and load model
    files = discover_sysml_files(models_path)
    if not files:
        return QualityCheckResult(
            level=2,
            level_name="Structural Completeness",
            success=True,
            warnings=["No SysML files found"],
        )

    print(f"Found {len(files)} SysML files")

    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=2,
            level_name="Structural Completeness",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # Run checks - now return List[ValidationIssue]
    all_issues: list[ValidationIssue] = []
    all_issues.extend(check_unused_definitions(model))
    all_issues.extend(check_unbound_inputs(model))
    # C1 (Item 12): FAIL when `in P = P` resolves the right-hand reference to the
    # bound input member itself. Same-named features elsewhere do not change that
    # resolved identity.
    all_issues.extend(check_self_named_bindings(model))
    all_issues.extend(check_orphaned_elements(model))

    # Create result and use add_issue() to populate both lists
    result = QualityCheckResult(
        level=2,
        level_name="Structural Completeness",
        success=len(all_issues) == 0,
    )

    # Add each issue using add_issue() to populate structured_issues and issues
    for issue in all_issues:
        result.add_issue(issue)

    # Calculate metrics from structured issues
    result.metrics = {
        "Unused definitions": len(
            [i for i in result.structured_issues if i.code == ValidationCode.UNUSED_DEFINITION]
        ),
        "Unbound inputs": len(
            [i for i in result.structured_issues if i.code == ValidationCode.UNBOUND_INPUT]
        ),
        "Undefined bindings": len(
            [i for i in result.structured_issues if i.code == ValidationCode.UNDEFINED_BINDING]
        ),
        "Placeholder bindings": len(
            [i for i in result.structured_issues if i.code == ValidationCode.LITERAL_BINDING]
        ),
        "Self-named bindings": len(
            [i for i in result.structured_issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING]
        ),
        "Orphaned elements": 0,  # No orphan check implemented yet
    }

    return result


def main() -> int:
    """Entry point for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Level 2: Structural Completeness")
    parser.add_argument("path", nargs="?", default="models", help="Path to models directory")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    result = validate_structure(args.path)
    print_result(result)

    return EXIT_SUCCESS if result.success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())

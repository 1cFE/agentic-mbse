#!/usr/bin/env python3
"""
Level 6: Architecture & Generator Subset

Application-specific validation: ADR-002 rules, manifest subsystem
checks, codegen checks, and the generator subset contract (EXEC-SUBSET-CONTRACT
Item 3: run first, presented through the execution target).

Merged from:
- Level 7 (Architectural Integrity): manifest-based subsystem validation
- Level 8 (Codegen Readiness): qualified names, calc def structure,
  binding formats, design attr completeness/extractability
- ADR-002 calls (previously in Level 2)
"""

from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any, TypeVar
from uuid import UUID

import yaml

from agentic_mbse.sysml.executable_profile import Eligibility, evaluate_identified_profile
from agentic_mbse.sysml.expression import (
    Unextractable,
    evaluate_true_static_expression,
    is_literal_node,
)
from agentic_mbse.sysml.reference_use import (
    resolved_chain_target,
    resolved_chaining_features,
    resolved_referent,
)
from agentic_mbse.sysml.subset_advisories import Advisories, extract_advisories
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_profile import SubsetProfileResult, evaluate_subset_profile
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue

from .adr002 import (
    check_calc_def_locations,
    check_static_expressions,
    check_static_function_invocations,
    check_supported_operators,
    is_expose_binding,
)
from .common import (
    QualityCheckResult,
    check_error_issue,
    discover_sysml_files,
    get_element_location,
    get_qualified_name,
    load_sysml_model,
    print_header,
)
from .execution_target import (
    FromFile,
    FromOverride,
    Target,
    TargetResolution,
    TargetSettingError,
    Unset,
    describe_target,
    resolve_target,
)
from .session import constraint_facts
from .subset_presentation import present, string_subjects

LEVEL_NAME = "Architecture & Generator Subset"

# --- Functions from L7 (manifest validation) ---


class ManifestError(Exception):
    """A design's manifest.yaml exists but cannot be read as a mapping."""


def load_manifest(design_path: Path) -> dict[Any, Any] | None:
    """
    Load a design's manifest.

    Args:
        design_path: Path to design directory (e.g., models/designs/design_model/)

    Returns:
        The manifest mapping, or None when the design carries no manifest at all.

    Raises:
        ManifestError: the manifest exists but is unreadable, malformed YAML, or is
            well-formed YAML that is not a mapping. Absent and invalid are different
            states and this function reports them differently: a design without a
            manifest has nothing to check, an unusable one is a Level 6 defect.
    """
    manifest_path = design_path / "manifest.yaml"

    if not manifest_path.exists():
        return None

    try:
        with manifest_path.open() as manifest_file:
            manifest = yaml.safe_load(manifest_file)
    # UnicodeDecodeError is a ValueError, not an OSError, and `yaml.safe_load` raises it
    # through the file handle before the parser ever sees the bytes.
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise ManifestError(f"{manifest_path} could not be read: {error}") from error
    if not isinstance(manifest, dict):
        # Callers subscript the result. Well-formed YAML that is a list or a scalar used to
        # reach them and fail there instead of here.
        raise ManifestError(
            f"{manifest_path} is a {type(manifest).__name__}, not a mapping of manifest keys"
        )
    return manifest


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
        if subsystem not in part_names:
            missing.append(subsystem)

    return missing


def _check_manifests(models_path: str, model: Any) -> tuple[list[str], int]:
    """Check manifest subsystem composition. Returns (issues, manifests_checked).

    Unlike old L7's validate_architecture(), this does NOT early-return a
    QualityCheckResult. Missing designs/ or no manifests -> empty list, not failure.
    The calling orchestrator handles these as "no manifest issues found."
    """
    designs_path = Path(models_path) / "designs"
    if not designs_path.exists():
        return [], 0

    manifests_found = list(designs_path.glob("*/manifest.yaml"))
    if not manifests_found:
        return [], 0

    issues = []
    for manifest_path in manifests_found:
        # Policy, stated here rather than hidden in the loader: an unusable manifest fails
        # Level 6, and one bad file must not stop the remaining designs from being checked.
        try:
            manifest = load_manifest(manifest_path.parent)
        except ManifestError as error:
            issues.append(f"Unusable manifest in {manifest_path.parent.name}: {error}")
            continue
        if manifest is None:
            # The glob above found this file, so it can only be gone because something
            # removed it mid-check. That is worth reporting, not skipping.
            issues.append(f"Manifest {manifest_path} vanished during the check")
            continue
        missing = check_subsystem_composition(model, manifest)
        for subsystem in missing:
            issues.append(f"Missing subsystem '{subsystem}' in {manifest_path.parent.name}")
    return issues, len(manifests_found)


# --- Functions from L8 (codegen readiness) ---


def _segment_is_quoted(segment: str) -> bool:
    """Whether a `::`-delimited name segment is a quoted name (e.g. 'Trap Plant').

    C6b (Item 12): `sanitize_name` (`sysml/qualified_names.py`, which sysml-codegen
    `b5663c07` re-exports at `core/qualified_names.py:10-17`) turns a quoted name into
    a valid Python identifier (`'Trap Plant'` -> `Trap_Plant`), so a space inside a
    quoted segment is legal, not a malformed qualified name. Only an *unquoted* space
    is flagged. That codegen sanitizes every segment, so L6_INVALID_QUALIFIED_NAME is
    not a generator refusal; backlog L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES.
    """
    s = segment.strip()
    return len(s) >= 2 and s.startswith("'") and s.endswith("'")


def _element_error(check: str, element: Any, error: Exception) -> ValidationIssue:
    """`L6_CHECK_ERROR` for one element `check` could not inspect (design D4, element scope)."""
    return check_error_issue(
        check, get_qualified_name(element), error, get_element_location(element)
    )


def _enumeration_error(check: str, type_name: str, error: Exception) -> ValidationIssue:
    """`L6_CHECK_ERROR` for a check that could not list its elements (D4, check scope)."""
    return check_error_issue(check, f"the model's {type_name} elements", error)


def check_qualified_names(model: Any) -> list[ValidationIssue]:
    """
    Validate all calc defs and usages have valid qualified names.

    Checks:
    - Calc defs have non-empty qualified_name
    - Calc usages have EQN-derivable qualified names

    Returns:
        List of ValidationIssue for invalid qualified names
    """
    issues: list[ValidationIssue] = []

    # Check CalculationDefinitions; a failed listing ends only this half, not the usage half.
    try:
        calc_defs = list(SysideAdapter.elements_of_type(model, "CalculationDefinition"))
    except Exception as error:
        calc_defs = []
        issues.append(_enumeration_error("check_qualified_names", "CalculationDefinition", error))

    for calc_def in calc_defs:
        try:
            qname = calc_def.qualified_name
            element_name = str(calc_def.name) if hasattr(calc_def, "name") else "<unnamed>"

            if not qname or str(qname).strip() == "":
                issues.append(
                    ValidationIssue(
                        level=6,
                        severity=Severity.ERROR,
                        code=ValidationCode.L6_MISSING_QUALIFIED_NAME,
                        message=f"Calc def '{element_name}' has no qualified_name",
                        element_name=element_name,
                        location=get_element_location(calc_def),
                        suggestion="Ensure calc def is in a named package",
                    )
                )
            else:
                # Validate format: must have :: separator or be simple name.
                # A space inside a quoted segment is legal (C6b, sanitize_name).
                qname_str = str(qname)
                unquoted_space = any(
                    " " in seg and not _segment_is_quoted(seg) for seg in qname_str.split("::")
                )
                if unquoted_space or qname_str.startswith("::"):
                    issues.append(
                        ValidationIssue(
                            level=6,
                            severity=Severity.ERROR,
                            code=ValidationCode.L6_INVALID_QUALIFIED_NAME,
                            message=f"Calc def '{element_name}' has malformed qualified_name: '{qname_str}'",
                            element_name=element_name,
                            location=get_element_location(calc_def),
                            suggestion="Qualified names should be Package::Element format",
                        )
                    )
        except Exception as error:
            # A failed read is not a missing name: report it, make no finding (Appendix B).
            issues.append(_element_error("check_qualified_names", calc_def, error))

    # Check CalculationUsages (EQN derivability)
    try:
        calc_usages = list(SysideAdapter.elements_of_type(model, "CalculationUsage"))
    except Exception as error:
        issues.append(_enumeration_error("check_qualified_names", "CalculationUsage", error))
        return issues

    for calc_usage in calc_usages:
        try:
            qname = calc_usage.qualified_name
            element_name = str(getattr(calc_usage, "name", "<unnamed>"))

            if not qname or str(qname).strip() == "":
                issues.append(
                    ValidationIssue(
                        level=6,
                        severity=Severity.ERROR,
                        code=ValidationCode.L6_MISSING_QUALIFIED_NAME,
                        message=f"Calc usage '{element_name}' has no qualified_name",
                        element_name=element_name,
                        location=get_element_location(calc_usage),
                        suggestion="Ensure calc usage is in a named package/part",
                    )
                )
            else:
                # Validate EQN derivability per ADR-001
                qname_str = str(qname)
                if "::" in qname_str:
                    segments = qname_str.split("::")
                    for segment in segments:
                        # A quoted segment (e.g. 'Trap Plant') sanitizes to a valid
                        # identifier (C6b), so its internal space is legal.
                        if _segment_is_quoted(segment):
                            continue
                        if not segment or " " in segment or segment.startswith("_"):
                            issues.append(
                                ValidationIssue(
                                    level=6,
                                    severity=Severity.ERROR,
                                    code=ValidationCode.L6_INVALID_QUALIFIED_NAME,
                                    message=f"Calc usage '{qname_str}' has invalid segment '{segment}' - cannot derive EQN",
                                    element_name=qname_str,
                                    location=get_element_location(calc_usage),
                                    suggestion="Segments must be valid identifiers (no spaces, leading underscores)",
                                )
                            )
                            break
        except Exception as error:
            issues.append(_element_error("check_qualified_names", calc_usage, error))

    return issues


def check_calc_def_structure(model: Any) -> list[ValidationIssue]:
    """
    Validate calc def parameter structure.

    Checks:
    - At least one output parameter (direction = Out/Return)
    - Input parameters have direction markers

    Returns:
        List of ValidationIssue for structural problems
    """
    issues: list[ValidationIssue] = []

    try:
        calc_defs = list(SysideAdapter.elements_of_type(model, "CalculationDefinition"))
    except Exception as error:
        return [_enumeration_error("check_calc_def_structure", "CalculationDefinition", error)]

    for calc_def in calc_defs:
        try:
            name = get_qualified_name(calc_def)
            location = get_element_location(calc_def)

            if not hasattr(calc_def, "owned_members"):
                continue

            has_output = False
            params_without_direction: list[str] = []

            for member in calc_def.owned_members:
                if not hasattr(member, "name"):
                    continue

                member_name = str(member.name) if member.name else "<unnamed>"

                if hasattr(member, "direction") and member.direction:
                    direction_str = str(member.direction).lower()
                    if "out" in direction_str or "inout" in direction_str:
                        has_output = True
                else:
                    if hasattr(member, "typing"):
                        params_without_direction.append(member_name)

            if not has_output:
                issues.append(
                    ValidationIssue(
                        level=6,
                        severity=Severity.ERROR,
                        code=ValidationCode.L6_CALC_DEF_NO_OUTPUT,
                        message=f"Calc def '{name}' has no output parameters",
                        element_name=name,
                        location=location,
                        suggestion="Add 'out' or 'return' parameter to calc def",
                    )
                )

            if params_without_direction:
                issues.append(
                    ValidationIssue(
                        level=6,
                        severity=Severity.WARNING,
                        code=ValidationCode.L6_CALC_DEF_NO_DIRECTION,
                        message=f"Calc def '{name}' has parameters without direction: {params_without_direction}",
                        element_name=name,
                        location=location,
                        suggestion="Add 'in' or 'out' direction to parameters",
                    )
                )

        except Exception as error:
            issues.append(_element_error("check_calc_def_structure", calc_def, error))

    return issues


def _extract_chain_path(expr: Any) -> str | None:
    """The resolved member path of a feature chain, dotted."""
    target = resolved_chain_target(expr)
    if target is None:
        return None
    parts = [
        str(feature.name)
        for feature in resolved_chaining_features(target)
        if getattr(feature, "name", None)
    ]
    return ".".join(parts) if parts else None


def _extract_reference_path(expr: Any) -> str | None:
    """The qualified name of a feature reference's exact referent."""
    referent = resolved_referent(expr)
    qualified_name = getattr(referent, "qualified_name", None) if referent else None
    return str(qualified_name) if qualified_name else None


def check_binding_formats(
    model: Any,
) -> tuple[list[ValidationIssue], int]:
    """
    Validate binding path formats match expected patterns.

    Checks:
    - REFERENCE bindings use :: separator (or simple names)
    - CHAIN bindings use . separator

    Returns:
        Tuple of (list of ValidationIssue, count of bindings validated)
    """
    issues: list[ValidationIssue] = []
    bindings_checked = 0

    try:
        calc_usages = list(SysideAdapter.elements_of_type(model, "CalculationUsage"))
    except Exception as error:
        return [_enumeration_error("check_binding_formats", "CalculationUsage", error)], 0

    for calc_usage in calc_usages:
        try:
            usage_name = get_qualified_name(calc_usage)

            if not hasattr(calc_usage, "owned_members"):
                continue

            for member in calc_usage.owned_members:
                if not hasattr(member, "feature_value_expression"):
                    continue
                expr = member.feature_value_expression
                if not expr:
                    continue

                bindings_checked += 1
                param_name = (
                    str(member.name) if hasattr(member, "name") and member.name else "<unnamed>"
                )

                if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
                    source_path = _extract_chain_path(expr)
                    if source_path and "::" in source_path:
                        issues.append(
                            ValidationIssue(
                                level=6,
                                severity=Severity.ERROR,
                                code=ValidationCode.L6_INVALID_BINDING_FORMAT,
                                message=f"CHAIN binding '{param_name}' in '{usage_name}' uses '::' separator (expected '.')",
                                element_name=usage_name,
                                location=get_element_location(calc_usage),
                                suggestion="Use instance.attribute format for chain bindings",
                            )
                        )

                elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
                    source_path = _extract_reference_path(expr)
                    if source_path and "." in source_path and "::" not in source_path:
                        issues.append(
                            ValidationIssue(
                                level=6,
                                severity=Severity.ERROR,
                                code=ValidationCode.L6_INVALID_BINDING_FORMAT,
                                message=f"REFERENCE binding '{param_name}' in '{usage_name}' uses '.' separator (expected '::')",
                                element_name=usage_name,
                                location=get_element_location(calc_usage),
                                suggestion="Use Package::Element format for reference bindings",
                            )
                        )

        except Exception as error:
            issues.append(_element_error("check_binding_formats", calc_usage, error))

    return issues, bindings_checked


def check_design_attr_completeness(
    model: Any,
    design_path_filter: str | None = "designs",
    string_subjects: frozenset[UUID] | None = None,
) -> tuple[list[ValidationIssue], int]:
    """
    Validate design attributes have values or EXPOSE bindings.

    Checks:
    - Design attrs in designs/ have feature_value_expression or binding
    - Design attrs with values produce extractable numeric defaults, except EXPOSE
      bindings (see is_expose_binding), which are complete as written

    Args:
        model: Parsed SysML model
        design_path_filter: Path component to filter files by. Only attributes
            in files whose path contains this component are checked. Use None
            or empty string to check all files.
        string_subjects: Element ids the subset contract reports as omitted String values
            (`string-value-omission`). Those get no `L6_DESIGN_ATTR_UNEXTRACTABLE`: the
            contract's `omitted` finding replaces it (Item 3 design D10). None when the
            contract did not run, so every legacy error stays.

    Returns:
        Tuple of (list of ValidationIssue, count of design attrs checked)
    """
    issues: list[ValidationIssue] = []
    attrs_checked = 0
    omitted_strings = string_subjects or frozenset()

    try:
        attrs = list(SysideAdapter.elements_of_type(model, "AttributeUsage"))
    except Exception as error:
        return [_enumeration_error("check_design_attr_completeness", "AttributeUsage", error)], 0

    for attr in attrs:
        try:
            doc = attr.document
            if not doc or not hasattr(doc, "url"):
                continue
            doc_path = Path(str(doc.url))
            if design_path_filter:
                if design_path_filter not in doc_path.parts:
                    continue

            # A failed owner test reaches the element handler below, so the attribute is
            # reported and not checked (Appendix B, :520).
            owner = attr.owner if hasattr(attr, "owner") else None
            if owner and SysideAdapter.is_instance(owner, "CalculationUsage"):
                continue

            attrs_checked += 1
            attr_name = get_qualified_name(attr)
            location = get_element_location(attr)

            has_value = (
                hasattr(attr, "feature_value_expression")
                and attr.feature_value_expression is not None
            )

            if has_value:
                # D3 (L6-EXPOSE-CONSISTENCY): an EXPOSE binding is complete. Codegen
                # wires the alias to its source (sysml-codegen `b5663c07`,
                # `elaboration/elaborate.py:982-1012`), so it needs no numeric default
                # and the static evaluator does not apply.
                if is_expose_binding(attr, attr.feature_value_expression):
                    continue
                if omitted_strings and _element_id(attr) in omitted_strings:
                    continue
                try:
                    evaluate_true_static_expression(attr.feature_value_expression)
                except Unextractable as e:  # only the evaluator's own signal (D16)
                    issues.append(
                        ValidationIssue(
                            level=6,
                            severity=Severity.ERROR,
                            code=ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE,
                            message=(
                                f"Design attribute '{attr_name}' has an expression with no "
                                f"static numeric value: {e}"
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
                        level=6,
                        severity=Severity.ERROR,
                        code=ValidationCode.L6_DESIGN_ATTR_INCOMPLETE,
                        message=f"Design attribute '{attr_name}' has no value or binding",
                        element_name=attr_name,
                        location=location,
                        suggestion="Add '= <value>' or bind to calc output",
                    )
                )

        except Exception as error:
            issues.append(_element_error("check_design_attr_completeness", attr, error))

    return issues, attrs_checked


def _element_id(element: Any) -> UUID | None:
    try:
        return SysideAdapter.element_id(element)
    except ValueError:
        return None


def check_anonymous_returns(model: Any) -> list[ValidationIssue]:
    """
    C2a (Item 12): FAIL a calc def with an anonymous `return`.

    An anonymous `return : Real = <expr>` has no declared name (syside synthesizes
    `result`, but declared_name is empty), so codegen derives no output channel from
    it. Mirrors codegen's V8 diagnostic (sysml-codegen `b5663c07`,
    `extraction/extractor.py:191-215`, REQ-EXT-11). The named forms — `out attribute`, named
    `return` (inline or body-assignment), and bare `in` — carry a declared name and
    are accepted.

    Returns:
        List of ValidationIssue (ERROR) for anonymous returns.
    """
    issues: list[ValidationIssue] = []

    for calc_def in SysideAdapter.elements_of_type(model, "CalculationDefinition"):
        try:
            if not hasattr(calc_def, "owned_members"):
                continue
            name = get_qualified_name(calc_def)
            for member in calc_def.owned_members:
                direction = (
                    str(getattr(member, "direction", "")) if hasattr(member, "direction") else ""
                )
                if "Out" not in direction and "Return" not in direction:
                    continue
                declared = getattr(member, "declared_name", None)
                if declared is None or str(declared).strip() == "":
                    issues.append(
                        ValidationIssue(
                            level=6,
                            severity=Severity.ERROR,
                            code=ValidationCode.L6_ANONYMOUS_RETURN,
                            message=(
                                f"Calc def '{name}' has an anonymous return (no declared name); "
                                f"codegen derives no output channel from it"
                            ),
                            element_name=name,
                            location=get_element_location(calc_def),
                            suggestion=(
                                "Name the result: `return <name> : Real = <expr>;` or "
                                "`out attribute <name> : Real = <expr>;`"
                            ),
                        )
                    )
        except Exception as error:
            issues.append(_element_error("check_anonymous_returns", calc_def, error))

    return issues


def _format_diagnostic_location(location: Any) -> str:
    if location is None:
        return "<no location>"
    return f"{location.file}:{location.line}"


def check_constraint_executability(model: Any) -> list[ValidationIssue]:
    """
    Report malformed numerical diagnostics as errors and non-numerical statements as warnings.

    BLOCK emits one ERROR per diagnostic so each malformed construct names its fix.
    NON_NUMERICAL emits one aggregated WARNING per statement, preserving diagnostic walk order.

    Runs the exact route: a usage is evaluated against the definition its parser UUID names.
    The neutral route indexed definitions by qualified name, so two definitions sharing one
    qualified name collapsed to whichever the enumeration reached last and the reported
    diagnostics depended on that order. The exact route refuses a duplicate UUID instead.
    """
    # D7 (Item 4): an extraction failure must surface, not collapse to "no diagnostics" — no
    # `except Exception: ...` swallow here, matching the discipline this function has kept since
    # Item 4 removed the equivalent swallow for constraint enumeration.
    result = evaluate_identified_profile(constraint_facts(model))

    issues: list[ValidationIssue] = []
    for identified in result.decisions:
        decision = identified.decision
        name = decision.identity.qualified_name or decision.identity.name or "<anonymous>"
        if decision.eligibility is Eligibility.BLOCK:
            for diagnostic in decision.diagnostics:
                issues.append(
                    ValidationIssue(
                        level=6,
                        severity=Severity.ERROR,
                        code=ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL,
                        message=(
                            f"Constraint '{name}' is a malformed numerical statement: "
                            f"{diagnostic.construct} ({diagnostic.reason})"
                        ),
                        element_name=name,
                        location=_format_diagnostic_location(diagnostic.location),
                        suggestion=diagnostic.message,
                        reason_code=diagnostic.reason,
                    )
                )
            continue
        if decision.eligibility is not Eligibility.NON_NUMERICAL:
            continue
        reasons = ", ".join(diagnostic.reason for diagnostic in decision.diagnostics)
        suggestions = "; ".join(diagnostic.message for diagnostic in decision.diagnostics)
        issues.append(
            ValidationIssue(
                level=6,
                severity=Severity.WARNING,
                code=ValidationCode.L6_CONSTRAINT_NON_NUMERICAL,
                message=(
                    f"Constraint '{name}' is not a numerical statement and will not execute: "
                    f"{reasons}"
                ),
                element_name=name,
                location=_format_diagnostic_location(decision.location),
                suggestion=suggestions,
                # One aggregated WARNING per statement, so the branchable code is the
                # first diagnostic's reason; the full set stays in `message`.
                reason_code=next((diagnostic.reason for diagnostic in decision.diagnostics), None),
            )
        )
    return issues


def check_calc_bearing_instantiation(model: Any) -> list[ValidationIssue]:
    """
    C4 (Item 12): FAIL a calc-bearing part def that no usage instantiates.

    A part def that owns template calcs but is never instantiated — plainly OR by
    retyping — has its calcs silently dropped at extraction. "Instantiated" means the
    part def's name appears in some part usage's resolved type set. A part usage's
    `.types` includes the full supertype chain AND any retype target, so a retyped
    usage (`part :>> x : Subtype`) counts the subtype as instantiated (Item 4).

    Returns:
        List of ValidationIssue (ERROR) for uninstantiated calc-bearing part defs.
    """
    issues: list[ValidationIssue] = []

    # Union of every type name reachable through a part usage (chain + retypes).
    # A partial set would make false findings, so a failure here ends the check (Appendix B).
    instantiated: set[str] = set()
    try:
        for part_usage in SysideAdapter.elements_of_type(model, "PartUsage"):
            for typ in getattr(part_usage, "types", []) or []:
                type_name = getattr(typ, "name", None)
                if type_name:
                    instantiated.add(str(type_name))
    except Exception as error:
        return [_enumeration_error("check_calc_bearing_instantiation", "PartUsage", error)]

    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        try:
            if not hasattr(part_def, "owned_members"):
                continue
            owns_calc = any(
                SysideAdapter.is_instance(member, "CalculationUsage")
                for member in part_def.owned_members
            )
            if not owns_calc:
                continue

            part_name = getattr(part_def, "name", None)
            if not part_name:
                continue
            if str(part_name) in instantiated:
                continue

            issues.append(
                ValidationIssue(
                    level=6,
                    severity=Severity.ERROR,
                    code=ValidationCode.L6_CALC_DEF_NO_INSTANTIATION,
                    message=(
                        f"Part def '{part_name}' owns template calcs but is never instantiated "
                        f"(plainly or by retyping); its calcs are dropped at extraction"
                    ),
                    element_name=str(part_name),
                    location=get_element_location(part_def),
                    suggestion=(
                        "Instantiate the part def with a part usage, or retype an existing usage to it"
                    ),
                )
            )
        except Exception as error:
            issues.append(_element_error("check_calc_bearing_instantiation", part_def, error))

    return issues


def check_body_assignment_impl_loss(model: Any) -> list[ValidationIssue]:
    """
    C2b (Item 12): WARN a calc def output computed by body assignment.

    The form `return attribute y : Real; y = <expr>` declares a named output with
    no inline value and assigns it in the calc body. Extraction captures the output
    channel but loses auto-impl: sysml-codegen `b5663c07` drops the body-assignment
    target as a parameter (`extraction/extractor.py:249-264`) and marks the output
    MANUAL_REQUIRED, "no expression AST" (`extraction/expression_compiler.py:265-274`),
    so the modeler must hand-write the stencil body.
    Prefer the inline form `return y : Real = <expr>` / `out attribute y : Real =
    <expr>`. WARNING, so Level 6 stays passing.

    Detection: a NAMED output member (Out/Return, declared name non-empty) with no
    inline value expression, whose name is also carried by a sibling member that
    DOES have a value expression (the body assignment). The inline forms carry the
    value on the output member itself, so they do not fire; an anonymous return
    (no declared name) is C2a's FAIL, not this WARN.

    Returns:
        List of ValidationIssue (WARNING) for body-assignment outputs.
    """
    issues: list[ValidationIssue] = []

    for calc_def in SysideAdapter.elements_of_type(model, "CalculationDefinition"):
        try:
            if not hasattr(calc_def, "owned_members"):
                continue
            members = list(calc_def.owned_members)

            # Names of members carrying a value expression — candidate body assignments.
            valued_names = {
                str(getattr(m, "name", ""))
                for m in members
                if getattr(m, "feature_value_expression", None) is not None
                and str(getattr(m, "name", ""))
            }

            name = get_qualified_name(calc_def)
            for member in members:
                direction = (
                    str(getattr(member, "direction", "")) if hasattr(member, "direction") else ""
                )
                if "Out" not in direction and "Return" not in direction:
                    continue
                declared = getattr(member, "declared_name", None)
                if declared is None or str(declared).strip() == "":
                    continue  # anonymous return -> C2a FAIL, not C2b
                if getattr(member, "feature_value_expression", None) is not None:
                    continue  # inline value -> auto-impl OK
                member_name = str(getattr(member, "name", ""))
                if member_name and member_name in valued_names:
                    issues.append(
                        ValidationIssue(
                            level=6,
                            severity=Severity.WARNING,
                            code=ValidationCode.L6_BODY_ASSIGNMENT_IMPL_LOSS,
                            message=(
                                f"Calc def '{name}' output '{member_name}' is set by body "
                                f"assignment; extraction keeps the channel but loses auto-impl"
                            ),
                            element_name=name,
                            location=get_element_location(calc_def),
                            suggestion=(
                                f"Use the inline form: `return {member_name} : Real = <expr>;` "
                                f"or `out attribute {member_name} : Real = <expr>;`"
                            ),
                        )
                    )
        except Exception as error:
            issues.append(_element_error("check_body_assignment_impl_loss", calc_def, error))

    return issues


def _is_literal_rhs(expr: Any) -> bool:
    """True if a value expression is a literal node per shared SysML expression API."""
    return is_literal_node(expr)


def check_attr_redef_expression_dropped(model: Any) -> list[ValidationIssue]:
    """
    C7 (Item 9): WARN an `attribute :>>` redefinition carrying an expression value.

    Written for an older sysml-codegen whose redefinition scan
    (`hierarchy_resolver._extract_single_redefinition`) read only ReferenceUsage
    members, so a redefinition written WITH the `attribute` keyword (an
    AttributeUsage) was dropped. sysml-codegen `b5663c07` has deleted that scan
    (`tests/helpers/live_extraction.py:9-10`); its current one takes every Feature with
    a qualified name and a value (`elaboration/elaborate.py:832-898`), so both spellings
    are treated alike. The check is kept unchanged under every target; backlog
    L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES decides it. It fires only when the RHS is a
    computed expression; the bare `:>> attr = ...` forms (ReferenceUsage) and the
    `attribute :>> attr = <literal>` form (taught in semantic-operators.md) do NOT
    fire. WARNING severity, so Level 6 stays passing.

    Detection: an AttributeUsage with a non-empty owned_redefinitions and a
    feature_value_expression that is not a literal.

    Returns:
        List of ValidationIssue (WARNING) for dropped attribute-redefinition exprs.
    """
    issues: list[ValidationIssue] = []

    for attr in SysideAdapter.elements_of_type(model, "AttributeUsage"):
        try:
            redefs = getattr(attr, "owned_redefinitions", None)
            if not redefs:
                continue  # a plain typed attribute, not a :>> redefinition
            expr = getattr(attr, "feature_value_expression", None)
            if expr is None:
                continue  # type-only redefinition — nothing to drop
            if _is_literal_rhs(expr):
                continue  # literal AttributeUsage redefine — taught (D5), not warned
            # A redefinition member carries no qualified_name; name it by the
            # redefined feature (falling back to the member's local name).
            redefined = getattr(redefs[0], "redefined_feature", None)
            name = (
                getattr(attr, "name", None)
                or getattr(redefined, "name", None)
                or get_qualified_name(attr)
            )
            issues.append(
                ValidationIssue(
                    level=6,
                    severity=Severity.WARNING,
                    code=ValidationCode.L6_ATTR_REDEF_EXPR_DROPPED,
                    message=(
                        f"Attribute redefinition '{name}' uses the `attribute :>>` form with an "
                        f"expression value; earlier sysml-codegen versions dropped this "
                        f"override at extraction"
                    ),
                    element_name=name,
                    location=get_element_location(attr),
                    suggestion=(
                        "Use the bare `:>> attr = <value>` form (parses as ReferenceUsage and is "
                        "captured), or move the computation into a calc def "
                        "(see semantic-operators.md)"
                    ),
                )
            )
        except Exception as error:
            issues.append(_element_error("check_attr_redef_expression_dropped", attr, error))

    return issues


# --- New orchestrator (combines L7 + L8 + ADR-002) ---


def _target_detail(resolution: TargetResolution) -> dict[str, Any]:
    """The target resolution as the JSON report records it."""
    file: Path | None
    file_value: str | None = None
    match resolution.source:
        case FromFile(path):
            file = path
        case FromOverride(path, value):
            file, file_value = path, value
        case Unset(path):
            file = path
    return {
        "target": resolution.target.value,
        "source": type(resolution.source).__name__,
        "description": describe_target(resolution),
        "root": None if resolution.root is None else str(resolution.root),
        "file": None if file is None else str(file),
        "file_value": file_value,
    }


def _setting_invalid_result(error: TargetSettingError) -> QualityCheckResult:
    """L6 with a broken setting: one `L6_SETTING_INVALID` ERROR, the target metric, no checks."""
    result = QualityCheckResult(
        level=6,
        level_name=LEVEL_NAME,
        success=False,
        metrics={"Execution target": f"invalid ({error.path}; see L6_SETTING_INVALID)"},
        report_detail={
            "target": {
                "target": None,
                "source": "invalid",
                "file": str(error.path),
                "fault": error.fault.value,
                "settings_fault": None
                if error.settings_fault is None
                else error.settings_fault.value,
                "detail": error.detail,
            }
        },
    )
    result.add_issue(
        ValidationIssue(
            level=6,
            severity=Severity.ERROR,
            code=ValidationCode.L6_SETTING_INVALID,
            message=f"execution target setting is invalid; L6 ran no checks: {error.detail}",
            location=str(error.path),
            suggestion=(
                "Fix [tool.agentic-mbse] in pyproject.toml: allowed keys are 'execution-target' "
                'and \'research\'; execution-target is "generated" or "native"'
            ),
            reason_code=error.fault.value
            if error.settings_fault is None
            else error.settings_fault.value,
        )
    )
    return result


_T = TypeVar("_T")


def _guarded(check: str, call: Callable[[], _T]) -> tuple[_T | None, list[ValidationIssue]]:
    """`call()`'s result, or None and one `L6_CHECK_ERROR` naming `check` if it raised (D4)."""
    try:
        return call(), []
    except Exception as error:
        return None, [check_error_issue(check, "the loaded model", error)]


def _run_contract(model: Any) -> tuple[SubsetProfileResult | None, list[ValidationIssue]]:
    """The subset contract's result over the shared model and constraint facts.

    A crash in extraction or evaluation is one `L6_CHECK_ERROR` and no result, so the verdict
    reads "not computed" and every legacy String error stays (design D4, D10).
    """
    return _guarded(
        "subset_profile",
        lambda: evaluate_subset_profile(
            extract_subset_facts(model, constraint_facts=constraint_facts)
        ),
    )


def _run_advisories(model: Any) -> tuple[Advisories | None, list[ValidationIssue]]:
    """The two advisories over the contract's expression sites.

    A walker's own `SemanticEvidenceError` is an advisory-unverified record inside the result
    (D15); any other exception is one `L6_CHECK_ERROR` and no result.
    """
    return _guarded("subset_advisories", lambda: extract_advisories(model))


# The legacy checks in the order they run (D13 prints their issues in this order), each with
# the issue codes it emits, so a failed check's counts read "not computed" (Appendix B).
_LEGACY_CHECKS: tuple[
    tuple[Callable[[Any], list[ValidationIssue]], tuple[ValidationCode, ...]], ...
] = (
    (check_calc_def_locations, (ValidationCode.V1_CALC_DEF_LOCATION,)),
    (check_static_expressions, (ValidationCode.V2_DYNAMIC_EXPRESSION,)),
    (check_supported_operators, (ValidationCode.V4_UNSUPPORTED_OPERATOR,)),
    (check_static_function_invocations, (ValidationCode.V4_STATIC_FUNCTION_INVOCATION,)),
    (
        check_qualified_names,
        (ValidationCode.L6_MISSING_QUALIFIED_NAME, ValidationCode.L6_INVALID_QUALIFIED_NAME),
    ),
    (
        check_calc_def_structure,
        (ValidationCode.L6_CALC_DEF_NO_OUTPUT, ValidationCode.L6_CALC_DEF_NO_DIRECTION),
    ),
    (check_anonymous_returns, (ValidationCode.L6_ANONYMOUS_RETURN,)),
    (check_body_assignment_impl_loss, (ValidationCode.L6_BODY_ASSIGNMENT_IMPL_LOSS,)),
    (
        check_constraint_executability,
        (
            ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL,
            ValidationCode.L6_CONSTRAINT_NON_NUMERICAL,
        ),
    ),
    (check_calc_bearing_instantiation, (ValidationCode.L6_CALC_DEF_NO_INSTANTIATION,)),
    (check_attr_redef_expression_dropped, (ValidationCode.L6_ATTR_REDEF_EXPR_DROPPED,)),
)

# The per-code count metrics, in their printed order.
_COUNTED_CODES = (
    ValidationCode.L6_MISSING_QUALIFIED_NAME,
    ValidationCode.L6_INVALID_QUALIFIED_NAME,
    ValidationCode.L6_CALC_DEF_NO_OUTPUT,
    ValidationCode.L6_CALC_DEF_NO_DIRECTION,
    ValidationCode.L6_INVALID_BINDING_FORMAT,
    ValidationCode.L6_DESIGN_ATTR_INCOMPLETE,
    ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE,
    ValidationCode.L6_ANONYMOUS_RETURN,
    ValidationCode.L6_BODY_ASSIGNMENT_IMPL_LOSS,
    ValidationCode.V4_STATIC_FUNCTION_INVOCATION,
    ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL,
    ValidationCode.L6_CONSTRAINT_NON_NUMERICAL,
    ValidationCode.L6_CALC_DEF_NO_INSTANTIATION,
    ValidationCode.L6_ATTR_REDEF_EXPR_DROPPED,
)

NOT_COMPUTED = "not computed"


def _reported_failure(issues: list[ValidationIssue]) -> bool:
    return any(issue.code is ValidationCode.L6_CHECK_ERROR for issue in issues)


def _count(value: int | None, failed: bool) -> int | str:
    """A count metric: the number, or "not computed" when its check reported a failure."""
    return NOT_COMPUTED if value is None or failed else value


def _element_count(model: Any, type_name: str) -> int:
    return len(list(SysideAdapter.elements_of_type(model, type_name)))


def _count_elements(model: Any, type_name: str) -> tuple[int | None, list[ValidationIssue]]:
    """The model's number of `type_name` elements, or None and one `L6_CHECK_ERROR`."""
    return _guarded(f"count of {type_name}", partial(_element_count, model, type_name))


def validate_architecture(
    models_path: str,
    design_path_filter: str | None = "designs",
    execution_target: Target | None = None,
) -> QualityCheckResult:
    """
    Main entry point for Level 6 validation.

    Runs the generator subset contract first, then the ADR-002, codegen and manifest checks,
    over one loaded model, and shows the contract's result through the execution target
    (Item 3 design, Core Concept).

    Args:
        models_path: Path to models directory
        design_path_filter: Path component to filter design attribute checks.
            Only files whose path contains this component are checked.
            Use None or empty string to check all files.
        execution_target: `--execution-target` (generated or native), or None to read the
            project's `[tool.agentic-mbse] execution-target` (Item 3 design D3)

    Returns:
        QualityCheckResult with the architecture and generator subset issues
    """
    print_header(LEVEL_NAME, 6)

    # The target comes first: a broken setting stops L6 before any check runs (D3).
    resolution = resolve_target(Path(models_path), execution_target)
    if isinstance(resolution, TargetSettingError):
        return _setting_invalid_result(resolution)
    target_metrics = {"Execution target": describe_target(resolution)}
    target_detail = {"target": _target_detail(resolution)}

    # Discover SysML files
    try:
        files = discover_sysml_files(models_path)
    except ValueError as e:
        return QualityCheckResult(
            level=6,
            level_name=LEVEL_NAME,
            success=False,
            issues=[str(e)],
        )

    if not files:
        return QualityCheckResult(
            level=6,
            level_name=LEVEL_NAME,
            success=True,
            warnings=["No SysML files found"],
            metrics={**target_metrics, "Files checked": 0},
            report_detail=target_detail,
        )

    # Load model
    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=6,
            level_name=LEVEL_NAME,
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

    # The contract runs first: its String subjects feed the design-attribute check (D10).
    contract, contract_errors = _run_contract(model)
    all_issues: list[ValidationIssue] = list(contract_errors)

    num_calc_defs, count_errors = _count_elements(model, "CalculationDefinition")
    all_issues.extend(count_errors)
    num_calc_usages, count_errors = _count_elements(model, "CalculationUsage")
    all_issues.extend(count_errors)

    # ADR-002, codegen and Item 12 checks, each wrapped so an escaped exception names it (D4).
    uncounted: set[ValidationCode] = set()
    for check, codes in _LEGACY_CHECKS:
        found, errors = _guarded(check.__name__, partial(check, model))
        issues = errors + (found or [])
        if _reported_failure(issues):
            uncounted.update(codes)
        all_issues.extend(issues)
    bindings, errors = _guarded("check_binding_formats", lambda: check_binding_formats(model))
    binding_issues, num_bindings = bindings or ([], None)
    binding_issues = errors + binding_issues
    if _reported_failure(binding_issues):
        uncounted.add(ValidationCode.L6_INVALID_BINDING_FORMAT)
    all_issues.extend(binding_issues)
    design_attrs, errors = _guarded(
        "check_design_attr_completeness",
        lambda: check_design_attr_completeness(
            model, design_path_filter=design_path_filter, string_subjects=string_subjects(contract)
        ),
    )
    design_attr_issues, num_design_attrs = design_attrs or ([], None)
    design_attr_issues = errors + design_attr_issues
    if _reported_failure(design_attr_issues):
        uncounted.update(
            (ValidationCode.L6_DESIGN_ATTR_INCOMPLETE, ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE)
        )
    all_issues.extend(design_attr_issues)

    # The advisories run after the legacy checks (D12, D15).
    advisories, advisory_errors = _run_advisories(model)
    all_issues.extend(advisory_errors)

    # Manifest checks (from old L7)
    manifests, manifest_errors = _guarded(
        "manifest_checks", partial(_check_manifests, models_path, model)
    )
    manifest_issues, manifests_checked = manifests or ([], None)
    all_issues.extend(manifest_errors)

    shown = present(resolution.target, contract, advisories, all_issues)

    # ERROR-only failure criteria (matches old L8 behavior), over the issues as shown.
    # Manifest issues are unstructured strings; also fail if any found
    success = not any(i.severity == Severity.ERROR for i in shown.issues)
    if manifest_issues:
        success = False

    code_counts: dict[str, int | str] = {
        code.value: _count(sum(1 for i in all_issues if i.code is code), failed=code in uncounted)
        for code in _COUNTED_CODES
    }
    result = QualityCheckResult(
        level=6,
        level_name=LEVEL_NAME,
        success=success,
        summarized=shown.summarized,
        pass_note=shown.pass_note if success else "",
        report_detail={**target_detail, **shown.profile},
        metrics={
            **target_metrics,
            **shown.metrics,
            "Calc defs checked": _count(num_calc_defs, failed=False),
            "Calc usages checked": _count(num_calc_usages, failed=False),
            "Bindings validated": _count(
                num_bindings, failed=ValidationCode.L6_INVALID_BINDING_FORMAT in uncounted
            ),
            "Design attrs checked": _count(
                num_design_attrs, failed=ValidationCode.L6_DESIGN_ATTR_INCOMPLETE in uncounted
            ),
            "Manifests checked": _count(manifests_checked, failed=False),
            **code_counts,
        },
    )

    # Add structured issues, in the order D13 gives them
    for issue in shown.issues:
        result.add_issue(issue)

    # Add manifest issues (unstructured strings)
    for issue_str in manifest_issues:
        result.issues.append(issue_str)

    return result

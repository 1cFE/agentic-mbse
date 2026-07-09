#!/usr/bin/env python3
"""
Level 6: Architecture & Pipeline Readiness

Application-specific validation: ADR-002 rules, manifest subsystem
checks, and codegen readiness requirements.

Merged from:
- Level 7 (Architectural Integrity): manifest-based subsystem validation
- Level 8 (Codegen Readiness): qualified names, calc def structure,
  binding formats, design attr completeness/extractability
- ADR-002 calls (previously in Level 2)
"""

from pathlib import Path
from typing import Any

import yaml

from agentic_mbse.sysml.expression import (
    evaluate_true_static_expression,
    is_literal_node,
)
from agentic_mbse.sysml.syside_adapter import (
    EXCLUDED_CONSTRAINT_TYPES,
    SysideAdapter,
)
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue

from .adr002 import (
    check_calc_def_locations,
    check_static_expressions,
    check_static_function_invocations,
    check_supported_operators,
)
from .common import (
    QualityCheckResult,
    discover_sysml_files,
    get_element_location,
    get_qualified_name,
    load_sysml_model,
    print_header,
)

# --- Functions from L7 (manifest validation) ---


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
        manifest = load_manifest(manifest_path.parent)
        if manifest:
            missing = check_subsystem_composition(model, manifest)
            for subsystem in missing:
                issues.append(f"Missing subsystem '{subsystem}' in {manifest_path.parent.name}")
    return issues, len(manifests_found)


# --- Functions from L8 (codegen readiness) ---


def _segment_is_quoted(segment: str) -> bool:
    """Whether a `::`-delimited name segment is a quoted name (e.g. 'Trap Plant').

    C6b (Item 12): codegen's Item-5 sanitization turns a quoted name into a valid
    Python identifier (`'Trap Plant'` -> `Trap_Plant`), so a space inside a quoted
    segment is legal, not a malformed qualified name. Only an *unquoted* space is a
    real EQN-derivation failure.
    """
    s = segment.strip()
    return len(s) >= 2 and s.startswith("'") and s.endswith("'")


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

    # Check CalculationDefinitions
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
                # A space inside a quoted segment is legal (C6b, sanitized by codegen).
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
        except AttributeError:
            element_name = getattr(calc_def, "name", "<unnamed>")
            issues.append(
                ValidationIssue(
                    level=6,
                    severity=Severity.ERROR,
                    code=ValidationCode.L6_MISSING_QUALIFIED_NAME,
                    message=f"Calc def '{element_name}' missing qualified_name attribute",
                    element_name=str(element_name),
                    location=get_element_location(calc_def),
                )
            )

    # Check CalculationUsages (EQN derivability)
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
        except AttributeError:
            element_name = str(getattr(calc_usage, "name", "<unnamed>"))
            issues.append(
                ValidationIssue(
                    level=6,
                    severity=Severity.ERROR,
                    code=ValidationCode.L6_MISSING_QUALIFIED_NAME,
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
    - At least one output parameter (direction = Out/Return)
    - Input parameters have direction markers

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

        except Exception:
            continue

    return issues


def _extract_chain_path(expr: Any) -> str | None:
    """Extract dotted path from FeatureChainExpression."""
    try:
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
    - REFERENCE bindings use :: separator (or simple names)
    - CHAIN bindings use . separator

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
    - Design attrs in designs/ have feature_value_expression or binding
    - Design attrs with values produce extractable numeric defaults

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
            doc = attr.document
            if not doc or not hasattr(doc, "url"):
                continue
            doc_path = Path(str(doc.url))
            if design_path_filter:
                if design_path_filter not in doc_path.parts:
                    continue

            owner = attr.owner if hasattr(attr, "owner") else None
            if owner:
                try:
                    if SysideAdapter.is_instance(owner, "CalculationUsage"):
                        continue
                except Exception:
                    pass

            attrs_checked += 1
            attr_name = get_qualified_name(attr)
            location = get_element_location(attr)

            has_value = (
                hasattr(attr, "feature_value_expression")
                and attr.feature_value_expression is not None
            )

            if has_value:
                try:
                    evaluate_true_static_expression(attr.feature_value_expression)
                except (ValueError, TypeError) as e:
                    issues.append(
                        ValidationIssue(
                            level=6,
                            severity=Severity.ERROR,
                            code=ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE,
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
                        level=6,
                        severity=Severity.ERROR,
                        code=ValidationCode.L6_DESIGN_ATTR_INCOMPLETE,
                        message=f"Design attribute '{attr_name}' has no value or binding",
                        element_name=attr_name,
                        location=location,
                        suggestion="Add '= <value>' or bind to calc output",
                    )
                )

        except Exception:
            continue

    return issues, attrs_checked


def check_anonymous_returns(model: Any) -> list[ValidationIssue]:
    """
    C2a (Item 12): FAIL a calc def with an anonymous `return`.

    An anonymous `return : Real = <expr>` has no declared name (syside synthesizes
    `result`, but declared_name is empty), so codegen derives no output channel from
    it. Mirrors codegen's V8 diagnostic. The named forms — `out attribute`, named
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
        except Exception:
            continue

    return issues


def check_constraint_executability(model: Any) -> list[ValidationIssue]:
    """
    C3 (Item 12): WARN that constraint usages are not executable.

    A model carrying constraint usages should warn that constraints are dropped at
    extraction — they document intent but produce no computation. WARNING severity,
    so it does not fail Level 6. Points at modeling-assumptions §8.

    Returns:
        List of ValidationIssue (WARNING), one per constraint usage.
    """
    issues: list[ValidationIssue] = []

    # Row 7 (Item 4): sweep ConstraintUsage subtypes so `assert` is seen, and
    # exclude requirement-side usages via the single droppable policy. D7: the
    # old `except Exception: constraints = []` swallow is removed — an extraction
    # failure here must be loud, not silently collapse to "zero constraints" and
    # mask this very fix.
    constraints = list(
        SysideAdapter.elements_of_type(
            model,
            "ConstraintUsage",
            include_subtypes=True,
            exclude=EXCLUDED_CONSTRAINT_TYPES,
        )
    )

    for constraint in constraints:
        try:
            name = get_qualified_name(constraint)
            issues.append(
                ValidationIssue(
                    level=6,
                    severity=Severity.WARNING,
                    code=ValidationCode.L6_CONSTRAINT_NON_EXECUTABLE,
                    message=(f"Constraint '{name}' is not executable and is dropped at extraction"),
                    element_name=name,
                    location=get_element_location(constraint),
                    suggestion=(
                        "Constraints document intent only; move any needed computation into a "
                        "calc def (see modeling-assumptions §8)"
                    ),
                )
            )
        except Exception:
            continue

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
    instantiated: set[str] = set()
    try:
        for part_usage in SysideAdapter.elements_of_type(model, "PartUsage"):
            for typ in getattr(part_usage, "types", []) or []:
                type_name = getattr(typ, "name", None)
                if type_name:
                    instantiated.add(str(type_name))
    except Exception:
        pass

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
        except Exception:
            continue

    return issues


def check_body_assignment_impl_loss(model: Any) -> list[ValidationIssue]:
    """
    C2b (Item 12): WARN a calc def output computed by body assignment.

    The form `return attribute y : Real; y = <expr>` declares a named output with
    no inline value and assigns it in the calc body. Extraction captures the output
    channel but loses auto-impl — codegen cannot recover the expression until its
    deferred-capture support lands, so the modeler must hand-write the stencil body.
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
        except Exception:
            continue

    return issues


def _is_literal_rhs(expr: Any) -> bool:
    """True if a value expression is a literal node per shared SysML expression API."""
    return is_literal_node(expr)


def check_attr_redef_expression_dropped(model: Any) -> list[ValidationIssue]:
    """
    C7 (Item 9): WARN an `attribute :>>` redefinition carrying an expression value.

    Codegen's redefinition scan (hierarchy_resolver._extract_single_redefinition)
    reads only ReferenceUsage members, so a redefinition written WITH the
    `attribute` keyword parses as an AttributeUsage and is silently dropped — its
    override never reaches the pipeline. This fires only when the dropped RHS is a
    computed expression (the dangerous case, where no supported one-line rewrite
    exists). The two forms codegen accepts or teaches do NOT fire:
    - the bare `:>> attr = <literal>` / bare `:>> attr = <expr>` forms parse as
      ReferenceUsage and are captured (D1 mechanism b);
    - the `attribute :>> attr = <literal>` form is an AttributeUsage too, but is
      taught in semantic-operators.md (use the bare form) rather than warned — the
      prior-epic C7 boundary is expression-vs-literal.

    WARNING severity, so Level 6 stays passing. Mirrors semantic-operators.md
    "attribute :>> with an expression is dropped".

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
                        f"expression value; codegen scans only ReferenceUsage redefinitions, so "
                        f"this override is silently dropped at extraction"
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
        except Exception:
            continue

    return issues


# --- New orchestrator (combines L7 + L8 + ADR-002) ---


def validate_architecture(
    models_path: str,
    design_path_filter: str | None = "designs",
) -> QualityCheckResult:
    """
    Main entry point for Level 6 validation.

    Combines ADR-002 checks, manifest subsystem validation, and
    codegen readiness checks into a single architecture level.

    Args:
        models_path: Path to models directory
        design_path_filter: Path component to filter design attribute checks.
            Only files whose path contains this component are checked.
            Use None or empty string to check all files.

    Returns:
        QualityCheckResult with architecture & pipeline readiness issues
    """
    print_header("Architecture & Pipeline Readiness", 6)

    # Discover SysML files
    try:
        files = discover_sysml_files(models_path)
    except ValueError as e:
        return QualityCheckResult(
            level=6,
            level_name="Architecture & Pipeline Readiness",
            success=False,
            issues=[str(e)],
        )

    if not files:
        return QualityCheckResult(
            level=6,
            level_name="Architecture & Pipeline Readiness",
            success=True,
            warnings=["No SysML files found"],
            metrics={"Files checked": 0},
        )

    # Load model
    try:
        model, diagnostics = load_sysml_model(files)
    except Exception as e:
        return QualityCheckResult(
            level=6,
            level_name="Architecture & Pipeline Readiness",
            success=False,
            issues=[f"Failed to load model: {e}"],
        )

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

    # ADR-002 checks (from old L2)
    all_issues.extend(check_calc_def_locations(model))
    all_issues.extend(check_static_expressions(model))
    all_issues.extend(check_supported_operators(model))
    all_issues.extend(check_static_function_invocations(model))  # C5 (Item 12)

    # Codegen readiness checks (from old L8)
    all_issues.extend(check_qualified_names(model))
    all_issues.extend(check_calc_def_structure(model))

    # Item 12 architecture checks (mirror codegen's shipped behavior)
    all_issues.extend(check_anonymous_returns(model))
    all_issues.extend(check_body_assignment_impl_loss(model))
    all_issues.extend(check_constraint_executability(model))
    all_issues.extend(check_calc_bearing_instantiation(model))
    all_issues.extend(check_attr_redef_expression_dropped(model))  # C7 (Item 9)
    binding_issues, num_bindings = check_binding_formats(model)
    all_issues.extend(binding_issues)
    design_attr_issues, num_design_attrs = check_design_attr_completeness(
        model, design_path_filter=design_path_filter
    )
    all_issues.extend(design_attr_issues)

    # Manifest checks (from old L7)
    manifest_issues, manifests_checked = _check_manifests(models_path, model)

    # Build result — ERROR-only failure criteria (matches old L8 behavior)
    # Manifest issues are unstructured strings; also fail if any found
    success = not any(i.severity == Severity.ERROR for i in all_issues)
    if manifest_issues:
        success = False

    result = QualityCheckResult(
        level=6,
        level_name="Architecture & Pipeline Readiness",
        success=success,
        metrics={
            "Calc defs checked": num_calc_defs,
            "Calc usages checked": num_calc_usages,
            "Bindings validated": num_bindings,
            "Design attrs checked": num_design_attrs,
            "Manifests checked": manifests_checked,
            "L6_MISSING_QUALIFIED_NAME": len(
                [i for i in all_issues if i.code == ValidationCode.L6_MISSING_QUALIFIED_NAME]
            ),
            "L6_INVALID_QUALIFIED_NAME": len(
                [i for i in all_issues if i.code == ValidationCode.L6_INVALID_QUALIFIED_NAME]
            ),
            "L6_CALC_DEF_NO_OUTPUT": len(
                [i for i in all_issues if i.code == ValidationCode.L6_CALC_DEF_NO_OUTPUT]
            ),
            "L6_CALC_DEF_NO_DIRECTION": len(
                [i for i in all_issues if i.code == ValidationCode.L6_CALC_DEF_NO_DIRECTION]
            ),
            "L6_INVALID_BINDING_FORMAT": len(
                [i for i in all_issues if i.code == ValidationCode.L6_INVALID_BINDING_FORMAT]
            ),
            "L6_DESIGN_ATTR_INCOMPLETE": len(
                [i for i in all_issues if i.code == ValidationCode.L6_DESIGN_ATTR_INCOMPLETE]
            ),
            "L6_DESIGN_ATTR_UNEXTRACTABLE": len(
                [i for i in all_issues if i.code == ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE]
            ),
            "L6_ANONYMOUS_RETURN": len(
                [i for i in all_issues if i.code == ValidationCode.L6_ANONYMOUS_RETURN]
            ),
            "L6_BODY_ASSIGNMENT_IMPL_LOSS": len(
                [i for i in all_issues if i.code == ValidationCode.L6_BODY_ASSIGNMENT_IMPL_LOSS]
            ),
            "V4_STATIC_FUNCTION_INVOCATION": len(
                [i for i in all_issues if i.code == ValidationCode.V4_STATIC_FUNCTION_INVOCATION]
            ),
            "L6_CONSTRAINT_NON_EXECUTABLE": len(
                [i for i in all_issues if i.code == ValidationCode.L6_CONSTRAINT_NON_EXECUTABLE]
            ),
            "L6_CALC_DEF_NO_INSTANTIATION": len(
                [i for i in all_issues if i.code == ValidationCode.L6_CALC_DEF_NO_INSTANTIATION]
            ),
            "L6_ATTR_REDEF_EXPR_DROPPED": len(
                [i for i in all_issues if i.code == ValidationCode.L6_ATTR_REDEF_EXPR_DROPPED]
            ),
        },
    )

    # Add structured issues
    for issue in all_issues:
        result.add_issue(issue)

    # Add manifest issues (unstructured strings)
    for issue_str in manifest_issues:
        result.issues.append(issue_str)

    return result

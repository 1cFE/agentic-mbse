#!/usr/bin/env python3
"""
Level 6: Architecture & Conventions

Application-specific validation: ADR-002 rules, manifest subsystem checks, design
attribute completeness and constraint executability. L6 holds no copy of a generator
check (ADR 0006); whether a model generates is `sysml-codegen check`'s answer, not L6's.
"""

from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any, TypeVar

import yaml

from agentic_mbse.sysml.executable_profile import Eligibility, evaluate_identified_profile
from agentic_mbse.sysml.expression import (
    Unextractable,
    evaluate_true_static_expression,
)
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
    UNSET_NOTE,
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

LEVEL_NAME = "Architecture & Conventions"


def generation_note(models_path: str) -> str:
    """The line every run that includes L6 ends with, pass or fail: L6 makes no generation claim."""
    return (
        "L6 does not check whether the model generates. For that, run "
        f"`uv run sysml-codegen check --models {models_path}` "
        '(modeling_project/MODELING_PROCESS.md, "Generated code").'
    )


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


def _element_error(check: str, element: Any, error: Exception) -> ValidationIssue:
    """`L6_CHECK_ERROR` for one element `check` could not inspect (design D4, element scope)."""
    return check_error_issue(
        check, get_qualified_name(element), error, get_element_location(element)
    )


def _enumeration_error(check: str, type_name: str, error: Exception) -> ValidationIssue:
    """`L6_CHECK_ERROR` for a check that could not list its elements (D4, check scope)."""
    return check_error_issue(check, f"the model's {type_name} elements", error)


def check_calc_def_structure(model: Any) -> list[ValidationIssue]:
    """
    Warn on calc def parameters that carry no direction marker.

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

            params_without_direction: list[str] = []

            for member in calc_def.owned_members:
                if not hasattr(member, "name"):
                    continue

                member_name = str(member.name) if member.name else "<unnamed>"

                has_direction = hasattr(member, "direction") and member.direction
                if not has_direction and hasattr(member, "typing"):
                    params_without_direction.append(member_name)

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


def check_design_attr_completeness(
    model: Any,
    design_path_filter: str | None = "designs",
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

    Returns:
        Tuple of (list of ValidationIssue, count of design attrs checked)
    """
    issues: list[ValidationIssue] = []
    attrs_checked = 0

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
                # D3 (L6-EXPOSE-CONSISTENCY): an EXPOSE binding is complete. Its value
                # comes from the bound source, so it needs no numeric default and the
                # static evaluator does not apply.
                if is_expose_binding(attr, attr.feature_value_expression):
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


# The checks in the order they run (their issues print in this order), each with
# the issue codes it emits, so a failed check's counts read "not computed" (Appendix B).
_CHECKS: tuple[tuple[Callable[[Any], list[ValidationIssue]], tuple[ValidationCode, ...]], ...] = (
    (check_calc_def_locations, (ValidationCode.V1_CALC_DEF_LOCATION,)),
    (check_static_expressions, (ValidationCode.V2_DYNAMIC_EXPRESSION,)),
    (check_supported_operators, (ValidationCode.V4_UNSUPPORTED_OPERATOR,)),
    (check_static_function_invocations, (ValidationCode.V4_STATIC_FUNCTION_INVOCATION,)),
    (check_calc_def_structure, (ValidationCode.L6_CALC_DEF_NO_DIRECTION,)),
    (
        check_constraint_executability,
        (
            ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL,
            ValidationCode.L6_CONSTRAINT_NON_NUMERICAL,
        ),
    ),
)

# The per-code count metrics, in their printed order.
_COUNTED_CODES = (
    ValidationCode.L6_CALC_DEF_NO_DIRECTION,
    ValidationCode.L6_DESIGN_ATTR_INCOMPLETE,
    ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE,
    ValidationCode.V4_STATIC_FUNCTION_INVOCATION,
    ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL,
    ValidationCode.L6_CONSTRAINT_NON_NUMERICAL,
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


def _target_note(target: Target) -> dict[str, str]:
    """The metric line the target adds: the unset note, or nothing."""
    if target is Target.UNSET:
        return {"Execution target note": UNSET_NOTE}
    return {}


def validate_architecture(
    models_path: str,
    design_path_filter: str | None = "designs",
    execution_target: Target | None = None,
) -> QualityCheckResult:
    """
    Main entry point for Level 6 validation.

    Runs the ADR-002, convention and manifest checks over one loaded model. The execution
    target is reported, never used to change a result.

    Args:
        models_path: Path to models directory
        design_path_filter: Path component to filter design attribute checks.
            Only files whose path contains this component are checked.
            Use None or empty string to check all files.
        execution_target: `--execution-target` (generated or native), or None to read the
            project's `[tool.agentic-mbse] execution-target` (Item 3 design D3)

    Returns:
        QualityCheckResult with the architecture and convention issues
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
            metrics=target_metrics,
            report_detail=target_detail,
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
            metrics=target_metrics,
            report_detail=target_detail,
        )

    num_calc_defs, count_errors = _count_elements(model, "CalculationDefinition")
    all_issues: list[ValidationIssue] = list(count_errors)
    num_calc_usages, count_errors = _count_elements(model, "CalculationUsage")
    all_issues.extend(count_errors)

    # ADR-002 and convention checks, each wrapped so an escaped exception names it (D4).
    uncounted: set[ValidationCode] = set()
    for check, codes in _CHECKS:
        found, errors = _guarded(check.__name__, partial(check, model))
        issues = errors + (found or [])
        if _reported_failure(issues):
            uncounted.update(codes)
        all_issues.extend(issues)
    design_attrs, errors = _guarded(
        "check_design_attr_completeness",
        lambda: check_design_attr_completeness(model, design_path_filter=design_path_filter),
    )
    design_attr_issues, num_design_attrs = design_attrs or ([], None)
    design_attr_issues = errors + design_attr_issues
    if _reported_failure(design_attr_issues):
        uncounted.update(
            (ValidationCode.L6_DESIGN_ATTR_INCOMPLETE, ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE)
        )
    all_issues.extend(design_attr_issues)

    # Manifest checks (from old L7)
    manifests, manifest_errors = _guarded(
        "manifest_checks", partial(_check_manifests, models_path, model)
    )
    manifest_issues, manifests_checked = manifests or ([], None)
    all_issues.extend(manifest_errors)

    # ERROR-only failure criteria.
    # Manifest issues are unstructured strings; also fail if any found
    success = not any(i.severity == Severity.ERROR for i in all_issues)
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
        report_detail=target_detail,
        metrics={
            **target_metrics,
            **_target_note(resolution.target),
            "Calc defs checked": _count(num_calc_defs, failed=False),
            "Calc usages checked": _count(num_calc_usages, failed=False),
            "Design attrs checked": _count(
                num_design_attrs, failed=ValidationCode.L6_DESIGN_ATTR_INCOMPLETE in uncounted
            ),
            "Manifests checked": _count(manifests_checked, failed=False),
            **code_counts,
        },
    )

    for issue in all_issues:
        result.add_issue(issue)

    # Add manifest issues (unstructured strings)
    for issue_str in manifest_issues:
        result.issues.append(issue_str)

    return result

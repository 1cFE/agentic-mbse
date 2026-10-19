"""Every L6 exception site reports `L6_CHECK_ERROR` and makes no dependent finding (Item 3 Phase 7).

Spec § Check failures fail under every target, bullets 1 and 2; design Appendix B, D4, D16.
One site per Appendix B row (lines reconciled to the current files in the plan's Phase 7
notes). Each site is forced on one real fixture model
(`tests/fixtures/l6/check_errors/models/`): an `elements_of_type` or `is_instance` call made by
the named function raises, or an element that function lists raises when it reads one
attribute. Nothing else in the model changes, so the fixture's own two findings
(`L6_DESIGN_ATTR_UNEXTRACTABLE` on `scaled`, `L6_DESIGN_ATTR_INCOMPLETE` on `unset`) show
what a site would have reported.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml import expression
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import ValidationCode
from agentic_mbse.validation import adr002, level6_architecture
from agentic_mbse.validation.common import QualityCheckResult
from agentic_mbse.validation.execution_target import Target
from tests.helpers.l6_projects import make_project, target_table

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "l6" / "check_errors" / "models"
TARGETS = ["unset", "generated", "native"]
CHECK_ERROR = ValidationCode.L6_CHECK_ERROR
UNEXTRACTABLE = ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE
INCOMPLETE = ValidationCode.L6_DESIGN_ATTR_INCOMPLETE


class ForcedError(RuntimeError):
    """The exception a test forces at one site."""


class _Exploding:
    """An element whose read of `attribute` raises; every other read goes to the real one."""

    def __init__(self, inner: Any, attribute: str, error: type[Exception]) -> None:
        object.__setattr__(self, "_inner", inner)
        object.__setattr__(self, "_attribute", attribute)
        object.__setattr__(self, "_error", error)

    def __getattr__(self, name: str) -> Any:
        if name == self._attribute:
            raise self._error(f"forced read of {name}")
        return getattr(self._inner, name)


def _caller() -> str:
    return sys._getframe(2).f_code.co_name


def _patch_enumeration(
    monkeypatch: pytest.MonkeyPatch,
    function: str,
    type_name: str,
    wrap: Callable[[Any], Any] | None,
) -> None:
    """`elements_of_type(model, type_name)` called by `function` raises, or wraps each element."""
    real = SysideAdapter.elements_of_type

    def elements_of_type(model: Any, name: str, **kwargs: Any) -> Iterator[Any]:
        if _caller() == function and name == type_name:
            if wrap is None:
                raise ForcedError(f"forced enumeration of {name}")
            return iter([wrap(element) for element in real(model, name, **kwargs)])
        return real(model, name, **kwargs)

    monkeypatch.setattr(SysideAdapter, "elements_of_type", staticmethod(elements_of_type))


def _patch_is_instance(monkeypatch: pytest.MonkeyPatch, function: str, type_name: str) -> None:
    """`is_instance(element, type_name)` called by `function` raises."""
    real = SysideAdapter.is_instance

    def is_instance(element: Any, name: str) -> bool:
        if _caller() == function and name == type_name:
            raise ForcedError(f"forced type test for {name}")
        return real(element, name)

    monkeypatch.setattr(SysideAdapter, "is_instance", staticmethod(is_instance))


@dataclass(frozen=True)
class Site:
    """One Appendix B row: where it is, how to force it, what must and must not appear."""

    where: str
    check: str
    force: Callable[[pytest.MonkeyPatch], None]
    no_finding: frozenset[ValidationCode] = frozenset()
    # The element whose inspection failed, when only its findings depend on the failure.
    subject: str | None = None

    def __str__(self) -> str:
        return self.where


def enumeration(function: str, type_name: str) -> Callable[[pytest.MonkeyPatch], None]:
    return lambda mp: _patch_enumeration(mp, function, type_name, None)


def element(
    function: str, type_name: str, attribute: str, error: type[Exception] = ForcedError
) -> Callable[[pytest.MonkeyPatch], None]:
    return lambda mp: _patch_enumeration(
        mp, function, type_name, lambda e: _Exploding(e, attribute, error)
    )


def type_test(function: str, type_name: str) -> Callable[[pytest.MonkeyPatch], None]:
    return lambda mp: _patch_is_instance(mp, function, type_name)


def raising(module: Any, name: str, error: Exception) -> Callable[[pytest.MonkeyPatch], None]:
    def force(mp: pytest.MonkeyPatch) -> None:
        def broken(*args: Any, **kwargs: Any) -> Any:
            raise error

        mp.setattr(module, name, broken)

    return force


QN = frozenset({ValidationCode.L6_MISSING_QUALIFIED_NAME, ValidationCode.L6_INVALID_QUALIFIED_NAME})
EXPOSE_DEPENDENT = frozenset(
    {ValidationCode.V2_DYNAMIC_EXPRESSION, ValidationCode.V4_UNSUPPORTED_OPERATOR, UNEXTRACTABLE}
)

SITES = [
    # level6_architecture.py (Appendix B line at ebb3d467 -> function)
    Site(
        ":191 qualified-name defs listed",
        "check_qualified_names",
        enumeration("check_qualified_names", "CalculationDefinition"),
        QN,
    ),
    Site(
        ":230 qualified-name read (AttributeError)",
        "check_qualified_names",
        element("check_qualified_names", "CalculationDefinition", "qualified_name", AttributeError),
        QN,
    ),
    Site(
        ":246 qualified-name usages listed",
        "check_qualified_names",
        enumeration("check_qualified_names", "CalculationUsage"),
        QN,
    ),
    Site(
        ":289 usage qualified-name read (AttributeError)",
        "check_qualified_names",
        element("check_qualified_names", "CalculationUsage", "qualified_name", AttributeError),
        QN,
    ),
    Site(
        ":320 calc def structure listed",
        "check_calc_def_structure",
        enumeration("check_calc_def_structure", "CalculationDefinition"),
    ),
    Site(
        ":374 calc def structure per def",
        "check_calc_def_structure",
        element("check_calc_def_structure", "CalculationDefinition", "owned_members"),
    ),
    Site(
        ":418 binding formats listed",
        "check_binding_formats",
        enumeration("check_binding_formats", "CalculationUsage"),
    ),
    Site(
        ":470 binding formats per usage",
        "check_binding_formats",
        element("check_binding_formats", "CalculationUsage", "owned_members"),
    ),
    Site(
        ":502 design attrs listed",
        "check_design_attr_completeness",
        enumeration("check_design_attr_completeness", "AttributeUsage"),
        frozenset({UNEXTRACTABLE, INCOMPLETE}),
    ),
    Site(
        ":520 design attr owner type test",
        "check_design_attr_completeness",
        type_test("check_design_attr_completeness", "CalculationUsage"),
        frozenset({UNEXTRACTABLE, INCOMPLETE}),
    ),
    Site(
        ":540 static evaluator fails (not its own signal)",
        "check_design_attr_completeness",
        raising(
            level6_architecture, "evaluate_true_static_expression", ForcedError("evaluator bug")
        ),
        frozenset({UNEXTRACTABLE}),
    ),
    Site(
        ":572 design attrs per attribute",
        "check_design_attr_completeness",
        element("check_design_attr_completeness", "AttributeUsage", "document"),
        frozenset({UNEXTRACTABLE, INCOMPLETE}),
    ),
    Site(
        ":623 anonymous returns per def",
        "check_anonymous_returns",
        element("check_anonymous_returns", "CalculationDefinition", "owned_members"),
    ),
    Site(
        "new: anonymous returns listed (no try of its own)",
        "check_anonymous_returns",
        enumeration("check_anonymous_returns", "CalculationDefinition"),
    ),
    Site(
        "new: constraint executability",
        "check_constraint_executability",
        raising(level6_architecture, "evaluate_identified_profile", ForcedError("profile bug")),
    ),
    Site(
        ":723 instantiated set",
        "check_calc_bearing_instantiation",
        enumeration("check_calc_bearing_instantiation", "PartUsage"),
        frozenset({ValidationCode.L6_CALC_DEF_NO_INSTANTIATION}),
    ),
    Site(
        ":759 instantiation per part def",
        "check_calc_bearing_instantiation",
        element("check_calc_bearing_instantiation", "PartDefinition", "owned_members"),
        frozenset({ValidationCode.L6_CALC_DEF_NO_INSTANTIATION}),
    ),
    Site(
        ":832 body assignment per def",
        "check_body_assignment_impl_loss",
        element("check_body_assignment_impl_loss", "CalculationDefinition", "owned_members"),
    ),
    Site(
        ":907 attribute redefinition per attribute",
        "check_attr_redef_expression_dropped",
        element("check_attr_redef_expression_dropped", "AttributeUsage", "owned_redefinitions"),
    ),
    Site(
        ":973 calc def count",
        "count of CalculationDefinition",
        enumeration("_element_count", "CalculationDefinition"),
    ),
    Site(
        ":978 calc usage count",
        "count of CalculationUsage",
        enumeration("_element_count", "CalculationUsage"),
    ),
    Site(
        "new: manifest checks",
        "manifest_checks",
        raising(level6_architecture, "_check_manifests", ForcedError("manifest bug")),
    ),
    # adr002.py
    Site(
        "adr002 :87 calc def locations per def",
        "check_calc_def_locations",
        element("check_calc_def_locations", "CalculationDefinition", "document"),
    ),
    Site(
        "adr002 :177 supported operators per attribute",
        "check_supported_operators",
        element("check_supported_operators", "AttributeUsage", "document"),
    ),
    Site(
        "adr002 :207 _is_invocation",
        "check_static_function_invocations",
        type_test("_is_invocation", "InvocationExpression"),
        frozenset({ValidationCode.V4_STATIC_FUNCTION_INVOCATION}),
    ),
    Site(
        "adr002 :254 static function invocations per attribute",
        "check_static_function_invocations",
        element("check_static_function_invocations", "AttributeUsage", "document"),
    ),
    Site(
        "adr002 :277 _is_calc_usage",
        "check_static_expressions",
        type_test("_is_calc_usage", "CalculationUsage"),
        EXPOSE_DEPENDENT,
        "plant::Plant::exposed",
    ),
    Site(
        "adr002 :335 _is_part_usage",
        "check_static_expressions",
        type_test("_is_part_usage", "PartUsage"),
        EXPOSE_DEPENDENT,
        "plant::Plant::exposed",
    ),
    Site(
        "adr002 :423 is_expose_binding",
        "check_static_expressions",
        raising(adr002, "resolved_referent", ForcedError("referent read failed")),
        EXPOSE_DEPENDENT,
        "plant::Plant::exposed",
    ),
    Site(
        "adr002 :624 static expressions per attribute",
        "check_static_expressions",
        element("check_static_expressions", "AttributeUsage", "document"),
    ),
]
SITE = {site.where: site for site in SITES}


def _l6(tmp_path: Path, target: str) -> QualityCheckResult:
    pyproject = None if target == "unset" else target_table(f'"{target}"')
    models = {str(p.relative_to(FIXTURE)): p.read_text() for p in sorted(FIXTURE.rglob("*.sysml"))}
    root = make_project(tmp_path, pyproject=pyproject, models=models)
    return level6_architecture.validate_architecture(str(root))


def _errors(result: QualityCheckResult, check: str) -> list[Any]:
    return [
        i
        for i in result.structured_issues
        if i.code is CHECK_ERROR and i.message.startswith(f"{check} could not inspect ")
    ]


def _codes(result: QualityCheckResult, subject: str | None = None) -> set[ValidationCode]:
    """Every code L6 reported or summarized, or only those on `subject`."""
    issues = [*result.structured_issues, *result.summarized]
    return {i.code for i in issues if subject is None or i.element_name == subject}


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_fixture_reaches_every_site_cleanly(tmp_path, target):
    result = _l6(tmp_path, target)
    assert CHECK_ERROR not in _codes(result)
    assert {UNEXTRACTABLE, INCOMPLETE} <= _codes(result)


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("site", SITES, ids=str)
def test_site_failure_is_check_error_naming_check(site, target, monkeypatch, tmp_path):
    site.force(monkeypatch)
    result = _l6(tmp_path, target)
    errors = _errors(result, site.check)
    assert errors, [i.message for i in result.structured_issues]
    assert all(e.severity.value == "error" for e in errors)
    assert not result.success
    assert not (site.no_finding & _codes(result, site.subject))
    assert CHECK_ERROR not in {i.code for i in result.summarized}


@pytest.mark.syside
@pytest.mark.parametrize(
    ("site", "metric"),
    [
        (SITE[":973 calc def count"], "Calc defs checked"),
        (SITE[":978 calc usage count"], "Calc usages checked"),
    ],
    ids=["calc defs", "calc usages"],
)
def test_failed_counts_print_not_computed(site, metric, monkeypatch, tmp_path):  # :973, :978
    site.force(monkeypatch)
    assert _l6(tmp_path, "unset").metrics[metric] == "not computed"


@pytest.mark.syside
def test_failed_manifest_check_prints_not_computed(monkeypatch, tmp_path):
    SITE["new: manifest checks"].force(monkeypatch)
    assert _l6(tmp_path, "unset").metrics["Manifests checked"] == "not computed"


@pytest.mark.syside
def test_failed_check_prints_its_code_counts_not_computed(monkeypatch, tmp_path):
    enumeration("check_design_attr_completeness", "AttributeUsage")(monkeypatch)
    metrics = _l6(tmp_path, "unset").metrics
    assert metrics["Design attrs checked"] == "not computed"
    assert metrics["L6_DESIGN_ATTR_INCOMPLETE"] == "not computed"
    assert metrics["L6_DESIGN_ATTR_UNEXTRACTABLE"] == "not computed"
    assert metrics["L6_ANONYMOUS_RETURN"] == 0


@pytest.mark.syside
def test_unextractable_catch_only_takes_evaluator_signal(monkeypatch, tmp_path):  # D16, :540
    signal = expression.UnextractableValueError("not a static number")
    raising(level6_architecture, "evaluate_true_static_expression", signal)(monkeypatch)
    result = _l6(tmp_path / "signal", "unset")
    assert UNEXTRACTABLE in _codes(result) and CHECK_ERROR not in _codes(result)
    raising(level6_architecture, "evaluate_true_static_expression", ValueError("bug"))(monkeypatch)
    result = _l6(tmp_path / "plain", "unset")
    assert UNEXTRACTABLE not in _codes(result)
    assert _errors(result, "check_design_attr_completeness")


@pytest.mark.parametrize(
    "expr",
    [
        None,
        type("LiteralString", (), {"value": "abc"})(),
        type("LiteralRational", (), {})(),
        type("SomethingElse", (), {})(),
    ],
    ids=["none", "string literal", "literal without value", "unknown node"],
)
def test_evaluator_deliberate_raises_are_unextractable_subclasses(expr):
    with pytest.raises(expression.Unextractable) as raised:
        expression.evaluate_true_static_expression(expr)
    assert isinstance(raised.value, (ValueError, TypeError))


def test_existing_value_type_error_callers_still_catch():
    assert issubclass(expression.UnextractableValueError, ValueError)
    assert issubclass(expression.UnextractableTypeError, TypeError)
    with pytest.raises(ValueError):
        expression.evaluate_true_static_expression(type("LiteralString", (), {"value": "x"})())
    with pytest.raises(TypeError):
        expression.evaluate_true_static_expression(None)


def test_dead_calc_usage_names_helper_is_deleted():  # adr002 :268
    assert not hasattr(adr002, "_get_calc_usage_names")


@pytest.mark.syside
def test_static_expression_walker_refusal_is_a_check_error(tmp_path):
    """A design attribute calling anything but `sum` fails L6 under every target.

    `check_static_expressions` reads references through `inspect_reference_uses`, which raises
    `SemanticEvidenceError` on every non-`sum` call (the ES-005 refusal path). Today's code
    skipped V2 for that attribute silently; under I1 it is now `L6_CHECK_ERROR`. Pinned here
    so a decision to treat it like D15 changes a test (plan Phase 7 notes, surprise 1).
    """
    model = FIXTURE / "designs" / "plant.sysml"
    text = model.read_text().replace("= a * 2.0;", "= abs(2.0);")
    models = {"library/calcs.sysml": (FIXTURE / "library" / "calcs.sysml").read_text()}
    root = make_project(tmp_path, models={**models, "designs/plant.sysml": text})
    result = level6_architecture.validate_architecture(str(root), execution_target=Target.NATIVE)
    (error,) = _errors(result, "check_static_expressions")
    assert error.reason_code == SemanticEvidenceError.__name__
    assert SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED.value not in error.message
    assert "is not supported by this executable subset" in error.message
    assert not result.success

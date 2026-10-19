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
from agentic_mbse.sysml.types import Severity, ValidationCode
from agentic_mbse.validation import adr002, level6_architecture
from agentic_mbse.validation.common import QualityCheckResult
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


def _abs_project(tmp_path: Path, target: str) -> Path:
    """The fixture with `scaled = a * 2.0` replaced by `abs(2.0)`: a call outside the subset.

    The design file moves to `analysis/`, outside the design-attribute check's `designs` filter,
    so V2 is the only legacy check with an ERROR to give: at `ebb3d467` this model passed L6
    with one `V4_STATIC_FUNCTION_INVOCATION` WARNING. (Under `designs/`, the evaluator's
    `L6_DESIGN_ATTR_UNEXTRACTABLE` ERROR fires on `abs(2.0)` before and after this item.)
    """
    model = FIXTURE / "designs" / "plant.sysml"
    text = model.read_text().replace("= a * 2.0;", "= abs(2.0);")
    assert "abs(2.0)" in text
    models = {"library/calcs.sysml": (FIXTURE / "library" / "calcs.sysml").read_text()}
    pyproject = None if target == "unset" else target_table(f'"{target}"')
    return make_project(
        tmp_path, pyproject=pyproject, models={**models, "analysis/plant.sysml": text}
    )


def _unverified(result: QualityCheckResult, check: str) -> list[Any]:
    return [
        i
        for i in result.structured_issues
        if i.code is ValidationCode.L6_CHECK_UNVERIFIED
        and i.message.startswith(f"{check} could not inspect ")
    ]


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_static_expression_walker_refusal_is_a_warning(target, tmp_path):
    """A design attribute calling anything but `sum`: V2 could not inspect it, under every target.

    `check_static_expressions` reads references through `inspect_reference_uses`, which raises
    `SemanticEvidenceError` on every non-`sum` call (the ES-005 refusal path). That is the walker
    declining the attribute, not a crash, so it is an `L6_CHECK_UNVERIFIED` WARNING naming the
    check, the attribute and the walker's reason, never folded into the native summary (design
    D15, I1; align § Audit decisions, B1). At `ebb3d467` this attribute passed L6.
    """
    result = level6_architecture.validate_architecture(str(_abs_project(tmp_path, target)))
    (warning,) = _unverified(result, "check_static_expressions")
    assert warning.severity is Severity.WARNING
    assert warning.element_name == "plant::Plant::scaled"
    assert warning.reason_code == SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED.value
    assert "is not supported by this executable subset" in warning.message
    assert ValidationCode.L6_CHECK_UNVERIFIED not in {i.code for i in result.summarized}
    assert not _errors(result, "check_static_expressions")
    assert result.success is (target != "generated")


@pytest.mark.syside
def test_static_expression_walker_refusal_still_fails_generated_via_contract(tmp_path):
    """Under `generated` the same attribute fails on the contract's refusal, not on V2."""
    result = level6_architecture.validate_architecture(str(_abs_project(tmp_path, "generated")))
    refused = [
        i
        for i in result.structured_issues
        if i.code is ValidationCode.L6_SUBSET_REFUSED and i.element_name == "plant::Plant::scaled"
    ]
    assert refused and all(i.severity is Severity.ERROR for i in refused)
    assert any(i.reason_code == "invocation_callable_unsupported" for i in refused)
    assert not any(i.code is CHECK_ERROR for i in result.structured_issues)
    assert not result.success


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_static_expression_walker_other_exception_is_still_a_check_error(
    target, monkeypatch, tmp_path
):
    """Only the walker's own `SemanticEvidenceError` is a WARNING; anything else stays an ERROR."""
    raising(adr002, "design_reference_uses", ForcedError("walker bug"))(monkeypatch)
    result = _l6(tmp_path, target)
    errors = _errors(result, "check_static_expressions")
    assert errors and all(e.reason_code == ForcedError.__name__ for e in errors)
    assert not _unverified(result, "check_static_expressions")
    assert not result.success


@pytest.mark.syside
@pytest.mark.parametrize(
    ("function", "check"),
    [
        ("extract_operators", "check_supported_operators"),
        ("traverse_expression", "check_static_function_invocations"),
    ],
)
def test_other_legacy_walker_calls_report_unverified(function, check, monkeypatch, tmp_path):
    """V4's walker calls get the same rule as V2's: a declined element is a WARNING."""
    declined = SemanticEvidenceError(
        SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED, function, "forced depth exhaustion"
    )
    raising(adr002, function, declined)(monkeypatch)
    result = _l6(tmp_path, "native")
    warnings = _unverified(result, check)
    assert warnings and all(w.severity is Severity.WARNING for w in warnings)
    assert all(
        w.reason_code == SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED.value for w in warnings
    )
    assert not _errors(result, check)


@pytest.mark.syside
def test_failed_calc_def_listing_still_checks_calc_usages(monkeypatch, tmp_path):
    """A failed calc-def listing ends only that half of `check_qualified_names` (audit adv. 2)."""
    enumeration("check_qualified_names", "CalculationDefinition")(monkeypatch)
    calcs = (FIXTURE / "library" / "calcs.sysml").read_text().replace("calc t :", "calc _t :")
    assert "calc _t :" in calcs
    models = {
        "library/calcs.sysml": calcs,
        "designs/plant.sysml": (FIXTURE / "designs" / "plant.sysml").read_text(),
    }
    result = level6_architecture.validate_architecture(
        str(make_project(tmp_path, pyproject=target_table('"native"'), models=models))
    )
    assert len(_errors(result, "check_qualified_names")) == 1
    invalid = [
        i for i in result.structured_issues if i.code is ValidationCode.L6_INVALID_QUALIFIED_NAME
    ]
    assert [i.element_name for i in invalid] == ["lib::Site::_t"]


def _assert_target_recorded(result: QualityCheckResult, pyproject: Path) -> None:
    assert not result.success
    assert result.metrics["Execution target"] == f"native (from {pyproject})"
    assert result.report_detail["target"]["target"] == "native"
    assert result.report_detail["target"]["source"] == "FromFile"
    assert result.report_detail["target"]["file"] == str(pyproject)


def test_missing_models_path_still_records_the_target(tmp_path):
    """The path-discovery exit names the target and its source (audit advisory 1)."""
    models = make_project(tmp_path, pyproject=target_table('"native"'))
    result = level6_architecture.validate_architecture(str(models / "absent"))
    assert any("Path does not exist" in issue for issue in result.issues)
    _assert_target_recorded(result, models.parent / "pyproject.toml")


def test_failed_model_load_still_records_the_target(monkeypatch, tmp_path):
    """The model-load exit names the target and its source (audit advisory 1)."""
    raising(level6_architecture, "load_sysml_model", ForcedError("load failed"))(monkeypatch)
    models = make_project(tmp_path, pyproject=target_table('"native"'))
    result = level6_architecture.validate_architecture(str(models))
    assert result.issues == ["Failed to load model: load failed"]
    _assert_target_recorded(result, models.parent / "pyproject.toml")

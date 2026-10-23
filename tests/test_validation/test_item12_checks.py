"""
Item 12 (UPSTREAM-FINDINGS) validation checks that remain after ADR 0006 removed the
generator copies (C1, C2a, C2b, C4, C6b):

- C3  L6  constraint ineligibility (CONSTRAINT-EXEC Item 3 superseded this: a genuinely
       blocked construct WARNs; an admitted one, like `constraint_model`'s clean
       `measured <= limit`, is silent) -> WARN, L6 still passes
- C5, C6, F6  ADR-002 operator, function and formula rules

Each check ships with a fixture under tests/fixtures/item12/. Models load via
syside (SYSIDE_LICENSE_KEY from .env, loaded by conftest).
"""

from pathlib import Path

from agentic_mbse.sysml.types import Severity, ValidationCode
from agentic_mbse.validation.adr002 import (
    check_static_expressions,
    check_static_function_invocations,
    check_supported_operators,
)
from agentic_mbse.validation.common import discover_sysml_files, load_sysml_model
from agentic_mbse.validation.level6_architecture import (
    check_constraint_executability,
)
from tests.helpers.identified_facts import identify

FIXTURES = Path(__file__).parent.parent / "fixtures" / "item12"

_MODEL_CACHE: dict[str, object] = {}


def load_fixture(name: str):
    """Load an item12 fixture model (library/ + designs/), cached per name."""
    if name not in _MODEL_CACHE:
        files = discover_sysml_files(str(FIXTURES / name))
        model, _ = load_sysml_model(files)
        _MODEL_CACHE[name] = model
    return _MODEL_CACHE[name]


def _codes(issues) -> list[str]:
    return [i.code.value for i in issues]


# --- C3: constraint ineligibility (L6, WARN) -------------------------------------


def test_c3_admitted_constraint_is_silent():
    """`within_limit` (`measured <= limit`, a clean unitless Real comparison) is admitted
    under the executable profile, not blocked — CONSTRAINT-EXEC Item 3's silent-on-clean,
    superseding the old blanket 'dropped at extraction' WARN this fixture used to trigger."""
    issues = check_constraint_executability(load_fixture("constraint_model"))
    assert issues == []


def test_c3_malformed_numerical_is_error():
    """A feature chain inside a numerical comparison is malformed and fails L6."""
    fixture_dir = Path(__file__).parent.parent / "fixtures" / "item4_subtype" / "l6_ineligible"
    files = discover_sysml_files(str(fixture_dir))
    model, _ = load_sysml_model(files)
    issues = check_constraint_executability(model)
    errors = [i for i in issues if i.code == ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL]
    assert len(errors) == 1, f"Expected one constraint ERROR, got {_codes(issues)}"
    assert all(i.severity == Severity.ERROR for i in errors)


def test_c3_non_numerical_is_one_warning_per_statement(monkeypatch):
    from agentic_mbse.sysml.constraint_facts import ConstraintFacts, parse
    from agentic_mbse.validation import level6_architecture

    facts_path = (
        Path(__file__).parent.parent
        / "fixtures"
        / "constraint_fact_shapes"
        / "production_facts.json"
    )
    facts = parse(facts_path.read_text())
    usage = next(u for u in facts.usages if u.identity.name == "boolean_boolean")
    narrowed = ConstraintFacts(
        definitions=facts.definitions,
        usages=[usage],
        contexts=facts.contexts,
        diagnostics=facts.diagnostics,
    )
    # The usage is inline, so it names no definition and its exact association is None.
    identified = identify(narrowed)
    monkeypatch.setattr(
        level6_architecture,
        "constraint_facts",
        lambda _model: identified,
    )

    issues = check_constraint_executability(object())

    assert len(issues) == 1
    assert issues[0].code == ValidationCode.L6_CONSTRAINT_NON_NUMERICAL
    assert issues[0].severity == Severity.WARNING
    assert "warn_non_numerical_equality" in issues[0].message


# --- C5: adr002 operator-set correction (L6) ------------------------------------


def test_c5_power_operator_is_unsupported():
    """`^` was wrongly in SUPPORTED_OPERATORS; `2.0 ^ 3.0` at design scope now
    fires V4_UNSUPPORTED_OPERATOR (C5a). The supported-op `ok` does NOT fire."""
    issues = check_supported_operators(load_fixture("static_operators"))
    unsup = [i for i in issues if i.code == ValidationCode.V4_UNSUPPORTED_OPERATOR]
    assert len(unsup) == 1, f"Expected one unsupported-operator ERROR, got {_codes(issues)}"
    assert "powered" in unsup[0].element_name


def test_c5_function_invocation_warns():
    """`sqrt(2.0)` at design scope invokes a function -> V4_STATIC_FUNCTION_INVOCATION
    WARN (C5b). The literal arg isolates it from the V2 derived-expr check; the
    supported-op `ok` does NOT fire."""
    issues = check_static_function_invocations(load_fixture("static_operators"))
    fn = [i for i in issues if i.code == ValidationCode.V4_STATIC_FUNCTION_INVOCATION]
    assert len(fn) == 1, f"Expected one function-invocation WARN, got {_codes(issues)}"
    assert fn[0].severity == Severity.WARNING
    assert "rooted" in fn[0].element_name


# --- C6: L6 false-positive corrections ------------------------------------------


def test_c6a_calc_def_internal_expr_not_flagged():
    """A calc-def-internal `out attribute derated = availability * 0.9` is where
    derived expressions belong (ADR-002) -> must NOT fire V2_DYNAMIC_EXPRESSION,
    even in a flat layout where the library/ path skip does not apply (C6a)."""
    issues = check_static_expressions(load_fixture("c6_false_positives"))
    dyn = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]
    assert dyn == [], f"Calc-def-internal derived expr must not fire V2: {_codes(issues)}"


def test_c6c_calc_def_internal_power_not_flagged():
    """`out attribute powered = availability ^ 2` uses power INSIDE a calc def ->
    must NOT fire V4_UNSUPPORTED_OPERATOR, even in a flat layout where the library/
    path skip does not apply. Power is unsupported at design scope (C5a) but
    legitimate in a calc def; the fix keys off the owner type, mirroring C6a."""
    issues = check_supported_operators(load_fixture("c6_false_positives"))
    unsup = [i for i in issues if i.code == ValidationCode.V4_UNSUPPORTED_OPERATOR]
    assert unsup == [], f"Calc-def-internal power must not fire V4: {_codes(issues)}"


def test_c6d_calc_def_internal_function_not_flagged():
    """`out attribute rooted = sqrt(availability)` invokes a function INSIDE a calc
    def -> must NOT fire V4_STATIC_FUNCTION_INVOCATION, even in a flat layout. A
    calc def is exactly where a function invocation belongs; the fix keys off the
    owner type, mirroring C6a."""
    issues = check_static_function_invocations(load_fixture("c6_false_positives"))
    fn = [i for i in issues if i.code == ValidationCode.V4_STATIC_FUNCTION_INVOCATION]
    assert fn == [], f"Calc-def-internal function must not fire V4: {_codes(issues)}"


# --- F6: FORMULA computed attributes (L6 false-positive correction) --------------


def test_f6_formula_computed_attrs_not_flagged():
    """A design computed attribute whose refs are all same-part owned siblings is a
    codegen-supported FORMULA (Item 5, REQ-CA-06): `net_margin = revenue - cost` and
    `total_payout = net_margin * 2.0` (FORMULA reading a FORMULA sibling) must NOT
    fire V2_DYNAMIC_EXPRESSION."""
    issues = check_static_expressions(load_fixture("formula_computed"))
    formula = [
        i
        for i in issues
        if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION
        and ("net_margin" in i.element_name or "total_payout" in i.element_name)
    ]
    assert formula == [], f"Same-part FORMULA must not fire V2: {_codes(issues)}"


def test_f6_calc_output_ref_still_fires():
    """Negative-of-the-negative: a reference to a calc OUTPUT inside arithmetic
    (`derated = scale.result * 0.95`, foreign namespace, dotted path) is the
    genuinely-unsupported dynamic-expression case and must STILL fire
    V2_DYNAMIC_EXPRESSION. The F6 fix must not go blind to it."""
    issues = check_static_expressions(load_fixture("formula_computed"))
    fired = [
        i
        for i in issues
        if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION and "derated" in i.element_name
    ]
    assert len(fired) == 1, f"Calc-output ref in arithmetic must fire V2: {_codes(issues)}"
    assert fired[0].severity == Severity.ERROR

"""
Item 12 (UPSTREAM-FINDINGS) validation checks.

The four non-fileable checks that catch the traps that actually bit fusion-tea,
each with a negative fixture AND a negative-of-the-negative (the shape codegen
accepts must NOT fire):

- C1  L2  self-named binding with no covering feature (a true dead-end) -> FAIL
       (self_named_deadend FAILs; self_named_trap AND self_named_rescue do NOT —
        both carry a same-named feature, the plant idiom Items 9/10 support)
- C2a L6  anonymous return -> FAIL
       (anonymous_return FAILs; return_styles does NOT)
- C3  L6  constraint non-executability -> WARN
       (constraint_model warns, L6 still passes)
- C4  L6  calc-bearing part def never instantiated -> FAIL
       (no_instantiation FAILs; retype_instantiation does NOT — retype counts)

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
from agentic_mbse.validation.level2_structure import check_self_named_bindings
from agentic_mbse.validation.level6_architecture import (
    check_anonymous_returns,
    check_body_assignment_impl_loss,
    check_calc_bearing_instantiation,
    check_constraint_executability,
    check_qualified_names,
)

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


# --- C1: self-named binding (L2) ------------------------------------------------


def test_c1_self_named_deadend_fails():
    """DeadEndPlant binds `in gain = gain` but owns NO feature named `gain` — no
    attribute, no sibling calc output. The reference dead-ends on the calc's own
    parameter with nothing to cover it -> L2 FAIL."""
    issues = check_self_named_bindings(load_fixture("self_named_deadend"))
    self_named = [i for i in issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING]
    assert len(self_named) == 1, f"Expected one self-named FAIL, got {_codes(issues)}"
    assert self_named[0].severity == Severity.ERROR
    assert "gain" in self_named[0].message


def test_c1_self_named_trap_does_not_fire():
    """The trap owns `attribute availability = 0.70` — a same-named covering
    feature (the plant design-attribute idiom Item 9 makes SUPPORTED). Its role
    flipped to negative-of-the-negative: C1 must NOT fire."""
    issues = check_self_named_bindings(load_fixture("self_named_trap"))
    self_named = [i for i in issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING]
    assert self_named == [], f"Trap now carries a covering attribute; must not fire: {_codes(issues)}"


def test_c1_self_named_rescue_does_not_fire():
    """The rescue exposes `attribute throughput = source_calc.throughput`, a real
    producer, so the same self-named binding must NOT fire (Item 10 rescues it)."""
    issues = check_self_named_bindings(load_fixture("self_named_rescue"))
    self_named = [i for i in issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING]
    assert self_named == [], f"Rescue must not fire self-named FAIL: {_codes(issues)}"


# --- C2a: anonymous return (L6) -------------------------------------------------


def test_c2a_anonymous_return_fails():
    """`return : Real = x * 2` has no declared name -> no output channel -> FAIL."""
    issues = check_anonymous_returns(load_fixture("anonymous_return"))
    anon = [i for i in issues if i.code == ValidationCode.L6_ANONYMOUS_RETURN]
    assert len(anon) == 1, f"Expected one anonymous-return FAIL, got {_codes(issues)}"
    assert anon[0].severity == Severity.ERROR


def test_c2a_return_styles_accepted():
    """The four legal output forms (out attribute, named inline/body return, bare
    in) all carry a declared name -> anonymous-return check must NOT fire."""
    issues = check_anonymous_returns(load_fixture("return_styles"))
    anon = [i for i in issues if i.code == ValidationCode.L6_ANONYMOUS_RETURN]
    assert anon == [], f"Legal return styles must not fire: {_codes(issues)}"


# --- C3: constraint non-executability (L6, WARN) --------------------------------


def test_c3_constraint_warns_not_fails():
    """A constraint usage warns that it is dropped at extraction (WARNING, not
    ERROR — L6 stays passing)."""
    issues = check_constraint_executability(load_fixture("constraint_model"))
    warns = [i for i in issues if i.code == ValidationCode.L6_CONSTRAINT_NON_EXECUTABLE]
    assert len(warns) >= 1, f"Expected a constraint WARN, got {_codes(issues)}"
    assert all(i.severity == Severity.WARNING for i in warns)


# --- C4: calc-bearing part def, no instantiation (L6) ---------------------------


def test_c4_no_instantiation_fails():
    """OrphanCalcHolder owns a template calc but no usage instantiates it -> FAIL."""
    issues = check_calc_bearing_instantiation(load_fixture("no_instantiation"))
    no_inst = [i for i in issues if i.code == ValidationCode.L6_CALC_DEF_NO_INSTANTIATION]
    assert len(no_inst) == 1, f"Expected one no-instantiation FAIL, got {_codes(issues)}"
    assert no_inst[0].severity == Severity.ERROR
    assert "OrphanCalcHolder" in no_inst[0].message


def test_c4_retype_counts_as_instantiation():
    """Both IfeDriver and HifDriver are instantiated — IfeDriver via Facility.driver
    and HifDriver via a retype (`part :>> driver : HifDriver`). Retyping counts, so
    the check must NOT fire on either."""
    issues = check_calc_bearing_instantiation(load_fixture("retype_instantiation"))
    no_inst = [i for i in issues if i.code == ValidationCode.L6_CALC_DEF_NO_INSTANTIATION]
    assert no_inst == [], f"Retyped instantiation must not fire: {_codes(issues)}"


# --- C2b: body-assignment auto-impl-loss (L6, WARN) -----------------------------


def test_c2b_body_assignment_warns():
    """BodyCalc's `return attribute y; y = d*5` keeps the channel but loses
    auto-impl -> exactly one WARN, on BodyCalc; the inline InlineCalc does NOT."""
    issues = check_body_assignment_impl_loss(load_fixture("body_assignment"))
    warns = [i for i in issues if i.code == ValidationCode.L6_BODY_ASSIGNMENT_IMPL_LOSS]
    assert len(warns) == 1, f"Expected one body-assignment WARN, got {_codes(issues)}"
    assert warns[0].severity == Severity.WARNING
    assert "BodyCalc" in warns[0].element_name


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


def test_c6b_quoted_name_not_flagged():
    """'Trap Plant' is a quoted name codegen sanitizes -> must NOT fire
    L6_INVALID_QUALIFIED_NAME (C6b)."""
    issues = check_qualified_names(load_fixture("c6_false_positives"))
    bad = [i for i in issues if i.code == ValidationCode.L6_INVALID_QUALIFIED_NAME]
    assert bad == [], f"Quoted name must not fire invalid-qualified-name: {_codes(issues)}"


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

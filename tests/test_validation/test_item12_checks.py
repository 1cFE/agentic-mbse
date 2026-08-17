"""
Item 12 (UPSTREAM-FINDINGS) validation checks.

The four non-fileable checks that catch the traps that actually bit fusion-tea,
each with a negative fixture AND a negative-of-the-negative (the shape codegen
accepts must NOT fire):

- C1  L2  self-named binding -> FAIL, with no exemption
       (self_named_deadend, self_named_trap AND self_named_rescue all FAIL: a
        same-named outer attribute or sibling calc output does not rescue the
        binding, because exact elaboration never reinterprets a self-binding as an
        outer reference — D-4 [OWNER-VERBATIM 2026-08-05])
- C2a L6  anonymous return -> FAIL
       (anonymous_return FAILs; return_styles does NOT)
- C3  L6  constraint ineligibility (CONSTRAINT-EXEC Item 3 superseded this: a genuinely
       blocked construct WARNs; an admitted one, like `constraint_model`'s clean
       `measured <= limit`, is silent) -> WARN, L6 still passes
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


# --- C1: self-named binding (L2) ------------------------------------------------


def test_c1_self_named_deadend_fails():
    """DeadEndPlant binds `in gain = gain`. The reference resolves to the calc's own
    parameter, so the intended outer value never arrives -> L2 FAIL. This fixture owns
    no same-named feature at all, which is why it was the one shape the check flagged
    even while the exemption stood."""
    issues = check_self_named_bindings(load_fixture("self_named_deadend"))
    self_named = [i for i in issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING]
    assert len(self_named) == 1, f"Expected one self-named FAIL, got {_codes(issues)}"
    assert self_named[0].severity == Severity.ERROR
    assert "gain" in self_named[0].message


def test_c1_self_named_binding_fires_over_a_covering_attribute():
    """TrapPlant owns `attribute availability = 0.70` and still binds
    `in availability = availability`. The outer attribute does not rescue it: exact
    elaboration never reinterprets a self-binding as an outer reference (D-4
    [OWNER-VERBATIM 2026-08-05]), so the binding dead-ends on the calc's own parameter
    and C1 FAILs. The check used to exempt exactly this shape."""
    issues = check_self_named_bindings(load_fixture("self_named_trap"))
    self_named = [i for i in issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING]
    assert len(self_named) == 1, f"Expected one self-named FAIL, got {_codes(issues)}"
    assert self_named[0].severity == Severity.ERROR
    assert "availability" in self_named[0].message
    assert "TrapLib::TrapPlant::avail_calc" == self_named[0].element_name


def test_c1_self_named_binding_fires_over_a_covering_calc_output():
    """RescuePlant exposes `attribute throughput = source_calc.throughput`, a real
    producer, and still binds `in throughput = throughput`. A sibling producer is the
    other shape the exemption used to cover; the same rule removes it. The author's fix
    is to bind the producer by a distinct path, not to rely on the name collision."""
    issues = check_self_named_bindings(load_fixture("self_named_rescue"))
    self_named = [i for i in issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING]
    assert len(self_named) == 1, f"Expected one self-named FAIL, got {_codes(issues)}"
    assert self_named[0].severity == Severity.ERROR
    assert "throughput" in self_named[0].message
    assert "RescueLib::RescuePlant::sink_calc" == self_named[0].element_name


def test_c1_message_does_not_offer_the_outer_feature_as_a_rescue():
    """The diagnostic must not send the author looking for a same-named outer feature:
    that reading is precisely what D-4 forbids, and the old message implied it by saying
    'no feature named P is in scope to supply it'."""
    issues = check_self_named_bindings(load_fixture("self_named_trap"))
    message = next(
        i.message for i in issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING
    )
    assert "is in scope to supply it" not in message
    assert "never reinterpreted as an outer reference" in message


def test_c1_qualified_binding_to_owner_attribute_is_not_self_named():
    """F-2 (self-binding-replacement Phase 1): `in availability =
    QualifiedPlant::availability` and the usage-qualified `station::availability`
    resolve to the OWNER's attribute — a different element from the calc's own
    parameter — and codegen accepts both (D-6). C1 compares referent identity,
    not names, so neither may fire. The other direction stays pinned by the
    three self-named tests above: deadend, trap, and rescue all still FAIL."""
    issues = check_self_named_bindings(load_fixture("usage_qualified_local"))
    self_named = [i for i in issues if i.code == ValidationCode.L2_SELF_NAMED_BINDING]
    assert self_named == [], f"Qualified referent must not fire C1: {_codes(issues)}"


def test_c1_inspection_failure_surfaces_as_error_not_clean(monkeypatch):
    """Audit F4 (self-binding-replacement): an unexpected failure while inspecting
    a calc usage must surface as an L2_CHECK_UNVERIFIABLE ERROR, never be swallowed
    into an empty (clean-looking) issue list. A SysIDE or adapter regression that
    made the check skip usages silently was exactly the failure mode."""
    from agentic_mbse.validation import level2_structure

    def _boom(_element):
        raise RuntimeError("simulated adapter regression")

    monkeypatch.setattr(
        level2_structure.SysideAdapter, "element_id", staticmethod(_boom)
    )
    issues = check_self_named_bindings(load_fixture("self_named_trap"))
    unverified = [i for i in issues if i.code == ValidationCode.L2_CHECK_UNVERIFIABLE]
    assert unverified, f"inspection failure must be reported, got {_codes(issues)}"
    assert all(i.severity == Severity.ERROR for i in unverified)
    assert "simulated adapter regression" in unverified[0].message


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
        "extract_identified_constraint_facts",
        lambda _model: identified,
    )

    issues = check_constraint_executability(object())

    assert len(issues) == 1
    assert issues[0].code == ValidationCode.L6_CONSTRAINT_NON_NUMERICAL
    assert issues[0].severity == Severity.WARNING
    assert "warn_non_numerical_equality" in issues[0].message


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

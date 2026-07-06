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
from agentic_mbse.validation.common import discover_sysml_files, load_sysml_model
from agentic_mbse.validation.level2_structure import check_self_named_bindings
from agentic_mbse.validation.level6_architecture import (
    check_anonymous_returns,
    check_calc_bearing_instantiation,
    check_constraint_executability,
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

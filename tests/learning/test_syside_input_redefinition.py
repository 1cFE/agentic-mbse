"""Learning test: how SysIDE 0.8.4 surfaces calc and constraint input redefinitions.

EXEC-SUBSET-CONTRACT Item 4 (positional-binding check) reads, for each authored input of a
calc or constraint owner, the redefinitions SysIDE resolved for it and whether each one is
implied (by position) or explicit. These tests pin what SysIDE 0.8.4 actually does for the
de-risk flags R1-R6 in `.project/active/positional-binding-check/design.md`. Findings and
their consequences for the design are in `learning-findings.md` beside it.

Every test asserts observed behavior, including where the design's rule tolerates either
answer, so a SysIDE upgrade that changes any of it fails here first.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

syside = get_syside()

SUB = "calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }"
ADD = "calc def Add { in p : Real; in q : Real; return r : Real = p + q; }"
LE = "constraint def Le { in x : Real; in lim : Real; x <= lim }"

Redef = tuple[str, bool]
"""One resolved redefinition: (target qualified name, is_implied)."""


def _source(body: str) -> str:
    return f"package P {{ private import ScalarValues::*; {SUB} {ADD} {LE} {body} }}"


def _load(body: str) -> Any:
    """Load a model that SysIDE accepts without errors."""
    model, _ = syside.load_model(sysml_source=_source(body))
    return model


def _load_rejected(body: str) -> tuple[Any, list[str]]:
    """Load a model SysIDE rejects; return the model and its error codes."""
    with pytest.raises(syside.ModelError) as raised:
        syside.load_model(sysml_source=_source(body))
    codes = sorted({str(d.code) for d in raised.value.diagnostics.errors})
    return raised.value.model, codes


def _owner(model: Any, kind: Any, name: str) -> Any:
    (found,) = [e for e in model.elements(kind, include_subtypes=True) if e.name == name]
    return found


def _inputs(owner: Any) -> list[Any]:
    return [
        f for f in owner.owned_features.collect() if f.direction == syside.FeatureDirectionKind.In
    ]


def _redefinitions(feature: Any) -> list[Redef]:
    """The input's redefinitions as the design reads them (`heritage.relationships`, D3)."""
    return [
        (str(r.redefined_feature.qualified_name), r.is_implied)
        for r in feature.heritage.relationships
        if isinstance(r, syside.Redefinition)
    ]


def _shape(owner: Any) -> list[tuple[str | None, list[Redef]]]:
    """(declared name, redefinitions) for each authored input, in declaration order."""
    return [(f.declared_name, _redefinitions(f)) for f in _inputs(owner)]


def _calc_c(body: str) -> Any:
    return _owner(_load(f"part q {{ calc c : Sub {{ {body} }} }}"), syside.CalculationUsage, "c")


def _native_value(body: str) -> Any:
    """Native SysIDE value of `c.r` for `calc c : Sub { body }` (intended answer: 10 - 3 = 7)."""
    model = _load(f"part q {{ calc c : Sub {{ {body} }} attribute v : Real = c.r; }}")
    q = _owner(model, syside.PartUsage, "q")
    (v,) = [f for f in q.owned_features.collect() if f.name == "v"]
    value, _ = syside.Compiler().evaluate_feature(v, scope=q, stdlib=model.lib)
    return value


# --- R1: implied redefinitions next to, and on, explicit inputs -------------------------


def test_r1a_mixed_spelling_gives_b_an_implied_redefinition_of_sub_a() -> None:
    """B2 holds: `b` implicitly redefines `Sub::a` although `:>> a` explicitly redefines it."""
    c = _calc_c("in b = 3; in :>> a = 10;")
    assert _shape(c) == [
        ("b", [("P::Sub::a", True)]),
        (None, [("P::Sub::a", False)]),
    ]


def test_r1a_mixed_spelling_leaves_sub_b_unbound_and_native_evaluation_yields_nothing() -> None:
    """Both inputs land on `Sub::a`; nothing binds `Sub::b`, so `a - b` has no value."""
    assert _native_value("in b = 3; in :>> a = 10;") is None


def test_r1_reversed_fully_implicit_swaps_both_targets_and_evaluates_to_minus_7() -> None:
    c = _calc_c("in b = 3; in a = 10;")
    assert _shape(c) == [
        ("b", [("P::Sub::a", True)]),
        ("a", [("P::Sub::b", True)]),
    ]
    assert _native_value("in b = 3; in a = 10;") == -7


def test_r1_reversed_fully_explicit_carries_only_explicit_targets_and_evaluates_to_7() -> None:
    c = _calc_c("in :>> b = 3; in :>> a = 10;")
    assert _shape(c) == [
        (None, [("P::Sub::b", False)]),
        (None, [("P::Sub::a", False)]),
    ]
    assert _native_value("in :>> b = 3; in :>> a = 10;") == 7


def test_r1b_explicit_redefines_keyword_inputs_carry_no_implied_redefinition() -> None:
    c = _calc_c("in y redefines b = 3; in x redefines a = 10;")
    assert _shape(c) == [
        ("y", [("P::Sub::b", False)]),
        ("x", [("P::Sub::a", False)]),
    ]
    assert _native_value("in y redefines b = 3; in x redefines a = 10;") == 7


def test_r1_deliberate_rename_first_leaves_the_next_input_on_its_own_position() -> None:
    """The explicit input still occupies position 1: `b` implicitly redefines `Sub::b`."""
    c = _calc_c("in local redefines a = 10; in b = 3;")
    assert _shape(c) == [
        ("local", [("P::Sub::a", False)]),
        ("b", [("P::Sub::b", True)]),
    ]
    assert _native_value("in local redefines a = 10; in b = 3;") == 7


def test_r1_owned_redefinitions_also_lists_implied_redefinitions() -> None:
    """D3 reads `heritage`; `owned_redefinitions` reports the same set, implied included."""
    for f in _inputs(_calc_c("in b = 3; in :>> a = 10;")):
        owned = [
            (str(r.redefined_feature.qualified_name), r.is_implied)
            for r in f.owned_redefinitions.collect()
        ]
        assert owned == _redefinitions(f)


# --- R2: subject, actor and stakeholder parameters --------------------------------------

SPECIAL_DEFS = (
    "part def V; part def D; part def O; "
    "requirement def R { subject v : V; in lo : Real; in hi : Real; } "
    "requirement def RA { subject vehicle : V; actor drv : D; stakeholder own : O; in lo : Real; } "
    "use case def UC { subject s : V; actor d : D; } "
)


def test_r2_special_parameters_are_inputs_told_apart_by_owning_membership_type() -> None:
    model = _load(SPECIAL_DEFS)
    ra = _owner(model, syside.RequirementDefinition, "RA")
    memberships = {f.declared_name: type(f.owning_membership) for f in _inputs(ra)}
    assert memberships == {
        "vehicle": syside.SubjectMembership,
        "drv": syside.ActorMembership,
        "own": syside.StakeholderMembership,
        "lo": syside.FeatureMembership,
    }
    uc = _owner(model, syside.UseCaseDefinition, "UC")
    assert [type(f.owning_membership) for f in _inputs(uc)] == [
        syside.SubjectMembership,
        syside.ActorMembership,
    ]


def test_r2_an_ordinary_input_is_none_of_the_three_special_memberships() -> None:
    ra = _owner(_load(SPECIAL_DEFS), syside.RequirementDefinition, "RA")
    special = (syside.SubjectMembership, syside.ActorMembership, syside.StakeholderMembership)
    (lo,) = [f for f in _inputs(ra) if f.declared_name == "lo"]
    assert not isinstance(lo.owning_membership, special)


def test_r2_definition_subjects_implicitly_redefine_the_library_subj() -> None:
    model = _load(SPECIAL_DEFS)
    r = _owner(model, syside.RequirementDefinition, "R")
    assert _shape(r)[0] == ("v", [("Requirements::RequirementCheck::subj", True)])
    ra = _owner(model, syside.RequirementDefinition, "RA")
    assert _shape(ra)[0] == ("vehicle", [("Requirements::RequirementCheck::subj", True)])
    uc = _owner(model, syside.UseCaseDefinition, "UC")
    assert _shape(uc)[0] == ("s", [("UseCases::UseCase::subj", True)])


def test_r2_a_renamed_usage_subject_implicitly_redefines_the_definition_subject() -> None:
    model = _load(SPECIAL_DEFS + "part q { requirement r : R { subject veh : V; in lo = 1; } }")
    (veh, lo) = _inputs(_owner(model, syside.RequirementUsage, "r"))
    assert isinstance(veh.owning_membership, syside.SubjectMembership)
    assert (veh.declared_name, _redefinitions(veh)) == (
        "veh",
        [("P::R::v", True), ("Requirements::RequirementCheck::subj", True)],
    )
    assert _redefinitions(lo) == [("P::R::lo", True)]


def test_r2_subject_counts_toward_positions_of_the_other_inputs() -> None:
    """With the subject restated, swapped `in` parameters land one past it, on each other."""
    model = _load(
        SPECIAL_DEFS + "part q { requirement r : R { subject v : V; in hi = 3; in lo = 1; } }"
    )
    assert _shape(_owner(model, syside.RequirementUsage, "r"))[1:] == [
        ("hi", [("P::R::lo", True)]),
        ("lo", [("P::R::hi", True)]),
    ]


def test_r2_omitting_the_subject_puts_the_first_input_on_the_subject_and_is_an_error() -> None:
    model, codes = _load_rejected(
        "requirement def R { subject v; in lo : Real; in hi : Real; } "
        "part q { requirement r0 : R { in hi = 3; in lo = 1; } }"
    )
    assert codes == ["requirement-usage-subject-parameter-position"]
    assert _shape(_owner(model, syside.RequirementUsage, "r0")) == [
        ("hi", [("P::R::v", True), ("Requirements::RequirementCheck::subj", True)]),
        ("lo", [("P::R::lo", True)]),
    ]


@pytest.mark.parametrize("keyword", ["actor", "stakeholder"])
def test_r2_an_actor_or_stakeholder_also_counts_toward_positions(keyword: str) -> None:
    """Not restating it binds the next ordinary input to it; a value there is a type error.

    An untyped actor or stakeholder is still a part (`Parts::Part`), so a literal value
    landing on it never conforms.
    """
    model, codes = _load_rejected(
        f"part def V; requirement def R {{ subject v : V; {keyword} d; in lo : Real; in hi : Real; }} "
        "part q { requirement r : R { subject v : V; in hi = 3; in lo = 1; } }"
    )
    assert codes == ["type-error"]
    assert _shape(_owner(model, syside.RequirementUsage, "r"))[1:] == [
        ("hi", [("P::R::d", True)]),
        ("lo", [("P::R::lo", True)]),
    ]


def test_r2_a_constraint_nested_in_a_requirement_is_an_ordinary_constraint_owner() -> None:
    model = _load("requirement def R { require constraint k : Le { in lim = 5; in x = 3; } }")
    k = _owner(model, syside.ConstraintUsage, "k")
    assert isinstance(k.owning_membership, syside.RequirementConstraintMembership)
    assert _shape(k) == [
        ("lim", [("P::Le::x", True)]),
        ("x", [("P::Le::lim", True)]),
    ]


# --- R3: multiple types and the owning definition ---------------------------------------


def test_r3_each_input_gets_one_implied_redefinition_per_type() -> None:
    model = _load("part q { calc c : Sub, Add { in b = 3; in a = 10; } }")
    c = _owner(model, syside.CalculationUsage, "c")
    assert _shape(c) == [
        ("b", [("P::Sub::a", True), ("P::Add::p", True)]),
        ("a", [("P::Sub::b", True), ("P::Add::q", True)]),
    ]
    owning = {
        str(r.redefined_feature.qualified_name): str(r.redefined_feature.owning_type.qualified_name)
        for f in _inputs(c)
        for r in f.heritage.relationships
        if isinstance(r, syside.Redefinition)
    }
    assert owning == {
        "P::Sub::a": "P::Sub",
        "P::Add::p": "P::Add",
        "P::Sub::b": "P::Sub",
        "P::Add::q": "P::Add",
    }


def test_r3_an_explicit_input_with_several_types_gets_no_implied_redefinition() -> None:
    """R1(b) under multiple types: `x` redefines `Sub::a` only; nothing binds `Add::p`."""
    model = _load("part q { calc c : Sub, Add { in x redefines a = 10; in b = 3; } }")
    assert _shape(_owner(model, syside.CalculationUsage, "c")) == [
        ("x", [("P::Sub::a", False)]),
        ("b", [("P::Sub::b", True), ("P::Add::q", True)]),
    ]


def test_r3_a_parameterless_subdefinition_resolves_to_the_supertype_formals() -> None:
    model = _load("calc def Sub3 :> Sub; part q { calc c : Sub3 { in b = 3; in a = 10; } }")
    c = _owner(model, syside.CalculationUsage, "c")
    assert _shape(c) == [
        ("b", [("P::Sub::a", True)]),
        ("a", [("P::Sub::b", True)]),
    ]
    (b, _) = _inputs(c)
    (redefinition,) = [r for r in b.heritage.relationships if isinstance(r, syside.Redefinition)]
    assert str(redefinition.redefined_feature.owning_type.qualified_name) == "P::Sub"


def test_r3_definition_to_definition_inheritance_is_positional_too() -> None:
    model = _load("calc def Sub2 :> Sub { in b; in a; } calc def D :> Sub { in c; }")
    assert _shape(_owner(model, syside.CalculationDefinition, "Sub2")) == [
        ("b", [("P::Sub::a", True)]),
        ("a", [("P::Sub::b", True)]),
    ]
    assert _shape(_owner(model, syside.CalculationDefinition, "D")) == [
        ("c", [("P::Sub::a", True)]),
    ]


# --- R4: an `out` parameter before the inputs -------------------------------------------


def test_r4_positions_count_an_out_parameter_and_syside_rejects_the_model() -> None:
    model, codes = _load_rejected(
        "calc def O { out o : Real; in a : Real; in b : Real; } "
        "part q { calc u : O { in a = 1; in b = 2; } }"
    )
    assert codes == ["redefinition-direction-conformance"]
    assert _shape(_owner(model, syside.CalculationUsage, "u")) == [
        ("a", [("P::O::o", True)]),
        ("b", [("P::O::a", True)]),
    ]


def test_r4_a_trailing_return_parameter_does_not_shift_input_positions() -> None:
    model = _load(
        "calc def O2 { in a : Real; in b : Real; return r : Real; } "
        "part q { calc u : O2 { in a = 1; in b = 2; } }"
    )
    assert _shape(_owner(model, syside.CalculationUsage, "u")) == [
        ("a", [("P::O2::a", True)]),
        ("b", [("P::O2::b", True)]),
    ]


# --- R5: anonymous and inherited inputs -------------------------------------------------


def test_r5_anonymous_and_by_name_inputs_have_no_declared_name() -> None:
    c = _calc_c("in : Real = 10; in :>> b = 3;")
    anonymous, by_name = _inputs(c)
    assert (anonymous.declared_name, by_name.declared_name) == (None, None)
    # `name` falls back to the redefined formal's name, even for an implied redefinition.
    assert (anonymous.name, by_name.name) == ("a", "b")
    assert _redefinitions(anonymous) == [("P::Sub::a", True)]
    assert _redefinitions(by_name) == [("P::Sub::b", False)]


def test_r5_an_inherited_input_that_is_not_redeclared_is_not_an_owned_feature() -> None:
    c = _calc_c("in b = 3;")
    assert [str(f.qualified_name) for f in c.owned_features.collect()] == ["P::q::c::b"]
    inherited_inputs = sorted(
        str(f.qualified_name)
        for f in c.inherited_features.collect()
        if f.direction == syside.FeatureDirectionKind.In and str(f.qualified_name).startswith("P::")
    )
    assert inherited_inputs == ["P::Sub::a", "P::Sub::b"]


# --- R6: owner enumeration and document tiers -------------------------------------------

OWNER_SWEEPS = (
    "CalculationUsage",
    "ConstraintUsage",
    "CalculationDefinition",
    "ConstraintDefinition",
)

OWNERS_MODEL = """\
package P {
    private import ScalarValues::*;
    part def V;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
    requirement def R { subject v : V; in lo : Real; require constraint k : Le { in x = 1; in lim = 2; } }
    use case def UC { subject s : V; }
    analysis def AD { subject s : V; }
    verification def VD { subject s : V; }
    part q {
        calc c : Sub { in a = 1; in b = 2; }
        assert constraint ac : Le { in x = 1; in lim = 2; }
        constraint cu : Le { in x = 1; in lim = 2; }
        requirement r : R { subject v : V; in lo = 1; }
        use case uc : UC;
    }
}
"""


def _swept_owners(model: Any) -> dict[Any, Any]:
    owners: dict[Any, Any] = {}
    for sweep in OWNER_SWEEPS:
        for element in SysideAdapter.elements_of_type(model, sweep, include_subtypes=True):
            owners.setdefault(element.element_id, element)
    return owners


def test_r6_the_four_subtype_sweeps_reach_requirement_case_and_assert_owners(
    tmp_path: Path,
) -> None:
    path = tmp_path / "owners.sysml"
    path.write_text(OWNERS_MODEL)
    model, diagnostics = SysideAdapter.load_model([path])
    assert not diagnostics.contains_errors()
    owners = _swept_owners(model)
    assert sorted((str(e.qualified_name), type(e).__name__) for e in owners.values()) == [
        ("P::AD", "AnalysisCaseDefinition"),
        ("P::Le", "ConstraintDefinition"),
        ("P::R", "RequirementDefinition"),
        ("P::R::k", "ConstraintUsage"),
        ("P::Sub", "CalculationDefinition"),
        ("P::UC", "UseCaseDefinition"),
        ("P::VD", "VerificationCaseDefinition"),
        ("P::q::ac", "AssertConstraintUsage"),
        ("P::q::c", "CalculationUsage"),
        ("P::q::cu", "ConstraintUsage"),
        ("P::q::r", "RequirementUsage"),
        ("P::q::uc", "UseCaseUsage"),
    ]


def test_r6_sweeps_never_return_standard_library_owners_and_every_tier_reads(
    tmp_path: Path,
) -> None:
    """`model.elements` covers only the model's own documents by default, not the stdlib."""
    path = tmp_path / "owners.sysml"
    path.write_text(OWNERS_MODEL)
    model, _ = SysideAdapter.load_model([path])
    tiers = {SysideAdapter.document_tier(e) for e in _swept_owners(model).values()}
    assert tiers == {syside.DocumentTier.Project}
    assert len(list(model.stdlib_docs)) > 0

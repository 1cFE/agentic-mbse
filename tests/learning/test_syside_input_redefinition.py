"""Learning test: how SysIDE 0.8.4 surfaces calc and constraint input redefinitions.

EXEC-SUBSET-CONTRACT Item 4 (positional-binding check) reads, for each authored input of a
calc or constraint owner, the redefinitions SysIDE resolved for it and whether each one is
implied (by position) or explicit. These tests pin what SysIDE 0.8.4 actually does for the
de-risk flags R1-R6 in `.project/completed/20261018_positional-binding-check/design.md`. Findings and
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


# --- M1 (design review): an owner whose type does not resolve ---------------------------


def _load_diagnostics(body: str) -> tuple[Any, Any]:
    """Load a model SysIDE rejects; return the model and the full diagnostics object."""
    with pytest.raises(syside.ModelError) as raised:
        syside.load_model(sysml_source=_source(body))
    return raised.value.model, raised.value.diagnostics


def _relationship_kinds(feature: Any) -> list[tuple[str, bool]]:
    return [(type(r).__name__, r.is_implied) for r in feature.heritage.relationships]


def _explicit_typing_target(owner: Any) -> Any:
    (typing,) = list(owner.owned_typings.collect())
    return typing.type


TYPO = (
    "part q { calc c : Sbu { in b = 3; in a = 10; } constraint k : Lee { in lim = 5; in x = 3; } }"
)


def test_m1_an_unresolved_type_gives_the_inputs_no_implied_redefinition() -> None:
    model, _ = _load_diagnostics(TYPO)
    c = _owner(model, syside.CalculationUsage, "c")
    k = _owner(model, syside.ConstraintUsage, "k")
    assert _shape(c) == [("b", []), ("a", [])]
    assert _shape(k) == [("lim", []), ("x", [])]


def test_m1_inputs_of_an_unresolved_owner_look_exactly_like_new_parameters() -> None:
    """Same relationships as an input of an untyped calc, which has no formals to bind."""
    model, _ = _load_diagnostics(TYPO + " part u { calc n { in b = 3; } }")
    (new_parameter,) = _inputs(_owner(model, syside.CalculationUsage, "n"))
    for owner in (
        _owner(model, syside.CalculationUsage, "c"),
        _owner(model, syside.ConstraintUsage, "k"),
    ):
        for feature in _inputs(owner):
            assert _relationship_kinds(feature) == _relationship_kinds(new_parameter)
            assert _relationship_kinds(feature) == [("FeatureTyping", True), ("Subsetting", True)]


def test_m1_the_loader_reports_a_semantic_reference_error_with_a_location_only() -> None:
    """The error is in `.sema`, not `.parser`, and carries file, line, column and text.

    Nothing in the message links it to the owner element; only the location does.
    """
    _, diagnostics = _load_diagnostics(TYPO)
    assert list(diagnostics.parser) == []
    assert sorted((str(d.code), str(d.message)) for d in diagnostics.sema) == [
        ("reference-error", "No Type named 'Lee' found."),
        ("reference-error", "No Type named 'Sbu' found."),
    ]
    for d in diagnostics.sema:
        assert d.severity == syside.DiagnosticSeverity.Error
        assert (str(d.filename), d.line) == ("memory://sysml_model.sysml", 1)


def test_m1_the_owner_keeps_an_explicit_typing_to_a_shared_placeholder_classifier() -> None:
    """The typing is not absent: it targets an unowned `<placeholder Classifier>`.

    The calc and the constraint point at the same placeholder element, which has no
    owning relationship, while every real type does.
    """
    model, _ = _load_diagnostics(TYPO)
    calc_type = _explicit_typing_target(_owner(model, syside.CalculationUsage, "c"))
    constraint_type = _explicit_typing_target(_owner(model, syside.ConstraintUsage, "k"))
    for placeholder in (calc_type, constraint_type):
        assert type(placeholder) is syside.Classifier
        assert placeholder.name == "<placeholder Classifier>"
        assert str(placeholder.qualified_name) == "'<placeholder Classifier>'"
        assert placeholder.owning_relationship is None
        assert placeholder.owning_namespace is None
        assert str(placeholder.document.url) == "memory://placeholders.sysml"
    assert calc_type.element_id == constraint_type.element_id
    resolved = _explicit_typing_target(
        _owner(_load("part q { calc c : Sub; }"), syside.CalculationUsage, "c")
    )
    assert resolved.owning_relationship is not None


def test_m1_the_placeholder_reads_as_a_project_tier_element() -> None:
    """A tier check gives no signal: the placeholder document reads `Project`."""
    model, _ = _load_diagnostics(TYPO)
    placeholder = _explicit_typing_target(_owner(model, syside.CalculationUsage, "c"))
    assert SysideAdapter.document_tier(placeholder) is syside.DocumentTier.Project


def test_m1_placeholders_are_not_returned_by_model_sweeps() -> None:
    model, _ = _load_diagnostics(TYPO)
    names = {e.name for e in model.elements(syside.Classifier, include_subtypes=True)}
    assert "<placeholder Classifier>" not in names


def test_m1_unresolved_supertypes_and_redefinitions_also_target_placeholders() -> None:
    model, diagnostics = _load_diagnostics(
        "calc def D :> Missing { in z; } "
        "part q { calc c : Sub { in :>> zz = 1; } } "
        "part def Q2 :> Q1 { calc :>> cc { in b = 3; } }"
    )
    assert sorted(str(d.message) for d in diagnostics.sema) == [
        "No Classifier named 'Missing' found.",
        "No Classifier named 'Q1' found.",
        "No Feature named 'cc' found.",
        "No Feature named 'zz' found.",
    ]
    d = _owner(model, syside.CalculationDefinition, "D")
    (subclassification,) = [
        r
        for r in d.heritage.relationships
        if isinstance(r, syside.Subclassification) and not r.is_implied
    ]
    assert subclassification.general.name == "<placeholder Classifier>"
    assert subclassification.general.owning_relationship is None
    # An unresolved explicit redefinition reads fine: its target is a placeholder Feature.
    (zz,) = _inputs(_owner(model, syside.CalculationUsage, "c"))
    assert _redefinitions(zz) == [("'<placeholder Feature>'", False)]
    (redefinition,) = [r for r in zz.heritage.relationships if isinstance(r, syside.Redefinition)]
    assert type(redefinition.redefined_feature) is syside.Feature
    assert redefinition.redefined_feature.owning_relationship is None
    # A usage whose `:>>` target does not resolve has no name and no qualified name.
    (cc,) = [
        e
        for e in model.elements(syside.CalculationUsage)
        if any(isinstance(r, syside.Redefinition) for r in e.heritage.relationships)
    ]
    assert (cc.name, cc.declared_name, cc.qualified_name) == (None, None, None)
    assert _shape(cc) == [("b", [])]


def test_m1_a_partial_run_without_the_definitions_behaves_like_a_typo(tmp_path: Path) -> None:
    (tmp_path / "defs").mkdir()
    (tmp_path / "designs").mkdir()
    (tmp_path / "defs" / "defs.sysml").write_text(
        "package Defs { private import ScalarValues::*; "
        "calc def Sub { in a : Real; in b : Real; return r : Real = a - b; } "
        "constraint def Le { in x : Real; in lim : Real; x <= lim } }"
    )
    (tmp_path / "designs" / "use.sysml").write_text(
        "package Use {\n"
        "    private import Defs::*;\n"
        "    part q {\n"
        "        calc c : Sub { in b = 3; in a = 10; }\n"
        "        constraint k : Le { in lim = 5; in x = 3; }\n"
        "    }\n"
        "}\n"
    )
    model, diagnostics = SysideAdapter.load_model([tmp_path / "designs"])
    assert diagnostics.contains_errors()
    assert list(diagnostics.parser) == []
    assert sorted((str(d.code), str(d.message), d.line) for d in diagnostics.sema) == [
        ("reference-error", "No Namespace named 'Defs' found.", 2),
        ("reference-error", "No Type named 'Le' found.", 5),
        ("reference-error", "No Type named 'Sub' found.", 4),
    ]
    c = _owner(model, syside.CalculationUsage, "c")
    k = _owner(model, syside.ConstraintUsage, "k")
    assert _shape(c) == [("b", []), ("a", [])]
    assert _shape(k) == [("lim", []), ("x", [])]
    assert _explicit_typing_target(c).name == "<placeholder Classifier>"

    model, diagnostics = SysideAdapter.load_model([tmp_path])
    assert not diagnostics.contains_errors()
    assert _shape(_owner(model, syside.CalculationUsage, "c")) == [
        ("b", [("Defs::Sub::a", True)]),
        ("a", [("Defs::Sub::b", True)]),
    ]


# --- A1 (audit): an owner that subsets (`:>`) an unresolved feature ---------------------


def _explicit_subsettings(owner: Any) -> list[tuple[str, Any]]:
    """(relationship kind, subsetted feature) for each explicit subsetting of the owner."""
    return [
        (type(r).__name__, r.subsetted_feature)
        for r in owner.heritage.relationships
        if isinstance(r, syside.Subsetting) and not r.is_implied
    ]


@pytest.mark.parametrize(
    ("spelling", "kind"),
    [(":>", "Subsetting"), ("subsets", "Subsetting"), ("::>", "ReferenceSubsetting")],
)
def test_a1_an_unresolved_subsetting_target_is_a_placeholder_and_inputs_look_new(
    spelling: str, kind: str
) -> None:
    """Same silence as M1's typo: the inputs get no implied redefinition and look new.

    The only trace on the owner is an explicit subsetting whose target is an unowned
    `<placeholder Feature>`; `ReferenceSubsetting` is a `Subsetting` and reads the same way.
    """
    model, diagnostics = _load_diagnostics(
        f"part q {{ calc c {spelling} missing {{ in b = 3; in a = 10; }} "
        f"constraint k {spelling} missing2 {{ in lim = 5; in x = 3; }} }}"
    )
    assert list(diagnostics.parser) == []
    assert sorted((str(d.code), str(d.message)) for d in diagnostics.sema) == [
        ("reference-error", "No Feature named 'missing' found."),
        ("reference-error", "No Feature named 'missing2' found."),
    ]
    c = _owner(model, syside.CalculationUsage, "c")
    k = _owner(model, syside.ConstraintUsage, "k")
    assert _shape(c) == [("b", []), ("a", [])]
    assert _shape(k) == [("lim", []), ("x", [])]
    for owner in (c, k):
        for feature in _inputs(owner):
            assert _relationship_kinds(feature) == [("FeatureTyping", True), ("Subsetting", True)]
        ((found_kind, target),) = _explicit_subsettings(owner)
        assert found_kind == kind
        assert type(target) is syside.Feature
        assert target.name == "<placeholder Feature>"
        assert target.owning_relationship is None


def test_a1_a_resolved_subsetting_target_binds_the_inputs_by_position() -> None:
    """The parameters really are inherited through `:>`, so the unresolved case hides a swap."""
    model = _load(
        "part q { calc s : Sub; constraint t : Le; "
        "calc c :> s { in b = 3; in a = 10; } constraint k :> t { in lim = 5; in x = 3; } }"
    )
    c = _owner(model, syside.CalculationUsage, "c")
    k = _owner(model, syside.ConstraintUsage, "k")
    assert _shape(c) == [("b", [("P::Sub::a", True)]), ("a", [("P::Sub::b", True)])]
    assert _shape(k) == [("lim", [("P::Le::x", True)]), ("x", [("P::Le::lim", True)])]
    for owner in (c, k):
        ((_, target),) = _explicit_subsettings(owner)
        assert target.owning_relationship is not None


# --- M4 (design review): requirement and case definitions with no subject ---------------


@pytest.mark.parametrize(
    ("keyword", "kind", "library_subj", "code"),
    [
        (
            "requirement def",
            "RequirementDefinition",
            "Requirements::RequirementCheck::subj",
            "requirement-definition-subject-parameter-position",
        ),
        (
            "case def",
            "CaseDefinition",
            "Cases::Case::subj",
            "case-definition-subject-parameter-position",
        ),
        (
            "use case def",
            "UseCaseDefinition",
            "UseCases::UseCase::subj",
            "case-definition-subject-parameter-position",
        ),
        (
            "analysis def",
            "AnalysisCaseDefinition",
            "AnalysisCases::AnalysisCase::subj",
            "case-definition-subject-parameter-position",
        ),
        (
            "verification def",
            "VerificationCaseDefinition",
            "VerificationCases::VerificationCase::subj",
            "case-definition-subject-parameter-position",
        ),
    ],
)
def test_m4_the_first_ordinary_input_lands_on_the_library_subject_and_is_an_error(
    keyword: str, kind: str, library_subj: str, code: str
) -> None:
    """The first `in` implicitly redefines the library `subj`; the rest get no redefinition.

    SysIDE reports this as an error, so a subject-less definition with inputs is not a
    model SysIDE accepts.
    """
    model, codes = _load_rejected(f"{keyword} X {{ in lo : Real; in hi : Real; }}")
    assert codes == [code]
    x = _owner(model, getattr(syside, kind), "X")
    assert type(x).__name__ == kind
    assert _shape(x) == [("lo", [(library_subj, True)]), ("hi", [])]
    (lo, _) = _inputs(x)
    assert type(lo.owning_membership) is syside.FeatureMembership


def test_m4_a_usage_of_a_subject_less_requirement_def_also_lands_on_the_library_subject() -> None:
    """In declaration order, `lo` matches `R::lo` but also carries the library `subj`."""
    model, codes = _load_rejected(
        "requirement def R { in lo : Real; in hi : Real; } "
        "part q { requirement r : R { in lo = 1; in hi = 3; } requirement rs : R { in hi = 3; in lo = 1; } }"
    )
    assert codes == [
        "requirement-definition-subject-parameter-position",
        "requirement-usage-subject-parameter-position",
    ]
    subj = ("Requirements::RequirementCheck::subj", True)
    assert _shape(_owner(model, syside.RequirementUsage, "r")) == [
        ("lo", [("P::R::lo", True), subj]),
        ("hi", [("P::R::hi", True)]),
    ]
    assert _shape(_owner(model, syside.RequirementUsage, "rs")) == [
        ("hi", [("P::R::lo", True), subj]),
        ("lo", [("P::R::hi", True)]),
    ]


# --- S4 (design review): what owns the formals of a usage redefined in a subpart --------


def _target_owners(owner: Any) -> list[tuple[str | None, list[tuple[str, str, str]]]]:
    """(declared name, [(target, target's owning type, its metatype)]) per input."""
    return [
        (
            f.declared_name,
            [
                (
                    str(r.redefined_feature.qualified_name),
                    str(r.redefined_feature.owning_type.qualified_name),
                    type(r.redefined_feature.owning_type).__name__,
                )
                for r in f.heritage.relationships
                if isinstance(r, syside.Redefinition)
            ],
        )
        for f in _inputs(owner)
    ]


def _subpart_c(model: Any, part_def: str) -> Any:
    (c,) = [
        f
        for f in _owner(model, syside.PartDefinition, part_def).owned_features.collect()
        if f.name == "c"
    ]
    return c


def test_s4_a_parent_usage_without_inputs_leaves_the_definition_owning_the_formals() -> None:
    model = _load(
        "part def Q1 { calc c : Sub; } "
        "part def Q2 :> Q1 { calc :>> c { in b = 3; in a = 10; } } "
        "part def Q3 :> Q1 { calc :>> c { in local redefines a = 10; in b = 3; } }"
    )
    assert _target_owners(_subpart_c(model, "Q2")) == [
        ("b", [("P::Sub::a", "P::Sub", "CalculationDefinition")]),
        ("a", [("P::Sub::b", "P::Sub", "CalculationDefinition")]),
    ]
    assert _target_owners(_subpart_c(model, "Q3")) == [
        ("local", [("P::Sub::a", "P::Sub", "CalculationDefinition")]),
        ("b", [("P::Sub::b", "P::Sub", "CalculationDefinition")]),
    ]


def test_s4_a_parent_usage_that_restates_inputs_owns_the_formals_itself() -> None:
    """Targets are the parent usage's own inputs, owned by a `CalculationUsage`."""
    model = _load(
        "part def Q1 { calc c : Sub { in a; in b; } } "
        "part def Q2 :> Q1 { calc :>> c { in b = 3; in a = 10; } } "
        "part def Q3 :> Q1 { calc :>> c { in local redefines a = 10; in b = 3; } }"
    )
    assert _target_owners(_subpart_c(model, "Q2")) == [
        ("b", [("P::Q1::c::a", "P::Q1::c", "CalculationUsage")]),
        ("a", [("P::Q1::c::b", "P::Q1::c", "CalculationUsage")]),
    ]
    assert _target_owners(_subpart_c(model, "Q3")) == [
        ("local", [("P::Q1::c::a", "P::Q1::c", "CalculationUsage")]),
        ("b", [("P::Q1::c::b", "P::Q1::c", "CalculationUsage")]),
    ]


def test_s4_restating_the_type_too_gives_targets_owned_by_both_usage_and_definition() -> None:
    """`calc :>> c : Sub` has two supertypes, so each implied input gets two targets.

    An explicit input still gets no implied target (R1b), so a deliberate rename carries
    only its one explicit target.
    """
    model = _load(
        "part def Q1 { calc c : Sub { in a; in b; } } "
        "part def Q4 :> Q1 { calc :>> c : Sub { in b = 3; in a = 10; } } "
        "part def Q5 :> Q1 { calc :>> c : Sub { in local redefines a = 10; in b = 3; } }"
    )
    assert _target_owners(_subpart_c(model, "Q4")) == [
        (
            "b",
            [
                ("P::Q1::c::a", "P::Q1::c", "CalculationUsage"),
                ("P::Sub::a", "P::Sub", "CalculationDefinition"),
            ],
        ),
        (
            "a",
            [
                ("P::Q1::c::b", "P::Q1::c", "CalculationUsage"),
                ("P::Sub::b", "P::Sub", "CalculationDefinition"),
            ],
        ),
    ]
    assert _target_owners(_subpart_c(model, "Q5")) == [
        ("local", [("P::Q1::c::a", "P::Q1::c", "CalculationUsage")]),
        (
            "b",
            [
                ("P::Q1::c::b", "P::Q1::c", "CalculationUsage"),
                ("P::Sub::b", "P::Sub", "CalculationDefinition"),
            ],
        ),
    ]


# --- Plan phase 1: library subject formals, inout, quoted names, anonymous owners --------


def test_p1_library_subject_formal_reads_subject_membership() -> None:
    """B3 for library formals: `RequirementCheck::subj` is owned through a SubjectMembership.

    D20's special-slot reason reads the target's role from its owning membership, so a
    library target must read the same way a user definition's subject does.
    """
    r = _owner(
        _load("part def V; requirement def R { subject v : V; in lo : Real; }"),
        syside.RequirementDefinition,
        "R",
    )
    v = _inputs(r)[0]
    (redefinition,) = [r for r in v.heritage.relationships if isinstance(r, syside.Redefinition)]
    target = redefinition.redefined_feature
    assert str(target.qualified_name) == "Requirements::RequirementCheck::subj"
    assert isinstance(target.owning_membership, syside.SubjectMembership)
    assert str(target.owning_type.qualified_name) == "Requirements::RequirementCheck"


def test_p1_the_library_subject_a_subject_less_case_def_lands_on_reads_subject_membership() -> None:
    model, codes = _load_rejected("case def X { in lo : Real; in hi : Real; }")
    assert codes == ["case-definition-subject-parameter-position"]
    lo = _inputs(_owner(model, syside.CaseDefinition, "X"))[0]
    (redefinition,) = [r for r in lo.heritage.relationships if isinstance(r, syside.Redefinition)]
    assert str(redefinition.redefined_feature.qualified_name) == "Cases::Case::subj"
    assert isinstance(redefinition.redefined_feature.owning_membership, syside.SubjectMembership)


def test_p1_library_formals_carry_reload_stable_uuid5_identities() -> None:
    """`ElementRef` (`fact_refs.py`) requires UUIDv5 for a named element; library formals have it."""
    r = _owner(
        _load("part def V; requirement def R { subject v : V; }"), syside.RequirementDefinition, "R"
    )
    (redefinition,) = [
        r for r in _inputs(r)[0].heritage.relationships if isinstance(r, syside.Redefinition)
    ]
    assert redefinition.redefined_feature.element_id.version == 5


def test_p1_inout_inputs_are_redefined_by_position() -> None:
    model = _load(
        "calc def S { inout a : Real; inout b : Real; } "
        "part q { calc c : S { inout b = 3; inout a = 10; } }"
    )
    c = _owner(model, syside.CalculationUsage, "c")
    inouts = [
        f for f in c.owned_features.collect() if f.direction == syside.FeatureDirectionKind.Inout
    ]
    assert [(f.declared_name, _redefinitions(f)) for f in inouts] == [
        ("b", [("P::S::a", True)]),
        ("a", [("P::S::b", True)]),
    ]


QUOTED = (
    "package 'Quoted Pkg' { private import ScalarValues::*; "
    "calc def 'Net Closure' { in a : Real; in b : Real; } "
    "part q { calc c : 'Net Closure' { in b = 3; in a = 10; } } }"
)


def _quoted_identities() -> list[tuple[str, str | None, list[str]]]:
    model, _ = syside.load_model(sysml_source=QUOTED)
    c = _owner(model, syside.CalculationUsage, "c")
    return [
        (str(c.qualified_name), f.declared_name, [t for t, _ in _redefinitions(f)])
        for f in _inputs(c)
    ]


def test_p1_quoted_qualified_names_match_the_prototype_log_spelling() -> None:
    """B4: `str(qualified_name)` quotes only the names that need it, as the fusion-tea log does.

    The prototype log spells a target as
    `integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in`:
    the plain package unquoted, the spaced name in single quotes. Two loads give equal text.
    """
    first = _quoted_identities()
    assert first == [
        ("'Quoted Pkg'::q::c", "b", ["'Quoted Pkg'::'Net Closure'::a"]),
        ("'Quoted Pkg'::q::c", "a", ["'Quoted Pkg'::'Net Closure'::b"]),
    ]
    assert _quoted_identities() == first
    plain = _owner(
        _load(
            "calc def 'Net Closure' { in a : Real; in b : Real; } "
            "part q { calc c : 'Net Closure' { in b = 3; in a = 10; } }"
        ),
        syside.CalculationUsage,
        "c",
    )
    assert _redefinitions(_inputs(plain)[0]) == [("P::'Net Closure'::a", True)]


def test_p1_an_anonymous_assert_owner_has_no_qualified_name_through_element_ref() -> None:
    """D9: `element_ref` gives an anonymous `assert constraint` no qualified name."""
    from agentic_mbse.sysml.element_refs import element_ref

    model = _load("part q { assert constraint : Le { in lim = 5; in x = 3; } }")
    (owner,) = list(model.elements(syside.AssertConstraintUsage))
    ref = element_ref(owner)
    assert ref.qualified_name is None
    assert ref.kind == "AssertConstraintUsage"
    assert [(f.declared_name, _redefinitions(f)) for f in _inputs(owner)] == [
        ("lim", [("P::Le::x", True)]),
        ("x", [("P::Le::lim", True)]),
    ]

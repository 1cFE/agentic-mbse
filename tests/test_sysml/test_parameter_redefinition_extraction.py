"""Tests for the positional-binding fact layer (`parameter_redefinition_extraction.py`).

The SysIDE behavior these rely on is pinned by `tests/learning/test_syside_input_redefinition.py`
and recorded in `.project/completed/20261018_positional-binding-check/learning-findings.md`. These tests
read it through the production extractor and `element_refs.py` instead.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import pytest

from agentic_mbse.sysml.constraint_extraction import extract_identified_constraint_facts
from agentic_mbse.sysml.parameter_redefinition_extraction import (
    extract_parameter_redefinitions,
    heritage_relationships,
    owned_features,
    sweep_owners,
)
from agentic_mbse.sysml.parameter_redefinition_facts import (
    Direction,
    InputRedefinitionFact,
    Origin,
    ParameterRedefinitionFacts,
    ParameterRole,
    RedefinitionFailure,
    RedefinitionFailureCause,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

syside = get_syside()

FIX = Path(__file__).parent.parent / "fixtures" / "positional_binding"
Cause = RedefinitionFailureCause


def load(path: Path) -> Any:
    model, _ = SysideAdapter.load_model([path])
    return model


def extract(path: Path, **seams: Any) -> ParameterRedefinitionFacts:
    return extract_parameter_redefinitions(load(path), **seams)


def owned_by(facts: ParameterRedefinitionFacts, owner: str) -> list[InputRedefinitionFact]:
    return [f for f in facts.facts if f.owner.qualified_name == owner]


def only(
    facts: ParameterRedefinitionFacts, *, owner: str, declared_name: str | None
) -> InputRedefinitionFact:
    (fact,) = [f for f in owned_by(facts, owner) if f.declared_name == declared_name]
    return fact


def targets(fact: InputRedefinitionFact) -> list[tuple[str | None, Origin]]:
    return [(r.formal.qualified_name, r.origin) for r in fact.redefinitions]


def failures(facts: ParameterRedefinitionFacts) -> list[tuple[Cause, int | None]]:
    return [(f.cause, f.subject.line if f.subject else None) for f in facts.failures]


def raise_for(name: str) -> Callable[[Any], Iterable[Any]]:
    def read(feature: Any) -> Iterable[Any]:
        if feature.declared_name == name:
            raise RuntimeError(f"simulated SysIDE heritage failure on {name}")
        return heritage_relationships(feature)

    return read


# ---- the stencil cases ----------------------------------------------------------------------


def test_mixed_spelling_gives_b_an_implied_target_and_the_by_name_input_an_explicit_one() -> None:
    facts = extract(FIX / "spelling" / "mixed_spelling.sysml")
    owner = "mixed_spelling::q::c"
    b = only(facts, owner=owner, declared_name="b")
    assert targets(b) == [("mixed_spelling::Sub::a", Origin.IMPLIED)]
    anon = only(facts, owner=owner, declared_name=None)
    assert targets(anon) == [("mixed_spelling::Sub::a", Origin.EXPLICIT)]
    assert facts.failures == ()


def test_unresolved_owner_type_is_a_failure_and_its_inputs_are_not_facts() -> None:
    facts = extract(FIX / "unresolved" / "unresolved_type.sysml")
    assert failures(facts) == [
        (Cause.UNRESOLVED_OWNER_TYPE, 13),
        (Cause.UNRESOLVED_OWNER_TYPE, 14),
    ]
    assert not owned_by(facts, "unresolved_type::q::c")
    assert not owned_by(facts, "unresolved_type::q::k")
    # The resolved definitions in the same file are still judged.
    assert [f.declared_name for f in owned_by(facts, "unresolved_type::Sub")] == ["a", "b"]


def test_raising_heritage_read_fails_one_input_and_keeps_the_rest() -> None:
    facts = extract(FIX / "prototype" / "calc_reversed.sysml", read_heritage=raise_for("b"))
    assert [(f.cause, f.subject.qualified_name if f.subject else None) for f in facts.failures] == [
        (Cause.REDEFINITIONS_UNREADABLE, "calc_reversed::Sub::b"),
        (Cause.REDEFINITIONS_UNREADABLE, "calc_reversed::q::c::b"),
    ]
    assert [f.declared_name for f in owned_by(facts, "calc_reversed::q::c")] == ["a"]
    assert "simulated SysIDE heritage failure on b" in facts.failures[0].detail


# ---- every failure cause ----------------------------------------------------------------------


def test_a_raising_owner_sweep_is_one_subjectless_failure() -> None:
    def broken(_model: Any) -> Iterable[Any]:
        raise RuntimeError("simulated sweep failure")

    facts = extract(FIX / "prototype" / "calc_reversed.sysml", list_owners=broken)
    assert facts.owners_enumerated is False
    assert facts.owners_inspected == 0
    assert facts.facts == ()
    assert facts.failures == (
        RedefinitionFailure(None, Cause.OWNERS_UNLISTED, "RuntimeError: simulated sweep failure"),
    )


def test_a_raising_owned_features_read_fails_that_owner_only() -> None:
    def read(owner: Any) -> Iterable[Any]:
        if owner.name == "c":
            raise RuntimeError("simulated owned_features failure")
        return owned_features(owner)

    facts = extract(FIX / "prototype" / "calc_reversed.sysml", read_owned_features=read)
    assert [(f.cause, f.subject.qualified_name if f.subject else None) for f in facts.failures] == [
        (Cause.INPUTS_UNLISTED, "calc_reversed::q::c")
    ]
    assert not owned_by(facts, "calc_reversed::q::c")
    assert [f.declared_name for f in owned_by(facts, "calc_reversed::Sub")] == ["a", "b"]


def test_unresolved_supertype_is_an_owner_failure() -> None:
    facts = extract(FIX / "unresolved" / "unresolved_supertype.sysml")
    assert failures(facts) == [(Cause.UNRESOLVED_OWNER_TYPE, 8)]
    assert facts.facts == ()
    assert "<placeholder Classifier>" in facts.failures[0].detail


def test_unresolved_subsetting_is_an_owner_failure() -> None:
    """Audit Advisory 1: a `:>` or `subsets` typo would otherwise leave the inputs reading new."""
    facts = extract(FIX / "unresolved" / "unresolved_subsetting.sysml")
    assert failures(facts) == [
        (Cause.UNRESOLVED_OWNER_TYPE, 14),
        (Cause.UNRESOLVED_OWNER_TYPE, 15),
    ]
    assert not owned_by(facts, "unresolved_subsetting::q::c")
    assert not owned_by(facts, "unresolved_subsetting::q::k")
    for failure in facts.failures:
        assert "explicit Subsetting targets an unresolved reference" in failure.detail
        assert "<placeholder Feature>" in failure.detail


def test_unresolved_input_redefinition_fails_that_input_and_judges_the_next() -> None:
    facts = extract(FIX / "unresolved" / "unresolved_input_redefinition.sysml")
    assert failures(facts) == [(Cause.UNRESOLVED_INPUT_REDEFINITION, 12)]
    b = only(facts, owner="unresolved_input_redefinition::q::c", declared_name="b")
    assert targets(b) == [("unresolved_input_redefinition::Sub::b", Origin.IMPLIED)]


def test_a_partial_run_without_the_definitions_gives_unverifiable_owners() -> None:
    facts = extract(FIX / "partial_run" / "designs")
    assert failures(facts) == [
        (Cause.UNRESOLVED_OWNER_TYPE, 5),
        (Cause.UNRESOLVED_OWNER_TYPE, 6),
    ]
    assert facts.facts == ()
    whole = extract(FIX / "partial_run")
    assert whole.failures == ()
    b = only(whole, owner="Use::q::c", declared_name="b")
    assert targets(b) == [("Defs::Sub::a", Origin.IMPLIED)]


class _Document:
    def __init__(self, tier: Any) -> None:
        self.document_tier = tier


class _StubOwner:
    """A non-live owner: the extractor reaches it only through the `list_owners` seam."""

    def __init__(self, document: _Document | None) -> None:
        self.document = document
        self.name = "library_owner"
        self.qualified_name = "Lib::library_owner"
        self.element_id = uuid5(NAMESPACE_URL, "Lib::library_owner")


def _with_owner(stub: Any) -> Callable[[Any], Iterable[Any]]:
    def owners(model: Any) -> Iterable[Any]:
        return [stub, *sweep_owners(model)]

    return owners


def test_tier_guard_skips_a_standard_library_owner_without_reading_it() -> None:
    """R6: the sweeps never return library owners, so the guard is tested with a stub."""
    stub = _StubOwner(_Document(syside.DocumentTier.StandardLibrary))
    plain = extract(FIX / "prototype" / "calc_reversed.sysml")
    guarded = extract(FIX / "prototype" / "calc_reversed.sysml", list_owners=_with_owner(stub))
    assert guarded == plain


def test_an_owner_whose_tier_cannot_be_read_is_a_failure() -> None:
    stub = _StubOwner(None)
    facts = extract(FIX / "prototype" / "calc_reversed.sysml", list_owners=_with_owner(stub))
    assert [f.cause for f in facts.failures] == [Cause.DOCUMENT_TIER_UNREADABLE]
    assert (
        facts.owners_inspected
        == extract(FIX / "prototype" / "calc_reversed.sysml").owners_inspected + 1
    )


class _StubInput:
    """A non-live input feature, handed to the extractor through `read_owned_features`."""

    def __init__(self, *, element_id: Any, membership: Any) -> None:
        self.element_id = element_id
        self.qualified_name = "calc_reversed::q::c::stub"
        self.declared_name = "stub"
        self.name = "stub"
        self.direction = "FeatureDirectionKind.In"
        self.owning_membership = membership
        self.document = None


def _extra_input(stub: _StubInput) -> Callable[[Any], Iterable[Any]]:
    def read(owner: Any) -> Iterable[Any]:
        features = list(owned_features(owner))
        return [*features, stub] if owner.name == "c" else features

    return read


def test_an_input_without_a_usable_identity_is_a_failure() -> None:
    stub = _StubInput(element_id="not-a-uuid", membership=None)
    facts = extract(
        FIX / "prototype" / "calc_reversed.sysml", read_owned_features=_extra_input(stub)
    )
    assert [f.cause for f in facts.failures] == [Cause.IDENTITY_UNAVAILABLE]
    assert len(owned_by(facts, "calc_reversed::q::c")) == 2


def test_an_input_without_an_owning_membership_has_an_unreadable_role() -> None:
    stub = _StubInput(element_id=uuid5(NAMESPACE_URL, "stub"), membership=None)
    facts = extract(
        FIX / "prototype" / "calc_reversed.sysml", read_owned_features=_extra_input(stub)
    )
    assert [f.cause for f in facts.failures] == [Cause.ROLE_UNREADABLE]


class MockRedefinition:
    """A non-live redefinition with no target; `is_instance` matches it by its MRO name."""

    redefined_feature = None
    is_implied = True


def test_a_redefinition_with_no_target_is_an_unreadable_target() -> None:
    def read(feature: Any) -> Iterable[Any]:
        relationships = list(heritage_relationships(feature))
        if feature.declared_name == "b" and feature.owner.name == "c":
            return [*relationships, MockRedefinition()]
        return relationships

    facts = extract(FIX / "prototype" / "calc_reversed.sysml", read_heritage=read)
    assert [(f.cause, f.subject.qualified_name if f.subject else None) for f in facts.failures] == [
        (Cause.TARGET_UNREADABLE, "calc_reversed::q::c::b")
    ]


# ---- what the facts say ------------------------------------------------------------------------


def test_roles_are_read_from_the_owning_membership() -> None:
    renamed = extract(FIX / "requirements" / "requirement_subject_renamed.sysml")
    owner = "requirement_subject_renamed::q::r"
    veh = only(renamed, owner=owner, declared_name="veh")
    assert veh.role is ParameterRole.SUBJECT
    assert [(r.formal.qualified_name, r.role) for r in veh.redefinitions] == [
        ("requirement_subject_renamed::R::v", ParameterRole.SUBJECT),
        ("Requirements::RequirementCheck::subj", ParameterRole.SUBJECT),
    ]
    assert only(renamed, owner=owner, declared_name="lo").role is ParameterRole.ORDINARY
    actor = extract(FIX / "requirements" / "requirement_actor.sysml")
    drv = only(actor, owner="requirement_actor::q::r", declared_name="drv")
    assert drv.role is ParameterRole.ACTOR
    assert [r.role for r in drv.redefinitions] == [ParameterRole.ACTOR]
    stakeholder = extract(FIX / "requirements" / "requirement_stakeholder.sysml")
    own = only(stakeholder, owner="requirement_stakeholder::q::r", declared_name="own")
    assert own.role is ParameterRole.STAKEHOLDER
    case = extract(FIX / "requirements" / "case_actor.sysml")
    assert only(case, owner="case_actor::q::uc", declared_name="d2").role is ParameterRole.ACTOR


def test_a_restated_parent_usage_owns_the_formals_it_restates() -> None:
    """S4 row 3: each input gets one target owned by the parent usage, one by the definition."""
    facts = extract(FIX / "types" / "subpart_restated_type_swap.sysml")
    b = only(facts, owner="subpart_restated_type_swap::Q4::c", declared_name="b")
    assert [
        (r.formal.qualified_name, r.owning_type.qualified_name, r.owning_type.kind)
        for r in b.redefinitions
    ] == [
        (
            "subpart_restated_type_swap::Q1::c::a",
            "subpart_restated_type_swap::Q1::c",
            "CalculationUsage",
        ),
        (
            "subpart_restated_type_swap::Sub::a",
            "subpart_restated_type_swap::Sub",
            "CalculationDefinition",
        ),
    ]
    assert {r.origin for r in b.redefinitions} == {Origin.IMPLIED}


def test_multiple_types_give_one_implied_target_per_type_and_names_from_the_formal() -> None:
    facts = extract(FIX / "prototype" / "multiple_types.sysml")
    b = only(facts, owner="multiple_types::q::c", declared_name="b")
    assert [(r.formal.qualified_name, r.name) for r in b.redefinitions] == [
        ("multiple_types::Sub::a", "a"),
        ("multiple_types::Add::p", "p"),
    ]
    assert b.direction is Direction.IN


def test_an_anonymous_assert_owner_has_no_qualified_name() -> None:
    facts = extract(FIX / "requirements" / "anonymous_assert_reversed.sysml")
    anonymous = [f for f in facts.facts if f.owner.kind == "AssertConstraintUsage"]
    assert [(f.owner.qualified_name, f.declared_name) for f in anonymous] == [
        (None, "lim"),
        (None, "x"),
    ]


def test_inout_inputs_are_recorded_with_their_direction(tmp_path: Path) -> None:
    path = tmp_path / "inout.sysml"
    path.write_text(
        "package P { private import ScalarValues::*; "
        "calc def S { inout a : Real; inout b : Real; } "
        "part q { calc c : S { inout b = 3; inout a = 10; } } }"
    )
    facts = extract(path)
    b = only(facts, owner="P::q::c", declared_name="b")
    assert b.direction is Direction.INOUT
    assert targets(b) == [("P::S::a", Origin.IMPLIED)]


def test_return_and_out_parameters_are_not_inputs() -> None:
    facts = extract(FIX / "dc3" / "dc3_serial_path_swap.sysml")
    names = [f.declared_name for f in owned_by(facts, "dc3_serial_path_swap::'Serial Path 8'")]
    assert names == [f"eta_0{i}_in" for i in range(1, 9)]


CONSTRAINT_FIXTURES = [
    FIX / "prototype" / "assert_constraint_byname.sysml",
    FIX / "prototype" / "assert_constraint_reversed.sysml",
    FIX / "prototype" / "constraint_reversed.sysml",
    FIX / "requirements" / "requirement_nested_constraint_reversed.sysml",
    FIX / "requirements" / "anonymous_assert_reversed.sysml",
    FIX / "partial_run",
]


@pytest.mark.parametrize("fixture", CONSTRAINT_FIXTURES, ids=lambda p: p.stem)
def test_item1_formal_targets_equal_this_facts_full_target_set(fixture: Path) -> None:
    """D21: Item 1's `ActualFact.formal_targets` is the same reading, without the origin mark.

    Item 1 keys actuals by SysIDE `name` (which falls back to the redefined formal's name), so
    the comparison is per usage over the multiset of each input's target set.
    """
    model = load(fixture)
    ours = extract_parameter_redefinitions(model)
    item1 = extract_identified_constraint_facts(model)
    compared = 0
    for usage in item1.usages:
        mine = [f for f in ours.facts if f.owner.element_id == usage.usage_id]
        theirs = sorted(tuple(a.formal_targets) for a in usage.fact.actuals)
        assert (
            sorted(
                tuple(sorted(r.formal.qualified_name or "" for r in f.redefinitions)) for f in mine
            )
            == theirs
        )
        compared += len(mine)
    assert compared > 0


# ---- order and determinism -------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    [
        FIX / "prototype" / "multiple_types.sysml",
        FIX / "unresolved" / "unresolved_type.sysml",
        FIX / "partial_scope",
        # Anonymous owner, two inputs on one line: SysIDE gives these elements a fresh
        # UUIDv4 per load, so any order that used the id would vary between loads.
        FIX / "requirements" / "anonymous_assert_reversed.sysml",
    ],
    ids=lambda p: p.stem,
)
def test_facts_and_failures_are_sorted_and_repeated_extractions_are_equal(fixture: Path) -> None:
    first = extract(fixture)
    for _ in range(5):
        again = extract(fixture)
        assert [(f.location, f.declared_name, targets(f)) for f in again.facts] == [
            (f.location, f.declared_name, targets(f)) for f in first.facts
        ]
        assert again.failures == first.failures
    assert list(first.facts) == sorted(first.facts, key=InputRedefinitionFact.sort_key)
    assert list(first.failures) == sorted(first.failures, key=RedefinitionFailure.sort_key)


def test_the_aggregate_rejects_unsorted_facts() -> None:
    facts = extract(FIX / "prototype" / "calc_reversed.sysml")
    with pytest.raises(ValueError, match="sorted"):
        ParameterRedefinitionFacts(True, 1, tuple(reversed(facts.facts)), ())


def test_only_owners_unlisted_has_no_subject() -> None:
    with pytest.raises(ValueError):
        RedefinitionFailure(None, Cause.INPUTS_UNLISTED, "x")

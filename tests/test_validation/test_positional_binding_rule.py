"""Pure tests of the positional-binding rule (`validation/positional_binding.decide`).

No SysIDE: facts are built by hand, so each step of the rule (design Implementation Notes,
D6-D9, D20) is tested on its own.
"""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid4, uuid5

from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.parameter_redefinition_facts import (
    Direction,
    InputRedefinitionFact,
    Origin,
    ParameterRedefinitionFacts,
    ParameterRole,
    RedefinedFormal,
    RedefinitionFailure,
    RedefinitionFailureCause,
)
from agentic_mbse.validation.positional_binding import (
    FindingReason,
    InputOutcome,
    PositionalResult,
    decide,
)
from agentic_mbse.validation.positional_pins import FindingIdentity

ORDINARY = ParameterRole.ORDINARY
SUBJECT = ParameterRole.SUBJECT
ACTOR = ParameterRole.ACTOR
STAKEHOLDER = ParameterRole.STAKEHOLDER


def ref(qualified_name: str | None, kind: str = "Feature") -> ElementRef:
    if qualified_name is None:
        return ElementRef(uuid4(), None, kind)
    return ElementRef(uuid5(NAMESPACE_URL, qualified_name), qualified_name, kind)


def _formal(
    qualified_name: str | None,
    name: str | None,
    owning_type: str,
    role: ParameterRole,
    origin: Origin,
) -> RedefinedFormal:
    return RedefinedFormal(
        formal=ref(qualified_name),
        name=name,
        owning_type=ref(owning_type, "CalculationDefinition"),
        role=role,
        origin=origin,
    )


def _owning_type(qualified_name: str | None) -> str:
    return qualified_name.rsplit("::", 1)[0] if qualified_name else "P::Anon"


def implied(
    qualified_name: str | None,
    name: str | None,
    *,
    owning_type: str | None = None,
    role: ParameterRole = ORDINARY,
) -> RedefinedFormal:
    return _formal(
        qualified_name, name, owning_type or _owning_type(qualified_name), role, Origin.IMPLIED
    )


def explicit(qualified_name: str, name: str, *, owning_type: str | None = None) -> RedefinedFormal:
    return _formal(
        qualified_name, name, owning_type or _owning_type(qualified_name), ORDINARY, Origin.EXPLICIT
    )


_Input = tuple[str | None, ParameterRole, tuple[RedefinedFormal, ...]]


def input_(
    name: str | None, *redefinitions: RedefinedFormal, role: ParameterRole = ORDINARY
) -> _Input:
    return (name, role, redefinitions)


def facts_of(
    *inputs: _Input, owner: str | None = "P::q::c", failures: tuple[RedefinitionFailure, ...] = ()
) -> ParameterRedefinitionFacts:
    owner_ref = ref(owner, "CalculationUsage")
    facts = [
        InputRedefinitionFact(
            owner=owner_ref,
            input=ref(None if owner is None or name is None else f"{owner}::{name}"),
            declared_name=name,
            direction=Direction.IN,
            role=role,
            location=SafeLocation(
                "m.sysml", line, None if owner is None or name is None else f"{owner}::{name}"
            ),
            redefinitions=redefinitions,
        )
        for line, (name, role, redefinitions) in enumerate(inputs, start=1)
    ]
    return ParameterRedefinitionFacts(
        owners_enumerated=True,
        owners_inspected=1,
        facts=tuple(sorted(facts, key=InputRedefinitionFact.sort_key)),
        failures=failures,
    )


def identities(result: PositionalResult) -> set[tuple[str, str, str]]:
    return {
        (f.identity.owner, f.identity.input, f.identity.target)
        for f in result.findings
        if f.identity is not None
    }


def outcomes(result: PositionalResult) -> dict[InputOutcome, int]:
    return {outcome: count for outcome, count in result.outcomes.items() if count}


# ---- the stencil cases -----------------------------------------------------------------------


def test_other_inputs_explicit_redefinition_does_not_exempt_b() -> None:
    """Mixed spelling: `:>> a` on another input does not account for `b`'s implied Sub::a."""
    facts = facts_of(
        input_("b", implied("P::Sub::a", "a")), input_(None, explicit("P::Sub::a", "a"))
    )
    result = decide(facts)
    assert identities(result) == {("P::q::c", "b", "P::Sub::a")}
    assert outcomes(result) == {InputOutcome.IMPLICIT_MISMATCH: 1, InputOutcome.EXPLICIT: 1}


def test_special_role_target_gets_special_slot_reason() -> None:
    facts = facts_of(
        input_("lo", implied("Requirements::RequirementCheck::subj", "subj", role=SUBJECT)),
        owner="P::X",
    )
    (finding,) = decide(facts).findings
    assert finding.reason is FindingReason.SPECIAL_SLOT
    assert finding.identity == FindingIdentity("P::X", "lo", "Requirements::RequirementCheck::subj")


# ---- each step of the rule, in order ---------------------------------------------------------


def test_step1_a_special_role_input_is_never_judged() -> None:
    for role in (SUBJECT, ACTOR, STAKEHOLDER):
        facts = facts_of(input_("veh", implied("P::R::v", "v", role=role), role=role))
        result = decide(facts)
        assert result.findings == ()
        assert outcomes(result) == {InputOutcome.SPECIAL_PARAMETER: 1}


def test_step2_an_input_without_a_declared_name_is_never_flagged() -> None:
    facts = facts_of(
        input_(None, implied("P::Sub::a", "a")),
        input_(None, explicit("P::Sub::b", "b")),
    )
    result = decide(facts)
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.ANONYMOUS: 1, InputOutcome.EXPLICIT: 1}


def test_step3_no_implied_redefinition_is_explicit_or_a_new_parameter() -> None:
    facts = facts_of(input_("local", explicit("P::Sub::a", "a")), input_("extra"))
    result = decide(facts)
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.EXPLICIT: 1, InputOutcome.NEW_PARAMETER: 1}


def test_step4_a_same_named_implied_target_matches() -> None:
    result = decide(facts_of(input_("a", implied("P::Sub::a", "a"))))
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.IMPLICIT_MATCHING: 1}


def test_step4_a_differently_named_implied_target_is_a_swap() -> None:
    result = decide(
        facts_of(input_("b", implied("P::Sub::a", "a")), input_("a", implied("P::Sub::b", "b")))
    )
    assert identities(result) == {("P::q::c", "b", "P::Sub::a"), ("P::q::c", "a", "P::Sub::b")}
    assert {f.reason for f in result.findings} == {FindingReason.SWAP}
    assert outcomes(result) == {InputOutcome.IMPLICIT_MISMATCH: 2}


# ---- D6: one finding per (input, implied target) ---------------------------------------------


def test_d6_a_multiply_typed_input_gives_one_finding_per_mismatched_target() -> None:
    facts = facts_of(
        input_("b", implied("P::Sub::a", "a"), implied("P::Add::p", "p")),
        input_("a", implied("P::Sub::b", "b"), implied("P::Add::q", "q")),
    )
    assert identities(decide(facts)) == {
        ("P::q::c", "b", "P::Sub::a"),
        ("P::q::c", "b", "P::Add::p"),
        ("P::q::c", "a", "P::Sub::b"),
        ("P::q::c", "a", "P::Add::q"),
    }


def test_d6_a_restated_parent_usage_and_its_definition_give_two_findings_per_input() -> None:
    """S4 row 3: targets owned by the parent usage and by the definition are both judged."""
    facts = facts_of(
        input_("b", implied("P::Q1::c::a", "a"), implied("P::Sub::a", "a")),
        owner="P::Q4::c",
    )
    assert identities(decide(facts)) == {
        ("P::Q4::c", "b", "P::Q1::c::a"),
        ("P::Q4::c", "b", "P::Sub::a"),
    }


def test_d6_only_the_mismatched_target_of_a_multiply_typed_input_is_flagged() -> None:
    """`multiple_types_with_rename`: `b` matches Sub::b and lands on Add::q."""
    result = decide(facts_of(input_("b", implied("P::Sub::b", "b"), implied("P::Add::q", "q"))))
    assert identities(result) == {("P::q::c", "b", "P::Add::q")}


# ---- D7: explicit redefinitions on the same input ---------------------------------------------


def test_d7_one_owning_type_any_explicit_redefinition_accounts_for_the_implied_target() -> None:
    result = decide(facts_of(input_("x", implied("P::Sub::a", "a"), explicit("P::Sub::b", "b"))))
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.EXPLICIT: 1}


def test_d7_several_owning_types_only_a_same_type_explicit_accounts_for_a_target() -> None:
    """No SysIDE 0.8.4 case (explicit inputs carry no implied targets, R1b); stated by D7."""
    facts = facts_of(
        input_(
            "x",
            explicit("P::Sub::a", "a"),
            implied("P::Sub::b", "b"),
            implied("P::Add::p", "p"),
        )
    )
    result = decide(facts)
    assert identities(result) == {("P::q::c", "x", "P::Add::p")}
    assert outcomes(result) == {InputOutcome.IMPLICIT_MISMATCH: 1}


def test_d7_several_owning_types_each_accounted_for_is_explicit() -> None:
    facts = facts_of(
        input_(
            "x",
            explicit("P::Sub::a", "a"),
            explicit("P::Add::p", "p"),
            implied("P::Sub::b", "b"),
            implied("P::Add::q", "q"),
        )
    )
    result = decide(facts)
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.EXPLICIT: 1}


# ---- D8: unnamed targets ----------------------------------------------------------------------


def test_d8_an_unnamed_target_is_not_flagged() -> None:
    result = decide(facts_of(input_("b", implied("P::Sub::anon", None))))
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.ANONYMOUS_TARGET: 1}


def test_d8_an_unnamed_target_beside_a_named_mismatch_still_flags_the_named_one() -> None:
    result = decide(
        facts_of(
            input_(
                "b", implied("P::Sub::anon", None, owning_type="P::Sub"), implied("P::Add::p", "p")
            )
        )
    )
    assert identities(result) == {("P::q::c", "b", "P::Add::p")}


# ---- D9: findings without a full identity ------------------------------------------------------


def test_d9_an_anonymous_owner_gives_findings_without_identity() -> None:
    facts = facts_of(
        input_("lim", implied("P::Le::x", "x")),
        input_("x", implied("P::Le::lim", "lim")),
        owner=None,
    )
    result = decide(facts)
    assert [
        (f.identity, f.input_name, f.target.formal.qualified_name) for f in result.findings
    ] == [
        (None, "lim", "P::Le::x"),
        (None, "x", "P::Le::lim"),
    ]


def test_d9_a_target_without_a_qualified_name_gives_a_finding_without_identity() -> None:
    (finding,) = decide(facts_of(input_("b", implied(None, "a", owning_type="P::Sub")))).findings
    assert finding.identity is None
    assert finding.input_name == "b"


# ---- D20: special-slot targets -----------------------------------------------------------------


def test_d20_each_special_role_target_gets_the_special_slot_reason() -> None:
    for role in (SUBJECT, ACTOR, STAKEHOLDER):
        result = decide(facts_of(input_("lo", implied("P::R::v", "v", role=role)), owner="P::r"))
        assert [(f.reason, f.identity) for f in result.findings] == [
            (FindingReason.SPECIAL_SLOT, FindingIdentity("P::r", "lo", "P::R::v"))
        ]


def test_d20_library_and_user_special_targets_on_one_input_are_each_findings() -> None:
    """M4 usage: `hi` lands on `R::lo` (a swap) and on the library subject slot."""
    facts = facts_of(
        input_(
            "hi",
            implied("P::R::lo", "lo"),
            implied("Requirements::RequirementCheck::subj", "subj", role=SUBJECT),
        ),
        owner="P::q::r",
    )
    assert sorted(
        (f.identity.target if f.identity else "", f.reason) for f in decide(facts).findings
    ) == [
        ("P::R::lo", FindingReason.SWAP),
        ("Requirements::RequirementCheck::subj", FindingReason.SPECIAL_SLOT),
    ]


def test_d20_a_same_named_special_target_is_not_flagged() -> None:
    result = decide(
        facts_of(
            input_("subj", implied("Requirements::RequirementCheck::subj", "subj", role=SUBJECT))
        )
    )
    assert result.findings == ()


# ---- failures, totals and order ----------------------------------------------------------------


def test_failures_pass_through_and_are_never_findings() -> None:
    failure = RedefinitionFailure(
        SafeLocation("m.sysml", 9, "P::q::k"), RedefinitionFailureCause.UNRESOLVED_OWNER_TYPE, "x"
    )
    result = decide(facts_of(input_("a", implied("P::Sub::a", "a")), failures=(failure,)))
    assert result.failures == (failure,)
    assert result.findings == ()


def test_every_outcome_is_counted_once_per_input_and_listed_in_full() -> None:
    facts = facts_of(
        input_("veh", role=SUBJECT),
        input_(None),
        input_("extra"),
        input_("a", implied("P::Sub::a", "a")),
        input_("b", implied("P::Sub::c", "c")),
        input_("local", explicit("P::Sub::d", "d")),
        input_("n", implied("P::Sub::anon", None)),
    )
    result = decide(facts)
    assert list(result.outcomes) == list(InputOutcome)
    assert dict(result.outcomes) == {outcome: 1 for outcome in InputOutcome}
    assert result.inputs_inspected == 7


def test_findings_are_sorted_by_location_then_identity() -> None:
    facts = facts_of(
        input_("z", implied("P::Sub::b", "b")),
        input_("y", implied("P::Sub::a", "a"), implied("P::Add::p", "p")),
    )
    result = decide(facts)
    assert [
        (f.location.line, f.input_name, f.target.formal.qualified_name) for f in result.findings
    ] == [
        (1, "z", "P::Sub::b"),
        (2, "y", "P::Add::p"),
        (2, "y", "P::Sub::a"),
    ]
    assert decide(facts) == result


def test_the_decision_layer_and_the_fact_types_import_neither_syside_nor_the_filesystem() -> None:
    """Design I6, checked on each module's import statements."""
    import ast
    from pathlib import Path

    import agentic_mbse

    root = Path(agentic_mbse.__file__).parent
    forbidden = {"syside", "os", "pathlib", "shutil", "io", "agentic_mbse.sysml.syside_adapter"}
    for module in (
        "validation/positional_binding.py",
        "validation/positional_pins.py",
        "sysml/parameter_redefinition_facts.py",
    ):
        tree = ast.parse((root / module).read_text())
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        assert not {
            name for name in imported if name.split(".")[0] in forbidden or name in forbidden
        }, module

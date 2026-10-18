"""Pure tests of the positional-binding rule (`validation/positional_binding.decide`).

No SysIDE: facts are built by hand, so each step of the rule (design Implementation Notes,
D6-D9, D20) and the pin judgement (D13, I2) is tested on its own.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path, PurePosixPath
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
    PinScope,
    PositionalResult,
    StalePin,
    StaleReason,
    decide,
)
from agentic_mbse.validation.positional_pins import FindingIdentity, Pin, PinList

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
    result = decide(facts, None)
    assert identities(result) == {("P::q::c", "b", "P::Sub::a")}
    assert outcomes(result) == {InputOutcome.IMPLICIT_MISMATCH: 1, InputOutcome.EXPLICIT: 1}


def test_special_role_target_gets_special_slot_reason() -> None:
    facts = facts_of(
        input_("lo", implied("Requirements::RequirementCheck::subj", "subj", role=SUBJECT)),
        owner="P::X",
    )
    (finding,) = decide(facts, None).findings
    assert finding.reason is FindingReason.SPECIAL_SLOT
    assert finding.identity == FindingIdentity("P::X", "lo", "Requirements::RequirementCheck::subj")


# ---- each step of the rule, in order ---------------------------------------------------------


def test_step1_a_special_role_input_is_never_judged() -> None:
    for role in (SUBJECT, ACTOR, STAKEHOLDER):
        facts = facts_of(input_("veh", implied("P::R::v", "v", role=role), role=role))
        result = decide(facts, None)
        assert result.findings == ()
        assert outcomes(result) == {InputOutcome.SPECIAL_PARAMETER: 1}


def test_step2_an_input_without_a_declared_name_is_never_flagged() -> None:
    facts = facts_of(
        input_(None, implied("P::Sub::a", "a")),
        input_(None, explicit("P::Sub::b", "b")),
    )
    result = decide(facts, None)
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.ANONYMOUS: 1, InputOutcome.EXPLICIT: 1}


def test_step3_no_implied_redefinition_is_explicit_or_a_new_parameter() -> None:
    facts = facts_of(input_("local", explicit("P::Sub::a", "a")), input_("extra"))
    result = decide(facts, None)
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.EXPLICIT: 1, InputOutcome.NEW_PARAMETER: 1}


def test_step4_a_same_named_implied_target_matches() -> None:
    result = decide(facts_of(input_("a", implied("P::Sub::a", "a"))), None)
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.IMPLICIT_MATCHING: 1}


def test_step4_a_differently_named_implied_target_is_a_swap() -> None:
    result = decide(
        facts_of(input_("b", implied("P::Sub::a", "a")), input_("a", implied("P::Sub::b", "b"))),
        None,
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
    assert identities(decide(facts, None)) == {
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
    assert identities(decide(facts, None)) == {
        ("P::Q4::c", "b", "P::Q1::c::a"),
        ("P::Q4::c", "b", "P::Sub::a"),
    }


def test_d6_only_the_mismatched_target_of_a_multiply_typed_input_is_flagged() -> None:
    """`multiple_types_with_rename`: `b` matches Sub::b and lands on Add::q."""
    result = decide(
        facts_of(input_("b", implied("P::Sub::b", "b"), implied("P::Add::q", "q"))), None
    )
    assert identities(result) == {("P::q::c", "b", "P::Add::q")}


# ---- D7: explicit redefinitions on the same input ---------------------------------------------


def test_d7_one_owning_type_any_explicit_redefinition_accounts_for_the_implied_target() -> None:
    result = decide(
        facts_of(input_("x", implied("P::Sub::a", "a"), explicit("P::Sub::b", "b"))), None
    )
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
    result = decide(facts, None)
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
    result = decide(facts, None)
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.EXPLICIT: 1}


# ---- D8: unnamed targets ----------------------------------------------------------------------


def test_d8_an_unnamed_target_is_not_flagged() -> None:
    result = decide(facts_of(input_("b", implied("P::Sub::anon", None))), None)
    assert result.findings == ()
    assert outcomes(result) == {InputOutcome.ANONYMOUS_TARGET: 1}


def test_d8_an_unnamed_target_beside_a_named_mismatch_still_flags_the_named_one() -> None:
    result = decide(
        facts_of(
            input_(
                "b", implied("P::Sub::anon", None, owning_type="P::Sub"), implied("P::Add::p", "p")
            )
        ),
        None,
    )
    assert identities(result) == {("P::q::c", "b", "P::Add::p")}


# ---- D9: findings without a full identity ------------------------------------------------------


def test_d9_an_anonymous_owner_gives_findings_without_identity() -> None:
    facts = facts_of(
        input_("lim", implied("P::Le::x", "x")),
        input_("x", implied("P::Le::lim", "lim")),
        owner=None,
    )
    result = decide(facts, None)
    assert [
        (f.identity, f.input_name, f.target.formal.qualified_name) for f in result.findings
    ] == [
        (None, "lim", "P::Le::x"),
        (None, "x", "P::Le::lim"),
    ]


def test_d9_a_target_without_a_qualified_name_gives_a_finding_without_identity() -> None:
    (finding,) = decide(
        facts_of(input_("b", implied(None, "a", owning_type="P::Sub"))), None
    ).findings
    assert finding.identity is None
    assert finding.input_name == "b"


# ---- D20: special-slot targets -----------------------------------------------------------------


def test_d20_each_special_role_target_gets_the_special_slot_reason() -> None:
    for role in (SUBJECT, ACTOR, STAKEHOLDER):
        result = decide(
            facts_of(input_("lo", implied("P::R::v", "v", role=role)), owner="P::r"), None
        )
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
        (f.identity.target if f.identity else "", f.reason) for f in decide(facts, None).findings
    ) == [
        ("P::R::lo", FindingReason.SWAP),
        ("Requirements::RequirementCheck::subj", FindingReason.SPECIAL_SLOT),
    ]


def test_d20_a_same_named_special_target_is_not_flagged() -> None:
    result = decide(
        facts_of(
            input_("subj", implied("Requirements::RequirementCheck::subj", "subj", role=SUBJECT))
        ),
        None,
    )
    assert result.findings == ()


# ---- failures, totals and order ----------------------------------------------------------------


def test_failures_pass_through_and_are_never_findings() -> None:
    failure = RedefinitionFailure(
        SafeLocation("m.sysml", 9, "P::q::k"), RedefinitionFailureCause.UNRESOLVED_OWNER_TYPE, "x"
    )
    result = decide(facts_of(input_("a", implied("P::Sub::a", "a")), failures=(failure,)), None)
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
    result = decide(facts, None)
    assert list(result.outcomes) == list(InputOutcome)
    assert dict(result.outcomes) == {outcome: 1 for outcome in InputOutcome}
    assert result.inputs_inspected == 7


def test_findings_are_sorted_by_location_then_identity() -> None:
    facts = facts_of(
        input_("z", implied("P::Sub::b", "b")),
        input_("y", implied("P::Sub::a", "a"), implied("P::Add::p", "p")),
    )
    result = decide(facts, None)
    assert [
        (f.location.line, f.input_name, f.target.formal.qualified_name) for f in result.findings
    ] == [
        (1, "z", "P::Sub::b"),
        (2, "y", "P::Add::p"),
        (2, "y", "P::Sub::a"),
    ]
    assert decide(facts, None) == result


def test_the_decision_layer_and_the_fact_types_import_neither_syside_nor_the_filesystem() -> None:
    """Design I6, checked on each module's import statements."""
    import ast

    import agentic_mbse

    root = Path(agentic_mbse.__file__).parent
    forbidden = {
        "syside",
        "os",
        "pathlib",
        "shutil",
        "io",
        "agentic_mbse.sysml.syside_adapter",
        "agentic_mbse.sysml.parameter_redefinition_extraction",
    }
    # `positional_pins.py` is the pin loader, which reads the filesystem by design; the
    # decision layer imports only its types. Pure paths (`PurePosixPath`) touch no filesystem.
    for module in (
        "validation/positional_binding.py",
        "sysml/parameter_redefinition_facts.py",
    ):
        tree = ast.parse((root / module).read_text())
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and not (
                node.module == "pathlib" and all(a.name.startswith("Pure") for a in node.names)
            )
        }
        assert not {
            name for name in imported if name.split(".")[0] in forbidden or name in forbidden
        }, module


# ---- pins (D13, I2) ----------------------------------------------------------------------------

B_ON_A = FindingIdentity("P::q::c", "b", "P::Sub::a")
A_ON_B = FindingIdentity("P::q::c", "a", "P::Sub::b")
SWAPPED = (input_("b", implied("P::Sub::a", "a")), input_("a", implied("P::Sub::b", "b")))


def pin(identity: FindingIdentity, file: str = "models/a.sysml", line: int = 1) -> Pin:
    return Pin(identity, PurePosixPath(file), line)


def scope(
    *pins: Pin, validated: tuple[str, ...] = ("models/a.sysml",), existing: tuple[str, ...] = ()
) -> PinScope:
    pin_list = PinList(
        Path("pins.toml"),
        Path("."),
        "r",
        date(2026, 10, 15),
        tuple(sorted(pins, key=lambda p: p.identity)),
    )
    return PinScope(
        pin_list=pin_list,
        validated_files=frozenset(PurePosixPath(f) for f in validated),
        existing_files=frozenset(PurePosixPath(f) for f in (*validated, *existing)),
    )


def pinned(result: PositionalResult) -> dict[FindingIdentity | None, bool]:
    return {f.identity: f.pinned for f in result.findings}


def test_without_a_pin_list_every_finding_is_unpinned() -> None:
    result = decide(facts_of(*SWAPPED), None)
    assert pinned(result) == {B_ON_A: False, A_ON_B: False}
    assert result.stale == result.out_of_scope == result.not_judged == ()


def test_only_an_exact_identity_is_pinned() -> None:
    result = decide(facts_of(*SWAPPED), scope(pin(B_ON_A)))
    assert pinned(result) == {B_ON_A: True, A_ON_B: False}
    assert result.stale == ()


def test_matching_ignores_the_pins_file_and_line() -> None:
    """D13: a moved owner still matches; the file only decides scope for an unmatched pin."""
    result = decide(facts_of(*SWAPPED), scope(pin(B_ON_A, "models/elsewhere.sysml", 99)))
    assert pinned(result)[B_ON_A] is True
    assert result.stale == result.out_of_scope == ()


def test_a_finding_without_identity_is_never_pinned() -> None:
    """D9: an anonymous owner's finding stays an ERROR even with a pin list present."""
    facts = facts_of(input_("b", implied("P::Le::x", "x")), owner=None)
    result = decide(facts, scope(pin(FindingIdentity("P::anon", "b", "P::Le::x"))))
    assert [(f.identity, f.pinned) for f in result.findings] == [(None, False)]


def test_an_unmatched_pin_in_a_validated_file_is_stale() -> None:
    lost = pin(FindingIdentity("P::q::d", "x", "P::Sub::a"), "models/a.sysml", 4)
    result = decide(facts_of(*SWAPPED), scope(lost))
    assert result.stale == (StalePin(lost, StaleReason.NOT_FOUND_IN_VALIDATED_FILE),)
    assert result.out_of_scope == ()


def test_an_unmatched_pin_whose_file_is_missing_is_stale() -> None:
    gone = pin(FindingIdentity("P::q::d", "x", "P::Sub::a"), "models/gone.sysml")
    result = decide(facts_of(*SWAPPED), scope(gone))
    assert result.stale == (StalePin(gone, StaleReason.PINNED_FILE_MISSING),)


def test_unmatched_pin_in_an_existing_unvalidated_file_is_out_of_scope() -> None:
    other = pin(FindingIdentity("P::q::d", "x", "P::Sub::a"), "models/b.sysml")
    result = decide(facts_of(), scope(other, existing=("models/b.sysml",)))
    assert result.out_of_scope == (other,)
    assert result.stale == ()


def test_a_changed_target_is_a_new_unpinned_finding_and_a_stale_pin() -> None:
    """Pol-1: the pin names the old target; the new identity is not pinned."""
    facts = facts_of(input_("b", implied("P::Sub::c", "c")))
    old = pin(B_ON_A)
    result = decide(facts, scope(old))
    assert pinned(result) == {FindingIdentity("P::q::c", "b", "P::Sub::c"): False}
    assert result.stale == (StalePin(old, StaleReason.NOT_FOUND_IN_VALIDATED_FILE),)


def test_a_pin_for_an_owner_that_could_not_be_inspected_is_not_judged() -> None:
    """Insp-1: a pin changes nothing where inspection failed; the failure is the ERROR."""
    failure = RedefinitionFailure(
        SafeLocation("models/a.sysml", 3, "P::q::k"),
        RedefinitionFailureCause.UNRESOLVED_OWNER_TYPE,
        "x",
    )
    on_k = pin(FindingIdentity("P::q::k", "b", "P::Sub::a"))
    result = decide(facts_of(*SWAPPED, failures=(failure,)), scope(on_k))
    assert result.not_judged == (on_k,)
    assert result.stale == result.out_of_scope == ()
    assert result.failures == (failure,)


def test_a_pin_for_an_input_that_could_not_be_inspected_is_not_judged() -> None:
    failure = RedefinitionFailure(
        SafeLocation("models/a.sysml", 3, "P::q::c::b"),
        RedefinitionFailureCause.REDEFINITIONS_UNREADABLE,
        "x",
    )
    facts = facts_of(input_("a", implied("P::Sub::b", "b")), failures=(failure,))
    result = decide(facts, scope(pin(B_ON_A), pin(A_ON_B)))
    assert result.not_judged == (pin(B_ON_A),)
    assert pinned(result) == {A_ON_B: True}


def test_when_owners_could_not_be_listed_no_unmatched_pin_is_judged() -> None:
    failure = RedefinitionFailure(None, RedefinitionFailureCause.OWNERS_UNLISTED, "x")
    facts = ParameterRedefinitionFacts(
        owners_enumerated=False, owners_inspected=0, facts=(), failures=(failure,)
    )
    result = decide(facts, scope(pin(B_ON_A), pin(A_ON_B, "models/gone.sysml")))
    assert result.not_judged == (pin(A_ON_B, "models/gone.sysml"), pin(B_ON_A))
    assert result.stale == ()


def test_stale_and_out_of_scope_pins_are_sorted_by_identity() -> None:
    pins = [
        pin(FindingIdentity(f"P::o{n}", "x", "P::Sub::a"), f, n)
        for n, f in [
            (3, "models/a.sysml"),
            (1, "models/b.sysml"),
            (2, "models/a.sysml"),
            (0, "models/b.sysml"),
        ]
    ]
    result = decide(facts_of(), scope(*reversed(pins), existing=("models/b.sysml",)))
    assert [s.pin.identity.owner for s in result.stale] == ["P::o2", "P::o3"]
    assert [p.identity.owner for p in result.out_of_scope] == ["P::o0", "P::o1"]

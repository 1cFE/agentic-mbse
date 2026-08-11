"""The walk: form gate, resolver, node-kind classification, `evaluate_profile`/`preflight`.

Drives `evaluate_profile` over the real neutral facts in `production_facts.json` (28 usages, all
six source forms) plus synthetic `ConstraintFacts` for the default-deny and absence cases the
production fixture doesn't exercise (mirrors how `unknown` category is covered — no golden pin).
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest

from agentic_mbse.sysml.constraint_extraction import (
    IdentifiedConstraintDefinition,
    IdentifiedConstraintFacts,
    IdentifiedConstraintUsage,
)
from agentic_mbse.sysml.constraint_facts import (
    ConstraintDefinitionFact,
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    IdentityFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
    parse,
)
from agentic_mbse.sysml.executable_profile import (
    Eligibility,
    evaluate_identified_profile,
    evaluate_profile,
    preflight,
    preflight_identified,
)
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import FeatureReferenceNode, LiteralNode, OperatorNode

_OWNER = OwnerFact(
    owner=None, owning_definition=OwningDefinitionFact(kind="package", qualified_name="Synthetic")
)

FACTS = parse(Path("tests/fixtures/constraint_fact_shapes/production_facts.json").read_text())


def _decision(name: str):
    return next(d for d in evaluate_profile(FACTS).decisions if d.identity.name == name)


# === Form-gate outcomes (production facts) ===


@pytest.mark.parametrize(
    "name",
    ["positive_limit", "below_limit", "satisfied_limit", "named_usage"],
)
def test_non_asserted_forms_are_unassessed(name: str) -> None:
    decision = _decision(name)
    assert decision.eligibility is Eligibility.UNASSESSED
    assert decision.diagnostics == []
    assert decision.effective_predicate is None


def test_assert_by_reference_blocks() -> None:
    decisions = evaluate_profile(FACTS).decisions
    named_ref = next(
        d
        for d in decisions
        if d.eligibility is Eligibility.BLOCK
        and any(diag.reason == "block_assert_by_reference" for diag in d.diagnostics)
    )
    assert named_ref.diagnostics[0].reason == "block_assert_by_reference"
    assert named_ref.effective_predicate is None


def test_feature_chain_actual_is_admitted() -> None:
    """Spec [HARD]: an actual's binding expression is resolvability-checked, not walked for
    predicate-construct eligibility — a chain bound to a formal does not trip the chain block."""
    decision = _decision("typed_feature_chain_and_literal")
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


@pytest.mark.parametrize(
    "name",
    [
        "inline_owner_reference",
        "typed_omitted_default",
        "negated_inline",
        "calc_owned",
        "direct_owned",
        "inherited_limit",
    ],
)
def test_clean_admitted_asserts_are_silent(name: str) -> None:
    """Silent-on-clean (I2): a usage whose predicate uses only admitted constructs and passes
    every gate emits zero diagnostics."""
    decision = _decision(name)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []
    assert decision.effective_predicate is not None


@pytest.mark.parametrize(
    ("name", "reason"),
    [
        ("integer_real", "block_real_equality_requires_tolerance"),
        ("integer_integer", "block_integer_equality_unpreservable"),
        ("quantity_same_unit", "block_real_equality_requires_tolerance"),
        ("quantity_convertible_unit", "block_unit_conversion_required"),
        ("quantity_incompatible_dimension", "block_incompatible_dimensions"),
        ("unit_bearing_arithmetic", "block_real_equality_requires_tolerance"),
        ("unitless_dimensioned", "block_unitless_dimensioned"),
        ("quantity_feature_unknown_unit", "block_unknown_exact_unit"),
        ("unresolved_operand", "block_unresolved_operand"),
        ("inherited_alias_type", "block_real_equality_requires_tolerance"),
    ],
)
def test_golden_equality_matrix_reproduced_through_the_walk(name: str, reason: str) -> None:
    """Loud-on-gap: each blocked equality construct emits exactly the matching named block,
    reached end to end through the walk (not just the matrix helper directly)."""
    decision = _decision(name)
    assert decision.eligibility is Eligibility.BLOCK
    assert len(decision.diagnostics) == 1
    assert decision.diagnostics[0].reason == reason


@pytest.mark.parametrize(
    "name", ["enum_own", "enum_incompatible", "boolean_boolean", "string_string"]
)
def test_non_numerical_equality_warns(name: str) -> None:
    decision = _decision(name)
    assert decision.eligibility is Eligibility.NON_NUMERICAL
    assert [diagnostic.reason for diagnostic in decision.diagnostics] == [
        "warn_non_numerical_equality"
    ]
    assert all(diagnostic.force == "non_numerical" for diagnostic in decision.diagnostics)


def test_compound_boolean_nested_walk_reaches_every_leaf() -> None:
    """`(color == Color::red and integer_value <= real_value) or not (length_value == 0 [m])` —
    the nested and/or/not walk must recurse into every branch, not just the first. The third
    leaf (`length_value`, a quantity feature with a known dimension but no exact unit) is the
    one genuinely ineligible comparison here, so the walk must reach it through two levels of
    connective nesting and name it — not stop at the first two (admitted) branches."""
    decision = _decision("compound_boolean")
    assert decision.eligibility is Eligibility.BLOCK
    assert [diagnostic.reason for diagnostic in decision.diagnostics] == [
        "block_non_numerical_containment",
        "block_unknown_exact_unit",
    ]
    assert all(diagnostic.force == "error" for diagnostic in decision.diagnostics)


def test_nested_connectives_over_clean_operands_are_silent() -> None:
    """`(a and b) or not c`, every leaf a clean admitted comparison — nested and/or/not must not
    misfire on a genuinely clean predicate."""
    clean_comparison = OperatorNode(
        operator="<=", operands=[_leaf("real"), _leaf("real")], operand_type=None
    )
    predicate = OperatorNode(
        operator="or",
        operands=[
            OperatorNode(
                operator="and", operands=[clean_comparison, clean_comparison], operand_type=None
            ),
            OperatorNode(operator="not", operands=[clean_comparison], operand_type=None),
        ],
        operand_type=None,
    )
    facts = _facts(_inline_usage("nested_clean", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.diagnostics == []


def test_multiple_violations_in_one_predicate_all_accumulate() -> None:
    """A predicate with both a chain and an `xor` yields two diagnostics (design.md#architecture:
    "the *outcome* is singular (BLOCK), the *diagnostics* plural")."""
    predicate = OperatorNode(
        operator="and",
        operands=[
            OperatorNode(
                operator="<=",
                operands=[_leaf("real", chain_segments=["sensor", "reading"]), _leaf("real")],
                operand_type=None,
            ),
            OperatorNode(
                operator="xor", operands=[_leaf("boolean"), _leaf("boolean")], operand_type=None
            ),
        ],
        operand_type=None,
    )
    facts = _facts(_inline_usage("multiple_violations", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    reasons = {diag.reason for diag in decision.diagnostics}
    assert reasons == {
        "block_feature_chain",
        "block_non_numerical_containment",
    }
    assert all(diagnostic.force == "error" for diagnostic in decision.diagnostics)


# === Totality (I1) ===


def test_every_usage_yields_exactly_one_decision() -> None:
    result = evaluate_profile(FACTS)
    assert len(result.decisions) == len(FACTS.usages)
    for decision in result.decisions:
        assert decision.eligibility is not None


def test_profile_result_derived_counts() -> None:
    result = evaluate_profile(FACTS)
    assert (
        result.admitted_count
        + result.blocked_count
        + result.non_numerical_count
        + result.unassessed_count
        == len(result.decisions)
    )
    assert result.admitted_count > 0
    assert result.blocked_count > 0
    assert result.unassessed_count > 0


# === Synthetic default-deny + absence-case tests (no golden pin, mirrors `unknown`) ===


def _identity(name: str) -> IdentityFact:
    return IdentityFact(
        kind="AssertConstraintUsage", name=name, qualified_name=f"Synthetic::{name}"
    )


def _location() -> LocationFact:
    return LocationFact(file="synthetic.sysml", line=1, column=1)


def _leaf(category: str, *, chain_segments: list[str] | None = None) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name="x",
            target=None,
            target_types=[],
            chain_segments=chain_segments or [],
        ),
        operand_type=OperandTypeFact(category=category, enumeration=None, unit=None),
    )


def _inline_usage(name: str, predicate) -> ConstraintUsageFact:
    identity = _identity(name)
    return ConstraintUsageFact(
        identity=identity,
        location=_location(),
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=_OWNER,
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _facts(*usages: ConstraintUsageFact, definitions: list[ConstraintDefinitionFact] | None = None):
    return ConstraintFacts(
        definitions=definitions or [],
        usages=list(usages),
        contexts=[],
        diagnostics=[],
    )


def _typed_usage(name: str, definition: IdentityFact) -> ConstraintUsageFact:
    usage = _inline_usage(name, None)
    return replace(
        usage,
        source=ConstraintSource(
            form="definition_typed",
            effective_predicate_source=definition,
            constraint_definition=definition,
            referenced_feature_target=None,
            asserted_constraint=usage.identity,
        ),
    )


def test_identified_profile_selects_by_exact_id_and_is_total_across_all_outcomes() -> None:
    collision_identity = IdentityFact(
        kind="ConstraintDefinition", name="Collision", qualified_name="Synthetic::Collision"
    )
    anonymous_definition_identity = IdentityFact(
        kind="ConstraintDefinition", name=None, qualified_name=None
    )
    admitted_predicate = OperatorNode(
        operator="<=", operands=[_leaf("real"), _leaf("real")], operand_type=None
    )
    blocked_predicate = OperatorNode(
        operator="==", operands=[_leaf("integer"), _leaf("integer")], operand_type=None
    )
    colliding_admit = ConstraintDefinitionFact(
        identity=collision_identity, formals=[], predicate=admitted_predicate
    )
    colliding_block = ConstraintDefinitionFact(
        identity=collision_identity, formals=[], predicate=blocked_predicate
    )
    anonymous_admit = ConstraintDefinitionFact(
        identity=anonymous_definition_identity, formals=[], predicate=admitted_predicate
    )

    blocked_usage = _typed_usage("blocked", collision_identity)
    admitted_usage = _typed_usage("admitted", anonymous_definition_identity)
    anonymous_identity = IdentityFact(
        kind="AssertConstraintUsage", name=None, qualified_name=None
    )
    anonymous_non_numerical = replace(
        _inline_usage("display_only", _leaf("boolean")),
        identity=anonymous_identity,
        scope=anonymous_identity,
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=anonymous_identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=anonymous_identity,
        ),
    )
    unassessed_usage = replace(
        _inline_usage("unassessed", None),
        source=ConstraintSource(
            form="plain_usage",
            effective_predicate_source=None,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=None,
        ),
    )

    definition_ids = [UUID(int=index) for index in range(1, 4)]
    usage_ids = [UUID(int=index) for index in range(11, 15)]
    facts = ConstraintFacts(
        definitions=[colliding_admit, colliding_block, anonymous_admit],
        usages=[
            blocked_usage,
            admitted_usage,
            anonymous_non_numerical,
            unassessed_usage,
        ],
        contexts=[],
        diagnostics=[],
    )
    identified = IdentifiedConstraintFacts(
        facts=facts,
        definitions=(
            IdentifiedConstraintDefinition(definition_ids[2], anonymous_admit),
            IdentifiedConstraintDefinition(definition_ids[1], colliding_block),
            IdentifiedConstraintDefinition(definition_ids[0], colliding_admit),
        ),
        usages=tuple(
            reversed(
                (
                    IdentifiedConstraintUsage(usage_ids[0], definition_ids[1], blocked_usage),
                    IdentifiedConstraintUsage(usage_ids[1], definition_ids[2], admitted_usage),
                    IdentifiedConstraintUsage(
                        usage_ids[2], None, anonymous_non_numerical
                    ),
                    IdentifiedConstraintUsage(usage_ids[3], None, unassessed_usage),
                )
            )
        ),
    )

    result = evaluate_identified_profile(identified)

    assert {item.usage_id for item in result.decisions} == set(usage_ids)
    assert not result.missing_usage_ids
    assert result.by_usage_id[usage_ids[0]].effective_definition_id == definition_ids[1]
    assert result.by_usage_id[usage_ids[0]].decision.eligibility is Eligibility.BLOCK
    assert result.by_usage_id[usage_ids[1]].decision.eligibility is Eligibility.ADMIT
    assert result.by_usage_id[usage_ids[2]].decision.eligibility is Eligibility.NON_NUMERICAL
    assert result.by_usage_id[usage_ids[3]].decision.eligibility is Eligibility.UNASSESSED


def test_identified_profile_rejects_duplicate_usage_ids() -> None:
    usage = _inline_usage("duplicate", _leaf("boolean"))
    duplicate_id = UUID(int=99)
    identified = IdentifiedConstraintFacts(
        facts=_facts(usage),
        definitions=(),
        usages=(
            IdentifiedConstraintUsage(duplicate_id, None, usage),
            IdentifiedConstraintUsage(duplicate_id, None, usage),
        ),
    )

    with pytest.raises(ValueError, match="duplicate identified constraint usage UUID"):
        evaluate_identified_profile(identified)


def test_unknown_operand_category_blocks() -> None:
    predicate = OperatorNode(
        operator="==",
        operands=[_leaf("unknown"), _leaf("real")],
        operand_type=None,
    )
    facts = _facts(_inline_usage("unknown_category", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_unsupported_operand_category"


def test_operator_outside_admit_set_blocks() -> None:
    predicate = OperatorNode(
        operator="??",  # a future/unexpected operator, not in the admitted set
        operands=[_leaf("real"), _leaf("real")],
        operand_type=None,
    )
    facts = _facts(_inline_usage("weird_operator", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_unsupported_operator"


def test_not_equal_mirrors_equality_bucketing() -> None:
    predicate = OperatorNode(
        operator="!=", operands=[_leaf("integer"), _leaf("integer")], operand_type=None
    )
    facts = _facts(_inline_usage("not_equal", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_integer_equality_unpreservable"


def test_bare_boolean_predicate_root_warns() -> None:
    predicate = _leaf("boolean")
    facts = _facts(_inline_usage("bare_boolean", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.NON_NUMERICAL
    assert decision.diagnostics[0].reason == "warn_non_numerical_predicate"


def test_boolean_connective_operand_warns() -> None:
    predicate = OperatorNode(
        operator="and", operands=[_leaf("boolean"), _leaf("boolean")], operand_type=None
    )
    facts = _facts(_inline_usage("boolean_connective_operand", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.NON_NUMERICAL
    assert all(d.force == "non_numerical" for d in decision.diagnostics)


def test_feature_chain_in_predicate_body_blocks() -> None:
    predicate = OperatorNode(
        operator="<=",
        operands=[_leaf("real", chain_segments=["sensor", "reading"]), _leaf("real")],
        operand_type=None,
    )
    facts = _facts(_inline_usage("chain_in_body", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_feature_chain"


def test_pure_boolean_xor_warns() -> None:
    predicate = OperatorNode(
        operator="xor", operands=[_leaf("boolean"), _leaf("boolean")], operand_type=None
    )
    facts = _facts(_inline_usage("xor_predicate", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.NON_NUMERICAL
    assert decision.diagnostics[0].reason == "warn_non_numerical_xor"


def test_pure_boolean_implies_warns() -> None:
    predicate = OperatorNode(
        operator="implies", operands=[_leaf("boolean"), _leaf("boolean")], operand_type=None
    )
    facts = _facts(_inline_usage("implies_predicate", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.NON_NUMERICAL
    assert decision.diagnostics[0].reason == "warn_non_numerical_implies"


def test_invocation_blocks() -> None:
    from agentic_mbse.sysml.expression_ir import InvocationNode

    predicate = OperatorNode(
        operator="<=",
        operands=[
            InvocationNode(
                function_qn=["Calc", "size"],
                arguments=[],
                operand_type=OperandTypeFact(category="integer", enumeration=None, unit=None),
            ),
            _leaf("integer"),
        ],
        operand_type=None,
    )
    facts = _facts(_inline_usage("invocation_operand", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_invocation"


def test_unsupported_node_blocks_with_carried_diagnostic() -> None:
    from agentic_mbse.sysml.expression_ir import UnsupportedNode

    predicate = OperatorNode(
        operator="<=",
        operands=[
            UnsupportedNode(
                node_kind="RangeExpression", diagnostic="unrecognized node", source_text="1..5"
            ),
            _leaf("integer"),
        ],
        operand_type=None,
    )
    facts = _facts(_inline_usage("unsupported_operand", predicate))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_unsupported_node"
    assert decision.diagnostics[0].message == "unrecognized node"


# === Absence cases (MF2) ===


def test_bodyless_definition_blocks_missing_predicate() -> None:
    definition = ConstraintDefinitionFact(
        identity=IdentityFact(
            kind="ConstraintDefinition", name="Bodyless", qualified_name="Synthetic::Bodyless"
        ),
        formals=[],
        predicate=None,
    )
    identity = _identity("typed_by_bodyless")
    usage = ConstraintUsageFact(
        identity=identity,
        location=_location(),
        source=ConstraintSource(
            form="definition_typed",
            effective_predicate_source=definition.identity,
            constraint_definition=definition.identity,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=_OWNER,
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=None,
        inherited_into=[],
    )
    facts = _facts(usage, definitions=[definition])
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_missing_predicate"


def test_unresolved_definition_lookup_blocks() -> None:
    missing = IdentityFact(
        kind="ConstraintDefinition", name="Missing", qualified_name="Synthetic::Missing"
    )
    identity = _identity("typed_by_missing_definition")
    usage = ConstraintUsageFact(
        identity=identity,
        location=_location(),
        source=ConstraintSource(
            form="definition_typed",
            effective_predicate_source=missing,
            constraint_definition=missing,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=_OWNER,
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=None,
        inherited_into=[],
    )
    facts = _facts(usage, definitions=[])  # the lookup index is empty — a miss
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_unresolved_definition"


def test_inline_none_predicate_blocks_missing_predicate() -> None:
    """A degenerate inline assert (both fields `ExpressionIR | None`) — resolved-None, not a
    definition-lookup miss."""
    facts = _facts(_inline_usage("degenerate_inline", None))
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_missing_predicate"


def test_definitions_not_referenced_by_any_usage_do_not_appear_as_decisions() -> None:
    """I1: `facts.definitions` is read solely as the lookup index — an unused
    `ConstraintDefinition` is authoring inventory, not a profile subject."""
    unused_definition = ConstraintDefinitionFact(
        identity=IdentityFact(
            kind="ConstraintDefinition", name="Unused", qualified_name="Synthetic::Unused"
        ),
        formals=[],
        predicate=OperatorNode(
            operator="<=", operands=[_leaf("real"), _leaf("real")], operand_type=None
        ),
    )
    literal_predicate = OperatorNode(
        operator="<=",
        operands=[
            _leaf("real"),
            LiteralNode(
                literal=LiteralFact(
                    kind="LiteralRational", value=0.0, result_type="ScalarValues::Rational"
                ),
                operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
            ),
        ],
        operand_type=None,
    )
    facts = _facts(_inline_usage("only_usage", literal_predicate), definitions=[unused_definition])
    result = evaluate_profile(facts)
    assert len(result.decisions) == 1
    assert result.decisions[0].identity.name == "only_usage"


# === preflight ===


def test_preflight_partitions_by_outcome() -> None:
    result = preflight(FACTS)
    assert result.ok is False  # production_facts.json carries blocked would-execute asserts
    assert len(result.blocking) > 0
    assert len(result.admitted) > 0
    assert len(result.non_numerical) > 0
    assert len(result.unassessed) > 0
    assert len(result.blocking) + len(result.admitted) + len(result.non_numerical) + len(
        result.unassessed
    ) == len(FACTS.usages)
    assert all(d.eligibility is Eligibility.BLOCK for d in result.blocking)
    assert all(d.eligibility is Eligibility.ADMIT for d in result.admitted)
    assert all(d.eligibility is Eligibility.NON_NUMERICAL for d in result.non_numerical)
    assert all(d.eligibility is Eligibility.UNASSESSED for d in result.unassessed)


def test_preflight_ok_when_nothing_blocks() -> None:
    predicate = OperatorNode(
        operator="<=", operands=[_leaf("real"), _leaf("real")], operand_type=None
    )
    facts = _facts(_inline_usage("clean", predicate))
    result = preflight(facts)
    assert result.ok is True
    assert result.blocking == []
    assert len(result.admitted) == 1
    assert result.admitted[0].effective_predicate is predicate  # I5: the exact object, not a copy


# === preflight_identified (the exact gate) ===


def _admitting_predicate() -> OperatorNode:
    return OperatorNode(
        operator="<=", operands=[_leaf("real"), _leaf("real")], operand_type=None
    )


def _blocking_predicate() -> OperatorNode:
    return OperatorNode(
        operator="==", operands=[_leaf("integer"), _leaf("integer")], operand_type=None
    )


def _unassessed_usage(name: str) -> ConstraintUsageFact:
    return replace(
        _inline_usage(name, None),
        source=ConstraintSource(
            form="plain_usage",
            effective_predicate_source=None,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=None,
        ),
    )


def test_exact_gate_partitions_every_outcome_and_follows_the_uuid_association() -> None:
    """The exact gate blocks on the definition the UUID names, not the one the name finds."""
    shared_identity = IdentityFact(
        kind="ConstraintDefinition", name="Twin", qualified_name="Synthetic::Twin"
    )
    admitting_twin = ConstraintDefinitionFact(
        identity=shared_identity, formals=[], predicate=_admitting_predicate()
    )
    blocking_twin = ConstraintDefinitionFact(
        identity=shared_identity, formals=[], predicate=_blocking_predicate()
    )
    typed_usage = _typed_usage("typed_to_the_blocking_twin", shared_identity)
    admitted_usage = _inline_usage("admitted", _admitting_predicate())
    non_numerical_usage = _inline_usage("display_only", _leaf("boolean"))
    unassessed_usage = _unassessed_usage("unassessed")

    facts = ConstraintFacts(
        definitions=[admitting_twin, blocking_twin],
        usages=[typed_usage, admitted_usage, non_numerical_usage, unassessed_usage],
        contexts=[],
        diagnostics=[],
    )
    # The neutral payload cannot tell the twins apart: one qualified name, two predicates.
    assert len({definition.identity.qualified_name for definition in facts.definitions}) == 1

    admitting_id, blocking_id = UUID(int=201), UUID(int=202)
    usage_ids = [UUID(int=index) for index in range(211, 215)]
    identified = IdentifiedConstraintFacts(
        facts=facts,
        definitions=(
            IdentifiedConstraintDefinition(admitting_id, admitting_twin),
            IdentifiedConstraintDefinition(blocking_id, blocking_twin),
        ),
        usages=(
            IdentifiedConstraintUsage(usage_ids[0], blocking_id, typed_usage),
            IdentifiedConstraintUsage(usage_ids[1], None, admitted_usage),
            IdentifiedConstraintUsage(usage_ids[2], None, non_numerical_usage),
            IdentifiedConstraintUsage(usage_ids[3], None, unassessed_usage),
        ),
    )

    gate = preflight_identified(evaluate_identified_profile(identified))

    assert gate.ok is False
    assert [d.identity.name for d in gate.blocking] == ["typed_to_the_blocking_twin"]
    assert [d.diagnostics[0].reason for d in gate.blocking] == [
        "block_integer_equality_unpreservable"
    ]
    assert [d.identity.name for d in gate.admitted] == ["admitted"]
    assert [d.identity.name for d in gate.non_numerical] == ["display_only"]
    assert [d.identity.name for d in gate.unassessed] == ["unassessed"]
    assert (
        len(gate.blocking) + len(gate.admitted) + len(gate.non_numerical) + len(gate.unassessed)
        == len(identified.usages)
    )


def test_exact_gate_and_neutral_gate_agree_when_definition_identity_is_unambiguous() -> None:
    """The transitional neutral gate stays available and answers the same on shared input."""
    definition_identity = IdentityFact(
        kind="ConstraintDefinition", name="Sole", qualified_name="Synthetic::Sole"
    )
    definition = ConstraintDefinitionFact(
        identity=definition_identity, formals=[], predicate=_blocking_predicate()
    )
    typed_usage = _typed_usage("typed", definition_identity)
    usages = [
        typed_usage,
        _inline_usage("admitted", _admitting_predicate()),
        _inline_usage("display_only", _leaf("boolean")),
        _unassessed_usage("unassessed"),
    ]
    facts = ConstraintFacts(
        definitions=[definition], usages=usages, contexts=[], diagnostics=[]
    )
    identified = IdentifiedConstraintFacts(
        facts=facts,
        definitions=(IdentifiedConstraintDefinition(UUID(int=301), definition),),
        usages=tuple(
            IdentifiedConstraintUsage(
                UUID(int=311 + index),
                UUID(int=301) if usage is typed_usage else None,
                usage,
            )
            for index, usage in enumerate(usages)
        ),
    )

    neutral = preflight(facts)
    exact = preflight_identified(evaluate_identified_profile(identified))

    def buckets(gate):
        return {
            "ok": gate.ok,
            "blocking": [d.identity.name for d in gate.blocking],
            "admitted": [d.identity.name for d in gate.admitted],
            "non_numerical": [d.identity.name for d in gate.non_numerical],
            "unassessed": [d.identity.name for d in gate.unassessed],
        }

    assert buckets(exact) == buckets(neutral)
    assert exact.ok is False

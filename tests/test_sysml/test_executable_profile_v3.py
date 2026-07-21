"""Executable-profile v3 containment, force, ordering, and location contracts."""

from __future__ import annotations

import pytest

from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    IdentityFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.constraint_facts import (
    parse as parse_constraint_facts,
)
from agentic_mbse.sysml.constraint_facts import (
    serialize as serialize_constraint_facts,
)
from agentic_mbse.sysml.executable_profile import Eligibility, evaluate_profile
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import FeatureReferenceNode, OperatorNode


def _leaf(category: str, *, chained: bool = False) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name="x",
            target=None,
            target_types=[],
            chain_segments=["owner", "x"] if chained else [],
        ),
        operand_type=OperandTypeFact(category=category, enumeration=None, unit=None),
    )


def _comparison() -> OperatorNode:
    return OperatorNode(operator=">", operands=[_leaf("real"), _leaf("real")], operand_type=None)


def _decision(predicate: object, *, location=None):
    identity = IdentityFact(
        kind="AssertConstraintUsage", name="case", qualified_name="Synthetic::case"
    )
    usage = ConstraintUsageFact(
        identity=identity,
        location=location,
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Synthetic"),
        ),
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )
    return evaluate_profile(
        ConstraintFacts(definitions=[], usages=[usage], contexts=[], diagnostics=[])
    ).decisions[0]


def _round_trip_decision(predicate: object):
    identity = IdentityFact(
        kind="AssertConstraintUsage", name="case", qualified_name="Synthetic::case"
    )
    usage = ConstraintUsageFact(
        identity=identity,
        location=None,
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Synthetic"),
        ),
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )
    facts = ConstraintFacts(definitions=[], usages=[usage], contexts=[], diagnostics=[])
    parsed = parse_constraint_facts(serialize_constraint_facts(facts))
    return evaluate_profile(parsed).decisions[0]


@pytest.mark.parametrize(
    ("operator", "operand_count"),
    [(operator, count) for operator in ("xor", "implies") for count in (0, 1, 3)],
)
def test_malformed_binary_connective_round_trip_blocks(operator: str, operand_count: int) -> None:
    predicate = OperatorNode(
        operator=operator,
        operands=[_leaf("boolean") for _ in range(operand_count)],
        operand_type=None,
    )
    decision = _round_trip_decision(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_unsupported_node"
    assert f"{operand_count} operands, expected 2" in decision.diagnostics[0].message


def test_containment_mixed_and_boolean_flag_errors() -> None:
    predicate = OperatorNode(
        operator="and", operands=[_comparison(), _leaf("boolean")], operand_type=None
    )
    decision = _decision(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert [diagnostic.reason for diagnostic in decision.diagnostics] == [
        "block_non_numerical_containment"
    ]
    assert decision.diagnostics[0].force == "error"


def test_containment_xor_of_comparisons_errors() -> None:
    predicate = OperatorNode(
        operator="xor", operands=[_comparison(), _comparison()], operand_type=None
    )
    decision = _decision(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_non_numerical_containment"
    assert decision.diagnostics[0].force == "error"


def test_containment_pure_boolean_xor_warns_in_walk_order() -> None:
    predicate = OperatorNode(
        operator="xor", operands=[_leaf("boolean"), _leaf("boolean")], operand_type=None
    )
    decision = _decision(predicate)
    assert decision.eligibility is Eligibility.NON_NUMERICAL
    assert [diagnostic.reason for diagnostic in decision.diagnostics] == [
        "warn_non_numerical_xor",
        "warn_non_numerical_predicate",
        "warn_non_numerical_predicate",
    ]


@pytest.mark.parametrize("operator", ["xor", "implies"])
def test_binary_connective_well_formed_decisions_stay_pinned(operator: str) -> None:
    pure_boolean = OperatorNode(
        operator=operator,
        operands=[_leaf("boolean"), _leaf("boolean")],
        operand_type=None,
    )
    numerical = OperatorNode(
        operator=operator,
        operands=[_comparison(), _comparison()],
        operand_type=None,
    )
    assert _decision(pure_boolean).eligibility is Eligibility.NON_NUMERICAL
    assert _decision(numerical).eligibility is Eligibility.BLOCK


def test_malformed_branch_under_warn_connective_errors() -> None:
    malformed = OperatorNode(
        operator=">", operands=[_leaf("real", chained=True), _leaf("real")], operand_type=None
    )
    predicate = OperatorNode(
        operator="implies", operands=[_leaf("boolean"), malformed], operand_type=None
    )
    decision = _decision(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert all(diagnostic.force == "error" for diagnostic in decision.diagnostics)


def test_location_none_still_classifies() -> None:
    decision = _decision(_comparison(), location=None)
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.location is None


@pytest.mark.parametrize(
    "non_numerical",
    [
        _leaf("boolean"),
        OperatorNode(
            operator="==", operands=[_leaf("boolean"), _leaf("boolean")], operand_type=None
        ),
        OperatorNode(
            operator="xor", operands=[_leaf("boolean"), _leaf("boolean")], operand_type=None
        ),
        OperatorNode(
            operator="implies",
            operands=[_leaf("boolean"), _leaf("boolean")],
            operand_type=None,
        ),
    ],
    ids=["bare_boolean", "equality", "xor", "implies"],
)
def test_numerical_containment_promotes_error_semantics(non_numerical: object) -> None:
    predicate = OperatorNode(
        operator="and", operands=[_comparison(), non_numerical], operand_type=None
    )
    decision = _decision(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics
    for diagnostic in decision.diagnostics:
        assert diagnostic.force == "error"
        assert diagnostic.reason == "block_non_numerical_containment"
        assert "generation stops" in diagnostic.message
        assert "separate" in diagnostic.message
        assert "rewrite" in diagnostic.message
        assert "is not executed" not in diagnostic.message

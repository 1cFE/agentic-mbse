"""Executable-profile v3 containment, force, ordering, and location contracts."""

from __future__ import annotations

from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    IdentityFact,
    OwnerFact,
    OwningDefinitionFact,
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


def test_containment_mixed_and_boolean_flag_errors() -> None:
    predicate = OperatorNode(
        operator="and", operands=[_comparison(), _leaf("boolean")], operand_type=None
    )
    decision = _decision(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert [diagnostic.reason for diagnostic in decision.diagnostics] == [
        "warn_non_numerical_predicate"
    ]
    assert decision.diagnostics[0].force == "error"


def test_containment_xor_of_comparisons_errors() -> None:
    predicate = OperatorNode(
        operator="xor", operands=[_comparison(), _comparison()], operand_type=None
    )
    decision = _decision(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "warn_non_numerical_xor"
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

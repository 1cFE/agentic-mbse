"""Executable-profile v4 ordering and polarity contract."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    IdentityFact,
    OwnerFact,
    OwningDefinitionFact,
    parse,
    serialize,
)
from agentic_mbse.sysml.executable_profile import (
    PROFILE_SEMANTIC_VERSION,
    Eligibility,
    UsageDecision,
    classify_ordering,
    evaluate_profile,
)
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact, UnitFact
from agentic_mbse.sysml.expression_ir import FeatureReferenceNode, OperatorNode

CATEGORIES = ("boolean", "string", "integer", "real", "enum", "quantity", "unresolved", "unknown")
ORDERING_OPERATORS = ("<", "<=", ">", ">=")
NUMERICAL_PAIRS = {
    ("integer", "integer"),
    ("integer", "real"),
    ("real", "integer"),
    ("real", "real"),
    ("quantity", "quantity"),
}


def _operand(category: str) -> OperandTypeFact:
    unit = (
        UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit")
        if category == "quantity"
        else None
    )
    return OperandTypeFact(category=category, enumeration=None, unit=unit)


def _expected_reason(left: str, right: str) -> str:
    if "unresolved" in (left, right):
        return "block_unresolved_operand"
    if "unknown" in (left, right):
        return "block_unsupported_operand_category"
    if (left, right) not in NUMERICAL_PAIRS:
        return "block_ordering_category_pair"
    return "ok"


@pytest.mark.parametrize("operator", ORDERING_OPERATORS)
@pytest.mark.parametrize("left", CATEGORIES)
@pytest.mark.parametrize("right", CATEGORIES)
def test_ordering_product_has_fixed_exact_oracle(operator: str, left: str, right: str) -> None:
    assert classify_ordering(operator, _operand(left), _operand(right)) == _expected_reason(
        left, right
    )


def _facts(*, is_negated: object = False) -> ConstraintFacts:
    identity = IdentityFact(
        kind="AssertConstraintUsage", name="ordered", qualified_name="M::ordered"
    )
    predicate = OperatorNode(
        operator="<",
        operands=[
            FeatureReferenceNode(
                reference=FeatureReferenceFact(
                    source_name="a", target=None, target_types=[], chain_segments=[]
                ),
                operand_type=_operand("real"),
            ),
            FeatureReferenceNode(
                reference=FeatureReferenceFact(
                    source_name="b", target=None, target_types=[], chain_segments=[]
                ),
                operand_type=_operand("real"),
            ),
        ],
        operand_type=None,
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
            owner=None, owning_definition=OwningDefinitionFact(kind="package", qualified_name="M")
        ),
        scope=identity,
        membership_kind=None,
        is_negated=is_negated,  # type: ignore[arg-type]
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )
    return ConstraintFacts(definitions=[], usages=[usage], contexts=[], diagnostics=[])


@pytest.mark.parametrize("is_negated", [False, True])
def test_polarity_is_classified_without_rewriting_positive_body(is_negated: bool) -> None:
    facts = _facts(is_negated=is_negated)
    decision = evaluate_profile(facts).decisions[0]
    assert decision.eligibility is Eligibility.ADMIT
    assert decision.is_negated is is_negated
    assert decision.expected_value is (not is_negated)
    assert decision.effective_predicate is facts.usages[0].predicate


@pytest.mark.parametrize("raw", [None, "false", 0, 1, []])
def test_invalid_direct_polarity_blocks_before_body(raw: object) -> None:
    decision = evaluate_profile(_facts(is_negated=raw)).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.effective_predicate is None
    assert decision.is_negated is None
    assert decision.expected_value is None
    assert [item.reason for item in decision.diagnostics] == ["block_invalid_assertion_polarity"]


@pytest.mark.parametrize("raw", [None, "false", 0, 1, []])
def test_invalid_codec_polarity_blocks_before_body(raw: object) -> None:
    payload = json.loads(serialize(_facts()))
    payload["usages"][0]["is_negated"] = raw
    decision = evaluate_profile(parse(json.dumps(payload))).decisions[0]
    assert [item.reason for item in decision.diagnostics] == ["block_invalid_assertion_polarity"]


def test_usage_decision_state_validation_is_not_assert_based() -> None:
    valid = evaluate_profile(_facts()).decisions[0]
    with pytest.raises(ValueError, match="complementary"):
        replace(valid, expected_value=False)
    with pytest.raises(ValueError, match="requires Boolean polarity"):
        UsageDecision(
            identity=valid.identity,
            location=None,
            eligibility=Eligibility.ADMIT,
            diagnostics=[],
            unassessed_kind=None,
            effective_predicate=valid.effective_predicate,
            is_negated=None,
            expected_value=None,
        )


def test_profile_semantic_version_is_v4() -> None:
    assert PROFILE_SEMANTIC_VERSION == "executable-profile/v4"


def test_malformed_ordering_arity_uses_approved_exact_message() -> None:
    facts = _facts()
    predicate = facts.usages[0].predicate
    assert isinstance(predicate, OperatorNode)
    predicate.operands.pop()
    decision = evaluate_profile(facts).decisions[0]
    assert [item.message for item in decision.diagnostics] == [
        "comparison has 1 operands; expected 2"
    ]

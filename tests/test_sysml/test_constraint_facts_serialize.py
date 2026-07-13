"""Byte-stable canonical JSON round-trip for the constraint facts wire contract (D2/D3/D2a)."""

from __future__ import annotations

import json
import math

import pytest

from agentic_mbse.sysml.constraint_facts import (
    CONSTRAINT_FACTS_SCHEMA_VERSION,
    ActualFact,
    ConstraintDefinitionFact,
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    ContextFact,
    ExtractionDiagnosticFact,
    FormalFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
    RedefinitionFact,
    parse,
    serialize,
)
from agentic_mbse.sysml.expression_facts import (
    PREDICATE_TREE_SCHEMA_VERSION,
    ExpressionFact,
    FeatureReferenceFact,
    IdentityFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)


def _identity(kind: str, name: str | None, qualified_name: str | None) -> IdentityFact:
    return IdentityFact(kind=kind, name=name, qualified_name=qualified_name)


def _literal_expression(value: float) -> ExpressionFact:
    return ExpressionFact(
        predicate_schema_version=PREDICATE_TREE_SCHEMA_VERSION,
        kind="LiteralRational",
        operator=None,
        operands=[],
        reference=None,
        literal=LiteralFact(kind="LiteralRational", value=value, result_type="ScalarValues::Rational"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _reference_expression() -> ExpressionFact:
    return ExpressionFact(
        predicate_schema_version=PREDICATE_TREE_SCHEMA_VERSION,
        kind="FeatureReferenceExpression",
        operator=None,
        operands=[],
        reference=FeatureReferenceFact(
            source_name="limit",
            target=_identity("AttributeUsage", "limit", "WithinLimit::limit"),
            target_types=["ScalarValues::Real"],
            chain_segments=[],
        ),
        literal=None,
        operand_type=OperandTypeFact(
            category="quantity",
            enumeration=None,
            unit=UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit"),
        ),
    )


def _hand_built_facts() -> ConstraintFacts:
    predicate = ExpressionFact(
        predicate_schema_version=PREDICATE_TREE_SCHEMA_VERSION,
        kind="OperatorExpression",
        operator="<=",
        operands=[_reference_expression(), _literal_expression(10.0)],
        reference=None,
        literal=None,
        operand_type=None,
    )
    definition = ConstraintDefinitionFact(
        identity=_identity("ConstraintDefinition", "WithinLimit", "WithinLimit"),
        formals=[
            FormalFact(
                name="limit",
                qualified_name="WithinLimit::limit",
                types=["ScalarValues::Real"],
                has_default=True,
                default=_literal_expression(10.0),
            ),
            FormalFact(
                name="observed",
                qualified_name="WithinLimit::observed",
                types=["ScalarValues::Real"],
                has_default=False,
                default=None,
            ),
        ],
        predicate=predicate,
    )
    usage = ConstraintUsageFact(
        identity=_identity("AssertConstraintUsage", "inline_check", "Probe::inline_check"),
        location=LocationFact(file="probe.sysml", line=5, column=9),
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=_identity(
                "AssertConstraintUsage", "inline_check", "Probe::inline_check"
            ),
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=None,
        ),
        owner=OwnerFact(
            owner=_identity("PartDefinition", "Probe", "Probe"),
            owning_definition=OwningDefinitionFact(kind="part_def", qualified_name="Probe"),
        ),
        scope=_identity("AssertConstraintUsage", "inline_check", "Probe::inline_check"),
        membership_kind=None,
        is_negated=False,
        actuals=[
            ActualFact(
                name="limit",
                direction="in",
                formal_targets=["WithinLimit::limit"],
                value=_literal_expression(12.0),
            )
        ],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )
    context = ContextFact(
        identity=_identity("PartDefinition", "Probe", "Probe"),
        general_types=[],
        types=["Probe"],
        inherited_constraints=[],
        redefinitions=[
            RedefinitionFact(
                feature="Probe::observed",
                redefines="WithinLimit::observed",
                value=_literal_expression(5.0),
            )
        ],
    )
    return ConstraintFacts(
        schema_version=CONSTRAINT_FACTS_SCHEMA_VERSION,
        definitions=[definition],
        usages=[usage],
        contexts=[context],
        diagnostics=[],
    )


def _facts_with_non_finite_literal() -> ConstraintFacts:
    facts = _hand_built_facts()
    facts.usages[0].predicate = _literal_expression(math.inf)
    return facts


def test_round_trip_is_byte_identical() -> None:
    facts = _hand_built_facts()
    once = serialize(facts)
    assert serialize(parse(once)) == once


def test_every_field_present_absence_is_explicit_null() -> None:
    doc = json.loads(serialize(_hand_built_facts()))
    usage = doc["usages"][0]
    assert "membership_kind" in usage
    assert usage["membership_kind"] is None
    assert "referenced_feature_target" in usage["source"]
    assert usage["source"]["referenced_feature_target"] is None
    assert "unit" in usage["actuals"][0]["value"]["operand_type"]


def test_schema_versions_are_pinned() -> None:
    doc = json.loads(serialize(_hand_built_facts()))
    assert doc["schema_version"] == "constraint-facts/v1"
    assert doc["usages"][0]["predicate"]["predicate_schema_version"] == "predicate-tree/v0"


def test_non_finite_serialize_backstop() -> None:
    with pytest.raises(ValueError):
        serialize(_facts_with_non_finite_literal())


def test_diagnostic_fact_round_trips() -> None:
    facts = _hand_built_facts()
    facts.diagnostics.append(
        ExtractionDiagnosticFact(
            kind="non_finite_literal",
            message="Non-finite literal operand encountered during extraction",
            operand_source="1.0/0.0",
            location=LocationFact(file="probe.sysml", line=10, column=4),
        )
    )
    once = serialize(facts)
    assert serialize(parse(once)) == once

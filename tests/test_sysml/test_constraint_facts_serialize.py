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
    FeatureReferenceFact,
    IdentityFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)
from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    FeatureReferenceNode,
    LiteralNode,
    OperatorNode,
)


def _identity(kind: str, name: str | None, qualified_name: str | None) -> IdentityFact:
    return IdentityFact(kind=kind, name=name, qualified_name=qualified_name)


def _literal_expression(value: float) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(
            kind="LiteralRational", value=value, result_type="ScalarValues::Rational"
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _reference_expression() -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name="limit",
            target=_identity("AttributeUsage", "limit", "WithinLimit::limit"),
            target_types=["ScalarValues::Real"],
            chain_segments=[],
        ),
        operand_type=OperandTypeFact(
            category="quantity",
            enumeration=None,
            unit=UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit"),
        ),
    )


def _hand_built_facts() -> ConstraintFacts:
    predicate: ExpressionIR = OperatorNode(
        operator="<=",
        operands=[_reference_expression(), _literal_expression(10.0)],
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
    assert doc["schema_version"] == "constraint-facts/v2"
    assert doc["usages"][0]["predicate"]["schema_version"] == "expression-ir/v1"


def test_non_finite_serialize_backstop() -> None:
    with pytest.raises(ValueError):
        serialize(_facts_with_non_finite_literal())


# === Fail-closed envelope and node version gates (F2) ===


def test_foreign_envelope_version_is_rejected() -> None:
    doc = json.loads(serialize(_hand_built_facts()))
    doc["schema_version"] = "constraint-facts/v999"
    with pytest.raises(ValueError, match=r"constraint-facts/v999.*constraint-facts/v2"):
        parse(json.dumps(doc))


def test_missing_envelope_version_is_rejected() -> None:
    doc = json.loads(serialize(_hand_built_facts()))
    del doc["schema_version"]
    with pytest.raises(ValueError, match=r"missing 'schema_version'"):
        parse(json.dumps(doc))


def test_foreign_nested_node_version_is_rejected() -> None:
    doc = json.loads(serialize(_hand_built_facts()))
    doc["usages"][0]["predicate"]["schema_version"] = "expression-ir/v999"
    with pytest.raises(ValueError, match=r"expression-ir/v999.*expression-ir/v1"):
        parse(json.dumps(doc))


def test_envelope_version_is_not_caller_settable() -> None:
    # `schema_version` is init=False: callers cannot set the tag in the constructor.
    with pytest.raises(TypeError):
        ConstraintFacts(
            schema_version=CONSTRAINT_FACTS_SCHEMA_VERSION,  # type: ignore[call-arg]
            definitions=[],
            usages=[],
            contexts=[],
            diagnostics=[],
        )


def test_mutated_envelope_version_cannot_serialize() -> None:
    facts = _hand_built_facts()
    facts.schema_version = "constraint-facts/v999"
    with pytest.raises(ValueError, match=r"schema_version.*constraint-facts/v999"):
        serialize(facts)


def test_mutated_nested_expression_tag_cannot_serialize() -> None:
    facts = _hand_built_facts()
    assert facts.usages[0].predicate is not None
    facts.usages[0].predicate.kind = "hologram"
    with pytest.raises(ValueError, match=r"kind.*hologram"):
        serialize(facts)


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

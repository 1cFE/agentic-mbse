"""Offline, byte-stable round-trip for the bare ExpressionIR tree (no syside)."""

from __future__ import annotations

from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    IdentityFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)
from agentic_mbse.sysml.expression_ir import (
    EXPRESSION_IR_SCHEMA_VERSION,
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    UnsupportedNode,
    parse_expression,
    serialize_expression,
)


def _lit(value: float) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=value, result_type="ScalarValues::Rational"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _round_trips(node) -> None:
    once = serialize_expression(node)
    assert serialize_expression(parse_expression(once)) == once


def test_version_constant_is_pinned() -> None:
    assert EXPRESSION_IR_SCHEMA_VERSION == "expression-ir/v1"


def test_literal_node_round_trips_byte_identically() -> None:
    _round_trips(_lit(1.0))


def test_operator_node_round_trips_byte_identically() -> None:
    tree = OperatorNode(operator="<=", operands=[_lit(1.0), _lit(2.0)], operand_type=None)
    _round_trips(tree)


def test_feature_reference_node_round_trips_byte_identically() -> None:
    node = FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name="limit",
            target=IdentityFact(kind="AttributeUsage", name="limit", qualified_name="WithinLimit::limit"),
            target_types=["ScalarValues::Real"],
            chain_segments=[],
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )
    _round_trips(node)


def test_unit_annotation_node_round_trips_byte_identically() -> None:
    node = UnitAnnotationNode(
        value=_lit(1.0),
        unit_text="m",
        operand_type=OperandTypeFact(
            category="quantity", enumeration=None, unit=UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit")
        ),
    )
    _round_trips(node)


def test_invocation_node_round_trips_byte_identically() -> None:
    node = InvocationNode(
        function_qn=["Some", "func"],
        arguments=[_lit(1.0)],
        operand_type=None,
    )
    _round_trips(node)


def test_unsupported_node_round_trips_byte_identically() -> None:
    node = UnsupportedNode(
        node_kind="ConditionalExpression",
        diagnostic="unknown node type: ConditionalExpression",
        source_text="if base > 0.0 ? true else false",
    )
    _round_trips(node)

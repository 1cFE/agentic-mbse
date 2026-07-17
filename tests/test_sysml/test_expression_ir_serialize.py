"""Offline, byte-stable round-trip for the bare ExpressionIR tree (no syside),
plus the fail-closed decoder gates: foreign/missing `schema_version` and unknown/missing
`kind` are rejected, never silently rewritten."""

from __future__ import annotations

import json

import pytest

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
        literal=LiteralFact(
            kind="LiteralRational", value=value, result_type="ScalarValues::Rational"
        ),
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
            target=IdentityFact(
                kind="AttributeUsage", name="limit", qualified_name="WithinLimit::limit"
            ),
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
            category="quantity",
            enumeration=None,
            unit=UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit"),
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


# === Fail-closed decoder gates (F2) ===


def _lit_doc() -> dict:
    return json.loads(serialize_expression(_lit(1.0)))


def test_foreign_node_version_is_rejected_not_rewritten() -> None:
    doc = _lit_doc()
    doc["schema_version"] = "expression-ir/v999"
    with pytest.raises(ValueError, match=r"expression-ir/v999.*expression-ir/v1"):
        parse_expression(json.dumps(doc))


def test_missing_node_version_is_rejected() -> None:
    doc = _lit_doc()
    del doc["schema_version"]
    with pytest.raises(ValueError, match=r"missing 'schema_version'"):
        parse_expression(json.dumps(doc))


def test_foreign_version_on_nested_operand_is_rejected() -> None:
    tree = OperatorNode(operator="<=", operands=[_lit(1.0), _lit(2.0)], operand_type=None)
    doc = json.loads(serialize_expression(tree))
    doc["operands"][1]["schema_version"] = "expression-ir/v999"
    with pytest.raises(ValueError, match=r"expression-ir/v999.*expression-ir/v1"):
        parse_expression(json.dumps(doc))


def test_unknown_kind_is_a_clean_error_not_keyerror() -> None:
    doc = _lit_doc()
    doc["kind"] = "hologram"
    with pytest.raises(ValueError, match=r"unrecognized ExpressionIR kind.*hologram"):
        parse_expression(json.dumps(doc))


def test_missing_kind_is_a_clean_error_not_keyerror() -> None:
    doc = _lit_doc()
    del doc["kind"]
    with pytest.raises(ValueError, match=r"missing 'kind'"):
        parse_expression(json.dumps(doc))


def test_future_extra_field_is_ignored() -> None:
    # Pins the decoder's existing lenient stance: unknown keys are dropped on parse (the
    # decoder reads only the known slots), so re-serialization is canonical-v1 without them.
    doc = _lit_doc()
    doc["future_field"] = {"anything": True}
    parsed = parse_expression(json.dumps(doc))
    assert serialize_expression(parsed) == serialize_expression(_lit(1.0))


def test_wire_tags_are_not_caller_settable() -> None:
    # `kind`/`schema_version` are init=False: callers cannot set tags in constructors.
    with pytest.raises(TypeError):
        LiteralNode(
            literal=LiteralFact(kind="LiteralRational", value=1.0, result_type=None),
            operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
            schema_version="expression-ir/v999",  # type: ignore[call-arg]
        )
    with pytest.raises(TypeError):
        UnsupportedNode(
            node_kind="X",
            diagnostic="d",
            source_text=None,
            kind="literal",  # type: ignore[call-arg]
        )


def _all_node_factories():
    return [
        lambda: _lit(1.0),
        lambda: FeatureReferenceNode(
            reference=FeatureReferenceFact(
                source_name="x", target=None, target_types=[], chain_segments=[]
            ),
            operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
        ),
        lambda: OperatorNode(operator="+", operands=[_lit(1.0), _lit(2.0)], operand_type=None),
        lambda: UnitAnnotationNode(
            value=_lit(1.0),
            unit_text="m",
            operand_type=OperandTypeFact(
                category="quantity",
                enumeration=None,
                unit=UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit"),
            ),
        ),
        lambda: InvocationNode(function_qn=["f"], arguments=[_lit(1.0)], operand_type=None),
        lambda: UnsupportedNode(node_kind="X", diagnostic="unsupported", source_text=None),
    ]


@pytest.mark.parametrize("node_factory", _all_node_factories())
@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [("kind", "hologram"), ("schema_version", "expression-ir/v999")],
)
def test_mutated_wire_tags_cannot_serialize(node_factory, field_name, invalid_value) -> None:
    node = node_factory()
    setattr(node, field_name, invalid_value)
    with pytest.raises(ValueError, match=field_name):
        serialize_expression(node)

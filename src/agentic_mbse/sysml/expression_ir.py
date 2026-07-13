"""Production predicate tree: distinct node algebra, serialize/parse, canonical JSON.

One dataclass per algebra kind — literal, feature reference, operator, unit annotation,
invocation, and an explicit unsupported node — joined by a `kind`-tagged union. Reuses Item 1's
frozen leaf facts (`FeatureReferenceFact`, `LiteralFact`, `OperandTypeFact`, `UnitFact`)
unchanged. Imports `expression_facts` only — `constraint_facts` imports this module, not the
other way, keeping the import direction one-way.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import Any, TypeAlias

from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    IdentityFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)

__all__ = [
    "EXPRESSION_IR_SCHEMA_VERSION",
    "ExpressionIR",
    "FeatureReferenceNode",
    "InvocationNode",
    "LiteralNode",
    "OperatorNode",
    "UnitAnnotationNode",
    "UnsupportedNode",
    "parse_expression",
    "serialize_expression",
]

EXPRESSION_IR_SCHEMA_VERSION = "expression-ir/v1"


@dataclass
class LiteralNode:
    """A literal leaf node: a number, string, or boolean constant."""

    literal: LiteralFact
    operand_type: OperandTypeFact
    kind: str = "literal"
    schema_version: str = EXPRESSION_IR_SCHEMA_VERSION


@dataclass
class FeatureReferenceNode:
    """A feature reference leaf node: a plain reference or a feature chain."""

    reference: FeatureReferenceFact
    operand_type: OperandTypeFact
    kind: str = "feature_ref"
    schema_version: str = EXPRESSION_IR_SCHEMA_VERSION


@dataclass
class OperatorNode:
    """An n-ary operator node: arithmetic, comparison, or Boolean connective.

    `operand_type` is `None` on comparison/connective nodes — they are propositions, not
    values.
    """

    operator: str
    operands: list[ExpressionIR]
    operand_type: OperandTypeFact | None
    kind: str = "operator"
    schema_version: str = EXPRESSION_IR_SCHEMA_VERSION


@dataclass
class UnitAnnotationNode:
    """A `[` unit-annotation node: the annotated value plus the resolved unit.

    `unit_text` is the source spelling (`"m"`); the resolved `UnitFact` lives on
    `operand_type`.
    """

    value: ExpressionIR
    unit_text: str | None
    operand_type: OperandTypeFact
    kind: str = "unit"
    schema_version: str = EXPRESSION_IR_SCHEMA_VERSION


@dataclass
class InvocationNode:
    """An invocation node: a resolved function reference plus its arguments."""

    function_qn: list[str] | None
    arguments: list[ExpressionIR]
    operand_type: OperandTypeFact | None
    kind: str = "invocation"
    schema_version: str = EXPRESSION_IR_SCHEMA_VERSION


@dataclass
class UnsupportedNode:
    """An explicit fallback for a structurally unrepresentable expression node.

    Carries the unrecognized metaclass, a diagnostic message, and the reconstructed source
    text where available — never silently coerced into a productive node kind.
    """

    node_kind: str
    diagnostic: str
    source_text: str | None
    kind: str = "unsupported"
    schema_version: str = EXPRESSION_IR_SCHEMA_VERSION


ExpressionIR: TypeAlias = (
    LiteralNode
    | FeatureReferenceNode
    | OperatorNode
    | UnitAnnotationNode
    | InvocationNode
    | UnsupportedNode
)


def _canonical_json(obj: Any) -> str:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def serialize_expression(ir: ExpressionIR) -> str:
    """Render `ir` as canonical, byte-stable JSON (D2/D5)."""
    return _canonical_json(dataclasses.asdict(ir))


def _identity_from_dict(data: dict[str, Any] | None) -> IdentityFact | None:
    if data is None:
        return None
    return IdentityFact(kind=data["kind"], name=data["name"], qualified_name=data["qualified_name"])


def _unit_from_dict(data: dict[str, Any] | None) -> UnitFact | None:
    if data is None:
        return None
    return UnitFact(unit=data["unit"], dimension=data["dimension"])


def _operand_type_from_dict(data: dict[str, Any] | None) -> OperandTypeFact | None:
    if data is None:
        return None
    return OperandTypeFact(
        category=data["category"],
        enumeration=data["enumeration"],
        unit=_unit_from_dict(data["unit"]),
    )


def _operand_type_from_dict_required(data: dict[str, Any]) -> OperandTypeFact:
    operand_type = _operand_type_from_dict(data)
    if operand_type is None:
        raise ValueError("expected a resolved operand_type, got null")
    return operand_type


def _reference_from_dict(data: dict[str, Any]) -> FeatureReferenceFact:
    return FeatureReferenceFact(
        source_name=data["source_name"],
        target=_identity_from_dict(data["target"]),
        target_types=list(data["target_types"]),
        chain_segments=list(data["chain_segments"]),
    )


def _literal_from_dict(data: dict[str, Any]) -> LiteralFact:
    return LiteralFact(kind=data["kind"], value=data["value"], result_type=data["result_type"])


def _expression_ir_from_dict(data: dict[str, Any]) -> ExpressionIR:
    """Dispatch on `kind` and reconstruct exactly one node type, recursing on child slots."""
    node_kind = data["kind"]
    if node_kind == "literal":
        return LiteralNode(
            literal=_literal_from_dict(data["literal"]),
            operand_type=_operand_type_from_dict_required(data["operand_type"]),
        )
    if node_kind == "feature_ref":
        return FeatureReferenceNode(
            reference=_reference_from_dict(data["reference"]),
            operand_type=_operand_type_from_dict_required(data["operand_type"]),
        )
    if node_kind == "operator":
        return OperatorNode(
            operator=data["operator"],
            operands=[_expression_ir_from_dict(operand) for operand in data["operands"]],
            operand_type=_operand_type_from_dict(data["operand_type"]),
        )
    if node_kind == "unit":
        return UnitAnnotationNode(
            value=_expression_ir_from_dict(data["value"]),
            unit_text=data["unit_text"],
            operand_type=_operand_type_from_dict_required(data["operand_type"]),
        )
    if node_kind == "invocation":
        return InvocationNode(
            function_qn=list(data["function_qn"]) if data["function_qn"] is not None else None,
            arguments=[_expression_ir_from_dict(argument) for argument in data["arguments"]],
            operand_type=_operand_type_from_dict(data["operand_type"]),
        )
    if node_kind == "unsupported":
        return UnsupportedNode(
            node_kind=data["node_kind"],
            diagnostic=data["diagnostic"],
            source_text=data["source_text"],
        )
    raise ValueError(f"unrecognized ExpressionIR kind: {node_kind!r}")


def parse_expression(text: str) -> ExpressionIR:
    """Reconstruct an `ExpressionIR` node from its canonical JSON section."""
    return _expression_ir_from_dict(json.loads(text))

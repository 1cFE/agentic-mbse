"""Production predicate tree: distinct node algebra, serialize/parse, canonical JSON.

One dataclass per algebra kind — literal, feature reference, operator, unit annotation,
invocation, and an explicit unsupported node — joined by a `kind`-tagged union. Reuses Item 1's
frozen leaf facts (`FeatureReferenceFact`, `LiteralFact`, `OperandTypeFact`, `UnitFact`)
unchanged. Imports `expression_facts` only — `constraint_facts` imports this module, not the
other way, keeping the import direction one-way.

The codec fails closed on its wire tags: exactly one schema version is supported per code
checkout, the decoder rejects any foreign `schema_version` or unknown `kind`, and the
serializer revalidates both tags so post-construction mutation cannot emit an impossible
document. Malformed semantic leaf facts remain representable for the executable profile's
named BLOCK contract.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
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
    "canonical_json",
    "expression_ir_from_dict",
    "identity_fact_from_dict",
    "parse_expression",
    "serialize_expression",
]

EXPRESSION_IR_SCHEMA_VERSION = "expression-ir/v1"


@dataclass
class LiteralNode:
    """A literal leaf node: a number, string, or boolean constant."""

    literal: LiteralFact
    operand_type: OperandTypeFact | None
    kind: str = field(init=False, default="literal")
    schema_version: str = field(init=False, default=EXPRESSION_IR_SCHEMA_VERSION)


@dataclass
class FeatureReferenceNode:
    """A feature reference leaf node: a plain reference or a feature chain."""

    reference: FeatureReferenceFact
    operand_type: OperandTypeFact | None
    kind: str = field(init=False, default="feature_ref")
    schema_version: str = field(init=False, default=EXPRESSION_IR_SCHEMA_VERSION)


@dataclass
class OperatorNode:
    """An n-ary operator node: arithmetic, comparison, or Boolean connective.

    `operand_type` is `None` on comparison/connective nodes — they are propositions, not
    values.
    """

    operator: str
    operands: list[ExpressionIR]
    operand_type: OperandTypeFact | None
    kind: str = field(init=False, default="operator")
    schema_version: str = field(init=False, default=EXPRESSION_IR_SCHEMA_VERSION)


@dataclass
class UnitAnnotationNode:
    """A `[` unit-annotation node: the annotated value plus the resolved unit.

    `unit_text` is the source spelling (`"m"`); the resolved `UnitFact` lives on
    `operand_type`.
    """

    value: ExpressionIR
    unit_text: str | None
    operand_type: OperandTypeFact | None
    kind: str = field(init=False, default="unit")
    schema_version: str = field(init=False, default=EXPRESSION_IR_SCHEMA_VERSION)


@dataclass
class InvocationNode:
    """An invocation node: a resolved function reference plus its arguments."""

    function_qn: list[str] | None
    arguments: list[ExpressionIR]
    operand_type: OperandTypeFact | None
    kind: str = field(init=False, default="invocation")
    schema_version: str = field(init=False, default=EXPRESSION_IR_SCHEMA_VERSION)


@dataclass
class UnsupportedNode:
    """An explicit fallback for a structurally unrepresentable expression node.

    Carries the unrecognized metaclass, a diagnostic message, and the reconstructed source
    text where available — never silently coerced into a productive node kind.
    """

    node_kind: str
    diagnostic: str
    source_text: str | None
    kind: str = field(init=False, default="unsupported")
    schema_version: str = field(init=False, default=EXPRESSION_IR_SCHEMA_VERSION)


ExpressionIR: TypeAlias = (
    LiteralNode
    | FeatureReferenceNode
    | OperatorNode
    | UnitAnnotationNode
    | InvocationNode
    | UnsupportedNode
)

_NODE_KINDS = (
    (LiteralNode, "literal"),
    (FeatureReferenceNode, "feature_ref"),
    (OperatorNode, "operator"),
    (UnitAnnotationNode, "unit"),
    (InvocationNode, "invocation"),
    (UnsupportedNode, "unsupported"),
)


def _validate_expression_ir_tags(obj: Any) -> None:
    """Reject mutated ExpressionIR wire tags anywhere in a dataclass aggregate."""
    for node_type, expected_kind in _NODE_KINDS:
        if isinstance(obj, node_type):
            if obj.kind != expected_kind:
                raise ValueError(
                    f"invalid ExpressionIR kind on {node_type.__name__}: "
                    f"found {obj.kind!r}, expected {expected_kind!r}"
                )
            if obj.schema_version != EXPRESSION_IR_SCHEMA_VERSION:
                raise ValueError(
                    f"invalid ExpressionIR schema_version on {node_type.__name__}: "
                    f"found {obj.schema_version!r}, expected {EXPRESSION_IR_SCHEMA_VERSION!r}"
                )
            break

    if dataclasses.is_dataclass(obj):
        for data_field in dataclasses.fields(obj):
            _validate_expression_ir_tags(getattr(obj, data_field.name))
    elif isinstance(obj, dict):
        for value in obj.values():
            _validate_expression_ir_tags(value)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            _validate_expression_ir_tags(value)


def canonical_json(obj: Any) -> str:
    """Render `obj` as canonical, byte-stable JSON (D2/D5): sorted keys, compact separators,
    ASCII-only, non-finite floats rejected."""
    _validate_expression_ir_tags(obj)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        json_value = dataclasses.asdict(obj)
    else:
        json_value = obj
    return json.dumps(
        json_value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def serialize_expression(ir: ExpressionIR) -> str:
    """Render `ir` as canonical, byte-stable JSON (D2/D5)."""
    return canonical_json(ir)


def identity_fact_from_dict(data: dict[str, Any] | None) -> IdentityFact | None:
    """Decode an `IdentityFact` leaf from its dict form; an explicit `null` stays `None`."""
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


def _reference_from_dict(data: dict[str, Any]) -> FeatureReferenceFact:
    return FeatureReferenceFact(
        source_name=data["source_name"],
        target=identity_fact_from_dict(data["target"]),
        target_types=list(data["target_types"]),
        chain_segments=list(data["chain_segments"]),
    )


def _literal_from_dict(data: dict[str, Any]) -> LiteralFact:
    return LiteralFact(kind=data["kind"], value=data["value"], result_type=data["result_type"])


def expression_ir_from_dict(data: dict[str, Any]) -> ExpressionIR:
    """Reconstruct one `ExpressionIR` node from its dict form, validating the wire tags.

    Validates `schema_version` and `kind` on every node (recursing on child slots) before
    dispatching: a missing or foreign version and a missing or unknown kind each raise
    `ValueError` naming what was found — never silently rewritten to the supported version.
    Unknown extra keys are ignored. The constructed nodes carry the supported tags by
    construction (`kind`/`schema_version` are non-init fields).
    """
    if "schema_version" not in data:
        raise ValueError(
            "ExpressionIR node is missing 'schema_version' "
            f"(supported: {EXPRESSION_IR_SCHEMA_VERSION!r})"
        )
    found_version = data["schema_version"]
    if found_version != EXPRESSION_IR_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported ExpressionIR schema_version: found {found_version!r}, "
            f"supported {EXPRESSION_IR_SCHEMA_VERSION!r}"
        )
    if "kind" not in data:
        raise ValueError("ExpressionIR node is missing 'kind'")
    node_kind = data["kind"]
    if node_kind == "literal":
        return LiteralNode(
            literal=_literal_from_dict(data["literal"]),
            operand_type=_operand_type_from_dict(data.get("operand_type")),
        )
    if node_kind == "feature_ref":
        return FeatureReferenceNode(
            reference=_reference_from_dict(data["reference"]),
            operand_type=_operand_type_from_dict(data.get("operand_type")),
        )
    if node_kind == "operator":
        return OperatorNode(
            operator=data["operator"],
            operands=[expression_ir_from_dict(operand) for operand in data["operands"]],
            operand_type=_operand_type_from_dict(data["operand_type"]),
        )
    if node_kind == "unit":
        return UnitAnnotationNode(
            value=expression_ir_from_dict(data["value"]),
            unit_text=data["unit_text"],
            operand_type=_operand_type_from_dict(data.get("operand_type")),
        )
    if node_kind == "invocation":
        return InvocationNode(
            function_qn=list(data["function_qn"]) if data["function_qn"] is not None else None,
            arguments=[expression_ir_from_dict(argument) for argument in data["arguments"]],
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
    return expression_ir_from_dict(json.loads(text))

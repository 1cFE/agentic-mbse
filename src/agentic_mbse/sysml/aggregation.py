"""Shared SysML aggregation decomposition.

This module extracts neutral aggregation facts. Python rendering, pipeline
identifiers, aliases, and codegen containers stay in sysml-codegen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypeAlias

from agentic_mbse.sysml.data_models import LocalTerm, SingletonTerm, SumTerm
from agentic_mbse.sysml.expression import (
    extract_feature_chain_name,
    extract_feature_reference_name,
    is_literal_node,
    reconstruct_expression,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = [
    "AggregationDecomposition",
    "AggregationDiagnostic",
    "AggregationNode",
    "FeatureChainNode",
    "FeatureReferenceNode",
    "InvocationNode",
    "LiteralNode",
    "LocalTerm",
    "NullNode",
    "OperatorNode",
    "SingletonTerm",
    "SumNode",
    "SumTerm",
    "UnsupportedNode",
    "WrapperFact",
    "decompose_aggregation_expression",
]

SUPPORTED_OPERATORS = frozenset(
    {
        "+",
        "-",
        "*",
        "/",
        "^",
        "<",
        ">",
        "<=",
        ">=",
        "==",
        "!=",
        "and",
        "or",
        "implies",
        "not",
    }
)
KNOWN_WRAPPER_FUNCTIONS = frozenset({"Evaluation", "evaluate", "collect", "select"})

DiagnosticKind: TypeAlias = Literal[
    "unsupported_node", "unsupported_operator", "unsupported_invocation"
]
WrapperReason: TypeAlias = Literal["sum_operand", "known_wrapper"]


@dataclass
class AggregationDiagnostic:
    """Neutral diagnostic discovered during aggregation decomposition."""

    diagnostic_id: str
    kind: DiagnosticKind
    message: str
    node_kind: str


@dataclass
class WrapperFact:
    """Record that a wrapper invocation was unwrapped."""

    function_name: str
    reason: WrapperReason
    depth: int = 0


@dataclass
class SumNode:
    """Neutral sum() node pointing at an ordered SumTerm."""

    term_index: int
    operand: AggregationNode
    wrapper_context: str | None = None


@dataclass
class FeatureChainNode:
    """Neutral feature-chain expression."""

    source_path: str


@dataclass
class FeatureReferenceNode:
    """Neutral feature-reference expression."""

    attribute_name: str


@dataclass
class LiteralNode:
    """Neutral literal or null expression."""

    literal_kind: str
    render_text: str
    value: Any = None


@dataclass
class OperatorNode:
    """Neutral operator expression."""

    operator: str
    operands: list[AggregationNode]
    unsupported: bool = False
    diagnostic_id: str | None = None


@dataclass
class InvocationNode:
    """Neutral invocation expression."""

    function_name: str
    operands: list[AggregationNode]
    wrapper_disposition: str | None = None
    unsupported: bool = False
    diagnostic_id: str | None = None


@dataclass
class UnsupportedNode:
    """Neutral fallback for an unclassified expression node."""

    fallback_render: str
    node_kind: str
    diagnostic_id: str
    diagnostic_message: str


@dataclass
class NullNode:
    """Neutral empty expression node."""

    render_text: str = ""


AggregationNode: TypeAlias = (
    SumNode
    | FeatureChainNode
    | FeatureReferenceNode
    | LiteralNode
    | OperatorNode
    | InvocationNode
    | UnsupportedNode
    | NullNode
)


@dataclass
class AggregationDecomposition:
    """Neutral decomposition of one aggregation expression."""

    root: AggregationNode
    sum_terms: list[SumTerm] = field(default_factory=list)
    singleton_terms: list[SingletonTerm] = field(default_factory=list)
    local_terms: list[LocalTerm] = field(default_factory=list)
    diagnostics: list[AggregationDiagnostic] = field(default_factory=list)
    wrappers: list[WrapperFact] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)

    @property
    def has_unsupported(self) -> bool:
        return bool(self.diagnostics)


class _AggregationContext:
    def __init__(self) -> None:
        self.sum_terms: list[SumTerm] = []
        self.singleton_terms: list[SingletonTerm] = []
        self.local_terms: list[LocalTerm] = []
        self.diagnostics: list[AggregationDiagnostic] = []
        self.wrappers: list[WrapperFact] = []
        self.source_refs: list[str] = []

    def add_diagnostic(self, kind: DiagnosticKind, node: Any, message: str) -> str:
        diagnostic_id = f"AGG-{len(self.diagnostics) + 1:03d}"
        self.diagnostics.append(
            AggregationDiagnostic(
                diagnostic_id=diagnostic_id,
                kind=kind,
                message=message,
                node_kind=type(node).__name__,
            )
        )
        return diagnostic_id


def decompose_aggregation_expression(expr_node: Any) -> AggregationDecomposition:
    """Decompose a SysML aggregation expression into neutral facts."""
    ctx = _AggregationContext()
    root = _decompose_node(expr_node, ctx)
    return AggregationDecomposition(
        root=root,
        sum_terms=ctx.sum_terms,
        singleton_terms=ctx.singleton_terms,
        local_terms=ctx.local_terms,
        diagnostics=ctx.diagnostics,
        wrappers=ctx.wrappers,
        source_refs=ctx.source_refs,
    )


def _decompose_node(
    node: Any, ctx: _AggregationContext, *, collect_terms: bool = True
) -> AggregationNode:
    if node is None:
        return NullNode()

    # FeatureChainExpression MUST be before OperatorExpression because SysIDE can
    # report feature chains as operators too.
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        source_path = extract_feature_chain_name(node)
        if collect_terms:
            ctx.singleton_terms.append(SingletonTerm(source_path=source_path))
            ctx.source_refs.append(source_path)
        return FeatureChainNode(source_path=source_path)

    if SysideAdapter.is_instance(node, "OperatorExpression"):
        operator = str(getattr(node, "operator", "+"))
        operands = [
            _decompose_node(op, ctx, collect_terms=collect_terms)
            for op in list(getattr(node, "operands", []))
        ]
        diagnostic_id = None
        unsupported = operator not in SUPPORTED_OPERATORS
        if unsupported:
            diagnostic_id = ctx.add_diagnostic(
                "unsupported_operator",
                node,
                f"Unsupported operator '{operator}' in aggregation expression",
            )
        return OperatorNode(
            operator=operator,
            operands=operands,
            unsupported=unsupported,
            diagnostic_id=diagnostic_id,
        )

    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        attr_name = extract_feature_reference_name(node)
        if collect_terms:
            ctx.local_terms.append(LocalTerm(attribute_name=attr_name))
            ctx.source_refs.append(attr_name)
        return FeatureReferenceNode(attribute_name=attr_name)

    # Literal/null must precede the invocation catch-all because real SysIDE
    # nodes can expose a derived .function.name.
    if is_literal_node(node):
        return LiteralNode(
            literal_kind=type(node).__name__,
            render_text=reconstruct_expression(node),
            value=getattr(node, "value", None),
        )

    if hasattr(node, "function") and hasattr(node.function, "name"):
        func_name = str(node.function.name)
        operands = list(getattr(node, "operands", []))

        if func_name == "sum" and operands:
            operand, wrapper_context = _unwrap_sum_operand(operands[0], ctx)
            operand_node = _decompose_node(operand, ctx, collect_terms=False)
            chain_name = _sum_operand_name(operand)
            parts = chain_name.split(".", 1)
            if len(parts) == 2:
                part_name, attr_name = parts
                term = SumTerm(
                    part_usage_name=part_name,
                    attribute_name=attr_name,
                    multiplicity_attr=None,
                    multiplicity_count=None,
                )
                ctx.sum_terms.append(term)
                return SumNode(
                    term_index=len(ctx.sum_terms) - 1,
                    operand=operand_node,
                    wrapper_context=wrapper_context,
                )

            ctx.local_terms.append(LocalTerm(attribute_name=chain_name))
            return FeatureReferenceNode(attribute_name=chain_name)

        if func_name in KNOWN_WRAPPER_FUNCTIONS and operands:
            unwrapped, _depth = _unwrap_known_wrapper(node, ctx)
            if unwrapped is not node:
                return _decompose_node(unwrapped, ctx, collect_terms=collect_terms)

        operand_nodes = [_decompose_node(op, ctx, collect_terms=collect_terms) for op in operands]
        diagnostic_id = ctx.add_diagnostic(
            "unsupported_invocation",
            node,
            f"Unsupported invocation '{func_name}' in aggregation expression",
        )
        return InvocationNode(
            function_name=func_name,
            operands=operand_nodes,
            unsupported=True,
            diagnostic_id=diagnostic_id,
        )

    message = f"Unrecognized AST node type in aggregation expression: {type(node).__name__}"
    diagnostic_id = ctx.add_diagnostic("unsupported_node", node, message)
    return UnsupportedNode(
        fallback_render=str(node),
        node_kind=type(node).__name__,
        diagnostic_id=diagnostic_id,
        diagnostic_message=message,
    )


def _unwrap_sum_operand(
    node: Any, ctx: _AggregationContext, depth: int = 0
) -> tuple[Any, str | None]:
    if depth >= 3:
        return node, None
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        return node, None
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        return node, None
    if hasattr(node, "function") and hasattr(node.function, "name"):
        operands = list(getattr(node, "operands", []))
        if operands:
            ctx.wrappers.append(WrapperFact(str(node.function.name), "sum_operand", depth))
            unwrapped, inner_context = _unwrap_sum_operand(operands[0], ctx, depth + 1)
            return unwrapped, inner_context or str(node.function.name)
    return node, None


def _unwrap_known_wrapper(node: Any, ctx: _AggregationContext, depth: int = 0) -> tuple[Any, int]:
    if depth >= 3:
        return node, depth
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        return node, depth
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        return node, depth
    if hasattr(node, "function") and hasattr(node.function, "name"):
        operands = list(getattr(node, "operands", []))
        if operands:
            ctx.wrappers.append(WrapperFact(str(node.function.name), "known_wrapper", depth))
            return _unwrap_known_wrapper(operands[0], ctx, depth + 1)
    return node, depth


def _sum_operand_name(operand: Any) -> str:
    if SysideAdapter.is_instance(operand, "FeatureChainExpression"):
        return extract_feature_chain_name(operand)
    return extract_feature_reference_name(operand)

"""Shared SysML aggregation decomposition.

This module extracts neutral aggregation facts. Python rendering, pipeline
identifiers, aliases, and codegen containers stay in sysml-codegen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypeAlias

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.data_models import (
    LocalTerm,
    ResolvedTargetFact,
    SingletonTerm,
    SumTerm,
)
from agentic_mbse.sysml.expression import (
    is_literal_node,
    reconstruct_expression,
)
from agentic_mbse.sysml.reference_use import (
    ReferenceUse,
    authored_reference_text,
    build_aggregation_term,
    inspect_reference_uses,
    materialize_operands,
    require_exact_reference_use,
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
        "**",
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
    """Neutral feature-chain expression.

    ``resolved_target`` is the exact SysIDE-resolved leaf of the chain,
    ``chain_root`` the resolved root referent, both captured before any name is
    rendered (SOURCE-IDENTITY Item 4). ``resolved_member_names`` is the resolved
    member path from root to leaf.

    There is no index marker.  An authored ``#(i)`` never reaches this node: the
    closed reference boundary refuses it by name first, so a chain node here is
    exact by construction rather than exact-unless-a-flag-says-otherwise.
    """

    source_path: str
    resolved_target: ResolvedTargetFact | None = None
    chain_root: ResolvedTargetFact | None = None
    resolved_member_names: tuple[str, ...] = ()


@dataclass
class FeatureReferenceNode:
    """Neutral feature-reference expression."""

    attribute_name: str
    resolved_target: ResolvedTargetFact | None = None


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
        # The guard runs before any term or node object exists, so this site cannot
        # manufacture an index-free term from an indexed reference.
        exact = require_exact_reference_use(
            _one_reference_use(node), operation="decompose_aggregation_expression"
        )
        if collect_terms:
            ctx.singleton_terms.append(build_aggregation_term(exact))
            ctx.source_refs.append(exact.authored_text)
        return FeatureChainNode(
            source_path=exact.authored_text,
            resolved_target=exact.path.leaf,
            chain_root=exact.path.root,
            resolved_member_names=exact.path.resolved_member_names,
        )

    if SysideAdapter.is_instance(node, "OperatorExpression"):
        operator = str(getattr(node, "operator", "+"))
        operands = [
            _decompose_node(op, ctx, collect_terms=collect_terms)
            for op in materialize_operands(node)
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
        exact = require_exact_reference_use(
            _one_reference_use(node), operation="decompose_aggregation_expression"
        )
        attr_name = exact.authored_text
        resolved_target: ResolvedTargetFact | None = exact.path.leaf
        if collect_terms:
            ctx.local_terms.append(
                LocalTerm(attribute_name=attr_name, resolved_target=resolved_target)
            )
            ctx.source_refs.append(attr_name)
        return FeatureReferenceNode(attribute_name=attr_name, resolved_target=resolved_target)

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
        operands = list(materialize_operands(node))

        if func_name == "sum" and operands:
            operand, wrapper_context = _unwrap_sum_operand(operands[0], ctx)
            operand_node = _decompose_node(operand, ctx, collect_terms=False)
            resolved_target, chain_root, member_names = _operand_chain_evidence(operand)
            chain_name = _sum_operand_name(operand)
            parts = chain_name.split(".", 1)
            if len(parts) == 2:
                part_name, attr_name = parts
                term = SumTerm(
                    part_usage_name=part_name,
                    attribute_name=attr_name,
                    multiplicity_attr=None,
                    multiplicity_count=None,
                    resolved_target=resolved_target,
                    chain_root=chain_root,
                    resolved_member_names=member_names,
                )
                ctx.sum_terms.append(term)
                return SumNode(
                    term_index=len(ctx.sum_terms) - 1,
                    operand=operand_node,
                    wrapper_context=wrapper_context,
                )

            ctx.local_terms.append(
                LocalTerm(
                    attribute_name=chain_name,
                    resolved_target=resolved_target,
                    chain_root=chain_root,
                    resolved_member_names=member_names,
                )
            )
            return FeatureReferenceNode(
                attribute_name=chain_name, resolved_target=resolved_target
            )

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
        operands = list(materialize_operands(node))
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
        operands = list(materialize_operands(node))
        if operands:
            ctx.wrappers.append(WrapperFact(str(node.function.name), "known_wrapper", depth))
            return _unwrap_known_wrapper(operands[0], ctx, depth + 1)
    return node, depth


def _sum_operand_name(operand: Any) -> str:
    return authored_reference_text(operand)


def _one_reference_use(node: Any) -> ReferenceUse:
    """The single reference use of one reference or chain node.

    The inspector is total over an expression tree; at a reference node it returns
    exactly one use, and anything else means the node was not the reference kind this
    caller dispatched on.
    """
    uses = inspect_reference_uses(node)
    if len(uses) != 1:
        raise SemanticEvidenceError(
            SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED,
            operation="decompose_aggregation_expression",
            detail=f"reference node yielded {len(uses)} reference uses, expected one",
            location=SysideAdapter.get_source_location(node),
        )
    return uses[0]


def _operand_chain_evidence(
    operand: Any,
) -> tuple[ResolvedTargetFact | None, ResolvedTargetFact | None, tuple[str, ...]]:
    """The exact (leaf, root, member names) of a sum() operand chain or reference."""
    if not (
        SysideAdapter.is_instance(operand, "FeatureChainExpression")
        or SysideAdapter.is_instance(operand, "FeatureReferenceExpression")
    ):
        return None, None, ()
    exact = require_exact_reference_use(
        _one_reference_use(operand), operation="decompose_aggregation_expression"
    )
    root = exact.path.root if exact.form == "chain" else None
    return exact.path.leaf, root, exact.path.resolved_member_names

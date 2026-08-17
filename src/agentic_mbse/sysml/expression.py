"""Expression traversal utilities for SysML AST analysis.

This module provides functions for traversing and analyzing SysML expression
ASTs, including visitor-pattern traversal and reference extraction.
"""

from collections.abc import Callable
from typing import Any, cast

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.data_models import (
    ResolvedSemanticReferenceFact,
    ResolvedTargetFact,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import ExpressionRef


def _semantic_reference(element: Any) -> str | None:
    value = getattr(element, "qualified_name", None) or getattr(element, "name", None)
    return str(value) if value else None


def _evidence_error(
    code: SemanticEvidenceCode,
    operation: str,
    detail: str,
    element: Any,
    *,
    cause: BaseException | None = None,
) -> SemanticEvidenceError:
    return SemanticEvidenceError(
        code,
        operation=operation,
        detail=detail,
        location=SysideAdapter.get_source_location(element),
        reference=_semantic_reference(element),
        cause=cause,
    )


def materialize_operands(expression: Any) -> tuple[Any, ...]:
    """Read one expression's complete operand sequence exactly once."""
    try:
        return tuple(expression.operands)
    except Exception as cause:
        error = _evidence_error(
            SemanticEvidenceCode.OPERAND_ITERATION_FAILED,
            "iterate_operands",
            "SysIDE could not materialize the expression operands",
            expression,
            cause=cause,
        )
        raise error from cause


def _traversal_operands(expression: Any) -> tuple[Any, ...]:
    """Materialize operands only for metatypes that own an operand sequence."""
    has_operands = any(
        SysideAdapter.is_instance(expression, type_name)
        for type_name in (
            "FeatureChainExpression",
            "OperatorExpression",
            "InvocationExpression",
        )
    )
    return materialize_operands(expression) if has_operands else ()


def traverse_expression(
    expr: Any,
    visitor: Callable[[Any], Any],
    max_depth: int = 100,
    _current_depth: int = 0,
) -> list[Any]:
    """Traverse expression AST using visitor pattern.

    Recursively visits all nodes in an expression tree, applying the visitor
    function to each node and collecting non-None results.

    Args:
        expr: Expression AST node to traverse (or None)
        visitor: Function called for each node, returns value to collect or None
        max_depth: Maximum recursion depth (default 100, prevents infinite loops)
        _current_depth: Internal depth counter (do not set externally)

    Returns:
        List of all non-None visitor results

    Example:
        >>> def get_names(node):
        ...     return node.name if hasattr(node, 'name') else None
        >>> refs = traverse_expression(expr, get_names)
        >>> print(refs)  # ['volume', 'area']
    """
    if expr is None:
        return []

    if _current_depth >= max_depth:
        return []

    results: list[Any] = []

    # Visit current node
    result = visitor(expr)
    if result is not None:
        results.append(result)

    for operand in _traversal_operands(expr):
        child_results = traverse_expression(operand, visitor, max_depth, _current_depth + 1)
        results.extend(child_results)

    return results


def _is_operator_expression(expr: Any) -> bool:
    """Check if expression is an OperatorExpression type."""
    return SysideAdapter.is_instance(expr, "OperatorExpression")


def _is_standard_library_element(element: Any) -> bool:
    """Classify one exact target through SysIDE's document tier."""
    tier = SysideAdapter.document_tier(element)
    return tier is SysideAdapter.document_tier_type().StandardLibrary


def extract_feature_refs(
    expr: Any,
    ignore_std_lib: bool = True,
) -> list[ExpressionRef]:
    """Extract all attribute references from an expression.

    Traverses the expression tree and returns ExpressionRef objects for
    all FeatureReferenceExpression and FeatureChainExpression nodes found.

    Args:
        expr: Expression AST node to analyze (or None)
        ignore_std_lib: If True, filter out references to standard library
                       elements (SI::, ISQ::, ScalarValues::, UnitsAndScales::).
                       Default is True to exclude unit annotations from ref counts.

    Returns:
        List of ExpressionRef objects for all referenced attributes

    Example:
        >>> refs = extract_feature_refs(expr)  # Filters std lib by default
        >>> refs = extract_feature_refs(expr, ignore_std_lib=False)  # Include all
    """
    if expr is None:
        return []

    def ref_visitor(node: Any) -> ExpressionRef | None:
        """Visitor that creates ExpressionRef for reference expressions."""
        is_chain = SysideAdapter.is_instance(node, "FeatureChainExpression")
        is_reference = SysideAdapter.is_instance(node, "FeatureReferenceExpression")
        if is_chain or is_reference:
            target = (
                getattr(node, "target_feature", None)
                if is_chain
                else getattr(node, "referent", None)
            )
            if target is None:
                raise _evidence_error(
                    SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
                    "extract_feature_refs",
                    "resolved reference has no exact target",
                    node,
                )
            if ignore_std_lib and _is_standard_library_element(target):
                return None
            name = str(getattr(target, "name", None) or "")
            qualified_name = str(getattr(target, "qualified_name", None) or "")
            document = getattr(target, "document", None)
            document_url = getattr(document, "url", None) if document else None
            return ExpressionRef(
                name=name,
                qualified_name=qualified_name,
                document_path=str(document_url) if document_url else None,
                element=target,
            )

        return None

    return traverse_expression(expr, ref_visitor)


def extract_operators(expr: Any) -> list[str]:
    """Extract all operators from an expression.

    Traverses the expression tree and returns a list of operator strings
    found in OperatorExpression nodes.

    Args:
        expr: Expression AST node to analyze (or None)

    Returns:
        List of operator strings (e.g., ["+", "*", "-"])

    Example:
        >>> ops = extract_operators(expr)
        >>> if "**" in ops:
        ...     print("Exponentiation found!")
    """
    if expr is None:
        return []

    def op_visitor(node: Any) -> str | None:
        """Visitor that extracts operator from OperatorExpression."""
        if _is_operator_expression(node) and hasattr(node, "operator"):
            return str(node.operator)

        return None

    return traverse_expression(expr, op_visitor)


def is_literal_expression(expr: Any) -> bool:
    """Check if expression contains only literals (no design attribute references).

    Returns True if the expression has no design attribute references, meaning
    it can be evaluated statically without any external values.

    Note: Standard library references (SI::, ISQ::, ScalarValues::, UnitsAndScales::)
    are filtered out by default. This means unit annotations like `3.0 [m]` return
    True even though they contain a reference to SI::metre - this is correct
    behavior per ADR-002. For the semantic equivalent with clearer naming,
    see `is_true_static_expression()`.

    NOT the same as `is_literal_node()`: that is a structural check ("is this AST
    node itself a Literal*/NullExpression node"), while this is a semantic check
    ("does this expression reference any design attribute"). A computed expression
    like `1 + 2` passes this check but fails `is_literal_node()`.

    Args:
        expr: Expression AST node to check (or None)

    Returns:
        True if expression has no design attribute refs, False otherwise

    Example:
        >>> is_literal_expression(literal_42)      # True
        >>> is_literal_expression(unit_3_meters)   # True (SI::metre filtered)
        >>> is_literal_expression(attr_ref)        # False
        >>> is_literal_expression(add_expr)        # Depends on operands
    """
    if expr is None:
        return True  # No expression = effectively literal

    refs = extract_feature_refs(expr)
    return len(refs) == 0


def is_literal_type(expr: Any) -> bool:
    """Check if expression is a literal type (LiteralRational, LiteralInteger, etc.).

    This utility supports the static expression evaluator by providing
    consistent type checking based on AST node type names.

    Args:
        expr: AST expression node to check

    Returns:
        True if the expression is a Literal* type, False otherwise

    Example:
        >>> is_literal_type(MockLiteralRational(3.14))  # True
        >>> is_literal_type(MockOperatorExpression("+", []))  # False
    """
    return any(
        SysideAdapter.is_instance(expr, type_name)
        for type_name in (
            "LiteralInteger",
            "LiteralRational",
            "LiteralString",
            "LiteralBoolean",
            "LiteralInfinity",
        )
    )


def is_reference_type(expr: Any) -> bool:
    """Check if expression is a feature reference type.

    Detects both FeatureReferenceExpression (simple refs like `radius`)
    and FeatureChainExpression (dotted refs like `calc.output`).

    Args:
        expr: AST expression node to check

    Returns:
        True if the expression is a reference type, False otherwise

    Example:
        >>> is_reference_type(MockFeatureReferenceExpression(name="radius"))  # True
        >>> is_reference_type(MockLiteralRational(3.0))  # False
    """
    return SysideAdapter.is_instance(
        expr, "FeatureChainExpression"
    ) or SysideAdapter.is_instance(expr, "FeatureReferenceExpression")


# Supported operators for static expressions (per ADR-002)
STATIC_OPERATORS = {"+", "-", "*", "/", "["}


def get_reference_name(expr: Any) -> str | None:
    """Extract the name from a feature reference expression.

    Works with both FeatureReferenceExpression and FeatureChainExpression.
    Returns the terminal name only (``"attr"``); for the full dotted path of a
    chain (``"instance.attr"``), see extract_feature_chain_name() or
    extract_feature_chain_segments().

    Args:
        expr: AST node (FeatureReferenceExpression or FeatureChainExpression)

    Returns:
        Reference name if extractable, None otherwise

    Example:
        >>> get_reference_name(MockFeatureReferenceExpression(name="radius"))
        'radius'
        >>> get_reference_name(MockFeatureChainExpression(instance_name="calc", attr_name="output"))
        'output'
        >>> get_reference_name(MockLiteralRational(3.0))
        None
    """
    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        target = getattr(expr, "target_feature", None)
    elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        target = getattr(expr, "referent", None)
    else:
        return None
    if target is None:
        raise _evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "get_reference_name",
            "resolved reference has no exact target",
            expr,
        )
    name = getattr(target, "name", None)
    return cast(str, name) if name else None


# Operator mapping for expression reconstruction (SysML text output)
OPERATOR_MAP = {
    "and": " and ",
    "or": " or ",
    "==": " == ",
    "!=": " != ",
    ">": " > ",
    "<": " < ",
    ">=": " >= ",
    "<=": " <= ",
    "+": " + ",
    "-": " - ",
    "*": " * ",
    "/": " / ",
    "**": " ** ",
    "^": " ^ ",
    "implies": " implies ",
    "not": "not ",
}

# Binary-operator precedence ranks from KerML Table 6 (§8.2.5.8.1).
# Smaller rank = binds tighter.
RANK = {
    "**": 3,
    "^": 3,
    "*": 4,
    "/": 4,
    "+": 5,
    "-": 5,
    "<": 7,
    ">": 7,
    "<=": 7,
    ">=": 7,
    "==": 9,
    "!=": 9,
    "and": 10,
    "or": 12,
    "implies": 13,
}
UNARY_RANK = 2
RIGHT_ASSOC = frozenset({"**", "^"})


def reconstruct_expression(expr_node: Any) -> str:
    """Reconstruct expression text from SysML AST nodes."""
    if isinstance(expr_node, str):
        return expr_node

    if expr_node is None:
        return ""

    # FeatureChainExpression MUST be before OperatorExpression because FCE is a
    # subtype of OE in SysIDE's type system.
    if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return extract_feature_chain_name(expr_node)

    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return reconstruct_operator_expression(expr_node)

    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return extract_feature_reference_name(expr_node)

    # Literal/null branches MUST dispatch before the invocation catch-all.
    if SysideAdapter.is_instance(expr_node, "LiteralInteger") or SysideAdapter.is_instance(
        expr_node, "LiteralRational"
    ):
        if hasattr(expr_node, "value"):
            return str(expr_node.value)

    if SysideAdapter.is_instance(expr_node, "LiteralBoolean"):
        if hasattr(expr_node, "value"):
            return "true" if expr_node.value else "false"

    if SysideAdapter.is_instance(expr_node, "LiteralString"):
        if hasattr(expr_node, "value"):
            return f'"{expr_node.value}"'

    if SysideAdapter.is_instance(expr_node, "LiteralInfinity"):
        return "*"

    if SysideAdapter.is_instance(expr_node, "NullExpression"):
        return "null"

    if hasattr(expr_node, "function") and hasattr(expr_node.function, "name"):
        func_name = expr_node.function.name
        operands = materialize_operands(expr_node)
        args = ", ".join(reconstruct_expression(op) for op in operands)
        return f"{func_name}({args})"

    return str(expr_node)


def binary_op_of(child: Any) -> str | None:
    """Return a child's operator iff it is a 2-operand binary OperatorExpression."""
    if not SysideAdapter.is_instance(child, "OperatorExpression"):
        return None
    if len(materialize_operands(child)) != 2:
        return None
    operator = getattr(child, "operator", None)
    if operator is None:
        return None
    op_sym = str(operator)
    return op_sym if op_sym in RANK else None


def needs_parens(parent_rank: int, parent_right_assoc: bool, child: Any, side: str) -> bool:
    """True iff `child` must be wrapped when it sits on `side` of a parent."""
    cop = binary_op_of(child)
    if cop is None:
        return False
    cr = RANK[cop]
    if cr > parent_rank:
        return True
    if cr < parent_rank:
        return False
    unfavored = "left" if parent_right_assoc else "right"
    return side == unfavored


def reconstruct_operator_expression(expr_node: Any) -> str:
    """Reconstruct an operator expression with precedence-aware parentheses."""
    operator = ""
    if hasattr(expr_node, "operator") and expr_node.operator:
        operator = str(expr_node.operator)

    operands = materialize_operands(expr_node)

    if len(operands) == 2:
        parent_rank = RANK.get(operator)
        right_assoc = operator in RIGHT_ASSOC
        left = reconstruct_expression(operands[0])
        right = reconstruct_expression(operands[1])
        if parent_rank is not None:
            if needs_parens(parent_rank, right_assoc, operands[0], "left"):
                left = f"({left})"
            if needs_parens(parent_rank, right_assoc, operands[1], "right"):
                right = f"({right})"
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        return f"{left}{op_str}{right}"

    if len(operands) == 1:
        operand = reconstruct_expression(operands[0])
        if needs_parens(UNARY_RANK, False, operands[0], "operand"):
            operand = f"({operand})"
        if operator == "-":
            return f"-{operand}"
        if operator == "not":
            return f"not {operand}"
        return f"{operator}({operand})"

    if len(operands) > 2:
        parent_rank = RANK.get(operator)
        right_assoc = operator in RIGHT_ASSOC
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        parts = []
        for i, op in enumerate(operands):
            text = reconstruct_expression(op)
            side = "left" if i == 0 else "right"
            if (
                parent_rank is not None
                and binary_op_of(op) != operator
                and needs_parens(parent_rank, right_assoc, op, side)
            ):
                text = f"({text})"
            parts.append(text)
        return op_str.join(parts)

    return operator


def extract_feature_reference_name(expr_node: Any) -> str:
    """Extract a name from a FeatureReferenceExpression."""
    referent = getattr(expr_node, "referent", None)
    if referent is None:
        raise _evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "extract_feature_reference_name",
            "resolved feature reference has no exact referent",
            expr_node,
        )
    name = getattr(referent, "name", None)
    return cast(str, name) if name else str(referent)


def extract_feature_chain_name(expr_node: Any) -> str:
    """Extract a dotted name from a FeatureChainExpression.

    For terminal-only reference extraction, see get_reference_name(). This helper
    reconstructs the chain text used by codegen compatibility paths.
    """
    path_parts: list[str] = []

    operands = materialize_operands(expr_node)
    if operands:
        operand_expr = operands[0]
        operand_name = reconstruct_expression(operand_expr)
        if operand_name:
            path_parts.append(operand_name)

    target = getattr(expr_node, "target_feature", None)
    if target is None:
        raise _evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "extract_feature_chain_name",
            "resolved feature chain has no exact target",
            expr_node,
        )
    if getattr(target, "name", None):
        path_parts.append(cast(str, target.name))

    if path_parts:
        return ".".join(path_parts)

    return str(expr_node)


def extract_feature_chain_segments(expr_node: Any) -> list[str]:
    """Return the full dotted-path segments of a FeatureChainExpression."""
    if not SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return []

    segments: list[str] = []

    operands = list(materialize_operands(expr_node))
    if operands:
        root = operands[0]
        if SysideAdapter.is_instance(root, "FeatureChainExpression"):
            segments.extend(extract_feature_chain_segments(root))
        else:
            name = reconstruct_expression(root)
            if name:
                segments.append(name)

    target = getattr(expr_node, "target_feature", None)
    if target is not None:
        chaining = list(getattr(target, "chaining_features", []) or [])
        if chaining:
            segments.extend(cast(str, c.name) for c in chaining if getattr(c, "name", None))
        elif getattr(target, "name", None):
            segments.append(cast(str, target.name))

    return segments


def resolved_target_fact(elem: Any) -> ResolvedTargetFact | None:
    """Build the immutable resolved-target fact for one live SysIDE element.

    Returns ``None`` when there is no element or the element has no qualified
    name (an anonymous chained feature — callers walk its ``chaining_features``
    instead). ``owner_is_definition`` uses the adapter's mapped definition
    metatypes.
    """
    if elem is None:
        return None
    qualified_name = getattr(elem, "qualified_name", None)
    if qualified_name is None:
        return None
    owner = getattr(elem, "owning_type", None)
    owner_qn = getattr(owner, "qualified_name", None) if owner is not None else None
    redefined: list[str] = []
    redefined_ids = []
    for redefinition in getattr(elem, "owned_redefinitions", None) or []:
        redefined_feature = getattr(redefinition, "redefined_feature", None)
        redefined_qn = getattr(redefined_feature, "qualified_name", None)
        if redefined_qn is not None:
            redefined.append(str(redefined_qn))
        if redefined_feature is not None:
            redefined_ids.append(SysideAdapter.element_id(redefined_feature))
    return ResolvedTargetFact(
        element_id=SysideAdapter.element_id(elem),
        owner_element_id=(
            SysideAdapter.element_id(owner) if owner is not None else None
        ),
        redefined_element_ids=tuple(redefined_ids),
        qualified_name=str(qualified_name),
        element_kind=type(elem).__name__,
        element_name=str(getattr(elem, "name", None) or ""),
        owner_qualified_name=str(owner_qn) if owner_qn is not None else "",
        owner_is_definition=(
            any(
                SysideAdapter.is_instance(owner, type_name)
                for type_name in (
                    "PartDefinition",
                    "CalculationDefinition",
                    "ConstraintDefinition",
                    "RequirementDefinition",
                )
            )
            if owner is not None
            else False
        ),
        redefined_qualified_names=tuple(redefined),
    )


def feature_chain_facts(
    expr_node: Any,
) -> ResolvedSemanticReferenceFact:
    """Resolved-target evidence for a FeatureChainExpression of any length.

    Returns one immutable fact containing the root, every exact resolved
    segment, the leaf, diagnostic member names, and the indexed-form marker:

    - ``root_fact`` — the chain root's resolved referent (the occurrence anchor).
    - ``leaf_fact`` — the exact resolved target of the whole chain: the last
      chaining feature when the target is a chained feature, else the target
      itself. This is the referent identity work must preserve (I1).
    - ``resolved_segment_qns`` — qualified names of every resolved step, root
      included, in chain order.
    - ``resolved_member_names`` — the RESOLVED element names of the steps after
      the root, in chain order. This is the structural member path from the
      root occurrence to the leaf; identity work uses it, never the authored
      spelling.
    - ``has_index_segment`` — True when an ``#(i)`` IndexExpression appears as a
      chain operand. The index segment is evidence, never flattened away; the
      adapter's closed type map has no ``IndexExpression`` entry, so the check is
      by metatype name.
    """
    root_fact: ResolvedTargetFact | None = None
    segments: list[ResolvedTargetFact] = []
    member_names: list[str] = []
    has_index = False

    operands = materialize_operands(expr_node)
    if operands:
        first = operands[0]
        if type(first).__name__ == "IndexExpression":
            has_index = True
            inner = list(materialize_operands(first))
            if inner and SysideAdapter.is_instance(inner[0], "FeatureReferenceExpression"):
                root_target = getattr(inner[0], "referent", None)
                if root_target is None:
                    raise _evidence_error(
                        SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
                        "feature_chain_facts",
                        "resolved chain root has no exact referent",
                        inner[0],
                    )
                root_fact = resolved_target_fact(root_target)
        elif SysideAdapter.is_instance(first, "FeatureChainExpression"):
            # The inner call's member names already cover every step after the
            # inner root, its leaf included.
            inner_fact = feature_chain_facts(first)
            root_fact = inner_fact.root
            segments.extend(inner_fact.segments)
            member_names.extend(inner_fact.resolved_member_names)
            has_index = has_index or inner_fact.has_index_segment
        elif SysideAdapter.is_instance(first, "FeatureReferenceExpression"):
            root_target = getattr(first, "referent", None)
            if root_target is None:
                raise _evidence_error(
                    SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
                    "feature_chain_facts",
                    "resolved chain root has no exact referent",
                    first,
                )
            root_fact = resolved_target_fact(root_target)

    if root_fact is not None and not segments:
        segments.append(root_fact)

    leaf_fact: ResolvedTargetFact | None = None
    target = getattr(expr_node, "target_feature", None)
    if target is None:
        raise _evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "feature_chain_facts",
            "resolved feature chain has no exact target",
            expr_node,
        )
    chaining = list(getattr(target, "chaining_features", []) or [])
    require_total_leaf = SysideAdapter.is_live_element(expr_node) or bool(
        getattr(expr_node, "semantic_reference_resolved", False)
    )
    if chaining:
        for chained in chaining:
            chained_fact = resolved_target_fact(chained)
            if chained_fact is None:
                if require_total_leaf:
                    raise _evidence_error(
                        SemanticEvidenceCode.RESOLVED_LEAF_MISSING,
                        "feature_chain_facts",
                        "resolved feature chain has an incomplete exact segment",
                        expr_node,
                    )
                continue
            segments.append(chained_fact)
            chained_name = getattr(chained, "name", None)
            if chained_name:
                member_names.append(str(chained_name))
        leaf_fact = resolved_target_fact(chaining[-1])
    else:
        leaf_fact = resolved_target_fact(target)
        if leaf_fact is None and require_total_leaf:
            raise _evidence_error(
                SemanticEvidenceCode.RESOLVED_LEAF_MISSING,
                "feature_chain_facts",
                "resolved feature chain has no exact leaf",
                expr_node,
            )
        if leaf_fact is not None:
            segments.append(leaf_fact)
        if leaf_fact is not None and leaf_fact.element_name:
            member_names.append(leaf_fact.element_name)

    return ResolvedSemanticReferenceFact(
        root=root_fact,
        segments=tuple(segments),
        leaf=leaf_fact,
        resolved_member_names=tuple(member_names),
        has_index_segment=has_index,
    )


def is_literal_node(expr: Any) -> bool:
    """Check whether a SysML AST node is a literal or null expression node.

    Structural check on the node type itself (the six Literal*/NullExpression
    types). NOT the same as `is_literal_expression()`, which is a semantic
    check for "no design attribute references" — a computed expression like
    `1 + 2` passes that check but fails this one.
    """
    return (
        SysideAdapter.is_instance(expr, "LiteralInteger")
        or SysideAdapter.is_instance(expr, "LiteralRational")
        or SysideAdapter.is_instance(expr, "LiteralBoolean")
        or SysideAdapter.is_instance(expr, "LiteralString")
        or SysideAdapter.is_instance(expr, "LiteralInfinity")
        or SysideAdapter.is_instance(expr, "NullExpression")
    )


def extract_literal_value(expr: Any) -> float | int | str | bool | None:
    """Extract the Python value from a literal AST node."""
    if hasattr(expr, "value"):
        return cast(float | int | str | bool | None, expr.value)
    return None


def evaluate_true_static_expression(expr: Any) -> float:
    """Evaluate a true static expression to a numeric value.

    True static expressions contain ONLY:
    - Literal values (LiteralRational, LiteralInteger)
    - OperatorExpression with supported operators (+, -, *, /, [)
    - Unit annotations (the [ operator) - value extracted, unit discarded

    IMPORTANT: Part 2.6 guarantees no feature references in valid models.
    If a reference is found, it indicates a model error that bypassed validation.
    This function raises immediately - no silent None propagation.

    Args:
        expr: SysML AST expression node

    Returns:
        Evaluated numeric value as float

    Raises:
        ValueError: If expression contains feature references, unsupported operators,
                   or division by zero
        TypeError: If expression is None or unexpected type

    Examples:
        >>> evaluate_true_static_expression(MockLiteralRational(3.14159))
        3.14159
        >>> evaluate_true_static_expression(MockOperatorExpression("*", [
        ...     MockLiteralRational(3.0), MockLiteralRational(2.0)]))
        6.0
    """
    if expr is None:
        raise TypeError("Cannot evaluate None expression")

    # Case 1: Literal values
    if is_literal_type(expr):
        if hasattr(expr, "value"):
            return float(expr.value)
        raise ValueError(f"Literal without value: {type(expr).__name__}")

    # Case 2: Feature reference - ERROR (model violation)
    if is_reference_type(expr):
        ref_name = get_reference_name(expr) or "<unknown>"
        raise ValueError(
            f"Feature reference '{ref_name}' found in static expression. "
            f"This violates ADR-002 Rule 3. Run 'agentic-mbse validate' "
            f"to identify and fix the violation."
        )

    # Case 3: Operator expression
    if _is_operator_expression(expr):
        # Get operator - may be Operator enum (syside) or string (mocks)
        operator_raw = getattr(expr, "operator", None)
        operator = str(operator_raw) if operator_raw is not None else None
        operands = materialize_operands(expr)

        if operator not in STATIC_OPERATORS:
            raise ValueError(
                f"Unsupported operator '{operator}' in static expression. "
                f"Supported: {STATIC_OPERATORS}. "
                f"Complex operations require a calc def in library/."
            )

        # Unit annotation: [
        if operator == "[":
            # First operand is the value, second is the unit (ignore)
            if operands:
                return evaluate_true_static_expression(operands[0])
            raise ValueError("Unit annotation without operands")

        # Unary operators
        if len(operands) == 1:
            val = evaluate_true_static_expression(operands[0])
            if operator == "-":
                return -val
            if operator == "+":
                return val
            raise ValueError(f"Unknown unary operator: {operator}")

        # Binary operators
        if len(operands) >= 2:
            left = evaluate_true_static_expression(operands[0])
            right = evaluate_true_static_expression(operands[1])

            if operator == "+":
                return left + right
            if operator == "-":
                return left - right
            if operator == "*":
                return left * right
            if operator == "/":
                if right == 0:
                    raise ValueError(
                        "Division by zero in static expression. "
                        "Check your model for divide-by-zero conditions."
                    )
                return left / right

        raise ValueError(f"Operator '{operator}' with unexpected operand count: {len(operands)}")

    raise TypeError(f"Cannot evaluate expression of type: {type(expr).__name__}")


def is_true_static_expression(expr: Any) -> bool:
    """Check if expression is "true static" per ADR-002.

    A true static expression contains ONLY:
    - Literal values (numbers, strings, booleans)
    - Standard library references (SI::, ISQ::, ScalarValues::, UnitsAndScales::)
    - Operators combining the above

    It does NOT contain any design attribute references, meaning the expression
    can be fully evaluated without any runtime values from the model.

    This is semantically equivalent to is_literal_expression() but named to
    match ADR-002 terminology. Unit annotations like `3.0 [m]` are considered
    true static because SI::metre is a standard library constant.

    Args:
        expr: Expression AST node to check (or None)

    Returns:
        True if expression is true static, False if it contains design refs

    Example:
        >>> is_true_static_expression(literal_42)           # True
        >>> is_true_static_expression(unit_annotated_3m)    # True (SI:: filtered)
        >>> is_true_static_expression(derived_radius_x_2)   # False (has design ref)
    """
    if expr is None:
        return True  # No expression = effectively static

    # extract_feature_refs filters std lib by default, so any remaining
    # refs are design attribute references
    refs = extract_feature_refs(expr)
    return len(refs) == 0

"""Expression traversal utilities for SysML AST analysis.

This module provides functions for traversing and analyzing SysML expression
ASTs, including visitor-pattern traversal and reference extraction.
"""

from collections.abc import Callable
from typing import Any, cast

from agentic_mbse.errors import SemanticEvidenceCode
from agentic_mbse.sysml.reference_use import (
    MAX_EXPRESSION_DEPTH,
    ReferenceUse,
    authored_reference_text,
    evidence_error,
    inspect_reference_uses,
    is_standard_library_use,
    materialize_operands,
    operand_bearing_operands,
    resolved_chain_target,
    resolved_referent,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter


def traverse_expression(
    expr: Any,
    visitor: Callable[[Any], Any],
    _current_depth: int = 0,
) -> list[Any]:
    """Traverse expression AST using visitor pattern.

    Recursively visits all nodes in an expression tree, applying the visitor
    function to each node and collecting non-None results.

    Args:
        expr: Expression AST node to traverse (or None)
        visitor: Function called for each node, returns value to collect or None
        _current_depth: Internal depth counter (do not set externally)

    The depth budget is ``MAX_EXPRESSION_DEPTH``, shared with every other recursive
    production expression entry and not selectable by a caller.

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

    if _current_depth >= MAX_EXPRESSION_DEPTH:
        raise evidence_error(
            SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED,
            "traverse_expression",
            "maximum expression traversal depth exhausted before all operands were visited",
            expr,
        )

    results: list[Any] = []

    # Visit current node
    result = visitor(expr)
    if result is not None:
        results.append(result)

    for operand in operand_bearing_operands(expr):
        child_results = traverse_expression(operand, visitor, _current_depth + 1)
        results.extend(child_results)

    return results


def _is_operator_expression(expr: Any) -> bool:
    """Check if expression is an OperatorExpression type."""
    return SysideAdapter.is_instance(expr, "OperatorExpression")


def design_reference_uses(expr: Any) -> tuple[ReferenceUse, ...]:
    """The reference uses in one expression that are not standard-library references.

    The filter is the policy this module owns: a unit annotation resolves into the SysIDE
    standard library and is not a design dependency, while everything else is.  The
    classification comes from the document tier the exact route captured (D6); a URL,
    path, or package name has no say.  An indexed use is never filtered out — it has no
    resolved target to classify, and dropping it would be the substitution this item
    removes.
    """
    if expr is None:
        return ()
    return tuple(use for use in inspect_reference_uses(expr) if not is_standard_library_use(use))


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

    return not design_reference_uses(expr)


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
    Returns the terminal name only (``"attr"``); for the full authored path of a
    chain (``"instance.attr"``), read ``authored_text`` off the reference use that
    ``inspect_reference_uses`` returns.

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
        target = resolved_chain_target(expr)
    elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        target = resolved_referent(expr)
    else:
        return None
    if target is None:
        raise evidence_error(
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


def reconstruct_expression(expr_node: Any, _depth: int = 0) -> str:
    """Reconstruct expression text from SysML AST nodes.

    Shares the one production traversal budget (`MAX_EXPRESSION_DEPTH`); `_depth` is the
    recursion's own position, not a caller knob.
    """
    if isinstance(expr_node, str):
        return expr_node

    if expr_node is None:
        return ""

    if _depth >= MAX_EXPRESSION_DEPTH:
        raise evidence_error(
            SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED,
            "reconstruct_expression",
            "maximum expression traversal depth exhausted before the text was reconstructed",
            expr_node,
        )

    # FeatureChainExpression MUST be before OperatorExpression because FCE is a
    # subtype of OE in SysIDE's type system.
    if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return authored_reference_text(expr_node)

    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return reconstruct_operator_expression(expr_node, _depth)

    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return authored_reference_text(expr_node)

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
        args = ", ".join(reconstruct_expression(op, _depth + 1) for op in operands)
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


def reconstruct_operator_expression(expr_node: Any, _depth: int = 0) -> str:
    """Reconstruct an operator expression with precedence-aware parentheses.

    `_depth` carries the shared traversal budget through the recursion; see
    `reconstruct_expression`.
    """
    operator = ""
    if hasattr(expr_node, "operator") and expr_node.operator:
        operator = str(expr_node.operator)

    operands = materialize_operands(expr_node)

    if len(operands) == 2:
        parent_rank = RANK.get(operator)
        right_assoc = operator in RIGHT_ASSOC
        left = reconstruct_expression(operands[0], _depth + 1)
        right = reconstruct_expression(operands[1], _depth + 1)
        if parent_rank is not None:
            if needs_parens(parent_rank, right_assoc, operands[0], "left"):
                left = f"({left})"
            if needs_parens(parent_rank, right_assoc, operands[1], "right"):
                right = f"({right})"
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        return f"{left}{op_str}{right}"

    if len(operands) == 1:
        operand = reconstruct_expression(operands[0], _depth + 1)
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
            text = reconstruct_expression(op, _depth + 1)
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

    # Standard-library references are not design dependencies, so anything left is one.
    return not design_reference_uses(expr)

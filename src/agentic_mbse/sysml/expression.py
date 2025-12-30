"""Expression traversal utilities for SysML AST analysis.

This module provides functions for traversing and analyzing SysML expression
ASTs, including visitor-pattern traversal and reference extraction.
"""

from collections.abc import Callable
from typing import Any

from agentic_mbse.sysml.types import ExpressionRef

# Standard library qualified name prefixes to filter.
# These are constants/types from the SysML standard library, not design-specific values.
# Unit annotations like `3.0 [m]` contain references to SI::metre, which should not
# be treated as "derived expressions" per ADR-002.
STANDARD_LIBRARY_PREFIXES = (
    "SI::",  # SI units (metre, kilogram, second, etc.)
    "ISQ::",  # ISQ quantity types (Length, Mass, Time, etc.)
    "ScalarValues::",  # Scalar types (Real, Integer, Boolean, String)
    "UnitsAndScales::",  # Unit system definitions
)


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

    # Recurse into children based on expression type
    # Check for operator expression with operands
    if _is_operator_expression(expr):
        if hasattr(expr, "operands"):
            try:
                for operand in expr.operands:
                    child_results = traverse_expression(
                        operand, visitor, max_depth, _current_depth + 1
                    )
                    results.extend(child_results)
            except (TypeError, AttributeError):
                pass
    elif hasattr(expr, "operands"):
        # Fallback: check for operands attribute directly (mock pattern)
        try:
            for operand in expr.operands:
                child_results = traverse_expression(
                    operand, visitor, max_depth, _current_depth + 1
                )
                results.extend(child_results)
        except (TypeError, AttributeError):
            pass

    return results


def _is_operator_expression(expr: Any) -> bool:
    """Check if expression is an OperatorExpression type."""
    # Try to detect OperatorExpression via type name
    # This works with both real syside and our mocks
    type_name = type(expr).__name__
    return "Operator" in type_name or "OperatorExpression" in type_name


def _is_standard_library_ref(ref: ExpressionRef) -> bool:
    """Check if reference points to a standard library element.

    Standard library elements are:
    - SI units (SI::metre, SI::kilogram, etc.)
    - ISQ quantities (ISQ::Length, ISQ::Mass, etc.)
    - Scalar values (ScalarValues::Real, ScalarValues::Integer, etc.)
    - Units and scales definitions (UnitsAndScales::*)

    Args:
        ref: ExpressionRef to check

    Returns:
        True if reference is to standard library element
    """
    if not ref.qualified_name:
        return False
    return any(
        ref.qualified_name.startswith(prefix) for prefix in STANDARD_LIBRARY_PREFIXES
    )


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
        type_name = type(node).__name__

        # Check for reference types
        if "FeatureReference" in type_name or "FeatureChain" in type_name:
            name = ""
            qualified_name = ""
            doc_path = None
            element = None

            # For FeatureChainExpression, prefer target_feature (the final target)
            if "FeatureChain" in type_name and hasattr(node, "target_feature"):
                target = node.target_feature
                if target:
                    element = target
                    if hasattr(target, "name") and target.name:
                        name = target.name
                    if hasattr(target, "qualified_name"):
                        qn = target.qualified_name
                        qualified_name = str(qn) if qn else ""
                    if hasattr(target, "document") and target.document:
                        if hasattr(target.document, "url"):
                            doc_path = str(target.document.url)

            # Fallback: Try to extract name from node directly
            if not name:
                if hasattr(node, "name") and node.name:
                    name = node.name

            # Fallback: Try to extract qualified_name
            if not qualified_name:
                if hasattr(node, "qualified_name") and node.qualified_name:
                    qualified_name = str(node.qualified_name)

            # Fallback: Try to get target element from memberships (syside pattern)
            if not name and hasattr(node, "memberships"):
                try:
                    for membership in node.memberships:
                        if hasattr(membership, "member_element"):
                            target = membership.member_element
                            if target:
                                element = target
                                if hasattr(target, "name") and target.name:
                                    name = target.name
                                if hasattr(target, "qualified_name"):
                                    qn = target.qualified_name
                                    qualified_name = str(qn) if qn else ""
                                if hasattr(target, "document") and target.document:
                                    if hasattr(target.document, "url"):
                                        doc_path = str(target.document.url)
                                break
                except (AttributeError, TypeError):
                    pass

            # Fallback: Try referent attribute (alternative syside pattern)
            if not name and hasattr(node, "referent") and node.referent:
                element = node.referent
                if hasattr(node.referent, "name"):
                    name = node.referent.name
                if hasattr(node.referent, "qualified_name"):
                    qn = node.referent.qualified_name
                    qualified_name = str(qn) if qn else ""

            if name:
                ref = ExpressionRef(
                    name=name,
                    qualified_name=qualified_name,
                    document_path=doc_path,
                    element=element,
                )
                # Filter standard library refs if requested (via closure)
                if ignore_std_lib and _is_standard_library_ref(ref):
                    return None
                return ref

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
        type_name = type(node).__name__

        if "Operator" in type_name and hasattr(node, "operator"):
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
    type_name = type(expr).__name__
    return "Literal" in type_name


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
    type_name = type(expr).__name__
    return "FeatureReference" in type_name or "FeatureChain" in type_name


# Supported operators for static expressions (per ADR-002)
STATIC_OPERATORS = {"+", "-", "*", "/", "["}


def get_reference_name(expr: Any) -> str | None:
    """Extract the name from a feature reference expression.

    Works with both FeatureReferenceExpression and FeatureChainExpression.
    Consolidates logic from parameter_group_derivation._extract_reference_path()
    and avoids duplication with the evaluator.

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
    # Try direct name attribute (works for mock objects and simple refs)
    if hasattr(expr, "name") and expr.name:
        return expr.name

    # Try memberships pattern (syside AST structure)
    if hasattr(expr, "memberships"):
        for m in expr.memberships:
            if hasattr(m, "member_element") and m.member_element:
                elem = m.member_element
                if hasattr(elem, "name") and elem.name:
                    return elem.name

    # Try target_feature for chain expressions
    if hasattr(expr, "target_feature") and expr.target_feature:
        target = expr.target_feature
        if hasattr(target, "name") and target.name:
            return target.name

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
            f"This violates ADR-002 Rule 3. Run 'python scripts/sysml_checks/run_all_checks.py' "
            f"to identify and fix the violation."
        )

    # Case 3: Operator expression
    if _is_operator_expression(expr):
        # Get operator - may be Operator enum (syside) or string (mocks)
        operator_raw = getattr(expr, "operator", None)
        operator = str(operator_raw) if operator_raw is not None else None
        operands = list(getattr(expr, "operands", []))

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

        raise ValueError(
            f"Operator '{operator}' with unexpected operand count: {len(operands)}"
        )

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

"""Binding analysis utilities for SysML calc usages.

This module provides functions for extracting and classifying parameter
bindings from CalculationUsage AST elements.
"""

from typing import Any

from agentic_mbse.sysml.expression import extract_feature_refs, extract_literal_value
from agentic_mbse.sysml.types import BindingInfo, BindingType, ExpressionRef


def classify_binding(expr: Any) -> BindingType:
    """Classify a binding expression into a BindingType.

    Examines the top-level expression type to determine the binding category.
    This is used to understand how a parameter receives its value.

    Args:
        expr: Expression AST node (or None for unbound)

    Returns:
        BindingType classification:
        - UNBOUND: No expression (None)
        - CHAIN: FeatureChainExpression (instance.attribute)
        - REFERENCE: FeatureReferenceExpression (simple_name)
        - LITERAL: LiteralRational, LiteralInteger, etc.
        - EXPRESSION: OperatorExpression (a + b * 2)

    Example:
        >>> classify_binding(None)
        BindingType.UNBOUND
        >>> classify_binding(chain_expr)
        BindingType.CHAIN
    """
    if expr is None:
        return BindingType.UNBOUND

    type_name = type(expr).__name__

    # Check for feature chain (instance.attribute)
    if "FeatureChain" in type_name:
        return BindingType.CHAIN

    # Check for operator expression (arithmetic)
    if "Operator" in type_name:
        return BindingType.EXPRESSION

    # Check for simple feature reference
    if "FeatureReference" in type_name:
        return BindingType.REFERENCE

    # Check for literal types
    if "Literal" in type_name:
        return BindingType.LITERAL

    # Default: if it has operands, it's an expression
    if hasattr(expr, "operands"):
        return BindingType.EXPRESSION

    # Unknown type - treat as reference
    return BindingType.REFERENCE


def extract_bindings(calc_usage: Any) -> list[BindingInfo]:
    """Extract all parameter bindings from a CalculationUsage.

    Analyzes a calc usage element and returns detailed binding information
    for each parameter, including binding type, source, and cross-file status.

    Args:
        calc_usage: CalculationUsage AST element

    Returns:
        List of BindingInfo for each parameter in the calc usage

    Example:
        >>> bindings = extract_bindings(calc_usage)
        >>> for b in bindings:
        ...     print(f"{b.param_name}: {b.binding_type.value}")
    """
    bindings: list[BindingInfo] = []

    # Get usage document URL for cross-file comparison
    usage_doc_url = _get_document_url(calc_usage)

    # Iterate owned_members to find parameters
    if not hasattr(calc_usage, "owned_members"):
        return bindings

    for member in calc_usage.owned_members:
        # Filter to attribute/reference usages (parameters)
        if not _is_parameter_member(member):
            continue

        param_name = getattr(member, "name", "")
        if not param_name:
            continue

        expr = getattr(member, "feature_value_expression", None)
        binding_type = classify_binding(expr)

        # Build binding info based on type
        binding_info = _build_binding_info(
            param_name=param_name,
            expr=expr,
            binding_type=binding_type,
            usage_doc_url=usage_doc_url,
        )
        bindings.append(binding_info)

    return bindings


def _is_parameter_member(member: Any) -> bool:
    """Check if member is an AttributeUsage or ReferenceUsage."""
    # Check _supported_types for mocks
    if hasattr(member, "_supported_types"):
        return True
    # Try isinstance method (syside pattern)
    type_name = type(member).__name__
    return "AttributeUsage" in type_name or "ReferenceUsage" in type_name or "Member" in type_name


def _get_document_url(element: Any) -> str | None:
    """Extract document URL from an element."""
    if hasattr(element, "document") and element.document:
        if hasattr(element.document, "url"):
            return str(element.document.url)
    return None


def _build_binding_info(
    param_name: str,
    expr: Any,
    binding_type: BindingType,
    usage_doc_url: str | None,
) -> BindingInfo:
    """Build a BindingInfo from expression and context."""
    source_path: str | None = None
    literal_value: float | int | str | bool | None = None
    expression_ast: Any = None
    references: list[ExpressionRef] = []
    is_cross_file = False

    if binding_type == BindingType.LITERAL:
        # Extract literal value
        literal_value = extract_literal_value(expr)

    elif binding_type == BindingType.CHAIN:
        # Build source path for chain expression
        source_path = _build_chain_source_path(expr)
        # Check cross-file
        is_cross_file = _is_cross_file_reference(expr, usage_doc_url)

    elif binding_type == BindingType.REFERENCE:
        # Simple reference - extract name as source path
        source_path = _extract_reference_name(expr)
        is_cross_file = _is_cross_file_reference(expr, usage_doc_url)

    elif binding_type == BindingType.EXPRESSION:
        # Preserve AST and extract references
        expression_ast = expr
        references = extract_feature_refs(expr)
        # Cross-file if any reference is from different file
        for ref in references:
            if ref.document_path and usage_doc_url:
                if ref.document_path != usage_doc_url:
                    is_cross_file = True
                    break

    return BindingInfo(
        param_name=param_name,
        source_path=source_path,
        binding_type=binding_type,
        is_cross_file=is_cross_file,
        literal_value=literal_value,
        expression_ast=expression_ast,
        references=references,
    )


def _build_chain_source_path(expr: Any) -> str | None:
    """Build dotted source path from FeatureChainExpression."""
    # Try instance_name.attr_name pattern (mock)
    if hasattr(expr, "instance_name") and hasattr(expr, "attr_name"):
        return f"{expr.instance_name}.{expr.attr_name}"

    # Try to extract from memberships
    if hasattr(expr, "memberships"):
        names = []
        for membership in expr.memberships:
            if hasattr(membership, "member_element"):
                target = membership.member_element
                if hasattr(target, "name") and target.name:
                    names.append(target.name)
        if names:
            return ".".join(names)

    return None


def _extract_reference_name(expr: Any) -> str | None:
    """Extract name from FeatureReferenceExpression."""
    if hasattr(expr, "name") and expr.name:
        return expr.name

    # Try memberships pattern
    if hasattr(expr, "memberships"):
        for membership in expr.memberships:
            if hasattr(membership, "member_element"):
                target = membership.member_element
                if hasattr(target, "name") and target.name:
                    return target.name
    return None


def _is_cross_file_reference(expr: Any, usage_doc_url: str | None) -> bool:
    """Determine if expression references element in different file.

    Cross-file detection edge cases (from spec):
    - If document URL cannot be determined for usage, assume same-file (False)
    - If document URL cannot be determined for referenced element, assume same-file (False)
    - Only return True when both URLs are available AND different
    """
    if usage_doc_url is None:
        return False

    # Try to get document URL from expression target
    target_url = _get_target_document_url(expr)
    if target_url is None:
        return False

    return target_url != usage_doc_url


def _get_target_document_url(expr: Any) -> str | None:
    """Extract document URL from expression target element."""
    # Check expression's own document
    if hasattr(expr, "document") and expr.document:
        if hasattr(expr.document, "url"):
            return str(expr.document.url)

    # Check through memberships
    if hasattr(expr, "memberships"):
        for membership in expr.memberships:
            if hasattr(membership, "member_element"):
                target = membership.member_element
                if target and hasattr(target, "document") and target.document:
                    if hasattr(target.document, "url"):
                        return str(target.document.url)

    return None

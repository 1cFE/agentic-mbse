#!/usr/bin/env python3
"""
ADR-002 Validation Checks

Implements validation rules from ADR-002 (Calculation Architecture):
- V1: Calc defs must be in library/, not designs/
- V2: Design expressions must be statically evaluable
- V4: Only supported operators in static expressions

These checks are integrated into Level 2 structural validation.
"""
from typing import Any

from agentic_mbse.sysml.expression import extract_feature_refs, extract_operators
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import ExpressionRef, Severity, ValidationCode, ValidationIssue

try:
    from .common import get_element_location, get_qualified_name
except ImportError:
    from common import get_element_location, get_qualified_name


# Supported operators per ADR-002
SUPPORTED_OPERATORS = {"+", "-", "*", "/", "[", "^"}


def check_calc_def_locations(model: Any) -> list[ValidationIssue]:
    """
    V1: Check that all calc defs are in library/, not designs/.

    Per ADR-002: "Calculation definitions must be in library/, not designs/"

    Algorithm:
    1. Find all CalculationDefinition elements in model
    2. For each, check document URL for path
    3. If path contains "designs/" → ERROR
    4. Suggestion: "Move to library/"

    Args:
        model: Loaded SysML model

    Returns:
        List of ValidationIssue for V1 violations
    """
    issues: list[ValidationIssue] = []

    for calc_def in SysideAdapter.elements_of_type(model, "CalculationDefinition"):
        try:
            doc = calc_def.document
            if not doc or not hasattr(doc, "url"):
                continue

            doc_path = str(doc.url)

            # Check if in designs/ directory (and NOT in library/)
            if "designs/" in doc_path and "library/" not in doc_path:
                def_name = get_qualified_name(calc_def)
                location = get_element_location(calc_def)

                issues.append(
                    ValidationIssue(
                        level=2,
                        severity=Severity.ERROR,
                        code=ValidationCode.V1_CALC_DEF_LOCATION,
                        message=f"Calc def '{def_name}' is in designs/ instead of library/",
                        element_name=def_name,
                        location=location,
                        suggestion="Move calculation definition to library/ directory",
                    )
                )

        except Exception:
            # Skip elements we can't analyze
            continue

    return issues


def check_supported_operators(model: Any) -> list[ValidationIssue]:
    """
    V4: Check that static expressions only use supported operators.

    Supported operators: +, -, *, /, [ (unit annotation)
    Unsupported: ** (exponentiation), ^ (power), function calls

    Per ADR-002: "Unsupported operator in static expression.
    Use calc def for complex calculations."

    Algorithm:
    1. Find all AttributeUsage in designs/ with expressions
    2. For each expression, extract all operators
    3. If any operator not in SUPPORTED_OPERATORS → ERROR
    4. Suggestion: "Use calc def for complex calculations"

    Args:
        model: Loaded SysML model

    Returns:
        List of ValidationIssue for V4 violations
    """
    issues: list[ValidationIssue] = []

    for attr in SysideAdapter.elements_of_type(model, "AttributeUsage"):
        try:
            # Only check design files (not library calc defs)
            doc = attr.document
            if not doc or not hasattr(doc, "url"):
                continue

            doc_path = str(doc.url)
            if "library/" in doc_path:
                continue  # Skip library files (calc defs have different rules)

            # Check if attribute has an expression
            if (
                not hasattr(attr, "feature_value_expression")
                or not attr.feature_value_expression
            ):
                continue

            expr = attr.feature_value_expression

            # Extract all operators from expression
            operators = extract_operators(expr)

            # Check for unsupported operators
            for op in operators:
                if op not in SUPPORTED_OPERATORS:
                    attr_name = get_qualified_name(attr)
                    location = get_element_location(attr)

                    issues.append(
                        ValidationIssue(
                            level=2,
                            severity=Severity.ERROR,
                            code=ValidationCode.V4_UNSUPPORTED_OPERATOR,
                            message=f"Unsupported operator '{op}' in attribute '{attr_name}'",
                            element_name=attr_name,
                            location=location,
                            suggestion="Use calc def for complex calculations requiring this operator",
                        )
                    )

        except Exception:
            continue

    return issues


def _build_calc_output_catalog(model: Any) -> tuple[set[str], set[str]]:
    """
    Build catalog of calc output names and calc def qualified names from library/.

    Returns:
        Tuple of (output_names, calc_def_qualified_names)
        - output_names: Set of simple output parameter names (e.g., "output_val")
        - calc_def_qualified_names: Set of calc def qualified names
          (e.g., "V2TestLibrary::SimpleCalc")
    """
    outputs: set[str] = set()
    calc_def_qualified_names: set[str] = set()

    for calc_def in SysideAdapter.elements_of_type(model, "CalculationDefinition"):
        try:
            doc = calc_def.document
            if not doc or not hasattr(doc, "url"):
                continue

            doc_path = str(doc.url)
            if "library/" not in doc_path:
                continue  # Only catalog library calc defs

            calc_name = calc_def.name if hasattr(calc_def, "name") else ""

            # Collect calc def qualified name for pattern matching
            if hasattr(calc_def, "qualified_name") and calc_def.qualified_name:
                calc_def_qualified_names.add(str(calc_def.qualified_name))

            # Find output parameters
            if not hasattr(calc_def, "owned_members"):
                continue

            for member in calc_def.owned_members:
                if not (
                    SysideAdapter.is_instance(member, "AttributeUsage")
                    or SysideAdapter.is_instance(member, "ReferenceUsage")
                ):
                    continue

                # Check if output direction
                if hasattr(member, "direction"):
                    direction_str = str(member.direction)
                    if "Out" in direction_str or "Return" in direction_str:
                        output_name = member.name if hasattr(member, "name") else ""
                        if output_name:
                            # Add output name
                            outputs.add(output_name)
                            if calc_name:
                                outputs.add(f"{calc_name}::{output_name}")

        except Exception:
            continue

    return outputs, calc_def_qualified_names


def _get_calc_usage_names(model: Any) -> set:
    """Get set of all calc usage instance names."""
    names = set()
    for usage in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        try:
            name = usage.name if hasattr(usage, "name") else ""
            if name:
                names.add(name)
        except Exception:
            continue
    return names


def _is_calc_usage(element: Any) -> bool:
    """Check if element is a CalculationUsage."""
    try:
        return SysideAdapter.is_instance(element, "CalculationUsage")
    except Exception:
        return False


def _is_calc_output_reference(
    ref: ExpressionRef,
    calc_def_qualified_names: set[str],
) -> bool:
    """
    Check if ref points to a calc output using multiple verification signals.

    Uses a layered approach to distinguish actual calc outputs from same-named
    design attributes:

    1. document_path (primary): If contains 'library/' → True, 'designs/' → False
    2. qualified_name (secondary): If parent path matches known calc def → True
    3. owner type (tertiary): If owner is CalculationDefinition → True,
       if owner is PartUsage/PartDefinition → False
    4. Conservative fallback: If all methods fail → True (backwards compatible)

    Args:
        ref: ExpressionRef from extract_feature_refs()
        calc_def_qualified_names: Set of calc def qualified names for pattern matching

    Returns:
        True if ref is to a calc output (or if all verifications fail - conservative)
        False if ref is definitively NOT to a calc output
    """
    # Method 1: Document path check (simplest, most reliable)
    if ref.document_path:
        if "library/" in ref.document_path:
            return True  # From library - it's a calc output
        if "designs/" in ref.document_path:
            return False  # From designs - NOT a calc output

    # Method 2: Qualified name pattern (proven in codegen)
    if ref.qualified_name and "::" in ref.qualified_name:
        parts = ref.qualified_name.split("::")
        if len(parts) >= 2:
            # Check if parent path matches a calc def
            parent_path = "::".join(parts[:-1])
            if parent_path in calc_def_qualified_names:
                return True

    # Method 3: Owner type check (fallback)
    if ref.element:
        owner = getattr(ref.element, "owner", None)
        if owner:
            try:
                # Calc output owners are always CalculationDefinition
                if SysideAdapter.is_instance(owner, "CalculationDefinition"):
                    return True
                # Explicit negative: design attrs have Part owners
                if SysideAdapter.is_instance(owner, "PartUsage") or SysideAdapter.is_instance(
                    owner, "PartDefinition"
                ):
                    return False
            except Exception:
                pass

    # Conservative fallback only if ALL methods fail
    return True


def _is_part_usage(element: Any) -> bool:
    """Check if element is a PartUsage."""
    try:
        return SysideAdapter.is_instance(element, "PartUsage")
    except Exception:
        return False


def _is_expose_pattern(
    attr: Any,
    expr,
    calc_outputs: set,
) -> bool:
    """
    Check if attribute follows EXPOSE pattern: attribute x = calc.x OR attribute x = part.y

    The EXPOSE pattern is value propagation from:
    1. A sibling calc usage's output (attribute x = calc.output), OR
    2. A sibling part's attribute that is itself an EXPOSE (transitive EXPOSE)

    This is architecturally valid per ADR-002 amendment because it enables clean
    cross-file interfaces without introducing computation.

    Detection criteria:
    1. Expression is a FeatureChainExpression (x.y pattern) - NO arithmetic
    2. The intermediate element is either:
       a. A CalculationUsage in the same owner (direct EXPOSE), OR
       b. A PartUsage in the same owner (transitive EXPOSE)
    3. The target is a single attribute/output reference (no computation)

    Args:
        attr: The AttributeUsage being analyzed
        expr: The attribute's value expression
        calc_outputs: Set of known calc output names from library/

    Returns:
        True if this is an EXPOSE pattern (exempt from V2), False otherwise
    """
    try:
        # 1. Check expression type - must be FeatureChainExpression
        # This is the key distinguisher: EXPOSE uses FeatureChain,
        # computed expressions use OperatorExpression
        type_name = type(expr).__name__
        if "FeatureChain" not in type_name:
            return False

        # 2. Get the chain elements to identify the source instance
        if not hasattr(expr, "owned_members"):
            return False

        chain_members = list(expr.owned_members)
        if len(chain_members) < 1:
            return False

        # 3. The first chain element should reference a calc or part usage
        # AST structure: chain_member -> feature_value_expression -> referent
        first_member = chain_members[0]

        # Get the referenced element (the calc or part instance)
        # Path: first_member.feature_value_expression.referent
        source_instance = None

        if hasattr(first_member, "feature_value_expression"):
            fve = first_member.feature_value_expression
            if fve and hasattr(fve, "referent"):
                source_instance = fve.referent

        # Fallback paths for different AST structures
        if source_instance is None and hasattr(first_member, "member_element"):
            source_instance = first_member.member_element
        if source_instance is None and hasattr(first_member, "referent"):
            source_instance = first_member.referent

        if source_instance is None:
            return False

        # 4. Verify it's either a CalculationUsage OR a PartUsage
        is_calc = _is_calc_usage(source_instance)
        is_part = _is_part_usage(source_instance)

        if not is_calc and not is_part:
            return False

        # 5. Verify it's a sibling (same owner as the attribute)
        attr_owner = attr.owner if hasattr(attr, "owner") else None
        source_owner = source_instance.owner if hasattr(source_instance, "owner") else None

        if attr_owner is None or source_owner is None:
            return False

        # Same owner means they're siblings
        if attr_owner is not source_owner:
            return False

        # All criteria met - this is an EXPOSE pattern
        # For CalculationUsage: direct EXPOSE (e.g., attribute x = calc.output)
        # For PartUsage: transitive EXPOSE (e.g., attribute x = sibling_part.volume)
        return True

    except Exception:
        # Conservative: don't exempt if we can't analyze
        return False


def _generate_calc_def_guidance(attr_name: str, ref_names: list[str]) -> str:
    """
    Generate actionable guidance for converting derived expression to calc def.

    Args:
        attr_name: The attribute name with the derived expression
        ref_names: List of referenced attribute names

    Returns:
        Multi-line string with example calc def structure
    """
    # Generate input parameters from ref names
    inputs = "\n    ".join(f"in {name} : Real;" for name in ref_names)
    output_name = attr_name.split("::")[-1] if "::" in attr_name else attr_name

    return (
        f"Create a calc def in library/:\n\n"
        f"calc def {output_name.title().replace('_', '')}Calculation {{\n"
        f"    {inputs}\n"
        f"    out {output_name} : Real = <expression>;\n"
        f"}}\n\n"
        f"Then use a calc usage in your design file."
    )


def check_static_expressions(model: Any) -> list[ValidationIssue]:
    """
    V2: Validate that design attribute expressions are either:
    - True static (no feature references except standard library), OR
    - EXPOSE pattern (single reference to sibling calc output)

    Derived expressions (references to design attributes) are VIOLATIONS.

    Per ADR-002 Rule 3 Amendment (2025-12-22):
    - Expressions with FeatureReferenceExpression nodes are NOT allowed
      (except references to standard library: SI::, ISQ::, ScalarValues::)
    - Only expressions composed purely of literals are "true static"
    - This is a STRUCTURAL check, not a SEMANTIC check

    Algorithm:
    1. For each AttributeUsage in designs/ with expression:
       - Skip if inside a calc usage (bindings are allowed)
       - Extract all feature references (std lib filtered by default)
       - If no refs → TRUE STATIC → OK
       - If EXPOSE pattern → OK
       - Otherwise → DERIVED EXPRESSION VIOLATION

    Args:
        model: Loaded SysML model

    Returns:
        List of ValidationIssue for V2 violations
    """
    issues: list[ValidationIssue] = []

    # Build catalog of calc output names (still needed for EXPOSE pattern detection)
    calc_outputs, _ = _build_calc_output_catalog(model)

    # Check each attribute in design files
    for attr in SysideAdapter.elements_of_type(model, "AttributeUsage"):
        try:
            # Skip if inside a calc usage (bindings are allowed)
            owner = attr.owner if hasattr(attr, "owner") else None
            if owner and _is_calc_usage(owner):
                continue

            # Only check design files
            doc = attr.document
            if not doc or not hasattr(doc, "url"):
                continue

            doc_path = str(doc.url)
            if "library/" in doc_path:
                continue  # Skip library files

            # Check if attribute has an expression
            if (
                not hasattr(attr, "feature_value_expression")
                or not attr.feature_value_expression
            ):
                continue

            expr = attr.feature_value_expression

            # Extract all feature references (std lib filtered by default per Phase 1)
            refs = extract_feature_refs(expr)

            # TRUE STATIC: No refs after filtering = only literals + std lib
            if len(refs) == 0:
                continue  # OK - true static expression

            # EXPOSE PATTERN: Single ref to sibling calc output is exempt
            if _is_expose_pattern(attr, expr, calc_outputs):
                continue  # OK - EXPOSE pattern exempt

            # DERIVED EXPRESSION VIOLATION: Has feature refs that aren't EXPOSE
            attr_name = get_qualified_name(attr)
            location = get_element_location(attr)
            ref_names = [ref.name for ref in refs]

            issues.append(
                ValidationIssue(
                    level=2,
                    severity=Severity.ERROR,
                    code=ValidationCode.V2_DYNAMIC_EXPRESSION,
                    message=(
                        f"Derived expression references design attributes: {ref_names}"
                    ),
                    element_name=attr_name,
                    location=location,
                    suggestion=_generate_calc_def_guidance(attr_name, ref_names),
                )
            )

        except Exception:
            continue

    return issues

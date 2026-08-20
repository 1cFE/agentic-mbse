#!/usr/bin/env python3
"""
ADR-002 Validation Checks

Implements validation rules from ADR-002 (Calculation Architecture):
- V1: Calc defs must be in library/, not designs/
- V2: Design expressions must be statically evaluable
- V4: Only supported operators in static expressions

These checks are integrated into Level 6 architecture validation.
"""
from typing import Any

from agentic_mbse.sysml.expression import (
    design_reference_uses,
    extract_operators,
    traverse_expression,
)
from agentic_mbse.sysml.reference_use import (
    ExactReferenceUse,
    IndexedReferenceUse,
    ReferenceUse,
    resolved_referent,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue

try:
    from .common import get_element_location, get_qualified_name
except ImportError:
    from common import get_element_location, get_qualified_name


# Supported operators per ADR-002: `+ - * /` and unit annotation `[`. Power
# (`^`/`**`), function calls, and conditionals are NOT static operators — they
# belong in a calc def (C5, Item 12). `^` was previously (wrongly) in this set,
# so `a ^ b` in a static design expression slipped through; removing it makes the
# operator check flag it as V4_UNSUPPORTED_OPERATOR, matching codegen V4.
SUPPORTED_OPERATORS = {"+", "-", "*", "/", "["}


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
                        level=6,
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
            # C5/C6a (Item 12): skip attributes owned by a calc def. Power and other
            # non-static operators are legitimate inside a calc-def-internal
            # `out attribute X = <expr>` — that is exactly where ADR-002 says complex
            # calculations belong. The `library/` path skip below misses flat-layout
            # calc defs (no `library/` dir), so key off the owner type, not the path.
            owner = getattr(attr, "owner", None)
            if owner is not None and SysideAdapter.is_instance(
                owner, "CalculationDefinition"
            ):
                continue

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
                            level=6,
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


def check_static_function_invocations(model: Any) -> list[ValidationIssue]:
    """
    C5 (Item 12): WARN on a function invocation inside a static design expression.

    A design-attribute expression like `x : Real = sqrt(2.0)` invokes a function
    (an InvocationExpression that is not an operator). Function results are not
    statically extractable — codegen cannot evaluate them at design scope, so the
    modeler should move the calculation into a calc def. WARNING, not ERROR, so
    Level 6 stays passing (mirrors codegen V4's steer-to-calc-def guidance).

    Operators (`a ^ b`, `a * b`) are OperatorExpressions, handled by
    check_supported_operators; only genuine function calls are flagged here.

    Returns:
        List of ValidationIssue (WARNING) for static function invocations.
    """
    issues: list[ValidationIssue] = []

    def _is_invocation(node: Any) -> Any:
        try:
            if SysideAdapter.is_instance(
                node, "InvocationExpression"
            ) and not SysideAdapter.is_instance(node, "OperatorExpression"):
                return node
        except Exception:
            return None
        return None

    for attr in SysideAdapter.elements_of_type(model, "AttributeUsage"):
        try:
            # Bindings inside calc usages are not static design expressions.
            owner = getattr(attr, "owner", None)
            if owner is not None and _is_calc_usage(owner):
                continue

            # C5/C6a (Item 12): a calc-def-internal `out attribute X = f(...)` is where
            # function invocations legitimately live; the `library/` skip below misses
            # flat-layout calc defs, so also skip by owner type.
            if owner is not None and SysideAdapter.is_instance(
                owner, "CalculationDefinition"
            ):
                continue

            doc = attr.document
            if not doc or not hasattr(doc, "url"):
                continue
            if "library/" in str(doc.url):
                continue  # library calc defs may invoke functions freely

            expr = getattr(attr, "feature_value_expression", None)
            if not expr:
                continue

            if not traverse_expression(expr, _is_invocation):
                continue

            attr_name = get_qualified_name(attr)
            issues.append(
                ValidationIssue(
                    level=6,
                    severity=Severity.WARNING,
                    code=ValidationCode.V4_STATIC_FUNCTION_INVOCATION,
                    message=(
                        f"Static design expression in '{attr_name}' invokes a function; "
                        f"function results are not statically extractable"
                    ),
                    element_name=attr_name,
                    location=get_element_location(attr),
                    suggestion="Move the calculation into a calc def",
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


def reference_is_dynamic(use: ReferenceUse) -> bool:
    """Whether a reference use counts as a dynamic reference for V2.

    Both variants of the closed union do.  An indexed use is a reference the model
    authored and the toolchain cannot honor exactly; treating it as absent would let a
    dynamic expression pass V2 because its index made it unreadable.  It is counted here
    and never flattened into an exact path or an empty reference list.
    """
    return isinstance(use, (ExactReferenceUse, IndexedReferenceUse))


def _is_calc_output_reference(
    use: ExactReferenceUse,
    calc_def_qualified_names: set[str],
) -> bool:
    """
    Check if ref points to a calc output using semantic evidence only.

    A known calculation-definition qualified name is positive evidence.  Otherwise the
    mapped owner metatype captured at the evidence boundary decides.  URL spellings and
    runtime Python class names have no classification force.  Missing evidence fails
    closed so it cannot exempt a dynamic reference from V2.

    Args:
        use: one ExactReferenceUse from design_reference_uses()
        calc_def_qualified_names: Set of calc def qualified names for pattern matching

    Returns:
        True if the evidence identifies a calculation output; False otherwise.
    """
    leaf = use.path.leaf

    # Qualified-name identity against the model's known calculation definitions.
    if leaf.qualified_name and "::" in leaf.qualified_name:
        parts = leaf.qualified_name.split("::")
        if len(parts) >= 2:
            # Check if parent path matches a calc def
            parent_path = "::".join(parts[:-1])
            if parent_path in calc_def_qualified_names:
                return True

    # Mapped owner-metatype evidence captured while the live element was available.
    if leaf.owner_is_calculation_definition:
        return True
    if leaf.owner_is_part:
        return False

    return False


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
            if fve is not None:
                source_instance = resolved_referent(fve)

        # Fallback paths for different AST structures
        if source_instance is None and hasattr(first_member, "member_element"):
            source_instance = first_member.member_element
        if source_instance is None:
            source_instance = resolved_referent(first_member)

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


def _contains_feature_chain(expr: Any) -> bool:
    """True if the expression tree contains a FeatureChainExpression (a dotted path).

    Codegen's FORMULA compiler rejects any FeatureChainExpression in a computed-
    attribute body, so a dotted path disqualifies an expression from the supported-
    FORMULA exemption in check_static_expressions (it is not a working FORMULA).
    """

    def _visitor(node: Any) -> Any:
        return node if "FeatureChain" in type(node).__name__ else None

    return bool(traverse_expression(expr, _visitor))


def _is_supported_formula(attr: Any, uses: tuple[ExactReferenceUse, ...]) -> bool:
    """True if a design computed attribute is a codegen-supported FORMULA (F6).

    sysml-codegen classifies a design-file `attribute X = <expr>` as a FORMULA
    computed attribute — a first-class, end-to-end supported wire as of Item 5 —
    when every feature reference resolves to a same-part OWNED sibling and the
    attribute does not reference itself. A FORMULA may read a literal sibling OR
    another FORMULA sibling on the same part (REQ-CA-06). These shapes generate
    and resolve, so flagging them V2_DYNAMIC_EXPRESSION is a false positive.

    The discriminator mirrors codegen's `_classify_attribute_expression`
    (computed_attribute_extractor.py): a ref is a same-part sibling iff its
    qualified name is nested under the owning part's qualified name. A ref whose
    qualified name is NOT under the part — a calc output in a foreign namespace
    (`my_calc.output * 0.95`) or an inherited attribute (carries the supertype's
    QN) — is the genuinely-unsupported case and must STILL fire. A self-reference
    (REQ-CA-07) falls through to the violation too. Dotted paths are excluded by
    the caller via _contains_feature_chain.
    """
    owner = getattr(attr, "owner", None)
    if owner is None:
        return False
    owner_qn = get_qualified_name(owner)
    if not owner_qn:
        return False
    prefix = owner_qn + "::"
    attr_qn = get_qualified_name(attr)

    for use in uses:
        ref_qn = use.path.leaf.qualified_name or ""
        # Foreign reference (calc output, cross-part, or inherited) -> not a FORMULA.
        if not ref_qn.startswith(prefix):
            return False
        # Self-reference -> codegen drops it (REQ-CA-07).
        if attr_qn and ref_qn == attr_qn:
            return False
    return True


def check_static_expressions(model: Any) -> list[ValidationIssue]:
    """
    V2: Validate that design attribute expressions are either:
    - True static (no feature references except standard library), OR
    - EXPOSE pattern (single reference to sibling calc output), OR
    - a supported FORMULA computed attribute (refs are all same-part siblings)

    A derived expression that references a calc output inside arithmetic (or
    combines calc outputs) is still a VIOLATION.

    Per ADR-002 Rule 3, as relaxed by sysml-codegen Item 5 (FORMULA computed
    attributes):
    - Expressions composed purely of literals + std lib are "true static"
    - An expression whose feature refs are all same-part owned siblings is a
      supported FORMULA (see _is_supported_formula) — NOT a violation
    - A reference to a calc output (foreign namespace) in arithmetic is the
      unsupported dynamic-expression case and fires V2_DYNAMIC_EXPRESSION
    - This is a STRUCTURAL check, not a SEMANTIC check

    Algorithm:
    1. For each AttributeUsage in designs/ with expression:
       - Skip if inside a calc usage or owned by a calc def (bindings/FORMULA-in-def)
       - Extract all feature references (std lib filtered by default)
       - If no refs → TRUE STATIC → OK
       - If EXPOSE pattern → OK
       - If supported FORMULA (all refs same-part siblings, no chain) → OK
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

            # C6a (Item 12): skip attributes owned by a calc def. A calc-def-internal
            # `out attribute X = <expr>` is exactly where ADR-002 says derived
            # expressions belong, so it is never a V2 violation. The `library/` path
            # skip below misses fixtures laid out as flat `library.sysml` files (no
            # `library/` dir), so key off the owner type, not the path.
            if owner and SysideAdapter.is_instance(owner, "CalculationDefinition"):
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
            uses = design_reference_uses(expr)

            # TRUE STATIC: No refs after filtering = only literals + std lib
            if not any(reference_is_dynamic(use) for use in uses):
                continue  # OK - true static expression

            # EXPOSE PATTERN: Single ref to sibling calc output is exempt
            if _is_expose_pattern(attr, expr, calc_outputs):
                continue  # OK - EXPOSE pattern exempt

            # F6 (Item 12): a design computed attribute whose refs are all same-part
            # owned siblings is a codegen-supported FORMULA (Item 5), not a violation.
            # A dotted path is rejected by codegen's FORMULA compiler, so a chain
            # keeps firing; a foreign (calc-output) ref keeps firing.
            exact_uses = tuple(use for use in uses if isinstance(use, ExactReferenceUse))
            if (
                len(exact_uses) == len(uses)
                and not _contains_feature_chain(expr)
                and _is_supported_formula(attr, exact_uses)
            ):
                continue  # OK - supported FORMULA computed attribute

            # DERIVED EXPRESSION VIOLATION: Has feature refs that aren't EXPOSE
            attr_name = get_qualified_name(attr)
            location = get_element_location(attr)
            ref_names = [
                use.path.leaf.element_name
                if isinstance(use, ExactReferenceUse)
                else use.reference
                for use in uses
            ]

            issues.append(
                ValidationIssue(
                    level=6,
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

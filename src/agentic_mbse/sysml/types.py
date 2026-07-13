"""Core type definitions for SysML analysis.

This module defines the fundamental data structures used throughout
the sysml_utils library for:

- Classifying parameter bindings (BindingType enum)
- Tracking validation results (Severity, ValidationCode, ValidationIssue)
- Capturing expression references (ExpressionRef, BindingInfo)
- Summarizing calculation usages (CalcUsageInfo)
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BindingType(Enum):
    """Classification of SysML binding expression types.

    Used to understand how a calculation parameter receives its value.
    This classifies the TOP-LEVEL binding expression, not internal components.

    Values:
        CHAIN: FeatureChainExpression like `instance.attribute` - entire binding is a chain
        REFERENCE: FeatureReferenceExpression like `simple_name` - entire binding is simple ref
        LITERAL: Constant value like `42.0` or `"string"` - entire binding is literal
        EXPRESSION: Arithmetic expression like `a + b * 2` - has operators, may contain refs
        UNBOUND: No binding - parameter uses default or is entry point

    Classification Examples:
        `in x = instance.attr` → CHAIN
        `in x = simple_name` → REFERENCE
        `in x = 42.0` → LITERAL
        `in x = instance.attr + 2` → EXPRESSION (has operator)
        `in x = a + b` → EXPRESSION (has operator)
        No binding → UNBOUND

    Example:
        >>> binding_type = BindingType.CHAIN
        >>> binding_type.value
        'chain'
    """

    CHAIN = "chain"
    REFERENCE = "reference"
    LITERAL = "literal"
    EXPRESSION = "expression"
    UNBOUND = "unbound"


class Severity(Enum):
    """Severity level for validation issues.

    Values:
        ERROR: Blocking issue - validation fails
        WARNING: Non-blocking - validation passes with warnings
        INFO: Informational - for metrics only
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationCode(str, Enum):
    """Machine-readable codes for all validation issues.

    Provides consistent, programmatically-checkable issue identifiers.
    Inherits from str for easy JSON serialization.
    """

    # ADR-002 Rules
    V1_CALC_DEF_LOCATION = "V1_CALC_DEF_LOCATION"
    V2_DYNAMIC_EXPRESSION = "V2_DYNAMIC_EXPRESSION"
    V3_CIRCULAR_DEPENDENCY = "V3_CIRCULAR_DEPENDENCY"
    V4_UNSUPPORTED_OPERATOR = "V4_UNSUPPORTED_OPERATOR"
    # C5 (Item 12): a function invocation inside a static design expression is not
    # statically extractable — steer the modeler to a calc def. WARN, not ERROR.
    V4_STATIC_FUNCTION_INVOCATION = "V4_STATIC_FUNCTION_INVOCATION"

    # Structural Issues
    UNBOUND_INPUT = "UNBOUND_INPUT"
    UNDEFINED_BINDING = "UNDEFINED_BINDING"
    LITERAL_BINDING = "LITERAL_BINDING"
    UNUSED_DEFINITION = "UNUSED_DEFINITION"
    # C1 (Item 12): an input bound to a same-named reference that dead-ends on the
    # calc's own parameter, with no producer of that name in scope. FAIL, L2.
    L2_SELF_NAMED_BINDING = "L2_SELF_NAMED_BINDING"

    # Dataflow Issues
    CIRCULAR_IMPORT = "CIRCULAR_IMPORT"

    # Level 6: Architecture & Pipeline Readiness
    L6_MISSING_QUALIFIED_NAME = "L6_MISSING_QUALIFIED_NAME"
    L6_INVALID_QUALIFIED_NAME = "L6_INVALID_QUALIFIED_NAME"
    L6_CALC_DEF_NO_OUTPUT = "L6_CALC_DEF_NO_OUTPUT"
    L6_CALC_DEF_NO_DIRECTION = "L6_CALC_DEF_NO_DIRECTION"
    L6_INVALID_BINDING_FORMAT = "L6_INVALID_BINDING_FORMAT"
    L6_DESIGN_ATTR_INCOMPLETE = "L6_DESIGN_ATTR_INCOMPLETE"
    L6_DESIGN_ATTR_UNEXTRACTABLE = "L6_DESIGN_ATTR_UNEXTRACTABLE"
    # Item 12 architecture checks (mirror sysml-codegen's shipped behavior).
    # C2a: an anonymous `return` (no declared name) yields no output channel -> FAIL (mirrors codegen V8).
    L6_ANONYMOUS_RETURN = "L6_ANONYMOUS_RETURN"
    # C2b: `return attribute y; y = expr` body-assignment extracts an output but loses auto-impl -> WARN.
    L6_BODY_ASSIGNMENT_IMPL_LOSS = "L6_BODY_ASSIGNMENT_IMPL_LOSS"
    # C3 / CONSTRAINT-EXEC Item 3: a would-execute constraint usage's predicate carries an
    # ineligible construct (executable_profile.evaluate_profile blocked it) -> WARN, one per
    # blocked construct, naming the construct + reason. Replaces the blanket
    # L6_CONSTRAINT_NON_EXECUTABLE warning, which fired on every constraint regardless of
    # whether its predicate was actually executable.
    L6_CONSTRAINT_INELIGIBLE = "L6_CONSTRAINT_INELIGIBLE"
    # C4: a calc-bearing part def that no usage instantiates (plainly or by retyping) -> FAIL; its template calcs are dropped.
    L6_CALC_DEF_NO_INSTANTIATION = "L6_CALC_DEF_NO_INSTANTIATION"
    # C7 (Item 9): `attribute :>> attr = <expr>` parses as an AttributeUsage, but codegen's
    # redefinition scan reads only ReferenceUsage -> the override is silently dropped -> WARN.
    L6_ATTR_REDEF_EXPR_DROPPED = "L6_ATTR_REDEF_EXPR_DROPPED"


class ExpressionRef(BaseModel):
    """A reference to an attribute found within an expression.

    Represents a single FeatureReferenceExpression or FeatureChainExpression
    target discovered during expression traversal.

    Attributes:
        name: Simple name of the referenced element (e.g., "volume")
        qualified_name: Full qualified name (e.g., "Package::part_name::attribute")
        document_path: Path to the file containing this element
        element: The raw AST element (for advanced analysis, not serialized)

    Example:
        >>> ref = ExpressionRef(
        ...     name="volume",
        ...     qualified_name="Package::part_name::attribute",
        ...     document_path="models/designs/example/component.sysml"
        ... )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    qualified_name: str = ""
    document_path: str | None = None
    element: Any | None = Field(default=None, exclude=True)


class ValidationIssue(BaseModel):
    """A structured validation issue with full context.

    Replaces unstructured string issues with typed, machine-readable data.

    Attributes:
        level: Validation level where issue was found (1-6)
        severity: ERROR, WARNING, or INFO
        code: Machine-readable issue code from ValidationCode enum
        message: Human-readable description
        element_name: Name of the affected element
        location: File:line location string
        suggestion: Optional guidance for fixing the issue

    Example:
        >>> issue = ValidationIssue(
        ...     level=2,
        ...     severity=Severity.ERROR,
        ...     code=ValidationCode.UNBOUND_INPUT,
        ...     message="Input 'power_output' has no binding",
        ...     element_name="net_electric",
        ...     location="physics.sysml:42"
        ... )
    """

    level: int
    severity: Severity
    code: ValidationCode
    message: str
    element_name: str = ""
    location: str = ""
    suggestion: str | None = None

    def __str__(self) -> str:
        """Format as human-readable string for backward compatibility."""
        if self.severity == Severity.ERROR:
            prefix = "ERROR"
        elif self.severity == Severity.WARNING:
            prefix = "WARN"
        else:
            prefix = "INFO"
        loc = f" at {self.location}" if self.location else ""
        return f"{prefix}: {self.message}{loc}"


class BindingInfo(BaseModel):
    """Detailed binding information for a calculation parameter.

    Captures everything needed to understand how a calc input is bound:
    what it's bound to, where that binding comes from, and its type.

    Attributes:
        param_name: Name of the parameter being bound (e.g., "power_output")
        source_path: Binding source as dotted path (e.g., "instance.attribute")
                     None if unbound
        binding_type: Classification of the binding expression
        is_cross_file: True if binding references element in different file.
                       Defaults to False when document URLs unavailable.
        literal_value: Parsed value for LITERAL bindings
        expression_ast: Raw AST for EXPRESSION bindings (for static evaluation, not serialized)
        references: List of all attribute references in the expression

    Example:
        >>> binding = BindingInfo(
        ...     param_name="power_output",
        ...     source_path="instance.attribute",
        ...     binding_type=BindingType.CHAIN,
        ...     is_cross_file=False
        ... )
        >>> binding.is_bound
        True
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=False)

    param_name: str
    source_path: str | None = None
    binding_type: BindingType
    is_cross_file: bool = False
    literal_value: float | int | str | bool | None = None
    expression_ast: Any | None = Field(default=None, exclude=True)
    references: list[ExpressionRef] = Field(default_factory=list)

    @property
    def is_bound(self) -> bool:
        """True if parameter has a binding (not UNBOUND)."""
        return self.binding_type != BindingType.UNBOUND

    @property
    def is_literal(self) -> bool:
        """True if bound to a literal constant."""
        return self.binding_type == BindingType.LITERAL

    @property
    def is_expression(self) -> bool:
        """True if bound to an arithmetic expression."""
        return self.binding_type == BindingType.EXPRESSION


class CalcUsageInfo(BaseModel):
    """Information about a CalculationUsage element.

    Captures the essential data about a calc instance for validation.

    Attributes:
        instance_name: Instance name (e.g., "net_electric")
        calc_def_name: Definition name (e.g., "NetElectricPower")
        bindings: List of parameter bindings
        source_file: Path to source file
        source_line: Line number in source
        parent_part: Name of containing part

    Note: unbound_params is a computed property, not a stored field.

    Example:
        >>> usage = CalcUsageInfo(
        ...     instance_name="net_electric",
        ...     calc_def_name="NetElectricPower",
        ...     bindings=[...],
        ...     source_file="physics.sysml",
        ...     source_line=42
        ... )
        >>> usage.unbound_params  # Computed from bindings
        ['efficiency']
    """

    instance_name: str
    calc_def_name: str
    bindings: list[BindingInfo] = Field(default_factory=list)
    source_file: str = ""
    source_line: int = 0
    parent_part: str = ""

    @property
    def location(self) -> str:
        """Get file:line location string."""
        if self.source_file:
            return f"{self.source_file}:{self.source_line}"
        return "<unknown>"

    @property
    def unbound_params(self) -> list[str]:
        """Parameters with no binding (derived from bindings list)."""
        return [b.param_name for b in self.bindings if b.binding_type == BindingType.UNBOUND]

    @property
    def has_cross_file_bindings(self) -> bool:
        """True if any binding references another file."""
        return any(b.is_cross_file for b in self.bindings)

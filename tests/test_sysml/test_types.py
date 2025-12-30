"""Tests for sysml_utils type definitions.

These tests document the expected behavior of all dataclasses and enums.
"""


def test_package_imports():
    """Verify sysml_utils package is importable.

    Input: Import statement
    Output: No ImportError raised
    """
    from agentic_mbse.sysml import types

    assert types is not None


# Phase 2: Core Enums


def test_binding_type_values():
    """BindingType enum has all expected values.

    Input: BindingType enum
    Output: Five distinct values for binding classification
    """
    from agentic_mbse.sysml.types import BindingType

    assert BindingType.CHAIN.value == "chain"
    assert BindingType.REFERENCE.value == "reference"
    assert BindingType.LITERAL.value == "literal"
    assert BindingType.EXPRESSION.value == "expression"
    assert BindingType.UNBOUND.value == "unbound"


def test_validation_code_is_string_enum():
    """ValidationCode enum values are strings for JSON serialization.

    Input: ValidationCode enum
    Output: String values that can be used directly in JSON
    """
    from agentic_mbse.sysml.types import ValidationCode

    assert ValidationCode.V1_CALC_DEF_LOCATION == "V1_CALC_DEF_LOCATION"
    assert ValidationCode.UNBOUND_INPUT == "UNBOUND_INPUT"
    # Can be used as dict key
    assert {ValidationCode.V1_CALC_DEF_LOCATION: "test"}[ValidationCode.V1_CALC_DEF_LOCATION] == "test"


def test_severity_values():
    """Severity enum has ERROR, WARNING, INFO values.

    Input: Severity enum
    Output: Three severity levels
    """
    from agentic_mbse.sysml.types import Severity

    assert Severity.ERROR.value == "error"
    assert Severity.WARNING.value == "warning"
    assert Severity.INFO.value == "info"


# Phase 3: Simple Dataclasses


def test_expression_ref_basic():
    """ExpressionRef captures attribute reference info.

    Input: ExpressionRef with name and qualified_name
    Output: Fields are accessible
    """
    from agentic_mbse.sysml.types import ExpressionRef

    ref = ExpressionRef(
        name="volume",
        qualified_name="CATFMFERadialBuild::plasma_region::volume",
        document_path="models/designs/catf_mfe/radial_build.sysml",
    )
    assert ref.name == "volume"
    assert ref.qualified_name == "CATFMFERadialBuild::plasma_region::volume"
    assert ref.document_path == "models/designs/catf_mfe/radial_build.sysml"


def test_expression_ref_element_excluded_from_serialization():
    """ExpressionRef.element is excluded from JSON/dict serialization.

    Input: ExpressionRef with element set
    Output: element not in model_dump() output
    """
    from agentic_mbse.sysml.types import ExpressionRef

    ref = ExpressionRef(name="test", element=object())
    dump = ref.model_dump()
    assert "element" not in dump


def test_validation_issue_str_format():
    """ValidationIssue formats correctly as string.

    Input: ValidationIssue with level, severity, message, location
    Output: Human-readable string with prefix and location
    """
    from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue

    error = ValidationIssue(
        level=2,
        severity=Severity.ERROR,
        code=ValidationCode.UNBOUND_INPUT,
        message="Input 'p_fusion' has no binding",
        location="physics.sysml:42",
    )
    assert str(error) == "ERROR: Input 'p_fusion' has no binding at physics.sysml:42"


def test_validation_issue_with_suggestion():
    """ValidationIssue can include fix suggestion.

    Input: ValidationIssue with suggestion
    Output: suggestion field is accessible
    """
    from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue

    issue = ValidationIssue(
        level=2,
        severity=Severity.ERROR,
        code=ValidationCode.V1_CALC_DEF_LOCATION,
        message="Calc def in designs/",
        suggestion="Move to library/",
    )
    assert issue.suggestion == "Move to library/"


# Phase 4: Complex Dataclasses


def test_binding_info_is_bound_property():
    """BindingInfo.is_bound returns True for all types except UNBOUND.

    Input: BindingInfo with each BindingType
    Output: is_bound=True for CHAIN/REFERENCE/LITERAL/EXPRESSION, False for UNBOUND
    """
    from agentic_mbse.sysml.types import BindingInfo, BindingType

    bound_chain = BindingInfo(param_name="x", binding_type=BindingType.CHAIN)
    bound_literal = BindingInfo(param_name="x", binding_type=BindingType.LITERAL)
    bound_expr = BindingInfo(param_name="x", binding_type=BindingType.EXPRESSION)
    unbound = BindingInfo(param_name="x", binding_type=BindingType.UNBOUND)

    assert bound_chain.is_bound is True
    assert bound_literal.is_bound is True
    assert bound_expr.is_bound is True
    assert unbound.is_bound is False


def test_binding_info_literal_value_extraction():
    """BindingInfo stores parsed literal values.

    Input: BindingInfo with LITERAL type and literal_value
    Output: literal_value is accessible and correctly typed
    """
    from agentic_mbse.sysml.types import BindingInfo, BindingType

    float_binding = BindingInfo(
        param_name="efficiency",
        binding_type=BindingType.LITERAL,
        literal_value=0.95,
    )
    assert float_binding.is_literal is True
    assert float_binding.literal_value == 0.95


def test_binding_info_expression_with_references():
    """BindingInfo captures references for EXPRESSION bindings.

    Input: BindingInfo with EXPRESSION type and references list
    Output: references are accessible
    """
    from agentic_mbse.sysml.types import BindingInfo, BindingType, ExpressionRef

    ref_a = ExpressionRef(name="a", qualified_name="Part::a")
    ref_b = ExpressionRef(name="b", qualified_name="Part::b")

    expr_binding = BindingInfo(
        param_name="result",
        binding_type=BindingType.EXPRESSION,
        references=[ref_a, ref_b],
    )

    assert expr_binding.is_expression is True
    assert len(expr_binding.references) == 2
    assert expr_binding.references[0].name == "a"


def test_calc_usage_info_location_property():
    """CalcUsageInfo.location combines file and line.

    Input: CalcUsageInfo with source_file and source_line
    Output: Formatted "file:line" string
    """
    from agentic_mbse.sysml.types import CalcUsageInfo

    usage = CalcUsageInfo(
        instance_name="net_electric",
        calc_def_name="NetElectricPower",
        source_file="physics.sysml",
        source_line=42,
    )
    assert usage.location == "physics.sysml:42"


def test_calc_usage_info_unbound_params_computed():
    """CalcUsageInfo.unbound_params is computed from bindings.

    Input: CalcUsageInfo with mixed bound/unbound bindings
    Output: unbound_params contains only UNBOUND param names
    """
    from agentic_mbse.sysml.types import BindingInfo, BindingType, CalcUsageInfo

    bindings = [
        BindingInfo(param_name="a", binding_type=BindingType.CHAIN),
        BindingInfo(param_name="b", binding_type=BindingType.UNBOUND),
        BindingInfo(param_name="c", binding_type=BindingType.LITERAL),
        BindingInfo(param_name="d", binding_type=BindingType.UNBOUND),
    ]
    usage = CalcUsageInfo(
        instance_name="test",
        calc_def_name="TestCalc",
        bindings=bindings,
    )
    assert usage.unbound_params == ["b", "d"]


def test_calc_usage_info_empty_bindings():
    """CalcUsageInfo.unbound_params returns empty list when no bindings.

    Input: CalcUsageInfo with no bindings
    Output: Empty unbound_params list
    """
    from agentic_mbse.sysml.types import CalcUsageInfo

    usage = CalcUsageInfo(
        instance_name="test",
        calc_def_name="TestCalc",
        bindings=[],
    )
    assert usage.unbound_params == []


def test_calc_usage_info_has_cross_file_bindings():
    """CalcUsageInfo.has_cross_file_bindings detects cross-file refs.

    Input: CalcUsageInfo with one cross-file binding
    Output: has_cross_file_bindings returns True
    """
    from agentic_mbse.sysml.types import BindingInfo, BindingType, CalcUsageInfo

    bindings = [
        BindingInfo(param_name="a", binding_type=BindingType.CHAIN, is_cross_file=False),
        BindingInfo(param_name="b", binding_type=BindingType.CHAIN, is_cross_file=True),
    ]
    usage = CalcUsageInfo(
        instance_name="test",
        calc_def_name="TestCalc",
        bindings=bindings,
    )
    assert usage.has_cross_file_bindings is True

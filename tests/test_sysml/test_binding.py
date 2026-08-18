"""Tests for binding analysis utilities.

These tests document how binding extraction works with calc usages.
"""

from agentic_mbse.sysml.binding import classify_binding, extract_bindings
from agentic_mbse.sysml.types import BindingType
from tests.test_sysml.conftest import (
    MockCalculationUsage,
    MockFeatureChainExpression,
    MockFeatureReferenceExpression,
    MockLiteralInteger,
    MockLiteralRational,
    MockMember,
    MockOperatorExpression,
    create_mock_calc_usage_with_chain_binding,
    create_mock_calc_usage_with_cross_file_binding,
    create_mock_calc_usage_with_expression_binding,
    create_mock_calc_usage_with_literal_binding,
    create_mock_calc_usage_with_no_binding,
)


def test_mock_calc_usage_fixtures_exist():
    """Verify all mock calc usage factories are available.

    Input: Factory functions from conftest.py
    Output: Factories create valid mock calc usages
    """
    # Chain binding
    usage = create_mock_calc_usage_with_chain_binding(
        param_name="p_fusion",
        source_instance="catf_physics",
        source_attr="p_fusion",
    )
    assert usage.name == "test_calc"
    assert len(usage.owned_members) == 1
    assert usage.owned_members[0].name == "p_fusion"

    # Literal binding
    usage = create_mock_calc_usage_with_literal_binding(
        param_name="efficiency",
        value=0.95,
    )
    assert usage.owned_members[0].feature_value_expression.value == 0.95

    # No binding
    usage = create_mock_calc_usage_with_no_binding(param_name="x")
    assert usage.owned_members[0].feature_value_expression is None


def test_mock_calc_usage_has_document():
    """Mock calc usages have document URL for cross-file detection.

    Input: Mock calc usage with doc_path
    Output: document.url is accessible
    """
    usage = create_mock_calc_usage_with_chain_binding(
        param_name="x",
        source_instance="inst",
        source_attr="attr",
        usage_file="physics.sysml",
    )
    assert hasattr(usage, "document")
    assert usage.document.url == "physics.sysml"


def test_mock_calc_usage_cross_file_binding():
    """Cross-file binding factory creates proper document references.

    Input: Mock calc usage with different usage_file and source_file
    Output: document URLs differ appropriately
    """
    usage = create_mock_calc_usage_with_cross_file_binding(
        param_name="p_coils",
        usage_file="physics.sysml",
        source_file="magnets.sysml",
    )
    assert usage.document.url == "physics.sysml"
    # The expression's target should have the source file
    expr = usage.owned_members[0].feature_value_expression
    assert expr.memberships[0].member_element.document.url == "magnets.sysml"


# classify_binding() tests


def test_classify_binding_chain_type():
    """classify_binding returns CHAIN for FeatureChainExpression.

    Input: FeatureChainExpression like `instance.attribute`
    Output: BindingType.CHAIN
    """
    expr = MockFeatureChainExpression(instance_name="inst", attr_name="attr")
    assert classify_binding(expr) == BindingType.CHAIN


def test_classify_binding_reference_type():
    """classify_binding returns REFERENCE for FeatureReferenceExpression.

    Input: FeatureReferenceExpression like `simple_name`
    Output: BindingType.REFERENCE
    """
    expr = MockFeatureReferenceExpression(name="x")
    assert classify_binding(expr) == BindingType.REFERENCE


def test_classify_binding_literal_type():
    """classify_binding returns LITERAL for literal expressions.

    Input: LiteralRational like `42.0`
    Output: BindingType.LITERAL
    """
    expr = MockLiteralRational(value=42.0)
    assert classify_binding(expr) == BindingType.LITERAL


def test_classify_binding_expression_type():
    """classify_binding returns EXPRESSION for OperatorExpression.

    Input: OperatorExpression like `a + b`
    Output: BindingType.EXPRESSION
    """
    expr = MockOperatorExpression(
        "+",
        [
            MockFeatureReferenceExpression(name="a"),
            MockFeatureReferenceExpression(name="b"),
        ],
    )
    assert classify_binding(expr) == BindingType.EXPRESSION


def test_classify_binding_unbound_for_none():
    """classify_binding returns UNBOUND for None.

    Input: None (no binding)
    Output: BindingType.UNBOUND
    """
    assert classify_binding(None) == BindingType.UNBOUND


def test_classify_binding_literal_integer():
    """classify_binding returns LITERAL for integer literals.

    Input: LiteralInteger like `42`
    Output: BindingType.LITERAL
    """
    expr = MockLiteralInteger(value=42)
    assert classify_binding(expr) == BindingType.LITERAL


# extract_bindings() tests


def test_extract_bindings_chain_type():
    """extract_bindings correctly identifies CHAIN bindings.

    Input: CalcUsage with binding `in p_fusion = catf_physics.p_fusion`
    Output: BindingInfo with type=CHAIN, source_path="catf_physics.p_fusion"
    """
    mock_usage = create_mock_calc_usage_with_chain_binding(
        param_name="p_fusion",
        source_instance="catf_physics",
        source_attr="p_fusion",
    )

    bindings = extract_bindings(mock_usage)

    assert len(bindings) == 1
    assert bindings[0].param_name == "p_fusion"
    assert bindings[0].binding_type == BindingType.CHAIN
    assert bindings[0].source_path == "catf_physics.p_fusion"


def test_extract_bindings_literal_type():
    """extract_bindings correctly identifies LITERAL bindings.

    Input: CalcUsage with binding `in p_neutron = 2079.41`
    Output: BindingInfo with type=LITERAL, literal_value=2079.41
    """
    mock_usage = create_mock_calc_usage_with_literal_binding(
        param_name="p_neutron",
        value=2079.41,
    )

    bindings = extract_bindings(mock_usage)

    assert len(bindings) == 1
    assert bindings[0].param_name == "p_neutron"
    assert bindings[0].binding_type == BindingType.LITERAL
    assert bindings[0].literal_value == 2079.41


def test_extract_bindings_expression_type():
    """extract_bindings correctly identifies EXPRESSION bindings.

    Input: CalcUsage with binding `in volume = a + b`
    Output: BindingInfo with type=EXPRESSION, references=[a, b]
    """
    mock_usage = create_mock_calc_usage_with_expression_binding(
        param_name="volume",
        refs=["a", "b"],
    )

    bindings = extract_bindings(mock_usage)

    assert len(bindings) == 1
    assert bindings[0].param_name == "volume"
    assert bindings[0].binding_type == BindingType.EXPRESSION
    assert len(bindings[0].reference_uses) == 2


def test_extract_bindings_unbound_parameter():
    """extract_bindings returns UNBOUND for missing bindings.

    Input: CalcUsage where input 'efficiency' has no binding
    Output: BindingInfo with type=UNBOUND
    """
    mock_usage = create_mock_calc_usage_with_no_binding(param_name="efficiency")

    bindings = extract_bindings(mock_usage)

    assert len(bindings) == 1
    assert bindings[0].param_name == "efficiency"
    assert bindings[0].binding_type == BindingType.UNBOUND
    assert bindings[0].is_bound is False


def test_extract_bindings_cross_file_detection():
    """extract_bindings detects cross-file references.

    Input: CalcUsage in physics.sysml bound to element in magnets.sysml
    Output: BindingInfo with is_cross_file=True
    """
    mock_usage = create_mock_calc_usage_with_cross_file_binding(
        param_name="p_coils",
        usage_file="physics.sysml",
        source_file="magnets.sysml",
    )

    bindings = extract_bindings(mock_usage)

    assert len(bindings) == 1
    assert bindings[0].is_cross_file is True


def test_extract_bindings_same_file_detection():
    """extract_bindings returns is_cross_file=False for same-file refs.

    Input: CalcUsage and source both in physics.sysml
    Output: BindingInfo with is_cross_file=False
    """
    mock_usage = create_mock_calc_usage_with_chain_binding(
        param_name="p_coils",
        source_instance="local_part",
        source_attr="value",
        usage_file="physics.sysml",
    )

    bindings = extract_bindings(mock_usage)

    assert len(bindings) == 1
    assert bindings[0].is_cross_file is False


def test_extract_bindings_preserves_expression_ast():
    """extract_bindings preserves expression AST for EXPRESSION bindings.

    Input: CalcUsage with expression binding
    Output: BindingInfo with expression_ast populated
    """
    mock_usage = create_mock_calc_usage_with_expression_binding(
        param_name="result",
        refs=["a", "b"],
    )

    bindings = extract_bindings(mock_usage)

    assert bindings[0].binding_type == BindingType.EXPRESSION
    assert bindings[0].expression_ast is not None


def test_extract_bindings_multiple_params():
    """extract_bindings handles calc with multiple parameters.

    Input: CalcUsage with 3 parameters (bound, literal, unbound)
    Output: 3 BindingInfo objects with correct types
    """
    members = [
        MockMember(
            name="p_fusion",
            feature_value_expression=MockFeatureChainExpression("inst", "val"),
        ),
        MockMember(
            name="efficiency",
            feature_value_expression=MockLiteralRational(0.95),
        ),
        MockMember(
            name="scaling",
            feature_value_expression=None,
        ),
    ]
    mock_usage = MockCalculationUsage(
        name="test_calc",
        calc_def_name="TestCalcDef",
        doc_path="physics.sysml",
        owned_members=members,
    )

    bindings = extract_bindings(mock_usage)

    assert len(bindings) == 3
    assert bindings[0].binding_type == BindingType.CHAIN
    assert bindings[1].binding_type == BindingType.LITERAL
    assert bindings[2].binding_type == BindingType.UNBOUND

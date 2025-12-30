"""Tests for expression traversal utilities.

These tests document how expression traversal works with different
expression tree structures.
"""

from agentic_mbse.sysml.expression import (
    extract_feature_refs,
    extract_operators,
    is_literal_expression,
    is_true_static_expression,
    traverse_expression,
)
from tests.test_sysml.conftest import (
    MockFeatureChainExpression,
    MockFeatureReferenceExpression,
    MockLiteralInteger,
    MockLiteralRational,
    MockOperatorExpression,
)


def test_mock_fixtures_exist(mock_feature_ref, mock_operator_expr, mock_literal):
    """Verify all mock fixtures are available.

    Input: pytest fixtures from conftest.py
    Output: Fixtures are callable factories
    """
    # Verify fixtures return callable factories
    ref = mock_feature_ref("volume")
    assert ref.name == "volume"

    lit = mock_literal(42.0)
    assert lit.value == 42.0

    op = mock_operator_expr("+", [ref, lit])
    assert op.operator == "+"
    assert len(op.operands) == 2


def test_mock_isinstance_method():
    """Mock elements support isinstance method for syside compatibility.

    Input: MockFeatureReferenceExpression
    Output: isinstance method correctly identifies type
    """
    ref = MockFeatureReferenceExpression(name="test")
    op = MockOperatorExpression("+", [])

    # isinstance method should work (syside pattern)
    assert ref.isinstance(MockFeatureReferenceExpression)
    assert not ref.isinstance(MockOperatorExpression)
    assert op.isinstance(MockOperatorExpression)


# Phase 2: traverse_expression() tests


def test_traverse_expression_none_input():
    """traverse_expression returns empty list for None input.

    Input: None
    Output: Empty list (graceful handling)
    """
    results = traverse_expression(None, lambda node: node)
    assert results == []


def test_traverse_expression_feature_ref():
    """traverse_expression visits FeatureReferenceExpression nodes.

    Input: Simple FeatureReferenceExpression pointing to attribute "volume"
    Output: Visitor is called with the expression, returns result
    """
    mock_expr = MockFeatureReferenceExpression(name="volume")

    results = traverse_expression(
        mock_expr, lambda node: node.name if hasattr(node, "name") and node.name else None
    )

    assert results == ["volume"]


def test_traverse_expression_operator_with_two_refs():
    """traverse_expression recursively visits all operands.

    Input: OperatorExpression: a + b
    Output: Both operand names are visited and returned
    """
    mock_a = MockFeatureReferenceExpression(name="a")
    mock_b = MockFeatureReferenceExpression(name="b")
    mock_expr = MockOperatorExpression(operator="+", operands=[mock_a, mock_b])

    results = traverse_expression(
        mock_expr, lambda node: node.name if hasattr(node, "name") and node.name else None
    )

    assert set(results) == {"a", "b"}


def test_traverse_expression_nested_operators():
    """traverse_expression handles nested operator expressions.

    Input: OperatorExpression: (a + b) * c
    Output: All three operand names are visited
    """
    mock_a = MockFeatureReferenceExpression(name="a")
    mock_b = MockFeatureReferenceExpression(name="b")
    mock_c = MockFeatureReferenceExpression(name="c")
    mock_inner = MockOperatorExpression(operator="+", operands=[mock_a, mock_b])
    mock_outer = MockOperatorExpression(operator="*", operands=[mock_inner, mock_c])

    results = traverse_expression(
        mock_outer,
        lambda node: node.name if hasattr(node, "name") and node.name else None,
    )

    assert set(results) == {"a", "b", "c"}


def test_traverse_expression_with_literal():
    """traverse_expression handles literal nodes correctly.

    Input: OperatorExpression: a + 2.0
    Output: Only the feature reference name is returned (visitor returns None for literals)
    """
    mock_a = MockFeatureReferenceExpression(name="a")
    mock_lit = MockLiteralRational(value=2.0)
    mock_expr = MockOperatorExpression(operator="+", operands=[mock_a, mock_lit])

    results = traverse_expression(
        mock_expr, lambda node: node.name if hasattr(node, "name") and node.name else None
    )

    assert results == ["a"]


def test_traverse_expression_max_depth_protection():
    """traverse_expression respects max_depth to prevent infinite recursion.

    Input: Expression tree deeper than max_depth
    Output: Traversal stops at max_depth, returns partial results
    """
    # Create deeply nested structure
    current = MockOperatorExpression("+", [])
    for _ in range(10):
        current = MockOperatorExpression("+", [current])

    # Should not raise RecursionError with max_depth protection
    results = traverse_expression(current, lambda n: 1, max_depth=5)
    # Should have stopped early
    assert len(results) <= 5


# Phase 3: Helper function tests


def test_extract_feature_refs_returns_expression_ref_list():
    """extract_feature_refs returns list of ExpressionRef objects.

    Input: Expression with two attribute references
    Output: List[ExpressionRef] with name and qualified_name
    """
    mock_expr = MockOperatorExpression(
        operator="+",
        operands=[
            MockFeatureReferenceExpression(name="volume", qualified_name="Part::volume"),
            MockFeatureReferenceExpression(name="area", qualified_name="Part::area"),
        ],
    )

    refs = extract_feature_refs(mock_expr)

    assert len(refs) == 2
    assert refs[0].name == "volume"
    assert refs[0].qualified_name == "Part::volume"
    assert refs[1].name == "area"


def test_extract_feature_refs_empty_for_literal():
    """extract_feature_refs returns empty list for pure literals.

    Input: LiteralRational expression
    Output: Empty list (no references)
    """
    mock_expr = MockLiteralRational(value=42.0)
    refs = extract_feature_refs(mock_expr)
    assert refs == []


def test_extract_feature_refs_none_input():
    """extract_feature_refs returns empty list for None.

    Input: None
    Output: Empty list (graceful handling)
    """
    refs = extract_feature_refs(None)
    assert refs == []


def test_extract_feature_refs_from_chain():
    """extract_feature_refs extracts target from chain expressions.

    Input: FeatureChainExpression like instance.attribute
    Output: ExpressionRef for the attribute
    """
    mock_expr = MockFeatureChainExpression(instance_name="catf_physics", attr_name="p_fusion")

    refs = extract_feature_refs(mock_expr)

    assert len(refs) >= 1
    # The chain should resolve to the attribute
    assert any(ref.name == "p_fusion" for ref in refs)


def test_extract_operators_returns_operator_list():
    """extract_operators returns all operators in expression.

    Input: Expression with multiple operators: a + b * c
    Output: List of operator strings ["+", "*"]
    """
    mock_a = MockFeatureReferenceExpression(name="a")
    mock_b = MockFeatureReferenceExpression(name="b")
    mock_c = MockFeatureReferenceExpression(name="c")
    mock_mult = MockOperatorExpression(operator="*", operands=[mock_b, mock_c])
    mock_add = MockOperatorExpression(operator="+", operands=[mock_a, mock_mult])

    operators = extract_operators(mock_add)

    assert set(operators) == {"+", "*"}


def test_extract_operators_empty_for_literal():
    """extract_operators returns empty list for literals.

    Input: LiteralRational
    Output: Empty list
    """
    operators = extract_operators(MockLiteralRational(42.0))
    assert operators == []


def test_is_literal_expression_true_for_pure_literal():
    """is_literal_expression returns True for literal constants.

    Input: LiteralRational expression
    Output: True (no feature references)
    """
    mock_expr = MockLiteralRational(value=42.0)
    assert is_literal_expression(mock_expr) is True


def test_is_literal_expression_false_for_ref():
    """is_literal_expression returns False when refs exist.

    Input: FeatureReferenceExpression
    Output: False (has feature reference)
    """
    mock_expr = MockFeatureReferenceExpression(name="volume")
    assert is_literal_expression(mock_expr) is False


def test_is_literal_expression_false_for_expr_with_refs():
    """is_literal_expression returns False for expression containing refs.

    Input: OperatorExpression with ref operands
    Output: False (has feature references internally)
    """
    mock_a = MockFeatureReferenceExpression(name="a")
    mock_literal = MockLiteralRational(value=2.0)
    mock_expr = MockOperatorExpression(operator="*", operands=[mock_a, mock_literal])

    assert is_literal_expression(mock_expr) is False


def test_is_literal_expression_true_for_literal_arithmetic():
    """is_literal_expression returns True for pure literal arithmetic.

    Input: OperatorExpression with only literal operands: 2 + 3
    Output: True (no feature references)
    """
    mock_2 = MockLiteralRational(value=2.0)
    mock_3 = MockLiteralRational(value=3.0)
    mock_expr = MockOperatorExpression(operator="+", operands=[mock_2, mock_3])

    assert is_literal_expression(mock_expr) is True


# Phase 4: Standard Library Filter tests (ADR-002 Amendment)


class TestStandardLibraryFilter:
    """extract_feature_refs() should filter standard library references.

    Standard library references (SI::, ISQ::, ScalarValues::, UnitsAndScales::)
    are filtered by default to avoid flagging unit annotations like `3.0 [m]`
    as derived expressions.
    """

    def test_filter_si_units(self):
        """SI:: references (metre, kilogram, etc.) should be filtered by default.

        Input: FeatureReferenceExpression with qualified_name="SI::metre"
        Output: Empty list with default filtering; 1 ref when filter disabled
        """
        mock_expr = MockFeatureReferenceExpression(
            name="metre", qualified_name="SI::metre"
        )

        # Default behavior filters SI::
        refs = extract_feature_refs(mock_expr)
        assert len(refs) == 0, "SI::metre should be filtered by default"

        # Explicit include shows the ref
        refs_all = extract_feature_refs(mock_expr, ignore_std_lib=False)
        assert len(refs_all) == 1
        assert refs_all[0].qualified_name == "SI::metre"

    def test_filter_isq_quantities(self):
        """ISQ:: references (Length, Mass, etc.) should be filtered.

        Input: FeatureReferenceExpression with qualified_name="ISQ::Length"
        Output: Empty list when filtered
        """
        mock_expr = MockFeatureReferenceExpression(
            name="Length", qualified_name="ISQ::Length"
        )

        refs = extract_feature_refs(mock_expr)
        assert len(refs) == 0, "ISQ::Length should be filtered by default"

        refs_all = extract_feature_refs(mock_expr, ignore_std_lib=False)
        assert len(refs_all) == 1

    def test_filter_scalar_values(self):
        """ScalarValues:: references should be filtered.

        Input: FeatureReferenceExpression with qualified_name="ScalarValues::Real"
        Output: Empty list when filtered
        """
        mock_expr = MockFeatureReferenceExpression(
            name="Real", qualified_name="ScalarValues::Real"
        )

        refs = extract_feature_refs(mock_expr)
        assert len(refs) == 0, "ScalarValues::Real should be filtered by default"

    def test_filter_units_and_scales(self):
        """UnitsAndScales:: references should be filtered.

        Input: FeatureReferenceExpression with qualified_name="UnitsAndScales::UnitFactor"
        Output: Empty list when filtered
        """
        mock_expr = MockFeatureReferenceExpression(
            name="UnitFactor", qualified_name="UnitsAndScales::UnitFactor"
        )

        refs = extract_feature_refs(mock_expr)
        assert len(refs) == 0, "UnitsAndScales:: should be filtered by default"

    def test_preserve_design_refs(self):
        """Design attribute references should NOT be filtered.

        Input: FeatureReferenceExpression with qualified_name="RadialBuild::major_radius"
        Output: 1 reference (design attributes preserved)
        """
        mock_expr = MockFeatureReferenceExpression(
            name="major_radius", qualified_name="RadialBuild::major_radius"
        )

        refs = extract_feature_refs(mock_expr)
        assert len(refs) == 1, "Design refs should NOT be filtered"
        assert refs[0].name == "major_radius"

    def test_mixed_refs_partial_filter(self):
        """Expression with both std lib and design refs filters correctly.

        Input: OperatorExpression with SI::metre and RadialBuild::radius
        Output: Only RadialBuild::radius returned (SI::metre filtered)
        """
        mock_unit = MockFeatureReferenceExpression(
            name="metre", qualified_name="SI::metre"
        )
        mock_design = MockFeatureReferenceExpression(
            name="radius", qualified_name="RadialBuild::radius"
        )
        mock_literal = MockLiteralRational(value=3.0)

        # Expression: 3.0 [m] + radius - represents `3.0 [m] + radius`
        mock_expr = MockOperatorExpression(
            operator="+",
            operands=[
                MockOperatorExpression(operator="[", operands=[mock_literal, mock_unit]),
                mock_design,
            ],
        )

        refs = extract_feature_refs(mock_expr)
        assert len(refs) == 1, "Only design ref should remain after filtering"
        assert refs[0].name == "radius"

    def test_disable_filter_flag(self):
        """ignore_std_lib=False should return all refs including std lib.

        Input: Expression with SI::metre reference
        Output: 1 reference when filter disabled
        """
        mock_expr = MockFeatureReferenceExpression(
            name="metre", qualified_name="SI::metre"
        )

        # With filter disabled, std lib refs are included
        refs = extract_feature_refs(mock_expr, ignore_std_lib=False)
        assert len(refs) == 1
        assert refs[0].name == "metre"
        assert "SI::" in refs[0].qualified_name

    def test_unit_annotation_expression(self):
        """Unit annotation `3.0 [m]` structure should result in empty refs.

        Input: OperatorExpression simulating `3.0 [m]` (literal with unit)
        Output: Empty list (unit ref filtered, literal has no refs)
        """
        # SysML AST structure for `3.0 [m]` is:
        # OperatorExpression (operator='[')
        #   operand[0]: LiteralRational (3.0)
        #   operand[1]: FeatureReferenceExpression → SI::metre
        mock_literal = MockLiteralRational(value=3.0)
        mock_unit = MockFeatureReferenceExpression(
            name="metre", qualified_name="SI::metre"
        )
        mock_expr = MockOperatorExpression(
            operator="[", operands=[mock_literal, mock_unit]
        )

        refs = extract_feature_refs(mock_expr)
        assert len(refs) == 0, "Unit annotation should yield zero refs after filtering"

    def test_empty_qualified_name_not_filtered(self):
        """Refs with empty qualified_name should NOT be filtered.

        Input: FeatureReferenceExpression with name but no qualified_name
        Output: 1 reference (not filtered - can't determine if std lib)
        """
        mock_expr = MockFeatureReferenceExpression(name="some_attr", qualified_name="")

        refs = extract_feature_refs(mock_expr)
        assert len(refs) == 1, "Refs without qualified_name should not be filtered"


# Phase 5: is_true_static_expression() tests (ADR-002 semantic helper)


class TestIsTrueStaticExpression:
    """is_true_static_expression() semantic helper for ADR-002.

    Tests the function that determines if an expression is "true static"
    per ADR-002 rules: contains only literals and standard library refs,
    no design attribute references.
    """

    def test_pure_literal_is_true_static(self):
        """Pure literal value is true static.

        Input: LiteralRational expression (42.0)
        Output: True (no design refs)
        """
        mock_expr = MockLiteralRational(value=42.0)
        assert is_true_static_expression(mock_expr) is True

    def test_literal_arithmetic_is_true_static(self):
        """Arithmetic with only literals is true static.

        Input: OperatorExpression: 3.14159 * 3.14159
        Output: True (no design refs)
        """
        mock_pi = MockLiteralRational(value=3.14159)
        mock_pi2 = MockLiteralRational(value=3.14159)
        mock_expr = MockOperatorExpression(operator="*", operands=[mock_pi, mock_pi2])

        assert is_true_static_expression(mock_expr) is True

    def test_unit_annotation_is_true_static(self):
        """Unit annotation like `3.0 [m]` is true static.

        Input: OperatorExpression simulating `3.0 [m]`
        Output: True (SI::metre is filtered, only literal remains)
        """
        mock_literal = MockLiteralRational(value=3.0)
        mock_unit = MockFeatureReferenceExpression(
            name="metre", qualified_name="SI::metre"
        )
        mock_expr = MockOperatorExpression(
            operator="[", operands=[mock_literal, mock_unit]
        )

        assert is_true_static_expression(mock_expr) is True

    def test_single_design_ref_not_true_static(self):
        """Single design attribute reference is NOT true static.

        Input: FeatureReferenceExpression to design attribute
        Output: False (has design ref)
        """
        mock_expr = MockFeatureReferenceExpression(
            name="major_radius", qualified_name="RadialBuild::major_radius"
        )

        assert is_true_static_expression(mock_expr) is False

    def test_derived_expression_not_true_static(self):
        """Derived expression (design ref in arithmetic) is NOT true static.

        Input: OperatorExpression: radius * 2.0
        Output: False (has design ref)
        """
        mock_radius = MockFeatureReferenceExpression(
            name="radius", qualified_name="RadialBuild::radius"
        )
        mock_two = MockLiteralRational(value=2.0)
        mock_expr = MockOperatorExpression(operator="*", operands=[mock_radius, mock_two])

        assert is_true_static_expression(mock_expr) is False

    def test_none_input_is_true_static(self):
        """None expression is considered true static.

        Input: None
        Output: True (no expression = no design refs)
        """
        assert is_true_static_expression(None) is True

    def test_complex_true_static_with_units(self):
        """Complex expression with multiple units is true static.

        Input: OperatorExpression: 3.0 [m] + 2.0 [m]
        Output: True (all refs are SI:: which are filtered)
        """
        mock_lit1 = MockLiteralRational(value=3.0)
        mock_unit1 = MockFeatureReferenceExpression(
            name="metre", qualified_name="SI::metre"
        )
        mock_unit_expr1 = MockOperatorExpression(
            operator="[", operands=[mock_lit1, mock_unit1]
        )

        mock_lit2 = MockLiteralRational(value=2.0)
        mock_unit2 = MockFeatureReferenceExpression(
            name="metre", qualified_name="SI::metre"
        )
        mock_unit_expr2 = MockOperatorExpression(
            operator="[", operands=[mock_lit2, mock_unit2]
        )

        mock_expr = MockOperatorExpression(
            operator="+", operands=[mock_unit_expr1, mock_unit_expr2]
        )

        assert is_true_static_expression(mock_expr) is True

    def test_mixed_static_and_design_ref_not_true_static(self):
        """Expression mixing units and design ref is NOT true static.

        Input: OperatorExpression: 3.0 [m] + major_radius
        Output: False (major_radius is a design ref)
        """
        mock_lit = MockLiteralRational(value=3.0)
        mock_unit = MockFeatureReferenceExpression(
            name="metre", qualified_name="SI::metre"
        )
        mock_unit_expr = MockOperatorExpression(
            operator="[", operands=[mock_lit, mock_unit]
        )

        mock_design = MockFeatureReferenceExpression(
            name="major_radius", qualified_name="RadialBuild::major_radius"
        )

        mock_expr = MockOperatorExpression(
            operator="+", operands=[mock_unit_expr, mock_design]
        )

        assert is_true_static_expression(mock_expr) is False


# Phase 6: Type Checking Utilities tests (ADR-002 Part 4)


class TestTypeCheckingUtilities:
    """Tests for type checking utility functions.

    These utilities support the static expression evaluator by providing
    consistent type checking for AST nodes.
    """

    def test_is_literal_type_rational(self):
        """LiteralRational should be detected as literal type.

        Input: MockLiteralRational
        Output: True
        """
        from agentic_mbse.sysml.expression import is_literal_type

        expr = MockLiteralRational(3.14)
        assert is_literal_type(expr) is True

    def test_is_literal_type_integer(self):
        """LiteralInteger should be detected as literal type.

        Input: MockLiteralInteger
        Output: True
        """
        from agentic_mbse.sysml.expression import is_literal_type

        expr = MockLiteralInteger(42)
        assert is_literal_type(expr) is True

    def test_is_literal_type_operator(self):
        """OperatorExpression should NOT be detected as literal type.

        Input: MockOperatorExpression
        Output: False
        """
        from agentic_mbse.sysml.expression import is_literal_type

        expr = MockOperatorExpression("+", [])
        assert is_literal_type(expr) is False

    def test_is_literal_type_feature_ref(self):
        """FeatureReferenceExpression should NOT be detected as literal type.

        Input: MockFeatureReferenceExpression
        Output: False
        """
        from agentic_mbse.sysml.expression import is_literal_type

        expr = MockFeatureReferenceExpression(name="radius")
        assert is_literal_type(expr) is False

    def test_is_reference_type_feature_ref(self):
        """FeatureReferenceExpression should be detected as reference type.

        Input: MockFeatureReferenceExpression
        Output: True
        """
        from agentic_mbse.sysml.expression import is_reference_type

        expr = MockFeatureReferenceExpression(name="radius")
        assert is_reference_type(expr) is True

    def test_is_reference_type_chain(self):
        """FeatureChainExpression should be detected as reference type.

        Input: MockFeatureChainExpression
        Output: True
        """
        from agentic_mbse.sysml.expression import is_reference_type

        expr = MockFeatureChainExpression(instance_name="calc", attr_name="output")
        assert is_reference_type(expr) is True

    def test_is_reference_type_literal(self):
        """LiteralRational should NOT be detected as reference type.

        Input: MockLiteralRational
        Output: False
        """
        from agentic_mbse.sysml.expression import is_reference_type

        expr = MockLiteralRational(3.0)
        assert is_reference_type(expr) is False

    def test_is_reference_type_operator(self):
        """OperatorExpression should NOT be detected as reference type.

        Input: MockOperatorExpression
        Output: False
        """
        from agentic_mbse.sysml.expression import is_reference_type

        expr = MockOperatorExpression("*", [])
        assert is_reference_type(expr) is False

    def test_get_reference_name_feature_ref(self):
        """get_reference_name extracts name from FeatureReferenceExpression.

        Input: MockFeatureReferenceExpression with name="radius"
        Output: "radius"
        """
        from agentic_mbse.sysml.expression import get_reference_name

        expr = MockFeatureReferenceExpression(name="radius")
        assert get_reference_name(expr) == "radius"

    def test_get_reference_name_chain(self):
        """get_reference_name extracts attribute name from FeatureChainExpression.

        Input: MockFeatureChainExpression with attr_name="output"
        Output: "output"
        """
        from agentic_mbse.sysml.expression import get_reference_name

        expr = MockFeatureChainExpression(instance_name="calc", attr_name="output")
        assert get_reference_name(expr) == "output"

    def test_get_reference_name_literal_returns_none(self):
        """get_reference_name returns None for non-reference types.

        Input: MockLiteralRational
        Output: None
        """
        from agentic_mbse.sysml.expression import get_reference_name

        expr = MockLiteralRational(3.0)
        assert get_reference_name(expr) is None

    def test_get_reference_name_operator_returns_none(self):
        """get_reference_name returns None for operator expressions.

        Input: MockOperatorExpression
        Output: None
        """
        from agentic_mbse.sysml.expression import get_reference_name

        expr = MockOperatorExpression("+", [])
        assert get_reference_name(expr) is None


# Phase 7: Static Expression Evaluator tests (ADR-002 Part 4)


class TestEvaluateTrueStaticExpression:
    """Tests for static expression evaluation.

    The evaluator handles true static expressions (literals + arithmetic)
    and raises errors for feature references or unsupported operators.
    """

    def test_literal_rational(self):
        """LiteralRational evaluates to its float value.

        Input: MockLiteralRational(3.14159)
        Output: 3.14159
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        expr = MockLiteralRational(3.14159)
        assert evaluate_true_static_expression(expr) == 3.14159

    def test_literal_integer(self):
        """LiteralInteger evaluates to float.

        Input: MockLiteralInteger(42)
        Output: 42.0
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        expr = MockLiteralInteger(42)
        assert evaluate_true_static_expression(expr) == 42.0

    def test_unit_annotation(self):
        """Unit annotation extracts numeric value, ignores unit.

        Input: 3.0 [m] (OperatorExpression with "[" operator)
        Output: 3.0
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        value = MockLiteralRational(3.0)
        unit = MockFeatureReferenceExpression(name="metre", qualified_name="SI::metre")
        expr = MockOperatorExpression("[", [value, unit])
        assert evaluate_true_static_expression(expr) == 3.0

    def test_binary_add(self):
        """Binary addition evaluates correctly.

        Input: 3.0 + 2.0
        Output: 5.0
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        left = MockLiteralRational(3.0)
        right = MockLiteralRational(2.0)
        expr = MockOperatorExpression("+", [left, right])
        assert evaluate_true_static_expression(expr) == 5.0

    def test_binary_subtract(self):
        """Binary subtraction evaluates correctly.

        Input: 5.0 - 2.0
        Output: 3.0
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        left = MockLiteralRational(5.0)
        right = MockLiteralRational(2.0)
        expr = MockOperatorExpression("-", [left, right])
        assert evaluate_true_static_expression(expr) == 3.0

    def test_binary_multiply(self):
        """Binary multiplication evaluates correctly.

        Input: 3.14159 * 2.0
        Output: ~6.28318
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        left = MockLiteralRational(3.14159)
        right = MockLiteralRational(2.0)
        expr = MockOperatorExpression("*", [left, right])
        assert abs(evaluate_true_static_expression(expr) - 6.28318) < 0.0001

    def test_binary_divide(self):
        """Binary division evaluates correctly.

        Input: 10.0 / 4.0
        Output: 2.5
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        left = MockLiteralRational(10.0)
        right = MockLiteralRational(4.0)
        expr = MockOperatorExpression("/", [left, right])
        assert evaluate_true_static_expression(expr) == 2.5

    def test_nested_expression(self):
        """Nested expressions evaluate correctly.

        Input: (3.0 + 4.0) * 2.0
        Output: 14.0
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        inner = MockOperatorExpression(
            "+", [MockLiteralRational(3.0), MockLiteralRational(4.0)]
        )
        expr = MockOperatorExpression("*", [inner, MockLiteralRational(2.0)])
        assert evaluate_true_static_expression(expr) == 14.0

    def test_unary_negation(self):
        """Unary negation evaluates correctly.

        Input: -3.0
        Output: -3.0
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        inner = MockLiteralRational(3.0)
        expr = MockOperatorExpression("-", [inner])
        assert evaluate_true_static_expression(expr) == -3.0

    def test_unary_plus(self):
        """Unary plus evaluates correctly.

        Input: +3.0
        Output: 3.0
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        inner = MockLiteralRational(3.0)
        expr = MockOperatorExpression("+", [inner])
        assert evaluate_true_static_expression(expr) == 3.0

    def test_integer_float_mixing(self):
        """Integer and float operands mix correctly.

        Input: 3 * 2.5
        Output: 7.5
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        left = MockLiteralInteger(3)
        right = MockLiteralRational(2.5)
        expr = MockOperatorExpression("*", [left, right])
        assert evaluate_true_static_expression(expr) == 7.5

    def test_complex_nested_with_unit(self):
        """Complex expression with unit annotation evaluates correctly.

        Input: (3.0 [m]) * 2.0
        Output: 6.0
        """
        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        value = MockLiteralRational(3.0)
        unit = MockFeatureReferenceExpression(name="metre", qualified_name="SI::metre")
        unit_expr = MockOperatorExpression("[", [value, unit])
        expr = MockOperatorExpression("*", [unit_expr, MockLiteralRational(2.0)])
        assert evaluate_true_static_expression(expr) == 6.0

    # Error cases

    def test_feature_reference_raises(self):
        """Feature reference in expression raises ValueError.

        Input: FeatureReferenceExpression("radius")
        Output: ValueError with descriptive message
        """
        import pytest

        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        expr = MockFeatureReferenceExpression(name="radius")
        with pytest.raises(ValueError, match="Feature reference 'radius'"):
            evaluate_true_static_expression(expr)

    def test_chain_expression_raises(self):
        """Chain expression raises ValueError.

        Input: FeatureChainExpression("my_calc", "output")
        Output: ValueError
        """
        import pytest

        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        expr = MockFeatureChainExpression(instance_name="my_calc", attr_name="output")
        with pytest.raises(ValueError, match="Feature reference"):
            evaluate_true_static_expression(expr)

    def test_unsupported_operator_raises(self):
        """Unsupported operator raises ValueError.

        Input: 2.0 ** 3.0 (exponentiation)
        Output: ValueError
        """
        import pytest

        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        left = MockLiteralRational(2.0)
        right = MockLiteralRational(3.0)
        expr = MockOperatorExpression("**", [left, right])
        with pytest.raises(ValueError, match="Unsupported operator"):
            evaluate_true_static_expression(expr)

    def test_division_by_zero_raises(self):
        """Division by zero raises ValueError.

        Input: 1.0 / 0.0
        Output: ValueError
        """
        import pytest

        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        left = MockLiteralRational(1.0)
        right = MockLiteralRational(0.0)
        expr = MockOperatorExpression("/", [left, right])
        with pytest.raises(ValueError, match="Division by zero"):
            evaluate_true_static_expression(expr)

    def test_none_expression_raises(self):
        """None expression raises TypeError.

        Input: None
        Output: TypeError
        """
        import pytest

        from agentic_mbse.sysml.expression import evaluate_true_static_expression

        with pytest.raises(TypeError, match="Cannot evaluate None"):
            evaluate_true_static_expression(None)

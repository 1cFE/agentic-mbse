"""Tests for sysml_utils type definitions.

These tests document the expected behavior of all dataclasses and enums.
"""

import pytest


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


def test_the_permissive_expression_ref_is_gone():
    """`ExpressionRef` is deleted, not deprecated.

    It let a consumer rebuild a reference from names and carried the live element along
    for anyone who wanted to go back to the parser.  Both are what `semantic-evidence/v2`
    removes, so the type has no replacement under its old name and no alias.
    """
    from agentic_mbse.sysml import types

    assert not hasattr(types, "ExpressionRef")
    with pytest.raises(ImportError):
        from agentic_mbse.sysml.types import ExpressionRef  # noqa: F401


def test_the_reference_evidence_carries_no_live_element():
    """The closed value records facts; it never hands a caller the parser node back."""
    from dataclasses import fields

    from agentic_mbse.sysml.data_models import ResolvedTargetFact
    from agentic_mbse.sysml.reference_use import ExactReferenceUse

    names = {field.name for field in fields(ResolvedTargetFact)}
    assert "element" not in names
    assert {"element_id", "qualified_name", "document_url", "document_tier"} <= names
    assert "element" not in {field.name for field in fields(ExactReferenceUse)}


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


def test_binding_info_expression_carries_ordered_reference_uses():
    """BindingInfo captures the ordered closed uses for EXPRESSION bindings.

    Input: BindingInfo with EXPRESSION type and a reference-use tuple
    Output: the uses are accessible in authored order, as closed values
    """
    from uuid import NAMESPACE_URL, uuid5

    from agentic_mbse.sysml.data_models import ResolvedTargetFact
    from agentic_mbse.sysml.reference_use import (
        ExactReferenceUse,
        ExactSemanticPath,
        IndexedReferenceUse,
    )
    from agentic_mbse.sysml.types import BindingInfo, BindingType

    def _use(name: str) -> ExactReferenceUse:
        fact = ResolvedTargetFact(
            element_id=uuid5(NAMESPACE_URL, name),
            owner_element_id=None,
            redefined_element_ids=(),
            qualified_name=f"Part::{name}",
            element_kind="AttributeUsage",
            element_name=name,
        )
        return ExactReferenceUse(
            path=ExactSemanticPath(
                root=fact, segments=(fact,), leaf=fact, resolved_member_names=()
            ),
            form="bare",
            authored_text=name,
            authored_segments=(name,),
            authored_qualifier=None,
            plural=False,
            location=None,
        )

    expr_binding = BindingInfo(
        param_name="result",
        binding_type=BindingType.EXPRESSION,
        reference_uses=(_use("a"), _use("b")),
    )

    assert expr_binding.is_expression is True
    assert len(expr_binding.reference_uses) == 2
    assert expr_binding.reference_uses[0].path.leaf.element_name == "a"

    # An indexed use stays closed here and is never projected into path metadata.
    indexed = BindingInfo(
        param_name="picked",
        binding_type=BindingType.EXPRESSION,
        reference_uses=(IndexedReferenceUse(reference="cells#(2).mass", location=None),),
    )
    assert not hasattr(indexed.reference_uses[0], "path")


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

"""Tests for Level 2 integration with sysml_utils.binding.

Validates that Level 2 uses sysml_utils binding utilities correctly.
"""

from agentic_mbse.sysml.binding import extract_bindings
from agentic_mbse.sysml.types import BindingInfo, BindingType


def test_level2_imports_extract_bindings():
    """Level 2 imports extract_bindings from agentic_mbse.sysml.binding.

    Input: Import check
    Output: extract_bindings is available in level2_structure module
    """
    from agentic_mbse.validation import level2_structure

    # Verify the import is present
    assert hasattr(level2_structure, "extract_bindings")
    assert level2_structure.extract_bindings is extract_bindings


def test_level2_uses_sysml_utils_exclusively():
    """Level 2 uses sysml_utils exclusively - no legacy functions.

    Input: Module inspection
    Output: No deprecated helper functions present
    """
    from agentic_mbse.validation import level2_structure

    # Verify legacy functions are removed (Phase 6 cleanup)
    assert not hasattr(level2_structure, "_get_binding_for_input")
    assert not hasattr(level2_structure, "_is_input_bound_in_usage")
    assert not hasattr(level2_structure, "_is_literal_binding")
    assert not hasattr(level2_structure, "_get_binding_targets")
    assert not hasattr(level2_structure, "_extract_all_feature_refs")


def test_binding_info_is_bound_property():
    """BindingInfo.is_bound property works for Level 2 logic.

    Input: BindingInfo with different binding types
    Output: is_bound returns correct value
    """
    bound = BindingInfo(param_name="x", binding_type=BindingType.CHAIN)
    unbound = BindingInfo(param_name="y", binding_type=BindingType.UNBOUND)
    literal = BindingInfo(param_name="z", binding_type=BindingType.LITERAL)

    assert bound.is_bound is True
    assert unbound.is_bound is False
    assert literal.is_bound is True  # Literals are still bound


def test_binding_info_is_literal_property():
    """BindingInfo.is_literal property works for Level 2 logic.

    Input: BindingInfo with literal binding
    Output: is_literal returns True
    """
    literal = BindingInfo(param_name="x", binding_type=BindingType.LITERAL)
    chain = BindingInfo(param_name="y", binding_type=BindingType.CHAIN)
    reference = BindingInfo(param_name="z", binding_type=BindingType.REFERENCE)
    expression = BindingInfo(param_name="w", binding_type=BindingType.EXPRESSION)

    assert literal.is_literal is True
    assert chain.is_literal is False
    assert reference.is_literal is False
    assert expression.is_literal is False


def test_binding_type_enum_values():
    """BindingType enum has expected values for Level 2 checks.

    Input: BindingType enum
    Output: All expected values present
    """
    assert BindingType.CHAIN.value == "chain"
    assert BindingType.REFERENCE.value == "reference"
    assert BindingType.LITERAL.value == "literal"
    assert BindingType.EXPRESSION.value == "expression"
    assert BindingType.UNBOUND.value == "unbound"


def test_level2_check_unbound_inputs_same_behavior():
    """check_unbound_inputs produces same results as before refactor.

    This is validated by the regression test in test_integration_regression.py.
    Here we just verify the function exists and is callable.
    """
    from agentic_mbse.validation.level2_structure import check_unbound_inputs

    assert callable(check_unbound_inputs)


def test_level2_essential_helpers_exist():
    """Level 2 has essential helper functions for validation.

    Input: Module inspection
    Output: Required functions exist
    """
    from agentic_mbse.validation import level2_structure

    # Essential helpers that remain after Phase 6 cleanup
    assert hasattr(level2_structure, "_extract_input_features")
    assert hasattr(level2_structure, "_has_default_value")

    # Verify they're callable
    assert callable(level2_structure._extract_input_features)
    assert callable(level2_structure._has_default_value)

    # `_has_defined_value` is gone: its only caller read `ExpressionRef.element` to reach a
    # live node, and the closed evidence route carries `ResolvedTargetFact.declares_value`
    # instead.  Nothing called it afterwards, and a `hasattr` assertion is not a caller.
    assert not hasattr(level2_structure, "_has_defined_value")

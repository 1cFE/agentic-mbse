"""Learning test: how SysIDE 0.8.4 spells a conditional, on the ES-006 prototype fixture.

The subset facts recognize a conditional as an `OperatorExpression` whose operator reads
``if`` (`subset_extraction._is_conditional`). If SysIDE changes the spelling, this fails first.
It also pins why ES-006 is refusal-eligible only with `RESOLVED_TARGET_MISSING`: the
conditional's branch operands leave the reference walk without an exact target.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.reference_use import inspect_reference_uses, operand_bearing_operands
from agentic_mbse.sysml.syside_adapter import SysideAdapter

FIXTURE = (
    Path(__file__).parents[1]
    / "fixtures"
    / "subset_profile"
    / "cases"
    / "conditional_operator.sysml"
)


def test_a_conditional_is_an_if_operator_expression_with_three_operands() -> None:
    model, diagnostics = SysideAdapter.load_model([FIXTURE])
    assert not diagnostics.contains_errors()
    (result,) = [
        f
        for f in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True)
        if str(getattr(f, "qualified_name", None)) == "fx::Min2::r"
    ]
    expression = result.feature_value_expression
    assert SysideAdapter.is_instance(expression, "OperatorExpression")
    assert str(expression.operator) == "if"
    condition, then_branch, else_branch = operand_bearing_operands(expression)
    assert str(condition.operator) == "<"
    assert SysideAdapter.is_instance(then_branch, "FeatureReferenceExpression")
    assert SysideAdapter.is_instance(else_branch, "FeatureReferenceExpression")
    with pytest.raises(SemanticEvidenceError) as raised:
        inspect_reference_uses(expression)
    assert raised.value.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING

"""Learning test: how SysIDE 0.8.4 spells a conditional, and what the reference walk makes of it.

SysIDE reads ``if c ? a else b`` as an `OperatorExpression` whose operator is ``if``, with the
condition and both branches as operands. The reference walk (`reference_use.py`) gives the
branch operands no exact target, so it raises `RESOLVED_TARGET_MISSING`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.reference_use import inspect_reference_uses, operand_bearing_operands
from agentic_mbse.sysml.syside_adapter import SysideAdapter

MODEL = """package fx {
    private import ScalarValues::*;
    calc def Min2 { in a : Real; in b : Real; return r : Real = if a < b ? a else b; }
    part def Site {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        calc m : Min2 { in a = x; in b = y; }
    }
    part site : Site;
}
"""


def test_a_conditional_is_an_if_operator_expression_with_three_operands(tmp_path: Path) -> None:
    path = tmp_path / "conditional.sysml"
    path.write_text(MODEL, encoding="utf-8")
    model, diagnostics = SysideAdapter.load_model([path])
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

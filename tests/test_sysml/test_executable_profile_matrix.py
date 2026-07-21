"""Golden-driven matrix tests: frozen operand facts receive the v3 answer key.

`classify_equality` and `unit_compatibility` are pure, offline decision procedures — this test
drives them straight off `golden.json`'s `type_units.equality_cases` (14 S1-certified rows) and
`type_units.inequality_cases` (2 rows added here, D9: byte-copies of certified operand facts,
only `operator`/`decision` are new). This is B1 pinned: the golden IS the table.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_mbse.sysml.executable_profile import classify_equality, unit_compatibility
from agentic_mbse.sysml.expression_facts import OperandTypeFact, UnitFact

GOLDEN = json.loads(Path("tests/fixtures/constraint_fact_shapes/golden.json").read_text())

_EQUALITY_CASES = GOLDEN["type_units"]["equality_cases"]
_INEQUALITY_CASES = GOLDEN["type_units"]["inequality_cases"]


def _operand(d: dict) -> OperandTypeFact:
    """Build an `OperandTypeFact` straight from a golden `left`/`right` dict.

    The golden's `unit.dimension` uses the retired `ISQBase::Length` spelling, not production
    `ISQBase::LengthUnit` — harmless here, since the gate only compares dimension *equality*
    between two operands sharing the same convention (plan.md Phase 1 note).
    """
    u = d["unit"]
    return OperandTypeFact(
        category=d["category"],
        enumeration=d["enumeration"],
        unit=UnitFact(unit=u["unit"], dimension=u["dimension"]) if u else None,
    )


V3_EXPECTED = {
    "enum_own": "warn_non_numerical_equality",
    "enum_incompatible": "warn_non_numerical_equality",
    "integer_real": "block_real_equality_requires_tolerance",
    "integer_integer": "block_integer_equality_unpreservable",
    "boolean_boolean": "warn_non_numerical_equality",
    "string_string": "warn_non_numerical_equality",
    "quantity_same_unit": "block_real_equality_requires_tolerance",
    "quantity_convertible_unit": "block_unit_conversion_required",
    "quantity_incompatible_dimension": "block_incompatible_dimensions",
    "unit_bearing_arithmetic": "block_real_equality_requires_tolerance",
    "unitless_dimensioned": "block_unitless_dimensioned",
    "quantity_feature_unknown_unit": "block_unknown_exact_unit",
    "unresolved_operand": "block_unresolved_operand",
    "inherited_alias_type": "block_real_equality_requires_tolerance",
}


@pytest.mark.parametrize("case", _EQUALITY_CASES, ids=lambda c: c["name"])
def test_v3_answer_key_over_frozen_golden_operand_facts(case: dict) -> None:
    got = classify_equality(_operand(case["left"]), _operand(case["right"]))
    assert got == V3_EXPECTED[case["name"]]


@pytest.mark.parametrize("case", _INEQUALITY_CASES, ids=lambda c: c["name"])
def test_inequality_matrix_reproduces_golden(case: dict) -> None:
    assert case["operator"] == "<="  # the only operator the two D9 fixtures use
    got = unit_compatibility(_operand(case["left"]), _operand(case["right"]))
    assert got == case["decision"]


def test_v3_answer_key_codes_are_profile_reason_codes() -> None:
    from agentic_mbse.sysml.executable_profile import REASON_CODES

    assert set(V3_EXPECTED.values()) <= REASON_CODES

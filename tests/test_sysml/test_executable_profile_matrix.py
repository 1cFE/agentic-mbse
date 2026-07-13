"""Golden-driven matrix tests: the operand-fact gate reproduces S1's answer key.

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

GOLDEN = json.loads(
    Path("tests/fixtures/constraint_fact_shapes/golden.json").read_text()
)

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


@pytest.mark.parametrize("case", _EQUALITY_CASES, ids=lambda c: c["name"])
def test_equality_matrix_reproduces_golden(case: dict) -> None:
    got = classify_equality(_operand(case["left"]), _operand(case["right"]))
    assert got == case["decision"]


@pytest.mark.parametrize("case", _INEQUALITY_CASES, ids=lambda c: c["name"])
def test_inequality_matrix_reproduces_golden(case: dict) -> None:
    assert case["operator"] == "<="  # the only operator the two D9 fixtures use
    got = unit_compatibility(_operand(case["left"]), _operand(case["right"]))
    assert got == case["decision"]


def test_golden_reason_codes_are_a_subset_of_profile_reason_codes() -> None:
    """I3: every golden decision the matrix can return is a name the profile owns."""
    from agentic_mbse.sysml.executable_profile import REASON_CODES

    golden_decisions = {c["decision"] for c in _EQUALITY_CASES}
    assert golden_decisions <= REASON_CODES

"""The design-choice pattern's validated example and the goal-layer dry-run seed (design D16).

`tests/fixtures/sump_pump/` holds one sump/pump model in three trees over one library.
`seed/` has no fit check, `right/` supplies the pump and asserts that it covers demand,
and `wrong/` sizes the pump from demand. All three pass every validation level; that
`wrong/` passes is the point, because validation cannot see the design-choice rule.
"""

from pathlib import Path

import pytest

from agentic_mbse.validation.runner import run_all_checks

FIXTURE = Path(__file__).parent / "fixtures" / "sump_pump"


def sysml(tree: str) -> str:
    """Return the SysML source of one fixture tree."""
    return "\n".join(
        p.read_text(encoding="utf-8") for p in sorted((FIXTURE / tree).rglob("*.sysml"))
    )


@pytest.mark.parametrize("tree", ["seed", "right", "wrong"])
def test_tree_passes_all_six_levels(tree):
    result = run_all_checks(str(FIXTURE / tree / "models"), fail_fast=False)

    assert [r.level for r in result.results] == [1, 2, 3, 4, 5, 6]
    assert result.overall_success
    assert [issue for r in result.results for issue in r.issues] == []


def test_only_right_reports_fit_and_only_wrong_sizes_the_pump():
    assert "assert constraint pump_fit" in sysml("right")
    assert "sizing.capacity" in sysml("wrong")
    assert "pump_fit" not in sysml("seed") and "PumpSizing" not in sysml("seed")


def test_the_fit_check_is_an_admitted_numerical_constraint():
    (level4,) = run_all_checks(str(FIXTURE / "right" / "models"), specific_level=4).results

    assert level4.metrics["Admitted numerical"] == 1
    assert level4.metrics["Malformed numerical"] == 0

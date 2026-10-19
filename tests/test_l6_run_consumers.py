"""The before/after safeguard's pure parts, with no consumer tree (Item 3 Phase 11, Appendix C).

`scripts/l6_subset/run_consumers.py` decides from a base run's text and a branch run's report
whether a tree went from pass to fail. These tests feed it built runs, so the decision itself is
checked without SysIDE or the sibling checkouts.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "l6_subset" / "run_consumers.py"


@pytest.fixture(scope="module")
def rc() -> ModuleType:
    spec = importlib.util.spec_from_file_location("l6_run_consumers", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look their module up while being built
    spec.loader.exec_module(module)
    return module


ROOT = "/tmp/x/trees/dc3-baseline"


def _text(l6: str = "✅", crash: int | None = None, l2_extra: str = "") -> str:
    lines = []
    for n in range(1, 7):
        if n == crash:
            lines.append(f"❌ Error running Level {n}: boom")
            continue
        mark = l6 if n == 6 else "✅"
        lines.append(f"{mark} Level {n}: Name {n}")
        if n == 2:
            lines.append(f"   Positional pin list: none (looked at {ROOT}/positional-pins.toml)")
            if l2_extra:
                lines.append(l2_extra)
        if n == 6:
            lines.append("   L6_DESIGN_ATTR_UNEXTRACTABLE: 3")
            lines.append("   L6_DESIGN_ATTR_INCOMPLETE: 0")
        lines.append("")
    return "\n".join(lines)


def _report(statuses: dict[int, str], extractions: int = 1, **l6: Any) -> dict[str, Any]:
    levels = []
    for n in range(1, 7):
        level = {
            "level": n,
            "status": statuses.get(n, "passed"),
            "metrics": {},
            "issues": [],
            "unstructured": [],
            "summarized": [],
        }
        if n == 6:
            level["metrics"] = {
                "Execution target": f"unset (no execution-target in {ROOT}/pyproject.toml)",
                "L6_DESIGN_ATTR_UNEXTRACTABLE": 3,
                "L6_DESIGN_ATTR_INCOMPLETE": 0,
            }
            level.update(l6)
        levels.append(level)
    return {
        "levels": levels,
        "run_info": {"constraint_extractions": extractions},
        "pass_notes": [],
        "exit_code": 0,
    }


def _run(rc: ModuleType, text: str, exit_code: int, report: dict[str, Any] | None = None) -> Any:
    return rc.TreeRun(
        tree="dc3-baseline",
        tree_commit="c",
        code_label="branch" if report else "base",
        code_commit="k",
        module_file="m",
        exit_code=exit_code,
        wall_time_s=1.0,
        levels=rc.parse_levels(text),
        stdout=text,
        stderr="",
        report=report,
    )


def test_parses_base_level_status_including_crashed_recorded_as_pass(rc):
    levels = rc.parse_levels(_text(l6="❌", crash=4))
    assert levels[4].status == "crashed, recorded as pass"
    assert levels[6].status == "failed" and levels[1].status == "passed"
    assert rc.text_code_counts(levels[6])["L6_DESIGN_ATTR_UNEXTRACTABLE"] == 3
    assert rc.resolved_root(_run(rc, _text(), 0)) == ROOT


def test_identical_passing_runs_raise_no_flag(rc):
    base = _run(rc, _text(), 0)
    branch = _run(rc, _text(), 0, _report({}))
    comparison = rc.compare_runs(base, branch)
    assert comparison["flags"] == []
    assert comparison["levels"][6] == {
        "before": "passed",
        "after": "passed",
        "issues": [0, 0],
        "identical_text": True,
    }
    assert rc.report_root(branch.report) == ROOT


def test_flags_pass_to_fail_and_l1_l5_difference_first(rc):
    base = _run(rc, _text(), 0)
    branch = _run(rc, _text(l6="❌", l2_extra="   - ERROR: new"), 1, _report({6: "failed"}))
    flags = rc.compare_runs(base, branch)["flags"]
    assert "dc3-baseline L6: passed -> failed" in flags
    assert "dc3-baseline L2: printed result differs from base" in flags
    assert "dc3-baseline: run passed at base and fails on the branch" in flags


def test_crashed_recorded_as_pass_that_now_reports_crashed_is_flagged(rc):
    base = _run(rc, _text(crash=3), 0)
    branch = _run(rc, _text(crash=3).replace("❌ Error running Level 3: boom", "❌ Level 3: N"), 1)
    branch.report = _report({3: "crashed"})
    flags = rc.compare_runs(base, branch)["flags"]
    assert "dc3-baseline L3: crashed, recorded as pass -> crashed" in flags
    assert not any("report says" in flag for flag in flags)  # printed failed, reported crashed


def test_failed_level_that_stays_failed_is_not_a_flag(rc):
    base = _run(rc, _text(l6="❌"), 1)
    branch = _run(rc, _text(l6="❌"), 1, _report({6: "failed"}))
    assert rc.compare_runs(base, branch)["flags"] == []


def test_report_and_text_disagreeing_is_flagged(rc):
    base = _run(rc, _text(), 0)
    branch = _run(rc, _text(), 0, _report({5: "failed"}))
    assert (
        "dc3-baseline L5: report says failed, text says passed"
        in rc.compare_runs(base, branch)["flags"]
    )


def test_more_than_one_constraint_extraction_is_flagged(rc):
    base = _run(rc, _text(), 0)
    branch = _run(rc, _text(), 0, _report({}, extractions=2))
    assert (
        "dc3-baseline: branch ran 2 constraint extractions, not 1"
        in rc.compare_runs(base, branch)["flags"]
    )


def test_time_criterion_fails_above_1_10(rc):
    assert rc.time_flag("fusion-tea", 100.0, 110.0) is None
    assert "over 1.1 x base" in rc.time_flag("fusion-tea", 100.0, 110.1)
    assert rc.time_flag("dc3-baseline", 10.0, 30.0) is None  # only fusion-tea is held to it


def test_refuses_dirty_branch_or_head_mismatch(rc):
    assert rc.branch_refusal("", "abc", "abc") is None
    assert "dirty" in rc.branch_refusal(" M src/x.py\n", "abc", "abc")
    assert "is not HEAD" in rc.branch_refusal("", "abc", "def")


def test_step_11_counts_new_omitted_warnings_and_unextractable_after_suppression(rc):
    issues = [
        {"code": "L6_SUBSET_OMITTED", "display": "warning"},
        {"code": "L6_SUBSET_OMITTED", "display": "warning"},
        {"code": "L6_SUBSET_REFUSED", "display": "error"},
    ]
    report = _report({6: "failed"}, issues=issues)
    report["levels"][5]["metrics"]["L6_DESIGN_ATTR_INCOMPLETE"] = 2
    base = _run(rc, _text(l6="❌"), 1)
    branch = _run(rc, _text(l6="❌"), 1, report)
    changes = rc.l6_changes("dc3-baseline", base, branch)
    assert changes["omitted_warnings"] == 2 and changes["omitted_expected"] == 32
    assert changes["unextractable"] == [3, 0]  # the String ones are suppressed (D10)
    assert changes["metric_changes"] == {"L6_DESIGN_ATTR_INCOMPLETE": [0, 2]}
    assert changes["branch_codes"] == {
        "L6_SUBSET_OMITTED (warning)": 2,
        "L6_SUBSET_REFUSED (error)": 1,
    }

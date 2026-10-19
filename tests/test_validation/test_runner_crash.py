"""A level that raises fails the run and is named (Item 3 design "Runner and report", gate R3-2)."""

import pytest

from agentic_mbse.sysml.types import Severity, ValidationCode
from agentic_mbse.validation import runner
from agentic_mbse.validation.common import QualityCheckResult, check_error_issue
from tests.helpers.l6_projects import make_project, run_cli


def _raise_at(monkeypatch: pytest.MonkeyPatch, level: int, error: Exception) -> None:
    name, _check = runner.QUALITY_CHECKS[level - 1]

    def raising(models_path: str) -> QualityCheckResult:
        raise error

    checks = list(runner.QUALITY_CHECKS)
    checks[level - 1] = (name, raising)
    monkeypatch.setattr(runner, "QUALITY_CHECKS", checks)


@pytest.mark.parametrize("level", [3, 6])
def test_level_that_raises_is_failed_and_named(monkeypatch, tmp_path, level):
    _raise_at(monkeypatch, level, RuntimeError("boom"))
    code, out = run_cli("validate", f"--level={level}", str(make_project(tmp_path)))
    assert code == 1
    assert f"❌ Level {level}:" in out
    assert f"ERROR: Level {level} crashed: RuntimeError: boom" in out
    assert "All quality checks passed" not in out
    assert "Quality checks failed" in out


@pytest.mark.syside
def test_complete_run_records_the_crash_and_runs_the_rest(monkeypatch, tmp_path):
    _raise_at(monkeypatch, 3, ValueError("bad graph"))
    code, out = run_cli("validate", "--complete", str(make_project(tmp_path)))
    assert code == 1
    assert "ERROR: Level 3 crashed: ValueError: bad graph" in out
    for level in (4, 5, 6):
        assert f"Level {level}:" in out
    assert "❌ Failed: 1" in out


@pytest.mark.syside
def test_fail_fast_stops_at_the_crashed_level(monkeypatch, tmp_path):
    _raise_at(monkeypatch, 2, RuntimeError("boom"))
    code, out = run_cli("validate", str(make_project(tmp_path)))
    assert code == 1
    assert "Stopping at first failure (Level 2)" in out
    assert "Level 3:" not in out


def test_crashed_result_carries_one_level_crashed_error():
    result = runner.crashed_result(4, "Level 4: Constraint Coverage", KeyError("x"))
    assert result.level == 4
    assert result.level_name == "Constraint Coverage"
    assert result.success is False
    (issue,) = result.structured_issues
    assert issue.code is ValidationCode.LEVEL_CRASHED
    assert issue.severity is Severity.ERROR
    assert issue.level == 4
    assert result.issues == ["ERROR: Level 4 crashed: KeyError: 'x'"]


def test_check_error_issue_names_check_subject_and_error():
    issue = check_error_issue(
        "check_anonymous_returns", "calc def Foo", AttributeError("no owner"), "m.sysml:3"
    )
    assert issue.code is ValidationCode.L6_CHECK_ERROR
    assert issue.severity is Severity.ERROR
    assert issue.level == 6
    assert issue.message == (
        "check_anonymous_returns could not inspect calc def Foo: AttributeError: no owner"
    )
    assert issue.location == "m.sysml:3"
    assert issue.reason_code == "AttributeError"


def test_verbose_prints_the_traceback(monkeypatch, tmp_path, capsys):
    _raise_at(monkeypatch, 3, RuntimeError("boom"))
    aggregated = runner.run_all_checks(str(make_project(tmp_path)), specific_level=3, verbose=True)
    assert aggregated.overall_success is False
    assert "Traceback" in capsys.readouterr().err

"""`validate --json-report`: every level's full result, untruncated (Item 3 design D6, I8)."""

import json
from pathlib import Path

import pytest

from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue
from agentic_mbse.validation import runner
from agentic_mbse.validation.common import QualityCheckResult
from agentic_mbse.validation.report import REPORT_SCHEMA, unstructured_issues
from tests.helpers.l6_projects import make_project, run_cli

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _report(tmp_path: Path, *argv: str) -> tuple[int, str, dict]:
    path = tmp_path / "report.json"
    code, out = run_cli("validate", "--json-report", str(path), *argv)
    return code, out, json.loads(path.read_text())


def _issue(text: str, severity: Severity = Severity.WARNING) -> ValidationIssue:
    return ValidationIssue(
        level=6, severity=severity, code=ValidationCode.L6_CHECK_ERROR, message=text
    )


def test_unstructured_is_issues_minus_structured_as_a_multiset():
    result = QualityCheckResult(level=6, level_name="x", success=True)
    result.add_issue(_issue("same"))
    result.issues.append("bare manifest problem")
    result.add_issue(_issue("same"))
    result.issues.append("WARN: same")  # a bare string equal to a structured one's text
    assert unstructured_issues(result) == ["bare manifest problem", "WARN: same"]
    assert len(unstructured_issues(result)) + len(result.structured_issues) == len(result.issues)


def test_structured_issue_missing_from_issues_is_an_error():
    result = QualityCheckResult(level=6, level_name="x", success=True)
    result.structured_issues.append(_issue("never added to issues"))
    with pytest.raises(ValueError, match="structured issues missing from issues"):
        unstructured_issues(result)


@pytest.mark.syside
def test_report_holds_every_issue_of_every_level_untruncated(tmp_path):
    code, out, report = _report(tmp_path, "--complete", str(FIXTURES / "adr002_violations"))
    assert report["schema"] == REPORT_SCHEMA == "validate-report/v3"
    assert report["exit_code"] == code == 1
    assert report["overall_success"] is False
    assert [level["level"] for level in report["levels"]] == [1, 2, 3, 4, 5, 6]
    assert report["run_info"]["constraint_extractions"] == 1
    assert report["command"] == {
        "path": str(FIXTURES / "adr002_violations"),
        "mode": "complete",
        "level": None,
        "execution_target": None,
    }
    l6 = report["levels"][5]
    assert l6["status"] == "failed"
    assert len(l6["issues"]) > 5  # the text shows five; the report shows all
    assert "... and" in out
    for issue in l6["issues"]:
        assert issue["display"] == issue["severity"]
    assert l6["detail"]["target"]["target"] == "unset"


@pytest.mark.syside
def test_unstructured_plus_structured_equals_issues_per_level(tmp_path):
    aggregated = runner.run_all_checks(str(FIXTURES / "adr002_violations"), fail_fast=False)
    for result in aggregated.results:
        assert len(unstructured_issues(result)) + len(result.structured_issues) == len(
            result.issues
        ), result.level


def test_crashed_level_appears_with_status_crashed(monkeypatch, tmp_path):
    name, _ = runner.QUALITY_CHECKS[2]

    def raising(models_path: str) -> QualityCheckResult:
        raise RuntimeError("boom")

    checks = list(runner.QUALITY_CHECKS)
    checks[2] = (name, raising)
    monkeypatch.setattr(runner, "QUALITY_CHECKS", checks)
    code, _, report = _report(tmp_path, "--level=3", str(make_project(tmp_path)))
    assert code == 1
    (level,) = report["levels"]
    assert level["status"] == "crashed"
    assert level["issues"][0]["code"] == "LEVEL_CRASHED"
    assert level["issues"][0]["message"] == "Level 3 crashed: RuntimeError: boom"


def test_pass_notes_reach_the_final_line_and_the_report(monkeypatch, tmp_path):
    name, _ = runner.QUALITY_CHECKS[2]

    def noted(models_path: str) -> QualityCheckResult:
        return QualityCheckResult(level=3, level_name="x", success=True, pass_note="a qualifier")

    checks = list(runner.QUALITY_CHECKS)
    checks[2] = (name, noted)
    monkeypatch.setattr(runner, "QUALITY_CHECKS", checks)
    code, out, report = _report(tmp_path, "--level=3", str(make_project(tmp_path)))
    assert code == 0
    assert "✅ Quality checks passed with a qualifier" in out
    assert report["pass_notes"] == ["a qualifier"]


def test_missing_report_parent_exits_2(tmp_path):
    code, out = run_cli(
        "validate",
        "--json-report",
        str(tmp_path / "absent" / "r.json"),
        str(make_project(tmp_path)),
    )
    assert code == 2
    assert "--json-report directory does not exist" in out


def test_unwritable_report_exits_1(tmp_path):
    target = tmp_path / "is-a-directory"
    target.mkdir()
    code, out = run_cli(
        "validate", "--level=3", "--json-report", str(target), str(make_project(tmp_path))
    )
    assert code == 1
    assert "cannot write --json-report" in out


@pytest.mark.syside
def test_report_is_byte_identical_across_runs_except_wall_time(tmp_path):
    """I8, with one exception the schema forces: `run_info.wall_time_s` is a measured time."""
    models = str(make_project(tmp_path))
    texts = []
    for run in ("a", "b"):
        path = tmp_path / f"{run}.json"
        run_cli("validate", "--complete", "--json-report", str(path), models)
        report = json.loads(path.read_text())
        report["run_info"]["wall_time_s"] = None
        texts.append(json.dumps(report, indent=2))
    assert texts[0] == texts[1]

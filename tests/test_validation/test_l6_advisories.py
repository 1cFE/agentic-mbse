"""L6's two routed advisories, at most WARNING and INFO under native (Item 3 Phase 6).

Spec § Library additions bullet 3; design D12, D15. Each fixture under
`tests/fixtures/l6/advisories/<name>/models/` is one shape; the tests copy it into a project in
`tmp_path` and run `validate --level=6 --json-report`.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.sysml import subset_advisories
from agentic_mbse.sysml.types import ValidationCode
from tests.helpers.l6_projects import make_project, run_cli, target_table

ADVISORIES = Path(__file__).resolve().parents[1] / "fixtures" / "l6" / "advisories"
TARGETS = ["unset", "generated", "native"]
ADVISORY = ValidationCode.L6_SUBSET_ADVISORY.value
UNVERIFIED = ValidationCode.L6_SUBSET_ADVISORY_UNVERIFIED.value
SUMMARY = "Generator-only findings (native: INFO summary)"


def _models(name: str) -> dict[str, str]:
    root = ADVISORIES / name / "models"
    return {str(p.relative_to(root)): p.read_text() for p in sorted(root.rglob("*.sysml"))}


def _run(parent: Path, name: str, target: str) -> tuple[int, str, dict[str, Any]]:
    pyproject = None if target == "unset" else target_table(f'"{target}"')
    models = make_project(parent, pyproject=pyproject, models=_models(name))
    path = parent / "report.json"
    code, out = run_cli("validate", "--level=6", "--json-report", str(path), str(models))
    (level,) = json.loads(path.read_text())["levels"]
    return code, out, level


@pytest.fixture(scope="module")
def l6(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str, str], dict[str, Any]]:
    """`l6(name, target)`: the L6 level of one `validate --level=6` report, cached per module."""
    runs: dict[tuple[str, str], dict[str, Any]] = {}

    def run(name: str, target: str) -> dict[str, Any]:
        if (name, target) not in runs:
            _code, _out, level = _run(tmp_path_factory.mktemp(f"{name}-{target}"), name, target)
            runs[name, target] = level
        return runs[name, target]

    return run


def _with(level: dict[str, Any], code: str, where: str) -> list[dict[str, Any]]:
    return [i for i in level[where] if i["code"] == code]


def _advisories(level: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [a for a in level["profile"]["advisories"] if a["kind"] == kind]


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_opaque_expression_fires_on_new_cell_and_not_on_plain_ref(l6, target):
    fired = l6("opaque_constructor", target)
    (advisory,) = _advisories(fired, "opaque-expression")
    assert advisory["node_kinds"] == ["ConstructorExpression"]
    assert advisory["location"]["qualified_name"] == "fx::Pack::c"
    assert advisory["matrix_row"] == "PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE"
    quiet = l6("opaque_quiet_plain_ref", target)
    assert quiet["profile"]["advisories"] == []
    assert quiet["profile"]["advisory_unverified"] == []


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize(
    ("name", "wrapper"), [("wrapper_collect", "collect"), ("wrapper_select", "select")]
)
def test_wrapper_fires_on_collect_select_and_not_on_bare_sum(l6, target, name, wrapper):
    (advisory,) = _advisories(l6(name, target), "wrapper")
    assert advisory["node_kinds"] == [wrapper]
    assert advisory["matrix_row"] == "PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE"
    assert l6("wrapper_quiet_bare_sum", target)["profile"]["advisories"] == []


@pytest.mark.syside
def test_wrapper_ignores_abs_inside_sum(l6):  # ES-005's refusal, not this advisory
    level = l6("wrapper_quiet_abs_in_sum", "generated")
    assert level["profile"]["advisories"] == []
    refused = [f for f in level["profile"]["findings"] if f["outcome"] == "refused"]
    assert {f["rule_id"] for f in refused} == {"invocation-callable"}


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_advisory_at_most_warning_info_under_native(l6, target):
    level = l6("opaque_constructor", target)
    shown = _with(level, ADVISORY, "issues")
    summarized = _with(level, ADVISORY, "summarized")
    if target == "native":
        assert shown == [] and len(summarized) == 1
        assert summarized[0]["severity"] == "info"
        assert ", 1 advisories, " in level["metrics"][SUMMARY]
    else:
        (issue,) = shown
        assert summarized == []
        assert issue["severity"] == "warning"
        assert issue["reason_code"] == "opaque-expression"
        assert issue["message"] == (
            "advisory (opaque-expression, not a generator refusal): ConstructorExpression has "
            "no structural rendering at fx::Pack::c"
        )


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize(
    ("name", "kind", "code"),
    [
        ("unverified_dot_select", "wrapper", "EXPRESSION_KIND_UNSUPPORTED"),
        ("unverified_metadata", "opaque-expression", "OPERAND_ITERATION_FAILED"),
    ],
)
def test_walker_semantic_evidence_error_is_advisory_unverified_warning(
    l6, target, name, kind, code
):
    level = l6(name, target)
    (issue,) = _with(level, UNVERIFIED, "issues")
    assert issue["severity"] == "warning"
    assert issue["reason_code"] == code
    assert f"advisory unverified ({kind}): could not inspect" in issue["message"]
    assert _with(level, UNVERIFIED, "summarized") == []
    assert _with(level, ValidationCode.L6_CHECK_ERROR.value, "issues") == []
    (record,) = level["profile"]["advisory_unverified"]
    assert (record["kind"], record["code"], record["display"]) == (kind, code, "warning")


@pytest.mark.syside
@pytest.mark.parametrize("name", ["unverified_dot_select", "unverified_metadata"])
def test_walker_semantic_evidence_error_lets_l6_pass_under_unset(tmp_path, name):
    code, out, level = _run(tmp_path, name, "unset")
    assert code == 0 and level["status"] == "passed"
    assert "generated compatibility not established" in out


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_other_walker_exception_is_check_error(tmp_path, monkeypatch, target):
    def broken(expression: Any) -> tuple[Any, ...]:
        raise RuntimeError("walker bug")

    monkeypatch.setattr(subset_advisories, "text_fallback_nodes", broken)
    code, _out, level = _run(tmp_path, "opaque_constructor", target)
    (error,) = _with(level, ValidationCode.L6_CHECK_ERROR.value, "issues")
    assert error["message"].startswith("subset_advisories could not inspect the loaded model")
    assert error["severity"] == "error"
    assert code == 1 and level["status"] == "failed"
    assert level["profile"]["advisories"] is None
    if target == "native":
        assert "advisories not computed" in level["metrics"][SUMMARY]

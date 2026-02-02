"""Tests for PM CLI subcommands (D4.5)."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

from agentic_mbse.pm.types import (
    ImpactResult,
    InsightInput,
    OperationResult,
    ParseWarning,
    TraceabilityEntry,
)
from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS


class MockArgs:
    """Mock argparse namespace."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# ---------------------------------------------------------------------------
# Phase 1: Infrastructure tests
# ---------------------------------------------------------------------------


class TestFindProjectRoot:
    def test_finds_root_via_backlog(self, tmp_path, monkeypatch):
        (tmp_path / "work").mkdir()
        (tmp_path / "work" / "BACKLOG.md").write_text("---\n---\n")
        sub = tmp_path / "work" / "active" / "WI-001_foo"
        sub.mkdir(parents=True)
        monkeypatch.chdir(sub)

        from agentic_mbse.cli import find_project_root

        assert find_project_root() == tmp_path

    def test_finds_root_via_claude_fallback(self, tmp_path, monkeypatch):
        (tmp_path / ".claude").mkdir()
        monkeypatch.chdir(tmp_path)

        from agentic_mbse.cli import find_project_root

        assert find_project_root() == tmp_path

    def test_returns_none_outside_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        from agentic_mbse.cli import find_project_root

        assert find_project_root() is None


class TestPrintWarnings:
    def test_prints_to_stderr(self, capsys):
        from agentic_mbse.cli.pm_cli import _print_warnings

        warnings = [
            ParseWarning(file="BACKLOG.md", location="line 5", message="missing field"),
        ]
        _print_warnings(warnings)
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "BACKLOG.md" in captured.err
        assert "missing field" in captured.err


class TestParseJsonArg:
    def test_valid_json(self):
        from agentic_mbse.cli.pm_cli import _parse_json_arg

        parsed, err = _parse_json_arg('[{"key": "val"}]', "--test")
        assert err is None
        assert parsed == [{"key": "val"}]

    def test_invalid_json(self):
        from agentic_mbse.cli.pm_cli import _parse_json_arg

        parsed, err = _parse_json_arg("not json", "--test")
        assert parsed is None
        assert "--test" in err


class TestDispatch:
    def test_no_project_root(self, monkeypatch, capsys):
        from agentic_mbse.cli.pm_cli import _dispatch

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: None)
        result = _dispatch(MockArgs(), lambda root: None)
        assert result == EXIT_FAILURE
        assert "Not inside a project" in capsys.readouterr().err

    def test_success(self, monkeypatch, tmp_path):
        from agentic_mbse.cli.pm_cli import _dispatch

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        op_result = OperationResult(success=True, message="Done")
        result = _dispatch(MockArgs(), lambda root, **kw: op_result)
        assert result == EXIT_SUCCESS

    def test_failure(self, monkeypatch, tmp_path, capsys):
        from agentic_mbse.cli.pm_cli import _dispatch

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        op_result = OperationResult(
            success=False,
            message="WI-999 not found",
            warnings=[ParseWarning(file="BACKLOG.md", location="line 1", message="warn")],
        )
        result = _dispatch(MockArgs(), lambda root, **kw: op_result)
        assert result == EXIT_FAILURE
        captured = capsys.readouterr()
        assert "WI-999 not found" in captured.out
        assert "warn" in captured.err


# ---------------------------------------------------------------------------
# Phase 2: status subcommand tests
# ---------------------------------------------------------------------------


def _make_minimal_project(tmp_path: Path) -> None:
    """Create a minimal project structure for status tests."""
    (tmp_path / "work").mkdir(exist_ok=True)
    (tmp_path / "work" / "BACKLOG.md").write_text("---\n---\n\n## Epics\n\n## Standalone Items\n")
    (tmp_path / "modeling_project").mkdir(exist_ok=True)
    (tmp_path / "modeling_project" / "REQUIREMENTS.md").write_text(
        "---\n---\n\n| ID | Requirement | Source | Enforcement | Validation Method |\n|---|---|---|---|---|\n"
    )
    (tmp_path / "modeling_project" / "VALIDATION_MATRIX.md").write_text(
        "---\n---\n\n| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |\n|---|---|---|---|---|---|---|---|---|\n"
    )
    (tmp_path / "modeling_project" / "OVERVIEW.md").write_text(
        "---\n---\n\n## Goals\n\n| ID | Goal | Priority | Status | Source | Traced Requirements |\n|---|---|---|---|---|---|\n\n## Analysis Questions\n\n| ID | Question | Implies | Source | Status |\n|---|---|---|---|---|\n"
    )
    (tmp_path / "modeling_project" / "ARCHITECTURE.md").write_text(
        "---\n---\n\n## Decisions\n\n| ID | Title | Decision | Rationale | Date | Status |\n|---|---|---|---|---|---|\n"
    )
    (tmp_path / "knowledge").mkdir(exist_ok=True)
    (tmp_path / "knowledge" / "KNOWLEDGE.md").write_text(
        "---\n---\n\n| ID | Title | Source | Context | Model Implications | Analysis Implications | Rationale | Status | Superseded By | Supersedes |\n|---|---|---|---|---|---|---|---|---|---|\n"
    )
    (tmp_path / "data").mkdir(exist_ok=True)
    (tmp_path / "data" / "traceability_matrix.csv").write_text(
        "Element,File,Type,Knowledge,Requirement,Source Type,Source Document,Source Location,Confidence,Assumptions,Last Verified\n"
    )
    # work dirs
    (tmp_path / "work" / "active").mkdir(exist_ok=True)
    (tmp_path / "work" / "completed").mkdir(exist_ok=True)
    (tmp_path / "work" / "backlog").mkdir(exist_ok=True)


class TestCmdStatus:
    def test_markdown_output(self, tmp_path, monkeypatch, capsys):
        _make_minimal_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        from agentic_mbse.cli import cmd_status

        result = cmd_status(MockArgs(json_output=False))
        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert "Project" in captured.out or "##" in captured.out

    def test_json_output(self, tmp_path, monkeypatch, capsys):
        _make_minimal_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        from agentic_mbse.cli import cmd_status

        result = cmd_status(MockArgs(json_output=True))
        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "project" in data
        assert "state" in data
        assert "requirements" in data
        assert "validation" in data

    def test_no_project_root(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)

        from agentic_mbse.cli import cmd_status

        result = cmd_status(MockArgs(json_output=False))
        assert result == EXIT_FAILURE
        assert "Not inside a project" in capsys.readouterr().err


class TestStatusIntegration:
    def test_status_in_help(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "--help"],
            capture_output=True,
            text=True,
        )
        assert "status" in result.stdout


# ---------------------------------------------------------------------------
# Phase 3: pm subcommand group tests
# ---------------------------------------------------------------------------

EXIT_USAGE = 2


class TestPmNoOperation:
    def test_no_operation_exits_usage(self, capsys):
        from agentic_mbse.cli.pm_cli import cmd_pm_no_operation

        result = cmd_pm_no_operation(MockArgs())
        assert result == EXIT_USAGE
        assert "No operation specified" in capsys.readouterr().err


class TestPmCloseItem:
    def test_dispatches_correctly(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_close_item

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(return_value=OperationResult(success=True, message="Closed WI-001"))
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_close_item", mock_fn)

        result = cmd_pm_close_item(MockArgs(wi_id="WI-001"))
        assert result == EXIT_SUCCESS
        mock_fn.assert_called_once_with(tmp_path, "WI-001")
        assert "Closed WI-001" in capsys.readouterr().out


class TestPmAddInsight:
    def test_dispatches_all_args(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_add_insight

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(
            return_value=OperationResult(
                success=True, message="Added DI-001", ids_assigned={"DI-001": "Test"}
            )
        )
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_add_insight", mock_fn)

        result = cmd_pm_add_insight(
            MockArgs(
                title="T",
                source="S",
                context="C",
                model_implications="MI",
                analysis_implications="AI",
                rationale="R",
            )
        )
        assert result == EXIT_SUCCESS
        mock_fn.assert_called_once_with(
            tmp_path,
            title="T",
            source="S",
            context="C",
            model_implications="MI",
            analysis_implications="AI",
            rationale="R",
        )


class TestPmSaveResearch:
    def test_reads_content_file(self, tmp_path, monkeypatch, capsys):
        from agentic_mbse.cli.pm_cli import cmd_pm_save_research

        content_file = tmp_path / "research.md"
        content_file.write_text("Research content here")

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(return_value=OperationResult(success=True, message="Saved research"))
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_save_research", mock_fn)

        result = cmd_pm_save_research(MockArgs(topic="my-topic", content_file=str(content_file)))
        assert result == EXIT_SUCCESS
        mock_fn.assert_called_once_with(tmp_path, topic="my-topic", content="Research content here")

    def test_missing_content_file(self, capsys):
        from agentic_mbse.cli.pm_cli import cmd_pm_save_research

        result = cmd_pm_save_research(MockArgs(topic="t", content_file="/nonexistent/file.md"))
        assert result == EXIT_USAGE
        assert "not found" in capsys.readouterr().err


class TestPmImpactQuery:
    def test_formats_results(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_impact_query

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(
            return_value=ImpactResult(
                query_id="DI-001",
                affected_elements=[
                    TraceabilityEntry(
                        element="Pump",
                        file="pump.sysml",
                        type="part",
                        source_type="",
                        source_document="",
                        source_location="",
                        confidence="",
                        assumptions="",
                        last_verified="",
                    )
                ],
            )
        )
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_impact_query", mock_fn)

        result = cmd_pm_impact_query(MockArgs(query_id="DI-001"))
        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert "DI-001" in captured.out
        assert "Pump" in captured.out

    def test_no_results(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_impact_query

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(return_value=ImpactResult(query_id="DI-999", affected_elements=[]))
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_impact_query", mock_fn)

        result = cmd_pm_impact_query(MockArgs(query_id="DI-999"))
        assert result == EXIT_SUCCESS
        assert "No traced elements" in capsys.readouterr().out


class TestPmTraceElement:
    def test_multi_value_args(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_trace_element

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(return_value=OperationResult(success=True, message="Traced element"))
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_trace_element", mock_fn)

        result = cmd_pm_trace_element(
            MockArgs(
                element="Pump",
                file="pump.sysml",
                type="part",
                knowledge=["DI-001", "DI-002"],
                requirement=["PR-001"],
                source_type="manual",
                source_doc="doc.pdf",
                source_location="p.5",
                confidence="high",
                assumptions="none",
            )
        )
        assert result == EXIT_SUCCESS
        call_kwargs = mock_fn.call_args[1]
        assert call_kwargs["knowledge"] == ["DI-001", "DI-002"]
        assert call_kwargs["requirement"] == ["PR-001"]


class TestPmIntegration:
    def test_pm_in_help(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "--help"],
            capture_output=True,
            text=True,
        )
        assert "pm" in result.stdout

    def test_pm_help_lists_operations(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "pm", "--help"],
            capture_output=True,
            text=True,
        )
        assert "close-item" in result.stdout
        assert "add-insight" in result.stdout
        assert "impact-query" in result.stdout


# ---------------------------------------------------------------------------
# Phase 4: JSON argument operation tests
# ---------------------------------------------------------------------------


class TestPmApproveResearch:
    def test_valid_json_insights(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_approve_research

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(return_value=OperationResult(success=True, message="Approved"))
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_approve_research", mock_fn)

        insights_json = json.dumps(
            [
                {
                    "title": "T",
                    "source": "S",
                    "context": "C",
                    "model_implications": "MI",
                    "analysis_implications": "AI",
                }
            ]
        )
        result = cmd_pm_approve_research(
            MockArgs(file="pending/research.md", insights=insights_json)
        )
        assert result == EXIT_SUCCESS
        call_kwargs = mock_fn.call_args[1]
        assert len(call_kwargs["insights"]) == 1
        assert isinstance(call_kwargs["insights"][0], InsightInput)

    def test_invalid_json(self, capsys):
        from agentic_mbse.cli.pm_cli import cmd_pm_approve_research

        result = cmd_pm_approve_research(MockArgs(file="f.md", insights="not json"))
        assert result == EXIT_USAGE
        assert "Invalid JSON" in capsys.readouterr().err

    def test_invalid_insight_schema(self, capsys):
        from agentic_mbse.cli.pm_cli import cmd_pm_approve_research

        result = cmd_pm_approve_research(MockArgs(file="f.md", insights='[{"title": "t"}]'))
        assert result == EXIT_USAGE
        assert "Invalid" in capsys.readouterr().err


class TestPmRegisterIntent:
    def test_goals_only(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_register_intent

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(return_value=OperationResult(success=True, message="Registered"))
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_register_intent", mock_fn)

        goals_json = json.dumps([{"goal": "G", "priority": "P0", "source": "S"}])
        result = cmd_pm_register_intent(MockArgs(goals=goals_json, questions=None))
        assert result == EXIT_SUCCESS

    def test_questions_only(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_register_intent

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)
        mock_fn = MagicMock(return_value=OperationResult(success=True, message="Registered"))
        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_register_intent", mock_fn)

        questions_json = json.dumps([{"question": "Q?", "source": "S"}])
        result = cmd_pm_register_intent(MockArgs(goals=None, questions=questions_json))
        assert result == EXIT_SUCCESS

    def test_neither_provided(self, capsys):
        from agentic_mbse.cli.pm_cli import cmd_pm_register_intent

        result = cmd_pm_register_intent(MockArgs(goals=None, questions=None))
        assert result == EXIT_USAGE
        assert "At least one" in capsys.readouterr().err


class TestPmSupersedeInsight:
    def test_not_implemented(self, monkeypatch, capsys, tmp_path):
        from agentic_mbse.cli.pm_cli import cmd_pm_supersede_insight

        monkeypatch.setattr("agentic_mbse.cli.pm_cli.find_project_root", lambda: tmp_path)

        def mock_supersede(root, **kwargs):
            raise NotImplementedError("supersede_insight not yet implemented")

        monkeypatch.setattr("agentic_mbse.cli.pm_cli._op_supersede_insight", mock_supersede)

        new_insight_json = json.dumps(
            {
                "title": "T",
                "source": "S",
                "context": "C",
                "model_implications": "MI",
                "analysis_implications": "AI",
            }
        )
        result = cmd_pm_supersede_insight(
            MockArgs(old_id="DI-001", new_insight=new_insight_json, reason="outdated")
        )
        assert result == EXIT_FAILURE
        assert "not yet implemented" in capsys.readouterr().err

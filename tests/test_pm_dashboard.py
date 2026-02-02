"""Tests for pm.dashboard — dashboard generation and rendering."""

from __future__ import annotations

from pathlib import Path

from agentic_mbse.pm.dashboard import (
    _format_date,
    _format_item_line,
    _format_item_status,
    _has_file_not_found,
    _render_header,
    _render_requirements,
    _render_validation,
    _render_work_items,
    generate_dashboard,
)
from agentic_mbse.pm.types import (
    DashboardResult,
    DerivedEpicState,
    DerivedWorkItemState,
    EpicStatus,
    ParseWarning,
    Priority,
    ProjectState,
    RequirementEntry,
    ValidationEntry,
    VerificationMechanism,
    VerificationStatus,
    VerificationType,
    WorkItemStage,
    WorkItemStatus,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_backlog_raw(work_dir: Path, yaml_body: str) -> None:
    """Write a BACKLOG.md with raw YAML frontmatter body."""
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "BACKLOG.md").write_text(f"---\n{yaml_body}\n---\n")


def _make_active(work_dir: Path, dirname: str) -> Path:
    d = work_dir / "active" / dirname
    d.mkdir(parents=True, exist_ok=True)
    return d


def _make_completed(work_dir: Path, dirname: str) -> Path:
    d = work_dir / "completed" / dirname
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_spec(item_dir: Path, status: str = "Active") -> None:
    (item_dir / "spec.md").write_text(f"---\nStatus: {status}\n---\n# Spec\n")


def _write_requirements(mp_dir: Path, rows: list[tuple[str, str, str, str, str]]) -> None:
    """Write REQUIREMENTS.md with table rows (id, req, source, enforcement, validation_method)."""
    mp_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "## Requirements\n",
        "| ID | Requirement | Source | Enforcement | Validation Method |",
        "|----|-------------|--------|-------------|-------------------|",
    ]
    for row in rows:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |")
    (mp_dir / "REQUIREMENTS.md").write_text("\n".join(lines) + "\n")


def _write_validation_matrix(mp_dir: Path, rows: list[tuple[str, str, str, str, str, str, str, str, str]]) -> None:
    """Write VALIDATION_MATRIX.md with table rows."""
    mp_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "## Verification Registry\n",
        "| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |",
        "|----|-------------|------|-----------|----------|-----------|--------|------|--------|",
    ]
    for row in rows:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | {row[8]} |")
    (mp_dir / "VALIDATION_MATRIX.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# TestRenderHeader
# ---------------------------------------------------------------------------


class TestRenderHeader:
    def test_normal_name(self, tmp_path: Path) -> None:
        project = tmp_path / "fusion-tea"
        project.mkdir()
        result = _render_header(project)
        assert result == "## Project: fusion-tea\n"

    def test_special_characters(self, tmp_path: Path) -> None:
        project = tmp_path / "my project (v2)"
        project.mkdir()
        result = _render_header(project)
        assert result == "## Project: my project (v2)\n"


# ---------------------------------------------------------------------------
# TestRenderWorkItems
# ---------------------------------------------------------------------------


def _item(
    wi_id: str = "WI-001",
    name: str = "foundation",
    state: WorkItemStatus = WorkItemStatus.BACKLOG,
    stage: WorkItemStage | None = None,
    completed_date: str | None = None,
) -> DerivedWorkItemState:
    return DerivedWorkItemState(
        id=wi_id, name=name, state=state, stage=stage, completed_date=completed_date,
    )


class TestRenderWorkItems:
    def test_no_items(self) -> None:
        state = ProjectState(epics=[], standalone=[])
        result = _render_work_items(state)
        assert "### Work Items\n" in result
        assert "No work items." in result

    def test_epic_with_mixed_states(self) -> None:
        epic = DerivedEpicState(
            name="Core",
            derived_status=EpicStatus.ACTIVE,
            declared_status=EpicStatus.ACTIVE,
            priority=Priority.P0,
            file="epics/core.md",
            items=[
                _item("WI-001", "foundation", WorkItemStatus.COMPLETED, completed_date="20260205"),
                _item("WI-002", "types", WorkItemStatus.ACTIVE, stage=WorkItemStage.DESIGNING),
                _item("WI-003", "future", WorkItemStatus.BACKLOG),
            ],
            total=3,
            done=1,
        )
        state = ProjectState(epics=[epic], standalone=[])
        result = _render_work_items(state)
        assert "Epic: Core" in result
        assert "[1/3 done]" in result
        assert "[x]" in result
        assert "completed 2026-02-05" in result
        assert "active:designing" in result
        assert "backlog" in result

    def test_multi_epic_and_standalone(self) -> None:
        epic1 = DerivedEpicState(
            name="Core",
            derived_status=EpicStatus.ACTIVE,
            declared_status=EpicStatus.ACTIVE,
            priority=Priority.P0,
            file="epics/core.md",
            items=[_item("WI-001", "foundation", WorkItemStatus.ACTIVE, stage=WorkItemStage.SPECCING)],
            total=1,
            done=0,
        )
        epic2 = DerivedEpicState(
            name="Extensions",
            derived_status=EpicStatus.DRAFT,
            declared_status=EpicStatus.DRAFT,
            priority=Priority.P1,
            file="epics/ext.md",
            items=[_item("WI-010", "plugin", WorkItemStatus.BACKLOG)],
            total=1,
            done=0,
        )
        standalone = [_item("WI-050", "one-off", WorkItemStatus.ACTIVE, stage=WorkItemStage.IMPLEMENTING)]
        state = ProjectState(epics=[epic1, epic2], standalone=standalone)
        result = _render_work_items(state)
        assert "Epic: Core" in result
        assert "Epic: Extensions" in result
        assert "Standalone:" in result
        assert "one-off" in result

    def test_all_completed(self) -> None:
        epic = DerivedEpicState(
            name="Done",
            derived_status=EpicStatus.COMPLETED,
            declared_status=EpicStatus.COMPLETED,
            priority=Priority.P0,
            file="epics/done.md",
            items=[
                _item("WI-001", "a", WorkItemStatus.COMPLETED, completed_date="20260201"),
                _item("WI-002", "b", WorkItemStatus.COMPLETED, completed_date="20260202"),
            ],
            total=2,
            done=2,
        )
        state = ProjectState(epics=[epic], standalone=[])
        result = _render_work_items(state)
        assert "[2/2 done]" in result
        assert result.count("[x]") == 2

    def test_zero_item_epic(self) -> None:
        epic = DerivedEpicState(
            name="Empty",
            derived_status=EpicStatus.DRAFT,
            declared_status=EpicStatus.DRAFT,
            priority=Priority.P2,
            file="epics/empty.md",
            items=[],
            total=0,
            done=0,
        )
        state = ProjectState(epics=[epic], standalone=[])
        result = _render_work_items(state)
        assert "[0/0 done]" in result


# ---------------------------------------------------------------------------
# TestRenderRequirements
# ---------------------------------------------------------------------------


class TestRenderRequirements:
    def test_no_file(self) -> None:
        result = _render_requirements([], has_file=False)
        assert "### Project Rules (REQUIREMENTS.md)" in result
        assert "No requirements file found." in result

    def test_empty_table(self) -> None:
        result = _render_requirements([], has_file=True)
        assert "Total: 0" in result
        assert "With validation method: 0" in result
        assert "Machine-enforceable: 0" in result

    def test_populated(self) -> None:
        entries = [
            RequirementEntry(id="PR-001", requirement="r1", source="s1", enforcement="model", validation_method="test"),
            RequirementEntry(id="PR-002", requirement="r2", source="s2", enforcement="-", validation_method="-"),
            RequirementEntry(id="PR-003", requirement="r3", source="s3", enforcement="test", validation_method=""),
        ]
        result = _render_requirements(entries, has_file=True)
        assert "Total: 3" in result
        assert "With validation method: 1" in result
        assert "Machine-enforceable: 2" in result


# ---------------------------------------------------------------------------
# TestRenderValidation
# ---------------------------------------------------------------------------


def _val_entry(
    sv_id: str = "SV-001",
    desc: str = "check",
    status: VerificationStatus = VerificationStatus.PASSING,
) -> ValidationEntry:
    return ValidationEntry(
        id=sv_id,
        description=desc,
        type=VerificationType.REASONABLENESS,
        mechanism=VerificationMechanism.TEST,
        expected="x",
        tolerance="0",
        source="s",
        test="t",
        status=status,
    )


class TestRenderValidation:
    def test_no_file(self) -> None:
        result = _render_validation([], has_file=False)
        assert "### Validation Status (VALIDATION_MATRIX.md)" in result
        assert "No validation matrix found." in result

    def test_all_passing(self) -> None:
        entries = [_val_entry("SV-001"), _val_entry("SV-002")]
        result = _render_validation(entries, has_file=True)
        assert "Passing: 2" in result
        assert "Failing: 0" in result
        assert "Failing: SV" not in result

    def test_mix_with_failing(self) -> None:
        entries = [
            _val_entry("SV-001", "good check", VerificationStatus.PASSING),
            _val_entry("SV-002", "bad check", VerificationStatus.FAILING),
            _val_entry("SV-003", "pending check", VerificationStatus.PENDING),
        ]
        result = _render_validation(entries, has_file=True)
        assert "Total: 3" in result
        assert "Passing: 1" in result
        assert "Failing: 1" in result
        assert "Pending: 1" in result
        assert "Failing: SV-002 (bad check)" in result

    def test_empty_table(self) -> None:
        result = _render_validation([], has_file=True)
        assert "Total: 0" in result
        assert "Passing: 0" in result


# ---------------------------------------------------------------------------
# TestGenerateDashboard (integration)
# ---------------------------------------------------------------------------


class TestGenerateDashboard:
    def test_empty_project(self, tmp_path: Path) -> None:
        """AP-1: freshly initialized project with no content."""
        result = generate_dashboard(tmp_path)
        assert isinstance(result, DashboardResult)
        assert f"## Project: {tmp_path.name}" in result.markdown
        assert "No work items." in result.markdown
        assert "No requirements file found." in result.markdown
        assert "No validation matrix found." in result.markdown

    def test_full_project(self, tmp_path: Path) -> None:
        """Project with all three sections populated."""
        work = tmp_path / "work"
        _write_backlog_raw(work, """\
epics:
  - name: Core
    goal: G-001
    priority: P0
    status: active
    file: epics/core.md
    items:
      - id: WI-001
        name: foundation
        scale: standard
        status: completed
        completed: "2026-02-05"
      - id: WI-002
        name: types
        scale: standard
        status: active
standalone: []""")
        _make_completed(work, "20260205_WI-001_foundation")
        d = _make_active(work, "WI-002_types")
        _write_spec(d, "Active")
        (d / "design.md").write_text("design")

        mp = tmp_path / "modeling_project"
        _write_requirements(mp, [
            ("PR-001", "req1", "src1", "model", "test"),
            ("PR-002", "req2", "src2", "-", "-"),
        ])
        _write_validation_matrix(mp, [
            ("SV-001", "check1", "reasonableness", "test", "x", "0", "s", "t", "passing"),
            ("SV-002", "check2", "reasonableness", "test", "x", "0", "s", "t", "failing"),
        ])

        result = generate_dashboard(tmp_path)
        assert "Epic: Core" in result.markdown
        assert "[1/2 done]" in result.markdown
        assert "Total: 2" in result.markdown
        assert "Failing: SV-002 (check2)" in result.markdown

    def test_missing_structured_files(self, tmp_path: Path) -> None:
        """Project with work items but no REQUIREMENTS.md or VALIDATION_MATRIX.md."""
        work = tmp_path / "work"
        _write_backlog_raw(work, """\
epics:
  - name: Core
    priority: P0
    status: draft
    file: epics/core.md
    items:
      - id: WI-001
        name: foundation
        scale: standard
        status: backlog
standalone: []""")

        result = generate_dashboard(tmp_path)
        assert "Epic: Core" in result.markdown
        assert "No requirements file found." in result.markdown
        assert "No validation matrix found." in result.markdown

    def test_warnings_accumulation(self, tmp_path: Path) -> None:
        """Warnings from all sub-operations are accumulated."""
        # No work dir, no modeling_project dir — all parsers will produce warnings
        result = generate_dashboard(tmp_path)
        # Should have warnings from requirements and validation matrix (file not found)
        warning_messages = [w.message for w in result.warnings]
        assert any("File not found" in m for m in warning_messages)
        # But dashboard still renders
        assert "## Project:" in result.markdown

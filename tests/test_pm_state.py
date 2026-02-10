"""Tests for pm.state — state derivation, stage detection, and work item resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_mbse.pm.state import (
    _derive_epic_status,
    _derive_item_state,
    _detect_stage,
    _scan_active_dirs,
    _scan_completed_dirs,
    derive_project_state,
    resolve_work_item,
)
from agentic_mbse.pm.types import (
    DerivedWorkItemState,
    EpicStatus,
    ParseWarning,
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


# ---------------------------------------------------------------------------
# TestScanActiveDirs
# ---------------------------------------------------------------------------


class TestScanActiveDirs:
    def test_normal_dirs(self, tmp_path: Path) -> None:
        active = tmp_path / "active"
        active.mkdir()
        (active / "WI-001_foundation").mkdir()
        (active / "WI-003_solar-model").mkdir()

        result = _scan_active_dirs(active, [])
        assert set(result.keys()) == {"WI-001", "WI-003"}
        assert result["WI-001"] == active / "WI-001_foundation"

    def test_empty_dir(self, tmp_path: Path) -> None:
        active = tmp_path / "active"
        active.mkdir()
        assert _scan_active_dirs(active, []) == {}

    def test_missing_dir(self, tmp_path: Path) -> None:
        assert _scan_active_dirs(tmp_path / "nonexistent", []) == {}

    def test_non_matching_ignored(self, tmp_path: Path) -> None:
        active = tmp_path / "active"
        active.mkdir()
        (active / "notes").mkdir()
        (active / "WI_bad").mkdir()
        (active / "WI-002_valid").mkdir()
        # Also ignore files
        (active / "README.md").write_text("hi")

        result = _scan_active_dirs(active, [])
        assert list(result.keys()) == ["WI-002"]


# ---------------------------------------------------------------------------
# TestScanCompletedDirs
# ---------------------------------------------------------------------------


class TestScanCompletedDirs:
    def test_normal_dirs(self, tmp_path: Path) -> None:
        completed = tmp_path / "completed"
        completed.mkdir()
        (completed / "20260205_WI-001_foundation").mkdir()
        (completed / "20260210_WI-002_types").mkdir()

        result = _scan_completed_dirs(completed, [])
        assert set(result.keys()) == {"WI-001", "WI-002"}
        path, date = result["WI-001"]
        assert path == completed / "20260205_WI-001_foundation"
        assert date == "20260205"

    def test_non_matching_ignored(self, tmp_path: Path) -> None:
        completed = tmp_path / "completed"
        completed.mkdir()
        (completed / "notes_WI-001_stuff").mkdir()
        (completed / "20260205_WI-003_valid").mkdir()

        result = _scan_completed_dirs(completed, [])
        assert list(result.keys()) == ["WI-003"]

    def test_missing_dir(self, tmp_path: Path) -> None:
        assert _scan_completed_dirs(tmp_path / "nonexistent", []) == {}


# ---------------------------------------------------------------------------
# TestDetectStage
# ---------------------------------------------------------------------------


class TestDetectStage:
    def test_spec_only(self, tmp_path: Path) -> None:
        (tmp_path / "spec.md").write_text("spec")
        assert _detect_stage(tmp_path) == WorkItemStage.SPECCING

    def test_spec_and_design(self, tmp_path: Path) -> None:
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "design.md").write_text("design")
        assert _detect_stage(tmp_path) == WorkItemStage.DESIGNING

    def test_spec_design_plan(self, tmp_path: Path) -> None:
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "design.md").write_text("design")
        (tmp_path / "plan.md").write_text("plan")
        assert _detect_stage(tmp_path) == WorkItemStage.IMPLEMENTING

    def test_spec_and_plan(self, tmp_path: Path) -> None:
        (tmp_path / "spec.md").write_text("spec")
        (tmp_path / "plan.md").write_text("plan")
        assert _detect_stage(tmp_path) == WorkItemStage.IMPLEMENTING

    def test_no_artifacts(self, tmp_path: Path) -> None:
        assert _detect_stage(tmp_path) == WorkItemStage.UNKNOWN

    def test_design_only(self, tmp_path: Path) -> None:
        (tmp_path / "design.md").write_text("design")
        assert _detect_stage(tmp_path) == WorkItemStage.DESIGNING


# ---------------------------------------------------------------------------
# TestDeriveItemState
# ---------------------------------------------------------------------------


class TestDeriveItemState:
    def test_active_default(self, tmp_path: Path) -> None:
        _write_spec(tmp_path, "Active")
        state, stage = _derive_item_state(tmp_path, [])
        assert state == WorkItemStatus.ACTIVE
        assert stage == WorkItemStage.SPECCING

    def test_paused_override(self, tmp_path: Path) -> None:
        _write_spec(tmp_path, "paused")
        state, stage = _derive_item_state(tmp_path, [])
        assert state == WorkItemStatus.PAUSED
        assert stage is None

    def test_abandoned_override(self, tmp_path: Path) -> None:
        _write_spec(tmp_path, "Abandoned")
        state, stage = _derive_item_state(tmp_path, [])
        assert state == WorkItemStatus.ABANDONED
        assert stage is None

    def test_failed_override(self, tmp_path: Path) -> None:
        _write_spec(tmp_path, "Failed")
        state, stage = _derive_item_state(tmp_path, [])
        assert state == WorkItemStatus.FAILED
        assert stage is None

    def test_completed_override(self, tmp_path: Path) -> None:
        _write_spec(tmp_path, "Completed")
        state, stage = _derive_item_state(tmp_path, [])
        assert state == WorkItemStatus.COMPLETED
        assert stage is None

    def test_missing_spec(self, tmp_path: Path) -> None:
        warnings: list[ParseWarning] = []
        state, stage = _derive_item_state(tmp_path, warnings)
        assert state == WorkItemStatus.ACTIVE
        assert stage == WorkItemStage.UNKNOWN
        msgs = [w.message for w in warnings]
        assert any("No spec.md found" in m for m in msgs)

    def test_malformed_frontmatter(self, tmp_path: Path) -> None:
        (tmp_path / "spec.md").write_text("---\n: bad yaml [[\n---\n")
        warnings: list[ParseWarning] = []
        state, stage = _derive_item_state(tmp_path, warnings)
        assert state == WorkItemStatus.ACTIVE
        # spec.md exists so stage is SPECCING (stage is file-existence based)
        assert stage == WorkItemStage.SPECCING
        assert any("Malformed YAML" in w.message for w in warnings)


# ---------------------------------------------------------------------------
# TestDeriveEpicStatus
# ---------------------------------------------------------------------------


class TestDeriveEpicStatus:
    def _item(self, state: WorkItemStatus) -> DerivedWorkItemState:
        return DerivedWorkItemState(id="WI-001", name="test", state=state)

    def test_no_items(self) -> None:
        assert _derive_epic_status([]) == EpicStatus.DRAFT

    def test_all_backlog(self) -> None:
        items = [self._item(WorkItemStatus.BACKLOG), self._item(WorkItemStatus.BACKLOG)]
        assert _derive_epic_status(items) == EpicStatus.DRAFT

    def test_one_active(self) -> None:
        items = [self._item(WorkItemStatus.BACKLOG), self._item(WorkItemStatus.ACTIVE)]
        assert _derive_epic_status(items) == EpicStatus.ACTIVE

    def test_all_completed(self) -> None:
        items = [self._item(WorkItemStatus.COMPLETED), self._item(WorkItemStatus.COMPLETED)]
        assert _derive_epic_status(items) == EpicStatus.COMPLETED

    def test_completed_and_abandoned(self) -> None:
        items = [self._item(WorkItemStatus.COMPLETED), self._item(WorkItemStatus.ABANDONED)]
        assert _derive_epic_status(items) == EpicStatus.ACTIVE

    def test_completed_and_backlog(self) -> None:
        items = [self._item(WorkItemStatus.COMPLETED), self._item(WorkItemStatus.BACKLOG)]
        assert _derive_epic_status(items) == EpicStatus.ACTIVE


# ---------------------------------------------------------------------------
# TestResolveWorkItem
# ---------------------------------------------------------------------------


class TestResolveWorkItem:
    def test_active_match(self, tmp_path: Path) -> None:
        d = _make_active(tmp_path / "work", "WI-003_solar-model")
        result = resolve_work_item(tmp_path, "WI-003")
        assert result == d

    def test_completed_match(self, tmp_path: Path) -> None:
        d = _make_completed(tmp_path / "work", "20260205_WI-001_foundation")
        result = resolve_work_item(tmp_path, "WI-001")
        assert result == d

    def test_bare_number(self, tmp_path: Path) -> None:
        d = _make_active(tmp_path / "work", "WI-003_solar-model")
        result = resolve_work_item(tmp_path, "3")
        assert result == d

    def test_not_found(self, tmp_path: Path) -> None:
        (tmp_path / "work" / "active").mkdir(parents=True)
        with pytest.raises(ValueError, match="not found"):
            resolve_work_item(tmp_path, "WI-099")

    def test_ambiguous(self, tmp_path: Path) -> None:
        _make_active(tmp_path / "work", "WI-003_solar-model")
        _make_completed(tmp_path / "work", "20260205_WI-003_old-solar")
        with pytest.raises(ValueError, match="Ambiguous"):
            resolve_work_item(tmp_path, "WI-003")

    def test_invalid_format(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Invalid work item ID format"):
            resolve_work_item(tmp_path, "bad")


# ---------------------------------------------------------------------------
# TestDeriveProjectState
# ---------------------------------------------------------------------------


class TestDeriveProjectState:
    def test_empty_project(self, tmp_path: Path) -> None:
        result = derive_project_state(tmp_path)
        assert result.data.epics == []
        assert result.data.standalone == []

    def test_backlog_only(self, tmp_path: Path) -> None:
        work = tmp_path / "work"
        _write_backlog_raw(
            work,
            """\
epics:
  - name: Core
    goal: G-001
    priority: P0
    status: draft
    file: epics/core.md
    items:
      - id: WI-001
        name: foundation
        scale: standard
        status: backlog
      - id: WI-002
        name: types
        scale: trivial
        status: backlog
standalone: []""",
        )

        result = derive_project_state(tmp_path)
        assert len(result.data.epics) == 1
        assert result.data.epics[0].total == 2
        assert result.data.epics[0].done == 0
        assert all(i.state == WorkItemStatus.BACKLOG for i in result.data.epics[0].items)

    def test_mixed_states(self, tmp_path: Path) -> None:
        work = tmp_path / "work"
        _write_backlog_raw(
            work,
            """\
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
      - id: WI-003
        name: future
        scale: trivial
        status: backlog
standalone: []""",
        )

        # Create completed dir for WI-001
        _make_completed(work, "20260205_WI-001_foundation")
        # Create active dir for WI-002 with spec and design
        d = _make_active(work, "WI-002_types")
        _write_spec(d, "Active")
        (d / "design.md").write_text("design")

        result = derive_project_state(tmp_path)
        items = {i.id: i for i in result.data.epics[0].items}
        assert items["WI-001"].state == WorkItemStatus.COMPLETED
        assert items["WI-002"].state == WorkItemStatus.ACTIVE
        assert items["WI-002"].stage == WorkItemStage.DESIGNING
        assert items["WI-003"].state == WorkItemStatus.BACKLOG
        assert result.data.epics[0].done == 1

    def test_orphaned_directory(self, tmp_path: Path) -> None:
        work = tmp_path / "work"
        _write_backlog_raw(work, "epics: []\nstandalone: []")
        d = _make_active(work, "WI-099_orphan")
        _write_spec(d, "Active")

        result = derive_project_state(tmp_path)
        assert len(result.data.standalone) == 1
        assert result.data.standalone[0].id == "WI-099"
        assert any("not found in BACKLOG.md" in w.message for w in result.warnings)

    def test_backlog_spec_conflict(self, tmp_path: Path) -> None:
        work = tmp_path / "work"
        _write_backlog_raw(
            work,
            """\
epics:
  - name: Core
    priority: P0
    status: active
    file: epics/core.md
    items:
      - id: WI-001
        name: foundation
        scale: standard
        status: active
standalone: []""",
        )
        d = _make_active(work, "WI-001_foundation")
        _write_spec(d, "paused")

        result = derive_project_state(tmp_path)
        items = {i.id: i for i in result.data.epics[0].items}
        assert items["WI-001"].state == WorkItemStatus.PAUSED
        assert any("overrides" in w.message for w in result.warnings)

    def test_epic_state_derivation(self, tmp_path: Path) -> None:
        work = tmp_path / "work"
        _write_backlog_raw(
            work,
            """\
epics:
  - name: Core
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
        status: completed
        completed: "2026-02-06"
standalone: []""",
        )
        _make_completed(work, "20260205_WI-001_foundation")
        _make_completed(work, "20260206_WI-002_types")

        result = derive_project_state(tmp_path)
        assert result.data.epics[0].derived_status == EpicStatus.COMPLETED

    def test_epic_status_mismatch(self, tmp_path: Path) -> None:
        work = tmp_path / "work"
        _write_backlog_raw(
            work,
            """\
epics:
  - name: Core
    priority: P0
    status: completed
    file: epics/core.md
    items:
      - id: WI-001
        name: foundation
        scale: standard
        status: backlog
standalone: []""",
        )

        result = derive_project_state(tmp_path)
        assert result.data.epics[0].derived_status == EpicStatus.DRAFT
        assert result.data.epics[0].declared_status == EpicStatus.COMPLETED
        assert any(
            "declared status='completed' but derived status='draft'" in w.message
            for w in result.warnings
        )

    def test_empty_backlog(self, tmp_path: Path) -> None:
        work = tmp_path / "work"
        _write_backlog_raw(work, "epics: []\nstandalone: []")
        result = derive_project_state(tmp_path)
        assert result.data.epics == []
        assert result.data.standalone == []
        assert result.warnings == []

"""State derivation for project management work items and epics.

Combines file system scanning with D4.1 parser output to derive
deterministic work item states, stages, epic states, and work item
name resolution. Returns ParseResult[ProjectState] following the
established warning-accumulation pattern.
"""

from __future__ import annotations

import re
from pathlib import Path

from agentic_mbse.pm.parser import parse_backlog, parse_frontmatter
from agentic_mbse.pm.types import (
    BacklogData,
    DerivedEpicState,
    DerivedWorkItemState,
    EpicStatus,
    ParseResult,
    ParseWarning,
    ProjectState,
    WorkItemStage,
    WorkItemStatus,
)

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

ACTIVE_DIR_RE = re.compile(r"^(WI-\d+)_(.+)$")
COMPLETED_DIR_RE = re.compile(r"^(\d{8})_(WI-\d+)_(.+)$")
_WI_ID_RE = re.compile(r"^WI-\d+$")


def _warn(warnings: list[ParseWarning], file: str, location: str, message: str) -> None:
    """Append a warning to the list."""
    warnings.append(ParseWarning(file=str(file), location=location, message=message))


def _scan_active_dirs(active_dir: Path, warnings: list[ParseWarning]) -> dict[str, Path]:
    """Scan work/active/ for directories matching WI-XXX_name pattern."""
    if not active_dir.is_dir():
        return {}

    result: dict[str, Path] = {}
    for d in active_dir.iterdir():
        if not d.is_dir():
            continue
        m = ACTIVE_DIR_RE.match(d.name)
        if m:
            result[m.group(1)] = d
    return result


def _scan_completed_dirs(
    completed_dir: Path, warnings: list[ParseWarning]
) -> dict[str, tuple[Path, str]]:
    """Scan work/completed/ for directories matching YYYYMMDD_WI-XXX_name pattern."""
    if not completed_dir.is_dir():
        return {}

    result: dict[str, tuple[Path, str]] = {}
    for d in completed_dir.iterdir():
        if not d.is_dir():
            continue
        m = COMPLETED_DIR_RE.match(d.name)
        if m:
            date_str = m.group(1)
            wi_id = m.group(2)
            result[wi_id] = (d, date_str)
    return result


def _detect_stage(item_dir: Path) -> WorkItemStage:
    """Determine work item stage from artifact file existence."""
    if (item_dir / "plan.md").exists():
        return WorkItemStage.IMPLEMENTING
    if (item_dir / "design.md").exists():
        return WorkItemStage.DESIGNING
    if (item_dir / "spec.md").exists():
        return WorkItemStage.SPECCING
    return WorkItemStage.UNKNOWN


def _derive_item_state(
    item_dir: Path,
    warnings: list[ParseWarning],
) -> tuple[WorkItemStatus, WorkItemStage | None]:
    """Derive state and stage for an active work item directory."""
    spec_path = item_dir / "spec.md"
    fm = parse_frontmatter(spec_path)
    warnings.extend(fm.warnings)

    status_str = fm.data.get("Status", "").strip().lower()

    if status_str == "completed":
        return WorkItemStatus.COMPLETED, None
    if status_str == "paused":
        return WorkItemStatus.PAUSED, None
    if status_str == "abandoned":
        return WorkItemStatus.ABANDONED, None
    if status_str == "failed":
        return WorkItemStatus.FAILED, None

    # Default: active — detect stage
    if not fm.data and not spec_path.exists():
        _warn(warnings, str(item_dir), "spec.md", "No spec.md found in active work item directory")

    stage = _detect_stage(item_dir)
    if stage == WorkItemStage.UNKNOWN:
        _warn(
            warnings,
            str(item_dir),
            "stage",
            "No recognized artifact files (spec.md, design.md, plan.md)",
        )

    return WorkItemStatus.ACTIVE, stage


def _derive_epic_status(items: list[DerivedWorkItemState]) -> EpicStatus:
    """Derive epic status from sub-item states (pure function, no I/O)."""
    if not items:
        return EpicStatus.DRAFT

    states = {item.state for item in items}

    if states == {WorkItemStatus.COMPLETED}:
        return EpicStatus.COMPLETED

    if states == {WorkItemStatus.BACKLOG}:
        return EpicStatus.DRAFT

    return EpicStatus.ACTIVE


def _get_backlog_status(backlog: BacklogData, wi_id: str) -> WorkItemStatus | None:
    """Look up a work item's declared status in BACKLOG.md."""
    for epic in backlog.epics:
        for item in epic.items:
            if item.id == wi_id:
                return item.status
    for sa in backlog.standalone:
        if sa.id == wi_id:
            return sa.status
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolve_work_item(project_root: Path, wi_id: str) -> Path:
    """Resolve a WI-XXX identifier to its directory path.

    Accepts bare numbers (e.g. "3" → "WI-003") or WI-XXX format.
    Raises ValueError on invalid format, not-found, or ambiguity.
    """
    if wi_id.isdigit():
        wi_id = f"WI-{int(wi_id):03d}"
    elif not _WI_ID_RE.match(wi_id):
        raise ValueError(f"Invalid work item ID format: '{wi_id}' (expected WI-XXX or a number)")

    candidates: list[Path] = []

    active_dir = project_root / "work" / "active"
    if active_dir.is_dir():
        for d in active_dir.iterdir():
            if d.is_dir() and d.name.startswith(f"{wi_id}_"):
                candidates.append(d)

    completed_dir = project_root / "work" / "completed"
    if completed_dir.is_dir():
        completed_re = re.compile(rf"^\d{{8}}_{re.escape(wi_id)}_")
        for d in completed_dir.iterdir():
            if d.is_dir() and completed_re.match(d.name):
                candidates.append(d)

    if len(candidates) == 0:
        searched = []
        if active_dir.is_dir():
            searched.append(str(active_dir))
        if completed_dir.is_dir():
            searched.append(str(completed_dir))
        raise ValueError(
            f"Work item '{wi_id}' not found. Searched: {', '.join(searched) or 'no directories exist'}"
        )

    if len(candidates) > 1:
        paths = ", ".join(str(c) for c in sorted(candidates))
        raise ValueError(f"Ambiguous work item '{wi_id}': multiple matches found: {paths}")

    return candidates[0]


def derive_project_state(project_root: Path) -> ParseResult[ProjectState]:
    """Derive full project state from BACKLOG.md and file system directories.

    Scans work/active/ and work/completed/ directories, reads spec.md
    frontmatter for status overrides, and aggregates epic-level summaries.
    """
    warnings: list[ParseWarning] = []
    work_dir = project_root / "work"

    # Step 1: Parse BACKLOG.md
    backlog_result = parse_backlog(work_dir / "BACKLOG.md")
    warnings.extend(backlog_result.warnings)
    backlog = backlog_result.data

    # Step 2: Scan file system
    active_dirs = _scan_active_dirs(work_dir / "active", warnings)
    completed_dirs = _scan_completed_dirs(work_dir / "completed", warnings)

    # Check for items in both active and completed
    for wi_id in set(active_dirs) & set(completed_dirs):
        _warn(
            warnings,
            str(active_dirs[wi_id]),
            wi_id,
            f"{wi_id} found in both work/active/ and work/completed/; using active",
        )
        del completed_dirs[wi_id]

    # Build lookup: WI-XXX → epic name
    backlog_epic_map: dict[str, str] = {}
    backlog_item_ids: set[str] = set()
    for epic in backlog.epics:
        for item in epic.items:
            backlog_epic_map[item.id] = epic.name
            backlog_item_ids.add(item.id)
    for sa in backlog.standalone:
        backlog_item_ids.add(sa.id)

    # Step 3: Derive state for each item
    all_items: dict[str, DerivedWorkItemState] = {}

    # 3a: Items with active directories
    for wi_id, dir_path in sorted(active_dirs.items()):
        m = ACTIVE_DIR_RE.match(dir_path.name)
        assert m is not None  # guaranteed by _scan_active_dirs
        name = m.group(2)
        state, stage = _derive_item_state(dir_path, warnings)

        if wi_id in backlog_item_ids:
            backlog_status = _get_backlog_status(backlog, wi_id)
            if backlog_status and backlog_status != state:
                _warn(
                    warnings,
                    str(dir_path / "spec.md"),
                    "Status",
                    f"spec.md Status='{state.value}' overrides "
                    f"BACKLOG.md status='{backlog_status.value}' for {wi_id}",
                )
        else:
            _warn(
                warnings,
                str(dir_path),
                wi_id,
                f"Directory exists in work/active/ but {wi_id} not found in BACKLOG.md",
            )

        all_items[wi_id] = DerivedWorkItemState(
            id=wi_id,
            name=name,
            state=state,
            stage=stage,
            epic=backlog_epic_map.get(wi_id),
            directory=dir_path,
            completed_date=None,
        )

    # 3b: Items with completed directories
    for wi_id, (dir_path, date_str) in sorted(completed_dirs.items()):
        if wi_id in all_items:
            continue
        m = COMPLETED_DIR_RE.match(dir_path.name)
        assert m is not None  # guaranteed by _scan_completed_dirs
        name = m.group(3)

        all_items[wi_id] = DerivedWorkItemState(
            id=wi_id,
            name=name,
            state=WorkItemStatus.COMPLETED,
            stage=None,
            epic=backlog_epic_map.get(wi_id),
            directory=dir_path,
            completed_date=date_str,
        )

    # 3c: Backlog-only items (in BACKLOG.md, no directory)
    for epic in backlog.epics:
        for item in epic.items:
            if item.id not in all_items:
                all_items[item.id] = DerivedWorkItemState(
                    id=item.id,
                    name=item.name,
                    state=WorkItemStatus.BACKLOG,
                    stage=None,
                    epic=epic.name,
                    directory=None,
                    completed_date=None,
                )
    for sa in backlog.standalone:
        if sa.id not in all_items:
            all_items[sa.id] = DerivedWorkItemState(
                id=sa.id,
                name=sa.name,
                state=WorkItemStatus.BACKLOG,
                stage=None,
                epic=None,
                directory=None,
                completed_date=None,
            )

    # Step 4: Build epic-level summaries
    derived_epics: list[DerivedEpicState] = []
    for epic in backlog.epics:
        epic_items = [all_items[item.id] for item in epic.items if item.id in all_items]
        derived_status = _derive_epic_status(epic_items)

        if derived_status != epic.status:
            _warn(
                warnings,
                str(work_dir / "BACKLOG.md"),
                epic.name,
                f"Epic '{epic.name}' declared status='{epic.status.value}' "
                f"but derived status='{derived_status.value}'",
            )

        derived_epics.append(
            DerivedEpicState(
                name=epic.name,
                derived_status=derived_status,
                declared_status=epic.status,
                priority=epic.priority,
                goal=epic.goal,
                file=epic.file,
                items=sorted(epic_items, key=lambda i: i.id),
                total=len(epic_items),
                done=sum(1 for i in epic_items if i.state == WorkItemStatus.COMPLETED),
            )
        )

    # Step 5: Build standalone list (includes orphans)
    standalone_items = [all_items[sa.id] for sa in backlog.standalone if sa.id in all_items]
    orphan_ids = set(all_items.keys()) - backlog_item_ids
    standalone_items += [
        all_items[wi_id] for wi_id in sorted(orphan_ids) if all_items[wi_id].epic is None
    ]

    return ParseResult(
        data=ProjectState(
            epics=derived_epics,
            standalone=sorted(standalone_items, key=lambda i: i.id),
        ),
        warnings=warnings,
    )

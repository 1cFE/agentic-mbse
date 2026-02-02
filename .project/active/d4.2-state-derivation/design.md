# Design: D4.2 — State Derivation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02 16:50:18 UTC
**Updated:** 2026-02-02 16:50:18 UTC
**Branch:** revamp-architecture
**Commit:** 3f58ea9

## Overview

Implement `src/agentic_mbse/pm/state.py` — a module that combines file system scanning with D4.1 parser output to derive deterministic work item states, stages, epic states, and work item name resolution. Returns `ParseResult[ProjectState]` following the established warning-accumulation pattern.

## Related Artifacts

- **Spec:** `.project/active/d4.2-state-derivation/spec.md`
- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.2 section)
- **D4.1 implementation:** `src/agentic_mbse/pm/parser.py`, `src/agentic_mbse/pm/types.py`
- **D4.1 tests (pattern reference):** `tests/test_pm_parser.py`
- **Frontmatter schemas:** `.project/concepts/architecture-redesign/frontmatter-schemas.md`

---

## Research Findings

### D4.1 API Contract

The parser module (`parser.py:193-248`) provides these functions used by state derivation:

- `parse_frontmatter(path: Path) -> ParseResult[dict[str, Any]]` — extracts YAML frontmatter from any `.md` file. Returns `{}` on missing/empty/malformed files with appropriate warnings.
- `parse_backlog(path: Path) -> ParseResult[BacklogData]` — parses `work/BACKLOG.md` YAML frontmatter into typed `BacklogData` with `epics: list[EpicEntry]` and `standalone: list[StandaloneEntry]`.

Key observations:
- `parse_frontmatter` normalizes YAML date coercion (dates → strings, bools → strings) at `parser.py:242-246`
- `parse_backlog` validates WI-XXX ID patterns, enum values, and completed dates — items that fail validation are skipped with warnings at `parser.py:324-331`
- Both return `ParseResult[T]` with warnings accumulated in a list — the pattern state.py must follow

### Warning Helper

`parser.py:49-51` defines `_warn(warnings, file, location, message)` — a private helper. State derivation should define its own identical helper (or we could promote it to `types.py`, but that's unnecessary coupling for a one-liner).

### Existing Types

`types.py` provides all the enums and entity models state derivation reads:
- `WorkItemStatus` (`types.py:39-45`): backlog, active, paused, abandoned, failed, completed
- `EpicStatus` (`types.py:33-36`): draft, active, completed
- `WorkItemEntry` (`types.py:95-100`): id, name, scale, status, completed
- `EpicEntry` (`types.py:103-109`): name, goal, priority, status, file, items
- `StandaloneEntry` (`types.py:112-118`): id, name, scale, priority, status, completed

### Test Patterns

`test_pm_parser.py` uses:
- `tmp_path` pytest fixture for isolated file system state
- Class-based test organization by feature (`TestParseFrontmatter`, `TestParseBacklog`, etc.)
- Consistent test naming: `test_valid_*`, `test_missing_file`, `test_empty_*`, `test_invalid_*`
- Template files tested via `TEMPLATES = Path(__file__).parent.parent / "project_templates"`

### Directory Name Conventions

From `workflows.md` § 3.2 and `frontmatter-schemas.md` § DD-1:
- Active: `work/active/{WI-XXX}_{descriptive-str}/` (e.g., `work/active/WI-003_solar-model/`)
- Completed: `work/completed/YYYYMMDD_{WI-XXX}_{descriptive-str}/` (e.g., `work/completed/20260205_WI-001_foundation-types/`)
- WI-XXX ID is derived from directory name, NOT from spec.md frontmatter (DD-1)

---

## Proposed Design

### Architecture

```
state.py
  ├── resolve_work_item()        # FR-4: WI-XXX → directory path
  ├── _scan_active_dirs()         # Internal: scan work/active/
  ├── _scan_completed_dirs()      # Internal: scan work/completed/
  ├── _detect_stage()             # FR-2: artifact file existence → stage
  ├── _derive_item_state()        # FR-1 step 2: frontmatter override + stage
  ├── _derive_epic_status()       # FR-3: sub-item states → epic status
  └── derive_project_state()      # FR-6: top-level aggregate function
```

Data flows:
```
derive_project_state(project_root)
  │
  ├── parse_backlog(work/BACKLOG.md)
  │     → BacklogData (epics + standalone items with declared states)
  │
  ├── _scan_active_dirs(work/active/)
  │     → dict[str, Path]  {WI-XXX: directory_path}
  │
  ├── _scan_completed_dirs(work/completed/)
  │     → dict[str, tuple[Path, str]]  {WI-XXX: (directory_path, date_str)}
  │
  ├── For each item in backlog + orphaned dirs:
  │     ├── Determine base state from file system (active/completed/backlog)
  │     ├── _derive_item_state() → read spec.md, apply override
  │     └── _detect_stage() → check plan.md/design.md/spec.md existence
  │
  ├── For each epic:
  │     └── _derive_epic_status() → aggregate sub-item states
  │
  └── Return ParseResult[ProjectState] with accumulated warnings
```

### New Types (additions to `types.py`)

```python
from pathlib import Path


class WorkItemStage(str, Enum):
    SPECCING = "speccing"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    UNKNOWN = "unknown"


class DerivedWorkItemState(BaseModel):
    id: str                          # WI-XXX (from directory name)
    name: str                        # descriptive-str from directory name
    state: WorkItemStatus            # derived: backlog/active/paused/abandoned/failed/completed
    stage: WorkItemStage | None      # only set when state = active; None otherwise
    epic: str | None                 # parent epic name from BACKLOG.md, or None
    directory: Path | None           # resolved path, or None for backlog-only items
    completed_date: str | None       # YYYYMMDD from completed dir name, or from BACKLOG.md


class DerivedEpicState(BaseModel):
    name: str
    derived_status: EpicStatus       # computed from sub-item states
    declared_status: EpicStatus      # as declared in BACKLOG.md frontmatter
    priority: Priority
    goal: str | None
    file: str                        # epic file path (relative, from BACKLOG.md)
    items: list[DerivedWorkItemState]
    total: int                       # len(items)
    done: int                        # count where state == completed


class ProjectState(BaseModel):
    epics: list[DerivedEpicState]
    standalone: list[DerivedWorkItemState]
```

`Path` in Pydantic v2: Pydantic natively handles `pathlib.Path` fields — no custom serializer needed. For JSON output, paths serialize to strings automatically.

### Component Details

#### `_scan_active_dirs(active_dir: Path, warnings) -> dict[str, Path]`

Scan `work/active/` for directories matching `WI-\d+_.*`.

```python
ACTIVE_DIR_RE = re.compile(r"^(WI-\d+)_(.+)$")
```

- Iterate `active_dir.iterdir()`, filter `is_dir()`
- Match each dirname against `ACTIVE_DIR_RE`
- Non-matching dirs are silently ignored (they're not work items)
- If `active_dir` doesn't exist, return empty dict (no warning — directory is optional)
- Returns `{wi_id: path}` — e.g., `{"WI-003": Path("work/active/WI-003_solar-model")}`

#### `_scan_completed_dirs(completed_dir: Path, warnings) -> dict[str, tuple[Path, str]]`

Scan `work/completed/` for directories matching `YYYYMMDD_WI-\d+_.*`.

```python
COMPLETED_DIR_RE = re.compile(r"^(\d{8})_(WI-\d+)_(.+)$")
```

- Same iteration pattern as active
- Returns `{wi_id: (path, date_str)}` — e.g., `{"WI-001": (Path("work/completed/20260205_WI-001_foundation/"), "20260205")}`
- If a WI-XXX appears in both active and completed, warn and prefer the active directory (something's wrong — the item wasn't cleaned up)

#### `_detect_stage(item_dir: Path) -> WorkItemStage`

Pure file existence check, evaluated in order (first match wins):

```python
def _detect_stage(item_dir: Path) -> WorkItemStage:
    if (item_dir / "plan.md").exists():
        return WorkItemStage.IMPLEMENTING
    if (item_dir / "design.md").exists():
        return WorkItemStage.DESIGNING
    if (item_dir / "spec.md").exists():
        return WorkItemStage.SPECCING
    return WorkItemStage.UNKNOWN
```

No frontmatter reading here — stage is purely file existence. This keeps stage detection fast and side-effect-free.

#### `_derive_item_state(item_dir, base_state, warnings) -> tuple[WorkItemStatus, WorkItemStage | None]`

For active items only — reads spec.md frontmatter and applies override logic.

```python
def _derive_item_state(
    item_dir: Path,
    warnings: list[ParseWarning],
) -> tuple[WorkItemStatus, WorkItemStage | None]:
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
    if not fm.data and spec_path.exists():
        # spec.md exists but frontmatter is empty/unparseable — already warned by parse_frontmatter
        pass
    elif not spec_path.exists():
        _warn(warnings, str(item_dir), "spec.md", "No spec.md found in active work item directory")

    stage = _detect_stage(item_dir)
    if stage == WorkItemStage.UNKNOWN:
        _warn(warnings, str(item_dir), "stage", "No recognized artifact files (spec.md, design.md, plan.md)")

    return WorkItemStatus.ACTIVE, stage
```

#### `_derive_epic_status(items: list[DerivedWorkItemState]) -> EpicStatus`

Pure function — no file I/O.

```python
def _derive_epic_status(items: list[DerivedWorkItemState]) -> EpicStatus:
    if not items:
        return EpicStatus.DRAFT

    states = {item.state for item in items}

    # All completed → epic completed
    if states == {WorkItemStatus.COMPLETED}:
        return EpicStatus.COMPLETED

    # All backlog → epic is still draft
    if states == {WorkItemStatus.BACKLOG}:
        return EpicStatus.DRAFT

    # Anything else (active, paused, abandoned, failed, or mix) → active
    return EpicStatus.ACTIVE
```

This handles the "2 completed + 1 abandoned = active" case correctly — `states` would be `{completed, abandoned}`, which is not `== {completed}`, so it returns `active`.

#### `resolve_work_item(project_root: Path, wi_id: str) -> Path`

Public utility for D4.4 operations. Raises `ValueError` on not-found or ambiguity (not warning-based — callers need a hard error).

```python
_WI_ID_RE = re.compile(r"^WI-\d+$")

def resolve_work_item(project_root: Path, wi_id: str) -> Path:
    # Normalize input: bare number → WI-XXX format
    if wi_id.isdigit():
        wi_id = f"WI-{int(wi_id):03d}"
    elif not _WI_ID_RE.match(wi_id):
        raise ValueError(f"Invalid work item ID format: '{wi_id}' (expected WI-XXX or a number)")

    candidates: list[Path] = []

    # Search active
    active_dir = project_root / "work" / "active"
    if active_dir.is_dir():
        for d in active_dir.iterdir():
            if d.is_dir() and d.name.startswith(f"{wi_id}_"):
                candidates.append(d)

    # Search completed (anchored on date prefix)
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
```

#### `derive_project_state(project_root: Path) -> ParseResult[ProjectState]`

Top-level aggregate function. The main entry point for D4.3 dashboard.

```python
def derive_project_state(project_root: Path) -> ParseResult[ProjectState]:
    warnings: list[ParseWarning] = []
    work_dir = project_root / "work"

    # Step 1: Parse BACKLOG.md
    backlog_result = parse_backlog(work_dir / "BACKLOG.md")
    warnings.extend(backlog_result.warnings)
    backlog = backlog_result.data

    # Step 2: Scan file system
    active_dirs = _scan_active_dirs(work_dir / "active", warnings)
    completed_dirs = _scan_completed_dirs(work_dir / "completed", warnings)

    # Build lookup: WI-XXX → epic name (from BACKLOG.md)
    backlog_epic_map: dict[str, str] = {}      # wi_id → epic name
    backlog_item_ids: set[str] = set()          # all WI-XXX in BACKLOG.md
    for epic in backlog.epics:
        for item in epic.items:
            backlog_epic_map[item.id] = epic.name
            backlog_item_ids.add(item.id)
    for sa in backlog.standalone:
        backlog_item_ids.add(sa.id)

    # Step 3: Derive state for each item
    all_items: dict[str, DerivedWorkItemState] = {}  # wi_id → derived state

    # 3a: Items with active directories
    for wi_id, dir_path in sorted(active_dirs.items()):
        name = ACTIVE_DIR_RE.match(dir_path.name).group(2)
        state, stage = _derive_item_state(dir_path, warnings)

        # Check for BACKLOG.md conflict
        if wi_id in backlog_item_ids:
            backlog_status = _get_backlog_status(backlog, wi_id)
            if backlog_status and backlog_status != state:
                _warn(warnings, str(dir_path / "spec.md"), "Status",
                      f"spec.md Status='{state.value}' overrides "
                      f"BACKLOG.md status='{backlog_status.value}' for {wi_id}")
        else:
            _warn(warnings, str(dir_path), wi_id,
                  f"Directory exists in work/active/ but {wi_id} not found in BACKLOG.md")

        all_items[wi_id] = DerivedWorkItemState(
            id=wi_id, name=name, state=state, stage=stage,
            epic=backlog_epic_map.get(wi_id),
            directory=dir_path, completed_date=None,
        )

    # 3b: Items with completed directories (skip if already seen as active)
    for wi_id, (dir_path, date_str) in sorted(completed_dirs.items()):
        if wi_id in all_items:
            continue  # already warned in _scan if both exist
        name = COMPLETED_DIR_RE.match(dir_path.name).group(3)

        all_items[wi_id] = DerivedWorkItemState(
            id=wi_id, name=name, state=WorkItemStatus.COMPLETED, stage=None,
            epic=backlog_epic_map.get(wi_id),
            directory=dir_path, completed_date=date_str,
        )

    # 3c: Backlog-only items (in BACKLOG.md, no directory)
    for epic in backlog.epics:
        for item in epic.items:
            if item.id not in all_items:
                all_items[item.id] = DerivedWorkItemState(
                    id=item.id, name=item.name,
                    state=WorkItemStatus.BACKLOG, stage=None,
                    epic=epic.name, directory=None, completed_date=None,
                )
    for sa in backlog.standalone:
        if sa.id not in all_items:
            all_items[sa.id] = DerivedWorkItemState(
                id=sa.id, name=sa.name,
                state=WorkItemStatus.BACKLOG, stage=None,
                epic=None, directory=None, completed_date=None,
            )

    # Step 4: Build epic-level summaries
    derived_epics: list[DerivedEpicState] = []
    for epic in backlog.epics:
        epic_items = [all_items[item.id] for item in epic.items if item.id in all_items]
        derived_status = _derive_epic_status(epic_items)

        if derived_status != epic.status:
            _warn(warnings, str(work_dir / "BACKLOG.md"), epic.name,
                  f"Epic '{epic.name}' declared status='{epic.status.value}' "
                  f"but derived status='{derived_status.value}'")

        derived_epics.append(DerivedEpicState(
            name=epic.name,
            derived_status=derived_status,
            declared_status=epic.status,
            priority=epic.priority,
            goal=epic.goal,
            file=epic.file,
            items=sorted(epic_items, key=lambda i: i.id),
            total=len(epic_items),
            done=sum(1 for i in epic_items if i.state == WorkItemStatus.COMPLETED),
        ))

    # Step 5: Build standalone list
    standalone_ids = {sa.id for sa in backlog.standalone}
    orphan_ids = set(all_items.keys()) - backlog_item_ids
    standalone_items = [
        all_items[sa.id] for sa in backlog.standalone if sa.id in all_items
    ] + [
        all_items[wi_id] for wi_id in sorted(orphan_ids)
        if all_items[wi_id].epic is None  # orphans without epic assignment
    ]

    return ParseResult(
        data=ProjectState(
            epics=derived_epics,
            standalone=sorted(standalone_items, key=lambda i: i.id),
        ),
        warnings=warnings,
    )
```

#### `_get_backlog_status(backlog: BacklogData, wi_id: str) -> WorkItemStatus | None`

Small helper to look up a WI-XXX's declared status in BACKLOG.md:

```python
def _get_backlog_status(backlog: BacklogData, wi_id: str) -> WorkItemStatus | None:
    for epic in backlog.epics:
        for item in epic.items:
            if item.id == wi_id:
                return item.status
    for sa in backlog.standalone:
        if sa.id == wi_id:
            return sa.status
    return None
```

### Error Handling

| Scenario | Behavior |
|----------|----------|
| `work/` doesn't exist | `parse_backlog` returns empty BacklogData with warning; dir scans return empty dicts. Result: empty ProjectState with warnings. |
| `work/active/` doesn't exist | `_scan_active_dirs` returns empty dict, no warning (optional dir) |
| spec.md missing in active dir | `parse_frontmatter` returns `{}` with warning; item defaults to `active` state; `_detect_stage` returns `UNKNOWN` with warning |
| spec.md has invalid Status value | Value doesn't match override cases → falls through to default `active` + stage detection. No explicit warning needed (unrecognized values are harmless). |
| BACKLOG.md ↔ spec.md conflict | spec.md wins; warning emitted naming both values |
| WI-XXX in both active and completed dirs | Warning emitted; active directory preferred |
| Orphaned directory (not in BACKLOG.md) | Included in results with warning; appears in standalone list |

### Module Exports

Update `__init__.py` to export:
- `WorkItemStage` (enum)
- `DerivedWorkItemState`, `DerivedEpicState`, `ProjectState` (models)
- `derive_project_state`, `resolve_work_item` (functions)

---

## Potential Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Large directories slow down scanning | Low | `iterdir()` is lazy; typical projects have <50 work items. Not a concern. |
| Regex mismatch on unusual directory names | Low | Regexes are strict (`WI-\d+_`, `\d{8}_WI-\d+_`). Non-matching dirs are silently skipped. |
| Pydantic `Path` serialization in JSON output | Low | Pydantic v2 handles Path natively. `model_dump(mode="json")` converts to string. |
| `resolve_work_item` raises ValueError — callers must handle | Low | This is the correct contract for an operation utility. D4.4 operations catch and report. Dashboard uses `derive_project_state` which doesn't call `resolve_work_item`. |

---

## Validation Approach

### Test Structure (`tests/test_pm_state.py`)

```
class TestScanActiveDirs
    test_normal_dirs            — 2 valid WI dirs → both found
    test_empty_dir              — empty work/active/ → empty dict
    test_missing_dir            — work/active/ doesn't exist → empty dict
    test_non_matching_ignored   — dirs like "notes/" or "WI_bad" → skipped

class TestScanCompletedDirs
    test_normal_dirs            — valid YYYYMMDD_WI-XXX_name dirs
    test_date_prefix_anchored   — dir with WI-like substring in name → not matched
    test_missing_dir            — work/completed/ doesn't exist → empty dict

class TestDetectStage
    test_spec_only              → speccing
    test_spec_and_design        → designing
    test_spec_design_plan       → implementing
    test_spec_and_plan          → implementing (design skipped)
    test_no_artifacts           → unknown
    test_design_only            → designing (unusual but valid)

class TestDeriveItemState
    test_active_default         — spec.md Status: active → active
    test_paused_override        — spec.md Status: paused → paused
    test_abandoned_override     — spec.md Status: abandoned → abandoned
    test_failed_override        — spec.md Status: failed → failed
    test_completed_override     — spec.md Status: completed → completed, no stage
    test_missing_spec           — no spec.md → active + unknown stage + warning
    test_malformed_frontmatter  — bad YAML → active + warning

class TestDeriveEpicStatus
    test_no_items               → draft
    test_all_backlog            → draft
    test_one_active             → active
    test_all_completed          → completed
    test_completed_and_abandoned → active
    test_completed_and_backlog  → active (not all completed)

class TestResolveWorkItem
    test_active_match           — WI-003 in active → found
    test_completed_match        — WI-001 in completed → found
    test_bare_number            — "3" → WI-003 → found
    test_not_found              — raises ValueError
    test_ambiguous              — raises ValueError with candidates
    test_invalid_format         — "bad" → raises ValueError

class TestDeriveProjectState
    test_empty_project          — no work/ dir → empty ProjectState
    test_backlog_only           — items in BACKLOG.md, no dirs → all backlog
    test_mixed_states           — active, completed, backlog items
    test_orphaned_directory     — dir without BACKLOG.md entry → included + warning
    test_backlog_spec_conflict  — BACKLOG says active, spec says paused → paused + warning
    test_epic_state_derivation  — epic status derived from sub-items
    test_epic_status_mismatch   — declared ≠ derived → warning
    test_ap1_empty_backlog      — BACKLOG.md with epics:[] standalone:[] → empty state
```

Each test creates a temp directory structure using `tmp_path`, writes BACKLOG.md frontmatter and spec.md files as needed, and asserts on the returned `ParseResult`.

---

## Integration Strategy

- **D4.3 (dashboard)** calls `derive_project_state(root)` and formats `ProjectState` into markdown
- **D4.4 (operations)** calls `resolve_work_item(root, wi_id)` for path resolution in close-item, impact-query, etc.
- **D4.5 (CLI)** wires `derive_project_state` to `agentic-mbse status` and `resolve_work_item` to `agentic-mbse pm` subcommands

No changes to D4.1 code. State derivation is a pure consumer of the parser API.

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`

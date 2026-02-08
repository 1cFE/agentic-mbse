# Design: D4.3 — Dashboard Generator

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02 17:06:15 UTC
**Branch:** revamp-architecture
**Commit:** b31c015

## Overview

A single-module rendering layer that composes D4.1 parsers and D4.2 state derivation into a plain-markdown dashboard. No architectural decisions required — the module is a pure function from file system state to markdown string.

## Related Artifacts

- **Spec:** `.project/active/d4.3-dashboard/spec.md`
- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.3 section)
- **D4.1 Parsers:** `src/agentic_mbse/pm/parser.py` (complete)
- **D4.2 State:** `src/agentic_mbse/pm/state.py` (in progress)
- **Types:** `src/agentic_mbse/pm/types.py`
- **Concept:** `.project/concepts/architecture-redesign/workflows.md` § 4.3

## Research Findings

### Parser Signatures (parser.py)

All parsers return `ParseResult[T]` and handle missing files gracefully:

| Parser | Signature | Missing file behavior |
|--------|-----------|----------------------|
| `parse_requirements(path)` | `→ ParseResult[list[RequirementEntry]]` | Empty list + warning |
| `parse_validation_matrix(path)` | `→ ParseResult[list[ValidationEntry]]` | Empty list + warning |
| `derive_project_state(root)` | `→ ParseResult[ProjectState]` | Empty epics/standalone + warnings |

### Available Type Fields

**`DerivedWorkItemState`** (types.py:215-222):
- `id: str` — WI-XXX
- `name: str` — descriptive name from directory
- `state: WorkItemStatus` — backlog/active/paused/abandoned/failed/completed
- `stage: WorkItemStage | None` — speccing/designing/implementing/unknown (only when active)
- `directory: Path | None` — resolved path or None for backlog-only
- `completed_date: str | None` — YYYYMMDD from completed directory name

**`DerivedEpicState`** (types.py:225-234) — dashboard-relevant fields only:
- `name: str`, `derived_status: EpicStatus`, `priority: Priority`
- `items: list[DerivedWorkItemState]`, `total: int`, `done: int`
- (Also has `declared_status`, `goal`, `file` — not used by dashboard)

**`RequirementEntry`** (types.py:127-133):
- `enforcement: str` — empty/"-" means not machine-enforceable
- `validation_method: str` — empty/"-" means no validation method

**`ValidationEntry`** (types.py:136-144):
- `id: str` (SV-XXX), `description: str`, `status: VerificationStatus` (passing/failing/pending)

### Existing Patterns

**`ParseResult` / `ParseWarning` pattern** — established in D4.1, used consistently in D4.2. Dashboard follows the same pattern: return data + accumulated warnings.

**Test pattern** (test_pm_state.py): Helper functions (`_write_backlog_raw`, `_make_active`, `_write_spec`), `tmp_path` fixture, test classes per feature, assertions on `.data` and `.warnings`.

### Completed Date Format

`DerivedWorkItemState.completed_date` stores `YYYYMMDD` (from directory name like `20260215_WI-001_foundation`). The spec's display format is `completed YYYY-MM-DD`. The dashboard must reformat: insert hyphens into the 8-digit string.

## Proposed Design

### New Type: `DashboardResult`

Add to `src/agentic_mbse/pm/types.py`:

```python
class DashboardResult(BaseModel):
    markdown: str
    warnings: list[ParseWarning] = Field(default_factory=list)
```

This parallels `ParseResult[T]` but with a fixed `markdown: str` field instead of generic `data: T`. Using a dedicated type rather than `ParseResult[str]` makes the API self-documenting.

### Module: `src/agentic_mbse/pm/dashboard.py`

One public function, four private renderers.

#### Public API

```python
def generate_dashboard(project_root: Path) -> DashboardResult:
```

Orchestrates the three data sources and composes the output:

1. Call `derive_project_state(project_root)` → `ParseResult[ProjectState]`
2. Call `parse_requirements(project_root / "modeling_project" / "REQUIREMENTS.md")` → `ParseResult[list[RequirementEntry]]`
3. Call `parse_validation_matrix(project_root / "modeling_project" / "VALIDATION_MATRIX.md")` → `ParseResult[list[ValidationEntry]]`
4. Accumulate all warnings from steps 1-3
5. Call each renderer, concatenate results with blank-line separators
6. Return `DashboardResult(markdown=..., warnings=...)`

#### Private Renderers

Each renderer is a pure function that takes parsed data and returns a markdown string. No I/O.

**`_render_header(project_root: Path) -> str`**

Returns `## Project: {project_root.name}\n`.

**`_render_work_items(state: ProjectState) -> str`**

Always renders the `### Work Items` section header first, then the body:

1. Start with `### Work Items\n`
2. If no epics and no standalone items → append `No work items.\n`
3. Else:
   - For each epic in `state.epics`:
     - Header line: `Epic: {name}  [{done}/{total} done]`
     - For each item (already sorted by ID from state derivation):
       - Format checkbox + name + dot-leader + state string
   - If standalone items exist:
     - Header: `Standalone:`
     - Same item formatting

**Item state string formatting**:

```python
def _format_item_status(item: DerivedWorkItemState) -> str:
    if item.state == WorkItemStatus.COMPLETED:
        date = _format_date(item.completed_date)  # YYYYMMDD → YYYY-MM-DD
        return f"completed {date}" if date else "completed"
    if item.state == WorkItemStatus.ACTIVE and item.stage:
        return f"active:{item.stage.value}"
    return item.state.value  # backlog, paused, abandoned, failed, active (no stage)
```

**Dot-leader alignment**: Compute the max name length within each group (epic or standalone). Pad each name to that width using dots. Minimum 2 dots between name and status. If a name exceeds the max width (shouldn't happen within a group, but defensively), use minimum 2 dots.

```python
def _format_item_line(name: str, status_str: str, completed: bool, pad_width: int) -> str:
    checkbox = "[x]" if completed else "[ ]"
    dots_needed = max(2, pad_width - len(name))
    dots = " " + "." * dots_needed + " "
    return f"  {checkbox} {name}{dots}{status_str}"
```

**`_render_requirements(entries: list[RequirementEntry], has_file: bool) -> str`**

Logic:
1. Header: `### Project Rules (REQUIREMENTS.md)`
2. If `not has_file` → `No requirements file found.`
3. Else compute metrics:
   - `total = len(entries)`
   - `with_validation = sum(1 for e in entries if e.validation_method.strip() not in ("", "-"))`
   - `enforceable = sum(1 for e in entries if e.enforcement.strip() not in ("", "-"))`
4. Format: `Total: {total} | With validation method: {with_validation} | Machine-enforceable: {enforceable}`

The `has_file` flag distinguishes "file missing" from "file exists but empty table" (which shows `Total: 0 | ...`). The caller determines this by checking whether `parse_requirements` produced a file-not-found warning.

**`_render_validation(entries: list[ValidationEntry], has_file: bool) -> str`**

Logic:
1. Header: `### Validation Status (VALIDATION_MATRIX.md)`
2. If `not has_file` → `No validation matrix found.`
3. Else compute metrics:
   - Count by `VerificationStatus` enum values
   - `total = len(entries)`
4. Format summary line: `Total: {total} | Passing: {passing} | Failing: {failing} | Pending: {pending}`
5. If `failing > 0`, append individual lines: `Failing: {id} ({description})`

### Detecting "File Not Found" vs "Empty File"

The parsers return empty lists for both missing files and empty tables, but add a `"File not found"` warning only when the file is missing. The dashboard checks for this specific warning pattern to determine `has_file`:

```python
def _has_file_not_found(warnings: list[ParseWarning], path: str) -> bool:
    return any(w.message.startswith("File not found") and path in w.file for w in warnings)
```

This avoids adding parser-level API changes. The `generate_dashboard` function calls the parser, checks warnings, and passes the `has_file` boolean to the renderer.

**Malformed file behavior**: When a file exists but contains unparseable content, the parsers return an empty list with parse warnings (not a "File not found" warning). The dashboard treats this the same as an empty table — `has_file` is true, so metrics render as `Total: 0 | ...` and the parse warnings accumulate in `DashboardResult.warnings` for the caller to report.

### File Changes

| File | Change |
|------|--------|
| `src/agentic_mbse/pm/dashboard.py` | **New** — `generate_dashboard` + 4 private renderers |
| `src/agentic_mbse/pm/types.py` | **Add** `DashboardResult` class |
| `src/agentic_mbse/pm/__init__.py` | **Add** exports for `generate_dashboard`, `DashboardResult` |
| `tests/test_pm_dashboard.py` | **New** — test suite |

### Data Flow

```
project_root
    │
    ├─► derive_project_state(root) ──► ProjectState ──► _render_work_items()
    │       (reads BACKLOG.md, work/active/, work/completed/, spec.md files)
    │
    ├─► parse_requirements(modeling_project/REQUIREMENTS.md) ──► [RequirementEntry] ──► _render_requirements()
    │
    └─► parse_validation_matrix(modeling_project/VALIDATION_MATRIX.md) ──► [ValidationEntry] ──► _render_validation()

All warnings accumulated ──► DashboardResult.warnings
All markdown concatenated ──► DashboardResult.markdown
```

### Error Handling

No new error handling needed. All parsers already return `ParseResult` with graceful degradation. The dashboard:

- Never raises exceptions (parsers handle all file errors)
- Accumulates all warnings into the result
- Renders whatever data it receives (partial parse = partial dashboard content)
- Always produces valid markdown (worst case: the empty-project output)

## Testing Strategy

### Test File: `tests/test_pm_dashboard.py`

Reuses the helper pattern from `test_pm_state.py` (`_write_backlog_raw`, `_make_active`, `_write_spec`, etc.) plus adds helpers for writing REQUIREMENTS.md and VALIDATION_MATRIX.md tables.

### Test Classes

**`TestRenderHeader`** (2 tests):
- Project name from directory
- Directory name with special characters

**`TestRenderWorkItems`** (5 tests):
- No items → "No work items."
- Single epic with mixed states
- Multiple epics + standalone
- All completed epic
- Zero-item epic (`[0/0 done]`)

**`TestRenderRequirements`** (3 tests):
- File not found → fallback message
- Empty table → `Total: 0 | ...`
- Populated table → correct counts

**`TestRenderValidation`** (4 tests):
- File not found → fallback message
- All passing → no failing lines
- Mix with failing → individual failing lines listed
- Empty table → `Total: 0 | ...`

**`TestGenerateDashboard`** (4 tests — integration):
- Empty project (AP-1) → full empty-state output
- Full project with all three sections populated
- Missing REQUIREMENTS.md + VALIDATION_MATRIX.md → graceful degradation
- Partial parse failure → warnings accumulated, renderable items still shown

### Test Helpers (new)

```python
def _write_requirements(mp_dir: Path, rows: list[tuple[str, str, str, str, str]]) -> None:
    """Write REQUIREMENTS.md with table rows (id, req, source, enforcement, validation_method)."""

def _write_validation_matrix(mp_dir: Path, rows: list[tuple[str, str, str, str, str, str, str, str, str]]) -> None:
    """Write VALIDATION_MATRIX.md with table rows."""
```

## Potential Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| D4.2 state derivation not yet merged — dashboard depends on it | Low | D4.2 is on the same branch and types are already in `types.py`. Dashboard can be implemented and tested against the current `state.py`. |
| Dot-leader alignment looks bad with very long names | Low | Minimum 2-dot floor prevents collision. Alignment is cosmetic — worst case is inconsistent dot counts. |
| `completed_date` format assumption (YYYYMMDD) is wrong | Low | Verified: `COMPLETED_DIR_RE` in state.py:32 captures exactly 8 digits. Reformatting to YYYY-MM-DD is safe. |
| Parser warning message format changes break `has_file` detection | Low | The "File not found" prefix is a stable convention used by all 8 parsers in parser.py. Could be hardened later with a warning code enum, but not needed now. |

## Integration Strategy

- Dashboard is consumed by D4.5 (`agentic-mbse status` CLI subcommand) which prints `result.markdown` to stdout and `result.warnings` to stderr
- Dashboard is consumed by the `status` operation in D4.4 (which delegates to `generate_dashboard`)
- Dashboard is consumed by the `/status` command (Epic 3) which calls `agentic-mbse status`
- No other modules are affected

## Validation Approach

1. **Unit tests**: Each renderer tested in isolation with constructed data
2. **Integration tests**: `generate_dashboard()` called with real `tmp_path` project structures
3. **AP-1 verification**: Explicit test for empty project output matching the spec exactly
4. **Type checking**: `uv run mypy src/agentic_mbse/pm/` must pass
5. **Linting**: `uv run ruff check src/agentic_mbse/pm/` must pass
6. **Regression**: `uv run pytest tests/` (all existing tests still pass)

---

**Next Step:** After approval → `/_my_implement`

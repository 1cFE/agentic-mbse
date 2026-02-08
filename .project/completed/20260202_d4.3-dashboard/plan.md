# Implementation Plan: D4.3 — Dashboard Generator

**Status:** Complete
**Created:** 2026-02-02 17:15:29 UTC
**Last Updated:** 2026-02-02

## Source Documents
- **Spec:** `.project/active/d4.3-dashboard/spec.md`
- **Design:** `.project/active/d4.3-dashboard/design.md` ← See here for component details, function signatures, data flow, type fields

## Implementation Strategy

**Phasing Rationale:**
Two phases. The module is ~150 lines of pure rendering logic over tested infrastructure (D4.1 parsers, D4.2 state derivation). No new patterns, no I/O in renderers, no architectural risk. Phase 1 writes all code and tests. Phase 2 runs quality gates.

**Overall Validation Approach:**
- Test-first: write test file before dashboard.py
- Unit tests for each renderer with constructed data
- Integration tests for `generate_dashboard` with `tmp_path` project structures
- Quality gates: mypy, ruff, full regression suite

---

## Phase 1: Implementation + Tests

### Goal
Implement the entire dashboard module (type, renderers, public API, exports) and full test suite. This is one coherent unit — the renderers are pure functions with no dependencies on each other, so there's no value in splitting them.

### Test Stencil (Write This First)
```python
class TestRenderWorkItems:
    def test_no_items(self) -> None:
        state = ProjectState(epics=[], standalone=[])
        result = _render_work_items(state)
        assert "### Work Items" in result
        assert "No work items." in result

    def test_epic_with_mixed_states(self, tmp_path: Path) -> None:
        # Build ProjectState with completed + active + backlog items
        # Assert epic header, progress counter, checkbox states, dot-leaders

class TestGenerateDashboard:
    def test_empty_project(self, tmp_path: Path) -> None:
        result = generate_dashboard(tmp_path)
        assert "## Project:" in result.markdown
        assert "No work items." in result.markdown
        assert "No requirements file found." in result.markdown
        assert "No validation matrix found." in result.markdown
```

### Changes Required

**See `design.md` for:**
- `DashboardResult` type definition → `design.md#new-type-dashboardresult`
- Public API signature → `design.md#public-api`
- Renderer logic → `design.md#private-renderers`
- File-not-found detection → `design.md#detecting-file-not-found-vs-empty-file`
- Test class/helper design → `design.md#testing-strategy`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pm_dashboard.py` (NEW — write first)
- [x] Create test file with imports
- [x] Add helpers: `_write_backlog_raw`, `_make_active`, `_write_spec` (reuse pattern from test_pm_state.py)
- [x] Add helpers: `_write_requirements`, `_write_validation_matrix`
- [x] `TestRenderHeader` — 2 tests (normal name, special characters)
- [x] `TestRenderWorkItems` — 5 tests (empty, mixed epic, multi-epic+standalone, all-completed, zero-item epic)
- [x] `TestRenderRequirements` — 3 tests (no file, empty table, populated)
- [x] `TestRenderValidation` — 4 tests (no file, all passing, mix with failing, empty)
- [x] `TestGenerateDashboard` — 4 tests (empty project AP-1, full project, missing files, warnings accumulation)

#### 2. Type Addition
**File:** `src/agentic_mbse/pm/types.py:240` (MODIFY — append after `ProjectState`)
- [x] Add `DashboardResult` class (see `design.md#new-type-dashboardresult`)

#### 3. Dashboard Module
**File:** `src/agentic_mbse/pm/dashboard.py` (NEW)
- [x] `_format_date()` — YYYYMMDD → YYYY-MM-DD
- [x] `_format_item_status()` — state+stage to display string
- [x] `_format_item_line()` — checkbox + name + dot-leader + status
- [x] `_has_file_not_found()` — check warnings for missing file
- [x] `_render_header()` — project name from directory
- [x] `_render_work_items()` — epic groups + standalone, always with `### Work Items` header
- [x] `_render_requirements()` — metrics or fallback
- [x] `_render_validation()` — metrics + failing list or fallback
- [x] `generate_dashboard()` — orchestrator (see `design.md#public-api`)

#### 4. Module Exports
**File:** `src/agentic_mbse/pm/__init__.py` (MODIFY)
- [x] Add import: `from agentic_mbse.pm.dashboard import generate_dashboard`
- [x] Add import: `DashboardResult` to types import line
- [x] Add to `__all__`: `"generate_dashboard"`, `"DashboardResult"`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_pm_dashboard.py -v` → All ~18 tests pass
- [x] `uv run pytest tests/` → No regressions

**Manual:**
- [x] Read dashboard output for a populated test case — verify it looks like the spec's FR-6 example
- [x] Verify empty-project output matches spec exactly

**What We Know Works After This Phase:**
All rendering logic, all edge cases (empty project, missing files, partial failures, failing validations), and the public API contract.

---

## Phase 2: Quality Gates

### Goal
Run type checking and linting. Fix any issues found.

### Changes Required
No new code expected — only fixes if mypy/ruff flag issues.

- [x] `uv run mypy src/agentic_mbse/pm/` → passes
- [x] `uv run ruff check src/agentic_mbse/pm/` → passes
- [x] `uv run ruff format --check src/agentic_mbse/pm/` → passes
- [x] `uv run pytest tests/` → final confirmation

**What We Know Works After This Phase:**
Full deliverable complete. Ready for D4.5 (CLI wiring).

---

## Environment Setup

**See CLAUDE.md for full environment rules**

All commands use `uv run` prefix.

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If `derive_project_state` behavior differs from expected, tests will catch it immediately since we test against real `tmp_path` structures using the actual parsers and state derivation.
- **Phase 2**: mypy issues are likely to be minor type annotation fixes given the established patterns in parser.py and state.py.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Created `tests/test_pm_dashboard.py` — 18 tests across 5 classes with 6 helpers
- Added `DashboardResult` class to `src/agentic_mbse/pm/types.py:243`
- Created `src/agentic_mbse/pm/dashboard.py` — `generate_dashboard` + 4 renderers + 4 helpers
- Updated `src/agentic_mbse/pm/__init__.py` — added `generate_dashboard` and `DashboardResult` exports
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Fixed mypy `no-any-return` on `item.state.value` by wrapping in `str()`
- Ran `ruff format` on `dashboard.py` and `state.py` (whitespace adjustments)
**Issues:** None
**Deviations:** None

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**

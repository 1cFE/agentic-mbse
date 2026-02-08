# Spec: D4.3 — Dashboard Generator

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02 17:03:14 UTC
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-004 (PM Script Engine)
**Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` § 3B.1 dashboard items

---

## Business Goals

### Why This Matters

The dashboard is the primary user-facing output of the PM engine. It replaces agent-memory-based status reporting (P5) with a deterministic, testable function that renders project state as plain markdown. Without it, `agentic-mbse status` has nothing to produce, and the `/status` command (Epic 3) has no script to wrap.

### Success Criteria

- [ ] `generate_dashboard(project_root)` produces accurate markdown for any project state
- [ ] An empty project (freshly `agentic-mbse init`) produces a valid dashboard with "none" placeholders, not errors
- [ ] Missing structured files (REQUIREMENTS.md, VALIDATION_MATRIX.md) degrade gracefully — sections show "N/A" rather than crashing
- [ ] The output is deterministic: same file system state always produces identical markdown

### Priority

Third deliverable in Epic 4. Blocked by D4.2 (state derivation). Blocks D4.5 (CLI subcommands).

---

## Problem Statement

### Current State

D4.1 provides parsers for all structured project files. D4.2 provides `derive_project_state()` which returns a `ParseResult[ProjectState]` containing every work item's state, stage, and epic grouping. But there is no module that composes these into a human-readable dashboard. The `agentic-mbse status` CLI subcommand (D4.5) needs a function to call.

### Desired Outcome

A `src/agentic_mbse/pm/dashboard.py` module with a single public function `generate_dashboard(project_root)` that returns a `DashboardResult` containing rendered markdown and accumulated warnings. The output covers three sections: work items, project rules, and validation status.

---

## Scope

### In Scope

- New module: `src/agentic_mbse/pm/dashboard.py`
- Update: `src/agentic_mbse/pm/__init__.py` (export new public API)
- Update: `src/agentic_mbse/pm/types.py` (new result type if needed)
- Three dashboard sections:
  1. Work Items — epic progress, per-item state/stage, standalone items
  2. Project Rules — REQUIREMENTS.md metrics
  3. Validation Status — VALIDATION_MATRIX.md metrics with failing items listed
- Project name derived from project root directory name
- Test suite: `tests/test_pm_dashboard.py`
- Test fixtures: additions to `tests/fixtures/pm/` as needed

### Out of Scope

- `blocked_by` display on work items (data model does not support it yet)
- Phase display (`phase X/Y` from plan.md) — deferred enhancement
- JSON output format (`--json` flag — D4.5 CLI concern)
- CLI wiring (`agentic-mbse status` subcommand — D4.5)
- `/status` command prompt (Epic 3)
- File writing or mutation (D4.4 operations)
- Model analysis metrics (Q14 — stays agent-driven)

### Edge Cases & Considerations

- **Empty project**: No `work/` directories, no REQUIREMENTS.md, no VALIDATION_MATRIX.md. All sections render with "none" or zero-count placeholders.
- **Missing REQUIREMENTS.md**: Project Rules section shows "No requirements file found." instead of metrics.
- **Missing VALIDATION_MATRIX.md**: Validation Status section shows "No validation matrix found." instead of metrics.
- **Partial parse failures**: If state derivation returns warnings (e.g., bad spec.md in one item), the dashboard MUST still render all items it could parse. Warnings are returned in the result, not displayed inline in the dashboard.
- **Zero items in an epic**: Epic appears with `[0/0 done]` — valid state for a draft epic.
- **All items completed**: Epic shows full progress, all checkboxes filled.

---

## Requirements

### Functional Requirements

#### FR-1: Dashboard Entry Point

The module MUST provide a `generate_dashboard(project_root: Path) -> DashboardResult` function that:

1. Calls `derive_project_state(project_root)` to get `ParseResult[ProjectState]`
2. Calls `parse_requirements(...)` and `parse_validation_matrix(...)` for metrics sections
3. Renders all three sections into a single markdown string
4. Returns `DashboardResult` containing the rendered markdown and accumulated warnings from all sub-operations

#### FR-2: Project Header

The dashboard MUST begin with:

```
## Project: {name}
```

Where `{name}` is the project root directory name (e.g., `Path("/home/user/fusion-tea").name` → `"fusion-tea"`).

#### FR-3: Work Items Section

The Work Items section MUST display:

- Each epic as a group with name and progress counter `[done/total done]`
- Each work item within an epic as a line with checkbox, name, and state
- Standalone items in a separate "Standalone" group
- Items sorted by WI-XXX ID within each group

**Item display format**:

| State | Display |
|-------|---------|
| `completed` | `[x] {name} .................. completed {YYYY-MM-DD}` |
| `active` (with stage) | `[ ] {name} .................. active:{stage}` |
| `active` (unknown stage) | `[ ] {name} .................. active` |
| `paused` | `[ ] {name} .................. paused` |
| `abandoned` | `[ ] {name} .................. abandoned` |
| `failed` | `[ ] {name} .................. failed` |
| `backlog` | `[ ] {name} .................. backlog` |

The dot-leader between name and state is cosmetic alignment. The module SHOULD pad names to a consistent width within each epic group for readability but MUST NOT fail if names vary in length.

When there are no work items at all, the section MUST display: `No work items.`

#### FR-4: Project Rules Section (REQUIREMENTS.md Metrics)

The Project Rules section MUST display three metrics from parsed REQUIREMENTS.md:

```
### Project Rules (REQUIREMENTS.md)
Total: N | With validation method: N | Machine-enforceable: N
```

- **Total**: Count of all `RequirementEntry` rows
- **With validation method**: Count where `validation_method` is not empty/"-"
- **Machine-enforceable**: Count where `enforcement` is not empty/"-"

If REQUIREMENTS.md does not exist or cannot be parsed, display:

```
### Project Rules (REQUIREMENTS.md)
No requirements file found.
```

#### FR-5: Validation Status Section (VALIDATION_MATRIX.md Metrics)

The Validation Status section MUST display metrics from parsed VALIDATION_MATRIX.md:

```
### Validation Status (VALIDATION_MATRIX.md)
Total: N | Passing: N | Failing: N | Pending: N
```

If any entries have status `failing`, they MUST be listed individually below the summary:

```
Failing: SV-XXX (description)
Failing: SV-YYY (description)
```

If VALIDATION_MATRIX.md does not exist or cannot be parsed, display:

```
### Validation Status (VALIDATION_MATRIX.md)
No validation matrix found.
```

#### FR-6: Empty Project Handling (AP-1)

The dashboard MUST produce valid output on a freshly initialized project with no content:

```
## Project: {name}

### Work Items
No work items.

### Project Rules (REQUIREMENTS.md)
No requirements file found.

### Validation Status (VALIDATION_MATRIX.md)
No validation matrix found.
```

#### FR-7: Warning Accumulation

The dashboard function MUST collect warnings from all sub-operations (state derivation, requirements parsing, validation matrix parsing) into the returned `DashboardResult.warnings` list. Warnings are NOT rendered into the dashboard markdown itself — they are available to the caller (e.g., CLI can print them to stderr).

### Non-Functional Requirements

- **NFR-1: Determinism** — Same file system state MUST produce identical markdown output. No randomness, no timestamp-dependent behavior.
- **NFR-2: No side effects** — The dashboard function MUST NOT write to any file, modify global state, or print to stdout/stderr.
- **NFR-3: Dependencies** — Dashboard uses D4.1 parsers, D4.2 state derivation, and stdlib (`pathlib`). No new external dependencies.
- **NFR-4: Rendering** — Output MUST be valid GitHub-flavored markdown that renders correctly in both terminal display and IDE preview.

---

## Acceptance Criteria

### Core Functionality

- [ ] `generate_dashboard(root)` returns `DashboardResult` with rendered markdown and warnings
- [ ] Header shows project name from directory
- [ ] Work Items section shows epics with progress counters
- [ ] Work Items section shows per-item state and stage
- [ ] Completed items show completion date
- [ ] Standalone items appear in their own group
- [ ] Project Rules section shows requirement metrics
- [ ] Validation Status section shows validation metrics
- [ ] Failing validation items listed individually

### Empty-State Verification (AP-1)

- [ ] Empty project (no `work/` directories) → valid dashboard with "No work items." etc.
- [ ] Missing REQUIREMENTS.md → "No requirements file found."
- [ ] Missing VALIDATION_MATRIX.md → "No validation matrix found."
- [ ] Project with BACKLOG.md but zero items → "No work items."

### Graceful Degradation

- [ ] If state derivation produces warnings, dashboard still renders all parseable items
- [ ] If REQUIREMENTS.md is malformed, section shows fallback message and warnings accumulate
- [ ] If VALIDATION_MATRIX.md is malformed, section shows fallback message and warnings accumulate

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] New tests pass (`uv run pytest tests/test_pm_dashboard.py`)
- [ ] `uv run mypy src/agentic_mbse/pm/` passes with no errors
- [ ] `uv run ruff check src/agentic_mbse/pm/` passes
- [ ] Dashboard tests cover: empty project, single item, multiple epics + standalone, missing structured files, failing validation items

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.3 section)
- **Depends on:** `.project/active/d4.1-parsers/` (parsers — complete)
- **Depends on:** `.project/active/d4.2-state-derivation/` (state derivation — in progress)
- **Concept:** `.project/concepts/architecture-redesign/workflows.md` § 4.3
- **Design:** `.project/active/d4.3-dashboard/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`

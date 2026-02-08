# Spec: D4.2 — State Derivation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02 16:29:12 UTC
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-004 (PM Script Engine)
**Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` § 3B.1 state items

---

## Business Goals

### Why This Matters

The dashboard (D4.3) and several AP-7 operations (D4.4: close-item, impact-query) cannot function without knowing the state of work items and epics. State derivation is the bridge between raw file parsing (D4.1) and meaningful project status. Without it, `agentic-mbse status` cannot produce accurate output, and P5 (PM depends on agent memory) remains unsolved.

### Success Criteria

- [ ] Calling a state derivation function with a project root returns an accurate, deterministic snapshot of every work item's state, stage, and parent epic
- [ ] Malformed or missing files in individual work items produce warnings but don't block derivation of other items
- [ ] An empty project (freshly `agentic-mbse init`) returns empty collections, not errors
- [ ] Work item name resolution reliably maps WI-XXX to directory paths across active and completed directories

### Priority

Second deliverable in Epic 4. Blocks D4.3 (dashboard) and partially blocks D4.4 (close-item needs `resolve_work_item`, impact-query needs state context).

---

## Problem Statement

### Current State

D4.1 provides parsers that can read individual structured files (BACKLOG.md frontmatter, spec.md frontmatter, etc.). But there is no module that combines these reads with file system structure to derive the overall state of work items and epics. The state of any work item currently exists only in an agent's conversational context — not programmatically accessible.

### Desired Outcome

A `src/agentic_mbse/pm/state.py` module that provides deterministic work item state derivation, stage detection, epic state derivation, and work item name resolution. All state queries are tolerant: partial results with warnings when individual items have parse errors.

---

## Scope

### In Scope

- New module: `src/agentic_mbse/pm/state.py`
- Update: `src/agentic_mbse/pm/__init__.py` (export new public API)
- Update: `src/agentic_mbse/pm/types.py` (new models for derived state)
- Four capabilities:
  1. Two-step work item state derivation (file system → frontmatter override)
  2. Stage detection for active items (three stages: speccing, designing, implementing)
  3. Epic state derivation from sub-item states
  4. Work item name resolution (WI-XXX → directory path)
- Test suite: `tests/test_pm_state.py`
- Test fixtures: additions to `tests/fixtures/pm/` (work item directories with stage artifacts)

### Out of Scope

- File writing or mutation (D4.4 operations)
- Dashboard rendering (D4.3 — consumes state derivation output)
- CLI integration (D4.5)
- review.md tracking (DD-3: review.md is not a PM-tracked stage)
- Git-based state tracking (deferred per Q16)
- A "planning" stage — once plan.md exists, the item is implementing (see DD-D4.2-1)

### Edge Cases & Considerations

- **Empty project**: `work/active/` and `work/completed/` may not exist yet. Return empty state, no errors.
- **Orphaned directories**: A directory in `work/active/WI-003_foo/` with no matching entry in BACKLOG.md. The item exists on the file system — state derivation SHOULD include it with a warning about the BACKLOG.md mismatch.
- **BACKLOG.md ↔ spec.md conflict**: Per frontmatter-schemas.md § 5 note 4, spec.md wins. State derivation MUST produce a warning when BACKLOG.md and spec.md disagree on status.
- **Missing spec.md in active directory**: An active directory exists but contains no spec.md. State derivation SHOULD report the item as active with stage "unknown" and a warning.
- **Ambiguous WI-XXX resolution**: Multiple directories match the same WI-XXX pattern. Return an error with the candidate list.
- **Completed items with date-prefix variations**: `work/completed/` directories use `YYYYMMDD_{WI-XXX}_{name}/` format. The date prefix varies per item.

---

## Design Decisions

### DD-D4.2-1: Stage Detection Logic (No "Planning" Stage)

**Decision**: Stage detection has three stages, not four. Stages do not assume linear artifact accumulation — users may skip stages per AP-5 (toolkit, not pipeline). Detection checks from the latest possible artifact backward.

**Rationale**: In the current command pipeline, `/plan-model` creates plan.md and the user proceeds to `/implement-model`. Planning is a transient activity that ends when plan.md is written — there is no observable "planning" state from the PM engine's perspective. The `audit-models` command will separately be responsible for marking plan.md Status as `complete`.

Additionally, stages can be skipped. A user might go directly from spec to plan (skipping design), or even have only a spec.md and start implementing. The stage detection must not require all prior artifacts to exist.

**Stage detection algorithm** (evaluated in order, first match wins):

1. If `spec.md` Status = `completed` → work item state is **completed** (not a stage — handled by FR-1 frontmatter override)
2. If `plan.md` exists → stage = **implementing**
3. Else if `design.md` exists → stage = **designing**
4. Else if `spec.md` exists → stage = **speccing**
5. Else (no recognized artifacts) → stage = **unknown** + warning

| Stage | Condition |
|-------|-----------|
| `speccing` | `spec.md` exists, no `design.md`, no `plan.md` |
| `designing` | `design.md` exists, no `plan.md` (spec.md may or may not exist) |
| `implementing` | `plan.md` exists (design.md and spec.md may or may not exist) |

### DD-D4.2-2: spec.md Wins on Conflict

**Decision**: When BACKLOG.md and spec.md report different statuses for the same WI-XXX, the state derivation module uses spec.md and produces a warning about the discrepancy.

**Rationale**: Per frontmatter-schemas.md § 5 note 4, spec.md is the authoritative source for work item state. BACKLOG.md may be stale.

---

## Requirements

### Functional Requirements

#### FR-1: Two-Step Work Item State Derivation

The module MUST derive work item state using this two-step process:

**Step 1 — File system scan**:
- Scan `work/active/` for directories matching `{WI-XXX}_{name}/` → state = `active`
- Scan `work/completed/` for directories matching `YYYYMMDD_{WI-XXX}_{name}/` → state = `completed`
- Cross-reference with BACKLOG.md: items listed in BACKLOG.md but with no directory → state = `backlog`
- Items with a directory but not in BACKLOG.md → include with a warning (orphaned item)

**Step 2 — Frontmatter override** (active items only):
- Read `spec.md` YAML frontmatter from the work item directory
- If Status is `completed`, override state to `completed` (item finished but not yet archived to `work/completed/`)
- If Status is `paused`, `abandoned`, or `failed`, that overrides the `active` state
- If Status is `active`, keep state as `active` and proceed to stage detection (FR-2)
- If spec.md is missing or unparseable, keep state as `active` with a warning

#### FR-2: Stage Detection

For active items (state = `active` after override), the module MUST determine stage by checking from the latest possible artifact backward. Stages do not require all prior artifacts to exist (AP-5: toolkit, not pipeline — users may skip stages).

**Detection order** (first match wins):

1. `plan.md` exists → stage = `implementing`
2. `design.md` exists (no `plan.md`) → stage = `designing`
3. `spec.md` exists (no `design.md`, no `plan.md`) → stage = `speccing`
4. No recognized artifacts → stage = `unknown` + warning

This means:
- A work item with only spec.md and plan.md (design skipped) → `implementing`
- A work item with only spec.md → `speccing`
- A work item with only design.md (unusual but valid) → `designing`

#### FR-3: Epic State Derivation

The module MUST derive epic state from sub-item states:

| Epic State | Condition |
|------------|-----------|
| `draft` | All sub-items are `backlog`, or there are no sub-items |
| `active` | At least one sub-item has a non-terminal state (`active`, `paused`) OR at least one sub-item has a terminal-unsuccessful state (`abandoned`, `failed`) while others are not all `completed` |
| `completed` | All sub-items have state `completed` (and there is at least one sub-item) |

**Note on abandoned/failed items**: An epic with 2 completed and 1 abandoned items is `active`, not `completed`. This is intentional — the epic needs human attention to decide whether to re-scope, replace the abandoned item, or accept the epic as done at reduced scope. An epic is only `completed` when every sub-item succeeded.

Epic state is derived by cross-referencing BACKLOG.md epic entries with the file-system-derived work item states. An epic with zero items is `draft`.

The module SHOULD produce a warning when the derived epic state differs from the BACKLOG.md frontmatter `status` field for that epic.

#### FR-4: Work Item Name Resolution

The module MUST provide a `resolve_work_item(project_root, wi_id)` function:

- **Input**: Project root path, WI-XXX identifier (string)
- **Output**: Resolved directory path, or error

Resolution order:
1. Search `work/active/` for directories matching `{wi_id}_*/`
2. Search `work/completed/` for directories matching `[0-9]{8}_{wi_id}_*/` (anchored on the YYYYMMDD date prefix to prevent false positives from work item names that happen to contain WI-XXX-like substrings)
3. If exactly one match across both → return the path
4. If zero matches → return not-found error with the searched paths
5. If multiple matches → return ambiguity error with the candidate list

The function MUST accept both full IDs (`WI-003`) and the numeric part alone (`003` or `3`). When given a bare number, it MUST zero-pad to match the `WI-XXX` pattern.

#### FR-5: Tolerant Error Handling

All state derivation functions MUST use the `ParseResult[T]` / `ParseWarning` pattern from D4.1. Specifically:

- One bad spec.md MUST NOT block derivation of other work items
- One unparseable BACKLOG.md epic MUST NOT block parsing of other epics
- Missing `work/active/` or `work/completed/` directories MUST return empty results, not errors
- All warnings MUST include the file path and a human-readable description

#### FR-6: Aggregate State Function

The module MUST provide a top-level function `derive_project_state(project_root)` that returns `ParseResult[ProjectState]`:

- `data`: `ProjectState` with all work items (derived state, stage, parent epic), all epics (derived state, sub-item summary), and all backlog-only items
- `warnings`: Accumulated `ParseWarning` list from all sub-operations (BACKLOG.md parsing, spec.md reads, directory scans, state conflicts)

This is the primary entry point for the dashboard (D4.3). The `ParseResult` wrapper ensures the dashboard can report partial-parse diagnostics (e.g., "3 of 5 work items parsed") alongside the state it did derive.

### Non-Functional Requirements

- **NFR-1: Determinism** — Same file system state MUST produce identical output. No randomness, no timestamp-dependent behavior, no ordering sensitivity (sort output by WI-XXX ID).
- **NFR-2: No side effects** — State derivation MUST NOT write to any file, modify global state, or print to stdout/stderr.
- **NFR-3: Dependency on D4.1 only** — State derivation uses D4.1 parsers (`parse_frontmatter`, `parse_backlog`) and stdlib (`pathlib`, `re`). No new dependencies.

---

## Acceptance Criteria

### Core Functionality

- [ ] `derive_project_state(root)` returns typed state for all work items, epics, and backlog items
- [ ] Active item with only spec.md → stage `speccing`
- [ ] Active item with design.md (no plan.md) → stage `designing`
- [ ] Active item with plan.md → stage `implementing`
- [ ] Active item with spec.md + plan.md (design skipped) → stage `implementing`
- [ ] Active item with spec.md Status = `completed` → state `completed` (overrides active)
- [ ] Active item with spec.md Status = `paused` → state `paused` (not `active`)
- [ ] Completed items in `work/completed/YYYYMMDD_WI-XXX_name/` → state `completed`
- [ ] Items in BACKLOG.md with no directory → state `backlog`
- [ ] Epic with all backlog items → derived status `draft`
- [ ] Epic with mix of active and backlog → derived status `active`
- [ ] Epic with all completed → derived status `completed`
- [ ] Epic with 2 completed + 1 abandoned → derived status `active` (needs attention)
- [ ] `resolve_work_item(root, "WI-003")` finds the correct directory

### Error Handling

- [ ] Missing `work/active/` directory → empty results, no error
- [ ] Missing spec.md in an active directory → item included with warning
- [ ] BACKLOG.md ↔ spec.md status conflict → spec.md wins + warning
- [ ] Unparseable spec.md frontmatter → item state defaults to `active` + warning
- [ ] `resolve_work_item` with no match → not-found error with searched paths
- [ ] `resolve_work_item` with multiple matches → ambiguity error with candidates

### Empty-State Verification (AP-1)

- [ ] Empty project (no `work/` directories at all) → empty state, no errors
- [ ] Project with `work/BACKLOG.md` containing `epics: []` and `standalone: []` → empty state
- [ ] Project with `work/active/` but no item directories → empty state

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] New tests pass (`uv run pytest tests/test_pm_state.py`)
- [ ] `uv run mypy src/agentic_mbse/pm/` passes with no errors
- [ ] `uv run ruff check src/agentic_mbse/pm/` passes
- [ ] Each capability has >=4 test cases covering happy path, edge cases, and error paths
- [ ] Test fixtures include: empty project, single active item at each stage, completed item, paused item, orphaned directory, BACKLOG.md conflict

---

## New Types (additions to `types.py`)

```python
class WorkItemStage(str, Enum):
    SPECCING = "speccing"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    UNKNOWN = "unknown"


class DerivedWorkItemState(BaseModel):
    id: str                          # WI-XXX
    name: str                        # descriptive part from directory name
    state: WorkItemStatus            # backlog/active/paused/abandoned/failed/completed
    stage: WorkItemStage | None      # only set when state = active
    epic: str | None                 # parent epic name, or None for standalone
    directory: Path | None           # resolved path, or None for backlog-only
    completed_date: str | None       # YYYYMMDD from directory name, if completed


class DerivedEpicState(BaseModel):
    name: str
    derived_status: EpicStatus       # draft/active/completed (derived)
    declared_status: EpicStatus      # from BACKLOG.md frontmatter
    priority: Priority
    goal: str | None
    file: str
    items: list[DerivedWorkItemState]
    total: int
    done: int


class ProjectState(BaseModel):
    epics: list[DerivedEpicState]
    standalone: list[DerivedWorkItemState]
```

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.2 section)
- **Depends on:** `.project/active/d4.1-parsers/` (parsers — implemented)
- **Frontmatter schemas:** `.project/concepts/architecture-redesign/frontmatter-schemas.md`
- **Workflows (state machine):** `.project/concepts/architecture-redesign/workflows.md` § 3.2
- **Design:** `.project/active/d4.2-state-derivation/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`

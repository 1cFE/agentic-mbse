# Design: D4.4 AP-7 Operations

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02
**Updated:** 2026-02-02
**Branch:** revamp-architecture

## Overview

Implement 14 AP-7 operations as public functions in `src/agentic_mbse/pm/operations.py`. Each operation takes a `project_root: Path` and operation-specific parameters, validates inputs using existing parsers, computes changes in memory, then writes atomically. A shared `OperationResult` return type provides consistent success/failure reporting for CLI integration (D4.5).

## Related Artifacts

- **Spec:** `.project/active/d4.4-operations/spec.md`
- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.4 section)
- **Depends on:** `src/agentic_mbse/pm/parser.py` (D4.1, 862 lines)
- **Depends on:** `src/agentic_mbse/pm/state.py` (D4.2, 357 lines)
- **Depends on:** `src/agentic_mbse/pm/types.py` (D4.1, 240 lines)
- **Depends on:** `src/agentic_mbse/pm/dashboard.py` (D4.3, 177 lines — `get_status` delegates here)

---

## Research Findings

### Existing Codebase Patterns

**Parser module** (`parser.py`):
- All 8 parsers return `ParseResult[T]` with accumulated `ParseWarning` list
- `_warn()` helper at `parser.py:49` appends to warnings list — same pattern in `state.py:36`
- `_strip_html_comments()` at `parser.py:54` removes `<!-- -->` blocks
- `_parse_markdown_table()` at `parser.py:59` extracts rows from markdown tables, scoped to section headings
- `_parse_heading_sections()` at `parser.py:135` splits by heading regex for DI-XXX/AD-XXX formats
- Parsers handle missing files, empty files, malformed content gracefully — operations can rely on this

**State module** (`state.py`):
- `resolve_work_item()` at `state.py:155` — already handles WI-XXX resolution with bare number support, ValueError on not-found/ambiguous
- `derive_project_state()` at `state.py:198` — full project state derivation, used by `status` delegation
- `ACTIVE_DIR_RE` at `state.py:31` — `^(WI-\d+)_(.+)$` pattern for active dirs
- `COMPLETED_DIR_RE` at `state.py:32` — `^(\d{8})_(WI-\d+)_(.+)$` for completed dirs

**Types module** (`types.py`):
- All entity models are Pydantic `BaseModel` subclasses
- Enums are `(str, Enum)` for YAML/JSON serialization
- `ParseResult[T]` is generic with `.data` and `.warnings`
- Entity models already have all fields needed for write formatting (e.g., `InsightEntry` has all DI-XXX fields, `RequirementEntry` has all 5 columns)

**Key observations for operations design:**
1. Parsers are read-only. Operations need write functions that produce the exact formats parsers expect to read — ensuring round-trip correctness.
2. The `_parse_markdown_table()` helper reads tables under section headings. Write functions must append rows preserving the same heading/separator/data structure.
3. BACKLOG.md uses YAML frontmatter + rendered markdown body. Write means: serialize `BacklogData` to YAML, render body from same data.
4. KNOWLEDGE.md and ARCHITECTURE.md use heading-based sections (not tables). Write means: format a new `### XX-XXX: Title` section with bulleted fields.
5. REQUIREMENTS.md, VALIDATION_MATRIX.md, and OVERVIEW.md use markdown tables. Write means: append a `| col | col | ... |` row.
6. traceability_matrix.csv uses standard CSV. Write means: append a row with proper quoting.

### File Path Conventions

| File | Path from project_root |
|------|----------------------|
| BACKLOG.md | `work/BACKLOG.md` |
| KNOWLEDGE.md | `knowledge/KNOWLEDGE.md` |
| REQUIREMENTS.md | `modeling_project/REQUIREMENTS.md` |
| VALIDATION_MATRIX.md | `modeling_project/VALIDATION_MATRIX.md` |
| ARCHITECTURE.md | `modeling_project/ARCHITECTURE.md` |
| OVERVIEW.md | `modeling_project/OVERVIEW.md` |
| traceability_matrix.csv | `data/traceability_matrix.csv` |
| Research pending | `knowledge/research/pending/` |
| Research approved | `knowledge/research/approved/` |
| Research impacts | `knowledge/research/impacts/` |

---

## Proposed Design

### Component 1: Result Types (`types.py` additions)

Add to `types.py`:

```python
class OperationResult(BaseModel):
    """Result of a PM operation."""
    success: bool
    message: str
    ids_assigned: dict[str, str] = Field(default_factory=dict)  # e.g. {"DI": "DI-005"}
    files_modified: list[str] = Field(default_factory=list)
    warnings: list[ParseWarning] = Field(default_factory=list)  # parser warnings from read phase

class ImpactResult(BaseModel):
    """Result of an impact query."""
    query_id: str
    affected_elements: list[TraceabilityEntry] = Field(default_factory=list)
    affected_work_items: list[str] = Field(default_factory=list)  # WI-XXX IDs — TODO: populate when model→WI mapping exists
    warnings: list[ParseWarning] = Field(default_factory=list)
```

The `warnings` field on `OperationResult` preserves parser warnings from the read phase (e.g., "spec.md has unknown field 'Tags'", "BACKLOG.md item WI-003 has completed status but no date"). Operations accumulate parser warnings during validation and pass them through — the CLI can display them on stderr while the success/failure message goes to stdout.

`OperationResult` is the uniform return type for all mutation operations. `ImpactResult` is the return type for `impact_query`. The `get_status` operation returns `DashboardResult` (already defined in `types.py:242` — has `.markdown` and `.warnings` fields) by delegating to `generate_dashboard()` in `dashboard.py:142`.

**Why a single result type instead of per-operation types**: Every caller (CLI in D4.5, commands in Epic 3) needs the same three things — did it work, what IDs were assigned, what changed. Per-operation result types would add complexity without adding information. The `message` field carries operation-specific confirmation text.

### Component 2: ID Assignment Helpers (private, in `operations.py`)

```python
def _next_id(prefix: str, existing_ids: list[str]) -> str:
    """Given a prefix ('DI', 'PR', etc.) and list of existing IDs, return next sequential ID."""
```

Single generic function. Extracts numeric suffixes, finds max, returns `{prefix}-{max+1:03d}`. On empty list, returns `{prefix}-001`.

Used by every append operation. The caller is responsible for parsing the relevant file and extracting the ID list — this keeps the helper pure and testable.

### Component 3: File Write Helpers (private, in `operations.py`)

These are the inverse of the parser read functions. Each produces the exact format the corresponding parser expects.

#### `_write_frontmatter(path, frontmatter_dict, body)`

Writes a complete markdown file with YAML frontmatter and body. Used by `close-item` (spec.md, design.md, plan.md updates) and BACKLOG.md re-rendering.

Strategy: Read the file, parse the frontmatter boundary positions, update the frontmatter dict, preserve the body. For BACKLOG.md, the body is fully re-rendered (not preserved).

For spec.md/design.md/plan.md updates, only specific fields change (`Status`, `Updated`). The implementation reads the file, finds the frontmatter boundaries, modifies only the target YAML fields, and writes back. This preserves any unknown fields or user additions (per frontmatter-schemas.md § 5 note 2: unknown fields are silently ignored by parsers, so they should be preserved by writers).

```python
def _update_frontmatter_fields(path: Path, updates: dict[str, str]) -> None:
    """Update specific fields in a file's YAML frontmatter, preserving the body and unknown fields."""
```

Implementation: Read file → split into frontmatter YAML text + body → `yaml.safe_load` → merge updates → `yaml.dump` → write frontmatter + body.

#### `_render_backlog_body(data: BacklogData) -> str`

Renders the markdown body of BACKLOG.md from `BacklogData`. The body is tool-owned (workflows.md § 3.6), so it's fully regenerated — no user content to preserve.

Format matches the BACKLOG.md template:
- Empty state: "No epics or work items yet." message
- Epic sections: `## Epic: {name}` with metadata line, epic file link, item table
- Standalone section: `## Standalone Items` with item table including priority column
- Completed items show date in Notes column

```python
def _render_backlog_body(data: BacklogData) -> str:
    """Render BACKLOG.md markdown body from BacklogData."""
```

#### `_write_backlog(path: Path, data: BacklogData) -> None`

Combines YAML serialization of `BacklogData` and body rendering into a single file write.

```python
def _write_backlog(path: Path, data: BacklogData) -> None:
    """Write complete BACKLOG.md: YAML frontmatter + rendered body."""
```

The YAML serialization must produce the exact format `parse_backlog` expects. Use `yaml.dump` with `default_flow_style=False` to get block style. Pydantic's `.model_dump()` converts the `BacklogData` to a dict suitable for `yaml.dump`.

**Enum serialization**: Since enums are `(str, Enum)`, `model_dump()` returns their `.value` strings. Verify this in implementation; if not, use `model_dump(mode='json')`.

#### `_format_insight_entry(entry: InsightEntry) -> str`

Formats a single DI-XXX entry as markdown text matching the KNOWLEDGE.md heading-based format.

```python
def _format_insight_entry(entry: InsightEntry) -> str:
    """Format a DI-XXX entry as markdown for KNOWLEDGE.md."""
```

Output format:
```
### DI-XXX: Title
- **Source**: ...
- **Rationale**: ...        # only if rationale is not None
- **Context**: ...
- **Model implications**: ...
- **Analysis implications**: ...
- **Status**: captured
```

No `Superseded-by` or `Supersedes` fields for new entries (those are only set by `supersede-insight`).

#### `_format_table_row(columns: list[str]) -> str`

Formats a markdown table row: `| col1 | col2 | ... |`.

```python
def _format_table_row(columns: list[str]) -> str:
    """Format a markdown table data row."""
```

Used by `promote-requirement`, `add-validation`, `register-intent` for appending to markdown tables.

#### `_format_decision_entry(entry: DecisionEntry) -> str`

Formats a single AD-XXX entry as markdown for ARCHITECTURE.md.

```python
def _format_decision_entry(entry: DecisionEntry) -> str:
    """Format an AD-XXX entry as markdown for ARCHITECTURE.md."""
```

Output format:
```
### AD-XXX: Title
**Decision**: ...
**Rationale**: ...
**Date**: YYYY-MM-DD
**Status**: active
```

#### `_append_section(path: Path, text: str) -> None`

Appends a markdown section (e.g., a `### DI-XXX` entry) to the end of a file, ensuring a blank line separator before the new content. Creates the file if it doesn't exist. Named `_append_section` to distinguish from `_append_table_row` which does section-scoped insertion within a table.

#### `_append_csv_row(path: Path, row: dict[str, str]) -> None`

Appends a row to a CSV file, using the existing header order. If the file is empty or missing, creates it with the full header row first.

### Component 4: Public Operations (in `operations.py`)

Each operation follows the same pattern:

1. Validate inputs (raise `ValueError` or return error `OperationResult`)
2. Parse relevant files using existing parsers
3. Compute all changes in memory
4. Write all files
5. Return `OperationResult`

**Error handling convention**: Operations return `OperationResult(success=False, message=...)` for all expected failures — missing files, invalid IDs, duplicates, items not in BACKLOG.md, etc. This includes catching `ValueError` from internal calls like `resolve_work_item()` and converting to a failed result. Exceptions propagate only for truly unexpected errors (I/O failures, bugs). This gives the CLI a single code path: check `result.success`, print `result.message`, exit 0 or 1.

#### `close_item(project_root: Path, wi_id: str) -> OperationResult`

1. Call `resolve_work_item(project_root, wi_id)` — catch `ValueError` and convert to `OperationResult(success=False, message=str(e))`. All expected failures (not found, ambiguous, invalid format) are reported this way, never raised.
2. Validate resolved path is in `work/active/` (not already completed) — return failure if not
3. Parse BACKLOG.md and validate the item exists in its epics or standalone list — return `OperationResult(success=False, message="WI-XXX not found in BACKLOG.md")` if missing
4. Read spec.md frontmatter, update `Status: completed`, `Updated: today`
5. If design.md exists, update `Status: complete`, `Updated: today`
6. If plan.md exists, update `Status: complete`, `Updated: today`
7. Compute destination: `work/completed/{today}_{WI-XXX}_{name}/`
8. Update BACKLOG.md data in memory: set item status to `completed`, set `completed` date
9. Write all frontmatter updates
10. Move directory (`shutil.move`)
11. Write BACKLOG.md (YAML + re-rendered body)
12. Return result with archive path

**Atomicity note**: Steps 8-10 are the write phase. If step 9 (directory move) fails after step 8 (frontmatter written), we have partial state. Mitigation: do the directory move first (step 9 before 8), since a moved directory with old frontmatter is recoverable (re-run close-item from completed dir), but updated frontmatter in a non-moved directory is confusing. Actually — `resolve_work_item` only searches `work/active/` and `work/completed/`, so the order matters. The safest order:

1. Write frontmatter updates to files in `work/active/{WI-XXX}_*/` (files still in place)
2. Move directory to `work/completed/`
3. Write BACKLOG.md

If (2) fails, the frontmatter is updated but the item is still in active — the next `close-item` call will still find and complete it. If (3) fails, the directory is moved but BACKLOG.md is stale — `derive_project_state()` already handles this discrepancy by scanning the file system.

#### `add_insight(project_root, *, title, source, context, model_implications, analysis_implications, rationale=None) -> OperationResult`

1. Validate required fields non-empty
2. Parse `knowledge/KNOWLEDGE.md` → extract existing DI-XXX IDs
3. Assign next ID via `_next_id("DI", ...)`
4. Create `InsightEntry` with status=`captured`
5. Format entry via `_format_insight_entry()`
6. Append to KNOWLEDGE.md
7. Return result with assigned ID

#### `save_research(project_root, *, topic, content) -> OperationResult`

1. Validate topic and content non-empty
2. Kebab-case the topic: `re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')`
3. Generate filename: `{YYYYMMDD}-{HHMMSS}_{topic}.md`
4. Ensure `knowledge/research/pending/` exists (`mkdir -p`)
5. Write content to file
6. Return result with file path

#### `approve_research(project_root, *, pending_file: str | Path, insights: list[InsightInput]) -> OperationResult`

**Input type** — add to `types.py`:
```python
class InsightInput(BaseModel):
    """Input for creating a new DI-XXX insight (no id or status — assigned by operation)."""
    title: str
    source: str
    context: str
    model_implications: str
    analysis_implications: str
    rationale: str | None = None
```

This validates required fields at the Pydantic level rather than requiring each caller to construct dicts correctly. The operation assigns `id` and `status`.

1. Resolve pending_file to absolute path, validate it's in `knowledge/research/pending/`
2. Validate file exists
3. Parse KNOWLEDGE.md for existing IDs
4. For each insight dict: validate required fields, assign next DI-XXX ID, create entry
5. Compute all formatted entries
6. Ensure `knowledge/research/approved/` exists
7. Move file to `knowledge/research/approved/` (same filename)
8. Append all formatted entries to KNOWLEDGE.md
9. Return result with new file path and all assigned DI-XXX IDs

**Atomicity**: Move file first, then append. If append fails, the file is in approved/ but insights aren't in KNOWLEDGE.md — re-running won't help (file is no longer in pending/). Better: append first, then move. If move fails, KNOWLEDGE.md has the insights (idempotent — they have assigned IDs), and the file is still in pending/ for retry.

Revised order: (1) append entries to KNOWLEDGE.md, (2) move file to approved/.

#### `trace_element(project_root, *, element: str, file: str, type: str, knowledge: list[str] | None = None, requirement: list[str] | None = None, source_type: str = "", source_document: str = "", source_location: str = "", confidence: str = "", assumptions: str = "", last_verified: str | None = None) -> OperationResult`

1. Validate element and file non-empty
2. If knowledge provided: parse KNOWLEDGE.md, validate each DI-XXX ID in the list exists
3. If requirement provided: parse REQUIREMENTS.md, validate each PR-XXX ID in the list exists
4. Parse traceability CSV, check no existing row with same element+file
5. Default `last_verified` to today's date if not provided
6. Append CSV row
7. Return result

#### `promote_requirement(project_root, *, requirement, source, enforcement, validation_method) -> OperationResult`

1. Validate all four fields non-empty
2. Validate source matches `DI-\d+` or `G-\d+` pattern
3. Parse REQUIREMENTS.md for existing PR-XXX IDs
4. Assign next PR-XXX ID
5. Format table row: `| {id} | {requirement} | {source} | {enforcement} | {validation_method} |`
6. Append row to REQUIREMENTS.md (under `## Requirements` table)
7. Return result with assigned ID

#### `impact_query(project_root, *, query_id: str) -> ImpactResult`

1. Validate query_id matches `DI-\d+` or `PR-\d+` pattern
2. Parse traceability CSV (tolerant — missing file returns empty results + warning)
3. Filter: if DI-XXX, match rows where Knowledge column contains the ID. If PR-XXX, match rows where Requirement column contains the ID.
4. Scan `work/active/` directories to identify affected work items (match element file paths against active work item directories)
5. Return `ImpactResult` with affected elements, work items, warnings

**Known gap — work item cross-reference**: The spec requires affected work items in the result. The traceability CSV `File` column contains model file paths (e.g., `models/library/calculations/magnet_cost.sysml`), not work item directories — there is no tracked model-file→work-item mapping. `affected_work_items` is returned as an empty list for now.

`# TODO: Populate affected_work_items when a model→work-item mapping exists (e.g., plan.md lists model files, or a future index tracks which WI-XXX produced which model files).`

The calling agent has sufficient context to interpret which work items are relevant from the affected element file paths.

#### `register_decision(project_root, *, title, decision, rationale) -> OperationResult`

1. Validate all three fields non-empty
2. Parse ARCHITECTURE.md for existing AD-XXX IDs
3. Assign next AD-XXX ID
4. Create `DecisionEntry` with date=today, status=`active`
5. Format entry via `_format_decision_entry()`
6. Append to ARCHITECTURE.md under `## Key Decisions`
7. Return result with assigned ID

#### `update_validation(project_root, *, sv_id: str, status: str) -> OperationResult`

1. Validate sv_id matches `SV-\d+` pattern
2. Validate status is a valid `VerificationStatus` value
3. Read entire VALIDATION_MATRIX.md
4. Parse to find the row, update the Status cell
5. Re-write the entire file with the updated table
6. Return result

**Implementation detail**: This is the one operation that re-writes an entire file (not append-only). Read the file content, use regex or line-by-line processing to find the table row matching `sv_id` in the ID column, replace the Status cell value, write the file back. This is simpler and more reliable than trying to do an in-place edit of one cell in a markdown table.

#### `register_intent(project_root, *, goals=None, questions=None) -> OperationResult`

1. Validate at least one of goals/questions is non-empty
2. Parse OVERVIEW.md for existing G-XXX and AQ-XXX IDs
3. For each goal: validate required fields (goal, priority, source), assign G-XXX ID
4. For each question: validate required fields (question, source), assign AQ-XXX ID
5. Format table rows for each
6. Append goal rows to `## Goals Registry` table
7. Append question rows to `## Analysis Questions` table
8. Return result with all assigned IDs

**Input types** — add to `types.py`:
```python
class GoalInput(BaseModel):
    """Input for creating a new G-XXX goal (no id — assigned by operation)."""
    goal: str
    priority: str
    status: str = "active"
    source: str
    traced_requirements: str = ""

class QuestionInput(BaseModel):
    """Input for creating a new AQ-XXX question (no id — assigned by operation)."""
    question: str
    implies: str = ""
    source: str
    status: str = "open"
```

Signature: `register_intent(project_root, *, goals: list[GoalInput] | None = None, questions: list[QuestionInput] | None = None)`

#### `add_item(project_root, *, name, scale, priority, epic=None, goal=None) -> OperationResult`

1. Validate name non-empty, scale/priority valid enums
2. Parse BACKLOG.md
3. If epic specified, validate it exists in epics list
4. Collect all WI-XXX IDs (from epics and standalone), assign next via `_next_id`
5. Add new entry to the appropriate list in BacklogData (epic items or standalone)
6. Write BACKLOG.md (YAML + re-rendered body)
7. Return result with assigned WI-XXX ID

#### `add_validation(project_root, *, description, type, mechanism, expected, tolerance, source="", test="") -> OperationResult`

1. Validate description non-empty, type/mechanism valid enums
2. Parse VALIDATION_MATRIX.md for existing SV-XXX IDs
3. Assign next SV-XXX ID
4. Format table row with status=`pending`
5. Append to VALIDATION_MATRIX.md table
6. Return result with assigned ID

#### `supersede_insight(project_root, *, old_id, new_insight, reason) -> OperationResult`

```python
def supersede_insight(
    project_root: Path,
    *,
    old_id: str,
    new_insight: dict,
    reason: str,
) -> OperationResult:
    # TODO: D4.4 stretch — implement full supersession flow per workflows.md § 6.1
    # Full implementation would:
    # 1. Mark old DI-XXX as superseded in KNOWLEDGE.md (Status → superseded, add Superseded-by)
    # 2. Assign new DI-XXX ID, create new entry with Supersedes field
    # 3. Query traceability_matrix.csv for affected elements
    # 4. Produce impact report to knowledge/research/impacts/DI-XXX_superseded.md
    raise NotImplementedError(
        "supersede-insight is not yet implemented. "
        "See workflows.md § 6.1 for the full supersession flow."
    )
```

#### `get_status(project_root: Path) -> DashboardResult`

Delegates to the D4.3 dashboard module (`dashboard.py`), which is already complete:

```python
def get_status(project_root: Path) -> DashboardResult:
    """Produce project status dashboard. Delegates to generate_dashboard() (D4.3)."""
    return generate_dashboard(project_root)
```

`generate_dashboard()` (`dashboard.py:142`) already orchestrates state derivation, requirements parsing, validation matrix parsing, and markdown rendering. This operation is a thin pass-through that provides a consistent entry point in the operations module.

### Component 5: Markdown Table Append Strategy

Several operations need to append a row to an existing markdown table. The strategy:

1. Read the file content
2. Find the table under the target section heading (same scoping logic as `_parse_markdown_table`)
3. Find the last `|`-prefixed line in that table
4. Insert the new row after it
5. Write the file back

This handles the case where content follows the table (other sections, comments). It does NOT re-render the entire table — just appends a row. This preserves any manual formatting in existing rows.

```python
def _append_table_row(path: Path, section_heading: str, row: str) -> None:
    """Append a row to a markdown table under a given section heading."""
```

If the file exists but the table is empty (header + separator only, no data rows), the new row goes after the separator. If the section heading doesn't exist, this is an error (the file is malformed or the wrong template was used).

### Component 6: `__init__.py` Updates

Add to the `__init__.py` exports:
- `OperationResult`, `ImpactResult` from types
- All 14 public operation functions from operations

---

## Potential Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| YAML round-trip changes formatting | Medium | Use `yaml.dump(default_flow_style=False, sort_keys=False)` to preserve block style. Test round-trip: write → parse → write produces stable output. |
| Markdown table append inserts in wrong location | Medium | Scope to section heading, find last pipe-prefixed line. Test with tables followed by other content. |
| Concurrent operation calls corrupt files | Low | Documented as out of scope (single-writer assumption). Acceptable at project scale. |
| close-item partial failure leaves inconsistent state | Medium | Write order: frontmatter → move dir → BACKLOG.md. Each step is recoverable. Document recovery in error messages. |
| Empty file edge cases | Medium | Every operation that reads a file handles the empty/missing case via parser graceful degradation. Operations that *write* to potentially-missing files must create them first. |

---

## Integration Strategy

Operations are pure library functions in the `pm` module. They have no dependency on CLI or command infrastructure.

**D4.5 integration**: Each operation maps to an `agentic-mbse pm <name>` CLI subcommand. The CLI parses arguments, calls the operation function, prints `result.message`, and exits with code 0 (success) or 1 (result.success=False).

**Epic 3 command integration**: Commands call operations via `agentic-mbse pm <name> ...` shell invocations. The CLI is the interface boundary — commands never import operations directly.

---

## Validation Approach

### Testing Strategy

Test file: `tests/test_pm_operations.py`

**Fixture approach**: Each test creates a `tmp_path` directory, copies or creates the minimum project structure needed, runs the operation, and asserts on file content.

**Per-operation test scenarios** (minimum):
1. Happy path (valid inputs, correct output)
2. Validation error (missing file, invalid ID, duplicate)
3. Empty project (first ID assignment, file creation)

**Round-trip tests**:
- BACKLOG.md: write → parse → write produces identical output
- KNOWLEDGE.md: append entry → parse → entry matches input
- REQUIREMENTS.md: append row → parse → row matches input

**Atomicity tests**:
- For `close-item`: mock a write failure mid-operation, verify state is recoverable

### Success Criteria

All spec acceptance criteria met. All existing tests continue to pass.

---

**Next Step:** After approval → `/_my_plan` (given the number of operations, a phased plan helps track progress)

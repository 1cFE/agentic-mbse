# Spec: D4.1 — PM Parsers

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02 15:56:59 UTC
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-004 (PM Script Engine)
**Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` § 3B.1 parser items

---

## Business Goals

### Why This Matters

Every D4 deliverable — state derivation, dashboard, AP-7 operations, CLI — reads structured project files. Without parsers, the PM engine cannot exist. This is the blocking foundation for eliminating P5 (PM depends on agent memory) and implementing AP-7 (script-mechanized transitions).

### Success Criteria

- [ ] Any downstream PM code can call a parser function and get typed, validated data back
- [ ] Malformed or missing files produce warnings and partial results, never crashes
- [ ] Empty-state files (freshly created by `agentic-mbse init`) parse correctly with empty collections
- [ ] Parser output types are well-defined Pydantic models that other modules import

### Priority

First deliverable in Epic 4. D4.2 (state), D4.3 (dashboard), D4.4 (operations) all depend on this.

---

## Problem Statement

### Current State

The codebase has no structured file parsing for PM files. The only YAML parsing is a single `yaml.safe_load()` in `validation/level7_architecture.py` for an optional manifest. All project documents (BACKLOG.md, REQUIREMENTS.md, KNOWLEDGE.md, etc.) are currently read only by Claude agent commands as unstructured text. There is no programmatic access to their structured content.

### Desired Outcome

A `src/agentic_mbse/pm/parser.py` module that provides typed, validated access to every structured project file the PM engine consumes. Each parser returns Pydantic models and collects warnings for malformed content. Downstream code (state derivation, dashboard, operations) calls these parsers instead of reading files directly.

---

## Scope

### In Scope

- New module: `src/agentic_mbse/pm/parser.py` (single file)
- New module: `src/agentic_mbse/pm/__init__.py` (public API exports)
- 8 parsers with Pydantic return types:
  1. Generic YAML frontmatter parser
  2. BACKLOG.md parser
  3. REQUIREMENTS.md table parser
  4. VALIDATION_MATRIX.md table parser
  5. KNOWLEDGE.md section parser
  6. ARCHITECTURE.md section parser
  7. OVERVIEW.md table parser (Goals Registry + Analysis Questions)
  8. traceability_matrix.csv parser
- Pydantic data models for all parsed entities
- Enum types for status/type fields
- Warning collection mechanism (not exceptions — warnings accumulate alongside partial results)
- Test suite: `tests/test_pm_parser.py`
- Test fixtures: `tests/fixtures/pm/` with sample files

### Out of Scope

- File writing or mutation (D4.4 operations)
- State derivation logic (D4.2 — uses parsers but is separate)
- Dashboard rendering (D4.3)
- CLI integration (D4.5)
- Parsing spec.md/design.md/plan.md/review.md body content (their YAML frontmatter is handled by the generic parser; body structure is command-specific)
- Epic file body content (frontmatter only, per decision)

### Edge Cases & Considerations

- **Empty files**: Templates produce files with headers but no data rows. All parsers MUST return empty collections (not errors) for these.
- **Missing files**: Parsers that accept a `Path` MUST handle `FileNotFoundError` and return a clear result indicating the file doesn't exist, not raise an exception.
- **Partial parse**: A BACKLOG.md with 5 epic items where 1 has an invalid status SHOULD still return the other 4 with a warning about the bad one.
- **Extra columns/fields**: Markdown tables MAY have extra columns not in the schema. These SHOULD be silently ignored (forwards compatibility).
- **Missing columns/fields**: If a required column is absent from a markdown table, the parser SHOULD warn and skip that row (not crash).
- **YAML type coercion**: `pyyaml` coerces unquoted `yes`/`no` to booleans and bare numbers to ints. Parsers MUST handle this (e.g., a date `2026-02-02` may arrive as a `datetime.date` object from pyyaml, not a string).
- **HTML comments in templates**: Templates use `<!-- ... -->` for format examples. Parsers MUST NOT treat comment content as data.
- **Multi-value CSV fields**: The `Knowledge` and `Requirement` columns in traceability_matrix.csv can contain comma-separated IDs (e.g., `DI-003, DI-012`). The parser MUST split these into lists.

---

## Requirements

### Functional Requirements

#### FR-1: Warning Collection Pattern

All parsers MUST use a shared warning collection mechanism. A warning is a structured record with:
- `file`: Path to the file being parsed
- `location`: Where in the file the problem is (line number, field name, row index)
- `message`: Human-readable description of the problem

Parsers MUST return both the parsed data AND any warnings collected. The caller decides what to do with warnings (display, log, aggregate).

**Pattern**: Each parse function returns a `ParseResult[T]` that holds both `data: T` and `warnings: list[ParseWarning]`.

#### FR-2: Generic YAML Frontmatter Parser

The parser MUST extract YAML frontmatter delimited by `---` at the start of a markdown file.

**Input**: File path (Path)
**Output**: `ParseResult[dict[str, Any]]` — raw YAML dict + warnings

Behavior:
- If the file doesn't start with `---`, return empty dict with a warning
- If the closing `---` is missing, return empty dict with a warning
- If YAML is malformed (syntax error), return empty dict with a warning containing the YAML error message
- Valid YAML with unknown fields: return all fields (unknown fields are the caller's problem, not the frontmatter parser's)
- This parser is a building block — the BACKLOG.md parser and other frontmatter-bearing files call this first, then validate the dict against their specific schema

#### FR-3: BACKLOG.md Parser

Parse `work/BACKLOG.md` YAML frontmatter into typed epic and standalone item structures.

**Input**: File path
**Output**: `ParseResult[BacklogData]`

`BacklogData` model:
- `epics: list[EpicEntry]` — each with `name`, `goal` (optional G-XXX), `priority` (P0-P3), `status` (draft/active/completed), `file` (path), `items: list[WorkItemEntry]`
- `standalone: list[StandaloneEntry]` — each with `id` (WI-XXX), `name`, `scale` (trivial/standard), `priority` (P0-P3), `status` (backlog/active/paused/abandoned/failed/completed), `completed` (optional date)

`WorkItemEntry` model: `id` (WI-XXX), `name`, `scale`, `status`, `completed` (optional date)

Validation:
- `epics` and `standalone` MUST be lists (warn if missing or wrong type, default to `[]`)
- Each item's `status` MUST be one of the allowed enum values (warn and skip item if invalid)
- `completed` date MUST be present when `status` = `completed` (warn if missing)
- `id` MUST match pattern `WI-\d+` (warn and skip if invalid)
- `priority` MUST be one of P0-P3 (warn if invalid)

#### FR-4: REQUIREMENTS.md Table Parser

Parse the markdown table under `## Requirements` into typed requirement entries.

**Input**: File path
**Output**: `ParseResult[list[RequirementEntry]]`

`RequirementEntry` model: `id` (PR-XXX), `requirement` (text), `source` (text), `enforcement` (text), `validation_method` (text)

Behavior:
- Locate the table by finding the `## Requirements` heading, then the first markdown table after it
- Parse each `| ... |` row, splitting by `|` and stripping whitespace
- Skip the header row and the separator row (`|---|---|...`)
- Skip rows where `id` doesn't match `PR-\d+` pattern (warn)
- If the `## Requirements` section doesn't exist, return empty list (not an error — AP-1)

#### FR-5: VALIDATION_MATRIX.md Table Parser

Parse the markdown table under `## Verification Registry` into typed verification entries.

**Input**: File path
**Output**: `ParseResult[list[ValidationEntry]]`

`ValidationEntry` model: `id` (SV-XXX), `description`, `type` (reasonableness/baseline/physical/relationship/rollup), `mechanism` (model/test/manual), `expected`, `tolerance`, `source`, `test`, `status` (passing/failing/pending)

Behavior:
- Locate by `## Verification Registry` heading
- Same markdown table parsing as FR-4
- Skip rows where `id` doesn't match `SV-\d+` (warn)
- Empty table → empty list (AP-1)

#### FR-6: KNOWLEDGE.md Section Parser

Parse `### DI-XXX: [Title]` sections into typed domain insight entries.

**Input**: File path
**Output**: `ParseResult[list[InsightEntry]]`

`InsightEntry` model: `id` (DI-XXX), `title`, `source` (text), `rationale` (optional text), `context` (text), `model_implications` (text), `analysis_implications` (text), `status` (captured/addressed/superseded), `superseded_by` (optional DI-XXX), `supersedes` (optional DI-XXX)

Behavior:
- Split file into sections by `### DI-\d+:` headings
- For each section, parse bullet points in `- **Field**: value` format
- Missing required fields (Source, Context, Model implications, Analysis implications, Status) → warn and include entry with empty strings for missing fields
- Optional fields (Rationale, Superseded-by, Supersedes) → omit without warning
- No DI sections found → empty list (AP-1)
- Sections inside HTML comments (`<!-- ... -->`) MUST be ignored (template has a format example in comments)

#### FR-7: ARCHITECTURE.md Section Parser

Parse `### AD-XXX: [Title]` sections under `## Key Decisions` into typed decision entries.

**Input**: File path
**Output**: `ParseResult[list[DecisionEntry]]`

`DecisionEntry` model: `id` (AD-XXX), `title`, `decision` (text), `rationale` (text), `date` (text), `status` (active/revised/superseded)

Behavior:
- Find `## Key Decisions` section, then split by `### AD-\d+:` headings
- Parse bold-prefixed fields: `**Decision**: ...`, `**Rationale**: ...`, `**Date**: ...`, `**Status**: ...`
- Missing required fields → warn and include with empty strings
- Sections inside HTML comments MUST be ignored
- No AD sections → empty list (AP-1)

#### FR-8: OVERVIEW.md Table Parser

Parse Goals Registry and Analysis Questions tables from OVERVIEW.md.

**Input**: File path
**Output**: `ParseResult[OverviewData]`

`OverviewData` model:
- `goals: list[GoalEntry]` — each with `id` (G-XXX), `goal` (text), `priority`, `status`, `source`, `traced_requirements` (text)
- `questions: list[AnalysisQuestionEntry]` — each with `id` (AQ-XXX), `question` (text), `implies` (text), `source`, `status`

Behavior:
- Locate `## Goals Registry` heading, parse the table after it
- Locate `## Analysis Questions` heading, parse the table after it
- Same table-parsing mechanics as FR-4
- Skip rows where id doesn't match expected pattern (warn)
- Missing sections → empty list for that section (AP-1)

#### FR-9: traceability_matrix.csv Parser

Parse `data/traceability_matrix.csv` into typed traceability entries.

**Input**: File path
**Output**: `ParseResult[list[TraceabilityEntry]]`

`TraceabilityEntry` model: `element` (text), `file` (text), `type` (text), `knowledge` (list[str] — split from comma-separated DI-XXX), `requirement` (list[str] — split from comma-separated PR-XXX), `source_type` (text), `source_document` (text), `source_location` (text), `confidence` (text), `assumptions` (text), `last_verified` (text)

Behavior:
- Use Python `csv` module (handles quoting correctly)
- Header row MUST match expected column names (case-insensitive comparison; warn if columns missing)
- Empty CSV (header only) → empty list (AP-1)
- Multi-value Knowledge/Requirement columns: split by `,`, strip whitespace, return as `list[str]`

### Non-Functional Requirements

- **FR-10: Type safety** — All parser return types MUST be Pydantic v2 `BaseModel` subclasses, following the pattern in `sysml/types.py`. Enum fields MUST use `str, Enum` pattern for JSON serialization.
- **FR-11: No side effects** — Parsers MUST NOT write to any file, modify global state, or print to stdout/stderr. Warnings are returned, not printed.
- **FR-12: Dependency minimal** — Parsers use only `pyyaml` (existing dependency), `csv` (stdlib), `re` (stdlib), `pathlib` (stdlib), and `pydantic` (existing dependency). No new dependencies.

---

## Acceptance Criteria

### Core Functionality

- [ ] `parse_frontmatter(path)` extracts YAML from any markdown file with `---` delimiters
- [ ] `parse_backlog(path)` returns typed `BacklogData` from BACKLOG.md
- [ ] `parse_requirements(path)` returns typed `list[RequirementEntry]` from REQUIREMENTS.md
- [ ] `parse_validation_matrix(path)` returns typed `list[ValidationEntry]` from VALIDATION_MATRIX.md
- [ ] `parse_knowledge(path)` returns typed `list[InsightEntry]` from KNOWLEDGE.md
- [ ] `parse_architecture(path)` returns typed `list[DecisionEntry]` from ARCHITECTURE.md
- [ ] `parse_overview(path)` returns typed `OverviewData` from OVERVIEW.md
- [ ] `parse_traceability(path)` returns typed `list[TraceabilityEntry]` from traceability CSV
- [ ] All parsers return `ParseResult[T]` with both data and warnings

### Error Handling

- [ ] Missing file → `ParseResult` with empty data + warning "File not found: {path}"
- [ ] Empty file → `ParseResult` with empty data + no warnings (empty is valid per AP-1)
- [ ] Malformed YAML → `ParseResult` with empty data + warning with YAML error detail
- [ ] Invalid enum value → row/entry skipped + warning naming the bad value and allowed values
- [ ] Missing required field → entry included with empty string + warning
- [ ] Template comment content (`<!-- ... -->`) → not parsed as data

### Empty-State Verification (AP-1)

- [ ] Every template file from `project_templates/` parses successfully with empty collections
- [ ] Specifically: `BACKLOG.md.template` → `BacklogData(epics=[], standalone=[])`
- [ ] Specifically: `REQUIREMENTS.md.template` → `[]`
- [ ] Specifically: `VALIDATION_MATRIX.md.template` → `[]`
- [ ] Specifically: `KNOWLEDGE.md.template` → `[]`
- [ ] Specifically: `ARCHITECTURE.md.template` → `[]`
- [ ] Specifically: `OVERVIEW.md.template` → `OverviewData(goals=[], questions=[])`
- [ ] Specifically: `traceability_matrix.csv` (header only) → `[]`

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] New tests pass (`uv run pytest tests/test_pm_parser.py`)
- [ ] `uv run mypy src/agentic_mbse/pm/` passes with no errors
- [ ] `uv run ruff check src/agentic_mbse/pm/` passes
- [ ] Each parser has ≥4 test cases: valid populated, valid empty, missing file, malformed content
- [ ] Test fixtures in `tests/fixtures/pm/` include sample files for each parser

---

## Technical Constraints

### Data Model Patterns

Follow existing codebase conventions from `sysml/types.py`:

```python
# Enums: str + Enum for JSON compatibility
class WorkItemStatus(str, Enum):
    BACKLOG = "backlog"
    ACTIVE = "active"
    PAUSED = "paused"
    ABANDONED = "abandoned"
    FAILED = "failed"
    COMPLETED = "completed"

# Models: Pydantic v2 BaseModel
class WorkItemEntry(BaseModel):
    id: str  # WI-XXX
    name: str
    scale: WorkItemScale
    status: WorkItemStatus
    completed: str | None = None  # YYYY-MM-DD or None

# Results: Generic wrapper
class ParseWarning(BaseModel):
    file: str
    location: str
    message: str

class ParseResult(BaseModel, Generic[T]):
    data: T
    warnings: list[ParseWarning] = Field(default_factory=list)
```

### Schema References

Authoritative schema sources (parser MUST match these):

| File | Schema source |
|------|--------------|
| BACKLOG.md frontmatter | `frontmatter-schemas.md` § 3.5 |
| spec.md frontmatter | `frontmatter-schemas.md` § 3.1 |
| design.md frontmatter | `frontmatter-schemas.md` § 3.2 |
| plan.md frontmatter | `frontmatter-schemas.md` § 3.3 |
| review.md frontmatter | `frontmatter-schemas.md` § 3.4 |
| epic file frontmatter | `frontmatter-schemas.md` § 3.6 |
| REQUIREMENTS.md table | `information-architecture.md` § 3 Role 4 |
| VALIDATION_MATRIX.md table | `information-architecture.md` § 3 Role 6 |
| KNOWLEDGE.md entries | `information-architecture.md` § 3 Role 2 |
| ARCHITECTURE.md entries | `information-architecture.md` § 3 Role 5 |
| OVERVIEW.md tables | `information-architecture.md` § 3 Role 3 |
| traceability_matrix.csv | `information-architecture.md` § 5.3 |

### Markdown Table Parsing Strategy

Markdown tables in templates follow this format:
```
| Col1 | Col2 | Col3 |
|------|------|------|
| val  | val  | val  |
```

Parsing approach:
1. Find the target section heading (e.g., `## Requirements`)
2. Scan forward for the first line matching `| ... |` (header row)
3. Skip the separator row (`|---|...`)
4. Parse each subsequent `| ... |` line as a data row
5. Stop at the next heading (`## ...` or `---`) or end of file
6. Split each row by `|`, strip whitespace from each cell, drop empty leading/trailing cells from the split

### Section Parsing Strategy

KNOWLEDGE.md and ARCHITECTURE.md use heading-based sections:
```
### DI-001: Some Title
- **Source**: ...
- **Context**: ...
```

Parsing approach:
1. Split file content into blocks by the heading regex (`### (DI|AD)-\d+: (.+)`)
2. For each block, parse bullet lines matching `- **FieldName**: value`
3. Multi-line values: if a bullet's value continues on the next line (no new `- **`), concatenate
4. Strip HTML comments before parsing

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.1 section)
- **Frontmatter schemas:** `.project/concepts/architecture-redesign/frontmatter-schemas.md`
- **Information architecture:** `.project/concepts/architecture-redesign/information-architecture.md`
- **Templates (parser input contracts):**
  - `project_templates/BACKLOG.md.template`
  - `project_templates/REQUIREMENTS.md.template`
  - `project_templates/VALIDATION_MATRIX.md.template`
  - `project_templates/KNOWLEDGE.md.template`
  - `project_templates/ARCHITECTURE.md.template`
  - `project_templates/OVERVIEW.md.template`
  - `project_templates/data/traceability_matrix.csv`
- **Design:** `.project/active/d4.1-parsers/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`

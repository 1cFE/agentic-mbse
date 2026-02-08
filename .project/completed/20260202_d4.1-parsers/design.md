# Design: D4.1 — PM Parsers

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-02
**Updated:** 2026-02-02
**Branch:** revamp-architecture
**Commit:** 03332e8

---

## Overview

A `src/agentic_mbse/pm/` package providing typed parsers that transform structured project files (YAML frontmatter, markdown tables, heading-based sections, CSV) into validated Pydantic models with accumulated warnings. This is the foundational data access layer for the PM engine.

The module exposes 8 public `parse_*` functions: 1 infrastructure parser (`parse_frontmatter` — a building block called by other parsers and also used directly by D4.2 for spec.md/design.md/plan.md) and 7 file-type parsers (backlog, requirements, validation matrix, knowledge, architecture, overview, traceability).

## Related Artifacts

- **Spec:** `.project/active/d4.1-parsers/spec.md`
- **Epic:** `.project/backlog/epic_architecture-pm-engine.md` (D4.1)
- **Frontmatter schemas:** `.project/concepts/architecture-redesign/frontmatter-schemas.md`
- **Information architecture:** `.project/concepts/architecture-redesign/information-architecture.md`
- **Existing type patterns:** `src/agentic_mbse/sysml/types.py`

---

## Research Findings

### Existing Codebase Patterns

**Pydantic v2 models** (`src/agentic_mbse/sysml/types.py:1-275`):
- Uses `BaseModel` with `ConfigDict` for configuration
- Enums: `ValidationCode(str, Enum)` pattern for JSON-serializable enums (`:66`)
- Plain `Enum` for internal enums like `BindingType` (`:18`)
- `Field(default_factory=list)` for mutable defaults (`:207`)
- Union types use `str | None` Python 3.10+ syntax
- Properties on Pydantic models for derived values (`:209-222`)

**YAML parsing** (`src/agentic_mbse/validation/level7_architecture.py:39-59`):
- `yaml.safe_load()` with graceful exception handling
- Returns `None` for missing files (but our parsers need `ParseResult` instead)

**Test patterns** (`tests/conftest.py`, `tests/test_sysml_quality_checks.py`):
- Fixtures for path setup, `tmp_path` for temp files
- `write_text()` for creating test files inline
- Class-based test grouping (`class TestTypeMap`)

### Template Analysis (Parser Input Contracts)

Each template defines the "empty state" the parser must handle:

| Template | Empty State Pattern |
|----------|-------------------|
| `BACKLOG.md.template` | YAML frontmatter with `epics: []`, `standalone: []` |
| `REQUIREMENTS.md.template` | `## Requirements` heading, table header, no data rows, HTML comment with examples |
| `VALIDATION_MATRIX.md.template` | `## Verification Registry` heading, table header, no data rows, HTML comment |
| `KNOWLEDGE.md.template` | Entry format in HTML comment only, no `### DI-XXX` sections |
| `ARCHITECTURE.md.template` | `## Key Decisions` heading, decision format in HTML comment only |
| `OVERVIEW.md.template` | `## Goals Registry` and `## Analysis Questions` headings, table headers, no data rows, HTML comments |
| `traceability_matrix.csv` | Header row only: `Element,File,Type,Knowledge,Requirement,Source_Type,Source_Document,Source_Location,Confidence,Assumptions,Last_Verified` |

### Key Design Observations

1. **HTML comments are pervasive** — every template uses `<!-- ... -->` for format examples. The comment stripping must happen early and reliably, including multi-line comments.

2. **Markdown table parsing is shared** — FR-4, FR-5, FR-7, FR-8 all need the same table-extraction logic. A shared helper avoids four copies.

3. **Section parsing is shared** — FR-6 (KNOWLEDGE.md) and FR-7 (ARCHITECTURE.md) both split by `### XX-\d+:` headings and parse bold-prefixed fields. Same helper, but **different field formats**: KNOWLEDGE.md uses bulleted `- **Field**: value`, ARCHITECTURE.md uses unbulleted `**Field**: value`. The helper's `field_pattern` parameter handles this.

4. **`ParseResult[T]` is the universal return type** — every parser returns data + warnings. This is a simple generic wrapper.

5. **Pydantic handles the YAML coercion problem** — pyyaml coerces `2026-02-02` to `datetime.date` and `yes`/`no` to booleans. Rather than fighting this in the YAML layer, the Pydantic models use `str` for dates and handle coerced types via `model_validator` or simple `str()` conversion in the frontmatter extraction step.

---

## Proposed Design

### High-Level Architecture

```
src/agentic_mbse/pm/
├── __init__.py          # Public API: re-exports all parse_* functions and models
├── types.py             # Pydantic models, enums, ParseResult, ParseWarning
└── parser.py            # All 8 parsers + shared helpers
```

Three files. `types.py` owns all data models. `parser.py` owns all parsing logic. `__init__.py` re-exports the public API.

### Module: `pm/types.py`

All Pydantic models and enums. No parsing logic.

#### Core Infrastructure

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from enum import Enum

T = TypeVar("T")

class ParseWarning(BaseModel):
    """A non-fatal issue encountered during parsing."""
    file: str
    location: str  # line number, field name, row index, etc.
    message: str

class ParseResult(BaseModel, Generic[T]):
    """Result of a parse operation: data + accumulated warnings."""
    data: T
    warnings: list[ParseWarning] = Field(default_factory=list)
```

#### Enums

Following the `ValidationCode(str, Enum)` pattern from `sysml/types.py:66`:

```python
class EpicStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"

class WorkItemStatus(str, Enum):
    BACKLOG = "backlog"
    ACTIVE = "active"
    PAUSED = "paused"
    ABANDONED = "abandoned"
    FAILED = "failed"
    COMPLETED = "completed"

class WorkItemScale(str, Enum):
    TRIVIAL = "trivial"
    STANDARD = "standard"

class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class InsightStatus(str, Enum):
    CAPTURED = "captured"
    ADDRESSED = "addressed"
    SUPERSEDED = "superseded"

class DecisionStatus(str, Enum):
    ACTIVE = "active"
    REVISED = "revised"
    SUPERSEDED = "superseded"

class VerificationType(str, Enum):
    REASONABLENESS = "reasonableness"
    BASELINE = "baseline"
    PHYSICAL = "physical"
    RELATIONSHIP = "relationship"
    ROLLUP = "rollup"

class VerificationMechanism(str, Enum):
    MODEL = "model"
    TEST = "test"
    MANUAL = "manual"

class VerificationStatus(str, Enum):
    PASSING = "passing"
    FAILING = "failing"
    PENDING = "pending"
```

#### Entity Models

Each model matches the spec exactly. All use `BaseModel` with simple types.

```python
# --- Backlog entities (FR-3) ---
class WorkItemEntry(BaseModel):
    id: str          # WI-XXX
    name: str
    scale: WorkItemScale
    status: WorkItemStatus
    completed: str | None = None  # YYYY-MM-DD or None

class EpicEntry(BaseModel):
    name: str
    goal: str | None = None      # G-XXX or None
    priority: Priority
    status: EpicStatus
    file: str                    # relative path
    items: list[WorkItemEntry] = Field(default_factory=list)

class StandaloneEntry(BaseModel):
    id: str          # WI-XXX
    name: str
    scale: WorkItemScale
    priority: Priority
    status: WorkItemStatus
    completed: str | None = None

class BacklogData(BaseModel):
    epics: list[EpicEntry] = Field(default_factory=list)
    standalone: list[StandaloneEntry] = Field(default_factory=list)

# --- Requirements (FR-4) ---
class RequirementEntry(BaseModel):
    id: str              # PR-XXX
    requirement: str
    source: str
    enforcement: str
    validation_method: str

# --- Validation Matrix (FR-5) ---
class ValidationEntry(BaseModel):
    id: str              # SV-XXX
    description: str
    type: VerificationType
    mechanism: VerificationMechanism
    expected: str
    tolerance: str
    source: str
    test: str
    status: VerificationStatus

# --- Knowledge (FR-6) ---
class InsightEntry(BaseModel):
    id: str              # DI-XXX
    title: str
    source: str
    rationale: str | None = None
    context: str
    model_implications: str
    analysis_implications: str
    status: InsightStatus
    superseded_by: str | None = None
    supersedes: str | None = None

# --- Architecture (FR-7) ---
class DecisionEntry(BaseModel):
    id: str              # AD-XXX
    title: str
    decision: str
    rationale: str
    date: str
    status: DecisionStatus

# --- Overview (FR-8) ---
class GoalEntry(BaseModel):
    id: str              # G-XXX
    goal: str
    priority: str
    status: str
    source: str
    traced_requirements: str

class AnalysisQuestionEntry(BaseModel):
    id: str              # AQ-XXX
    question: str
    implies: str
    source: str
    status: str

class OverviewData(BaseModel):
    goals: list[GoalEntry] = Field(default_factory=list)
    questions: list[AnalysisQuestionEntry] = Field(default_factory=list)

# --- Traceability (FR-9) ---
class TraceabilityEntry(BaseModel):
    element: str
    file: str
    type: str
    knowledge: list[str] = Field(default_factory=list)   # split from comma-separated DI-XXX
    requirement: list[str] = Field(default_factory=list)  # split from comma-separated PR-XXX
    source_type: str
    source_document: str
    source_location: str
    confidence: str
    assumptions: str
    last_verified: str
```

#### Design Decisions for Types

**Why `str` for dates, not `datetime.date`**: pyyaml may deliver dates as `datetime.date` objects or as strings depending on formatting. Using `str` and converting in the parser layer avoids Pydantic validation errors. The PM engine can parse dates when it needs to compare them.

**Why `str` for `GoalEntry.priority`/`status` etc.**: The OVERVIEW.md tables are less rigidly typed than BACKLOG.md. The spec doesn't define enum values for goal status or priority. Using `str` keeps the parser flexible. If enum validation is needed later, these can be tightened without breaking the API.

**Why separate `StandaloneEntry` from `WorkItemEntry`**: Standalone items have a `priority` field that epic work items don't (epic items inherit priority from the epic). The spec defines them as distinct structures.

### Module: `pm/parser.py`

All parsing functions and shared helpers. No models (those are in `types.py`).

#### Shared Helpers (private)

```python
def _strip_html_comments(text: str) -> str:
    """Remove all HTML comments (<!-- ... -->) from text, including multi-line."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

def _warn(warnings: list[ParseWarning], file: str, location: str, message: str) -> None:
    """Append a warning to the list."""
    warnings.append(ParseWarning(file=str(file), location=location, message=message))

def _parse_markdown_table(
    text: str,
    section_heading: str | None,
    file_path: str,
    warnings: list[ParseWarning],
) -> list[dict[str, str]]:
    """Extract rows from a markdown table, optionally under a specific heading.

    IMPORTANT: `text` must be the file body AFTER frontmatter stripping.
    Callers that use parse_frontmatter get the body naturally (content after
    the closing ---). Callers that read the file directly must strip
    frontmatter before calling this helper. This ensures --- horizontal
    rules in the body are correctly treated as section terminators without
    confusion with YAML frontmatter delimiters.

    Returns a list of dicts mapping column-name → cell-value for each data row.

    Algorithm:
    1. If section_heading given, find that heading and take text from there
       to next ## heading or end of text
    2. Find first line matching `| ... |` (header row), extract column names
    3. Skip separator row (|---|...)
    4. Parse each subsequent `| ... |` line as a data row
    5. Stop at next heading (##), horizontal rule (--- on its own line), or end of text
    """

def _parse_heading_sections(
    text: str,
    heading_pattern: str,   # e.g. r"### (DI-\d+):\s*(.+)"
    field_pattern: str,     # caller-supplied — differs per file type (see below)
    file_path: str,
    warnings: list[ParseWarning],
) -> list[tuple[str, str, dict[str, str]]]:
    """Split text into sections by heading regex, parse field lines in each.

    Returns list of (id, title, fields_dict) tuples.
    Field names in the dict are normalized to title case as they appear
    in the bold markers (e.g. "Source", "Model implications").

    Algorithm:
    1. Strip HTML comments from text
    2. Find all matches of heading_pattern with their positions
    3. For each section between headings, extract fields matching field_pattern
    4. Multi-line values: if a line doesn't match field_pattern or a new heading,
       append to previous field value (stripped)
    """
```

**`_parse_markdown_table` detail**: The helper returns raw `dict[str, str]` — the caller validates each row against its specific schema and builds typed models. This keeps the helper reusable across FR-4, FR-5, FR-8.

**`_parse_heading_sections` detail**: Returns raw `(id, title, fields_dict)` — the caller maps field names to model attributes. This keeps the helper reusable across FR-6, FR-7.

**Two field patterns** — the templates use different formats:

| File | Format | `field_pattern` |
|------|--------|----------------|
| KNOWLEDGE.md | Bulleted: `- **Source**: value` | `r"^-\s+\*\*(.+?)\*\*:\s*(.+)"` |
| ARCHITECTURE.md | Unbulleted: `**Decision**: value` | `r"^\*\*(.+?)\*\*:\s*(.+)"` |

FR-6 (`parse_knowledge`) passes the bulleted pattern. FR-7 (`parse_architecture`) passes the unbulleted pattern. The helper itself is format-agnostic — it just applies whatever regex the caller provides.

#### Public Parse Functions

Each function signature and behavior:

**FR-2: `parse_frontmatter(path: Path) -> ParseResult[dict[str, Any]]`**

```
1. Read file, handle FileNotFoundError → empty dict + warning
   Empty/whitespace-only file → empty dict, no warnings (valid empty state)
2. Check first line is "---", if not → empty dict + warning
3. Find closing "---", if missing → empty dict + warning
4. yaml.safe_load() the content between delimiters
5. Handle yaml.YAMLError → empty dict + warning with error detail
6. Convert datetime.date/bool values to strings in the returned dict
   (pyyaml coerces unquoted dates and yes/no — normalize here)
7. Return ParseResult(data=dict, warnings=warnings)
```

**FR-3: `parse_backlog(path: Path) -> ParseResult[BacklogData]`**

```
1. Call parse_frontmatter(path) — get raw dict + its warnings
2. Extract `epics` list from dict (default []), warn if not a list
3. For each epic dict:
   a. Validate required fields (name, priority, status, file)
   b. Validate priority ∈ Priority enum, status ∈ EpicStatus enum
   c. Parse items[] list same way (validate id ~ WI-\d+, scale, status)
   d. Check completed date present when status=completed
   e. Skip invalid items with warning, build valid EpicEntry
4. Extract `standalone` list, same validation pattern
5. Return ParseResult(data=BacklogData(...), warnings=all_warnings)
```

**FR-4: `parse_requirements(path: Path) -> ParseResult[list[RequirementEntry]]`**

```
1. Read file, handle FileNotFoundError → empty list + warning
   Empty/whitespace-only file → empty list, no warnings
2. Strip HTML comments
3. Call _parse_markdown_table(text, "## Requirements", ...)
4. For each row dict:
   a. Check id matches PR-\d+ (skip + warn if not)
   b. Map columns: ID→id, Requirement→requirement, Source→source,
      Enforcement→enforcement, Validation Method→validation_method
   c. Build RequirementEntry
5. Return ParseResult(data=entries, warnings=warnings)
```

**FR-5: `parse_validation_matrix(path: Path) -> ParseResult[list[ValidationEntry]]`**

```
1. Read file, handle FileNotFoundError → empty list + warning
   Empty/whitespace-only file → empty list, no warnings
2. Strip HTML comments
3. Call _parse_markdown_table(text, "## Verification Registry", ...)
4. For each row dict:
   a. Check id matches SV-\d+ (skip + warn if not)
   b. Validate type ∈ VerificationType, mechanism ∈ VerificationMechanism,
      status ∈ VerificationStatus (skip + warn on invalid)
   c. Build ValidationEntry
5. Return ParseResult(data=entries, warnings=warnings)
```

**FR-6: `parse_knowledge(path: Path) -> ParseResult[list[InsightEntry]]`**

```
1. Read file, handle FileNotFoundError → empty list + warning
   Empty/whitespace-only file → empty list, no warnings
2. Call _parse_heading_sections(text,
     heading_pattern=r"### (DI-\d+):\s*(.+)",
     field_pattern=r"^-\s+\*\*(.+?)\*\*:\s*(.+)",  # bulleted format
     ...)
3. For each (id, title, fields):
   a. Map: Source→source, Rationale→rationale, Context→context,
      Model implications→model_implications, Analysis implications→analysis_implications,
      Status→status, Superseded-by→superseded_by, Supersedes→supersedes
   b. Validate status ∈ InsightStatus (skip + warn if invalid)
   c. Warn on missing required fields (Source, Context, Model implications,
      Analysis implications, Status), but include entry with empty strings
   d. Build InsightEntry
4. Return ParseResult(data=entries, warnings=warnings)
```

**FR-7: `parse_architecture(path: Path) -> ParseResult[list[DecisionEntry]]`**

```
1. Read file, handle FileNotFoundError → empty list + warning
   Empty/whitespace-only file → empty list, no warnings
2. Find "## Key Decisions" section, take text from there to next ## or end
   If section not found → empty list, no warnings (AP-1)
3. Call _parse_heading_sections(section_text,
     heading_pattern=r"### (AD-\d+):\s*(.+)",
     field_pattern=r"^\*\*(.+?)\*\*:\s*(.+)",  # unbulleted format
     ...)
4. For each (id, title, fields):
   a. Map: Decision→decision, Rationale→rationale, Date→date, Status→status
   b. Validate status ∈ DecisionStatus (skip + warn if invalid)
   c. Warn on missing required fields, include with empty strings
   d. Build DecisionEntry
5. Return ParseResult(data=entries, warnings=warnings)
```

**FR-8: `parse_overview(path: Path) -> ParseResult[OverviewData]`**

```
1. Read file, handle FileNotFoundError → OverviewData() + warning
   Empty/whitespace-only file → OverviewData(), no warnings
2. Strip HTML comments
3. Call _parse_markdown_table(text, "## Goals Registry", ...) → goal rows
4. For each goal row: check id ~ G-\d+ (skip + warn), build GoalEntry
5. Call _parse_markdown_table(text, "## Analysis Questions", ...) → question rows
6. For each question row: check id ~ AQ-\d+ (skip + warn), build AnalysisQuestionEntry
7. Return ParseResult(data=OverviewData(goals=..., questions=...), warnings=warnings)
```

**FR-9: `parse_traceability(path: Path) -> ParseResult[list[TraceabilityEntry]]`**

```
1. Open file with csv.DictReader, handle FileNotFoundError → empty list + warning
2. Normalize header names to lowercase for case-insensitive matching
3. Warn on missing expected columns
4. For each row:
   a. Split Knowledge column by "," → list[str], strip whitespace
   b. Split Requirement column by "," → list[str], strip whitespace
   c. Filter out empty strings from splits
   d. Build TraceabilityEntry
5. Return ParseResult(data=entries, warnings=warnings)
```

### Module: `pm/__init__.py`

```python
"""Project Management file parsers.

Provides typed, validated access to structured project files:
BACKLOG.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md,
ARCHITECTURE.md, OVERVIEW.md, and traceability_matrix.csv.
"""

from agentic_mbse.pm.types import (
    # Infrastructure
    ParseWarning,
    ParseResult,
    # Enums
    EpicStatus,
    WorkItemStatus,
    WorkItemScale,
    Priority,
    InsightStatus,
    DecisionStatus,
    VerificationType,
    VerificationMechanism,
    VerificationStatus,
    # Entity models
    WorkItemEntry,
    EpicEntry,
    StandaloneEntry,
    BacklogData,
    RequirementEntry,
    ValidationEntry,
    InsightEntry,
    DecisionEntry,
    GoalEntry,
    AnalysisQuestionEntry,
    OverviewData,
    TraceabilityEntry,
)
from agentic_mbse.pm.parser import (
    parse_frontmatter,
    parse_backlog,
    parse_requirements,
    parse_validation_matrix,
    parse_knowledge,
    parse_architecture,
    parse_overview,
    parse_traceability,
)

__all__ = [
    # Infrastructure
    "ParseWarning",
    "ParseResult",
    # Enums
    "EpicStatus",
    "WorkItemStatus",
    "WorkItemScale",
    "Priority",
    "InsightStatus",
    "DecisionStatus",
    "VerificationType",
    "VerificationMechanism",
    "VerificationStatus",
    # Entity models
    "WorkItemEntry",
    "EpicEntry",
    "StandaloneEntry",
    "BacklogData",
    "RequirementEntry",
    "ValidationEntry",
    "InsightEntry",
    "DecisionEntry",
    "GoalEntry",
    "AnalysisQuestionEntry",
    "OverviewData",
    "TraceabilityEntry",
    # Parsers
    "parse_frontmatter",
    "parse_backlog",
    "parse_requirements",
    "parse_validation_matrix",
    "parse_knowledge",
    "parse_architecture",
    "parse_overview",
    "parse_traceability",
]
```

### Dependencies

- `pyyaml` (existing — `pyproject.toml`)
- `pydantic` (existing — `pyproject.toml`)
- `csv` (stdlib)
- `re` (stdlib)
- `pathlib` (stdlib)

No new dependencies required (FR-12).

### Error Handling Strategy

All parsers follow the same pattern:

1. **FileNotFoundError** → `ParseResult(data=<empty>, warnings=[warning])` — never raises
2. **Empty/whitespace-only file** → `ParseResult(data=<empty>, warnings=[])` — valid empty state, no warnings
3. **Malformed content** → partial parse + warnings — never crashes
3. **Invalid enum values** → skip the entry + warning naming the bad value and allowed values
4. **Missing required fields** → include entry with empty strings + warning
5. **Extra columns/fields** → silently ignored (forwards compatibility)
6. **No side effects** (FR-11) — no prints, no file writes, no global state

---

## Testing Strategy

### Test File: `tests/test_pm_parser.py`

### Test Fixtures: `tests/fixtures/pm/`

Fixture files for each parser — both populated and empty-state versions:

```
tests/fixtures/pm/
├── backlog_populated.md           # BACKLOG.md with epics and standalone items
├── backlog_malformed.md           # Bad statuses, missing fields
├── requirements_populated.md      # REQUIREMENTS.md with PR-XXX rows
├── requirements_with_hr.md        # Table section followed by --- horizontal rule
├── validation_matrix_populated.md
├── knowledge_populated.md         # KNOWLEDGE.md with DI-XXX entries (bulleted fields)
├── knowledge_with_comments.md     # DI entries + HTML comment examples
├── architecture_populated.md      # ARCHITECTURE.md with AD-XXX decisions (unbulleted fields)
├── overview_populated.md          # OVERVIEW.md with goals and questions
└── traceability_populated.csv
```

### Test Cases Per Parser (≥4 each)

For each parser, at minimum:

1. **Valid populated** — full content, all fields, correct types → expected models
2. **Valid empty** — template file from `project_templates/` → empty collections, no warnings
3. **Missing file** — nonexistent path → empty data + "File not found" warning
4. **Malformed content** — invalid enum values, missing fields, bad IDs → partial results + specific warnings

Additional cases as appropriate:
- HTML comments not parsed as data
- Unclosed HTML comment (`<!--` with no `-->`) — should not consume the rest of the file
- Multi-line field values (knowledge/architecture sections)
- YAML type coercion (dates, booleans)
- Multi-value CSV fields (comma-separated DI-XXX, PR-XXX)
- Extra columns silently ignored
- Missing columns warned
- Empty file (exists but 0 bytes) → empty data, no warnings
- `---` horizontal rules between sections don't confuse table scoping (M-1 edge case)
- ARCHITECTURE.md unbulleted `**Field**: value` vs KNOWLEDGE.md bulleted `- **Field**: value` both parse correctly

### Empty-State Tests (AP-1)

Dedicated test function that parses each actual template file from `project_templates/`:

```python
def test_backlog_template_empty_state():
    path = Path(__file__).parent.parent / "project_templates" / "BACKLOG.md.template"
    result = parse_backlog(path)
    assert result.data == BacklogData(epics=[], standalone=[])
    assert result.warnings == []

# ... similar for all 7 templates
```

This directly tests against the real templates, ensuring parsers stay in sync with template changes.

---

## Potential Risks

| Risk | Mitigation |
|------|-----------|
| Regex for HTML comment stripping could be too greedy or miss edge cases | Use `re.DOTALL` with non-greedy `.*?`; test with nested/adjacent comments |
| Unclosed `<!--` could consume rest of file | Non-greedy `.*?` limits damage, but an unclosed comment with no closing `-->` means the regex won't match at all (no stripping occurs) — this is the correct behavior. Add a defensive test case. |
| Markdown table parsing fragile if templates change format | Tests parse actual template files (AP-1 tests) — breakage caught immediately |
| `---` horizontal rules confused with YAML frontmatter | `_parse_markdown_table` receives body text after frontmatter stripping, so `---` in the body is always a horizontal rule. Documented as a caller contract. |
| YAML coercion surprises beyond dates and booleans | `parse_frontmatter` normalizes all non-string scalar values to strings; Pydantic models use `str` for flexible fields |
| `ParseResult[T]` generic may need Pydantic v2 Generic handling | Pydantic v2 supports `BaseModel` + `Generic[T]` natively; validated in `sysml/types.py` patterns |

## Integration Strategy

- **D4.2 (state derivation)** will call `parse_backlog()`, `parse_frontmatter()` on spec.md/design.md/plan.md files, and scan `work/active/` directories
- **D4.3 (dashboard)** will call all parsers to aggregate project state for display
- **D4.4 (operations)** will read via parsers, write via separate mutation functions
- Parsers are stateless and side-effect-free — safe to call from any context

## Validation Approach

1. **Unit tests**: `uv run pytest tests/test_pm_parser.py` — all test cases above
2. **Type checking**: `uv run mypy src/agentic_mbse/pm/` — must pass clean
3. **Linting**: `uv run ruff check src/agentic_mbse/pm/` — must pass
4. **Template sync**: AP-1 tests parse real templates, catching format drift
5. **Existing tests**: `uv run pytest tests/` — must still pass (no regressions)

---

Next Step: After approval → `/_my_implement` or `/_my_plan`

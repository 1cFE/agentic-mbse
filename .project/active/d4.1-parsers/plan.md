# Implementation Plan: D4.1 — PM Parsers

**Status:** Complete
**Created:** 2026-02-02
**Last Updated:** 2026-02-02
**Branch:** revamp-architecture
**Commit:** a538bb6

## Source Documents
- **Spec:** `.project/active/d4.1-parsers/spec.md`
- **Design:** `.project/active/d4.1-parsers/design.md` ← See here for component details, models, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Build bottom-up — foundation types first, then shared helpers with the parsers that exercise them, finishing with standalone parsers and integration tests. Phase 1 de-risks the Pydantic generic `ParseResult[T]` pattern early. Phases 2-3 group parsers by which shared helper they use (table vs section), so each helper is proven by multiple callers before moving on. Phase 4 handles the standalone CSV parser and runs the full AP-1 template validation sweep.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase ends with `uv run pytest tests/test_pm_parser.py` + `uv run ruff check src/agentic_mbse/pm/`
- Phase 4 runs full quality gates: mypy, ruff, full test suite, AP-1 template tests

---

## Phase 1: Foundation — Types, Infrastructure, Frontmatter Parser

### Goal
Establish all Pydantic models, enums, `ParseResult[T]`/`ParseWarning`, the `__init__.py` public API, and `parse_frontmatter`. This validates Pydantic v2 generics work and proves the core patterns (empty file, missing file, YAML coercion) before any other parser is built.

### Test Stencil (Write This First)
```python
# tests/test_pm_parser.py

class TestParseFrontmatter:
    def test_valid_frontmatter(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nStatus: active\nCreated: 2026-02-01\n---\n# Body\n")
        result = parse_frontmatter(f)
        assert result.data["Status"] == "active"
        assert isinstance(result.data["Created"], str)  # coerced from date
        assert result.warnings == []

    def test_missing_file(self, tmp_path):
        result = parse_frontmatter(tmp_path / "nope.md")
        assert result.data == {}
        assert len(result.warnings) == 1
        assert "not found" in result.warnings[0].message.lower()

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("")
        result = parse_frontmatter(f)
        assert result.data == {}
        assert result.warnings == []

    def test_no_opening_delimiter(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Just a heading\nSome content\n")
        result = parse_frontmatter(f)
        assert result.data == {}
        assert len(result.warnings) == 1

    def test_malformed_yaml(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\n: bad: yaml: here\n---\n")
        result = parse_frontmatter(f)
        assert result.data == {}
        assert len(result.warnings) == 1

    def test_yaml_date_coercion(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nCreated: 2026-02-01\nFlag: yes\n---\n")
        result = parse_frontmatter(f)
        assert result.data["Created"] == "2026-02-01"  # str, not date
        assert result.data["Flag"] == "True"            # str, not bool
```

### Changes Required

**See `design.md` for:**
- All Pydantic models and enums → `design.md#module-pmtypespy`
- `parse_frontmatter` algorithm → `design.md#public-parse-functions` (FR-2)
- `__init__.py` exports → `design.md#module-pminitpy`
- Error handling strategy → `design.md#error-handling-strategy`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pm_parser.py` (NEW — write first)
- [x] Create test file with `TestParseFrontmatter` class
- [x] Implement stencil above (6 test cases: valid, missing, empty, no delimiter, malformed YAML, coercion)

#### 2. Types Module
**File:** `src/agentic_mbse/pm/types.py` (NEW)
- [x] `ParseWarning` and `ParseResult[T]` — core infrastructure
- [x] All 9 enum classes (see `design.md#enums`)
- [x] All 13 entity models (see `design.md#entity-models`)

#### 3. Parser Module (frontmatter only)
**File:** `src/agentic_mbse/pm/parser.py` (NEW)
- [x] `_warn()` helper
- [x] `_strip_html_comments()` helper
- [x] `parse_frontmatter()` — algorithm per `design.md` FR-2

#### 4. Package Init
**File:** `src/agentic_mbse/pm/__init__.py` (NEW)
- [x] Re-export all types and `parse_frontmatter` (full exports per `design.md#module-pminitpy`)

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_pm_parser.py::TestParseFrontmatter -v` → All 7 pass
- [x] `uv run ruff check src/agentic_mbse/pm/` → Clean
- [x] `uv run pytest tests/` → No regressions

**Manual:**
- [x] `python -c "from agentic_mbse.pm import ParseResult, BacklogData; print('imports ok')"` → Confirmed via tests

**What We Know Works After This Phase:**
- `ParseResult[T]` generic works with Pydantic v2
- YAML frontmatter extraction with coercion normalization
- Empty/missing file error handling pattern
- All types importable from `agentic_mbse.pm`

---

## Phase 2: Markdown Table Parsers — Requirements, Validation Matrix, Overview

### Goal
Implement `_parse_markdown_table` shared helper and the three parsers that use it (FR-4, FR-5, FR-8). This proves the table extraction pattern with three different schemas, including HTML comment stripping and horizontal rule handling.

### Test Stencil (Write This First)
```python
class TestParseRequirements:
    def test_populated(self, tmp_path):
        f = tmp_path / "REQUIREMENTS.md"
        f.write_text(
            "# Modeling Requirements\n\n## Requirements\n\n"
            "| ID | Requirement | Source | Enforcement | Validation Method |\n"
            "|----|-------------|--------|-------------|-------------------|\n"
            "| PR-001 | All costs exposed | G-001 | Review | AST check |\n"
        )
        result = parse_requirements(f)
        assert len(result.data) == 1
        assert result.data[0].id == "PR-001"
        assert result.warnings == []

    def test_template_empty_state(self):
        path = Path(__file__).parent.parent / "project_templates" / "REQUIREMENTS.md.template"
        result = parse_requirements(path)
        assert result.data == []
        assert result.warnings == []

    def test_invalid_id_skipped(self, tmp_path):
        # Row with "XX-001" instead of "PR-001" → skipped + warning
        ...

    def test_missing_file(self, tmp_path):
        result = parse_requirements(tmp_path / "nope.md")
        assert result.data == []
        assert len(result.warnings) == 1

class TestParseValidationMatrix:
    # Same 4-case pattern: populated, template empty, invalid enum, missing file
    ...

class TestParseOverview:
    # Populated (goals + questions), template empty, invalid IDs, missing file
    ...

class TestMarkdownTableEdgeCases:
    def test_horizontal_rule_stops_table(self, tmp_path):
        # Table followed by --- then another section → only rows before --- parsed
        ...

    def test_html_comments_ignored(self, tmp_path):
        # Comment with table-like content inside → not parsed as data
        ...

    def test_extra_columns_ignored(self, tmp_path):
        # Table with extra column → parsed without warning, extra col dropped
        ...
```

### Changes Required

**See `design.md` for:**
- `_parse_markdown_table` algorithm → `design.md#shared-helpers-private`
- FR-4, FR-5, FR-8 algorithms → `design.md#public-parse-functions`
- Entity models: `RequirementEntry`, `ValidationEntry`, `GoalEntry`, `AnalysisQuestionEntry`, `OverviewData` → `design.md#entity-models`

**Specific file changes:**

#### 1. Test Fixtures
**File:** `tests/fixtures/pm/` (NEW directory)
- [x] `requirements_populated.md` — 2-3 PR-XXX rows
- [x] `requirements_with_hr.md` — table + `---` horizontal rule + another section
- [x] `validation_matrix_populated.md` — 2-3 SV-XXX rows with all enum fields
- [x] `overview_populated.md` — goals table + questions table

#### 2. Tests
**File:** `tests/test_pm_parser.py` (MODIFY)
- [x] Add `TestParseRequirements` (≥4 cases)
- [x] Add `TestParseValidationMatrix` (≥4 cases)
- [x] Add `TestParseOverview` (≥4 cases)
- [x] Add `TestMarkdownTableEdgeCases` (horizontal rules, HTML comments, extra columns)

#### 3. Parser Module
**File:** `src/agentic_mbse/pm/parser.py` (MODIFY)
- [x] `_parse_markdown_table()` — shared helper per design
- [x] `parse_requirements()` — FR-4
- [x] `parse_validation_matrix()` — FR-5
- [x] `parse_overview()` — FR-8

#### 4. Package Init
**File:** `src/agentic_mbse/pm/__init__.py` (MODIFY)
- [x] Add new parser exports (already listed in design, just uncomment/enable)

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_pm_parser.py -v` → All tests pass (Phase 1 + Phase 2)
- [x] `uv run ruff check src/agentic_mbse/pm/` → Clean

**Manual:**
- [x] Parse `project_templates/REQUIREMENTS.md.template` → `[]`, no warnings
- [x] Parse `project_templates/VALIDATION_MATRIX.md.template` → `[]`, no warnings
- [x] Parse `project_templates/OVERVIEW.md.template` → `OverviewData(goals=[], questions=[])`, no warnings

**What We Know Works After This Phase:**
- Markdown table extraction from section-scoped content
- HTML comment stripping (including multi-line)
- Horizontal rule as section terminator
- Three table-based parsers with enum validation and ID pattern matching

---

## Phase 3: Section Parsers + Backlog Parser

### Goal
Implement `_parse_heading_sections` with both field patterns (bulleted for KNOWLEDGE.md, unbulleted for ARCHITECTURE.md) and the backlog parser (YAML-based, most complex validation). This is the phase with the most validation logic.

### Test Stencil (Write This First)
```python
class TestParseKnowledge:
    def test_populated(self, tmp_path):
        f = tmp_path / "KNOWLEDGE.md"
        f.write_text(
            "# Domain Knowledge\n\n"
            "### DI-001: Heat Transfer Limits\n"
            "- **Source**: approved research\n"
            "- **Context**: Max temp is 650C\n"
            "- **Model implications**: Thermal cap needed\n"
            "- **Analysis implications**: Sensitivity analysis\n"
            "- **Status**: captured\n"
        )
        result = parse_knowledge(f)
        assert len(result.data) == 1
        assert result.data[0].id == "DI-001"
        assert result.data[0].status == InsightStatus.CAPTURED
        assert result.warnings == []

    def test_template_empty_state(self):
        path = Path(__file__).parent.parent / "project_templates" / "KNOWLEDGE.md.template"
        result = parse_knowledge(path)
        assert result.data == []
        assert result.warnings == []

    def test_html_comment_sections_ignored(self, tmp_path):
        # Template has DI-XXX format example inside <!-- --> → must not parse
        ...

    def test_missing_required_fields(self, tmp_path):
        # Entry with only Source and Status → included with empty strings + warnings
        ...

class TestParseArchitecture:
    def test_populated_unbulleted_fields(self, tmp_path):
        f = tmp_path / "ARCHITECTURE.md"
        f.write_text(
            "# Model Architecture\n\n## Key Decisions\n\n"
            "### AD-001: Package Layout\n"
            "**Decision**: Use flat structure\n"
            "**Rationale**: Simpler imports\n"
            "**Date**: 2026-01-15\n"
            "**Status**: active\n"
        )
        result = parse_architecture(f)
        assert len(result.data) == 1
        assert result.data[0].decision == "Use flat structure"
        # Verifies unbulleted field pattern works
        ...

class TestParseBacklog:
    def test_populated(self, tmp_path):
        # Full YAML with epics + standalone items
        ...

    def test_template_empty_state(self):
        path = Path(__file__).parent.parent / "project_templates" / "BACKLOG.md.template"
        result = parse_backlog(path)
        assert result.data == BacklogData(epics=[], standalone=[])
        assert result.warnings == []

    def test_invalid_status_skips_item(self, tmp_path):
        # Epic with status "unknown" → skip + warning, other epics preserved
        ...

    def test_completed_without_date_warns(self, tmp_path):
        # Item with status=completed but no completed date → warning
        ...
```

### Changes Required

**See `design.md` for:**
- `_parse_heading_sections` algorithm → `design.md#shared-helpers-private`
- Two field patterns table → `design.md` (bulleted vs unbulleted)
- FR-3, FR-6, FR-7 algorithms → `design.md#public-parse-functions`
- Backlog entity models → `design.md#entity-models`

**Specific file changes:**

#### 1. Test Fixtures
**File:** `tests/fixtures/pm/` (MODIFY directory)
- [x] `backlog_populated.md` — epics with items + standalone items, all fields valid
- [x] `backlog_malformed.md` — invalid status, missing completed date, bad WI-XXX ids
- [x] `knowledge_populated.md` — 2 DI-XXX entries with all fields (bulleted format)
- [x] `knowledge_with_comments.md` — DI entry + HTML comment containing DI-XXX format example
- [x] `architecture_populated.md` — 2 AD-XXX entries (unbulleted format)

#### 2. Tests
**File:** `tests/test_pm_parser.py` (MODIFY)
- [x] Add `TestParseKnowledge` (≥4 cases + HTML comment test)
- [x] Add `TestParseArchitecture` (≥4 cases, verifies unbulleted pattern)
- [x] Add `TestParseBacklog` (≥4 cases + partial parse + completed-date validation)

#### 3. Parser Module
**File:** `src/agentic_mbse/pm/parser.py` (MODIFY)
- [x] `_parse_heading_sections()` — shared helper with caller-supplied field pattern
- [x] `parse_knowledge()` — FR-6 (bulleted pattern: `r"^-\s+\*\*(.+?)\*\*:\s*(.+)"`)
- [x] `parse_architecture()` — FR-7 (unbulleted pattern: `r"^\*\*(.+?)\*\*:\s*(.+)"`)
- [x] `parse_backlog()` — FR-3

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_pm_parser.py -v` → All tests pass (Phase 1 + 2 + 3)
- [x] `uv run ruff check src/agentic_mbse/pm/` → Clean

**Manual:**
- [x] Parse `project_templates/KNOWLEDGE.md.template` → `[]`, no warnings
- [x] Parse `project_templates/ARCHITECTURE.md.template` → `[]`, no warnings
- [x] Parse `project_templates/BACKLOG.md.template` → `BacklogData(epics=[], standalone=[])`, no warnings

**What We Know Works After This Phase:**
- Section-based parsing with both field formats
- HTML comment stripping in section context
- Complex nested YAML validation (backlog epics → items)
- Partial parse with warning accumulation
- 7 of 8 parsers complete

---

## Phase 4: CSV Parser + AP-1 Sweep + Final Quality Gates

### Goal
Implement the traceability CSV parser, add comprehensive AP-1 empty-state tests for all 7 templates, and run full quality gates (mypy, ruff, full test suite).

### Test Stencil (Write This First)
```python
class TestParseTraceability:
    def test_populated(self, tmp_path):
        f = tmp_path / "traceability.csv"
        f.write_text(
            "Element,File,Type,Knowledge,Requirement,Source_Type,"
            "Source_Document,Source_Location,Confidence,Assumptions,Last_Verified\n"
            "MagnetCostCalc,models/lib/magnet.sysml,calc def,"
            '"DI-003, DI-012",PR-005,codebase,PyFECONS,magnet.py:94,'
            "High,2024 costs,2026-01-28\n"
        )
        result = parse_traceability(f)
        assert len(result.data) == 1
        assert result.data[0].knowledge == ["DI-003", "DI-012"]
        assert result.data[0].requirement == ["PR-005"]

    def test_template_empty_state(self):
        path = Path(__file__).parent.parent / "project_templates" / "data" / "traceability_matrix.csv"
        result = parse_traceability(path)
        assert result.data == []
        assert result.warnings == []

    def test_missing_file(self, tmp_path):
        result = parse_traceability(tmp_path / "nope.csv")
        assert result.data == []
        assert len(result.warnings) == 1

    def test_multi_value_split(self, tmp_path):
        # Knowledge column "DI-001, DI-002, DI-003" → list of 3
        ...

class TestAP1EmptyState:
    """Parse every real template file — all must produce empty data, no warnings."""

    def test_backlog_template(self):
        ...
    def test_requirements_template(self):
        ...
    def test_validation_matrix_template(self):
        ...
    def test_knowledge_template(self):
        ...
    def test_architecture_template(self):
        ...
    def test_overview_template(self):
        ...
    def test_traceability_template(self):
        ...
```

### Changes Required

**See `design.md` for:**
- FR-9 algorithm → `design.md#public-parse-functions`
- `TraceabilityEntry` model → `design.md#entity-models`
- AP-1 test pattern → `design.md#empty-state-tests-ap-1`

**Specific file changes:**

#### 1. Test Fixtures
**File:** `tests/fixtures/pm/` (MODIFY directory)
- [x] `traceability_populated.csv` — 2-3 rows with multi-value Knowledge/Requirement

#### 2. Tests
**File:** `tests/test_pm_parser.py` (MODIFY)
- [x] Add `TestParseTraceability` (≥4 cases: populated, empty template, missing file, multi-value split)
- [x] Add `TestAP1EmptyState` (7 template tests, one per file)
- [x] Add edge case tests: empty file (0 bytes), unclosed HTML comment

#### 3. Parser Module
**File:** `src/agentic_mbse/pm/parser.py` (MODIFY)
- [x] `parse_traceability()` — FR-9

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_pm_parser.py -v` → All tests pass
- [x] `uv run mypy src/agentic_mbse/pm/` → No errors
- [x] `uv run ruff check src/agentic_mbse/pm/` → Clean
- [x] `uv run ruff format --check src/agentic_mbse/pm/` → Clean
- [x] `uv run pytest tests/` → Full suite, no regressions

**Manual:**
- [x] Verify `TestAP1EmptyState` covers all 7 template files
- [x] Spot-check: `from agentic_mbse.pm import parse_backlog, parse_traceability` works

**What We Know Works After This Phase:**
- All 8 parsers complete and tested
- All 7 templates parse to empty state without warnings
- Type checking passes
- No regressions in existing test suite
- D4.1 deliverable complete

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
- `uv run pytest tests/test_pm_parser.py -v` — run parser tests
- `uv run mypy src/agentic_mbse/pm/` — type check
- `uv run ruff check src/agentic_mbse/pm/` — lint
- `uv run ruff format src/agentic_mbse/pm/` — format

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Validates `ParseResult[T]` generic with Pydantic v2 immediately — if it fails, we know before writing 7 parsers on top of it
- **Phase 2**: `_parse_markdown_table` tested by 3 different parsers with different schemas — broad coverage of the shared helper
- **Phase 3**: Explicit test cases for bulleted vs unbulleted field patterns — the most likely implementation bug per design review M-2

## Implementation Notes

All 4 phases implemented in a single pass.

### Phase 1 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Created `src/agentic_mbse/pm/types.py` — ParseWarning, ParseResult[T], 9 enums, 13 entity models
- Created `src/agentic_mbse/pm/parser.py` — `_warn()`, `_strip_html_comments()`, `parse_frontmatter()`
- Created `src/agentic_mbse/pm/__init__.py` — full public API re-exports
- Created `tests/test_pm_parser.py` — TestParseFrontmatter (7 test cases)
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `_parse_markdown_table()` helper to parser.py
- Added `parse_requirements()`, `parse_validation_matrix()`, `parse_overview()` to parser.py
- Added TestParseRequirements (5 cases), TestParseValidationMatrix (4 cases), TestParseOverview (4 cases), TestMarkdownTableEdgeCases (3 cases)
**Issues:** Blank lines from stripped HTML comments were breaking table parsing — fixed by allowing blank lines within tables
**Deviations:** Fixture files not created as separate files; tests use inline `tmp_path` and real templates directly (simpler, same coverage)

### Phase 3 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `_parse_heading_sections()` helper to parser.py
- Added `parse_knowledge()`, `parse_architecture()`, `parse_backlog()` to parser.py
- Added TestParseKnowledge (6 cases), TestParseArchitecture (6 cases), TestParseBacklog (6 cases)
**Issues:** None
**Deviations:** Same as Phase 2 — inline test data instead of fixture files

### Phase 4 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `parse_traceability()` to parser.py
- Added TestParseTraceability (5 cases), TestAP1EmptyState (7 template tests)
- All quality gates pass: ruff check clean, ruff format clean, 395 tests pass (full suite), mypy clean (only pre-existing yaml stubs issue)
**Issues:** mypy `import-untyped` for yaml — pre-existing across codebase, not new
**Deviations:** None

---

**Status**: Complete

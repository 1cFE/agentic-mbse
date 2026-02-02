# Implementation Plan: D4.4 AP-7 Operations

**Status:** Complete
**Created:** 2026-02-02
**Last Updated:** 2026-02-02

## Source Documents
- **Spec:** `.project/active/d4.4-operations/spec.md`
- **Design:** `.project/active/d4.4-operations/design.md` — See here for component details, function signatures, file formats, dependencies, error handling

## Implementation Strategy

**Phasing Rationale:**
Foundation-first, complexity-ascending. Phase 1 builds all shared infrastructure (types, helpers, write functions) and tests them in isolation — catching format bugs before they compound across operations. Phases 2-3 implement operations in order of increasing cross-file complexity. Phase 4 tackles the three in-place-mutation operations (the hardest write patterns). Phase 5 is mechanical cleanup.

**Overall Validation Approach:**
- Each phase starts with tests
- Round-trip correctness (write → parse → verify) is the primary correctness signal
- `uv run pytest tests/` after every phase to catch regressions

---

## Phase 1: Foundation — Types, ID Helper, Write Helpers

### Goal
Build all shared infrastructure that every operation depends on. This is the highest-leverage phase — every bug caught here prevents 14 downstream failures. The BACKLOG.md YAML round-trip is the single highest risk item.

### Test Stencil (Write This First)
```python
# tests/test_pm_operations.py

class TestNextId:
    def test_empty_list(self):
        assert _next_id("DI", []) == "DI-001"

    def test_sequential(self):
        assert _next_id("DI", ["DI-001", "DI-002"]) == "DI-003"

    def test_gap_uses_highest(self):
        assert _next_id("PR", ["PR-001", "PR-005"]) == "PR-006"

    def test_all_prefixes(self):
        for prefix in ("DI", "PR", "AD", "SV", "G", "AQ", "WI"):
            assert _next_id(prefix, []).startswith(f"{prefix}-")


class TestRenderBacklogBody:
    def test_empty_state(self):
        body = _render_backlog_body(BacklogData(epics=[], standalone=[]))
        assert "No epics or work items yet" in body

    def test_epic_with_items(self):
        # Build BacklogData with one epic, two items (one completed)
        # Assert: ## Epic: heading, item table, completed date in Notes

    def test_standalone_items(self):
        # Assert: ## Standalone Items heading, priority column present


class TestWriteBacklogRoundTrip:
    def test_round_trip(self, tmp_path):
        # Create BacklogData with epics + standalone
        # _write_backlog(path, data)
        # result = parse_backlog(path)
        # Assert result.data matches original data
        # _write_backlog(path, result.data)
        # Assert file content is identical (stable round-trip)


class TestFormatInsightEntry:
    def test_with_rationale(self):
        # Assert output contains "- **Rationale**:" line

    def test_without_rationale(self):
        # Assert output does NOT contain Rationale line

    def test_round_trip(self, tmp_path):
        # Write entry to file, parse_knowledge(), verify fields match


class TestAppendTableRow:
    def test_append_to_existing_table(self, tmp_path):
        # Create file with header+separator+1 row, append, verify 2 rows

    def test_append_to_empty_table(self, tmp_path):
        # Create file with header+separator only, append, verify 1 row

    def test_preserves_content_after_table(self, tmp_path):
        # Create file with table + ## Next Section, append row, verify section preserved
```

### Changes Required

**See `design.md` for:**
- Result type definitions → `design.md#component-1`
- ID assignment logic → `design.md#component-2`
- Write helper signatures and formats → `design.md#component-3`
- Markdown table append strategy → `design.md#component-5`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pm_operations.py` (NEW — write first)
- [ ] Create test file with imports from `agentic_mbse.pm`
- [ ] `TestNextId` — 4+ tests: empty, sequential, gap, all prefixes
- [ ] `TestRenderBacklogBody` — 3+ tests: empty, epic with items, standalone
- [ ] `TestWriteBacklogRoundTrip` — round-trip stability test
- [ ] `TestFormatInsightEntry` — with/without rationale, round-trip via `parse_knowledge`
- [ ] `TestFormatDecisionEntry` — round-trip via `parse_architecture`
- [ ] `TestFormatTableRow` — basic formatting
- [ ] `TestAppendTableRow` — existing table, empty table, content-after-table
- [ ] `TestAppendCsvRow` — existing CSV, empty/missing CSV
- [ ] `TestUpdateFrontmatterFields` — update Status, preserve unknown fields, preserve body

#### 2. Types
**File:** `src/agentic_mbse/pm/types.py`
- [ ] Add `OperationResult` model (see `design.md#component-1`)
- [ ] Add `ImpactResult` model
- [ ] Add `InsightInput` model (see `design.md` approve_research section)
- [ ] Add `GoalInput` model (see `design.md` register_intent section)
- [ ] Add `QuestionInput` model

#### 3. Operations Module — Helpers Only
**File:** `src/agentic_mbse/pm/operations.py` (NEW)
- [ ] `_next_id(prefix, existing_ids)` — ID assignment
- [ ] `_update_frontmatter_fields(path, updates)` — YAML frontmatter field update
- [ ] `_render_backlog_body(data)` — BACKLOG.md body from BacklogData
- [ ] `_write_backlog(path, data)` — full BACKLOG.md write (YAML + body)
- [ ] `_format_insight_entry(entry)` — DI-XXX markdown
- [ ] `_format_decision_entry(entry)` — AD-XXX markdown
- [ ] `_format_table_row(columns)` — markdown table row
- [ ] `_append_section(path, text)` — append heading-based section to EOF
- [ ] `_append_table_row(path, section_heading, row)` — section-scoped table append
- [ ] `_append_csv_row(path, row)` — CSV row append

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pm_operations.py -v` → All Phase 1 tests pass
- [ ] `uv run pytest tests/` → No regressions
- [ ] `uv run ruff check src/agentic_mbse/pm/operations.py`

**Manual:**
- [ ] BACKLOG.md round-trip: visually inspect that written file matches template format
- [ ] Insight entry round-trip: parse_knowledge output matches input fields exactly

**What We Know Works After This Phase:**
ID assignment is correct for all 7 prefixes. All write helpers produce output that existing parsers read back correctly. BACKLOG.md YAML serialization round-trips stably.

---

## Phase 2: Simple Append Operations

### Goal
Implement the 5 operations that each touch one file and append one entry: `add_insight`, `save_research`, `promote_requirement`, `register_decision`, `add_validation`. These exercise every write helper from Phase 1 against real project structures.

### Test Stencil (Write This First)
```python
class TestAddInsight:
    def test_happy_path(self, tmp_path):
        # Create project with empty KNOWLEDGE.md
        result = add_insight(tmp_path, title="Test", source="research.md",
                            context="A fact", model_implications="Must model X",
                            analysis_implications="Enables Y")
        assert result.success
        assert result.ids_assigned["DI"] == "DI-001"
        # parse_knowledge → verify entry matches

    def test_sequential_ids(self, tmp_path):
        # Add two insights, verify DI-001 then DI-002

    def test_missing_field(self, tmp_path):
        result = add_insight(tmp_path, title="", source="x", ...)
        assert not result.success

    def test_with_rationale(self, tmp_path):
        # Verify rationale field appears in output


class TestSaveResearch:
    def test_happy_path(self, tmp_path):
        result = save_research(tmp_path, topic="HTS magnets", content="# Research\n...")
        assert result.success
        # Verify file exists at knowledge/research/pending/YYYYMMDD-HHMMSS_hts-magnets.md

    def test_creates_pending_dir(self, tmp_path):
        # No pending/ dir exists yet — operation creates it

    def test_kebab_case(self, tmp_path):
        result = save_research(tmp_path, topic="Cost Model Updates!", content="x")
        # Verify filename uses "cost-model-updates"


class TestPromoteRequirement:
    def test_happy_path(self, tmp_path):
        # Create REQUIREMENTS.md from template
        result = promote_requirement(tmp_path, requirement="All X SHALL Y",
                                     source="DI-001", enforcement="Design review",
                                     validation_method="Manual check")
        assert result.ids_assigned["PR"] == "PR-001"
        # parse_requirements → verify row
```

### Changes Required

**See `design.md` for:**
- Operation signatures and validation rules → `design.md#component-4`
- Error handling convention → `design.md#component-4` (intro paragraph)

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_pm_operations.py`
- [ ] `TestAddInsight` — happy path, sequential IDs, missing field, with rationale, empty KNOWLEDGE.md
- [ ] `TestSaveResearch` — happy path, creates dir, kebab-case, empty topic/content
- [ ] `TestPromoteRequirement` — happy path, sequential IDs, invalid source pattern, all 5 columns present
- [ ] `TestRegisterDecision` — happy path, sequential IDs, date auto-set, missing fields
- [ ] `TestAddValidation` — happy path, sequential IDs, invalid type/mechanism enum, status=pending

#### 2. Operations
**File:** `src/agentic_mbse/pm/operations.py`
- [ ] `add_insight()` — see `design.md` for steps
- [ ] `save_research()` — see `design.md` for steps
- [ ] `promote_requirement()` — see `design.md` for steps
- [ ] `register_decision()` — see `design.md` for steps
- [ ] `add_validation()` — see `design.md` for steps

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pm_operations.py -v` → All Phase 1+2 tests pass
- [ ] `uv run pytest tests/` → No regressions

**Manual:**
- [ ] Run `add_insight` on a project with existing DI-003 → verify DI-004 assigned
- [ ] Run `save_research` → verify filename matches `YYYYMMDD-HHMMSS_topic.md` pattern

**What We Know Works After This Phase:**
5 operations produce correct output and handle errors. Every write helper is exercised against real file structures. ID assignment confirmed across DI, PR, AD, SV prefixes.

---

## Phase 3: Cross-File and Multi-File Operations

### Goal
Implement 4 operations with cross-file validation or multi-file writes: `trace_element`, `approve_research`, `register_intent`, `impact_query`.

### Test Stencil (Write This First)
```python
class TestTraceElement:
    def test_happy_path(self, tmp_path):
        # Create KNOWLEDGE.md with DI-001, REQUIREMENTS.md with PR-001, empty CSV
        result = trace_element(tmp_path, element="MagnetCostCalc",
                              file="models/library/magnet_cost.sysml", type="calc def",
                              knowledge=["DI-001"], requirement=["PR-001"])
        assert result.success
        # parse_traceability → verify row

    def test_invalid_knowledge_id(self, tmp_path):
        # Reference DI-999 that doesn't exist
        result = trace_element(tmp_path, ..., knowledge=["DI-999"])
        assert not result.success
        assert "DI-999" in result.message

    def test_duplicate_rejected(self, tmp_path):
        # Add same element+file twice → second fails


class TestApproveResearch:
    def test_happy_path(self, tmp_path):
        # Create pending file, call with 2 InsightInput objects
        # Verify: file moved to approved/, 2 DI entries in KNOWLEDGE.md

    def test_file_not_in_pending(self, tmp_path):
        # Path outside pending/ → failure


class TestImpactQuery:
    def test_by_knowledge_id(self, tmp_path):
        # CSV with 3 rows, 2 reference DI-001 → returns 2 affected elements

    def test_missing_csv(self, tmp_path):
        result = impact_query(tmp_path, query_id="DI-001")
        assert result.affected_elements == []
        assert len(result.warnings) > 0
```

### Changes Required

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_pm_operations.py`
- [ ] `TestTraceElement` — happy path, invalid DI-XXX, invalid PR-XXX, duplicate, last_verified default, empty CSV
- [ ] `TestApproveResearch` — happy path (multiple insights), file not in pending, missing file, append-then-move order
- [ ] `TestRegisterIntent` — goals only, questions only, both, sequential IDs for G-XXX and AQ-XXX
- [ ] `TestImpactQuery` — by DI-XXX, by PR-XXX, missing CSV, invalid query ID pattern

#### 2. Operations
**File:** `src/agentic_mbse/pm/operations.py`
- [ ] `trace_element()` — see `design.md` for steps and type annotations
- [ ] `approve_research()` — see `design.md` for steps and atomicity order
- [ ] `register_intent()` — see `design.md` for steps and input types
- [ ] `impact_query()` — see `design.md` for steps and known gap

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pm_operations.py -v` → All Phase 1-3 tests pass
- [ ] `uv run pytest tests/` → No regressions

**Manual:**
- [ ] `trace_element` with both knowledge and requirement IDs → verify CSV row has both
- [ ] `approve_research` → verify file physically moved, KNOWLEDGE.md has entries

**What We Know Works After This Phase:**
Cross-file ID validation catches invalid references. Multi-file writes maintain atomicity ordering. Impact query returns correct filtered results. 9 of 14 operations complete.

---

## Phase 4: BACKLOG.md Mutation Operations

### Goal
Implement the 3 operations that modify structured files in-place: `add_item`, `close_item`, `update_validation`. These are the most complex write patterns — `close_item` touches 4+ files and moves a directory.

### Test Stencil (Write This First)
```python
class TestAddItem:
    def test_standalone(self, tmp_path):
        # Create BACKLOG.md from template (empty)
        result = add_item(tmp_path, name="Fix redefines", scale="trivial", priority="P1")
        assert result.ids_assigned["WI"] == "WI-001"
        # parse_backlog → verify standalone entry
        # Verify body re-rendered with item table

    def test_under_epic(self, tmp_path):
        # Create BACKLOG.md with one epic (no items)
        result = add_item(tmp_path, name="Solar model", scale="standard",
                         priority="P0", epic="End-to-End Pipeline")
        # parse_backlog → verify item under epic

    def test_epic_not_found(self, tmp_path):
        result = add_item(tmp_path, ..., epic="Nonexistent")
        assert not result.success


class TestCloseItem:
    def test_happy_path(self, tmp_path):
        # Create work/active/WI-001_solar/ with spec.md, design.md, plan.md
        # Create BACKLOG.md with WI-001 entry
        result = close_item(tmp_path, "WI-001")
        assert result.success
        # Verify: spec.md Status=completed, design.md Status=complete
        # Verify: directory moved to work/completed/YYYYMMDD_WI-001_solar/
        # Verify: BACKLOG.md updated + re-rendered

    def test_not_found(self, tmp_path):
        result = close_item(tmp_path, "WI-999")
        assert not result.success

    def test_not_in_backlog(self, tmp_path):
        # Directory exists but not in BACKLOG.md
        result = close_item(tmp_path, "WI-001")
        assert not result.success
        assert "BACKLOG.md" in result.message

    def test_spec_only(self, tmp_path):
        # No design.md or plan.md — should still succeed


class TestUpdateValidation:
    def test_happy_path(self, tmp_path):
        # Create VALIDATION_MATRIX.md with SV-001 status=pending
        result = update_validation(tmp_path, sv_id="SV-001", status="passing")
        assert result.success
        # parse_validation_matrix → verify SV-001 status=passing

    def test_not_found(self, tmp_path):
        result = update_validation(tmp_path, sv_id="SV-999", status="passing")
        assert not result.success
```

### Changes Required

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_pm_operations.py`
- [ ] `TestAddItem` — standalone, under epic, epic not found, sequential IDs, empty backlog
- [ ] `TestCloseItem` — happy path, not found, not in backlog, not in active, spec-only (no design/plan), BACKLOG.md re-render correct
- [ ] `TestUpdateValidation` — happy path, SV not found, invalid status enum, preserves other rows

#### 2. Operations
**File:** `src/agentic_mbse/pm/operations.py`
- [ ] `add_item()` — see `design.md` for steps
- [ ] `close_item()` — see `design.md` for steps and write ordering
- [ ] `update_validation()` — see `design.md` for in-place rewrite strategy

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pm_operations.py -v` → All Phase 1-4 tests pass
- [ ] `uv run pytest tests/` → No regressions

**Manual:**
- [ ] `close_item` end-to-end: verify directory moved, all frontmatter updated, BACKLOG.md body correct
- [ ] `add_item` then `close_item` on same item → full lifecycle test

**What We Know Works After This Phase:**
All 12 real operations work. BACKLOG.md mutations round-trip correctly. `close_item` archive flow handles the full multi-file workflow. In-place table update preserves file structure.

---

## Phase 5: Stubs, Exports, Final Validation

### Goal
Add the two stubs (`get_status`, `supersede_insight`), update `__init__.py` exports, run full test suite. Mechanical cleanup phase.

### Test Stencil (Write This First)
```python
class TestGetStatus:
    def test_delegates_to_dashboard(self, tmp_path):
        # Create minimal project structure
        result = get_status(tmp_path)
        assert isinstance(result, DashboardResult)
        assert "## Project:" in result.markdown


class TestSupersedeInsight:
    def test_raises_not_implemented(self, tmp_path):
        with pytest.raises(NotImplementedError, match="supersede-insight"):
            supersede_insight(tmp_path, old_id="DI-001",
                            new_insight={}, reason="test")
```

### Changes Required

#### 1. Tests
**File:** `tests/test_pm_operations.py`
- [ ] `TestGetStatus` — returns DashboardResult with markdown
- [ ] `TestSupersedeInsight` — raises NotImplementedError

#### 2. Operations
**File:** `src/agentic_mbse/pm/operations.py`
- [ ] `get_status()` — delegates to `generate_dashboard()`
- [ ] `supersede_insight()` — NotImplementedError stub with TODO

#### 3. Exports
**File:** `src/agentic_mbse/pm/__init__.py`
- [ ] Import all operations from `operations.py`
- [ ] Import `OperationResult`, `ImpactResult`, `InsightInput`, `GoalInput`, `QuestionInput` from `types.py`
- [ ] Add all to `__all__`

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pm_operations.py -v` → All tests pass
- [ ] `uv run pytest tests/` → Full suite green, no regressions
- [ ] `uv run ruff check src/ tests/` → Clean
- [ ] `uv run mypy src/agentic_mbse/pm/operations.py` → No errors

**Manual:**
- [ ] `python -c "from agentic_mbse.pm import close_item, add_insight, OperationResult"` → imports work
- [ ] Verify all 14 operation names + 5 types appear in `__all__`

**What We Know Works After This Phase:**
All 14 operations implemented (12 real + 2 stubs). All importable from `agentic_mbse.pm`. Full test suite green. Ready for D4.5 CLI wiring.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
```bash
uv run pytest tests/                          # Full suite
uv run pytest tests/test_pm_operations.py -v  # Operations tests only
uv run ruff check src/ tests/                 # Lint
uv run ruff format src/ tests/                # Format
uv run mypy src/                              # Type check
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: BACKLOG.md YAML round-trip is tested before any operation uses it. If `yaml.dump` produces unexpected formatting, we catch it here.
- **Phase 4**: `close_item` write ordering (frontmatter → move → BACKLOG.md) is tested with assertions on intermediate state. Recovery path documented in test comments.

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `OperationResult`, `ImpactResult`, `InsightInput`, `GoalInput`, `QuestionInput` to `types.py`
- Created `operations.py` with 10 private helpers: `_next_id`, `_update_frontmatter_fields`, `_render_backlog_body`, `_write_backlog`, `_format_insight_entry`, `_format_decision_entry`, `_format_table_row`, `_append_section`, `_append_table_row`, `_append_csv_row`
- Created `tests/test_pm_operations.py` with 22 Phase 1 tests
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added 5 operations: `add_insight`, `save_research`, `promote_requirement`, `register_decision`, `add_validation`
- Added 18 Phase 2 tests (40 total)
**Issues:** None
**Deviations:** None

### Phase 3 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added 4 operations: `trace_element`, `approve_research`, `register_intent`, `impact_query`
- Added 13 Phase 3 tests (53 total)
**Issues:** None
**Deviations:** None

### Phase 4 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added 3 operations: `add_item`, `close_item`, `update_validation`
- Added 12 Phase 4 tests (65 total)
**Issues:** None
**Deviations:** None

### Phase 5 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `get_status` (delegates to `generate_dashboard`)
- Added `supersede_insight` stub (raises `NotImplementedError`)
- Updated `__init__.py` with all 14 operations, 5 new types, exports in `__all__`
- Added 3 Phase 5 tests (68 total)
- Fixed lint issues: removed unused `io` import, `EpicStatus` import, quoted annotation
**Issues:** None
**Deviations:** None

---

**Status**: Complete

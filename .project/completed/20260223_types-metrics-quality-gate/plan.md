# Implementation Plan: Types, Metrics & Quality Gate

**Status:** Complete
**Created:** 2026-02-23
**Last Updated:** 2026-02-23

## Source Documents
- **Spec:** `.project/active/types-metrics-quality-gate/spec.md`
- **Design:** `.project/active/types-metrics-quality-gate/design.md` ← See here for component details, function signatures, type definitions, routing logic pseudocode
- **Parent Design:** `.project/concepts/doc-extraction/design.md` (§3, §4.5, §4.7, §6, §13)

## Implementation Strategy

**Phasing Rationale:**
Build bottom-up along the dependency graph: `metrics.py` → `types.py` → `quality_gate.py` → `pipeline.py` stub. Phase 1 de-risks the shim conversion (riskiest change — could break experiment scripts). Phase 2 builds the bulk of new logic. Phase 3 is integration validation.

**Overall Validation Approach:**
- Each phase starts with tests (write test file before or alongside implementation)
- Each phase runs `uv run pytest` on new + existing tests
- Phase 3 runs full suite + lint as final gate

---

## Phase 1: Metrics, Types & Shim

### Goal
Build the two leaf modules and convert the test shim. This validates that the code promotion from `tests/corpus/metrics.py` works correctly and that the shim preserves backward compatibility for experiment scripts.

### Test Stencil (Write This First)

```python
# tests/test_extraction_metrics.py
import pytest
from pathlib import Path
from agentic_mbse.extraction.metrics import (
    ExtractionMetrics, compute_metrics, load_ground_truth,
    score_against_ground_truth, AccuracyScore, GroundTruth,
)

class TestComputeMetrics:
    def test_heading_count(self):
        md = "# H1\n## H2\n### H3\nNot a heading"
        m = compute_metrics(md)
        assert m.heading_count == 3
        assert m.heading_by_level == {1: 1, 2: 1, 3: 1}

    def test_table_rows(self):
        md = "| a | b |\n|---|---|\n| 1 | 2 |"
        m = compute_metrics(md)
        assert m.table_row_count == 3

    def test_math_symbols(self):
        md = "The integral ∫ and sum ∑ of α + β"
        m = compute_metrics(md)
        assert m.math_symbol_count >= 4

    def test_empty_string(self):
        m = compute_metrics("")
        assert m.char_count == 0
        assert m.heading_count == 0

class TestScoreAgainstGroundTruth:
    def test_exact_match(self):
        m = ExtractionMetrics(char_count=100, heading_count=10, heading_by_level={1: 10},
                              table_row_count=0, math_symbol_count=0, figure_ref_count=0,
                              extraction_time_seconds=0.0)
        gt = GroundTruth(slug="test", pages=1, headings=10, heading_levels=None,
                         data_tables=None, table_data_rows=None,
                         expected_metric_table_rows=None, display_equations=None,
                         has_inline_math=None, notes="")
        scores = score_against_ground_truth(m, gt)
        assert scores["headings"].category == "exact"
```

### Changes Required

**See `design.md` for:**
- `ExtractionMetrics` fields → `design.md#component-1`
- `load_ground_truth` signature deviation → `design.md#spec-deviations-summary`
- Type definitions → `design.md#component-2`
- Shim structure → `design.md#component-5`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_extraction_metrics.py` (NEW — write first)
- [x] Create file with test stencil above
- [x] `TestComputeMetrics`: `test_heading_count`, `test_heading_by_level`, `test_table_rows`, `test_math_symbols`, `test_figure_refs`, `test_empty_string`, `test_extraction_time_passthrough`
- [x] `TestScoreAgainstGroundTruth`: `test_exact_match`, `test_over_detection`, `test_under_detection`, `test_miss`, `test_close_within_10pct`, `test_none_when_gt_unavailable`
- [x] `TestLoadGroundTruth`: `test_loads_corpus_file` (skips if JSONL absent)

#### 2. Metrics Module
**File:** `src/agentic_mbse/extraction/metrics.py` (NEW)
- [x] Copy `ExtractionMetrics`, `compute_metrics`, `GroundTruth`, `AccuracyScore`, `score_against_ground_truth` from `tests/corpus/metrics.py`
- [x] Change `load_ground_truth(path)` to required parameter (no default) per `design.md#load_ground_truth-default-path`
- [x] Do NOT copy `compare_metrics()` or `__main__` block

#### 3. Types Module
**File:** `src/agentic_mbse/extraction/types.py` (NEW)
- [x] Copy verbatim from `design.md#component-2` (PageAction enum, PageResult, DetectedTable, PageAssessment, PageDecision, CostRecord, PipelineResult)

#### 4. Shim Conversion
**File:** `tests/corpus/metrics.py` (MODIFY)
- [x] Replace implementation body with re-exports per `design.md#component-5`
- [x] Keep `compare_metrics()` body verbatim with NOTE comment
- [x] Keep `__main__` block verbatim
- [x] Add `load_ground_truth` wrapper with `_DEFAULT_GT_PATH`

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extraction_metrics.py -v` → All pass
- [x] `uv run pytest tests/` → No regressions (shim preserves backward compat)

**Manual:**
- [x] Verify imports work: `uv run python -c "from agentic_mbse.extraction.types import PageAction, PipelineResult; print('OK')"`
- [x] Verify shim re-exports: `uv run python -c "from tests.corpus.metrics import compute_metrics, load_ground_truth; print('OK')"` (or equivalent)

**What We Know Works After This Phase:**
- All 8 pipeline types importable from `types.py`
- `compute_metrics()` produces identical output to experiment code
- `score_against_ground_truth()` categorizes correctly
- Shim preserves experiment script compatibility

---

## Phase 2: Quality Gate, Budget & Routing

### Goal
Build the quality gate (assessment + routing), budget allocation, and their tests. This is the bulk of new logic — especially `route_page()` which is genuinely new code (not promoted from experiments).

### Test Stencil (Write This First)

```python
# tests/test_quality_gate.py
from agentic_mbse.extraction.quality_gate import (
    QualityGateConfig, assess_page, assess_heading_anomaly,
    route_page, prioritize_pages, count_headings,
)
from agentic_mbse.extraction.pipeline import EnhancerBudget, allocate_budget
from agentic_mbse.extraction.types import DetectedTable, PageAction, PageAssessment
from agentic_mbse.extraction.metrics import compute_metrics

class TestMathGarbling:
    def test_strikethrough_high(self):
        md = "Some ~~garbled~~ text ~~more~~ and ~~again~~ content"
        a = assess_page(md, 0)
        assert a.needs_claude
        assert a.math_garble_score >= 2.0

    def test_clean_page(self):
        md = "## Introduction\n\nThis is normal text with no issues."
        a = assess_page(md, 0)
        assert not a.needs_claude
        assert not a.needs_gmft

class TestRouting:
    def test_keep(self):
        a = PageAssessment(page_num=0)
        d = route_page(a, None, "text", within_claude_budget=True)
        assert d.action == PageAction.KEEP

    def test_claude_replace(self):
        a = PageAssessment(page_num=0, needs_claude=True, severity=2.0)
        d = route_page(a, None, "text", within_claude_budget=True)
        assert d.action == PageAction.CLAUDE_REPLACE

class TestCountHeadings:
    def test_agrees_with_compute_metrics(self):
        md = "# H1\n## H2\nNot a heading\n### H3\n##NoSpace"
        assert count_headings(md) == compute_metrics(md).heading_count

class TestBudgetAllocation:
    def test_selects_highest_severity(self):
        assessments = [
            PageAssessment(page_num=0, needs_claude=True, severity=1.0),
            PageAssessment(page_num=1, needs_claude=True, severity=3.0),
            PageAssessment(page_num=2, needs_claude=True, severity=2.0),
        ]
        budget = EnhancerBudget(total_usd=0.16, cost_per_page_usd=0.078)  # budget for 2
        selected = allocate_budget(assessments, budget)
        assert selected == {1, 2}  # top 2 by severity
```

### Changes Required

**See `design.md` for:**
- Quality gate structure and all helper functions → `design.md#component-3`
- `route_page()` pseudocode → `design.md#routing-logic-in-route_page`
- `_has_col_headers`, `_has_br_in_tables`, `_has_pipe_tables` → `design.md#component-3`
- Budget allocation → `design.md#component-4`
- Full test catalog → `design.md#component-7`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_quality_gate.py` (NEW — write first)
- [x] Create file with test stencil above
- [x] `TestMathGarbling`: 5 tests — `test_strikethrough_high`, `test_strikethrough_low`, `test_replacement_chars`, `test_bracket_operators`, `test_clean_page`
- [x] `TestTableAnomaly`: 2 tests — `test_br_in_tables`, `test_col_headers`
- [x] `TestTextDensity`: 2 tests — `test_sparse_page`, `test_normal_page`
- [x] `TestHeadingAnomaly`: 4 tests — `test_zero_headings_multipage`, `test_high_density`, `test_normal_density`, `test_single_page_no_anomaly`
- [x] `TestRouting`: 9 tests — 7 from design §13.2 + `test_claude_over_budget_no_gmft_keeps` + `test_needs_gmft_no_tables_no_specific_anomaly`
- [x] `TestCountHeadings`: 3 tests — `test_atx_headings`, `test_not_heading_without_space`, `test_agrees_with_compute_metrics`
- [x] `TestBudgetAllocation`: 4 tests — `test_selects_highest_severity`, `test_zero_budget`, `test_no_eligible`, `test_custom_needs_field`
- [x] `TestPrioritizePages`: 2 tests — `test_returns_page_order`, `test_respects_budget`

#### 2. Quality Gate Module
**File:** `src/agentic_mbse/extraction/quality_gate.py` (NEW)
- [x] `QualityGateConfig` dataclass with Stage 3 defaults
- [x] Private helpers promoted from `tests/corpus/pipelines/quality_gate.py`: `_count_strikethroughs`, `_count_replacement_chars`, `_count_garbled_fractions`, `_assess_math_garbling`, `_assess_table_anomaly`, `_assess_text_density`
- [x] Private helpers from `tests/corpus/pipelines/shared.py`: `_has_col_headers`, `_has_br_in_tables`, `_has_pipe_tables`
- [x] `count_headings()` — public, naive line check (see design note on code blocks)
- [x] `assess_page()` — renamed from experiment's `assess_page_quality()`, add `config` param
- [x] `assess_heading_anomaly()` — add `config` param for `heading_density_max`
- [x] `route_page()` — NEW, implement from `design.md#routing-logic-in-route_page` pseudocode
- [x] `prioritize_pages()` — from experiment, add cross-reference docstring to `allocate_budget()`

#### 3. Pipeline Stub
**File:** `src/agentic_mbse/extraction/pipeline.py` (NEW)
- [x] `EnhancerBudget` dataclass with `max_pages` property
- [x] `allocate_budget()` function
- [x] Verbatim from `design.md#component-4`

### Validation

**Automated:**
- [x] `uv run pytest tests/test_quality_gate.py -v` → All 31 tests pass
- [x] `uv run pytest tests/test_extraction_metrics.py tests/test_quality_gate.py -v` → All pass together
- [x] `uv run pytest tests/` → No regressions

**What We Know Works After This Phase:**
- `assess_page()` detects all 3 quality dimensions at correct severity levels
- `route_page()` covers all 6 `PageAction` paths + 2 edge cases
- `count_headings()` agrees with `compute_metrics().heading_count`
- `allocate_budget()` selects highest-severity pages within dollar cap
- `prioritize_pages()` returns page-ordered results within page budget

---

## Phase 3: Full Validation & Lint

### Goal
Final integration check — verify the full test suite passes, all new code is lint-clean, and the shim's `__main__` entry point still works.

### Changes Required

No code changes. Validation only.

### Validation

**Automated:**
- [x] `uv run pytest tests/ -v` → Full suite passes, no regressions
- [x] `uv run ruff check src/agentic_mbse/extraction/metrics.py src/agentic_mbse/extraction/types.py src/agentic_mbse/extraction/quality_gate.py src/agentic_mbse/extraction/pipeline.py` → Clean
- [x] `uv run ruff format --check src/agentic_mbse/extraction/metrics.py src/agentic_mbse/extraction/types.py src/agentic_mbse/extraction/quality_gate.py src/agentic_mbse/extraction/pipeline.py` → Clean
- [x] `uv run ruff check tests/test_extraction_metrics.py tests/test_quality_gate.py` → Clean
- [x] `uv run ruff format --check tests/test_extraction_metrics.py tests/test_quality_gate.py` → Clean

**Manual:**
- [x] Verify all types importable: `uv run python -c "from agentic_mbse.extraction.types import PageAction, PageResult, DetectedTable, PageAssessment, PageDecision, CostRecord, PipelineResult; print('All types OK')"`
- [x] Verify quality gate importable: `uv run python -c "from agentic_mbse.extraction.quality_gate import assess_page, route_page, count_headings; print('Quality gate OK')"`
- [x] Verify pipeline stub importable: `uv run python -c "from agentic_mbse.extraction.pipeline import EnhancerBudget, allocate_budget; print('Pipeline stub OK')"`

**What We Know Works After This Phase:**
- All spec acceptance criteria met
- Zero regressions from shim conversion
- Code is lint-clean and formatted
- Ready for Item 2 (enhancement components) and Item 3 (pipeline orchestration)

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Shim conversion risk — run full `pytest tests/` immediately after conversion to catch any import breakage before proceeding
- **Phase 2**: `route_page()` is new code (not promoted) — the 9-test routing suite covers all 6 actions plus 2 edge cases identified during design audit

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `src/agentic_mbse/extraction/metrics.py` — verbatim promotion from `tests/corpus/metrics.py` with `load_ground_truth(path)` as required parameter
- Created `src/agentic_mbse/extraction/types.py` — verbatim from design §3 (PageAction, PageResult, DetectedTable, PageAssessment, PageDecision, CostRecord, PipelineResult)
- Modified `tests/corpus/metrics.py` — converted to shim with re-exports; kept `compare_metrics()` and `__main__` verbatim
- Created `tests/test_extraction_metrics.py` — 15 tests (7 compute_metrics, 1 serialization, 6 scoring, 1 load_ground_truth)
**Issues:** None
**Deviations:** None — matched design exactly

### Phase 2 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `src/agentic_mbse/extraction/quality_gate.py` — QualityGateConfig, assess_page, assess_heading_anomaly, route_page, prioritize_pages, count_headings, plus private helpers
- Created `src/agentic_mbse/extraction/pipeline.py` — EnhancerBudget + allocate_budget stub
- Created `tests/test_quality_gate.py` — 32 tests (5 math garbling, 2 table anomaly, 2 text density, 4 heading anomaly, 10 routing, 3 count_headings, 4 budget allocation, 2 prioritize_pages)
**Issues:** Two test data issues — synthetic markdown strings were too short, triggering text density checks unexpectedly. Fixed by padding test strings above 200-char threshold.
**Deviations:** Added `test_gmft_found_missed_tables` routing test (design's FR-Q7 GMFT_APPEND case) beyond the 9 originally planned.

### Phase 3 Completion
**Completed:** 2026-02-23
**Actual Changes:** No code changes. Validation only.
- All 47 new tests pass
- ruff check: clean (all 7 files)
- ruff format: clean (all 7 files)
- All modules importable
- Full test suite: 843 passed, 34 failed (all pre-existing syside license key failures), 0 new regressions
**Issues:** None
**Deviations:** None

---

**Status**: Complete

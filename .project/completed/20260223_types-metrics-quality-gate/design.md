# Design: Types, Metrics & Quality Gate

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-23 16:26 PST
**Branch:** `doc-ingest-clean`
**Commit:** ca91e60

## Overview

Build three production modules (`types.py`, `metrics.py`, `quality_gate.py`) and a stub `pipeline.py` that form the foundation layer for the v4 PDF extraction pipeline. The code is a direct promotion of proven Stage 3 experiment code into `src/agentic_mbse/extraction/`, with the addition of the routing decision table and budget allocation mechanism from the parent design.

## Related Artifacts

- **Spec:** `.project/active/types-metrics-quality-gate/spec.md`
- **Parent Design:** `.project/concepts/doc-extraction/design.md` (§3, §4.5, §4.7, §6, §13)
- **Parent Requirements:** `.project/concepts/doc-extraction/requirements.md` (FR-5 through FR-7, FR-11)
- **Epic:** `.project/backlog/epic_pdf-extraction-v4.md` (Item 1)
- **Source — quality gate:** `tests/corpus/pipelines/quality_gate.py`
- **Source — metrics:** `tests/corpus/metrics.py`
- **Source — shared types:** `tests/corpus/pipelines/shared.py`

## Research Findings

### Existing Code to Promote

The Stage 3 experiment code is the primary source. Here's a mapping from experiment → production:

| Experiment Source | Production Target | What Changes |
|---|---|---|
| `tests/corpus/pipelines/quality_gate.py:24-38` (`PageAssessment`) | `types.py` | Identical — copy verbatim |
| `tests/corpus/pipelines/shared.py:38-43` (`PageResult`) | `types.py` | Identical |
| `tests/corpus/pipelines/shared.py:57-64` (`PageDecision`) | `types.py` | `action` changes from `str` → `PageAction` enum; `details` gets type annotation |
| `tests/corpus/metrics.py:15-34` (`ExtractionMetrics`) | `metrics.py` | Identical |
| `tests/corpus/metrics.py:36-108` (`compute_metrics`) | `metrics.py` | Identical |
| `tests/corpus/metrics.py:168-201` (`GroundTruth`) | `metrics.py` | Identical |
| `tests/corpus/metrics.py:228-304` (`AccuracyScore`, scoring) | `metrics.py` | Identical |
| `tests/corpus/pipelines/quality_gate.py:276-318` (`assess_page_quality`) | `quality_gate.py` as `assess_page()` | Rename function; add `config` parameter; logic identical |
| `tests/corpus/pipelines/quality_gate.py:210-243` (`assess_heading_anomaly`) | `quality_gate.py` | Add `config` parameter for `heading_density_max` |
| `tests/corpus/pipelines/quality_gate.py:326-349` (`prioritize_pages`) | `quality_gate.py` | Keep as-is (simpler interface for direct use); `allocate_budget()` in `pipeline.py` is the generic version |

### New Code (Not in Experiments)

These are specified in the parent design but have no experiment implementation to promote:

| Component | Source | Notes |
|---|---|---|
| `PageAction` enum | Design §3 | 6 values; new |
| `DetectedTable` dataclass | Design §3 | Extends experiment's `GmftTable` with `image_path`, `extraction_failed`, `detector`, `source` |
| `CostRecord` dataclass | Design §3 | New; tracks Claude invocation costs |
| `PipelineResult` dataclass | Design §3 | New; wraps everything together |
| `QualityGateConfig` dataclass | Design §4.5 | New; extracts thresholds from hardcoded constants |
| `route_page()` | Design §4.5 | New; the H5 experiment inlined this logic in the pipeline script |
| `count_headings()` | Design §4.5 | Public helper; used by orchestrator for document-level heading count |
| `EnhancerBudget` + `allocate_budget()` | Design §6 | New; generic budget mechanism |

### Patterns and Conventions

**Import style** (`extraction/__init__.py:1-17`): The extraction package uses explicit `from module import ...` in `__init__.py`. Follow this pattern for new exports.

**Dataclass style**: All existing extraction types use `@dataclass` with `from __future__ import annotations` for forward references. The experiment code uses the same pattern. Follow it.

**Test style** (`tests/test_quality_gates.py`): Tests use pytest classes grouped by component (`TestDetectBrokenTables`, `TestDetectGarbledEquations`, etc.). Each test method is a single assertion scenario. No fixtures for synthetic markdown — inline strings. Follow this pattern.

### `load_ground_truth()` Default Path

The current `tests/corpus/metrics.py:214-216` resolves the default path via `Path(__file__).parent / "ground_truth.jsonl"`. This works because the file lives next to the JSONL. After promotion to `src/agentic_mbse/extraction/metrics.py`, `__file__` will be in a completely different location.

**Resolution:** Change the default to `None` and require callers to pass the path explicitly. The test shim in `tests/corpus/metrics.py` will pass `Path(__file__).parent / "ground_truth.jsonl"` to maintain existing behavior. The `__main__` block in the shim is the only consumer that uses the default. Production code (pipeline, CLI) will always pass an explicit path.

**Spec deviation (FR-M5):** This changes the signature from spec FR-M5 (`load_ground_truth(path=None)` with implicit default) to `load_ground_truth(path: Path)` (required). The spec was written before the relocation issue was identified. The shim preserves the original caller experience.

### Spec Deviations Summary

All deviations from the spec, collected here for traceability:

| Spec Item | Spec Says | Design Says | Rationale |
|---|---|---|---|
| FR-M5 | `load_ground_truth(path=None)` with implicit default | `load_ground_truth(path: Path)` (required) | `__file__`-relative default breaks after relocation; shim preserves caller experience |
| FR-Q6 | `_count_headings()` (private) | `count_headings()` (public) | Item 3 orchestrator needs to call this directly; testing private functions is a code smell |
| Spec test plan | `test_hash_in_code_block` ("# in code blocks not counted") | Removed | `count_headings()` intentionally uses naive line check matching `compute_metrics()` behavior; pymupdf4llm doesn't produce fenced code blocks |

### Routing Logic Gap

The H5 experiment script (`tests/corpus/pipelines/h5_quality_gated.py:67-`) inlines the routing decision. It does NOT have the `STRIP_FALSE` or `STRIP_BROKEN` actions — those are new in the design. The H1 experiment (`h1_pymupdf_gmft.py`) handles table stripping as part of `decide_page()` but uses a different interface.

The routing logic in `route_page()` needs to differentiate `STRIP_FALSE` (ColN headers) from `STRIP_BROKEN` (`<br>` artifacts). Since `PageAssessment.table_anomaly` is a single bool, the function must inspect the page markdown directly. The table anomaly helpers `has_col_headers()` and `has_br_in_tables()` from `tests/corpus/pipelines/shared.py:362-379` provide the detection logic.

**Resolution:** `route_page()` calls `_has_col_headers()` and `_has_br_in_tables()` from the page markdown to decide which strip action to apply. These two helpers are tiny (4-5 lines each) and will be inlined in `quality_gate.py` as private functions rather than importing from `tables.py` (which doesn't exist yet in Item 1).

**Duplication migration (Major):** When `tables.py` is built in Item 2, it will have public `has_col_headers()` and `has_br_in_tables()` functions. At that point, Item 2 SHOULD refactor `quality_gate.py` to import from `tables.py` and delete the private copies. This is explicitly called out here to prevent permanent duplication. The Item 2 spec/plan should include a task: "Refactor `quality_gate.py` to import `has_col_headers` and `has_br_in_tables` from `tables.py`".

---

## Proposed Design

### Module Dependency Graph

```
metrics.py          (standalone — no extraction imports)
    ↑
types.py            (imports ExtractionMetrics from metrics.py)
    ↑
quality_gate.py     (imports PageAssessment, PageAction, PageDecision, DetectedTable from types.py)
    ↑
pipeline.py (stub)  (imports PageAssessment from types.py)
```

No circular dependencies. `metrics.py` is the leaf.

### Component 1: `src/agentic_mbse/extraction/metrics.py` (~170 lines)

**Purpose:** Canonical extraction quality metrics — single source of truth for both production and experiment code.

**Source:** Direct copy of `tests/corpus/metrics.py` with one change to `load_ground_truth()`.

**Contents:**
- `ExtractionMetrics` — verbatim from `tests/corpus/metrics.py:15-34`. Fields: `char_count: int`, `heading_count: int`, `heading_by_level: dict[int, int]`, `table_row_count: int`, `math_symbol_count: int`, `figure_ref_count: int`, `extraction_time_seconds: float`. Methods: `to_dict()`, `from_dict()`.
- `compute_metrics(markdown, elapsed=0.0)` — verbatim from `tests/corpus/metrics.py:36-108`
- `GroundTruth` — verbatim from `tests/corpus/metrics.py:168-201`
- `AccuracyScore` — verbatim from `tests/corpus/metrics.py:228-236`
- `load_ground_truth(path)` — **`path` is required, no default**. Remove `if path is None` fallback. Callers must pass the path.
- `score_against_ground_truth(metrics, gt)` — verbatim from `tests/corpus/metrics.py:239-304`

**NOT promoted:** `compare_metrics()` (stays in test shim).

**Key decision: no `__main__` block** in the production module. The CLI entry point for ad-hoc metric computation stays in the test shim.

### Component 2: `src/agentic_mbse/extraction/types.py` (~130 lines)

**Purpose:** All pipeline data types.

**Source:** Combination of experiment types + design §3 new types.

**Contents** (in definition order):

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from agentic_mbse.extraction.metrics import ExtractionMetrics


class PageAction(str, Enum):
    KEEP = "keep"
    GMFT_REPLACE = "gmft_replace"
    GMFT_APPEND = "gmft_append"
    STRIP_FALSE = "strip_false"
    STRIP_BROKEN = "strip_broken"
    CLAUDE_REPLACE = "claude_replace"


@dataclass
class PageResult:
    page_num: int   # 0-indexed
    markdown: str


@dataclass
class DetectedTable:
    markdown: str
    confidence: float
    num_rows: int
    num_cols: int
    avg_cell_length: float
    image_path: Path | None = None
    extraction_failed: bool = False
    detector: str = "gmft"
    source: str = "gmft"


@dataclass
class PageAssessment:
    page_num: int
    needs_claude: bool = False
    needs_gmft: bool = False
    reasons: list[str] = field(default_factory=list)
    severity: float = 0.0
    math_garble_score: float = 0.0
    table_anomaly: bool = False
    heading_anomaly: bool = False
    low_text_density: bool = False


@dataclass
class PageDecision:
    page_num: int
    action: PageAction
    reasons: list[str] = field(default_factory=list)
    details: dict[str, float | bool | str | list[str]] = field(default_factory=dict)


@dataclass
class CostRecord:
    page_num: int
    cost_usd: float
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    elapsed_seconds: float = 0.0
    table_index: int | None = None


@dataclass
class PipelineResult:
    markdown: str
    metrics: ExtractionMetrics
    decisions: list[PageDecision] = field(default_factory=list)
    cost: list[CostRecord] = field(default_factory=list)
    total_cost_usd: float = 0.0
    source: str = ""
    elapsed_seconds: float = 0.0
    error: str | None = None
```

This is verbatim from the parent design §3. No deviations.

### Component 3: `src/agentic_mbse/extraction/quality_gate.py` (~250 lines)

**Purpose:** Per-page quality assessment, document-level heading check, routing decisions.

**Source:** `tests/corpus/pipelines/quality_gate.py` (assessment logic) + new routing logic from design §4.5.

**Structure:**

```python
from __future__ import annotations
import re
from dataclasses import dataclass
from agentic_mbse.extraction.types import (
    DetectedTable, PageAction, PageAssessment, PageDecision,
)

# --- Config ---

@dataclass
class QualityGateConfig:
    math_severity_threshold: float = 1.0
    text_density_min_chars: int = 200
    heading_density_max: float = 3.0
    heading_anomaly_boost: float = 0.5

# --- Internal detection helpers (from experiment quality_gate.py) ---

_STRIKETHROUGH_RE = ...      # from quality_gate.py:45
_REPLACEMENT_CHAR = ...      # from quality_gate.py:48
_GARBLED_FRACTION_RE = ...   # from quality_gate.py:54
_UNICODE_MATH_RANGES = ...   # from quality_gate.py:58-62
_COL_HEADER_RE = ...         # from shared.py:333
_TABLE_ROW_RE = ...          # (inline: line.strip().startswith("|") and count >= 2)

def _count_strikethroughs(text: str) -> int: ...       # from quality_gate.py:65-67
def _count_replacement_chars(text: str) -> int: ...    # from quality_gate.py:70-72
def _count_garbled_fractions(text: str) -> int: ...    # from quality_gate.py:75-87
def _assess_math_garbling(md: str) -> tuple[float, list[str]]: ...  # from quality_gate.py:106-157
def _assess_table_anomaly(md: str) -> tuple[bool, list[str]]: ...   # from quality_gate.py:169-202
def _assess_text_density(md: str) -> tuple[bool, list[str]]: ...    # from quality_gate.py:254-268
def _has_col_headers(md: str) -> bool: ...             # from shared.py:370-379
def _has_br_in_tables(md: str) -> bool: ...            # from shared.py:362-368
def _has_pipe_tables(md: str) -> bool: ...             # True if any line starts with | and has >= 2 pipes

# --- Public API ---

def count_headings(markdown: str) -> int:
    """Count ATX headings (lines starting with # followed by space).

    Naive line-by-line check — does NOT track fenced code blocks.
    This matches the experiment code behavior and the metrics.py heading
    counter. Code blocks with # comments are rare in extraction output
    (pymupdf4llm doesn't produce fenced code blocks for PDF content).
    """

def assess_page(
    page_markdown: str,
    page_num: int,
    config: QualityGateConfig | None = None,
) -> PageAssessment:
    """Assess a single page. Calls _assess_math_garbling, _assess_table_anomaly, _assess_text_density."""

def assess_heading_anomaly(
    total_headings: int,
    total_pages: int,
    config: QualityGateConfig | None = None,
) -> tuple[bool, list[str]]:
    """Document-level heading check."""

def route_page(
    assessment: PageAssessment,
    gmft_tables: list[DetectedTable] | None,
    page_markdown: str,
    within_claude_budget: bool,
) -> PageDecision:
    """Route a page to the appropriate action."""

def prioritize_pages(
    assessments: list[PageAssessment],
    budget_pages: int,
) -> list[int]:
    """Select highest-severity pages within a page budget. Returns page numbers in page order.

    For dollar-based selection, see allocate_budget() in pipeline.py.
    """
```

**Routing logic in `route_page()`** (the key new code):

```python
def route_page(assessment, gmft_tables, page_markdown, within_claude_budget):
    reasons = list(assessment.reasons)  # Copy
    has_tables = gmft_tables is not None and len(gmft_tables) > 0

    # 1. Claude if needed and affordable
    if assessment.needs_claude and within_claude_budget:
        return PageDecision(assessment.page_num, PageAction.CLAUDE_REPLACE, reasons)

    # 2. Claude over budget — fall back to GMFT if table issues
    if assessment.needs_claude and not within_claude_budget and assessment.needs_gmft and has_tables:
        reasons.append("Claude over budget — GMFT fallback for table issues")
        return PageDecision(assessment.page_num, PageAction.GMFT_REPLACE, reasons)

    # 3. Table issues with GMFT available
    if assessment.needs_gmft and has_tables:
        # Check if pymupdf found any tables — if not, append rather than replace
        has_existing_tables = _has_pipe_tables(page_markdown)
        if has_existing_tables:
            return PageDecision(assessment.page_num, PageAction.GMFT_REPLACE, reasons)
        else:
            return PageDecision(assessment.page_num, PageAction.GMFT_APPEND, reasons)

    # 4. Table issues but no GMFT — strip problematic tables or keep
    if assessment.needs_gmft and not has_tables:
        if _has_col_headers(page_markdown):
            reasons.append("ColN auto-headers detected, no GMFT — stripping false tables")
            return PageDecision(assessment.page_num, PageAction.STRIP_FALSE, reasons)
        if _has_br_in_tables(page_markdown):
            reasons.append("<br> artifacts in tables, no GMFT — stripping broken tables")
            return PageDecision(assessment.page_num, PageAction.STRIP_BROKEN, reasons)
        # Table anomaly flagged but neither ColN nor <br> matched — keep as-is
        # (assess_table_anomaly may have fired on a pattern not handled by strip actions)
        reasons.append("Table anomaly detected but no specific strip action applicable — keeping")
        return PageDecision(assessment.page_num, PageAction.KEEP, reasons)

    # 5. GMFT tables available but no issues flagged — pymupdf missed tables
    if has_tables and not assessment.needs_gmft and not assessment.needs_claude:
        has_existing_tables = _has_pipe_tables(page_markdown)
        if not has_existing_tables:
            reasons.append("GMFT found tables not in pymupdf4llm output")
            return PageDecision(assessment.page_num, PageAction.GMFT_APPEND, reasons)

    # 6. Default: keep
    return PageDecision(assessment.page_num, PageAction.KEEP, reasons)
```

**Note on `_has_pipe_tables()`:** A small helper that checks if the page markdown contains any pipe table rows. This is needed for the GMFT_REPLACE vs GMFT_APPEND decision. Simple implementation: `any(line.strip().startswith("|") and line.count("|") >= 2 for line in markdown.split("\n"))`.

**Change from experiment:** The experiment's `assess_page_quality()` is renamed to `assess_page()` in production (shorter, matches design §4.5 interface). The `config` parameter replaces hardcoded threshold constants. The default `QualityGateConfig()` produces identical behavior to the experiment.

### Component 4: `src/agentic_mbse/extraction/pipeline.py` (stub, ~60 lines)

**Purpose:** Budget allocation mechanism only. The orchestration logic (`extract_pdf()`, `PipelineConfig`) will be added in Item 3.

**Contents:**

```python
from __future__ import annotations
from dataclasses import dataclass
from agentic_mbse.extraction.types import PageAssessment


@dataclass
class EnhancerBudget:
    total_usd: float
    cost_per_page_usd: float

    @property
    def max_pages(self) -> int:
        if self.cost_per_page_usd <= 0:
            return 0
        return int(self.total_usd / self.cost_per_page_usd)


def allocate_budget(
    assessments: list[PageAssessment],
    budget: EnhancerBudget,
    needs_field: str = "needs_claude",
) -> set[int]:
    eligible = [a for a in assessments if getattr(a, needs_field, False)]
    ranked = sorted(eligible, key=lambda a: a.severity, reverse=True)
    selected = ranked[:budget.max_pages]
    return {a.page_num for a in selected}
```

This is verbatim from design §6.1.

### Component 5: `tests/corpus/metrics.py` (shim conversion)

**Purpose:** Backward compatibility for experiment scripts.

**Approach:** Replace the implementation body with re-exports. Keep `compare_metrics()` and `__main__` in-place.

```python
"""Test corpus metrics computation.

Canonical implementation lives in agentic_mbse.extraction.metrics.
This module re-exports for backward compatibility with experiment scripts.
"""
from pathlib import Path

# Re-export canonical implementation
from agentic_mbse.extraction.metrics import (
    ExtractionMetrics,
    GroundTruth,
    AccuracyScore,
    compute_metrics,
    load_ground_truth as _load_ground_truth,
    score_against_ground_truth,
)

# Convenience wrapper: default path for corpus ground truth
_DEFAULT_GT_PATH = Path(__file__).parent / "ground_truth.jsonl"

def load_ground_truth(path: Path | None = None) -> dict[str, GroundTruth]:
    """Load ground truth with default path to corpus JSONL."""
    return _load_ground_truth(path or _DEFAULT_GT_PATH)


def compare_metrics(baseline: ExtractionMetrics, current: ExtractionMetrics) -> dict:
    """Compare two sets of metrics and compute deltas.

    NOTE: Not promoted to production metrics.py. Kept here for experiment
    scripts. If needed in production later, copy the implementation from
    the git history of this file (pre-shim conversion).
    """
    # ... (preserve existing implementation verbatim)


if __name__ == "__main__":
    # ... (preserve existing __main__ block verbatim)
```

### Component 6: `__init__.py` Update

**Deferred to Item 3.** No changes in this item — `pipeline.py` is a stub and `extract_pdf`/`PipelineConfig` don't exist yet. The new modules are importable directly (`from agentic_mbse.extraction.types import ...`).

### Component 7: Tests

#### `tests/test_extraction_metrics.py`

Tests for `metrics.py`. All use inline markdown strings.

```python
from pathlib import Path
from agentic_mbse.extraction.metrics import (
    ExtractionMetrics, AccuracyScore, GroundTruth,
    compute_metrics, load_ground_truth, score_against_ground_truth,
)

class TestComputeMetrics:
    def test_heading_count(self): ...
    def test_heading_by_level(self): ...
    def test_table_rows(self): ...
    def test_math_symbols(self): ...
    def test_figure_refs(self): ...
    def test_empty_string(self): ...
    def test_extraction_time_passthrough(self): ...

class TestScoreAgainstGroundTruth:
    def test_exact_match(self): ...
    def test_over_detection(self): ...
    def test_under_detection(self): ...
    def test_miss(self): ...
    def test_close_within_10pct(self): ...
    def test_none_when_gt_unavailable(self): ...

class TestLoadGroundTruth:
    def test_loads_corpus_file(self):
        """Loads from actual corpus JSONL to verify format compatibility."""
        gt_path = Path(__file__).parent / "corpus" / "ground_truth.jsonl"
        if not gt_path.exists():
            pytest.skip("ground_truth.jsonl not available")
        gt = load_ground_truth(gt_path)
        assert "hawker_2020" in gt
        assert isinstance(gt["hawker_2020"].heading_levels, dict)
        # heading_levels keys should be int, not str
        assert all(isinstance(k, int) for k in gt["hawker_2020"].heading_levels)
```

#### `tests/test_quality_gate.py`

Tests for `quality_gate.py` and budget allocation from `pipeline.py`. All use synthetic markdown.

```python
from agentic_mbse.extraction.quality_gate import (
    QualityGateConfig, assess_page, assess_heading_anomaly,
    route_page, prioritize_pages, count_headings,
)
from agentic_mbse.extraction.pipeline import EnhancerBudget, allocate_budget
from agentic_mbse.extraction.types import (
    DetectedTable, PageAction, PageAssessment, PageDecision,
)

class TestMathGarbling:
    # 5 tests from design §13.1
    ...

class TestTableAnomaly:
    # 2 tests from design §13.1
    ...

class TestTextDensity:
    # 2 tests from design §13.1
    ...

class TestHeadingAnomaly:
    def test_zero_headings_multipage(self): ...
    def test_high_density(self): ...
    def test_normal_density(self): ...
    def test_single_page_no_anomaly(self): ...

class TestRouting:
    # 7 tests from design §13.2, plus edge cases:
    # test_claude_over_budget_no_gmft_keeps — needs_claude, over budget, no table issues → KEEP
    # test_needs_gmft_no_tables_no_specific_anomaly — table anomaly but neither ColN nor <br> → KEEP with reason
    ...

class TestCountHeadings:
    def test_atx_headings(self): ...
    def test_not_heading_without_space(self): ...  # "##NoSpace" shouldn't count
    def test_agrees_with_compute_metrics(self):
        """count_headings() and compute_metrics().heading_count MUST agree."""
        md = "# H1\n## H2\nNot a heading\n### H3\n##NoSpace"
        assert count_headings(md) == compute_metrics(md).heading_count
    # No code-block tracking test — count_headings() is a naive line-by-line
    # check matching compute_metrics() behavior. See design note on count_headings().

class TestBudgetAllocation:
    def test_selects_highest_severity(self): ...
    def test_zero_budget(self): ...
    def test_no_eligible(self): ...
    def test_custom_needs_field(self): ...

class TestPrioritizePages:
    def test_returns_page_order(self): ...
    def test_respects_budget(self): ...
```

---

## Potential Risks

| Risk | Impact | Mitigation |
|---|---|---|
| `tests/corpus/metrics.py` shim breaks experiment scripts | Medium | The shim re-exports all public names. `compare_metrics()` body is preserved verbatim. `load_ground_truth()` wrapper provides the default path. Run existing experiment scripts after shim conversion to verify. |
| `route_page()` routing table incomplete — edge cases not covered by design | Low | The design §13.2 test cases cover all 6 actions. The implementation adds one more edge case: `needs_claude` over budget with no GMFT → `KEEP` (can't do anything). |
| `_has_col_headers` / `_has_br_in_tables` duplicated between `quality_gate.py` and future `tables.py` | Low | Private `_` functions in `quality_gate.py` for now. Item 2 MUST refactor `quality_gate.py` to import from `tables.py` and delete the private copies (see "Duplication migration" note in Research Findings). |

## Integration Strategy

- **No existing code changes except the shim.** The old `quality_gates.py` is untouched — it will be deleted in Item 4.
- **New modules are additive.** They sit alongside existing extraction modules with no import conflicts.
- **Items 2 and 3 import from these modules.** `types.py` is the shared vocabulary for the entire pipeline.

## Validation Approach

1. **Unit tests:** `uv run pytest tests/test_quality_gate.py tests/test_extraction_metrics.py -v`
2. **Shim compatibility:** `uv run python tests/corpus/metrics.py tests/corpus/runs/pipeline_h1/hawker_2020/output.md` (if output exists — verify the shim's `__main__` still works)
3. **Full suite:** `uv run pytest tests/` — verify no regressions from shim conversion
4. **Lint:** `uv run ruff check src/agentic_mbse/extraction/types.py src/agentic_mbse/extraction/metrics.py src/agentic_mbse/extraction/quality_gate.py src/agentic_mbse/extraction/pipeline.py`

---

**Next Step:** After approval → `/_my_plan` for implementation planning

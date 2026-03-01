# Spec: Types, Metrics & Quality Gate

**Status:** Complete (audited 2026-02-23)
**Owner:** Reid W
**Created:** 2026-02-23 16:26 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`
**Epic:** `EPIC-PDFV4-001` Item 1
**Design:** `.project/concepts/doc-extraction/design.md`
**Requirements:** `.project/concepts/doc-extraction/requirements.md`

---

## Business Goals

### Why This Matters

This is the foundation layer for the v4 PDF extraction pipeline. Every other item (enhancement components, pipeline orchestration, integration tests) imports from the types, metrics, and quality gate modules built here. The quality gate is the "decision brain" — it assesses each page and determines what happens to it. Without this layer, nothing else can be wired together.

### Success Criteria

- [ ] All pipeline data types defined and importable
- [ ] Canonical `compute_metrics()` matches existing `tests/corpus/metrics.py` output on identical inputs
- [ ] Quality gate detects math garbling, table anomalies, and text density issues at correct severity levels
- [ ] Routing decision table covers all 6 `PageAction` paths
- [ ] Budget allocation selects highest-severity pages within dollar cap
- [ ] All unit tests pass with no external dependencies (no PDFs, no network, no Claude)

### Priority

P1 — first item on the critical path. Item 2 can start in parallel but depends on these types. Items 3 and 4 depend on everything here.

---

## Problem Statement

### Current State

- `tests/corpus/metrics.py` has working `compute_metrics()` and `ExtractionMetrics` but lives in test code, not production
- `tests/corpus/pipelines/quality_gate.py` has proven quality assessment logic (Stage 3) but uses experiment-only interfaces
- Old `quality_gates.py` uses `RepairRequest` full-document interface — incompatible with per-page routing
- No pipeline data types exist (`PageResult`, `PageDecision`, `PageAction`, etc.)
- No budget allocation mechanism exists in production code

### Desired Outcome

A clean type system, canonical metrics module, and quality gate that serve as the shared foundation for the entire v4 pipeline. All three modules are independently testable with synthetic inputs.

---

## Scope

### In Scope

1. **`src/agentic_mbse/extraction/types.py`** — all pipeline data types from design §3
2. **`src/agentic_mbse/extraction/metrics.py`** — canonical metrics promoted from `tests/corpus/metrics.py`
3. **`src/agentic_mbse/extraction/quality_gate.py`** — per-page assessment, routing decisions, heading anomaly check
4. **`src/agentic_mbse/extraction/pipeline.py`** (stub) — `EnhancerBudget` and `allocate_budget()` only
5. **`tests/corpus/metrics.py`** — converted to thin shim re-exporting from canonical module
6. **`tests/test_quality_gate.py`** — unit tests for quality gate and routing
7. **`tests/test_extraction_metrics.py`** — unit tests for metrics computation

### Out of Scope

- Table detection or enhancement (Item 2)
- Claude or Pandoc integration (Item 2)
- Pipeline orchestration / `extract_pdf()` function (Item 3)
- CLI changes (Item 3)
- `__init__.py` export updates for `extract_pdf` / `PipelineConfig` (Item 3 — `pipeline.py` is a stub here)
- Integration tests against real PDFs (Item 4)
- Deletion of deprecated modules (Item 4)

### Edge Cases & Considerations

- `tests/corpus/metrics.py` has a `compare_metrics()` function not in the design. Leave it in the shim, not promoted. The shim should reference the original code so Item 3/4 can decide whether to promote it later.
- `ExtractionMetrics` in the existing test module has an `extraction_time_seconds` field. The design's `ExtractionMetrics` should preserve this for backward compatibility with the shim.
- `GroundTruth.from_dict()` handles string-to-int key conversion for `heading_levels`. Must be preserved in the canonical version.
- The quality gate's `assess_page()` does NOT compute heading counts — heading anomaly is a document-level check (`assess_heading_anomaly()`). The design is explicit about this separation (design §4.5).
- `route_page()` needs to distinguish `STRIP_FALSE` vs `STRIP_BROKEN` based on what kind of table anomaly was detected (`ColN` headers vs `<br>` artifacts). The `PageAssessment` currently has a single `table_anomaly: bool`. The routing logic must inspect the page markdown to differentiate.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic and design documents unless marked [INFERRED].

#### Types (`types.py`)

1. **FR-T1**: `PageAction` enum with 6 values: `KEEP`, `GMFT_REPLACE`, `GMFT_APPEND`, `STRIP_FALSE`, `STRIP_BROKEN`, `CLAUDE_REPLACE` (design §3)
2. **FR-T2**: `PageResult` dataclass with `page_num: int` (0-indexed) and `markdown: str` (design §3)
3. **FR-T3**: `DetectedTable` dataclass with fields: `markdown`, `confidence`, `num_rows`, `num_cols`, `avg_cell_length`, `image_path`, `extraction_failed`, `detector`, `source` (design §3)
4. **FR-T4**: `PageAssessment` dataclass with fields: `page_num`, `needs_claude`, `needs_gmft`, `reasons`, `severity`, `math_garble_score`, `table_anomaly`, `heading_anomaly`, `low_text_density` (design §3)
5. **FR-T5**: `PageDecision` dataclass with `page_num`, `action: PageAction`, `reasons`, `details` (design §3)
6. **FR-T6**: `CostRecord` dataclass with `page_num`, `cost_usd`, `input_tokens`, `output_tokens`, `model`, `elapsed_seconds`, `table_index` (design §3)
7. **FR-T7**: `PipelineResult` dataclass with `markdown`, `metrics: ExtractionMetrics`, `decisions`, `cost`, `total_cost_usd`, `source`, `elapsed_seconds`, `error` (design §3)
8. **FR-T8**: `types.py` imports `ExtractionMetrics` from `metrics.py` (design §3 shows this dependency)

#### Metrics (`metrics.py`)

9. **FR-M1**: `ExtractionMetrics` dataclass identical to `tests/corpus/metrics.py` — fields: `char_count`, `heading_count`, `heading_by_level`, `table_row_count`, `math_symbol_count`, `figure_ref_count`, `extraction_time_seconds`, plus `to_dict()` and `from_dict()` methods
10. **FR-M2**: `compute_metrics(markdown, elapsed=0.0)` with identical logic to `tests/corpus/metrics.py` (design §4.7)
11. **FR-M3**: `GroundTruth` dataclass with `from_dict()` class method preserving string-to-int key conversion for `heading_levels`
12. **FR-M4**: `AccuracyScore` dataclass with `detected`, `ground_truth`, `delta`, `error_pct`, `category`
13. **FR-M5**: `load_ground_truth(path=None)` loading from JSONL — default path MUST resolve to `tests/corpus/ground_truth.jsonl` (via the same `Path(__file__).parent` trick won't work since the file moved; need explicit default or parameter)
14. **FR-M6**: `score_against_ground_truth(metrics, gt)` with identical scoring logic to `tests/corpus/metrics.py`

#### Quality Gate (`quality_gate.py`)

15. **FR-Q1**: `QualityGateConfig` dataclass with Stage 3-traced defaults: `math_severity_threshold=1.0`, `text_density_min_chars=200`, `heading_density_max=3.0`, `heading_anomaly_boost=0.5` (design §4.5)
16. **FR-Q2**: `assess_page(page_markdown, page_num, config=None)` returning `PageAssessment` — detects math garbling (strikethroughs, replacement chars, bracket operators), table anomalies (`<br>`, `ColN`), text density (design §4.5, requirements FR-5)
17. **FR-Q3**: Math garbling detection uses the same scoring as `tests/corpus/pipelines/quality_gate.py`: strikethroughs 3+ → severity 2.0, 1+ → 0.5; replacement chars 2+ → 2.0, 1+ → 1.0; bracket operators 3+ → 1.0, 1+ → 0.3; Unicode math density boost +0.5 only if already suspicious
18. **FR-Q4**: `assess_heading_anomaly(total_headings, total_pages, config=None)` — document-level check: 0 headings in >2 page doc → anomaly; density > `heading_density_max` → anomaly (design §4.5)
19. **FR-Q5**: `route_page(assessment, gmft_tables, page_markdown, within_claude_budget)` returning `PageDecision` with the 6-action routing table from design §4.5:
    - `needs_claude` AND `within_budget` → `CLAUDE_REPLACE`
    - `needs_claude` AND NOT `within_budget` AND `needs_gmft` AND tables available → `GMFT_REPLACE`
    - `needs_gmft` AND tables available → `GMFT_REPLACE` or `GMFT_APPEND`
    - `needs_gmft` AND no tables AND `ColN` headers in markdown → `STRIP_FALSE`
    - `needs_gmft` AND no tables AND `<br>` in tables → `STRIP_BROKEN`
    - else → `KEEP`
20. **FR-Q6**: `_count_headings(markdown)` — lightweight helper counting ATX headings (lines starting with `# `) (design §4.5)
21. **FR-Q7**: [INFERRED] `GMFT_APPEND` fires when the assessment has no issues flagged but GMFT tables were detected and the page has no existing pipe tables — the ensemble found tables pymupdf4llm missed entirely

#### Budget Helpers (`pipeline.py` stub)

22. **FR-B1**: `EnhancerBudget` dataclass with `total_usd`, `cost_per_page_usd`, and `max_pages` property (design §6.1)
23. **FR-B2**: `allocate_budget(assessments, budget, needs_field="needs_claude")` returning `set[int]` of selected page numbers — generic over any enhancer, sorts by severity descending, takes top N within budget (design §6.1)

#### Test Shim (`tests/corpus/metrics.py`)

24. **FR-S1**: Replace implementation with re-exports from `agentic_mbse.extraction.metrics`: `ExtractionMetrics`, `GroundTruth`, `AccuracyScore`, `compute_metrics`, `load_ground_truth`, `score_against_ground_truth`
25. **FR-S2**: Keep `compare_metrics()` in the shim (not promoted to production) with a comment noting it can be promoted later if needed
26. **FR-S3**: Preserve the `if __name__ == "__main__"` CLI entry point

### Non-Functional Requirements

27. **NFR-1**: All modules have zero external dependencies beyond the standard library and `agentic_mbse.extraction.metrics` (for `types.py`). No pymupdf, no gmft, no network.
28. **NFR-2**: All unit tests use synthetic markdown strings — no PDF files, no network calls, no Claude API.
29. **NFR-3**: `load_ground_truth()` default path must work both from production code and from the test shim. Use a parameter with no default that callers pass explicitly, OR use a well-known path relative to the repo root.

---

## Acceptance Criteria

### Core Functionality

- [ ] `assess_page()` detects math garbling (strikethroughs, replacement chars, bracket operators) at correct severity levels matching Stage 3 thresholds
- [ ] `assess_page()` detects table anomalies (`<br>` in tables, `ColN` auto-headers)
- [ ] `assess_page()` detects low text density (< 200 chars)
- [ ] `assess_page()` returns clean assessment for normal text (no false positives)
- [ ] `route_page()` produces correct `PageAction` for all 6 routing paths (design §13.2 test cases)
- [ ] `route_page()` differentiates `STRIP_FALSE` (ColN) from `STRIP_BROKEN` (`<br>`)
- [ ] `allocate_budget()` selects highest-severity pages within dollar cap
- [ ] `allocate_budget()` returns empty set when budget is $0
- [ ] `compute_metrics()` matches `tests/corpus/metrics.py` output on identical inputs
- [ ] `score_against_ground_truth()` produces correct `AccuracyScore` categories
- [ ] `load_ground_truth()` loads from JSONL file correctly
- [ ] All types are importable from their respective modules

### Quality & Integration

- [ ] Existing tests continue to pass (the shim preserves backward compatibility)
- [ ] All new unit tests pass with `uv run pytest tests/test_quality_gate.py tests/test_extraction_metrics.py`
- [ ] No external dependencies required to run any test in this item
- [ ] `ruff check` and `ruff format` pass on all new/modified files

---

## Test Plan

### `tests/test_quality_gate.py`

Tests from design §13.1 and §13.2:

**Math Garbling (§13.1)**:
- `test_strikethrough_high`: 3+ strikethroughs → `needs_claude=True`, severity >= 2.0
- `test_strikethrough_low`: 1 strikethrough → score >= 0.5, < 1.0 (below threshold alone)
- `test_replacement_chars`: 2+ `\ufffd` → `needs_claude=True`
- `test_bracket_operators`: 3+ `[/][+][-][*]` → `needs_claude=True`
- `test_clean_page`: Normal text → `needs_claude=False`, `needs_gmft=False`

**Table Anomaly (§13.1)**:
- `test_br_in_tables`: `<br>` in pipe table → `needs_gmft=True`, `table_anomaly=True`
- `test_col_headers`: `Col1`/`Col2` headers → `needs_gmft=True`

**Text Density (§13.1)**:
- `test_sparse_page`: < 200 chars → `low_text_density=True`
- `test_normal_page`: >= 200 chars → `low_text_density=False`

**Heading Anomaly**:
- `test_zero_headings_multipage`: 0 headings in >2 pages → anomaly
- `test_high_density`: > 3.0 headings/page → anomaly
- `test_normal_density`: 1.0 heading/page → no anomaly

**Routing (§13.2)**:
- `test_keep`: No issues → `KEEP`
- `test_claude_replace`: `needs_claude` + within budget → `CLAUDE_REPLACE`
- `test_claude_over_budget_fallback_gmft`: `needs_claude` + over budget + `needs_gmft` + tables → `GMFT_REPLACE`
- `test_gmft_replace`: `needs_gmft` + tables available → `GMFT_REPLACE`
- `test_gmft_append`: No issues + GMFT tables + no existing pipe tables → `GMFT_APPEND`
- `test_strip_false`: `needs_gmft` + no tables + ColN headers → `STRIP_FALSE`
- `test_strip_broken`: `needs_gmft` + no tables + `<br>` artifacts → `STRIP_BROKEN`

**Budget Allocation**:
- `test_allocate_within_budget`: 3 pages need Claude, budget for 2 → selects top 2 by severity
- `test_allocate_zero_budget`: Budget $0 → empty set
- `test_allocate_no_eligible`: No pages need Claude → empty set

**Heading Count Helper**:
- `test_count_headings_atx`: ATX headings counted correctly
- `test_count_headings_not_code`: `#` in code blocks or mid-line not counted

### `tests/test_extraction_metrics.py`

Tests from design §13.5:

- `test_heading_count`: `# H1\n## H2\n### H3` → 3 headings, levels {1:1, 2:1, 3:1}
- `test_table_rows`: Pipe table → correct row count (header + separator + data)
- `test_math_symbols`: Unicode math chars (∫, ∑, α, β) counted
- `test_figure_refs`: "Figure 1", "Fig. 2" counted
- `test_empty_string`: Empty input → all zeros
- `test_score_exact`: Detected == ground truth → category "exact"
- `test_score_over`: Detected > ground truth → category "over"
- `test_score_under`: Detected < ground truth → category "under"
- `test_load_ground_truth`: Loads from JSONL, keys are slugs, heading_levels has int keys

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pdf-extraction-v4.md`
- **Design:** `.project/concepts/doc-extraction/design.md` (§3, §4.5, §4.7, §6, §13.1-13.2, §13.5)
- **Requirements:** `.project/concepts/doc-extraction/requirements.md` (FR-5, FR-6, FR-7, FR-11)
- **Stage 3 quality gate:** `tests/corpus/pipelines/quality_gate.py` (source for assess_page logic)
- **Stage 3 metrics:** `tests/corpus/metrics.py` (source for compute_metrics logic)
- **Design:** `.project/active/types-metrics-quality-gate/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` (or skip to `/_my_plan` since the design doc already covers this item thoroughly).

# Epic: PDF Extraction Pipeline v4 — Quality-Gated Per-Page Pipeline

**Epic ID**: EPIC-PDFV4-001
**Status**: Draft
**Priority**: P1
**Created**: 2026-02-23
**Estimated Effort**: 5-6 days

**Concept Documents**:
- **Strategy**: `.project/concepts/doc-extraction-development-strategy.md` (Stages 1-4 experiment results, pipeline evolution rationale)
- **Requirements**: `.project/concepts/doc-extraction/requirements.md` (FR-1 through FR-11, NFR-1 through NFR-4, structural constraints)
- **Design**: `.project/concepts/doc-extraction/design.md` (architecture, type system, component interfaces, orchestration pseudocode)

---

## Executive Summary

Replace the v3 full-document extraction pipeline with a per-page quality-gated pipeline that routes each page independently through pymupdf4llm base extraction, ensemble table detection (GMFT + Img2Table + Docling), and Claude vision enhancement — all within a configurable cost budget. The design is proven by Stage 3 experiments (H5: 70% heading error reduction, 8% table error at $0.12/doc average) and the Stage 4 table-image spike (86% table recall with ensemble, Claude as FP filter).

**Critical Success Factor**: `extract_pdf(path)` produces markdown with quality parity to Stage 3 H5 on the 7-document corpus, with zero regressions on documents that v3 handles correctly, and graceful degradation when optional dependencies (GMFT, Claude, Pandoc) are absent.

---

## Why This Epic?

**Current State**:
- v3 pipeline operates on full documents — quality gates produce `RepairRequest` objects at document level
- Table detection uses single GMFT pass; 7/15 extraction failures on aries unrecoverable without Claude
- Claude structural pass (`claude_structure.py`) uses chunked text-anchor insertions — a fundamentally different approach from Stage 3's proven page-level replacement
- Heading error averages 89% without Claude; 70% with quality-gated Claude (Stage 3 H5)
- `ai_repair.py` does cross-validated region repair — superseded by full-page Claude replacement (no benefit to partial repair per Stage 1D)
- 6 modules (ai_repair, claude_structure, table_repair, quality_gates, table_extraction, postprocess) implement patterns that Stage 3/4 proved suboptimal

**Future State**:
- Single entry point: `extract_pdf(path)` with sensible defaults, two imports for most callers
- Per-page routing: each page assessed independently, routed to best available enhancer
- Ensemble table detection: GMFT → Img2Table → Docling (optional), with Claude as FP filter and extraction fallback
- Budget-controlled Claude: shared budget across table-level and page-level enhancement, highest-severity pages first
- Provenance: every page decision logged with reasons, every Claude call tracked with cost
- Graceful degradation: full pipeline → no detectors → no Claude → pymupdf4llm only (all work correctly)
- 6 deprecated modules removed, replaced by 6 new focused modules (~1,340 LOC estimated)

---

## Success Criteria

- [ ] `extract_pdf()` produces non-empty markdown for all 7 corpus PDFs with `claude_budget_usd=0` (no Claude, no network)
- [ ] Quality gate correctly identifies math garbling, table anomalies, and text density issues on synthetic test pages (unit tests)
- [x] Routing logic covers all 6 `PageAction` paths with unit tests (KEEP, GMFT_REPLACE, GMFT_APPEND, STRIP_FALSE, STRIP_BROKEN, CLAUDE_REPLACE)
- [ ] Table filter passes real tables, rejects prose blocks and layout artifacts (unit tests matching Stage 2 ground truth)
- [ ] Claude sanity check rejects empty, truncated (>50% drop), and prompt-leaked outputs (unit tests)
- [x] Budget allocation selects highest-severity pages first, respects dollar cap (unit tests)
- [x] Pipeline degrades gracefully: no GMFT → skip tables; no Pandoc → skip arXiv; no Claude → GMFT fallback or keep
- [ ] Deprecated modules removed: `ai_repair.py`, `claude_structure.py`, `table_repair.py`, old `quality_gates.py`, old `table_extraction.py`
- [ ] All existing tests updated or replaced; full test suite passes
- [x] CLI: `agentic-mbse extract paper.pdf` uses new pipeline by default; `--backend pymupdf` preserves old path

---

## Backlog Items

### Item 1: Types, Metrics & Quality Gate [1.5 days] — COMPLETE

**Type**: Implementation
**Status**: Complete (audited 2026-02-23)
**Effort**: 1.5 days (spec 0h — design covers this, design 0h — done, plan 1h, execute 10h)
**Dependencies**: None

**Objective**: Build the pipeline's type system, canonical metrics implementation, and quality gate (assessment + routing) — the "decision brain" that determines what happens to each page.

**Current State**:
- ✅ Design complete with full type definitions (design.md §3)
- ✅ `tests/corpus/metrics.py` has working `compute_metrics()` and `ExtractionMetrics` (needs promotion to production)
- ✅ Stage 3 `quality_gate.py` has proven thresholds and detection logic (needs translation from experiment script to production module)
- ⚠️ Old `quality_gates.py` uses `RepairRequest` full-document interface (incompatible with per-page routing)

**Scope**:
1. **`types.py`** (~120 lines): `PageResult`, `DetectedTable`, `PageAssessment`, `PageDecision`, `PageAction`, `CostRecord`, `PipelineResult` — all pipeline data types from design §3
2. **`metrics.py`** (~150 lines): Canonical `ExtractionMetrics`, `compute_metrics()`, `GroundTruth`, `AccuracyScore`, `load_ground_truth()`, `score_against_ground_truth()` — promoted from `tests/corpus/metrics.py`
3. **`quality_gate.py`** (~200 lines): `QualityGateConfig`, `assess_page()`, `assess_heading_anomaly()`, `route_page()`, `prioritize_pages()`, `_count_headings()` — from design §4.5
4. **`pipeline.py` budget helpers** (~50 lines): `EnhancerBudget`, `allocate_budget()` — from design §6
5. **Update `tests/corpus/metrics.py`** to re-export from canonical implementation (thin shim)
6. **Update `__init__.py`** with new exports (`extract_pdf`, `PipelineConfig`, `PipelineResult`)
7. **Unit tests** for all three modules: synthetic markdown tests for quality gate (design §13.1-13.2), metric computation (§13.5), budget allocation, routing decision table

**Out of Scope**:
- Table detection or enhancement (Item 2)
- Claude or Pandoc integration (Item 2)
- Pipeline orchestration (Item 3)
- CLI changes (Item 3)

**Success Criteria**:
- [x] `assess_page()` detects math garbling (strikethroughs, replacement chars, bracket operators) at correct severity levels
- [x] `assess_page()` detects table anomalies (`<br>` in tables, ColN auto-headers)
- [x] `assess_page()` detects low text density (< 200 chars)
- [x] `route_page()` produces correct `PageAction` for all 6 routing paths
- [x] `allocate_budget()` selects highest-severity pages within dollar cap
- [x] `compute_metrics()` matches `tests/corpus/metrics.py` output on sample inputs
- [x] All unit tests pass with no external dependencies (no PDFs, no network, no Claude)

**Deliverables**:
- `src/agentic_mbse/extraction/types.py`
- `src/agentic_mbse/extraction/metrics.py`
- `src/agentic_mbse/extraction/quality_gate.py`
- `tests/test_quality_gate.py`
- `tests/test_extraction_metrics.py`
- Updated `tests/corpus/metrics.py` (thin shim)
- Updated `src/agentic_mbse/extraction/__init__.py`

---

### Item 2: Enhancement Components [1.5 days] — COMPLETE

**Type**: Implementation
**Status**: Complete (audited 2026-02-23)
**Effort**: 1.5 days (spec 0h, design 0h, plan 1h, execute 10h)
**Dependencies**: Item 1 (imports `types.py` data types)

**Objective**: Build all enhancement components — ensemble table detection, arXiv/Pandoc conversion, Claude page and table extraction, and the `extract_pages()` base extraction refactor.

**Current State**:
- ✅ `pymupdf_backend.py` has `extract()` and `CompositeHeaderDetector` — need to add `extract_pages()` returning `list[PageResult]`
- ✅ `table_extraction.py` has basic GMFT detection — needs ensemble (+ Img2Table, + Docling) and secondary filters
- ✅ `ai_repair.py` has `render_page_image()` — moves to `claude_enhance.py`
- ✅ Stage 4 table-image spike proved Claude table extraction from cropped images (27 tables, $0.076/table)
- ⚠️ No Img2Table integration exists yet (available via `gmft.detectors.img2table`)
- ⚠️ No Pandoc arXiv conversion exists yet (Stage 1B experiment scripts only)

**Scope**:
1. **`pymupdf_backend.py` refactor** (~30 lines added): New `extract_pages()` function returning `list[PageResult]` with per-page markdown. `CompositeHeaderDetector` and existing `extract()` preserved.
2. **`tables.py`** (~400 lines): Ensemble detection (`_detect_gmft`, `_detect_img2table`, `_detect_docling`), `filter_tables()`, `assess_table_quality()`, `enhance_table_with_claude()`, markdown utilities (`strip_pipe_tables`, `replace_tables`, `insert_tables_at_end`, `has_br_in_tables`, `has_col_headers`, `count_pipe_rows`) — from design §4.4
3. **`pandoc_convert.py`** (~120 lines): `detect_arxiv_id()`, `check_arxiv_html()`, `convert_arxiv_html()` — from design §4.2
4. **`claude_enhance.py`** (~100 lines): `render_page_image()`, `extract_page_with_claude()`, `validate_claude_output()` — from design §4.6
5. **Unit tests** for each module: table filter tests (design §13.3-13.5), Claude sanity check tests (§13.6), arXiv detection tests (§13.7), table utility tests (§13.5). All Claude/GMFT calls mocked.

**Out of Scope**:
- Pipeline orchestration (Item 3 wires these together)
- CLI changes (Item 3)
- Integration tests against real PDFs (Item 4)
- Docling MCP integration beyond stub (requires MCP server)

**Success Criteria**:
- [x] `extract_pages()` returns `list[PageResult]` with per-page markdown from pymupdf4llm
- [x] `detect_tables_ensemble()` calls GMFT → Img2Table (on GMFT-empty pages) → Docling (optional) in sequence
- [x] `filter_tables()` rejects prose blocks (avg_cell_length > 80) and layout artifacts (1 row, >4 cols)
- [x] `assess_table_quality()` flags extraction-failed tables for Claude enhancement
- [x] `enhance_table_with_claude()` returns `DetectedTable` with `source="claude_cropped"` (mocked)
- [x] `validate_claude_output()` rejects empty output, >50% character drop, and prompt leaks
- [x] `detect_arxiv_id()` extracts arXiv IDs from page 1 text
- [x] `convert_arxiv_html()` strips `<figure>` tags and `\hspace{0pt}` artifacts
- [x] All graceful degradation works: `ImportError` for GMFT/Img2Table → empty dict; missing Pandoc → None

**Deliverables**:
- Updated `src/agentic_mbse/extraction/pymupdf_backend.py` (extract_pages added)
- `src/agentic_mbse/extraction/tables.py`
- `src/agentic_mbse/extraction/pandoc_convert.py`
- `src/agentic_mbse/extraction/claude_enhance.py`
- `tests/test_tables.py`
- `tests/test_pandoc_convert.py`
- `tests/test_claude_enhance.py`

---

### Item 3: Pipeline Orchestration + CLI [1.5 days] — COMPLETE

**Type**: Integration
**Status**: Complete (audited 2026-02-26)
**Effort**: 1.5 days (spec 0h, design 0h, plan 1h, execute 10h)
**Dependencies**: Items 1 and 2

**Objective**: Wire all components into the `extract_pdf()` orchestrator with error isolation, budget management, and decision logging. Integrate with the CLI so `agentic-mbse extract paper.pdf` uses the new pipeline by default.

**Current State**:
- ✅ Items 1-2 provide all components (quality gate, tables, Claude, Pandoc, base extraction)
- ✅ `extract_cli.py` has existing `--backend`, `--enhance`, `--fix-tables` flags
- ✅ Design §5 has detailed pseudocode for orchestration flow
- ⚠️ Current CLI default routes to single-backend extraction — needs to route to `extract_pdf()` for PDFs

**Scope**:
1. **`pipeline.py`** (~250 lines): `PipelineConfig`, `extract_pdf()` orchestrator with 8-step flow (design §5.1), `_try_arxiv_shortcut()`, error isolation wrappers (`_try_detect_tables`), table enhancement loop with shared budget — from design §5
2. **CLI integration**: New flags (`--budget`, `--no-tables`, `--no-img2table`, `--docling`, `--dry-run`, `--model`). Default behavior change: PDF without `--backend` → `extract_pdf()`. Legacy flags preserved with deprecation warnings.
3. **Output persistence** (design §8.3): Write `output.md`, `metrics.json`, `decisions.json`, `cost.json` to output directory
4. **Unit tests**: Pipeline orchestration with mocked components — verify step ordering, budget deduction, error isolation, arXiv shortcut, decision logging

**Out of Scope**:
- Modifying component internals (Items 1-2)
- Integration tests against real PDFs (Item 4)
- Batch processing (Stage 6)

**Success Criteria**:
- [x] `extract_pdf()` produces `PipelineResult` with markdown, metrics, decisions, and cost
- [x] arXiv shortcut fires for arXiv PDFs, returns `source="pandoc_arxiv"`
- [x] Table enhancement deducts from shared budget before page-level Claude
- [x] Error in table detection → pipeline continues with pymupdf4llm only (no crash)
- [x] Error in Claude → page falls back to GMFT or keep (no crash)
- [x] `--dry-run` shows decisions without calling Claude
- [x] `agentic-mbse extract paper.pdf` uses new pipeline; `--backend pymupdf` uses old path
- [x] `decisions.json` and `cost.json` written alongside output markdown
- [x] All pipeline unit tests pass with mocked components

**Deliverables**:
- `src/agentic_mbse/extraction/pipeline.py`
- Updated `src/agentic_mbse/cli/extract_cli.py`
- `tests/test_pipeline.py`
- Updated `tests/test_extract_cli.py`

---

### Item 4: Integration Tests, Cleanup & Ship [1 day]

**Type**: Testing
**Effort**: 1 day (spec 0h, design 0h, plan 0.5h, execute 7h)
**Dependencies**: Item 3

**Objective**: Validate the pipeline against real corpus PDFs, remove deprecated modules, ensure no dormant code, and verify the full test suite passes.

**Current State**:
- ✅ Items 1-3 deliver the complete pipeline with unit tests
- ⚠️ 5 modules to delete: `ai_repair.py`, `claude_structure.py`, `table_repair.py`, old `quality_gates.py`, old `table_extraction.py`
- ⚠️ Existing tests reference deprecated modules (`test_quality_gates.py`, `test_table_extraction.py`, `test_claude_structure.py`)

**Scope**:
1. **Integration tests** (`@pytest.mark.corpus`): Run `extract_pdf()` on all corpus PDFs with `claude_budget_usd=0`. Verify non-empty output, no errors. Compare metrics against ground truth where available (design §13.8)
2. **Delete deprecated modules**: `ai_repair.py`, `claude_structure.py`, `table_repair.py`, `quality_gates.py` (old), `table_extraction.py` (old)
3. **Update/delete affected tests**: `test_quality_gates.py`, `test_table_extraction.py`, `test_claude_structure.py`, any tests importing deleted modules
4. **No-dormant-code check**: Verify every module in `extraction/` is imported by pipeline or CLI (design §15)
5. **Full test suite**: Run `pytest tests/` — all tests pass, no import errors from deleted modules
6. **Deprecation warnings**: `--fix-tables`, `--enhance`, `--structure-only` flags emit deprecation warnings pointing to new pipeline

**Out of Scope**:
- Prompt tuning for specific documents (future iteration)
- Performance optimization (parallelization, caching)
- Updating the `/pdf-analysis` skill (separate work item)
- Batch processing (Stage 6)

**Success Criteria**:
- [ ] All corpus PDFs produce non-empty markdown via `extract_pdf()` with `claude_budget_usd=0`
- [ ] Deprecated modules deleted (5 files)
- [ ] No test imports deleted modules
- [ ] Full test suite passes (`pytest tests/`)
- [ ] No module in `extraction/` is unreachable from `pipeline.py` or `__init__.py`
- [ ] `--enhance` and `--fix-tables` emit deprecation warnings

**Deliverables**:
- `tests/test_corpus_integration.py`
- Deleted: `ai_repair.py`, `claude_structure.py`, `table_repair.py`, `quality_gates.py`, `table_extraction.py`
- Updated/deleted: `test_quality_gates.py`, `test_table_extraction.py`, `test_claude_structure.py`
- Clean `pytest tests/` run

---

## Dependencies

**External**:
- `pymupdf` / `pymupdf4llm` (required — base extraction)
- `gmft` (optional — table detection, degrades gracefully)
- `pandoc` binary (optional — arXiv conversion, degrades gracefully)
- `claude` CLI (optional — vision enhancement, degrades gracefully)

**Internal**:
- Design document: `.project/concepts/doc-extraction/design.md` (Stage 4)
- Requirements: `.project/concepts/doc-extraction/requirements.md` (Stage 4)
- Stage 3 experiment code: `tests/corpus/pipelines/` (reference implementations)
- Stage 4 table spike: `tests/corpus/table_image_spike/` (reference for ensemble detection)

**Item Dependency Graph**:
```
Item 1 (Types + Quality Gate) ──┐
                                 ├──> Item 3 (Pipeline + CLI) ──> Item 4 (Tests + Cleanup)
Item 2 (Enhancement Components) ┘
```

**Critical Path**: Item 1 → Item 3 → Item 4 (4 days). Item 2 can parallel with Item 1 but must complete before Item 3.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `extract_pages()` per-page output differs from `extract()` full-document output (heading calibration) | Medium | Medium | `extract_pages()` uses `page_chunks=True` with full-document `IdentifyHeaders` scan — headings should be identical. Unit test comparing per-page join vs full-document output. |
| GMFT import fails in CI (binary dependency) | Medium | Low | Lazy imports with `try/except ImportError → {}`. Pipeline works without GMFT. |
| Old tests reference deleted modules, causing unexpected failures | Low | Medium | Item 4 specifically audits all imports before deleting. `git grep` for imports of each module before removal. |
| Table enhancement loop exceeds budget (Claude cost estimation inaccurate) | Low | Low | Budget is a hard cap — loop stops when cumulative spend exceeds `claude_budget_usd`. Cost tracking is per-call, not estimated. |
| Stage 3 experiment thresholds don't generalize to new documents | Medium | Medium | All thresholds in `QualityGateConfig` dataclass — configurable per-call. Wrong thresholds mean Claude fires too often (costs money) or too rarely (lower quality), but pipeline still works. |

---

## Timeline

**Total Effort**: 5.5 days (with Items 1 & 2 parallelizable)
**Critical Path**: 4 days (Item 1 → Item 3 → Item 4, with Item 2 completing before Item 3)

| Item | Effort | Dependencies | Parallelizable |
|------|--------|--------------|----------------|
| Item 1: Types, Metrics & Quality Gate | 1.5 days | None | Yes (with Item 2) |
| Item 2: Enhancement Components | 1.5 days | Item 1 types | Yes (with Item 1) |
| Item 3: Pipeline + CLI | 1.5 days | Items 1, 2 | No |
| Item 4: Tests + Cleanup | 1 day | Item 3 | No |

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-02-26
**Next Action**: Begin Item 4 (Integration Tests, Cleanup & Ship)

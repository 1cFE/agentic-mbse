# Spec: Integration Tests, Cleanup & Ship (Epic Item 4)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-26 21:49 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`

---

## Business Goals

### Why This Matters

Items 1-3 built the complete v4 pipeline with unit tests, but the codebase is in a split state: 5 deprecated modules still exist, 5 old test files import them, a benchmark script references deleted APIs, and there's no validation against actual PDFs. Until cleanup and integration testing are done, the codebase has dead code that causes confusion, and the pipeline is unproven on real documents.

### Success Criteria

- [ ] Pipeline produces quality output on real corpus PDFs with Claude enhancement
- [ ] 5 deprecated modules deleted — zero dead extraction code remains (except `postprocess.py`, deferred)
- [ ] `pytest tests/` passes with no import errors from deleted modules
- [ ] Every module in `extraction/` is reachable from pipeline or `__init__.py`
- [ ] Legacy flags emit deprecation warnings pointing to new pipeline

### Priority

P1 — final blocker before the EPIC-PDFV4-001 epic can ship.

---

## Problem Statement

### Current State

- 5 deprecated modules still exist in `src/agentic_mbse/extraction/`: `ai_repair.py`, `claude_structure.py`, `table_repair.py`, `quality_gates.py` (old), `table_extraction.py` (old)
- 5 test files import from deprecated modules: `test_ai_repair.py`, `test_claude_structure.py`, `test_table_repair.py`, `test_quality_gates.py`, `test_table_extraction.py`
- `scripts/benchmark_corpus.py` imports from `quality_gates` and `table_extraction`
- `select_backend()` and `_FALLBACK_ORDER` still contain `.pdf` entries, but PDFs always route to `extract_pdf()` — these are dead code
- Legacy CLI flags (`--fix-tables`, `--enhance`, `--structure-only`) were removed in Item 3 but not replaced with deprecation stubs
- No integration tests run the pipeline against real corpus PDFs
- No ground truth quality assertions exist

### Desired Outcome

- `tests/test_corpus_integration.py` validates the full pipeline (with Claude budget) against 7 ground-truth corpus PDFs and verifies non-empty output for all 15
- All deprecated modules deleted, deprecated test files deleted
- `scripts/benchmark_corpus.py` updated to use new pipeline API
- `.pdf` dead code removed from `select_backend()` and `_FALLBACK_ORDER`
- Legacy flags (`--fix-tables`, `--enhance`, `--structure-only`) emit deprecation warnings pointing to new pipeline
- `pytest tests/` passes clean

---

## Scope

### In Scope

1. **Integration tests** (`@pytest.mark.corpus`): Run `extract_pdf()` on corpus PDFs with real Claude budget. Verify non-empty output for all 15 PDFs. Compare metrics against ground truth for the 7 reviewed documents. Assert quality thresholds.
2. **Delete 5 deprecated modules**: `ai_repair.py`, `claude_structure.py`, `table_repair.py`, `quality_gates.py` (old), `table_extraction.py` (old)
3. **Delete 5 deprecated test files**: `test_ai_repair.py`, `test_claude_structure.py`, `test_table_repair.py`, `test_quality_gates.py`, `test_table_extraction.py`
4. **Clean up CLI dead code**: Remove `.pdf` entries from `select_backend()` and `_FALLBACK_ORDER` (PDFs always use pipeline). Add deprecation warning stubs for `--fix-tables`, `--enhance`, `--structure-only`.
5. **Update `scripts/benchmark_corpus.py`**: Replace deprecated imports with new pipeline API
6. **No-dormant-code test**: Verify every module in `extraction/` is imported by pipeline, CLI, or `__init__.py`
7. **Full test suite**: `pytest tests/` passes with no import errors

### Out of Scope

- Prompt tuning for specific documents (future iteration)
- Performance optimization (parallelization, caching)
- Updating the `/pdf-analysis` skill (separate work item)
- Deleting `postprocess.py` or cleaning up `pymupdf_backend.extract()` (deferred — skill and legacy path still depend on them)
- Batch processing (Stage 6)
- Docling MCP integration beyond existing stub

### Edge Cases & Considerations

- Some ground truth entries are partial (e.g., `aries_cost_account` has tables only, `energy_amplifier` has headings only). Integration tests MUST only assert on non-null ground truth fields.
- Corpus integration tests cost real money (Claude API calls). They SHOULD be marked `@pytest.mark.corpus` so they can be skipped in CI. Tests with `claude_budget_usd=0` should be a separate subset for offline validation.
- `postprocess.py` is NOT deleted in this item — it is still used by `pymupdf_backend.extract()` (legacy path) and `claude/skills/pdf-analysis/scripts/extract_page.py`. Cleanup deferred to a future work item alongside the skill update.
- `--backend pymupdf` is kept as a valid CLI choice. The `pymupdf` path through `_run_extraction()` → `extract()` remains intact. Only the `.pdf` entries in `select_backend()` auto-selection and `_FALLBACK_ORDER` are removed (dead code — PDFs always use `extract_pdf()`).

---

## Requirements

### Functional Requirements

> Requirements below are from the user's request and epic Item 4 unless marked [INFERRED].

1. **FR-1: Corpus Integration Tests (with Claude)**
   Integration tests MUST run `extract_pdf()` on corpus PDFs with a real Claude budget (default $2.0). Tests MUST verify:
   - Non-empty markdown output for all 15 corpus PDFs
   - No `result.error` for any PDF
   - Metrics scored against ground truth for the 7 reviewed documents
   - Quality thresholds on non-null ground truth fields (heading count, table row count)

2. **FR-2: Offline Integration Tests (budget=0)**
   A separate subset of integration tests MUST run with `claude_budget_usd=0` to verify graceful degradation. These tests verify:
   - Non-empty output for all 15 corpus PDFs without network access
   - No crashes from missing Claude/GMFT/Pandoc

3. **FR-3: Delete Deprecated Modules**
   The following 5 files MUST be deleted:
   - `src/agentic_mbse/extraction/ai_repair.py`
   - `src/agentic_mbse/extraction/claude_structure.py`
   - `src/agentic_mbse/extraction/table_repair.py`
   - `src/agentic_mbse/extraction/quality_gates.py`
   - `src/agentic_mbse/extraction/table_extraction.py`

   **Not deleted**: `postprocess.py` — still used by `pymupdf_backend.extract()` and the `/pdf-analysis` skill. Deferred to future work item.

4. **FR-4: Delete Deprecated Test Files**
   The following 5 test files MUST be deleted:
   - `tests/test_ai_repair.py`
   - `tests/test_claude_structure.py`
   - `tests/test_table_repair.py`
   - `tests/test_quality_gates.py`
   - `tests/test_table_extraction.py`

5. **FR-5: Clean Up CLI Dead Code**
   - Remove `.pdf` entry from `_FALLBACK_ORDER` (PDFs always use pipeline)
   - Remove `.pdf` candidates from `select_backend()` (PDFs never go through backend selection)
   - Keep `--backend pymupdf` as a valid choice (legacy path through `extract()` is intact)
   - Keep `_run_extraction()` pymupdf branch and `_is_available("pymupdf")` (still callable)

6. **FR-6: Deprecation Warning Stubs**
   Add `--fix-tables`, `--enhance`, and `--structure-only` as hidden CLI flags that emit deprecation warnings pointing users to the new pipeline flags (`--budget`, `--no-tables`, etc.). Per epic Item 4 scope §6.

7. **FR-7: Update Benchmark Script**
   `scripts/benchmark_corpus.py` MUST be updated to use the new pipeline API:
   - Replace `from agentic_mbse.extraction.quality_gates import detect_problems` with new pipeline imports
   - Replace `from agentic_mbse.extraction.table_extraction import enhance_tables` with new pipeline imports
   - The script MUST run without import errors after deprecated modules are deleted

8. **FR-8: No-Dormant-Code Check**
   A test MUST verify that every `.py` module in `src/agentic_mbse/extraction/` (excluding `__init__.py`) is reachable from at least one of:
   - `pipeline.py` (via transitive imports)
   - `__init__.py` (direct exports)
   - `extract_cli.py` (CLI dispatch)
   Per design §15 (IC-6).

9. **FR-9: Full Test Suite Passes**
   After all deletions and updates, `pytest tests/` MUST pass with zero failures and zero import errors from deleted modules.

---

## Acceptance Criteria

### Integration Tests
- [ ] All 15 corpus PDFs produce non-empty markdown via `extract_pdf()` with `claude_budget_usd=0`
- [ ] All 15 corpus PDFs produce non-empty markdown via `extract_pdf()` with default budget ($2.0)
- [ ] Ground truth scoring runs on 7 reviewed documents; quality thresholds asserted on non-null fields
- [ ] Integration tests marked `@pytest.mark.corpus` (skippable in CI)

### Cleanup
- [ ] 5 deprecated modules deleted from `src/agentic_mbse/extraction/`
- [ ] 5 deprecated test files deleted from `tests/`
- [ ] `select_backend()` and `_FALLBACK_ORDER` have no `.pdf` entries
- [ ] `--fix-tables`, `--enhance`, `--structure-only` emit deprecation warnings
- [ ] `scripts/benchmark_corpus.py` runs without import errors

### Quality & Integration
- [ ] No-dormant-code test passes: every module in `extraction/` is reachable
- [ ] `pytest tests/` passes (full suite, excluding `@pytest.mark.corpus` if offline)
- [ ] `uv run ruff check src/ tests/` passes
- [ ] No test file imports any deleted module

---

## Inventory: Files to Delete

| File | Reason | Dependents (all resolved by this spec) |
|------|--------|---------------------------------------|
| `src/agentic_mbse/extraction/ai_repair.py` | Superseded by `claude_enhance.py` | `claude_structure.py` (also deleted) |
| `src/agentic_mbse/extraction/claude_structure.py` | Superseded by quality-gated pipeline | `tests/test_claude_structure.py` (deleted) |
| `src/agentic_mbse/extraction/table_repair.py` | Superseded by `tables.py` | `tests/test_table_repair.py` (deleted) |
| `src/agentic_mbse/extraction/quality_gates.py` | Superseded by `quality_gate.py` | `tests/test_quality_gates.py` (deleted), `scripts/benchmark_corpus.py` (updated) |
| `src/agentic_mbse/extraction/table_extraction.py` | Superseded by `tables.py` | `tests/test_table_extraction.py` (deleted), `scripts/benchmark_corpus.py` (updated) |
| `tests/test_ai_repair.py` | Tests deleted module | — |
| `tests/test_claude_structure.py` | Tests deleted module | — |
| `tests/test_table_repair.py` | Tests deleted module | — |
| `tests/test_quality_gates.py` | Tests deleted module | — |
| `tests/test_table_extraction.py` | Tests deleted module | — |

**Total: 10 files deleted**

**Deferred**: `postprocess.py` — still used by `pymupdf_backend.extract()` and `/pdf-analysis` skill `extract_page.py`. Will be cleaned up alongside the skill update.

## Inventory: Files to Modify

| File | Change |
|------|--------|
| `src/agentic_mbse/cli/extract_cli.py` | Remove `.pdf` from `select_backend()` and `_FALLBACK_ORDER`; add `--fix-tables`/`--enhance`/`--structure-only` deprecation stubs |
| `scripts/benchmark_corpus.py` | Replace deprecated imports with new pipeline API |

## Inventory: Files to Create

| File | Purpose |
|------|---------|
| `tests/test_corpus_integration.py` | Integration tests against real corpus PDFs |

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pdf-extraction-v4.md` (Item 4)
- **Design:** `.project/concepts/doc-extraction/design.md` (§13.8 integration tests, §15 dormant code check)
- **Ground Truth:** `tests/corpus/ground_truth.jsonl` (7 documents)
- **Item 3 Spec:** `.project/active/pipeline-orchestration-cli/spec.md` (predecessor)

---

**Next Steps:** After approval, proceed to `/_my_design` or `/_my_plan`

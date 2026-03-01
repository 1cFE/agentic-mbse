# Implementation Plan: Pipeline Orchestration + CLI (Epic Item 3)

**Status:** Complete (audited 2026-02-26)
**Created:** 2026-02-24
**Last Updated:** 2026-02-26

## Source Documents
- **Spec:** `.project/active/pipeline-orchestration-cli/spec.md`
- **Design:** `.project/active/pipeline-orchestration-cli/design.md` ← See here for component inventory, function signatures, CLI flag mapping, test class details

## Implementation Strategy

**Phasing Rationale:**
Phase 1 tackles the orchestrator + its tests first because that's where the complexity lives (8-step flow, error isolation, budget tracking across two enhancement levels). Phase 2 wires it into the CLI — straightforward once the pipeline is proven. Phase 3 is a quick cleanup pass (exports + full validation).

**Overall Validation Approach:**
- Each phase starts with tests (test-first for Phase 1, test-alongside for Phase 2)
- Quality gate and routing use real implementations in tests (deterministic, no deps)
- Only enhancers and detectors are mocked
- Full test suite run after each phase to catch regressions

---

## Phase 1: Pipeline Orchestrator + Tests

### Goal
Implement `PipelineConfig` and `extract_pdf()` in `pipeline.py` with all 8 orchestration steps, error isolation wrappers, and budget tracking. Write comprehensive unit tests. This is the core deliverable — everything else depends on it.

### Test Stencil (Write This First)
```python
# tests/test_pipeline.py — write before implementation

class TestExtractPdfBasicFlow:
    """Verify extract_pdf() produces a PipelineResult with the happy path."""

    @patch("agentic_mbse.extraction.pipeline.extract_page_with_claude")
    @patch("agentic_mbse.extraction.pipeline.detect_tables_ensemble", return_value={})
    @patch("agentic_mbse.extraction.pipeline.extract_pages")
    @patch("agentic_mbse.extraction.pipeline._pandoc_available", return_value=False)
    def test_basic_flow_no_tables_no_claude(self, mock_pandoc, mock_pages, mock_tables, mock_claude):
        mock_pages.return_value = [PageResult(0, "# Page 1\n\nText.")]
        result = extract_pdf(Path("/fake.pdf"), PipelineConfig(claude_budget_usd=0))
        assert result.markdown
        assert result.source == "pdf_pipeline"
        assert len(result.decisions) == 1
        assert result.error is None
        mock_claude.assert_not_called()
```

### Changes Required

**See `design.md` for:**
- `PipelineConfig` fields and defaults → `design.md#pipelineconfig`
- 8-step flow detail → `design.md#extract_pdf----8-step-flow`
- `_try_arxiv_shortcut()` logic → `design.md#_try_arxiv_shortcut`
- `_try_detect_tables()` logic → `design.md#_try_detect_tables`
- Import list → `design.md#imports`
- Mocking strategy → `design.md#mocking-strategy`
- Full test class/method inventory → `design.md#test-classes`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pipeline.py` (NEW — write first)
- [x] Create file with imports from `pipeline`, `types`, `quality_gate`
- [x] `TestPipelineConfig` — defaults, budget-zero behavior (2 tests)
- [x] `TestExtractPdfArxivShortcut` — arxiv detection, fallthrough, error isolation (6 tests)
- [x] `TestExtractPdfBaseExtraction` — pages flow, error propagation (2 tests)
- [x] `TestExtractPdfTableEnhancement` — detection disabled/error, filter, Claude enhance/FP/budget/error, dry-run (9 tests)
- [x] `TestExtractPdfQualityGateAndBudget` — step ordering, heading anomaly boost, remaining budget, budget-zero (4 tests)
- [x] `TestExtractPdfClaudePageEnhancement` — accepted, rejected, error, dry-run (4 tests)
- [x] `TestExtractPdfRouteAndMerge` — all actions applied, decisions count, filter reasons in details, cost sum, metrics on merged (5 tests)
- [x] `TestExtractPdfStepOrdering` — call sequence verification for 4 step-order invariants (4 tests)

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/pipeline.py` (EXTEND — currently 50-line stub)
- [x] Add imports for all component modules (see design.md#imports)
- [x] Add `PipelineConfig` dataclass (~15 lines)
- [x] Add `_try_arxiv_shortcut()` with try/except returning None on failure (~25 lines)
- [x] Add `_try_detect_tables()` with try/except returning {} on failure (~15 lines)
- [x] Add `extract_pdf()` implementing 8-step flow (~140 lines):
  - Step 1: arXiv shortcut (early return)
  - Step 2: Base extraction (only propagating error)
  - Step 3: Ensemble table detection (error-isolated)
  - Step 3b: Table filtering + enhancement loop with per-table try/except, budget tracking
  - Step 4: Quality gate per page + document-level heading anomaly
  - Step 5: Budget allocation with remaining budget
  - Step 6: Claude page enhancement loop with per-page try/except, validation
  - Step 7: Route and merge per page, apply actions
  - Step 8: Join pages, compute_metrics, assemble PipelineResult

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_pipeline.py -v` → All ~36 tests pass
- [x] `uv run pytest tests/ -v` → No regressions in existing tests
- [x] `uv run ruff check src/agentic_mbse/extraction/pipeline.py` → Clean

**Manual:**
- [x] `python -c "from agentic_mbse.extraction.pipeline import extract_pdf, PipelineConfig"` → imports work

**What We Know Works After This Phase:**
- `extract_pdf()` correctly orchestrates all 8 steps in order
- Error isolation: each enhancement step fails independently
- Budget tracking: table spend deducted before page allocation
- All `PageAction` values produce correct merged output
- Decisions and costs are properly assembled in `PipelineResult`

---

## Phase 2: CLI Rewrite + Tests

### Goal
Rewrite `cmd_extract()` to route PDFs through `extract_pdf()`. Add new pipeline flags, remove legacy flags and Layer 2-4 post-processing code. Write output artifacts. Preserve DOCX path unchanged. Update CLI tests.

### Test Stencil (Write This First)
```python
# tests/test_extract_cli.py — new TestCmdExtractPdf class

class TestCmdExtractPdf:
    """Verify PDF files route through extract_pdf() with correct config."""

    @patch("agentic_mbse.cli.extract_cli.extract_pdf")
    def test_pdf_uses_pipeline(self, mock_pipeline, tmp_path):
        pdf = tmp_path / "paper.pdf"
        pdf.touch()
        mock_pipeline.return_value = PipelineResult(
            markdown="# Test", metrics=compute_metrics("# Test"), source="pdf_pipeline"
        )
        args = MockArgs(path=str(pdf), output=str(tmp_path / "out"), budget=2.0,
                        no_tables=False, no_img2table=False, docling=False,
                        model="sonnet", html_path=None, dry_run=False,
                        force=False, index=False, summarize=False,
                        backend=None, timeout=600)
        rc = cmd_extract(args)
        assert rc == EXIT_SUCCESS
        mock_pipeline.assert_called_once()
```

### Changes Required

**See `design.md` for:**
- New flag table → `design.md#new-flags`
- Removed flags → `design.md#removed-flags`
- Preserved flags → `design.md#preserved-flags`
- `cmd_extract()` PDF flow pseudocode → `design.md#cmd_extract-flow-for-pdfs`
- Serialization helpers → `design.md#serialization-helpers`
- Summary printer → `design.md#_print_pipeline_summary`
- Output directory strategy → `design.md#output-directory-for-pdfs`
- Index generation → `design.md#index-generation`
- CLI test inventory → `design.md#5-cli-tests----update-teststest_extract_clipy`

**Specific file changes:**

#### 1. Update CLI Test File
**File:** `tests/test_extract_cli.py` (MODIFY)
- [x] Remove `TestStructuralPass` class entirely (8 tests)
- [x] Remove `test_fix_tables_post_processing` from `TestCmdExtract`
- [x] Update all `MockArgs` constructors: remove `fix_tables`, `enhance`, `structure_only`, `max_repair_pages`; add `budget`, `no_tables`, `no_img2table`, `docling`, `model`, `html_path`, `dry_run`
- [x] Add `TestCmdExtractPdf` class (11 tests — see design.md#testcmdextractpdf)
- [x] Add `TestCmdExtractDocx` class (2 tests — DOCX path unchanged)
- [x] Add `TestLegacyFlagsRemoved` class (4 tests — verify removed flags error)
- [x] Update `TestCLIIntegration` help text expectations

#### 2. Rewrite CLI
**File:** `src/agentic_mbse/cli/extract_cli.py` (MODIFY)
- [x] Add imports: `json`, `extract_pdf`, `PipelineConfig`, `PipelineResult`, `compute_metrics`
- [x] Add `_decision_to_dict()` helper (~8 lines)
- [x] Add `_cost_to_dict()` helper (~10 lines)
- [x] Add `_print_pipeline_summary()` helper (~10 lines)
- [x] In `cmd_extract()` per-document loop: add PDF branch that constructs `PipelineConfig` from args, calls `extract_pdf()`, writes output artifacts (`output.md`, `metrics.json`, `decisions.json`, conditional `cost.json`), handles error reporting
- [x] For PDF skip/force: check `(output_dir / "output.md").exists()` instead of `check_processing_needed()` (the summary.json-based check is tied to `ExtractionResult`; PDFs use `PipelineResult`)
- [x] DOCX path: move existing backend selection + `_run_extraction()` + `write_summary()` + Layer 2-4 code into an `else` branch (only for non-PDF files)
- [x] Remove Layer 2-4 post-processing code from DOCX path too (lines 212-314 — all of `quality_gates.detect_problems`, `table_extraction.enhance_tables`, `claude_structure.enhance_structure`, `ai_repair.repair_document`). This code was only ever applied to PDF extractions.
- [x] Add `--index` support for PDFs: after writing `output.md`, run `generate_index()` on it if `--index` is set
- [x] In `register_extract_subcommand()`: remove `--fix-tables`, `--enhance`, `--structure-only`, `--max-repair-pages` arguments; add `--budget`, `--no-img2table`, `--docling`, `--dry-run`, `--html-path`; update `--model` choices to include "sonnet" default; repurpose `--no-tables` help text

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_extract_cli.py -v` → All tests pass (new + updated)
- [x] `uv run pytest tests/test_pipeline.py -v` → Phase 1 tests still pass
- [x] `uv run pytest tests/ -v` → No regressions across entire suite
- [x] `uv run ruff check src/agentic_mbse/cli/extract_cli.py` → Clean

**Manual:**
- [x] `uv run agentic-mbse extract --help` → shows new flags, no legacy flags
- [x] `uv run agentic-mbse extract tests/corpus/pdfs/hawker_2020.pdf --budget 0 -o /tmp/test_out` → writes `output.md`, `metrics.json`, `decisions.json` (no `cost.json` since budget=0)
- [x] `uv run agentic-mbse extract tests/corpus/pdfs/hawker_2020.pdf --dry-run -o /tmp/test_dry` → writes artifacts, decisions show routing but no Claude costs
- [x] Verify `output.md` contains non-empty markdown with headings

**What We Know Works After This Phase:**
- PDF files always use the new pipeline
- CLI flags correctly map to `PipelineConfig` fields
- Output artifacts written in correct format
- Legacy flags are gone
- DOCX extraction is unaffected

---

## Phase 3: Exports + Final Validation

### Goal
Update `__init__.py` exports so users can `from agentic_mbse.extraction import extract_pdf`. Run full validation pass.

### Test Stencil
```python
# Quick import test — can add to test_pipeline.py or verify manually
def test_package_exports():
    from agentic_mbse.extraction import extract_pdf, PipelineConfig, PipelineResult
    assert callable(extract_pdf)
```

### Changes Required

**See `design.md` for:**
- Exact `__init__.py` content → `design.md#3-__init__py----add-pipeline-exports`

**Specific file changes:**

#### 1. Package Exports
**File:** `src/agentic_mbse/extraction/__init__.py` (MODIFY)
- [x] Add `from agentic_mbse.extraction.pipeline import PipelineConfig, extract_pdf`
- [x] Add `from agentic_mbse.extraction.types import PipelineResult`
- [x] Add `"extract_pdf"`, `"PipelineConfig"`, `"PipelineResult"` to `__all__`

#### 2. Export Test
**File:** `tests/test_pipeline.py` (APPEND)
- [x] Add `test_package_exports()` verifying the three new exports

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/ -v` → Full suite passes, zero regressions
- [x] `uv run ruff check src/ tests/` → Clean
- [x] `uv run mypy src/agentic_mbse/extraction/pipeline.py` → No type errors (best-effort)

**Manual:**
- [x] `python -c "from agentic_mbse.extraction import extract_pdf, PipelineConfig, PipelineResult; print('OK')"` → prints OK
- [x] Re-run manual smoke test from Phase 2 to confirm end-to-end

**What We Know Works After This Phase:**
- Public API surface matches spec FR-10
- All acceptance criteria from spec are met
- Item 4 (integration tests + cleanup) is unblocked

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: The 8-step orchestration has many error paths. Mitigated by writing tests first — each error isolation wrapper gets its own test before the code exists.
- **Phase 2**: `MockArgs` in ~15 existing tests needs updating (legacy flag removal). Mitigated by doing test updates first, then CLI changes — ensures the test changes are correct before the code changes.
- **Phase 2**: Skip/force check for PDFs uses `output.md` existence (not `summary.json`). This is simpler and correct — the pipeline doesn't produce `ExtractionResult` so `check_processing_needed()` / `write_summary()` don't apply. Documented in the CLI changes above.

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-24
**Actual Changes:**
- Created `tests/test_pipeline.py` with 37 tests (36 class-based + 1 export test)
- Extended `src/agentic_mbse/extraction/pipeline.py` from 50-line stub to ~250 lines: `PipelineConfig`, `_try_arxiv_shortcut()`, `_try_detect_tables()`, `extract_pdf()` 8-step flow
- Moved `extract_pages` import from lazy (inside function) to module-level for mockability

**Issues:**
- Initial test failures due to short page content triggering quality gate low text density (200 char threshold). Fixed by using budget=0 or longer content in tests.

**Deviations:**
- `extract_pages` is a module-level import in pipeline.py instead of lazy import inside extract_pdf(). This is safe because pymupdf_backend.py lazy-imports pymupdf4llm internally.

### Phase 2 Completion
**Completed:** 2026-02-24
**Actual Changes:**
- Rewrote `src/agentic_mbse/cli/extract_cli.py`: PDF files route to `extract_pdf()`, DOCX uses existing backend path. Added `_decision_to_dict()`, `_cost_to_dict()`, `_print_pipeline_summary()` helpers. Removed all Layer 2-4 post-processing code and legacy flags (`--fix-tables`, `--enhance`, `--structure-only`, `--max-repair-pages`). Added new flags (`--budget`, `--no-img2table`, `--docling`, `--dry-run`, `--model`, `--html-path`). Repurposed `--no-tables`.
- Rewrote `tests/test_extract_cli.py`: Removed `TestStructuralPass` (8 tests), `test_fix_tables_post_processing`. Updated `MockArgs` with new flags. Added `TestCmdExtractPdf` (14 tests), `TestCmdExtractDocx` (2 tests), `TestLegacyFlagsRemoved` (4 tests). Updated `TestCLIIntegration` for new flags. Total: 36 tests.
- PDF skip check uses `output.md` existence (not `summary.json`).

**Issues:**
- One test assertion used keyword arg access (`call_kwargs[1]["backend"]`) but `_run_extraction` is called with positional args. Fixed to `call_args[0][2]`.

**Deviations:** None.

### Phase 3 Completion
**Completed:** 2026-02-24
**Actual Changes:**
- Updated `src/agentic_mbse/extraction/__init__.py` with `extract_pdf`, `PipelineConfig`, `PipelineResult` exports
- Added `test_package_exports()` to `tests/test_pipeline.py`

**Issues:** None.
**Deviations:** None.

---

**Status**: Complete

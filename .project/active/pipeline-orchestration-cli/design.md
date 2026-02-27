# Design: Pipeline Orchestration + CLI (Epic Item 3)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-24 06:30 PST
**Branch:** `doc-ingest-clean`
**Commit:** fd47166

## Overview

Wire the 8-step extraction pipeline into `pipeline.py` and rewrite the `extract` CLI subcommand to use it for PDFs. All components (types, quality gate, tables, Claude enhancement, Pandoc conversion, base extraction, metrics) are complete from Items 1-2. This item adds the orchestrator and CLI integration.

## Related Artifacts

- **Spec:** `.project/active/pipeline-orchestration-cli/spec.md`
- **Concept requirements:** `.project/concepts/doc-extraction/requirements.md`
- **Concept design:** `.project/concepts/doc-extraction/design.md` (§5 orchestration, §10 CLI)
- **Epic:** `.project/backlog/epic_pdf-extraction-v4.md` (Item 3)

---

## Research Findings

### Current State of Files to Modify

| File | Current State | Lines |
|------|--------------|:-----:|
| `src/agentic_mbse/extraction/pipeline.py` | Stub: `EnhancerBudget` + `allocate_budget()` only | 50 |
| `src/agentic_mbse/cli/extract_cli.py` | Legacy 4-layer post-processing, old flags | 439 |
| `src/agentic_mbse/extraction/__init__.py` | Only exports `base.py` types | 17 |

### Components Available from Items 1-2

Every function needed by the orchestrator already exists and is tested:

| Component | Module | Key Functions |
|-----------|--------|---------------|
| Base extraction | `pymupdf_backend.py:124` | `extract_pages(pdf_path) → list[PageResult]` |
| arXiv shortcut | `pandoc_convert.py:69,111,132` | `detect_arxiv_id()`, `check_arxiv_html()`, `convert_arxiv_html()` |
| Pandoc check | `pandoc_convert.py:21` | `_pandoc_available()` |
| Table detection | `tables.py:510` | `detect_tables_ensemble(pdf_path, ...) → dict[int, list[DetectedTable]]` |
| Table filtering | `tables.py:190` | `filter_tables(tables) → (kept, reasons)` |
| Table quality | `tables.py:239` | `assess_table_quality(table) → (needs_enhance, reasons)` |
| Table enhancement | `tables.py:548` | `enhance_table_with_claude(table, ...) → (DetectedTable, CostRecord)` |
| Quality gate | `quality_gate.py:252` | `assess_page(markdown, page_num, config) → PageAssessment` |
| Heading anomaly | `quality_gate.py:304` | `assess_heading_anomaly(total, pages, config) → (bool, reasons)` |
| Heading count | `quality_gate.py:235` | `count_headings(markdown) → int` |
| Routing | `quality_gate.py:343` | `route_page(assessment, tables, markdown, budget) → PageDecision` |
| Budget allocation | `pipeline.py:27` | `allocate_budget(assessments, budget, field) → set[int]` |
| Claude page extract | `claude_enhance.py:143` | `extract_page_with_claude(pdf, page, ...) → (str, CostRecord)` |
| Claude validation | `claude_enhance.py:196` | `validate_claude_output(claude_md, orig_md, page) → (accept, reason)` |
| Metrics | `metrics.py:41` | `compute_metrics(markdown) → ExtractionMetrics` |
| Table markdown | `tables.py:104,132,146` | `strip_pipe_tables()`, `insert_tables_at_end()`, `replace_tables()` |

### Legacy Code to Remove from CLI

`extract_cli.py:212-314` contains the old Layer 2-4 post-processing chain:
- L2: `quality_gates.detect_problems()` → `table_extraction.enhance_tables()` (lines 233-254)
- L3: `claude_structure.enhance_structure()` (lines 257-293)
- L4: `ai_repair.repair_document()` (lines 296-313)

All controlled by flags: `--fix-tables`, `--enhance`, `--structure-only`, `--max-repair-pages`, `--model`.

These are replaced by the pipeline's integrated quality gate + routing.

### Existing CLI Infrastructure to Preserve

- `discover_documents()` (line 51) — file discovery, works for both PDF and DOCX
- `select_backend()` (line 73) — still needed for DOCX backend selection
- `_is_available()` (line 25) — backend availability checks
- `_run_extraction()` (line 110) — single-backend dispatch, still needed for DOCX
- `_FALLBACK_ORDER` (line 104) — DOCX fallback logic
- `get_output_dir()`, `check_processing_needed()`, `write_summary()` — from `base.py`, still used
- `--index` / `--summarize` flags — orthogonal to pipeline, keep as-is
- `--force` flag — keep for both PDF and DOCX
- `--timeout` flag — keep for DOCX backend timeout
- `--output` flag — keep, also used for pipeline output

---

## Proposed Design

### 1. `pipeline.py` — Add `PipelineConfig` and `extract_pdf()`

The stub already contains `EnhancerBudget` and `allocate_budget()`. Add `PipelineConfig` dataclass and the `extract_pdf()` orchestrator function.

#### PipelineConfig

```python
@dataclass
class PipelineConfig:
    claude_budget_usd: float = 2.0
    claude_cost_per_page_usd: float = 0.078
    claude_model: str = "sonnet"
    enable_tables: bool = True
    enable_img2table: bool = True
    enable_docling: bool = False
    enable_claude: bool = True
    arxiv_html_path: Path | None = None
    dry_run: bool = False
    page_image_dir: Path | None = None
    quality_gate: QualityGateConfig = field(default_factory=QualityGateConfig)
```

All defaults match Stage 3 proven values (traced in concept design §12, §14).

#### extract_pdf() — 8-Step Flow

```python
def extract_pdf(
    pdf_path: Path,
    config: PipelineConfig | None = None,
) -> PipelineResult:
```

The function implements the 8 steps from spec FR-3. Each step calls existing component functions:

**Step 1: arXiv shortcut** — `_try_arxiv_shortcut(pdf_path, config)`. Returns early with `source="pandoc_arxiv"` on success, `None` on failure. Checks `_pandoc_available()` first, then `config.arxiv_html_path` or auto-detect via `detect_arxiv_id()` + `check_arxiv_html()`. Entire step wrapped in try/except (returns `None` on any error).

**Step 2: Base extraction** — `pymupdf_backend.extract_pages(pdf_path)`. Returns `list[PageResult]`. This is the ONLY step that propagates errors — if it fails, return `PipelineResult(error=str(exc))`.

**Step 3: Ensemble table detection** — `_try_detect_tables(pdf_path, config)`. Calls `detect_tables_ensemble()` if `config.enable_tables`. Wrapped in try/except returning `{}` on failure (ImportError or runtime).

**Step 3b: Table filtering and enhancement** — For each page's detected tables:
1. `filter_tables()` to apply secondary filters
2. `assess_table_quality()` for each kept table
3. `enhance_table_with_claude()` if needed AND within budget AND not dry_run
4. If Claude returns empty markdown → drop table (FP filter)
5. If no Claude (budget/dry_run/disabled) and extraction_failed → drop table
6. Track table-level Claude cost, deduct from shared budget

Each individual table enhancement wrapped in try/except (skip that table on failure).

**Step 4: Quality gate** — `assess_page()` for each page. Then `assess_heading_anomaly()` at document level; if anomaly, boost severity on `needs_claude` pages.

**Step 5: Budget allocation** — Remaining budget = `claude_budget_usd - table_claude_spend`. Call `allocate_budget()` to select highest-severity pages.

**Step 6: Claude page enhancement** — For each selected page (if `enable_claude` and not `dry_run`): `extract_page_with_claude()`, then `validate_claude_output()`. Track cost regardless of acceptance. Each page wrapped in try/except (skip on failure, log warning).

**Step 7: Route and merge** — `route_page()` for each page. Apply the decision:
- `CLAUDE_REPLACE` → use Claude result (if available)
- `GMFT_REPLACE` → `replace_tables(page.markdown, tables)`
- `GMFT_APPEND` → `insert_tables_at_end(page.markdown, tables)`
- `STRIP_FALSE` / `STRIP_BROKEN` → `strip_pipe_tables(page.markdown)`
- `KEEP` → `page.markdown`

Capture table_filter_reasons in `PageDecision.details["table_filter"]`.

**Step 8: Assemble** — Join pages with `"\n\n"`, `compute_metrics()`, return `PipelineResult`.

#### _try_arxiv_shortcut()

```python
def _try_arxiv_shortcut(
    pdf_path: Path, config: PipelineConfig
) -> PipelineResult | None:
```

Calls `pandoc_convert._pandoc_available()`, `detect_arxiv_id()`, `check_arxiv_html()`, `convert_arxiv_html()`. Returns `PipelineResult` with `source="pandoc_arxiv"`, empty decisions, computed metrics. Returns `None` on any failure.

#### _try_detect_tables()

```python
def _try_detect_tables(
    pdf_path: Path, config: PipelineConfig
) -> dict[int, list[DetectedTable]]:
```

Wraps `detect_tables_ensemble()` in try/except. Returns `{}` on ImportError or runtime error.

#### Imports

`pipeline.py` imports from:
- `types.py` — `PageAssessment`, `PageDecision`, `PageAction`, `DetectedTable`, `CostRecord`, `PipelineResult`, `PageResult`
- `quality_gate.py` — `QualityGateConfig`, `assess_page`, `assess_heading_anomaly`, `count_headings`, `route_page`
- `tables.py` — `detect_tables_ensemble`, `filter_tables`, `assess_table_quality`, `enhance_table_with_claude`, `strip_pipe_tables`, `replace_tables`, `insert_tables_at_end`
- `claude_enhance.py` — `extract_page_with_claude`, `validate_claude_output`
- `pandoc_convert.py` — `_pandoc_available`, `detect_arxiv_id`, `check_arxiv_html`, `convert_arxiv_html`
- `pymupdf_backend.py` — `extract_pages`
- `metrics.py` — `compute_metrics`

#### Estimated Size

~200 lines. `PipelineConfig` (~15 lines), `extract_pdf()` (~140 lines including error isolation), `_try_arxiv_shortcut()` (~25 lines), `_try_detect_tables()` (~15 lines).

### 2. `extract_cli.py` — Rewrite for Pipeline

#### Strategy

The rewrite follows a clean split:
- **PDF files** → ALWAYS route to `extract_pdf()` (no `--backend` for PDFs)
- **DOCX files** → Keep existing `select_backend()` + `_run_extraction()` path unchanged

The `cmd_extract()` function will dispatch based on file extension. For PDFs, it constructs a `PipelineConfig` from CLI flags, calls `extract_pdf()`, and writes output artifacts.

#### New Flags

| Flag | Type | Default | Maps to |
|------|------|---------|---------|
| `--budget` | float | 2.0 | `PipelineConfig.claude_budget_usd` |
| `--no-tables` | store_true | False | `enable_tables=False` (repurposed from old meaning) |
| `--no-img2table` | store_true | False | `enable_img2table=False` |
| `--docling` | store_true | False | `enable_docling=True` |
| `--dry-run` | store_true | False | `PipelineConfig.dry_run` |
| `--model` | str | "sonnet" | `PipelineConfig.claude_model` |
| `--html-path` | Path | None | `PipelineConfig.arxiv_html_path` |

#### Removed Flags

- `--fix-tables` — removed entirely
- `--enhance` — removed entirely
- `--structure-only` — removed entirely
- `--max-repair-pages` — removed entirely

#### Preserved Flags

- `--output, -o` — output directory (used for both PDF pipeline and DOCX)
- `--backend` — **kept but only applies to DOCX** files; ignored for PDFs
- `--timeout` — kept for DOCX backend timeout
- `--force, -f` — kept for both
- `--index` — kept, runs after pipeline or backend extraction
- `--summarize` — kept, used with `--index`

#### cmd_extract() Flow for PDFs

```python
# Inside the per-document loop, after discovering the file is a PDF:
if doc.suffix.lower() == ".pdf":
    config = PipelineConfig(
        claude_budget_usd=args.budget,
        claude_model=args.model,
        enable_tables=not args.no_tables,
        enable_img2table=not args.no_img2table,
        enable_docling=args.docling,
        arxiv_html_path=Path(args.html_path) if args.html_path else None,
        dry_run=args.dry_run,
    )
    result = extract_pdf(doc, config)

    # Write output artifacts
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "output.md").write_text(result.markdown)
    (output_dir / "metrics.json").write_text(json.dumps(
        result.metrics.to_dict(), indent=2
    ))
    (output_dir / "decisions.json").write_text(json.dumps(
        [_decision_to_dict(d) for d in result.decisions], indent=2
    ))
    if result.cost:
        (output_dir / "cost.json").write_text(json.dumps(
            [_cost_to_dict(c) for c in result.cost], indent=2
        ))

    # Report
    if result.error:
        print(f"  FAIL  {label}: {result.error}")
        failed += 1
    else:
        _print_pipeline_summary(label, result)
        processed += 1
    continue  # Skip DOCX path
```

The DOCX path remains in the else branch with the existing backend selection, fallback, and write_summary logic.

#### Serialization Helpers

Two small helper functions to serialize `PageDecision` and `CostRecord` to dicts for JSON output:

```python
def _decision_to_dict(d: PageDecision) -> dict:
    return {
        "page_num": d.page_num,
        "action": d.action.value,
        "reasons": d.reasons,
        "details": d.details,
    }

def _cost_to_dict(c: CostRecord) -> dict:
    return {
        "page_num": c.page_num,
        "cost_usd": c.cost_usd,
        "input_tokens": c.input_tokens,
        "output_tokens": c.output_tokens,
        "model": c.model,
        "elapsed_seconds": c.elapsed_seconds,
        "table_index": c.table_index,
    }
```

These are simple dict constructors — no need for a serialization library. The dataclasses are flat and the fields are JSON-native types.

#### _print_pipeline_summary()

A short helper that prints a human-readable summary:

```python
def _print_pipeline_summary(label: str, result: PipelineResult) -> None:
    stats = [f"{result.metrics.char_count:,} chars"]
    if result.metrics.heading_count:
        stats.append(f"{result.metrics.heading_count} headings")
    if result.metrics.table_row_count:
        stats.append(f"{result.metrics.table_row_count} table rows")
    if result.total_cost_usd > 0:
        stats.append(f"${result.total_cost_usd:.3f}")
    stats.append(f"{result.elapsed_seconds:.1f}s")
    print(f"   ok   {label} [{result.source}] ({', '.join(stats)})")
```

#### Output Directory for PDFs

For PDF files, the output directory is determined the same way as DOCX — via `get_output_dir(doc, output_base)` from `base.py`. The pipeline writes its artifacts into this directory. The `output.md` file serves as the primary output (analogous to what `write_summary()` creates for DOCX).

For the skip/force check: use `check_processing_needed()` from `base.py` for the existing behavior. The pipeline's `output.md` takes the place of the legacy markdown file.

#### Index Generation

The `--index` flag still works for PDFs. After the pipeline writes `output.md`, the index generation reads it:

```python
if args.index:
    md_path = output_dir / "output.md"
    if md_path.exists():
        from agentic_mbse.extraction.index import generate_index
        idx = generate_index(md_path, summarize=args.summarize, force=args.force)
        if idx:
            print(f"        index → {idx.name}")
```

### 3. `__init__.py` — Add Pipeline Exports

```python
"""Document extraction package — PDF and DOCX to structured markdown."""

from agentic_mbse.extraction.base import (
    ExtractionResult,
    check_processing_needed,
    get_output_dir,
    sanitize_filename,
    write_summary,
)

# New pipeline exports
from agentic_mbse.extraction.pipeline import PipelineConfig, extract_pdf
from agentic_mbse.extraction.types import PipelineResult

__all__ = [
    "ExtractionResult",
    "check_processing_needed",
    "get_output_dir",
    "sanitize_filename",
    "write_summary",
    "extract_pdf",
    "PipelineConfig",
    "PipelineResult",
]
```

### 4. Unit Tests — `tests/test_pipeline.py` (new file)

All tests mock external dependencies. No PDFs, no network, no Claude, no GMFT.

#### Test Strategy

The pipeline tests verify **orchestration logic**: correct step ordering, error isolation, budget tracking, and decision assembly. Component-level tests (quality gate signals, table filtering, Claude validation) are already covered in `test_quality_gate.py`, `test_extraction_metrics.py`, and the existing test files.

#### Test Classes

**TestPipelineConfig** — Verify defaults match spec FR-2:
- `test_defaults()` — all fields have correct default values
- `test_budget_zero_disables_claude()` — `claude_budget_usd=0` + `enable_claude=True` means 0 pages selected

**TestExtractPdfArxivShortcut** — arXiv path (mock `detect_arxiv_id`, `check_arxiv_html`, `convert_arxiv_html`):
- `test_arxiv_detected_html_available()` — returns `PipelineResult(source="pandoc_arxiv")`
- `test_arxiv_detected_no_html()` — falls through to PDF extraction
- `test_no_arxiv_id()` — falls through to PDF extraction
- `test_pandoc_not_available()` — falls through to PDF extraction
- `test_explicit_html_path_overrides_autodetect()` — uses `config.arxiv_html_path`
- `test_arxiv_shortcut_error_falls_through()` — exception in arXiv path → PDF extraction continues

**TestExtractPdfBaseExtraction** — Base path (mock `extract_pages`):
- `test_base_extraction_returns_pages()` — verify pages flow to next step
- `test_base_extraction_error_returns_error_result()` — returns `PipelineResult(error=...)`

**TestExtractPdfTableEnhancement** — Table flow (mock GMFT + Claude):
- `test_table_detection_disabled()` — `enable_tables=False` → no tables detected
- `test_table_detection_import_error()` — GMFT not installed → empty tables, pipeline continues
- `test_table_detection_runtime_error()` — crash → empty tables, pipeline continues
- `test_table_filter_applies()` — prose tables filtered out
- `test_table_claude_enhancement_within_budget()` — enhance called, cost tracked
- `test_table_claude_fp_rejection()` — Claude returns empty → table dropped
- `test_table_claude_budget_exhausted()` — tables beyond budget not enhanced
- `test_table_enhancement_error_skips_table()` — individual table error → skip, continue
- `test_dry_run_no_table_claude()` — `dry_run=True` → no Claude calls for tables

**TestExtractPdfQualityGateAndBudget** — Quality gate + budget:
- `test_quality_gate_runs_after_tables()` — step ordering
- `test_heading_anomaly_boosts_severity()` — document-level check
- `test_budget_allocation_uses_remaining_budget()` — table spend deducted first
- `test_budget_zero_no_claude_pages()` — no page-level Claude when budget=0

**TestExtractPdfClaudePageEnhancement** — Claude pages (mock Claude):
- `test_claude_page_accepted()` — accepted, cost tracked, page replaced
- `test_claude_page_rejected_empty()` — rejected, cost still tracked, falls back
- `test_claude_page_error_continues()` — exception → skip page, continue
- `test_dry_run_no_claude_pages()` — `dry_run=True` → no page-level Claude

**TestExtractPdfRouteAndMerge** — Route + merge:
- `test_all_actions_applied()` — each `PageAction` produces correct output
- `test_decisions_one_per_page()` — `len(decisions) == len(pages)`
- `test_table_filter_reasons_in_details()` — decision.details["table_filter"]
- `test_cost_sum_matches_total()` — `total_cost_usd == sum(cost_records)`
- `test_metrics_computed_on_merged()` — metrics computed on final markdown

**TestExtractPdfStepOrdering** — Verify ordering with call sequence tracking:
- `test_arxiv_before_base_extraction()` — arXiv checked first
- `test_table_enhancement_before_quality_gate()` — tables processed before assessment
- `test_quality_gate_before_budget_allocation()` — assess before allocate
- `test_budget_allocation_before_claude_pages()` — allocate before enhance

#### Mocking Strategy

Use `unittest.mock.patch` to replace all external calls:
- `patch("agentic_mbse.extraction.pipeline.extract_pages")` — returns synthetic `list[PageResult]`
- `patch("agentic_mbse.extraction.pipeline.detect_tables_ensemble")` — returns synthetic tables
- `patch("agentic_mbse.extraction.pipeline.extract_page_with_claude")` — returns synthetic markdown + cost
- `patch("agentic_mbse.extraction.pandoc_convert._pandoc_available")` — returns `True`/`False`
- `patch("agentic_mbse.extraction.pandoc_convert.detect_arxiv_id")` — returns ID or None
- `patch("agentic_mbse.extraction.pandoc_convert.check_arxiv_html")` — returns URL or None
- `patch("agentic_mbse.extraction.pandoc_convert.convert_arxiv_html")` — returns markdown

Quality gate and routing use **real implementations** (they're deterministic, no external deps) — only the enhancers and detectors are mocked.

### 5. CLI Tests — Update `tests/test_extract_cli.py`

#### Changes Needed

**Remove tests for legacy flags:**
- Tests referencing `--fix-tables`, `--enhance`, `--structure-only`, `--max-repair-pages`
- `TestStructuralPass` class (8 tests) — entirely removed

**Add tests for new pipeline path:**

**TestCmdExtractPdf** (new class):
- `test_pdf_uses_pipeline()` — PDF file calls `extract_pdf()`, not old backend path
- `test_pdf_budget_flag()` — `--budget 0` maps to `PipelineConfig(claude_budget_usd=0)`
- `test_pdf_dry_run_flag()` — `--dry-run` maps to `PipelineConfig(dry_run=True)`
- `test_pdf_no_tables_flag()` — `--no-tables` maps to `enable_tables=False`
- `test_pdf_no_img2table_flag()` — `--no-img2table` maps to `enable_img2table=False`
- `test_pdf_docling_flag()` — `--docling` maps to `enable_docling=True`
- `test_pdf_model_flag()` — `--model sonnet` maps to `claude_model="sonnet"`
- `test_pdf_html_path_flag()` — `--html-path /tmp/a.html` maps to `arxiv_html_path`
- `test_pdf_output_files()` — writes `output.md`, `metrics.json`, `decisions.json`
- `test_pdf_cost_json_only_when_claude_used()` — `cost.json` present iff `result.cost` non-empty
- `test_pdf_error_reports_failure()` — `PipelineResult(error=...)` → "FAIL" in output

**TestCmdExtractDocx** (verify existing behavior preserved):
- `test_docx_uses_backend_selection()` — DOCX still goes through `select_backend()` + `_run_extraction()`
- `test_backend_flag_applies_to_docx()` — `--backend pandoc` works for DOCX

**TestLegacyFlagsRemoved**:
- `test_fix_tables_not_in_help()` — `--fix-tables` not recognized
- `test_enhance_not_in_help()` — `--enhance` not recognized
- `test_structure_only_not_in_help()` — `--structure-only` not recognized
- `test_max_repair_pages_not_in_help()` — `--max-repair-pages` not recognized

**Preserved tests:**
- `TestDiscoverDocuments` — unchanged (file discovery)
- `TestSelectBackend` — unchanged (DOCX backend selection)
- `TestCLIIntegration` — update help text expectations

---

## Potential Risks

| Risk | Mitigation |
|------|-----------|
| Import cycle between `pipeline.py` and `pandoc_convert.py` | `pandoc_convert.py` has no imports from `pipeline.py`. One-way dependency. |
| `extract_pages()` raises on corrupt PDF | Step 2 is the ONLY step that propagates errors. Return `PipelineResult(error=...)` so CLI can report it. |
| Table enhancement spend exceeds budget due to race | Budget check is sequential (single-threaded loop). Each table's cost is accumulated before the next check. |
| DOCX extraction regresses | No DOCX code is modified. Only the dispatch logic changes (PDF vs DOCX branching). |
| `check_processing_needed()` doesn't detect pipeline output | The function checks for `output.md` existence. Pipeline writes `output.md` to the same path, so skip logic works. |

---

## Integration Strategy

### How This Fits Into the Workflow

- **Before this:** Items 1-2 delivered all components. Each is independently tested.
- **This item:** Wires components into a single `extract_pdf()` call + CLI integration.
- **After this:** Item 4 runs integration tests against the corpus and deletes deprecated modules (`table_repair.py`, `ai_repair.py`, `claude_structure.py`, old `quality_gates.py`, old `table_extraction.py`).

### What This Replaces

The entire Layer 2-4 post-processing chain in `extract_cli.py:212-314` is replaced by a single call to `extract_pdf()`. The old chain:

```
quality_gates.detect_problems() → table_extraction.enhance_tables() →
claude_structure.enhance_structure() → ai_repair.repair_document()
```

becomes:

```
extract_pdf(doc, config)
```

The old modules (`quality_gates.py`, `table_extraction.py`, `claude_structure.py`, `ai_repair.py`, `table_repair.py`) are NOT deleted in this item — that's Item 4's cleanup scope. They remain in the codebase but are no longer called by the CLI for PDF files.

---

## Validation Approach

### Unit Tests (this item)

- `tests/test_pipeline.py` — ~35 tests covering all 8 steps, error isolation, budget tracking, step ordering
- `tests/test_extract_cli.py` — ~15 new tests for pipeline CLI flags + output files, ~8 removed for legacy flags
- All tests mock external dependencies (zero PDFs, zero network, zero Claude, zero GMFT)
- Quality gate and routing use real implementations (deterministic)

### Integration Tests (Item 4)

- Run `extract_pdf()` on all 7 ground truth corpus PDFs with `claude_budget_usd=0`
- Verify non-empty markdown output for each
- Score against ground truth, verify parity with Stage 3 H1 results

### Manual Verification

- `uv run agentic-mbse extract tests/corpus/pdfs/hawker_2020.pdf --budget 0` produces `output.md`, `metrics.json`, `decisions.json`
- `uv run agentic-mbse extract tests/corpus/pdfs/hawker_2020.pdf --dry-run` shows decisions without Claude calls
- `uv run agentic-mbse extract some.docx` still works via old backend path

---

Next Step: After approval → `/_my_plan` to create implementation phases, or directly `/_my_implement` since the design is straightforward (3 files + 2 test files).

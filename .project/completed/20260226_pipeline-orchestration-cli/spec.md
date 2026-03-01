# Spec: Pipeline Orchestration + CLI (Epic Item 3)

**Status:** Complete (audited 2026-02-26)
**Owner:** Reid W
**Created:** 2026-02-23 19:56 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`

---

## Business Goals

### Why This Matters

Items 1-2 delivered all the individual components — types, metrics, quality gate, ensemble table detection, Claude enhancement, Pandoc conversion, per-page base extraction. But without the orchestrator, none of it is usable. `extract_pdf()` is the single entry point that composes these components into a working pipeline, and the CLI integration is how users actually invoke it.

### Success Criteria

- [x] `extract_pdf(path)` produces non-empty markdown for all 7 corpus PDFs with `claude_budget_usd=0`
- [x] `uv run agentic-mbse extract paper.pdf` uses the new pipeline and writes output artifacts
- [x] Pipeline unit tests pass with all external dependencies mocked
- [x] Item 4 (integration tests + cleanup) is unblocked

### Priority

P1 — critical path. Items 1-2 are complete. Item 4 is blocked on this.

---

## Problem Statement

### Current State

- `pipeline.py` is a stub containing only `EnhancerBudget` and `allocate_budget()` (50 lines)
- `extract_cli.py` routes PDFs to the old single-backend extraction path with Layer 2-4 post-processing (`quality_gates.detect_problems` -> `table_extraction.enhance_tables` -> `claude_structure.enhance_structure` -> `ai_repair.repair_document`)
- Legacy flags (`--fix-tables`, `--enhance`, `--structure-only`, `--max-repair-pages`) control the old pipeline
- `__init__.py` exports only `base.py` types — no pipeline entry point
- No output persistence for decisions, cost, or metrics

### Desired Outcome

- `pipeline.py` contains `PipelineConfig` + `extract_pdf()` implementing the 8-step orchestration flow from design §5
- `extract_cli.py` routes PDFs to `extract_pdf()`, with new flags for pipeline control
- Legacy flags and old post-processing code removed (no users, no backwards compatibility)
- Output artifacts (markdown, metrics.json, decisions.json, cost.json) written to output directory
- `__init__.py` exports `extract_pdf`, `PipelineConfig`, `PipelineResult`

---

## Scope

### In Scope

1. **`pipeline.py` orchestration** — `PipelineConfig`, `extract_pdf()`, `_try_arxiv_shortcut()`, `_try_detect_tables()` error isolation
2. **`extract_cli.py` rewrite** — new pipeline flags, remove legacy flags/code, output persistence
3. **`__init__.py` exports** — add `extract_pdf`, `PipelineConfig`, `PipelineResult`
4. **Unit tests** — `tests/test_pipeline.py`, updated `tests/test_extract_cli.py`

### Out of Scope

- Modifying component internals from Items 1-2 (types, quality_gate, tables, claude_enhance, pandoc_convert, pymupdf_backend)
- Integration tests against real corpus PDFs (Item 4)
- Deleting deprecated modules (Item 4)
- Batch processing (Stage 6)
- Docling MCP integration beyond existing stub

---

## Requirements

### FR-1: Pipeline Entry Point (from requirements §3 FR-1)

The pipeline MUST accept a single PDF file path and return a `PipelineResult` (markdown + metrics + decisions + cost). Optional configuration via `PipelineConfig` dataclass with sensible defaults matching Stage 3's proven values.

```python
def extract_pdf(
    pdf_path: Path,
    config: PipelineConfig | None = None,
) -> PipelineResult:
```

### FR-2: Pipeline Configuration

`PipelineConfig` MUST expose these controls with defaults from design §12:

| Parameter | Type | Default | Source |
|-----------|------|---------|--------|
| `claude_budget_usd` | float | 2.0 | Stage 3 H5 |
| `claude_cost_per_page_usd` | float | 0.078 | Stage 1D |
| `claude_model` | str | "sonnet" | Stage 1D |
| `enable_tables` | bool | True | Stage 3 H1 |
| `enable_img2table` | bool | True | Table spike v2 |
| `enable_docling` | bool | False | Table spike v2 |
| `enable_claude` | bool | True | Stage 3 H5 |
| `arxiv_html_path` | Path \| None | None | FR-2 override |
| `dry_run` | bool | False | — |
| `page_image_dir` | Path \| None | None | Pre-rendered images |
| `quality_gate` | QualityGateConfig | defaults | Stage 3 |

### FR-3: 8-Step Orchestration Flow (from design §5.1)

`extract_pdf()` MUST implement these steps in order:

1. **arXiv shortcut** (FR-2 from requirements) — detect arXiv ID, check HTML availability, convert via Pandoc if available. Return early with `source="pandoc_arxiv"`.
2. **Base extraction** (FR-3 from requirements) — `pymupdf_backend.extract_pages(pdf_path)` returning `list[PageResult]`.
3. **Ensemble table detection** (FR-4 from requirements) — `detect_tables_ensemble()` if `enable_tables`. Returns `dict[int, list[DetectedTable]]`.
4. **Table filtering and enhancement** — For each page's detected tables: `filter_tables()` to reject FPs, `assess_table_quality()` to identify Claude candidates, `enhance_table_with_claude()` within budget. Table-level Claude costs deducted from shared budget first (higher ROI than page-level).
5. **Quality gate** (FR-5 from requirements) — `assess_page()` for each page. Then `assess_heading_anomaly()` at document level; if anomaly detected, boost severity on `needs_claude` pages by `heading_anomaly_boost`.
6. **Budget allocation** (FR-6 from requirements) — Remaining budget (after table enhancement) allocated to page-level Claude. `allocate_budget()` selects highest-severity pages.
7. **Claude page enhancement** — For selected pages: `extract_page_with_claude()`, then `validate_claude_output()`. Accepted results stored; rejected results logged with reason. Cost tracked regardless of acceptance.
8. **Route and merge** (FR-7 from requirements) — `route_page()` for each page, apply decision (CLAUDE_REPLACE, GMFT_REPLACE, GMFT_APPEND, STRIP_FALSE, STRIP_BROKEN, KEEP), join pages, `compute_metrics()`, return `PipelineResult`.

### FR-4: arXiv Shortcut (from design §5.2)

`_try_arxiv_shortcut()` MUST:
- Check `_pandoc_available()` first — return None if no Pandoc
- Use `config.arxiv_html_path` if provided, else auto-detect via `detect_arxiv_id()` + `check_arxiv_html()`
- On success: return `PipelineResult` with `source="pandoc_arxiv"`, empty decisions list, computed metrics
- On failure at any step: return None (fall through to PDF extraction)

### FR-5: Error Isolation (from requirements NFR-3)

Each enhancement step MUST be wrapped in try/except:
- Table detection failure → pipeline continues with `detected_pages = {}`
- Table enhancement failure (individual table) → skip that table, continue
- Claude page enhancement failure (individual page) → page falls back to GMFT or keep
- arXiv shortcut failure → fall through to PDF extraction
- Base extraction (`extract_pages`) is the only step that MAY propagate errors — if it fails, return `PipelineResult` with `error` set

### FR-6: Decision Logging (from requirements FR-8)

Every page routing decision MUST be captured in `PipelineResult.decisions` as `PageDecision` objects. Table filter reasons MUST be captured in `PageDecision.details["table_filter"]` for pages with detected tables.

### FR-7: Cost Tracking (from requirements FR-9)

Every Claude invocation (table-level and page-level) MUST produce a `CostRecord` appended to `PipelineResult.cost`. Table-level records have `table_index` set; page-level records have `table_index=None`. `PipelineResult.total_cost_usd` MUST equal the sum of all `CostRecord.cost_usd`.

### FR-8: CLI Integration (from requirements FR-10, design §10)

The `extract` subcommand MUST:

**New pipeline flags:**
- `--output, -o DIR` — Output directory (existing)
- `--budget FLOAT` — Claude budget in USD (default: 2.0, 0 = no Claude)
- `--no-tables` — Disable all table detection (repurposed from old meaning)
- `--no-img2table` — Disable Img2Table second-pass detection
- `--docling` — Enable Docling third-pass detection
- `--dry-run` — Show quality gate decisions without calling Claude
- `--model MODEL` — Claude model (default: sonnet)
- `--html-path PATH` — arXiv HTML override for Pandoc shortcut

**Behavior:**
- For PDF files: ALWAYS use `extract_pdf()` — no `--backend` option for PDFs
- For DOCX files: keep existing backend selection (docling, pandoc) unchanged
- `--backend` flag is kept but ONLY applies to DOCX files; ignored for PDFs

**Removed flags** (no backwards compatibility):
- `--fix-tables` — removed entirely
- `--enhance` — removed entirely
- `--structure-only` — removed entirely
- `--max-repair-pages` — removed entirely

**Removed code:**
- All Layer 2-4 post-processing logic in `cmd_extract` (the `quality_gates.detect_problems` → `table_extraction.enhance_tables` → `claude_structure.enhance_structure` → `ai_repair.repair_document` chain)

### FR-9: Output Persistence (from design §8.3)

When processing a PDF via `extract_pdf()`, the CLI MUST write to the output directory:
- `output.md` — Final markdown
- `metrics.json` — Serialized `ExtractionMetrics`
- `decisions.json` — Serialized `list[PageDecision]`
- `cost.json` — Serialized `list[CostRecord]` (only if any Claude calls were made)

### FR-10: Package Exports (from design §9.4)

`__init__.py` MUST export:
```python
# Existing exports (still used by DOCX paths)
from agentic_mbse.extraction.base import (
    ExtractionResult,
    check_processing_needed,
    get_output_dir,
    sanitize_filename,
    write_summary,
)

# New pipeline exports
from agentic_mbse.extraction.pipeline import extract_pdf, PipelineConfig
from agentic_mbse.extraction.types import PipelineResult
```

### FR-11: Metrics Computation (from requirements FR-11)

`extract_pdf()` MUST compute `ExtractionMetrics` on the final merged markdown using `compute_metrics()` from `metrics.py`.

---

## Acceptance Criteria

### Core Functionality
- [x] `extract_pdf()` returns `PipelineResult` with non-empty markdown for a mocked PDF
- [x] arXiv shortcut fires when `detect_arxiv_id` returns an ID and HTML is available
- [x] arXiv shortcut returns None when Pandoc unavailable, no arXiv ID, or no HTML
- [x] Table enhancement deducts from shared budget BEFORE page-level Claude allocation
- [x] Budget allocation selects highest-severity pages within remaining dollar cap
- [x] Claude page enhancement calls `validate_claude_output()` and rejects empty/truncated output
- [x] Rejected Claude output still has its cost tracked in `PipelineResult.cost`
- [x] Route-and-merge correctly applies all 6 `PageAction` values
- [x] `PipelineResult.decisions` contains one `PageDecision` per page
- [x] `PipelineResult.total_cost_usd` equals sum of individual `CostRecord.cost_usd`

### Error Isolation
- [x] Table detection ImportError → pipeline continues with empty tables
- [x] Table detection runtime error → pipeline continues with empty tables
- [x] Claude page enhancement error → page falls back per routing logic
- [x] Base extraction error → returns `PipelineResult` with `error` set

### CLI
- [x] `agentic-mbse extract paper.pdf` calls `extract_pdf()` (not old backend path)
- [x] `--budget 0` passes `claude_budget_usd=0` to `PipelineConfig`
- [x] `--dry-run` passes `dry_run=True` to `PipelineConfig`
- [x] `--no-tables` passes `enable_tables=False`
- [x] `--no-img2table` passes `enable_img2table=False`
- [x] `--docling` passes `enable_docling=True`
- [x] `--model sonnet` passes `claude_model="sonnet"`
- [x] `--html-path /tmp/arxiv.html` passes `arxiv_html_path`
- [x] Output files written: `output.md`, `metrics.json`, `decisions.json`
- [x] `cost.json` written only when Claude was used
- [x] Legacy flags removed: `--fix-tables`, `--enhance`, `--structure-only`, `--max-repair-pages` do not appear in `--help`
- [x] DOCX extraction still works via existing backend selection

### Tests
- [x] All pipeline tests pass with zero external dependencies (no PDFs, no network, no Claude, no GMFT)
- [x] Step ordering verified: arXiv check before base extraction, table enhancement before quality gate, quality gate before budget allocation
- [x] Error isolation tested for each wrapper
- [x] Dry-run mode: decisions computed but no Claude calls made
- [x] CLI arg parsing tested for new flags
- [x] Existing non-extraction CLI tests still pass

---

## Related Artifacts

- **Requirements:** `.project/concepts/doc-extraction/requirements.md` (FR-1 through FR-11, NFR-1 through NFR-4)
- **Design:** `.project/concepts/doc-extraction/design.md` (§5 orchestration, §6 budget, §8 provenance, §10 CLI)
- **Epic:** `.project/backlog/epic_pdf-extraction-v4.md` (Item 3)
- **Design:** `.project/active/pipeline-orchestration-cli/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` (or directly to `/_my_plan` since the design document already exists at `.project/concepts/doc-extraction/design.md` and covers this item fully).

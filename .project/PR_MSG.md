# PR: PDF Extraction v4 Pipeline

**Branch:** `doc-ingest-clean` → `main`
**Commits:** 24
**Scale:** 197 files, +44,685 / -4,200 lines

---

## Summary

Complete rewrite of the PDF extraction module. Replaces 5 ad-hoc repair modules with a structured 8-step per-page pipeline: arXiv shortcut → base extraction → ensemble table detection → table filtering/enhancement → quality gate → budget allocation → Claude page enhancement → route & merge.

Includes a 4-stage research methodology (tool deep-dives, ground truth, pipeline experiments, implementation) with corpus infrastructure retained for future regression testing.

---

## What Changed

### New extraction pipeline (`src/agentic_mbse/extraction/`)

Deleted 5 old modules (~1,600 lines): `ai_repair.py`, `claude_structure.py`, `quality_gates.py`, `table_extraction.py`, `table_repair.py`

Added 10 new modules (~3,650 lines):

| Module | Purpose |
|--------|---------|
| `pipeline.py` | 8-step orchestrator: `extract_pdf()`, `PipelineConfig`, budget allocation |
| `types.py` | Shared types: `PageAction`, `PageResult`, `PageAssessment`, `PipelineProfile` |
| `quality_gate.py` | Per-page quality scoring: math garble, table anomaly, heading anomaly, equation fragments |
| `tables.py` | Ensemble table detection (GMFT + Img2Table + Docling stub), filtering, Claude enhancement |
| `claude_enhance.py` | Claude vision page re-extraction with output validation |
| `equations.py` | Equation region detection via `docling-ibm-models` LayoutPredictor |
| `metrics.py` | `ExtractionMetrics` dataclass + `compute_metrics()` |
| `pandoc_convert.py` | arXiv detection + Pandoc HTML→markdown shortcut |
| `profile.py` | Pipeline step timing and summary table |
| `check.py` | `--check` diagnostic probing all pipeline components |

### 8-step pipeline architecture

Each page is independently routed to one of 6 actions: `KEEP`, `CLAUDE_REPLACE`, `GMFT_REPLACE`, `GMFT_APPEND`, `STRIP_FALSE`, `STRIP_BROKEN`. Budget allocation ranks pages by severity and selects the top N within the Claude spending limit.

### `extract --check` diagnostic

New CLI mode that probes every pipeline component (pymupdf4llm, GMFT, Img2Table, Docling, Claude CLI, Pandoc, math garbling, arXiv) and reports health as pass/fail/not_installed/degraded. Ships with a built-in 2-PDF check corpus so it works without user-provided PDFs. `--check-json` for machine-readable output.

### New CLI flags

`--budget`, `--model`, `--no-tables`, `--no-img2table`, `--docling`, `--no-equations`, `--dry-run`, `--profile`, `--html-path`, `--check`, `--check-json`

### Pipeline features (EPIC-PDFV4-002 items 1-4)

- **Quality regressions fixed**: equation-fragment detection, GMFT cross-reference routing, postprocess cleanup (running headers, page numbers, ligatures)
- **Unified image output**: `ImageCollector`/`ImageEntry` pattern for figures + table crops in `output_dir/images/`
- **Pipeline profiling**: `--profile` flag, `PipelineProfile` dataclass, `profile.json` output
- **Equation region detection**: `docling-ibm-models` LayoutPredictor with NMS and crop saving, `--no-equations` flag

### `CompositeHeaderDetector`

Replaced ad-hoc `_academic_header_detector` in `pymupdf_backend.py` with a public class combining font-size and bold+pattern strategies. Validated on 14-document corpus: zero regressions, improvements on 10 of 13 docs.

### Output artifacts

Each extraction now produces: `output.md`, `metrics.json`, `decisions.json`, and optionally `cost.json` and `profile.json`.

### Bug fix: Claude subprocess TTY corruption

Added `start_new_session=True` to subprocess calls invoking the Claude CLI, fixing terminal output blanking when `extract` is run from Claude Code's Bash tool.

### Test suite overhaul

Deleted 5 old test files (~1,600 lines), added 10 new test files (~4,900 lines). Added `slow` marker for corpus integration tests. Default `pytest` excludes slow tests.

### Dependency changes

- `img2table>=1.4.2` promoted from optional extra to core dependency
- `pytest`/`pytest-cov` moved to `dependency-groups.dev`

### Documentation

- `docs/extraction.md` — user-facing CLI reference
- `docs/extraction-internals.md` — developer guide with research methodology and module reference
- Updated `CLAUDE.md` with slow-test instructions and TTY workaround

### Research corpus infrastructure

`tests/corpus/` with 9 pipeline experiments, ground truth, baseline metrics, 16 Pandoc configuration experiments, and experiment runner tooling. Retained as evidence and future regression tooling.

---

## Test plan

- [ ] `uv run pytest tests/` — all non-slow tests pass
- [ ] `uv run pytest tests/ -m ""` — all tests including corpus integration pass
- [ ] `uv run ruff check src/ tests/` — no lint errors
- [ ] `uv run agentic-mbse extract --check` — all installed components report pass/degraded
- [ ] Manual: `uv run agentic-mbse extract --budget 0 <pdf>` produces clean markdown with no regressions

---

## Items remaining on EPIC-PDFV4-002

Items 5 (OCR integration) and 6 (summarize hallucination fix) are not included in this PR and remain in the backlog.

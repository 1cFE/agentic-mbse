# Current Work

**Last Updated**: 2026-02-22

---

## Active Work

### Doc Ingest Clean — Stage 2 Head-to-Head Comparison: **COMPLETE**

**Branch:** `doc-ingest-clean`
**Report:** `tests/corpus/comparison_report.md`
**Ground truth:** `tests/corpus/ground_truth.jsonl`

Consolidated all Stage 1 results (pymupdf4llm, Docling, GMFT, Claude vision, Pandoc) into a head-to-head comparison. Established ground truth for 7 documents via manual PDF review. Added `score_against_ground_truth()` to `tests/corpus/metrics.py`.

Key findings:
- Claude vision is the accuracy ceiling (~12% heading error, ~1% table error)
- pymupdf4llm best_v1 over-detects headings on bold-heavy docs (+45 on paischer) and misses gridless tables
- GMFT is exact for grid-lined tables but over-detects TOC/lists
- Docling times out on 67% of corpus; accurate where it completes
- Recommended pipeline: Pandoc first → pymupdf4llm base → quality gate → Claude vision targeted → GMFT table fix

**Next:** Stage 3 — Pipeline experimentation (test compositions against ground truth)

---

## Recently Completed

### 2026-02-22: Stage 2 Head-to-Head Comparison and Ground Truth

Consolidated all Stage 1 results into a definitive comparison. Established ground truth for 7 corpus documents (4 fully reviewed, 3 partial) via manual PDF review. Produced `tests/corpus/comparison_report.md` (scorecard + pipeline recommendations), `tests/corpus/ground_truth.jsonl` (machine-readable), and `score_against_ground_truth()` in `tests/corpus/metrics.py`. Updated development strategy with Stage 2 completion status.

### 2026-02-22: pymupdf4llm Deep-Dive (Stage 1A)

Systematic evaluation of pymupdf4llm API parameters across 14-document corpus (9 configs tested). Discovered CompositeHeaderDetector as clear winner. Updated `pymupdf_backend.py` with evidence-backed config. Fixed stale test. Full findings report in `.project/active/pymupdf4llm-deep-dive/findings.md`.

### 2026-02-08: EPIC-PDFV3-001 PDF Extraction v3

Claude-powered document structure detection pipeline. 4-layer extraction (pymupdf4llm base → GMFT tables → Claude structure repair → AI quality repair). Benchmarked on 12-doc corpus: 4/5 new docs produce usable INDEX files, zero regressions on original 7 docs. 881 tests passing.

Key deliverables:
- `src/agentic_mbse/extraction/` — 11 modules, ~3,000 lines
- `agentic-mbse extract` CLI subcommand with `--enhance`, `--structure-only`, `--model` flags
- `claude/skills/pdf-analysis/` — interactive PDF extraction skill
- 9 new test files, 3,824 lines of test coverage

### 2026-02-03: Architecture Redesign (4 Epics)

Complete toolkit redesign across 4 phases:

**EPIC-ARCH-001 Structure** — 4-directory architecture (`knowledge/`, `modeling_project/`, `work/`, `data/`), new/revised project templates, YAML frontmatter schemas, cmd_init rewiring, 80+ tests updated.

**EPIC-ARCH-002 Knowledge** — 9 new skills (epic-decomposition, model-validation, pdf-analysis, project-structure, record-learning, requirements-tracking, source-traceability, sysml-conventions, toolkit-awareness). Context measurement and extraction mapping complete.

**EPIC-ARCH-003 Commands** — All 9 existing commands refactored to lean ~300-line format. 5 new commands (analyze-models, formalize-intent, quick-model, review-model, status). All registered in installation pipeline. sysmlv2-doc-analyzer deprecated.

**EPIC-ARCH-004 PM Engine** — 8 typed parsers, deterministic state derivation, dashboard generator, 14 PM mutation operations, CLI subcommands (`agentic-mbse pm`, `agentic-mbse status`). 3,267 lines of PM tests.

### 2026-01-23: ITEM-SYMLINK-001 Tool-Owned File Safety

Hash-based modification detection for tool-owned files. Re-running `init` warns before overwriting local modifications.

### 2026-01-23: ITEM-REGTEST-001 Model Regression Testing

pytest-compatible testing infrastructure for SysML models. `tests/models/` with example tests.

### 2026-01-23: ITEM-RENAME-001 Rename `project/` to `modeling_pm/`

Renamed modeling project management directory for clearer semantic distinction.

---

## Up Next

1. Stage 3: Pipeline experimentation — test compositions against Stage 2 ground truth
2. EPIC-LCOE-001: LCOE Costing Patterns (tracking — active in fusion-tea)

---

## Session Notes

### 2026-02-22

- Completed Phase 3 (Synthesize) of pymupdf4llm deep-dive
- Added Final Recommendation section to findings.md
- Fixed stale test `test_extract_passes_hdr_info_and_table_strategy` — was asserting old `_academic_header_detector`
- Re-ran best config on full 15-PDF corpus, confirmed reproducibility (1 char diff in 109k chars)
- 3 heading regressions vs fusion-tea baseline are inherent pymupdf4llm limitations, documented
- `uv sync` without `--extra dev` strips pytest — use `uv sync --extra dev` to get test deps back

### 2026-02-08

- Archived 31 completed active work items to `.project/completed/`
- Updated BACKLOG.md: EPIC-CMDREV-001 superseded, architecture epics complete, PDFV3 complete
- Added lingering TODOs to backlog (operations.py stubs, TASK-PDF-001 superseded)
- Prepared PR for pdf-extract → master

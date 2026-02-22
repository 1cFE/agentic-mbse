# Current Work

**Last Updated**: 2026-02-22

---

## Active Work

### Doc Ingest Clean — Stage 1A pymupdf4llm Deep-Dive: **COMPLETE**

**Branch:** `doc-ingest-clean`
**Work item:** `.project/active/pymupdf4llm-deep-dive/`

All 4 phases complete. Findings:
- CompositeHeaderDetector (font-size + bold union) is the best `hdr_info` — zero regressions, +10/13 docs improved
- `ignore_code=True` eliminates code fence spam in patent/monospace docs
- `table_strategy="lines"` is correct — `lines_strict` kills real tables
- `pymupdf_backend.py` and `extract_page.py` updated with best config + rationale comments
- Full findings in `.project/active/pymupdf4llm-deep-dive/findings.md`

**Next:** Move to Stage 1B (Docling) or 1C (Pandoc). Pandoc deep-dive spec/plan already drafted (staged).

### Doc Ingest Clean — Stage 1C Pandoc Deep-Dive: **DRAFTED**

Spec, plan, and 16 experiment iterations already staged. Not yet committed.

---

## Recently Completed

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

1. Commit Stage 1A + 1C work on `doc-ingest-clean` branch
2. Stage 1B: Docling deep-dive (evaluate Docling for math, tables, headings that pymupdf4llm misses)
3. Stage 1C: Pandoc deep-dive (experiment iterations already run, needs synthesis)
4. Stage 2: Quality gates and pipeline assembly
5. EPIC-LCOE-001: LCOE Costing Patterns (tracking — active in fusion-tea)

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

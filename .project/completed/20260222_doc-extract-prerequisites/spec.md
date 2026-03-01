# Spec: Document Extraction Prerequisites (Stage 0)

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-02-22 09:41 PST
**Complexity:** LOW
**Branch:** `doc-ingest-clean`

---

## Business Goals

### Why This Matters

The `doc-ingest-clean` branch is a deliberate, staged rebuild of document extraction infrastructure. The previous `ralph/doc-ingest` branch (97 commits, ~25,900 lines) produced useful code but also accumulated anti-patterns — notably 560 lines of regex postprocessing built without fully understanding upstream tool capabilities.

Stage 0 gates all subsequent work. Before we deep-dive into pymupdf4llm parameters (Stage 1) or assemble a pipeline (Stage 3), we need a verified environment with tools working and test data in place. This is the cheapest stage and the one most likely to cause frustrating false starts if skipped.

### Success Criteria

- [ ] A developer on `doc-ingest-clean` can run all extraction tools (pymupdf4llm, Pandoc, Docling MCP) or knows explicitly which are deferred
- [ ] Test corpus PDFs are local and accessible, covering the required variety (text-heavy, table-heavy, math-heavy, scanned)
- [ ] Corpus infrastructure (metrics, papers.jsonl, baseline) is migrated from the worktree and functional
- [ ] The `setup-docling.sh` script is available on this branch for optional Docling setup
- [ ] A documented checklist confirms all prerequisites, re-runnable for new developers

### Priority

Blocking prerequisite for all other stages. Low effort, high gating value.

---

## Problem Statement

### Current State

The `doc-ingest-clean` branch was cut fresh from `main`. It has:
- The v3 extraction pipeline in `src/agentic_mbse/extraction/` (12 modules)
- The `pdf-analysis` skill in `claude/skills/pdf-analysis/`
- `pymupdf4llm>=0.2.9` as a core dependency, `docling>=2.0` and `gmft>=0.3` as optional extras

It does **not** have:
- `tests/corpus/` directory (PDFs, papers.jsonl, metrics.py, baseline/, compare.py)
- `scripts/setup-docling.sh` (342-line Docling MCP setup script)
- Verified Pandoc installation
- Any confirmation that extraction tools actually work on this branch

### Desired Outcome

A verified, ready-to-go development environment where Stage 1 experimentation can begin immediately without environment debugging.

---

## Scope

### In Scope

1. **Migrate test corpus infrastructure** from the worktree (`agentic-mbse_doc-ingest`)
   - `tests/corpus/pdfs/` — 8 PDF files (~28MB), copied locally
   - `tests/corpus/papers.jsonl` — paper metadata registry
   - `tests/corpus/metrics.py` — metric computation module (185 lines)
   - `tests/corpus/compare.py` — comparison report generator (289 lines)
   - `tests/corpus/baseline/` — per-paper baseline metrics (8 directories)
2. **Migrate `scripts/setup-docling.sh`** from the worktree (342 lines)
3. **Verify tool availability** — pymupdf4llm, Pandoc, Docling MCP (or explicit deferral)
4. **Document the verification** as a checklist in this spec (not a separate script)

### Out of Scope

- Writing new extractor classes (Stage 1)
- Modifying the extraction pipeline code
- Running BART iteration loops
- Migrating `src/doc_ingest/` (that's Stages 4-5)
- Creating new test PDFs beyond the existing 8-paper corpus
- Building Docling MCP auto-configuration into `agentic-mbse init` (ITEM-DOCLING-001)

### Edge Cases & Considerations

- PDFs are `.gitignore`'d (28MB total). They MUST NOT be committed to git. The worktree sources them from `../fusion-tea/knowledge/raw/`; we copy them directly from the worktree.
- `setup-docling.sh` is Linux-only (uses `/proc/meminfo`, `nproc`). This is a known limitation (audit issue Cap4 #1). Not fixing it now.
- The worktree's `tests/corpus/phantom_survey.py` (395 lines) is a diagnostic tool specific to the heading regression analysis. It is NOT needed for Stage 0 and SHOULD NOT be migrated unless explicitly needed later.
- The worktree's `tests/corpus/pool/` directory and `tests/corpus/discovery_validation.md` are experimental artifacts, not prerequisites. Do not migrate.

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED].

1. **FR-1**: Copy the 8 test corpus PDFs from the worktree to `tests/corpus/pdfs/` on this branch
2. **FR-2**: Copy `tests/corpus/papers.jsonl` from the worktree
3. **FR-3**: Copy `tests/corpus/metrics.py` from the worktree
4. **FR-4**: Copy `tests/corpus/compare.py` from the worktree
5. **FR-5**: Copy `tests/corpus/baseline/` (all 8 paper directories with `metrics.json`) from the worktree
6. **FR-6**: Copy `scripts/setup-docling.sh` from the worktree
7. **FR-7**: Verify `pymupdf4llm` imports and runs (`uv run python -c "import pymupdf4llm; print(pymupdf4llm.__version__)"`)
8. **FR-8**: Verify `pandoc --version` returns a version
9. **FR-9**: Verify or explicitly defer Docling MCP (run `setup-docling.sh` or document that it is deferred)
10. **FR-10**: [INFERRED] Ensure `tests/corpus/pdfs/` is covered by `.gitignore` so PDFs are never committed
11. **FR-11**: [INFERRED] Add a `tests/corpus/__init__.py` if needed for pytest discovery
12. **FR-12**: [INFERRED] Verify the migrated corpus infrastructure works: `uv run python tests/corpus/metrics.py tests/corpus/baseline/hsu_2020/full_document.md` or equivalent smoke test

### Non-Functional Requirements

- Corpus PDFs MUST NOT be committed to git (they are 28MB and `.gitignore`'d)
- Migration SHOULD be a copy, not a move — the worktree remains intact as reference

---

## Acceptance Criteria

### Core Functionality

- [ ] `tests/corpus/pdfs/` contains all 8 PDFs: hawker_2020, aries_cost_account, helios_design, hsu_2020, delene_2001, sparc_overview, energy_amplifier, woodruff_2026
- [ ] `tests/corpus/papers.jsonl` exists with 8 entries
- [ ] `tests/corpus/metrics.py` exists and can compute metrics on a markdown file
- [ ] `tests/corpus/compare.py` exists
- [ ] `tests/corpus/baseline/` has 8 subdirectories, each with `metrics.json`
- [ ] `scripts/setup-docling.sh` exists on this branch
- [ ] `uv run python -c "import pymupdf4llm"` succeeds
- [ ] `pandoc --version` succeeds
- [ ] Docling MCP is either running or explicitly documented as deferred
- [ ] `.gitignore` covers `*.pdf` and `tests/corpus/pdfs/` (already the case on main — verify preserved)

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] No new files committed that should be `.gitignore`'d

---

## Verification Checklist

Run these steps to confirm all prerequisites are met:

```bash
# 1. Python dependencies
uv run python -c "import pymupdf4llm; print(f'pymupdf4llm: {pymupdf4llm.__version__}')"
uv run python -c "import pymupdf; print(f'pymupdf: {pymupdf.__version__}')"

# 2. Pandoc
pandoc --version | head -1

# 3. Docling MCP (optional — skip if deferring)
# bash scripts/setup-docling.sh

# 4. Test corpus PDFs
ls tests/corpus/pdfs/*.pdf | wc -l  # Should be 8

# 5. Corpus metadata
python -c "
import json
papers = [json.loads(l) for l in open('tests/corpus/papers.jsonl')]
print(f'Papers registered: {len(papers)}')
for p in papers:
    print(f'  {p[\"slug\"]}: {p[\"pages\"]} pages, tables={p.get(\"has_tables\", False)}, math={p.get(\"has_math\", False)}')
"

# 6. Baseline metrics
ls tests/corpus/baseline/*/metrics.json | wc -l  # Should be 8

# 7. Metrics module smoke test
uv run python tests/corpus/metrics.py tests/corpus/baseline/hsu_2020/full_document.md 2>/dev/null \
  || echo "Note: metrics.py needs a full_document.md, not metrics.json — check baseline contents"

# 8. Existing tests still pass
uv run pytest tests/ -x -q
```

---

## Migration Source Reference

All files are copied from the worktree at `/home/reid/1cfe/agentic-mbse_doc-ingest/`:

| Source (worktree) | Destination (this branch) | Notes |
|---|---|---|
| `tests/corpus/pdfs/*.pdf` (8 files, 28MB) | `tests/corpus/pdfs/` | NOT committed to git |
| `tests/corpus/papers.jsonl` | `tests/corpus/papers.jsonl` | 8 entries |
| `tests/corpus/metrics.py` | `tests/corpus/metrics.py` | 185 lines |
| `tests/corpus/compare.py` | `tests/corpus/compare.py` | 289 lines |
| `tests/corpus/baseline/*/metrics.json` | `tests/corpus/baseline/*/metrics.json` | 8 directories |
| `scripts/setup-docling.sh` | `scripts/setup-docling.sh` | 342 lines, Linux-only |

### NOT Migrating

| File | Reason |
|---|---|
| `tests/corpus/phantom_survey.py` | Heading-specific diagnostic, not a prerequisite |
| `tests/corpus/pool/` | Experimental download staging, not needed |
| `tests/corpus/discovery_validation.md` | API validation report, not needed |
| `tests/corpus/current/` | Regenerated by test runs, not a prerequisite |
| `tests/corpus/test_output/` | Transient test output |
| `src/doc_ingest/` | Stages 4-5 scope |
| `experiment-history/`, BART scripts | Out of scope entirely |
| `AGENTS.md`, `IMPLEMENTATION_PLAN.md` | Worktree-specific docs |

---

## Related Artifacts

- **Development Strategy:** `.project/concepts/doc-extraction-development-strategy.md`
- **Resilient Ingestion Concept:** `.project/concepts/resilient-document-ingestion.md`
- **Branch Audit:** `.project/research/20260221-094043_doc-ingest-branch-full-audit.md`
- **Existing extraction code:** `src/agentic_mbse/extraction/` (12 modules on main)
- **pdf-analysis skill:** `claude/skills/pdf-analysis/SKILL.md`

---

**Next Steps:** After approval, execute the migration and verification checklist. Then proceed to Stage 1 deep-dive (`/_my_design` or `/_my_plan` for Stage 1).

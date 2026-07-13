# Current Work

**Last Updated**: 2026-07-11

---

## Active Work

### Neutral Constraint Facts — Production Schemas & Extraction (CONSTRAINT-EXEC Item 1)

**Branch:** `constraint-exec-epic`
**Active:** `.project/active/constraint-facts/`

Spec in progress. Promote S1's frozen fact shapes into production `ConstraintDefinitionFact` /
`ConstraintUsageFact` / `ConstraintSource` schemas with live extraction and versioned JSON
serialization (consumed downstream by sysml-codegen snapshot v3).

### FORMULA Teaching Reconciliation (UPSTREAM-FINDINGS Item 12 follow-up)

**Branch:** `upstream-findings-sync`
**Active:** `.project/active/formula-teaching-reconciliation/`

Implemented (surgical stance). The F6 validator fix (same-part FORMULA no longer FAILs V2) left shipped teaching surfaces contradicting the validator. Reconciled across adr002-calculations.md, common-mistakes.md, the sysml-conventions skill, MODELING_GUIDE + MODELING_PROCESS (templates + tracked install copies): inline FORMULA taught as a convenience for simple arithmetic; calc defs remain recommended for real calculations; calc-output-arithmetic / self-ref / dotted-path still taught as violations.

### C4 Plain-Subtype Instantiation — docstring + test gap (UPSTREAM-FINDINGS Item 12 follow-up)

**Branch:** `upstream-findings-sync`
**Active:** `.project/active/c4-plain-subtype-instantiation/`

Spec in progress. `check_calc_bearing_instantiation` (L6) behaves correctly but its docstring wrongly claims `.types` walks the full supertype chain; the plain-subtype FAIL path is untested. Codegen confirmed (REQ-EXT-13/14) to drop plain-subtype-inherited calcs, so the FAIL is correct — fix is docstring + missing fixture, NOT walking the chain.

### PDF Skill Deployment (ITEM-DOCLING-002)

**Branch:** `doc-ingest-clean`
**Active:** `.project/active/pdf-skill-deployment/`

Integrate Docling MCP server setup into `agentic-mbse init`. Spec and design exist from Feb 6 but predate the v4 pipeline — need design revision before implementation.

**Next:** Revisit design against v4 architecture, then plan and implement.

### PDF Extraction Quality & Features (EPIC-PDFV4-002)

**Branch:** `doc-ingest-clean`
**Epic:** `.project/backlog/epic_pdf-extraction-improvements.md`

Four items, ~4.5 days:
1. **Quality regressions** (Item 1) — Phase 1 (equation fragments) DONE. Phases 2-3 remaining: GMFT xref, postprocess cleanup.
2. **Unified image output** (Item 2) — ImageCollector pattern: figures + table crops in one system. Absorbs IMGEXT-001 + IMGEXT-003 + quality regressions Phase 4.
3. **Equation region detection** (Item 3) — Research + implement detector, plug into image collector.
4. **OCR integration** (Item 4) — EasyOCR via Docling, independent.

**Next:** Finish Item 1 (Phases 2-3), then Item 2 design.

---

## Remaining Active Items (Under Review)

| Item | Status | Decision Needed |
|------|--------|-----------------|
| `docling-deep-dive` | Phases 3-4 not started | Fold remaining work into new epic? |
| `pandoc-deep-dive` | Phases 5-6 not started | Close as research-complete? |
| `iteration-loop` | Spec draft only | Still relevant or shelve? |

---

## Recently Completed

### 2026-07-11: S1 Constraint Fact-Shape Learning Test

Live SysIDE 0.8.4 fixture matrix, golden JSON, and five kept tests now pin all four constraint
source forms, membership/polarity/ownership, actuals/defaults, inheritance/retyping, compound
expressions, and the equality type/unit gate. S1 passed with one explicit restriction: a
dimensioned quantity feature does not prove one exact runtime unit. Full suite: 1,295 passed,
1 skipped, 33 deselected. Findings:
`.project/active/spike-constraint-fact-shapes/findings.md`.

### 2026-07-05: Web Source Capture + arXiv Extraction Pipeline (PR #6, merged)

Five standalone items shipped together on `webfetch-tools` → `main` and archived
to `.project/completed/20260705_*`:

- **Web Source Capture** — `extract <url>` → sanitized markdown (trafilatura +
  Pandoc fallback, CSS-hidden-content stripping, batch mode, `--save-source`).
- **Extraction Provenance** — universal frontmatter (source/backend/hash),
  `--no-frontmatter`.
- **Hash Consolidation** — single SHA256 `compute_source_hash` in `base.py`.
- **Web Extraction Quality** — arXiv HTML routed through Pandoc; figures
  downloaded locally; download failures surfaced as warnings. (Remaining
  non-arXiv-HTML-quality and fusion-tea re-extraction scope dropped at close.)
- **arXiv Latest-Version** — pinned ids/URLs resolve to newest version; served
  version recorded in `source`. **Certified** (`audit.md`), verified live
  (`1706.03762v1` → `v7`).

### 2026-03-29: arXiv HTML Routing Fix

arXiv HTML URLs (`arxiv.org/html/...`) extracted via `agentic-mbse extract <url>` were going through trafilatura, producing broken tables and lost equations. Fixed by detecting arXiv URLs and routing through the existing Pandoc pipeline from `pandoc_convert.py` (same one the PDF arXiv shortcut uses). ~50 lines in `web_backend.py`. Verified on arxiv-2411-06644: Table 3 now has all parameter names, scientific notation, and correct alignment.

### 2026-03-28–29: Web Source Capture

Added URL-to-markdown extraction to `agentic-mbse extract`. Trafilatura backend with Pandoc fallback, HTML sanitization (CSS-hidden content stripping), batch mode via `--urls-from`, frontmatter provenance, and `--save-source` flag. Four commits on `webfetch-tools` branch.

### 2026-03-01: Validation Stack Restructuring (8 → 6 Levels)

Restructured validation pyramid from 8 to 6 levels. Deleted stubs (L5 Semantic, L7 Architecture), merged into L6, renumbered. Post-audit fixed 7 stale references, added 8 L6 negative tests. 895 tests passing.

### 2026-02-27: EPIC-PDFV4-001 PDF Extraction Pipeline v4

Complete rewrite of extraction pipeline. Per-page quality-gated orchestration replacing v3 document-level approach. Includes:
- Research phase: 4 tool deep-dives (pymupdf4llm, Docling/GMFT, Claude vision, Pandoc) + pipeline experimentation + table image spike
- Implementation: Types/metrics/quality-gate → enhancement modules → pipeline orchestration/CLI → integration tests/cleanup
- Bug fixes: Claude invocation silent failures, `extract --check` with built-in test corpus
- All 4 epic items complete, 13 work items archived

### 2026-02-08: EPIC-PDFV3-001 PDF Extraction v3

Claude-powered document structure detection pipeline. 4-layer extraction, 12-doc corpus benchmarked.

---

## Session Notes

### 2026-03-01

- Archived 13 completed work items from `.project/active/` to `.project/completed/`
- Marked EPIC-PDFV4-001 as complete in epic file and backlog
- Updated CHANGELOG with v4 epic and validation restructuring entries
- Cleaned up BACKLOG.md: PDFV4-001 → completed, QUALREG-001 folded into new epic, DOCLING-001 promoted to P1
- 5 active items remain: pdf-skill-deployment, v4-output-quality-regressions, docling-deep-dive, pandoc-deep-dive, iteration-loop

### 2026-02-22

- Completed Phase 3 (Synthesize) of pymupdf4llm deep-dive
- Added Final Recommendation section to findings.md
- Fixed stale test `test_extract_passes_hdr_info_and_table_strategy`
- `uv sync` without `--extra dev` strips pytest — use `uv sync --extra dev`

# Current Work

**Last Updated**: 2026-03-01

---

## Active Work

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

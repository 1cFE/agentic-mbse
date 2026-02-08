# Spec: PDF Extraction v3 — Corpus Validation Baseline

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-08 00:11 UTC
**Complexity:** LOW
**Branch:** pdf-extract
**Commit:** 157d068
**Epic:** `.project/backlog/epic_pdf-extraction-v3.md` — Item 1

---

## Business Goals

### Why This Matters

The v3 epic introduces a Claude-powered structural pass to replace regex-driven header promotion. To measure whether that pass actually improves quality — and to catch regressions — we need a precise, quantified baseline of the current pipeline's output across all 12 corpus documents. The existing quality data is stale: the v1 evaluation report (2026-02-06) predates the v2 pipeline, and the v3 strategy document's grades for the new corpus (D, C+, B-) were recorded before Workstream A bug fixes (commit 157d068) landed. All existing extractions on disk are pre-bug-fix.

### Success Criteria

- [x] All 12 documents re-extracted with the current pipeline (post-bug-fix)
- [x] Per-document metrics recorded across all quality dimensions (structure, tables, body text, images)
- [x] Structured, machine-diff-able baseline table that Item 4 can compare against
- [x] Report saved to `.project/reports/`

### Priority

Gating for Item 4 (Benchmark + Ship). Items 2-3 can proceed in parallel since they use mocked tests.

---

## Problem Statement

### Current State

- v1 evaluation report (`.project/active/document-extraction/evaluation-report.md`) covers 7 original docs with v1 pipeline — outdated
- v3 strategy document has per-document grades for 5 new corpus docs, but these were measured pre-bug-fix (extractions at 18:11-22:39 UTC, bug fixes committed at 23:47 UTC on 2026-02-07)
- No single report covers all 12 documents with the same pipeline version
- Quality data is prose-based grades (D, C+, B-), not structured metrics

### Desired Outcome

A single baseline report with quantified, structured metrics for all 12 documents — extracted with the current pipeline (v2 + Workstream A bug fixes) — that Item 4's benchmark can directly compare against row-by-row.

---

## Scope

### In Scope

- Re-extract all 12 corpus documents with `uv run agentic-mbse extract <path> --index --force`
- Collect automated metrics per document (see FR-2)
- Manual spot-check of header accuracy per document (see FR-3)
- Qualitative grade per document using consistent rubric
- Write baseline report

### Out of Scope

- Fixing any issues discovered (that's Items 2-4)
- Running `--enhance` mode (structural pass doesn't exist yet)
- GMFT table re-extraction (focus is on what the current pipeline produces out of the box)
- Automating the evaluation as a reusable script (one-time manual measurement)
- Evaluating AI repair quality (Layer 3/4)

### Edge Cases & Considerations

- Documents 2235 and 2236 have PDFs named `_.pdf` — ensure the extraction still produces correct output directories
- Document 2243 (127-page slides) may take longer to extract — allow sufficient time
- The `fusion-standards.pdf` exists at two paths (`/home/reid/1cfe/literature/fusion-standards.pdf` and `/home/reid/1cfe/literature/fusion-standards-doc/fusion-standards.pdf`) — use the `-doc/` directory version which already has an output directory

---

## Requirements

### Functional Requirements

> Requirements below derive from the epic definition and the agreed review criteria.

1. **FR-1: Re-extract all 12 documents**. MUST run `uv run agentic-mbse extract <pdf-path> --index --force` on each document to produce fresh `full_document.md`, `INDEX.md`, and `summary.json` using the post-bug-fix pipeline.

   **Corpus manifest** (12 documents):

   | ID | Short Name | Pages | PDF Path |
   |----|-----------|-------|----------|
   | 2232 | Handley (Fusion Markets) | 17 | `literature/2232/Handley et al. - 2021 - *.pdf` |
   | 2233 | Araiinejad (D-T MCF TEA) | 12 | `literature/2233/Araiinejad and Shirvan - 2025 - *.pdf` |
   | 2235 | Global Fusion & AI | 32 | `literature/2235/_.pdf` |
   | 2236 | Digital Twins | 66 | `literature/2236/_.pdf` |
   | 2237 | LANL PJMIF | 61 | `literature/2237/LA-UR-25-24580.pdf` |
   | 2238 | Lampe CBFR | 39 | `literature/2238/Lampe and Manheimer - 1998 - *.pdf` |
   | 2241 | Eester ICRH | 30 | `literature/2241/Eester et al. - 2026 - *.pdf` |
   | 2243 | Rider Slides | 127 | `literature/2243/Rider - Is There a Better Route to Fusion.pdf` |
   | 2244 | Helios Stellarator | 29 | `literature/2244/Swanson et al. - 2025 - *.pdf` |
   | safety | Fusion Safety Program | 14 | `literature/safety-program/Fusion Safety Program.pdf` |
   | fusion-std | Fusion Standards | 4 | `literature/fusion-standards-doc/fusion-standards.pdf` |
   | hazards | Afify Hazards | 8 | `literature/hazards-afify/hazards-34-paper-095-afify.pdf` |

2. **FR-2: Collect automated metrics**. For each document, MUST record these machine-readable metrics from the extraction output:

   | Metric | Source | How |
   |--------|--------|-----|
   | Page count | `full_document.md` | `grep -c '<!-- PAGE:'` |
   | Total lines | `full_document.md` | `wc -l` |
   | Total chars | `summary.json` | `statistics.total_characters` |
   | Image count | `summary.json` | `statistics.total_images` |
   | `##` header count | `full_document.md` | `grep -c '^## '` |
   | `###` header count | `full_document.md` | `grep -c '^### '` |
   | INDEX section count | `INDEX.md` frontmatter | `section_count` field |
   | Pipe table lines | `full_document.md` | `grep -c '^\s*\|'` |
   | Backend used | `summary.json` | `backend_used` field |

3. **FR-3: Manual spot-check of header accuracy**. For each document, MUST manually verify header quality by checking:
   - First 10 pages of the source PDF against extracted headers
   - Last 5 pages (catches appendix/reference section issues)
   - Any pages with known problems from prior evaluations

   Record per document:
   - **False positive headers**: `##`/`###` lines in the markdown that are NOT real section headings (e.g., physics variables, table content, footers promoted to headers)
   - **False negative headers**: Real section headings in the PDF that are NOT marked as `##`/`###` in the markdown
   - **Methodology note**: Which pages were checked

4. **FR-4: Qualitative grading**. MUST assign each document an overall letter grade using this rubric:

   | Grade | Meaning |
   |-------|---------|
   | A | Excellent — correct headers, clean body text, tables as pipes, usable INDEX |
   | A- | Very good — minor issues (1-2 missed subsections, cosmetic artifacts) |
   | B+ | Good — mostly correct structure, some false negatives, tables partially captured |
   | B | Adequate — usable INDEX but incomplete, noticeable artifacts |
   | B- | Passable — INDEX exists but sparse, body text usable, some structural gaps |
   | C+ | Below average — few or no correct headers, body text mostly usable |
   | C | Poor — no useful INDEX, significant body text issues |
   | D+ | Bad — misleading INDEX (false positives), text artifacts throughout |
   | D | Very bad — actively harmful INDEX, substantial content loss |

   Also assign sub-grades for: Structure (headers/INDEX), Tables, Body Text, Images.

5. **FR-5: Baseline report format**. MUST produce a markdown report with:
   - Summary table: all 12 docs, all automated metrics, sub-grades, overall grade
   - Per-document notes: false positive/negative counts, methodology, notable issues
   - Comparison to prior evaluations where available (v1 evaluation report, v3 strategy grades)
   - Section noting which grades changed due to Workstream A bug fixes vs unchanged

### Non-Functional Requirements

- **NFR-1**: Report MUST be structured so that Item 4 can mechanically compare its results row-by-row (same column order, same grade scale, same metric definitions).
- **NFR-2**: Extraction MUST use the installed package from the `pdf-extract` branch at commit 157d068 or later (post-bug-fix).

---

## Acceptance Criteria

### Core Functionality
- [x] All 12 PDFs successfully extracted with `--index --force` (no extraction failures)
- [x] Automated metrics table has all 9 metrics for all 12 documents (108 cells, no blanks)
- [x] Manual spot-check completed for all 12 documents with methodology notes
- [x] Overall grade assigned to all 12 documents
- [x] Sub-grades (Structure, Tables, Body Text, Images) assigned to all 12 documents

### Report Quality
- [x] Report includes comparison column showing delta from prior evaluation where available
- [x] Report identifies which Workstream A bug fixes had observable impact on each document
- [x] Report format matches NFR-1 (Item 4 can compare row-by-row)

### Quality & Integration
- [x] Report saved to `.project/reports/20260208_pdfv3-baseline.md`
- [x] No changes to source code (this is measurement only)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pdf-extraction-v3.md`
- **Concept:** `.project/concepts/pdf-extraction-v3-strategy.md`
- **Prior evaluation (v1):** `.project/active/document-extraction/evaluation-report.md`
- **v2 status report:** `.project/research/20260206_pdf-extraction-v2-phase2-status.md`
- **Design:** Not needed — this is a measurement item, not an implementation item

---

**Completed:** 2026-02-08. Report delivered at `.project/reports/20260208_pdfv3-baseline.md`.

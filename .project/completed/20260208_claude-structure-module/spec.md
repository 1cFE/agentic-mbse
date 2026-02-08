# Spec: Claude Structure Module — Core Implementation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-08 15:35 UTC
**Complexity:** HIGH
**Branch:** pdf-extract
**Epic:** `.project/backlog/epic_pdf-extraction-v3.md` — Item 2

---

## Business Goals

### Why This Matters

The v2 extraction pipeline scores 7/7 usable indexes on its training corpus (documents with bold numbered headings) but 0/5 on unseen documents — slide decks, arXiv papers with italic subsections, Word docs with unnumbered bold headings, and OCR scans. The root cause is that regex header promotion cannot answer the semantic question "is this a heading?" for documents outside the narrow "numbered bold headings" format.

This module provides the Claude-powered structural backbone that closes that gap. By detecting document style from page images and inserting headers via text-anchored structured diffs, it handles any heading convention without requiring new regex patterns for each document type.

### Success Criteria

- [ ] At least 4/5 new corpus documents produce usable INDEX files after structural repair (critical success factor from epic)
- [ ] Original 7-doc corpus produces equal or better results (no regressions)
- [ ] Module is fully unit-tested with mocked Claude calls — no real API calls in tests

### Priority

P1 — on the critical path. Item 3 (pipeline integration) and Item 4 (corpus benchmark) both depend on this module.

---

## Problem Statement

### Current State

- `postprocess.py` has regex header promotion (`promote_bold_headers`, `promote_plain_headers`) that only matches numbered bold patterns (`**1 Introduction**`, `**A.1 Background**`)
- `ai_repair.py` exists with `render_page_image()`, `claude -p` invocation pattern, and cross-validation — but handles tables/equations, not document structure
- Page markers (`<!-- PAGE:N -->`) provide reliable page-to-content mapping
- No module exists for Claude-powered style detection or structural repair
- Documents with italic subsections, unnumbered bold headings, slide titles, or OCR-scanned headings produce zero or garbage headers

### Desired Outcome

A new `claude_structure.py` module that:
1. Detects document style (heading convention, doc type, running headers) from page images + markdown
2. Inserts proper markdown headers via text-anchored structured diffs processed in chunks
3. Caches Phase A results to disk so Phase B retries don't re-pay
4. Provides a gate heuristic (`needs_claude_structure()`) so well-structured documents skip the Claude pass entirely

---

## Scope

### In Scope

1. **`DocumentStyle` dataclass** — structured representation of document style detection results
2. **`HeaderInsertion` dataclass** — text-anchored header insertion instruction
3. **`detect_document_style()`** — Phase A: page thumbnails + markdown → Haiku → cached `DocumentStyle`
4. **`repair_structure()`** — Phase B: chunked markdown + images → Sonnet → `list[HeaderInsertion]`
5. **`apply_insertions()`** — apply validated `HeaderInsertion` list to markdown text
6. **`needs_claude_structure()`** — ratio-based gate heuristic
7. **Post-Phase-A running header strip** — targeted removal using detected `running_headers`
8. **Error handling** — malformed JSON retry, network timeout fallback, Phase A caching
9. **Unit tests** — all functions tested with mocked Claude subprocess calls

### Out of Scope

- Pipeline integration / CLI wiring (Item 3)
- Quality sweep / page-level sampling (deferred per design decision D3)
- Changes to `ai_repair.py` internals (stays as separate Layer 4 per D6)
- Changes to GMFT table extraction
- Documents over 200 pages (noted as future work; chunking handles up to ~200)
- Real-document validation (Item 4)

### Edge Cases & Considerations

- **Chunking boundary headers**: A heading may appear at the end of one chunk and the beginning of the next due to overlap. Deduplication across chunk boundaries is required.
- **Ambiguous anchor text**: Multiple identical text snippets in a document could cause anchor mismatches. Validation MUST reject insertions with unmatched or ambiguous anchors.
- **Empty/minimal documents**: Documents with < 3 pages may not have enough content for meaningful style detection. Phase A SHOULD handle gracefully.
- **Mixed heading conventions**: Some documents use numbered headings for top-level sections and unnumbered bold for subsections. Style detection SHOULD capture this.
- **Pre-existing correct headers**: `apply_insertions()` MUST NOT duplicate headers that regex promotion already placed correctly.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic (Item 2 scope) unless marked [INFERRED].

1. **FR-1: `DocumentStyle` dataclass**
   - MUST include fields: `doc_type`, `heading_convention`, `has_toc`, `running_headers`, `page_number_format`
   - `doc_type`: classification of the document (e.g., academic paper, slide deck, technical report, OCR scan, Word doc)
   - `heading_convention`: how headings appear in the source (e.g., numbered_bold, unnumbered_bold, italic_subsections, slide_titles)
   - `running_headers`: list of detected running header patterns for post-hoc stripping
   - MUST be JSON-serializable for disk caching

2. **FR-2: `HeaderInsertion` dataclass**
   - MUST use `anchor_text` (not line numbers) per design decision D1
   - MUST include: `anchor_text`, `level` (int, 2–6 mapping to ##–######), `title`, `insert_position` (before/after anchor)
   - [INFERRED] SHOULD include a `confidence` or validation status field for downstream filtering

3. **FR-3: `detect_document_style()` — Phase A**
   - MUST render first 3 pages as thumbnails via `render_page_image()` from `ai_repair.py`
   - MUST send thumbnails + first ~200 lines of markdown to Claude (Haiku for cost efficiency per D7)
   - MUST parse structured JSON response with validation
   - MUST cache result to `{output_dir}/style.json` per D8
   - MUST load from cache on subsequent calls (skip Claude if cache exists)
   - MUST handle malformed JSON: retry once, then return a default/fallback `DocumentStyle` with warning

4. **FR-4: `repair_structure()` — Phase B**
   - MUST chunk document into ~20–30 page windows using `<!-- PAGE:N -->` markers per D2
   - MUST use 2–3 page overlap between chunks for boundary consistency
   - For each chunk: MUST send markdown text + style context + 1–2 page images to Claude (Sonnet per D7)
   - Claude MUST return `list[HeaderInsertion]` with text-based anchors per D5
   - MUST validate response: reject insertions with unmatched anchor text, deduplicate, check level consistency
   - MUST merge insertions across chunks (overlap dedup)
   - MUST handle malformed JSON per chunk: retry once, then skip that chunk with warning

5. **FR-5: `apply_insertions()`**
   - MUST apply validated `HeaderInsertion` list to markdown text
   - MUST locate anchor text in the markdown and insert the header line at the correct position (before or after)
   - MUST NOT modify any existing content other than inserting header lines
   - [INFERRED] MUST handle the case where anchor text appears multiple times — use surrounding context or position hints to disambiguate, or skip with warning

6. **FR-6: `needs_claude_structure()` gate heuristic**
   - MUST return `True` when `headers_per_page < 0.1`
   - MUST return `True` when noise fraction > 0.3
   - MUST return `True` when zero depth variance (all `##`, no `###`)
   - [INFERRED] Inputs: the markdown text and page count. SHOULD parse existing `##`/`###` headers and `<!-- PAGE:N -->` markers to compute metrics.
   - [INFERRED] SHOULD be a pure function (no I/O) so it can be unit tested without mocks

7. **FR-7: Post-Phase-A running header strip**
   - After `detect_document_style()` returns `running_headers`, MUST do targeted removal of any remaining running headers that `strip_running_headers()` in `postprocess.py` missed
   - [INFERRED] This is separate from the existing `strip_running_headers()` — it uses the style-detected patterns for precision rather than frequency-based heuristics

8. **FR-8: Error handling**
   - Malformed JSON from Claude → retry once → fall back to regex-only with warning
   - Network/subprocess timeout → same fallback behavior
   - Phase A result MUST be cached to disk so Phase B retry doesn't re-pay for Phase A
   - [INFERRED] All warnings MUST be collected and returned to the caller for logging

### Non-Functional Requirements

- **NFR-1**: All Claude subprocess calls MUST be mocked in tests (no real API calls)
- **NFR-2**: Module SHOULD be ~300 lines (per epic estimate) — keep it focused
- **NFR-3**: Test file SHOULD be ~250 lines (per epic estimate)
- **NFR-4**: MUST follow existing code patterns: `claude -p` invocation via `subprocess.run`, `render_page_image()` reuse, dataclasses for structured types
- **NFR-5**: MUST use existing `<!-- PAGE:N -->` marker parsing pattern from `quality_gates.py`

---

## Acceptance Criteria

### Core Functionality

- [ ] `DocumentStyle` is a dataclass that serializes to/from JSON
- [ ] `HeaderInsertion` is a dataclass with `anchor_text`, `level`, `title`, `insert_position`
- [ ] `detect_document_style()` returns valid `DocumentStyle` for mocked inputs covering all 5 doc types (academic paper, slide deck, technical report, OCR scan, Word doc)
- [ ] `detect_document_style()` caches result to `style.json`; second call loads from cache without invoking Claude
- [ ] `repair_structure()` returns `list[HeaderInsertion]` with text-anchored insertions for mocked inputs
- [ ] `repair_structure()` produces correct chunk windows with 2–3 page overlap (unit tested)
- [ ] `apply_insertions()` correctly inserts headers at anchor positions (unit tested with known markdown)
- [ ] `needs_claude_structure()` returns `True` for profiles matching 4/5 new corpus docs, `False` for profiles matching 5/7 original corpus docs
- [ ] Malformed JSON response → graceful fallback with warning (tested)

### Quality & Integration

- [ ] All existing tests pass (799+)
- [ ] All Claude subprocess calls mocked in tests
- [ ] New tests added for every new public function
- [ ] No changes to `ai_repair.py`, `postprocess.py`, `quality_gates.py`, or any other existing module
- [ ] `ruff check` and `ruff format` pass

---

## Design Decisions (Inherited from Epic)

These decisions were agreed in the concept review and constrain this spec:

| # | Decision | Constraint on this module |
|---|----------|--------------------------|
| D1 | Text-based anchoring | `HeaderInsertion.anchor_text` is a text snippet, not a line number |
| D2 | Chunked processing (~20–30 pages) | `repair_structure()` splits on `<!-- PAGE:N -->` markers with overlap |
| D5 | Return `list[HeaderInsertion]`, not modified markdown | Claude returns structured diffs, not full rewrites |
| D6 | Keep `ai_repair.py` as separate Layer 4 | This module MUST NOT modify `ai_repair.py` |
| D7 | Haiku for Phase A, Sonnet for Phase B | Model selection is part of the prompts/subprocess calls |
| D8 | Cache Phase A result to disk | `style.json` in output directory |

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pdf-extraction-v3.md`
- **Baseline:** `.project/reports/20260208_pdfv3-baseline.md`
- **Research:** `.project/research/20260206_scientific-pdf-extraction.md`
- **Design:** `.project/active/claude-structure-module/design.md` (to be created)
- **Existing code:**
  - `src/agentic_mbse/extraction/ai_repair.py` — `render_page_image()`, `claude -p` pattern
  - `src/agentic_mbse/extraction/postprocess.py` — regex header promotion (preserved for fast-path)
  - `src/agentic_mbse/extraction/quality_gates.py` — `<!-- PAGE:N -->` marker parsing
  - `src/agentic_mbse/extraction/base.py` — `RepairRequest`, `ExtractionResult` types

---

## Deliverables

- `src/agentic_mbse/extraction/claude_structure.py` (~300 lines)
- `tests/test_claude_structure.py` (~250 lines)

---

**Next Steps:** After approval, proceed to `/_my_design`

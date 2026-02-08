# Epic: PDF Extraction v3 — Claude as the Structural Backbone

**Epic ID**: EPIC-PDFV3-001
**Status**: Draft
**Priority**: P1
**Created**: 2026-02-07
**Estimated Effort**: 4-5 days

---

## Executive Summary

Replace regex-driven header promotion — which fails catastrophically on documents outside the narrow "numbered bold headings" format — with a Claude-powered structural pass that can identify headings in any document type. The v2 pipeline achieves 7/7 usable indexes on its training corpus but 0/5 on unseen documents. This epic closes that gap while preserving everything that already works (body text, images, GMFT tables, cross-validation).

**Critical Success Factor**: At least 4/5 new corpus documents produce usable INDEX files with correct heading structure, with zero regressions on the original 7-doc corpus.

---

## Why This Epic?

**Current State**:
- v2 pipeline scores 7/7 usable indexes on the original corpus (documents with bold numbered headings)
- 0/5 usable indexes on the new evaluation corpus (slides, arXiv, Word docs, OCR scans)
- 68 garbage headers on a physics slide deck from over-matching appendix regex
- Regex-driven header promotion cannot generalize — "is this a heading?" is a semantic question
- Existing Layer 3 (ai_repair.py) handles tables/equations but not document structure

**Future State**:
- Claude detects document style (heading convention, running headers, doc type) from a few page images
- Claude adds proper markdown headers via text-anchored structured diffs processed in chunks
- Regex header promotion preserved as free fast-path for documents where it works well
- `--enhance` flag triggers the Claude structural pass; `--fast` explicitly skips it
- 4-5/5 new corpus documents produce usable INDEX files
- Original 7-doc corpus produces identical or better results (no regressions)

---

## Success Criteria

- [ ] `detect_document_style()` correctly classifies all 12 corpus documents (7 original + 5 new)
- [ ] `repair_structure()` produces correct heading hierarchy for at least 4/5 new corpus documents
- [ ] Original 7-doc corpus: no regression in INDEX section counts or heading accuracy in `--fast` mode
- [ ] Original 7-doc corpus: equal or better results in `--enhance` mode
- [ ] `needs_claude_structure()` correctly routes: skips Claude for well-structured docs, escalates for poorly-structured ones
- [ ] Structured diff uses text-based anchoring (not line numbers) — zero off-by-one insertion errors on test corpus
- [ ] Phase A (style detection) result is cached to disk — re-running after Phase B failure doesn't re-pay for Phase A
- [ ] All existing tests pass (799+), new tests added for every new function
- [ ] Full test suite runs without requiring Claude CLI (all Claude calls mocked in tests)
- [ ] Cost actuals documented for all 12 corpus documents in both modes

---

## Backlog Items

### Item 1: Corpus Validation Baseline [0.5 day]

**Type**: Testing
**Effort**: 0.5 day (spec 0h, design 0h, plan 0h, execute 4h)
**Dependencies**: None

**Objective**: Re-run the v2 pipeline (with Workstream A bug fixes) on all 12 corpus documents and record precise baseline metrics, so that Items 2-4 can measure improvement and regression.

**Current State**:
- ✅ Workstream A bug fixes shipped (A1-A4)
- ✅ Original 7-doc corpus has v2 results documented
- ✅ All 12 documents re-extracted post-bug-fix with baseline metrics recorded
- ✅ Baseline report delivered: `.project/reports/20260208_pdfv3-baseline.md`

**Scope**:
1. **Run extraction pipeline** on all 12 documents with `--index --force`
2. **Record per-document metrics**: INDEX section count, `##` header count, false positive headers (manual spot-check), false negative headers (manual spot-check), overall grade
3. **Write baseline report** with a table of results that Items 2-4 will reference

**Out of Scope**:
- Fixing any issues found (that's Items 2-4)
- GMFT or Layer 3 AI repair evaluation (focus is structural quality only)

**Success Criteria**:
- [x] All 12 documents extracted with current pipeline
- [x] Per-document metrics recorded in structured table
- [x] Baseline grades updated post-bug-fixes (may differ from strategy doc)
- [x] Report saved to `.project/reports/`

**Deliverables**:
- `.project/reports/20260208_pdfv3-baseline.md`

---

### Item 2: Claude Structure Module — Core Implementation [1.5 days]

**Type**: Implementation
**Effort**: 1.5 days (spec 1h, design 2h, plan 1h, execute 8h)
**Dependencies**: None (can parallel with Item 1; uses mocked tests)

**Objective**: Build `claude_structure.py` with style detection, chunked structure repair, and text-based anchoring — the core engine that replaces regex header promotion for non-trivial documents.

**Current State**:
- ✅ `ai_repair.py` exists with `render_page_image()`, `claude -p` invocation pattern, cross-validation infrastructure
- ✅ `postprocess.py` has header promotion regex (kept for fast-path)
- ✅ Page markers (`<!-- PAGE:N -->`) provide reliable page-to-content mapping
- ✅ `claude_structure.py` module implemented (684 lines, 50 tests)
- ✅ Style detection + structural repair + orchestrator complete

**Scope**:
1. **`DocumentStyle` dataclass**: `doc_type`, `heading_convention`, `has_toc`, `running_headers`, `page_number_format`
2. **`HeaderInsertion` dataclass**: `anchor_text` (not line number), `level`, `title`, `insert_position` (before/after)
3. **`detect_document_style()`**:
   - Render first 3 pages as thumbnails via `render_page_image()`
   - Send thumbnails + first ~200 lines of markdown to Claude (Haiku for cost efficiency)
   - Parse structured JSON response with validation
   - Cache result to `{output_dir}/style.json`
4. **`repair_structure()`**:
   - Chunk document into ~20-30 page windows using `<!-- PAGE:N -->` markers, with 2-3 page overlap
   - For each chunk: send markdown text + style context + 1-2 page images to Claude (Sonnet)
   - Claude returns `list[HeaderInsertion]` with text-based anchors
   - Validate response: reject insertions with unmatched anchor text, deduplicate, check level consistency
   - Merge insertions across chunks (overlap dedup)
5. **`apply_insertions()`**: Apply validated `HeaderInsertion` list to markdown text
6. **`needs_claude_structure()`**: Ratio-based heuristic — `headers_per_page < 0.1` or noise fraction > 0.3 or zero depth variance (all `##`, no `###`)
7. **Post-Phase-A running header strip**: After style detection returns `running_headers`, do targeted removal of any L1 missed
8. **Error handling**: Malformed JSON → retry once → fall back to regex-only with warning. Network timeout → same. Cache Phase A result so Phase B retry doesn't re-pay.

**Out of Scope**:
- Quality sweep / page-level sampling (deferred — see strategy review)
- Changes to `ai_repair.py` (stays as separate Layer 4)
- Changes to GMFT table extraction
- Documents over 200 pages (chunking handles up to ~200; longer docs noted as future work)

**Success Criteria**:
- [x] `detect_document_style()` returns valid `DocumentStyle` for mocked inputs covering all 5 doc types
- [x] `repair_structure()` returns `list[HeaderInsertion]` with text-anchored insertions
- [x] `apply_insertions()` correctly inserts headers at anchor positions
- [x] `needs_claude_structure()` returns True for 4/5 new corpus doc profiles, False for 5/7 original corpus profiles
- [x] Style detection result cached to disk; second call loads from cache
- [x] All Claude subprocess calls mocked in tests
- [x] Malformed JSON response → graceful fallback with warning (tested)
- [x] Chunking produces correct windows with overlap (unit tested)

**Deliverables**:
- `src/agentic_mbse/extraction/claude_structure.py` (684 lines)
- `tests/test_claude_structure.py` (637 lines, 50 tests)

---

### Item 3: Pipeline Integration + CLI Wiring [1 day]

**Type**: Integration
**Effort**: 1 day (spec 0.5h, design 1h, plan 0.5h, execute 5h)
**Dependencies**: Item 2

**Objective**: Wire `claude_structure.py` into the extraction pipeline as Layer 3, running after GMFT (Layer 2) and before AI repair (now Layer 4). Update CLI flags and ensure correct ordering.

**Current State**:
- ✅ `extract_cli.py` has `--enhance` flag that triggers `ai_repair.repair_document()`
- ✅ Quality gates detect table/equation problems → Layer 2 (GMFT) → Layer 3 (AI repair)
- ✅ `--index` flag runs after all enhancement
- ❌ No Claude structural pass in the pipeline
- ❌ `--enhance` only triggers table/equation repair, not structural repair

**Scope**:
1. **Pipeline ordering**:
   ```
   L1: pymupdf + postprocess (unchanged)
   L2: GMFT table enhancement (unchanged)
   L3: Claude structural pass (NEW — claude_structure.py)
     - needs_claude_structure() gate
     - detect_document_style() → cache
     - repair_structure() → apply_insertions()
     - Post-hoc running header strip
   L4: AI quality repair (EXISTING ai_repair.py, renumbered)
     - Runs on remaining RepairRequests from quality_gates
     - Cross-validation preserved
   Index generation: After all layers
   ```
2. **CLI changes**:
   - `--enhance` now triggers L3 (structural) AND L4 (quality repair)
   - `--fast` explicitly skips both L3 and L4 (regex-only + GMFT)
   - `--structure-only` flag: run L3 but skip L4 (useful for testing structural pass in isolation)
   - `--model` flag: override Claude model selection (default: haiku for Phase A, sonnet for Phase B)
3. **Ordering enforcement**: INDEX generation must happen after L3 completes. Add explicit check: if `--enhance` and `--index`, run index generation last.
4. **Cost reporting**: Before running L3, estimate and print cost: "Structural pass: ~$X.XX for N pages (Y chunks). Proceed? [Y/n]". Skip prompt with `--yes`.
5. **Logging**: Print what L3 did: "Style: paper (numbered_bold), Structure: 15 headers inserted, Running headers stripped: 2"

**Out of Scope**:
- Changes to `ai_repair.py` internals (just renumber its conceptual layer)
- Changes to `quality_gates.py`
- Changes to GMFT table extraction
- New CLI subcommands

**Success Criteria**:
- [ ] `--enhance` on a new-corpus document triggers style detection → structural repair → AI repair (in order)
- [ ] `--fast` produces identical output to current pipeline (no structural pass)
- [ ] `--structure-only` runs structural pass without AI repair
- [ ] `--index` always runs after structural pass (ordering enforced)
- [ ] Cost estimate printed before Claude calls; `--yes` skips prompt
- [ ] Mocked integration test: full pipeline with mocked Claude returns correct final markdown

**Deliverables**:
- Updated `src/agentic_mbse/cli/extract_cli.py`
- Updated `tests/test_extract_cli.py`

---

### Item 4: Corpus Benchmark + Ship [1 day]

**Type**: Testing
**Effort**: 1 day (spec 0h, design 0h, plan 0.5h, execute 7h)
**Dependencies**: Items 1, 2, 3

**Objective**: Run the full v3 pipeline on all 12 corpus documents in both `--fast` and `--enhance` modes, compare against the Item 1 baseline, document results, and verify the critical success factor.

**Current State**:
- ✅ (after Items 1-3) Full pipeline implemented and unit-tested with mocks
- ❌ No real-document validation
- ❌ No cost actuals

**Scope**:
1. **Run `--fast` mode** on all 12 documents:
   - Compare INDEX section counts and header accuracy against Item 1 baseline
   - Verify zero regressions on original 7-doc corpus
   - Record any improvements from Workstream A bug fixes (already in pipeline)
2. **Run `--enhance` mode** on all 12 documents:
   - Record: style detection result, headers inserted, headers correct/incorrect, INDEX section count
   - Record: wall clock time per document, actual API cost per document
   - Grade each document (same scale as strategy doc)
3. **Regression analysis**:
   - Any original-corpus document that degrades in `--enhance` mode → investigate and fix
   - Any new-corpus document below B- grade → investigate if prompt tuning would help
4. **Prompt tuning** (if needed):
   - Adjust style detection prompt or structure repair prompt based on failure patterns
   - Re-run affected documents
   - Maximum 2 tuning iterations (diminishing returns beyond that)
5. **Documentation**:
   - Results table with per-document grades in both modes
   - Cost actuals vs estimates from strategy doc
   - Known limitations
   - Updated `--help` text for new flags

**Out of Scope**:
- Quality sweep (Workstream C — deferred)
- Documents over 200 pages (noted as limitation)
- Performance optimization (chunking parallelization etc.)
- Updating the `/pdf-analysis` skill (separate follow-up)

**Success Criteria**:
- [ ] `--fast` mode: zero regressions on original 7-doc corpus (section counts equal or better)
- [ ] `--enhance` mode: at least 4/5 new corpus documents produce usable INDEX (critical success factor)
- [ ] `--enhance` mode: at least 3/5 new corpus documents grade B- or better
- [ ] `--enhance` mode: all 7 original corpus documents grade equal or better than v2
- [ ] Cost actuals within 2x of estimates ($1-4/doc acceptable, >$5/doc needs investigation)
- [ ] Results report published with per-document breakdown
- [ ] `--help` text updated for `--enhance`, `--fast`, `--structure-only`, `--model`, `--yes`
- [ ] Full test suite passes (existing + new)

**Deliverables**:
- `.project/reports/20260210_pdfv3-benchmark.md` — Full results
- Updated CLI help text
- Any prompt adjustments committed

---

## Dependencies

**External**:
- `claude` CLI available in PATH (for `--enhance` mode; `--fast` requires nothing new)
- `pymupdf` / `pymupdf4llm` (already required)
- Claude API access with Haiku and Sonnet models

**Internal**:
- Workstream A bug fixes (complete — merged on pdf-extract branch)
- Existing extraction pipeline (Layer 1, Layer 2, quality gates, ai_repair)

**Item Dependency Graph**:
```
Item 1: Corpus Baseline (no dependencies)
Item 2: Core Implementation (no dependencies; can parallel with Item 1)
  └─> Item 3: Pipeline Integration (depends on Item 2)
        └─> Item 4: Benchmark + Ship (depends on Items 1, 2, 3)
```

**Critical Path**: Item 2 → Item 3 → Item 4 (3.5 days). Item 1 runs in parallel with Item 2.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Claude returns malformed JSON or unanchored insertions | Medium | Medium | Validate all responses; retry once; fall back to regex-only with warning. Text-based anchoring is more robust than line numbers. |
| Full-document chunking produces inconsistent headers across chunk boundaries | Medium | Medium | 2-3 page overlap + chunk-boundary dedup. Style context shared across all chunks provides consistency. |
| Cost exceeds $5/doc for large documents | Low | Low | Cost estimate + confirmation before execution. `--max-repair-pages` budget cap. User has said cost is not a primary concern. |
| `needs_claude_structure()` misclassifies — skips Claude when needed or runs Claude unnecessarily | Medium | Low | Conservative threshold (escalate when uncertain). `--force-enhance` override. Wrong direction is "runs Claude unnecessarily" which costs money but doesn't degrade quality. |
| Prompt tuning required for each new document type (poor generalization) | Low | High | Two-phase approach (style detection → targeted structure prompt) provides document-type-specific context. If a new document type fails, the fix is prompt adjustment in one file, not architectural change. |
| Regression on original corpus in `--fast` mode | Very Low | High | No regex patterns removed from fast path — only Workstream A bug fixes applied, which are tightening (not loosening). Full regression test in Item 4. |
| Claude structural pass takes >60s per chunk, making 127-page docs take >10 min | Medium | Medium | Per-chunk timeout. Parallel chunk processing as future optimization. For v3 shipping, sequential is acceptable. |

---

## Architecture Reference

```
                ┌─────────────────────────────────────┐
                │          INPUT: PDF file             │
                └────────────────┬────────────────────┘
                                 │
                ┌────────────────▼────────────────────┐
                │  L1: Fast Extraction (simplified)    │
                │  pymupdf4llm + postprocess           │
                │  (regex header promotion preserved   │
                │   for --fast path)                   │
                │  Cost: $0   Time: ~2-5s              │
                └────────────────┬────────────────────┘
                                 │
                ┌────────────────▼────────────────────┐
                │  L2: GMFT Table Enhancement          │
                │  (unchanged)                         │
                │  Cost: $0   Time: ~1-2s/table        │
                └────────────────┬────────────────────┘
                                 │
              ┌──────────────────▼──────────────────────┐
              │  L3: Claude Structural Pass (NEW)       │
              │  claude_structure.py                     │
              │                                         │
              │  Gate: needs_claude_structure()          │
              │    ratio-based: headers/page < 0.1      │
              │    or noise fraction > 0.3              │
              │    or zero depth variance               │
              │                                         │
              │  Phase A: detect_document_style()        │
              │    3 page thumbnails + 200 lines → Haiku│
              │    → DocumentStyle (cached to disk)     │
              │                                         │
              │  Phase B: repair_structure()             │
              │    ~20-30 page chunks with overlap       │
              │    text + style + 1-2 images → Sonnet   │
              │    → list[HeaderInsertion]               │
              │    text-based anchoring (not line nums)  │
              │                                         │
              │  apply_insertions() + running hdr strip  │
              │  Cost: ~$0.30-1.00   Time: ~30-120s     │
              └──────────────────┬──────────────────────┘
                                 │
              ┌──────────────────▼──────────────────────┐
              │  L4: AI Quality Repair (EXISTING)       │
              │  ai_repair.py (unchanged)               │
              │  Tables + equations from quality_gates   │
              │  Cross-validation preserved              │
              │  Cost: ~$0.03-0.08/page                 │
              └──────────────────┬──────────────────────┘
                                 │
              ┌──────────────────▼──────────────────────┐
              │  INDEX Generation                       │
              │  Runs LAST, after all layers             │
              └─────────────────────────────────────────┘
```

---

## Design Decisions (from Strategy Review)

These decisions were agreed in the concept review and should be followed during implementation:

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | **Text-based anchoring**, not line numbers, for header insertions | Claude miscounts lines in long documents. Text snippets are robust to reformatting. |
| D2 | **Chunked processing** (~20-30 pages) instead of full-document single pass | Reduces context pressure, enables per-chunk validation, degrades gracefully. |
| D3 | **Workstream C (quality sweep) deferred** | Different problem from structural backbone. Existing quality_gates + ai_repair handles tables/equations. Ship structure first. |
| D4 | **Ratio-based fast-path heuristic** (headers/page, not absolute count) | Absolute threshold of 5 headers misses sparse documents. |
| D5 | **Return `list[HeaderInsertion]`**, not modified markdown, from Claude | Auditability — can log exactly what Claude changed. Safer than full rewrite. |
| D6 | **Keep `ai_repair.py` as separate Layer 4** | Clean abstraction boundaries. Structure and quality repair are different concerns. |
| D7 | **Haiku for Phase A, Sonnet for Phase B** | Phase A is classification (cheap). Phase B requires semantic understanding (needs quality). |
| D8 | **Cache Phase A result to disk** | If Phase B fails, retry doesn't re-pay for style detection. |

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-02-08
**Next Action**: Items 1-2 complete. Begin Item 3 (pipeline integration).

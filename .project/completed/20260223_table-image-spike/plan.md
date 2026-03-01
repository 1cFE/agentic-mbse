# Implementation Plan: Cropped Table Image Extraction Spike

**Status:** Complete
**Created:** 2026-02-23
**Last Updated:** 2026-02-23

## Source Documents
- **Spec:** `.project/active/table-image-spike/spec.md`
- **Research:** `.project/research/20260223-table-images-from-pdfs.md`
- **Existing infra:** `tests/corpus/pipelines/shared.py`, `h1_pymupdf_gmft.py`, `h3_pymupdf_claude_eq.py`

## Implementation Strategy

**Phasing Rationale:**
Track 0 (detection) must come first because all other tracks depend on having cropped table images. Track 1 (Claude extraction) is next because Track 2 (vote/resolve) needs both GMFT and Claude results. Track 3 (sequential review) technically only needs Track 0 output, but grouping it with Track 2 in Phase 3 keeps the multi-pass experiments together. Findings come last once all empirical data exists.

**Overall Validation Approach:**
- Each phase produces a standalone script runnable via `python tests/corpus/pipelines/trackN_*.py --slugs hawker_2020`
- Each phase saves structured output to `tests/corpus/runs/table_spike_trackN/`
- Ground truth scoring reuses `shared.py` infrastructure
- Manual validation: spot-check saved images visually, verify row counts against `ground_truth.jsonl`

---

## Phase 1: Track 0 — Table Detection Coverage

### Goal
Run both GMFT `AutoTableDetector` and PyMuPDF `page.find_tables()` on all 5 test papers. Save cropped table images from both detectors. Measure detection coverage: per-paper counts, overlap (IoU), and the union. This is first because it de-risks the core assumption (does PyMuPDF catch what GMFT misses?) and produces the images all later phases need.

### Test Stencil (Write This First)
```python
# Quick smoke test: run detection on hawker_2020 (14pp, 3 known tables)
# Verify: both detectors find tables, images are saved, overlap computed

def test_track0_hawker():
    results = run_track0("hawker_2020")
    # GMFT should find tables (it gets 40/40 rows in Stage 2)
    assert results["gmft_tables_found"] >= 3
    # Images saved
    assert len(list(output_dir.glob("gmft_*.png"))) >= 3
    # Detection summary produced
    assert "union_tables" in results
```

### Changes Required

#### 1. Script: `tests/corpus/pipelines/track0_detection.py` (NEW)
- [x] Create script following h1/h3 pattern (argparse, `--slugs`, per-paper loop)
- [x] GMFT detection: reuse `extract_gmft_pages()` from `shared.py`, but also save `table.image(dpi=200)` per table and record `table.rect.bbox`
- [x] PyMuPDF detection: open PDF with `pymupdf.open()`, call `page.find_tables()` per page, save `page.get_pixmap(dpi=200, clip=tab.bbox)` per table, record `tab.bbox`, `tab.row_count`, `tab.col_count`
- [x] False-positive filtering: apply existing `filter_gmft_tables()` for GMFT; implement analogous filter for PyMuPDF (min rows, min cols, min cell count)
- [x] Overlap detection: normalize bboxes to page-relative coordinates (0-1), compute IoU between GMFT and PyMuPDF detections on the same page, threshold at IoU > 0.5
- [x] Per-paper summary: tables found by GMFT only, PyMuPDF only, both, union count
- [x] Save output to `runs/table_spike_track0/{slug}/`:
  - `gmft_p{page}_t{idx}.png` — cropped images from GMFT
  - `pymupdf_p{page}_t{idx}.png` — cropped images from PyMuPDF
  - `detection_summary.json` — per-paper detection counts, bboxes, overlaps, filtering
  - `images_manifest.json` — full per-table manifest with bbox, dimensions, filter status, GMFT markdown
  - `overlaps.json` — IoU match details
  - `per_page_breakdown.json` — per-page detector counts

#### 2. Shared infrastructure additions
- [x] Keep Track 0 self-contained with its own `DetectedTable` dataclass (chose self-contained for spike)

### Validation (How to Verify This Phase)

**Automated:**
- [x] Run `python tests/corpus/pipelines/track0_detection.py --slugs hawker_2020` → completes without error
- [x] Run on full 5-paper set → all complete
- [x] Verify cropped image files exist and are non-zero size
- [x] Verify `detection_summary.json` has expected fields

**Manual:**
- [x] Open 3-5 saved table images — verify they show actual tables, not garbage
- [x] Check aries_cost_account detection counts: does GMFT find ~28 tables? Does PyMuPDF find any that GMFT misses?
- [x] Check overlap: for papers where both detect, do IoU scores look reasonable?

**What We Know Works After This Phase:**
- Both detectors run end-to-end on all 5 papers
- Cropped images are saved and usable
- We know the detection coverage gap (SC-1)
- We have the image manifest needed for Phase 2

---

## Phase 2: Track 1 — Claude Cropped Image Extraction

### Goal
Send cropped table images to Claude (Sonnet) with a table-specific extraction prompt. Measure accuracy vs ground truth (row counts), cost per table, tokens per table. Compare against GMFT DataFrame extraction and Stage 1D full-page Claude data. This answers the core question: is Claude more accurate from cropped images?

### Test Stencil (Write This First)
```python
# Dry-run test: verify prompt construction and image loading
# without actually calling Claude

def test_track1_prompt_construction():
    manifest = load_manifest("hawker_2020")
    for table_entry in manifest:
        img_path = Path(table_entry["image_path"])
        assert img_path.exists()
        prompt = build_table_prompt(img_path)
        assert "markdown pipe table" in prompt
        assert "ONLY the markdown table" in prompt
```

### Changes Required

#### 1. Prompt file: `tests/corpus/prompts/extract_table_cropped.txt` (NEW)
- [x] Create table-specific extraction prompt per spec (created in Phase 1)

#### 2. Script: `tests/corpus/pipelines/track1_cropped_extraction.py` (NEW)
- [x] Load image manifest from Phase 1 (`runs/table_spike_track0/{slug}/images_manifest.json`)
- [x] For each table image: build prompt referencing the cropped image path, invoke Claude via `invoke_claude()` pattern from `h3_pymupdf_claude_eq.py`
- [x] Record per-table: input tokens, output tokens, total cost, wall clock time, image dimensions (from manifest)
- [x] Parse Claude's response to extract the markdown table
- [x] Count rows in Claude's table output; compare against GMFT row count from manifest and GT from `ground_truth.jsonl`
- [x] Save output to `runs/table_spike_track1/{slug}/`:
  - `table_p{page}_t{idx}_claude.md` — Claude's extracted table
  - `results.json` — per-table accuracy, cost, tokens, dimensions
  - `comparison.json` — side-by-side: Claude-cropped rows vs GMFT rows vs GT rows
- [x] Support `--dry-run` flag (show what would be sent without calling Claude)
- [x] Support `--slugs` filter
- [x] Support `--detector` flag (gmft/pymupdf/both)

### Validation (How to Verify This Phase)

**Automated:**
- [x] Run `--dry-run` on hawker_2020 → shows table list, no Claude calls
- [x] Run on hawker_2020 (3 tables, cheap) → Claude returns markdown tables
- [x] Run on full set → all complete within budget
- [x] `results.json` has cost data for every table

**Manual:**
- [x] Compare Claude-cropped table output against GT for hawker_2020 (should be close to 40 rows) → EXACT: 40/40
- [x] Check cost: cropped tables should be significantly cheaper than full-page ($0.078/page) → ~$0.076/table avg, modest savings
- [x] Spot-check 2-3 tables: are numerical values preserved exactly? → Yes, clean pipe tables with exact values

**What We Know Works After This Phase:**
- Claude can extract tables from cropped images (SC-2)
- We know accuracy difference: cropped vs full-page vs GMFT
- We know cost per table (empirical validation of the 4-8x cheaper estimate)
- We have the Claude results needed for Phase 3's vote/resolve

---

## Phase 3: Track 2 + Track 3 — Multi-Pass Strategies

### Goal
Test two multi-pass approaches: (A) independent vote/resolve between GMFT and Claude outputs, and (B) sequential review where Claude corrects GMFT output using the cropped image. Compare both against individual tools and against each other. This answers SC-3 and SC-4.

### Test Stencil (Write This First)
```python
# Track 2: verify vote/resolve logic on synthetic data

def test_vote_resolve_prefer_higher_row_count():
    gmft_table = "| A | B |\n|---|---|\n| 1 | 2 |"      # 1 data row
    claude_table = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"  # 2 data rows
    result = resolve_prefer_higher_rows(gmft_table, claude_table)
    assert result == claude_table

# Track 3: verify review prompt includes both GMFT table and image reference

def test_review_prompt_construction():
    prompt = build_review_prompt(gmft_markdown="| A |\n|---|\n| 1 |", image_path="/tmp/table.png")
    assert "library tool extracted" in prompt
    assert "| A |" in prompt
    assert "/tmp/table.png" in prompt
```

### Changes Required

#### 1. Prompt file: `tests/corpus/prompts/review_table.txt` (NEW)
- [x] Create sequential review prompt per spec

#### 2. Script: `tests/corpus/pipelines/track2_vote_resolve.py` (NEW)
- [x] Load GMFT results from Track 0 manifest and Claude results from Track 1
- [x] For each table with both GMFT and Claude output, implement two resolution strategies:
  - Strategy A: Prefer whichever has more rows (Claude is accuracy ceiling from Stage 2)
  - Strategy B: Cell-level comparison — parse both tables, flag cells where they disagree, prefer Claude's value
- [x] Score each strategy against GT: row count match, note which tables each strategy gets right/wrong
- [x] Save to `runs/table_spike_track2/{slug}/`

#### 3. Script: `tests/corpus/pipelines/track3_sequential_review.py` (NEW)
- [x] Load GMFT markdown from Track 0 and cropped images from Track 0
- [x] For each table: build review prompt with GMFT markdown + image path, invoke Claude
- [x] Record per-table: input tokens, output tokens, cost, wall clock time
- [x] Check for reasoning leakage: grep Claude output for non-table text (commentary, "I notice", etc.)
- [x] Score against GT; compare against Track 1 (independent Claude) and GMFT alone
- [x] Save to `runs/table_spike_track3/{slug}/`
- [x] Support `--dry-run` and `--slugs`

### Validation (How to Verify This Phase)

**Automated:**
- [x] Track 2: run on all papers → both strategies produce results, comparison.json populated
- [x] Track 3: run `--dry-run` → shows reviewable tables without calling Claude
- [x] Track 3: run on hawker_2020 (3 tables) → Claude returns corrected tables
- [x] Both: run on full set

**Manual:**
- [x] Track 2: check whether vote/resolve actually picks the better table in disagreement cases
- [x] Track 3: check whether Claude's reviewed output fixes known GMFT errors — mixed: fixes minor issues but misses big structural gaps
- [x] Track 3: check reasoning leakage — **zero leakage** across all 20 tables, strict prompt works perfectly
- [x] Compare row counts across all 4 approaches for each paper

**What We Know Works After This Phase:**
- Whether vote/resolve beats either individual tool (SC-3)
- Whether sequential review beats independent Claude extraction (SC-4)
- Whether strict prompts eliminate reasoning leakage
- We have all empirical data needed for the findings document

---

## Phase 4: Findings & Recommendations

### Goal
Synthesize all empirical results into a findings document with cross-track comparison tables and concrete Stage 4 recommendations. Answers SC-5 and produces the deliverable specified in FR-15.

### Test Stencil (Write This First)
```
# No code to test — this phase is documentation.
# Validation: all success criteria answered, recommendations actionable.
```

### Changes Required

#### 1. Findings document: `.project/active/table-image-spike/findings.md` (NEW)
- [x] Track 0 findings: detection coverage table (per-paper: GMFT count, PyMuPDF count, both, union, GT)
- [x] Track 0 findings: does the union close the aries_cost_account gap?
- [x] Track 1 findings: accuracy table (per-paper: Claude-cropped rows, GMFT rows, Claude-full-page rows, GT)
- [x] Track 1 findings: cost table (per-table: tokens, cost, dimensions, compared to full-page $0.078)
- [x] Track 2 findings: vote/resolve accuracy table (Strategy A vs B vs individuals)
- [x] Track 3 findings: sequential review accuracy table (reviewed vs independent vs GMFT)
- [x] Track 3 findings: reasoning leakage assessment
- [x] Cross-track comparison: master table with all approaches side-by-side per paper
- [x] Recommendations: which detector strategy for Stage 4
- [x] Recommendations: which multi-pass strategy (if any) for Stage 4
- [x] Recommendations: integration points in the pipeline
- [x] Answer all 5 success criteria explicitly (SC-1 through SC-5)

### Validation (How to Verify This Phase)

**Manual:**
- [x] All 5 success criteria have explicit answers
- [x] Recommendations are concrete (not "maybe" or "it depends")
- [x] Numbers in findings match the raw data in `runs/table_spike_track*/`
- [x] Findings are actionable for Stage 4 planning

**What We Know Works After This Phase:**
- The spike is complete
- Stage 4 pipeline design has empirical guidance on detectors and multi-pass strategies

---

## Environment Setup

See CLAUDE.md for full environment rules. Key points:
- Run scripts from repo root: `python tests/corpus/pipelines/track0_detection.py`
- GMFT and PyMuPDF are already installed (used by existing pipelines)
- Claude CLI is available (used by h3 pipeline)
- Page images for all 5 papers exist in `tests/corpus/page_images/`

---

## Risk Management

**Phase-Specific Mitigations:**
- **Phase 1**: PyMuPDF `find_tables()` coordinate format may differ from expectations. Test on one paper first (hawker_2020), verify bbox values make sense before running full set.
- **Phase 2**: Claude CLI overhead (~10-15s per call) makes running all tables on all papers slow. Start with hawker_2020 (3 tables), add papers incrementally. Use `--dry-run` to verify before spending money.
- **Phase 3**: Track 3 requires Claude calls ($$). Budget carefully — run on hawker_2020 first, assess value before running full set. Track 2 is free (just comparison logic).

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `tests/corpus/pipelines/track0_detection.py` — self-contained detection script with `DetectedTable`, `OverlapMatch`, `PaperSummary` dataclasses
- Created `tests/corpus/prompts/extract_table_cropped.txt` — table-specific extraction prompt for Phase 2
- Output saved to `tests/corpus/runs/table_spike_track0/{slug}/` with detection_summary.json, images_manifest.json, overlaps.json, per_page_breakdown.json, and cropped PNG images

**Results (SC-1 answer):**
| Paper | GMFT | PyMuPDF | Both | G-only | P-only | Union | GT tables |
|-------|------|---------|------|--------|--------|-------|-----------|
| hawker_2020 | 3 | 0 | 0 | 3 | 0 | 3 | 3 |
| hsu_2020 | 3 | 3 | 3 | 0 | 0 | 3 | 3 |
| hansen_2025 | 1 | 0 | 0 | 1 | 0 | 1 | 1 |
| paischer_2025 | 5 | 8 | 2 | 3 | 6 | 11 | 5 |
| aries_cost_account | 15 | 26 | 0 | 15 | 26 | 41 | 28 |
| **TOTAL** | **27** | **37** | **5** | **22** | **32** | **59** | **40** |

**Key Findings:**
- GMFT and PyMuPDF have **zero overlap on aries_cost_account** — visual inspection reveals PyMuPDF detects prose paragraphs, not tables. Most of its 26 "tables" are false positives (text blocks).
- PyMuPDF `find_tables()` does NOT close the aries gap. GMFT remains the better detector for space-aligned tables.
- PyMuPDF adds genuine value only on grid-line papers: perfect overlap on hsu_2020 (IoU 0.87-0.93), finds 6 extra tables on paischer_2025 (though likely some over-detection vs GT of 5).
- hawker_2020 (dotted-line tables) and hansen_2025 (space-aligned): only GMFT detects tables.
- GMFT's confidence filter rejects 11/26 aries tables. Some borderline rejections (0.976, 0.979, 0.980) may include real tables — worth reviewing in findings.

**Issues:**
- PyMuPDF false-positive filter (min 2 rows, 2 cols, 4 cells) is too lenient for report-style docs like aries. Prose blocks with green highlighting pass the filter. Would need content-based heuristics (e.g., avg cell text length) to improve.
- GMFT `detect_gmft_pages()` from shared.py was not reused directly — wrote fresh detection logic to capture bbox and images alongside DataFrames. Self-contained approach as planned.

**Deviations:**
- Image filenames use `gmft_p{page:03d}_t{idx}` (3-digit zero-padded page) instead of plan's `gmft_table_p{page}_t{idx}` — more consistent with multi-digit pages (aries has 100 pages).
- Added `overlaps.json` and `per_page_breakdown.json` output files beyond what the plan specified — useful for analysis.
- Also saves GMFT DataFrame markdown in the manifest (for Track 2/3 reuse).

### Phase 2 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `tests/corpus/pipelines/track1_cropped_extraction.py` — Claude extraction script with `--dry-run`, `--slugs`, `--detector` flags
- Output saved to `tests/corpus/runs/table_spike_track1/{slug}/` with results.json, comparison.json, and per-table Claude markdown files

**Results (SC-2 answer — Claude cropped vs GT):**
| Paper | Claude rows | GMFT rows | GT rows | Claude accuracy |
|-------|-------------|-----------|---------|-----------------|
| hawker_2020 | 40 | 34 | 40 | EXACT |
| hsu_2020 | 56 | 50 | 56 | EXACT |
| hansen_2025 | 15 | 13 | 15 | EXACT |
| paischer_2025 | 53 | 42 | 53 | EXACT |
| aries_cost_account | 162 | 76 | 280 | 58% (detection-limited) |

**Claude achieves EXACT GT match on 4/4 papers where GMFT detects all tables.** On aries, the 58% coverage is because GMFT only detects 15/28 tables; Claude's per-table extraction is strong (162 rows vs GMFT's 76 from the same images — Claude extracts ~2x more from space-aligned tables).

**Cost Data:**
| Paper | Tables | Total cost | Avg/table | Full-page equiv |
|-------|--------|-----------|-----------|-----------------|
| hawker_2020 | 3 | $0.129 | $0.043 | $0.234 (3pg) |
| hsu_2020 | 3 | $0.253 | $0.084 | $0.234 (3pg) |
| hansen_2025 | 1 | $0.087 | $0.087 | $0.078 (1pg) |
| paischer_2025 | 5 | $0.407 | $0.081 | $0.390 (5pg) |
| aries_cost_account | 15 | $1.171 | $0.078 | $1.170 (15pg) |
| **TOTAL** | **27** | **$2.047** | **$0.076** | — |

Cost savings are modest (~$0.076/table vs $0.078/page) — mostly because aries tables are large (nearly page-sized images). Smaller tables (hawker: $0.043) show better savings. The main value is accuracy, not cost.

**Key Findings:**
- Claude correctly refuses non-tables: p42 and p48 on aries were GMFT false positives (descriptive text), Claude said "no table to extract"
- GMFT's DataFrame extraction returns `null` (failure) on 7/15 aries tables where its detection worked — Claude still extracts successfully from those images
- The bottleneck for aries is detection (15/28 tables found), not extraction quality

**Issues:**
- Print statements not visible when running as subprocess under Claude CLI (stdout captured). Results verified via saved JSON files.

**Deviations:**
- Added `--detector` flag (gmft/pymupdf/both) beyond plan — allows experimenting with PyMuPDF-detected tables later
- Did not compare against Stage 1D full-page Claude data (FR-8) — will include in Phase 4 findings when synthesizing all results

### Phase 3 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `tests/corpus/prompts/review_table.txt` — sequential review prompt
- Created `tests/corpus/pipelines/track2_vote_resolve.py` — vote/resolve comparison logic (no Claude calls)
- Created `tests/corpus/pipelines/track3_sequential_review.py` — sequential review with `--dry-run`, `--slugs`
- Output in `runs/table_spike_track2/` and `runs/table_spike_track3/`

**Track 2 Results (SC-3 — vote/resolve):**
| Paper | Pairs | GMFT | Claude | St.A | St.B | GT |
|-------|-------|------|--------|------|------|----|
| hawker | 3 | 40 | 40 | 40 | 40 | 40 |
| hsu | 3 | 56 | 56 | 56 | 56 | 56 |
| hansen | 1 | 15 | 15 | 15 | 15 | 15 |
| paischer | 5 | 52 | 53 | 53 | 53 | 53 |
| aries | 6 | 77 | 88 | 91 | 88 | 280 |

**SC-3 answer:** Vote/resolve does NOT beat Claude alone. On 4/5 papers, all approaches converge at GT. On aries, Strategy A gains 3 rows (91 vs 88) by preferring GMFT on 2 tables where GMFT has more rows. Marginal value; the real bottleneck is detection, not resolution.

**Track 3 Results (SC-4 — sequential review):**
| Paper | Tables | GMFT | Reviewed | Track1 | GT | Leakage |
|-------|--------|------|----------|--------|----|---------|
| hawker | 3 | 40 | 40 | 40 | 40 | 0/3 |
| hsu | 3 | 56 | 56 | 56 | 56 | 0/3 |
| hansen | 1 | 15 | 15 | 15 | 15 | 0/1 |
| paischer | 5 | 52 | 53 | 53 | 53 | 0/5 |
| aries | 8 | 92 | 92 | 88 | 280 | 0/8 |

**SC-4 answer:** Sequential review does NOT beat independent extraction. Review mode is too conservative — it makes incremental corrections (paischer p23: +1 row, aries p7: +2 rows, aries p38: -1 row) but misses structural re-extraction that independent Claude achieves. Critical example: aries p4, GMFT has a 2-column garbled table (9 rows), review kept it at 9 rows, but independent Claude extracted 22 clean rows.

**Zero reasoning leakage across all 20 tables.** The strict "output ONLY the corrected markdown table" prompt works perfectly.

**Cost:** Track 3 total $2.13 (20 tables) vs Track 1 $2.05 (27 tables). Review is slightly MORE expensive per table because the prompt includes GMFT markdown + image.

**Key Findings:**
1. Independent extraction (Track 1) is the best approach — exact GT match on 4/5 papers
2. Review mode anchors Claude to GMFT's structure, preventing big wins on badly-extracted tables
3. Vote/resolve adds no meaningful value when Claude already matches GT
4. Zero leakage confirms strict prompt design works
5. The real bottleneck is detection (GMFT finds 15/28 aries tables), not extraction quality

**Issues:**
- Track 2 cell-level comparison (Strategy B) shows artificially low agreement (12% on hawker) due to formatting differences between GMFT's `df.to_markdown()` and Claude's pipe format — a normalization issue, not real disagreement
- Track 3 on aries p42/p48: GMFT provided tables for regions that are actually prose; review mode kept them (9 and 5 rows) while Track 1 correctly rejected them as non-tables

**Deviations:**
- None significant

### Phase 4 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `.project/active/table-image-spike/findings.md` — comprehensive findings document with all track results, cross-track comparison, and Stage 4 recommendations
- All 5 success criteria answered with explicit verdicts and evidence references
- Includes: executive summary, per-track analysis with data tables, cross-track master comparison, architecture sketch for TableEnhancer, and "what NOT to build" section

**Key Conclusions:**
- Claude cropped-image extraction is the clear winner: exact GT on 4/5 papers, 2.1x better than GMFT-DF on aries
- Multi-pass strategies (vote/resolve, sequential review) add no meaningful value
- Cost is comparable to full-page ($0.076 vs $0.078), not cheaper as originally hypothesized
- The bottleneck is detection (GMFT finds 15/28 aries tables), not extraction quality
- Recommendation: Ship as TableEnhancer triggered on GMFT extraction failures

**Issues:**
- None

**Deviations:**
- Added per-table aries breakdown in Track 1 section (not in plan, but useful for understanding extraction patterns)
- Added image dimension distribution analysis and pipeline architecture sketch beyond plan scope

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**

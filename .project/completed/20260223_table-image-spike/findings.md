# Findings: Cropped Table Image Extraction Spike

**Date:** 2026-02-23
**Status:** Complete
**Branch:** `doc-ingest-clean`

---

## Executive Summary

This spike tested whether cropped table images improve table extraction quality in the doc-extraction pipeline. Four tracks were run across 5 test papers (40 ground truth tables, ~444 GT rows).

**Key findings:**

1. **Claude + cropped images achieves exact GT match on 4/5 papers** (hawker, hsu, hansen, paischer). This is the best extraction quality observed in any stage.
2. **The bottleneck is detection, not extraction.** On aries_cost_account, GMFT detects only 15/28 tables. Claude extracts 162 rows from those 15 images — 2.1x more than GMFT's DataFrame extraction (76 rows) from the same detections — but still only 58% of GT because 13 tables were never detected.
3. **Multi-pass strategies add no meaningful value.** Vote/resolve (Track 2) and sequential review (Track 3) converge with independent Claude extraction on all non-aries papers. On aries, they are slightly worse because review mode anchors Claude to GMFT's broken structure.
4. **PyMuPDF `find_tables()` does not complement GMFT.** Zero detection overlap on aries (the gap paper). PyMuPDF's "tables" on aries are prose paragraphs, not tables.
5. **Cost is comparable to full-page, not cheaper.** Average $0.076/table vs $0.078/page — aries tables are nearly page-sized. The value is accuracy, not savings.

**Stage 4 recommendation:** Ship Claude cropped-image extraction as a `TableEnhancer` protocol, triggered when GMFT detects a table but its DataFrame extraction fails or looks suspect. Do not invest in multi-pass strategies or PyMuPDF detection. The highest-value next work is improving detection coverage on space-aligned tables.

---

## Track 0: Table Detection Coverage (SC-1)

### Method

Both GMFT `AutoTableDetector` and PyMuPDF `page.find_tables()` were run on all 5 papers. Cropped images were saved from both detectors. False-positive filtering was applied (GMFT: confidence < 0.98 or avg cell length > 80; PyMuPDF: min 2 rows, 2 cols, 4 cells). Overlap computed via IoU > 0.5 on page-normalized bounding boxes.

### Detection Coverage Results

| Paper | GMFT raw | GMFT filtered | PyMuPDF raw | PyMuPDF filtered | Overlap | G-only | P-only | Union | GT |
|-------|----------|---------------|-------------|------------------|---------|--------|--------|-------|----|
| hawker_2020 | 3 | 3 | 0 | 0 | 0 | 3 | 0 | 3 | 3 |
| hsu_2020 | 6 | 3 | 3 | 3 | 3 | 0 | 0 | 3 | 3 |
| hansen_2025 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 1 |
| paischer_2025 | 5 | 5 | 32 | 8 | 2 | 3 | 6 | 11 | 5 |
| aries_cost_account | 26 | 15 | 35 | 26 | 0 | 15 | 26 | 41 | 28 |
| **TOTAL** | **42** | **27** | **70** | **37** | **5** | **22** | **32** | **59** | **40** |

### Key Observations

**GMFT is the better detector overall.** On papers with dotted-line tables (hawker) and space-aligned tables (hansen), only GMFT detects tables. PyMuPDF `find_tables()` finds nothing on either paper.

**PyMuPDF does NOT close the aries gap.** This was the central question for Track 0. Despite finding 26 "tables" after filtering (35 raw), visual inspection reveals PyMuPDF is detecting prose paragraphs with green highlighting, not actual tables. The zero overlap with GMFT on aries confirms these are entirely different regions. PyMuPDF's heuristic detection (line/text analysis) is fooled by the formatting of aries_cost_account.

**PyMuPDF adds value only on grid-line papers.** On hsu_2020, perfect overlap with GMFT (IoU 0.87-0.93 across all 3 tables). On paischer_2025, it finds 6 additional "tables" beyond GMFT's 5, but GT is only 5 — so these are likely over-detections.

**GMFT's confidence filter is aggressive on aries.** 11/26 raw detections rejected (42%). Some borderline rejections (confidence 0.976-0.980) may include real tables. Lowering the threshold to 0.95 would recover ~3 more tables, but risks more false positives.

**SC-1 Answer:** GMFT detects 27/40 GT tables after filtering. PyMuPDF detects 37 "tables" but most are false positives on report-style docs. Their union (59) exceeds GT (40) due to over-detection, not complementary coverage. On aries specifically, GMFT finds 15/28 tables and PyMuPDF finds 0 real tables. The detection gap remains open.

---

## Track 1: Cropped Image Extraction (SC-2)

### Method

Cropped table images from Track 0 (GMFT-detected, filtered) were sent to Claude Sonnet with a table-specific extraction prompt ("Extract this table as a markdown pipe table... Output ONLY the markdown table, no commentary"). Per-table metrics recorded: row count, input/output tokens, cost, wall clock time, image dimensions.

### Accuracy Results

| Paper | Tables | Claude rows | GMFT-DF rows | GT rows | Claude vs GT |
|-------|--------|-------------|--------------|---------|-------------|
| hawker_2020 | 3 | 40 | 34 | 40 | **EXACT** |
| hsu_2020 | 3 | 56 | 50 | 56 | **EXACT** |
| hansen_2025 | 1 | 15 | 13 | 15 | **EXACT** |
| paischer_2025 | 5 | 53 | 42 | 53 | **EXACT** |
| aries_cost_account | 15 | 162 | 76 | 280 | 58% (detection-limited) |
| **TOTAL** | **27** | **326** | **215** | **444** | **73%** |

*Claude rows = pipe table rows (header + separator + data). GMFT-DF rows = DataFrame data rows only. GT rows = expected pipe table rows from ground_truth.jsonl.*

### Per-Table Accuracy on aries_cost_account

| Page | Claude rows | GMFT-DF rows | Image size | Notes |
|------|-------------|-------------|------------|-------|
| p4 | 22 | 7 | 1172x818 | Claude extracts 3.1x more rows from space-aligned table |
| p7 | 19 | 16 | 1059x751 | Claude finds 3 extra rows |
| p12 | 9 | null | 1003x282 | GMFT detection OK, DataFrame extraction failed; Claude succeeds |
| p30 | 11 | 9 | 1049x460 | |
| p34 | 19 | 19 | 1236x595 | Same extraction quality |
| p38 | 6 | 5 | 942x287 | |
| p42 | **0** | 7 | 1289x1580 | Claude correctly rejects — not a table (GMFT false positive) |
| p48 | **0** | 4 | 1290x571 | Claude correctly rejects — not a table (GMFT false positive) |
| p51 | 11 | null | 1257x403 | GMFT detection OK, DataFrame failed; Claude succeeds |
| p66 | 14 | null | 1046x482 | GMFT detection OK, DataFrame failed; Claude succeeds |
| p69 | 12 | null | 583x459 | GMFT detection OK, DataFrame failed; Claude succeeds |
| p72 | 7 | null | 1057x230 | GMFT detection OK, DataFrame failed; Claude succeeds |
| p74 | 12 | null | 639x407 | GMFT detection OK, DataFrame failed; Claude succeeds |
| p83 | 9 | null | 1257x246 | GMFT detection OK, DataFrame failed; Claude succeeds |
| p87 | 11 | 9 | 1052x292 | |

Two critical patterns:
1. **GMFT detects but can't extract (7/15 tables):** DataFrame extraction returns null, but the detection bounding box is correct. Claude successfully extracts from these images. This is the highest-value use case for cropped image extraction.
2. **Claude as false-positive filter (2/15 tables):** p42 and p48 are GMFT false positives (descriptive text, not tables). Claude correctly identifies these as non-tables and refuses to extract. This is a free quality improvement.

### Cost Results

| Paper | Tables | Total cost | Avg/table | Full-page equiv | Savings |
|-------|--------|-----------|-----------|-----------------|---------|
| hawker_2020 | 3 | $0.129 | $0.043 | $0.234 (3 pages) | 45% |
| hsu_2020 | 3 | $0.253 | $0.084 | $0.234 (3 pages) | -8% |
| hansen_2025 | 1 | $0.087 | $0.087 | $0.078 (1 page) | -12% |
| paischer_2025 | 5 | $0.407 | $0.081 | $0.390 (5 pages) | -4% |
| aries_cost_account | 15 | $1.172 | $0.078 | $1.170 (15 pages) | 0% |
| **TOTAL** | **27** | **$2.047** | **$0.076** | — | — |

*Full-page equiv = number of table-containing pages x $0.078/page (Stage 1D rate).*

**Cost savings are modest and inconsistent.** The research estimate of 4-8x cheaper assumed small table crops. In practice:
- Small tables (hawker, avg 300K px) save ~45%
- Large tables spanning most of a page (aries, avg 600K px) save nothing
- Multi-column journal tables (hsu, paischer, hansen) are often wider than half the page, giving no savings

The average cost of $0.076/table is essentially the same as $0.078/page. **The value of cropped images is accuracy, not cost reduction.**

### Image Dimension Distribution

| Category | Dimensions | % of full page | Avg cost |
|----------|-----------|----------------|----------|
| Small (< 200K px) | 948x115, 646x302 | 3-5% | ~$0.074 |
| Medium (200K-500K) | 672x634, 1003x282, 942x287 | 5-13% | ~$0.076 |
| Large (500K-1M) | 1046x633, 1236x595, 1059x751 | 13-26% | ~$0.082 |
| Very large (> 1M) | 1210x1733, 1289x1580 | 27-54% | ~$0.090 |

*Full page at 200 DPI ~= 1654x2339 = 3.87M pixels.*

### SC-2 Answer

**Yes, Claude extracts tables more accurately from cropped images.** Exact GT match on 4/5 papers. On aries, Claude gets 162 rows vs GMFT-DF's 76 from the same detected images (2.1x improvement). Claude also successfully extracts from 7 tables where GMFT's DataFrame extraction completely fails. The accuracy improvement is definitive; the cost improvement is negligible.

Compared to Claude full-page extraction (Stage 1D data: 40/40 hawker, 56/56 hsu, 15/15 hansen, 55/53 paischer), cropped-image extraction matches on hawker/hsu/hansen and is slightly tighter on paischer (53 vs 55 — full-page over-extracted by 2 rows). Cropped images give Claude less opportunity to hallucinate extra content.

---

## Track 2: Vote/Resolve Multi-Pass (SC-3)

### Method

For tables where both GMFT DataFrame and Claude cropped-image extraction produced output, two resolution strategies were tested:
- **Strategy A (prefer higher row count):** Pick whichever output has more rows. Tiebreak: prefer Claude.
- **Strategy B (cell-level comparison):** Parse both tables, compare cells. When they disagree, prefer Claude's value.

### Results

| Paper | Pairs | GMFT rows | Claude rows | Strategy A | Strategy B | GT |
|-------|-------|-----------|-------------|------------|------------|-----|
| hawker_2020 | 3 | 40 | 40 | 40 | 40 | 40 |
| hsu_2020 | 3 | 56 | 56 | 56 | 56 | 56 |
| hansen_2025 | 1 | 15 | 15 | 15 | 15 | 15 |
| paischer_2025 | 5 | 52 | 53 | 53 | 53 | 53 |
| aries_cost_account | 6 | 77 | 88 | 91 | 88 | 280 |

*Pairs = tables where both GMFT and Claude produced output. Aries has 6 pairs (not 15) because GMFT DataFrame extraction fails on 7/15 tables and Claude rejects 2 false positives.*

*Row counts here use pipe-row counting (header + separator + data) for direct GT comparison.*

### Analysis

**On 4/5 papers, all approaches produce identical results.** When both tools detect and extract the same tables, there's nothing to resolve — Claude already matches GT.

**On aries, Strategy A gains 3 rows over Claude alone** (91 vs 88) by choosing GMFT's output on 2 tables where GMFT has more rows (p34: 21 vs 19, p38: 7 vs 6). Strategy B stays at 88 because it always prefers Claude's cell values.

**Cell-level agreement is artificially low** due to formatting differences between GMFT's `df.to_markdown()` output and Claude's pipe table format. hawker shows only 12% cell agreement despite identical row counts — this is a normalization artifact, not real disagreement.

### SC-3 Answer

**No, vote/resolve does not produce measurably better accuracy than Claude alone.** The maximum gain is 3 rows on aries (from 88 to 91 out of 280 GT). This is a 1.1% improvement in absolute terms, far smaller than the 118-row detection gap. Multi-pass resolution is not worth the implementation complexity given that the two tools agree on nearly everything when they both have good detections.

---

## Track 3: Sequential Review Multi-Pass (SC-4)

### Method

Claude received both the GMFT markdown table AND the cropped table image with a review prompt: "A library tool extracted the following table from this image. Review the extracted table against the image. Correct any errors... Output ONLY the corrected markdown table, no commentary."

### Results

| Paper | Tables | GMFT rows | Reviewed rows | Track 1 (independent) | GT | Leakage |
|-------|--------|-----------|---------------|----------------------|-----|---------|
| hawker_2020 | 3 | 40 | 40 | 40 | 40 | 0/3 |
| hsu_2020 | 3 | 56 | 56 | 56 | 56 | 0/3 |
| hansen_2025 | 1 | 15 | 15 | 15 | 15 | 0/1 |
| paischer_2025 | 5 | 52 | 53 | 53 | 53 | 0/5 |
| aries_cost_account | 8 | 92 | 92 | 88 | 280 | 0/8 |

### Detailed Analysis

**On 4/5 papers, review mode matches independent extraction exactly.** No value added.

**On aries, review mode is worse than independent extraction on the tables that matter most:**

| Page | GMFT | Reviewed | Independent (T1) | Behavior |
|------|------|----------|-------------------|----------|
| p4 | 9 | **9** | **22** | Review kept GMFT's garbled 2-col table; T1 extracted 22 clean rows |
| p7 | 18 | **20** | 19 | Review added 2 rows (minor fix) |
| p34 | 21 | **21** | 19 | Review kept GMFT's structure (slightly higher) |
| p38 | 7 | **6** | 6 | Review removed 1 row |
| p42 | 9 | **9** | **0** | Review kept GMFT false-positive; T1 correctly rejected |
| p48 | 6 | **5** | **0** | Review kept GMFT false-positive; T1 correctly rejected |

The critical failure is **p4**: GMFT produced a garbled 2-column table with 9 rows. Review mode made only minor corrections, keeping the fundamentally broken structure. Independent Claude (Track 1) ignored the broken structure entirely and extracted 22 clean rows from the image — a 2.4x improvement.

Similarly, **p42 and p48** are GMFT false positives. Independent Claude correctly identifies these as non-tables. Review mode, anchored to GMFT's "table", keeps them.

**Review mode's conservative behavior is its weakness.** When GMFT's extraction is structurally correct, review makes minor improvements (+1/-1 rows). When GMFT's extraction is structurally wrong, review still anchors to it. Independent extraction has no such anchor and can produce a clean result.

### Cost

| Track | Tables | Total cost | Avg/table |
|-------|--------|-----------|-----------|
| Track 1 (independent) | 27 | $2.047 | $0.076 |
| Track 3 (review) | 20 | $2.132 | $0.107 |

Review costs **41% more per table** than independent extraction because the prompt includes the full GMFT markdown table in addition to the image.

### Reasoning Leakage

**Zero leakage across all 20 reviewed tables.** The strict prompt ("Output ONLY the corrected markdown table, no commentary. If the table is correct, output it unchanged.") completely eliminates the reasoning leakage found in Stage 1D's repair experiments.

### SC-4 Answer

**No, sequential review does not produce measurably better results than independent extraction.** Review mode matches independent extraction on well-extracted tables and is worse on badly-extracted ones (anchoring to GMFT's broken structure). It costs 41% more per table. The strict prompt does eliminate reasoning leakage, but this is also true of Track 1's extraction prompt.

---

## Cross-Track Comparison

### Master Results Table (rows vs ground truth)

| Paper | GT | GMFT-DF | Claude Cropped (T1) | Vote/Resolve A (T2) | Sequential Review (T3) | Claude Full-Page (1D) |
|-------|-----|---------|---------------------|---------------------|----------------------|----------------------|
| hawker_2020 | 40 | 34 | **40** | 40 | 40 | 40 |
| hsu_2020 | 56 | 50 | **56** | 56 | 56 | 56 |
| hansen_2025 | 15 | 13 | **15** | 15 | 15 | 15 |
| paischer_2025 | 53 | 42 | **53** | 53 | 53 | 55 |
| aries_cost_account | 280 | 76 | **162** | 91 | 92 | N/A |

*GMFT-DF rows = DataFrame data rows (no header/separator). All other columns use pipe-row counting. Aries T2 has 6 pairs; T3 has 8 reviewed tables; T1 has 15 tables. Numbers are not directly comparable for aries because each track covers a different subset.*

### Cost Comparison

| Approach | Per-table cost | Claude calls | Value proposition |
|----------|---------------|-------------|-------------------|
| GMFT DataFrame | $0 | 0 | Free but misses rows; fails on 7/15 aries tables |
| Claude cropped (T1) | $0.076 | 1 per table | Best accuracy; 2.1x more rows than GMFT on aries |
| Vote/resolve (T2) | $0.076 | 1 per table | Same cost as T1, marginal accuracy gain (+3 rows on aries) |
| Sequential review (T3) | $0.107 | 1 per table | 41% more expensive than T1, worse on badly-extracted tables |
| Claude full-page (1D) | $0.078 | 1 per page | Similar cost; slight over-extraction risk (paischer: 55 vs GT 53) |

### What Each Approach Gets Right

| Capability | GMFT | Claude Cropped | Vote/Resolve | Sequential Review |
|-----------|------|----------------|--------------|-------------------|
| Grid-lined tables | Good | **Exact** | Same as Claude | Same as Claude |
| Space-aligned tables | Partial | **Best** | Same as Claude | Anchored to GMFT |
| False-positive rejection | No | **Yes** | Depends | **No** (keeps FPs) |
| GMFT extraction failures | Fails | **Succeeds** | N/A (no pair) | Keeps GMFT structure |
| Cost | Free | $0.076 | $0.076 | $0.107 |
| Requires Claude | No | Yes | Yes | Yes |

---

## Stage 4 Recommendations (SC-5)

### Detection Strategy

**Use GMFT only.** PyMuPDF `find_tables()` does not complement GMFT on the document types where we have gaps (government reports, cost accounts). It adds value only on grid-line journal papers where GMFT already works well.

**Do not lower GMFT's confidence threshold.** The current 0.98 threshold filters 11/26 aries detections. Some may be real tables, but the false-positive risk (p42, p48) outweighs the marginal coverage gain. Claude's false-positive rejection provides a safety net for borderline cases.

**Future work for detection:** The 13 undetected aries tables remain the biggest gap. These are space-aligned tables with no grid lines and no visual formatting cues that either detector uses. Solving this likely requires a different approach: page-level heuristics (detecting column-aligned numeric data), document structure analysis, or a vision model specifically trained for table detection. This is out of scope for the current pipeline.

### Extraction Strategy

**Ship Claude cropped-image extraction as a `TableEnhancer`.** Integration points:

1. **Primary trigger: GMFT detects but can't extract.** When GMFT's `AutoTableDetector` finds a table (confidence >= 0.98) but `AutoTableFormatter` returns null or an empty DataFrame, send the cropped image to Claude. This recovers 7/15 aries tables at $0.076 each. This is the highest-ROI use case.

2. **Secondary trigger: GMFT extraction looks suspect.** When GMFT produces a DataFrame but the quality looks questionable (e.g., very few rows vs the image size, garbled column names), send the image to Claude as an alternative. Use Claude's output if it has more rows. This addresses cases like aries p4 (GMFT: 7 rows, Claude: 22 rows).

3. **Optional: Claude as false-positive filter.** When Claude returns 0 rows or responds with "no table," flag the detection as a false positive. This caught p42 and p48 on aries.

### Multi-Pass Strategy

**Do not ship multi-pass.** Neither vote/resolve nor sequential review beat independent extraction. The implementation complexity is not justified by the marginal gains:

- Vote/resolve: +3 rows on aries (1.1% absolute), zero gain on other papers
- Sequential review: anchors Claude to GMFT's mistakes, costs 41% more, worse on key cases

If multi-pass is ever reconsidered, the research shows that independent extraction is strictly better than review mode. Claude should never be given GMFT's output as a starting point for correction — it should extract independently from the image.

### Prompt Design

The extraction prompt works well as-is:
```
Extract this table as a markdown pipe table.
Rules:
- Use | column headers | separated | by pipes |
- Include separator row (|---|---|---|)
- Preserve ALL numerical values exactly as printed
- Preserve merged/spanning cells by repeating values
- Output ONLY the markdown table, no commentary
```

**Zero reasoning leakage** across 47 Claude calls (27 Track 1 + 20 Track 3). The "Output ONLY the markdown table" instruction is sufficient.

### Pipeline Architecture Sketch

```
GMFT detects table
  |
  +-- DataFrame extraction succeeds, quality OK
  |     -> use GMFT markdown (free, fast, current behavior)
  |
  +-- DataFrame extraction fails (returns null)
  |     -> TableEnhancer: send cropped image to Claude ($0.076)
  |     -> use Claude markdown
  |
  +-- DataFrame extraction succeeds but suspect quality
        -> TableEnhancer: send cropped image to Claude ($0.076)
        -> compare row counts; use whichever has more
        -> if Claude returns 0 rows: flag as false positive, drop table
```

### What NOT to Build

- **PyMuPDF detection integration.** Over-detects on non-journal docs, no complementary value on aries.
- **Vote/resolve logic.** Adds complexity, no accuracy gain.
- **Review/correction mode.** Worse than independent extraction, more expensive.
- **Batch/parallel Claude calls.** The 10-15s per-call latency is not the bottleneck (detection is). Optimize later if table counts increase.

---

## Success Criteria Summary

| SC | Question | Answer | Evidence |
|----|----------|--------|----------|
| SC-1 | Detection coverage: GMFT vs PyMuPDF vs union | GMFT: 27/40 tables. PyMuPDF: 37 "tables" (mostly false positives on aries). Union: 59 (over-detected). **PyMuPDF does not close the aries gap.** | Track 0 detection_summary.json, 0 overlaps on aries |
| SC-2 | Claude accuracy from cropped images | **Exact GT on 4/5 papers.** 2.1x more rows than GMFT-DF on aries. Correctly rejects false positives. | Track 1 results.json, comparison.json |
| SC-3 | Vote/resolve vs individual tools | **No meaningful improvement.** Max +3 rows on aries (1.1%). Zero gain elsewhere. | Track 2 comparison.json |
| SC-4 | Sequential review vs independent extraction | **Worse on key cases.** Anchors to GMFT's broken structure (p4: 9 vs 22 rows). Keeps false positives. 41% more expensive. | Track 3 results.json |
| SC-5 | Stage 4 recommendations | **Ship Claude cropped-image as TableEnhancer.** GMFT-only detection. No multi-pass. Highest-value trigger: GMFT detects but can't extract. | Cross-track analysis above |

---

## Raw Data Sources

All experiment data is saved in `tests/corpus/runs/`:

| Track | Directory | Key files |
|-------|-----------|-----------|
| 0 | `table_spike_track0/{slug}/` | `detection_summary.json`, `images_manifest.json`, `overlaps.json`, `per_page_breakdown.json`, `*.png` |
| 1 | `table_spike_track1/{slug}/` | `results.json`, `comparison.json`, `table_p*_t*_claude.md` |
| 2 | `table_spike_track2/{slug}/` | `comparison.json` |
| 3 | `table_spike_track3/{slug}/` | `results.json`, `table_p*_t*_reviewed.md` |

Experiment scripts: `tests/corpus/pipelines/track{0,1,2,3}_*.py`
Prompts: `tests/corpus/prompts/{extract_table_cropped,review_table}.txt`

---
date: 2026-02-23T14:00:00-06:00
researcher: Claude
topic: "Saving tables as cropped images from PDFs"
tags: [research, doc-extraction, tables, gmft, pymupdf, claude-vision]
status: complete
last_updated: 2026-02-23
---

# Research: Saving Tables as Cropped Images from PDFs

**Date**: 2026-02-23
**Researcher**: Claude
**Research Type**: Feasibility / Gap Analysis

## Research Question

Is there a gap in the doc-extraction experimentation around saving **tables as cropped images** (separate from full-page images)? Specifically:

a) Could saving table regions as images be a resilient extraction technique (similar to how we already save full-page images for Claude vision)?
b) Could cropped table images help with targeted Claude usage, given the Stage 1D finding that Claude tends to ignore "focus only on fixing the table" when given full-page context?

## Summary

- **Yes, this is a genuine gap.** Stages 1-3 never experimented with cropped table images. GMFT exposes bounding boxes (`CroppedTable.rect.bbox`) but the pipeline only uses confidence scores and DataFrames.
- **GMFT has a built-in `table.image()` method** that returns a PIL Image of just the table region. This is ~5 lines of code to add.
- **PyMuPDF also supports `page.get_pixmap(clip=bbox)`** for rendering arbitrary page regions, and has its own `page.find_tables()` with bounding boxes.
- **This directly addresses two known limitations:** (1) Claude ignoring targeted repair instructions when given full-page images (1D finding), and (2) the space-aligned table problem (aries_cost_account: 120 vs GT 280) where neither pymupdf4llm nor GMFT produce good structured output.
- **Cost-effectiveness is high:** A cropped table image is ~10-30% the tokens of a full page image, so Claude table repair via cropped images could be 3-10x cheaper per table than full-page replacement.

## Detailed Findings

### 1. What Tools Support Table Region Cropping

#### GMFT (already in the pipeline)

GMFT's `CroppedTable` object has a built-in `image()` method:

```python
from gmft.auto import AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document

detector = AutoTableDetector()
doc = PyPDFium2Document("input.pdf")

for page in doc:
    tables = detector.extract(page)  # list[CroppedTable]
    for table in tables:
        # Bounding box
        print(table.rect.bbox)       # (xmin, ymin, xmax, ymax)
        print(table.confidence_score) # float

        # Cropped image — built-in!
        img = table.image(dpi=200)    # Returns PIL Image
        img.save("table_crop.png")
```

**Current usage in the pipeline** (`tests/corpus/pipelines/shared.py:259`): The pipeline already has the `CroppedTable` object in hand but only reads `table.confidence_score` and converts to DataFrame via `formatter.extract(table).df()`. The bbox and image capabilities are unused.

#### PyMuPDF (already in the pipeline)

PyMuPDF supports region clipping on its pixmap renderer:

```python
import pymupdf
doc = pymupdf.open("input.pdf")
page = doc[0]

# Option A: Use PyMuPDF's own find_tables()
tabs = page.find_tables()
for tab in tabs:
    pix = page.get_pixmap(dpi=300, clip=tab.bbox)
    pix.save("table_region.png")

# Option B: Use GMFT bbox with PyMuPDF rendering
# (GMFT uses PyPDFium2 coordinates, which are top-left origin like PyMuPDF)
pix = page.get_pixmap(dpi=300, clip=(x0, y0, x1, y1))
pix.save("table_region.png")
```

#### Docling

Docling provides `element.get_image(doc)` on `TableItem` objects, but requires enabling `generate_page_images=True` in pipeline options and is much slower (7-9s/page).

### 2. The Gap in Current Experimentation

| Stage | What was tested | What was NOT tested |
|-------|----------------|---------------------|
| 1A (pymupdf4llm) | `table_strategy` params, markdown output | PyMuPDF's `find_tables()` bbox extraction |
| 1C (GMFT) | DataFrame extraction, confidence filtering | `CroppedTable.image()`, bbox preservation |
| 1D (Claude vision) | Full-page images → Claude | Cropped table images → Claude |
| 3 (pipelines) | GMFT markdown replacement, Claude full-page replacement | Table image → Claude for targeted repair |

**The pipeline currently has two modes for Claude:** full-page replacement (expensive, $0.078/page) or no Claude at all. There is no middle ground of "send just the table image to Claude for targeted extraction."

### 3. Why Cropped Table Images Would Help

#### 3a. Resilient Technique for High-Sensitivity Content

Tables are the highest-sensitivity extraction target — a single wrong number in a cost table or performance spec invalidates the entire table. Current failure modes:

- **pymupdf4llm**: `<br>` artifacts in 333 cells across 7 docs, misses gridless tables entirely
- **GMFT**: Over-detects TOC/lists (delene_2001: 255 vs GT 150), can't detect space-aligned tables
- **Both**: aries_cost_account gets 120 vs GT 280 table rows

Saving table regions as images provides a **fallback that doesn't depend on any structured extraction working correctly**. Even if GMFT's DataFrame extraction garbles a table, the image preserves the exact visual content for human review or Claude re-extraction.

#### 3b. Targeted Claude Usage (the "Focus" Problem)

Stage 1D finding (`.project/active/claude-headless-deep-dive/findings.md`): When Claude receives a full-page image with instructions to "focus only on fixing the table," it tends to re-extract the entire page anyway. The supplemental text / repair approaches showed no improvement over pure vision — Claude ignores the "focus" instruction.

**Cropped table images solve this structurally:** You can't ignore "focus on the table" when the image IS the table. Claude would receive:
- A 200-400px wide image of just the table
- A prompt: "Extract this table as a markdown pipe table. Preserve all numbers exactly."
- No surrounding text to get distracted by

This is a fundamentally different signal-to-noise ratio than sending a full 1200px page image where the table is one of several elements.

#### 3c. Cost Reduction

A cropped table image at 200 DPI is roughly 200-600px wide and 100-800px tall (depending on table size), vs a full page at ~1200x1700px. The token cost for vision is roughly proportional to pixel area:

| Approach | Image size | Est. tokens | Est. cost |
|----------|-----------|------------|-----------|
| Full page (current) | ~1200x1700 | ~1,000 | $0.078/page |
| Cropped table | ~400x300 avg | ~150-300 | $0.010-0.020/table |

For a page with 1 table, this is **4-8x cheaper** than full-page replacement, while being more targeted.

### 4. How It Fits Into the Pipeline

Two integration points in the H5 pipeline:

#### Integration A: GMFT Confidence Bridge

When GMFT detects a table (confidence >= 0.98) but the DataFrame extraction looks suspicious (e.g., garbled cells, unexpected structure), save the table image for Claude repair instead of using the DataFrame.

```
GMFT detects table → confidence OK → DataFrame extraction → quality check
  ├── DataFrame OK → use GMFT markdown (current behavior)
  └── DataFrame suspect → save table.image() → Claude table repair (NEW)
```

**Cost:** Only triggers on tables where structured extraction fails but detection succeeds. Estimated <5% of detected tables.

#### Integration B: Claude Table-Only Enhancement

When the quality gate routes a page to Claude for table issues (not math), send just the cropped table image(s) instead of the full page. Keep the pymupdf4llm text for the non-table portions.

```
Quality gate: table anomaly detected, no math issues
  ├── Current: full page → Claude → replace entire page ($0.078)
  └── New: crop table image → Claude → replace just the table ($0.010-0.020)
```

**Cost:** ~4x cheaper per table-only page. Preserves pymupdf4llm's body text (which is fine for non-table content).

#### Integration C: Space-Aligned Table Recovery (Advanced)

For documents like aries_cost_account where neither pymupdf4llm nor GMFT detect tables:

1. Use PyMuPDF's `page.find_tables()` as a second-opinion detector (different algorithm than GMFT)
2. For any detected region, save the cropped image
3. Send to Claude for extraction

This addresses the "missing table detection" gap noted in findings section 6.3.

### 5. Implementation Complexity

**Low.** The infrastructure already exists:

| Component | Status | What's needed |
|-----------|--------|---------------|
| GMFT table detection | In pipeline | Already runs in `extract_gmft_pages()` |
| CroppedTable object | Available | Already in scope at `shared.py:259` |
| `table.image(dpi=N)` | GMFT built-in | Add 1 line to save image |
| Page rendering | Working | `extract_page.py`, `ai_repair.py` |
| Claude vision API | Working | Already used for full-page extraction |
| Image temp storage | Working | `tests/corpus/page_images/` pattern |

A minimal experiment (save GMFT table images + send to Claude) would be ~30-50 lines of new code in the pipeline scripts.

## Feasibility Assessment

**Highly feasible.** This is a composition of capabilities that already exist in the codebase and dependencies:
- GMFT's `.image()` method is a one-liner
- PyMuPDF's `get_pixmap(clip=bbox)` is a one-liner
- Claude vision integration is already working
- The pipeline's per-page decision framework already supports routing decisions

**Risk:** GMFT's bbox coordinates use PyPDFium2's coordinate space. If using PyMuPDF to render the crop (e.g., for pages where GMFT isn't loaded), coordinate translation may be needed. However, GMFT's built-in `.image()` method avoids this entirely — it uses its own PyPDFium2 backend for rendering.

## Recommendations

### Quick Win (Experiment-Level, Stage 3 Addendum)

1. Modify `extract_gmft_pages()` in `shared.py` to optionally save `table.image(dpi=200)` alongside the DataFrame
2. Write a small experiment script that sends GMFT-cropped table images to Claude with a table-specific prompt
3. Compare results against: (a) GMFT DataFrame extraction, (b) full-page Claude extraction, (c) pymupdf4llm table extraction
4. Test on hsu_2020 (table-heavy, good reference) and aries_cost_account (space-aligned tables)

### Stage 4 Integration

If the experiment confirms value:
1. Add `bbox: tuple[float, float, float, float]` and `image_path: Optional[str]` fields to the `GmftTable` dataclass
2. Add a `TableEnhancer` protocol alongside the existing `PageEnhancer` — sends cropped image to Claude for table-only repair
3. Quality gate gains a new route: `table_image_repair` (between `gmft_replace` and `claude_replace` in cost)
4. Decision log records which tables were repaired via image vs DataFrame vs full-page

### What NOT to Do

- Don't save table images for every table in every document — only for quality-gate-flagged tables or confidence-borderline detections
- Don't replace GMFT DataFrame extraction — it's fast, free, and works well for grid-lined tables. Table images are the fallback, not the primary path
- Don't build a PyMuPDF `find_tables()` → image path yet — that's more complex (coordinate spaces, different detection algorithm) and should be a separate experiment

## Open Questions

1. **Token cost validation:** The 4-8x cheaper estimate for cropped images needs empirical validation. GMFT table images may include padding/margins that increase size.
2. **Coordinate space interop:** If we later want to use PyMuPDF's `find_tables()` bounding boxes for cropping (Integration C), we need to verify coordinate space compatibility between PyMuPDF and PyPDFium2.
3. **Table image prompt design:** The prompt for "extract this table from an image" likely needs to be different from the full-page extraction prompt. Should be tested in the experiment.
4. **Multi-table pages:** When a page has 2-3 tables, should we send them individually (more API calls, more targeted) or as a composite image (fewer calls, potential confusion)?

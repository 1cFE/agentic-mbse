# Spec: Web Extraction Quality — Tables, Images, HTML Fidelity

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-03-29
**Complexity:** MEDIUM-HIGH
**Branch:** TBD (off `webfetch-tools`)
**Upstream:** `fusion-tea/.project/backlog/epic_source_extraction_fix.md` Item 1

---

## Business Goals

### Why This Matters

The web extraction backend (`web_backend.py`) landed in the previous work item but trafilatura's markdown output has critical quality gaps that make extracted sources unusable for technical analysis:

1. **Broken tables**: Parameter names are stripped, rows are misaligned, scientific notation values (e.g., `2.0×10²⁰`) vanish, units are orphaned on separate lines. Table 3 from arxiv-2411-06644 is a concrete failure case — it's the primary data table in the paper and is completely unusable.

2. **Lost images**: HTML pages contain figures (plots, diagrams, schematics) that are referenced throughout the text. The current pipeline extracts zero images (`image_count=0` hardcoded). For technical papers, losing all figures means losing a significant portion of the information.

3. **Mangled equations**: Mathematical content rendered as MathML or LaTeX-in-HTML comes through as empty table-like rows (`| (1) |`) with all mathematical content stripped.

4. **List formatting**: Bullet lists come through with redundant markers (`- \n• \nitem text`) instead of clean markdown.

These issues affect every HTML source extracted by the pipeline. The fusion-tea project has ~20 arxiv HTML sources that need re-extraction once this is fixed.

### Success Criteria

- [ ] Table 3 from `arxiv.org/html/2411.06644v1` renders with correct parameter names (e.g., `a_m`, `B_m`, `⟨n_p⟩`), values (e.g., `0.15 m`, `25 T`), and scientific notation (e.g., `1.7×10²⁰ m⁻³`)
- [ ] Table 1 (simple numeric table with subscript headers and superscript values) extracts with all 5 columns and 4 data rows intact
- [ ] Table 2 (parameter ranges) extracts with parameter names and ranges aligned
- [ ] Images from HTML sources are downloaded and saved to `images/` directory alongside extracted markdown, with relative path references in the markdown
- [ ] Numbered equations render as recognizable mathematical content (LaTeX notation or Unicode), not empty table rows
- [ ] Bullet lists render as clean markdown without duplicate markers
- [ ] Existing web extraction behavior (frontmatter, sanitization, fallback, batch mode) is fully preserved

### Priority

P0 — Blocking re-extraction of all HTML sources in fusion-tea. The current extracted sources are unusable for analysis.

---

## Problem Statement

### Current State

The web backend (`web_backend.py`) delegates entirely to trafilatura for HTML-to-markdown conversion:

```python
text = trafilatura.extract(
    html, url=url,
    include_comments=False,
    include_tables=True,
    include_links=True,
    output_format="markdown",
)
```

Trafilatura is a content extraction library optimized for news articles and blog posts. It works well for prose but has fundamental limitations with technical content:

**Tables**: Trafilatura's markdown table output strips HTML sub/superscripts (`<sub>`, `<sup>`) and inline math from table cells. For a table header like `⟨n_p⟩ [m⁻³]`, it produces `[m] |` or worse — an empty cell. For data cells containing `2.0×10²⁰`, it produces empty cells. The result is tables with missing parameter names, missing values, and orphaned units.

**Concrete failure — Table 3 from arxiv-2411-06644**:

What the HTML source contains:
```
| Parameter     | Optimum        | Alternate      |
|---------------|----------------|----------------|
| a_m           | 0.15 m         | 0.20 m         |
| B_m           | 25 T           | 25 T           |
| ⟨n_p⟩         | 1.7×10²⁰ m⁻³  | 1.3×10²⁰ m⁻³  |
| E_NBI         | 240 keV        | 360 keV        |
| P_NBI         | 15 MW          | 20 MW          |
| Q             | 5.8            | 5              |
```

What trafilatura produces:
```
| Parameter | Optimum | Alternate |
|---|---|---|
| End plug | ||
| 0.15 m | 0.20 m | |
| 4.5 m | 4.5 m | |
| 25 T | 25 T | |
| 4.0 T | 5.0 T | |
m-3
|
m-3
|
|
| 0.58 | 0.53 | |
```

Parameter names gone. Scientific notation values on their own lines. Row alignment broken. Unusable.

**Images**: The HTML contains `<img>` tags with relative URLs (e.g., `extracted/5986138/wham_ions.png`). Trafilatura may preserve image references in its markdown output but the pipeline does not download or save any images. `image_count=0` is hardcoded in the return value.

**Equations**: Display equations in arxiv HTML are rendered as MathML within `<table>` elements (one column for the equation, one for the number). Trafilatura extracts these as `| (1) |` — preserving only the equation number and losing all mathematical content.

### Desired Outcome

Web extraction produces high-fidelity markdown from technical HTML sources:
- Tables preserve structure, subscripts/superscripts (as Unicode or plaintext), and scientific notation
- Images are downloaded and saved locally with correct markdown references
- Equations are preserved as LaTeX or Unicode math notation
- Lists are clean markdown

---

## Scope

### In Scope

1. **HTML table pre-processing**: Convert `<sub>`, `<sup>`, `<math>`, inline LaTeX within table cells to plaintext/Unicode before trafilatura runs, so the markdown output preserves them.

2. **Image downloading**: Detect `<img>` tags in the HTML, resolve relative URLs, download images to an `images/` subdirectory, and update references in the extracted markdown.

3. **Equation handling**: Convert MathML display equations to LaTeX notation (or at minimum, preserve them as inline LaTeX `$...$` / display `$$...$$`) instead of losing them entirely.

4. **List cleanup**: Post-process markdown to fix duplicate bullet markers and broken list formatting.

5. **Post-processing pipeline**: A composable set of HTML pre-processing and markdown post-processing steps that run around the trafilatura core, improving output without replacing the extraction engine.

### Out of Scope

- Replacing trafilatura with a different extraction engine (we fix around it)
- JavaScript rendering / headless browser
- Table detection from images (that's the PDF pipeline's job)
- Changes to HTML sanitization logic (working correctly)
- Changes to frontmatter/provenance system (working correctly)
- Re-extraction of fusion-tea sources (that's epic Item 2, depends on this)

### Edge Cases & Considerations

- **MathML variants**: arXiv uses MathML extensively; other sites may use KaTeX, MathJax, or plain LaTeX. The pre-processor should handle the most common representations.
- **Image download failures**: Individual image failures should not fail the extraction. Log a warning, leave the markdown reference as-is (pointing to original URL).
- **Image size limits**: Should we cap image downloads? A reasonable default (e.g., 20MB per image, 100MB total) prevents runaway downloads.
- **Relative vs absolute image URLs**: Need to resolve relative URLs against the page's base URL (and handle `<base>` tags).
- **SVG images**: Common in technical content. Download as-is (`.svg` files), don't try to rasterize.
- **Data URIs in images**: Skip `data:` URI images (they're inline, no download needed, and can be huge).
- **Pandoc fallback path**: The pandoc fallback (`_fallback_pandoc`) should also benefit from image downloading. Consider whether pre-processing should happen before both backends or only trafilatura.
- **Trafilatura version sensitivity**: Pre-processing the HTML before passing to trafilatura could interact poorly with trafilatura's own content detection. Test carefully.

---

## Requirements

### Functional Requirements

**HTML Pre-processing (before extraction)**

1. **FR-1**: A pre-processing step MUST convert `<sub>` and `<sup>` tags within `<table>` elements to Unicode subscript/superscript characters (e.g., `<sup>20</sup>` → `²⁰`, `<sub>m</sub>` → `ₘ`) before passing HTML to trafilatura.

2. **FR-2**: A pre-processing step MUST convert `<sub>` and `<sup>` tags in non-table contexts to a readable plaintext representation where Unicode subscript/superscript characters are not available (e.g., `T<sub>e</sub>` → `T_e`, `10<sup>20</sup>` → `10²⁰`).

3. **FR-3**: A pre-processing step MUST convert MathML `<math>` elements to LaTeX notation (using a lightweight converter) or, at minimum, extract the `alttext` attribute that arXiv MathML elements provide.

4. **FR-4**: A pre-processing step SHOULD convert display equation tables (the `<table>` wrapping pattern arXiv uses for numbered equations) into markdown-friendly format: `$$ equation $$` with the equation number as a trailing comment or parenthetical.

5. **FR-5**: All pre-processing MUST be applied to the HTML *after* sanitization but *before* trafilatura extraction, so trafilatura sees clean, simplified HTML.

**Image Downloading**

6. **FR-6**: The web backend MUST detect `<img>` tags in the extracted markdown (or source HTML), resolve their `src` URLs against the page's base URL, and download them to an `images/` subdirectory within the output directory.

7. **FR-7**: Image references in the output markdown MUST be rewritten to use relative paths (`images/filename.png`) matching the downloaded files.

8. **FR-8**: Image downloads MUST have a per-image size limit (default 20MB) and a per-page total limit (default 100MB). Images exceeding limits MUST be skipped with a log warning, and the markdown reference SHOULD be left pointing to the original URL.

9. **FR-9**: `data:` URI images MUST be skipped (not downloaded). SVG images MUST be downloaded as-is.

10. **FR-10**: Individual image download failures MUST NOT fail the overall extraction. The `ExtractionResult.image_count` field MUST reflect the actual number of successfully downloaded images (not hardcoded 0).

**Markdown Post-processing**

11. **FR-11**: A post-processing step MUST clean up duplicate bullet markers in lists (e.g., `- \n• \ntext` → `- text`).

12. **FR-12**: A post-processing step SHOULD normalize whitespace around table separators to ensure valid markdown table syntax.

13. **FR-13**: Post-processing MUST be applied after trafilatura extraction and before writing the output file.

**Integration**

14. **FR-14**: The `extract_web_content()` function signature MUST remain backward-compatible. New parameters (if any) MUST have defaults that preserve current behavior.

15. **FR-15**: The pandoc fallback path SHOULD also benefit from image downloading (images detected in pandoc output should also be downloaded).

16. **FR-16**: The `--save-source` flag MUST continue to save the *original* HTML (before pre-processing), as this is the provenance record.

### Non-Functional Requirements

17. **NFR-1**: Pre-processing and post-processing steps MUST be individually testable as pure functions (HTML string → HTML string, markdown string → markdown string).

18. **NFR-2**: Image downloading MUST use the existing `fetch_url()` from `http.py` with appropriate timeout and User-Agent settings.

19. **NFR-3**: The pre-processing pipeline MUST NOT significantly increase extraction time for non-technical pages (< 1 second overhead for pages without math/tables).

20. **NFR-4**: All existing web extraction tests MUST continue to pass.

---

## Acceptance Criteria

### Table Quality (primary success gate)

- [ ] Extract `https://arxiv.org/html/2411.06644v1` → Table 1 has 5 columns including `⟨n_p⟩` header and `×10²⁰` values
- [ ] Same extraction → Table 3 has parameter names (a_m, B_m, etc.) in first column, Optimum and Alternate values aligned
- [ ] Same extraction → Table 2 has Parameter and Range columns with values in correct rows
- [ ] Extract a Wikipedia page with tables → tables render correctly in markdown

### Image Handling

- [ ] Extract `https://arxiv.org/html/2411.06644v1` → `images/` directory contains downloaded figure PNGs
- [ ] Markdown references point to `images/filename.png` (relative paths)
- [ ] `ExtractionResult.image_count` equals the number of downloaded images
- [ ] Broken image URLs produce warnings but don't fail extraction

### Equation Handling

- [ ] Display equations from arxiv-2411-06644 render as LaTeX (`$$...$$`) or at minimum contain the mathematical content (not just `| (1) |`)
- [ ] Equation numbers are preserved

### List & Formatting

- [ ] Bullet lists from arxiv-2411-06644 render as clean `- item` markdown without duplicate markers

### Regression

- [ ] All existing tests pass (`uv run pytest tests/`)
- [ ] Frontmatter, sanitization, batch mode, PDF routing all work identically
- [ ] `--save-source` saves original HTML (not pre-processed HTML)

---

## Technical Approach (directional, not binding)

### Architecture: Pre/Post-processing Wrapper

Rather than replacing trafilatura, add processing stages around it:

```
HTML (raw)
  → sanitize (existing)
  → pre-process: sub/sup → Unicode, MathML → LaTeX, equation tables → $$
  → trafilatura.extract()
  → post-process: fix lists, normalize tables, download images
  → write output
```

This keeps trafilatura as the content extraction engine (it's good at identifying article content vs. boilerplate) while fixing its output quality for technical content.

### Key Implementation Decisions (for design phase)

1. **MathML → LaTeX converter**: Use `latex2mathml` (reverse direction) or a lightweight custom walker? arXiv MathML elements have `alttext` attributes with the original LaTeX — this may be the simplest path.

2. **Unicode sub/superscript coverage**: Full Unicode coverage only exists for digits and some Latin letters. For characters without Unicode equivalents, fall back to `_x` / `^x` notation.

3. **Image download concurrency**: Sequential is simplest. Consider `concurrent.futures.ThreadPoolExecutor` if papers with many images are slow.

4. **Where to detect images**: From the source HTML (more reliable, captures all `<img>` tags) vs. from trafilatura's markdown output (may miss images trafilatura filtered out). HTML detection is safer.

### New/Modified Files (directional)

```
src/agentic_mbse/extraction/
    web_preprocess.py    # NEW — sub/sup conversion, MathML handling, equation tables
    web_postprocess.py   # NEW — list cleanup, table normalization
    web_images.py        # NEW — image detection, download, path rewriting
    web_backend.py       # MODIFIED — integrate pre/post-processing and image pipeline

tests/
    test_web_preprocess.py   # NEW — unit tests for HTML pre-processing
    test_web_postprocess.py  # NEW — unit tests for markdown post-processing
    test_web_images.py       # NEW — image download tests (with mocked HTTP)
    fixtures/
        arxiv_table.html     # NEW — sample table HTML from arxiv
        arxiv_equation.html  # NEW — sample equation HTML from arxiv
```

---

## Related Artifacts

- **Upstream epic**: `fusion-tea/.project/backlog/epic_source_extraction_fix.md`
- **Previous spec**: `.project/active/web-source-capture/spec.md` (the web backend itself)
- **Reference failure case**: `fusion-tea/exploration/phase_1a/research/11-magnetic-mirror/iter-01/sources/arxiv-2411-06644-confinement-predictions.md`
- **Reference HTML source**: `https://arxiv.org/html/2411.06644v1`
- **Web backend code**: `src/agentic_mbse/extraction/web_backend.py`

---

**Next Steps:** Review spec, then proceed to `/_my_design`

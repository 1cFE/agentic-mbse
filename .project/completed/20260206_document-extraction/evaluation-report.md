# Extraction Pipeline Evaluation Report

**Date:** 2026-02-06
**Branch:** pdf-extract
**Evaluator:** Claude (automated inspection agents)
**Pipeline version:** Commit 73a20d5

---

## Executive Summary

Evaluated 7 PDF extractions from `/home/reid/1cfe/literature/` across four quality dimensions: markdown structure, index quality, image extraction, and table extraction. All 7 documents were extracted using the **pymupdf** backend (Docling failed on the 2 documents where it was attempted, falling back correctly).

**Overall score: 2.68 / 5.00** — Usable for text-heavy reading but significant gaps in tables, equations, and structural fidelity.

| Category | Avg Score | Assessment |
|---|---|---|
| Markdown Structure | 2.64 / 5 | Headers often rendered as bold text; page number artifacts pervasive |
| Index Quality | 2.43 / 5 | Empty indexes for 4/7 docs due to header detection failure |
| Image Extraction | 3.64 / 5 | Strongest area — images extracted reliably with correct paths |
| Table Extraction | 2.00 / 5 | Weakest area — most tables rendered as space-separated plain text |

---

## Test Corpus

| ID | Document | Pages | Size | Backend | Chars | Images |
|---|---|---|---|---|---|---|
| 2232 | Handley et al. — "Potential Early Markets for Fusion Energy" | ~30 | 4.3 MB | pymupdf | 83K | 6 |
| 2233 | Araiinejad & Shirvan — "Techno-economic analysis of D-T MCF" | ~30 | 2.4 MB | pymupdf | 77K | 8 |
| 2235 | "Global Fusion and AI Landscape" | ~40 | 4.3 MB | pymupdf | 100K | 2 |
| 2236 | "Digital Twins for Fusion and SMRs" | ~80 | 3.6 MB | pymupdf | 281K | 31 |
| 2237 | LA-UR-25-24580 (LANL PJMIF costing) | 65 | 2.7 MB | pymupdf* | 182K | 19 |
| 2238 | Lampe & Manheimer — "Comments on CBFR" | ~40 | 1.8 MB | pymupdf* | 89K | 40 |
| 2241 | Eester et al. — "ICRH wave and Fokker-Planck" | ~30 | 1.0 MB | pymupdf | 96K | 28 |

*Docling attempted first but failed; pymupdf fallback used. Fallback mechanism worked correctly.

---

## Per-Document Scores

| ID | Structure | Index | Images | Tables | Overall |
|---|---|---|---|---|---|
| 2232 | 3.0 | 1.0 | 4.0 | 2.0 | **2.50** |
| 2233 | 2.5 | 1.0 | 3.5 | 2.0 | **2.25** |
| 2235 | 3.0 | 3.0 | 2.0 | 2.0 | **2.50** |
| 2236 | 3.0 | 3.0 | 4.0 | 4.0 | **3.50** |
| 2237 | 3.0 | 4.0 | 4.0 | 2.0 | **3.25** |
| 2238 | 2.0 | 1.0 | 4.0 | 1.0 | **2.00** |
| 2241 | 2.0 | 4.0 | 4.0 | 1.0 | **2.75** |
| **Avg** | **2.64** | **2.43** | **3.64** | **2.00** | **2.68** |

---

## Category Analysis

### 1. Markdown Structure (2.64 / 5)

**What works:**
- Body text is generally readable and flows logically
- Bullet lists render correctly with `- ` prefix
- Bold/italic inline formatting preserved in most cases
- Document ordering matches original PDFs

**Persistent issues:**

| Issue | Severity | Affected Docs | Example |
|---|---|---|---|
| Headers as bold text | HIGH | 2232, 2233, 2238 | `**1 Introduction**` instead of `## 1 Introduction` |
| Page number artifacts | HIGH | All 7 | Bare `17` on its own line between paragraphs |
| Running header/footer leaks | MEDIUM | 2232, 2233, 2238 | Document title repeated every 2 pages |
| Equation garbling | MEDIUM | 2237, 2238, 2241 | `_LCOE_ [$ _MWh_ ] = [(] _[C][AC]_` |
| Unicode ligature failures | MEDIUM | 2235 | `fi` → `` (199 occurrences) |
| Superscript/subscript loss | LOW | 2237, 2241 | `m³` → `m [3]`, `km²` → `km[2]` |
| Soft hyphen artifacts | LOW | 2233 | Word-join artifacts from column layouts |

### 2. Index Quality (2.43 / 5)

**What works:**
- When sections ARE detected, line numbers are accurate (spot-checked across 3 docs)
- YAML frontmatter properly formatted with checksums
- Hierarchy and breadcrumb generation correct
- Checksum-based freshness detection works

**Persistent issues:**

| Issue | Severity | Affected Docs | Root Cause |
|---|---|---|---|
| Empty index (0 sections) | CRITICAL | 2232, 2233, 2238 | `parse_sections()` requires `##`-prefixed markdown headers, but pymupdf renders headers as bold text for these docs |
| Low section count | MEDIUM | 2235, 2236 | Only top-level sections detected; subsections rendered as bold text |
| Appendices not indexed | LOW | 2237 | Appendix headers (A, B, C) use letter numbering, not matched by `\d+` pattern |

**Root cause analysis:** The index parser (`index.py:73-79`) uses three regex patterns, all requiring markdown header syntax (`^#{2,6}\s+`). When pymupdf renders section headers as bold text (`**1 Introduction**`) instead of markdown headers (`## 1 Introduction`), the parser finds zero matches. This is the single biggest quality gap because it cascades: no index → no `read_section()` → no AI-assisted navigation.

### 3. Image Extraction (3.64 / 5)

**What works:**
- All images extract as valid PNGs with non-zero file sizes
- Image paths in markdown resolve correctly to `images/` directory
- Figure captions preserved adjacent to image references
- DPI (150) produces readable images

**Persistent issues:**

| Issue | Severity | Affected Docs | Example |
|---|---|---|---|
| Empty alt-text | MEDIUM | All 7 | `![]()` instead of `![Figure 1: ...]()` |
| Absolute paths in markdown | MEDIUM | 2237, 2238 | `![](/home/reid/1cfe/literature/2237/...images/...)` |
| Decorative images extracted | LOW | 2235, 2236 | Logos, borders, page decorations |

**Note:** The absolute path issue only affects pymupdf fallback output. The docling backend has `_rewrite_image_paths()` but pymupdf writes absolute paths directly. This makes the markdown non-portable.

### 4. Table Extraction (2.00 / 5)

**What works:**
- Document 2236 had proper markdown pipe tables (4/5 score) — this appears to be document-dependent
- Simple 2-3 column tables occasionally render correctly

**Persistent issues:**

| Issue | Severity | Affected Docs | Example |
|---|---|---|---|
| Tables as plain text | CRITICAL | 2232, 2233, 2237, 2238, 2241 | Columns space-separated, no `|` delimiters |
| Multi-column collapse | HIGH | 2237 | Multiple table rows merged into single lines |
| Missing cell values | MEDIUM | 2237 | Table 3: rows like `"GdBCO"` with no data columns |
| Table caption detachment | LOW | 2233, 2238 | Caption appears far from table content |

**Root cause:** pymupdf4llm's default `table_strategy="lines_strict"` requires visible cell borders in the PDF. Most academic papers use borderless or minimal-border tables, which fall through to plain-text rendering. The `"lines"` and `"text"` strategies exist but are not currently used.

---

## Spec Cross-Reference

| Requirement | Status | Notes |
|---|---|---|
| FR-1: PDF support | PASS | All 7 PDFs processed |
| FR-3: Image extraction with embedded refs | PARTIAL | Images extracted; refs use absolute paths for pymupdf |
| FR-5: Fallback when primary fails | PASS | Docling → pymupdf fallback worked on 2237, 2238 |
| FR-6: Table reconstruction | FAIL | Only 1/7 docs had proper markdown tables |
| FR-9: Index generation | PARTIAL | Works when headers detected; fails for 4/7 docs |
| FR-12: Configurable timeout | PASS | 600s default, configurable via `--timeout` |
| FR-14: summary.json metadata | PASS | All docs produced valid summary.json |
| FR-17: full_document.md output | PASS | All docs produced full_document.md |
| FR-18: images/ subdirectory | PASS | All docs with images saved to images/ |
| AC: Tables rendered as markdown | FAIL | Most tables not in pipe syntax |

---

## Persistent Issues: Root Causes and Recommendations

### Issue 1: Headers Rendered as Bold Text (CRITICAL)

**Impact:** Cascading — breaks index generation, section navigation, and downstream tooling.

**Root cause:** pymupdf4llm's default header detection (`IdentifyHeaders`) uses font-size popularity analysis. If a document uses fonts where bold section headers happen to match the "body text" size determination, they get rendered as bold text rather than markdown headers.

**Recommendation — Two-pronged approach:**

1. **Use `hdr_info` with ToC-based detection.** pymupdf4llm supports a `TocHeaders` class that uses the PDF's built-in table of contents instead of font-size heuristics. Pass this to `to_markdown(hdr_info=...)`. This should work for any PDF with a proper ToC (most academic papers).

2. **Post-processing header promotion.** Add a post-extraction pass that detects bold-text patterns matching numbered section headers and promotes them to markdown headers:
   ```
   **1 Introduction**          →  ## 1 Introduction
   **1.2 Background**          →  ### 1.2 Background
   **Appendix A Title**        →  ## Appendix A Title
   ```
   This catches cases where ToC-based detection fails.

**Implementation priority:** HIGH — this is the single most impactful fix.

**References:**
- [pymupdf4llm API docs](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html) — `hdr_info` parameter
- [PyMuPDF header detection](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) — `IdentifyHeaders` vs `TocHeaders`

### Issue 2: Page Number and Running Header/Footer Artifacts (HIGH)

**Impact:** 16-66 artifacts per document; pollutes text and confuses search/indexing.

**Root cause:** pymupdf4llm extracts all text content including page numbers, running headers, and footers. There are `header=False` and `footer=False` parameters, but they require the **PyMuPDF Layout** package (`pymupdf-layout`), which provides ML-based page element classification.

**Recommendation — Tiered approach:**

1. **Investigate `pymupdf-layout` integration.** The layout package provides automatic header/footer detection and suppression via `header=False, footer=False`. This is the cleanest solution but adds a dependency.

2. **Post-processing regex strip.** Add a cleanup pass that removes:
   - Bare page numbers on their own lines: `^\d{1,4}$` (between blank lines)
   - Repeated running headers: detect the most common short lines (< 80 chars) and remove duplicates
   - Lines consisting only of the document title/author names repeated

**Implementation priority:** HIGH — affects all documents.

**References:**
- [PyMuPDF Layout docs](https://pymupdf.readthedocs.io/en/latest/pymupdf-layout/index.html)
- [PyMuPDF Discussion #2259](https://github.com/pymupdf/PyMuPDF/discussions/2259) — header/footer removal
- [PyMuPDF Discussion #1930](https://github.com/pymupdf/PyMuPDF/discussions/1930) — footer/header text

### Issue 3: Tables Not in Markdown Pipe Syntax (CRITICAL)

**Impact:** Quantitative data in tables is effectively lost for programmatic use.

**Root cause:** pymupdf4llm's default `table_strategy="lines_strict"` requires visible cell borders. Academic papers commonly use borderless tables, which are not detected as tables and fall through to plain-text rendering.

**Recommendation — Multi-strategy approach:**

1. **Try `table_strategy="lines"` first.** This is less strict and should catch more tables. If that fails, try `"text"` which uses text positioning alone.

2. **Implement strategy cascade.** Extract with `"lines_strict"`, check if tables were detected, if not re-extract with `"lines"`, then `"text"`. This mirrors the existing primary/fallback backend pattern.

3. **Leverage the existing `--fix-tables` flag.** The spec (FR-11) already defines a two-pass table repair using Claude headless mode. This is the right approach for tables that no heuristic can handle — use AI to reconstruct pipe tables from the plain-text layout. This should be prioritized.

**Implementation priority:** CRITICAL — tables carry essential quantitative data in technical documents.

**References:**
- [pymupdf4llm API](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html) — `table_strategy` parameter
- [pymupdf4llm Discussion #168](https://github.com/pymupdf/pymupdf4llm/discussions/168) — table extraction issues

### Issue 4: Equation/Formula Garbling (MEDIUM)

**Impact:** Mathematical content unreadable in 3/7 documents.

**Root cause:** PDF equations use specialized fonts and glyph positioning that don't map to Unicode text streams. pymupdf4llm extracts the raw text layer, which produces garbled sequences of brackets, subscripts, and variable names. This is a fundamental limitation of text-based PDF extraction for math-heavy content.

**Recommendation:**

1. **Docling prioritization.** Docling's ML-based extraction handles equations significantly better. Focus on making Docling reliable (investigate why it failed on 2237/2238) rather than trying to fix pymupdf equation output.

2. **Flag math-heavy sections.** Add a heuristic to detect likely equations (density of brackets, single-character variable names, fraction-like patterns) and insert a marker like `<!-- equation: see original PDF page N -->` to alert downstream consumers.

3. **Long-term: MathPix/Nougat integration.** For math-heavy corpora, consider integrating a specialized equation OCR tool as a post-processor. Out of scope for now, but worth noting.

**Implementation priority:** MEDIUM — affects a subset of documents.

### Issue 5: Absolute Image Paths in Pymupdf Output (MEDIUM)

**Impact:** Output markdown is non-portable; images won't render if files are moved.

**Root cause:** The pymupdf backend passes `image_path=str(images_dir)` (absolute path) to `to_markdown()`, and pymupdf4llm embeds whatever path it receives into the markdown. The docling backend has `_rewrite_image_paths()` to normalize paths, but no equivalent exists for pymupdf.

**Recommendation:** Add a post-extraction path rewrite in the pymupdf backend, identical to what docling does:
```python
md_text = md_text.replace(str(images_dir), "images")
```

**Implementation priority:** MEDIUM — simple fix, high portability impact.

### Issue 6: Unicode Ligature Failures (MEDIUM)

**Impact:** 199 replacement characters in one document (2235); occasional in others.

**Root cause:** Some PDFs use font-specific ligature glyphs (fi, fl, ff, ffi) that pymupdf maps to Unicode replacement characters when the font's ToUnicode CMap is incomplete or missing.

**Recommendation:** Add a post-processing pass that:
1. Replaces common Unicode replacement patterns: `` adjacent to known ligature contexts → `fi`, `fl`, etc.
2. Uses `pymupdf4llm`'s `use_glyphs=True` parameter experimentally to see if glyph-based extraction resolves the issue for affected fonts.

**Implementation priority:** LOW-MEDIUM — affects specific documents.

### Issue 7: Empty Image Alt-Text (LOW)

**Impact:** Accessibility concern; doesn't affect content extraction.

**Root cause:** pymupdf4llm generates `![]()` references without extracting figure captions as alt-text. Figure captions exist in the document text but are not associated with image references.

**Recommendation:** Post-processing: scan for `![](...)` immediately followed by `Figure N:` text and promote the caption into alt-text: `![Figure N: caption](...)`.

**Implementation priority:** LOW — cosmetic improvement.

### Issue 8: Index Pattern Doesn't Match Appendices (LOW)

**Impact:** Appendix sections (A, B, C) not indexed even when rendered as proper markdown headers.

**Root cause:** `parse_sections()` regex requires `\d+` (digit-based numbering). Letter-based section numbers like `A`, `B.1` are not matched.

**Recommendation:** Add a pattern for letter-based sections:
```python
re.compile(r"^#{2,6}\s+([A-Z](?:\.\d+)*)\s+(.+)$")
```

**Implementation priority:** LOW — minor enhancement.

---

## Recommended Implementation Order

| Priority | Issue | Effort | Impact |
|---|---|---|---|
| 1 | Post-processing header promotion (bold → `##`) | Small | Fixes empty indexes for 4/7 docs |
| 2 | Absolute image path rewrite in pymupdf backend | Trivial | Fixes portability |
| 3 | `table_strategy` cascade (`lines_strict` → `lines` → `text`) | Small | Improves table detection |
| 4 | Page number / running header stripping | Medium | Cleans up all 7 docs |
| 5 | `--fix-tables` implementation (Claude headless table repair) | Medium | Fixes remaining broken tables |
| 6 | `hdr_info=TocHeaders` for ToC-based header detection | Small | Better header detection upstream |
| 7 | Figure caption → alt-text promotion | Small | Accessibility improvement |
| 8 | Appendix letter-numbering in index parser | Trivial | Minor coverage improvement |
| 9 | Ligature replacement post-processing | Small | Font-specific fix |
| 10 | Investigate Docling failures on 2237/2238 | Medium | Enables better primary extraction |

---

## Appendix: Detailed Per-Document Findings

### 2232 — Handley et al. (Fusion Markets)
- **Structure (3/5):** Headers properly rendered as `##` for top-level; subsections as bold. Running headers leak through (title repeated ~16 times).
- **Index (1/5):** 0 sections detected. Headers in the original use bold styling that pymupdf renders as `**bold**` not `## header`.
- **Images (4/5):** 6 images extracted, all valid PNGs. One decorative header image.
- **Tables (2/5):** Tables present but rendered as space-separated text. Cost comparison tables lose column alignment.

### 2233 — Araiinejad & Shirvan (D-T MCF TEA)
- **Structure (2.5/5):** Similar bold-header issue as 2232. Soft hyphen artifacts from two-column layout. Page numbers throughout.
- **Index (1/5):** 0 sections. Same bold-header root cause.
- **Images (3.5/5):** 8 images extracted. Some figures slightly clipped.
- **Tables (2/5):** Economic parameter tables rendered as plain text. Key TEA data hard to parse.

### 2235 — Global Fusion and AI Landscape
- **Structure (3/5):** Headers detected for some sections. 199 Unicode replacement characters from ligature failures.
- **Index (3/5):** Partial — some sections indexed but not all. Missing subsections.
- **Images (2/5):** Only 2 images extracted despite document containing more figures.
- **Tables (2/5):** Tables as space-separated text.

### 2236 — Digital Twins for Fusion and SMRs
- **Structure (3/5):** Best-structured of the corpus. Headers mostly detected correctly. Page artifacts still present.
- **Index (3/5):** Reasonable section coverage. Some subsections missing.
- **Images (4/5):** 31 images extracted — comprehensive. All valid.
- **Tables (4/5):** **Best table extraction** — most tables rendered as proper markdown pipe tables. This document likely had visible cell borders that triggered `lines_strict` detection.

### 2237 — LA-UR-25-24580 (LANL PJMIF)
- **Structure (3/5):** 12 major sections properly detected as `##` headers. Subsections as bold. 55 page number artifacts. Equations garbled.
- **Index (4/5):** Good — 12 sections indexed with accurate line numbers. Missing appendices A, B, C (letter numbering).
- **Images (4/5):** 19 images extracted, all valid. Absolute paths in markdown.
- **Tables (2/5):** 11 table captions found but only 2 rendered as markdown tables. Building cost table (Table 2) and material properties (Table 3) critical for TEA analysis but plain-text only.

### 2238 — Lampe & Manheimer (CBFR)
- **Structure (2/5):** Headers as bold text. Heavy equation content garbled. Two-column layout artifacts.
- **Index (1/5):** 0 sections. Bold-header issue.
- **Images (4/5):** 40 images extracted — thorough. Includes plots and diagrams.
- **Tables (1/5):** Worst table extraction. Physics parameter tables completely lost to plain text.

### 2241 — Eester et al. (ICRH Fokker-Planck)
- **Structure (2/5):** Headers as bold for some sections. Dense mathematical content heavily garbled.
- **Index (4/5):** Good detection for sections that used proper header formatting.
- **Images (4/5):** 28 images extracted. Physics plots and diagrams all present.
- **Tables (1/5):** Parameter tables rendered as space-separated text. Plasma physics data tables non-parseable.

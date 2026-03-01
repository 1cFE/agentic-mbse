# pymupdf4llm API Reference (v0.2.9)

**Captured:** 2026-02-22
**Source:** Installed package at `.venv/lib/python3.12/site-packages/pymupdf4llm/`

---

## `to_markdown()` Full Signature

```python
to_markdown(
    doc,                        # pymupdf.Document or filename string (REQUIRED)
    *,
    pages=None,                 # list[int] | None — 0-based page numbers (None = all)
    hdr_info=None,              # callable | object | False | None — header detection
    write_images=False,         # bool — save images/graphics as files
    embed_images=False,         # bool — embed images as base64 in markdown
    ignore_images=False,        # bool — skip image extraction entirely
    ignore_graphics=False,      # bool — skip vector graphics
    detect_bg_color=True,       # bool — detect background color
    image_path='',              # str — directory to store extracted images
    image_format='png',         # str — image format (png, jpg, etc.)
    image_size_limit=0.05,      # float — skip images smaller than this fraction of page
    filename=None,              # str | None — override filename for image naming
    force_text=True,            # bool — output text even over image backgrounds
    page_chunks=False,          # bool — return list of per-page dicts instead of string
    page_separators=False,      # bool — insert page separator markers
    margins=0,                  # int | tuple — omit content overlapping margins
    dpi=150,                    # int — resolution for generated images
    page_width=612,             # float — assumed page width (for variable layouts)
    page_height=None,           # float — assumed page height
    table_strategy='lines_strict',  # str — table detection strategy
    graphics_limit=None,        # int | None — ignore all graphics if count exceeds this
    fontsize_limit=3,           # float — minimum font size to include
    ignore_code=False,          # bool — suppress code formatting (monospace fonts)
    extract_words=False,        # bool — include word-level bboxes in page chunks
    show_progress=False,        # bool — print per-page progress
    use_glyphs=False,           # bool — replace invalid Unicode with glyph numbers
    ignore_alpha=False,         # bool — ignore transparent text (alpha=0)
    **kwargs
) -> str | list[dict]          # string if page_chunks=False, list if True
```

---

## Parameter Details

### Header Detection (`hdr_info`)

Four modes:

| Value | Behavior |
|-------|----------|
| `None` (default) | Auto-creates `IdentifyHeaders(doc)` — font-size-based detection |
| Callable function | Called as `func(span, page=None)` → returns `"## "` etc. or `""` |
| Object with `.get_header_id()` | Method called same way as callable |
| `False` | Disable header detection entirely — no `#` prefixes |

**Our current code** passes a custom callable `_academic_header_detector` that uses bold flag + section numbering regex.

### Table Strategy (`table_strategy`)

| Value | Behavior | Notes |
|-------|----------|-------|
| `"lines_strict"` | **DEFAULT.** Detect tables only where clear line boundaries exist | Most conservative, fewest false positives |
| `"lines"` | More aggressive line-based detection | What our code currently uses — may produce false `<br>` artifacts |
| `"text"` | Text-based table detection (no lines needed) | For tables without drawn borders |
| `None` | Disable table detection | |

**Key finding from old branch:** Switching from `"lines"` to `"lines_strict"` eliminated 252 false `<br>` artifacts. This is the single most impactful parameter discovered so far.

### Image Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `write_images` | `False` | Save extracted images to disk |
| `embed_images` | `False` | Base64-encode images inline in markdown |
| `ignore_images` | `False` | Skip images entirely (faster) |
| `image_path` | `""` | Directory for saved images |
| `image_format` | `"png"` | Output format |
| `image_size_limit` | `0.05` | Skip images smaller than 5% of page area |
| `dpi` | `150` | Resolution for rasterized images |

### Layout Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `margins` | `0` | Can be int (all sides) or tuple `(left, top, right, bottom)`. Content overlapping margins is excluded. |
| `page_width` | `612` | 612pt = 8.5in (US Letter). Used when page layout is variable. |
| `page_height` | `None` | |
| `force_text` | `True` | Extract text even when it overlays an image background. Important for papers with watermarks/headers over images. |
| `fontsize_limit` | `3` | Minimum font size in points. Text smaller than this is excluded. |
| `ignore_code` | `False` | When True, suppresses backtick-wrapping of monospace font text |

### Output Format

| Parameter | Default | Notes |
|-----------|---------|-------|
| `page_chunks` | `False` | When True, returns `list[dict]` with `{"text": ..., "metadata": {"page": N}}` per page |
| `page_separators` | `False` | Insert `-----` page separator markers |
| `extract_words` | `False` | Include word-level bbox data in page chunks (for layout analysis) |

### Miscellaneous

| Parameter | Default | Notes |
|-----------|---------|-------|
| `graphics_limit` | `None` | If page has more vector graphics than this, ignore ALL graphics on that page. Safety valve for complex diagrams. |
| `show_progress` | `False` | Print progress per page |
| `use_glyphs` | `False` | Replace unmappable Unicode with glyph IDs (diagnostic) |
| `ignore_alpha` | `False` | Skip transparent text (alpha=0). Some PDFs have invisible text layers. |
| `detect_bg_color` | `True` | Detect page background color |

---

## IdentifyHeaders (Built-in Font-Size Detection)

**Location:** `pymupdf4llm/helpers/pymupdf_rag.py`

### Algorithm

1. Scans all selected pages, extracts every text span
2. Records rounded font size for each span, weighted by character count
3. Identifies the most frequent font size as "body text"
4. All font sizes larger than body text become potential header levels
5. Maps up to 6 largest distinct sizes to `# ` through `###### `

### Constructor

```python
IdentifyHeaders(
    doc,                    # pymupdf.Document or filename
    pages=None,             # Pages to analyze (default: all)
    body_limit=12,          # Force text >= this size as body text
    max_levels=6,           # Max header levels (1-6)
)
```

### Key Method

```python
def get_header_id(self, span: dict, page=None) -> str:
    # span must have "size" key (font size in points)
    # Returns "# ", "## ", etc. or "" if not a header
```

### Strengths
- Works on any PDF without prior knowledge
- Correctly handles multi-level hierarchies in well-formatted documents

### Weaknesses
- Relies on font size alone — bold text at body size won't be detected as headers
- Can be confused by documents with many font sizes (footnotes, captions, etc.)
- The `body_limit=12` default may not suit all documents

---

## TocHeaders (TOC-Based Detection)

**Location:** `pymupdf4llm/helpers/pymupdf_rag.py`

### Algorithm

1. Reads the document's Table of Contents on initialization
2. For each span, checks if the span's text matches any TOC entry on the same page
3. Uses forgiving matching: span text starts with TOC title OR TOC title starts with span text
4. Maps TOC hierarchy level directly to markdown header level

### Constructor

```python
TocHeaders(doc)  # pymupdf.Document or filename
```

### Key Method

```python
def get_header_id(self, span: dict, page=None) -> str:
    # span must have "text" key
    # page parameter is REQUIRED (unlike IdentifyHeaders)
    # Returns "# ", "## ", etc. or "" if not a match
```

### Strengths
- Very accurate for documents with a proper TOC
- Respects the document's own hierarchy
- Faster than IdentifyHeaders (no font scanning)

### Weaknesses
- Requires a well-formed TOC — many academic PDFs lack this
- The `page` parameter is required (must pass page object)
- Can miss headers not in the TOC

---

## Custom hdr_info Callback

Our current `_academic_header_detector` signature:

```python
def _academic_header_detector(span, page=None) -> str:
    """
    Args:
        span: dict with keys:
            "text": str     — span text content
            "size": float   — font size in points
            "flags": int    — font flags (bit 4 = bold)
            "font": str     — font name
            "bbox": tuple   — bounding box (x0, y0, x1, y1)
        page: pymupdf.Page | None — page object (has .number, .rect)

    Returns:
        "## ", "### ", etc. for headers
        "" for non-headers
    """
```

### Span flags bit field

| Bit | Value | Meaning |
|-----|-------|---------|
| 0 | 1 | Superscript |
| 1 | 2 | Italic |
| 2 | 4 | Serif |
| 3 | 8 | Monospace |
| 4 | 16 | **Bold** |

---

## Parameters to Explore in Experiments

### High Priority (likely impactful)

1. **`table_strategy`**: `"lines"` vs `"lines_strict"` vs `"text"` — verify old finding on expanded corpus
2. **`hdr_info`**: `None` (auto) vs custom vs `False` vs `TocHeaders` — compare header detection approaches
3. **`margins`**: May help exclude running headers/footers at source instead of in postprocessing

### Medium Priority

4. **`force_text`**: Default is `True`. Try `False` to see if it affects scanned-looking pages
5. **`image_size_limit`**: Default `0.05` (5% of page). May affect small equation images
6. **`graphics_limit`**: Could help with PDFs that have complex diagrams
7. **`fontsize_limit`**: Default `3`. Raising it might filter noise; lowering might capture subscripts

### Low Priority (unlikely to change much)

8. **`dpi`**: 150 is standard. Test 72 (speed) and 300 (quality) for image extraction
9. **`ignore_code`**: Might affect papers with code listings
10. **`page_chunks` vs `page_separators`**: Output format choice
11. **`use_glyphs`**: Diagnostic only
12. **`ignore_alpha`**: Unlikely relevant for academic papers

---

## Current Configuration (pymupdf_backend.py)

```python
chunks = to_markdown(
    str(input_path),
    write_images=True,
    image_path=str(images_dir),
    image_format="png",
    dpi=150,
    page_chunks=True,
    hdr_info=_academic_header_detector,   # Custom bold+numbering detector
    table_strategy="lines",               # NOT the default "lines_strict"
)
```

### Known Issues
- `table_strategy="lines"` overrides the better default `"lines_strict"`
- Custom `_academic_header_detector` only detects bold+numbered headers — misses non-bold headers and non-numbered sections
- No `margins` set — running headers/footers handled in postprocessing instead
- Default `image_size_limit=0.05` and `fontsize_limit=3` are untested

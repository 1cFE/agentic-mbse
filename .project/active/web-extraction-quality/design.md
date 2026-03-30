# Design: Web Extraction Quality — Tables, Images, HTML Fidelity

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-03-29
**Branch:** `webfetch-tools`
**Commit:** `693dcdc`

## Overview

Fix web extraction to produce usable markdown from technical HTML sources. The core issue: trafilatura strips sub/sup tags, loses MathML, and mangles table structure. The design adds site-aware routing, HTML pre-processing, image downloading, and markdown post-processing around the existing extraction engine.

## Related Artifacts

- **Spec:** `.project/active/web-extraction-quality/spec.md`
- **Web backend spec:** `.project/active/web-source-capture/spec.md`
- **Upstream epic:** `fusion-tea/.project/backlog/epic_source_extraction_fix.md`
- **Reference failure:** `fusion-tea/.../arxiv-2411-06644-confinement-predictions.md`
- **arXiv shortcut code:** `src/agentic_mbse/extraction/pandoc_convert.py`
- **Web backend:** `src/agentic_mbse/extraction/web_backend.py`
- **PDF pipeline (patterns):** `src/agentic_mbse/extraction/pipeline.py`
- **Postprocessing (patterns):** `src/agentic_mbse/extraction/postprocess.py`
- **HTML sanitize (patterns):** `src/agentic_mbse/extraction/html_sanitize.py`
- **Test fixture (arXiv HTML):** `tests/corpus/html/paischer_2025.html`
- **Real raw HTML files:** `fusion-tea/.../raw.html` (93+ files via `--save-source`)

---

## Research Findings

### The Core Problem

Trafilatura's `extract(output_format="markdown")` processes HTML through a text extraction pipeline that:
1. **Strips `<sub>`/`<sup>` tags** — `H<sub>2</sub>O` → `H 2 O` (lost semantics)
2. **Strips MathML** — `<math alttext="\beta">` → empty or garbled
3. **Mangles table cells with inline markup** — cells containing sub/sup/math become empty or misaligned
4. **No image downloading** — `include_images` exists but only affects XML output format

No trafilatura configuration option fixes these issues. They're fundamental to its text extraction approach.

### Pandoc: Already Proven

The arXiv shortcut in the PDF pipeline (`pandoc_convert.py:132-208`) already converts arXiv HTML to excellent markdown:
- Tables with math headers: `| $a_{m}$ [m] | $B_{m}$ [T] |` — correct structure
- Inline math: `$\beta$` — LaTeX preserved
- Display equations: `$$\frac{df}{dt} = C(f)$$` — block LaTeX
- Images: `![caption](path)` — references preserved

Flags: `-f html-native_divs-native_spans -t markdown-header_attributes --wrap=none --markdown-headings=atx`

### arXiv HTML Structure (LaTeXML)

arXiv uses LaTeXML to generate HTML. Key patterns:
- **Data tables**: `<table class="ltx_tabular ...">` with `<math alttext="...">` in headers/cells
- **Equation tables**: `<table class="ltx_equation ltx_eqn_table">` wrapping `<math display="block">`
- **Math elements**: Always have `alttext` attribute and `<annotation encoding="application/x-tex">` child
- **Images**: `<img src="extracted/NNNNNN/figure.png">` with relative paths

Detection: `<meta name="generator" content="LaTeXML">` or class `ltx_document`

### PDF Pipeline Patterns Worth Reusing

1. **Error isolation** (`pipeline.py:216-226`): Wrap optional steps in `try/except`, return empty on failure
2. **Pure function composition** (`postprocess.py:370-382`): Chain `str → str` transforms
3. **ImageCollector** (`pipeline.py:66-99`): Accumulate image metadata, defer persistence to end
4. **Module-level regex constants** (`postprocess.py:32-66`): Compile once, reuse
5. **Cascade/fallback** (`tables.py:510-540`): Try primary, fall back to secondary on failure

### Available Dependencies

Already installed: `beautifulsoup4`, `lxml`, `pandoc` (system binary), `trafilatura`
Available but unused: `latex2mathml` (v3.78.1), `pylatexenc`

---

## Design Concepts

### Concept A: Pandoc-First with Trafilatura Fallback

**Idea:** Reverse the current priority. Try Pandoc first (proven for scientific content), fall back to trafilatura only if Pandoc fails or produces poor results.

**Flow:**
```
HTML → sanitize → Pandoc → quality check → [if poor] → trafilatura → output
```

**Pros:**
- Pandoc handles all three failure cases (tables, math, equations) correctly out of the box
- Already proven in production (arXiv shortcut)
- Minimal new code — mostly reordering existing logic

**Cons:**
- Pandoc converts the ENTIRE HTML page including boilerplate (nav, footer, sidebar, ads)
- No content extraction intelligence — trafilatura is specifically designed to find "the article" in a page
- Would produce massive, noisy output for pages with lots of non-content HTML
- Quality check to decide "is Pandoc output good enough?" is hard to write

**Verdict:** Not viable as the primary path for general web pages. Pandoc is a format converter, not a content extractor.

### Concept B: Preprocess HTML + Trafilatura

**Idea:** Keep trafilatura as primary but add BeautifulSoup preprocessing to convert sub/sup/MathML to plaintext/Unicode before trafilatura ever sees the HTML. Trafilatura then extracts its text normally but the scientific content is already in a form it won't destroy.

**Flow:**
```
HTML → sanitize → preprocess(sub/sup→Unicode, MathML→LaTeX) → trafilatura → postprocess → output
```

**Pros:**
- Trafilatura still handles content extraction/boilerplate removal
- Preprocessing is a pure function, easy to test
- Follows the `html_sanitize.py` pattern already in the codebase
- Handles any HTML source, not just arXiv

**Cons:**
- Unicode sub/superscripts have limited character coverage (digits + some Latin letters only)
- Characters without Unicode equivalents (most Greek, special symbols) fall back to `_x`/`^x` notation
- MathML → inline LaTeX conversion is lossy for complex expressions
- May not fix table STRUCTURE issues (row alignment, column counting) — only fixes content within cells
- Preprocessing can interact unpredictably with trafilatura's content detection (it may see the Unicode as "not article text")

**Verdict:** Good for simple cases (digit subscripts/superscripts), insufficient for complex scientific tables where the structural alignment is also broken.

### Concept C: Trafilatura for Content Zone, Pandoc for Rendering

**Idea:** Use trafilatura to identify the main content area of the page (its core competency), extract that HTML fragment, then convert it with Pandoc (proven for scientific rendering).

**Flow:**
```
HTML → sanitize → trafilatura.bare_extraction() → get content HTML zone
     → Pandoc converts content HTML → postprocess → output
```

**Pros:**
- Best of both worlds: trafilatura's content detection + Pandoc's rendering fidelity
- Pandoc handles tables, math, equations, images correctly
- Content zone is clean (no nav/footer/sidebar boilerplate)

**Cons:**
- trafilatura's `bare_extraction()` doesn't expose the raw content HTML — it returns a Document object with text, not the intermediate HTML fragment
- Would need to either: (a) hack trafilatura internals, (b) use trafilatura's output to identify content boundaries then extract HTML ourselves, or (c) use a different content detection library
- Complexity of HTML zone detection + extraction is significant
- Fragile — content boundary detection varies by page structure

**Verdict:** Architecturally elegant but impractical without trafilatura exposing its content HTML.

### Concept D: Site-Aware Routing with Fallback Cascade

**Idea:** Detect the HTML generator/site type and route to the best backend. arXiv/LaTeXML → Pandoc (proven). Everything else → preprocessed trafilatura. Quality-check the result and fall back through alternatives.

**Flow:**
```
HTML → sanitize → detect site type
  ├─ LaTeXML/arXiv → Pandoc (with existing pre/post-process from pandoc_convert.py)
  ├─ Other technical (has <math>, complex <table>) → preprocess + trafilatura, fallback to Pandoc
  └─ General content → trafilatura (current behavior)
→ postprocess (list cleanup, image download) → output
```

**Pros:**
- Optimized path for the known-worst case (arXiv), which is the P0 blocker
- General HTML still gets trafilatura's content detection
- Fallback cascade means we try multiple approaches before giving up
- Extensible — can add more site-specific routes later (e.g., Wikipedia, PubMed)
- Follows the cascade pattern from `tables.py:510-540` (ensemble detection)

**Cons:**
- Site detection adds complexity
- Multiple code paths to maintain
- Non-arXiv scientific HTML (e.g., MDPI, Springer, IEEE) still goes through trafilatura with only preprocessing

**Verdict:** Best practical approach. Solves the P0 (arXiv) immediately and provides a framework for improving other sources.

### Concept E: Readability + Pandoc (Content Detection Without Trafilatura)

**Idea:** Replace trafilatura entirely with Mozilla's Readability algorithm (via `readability-lxml` or `readabilipy`) for content detection, then Pandoc for conversion. Readability identifies the main content DOM subtree and returns clean HTML, which Pandoc then converts.

**Flow:**
```
HTML → sanitize → readability (extract content HTML subtree) → Pandoc → postprocess → output
```

**Pros:**
- Readability returns actual HTML, not text — preserves all tags including math/tables
- Pandoc converts the clean content HTML with full fidelity
- Readability is battle-tested (Firefox Reader View uses it)
- Clean two-stage pipeline: content detection → format conversion

**Cons:**
- New dependency (`readability-lxml` or `readabilipy`)
- Readability may strip some content that trafilatura would keep (different heuristics)
- Less mature than trafilatura for academic/technical content
- Would need validation against existing test cases

**Verdict:** Promising alternative to Concept D but introduces a new dependency and unknown content detection quality. Worth prototyping.

---

## Design Decision: Routing Strategy

**Recommendation: Concept D (Site-Aware Routing) with elements of Concept B (Preprocessing)**

Rationale:
1. **Solves P0 immediately**: arXiv/LaTeXML → Pandoc is already proven, just needs wiring
2. **Low risk for general HTML**: Preprocessing + trafilatura improves quality without changing the engine
3. **Fallback cascade**: If the primary path produces poor results, try alternatives
4. **Extensible**: New site types can be added as detection rules
5. **Follows established patterns**: Cascade from `tables.py`, preprocessing from `html_sanitize.py`, error isolation from `pipeline.py`

**What I'd like your input on:**

1. Should we add `readability-lxml` as an optional dependency for Concept E as a future enhancement, or keep the dependency surface minimal for now?
2. For non-arXiv scientific HTML, is preprocessing + trafilatura sufficient, or should Pandoc be the universal fallback for any page with `<math>` elements?
3. For image downloading: should we also convert Pandoc's `![](extracted/NNNN/fig.png)` image references (relative to arxiv CDN) to downloaded local images, or leave them as remote URLs?

---

## Proposed Design

### Architecture Overview

```
extract_web_content(url)
  │
  ├─ Step 1: Fetch HTML                    [existing - http.py]
  ├─ Step 2: Sanitize                      [existing - html_sanitize.py]
  ├─ Step 3: Detect site type              [NEW - web_preprocess.py]
  ├─ Step 4: Route to extraction backend
  │    ├─ LaTeXML → _extract_with_pandoc() [NEW - web_backend.py]
  │    ├─ Technical → preprocess + trafilatura, fallback pandoc [MODIFIED]
  │    └─ General → trafilatura            [existing]
  ├─ Step 5: Post-process markdown         [NEW - web_postprocess.py]
  ├─ Step 6: Download images               [NEW - web_images.py]
  └─ Step 7: Write output                  [existing - web_backend.py]
```

### Component 1: Site Detection & HTML Pre-processing

**File:** `src/agentic_mbse/extraction/web_preprocess.py` (NEW)

**Purpose:** Detect HTML generator/site type and pre-process HTML for extraction.

```python
"""HTML pre-processing for web extraction.

Detects site/generator type (LaTeXML, generic) and pre-processes
HTML to preserve scientific content through extraction backends.
Follows the multi-layer pattern from html_sanitize.py.
"""

from __future__ import annotations
from enum import Enum

class SiteType(str, Enum):
    LATEXTML = "latextml"       # arXiv, other LaTeXML-generated pages
    TECHNICAL = "technical"     # Has <math>, complex tables, but not LaTeXML
    GENERAL = "general"         # Standard web content


def detect_site_type(html: str) -> SiteType:
    """Detect HTML generator/site type for routing.

    Detection rules (checked in order):
    1. LaTeXML meta generator tag → LATEXTML
    2. ltx_document class → LATEXTML
    3. <math> elements or MathJax/KaTeX scripts → TECHNICAL
    4. Everything else → GENERAL

    Uses string matching (not BS4 parsing) for speed — this runs
    on every URL extraction.
    """

def preprocess_html(html: str, site_type: SiteType) -> str:
    """Pre-process HTML based on detected site type.

    For LATEXTML:
      - Strip <figure> wrappers (existing pattern from pandoc_convert.py:33-38)
      - Strip CSS transform wrappers (existing pattern from pandoc_convert.py:40-51)

    For TECHNICAL:
      - Convert <sub>/<sup> to Unicode where possible (digits, common letters)
      - Extract MathML alttext as $latex$ notation

    For GENERAL:
      - No pre-processing (trafilatura handles it)

    Returns modified HTML string (pure function).
    """

# Unicode maps for sub/sup conversion
_SUB_DIGITS = {str(i): chr(0x2080 + i) for i in range(10)}  # ₀₁₂₃₄₅₆₇₈₉
_SUB_LETTERS = {'a': 'ₐ', 'e': 'ₑ', 'i': 'ᵢ', 'm': 'ₘ', 'n': 'ₙ',
                'o': 'ₒ', 'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ',
                'x': 'ₓ'}
_SUB_SYMBOLS = {'+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎'}

_SUP_DIGITS = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
               '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
_SUP_SYMBOLS = {'+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
                'n': 'ⁿ', 'i': 'ⁱ'}

def _convert_sub_sup_to_unicode(html: str) -> str:
    """Convert <sub>/<sup> tags to Unicode equivalents.

    Characters without Unicode equivalents fall back to _x / ^x notation.
    Only processes tags — does not affect other HTML structure.
    """

def _extract_mathml_alttext(html: str) -> str:
    """Replace <math> elements with their alttext or x-tex annotation.

    arXiv MathML pattern:
      <math alttext="\\beta" class="ltx_Math">
        <semantics>
          <annotation encoding="application/x-tex">\\beta</annotation>
        </semantics>
      </math>

    Replacement:
      - display="block" → $$alttext$$
      - display="inline" or default → $alttext$

    Falls back to alttext attribute if <annotation> not found.
    """
```

**Key design decisions:**
- `detect_site_type()` uses **string matching** (not BeautifulSoup parsing) for speed. We just need to check for `LaTeXML` in a meta tag or `ltx_document` in a class.
- `preprocess_html()` for TECHNICAL uses BeautifulSoup (same pattern as `html_sanitize.py`).
- LaTeXML pre-processing reuses the exact patterns from `pandoc_convert.py:33-51` — these are proven.

### Component 2: Pandoc Extraction Path

**File:** `src/agentic_mbse/extraction/web_backend.py` (MODIFIED)

**New function:** `_extract_with_pandoc(html: str) -> str | None`

```python
def _extract_with_pandoc(html: str) -> str | None:
    """Convert HTML to markdown via Pandoc.

    Used as primary backend for LaTeXML/arXiv HTML and as fallback
    for technical content when trafilatura produces poor results.

    Pandoc flags match those in pandoc_convert.py:178-186 for consistency.
    Post-processes to remove LaTeXML artifacts (pandoc_convert.py:54-63).

    Returns markdown string or None on failure.
    """
```

This replaces the existing `_fallback_pandoc()` with a more capable version that includes the LaTeXML pre/post-processing from `pandoc_convert.py`.

**Modified `extract_web_content()` flow:**

```python
def extract_web_content(url, ...):
    # Steps 1-2: Fetch + Sanitize (unchanged)

    # Step 3: Detect site type
    site_type = detect_site_type(html)

    # Step 4: Route to backend
    if site_type == SiteType.LATEXTML:
        # Primary: Pandoc (proven for LaTeXML)
        preprocessed = preprocess_html(html, site_type)
        markdown = _extract_with_pandoc(preprocessed)
        backend = "pandoc-latextml"

        # Fallback: trafilatura if Pandoc fails
        if not markdown or len(markdown) < _MIN_CONTENT_LENGTH:
            markdown, metadata = _extract_with_trafilatura(html, final_url)
            backend = "trafilatura-fallback"

    elif site_type == SiteType.TECHNICAL:
        # Primary: preprocess + trafilatura
        preprocessed = preprocess_html(html, site_type)
        markdown, metadata = _extract_with_trafilatura(preprocessed, final_url)
        backend = "trafilatura"

        # Fallback: Pandoc if trafilatura result is poor
        if not markdown or len(markdown) < _MIN_CONTENT_LENGTH:
            markdown = _extract_with_pandoc(html)
            backend = "pandoc-fallback"

    else:  # GENERAL
        # Current behavior (unchanged)
        markdown, metadata = _extract_with_trafilatura(html, final_url)
        backend = "trafilatura"

        if not markdown or len(markdown) < _MIN_CONTENT_LENGTH:
            markdown = _extract_with_pandoc(html)
            backend = "pandoc-fallback"

    # Steps 5-7: postprocess, images, write (see below)
```

### Component 3: Markdown Post-processing

**File:** `src/agentic_mbse/extraction/web_postprocess.py` (NEW)

**Purpose:** Clean up markdown output from any backend. Pure `str → str` functions following the composition pattern from `postprocess.py:370-382`.

```python
"""Markdown post-processing for web extraction.

Pure str → str transforms applied after extraction backend runs.
Follows the composition pattern from postprocess.py.
"""

import re

# --- Module-level compiled regexes ---

# Duplicate bullet markers: "- \n• \ntext" or "-\n•\ntext"
_DUPLICATE_BULLET_RE = re.compile(
    r'^(\s*)-\s*\n\s*•\s*\n?',
    re.MULTILINE
)

# Orphaned bullet on its own line
_ORPHANED_BULLET_RE = re.compile(
    r'^(\s*)•\s*$\n',
    re.MULTILINE
)

# Pandoc attribute suffixes on images: {width="300" height="200"}
_IMG_ATTR_RE = re.compile(
    r'(!\[.*?\]\(.*?\))\{[^}]*\}',
)

# Table separator normalization: ensure proper |---|---| format
_TABLE_SEP_RE = re.compile(
    r'^\|[\s:|-]+\|$',
    re.MULTILINE
)

# Equation table artifacts from Pandoc: | (1) | or |  | (1) |
_EQUATION_NUMBER_ONLY_RE = re.compile(
    r'^\|\s*\|\s*\((\d+[a-z]?)\)\s*\|$',
    re.MULTILINE
)


def postprocess_web_markdown(md: str) -> str:
    """Apply all web-specific post-processing steps.

    Composition order matters:
    1. Fix list formatting (before other cleanup)
    2. Clean Pandoc artifacts (attribute suffixes)
    3. Normalize tables
    """
    md = fix_duplicate_bullets(md)
    md = fix_orphaned_bullets(md)
    md = strip_pandoc_image_attributes(md)
    md = normalize_table_separators(md)
    return md


def fix_duplicate_bullets(md: str) -> str:
    """Clean up '- \\n• \\n text' → '- text' patterns."""

def fix_orphaned_bullets(md: str) -> str:
    """Remove orphaned '•' on their own lines."""

def strip_pandoc_image_attributes(md: str) -> str:
    """Remove {width=... height=...} suffixes from image references."""

def normalize_table_separators(md: str) -> str:
    """Ensure table separator rows are valid markdown."""
```

### Component 4: Image Downloading

**File:** `src/agentic_mbse/extraction/web_images.py` (NEW)

**Purpose:** Download images referenced in HTML, save locally, rewrite markdown references. Follows the `ImageCollector` pattern from `pipeline.py:66-99`.

```python
"""Image downloading for web extraction.

Detects images in source HTML, downloads them, and rewrites
markdown references to use local paths. Follows the ImageCollector
pattern from pipeline.py.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse
import logging
import re

logger = logging.getLogger(__name__)

# Limits
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024   # 20 MB per image
MAX_TOTAL_SIZE_BYTES = 100 * 1024 * 1024   # 100 MB total

# Skip patterns
_SKIP_SCHEMES = frozenset({"data", "javascript"})
_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"})


@dataclass
class WebImage:
    """A detected image from HTML source."""
    original_url: str        # Resolved absolute URL
    local_filename: str      # Filename for local storage
    downloaded: bool = False
    error: str | None = None


@dataclass
class WebImageCollector:
    """Collect, download, and persist web images.

    Mirrors the ImageCollector pattern from pipeline.py but adapted
    for web URLs instead of local temp files.

    Usage:
        collector = WebImageCollector(output_dir=Path("output/images"))
        collector.detect_images(html, base_url)
        collector.download_all()
        markdown = collector.rewrite_references(markdown)
        count = collector.persist()
    """
    output_dir: Path
    images: list[WebImage] = field(default_factory=list)
    _total_bytes: int = 0

    def detect_images(self, html: str, base_url: str) -> None:
        """Parse HTML for <img> tags, resolve URLs, build download list.

        Detects from SOURCE HTML (not markdown output) to capture all
        images including those trafilatura may filter.

        Skips: data: URIs, javascript: URIs, duplicate URLs.
        """

    def download_all(self, timeout: int = 15) -> int:
        """Download all detected images. Returns count of successes.

        Uses fetch_url() from http.py for consistent User-Agent/timeout.
        Respects per-image and total size limits.
        Individual failures are logged but don't stop other downloads.
        """

    def rewrite_references(self, markdown: str) -> str:
        """Rewrite image URLs in markdown to local paths.

        Replaces original URLs (and relative paths) with images/filename.
        Only rewrites images that were successfully downloaded.
        """

    def persist(self) -> int:
        """Ensure output_dir exists and return count of downloaded images.

        Downloads are written directly to output_dir during download_all(),
        so persist() just handles directory creation and returns count.
        """

    @property
    def image_count(self) -> int:
        """Count of successfully downloaded images."""
        return sum(1 for img in self.images if img.downloaded)
```

**Key design decisions:**
- Detect images from **source HTML** (not markdown output) — more reliable, catches images trafilatura might filter
- Download sequentially — simplest; can add concurrency later if needed
- Use existing `fetch_url()` from `http.py` for consistent behavior
- `rewrite_references()` is a pure function on the markdown string — can be tested independently
- Error isolation per image — one broken image doesn't fail the extraction

**Image URL resolution:**
```python
def _resolve_image_url(src: str, base_url: str) -> str | None:
    """Resolve image src against base URL.

    Handles:
    - Absolute URLs: https://example.com/img.png → pass through
    - Protocol-relative: //cdn.example.com/img.png → add https:
    - Relative: extracted/5986138/fig.png → urljoin(base_url, src)
    - data: URIs → skip (return None)
    - javascript: → skip (return None)
    """
```

**Filename generation:**
```python
def _image_filename(url: str, index: int) -> str:
    """Generate local filename from URL.

    Strategy: use original filename if clean, otherwise img_NNN.ext.
    Avoids collisions by prepending index.

    Examples:
        https://arxiv.org/extracted/5986138/wham_ions.png → wham_ions.png
        https://cdn.example.com/assets/a/b/c.jpg?v=123  → img_003_c.jpg
    """
```

### Component 5: Integration into `extract_web_content()`

**File:** `src/agentic_mbse/extraction/web_backend.py` (MODIFIED)

The main function gains three new stages. Backward-compatible — all new parameters have defaults that preserve current behavior.

```python
def extract_web_content(
    url: str,
    *,
    output_dir: Path | None = None,
    sanitize: bool = True,
    save_source: bool = False,
    no_frontmatter: bool = False,
    timeout: int = 30,
    download_images: bool = True,     # NEW — default True
) -> ExtractionResult:
    """Extract web page content to structured markdown.

    Pipeline: fetch → sanitize → detect → route → extract → postprocess
              → download images → write output.
    """
    # Steps 1-2: Fetch + Sanitize (unchanged)
    # save_source saves ORIGINAL html (before preprocess), per FR-16
    original_html = html

    if sanitize:
        html = strip_hidden_content(html)

    # Step 3: Detect site type (NEW)
    site_type = detect_site_type(html)

    # Step 4: Route + Extract (NEW routing logic — see Component 2)
    # ... (sets markdown, metadata, backend)

    # Step 5: Post-process markdown (NEW)
    markdown = postprocess_web_markdown(markdown)

    # Step 6: Download images (NEW)
    image_count = 0
    if download_images:
        img_dir = output_dir / "images"
        collector = WebImageCollector(output_dir=img_dir)
        collector.detect_images(original_html, final_url)
        collector.download_all(timeout=timeout)
        markdown = collector.rewrite_references(markdown)
        collector.persist()
        image_count = collector.image_count

    # Step 7: Write output (existing, but with image_count)
    # ...
    return ExtractionResult(
        ...,
        image_count=image_count,  # was hardcoded 0
        backend_used=backend,
    )
```

### File Summary

| File | Status | Purpose |
|------|--------|---------|
| `extraction/web_preprocess.py` | NEW | Site detection, HTML pre-processing (sub/sup, MathML) |
| `extraction/web_postprocess.py` | NEW | Markdown post-processing (lists, tables, cleanup) |
| `extraction/web_images.py` | NEW | Image detection, downloading, path rewriting |
| `extraction/web_backend.py` | MODIFIED | Integrate routing, pre/post-processing, images |
| `tests/test_web_preprocess.py` | NEW | Site detection + preprocessing tests |
| `tests/test_web_postprocess.py` | NEW | Markdown cleanup tests |
| `tests/test_web_images.py` | NEW | Image download tests (mocked HTTP) |
| `tests/fixtures/arxiv_table.html` | NEW | Sample arXiv table HTML fragment |

---

## Potential Risks

### Risk 1: Pandoc Not Available
**Impact:** LaTeXML routing falls through to trafilatura (still broken)
**Mitigation:** Already handled — `shutil.which("pandoc")` check exists. Log warning when Pandoc is missing but LaTeXML detected. Consider adding Pandoc availability to the `--check` output.

### Risk 2: Preprocessing Breaks Trafilatura Content Detection
**Impact:** Trafilatura may not recognize the article body if HTML is modified
**Mitigation:** Only preprocess for TECHNICAL site type (not GENERAL). Preprocessing targets only `<sub>`/`<sup>`/`<math>` tags — unlikely to affect trafilatura's content boundary detection. Test with the arXiv and Wikipedia fixtures.

### Risk 3: Image Download Performance
**Impact:** Many images could slow extraction significantly
**Mitigation:** Per-image timeout (15s), total size cap (100MB), sequential download. Can add concurrency later if needed. Skip `data:` URIs (can be multi-MB).

### Risk 4: Pandoc Output Too Noisy for Non-arXiv Pages
**Impact:** Pandoc converts entire page HTML including boilerplate
**Mitigation:** Pandoc is only the PRIMARY backend for LaTeXML pages (which are mostly article content). For other pages, it's only the FALLBACK when trafilatura fails. The quality threshold (`_MIN_CONTENT_LENGTH`) gates fallback activation.

### Risk 5: Unicode Sub/Sup Incomplete Coverage
**Impact:** Characters without Unicode equivalents (most Greek, many symbols) fall back to `_x`/`^x`
**Mitigation:** For LaTeXML (where this matters most), we use Pandoc which preserves LaTeX notation. Unicode conversion is only for the TECHNICAL path where it's a best-effort improvement.

---

## Integration Strategy

This design integrates at a single point: `extract_web_content()` in `web_backend.py`. No changes to:
- PDF pipeline (`pipeline.py`)
- Existing arXiv shortcut (`pandoc_convert.py`)
- HTML sanitization (`html_sanitize.py`)
- CLI dispatch (`extract_cli.py`)
- Frontmatter system (`frontmatter.py`)

The new modules (`web_preprocess.py`, `web_postprocess.py`, `web_images.py`) are independently importable and testable. They have no dependencies on each other.

---

## Validation Approach

### Unit Tests (no network)

1. **`test_web_preprocess.py`**:
   - `test_detect_latextml()` — LaTeXML meta tag detection
   - `test_detect_technical()` — `<math>` element detection
   - `test_detect_general()` — no special markers
   - `test_sub_sup_unicode()` — digit conversion (₀₁₂, ⁰¹²)
   - `test_sub_sup_fallback()` — non-digit characters (_x, ^x)
   - `test_mathml_alttext()` — inline `$...$` and display `$$...$$`

2. **`test_web_postprocess.py`**:
   - `test_fix_duplicate_bullets()` — `- \n• \n` → `- `
   - `test_fix_orphaned_bullets()` — standalone `•` removal
   - `test_strip_pandoc_image_attrs()` — `{width=...}` removal
   - `test_normalize_table_separators()` — ensure valid `|---|` format

3. **`test_web_images.py`** (mocked HTTP):
   - `test_detect_images_from_html()` — finds `<img>` tags
   - `test_resolve_relative_urls()` — relative → absolute
   - `test_skip_data_uris()` — data: URIs skipped
   - `test_rewrite_references()` — markdown URL replacement
   - `test_size_limits()` — per-image and total caps respected
   - `test_download_failure_isolation()` — one failure doesn't stop others

### Integration Tests (with fixtures)

4. **`test_web_backend.py`** (existing file, add tests):
   - `test_extract_arxiv_tables()` — use `tests/corpus/html/paischer_2025.html` fixture
   - Verify tables have correct column count and header content
   - Verify math rendered as `$...$` notation
   - Verify images referenced in markdown

### Manual Validation

5. **Primary acceptance test**: Extract `https://arxiv.org/html/2411.06644v1` and verify:
   - Table 1: 5 columns, 4 data rows, `⟨n_p⟩` header present
   - Table 3: Parameter names in first column, values aligned
   - Equations: LaTeX content visible (not just `| (1) |`)
   - Images: downloaded to `images/` directory

---

**Next Step:** After approval → `/_my_plan` (this spans 3+ new modules, warrants a phased plan)

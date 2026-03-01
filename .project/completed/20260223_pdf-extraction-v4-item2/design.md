# Design: PDF Extraction Pipeline v4 — Item 2: Enhancement Components

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-23 17:55 PST
**Branch:** `doc-ingest-clean`
**Commit:** c8242a7

---

## Overview

Build the 4 enhancement modules (+ 1 refactor) that provide concrete actions for the pipeline's routing decisions. This design translates Stage 3 experiment implementations and the concept design (§4.2-4.6) into production code, specifying exact reuse points, integration patterns, and implementation details.

## Related Artifacts

- **Spec:** `.project/active/pdf-extraction-v4-item2/spec.md`
- **Concept Design:** `.project/concepts/doc-extraction/design.md` (§4.2-4.6, §11, §13)
- **Requirements:** `.project/concepts/doc-extraction/requirements.md` (FR-2 through FR-6)
- **Epic:** `.project/backlog/epic_pdf-extraction-v4.md` (Item 2)
- **Item 1 Deliverables:** `types.py`, `metrics.py`, `quality_gate.py`, `pipeline.py`
- **Stage 3 Reference:** `tests/corpus/pipelines/shared.py`, `h6_pandoc_shortcut.py`, `h3_pymupdf_claude_eq.py`, `track1_cropped_extraction.py`

---

## Research Findings

### Existing Code to Reuse

| Source | What | Target |
|--------|------|--------|
| `shared.py:180-208` | `extract_pymupdf_pages()` — per-page extraction with `BEST_V1_PARAMS` and page_chunks=True | `pymupdf_backend.py:extract_pages()` |
| `shared.py:216-274` | `extract_gmft_pages()` — GMFT detection with DataFrame extraction and avg_cell_length | `tables.py:_detect_gmft()` |
| `shared.py:282-320` | `filter_gmft_tables()` — confidence, prose, layout artifact filters | `tables.py:filter_tables()` |
| `shared.py:335-430` | Table utilities: `_is_table_row`, `strip_pipe_tables`, `replace_tables`, `insert_tables_at_end`, `has_br_in_tables`, `has_col_headers`, `count_pipe_rows` | `tables.py` (utilities section) |
| `ai_repair.py:122-143` | `render_page_image()` — pymupdf page → PNG | `claude_enhance.py:render_page_image()` |
| `track1_cropped_extraction.py:80-155` | `invoke_claude()` + `extract_table_with_claude()` — Claude CLI JSON invocation, cost extraction | `claude_enhance.py:invoke_claude()`, `tables.py:enhance_table_with_claude()` |
| `h3_pymupdf_claude_eq.py:80-100` | Same `invoke_claude()` pattern for page-level extraction | `claude_enhance.py:extract_page_with_claude()` |
| `h6_pandoc_shortcut.py:78-144` | `preprocess_html()`, `postprocess_markdown()`, `run_pandoc()` — full Pandoc pipeline | `pandoc_convert.py` |
| `prompts/extract_baseline.txt` | Full-page extraction prompt (20 lines) | `claude_enhance.py:_PAGE_EXTRACTION_PROMPT` constant |
| `prompts/extract_table_cropped.txt` | Table extraction prompt (7 lines) | `tables.py:_TABLE_EXTRACTION_PROMPT` constant |

### API Details Discovered

**Img2Table** (from gmft package — available, never used in experiments):
- Import: `from gmft.detectors.img2table import Img2TableDetector, Img2TableDetectorConfig`
- Config: `Img2TableDetectorConfig(borderless_tables=True)` — the `borderless_tables` param is on the config, not the constructor
- API: `detector.detect(page)` → `list[CroppedTable]` (same interface as `AutoTableDetector`)
- Formatting: `AutoTableFormatter.extract(cropped_table)` works with Img2Table's `CroppedTable` output
- `CroppedTable.confidence_score` defaults to 1.0 (Img2Table doesn't produce confidence scores)

**CroppedTable image saving:**
- `CroppedTable.image(dpi=200)` → PIL Image
- Save via `pil_image.save(path)` — standard PIL

**Claude CLI JSON output:**
- `claude -p --output-format json` returns: `{"result": "...", "total_cost_usd": 0.078, "usage": {"input_tokens": N, "output_tokens": N}, "model": "..."}`
- Must unset `CLAUDECODE` env var to avoid nested session guard
- Flags: `--dangerously-skip-permissions --no-session-persistence --allowedTools Read`

### Key Patterns from Item 1

- `quality_gate.py` has private helpers `_has_col_headers()`, `_has_br_in_tables()`, `_has_pipe_tables()` (lines 205-227) — these duplicate what `tables.py` will provide as public utilities. After `tables.py` exists, quality_gate.py should import from it (deferred to Item 3 wiring).
- `types.py:DetectedTable` has all fields needed: `markdown`, `confidence`, `num_rows`, `num_cols`, `avg_cell_length`, `image_path`, `extraction_failed`, `detector`, `source`
- `types.py:CostRecord` has `table_index: int | None` for distinguishing page-level vs table-level costs

### Confidence Filter Change

The Stage 3 `shared.py:filter_gmft_tables()` (line 303) still has `confidence < 0.98` filter. The table spike v2 findings proved this rejects 7 real tables on aries (10/11 filtered detections were real). **The production `filter_tables()` MUST NOT have a confidence filter.** Only prose cell length and layout artifact filters are retained.

---

## Proposed Design

### Architecture

```
pymupdf_backend.py                    tables.py
  extract_pages() ──→ list[PageResult]    detect_tables_ensemble()
                                           ├── _detect_gmft()
                                           ├── _detect_img2table()
                                           └── _detect_docling()
                                          filter_tables()
                                          assess_table_quality()
                                          enhance_table_with_claude()
                                          ─── table markdown utilities ───

pandoc_convert.py                     claude_enhance.py
  detect_arxiv_id()                     render_page_image()
  check_arxiv_html()                    extract_page_with_claude()
  convert_arxiv_html()                  validate_claude_output()
                                        invoke_claude()  [package-internal helper]
```

All four modules import from `types.py` (Item 1). One cross-import exists: `tables.py` imports `invoke_claude` from `claude_enhance.py` (a package-internal mechanical helper — see §2d). The pipeline orchestrator (Item 3) wires them together.

### Component 1: `pymupdf_backend.py` — Add `extract_pages()`

**Location:** `src/agentic_mbse/extraction/pymupdf_backend.py` (add ~30 lines)

**What changes:** Add one new function after the existing `extract()` function. No changes to `extract()`, `CompositeHeaderDetector`, or `_bold_header_detector`.

```python
def extract_pages(pdf_path: Path) -> list[PageResult]:
    """Extract per-page markdown using pymupdf4llm with BEST_V1 config.

    Uses page_chunks=True for per-page output with full-document header
    calibration (IdentifyHeaders scans all pages for font statistics).

    Does NOT call postprocess() — see design.md §2.4 for rationale.

    Returns list of PageResult, 0-indexed page numbers.
    """
```

**Implementation pattern** — direct translation of `shared.py:extract_pymupdf_pages()` (lines 180-208):

1. Call `_get_to_markdown()` (existing lazy import, line 19-23)
2. Pass same params as `extract()` line 135-151, but:
   - `write_images=False` (no image files needed)
   - `page_chunks=True` (already used by extract())
   - `hdr_info=_composite_header_detector` (existing singleton, line 120)
   - Same `table_strategy="lines"`, `ignore_code=True`, `dpi=150`
   - Add `force_text=True` (matches BEST_V1_PARAMS in shared.py:175)
3. Convert chunks to `list[PageResult]` — `chunk["metadata"]["page"] - 1` for 0-indexed page numbers
4. Import `PageResult` from `types.py`

**New import at top of file:**
```python
from agentic_mbse.extraction.types import PageResult
```

**Intentional differences from `extract()`:**
- No `postprocess()` call (see concept design §2.4 — Stage 3 experiments did not use postprocess)
- No image writing, no `ExtractionResult` wrapping, no output directory — pure data function
- **`force_text=True`** is added (matching `BEST_V1_PARAMS` in `shared.py:175`). The existing `extract()` does NOT pass `force_text`. This means `extract_pages()` will include text from form fields and annotations that `extract()` may omit. This is intentional: the Stage 3 experiments that proved the pipeline's quality all used `force_text=True`, so the production pipeline must match. The legacy `extract()` function is preserved as-is for backward compatibility with `--backend pymupdf`.

### Component 2: `tables.py` — Ensemble Table Detection and Enhancement

**Location:** `src/agentic_mbse/extraction/tables.py` (new, ~400 lines)

**Structure:**

```
tables.py
├── Constants & prompts
├── Ensemble detection
│   ├── detect_tables_ensemble()        [public entry point]
│   ├── _detect_gmft()                  [from shared.py:216-274]
│   ├── _detect_img2table()             [new — API discovered above]
│   └── _detect_docling()               [stub — returns empty dict]
├── Filtering & quality
│   ├── filter_tables()                 [from shared.py:282-320, no confidence filter]
│   └── assess_table_quality()          [new — extraction_failed + suspect triggers]
├── Enhancement
│   └── enhance_table_with_claude()     [from track1:123-155, adapted]
└── Table markdown utilities
    ├── strip_pipe_tables()             [from shared.py:382-408]
    ├── replace_tables()                [from shared.py:423-429]
    ├── insert_tables_at_end()          [from shared.py:411-420]
    ├── has_br_in_tables()              [from shared.py:362-367]
    ├── has_col_headers()               [from shared.py:370-379]
    └── count_pipe_rows()               [from shared.py:345-351]
```

#### 2a. `detect_tables_ensemble()`

```python
def detect_tables_ensemble(
    pdf_path: Path,
    save_images: bool = True,
    enable_img2table: bool = True,
    enable_docling: bool = False,
) -> dict[int, list[DetectedTable]]:
```

Orchestrates the three detectors in sequence. Returns merged dict of page → tables.

**GMFT detection** (`_detect_gmft`): Translates `shared.py:extract_gmft_pages()` (lines 216-274), with these changes:
- Returns `dict[int, list[DetectedTable]]` instead of `dict[int, list[GmftTable]]`
- Sets `DetectedTable.extraction_failed=True` when `df is None or df.empty` (instead of `continue`)
- Saves cropped table images via `cropped_table.image(dpi=200).save(path)` when `save_images=True`
- Sets `DetectedTable.image_path` to saved image path
- Sets `DetectedTable.confidence = table.confidence_score`
- Uses copied `_dataframe_to_pipe_table()` for DataFrame → pipe table conversion (copied from `table_extraction.py:57-79` — see Implementation Notes re: copy vs import)
- **Caches detector and formatter as module-level singletons** (`_gmft_detector`, `_gmft_formatter`) matching the pattern in `table_extraction.py:27-44`. AutoTableDetector has a ~1-2 second model initialization cost that should not repeat per call.

**Per-page error isolation (NFR-EXT-2):** The outer page loop wraps each page in `try/except Exception`. A crash on page N logs a warning and continues to page N+1. This is critical because GMFT can fail on individual malformed pages without invalidating the whole document.

```python
def _detect_gmft(pdf_path: Path, save_images: bool = True) -> dict[int, list[DetectedTable]]:
    try:
        from gmft.auto import AutoTableDetector, AutoTableFormatter
        from gmft.pdf_bindings.pdfium import PyPDFium2Document
    except ImportError:
        return {}

    global _gmft_detector, _gmft_formatter
    if _gmft_detector is None:
        _gmft_detector = AutoTableDetector()
        _gmft_formatter = AutoTableFormatter()

    doc = PyPDFium2Document(str(pdf_path))
    result: dict[int, list[DetectedTable]] = {}
    try:
        for page_idx in range(len(doc)):
            try:  # Per-page isolation
                page = doc.get_page(page_idx)
                tables = _gmft_detector.extract(page)
                if not tables:
                    continue
                page_tables = []
                for table in tables:
                    # ... per-table try/except (same as shared.py)
                    ...
                if page_tables:
                    result[page_idx] = page_tables
            except Exception as exc:
                logger.warning(f"GMFT failed on page {page_idx}: {exc}")
                continue
    finally:
        doc.close()
    return result
```

**Where to save images:** Create a temp directory per call (`tempfile.mkdtemp(prefix="gmft_")`) and save images as `page_{page_num:03d}_table_{idx}.png`. The pipeline orchestrator is responsible for cleanup (Item 3).

**Img2Table detection** (`_detect_img2table`): New implementation using the API discovered above.

Same per-page error isolation pattern as `_detect_gmft()`: outer page loop wraps each page in `try/except Exception`.

```python
def _detect_img2table(
    pdf_path: Path,
    gmft_pages: set[int],
    save_images: bool = True,
) -> dict[int, list[DetectedTable]]:
    try:
        from gmft.detectors.img2table import Img2TableDetector, Img2TableDetectorConfig
        from gmft.auto import AutoTableFormatter
        from gmft.pdf_bindings.pdfium import PyPDFium2Document
    except ImportError:
        return {}

    config = Img2TableDetectorConfig(borderless_tables=True)
    detector = Img2TableDetector(config)
    formatter = AutoTableFormatter()

    doc = PyPDFium2Document(str(pdf_path))
    result: dict[int, list[DetectedTable]] = {}
    try:
        for page_idx in range(len(doc)):
            if page_idx in gmft_pages:
                continue  # Skip pages where GMFT already found tables
            try:  # Per-page isolation (NFR-EXT-2)
                page = doc.get_page(page_idx)
                tables = detector.detect(page)
                # ... same per-table extraction pattern as _detect_gmft
                # Set detector="img2table" on DetectedTable
                # confidence_score defaults to 1.0 (Img2Table doesn't provide confidence)
            except Exception as exc:
                logger.warning(f"Img2Table failed on page {page_idx}: {exc}")
                continue
    finally:
        doc.close()
    return result
```

**Docling detection** (`_detect_docling`): Stub returning empty dict. Full implementation requires MCP server integration (out of scope per spec).

```python
def _detect_docling(pdf_path: Path, covered_pages: set[int]) -> dict[int, list[DetectedTable]]:
    # Docling MCP integration — future work
    return {}
```

#### 2b. `filter_tables()`

Translates `shared.py:filter_gmft_tables()` (lines 282-320) with these changes:
- **No confidence filter** (the key change from Stage 3 → production)
- Operates on `list[DetectedTable]` instead of `list[GmftTable]`
- Tables with `extraction_failed=True` pass through without filtering (no DataFrame to assess)

```python
def filter_tables(tables: list[DetectedTable]) -> tuple[list[DetectedTable], list[str]]:
    kept, reasons = [], []
    for i, table in enumerate(tables):
        tag = f"table {i+1} ({table.num_rows}r×{table.num_cols}c, detector={table.detector})"
        if table.extraction_failed:
            kept.append(table)  # Pass through for Claude enhancement
            reasons.append(f"PASS {tag}: extraction_failed (needs Claude)")
            continue
        if table.avg_cell_length > 80:
            reasons.append(f"REJECT {tag}: avg cell {table.avg_cell_length:.0f} > 80 (prose)")
            continue
        if table.num_rows == 1 and table.num_cols > 4:
            reasons.append(f"REJECT {tag}: single row, {table.num_cols} cols (layout artifact)")
            continue
        kept.append(table)
        reasons.append(f"KEEP {tag}")
    return kept, reasons
```

#### 2c. `assess_table_quality()`

New function — no direct experiment equivalent (the table spike did this manually).

```python
def assess_table_quality(table: DetectedTable) -> tuple[bool, list[str]]:
    """Assess whether a detected table needs Claude enhancement.

    Primary trigger: extraction_failed=True
    Secondary trigger: suspect quality (very few rows, garbled columns)

    Returns (needs_enhancement, reasons).
    """
    reasons = []
    if table.extraction_failed:
        reasons.append("Extraction failed: detector found table but DataFrame was null/empty")
        return True, reasons
    if table.image_path is None:
        return False, []  # Can't enhance without image
    # Suspect: very few data rows for a table that was detected
    if table.num_rows <= 1 and table.num_cols >= 3:
        reasons.append(f"Suspect: only {table.num_rows} row(s) with {table.num_cols} columns")
        return True, reasons
    return False, []
```

#### 2d. `enhance_table_with_claude()`

Translates `track1_cropped_extraction.py:extract_table_with_claude()` (lines 123-155).

```python
def enhance_table_with_claude(
    table: DetectedTable,
    model: str = "sonnet",
    timeout: int = 120,
) -> tuple[DetectedTable, CostRecord]:
```

Uses `invoke_claude()` from `claude_enhance.py` (shared helper, see Component 4). Constructs prompt using `_TABLE_EXTRACTION_PROMPT` constant (embedded from `prompts/extract_table_cropped.txt`).

**Key behavior:** When Claude returns empty/0-row output → return `DetectedTable(markdown="", ...)` — the caller treats this as a confirmed false positive.

**Import:** `from agentic_mbse.extraction.claude_enhance import invoke_claude`

This is the ONE cross-import between Item 2 modules: `tables.py` imports `invoke_claude` from `claude_enhance.py`. The function is public (no leading underscore) because it is intentionally shared within the extraction package. It is a mechanical CLI helper, not domain logic — the table-specific prompt and behavior live in `tables.py`.

#### 2e. Table Markdown Utilities

Direct translations from `shared.py:335-430`. The type signature changes from `GmftTable` to `DetectedTable`:

```python
def strip_pipe_tables(markdown: str) -> str: ...     # shared.py:382-408
def replace_tables(page_md: str, tables: list[DetectedTable]) -> str: ...  # shared.py:423-429
def insert_tables_at_end(page_md: str, tables: list[DetectedTable]) -> str: ...  # shared.py:411-420
def has_br_in_tables(markdown: str) -> bool: ...      # shared.py:362-367
def has_col_headers(markdown: str) -> bool: ...        # shared.py:370-379
def count_pipe_rows(markdown: str) -> int: ...         # shared.py:345-351
```

Also include the private helper `_is_table_row()` (shared.py:335-342) used by `strip_pipe_tables()`.

### Component 3: `pandoc_convert.py` — arXiv Detection and Conversion

**Location:** `src/agentic_mbse/extraction/pandoc_convert.py` (new, ~120 lines)

**Structure:**
```
pandoc_convert.py
├── detect_arxiv_id(pdf_path) → str | None
├── check_arxiv_html(arxiv_id) → str | None
├── convert_arxiv_html(html_source, pandoc_path) → str
├── _preprocess_html(html) → str          [from h6:78-92]
├── _postprocess_markdown(md) → str       [from h6:95-106]
└── _pandoc_available() → bool
```

#### 3a. `detect_arxiv_id()`

**New implementation** — the experiment used `papers.jsonl` lookup, but production needs to detect from the PDF itself (per design §4.2).

```python
def detect_arxiv_id(pdf_path: Path) -> str | None:
    """Extract arXiv ID from PDF page 1 text.

    Sequence:
    1. pymupdf page 1 text extraction
    2. Regex: arXiv:\d{4}\.\d{4,5}(v\d+)?
    3. Fallback: check PDF Creator metadata for 'arXiv'
    """
    import pymupdf
    doc = pymupdf.open(str(pdf_path))
    try:
        if len(doc) == 0:
            return None
        page_text = doc[0].get_text()
        # Primary: regex on page 1 text
        m = re.search(r"arXiv:(\d{4}\.\d{4,5}(?:v\d+)?)", page_text)
        if m:
            return m.group(1)
        # Fallback: PDF Creator metadata
        metadata = doc.metadata or {}
        creator = metadata.get("creator", "")
        if "arxiv" in creator.lower():
            # Try to find ID in full document text (first 2 pages)
            for i in range(min(2, len(doc))):
                text = doc[i].get_text()
                m = re.search(r"arXiv:(\d{4}\.\d{4,5}(?:v\d+)?)", text)
                if m:
                    return m.group(1)
        return None
    finally:
        doc.close()
```

#### 3b. `check_arxiv_html()`

```python
def check_arxiv_html(arxiv_id: str) -> str | None:
    """Check if arXiv HTML is available. Returns URL or None."""
    import urllib.request
    url = f"https://arxiv.org/html/{arxiv_id}"
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", "agentic-mbse/0.1 (PDF extraction pipeline)")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return url
    except Exception:
        pass
    return None
```

The `User-Agent` header avoids potential rate-limiting or blocking by arXiv infrastructure. The same header should be used in `convert_arxiv_html()` when downloading HTML from a URL.

#### 3c. `convert_arxiv_html()`

Translates `h6_pandoc_shortcut.py:78-144`. Accepts either URL or local path. Downloads URL to temp file if needed.

```python
def convert_arxiv_html(
    html_source: str | Path,
    pandoc_path: str = "pandoc",
) -> str:
    """Convert arXiv HTML to markdown via Pandoc.

    Args:
        html_source: URL or local file path.
        pandoc_path: Path to pandoc binary.

    Returns clean markdown. Raises subprocess.CalledProcessError on Pandoc failure.
    """
```

Steps:
1. If `html_source` is a URL, download to temp file (urllib)
2. Read HTML, run `_preprocess_html()` (from h6:78-92)
3. Write preprocessed HTML to temp file
4. Run Pandoc: `pandoc -f html-native_divs-native_spans -t markdown-header_attributes --wrap=none --markdown-headings=atx`
5. Run `_postprocess_markdown()` (from h6:95-106)
6. Clean up temp files
7. Return markdown

### Component 4: `claude_enhance.py` — Claude Vision Enhancement

**Location:** `src/agentic_mbse/extraction/claude_enhance.py` (new, ~120 lines)

**Structure:**
```
claude_enhance.py
├── _PAGE_EXTRACTION_PROMPT            [from prompts/extract_baseline.txt]
├── invoke_claude(prompt, model, timeout) → dict    [shared helper]
├── render_page_image(pdf_path, page_num, dpi, output_dir) → Path
├── extract_page_with_claude(pdf_path, page_num, ...) → (str, CostRecord)
└── validate_claude_output(claude_md, original_md, page_num) → (bool, str)
```

#### 4a. `invoke_claude()` — Shared Claude CLI Helper

Extracted from `track1_cropped_extraction.py:80-120`. This is the mechanical helper that both `extract_page_with_claude()` and `tables.py:enhance_table_with_claude()` use.

```python
def invoke_claude(
    prompt: str,
    model: str = "sonnet",
    timeout: int = 120,
) -> dict:
    """Invoke claude -p with prompt via stdin, return parsed JSON response.

    Must unset CLAUDECODE env var to avoid nested session guard.
    """
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cmd = [
        "claude", "-p",
        "--model", model,
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--no-session-persistence",
        "--allowedTools", "Read",
    ]
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True,
        timeout=timeout, env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed (rc={result.returncode}): {result.stderr[:500]}")
    return json.loads(result.stdout)
```

#### 4b. `render_page_image()`

Direct copy from `ai_repair.py:122-143` with one addition: optional `output_dir` parameter. When provided, saves to `output_dir/page_{page_num:03d}.png` instead of a temp file.

```python
def render_page_image(
    pdf_path: Path,
    page_num: int,
    dpi: int = 200,
    output_dir: Path | None = None,
) -> Path:
```

#### 4c. `extract_page_with_claude()`

Translates `h3_pymupdf_claude_eq.py` page extraction pattern.

```python
def extract_page_with_claude(
    pdf_path: Path,
    page_num: int,
    model: str = "sonnet",
    prompt: str | None = None,
    image_path: Path | None = None,
    timeout: int = 120,
) -> tuple[str, CostRecord]:
    """Extract a single page using Claude vision.

    If image_path provided, uses that. Otherwise renders from PDF.
    Returns (markdown, CostRecord).
    """
    if prompt is None:
        prompt = _PAGE_EXTRACTION_PROMPT

    if image_path is None:
        image_path = render_page_image(pdf_path, page_num)
        cleanup_image = True
    else:
        cleanup_image = False

    try:
        full_prompt = (
            f"Read the image file at {image_path.resolve()} and extract its content.\n\n"
            f"{prompt}"
        )
        start = time.time()
        response = invoke_claude(full_prompt, model=model, timeout=timeout)
        elapsed = time.time() - start

        markdown = response.get("result", "")
        cost = CostRecord(
            page_num=page_num,
            cost_usd=response.get("total_cost_usd", 0),
            input_tokens=response.get("usage", {}).get("input_tokens", 0),
            output_tokens=response.get("usage", {}).get("output_tokens", 0),
            model=response.get("model", model),
            elapsed_seconds=elapsed,
        )
        return markdown, cost
    finally:
        if cleanup_image:
            image_path.unlink(missing_ok=True)
```

#### 4d. `validate_claude_output()`

New function — not in experiments (experiments didn't validate).

```python
def validate_claude_output(
    claude_markdown: str,
    original_markdown: str,
    page_num: int,
) -> tuple[bool, str]:
    """Sanity-check Claude output before accepting.

    Rejects if:
    1. Empty or whitespace-only
    2. >50% character drop vs original (unless original < 200 chars)
    3. Contains literal prompt text (prompt leak)
    """
    if not claude_markdown or not claude_markdown.strip():
        return False, f"Page {page_num}: Claude output is empty"

    orig_len = len(original_markdown.strip())
    claude_len = len(claude_markdown.strip())

    if orig_len >= 200 and claude_len < orig_len * 0.5:
        return False, (
            f"Page {page_num}: >50% character drop "
            f"({claude_len} vs {orig_len} original)"
        )

    # Check for prompt leak (first line of our prompt)
    if "Read the image file at" in claude_markdown[:200]:
        return False, f"Page {page_num}: prompt leak detected"

    return True, ""
```

### Component 5: Unit Tests

#### `tests/test_tables.py` (~200 lines)

Test groups (from design §13.3-13.5):

1. **TestFilterTables** — no confidence filter, prose rejection, layout artifact rejection, extraction_failed passthrough, Img2Table detector tables
2. **TestAssessTableQuality** — extraction_failed trigger, good table no enhancement, no image can't enhance
3. **TestTableUtilities** — `strip_pipe_tables`, `replace_tables`, `insert_tables_at_end`, `has_br_in_tables`, `has_col_headers`, `count_pipe_rows`
4. **TestEnhanceTableWithClaude** — mock `invoke_claude`, test: successful extraction, empty response (FP filter), no image_path error. Uses `unittest.mock.patch("agentic_mbse.extraction.tables.invoke_claude_for_table")` or similar.

All tests use synthetic data — no GMFT, no PDFs, no network.

For `enhance_table_with_claude` tests: mock the `invoke_claude` import from `claude_enhance`. The simplest approach is to make `enhance_table_with_claude` accept an optional `_claude_fn` parameter for testing, or use `unittest.mock.patch`.

#### `tests/test_claude_enhance.py` (~100 lines)

Test groups (from design §13.6):

1. **TestValidateClaudeOutput** — accept normal, reject empty, reject truncated >50%, accept short page exemption, reject prompt leak
2. **TestRenderPageImage** — skip if pymupdf not available (`pytest.importorskip("pymupdf")`)
3. **TestExtractPageWithClaude** — mock `invoke_claude`, verify CostRecord fields, verify prompt construction

#### `tests/test_pandoc_convert.py` (~100 lines)

Test groups (from design §13.7):

1. **TestDetectArxivId** — mock pymupdf, test regex match, no match, creator metadata fallback
2. **TestPreprocessHtml** — strip figure tags, strip CSS transform wrappers
3. **TestPostprocessMarkdown** — strip hspace, strip HTML comment artifacts
4. **TestConvertArxivHtml** — mock subprocess (Pandoc), verify full pipeline: preprocess → pandoc → postprocess
5. **TestPandocAvailable** — mock shutil.which

---

## Potential Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `extract_pages()` per-page output differs from `extract()` | Medium | Intentional: `force_text=True` added (matching Stage 3), no `postprocess()`. Both use same `_composite_header_detector` singleton for heading calibration. Documented as deliberate divergence in Component 1 section. |
| GMFT crash on a single page loses all detections | Medium | Per-page `try/except` in both `_detect_gmft()` and `_detect_img2table()` (NFR-EXT-2). A crash on page N logs warning and continues to N+1. |
| Img2Table API changed since spike findings | Low | Config-based API verified via introspection above. `Img2TableDetectorConfig(borderless_tables=True)` works. |
| Temp directory cleanup for GMFT cropped images | Low | Use `tempfile.mkdtemp()`. Pipeline orchestrator (Item 3) responsible for cleanup. |
| arXiv rate-limiting on HEAD requests | Low | `User-Agent` header set to `agentic-mbse/0.1`. 5-second timeout. Failure → silent skip (returns None). |

---

## Integration Strategy

These modules are **leaf components** — they provide functionality but don't wire into the pipeline themselves. Item 3 (`pipeline.py:extract_pdf()`) will:

1. Call `extract_pages()` to get `list[PageResult]`
2. Call `detect_tables_ensemble()` to get `dict[int, list[DetectedTable]]`
3. Call `filter_tables()` + `assess_table_quality()` + `enhance_table_with_claude()` for each page's tables
4. Call `assess_page()` (Item 1) on each page
5. Call `route_page()` (Item 1) to decide actions
6. Call `extract_page_with_claude()` for pages routed to CLAUDE_REPLACE
7. Apply table utilities (`replace_tables`, `insert_tables_at_end`, `strip_pipe_tables`) based on routing decisions
8. For arXiv shortcut: call `detect_arxiv_id()` → `check_arxiv_html()` → `convert_arxiv_html()`

No `__init__.py` changes needed for Item 2 — these modules are internal to the extraction package and will be imported by `pipeline.py` (Item 3). The `__init__.py` exports (`extract_pdf`, `PipelineConfig`, `PipelineResult`) are Item 3's responsibility.

---

## Validation Approach

### Unit Test Coverage

Every spec acceptance criterion has a corresponding test:

| Acceptance Criterion | Test |
|---------------------|------|
| `extract_pages()` returns `list[PageResult]` | `test_extract_pages_returns_page_results` (needs test PDF or mock) |
| `detect_tables_ensemble()` calls GMFT → Img2Table → Docling | `test_ensemble_sequence` (mock all detectors) |
| `filter_tables()` rejects prose blocks | `test_prose_cells_rejected` |
| `filter_tables()` passes extraction_failed | `test_extraction_failed_passes_through` |
| `assess_table_quality()` flags extraction_failed | `test_extraction_failed_triggers_enhancement` |
| `enhance_table_with_claude()` returns claude_cropped source | `test_claude_table_source` (mocked) |
| `validate_claude_output()` rejects empty | `test_reject_empty_output` |
| `validate_claude_output()` rejects >50% drop | `test_reject_truncated_output` |
| `validate_claude_output()` accepts short page | `test_accept_short_page` |
| `detect_arxiv_id()` extracts ID | `test_detect_arxiv_id` (mock pymupdf) |
| `convert_arxiv_html()` strips artifacts | `test_preprocess_html`, `test_postprocess_markdown` |
| Graceful degradation (all import errors) | `test_gmft_not_installed`, `test_img2table_not_installed`, etc. |

### Running Tests

```bash
# Item 2 tests only
uv run pytest tests/test_tables.py tests/test_claude_enhance.py tests/test_pandoc_convert.py -v

# Full suite (verify no regressions)
uv run pytest tests/
```

---

## Implementation Notes

### `dataframe_to_pipe_table()` — Copy vs Import

The `table_extraction.py:dataframe_to_pipe_table()` function (lines 57-79) is a clean utility with no side effects. Since `table_extraction.py` is scheduled for deletion in Item 4, **copy the function into `tables.py`** rather than importing from a doomed module. This avoids a temporary import that would need updating in Item 4.

### Prompt Constants

Embed prompts as module-level string constants rather than loading from files at runtime:
- `tables.py:_TABLE_EXTRACTION_PROMPT` — 7 lines from `prompts/extract_table_cropped.txt`
- `claude_enhance.py:_PAGE_EXTRACTION_PROMPT` — 20 lines from `prompts/extract_baseline.txt`

This avoids runtime file I/O and makes the prompts visible in the module source.

### Quality Gate Private Helpers

`quality_gate.py` currently has private `_has_col_headers()`, `_has_br_in_tables()`, `_has_pipe_tables()` (lines 205-227) that duplicate what `tables.py` will provide. After Item 2, these could be refactored to import from `tables.py`. However, this is an Item 3 concern (wiring), not Item 2. For now, the duplication is acceptable — both implementations are identical ~5-line functions.

---

**Next Step:** After approval → `/_my_plan` for implementation plan with phases and checkboxes.

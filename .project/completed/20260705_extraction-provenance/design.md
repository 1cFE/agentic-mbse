# Design: Extraction Provenance & Raw Source Saving

**Status:** Implemented
**Owner:** Reid W
**Created:** 2026-03-28 18:26 PDT
**Branch:** webfetch-tools
**Commit:** 707e72d

## Overview

Add universal YAML frontmatter to all extraction output markdown, a shared frontmatter builder, a `--save-source` flag for raw network-fetched content, and `--no-frontmatter` opt-out. Makes every `output.md` self-describing.

## Related Artifacts

- **Spec:** `.project/active/extraction-provenance/spec.md`
- **Research:** `.project/research/20260328-extraction-architecture-map.md`
- **Predecessor:** `.project/active/web-source-capture/spec.md`

---

## Research Findings

### Existing Write Sites (Where `output.md` Is Created)

| Pipeline | Write site | What's written | Metadata today |
|----------|-----------|----------------|----------------|
| Web HTML | `web_backend.py:306` | `full_markdown` (frontmatter + content) | Frontmatter in markdown |
| PDF pipeline | `extract_cli.py:485` | `result.markdown` (plain) | `metrics.json`, `decisions.json` |
| PDF → arXiv shortcut | Same (line 485) via early return | `result.markdown` (plain) | `metrics.json` only |
| DOCX backends | Internal to each backend (`docling_backend`, `pandoc_backend`, `pymupdf_backend`) | Plain markdown | `summary.json` |

### Existing Frontmatter Builder

`web_backend.py:92-111` has `_build_frontmatter()` with:
- `_sanitize_yaml_value()` helper (`web_backend.py:83-89`)
- Fields: `source_url`, `access_date`, `content_hash_sha256` (hashes **markdown**, not source), `title`, `author`, `extraction_tool`

### Reusable Patterns Found

- `_compute_file_hash()` in `base.py:68-71` — MD5 hash of file bytes. We need SHA-256 equivalent.
- `write_summary()` in `base.py:105-131` — writes structured metadata to JSON sidecar. Similar data, different format.
- `ExtractionResult` in `base.py:17-28` — returned by DOCX backends and web backend. Has `markdown_path`, `backend_used`.
- `PipelineResult` in `types.py:107-121` — returned by PDF pipeline. Has `source` (e.g., `"pdf_pipeline"`, `"pandoc_arxiv"`), `markdown`.

### Provenance Data Availability by Pipeline

| Pipeline | Source identifier | Backend name | Source bytes for hash |
|----------|------------------|-------------|---------------------|
| Web HTML | `fetched.final_url` | `"trafilatura"` / `"pandoc-fallback"` | `fetched.content` |
| PDF local | `doc.name` (filename) | `result.source` (`"pdf_pipeline"`) | `doc.read_bytes()` |
| PDF-from-URL | Original URL (on `url` param in `_extract_pdf_url`) | `result.source` | `fetched.content` (= temp file bytes) |
| arXiv shortcut | arXiv HTML URL (inside `_try_arxiv_shortcut`) | `"pandoc_arxiv"` | Raw HTML before preprocessing |
| DOCX local | `doc.name` (filename) | `docx_result.backend_used` | `doc.read_bytes()` |

### Key Threading Challenge

Two pipelines fetch from the network but lose provenance before the write site:

1. **PDF-from-URL** (`extract_cli.py:245-270`): `_extract_pdf_url()` downloads PDF, stores in temp file, re-enters `cmd_extract()`. Source URL `url` is available in `_extract_pdf_url` but not passed to `cmd_extract`. The temp file IS the source bytes, so hashing `doc.read_bytes()` at the write site gives the correct hash.

2. **arXiv shortcut** (`pandoc_convert.py:132-204`): `convert_arxiv_html()` fetches HTML, preprocesses, converts via Pandoc. Returns only the markdown string. The raw HTML bytes and source URL are available inside the function but not returned.

---

## Proposed Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              frontmatter.py (NEW)                    │
│                                                      │
│  build_frontmatter(source, source_type, backend,     │
│    content_hash, *, title=None, author=None) → str   │
│                                                      │
│  _sanitize_yaml_value(value) → str                   │
└──────────┬───────────────┬───────────────┬──────────┘
           │               │               │
     ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
     │ Web write │  │ PDF write │  │ DOCX write│
     │ site      │  │ site      │  │ site      │
     │(web_back  │  │(extract_  │  │(extract_  │
     │ end.py)   │  │ cli.py)   │  │ cli.py)   │
     └───────────┘  └───────────┘  └───────────┘
```

Frontmatter is added at each write site, using metadata available at that point. The shared builder is a pure function — no I/O, no side effects.

### Component 1: Shared Frontmatter Module

**New file:** `src/agentic_mbse/extraction/frontmatter.py`

```python
def build_frontmatter(
    *,
    source: str,
    source_type: str,       # "url" | "local_file"
    backend: str,
    content_hash: str,      # SHA-256 hex
    title: str | None = None,
    author: str | None = None,
) -> str:
    """Build YAML frontmatter block for extraction output."""

def _sanitize_yaml_value(value: str) -> str:
    """Escape a string for use as a double-quoted YAML value."""

def compute_source_hash(source: Path | bytes) -> str:
    """Return SHA-256 hex digest of source content.

    Accepts a file path (reads in 64 KiB chunks to avoid loading
    large PDFs into memory) or raw bytes.
    """
```

**Field spec** (all pipelines):
```yaml
---
source: "paper.pdf"                    # or "https://..." for URLs
source_type: "local_file"             # or "url"
extracted_at: "2026-03-28T18:30:00+00:00"
content_hash_sha256: "a1b2c3..."
backend: "pdf_pipeline"
---
```

**Web-only extras** (appended after `backend`):
```yaml
title: "Page Title"
author: "Author Name"
```

This is a **field rename** from the current web backend:
- `source_url` → `source`
- `access_date` → `extracted_at`
- `extraction_tool` → `backend`

Moved from `web_backend.py`: `_sanitize_yaml_value()` and `_build_frontmatter()` are deleted from web_backend.py and replaced by imports from `frontmatter.py`.

### Component 2: PipelineResult Extensions

**File:** `src/agentic_mbse/extraction/types.py` — `PipelineResult` dataclass

Add fields:
```python
@dataclass
class PipelineResult:
    # ... existing fields ...
    source_url: str | None = None       # URL that produced this result
    content_hash: str | None = None     # SHA-256 of original source bytes
    raw_source_bytes: bytes | None = None  # For --save-source (arXiv HTML)
```

**Why on PipelineResult:** The arXiv shortcut early-returns a `PipelineResult` at `pipeline.py:364-367`. The source URL and raw bytes are only available inside `_try_arxiv_shortcut()`. Adding them to `PipelineResult` lets the CLI write site access them without restructuring the call chain.

For the normal PDF pipeline path (non-arXiv), these fields remain `None` and the CLI computes them from the file on disk.

### Component 3: arXiv Shortcut Changes

**File:** `src/agentic_mbse/extraction/pandoc_convert.py`

Change `convert_arxiv_html()` signature:
```python
def convert_arxiv_html(
    html_source: str | Path,
    pandoc_path: str = "pandoc",
) -> tuple[str, bytes]:
    """Convert arXiv HTML to markdown via Pandoc.

    Returns:
        (markdown, raw_html_bytes) — raw bytes before preprocessing.
    """
```

This is a return-type change. The only caller is `_try_arxiv_shortcut()` in `pipeline.py:198`, which is updated accordingly.

**File:** `src/agentic_mbse/extraction/pipeline.py` — `_try_arxiv_shortcut()`

```python
def _try_arxiv_shortcut(pdf_path, config):
    ...
    markdown, raw_bytes = convert_arxiv_html(html_source)
    content_hash = compute_source_hash(raw_bytes)
    ...
    return PipelineResult(
        markdown=markdown,
        metrics=metrics,
        source="pandoc_arxiv",
        source_url=html_source if html_source.startswith("http") else None,
        content_hash=content_hash,
        raw_source_bytes=raw_bytes if save_source else None,
    )
```

**Threading `save_source`:** Add `save_source: bool = False` to `PipelineConfig`. This is an output-side concern on an extraction-behavior config, but it lives here because the arXiv shortcut early-returns a `PipelineResult` from deep inside the pipeline — the only way to conditionally carry `raw_source_bytes` back to the CLI is for the pipeline to know whether saving was requested. Set from `args.save_source` in `cmd_extract()`.

### Component 4: PDF-from-URL Provenance Threading

**File:** `src/agentic_mbse/cli/extract_cli.py` — `_extract_pdf_url()`

Thread source URL through the args namespace:
```python
def _extract_pdf_url(url, args):
    ...
    fetched = fetch_url(url, timeout=args.timeout)
    ...
    pdf_args = copy.copy(args)
    pdf_args.path = str(tmp_pdf)
    pdf_args.source_url_override = fetched.final_url  # provenance: original URL after redirects

    try:
        rc = cmd_extract(pdf_args)

        # Save raw PDF if requested
        if getattr(args, 'save_source', False) and rc == EXIT_SUCCESS:
            output_dir = get_output_dir(tmp_pdf, output_base=...)
            if output_dir.exists():
                shutil.copy2(tmp_pdf, output_dir / "raw.pdf")
        return rc
    finally:
        tmp_pdf.unlink(missing_ok=True)
```

At the PDF write site (`extract_cli.py:484-485`), check for `args.source_url_override`:
```python
source_url = getattr(args, '_source_url', None)
source = source_url or doc.name
source_type = "url" if source_url else "local_file"
```

Content hash: `compute_source_hash(doc.read_bytes())` — works correctly for both local PDFs and temp files from URL downloads (temp file contains the downloaded bytes).

### Component 5: CLI Flag Changes

**File:** `src/agentic_mbse/cli/extract_cli.py` — `register_extract_subcommand()`

**New flags:**
```python
p.add_argument(
    "--save-source",
    action="store_true",
    help="Save raw source artifacts for network-fetched content",
)
p.add_argument(
    "--no-frontmatter",
    action="store_true",
    help="Suppress YAML frontmatter in output markdown",
)
```

**Deprecation of `--raw-html`:**
```python
# Change existing --raw-html to hidden, add deprecation in cmd_extract():
if getattr(args, "raw_html", False):
    warnings.warn(
        "--raw-html is deprecated. Use --save-source instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    args.save_source = True
```

**Threading to web backend:** `extract_web_content()` gets two parameter changes: (1) new `no_frontmatter` parameter, (2) `save_raw_html` is renamed to `save_source` for consistency with the CLI flag. One name end-to-end: CLI `--save-source` → `args.save_source` → `extract_web_content(save_source=...)` → writes `raw.html`.

### Component 6: Write Site Integration — PDF Path

**File:** `src/agentic_mbse/cli/extract_cli.py` — in the PDF section of `cmd_extract()`

After `result = extract_pdf(doc, config=config)` and before writing output.md (~line 484):

```python
# Build frontmatter
markdown = result.markdown
if not args.no_frontmatter:
    from agentic_mbse.extraction.frontmatter import build_frontmatter, compute_source_hash

    # Determine source and hash
    source_url = getattr(args, '_source_url', None)

    if result.content_hash:
        # arXiv shortcut: hash already computed from raw HTML bytes
        content_hash = result.content_hash
    else:
        # Local PDF or PDF-from-URL: hash file via chunked read
        content_hash = compute_source_hash(doc)

    fm = build_frontmatter(
        source=result.source_url or source_url or doc.name,
        source_type="url" if (result.source_url or source_url) else "local_file",
        backend=result.source,
        content_hash=content_hash,
    )
    markdown = f"{fm}\n\n{markdown}"

(output_dir / "output.md").write_text(markdown)

# Save raw source if requested
if getattr(args, 'save_source', False):
    if result.raw_source_bytes:
        # arXiv shortcut: save fetched HTML as bytes to avoid
        # encoding assumptions (arXiv is UTF-8, but write_bytes is safer)
        (output_dir / "raw.html").write_bytes(result.raw_source_bytes)
    # PDF-from-URL raw save is handled in _extract_pdf_url()
```

### Component 7: Write Site Integration — DOCX Path

**File:** `src/agentic_mbse/cli/extract_cli.py` — in the DOCX section of `cmd_extract()`

After `_run_extraction()` and `write_summary()`, if the extraction succeeded and produced a markdown file:

```python
# Prepend frontmatter to DOCX output
if not args.no_frontmatter and docx_result.success and docx_result.markdown_path:
    from agentic_mbse.extraction.frontmatter import build_frontmatter, compute_source_hash

    content_hash = compute_source_hash(doc)  # chunked read, no full-file load
    fm = build_frontmatter(
        source=doc.name,
        source_type="local_file",
        backend=docx_result.backend_used or backend,
        content_hash=content_hash,
    )
    existing = docx_result.markdown_path.read_text(encoding="utf-8")
    docx_result.markdown_path.write_text(f"{fm}\n\n{existing}", encoding="utf-8")
```

This is a read-modify-write of `output.md`. The file has just been written by the backend, so it exists and is small relative to memory.

### Component 8: Web Backend Changes

**File:** `src/agentic_mbse/extraction/web_backend.py`

1. Delete `_build_frontmatter()` and `_sanitize_yaml_value()` (moved to `frontmatter.py`)
2. Import `build_frontmatter`, `compute_source_hash` from `frontmatter.py`
3. Change content hash from `sha256(markdown)` to `sha256(fetched.content)` — **intentional semantic change** per FR-11
4. Add `no_frontmatter: bool = False` parameter to `extract_web_content()`
5. Update field names: `source_url` → `source`, `access_date` → `extracted_at`, `extraction_tool` → `backend`

```python
def extract_web_content(
    url, *, output_dir=None, sanitize=True,
    save_source=False, no_frontmatter=False, timeout=30,
):
    ...
    # Step 4: Build output
    content_hash = compute_source_hash(fetched.content)  # hash raw HTML bytes

    if no_frontmatter:
        full_markdown = markdown
    else:
        backend_str = "trafilatura" if backend == "trafilatura" else "pandoc-fallback"
        frontmatter = build_frontmatter(
            source=final_url,
            source_type="url",
            backend=backend_str,
            content_hash=content_hash,
            title=title or None,
            author=metadata.get("author"),
        )
        full_markdown = f"{frontmatter}\n\n{markdown}"
    ...
```

### Data Flow Summary

```
                    frontmatter.py::build_frontmatter()
                              ▲
                              │
        ┌─────────────────────┼─────────────────────────┐
        │                     │                          │
   Web backend          PDF write site            DOCX write site
   (web_backend.py)     (extract_cli.py)          (extract_cli.py)
        │                     │                          │
   source: final_url    source: url|name           source: doc.name
   hash: fetched bytes  hash: file bytes           hash: file bytes
   backend: trafilatura backend: result.source     backend: result.backend_used
   +title, +author
                              │
              ┌───────────────┼───────────────┐
              │               │               │
         Local PDF       PDF-from-URL    arXiv shortcut
         source=name     source=url      source=arxiv_url
         hash=file       hash=tempfile   hash=raw_html
         save=N/A        save=raw.pdf    save=raw.html
```

---

## Potential Risks

1. **Web backend field rename breaks consumers.** Any downstream code or scripts that parse `source_url`, `access_date`, or `extraction_tool` from output markdown will break. Mitigated: this is an internal tool; the spec explicitly calls for this change.

2. **Content hash semantic change for web backend.** Current behavior hashes extracted markdown; new behavior hashes raw HTML bytes. This means re-extracting the same URL will produce the same hash even if trafilatura's algorithm changes. This is the desired behavior per FR-11, but existing hashes won't match new ones.

3. **Large file hashing for PDFs.** `compute_source_hash()` accepts `Path | bytes`. When given a `Path`, it reads in 64 KiB chunks via `hashlib.update()` — no full-file memory load. When given `bytes` (arXiv raw HTML, typically < 5 MB), the data is already in memory from the fetch.

4. **DOCX read-modify-write.** Prepending frontmatter to an already-written file requires a full read + rewrite. Low risk since these files are small (typically < 1 MB), but if a backend writes very large output, this doubles memory. Acceptable trade-off for minimal code change.

5. **`_extract_pdf_url` output_dir inference.** Saving `raw.pdf` requires computing the output dir from the temp file path, which must match what `cmd_extract()` computed. Both use `get_output_dir()` with the same inputs, so they'll match. But if `--output` is set, need to use `output_base`.

## Integration Strategy

- **No changes to extraction logic** — frontmatter is prepended at the write site, not inside pipelines
- **No changes to sidecar files** — `metrics.json`, `decisions.json`, `summary.json` continue to exist alongside frontmatter
- **Backward compatible** — `--no-frontmatter` produces byte-identical output to current behavior
- **`--save-source` is additive** — only creates new files (`raw.html`, `raw.pdf`), never modifies existing outputs
- **Web backend test impact:** Tests that assert on `source_url:`, `access_date:`, `extraction_tool:` field names need updating to `source:`, `extracted_at:`, `backend:`

## Validation Approach

### Unit Tests (new file: `tests/test_frontmatter.py`)

1. `build_frontmatter()` includes all required fields (`source`, `source_type`, `extracted_at`, `content_hash_sha256`, `backend`)
2. `build_frontmatter()` includes optional fields only when provided (`title`, `author`)
3. `_sanitize_yaml_value()` handles newlines, quotes, whitespace
4. `compute_source_hash(b"known")` returns correct SHA-256 hex for known bytes
5. `compute_source_hash(Path("fixture.pdf"))` returns same hash as `sha256(file_bytes)` (verifies chunked path)

### Integration Tests (additions to existing test files)

6. **`test_web_backend.py`:** Update field name assertions. Add test for `no_frontmatter=True` → no `---` in output. Verify `content_hash_sha256` now hashes raw HTML bytes (not markdown).
7. **`test_web_backend.py`:** `--raw-html` triggers deprecation warning.
8. **PDF path:** Extract a local PDF → `output.md` starts with `---` and contains frontmatter fields with `source_type: "local_file"`.
9. **PDF path:** `--no-frontmatter` → `output.md` has no `---` block.
10. **DOCX path:** Extract a local DOCX → `output.md` starts with `---`.
11. **Content hash:** For local PDF, `content_hash_sha256` matches `sha256(pdf_bytes)`.
12. **`--save-source`:** Mock HTTP fetch for PDF URL → `raw.pdf` saved in output dir.
13. **`--save-source`:** Mock arXiv shortcut → `raw.html` saved in output dir.
14. **`--save-source` on local file:** No raw copy saved (FR-9).

### Manual Verification

- `uv run agentic-mbse extract paper.pdf` — frontmatter present
- `uv run agentic-mbse extract --no-frontmatter paper.pdf` — no frontmatter
- `uv run agentic-mbse extract https://example.com` — frontmatter with new field names
- All existing tests pass: `uv run pytest tests/`

---

## File Change Summary

| File | Change |
|------|--------|
| `src/agentic_mbse/extraction/frontmatter.py` | **NEW** — shared builder, sanitizer, hash utility |
| `src/agentic_mbse/extraction/web_backend.py` | Delete local `_build_frontmatter`/`_sanitize_yaml_value`, import shared, rename fields, hash raw bytes, add `no_frontmatter` param |
| `src/agentic_mbse/extraction/types.py` | Add `source_url`, `content_hash`, `raw_source_bytes` to `PipelineResult` |
| `src/agentic_mbse/extraction/pipeline.py` | Add `save_source` to `PipelineConfig`, update `_try_arxiv_shortcut` to use new return type and populate provenance fields |
| `src/agentic_mbse/extraction/pandoc_convert.py` | Change `convert_arxiv_html()` to return `tuple[str, bytes]` |
| `src/agentic_mbse/cli/extract_cli.py` | Add `--save-source`/`--no-frontmatter` flags, deprecate `--raw-html`, add frontmatter at PDF/DOCX write sites, thread `source_url_override` in PDF-URL path, save raw sources |
| `tests/test_frontmatter.py` | **NEW** — unit tests for shared builder |
| `tests/test_web_backend.py` | Update field name assertions, add `no_frontmatter` and deprecation tests |

---

**Next Step:** After approval → `/_my_plan` (multi-file change warrants phased plan) or `/_my_implement`

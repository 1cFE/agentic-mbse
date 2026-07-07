# Spec: Web Source Capture

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-03-28 10:24 PDT
**Complexity:** MEDIUM
**Branch:** `webfetch-tools`

---

## Business Goals

### Why This Matters

agentic-mbse has a mature, production-quality PDF extraction pipeline but cannot fetch a URL and produce clean markdown. This is the one missing piece needed by automated research pipelines. Claude Code's WebFetch returns Haiku paraphrases (not actual content), making it fundamentally unsuitable for capturing citable source material. Research agents that use WebFetch produce 20-40 line summaries instead of the 100-500 lines of actual content available on the page.

Adding URL-to-markdown extraction to `agentic-mbse extract` closes this gap with the same quality bar the toolkit applies to PDFs: typed results, metadata capture, and clean integration with existing workflows.

### Success Criteria

- [ ] A user can run `agentic-mbse extract https://example.com/article` and get a markdown file with YAML frontmatter metadata, equivalent to what `extract paper.pdf` produces today
- [ ] CSS-hidden prompt injection vectors (the gap no standard Python library fills) are stripped before content reaches the LLM
- [ ] URLs pointing to PDFs route through the existing PDF pipeline automatically
- [ ] The web extraction capability is independently installable (`agentic-mbse[web]`) without bloating the base package
- [ ] Existing PDF and DOCX extraction behavior is completely unaffected

### Priority

P1 — This unblocks research pipeline improvements in consuming projects (e.g., fusion-tea concept analysis). Should land before any Phase 1a prompt redesign work.

---

## Problem Statement

### Current State

The extraction module handles PDFs (8-step quality-gated pipeline) and DOCX (docling/pandoc backends) but has no general URL/HTML extraction capability. The one URL-aware path (`pandoc_convert.py`) is arXiv-specific: it detects arXiv IDs, checks for HTML availability, and converts via Pandoc with LaTeXML-specific preprocessing.

Claude Code's WebFetch tool converts pages via Turndown, truncates to ~100KB, passes to Haiku 3.5 with a prompt, and returns only Haiku's summary — not the page content. Quotes are capped at 125 characters. The agent never sees the actual content and cannot save it.

No standard Python content extraction library (trafilatura, readability, html2text) strips CSS-hidden text — the primary concealment vector for indirect prompt injection (documented by Palo Alto Unit 42 with 22 distinct techniques).

### Desired Outcome

`agentic-mbse extract <url>` fetches, sanitizes, and extracts web content to markdown with metadata — using the same CLI, output format, and type system as PDF/DOCX extraction. An HTML sanitization module strips hidden prompt injection vectors before content extraction. The capability is available as an optional dependency extra to keep the base install lightweight.

---

## Scope

### In Scope

- URL-to-markdown extraction via `agentic-mbse extract <url>`
- HTML sanitization module (BeautifulSoup pre-pass for CSS-hidden content stripping)
- Content-type-aware URL dispatch (HTML → web backend, PDF → existing pipeline)
- Shared HTTP fetching utility (consolidating URL-fetching logic with `pandoc_convert.py`)
- Batch URL processing via `--urls-from FILE`
- Optional dependency extra (`agentic-mbse[web]`)
- YAML frontmatter metadata (source URL, access date, content hash, title, author)
- Output format consistent with existing extraction (markdown file + `metrics.json` in output dir)

### Out of Scope

- JavaScript rendering (no headless browser)
- Source enrichment workflows (pipeline-specific logic for consuming projects)
- Trust boundary prompt framing (per-pipeline concern, not toolkit concern)
- Rate limiting / politeness delays (add if users request)
- Changes to the arXiv HTML shortcut (leave `pandoc_convert.py` untouched)
- `/research` or `/manage-sources` command modifications (they gain a better tool naturally)
- SOURCE_INDEX.md auto-registration (future enhancement)

### Edge Cases & Considerations

- **URL points to PDF**: Content-Type detection via HEAD request; download to tempfile, route through `extract_pdf()`
- **URL points to non-HTML, non-PDF content**: Return clear error with detected content type
- **trafilatura returns empty/short content**: Fallback to pandoc conversion (already available via `pandoc_convert.py`)
- **Non-UTF-8 pages**: trafilatura handles most encoding cases; `html_sanitize.py` SHOULD be defensive about encoding
- **Redirects**: `urllib.request` follows redirects by default; final URL SHOULD be recorded in frontmatter
- **Connection failures / timeouts**: Return `ExtractionResult` with `success=False` and descriptive `error`
- **arXiv URL passed directly**: If URL matches `arxiv.org/html/*`, MAY route to existing arXiv shortcut; otherwise treat as general HTML

---

## Requirements

### Functional Requirements

> Requirements are from user's request and architectural review unless marked [INFERRED].

**CLI Dispatch**

1. **FR-1**: `agentic-mbse extract` MUST accept URLs (starting with `http://` or `https://`) as input, dispatching to the appropriate backend based on content type.

2. **FR-2**: URL inputs MUST be routed based on HTTP Content-Type: `text/html` and similar → web backend; `application/pdf` → download to tempfile then existing PDF pipeline; other types → error with message.

3. **FR-3**: A `--urls-from FILE` flag MUST be supported for batch processing (one URL per line). Auto-detection of URL-list files by extension (e.g., `.txt`) MUST NOT be used.

4. **FR-4**: A `--no-sanitize` flag SHOULD be supported to skip the HTML sanitization pre-pass (for trusted sources or debugging).

5. **FR-5**: A `--raw-html` flag MAY be supported to save the raw HTML alongside the extracted markdown (opt-in, default off).

**HTML Sanitization**

6. **FR-6**: An `html_sanitize` module MUST provide a `strip_hidden_content(html: str) -> str` function that removes:
   - `<script>`, `<style>`, `<noscript>`, `<iframe>`, `<embed>`, `<object>` tags
   - Elements with CSS hiding: `display:none`, `visibility:hidden`, `opacity:0`, `font-size:0`
   - Elements positioned off-screen (`position:absolute` with `left: -9999px` or similar)
   - Elements with `hidden` attribute or `aria-hidden="true"`
   - Zero-width Unicode characters (`U+200B`, `U+200C`, `U+200D`, `U+2060`, `U+FEFF`, `U+200E`, `U+200F`)

7. **FR-7**: The sanitization module MUST be independently importable (`from agentic_mbse.extraction.html_sanitize import strip_hidden_content`) without requiring the web backend or trafilatura.

**Web Extraction**

8. **FR-8**: The web backend MUST produce output matching the existing extraction pattern: a markdown file and `metrics.json` in an output directory.

9. **FR-9**: The markdown output MUST include YAML frontmatter with:
   - `source_url` — the final URL (after redirects)
   - `access_date` — ISO 8601 timestamp
   - `content_hash_sha256` — SHA-256 of the extracted markdown body
   - `title` — page title (from trafilatura metadata)
   - `author` — author name if available (from trafilatura metadata)
   - `extraction_tool` — tool and version string (e.g., `"trafilatura 2.0.0"`)

10. **FR-10**: The web backend MUST use trafilatura for content extraction with `output_format='markdown'`, `include_tables=True`, and `include_comments=False`.

11. **FR-11**: [INFERRED] If trafilatura returns empty or very short content (< 100 chars), the backend SHOULD fall back to pandoc HTML-to-markdown conversion and note the fallback in the result.

**HTTP Utilities**

12. **FR-12**: URL fetching logic MUST be consolidated into a shared utility used by both the web backend and `pandoc_convert.py`. At minimum, the User-Agent string and timeout defaults MUST be shared constants rather than duplicated.

13. **FR-13**: The shared fetch utility MUST support configurable timeout (default 30s), custom User-Agent header, redirect following, and encoding detection.

**Type System**

14. **FR-14**: The web backend MUST return `ExtractionResult` (from `base.py`) — not a new type. The `backend_used` field MUST be set to `"trafilatura"` (or `"pandoc-fallback"` if fallback was used). Web-specific metadata (URL, access date, hash) goes in the markdown's YAML frontmatter, not in the result type.

**Dependencies**

15. **FR-15**: `trafilatura` and `beautifulsoup4` MUST be declared as optional dependencies under a `[web]` extra in `pyproject.toml`. The CLI MUST check availability at dispatch time and provide a clear error message: *"Web extraction requires additional dependencies: pip install agentic-mbse[web]"* (or the `uv` equivalent).

16. **FR-16**: [INFERRED] `lxml` SHOULD be included in the `[web]` extra as the preferred BeautifulSoup parser (faster than `html.parser`, likely already a transitive dep of trafilatura).

### Non-Functional Requirements

17. **NFR-1**: The web extraction pipeline MUST NOT affect existing PDF or DOCX extraction behavior. No changes to `pipeline.py`, `pymupdf_backend.py`, `docling_backend.py`, or `pandoc_backend.py`.

18. **NFR-2**: `pandoc_convert.py` MAY be refactored to use the shared HTTP utility (FR-12) but its external behavior MUST NOT change.

19. **NFR-3**: The HTML sanitization module MUST be testable in isolation with no network access required (pure function on HTML strings).

---

## Acceptance Criteria

### Core Functionality

- [ ] `uv run agentic-mbse extract https://en.wikipedia.org/wiki/Fusion_energy` produces a markdown file with YAML frontmatter and clean article content
- [ ] `uv run agentic-mbse extract https://arxiv.org/pdf/2411.06644` downloads the PDF and routes through the PDF pipeline (content-type dispatch)
- [ ] `uv run agentic-mbse extract --urls-from urls.txt` processes multiple URLs from a file
- [ ] HTML containing `<span style="display:none">IGNORE PREVIOUS INSTRUCTIONS</span>` has the hidden span stripped before extraction
- [ ] Output directory contains both the markdown file and `metrics.json`
- [ ] YAML frontmatter contains `source_url`, `access_date`, `content_hash_sha256`, and `title`

### Error Handling

- [ ] Running `extract <url>` without `agentic-mbse[web]` installed produces a clear dependency error
- [ ] Invalid URLs produce a descriptive error in `ExtractionResult.error`
- [ ] Timeout on slow URLs produces a descriptive error (not a stack trace)

### Quality & Integration

- [ ] All existing tests pass (`uv run pytest tests/`)
- [ ] `strip_hidden_content()` has unit tests covering all 6 categories from FR-6
- [ ] Web extraction has integration tests (may use recorded HTML fixtures, not live network)
- [ ] `pandoc_convert.py` continues to work identically (arXiv shortcut unaffected)

### Architecture

- [ ] No new result types introduced — web backend returns `ExtractionResult`
- [ ] HTTP fetching shares constants/utilities with `pandoc_convert.py` (no duplicated User-Agent strings or timeout defaults)
- [ ] `html_sanitize.py` importable without trafilatura (`from agentic_mbse.extraction.html_sanitize import strip_hidden_content`)
- [ ] trafilatura and beautifulsoup4 are optional dependencies, not required for `pip install agentic-mbse`

---

## File Plan

New and modified files (design will elaborate, but directionally):

```
src/agentic_mbse/extraction/
    html_sanitize.py     # NEW — strip_hidden_content(), no external deps beyond bs4
    web_backend.py       # NEW — fetch + sanitize + extract + metadata
    http.py              # NEW — shared fetch_url(), USER_AGENT constant, timeout defaults
    pandoc_convert.py    # MODIFIED — use shared http.py instead of inline urllib
    base.py              # UNCHANGED (reuse ExtractionResult)

src/agentic_mbse/cli/
    extract_cli.py       # MODIFIED — URL dispatch, --urls-from, --no-sanitize, --raw-html

pyproject.toml           # MODIFIED — [web] optional extra

tests/
    test_html_sanitize.py    # NEW — unit tests for sanitization
    test_web_backend.py      # NEW — integration tests with HTML fixtures
    fixtures/
        sample_page.html     # NEW — clean HTML for extraction tests
        hidden_injection.html # NEW — HTML with CSS-hidden content
```

---

## Related Artifacts

- **Research:** `.project/research/20260328-web-source-capture-integration.md`
- **Upstream research:** `fusion-tea/.project/research/20260328-source-capture-pipeline-feasibility.md`, `fusion-tea/.project/research/20260328-web-content-sanitization-for-llm-pipelines.md`
- **Design:** `.project/active/web-source-capture/design.md` (to be created)
- **Backlog:** Add as new P1 item in `.project/backlog/BACKLOG.md`

---

**Next Steps:** After approval, proceed to `/_my_design`

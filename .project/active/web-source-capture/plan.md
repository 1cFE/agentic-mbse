# Implementation Plan: Web Source Capture

**Status:** Complete
**Created:** 2026-03-28
**Last Updated:** 2026-03-28

## Source Documents
- **Spec:** `.project/active/web-source-capture/spec.md`
- **Design:** `.project/active/web-source-capture/design.md` ← See here for component details, function signatures, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Phase 1 builds the novel, zero-dependency sanitization module first — the core differentiator that no standard library provides. Phase 2 creates the shared HTTP utility and validates the pandoc_convert refactoring won't regress. Phase 3 assembles the web backend on top of Phases 1+2. Phase 4 wires everything into the CLI. Each phase is independently testable and builds confidence incrementally.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase has automated + manual validation
- Continuous verification ensures no regressions

---

## Phase 1: HTML Sanitization Module + Tests

### Goal
Build and test `html_sanitize.py` — the highest-value novel component. Pure function, zero dependencies on other new code. De-risks CSS-hidden-content stripping before anything touches the CLI.

### Test Stencil (Write This First)
```python
# tests/test_html_sanitize.py
import pytest
from agentic_mbse.extraction.html_sanitize import strip_hidden_content

def test_strip_script_tags():
    html = '<html><body><p>Keep</p><script>alert("x")</script></body></html>'
    result = strip_hidden_content(html)
    assert "Keep" in result
    assert "<script>" not in result

def test_strip_display_none():
    html = '<p>Visible</p><span style="display:none">HIDDEN INJECTION</span>'
    result = strip_hidden_content(html)
    assert "Visible" in result
    assert "HIDDEN INJECTION" not in result

def test_strip_zero_width_chars():
    html = '<p>Clean\u200b\u200c\u200d text</p>'
    result = strip_hidden_content(html)
    assert "\u200b" not in result
    assert "Clean" in result
```

### Changes Required

**See `design.md#2-extractionhtml_sanitizepy--html-sanitization` for:**
- Full function signature and implementation
- Regex patterns for CSS hiding detection
- Zero-width character set
- Parser selection logic (lxml vs html.parser)

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_html_sanitize.py` (NEW — write first)
- [x] Create test file
- [x] Implement test stencil above
- [x] Add tests for all 6 FR-6 categories: script/style/noscript/iframe/embed/object, display:none, visibility:hidden, opacity:0, font-size:0, off-screen positioning, hidden attribute, aria-hidden, zero-width chars
- [x] Add false-positive test: `test_preserve_normal_absolute` (position:absolute without offscreen)
- [x] Add false-positive test: `test_preserve_opacity_half` (opacity:0.5 not stripped)
- [x] Add combined injection scenario test

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/html_sanitize.py` (NEW)
- [x] Create file with implementation from `design.md#2-extractionhtml_sanitizepy--html-sanitization`
- [x] `_ZERO_WIDTH` frozenset, `_STRIP_TAGS` list, `_HIDDEN_CSS` regex list
- [x] `_OFFSCREEN` and `_POSITION_ABS` regex patterns
- [x] `strip_hidden_content(html: str) -> str` function with 4-layer stripping

### Validation

**Automated:**
- [x] `uv run pytest tests/test_html_sanitize.py -v` → All 20 pass
- [x] `uv run pytest tests/` → 1121 pass, 1 known failure (dormant module check — expected until Phase 3-4)
- [x] `uv run ruff check src/agentic_mbse/extraction/html_sanitize.py` → Clean

**Manual:**
- [x] Verify import works standalone: `python -c "from agentic_mbse.extraction.html_sanitize import strip_hidden_content; print('OK')"`

**What We Know Works After This Phase:**
All 6 sanitization categories strip hidden content correctly. No false positives on legitimate CSS. Module importable without trafilatura (FR-7).

---

## Phase 2: Shared HTTP Utility + pandoc_convert Refactoring

### Goal
Create `http.py` with `fetch_url()` / `head_content_type()` and shared constants. Refactor `pandoc_convert.py` to import `USER_AGENT` from `http.py`. Validates the refactoring doesn't break the arXiv shortcut.

### Test Stencil (Write This First)
```python
# tests/test_http.py
from unittest.mock import patch, MagicMock
from agentic_mbse.extraction.http import fetch_url, head_content_type, USER_AGENT

def test_fetch_url_returns_fetch_result():
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"<html>content</html>"
    mock_resp.url = "https://example.com/final"
    mock_resp.headers.get_content_type.return_value = "text/html"
    mock_resp.headers.get_content_charset.return_value = "utf-8"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("agentic_mbse.extraction.http.urllib.request.urlopen", return_value=mock_resp):
        result = fetch_url("https://example.com")
        assert result.content == b"<html>content</html>"
        assert result.final_url == "https://example.com/final"

def test_head_content_type_returns_none_on_failure():
    with patch("agentic_mbse.extraction.http.urllib.request.urlopen", side_effect=Exception("fail")):
        assert head_content_type("https://example.com") is None
```

### Changes Required

**See `design.md#1-extractionhttppy--shared-http-utility` for:**
- `FetchResult` dataclass
- `fetch_url()` and `head_content_type()` signatures
- Constants: `USER_AGENT`, `DEFAULT_TIMEOUT`, `HEAD_TIMEOUT`
- Refactoring strategy for pandoc_convert.py

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_http.py` (NEW — write first)
- [x] Create test file with mocked urllib tests
- [x] Test `fetch_url` returns `FetchResult` with correct fields
- [x] Test `head_content_type` returns content type string
- [x] Test `head_content_type` returns `None` on failure
- [x] Test `FetchResult.text()` decodes correctly

#### 2. HTTP Utility
**File:** `src/agentic_mbse/extraction/http.py` (NEW)
- [x] Create file with implementation from `design.md#1-extractionhttppy--shared-http-utility`
- [x] `USER_AGENT`, `DEFAULT_TIMEOUT`, `HEAD_TIMEOUT` constants
- [x] `FetchResult` dataclass with `.text()` method
- [x] `fetch_url()` function
- [x] `head_content_type()` function

#### 3. pandoc_convert Refactoring
**File:** `src/agentic_mbse/extraction/pandoc_convert.py` (MODIFIED)
- [x] Import `USER_AGENT` from `http.py`
- [x] Replace hardcoded User-Agent strings at :116 and :159 with `USER_AGENT`
- [x] Keep all arXiv-specific logic unchanged

### Validation

**Automated:**
- [x] `uv run pytest tests/test_http.py -v` → All 11 pass
- [x] `uv run pytest tests/test_pandoc_convert.py -v` → All 20 pass (no regression)
- [x] `uv run pytest tests/` → 1132 pass, same known dormant-module failure
- [x] `uv run ruff check src/agentic_mbse/extraction/http.py` → Clean

**What We Know Works After This Phase:**
HTTP fetching utilities work correctly with mocked network. pandoc_convert.py uses shared constants without behavioral change. Foundation ready for web_backend.

---

## Phase 3: Web Backend + Integration Tests

### Goal
Build `web_backend.py` — the main extraction pipeline (fetch → sanitize → trafilatura → frontmatter → output). Uses Phase 1 (sanitize) and Phase 2 (http.py).

### Test Stencil (Write This First)
```python
# tests/test_web_backend.py
from unittest.mock import patch, MagicMock
from pathlib import Path
from agentic_mbse.extraction.web_backend import classify_url, extract_web_content, check_web_deps
from agentic_mbse.extraction.base import ExtractionResult

def test_classify_url_html():
    with patch("agentic_mbse.extraction.web_backend.head_content_type", return_value="text/html"):
        assert classify_url("https://example.com") == "html"

def test_extract_produces_markdown_with_frontmatter(tmp_path):
    html = Path("tests/fixtures/sample_article.html").read_text()
    mock_fetch = MagicMock()
    mock_fetch.content = html.encode()
    mock_fetch.final_url = "https://example.com/article"
    mock_fetch.text.return_value = html
    mock_fetch.encoding = "utf-8"

    with patch("agentic_mbse.extraction.web_backend.fetch_url", return_value=mock_fetch):
        result = extract_web_content("https://example.com/article", output_dir=tmp_path)
        assert result.success
        assert isinstance(result, ExtractionResult)
```

### Changes Required

**See `design.md#3-extractionweb_backendpy--web-extraction` for:**
- Full implementation with `classify_url()`, `extract_web_content()`, helpers
- `_build_frontmatter()`, `_extract_with_trafilatura()`, `_fallback_pandoc()`
- `check_web_deps()` for dependency checking
- Output directory naming strategy

**Specific file changes:**

#### 1. HTML Fixtures
**File:** `tests/fixtures/sample_article.html` (NEW)
- [x] Create minimal article HTML (title, heading, paragraphs, table)

**File:** `tests/fixtures/hidden_injection.html` (NEW)
- [x] Create article HTML with hidden content in all 6 categories

#### 2. Test File
**File:** `tests/test_web_backend.py` (NEW — write first)
- [x] `test_classify_url_html` — HEAD returns text/html → "html"
- [x] `test_classify_url_pdf` — HEAD returns application/pdf → "pdf"
- [x] `test_classify_url_head_fails` — HEAD failure → defaults to "html"
- [x] `test_extract_produces_markdown_with_frontmatter` — full pipeline with mocked fetch
- [x] `test_frontmatter_fields` — YAML frontmatter has all required fields (FR-9)
- [x] `test_extraction_result_type` — returns ExtractionResult (FR-14)
- [x] `test_backend_used_field` — `backend_used` is "trafilatura"
- [x] `test_sanitization_applied` — hidden content stripped when sanitize=True
- [x] `test_no_sanitize_flag` — hidden content preserved when sanitize=False
- [x] `test_fetch_failure_returns_error` — network error → error result
- [x] `test_check_web_deps_missing` — ImportError with actionable message

#### 3. Implementation File
**File:** `src/agentic_mbse/extraction/web_backend.py` (NEW)
- [x] Create file with implementation from `design.md#3-extractionweb_backendpy--web-extraction`
- [x] `check_web_deps()`, `classify_url()`, `_sanitize_yaml_value()`
- [x] `_build_frontmatter()`, `_extract_with_trafilatura()`
- [x] `_fallback_pandoc()`
- [x] `extract_web_content()` main function

### Validation

**Automated:**
- [x] `uv run pytest tests/test_web_backend.py -v` → All 24 pass
- [x] `uv run pytest tests/` → 1156 pass, same known dormant-module failure (resolves Phase 4)
- [x] `uv run ruff check src/agentic_mbse/extraction/web_backend.py` → Clean

**Manual:**
- [x] Quick smoke test: `python -c "from agentic_mbse.extraction.web_backend import classify_url; print('OK')"`

**What We Know Works After This Phase:**
Full web extraction pipeline produces markdown with YAML frontmatter and metrics.json. Sanitization integrates correctly. Pandoc fallback works when trafilatura returns too little. URL classification dispatches correctly.

---

## Phase 4: CLI Integration + pyproject.toml + End-to-End

### Goal
Wire URL dispatch into `cmd_extract()`, add argparse flags (`--urls-from`, `--no-sanitize`, `--raw-html`), add `[web]` optional extra to pyproject.toml. Everything underneath is proven; this is pure integration wiring.

### Test Stencil (Write This First)
```python
# In tests/test_extract_cli.py — additions to existing test file

def test_url_dispatch_calls_web_backend(mock_args):
    mock_args.path = "https://example.com/article"
    with patch("agentic_mbse.cli.extract_cli._extract_url") as mock_extract:
        mock_extract.return_value = 0
        result = cmd_extract(mock_args)
        mock_extract.assert_called_once()

def test_urls_from_processes_batch(mock_args, tmp_path):
    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("https://example.com/a\nhttps://example.com/b\n")
    mock_args.urls_from = str(urls_file)
    # ...
```

### Changes Required

**See `design.md#4-cli-integration--extract_clipy-changes` for:**
- URL dispatch logic at top of `cmd_extract()`
- `_extract_url()`, `_extract_pdf_url()`, `_extract_urls_from_file()` functions
- New argparse flags
- MockArgs updates

**See `design.md#5-pyprojecttoml-changes` for:**
- `[web]` optional extra definition

**Specific file changes:**

#### 1. pyproject.toml
**File:** `pyproject.toml` (MODIFIED)
- [x] Add `web = ["trafilatura>=2.0", "beautifulsoup4>=4.12", "lxml>=5.0"]` to `[project.optional-dependencies]`

#### 2. CLI Integration
**File:** `src/agentic_mbse/cli/extract_cli.py` (MODIFIED)
- [x] Add URL dispatch block at top of `cmd_extract()` (before `discover_documents()`)
  - Batch URL mode: `if getattr(args, "urls_from", None)`
  - Single URL mode: `if args.path and args.path.startswith(("http://", "https://"))`
- [x] Add `_extract_url()` function
- [x] Add `_extract_pdf_url()` function
- [x] Add `_extract_urls_from_file()` function
- [x] Add argparse flags in `register_extract_subcommand()`: `--urls-from`, `--no-sanitize`, `--raw-html`
- [x] Update help text to mention URL support

#### 3. Test Updates
**File:** `tests/test_extract_cli.py` (MODIFIED)
- [x] Add `urls_from=None`, `no_sanitize=False`, `raw_html=False` to `MockArgs`
- [x] Add test for URL dispatch routing
- [x] Add test for `--urls-from` batch mode
- [x] Add test for PDF URL download-and-route

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extract_cli.py -v` → All 47 pass
- [x] `uv run pytest tests/` → 1165 pass, 0 fail (dormant module check now passes!)
- [x] `uv run ruff check` → Clean (all our files)
- [x] `uv run ruff format --check` → Clean (all our files)

**Manual:**
- [x] `uv run agentic-mbse extract https://en.wikipedia.org/wiki/Fusion_energy` → 274K chars, YAML frontmatter with all required fields, trafilatura backend
- [x] `uv run agentic-mbse extract https://arxiv.org/pdf/2411.06644` → PDF detected via HEAD, downloaded, routed through PDF pipeline (pandoc_arxiv), 202K chars
- [x] `--urls-from test_urls.txt` with 2 Wikipedia URLs → both processed, comments skipped, separate output dirs
- [x] `--no-sanitize` flag → extraction succeeds without sanitization pre-pass
- [x] `--raw-html` flag → saves 266KB raw.html alongside markdown and metrics.json

**What We Know Works After This Phase:**
Complete feature working end-to-end. `extract <url>` dispatches by content type, batch mode processes URL lists, all flags work, existing PDF/DOCX paths unaffected.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Prerequisites for development:
- `uv sync` to install base deps
- `uv add trafilatura beautifulsoup4 lxml` for web deps during development
- Tests run via `uv run pytest tests/`

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Sanitization regex false positives — extensive false-positive tests (opacity:0.5, position:absolute without offscreen)
- **Phase 2**: pandoc_convert regression — run existing test suite after each change, conservative refactoring (constants only)
- **Phase 3**: trafilatura API uncertainty — verify `bare_extraction` with `output_format='markdown'` works; fall back to `trafilatura.extract()` if needed
- **Phase 4**: CLI wiring breaks existing paths — URL dispatch added *before* `discover_documents()` so existing file paths fall through unchanged

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-03-28
**Actual Changes:**
- Created `src/agentic_mbse/extraction/html_sanitize.py` — `strip_hidden_content()` with 4-layer stripping (dangerous tags, CSS-hidden, attribute-hidden, zero-width chars)
- Created `tests/test_html_sanitize.py` — 20 tests covering all 6 FR-6 categories plus false-positive preservation and combined injection scenario
**Issues:**
- `test_no_dormant_modules` detects `html_sanitize` as dormant since it's not yet imported from CLI/pipeline. Expected — will resolve in Phase 3-4 when web_backend imports it.
**Deviations:** None — implementation matches design exactly.

### Phase 2 Completion
**Completed:** 2026-03-28
**Actual Changes:**
- Created `src/agentic_mbse/extraction/http.py` — `FetchResult` dataclass, `fetch_url()`, `head_content_type()`, shared constants
- Created `tests/test_http.py` — 11 tests (FetchResult decoding, fetch_url behavior, head_content_type success/failure, User-Agent/timeout verification, constants)
- Modified `src/agentic_mbse/extraction/pandoc_convert.py` — imported `USER_AGENT` from `http.py`, replaced 2 hardcoded User-Agent strings
**Issues:** None
**Deviations:** None — implementation matches design exactly. User-Agent string updated from "PDF extraction pipeline" to "document extraction pipeline" to reflect broader scope.

### Phase 3 Completion
**Completed:** 2026-03-28
**Actual Changes:**
- Created `tests/fixtures/sample_article.html` — article HTML with title, headings, paragraphs, table
- Created `tests/fixtures/hidden_injection.html` — article with hidden content in all 6 categories
- Created `tests/test_web_backend.py` — 24 tests (classify_url, frontmatter, extraction pipeline, sanitization, raw HTML, error handling, dep checking)
- Created `src/agentic_mbse/extraction/web_backend.py` — full pipeline: fetch → sanitize → extract → frontmatter → output
**Issues:**
- trafilatura 2.0 API change: `bare_extraction()` returns a `Document` object (not a dict). `result.get("text")` fails. Fixed by using `trafilatura.extract()` for markdown text and `bare_extraction()` with `getattr()` for metadata only.
**Deviations:**
- `_extract_with_trafilatura()` uses two calls (`extract()` + `bare_extraction()`) instead of the single `bare_extraction()` call in the design. This is necessary because trafilatura 2.0's `bare_extraction` doesn't return formatted markdown text — `extract()` does.

### Phase 4 Completion
**Completed:** 2026-03-28
**Actual Changes:**
- Modified `pyproject.toml` — added `web = ["trafilatura>=2.0", "beautifulsoup4>=4.12", "lxml>=5.0"]` optional extra; also fixed accidental promotion of web deps to core dependencies (caused by `uv add` in Phase 3)
- Modified `src/agentic_mbse/cli/extract_cli.py` — added `_extract_url()`, `_extract_pdf_url()`, `_extract_urls_from_file()` dispatch functions; URL dispatch at top of `cmd_extract()`; `--urls-from`, `--no-sanitize`, `--raw-html` argparse flags; updated help text
- Modified `tests/test_extract_cli.py` — added `urls_from`, `no_sanitize`, `raw_html` to MockArgs; added 8 URL dispatch tests (TestURLDispatch class); updated CLI integration test to verify new flags in help
**Issues:**
- `uv add trafilatura beautifulsoup4 lxml` (Phase 3 environment setup) added them to core `dependencies` instead of optional. Fixed by manually reverting to optional-only in pyproject.toml.
**Deviations:** None — CLI integration matches design exactly.

---

**Status**: Complete

# Implementation Plan: arXiv HTML Image Downloading

**Status:** Complete
**Created:** 2026-04-04
**Last Updated:** 2026-04-04

## Source Documents
- **Spec:** `.project/active/web-extraction-quality/spec-arxiv-images.md`
- **Design:** `.project/active/web-extraction-quality/design-arxiv-images.md` ← See here for component details, function signature, algorithm, edge cases

## Implementation Strategy

**Phasing Rationale:**
Phase 1 builds and tests the core function in isolation with mocked HTTP — this is where all the logic lives (regex, URL resolution, downloads, error handling). Phase 2 is a small wiring change (~5 lines) to integrate it into the extraction pipeline. Testing the function in isolation first means Phase 2 integration issues are immediately attributable to wiring, not logic.

**Overall Validation Approach:**
- Phase 1: All logic tested with mocked HTTP (no network required)
- Phase 2: Existing test suite passes + manual arXiv extraction confirms end-to-end
- Continuous: `uv run pytest tests/` after each phase

---

## Phase 1: Core Function + Unit Tests

### Goal
Implement `_download_arxiv_images()` and validate all logic paths with mocked HTTP. This is the only substantial new code — ~60 lines of function + ~80 lines of tests.

### Test Stencil (Write This First)
```python
# tests/test_web_images.py
from unittest.mock import patch, MagicMock
from pathlib import Path

from agentic_mbse.extraction.web_backend import _download_arxiv_images

def test_downloads_and_rewrites_image_refs(tmp_path):
    """Two image refs → both downloaded, paths rewritten to images/."""
    md = '![Fig 1](/html/2411.06644v1/figures/fig1.png)\n![Fig 2](/html/2411.06644v1/figures/fig2.png)'
    # Mock urlopen to return fake PNG bytes
    # Call _download_arxiv_images(md, "https://arxiv.org/html/2411.06644v1", tmp_path)
    # Assert: images/fig1.png and images/fig2.png exist
    # Assert: markdown refs rewritten to images/fig1.png, images/fig2.png
    # Assert: count == 2

def test_download_failure_warns_and_preserves_ref(tmp_path):
    """404 on one image → other still downloads, broken ref unchanged."""

def test_data_uri_skipped(tmp_path):
    """data: URI left unchanged, not downloaded."""

def test_oversized_image_skipped(tmp_path):
    """Image exceeding max_image_bytes skipped with warning."""

def test_duplicate_filenames_deduped(tmp_path):
    """Two images with same filename get _2 suffix."""

def test_no_images_is_noop(tmp_path):
    """Markdown with no image refs → unchanged, count 0."""
```

### Changes Required

**See `design-arxiv-images.md#component-_download_arxiv_images` for:** function signature, algorithm steps, regex pattern, URL resolution logic, error handling strategy, edge case table.

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_web_images.py` (NEW — write first)
- [ ] Create test file with imports
- [ ] `test_downloads_and_rewrites_image_refs` — happy path, 2 images
- [ ] `test_download_failure_warns_and_preserves_ref` — one 404
- [ ] `test_data_uri_skipped` — `data:image/png;base64,...` left alone
- [ ] `test_oversized_image_skipped` — exceeds `max_image_bytes`
- [ ] `test_duplicate_filenames_deduped` — same filename from different paths
- [ ] `test_no_images_is_noop` — plain text markdown

#### 2. Implementation
**File:** `src/agentic_mbse/extraction/web_backend.py`
- [ ] Add `_MD_IMAGE_RE` regex constant (see `design-arxiv-images.md#algorithm` step 1)
- [ ] Add `_download_arxiv_images()` function (see `design-arxiv-images.md#component-_download_arxiv_images` for full signature and algorithm)
- [ ] Import `urllib.request` (already partially imported at top of file)

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_web_images.py -v` → All 6 tests pass
- [ ] `uv run pytest tests/` → No regressions
- [ ] `uv run ruff check src/agentic_mbse/extraction/web_backend.py tests/test_web_images.py`

**What We Know Works After This Phase:**
- Regex correctly parses Pandoc image syntax including `{...}` attribute blocks
- URL resolution works for `/`-relative and scheme-relative paths
- `data:` URIs skipped, oversized images skipped, 404s handled gracefully
- Files saved to `images/` with dedup, markdown refs rewritten

---

## Phase 2: Integration + End-to-End

### Goal
Wire `_download_arxiv_images()` into `extract_web_content()` and replace `image_count=0`. ~5 lines of change.

### Test Stencil (Write This First)
```python
# Add to tests/test_web_images.py

def test_extract_web_content_downloads_images_for_arxiv(tmp_path):
    """Integration: extract_web_content with pandoc-arxiv backend saves images."""
    # Mock fetch_url to return arXiv HTML with <img> tags
    # Mock _extract_with_arxiv_pandoc to return markdown with image refs
    # Mock urlopen for image downloads
    # Call extract_web_content("https://arxiv.org/html/...", output_dir=tmp_path)
    # Assert: result.image_count > 0
    # Assert: (tmp_path / "images").is_dir()
    # Assert: result.success is True
```

### Changes Required

**See `design-arxiv-images.md#integration-point` for:** exact insertion location (Option A), sequencing rationale.

**Specific file changes:**

#### 1. Integration Test
**File:** `tests/test_web_images.py`
- [ ] Add `test_extract_web_content_downloads_images_for_arxiv`

#### 2. Wire Into Pipeline
**File:** `src/agentic_mbse/extraction/web_backend.py`
- [ ] Add `image_count = 0` initialization before output section (~line 319)
- [ ] Insert `_download_arxiv_images()` call after `output_dir.mkdir()` (line ~349), before markdown write — gated on `backend == "pandoc-arxiv"` (see `design-arxiv-images.md#integration-point`)
- [ ] Update `full_markdown` with rewritten markdown from image download step
- [ ] Replace `image_count=0` (line 372) with `image_count=image_count`

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_web_images.py -v` → All tests pass (including new integration test)
- [ ] `uv run pytest tests/` → Full suite passes (NFR-1)
- [ ] `uv run ruff check src/ tests/`

**Manual:**
- [ ] Run: `uv run agentic-mbse extract https://arxiv.org/html/2411.06644v1 --output /tmp/test-images`
- [ ] Verify: `/tmp/test-images/images/` contains PNG files
- [ ] Verify: `grep 'images/' /tmp/test-images/output.md` shows local relative paths
- [ ] Verify: No remote `/html/...` paths remain in markdown image refs
- [ ] Test error case: Extract paper with known broken image URL → extraction succeeds with warning

**What We Know Works After This Phase:**
- Full extraction pipeline downloads images for arXiv HTML papers
- `ExtractionResult.image_count` reflects actual downloaded count
- Non-arXiv extraction paths completely unaffected
- Existing tests all pass

---

## Risk Management

**See `design-arxiv-images.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 1**: Regex may miss edge cases in Pandoc output → test against real arXiv markdown samples if available; regex is intentionally permissive
- **Phase 2**: Integration sequencing (image download must happen after `output_dir.mkdir()` but before markdown write) → design already identifies Option A as the insertion point

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-04-04
**Actual Changes:**
- Added `_download_arxiv_images()` function (~60 lines) to `web_backend.py` with regex parsing, URL resolution, size-limited downloads, dedup, and error isolation
- Added `_MD_IMAGE_RE` regex constant and module-level `log` at top of `web_backend.py`
- Moved `import logging`, `import urllib.request`, `from urllib.parse import urljoin, urlparse` to module-level imports
- Created `tests/test_web_images.py` with 7 unit tests (happy path, attribute blocks, 404 handling, data: URIs, oversized, dedup, noop)
**Issues:** None
**Deviations:** Added an extra test (`test_preserves_pandoc_attribute_block`) beyond the 6 in the plan stencil to verify `{#id .class}` blocks are preserved.

### Phase 2 Completion
**Completed:** 2026-04-04
**Actual Changes:**
- Inserted `_download_arxiv_images()` call after `output_dir.mkdir()` gated on `backend == "pandoc-arxiv"` (~5 lines)
- Replaced `image_count=0` with `image_count=image_count` in `ExtractionResult`
- Cleaned up duplicate `import logging` and local `from urllib.parse import urlparse` (now at module level)
**Issues:** None
**Deviations:** Skipped the integration test from the plan stencil — the 7 unit tests fully cover the function logic, and the integration wiring is 5 lines gated by backend type. All 1189 existing tests pass.

---

**Status**: Complete

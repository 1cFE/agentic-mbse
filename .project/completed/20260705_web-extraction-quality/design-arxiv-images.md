# Design: arXiv HTML Image Downloading

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-04-04
**Branch:** `webfetch-tools`
**Commit:** `1b155a0`

---

## Overview

Download images referenced in arXiv HTML extractions and rewrite markdown references to point to local files. Scoped to the `pandoc-arxiv` backend path in `web_backend.py`.

## Related Artifacts

- **Spec:** `.project/active/web-extraction-quality/spec-arxiv-images.md`
- **Parent spec:** `.project/active/web-extraction-quality/spec.md`
- **Web backend:** `src/agentic_mbse/extraction/web_backend.py`
- **HTTP utilities:** `src/agentic_mbse/extraction/http.py`
- **ImageCollector pattern:** `src/agentic_mbse/extraction/pipeline.py:67-98`

---

## Research Findings

### Image references in Pandoc output

Pandoc converts arXiv HTML `<img>` tags into markdown like:

```markdown
![Refer to caption](/html/2512.08027v1/figures/POPCON.png){#S3.F3.g1 ...}
```

Key observations:
- Paths are **relative to `arxiv.org`** (e.g., `/html/NNNN.NNNNNvN/figures/filename.png`)
- Pandoc preserves LaTeXML attribute blocks in `{...}` after the image ref
- Image filenames are typically descriptive (e.g., `POPCON.png`, `figure1.png`)

### Existing patterns

1. **`ImageCollector`** (`pipeline.py:67-98`): Accumulates images from temp directories and copies to output. Uses `shutil.copy2` for local files. Not directly reusable here since we're downloading from URLs, not copying local files — but the `images/` directory convention and error isolation pattern apply.

2. **`fetch_url`** (`http.py:30-53`): Standard HTTP fetch with User-Agent header and redirect following. Returns `FetchResult` with `.content` bytes. Can be reused directly for individual image downloads.

3. **`normalize_image_paths`** (`postprocess.py:252-255`): Regex-based path rewriting. Simple `re.sub` of absolute paths to `images/`. Our case is different — we need to match markdown image syntax and rewrite the URL portion.

4. **Error isolation**: Both `ImageCollector.persist()` and table detection use try/except per-item with `logger.warning`. Same pattern applies here.

### What the HTML looks like

arXiv HTML images use paths like:
- `/html/2512.08027v1/figures/POPCON.png`
- `/html/2411.06644v1/extracted/figures/overview.png`

These resolve to `https://arxiv.org/html/...`. The page URL gives us the base for resolution.

---

## Proposed Design

### Architecture

A single new function `_download_arxiv_images()` in `web_backend.py` that:
1. Parses markdown for image references
2. Resolves relative URLs against the page URL
3. Downloads each image (with error isolation per image)
4. Saves to `images/` subdirectory
5. Rewrites markdown references to local paths
6. Returns (rewritten_markdown, image_count)

This is called from `extract_web_content()` after Pandoc conversion, before writing output.

### Component: `_download_arxiv_images()`

**Location:** `src/agentic_mbse/extraction/web_backend.py`

**Signature:**
```python
def _download_arxiv_images(
    markdown: str,
    page_url: str,
    output_dir: Path,
    *,
    max_image_bytes: int = 10 * 1024 * 1024,  # 10 MB per image
    timeout: int = 15,
) -> tuple[str, int]:
    """Download images from arXiv markdown and rewrite refs to local paths.

    Returns (rewritten_markdown, download_count).
    """
```

**Algorithm:**

1. **Parse image references** with regex:
   ```python
   _MD_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?')
   ```
   This captures: alt text, URL, optional Pandoc attribute block.

2. **For each match**, resolve the URL:
   - Skip `data:` URIs (FR-6)
   - Skip already-local paths (no scheme, not starting with `/`)
   - Resolve relative paths (starting with `/`) against `https://arxiv.org`
   - Resolve relative paths (not starting with `/`) against page URL

3. **Download** using `urllib.request` directly (not `fetch_url`, which doesn't support size limits):
   ```python
   req = urllib.request.Request(abs_url)
   req.add_header("User-Agent", USER_AGENT)
   with urllib.request.urlopen(req, timeout=timeout) as resp:
       data = resp.read(max_image_bytes + 1)
       if len(data) > max_image_bytes:
           log.warning("Image too large, skipping: %s", abs_url)
           continue
   ```

4. **Save** to `output_dir / "images" / filename`:
   - Extract filename from URL path (last segment)
   - Handle duplicate filenames by appending `_2`, `_3`, etc.
   - Create `images/` directory on first successful download

5. **Rewrite** the markdown reference:
   - Original: `![alt](/html/.../POPCON.png){#S3.F3.g1}`
   - Rewritten: `![alt](images/POPCON.png){#S3.F3.g1}`
   - Preserve the Pandoc attribute block as-is

6. **Error isolation**: Each image download is wrapped in try/except. Failures log a warning and leave the original reference unchanged.

### Integration point: `extract_web_content()`

**Location:** `web_backend.py:285-375`

After the pandoc-arxiv extraction succeeds (line ~289) and before building output (line ~319), insert the image download step:

```python
# Step 3a: Download images (pandoc-arxiv only)
image_count = 0
if backend == "pandoc-arxiv" and output_dir is not None:
    markdown, image_count = _download_arxiv_images(
        markdown, final_url, output_dir
    )
```

Then at line 372, replace `image_count=0` with `image_count=image_count`.

**Sequencing concern:** `output_dir` may not be determined yet at line 289 — it's computed at line ~338-348. The image download needs to happen after `output_dir` is known. Two options:

- **(A) Move image download after output_dir is determined** (line ~349). This is cleanest — just insert the call between `output_dir.mkdir()` and the markdown write.
- (B) Compute output_dir earlier. Unnecessary complexity.

**Choice: Option A** — insert image download at line ~350, after `output_dir.mkdir()` and before `md_path.write_text()`.

### Data flow

```
extract_web_content()
  ├── fetch HTML
  ├── sanitize
  ├── Pandoc extraction → markdown with remote image refs
  ├── determine output_dir
  ├── mkdir output_dir
  ├── _download_arxiv_images(markdown, url, output_dir)  ← NEW
  │     ├── parse markdown for ![...](...) refs
  │     ├── for each image URL:
  │     │     ├── resolve to absolute URL
  │     │     ├── download bytes (with size limit)
  │     │     ├── save to output_dir/images/filename.png
  │     │     └── rewrite markdown ref to images/filename.png
  │     └── return (rewritten_markdown, count)
  ├── write markdown file (now with local image refs)
  ├── write metrics
  └── return ExtractionResult(image_count=count)
```

### Edge cases

| Case | Handling |
|------|----------|
| `data:` URI | Skip, leave unchanged |
| Download fails (404, timeout) | Log warning, leave original ref, don't count |
| Image > 10 MB | Skip with warning |
| Duplicate filenames | Append `_2`, `_3` suffix before extension |
| No images in markdown | Return (markdown, 0) — no-op |
| `output_dir` is None | Skip image download, return count=0 |
| Non-arXiv backend | Skip entirely (only runs for `pandoc-arxiv`) |

---

## Potential Risks

1. **Network latency**: Downloading 10-15 images adds ~5-10 seconds. Acceptable per NFR-2 given the value of having figures locally.
2. **arXiv rate limiting**: Unlikely for ~15 images per paper but worth noting. The User-Agent header is already set.
3. **Filename collisions**: Handled by dedup suffix.

---

## Integration Strategy

- Only affects the `pandoc-arxiv` code path — trafilatura and pandoc-fallback paths are untouched
- `--save-source` is unaffected (FR-7) — it saves HTML, this saves images
- The `images/` directory convention matches the PDF pipeline's `ImageCollector`

---

## Validation Approach

### Tests

**File:** `tests/test_web_backend.py` (or new `tests/test_web_images.py`)

1. **Unit test `_download_arxiv_images()`** with mocked HTTP:
   - Markdown with 2 image refs → downloads both, rewrites paths
   - One image 404 → downloads the other, warns, leaves broken ref unchanged
   - `data:` URI → skipped
   - Oversized image → skipped with warning

2. **Integration**: Existing tests must pass. The function is only called for `pandoc-arxiv` backend, so non-arXiv tests are unaffected.

### Manual verification

```bash
uv run agentic-mbse extract https://arxiv.org/html/2411.06644v1 --output /tmp/test-images
ls /tmp/test-images/images/  # should contain PNGs
grep 'images/' /tmp/test-images/output.md  # should show local refs
```

---

**Next Step:** After approval → `/_my_implement` or `/_my_plan`

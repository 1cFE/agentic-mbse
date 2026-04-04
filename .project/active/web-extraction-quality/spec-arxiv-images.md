# Spec: arXiv HTML Image Downloading

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-04-04
**Complexity:** LOW-MEDIUM
**Branch:** `webfetch-tools`

---

## Business Goals

### Why This Matters

When research agents extract arXiv HTML papers via `agentic-mbse extract <url>`, the markdown output contains image references pointing to remote relative paths (e.g., `/html/2512.08027v1/figures/POPCON.png`). The actual image files are not downloaded. This means:

- Agents cannot view or interpret figures when answering questions about papers
- Users asking about plots, diagrams, or schematics get text-only descriptions instead of quantitative answers from the actual figures
- The extracted source is incomplete — figures carry information not present in the text

This was directly observed when an agent couldn't explain Figure 3 (a POPCON plot) from the Helios stellarator paper because the PNG wasn't available locally.

### Success Criteria

- [ ] After extracting an arXiv HTML paper, all referenced images are saved locally in an `images/` subdirectory alongside the markdown output
- [ ] Image references in the markdown point to local relative paths (e.g., `images/POPCON.png`)
- [ ] `ExtractionResult.image_count` reflects the actual number of downloaded images (not hardcoded 0)
- [ ] Agents can view/reference figures from extracted arXiv sources

### Priority

High — direct follow-on to the arXiv Pandoc routing fix (commit `1b155a0`). Part of SOURCE-FIX epic Item 1 (`fusion-tea/.project/backlog/epic_source_extraction_fix.md`).

---

## Problem Statement

### Current State

The `pandoc-arxiv` extraction path produces markdown with image references like:

```markdown
![Refer to caption](/html/2512.08027v1/figures/POPCON.png){#S3.F3.g1 ...}
```

These are relative paths on `arxiv.org`. The images are not downloaded. `ExtractionResult.image_count` is hardcoded to `0` in `web_backend.py:372`.

### Desired Outcome

Images referenced in the extracted markdown are downloaded to a local `images/` directory. Markdown references are rewritten to point to the local files. The extraction result reports the actual image count.

---

## Scope

### In Scope

- Downloading images referenced in arXiv HTML extractions (`pandoc-arxiv` backend path)
- Saving images to `images/` subdirectory within the output directory
- Rewriting markdown image references to use local relative paths
- Reporting actual image count in `ExtractionResult`
- Maximizing reuse of existing patterns and utilities in the codebase

### Out of Scope

- Image downloading for non-arXiv web pages (trafilatura / pandoc-fallback paths)
- Image analysis, captioning, or OCR
- SVG rasterization
- Changes to the PDF extraction image pipeline

### Edge Cases & Considerations

- **Download failures**: Individual image failures MUST NOT fail the overall extraction
- **Image size**: arXiv figures are typically small PNGs (< 1 MB each), but a reasonable size limit should be enforced
- **Duplicate filenames**: Multiple papers could have images with the same filename (e.g., `figure1.png`); the output directory is per-extraction so this shouldn't collide, but worth considering
- **`data:` URIs**: Should be skipped if encountered
- **Already-fetched HTML**: The HTML is already in memory from the fetch step; image URLs should be resolved against the page's base URL without re-fetching the HTML

---

## Requirements

### Functional Requirements

1. **FR-1**: Images referenced in the `pandoc-arxiv` extraction output MUST be downloaded and saved to an `images/` subdirectory within the extraction output directory.

2. **FR-2**: Image references in the output markdown MUST be rewritten to use relative local paths (e.g., `images/POPCON.png`).

3. **FR-3**: `ExtractionResult.image_count` MUST reflect the actual number of successfully downloaded images.

4. **FR-4**: Individual image download failures MUST NOT fail the overall extraction. Failures SHOULD be logged as warnings.

5. **FR-5**: Image downloads SHOULD have a per-image size limit to prevent runaway downloads.

6. **FR-6**: `data:` URI image references MUST be skipped (not downloaded).

7. **FR-7**: [INFERRED] The `--save-source` flag behavior MUST be unaffected — it saves the original HTML, not images.

8. **FR-8**: [INFERRED] The implementation SHOULD maximize reuse of existing patterns and utilities in the extraction codebase.

### Non-Functional Requirements

9. **NFR-1**: Existing tests MUST continue to pass.

10. **NFR-2**: Image downloading SHOULD NOT significantly increase extraction time for papers with few images (typical arXiv papers have 5-15 figures).

---

## Acceptance Criteria

### Core Functionality

- [ ] `uv run agentic-mbse extract https://arxiv.org/html/2411.06644v1 --output /tmp/test` produces an `images/` directory with downloaded PNGs
- [ ] Markdown in the output references `images/filename.png` (relative paths)
- [ ] `ExtractionResult.image_count` > 0 for a paper with figures
- [ ] A paper with a broken/missing image URL still extracts successfully with a warning logged

### Quality & Integration

- [ ] All existing tests pass (`uv run pytest tests/`)
- [ ] Image downloading has test coverage (may use mocked HTTP)

---

## Related Artifacts

- **Previous fix:** Commit `1b155a0` — arXiv HTML routing to Pandoc pipeline
- **Spec (parent):** `.project/active/web-extraction-quality/spec.md`
- **Upstream epic:** `fusion-tea/.project/backlog/epic_source_extraction_fix.md` Item 1
- **Web backend:** `src/agentic_mbse/extraction/web_backend.py`
- **Existing image patterns:** `src/agentic_mbse/extraction/pipeline.py` (ImageCollector), `src/agentic_mbse/extraction/http.py` (fetch utilities)

---

**Next Steps:** After approval, proceed to `/_my_design`

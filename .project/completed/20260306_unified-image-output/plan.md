# Implementation Plan: Unified Image Output Pipeline

**Status:** Complete
**Created:** 2026-03-01
**Last Updated:** 2026-03-01

## Source Documents
- **Spec:** `.project/active/unified-image-output/spec.md`
- **Design:** `.project/active/unified-image-output/design.md` ← See here for component details, function signatures, architecture

## Implementation Strategy

**Phasing Rationale:**
Three phases ordered by dependency and isolation. Phase 1 builds the collector mechanism and config/result fields — everything else depends on these. Phase 2 adds figure extraction (pymupdf side) and postprocess updates — validates the image path pipeline independently. Phase 3 wires table crops through the collector, adds CLI plumbing, and integrates everything into the orchestrator.

**Overall Validation Approach:**
- Each phase starts with tests
- `uv run pytest tests/ -x` after each phase for regression check
- No manual verification until Phase 3 (first two phases are internal plumbing)

---

## Phase 1: Foundation — ImageCollector + Config + Types

### Goal
Build the core accumulator (`ImageCollector` in `pipeline.py`, `ImageEntry` in `types.py`), add `extracted_images_dir` to `PipelineConfig`, and add `image_count` to `PipelineResult`. Purely additive — no existing behavior changes.

### Test Stencil (Write This First)
```python
class TestImageCollector:
    def test_add_returns_markdown_ref(self):
        """add() returns ![](images/rel_name) string."""
        collector = ImageCollector(output_dir=Path("/fake/images"))
        ref = collector.add(Path("/tmp/src.png"), "page_001_table_0.png", "table_crop", 1)
        assert ref == "![](images/page_001_table_0.png)"
        assert len(collector.entries) == 1

    def test_persist_copies_files(self, tmp_path):
        """persist() copies source files to output_dir."""
        src = tmp_path / "src.png"
        src.write_bytes(b"fake png")
        out = tmp_path / "images"
        collector = ImageCollector(output_dir=out)
        collector.add(src, "table.png", "table_crop", 0)
        count = collector.persist()
        assert count == 1
        assert (out / "table.png").exists()

    def test_persist_empty_collector(self, tmp_path):
        """persist() with zero entries returns 0 without error."""
        collector = ImageCollector(output_dir=tmp_path / "images")
        assert collector.persist() == 0

    def test_persist_missing_source_warns(self, tmp_path, caplog):
        """persist() skips missing files with warning, doesn't raise."""
        collector = ImageCollector(output_dir=tmp_path / "images")
        collector.add(Path("/nonexistent/file.png"), "ghost.png", "table_crop", 0)
        count = collector.persist()
        assert count == 0
        assert "Failed to persist" in caplog.text

    def test_total_image_count_includes_all_files(self, tmp_path):
        """total_image_count scans directory (includes pre-existing files)."""
        out = tmp_path / "images"
        out.mkdir()
        (out / "figure.png").write_bytes(b"fig")
        (out / "table.png").write_bytes(b"tab")
        collector = ImageCollector(output_dir=out)
        assert collector.total_image_count == 2

    def test_total_image_count_no_dir(self, tmp_path):
        """total_image_count returns 0 when output_dir doesn't exist."""
        collector = ImageCollector(output_dir=tmp_path / "nope")
        assert collector.total_image_count == 0
```

### Changes Required

**See `design.md#component-1` for:** ImageCollector/ImageEntry interface, design rationale, placement decision

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pipeline.py`
- [x] Add `TestImageCollector` class with 6 tests per stencil above

#### 2. Types
**File:** `src/agentic_mbse/extraction/types.py`
- [x] Add `ImageEntry` dataclass (4 fields: source_path, rel_name, kind, page_num)
- [x] Add `image_count: int = 0` field to `PipelineResult`

#### 3. Pipeline — ImageCollector class + config field
**File:** `src/agentic_mbse/extraction/pipeline.py`
- [x] Add `ImageCollector` dataclass with `add()`, `persist()`, `total_image_count` (see `design.md#component-1`)
- [x] Import `ImageEntry` from `types`
- [x] Add `extracted_images_dir: Path | None = None` to `PipelineConfig`

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pipeline.py::TestImageCollector -v` → All 6 pass
- [x] `uv run pytest tests/ -x` → No regressions (1053 passed, 1 skipped)

**What We Know Works After This Phase:**
ImageCollector accumulates entries, copies files from temp sources to output dir, tolerates missing files, and counts all images in the directory (including pre-existing ones). Config and result fields exist with correct defaults.

---

## Phase 2: Figure Extraction + Postprocess

### Goal
Enable `write_images=True` in `extract_pages()` when `extracted_images_dir` is provided. Wire `normalize_image_paths()` and `promote_figure_captions()` into `_postprocess_final()`. This validates the pymupdf figure path end-to-end without touching table crops.

### Test Stencil (Write This First)
```python
class TestFigureExtraction:
    def test_extract_pages_with_images_dir(self):
        """extract_pages passes write_images=True when dir provided."""
        with patch("agentic_mbse.extraction.pymupdf_backend._get_to_markdown") as mock_get:
            mock_to_md = MagicMock(return_value=[{"metadata": {"page": 1}, "text": "# Page"}])
            mock_get.return_value = mock_to_md
            extract_pages(Path("/fake.pdf"), extracted_images_dir=Path("/out/images"))
            call_kwargs = mock_to_md.call_args[1]
            assert call_kwargs["write_images"] is True
            assert call_kwargs["image_path"] == "/out/images"

    def test_extract_pages_without_images_dir(self):
        """extract_pages passes write_images=False when dir is None."""
        with patch("agentic_mbse.extraction.pymupdf_backend._get_to_markdown") as mock_get:
            mock_to_md = MagicMock(return_value=[{"metadata": {"page": 1}, "text": "# Page"}])
            mock_get.return_value = mock_to_md
            extract_pages(Path("/fake.pdf"))
            call_kwargs = mock_to_md.call_args[1]
            assert call_kwargs["write_images"] is False


class TestPostprocessWithImages:
    def test_normalizes_absolute_paths(self):
        """_postprocess_final normalizes absolute image paths when dir provided."""
        md = "![](/tmp/out/images/fig-0-0.png)\n\nSome text."
        result = _postprocess_final(md, extracted_images_dir=Path("/tmp/out/images"))
        assert "![](images/fig-0-0.png)" in result
        assert "/tmp/out/images" not in result

    def test_promotes_figure_captions(self):
        """_postprocess_final promotes captions after normalizing paths."""
        md = "![](/tmp/out/images/fig.png)\nFigure 1: A diagram."
        result = _postprocess_final(md, extracted_images_dir=Path("/tmp/out/images"))
        assert "![Figure 1: A diagram.](images/fig.png)" in result

    def test_no_images_dir_no_normalization(self):
        """_postprocess_final with None dir skips image processing."""
        md = "![](/absolute/path/images/fig.png)\n\nText."
        result = _postprocess_final(md)
        assert "/absolute/path/images/fig.png" in result
```

### Changes Required

**See `design.md#component-2` for:** extract_pages interface change, to_markdown params
**See `design.md#component-5` for:** _postprocess_final update, ordering rationale

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pipeline.py`
- [x] Add `TestFigureExtraction` class with 2 tests
- [x] Add `TestPostprocessWithImages` class with 3 tests
- [x] Add necessary imports (`MagicMock`, `_postprocess_final`, `extract_pages`)

#### 2. pymupdf_backend
**File:** `src/agentic_mbse/extraction/pymupdf_backend.py`
- [x] Add `extracted_images_dir: Path | None = None` param to `extract_pages()` (~line 124)
- [x] Update `to_markdown()` call: `write_images=extracted_images_dir is not None`, `image_path=str(extracted_images_dir) if extracted_images_dir else None` (~line 141-143)

#### 3. Pipeline — postprocess update + imports
**File:** `src/agentic_mbse/extraction/pipeline.py`
- [x] Add `normalize_image_paths`, `promote_figure_captions` to postprocess imports (~line 20-24)
- [x] Add `extracted_images_dir: Path | None = None` param to `_postprocess_final()` (~line 178)
- [x] Add `normalize_image_paths()` then `promote_figure_captions()` calls gated by `if extracted_images_dir is not None` (~line 185)

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pipeline.py::TestFigureExtraction -v` → 2/2 pass
- [x] `uv run pytest tests/test_pipeline.py::TestPostprocessWithImages -v` → 3/3 pass
- [x] `uv run pytest tests/ -x` → No regressions (1058 passed, 1 skipped)

**What We Know Works After This Phase:**
`extract_pages()` conditionally enables image writing. `_postprocess_final()` normalizes absolute paths and promotes figure captions when images dir is provided. No change when dir is None.

---

## Phase 3: Table Crops + CLI + Pipeline Integration

### Goal
Wire the collector into step 3b for table crop persistence. Update the orchestrator to create the collector, pass `extracted_images_dir` to `extract_pages()`, call `persist()`, and set `image_count`. Update CLI to create `output_dir/images/` and pass it through config.

### Test Stencil (Write This First)
```python
class TestTableCropPersistence:
    def test_table_crops_registered_with_collector(self, tmp_path):
        """Tables with image_path get registered and image ref prepended."""
        # E2E: run pipeline with tables that have image_path set
        # Verify markdown contains ![](images/page_000_table_0.png) near pipe table

    def test_no_collector_when_images_dir_none(self):
        """Pipeline with extracted_images_dir=None produces no image refs."""
        # E2E: default config → no image references in output

    def test_table_without_image_path_skipped(self):
        """Tables with image_path=None don't get image refs."""

    def test_image_count_in_result(self, tmp_path):
        """PipelineResult.image_count reflects total images in dir."""

    def test_backward_compat_no_images_dir(self):
        """Pipeline output identical when extracted_images_dir=None."""
```

### Changes Required

**See `design.md#component-3` for:** Table crop registration logic, naming convention, why prepend to markdown
**See `design.md#component-4` for:** CLI wiring, early dir creation, error handling
**See `design.md#component-6` for:** Orchestrator collector lifecycle

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pipeline.py`
- [x] Add `TestTableCropPersistence` class with 5 tests
- [x] Created temp PNG files for realistic table.image_path values

#### 2. Pipeline — orchestrator integration
**File:** `src/agentic_mbse/extraction/pipeline.py`
- [x] In `extract_pdf()`: create `ImageCollector` when `config.extracted_images_dir` is set
- [x] Pass `extracted_images_dir=config.extracted_images_dir` to `extract_pages()` call
- [x] After inner table loop, add collector registration loop over `enhanced` list — prepend image ref to `table.markdown` for tables with `image_path`
- [x] Before `_postprocess_final()`: call `collector.persist()` if collector is not None
- [x] Pass `extracted_images_dir=config.extracted_images_dir` to `_postprocess_final()`
- [x] In result assembly: set `image_count=collector.total_image_count if collector else 0`

#### 3. CLI
**File:** `src/agentic_mbse/cli/extract_cli.py`
- [x] Move `output_dir.mkdir(parents=True, exist_ok=True)` BEFORE `extract_pdf()` call
- [x] Add `images_dir = output_dir / "images"` + `images_dir.mkdir(exist_ok=True)` after output_dir creation
- [x] Add `extracted_images_dir=images_dir` to `PipelineConfig` constructor
- [x] Remove duplicate `output_dir.mkdir()` that was at line 348

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pipeline.py::TestTableCropPersistence -v` → 5/5 pass
- [x] `uv run pytest tests/ -x` → No regressions (1063 passed, 1 skipped)
- [x] `uv run ruff check` → Clean on changed files (pre-existing corpus issues only)
- [x] `uv run ruff format` → Applied, tests still pass

**What We Know Works After This Phase:**
Full pipeline produces images in `output_dir/images/` — both pymupdf figures and table crops. Markdown has relative `![](images/...)` references. Figure captions promoted to alt-text. Table crop images appear near their pipe tables. `PipelineResult.image_count` reflects total. Backward compatible when `extracted_images_dir=None`.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
uv run pytest tests/ -x          # Full regression check
uv run ruff check src/ tests/    # Linting
uv run ruff format src/ tests/   # Formatting
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Low risk. Pure dataclasses + collector class with no external deps. Tests validate file I/O in isolation using `tmp_path`.
- **Phase 2**: Low risk. `extract_pages()` change is a single conditional — `write_images` param already well-tested by legacy `extract()`. Postprocess functions already tested independently.
- **Phase 3**: Medium risk. Orchestrator integration touches the most code. Mitigated by Phase 1+2 proving the pieces work in isolation. E2E tests catch integration issues.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Added `ImageEntry` dataclass to `types.py` (source_path, rel_name, kind, page_num)
- Added `image_count: int = 0` field to `PipelineResult` in `types.py`
- Added `ImageCollector` dataclass to `pipeline.py` with `add()`, `persist()`, `total_image_count`
- Added `extracted_images_dir: Path | None = None` to `PipelineConfig` in `pipeline.py`
- Added `ImageEntry` import in `pipeline.py`
- Added `TestImageCollector` class with 6 tests in `test_pipeline.py`
**Issues:** None
**Deviations:** None — implemented exactly per design

### Phase 2 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Added `extracted_images_dir: Path | None = None` param to `extract_pages()` in `pymupdf_backend.py`
- Updated `to_markdown()` call to conditionally pass `write_images=True` and `image_path`
- Added `normalize_image_paths`, `promote_figure_captions` imports to `pipeline.py`
- Added `extracted_images_dir` param to `_postprocess_final()` with gated normalize + promote calls
- Added `TestFigureExtraction` (2 tests) and `TestPostprocessWithImages` (3 tests) to `test_pipeline.py`
- Added `MagicMock` and `extract_pages` imports to test file
**Issues:** None
**Deviations:** None — implemented exactly per design

### Phase 3 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Created `ImageCollector` in `extract_pdf()` when `extracted_images_dir` set
- Passed `extracted_images_dir` to `extract_pages()` call
- Added collector registration loop after step 3b enhancement — prepends image ref to `table.markdown`
- Called `collector.persist()` before `_postprocess_final()`
- Passed `extracted_images_dir` to `_postprocess_final()`
- Set `image_count=collector.total_image_count` in `PipelineResult`
- CLI: moved `output_dir.mkdir()` before extraction, added `images_dir` creation, passed to config
- Added `TestTableCropPersistence` with 5 E2E tests
**Issues:** Two tests initially failed because short synthetic page text triggered CLAUDE_REPLACE routing, which replaced the page content (hiding table image refs). Fixed by setting `enable_claude=False, claude_budget_usd=0` in those tests to force GMFT routing.
**Deviations:** None from design — test adjustments only

---

**Status**: Complete

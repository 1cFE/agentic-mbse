# Design: Unified Image Output Pipeline

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-03-01 14:50 PST
**Branch:** `doc-ingest-clean`
**Last Commit:** `c989e93`

## Overview

Build an `ImageCollector` that manages table crop persistence from temp directories to `output_dir/images/`, while pymupdf4llm handles figure extraction directly via `write_images=True`. Both image types land in the same output directory. Postprocess cleanup normalizes paths and promotes figure captions.

## Related Artifacts

- **Spec:** `.project/active/unified-image-output/spec.md`
- **Epic:** `.project/backlog/epic_pdf-extraction-improvements.md` (Item 2)
- **Quality regressions design:** `.project/active/v4-output-quality-regressions/design.md` (Component 4 — reference material)
- **Pipeline internals:** `docs/extraction-internals.md`

---

## Research Findings

### pymupdf4llm Image Handling

`extract_pages()` (`pymupdf_backend.py:124-157`) calls `to_markdown()` with `write_images=False`. The legacy `extract()` function (`pymupdf_backend.py:160-221`) calls it with `write_images=True, image_path=str(images_dir)`.

When `write_images=True`:
- pymupdf4llm saves embedded images as PNGs to the `image_path` directory
- Image references in markdown use absolute paths: `![](/absolute/path/to/images/doc-0-0.png)`
- Naming convention: `{stem}-{page_num}-{img_num}.png` where stem is the PDF filename stem
- Page images (rendered page as image for Claude vision) are a separate concept — `PipelineConfig.page_image_dir` exists for that purpose

### Table Crop Image Lifecycle

Table detectors create temp directories and save crops:
- `_detect_gmft()` (`tables.py:371`): `Path(tempfile.mkdtemp(prefix="gmft_"))`
- `_detect_img2table()` (`tables.py:444`): `Path(tempfile.mkdtemp(prefix="img2table_"))`
- `_save_table_image()` (`tables.py:273-293`): names files `page_{page_idx:03d}_table_{table_idx}.png`
- Paths stored in `DetectedTable.image_path` (`types.py:34`)
- Used by `enhance_table_with_claude()` (`tables.py:548-604`) for Claude vision
- After pipeline completes, temp dirs are abandoned — never cleaned up, never persisted

### Existing Postprocess Functions

Two functions needed for image handling, both in `postprocess.py`:

| Function | Signature | Purpose | Reference |
|----------|-----------|---------|-----------|
| `normalize_image_paths()` | `(md: str, images_dir: Path) -> str` | Replace absolute pymupdf paths with relative `images/` | `postprocess.py:252-255` |
| `promote_figure_captions()` | `(md: str) -> str` | Move `Figure N:` text into image alt-text | `postprocess.py:343-362` |

Both are already tested in `test_postprocess.py:363-381` and `test_postprocess.py:430-457`.

`promote_figure_captions()` matches pattern: `![](images/...)` followed by `Figure N:` text within 1-2 lines. This means it must run AFTER `normalize_image_paths()` (which converts absolute paths to `images/...`).

### Current `_postprocess_final()`

`pipeline.py:178-187`:
```python
def _postprocess_final(markdown: str) -> str:
    markdown = strip_page_numbers(markdown)
    markdown = strip_running_headers(markdown)
    markdown = repair_ligatures(markdown)
    return markdown
```

Needs two additions: `normalize_image_paths()` and `promote_figure_captions()`. Order matters — normalize must come before caption promotion.

### Table Insertion Functions

`insert_tables_at_end()` (`tables.py:132-143`) appends table markdown at page end. `replace_tables()` (`tables.py:146-151`) strips existing pipe tables then appends. Both take `tables: list[DetectedTable]` and use `table.markdown` directly.

Key insight: if we prepend an image reference to `DetectedTable.markdown` during step 3b, it flows through `insert_tables_at_end()` and `replace_tables()` with zero changes to those functions.

### Pipeline Config

`PipelineConfig` (`pipeline.py:102-114`) has `page_image_dir: Path | None = None` for pre-rendered page PNGs (Claude vision). The new `extracted_images_dir` field is conceptually distinct — it's the output directory for document-embedded figures and table crops.

### CLI Output Flow

`cmd_extract()` (`extract_cli.py:319-376`):
1. Checks skip condition
2. Creates `PipelineConfig`
3. Calls `extract_pdf()`
4. Creates `output_dir` AFTER extraction succeeds (`extract_cli.py:348`)
5. Writes `output.md`, `metrics.json`, `decisions.json`, `cost.json`

The images dir must be created BEFORE extraction (pymupdf needs it for `write_images=True`). This means moving `output_dir.mkdir()` earlier and adding `images_dir.mkdir()`.

### Test Patterns

Pipeline tests (`test_pipeline.py:1-112`):
- Helpers: `_page()`, `_table()`, `_cost()` for synthetic data
- Patching: `_patch_base()`, `_patch_tables()`, `_patch_claude_page()`, `_patch_which_claude()`
- All external deps mocked, business logic runs real
- E2E tests use `extract_pdf()` with patches; unit tests import internal functions directly

---

## Proposed Design

### Architecture Overview

```
                        Changed
                        ┌──────┐
1. arXiv shortcut       │      │
2. Base extraction    ← │ (A)  │  Add extracted_images_dir param
3. Table detection      │      │
3b. Table filter      ← │ (B)  │  Register table crops with collector
4. Quality gate         │      │
  4b. GMFT xref        │      │
5. Budget allocation    │      │
6. Claude enhance       │      │
7. Route and merge      │      │
  7b. Postprocess     ← │ (C)  │  Persist collector, normalize paths,
                        │      │  promote captions
8. Assemble           ← │ (D)  │  image_count in PipelineResult
                        └──────┘
```

Four changes (A–D) integrate into the existing pipeline without restructuring any existing steps.

### Component 1: ImageCollector + ImageEntry (`types.py`)

**Purpose:** Accumulate table crop (and future equation crop) images from temp directories and copy them to the output directory.

**Why the collector doesn't manage figures:** pymupdf4llm writes figures directly to `extracted_images_dir` via `write_images=True, image_path=str(dir)`. The images are already in the output location — having the collector "register" and "copy" them would be a no-op. The collector's value is managing images that start in temp directories and need copying to the final output location.

**Interface:**

```python
@dataclass
class ImageEntry:
    source_path: Path       # temp file that needs copying
    rel_name: str           # "page_003_table_1.png"
    kind: str               # "table_crop" | "equation_crop"
    page_num: int


@dataclass
class ImageCollector:
    output_dir: Path
    entries: list[ImageEntry] = field(default_factory=list)

    def add(self, source_path: Path, rel_name: str,
            kind: str, page_num: int) -> str:
        """Register an image for persistence. Returns markdown ref."""
        self.entries.append(
            ImageEntry(source_path, rel_name, kind, page_num)
        )
        return f"![](images/{rel_name})"

    def persist(self) -> int:
        """Copy all registered images to output_dir. Returns count."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for entry in self.entries:
            dest = self.output_dir / entry.rel_name
            try:
                shutil.copy2(entry.source_path, dest)
                count += 1
            except (FileNotFoundError, OSError) as exc:
                logger.warning(
                    "Failed to persist %s: %s", entry.rel_name, exc
                )
        return count

    @property
    def total_image_count(self) -> int:
        """Count all image files in output_dir (figures + collected)."""
        if not self.output_dir.exists():
            return 0
        return sum(1 for f in self.output_dir.iterdir() if f.is_file())
```

**Design rationale:**
- `add()` returns a markdown string so callers can immediately embed references
- `persist()` uses `shutil.copy2` (not move) — source files may still be needed by other pipeline steps, and the spec requires tolerating missing files
- `total_image_count` scans the directory to include both pymupdf figures and collector-copied images — this is the number that goes into `PipelineResult.image_count`
- Missing source files produce warnings, not errors (FR-3)
- `shutil` import already exists in `pipeline.py`; `types.py` will need it added

**Location:** `ImageEntry` goes in `types.py` (pure dataclass, no I/O — consistent with the other 6 dataclasses there). `ImageCollector` goes in `pipeline.py` (it does file I/O via `shutil.copy2` and `Path.iterdir()` — `pipeline.py` already imports `shutil`). This preserves `types.py` as a data-only module.

### Component 2: Figure Extraction in `extract_pages()` (`pymupdf_backend.py`)

**What:** Add `extracted_images_dir` parameter to `extract_pages()`. When provided, pass `write_images=True` and `image_path=str(extracted_images_dir)` to `to_markdown()`.

**Interface change:**

```python
def extract_pages(
    pdf_path: Path,
    extracted_images_dir: Path | None = None,
) -> list[PageResult]:
```

**In the `to_markdown()` call:**

```python
chunks = to_markdown(
    str(pdf_path),
    write_images=extracted_images_dir is not None,
    image_path=str(extracted_images_dir) if extracted_images_dir else None,
    dpi=150,
    page_chunks=True,
    hdr_info=_composite_header_detector,
    table_strategy="lines",
    ignore_code=True,
    force_text=True,
)
```

**Backward compatibility:** When `extracted_images_dir` is None (default), behavior is identical to current code (`write_images=False`).

**Image path format:** pymupdf4llm produces `![](/absolute/path/to/images/stem-page-img.png)` in the per-page markdown. These absolute paths are normalized to relative `images/` paths in step 7b by `normalize_image_paths()`.

### Component 3: Table Crop Registration (pipeline step 3b)

**What:** After table filtering and enhancement in step 3b, register each surviving table's crop image with the collector. Prepend the image reference to the table's markdown so it flows through `insert_tables_at_end()` / `replace_tables()` unchanged.

**Where:** Inside the existing table processing loop in `extract_pdf()` (`pipeline.py:296-334`), after a table is appended to `enhanced`.

**Logic:**

```python
# After enhanced.append(table) or enhanced.append(etable):
if collector is not None and table.image_path is not None:
    rel_name = f"page_{page_num:03d}_table_{i}.png"
    img_ref = collector.add(table.image_path, rel_name, "table_crop", page_num)
    # Prepend image reference to table markdown
    table.markdown = f"{img_ref}\n\n{table.markdown}"
```

Wait — we need to be careful about which `table` object we're modifying. If Claude enhanced the table, we have `etable` (new object); if not, we have the original `table`. The image reference should be prepended to whichever table ends up in `enhanced`.

**Refined logic** — add image reference at the point where we know the table will be used:

```python
for i, table in enumerate(kept):
    needs_enhance, _assess_reasons = assess_table_quality(table)

    if needs_enhance and claude_available:
        # ... Claude enhancement block (existing) ...
        # On success: enhanced.append(etable); continue
        # On failure: falls through

    # No Claude enhancement path
    if table.extraction_failed:
        continue
    enhanced.append(table)

# After the inner loop, add image references to all surviving tables
if collector is not None:
    for i, table in enumerate(enhanced):
        if table.image_path is not None:
            rel_name = f"page_{page_num:03d}_table_{i}.png"
            img_ref = collector.add(
                table.image_path, rel_name, "table_crop", page_num
            )
            table.markdown = f"{img_ref}\n\n{table.markdown}"
```

**Why prepend to markdown?** This avoids changing `insert_tables_at_end()` or `replace_tables()` signatures. The image reference becomes part of the table block and naturally appears near the pipe table in the output. Satisfies FR-11 (table crop references near their pipe tables).

**Naming convention:** `page_{NNN}_table_{M}.png` matches the existing `_save_table_image()` naming in `tables.py:285`. The index `M` is the position within the `enhanced` list (post-filter), not the raw detection index.

### Component 4: PipelineConfig + CLI Wiring

**PipelineConfig change** (`pipeline.py:102-114`):

Add one field:
```python
extracted_images_dir: Path | None = None
```

**CLI wiring** (`extract_cli.py:319-376`):

The current flow creates `output_dir` AFTER extraction succeeds (`extract_cli.py:348`). This must change because pymupdf needs the images dir to exist before `to_markdown()` runs.

```python
# Before extraction — create dirs early
output_dir.mkdir(parents=True, exist_ok=True)
images_dir = output_dir / "images"
images_dir.mkdir(exist_ok=True)

config = PipelineConfig(
    claude_budget_usd=args.budget,
    claude_model=args.model,
    enable_tables=not args.no_tables,
    enable_img2table=not args.no_img2table,
    enable_docling=args.docling,
    arxiv_html_path=Path(args.html_path) if args.html_path else None,
    dry_run=args.dry_run,
    extracted_images_dir=images_dir,
)
result = extract_pdf(doc, config=config)

if result.error:
    # Clean up early-created dirs on failure
    ...
```

**Error handling:** If extraction fails, the empty `output_dir` and `images/` exist but no `output.md` is written. The existing skip check (`(output_dir / "output.md").exists()`) still works — next run with `--force` will redo. The empty dirs are harmless.

Remove the duplicate `output_dir.mkdir(parents=True, exist_ok=True)` that currently appears after extraction success (`extract_cli.py:348`).

### Component 5: Postprocess Update (`_postprocess_final()`)

**What:** Add `extracted_images_dir` parameter. When provided, call `normalize_image_paths()` and `promote_figure_captions()`.

**Updated interface:**

```python
def _postprocess_final(
    markdown: str,
    extracted_images_dir: Path | None = None,
) -> str:
    """Apply deterministic cleanup to the final merged markdown.

    Selectively applies ONLY the safe str→str transforms from
    postprocess.py. Does NOT apply header promotion/demotion (FR-4).
    """
    markdown = strip_page_numbers(markdown)
    markdown = strip_running_headers(markdown)
    markdown = repair_ligatures(markdown)
    if extracted_images_dir is not None:
        markdown = normalize_image_paths(markdown, extracted_images_dir)
        markdown = promote_figure_captions(markdown)
    return markdown
```

**Order matters:** `normalize_image_paths()` must run before `promote_figure_captions()` because the caption regex matches `![](images/...)` — the relative path form, not absolute.

**New imports in `pipeline.py`:**
```python
from agentic_mbse.extraction.postprocess import (
    normalize_image_paths,    # NEW
    promote_figure_captions,  # NEW
    repair_ligatures,
    strip_page_numbers,
    strip_running_headers,
)
```

### Component 6: Pipeline Orchestrator Changes (`extract_pdf()`)

**Collector lifecycle:**

```python
def extract_pdf(pdf_path, config=None):
    ...
    # Create collector if images dir is configured
    collector = None
    if config.extracted_images_dir:
        collector = ImageCollector(output_dir=config.extracted_images_dir)

    # Step 2: pass extracted_images_dir to extract_pages
    pages = extract_pages(pdf_path, extracted_images_dir=config.extracted_images_dir)

    # Step 3b: table loop adds image refs to collector (see Component 3)
    ...

    # Step 7b: persist collector, then postprocess
    if collector is not None:
        collector.persist()
    final_markdown = "\n\n".join(merged_pages)
    final_markdown = _postprocess_final(final_markdown, config.extracted_images_dir)

    # Step 8: assemble result with image_count
    image_count = collector.total_image_count if collector else 0
    return PipelineResult(
        ...,
        image_count=image_count,
    )
```

**Key ordering:** `collector.persist()` BEFORE `_postprocess_final()` — the postprocess step normalizes image paths in the markdown, which only works if the images are already in the output dir (for figure path normalization) and the table crop refs are already embedded in the page markdown (done in step 3b).

Wait — actually `collector.persist()` copies table crops, and `normalize_image_paths()` handles pymupdf absolute paths. These are independent. But `promote_figure_captions()` needs the normalized paths, so the order is: persist → normalize → promote. All correct.

Actually, `collector.persist()` timing relative to `"\n\n".join(merged_pages)` doesn't matter because the merged markdown already has the table crop references (prepended in step 3b) — they use relative paths from `collector.add()`. The persist just copies the actual files. So persist can happen before or after join. Putting it before the join is fine.

### Component 7: PipelineResult Update (`types.py`)

Add one field:

```python
@dataclass
class PipelineResult:
    ...
    image_count: int = 0
```

---

## Potential Risks

| Risk | Likelihood | Mitigation |
|------|:---:|-----------|
| pymupdf4llm `write_images=True` changes extraction timing or markdown content | Low | Same parameter used by legacy `extract()` for months. Only adds image references to markdown; text content unchanged. |
| Table crop temp files deleted before `persist()` runs | Low | `persist()` uses `shutil.copy2` with try/except per file. Missing files produce warnings, not pipeline failures. |
| `normalize_image_paths()` false-matches text that contains the absolute path string | Very Low | Uses `re.escape()` on the full dir path. Already tested in `test_postprocess.py:370-374`. |
| Prepending image ref to `table.markdown` breaks downstream consumers | Low | `insert_tables_at_end()` and `replace_tables()` treat markdown as opaque strings — prepended content is just more markdown. |
| Large PDFs with many images slow down pipeline due to file copies | Low | `shutil.copy2` is fast for small PNGs (table crops are typically < 500KB). Figures aren't copied at all (pymupdf writes directly). |

---

## Integration Strategy

- **No existing step is modified** — only new parameters added to existing functions
- **Backward compatibility guaranteed** — `extracted_images_dir=None` produces identical behavior to current pipeline
- **Postprocess functions already exist and are tested** — we're wiring them into `_postprocess_final()`, not writing new transforms
- **Table insertion functions unchanged** — image references ride along in `table.markdown`

---

## Validation Approach

### Unit Tests

| Component | Test File | New Tests | Description |
|-----------|-----------|:---------:|-------------|
| ImageCollector | `test_pipeline.py` | ~5 | add/persist/total_image_count, zero entries, missing source files |
| extract_pages with images | `test_pipeline.py` | ~2 | Verify `write_images=True` passed when dir provided, `False` when not |
| Table crop registration | `test_pipeline.py` | ~3 | Crops registered with collector, image ref prepended to markdown, no collector when None |
| _postprocess_final | `test_pipeline.py` | ~3 | Path normalization, caption promotion, no-op when None |
| PipelineResult.image_count | `test_pipeline.py` | ~1 | E2E: image_count reflects collector total |
| PipelineConfig | `test_pipeline.py` | ~1 | extracted_images_dir field exists and defaults to None |

### Regression Check

```bash
uv run pytest tests/ -x          # Full regression
uv run ruff check src/ tests/    # Linting
```

### Manual Verification

Re-extract the TEA cost analysis document and verify:
- `images/` directory contains PNGs (figures from pymupdf + table crops)
- `output.md` contains `![](images/...)` references (not absolute paths)
- Figure captions promoted to alt-text where applicable
- Table crop images appear near their corresponding pipe tables

---

## Files Changed Summary

| File | Changes |
|------|---------|
| `types.py` | Add `ImageEntry` dataclass; add `image_count: int = 0` to `PipelineResult` |
| `pymupdf_backend.py` | Add `extracted_images_dir` param to `extract_pages()`, conditionally enable `write_images` |
| `pipeline.py` | Add `ImageCollector` class; add `extracted_images_dir` to `PipelineConfig`; create collector in `extract_pdf()`; register table crops in step 3b; persist + pass images_dir to `_postprocess_final()` in step 7b; set `image_count` in step 8; add `normalize_image_paths`/`promote_figure_captions` imports and calls |
| `extract_cli.py` | Create `output_dir/images/` before extraction; pass `extracted_images_dir` in `PipelineConfig`; remove duplicate `output_dir.mkdir()` |
| `test_pipeline.py` | Tests for ImageCollector, extract_pages image param, table crop registration, postprocess with images, image_count E2E |

---

**Next Step:** After approval → `/_my_plan` for implementation phasing

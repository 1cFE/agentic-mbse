# Design: Equation Region Detection

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-03-01
**Branch:** doc-ingest-clean
**Commit:** 69ed20b

---

## Overview

Add equation region detection to the PDF extraction pipeline using Docling's `LayoutPredictor`, producing cropped equation images registered with the existing `ImageCollector` and placed inline near corresponding equation text.

## Related Artifacts

- **Spec:** `.project/active/equation-region-detection/spec.md`
- **Research:** `.project/research/20260301-192400_equation-region-detection-tools.md`
- **Learning tests:** `.project/active/equation-region-detection/learning-test.md`
- **Epic:** `.project/backlog/epic_pdf-extraction-improvements.md` (EPIC-PDFV4-002, Item 4)
- **Dependency:** Unified image output (Item 2, complete — provides `ImageCollector`)

## Research Findings

### Learning Test Results (LT-1 through LT-9)

Extensive experiments were run against the corpus. Key findings:

| Document | GT | Detected (NMS + conf≥0.5) | Result |
|----------|:--:|:--:|--------|
| hawker_2020 | 21 | 21 | exact match |
| paischer_2025 | 23 | 23 | exact match |
| hansen_2025 | 0 | 0 | perfect negative |
| seo_2024 (non-TeX) | ~2 | 2 | correct |

- **Confidence threshold 0.5** achieves 100% precision and 100% recall on test corpus
- **NMS (IoU ≥ 0.3)** eliminates duplicate bounding boxes (2 dupes on hawker page 6)
- **Zero false positives on inline-math-only document** — no height/width post-filtering needed
- **Crop quality excellent** — equation numbers included, no clipping, no padding needed
- **CPU inference ~0.85s/page** — significant overhead, must be gated
- **Batch prediction slower than sequential** — do not use `predict_batch()`
- **Font pre-filter NOT worth implementing** — misses non-TeX equations, marginal savings

Full details in `learning-test.md`.

### Codebase Patterns

**Table detection pattern** (`tables.py`): The equation detector mirrors the table detection architecture:
- Module-level singleton for detector instance (`tables.py:39-41`)
- Lazy import with `try/except ImportError` for graceful degradation (`tables.py:360-364`)
- Detection function returns `dict[int, list[Detected*]]` keyed by 0-based page number (`tables.py:352-418`)
- Error-isolated wrapper `_try_detect_*()` in pipeline (`pipeline.py:207-217`)
- Crop images saved to temp directory, registered with `ImageCollector` (`pipeline.py:400-406`)

**ImageCollector** (`pipeline.py:64-96`): Already supports `kind="equation_crop"` in its type definitions. `collector.add()` returns a markdown image reference string. `collector.persist()` copies all registered images to the output directory.

**PipelineConfig** (`pipeline.py:147-161`): Dataclass with boolean flags per feature. Equation detection joins `enable_tables`, `enable_img2table`, `enable_docling`.

**PipelineProfile** (`types.py:81-94`): Dataclass with per-step timing fields. Equation detection needs a new `equation_detection` field.

**Pipeline step numbering**: Currently Steps 1–8. Table detection is Step 3, table filtering is Step 3b. Equation detection becomes Step 3c.

### LayoutPredictor API

- **Import:** `from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor`
- **Constructor:** `LayoutPredictor(artifact_path=str, device="cpu", num_threads=4, base_threshold=0.3)`
- **Model path:** `~/.cache/huggingface/hub/models--docling-project--docling-layout-heron/snapshots/{hash}/`
- **predict():** Takes `PIL.Image.Image`, yields `{"label": str, "confidence": float, "l": float, "t": float, "r": float, "b": float}`
- **Formula label:** `label == "Formula"` (class ID 2 of 17 layout labels)
- **Init time:** 0.56s (singleton, one-time cost)

---

## Proposed Design

### Architecture Overview

```
equations.py (new)              pipeline.py (modified)         types.py (modified)
┌──────────────────┐            ┌──────────────────┐           ┌────────────────┐
│ detect_equations()│──returns──▶│ Step 3c:         │           │ DetectedEquation│
│   - singleton    │            │  _try_detect_eqs │           │ PipelineProfile │
│   - render page  │            │                  │           │   +equation_det │
│   - predict      │            │ Step 7:          │           │ PipelineConfig  │
│   - NMS          │            │  insert eq refs  │           │   +enable_eqs   │
│   - crop & save  │            │  via collector   │           └────────────────┘
└──────────────────┘            └──────────────────┘
```

### Component 1: `DetectedEquation` dataclass

**File:** `src/agentic_mbse/extraction/types.py`

```python
@dataclass
class DetectedEquation:
    confidence: float
    bbox: tuple[float, float, float, float] | None = None  # (l, t, r, b) in pixels at render DPI
    image_path: Path | None = None
    y_fraction: float = 0.0  # vertical center as fraction of page height (0=top, 1=bottom)
    is_display: bool = True  # always True — model at threshold 0.5 returns only display equations
```

`bbox` preserves the raw bounding box coordinates from the detector for downstream consumers (overlap checking with table regions, re-cropping at different DPI, debugging). `y_fraction` is the derived convenience field for inline placement, computed as `((t + b) / 2) / page_height`. `is_display` is always `True` given our detection approach — the model at conf ≥ 0.5 empirically returns only display equations (validated in LT-3/LT-8) — but the field makes the dataclass self-documenting per FR-2.

**Location:** After `ImageEntry`, before `PageAction` (`types.py:12`).

### Component 2: `equations.py` detector module

**File:** `src/agentic_mbse/extraction/equations.py` (new)

**Structure mirrors `tables.py`:**

```python
"""Equation region detection using Docling LayoutPredictor.

Detects display (block) equations on PDF pages, crops them as images,
and returns DetectedEquation objects for pipeline integration.

The LayoutPredictor dependency (docling-ibm-models) is guarded by lazy
import with try/except ImportError for graceful degradation.
"""

# Module-level singleton
_layout_predictor = None

def _get_predictor() -> LayoutPredictor:
    """Initialize or return cached LayoutPredictor singleton."""
    ...

def _nms(detections: list[LayoutDetection], iou_threshold: float = 0.3) -> list[LayoutDetection]:
    """Non-maximum suppression to remove overlapping bounding boxes."""
    ...

def detect_equations(
    pdf_path: Path,
    confidence_threshold: float = 0.5,
    save_images: bool = True,
) -> dict[int, list[DetectedEquation]]:
    """Detect display equations on all pages of a PDF.

    Returns dict mapping 0-indexed page number to detected equations.
    Returns empty dict if docling-ibm-models is not installed.
    """
    ...
```

#### `_get_predictor()`

Lazy-initializes the `LayoutPredictor` singleton. Uses the HuggingFace Hub API to resolve the model artifact path:

```python
from huggingface_hub import snapshot_download

artifact_path = snapshot_download("docling-project/docling-layout-heron")
```

This avoids hardcoding a snapshot hash. `snapshot_download` returns the cached path if already downloaded, or downloads on first use. This is the same approach Docling itself uses internally.

**Constructor args:** `device="cpu"`, `num_threads=4`, `base_threshold=0.3` (we apply our own 0.5 threshold after NMS, so the model's base threshold should be permissive to allow NMS to work properly).

#### `_nms()`

Simple IoU-based non-maximum suppression. Input type is documented with a `TypedDict`:

```python
class LayoutDetection(TypedDict):
    label: str
    confidence: float
    l: float
    t: float
    r: float
    b: float
```

Algorithm:

1. Sort detections by confidence descending
2. For each detection, check IoU against all kept detections
3. If IoU > threshold with any kept detection, suppress it
4. Return kept detections

IoU threshold: 0.3 (validated in learning tests — removes duplicates without losing true positives).

#### `detect_equations()`

Core flow for each page:

1. Render page to 200 DPI PIL Image via `pymupdf.Page.get_pixmap(dpi=200)`
2. Run `predictor.predict(image)` → list of detection dicts
3. Filter for `label == "Formula"`
4. Apply NMS (IoU threshold 0.3)
5. Filter by confidence threshold (0.5)
6. For each surviving detection:
   - Store `bbox = (l, t, r, b)` (raw pixel coordinates at render DPI)
   - Compute `y_fraction = ((t + b) / 2) / image_height`
   - If `save_images`: crop the bounding box region, save to tempdir as `page_{NNN}_eq_{M}.png`
   - Create `DetectedEquation(confidence, bbox, image_path, y_fraction, is_display=True)`
7. Return non-empty pages only

**Lazy import guard:**

```python
def detect_equations(...) -> dict[int, list[DetectedEquation]]:
    try:
        from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor  # noqa: F401
    except ImportError:
        return {}
    ...
```

**Temp directory:** Created once via `tempfile.mkdtemp(prefix="eqdet_")` when `save_images=True`. Same pattern as `_detect_gmft()` in `tables.py:371`.

### Component 3: Pipeline integration

**File:** `src/agentic_mbse/extraction/pipeline.py`

#### 3a. New import

```python
from agentic_mbse.extraction.equations import detect_equations
from agentic_mbse.extraction.types import DetectedEquation  # added to existing import
```

#### 3b. `PipelineConfig` changes

Add one field:

```python
@dataclass
class PipelineConfig:
    ...
    enable_equations: bool = True  # after enable_docling
```

Default `True` — but equation detection only runs when `extracted_images_dir` is also set (no images dir = no point detecting equations). This is a runtime check in the pipeline, not a config interaction.

#### 3c. Error-isolated wrapper

```python
def _try_detect_equations(pdf_path: Path, config: PipelineConfig) -> dict[int, list[DetectedEquation]]:
    """Detect equations with error isolation. Returns {} on failure."""
    try:
        return detect_equations(pdf_path)
    except Exception:
        logger.warning("Equation detection failed, continuing without equations", exc_info=True)
        return {}
```

Follows exact pattern of `_try_detect_tables()` at `pipeline.py:207-217`.

#### 3d. New pipeline step (Step 3c)

Inserted between Step 3b (table filter/enhance) and Step 4 (quality gate):

```python
    # ------------------------------------------------------------------
    # Step 3c: Equation detection (error-isolated)
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    if config.enable_equations and config.extracted_images_dir:
        detected_equations = _try_detect_equations(pdf_path, config)
    else:
        detected_equations = {}
    if prof:
        prof.equation_detection = time.perf_counter() - _t
```

**Gating logic:** Only runs when BOTH `enable_equations` and `extracted_images_dir` are set. This avoids the ~0.85s/page overhead when the user isn't requesting images.

#### 3e. Equation image registration and inline placement (in Step 7)

During the route/merge loop, after deciding which markdown to use for a page, insert equation crop references:

```python
    for i, page in enumerate(pages):
        pnum = page.page_num
        ...
        # (existing routing logic produces page_md)

        # Insert equation crop references
        if collector is not None and pnum in detected_equations:
            page_md = _insert_equation_refs(page_md, detected_equations[pnum], pnum, collector)

        merged_pages.append(page_md)
```

#### 3f. `_insert_equation_refs()` helper

```python
def _insert_equation_refs(
    page_md: str,
    equations: list[DetectedEquation],
    page_num: int,
    collector: ImageCollector,
) -> str:
    """Insert equation crop image references into page markdown.

    Places each equation's image reference at the line closest to its
    vertical position on the original page, preferring insertion after
    blank lines to avoid breaking paragraphs.
    """
```

**Placement algorithm:**

1. Split page markdown into lines
2. For each equation (sorted by `y_fraction`):
   a. Compute target line: `target = int(y_fraction * len(lines))`
   b. Register with collector: `ref = collector.add(eq.image_path, rel_name, "equation_crop", page_num)`
   c. Search forward from `target` for the nearest blank line (within 5 lines)
   d. If a blank line is found, insert `ref + "\n"` after it
   e. If no blank line nearby, insert after `target` line
3. Return the reassembled markdown

This approach:
- Works for all page types (KEEP, CLAUDE_REPLACE, GMFT_REPLACE, etc.)
- Doesn't depend on equation number patterns or text matching
- Satisfies the spec's "within 5 lines" positioning requirement
- Avoids splitting paragraph text since it prefers blank-line boundaries

### Component 4: CLI `--no-equations` flag

**File:** `src/agentic_mbse/cli/extract_cli.py`

Add `--no-equations` argument following the existing `--no-tables` / `--no-img2table` pattern (`extract_cli.py:562-567`):

```python
    "--no-equations",
    action="store_true",
    default=False,
    help="Disable equation region detection",
```

Wire to config (`extract_cli.py:343-344` area):

```python
    enable_equations=not args.no_equations,
```

This gives users explicit opt-out from the ~0.85s/page overhead.

### Component 5: `PipelineProfile` extension

**File:** `src/agentic_mbse/extraction/types.py`

Add one field to `PipelineProfile`:

```python
@dataclass
class PipelineProfile:
    ...
    equation_detection: float = 0.0  # after table_filter_enhance
```

### Table/Equation Overlap (Spec line 76 — SHOULD, deferred)

The spec says the detector SHOULD avoid cropping regions already identified as tables. This cross-check is **deferred** for two reasons:

1. **Coordinate space mismatch**: GMFT operates on PDFium-rendered pages while LayoutPredictor operates on pymupdf-rendered pixmaps. Mapping between these coordinate spaces requires DPI normalization and page dimension alignment — non-trivial plumbing for marginal benefit.
2. **Low real-world risk**: The LayoutPredictor model assigns mutually exclusive labels to regions — a single bounding box is classified as either "Formula" (class 2) or "Table" (class 8), never both. In our corpus testing (hawker_2020 has both tables and equations), zero table regions were misclassified as formulas.

If overlap becomes a real issue in production, the `bbox` field on `DetectedEquation` preserves the coordinates needed to implement IoU-based cross-checking against table regions in a future iteration.

### Known Limitations

1. **`y_fraction` placement is approximate on restructured pages.** The linear mapping from page fraction to markdown line number assumes proportional vertical distribution of text. On pages where tables are replaced/stripped (GMFT_REPLACE, STRIP_*) or Claude produces significantly different text (CLAUDE_REPLACE), the mapping may be off by more than the ideal. The spec's "within 5 lines" tolerance accommodates this, and the blank-line insertion preference prevents mid-paragraph splits. For Claude-replaced pages specifically, the crop is supplementary (Claude already produces better equation text), so imprecise placement is acceptable.

2. **No inline equation detection.** The model at conf ≥ 0.5 empirically returns zero inline math detections (validated on hansen_2025), but this is a property of the confidence threshold, not a guarantee. If a future document triggers inline detections, the `is_display=True` field would be inaccurate. Mitigation: the 0.5 threshold was validated on our corpus and can be raised if needed.

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:---:|:---:|-----------|
| Model not cached on first run → download delay | Low (one-time) | Medium | `snapshot_download` handles this; log a message |
| CPU overhead on large docs (100+ pages) | Medium | Medium | Gated behind `extracted_images_dir`; opt-in via `enable_equations` |
| `y_fraction` placement inaccuracy | Low | Low | 5-line tolerance in spec; blank-line preference improves accuracy |
| LayoutPredictor API changes in future docling-ibm-models | Low | Medium | Lazy import catches ImportError; pinned version in deps |

---

## Integration Strategy

- **Additive only**: No changes to existing modules (`quality_gate.py`, `tables.py`, `postprocess.py`). The equation detector is a new module with a new pipeline step.
- **Complementary to quality gate**: `_assess_equation_fragments()` detects equation *rendering failures* at the text level. Equation region detection provides *visual crops* regardless of rendering quality. Both can fire on the same page.
- **Same collector**: Uses the existing `ImageCollector` with `kind="equation_crop"`. No changes needed to the collector itself.
- **Feature flag**: `PipelineConfig.enable_equations` defaults `True` but is effectively gated by `extracted_images_dir`. Users who don't configure an images directory get zero overhead.

---

## Validation Approach

### Unit tests (`tests/test_equations.py`, new file)

1. **`test_nms_removes_duplicates`**: Two overlapping bboxes → keeps highest confidence
2. **`test_nms_keeps_non_overlapping`**: Two distant bboxes → keeps both
3. **`test_detect_equations_import_error`**: Mock ImportError → returns `{}`
4. **`test_detect_equations_returns_dict`**: Mock predictor → returns correct structure
5. **`test_detected_equation_y_fraction`**: Verify y_fraction computation

### Pipeline integration tests (`tests/test_pipeline.py`, additions)

6. **`test_equation_detection_disabled`**: `enable_equations=False` → no equation detection called
7. **`test_equation_detection_no_images_dir`**: `extracted_images_dir=None` → no equation detection called
8. **`test_equation_detection_error_isolated`**: Detection raises → pipeline completes without equations
9. **`test_equation_crops_registered_with_collector`**: Mock detector → verify `ImageCollector.entries` contains `kind="equation_crop"`
10. **`test_equation_refs_in_merged_markdown`**: Verify `![](images/page_*_eq_*.png)` appears in output

### Corpus integration tests (`tests/test_equations.py`, marked `@pytest.mark.slow`)

11. **`test_hawker_equation_count`**: Run on `hawker_2020.pdf` → >= 17 equations detected (80% of 21)
12. **`test_hansen_zero_equations`**: Run on `hansen_2025.pdf` → 0 equations detected

---

**Next Step:** After approval → `/_my_plan` to break implementation into phases with checkboxes.

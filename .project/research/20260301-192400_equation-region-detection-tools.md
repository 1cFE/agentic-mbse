---
date: 2026-03-01T19:24:00-08:00
researcher: Claude
topic: "Equation region detection tools and approaches for PDF extraction"
tags: [research, extraction, equations, layout-detection]
status: complete
last_updated: 2026-03-01
---

# Research: Equation Region Detection Tools

**Date**: 2026-03-01 19:24 PST
**Researcher**: Claude
**Research Type**: Domain / Integration / Feasibility

## Research Question

What tools and approaches are available for detecting display equation regions on PDF pages, cropping them as images, and integrating them into the existing extraction pipeline? What experiments should we run to evaluate them?

## Summary

- **Docling's layout model (already installed) detects "Formula" as class ID 2 of 17 layout labels.** The `LayoutPredictor` in `docling-ibm-models` is an RT-DETRv2 object detector that returns bounding boxes for formula regions. A companion `CodeFormulaPredictor` can convert crops to LaTeX. Both are installed at `docling-ibm-models==3.11.0`.
- **PyMuPDF font-based heuristics work for TeX-produced PDFs only.** Math fonts (CMMI, CMSY, CMEX, MTSY, MTEX, RMTMI) in text block spans can identify equation blocks with high precision on TeX-produced documents. Fails completely on scanned, Word-exported, or non-TeX PDFs.
- **Several external tools exist but Docling is the strongest candidate** because it's already a dependency, Apache 2.0 licensed, CPU-capable, and covers the broadest document types. Alternatives (DocLayout-YOLO, Surya, Pix2Text MFD) are AGPL/GPL-licensed or require additional large dependencies.
- **Two practical approaches emerge**: (A) Docling layout model as primary detector (vision-based, works on all PDFs), optionally (B) PyMuPDF font heuristics as a fast pre-filter for TeX-produced documents (zero additional dependencies, CPU-only).
- **gmft and img2table have zero equation detection capability** — they are table-only libraries.

## Detailed Findings

### Approach 1: Docling Layout Model (Already Installed)

**Package**: `docling-ibm-models==3.11.0` (installed), `docling==2.71.0` (installed)

**Architecture**: RT-DETRv2 (Real-Time Detection Transformer v2) with ResNet-50 backbone. Model: `docling-project/docling-layout-heron` from HuggingFace, cached at `~/.cache/huggingface/hub/`.

**Layout labels** (17 classes):

| ID | Label | Relevant? |
|----|-------|-----------|
| 0 | Caption | No |
| 1 | Footnote | No |
| **2** | **Formula** | **Yes — primary target** |
| 3 | List-item | No |
| 4 | Page-footer | No |
| 5 | Page-header | No |
| 6 | Picture | No |
| 7 | Section-header | No |
| 8 | Table | No |
| 9 | Text | No |
| 10 | Title | No |
| 11 | Document Index | No |
| 12 | Code | No |
| 13-16 | Checkbox/Form/KV | No |

**Standalone usage** (no full DocumentConverter needed):

```python
from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor
from PIL import Image

predictor = LayoutPredictor(artifact_path="/path/to/model/", device="cpu")
page_image = Image.open("page.png")

for detection in predictor.predict(page_image):
    if detection["label"] == "Formula":
        bbox = (detection["l"], detection["t"], detection["r"], detection["b"])
        confidence = detection["confidence"]
        crop = page_image.crop(bbox)
        crop.save("equation_crop.png")
```

Also supports `predict_batch(images)` for multi-page efficiency.

**Companion: CodeFormulaPredictor** — SAM-ViT-B + OPT VLM that converts cropped formula images to LaTeX strings. Available at `docling_ibm_models.code_formula_model.code_formula_predictor`. Not needed for the current spec (positional placement only), but available for future LaTeX transcription work.

**Performance**:
- GPU (A100): ~28 ms/image
- CPU (AMD EPYC, 4 threads): ~988 ms/image
- Apple MPS (M3 Max): ~62-167 ms/image
- Accuracy: 78% mAP on DocLayNet benchmark (heron-101 model)

**License**: Apache 2.0

**Strengths**:
- Already installed — zero new dependencies
- Vision-based — works on any PDF (TeX, Word, scanned, etc.)
- Returns bounding boxes with confidence scores
- Battle-tested on DocLayNet (IBM's own diverse document dataset)
- `DocItemLabel.FORMULA` in `docling_core` confirms first-class support

**Weaknesses**:
- ~1 second per page on CPU — significant overhead for large documents
- Requires rendering PDF page to image first (pymupdf can do this)
- Model download on first use (~hundreds of MB)
- May detect inline formulas as well as display equations (filtering needed)

**Code references**:
- `docling_ibm_models/layoutmodel/layout_predictor.py` — `LayoutPredictor` class
- `docling_ibm_models/layoutmodel/labels.py` — label definitions (ID 2 = Formula)
- `docling_core/types/doc/labels.py` — `DocItemLabel.FORMULA`

---

### Approach 2: PyMuPDF Font-Based Heuristics

**Package**: `pymupdf==1.26.7` (installed)

**Mechanism**: PyMuPDF's `page.get_text("dict")` returns text blocks with per-span font metadata. Math fonts have distinctive names that can be used to identify equation-containing blocks.

**Math font catalog** (found in corpus):

| Font Family | Examples | Source |
|-------------|----------|--------|
| TeX Computer Modern | `CMMI10`, `CMMI12`, `CMSY10`, `CMEX10`, `CMR10`, `CMTI10`, `CMBX12`, `CMSS12` | TeX/LaTeX |
| MathType | `MTSY`, `MTEX`, `RMTMI` | MathType equation editor |

**Detection signals per block**:

| Signal | Score | Description |
|--------|-------|-------------|
| CM/MT math font present | +3 | Any span uses a known math font family |
| Superscript flag (flags & 1) | +2 | Span has superscript positioning |
| Italic flag (flags & 2) | +1 | Span has italic styling |
| Fraction bar overlap | +3 | `page.get_drawings()` finds a thin horizontal line within the block bbox |

Threshold: score >= 5 → high-confidence equation region.

**Corpus validation results** (score >= 5):

| Document | Equation Regions | Ground Truth | Notes |
|----------|:---:|:---:|-------|
| `hawker_2020` | 22 | 21 display eqs | Close match — some multi-block equations count as 2 |
| `paischer_2025` | 125 | 23 display eqs | Over-counts — each equation fragment is a separate block |
| `hansen_2025` | 62 | 0 display eqs | **False positives** — inline math uses same fonts |
| `energy_amplifier` | 135 | many | Expected — 241-page CERN report |
| `araiinejad_2024` | 0 | ~5 | **Misses** — uses Times/Arial, not CM fonts |
| `schulte_1978` | 0 | ~10 | **Misses** — scanned, no font metadata |

**Known limitations**:
1. **Only works on TeX-produced PDFs.** Documents using Times, Arial, Helvetica, or embedded equation images have no detectable math fonts. Zero recall on non-TeX PDFs.
2. **No spatial merging.** A single displayed equation may span 2-3 text blocks (numerator, fraction bar, denominator are separate). Spatial merging by y-proximity would be needed.
3. **High false positive rate on inline math.** `hansen_2025` has 62 "equation" blocks but zero display equations — all are inline math using the same CM fonts.
4. **Cannot distinguish display vs inline.** Font signals are identical for both.

**Strengths**:
- Zero additional dependencies
- Extremely fast (no model inference, just metadata parsing)
- Provides exact bounding boxes from block coordinates
- High precision *on TeX documents* when combined with fraction bar detection

**Weaknesses**:
- Fails completely on non-TeX PDFs (0% recall)
- Cannot distinguish display vs inline equations
- Requires spatial merging logic for multi-block equations
- High false positive rate without careful filtering

**Code references**:
- `pymupdf` `page.get_text("dict")` — returns blocks with span font metadata
- `pymupdf` `page.get_drawings()` — returns vector graphics (fraction bars are type 's' strokes)

---

### Approach 3: External Tools (Not Installed)

#### DocLayout-YOLO

- **What**: YOLO-based document layout detector with "Isolated Formula" + "Formula Caption" classes
- **Package**: `pip install doclayout-yolo`
- **Performance**: 85.5 FPS on GPU, 79.7% mAP on DocLayNet
- **License**: **AGPL-3.0** (Ultralytics YOLO dependency — commercial use requires enterprise license)
- **Verdict**: Strong detector but AGPL license is problematic. Redundant given Docling is already installed.

#### Surya

- **What**: Multi-purpose OCR toolkit with "Formula" + "Text-inline-math" layout classes
- **Package**: `pip install surya-ocr`
- **Performance**: EfficientViT-based, ~0.13s/image on A10 GPU
- **License**: **Modified AI2 Open Rail-M** (model weights) + **GPL** (code) — restrictive for commercial use
- **Verdict**: Good detector and distinguishes inline math. License is restrictive. Heavy dependency chain.

#### Pix2Text MFD

- **What**: YOLOv7-based Mathematical Formula Detection — detects both inline and block formulas
- **Package**: `pip install pix2text`
- **Performance**: YOLOv7 inference, GPU recommended
- **License**: **MIT** — permissive
- **Verdict**: Good alternative if Docling's accuracy is insufficient. MIT-licensed. Adds YOLOv7 dependency.

#### pix2tex / LaTeX-OCR

- **What**: Recognition-only — takes a pre-cropped equation image and produces LaTeX
- **Detection**: **No.** Does not detect equation regions.
- **Verdict**: Not applicable for our detection task.

#### Nougat (Meta)

- **What**: Full-page academic PDF to Markdown — no bounding boxes
- **Detection**: **No.** Processes entire pages holistically.
- **Verdict**: Not applicable. Also stalled since 2023 and CC-BY-NC model weights.

---

### Tools With No Equation Capability

| Package | Installed | Verdict |
|---------|-----------|---------|
| gmft v0.4.2 | Yes | Tables only — uses Microsoft TATR with 2 labels (table, rotated-table) |
| img2table v1.4.2 | Yes | Tables only — classical CV line detection, no ML layout model |

---

## Recommended Approaches for Evaluation

### Primary: Docling LayoutPredictor (Standalone)

Use Docling's `LayoutPredictor` directly — not the full `DocumentConverter` pipeline — to detect Formula regions on rendered page images. This avoids the overhead of Docling's full document conversion while using the same model.

**Integration pattern** (mirrors `_detect_gmft()` in `tables.py`):

```python
def detect_equations(pdf_path: Path, save_images: bool = True) -> dict[int, list[DetectedEquation]]:
    import pymupdf
    from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor

    doc = pymupdf.open(pdf_path)
    result: dict[int, list[DetectedEquation]] = {}

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        equations = []
        for det in predictor.predict(img):
            if det["label"] == "Formula" and det["confidence"] > threshold:
                bbox = (det["l"], det["t"], det["r"], det["b"])
                crop = img.crop(bbox)
                # Save crop, create DetectedEquation...
                equations.append(...)

        if equations:
            result[page_idx] = equations

    doc.close()
    return result
```

### Secondary: PyMuPDF Font Heuristics (Fast Pre-Filter)

Optional fast path: before running the vision model, check if the page has known math fonts. If no math fonts are found AND no image blocks exist (i.e., no embedded equation images), skip the expensive vision inference for that page. This reduces CPU time on non-equation pages.

**Not a standalone detector** — only useful as a pre-filter to skip pages that definitely have no equations.

---

## Experiments to Run

### Experiment 1: Docling LayoutPredictor Accuracy on Corpus

**Goal**: Measure detection accuracy on our math-heavy corpus documents.

**Method**:
1. Render each page of `hawker_2020.pdf` (14 pages) to 200 DPI images
2. Run `LayoutPredictor.predict()` on each page image
3. Filter for `label == "Formula"`
4. Record: page number, bounding box, confidence score
5. Manually compare against the PDF to count true positives, false positives, false negatives

**Evaluation criteria**:
- Recall: what fraction of display equations are detected?
- Precision: what fraction of detections are actual display equations (not inline math, not tables)?
- Are multi-line equations (aligned, matrices) detected as single or multiple regions?

**Repeat for**: `paischer_2025.pdf` (23 display eqs), `hansen_2025.pdf` (0 display eqs — negative test)

**Expected output**: Precision/recall table per document.

### Experiment 2: Crop Quality Assessment

**Goal**: Verify that bounding boxes produce clean crops without clipping.

**Method**:
1. From Experiment 1, save all cropped equation images
2. Visually inspect 10 random crops from each document
3. Check: full equation captured? Equation label `(N.N)` included? Excess surrounding text?

**Evaluation criteria**:
- Does the crop include the full equation without clipping symbols at boundaries?
- Does it include the equation number when present?
- How much surrounding text/whitespace is included?
- Should we add padding to the bounding box?

### Experiment 3: Confidence Threshold Tuning

**Goal**: Find the optimal confidence threshold that maximizes precision without losing too many true equations.

**Method**:
1. From Experiment 1 data, plot precision/recall at thresholds 0.1, 0.2, 0.3, 0.5, 0.7
2. Identify the threshold that achieves >90% precision with >80% recall

**Expected output**: Threshold recommendation.

### Experiment 4: Performance Profiling (CPU vs GPU)

**Goal**: Measure per-page inference time for the layout model.

**Method**:
1. Run `LayoutPredictor.predict()` on 14 pages of `hawker_2020.pdf` (CPU mode)
2. Measure wall-clock time per page
3. Estimate total overhead for a 30-page document
4. If available, compare GPU timing

**Evaluation criteria**:
- Is CPU inference acceptable (<2s/page)?
- Total pipeline overhead for a typical document?
- Is batched prediction (`predict_batch`) worth the implementation complexity?

### Experiment 5: PyMuPDF Font Heuristics as Pre-Filter

**Goal**: Measure how many pages can be skipped by checking for math fonts first.

**Method**:
1. For each corpus PDF, check which pages have math fonts (CM*/MT* families)
2. Compare against Docling's detected Formula pages
3. Measure: pages with math fonts that have no formulas (false positive filter rate), pages with formulas that have no math fonts (would-be-missed rate)

**Evaluation criteria**:
- What percentage of pages can be safely skipped (no math fonts, no image blocks)?
- Are there any formula-containing pages that would be incorrectly skipped?
- Is the pre-filter worth the implementation complexity vs just running Docling on all pages?

### Experiment 6: Display vs Inline Discrimination

**Goal**: Determine if the Docling model naturally distinguishes display from inline equations, or if post-filtering is needed.

**Method**:
1. Run LayoutPredictor on `hansen_2025.pdf` (heavy inline math, 0 display equations)
2. Record all Formula detections with confidence and bounding box dimensions
3. Check: does the model detect inline math as Formula, or only display equations?
4. If inline math is detected, can we filter by bounding box height (display equations are taller)?

**Evaluation criteria**:
- False positive rate on inline-math-only documents
- Can display equations be distinguished by bbox height > threshold?
- Does confidence score correlate with display vs inline?

### Experiment 7: Integration Smoke Test

**Goal**: End-to-end test of equation crops through the image collector.

**Method**:
1. Run the pipeline on `hawker_2020.pdf` with equation detection enabled
2. Verify: equation crop PNGs appear in `images/` directory
3. Verify: inline `![](images/page_NNN_eq_M.png)` references appear in output markdown
4. Verify: references are positioned near corresponding equation text
5. Verify: `PipelineResult.image_count` includes equation crops

**Evaluation criteria**:
- Do equation crops appear alongside table crops and figures?
- Is the markdown reference positioned within 5 lines of the equation text?
- Does the pipeline still pass all existing tests?

---

## Feasibility Assessment

**High confidence this is feasible.** The primary approach (Docling LayoutPredictor) is:
- Already installed — no new dependencies needed for detection
- Has a dedicated "Formula" class trained on DocLayNet
- Returns bounding boxes directly usable for cropping
- Follows the exact same integration pattern as GMFT table detection

**Risks**:
1. **CPU performance**: ~1s/page adds significant overhead on large documents. Mitigation: font-heuristic pre-filter, batch prediction, or making equation detection opt-in.
2. **Inline vs display discrimination**: The model may detect inline math as Formula. Mitigation: confidence threshold tuning, bbox dimension filtering.
3. **Multi-line equation fragmentation**: Complex equations (aligned, matrices) may be detected as multiple regions. Mitigation: spatial merging by y-proximity (same approach needed for PyMuPDF heuristics).

**No research blockers.** All experiments can be run with currently installed packages.

## Recommendations

1. **Run Experiments 1-3 first** (accuracy and threshold tuning on hawker_2020 and paischer_2025). These determine whether Docling's model is accurate enough before committing to the integration work.
2. **Design should use Docling LayoutPredictor as the primary detector.** It's already installed, Apache 2.0 licensed, and covers all PDF types. PyMuPDF font heuristics should be evaluated as an optional pre-filter for performance, not a standalone approach.
3. **Defer LaTeX transcription** (CodeFormulaPredictor) to a future item. The current spec requires positional placement only.
4. **Gate equation detection behind `extracted_images_dir`** — if the user isn't requesting images, don't run the layout model. This avoids performance overhead by default.

## Open Questions

1. Should equation detection default to enabled (when images dir is set) or require an explicit `--equations` flag?
2. Is ~1s/page CPU overhead acceptable, or do we need the font-heuristic pre-filter to skip non-equation pages?
3. Should the `LayoutPredictor` be initialized once and reused across pages (singleton), or created per-call like GMFT's `AutoTableDetector`?

## Code References

- `docling_ibm_models/layoutmodel/layout_predictor.py` — `LayoutPredictor` class, `predict()` and `predict_batch()` methods
- `docling_ibm_models/layoutmodel/labels.py` — label ID 2 = Formula
- `docling_ibm_models/code_formula_model/code_formula_predictor.py` — future LaTeX conversion
- `docling_core/types/doc/labels.py` — `DocItemLabel.FORMULA = "formula"`
- `src/agentic_mbse/extraction/tables.py:352-407` — `_detect_gmft()` structural template
- `src/agentic_mbse/extraction/tables.py:273-293` — `_save_table_image()` crop pattern
- `src/agentic_mbse/extraction/pipeline.py:320-388` — steps 3/3b (insertion point for equation detection)
- `src/agentic_mbse/extraction/pipeline.py:63-95` — `ImageCollector` (supports `"equation_crop"` kind)
- `src/agentic_mbse/extraction/quality_gate.py:162-200` — `_assess_equation_fragments()` (complementary)
- `tests/corpus/papers.jsonl` — ground truth with `display_equations` counts

"""Equation region detection using Docling LayoutPredictor.

Detects display (block) equations on PDF pages, crops them as images,
and returns DetectedEquation objects for pipeline integration.

The LayoutPredictor dependency (docling-ibm-models) is guarded by lazy
import with try/except ImportError for graceful degradation.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import TypedDict

from agentic_mbse.extraction.types import DetectedEquation

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class LayoutDetection(TypedDict):
    label: str
    confidence: float
    l: float  # noqa: E741
    t: float
    r: float
    b: float


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_layout_predictor = None


def _import_layout_predictor():
    """Import LayoutPredictor class. Raises ImportError if not installed."""
    from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor  # noqa: F401

    return LayoutPredictor


def _get_predictor():
    """Initialize or return cached LayoutPredictor singleton."""
    global _layout_predictor
    if _layout_predictor is not None:
        return _layout_predictor

    from huggingface_hub import snapshot_download

    predictor_cls = _import_layout_predictor()
    artifact_path = snapshot_download("docling-project/docling-layout-heron")
    _layout_predictor = predictor_cls(
        artifact_path=str(artifact_path),
        device="cpu",
        num_threads=4,
        base_threshold=0.3,
    )
    return _layout_predictor


# ---------------------------------------------------------------------------
# Non-maximum suppression
# ---------------------------------------------------------------------------


def _nms(
    detections: list[LayoutDetection],
    iou_threshold: float = 0.3,
) -> list[LayoutDetection]:
    """Non-maximum suppression to remove overlapping bounding boxes.

    Sorts by confidence descending, keeps a detection only if its IoU
    with all already-kept detections is below the threshold.
    """
    if not detections:
        return []

    sorted_dets = sorted(detections, key=lambda d: d["confidence"], reverse=True)
    kept: list[LayoutDetection] = []

    for det in sorted_dets:
        should_keep = True
        for kept_det in kept:
            iou = _compute_iou(det, kept_det)
            if iou > iou_threshold:
                should_keep = False
                break
        if should_keep:
            kept.append(det)

    return kept


def _compute_iou(a: LayoutDetection, b: LayoutDetection) -> float:
    """Compute intersection-over-union between two bounding boxes."""
    x_left = max(a["l"], b["l"])
    y_top = max(a["t"], b["t"])
    x_right = min(a["r"], b["r"])
    y_bottom = min(a["b"], b["b"])

    if x_right <= x_left or y_bottom <= y_top:
        return 0.0

    intersection = (x_right - x_left) * (y_bottom - y_top)
    area_a = (a["r"] - a["l"]) * (a["b"] - a["t"])
    area_b = (b["r"] - b["l"]) * (b["b"] - b["t"])
    union = area_a + area_b - intersection

    if union <= 0:
        return 0.0
    return intersection / union


# ---------------------------------------------------------------------------
# Core detection
# ---------------------------------------------------------------------------


def detect_equations(
    pdf_path: Path,
    confidence_threshold: float = 0.5,
    save_images: bool = True,
) -> dict[int, list[DetectedEquation]]:
    """Detect display equations on all pages of a PDF.

    Returns dict mapping 0-indexed page number to detected equations.
    Returns empty dict if docling-ibm-models is not installed.
    """
    try:
        _import_layout_predictor()
    except ImportError:
        return {}

    import pymupdf

    predictor = _get_predictor()
    image_dir = Path(tempfile.mkdtemp(prefix="eqdet_")) if save_images else None

    doc = pymupdf.open(str(pdf_path))
    result: dict[int, list[DetectedEquation]] = {}

    try:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=200)
            # Convert pymupdf Pixmap to PIL Image
            from PIL import Image

            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img_height = pix.height

            # Run prediction
            raw_dets: list[LayoutDetection] = [
                d for d in predictor.predict(img) if d["label"] == "Formula"
            ]

            if not raw_dets:
                continue

            # NMS then confidence filter
            nms_dets = _nms(raw_dets, iou_threshold=0.3)
            filtered = [d for d in nms_dets if d["confidence"] >= confidence_threshold]

            if not filtered:
                continue

            page_eqs: list[DetectedEquation] = []
            for eq_idx, det in enumerate(filtered):
                left, top, right, bottom = det["l"], det["t"], det["r"], det["b"]
                y_fraction = ((top + bottom) / 2) / img_height

                image_path = None
                if save_images and image_dir is not None:
                    crop = img.crop((int(left), int(top), int(right), int(bottom)))
                    image_path = image_dir / f"page_{page_idx:03d}_eq_{eq_idx}.png"
                    crop.save(str(image_path))

                page_eqs.append(
                    DetectedEquation(
                        confidence=det["confidence"],
                        bbox=(left, top, right, bottom),
                        image_path=image_path,
                        y_fraction=y_fraction,
                        is_display=True,
                    )
                )

            if page_eqs:
                result[page_idx] = page_eqs

    finally:
        doc.close()

    return result

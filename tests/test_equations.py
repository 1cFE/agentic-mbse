"""Tests for agentic_mbse.extraction.equations — equation region detection.

Unit tests mock the LayoutPredictor dependency. Corpus tests (marked slow)
run the real detector against test PDFs.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_mbse.extraction.types import DetectedEquation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MOD = "agentic_mbse.extraction.equations"

CORPUS = Path(__file__).parent / "corpus"


def _det(
    label: str = "Formula",
    confidence: float = 0.9,
    left: float = 100,
    top: float = 100,
    right: float = 500,
    bottom: float = 200,
) -> dict:
    return {"label": label, "confidence": confidence, "l": left, "t": top, "r": right, "b": bottom}


# ---------------------------------------------------------------------------
# TestDetectedEquation
# ---------------------------------------------------------------------------


class TestDetectedEquation:
    def test_dataclass_fields(self):
        eq = DetectedEquation(confidence=0.95)
        assert eq.confidence == 0.95
        assert eq.bbox is None
        assert eq.image_path is None
        assert eq.y_fraction == 0.0
        assert eq.is_display is True

    def test_y_fraction_stored(self):
        eq = DetectedEquation(confidence=0.8, y_fraction=0.42)
        assert eq.y_fraction == 0.42


# ---------------------------------------------------------------------------
# TestNms
# ---------------------------------------------------------------------------


class TestNms:
    def _nms(self, *args, **kwargs):
        from agentic_mbse.extraction.equations import _nms

        return _nms(*args, **kwargs)

    def test_removes_overlapping_lower_confidence(self):
        dets = [
            _det(confidence=0.9, left=100, top=100, right=500, bottom=200),
            _det(confidence=0.8, left=105, top=105, right=505, bottom=205),
        ]
        kept = self._nms(dets, iou_threshold=0.3)
        assert len(kept) == 1
        assert kept[0]["confidence"] == 0.9

    def test_keeps_non_overlapping(self):
        dets = [
            _det(confidence=0.9, left=100, top=100, right=500, bottom=200),
            _det(confidence=0.8, left=100, top=800, right=500, bottom=900),
        ]
        kept = self._nms(dets, iou_threshold=0.3)
        assert len(kept) == 2

    def test_empty_input(self):
        kept = self._nms([], iou_threshold=0.3)
        assert kept == []


# ---------------------------------------------------------------------------
# TestDetectEquations (mocked predictor)
# ---------------------------------------------------------------------------


class TestDetectEquations:
    def test_import_error_returns_empty(self):
        """When docling_ibm_models is not installed, returns empty dict."""
        with patch(f"{_MOD}._import_layout_predictor", side_effect=ImportError):
            from agentic_mbse.extraction.equations import detect_equations

            result = detect_equations(Path("/fake/doc.pdf"))
            assert result == {}

    def test_returns_detected_equations(self, tmp_path):
        """Mock predictor returns synthetic detections → correct structure."""
        pdf_path = tmp_path / "test.pdf"

        # Create a minimal 1-page PDF with pymupdf
        import pymupdf

        doc = pymupdf.open()
        page = doc.new_page(width=612, height=792)
        page.insert_text((100, 400), "y = mx + b")
        doc.save(str(pdf_path))
        doc.close()

        mock_predictor = MagicMock()
        mock_predictor.predict.return_value = iter(
            [
                {"label": "Formula", "confidence": 0.95, "l": 50, "t": 180, "r": 400, "b": 230},
                {"label": "Text", "confidence": 0.99, "l": 50, "t": 50, "r": 400, "b": 100},
            ]
        )

        with (
            patch(f"{_MOD}._import_layout_predictor"),
            patch(f"{_MOD}._get_predictor", return_value=mock_predictor),
        ):
            from agentic_mbse.extraction.equations import detect_equations

            result = detect_equations(pdf_path, save_images=True)

        assert isinstance(result, dict)
        assert 0 in result
        eqs = result[0]
        assert len(eqs) == 1
        assert isinstance(eqs[0], DetectedEquation)
        assert eqs[0].confidence == 0.95
        assert eqs[0].is_display is True
        assert eqs[0].y_fraction > 0
        assert eqs[0].image_path is not None
        assert eqs[0].image_path.exists()


# ---------------------------------------------------------------------------
# TestCorpusEquations (real detector, slow)
# ---------------------------------------------------------------------------


@pytest.mark.slow
class TestCorpusEquations:
    def test_hawker_recall(self):
        """hawker_2020: >= 20 of 21 display equations detected (95% recall)."""
        from agentic_mbse.extraction.equations import detect_equations

        result = detect_equations(CORPUS / "pdfs/hawker_2020.pdf")
        total = sum(len(eqs) for eqs in result.values())
        assert total >= 20, f"Expected >= 20 equations, got {total}"

    def test_hansen_zero_false_positives(self):
        """hansen_2025: 0 display equations (inline math only)."""
        from agentic_mbse.extraction.equations import detect_equations

        result = detect_equations(CORPUS / "pdfs/hansen_2025.pdf")
        total = sum(len(eqs) for eqs in result.values())
        assert total == 0, f"Expected 0 equations, got {total}"

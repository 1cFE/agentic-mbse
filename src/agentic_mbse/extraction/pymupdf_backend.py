"""PyMuPDF4LLM extraction backend (PDF only).

Fast, reliable fallback. Requires the ``pymupdf4llm`` package
(installed via the ``extract`` optional dependency).

Configuration rationale documented in:
  .project/active/pymupdf4llm-deep-dive/findings.md
"""

from __future__ import annotations

import re
from pathlib import Path

from agentic_mbse.extraction.base import ExtractionResult
from agentic_mbse.extraction.postprocess import postprocess
from agentic_mbse.extraction.types import PageResult


def _get_to_markdown():
    """Lazy-import ``pymupdf4llm.to_markdown`` and return it."""
    import pymupdf4llm  # type: ignore[import-untyped]

    return pymupdf4llm.to_markdown


# ---------------------------------------------------------------------------
# Header detection
# ---------------------------------------------------------------------------
# pymupdf4llm's built-in IdentifyHeaders uses font-size only, which works for
# documents with clear size hierarchy (e.g., araiinejad_2024, hawker_2020) but
# fails on documents where headers are distinguished by bold/caps only (e.g.,
# hansen_2025, delene_2001, helios_design).
#
# The composite detector below combines BOTH approaches:
#   1. Bold pattern matching: catches bold + numbered/all-caps headers
#   2. IdentifyHeaders fallback: catches font-size-differentiated headers
#
# Tested on 14-document corpus (9 configurations). See findings.md Exp 6.
# Result: zero regressions vs baseline, improvements on 10 of 13 documents.
# ---------------------------------------------------------------------------


def _bold_header_detector(span, page=None):
    """Bold-based header detector for academic papers.

    Detects:
    - Arabic numbered sections: "1 Introduction", "2.1 Methods"
    - All-caps short titles: "ABSTRACT", "REFERENCES", "INTRODUCTION"
    """
    text = span["text"].strip()
    if not text:
        return ""
    is_bold = bool(span["flags"] & 16)  # bit 4 = bold
    if not is_bold:
        return ""

    # Numbered sections: "1 Introduction", "2.1 Background", "A.1 Appendix"
    m = re.match(r"^\d+(?:\.\d+)*\.?\s+[A-Z]", text)
    if m:
        sec_num = text.split()[0].rstrip(".")
        depth = sec_num.count(".") + 1
        return "#" * min(depth + 1, 6) + " "

    # All-caps short titles (e.g., "ABSTRACT", "REFERENCES")
    if text.isupper() and len(text) < 60 and len(text.split()) <= 6:
        return "## "

    return ""


class CompositeHeaderDetector:
    """Combines IdentifyHeaders (font-size) with bold pattern matching.

    Re-initializes per document. For each span, returns the first match from:
    1. Bold pattern detector (numbered sections, all-caps titles)
    2. IdentifyHeaders font-size fallback

    When both fire, uses the deeper (more specific) heading level.
    """

    def __init__(self):
        self._identify_headers = None
        self._current_doc_name = None

    def _ensure_initialized(self, page):
        """Re-initialize IdentifyHeaders when processing a new document."""
        if page is None:
            return
        doc = page.parent
        doc_name = doc.name if doc else None
        if doc_name != self._current_doc_name:
            self._current_doc_name = doc_name
            try:
                from pymupdf4llm.helpers.pymupdf_rag import IdentifyHeaders

                self._identify_headers = IdentifyHeaders(doc)
            except Exception:
                self._identify_headers = None

    def get_header_id(self, span, page=None):
        self._ensure_initialized(page)

        bold_result = _bold_header_detector(span, page)
        font_result = ""
        if self._identify_headers is not None:
            try:
                font_result = self._identify_headers.get_header_id(span, page)
            except Exception:
                font_result = ""

        if bold_result and font_result:
            return bold_result if len(bold_result) > len(font_result) else font_result
        return bold_result or font_result

    def __call__(self, span, page=None):
        return self.get_header_id(span, page)


# Singleton instance reused across calls; re-initializes per document.
_composite_header_detector = CompositeHeaderDetector()


def extract_pages(
    pdf_path: Path,
    extracted_images_dir: Path | None = None,
) -> list[PageResult]:
    """Extract per-page markdown using pymupdf4llm with BEST_V1 config.

    Uses ``page_chunks=True`` for per-page output with full-document header
    calibration (IdentifyHeaders scans all pages for font statistics).

    Does NOT call ``postprocess()`` — the pipeline applies enhancements
    on the raw per-page output (see design.md §2.4 for rationale).

    Adds ``force_text=True`` (matching Stage 3 BEST_V1_PARAMS) to include
    text from form fields and annotations.  The legacy ``extract()``
    function is preserved as-is for backward compatibility.

    When *extracted_images_dir* is provided, embedded figures are saved
    to that directory and referenced in the per-page markdown.

    Returns list of PageResult, 0-indexed page numbers.
    """
    to_markdown = _get_to_markdown()

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

    results = []
    for chunk in chunks:
        page_num = chunk["metadata"]["page"] - 1  # Convert 1-indexed to 0-indexed
        results.append(PageResult(page_num=page_num, markdown=chunk["text"]))

    return results


def extract(input_path: Path, output_dir: Path) -> ExtractionResult:
    """Extract a PDF using PyMuPDF4LLM.

    Creates *output_dir*/``full_document.md`` and *output_dir*/``images/``.
    """
    try:
        to_markdown = _get_to_markdown()

        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        chunks = to_markdown(
            str(input_path),
            write_images=True,
            image_path=str(images_dir),
            image_format="png",
            dpi=150,
            page_chunks=True,
            # Composite: font-size (IdentifyHeaders) + bold pattern matching.
            # See findings.md Experiment 6 for evidence.
            hdr_info=_composite_header_detector,
            # "lines" is the right balance — "lines_strict" eliminates real tables
            # in documents like aries_cost_account. See findings.md Experiment 1.
            table_strategy="lines",
            # Eliminates code fence spam in patent/monospace documents.
            # See findings.md Experiment 3 (tajima: 610 fences → 0).
            ignore_code=True,
        )

        # Join page chunks with page markers for downstream page resolution
        page_texts = []
        for chunk in chunks:
            page_num = chunk.get("metadata", {}).get("page", None)
            if page_num is not None:
                page_texts.append(f"<!-- PAGE:{page_num} -->")
            page_texts.append(chunk["text"])
        md_text: str = "\n".join(page_texts)

        # Apply deterministic post-processing
        md_text = postprocess(md_text, images_dir=images_dir)

        md_path = output_dir / "full_document.md"
        md_path.write_text(md_text)

        image_count = sum(1 for f in images_dir.iterdir() if f.is_file())

        return ExtractionResult(
            success=True,
            output_dir=output_dir,
            markdown_path=md_path,
            image_count=image_count,
            char_count=len(md_text),
            backend_used="pymupdf",
        )
    except Exception as exc:
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error=str(exc),
            backend_used="pymupdf",
        )

"""PyMuPDF4LLM extraction backend (PDF only).

Fast, reliable fallback. Requires the ``pymupdf4llm`` package
(installed via the ``extract`` optional dependency).
"""

from __future__ import annotations

import re
from pathlib import Path

from agentic_mbse.extraction.base import ExtractionResult
from agentic_mbse.extraction.postprocess import postprocess


def _get_to_markdown():
    """Lazy-import ``pymupdf4llm.to_markdown`` and return it."""
    import pymupdf4llm  # type: ignore[import-untyped]

    return pymupdf4llm.to_markdown


def _academic_header_detector(span, page=None):
    """Custom header detector for academic papers.

    Uses bold flag + section numbering regex instead of font-size heuristics.
    Passed as the ``hdr_info`` callback to ``pymupdf4llm.to_markdown()``.
    """
    text = span["text"].strip()
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
            # Use default header detector (font-size based) instead of custom bold-only detector
            # This provides better coverage for papers with non-bold headers
            # hdr_info=_academic_header_detector,
            table_strategy="lines",
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

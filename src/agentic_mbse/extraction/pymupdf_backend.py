"""PyMuPDF4LLM extraction backend (PDF only).

Fast, reliable fallback. Requires the ``pymupdf4llm`` package
(installed via the ``extract`` optional dependency).
"""

from __future__ import annotations

from pathlib import Path

from agentic_mbse.extraction.base import ExtractionResult


def _get_to_markdown():
    """Lazy-import ``pymupdf4llm.to_markdown`` and return it."""
    import pymupdf4llm  # type: ignore[import-untyped]

    return pymupdf4llm.to_markdown


def extract(input_path: Path, output_dir: Path) -> ExtractionResult:
    """Extract a PDF using PyMuPDF4LLM.

    Creates *output_dir*/``full_document.md`` and *output_dir*/``images/``.
    """
    try:
        to_markdown = _get_to_markdown()

        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        md_text: str = to_markdown(
            str(input_path),
            write_images=True,
            image_path=str(images_dir),
            image_format="png",
            dpi=150,
            page_chunks=False,
        )

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

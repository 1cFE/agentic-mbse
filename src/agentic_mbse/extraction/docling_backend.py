"""Docling extraction backend (PDF and DOCX).

ML-based extraction with table structure detection and image extraction.
Requires the ``docling`` package (installed via the ``extract-full``
optional dependency).  Runs in a subprocess with a configurable timeout
to handle memory exhaustion on large documents.
"""

from __future__ import annotations

import re
from pathlib import Path

from agentic_mbse.extraction.base import (
    ExtractionResult,
    ProcessCrashedError,
    _Timeout,
    run_with_timeout,
)


def _docling_extract_inner(input_path: Path, output_dir: Path) -> ExtractionResult:
    """Perform Docling extraction (runs inside a child process)."""
    # Lazy import — docling is heavy and only needed here
    from docling.datamodel.base_models import InputFormat  # type: ignore[import-untyped]
    from docling.datamodel.pipeline_options import (  # type: ignore[import-untyped]
        PdfPipelineOptions,
    )
    from docling.document_converter import (  # type: ignore[import-untyped]
        DocumentConverter,
        PdfFormatOption,
    )

    pipeline_opts = PdfPipelineOptions(
        do_table_structure=True,
        generate_picture_images=True,
        do_ocr=False,
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts),
        }
    )

    conv_result = converter.convert(str(input_path))

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    # Export full markdown
    md_text: str = conv_result.document.export_to_markdown()

    # Save images from the document
    image_count = 0
    for idx, picture in enumerate(conv_result.document.pictures, start=1):
        if hasattr(picture, "image") and picture.image is not None:
            img_path = images_dir / f"figure_{idx:03d}.png"
            picture.image.save(str(img_path))
            image_count += 1

    # Rewrite image references in markdown to point to images/ relative path
    # Docling may produce various image reference styles; normalise them
    md_text = _rewrite_image_paths(md_text, images_dir)

    md_path = output_dir / "full_document.md"
    md_path.write_text(md_text)

    return ExtractionResult(
        success=True,
        output_dir=output_dir,
        markdown_path=md_path,
        image_count=image_count,
        char_count=len(md_text),
        backend_used="docling",
    )


def _rewrite_image_paths(md_text: str, images_dir: Path) -> str:
    """Ensure markdown image references use ``images/`` relative paths."""
    # Replace absolute paths to images_dir with relative
    abs_pattern = re.escape(str(images_dir))
    md_text = re.sub(abs_pattern, "images", md_text)
    return md_text


def extract(
    input_path: Path,
    output_dir: Path,
    timeout: int = 600,
) -> ExtractionResult:
    """Extract a document using Docling with timeout protection.

    Supports both PDF and DOCX.  Runs the actual extraction in a child
    process via :func:`run_with_timeout` so that memory exhaustion or
    hangs are handled cleanly.
    """
    try:
        result = run_with_timeout(
            _docling_extract_inner,
            args=(input_path, output_dir),
            timeout=timeout,
        )
    except ProcessCrashedError as exc:
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error=f"Docling process crashed (exit code: {exc.exit_code})",
            backend_used="docling",
        )
    except Exception as exc:
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error=f"Docling extraction error: {exc}",
            backend_used="docling",
        )

    if isinstance(result, _Timeout):
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error=f"Docling extraction timed out after {timeout}s",
            backend_used="docling",
        )

    if isinstance(result, Exception):
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error=f"Docling extraction failed: {result}",
            backend_used="docling",
        )

    return result

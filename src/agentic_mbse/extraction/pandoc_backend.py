"""Pandoc extraction backend (DOCX only).

Proven best-in-class for DOCX → markdown conversion.  Requires the
``pandoc`` system binary.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from agentic_mbse.extraction.base import ExtractionResult


def _pandoc_available() -> bool:
    """Return ``True`` if the ``pandoc`` binary is on ``$PATH``."""
    return shutil.which("pandoc") is not None


def _rewrite_image_paths(md_text: str, media_dir: Path, images_dir: Path) -> str:
    """Rewrite pandoc's ``--extract-media`` paths to ``images/`` relative.

    Pandoc writes media to the directory given via ``--extract-media`` and
    embeds absolute or relative references.  We normalise them so the
    markdown always uses ``images/<filename>`` references.

    Only rewrites paths inside markdown image/link syntax ``(...)`` to
    avoid false positives in prose text.
    """
    abs_escaped = re.escape(str(media_dir))
    name_escaped = re.escape(media_dir.name)

    # Match media paths only within markdown link parentheses: ](path)
    for pattern in (abs_escaped, name_escaped):
        md_text = re.sub(
            r"(\]\()" + pattern + r"(/)",
            r"\1images\2",
            md_text,
        )
    return md_text


def extract(input_path: Path, output_dir: Path, timeout: int = 120) -> ExtractionResult:
    """Extract a DOCX file using Pandoc.

    Creates *output_dir*/``full_document.md`` and *output_dir*/``images/``.
    """
    if not _pandoc_available():
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error="Pandoc is not installed. Install it: https://pandoc.org/installing.html",
            backend_used="pandoc",
        )

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        md_path = output_dir / "full_document.md"
        media_dir = output_dir / "media"

        proc = subprocess.run(
            [
                "pandoc",
                str(input_path),
                "--from=docx",
                "--to=markdown",
                f"--extract-media={media_dir}",
                "-o",
                str(md_path),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if proc.returncode != 0:
            return ExtractionResult(
                success=False,
                output_dir=output_dir,
                error=f"Pandoc failed (exit {proc.returncode}): {proc.stderr.strip()}",
                backend_used="pandoc",
            )

        # Move extracted media into images/ and rewrite references
        image_count = 0
        seen_names: dict[str, int] = {}
        if media_dir.exists():
            for img_file in sorted(media_dir.rglob("*")):
                if img_file.is_file():
                    name = img_file.name
                    # Deduplicate filenames from different subdirectories
                    if name in seen_names:
                        seen_names[name] += 1
                        stem = img_file.stem
                        suffix = img_file.suffix
                        name = f"{stem}_{seen_names[name]}{suffix}"
                    else:
                        seen_names[name] = 0
                    dest = images_dir / name
                    shutil.move(str(img_file), str(dest))
                    image_count += 1
            # Clean up now-empty media dir
            shutil.rmtree(media_dir, ignore_errors=True)

        # Rewrite image paths in markdown
        md_text = md_path.read_text()
        md_text = _rewrite_image_paths(md_text, media_dir, images_dir)
        md_path.write_text(md_text)

        return ExtractionResult(
            success=True,
            output_dir=output_dir,
            markdown_path=md_path,
            image_count=image_count,
            char_count=len(md_text),
            backend_used="pandoc",
        )
    except subprocess.TimeoutExpired:
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error=f"Pandoc timed out after {timeout}s",
            backend_used="pandoc",
        )
    except Exception as exc:
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error=f"Pandoc extraction error: {exc}",
            backend_used="pandoc",
        )

"""Generated PDFs for arXiv identity tests.

The margin stamp is drawn the way arXiv places it: one line rotated 90° in the
left margin of page 1 (see `.project/active/arxiv-extraction/spike-margin-stamp.md`).
Prose citations are drawn horizontally in the body.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf  # type: ignore[import-untyped]

STAMP = "arXiv:2610.14224v1  [cs.AI]  9 Oct 2026"
OTHER_STAMP = "arXiv:1706.03762v7  [cs.CL]  2 Aug 2023"
CITATION = "Prior work: arXiv:2610.14224"


def make_pdf(
    path: Path,
    *,
    stamps: tuple[str, ...] = (),
    prose: str = "The document's own text about magnets.",
) -> Path:
    """Write a one-page PDF with *stamps* in the left margin and *prose* in the body."""
    doc = pymupdf.open()
    page = doc.new_page()
    for i, stamp in enumerate(stamps):
        page.insert_text((30 + 10 * i, 500), stamp, rotate=90)
    page.insert_text((72, 90), prose)
    doc.save(path)
    doc.close()
    return path

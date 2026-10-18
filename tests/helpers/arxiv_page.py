"""The trimmed real arXiv page fixture and its nine figures.

Shared by the arxiv_html, web-route and PDF-route tests so the figure
acceptance check (every figure saved, referenced relatively, counted) is one
definition.
"""

from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

from agentic_mbse.extraction.arxiv_html import _MD_IMAGE_RE

ARXIV_PAGE = Path(__file__).parent.parent / "fixtures" / "arxiv_2610.14224v1_page.html"
FIGURE_BASE = "https://arxiv.org/html/2610.14224v1/"

# The nine figures of 2610.14224 in page order; Figures 5, 6, 7 and 9 are SVG <object>s.
FIGURES = [
    "2610.14224v1/intro_teaser.png",
    "2610.14224v1/components.png",
    "2610.14224v1/harness2_main_new.png",
    "2610.14224v1/scaling.png",
    "2610.14224v1/scaling_curves.svg",
    "2610.14224v1/total_cost.svg",
    "2610.14224v1/library_transfer.svg",
    "2610.14224v1/figures/same_model.png",
    "2610.14224v1/case_jobbench.svg",
]


def serve_figure(url: str) -> bytes:
    """Image fetcher stub: arXiv serves every figure of the paper, nothing else."""
    if not url.startswith(FIGURE_BASE):
        raise OSError(f"HTTP Error 404: {url}")
    return f"bytes of {url}".encode()


# The fixture's one synthetic in-article data: image (a 1x1 PNG), saved by content hash (D18).
SYNTHETIC_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)
_HASH_NAME_RE = re.compile(r"^[0-9a-f]{16}\.\w+$")


def assert_all_images_saved(markdown: str, images_dir: Path, saved_count: int) -> None:
    """Every image in the paper is a relative ref to a file that exists; none stays inline.

    The nine figures keep their names, in page order. In-article ``data:``
    images (LaTeXML pictures, the synthetic PNG) are saved under content-hash
    names. The saved count equals the files written.
    """
    assert "data:image" not in markdown, "an inline data: image is left in the output"
    refs = [m.group(2) for m in _MD_IMAGE_RE.finditer(markdown)]
    assert refs and all(r.startswith("images/") for r in refs), refs
    for ref in refs:
        assert (images_dir.parent / ref).is_file(), f"{ref} does not exist"

    figure_refs = [r for r in refs if not _HASH_NAME_RE.match(Path(r).name)]
    assert figure_refs == [f"images/{Path(f).name}" for f in FIGURES]
    for figure, ref in zip(FIGURES, figure_refs, strict=True):
        assert (images_dir.parent / ref).read_bytes() == serve_figure(
            f"https://arxiv.org/html/{figure}"
        )
    synthetic = f"{hashlib.sha256(SYNTHETIC_PNG).hexdigest()[:16]}.png"
    assert (images_dir / synthetic).read_bytes() == SYNTHETIC_PNG

    files = {p.name for p in images_dir.iterdir()}
    assert files == {Path(r).name for r in refs}
    assert len(files) > len(FIGURES)  # inline pictures were externalized too
    assert saved_count == len(files)

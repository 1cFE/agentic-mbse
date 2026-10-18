"""The trimmed real arXiv page fixture and its nine figures.

Shared by the arxiv_html, web-route and PDF-route tests so the figure
acceptance check (every figure saved, referenced relatively, counted) is one
definition.
"""

from __future__ import annotations

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


def assert_all_figures_saved(markdown: str, images_dir: Path, saved_count: int) -> None:
    """All nine figures are relative refs to files that exist, and the count matches the files."""
    refs = [m.group(2) for m in _MD_IMAGE_RE.finditer(markdown)]
    figure_refs = [r for r in refs if not r.startswith("data:")]
    assert figure_refs == [f"images/{Path(f).name}" for f in FIGURES]
    for figure, ref in zip(FIGURES, figure_refs, strict=True):
        saved = images_dir.parent / ref
        assert saved.is_file(), f"{ref} does not exist"
        assert saved.read_bytes() == serve_figure(f"https://arxiv.org/html/{figure}")
    files = sorted(p.name for p in images_dir.iterdir())
    assert files == sorted(Path(f).name for f in FIGURES)
    assert saved_count == len(files) == 9

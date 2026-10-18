"""Tests for identify_arxiv_paper: trusted own-ID evidence from real PDF bytes."""

from __future__ import annotations

import pymupdf  # type: ignore[import-untyped]
import pytest

from agentic_mbse.extraction.pandoc_convert import (
    ArxivIdentity,
    detect_arxiv_id,
    identify_arxiv_paper,
)
from tests.helpers.arxiv_pdfs import CITATION, OTHER_STAMP, STAMP, make_pdf


def test_generated_stamp_line_is_vertical_left_margin(tmp_path):
    """Pins the pymupdf behavior the stamp rule relies on (design B2)."""
    pdf = make_pdf(tmp_path / "s.pdf", stamps=(STAMP,))
    doc = pymupdf.open(pdf)
    page = doc[0]
    lines = [
        line
        for block in page.get_text("dict")["blocks"]
        for line in block.get("lines", [])
        if "arXiv:" in "".join(span["text"] for span in line["spans"])
    ]
    width = page.rect.width
    doc.close()

    [line] = lines
    assert line["dir"] == pytest.approx((0, -1), abs=0.05)
    assert line["bbox"][2] <= 0.15 * width


def test_citation_only_is_not_identity(tmp_path):
    pdf = make_pdf(tmp_path / "c.pdf", prose=CITATION)
    assert identify_arxiv_paper(pdf) == ArxivIdentity(None, ())


def test_plain_pdf_is_not_identity(tmp_path):
    assert identify_arxiv_paper(make_pdf(tmp_path / "p.pdf")) == ArxivIdentity(None, ())


def test_stamp_identifies(tmp_path):
    pdf = make_pdf(tmp_path / "s.pdf", stamps=(STAMP,))
    assert identify_arxiv_paper(pdf) == ArxivIdentity("2610.14224v1", ("stamp",))


def test_stamp_wins_over_cited_prose_id(tmp_path):
    """An arXiv-origin PDF citing another paper substitutes only its own ID."""
    pdf = make_pdf(tmp_path / "s.pdf", stamps=(STAMP,), prose="See arXiv:1706.03762v7 [cs.CL]")
    assert identify_arxiv_paper(pdf).arxiv_id == "2610.14224v1"


def test_full_stamp_text_in_prose_is_not_identity(tmp_path):
    """Even the complete stamp text does not count when it is horizontal body text."""
    pdf = make_pdf(tmp_path / "c.pdf", prose=STAMP)
    assert identify_arxiv_paper(pdf) == ArxivIdentity(None, ())


def test_two_stamps_conflict(tmp_path):
    pdf = make_pdf(tmp_path / "s.pdf", stamps=(STAMP, OTHER_STAMP))
    identity = identify_arxiv_paper(pdf)
    assert identity.arxiv_id is None
    assert identity.conflict is not None
    assert "2610.14224v1" in identity.conflict and "1706.03762v7" in identity.conflict


def test_stamp_vs_source_url_conflict(tmp_path):
    pdf = make_pdf(tmp_path / "s.pdf", stamps=(STAMP,))
    identity = identify_arxiv_paper(pdf, "https://arxiv.org/pdf/1706.03762v7")
    assert identity.arxiv_id is None
    assert identity.evidence == ("stamp", "url")
    assert identity.conflict is not None
    assert "2610.14224" in identity.conflict and "1706.03762" in identity.conflict


def test_same_id_different_version_is_not_conflict(tmp_path):
    pdf = make_pdf(tmp_path / "s.pdf", stamps=(STAMP,))
    identity = identify_arxiv_paper(pdf, "https://arxiv.org/abs/2610.14224v3")
    assert identity == ArxivIdentity("2610.14224v1", ("stamp", "url"))


@pytest.mark.parametrize(
    ("url", "arxiv_id"),
    [
        ("https://arxiv.org/pdf/2610.14224v1", "2610.14224v1"),
        ("https://arxiv.org/pdf/2610.14224", "2610.14224"),
        ("https://arxiv.org/pdf/2610.14224v2.pdf", "2610.14224v2"),
        ("https://arxiv.org/abs/2610.14224", "2610.14224"),
        ("http://export.arxiv.org/pdf/2610.14224v1", "2610.14224v1"),
    ],
)
def test_source_url_alone_identifies(tmp_path, url, arxiv_id):
    pdf = make_pdf(tmp_path / "u.pdf", prose=CITATION)
    assert identify_arxiv_paper(pdf, url) == ArxivIdentity(arxiv_id, ("url",))


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/pdf/2610.14224v1",
        "https://arxiv.org/html/2610.14224v1",
        "https://notarxiv.org/pdf/2610.14224",
        "https://example.com/papers/arxiv.org/pdf/2610.14224",
    ],
)
def test_other_source_urls_are_not_evidence(tmp_path, url):
    pdf = make_pdf(tmp_path / "u.pdf", prose=CITATION)
    assert identify_arxiv_paper(pdf, url) == ArxivIdentity(None, ())


def test_empty_pdf_is_not_identity(tmp_path):
    doc = pymupdf.open()
    doc.new_page()
    pdf = tmp_path / "blank.pdf"
    doc.save(pdf)
    doc.close()
    assert identify_arxiv_paper(pdf) == ArxivIdentity(None, ())


def test_detect_arxiv_id_wraps_the_identity_rule(tmp_path):
    assert detect_arxiv_id(make_pdf(tmp_path / "c.pdf", prose=CITATION)) is None
    assert detect_arxiv_id(make_pdf(tmp_path / "s.pdf", stamps=(STAMP,))) == "2610.14224v1"

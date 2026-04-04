"""Tests for arXiv HTML image downloading."""

from __future__ import annotations

import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentic_mbse.extraction.web_backend import _download_arxiv_images


def _fake_urlopen(data: bytes, *, status: int = 200):
    """Create a mock urlopen context manager returning *data*."""
    resp = MagicMock()
    resp.read = lambda n=-1: data if n == -1 else data[:n]
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestDownloadArxivImages:
    """Unit tests for _download_arxiv_images()."""

    def test_downloads_and_rewrites_image_refs(self, tmp_path: Path):
        """Two image refs → both downloaded, paths rewritten to images/."""
        md = (
            "![Fig 1](/html/2411.06644v1/figures/fig1.png)\n"
            "![Fig 2](/html/2411.06644v1/figures/fig2.png)"
        )
        fake_png = b"\x89PNG fake image data"

        with patch("agentic_mbse.extraction.web_backend.urllib.request.urlopen") as mock_open:
            mock_open.return_value = _fake_urlopen(fake_png)
            result_md, count = _download_arxiv_images(
                md, "https://arxiv.org/html/2411.06644v1", tmp_path
            )

        assert count == 2
        assert (tmp_path / "images" / "fig1.png").exists()
        assert (tmp_path / "images" / "fig2.png").exists()
        assert (tmp_path / "images" / "fig1.png").read_bytes() == fake_png
        assert "![Fig 1](images/fig1.png)" in result_md
        assert "![Fig 2](images/fig2.png)" in result_md
        # No remote refs remain
        assert "/html/" not in result_md

    def test_preserves_pandoc_attribute_block(self, tmp_path: Path):
        """Pandoc {#id .class} attribute blocks are preserved after rewrite."""
        md = "![cap](/html/2411.06644v1/figures/fig.png){#S3.F3.g1 .ltx_graphics}"
        fake_png = b"\x89PNG"

        with patch("agentic_mbse.extraction.web_backend.urllib.request.urlopen") as mock_open:
            mock_open.return_value = _fake_urlopen(fake_png)
            result_md, count = _download_arxiv_images(
                md, "https://arxiv.org/html/2411.06644v1", tmp_path
            )

        assert count == 1
        assert "![cap](images/fig.png){#S3.F3.g1 .ltx_graphics}" in result_md

    def test_download_failure_warns_and_preserves_ref(self, tmp_path: Path):
        """404 on one image → other still downloads, broken ref unchanged."""
        md = (
            "![Good](/html/2411.06644v1/figures/good.png)\n"
            "![Bad](/html/2411.06644v1/figures/bad.png)"
        )
        fake_png = b"\x89PNG"

        call_count = 0

        def side_effect(req, **kwargs):
            nonlocal call_count
            call_count += 1
            url = req.full_url if hasattr(req, "full_url") else str(req)
            if "bad.png" in url:
                raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
            return _fake_urlopen(fake_png)

        with patch("agentic_mbse.extraction.web_backend.urllib.request.urlopen", side_effect=side_effect):
            result_md, count = _download_arxiv_images(
                md, "https://arxiv.org/html/2411.06644v1", tmp_path
            )

        assert count == 1
        assert "![Good](images/good.png)" in result_md
        # Bad ref left unchanged
        assert "![Bad](/html/2411.06644v1/figures/bad.png)" in result_md

    def test_data_uri_skipped(self, tmp_path: Path):
        """data: URI left unchanged, not downloaded."""
        md = "![inline](data:image/png;base64,iVBORw0KGgo=)\n![Real](/html/2411.06644v1/figures/real.png)"
        fake_png = b"\x89PNG"

        with patch("agentic_mbse.extraction.web_backend.urllib.request.urlopen") as mock_open:
            mock_open.return_value = _fake_urlopen(fake_png)
            result_md, count = _download_arxiv_images(
                md, "https://arxiv.org/html/2411.06644v1", tmp_path
            )

        assert count == 1
        # data: URI unchanged
        assert "data:image/png;base64," in result_md
        assert "![Real](images/real.png)" in result_md

    def test_oversized_image_skipped(self, tmp_path: Path):
        """Image exceeding max_image_bytes skipped with warning."""
        md = "![Big](/html/2411.06644v1/figures/big.png)"
        # 1 byte over limit
        big_data = b"X" * 101

        with patch("agentic_mbse.extraction.web_backend.urllib.request.urlopen") as mock_open:
            mock_open.return_value = _fake_urlopen(big_data)
            result_md, count = _download_arxiv_images(
                md, "https://arxiv.org/html/2411.06644v1", tmp_path,
                max_image_bytes=100,
            )

        assert count == 0
        # Original ref preserved
        assert "/html/2411.06644v1/figures/big.png" in result_md
        assert not (tmp_path / "images").exists()

    def test_duplicate_filenames_deduped(self, tmp_path: Path):
        """Two images with same filename get _2 suffix."""
        md = (
            "![A](/html/2411.06644v1/figures/fig.png)\n"
            "![B](/html/2411.06644v1/extracted/fig.png)"
        )
        fake_a = b"image_a"
        fake_b = b"image_b"

        call_count = 0

        def side_effect(req, **kwargs):
            nonlocal call_count
            call_count += 1
            url = req.full_url if hasattr(req, "full_url") else str(req)
            if "extracted" in url:
                return _fake_urlopen(fake_b)
            return _fake_urlopen(fake_a)

        with patch("agentic_mbse.extraction.web_backend.urllib.request.urlopen", side_effect=side_effect):
            result_md, count = _download_arxiv_images(
                md, "https://arxiv.org/html/2411.06644v1", tmp_path
            )

        assert count == 2
        assert (tmp_path / "images" / "fig.png").exists()
        assert (tmp_path / "images" / "fig_2.png").exists()
        assert (tmp_path / "images" / "fig.png").read_bytes() == fake_a
        assert (tmp_path / "images" / "fig_2.png").read_bytes() == fake_b
        assert "![A](images/fig.png)" in result_md
        assert "![B](images/fig_2.png)" in result_md

    def test_no_images_is_noop(self, tmp_path: Path):
        """Markdown with no image refs → unchanged, count 0."""
        md = "# Hello\n\nJust text, no images."
        result_md, count = _download_arxiv_images(
            md, "https://arxiv.org/html/2411.06644v1", tmp_path
        )
        assert count == 0
        assert result_md == md
        assert not (tmp_path / "images").exists()

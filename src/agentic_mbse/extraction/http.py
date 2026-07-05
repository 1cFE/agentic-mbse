"""Shared HTTP utilities for extraction backends."""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass

USER_AGENT = "agentic-mbse/0.1 (document extraction pipeline)"

DEFAULT_TIMEOUT = 30  # seconds
HEAD_TIMEOUT = 5  # seconds


@dataclass
class FetchResult:
    """Result of an HTTP fetch."""

    content: bytes
    final_url: str
    content_type: str
    encoding: str | None = None

    def text(self) -> str:
        """Decode content to string."""
        enc = self.encoding or "utf-8"
        return self.content.decode(enc)


def fetch_url(url: str, *, timeout: int = DEFAULT_TIMEOUT) -> FetchResult:
    """Fetch URL content with standard headers.

    Returns FetchResult with content bytes, final URL (after redirects),
    content type, and detected encoding.

    Raises:
        urllib.error.URLError: On network errors.
        urllib.error.HTTPError: On HTTP error status codes.
        TimeoutError: When request exceeds timeout.
    """
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content = resp.read()
        final_url = resp.url  # after redirects
        content_type = resp.headers.get_content_type() or ""
        encoding = resp.headers.get_content_charset()
        return FetchResult(
            content=content,
            final_url=final_url,
            content_type=content_type,
            encoding=encoding,
        )


def head_content_type(url: str, *, timeout: int = HEAD_TIMEOUT) -> str | None:
    """Send HEAD request and return Content-Type, or None on failure."""
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.headers.get_content_type()
    except Exception:
        return None

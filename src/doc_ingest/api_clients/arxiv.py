"""arXiv API client for discovering paper sources.

arXiv provides:
- HTML5 rendering: https://arxiv.org/html/{arxiv_id} (high quality, MathML preserved)
- PDF: https://arxiv.org/pdf/{arxiv_id}.pdf

The HTML version is preferred (tier 2) when available, with PDF as fallback (tier 4).
No API key required, but rate limiting is applied as a courtesy.
"""

import re
import time

import requests

from doc_ingest.types import SourceCandidate


class ArXivClient:
    """Client for querying arXiv to discover paper sources.

    The arXiv platform provides both HTML5 and PDF versions of papers. This client
    checks for HTML availability and returns both sources in quality-tier order.
    HTML sources (tier 2) are preferred over PDF (tier 4) for extraction quality.
    """

    HTML_BASE_URL = "https://arxiv.org/html"
    PDF_BASE_URL = "https://arxiv.org/pdf"
    USER_AGENT = "agentic-mbse/doc-ingest (https://github.com/reid/agentic-mbse)"
    REQUEST_DELAY_SECONDS = 0.1  # 100ms courtesy delay between requests

    def __init__(self) -> None:
        """Initialize arXiv client."""
        self._last_request_time: float = 0.0

    def query(self, arxiv_id: str) -> tuple[list[SourceCandidate], list[str]]:
        """Query arXiv for an ID and return discovered sources.

        Checks if HTML version exists and returns both HTML (tier 2) and PDF (tier 4)
        sources. HTML is preferred for higher extraction quality (MathML preserved).

        Args:
            arxiv_id: arXiv identifier (e.g., "2401.00001" or "arXiv:2401.00001")

        Returns:
            Tuple of (source_candidates, errors)
            - source_candidates: List of SourceCandidate sorted by quality tier
            - errors: List of error messages from API (empty on success)
        """
        # Normalize arXiv ID format (remove "arXiv:" prefix if present)
        normalized_id = self._normalize_arxiv_id(arxiv_id)

        # Rate limiting: ensure minimum delay between requests
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY_SECONDS:
            time.sleep(self.REQUEST_DELAY_SECONDS - elapsed)

        sources: list[SourceCandidate] = []
        errors: list[str] = []

        # Check if HTML version exists (HEAD request to avoid downloading full page)
        html_url = f"{self.HTML_BASE_URL}/{normalized_id}"
        html_available = self._check_html_availability(html_url)

        if html_available:
            sources.append(
                SourceCandidate(
                    quality_tier=2,  # Structured HTML (high quality, MathML preserved)
                    format="arxiv_html",
                    url=html_url,
                    discovered_via="arxiv:html",
                )
            )

        # PDF is always available for valid arXiv IDs
        pdf_url = f"{self.PDF_BASE_URL}/{normalized_id}.pdf"
        sources.append(
            SourceCandidate(
                quality_tier=4,  # PDF (standard quality)
                format="pdf",
                url=pdf_url,
                discovered_via="arxiv:pdf",
            )
        )

        # Sort by quality tier (lower = better) - HTML will be first if available
        sources.sort()
        return sources, errors

    def _normalize_arxiv_id(self, arxiv_id: str) -> str:
        """Normalize arXiv ID format by removing prefix.

        Args:
            arxiv_id: arXiv ID in any format (e.g., "2401.00001", "arXiv:2401.00001")

        Returns:
            Normalized ID without prefix (e.g., "2401.00001")
        """
        # Remove "arXiv:" prefix if present (case-insensitive)
        normalized = re.sub(r"^arxiv:\s*", "", arxiv_id, flags=re.IGNORECASE)
        return normalized.strip()

    def _check_html_availability(self, html_url: str) -> bool:
        """Check if HTML version is available via HEAD request.

        Args:
            html_url: Full URL to arXiv HTML page

        Returns:
            True if HTML version exists (HTTP 200), False otherwise
        """
        headers = {"User-Agent": self.USER_AGENT}

        try:
            response = requests.head(html_url, headers=headers, timeout=10, allow_redirects=True)
            self._last_request_time = time.time()
            return response.status_code == 200

        except requests.RequestException:
            self._last_request_time = time.time()
            # If HEAD request fails, assume HTML not available (fallback to PDF)
            return False

"""OpenAlex API client for discovering academic paper sources.

OpenAlex provides free metadata for academic papers including:
- Open access PDF URLs
- Publisher landing pages (may have HTML full text)
- PMC links (which have JATS XML)

Rate limit: 100,000 requests/day (free tier, no API key required).
"""

import time
from typing import Any

import requests

from doc_ingest.types import SourceCandidate


class OpenAlexClient:
    """Client for querying OpenAlex API to discover paper sources.

    The OpenAlex API provides comprehensive metadata about academic papers,
    including various access URLs that can be used for document extraction.
    This client parses the response and returns SourceCandidate objects
    sorted by quality tier.
    """

    BASE_URL = "https://api.openalex.org/works"
    USER_AGENT = "agentic-mbse/doc-ingest (https://github.com/reid/agentic-mbse)"
    REQUEST_DELAY_SECONDS = 0.1  # 100ms courtesy delay between requests

    def __init__(self) -> None:
        """Initialize OpenAlex client."""
        self._last_request_time: float = 0.0

    def query(self, doi: str) -> tuple[list[SourceCandidate], list[str]]:
        """Query OpenAlex for a DOI and return discovered sources.

        Parses the OpenAlex response to extract:
        - open_access.oa_url (primary open access source)
        - primary_location.pdf_url (publisher PDF)
        - primary_location.landing_page_url (publisher page, may have HTML)
        - PMC ID from ids.pmcid (for JATS XML discovery in future)

        Args:
            doi: Document DOI (e.g., "10.1098/rsta.2020.0053")

        Returns:
            Tuple of (source_candidates, errors)
            - source_candidates: List of SourceCandidate sorted by quality tier
            - errors: List of error messages from API (empty on success)
        """
        # Rate limiting: ensure minimum delay between requests
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY_SECONDS:
            time.sleep(self.REQUEST_DELAY_SECONDS - elapsed)

        # Query OpenAlex API
        url = f"{self.BASE_URL}/doi:{doi}"
        headers = {"User-Agent": self.USER_AGENT}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            self._last_request_time = time.time()

            if response.status_code == 404:
                return [], [f"DOI not found in OpenAlex: {doi}"]

            if response.status_code != 200:
                return [], [f"OpenAlex API error: HTTP {response.status_code}"]

            data = response.json()
            sources = self._parse_response(data, doi)
            return sources, []

        except requests.RequestException as e:
            self._last_request_time = time.time()
            return [], [f"OpenAlex API request failed: {e}"]

    def _parse_response(self, data: dict[str, Any], doi: str) -> list[SourceCandidate]:
        """Parse OpenAlex response JSON and extract source candidates.

        Extracts sources from multiple locations in the response:
        1. open_access.oa_url - primary open access location
        2. primary_location.pdf_url - publisher PDF
        3. primary_location.landing_page_url - publisher page
        4. best_oa_location - fallback open access location

        Args:
            data: Parsed JSON response from OpenAlex API
            doi: Original DOI (for provenance tracking)

        Returns:
            List of SourceCandidate objects sorted by quality tier
        """
        sources: list[SourceCandidate] = []

        # Extract open_access.oa_url (primary OA source, usually PDF)
        open_access = data.get("open_access", {})
        if oa_url := open_access.get("oa_url"):
            sources.append(
                SourceCandidate(
                    quality_tier=4,  # Assume PDF quality
                    format="pdf",
                    url=oa_url,
                    discovered_via="openalex:open_access.oa_url",
                    license=open_access.get("oa_status"),
                )
            )

        # Extract primary_location sources
        primary_location = data.get("primary_location", {})

        # PDF URL from primary location
        if pdf_url := primary_location.get("pdf_url"):
            # Avoid duplicate if same as oa_url
            if pdf_url not in [s.url for s in sources]:
                sources.append(
                    SourceCandidate(
                        quality_tier=4,
                        format="pdf",
                        url=pdf_url,
                        discovered_via="openalex:primary_location.pdf_url",
                    )
                )

        # Landing page URL (may have HTML full text)
        if landing_url := primary_location.get("landing_page_url"):
            # Only add if it's not just a DOI resolver
            if not landing_url.startswith("https://doi.org/"):
                sources.append(
                    SourceCandidate(
                        quality_tier=3,  # Publisher HTML (unknown quality)
                        format="publisher_html",
                        url=landing_url,
                        discovered_via="openalex:primary_location.landing_page_url",
                        publisher=primary_location.get("source", {}).get("display_name"),
                    )
                )

        # Extract best_oa_location as fallback
        best_oa = data.get("best_oa_location", {})
        if best_oa_url := best_oa.get("pdf_url"):
            # Avoid duplicates
            if best_oa_url not in [s.url for s in sources]:
                sources.append(
                    SourceCandidate(
                        quality_tier=4,
                        format="pdf",
                        url=best_oa_url,
                        discovered_via="openalex:best_oa_location.pdf_url",
                        license=best_oa.get("license"),
                    )
                )

        # Sort by quality tier (lower = better)
        sources.sort()
        return sources

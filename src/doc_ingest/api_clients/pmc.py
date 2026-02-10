"""PubMed Central (PMC) API client for discovering JATS XML sources.

PMC provides:
- JATS XML: Structured full text with semantic tags, tables, math (tier 1 - highest quality)

The PMC E-utilities API provides free access to open-access articles via efetch.
Rate limit: 3 requests/second without API key, 10 requests/second with API key.
"""

import re
import time

import requests

from doc_ingest.types import SourceCandidate


class PMCClient:
    """Client for querying PubMed Central to discover JATS XML sources.

    The PMC E-utilities API provides access to open-access articles in JATS XML
    format, which is the highest quality source format (tier 1) for document
    extraction. JATS XML preserves semantic structure, tables, math, and citations.
    """

    EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    USER_AGENT = "agentic-mbse/doc-ingest (https://github.com/reid/agentic-mbse)"
    REQUEST_DELAY_SECONDS = 0.35  # ~3 requests/sec (conservative, no API key)

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize PMC client.

        Args:
            api_key: Optional NCBI API key for higher rate limits (10 req/sec vs 3 req/sec)
        """
        self._api_key = api_key
        self._last_request_time: float = 0.0
        # Higher rate limit with API key
        if api_key:
            self.REQUEST_DELAY_SECONDS = 0.11  # ~10 requests/sec

    def query(self, pmc_id: str) -> tuple[list[SourceCandidate], list[str]]:
        """Query PMC for a PMC ID and return JATS XML source.

        Constructs efetch URL to retrieve JATS XML from PMC. PMC IDs should
        include the "PMC" prefix (e.g., "PMC7463680"). If the prefix is missing,
        it will be added automatically.

        Args:
            pmc_id: PMC identifier (e.g., "PMC7463680" or "7463680")

        Returns:
            Tuple of (source_candidates, errors)
            - source_candidates: List with single SourceCandidate for JATS XML (tier 1)
            - errors: List of error messages from API (empty on success)
        """
        # Normalize PMC ID format (ensure "PMC" prefix)
        normalized_id = self._normalize_pmc_id(pmc_id)

        # Rate limiting: ensure minimum delay between requests
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY_SECONDS:
            time.sleep(self.REQUEST_DELAY_SECONDS - elapsed)

        # Construct efetch URL for JATS XML retrieval
        params = {
            "db": "pmc",
            "id": normalized_id,
            "rettype": "xml",
        }
        if self._api_key:
            params["api_key"] = self._api_key

        headers = {"User-Agent": self.USER_AGENT}

        try:
            # HEAD request to check availability without downloading full XML
            response = requests.head(
                self.EFETCH_URL, params=params, headers=headers, timeout=10, allow_redirects=True
            )
            self._last_request_time = time.time()

            # Check if PMC ID is valid (200 = available, 400 = invalid ID)
            if response.status_code == 400:
                return [], [f"PMC ID not found or invalid: {pmc_id}"]

            if response.status_code != 200:
                return [], [f"PMC API error: HTTP {response.status_code}"]

            # Construct URL for downstream converter to fetch
            xml_url = f"{self.EFETCH_URL}?db=pmc&id={normalized_id}&rettype=xml"
            if self._api_key:
                xml_url += f"&api_key={self._api_key}"

            source = SourceCandidate(
                quality_tier=1,  # Structured JATS XML (highest quality)
                format="jats_xml",
                url=xml_url,
                discovered_via="pmc:efetch",
            )

            return [source], []

        except requests.RequestException as e:
            self._last_request_time = time.time()
            return [], [f"PMC API request failed: {e}"]

    def _normalize_pmc_id(self, pmc_id: str) -> str:
        """Normalize PMC ID format by ensuring "PMC" prefix.

        Args:
            pmc_id: PMC ID in any format (e.g., "7463680", "PMC7463680", "pmc7463680")

        Returns:
            Normalized ID with "PMC" prefix (e.g., "PMC7463680")
        """
        # Remove whitespace
        normalized = pmc_id.strip()

        # Add "PMC" prefix if missing (case-insensitive check)
        if not re.match(r"^pmc\d+$", normalized, flags=re.IGNORECASE):
            normalized = f"PMC{normalized}"

        # Ensure uppercase PMC prefix
        normalized = re.sub(r"^pmc", "PMC", normalized, flags=re.IGNORECASE)

        return normalized

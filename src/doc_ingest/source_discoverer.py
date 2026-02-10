"""Source discovery for document extraction.

Discovers source candidates for documents using:
- Local filesystem for direct file paths
- OpenAlex API for DOI-based discovery
- arXiv API for arXiv ID-based discovery
- PMC API for PMC ID-based discovery (JATS XML)
"""

from pathlib import Path

from doc_ingest.api_clients.arxiv import ArXivClient
from doc_ingest.api_clients.openalex import OpenAlexClient
from doc_ingest.api_clients.pmc import PMCClient
from doc_ingest.discovery_cache import DiscoveryCache
from doc_ingest.types import DocumentIdentifiers, SourceCandidate


class SourceDiscoverer:
    """Discover source candidates for document extraction.

    Discovers sources from multiple channels:
    - Local file paths → single SourceCandidate with local_path
    - DOI → OpenAlex API (returns PDFs, publisher pages, PMC links)
    - arXiv ID → arXiv API (returns HTML + PDF sources)
    - PMC ID → PMC API (returns JATS XML)

    All discovered sources are cached to avoid redundant API calls.
    """

    def __init__(self, cache: DiscoveryCache, pmc_api_key: str | None = None) -> None:
        """Initialize discoverer with discovery cache and API clients.

        Args:
            cache: DiscoveryCache instance for caching discovered sources
            pmc_api_key: Optional NCBI API key for PMC (higher rate limits)
        """
        self._cache = cache
        self._openalex_client = OpenAlexClient()
        self._arxiv_client = ArXivClient()
        self._pmc_client = PMCClient(api_key=pmc_api_key)

    def discover(self, identifiers: DocumentIdentifiers) -> tuple[list[SourceCandidate], list[str]]:
        """Resolve identifiers to ranked source candidates.

        Returns cached sources if available, otherwise performs discovery and caches
        the result. Discovery strategy:
        1. Check cache first (avoid redundant API calls)
        2. Discover from local filesystem (if local_path provided)
        3. Discover from OpenAlex API (if DOI provided)
        4. Discover from arXiv API (if arxiv_id provided)
        5. Discover from PMC API (if pmc_id provided)
        6. Sort by quality tier and cache result

        Args:
            identifiers: Document identifiers to resolve

        Returns:
            Tuple of (source_candidates, discovery_errors)
            - source_candidates: List of SourceCandidate sorted by quality tier
            - discovery_errors: List of error messages from discovery APIs
        """
        # Check cache first
        primary_type, primary_value = identifiers.primary_identifier()
        cache_key = f"{primary_type}:{primary_value}"

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached, []

        # Perform discovery
        sources: list[SourceCandidate] = []
        errors: list[str] = []

        # Local file path discovery
        if identifiers.local_path is not None:
            local_path = Path(identifiers.local_path)
            if local_path.exists():
                # Infer format from extension
                format_map = {
                    ".pdf": "pdf",
                    ".xml": "jats_xml",
                    ".html": "publisher_html",
                    ".docx": "docx",
                }
                suffix = local_path.suffix.lower()
                format_type = format_map.get(suffix, "pdf")
                quality_tier = 4 if format_type == "pdf" else 1  # PDF=4, others=1 for simplicity

                sources.append(
                    SourceCandidate(
                        quality_tier=quality_tier,
                        format=format_type,  # type: ignore[arg-type]
                        local_path=str(local_path),
                        discovered_via="local_filesystem",
                    )
                )
            else:
                errors.append(f"Local file not found: {identifiers.local_path}")

        # OpenAlex API discovery for DOIs
        if identifiers.doi is not None:
            openalex_sources, openalex_errors = self._openalex_client.query(identifiers.doi)
            sources.extend(openalex_sources)
            errors.extend(openalex_errors)

        # arXiv API discovery for arXiv IDs
        if identifiers.arxiv_id is not None:
            arxiv_sources, arxiv_errors = self._arxiv_client.query(identifiers.arxiv_id)
            sources.extend(arxiv_sources)
            errors.extend(arxiv_errors)

        # PMC API discovery for PMC IDs
        if identifiers.pmc_id is not None:
            pmc_sources, pmc_errors = self._pmc_client.query(identifiers.pmc_id)
            sources.extend(pmc_sources)
            errors.extend(pmc_errors)

        # Sort by quality tier (lower = better)
        sources.sort()

        # Cache the result if we found sources
        if sources:
            self._cache.put(cache_key, sources)

        return sources, errors

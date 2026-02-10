"""Source discovery for document extraction.

Minimal stub implementation of SourceDiscoverer for MVP. Provides basic discovery
for local files and stubbed discovery for identifiers. Full API integration with
OpenAlex, arXiv, and PMC APIs deferred to post-MVP.
"""

from pathlib import Path

from doc_ingest.discovery_cache import DiscoveryCache
from doc_ingest.types import DocumentIdentifiers, SourceCandidate


class SourceDiscoverer:
    """Discover source candidates for document extraction.

    Stub implementation that handles:
    - Local file paths → single SourceCandidate with local_path
    - DOI/arXiv/PMC identifiers → stubbed mock sources for testing

    Full API integration with OpenAlex, arXiv, and PMC is deferred to post-MVP.
    """

    def __init__(self, cache: DiscoveryCache) -> None:
        """Initialize discoverer with discovery cache.

        Args:
            cache: DiscoveryCache instance for caching discovered sources
        """
        self._cache = cache

    def discover(self, identifiers: DocumentIdentifiers) -> tuple[list[SourceCandidate], list[str]]:
        """Resolve identifiers to ranked source candidates.

        Returns cached sources if available, otherwise performs discovery and caches
        the result. For MVP, only supports local file discovery; API discovery is
        stubbed with mock sources.

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

        # Stubbed API discovery for identifiers
        # For MVP, create mock sources to enable testing
        if identifiers.doi is not None:
            # Mock JATS XML source for DOI
            sources.append(
                SourceCandidate(
                    quality_tier=1,
                    format="jats_xml",
                    url=f"https://api.stub/jats/{identifiers.doi}",
                    discovered_via="stub_api",
                )
            )
            sources.append(
                SourceCandidate(
                    quality_tier=4,
                    format="pdf",
                    url=f"https://api.stub/pdf/{identifiers.doi}",
                    discovered_via="stub_api",
                )
            )

        if identifiers.arxiv_id is not None:
            # Mock arXiv HTML source
            sources.append(
                SourceCandidate(
                    quality_tier=2,
                    format="arxiv_html",
                    url=f"https://arxiv.org/html/{identifiers.arxiv_id}",
                    discovered_via="stub_api",
                )
            )

        # Sort by quality tier (lower = better)
        sources.sort()

        # Cache the result if we found sources
        if sources:
            self._cache.put(cache_key, sources)

        return sources, errors

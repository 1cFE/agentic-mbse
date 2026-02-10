"""Unit tests for SourceDiscoverer with OpenAlex integration."""

from unittest.mock import Mock, patch

import pytest

from doc_ingest.source_discoverer import SourceDiscoverer
from doc_ingest.types import DocumentIdentifiers, SourceCandidate


@pytest.fixture
def mock_cache():
    """Create mock DiscoveryCache."""
    cache = Mock()
    cache.get.return_value = None
    cache.put.return_value = None
    return cache


@pytest.fixture
def discoverer(mock_cache):
    """Create SourceDiscoverer with mocked cache."""
    return SourceDiscoverer(cache=mock_cache)


def test_discover_local_file_exists(discoverer, tmp_path):
    """Test discovering local file returns single source candidate."""
    # Arrange
    test_file = tmp_path / "paper.pdf"
    test_file.write_text("test content")
    identifiers = DocumentIdentifiers(local_path=str(test_file))

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) == 1
    assert sources[0].format == "pdf"
    assert sources[0].local_path == str(test_file)
    assert sources[0].discovered_via == "local_filesystem"
    assert len(errors) == 0


def test_discover_local_file_not_found(discoverer, tmp_path):
    """Test discovering non-existent local file reports error."""
    # Arrange
    missing_file = tmp_path / "missing.pdf"
    identifiers = DocumentIdentifiers(local_path=str(missing_file))

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) == 0
    assert len(errors) == 1
    assert "not found" in errors[0].lower()


def test_discover_doi_queries_openalex(discoverer):
    """Test DOI discovery queries OpenAlex API."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    mock_sources = [
        SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="https://example.com/paper.pdf",
            discovered_via="openalex:open_access.oa_url",
        )
    ]

    # Act
    with patch.object(discoverer._openalex_client, "query", return_value=(mock_sources, [])):
        sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) >= 1
    assert any(s.format == "pdf" for s in sources)
    assert any(s.discovered_via.startswith("openalex:") for s in sources)
    assert len(errors) == 0


def test_discover_arxiv_returns_stub_source(discoverer):
    """Test arXiv ID discovery returns stubbed HTML source."""
    # Arrange
    identifiers = DocumentIdentifiers(arxiv_id="1234.5678")

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) >= 1
    assert any(s.format == "arxiv_html" for s in sources)
    assert any("arxiv.org" in (s.url or "") for s in sources)
    assert len(errors) == 0


def test_discover_sources_sorted_by_quality_tier(discoverer):
    """Test sources are sorted by quality tier (lower = better)."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    # Verify sorting: quality_tier should be ascending
    tiers = [s.quality_tier for s in sources]
    assert tiers == sorted(tiers)


def test_discover_caches_result(discoverer, mock_cache):
    """Test discovery result is cached."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    mock_sources = [
        SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="https://example.com/paper.pdf",
            discovered_via="openalex:open_access.oa_url",
        )
    ]

    # Act
    with patch.object(discoverer._openalex_client, "query", return_value=(mock_sources, [])):
        sources, errors = discoverer.discover(identifiers)

    # Assert
    # Verify cache.put was called with the sources
    mock_cache.put.assert_called_once()
    cache_key, cached_sources = mock_cache.put.call_args[0]
    assert cache_key == "doi:10.1234/test"
    assert cached_sources == sources


def test_discover_returns_cached_result_on_hit(discoverer, mock_cache):
    """Test cached discovery is returned without re-discovery."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test")
    cached_sources = [Mock(quality_tier=1, format="jats_xml", url="https://cached.com/paper.xml")]
    mock_cache.get.return_value = cached_sources

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    assert sources == cached_sources
    assert len(errors) == 0
    # Verify cache.put was NOT called (cache hit)
    mock_cache.put.assert_not_called()


def test_discover_local_xml_infers_jats_format(discoverer, tmp_path):
    """Test .xml file is inferred as JATS format."""
    # Arrange
    test_file = tmp_path / "paper.xml"
    test_file.write_text("<article>test</article>")
    identifiers = DocumentIdentifiers(local_path=str(test_file))

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) == 1
    assert sources[0].format == "jats_xml"
    assert sources[0].quality_tier == 1  # JATS = tier 1


def test_discover_local_html_infers_publisher_html_format(discoverer, tmp_path):
    """Test .html file is inferred as publisher_html format."""
    # Arrange
    test_file = tmp_path / "paper.html"
    test_file.write_text("<html><body>test</body></html>")
    identifiers = DocumentIdentifiers(local_path=str(test_file))

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) == 1
    assert sources[0].format == "publisher_html"


def test_discover_local_docx_infers_docx_format(discoverer, tmp_path):
    """Test .docx file is inferred as docx format."""
    # Arrange
    test_file = tmp_path / "paper.docx"
    test_file.write_bytes(b"PK\x03\x04")  # ZIP header (simplified)
    identifiers = DocumentIdentifiers(local_path=str(test_file))

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) == 1
    assert sources[0].format == "docx"


def test_discover_no_sources_no_cache(discoverer, mock_cache):
    """Test no sources found does not cache result."""
    # Arrange
    identifiers = DocumentIdentifiers(local_path="/nonexistent/file.pdf")

    # Act
    sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) == 0
    # Verify cache.put was NOT called (no sources to cache)
    mock_cache.put.assert_not_called()


def test_discover_primary_identifier_used_for_cache_key(discoverer, mock_cache):
    """Test primary identifier is used for cache key."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.1234/test", arxiv_id="1234.5678")
    mock_sources = [
        SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="https://example.com/paper.pdf",
            discovered_via="openalex:open_access.oa_url",
        )
    ]

    # Act
    with patch.object(discoverer._openalex_client, "query", return_value=(mock_sources, [])):
        sources, errors = discoverer.discover(identifiers)

    # Assert
    # DOI has higher priority, so cache key should be "doi:10.1234/test"
    cache_key = mock_cache.get.call_args[0][0]
    assert cache_key == "doi:10.1234/test"


def test_discover_doi_propagates_openalex_errors(discoverer):
    """Test OpenAlex API errors are propagated in discovery errors."""
    # Arrange
    identifiers = DocumentIdentifiers(doi="10.9999/nonexistent")

    # Act
    with patch.object(
        discoverer._openalex_client,
        "query",
        return_value=([], ["DOI not found in OpenAlex: 10.9999/nonexistent"]),
    ):
        sources, errors = discoverer.discover(identifiers)

    # Assert
    assert len(sources) == 0
    assert len(errors) == 1
    assert "not found" in errors[0].lower()

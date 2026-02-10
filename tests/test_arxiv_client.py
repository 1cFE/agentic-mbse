"""Unit tests for ArXivClient."""

from unittest.mock import Mock, patch

import pytest
import requests

from doc_ingest.api_clients.arxiv import ArXivClient


@pytest.fixture
def arxiv_client():
    """Create ArXivClient instance."""
    return ArXivClient()


def test_query_returns_html_and_pdf_when_html_available(arxiv_client):
    """Test query returns both HTML and PDF sources when HTML exists."""
    # Arrange
    arxiv_id = "2401.00001"

    # Mock HEAD request to return success (HTML available)
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = arxiv_client.query(arxiv_id)

    # Assert
    assert len(sources) == 2
    assert len(errors) == 0

    # HTML should be first (tier 2 < tier 4)
    assert sources[0].format == "arxiv_html"
    assert sources[0].quality_tier == 2
    assert sources[0].url == f"https://arxiv.org/html/{arxiv_id}"
    assert sources[0].discovered_via == "arxiv:html"

    # PDF should be second
    assert sources[1].format == "pdf"
    assert sources[1].quality_tier == 4
    assert sources[1].url == f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    assert sources[1].discovered_via == "arxiv:pdf"


def test_query_returns_only_pdf_when_html_not_available(arxiv_client):
    """Test query returns only PDF when HTML version does not exist."""
    # Arrange
    arxiv_id = "1234.5678"

    # Mock HEAD request to return 404 (HTML not available)
    mock_response = Mock()
    mock_response.status_code = 404

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = arxiv_client.query(arxiv_id)

    # Assert
    assert len(sources) == 1
    assert len(errors) == 0
    assert sources[0].format == "pdf"
    assert sources[0].quality_tier == 4
    assert sources[0].url == f"https://arxiv.org/pdf/{arxiv_id}.pdf"


def test_query_handles_arxiv_prefix(arxiv_client):
    """Test query normalizes arXiv ID with prefix."""
    # Arrange
    arxiv_id = "arXiv:2401.00001"
    normalized_id = "2401.00001"

    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = arxiv_client.query(arxiv_id)

    # Assert - URLs should use normalized ID (without prefix)
    assert sources[0].url == f"https://arxiv.org/html/{normalized_id}"
    assert sources[1].url == f"https://arxiv.org/pdf/{normalized_id}.pdf"


def test_query_handles_arxiv_prefix_case_insensitive(arxiv_client):
    """Test query normalizes arXiv ID with case variations."""
    # Arrange - various case variations
    test_cases = [
        "arXiv:2401.00001",
        "arxiv:2401.00001",
        "ARXIV:2401.00001",
        "ArXiv:2401.00001",
    ]
    normalized_id = "2401.00001"

    mock_response = Mock()
    mock_response.status_code = 404  # HTML not available for simplicity

    for arxiv_id in test_cases:
        # Act
        with patch("requests.head", return_value=mock_response):
            sources, _ = arxiv_client.query(arxiv_id)

        # Assert - All should normalize to same ID
        assert sources[0].url == f"https://arxiv.org/pdf/{normalized_id}.pdf"


def test_query_handles_head_request_failure(arxiv_client):
    """Test query handles HEAD request failure gracefully."""
    # Arrange
    arxiv_id = "2401.00001"

    # Mock HEAD request to raise exception
    with patch("requests.head", side_effect=requests.RequestException("Network error")):
        sources, errors = arxiv_client.query(arxiv_id)

    # Assert - Should fallback to PDF only
    assert len(sources) == 1
    assert sources[0].format == "pdf"
    assert len(errors) == 0  # Errors are silent (fallback behavior)


def test_query_applies_rate_limiting(arxiv_client):
    """Test query applies rate limiting between requests."""
    # Arrange
    arxiv_id = "2401.00001"
    mock_response = Mock()
    mock_response.status_code = 200

    # Act - Make two requests back-to-back
    with patch("requests.head", return_value=mock_response):
        with patch("time.sleep") as mock_sleep:
            arxiv_client.query(arxiv_id)
            arxiv_client.query(arxiv_id)

    # Assert - sleep should be called to enforce rate limit
    assert mock_sleep.call_count >= 1


def test_query_includes_user_agent_header(arxiv_client):
    """Test query includes User-Agent header in requests."""
    # Arrange
    arxiv_id = "2401.00001"
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response) as mock_head:
        arxiv_client.query(arxiv_id)

    # Assert
    assert mock_head.called
    call_kwargs = mock_head.call_args[1]
    assert "headers" in call_kwargs
    assert "User-Agent" in call_kwargs["headers"]
    assert "agentic-mbse" in call_kwargs["headers"]["User-Agent"]


def test_query_uses_correct_timeout(arxiv_client):
    """Test query uses 10 second timeout for HEAD requests."""
    # Arrange
    arxiv_id = "2401.00001"
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response) as mock_head:
        arxiv_client.query(arxiv_id)

    # Assert
    call_kwargs = mock_head.call_args[1]
    assert call_kwargs.get("timeout") == 10


def test_query_allows_redirects(arxiv_client):
    """Test query allows redirects for HEAD requests."""
    # Arrange
    arxiv_id = "2401.00001"
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response) as mock_head:
        arxiv_client.query(arxiv_id)

    # Assert
    call_kwargs = mock_head.call_args[1]
    assert call_kwargs.get("allow_redirects") is True


def test_normalize_arxiv_id_removes_prefix():
    """Test _normalize_arxiv_id removes arXiv: prefix."""
    # Arrange
    client = ArXivClient()

    # Act & Assert
    assert client._normalize_arxiv_id("2401.00001") == "2401.00001"
    assert client._normalize_arxiv_id("arXiv:2401.00001") == "2401.00001"
    assert client._normalize_arxiv_id("arxiv:2401.00001") == "2401.00001"
    assert client._normalize_arxiv_id("ARXIV:2401.00001") == "2401.00001"


def test_normalize_arxiv_id_strips_whitespace():
    """Test _normalize_arxiv_id strips whitespace."""
    # Arrange
    client = ArXivClient()

    # Act & Assert
    assert client._normalize_arxiv_id("  2401.00001  ") == "2401.00001"
    assert client._normalize_arxiv_id("arXiv: 2401.00001") == "2401.00001"
    assert client._normalize_arxiv_id("arXiv:  2401.00001  ") == "2401.00001"


def test_check_html_availability_returns_true_for_200():
    """Test _check_html_availability returns True for HTTP 200."""
    # Arrange
    client = ArXivClient()
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response):
        result = client._check_html_availability("https://arxiv.org/html/2401.00001")

    # Assert
    assert result is True


def test_check_html_availability_returns_false_for_404():
    """Test _check_html_availability returns False for HTTP 404."""
    # Arrange
    client = ArXivClient()
    mock_response = Mock()
    mock_response.status_code = 404

    # Act
    with patch("requests.head", return_value=mock_response):
        result = client._check_html_availability("https://arxiv.org/html/2401.00001")

    # Assert
    assert result is False


def test_check_html_availability_returns_false_on_exception():
    """Test _check_html_availability returns False on request exception."""
    # Arrange
    client = ArXivClient()

    # Act
    with patch("requests.head", side_effect=requests.RequestException("Network error")):
        result = client._check_html_availability("https://arxiv.org/html/2401.00001")

    # Assert
    assert result is False


def test_sources_are_sortable_by_quality_tier():
    """Test that returned sources maintain quality tier ordering."""
    # Arrange
    client = ArXivClient()
    mock_response = Mock()
    mock_response.status_code = 200  # HTML available

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, _ = client.query("2401.00001")

    # Assert - Sources should be sorted (tier 2 before tier 4)
    assert sources[0].quality_tier < sources[1].quality_tier
    assert sources == sorted(sources)

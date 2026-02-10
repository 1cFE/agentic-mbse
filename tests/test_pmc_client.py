"""Unit tests for PMCClient."""

from unittest.mock import Mock, patch

import pytest
import requests

from doc_ingest.api_clients.pmc import PMCClient


@pytest.fixture
def pmc_client():
    """Create PMCClient instance without API key."""
    return PMCClient()


@pytest.fixture
def pmc_client_with_api_key():
    """Create PMCClient instance with API key."""
    return PMCClient(api_key="test_api_key_12345")


def test_query_returns_jats_xml_source(pmc_client):
    """Test query returns JATS XML source candidate."""
    # Arrange
    pmc_id = "PMC7463680"

    # Mock HEAD request to return success (PMC ID valid)
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = pmc_client.query(pmc_id)

    # Assert
    assert len(sources) == 1
    assert len(errors) == 0

    source = sources[0]
    assert source.format == "jats_xml"
    assert source.quality_tier == 1  # Highest quality tier
    assert source.url is not None
    assert pmc_id in source.url
    assert "efetch.fcgi" in source.url
    assert "db=pmc" in source.url
    assert "rettype=xml" in source.url
    assert source.discovered_via == "pmc:efetch"


def test_query_returns_error_for_404(pmc_client):
    """Test query returns error for invalid PMC ID (400 status)."""
    # Arrange
    pmc_id = "PMC9999999999"

    # Mock HEAD request to return 400 (invalid ID)
    mock_response = Mock()
    mock_response.status_code = 400

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = pmc_client.query(pmc_id)

    # Assert
    assert len(sources) == 0
    assert len(errors) == 1
    assert "not found" in errors[0].lower() or "invalid" in errors[0].lower()
    assert pmc_id in errors[0]


def test_query_returns_error_for_non_200(pmc_client):
    """Test query returns error for non-200 status codes."""
    # Arrange
    pmc_id = "PMC7463680"

    # Mock HEAD request to return 500 (server error)
    mock_response = Mock()
    mock_response.status_code = 500

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = pmc_client.query(pmc_id)

    # Assert
    assert len(sources) == 0
    assert len(errors) == 1
    assert "HTTP 500" in errors[0]


def test_query_handles_network_error(pmc_client):
    """Test query handles network errors gracefully."""
    # Arrange
    pmc_id = "PMC7463680"

    # Mock HEAD request to raise exception
    with patch("requests.head", side_effect=requests.RequestException("Network error")):
        sources, errors = pmc_client.query(pmc_id)

    # Assert
    assert len(sources) == 0
    assert len(errors) == 1
    assert "request failed" in errors[0].lower()


def test_query_normalizes_pmc_id_without_prefix(pmc_client):
    """Test query normalizes PMC ID by adding prefix."""
    # Arrange
    pmc_id_numeric = "7463680"
    expected_normalized = "PMC7463680"

    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = pmc_client.query(pmc_id_numeric)

    # Assert - URL should contain normalized ID with "PMC" prefix
    assert len(sources) == 1
    assert expected_normalized in sources[0].url


def test_query_normalizes_pmc_id_case_insensitive(pmc_client):
    """Test query normalizes PMC ID with case variations."""
    # Arrange - various case variations
    test_cases = [
        "PMC7463680",
        "pmc7463680",
        "Pmc7463680",
        "pMc7463680",
    ]
    expected_normalized = "PMC7463680"

    mock_response = Mock()
    mock_response.status_code = 200

    for pmc_id in test_cases:
        # Act
        with patch("requests.head", return_value=mock_response):
            sources, _ = pmc_client.query(pmc_id)

        # Assert - All should normalize to same ID
        assert len(sources) == 1
        assert expected_normalized in sources[0].url


def test_query_includes_api_key_when_provided(pmc_client_with_api_key):
    """Test query includes API key in URL when provided."""
    # Arrange
    pmc_id = "PMC7463680"

    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = pmc_client_with_api_key.query(pmc_id)

    # Assert
    assert len(sources) == 1
    assert "api_key=test_api_key_12345" in sources[0].url


def test_query_does_not_include_api_key_when_not_provided(pmc_client):
    """Test query does not include API key in URL when not provided."""
    # Arrange
    pmc_id = "PMC7463680"

    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, errors = pmc_client.query(pmc_id)

    # Assert
    assert len(sources) == 1
    assert "api_key" not in sources[0].url


def test_query_applies_rate_limiting_without_api_key(pmc_client):
    """Test query applies rate limiting between requests (no API key)."""
    # Arrange
    pmc_id = "PMC7463680"
    mock_response = Mock()
    mock_response.status_code = 200

    # Act - Make two requests back-to-back
    with patch("requests.head", return_value=mock_response):
        with patch("time.sleep") as mock_sleep:
            pmc_client.query(pmc_id)
            pmc_client.query(pmc_id)

    # Assert - sleep should be called to enforce rate limit
    assert mock_sleep.call_count >= 1


def test_query_applies_different_rate_limit_with_api_key(pmc_client_with_api_key):
    """Test query applies different rate limiting with API key."""
    # Arrange - Client with API key should have faster rate limit
    assert pmc_client_with_api_key.REQUEST_DELAY_SECONDS < PMCClient().REQUEST_DELAY_SECONDS


def test_query_includes_user_agent_header(pmc_client):
    """Test query includes User-Agent header in requests."""
    # Arrange
    pmc_id = "PMC7463680"
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response) as mock_head:
        pmc_client.query(pmc_id)

    # Assert
    assert mock_head.called
    call_kwargs = mock_head.call_args[1]
    assert "headers" in call_kwargs
    assert "User-Agent" in call_kwargs["headers"]
    assert "agentic-mbse" in call_kwargs["headers"]["User-Agent"]


def test_query_uses_correct_timeout(pmc_client):
    """Test query uses 10 second timeout for HEAD requests."""
    # Arrange
    pmc_id = "PMC7463680"
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response) as mock_head:
        pmc_client.query(pmc_id)

    # Assert
    call_kwargs = mock_head.call_args[1]
    assert call_kwargs.get("timeout") == 10


def test_query_allows_redirects(pmc_client):
    """Test query allows redirects for HEAD requests."""
    # Arrange
    pmc_id = "PMC7463680"
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response) as mock_head:
        pmc_client.query(pmc_id)

    # Assert
    call_kwargs = mock_head.call_args[1]
    assert call_kwargs.get("allow_redirects") is True


def test_normalize_pmc_id_adds_prefix():
    """Test _normalize_pmc_id adds PMC prefix when missing."""
    # Arrange
    client = PMCClient()

    # Act & Assert
    assert client._normalize_pmc_id("7463680") == "PMC7463680"
    assert client._normalize_pmc_id("PMC7463680") == "PMC7463680"


def test_normalize_pmc_id_handles_case_variations():
    """Test _normalize_pmc_id handles case variations."""
    # Arrange
    client = PMCClient()

    # Act & Assert
    assert client._normalize_pmc_id("pmc7463680") == "PMC7463680"
    assert client._normalize_pmc_id("Pmc7463680") == "PMC7463680"
    assert client._normalize_pmc_id("PMC7463680") == "PMC7463680"
    assert client._normalize_pmc_id("pMc7463680") == "PMC7463680"


def test_normalize_pmc_id_strips_whitespace():
    """Test _normalize_pmc_id strips whitespace."""
    # Arrange
    client = PMCClient()

    # Act & Assert
    assert client._normalize_pmc_id("  7463680  ") == "PMC7463680"
    assert client._normalize_pmc_id("  PMC7463680  ") == "PMC7463680"
    assert (
        client._normalize_pmc_id(" pmc 7463680 ") == "PMCpmc 7463680"
    )  # Note: only prefix normalized


def test_source_has_tier_1_quality():
    """Test that PMC sources have highest quality tier (tier 1)."""
    # Arrange
    client = PMCClient()
    mock_response = Mock()
    mock_response.status_code = 200

    # Act
    with patch("requests.head", return_value=mock_response):
        sources, _ = client.query("PMC7463680")

    # Assert
    assert sources[0].quality_tier == 1  # Tier 1 = highest quality (JATS XML)

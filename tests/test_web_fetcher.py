"""Tests for WebFetcher (spec 005)."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from src.doc_ingest.types import SourceCandidate
from src.doc_ingest.web_fetcher import FetchError, WebFetcher


class TestFetchError:
    """Tests for FetchError exception class."""

    def test_construction_with_category(self) -> None:
        """Given message and category, when constructed, then stores both."""
        error = FetchError("Protocol not allowed", category="invalid_protocol")
        assert str(error) == "Protocol not allowed"
        assert error.category == "invalid_protocol"

    def test_is_exception_subclass(self) -> None:
        """Given FetchError, when checked, then is Exception subclass."""
        error = FetchError("Test", category="network_error")
        assert isinstance(error, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        """Given FetchError raised, when caught, then attributes accessible."""
        with pytest.raises(FetchError) as exc_info:
            raise FetchError("Timeout occurred", category="timeout")

        assert exc_info.value.category == "timeout"
        assert str(exc_info.value) == "Timeout occurred"

    def test_repr_includes_category_and_message(self) -> None:
        """Given FetchError, when repr called, then includes category and message."""
        error = FetchError("Test error", category="not_found")
        repr_str = repr(error)
        assert "not_found" in repr_str
        assert "Test error" in repr_str

    def test_all_error_categories_accepted(self) -> None:
        """Given all valid error categories, when constructed, then no type errors."""
        categories = [
            "invalid_protocol",
            "size_limit_exceeded",
            "timeout",
            "not_found",
            "network_error",
        ]
        for category in categories:
            error = FetchError(f"Test {category}", category=category)  # type: ignore[arg-type]
            assert error.category == category


class TestWebFetcherURL:
    """Tests for WebFetcher URL fetching."""

    def test_fetch_https_url_success(self) -> None:
        """Given valid HTTPS URL, when fetch called, then content returned as bytes."""
        # Spec AC: "Given a valid HTTPS URL, when fetch is called, then content is returned as bytes"
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/paper.xml",
            discovered_via="api",
        )

        # Mock requests.get to return test content
        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Length": "100"}
            mock_response.iter_content = lambda chunk_size: [b"test content"]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            content = fetcher.fetch(source)

            assert content == b"test content"
            assert isinstance(content, bytes)
            mock_get.assert_called_once()

    def test_fetch_http_url_allowed(self) -> None:
        """Given valid HTTP URL, when fetch called, then content returned."""
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="http://example.com/paper.xml",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.iter_content = lambda chunk_size: [b"http content"]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            content = fetcher.fetch(source)
            assert content == b"http content"

    def test_invalid_protocol_file(self) -> None:
        """Given URL with protocol file://, when fetch called, then raise FetchError."""
        # Spec AC: "Given a URL with protocol file://, when fetch is called,
        # then raise FetchError with category 'invalid_protocol'"
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="file:///home/user/paper.pdf",
            discovered_via="local",
        )

        with pytest.raises(FetchError) as exc_info:
            fetcher.fetch(source)

        assert exc_info.value.category == "invalid_protocol"
        assert "file://" in str(exc_info.value)

    def test_invalid_protocol_ftp(self) -> None:
        """Given URL with protocol ftp://, when fetch called, then raise FetchError."""
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="ftp://example.com/paper.pdf",
            discovered_via="api",
        )

        with pytest.raises(FetchError) as exc_info:
            fetcher.fetch(source)

        assert exc_info.value.category == "invalid_protocol"
        assert "ftp://" in str(exc_info.value)

    def test_size_limit_exceeded_from_header(self) -> None:
        """Given response with Content-Length > 50MB, when fetch called, then raise FetchError."""
        # Spec AC: "Given a response larger than 50MB, when fetch is called,
        # then raise FetchError with category 'size_limit_exceeded'"
        fetcher = WebFetcher(max_size_bytes=1000)
        source = SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="https://example.com/large.pdf",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Length": "2000"}
            mock_get.return_value = mock_response

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch(source)

            assert exc_info.value.category == "size_limit_exceeded"
            assert "2000" in str(exc_info.value)

    def test_size_limit_exceeded_during_download(self) -> None:
        """Given response that exceeds size limit during download, when fetch called, then raise FetchError."""
        fetcher = WebFetcher(max_size_bytes=100)
        source = SourceCandidate(
            quality_tier=4,
            format="pdf",
            url="https://example.com/large.pdf",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {}  # No Content-Length header
            # Simulate chunks that exceed limit
            mock_response.iter_content = lambda chunk_size: [b"x" * 60, b"x" * 60]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch(source)

            assert exc_info.value.category == "size_limit_exceeded"

    def test_timeout_error(self) -> None:
        """Given request that times out, when fetch called, then raise FetchError."""
        # Spec AC: "Given a request that times out after 60 seconds, when fetch is called,
        # then raise FetchError with category 'timeout'"
        fetcher = WebFetcher(timeout_seconds=5)
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/slow.xml",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Request timed out")

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch(source)

            assert exc_info.value.category == "timeout"
            assert "5 seconds" in str(exc_info.value)

    def test_404_not_found(self) -> None:
        """Given 404 response, when fetch called, then raise FetchError."""
        # Spec AC: "Given a 404 response, when fetch is called,
        # then raise FetchError with category 'not_found'"
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/missing.xml",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch(source)

            assert exc_info.value.category == "not_found"

    def test_network_error(self) -> None:
        """Given network unreachable error, when fetch called, then raise FetchError."""
        # Spec AC: "Given a network unreachable error, when fetch is called,
        # then raise FetchError with category 'network_error'"
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://unreachable.example.com/paper.xml",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Network unreachable")

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch(source)

            assert exc_info.value.category == "network_error"

    def test_http_500_error(self) -> None:
        """Given HTTP 500 error, when fetch called, then raise FetchError."""
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/error.xml",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status = Mock(
                side_effect=requests.HTTPError("500 Server Error")
            )
            mock_get.return_value = mock_response

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch(source)

            assert exc_info.value.category == "network_error"

    def test_custom_timeout_respected(self) -> None:
        """Given custom timeout value, when fetch called, then requests.get receives timeout."""
        fetcher = WebFetcher(timeout_seconds=30)
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/paper.xml",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.iter_content = lambda chunk_size: [b"content"]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            fetcher.fetch(source)

            # Verify timeout was passed to requests.get
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["timeout"] == 30


class TestWebFetcherLocal:
    """Tests for WebFetcher local file fetching."""

    def test_fetch_local_file_success(self) -> None:
        """Given local file path, when fetch called, then file content returned as bytes."""
        # Spec AC: "Given a local file path, when fetch is called,
        # then file content is read and returned as bytes"
        fetcher = WebFetcher()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(b"PDF content here")
            tmp_path = tmp.name

        try:
            source = SourceCandidate(
                quality_tier=4,
                format="pdf",
                local_path=tmp_path,
                discovered_via="local_file",
            )

            content = fetcher.fetch(source)

            assert content == b"PDF content here"
            assert isinstance(content, bytes)
        finally:
            Path(tmp_path).unlink()

    def test_local_file_not_found(self) -> None:
        """Given non-existent local file, when fetch called, then raise FetchError."""
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=4,
            format="pdf",
            local_path="/nonexistent/path/to/paper.pdf",
            discovered_via="local_file",
        )

        with pytest.raises(FetchError) as exc_info:
            fetcher.fetch(source)

        assert exc_info.value.category == "not_found"

    def test_local_file_size_limit_exceeded(self) -> None:
        """Given local file exceeding size limit, when fetch called, then raise FetchError."""
        fetcher = WebFetcher(max_size_bytes=10)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(b"x" * 100)  # 100 bytes > 10 byte limit
            tmp_path = tmp.name

        try:
            source = SourceCandidate(
                quality_tier=4,
                format="pdf",
                local_path=tmp_path,
                discovered_via="local_file",
            )

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch(source)

            assert exc_info.value.category == "size_limit_exceeded"
            assert "100" in str(exc_info.value)
        finally:
            Path(tmp_path).unlink()

    def test_source_without_url_or_path_raises_error(self) -> None:
        """Given SourceCandidate with neither URL nor path, when fetch called, then raise ValueError."""
        fetcher = WebFetcher()

        # Create a source with both None (bypassing __post_init__ validation)
        # This shouldn't happen in practice, but tests defensive coding
        source = SourceCandidate.__new__(SourceCandidate)
        source.url = None
        source.local_path = None
        source.quality_tier = 4
        source.format = "pdf"
        source.discovered_via = "unknown"

        with pytest.raises(ValueError, match="must have either url or local_path"):
            fetcher.fetch(source)

    def test_large_file_chunks_properly(self) -> None:
        """Given large local file, when fetch called, then reads correctly."""
        fetcher = WebFetcher(max_size_bytes=100 * 1024)  # 100KB limit

        # Create a 50KB file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = b"x" * (50 * 1024)
            tmp.write(content)
            tmp_path = tmp.name

        try:
            source = SourceCandidate(
                quality_tier=4,
                format="pdf",
                local_path=tmp_path,
                discovered_via="local_file",
            )

            result = fetcher.fetch(source)

            assert result == content
            assert len(result) == 50 * 1024
        finally:
            Path(tmp_path).unlink()


class TestWebFetcherConfiguration:
    """Tests for WebFetcher configuration and defaults."""

    def test_default_max_size_50mb(self) -> None:
        """Given WebFetcher with defaults, when checked, then max_size is 50MB."""
        fetcher = WebFetcher()
        assert fetcher.max_size_bytes == 50 * 1024 * 1024

    def test_default_timeout_60_seconds(self) -> None:
        """Given WebFetcher with defaults, when checked, then timeout is 60 seconds."""
        fetcher = WebFetcher()
        assert fetcher.timeout_seconds == 60

    def test_custom_configuration(self) -> None:
        """Given custom max_size and timeout, when WebFetcher created, then uses custom values."""
        fetcher = WebFetcher(max_size_bytes=10 * 1024 * 1024, timeout_seconds=30)
        assert fetcher.max_size_bytes == 10 * 1024 * 1024
        assert fetcher.timeout_seconds == 30

    def test_follows_redirects(self) -> None:
        """Given URL that redirects, when fetch called, then follows redirect."""
        fetcher = WebFetcher()
        source = SourceCandidate(
            quality_tier=1,
            format="jats_xml",
            url="https://example.com/redirect",
            discovered_via="api",
        )

        with patch("src.doc_ingest.web_fetcher.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.iter_content = lambda chunk_size: [b"redirected content"]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            fetcher.fetch(source)

            # Verify allow_redirects=True was passed
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["allow_redirects"] is True

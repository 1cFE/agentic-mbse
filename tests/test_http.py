"""Tests for agentic_mbse.extraction.http — shared HTTP utilities."""

from unittest.mock import MagicMock, patch

from agentic_mbse.extraction.http import (
    DEFAULT_TIMEOUT,
    HEAD_TIMEOUT,
    USER_AGENT,
    FetchResult,
    fetch_url,
    head_content_type,
)

# ---------------------------------------------------------------------------
# FetchResult
# ---------------------------------------------------------------------------


def test_fetch_result_text_decodes_utf8():
    fr = FetchResult(content=b"hello", final_url="https://x.com", content_type="text/html")
    assert fr.text() == "hello"


def test_fetch_result_text_uses_encoding():
    fr = FetchResult(
        content="café".encode("latin-1"),
        final_url="https://x.com",
        content_type="text/html",
        encoding="latin-1",
    )
    assert fr.text() == "café"


def test_fetch_result_text_defaults_to_utf8():
    fr = FetchResult(
        content="日本語".encode(),
        final_url="https://x.com",
        content_type="text/html",
        encoding=None,
    )
    assert fr.text() == "日本語"


# ---------------------------------------------------------------------------
# fetch_url
# ---------------------------------------------------------------------------


def _mock_response(
    content=b"<html>ok</html>",
    url="https://example.com/final",
    content_type="text/html",
    charset="utf-8",
):
    resp = MagicMock()
    resp.read.return_value = content
    resp.url = url
    resp.headers.get_content_type.return_value = content_type
    resp.headers.get_content_charset.return_value = charset
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_fetch_url_returns_fetch_result():
    mock_resp = _mock_response()
    with patch("agentic_mbse.extraction.http.urllib.request.urlopen", return_value=mock_resp):
        result = fetch_url("https://example.com")
        assert isinstance(result, FetchResult)
        assert result.content == b"<html>ok</html>"
        assert result.final_url == "https://example.com/final"
        assert result.content_type == "text/html"
        assert result.encoding == "utf-8"


def test_fetch_url_sets_user_agent():
    mock_resp = _mock_response()
    with patch(
        "agentic_mbse.extraction.http.urllib.request.urlopen", return_value=mock_resp
    ) as mock_open:
        fetch_url("https://example.com")
        req = mock_open.call_args[0][0]
        assert req.get_header("User-agent") == USER_AGENT


def test_fetch_url_uses_timeout():
    mock_resp = _mock_response()
    with patch(
        "agentic_mbse.extraction.http.urllib.request.urlopen", return_value=mock_resp
    ) as mock_open:
        fetch_url("https://example.com", timeout=42)
        assert mock_open.call_args[1]["timeout"] == 42


def test_fetch_url_propagates_exception():
    with patch(
        "agentic_mbse.extraction.http.urllib.request.urlopen",
        side_effect=Exception("connection refused"),
    ):
        try:
            fetch_url("https://example.com")
            assert False, "Should have raised"
        except Exception as exc:
            assert "connection refused" in str(exc)


# ---------------------------------------------------------------------------
# head_content_type
# ---------------------------------------------------------------------------


def test_head_content_type_returns_type():
    mock_resp = MagicMock()
    mock_resp.headers.get_content_type.return_value = "application/pdf"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("agentic_mbse.extraction.http.urllib.request.urlopen", return_value=mock_resp):
        assert head_content_type("https://example.com/file.pdf") == "application/pdf"


def test_head_content_type_returns_none_on_failure():
    with patch(
        "agentic_mbse.extraction.http.urllib.request.urlopen", side_effect=Exception("fail")
    ):
        assert head_content_type("https://example.com") is None


def test_head_content_type_sends_head_method():
    mock_resp = MagicMock()
    mock_resp.headers.get_content_type.return_value = "text/html"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch(
        "agentic_mbse.extraction.http.urllib.request.urlopen", return_value=mock_resp
    ) as mock_open:
        head_content_type("https://example.com")
        req = mock_open.call_args[0][0]
        assert req.get_method() == "HEAD"


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_constants_are_sensible():
    assert DEFAULT_TIMEOUT == 30
    assert HEAD_TIMEOUT == 5
    assert "agentic-mbse" in USER_AGENT

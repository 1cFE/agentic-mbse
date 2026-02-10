"""Web fetcher for document sources (spec 005)."""

from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import requests

from src.doc_ingest.types import SourceCandidate

# Fetch error categories
FetchErrorCategory = Literal[
    "invalid_protocol",
    "size_limit_exceeded",
    "timeout",
    "not_found",
    "network_error",
]


class FetchError(Exception):
    """Typed exception for fetch failures with structured error categories.

    Raised by WebFetcher to signal fetch failures with explicit categorization,
    enabling proper error handling and logging without string parsing.

    Spec 005: FetchError provides typed failure categories for network errors,
    protocol validation, size limits, and timeouts.

    Attributes:
        category: The failure category (e.g., "timeout", "size_limit_exceeded")

    Examples:
        >>> raise FetchError(
        ...     "URL protocol 'file://' not allowed",
        ...     category="invalid_protocol"
        ... )
        >>> try:
        ...     fetch_content()
        ... except requests.Timeout:
        ...     raise FetchError("Request timed out", category="timeout")
    """

    def __init__(self, message: str, category: FetchErrorCategory) -> None:
        """Initialize FetchError with message and category.

        Args:
            message: Human-readable error message for logging
            category: Typed failure category from FetchErrorCategory literal
        """
        super().__init__(message)
        self.category = category

    def __repr__(self) -> str:
        """Return detailed representation including category."""
        return f"FetchError(category={self.category!r}, message={str(self)!r})"


class WebFetcher:
    """Fetch content from remote URLs or local file paths.

    Provides content fetching with protocol validation, size limits, timeouts,
    and typed error handling. Supports both HTTP(S) URLs and local file paths.

    Spec 005: WebFetcher enforces security and resource constraints:
    - Protocol allowlist (http, https only)
    - Maximum content size (default 50MB)
    - Request timeouts (default 60 seconds)
    - Typed error categorization via FetchError

    Attributes:
        max_size_bytes: Maximum allowed content size in bytes (default 50MB)
        timeout_seconds: Request timeout in seconds (default 60)
    """

    def __init__(self, max_size_bytes: int = 50 * 1024 * 1024, timeout_seconds: int = 60) -> None:
        """Initialize WebFetcher with size and timeout limits.

        Args:
            max_size_bytes: Maximum content size in bytes (default 50MB)
            timeout_seconds: Request timeout in seconds (default 60)
        """
        self.max_size_bytes = max_size_bytes
        self.timeout_seconds = timeout_seconds

    def fetch(self, source: SourceCandidate) -> bytes:
        """Fetch content from URL or local path.

        Fetches content from the source's URL or local_path, applying protocol
        validation, size limits, and timeout constraints. Returns raw bytes for
        downstream validation and conversion.

        Args:
            source: The source candidate with URL or local_path

        Returns:
            Raw content bytes

        Raises:
            FetchError: On protocol validation failure, size limit exceeded,
                       timeout, HTTP errors, or network failures
            ValueError: If source has neither URL nor local_path

        Examples:
            >>> fetcher = WebFetcher()
            >>> source = SourceCandidate(
            ...     quality_tier=1,
            ...     format="jats_xml",
            ...     url="https://example.com/paper.xml",
            ...     discovered_via="api"
            ... )
            >>> content = fetcher.fetch(source)
        """
        if source.url is not None:
            return self._fetch_url(source.url)
        elif source.local_path is not None:
            return self._fetch_local(source.local_path)
        else:
            raise ValueError("SourceCandidate must have either url or local_path")

    def _fetch_url(self, url: str) -> bytes:
        """Fetch content from HTTP(S) URL.

        Validates URL protocol, fetches content with timeout, and enforces size limits.

        Args:
            url: The URL to fetch

        Returns:
            Raw content bytes

        Raises:
            FetchError: On protocol validation failure, size limit exceeded,
                       timeout, HTTP errors, or network failures
        """
        # Validate protocol
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise FetchError(
                f"URL protocol '{parsed.scheme}://' not allowed. Only http and https are supported.",
                category="invalid_protocol",
            )

        try:
            # Stream the response to check size before downloading
            response = requests.get(
                url, timeout=self.timeout_seconds, stream=True, allow_redirects=True
            )

            # Check HTTP status
            if response.status_code == 404:
                raise FetchError(f"URL not found: {url}", category="not_found")
            response.raise_for_status()

            # Check content length header if available
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > self.max_size_bytes:
                raise FetchError(
                    f"Content size {content_length} bytes exceeds limit of {self.max_size_bytes} bytes",
                    category="size_limit_exceeded",
                )

            # Read content with size limit enforcement
            content = bytearray()
            for chunk in response.iter_content(chunk_size=8192):
                content.extend(chunk)
                if len(content) > self.max_size_bytes:
                    raise FetchError(
                        f"Content size exceeds limit of {self.max_size_bytes} bytes",
                        category="size_limit_exceeded",
                    )

            return bytes(content)

        except requests.Timeout as e:
            raise FetchError(
                f"Request timed out after {self.timeout_seconds} seconds: {url}",
                category="timeout",
            ) from e
        except requests.ConnectionError as e:
            raise FetchError(
                f"Network error while fetching {url}: {e}", category="network_error"
            ) from e
        except requests.RequestException as e:
            # Catch other requests exceptions (excluding FetchError we already raised)
            if isinstance(e, FetchError):
                raise
            raise FetchError(
                f"HTTP error while fetching {url}: {e}", category="network_error"
            ) from e

    def _fetch_local(self, path: str) -> bytes:
        """Fetch content from local file system.

        Reads file content with size limit enforcement.

        Args:
            path: The local file path

        Returns:
            Raw content bytes

        Raises:
            FetchError: On file not found, size limit exceeded, or read errors
        """
        try:
            # Check file exists and get size
            file_path = Path(path)
            if not file_path.exists():
                raise FetchError(f"Local file not found: {path}", category="not_found")

            file_size = file_path.stat().st_size
            if file_size > self.max_size_bytes:
                raise FetchError(
                    f"File size {file_size} bytes exceeds limit of {self.max_size_bytes} bytes",
                    category="size_limit_exceeded",
                )

            # Read file content
            return file_path.read_bytes()

        except OSError as e:
            if isinstance(e, FileNotFoundError):
                raise FetchError(f"Local file not found: {path}", category="not_found") from e
            raise FetchError(
                f"Error reading local file {path}: {e}", category="network_error"
            ) from e

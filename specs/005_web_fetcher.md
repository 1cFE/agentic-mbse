
## Purpose
Fetch content from remote URLs or local file paths, with validation of protocol, size limits, timeouts, and error handling for network failures.

## Requirements
- Fetch content from HTTPS and HTTP URLs
- Read content from local file system paths
- Enforce maximum content size limit (e.g., 50MB) to prevent disk exhaustion
- Apply request timeouts to prevent hanging
- Validate URL protocol (allowlist: http, https; reject file://, ftp://, etc.)
- Return raw bytes for downstream validation and conversion
- Raise typed exceptions for network errors, size limits, timeouts

## Acceptance Criteria
- **Given** a valid HTTPS URL, **when** fetch is called, **then** content is returned as bytes
- **Given** a local file path, **when** fetch is called, **then** file content is read and returned as bytes
- **Given** a URL with protocol `file://`, **when** fetch is called, **then** raise `FetchError` with category "invalid_protocol"
- **Given** a response larger than 50MB, **when** fetch is called, **then** raise `FetchError` with category "size_limit_exceeded"
- **Given** a request that times out after 60 seconds, **when** fetch is called, **then** raise `FetchError` with category "timeout"
- **Given** a 404 response, **when** fetch is called, **then** raise `FetchError` with category "not_found"
- **Given** a network unreachable error, **when** fetch is called, **then** raise `FetchError` with category "network_error"

## Interfaces
**API:**
```python
class FetchError(Exception):
    def __init__(self, message: str, category: str):
        self.category = category  # "invalid_protocol" | "size_limit_exceeded" | "timeout" | "not_found" | "network_error"

class WebFetcher:
    def fetch(self, source: SourceCandidate) -> bytes:
        """Fetch content from URL or local path. Raises FetchError on failure."""


"""Shared YAML frontmatter builder for extraction output markdown.

All extraction pipelines (web, PDF, DOCX) use this module to produce
consistent provenance metadata in output.md files.
"""

from __future__ import annotations

from datetime import datetime, timezone

from agentic_mbse.extraction.base import compute_source_hash  # noqa: F401


def _sanitize_yaml_value(value: str) -> str:
    """Escape a string for use as a double-quoted YAML value."""
    value = value.replace("\r", "").replace("\n", " ")
    value = " ".join(value.split())  # collapse runs of whitespace
    value = value.replace('"', "'")
    return value


def build_frontmatter(
    *,
    source: str,
    source_type: str,
    backend: str,
    content_hash: str,
    title: str | None = None,
    author: str | None = None,
) -> str:
    """Build a YAML frontmatter block for extraction output.

    Args:
        source: Source identifier — URL (after redirects) or local filename.
        source_type: ``"url"`` or ``"local_file"``.
        backend: Extraction backend that produced the output.
        content_hash: SHA-256 hex digest of the original source bytes.
        title: Page/document title (optional, web-only).
        author: Author name (optional, web-only).

    Returns:
        A complete ``---`` delimited YAML frontmatter string.
    """
    now = datetime.now(timezone.utc).isoformat()

    lines = ["---"]
    lines.append(f'source: "{_sanitize_yaml_value(source)}"')
    lines.append(f'source_type: "{_sanitize_yaml_value(source_type)}"')
    lines.append(f'extracted_at: "{now}"')
    lines.append(f'content_hash_sha256: "{content_hash}"')
    lines.append(f'backend: "{_sanitize_yaml_value(backend)}"')
    if title:
        lines.append(f'title: "{_sanitize_yaml_value(title)}"')
    if author:
        lines.append(f'author: "{_sanitize_yaml_value(author)}"')
    lines.append("---")
    return "\n".join(lines)

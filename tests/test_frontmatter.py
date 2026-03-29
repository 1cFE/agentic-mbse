"""Tests for agentic_mbse.extraction.frontmatter — shared frontmatter builder."""

import hashlib

from agentic_mbse.extraction.frontmatter import (
    _sanitize_yaml_value,
    build_frontmatter,
    compute_source_hash,
)

# ---------------------------------------------------------------------------
# build_frontmatter
# ---------------------------------------------------------------------------


def test_build_frontmatter_has_all_required_fields():
    fm = build_frontmatter(
        source="paper.pdf",
        source_type="local_file",
        backend="pdf_pipeline",
        content_hash="abc123",
    )
    assert fm.startswith("---")
    assert fm.endswith("---")
    assert "source:" in fm
    assert "source_type:" in fm
    assert "extracted_at:" in fm
    assert "content_hash_sha256:" in fm
    assert "backend:" in fm


def test_build_frontmatter_omits_none_optional_fields():
    fm = build_frontmatter(
        source="x",
        source_type="url",
        backend="b",
        content_hash="h",
    )
    assert "title:" not in fm
    assert "author:" not in fm


def test_build_frontmatter_includes_optional_fields():
    fm = build_frontmatter(
        source="x",
        source_type="url",
        backend="b",
        content_hash="h",
        title="My Title",
        author="Jane Doe",
    )
    assert "title:" in fm
    assert "author:" in fm


def test_build_frontmatter_omits_empty_string_title():
    """Empty string title should be treated as absent (falsy check)."""
    fm = build_frontmatter(
        source="x",
        source_type="url",
        backend="b",
        content_hash="h",
        title="",
        author="",
    )
    assert "title:" not in fm
    assert "author:" not in fm


def test_build_frontmatter_field_order():
    """Fields should appear in the spec-defined order."""
    fm = build_frontmatter(
        source="https://example.com",
        source_type="url",
        backend="trafilatura",
        content_hash="deadbeef",
        title="T",
        author="A",
    )
    lines = fm.strip().split("\n")
    # First and last are ---
    assert lines[0] == "---"
    assert lines[-1] == "---"
    # Check order of field keys (between the --- delimiters)
    field_keys = [line.split(":")[0] for line in lines[1:-1]]
    assert field_keys == [
        "source",
        "source_type",
        "extracted_at",
        "content_hash_sha256",
        "backend",
        "title",
        "author",
    ]


def test_build_frontmatter_extracted_at_is_iso8601():
    fm = build_frontmatter(
        source="x",
        source_type="url",
        backend="b",
        content_hash="h",
    )
    # Find the extracted_at line and verify it contains a timezone-aware ISO timestamp
    for line in fm.split("\n"):
        if line.startswith("extracted_at:"):
            # Should contain UTC offset (+00:00) or Z
            value = line.split(": ", 1)[1].strip('"')
            assert "+" in value or "Z" in value
            break
    else:
        raise AssertionError("extracted_at field not found")


# ---------------------------------------------------------------------------
# _sanitize_yaml_value
# ---------------------------------------------------------------------------


def test_sanitize_yaml_value_strips_newlines():
    assert "\n" not in _sanitize_yaml_value("line1\nline2\rline3")


def test_sanitize_yaml_value_escapes_quotes():
    assert '"' not in _sanitize_yaml_value('He said "hello"')


def test_sanitize_yaml_value_collapses_whitespace():
    assert "  " not in _sanitize_yaml_value("too   many   spaces")


def test_sanitize_yaml_value_handles_empty_string():
    assert _sanitize_yaml_value("") == ""


# ---------------------------------------------------------------------------
# compute_source_hash
# ---------------------------------------------------------------------------


def test_compute_source_hash_bytes():
    h = compute_source_hash(b"hello")
    assert h == hashlib.sha256(b"hello").hexdigest()


def test_compute_source_hash_path(tmp_path):
    f = tmp_path / "test.bin"
    f.write_bytes(b"hello")
    assert compute_source_hash(f) == hashlib.sha256(b"hello").hexdigest()


def test_compute_source_hash_path_matches_bytes(tmp_path):
    """Chunked path hashing and direct bytes hashing produce the same result."""
    data = b"x" * 200_000  # larger than chunk size (64 KiB)
    f = tmp_path / "large.bin"
    f.write_bytes(data)
    assert compute_source_hash(f) == compute_source_hash(data)


def test_compute_source_hash_empty_bytes():
    assert compute_source_hash(b"") == hashlib.sha256(b"").hexdigest()

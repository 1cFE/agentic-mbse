"""Source kinds, the keyed kind's refusals, slugs and URL normalization."""

from pathlib import Path

import pytest

from agentic_mbse.research import KeyedFileSource, LocalPdfSource, UrlSource
from agentic_mbse.research.sources import normalize_url, slugify

KEYED = dict(
    path=Path("inbox/paper.pdf"),
    kind="catalog",
    key_field="catalog_key",
    key="ABC123",
    key_label="Catalog Key",
    key_display="lib:ABC123",
)


def test_a_keyed_source_names_its_kind_key_field_and_suffix():
    source = KeyedFileSource(**KEYED)
    assert source.identity == "catalog:ABC123"
    assert source.row_extras == {"catalog_key": "ABC123"}
    assert source.slug_suffix == "ABC123"
    assert source.staged_input == Path("inbox/paper.pdf")
    assert source.index_profile == "batch"


@pytest.mark.parametrize("kind", ["url", "local_pdf", "", "  "])
def test_a_keyed_source_must_name_its_own_kind(kind):
    with pytest.raises(ValueError, match="kind"):
        KeyedFileSource(**KEYED | {"kind": kind})


@pytest.mark.parametrize(
    "key_field",
    [
        "source_id",
        "source_kind",
        "slug",
        "title",
        "source_url",
        "origin_path",
        "raw_sha256",
        "raw_artifact_sha256",
        "extract_sha256",
        "date_extracted",
        "",
    ],
)
def test_a_keyed_source_cannot_overwrite_a_registry_field(key_field):
    with pytest.raises(ValueError, match="key field"):
        KeyedFileSource(**KEYED | {"key_field": key_field})


@pytest.mark.parametrize("key", ["", "a/b", "..", "AB-12", "a b", "café"])
def test_a_key_must_be_one_slug_segment(key):
    with pytest.raises(ValueError, match="key must match"):
        KeyedFileSource(**KEYED | {"key": key})


def test_url_and_local_pdf_sources_use_the_seam_profile():
    url = UrlSource(url="https://example.org/a")
    pdf = LocalPdfSource(path=Path("inbox/a.pdf"))
    assert (url.kind, url.identity, url.row_extras, url.staged_input, url.slug_suffix) == (
        "url",
        "https://example.org/a",
        {"source_url": "https://example.org/a"},
        None,
        None,
    )
    assert (pdf.kind, pdf.identity, pdf.row_extras, pdf.staged_input, pdf.slug_suffix) == (
        "local_pdf",
        "inbox/a.pdf",
        {"origin_path": "inbox/a.pdf"},
        Path("inbox/a.pdf"),
        None,
    )
    assert url.index_profile == pdf.index_profile == "seam"


@pytest.mark.parametrize(
    ("title", "slug"),
    [
        ("Widget Coil Note", "widget_coil_note"),
        ("  --Hello,  World!! ", "hello_world"),
        ("Câble Note (2026)", "c_ble_note_2026"),
        ("a" * 70, "a" * 60),
        ("word " * 20, ("word_" * 12).rstrip("_")),
    ],
)
def test_slugify(title, slug):
    assert slugify(title) == slug


@pytest.mark.parametrize(
    ("url", "normalized"),
    [
        ("HTTP://Example.ORG/a/./b/../c#frag", "http://example.org/a/c"),
        ("https://example.org/a?q=1#x", "https://example.org/a?q=1"),
        ("https://example.org", "https://example.org"),
    ],
)
def test_normalize_url(url, normalized):
    assert normalize_url(url) == normalized

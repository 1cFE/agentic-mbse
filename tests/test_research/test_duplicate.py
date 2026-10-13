"""Dedupe before the fetch, on the URL, and after it, on the bytes as fetched."""

from dataclasses import replace

from agentic_mbse.research import SourceMetadata, UrlSource, load_manifest_rows, register

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises dedupe.",
    validation="Compare against the fixture page itself.",
    caveat="A test fixture.",
)


def _register(tree, url, title=None):
    metadata = METADATA if title is None else replace(METADATA, title=title)
    return register(UrlSource(url=url), metadata, paths=tree.paths)


def _row_count(tree) -> int:
    return len(load_manifest_rows(tree.paths))


def test_same_url_twice_is_a_duplicate(local_site, knowledge_tree):
    first = _register(knowledge_tree, local_site.url("utf8.html"))
    second = _register(knowledge_tree, local_site.url("utf8.html"))

    assert first.outcome == "registered"
    assert second.outcome == "duplicate"
    assert second.reason == f"already registered as {first.slug}"
    assert second.existing_slug == first.slug
    assert second.existing_path == first.location
    assert _row_count(knowledge_tree) == 1
    assert knowledge_tree.index.read_text().count("### Widget Coil Note") == 1


def test_url_dedupe_ignores_scheme_host_case_and_fragment(local_site, knowledge_tree):
    """The path stays case-significant, because servers treat it that way."""
    original = local_site.url("utf8.html")
    variant = "HTTP://" + original.split("://", 1)[1] + "#section-2"

    _register(knowledge_tree, original)
    again = _register(knowledge_tree, variant)
    assert again.outcome == "duplicate", again.reason
    assert _row_count(knowledge_tree) == 1


def test_same_bytes_at_a_different_url_is_a_duplicate(local_site, knowledge_tree):
    """The pre-fetch URL check cannot see this; the post-capture source-id check can.

    URL normalization keeps the query, and the fixture server ignores it, so the
    alias serves the same bytes under a URL no row matches.
    """
    first = _register(knowledge_tree, local_site.url("utf8.html"))
    second = _register(knowledge_tree, local_site.url("utf8.html?alias=1"), title="Alias Note")

    assert second.outcome == "duplicate"
    assert second.reason == f"same bytes already registered (source_id {first.source_id})"
    assert second.existing_slug == first.slug
    assert _row_count(knowledge_tree) == 1
    assert "### Alias Note" not in knowledge_tree.index.read_text()


def test_a_duplicate_leaves_staging_empty(local_site, knowledge_tree):
    _register(knowledge_tree, local_site.url("utf8.html"))
    _register(knowledge_tree, local_site.url("utf8.html"))
    assert not list(knowledge_tree.paths.staging.iterdir())


def test_a_different_page_is_not_a_duplicate(local_site, knowledge_tree):
    _register(knowledge_tree, local_site.url("utf8.html"))
    other = _register(knowledge_tree, local_site.url("latin1.html"), title="Cable Note")
    assert other.outcome == "registered"
    assert _row_count(knowledge_tree) == 2

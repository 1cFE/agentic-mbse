"""A URL goes from a loopback page to a registry entry, through the real extractor.

Nothing about capture is stubbed: the extractor runs as a subprocess, offline,
against fixture pages served over HTTP. This proves the two hashes keep their
two jobs (the source id is the digest of the bytes as fetched; the raw-artifact
hash is the digest of the stored copy) on a target built as `init` leaves it.
"""

import hashlib
import json
import re
import sys
import threading
from dataclasses import replace
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from agentic_mbse.research import SourceMetadata, UrlSource, load_manifest_rows, register
from agentic_mbse.research.runs import read_receipts
from tests.test_research.conftest import assert_nothing_written

FRONTMATTER_HASH = re.compile(r'^content_hash_sha256: "([0-9a-f]{64})"', re.MULTILINE)

#: The fields of a URL row, in the order the snapshot wrote them.
URL_ROW_FIELDS = list(
    json.loads((Path(__file__).parent / "golden" / "manifest" / "url.jsonl").read_text())
)

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises the URL capture chain.",
    validation="Compare the quoted dimensions against the fixture page itself.",
    caveat="A test fixture. It states nothing about any real machine.",
)


def _only_row(tree) -> dict:
    rows = load_manifest_rows(tree.paths)
    assert len(rows) == 1, rows
    return rows[0]


def _block_for(tree, title: str) -> str:
    body = tree.index.read_text()
    return body.split(f"### {title}", 1)[1].split("\n## ", 1)[0]


def _register(local_site, tree, page="utf8.html", metadata=METADATA, **kwargs):
    return register(UrlSource(url=local_site.url(page)), metadata, paths=tree.paths, **kwargs)


def test_utf8_page_registers_with_full_provenance(local_site, knowledge_tree):
    result = _register(local_site, knowledge_tree)
    assert result.outcome == "registered", result.reason

    row = _only_row(knowledge_tree)
    frontmatter_hash = FRONTMATTER_HASH.search((result.path / "output.md").read_text()).group(1)

    assert list(row) == URL_ROW_FIELDS  # no origin path, no key field
    assert row["source_kind"] == "url"
    assert row["source_id"] == row["raw_sha256"] == frontmatter_hash
    assert (
        row["raw_artifact_sha256"]
        == hashlib.sha256((result.path / "raw.html").read_bytes()).hexdigest()
    )
    assert (
        row["extract_sha256"]
        == hashlib.sha256((result.path / "output.md").read_bytes()).hexdigest()
    )
    assert row["source_url"] == local_site.url("utf8.html")
    assert row["slug"] == result.slug and row["title"] == METADATA.title


def test_registered_source_id_is_the_digest_of_the_bytes_as_fetched(local_site, knowledge_tree):
    result = _register(local_site, knowledge_tree)
    served = hashlib.sha256(local_site.fetched_bytes("utf8.html")).hexdigest()
    assert result.source_id == served


def test_latin1_page_registers_and_the_two_hashes_differ(local_site, knowledge_tree):
    """The stored `raw.html` is re-encoded, so identity and integrity part ways."""
    result = _register(local_site, knowledge_tree, page="latin1.html")
    assert result.outcome == "registered", result.reason

    row = _only_row(knowledge_tree)
    served = hashlib.sha256(local_site.fetched_bytes("latin1.html")).hexdigest()
    stored = hashlib.sha256((result.path / "raw.html").read_bytes()).hexdigest()

    assert row["raw_sha256"] == served
    assert row["raw_artifact_sha256"] == stored
    assert row["raw_sha256"] != row["raw_artifact_sha256"]


def test_index_block_carries_every_required_field(local_site, knowledge_tree):
    result = _register(local_site, knowledge_tree)
    block = _block_for(knowledge_tree, METADATA.title)
    for field, value in [
        ("Use for", METADATA.use_for),
        ("Validation", METADATA.validation),
        ("Caveat", METADATA.caveat),
        ("Source URL", local_site.url("utf8.html")),
        ("Source ID", result.source_id),
        ("Raw SHA256", result.raw_sha256),
        ("Raw Artifact SHA256", result.raw_artifact_sha256),
        ("Extract SHA256", result.extract_sha256),
    ]:
        assert f"- **{field}**: {value}" in block


def test_the_block_lands_before_the_shipped_index_anchor(local_site, knowledge_tree):
    _register(local_site, knowledge_tree)
    body = knowledge_tree.index.read_text()
    assert body.index(f"### {METADATA.title}") < body.index("## How This File Is Used")


def test_location_resolves_on_disk(local_site, knowledge_tree):
    """The entry names a path a later reader can open."""
    result = _register(local_site, knowledge_tree)
    block = _block_for(knowledge_tree, METADATA.title)
    assert f"- **Location**: {result.location}" in block
    assert result.location == f"knowledge/sources/{result.slug}/"
    assert (result.path / "output.md").is_file()


def test_staging_is_empty_after_a_successful_registration(local_site, knowledge_tree):
    _register(local_site, knowledge_tree)
    assert not list(knowledge_tree.paths.staging.iterdir())


def test_registration_writes_exactly_one_block_and_one_row(local_site, knowledge_tree):
    _register(local_site, knowledge_tree)
    assert knowledge_tree.index.read_text().count(f"### {METADATA.title}") == 1
    assert len(knowledge_tree.manifest.read_text().strip().splitlines()) == 1


@pytest.mark.parametrize("field", ["title", "use_for", "validation", "caveat"])
def test_missing_caller_metadata_is_a_precondition_failure(local_site, knowledge_tree, field):
    """A missing title is refused, never guessed from the URL or the page."""
    result = _register(local_site, knowledge_tree, metadata=replace(METADATA, **{field: "  "}))
    assert result.outcome == "precondition_failed"
    assert result.reason == f"caller must supply non-empty {field}"
    assert_nothing_written(knowledge_tree)


def test_slug_collision_gets_a_numeric_suffix(local_site, knowledge_tree):
    (knowledge_tree.paths.sources / "widget_coil_note").mkdir()
    result = _register(local_site, knowledge_tree)
    assert result.slug == "widget_coil_note_2"


def test_unreachable_url_is_a_capture_failure_leaving_nothing(knowledge_tree):
    result = register(
        UrlSource(url="http://127.0.0.1:1/nothing.html"), METADATA, paths=knowledge_tree.paths
    )
    assert result.outcome == "capture_failed"
    assert result.reason
    assert_nothing_written(knowledge_tree)


def test_manifest_and_index_carry_the_same_raw_artifact_hash(local_site, knowledge_tree):
    """One value, digested once, handed to both writers."""
    result = _register(local_site, knowledge_tree, page="latin1.html")
    row = _only_row(knowledge_tree)
    block = _block_for(knowledge_tree, METADATA.title)
    assert f"- **Raw Artifact SHA256**: {row['raw_artifact_sha256']}" in block
    assert result.raw_artifact_sha256 == row["raw_artifact_sha256"]


# --- refusals that spend no capture -------------------------------------------------


def test_without_the_web_extra_a_url_is_refused_before_capture(
    local_site, knowledge_tree, run_dir, monkeypatch
):
    monkeypatch.setitem(sys.modules, "trafilatura", None)  # makes `import trafilatura` fail

    result = _register(local_site, knowledge_tree, run_dir=run_dir)

    assert result.outcome == "precondition_failed"
    assert result.reason.startswith("URL capture needs the web extra:")
    assert "agentic-mbse[web]" in result.reason
    (receipt,) = read_receipts(run_dir)
    assert receipt["captured"] is False
    assert_nothing_written(knowledge_tree)


@pytest.mark.parametrize("field", ["title", "use_for", "validation", "caveat"])
def test_caller_prose_that_opens_a_comment_is_refused_before_capture(
    field, local_site, knowledge_tree, run_dir, no_capture
):
    """Written into the index, `<!--` would hide every later block, and the anchor, from the parser."""
    metadata = replace(METADATA, **{field: getattr(METADATA, field) + " <!-- stray marker"})

    result = _register(local_site, knowledge_tree, metadata=metadata, run_dir=run_dir)

    assert result.outcome == "precondition_failed"
    assert result.reason == f"{field} must not open an HTML comment"
    (receipt,) = read_receipts(run_dir)
    assert receipt["reason"] == result.reason
    assert receipt["captured"] is False
    assert_nothing_written(knowledge_tree)


def test_a_url_that_opens_a_comment_is_refused_before_capture(
    local_site, knowledge_tree, run_dir, no_capture
):
    """The seam block writes the URL as given, so it is checked like the prose."""
    url = local_site.url("utf8.html") + "?note=<!--"

    result = register(UrlSource(url=url), METADATA, paths=knowledge_tree.paths, run_dir=run_dir)

    assert result.outcome == "precondition_failed"
    assert result.reason == "url must not open an HTML comment"
    (receipt,) = read_receipts(run_dir)
    assert receipt["candidate"] == url
    assert receipt["captured"] is False
    assert_nothing_written(knowledge_tree)


def test_a_missing_source_index_is_refused_before_capture(local_site, knowledge_tree, run_dir):
    knowledge_tree.index.unlink()

    result = _register(local_site, knowledge_tree, run_dir=run_dir)

    assert result.outcome == "precondition_failed"
    assert result.reason == f"source index missing: {knowledge_tree.index}"
    (receipt,) = read_receipts(run_dir)
    assert receipt["captured"] is False
    assert not knowledge_tree.index.exists()
    assert not knowledge_tree.manifest.exists()
    assert not list(knowledge_tree.sources.iterdir())
    assert not list(knowledge_tree.paths.staging.iterdir())


# --- a URL that serves a PDF ---------------------------------------------------------
#
# The extractor downloads the document, runs the PDF pipeline, and saves the
# fetched bytes as `raw.pdf` beside the extraction, not `raw.html`.


@pytest.fixture
def local_pdf_site(generated_pdf):
    """Serve the generated fixture PDF over loopback, like `local_site`."""

    class _QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(_QuietHandler, directory=str(generated_pdf.parent)),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/{generated_pdf.name}"
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.slow
def test_a_pdf_url_registers_with_raw_pdf_and_url_provenance(
    local_pdf_site, generated_pdf, knowledge_tree
):
    result = register(UrlSource(url=local_pdf_site), METADATA, paths=knowledge_tree.paths)
    assert result.outcome == "registered", result.reason

    row = _only_row(knowledge_tree)
    assert list(row) == URL_ROW_FIELDS
    assert row["source_kind"] == "url"
    assert row["source_url"] == local_pdf_site

    # The raw artifact is the fetched PDF, stored flattened in the source dir.
    assert (result.path / "raw.pdf").is_file()
    assert not (result.path / "raw.html").exists()
    assert (result.path / "raw.pdf").read_bytes() == generated_pdf.read_bytes()
    assert (
        row["raw_artifact_sha256"]
        == hashlib.sha256((result.path / "raw.pdf").read_bytes()).hexdigest()
    )
    assert (result.path / "output.md").is_file()

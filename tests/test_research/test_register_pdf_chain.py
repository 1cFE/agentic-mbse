"""A local PDF goes from this machine to a registry entry, through the real extractor.

Marked slow where capture runs: the PDF pipeline loads table-detection weights
on every run.
"""

import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

from agentic_mbse.research import LocalPdfSource, SourceMetadata, load_manifest_rows, register
from agentic_mbse.research.runs import read_receipts
from tests.test_research.conftest import assert_nothing_written

FRONTMATTER_HASH = re.compile(r'^content_hash_sha256: "([0-9a-f]{64})"', re.MULTILINE)

#: The fields of a local-PDF row, in the order the snapshot wrote them.
LOCAL_PDF_ROW_FIELDS = list(
    json.loads((Path(__file__).parent / "golden" / "manifest" / "local_pdf.jsonl").read_text())
)

METADATA = SourceMetadata(
    title="Widget Coil Note PDF",
    use_for="Synthetic PDF; exercises the local-PDF capture chain.",
    validation="Compare against the generated fixture PDF itself.",
    caveat="A test fixture. It states nothing about any real machine.",
)


def _only_row(tree) -> dict:
    (row,) = load_manifest_rows(tree.paths)
    return row


@pytest.fixture
def registered_pdf(knowledge_tree, generated_pdf):
    return register(LocalPdfSource(path=generated_pdf), METADATA, paths=knowledge_tree.paths)


@pytest.mark.slow
def test_local_pdf_registers_flattened_with_full_provenance(
    knowledge_tree, generated_pdf, registered_pdf
):
    result = registered_pdf
    assert result.outcome == "registered", result.reason

    row = _only_row(knowledge_tree)
    frontmatter_hash = FRONTMATTER_HASH.search((result.path / "output.md").read_text()).group(1)
    input_hash = hashlib.sha256(generated_pdf.read_bytes()).hexdigest()

    assert list(row) == LOCAL_PDF_ROW_FIELDS  # no source URL, no key field
    assert row["source_kind"] == "local_pdf"
    assert row["source_id"] == row["raw_sha256"] == frontmatter_hash == input_hash

    # Flattened: output.md sits at the top of the source dir, not under a stem dir.
    assert (result.path / "output.md").is_file()
    assert not (result.path / generated_pdf.stem).exists()


@pytest.mark.slow
def test_raw_copy_lands_in_knowledge_raw_only_after_commit(
    knowledge_tree, generated_pdf, registered_pdf
):
    """The extractor saves no raw copy of a local file, so the registry stages one itself."""
    result = registered_pdf
    raw_copy = knowledge_tree.raw / generated_pdf.name
    assert raw_copy.is_file()
    assert raw_copy.read_bytes() == generated_pdf.read_bytes()

    row = _only_row(knowledge_tree)
    assert row["raw_artifact_sha256"] == hashlib.sha256(raw_copy.read_bytes()).hexdigest()
    assert row["origin_path"] == str(generated_pdf)
    assert not (result.path / generated_pdf.name).exists()  # moved out of the source dir
    assert not (result.path / ".rawin").exists()


@pytest.mark.slow
def test_pdf_index_block_uses_origin_path_not_source_url(
    knowledge_tree, generated_pdf, registered_pdf
):
    block = knowledge_tree.index.read_text().split(f"### {METADATA.title}", 1)[1]
    assert f"- **Origin Path**: {generated_pdf}" in block
    assert "- **Source URL**" not in block


@pytest.mark.slow
def test_manifest_and_index_agree_on_the_raw_artifact_hash(knowledge_tree, registered_pdf):
    """The local-PDF path is where two derivations of this hash could read different files."""
    row = _only_row(knowledge_tree)
    block = knowledge_tree.index.read_text().split(f"### {METADATA.title}", 1)[1]
    assert f"- **Raw Artifact SHA256**: {row['raw_artifact_sha256']}" in block
    assert registered_pdf.raw_artifact_sha256 == row["raw_artifact_sha256"]


def test_missing_local_pdf_is_a_precondition_failure(knowledge_tree, tmp_path):
    absent = tmp_path / "absent.pdf"
    result = register(LocalPdfSource(path=absent), METADATA, paths=knowledge_tree.paths)
    assert result.outcome == "precondition_failed"
    assert result.reason == f"input file not found: {absent}"
    assert_nothing_written(knowledge_tree)


def test_an_input_path_that_opens_a_comment_is_refused_before_capture(
    knowledge_tree, generated_pdf, run_dir, no_capture, tmp_path
):
    """The seam block writes the input path as its Origin Path, so it is checked like the prose."""
    odd = tmp_path / "scans <!-- 2026" / generated_pdf.name
    odd.parent.mkdir()
    shutil.copy(generated_pdf, odd)

    result = register(
        LocalPdfSource(path=odd), METADATA, paths=knowledge_tree.paths, run_dir=run_dir
    )

    assert result.outcome == "precondition_failed"
    assert result.reason == "path must not open an HTML comment"
    (receipt,) = read_receipts(run_dir)
    assert receipt["captured"] is False
    assert_nothing_written(knowledge_tree)


def test_a_missing_source_index_is_refused_before_capture(knowledge_tree, generated_pdf, run_dir):
    knowledge_tree.index.unlink()

    result = register(
        LocalPdfSource(path=generated_pdf), METADATA, paths=knowledge_tree.paths, run_dir=run_dir
    )

    assert result.outcome == "precondition_failed"
    assert result.reason.startswith("source index missing:")
    assert not knowledge_tree.index.exists()
    assert not knowledge_tree.manifest.exists()
    assert not knowledge_tree.raw.exists()
    assert not list(knowledge_tree.sources.iterdir())

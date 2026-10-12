"""What a keyed batch caller gets: its index block, and dedupe on its key before any fetch.

The block must stay byte-compatible with the blocks an unattended batch ingest
has always written (`test_golden_shapes.py` pins the bytes). Rows that ingest
wrote before rows carried a `source_kind` must still dedupe a new attempt. Here
the key is a neutral one, to show the caller names it.
"""

import json
import re
import subprocess
from datetime import date
from pathlib import Path

import pytest

from agentic_mbse.research import KeyedFileSource, SourceMetadata, load_manifest_rows, register
from agentic_mbse.research.index import render_batch_block
from agentic_mbse.research.runs import read_receipts

FIELD_RE = re.compile(r"^- \*\*(?P<name>[^*]+)\*\*:", re.MULTILINE)

BATCH = dict(
    title="T",
    slug="t",
    key_label="Catalog Key",
    key_display="lib:ABC",
    source_id="a" * 64,
    extract_sha256="b" * 64,
    added=date(2026, 10, 12),
)


def test_batch_block_field_names_and_order():
    assert FIELD_RE.findall(render_batch_block(**BATCH)) == [
        "Type",
        "Location",
        "Use for",
        "Validation",
        "Catalog Key",
        "Raw SHA256",
        "Extracted Path",
        "Extract SHA256",
        "Date Added",
    ]


def test_batch_block_values():
    block = render_batch_block(**BATCH)
    assert block.startswith("### T\n")
    assert "- **Type**: documentation\n" in block
    assert "- **Location**: knowledge/sources/t/\n" in block
    assert "- **Use for**:\n" in block  # deliberately empty in this profile
    assert "- **Validation**:\n" in block
    assert "#### Extended Metadata\n- **Catalog Key**: lib:ABC\n" in block
    assert f"- **Raw SHA256**: {'a' * 64}\n" in block
    assert "- **Extracted Path**: knowledge/sources/t/\n" in block
    assert block.endswith("- **Date Added**: 2026-10-12")


# --- dedupe on the key --------------------------------------------------------------

KEYED_ROW_FIELDS = [
    "catalog_key" if name == "zotero_key" else name
    for name in json.loads(
        (Path(__file__).parent / "golden" / "manifest" / "keyed.jsonl").read_text()
    )
]


def _keyed(path: Path, key: str = "ABC123") -> KeyedFileSource:
    return KeyedFileSource(
        path=path,
        kind="catalog",
        key_field="catalog_key",
        key=key,
        key_label="Catalog Key",
        key_display=f"lib:{key}",
    )


@pytest.fixture
def inbox_pdf(tmp_path) -> Path:
    path = tmp_path / "inbox" / "paper.pdf"
    path.parent.mkdir()
    path.write_bytes(b"%PDF-1.4 never captured in these tests\n")
    return path


@pytest.fixture
def extractor_calls(monkeypatch) -> list[list[str]]:
    """Record every extractor run, and fail it, so a test sees whether capture was reached."""
    calls: list[list[str]] = []

    def run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="recorded, not run\n")

    monkeypatch.setattr(subprocess, "run", run)
    return calls


@pytest.mark.parametrize(
    "old_row",
    [
        {
            "catalog_key": "ABC123",
            "slug": "old_paper",
            "title": "Old Paper",
            "date_extracted": "2025-01-01",
        },
        {
            "source_id": "a" * 64,
            "source_kind": "catalog",
            "slug": "old_paper",
            "catalog_key": "ABC123",
        },
    ],
    ids=["row-without-source-kind", "row-with-source-kind"],
)
def test_a_known_key_is_a_duplicate_before_any_fetch(
    old_row, knowledge_tree, inbox_pdf, extractor_calls, run_dir
):
    knowledge_tree.manifest.write_text(json.dumps(old_row) + "\n")
    manifest_before = knowledge_tree.manifest.read_bytes()
    index_before = knowledge_tree.index.read_bytes()

    result = register(
        _keyed(inbox_pdf),
        SourceMetadata(title="Old Paper Again"),
        paths=knowledge_tree.paths,
        run_dir=run_dir,
    )

    assert result.outcome == "duplicate"
    assert result.reason == "already registered as old_paper"
    assert result.existing_slug == "old_paper"
    assert extractor_calls == []
    assert knowledge_tree.manifest.read_bytes() == manifest_before
    assert knowledge_tree.index.read_bytes() == index_before
    (receipt,) = read_receipts(run_dir)
    assert receipt["candidate"] == "catalog:ABC123"


def test_an_unknown_key_goes_on_to_capture(knowledge_tree, inbox_pdf, extractor_calls):
    knowledge_tree.manifest.write_text(
        json.dumps({"catalog_key": "ABC123", "slug": "old_paper", "title": "Old Paper"}) + "\n"
    )

    result = register(
        _keyed(inbox_pdf, key="XYZ789"),
        SourceMetadata(title="New Paper"),
        paths=knowledge_tree.paths,
    )

    assert result.outcome == "capture_failed"
    assert result.reason == "recorded, not run"
    assert len(extractor_calls) == 1


def test_a_batch_caller_supplies_only_a_title(knowledge_tree, inbox_pdf, extractor_calls):
    """The batch profile needs no prose; a blank title is still refused."""
    blank = register(_keyed(inbox_pdf), SourceMetadata(title=" "), paths=knowledge_tree.paths)
    assert blank.outcome == "precondition_failed"
    assert blank.reason == "caller must supply non-empty title"

    titled = register(_keyed(inbox_pdf), SourceMetadata(title="Paper"), paths=knowledge_tree.paths)
    assert titled.outcome == "capture_failed"  # past every precondition, into capture


@pytest.mark.slow
def test_a_keyed_source_registers_with_a_batch_block_and_its_key(knowledge_tree, generated_pdf):
    (knowledge_tree.sources / "batch_paper").mkdir()  # the slug is taken, so the key disambiguates

    result = register(
        _keyed(generated_pdf), SourceMetadata(title="Batch Paper"), paths=knowledge_tree.paths
    )

    assert result.outcome == "registered", result.reason
    assert result.slug == "batch_paper_ABC123"
    (row,) = load_manifest_rows(knowledge_tree.paths)
    assert list(row) == KEYED_ROW_FIELDS
    assert row["source_kind"] == "catalog"
    assert row["catalog_key"] == "ABC123"
    block = knowledge_tree.index.read_text().split("### Batch Paper", 1)[1]
    assert (
        "- **Type**: documentation\n- **Location**: knowledge/sources/batch_paper_ABC123/\n"
        in block
    )
    assert "- **Use for**:\n- **Validation**:\n" in block
    assert "- **Catalog Key**: lib:ABC123\n" in block
    assert (knowledge_tree.raw / generated_pdf.name).is_file()

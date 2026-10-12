"""On-disk bytes the package must write exactly as the fusion-tea seam did.

Every expectation under `golden/` was produced once from the seam snapshot
(fusion-tea 0a833b9f7) with the clock fixed at 2026-10-12T09:30:00Z, by a
derivation script kept with the work item's logs. Nothing here is recomputed
from package code. Where each file came from:

- `index/block.md`, `index/block_local_pdf.md`: the seam-profile block that
  `zotero_ingest.append_source_index_entry` writes (`_seam_block_lines`).
- `index/batch_block.md`: its `zotero-batch` profile (`_zotero_batch_block_lines`),
  whose key line is `- **Zotero Key**: <group id>:<item key>`.
- `index/anchor_how_sources.after.md`, `index/anchor_how_sources.batch.after.md`:
  `append_source_index_entry` run on `anchor_how_sources.before.md`.
- `index/anchor_how_this_file.*`, `index/eof_newline.*`, `index/eof_no_newline.*`:
  cases the snapshot cannot produce. The first applies the snapshot's own
  insertion (`<block>\\n\\n` at the start of the anchor's line) to the shipped
  template as of 2026-10-12, at its `## How This File Is Used` heading. The other
  two append `<block>\\n`, after a newline when the file lacks a final one.
- `receipts/*.json`: `source_registry._write_receipt`, for a registration and a
  pre-capture hold-out refusal in one run.
- `manifest/*.jsonl`: `source_registry._manifest_row` and `_append_manifest_row`.
- `seam.json`, `seam/`: `research_seam.request_key`, `open_run`, `log_*` and `close`,
  run from a scratch directory with `knowledge/research/requests` as the seam's
  home and the seam's clock fixed. The tests here run the package the same way.
- `index/hand_curated*`: a case the snapshot cannot produce, since it had no
  hand-curated writer. The block is the entry shape `docs/source-index.md` gives
  (heading, Type, Location, Use for, Validation), inserted into the frozen
  shipped template with the snapshot's own insertion at `## How This File Is Used`.

The register-then-retire round trips compare a registry with its own earlier bytes.
"""

import importlib
import json
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from agentic_mbse.research import (
    KeyedFileSource,
    LocalPdfSource,
    RegistryPaths,
    SourceMetadata,
    UrlSource,
    register,
)
from agentic_mbse.research.index import (
    HandCuratedEntry,
    add_entry,
    insert_block,
    render_batch_block,
    render_hand_curated_block,
    render_seam_block,
)
from agentic_mbse.research.manifest import append_manifest_row
from agentic_mbse.research.register import manifest_row
from agentic_mbse.research.retire import retire
from agentic_mbse.research.runs import write_receipt
from agentic_mbse.research.seam import (
    SeamHome,
    close,
    log_candidate,
    log_failure,
    log_search,
    open_run,
    request_key,
)
from tests.test_research.conftest import NO_GUARD

GOLDEN = Path(__file__).parent / "golden"


def _golden_json(relative: str) -> dict:
    return json.loads((GOLDEN / relative).read_text())


def _with_date(inputs: dict) -> dict:
    return inputs | {"added": date.fromisoformat(inputs["added"])}


@pytest.mark.parametrize(
    ("case", "block", "after"),
    [
        ("anchor_how_sources", "block.md", "anchor_how_sources.after.md"),
        ("anchor_how_sources", "batch_block.md", "anchor_how_sources.batch.after.md"),
        ("anchor_how_this_file", "block.md", "anchor_how_this_file.after.md"),
        ("eof_newline", "block.md", "eof_newline.after.md"),
        ("eof_no_newline", "block.md", "eof_no_newline.after.md"),
    ],
)
def test_insertion_bytes(case, block, after, tmp_path):
    index = tmp_path / "SOURCE_INDEX.md"
    index.write_bytes((GOLDEN / "index" / f"{case}.before.md").read_bytes())
    insert_block(index, (GOLDEN / "index" / block).read_text())
    assert index.read_bytes() == (GOLDEN / "index" / after).read_bytes()


@pytest.mark.parametrize(
    ("kind", "golden"), [("url", "block.md"), ("local_pdf", "block_local_pdf.md")]
)
def test_seam_block_equals_the_snapshot_block(kind, golden):
    inputs = _with_date(_golden_json("index/seam_inputs.json")[kind])
    assert render_seam_block(**inputs) == (GOLDEN / "index" / golden).read_text()


def test_keyed_batch_block_equals_the_snapshot_block():
    inputs = _with_date(_golden_json("index/batch_inputs.json"))
    assert render_batch_block(**inputs) == (GOLDEN / "index" / "batch_block.md").read_text()


def test_receipts_match_the_snapshot_names_and_bytes(tmp_path):
    inputs = _golden_json("receipts/inputs.json")
    at = datetime.fromisoformat(inputs["at"])
    for fields in inputs["receipts"]:
        write_receipt(tmp_path, at=at, **fields)

    written = sorted((tmp_path / "receipts").iterdir())
    golden = sorted(
        p
        for p in (GOLDEN / "receipts").iterdir()
        if p.suffix == ".json" and p.name != "inputs.json"
    )
    assert [p.name for p in written] == [p.name for p in golden]
    for ours, snapshot in zip(written, golden, strict=True):
        assert ours.read_bytes() == snapshot.read_bytes()


def _manifest_source(kind: str, inputs: dict):
    path = Path(inputs["local_pdf_path"])
    if kind == "url":
        return UrlSource(url=inputs["url"])
    if kind == "local_pdf":
        return LocalPdfSource(path=path)
    return KeyedFileSource(
        path=path, key_label="Key", key_display="not in a row", **inputs["keyed"]
    )


@pytest.mark.parametrize("kind", ["url", "local_pdf", "keyed"])
def test_manifest_rows_match_the_snapshot_bytes(kind, tmp_path):
    """Fields, their order and their values, as the line the snapshot appended."""
    inputs = _golden_json("manifest/inputs.json")
    paths = RegistryPaths(knowledge_dir=tmp_path)
    row = manifest_row(
        _manifest_source(kind, inputs),
        **inputs["rows"][kind],
        source_id=inputs["source_id"],
        raw_artifact_sha256=inputs["raw_artifact_sha256"],
        extract_sha256=inputs["extract_sha256"],
        extracted=date.fromisoformat(inputs["date_extracted"]),
    )
    append_manifest_row(paths, row)
    assert paths.manifest.read_bytes() == (GOLDEN / "manifest" / f"{kind}.jsonl").read_bytes()


def test_add_entry_bytes_on_the_shipped_template(tmp_path):
    paths = RegistryPaths(knowledge_dir=tmp_path / "knowledge")
    paths.knowledge_dir.mkdir()
    paths.index.write_bytes((GOLDEN / "index" / "anchor_how_this_file.before.md").read_bytes())
    entry = HandCuratedEntry(**_golden_json("index/hand_curated_inputs.json"))

    assert (
        render_hand_curated_block(entry) == (GOLDEN / "index" / "hand_curated_block.md").read_text()
    )
    assert add_entry(entry, paths=paths, guard=NO_GUARD).outcome == "added"
    assert paths.index.read_bytes() == (GOLDEN / "index" / "hand_curated.after.md").read_bytes()


ROUND_TRIP_METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises the round trip.",
    validation="Compare against the fixture page itself.",
    caveat="A test fixture.",
)


@pytest.fixture
def tree_with_one_registration(tmp_path, local_site):
    """A registry whose index starts as a golden `before` file and that already holds one source.

    The earlier registration means the manifest exists before the round trip, so
    the round trip has bytes to restore rather than a file to leave empty.
    """

    def make(case: str) -> RegistryPaths:
        paths = RegistryPaths(knowledge_dir=tmp_path / case / "knowledge")
        paths.sources.mkdir(parents=True)
        paths.index.write_bytes((GOLDEN / "index" / f"{case}.before.md").read_bytes())
        earlier = register(
            UrlSource(url=local_site.url("utf8.html")),
            ROUND_TRIP_METADATA,
            paths=paths,
            guard=NO_GUARD,
        )
        assert earlier.outcome == "registered", earlier.reason
        return paths

    return make


@pytest.mark.parametrize("case", ["anchor_how_sources", "anchor_how_this_file", "eof_newline"])
def test_register_then_retire_restores_the_registry(case, tree_with_one_registration, local_site):
    paths = tree_with_one_registration(case)
    before = (paths.index.read_bytes(), paths.manifest.read_bytes())

    result = register(
        UrlSource(url=local_site.url("latin1.html")),
        replace(ROUND_TRIP_METADATA, title="Cable Note"),
        paths=paths,
        guard=NO_GUARD,
    )
    assert result.outcome == "registered", result.reason
    assert result.slug is not None
    assert (paths.index.read_bytes(), paths.manifest.read_bytes()) != before
    assert retire(result.slug, "round trip", paths=paths, guard=NO_GUARD).outcome == "retired"

    assert (paths.index.read_bytes(), paths.manifest.read_bytes()) == before


# --- the seam's run directory ----------------------------------------------------------

seam_module = importlib.import_module("agentic_mbse.research.seam")

#: The instant the snapshot's clock was fixed at when the seam goldens were derived.
SEAM_NOW = datetime(2026, 10, 12, 9, 30, tzinfo=timezone.utc)


def test_request_key_matches_the_snapshot():
    golden = _golden_json("seam.json")
    assert request_key(golden["request"]) == golden["request_key"]


@pytest.fixture
def seam_home(tmp_path, monkeypatch) -> SeamHome:
    """The seam home at the relative path the snapshot ran with, its clock fixed at `SEAM_NOW`."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(seam_module, "_now", lambda: SEAM_NOW)
    home = SeamHome(root=Path("knowledge/research/requests"))
    home.root.mkdir(parents=True)
    return home


def _open(home: SeamHome, request: dict) -> Path:
    request_path = home.root / f"{request['request_id']}.json"
    request_path.write_text(json.dumps(request))
    opened = open_run(request_path, home=home)
    assert opened.outcome == "opened" and opened.run_dir is not None, opened.message
    return opened.run_dir


def test_a_bounded_negative_run_matches_the_snapshot_bytes(seam_home):
    run_dir = _open(seam_home, _golden_json("seam.json")["request"])
    log_search(run_dir, "widget coil current density")
    log_candidate(run_dir, "https://example.org/a", "rejected", "paywalled")
    log_failure(run_dir, "https://example.org/b", "404", disposition="closed")
    close(run_dir, adequacy="exhausted")

    golden_run = GOLDEN / "seam" / "negative_run"
    assert f"{run_dir}\n" == (golden_run / "run_dir.txt").read_text()
    for name in ("run.json", "run.jsonl", "process_log.md", "return.json"):
        assert (run_dir / name).read_bytes() == (golden_run / name).read_bytes(), name
    (negative,) = seam_home.negatives.iterdir()
    assert negative.read_bytes() == (GOLDEN / "seam" / "negative.json").read_bytes()


def test_a_registered_run_matches_the_snapshot_bytes(seam_home):
    request = _golden_json("seam.json")["request"] | {"request_id": "REQ-902", "consumer": "WI-902"}
    run_dir = _open(seam_home, request)
    write_receipt(
        run_dir,
        outcome="registered",
        candidate="http://127.0.0.1:8000/utf8.html",
        slug="widget_coil_note",
        path="knowledge/sources/widget_coil_note/",
        source_id="99d8ff05c9631996c0d62b5c3ac53be01bcbdc92d76e9a18ad95096080336bed",
        triage="keeper",
        reason="",
        rule_id=None,
        captured=True,
        at=SEAM_NOW,
    )
    close(run_dir)

    golden_run = GOLDEN / "seam" / "registered_run"
    for name in ("run.json", "return.json"):
        assert (run_dir / name).read_bytes() == (golden_run / name).read_bytes(), name
    assert not seam_home.negatives.exists()

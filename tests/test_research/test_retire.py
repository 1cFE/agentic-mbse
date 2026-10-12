"""`retire`: the one removal door.

It removes exactly one entry's four artifacts together, or nothing, and leaves
one durable `RETIRED.jsonl` line; `verify` then expects the slug absent and
reports it if it comes back. Sources are registered through the real capture
chain against the loopback fixture site, so what is retired is what `register`
actually wrote.
"""

import hashlib
import importlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from agentic_mbse.cli import get_template_path
from agentic_mbse.research import LocalPdfSource, SourceMetadata, UrlSource, register
from agentic_mbse.research.index import (
    HandCuratedEntry,
    add_entry,
    parse_index,
    with_block_inserted,
)
from agentic_mbse.research.retire import RetirementError, retire
from agentic_mbse.research.verify import verify
from tests.test_research.conftest import (
    GUARD_FILE_SOURCE,
    NO_GUARD,
    SEALED_TOKEN,
    FakeGuard,
    FakeMatch,
    RecordingGuard,
    ScriptedGuard,
    registry_state,
    write_research_config,
)

retire_module = importlib.import_module("agentic_mbse.research.retire")

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises retirement.",
    validation="Compare against the fixture page itself.",
    caveat="A test fixture.",
)
REASON = "Captured content is a fixture, not a paper (test)."

#: Each removal rung, by the name the ladder calls it through in `retire.py`.
RUNGS = {
    "at_park": "_park",
    "after_park": "write_manifest_without",
    "after_manifest": "_write_index_without",
    "after_index": "_append_retired_line",
}

#: Bars a registry path, a hold-out path and the neutral token.
RETIRE_GUARD = FakeGuard(
    terms=(SEALED_TOKEN,), path_globs=("knowledge/sources/sealed_*", "knowledge/holdout/*")
)

FAULT_PREFIX = "hold-out guard unavailable: "


def _state(tree) -> tuple:
    """`registry_state` plus the `RETIRED.jsonl` bytes, or None when absent."""
    retired = tree.paths.retired
    return (*registry_state(tree), retired.read_bytes() if retired.exists() else None)


def _rows(tree) -> list[dict]:
    return [json.loads(line) for line in tree.manifest.read_text().splitlines() if line.strip()]


def _block_text(tree, slug: str) -> str:
    """The block as the writer wrote it: heading through last metadata line."""
    blocks = parse_index(tree.index.read_text(), project_root=tree.paths.project_root)
    (block,) = [b for b in blocks if b.slug == slug]
    return block.text


def _register(local_site, tree, page, title):
    result = register(
        UrlSource(url=local_site.url(page)), replace(METADATA, title=title), paths=tree.paths
    )
    assert result.outcome == "registered", result.reason
    return result


@pytest.fixture
def two_sources(local_site, knowledge_tree):
    """Two registered entries, and the registry state taken between them."""
    kept = _register(local_site, knowledge_tree, "utf8.html", "Widget Coil Note")
    after_first = _state(knowledge_tree)
    gone = _register(local_site, knowledge_tree, "latin1.html", "Cable Note")
    return kept, gone, after_first


# --- a removal, and the line it leaves ---------------------------------------------


def test_retire_removes_all_four_artifacts_and_records_one_line(knowledge_tree, two_sources):
    kept, gone, after_first = two_sources
    block = _block_text(knowledge_tree, gone.slug)
    row = next(r for r in _rows(knowledge_tree) if r["slug"] == gone.slug)
    before = datetime.now(timezone.utc)

    result = retire(gone.slug, REASON, paths=knowledge_tree.paths)

    assert result.outcome == "retired" and result.slug == gone.slug
    assert not gone.path.exists()
    assert gone.slug not in {r["slug"] for r in _rows(knowledge_tree)}
    assert f"knowledge/sources/{gone.slug}/" not in knowledge_tree.index.read_text()
    assert not list(knowledge_tree.paths.staging.iterdir())
    # The registry is byte-identical to its state before the retired entry was registered.
    assert _state(knowledge_tree)[:4] == after_first[:4]
    assert (kept.path / "output.md").is_file()

    lines = [json.loads(line) for line in knowledge_tree.paths.retired.read_text().splitlines()]
    assert len(lines) == 1 and lines[0] == result.retired_line
    line = lines[0]
    assert list(line) == ["slug", "retired_at", "reason", "index_block_sha256", "row"]
    assert line["slug"] == gone.slug and line["row"] == row and line["reason"] == REASON
    assert line["index_block_sha256"] == hashlib.sha256(block.encode("utf-8")).hexdigest()
    retired_at = datetime.fromisoformat(line["retired_at"])
    assert retired_at.tzinfo is not None and before <= retired_at <= datetime.now(timezone.utc)

    assert result.removed == {
        "manifest_row": row,
        "index_block": block,
        "source_dir": f"knowledge/sources/{gone.slug}/",
        "raw_copy": None,  # a URL source keeps raw.html inside its directory
    }

    report = verify(knowledge_tree.paths)
    assert report.findings == () and not report.has_faults


def test_retiring_a_fresh_targets_only_source_leaves_the_template_and_an_empty_manifest(
    knowledge_tree, local_site
):
    only = _register(local_site, knowledge_tree, "utf8.html", "Widget Coil Note")

    assert retire(only.slug, REASON, paths=knowledge_tree.paths).outcome == "retired"

    assert knowledge_tree.index.read_bytes() == get_template_path().read_bytes()
    assert knowledge_tree.manifest.read_bytes() == b""
    assert list(knowledge_tree.sources.iterdir()) == []
    assert verify(knowledge_tree.paths).findings == ()


@pytest.mark.slow
def test_a_local_pdf_retirement_removes_its_raw_copy_or_puts_it_back(
    knowledge_tree, generated_pdf, monkeypatch
):
    """A local PDF owns a copy in `knowledge/raw/`, so it is the one source with two artifacts to park."""
    registered = register(LocalPdfSource(path=generated_pdf), METADATA, paths=knowledge_tree.paths)
    assert registered.outcome == "registered", registered.reason
    raw_copy = knowledge_tree.raw / generated_pdf.name
    assert raw_copy.is_file()
    before = _state(knowledge_tree)

    park = retire_module._park
    parks = []

    def fail_second_park(original, spot):
        parks.append(original)
        if len(parks) == 2:
            raise OSError("injected failure parking the raw copy")
        park(original, spot)

    monkeypatch.setattr(retire_module, "_park", fail_second_park)
    with pytest.raises(RetirementError, match="parking the raw copy"):
        retire(registered.slug, REASON, paths=knowledge_tree.paths)
    assert parks == [registered.path, raw_copy]
    assert _state(knowledge_tree) == before
    monkeypatch.setattr(retire_module, "_park", park)

    result = retire(registered.slug, REASON, paths=knowledge_tree.paths)

    assert result.outcome == "retired"
    assert result.removed is not None
    assert result.removed["raw_copy"] == f"knowledge/raw/{generated_pdf.name}"
    assert not raw_copy.exists() and not registered.path.exists()
    assert generated_pdf.is_file()  # the caller's original is never touched
    assert verify(knowledge_tree.paths).findings == ()


# --- refusals write nothing --------------------------------------------------------


def test_unknown_slug_refuses_and_writes_nothing(knowledge_tree, two_sources):
    before = _state(knowledge_tree)
    result = retire("no_such_source", REASON, paths=knowledge_tree.paths)
    assert result.outcome == "unknown_slug"
    assert result.reason == "no manifest row carries slug no_such_source"
    assert _state(knowledge_tree) == before
    assert not knowledge_tree.paths.retired.exists()


@pytest.mark.parametrize(
    ("slug", "rule_id"),
    [
        ("sealed_cost_documentation", "path:knowledge/sources/sealed_*"),  # a barred registry path
        (
            "knowledge/holdout/widget/paper.pdf",
            "path:knowledge/holdout/*",
        ),  # a hold-out path as slug
        (f"{SEALED_TOKEN}_notes", f"term:{SEALED_TOKEN}"),  # a barred term in the slug
    ],
)
def test_holdout_slug_refuses_before_anything_else(knowledge_tree, two_sources, slug, rule_id):
    before = _state(knowledge_tree)
    result = retire(slug, REASON, paths=knowledge_tree.paths, guard=RETIRE_GUARD)
    assert result.outcome == "holdout_hit"
    assert result.rule_id == rule_id
    assert result.reason == f"{rule_id} matched 1x"
    assert _state(knowledge_tree) == before


@pytest.mark.parametrize("slug", ["cable_note", "../not a slug"])
def test_the_guard_sees_the_slug_twice_as_a_path_then_as_text(knowledge_tree, two_sources, slug):
    """Bare, then as the literal relative registry path the project's globs spell, never the tree's own."""
    guard = RecordingGuard()
    retire(slug, REASON, paths=knowledge_tree.paths, guard=guard)
    assert guard.calls == [
        ("check_input_path", Path(slug)),
        ("check_input_path", Path("knowledge/sources") / slug),
        ("scan_terms", slug),
    ]


def test_a_guard_file_the_project_names_bars_a_slug(knowledge_tree, two_sources):
    project = knowledge_tree.root.parent
    (project / "guard.py").write_text(GUARD_FILE_SOURCE)
    write_research_config(project, 'holdout-guard = "guard.py"')
    before = _state(knowledge_tree)

    result = retire(f"{SEALED_TOKEN}_notes", REASON, paths=knowledge_tree.paths)

    assert result.outcome == "holdout_hit" and result.rule_id == f"term:{SEALED_TOKEN}"
    assert _state(knowledge_tree) == before


@pytest.mark.parametrize(
    ("guard", "detail"),
    [
        pytest.param(
            ScriptedGuard(raises_in="check_input_path"),
            "check_input_path raised RuntimeError: check_input_path could not run",
            id="input path check raises",
        ),
        pytest.param(
            ScriptedGuard(raises_in="scan_terms"),
            "scan_terms raised RuntimeError: scan_terms could not run",
            id="term scan raises",
        ),
        pytest.param(
            ScriptedGuard(terms_answer=[FakeMatch(rule_id="", count=1, offsets=(0,))]),
            "scan_terms answered a match without a rule_id",
            id="malformed match",
        ),
    ],
)
def test_a_guard_that_cannot_answer_refuses_and_writes_nothing(
    guard, detail, knowledge_tree, two_sources
):
    _, gone, _ = two_sources
    before = _state(knowledge_tree)
    result = retire(gone.slug, REASON, paths=knowledge_tree.paths, guard=guard)
    assert result.outcome == "precondition_failed"
    assert result.reason == FAULT_PREFIX + detail
    assert _state(knowledge_tree) == before


def test_a_misconfigured_project_guard_refuses_a_retirement_that_would_pass(
    knowledge_tree, two_sources
):
    _, gone, _ = two_sources
    write_research_config(knowledge_tree.root.parent, 'holdout_guard = "guard.py"')
    before = _state(knowledge_tree)

    result = retire(gone.slug, REASON, paths=knowledge_tree.paths)

    assert result.outcome == "precondition_failed"
    assert result.reason.startswith(FAULT_PREFIX) and "holdout_guard" in result.reason
    assert _state(knowledge_tree) == before
    assert gone.path.is_dir()


@pytest.mark.parametrize(
    ("slug", "reason", "message"),
    [
        ("cable_note", "   ", "caller must supply a non-empty reason"),
        ("../sources/cable_note", REASON, "not a registry slug: '../sources/cable_note'"),
        (
            "knowledge/sources/cable_note",
            REASON,
            "not a registry slug: 'knowledge/sources/cable_note'",
        ),
    ],
)
def test_blank_reason_or_malformed_slug_refuses(knowledge_tree, two_sources, slug, reason, message):
    before = _state(knowledge_tree)
    result = retire(slug, reason, paths=knowledge_tree.paths, guard=NO_GUARD)
    assert result.outcome == "precondition_failed"
    assert result.reason == message
    assert _state(knowledge_tree) == before


def _duplicate_the_row(tree, slug):
    row = next(r for r in _rows(tree) if r["slug"] == slug)
    with open(tree.manifest, "a") as handle:
        handle.write(json.dumps(row) + "\n")


def _duplicate_the_block(tree, slug):
    tree.index.write_text(with_block_inserted(tree.index.read_text(), _block_text(tree, slug)))


def _drop_the_block(tree, slug):
    blocks = parse_index(tree.index.read_text(), project_root=tree.paths.project_root)
    (block,) = [b for b in blocks if b.slug == slug]
    text = tree.index.read_text()
    tree.index.write_text(text[: block.start] + text[block.end :])


def _drop_the_directory(tree, slug):
    (tree.sources / slug).rename(tree.root / "moved_away")


@pytest.mark.parametrize(
    ("drift", "message"),
    [
        (
            _duplicate_the_row,
            "2 manifest rows carry slug cable_note; run verify and resolve the drift first",
        ),
        (
            _duplicate_the_block,
            "2 SOURCE_INDEX.md blocks locate cable_note; expected exactly one — run verify and resolve the drift first",
        ),
        (
            _drop_the_block,
            "0 SOURCE_INDEX.md blocks locate cable_note; expected exactly one — run verify and resolve the drift first",
        ),
        (
            _drop_the_directory,
            "source directory knowledge/sources/cable_note/ does not exist; run verify",
        ),
    ],
)
def test_drift_around_the_slug_refuses_and_writes_nothing(
    knowledge_tree, two_sources, drift, message
):
    _, gone, _ = two_sources
    assert gone.slug == "cable_note"
    drift(knowledge_tree, gone.slug)
    before = _state(knowledge_tree)

    result = retire(gone.slug, REASON, paths=knowledge_tree.paths)

    assert result.outcome == "precondition_failed"
    assert result.reason == message
    assert _state(knowledge_tree) == before


def test_a_reference_from_another_entry_refuses_but_a_supersession_claim_does_not(
    knowledge_tree, two_sources
):
    kept, gone, _ = two_sources
    index = knowledge_tree.index.read_text()
    caveat = "- **Caveat**: A test fixture."
    kept_block = _block_text(knowledge_tree, kept.slug)
    assert caveat in kept_block

    dependent = kept_block.replace(caveat, f"{caveat} Read with knowledge/sources/{gone.slug}/.")
    knowledge_tree.index.write_text(index.replace(kept_block, dependent))
    before = _state(knowledge_tree)
    result = retire(gone.slug, REASON, paths=knowledge_tree.paths)
    assert result.outcome == "referenced"
    assert result.references == (f"SOURCE_INDEX.md block ({kept.slug})",)
    assert _state(knowledge_tree) == before

    superseding = kept_block.replace(
        caveat, f"{caveat} Supersedes the defective registration knowledge/sources/{gone.slug}/."
    )
    knowledge_tree.index.write_text(index.replace(kept_block, superseding))
    result = retire(gone.slug, REASON, paths=knowledge_tree.paths)
    assert result.outcome == "retired"
    assert f"knowledge/sources/{gone.slug}/" in _block_text(knowledge_tree, kept.slug)
    assert verify(knowledge_tree.paths).findings == ()


def test_a_hand_curated_entry_that_names_the_slug_refuses(knowledge_tree, two_sources):
    _, gone, _ = two_sources
    entry = HandCuratedEntry(
        title="Widget Notebook",
        type="documentation",
        location="docs/widget_notebook.md",
        use_for=f"Annotations on {gone.slug}",
        validation="N/A",
    )
    assert add_entry(entry, paths=knowledge_tree.paths, guard=NO_GUARD).outcome == "added"

    result = retire(gone.slug, REASON, paths=knowledge_tree.paths)

    assert result.outcome == "referenced"
    assert result.references == ("SOURCE_INDEX.md block (### Widget Notebook)",)


def test_a_manifest_field_referencing_the_slug_refuses(knowledge_tree, two_sources):
    kept, gone, _ = two_sources
    rows = _rows(knowledge_tree)
    for row in rows:
        if row["slug"] == kept.slug:
            row["caveat"] = f"companion to {gone.slug}"
    knowledge_tree.manifest.write_text("".join(json.dumps(r) + "\n" for r in rows))
    before = _state(knowledge_tree)
    result = retire(gone.slug, REASON, paths=knowledge_tree.paths)
    assert result.outcome == "referenced"
    assert result.references == (f"manifest row field caveat ({kept.slug})",)
    assert _state(knowledge_tree) == before


# --- a failed rung puts everything back --------------------------------------------


@pytest.mark.parametrize("rung", sorted(RUNGS))
def test_failure_at_each_rung_leaves_everything(rung, knowledge_tree, two_sources, monkeypatch):
    kept, gone, _ = two_sources
    before = _state(knowledge_tree)

    def boom(*args, **kwargs):
        raise OSError(f"injected failure at {rung}")

    monkeypatch.setattr(retire_module, RUNGS[rung], boom)
    with pytest.raises(RetirementError, match=rung):
        retire(gone.slug, REASON, paths=knowledge_tree.paths)

    assert _state(knowledge_tree) == before
    assert (gone.path / "output.md").is_file() and (kept.path / "output.md").is_file()
    assert not list(knowledge_tree.paths.staging.iterdir())
    assert verify(knowledge_tree.paths).findings == ()


@pytest.mark.parametrize("earlier_retirement", [False, True], ids=["no log yet", "log exists"])
def test_a_half_written_retired_line_is_cut_back(
    earlier_retirement, knowledge_tree, two_sources, monkeypatch
):
    """The log goes back to its length before the attempt, or away if the attempt created it."""
    kept, gone, _ = two_sources
    if earlier_retirement:
        assert retire(kept.slug, REASON, paths=knowledge_tree.paths).outcome == "retired"
    before = _state(knowledge_tree)

    def half_a_line(paths, line):
        with open(paths.retired, "a") as handle:
            handle.write('{"slug": "cable_')
        raise OSError("disk full")

    monkeypatch.setattr(retire_module, "_append_retired_line", half_a_line)
    with pytest.raises(RetirementError, match="disk full"):
        retire(gone.slug, REASON, paths=knowledge_tree.paths)

    assert _state(knowledge_tree) == before
    assert knowledge_tree.paths.retired.exists() is earlier_retirement


# --- verify expects a retired slug absent, and reports it coming back -----------------


def test_verify_reports_each_way_a_retired_slug_can_reappear(knowledge_tree, two_sources):
    kept, gone, _ = two_sources
    block = _block_text(knowledge_tree, gone.slug)
    row = next(r for r in _rows(knowledge_tree) if r["slug"] == gone.slug)
    assert retire(gone.slug, REASON, paths=knowledge_tree.paths).outcome == "retired"
    assert verify(knowledge_tree.paths).findings == ()

    with open(knowledge_tree.manifest, "a") as handle:
        handle.write(json.dumps(row) + "\n")
    report = verify(knowledge_tree.paths)
    assert [(f.kind, f.klass, f.path) for f in report.findings] == [
        ("retired_reappeared", "fault", f"knowledge/sources/{gone.slug}"),
    ]
    assert "manifest row" in report.findings[0].detail and report.has_faults

    (knowledge_tree.paths.sources / gone.slug).mkdir()
    knowledge_tree.index.write_text(with_block_inserted(knowledge_tree.index.read_text(), block))
    report = verify(knowledge_tree.paths)
    assert {f.kind for f in report.findings} == {"retired_reappeared"}
    assert sorted(f.detail.split(" for ")[0] for f in report.findings) == [
        "SOURCE_INDEX.md block",
        "manifest row",
        "source directory",
    ]
    assert report.has_faults


def test_verify_still_reports_ordinary_drift_beside_retirements(knowledge_tree, two_sources):
    kept, gone, _ = two_sources
    assert retire(gone.slug, REASON, paths=knowledge_tree.paths).outcome == "retired"
    (knowledge_tree.paths.sources / "orphan_source").mkdir()
    report = verify(knowledge_tree.paths)
    assert [f.kind for f in report.findings] == ["orphan_source_dir"]

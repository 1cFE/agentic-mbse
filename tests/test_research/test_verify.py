"""`verify` reports registry drift and never repairs it.

It sees drift in both directions: a source directory or a manifest row with
nothing behind it, and an index block locating a directory no row carries.
Hand-curated entries and commented-out blocks are never findings.
"""

import json

import pytest

from agentic_mbse.research import SourceMetadata, UrlSource, register
from agentic_mbse.research.index import HandCuratedEntry, add_entry, insert_block
from agentic_mbse.research.verify import Finding, format_finding, verify
from tests.test_research.conftest import NO_GUARD, registry_state

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises verify.",
    validation="Compare against the fixture page itself.",
    caveat="A test fixture.",
)


def _append_row(tree, row: dict) -> None:
    with open(tree.manifest, "a") as handle:
        handle.write(json.dumps(row) + "\n")


def _make_orphan_dir(tree, name="orphan_source") -> None:
    (tree.sources / name).mkdir()
    (tree.sources / name / "output.md").write_text("orphan\n")


def _make_row_without_block(tree, slug="rowless") -> None:
    (tree.sources / slug).mkdir()
    _append_row(
        tree, {"source_id": "a" * 64, "source_kind": "url", "slug": slug, "title": "Rowless"}
    )


def _make_unresolvable_row(tree, slug="vanished") -> None:
    _append_row(
        tree, {"source_id": "b" * 64, "source_kind": "url", "slug": slug, "title": "Vanished"}
    )


def _place_block(tree, title: str, location: str) -> None:
    """An index block written by hand, as a person in an editor would."""
    insert_block(
        tree.index,
        "\n".join(
            [
                f"### {title}",
                "- **Type**: documentation",
                f"- **Location**: {location}",
                "- **Use for**: Written by hand.",
                "- **Validation**: N/A",
            ]
        ),
    )


def _write_baseline(tree, *, orphan_source_dirs=(), loose_files=()) -> None:
    tree.paths.baseline.write_text(
        json.dumps(
            {
                "generated": "2026-08-25",
                "note": "pre-registry drift",
                "orphan_source_dirs": list(orphan_source_dirs),
                "loose_files": list(loose_files),
            }
        )
    )


def test_each_drift_shape_is_reported(knowledge_tree):
    _make_orphan_dir(knowledge_tree)
    _make_row_without_block(knowledge_tree)
    _make_unresolvable_row(knowledge_tree)
    (knowledge_tree.sources / "LOOSE.md").write_text("not a source dir\n")
    _place_block(knowledge_tree, "Hand-Placed Capture", "knowledge/sources/hand_placed/")

    report = verify(knowledge_tree.paths)
    assert {f.kind for f in report.findings} == {
        "orphan_source_dir",
        "row_without_block",
        "unresolvable_path",
        "loose_file",
        "block_without_row",
    }
    assert all(f.klass == "fault" for f in report.findings)
    assert report.has_faults


def test_findings_come_in_the_snapshot_order(knowledge_tree):
    """Source directories first, then index blocks, then manifest rows."""
    _make_unresolvable_row(knowledge_tree)
    _place_block(knowledge_tree, "Hand-Placed Capture", "knowledge/sources/hand_placed/")
    _make_orphan_dir(knowledge_tree)

    assert [f.kind for f in verify(knowledge_tree.paths).findings] == [
        "orphan_source_dir",
        "block_without_row",
        "unresolvable_path",
    ]


def test_a_registered_source_produces_no_finding(local_site, knowledge_tree):
    result = register(
        UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths
    )
    assert result.outcome == "registered"
    report = verify(knowledge_tree.paths)
    assert report.findings == () and not report.has_faults


def test_baseline_entries_are_legacy_not_faults(knowledge_tree):
    _write_baseline(
        knowledge_tree,
        orphan_source_dirs=["knowledge/sources/orphan_source/"],
        loose_files=["knowledge/sources/LOOSE.md"],
    )
    _make_orphan_dir(knowledge_tree)
    (knowledge_tree.sources / "LOOSE.md").write_text("not a source dir\n")
    _make_row_without_block(knowledge_tree)

    report = verify(knowledge_tree.paths)
    by_kind = {f.kind: f for f in report.findings}
    assert by_kind["orphan_source_dir"].klass == "legacy"
    assert by_kind["loose_file"].klass == "legacy"
    assert by_kind["row_without_block"].klass == "fault"
    assert report.has_faults


# --- an index block with no row ------------------------------------------------------


def test_a_block_locating_a_baseline_orphan_is_legacy(knowledge_tree):
    """A hand-made block over a directory the baseline already lists, as a project's first registry has."""
    _write_baseline(knowledge_tree, orphan_source_dirs=["knowledge/sources/orphan_source"])
    _make_orphan_dir(knowledge_tree)
    _place_block(knowledge_tree, "Orphan Source (by hand)", "knowledge/sources/orphan_source/")

    report = verify(knowledge_tree.paths)

    assert [format_finding(f) for f in report.findings] == [
        "legacy  orphan_source_dir    knowledge/sources/orphan_source — source directory with no manifest row",
        "legacy  block_without_row    knowledge/sources/orphan_source — SOURCE_INDEX.md block with no manifest row",
    ]
    assert not report.has_faults


@pytest.mark.parametrize(
    "location",
    [
        "knowledge/sources/hand_placed/",
        "knowledge/sources/hand_placed",
        "./knowledge/sources/hand_placed/",
        "knowledge/sources/hand_placed/output.md",
    ],
)
def test_a_block_locating_a_directory_no_row_carries_is_a_fault(knowledge_tree, location):
    _place_block(knowledge_tree, "Hand-Placed Capture", location)

    report = verify(knowledge_tree.paths)

    assert report.findings == (
        Finding(
            kind="block_without_row",
            klass="fault",
            path="knowledge/sources/hand_placed",
            detail="SOURCE_INDEX.md block with no manifest row",
        ),
    )
    assert report.has_faults


def test_an_absolute_location_under_the_project_is_read_as_relative(knowledge_tree):
    absolute = knowledge_tree.root.parent.resolve() / "knowledge" / "sources" / "hand_placed"
    _place_block(knowledge_tree, "Hand-Placed Capture", f"{absolute}/")

    assert [f.path for f in verify(knowledge_tree.paths).findings] == [
        "knowledge/sources/hand_placed"
    ]


def test_hand_curated_entries_are_never_findings(knowledge_tree):
    for title, kind, location in [
        ("Reference Code", "codebase", "/srv/reference/widget-model"),
        ("Standards API", "database", "https://standards.example.com/api"),
        ("Widget Spec", "documentation", "docs/widget_spec.pdf"),
        ("Old Sources Folder", "reference", "knowledge/sources_archive/widget/"),
    ]:
        entry = HandCuratedEntry(
            title=title, type=kind, location=location, use_for="Widget sizing.", validation="N/A"
        )
        assert add_entry(entry, paths=knowledge_tree.paths, guard=NO_GUARD).outcome == "added"

    report = verify(knowledge_tree.paths)
    assert report.findings == () and not report.has_faults


def test_commented_blocks_are_ignored(knowledge_tree):
    """The shipped template's examples, and a commented-out registry block, are not entries."""
    commented = "\n".join(
        [
            "<!--",
            "### Retired Capture",
            "- **Type**: url",
            "- **Location**: knowledge/sources/ghost_capture/",
            "-->",
        ]
    )
    insert_block(knowledge_tree.index, commented)
    knowledge_tree.paths.retired.write_text(
        json.dumps({"slug": "ghost_capture", "reason": "test"}) + "\n"
    )

    report = verify(knowledge_tree.paths)
    assert report.findings == () and not report.has_faults


# --- reading only ---------------------------------------------------------------------


def test_verify_writes_nothing(knowledge_tree):
    _make_orphan_dir(knowledge_tree)
    _make_unresolvable_row(knowledge_tree)
    before = registry_state(knowledge_tree)
    verify(knowledge_tree.paths)
    assert registry_state(knowledge_tree) == before
    assert not knowledge_tree.paths.lock.exists()
    assert not knowledge_tree.paths.staging.exists()


def test_a_clean_registry_has_no_faults(knowledge_tree):
    report = verify(knowledge_tree.paths)
    assert report.findings == () and not report.has_faults


# --- the report line ------------------------------------------------------------------

# Report lines in the seam snapshot's format: the class padded to 7, the kind to 20,
# then the path, an em dash and the detail. Written out by hand, not formatted here.
SNAPSHOT_LINES = [
    (
        Finding(
            kind="loose_file",
            klass="legacy",
            path="knowledge/sources/NOTES.md",
            detail="not a source directory",
        ),
        "legacy  loose_file           knowledge/sources/NOTES.md — not a source directory",
    ),
    (
        Finding(
            kind="orphan_source_dir",
            klass="legacy",
            path="knowledge/sources/widget_pages",
            detail="source directory with no manifest row",
        ),
        "legacy  orphan_source_dir    knowledge/sources/widget_pages — source directory with no manifest row",
    ),
]


@pytest.mark.parametrize(("finding", "line"), SNAPSHOT_LINES)
def test_a_finding_prints_in_the_snapshot_format(finding, line):
    assert format_finding(finding) == line


def test_a_fault_line_pads_the_class_to_the_width_of_legacy():
    finding = Finding(
        kind="retired_reappeared",
        klass="fault",
        path="knowledge/sources/cable_note",
        detail="manifest row for a slug retired in knowledge/RETIRED.jsonl",
    )
    assert format_finding(finding) == (
        "fault   retired_reappeared   knowledge/sources/cable_note — "
        "manifest row for a slug retired in knowledge/RETIRED.jsonl"
    )

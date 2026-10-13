"""`MANIFEST.jsonl`: reading, appending, and rolling back, on a target that may have none."""

import json

from agentic_mbse.research.manifest import (
    append_manifest_row,
    first_matching_row,
    load_manifest_rows,
    mark_manifest,
    roll_back_manifest,
    write_manifest_without,
)


def test_a_fresh_target_has_no_manifest_and_no_rows(knowledge_tree):
    assert not knowledge_tree.manifest.exists()
    assert load_manifest_rows(knowledge_tree.paths) == []


def test_load_manifest_rows_returns_every_row(knowledge_tree):
    knowledge_tree.manifest.write_text(
        json.dumps({"source_id": "a" * 64, "slug": "s"})
        + "\n"
        + "\n"
        + json.dumps({"catalog_key": "ABC", "slug": "t"})
        + "\n"
    )
    rows = load_manifest_rows(knowledge_tree.paths)
    assert [r["slug"] for r in rows] == ["s", "t"]


def test_append_creates_the_manifest_and_writes_one_line_per_row(knowledge_tree):
    append_manifest_row(knowledge_tree.paths, {"slug": "a", "title": "A"})
    append_manifest_row(knowledge_tree.paths, {"slug": "b", "title": "B"})
    assert knowledge_tree.manifest.read_text() == (
        '{"slug": "a", "title": "A"}\n{"slug": "b", "title": "B"}\n'
    )


def test_truncate_manifest_restores_recorded_byte_length(knowledge_tree):
    append_manifest_row(knowledge_tree.paths, {"slug": "a"})
    before = knowledge_tree.manifest.read_bytes()
    mark = mark_manifest(knowledge_tree.paths)
    append_manifest_row(knowledge_tree.paths, {"slug": "b"})

    roll_back_manifest(knowledge_tree.paths, mark)
    assert knowledge_tree.manifest.read_bytes() == before


def test_rolling_back_to_a_mark_taken_with_no_manifest_removes_it(knowledge_tree):
    mark = mark_manifest(knowledge_tree.paths)
    append_manifest_row(knowledge_tree.paths, {"slug": "a"})

    roll_back_manifest(knowledge_tree.paths, mark)
    assert not knowledge_tree.manifest.exists()


def test_rolling_back_before_anything_was_written_leaves_no_manifest(knowledge_tree):
    roll_back_manifest(knowledge_tree.paths, mark_manifest(knowledge_tree.paths))
    assert not knowledge_tree.manifest.exists()


def test_rewriting_without_a_slug_keeps_every_other_line_byte_identical(knowledge_tree):
    original = b'{"slug": "a",  "x": 1}\n{"slug":"b"}\n\n{"title": "\\u00e9", "slug": "c"}\n'
    knowledge_tree.manifest.write_bytes(original)

    write_manifest_without(knowledge_tree.paths, "b", original)
    assert knowledge_tree.manifest.read_bytes() == (
        b'{"slug": "a",  "x": 1}\n\n{"title": "\\u00e9", "slug": "c"}\n'
    )


def test_first_matching_row_is_the_first_in_file_order(knowledge_tree):
    for slug in ("a", "b", "c"):
        append_manifest_row(knowledge_tree.paths, {"slug": slug, "even": slug != "b"})
    match = first_matching_row(knowledge_tree.paths, lambda row: row["even"])
    assert match == {"slug": "a", "even": True}
    assert first_matching_row(knowledge_tree.paths, lambda row: row["slug"] == "z") is None

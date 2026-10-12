"""The index: block rendering, where new blocks go, and how the parser bounds entries.

Placement tests run on the index `init` ships, which has the other anchor and
commented examples. Byte-exact expectations live in `test_golden_shapes.py`.
"""

import re
from datetime import date
from pathlib import Path

import pytest

from agentic_mbse.research.index import (
    blocks_titled,
    insert_block,
    parse_index,
    render_batch_block,
    render_seam_block,
    with_block_inserted,
    with_block_replaced,
    without_block,
)

GOLDEN_INDEX = Path(__file__).parent / "golden" / "index"

SEAM = dict(
    title="Coil Note",
    slug="coil_note",
    source_kind="url",
    origin="http://127.0.0.1:1/coil.html",
    use_for="Winding-pack current density for the widget arm.",
    validation="Cross-check the current against Fig. 1 of the source.",
    caveat="Conference preprint; not peer reviewed.",
    source_id="e" * 64,
    raw_artifact_sha256="f" * 64,
    extract_sha256="0" * 64,
    added=date(2026, 10, 12),
)

BATCH = dict(
    title="Batch Paper",
    slug="batch_paper",
    key_label="Catalog Key",
    key_display="lib:ABC123",
    source_id="a" * 64,
    extract_sha256="b" * 64,
    added=date(2026, 10, 12),
)

FIELD_RE = re.compile(r"^- \*\*(?P<name>[^*]+)\*\*:", re.MULTILINE)


def _entry(title: str, location: str, *, extra: str = "") -> str:
    return (
        f"### {title}\n- **Type**: reference\n- **Location**: {location}\n"
        f"- **Use for**: Testing.\n- **Validation**: N/A{extra}"
    )


# --- rendering -----------------------------------------------------------------


@pytest.mark.parametrize("blank", ["use_for", "validation", "caveat"])
def test_seam_block_refuses_blank_prose_fields(blank):
    with pytest.raises(ValueError, match=blank):
        render_seam_block(**SEAM | {blank: "  "})


def test_seam_block_refuses_a_blank_origin():
    with pytest.raises(ValueError, match="origin"):
        render_seam_block(**SEAM | {"origin": " "})


def test_seam_block_field_order():
    assert FIELD_RE.findall(render_seam_block(**SEAM)) == [
        "Type",
        "Location",
        "Use for",
        "Validation",
        "Caveat",
        "Source URL",
        "Source ID",
        "Raw SHA256",
        "Raw Artifact SHA256",
        "Extracted Path",
        "Extract SHA256",
        "Date Added",
    ]


def test_local_pdf_seam_block_uses_origin_path():
    block = render_seam_block(
        **SEAM | {"source_kind": "local_pdf", "origin": "inbox/coil_note.pdf"}
    )
    assert "- **Origin Path**: inbox/coil_note.pdf" in block
    assert "Source URL" not in FIELD_RE.findall(block)


# --- placement -------------------------------------------------------------------


def test_a_block_lands_before_the_shipped_index_anchor(knowledge_tree):
    insert_block(knowledge_tree.index, render_seam_block(**SEAM))
    body = knowledge_tree.index.read_text()
    assert body.index("## Primary Sources") < body.index("### Coil Note")
    assert body.index("### Coil Note") < body.index("## How This File Is Used")


def test_a_batch_block_also_lands_before_the_anchor(knowledge_tree):
    insert_block(knowledge_tree.index, render_batch_block(**BATCH))
    body = knowledge_tree.index.read_text()
    assert body.index("### Batch Paper") < body.index("## How This File Is Used")


@pytest.mark.parametrize(
    "anchors",
    [
        ("## How Sources Are Used", "## How This File Is Used"),
        ("## How This File Is Used", "## How Sources Are Used"),
    ],
)
def test_the_block_goes_before_whichever_anchor_comes_first(anchors):
    first, second = anchors
    text = f"# Source Index\n\n## Primary Sources\n\n{first}\n\nOne.\n\n{second}\n\nTwo.\n"
    body = with_block_inserted(text, "### New\n- **Type**: reference")
    assert body.index("### New") < body.index(first) < body.index(second)


def test_without_either_anchor_the_block_is_appended_at_the_end():
    text = "# Source Index\n\n## Primary Sources\n"
    assert with_block_inserted(text, "### New") == text + "### New\n"


def test_an_anchor_inside_a_comment_is_not_where_blocks_go():
    text = (
        "# Source Index\n\n<!--\n## How Sources Are Used\n-->\n\n"
        "## Primary Sources\n\n## How This File Is Used\n"
    )
    body = with_block_inserted(text, "### New")
    assert body.index("-->") < body.index("### New") < body.index("## How This File Is Used")


def test_two_blocks_stack_in_write_order(knowledge_tree):
    insert_block(knowledge_tree.index, render_seam_block(**SEAM))
    insert_block(
        knowledge_tree.index, render_seam_block(**SEAM | {"title": "Second", "slug": "second"})
    )
    body = knowledge_tree.index.read_text()
    assert (
        body.index("### Coil Note")
        < body.index("### Second")
        < body.index("## How This File Is Used")
    )


@pytest.mark.parametrize(
    ("case", "block", "restored_suffix"),
    [
        ("anchor_how_sources", "block.md", ""),
        ("anchor_how_sources", "batch_block.md", ""),
        ("anchor_how_this_file", "block.md", ""),
        ("eof_newline", "block.md", ""),
        ("eof_no_newline", "block.md", "\n"),
    ],
)
def test_an_inserted_block_spans_exactly_what_was_inserted(case, block, restored_suffix, tmp_path):
    before = (GOLDEN_INDEX / f"{case}.before.md").read_text()
    block_text = (GOLDEN_INDEX / block).read_text()
    after = with_block_inserted(before, block_text)

    (inserted,) = blocks_titled(
        parse_index(after, project_root=tmp_path), block_text.splitlines()[0][4:]
    )
    assert inserted.text == block_text
    assert without_block(after, inserted) == before + restored_suffix


# --- parsing ---------------------------------------------------------------------


def test_the_shipped_templates_commented_examples_are_not_entries(knowledge_tree):
    assert (
        parse_index(knowledge_tree.index.read_text(), project_root=knowledge_tree.root.parent) == []
    )


def test_a_block_reads_its_title_type_location_and_slug(tmp_path):
    text = (
        "## Primary Sources\n\n" + _entry("  Widget Note ", "knowledge/sources/widget_note/") + "\n"
    )
    (block,) = parse_index(text, project_root=tmp_path)
    assert (block.title, block.type, block.location, block.slug) == (
        "Widget Note",
        "reference",
        "knowledge/sources/widget_note/",
        "widget_note",
    )


def test_a_block_without_a_location_has_none(tmp_path):
    (block,) = parse_index("### Bare\n- **Type**: reference\n", project_root=tmp_path)
    assert (block.location, block.slug) == (None, None)


def test_a_block_ends_at_the_next_heading_of_any_level(tmp_path):
    text = _entry("A", "a") + "\n\n# Top\n\n" + _entry("B", "b") + "\n\n## Next\n"
    a, b = parse_index(text, project_root=tmp_path)
    assert text[a.start : a.end] == _entry("A", "a") + "\n\n"
    assert text[b.start : b.end] == _entry("B", "b") + "\n\n"


def test_an_extended_metadata_subheading_stays_inside_its_block(tmp_path):
    text = render_seam_block(**SEAM) + "\n\n## How Sources Are Used\n"
    (block,) = parse_index(text, project_root=tmp_path)
    assert block.text == render_seam_block(**SEAM)


def test_a_block_ends_where_a_comment_opens(knowledge_tree):
    """A hand-placed entry above the template's commented examples leaves them behind when cut."""
    template = knowledge_tree.index.read_text()
    heading = "## Primary Sources\n\n"
    entry = _entry("Hand Placed", "/opt/reference/code") + "\n\n"
    text = template.replace(heading, heading + entry, 1)

    (block,) = parse_index(text, project_root=knowledge_tree.root.parent)
    assert text[block.end :].startswith("<!-- Add your domain sources below.")
    assert without_block(text, block) == template


def test_a_comment_opened_mid_line_stays_inside_its_block(tmp_path):
    entry = _entry("A", "a", extra=" <!-- checked 2026-10 -->\n- **Caveat**: Old.")
    text = entry + "\n\n## Next\n"
    (block,) = parse_index(text, project_root=tmp_path)
    assert block.text == entry


def test_an_unclosed_comment_hides_everything_after_it(tmp_path):
    text = _entry("A", "a") + "\n\n<!--\n" + _entry("B", "b") + "\n"
    (block,) = parse_index(text, project_root=tmp_path)
    assert block.title == "A"


def test_offsets_hold_after_a_comment(tmp_path):
    """Masking a comment must not shift where later blocks start or what their text is."""
    comment = "<!-- an ünïcode comment\n### Not An Entry\n-->\n\n"
    entry = render_seam_block(**SEAM)
    text = "## Primary Sources\n\n" + comment + entry + "\n\n## How Sources Are Used\n"
    (block,) = parse_index(text, project_root=tmp_path)
    assert block.start == text.index("### Coil Note")
    assert block.text == entry


def test_fields_inside_a_comment_are_not_read(tmp_path):
    # The comment opens mid-line, so the block runs past it; its Location line is hidden.
    text = "### A\nNote <!-- moved from\n- **Location**: knowledge/sources/old/ -->\n- **Location**: elsewhere\n"
    (block,) = parse_index(text, project_root=tmp_path)
    assert block.location == "elsewhere"


# --- Locations -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("written", "location", "slug"),
    [
        ("knowledge/sources/x/", "knowledge/sources/x/", "x"),
        ("./knowledge/sources/x/", "knowledge/sources/x/", "x"),
        ("  knowledge/sources/x/  ", "knowledge/sources/x/", "x"),
        ("knowledge/sources/x", "knowledge/sources/x", "x"),
        ("knowledge/sources/x/ (two extractions)", "knowledge/sources/x/ (two extractions)", "x"),
        ("{root}/knowledge/sources/x/", "knowledge/sources/x/", "x"),
        ("/elsewhere/knowledge/sources/x/", "/elsewhere/knowledge/sources/x/", None),
        (
            "https://example.org/knowledge/sources/x/",
            "https://example.org/knowledge/sources/x/",
            None,
        ),
        ("data/documents/spec.pdf", "data/documents/spec.pdf", None),
        ("knowledge/sources/", "knowledge/sources/", None),
    ],
)
def test_locations_are_normalized_before_the_sources_check(written, location, slug, tmp_path):
    text = _entry("A", written.format(root=tmp_path.resolve())) + "\n"
    (block,) = parse_index(text, project_root=tmp_path)
    assert (block.location, block.slug) == (location, slug)


# --- titles and rewrites ---------------------------------------------------------


def test_titles_match_exactly_after_stripping_whitespace(tmp_path):
    text = _entry("Widget Note", "a") + "\n\n" + _entry("Widget Notes", "b") + "\n"
    blocks = parse_index(text, project_root=tmp_path)
    assert [b.location for b in blocks_titled(blocks, "  Widget Note ")] == ["a"]
    assert blocks_titled(blocks, "widget note") == []


def test_replacing_a_block_keeps_what_followed_it(tmp_path):
    text = "## Primary Sources\n\n" + _entry("A", "a") + "\n\n## How This File Is Used\n"
    (block,) = parse_index(text, project_root=tmp_path)
    replaced = with_block_replaced(text, block, _entry("A", "b"))
    assert replaced == text.replace("- **Location**: a", "- **Location**: b")

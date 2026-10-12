"""`SOURCE_INDEX.md`: parsing its `###` entries, rendering registry blocks, and placing them.

An entry is a `###` block. HTML comments are invisible to the parser: a heading
inside `<!-- -->` is not an entry, so a template's commented examples never list
as sources. A block runs from its heading to the next heading outside a comment,
or to the next line that opens a comment, whichever comes first, so cutting a
block never cuts a comment that follows it.
"""

from __future__ import annotations

import bisect
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

#: Headings that mark where registered entries end. A new block goes before the first.
ANCHOR_HEADINGS = ("## How Sources Are Used", "## How This File Is Used")

#: Where registered sources live, as a normalized Location spells it.
SOURCES_PREFIX = "knowledge/sources/"

_HEADING_RE = re.compile(r"^(?:### |## |# )", re.MULTILINE)
_BLOCK_HEADING_RE = re.compile(r"^### (?P<title>.*)$", re.MULTILINE)
_ANCHOR_RE = re.compile("^(?:" + "|".join(map(re.escape, ANCHOR_HEADINGS)) + ")", re.MULTILINE)
_COMMENT_RE = re.compile(r"<!--.*?(?:-->|\Z)", re.DOTALL)
_FIELD_RE = re.compile(r"^- \*\*(?P<name>[^*]+)\*\*:(?P<value>.*)$", re.MULTILINE)
_SLUG_RE = re.compile(re.escape(SOURCES_PREFIX) + r"(?P<slug>[^/\s]+)")

_ORIGIN_LABELS = {"url": "Source URL", "local_pdf": "Origin Path"}


@dataclass(frozen=True)
class IndexBlock:
    """One `###` entry of the index.

    `start` and `end` bound its span in the file, trailing blank lines included,
    so removing the span leaves the file as it was before the block was inserted.
    `text` is the span without its trailing newlines: the block exactly as its
    writer wrote it. `location` is normalized, and `slug` is the first path
    segment under `knowledge/sources/`, if the location is there.
    """

    start: int
    end: int
    text: str
    title: str
    type: str | None
    location: str | None
    slug: str | None


def parse_index(index_text: str, *, project_root: Path) -> list[IndexBlock]:
    """Every `###` entry outside an HTML comment, in file order."""
    comments = _comment_spans(index_text)
    masked = _masked(index_text, comments)
    boundaries = sorted(
        {match.start() for match in _HEADING_RE.finditer(masked)}
        | {start for start, _ in comments if _at_line_start(index_text, start)}
    )
    blocks = []
    for heading in _BLOCK_HEADING_RE.finditer(masked):
        start = heading.start()
        following = bisect.bisect_right(boundaries, start)
        end = boundaries[following] if following < len(boundaries) else len(index_text)
        fields = _first_fields(index_text, masked, start, end)
        location = (
            normalize_location(fields["Location"], project_root) if "Location" in fields else None
        )
        blocks.append(
            IndexBlock(
                start=start,
                end=end,
                text=index_text[start:end].rstrip("\n"),
                title=index_text[heading.start("title") : heading.end("title")].strip(),
                type=fields.get("Type"),
                location=location,
                slug=_slug_of(location),
            )
        )
    return blocks


def normalize_location(location: str, project_root: Path) -> str:
    """The Location as the registry compares it.

    Surrounding whitespace and a leading `./` are dropped, and an absolute path
    under the project root becomes relative to it. Anything else is unchanged.
    """
    normalized = location.strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    candidate = Path(normalized)
    root = project_root.resolve()
    if candidate.is_absolute() and candidate.is_relative_to(root):
        relative = candidate.relative_to(root).as_posix()
        if normalized.endswith("/"):
            relative += "/"
        normalized = relative
    return normalized


def blocks_titled(blocks: Sequence[IndexBlock], title: str) -> list[IndexBlock]:
    """The blocks whose title equals `title`, ignoring surrounding whitespace."""
    wanted = title.strip()
    return [block for block in blocks if block.title == wanted]


def with_block_inserted(index_text: str, block: str) -> str:
    """`index_text` with `block` placed where new entries go.

    Before the first anchor heading outside a comment, the block is inserted as
    `<block>\\n\\n` at the start of the anchor's line. With no anchor it is
    appended as `<block>\\n`, after a newline if the text does not end with one.
    """
    anchor = _ANCHOR_RE.search(_masked(index_text, _comment_spans(index_text)))
    if anchor is not None:
        at = anchor.start()
        return index_text[:at] + block + "\n\n" + index_text[at:]
    separator = "\n" if index_text and not index_text.endswith("\n") else ""
    return index_text + separator + block + "\n"


def insert_block(index_path: Path, block: str) -> None:
    """Rewrite the index file with `block` placed where new entries go."""
    text = index_path.read_text(encoding="utf-8")
    index_path.write_text(with_block_inserted(text, block), encoding="utf-8")


def without_block(index_text: str, block: IndexBlock) -> str:
    """`index_text` with the block's span cut out and everything else untouched."""
    return index_text[: block.start] + index_text[block.end :]


def with_block_replaced(index_text: str, block: IndexBlock, new_block: str) -> str:
    """`index_text` with the block's text replaced by `new_block`, keeping what followed it."""
    return index_text[: block.start] + new_block + index_text[block.start + len(block.text) :]


def render_seam_block(
    *,
    title: str,
    slug: str,
    source_kind: Literal["url", "local_pdf"],
    origin: str,
    use_for: str,
    validation: str,
    caveat: str,
    source_id: str,
    raw_artifact_sha256: str,
    extract_sha256: str,
    added: date,
) -> str:
    """The index block for a source an agent or operator registered, with its prose and provenance.

    `origin` is the URL for a `url` source and the input path for a `local_pdf`
    one. The raw SHA-256 is the source id: a source's identity is the digest of
    its raw bytes as fetched. Raises ValueError when a prose field or the origin
    is blank.
    """
    blank = [
        name
        for name, value in (("use_for", use_for), ("validation", validation), ("caveat", caveat))
        if not value.strip()
    ]
    if blank:
        raise ValueError("seam-profile index block requires non-empty " + ", ".join(blank))
    if not origin.strip():
        raise ValueError("seam-profile index block requires an origin")
    return "\n".join(
        [
            f"### {title}",
            f"- **Type**: {source_kind}",
            f"- **Location**: {SOURCES_PREFIX}{slug}/",
            f"- **Use for**: {use_for}",
            f"- **Validation**: {validation}",
            f"- **Caveat**: {caveat}",
            "",
            "#### Extended Metadata",
            f"- **{_ORIGIN_LABELS[source_kind]}**: {origin}",
            f"- **Source ID**: {source_id}",
            f"- **Raw SHA256**: {source_id}",
            f"- **Raw Artifact SHA256**: {raw_artifact_sha256}",
            f"- **Extracted Path**: {SOURCES_PREFIX}{slug}/",
            f"- **Extract SHA256**: {extract_sha256}",
            f"- **Date Added**: {added.isoformat()}",
        ]
    )


def render_batch_block(
    *,
    title: str,
    slug: str,
    key_label: str,
    key_display: str,
    source_id: str,
    extract_sha256: str,
    added: date,
) -> str:
    """The index block for a keyed source a batch caller registered.

    Use for and Validation stay empty: a batch caller has no per-item prose. The
    key appears as `- **<key_label>**: <key_display>`, and the source id as the
    Raw SHA256.
    """
    return "\n".join(
        [
            f"### {title}",
            "- **Type**: documentation",
            f"- **Location**: {SOURCES_PREFIX}{slug}/",
            "- **Use for**:",
            "- **Validation**:",
            "",
            "#### Extended Metadata",
            f"- **{key_label}**: {key_display}",
            f"- **Raw SHA256**: {source_id}",
            f"- **Extracted Path**: {SOURCES_PREFIX}{slug}/",
            f"- **Extract SHA256**: {extract_sha256}",
            f"- **Date Added**: {added.isoformat()}",
        ]
    )


def _comment_spans(text: str) -> list[tuple[int, int]]:
    """Every HTML comment's span. An unclosed comment runs to the end of the text."""
    return [(match.start(), match.end()) for match in _COMMENT_RE.finditer(text)]


def _masked(text: str, spans: Sequence[tuple[int, int]]) -> str:
    """`text` with each span blanked to spaces, newlines kept, so every offset still holds."""
    pieces = []
    cursor = 0
    for start, end in spans:
        pieces.append(text[cursor:start])
        pieces.append(re.sub(r"[^\n]", " ", text[start:end]))
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


def _at_line_start(text: str, offset: int) -> bool:
    return offset == 0 or text[offset - 1] == "\n"


def _first_fields(text: str, masked: str, start: int, end: int) -> dict[str, str]:
    """Each `- **Name**: value` field's first value in `text[start:end]`, ignoring comments."""
    fields: dict[str, str] = {}
    for match in _FIELD_RE.finditer(masked, start, end):
        name = match.group("name")
        if name not in fields:
            fields[name] = text[match.start("value") : match.end("value")].strip()
    return fields


def _slug_of(location: str | None) -> str | None:
    if location is None:
        return None
    match = _SLUG_RE.match(location)
    return match.group("slug") if match else None

"""`SOURCE_INDEX.md`: parsing its `###` entries, rendering blocks, placing them, and hand-curated entries.

An entry is a `###` block. HTML comments are invisible to the parser: a heading
inside `<!-- -->` is not an entry, so a template's commented examples never list
as sources. A block runs from its heading to the next heading outside a comment,
or to the next line that opens a comment, whichever comes first, so cutting a
block never cuts a comment that follows it.

An entry whose Location names a directory under `knowledge/sources/` belongs to
the registry: `register` writes it and `retire` removes it. Every other entry is
hand-curated, a source the registry cannot capture, such as a codebase or a
book. `add_entry`, `replace_entry` and `remove_entry` are its only writers.
"""

from __future__ import annotations

import bisect
import dataclasses
import re
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from agentic_mbse.research.holdout import (
    HoldoutGuard,
    HoldoutGuardError,
    HoldoutHit,
    first_term_hit,
    input_path_hit,
    load_holdout_guard,
)
from agentic_mbse.research.manifest import load_manifest_rows
from agentic_mbse.research.paths import RegistryPaths, default_paths, registry_lock

#: Headings that mark where registered entries end. A new block goes before the first.
ANCHOR_HEADINGS = ("## How Sources Are Used", "## How This File Is Used")

#: Where registered sources live, as a normalized Location spells it.
SOURCES_PREFIX = "knowledge/sources/"

#: The types a hand-curated entry may have. Registered types are the registry's to write.
HAND_CURATED_TYPES = ("codebase", "documentation", "database", "reference")

EntryLabel = Literal["registered", "hand-curated", "unregistered"]
EntryOutcome = Literal["added", "replaced", "removed", "holdout_hit", "precondition_failed"]

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


@dataclass(frozen=True)
class HandCuratedEntry:
    """A source described by hand, with the four fields every entry carries."""

    title: str
    type: str
    location: str
    use_for: str
    validation: str


@dataclass(frozen=True)
class ListedEntry:
    """One index entry as `sources` lists it.

    `registered` and `unregistered` entries locate a directory under
    `knowledge/sources/`, with and without a manifest row behind it; every other
    entry is `hand-curated`.
    """

    label: EntryLabel
    title: str
    type: str | None
    location: str | None


@dataclass(frozen=True)
class EntryResult:
    """What one hand-curated write came to. Only `added`, `replaced` and `removed` wrote anything.

    `holdout_hit` carries the rule that fired and where. Every refusal carries a
    one-line reason.
    """

    outcome: EntryOutcome
    reason: str = ""
    rule_id: str | None = None
    offsets: tuple[int, ...] = ()


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


def render_hand_curated_block(entry: HandCuratedEntry) -> str:
    """The index block for a hand-curated entry: its title and its four fields, as written."""
    return "\n".join(
        [
            f"### {entry.title}",
            f"- **Type**: {entry.type}",
            f"- **Location**: {entry.location}",
            f"- **Use for**: {entry.use_for}",
            f"- **Validation**: {entry.validation}",
        ]
    )


def entry_label(block: IndexBlock, registered_slugs: Collection[str]) -> EntryLabel:
    """`hand-curated` outside `knowledge/sources/`; there, `registered` when a row carries the slug."""
    if block.slug is None:
        return "hand-curated"
    return "registered" if block.slug in registered_slugs else "unregistered"


# --- hand-curated entries ------------------------------------------------------------
#
# Each write is a read-modify-write of the index under the registry lock, so it
# cannot lose a registration's write or lose its own to one. An addition passes
# the same hold-out guard a registration does.


def list_entries(paths: RegistryPaths) -> list[ListedEntry]:
    """Every entry of the index, in file order, labelled. Reads without the lock and writes nothing."""
    registered = {row["slug"] for row in load_manifest_rows(paths) if "slug" in row}
    index_text = paths.index.read_text(encoding="utf-8")
    return [
        ListedEntry(
            label=entry_label(block, registered),
            title=block.title,
            type=block.type,
            location=block.location,
        )
        for block in parse_index(index_text, project_root=paths.project_root)
    ]


def add_entry(
    entry: HandCuratedEntry,
    *,
    paths: RegistryPaths | None = None,
    guard: HoldoutGuard | None = None,
) -> EntryResult:
    """Add a hand-curated entry where new entries go.

    Refuses with nothing written when a field is blank, spans lines or opens an
    HTML comment, the type is not a hand-curated type, the Location is under
    `knowledge/sources/`, the index is missing, the guard bars the entry or
    cannot answer, or a hand-curated entry already has the title. A registered
    entry may share it. Fields are written stripped, with the Location
    normalized. `paths` and `guard` default as `register`'s do.
    """
    paths = paths if paths is not None else default_paths()
    guard = guard if guard is not None else load_holdout_guard(paths.project_root)
    entry = _cleaned(entry, paths.project_root)
    refusal = _entry_refusal(entry, paths=paths, guard=guard)
    if refusal is not None:
        return refusal
    with registry_lock(paths):
        index_text = paths.index.read_text(encoding="utf-8")
        if _hand_curated(_titled(index_text, entry.title, paths)):
            return _entry_refused(
                f"a hand-curated entry titled {entry.title!r} already exists; replace it instead"
            )
        paths.index.write_text(
            with_block_inserted(index_text, render_hand_curated_block(entry)), encoding="utf-8"
        )
    return EntryResult(outcome="added")


def replace_entry(
    entry: HandCuratedEntry,
    *,
    paths: RegistryPaths | None = None,
    guard: HoldoutGuard | None = None,
) -> EntryResult:
    """Rewrite the one hand-curated entry titled as `entry` is, in place.

    Refuses as `add_entry` does, except on the title: exactly one hand-curated
    entry must have it.
    """
    paths = paths if paths is not None else default_paths()
    guard = guard if guard is not None else load_holdout_guard(paths.project_root)
    entry = _cleaned(entry, paths.project_root)
    refusal = _entry_refusal(entry, paths=paths, guard=guard)
    if refusal is not None:
        return refusal
    with registry_lock(paths):
        index_text = paths.index.read_text(encoding="utf-8")
        titled = _titled(index_text, entry.title, paths)
        matches = _hand_curated(titled)
        if len(matches) != 1:
            return _not_exactly_one(entry.title, titled)
        paths.index.write_text(
            with_block_replaced(index_text, matches[0], render_hand_curated_block(entry)),
            encoding="utf-8",
        )
    return EntryResult(outcome="replaced")


def remove_entry(title: str, *, paths: RegistryPaths | None = None) -> EntryResult:
    """Cut the one hand-curated entry titled `title` out of the index, leaving every other byte.

    Refuses with nothing written when the title is blank, the index is missing,
    or not exactly one hand-curated entry has the title. A registered entry is
    removed with `retire`, never here.
    """
    paths = paths if paths is not None else default_paths()
    wanted = title.strip()
    if not wanted:
        return _entry_refused("caller must supply non-empty title")
    if not paths.index.is_file():
        return _entry_refused(f"source index missing: {paths.index}")
    with registry_lock(paths):
        index_text = paths.index.read_text(encoding="utf-8")
        titled = _titled(index_text, wanted, paths)
        matches = _hand_curated(titled)
        if len(matches) != 1:
            return _not_exactly_one(wanted, titled)
        paths.index.write_text(without_block(index_text, matches[0]), encoding="utf-8")
    return EntryResult(outcome="removed")


def _cleaned(entry: HandCuratedEntry, project_root: Path) -> HandCuratedEntry:
    """The entry with every field stripped and the Location normalized."""
    return HandCuratedEntry(
        title=entry.title.strip(),
        type=entry.type.strip(),
        location=normalize_location(entry.location, project_root),
        use_for=entry.use_for.strip(),
        validation=entry.validation.strip(),
    )


def _entry_refusal(
    entry: HandCuratedEntry, *, paths: RegistryPaths, guard: HoldoutGuard
) -> EntryResult | None:
    """The first reason a cleaned entry may not be written, checked before the lock. None means go on."""
    fields = dataclasses.asdict(entry)
    blank = [name for name, value in fields.items() if not value]
    if blank:
        return _entry_refused(f"caller must supply non-empty {', '.join(blank)}")
    # A line break or a comment opener would end the block early, or hide what follows it.
    unwritable = [name for name, value in fields.items() if _breaks_a_block(value)]
    if unwritable:
        return _entry_refused(
            f"{', '.join(unwritable)} must be one line and must not open an HTML comment"
        )
    if entry.type not in HAND_CURATED_TYPES:
        return _entry_refused(
            f"type {entry.type!r} is not a hand-curated type; use one of "
            + ", ".join(HAND_CURATED_TYPES)
        )
    if _slug_of(entry.location) is not None:
        return _entry_refused(
            f"location {entry.location} is under {SOURCES_PREFIX}, which only register "
            "writes; register the source instead"
        )
    if not paths.index.is_file():
        return _entry_refused(f"source index missing: {paths.index}")

    try:
        hit = _entry_holdout_hit(entry, guard)
    except HoldoutGuardError as fault:
        return _entry_refused(str(fault))
    if hit is not None:
        return EntryResult(
            outcome="holdout_hit",
            reason=f"{hit.rule_id} matched {hit.count}x",
            rule_id=hit.rule_id,
            offsets=hit.offsets,
        )
    return None


def _breaks_a_block(value: str) -> bool:
    return "\n" in value or "\r" in value or "<!--" in value


def _entry_holdout_hit(entry: HandCuratedEntry, guard: HoldoutGuard) -> HoldoutHit | None:
    """Check the Location as an input path unless it is a URL, then scan each field's text."""
    if not _is_url(entry.location):
        hit = input_path_hit(guard, Path(entry.location))
        if hit is not None:
            return hit
    for text in (entry.title, entry.location, entry.use_for, entry.validation):
        hit = first_term_hit(guard, text)
        if hit is not None:
            return hit
    return None


def _is_url(location: str) -> bool:
    parts = urlsplit(location)
    return bool(parts.scheme and parts.netloc)


def _titled(index_text: str, title: str, paths: RegistryPaths) -> list[IndexBlock]:
    return blocks_titled(parse_index(index_text, project_root=paths.project_root), title)


def _hand_curated(blocks: Sequence[IndexBlock]) -> list[IndexBlock]:
    return [block for block in blocks if block.slug is None]


def _not_exactly_one(title: str, titled: Sequence[IndexBlock]) -> EntryResult:
    """The refusal when the blocks titled `title` hold no hand-curated entry, or more than one."""
    matches = _hand_curated(titled)
    if matches:
        return _entry_refused(
            f"{len(matches)} hand-curated entries are titled {title!r}; "
            "tell them apart in the index first"
        )
    reason = f"no hand-curated entry titled {title!r}"
    if titled:
        reason += f"; the entry with that title is under {SOURCES_PREFIX}, so retire it by its slug"
    return _entry_refused(reason)


def _entry_refused(reason: str) -> EntryResult:
    return EntryResult(outcome="precondition_failed", reason=reason)


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

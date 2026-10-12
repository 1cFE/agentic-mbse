"""`retire`: the one door a registered source leaves by.

Removes one entry's four artifacts together, or nothing: its manifest row, its
index block, its source directory, and the raw copy it owns. A completed removal
leaves one line in `RETIRED.jsonl`, so `verify` expects the slug absent from then
on and reports any of its artifacts that comes back.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

from agentic_mbse.research.holdout import (
    HoldoutGuard,
    HoldoutGuardError,
    HoldoutHit,
    first_term_hit,
    input_path_hit,
    load_holdout_guard,
)
from agentic_mbse.research.index import SOURCES_PREFIX, IndexBlock, parse_index, without_block
from agentic_mbse.research.manifest import Row, load_manifest_rows, write_manifest_without
from agentic_mbse.research.paths import RegistryPaths, default_paths, registry_lock

Outcome = Literal["retired", "unknown_slug", "holdout_hit", "referenced", "precondition_failed"]

#: A registry slug: one path segment, so it can name nothing outside `knowledge/sources/`.
SLUG_RE = re.compile(r"[A-Za-z0-9_]+")

#: The registry's directory as a project's hold-out globs spell it. The guard checks
#: this literal path, not the tree's own, so a barred slug refuses whatever tree it
#: is retired from.
CANONICAL_SOURCES = Path("knowledge/sources")


class RetirementError(RuntimeError):
    """A removal rung failed. Everything the attempt moved or rewrote has already been put back."""


class Removed(TypedDict):
    """What a retirement removed, as the CLI reports it."""

    manifest_row: Row
    index_block: str
    source_dir: str
    raw_copy: str | None


class RetiredLine(TypedDict):
    """One `RETIRED.jsonl` line: the removed row verbatim, and the hash of the removed block."""

    slug: str
    retired_at: str
    reason: str
    index_block_sha256: str
    row: Row


@dataclass(frozen=True)
class RetirementResult:
    """What one retirement attempt came to.

    `retired` is the only outcome that wrote anything, and carries what it
    removed and the line it recorded. `holdout_hit` carries the rule that fired,
    and `referenced` the entries that depend on the slug. Every refusal carries a
    one-line reason.
    """

    outcome: Outcome
    reason: str = ""
    slug: str | None = None
    removed: Removed | None = None
    retired_line: RetiredLine | None = None
    rule_id: str | None = None
    offsets: tuple[int, ...] = ()
    references: tuple[str, ...] = ()


def retire(
    slug: str,
    reason: str,
    *,
    paths: RegistryPaths | None = None,
    guard: HoldoutGuard | None = None,
) -> RetirementResult:
    """Remove one registered entry's row, block, directory and raw copy, or nothing.

    Refuses with nothing written when the reason is blank, the guard bars the
    slug or cannot answer, the slug is not a registry slug, no manifest row
    carries it, its block or directory cannot be identified (that is drift: run
    `verify`), or another entry depends on it. Raises `RetirementError` when a
    removal rung failed, with everything put back.

    A line in another entry that says it supersedes the retiree is the
    announcement that the retiree was replaced, so it does not block. Any other
    mention of the slug by another entry does.

    The `RETIRED.jsonl` line holds the removed row verbatim, `retired_at`, the
    reason, and the SHA-256 of the removed block as its writer wrote it (heading
    through last line, no trailing newline). `paths` and `guard` default as
    `register`'s do.
    """
    paths = paths if paths is not None else default_paths()
    guard = guard if guard is not None else load_holdout_guard(paths.project_root)
    with registry_lock(paths):
        refusal = _retire_refusal(slug, reason, paths=paths, guard=guard)
        if refusal is not None:
            return refusal
        return _remove(slug, reason, paths)


# --- refusals ----------------------------------------------------------------------


def _retire_refusal(
    slug: str, reason: str, *, paths: RegistryPaths, guard: HoldoutGuard
) -> RetirementResult | None:
    """Everything checkable before a byte moves, cheapest first. None means go on."""
    if not reason.strip():
        return _precondition_failed("caller must supply a non-empty reason")

    # The guard sees the slug before its shape is checked, so a barred path handed in
    # as a slug refuses as a hold-out hit.
    try:
        hit = _slug_holdout_hit(slug, guard)
    except HoldoutGuardError as fault:
        return _precondition_failed(str(fault))
    if hit is not None:
        return RetirementResult(
            outcome="holdout_hit",
            reason=f"{hit.rule_id} matched {hit.count}x",
            rule_id=hit.rule_id,
            offsets=hit.offsets,
        )

    if not SLUG_RE.fullmatch(slug):
        return _precondition_failed(f"not a registry slug: {slug!r}")

    rows = load_manifest_rows(paths)
    carrying = [row for row in rows if row.get("slug") == slug]
    if not carrying:
        return RetirementResult(
            outcome="unknown_slug", reason=f"no manifest row carries slug {slug}"
        )
    if len(carrying) > 1:
        return _precondition_failed(
            f"{len(carrying)} manifest rows carry slug {slug}; "
            "run verify and resolve the drift first"
        )

    blocks = _index_blocks(paths)
    locating = [block for block in blocks if block.slug == slug]
    if len(locating) != 1:
        return _precondition_failed(
            f"{len(locating)} SOURCE_INDEX.md blocks locate {slug}; expected exactly one — "
            "run verify and resolve the drift first"
        )
    if not (paths.sources / slug).is_dir():
        return _precondition_failed(
            f"source directory {SOURCES_PREFIX}{slug}/ does not exist; run verify"
        )

    references = _references_to(slug, rows, blocks)
    if references:
        return RetirementResult(
            outcome="referenced",
            reason="another registry entry references this slug: " + "; ".join(references),
            slug=slug,
            references=tuple(references),
        )
    return None


def _slug_holdout_hit(slug: str, guard: HoldoutGuard) -> HoldoutHit | None:
    """The slug as a bare path, then as the registry path it names, then as text."""
    for candidate in (Path(slug), CANONICAL_SOURCES / slug):
        hit = input_path_hit(guard, candidate)
        if hit is not None:
            return hit
    return first_term_hit(guard, slug)


def _precondition_failed(reason: str) -> RetirementResult:
    return RetirementResult(outcome="precondition_failed", reason=reason)


def _index_blocks(paths: RegistryPaths) -> list[IndexBlock]:
    index_text = paths.index.read_text(encoding="utf-8") if paths.index.exists() else ""
    return parse_index(index_text, project_root=paths.project_root)


def _references_to(slug: str, rows: Sequence[Row], blocks: Sequence[IndexBlock]) -> list[str]:
    """Other entries that depend on `slug`, as `<where> (<their slug>)` labels.

    A mention on a line that says the other entry supersedes the retiree is a
    claim about it, not a dependency on it, and is left out. So is a row's
    `supersedes` field naming exactly the retiree.
    """
    mention = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(slug) + r"(?![A-Za-z0-9_])")
    supersedes = re.compile(r"\bsupersedes\b", re.IGNORECASE)
    found = []
    for row in rows:
        other = row.get("slug")
        if other == slug or other is None:
            continue
        for key, value in row.items():
            if key == "slug" or not isinstance(value, str) or not mention.search(value):
                continue
            if key == "supersedes" and value.strip() == slug:
                continue
            found.append(f"manifest row field {key} ({other})")
    for block in blocks:
        if block.slug == slug:
            continue
        for line in block.text.splitlines():
            hit = mention.search(line)
            if hit is None or supersedes.search(line[: hit.start()]):
                continue
            found.append(f"SOURCE_INDEX.md block ({block.slug or block.text.splitlines()[0]})")
            break
    return found


# --- removal, and the rollback that undoes it ----------------------------------------
#
# Each rung is a module-level name, so a test can make any one of them fail.


@dataclass(frozen=True)
class _Before:
    """The files a retirement rewrites, as they were: bytes to write back, and the log's length.

    `retired_length` is None when there was no `RETIRED.jsonl`.
    """

    manifest: bytes
    index: bytes
    retired_length: int | None


def _remove(slug: str, reason: str, paths: RegistryPaths) -> RetirementResult:
    """Park, rewrite, record, under the lock already held, or put everything back.

    The directory and the raw copy are parked in staging by rename, which is
    reversible, and deleted only after every rung succeeded. The manifest and the
    index are rewritten from byte snapshots that rollback writes straight back.
    The `RETIRED.jsonl` line goes last, so the durable record exists only for a
    removal that completed.
    """
    rows = load_manifest_rows(paths)
    row = next(r for r in rows if r.get("slug") == slug)
    index_text = paths.index.read_text(encoding="utf-8")
    block = next(
        b for b in parse_index(index_text, project_root=paths.project_root) if b.slug == slug
    )
    source_dir = paths.sources / slug
    raw_copy = _owned_raw_copy(row, rows, paths)
    before = _Before(
        manifest=paths.manifest.read_bytes(),
        index=paths.index.read_bytes(),
        retired_length=paths.retired.stat().st_size if paths.retired.exists() else None,
    )
    line: RetiredLine = {
        "slug": slug,
        "retired_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "index_block_sha256": hashlib.sha256(block.text.encode("utf-8")).hexdigest(),
        "row": row,
    }

    staging = paths.staging / uuid.uuid4().hex
    moves = [(source_dir, staging / "sources" / slug)]
    if raw_copy is not None:
        moves.append((raw_copy, staging / "raw" / raw_copy.name))
    parked: list[tuple[Path, Path]] = []
    try:
        for original, spot in moves:
            _park(original, spot)
            parked.append((original, spot))
        write_manifest_without(paths, slug, before.manifest)
        _write_index_without(paths, index_text, block)
        _append_retired_line(paths, line)
    except Exception as error:
        _roll_back(before, parked, paths)
        shutil.rmtree(staging, ignore_errors=True)
        raise RetirementError(f"retire failed for {slug}: {error}") from error

    shutil.rmtree(staging, ignore_errors=True)
    return RetirementResult(
        outcome="retired",
        slug=slug,
        removed={
            "manifest_row": row,
            "index_block": block.text,
            "source_dir": f"{SOURCES_PREFIX}{slug}/",
            "raw_copy": f"knowledge/raw/{raw_copy.name}" if raw_copy is not None else None,
        },
        retired_line=line,
    )


def _owned_raw_copy(row: Row, rows: Sequence[Row], paths: RegistryPaths) -> Path | None:
    """The `knowledge/raw/` copy this row alone owns, if the registry knows its name.

    Only a local-PDF row records the name its raw copy was stored under
    (`origin_path`). A keyed row records its key, not its file, so its raw copy
    stays where it is. A copy another row's origin also names is shared, and stays.
    """
    origin = row.get("origin_path")
    if not origin:
        return None
    name = Path(origin).name
    shared = any(
        other is not row and other.get("origin_path") and Path(other["origin_path"]).name == name
        for other in rows
    )
    candidate = paths.raw / name
    return candidate if candidate.is_file() and not shared else None


def _park(original: Path, spot: Path) -> None:
    """Rung one, per artifact: move it aside into staging, where rollback can move it back."""
    spot.parent.mkdir(parents=True, exist_ok=True)
    original.rename(spot)


def _write_index_without(paths: RegistryPaths, index_text: str, block: IndexBlock) -> None:
    """Rung three: cut the block's span out of the index, leaving every other byte."""
    paths.index.write_text(without_block(index_text, block), encoding="utf-8")


def _append_retired_line(paths: RegistryPaths, line: RetiredLine) -> None:
    """Rung four: record the removal."""
    with open(paths.retired, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(line) + "\n")
        handle.flush()


def _roll_back(before: _Before, parked: Sequence[tuple[Path, Path]], paths: RegistryPaths) -> None:
    """Undo the rungs in reverse: the log, the index, the manifest, then each parked artifact."""
    if before.retired_length is None:
        paths.retired.unlink(missing_ok=True)
    else:
        with open(paths.retired, "r+b") as handle:
            handle.truncate(before.retired_length)
    paths.index.write_bytes(before.index)
    paths.manifest.write_bytes(before.manifest)
    for original, spot in reversed(parked):
        spot.rename(original)

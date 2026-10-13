"""`MANIFEST.jsonl`: one JSON row per registered source, in registration order."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from agentic_mbse.research.paths import RegistryPaths

Row = dict[str, Any]


@dataclass(frozen=True)
class ManifestMark:
    """The manifest's state before an attempt: its byte length, or None if it did not exist."""

    byte_length: int | None


def load_manifest_rows(paths: RegistryPaths) -> list[Row]:
    """Every manifest row, in file order. No manifest means no rows."""
    if not paths.manifest.exists():
        return []
    return [
        json.loads(line)
        for line in paths.manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def first_matching_row(paths: RegistryPaths, matches: Callable[[Row], bool]) -> Row | None:
    """The first row, in file order, for which `matches` is true."""
    for row in load_manifest_rows(paths):
        if matches(row):
            return row
    return None


def append_manifest_row(paths: RegistryPaths, row: Row) -> None:
    """Append one row as one JSON line and flush it, creating the manifest if absent."""
    with open(paths.manifest, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")
        handle.flush()


def mark_manifest(paths: RegistryPaths) -> ManifestMark:
    """Record the manifest's state, to roll back to if an attempt fails."""
    if not paths.manifest.exists():
        return ManifestMark(byte_length=None)
    return ManifestMark(byte_length=paths.manifest.stat().st_size)


def roll_back_manifest(paths: RegistryPaths, mark: ManifestMark) -> None:
    """Restore the manifest to `mark`: cut it back to the recorded length, or remove it if it did not exist."""
    if mark.byte_length is None:
        paths.manifest.unlink(missing_ok=True)
        return
    with open(paths.manifest, "r+b") as handle:
        handle.truncate(mark.byte_length)


def write_manifest_without(paths: RegistryPaths, slug: str, manifest_bytes: bytes) -> None:
    """Rewrite the manifest from `manifest_bytes` minus the rows carrying `slug`, every other line byte-identical."""
    kept = []
    for raw_line in manifest_bytes.splitlines(keepends=True):
        text = raw_line.decode("utf-8")
        if text.strip() and json.loads(text).get("slug") == slug:
            continue
        kept.append(raw_line)
    paths.manifest.write_bytes(b"".join(kept))

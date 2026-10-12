"""What can be registered, and what the caller must say about it."""

from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Literal
from urllib.parse import urlsplit, urlunsplit

IndexProfile = Literal["seam", "batch"]

#: Kinds the registry defines itself; a keyed source must name another.
REGISTRY_KINDS = frozenset({"url", "local_pdf"})

#: Fields every manifest row carries, plus the two origin fields of the registry's own kinds.
#: A keyed source's key field must not overwrite any of them.
REGISTRY_ROW_FIELDS = frozenset(
    {
        "source_id",
        "source_kind",
        "slug",
        "title",
        "source_url",
        "origin_path",
        "raw_sha256",
        "raw_artifact_sha256",
        "extract_sha256",
        "date_extracted",
    }
)

#: A key becomes a slug suffix and a path segment, so it is one segment `retire` accepts.
KEY_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class UrlSource:
    """A web page or online document, fetched from its URL."""

    url: str

    kind: ClassVar[str] = "url"
    index_profile: ClassVar[IndexProfile] = "seam"

    @property
    def identity(self) -> str:
        return self.url

    @property
    def slug_suffix(self) -> str | None:
        return None

    @property
    def staged_input(self) -> Path | None:
        return None

    @property
    def row_extras(self) -> dict[str, str]:
        return {"source_url": self.url}


@dataclass(frozen=True)
class LocalPdfSource:
    """A PDF already on this machine, handed in by an operator."""

    path: Path

    kind: ClassVar[str] = "local_pdf"
    index_profile: ClassVar[IndexProfile] = "seam"

    @property
    def identity(self) -> str:
        return str(self.path)

    @property
    def slug_suffix(self) -> str | None:
        return None

    @property
    def staged_input(self) -> Path | None:
        return self.path

    @property
    def row_extras(self) -> dict[str, str]:
        return {"origin_path": str(self.path)}


@dataclass(frozen=True)
class KeyedFileSource:
    """A local file that an outside catalogue identifies by key, registered by a batch caller.

    The caller names the kind, the manifest field that holds the key, and how the
    key reads in the index block. It uses the batch index profile: an unattended
    run has no per-item prose to supply, so its blocks carry empty Use for and
    Validation fields rather than invented ones.
    """

    path: Path
    kind: str
    key_field: str
    key: str
    key_label: str
    key_display: str

    index_profile: ClassVar[IndexProfile] = "batch"

    def __post_init__(self) -> None:
        if not self.kind.strip() or self.kind in REGISTRY_KINDS:
            raise ValueError(f"a keyed source must name its own kind, not {self.kind!r}")
        if not self.key_field.strip() or self.key_field in REGISTRY_ROW_FIELDS:
            raise ValueError(
                f"a keyed source's key field must not be blank or a field the registry "
                f"writes: {self.key_field!r}"
            )
        if not KEY_RE.fullmatch(self.key):
            raise ValueError(f"a key must match [A-Za-z0-9_]+: {self.key!r}")

    @property
    def identity(self) -> str:
        return f"{self.kind}:{self.key}"

    @property
    def slug_suffix(self) -> str | None:
        return self.key

    @property
    def staged_input(self) -> Path | None:
        return self.path

    @property
    def row_extras(self) -> dict[str, str]:
        return {self.key_field: self.key}


Source = UrlSource | LocalPdfSource | KeyedFileSource


@dataclass(frozen=True)
class SourceMetadata:
    """What the caller says about a source. Registration never invents any of it.

    A seam-profile source needs all four fields. A batch caller supplies only the
    title.
    """

    title: str
    use_for: str = ""
    validation: str = ""
    caveat: str = ""


def slugify(title: str, max_len: int = 60) -> str:
    """A filesystem-safe slug: lowercase, runs of other characters as one underscore.

    A slug longer than `max_len` is cut at its last underscore when that keeps
    more than half of it, so words are not broken.
    """
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = re.sub(r"_+", "_", slug)
    slug = slug.strip("_")
    if len(slug) <= max_len:
        return slug
    truncated = slug[:max_len]
    last_sep = truncated.rfind("_")
    if last_sep > max_len // 2:
        return truncated[:last_sep]
    return truncated


def normalize_url(url: str) -> str:
    """The URL with scheme and host lowercased, the path normalized and the fragment dropped."""
    parts = urlsplit(url)
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            posixpath.normpath(parts.path) if parts.path else parts.path,
            parts.query,
            "",
        )
    )

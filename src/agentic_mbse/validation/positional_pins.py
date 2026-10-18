"""The positional-binding pin list: finding identities a project recorded as legacy.

A pin names one positional finding by its identity, the (owner, input, target) triple of
qualified names, with the input given by its declared name. A pinned finding is reported as a
WARNING instead of an ERROR; a pin certifies nothing about values or about agreement between
the native and generated routes (design D1).

The file is TOML, schema ``positional-pins/v1``, closed at every level (D10)::

    schema = "positional-pins/v1"
    [recorded_against]
    revision = "f96ad312c63e8c66695971b12feab971f3ba6eb3"
    date = 2026-10-15
    [[pin]]
    owner = "P::q::c"
    input = "b"
    target = "P::Sub::a"
    file = "models/designs/plant.sysml"
    line = 270

``file`` is a POSIX path relative to the pin root (D12): the pin file's directory, unless the
caller names another. Only :func:`discover` and :func:`load` touch the filesystem, and neither
writes (I3). This module imports nothing from SysIDE.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any, TypeVar

import tomllib

from agentic_mbse.project_root import find_project_root

__all__ = [
    "PIN_FILE_NAME",
    "SCHEMA",
    "FindingIdentity",
    "Pin",
    "PinList",
    "PinListAbsent",
    "PinListDefect",
    "PinListInvalid",
    "PinListResult",
    "discover",
    "load",
]

SCHEMA = "positional-pins/v1"
PIN_FILE_NAME = "positional-pins.toml"

_TOP_KEYS = frozenset({"schema", "recorded_against", "pin"})
_RECORDED_KEYS = frozenset({"revision", "date"})
_PIN_KEYS = ("owner", "input", "target", "file", "line")
_T = TypeVar("_T")


@dataclass(frozen=True, order=True)
class FindingIdentity:
    """One positional finding: owner and target qualified names, and the input's declared name."""

    owner: str
    input: str
    target: str

    def __post_init__(self) -> None:
        if not (self.owner and self.input and self.target):
            raise ValueError(f"a finding identity needs all three parts, got {self!r}")


@dataclass(frozen=True)
class Pin:
    """One recorded legacy finding. ``file`` and ``line`` say where it was, for review and scope."""

    identity: FindingIdentity
    file: PurePosixPath
    line: int


@dataclass(frozen=True)
class PinList:
    """A valid pin list. ``pins`` is sorted by identity, whatever the file's entry order."""

    path: Path
    pin_root: Path
    revision: str
    recorded: date
    pins: tuple[Pin, ...]


@dataclass(frozen=True)
class PinListAbsent:
    """No pin list. ``project_root`` and ``looked_at`` are both None when no root was found."""

    project_root: Path | None
    looked_at: Path | None


class PinListDefect(StrEnum):
    """Why a pin list is invalid; rendered as the issue's ``reason_code`` (D14)."""

    UNREADABLE = "unreadable"
    TOML_SYNTAX = "toml_syntax"
    SCHEMA_MISSING = "schema_missing"
    SCHEMA_UNSUPPORTED = "schema_unsupported"
    RECORDED_AGAINST_MISSING = "recorded_against_missing"
    REVISION_EMPTY = "revision_empty"
    DATE_NOT_A_DATE = "date_not_a_date"
    UNKNOWN_KEY = "unknown_key"
    WRONG_TYPE = "wrong_type"
    PIN_KEY_MISSING = "pin_key_missing"
    IDENTITY_PART_EMPTY = "identity_part_empty"
    LINE_NOT_POSITIVE = "line_not_positive"
    DUPLICATE_IDENTITY = "duplicate_identity"
    FILE_EMPTY = "file_empty"
    FILE_ABSOLUTE = "file_absolute"
    FILE_PARENT_REFERENCE = "file_parent_reference"
    FILE_NOT_POSIX = "file_not_posix"


@dataclass(frozen=True)
class PinListInvalid:
    """A pin list that exists but cannot be used. The check then runs as if there were none."""

    path: Path
    reason_code: PinListDefect
    detail: str


PinListResult = PinList | PinListAbsent | PinListInvalid


class _InvalidError(Exception):
    def __init__(self, defect: PinListDefect, detail: str) -> None:
        super().__init__(detail)
        self.defect = defect
        self.detail = detail


def discover(validated_path: Path) -> Path | PinListAbsent:
    """The project root's pin file, if there is one; nowhere else is looked at (D11).

    The project root is found by walking up from the validated path. A file of that name
    anywhere else, below the root or above it, is never read.
    """
    root = find_project_root(start=validated_path)
    if root is None:
        return PinListAbsent(project_root=None, looked_at=None)
    candidate = root / PIN_FILE_NAME
    if not candidate.exists():
        return PinListAbsent(project_root=root, looked_at=candidate)
    return candidate


def load(path: Path, pin_root: Path) -> PinListResult:
    """Read and strictly check one pin list. Every defect gives :class:`PinListInvalid`."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return PinListInvalid(path, PinListDefect.UNREADABLE, f"{type(error).__name__}: {error}")
    try:
        document = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        return PinListInvalid(path, PinListDefect.TOML_SYNTAX, str(error))
    try:
        return _parse(document, path, pin_root)
    except _InvalidError as invalid:
        return PinListInvalid(path, invalid.defect, invalid.detail)


def _parse(document: dict[str, Any], path: Path, pin_root: Path) -> PinList:
    _no_unknown_keys(document, _TOP_KEYS, "top level")
    if "schema" not in document:
        raise _InvalidError(PinListDefect.SCHEMA_MISSING, f'`schema = "{SCHEMA}"` is required')
    schema = _typed(document["schema"], str, "schema")
    if schema != SCHEMA:
        raise _InvalidError(
            PinListDefect.SCHEMA_UNSUPPORTED, f"schema {schema!r}; expected {SCHEMA!r}"
        )
    revision, recorded = _recorded_against(document)
    raw_pins = _typed(document.get("pin", []), list, "pin")
    pins: list[Pin] = []
    first_at: dict[FindingIdentity, int] = {}
    for index, raw in enumerate(raw_pins):
        pin = _pin(raw, f"pin[{index}]")
        if pin.identity in first_at:
            raise _InvalidError(
                PinListDefect.DUPLICATE_IDENTITY,
                f"pin[{index}] repeats the identity of pin[{first_at[pin.identity]}]: "
                f"{pin.identity.owner} | {pin.identity.input} | {pin.identity.target}",
            )
        first_at[pin.identity] = index
        pins.append(pin)
    return PinList(
        path=path,
        pin_root=pin_root,
        revision=revision,
        recorded=recorded,
        pins=tuple(sorted(pins, key=lambda p: p.identity)),
    )


def _recorded_against(document: dict[str, Any]) -> tuple[str, date]:
    if "recorded_against" not in document:
        raise _InvalidError(
            PinListDefect.RECORDED_AGAINST_MISSING, "the [recorded_against] table is required"
        )
    table = _typed(document["recorded_against"], dict, "recorded_against")
    _no_unknown_keys(table, _RECORDED_KEYS, "recorded_against")
    for key in ("revision", "date"):
        if key not in table:
            raise _InvalidError(
                PinListDefect.RECORDED_AGAINST_MISSING, f"recorded_against.{key} is required"
            )
    revision = _typed(table["revision"], str, "recorded_against.revision")
    if not revision:
        raise _InvalidError(PinListDefect.REVISION_EMPTY, "recorded_against.revision is empty")
    recorded = table["date"]
    # A TOML datetime is a `date` subclass in Python; only a plain date is accepted.
    if not isinstance(recorded, date) or isinstance(recorded, datetime):
        raise _InvalidError(
            PinListDefect.DATE_NOT_A_DATE,
            f"recorded_against.date must be a TOML date (2026-10-15), got {recorded!r}",
        )
    return revision, recorded


def _pin(raw: Any, where: str) -> Pin:
    table = _typed(raw, dict, where)
    _no_unknown_keys(table, frozenset(_PIN_KEYS), where)
    missing = [key for key in _PIN_KEYS if key not in table]
    if missing:
        raise _InvalidError(
            PinListDefect.PIN_KEY_MISSING, f"{where} is missing {', '.join(missing)}"
        )
    owner, input_name, target, file = (
        _typed(table[key], str, f"{where}.{key}") for key in ("owner", "input", "target", "file")
    )
    line = table["line"]
    if isinstance(line, bool) or not isinstance(line, int):
        raise _InvalidError(
            PinListDefect.WRONG_TYPE, f"{where}.line must be an integer, got {line!r}"
        )
    if line <= 0:
        raise _InvalidError(PinListDefect.LINE_NOT_POSITIVE, f"{where}.line is {line}")
    empty = [
        key
        for key, value in (("owner", owner), ("input", input_name), ("target", target))
        if not value
    ]
    if empty:
        raise _InvalidError(PinListDefect.IDENTITY_PART_EMPTY, f"{where}.{empty[0]} is empty")
    return Pin(FindingIdentity(owner, input_name, target), _relative_file(file, where), line)


def _relative_file(file: str, where: str) -> PurePosixPath:
    if "\\" in file:
        raise _InvalidError(
            PinListDefect.FILE_NOT_POSIX, f"{where}.file {file!r} must use `/` separators"
        )
    path = PurePosixPath(file)
    if path.is_absolute():
        raise _InvalidError(
            PinListDefect.FILE_ABSOLUTE, f"{where}.file {file!r} must be relative to the pin root"
        )
    if ".." in path.parts:
        raise _InvalidError(
            PinListDefect.FILE_PARENT_REFERENCE, f"{where}.file {file!r} contains `..`"
        )
    if path == PurePosixPath("."):
        raise _InvalidError(PinListDefect.FILE_EMPTY, f"{where}.file {file!r} names no file")
    return path


def _no_unknown_keys(table: dict[str, Any], allowed: frozenset[str], where: str) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise _InvalidError(
            PinListDefect.UNKNOWN_KEY, f"unknown key {', '.join(unknown)} at {where}"
        )


def _typed(value: Any, expected: type[_T], where: str) -> _T:
    if isinstance(value, bool) or not isinstance(value, expected):
        raise _InvalidError(
            PinListDefect.WRONG_TYPE,
            f"{where} must be {expected.__name__}, got {type(value).__name__}",
        )
    checked: _T = value
    return checked

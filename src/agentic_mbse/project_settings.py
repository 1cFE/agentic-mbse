"""The toolkit's table in a project's `pyproject.toml`: `[tool.agentic-mbse]` (Item 3 design D1).

One definition of the keys allowed there, and one reader that returns the table or names what is
wrong with it. The reader checks the file, the table shapes and which keys are present. It never
checks a value: each consumer validates only its own key (research reads `research`, validation
reads `execution-target`), so a bad value for one key never breaks the other's reader.

`add_execution_target` is the one writer: `init` uses it to add `execution-target` (design D7).

Standard library only; `research`, `validation` and `cli` all import it.
"""

from __future__ import annotations

import copy
import os
import re
import stat
import tempfile
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import tomllib

TARGET_KEY = "execution-target"
TOOLKIT_KEYS = frozenset({TARGET_KEY, "research"})
TOOLKIT_TABLE = ("tool", "agentic-mbse")
# The toolkit's table name with an underscore. The toolkit never reads it, so a table there is
# a misspelling.
UNDERSCORE_SPELLING = "agentic_mbse"


class SettingsFault(StrEnum):
    UNREADABLE = "unreadable"
    TOML_SYNTAX = "toml_syntax"
    NOT_A_TABLE = "not_a_table"
    UNDERSCORE_TABLE = "underscore_table"
    UNKNOWN_KEY = "unknown_key"


@dataclass(frozen=True)
class SettingsDefect:
    """What is wrong with the toolkit table; `detail` names the file and the fault."""

    path: Path
    fault: SettingsFault
    detail: str


@dataclass(frozen=True)
class ToolkitTable:
    """`[tool.agentic-mbse]` as read from `path`; empty when the file or the table is absent."""

    path: Path
    table: dict[str, Any] = field(default_factory=dict)


def dotted(table_path: tuple[str, ...]) -> str:
    return f"[{'.'.join(table_path)}]"


def read_toolkit_table(root: Path) -> ToolkitTable | SettingsDefect:
    """`<root>/pyproject.toml`'s `[tool.agentic-mbse]` table, or the defect that stops reading it."""
    pyproject = root / "pyproject.toml"
    try:
        text = pyproject.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ToolkitTable(pyproject)
    except (OSError, UnicodeDecodeError) as error:
        return SettingsDefect(
            pyproject, SettingsFault.UNREADABLE, f"cannot read {pyproject}: {error}"
        )
    try:
        config = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        return SettingsDefect(
            pyproject, SettingsFault.TOML_SYNTAX, f"cannot read {pyproject}: {error}"
        )

    tool = config.get("tool")
    if tool is None:
        return ToolkitTable(pyproject)
    if not isinstance(tool, dict):
        return _not_a_table(pyproject, TOOLKIT_TABLE[:1])
    if UNDERSCORE_SPELLING in tool:
        return SettingsDefect(
            pyproject,
            SettingsFault.UNDERSCORE_TABLE,
            f"{pyproject}: [tool.{UNDERSCORE_SPELLING}] is not read; "
            f"the toolkit's table is {dotted(TOOLKIT_TABLE)}, with keys {_allowed()}",
        )
    toolkit = tool.get(TOOLKIT_TABLE[-1])
    if toolkit is None:
        return ToolkitTable(pyproject)
    if not isinstance(toolkit, dict):
        return _not_a_table(pyproject, TOOLKIT_TABLE)
    unknown = sorted(set(toolkit) - TOOLKIT_KEYS)
    if unknown:
        return SettingsDefect(
            pyproject,
            SettingsFault.UNKNOWN_KEY,
            f"{pyproject}: unknown key {', '.join(map(repr, unknown))} in "
            f"{dotted(TOOLKIT_TABLE)}; allowed keys are {_allowed()}",
        )
    return ToolkitTable(pyproject, toolkit)


def _allowed() -> str:
    return ", ".join(map(repr, sorted(TOOLKIT_KEYS)))


def _not_a_table(pyproject: Path, table_path: tuple[str, ...]) -> SettingsDefect:
    return SettingsDefect(
        pyproject, SettingsFault.NOT_A_TABLE, f"{pyproject}: {dotted(table_path)} is not a table"
    )


# ---- adding execution-target (init) ------------------------------------------------------------

# A `[tool.agentic-mbse]` header line: any spacing, bare or quoted keys, an optional comment.
_HEADER = re.compile(
    r"""^[ \t]*\[[ \t]*(?:tool|"tool"|'tool')[ \t]*\.[ \t]*"""
    r"""(?:agentic-mbse|"agentic-mbse"|'agentic-mbse')[ \t]*\][ \t]*(?:#.*)?$"""
)
_INLINE = re.compile(r"""(?:agentic-mbse|"agentic-mbse"|'agentic-mbse')[ \t]*=[ \t]*\{""")
_BOM = b"\xef\xbb\xbf"
_PROBE_VALUE = "generated"


class BlockReason(StrEnum):
    DEFECT = "defect"  # the settings reader returned a `SettingsDefect`
    LAYOUT = "layout"  # a file layout the insert does not handle
    # No file here, but a parent directory has one: creating it would split uv's project.
    NESTED = "nested"


@dataclass(frozen=True)
class Insertable:
    """`execution-target` can be added: at `offset` in `text`, or as a new table when `offset` is None.

    `text` is None when the file does not exist.
    """

    path: Path
    text: str | None
    offset: int | None
    parsed: dict[str, Any]


@dataclass(frozen=True)
class Present:
    """The file already sets `execution-target`, to `value`, which may not be an allowed value."""

    path: Path
    value: Any


@dataclass(frozen=True)
class Blocked:
    """Nothing can be written: `detail` names the file and why."""

    path: Path
    reason: BlockReason
    detail: str


@dataclass(frozen=True)
class Written:
    path: Path
    created: bool


TargetSlot = Insertable | Present | Blocked
SettingWrite = Written | Present | Blocked


def target_line(value: str) -> str:
    return f'{TARGET_KEY} = "{value}"'


def inspect_execution_target(root: Path) -> TargetSlot:
    """Whether `init` can add `execution-target` to `<root>/pyproject.toml`, and where (D7)."""
    pyproject = root / "pyproject.toml"
    if pyproject.is_symlink():
        return _layout(pyproject, "it is a symlink, and replacing it would break the link")
    try:
        status = pyproject.lstat()
    except FileNotFoundError:
        enclosing = enclosing_pyproject(root)
        if enclosing is None:
            return Insertable(pyproject, None, None, {})
        return Blocked(
            pyproject,
            BlockReason.NESTED,
            f"{pyproject}: not created, because {enclosing} encloses this directory, and a "
            "pyproject.toml here would make uv treat this directory as its own project, "
            "outside that project's environment",
        )
    if status.st_nlink > 1:
        return _layout(
            pyproject, "it has more than one hard link, and replacing it would split them"
        )
    try:
        raw = pyproject.read_bytes()
    except OSError as error:
        return Blocked(pyproject, BlockReason.DEFECT, f"cannot read {pyproject}: {error}")
    if raw.startswith(_BOM):
        return _layout(pyproject, "it starts with a UTF-8 byte order mark")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        return _layout(pyproject, f"it is not UTF-8 ({error})")

    table = read_toolkit_table(root)
    if isinstance(table, SettingsDefect):
        return Blocked(pyproject, BlockReason.DEFECT, table.detail)
    if TARGET_KEY in table.table:
        return Present(pyproject, table.table[TARGET_KEY])

    parsed = tomllib.loads(text)
    lines = text.splitlines(keepends=True)
    headers = [i for i, line in enumerate(lines) if _HEADER.match(line.rstrip("\r\n"))]
    if len(headers) > 1:
        return _layout(pyproject, f"{len(headers)} lines match the {dotted(TOOLKIT_TABLE)} header")
    offset = sum(map(len, lines[: headers[0] + 1])) if headers else None
    slot = Insertable(pyproject, text, offset, parsed)
    # The insert is the same shape for either value, so one probe decides the layout.
    if _verified_insert(slot, _PROBE_VALUE) is not None:
        return slot
    if offset is None and TOOLKIT_TABLE[-1] in parsed.get(TOOLKIT_TABLE[0], {}):
        how = "an inline table" if _INLINE.search(text) else "dotted keys"
        return _layout(pyproject, f"{dotted(TOOLKIT_TABLE)} is defined through {how}")
    return _layout(
        pyproject, "the file with the line added does not parse to the original plus one key"
    )


def enclosing_pyproject(root: Path) -> Path | None:
    """The nearest `pyproject.toml` in a directory above `root`, as uv's project search finds it."""
    for parent in root.resolve().parents:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def add_execution_target(root: Path, value: str) -> SettingWrite:
    """Add `execution-target = "<value>"` to `<root>/pyproject.toml`, changing no other byte (D7).

    Writes only when the result parses to the original document plus that one key; anything
    else is `Blocked` with nothing written. An existing key is `Present` and never changed.
    """
    slot = inspect_execution_target(root)
    if not isinstance(slot, Insertable):
        return slot
    new_text = _verified_insert(slot, value)
    if new_text is None:
        return _layout(
            slot.path, "the file with the line added does not parse to the original plus one key"
        )
    _replace_atomically(slot.path, new_text.encode("utf-8"))
    return Written(slot.path, created=slot.text is None)


def _verified_insert(slot: Insertable, value: str) -> str | None:
    """The file's text with the key added, or None if it does not parse to the original plus it."""
    new_text = _inserted(slot, value)
    expected = copy.deepcopy(slot.parsed)
    expected.setdefault(TOOLKIT_TABLE[0], {}).setdefault(TOOLKIT_TABLE[1], {})[TARGET_KEY] = value
    try:
        return new_text if tomllib.loads(new_text) == expected else None
    except tomllib.TOMLDecodeError:
        return None


def _inserted(slot: Insertable, value: str) -> str:
    text = slot.text or ""
    newline = _newline_style(text)
    if slot.offset is not None:
        before, after = text[: slot.offset], text[slot.offset :]
        header_newline = before[len(before.rstrip("\r\n")) :]
        if header_newline:
            return before + target_line(value) + header_newline + after
        return before + newline + target_line(value) + newline + after
    table = f"{dotted(TOOLKIT_TABLE)}{newline}{target_line(value)}{newline}"
    if not text:
        return table
    if not text.endswith(("\n", "\r")):
        text += newline
    return text + newline + table


def _newline_style(text: str) -> str:
    match = re.search(r"\r\n|\n|\r", text)
    return match.group(0) if match else "\n"


def _replace_atomically(path: Path, data: bytes) -> None:
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else _default_file_mode()
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _default_file_mode() -> int:
    umask = os.umask(0)
    os.umask(umask)
    return 0o666 & ~umask


def _layout(pyproject: Path, why: str) -> Blocked:
    return Blocked(pyproject, BlockReason.LAYOUT, f"{pyproject}: not changed, because {why}")

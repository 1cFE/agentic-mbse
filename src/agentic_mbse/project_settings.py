"""The toolkit's table in a project's `pyproject.toml`: `[tool.agentic-mbse]` (Item 3 design D1).

One definition of the keys allowed there, and one reader that returns the table or names what is
wrong with it. The reader checks the file, the table shapes and which keys are present. It never
checks a value: each consumer validates only its own key (research reads `research`, validation
reads `execution-target`), so a bad value for one key never breaks the other's reader.

Standard library only; `research`, `validation` and `cli` all import it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import tomllib

TOOLKIT_KEYS = frozenset({"execution-target", "research"})
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
            f"the toolkit's table is {dotted(TOOLKIT_TABLE)}",
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
            f"{dotted(TOOLKIT_TABLE)}; allowed keys are "
            f"{', '.join(map(repr, sorted(TOOLKIT_KEYS)))}",
        )
    return ToolkitTable(pyproject, toolkit)


def _not_a_table(pyproject: Path, table_path: tuple[str, ...]) -> SettingsDefect:
    return SettingsDefect(
        pyproject, SettingsFault.NOT_A_TABLE, f"{pyproject}: {dotted(table_path)} is not a table"
    )

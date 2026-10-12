"""The hold-out hook: how a target bars material the registry must never take in.

A guard answers three questions: is this input path barred, does this text name
something barred, does this file. A match names the rule that fired and where,
never the content that fired it.

A target names its guard file in `pyproject.toml`, relative to the project root:

    [tool.agentic-mbse.research]
    holdout-guard = "scripts/holdout_guard.py"

The hook fails closed. A configured guard that cannot answer, because the
configuration is wrong, the file will not load, a function is missing, or a
check raises or answers in the wrong shape, raises `HoldoutGuardError` at the
check, and the caller refuses. It never answers "nothing barred".
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import tomllib

GUARD_KEY = "holdout-guard"
_TABLE_PATH = ("tool", "agentic-mbse", "research")
_CHECKS = ("check_input_path", "scan_terms", "scan_file")

# A loaded guard is registered under a private name derived from its file, so two
# projects' guards loaded in one process never replace each other.
_MODULE_PREFIX = "_agentic_mbse_holdout_guard_"


class HoldoutMatch(Protocol):
    """One barred rule that fired, and the offsets in the checked text where it fired."""

    @property
    def rule_id(self) -> str: ...  # e.g. "term:<t>" or "path:<glob>"; never the content

    @property
    def count(self) -> int: ...

    @property
    def offsets(self) -> tuple[int, ...]: ...


class HoldoutGuard(Protocol):
    """A target's hold-out rule, as three checks."""

    def check_input_path(self, path: Path) -> HoldoutMatch | None: ...

    def scan_terms(self, text: str) -> Sequence[HoldoutMatch]: ...

    def scan_file(self, path: Path) -> Sequence[HoldoutMatch]: ...


class HoldoutGuardError(RuntimeError):
    """The configured guard cannot answer, so nothing it would check may pass.

    The message starts `hold-out guard unavailable:`. The skills read a refusal
    with that reason as a seam repair, not a source to obtain.
    """

    def __init__(self, detail: str) -> None:
        super().__init__(f"hold-out guard unavailable: {detail}")
        self.detail = detail


@dataclass(frozen=True)
class HoldoutHit:
    """A guard's match, read into plain values. Callers see only these, never the guard's object."""

    rule_id: str
    count: int
    offsets: tuple[int, ...]


# --- asking a guard --------------------------------------------------------------
#
# Every call into a guard, and every read of what it returns, goes through `_ask`.


def input_path_hit(guard: HoldoutGuard, path: Path) -> HoldoutHit | None:
    """The rule barring this input path, or None. Raises `HoldoutGuardError` if the guard faults."""
    return _ask("check_input_path", lambda: _optional_hit(guard.check_input_path(path)))


def first_term_hit(guard: HoldoutGuard, text: str) -> HoldoutHit | None:
    """The first barred term in `text`, or None. Raises `HoldoutGuardError` if the guard faults."""
    return _ask("scan_terms", lambda: _first_hit(guard.scan_terms(text)))


def first_file_hit(guard: HoldoutGuard, path: Path) -> HoldoutHit | None:
    """The first barred term in the file, or None. Raises `HoldoutGuardError` if the guard faults."""
    return _ask("scan_file", lambda: _first_hit(guard.scan_file(path)))


class _MalformedAnswerError(Exception):
    """A guard answered, but not in the protocol's shape."""


def _ask(check: str, question: Callable[[], HoldoutHit | None]) -> HoldoutHit | None:
    """Put one question to the guard and read its answer, turning every fault into `HoldoutGuardError`.

    The guard is the target's code, so whatever it raises means it cannot
    answer. The broad catch is the point: no exception from it may read as
    "nothing barred".
    """
    try:
        return question()
    except HoldoutGuardError:
        raise
    except _MalformedAnswerError as error:
        raise HoldoutGuardError(f"{check} answered {error}") from error
    except Exception as error:
        raise HoldoutGuardError(f"{check} raised {type(error).__name__}: {error}") from error


def _optional_hit(match: object) -> HoldoutHit | None:
    return None if match is None else _read_match(match)


def _first_hit(matches: object) -> HoldoutHit | None:
    if isinstance(matches, (str, bytes)) or not isinstance(matches, Sequence):
        raise _MalformedAnswerError(f"{type(matches).__name__}, not a sequence of matches")
    return _read_match(matches[0]) if matches else None


def _read_match(match: object) -> HoldoutHit:
    rule_id = getattr(match, "rule_id", None)
    count = getattr(match, "count", None)
    offsets = getattr(match, "offsets", None)
    if not isinstance(rule_id, str) or not rule_id:
        raise _MalformedAnswerError("a match without a rule_id")
    if not isinstance(count, int):
        raise _MalformedAnswerError("a match without an integer count")
    if not isinstance(offsets, Sequence) or not all(isinstance(at, int) for at in offsets):
        raise _MalformedAnswerError("a match without integer offsets")
    return HoldoutHit(rule_id=rule_id, count=count, offsets=tuple(offsets))


# --- the guards ------------------------------------------------------------------


class _NoHoldoutGuard:
    """The guard of a target that holds nothing out: every check passes."""

    def check_input_path(self, path: Path) -> HoldoutMatch | None:
        return None

    def scan_terms(self, text: str) -> Sequence[HoldoutMatch]:
        return ()

    def scan_file(self, path: Path) -> Sequence[HoldoutMatch]:
        return ()


#: The guard for a target with no hold-out.
NO_HOLDOUT_GUARD: HoldoutGuard = _NoHoldoutGuard()


@dataclass(frozen=True)
class _UnavailableGuard:
    """Stands in for a configured guard that could not be loaded: every check raises its fault."""

    detail: str

    def check_input_path(self, path: Path) -> HoldoutMatch | None:
        raise HoldoutGuardError(self.detail)

    def scan_terms(self, text: str) -> Sequence[HoldoutMatch]:
        raise HoldoutGuardError(self.detail)

    def scan_file(self, path: Path) -> Sequence[HoldoutMatch]:
        raise HoldoutGuardError(self.detail)


@dataclass(frozen=True)
class _FileGuard:
    """A guard loaded from a target's file: its three module-level functions."""

    check_input_path: Callable[[Path], HoldoutMatch | None]
    scan_terms: Callable[[str], Sequence[HoldoutMatch]]
    scan_file: Callable[[Path], Sequence[HoldoutMatch]]


# --- loading the configured guard --------------------------------------------------


def load_holdout_guard(project_root: Path) -> HoldoutGuard:
    """The guard `project_root/pyproject.toml` names, loaded from its file.

    No `[tool.agentic-mbse.research]` table, or an empty one, gives a guard that
    holds nothing out. Any fault gives a guard whose every check raises
    `HoldoutGuardError` naming it: unreadable TOML, a key other than
    `holdout-guard`, a value that is not a non-empty string, a file that is
    missing or will not load, or a missing function. Loading itself never
    raises, so the fault surfaces at the first check, where the caller refuses.
    """
    try:
        guard_file = _configured_guard_file(project_root)
        return NO_HOLDOUT_GUARD if guard_file is None else _load_guard_file(guard_file)
    except HoldoutGuardError as fault:
        return _UnavailableGuard(fault.detail)


def _configured_guard_file(project_root: Path) -> Path | None:
    """The guard file the project's configuration names, or None when it names none."""
    pyproject = project_root / "pyproject.toml"
    try:
        config = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise HoldoutGuardError(f"cannot read {pyproject}: {error}") from error

    table = _research_table(config, pyproject)
    if table is None:
        return None
    unknown = sorted(set(table) - {GUARD_KEY})
    if unknown:
        # A misspelled key would otherwise switch the guard off without a word.
        raise HoldoutGuardError(
            f"{pyproject}: unknown key {', '.join(map(repr, unknown))} in "
            f"[tool.agentic-mbse.research]; its only key is {GUARD_KEY!r}"
        )
    if GUARD_KEY not in table:
        return None
    value = table[GUARD_KEY]
    if not isinstance(value, str) or not value.strip():
        raise HoldoutGuardError(f"{pyproject}: {GUARD_KEY} must be a non-empty path, got {value!r}")
    return project_root / value


def _research_table(config: dict[str, Any], pyproject: Path) -> dict[str, Any] | None:
    """`[tool.agentic-mbse.research]`, or None when absent. Anything but a table on the way is a fault."""
    table = config
    for depth, key in enumerate(_TABLE_PATH, start=1):
        if key not in table:
            return None
        section = table[key]
        if not isinstance(section, dict):
            raise HoldoutGuardError(
                f"{pyproject}: [{'.'.join(_TABLE_PATH[:depth])}] is not a table"
            )
        table = section
    return table


def _load_guard_file(guard_file: Path) -> HoldoutGuard:
    """Run the guard file as a module and take its three functions.

    The module goes into `sys.modules` before it runs, as an imported module
    would: a dataclass under postponed annotations looks its module up there.
    A module that fails to load, or lacks a function, is taken out again.
    """
    if not guard_file.is_file():
        raise HoldoutGuardError(f"no file at {guard_file}")
    resolved = guard_file.resolve()
    name = _MODULE_PREFIX + hashlib.sha256(str(resolved).encode()).hexdigest()[:16]
    spec = importlib.util.spec_from_file_location(name, resolved)
    if spec is None or spec.loader is None:
        raise HoldoutGuardError(f"{guard_file} is not a Python module")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        sys.modules.pop(name, None)
        raise HoldoutGuardError(
            f"{guard_file} failed to load: {type(error).__name__}: {error}"
        ) from error

    missing = [check for check in _CHECKS if not callable(getattr(module, check, None))]
    if missing:
        sys.modules.pop(name, None)
        raise HoldoutGuardError(f"{guard_file} lacks {', '.join(missing)}")
    return _FileGuard(
        check_input_path=module.check_input_path,
        scan_terms=module.scan_terms,
        scan_file=module.scan_file,
    )

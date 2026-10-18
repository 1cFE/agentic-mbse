"""One model load and one constraint extraction per `validate` run (design D14).

The runner opens a `ValidationSession` around its level loop. Inside it, `load_sysml_model`
returns the cached `(model, diagnostics)` for the same file list, and `constraint_facts(model)`
runs `extract_identified_constraint_facts` once per loaded model, so L4 and L6 read the same
facts. Facts cannot be shared across separate loads (an anonymous element's id is local to its
load), so the model and its facts are shared together.

Outside a session (a level called directly, a test, another repository's code) both calls behave
exactly as they did before the session existed.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from pathlib import Path
from types import TracebackType
from typing import Any

from agentic_mbse.sysml.constraint_extraction import (
    IdentifiedConstraintFacts,
    extract_identified_constraint_facts,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

# (resolved path, size, mtime_ns) for each file, in the caller's order.
_FileStamps = tuple[tuple[str, int, int], ...]


def _stamps(files: list[Path]) -> _FileStamps:
    stamps = []
    for file in files:
        if not file.is_file():
            # A directory's own mtime does not change when a file inside it does, so a cached
            # directory load could be stale. The levels always pass discovered files.
            raise ValueError(f"ValidationSession caches file lists only; {file} is not a file")
        stat = file.stat()
        stamps.append((str(file.resolve()), stat.st_size, stat.st_mtime_ns))
    return tuple(stamps)


class ValidationSession:
    """A run's shared model loads and constraint facts. Use as a context manager; not nestable."""

    def __init__(self) -> None:
        # Keyed by the resolved paths alone, so a changed file replaces its entry, not adds one.
        self._loads: dict[tuple[str, ...], tuple[_FileStamps, tuple[Any, Any]]] = {}
        # Keyed by id(model). The entry holds the model itself, so the id cannot be reused by
        # another object while the session is open.
        self._facts: dict[int, tuple[Any, IdentifiedConstraintFacts | Exception]] = {}
        self.model_loads = 0
        self.constraint_extractions = 0
        self._token: Token[ValidationSession | None] | None = None

    def __enter__(self) -> ValidationSession:
        if _ACTIVE.get() is not None:
            raise RuntimeError("a ValidationSession is already active")
        self._token = _ACTIVE.set(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        assert self._token is not None
        _ACTIVE.reset(self._token)
        self._token = None
        self._loads.clear()
        self._facts.clear()

    def load(self, files: list[Path]) -> tuple[Any, Any]:
        """`(model, diagnostics)` for `files`, loaded once while every file's size and mtime hold."""
        stamps = _stamps(files)
        key = tuple(path for path, _, _ in stamps)
        cached = self._loads.get(key)
        if cached is not None and cached[0] == stamps:
            return cached[1]
        loaded = SysideAdapter.load_model(files)
        self.model_loads += 1
        self._loads[key] = (stamps, loaded)
        return loaded

    def constraint_facts(self, model: Any) -> IdentifiedConstraintFacts:
        """`extract_identified_constraint_facts(model)`, run once; a raised error re-raises each call."""
        entry = self._facts.get(id(model))
        if entry is None:
            self.constraint_extractions += 1
            outcome: IdentifiedConstraintFacts | Exception
            try:
                outcome = extract_identified_constraint_facts(model)
            except Exception as error:  # stored and re-raised below, never swallowed
                outcome = error
            entry = (model, outcome)
            self._facts[id(model)] = entry
        outcome = entry[1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


_ACTIVE: ContextVar[ValidationSession | None] = ContextVar("validation_session", default=None)


def active_session() -> ValidationSession | None:
    """The session the runner opened, or None outside a run."""
    return _ACTIVE.get()


def constraint_facts(model: Any) -> IdentifiedConstraintFacts:
    """The model's identified constraint facts: from the active session, else extracted now."""
    session = _ACTIVE.get()
    if session is None:
        return extract_identified_constraint_facts(model)
    return session.constraint_facts(model)

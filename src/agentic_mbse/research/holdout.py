"""The hold-out hook: how a target bars material the registry must never take in.

A guard answers three questions: is this input path barred, does this text name
something barred, does this file. A match names the rule that fired and where,
never the content that fired it.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol


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

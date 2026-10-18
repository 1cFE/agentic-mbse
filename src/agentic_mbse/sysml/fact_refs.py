"""Pure references from a fact to the model element it is about.

Shared by the occurrence facts and the subset facts. Neither type holds a SysIDE node: an
:class:`ElementRef` names a declaration by its reload-stable identity, and a
:class:`SafeLocation` says where a subject was authored as far as that is known. Both are
built on the SysIDE side and read anywhere, including the pure decision layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

__all__ = ["ElementRef", "SafeLocation"]


@dataclass(frozen=True, order=True)
class ElementRef:
    """One declaration: its reload-stable UUIDv5, qualified name and SysIDE metatype name."""

    element_id: UUID
    qualified_name: str
    kind: str

    def __post_init__(self) -> None:
        if not isinstance(self.element_id, UUID) or self.element_id.version != 5:
            raise ValueError(f"ElementRef needs a reload-stable UUIDv5, got {self.element_id!r}")
        if not self.qualified_name:
            raise ValueError("ElementRef needs a qualified name")
        if not self.kind:
            raise ValueError("ElementRef needs a metatype name")


@dataclass(frozen=True, order=True)
class SafeLocation:
    """Where a subject was authored, with each part absent when SysIDE could not say.

    Building one never raises (the extraction side reads every part defensively), so a
    failure can always say where it happened as far as that is known.
    """

    file: str | None
    line: int | None
    qualified_name: str | None

    def __post_init__(self) -> None:
        if self.line is not None and self.line < 0:
            raise ValueError(f"SafeLocation line must be non-negative, got {self.line}")

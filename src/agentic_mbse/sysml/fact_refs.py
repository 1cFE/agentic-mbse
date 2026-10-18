"""Pure references from a fact to the model element it is about.

Shared by the occurrence facts and the subset facts. Neither type holds a SysIDE node: an
:class:`ElementRef` names an element by its identity, and a
:class:`SafeLocation` says where a subject was authored as far as that is known. Both are
built on the SysIDE side and read anywhere, including the pure decision layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

__all__ = ["ElementRef", "SafeLocation"]


@dataclass(frozen=True)
class ElementRef:
    """One element: its parser UUID, its qualified name and its SysIDE metatype name.

    A named declaration carries its reload-stable UUIDv5 and qualified name. An anonymous
    element (an anonymous ``assert constraint``, say) has neither: SysIDE gives it a
    session-local UUID and no qualified name, so its location is what identifies it across
    loads, and facts sort by location before identity for that reason.
    """

    element_id: UUID
    qualified_name: str | None
    kind: str

    def __post_init__(self) -> None:
        if not isinstance(self.element_id, UUID):
            raise TypeError(f"ElementRef needs a UUID, got {self.element_id!r}")
        if self.qualified_name is not None and self.element_id.version != 5:
            raise ValueError("a named ElementRef carries its reload-stable UUIDv5")
        if self.qualified_name == "":
            raise ValueError("an anonymous element has qualified name None, not empty")
        if not self.kind:
            raise ValueError("ElementRef needs a metatype name")


@dataclass(frozen=True)
class SafeLocation:
    """Where a subject was authored, with each part absent when SysIDE could not say.

    Building one never raises (the extraction side reads every part defensively), so a
    failure can always say where it happened as far as that is known.
    """

    file: str | None
    line: int | None
    qualified_name: str | None

    def sort_key(self) -> tuple[str, int, str]:
        return (self.file or "", -1 if self.line is None else self.line, self.qualified_name or "")

    def __post_init__(self) -> None:
        if self.line is not None and self.line < 0:
            raise ValueError(f"SafeLocation line must be non-negative, got {self.line}")

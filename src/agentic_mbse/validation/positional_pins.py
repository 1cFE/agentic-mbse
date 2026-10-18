"""The positional-binding pin list: finding identities a project recorded as legacy.

A pin names one positional finding by its identity, the (owner, input, target) triple of
qualified names, with the input given by its declared name. This module is pure data and
parsing; it imports nothing from SysIDE (design I6).
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["FindingIdentity"]


@dataclass(frozen=True, order=True)
class FindingIdentity:
    """One positional finding: owner and target qualified names, and the input's declared name."""

    owner: str
    input: str
    target: str

    def __post_init__(self) -> None:
        if not (self.owner and self.input and self.target):
            raise ValueError(f"a finding identity needs all three parts, got {self!r}")

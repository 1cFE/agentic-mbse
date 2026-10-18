"""The invocation capability boundary: which callables the executable subset supports.

One pure module, imported by the fact layer (`reference_use`, whose refusal of every other
invocation is the generator's ES-005 refusal) and by the decision layer (`subset_profile`), so
the two cannot disagree about what is supported (design review S8). It imports no SysIDE.

Changing `SUPPORTED_INVOCATION_IDS` changes the generator's refusals and must bump
`SUBSET_PROFILE_VERSION`; a test pins a digest of it.

:class:`InvocationUse` is the pure record of one ordinary invocation, produced by
`reference_use.invocation_uses` and read by the subset facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

__all__ = [
    "STANDARD_SUM_FUNCTION_ID",
    "SUPPORTED_INVOCATION_IDS",
    "InvocationUse",
    "is_supported_invocation_id",
]

#: Reload-stable declaration identity of ``NumericalFunctions::sum`` in the SysML standard
#: library. Its spelling is not authority: a different declaration called ``sum`` is still a
#: different function and must not gain collection semantics.
STANDARD_SUM_FUNCTION_ID = UUID("6d745ea3-e265-5ddd-aa6c-b3fe29dc4272")

#: Every callable an ordinary invocation may resolve to. Identity, never name, decides.
SUPPORTED_INVOCATION_IDS: frozenset[UUID] = frozenset({STANDARD_SUM_FUNCTION_ID})


def is_supported_invocation_id(callable_id: UUID) -> bool:
    """Whether an invocation of this declaration is inside the executable subset."""
    return callable_id in SUPPORTED_INVOCATION_IDS


@dataclass(frozen=True)
class InvocationUse:
    """One ordinary (non-operator) invocation in an expression.

    `callable_id` and `callable_name` are ``None`` when SysIDE resolved no function, which the
    subset refuses like any unsupported callable. `authored_text` is the invocation as written,
    when SysIDE can give it.
    """

    callable_id: UUID | None
    callable_name: str | None
    authored_text: str | None
    location: tuple[str, int] | None

    @property
    def supported(self) -> bool:
        return self.callable_id is not None and is_supported_invocation_id(self.callable_id)

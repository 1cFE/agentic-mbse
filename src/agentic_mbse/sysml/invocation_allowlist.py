"""The invocation capability boundary: which callables the executable subset supports.

One pure module that imports no SysIDE. The reference walk (`reference_use`) refuses every
invocation of a callable outside `SUPPORTED_INVOCATION_IDS`, as the generator's ES-005 refusal
does.
"""

from __future__ import annotations

from uuid import UUID

__all__ = [
    "STANDARD_SUM_FUNCTION_ID",
    "SUPPORTED_INVOCATION_IDS",
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

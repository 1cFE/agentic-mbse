"""The invocation allowlist is one pure module both layers import (design review S8)."""

from __future__ import annotations

import subprocess
import sys
from uuid import UUID, uuid5

from agentic_mbse.sysml.invocation_allowlist import (
    STANDARD_SUM_FUNCTION_ID,
    SUPPORTED_INVOCATION_IDS,
    is_supported_invocation_id,
)

#: `NumericalFunctions::sum`, the one identity `reference_use.py:61` held before the move.
SUM = UUID("6d745ea3-e265-5ddd-aa6c-b3fe29dc4272")


def test_the_allowlist_is_exactly_standard_sum() -> None:
    assert STANDARD_SUM_FUNCTION_ID == SUM
    assert SUPPORTED_INVOCATION_IDS == frozenset({SUM})
    assert is_supported_invocation_id(SUM)
    assert not is_supported_invocation_id(uuid5(SUM, "NumericalFunctions::product"))


def test_reference_use_consults_the_same_allowlist() -> None:
    from agentic_mbse.sysml import invocation_allowlist, reference_use

    assert (
        reference_use.is_supported_invocation_id is invocation_allowlist.is_supported_invocation_id
    )
    assert not hasattr(reference_use, "_STANDARD_SUM_FUNCTION_ID")


def test_importing_the_allowlist_pulls_in_no_parser() -> None:
    code = (
        "import sys, agentic_mbse.sysml.invocation_allowlist;"
        "bad = [m for m in sys.modules if m == 'syside' or m.endswith('syside_adapter') "
        "or m.endswith('reference_use')];"
        "assert not bad, bad"
    )
    subprocess.run([sys.executable, "-c", code], check=True)

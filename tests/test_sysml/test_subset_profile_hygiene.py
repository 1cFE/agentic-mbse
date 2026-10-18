"""Import hygiene: the decision layer pulls in no SysIDE and no SysIDE-reading module."""

from __future__ import annotations

import subprocess
import sys


def test_subset_profile_imports_no_syside_and_no_reader() -> None:
    forbidden = (
        "syside",
        "agentic_mbse.sysml.syside_adapter",
        "agentic_mbse.sysml.reference_use",
        "agentic_mbse.sysml.constraint_extraction",
        "agentic_mbse.sysml.subset_extraction",
        "agentic_mbse.sysml.occurrence_extraction",
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import agentic_mbse.sysml.subset_profile, sys; "
            f"loaded = [m for m in {forbidden!r} if m in sys.modules]; "
            "assert not loaded, loaded",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

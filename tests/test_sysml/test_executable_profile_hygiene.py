"""Import-hygiene test (I4/D2): the profile pulls in no syside.

A plain `python` subprocess, not the Claude-CLI-invoked `agentic-mbse` command — the CLAUDE.md
blank-output caveat is about the Claude CLI's `/dev/tty` status-line rendering, not this.
"""

from __future__ import annotations

import subprocess
import sys


def test_executable_profile_imports_no_syside() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import agentic_mbse.sysml.executable_profile, sys; "
            "assert 'syside' not in sys.modules, sys.modules.keys()",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

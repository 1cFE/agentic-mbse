"""`python -m agentic_mbse` runs the CLI, so capture can start the extractor with the running interpreter."""

import subprocess
import sys


def _run_module(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "agentic_mbse", *args], capture_output=True, text=True, timeout=120
    )


def test_the_module_runs_the_cli():
    completed = _run_module("--help")
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.startswith("usage: agentic-mbse")


def test_the_module_reaches_the_extract_subcommand():
    completed = _run_module("extract", "--help")
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.startswith("usage: agentic-mbse extract")

"""Fixture projects for L6 and CLI tests, built under `tmp_path` (Item 3 plan Phase 4).

Each project is marked as a project root by `work/BACKLOG.md`, so `find_project_root` stops at
it and never reaches the test runner's checkout or `$HOME`. Later phases add model shapes.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

from agentic_mbse.cli import main

# A calc def used by one part, with typed inputs, a named return and docs: clean at every level.
CLEAN_MODEL = """\
package TestPackage {
    doc /* A clean model: every level passes on it. */
    private import ScalarValues::*;

    calc def TestCalculation {
        doc /* A simple test calculation definition */
        in x : Real;
        in y : Real;
        return result : Real = x + y;
    }

    part def Plant {
        doc /* A plant that uses the calculation */
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        calc total : TestCalculation {
            in x = a;
            in y = b;
        }
    }

    part plant : Plant;
}
"""


def make_project(
    parent: Path,
    *,
    pyproject: str | None = None,
    models: dict[str, str] | None = None,
    name: str = "project",
) -> Path:
    """A project under `parent/name` with `models/` and an optional `pyproject.toml`; returns models/."""
    root = parent / name
    (root / "work").mkdir(parents=True)
    (root / "work" / "BACKLOG.md").write_text("# Backlog\n")
    if pyproject is not None:
        (root / "pyproject.toml").write_text(pyproject)
    for relative, text in (models or {"library/calc.sysml": CLEAN_MODEL}).items():
        path = root / "models" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root / "models"


def target_table(value: str) -> str:
    """A `pyproject.toml` whose toolkit table holds `execution-target = <value>` (TOML text)."""
    return f"[tool.agentic-mbse]\nexecution-target = {value}\n"


def run_cli(*argv: str) -> tuple[int, str]:
    """`agentic-mbse <argv>` in this process; returns the exit code and stdout plus stderr."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = main(list(argv))
    return code, out.getvalue()

"""Finding the project root of a target repo.

A project root is the nearest directory, walking up, that holds `work/BACKLOG.md`, the
install manifest, or a `.claude/` directory. It lives here rather than in `cli/` because the
validation layer needs it too (the positional pin list is found at the project root), and
`cli/` imports the validation layer: importing `cli` from `validation` would be a cycle.
`agentic_mbse.cli` re-exports :func:`find_project_root` under its old name.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["MANIFEST", "find_project_root"]

MANIFEST = ".agentic-mbse/install.json"


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from ``start`` (default: the working directory) to the first project root.

    A relative ``start`` is taken from the working directory. Returns None if no directory on
    the way up holds a marker.
    """
    current = Path.cwd() if start is None else start.absolute()
    while True:
        if (current / "work" / "BACKLOG.md").exists():
            return current
        if (current / MANIFEST).is_file() or (current / ".claude").is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent

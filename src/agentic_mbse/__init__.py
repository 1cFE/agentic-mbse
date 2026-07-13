"""agentic-mbse: Domain-agnostic MBSE toolkit for AI-assisted systems engineering."""

from __future__ import annotations

from typing import Any

__version__ = "0.1.0"

__all__ = ["__version__", "main"]


def __getattr__(name: str) -> Any:
    """Lazy re-export of `main` (PEP 562).

    `cli` pulls in the full validation stack (and, through it, syside) at import time. Eagerly
    importing it here would mean `import agentic_mbse.<anything>` always loads syside, breaking
    the license-free guarantee pure submodules like `sysml.constraint_facts` and
    `sysml.executable_profile` make (I4). The packaged console script points at
    `agentic_mbse.cli:main` directly and never touches this re-export.
    """
    if name == "main":
        from agentic_mbse.cli import main

        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

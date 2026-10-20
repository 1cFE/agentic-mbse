"""`reconstruct_expression`'s text for every expression in the test fixtures (Item 3 Phase 6).

`scripts/l6_subset/record_reconstruct_texts.py` records this once, before `expression.py`'s
dispatch is refactored, into `tests/fixtures/l6/reconstruct_texts_ebb3d467.json`;
`tests/test_sysml/test_text_fallback.py` recomputes it and compares exactly. Item 2's agent
depends on `reconstruct_expression`, so its output must not change.

Each fixture file is loaded alone, so the record does not depend on which files share a load.
Every `Expression` element SysIDE enumerates in the file (root and nested) is reconstructed.
An element is keyed by its position in that enumeration, its source line and column and its
SysIDE type; a raise is recorded as `!<ExceptionType>: <code or message>`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_mbse.errors import SemanticEvidenceError
from agentic_mbse.sysml.expression import reconstruct_expression
from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
RECORD = FIXTURES / "l6" / "reconstruct_texts_ebb3d467.json"


def _position(element: Any) -> str:
    start = element.cst_node.start_point if element.cst_node else None
    return f"{start.line + 1}:{start.character + 1}" if start else "?"


def _text(element: Any) -> str:
    try:
        return reconstruct_expression(element)
    except SemanticEvidenceError as error:
        return f"!SemanticEvidenceError: {error.code.value}"


def reconstruct_file(path: Path) -> list[list[str]]:
    """`[position, type, text]` for every expression in one fixture file, in SysIDE's order."""
    syside = get_syside()
    model, _diagnostics = SysideAdapter.load_model([path])
    expressions = [
        feature
        for feature in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True)
        if isinstance(feature, syside.Expression)
    ]
    return [[_position(e), type(e).__name__, _text(e)] for e in expressions]


def reconstruct_all(root: Path = FIXTURES) -> dict[str, list[list[str]]]:
    """`reconstruct_file` for every `*.sysml` under `root`, keyed by its path below `root`."""
    return {
        path.relative_to(root).as_posix(): reconstruct_file(path)
        for path in sorted(root.rglob("*.sysml"))
    }

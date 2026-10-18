"""`subset_extraction` reads the model through the generator's shared helpers, not its own copy.

An AST gate (plan Phase 4): the module imports `is_literal_node`, `unit_annotation_value`,
`inspect_reference_uses` and `invocation_uses`, and no function in it compares against the
metatype names `FeatureReferenceExpression` or `InvocationExpression` except
`_is_reference_expression`, the one metatype test the generator also has
(`elaborate.py:1114-1118`).
"""

from __future__ import annotations

import ast
from pathlib import Path

MODULE = Path(__file__).parents[2] / "src" / "agentic_mbse" / "sysml" / "subset_extraction.py"
SHARED_HELPERS = {
    "is_literal_node",
    "unit_annotation_value",
    "inspect_reference_uses",
    "invocation_uses",
}
GUARDED_NAMES = {"FeatureReferenceExpression", "InvocationExpression"}
ALLOWED = {"_is_reference_expression"}


def _imported_names(tree: ast.AST) -> set[str]:
    return {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }


def _functions_naming(tree: ast.AST, names: set[str]) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Constant) and inner.value in names:
                    found.add(node.name)
    return found


def test_the_shared_helpers_are_imported() -> None:
    tree = ast.parse(MODULE.read_text())
    assert SHARED_HELPERS <= _imported_names(tree)


def test_only_the_generators_metatype_test_names_reference_or_invocation() -> None:
    tree = ast.parse(MODULE.read_text())
    assert _functions_naming(tree, GUARDED_NAMES) == ALLOWED


def test_the_gate_sees_a_second_copy(tmp_path: Path) -> None:
    """Anti-vacuity: a function spelling the metatype name itself is caught."""
    mutant = ast.parse(
        "def _is_reference_expression(e):\n    return is_(e, 'FeatureReferenceExpression')\n"
        "def sneaky(e):\n    return is_(e, 'InvocationExpression')\n"
    )
    assert _functions_naming(mutant, GUARDED_NAMES) == {"_is_reference_expression", "sneaky"}

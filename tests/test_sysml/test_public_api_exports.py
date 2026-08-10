"""Export-consistency tests for the ``agentic_mbse.sysml`` barrel (F7).

``__all__`` is derived from the ``_LAZY`` registry, so these tests pin that the one
inventory stays total: every advertised name resolves through the PEP 562 hook, the
advertised set is exactly the registry, and the hand-written TYPE_CHECKING imports track
the registry too (the barrel suppresses F401 file-wide, so this test is the guard that
catches a stale or missing static import).

Resolving every name imports the syside-backed submodules in *this* process — deliberate,
and compatible with ``test_executable_profile_hygiene.py``: that test guards the
license-free-import property in a clean subprocess, so nothing loaded here can leak into it.
"""

from __future__ import annotations

import ast
import inspect

import agentic_mbse.sysml as sysml
import agentic_mbse.sysml.constraint_extraction as constraint_extraction


def test_all_is_sorted_list_of_str() -> None:
    assert isinstance(sysml.__all__, list)
    assert all(isinstance(name, str) for name in sysml.__all__)
    assert sysml.__all__ == sorted(sysml.__all__)


def test_all_matches_lazy_registry() -> None:
    assert set(sysml.__all__) == set(sysml._LAZY)
    assert len(sysml.__all__) == len(set(sysml.__all__))


def test_every_exported_name_resolves() -> None:
    unresolved = [name for name in sysml.__all__ if getattr(sysml, name, None) is None]
    assert unresolved == []


def test_star_import_respects_all() -> None:
    namespace: dict[str, object] = {}
    exec("from agentic_mbse.sysml import *", namespace)  # noqa: S102
    imported = {name for name in namespace if not name.startswith("__")}
    assert imported == set(sysml.__all__)


def test_type_checking_imports_match_lazy_registry() -> None:
    """The static TYPE_CHECKING imports and the runtime registry name the same set."""
    tree = ast.parse(inspect.getsource(sysml))
    static_names: set[str] = set()
    for node in tree.body:
        is_type_checking_block = (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
        )
        if not is_type_checking_block:
            continue
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.ImportFrom):
                static_names.update(alias.asname or alias.name for alias in stmt.names)
    assert static_names == set(sysml._LAZY)


def test_constraint_extraction_star_import_includes_all_public_extractors() -> None:
    assert set(constraint_extraction.__all__) == {
        "extract_constraint_facts",
        "extract_expression_ir",
        "extract_identified_constraint_facts",
    }
    namespace: dict[str, object] = {}
    exec("from agentic_mbse.sysml.constraint_extraction import *", namespace)  # noqa: S102
    assert namespace["extract_constraint_facts"] is constraint_extraction.extract_constraint_facts
    assert namespace["extract_expression_ir"] is constraint_extraction.extract_expression_ir
    assert (
        namespace["extract_identified_constraint_facts"]
        is constraint_extraction.extract_identified_constraint_facts
    )

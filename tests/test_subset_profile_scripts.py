"""The subset-profile dev scripts write only where they are told, and share one isolated-tree module.

EXEC-SUBSET-CONTRACT Item 2a (spec Boundaries, design D13): Item 1's scripts are reused only once
their output path is a parameter, so nothing writes into the archived Item 1 folder. Pure: reads
the script sources and runs `codegen_suite.py`'s argument parser, which exits before any git or
SysIDE work.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "subset_profile"
CODEGEN_SUITE = SCRIPTS / "codegen_suite.py"
ISOLATED_TREE = SCRIPTS / "isolated_tree.py"
ARCHIVE = ".project/completed"

# What `codegen_suite.py` builds its tree with (design D13).
SUITE_HELPERS = {
    "build_tree",
    "child_env",
    "read_identity",
    "read_license_key",
    "resolve_rev",
    "sibling_state",
    "IsolationBreachError",
}


def _string_constants(path: Path) -> list[str]:
    return [
        node.value
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def _names_bound_at_module_level(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.FunctionDef | ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names |= {t.id for t in node.targets if isinstance(t, ast.Name)}
    return names


def _imported_from(path: Path, module: str) -> set[str]:
    return {
        alias.name
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.ImportFrom) and node.module == module
        for alias in node.names
    }


@pytest.mark.parametrize("missing", ["--out", "--codegen-rev"])
def test_codegen_suite_run_requires_an_output_directory_and_a_codegen_revision(missing):
    argv = {"--agentic-rev": "HEAD", "--label": "x", "--out": "/tmp/x", "--codegen-rev": "HEAD"}
    del argv[missing]
    done = subprocess.run(
        [sys.executable, str(CODEGEN_SUITE), "run", *(a for kv in argv.items() for a in kv)],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 2, done.stderr
    assert f"the following arguments are required: {missing}" in done.stderr


@pytest.mark.parametrize("script", sorted(SCRIPTS.glob("*.py")), ids=lambda p: p.name)
def test_no_script_names_the_archive(script):
    archived = [s for s in _string_constants(script) if ARCHIVE in s or s.strip("/") == "completed"]
    assert archived == [], f"{script.name} names the archive: {archived}"


def test_isolated_tree_defines_every_helper_codegen_suite_imports():
    imported = _imported_from(CODEGEN_SUITE, "isolated_tree")
    assert SUITE_HELPERS <= imported
    assert imported <= _names_bound_at_module_level(ISOLATED_TREE)

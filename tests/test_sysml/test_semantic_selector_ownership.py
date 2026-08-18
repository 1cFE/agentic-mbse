"""Agentic's raw-selector ownership manifest and its symbol-absence inventory.

The mirror of Codegen's ownership harness.  Agentic owns operand materialization, mapped
metatype and index recognition, exact expression targets, authored reference form, and the
shared depth budget.  After `semantic-evidence/v2` lands, every raw read of the reviewed
selectors must sit inside that owned boundary, and the permissive helpers that let a caller
rebuild a path by hand must be gone.

At `A_base` neither holds.  `REVIEWED_MODULES` is the target boundary, so
`test_raw_selector_reads_stay_inside_the_owned_boundary` is a recorded red naming each
module that still reads a selector outside it, and `test_permissive_symbols_are_absent` is a
recorded red naming each surviving helper.

See `.project/active/stop-reinventing-the-parser/design.md#checked-consumer-and-ownership-manifests`.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "src" / "agentic_mbse"

REVIEWED_SELECTORS = frozenset({"operands", "referent", "target_feature", "chaining_features"})

#: The modules allowed to read a raw selector once the closed boundary exists.  The
#: inspector owns acquisition; the adapter owns the metatype query it delegates to.
REVIEWED_MODULES = (
    "sysml/reference_use.py",
    "sysml/syside_adapter.py",
)

#: Permissive identifiers that must not survive.  Each one lets a consumer reconstruct or
#: ignore evidence instead of receiving a closed value.
PERMISSIVE_SYMBOLS = (
    "has_index_segment",
    "feature_reference_facts",
    "feature_chain_facts",
    "extract_feature_chain_segments",
    "extract_feature_chain_name",
    "extract_feature_reference_name",
)


def _modules() -> list[Path]:
    return sorted(PACKAGE_ROOT.rglob("*.py"))


def _selector_reads(path: Path) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Attribute) and node.attr in REVIEWED_SELECTORS:
            found.add(node.attr)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value in REVIEWED_SELECTORS
        ):
            found.add(str(node.args[1].value))
    return found


def test_raw_selector_reads_stay_inside_the_owned_boundary() -> None:
    """Recorded red at `A_base`: selectors are read well outside the reviewed modules."""
    outside: list[str] = []
    for path in _modules():
        module = path.relative_to(PACKAGE_ROOT).as_posix()
        if module in REVIEWED_MODULES:
            continue
        for selector in sorted(_selector_reads(path)):
            outside.append(f"{module}::{selector}")
    assert not outside, f"raw selector reads outside the owned boundary: {outside}"


def test_the_reviewed_boundary_modules_exist() -> None:
    """Recorded red at `A_base`: `sysml/reference_use.py` is not written yet.

    An exclusion list that names an absent module is an exemption nobody exercises, so the
    manifest pins existence rather than trusting the name.
    """
    missing = [module for module in REVIEWED_MODULES if not (PACKAGE_ROOT / module).is_file()]
    assert not missing, f"reviewed boundary names an absent module: {missing}"


def test_permissive_symbols_are_absent() -> None:
    """Recorded red at `A_base`: every permissive helper and the bool marker still exist."""
    surviving: list[str] = []
    for path in _modules():
        module = path.relative_to(PACKAGE_ROOT).as_posix()
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name in PERMISSIVE_SYMBOLS:
                    surviving.append(f"{module}::{node.name}")
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id in PERMISSIVE_SYMBOLS:
                    surviving.append(f"{module}::{node.target.id}")
    assert not surviving, f"permissive symbols that must not survive: {sorted(surviving)}"


def test_no_permissive_symbol_is_publicly_exported() -> None:
    """Recorded red at `A_base`: the barrel must not re-export a deleted helper."""
    from agentic_mbse import sysml

    exported = set(getattr(sysml, "__all__", ()))
    assert not exported & set(PERMISSIVE_SYMBOLS), sorted(exported & set(PERMISSIVE_SYMBOLS))


@pytest.mark.parametrize("selector", sorted(REVIEWED_SELECTORS))
def test_the_scanner_finds_each_reviewed_selector(selector: str, tmp_path: Path) -> None:
    """Anti-vacuity: an empty selector set would make the boundary test pass silently."""
    module = tmp_path / "mutant.py"
    module.write_text(f"def consume(node):\n    return node.{selector}\n")
    assert _selector_reads(module) == {selector}


def test_the_scanner_ignores_an_unrelated_attribute(tmp_path: Path) -> None:
    module = tmp_path / "clean.py"
    module.write_text("def consume(node):\n    return node.qualified_name\n")
    assert _selector_reads(module) == set()

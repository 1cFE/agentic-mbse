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

#: The gate is about *SysIDE* selectors, so it scans the modules that can actually hold a
#: SysIDE node — the ones reaching the parser through the adapter.  Without this scope the
#: name-based scan also flags `operands` on the neutral `ExpressionIR` dataclasses, which
#: are not parser nodes at all: `sysml/executable_profile.py` is pinned license-free and
#: provably never imports syside, so its `node.operands` is a plain field read.  This
#: mirrors the scoping the Phase-1 audit required on the Codegen side (Finding 3): key the
#: gate on the adapter, which is how this repository actually reaches the parser.
ADAPTER_IMPORT = "agentic_mbse.sysml.syside_adapter"

#: Permissive identifiers that must not survive.  Each one lets a consumer reconstruct or
#: ignore evidence instead of receiving a closed value.
#:
#: Audit Minor 5: Phase 1 listed only six names and omitted four of the seven ordered
#: deletions, so the gate could have gone green while `extract_feature_refs`,
#: `ResolvedSemanticReferenceFact`, and `ExpressionRef` were still in the tree.  All seven
#: ordered deletions are covered here now.  `BindingInfo.references` is the one that cannot
#: be a bare name — `references` is far too common a local identifier to scan for — so it
#: has its own class-scoped check below.
PERMISSIVE_SYMBOLS = (
    "extract_feature_refs",
    "feature_reference_facts",
    "feature_chain_facts",
    "ResolvedSemanticReferenceFact",
    "has_index_segment",
    "ExpressionRef",
    "extract_feature_chain_segments",
    "extract_feature_chain_name",
    "extract_feature_reference_name",
)

#: The seventh ordered deletion, as (class, attribute).  Scanned in class scope so an
#: unrelated local named `references` cannot make the gate red or green by accident.
PERMISSIVE_CLASS_ATTRIBUTES = (("BindingInfo", "references"),)


def _modules() -> list[Path]:
    return sorted(PACKAGE_ROOT.rglob("*.py"))


def _imported_modules(path: Path) -> set[str]:
    """Every module name this file imports, read from its parsed import statements."""
    imported: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            imported.add(node.module)
            imported.update(f"{node.module}.{alias.name}" for alias in node.names)
    return imported


def _reaches_the_parser(path: Path) -> bool:
    """Whether a module can hold a live SysIDE node.

    The adapter itself is the parser gateway, so it is in scope by definition; every other
    module reaches SysIDE only by importing it.

    Audit m2: this used to be `ADAPTER_IMPORT in path.read_text()`, a substring test that a
    docstring or a comment naming the adapter would satisfy, and that a re-exported or
    aliased import would not.  The scope is now read off the parsed import statements.
    """
    if path.relative_to(PACKAGE_ROOT).as_posix() == "sysml/syside_adapter.py":
        return True
    return ADAPTER_IMPORT in _imported_modules(path)


def _scanned_modules() -> list[Path]:
    return [path for path in _modules() if _reaches_the_parser(path)]


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
    for path in _scanned_modules():
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


def _class_attribute_survives(path: Path, class_name: str, attribute: str) -> bool:
    for node in ast.walk(ast.parse(path.read_text())):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for statement in node.body:
            target = None
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                target = statement.target.id
            elif isinstance(statement, ast.Assign):
                names = [t.id for t in statement.targets if isinstance(t, ast.Name)]
                target = names[0] if names else None
            if target == attribute:
                return True
    return False


def test_no_permissive_class_attribute_survives() -> None:
    """Recorded red: `BindingInfo.references` still declares a rebuildable reference list.

    Audit Minor 5's seventh deletion.  Scanned in class scope, so the gate proves the field
    is gone from `BindingInfo` specifically rather than reacting to any local named
    `references`.
    """
    surviving: list[str] = []
    for path in _modules():
        module = path.relative_to(PACKAGE_ROOT).as_posix()
        for class_name, attribute in PERMISSIVE_CLASS_ATTRIBUTES:
            if _class_attribute_survives(path, class_name, attribute):
                surviving.append(f"{module}::{class_name}.{attribute}")
    assert not surviving, f"permissive class attributes that must not survive: {surviving}"


def test_the_class_attribute_scanner_is_not_vacuous(tmp_path: Path) -> None:
    """Anti-vacuity: the scanner must find the field it is looking for, and only there."""
    module = tmp_path / "mutant.py"
    module.write_text(
        "class BindingInfo:\n"
        "    references: list = []\n"
        "\n"
        "class Other:\n"
        "    references: list = []\n"
    )
    assert _class_attribute_survives(module, "BindingInfo", "references")
    assert not _class_attribute_survives(module, "Missing", "references")

    clean = tmp_path / "clean.py"
    clean.write_text("class BindingInfo:\n    reference_uses: tuple = ()\n")
    assert not _class_attribute_survives(clean, "BindingInfo", "references")


def test_every_ordered_deletion_is_covered_by_a_gate() -> None:
    """The gate's own coverage check — audit Minor 5's root cause.

    Phase 1's list drifted from the design's ordered-deletion set without anything
    noticing.  This asserts the two scanners between them name all seven.
    """
    ordered_deletions = {
        "extract_feature_refs",
        "feature_reference_facts",
        "feature_chain_facts",
        "ResolvedSemanticReferenceFact",
        "has_index_segment",
        "ExpressionRef",
        "BindingInfo.references",
    }
    covered = set(PERMISSIVE_SYMBOLS) | {
        f"{class_name}.{attribute}"
        for class_name, attribute in PERMISSIVE_CLASS_ATTRIBUTES
    }
    assert ordered_deletions <= covered, sorted(ordered_deletions - covered)


def test_the_scanned_module_set_admits_neither_everything_nor_nothing() -> None:
    """Anti-vacuity for the adapter scope: it must be a real, non-trivial subset.

    An empty scope would make the boundary test pass without reading anything; a scope of
    every module would drag the neutral IR dataclasses back in and make it fail for a
    reason it is not about.
    """
    scanned = {path.relative_to(PACKAGE_ROOT).as_posix() for path in _scanned_modules()}
    everything = {path.relative_to(PACKAGE_ROOT).as_posix() for path in _modules()}

    assert scanned, "the adapter scope admits nothing"
    assert scanned < everything, "the adapter scope admits everything"
    assert set(REVIEWED_MODULES) <= scanned, "a reviewed boundary module fell out of scope"
    assert "sysml/executable_profile.py" in everything - scanned


def test_no_production_module_reaches_syside_directly() -> None:
    """The scope premise: this repository reaches the parser only through the adapter.

    If a module ever imported `syside` directly, the adapter-keyed scope would stop being
    the right scope, and this test says so before the boundary test goes quietly vacuous.
    """
    direct: list[str] = []
    for path in _modules():
        module = path.relative_to(PACKAGE_ROOT).as_posix()
        if module == "sysml/syside_adapter.py":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            if any(name == "syside" or name.startswith("syside.") for name in names):
                direct.append(module)
    assert not direct, f"modules importing syside outside the adapter: {sorted(set(direct))}"


def test_the_import_scope_is_structural_not_a_substring_match() -> None:
    """Audit m2: prose naming the adapter must not pull a module into scope.

    Both directions matter.  A comment mentioning the adapter is not an import, and a real
    `from ... import` is one however it is spelled.
    """
    prose_only = ast.parse(
        f'''"""A module that only talks about {ADAPTER_IMPORT} in its docstring."""\n'''
    )
    assert not _imported_modules_from_tree(prose_only)

    real = ast.parse(f"from {ADAPTER_IMPORT} import SysideAdapter\n")
    assert ADAPTER_IMPORT in _imported_modules_from_tree(real)

    plain = ast.parse(f"import {ADAPTER_IMPORT}\n")
    assert ADAPTER_IMPORT in _imported_modules_from_tree(plain)


def _imported_modules_from_tree(tree: ast.AST) -> set[str]:
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            imported.add(node.module)
            imported.update(f"{node.module}.{alias.name}" for alias in node.names)
    return imported


@pytest.mark.parametrize("selector", sorted(REVIEWED_SELECTORS))
def test_the_scanner_finds_a_dynamic_getattr_read(selector: str, tmp_path: Path) -> None:
    """Anti-vacuity for the `getattr` branch (audit m7).

    The scanner has two detection branches and only the attribute one was exercised, so a
    regression in the `getattr` branch would have gone unnoticed while the gate stayed
    green.
    """
    module = tmp_path / "mutant_getattr.py"
    module.write_text(f'def consume(node):\n    return getattr(node, "{selector}", None)\n')
    assert _selector_reads(module) == {selector}


def test_the_scanner_ignores_an_unrelated_getattr(tmp_path: Path) -> None:
    module = tmp_path / "clean_getattr.py"
    module.write_text('def consume(node):\n    return getattr(node, "qualified_name", None)\n')
    assert _selector_reads(module) == set()

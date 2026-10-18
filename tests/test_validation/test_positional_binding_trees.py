"""The production check reproduces the prototype on the consumer trees (slow; spec Base-3).

Reads checkout paths from `POSITIONAL_BINDING_FUSION_TEA_REPO` and `POSITIONAL_BINDING_DC3_REPO`
and skips with the missing variable's name otherwise. Each test exports its pinned revision with
`git archive` into a temp directory (the checkouts are never written) and runs the production
L2 on its `models/`. fusion-tea uses the committed pin list through the override options, so
every one of the 125 prototype identities must come back pinned and nothing else may appear.
`scripts/positional_binding/run_trees.py` records the same comparison, and more, as evidence.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "positional_binding" / "run_trees.py"

pytestmark = pytest.mark.slow


def run_trees() -> ModuleType:
    spec = importlib.util.spec_from_file_location("positional_run_trees", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look their module up while being built
    spec.loader.exec_module(module)
    return module


def checkout(variable: str) -> Path:
    value = os.environ.get(variable)
    if not value:
        pytest.skip(f"{variable} not set")
    return Path(value)


def test_fusion_tea_matches_the_prototype_identities(tmp_path: Path) -> None:
    repo = checkout("POSITIONAL_BINDING_FUSION_TEA_REPO")
    rt = run_trees()
    export = tmp_path / "fusion-tea"
    rt.export_tree(repo, rt.resolve_rev(repo, rt.FUSION_TEA_REV), export)
    run = rt.run_l2(export / "models", positional_pins=rt.BASELINE, pin_root=export)
    difference = rt.compare_identities(run.finding_identities(), rt.reference_identities())
    assert difference == {"added": [], "missing": [], "changed_target": []}
    assert run.count("L2_POSITIONAL_BINDING", "warning") == 125
    assert run.count("L2_POSITIONAL_BINDING", "error") == 0
    assert run.count("L2_POSITIONAL_PIN_STALE") == 0
    assert run.unverifiable() == 0
    assert int(run.metrics["Positional inputs inspected"]) > 0


@pytest.mark.parametrize("rev", ["808464d", "60b44d5"])
def test_dc3_has_no_positional_finding_and_nothing_unverifiable(tmp_path: Path, rev: str) -> None:
    repo = checkout("POSITIONAL_BINDING_DC3_REPO")
    rt = run_trees()
    export = tmp_path / "dc3"
    rt.export_tree(repo, rt.resolve_rev(repo, rev), export)
    run = rt.run_l2(export / "models")
    assert run.count("L2_POSITIONAL_BINDING") == 0
    assert run.unverifiable() == 0
    assert int(run.metrics["Positional inputs inspected"]) > 0
    assert run.outcomes()["implicit_matching"] == rt.DC3_REVS[rev]

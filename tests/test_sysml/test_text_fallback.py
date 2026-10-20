"""`reconstruct_expression`'s output is unchanged by the text-fallback predicate (Item 3 Phase 6).

The texts were recorded from `expression.py` at `ebb3d467`, before its dispatch was shared with
`falls_to_text_fallback` (`scripts/l6_subset/record_reconstruct_texts.py`). Item 2's agent
depends on `reconstruct_expression`, so every text must match exactly (design D12a, I4).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.expression import (
    falls_to_text_fallback,
    reconstruct_expression,
    text_fallback_nodes,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from tests.helpers.reconstruct_texts import (
    FIXTURES,
    RECORD,
    RELOCATIONS,
    reconstruct_file,
    recorded_path,
)


@pytest.mark.syside
def test_reconstruct_expression_output_unchanged_on_every_fixture_expression():
    recorded = json.loads(RECORD.read_text(encoding="utf-8"))
    relocations = json.loads(RELOCATIONS.read_text(encoding="utf-8"))
    assert len(recorded) >= 268
    assert set(relocations["moved"]) | set(relocations["left"]) <= set(recorded)
    assert [k for k in relocations["moved"] if (FIXTURES / k).exists()] == []
    paths = {relative: recorded_path(relative, relocations) for relative in recorded}
    now = {relative: reconstruct_file(path) for relative, path in paths.items() if path is not None}
    changed = sorted(relative for relative in now if now[relative] != recorded[relative])
    assert changed == []
    assert len(now) == len(recorded) - len(relocations["left"])


# ---- the shared dispatch ----------------------------------------------------------------------

SHAPES = """package fx {
    private import ScalarValues::*;
    part def Cell { attribute mass : Real = 2.0; }
    part def Pack {
        part cells : Cell[3];
        attribute c = new Cell();
        attribute y : Real = if true ? 1.0 else 2.0;
        attribute z = cells.mass as Real;
        attribute b : Boolean = cells istype Cell;
        attribute m = Cell.metadata;
    }
}
"""


@pytest.fixture(scope="module")
def pack_values(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    path = tmp_path_factory.mktemp("fallback") / "pack.sysml"
    path.write_text(SHAPES, encoding="utf-8")
    model, diagnostics = SysideAdapter.load_model([path])
    assert list(diagnostics.errors) == []
    return {
        str(f.name): f.feature_value_expression
        for f in SysideAdapter.elements_of_type(model, "AttributeUsage")
        if str(f.owning_type.name) == "Pack"
    }


@pytest.mark.syside
def test_falls_to_text_fallback_true_for_constructor_false_for_if_as_istype(pack_values):
    assert falls_to_text_fallback(pack_values["c"])
    for name in ("y", "z", "b"):
        assert not falls_to_text_fallback(pack_values[name]), name
    assert not falls_to_text_fallback("text") and not falls_to_text_fallback(None)


@pytest.mark.syside
def test_text_fallback_nodes_are_the_nodes_reconstruction_renders_with_str(pack_values):
    (node,) = text_fallback_nodes(pack_values["c"])
    assert type(node).__name__ == "ConstructorExpression"
    assert reconstruct_expression(pack_values["c"]) == str(node)
    for name in ("y", "z", "b"):
        assert text_fallback_nodes(pack_values[name]) == (), name


@pytest.mark.syside
def test_text_fallback_nodes_raises_where_reconstruction_raises(pack_values):  # Cell.metadata
    with pytest.raises(SemanticEvidenceError) as reconstructed:
        reconstruct_expression(pack_values["m"])
    with pytest.raises(SemanticEvidenceError) as walked:
        text_fallback_nodes(pack_values["m"])
    assert walked.value.code is reconstructed.value.code
    assert walked.value.code is SemanticEvidenceCode.OPERAND_ITERATION_FAILED

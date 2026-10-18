"""Native SysIDE values of the positional-binding counterexample (spec XR-1).

`calc def Sub { in a; in b; return r = a - b; }` with a = 10 and b = 3 is meant to give 7.
Written with the inputs reversed and unprefixed, SysIDE binds them by position and gives -7;
the generated/TEAx route wires by name and gives 7 (`evidence/cross-route/`). These tests pin
the native side on the retained prototype fixtures, evaluated the way the prototype did
(`.project/concepts/convince-me-exec-subset/evidence/04-eval.py:46-54`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.sysml.syside_adapter import get_syside

syside = get_syside()

FIXTURES = Path(__file__).parent.parent / "fixtures" / "positional_binding" / "native_values"


def _part(model: Any, name: str) -> Any:
    (part,) = [p for p in model.elements(syside.PartUsage) if p.name == name]
    return part


def _evaluate(scope: Any, feature: Any, model: Any) -> tuple[Any, list[str]]:
    """The native value and the evaluation report's diagnostic messages."""
    value, report = syside.Compiler().evaluate_feature(feature, scope=scope, stdlib=model.lib)
    return value, [str(d.message) for d in report.diagnostics]


def evaluate_r(path: Path) -> tuple[Any, list[str]]:
    """Native value of `q.v = c.r` in a `sub_*.sysml` fixture."""
    model, _ = syside.load_model([str(path)])
    q = _part(model, "q")
    (v,) = [f for f in q.owned_features.collect() if f.name == "v"]
    return _evaluate(q, v, model)


def evaluate_plant_result(directory: Path) -> tuple[Any, list[str]]:
    """Native value of `plant.result` in a retained generator fixture."""
    model, _ = syside.load_model([str(directory / "model.sysml")])
    plant = _part(model, "plant")
    (result,) = [f for f in plant.inherited_features.collect() if f.name == "result"]
    return _evaluate(plant, result, model)


@pytest.mark.parametrize(
    ("spelling", "expected"),
    [("in_order", 7), ("reversed", -7), ("reversed_byname", 7), ("rename", 7)],
)
def test_sub_native_value(spelling: str, expected: int) -> None:
    assert evaluate_r(FIXTURES / f"sub_{spelling}.sysml") == (expected, [])


def test_mixed_spelling_has_no_native_value() -> None:
    """`in b = 3; in :>> a = 10;` puts both inputs on `Sub::a`; `Sub::b` is unbound.

    The evaluation reports a type error on `a - b` instead of returning a number.
    """
    assert evaluate_r(FIXTURES / "sub_mixed.sysml") == (
        None,
        ["Invalid operator '-' for types 'integer' and 'element'"],
    )


@pytest.mark.parametrize(("fixture", "expected"), [("gen_byname", 7), ("gen_reversed", -7)])
def test_generator_fixture_native_value(fixture: str, expected: int) -> None:
    assert evaluate_plant_result(FIXTURES / fixture) == (expected, [])

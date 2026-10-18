"""The occurrence port matches sysml-codegen `b5663c07` on the parity seed (design invariant 10).

Each case under `tests/fixtures/subset_profile/occurrence/` holds a model and the
`expected.json` that codegen's own oracle wrote for it
(`scripts/subset_profile/occurrence_parity.py capture`). No expectation is hand-written, and this
test needs no codegen checkout. Abort cases match on build stage and mapped generator code.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_mbse.sysml.occurrence_extraction import extract_occurrence_structure
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from tests.helpers.occurrence_oracle_schema import (
    schema_differences,
    strip_oracle_only_fields,
    to_oracle_schema,
)
from tests.helpers.subset_probe_judge import PINNED_CODEGEN_REV, PINNED_SYSIDE_VERSION

SEED_DIR = Path(__file__).parents[1] / "fixtures" / "subset_profile" / "occurrence"
SEED = sorted(d for d in SEED_DIR.iterdir() if d.is_dir())


def model_paths(case: Path) -> list[Path]:
    return sorted(case.glob("*.sysml"))


@pytest.mark.parametrize("case", SEED, ids=lambda p: p.name)
def test_port_matches_codegen_oracle(case: Path) -> None:
    model, _ = SysideAdapter.load_model(model_paths(case))
    actual = to_oracle_schema(extract_occurrence_structure(model))
    expected = strip_oracle_only_fields(json.loads((case / "expected.json").read_text()))
    assert actual == expected, "\n".join(schema_differences(expected, actual))


@pytest.mark.parametrize("case", SEED, ids=lambda p: p.name)
def test_every_expectation_is_an_oracle_capture_at_the_pin(case: Path) -> None:
    """A hand-written expectation would carry no oracle identity or cross-check."""
    captured = json.loads((case / "expected.json").read_text())
    identity = captured["identity"]
    assert identity["codegen_rev"] == PINNED_CODEGEN_REV
    assert identity["syside_version"] == PINNED_SYSIDE_VERSION
    assert "full" in captured and "names" in captured
    assert captured["inputs"] == [f"cases/{case.name}/{p.name}" for p in model_paths(case)]


def test_the_seed_is_the_planned_set() -> None:
    """The 11 F1 edge fixtures, the 22 prototype fixtures and P-6's effective-declaration case."""
    names = {case.name for case in SEED}
    assert len(names) == 34
    assert sum(n.startswith("f1_") for n in names) == 12
    assert "f1_effective_declaration_slot" in names

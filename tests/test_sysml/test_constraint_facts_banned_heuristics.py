"""Guard: neither S1 banned heuristic reappears in the constraint-facts production modules.

Grep-level assertions over source text, not behavior — the two heuristics S1's capture module
used (`tests/constraint_fact_learning.py`, retired by D7) are banned outright, so their absence
is checked directly rather than inferred from test outcomes.
"""

from __future__ import annotations

from pathlib import Path

MODULES = [
    Path("src/agentic_mbse/sysml/expression_facts.py"),
    Path("src/agentic_mbse/sysml/constraint_facts.py"),
    Path("src/agentic_mbse/sysml/constraint_extraction.py"),
]


def _combined_source() -> str:
    return "\n".join(module.read_text() for module in MODULES)


def test_modules_exist() -> None:
    for module in MODULES:
        assert module.is_file(), f"{module} not found"


def test_no_namespace_prefix_classification() -> None:
    """The banned inline-vs-definition-typed discriminator: a namespace-prefix `startswith` test."""
    source = _combined_source()
    assert "ConstraintFactShapeProbe" not in source
    assert "startswith(" not in source


def test_no_unit_suffix_strip() -> None:
    """The banned dimension/quantity strip: `removesuffix("Unit")` / `removesuffix("Value")`."""
    source = _combined_source()
    assert 'removesuffix("Unit")' not in source
    assert "removesuffix('Unit')" not in source
    assert 'removesuffix("Value")' not in source
    assert "removesuffix('Value')" not in source
    assert "removesuffix(" not in source

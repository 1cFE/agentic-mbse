"""Durable constraint guidance must describe the executable-profile v3 contract."""

from pathlib import Path


def test_constraint_guide_has_one_four_outcome_contract() -> None:
    guide = (
        Path(__file__).resolve().parents[1] / "docs" / "patterns" / "constraints.md"
    ).read_text(encoding="utf-8")

    assert "one of three" not in guide
    assert "three-outcome" not in guide
    for outcome in ("ADMIT", "BLOCK", "NON_NUMERICAL", "UNASSESSED"):
        assert outcome in guide

    opening = guide.split("`require` and `assume` constraints", maxsplit=1)[0]
    assert "L6 emits one named ERROR per blocked construct" in opening

    subtype_summary = guide.split(
        "## Subtype-aware validation: `assert` constraints are now visible", maxsplit=1
    )[1]
    assert "`assert` predicates land in admitted, blocked, or non-numerical" in subtype_summary
    assert "**L6** emits one named ERROR per blocked construct" in subtype_summary
    assert "WARNING per blocked construct" not in guide

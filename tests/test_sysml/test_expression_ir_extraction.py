"""Live coverage: the success criteria that need the cutover extractor (Phase 3).

Spelling distinctness, an exercised unsupported node, unit-annotation source+resolved
fidelity, and byte-stable round-trip over real facts — at the pinned pair
`(constraint-facts/v3, expression-ir/v1)`, within a load and across independent loads.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_mbse.sysml.constraint_extraction import extract_identified_constraint_facts
from agentic_mbse.sysml.constraint_facts import ConstraintFacts, parse, serialize
from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)
from agentic_mbse.sysml.expression_ir import ExpressionIR
from agentic_mbse.sysml.syside_adapter import get_syside

syside = get_syside()

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "expression_ir"
OPERATOR_FIDELITY = FIXTURE_DIR / "operator_fidelity.sysml"
TYPE_UNITS = (
    Path(__file__).parent.parent / "fixtures" / "constraint_fact_shapes" / "type_units.sysml"
)


def _extract(*paths: Path) -> ConstraintFacts:
    model, _diagnostics = syside.try_load_model([str(path) for path in paths])
    return extract_identified_constraint_facts(model).facts


def _by_name(facts: ConstraintFacts, name: str) -> Any:
    return next(usage for usage in facts.usages if usage.identity.name == name)


def _operator_strings(node: ExpressionIR | None, acc: list[str]) -> None:
    if node is None:
        return
    if node.kind == "operator":
        acc.append(node.operator)
        for operand in node.operands:
            _operator_strings(operand, acc)
    elif node.kind == "unit":
        _operator_strings(node.value, acc)
    elif node.kind == "invocation":
        for argument in node.arguments:
            _operator_strings(argument, acc)


def test_caret_and_power_stay_distinct() -> None:
    facts = _extract(OPERATOR_FIDELITY)
    ops: list[str] = []
    _operator_strings(_by_name(facts, "caret_form").predicate, ops)
    _operator_strings(_by_name(facts, "power_form").predicate, ops)
    assert "^" in ops
    assert "**" in ops


def test_unary_minus_preserved_as_one_operand_operator() -> None:
    facts = _extract(OPERATOR_FIDELITY)
    predicate = _by_name(facts, "unary_minus_form").predicate
    assert predicate is not None
    minus = predicate.operands[0]
    assert minus.kind == "operator"
    assert minus.operator == "-"
    assert len(minus.operands) == 1


def test_unsupported_node_is_exercised() -> None:
    facts = _extract(OPERATOR_FIDELITY)
    node = _by_name(facts, "unsupported_form").predicate
    assert node is not None
    assert node.kind == "unsupported"
    assert node.node_kind
    assert node.diagnostic


def test_unit_annotation_keeps_source_and_resolved() -> None:
    facts = _extract(TYPE_UNITS)
    predicate = _by_name(facts, "quantity_same_unit").predicate
    assert predicate is not None
    unit_node = predicate.operands[0]
    assert unit_node.kind == "unit"
    assert unit_node.unit_text == "m"
    assert unit_node.operand_type.unit is not None
    assert unit_node.operand_type.unit.unit == "SI::metre"


def test_leaf_facts_are_the_frozen_leaf_types() -> None:
    facts = _extract(TYPE_UNITS)
    predicate = _by_name(facts, "quantity_same_unit").predicate
    assert predicate is not None
    unit_node = predicate.operands[0]
    literal_node = unit_node.value
    assert isinstance(literal_node.literal, LiteralFact)
    assert isinstance(literal_node.operand_type, OperandTypeFact)
    assert isinstance(unit_node.operand_type.unit, UnitFact)

    reference_node = _by_name(facts, "unresolved_operand").predicate.operands[0]
    assert isinstance(reference_node.reference, FeatureReferenceFact)


def test_round_trip_over_real_facts_at_pinned_version_pair() -> None:
    facts = _extract(OPERATOR_FIDELITY, TYPE_UNITS)
    once = serialize(facts)
    assert serialize(parse(once)) == once


def test_round_trip_stable_across_independent_loads() -> None:
    first = serialize(_extract(OPERATOR_FIDELITY, TYPE_UNITS))
    second = serialize(_extract(OPERATOR_FIDELITY, TYPE_UNITS))
    assert first == second

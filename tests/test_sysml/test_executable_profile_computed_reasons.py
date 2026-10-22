"""The five computed reason sites in `executable_profile.py` emit only `REASON_CODES` members.

Five sites build a diagnostic reason from a value instead of a literal (re-located at this
revision; the prototype cited the same lines):

- `:542` `_walk_arithmetic`: the reason `_derive_arithmetic_fact` returns.
- `:597` `_walk_value`: ``f"block_{operator}"`` for a value-position ``xor`` / ``implies``.
- `:660` `_walk_comparison`: the reason `classify_equality` returns.
- `:711` `_walk_comparison`: the reason `classify_ordering` returns.
- `:813` `_walk_proposition`: ``f"warn_non_numerical_{operator}"`` for ``xor`` / ``implies``.

Each test drives its site through the walk over every operand fact the closed category
vocabulary allows (`expression_facts.OperandTypeFact`), with every unit state the guards
distinguish, and collects every reason the site emitted. At the three sites whose reason comes
from a helper, the reasons are read from the helper's returns, so a reason another site emits
on the same walk is not counted. Each site's set must equal the set recorded here exactly: a
site that stops emitting a reason, or starts emitting another known one, fails here.
`EligibilityDiagnostic` already refuses an unknown reason at construction.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

import pytest

from agentic_mbse.sysml import executable_profile as ep
from agentic_mbse.sysml.expression_facts import (
    IdentityFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)
from agentic_mbse.sysml.expression_ir import ExpressionIR, LiteralNode, OperatorNode

IDENTITY = IdentityFact(kind="AssertConstraintUsage", name="c", qualified_name="fx::c")
CATEGORIES = ("boolean", "string", "integer", "real", "enum", "quantity", "unresolved", "unknown")
UNITS = (
    None,
    UnitFact(unit=None, dimension="ISQBase::LengthUnit"),
    UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit"),
    UnitFact(unit="SI::millimetre", dimension="ISQBase::LengthUnit"),
    UnitFact(unit="SI::second", dimension="ISQBase::DurationUnit"),
)


ARITHMETIC_REASONS = {
    "block_derived_unit_unsupported",
    "block_incompatible_dimensions",
    "block_malformed_operand_fact",
    "block_unit_conversion_required",
    "block_unitless_dimensioned",
    "block_unknown_exact_unit",
    "block_unresolved_operand",
    "block_unsupported_operand_category",
}
EQUALITY_REASONS = {
    "block_incompatible_dimensions",
    "block_integer_equality_unpreservable",
    "block_malformed_operand_fact",
    "block_real_equality_requires_tolerance",
    "block_unit_conversion_required",
    "block_unitless_dimensioned",
    "block_unknown_exact_unit",
    "block_unresolved_operand",
    "block_unsupported_operand_category",
    "warn_non_numerical_equality",
}
ORDERING_REASONS = {
    "block_incompatible_dimensions",
    "block_malformed_operand_fact",
    "block_ordering_category_pair",
    "block_unit_conversion_required",
    "block_unknown_exact_unit",
    "block_unresolved_operand",
    "block_unsupported_operand_category",
}


@contextmanager
def returns_of(monkeypatch: pytest.MonkeyPatch, name: str) -> Iterator[set[str]]:
    """Collect every reason string the module helper `name` returns while the block runs."""
    seen: set[str] = set()
    helper: Callable[..., Any] = getattr(ep, name)

    def recording(*args: Any) -> Any:
        result = helper(*args)
        if isinstance(result, str) and result != "ok":
            seen.add(result)
        return result

    with monkeypatch.context() as patch:
        patch.setattr(ep, name, recording)
        yield seen


def every_fact() -> list[OperandTypeFact]:
    facts = []
    for category in CATEGORIES:
        for unit in UNITS if category == "quantity" else (None,):
            facts.append(OperandTypeFact(category=category, enumeration=None, unit=unit))
    facts.append(OperandTypeFact(category="enum", enumeration="fx::Mode", unit=None))
    return facts


def leaf(fact: OperandTypeFact) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=1.0, result_type=None), operand_type=fact
    )


def comparison(fact: OperandTypeFact) -> OperatorNode:
    return OperatorNode(operator="<", operands=[leaf(fact), leaf(fact)], operand_type=None)


def reasons_from_value(node: ExpressionIR) -> set[str]:
    result = ep._walk_value(node, IDENTITY, None)
    return {d.reason for d in result} if isinstance(result, list) else set()


def reasons_from_proposition(node: ExpressionIR) -> set[str]:
    diagnostics: list[ep.EligibilityDiagnostic] = []
    ep._walk_proposition(node, IDENTITY, None, diagnostics)
    return {d.reason for d in diagnostics}


def test_site_542_arithmetic_reasons_are_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    with returns_of(monkeypatch, "_derive_arithmetic_fact") as emitted:
        for operator in ("+", "-", "*", "/", "**", "^"):
            for left, right in itertools.product(every_fact(), repeat=2):
                node = OperatorNode(
                    operator=operator, operands=[leaf(left), leaf(right)], operand_type=None
                )
                reasons_from_value(node)
            for only in every_fact():
                reasons_from_value(
                    OperatorNode(operator=operator, operands=[leaf(only)], operand_type=None)
                )
    assert emitted <= ep.REASON_CODES
    assert emitted == ARITHMETIC_REASONS


def test_site_597_value_position_connective_reasons_are_closed() -> None:
    real = OperandTypeFact(category="real", enumeration=None, unit=None)
    emitted = set()
    for operator in ("xor", "implies"):
        node = OperatorNode(operator=operator, operands=[leaf(real), leaf(real)], operand_type=None)
        emitted |= reasons_from_value(node)
    assert emitted == {"block_xor", "block_implies"} <= ep.REASON_CODES


def test_site_660_equality_reasons_are_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    with returns_of(monkeypatch, "classify_equality") as emitted:
        for operator in ("==", "!="):
            for left, right in itertools.product(every_fact(), repeat=2):
                node = OperatorNode(
                    operator=operator, operands=[leaf(left), leaf(right)], operand_type=None
                )
                reasons_from_proposition(node)
    assert emitted <= ep.REASON_CODES
    assert emitted == EQUALITY_REASONS


def test_site_711_ordering_reasons_are_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    with returns_of(monkeypatch, "classify_ordering") as emitted:
        for operator in ("<", "<=", ">", ">="):
            for left, right in itertools.product(every_fact(), repeat=2):
                node = OperatorNode(
                    operator=operator, operands=[leaf(left), leaf(right)], operand_type=None
                )
                reasons_from_proposition(node)
    assert emitted <= ep.REASON_CODES
    assert emitted == ORDERING_REASONS


def test_site_813_proposition_connective_reasons_are_closed() -> None:
    real = OperandTypeFact(category="real", enumeration=None, unit=None)
    emitted = set()
    for operator in ("xor", "implies"):
        node = OperatorNode(
            operator=operator, operands=[comparison(real), comparison(real)], operand_type=None
        )
        emitted |= reasons_from_proposition(node)
    assert emitted == {"warn_non_numerical_xor", "warn_non_numerical_implies"} <= ep.REASON_CODES

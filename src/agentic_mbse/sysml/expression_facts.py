"""Neutral leaf vocabulary and predicate-tree node algebra for constraint facts.

This is the frozen leaf vocabulary S1 (`.project/active/spike-constraint-fact-shapes/`)
proved recoverable from live SysIDE: a feature reference or a literal, each carrying its
type category, enumeration identity, and unit/dimension fact. It is the leaf Item 2's
`ExpressionIR` adopts, so this module imports neither syside nor `constraint_facts` — the
import direction points one way, toward the leaves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "PREDICATE_TREE_SCHEMA_VERSION",
    "ExpressionFact",
    "FeatureReferenceFact",
    "IdentityFact",
    "LiteralFact",
    "OperandTypeFact",
    "UnitFact",
]

PREDICATE_TREE_SCHEMA_VERSION = "predicate-tree/v0"


@dataclass
class IdentityFact:
    """Neutral identity of a SysML element: its metaclass, name, and qualified name.

    ``kind`` is a SysML v2 metaclass name (e.g. ``"AssertConstraintUsage"``) — spec-standardized
    and tool-independent, not a library-coupled leak.
    """

    kind: str | None
    name: str | None
    qualified_name: str | None


@dataclass
class UnitFact:
    """A resolved measurement unit and/or dimension.

    ``unit`` is the exact unit's qualified name (e.g. ``"SI::metre"``); ``dimension`` is the
    measurement-unit-definition qualified name (e.g. ``"ISQBase::LengthUnit"``), reached by
    structural traversal — never by string manipulation. ``unit=None, dimension=<set>`` is the
    first-class "dimension known, exact unit unknown" state.
    """

    unit: str | None
    dimension: str | None


@dataclass
class OperandTypeFact:
    """The recovered type facts for one leaf operand.

    ``category`` is one of ``boolean``/``string``/``integer``/``real``/``enum``/``quantity``,
    or the explicit unresolved states ``unresolved`` (no ``cached_result_type``) / ``unknown``
    (resolved but none of the known categories matched).
    """

    category: str
    enumeration: str | None
    unit: UnitFact | None


@dataclass
class FeatureReferenceFact:
    """A feature reference leaf: source text, resolved target, and chain path.

    Carries no channel/parameter/intermediate role tag (`[HARD]` — that classification is
    codegen's job, not this item's). ``chain_segments`` is empty for a single (non-chained)
    reference and the ordered path names for a feature chain (e.g. ``["sensor", "reading"]``).
    """

    source_name: str | None
    target: IdentityFact | None
    target_types: list[str] = field(default_factory=list)
    chain_segments: list[str] = field(default_factory=list)


@dataclass
class LiteralFact:
    """A literal leaf: its SysML metaclass kind, Python value, and result type."""

    kind: str
    value: Any
    result_type: str | None


@dataclass
class ExpressionFact:
    """One node of the provisional predicate tree.

    Every value-producing node carries ``operand_type`` — a ``reference``/``literal`` leaf, a
    unit-annotation node like ``1 [m]`` (``category="quantity"`` and its ``UnitFact``), and a
    same-unit arithmetic combination like ``1 [m] + 1 [m]``. Only a Boolean-relational or
    connective node (``==``, ``<=``, ``and``, ``not``, ...) is a pure proposition and carries
    ``operand_type=None`` — it is a statement about operands, not a value itself.
    """

    predicate_schema_version: str
    kind: str
    operator: str | None
    operands: list[ExpressionFact]
    reference: FeatureReferenceFact | None
    literal: LiteralFact | None
    operand_type: OperandTypeFact | None

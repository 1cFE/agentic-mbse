"""Neutral leaf vocabulary for the constraint predicate tree.

This is the frozen leaf vocabulary S1 (`.project/active/spike-constraint-fact-shapes/`)
proved recoverable from live SysIDE: a feature reference or a literal, each carrying its
type category, enumeration identity, and unit/dimension fact. It is the leaf `expression_ir`'s
`ExpressionIR` adopts, so this module imports neither syside nor `constraint_facts`/`expression_ir`
— the import direction points one way, toward the leaves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "FeatureReferenceFact",
    "IdentityFact",
    "LiteralFact",
    "OperandTypeFact",
    "UnitFact",
]


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

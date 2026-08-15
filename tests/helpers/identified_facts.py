"""Mint exact identities for a synthetic neutral constraint-fact payload.

The executable profile is reached through `evaluate_identified_profile`, which takes
`IdentifiedConstraintFacts` — neutral facts plus a UUID for every definition and usage,
and, per usage, the UUID of the definition that supplies its predicate. Live extraction
gets those UUIDs from the parser. A test that constructs its own `ConstraintFacts`, or
loads a stored neutral golden, has no parser to ask, so it states the identities here.

`identify` mints them positionally and deterministically. It deliberately does NOT infer
which definition supplies a usage: that association is the one thing the exact route
exists to stop deriving from a name, and a helper that guessed it by qualified name would
put the collapsed name lookup back inside the test's own oracle. A usage that is supplied
by a definition says so, by position, through `typed`.
"""

from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from agentic_mbse.sysml.constraint_extraction import (
    IdentifiedConstraintDefinition,
    IdentifiedConstraintFacts,
    IdentifiedConstraintUsage,
)
from agentic_mbse.sysml.constraint_facts import ConstraintFacts

# Disjoint, stable, and far from the small ints tests pick by hand for one-off UUIDs.
_DEFINITION_ID_BASE = 0xD0000
_USAGE_ID_BASE = 0xE0000


def definition_id(index: int) -> UUID:
    """The UUID `identify` mints for the definition at `index`."""
    return UUID(int=_DEFINITION_ID_BASE + index)


def usage_id(index: int) -> UUID:
    """The UUID `identify` mints for the usage at `index`."""
    return UUID(int=_USAGE_ID_BASE + index)


def identify(
    facts: ConstraintFacts, *, typed: Mapping[int, int] | None = None
) -> IdentifiedConstraintFacts:
    """Wrap neutral `facts` in the exact identity sidecars the profile route reads.

    Args:
        facts: the neutral payload, carried through unchanged.
        typed: usage position -> definition position, for each usage whose predicate
            comes from a definition. Every other usage carries no effective definition,
            which is what an inline or unassessed usage has.

    Raises:
        IndexError: `typed` names a usage or definition position that does not exist.
            A test that mis-states the association gets told, rather than silently
            evaluating against no definition at all.
    """
    associations = dict(typed or {})
    for usage_index, definition_index in associations.items():
        if not 0 <= usage_index < len(facts.usages):
            raise IndexError(f"no usage at position {usage_index}")
        if not 0 <= definition_index < len(facts.definitions):
            raise IndexError(f"no definition at position {definition_index}")

    return IdentifiedConstraintFacts(
        facts=facts,
        definitions=tuple(
            IdentifiedConstraintDefinition(definition_id(index), definition)
            for index, definition in enumerate(facts.definitions)
        ),
        usages=tuple(
            IdentifiedConstraintUsage(
                usage_id(index),
                definition_id(associations[index]) if index in associations else None,
                usage,
            )
            for index, usage in enumerate(facts.usages)
        ),
    )

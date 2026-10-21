"""Pure facts about how each authored calc or constraint input redefines its formals.

For every authored input of a calculation or constraint owner (usage or definition,
including requirements, cases and ``assert constraint``), the fact records its declared
name, direction and role, and every redefinition SysIDE resolved for it, each marked
implied (by position) or explicit (``:>>`` or ``redefines``). The positional-binding check
(`validation/positional_binding.py`) reads these facts and nothing else from SysIDE.

Status: L2-internal. This family has no version marker and is not a surface sysml-codegen
should consume (design D1). Promoting it needs its own item.

The extraction (`parameter_redefinition_extraction.py`) is total: every inspected owner and
input yields exactly one fact or one :class:`RedefinitionFailure`. An owner or input whose
type, supertype or redefinition target did not resolve is a failure, never a fact (D19).

This module imports nothing from SysIDE (design I6).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation

__all__ = [
    "Direction",
    "InputRedefinitionFact",
    "Origin",
    "ParameterRedefinitionFacts",
    "ParameterRole",
    "RedefinedFormal",
    "RedefinitionFailure",
    "RedefinitionFailureCause",
]


class Origin(StrEnum):
    """Whether SysIDE implied the redefinition by position or the author wrote it."""

    EXPLICIT = "explicit"
    IMPLIED = "implied"


class ParameterRole(StrEnum):
    """An input's role, read from the type of its owning membership."""

    ORDINARY = "ordinary"
    SUBJECT = "subject"
    ACTOR = "actor"
    STAKEHOLDER = "stakeholder"


class Direction(StrEnum):
    """The input directions the fact records; ``out`` and return parameters are not inputs."""

    IN = "in"
    INOUT = "inout"


@dataclass(frozen=True)
class RedefinedFormal:
    """One formal an input redefines.

    ``name`` is the formal's effective name (SysIDE ``name``), which is what a positional
    slot is called; ``None`` for an unnamed formal. ``owning_type`` is the type that declares
    the formal: a definition, or a usage when a parent usage restates its inputs.
    """

    formal: ElementRef
    name: str | None
    owning_type: ElementRef
    role: ParameterRole
    origin: Origin


@dataclass(frozen=True)
class InputRedefinitionFact:
    """One authored input and every redefinition SysIDE resolved for it.

    ``declared_name`` is what the author wrote (SysIDE ``declared_name``): ``None`` for
    ``in : Real = 10`` and for ``in :>> b``, where SysIDE's ``name`` would instead fall back
    to the redefined formal's name. ``redefinitions`` keeps SysIDE's order (type order for a
    multiply typed owner).
    """

    owner: ElementRef
    input: ElementRef
    declared_name: str | None
    direction: Direction
    role: ParameterRole
    location: SafeLocation
    redefinitions: tuple[RedefinedFormal, ...]

    def sort_key(self) -> tuple[tuple[str, int, str], str, str, tuple[tuple[str, str], ...]]:
        """Location, then what the fact says; never the element id.

        An anonymous owner's inputs have no qualified name, and SysIDE gives anonymous
        elements a fresh UUIDv4 on every load, so an id tie-break would order two inputs on
        one line at random. Facts this key cannot separate say the same thing.
        """
        return (
            self.location.sort_key(),
            self.owner.qualified_name or "",
            self.declared_name or "",
            tuple((r.formal.qualified_name or "", r.origin.value) for r in self.redefinitions),
        )


class RedefinitionFailureCause(StrEnum):
    """Why an owner or input yielded no fact. Closed; each renders as its own reason code."""

    #: The owner sweep raised: the whole population is missing. Recorded once, no subject.
    OWNERS_UNLISTED = "OWNERS_UNLISTED"
    #: The owner's document tier could not be read, so it is unknown whether it is authored.
    DOCUMENT_TIER_UNREADABLE = "DOCUMENT_TIER_UNREADABLE"
    #: The owner's explicit type, supertype, redefinition or subsetting target is a SysIDE placeholder.
    UNRESOLVED_OWNER_TYPE = "UNRESOLVED_OWNER_TYPE"
    #: The owner's owned features, or their relationships, could not be listed.
    INPUTS_UNLISTED = "INPUTS_UNLISTED"
    #: The input's owning membership could not be read or classified.
    ROLE_UNREADABLE = "ROLE_UNREADABLE"
    #: The input's relationships could not be read.
    REDEFINITIONS_UNREADABLE = "REDEFINITIONS_UNREADABLE"
    #: One of the input's redefinitions targets a SysIDE placeholder.
    UNRESOLVED_INPUT_REDEFINITION = "UNRESOLVED_INPUT_REDEFINITION"
    #: A redefinition has no target, or its target's name, owning type or role is unreadable.
    TARGET_UNREADABLE = "TARGET_UNREADABLE"
    #: SysIDE gave the owner, input, target or owning type no usable identity.
    IDENTITY_UNAVAILABLE = "IDENTITY_UNAVAILABLE"


_NO_SUBJECT = SafeLocation(None, None, None)


@dataclass(frozen=True)
class RedefinitionFailure:
    """One owner or input whose redefinitions could not be established.

    ``subject`` is where the owner or input was authored, as far as SysIDE could say;
    ``None`` only for :attr:`RedefinitionFailureCause.OWNERS_UNLISTED`.
    """

    subject: SafeLocation | None
    cause: RedefinitionFailureCause
    detail: str

    def __post_init__(self) -> None:
        if (self.subject is None) != (self.cause is RedefinitionFailureCause.OWNERS_UNLISTED):
            raise ValueError("only OWNERS_UNLISTED has no subject, and it never has one")

    def sort_key(self) -> tuple[tuple[str, int, str], str, str]:
        return ((self.subject or _NO_SUBJECT).sort_key(), self.cause.value, self.detail)


@dataclass(frozen=True)
class ParameterRedefinitionFacts:
    """Every input fact and every failure from one model, each in its stated sort order.

    ``owners_enumerated`` is false when the owner sweep itself failed; ``owners_inspected``
    counts the authored (non-library) owners examined, including those that failed.
    """

    owners_enumerated: bool
    owners_inspected: int
    facts: tuple[InputRedefinitionFact, ...]
    failures: tuple[RedefinitionFailure, ...]

    def __post_init__(self) -> None:
        if list(self.facts) != sorted(self.facts, key=InputRedefinitionFact.sort_key):
            raise ValueError("facts must be sorted by InputRedefinitionFact.sort_key")
        if list(self.failures) != sorted(self.failures, key=RedefinitionFailure.sort_key):
            raise ValueError("failures must be sorted by RedefinitionFailure.sort_key")

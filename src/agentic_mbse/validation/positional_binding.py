"""The positional-binding check: the rule over parameter-redefinition facts.

In SysML v2 an unprefixed input on a calc or constraint usage (`in b = 3;`) binds to the
definition's parameter by position, not by name (KerML 8.3.3.3.4,
`checkFeatureParameterRedefinition`). A correctly named input written out of definition
order is silently swapped. The facts (`sysml/parameter_redefinition_facts.py`) say, for each
authored input, which formals SysIDE resolved it onto and whether each was implied by
position; :func:`decide` reports every implied target whose name differs from the input's.

`decide` is pure: it imports neither SysIDE nor the filesystem (design I6).

The rule, one outcome per input, in this order (design Implementation Notes):

1. A subject, actor or stakeholder input → ``special_parameter``.
2. No declared name → ``explicit`` if it has an explicit redefinition, else ``anonymous``.
3. No implied redefinition → ``explicit`` if it has an explicit one, else ``new_parameter``.
4. Otherwise each implied target is judged: unnamed (D8), same-named, or accounted for by
   one of the input's own explicit redefinitions (D7) is fine; anything else is a finding,
   one per target (D6). Any finding → ``implicit_mismatch``; else ``explicit`` if it has an
   explicit redefinition; else ``anonymous_target`` if every implied target is unnamed;
   else ``implicit_matching``.

A finding whose target is a subject, actor or stakeholder slot gets its own reason (D20). A
finding whose owner or target has no qualified name has no identity (D9).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.parameter_redefinition_facts import (
    InputRedefinitionFact,
    Origin,
    ParameterRedefinitionFacts,
    ParameterRole,
    RedefinedFormal,
    RedefinitionFailure,
)
from agentic_mbse.validation.positional_pins import FindingIdentity

__all__ = [
    "FindingReason",
    "InputOutcome",
    "PositionalFinding",
    "PositionalResult",
    "decide",
]


class FindingReason(StrEnum):
    """Why an implied target is a finding; rendered as the issue's `reason_code`."""

    SWAP = "POSITIONAL_SWAP"
    SPECIAL_SLOT = "POSITIONAL_SPECIAL_SLOT"


class InputOutcome(StrEnum):
    """What the rule concluded for one input. Names match the prototype's where they exist."""

    EXPLICIT = "explicit"
    ANONYMOUS = "anonymous"
    IMPLICIT_MATCHING = "implicit_matching"
    IMPLICIT_MISMATCH = "implicit_mismatch"
    NEW_PARAMETER = "new_parameter"
    SPECIAL_PARAMETER = "special_parameter"
    ANONYMOUS_TARGET = "anonymous_target"


@dataclass(frozen=True)
class PositionalFinding:
    """One authored input landing by position on a differently named formal.

    ``owner`` is kept beside the identity so a finding without one (D9) can still say whose
    input it is.
    """

    identity: FindingIdentity | None
    owner: ElementRef
    input_name: str
    target: RedefinedFormal
    location: SafeLocation
    reason: FindingReason

    def sort_key(self) -> tuple[tuple[str, int, str], str, str, str]:
        """Location, then owner, input and target names; never an element id (see the fact's key)."""
        return (
            self.location.sort_key(),
            self.owner.qualified_name or "",
            self.input_name,
            self.target.formal.qualified_name or "",
        )


@dataclass(frozen=True)
class PositionalResult:
    """Findings and failures in sorted order, and the count of each outcome.

    ``outcomes`` lists every :class:`InputOutcome` in declaration order, zeros included.
    """

    findings: tuple[PositionalFinding, ...]
    failures: tuple[RedefinitionFailure, ...]
    outcomes: Mapping[InputOutcome, int]

    @property
    def inputs_inspected(self) -> int:
        return sum(self.outcomes.values())


def _accounts_for(
    target: RedefinedFormal, explicit: list[RedefinedFormal], implied: list[RedefinedFormal]
) -> bool:
    """D7: whether the input's own explicit redefinitions account for this implied target."""
    if not explicit:
        return False
    if len({t.owning_type for t in implied}) == 1:
        return True
    return any(e.owning_type == target.owning_type for e in explicit)


def _identity(
    owner: ElementRef, input_name: str, target: RedefinedFormal
) -> FindingIdentity | None:
    if owner.qualified_name is None or target.formal.qualified_name is None:
        return None
    return FindingIdentity(owner.qualified_name, input_name, target.formal.qualified_name)


def _judge(fact: InputRedefinitionFact) -> tuple[InputOutcome, list[PositionalFinding]]:
    """One input's outcome and findings, by the rule's steps in order."""
    explicit = [r for r in fact.redefinitions if r.origin is Origin.EXPLICIT]
    implied = [r for r in fact.redefinitions if r.origin is Origin.IMPLIED]
    if fact.role is not ParameterRole.ORDINARY:
        return InputOutcome.SPECIAL_PARAMETER, []
    name = fact.declared_name
    if name is None:
        return (InputOutcome.EXPLICIT if explicit else InputOutcome.ANONYMOUS), []
    if not implied:
        return (InputOutcome.EXPLICIT if explicit else InputOutcome.NEW_PARAMETER), []
    findings = [
        PositionalFinding(
            identity=_identity(fact.owner, name, target),
            owner=fact.owner,
            input_name=name,
            target=target,
            location=fact.location,
            reason=FindingReason.SWAP
            if target.role is ParameterRole.ORDINARY
            else FindingReason.SPECIAL_SLOT,
        )
        for target in implied
        if target.name is not None
        and target.name != name
        and not _accounts_for(target, explicit, implied)
    ]
    if findings:
        return InputOutcome.IMPLICIT_MISMATCH, findings
    if explicit:
        return InputOutcome.EXPLICIT, []
    if all(target.name is None for target in implied):
        return InputOutcome.ANONYMOUS_TARGET, []
    return InputOutcome.IMPLICIT_MATCHING, []


def decide(facts: ParameterRedefinitionFacts) -> PositionalResult:
    """Every positional finding in the facts, with the extraction's failures carried as-is."""
    counts: Counter[InputOutcome] = Counter()
    findings: list[PositionalFinding] = []
    for fact in facts.facts:
        outcome, found = _judge(fact)
        counts[outcome] += 1
        findings.extend(found)
    return PositionalResult(
        findings=tuple(sorted(findings, key=PositionalFinding.sort_key)),
        failures=facts.failures,
        outcomes={outcome: counts[outcome] for outcome in InputOutcome},
    )

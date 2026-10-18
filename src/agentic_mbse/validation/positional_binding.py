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

Pins change only a finding's ``pinned`` mark, and only on an exact identity match (I2). A pin
no finding matches is judged by its file (D13): stale if the file was validated, stale if the
file does not exist, out of scope if it exists but was not validated. A pin whose owner or
input could not be inspected is not judged at all: the inspection failure is already the
blocking result, and calling the pin stale would claim something nobody checked.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import PurePosixPath

from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.parameter_redefinition_facts import (
    InputRedefinitionFact,
    Origin,
    ParameterRedefinitionFacts,
    ParameterRole,
    RedefinedFormal,
    RedefinitionFailure,
)
from agentic_mbse.validation.positional_pins import FindingIdentity, Pin, PinList

__all__ = [
    "FindingReason",
    "InputOutcome",
    "PinScope",
    "PositionalFinding",
    "PositionalResult",
    "StalePin",
    "StaleReason",
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
    pinned: bool

    def sort_key(self) -> tuple[tuple[str, int, str], str, str, str]:
        """Location, then owner, input and target names; never an element id (see the fact's key)."""
        return (
            self.location.sort_key(),
            self.owner.qualified_name or "",
            self.input_name,
            self.target.formal.qualified_name or "",
        )


class StaleReason(StrEnum):
    """Why an unmatched pin is stale; rendered as the issue's `reason_code` (D13)."""

    NOT_FOUND_IN_VALIDATED_FILE = "not_found_in_validated_file"
    PINNED_FILE_MISSING = "pinned_file_missing"


@dataclass(frozen=True)
class StalePin:
    pin: Pin
    reason: StaleReason


@dataclass(frozen=True)
class PinScope:
    """A valid pin list and what the caller found on disk, as data (D13).

    Paths are POSIX paths relative to the pin list's pin root. ``validated_files`` are the
    files this run loaded; ``existing_files`` are the files that exist under the pin root,
    at least every pinned file that does.
    """

    pin_list: PinList
    validated_files: frozenset[PurePosixPath]
    existing_files: frozenset[PurePosixPath]


@dataclass(frozen=True)
class PositionalResult:
    """Findings, failures and unmatched pins in sorted order, and the count of each outcome.

    ``outcomes`` lists every :class:`InputOutcome` in declaration order, zeros included.
    ``stale``, ``out_of_scope`` and ``not_judged`` partition the pins no finding matched;
    all three are empty without a pin list.
    """

    findings: tuple[PositionalFinding, ...]
    failures: tuple[RedefinitionFailure, ...]
    outcomes: Mapping[InputOutcome, int]
    stale: tuple[StalePin, ...]
    out_of_scope: tuple[Pin, ...]
    not_judged: tuple[Pin, ...]

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
            pinned=False,
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


def decide(facts: ParameterRedefinitionFacts, pins: PinScope | None) -> PositionalResult:
    """Every positional finding in the facts, marked pinned where ``pins`` names its identity.

    ``pins`` is None when there is no usable pin list. The extraction's failures are carried
    as-is; a pin never applies to one (I2).
    """
    counts: Counter[InputOutcome] = Counter()
    findings: list[PositionalFinding] = []
    for fact in facts.facts:
        outcome, found = _judge(fact)
        counts[outcome] += 1
        findings.extend(found)
    pinned_identities = (
        frozenset() if pins is None else frozenset(p.identity for p in pins.pin_list.pins)
    )
    findings = [replace(f, pinned=True) if f.identity in pinned_identities else f for f in findings]
    stale: list[StalePin] = []
    out_of_scope: list[Pin] = []
    not_judged: list[Pin] = []
    if pins is not None:
        matched = {f.identity for f in findings}
        uninspected = _uninspected_names(facts)
        for pin in pins.pin_list.pins:
            if pin.identity in matched:
                continue
            if uninspected is None or _names(pin) & uninspected:
                not_judged.append(pin)
            elif pin.file in pins.validated_files:
                stale.append(StalePin(pin, StaleReason.NOT_FOUND_IN_VALIDATED_FILE))
            elif pin.file not in pins.existing_files:
                stale.append(StalePin(pin, StaleReason.PINNED_FILE_MISSING))
            else:
                out_of_scope.append(pin)
    return PositionalResult(
        findings=tuple(sorted(findings, key=PositionalFinding.sort_key)),
        failures=facts.failures,
        outcomes={outcome: counts[outcome] for outcome in InputOutcome},
        stale=tuple(sorted(stale, key=lambda s: s.pin.identity)),
        out_of_scope=tuple(sorted(out_of_scope, key=lambda p: p.identity)),
        not_judged=tuple(sorted(not_judged, key=lambda p: p.identity)),
    )


def _uninspected_names(facts: ParameterRedefinitionFacts) -> frozenset[str] | None:
    """Qualified names of the owners and inputs that failed; None if no owner was listed."""
    if not facts.owners_enumerated:
        return None
    return frozenset(
        f.subject.qualified_name
        for f in facts.failures
        if f.subject is not None and f.subject.qualified_name is not None
    )


def _names(pin: Pin) -> frozenset[str]:
    """The owner and input qualified names a pin refers to."""
    return frozenset({pin.identity.owner, f"{pin.identity.owner}::{pin.identity.input}"})

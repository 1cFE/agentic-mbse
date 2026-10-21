"""Extract, from SysIDE, how each authored calc or constraint input redefines its formals.

`extract_parameter_redefinitions(model)` reads the facts in
:mod:`~agentic_mbse.sysml.parameter_redefinition_facts` and decides nothing. L2-internal
(design D1): not a surface for sysml-codegen.

The reads, each observed on SysIDE 0.8.4 and pinned by
`tests/learning/test_syside_input_redefinition.py`:

| Reading | SysIDE surface | Learning finding |
|---|---|---|
| Owners | ``CalculationUsage``, ``ConstraintUsage``, ``CalculationDefinition``, ``ConstraintDefinition``, each with ``include_subtypes=True``, de-duplicated by element id (D5) | R6 |
| Library owners skipped | ``SysideAdapter.document_tier`` is ``StandardLibrary`` (a guard: the sweeps return none) | R6 |
| Unresolved references | an explicit ``FeatureTyping``, ``Subclassification``, ``Redefinition`` or ``Subsetting`` whose target has ``owning_relationship is None`` is a SysIDE placeholder (D19) | M1, A1 |
| Inputs | ``owned_features`` whose direction is ``in`` or ``inout`` (D4) | R2, R5 |
| Name | ``declared_name``, never ``name`` (which falls back to the redefined formal's) | R5 |
| Role | the type of ``owning_membership``: ``SubjectMembership``, ``ActorMembership``, ``StakeholderMembership``, else ordinary | R2, plan phase 1 |
| Redefinitions | ``heritage.relationships`` filtered to ``Redefinition``, split by ``is_implied`` (D3) | R1, R3, S4 |

Totality (design I4): every inspected owner and input yields exactly one fact or one
:class:`RedefinitionFailure`. An owner-level failure (tier, identity, placeholder type,
unlistable inputs) replaces all of that owner's inputs; an input-level failure replaces only
that input, and the owner's other inputs are still read. A failing owner never stops the
others. The exceptions turned into failures are the adapter's named error and the ones an
attribute read on a partial SysIDE node raises (`_READ_ERRORS`); anything else propagates.

The keyword-only seams ``list_owners``, ``read_owned_features`` and ``read_heritage`` let tests
inject failures, as the prototype's ``heritage_of`` did (`04-detector.py:93-95`).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Any, TypeVar
from uuid import UUID

from agentic_mbse.errors import SemanticEvidenceError
from agentic_mbse.sysml.element_refs import ElementIdentityError, element_ref, safe_location
from agentic_mbse.sysml.fact_refs import ElementRef
from agentic_mbse.sysml.parameter_redefinition_facts import (
    Direction,
    InputRedefinitionFact,
    Origin,
    ParameterRedefinitionFacts,
    ParameterRole,
    RedefinedFormal,
    RedefinitionFailure,
    RedefinitionFailureCause,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = [
    "extract_parameter_redefinitions",
    "heritage_relationships",
    "owned_features",
    "sweep_owners",
]

Cause = RedefinitionFailureCause

#: The owner sweeps (design D5), recorded in the adapter's enumeration table.
OWNER_SWEEPS = (
    "CalculationUsage",
    "ConstraintUsage",
    "CalculationDefinition",
    "ConstraintDefinition",
)

#: Owning-membership type → role. Anything else (plain `FeatureMembership`) is ordinary.
_ROLE_MEMBERSHIPS = (
    ("SubjectMembership", ParameterRole.SUBJECT),
    ("ActorMembership", ParameterRole.ACTOR),
    ("StakeholderMembership", ParameterRole.STAKEHOLDER),
)

#: What a read on a live SysIDE node, or a seam standing in for one, raises when the node is
#: partial: the adapter's named error and the lookup errors `safe_location` also catches.
_READ_ERRORS = (SemanticEvidenceError, AttributeError, TypeError, ValueError, RuntimeError)

_T = TypeVar("_T")


# ---- the default SysIDE reads (also the seams' defaults) -------------------------------------


def sweep_owners(model: Any) -> Iterator[Any]:
    """Every calc and constraint owner in the model's own documents, each once."""
    seen: set[UUID] = set()
    for sweep in OWNER_SWEEPS:
        for owner in SysideAdapter.elements_of_type(model, sweep, include_subtypes=True):
            element_id = SysideAdapter.element_id(owner)
            if element_id not in seen:
                seen.add(element_id)
                yield owner


def owned_features(owner: Any) -> Iterable[Any]:
    return owner.owned_features.collect()  # type: ignore[no-any-return]


def heritage_relationships(element: Any) -> Iterable[Any]:
    return element.heritage.relationships  # type: ignore[no-any-return]


# ---- failure plumbing ------------------------------------------------------------------------


class _UnreadableError(Exception):
    """One owner or input yields no fact; carried to the loop that records the failure."""

    def __init__(self, cause: RedefinitionFailureCause, detail: str) -> None:
        super().__init__(detail)
        self.cause = cause
        self.detail = detail


def _describe(error: Exception) -> str:
    if isinstance(error, SemanticEvidenceError):
        return f"{error.code.value}: {error.detail}"
    return f"{type(error).__name__}: {error}"


def _read(cause: RedefinitionFailureCause, what: str, read: Callable[[], _T]) -> _T:
    """Run one SysIDE read; a read error becomes `_UnreadableError(cause)` naming what was read."""
    try:
        return read()
    except _READ_ERRORS as error:
        raise _UnreadableError(cause, f"{what}: {_describe(error)}") from error


def _identity(element: Any, what: str) -> ElementRef:
    try:
        return element_ref(element)
    except ElementIdentityError as error:
        raise _UnreadableError(Cause.IDENTITY_UNAVAILABLE, f"{what}: {error}") from error


def _label(element: Any) -> str:
    return safe_location(element).qualified_name or f"<anonymous {type(element).__name__}>"


# ---- single readings (mechanism; the caller names the failure cause) -------------------------


def _direction(feature: Any) -> Direction | None:
    """`in` or `inout`; else not an input."""
    direction = getattr(feature, "direction", None)
    if direction is None:
        return None
    spelled = str(direction).rsplit(".", 1)[-1].lower()
    return Direction(spelled) if spelled in {"in", "inout"} else None


def _role(feature: Any) -> ParameterRole:
    membership = feature.owning_membership
    if membership is None:
        raise ValueError(f"{type(feature).__name__} has no owning membership")
    for type_name, role in _ROLE_MEMBERSHIPS:
        if SysideAdapter.is_instance(membership, type_name):
            return role
    return ParameterRole.ORDINARY


def _explicit_targets(relationships: Iterable[Any]) -> Iterator[tuple[str, Any]]:
    """(relationship kind, target) for each explicit typing, supertype, redefinition and subset.

    `Redefinition` is tested before `Subsetting`, its supertype; `ReferenceSubsetting` (`::>`)
    is a `Subsetting` and reads as one.
    """
    for relationship in relationships:
        if relationship.is_implied:
            continue
        if SysideAdapter.is_instance(relationship, "Redefinition"):
            yield "Redefinition", relationship.redefined_feature
        elif SysideAdapter.is_instance(relationship, "Subsetting"):
            yield "Subsetting", relationship.subsetted_feature
        elif SysideAdapter.is_instance(relationship, "FeatureTyping"):
            yield "FeatureTyping", relationship.type
        elif SysideAdapter.is_instance(relationship, "Subclassification"):
            yield "Subclassification", relationship.general


def _is_placeholder(target: Any) -> bool:
    """SysIDE's stand-in for an unresolved reference has no owning relationship (M1, B6)."""
    return target.owning_relationship is None


# ---- owners ----------------------------------------------------------------------------------


def _is_library(owner: Any) -> bool:
    try:
        tier = SysideAdapter.document_tier(owner)
    except SemanticEvidenceError as error:
        raise _UnreadableError(Cause.DOCUMENT_TIER_UNREADABLE, _describe(error)) from error
    return bool(tier is SysideAdapter.document_tier_type().StandardLibrary)


def _require_resolved_owner(owner: Any, read_heritage: Callable[[Any], Iterable[Any]]) -> None:
    """D19: an owner whose explicit type, supertype, `:>>` or `:>` target is a placeholder fails."""
    relationships = _read(
        Cause.REDEFINITIONS_UNREADABLE,
        "the owner's typing and redefinitions",
        lambda: list(read_heritage(owner)),
    )
    targets = _read(
        Cause.REDEFINITIONS_UNREADABLE,
        "the owner's explicit typing and redefinitions",
        lambda: list(_explicit_targets(relationships)),
    )
    for kind, target in targets:
        if target is None:
            raise _UnreadableError(
                Cause.TARGET_UNREADABLE, f"the owner's explicit {kind} has no target"
            )
        placeholder = _read(
            Cause.TARGET_UNREADABLE, f"the owner's {kind} target", lambda: _is_placeholder(target)
        )
        if placeholder:
            raise _UnreadableError(
                Cause.UNRESOLVED_OWNER_TYPE,
                f"the owner's explicit {kind} targets an unresolved reference ({_label(target)})",
            )


def _owner_inputs(
    owner: Any,
    read_owned_features: Callable[[Any], Iterable[Any]],
    read_heritage: Callable[[Any], Iterable[Any]],
) -> list[InputRedefinitionFact | RedefinitionFailure]:
    """One fact or failure per input of a resolved owner; raises `_UnreadableError` for the owner."""
    _require_resolved_owner(owner, read_heritage)
    owner_ref = _identity(owner, "owner")
    features = _read(
        Cause.INPUTS_UNLISTED,
        "the owner's owned features",
        lambda: list(read_owned_features(owner)),
    )
    inputs = [
        (feature, direction)
        for feature in features
        if (
            direction := _read(
                Cause.INPUTS_UNLISTED, "a feature's direction", lambda: _direction(feature)
            )
        )
        is not None
    ]
    readings: list[InputRedefinitionFact | RedefinitionFailure] = []
    for feature, direction in inputs:
        try:
            readings.append(_input_fact(owner_ref, feature, direction, read_heritage))
        except _UnreadableError as failure:
            readings.append(
                RedefinitionFailure(
                    safe_location(feature),
                    failure.cause,
                    f"input of {_label(owner)}: {failure.detail}",
                )
            )
    return readings


# ---- inputs ----------------------------------------------------------------------------------


def _input_fact(
    owner: ElementRef,
    feature: Any,
    direction: Direction,
    read_heritage: Callable[[Any], Iterable[Any]],
) -> InputRedefinitionFact:
    input_ref = _identity(feature, "input")
    declared_name = _read(
        Cause.IDENTITY_UNAVAILABLE, "declared name", lambda: feature.declared_name
    )
    role = _read(Cause.ROLE_UNREADABLE, "owning membership", lambda: _role(feature))
    relationships = _read(
        Cause.REDEFINITIONS_UNREADABLE, "relationships", lambda: list(read_heritage(feature))
    )
    redefinitions = [
        relationship
        for relationship in relationships
        if _read(
            Cause.REDEFINITIONS_UNREADABLE,
            "relationship kind",
            lambda: SysideAdapter.is_instance(relationship, "Redefinition"),
        )
    ]
    return InputRedefinitionFact(
        owner=owner,
        input=input_ref,
        declared_name=None if declared_name is None else str(declared_name),
        direction=direction,
        role=role,
        location=safe_location(feature),
        redefinitions=tuple(_redefined_formal(r) for r in redefinitions),
    )


def _redefined_formal(redefinition: Any) -> RedefinedFormal:
    target = _read(
        Cause.TARGET_UNREADABLE, "redefinition target", lambda: redefinition.redefined_feature
    )
    if target is None:
        raise _UnreadableError(Cause.TARGET_UNREADABLE, "a redefinition has no target")
    if _read(Cause.TARGET_UNREADABLE, "redefinition target", lambda: _is_placeholder(target)):
        raise _UnreadableError(
            Cause.UNRESOLVED_INPUT_REDEFINITION,
            f"a redefinition targets an unresolved reference ({_label(target)})",
        )
    implied = _read(
        Cause.REDEFINITIONS_UNREADABLE, "is_implied", lambda: bool(redefinition.is_implied)
    )
    name = _read(Cause.TARGET_UNREADABLE, "target name", lambda: target.name)
    owning_type = _read(Cause.TARGET_UNREADABLE, "target owning type", lambda: target.owning_type)
    if owning_type is None:
        raise _UnreadableError(
            Cause.TARGET_UNREADABLE, f"target {_label(target)} has no owning type"
        )
    return RedefinedFormal(
        formal=_identity(target, "target"),
        name=None if name is None else str(name),
        owning_type=_identity(owning_type, "target owning type"),
        role=_read(Cause.TARGET_UNREADABLE, "target owning membership", lambda: _role(target)),
        origin=Origin.IMPLIED if implied else Origin.EXPLICIT,
    )


# ---- the entry point -------------------------------------------------------------------------


def extract_parameter_redefinitions(
    model: Any,
    *,
    list_owners: Callable[[Any], Iterable[Any]] = sweep_owners,
    read_owned_features: Callable[[Any], Iterable[Any]] = owned_features,
    read_heritage: Callable[[Any], Iterable[Any]] = heritage_relationships,
) -> ParameterRedefinitionFacts:
    """Every authored calc and constraint input's redefinitions, or why each could not be read."""
    try:
        owners = list(list_owners(model))
    except _READ_ERRORS as error:
        return ParameterRedefinitionFacts(
            owners_enumerated=False,
            owners_inspected=0,
            facts=(),
            failures=(RedefinitionFailure(None, Cause.OWNERS_UNLISTED, _describe(error)),),
        )
    facts: list[InputRedefinitionFact] = []
    failures: list[RedefinitionFailure] = []
    inspected = 0
    for owner in owners:
        try:
            if _is_library(owner):
                continue
        except _UnreadableError as failure:
            inspected += 1
            failures.append(
                RedefinitionFailure(safe_location(owner), failure.cause, failure.detail)
            )
            continue
        inspected += 1
        try:
            readings = _owner_inputs(owner, read_owned_features, read_heritage)
        except _UnreadableError as failure:
            failures.append(
                RedefinitionFailure(safe_location(owner), failure.cause, failure.detail)
            )
            continue
        for reading in readings:
            if isinstance(reading, RedefinitionFailure):
                failures.append(reading)
            else:
                facts.append(reading)
    return ParameterRedefinitionFacts(
        owners_enumerated=True,
        owners_inspected=inspected,
        facts=tuple(sorted(facts, key=InputRedefinitionFact.sort_key)),
        failures=tuple(sorted(failures, key=RedefinitionFailure.sort_key)),
    )

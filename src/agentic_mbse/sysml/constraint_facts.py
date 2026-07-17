"""Neutral constraint fact schemas and canonical serialization.

Promotes S1's frozen, test-only constraint fact shapes
(`.project/completed/20260711_spike-constraint-fact-shapes/findings.md`) into the production schema
downstream repos read as ground truth. The leaf vocabulary is defined in `expression_facts`
so Item 2's `ExpressionIR` can adopt it without a cycle; the shared codec surface
(`canonical_json`, `expression_ir_from_dict`, `identity_fact_from_dict`) comes from
`expression_ir` — this module imports only public names from it, and the import direction
stays one-way (`constraint_facts` → `expression_ir`).

The codec fails closed on the envelope tag: `parse` rejects any unsupported
`schema_version`, and `serialize` revalidates it so post-construction mutation cannot emit an
impossible document.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from agentic_mbse.sysml.expression_facts import IdentityFact
from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    canonical_json,
    expression_ir_from_dict,
    identity_fact_from_dict,
)

__all__ = [
    "CONSTRAINT_FACTS_SCHEMA_VERSION",
    "ActualFact",
    "ConstraintDefinitionFact",
    "ConstraintFacts",
    "ConstraintSource",
    "ConstraintUsageFact",
    "ContextFact",
    "ExtractionDiagnosticFact",
    "FormalFact",
    "IdentityFact",
    "LocationFact",
    "OwnerFact",
    "OwningDefinitionFact",
    "RedefinitionFact",
    "parse",
    "serialize",
]

CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v1"


@dataclass
class LocationFact:
    """Source location: an anonymous assertion's only identity (`[HARD]`)."""

    file: str
    line: int
    column: int


@dataclass
class OwningDefinitionFact:
    """The resolved, tagged owning definition (D6/MF3) — total over all six source forms.

    ``kind`` is one of ``part_def``/``calc_def``/``requirement_def``/``package``, resolved by
    walking ``owner`` up to the first enclosing ``PartDefinition``/``CalculationDefinition``/
    ``RequirementDefinition``/``Package``. A ``Package`` always terminates the chain, so this
    fact is never absent.
    """

    kind: str
    qualified_name: str


@dataclass
class OwnerFact:
    """The constraint's immediate owner and its resolved owning definition."""

    owner: IdentityFact | None
    owning_definition: OwningDefinitionFact


@dataclass
class ConstraintSource:
    """The single discriminant naming a usage's form (D5).

    ``constraint_definition`` and ``asserted_constraint`` are raw, unconditional reads of the
    usage's own attributes — populated whenever the underlying SysML element resolves to
    something, independent of ``form`` (e.g. a ``satisfy`` usage's ``constraint_definition``
    resolves to the ``RequirementDefinition`` it satisfies). Only ``effective_predicate_source``
    is form-derived: ``inline`` and ``requirement_constraint`` point at the usage itself,
    ``definition_typed`` at its ``constraint_definition``, ``named_usage_reference`` at the
    referenced usage's ``constraint_definition``, and ``satisfy``/``plain_usage`` at ``None``.
    """

    form: str
    effective_predicate_source: IdentityFact | None
    constraint_definition: IdentityFact | None
    referenced_feature_target: IdentityFact | None
    asserted_constraint: IdentityFact | None


@dataclass
class FormalFact:
    """One constraint-definition formal parameter."""

    name: str | None
    qualified_name: str | None
    types: list[str] = field(default_factory=list)
    has_default: bool = False
    default: ExpressionIR | None = None


@dataclass
class ActualFact:
    """One actual bound to a formal on a definition-typed or named usage."""

    name: str | None
    direction: str | None
    formal_targets: list[str] = field(default_factory=list)
    value: ExpressionIR | None = None


@dataclass
class ConstraintDefinitionFact:
    """A reusable ``constraint def``: identity, formals, and predicate."""

    identity: IdentityFact
    formals: list[FormalFact]
    predicate: ExpressionIR | None


@dataclass
class ConstraintUsageFact:
    """One extracted ``ConstraintUsage``, tagged with exactly one `ConstraintSource` form."""

    identity: IdentityFact
    location: LocationFact | None
    source: ConstraintSource
    owner: OwnerFact
    scope: IdentityFact
    membership_kind: str | None
    is_negated: bool | None
    actuals: list[ActualFact]
    omitted_default_formals: list[str]
    predicate: ExpressionIR | None
    inherited_into: list[str]


@dataclass
class RedefinitionFact:
    """One ``:>>`` redefinition observed at a context."""

    feature: str | None
    redefines: str | None
    value: ExpressionIR | None


@dataclass
class ContextFact:
    """Inheritance/retyping facts at one owning context (definition or retyped usage)."""

    identity: IdentityFact
    general_types: list[str]
    types: list[str]
    inherited_constraints: list[str]
    redefinitions: list[RedefinitionFact]


@dataclass
class ExtractionDiagnosticFact:
    """A structured diagnostic raised during extraction (D2a): a non-finite literal operand."""

    kind: str
    message: str
    operand_source: str | None
    location: LocationFact | None


@dataclass
class ConstraintFacts:
    """The full extracted fact aggregate for one model."""

    schema_version: str = field(init=False, default=CONSTRAINT_FACTS_SCHEMA_VERSION)
    definitions: list[ConstraintDefinitionFact]
    usages: list[ConstraintUsageFact]
    contexts: list[ContextFact]
    diagnostics: list[ExtractionDiagnosticFact]


def serialize(facts: ConstraintFacts) -> str:
    """Render ``facts`` as the canonical, byte-stable JSON section (D2).

    Every field is present; absence is an explicit ``null`` (D3). Raises ``ValueError`` if a
    non-finite float slipped past extraction (D2a's serialize-time backstop).
    """
    if facts.schema_version != CONSTRAINT_FACTS_SCHEMA_VERSION:
        raise ValueError(
            f"invalid ConstraintFacts schema_version: found {facts.schema_version!r}, "
            f"expected {CONSTRAINT_FACTS_SCHEMA_VERSION!r}"
        )
    return canonical_json(facts)


def _identity_from_dict_required(data: dict[str, Any]) -> IdentityFact:
    identity = identity_fact_from_dict(data)
    if identity is None:
        raise ValueError("expected an identity fact, got null")
    return identity


def _location_from_dict(data: dict[str, Any] | None) -> LocationFact | None:
    if data is None:
        return None
    return LocationFact(file=data["file"], line=data["line"], column=data["column"])


def _expression_ir_from_dict(data: dict[str, Any] | None) -> ExpressionIR | None:
    if data is None:
        return None
    return expression_ir_from_dict(data)


def _formal_from_dict(data: dict[str, Any]) -> FormalFact:
    return FormalFact(
        name=data["name"],
        qualified_name=data["qualified_name"],
        types=list(data["types"]),
        has_default=data["has_default"],
        default=_expression_ir_from_dict(data["default"]),
    )


def _actual_from_dict(data: dict[str, Any]) -> ActualFact:
    return ActualFact(
        name=data["name"],
        direction=data["direction"],
        formal_targets=list(data["formal_targets"]),
        value=_expression_ir_from_dict(data["value"]),
    )


def _owning_definition_from_dict(data: dict[str, Any]) -> OwningDefinitionFact:
    return OwningDefinitionFact(kind=data["kind"], qualified_name=data["qualified_name"])


def _owner_from_dict(data: dict[str, Any]) -> OwnerFact:
    return OwnerFact(
        owner=identity_fact_from_dict(data["owner"]),
        owning_definition=_owning_definition_from_dict(data["owning_definition"]),
    )


def _source_from_dict(data: dict[str, Any]) -> ConstraintSource:
    return ConstraintSource(
        form=data["form"],
        effective_predicate_source=identity_fact_from_dict(data["effective_predicate_source"]),
        constraint_definition=identity_fact_from_dict(data["constraint_definition"]),
        referenced_feature_target=identity_fact_from_dict(data["referenced_feature_target"]),
        asserted_constraint=identity_fact_from_dict(data["asserted_constraint"]),
    )


def _definition_from_dict(data: dict[str, Any]) -> ConstraintDefinitionFact:
    return ConstraintDefinitionFact(
        identity=_identity_from_dict_required(data["identity"]),
        formals=[_formal_from_dict(item) for item in data["formals"]],
        predicate=_expression_ir_from_dict(data["predicate"]),
    )


def _usage_from_dict(data: dict[str, Any]) -> ConstraintUsageFact:
    return ConstraintUsageFact(
        identity=_identity_from_dict_required(data["identity"]),
        location=_location_from_dict(data["location"]),
        source=_source_from_dict(data["source"]),
        owner=_owner_from_dict(data["owner"]),
        scope=_identity_from_dict_required(data["scope"]),
        membership_kind=data["membership_kind"],
        is_negated=data["is_negated"],
        actuals=[_actual_from_dict(item) for item in data["actuals"]],
        omitted_default_formals=list(data["omitted_default_formals"]),
        predicate=_expression_ir_from_dict(data["predicate"]),
        inherited_into=list(data["inherited_into"]),
    )


def _redefinition_from_dict(data: dict[str, Any]) -> RedefinitionFact:
    return RedefinitionFact(
        feature=data["feature"],
        redefines=data["redefines"],
        value=_expression_ir_from_dict(data["value"]),
    )


def _context_from_dict(data: dict[str, Any]) -> ContextFact:
    return ContextFact(
        identity=_identity_from_dict_required(data["identity"]),
        general_types=list(data["general_types"]),
        types=list(data["types"]),
        inherited_constraints=list(data["inherited_constraints"]),
        redefinitions=[_redefinition_from_dict(item) for item in data["redefinitions"]],
    )


def _diagnostic_from_dict(data: dict[str, Any]) -> ExtractionDiagnosticFact:
    return ExtractionDiagnosticFact(
        kind=data["kind"],
        message=data["message"],
        operand_source=data["operand_source"],
        location=_location_from_dict(data["location"]),
    )


def parse(text: str) -> ConstraintFacts:
    """Reconstruct a `ConstraintFacts` aggregate from its canonical JSON section.

    Rejects a missing or unsupported envelope `schema_version` with `ValueError` naming
    found vs supported — a foreign-version document never parses. Goes through the typed
    layer (not a bare `json.loads`), so `serialize(parse(serialize(f))) == serialize(f)`
    exercises the full round-trip, not just JSON re-encoding.
    """
    data = json.loads(text)
    if "schema_version" not in data:
        raise ValueError(
            "ConstraintFacts document is missing 'schema_version' "
            f"(supported: {CONSTRAINT_FACTS_SCHEMA_VERSION!r})"
        )
    found_version = data["schema_version"]
    if found_version != CONSTRAINT_FACTS_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported ConstraintFacts schema_version: found {found_version!r}, "
            f"supported {CONSTRAINT_FACTS_SCHEMA_VERSION!r}"
        )
    return ConstraintFacts(
        definitions=[_definition_from_dict(item) for item in data["definitions"]],
        usages=[_usage_from_dict(item) for item in data["usages"]],
        contexts=[_context_from_dict(item) for item in data["contexts"]],
        diagnostics=[_diagnostic_from_dict(item) for item in data["diagnostics"]],
    )

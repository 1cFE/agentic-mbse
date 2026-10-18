"""Synthetic subset facts for the pure evaluator tests: no SysIDE, no model.

Every builder returns a real fact type, so the facts are validated by the same constructors
extraction uses. Names become reload-stable UUIDv5 identities, as SysIDE gives a named
declaration.
"""

from __future__ import annotations

from collections.abc import Iterable
from uuid import NAMESPACE_URL, UUID, uuid5

from agentic_mbse.sysml.constraint_extraction import IdentifiedConstraintFacts
from agentic_mbse.sysml.constraint_facts import ConstraintFacts
from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.invocation_allowlist import STANDARD_SUM_FUNCTION_ID, InvocationUse
from agentic_mbse.sysml.occurrence_facts import (
    Attachment,
    AttachmentCause,
    MultiplicityReading,
    OccurrenceScope,
    OccurrenceStructure,
    PackageScope,
    PartUsageReading,
    PathStep,
    Scope,
    UsageVisit,
    WriterSelection,
)
from agentic_mbse.sysml.subset_facts import (
    AssertionOwnerFact,
    BindingKind,
    BindingSourceFact,
    ExpressionSiteFact,
    FactFailure,
    FactKind,
    InvocationOutcome,
    InvocationsWalked,
    OwnerKind,
    PartMultiplicityFact,
    ReferenceOutcome,
    ReferencesWalked,
    SiteInspection,
    SiteRole,
    StringSpelling,
    StringValueFact,
    SubsetFacts,
)

FILE = "model.sysml"


def uid(qualified_name: str) -> UUID:
    return uuid5(NAMESPACE_URL, qualified_name)


def ref(qualified_name: str, kind: str = "Feature") -> ElementRef:
    return ElementRef(uid(qualified_name), qualified_name, kind)


def loc(line: int, qualified_name: str | None = None) -> SafeLocation:
    return SafeLocation(FILE, line, qualified_name)


# ---- facts --------------------------------------------------------------------------------


def binding(consumer: str, formal: str, kind: BindingKind, line: int) -> BindingSourceFact:
    return BindingSourceFact(
        consumer=ref(consumer, "CalculationUsage"),
        formal=ref(formal, "ReferenceUsage"),
        location=loc(line, formal),
        authored="(a, b)",
        kind=kind,
    )


def call(name: str, supported: bool = False) -> InvocationUse:
    return InvocationUse(
        STANDARD_SUM_FUNCTION_ID if supported else uid(name), name, f"{name}(x)", (FILE, 1)
    )


def site(
    feature: str,
    role: SiteRole,
    line: int,
    *,
    references: ReferenceOutcome = ReferencesWalked(1, 0),
    invocations: InvocationOutcome = InvocationsWalked(()),
    conditionals: Iterable[int] = (),
) -> ExpressionSiteFact:
    return ExpressionSiteFact(
        feature=ref(feature, "AttributeUsage"),
        role=role,
        location=loc(line, feature),
        inspection=SiteInspection(references, invocations, tuple(loc(n) for n in conditionals)),
    )


def assertion(
    constraint: str, owner: str, owner_kind: OwnerKind, *, asserted: bool, line: int
) -> AssertionOwnerFact:
    return AssertionOwnerFact(
        constraint=ref(constraint, "AssertConstraintUsage"),
        location=loc(line, constraint),
        form="inline" if asserted else "plain_usage",
        asserted=asserted,
        owner=ref(owner, "Element"),
        owner_kind=owner_kind,
    )


def ranged(lower: int, upper: int) -> MultiplicityReading:
    return MultiplicityReading(True, False, False, upper, lower, True)


def exact(count: int) -> MultiplicityReading:
    return MultiplicityReading(True, False, False, count, None, False)


def visit(
    usage: str, root: str, reading: MultiplicityReading, parent: str | None = None
) -> UsageVisit:
    return UsageVisit(
        usage_id=uid(usage),
        parent=None if parent is None else (PathStep(uid(parent), None),),
        root_id=uid(root),
        reading=reading,
    )


def multiplicity(
    usage: str, reading: MultiplicityReading, visits: Iterable[UsageVisit], line: int
) -> PartMultiplicityFact:
    return PartMultiplicityFact(
        usage=ref(usage, "PartUsage"),
        location=loc(line, usage),
        shape=PartUsageReading(uid(usage), True, reading),
        visits=tuple(visits),
    )


def string(feature: str, line: int) -> StringValueFact:
    return StringValueFact(
        ref(feature, "AttributeUsage"), loc(line, feature), StringSpelling.ATTRIBUTE_DECLARATION
    )


# ---- occurrence structure -----------------------------------------------------------------


def occ(root: str, *path: str) -> OccurrenceScope:
    return OccurrenceScope(uid(root), tuple(PathStep(uid(p), None) for p in (root, *path)))


def pkg(name: str) -> PackageScope:
    return PackageScope(uid(name))


def attached(usage: str, owner: str, scopes: Iterable[Scope]) -> Attachment:
    ordered = tuple(sorted(scopes, key=_scope_key))
    if ordered:
        return Attachment(uid(usage), uid(owner), ordered, None)
    return Attachment(uid(usage), uid(owner), (), AttachmentCause.OWNER_HAS_NO_OCCURRENCES)


def unattachable(usage: str, owner: str) -> Attachment:
    return Attachment(uid(usage), uid(owner), (), AttachmentCause.OWNER_KIND_UNATTACHABLE)


def writer(slot: str, scope: Scope, selected: str, applicable: Iterable[str]) -> WriterSelection:
    return WriterSelection(
        slot=uid(slot),
        scope=scope,
        base_id=uid(slot),
        selected_id=uid(selected),
        applicable_ids=tuple(sorted((uid(a) for a in applicable), key=str)),
    )


def _scope_key(scope: Scope) -> tuple[int, str, tuple[tuple[str, int], ...]]:
    if isinstance(scope, PackageScope):
        return (0, str(scope.package_id), ())
    return (1, str(scope.root_id), tuple(step.sort_key() for step in scope.path))


def structure(
    *,
    roots: Iterable[str] = (),
    callers: Iterable[str] = (),
    visits: Iterable[UsageVisit] = (),
    calc: Iterable[Attachment] = (),
    constraint: Iterable[Attachment] = (),
    writers: Iterable[WriterSelection] = (),
) -> OccurrenceStructure:
    return OccurrenceStructure(
        generator_root_ids=tuple(sorted({uid(r) for r in roots}, key=str)),
        caller_root_ids=tuple(sorted({uid(r) for r in callers}, key=str)),
        visits=tuple(visits),
        nodes=(),
        part_definition_ids=(),
        part_usages=(),
        calc_attachments=tuple(sorted(calc, key=lambda a: str(a.usage_id))),
        constraint_attachments=tuple(sorted(constraint, key=lambda a: str(a.usage_id))),
        writers=tuple(sorted(writers, key=lambda w: (_scope_key(w.scope), str(w.slot)))),
    )


def no_constraints() -> IdentifiedConstraintFacts:
    return IdentifiedConstraintFacts(
        facts=ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[]),
        definitions=(),
        usages=(),
    )


def facts(
    *,
    occurrence: OccurrenceStructure | None = None,
    bindings: Iterable[BindingSourceFact] = (),
    sites: Iterable[ExpressionSiteFact] = (),
    assertions: Iterable[AssertionOwnerFact] = (),
    multiplicities: Iterable[PartMultiplicityFact] = (),
    strings: Iterable[StringValueFact] = (),
    failures: Iterable[FactFailure] = (),
    missing: Iterable[FactKind] = (),
) -> SubsetFacts:
    """Every kind enumerated except `missing`; an empty structure unless one is given."""
    missing = frozenset(missing)
    enumerated = frozenset(FactKind) - missing
    if FactKind.OCCURRENCE in enumerated and occurrence is None:
        occurrence = structure()
    return SubsetFacts(
        occurrence=occurrence if FactKind.OCCURRENCE in enumerated else None,
        bindings=tuple(sorted(bindings, key=lambda f: f.sort_key())),
        sites=tuple(sorted(sites, key=lambda f: f.sort_key())),
        assertions=tuple(sorted(assertions, key=lambda f: f.sort_key())),
        multiplicities=tuple(sorted(multiplicities, key=lambda f: f.sort_key())),
        strings=tuple(sorted(strings, key=lambda f: f.sort_key())),
        constraints=no_constraints() if FactKind.CONSTRAINT in enumerated else None,
        enumerated=enumerated,
        failures=tuple(sorted(failures, key=lambda f: f.sort_key())),
    )

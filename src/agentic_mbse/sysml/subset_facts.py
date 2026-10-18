"""Pure subset facts: what a model declares that the executable-subset rules read.

Built once by `subset_extraction.py` from SysIDE and read by the pure decision layer. Each kind
is total: every element of the kind yields a fact or a :class:`FactFailure`, and a kind whose
population could not be enumerated is missing from :attr:`SubsetFacts.enumerated`, so a rule
that needs it reports ``unverified`` instead of finding nothing.

Nothing here decides an outcome, and nothing here imports SysIDE, `reference_use` or the
generator. `IdentifiedConstraintFacts` is named for typing only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, TypeAlias

from agentic_mbse.errors import SemanticEvidenceCode
from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.invocation_allowlist import InvocationUse
from agentic_mbse.sysml.occurrence_facts import (
    OccurrenceAbort,
    OccurrenceStructure,
    PartUsageReading,
    UsageVisit,
)

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_extraction import IdentifiedConstraintFacts

__all__ = [
    "AssertionOwnerFact",
    "BindingKind",
    "BindingSourceFact",
    "ElementRef",
    "ExpressionSiteFact",
    "FactFailure",
    "FactKind",
    "InvocationsFailed",
    "InvocationsWalked",
    "OwnerKind",
    "PartMultiplicityFact",
    "ReferencesFailed",
    "ReferencesWalked",
    "SafeLocation",
    "ScopeCause",
    "SiteInspection",
    "SiteRole",
    "StringSpelling",
    "StringValueFact",
    "SubsetFacts",
]


class FactKind(StrEnum):
    OCCURRENCE = "occurrence"
    BINDING_SOURCE = "binding_source"
    EXPRESSION_SITE = "expression_site"
    ASSERTION_OWNER = "assertion_owner"
    PART_MULTIPLICITY = "part_multiplicity"
    STRING_VALUE = "string_value"
    CONSTRAINT = "constraint"


class ScopeCause(StrEnum):
    """Why a fact is missing when no closed evidence code or occurrence abort names it."""

    #: The kind's population could not be listed at all.
    ENUMERATION_FAILED = "enumeration_failed"
    #: The generator roots could not be computed.
    ROOTS_UNAVAILABLE = "roots_unavailable"
    #: SysIDE gave an element no usable identity (no UUID, or a named non-UUIDv5 one).
    ADAPTER_ERROR = "adapter_error"


FailureCause: TypeAlias = SemanticEvidenceCode | ScopeCause | OccurrenceAbort


@dataclass(frozen=True)
class FactFailure:
    """One element, or one whole kind (``subject`` None), whose fact could not be read."""

    fact_kind: FactKind
    subject: SafeLocation | None
    cause: FailureCause
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(self.fact_kind, FactKind):
            raise TypeError(f"fact_kind must be a FactKind, got {self.fact_kind!r}")
        if not isinstance(self.cause, (SemanticEvidenceCode, ScopeCause, OccurrenceAbort)):
            raise TypeError(f"cause must be a closed failure code, got {self.cause!r}")

    def sort_key(self) -> tuple[str, tuple[str, int, str], str, str]:
        subject = self.subject.sort_key() if self.subject else ("", -1, "")
        return (self.fact_kind.value, subject, str(self.cause.value), self.detail)


class OwnerKind(StrEnum):
    """The metatype of an element's semantic owner (owning type, else owner)."""

    PART_DEFINITION = "part_definition"
    PART_USAGE = "part_usage"
    CALCULATION_DEFINITION = "calculation_definition"
    CALCULATION_USAGE = "calculation_usage"
    PACKAGE = "package"
    REQUIREMENT_DEFINITION = "requirement_definition"
    #: Any other metatype: outside the generator's constraint owner map
    #: (`elaborate.py:800-827`), which maps the five kinds above other than a calc usage.
    OTHER = "other"
    ABSENT = "absent"


def _ref_key(ref: ElementRef, location: SafeLocation) -> tuple[tuple[str, int, str], str]:
    return (location.sort_key(), str(ref.element_id))


# ---- binding sources ----------------------------------------------------------------------


class BindingKind(StrEnum):
    """The generator's binding-source classes (`elaborate.py:2130-2196`)."""

    LITERAL = "literal"
    SELF_BINDING = "self_binding"
    INDEXED = "indexed"
    SINGLE_REFERENCE = "single_reference"
    OTHER_EXPRESSION = "other_expression"


@dataclass(frozen=True)
class BindingSourceFact:
    """One bound input of a calculation or constraint usage, classified like the generator."""

    consumer: ElementRef
    formal: ElementRef
    location: SafeLocation
    authored: str | None
    kind: BindingKind

    def sort_key(self) -> tuple[tuple[str, int, str], str]:
        return _ref_key(self.formal, self.location)


# ---- expression sites ---------------------------------------------------------------------


class SiteRole(StrEnum):
    """Where an expression sits.

    The first five are the generator's inventory roles (`expression_evidence.py:63-75`,
    decided as in `_role_for_owner`, `:328-347`). The last two are result expressions the
    inventory does not enumerate.
    """

    CALC_DEFINITION_DEPENDENCY = "calc_definition_dependency"
    BINDING = "binding"
    ALIAS = "alias"
    COMPUTED_ATTRIBUTE = "computed_attribute"
    CONSTRAINT_PREDICATE = "constraint_predicate"
    #: A calculation definition's bare result expression (no ``return`` feature).
    CALC_RESULT_EXPRESSION = "calc_result_expression"
    #: A calculation usage's bare result expression.
    OTHER_EXPRESSION_SITE = "other_expression_site"


@dataclass(frozen=True)
class ReferencesWalked:
    """The reference walk completed: how many uses it found, and how many are indexed."""

    use_count: int
    indexed_count: int

    def __post_init__(self) -> None:
        if not 0 <= self.indexed_count <= self.use_count:
            raise ValueError("indexed uses are a subset of all uses")


@dataclass(frozen=True)
class ReferencesFailed:
    """The reference walk raised this named code, as the generator's inventory would."""

    code: SemanticEvidenceCode
    detail: str


@dataclass(frozen=True)
class InvocationsWalked:
    uses: tuple[InvocationUse, ...]


@dataclass(frozen=True)
class InvocationsFailed:
    """The invocation walk could not finish; any invocation-dependent rule is unverified."""

    code: SemanticEvidenceCode
    detail: str


ReferenceOutcome: TypeAlias = ReferencesWalked | ReferencesFailed
InvocationOutcome: TypeAlias = InvocationsWalked | InvocationsFailed


@dataclass(frozen=True)
class SiteInspection:
    """Everything known about one site's expression, as one total value (design review S3).

    `conditionals` are the recognized ``if`` operator nodes, found by a structural walk that
    resolves nothing, so they are known even when the reference walk failed.
    """

    references: ReferenceOutcome
    invocations: InvocationOutcome
    conditionals: tuple[SafeLocation, ...]


@dataclass(frozen=True)
class ExpressionSiteFact:
    feature: ElementRef
    role: SiteRole
    location: SafeLocation
    inspection: SiteInspection

    def sort_key(self) -> tuple[tuple[str, int, str], str, str]:
        return (self.location.sort_key(), self.role.value, str(self.feature.element_id))


# ---- assertion owners, multiplicities, strings ----------------------------------------------


@dataclass(frozen=True)
class AssertionOwnerFact:
    """One constraint usage, its source form and its semantic owner.

    `form` is the constraint extractor's own classification (`constraint_extraction._classify`),
    carried over unchanged, and `asserted` is whether that form is in the extractor's own
    asserted set (`constraint_extraction._ASSERTED_FORMS`, the generator's
    `ASSERTED_SOURCE_FORMS`), so no decision re-lists the forms.
    """

    constraint: ElementRef
    location: SafeLocation
    form: str
    asserted: bool
    owner: ElementRef | None
    owner_kind: OwnerKind

    def __post_init__(self) -> None:
        if (self.owner is None) != (self.owner_kind is OwnerKind.ABSENT):
            raise ValueError("only an absent owner has no owner reference")

    def sort_key(self) -> tuple[tuple[str, int, str], str]:
        return _ref_key(self.constraint, self.location)


@dataclass(frozen=True)
class PartMultiplicityFact:
    """One user-model part usage's multiplicity, as the occurrence port read it.

    `shape` is the reading with no parent occurrence; `visits` are the generator's visits of
    the usage, one per parent occurrence, empty when no root reaches it.
    """

    usage: ElementRef
    location: SafeLocation
    shape: PartUsageReading
    visits: tuple[UsageVisit, ...]

    def __post_init__(self) -> None:
        if self.shape.usage_id != self.usage.element_id:
            raise ValueError("the reading belongs to this usage")
        if any(v.usage_id != self.usage.element_id for v in self.visits):
            raise ValueError("every visit is of this usage")

    def sort_key(self) -> tuple[tuple[str, int, str], str]:
        return _ref_key(self.usage, self.location)


class StringSpelling(StrEnum):
    #: ``attribute s : String = "..";`` (an `AttributeUsage`).
    ATTRIBUTE_DECLARATION = "attribute_declaration"
    #: ``:>> s = "..";`` (SysIDE parses the shorthand as a `ReferenceUsage`).
    REDEFINITION_SHORTHAND = "redefinition_shorthand"


@dataclass(frozen=True)
class StringValueFact:
    feature: ElementRef
    location: SafeLocation
    spelling: StringSpelling

    def sort_key(self) -> tuple[tuple[str, int, str], str]:
        return _ref_key(self.feature, self.location)


# ---- the aggregate --------------------------------------------------------------------------


@dataclass(frozen=True)
class SubsetFacts:
    """Every subset fact for one model. Each tuple is in its fact type's `sort_key` order."""

    occurrence: OccurrenceStructure | None
    bindings: tuple[BindingSourceFact, ...]
    sites: tuple[ExpressionSiteFact, ...]
    assertions: tuple[AssertionOwnerFact, ...]
    multiplicities: tuple[PartMultiplicityFact, ...]
    strings: tuple[StringValueFact, ...]
    constraints: IdentifiedConstraintFacts | None
    enumerated: frozenset[FactKind]
    failures: tuple[FactFailure, ...]

    def __post_init__(self) -> None:
        for name, facts in (
            ("bindings", self.bindings),
            ("sites", self.sites),
            ("assertions", self.assertions),
            ("multiplicities", self.multiplicities),
            ("strings", self.strings),
            ("failures", self.failures),
        ):
            keys = [fact.sort_key() for fact in facts]
            if keys != sorted(keys):
                raise ValueError(f"{name} are in sort-key order")
        if (self.occurrence is None) == (FactKind.OCCURRENCE in self.enumerated):
            raise ValueError(
                "the occurrence structure exists exactly when OCCURRENCE is enumerated"
            )
        if (self.constraints is None) == (FactKind.CONSTRAINT in self.enumerated):
            raise ValueError("the constraint facts exist exactly when CONSTRAINT is enumerated")
        for kind, facts in (
            (FactKind.BINDING_SOURCE, self.bindings),
            (FactKind.EXPRESSION_SITE, self.sites),
            (FactKind.ASSERTION_OWNER, self.assertions),
            (FactKind.PART_MULTIPLICITY, self.multiplicities),
            (FactKind.STRING_VALUE, self.strings),
        ):
            if facts and kind not in self.enumerated:
                raise ValueError(f"{kind.value} facts exist only for an enumerated kind")

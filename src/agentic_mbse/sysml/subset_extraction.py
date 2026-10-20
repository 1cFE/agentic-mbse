"""Extract the subset facts from SysIDE, once per kind, as a total result.

`extract_subset_facts(model, extra_roots=())` reads every fact kind the executable-subset rules
need. It decides nothing. Each kind is read by calling the helpers the generator itself calls,
so these facts agree with the generator by shared code; the occurrence facts are the one
exception, and they come from the summary port (`occurrence_extraction.py`), held to the
generator by its parity seed.

Totality: an element whose fact cannot be read becomes a :class:`FactFailure` with its closed
code; a kind whose population cannot be listed is left out of `enumerated`; an occurrence-build
abort becomes one `FactFailure(OCCURRENCE, <abort>)`. Nothing raises past this function except a
caller error (a non-`PartUsage` extra root) or a broken internal invariant.

What the generator does, read at sysml-codegen `b5663c07` (paths under `src/sysml_codegen/`),
and the shared helper this module calls for it:

| Fact | Generator | Shared helper used here |
|---|---|---|
| Expression sites and roles | `elaboration/expression_evidence.py:281-347`: every QN-bearing feature with a value (`_role_for_owner`: owned by a calc def → `calc_definition_dependency`; by a calc or constraint usage → `binding`; else a plain reference after the unit is stripped → `alias`, anything else → `computed_attribute`), plus every constraint definition's and usage's `result_expression` → `constraint_predicate` | `inspect_reference_uses` per site, as `_acquire` (`:256-275`) |
| Calc and calc-def bare results | not inventoried; a calc def's bare result becomes a `MANUAL_REQUIRED` stub at compilation | roles `calc_result_expression`, `other_expression_site` |
| Which members are bound inputs | `elaboration/elaborate.py:1878-1955` (`_collect_bound_members`): owned members whose direction reads `in` (`:1684-1685`) and that carry a value; the unit annotation is stripped once (`:1918-1921`) | `unit_annotation_value` |
| Binding-source class | `elaborate.py:2130-2171` (`_binding_evidence`): literal first (`is_literal_node`), then expression unless exactly one inventoried use and a reference metatype, then indexed or exact | `is_literal_node`, `inspect_reference_uses` |
| Reference metatype test | `elaborate.py:1114-1118` (`_is_reference_expression`): a feature chain or feature reference | `_is_reference_expression` here, the one copy |
| Self-binding | `extraction/binding_source.py:87-89`: the exact use's leaf is the formal itself | `ExactReferenceUse.path.leaf` |
| Unsupported invocation | `reference_use._require_supported_invocation`, reached through the inventory | `invocation_uses` |
| Conditional | an `if` operator expression; its branches leave the reference walk with `RESOLVED_TARGET_MISSING` | the operand primitives of `reference_use` |
| Assertion owners | attachment by semantic owner (`elaborate.py:759-787`) | `extract_identified_constraint_facts` forms; `semantic_owner` |
| Part multiplicities | `elaboration/occurrence.py:812-899` | the occurrence port's readings, not re-read |
| Strings | dropped from generated output (ES-010 omission) | `types`, both spellings |

The binding walk comes before classification, as the generator's inventory runs before any
binding is classified: a binding whose reference walk fails yields a failure, not a class.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.constraint_extraction import (
    _ASSERTED_FORMS,
    IdentifiedConstraintFacts,
    extract_identified_constraint_facts,
)
from agentic_mbse.sysml.expression import is_literal_node
from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.occurrence_extraction import (
    extract_occurrence_structure,
    safe_location,
    semantic_owner,
)
from agentic_mbse.sysml.occurrence_facts import (
    OccurrenceFailure,
    OccurrenceStructure,
    PartUsageReading,
)
from agentic_mbse.sysml.reference_use import (
    MAX_EXPRESSION_DEPTH,
    IndexedReferenceUse,
    evidence_error,
    inspect_reference_uses,
    invocation_uses,
    operand_bearing_operands,
    unit_annotation_value,
)
from agentic_mbse.sysml.subset_facts import (
    AssertionOwnerFact,
    BindingKind,
    BindingSourceFact,
    ExpressionSiteFact,
    FactFailure,
    FactKind,
    InvocationOutcome,
    InvocationsFailed,
    InvocationsWalked,
    OwnerKind,
    PartMultiplicityFact,
    ReferenceOutcome,
    ReferencesFailed,
    ReferencesWalked,
    ScopeCause,
    SiteInspection,
    SiteRole,
    StringSpelling,
    StringValueFact,
    SubsetFacts,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = ["extract_subset_facts"]

_is = SysideAdapter.is_instance


class _Sortable(Protocol):
    def sort_key(self) -> Any: ...


_Fact = TypeVar("_Fact", bound=_Sortable)

#: `_role_for_owner` (`expression_evidence.py:227-230`).
_DEFINITION_OWNERS = ("CalculationDefinition",)
_BINDING_OWNERS = ("CalculationUsage", "ConstraintUsage")

#: The standard-library type whose values the generator drops (ES-010 omission).
_STRING_TYPE = "ScalarValues::String"


class _IdentityError(Exception):
    """SysIDE gave an element no usable identity; recorded as `ScopeCause.ADAPTER_ERROR`."""


# ---- shared readings ----------------------------------------------------------------------


def _element_ref(element: Any) -> ElementRef:
    qualified_name = getattr(element, "qualified_name", None)
    try:
        return ElementRef(
            SysideAdapter.element_id(element),
            None if qualified_name is None else str(qualified_name),
            type(element).__name__,
        )
    except ValueError as error:
        raise _IdentityError(str(error)) from error


def _located(expression: Any, subject: Any) -> SafeLocation:
    """The expression's source position, named by the declaration it belongs to."""
    where = safe_location(expression)
    return SafeLocation(where.file, where.line, safe_location(subject).qualified_name)


def _authored(expression: Any) -> str | None:
    try:
        return SysideAdapter.authored_text(expression)
    except SemanticEvidenceError:
        return None


def _value_expression(expression: Any) -> Any:
    """The value a unit annotation wraps, or the expression itself (`unit_annotated_value`)."""
    value = unit_annotation_value(expression)
    return expression if value is None else value


def _is_reference_expression(expression: Any) -> bool:
    """`elaborate.py:1114-1118`: a feature chain or a feature reference, by mapped metatype."""
    return _is(expression, "FeatureChainExpression") or _is(
        expression, "FeatureReferenceExpression"
    )


def _owner_kind(owner: Any) -> OwnerKind:
    if owner is None:
        return OwnerKind.ABSENT
    for type_name, kind in (
        ("PartDefinition", OwnerKind.PART_DEFINITION),
        ("PartUsage", OwnerKind.PART_USAGE),
        ("CalculationDefinition", OwnerKind.CALCULATION_DEFINITION),
        ("CalculationUsage", OwnerKind.CALCULATION_USAGE),
        ("Package", OwnerKind.PACKAGE),
        ("RequirementDefinition", OwnerKind.REQUIREMENT_DEFINITION),
    ):
        if _is(owner, type_name):
            return kind
    return OwnerKind.OTHER


def _feature_values(model: Any) -> list[Any]:
    """Every QN-bearing feature with a value: the inventory's declared-feature sites (`:290-294`)."""
    return [
        feature
        for feature in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True)
        if getattr(feature, "qualified_name", None) is not None
        and getattr(feature, "feature_value_expression", None) is not None
    ]


# ---- binding sources ----------------------------------------------------------------------


def _is_bound_input(member: Any) -> bool:
    owner = getattr(member, "owning_type", None)
    if owner is None or not any(_is(owner, name) for name in _BINDING_OWNERS):
        return False
    return str(getattr(member, "direction", "")).rsplit(".", 1)[-1].lower() == "in"


def _binding_kind(formal: ElementRef, expression: Any, uses: tuple[Any, ...]) -> BindingKind:
    if is_literal_node(expression):
        return BindingKind.LITERAL
    if len(uses) != 1 or not _is_reference_expression(expression):
        return BindingKind.OTHER_EXPRESSION
    (use,) = uses
    if isinstance(use, IndexedReferenceUse):
        return BindingKind.INDEXED
    if use.path.leaf.element_id == formal.element_id:
        return BindingKind.SELF_BINDING
    return BindingKind.SINGLE_REFERENCE


def _binding_fact(member: Any) -> BindingSourceFact | None:
    """The member's binding-source fact, or ``None`` when it is not a bound input."""
    if not _is_bound_input(member):
        return None
    raw = member.feature_value_expression
    uses = inspect_reference_uses(raw)  # the inventory walk, before any classification
    formal = _element_ref(member)
    return BindingSourceFact(
        consumer=_element_ref(member.owning_type),
        formal=formal,
        location=_located(raw, member),
        authored=_authored(raw),
        kind=_binding_kind(formal, _value_expression(raw), uses),
    )


# ---- expression sites ---------------------------------------------------------------------


@dataclass(frozen=True)
class _SiteCandidate:
    declaration: Any
    expression: Any
    role: SiteRole | None  # None: a declared feature value, whose role depends on its owner


def _site_candidates(model: Any) -> list[_SiteCandidate]:
    candidates = [
        _SiteCandidate(f, f.feature_value_expression, None) for f in _feature_values(model)
    ]
    for type_name, role in (
        ("ConstraintDefinition", SiteRole.CONSTRAINT_PREDICATE),
        ("ConstraintUsage", SiteRole.CONSTRAINT_PREDICATE),
        ("CalculationDefinition", SiteRole.CALC_RESULT_EXPRESSION),
        ("CalculationUsage", SiteRole.OTHER_EXPRESSION_SITE),
    ):
        for declaration in SysideAdapter.elements_of_type(model, type_name, include_subtypes=True):
            predicate = getattr(declaration, "result_expression", None)
            if predicate is not None:
                candidates.append(_SiteCandidate(declaration, predicate, role))
    return candidates


def expression_sites(model: Any) -> list[tuple[Any, Any]]:
    """`(declaration, expression)` for every expression site the contract inspects.

    The same sites, in the same order, as the `EXPRESSION_SITE` facts; L6's advisories walk
    them (Item 3 design D12).
    """
    return [(c.declaration, c.expression) for c in _site_candidates(model)]


def _feature_role(feature: Any, expression: Any) -> SiteRole:
    """`_role_for_owner` (`expression_evidence.py:328-347`)."""
    owner = getattr(feature, "owning_type", None)
    if owner is not None:
        if any(_is(owner, name) for name in _DEFINITION_OWNERS):
            return SiteRole.CALC_DEFINITION_DEPENDENCY
        if any(_is(owner, name) for name in _BINDING_OWNERS):
            return SiteRole.BINDING
    if _is_reference_expression(_value_expression(expression)):
        return SiteRole.ALIAS
    return SiteRole.COMPUTED_ATTRIBUTE


def _conditionals(node: Any, *, depth: int) -> list[SafeLocation]:
    """Every ``if`` operator node, by a structural walk that resolves nothing.

    It visits what the reference walk visits: an indexed or chained reference is a leaf, a unit
    annotation is read through its value, and every other operand-bearing node is descended.
    """
    if node is None:
        return []
    if depth >= MAX_EXPRESSION_DEPTH:
        raise evidence_error(
            SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED,
            "subset_conditionals",
            "maximum expression traversal depth exhausted before all operands were visited",
            node,
        )
    if _is(node, "IndexExpression") or _is(node, "FeatureChainExpression"):
        return []
    value = unit_annotation_value(node)
    if value is not None:
        return _conditionals(value, depth=depth + 1)
    found = [safe_location(node)] if _is_conditional(node) else []
    for operand in operand_bearing_operands(node):
        found.extend(_conditionals(operand, depth=depth + 1))
    return found


def _is_conditional(node: Any) -> bool:
    """An operator expression whose operator reads ``if`` (the learning test pins the spelling)."""
    return _is(node, "OperatorExpression") and str(getattr(node, "operator", "") or "") == "if"


def _reference_outcome(expression: Any) -> ReferenceOutcome:
    try:
        uses = inspect_reference_uses(expression)
    except SemanticEvidenceError as error:
        return ReferencesFailed(error.code, error.detail)
    indexed = sum(isinstance(use, IndexedReferenceUse) for use in uses)
    return ReferencesWalked(len(uses), indexed)


def _invocation_outcome(expression: Any) -> InvocationOutcome:
    try:
        return InvocationsWalked(invocation_uses(expression))
    except SemanticEvidenceError as error:
        return InvocationsFailed(error.code, error.detail)


def _site_fact(candidate: _SiteCandidate) -> ExpressionSiteFact:
    declaration, expression = candidate.declaration, candidate.expression
    role = candidate.role or _feature_role(declaration, expression)
    return ExpressionSiteFact(
        feature=_element_ref(declaration),
        role=role,
        location=_located(expression, declaration),
        inspection=SiteInspection(
            references=_reference_outcome(expression),
            invocations=_invocation_outcome(expression),
            conditionals=tuple(_conditionals(expression, depth=0)),
        ),
    )


# ---- assertion owners, multiplicities, strings ----------------------------------------------


def _assertion_fact(usage_id_form: tuple[Any, str], live: dict[Any, Any]) -> AssertionOwnerFact:
    usage_id, form = usage_id_form
    constraint = live[usage_id]
    owner = semantic_owner(constraint)
    return AssertionOwnerFact(
        constraint=_element_ref(constraint),
        location=safe_location(constraint),
        form=form,
        asserted=form in _ASSERTED_FORMS,
        owner=None if owner is None else _element_ref(owner),
        owner_kind=_owner_kind(owner),
    )


def _string_fact(feature: Any) -> StringValueFact | None:
    """The feature's String-value fact, or ``None`` when its value is not a String."""
    if _is(feature, "ReferenceUsage") and getattr(feature, "direction", None) is not None:
        return None  # a directed reference usage is a parameter, not a shorthand value
    if not any(
        str(getattr(t, "qualified_name", "")) == _STRING_TYPE
        and SysideAdapter.document_tier(t).name == "StandardLibrary"
        for t in (getattr(feature, "types", None) or ())
    ):
        return None
    spelling = (
        StringSpelling.REDEFINITION_SHORTHAND
        if _is(feature, "ReferenceUsage")
        else StringSpelling.ATTRIBUTE_DECLARATION
    )
    return StringValueFact(_element_ref(feature), safe_location(feature), spelling)


def _string_candidates(model: Any) -> list[Any]:
    return [
        feature
        for type_name in ("AttributeUsage", "ReferenceUsage")
        for feature in SysideAdapter.elements_of_type(model, type_name)
        if getattr(feature, "feature_value_expression", None) is not None
    ]


def _multiplicity_fact(
    shape: PartUsageReading, usage: Any, structure: OccurrenceStructure
) -> PartMultiplicityFact:
    return PartMultiplicityFact(
        usage=_element_ref(usage),
        location=safe_location(usage),
        shape=shape,
        visits=tuple(v for v in structure.visits if v.usage_id == shape.usage_id),
    )


# ---- the total collector --------------------------------------------------------------------


@dataclass
class _Collector:
    failures: list[FactFailure]
    enumerated: set[FactKind]

    def collect(
        self,
        kind: FactKind,
        population: Callable[[], Iterable[Any]],
        fact_of: Callable[[Any], _Fact | None],
        subject_of: Callable[[Any], Any],
    ) -> list[_Fact]:
        """One fact per element of the kind's population; a failure per element that fails.

        `fact_of` returns ``None`` for an element that turns out not to belong to the kind.
        """
        try:
            elements = list(population())
        except SemanticEvidenceError as error:
            self.failures.append(
                FactFailure(
                    kind, None, ScopeCause.ENUMERATION_FAILED, f"{error.code.value}: {error.detail}"
                )
            )
            return []
        self.enumerated.add(kind)
        facts: list[_Fact] = []
        for element in elements:
            try:
                fact = fact_of(element)
            except SemanticEvidenceError as error:
                self.failures.append(
                    FactFailure(kind, safe_location(subject_of(element)), error.code, error.detail)
                )
                continue
            except _IdentityError as error:
                self.failures.append(
                    FactFailure(
                        kind,
                        safe_location(subject_of(element)),
                        ScopeCause.ADAPTER_ERROR,
                        str(error),
                    )
                )
                continue
            if fact is not None:
                facts.append(fact)
        return facts


def _occurrence(
    model: Any, extra_roots: Iterable[Any], collector: _Collector
) -> OccurrenceStructure | None:
    try:
        result = extract_occurrence_structure(model, extra_roots)
    except SemanticEvidenceError as error:
        collector.failures.append(FactFailure(FactKind.OCCURRENCE, None, error.code, error.detail))
        return None
    if isinstance(result, OccurrenceFailure):
        collector.failures.append(
            FactFailure(
                FactKind.OCCURRENCE,
                result.subject,
                result.abort,
                f"{result.stage.value}: {result.detail}",
            )
        )
        return None
    collector.enumerated.add(FactKind.OCCURRENCE)
    return result


def _constraints(
    model: Any,
    collector: _Collector,
    constraint_facts: Callable[[Any], IdentifiedConstraintFacts],
) -> IdentifiedConstraintFacts | None:
    try:
        constraints = constraint_facts(model)
    except SemanticEvidenceError as error:
        collector.failures.append(FactFailure(FactKind.CONSTRAINT, None, error.code, error.detail))
        return None
    collector.enumerated.add(FactKind.CONSTRAINT)
    return constraints


def _sorted(facts: list[_Fact]) -> tuple[_Fact, ...]:
    return tuple(sorted(facts, key=lambda fact: fact.sort_key()))


def extract_subset_facts(
    model: Any,
    extra_roots: Iterable[Any] = (),
    constraint_facts: Callable[[Any], IdentifiedConstraintFacts] = (
        extract_identified_constraint_facts
    ),
) -> SubsetFacts:
    """Every subset fact for one loaded model, each kind total, in deterministic order.

    `extra_roots` are caller-supplied `PartUsage` roots for the occurrence facts (design D7).
    `constraint_facts` produces the model's constraint facts; `validate` passes its run's shared
    extraction so the facts are computed once per run (Item 3 design D14).
    """
    collector = _Collector([], set())
    structure = _occurrence(model, extra_roots, collector)
    constraints = _constraints(model, collector, constraint_facts)

    multiplicities: list[PartMultiplicityFact] = []
    if structure is not None:
        # Read from the occurrence structure, so the kind is listed exactly when it is.
        part_usages = {
            SysideAdapter.element_id(u): u
            for u in SysideAdapter.elements_of_type(model, "PartUsage")
        }
        multiplicities = collector.collect(
            FactKind.PART_MULTIPLICITY,
            lambda: structure.part_usages,
            lambda shape: _multiplicity_fact(shape, part_usages[shape.usage_id], structure),
            lambda shape: part_usages[shape.usage_id],
        )

    assertions: list[AssertionOwnerFact] = []
    if constraints is not None:
        live = {
            SysideAdapter.element_id(c): c
            for c in SysideAdapter.elements_of_type(model, "ConstraintUsage", include_subtypes=True)
        }
        assertions = collector.collect(
            FactKind.ASSERTION_OWNER,
            lambda: [(u.usage_id, u.fact.source.form) for u in constraints.usages],
            lambda pair: _assertion_fact(pair, live),
            lambda pair: live[pair[0]],
        )

    bindings = collector.collect(
        FactKind.BINDING_SOURCE, lambda: _feature_values(model), _binding_fact, lambda f: f
    )
    sites = collector.collect(
        FactKind.EXPRESSION_SITE,
        lambda: _site_candidates(model),
        _site_fact,
        lambda c: c.expression,
    )
    strings = collector.collect(
        FactKind.STRING_VALUE, lambda: _string_candidates(model), _string_fact, lambda f: f
    )
    return SubsetFacts(
        occurrence=structure,
        bindings=_sorted(bindings),
        sites=_sorted(sites),
        assertions=_sorted(assertions),
        multiplicities=_sorted(multiplicities),
        strings=_sorted(strings),
        constraints=constraints,
        enumerated=frozenset(collector.enumerated),
        failures=tuple(sorted(collector.failures, key=lambda f: f.sort_key())),
    )

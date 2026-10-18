"""The executable-subset contract: which (shape, context) pairs the pinned generator executes.

A pure decision layer over the subset facts (`subset_facts.py`, `occurrence_facts.py`). It
imports no SysIDE, no `reference_use` and nothing from the generator.

How a decision is made:

1. **Rules recognize.** Each rule function reads the facts, recognizes a *shape* and computes
   its *context* from the closed :class:`ContextId` vocabulary. A rule never decides an outcome.
2. **Records decide.** The packaged records (`subset_profile_rules.toml`) map each
   (rule, shape, context) to an :class:`Outcome` and the evidence for it: a conformance case
   (`case:<id>`, packaged under `subset_cases/`, see `conformance_case.py`), or for
   `admitted` a corpus snapshot fixture. A pair the records do not list is `unconfirmed`. The
   loader refuses any non-`unconfirmed` entry without the evidence design D3 requires, so
   "no `refused` without a case" holds when the records load. The loader checks a citation's
   form only; that the case exists and shows its pair is checked by the test suite, and that
   the generator does what the case says is checked live in sysml-codegen.
3. **Missing facts are not findings.** A rule whose required fact kind was not enumerated, or
   whose element failed to extract, reports an :class:`UnverifiedCheck`, and the verdict is
   `INCOMPLETE`, or `REFUSED_INCOMPLETE` when a finding is refused. Rules whose facts are
   available still report.

**CLEAR is relative to the implemented rules.** A shape no rule recognizes draws no finding, so
a model can be CLEAR and still be refused by the generator. The refusal families the matrix
records with no rule are DEEP-QUALIFIED-WIRING (codegen's `deep_cross_scope_probe` corpus
fixture is refused and evaluates CLEAR), ES-002, ES-008, ES-009, the ES-010 refusal side and
CALC-DEF-BARE-RESULT; ES-011, G2, L6-LIBRARY-ALIAS-SOURCE and the PUSH-DOWN rows are tracked as
unconfirmed; and the site account's follow-up sites are outside every rule. A calculation
usage's bare result expression is dropped from the output (CALC-USAGE-BARE-RESULT-DROP); the
site rules report that drop as `omitted` only for the shapes they recognize.

Each finding is counterfactual: what the generator does with this construct as if the rest of
the model were admitted. The generator itself stops at its first error class.

Generator citations are sysml-codegen `b5663c07`, paths under `src/sysml_codegen/`. `SI_*`
codes appear only in the records' evidence fields, never in this module's vocabulary.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from importlib import resources
from typing import Any, TypeAlias
from uuid import UUID

import tomllib

from agentic_mbse.errors import SemanticEvidenceCode
from agentic_mbse.sysml.executable_profile import (
    PROFILE_SEMANTIC_VERSION,
    REASON_CODES,
    Eligibility,
    evaluate_identified_profile,
)
from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.occurrence_facts import (
    Attachment,
    AttachmentCause,
    MultiplicityReading,
    MultiplicityResolution,
    OccurrenceAbort,
    OccurrenceScope,
    OccurrenceStructure,
    PackageScope,
    Scope,
    UsageVisit,
)
from agentic_mbse.sysml.subset_facts import (
    BindingKind,
    ExpressionSiteFact,
    FactFailure,
    FactKind,
    InvocationsFailed,
    OwnerKind,
    ReferencesFailed,
    ReferencesWalked,
    ScopeCause,
    SiteRole,
    SubsetFacts,
)

__all__ = [
    "PACKAGED_RULES",
    "SUBSET_PROFILE_VERSION",
    "SUBSET_REASON_CODES",
    "Admission",
    "ContextId",
    "CaseRef",
    "CorpusRef",
    "EvidenceRef",
    "EvidenceStatus",
    "ExplicitRoots",
    "GeneratorEvidence",
    "GeneratorIdentity",
    "GeneratorRoots",
    "NoAdmittedContext",
    "Outcome",
    "Qualification",
    "RecordError",
    "RootSelection",
    "RuleRecord",
    "RuleRecords",
    "ScopeReport",
    "ShapeRecord",
    "SubsetCounts",
    "SubsetFinding",
    "SubsetProfileResult",
    "Unobservable",
    "UnverifiedCheck",
    "Verdict",
    "evaluate_subset_profile",
    "load_packaged_rule_records",
    "load_rule_records",
    "rule_contexts",
    "rule_ids",
    "rule_shapes",
]

#: The decision version. Changing the records or the invocation allowlist changes it; a test
#: pins a digest of both to this string (design invariant 9).
SUBSET_PROFILE_VERSION = "subset-profile/v2"

#: Every reason a finding can carry. Disjoint from the executable profile's `REASON_CODES`
#: (design D4); ES-007 findings carry those as `detail_reasons` instead.
SUBSET_REASON_CODES = frozenset(
    {
        "calc_owned_asserted_constraint",
        "calc_owned_non_asserted_constraint",
        "binding_source_expression",
        "binding_source_self_reference",
        "indexed_reference_unsupported",
        "part_multiplicity_ordered",
        "part_multiplicity_range",
        "part_multiplicity_unresolved_bound",
        "invocation_callable_unsupported",
        "conditional_expression_unsupported",
        "conditional_expression_resolved_branches",
        "constraint_predicate_blocked",
        "constraint_predicate_non_numerical",
        "string_value_not_generated",
    }
)


class Outcome(StrEnum):
    #: The generator stops on this construct.
    REFUSED = "refused"
    #: The generator executes it, never examines it, or turns it into a handwritten stub.
    ADMITTED = "admitted"
    #: The generator leaves it out of the generated contract by policy (NON_NUMERICAL).
    EXCLUDED = "excluded"
    #: The generator drops it from the generated output silently (String values, a calc
    #: usage's bare result expression).
    OMITTED = "omitted"
    #: The rule recognizes the pair and no conformance case has observed it.
    UNCONFIRMED = "unconfirmed"


class Verdict(StrEnum):
    #: At least one case-backed refusal, and a check could not run or the roots were narrowed.
    #: Both facts stand: the refusals are certain, and the findings are not the whole picture.
    REFUSED_INCOMPLETE = "refused_incomplete"
    #: No refusal, and a check could not run (missing facts) or the roots were narrowed. Never
    #: clean.
    INCOMPLETE = "incomplete"
    REFUSED = "refused"
    UNCONFIRMED = "unconfirmed"
    #: Complete, and every finding is admitted, excluded or omitted. The only clean verdict,
    #: and clean only over the implemented rules (see the module docstring): CLEAR does not
    #: mean the generator accepts the model.
    CLEAR = "clear"


class ContextId(StrEnum):
    """Where a shape sits, as far as the generator's decision depends on it. Closed."""

    #: The consumer's owner attaches to occurrences under the generator roots, and the
    #: consumer is the selected writer in at least one (`elaborate.py:759-787`, `:901-952`).
    OWNER_INSTANTIATED = "owner_instantiated"
    #: The consumer's owner is a package, which always gets one scope (`elaborate.py:781`).
    OWNER_PACKAGE = "owner_package"
    #: The owner could attach but has no occurrence: the generator never examines the shape
    #: (`elaborate.py:772-779`).
    OWNER_UNINSTANTIATED = "owner_uninstantiated"
    #: The calculation usage attaches to scopes and another writer wins in every one, so its
    #: bindings are never classified (`elaborate.py:1885`; design Implementation Note (a)).
    WRITER_OVERRIDDEN = "writer_overridden"
    #: The owner is absent or of a kind that attaches nothing (`elaborate.py:771`, `:787`).
    OWNER_OTHER = "owner_other"
    #: Expression-inventory role `binding` (`expression_evidence.py:328-347`).
    BINDING_VALUE = "binding_value"
    #: Inventory role `calc_definition_dependency`: a feature value owned by a calc def.
    CALC_DEFINITION_FEATURE_VALUE = "calc_definition_feature_value"
    #: Inventory roles `alias` and `computed_attribute`: any other declared feature value.
    ATTRIBUTE_VALUE = "attribute_value"
    #: Inventory role `constraint_predicate`.
    CONSTRAINT_PREDICATE = "constraint_predicate"
    #: A calc def's bare result expression; not inventoried, compiled to a stub
    #: (`extraction/expression_compiler.py:285-303`).
    CALC_RESULT_EXPRESSION = "calc_result_expression"
    #: A calc usage's bare result expression; not inventoried, and dropped from the output.
    OTHER_EXPRESSION_SITE = "other_expression_site"
    #: The constraint's semantic owner is a calc def (`elaborate.py:1625`, `graph.py:287-292`).
    CALC_DEFINITION_OWNER = "calc_definition_owner"
    #: The constraint's semantic owner is a calc usage, an unmapped owner kind
    #: (`elaborate.py:794-820`).
    CALC_USAGE_OWNER = "calc_usage_owner"
    #: The constraint's semantic owner is any other kind outside the generator's owner map
    #: (`elaborate.py:800-827`): an item def, an attribute def, a constraint def and so on.
    UNMAPPED_OWNER_KIND = "unmapped_owner_kind"
    #: The part usage is visited under a generator root (`occurrence.py:812-899`, `:927-1046`).
    EXPANDED_PART_USAGE = "expanded_part_usage"
    #: The part usage is never visited: a template, or a non-composite usage.
    UNEXPANDED_PART_USAGE = "unexpanded_part_usage"
    #: Reached only from a caller-supplied root the generator does not use (design D7).
    BEYOND_GENERATOR_ROOTS = "beyond_generator_roots"
    #: Not instantiated while the model has a part multiplicity the generator cannot expand,
    #: so whether the generator would reach it is undefined (design Implementation Note (b)).
    BENEATH_REFUSED_MULTIPLICITY = "beneath_refused_multiplicity"


#: Contexts no record may decide: they always report `unconfirmed`, by design.
ALWAYS_UNCONFIRMED_CONTEXTS = frozenset(
    {ContextId.BEYOND_GENERATOR_ROOTS, ContextId.BENEATH_REFUSED_MULTIPLICITY}
)


class EvidenceStatus(StrEnum):
    #: Every shape of the rule has at least one case-observed admission.
    CASE_OBSERVED = "case_observed"
    #: Some shapes do.
    PARTIAL = "partial"
    #: None does; every pair reports `unconfirmed` until a case observes it.
    CODE_READ_PENDING_ITEM_2 = "code_read_pending_item_2"


class Qualification(StrEnum):
    NONE = "none"
    #: Admitted as a handwritten stub (`MANUAL_REQUIRED`), not executed.
    MANUAL_STUB = "manual_stub"


# ---- records ----------------------------------------------------------------------------------

#: The 14 snapshot records of sysml-codegen's `tests/fixtures/v6_recapture_batch/batch.json` at
#: `b5663c07` (its `captured` list): the only corpus fixtures an `admitted` may cite (D3).
SNAPSHOT_FIXTURES = frozenset(
    {
        "agg_literal_probe",
        "attr_expr_probe",
        "constraint_inline",
        "constraint_multi_instance",
        "constraint_non_numerical",
        "d38_caret",
        "fusion_tea",
        "modeled_default_fidelity",
        "quoted_owner_formula",
        "retype_model",
        "sample_model",
        "shadowed_reference",
        "unresolvable_attr_probe",
        "wi014_toy",
    }
)

_GENERATOR_CODE = re.compile(r"SI_[A-Z0-9_]+")
_REV = re.compile(r"[0-9a-f]{40}")


class RecordError(ValueError):
    """The packaged records break the record schema or the evidence rules."""


@dataclass(frozen=True)
class CaseRef:
    """A packaged conformance case, `subset_cases/<case_id>/` (see `conformance_case.py`)."""

    case_id: str


@dataclass(frozen=True)
class CorpusRef:
    """A snapshot fixture of the generator's accepted corpus. Evidence for `admitted` only."""

    fixture: str


EvidenceRef: TypeAlias = CaseRef | CorpusRef


@dataclass(frozen=True)
class Admission:
    outcome: Outcome
    evidence: tuple[EvidenceRef, ...]
    qualification: Qualification


@dataclass(frozen=True)
class NoAdmittedContext:
    """Accepted spec amendment SA-1: the generator refuses the shape in every computable context."""

    citation: str
    statement: str


@dataclass(frozen=True)
class Unobservable:
    """An `unconfirmed` pair no case can observe, and why (Item 2a design § B).

    Its cases show what happens instead: another refusal that comes first, or a model the
    shape cannot be authored in. The pair still reports `unconfirmed`.
    """

    reason: str
    evidence: tuple[CaseRef, ...]


@dataclass(frozen=True)
class GeneratorEvidence:
    """A generator raise site and the code it carries. Evidence, not vocabulary."""

    code: str
    site: str


@dataclass(frozen=True)
class GeneratorIdentity:
    codegen_rev: str
    agentic_rev: str
    syside_version: str


@dataclass(frozen=True)
class ShapeRecord:
    shape_id: str
    reason: str
    #: The code a refusal of this shape carries (evidence field); required iff any context
    #: is refused.
    expected_code: str | None
    admissions: Mapping[ContextId, Admission]
    no_admitted_context: NoAdmittedContext | None
    unobservable: Mapping[ContextId, Unobservable]

    def contexts_with(self, outcome: Outcome) -> tuple[ContextId, ...]:
        return tuple(c for c, a in self.admissions.items() if a.outcome is outcome)


@dataclass(frozen=True)
class RuleRecord:
    rule_id: str
    title: str
    matrix_rows: tuple[str, ...]
    fact_requirements: frozenset[FactKind]
    shapes: tuple[ShapeRecord, ...]
    remedy: str
    semantic_limits: str
    #: A case whose model the generator runs (admitted, omitted or excluded). None only while
    #: the rule has no observed evidence.
    example_case: str | None
    doc_anchor: str
    evidence_status: EvidenceStatus
    generator_evidence: tuple[GeneratorEvidence, ...]

    def shape(self, shape_id: str) -> ShapeRecord:
        for shape in self.shapes:
            if shape.shape_id == shape_id:
                return shape
        raise KeyError(f"{self.rule_id} has no shape {shape_id!r}")


@dataclass(frozen=True)
class RuleRecords:
    verified_against: GeneratorIdentity
    rules: tuple[RuleRecord, ...]

    def rule(self, rule_id: str) -> RuleRecord:
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        raise KeyError(f"no rule record {rule_id!r}")


def _keys(table: Mapping[str, Any], required: set[str], optional: set[str], where: str) -> None:
    unknown = set(table) - required - optional
    missing = required - set(table)
    if unknown or missing:
        raise RecordError(
            f"{where}: unknown keys {sorted(unknown)}, missing keys {sorted(missing)}"
        )


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecordError(f"{where}: expected non-empty text, got {value!r}")
    return value


def _member(enum: type[StrEnum], value: Any, where: str) -> Any:
    try:
        return enum(value)
    except ValueError as error:
        raise RecordError(f"{where}: {value!r} is not a {enum.__name__}") from error


def _code(value: Any, where: str) -> str:
    if not isinstance(value, str) or not _GENERATOR_CODE.fullmatch(value):
        raise RecordError(f"{where}: {value!r} is not a generator code")
    return value


def _evidence(
    value: str, rule_id: str, shape_id: str, context: ContextId, where: str
) -> EvidenceRef:
    kind, _, target = value.partition(":")
    if kind == "case":
        pair = f"{rule_id}__{shape_id}__{context.value}"
        if target != pair and not target.startswith(f"{pair}__"):
            raise RecordError(f"{where}: case {target!r} is not a case of {pair}")
        return CaseRef(target)
    if kind == "corpus":
        if target not in SNAPSHOT_FIXTURES:
            raise RecordError(f"{where}: corpus fixture {target!r} is not a snapshot fixture")
        return CorpusRef(target)
    raise RecordError(f"{where}: evidence {value!r} is neither case:<id> nor corpus:<fixture>")


def _admission(
    table: Mapping[str, Any],
    rule_id: str,
    shape_id: str,
    contexts: frozenset[ContextId],
    where: str,
) -> tuple[ContextId, Admission]:
    _keys(table, {"context", "outcome", "evidence"}, {"qualification"}, where)
    context = _member(ContextId, table["context"], f"{where}.context")
    if context not in contexts:
        raise RecordError(f"{where}: rule {rule_id} cannot compute context {context.value}")
    if context in ALWAYS_UNCONFIRMED_CONTEXTS:
        raise RecordError(f"{where}: context {context.value} always reports unconfirmed")
    outcome = _member(Outcome, table["outcome"], f"{where}.outcome")
    if outcome is Outcome.UNCONFIRMED:
        raise RecordError(f"{where}: unconfirmed is the absence of an admission; do not list it")
    if not isinstance(table["evidence"], list) or not table["evidence"]:
        raise RecordError(f"{where}: outcome {outcome.value} requires evidence")
    evidence = tuple(
        _evidence(e, rule_id, shape_id, context, f"{where}.evidence") for e in table["evidence"]
    )
    if outcome is not Outcome.ADMITTED and not all(isinstance(e, CaseRef) for e in evidence):
        raise RecordError(f"{where}: outcome {outcome.value} requires case evidence only")
    qualification = _member(
        Qualification, table.get("qualification", "none"), f"{where}.qualification"
    )
    if qualification is not Qualification.NONE and outcome is not Outcome.ADMITTED:
        raise RecordError(f"{where}: only an admission carries a qualification")
    return context, Admission(outcome, evidence, qualification)


def _unobservable(
    table: Mapping[str, Any],
    rule_id: str,
    shape_id: str,
    contexts: frozenset[ContextId],
    where: str,
) -> tuple[ContextId, Unobservable]:
    _keys(table, {"context", "reason", "evidence"}, set(), where)
    context = _member(ContextId, table["context"], f"{where}.context")
    if context not in contexts:
        raise RecordError(f"{where}: rule {rule_id} cannot compute context {context.value}")
    if context in ALWAYS_UNCONFIRMED_CONTEXTS:
        raise RecordError(f"{where}: context {context.value} is unconfirmed by design")
    if not isinstance(table["evidence"], list) or not table["evidence"]:
        raise RecordError(f"{where}: an unobservable pair requires case evidence")
    evidence = tuple(
        _evidence(e, rule_id, shape_id, context, f"{where}.evidence") for e in table["evidence"]
    )
    cases = tuple(e for e in evidence if isinstance(e, CaseRef))
    if len(cases) != len(evidence):
        raise RecordError(f"{where}: an unobservable pair requires case evidence only")
    return context, Unobservable(_text(table["reason"], f"{where}.reason"), cases)


def _shape(
    table: Mapping[str, Any], rule_id: str, contexts: frozenset[ContextId], where: str
) -> ShapeRecord:
    _keys(
        table,
        {"id", "reason"},
        {"expected_code", "admission", "no_admitted_context", "unobservable"},
        where,
    )
    shape_id = _text(table["id"], f"{where}.id")
    reason = table["reason"]
    if reason not in SUBSET_REASON_CODES:
        raise RecordError(f"{where}: reason {reason!r} is not in SUBSET_REASON_CODES")
    admissions: dict[ContextId, Admission] = {}
    for i, entry in enumerate(table.get("admission", [])):
        context, admission = _admission(
            entry, rule_id, shape_id, contexts, f"{where}.admission[{i}]"
        )
        if context in admissions:
            raise RecordError(f"{where}: context {context.value} is listed twice")
        admissions[context] = admission
    unobservable: dict[ContextId, Unobservable] = {}
    for i, entry in enumerate(table.get("unobservable", [])):
        context, entry_record = _unobservable(
            entry, rule_id, shape_id, contexts, f"{where}.unobservable[{i}]"
        )
        if context in admissions:
            raise RecordError(f"{where}: context {context.value} is decided and unobservable")
        if context in unobservable:
            raise RecordError(f"{where}: context {context.value} is unobservable twice")
        unobservable[context] = entry_record
    refused = [c for c, a in admissions.items() if a.outcome is Outcome.REFUSED]
    expected = table.get("expected_code")
    expected_code = None if expected is None else _code(expected, f"{where}.expected_code")
    if refused and expected_code is None:
        raise RecordError(f"{where}: a refused shape needs its expected_code")
    # The gate proves a refusal is not a universal ban: some context of the shape has a case
    # that is not refused. An omission or exclusion proves that as well as an admission.
    not_refused_by_case = any(
        a.outcome is not Outcome.REFUSED and any(isinstance(e, CaseRef) for e in a.evidence)
        for a in admissions.values()
    )
    statement = table.get("no_admitted_context")
    no_admitted: NoAdmittedContext | None = None
    if statement is not None:
        _keys(statement, {"citation", "statement"}, set(), f"{where}.no_admitted_context")
        if not_refused_by_case:
            raise RecordError(
                f"{where}: no_admitted_context contradicts a case of a context not refused"
            )
        no_admitted = NoAdmittedContext(
            _text(statement["citation"], f"{where}.no_admitted_context.citation"),
            _text(statement["statement"], f"{where}.no_admitted_context.statement"),
        )
        uncovered = sorted(c.value for c in contexts - ALWAYS_UNCONFIRMED_CONTEXTS - set(refused))
        if uncovered:
            raise RecordError(
                f"{where}: no_admitted_context needs refused cases in every computable context; "
                f"missing {uncovered}"
            )
    if refused and not not_refused_by_case and no_admitted is None:
        raise RecordError(
            f"{where}: a refused shape needs a case of a context it is not refused in "
            "(admitted, omitted or excluded) or a no_admitted_context statement "
            "(design invariant 3 as generalized by audit S1, SA-1)"
        )
    ordered = dict(sorted(admissions.items(), key=lambda item: item[0].value))
    unobservable_ordered = dict(sorted(unobservable.items(), key=lambda item: item[0].value))
    return ShapeRecord(
        shape_id, reason, expected_code, ordered, no_admitted, unobservable_ordered
    )


def _status(shapes: tuple[ShapeRecord, ...]) -> EvidenceStatus:
    observed = [
        any(isinstance(e, CaseRef) for a in s.admissions.values() for e in a.evidence)
        for s in shapes
    ]
    if all(observed):
        return EvidenceStatus.CASE_OBSERVED
    return EvidenceStatus.PARTIAL if any(observed) else EvidenceStatus.CODE_READ_PENDING_ITEM_2


def _rule(table: Mapping[str, Any], where: str) -> RuleRecord:
    required = {
        "id",
        "title",
        "matrix_rows",
        "fact_requirements",
        "remedy",
        "semantic_limits",
        "doc_anchor",
        "evidence_status",
        "generator_evidence",
        "shape",
    }
    _keys(table, required, {"example_case"}, where)
    rule_id = _text(table["id"], f"{where}.id")
    spec = _RULES.get(rule_id)
    if spec is None:
        raise RecordError(f"{where}: no rule function implements {rule_id!r}")
    where = f"rule {rule_id}"
    requirements = frozenset(
        _member(FactKind, k, f"{where}.fact_requirements") for k in table["fact_requirements"]
    )
    if requirements != spec.requirements:
        raise RecordError(
            f"{where}: fact_requirements {sorted(requirements)} differ from what the rule reads "
            f"{sorted(spec.requirements)}"
        )
    shapes = tuple(_shape(s, rule_id, spec.contexts, f"{where} shape") for s in table["shape"])
    if [s.shape_id for s in shapes] != sorted(spec.shapes) or len(shapes) != len(spec.shapes):
        raise RecordError(
            f"{where}: shapes {[s.shape_id for s in shapes]} must be exactly, in order, "
            f"{sorted(spec.shapes)}"
        )
    status = _member(EvidenceStatus, table["evidence_status"], f"{where}.evidence_status")
    if status is not _status(shapes):
        raise RecordError(
            f"{where}: evidence_status {status.value} disagrees with its admissions "
            f"({_status(shapes).value})"
        )
    example: str | None = None
    if status is EvidenceStatus.CODE_READ_PENDING_ITEM_2:
        if "example_case" in table:
            raise RecordError(f"{where}: a rule with no observed evidence has no working example")
    else:
        example = _text(table.get("example_case"), f"{where}.example_case")
        if not example.startswith(f"{rule_id}__"):
            raise RecordError(f"{where}: example_case {example!r} is not a case of this rule")
    rows = table["matrix_rows"]
    if not isinstance(rows, list) or not rows:
        raise RecordError(f"{where}: matrix_rows must list the matrix rows the rule covers")
    evidence = []
    for i, item in enumerate(table["generator_evidence"]):
        _keys(item, {"code", "site"}, set(), f"{where}.generator_evidence[{i}]")
        evidence.append(
            GeneratorEvidence(
                _code(item["code"], f"{where}.generator_evidence[{i}].code"),
                _text(item["site"], f"{where}.generator_evidence[{i}].site"),
            )
        )
    if bool(evidence) != any(s.expected_code is not None for s in shapes):
        raise RecordError(
            f"{where}: generator_evidence cites the raise sites, so it is empty exactly when no "
            "shape has an expected_code"
        )
    return RuleRecord(
        rule_id=rule_id,
        title=_text(table["title"], f"{where}.title"),
        matrix_rows=tuple(_text(r, f"{where}.matrix_rows") for r in rows),
        fact_requirements=requirements,
        shapes=shapes,
        remedy=_text(table["remedy"], f"{where}.remedy"),
        semantic_limits=_text(table["semantic_limits"], f"{where}.semantic_limits"),
        example_case=example,
        doc_anchor=_text(table["doc_anchor"], f"{where}.doc_anchor"),
        evidence_status=status,
        generator_evidence=tuple(evidence),
    )


def load_rule_records(text: str) -> RuleRecords:
    """Parse and validate the records. Raises :class:`RecordError` on any violation.

    Enforced here: closed vocabularies, every field present, exactly the implemented rules and
    shapes, evidence for every listed outcome (D3), case ids naming their own pair, a case of
    a context that is not refused (admitted, omitted or excluded) or an SA-1 statement for
    every refused shape (invariant 3, generalized by audit S1), and an evidence status that
    matches the admissions. The citation's form is all this reads: that each cited case is
    packaged and shows its pair is `tests/test_subset_case_citations.py`'s check, and that the
    generator does what the case says is sysml-codegen's (Item 2a design D4).
    """
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise RecordError(f"records are not TOML: {error}") from error
    _keys(data, {"schema", "verified_against", "rule"}, set(), "records")
    if data["schema"] != 1:
        raise RecordError(f"records: unknown schema {data['schema']!r}")
    verified = data["verified_against"]
    _keys(verified, {"codegen_rev", "agentic_rev", "syside_version"}, set(), "verified_against")
    for key in ("codegen_rev", "agentic_rev"):
        if not isinstance(verified[key], str) or not _REV.fullmatch(verified[key]):
            raise RecordError(f"verified_against.{key} must be a full revision")
    rules = tuple(_rule(r, f"rule[{i}]") for i, r in enumerate(data["rule"]))
    ids = [r.rule_id for r in rules]
    if ids != sorted(_RULES) or len(set(ids)) != len(ids):
        raise RecordError(
            f"records must hold exactly the rules {sorted(_RULES)}, in order; got {ids}"
        )
    return RuleRecords(
        GeneratorIdentity(
            verified["codegen_rev"],
            verified["agentic_rev"],
            _text(verified["syside_version"], "verified_against.syside_version"),
        ),
        rules,
    )


def load_packaged_rule_records() -> RuleRecords:
    resource = resources.files("agentic_mbse.sysml").joinpath("subset_profile_rules.toml")
    return load_rule_records(resource.read_text(encoding="utf-8"))


# ---- results ----------------------------------------------------------------------------------

UnverifiedCause: TypeAlias = SemanticEvidenceCode | ScopeCause | OccurrenceAbort


@dataclass(frozen=True)
class SubsetFinding:
    """One declaration's (rule, shape, context) and the outcome the records give it (D6)."""

    rule_id: str
    shape_id: str
    context_id: ContextId
    outcome: Outcome
    reason: str
    detail_reasons: tuple[str, ...]
    subject: ElementRef
    location: SafeLocation
    occurrence_count: int | None
    via_roots: tuple[UUID, ...]
    evidence: tuple[EvidenceRef, ...]
    qualification: Qualification

    def __post_init__(self) -> None:
        if self.rule_id not in _RULES or self.shape_id not in _RULES[self.rule_id].shapes:
            raise ValueError(f"unknown rule or shape: {self.rule_id}/{self.shape_id}")
        if not isinstance(self.context_id, ContextId) or not isinstance(self.outcome, Outcome):
            raise TypeError("context_id and outcome come from their closed vocabularies")
        if self.reason not in SUBSET_REASON_CODES:
            raise ValueError(f"unknown subset reason: {self.reason!r}")
        unknown = [r for r in self.detail_reasons if r not in REASON_CODES]
        if unknown:
            raise ValueError(f"unknown executable-profile detail reasons: {unknown}")
        if (self.outcome is Outcome.UNCONFIRMED) != (not self.evidence):
            raise ValueError("a finding has evidence exactly when it is not unconfirmed")

    def sort_key(self) -> tuple[str, str, int, str, str, str, str]:
        return (
            self.rule_id,
            self.location.file or "",
            -1 if self.location.line is None else self.location.line,
            self.subject.qualified_name or "",
            self.context_id.value,
            self.shape_id,
            str(self.subject.element_id),
        )


@dataclass(frozen=True)
class UnverifiedCheck:
    """A check that could not run because its facts are missing. Never clean."""

    rule_id: str
    context_id: ContextId | None
    subject: SafeLocation | None
    cause: UnverifiedCause
    detail: str

    def __post_init__(self) -> None:
        if self.rule_id not in _RULES:
            raise ValueError(f"unknown rule {self.rule_id!r}")
        if not isinstance(self.cause, (SemanticEvidenceCode, ScopeCause, OccurrenceAbort)):
            raise TypeError(f"cause must be a closed failure code, got {self.cause!r}")

    def sort_key(self) -> tuple[str, tuple[str, int, str], str, str, str]:
        subject = self.subject.sort_key() if self.subject else ("", -1, "")
        context = self.context_id.value if self.context_id else ""
        return (self.rule_id, subject, context, str(self.cause.value), self.detail)


@dataclass(frozen=True)
class GeneratorRoots:
    """Evaluate with the generator's own roots (the default)."""


@dataclass(frozen=True)
class ExplicitRoots:
    """Evaluate with these roots. Each must be a generator root or an extracted caller root."""

    root_ids: frozenset[UUID]


RootSelection: TypeAlias = GeneratorRoots | ExplicitRoots
GENERATOR_ROOTS = GeneratorRoots()


@dataclass(frozen=True)
class ScopeReport:
    """What the evaluation covered.

    `roots_used` is empty only when the roots could not be computed (`roots_available`
    False); `narrowed` is true when a generator root was left out.
    """

    roots_available: bool
    generator_root_ids: tuple[UUID, ...]
    roots_used: tuple[UUID, ...]
    narrowed: bool
    enumerated: tuple[FactKind, ...]
    not_enumerated: tuple[FactKind, ...]


@dataclass(frozen=True)
class SubsetCounts:
    """Declarations (findings) and occurrences are counted apart (D6)."""

    declarations: int
    occurrences: int
    by_outcome: tuple[tuple[Outcome, int], ...]
    unverified: int
    unassessed_constraints: int


@dataclass(frozen=True)
class SubsetProfileResult:
    subset_profile_version: str
    executable_profile_version: str
    scope: ScopeReport
    verdict: Verdict
    findings: tuple[SubsetFinding, ...]
    unverified: tuple[UnverifiedCheck, ...]
    counts: SubsetCounts


# ---- rule functions: recognize a shape and compute its context, never an outcome --------------


@dataclass(frozen=True)
class _Recognized:
    shape_id: str
    context_id: ContextId
    subject: ElementRef
    location: SafeLocation
    occurrence_count: int | None
    via_roots: tuple[UUID, ...]
    detail_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Unverified:
    context_id: ContextId | None
    subject: SafeLocation
    cause: UnverifiedCause
    detail: str


_RuleOutput: TypeAlias = _Recognized | _Unverified


@dataclass(frozen=True)
class _Placement:
    context_id: ContextId
    occurrence_count: int | None
    via_roots: tuple[UUID, ...]


def _roots_of(scopes: Iterable[Scope]) -> tuple[UUID, ...]:
    return tuple(sorted({s.root_id for s in scopes if isinstance(s, OccurrenceScope)}, key=str))


class _Instantiation:
    """What the generator instantiates under the roots in use, read from the occurrence facts."""

    def __init__(self, structure: OccurrenceStructure, roots_used: frozenset[UUID]) -> None:
        self.structure = structure
        self.generator = roots_used & set(structure.generator_root_ids)
        self.callers = roots_used & set(structure.caller_root_ids)
        self.refused_multiplicity = any(
            v.count is None for v in structure.visits if v.root_id in self.generator
        )
        self.calc = {a.usage_id: a for a in structure.calc_attachments}
        self.constraint = {a.usage_id: a for a in structure.constraint_attachments}
        self.selected: dict[UUID, list[Scope]] = {}
        for writer in structure.writers:
            self.selected.setdefault(writer.selected_id, []).append(writer.scope)

    def _in_use(self, scope: Scope) -> bool:
        return isinstance(scope, PackageScope) or scope.root_id in self.generator

    def _beyond(self, scope: Scope) -> bool:
        return isinstance(scope, OccurrenceScope) and scope.root_id in self.callers

    def _unreached(self) -> _Placement:
        if self.refused_multiplicity:
            return _Placement(ContextId.BENEATH_REFUSED_MULTIPLICITY, None, ())
        return _Placement(ContextId.OWNER_UNINSTANTIATED, 0, ())

    def _examined(self, scopes: Iterable[Scope]) -> _Placement | None:
        """Instantiated or package placement over the scopes under the roots in use, if any."""
        in_use = [s for s in scopes if self._in_use(s)]
        if any(isinstance(s, PackageScope) for s in in_use):
            return _Placement(ContextId.OWNER_PACKAGE, len(in_use), ())
        if in_use:
            return _Placement(ContextId.OWNER_INSTANTIATED, len(in_use), _roots_of(in_use))
        return None

    def _beyond_or_unreached(self, scopes: Iterable[Scope]) -> _Placement:
        beyond = [s for s in scopes if self._beyond(s)]
        if beyond:
            return _Placement(ContextId.BEYOND_GENERATOR_ROOTS, len(beyond), _roots_of(beyond))
        return self._unreached()

    def _unattached(self, attachment: Attachment) -> _Placement | None:
        if attachment.cause in (
            AttachmentCause.OWNER_ABSENT,
            AttachmentCause.OWNER_KIND_UNATTACHABLE,
        ):
            return _Placement(ContextId.OWNER_OTHER, None, ())
        if attachment.cause is AttachmentCause.OWNER_HAS_NO_OCCURRENCES:
            return self._unreached()
        return None

    def constraint_placement(self, usage_id: UUID) -> _Placement:
        """A constraint usage is examined in every scope its owner attaches to (`elaborate.py:1332`)."""
        attachment = self.constraint[usage_id]
        return (
            self._unattached(attachment)
            or self._examined(attachment.scopes)
            or self._beyond_or_unreached(attachment.scopes)
        )

    def calc_placement(self, usage_id: UUID) -> _Placement:
        """A calculation usage's bindings are classified only where it is the selected writer."""
        attachment = self.calc[usage_id]
        placed = self._unattached(attachment) or self._examined(self.selected.get(usage_id, ()))
        if placed is not None:
            return placed
        overridden = [s for s in attachment.scopes if self._in_use(s)]
        if overridden:
            return _Placement(ContextId.WRITER_OVERRIDDEN, len(overridden), _roots_of(overridden))
        return self._beyond_or_unreached(attachment.scopes)

    def consumer_placement(self, consumer: ElementRef) -> _Placement:
        """Where a bound input's consuming calculation or constraint usage is examined.

        A consumer the generator attaches as neither (a calculation-usage subtype it does not
        enumerate, say) is `OWNER_OTHER`.
        """
        if consumer.element_id in self.calc:
            return self.calc_placement(consumer.element_id)
        if consumer.element_id in self.constraint:
            return self.constraint_placement(consumer.element_id)
        return _Placement(ContextId.OWNER_OTHER, None, ())


_ROLE_CONTEXT: Mapping[SiteRole, ContextId] = {
    SiteRole.BINDING: ContextId.BINDING_VALUE,
    SiteRole.CALC_DEFINITION_DEPENDENCY: ContextId.CALC_DEFINITION_FEATURE_VALUE,
    SiteRole.ALIAS: ContextId.ATTRIBUTE_VALUE,
    SiteRole.COMPUTED_ATTRIBUTE: ContextId.ATTRIBUTE_VALUE,
    SiteRole.CONSTRAINT_PREDICATE: ContextId.CONSTRAINT_PREDICATE,
    SiteRole.CALC_RESULT_EXPRESSION: ContextId.CALC_RESULT_EXPRESSION,
    SiteRole.OTHER_EXPRESSION_SITE: ContextId.OTHER_EXPRESSION_SITE,
}
_SITE_CONTEXTS = frozenset(_ROLE_CONTEXT.values())


def _at_site(site: ExpressionSiteFact, shape_id: str) -> _Recognized:
    return _Recognized(shape_id, _ROLE_CONTEXT[site.role], site.feature, site.location, None, ())


def _calc_owned_assertion(facts: SubsetFacts) -> list[_RuleOutput]:
    """ES-001: a constraint owned by a calc def, a calc usage or any owner kind the generator
    does not map (Item 2a P3 widened it to the last)."""
    context_of = {
        OwnerKind.CALCULATION_DEFINITION: ContextId.CALC_DEFINITION_OWNER,
        OwnerKind.CALCULATION_USAGE: ContextId.CALC_USAGE_OWNER,
        OwnerKind.OTHER: ContextId.UNMAPPED_OWNER_KIND,
    }
    out: list[_RuleOutput] = []
    for fact in facts.assertions:
        context = context_of.get(fact.owner_kind)
        if context is not None:
            shape = "asserted_constraint" if fact.asserted else "non_asserted_constraint"
            out.append(_Recognized(shape, context, fact.constraint, fact.location, None, ()))
    return out


def _indexed_reference(facts: SubsetFacts) -> list[_RuleOutput]:
    """An indexed reference anywhere the expression inventory walks (`expression_evidence.py:274-276`)."""
    out: list[_RuleOutput] = []
    for site in facts.sites:
        references = site.inspection.references
        if isinstance(references, ReferencesFailed):
            out.append(
                _Unverified(
                    _ROLE_CONTEXT[site.role], site.location, references.code, references.detail
                )
            )
        elif references.indexed_count:
            out.append(_at_site(site, "indexed_reference"))
    return out


def _invocation_callable(facts: SubsetFacts) -> list[_RuleOutput]:
    """ES-005: an invocation of a callable outside the shared allowlist."""
    out: list[_RuleOutput] = []
    for site in facts.sites:
        invocations = site.inspection.invocations
        if isinstance(invocations, InvocationsFailed):
            out.append(
                _Unverified(
                    _ROLE_CONTEXT[site.role], site.location, invocations.code, invocations.detail
                )
            )
        elif any(not use.supported for use in invocations.uses):
            out.append(_at_site(site, "unsupported_callable"))
    return out


def _conditional_expression(facts: SubsetFacts) -> list[_RuleOutput]:
    """ES-006: a conditional whose branch reference the walk cannot resolve.

    Refusal-eligible only for a recognized conditional with `RESOLVED_TARGET_MISSING`; any other
    reference failure leaves the site unverified, and a conditional whose references all
    resolve is a separate shape no case has observed.
    """
    out: list[_RuleOutput] = []
    for site in facts.sites:
        if not site.inspection.conditionals:
            continue
        references = site.inspection.references
        if isinstance(references, ReferencesWalked):
            out.append(_at_site(site, "conditional_resolved_branches"))
        elif references.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING:
            out.append(_at_site(site, "conditional_unresolved_branch"))
        else:
            out.append(
                _Unverified(
                    _ROLE_CONTEXT[site.role], site.location, references.code, references.detail
                )
            )
    return out


def _string_value_omission(facts: SubsetFacts) -> list[_RuleOutput]:
    """ES-010 omission: a String value, in either spelling, never reaches generated output."""
    return [
        _Recognized("string_value", ContextId.ATTRIBUTE_VALUE, f.feature, f.location, None, ())
        for f in facts.strings
    ]


def _binding_source(facts: SubsetFacts, view: _Instantiation) -> list[_RuleOutput]:
    """ES-003, ES-012 and self-binding: the generator's binding-source classifier."""
    shape_of = {
        BindingKind.OTHER_EXPRESSION: "expression_source",
        BindingKind.SELF_BINDING: "self_reference_source",
    }
    out: list[_RuleOutput] = []
    for fact in facts.bindings:
        shape = shape_of.get(fact.kind)
        if shape is None:
            continue
        place = view.consumer_placement(fact.consumer)
        out.append(
            _Recognized(
                shape,
                place.context_id,
                fact.formal,
                fact.location,
                place.occurrence_count,
                place.via_roots,
            )
        )
    return out


_MULTIPLICITY_SHAPE: Mapping[MultiplicityResolution, str] = {
    MultiplicityResolution.ORDERED: "ordered",
    MultiplicityResolution.RANGE: "range",
    MultiplicityResolution.UNRESOLVED_UPPER: "unresolved_bound",
    MultiplicityResolution.UNRESOLVED_LOWER: "unresolved_bound",
}

#: SysIDE 0.8.4 rejects a nonunique part usage and a negative bound before the generator runs,
#: so the owner retired both shapes (Item 1 R3 disposition, 2026-10-18). A model that loads
#: with either means that premise no longer holds, and the rule cannot say what follows.
_RETIRED_RESOLUTIONS = frozenset(
    {MultiplicityResolution.NONUNIQUE, MultiplicityResolution.NEGATIVE}
)


def _shape_of(reading: MultiplicityReading) -> str | None:
    resolution = reading.resolution
    if resolution in _RETIRED_RESOLUTIONS:
        raise ValueError(
            f"a part multiplicity resolved {resolution.value}, which SysIDE was found to reject "
            "before the generator runs; the part-multiplicity rule has no shape for it"
        )
    return _MULTIPLICITY_SHAPE.get(resolution)


def _visit_shapes(visits: Iterable[UsageVisit]) -> dict[str, list[UsageVisit]]:
    by_shape: dict[str, list[UsageVisit]] = {}
    for visit in visits:
        shape = _shape_of(visit.reading)
        if shape is not None:
            by_shape.setdefault(shape, []).append(visit)
    return by_shape


def _part_multiplicity(facts: SubsetFacts, view: _Instantiation) -> list[_RuleOutput]:
    """ES-004: a multiplicity the generator cannot expand, on a part usage it expands.

    Per visit: the same usage can resolve under one parent and not another. A usage never
    visited is read once with no parent.
    """
    out: list[_RuleOutput] = []
    for fact in facts.multiplicities:
        visited = [v for v in fact.visits if v.root_id in view.generator]
        context = ContextId.EXPANDED_PART_USAGE
        if not visited:
            visited = [v for v in fact.visits if v.root_id in view.callers]
            context = ContextId.BEYOND_GENERATOR_ROOTS
        if visited:
            for shape, visits in sorted(_visit_shapes(visited).items()):
                roots = tuple(sorted({v.root_id for v in visits}, key=str))
                out.append(
                    _Recognized(shape, context, fact.usage, fact.location, len(visits), roots)
                )
            continue
        unparented = _shape_of(fact.shape.reading)
        if unparented is not None:
            unvisited = (
                ContextId.BENEATH_REFUSED_MULTIPLICITY
                if view.refused_multiplicity
                else ContextId.UNEXPANDED_PART_USAGE
            )
            out.append(_Recognized(unparented, unvisited, fact.usage, fact.location, None, ()))
    return out


def _constraint_predicate(facts: SubsetFacts, view: _Instantiation) -> list[_RuleOutput]:
    """ES-007: the executable profile's BLOCK and NON_NUMERICAL, where the owner attaches.

    The profile is the authority (`evaluate_identified_profile`); UNASSESSED is counted by the
    evaluator and never admitted.
    """
    assert facts.constraints is not None
    owners = {a.constraint.element_id: a for a in facts.assertions}
    shape_of = {
        Eligibility.BLOCK: "blocked_predicate",
        Eligibility.NON_NUMERICAL: "non_numerical_predicate",
    }
    out: list[_RuleOutput] = []
    for item in evaluate_identified_profile(facts.constraints).decisions:
        shape = shape_of.get(item.decision.eligibility)
        if shape is None:
            continue
        owner = owners.get(item.usage_id)
        if owner is None:
            if not any(f.fact_kind is FactKind.ASSERTION_OWNER for f in facts.failures):
                raise ValueError(
                    f"constraint usage {item.usage_id} has neither a fact nor a failure"
                )
            continue  # its extraction failure is reported as unverified
        place = view.constraint_placement(item.usage_id)
        reasons = tuple(sorted({d.reason for d in item.decision.diagnostics}))
        out.append(
            _Recognized(
                shape,
                place.context_id,
                owner.constraint,
                owner.location,
                place.occurrence_count,
                place.via_roots,
                reasons,
            )
        )
    return out


@dataclass(frozen=True)
class _RuleSpec:
    shapes: frozenset[str]
    contexts: frozenset[ContextId]
    requirements: frozenset[FactKind]
    model_wide: Callable[[SubsetFacts], list[_RuleOutput]] | None
    instantiated: Callable[[SubsetFacts, _Instantiation], list[_RuleOutput]] | None


_OWNER_CONTEXTS = frozenset(
    {
        ContextId.OWNER_INSTANTIATED,
        ContextId.OWNER_PACKAGE,
        ContextId.OWNER_UNINSTANTIATED,
        ContextId.OWNER_OTHER,
        ContextId.BEYOND_GENERATOR_ROOTS,
        ContextId.BENEATH_REFUSED_MULTIPLICITY,
    }
)
_SITE_REQUIREMENTS = frozenset({FactKind.EXPRESSION_SITE})


def _model_wide(
    shapes: Iterable[str],
    contexts: Iterable[ContextId],
    requirements: Iterable[FactKind],
    function: Callable[[SubsetFacts], list[_RuleOutput]],
) -> _RuleSpec:
    return _RuleSpec(
        frozenset(shapes), frozenset(contexts), frozenset(requirements), function, None
    )


def _instantiated(
    shapes: Iterable[str],
    contexts: Iterable[ContextId],
    requirements: Iterable[FactKind],
    function: Callable[[SubsetFacts, _Instantiation], list[_RuleOutput]],
) -> _RuleSpec:
    return _RuleSpec(
        frozenset(shapes),
        frozenset(contexts),
        frozenset(requirements) | {FactKind.OCCURRENCE},
        None,
        function,
    )


_RULES: Mapping[str, _RuleSpec] = {
    "binding-source": _instantiated(
        ("expression_source", "self_reference_source"),
        _OWNER_CONTEXTS | {ContextId.WRITER_OVERRIDDEN},
        (FactKind.BINDING_SOURCE,),
        _binding_source,
    ),
    "calc-owned-assertion": _model_wide(
        ("asserted_constraint", "non_asserted_constraint"),
        (
            ContextId.CALC_DEFINITION_OWNER,
            ContextId.CALC_USAGE_OWNER,
            ContextId.UNMAPPED_OWNER_KIND,
        ),
        (FactKind.CONSTRAINT, FactKind.ASSERTION_OWNER),
        _calc_owned_assertion,
    ),
    "conditional-expression": _model_wide(
        ("conditional_resolved_branches", "conditional_unresolved_branch"),
        _SITE_CONTEXTS,
        _SITE_REQUIREMENTS,
        _conditional_expression,
    ),
    "constraint-predicate": _instantiated(
        ("blocked_predicate", "non_numerical_predicate"),
        _OWNER_CONTEXTS,
        (FactKind.CONSTRAINT, FactKind.ASSERTION_OWNER),
        _constraint_predicate,
    ),
    "indexed-reference": _model_wide(
        ("indexed_reference",), _SITE_CONTEXTS, _SITE_REQUIREMENTS, _indexed_reference
    ),
    "invocation-callable": _model_wide(
        ("unsupported_callable",), _SITE_CONTEXTS, _SITE_REQUIREMENTS, _invocation_callable
    ),
    "part-multiplicity": _instantiated(
        ("ordered", "range", "unresolved_bound"),
        (
            ContextId.EXPANDED_PART_USAGE,
            ContextId.UNEXPANDED_PART_USAGE,
            ContextId.BEYOND_GENERATOR_ROOTS,
            ContextId.BENEATH_REFUSED_MULTIPLICITY,
        ),
        (FactKind.PART_MULTIPLICITY,),
        _part_multiplicity,
    ),
    "string-value-omission": _model_wide(
        ("string_value",),
        (ContextId.ATTRIBUTE_VALUE,),
        (FactKind.STRING_VALUE,),
        _string_value_omission,
    ),
}


def rule_ids() -> tuple[str, ...]:
    """Every implemented rule, in record order."""
    return tuple(sorted(_RULES))


def rule_shapes(rule_id: str) -> frozenset[str]:
    return _RULES[rule_id].shapes


def rule_contexts(rule_id: str) -> frozenset[ContextId]:
    """Every context the rule can compute, including the always-unconfirmed ones."""
    return _RULES[rule_id].contexts


PACKAGED_RULES = load_packaged_rule_records()


# ---- the evaluator ----------------------------------------------------------------------------


def _roots_used(structure: OccurrenceStructure, roots: RootSelection) -> frozenset[UUID]:
    if isinstance(roots, GeneratorRoots):
        return frozenset(structure.generator_root_ids)
    known = set(structure.generator_root_ids) | set(structure.caller_root_ids)
    unknown = roots.root_ids - known
    if unknown:
        raise ValueError(
            f"roots {sorted(map(str, unknown))} are neither generator roots nor extracted caller "
            "roots; pass them to extract_subset_facts(extra_roots=...)"
        )
    return roots.root_ids


def _missing_kind_checks(rule_id: str, facts: SubsetFacts, kind: FactKind) -> list[UnverifiedCheck]:
    failures = [f for f in facts.failures if f.fact_kind is kind]
    if not failures:
        return [
            UnverifiedCheck(
                rule_id,
                None,
                None,
                ScopeCause.ENUMERATION_FAILED,
                f"{kind.value} was not enumerated",
            )
        ]
    return [
        UnverifiedCheck(rule_id, None, f.subject, f.cause, f"{kind.value}: {f.detail}")
        for f in failures
    ]


def _element_checks(rule_id: str, failures: Iterable[FactFailure]) -> list[UnverifiedCheck]:
    return [
        UnverifiedCheck(rule_id, None, f.subject, f.cause, f"{f.fact_kind.value}: {f.detail}")
        for f in failures
    ]


def _decide(rule: RuleRecord, recognized: _Recognized) -> SubsetFinding:
    shape = rule.shape(recognized.shape_id)
    admission = shape.admissions.get(recognized.context_id)
    return SubsetFinding(
        rule_id=rule.rule_id,
        shape_id=recognized.shape_id,
        context_id=recognized.context_id,
        outcome=Outcome.UNCONFIRMED if admission is None else admission.outcome,
        reason=shape.reason,
        detail_reasons=recognized.detail_reasons,
        subject=recognized.subject,
        location=recognized.location,
        occurrence_count=recognized.occurrence_count,
        via_roots=recognized.via_roots,
        evidence=() if admission is None else admission.evidence,
        qualification=Qualification.NONE if admission is None else admission.qualification,
    )


def _verdict(
    findings: tuple[SubsetFinding, ...], unverified: tuple[UnverifiedCheck, ...], narrowed: bool
) -> Verdict:
    outcomes = {f.outcome for f in findings}
    if unverified or narrowed:
        if Outcome.REFUSED in outcomes:
            return Verdict.REFUSED_INCOMPLETE
        return Verdict.INCOMPLETE
    if Outcome.REFUSED in outcomes:
        return Verdict.REFUSED
    if Outcome.UNCONFIRMED in outcomes:
        return Verdict.UNCONFIRMED
    return Verdict.CLEAR


def _unassessed(facts: SubsetFacts) -> int:
    if facts.constraints is None:
        return 0
    return sum(
        item.decision.eligibility is Eligibility.UNASSESSED
        for item in evaluate_identified_profile(facts.constraints).decisions
    )


def evaluate_subset_profile(
    facts: SubsetFacts,
    rules: RuleRecords = PACKAGED_RULES,
    roots: RootSelection = GENERATOR_ROOTS,
) -> SubsetProfileResult:
    """Apply every rule to the facts and decide each recognized pair from the records.

    `roots` selects which roots count as instantiated: the generator's own by default. A
    caller root (extracted with `extract_subset_facts(extra_roots=...)`) widens the scope, and
    whatever only it reaches is `BEYOND_GENERATOR_ROOTS`, which is never refused. Leaving out a
    generator root narrows the scope, and the verdict is then `INCOMPLETE` (or
    `REFUSED_INCOMPLETE`).
    """
    structure = facts.occurrence
    roots_used = frozenset() if structure is None else _roots_used(structure, roots)
    view = None if structure is None else _Instantiation(structure, roots_used)
    narrowed = structure is not None and not set(structure.generator_root_ids) <= roots_used

    findings: list[SubsetFinding] = []
    unverified: list[UnverifiedCheck] = []
    for rule in rules.rules:
        spec = _RULES[rule.rule_id]
        missing = sorted(spec.requirements - facts.enumerated)
        if missing:
            for kind in missing:
                unverified.extend(_missing_kind_checks(rule.rule_id, facts, kind))
            continue
        unverified.extend(
            _element_checks(
                rule.rule_id, (f for f in facts.failures if f.fact_kind in spec.requirements)
            )
        )
        if spec.model_wide is not None:
            outputs = spec.model_wide(facts)
        else:
            assert spec.instantiated is not None and view is not None
            outputs = spec.instantiated(facts, view)
        for output in outputs:
            if isinstance(output, _Unverified):
                unverified.append(
                    UnverifiedCheck(
                        rule.rule_id, output.context_id, output.subject, output.cause, output.detail
                    )
                )
                continue
            if output.context_id not in spec.contexts:
                raise ValueError(
                    f"{rule.rule_id} computed context {output.context_id.value} it does not declare"
                )
            findings.append(_decide(rule, output))

    keys = Counter((f.rule_id, f.shape_id, f.context_id, f.subject.element_id) for f in findings)
    duplicated = [k for k, n in keys.items() if n > 1]
    if duplicated:
        raise ValueError(f"findings are keyed by declaration; duplicated {duplicated[:3]}")
    ordered = tuple(sorted(findings, key=lambda f: f.sort_key()))
    unverified_sorted = tuple(sorted(set(unverified), key=lambda u: u.sort_key()))
    outcome_counts = Counter(f.outcome for f in ordered)
    return SubsetProfileResult(
        subset_profile_version=SUBSET_PROFILE_VERSION,
        executable_profile_version=PROFILE_SEMANTIC_VERSION,
        scope=ScopeReport(
            roots_available=structure is not None,
            generator_root_ids=() if structure is None else structure.generator_root_ids,
            roots_used=tuple(sorted(roots_used, key=str)),
            narrowed=narrowed,
            enumerated=tuple(sorted(facts.enumerated)),
            not_enumerated=tuple(sorted(set(FactKind) - facts.enumerated)),
        ),
        verdict=_verdict(ordered, unverified_sorted, narrowed),
        findings=ordered,
        unverified=unverified_sorted,
        counts=SubsetCounts(
            declarations=len(ordered),
            occurrences=sum(f.occurrence_count or 0 for f in ordered),
            by_outcome=tuple((o, outcome_counts[o]) for o in Outcome),
            unverified=len(unverified_sorted),
            unassessed_constraints=_unassessed(facts),
        ),
    )

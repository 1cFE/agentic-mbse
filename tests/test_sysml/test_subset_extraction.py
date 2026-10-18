"""Subset facts: every kind extracted once, totally, from the generator's shared helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml import subset_extraction
from agentic_mbse.sysml.occurrence_facts import MultiplicityResolution, OccurrenceAbort
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_facts import (
    BindingKind,
    FactKind,
    InvocationsFailed,
    InvocationsWalked,
    OwnerKind,
    ReferencesFailed,
    ReferencesWalked,
    ScopeCause,
    SiteRole,
    StringSpelling,
    SubsetFacts,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

FIXTURES = Path(__file__).parents[1] / "fixtures" / "subset_profile"
CASES = FIXTURES / "cases"
SEED = FIXTURES / "occurrence"
ALL_KINDS = frozenset(FactKind)


def load(path: Path) -> Any:
    model, diagnostics = SysideAdapter.load_model([path])
    assert not diagnostics.contains_errors(), [str(d) for d in diagnostics.all]
    return model


def last(qualified_name: str | None) -> str:
    assert qualified_name is not None
    return qualified_name.split("::")[-1]


def raise_code(code: SemanticEvidenceCode) -> Any:
    def raising(*_args: Any, **_kwargs: Any) -> Any:
        raise SemanticEvidenceError(code, operation="injected", detail="injected failure")

    return raising


def test_binding_source_kinds() -> None:
    facts = extract_subset_facts(load(CASES / "binding_kinds.sysml"))
    kinds = {last(b.formal.qualified_name): b.kind for b in facts.bindings}
    assert kinds == {
        "lit": BindingKind.LITERAL,
        "src": BindingKind.SINGLE_REFERENCE,
        "me": BindingKind.SELF_BINDING,
        "idx": BindingKind.OTHER_EXPRESSION,  # an IndexExpression is not a reference metatype
        "cidx": BindingKind.INDEXED,  # a chain with an indexed head
        "tup": BindingKind.OTHER_EXPRESSION,
        "unit": BindingKind.LITERAL,  # the unit annotation is stripped first
    }
    assert {b.consumer.qualified_name for b in facts.bindings} == {"bk::P::f"}
    assert {b.authored for b in facts.bindings} >= {"xs#(1)", "3.0 [SI::m]", "me"}
    assert facts.failures == ()
    assert facts.enumerated == ALL_KINDS


def test_reference_walk_failure_becomes_fact_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subset_extraction,
        "inspect_reference_uses",
        raise_code(SemanticEvidenceCode.RESOLVED_TARGET_MISSING),
    )
    facts = extract_subset_facts(load(CASES / "binding_kinds.sysml"))
    assert facts.bindings == ()
    assert {f.cause for f in facts.failures} == {SemanticEvidenceCode.RESOLVED_TARGET_MISSING}
    assert {f.fact_kind for f in facts.failures} == {FactKind.BINDING_SOURCE}
    assert all(f.subject is not None and f.subject.line for f in facts.failures)
    # Sites keep reporting: their reference outcome records the failure instead.
    assert facts.sites
    assert all(isinstance(s.inspection.references, ReferencesFailed) for s in facts.sites)


def test_invocation_walk_failure_is_recorded_on_the_site(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subset_extraction,
        "invocation_uses",
        raise_code(SemanticEvidenceCode.OPERAND_ITERATION_FAILED),
    )
    facts = extract_subset_facts(load(CASES / "expression_sites.sysml"))
    assert facts.sites
    for site in facts.sites:
        assert site.inspection.invocations == InvocationsFailed(
            SemanticEvidenceCode.OPERAND_ITERATION_FAILED, "injected failure"
        )


def test_enumeration_failure_leaves_the_kind_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subset_extraction,
        "_string_candidates",
        raise_code(SemanticEvidenceCode.METATYPE_CHECK_FAILED),
    )
    facts = extract_subset_facts(load(CASES / "string_spellings.sysml"))
    assert FactKind.STRING_VALUE not in facts.enumerated
    assert facts.enumerated == ALL_KINDS - {FactKind.STRING_VALUE}
    (failure,) = facts.failures
    assert (failure.fact_kind, failure.subject, failure.cause) == (
        FactKind.STRING_VALUE,
        None,
        ScopeCause.ENUMERATION_FAILED,
    )
    assert "METATYPE_CHECK_FAILED" in failure.detail
    assert facts.strings == ()


def test_occurrence_abort_is_one_failure_and_other_kinds_report() -> None:
    model, _ = SysideAdapter.load_model([SEED / "f1_abort_recursive_containment" / "model.sysml"])
    facts = extract_subset_facts(model)
    assert facts.occurrence is None
    occurrence_failures = [f for f in facts.failures if f.fact_kind is FactKind.OCCURRENCE]
    (failure,) = occurrence_failures
    assert failure.cause is OccurrenceAbort.RECURSIVE_CONTAINMENT
    assert failure.detail.startswith("occurrences: ")
    assert facts.enumerated == ALL_KINDS - {FactKind.OCCURRENCE, FactKind.PART_MULTIPLICITY}
    assert facts.multiplicities == ()


def test_expression_site_roles_and_inspection() -> None:
    facts = extract_subset_facts(load(CASES / "expression_sites.sysml"))
    roles = {(last(s.feature.qualified_name), s.role) for s in facts.sites}
    assert roles == {
        ("r", SiteRole.CALC_DEFINITION_DEPENDENCY),
        ("Bare", SiteRole.CALC_RESULT_EXPRESSION),
        ("Positive", SiteRole.CONSTRAINT_PREDICATE),
        ("x", SiteRole.COMPUTED_ATTRIBUTE),  # a literal is not a plain reference
        ("mirror", SiteRole.ALIAS),
        ("scaled", SiteRole.COMPUTED_ATTRIBUTE),
        ("product_value", SiteRole.COMPUTED_ATTRIBUTE),
        ("v", SiteRole.BINDING),
        ("q", SiteRole.BINDING),
        ("anon", SiteRole.OTHER_EXPRESSION_SITE),
    }
    by_name = {last(s.feature.qualified_name): s for s in facts.sites}
    product = by_name["product_value"].inspection
    assert product.references == ReferencesFailed(
        SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED,
        product.references.detail,  # type: ignore[union-attr]
    )
    assert isinstance(product.invocations, InvocationsWalked)
    assert [(u.callable_name, u.supported) for u in product.invocations.uses] == [
        ("NumericalFunctions::product", False)
    ]
    assert by_name["mirror"].inspection.references == ReferencesWalked(1, 0)
    assert all(s.inspection.conditionals == () for s in facts.sites)


def test_conditionals_are_found_where_the_reference_walk_fails() -> None:
    facts = extract_subset_facts(load(CASES / "conditional.sysml"))
    by_name = {s.feature.qualified_name: s.inspection for s in facts.sites}
    for name in ("cd::Pick::r", "cd::P::chosen", "cd::P::nested", "cd::P::k::a"):
        inspection = by_name[name]
        assert len(inspection.conditionals) == 1, name
        assert isinstance(inspection.references, ReferencesFailed)
        assert inspection.references.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING
    assert by_name["cd::P::plain"].conditionals == ()
    assert by_name["cd::P::plain"].references == ReferencesWalked(2, 0)
    (nested,) = by_name["cd::P::nested"].conditionals
    assert nested.line == 9


def test_assertion_owner_forms_and_kinds() -> None:
    facts = extract_subset_facts(load(CASES / "assertion_owners.sysml"))
    owners = {(c.constraint.qualified_name, c.form, c.owner_kind) for c in facts.assertions}
    assert owners == {
        ("ao::Checked::inDef", "inline", OwnerKind.CALCULATION_DEFINITION),
        ("ao::Checked::plainInDef", "plain_usage", OwnerKind.CALCULATION_DEFINITION),
        ("ao::P::inPart", "inline", OwnerKind.PART_DEFINITION),
        (None, "inline", OwnerKind.PART_DEFINITION),  # the anonymous assert
        ("ao::P::typed", "definition_typed", OwnerKind.PART_DEFINITION),
        ("ao::P::c::inUsage", "inline", OwnerKind.CALCULATION_USAGE),
    }
    assert facts.constraints is not None
    assert len(facts.constraints.usages) == len(facts.assertions)


def test_string_values_in_both_spellings() -> None:
    facts = extract_subset_facts(load(CASES / "string_spellings.sysml"))
    strings = {(s.feature.qualified_name, s.spelling) for s in facts.strings}
    assert strings == {
        ("ss::Gen::label", StringSpelling.ATTRIBUTE_DECLARATION),
        ("ss::gen::fuel", StringSpelling.REDEFINITION_SHORTHAND),
    }


def test_part_multiplicities_come_from_the_occurrence_port() -> None:
    model, _ = SysideAdapter.load_model([SEED / "es004_refused_range_parts" / "model.sysml"])
    facts = extract_subset_facts(model)
    assert facts.occurrence is not None
    assert len(facts.multiplicities) == len(facts.occurrence.part_usages)
    resolutions = {
        last(m.usage.qualified_name): {v.reading.resolution for v in m.visits}
        for m in facts.multiplicities
    }
    assert MultiplicityResolution.RANGE in resolutions["servers"]
    for fact in facts.multiplicities:
        assert all(v.usage_id == fact.usage.element_id for v in fact.visits)


def test_extraction_is_deterministic() -> None:
    first = extract_subset_facts(load(CASES / "expression_sites.sysml"))
    second = extract_subset_facts(load(CASES / "expression_sites.sysml"))
    assert _comparable(first) == _comparable(second)


def _comparable(facts: SubsetFacts) -> tuple[Any, ...]:
    """The facts minus the constraint sidecar, whose mutable payload has no equality contract."""
    return (
        facts.occurrence,
        facts.bindings,
        facts.sites,
        facts.assertions,
        facts.multiplicities,
        facts.strings,
        facts.enumerated,
        facts.failures,
    )


def test_both_dc3_style_failures_are_listed_not_raised() -> None:
    """An unsupported call and a conditional in one model: extraction returns, failures listed."""
    model, _ = SysideAdapter.load_model(
        [SEED / "es005_refused_product" / "model.sysml", CASES / "conditional.sysml"]
    )
    facts = extract_subset_facts(model)
    assert facts.enumerated == ALL_KINDS
    failed = [s for s in facts.sites if isinstance(s.inspection.references, ReferencesFailed)]
    assert {s.inspection.references.code for s in failed} == {  # type: ignore[union-attr]
        SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED,
        SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
    }

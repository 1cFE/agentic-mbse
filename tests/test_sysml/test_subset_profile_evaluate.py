"""The evaluator on synthetic facts: outcomes come from records, and missing facts never read clean.

No model is loaded. Records are written per test, so these tests do not depend on which
admissions the packaged records hold.
"""

from __future__ import annotations

import dataclasses
import random

import pytest

from agentic_mbse.errors import SemanticEvidenceCode
from agentic_mbse.sysml.occurrence_facts import OccurrenceAbort
from agentic_mbse.sysml.subset_facts import (
    BindingKind,
    FactFailure,
    FactKind,
    InvocationsFailed,
    InvocationsWalked,
    OwnerKind,
    ReferencesFailed,
    ReferencesWalked,
    ScopeCause,
    SiteRole,
)
from agentic_mbse.sysml.subset_profile import (
    PACKAGED_RULES,
    ContextId,
    ExplicitRoots,
    Outcome,
    ProbeRef,
    SubsetFinding,
    SubsetProfileResult,
    Verdict,
    evaluate_subset_profile,
)
from tests.helpers import subset_synthetic as syn
from tests.helpers.subset_records import records_with

MISSING = SemanticEvidenceCode.RESOLVED_TARGET_MISSING

# One refused pair per rule the tests below exercise, with the admitted partner the loader
# demands (design invariant 3). Probe ids are only syntax here; the evidence test owns them.
RECORDS = records_with(
    {
        ("binding-source", "expression_source"): {
            "owner_instantiated": "refused",
            "owner_package": "refused",
            "owner_uninstantiated": "admitted",
            "writer_overridden": "admitted",
        },
        ("invocation-callable", "unsupported_callable"): {
            "attribute_value": "refused",
            "calc_result_expression": "admitted",
        },
        ("part-multiplicity", "range"): {
            "expanded_part_usage": "refused",
            "unexpanded_part_usage": "admitted",
        },
        ("string-value-omission", "string_value"): {"attribute_value": "omitted"},
    }
)


def by_rule(result: SubsetProfileResult, rule_id: str) -> list[SubsetFinding]:
    return [f for f in result.findings if f.rule_id == rule_id]


def instantiated_binding() -> syn.SubsetFacts:
    """Calc usage `P::t` in part def `P`, instantiated once by root `p`, binds `(a, b)`."""
    scope = syn.occ("fx::p")
    return syn.facts(
        occurrence=syn.structure(
            roots=["fx::p"],
            calc=[syn.attached("fx::P::t", "fx::P", [scope])],
            writers=[syn.writer("fx::P::t", scope, "fx::P::t", ["fx::P::t"])],
        ),
        bindings=[syn.binding("fx::P::t", "fx::P::t::xs", BindingKind.OTHER_EXPRESSION, 7)],
    )


# ---- outcomes come from records -------------------------------------------------------------


def test_listed_pair_takes_the_record_outcome_and_evidence() -> None:
    result = evaluate_subset_profile(instantiated_binding(), RECORDS)
    (finding,) = by_rule(result, "binding-source")
    assert (finding.context_id, finding.outcome) == (ContextId.OWNER_INSTANTIATED, Outcome.REFUSED)
    assert finding.reason == "binding_source_expression"
    assert finding.evidence == (ProbeRef("binding-source__expression_source__owner_instantiated"),)
    assert finding.occurrence_count == 1 and finding.via_roots == (syn.uid("fx::p"),)
    assert result.verdict is Verdict.REFUSED


def test_unlisted_pair_is_unconfirmed() -> None:
    facts = syn.facts(
        bindings=[syn.binding("fx::P::t", "fx::P::t::me", BindingKind.SELF_BINDING, 7)],
        occurrence=instantiated_binding().occurrence,
    )
    result = evaluate_subset_profile(facts, RECORDS)
    (finding,) = by_rule(result, "binding-source")
    assert finding.shape_id == "self_reference_source"
    assert finding.outcome is Outcome.UNCONFIRMED and finding.evidence == ()
    assert result.verdict is Verdict.UNCONFIRMED


def test_stripping_a_pairs_evidence_makes_it_unconfirmed() -> None:
    stripped = records_with(
        {
            ("binding-source", "expression_source"): {"owner_uninstantiated": "admitted"},
        }
    )
    (finding,) = by_rule(
        evaluate_subset_profile(instantiated_binding(), stripped), "binding-source"
    )
    assert finding.outcome is Outcome.UNCONFIRMED


def test_literal_and_single_reference_bindings_are_not_findings() -> None:
    facts = syn.facts(
        occurrence=instantiated_binding().occurrence,
        bindings=[
            syn.binding("fx::P::t", "fx::P::t::a", BindingKind.LITERAL, 7),
            syn.binding("fx::P::t", "fx::P::t::b", BindingKind.SINGLE_REFERENCE, 8),
        ],
    )
    result = evaluate_subset_profile(facts, RECORDS)
    assert result.findings == () and result.verdict is Verdict.CLEAR


def test_clear_only_when_every_finding_is_admitted_excluded_or_omitted() -> None:
    facts = syn.facts(strings=[syn.string("fx::P::unit", 4)])
    result = evaluate_subset_profile(facts, RECORDS)
    assert [f.outcome for f in result.findings] == [Outcome.OMITTED]
    assert result.verdict is Verdict.CLEAR


# ---- binding placement ----------------------------------------------------------------------


def placed(attachment: syn.Attachment, writers: list[syn.WriterSelection]) -> ContextId:
    facts = syn.facts(
        occurrence=syn.structure(roots=["fx::p"], calc=[attachment], writers=writers),
        bindings=[syn.binding("fx::P::t", "fx::P::t::xs", BindingKind.OTHER_EXPRESSION, 7)],
    )
    (finding,) = by_rule(evaluate_subset_profile(facts, RECORDS), "binding-source")
    return finding.context_id


def test_binding_placement_follows_attachment_and_writer_selection() -> None:
    scope = syn.occ("fx::p")
    package = syn.pkg("fx")
    assert placed(syn.attached("fx::P::t", "fx::P", []), []) is ContextId.OWNER_UNINSTANTIATED
    assert placed(syn.unattachable("fx::P::t", "fx::Calc"), []) is ContextId.OWNER_OTHER
    assert (
        placed(
            syn.attached("fx::P::t", "fx", [package]),
            [syn.writer("fx::P::t", package, "fx::P::t", ["fx::P::t"])],
        )
        is ContextId.OWNER_PACKAGE
    )
    overridden = syn.writer("fx::P::t", scope, "fx::Q::t", ["fx::P::t", "fx::Q::t"])
    assert (
        placed(syn.attached("fx::P::t", "fx::P", [scope]), [overridden])
        is ContextId.WRITER_OVERRIDDEN
    )


def test_uninstantiated_beside_a_refused_multiplicity_is_beneath_it() -> None:
    facts = syn.facts(
        occurrence=syn.structure(
            roots=["fx::rack"],
            visits=[syn.visit("fx::rack", "fx::rack", syn.ranged(1, 4))],
            calc=[syn.attached("fx::P::t", "fx::P", [])],
        ),
        bindings=[syn.binding("fx::P::t", "fx::P::t::xs", BindingKind.OTHER_EXPRESSION, 7)],
    )
    (finding,) = by_rule(evaluate_subset_profile(facts, RECORDS), "binding-source")
    assert finding.context_id is ContextId.BENEATH_REFUSED_MULTIPLICITY
    assert finding.outcome is Outcome.UNCONFIRMED


# ---- roots ----------------------------------------------------------------------------------


def two_roots_binding() -> syn.SubsetFacts:
    """`P::t` is instantiated only under caller root `T::site`, not under generator root `p`."""
    caller = syn.occ("fx::T::site")
    return syn.facts(
        occurrence=syn.structure(
            roots=["fx::p"],
            callers=["fx::T::site"],
            calc=[syn.attached("fx::P::t", "fx::P", [caller])],
            writers=[syn.writer("fx::P::t", caller, "fx::P::t", ["fx::P::t"])],
        ),
        bindings=[syn.binding("fx::P::t", "fx::P::t::xs", BindingKind.OTHER_EXPRESSION, 7)],
    )


def test_default_roots_ignore_caller_roots_and_report_the_roots_used() -> None:
    result = evaluate_subset_profile(two_roots_binding(), RECORDS)
    (finding,) = by_rule(result, "binding-source")
    assert finding.context_id is ContextId.OWNER_UNINSTANTIATED
    assert result.scope.roots_used == (syn.uid("fx::p"),) and not result.scope.narrowed


def test_widened_roots_report_beyond_generator_roots_never_refused() -> None:
    roots = ExplicitRoots(frozenset({syn.uid("fx::p"), syn.uid("fx::T::site")}))
    result = evaluate_subset_profile(two_roots_binding(), RECORDS, roots)
    (finding,) = by_rule(result, "binding-source")
    assert finding.context_id is ContextId.BEYOND_GENERATOR_ROOTS
    assert finding.outcome is Outcome.UNCONFIRMED
    assert set(result.scope.roots_used) == roots.root_ids


def test_narrowed_roots_are_incomplete() -> None:
    result = evaluate_subset_profile(instantiated_binding(), RECORDS, ExplicitRoots(frozenset()))
    assert result.scope.narrowed and result.verdict is Verdict.INCOMPLETE


def test_an_unextracted_root_is_a_caller_error() -> None:
    with pytest.raises(ValueError, match="extra_roots"):
        evaluate_subset_profile(
            instantiated_binding(), RECORDS, ExplicitRoots(frozenset({syn.uid("fx::nowhere")}))
        )


def test_unavailable_roots_leave_root_dependent_rules_unverified() -> None:
    failure = FactFailure(
        FactKind.OCCURRENCE, syn.loc(3), OccurrenceAbort.RECURSIVE_CONTAINMENT, "occurrences: cycle"
    )
    facts = syn.facts(
        missing=[FactKind.OCCURRENCE, FactKind.PART_MULTIPLICITY],
        failures=[failure],
        strings=[syn.string("fx::P::unit", 4)],
    )
    result = evaluate_subset_profile(facts, RECORDS)
    by_cause = {(u.rule_id, u.cause) for u in result.unverified}
    for rule in ("binding-source", "part-multiplicity", "constraint-predicate"):
        assert (rule, OccurrenceAbort.RECURSIVE_CONTAINMENT) in by_cause
    assert not result.scope.roots_available and result.scope.roots_used == ()
    assert [f.rule_id for f in result.findings] == ["string-value-omission"]
    assert result.verdict is Verdict.INCOMPLETE


# ---- failure injection: (a) extraction, (b) enumeration, (c) occurrence ----------------------


def test_failed_fact_is_unverified_and_others_still_report() -> None:
    """Design stencil: an expression-site failure, a binding finding beside it."""
    base = instantiated_binding()
    facts = dataclasses.replace(
        base, failures=(FactFailure(FactKind.EXPRESSION_SITE, None, MISSING, ""),)
    )
    result = evaluate_subset_profile(facts, RECORDS)
    assert result.verdict is Verdict.INCOMPLETE
    assert {u.rule_id for u in result.unverified} >= {
        "invocation-callable",
        "conditional-expression",
    }
    assert any(f.rule_id == "binding-source" for f in result.findings)


def test_element_failure_carries_rule_safe_location_and_cause() -> None:
    subject = syn.loc(12, "fx::P::t::xs")
    failure = FactFailure(
        FactKind.BINDING_SOURCE, subject, SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED, "walk"
    )
    facts = dataclasses.replace(instantiated_binding(), failures=(failure,))
    result = evaluate_subset_profile(facts, RECORDS)
    (check,) = [u for u in result.unverified if u.rule_id == "binding-source"]
    assert (check.subject, check.cause) == (
        subject,
        SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED,
    )
    assert by_rule(result, "binding-source"), "the binding that did extract still reports"
    assert result.verdict is Verdict.INCOMPLETE


def test_enumeration_failure_is_unverified_for_its_rules_only() -> None:
    failure = FactFailure(FactKind.STRING_VALUE, None, ScopeCause.ENUMERATION_FAILED, "listing")
    facts = dataclasses.replace(
        instantiated_binding(),
        enumerated=frozenset(FactKind) - {FactKind.STRING_VALUE},
        failures=(failure,),
    )
    result = evaluate_subset_profile(facts, RECORDS)
    assert [(u.rule_id, u.cause) for u in result.unverified] == [
        ("string-value-omission", ScopeCause.ENUMERATION_FAILED)
    ]
    assert by_rule(result, "binding-source")
    assert result.verdict is Verdict.INCOMPLETE


def test_a_kind_missing_without_its_own_failure_is_still_unverified() -> None:
    facts = syn.facts(missing=[FactKind.ASSERTION_OWNER])
    result = evaluate_subset_profile(facts, RECORDS)
    assert {u.rule_id for u in result.unverified} == {
        "calc-owned-assertion",
        "constraint-predicate",
    }
    assert {u.cause for u in result.unverified} == {ScopeCause.ENUMERATION_FAILED}


# ---- expression-site rules ------------------------------------------------------------------


def test_site_rules_read_their_own_walk_and_unverify_on_its_failure() -> None:
    walked_badly = InvocationsFailed(SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED, "deep")
    facts = syn.facts(
        sites=[
            syn.site(
                "fx::P::eff",
                SiteRole.COMPUTED_ATTRIBUTE,
                5,
                invocations=InvocationsWalked((syn.call("product"),)),
            ),
            syn.site(
                "fx::P::tot",
                SiteRole.COMPUTED_ATTRIBUTE,
                6,
                invocations=InvocationsWalked((syn.call("sum", supported=True),)),
            ),
            syn.site("fx::P::deep", SiteRole.COMPUTED_ATTRIBUTE, 7, invocations=walked_badly),
            syn.site(
                "fx::Bare",
                SiteRole.CALC_RESULT_EXPRESSION,
                8,
                invocations=InvocationsWalked((syn.call("max"),)),
            ),
        ]
    )
    result = evaluate_subset_profile(facts, RECORDS)
    found = {
        (f.subject.qualified_name, f.context_id, f.outcome)
        for f in by_rule(result, "invocation-callable")
    }
    assert found == {
        ("fx::P::eff", ContextId.ATTRIBUTE_VALUE, Outcome.REFUSED),
        ("fx::Bare", ContextId.CALC_RESULT_EXPRESSION, Outcome.ADMITTED),
    }
    (check,) = [u for u in result.unverified if u.rule_id == "invocation-callable"]
    assert check.context_id is ContextId.ATTRIBUTE_VALUE and check.cause is walked_badly.code


def test_conditional_is_refusal_eligible_only_with_a_missing_target() -> None:
    other = SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED
    facts = syn.facts(
        sites=[
            syn.site(
                "fx::P::a",
                SiteRole.COMPUTED_ATTRIBUTE,
                5,
                references=ReferencesFailed(MISSING, "x"),
                conditionals=[5],
            ),
            syn.site(
                "fx::P::b",
                SiteRole.COMPUTED_ATTRIBUTE,
                6,
                references=ReferencesFailed(other, "x"),
                conditionals=[6],
            ),
            syn.site(
                "fx::P::c",
                SiteRole.COMPUTED_ATTRIBUTE,
                7,
                references=ReferencesWalked(0, 0),
                conditionals=[7],
            ),
            syn.site(
                "fx::P::d",
                SiteRole.COMPUTED_ATTRIBUTE,
                8,
                references=ReferencesFailed(MISSING, "x"),
            ),
        ]
    )
    result = evaluate_subset_profile(facts, RECORDS)
    shapes = {
        (f.subject.qualified_name, f.shape_id) for f in by_rule(result, "conditional-expression")
    }
    assert shapes == {
        ("fx::P::a", "conditional_unresolved_branch"),
        ("fx::P::c", "conditional_resolved_branches"),
    }
    unverified = {
        (u.rule_id, u.subject.qualified_name if u.subject else None) for u in result.unverified
    }
    assert ("conditional-expression", "fx::P::b") in unverified
    assert ("conditional-expression", "fx::P::d") not in unverified, "no conditional there"
    assert ("indexed-reference", "fx::P::d") in unverified, (
        "the walk failed, so indexes are unknown"
    )


def test_calc_owned_assertion_reads_owner_kind_and_asserted_form() -> None:
    facts = syn.facts(
        assertions=[
            syn.assertion(
                "fx::C::f1", "fx::C", OwnerKind.CALCULATION_DEFINITION, asserted=True, line=3
            ),
            syn.assertion(
                "fx::C::f2", "fx::C", OwnerKind.CALCULATION_DEFINITION, asserted=False, line=4
            ),
            syn.assertion(
                "fx::P::t::f3", "fx::P::t", OwnerKind.CALCULATION_USAGE, asserted=False, line=5
            ),
            syn.assertion("fx::P::f4", "fx::P", OwnerKind.PART_DEFINITION, asserted=True, line=6),
        ]
    )
    found = {
        (f.subject.qualified_name, f.shape_id, f.context_id)
        for f in by_rule(evaluate_subset_profile(facts, RECORDS), "calc-owned-assertion")
    }
    assert found == {
        ("fx::C::f1", "asserted_constraint", ContextId.CALC_DEFINITION_OWNER),
        ("fx::C::f2", "non_asserted_constraint", ContextId.CALC_DEFINITION_OWNER),
        ("fx::P::t::f3", "non_asserted_constraint", ContextId.CALC_USAGE_OWNER),
    }


# ---- part multiplicity, counts and dedup -----------------------------------------------------


def test_multiplicity_is_per_visit_and_counted_by_declaration_and_occurrence() -> None:
    racks = syn.multiplicity(
        "fx::Rack::servers",
        syn.ranged(1, 4),
        [
            syn.visit("fx::Rack::servers", "fx::a", syn.ranged(1, 4), parent="fx::a"),
            syn.visit("fx::Rack::servers", "fx::b", syn.ranged(1, 4), parent="fx::b"),
        ],
        5,
    )
    template = syn.multiplicity("fx::T::spares", syn.ranged(0, 2), [], 9)
    fine = syn.multiplicity(
        "fx::T::one", syn.exact(1), [syn.visit("fx::T::one", "fx::a", syn.exact(1))], 10
    )
    facts = syn.facts(
        occurrence=syn.structure(roots=["fx::a", "fx::b"], visits=[*racks.visits, *fine.visits]),
        multiplicities=[racks, template, fine],
    )
    result = evaluate_subset_profile(facts, RECORDS)
    found = {
        (f.subject.qualified_name, f.context_id, f.outcome, f.occurrence_count)
        for f in result.findings
    }
    assert found == {
        ("fx::Rack::servers", ContextId.EXPANDED_PART_USAGE, Outcome.REFUSED, 2),
        ("fx::T::spares", ContextId.BENEATH_REFUSED_MULTIPLICITY, Outcome.UNCONFIRMED, None),
    }
    assert (result.counts.declarations, result.counts.occurrences) == (2, 2)


def test_an_unvisited_template_without_any_refused_visit_is_unexpanded() -> None:
    template = syn.multiplicity("fx::T::spares", syn.ranged(0, 2), [], 9)
    result = evaluate_subset_profile(syn.facts(multiplicities=[template]), RECORDS)
    (finding,) = result.findings
    assert (finding.context_id, finding.outcome) == (
        ContextId.UNEXPANDED_PART_USAGE,
        Outcome.ADMITTED,
    )


# ---- versions and determinism ---------------------------------------------------------------


def test_result_reports_both_versions() -> None:
    result = evaluate_subset_profile(syn.facts(), PACKAGED_RULES)
    assert result.subset_profile_version.startswith("subset-profile/")
    assert result.executable_profile_version.startswith("executable-profile/")
    assert result.verdict is Verdict.CLEAR


def test_permuted_fact_order_gives_identical_output() -> None:
    """Facts must arrive sorted, so permute the inputs the builder sorts, then compare."""
    sites = [
        syn.site(
            f"fx::P::s{n}",
            SiteRole.COMPUTED_ATTRIBUTE,
            n,
            invocations=InvocationsWalked((syn.call("max"),)),
        )
        for n in range(1, 9)
    ]
    strings = [syn.string(f"fx::P::u{n}", 20 + n) for n in range(5)]
    first = evaluate_subset_profile(syn.facts(sites=sites, strings=strings), RECORDS)
    rng = random.Random(7)
    for _ in range(5):
        rng.shuffle(sites)
        rng.shuffle(strings)
        assert evaluate_subset_profile(syn.facts(sites=sites, strings=strings), RECORDS) == first
    keys = [f.sort_key() for f in first.findings]
    assert keys == sorted(keys)

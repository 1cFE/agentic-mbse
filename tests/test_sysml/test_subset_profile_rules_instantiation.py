"""The instantiation-dependent rules on their packaged cases, and roots and order end to end.

Every packaged case of `binding-source`, `part-multiplicity` and `constraint-predicate`,
including every B5 variation case and every control, reproduces its stored screen answer: the
verdict and every finding, not only the construct's (Item 2a design D14). The stored answers
themselves are held to the records by `tests/test_subset_case_citations.py`, and to the
generator by sysml-codegen. Then roots: the default is the generator's, a widened set reports
`beyond_generator_roots` (never refused), a narrowed set is incomplete. Then determinism over a
model split across documents, loaded in every order.
"""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.sysml.conformance_case import PackagedCase, load_packaged_case, screen_answer
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_profile import (
    PACKAGED_RULES,
    ContextId,
    ExplicitRoots,
    Outcome,
    SubsetFinding,
    SubsetProfileResult,
    Verdict,
    evaluate_subset_profile,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from tests.helpers.subset_cases import at_construct, cases_of, evaluate

CASES = Path(__file__).parents[1] / "fixtures" / "subset_profile" / "cases"
RULES = {"binding-source", "part-multiplicity", "constraint-predicate"}
MULTI_DOC = sorted((CASES / "multi_doc").glob("*.sysml"))


def load(*paths: Path) -> Any:
    model, diagnostics = SysideAdapter.load_model(list(paths))
    assert not diagnostics.contains_errors(), [str(d) for d in diagnostics.all]
    return model


@pytest.mark.parametrize("case", cases_of(RULES), ids=lambda c: c.case_id)
def test_screen_reproduces_the_stored_answer(case: PackagedCase) -> None:
    assert screen_answer(evaluate(case)) == case.screen


#: Appendix C's variation cases (B5): for each instantiation-dependent refused pair, the reach
#: paths the context label claims to cover. Each named variant must be a cited record case.
REACH_VARIANTS = {
    ("binding-source", "expression_source", "owner_instantiated"): {
        "part_usage_owner",
        "subtype",
        "nested",
        "indexed_owner",
        "selected_and_overridden",
    },
    ("binding-source", "self_reference_source", "owner_instantiated"): {
        "part_usage_owner",
        "subtype",
        "indexed_owner",
    },
    ("constraint-predicate", "blocked_predicate", "owner_instantiated"): {
        "part_usage_owner",
        "subtype",
        "under_two",
    },
    ("part-multiplicity", "range", "expanded_part_usage"): {
        "depth_two",
        "under_two",
        "subtype",
        "root",
    },
    ("part-multiplicity", "ordered", "expanded_part_usage"): {"under_two"},
    ("part-multiplicity", "unresolved_bound", "expanded_part_usage"): {"under_two"},
}


def test_every_instantiation_dependent_refused_pair_has_its_reach_variations() -> None:
    refused = {
        (rule, shape.shape_id, context.value)
        for rule in RULES
        for shape in PACKAGED_RULES.rule(rule).shapes
        for context in shape.contexts_with(Outcome.REFUSED)
        if context in (ContextId.OWNER_INSTANTIATED, ContextId.EXPANDED_PART_USAGE)
    }
    assert refused == set(REACH_VARIANTS)
    for (rule, shape, context), variants in REACH_VARIANTS.items():
        cited = {
            ref.case_id
            for ref in PACKAGED_RULES.rule(rule)
            .shape(shape)
            .admissions[ContextId(context)]
            .evidence
        }
        prefix = f"{rule}__{shape}__{context}__"
        present = {c.removeprefix(prefix) for c in cited if c.startswith(prefix)}
        assert variants <= present, ((rule, shape, context), variants - present)


def test_non_numerical_predicate_is_excluded_with_its_profile_reasons() -> None:
    case = load_packaged_case("constraint-predicate__non_numerical_predicate__owner_instantiated")
    (finding,) = at_construct(evaluate(case), case, "constraint-predicate")
    assert finding.outcome is Outcome.EXCLUDED
    assert finding.detail_reasons == ("warn_non_numerical_predicate",)


def test_an_overridden_writers_binding_is_counted_by_the_scopes_it_loses() -> None:
    case = load_packaged_case("binding-source__expression_source__writer_overridden")
    (finding,) = at_construct(evaluate(case), case, "binding-source")
    assert finding.outcome is Outcome.ADMITTED and finding.occurrence_count == 1


# ---- roots, end to end ----------------------------------------------------------------------


def template_site(model: Any) -> Any:
    return next(
        u
        for u in SysideAdapter.elements_of_type(model, "PartUsage")
        if str(u.qualified_name) == "wr::Templates::site"
    )


def binding(result: SubsetProfileResult) -> SubsetFinding:
    (finding,) = [f for f in result.findings if f.rule_id == "binding-source"]
    return finding


def test_default_roots_leave_a_template_uninstantiated_and_report_the_roots_used() -> None:
    model = load(CASES / "widened_roots.sysml")
    result = evaluate_subset_profile(extract_subset_facts(model))
    assert binding(result).context_id is ContextId.OWNER_UNINSTANTIATED
    assert result.scope.roots_used == result.scope.generator_root_ids != ()


def test_widened_roots_do_not_refuse() -> None:
    model = load(CASES / "widened_roots.sysml")
    template = template_site(model)
    facts = extract_subset_facts(model, extra_roots=(template,))
    widened = frozenset({*facts.occurrence.generator_root_ids, *facts.occurrence.caller_root_ids})  # type: ignore[union-attr]
    result = evaluate_subset_profile(facts, roots=ExplicitRoots(widened))
    finding = binding(result)
    assert finding.context_id is ContextId.BEYOND_GENERATOR_ROOTS
    assert finding.outcome is Outcome.UNCONFIRMED and finding.via_roots == (
        SysideAdapter.element_id(template),
    )
    assert set(result.scope.roots_used) == widened and not result.scope.narrowed
    assert result.verdict is Verdict.UNCONFIRMED


def test_narrowed_roots_report_incomplete_scope() -> None:
    case = load_packaged_case("binding-source__expression_source__owner_instantiated")
    facts = extract_subset_facts(load(*case.model_files()))
    result = evaluate_subset_profile(facts, roots=ExplicitRoots(frozenset()))
    assert result.scope.narrowed and result.scope.roots_used == ()
    assert result.verdict is Verdict.INCOMPLETE


# ---- determinism, end to end ----------------------------------------------------------------


def test_permuted_document_order_is_identical() -> None:
    results = [
        evaluate_subset_profile(extract_subset_facts(load(*order)))
        for order in itertools.permutations(MULTI_DOC)
    ]
    assert len(MULTI_DOC) == 3 and len(results) == 6
    assert all(r == results[0] for r in results[1:])
    first = results[0]
    assert {f.rule_id for f in first.findings} >= {
        "binding-source",
        "part-multiplicity",
        "invocation-callable",
        "string-value-omission",
    }
    keys = [f.sort_key() for f in first.findings]
    assert keys == sorted(keys)


def test_evaluating_twice_is_identical() -> None:
    model = load(*MULTI_DOC)
    assert evaluate_subset_profile(extract_subset_facts(model)) == evaluate_subset_profile(
        extract_subset_facts(model)
    )

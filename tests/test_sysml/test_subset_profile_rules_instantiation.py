"""The instantiation-dependent rules on their own probe models, and roots and order end to end.

Plan Phase 7. Each record probe of `binding-source`, `part-multiplicity` and
`constraint-predicate`, including every B5 variation probe, is reproduced by the evaluator at
its construct with its probed context and the recorded outcome. Each control (the prototype's
admitted neighbors) draws no finding of its rule and no refusal. Then roots: the default is the
generator's, a widened set reports `beyond_generator_roots` (never refused), a narrowed set is
incomplete. Then determinism over a model split across documents, loaded in every order.
"""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any

import pytest

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
from tests.helpers.subset_probe_judge import Probe, ProbeKind, load_probe

FIXTURES = Path(__file__).parents[1] / "fixtures" / "subset_profile"
PROBES_DIR = FIXTURES / "probes"
CASES = FIXTURES / "cases"
RULES = {"binding-source", "part-multiplicity", "constraint-predicate"}
ALL = [load_probe(d) for d in sorted(PROBES_DIR.iterdir()) if d.is_dir()]
MULTI_DOC = sorted((CASES / "multi_doc").glob("*.sysml"))


def load(*paths: Path) -> Any:
    model, diagnostics = SysideAdapter.load_model(list(paths))
    assert not diagnostics.contains_errors(), [str(d) for d in diagnostics.all]
    return model


def evaluate(probe: Probe) -> SubsetProfileResult:
    return evaluate_subset_profile(
        extract_subset_facts(load(PROBES_DIR / probe.id / "model.sysml"))
    )


def at_construct(result: SubsetProfileResult, probe: Probe) -> list[SubsetFinding]:
    first, last = probe.construct.first_line, probe.construct.last_line
    return [
        f
        for f in result.findings
        if f.rule_id == probe.rule
        and f.location.line is not None
        and first <= f.location.line <= last
    ]


def of_kind(kind: ProbeKind) -> list[Probe]:
    return [p for p in ALL if p.kind is kind and p.rule in RULES]


@pytest.mark.parametrize("probe", of_kind(ProbeKind.RECORD), ids=lambda p: p.id)
def test_evaluator_reproduces_probe(probe: Probe) -> None:
    (finding,) = at_construct(evaluate(probe), probe)
    assert (finding.shape_id, finding.context_id) == (probe.shape, ContextId(probe.context))
    recorded = PACKAGED_RULES.rule(probe.rule).shape(probe.shape).admissions[finding.context_id]
    assert finding.outcome is recorded.outcome
    assert finding.outcome.value == probe.expected_outcome


@pytest.mark.parametrize("probe", of_kind(ProbeKind.CONTROL), ids=lambda p: p.id)
def test_admitted_neighbor_draws_no_finding_of_its_rule(probe: Probe) -> None:
    result = evaluate(probe)
    assert at_construct(result, probe) == []
    assert [f for f in result.findings if f.outcome is Outcome.REFUSED] == []


#: Appendix C's variation probes (B5): for each instantiation-dependent refused pair, the reach
#: paths the context label claims to cover. Each named variant must be a certified record probe.
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
    for pair, variants in REACH_VARIANTS.items():
        present = {p.variant for p in ALL if (p.rule, p.shape, p.context) == pair}
        assert variants <= present, (pair, variants - present)


def test_non_numerical_predicate_is_excluded_with_its_profile_reasons() -> None:
    probe = next(
        p
        for p in ALL
        if p.id == "constraint-predicate__non_numerical_predicate__owner_instantiated"
    )
    (finding,) = at_construct(evaluate(probe), probe)
    assert finding.outcome is Outcome.EXCLUDED
    assert finding.detail_reasons == ("warn_non_numerical_predicate",)


def test_an_overridden_writers_binding_is_counted_by_the_scopes_it_loses() -> None:
    probe = next(p for p in ALL if p.id == "binding-source__expression_source__writer_overridden")
    (finding,) = at_construct(evaluate(probe), probe)
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
    probe = next(p for p in ALL if p.id == "binding-source__expression_source__owner_instantiated")
    facts = extract_subset_facts(load(PROBES_DIR / probe.id / "model.sysml"))
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

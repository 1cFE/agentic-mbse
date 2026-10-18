"""The model-wide rules on their own probe models (plan Phase 6).

Each record probe of `calc-owned-assertion`, `indexed-reference`, `invocation-callable`,
`conditional-expression` and `string-value-omission` is reproduced by the evaluator at its
construct with its probed context and the recorded outcome. Each control model (the prototype's
admitted neighbors: part-owned assert, explicit multiply, arithmetic min, numeric value) draws
no finding of its rule and no refusal at all. A candidate reproduction is not a rule, so no
rule refuses it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_profile import (
    PACKAGED_RULES,
    ContextId,
    Outcome,
    SubsetFinding,
    SubsetProfileResult,
    evaluate_subset_profile,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from tests.helpers.subset_probe_judge import Probe, ProbeKind, load_probe

PROBES_DIR = Path(__file__).parents[1] / "fixtures" / "subset_profile" / "probes"
RULES = {
    "calc-owned-assertion",
    "indexed-reference",
    "invocation-callable",
    "conditional-expression",
    "string-value-omission",
}
ALL = [load_probe(d) for d in sorted(PROBES_DIR.iterdir()) if d.is_dir()]


def of_kind(kind: ProbeKind, rules: set[str] | None = None) -> list[Probe]:
    return [p for p in ALL if p.kind is kind and (rules is None or p.rule in rules)]


def evaluate(probe: Probe) -> SubsetProfileResult:
    model, diagnostics = SysideAdapter.load_model([PROBES_DIR / probe.id / probe.construct.file])
    assert not diagnostics.contains_errors(), [str(d) for d in diagnostics.all]
    return evaluate_subset_profile(extract_subset_facts(model))


def only(result: SubsetProfileResult, probe: Probe) -> SubsetFinding:
    first, last = probe.construct.first_line, probe.construct.last_line
    found = [
        f
        for f in result.findings
        if (f.rule_id, f.shape_id) == (probe.rule, probe.shape)
        and f.location.line is not None
        and first <= f.location.line <= last
    ]
    assert len(found) == 1, found
    return found[0]


@pytest.mark.parametrize("probe", of_kind(ProbeKind.RECORD, RULES), ids=lambda p: p.id)
def test_evaluator_reproduces_probe(probe: Probe) -> None:
    finding = only(evaluate(probe), probe)
    recorded = PACKAGED_RULES.rule(probe.rule).shape(probe.shape).admissions
    assert finding.context_id is ContextId(probe.context)
    assert finding.outcome is recorded[finding.context_id].outcome
    assert finding.outcome.value == probe.expected_outcome


@pytest.mark.parametrize("probe", of_kind(ProbeKind.CONTROL, RULES), ids=lambda p: p.id)
def test_admitted_neighbor_draws_no_finding_of_its_rule(probe: Probe) -> None:
    result = evaluate(probe)
    assert [f for f in result.findings if f.rule_id == probe.rule] == []
    assert [f for f in result.findings if f.outcome is Outcome.REFUSED] == []


@pytest.mark.parametrize("probe", of_kind(ProbeKind.REPRODUCTION), ids=lambda p: p.id)
def test_candidate_reproductions_are_not_refused_by_any_rule(probe: Probe) -> None:
    """ES-002, ES-008, ES-009, the ES-010 refusal side and a bare calc-def result are R3 items."""
    result = evaluate(probe)
    assert [f for f in result.findings if f.outcome is Outcome.REFUSED] == []


def test_a_calc_usage_owned_constraint_is_reported_on_the_constraint_not_its_owner() -> None:
    probe = next(
        p for p in ALL if p.id == "calc-owned-assertion__asserted_constraint__calc_usage_owner"
    )
    finding = only(evaluate(probe), probe)
    assert finding.subject.qualified_name == "fx::Site::path::f1"
    assert finding.location.line == 11  # the generator locates the refusal at the owner, line 8


def test_both_string_spellings_are_omitted() -> None:
    spellings = [p for p in of_kind(ProbeKind.RECORD, {"string-value-omission"})]
    assert {p.variant for p in spellings} == {"attribute_declaration", "redefinition_shorthand"}
    for probe in spellings:
        assert only(evaluate(probe), probe).outcome is Outcome.OMITTED

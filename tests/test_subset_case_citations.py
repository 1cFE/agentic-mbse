"""Every case a record cites is packaged and its stored screen answer shows the cited pair.

Item 2a design D4 splits ADR 0001 invariant 1 by what each repository can see. The loader
checks a citation's form only. This module checks the rest that agentic-mbse can see: the
cited case is packaged, it is a `record` case, and its stored screen answer has the cited
(rule, shape, context, outcome) on the case's construct. A case cited for an `unobservable`
pair shows no decided outcome for it. Every `record` case is cited, a `control` case draws no
finding of its rule, and a case cited for a run the generator completes draws no refusal.
What the generator does on each case is sysml-codegen's check.

The first part is pure: it reads the records and the stored answers. The SysIDE part runs the
screen with one shape's evidence stripped.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from agentic_mbse.sysml.conformance_case import CaseKind, PackagedCase, ScreenFinding
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_profile import (
    PACKAGED_RULES,
    CaseRef,
    ContextId,
    Outcome,
    evaluate_subset_profile,
    load_rule_records,
    rule_ids,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from tests.helpers.subset_cases import ALL_CASES, rule_of
from tests.helpers.subset_records import data_with, dump_records

CASES = {c.case_id: c for c in ALL_CASES}


@dataclass(frozen=True)
class Citation:
    rule: str
    shape: str
    context: ContextId
    outcome: Outcome
    case_id: str

    def __str__(self) -> str:
        return self.case_id


def citations() -> Iterator[Citation]:
    for rule in PACKAGED_RULES.rules:
        for shape in rule.shapes:
            for context, admission in shape.admissions.items():
                for ref in admission.evidence:
                    if isinstance(ref, CaseRef):
                        yield Citation(
                            rule.rule_id, shape.shape_id, context, admission.outcome, ref.case_id
                        )


CITATIONS = sorted(citations(), key=lambda c: (c.case_id, c.rule, c.shape, c.context.value))


@dataclass(frozen=True)
class UnobservableCitation:
    rule: str
    shape: str
    context: ContextId
    case_id: str

    def __str__(self) -> str:
        return self.case_id


UNOBSERVABLE = sorted(
    (
        UnobservableCitation(rule.rule_id, shape.shape_id, context, ref.case_id)
        for rule in PACKAGED_RULES.rules
        for shape in rule.shapes
        for context, entry in shape.unobservable.items()
        for ref in entry.evidence
    ),
    key=lambda c: c.case_id,
)


def on_construct(case: PackagedCase, rule: str) -> list[ScreenFinding]:
    return [
        f
        for f in case.screen.findings
        if f.rule == rule and f.line is not None and case.construct.contains(f.line)
    ]


def refused(case: PackagedCase) -> list[ScreenFinding]:
    return [f for f in case.screen.findings if f.outcome is Outcome.REFUSED]


def test_every_case_belongs_to_a_rule_or_reproduces_a_family() -> None:
    for case in ALL_CASES:
        rule = rule_of(case)
        if rule is None:
            assert case.case_id.startswith("candidate-"), case.case_id
        else:
            assert rule in rule_ids(), case.case_id


@pytest.mark.parametrize("citation", CITATIONS, ids=str)
def test_cited_case_is_packaged_and_shows_its_pair(citation: Citation) -> None:
    case = CASES.get(citation.case_id)
    assert case is not None, f"records cite {citation.case_id}, which is not packaged"
    assert case.kind is CaseKind.RECORD
    shown = [
        (f.context, f.outcome)
        for f in on_construct(case, citation.rule)
        if f.shape == citation.shape
    ]
    assert shown == [(citation.context, citation.outcome)]


@pytest.mark.parametrize(
    "citation", [c for c in CITATIONS if c.outcome is not Outcome.REFUSED], ids=str
)
def test_a_case_cited_for_a_run_the_generator_completes_draws_no_refusal(
    citation: Citation,
) -> None:
    assert refused(CASES[citation.case_id]) == []


@pytest.mark.parametrize("citation", UNOBSERVABLE, ids=str)
def test_an_unobservable_pairs_case_is_packaged_and_shows_no_outcome_for_it(
    citation: UnobservableCitation,
) -> None:
    """The case shows what happens instead; the pair itself stays unconfirmed or unrecognized."""
    case = CASES.get(citation.case_id)
    assert case is not None, f"records cite {citation.case_id}, which is not packaged"
    assert case.kind is CaseKind.RECORD
    shown = [
        (f.context, f.outcome)
        for f in on_construct(case, citation.rule)
        if f.shape == citation.shape
    ]
    assert shown in ([], [(citation.context, Outcome.UNCONFIRMED)])


def test_every_record_case_is_cited() -> None:
    cited = {c.case_id for c in CITATIONS} | {c.case_id for c in UNOBSERVABLE}
    uncited = [c.case_id for c in ALL_CASES if c.kind is CaseKind.RECORD and c.case_id not in cited]
    assert uncited == []


@pytest.mark.parametrize(
    "case", [c for c in ALL_CASES if c.kind is CaseKind.CONTROL], ids=lambda c: c.case_id
)
def test_a_control_draws_no_finding_of_its_rule_and_no_refusal(case: PackagedCase) -> None:
    rule = rule_of(case)
    assert rule is not None
    assert on_construct(case, rule) == []
    assert refused(case) == []


@pytest.mark.parametrize(
    "case", [c for c in ALL_CASES if c.kind is CaseKind.REPRODUCTION], ids=lambda c: c.case_id
)
def test_a_reproduction_is_refused_by_no_rule(case: PackagedCase) -> None:
    """ES-002, ES-008, ES-009, the ES-010 refusal side, a bare calc-def result, a constraint
    under an item def owner and an anonymous assertion by reference have no rule."""
    assert refused(case) == []


def test_each_rule_example_is_a_cited_case_the_generator_runs() -> None:
    cited_ok = {c.case_id for c in CITATIONS if c.outcome is not Outcome.REFUSED}
    for rule in PACKAGED_RULES.rules:
        if rule.example_case is None:
            continue
        assert rule.example_case in cited_ok, rule.rule_id
        assert rule_of(CASES[rule.example_case]) == rule.rule_id


# ---- the SysIDE half: without its evidence the shape is unconfirmed ---------------------------


@pytest.mark.parametrize("citation", CITATIONS, ids=str)
def test_stripping_the_shapes_evidence_makes_it_unconfirmed(citation: Citation) -> None:
    """Without its admissions (and so without any SA-1 statement) the shape is unconfirmed."""
    pair = (citation.rule, citation.shape)
    pairs = {
        (r.rule_id, s.shape_id): {c.value: a.outcome.value for c, a in s.admissions.items()}
        for r in PACKAGED_RULES.rules
        for s in r.shapes
        if s.admissions and (r.rule_id, s.shape_id) != pair
    }
    data = data_with(pairs)
    for rule in data["rule"]:  # data_with drops SA-1 statements; restore the other shapes'
        for shape in rule["shape"]:
            original = PACKAGED_RULES.rule(rule["id"]).shape(shape["id"]).no_admitted_context
            if original is not None and (rule["id"], shape["id"]) != pair:
                shape["no_admitted_context"] = {
                    "citation": original.citation,
                    "statement": original.statement,
                }
    stripped = load_rule_records(dump_records(data))
    case = CASES[citation.case_id]
    model, _ = SysideAdapter.load_model(list(case.model_files()))
    result = evaluate_subset_profile(extract_subset_facts(model), stripped)
    found = [
        f.outcome
        for f in result.findings
        if (f.rule_id, f.shape_id) == pair
        and f.location.line is not None
        and case.construct.contains(f.location.line)
    ]
    assert found == [Outcome.UNCONFIRMED]

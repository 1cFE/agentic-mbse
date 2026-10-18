"""The record loader: every field present, closed vocabularies, and no outcome without evidence.

Pure. Records are built from the packaged data (`tests/helpers/subset_records.py`) and
mutated, so each test shows one loader rule biting.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

from agentic_mbse.sysml.subset_profile import (
    ALWAYS_UNCONFIRMED_CONTEXTS,
    PACKAGED_RULES,
    SNAPSHOT_FIXTURES,
    SUBSET_REASON_CODES,
    CaseRef,
    CorpusRef,
    EvidenceStatus,
    Outcome,
    RecordError,
    load_rule_records,
    rule_contexts,
    rule_ids,
    rule_shapes,
)
from tests.helpers.subset_records import data_with, dump_records, packaged_data

BINDING = ("binding-source", "expression_source")
REFUSED_WITH_PARTNER = {
    BINDING: {"owner_instantiated": "refused", "owner_uninstantiated": "admitted"}
}


def rule(data: dict[str, Any], rule_id: str) -> dict[str, Any]:
    return next(r for r in data["rule"] if r["id"] == rule_id)


def shape(data: dict[str, Any], rule_id: str, shape_id: str) -> dict[str, Any]:
    return next(s for s in rule(data, rule_id)["shape"] if s["id"] == shape_id)


def load(data: dict[str, Any]) -> Any:
    return load_rule_records(dump_records(data))


# ---- the packaged records -------------------------------------------------------------------


def test_packaged_records_load_and_hold_every_implemented_rule_and_shape() -> None:
    assert tuple(r.rule_id for r in PACKAGED_RULES.rules) == rule_ids()
    for record in PACKAGED_RULES.rules:
        assert {s.shape_id for s in record.shapes} == rule_shapes(record.rule_id)


def test_records_are_complete() -> None:
    """Spec "Records are complete": every field the epic names, on every rule."""
    for record in PACKAGED_RULES.rules:
        assert record.rule_id and record.title and record.matrix_rows
        assert record.fact_requirements
        assert record.remedy and record.semantic_limits and record.doc_anchor
        assert isinstance(record.evidence_status, EvidenceStatus)
        if record.evidence_status is not EvidenceStatus.CODE_READ_PENDING_ITEM_2:
            assert record.example_case and record.example_case.startswith(record.rule_id)
        for s in record.shapes:
            assert s.reason in SUBSET_REASON_CODES
            # refused and admitted contexts are the two explicit lists (spec L3-1)
            refused, admitted = s.contexts_with(Outcome.REFUSED), s.contexts_with(Outcome.ADMITTED)
            assert set(refused).isdisjoint(admitted)
            assert set(s.admissions) <= rule_contexts(record.rule_id) - ALWAYS_UNCONFIRMED_CONTEXTS


def test_packaged_records_round_trip_through_the_test_writer() -> None:
    assert load(packaged_data()) == PACKAGED_RULES


# ---- evidence (design D3, invariants 1 and 3) -----------------------------------------------


def test_a_refused_pair_with_its_admitted_partner_loads() -> None:
    records = load(data_with(REFUSED_WITH_PARTNER))
    admission = records.rule("binding-source").shape("expression_source").admissions
    assert {c.value: a.outcome for c, a in admission.items()} == {
        "owner_instantiated": Outcome.REFUSED,
        "owner_uninstantiated": Outcome.ADMITTED,
    }


@pytest.mark.parametrize("outcome", ["refused", "admitted", "excluded", "omitted"])
def test_loader_rejects_an_outcome_without_evidence(outcome: str) -> None:
    data = data_with({BINDING: {"owner_instantiated": outcome, "owner_uninstantiated": "admitted"}})
    shape(data, *BINDING)["admission"][0]["evidence"] = []
    with pytest.raises(RecordError, match="requires evidence"):
        load(data)


@pytest.mark.parametrize("outcome", ["refused", "excluded", "omitted"])
def test_loader_rejects_a_corpus_citation_for_anything_but_admitted(outcome: str) -> None:
    data = data_with({BINDING: {"owner_instantiated": outcome, "owner_uninstantiated": "admitted"}})
    shape(data, *BINDING)["admission"][0]["evidence"] = ["corpus:sample_model"]
    with pytest.raises(RecordError, match="requires case evidence only"):
        load(data)


def test_an_admission_may_cite_a_snapshot_fixture_and_nothing_else_from_the_corpus() -> None:
    data = data_with({BINDING: {"owner_uninstantiated": "admitted"}})
    shape(data, *BINDING)["admission"][0]["evidence"] = ["corpus:sample_model"]
    # a corpus citation is not a case observation, so the rule stays pending
    rule(data, "binding-source")["evidence_status"] = "code_read_pending_item_2"
    del rule(data, "binding-source")["example_case"]
    admission = load(data).rule("binding-source").shape("expression_source").admissions
    assert [a.evidence for a in admission.values()] == [(CorpusRef("sample_model"),)]
    assert "sample_model" in SNAPSHOT_FIXTURES
    shape(data, *BINDING)["admission"][0]["evidence"] = ["corpus:invocation_binding_probe"]
    with pytest.raises(RecordError, match="not a snapshot fixture"):
        load(data)


def test_loader_rejects_a_case_of_another_pair() -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    shape(data, *BINDING)["admission"][0]["evidence"] = [
        "case:binding-source__expression_source__owner_package"
    ]
    with pytest.raises(RecordError, match="is not a case of"):
        load(data)
    shape(data, *BINDING)["admission"][0]["evidence"] = [
        "case:binding-source__expression_source__owner_uninstantiated__variant"
    ]
    with pytest.raises(RecordError, match="is not a case of"):
        load(data)


def test_loader_rejects_a_probe_citation() -> None:
    """Item 2a retired the probes: a case replaces each one as evidence (design D4)."""
    data = data_with(REFUSED_WITH_PARTNER)
    shape(data, *BINDING)["admission"][0]["evidence"] = [
        "probe:binding-source__expression_source__owner_instantiated"
    ]
    with pytest.raises(RecordError, match="neither case:<id> nor corpus:<fixture>"):
        load(data)


def test_a_case_variant_of_the_same_pair_is_evidence() -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    entry = shape(data, *BINDING)["admission"][0]
    assert entry["context"] == "owner_instantiated"
    entry["evidence"] = ["case:binding-source__expression_source__owner_instantiated__part_usage"]
    admissions = load(data).rule("binding-source").shape("expression_source").admissions
    assert CaseRef("binding-source__expression_source__owner_instantiated__part_usage") in [
        e for a in admissions.values() for e in a.evidence
    ]


def test_a_refused_shape_needs_a_case_of_a_context_it_is_not_refused_in() -> None:
    data = data_with({BINDING: {"owner_instantiated": "refused"}})
    with pytest.raises(RecordError, match="context it is not refused in"):
        load(data)
    data = data_with({BINDING: {"owner_instantiated": "refused", "owner_package": "refused"}})
    with pytest.raises(RecordError, match="context it is not refused in"):
        load(data)


@pytest.mark.parametrize("partner", ["admitted", "omitted", "excluded"])
def test_a_certified_omission_or_exclusion_meets_the_gate_like_an_admission(
    partner: str,
) -> None:
    """Audit S1: the gate proves a refusal is not a universal ban; any non-refused case does."""
    data = data_with({BINDING: {"owner_instantiated": "refused", "owner_uninstantiated": partner}})
    admissions = load(data).rule("binding-source").shape("expression_source").admissions
    assert {a.outcome for a in admissions.values()} == {Outcome.REFUSED, Outcome(partner)}


def test_sa1_statement_needs_refused_cases_in_every_computable_context() -> None:
    pair = ("calc-owned-assertion", "asserted_constraint")
    statement = {"citation": "elaboration/elaborate.py:1625", "statement": "refused everywhere"}
    data = data_with({pair: {"calc_definition_owner": "refused", "calc_usage_owner": "refused"}})
    shape(data, *pair)["no_admitted_context"] = statement
    assert load(data).rule(pair[0]).shape(pair[1]).no_admitted_context is not None
    data = data_with({pair: {"calc_definition_owner": "refused"}})
    shape(data, *pair)["no_admitted_context"] = statement
    with pytest.raises(RecordError, match="missing \\['calc_usage_owner'\\]"):
        load(data)


def test_sa1_statement_cannot_stand_beside_an_admitted_case() -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    shape(data, *BINDING)["no_admitted_context"] = {"citation": "c", "statement": "s"}
    with pytest.raises(RecordError, match="contradicts"):
        load(data)


def test_a_refused_shape_needs_its_expected_code() -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    del shape(data, *BINDING)["expected_code"]
    with pytest.raises(RecordError, match="expected_code"):
        load(data)


@pytest.mark.parametrize("context", ["beyond_generator_roots", "beneath_refused_multiplicity"])
def test_always_unconfirmed_contexts_take_no_admission(context: str) -> None:
    data = data_with({BINDING: {context: "admitted"}})
    with pytest.raises(RecordError, match="always reports unconfirmed"):
        load(data)


def test_unconfirmed_is_never_listed() -> None:
    data = data_with({BINDING: {"owner_uninstantiated": "unconfirmed"}})
    with pytest.raises(RecordError, match="absence of an admission"):
        load(data)


def test_a_context_the_rule_cannot_compute_is_rejected() -> None:
    data = data_with({BINDING: {"attribute_value": "admitted"}})
    with pytest.raises(RecordError, match="cannot compute context"):
        load(data)


def test_only_an_admission_carries_a_qualification() -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    assert shape(data, *BINDING)["admission"][0]["outcome"] == "refused"
    shape(data, *BINDING)["admission"][0]["qualification"] = "manual_stub"
    with pytest.raises(RecordError, match="qualification"):
        load(data)


# ---- schema and closed vocabularies ---------------------------------------------------------


def test_evidence_status_must_match_the_admissions() -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    rule(data, "binding-source")["evidence_status"] = "case_observed"
    with pytest.raises(RecordError, match="disagrees with its admissions"):
        load(data)


def test_example_case_exists_exactly_when_evidence_does() -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    del rule(data, "binding-source")["example_case"]
    with pytest.raises(RecordError, match="example_case"):
        load(data)
    data = data_with({})
    rule(data, "binding-source")["example_case"] = "binding-source__x__y"
    with pytest.raises(RecordError, match="no working example"):
        load(data)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: rule(d, "binding-source").update(colour="red"), "unknown keys \\['colour'\\]"),
        (lambda d: rule(d, "binding-source").pop("remedy"), "missing keys \\['remedy'\\]"),
        (lambda d: rule(d, "binding-source").update(remedy=" "), "non-empty text"),
        (
            lambda d: rule(d, "binding-source").update(fact_requirements=["binding_source"]),
            "differ",
        ),
        (lambda d: rule(d, "binding-source").update(fact_requirements=["moon"]), "not a FactKind"),
        (
            lambda d: shape(d, *BINDING).update(reason="SI_EXPRESSION_SOURCE_UNSUPPORTED"),
            "SUBSET_REASON_CODES",
        ),
        (
            lambda d: shape(d, *BINDING).update(expected_code="binding_source_expression"),
            "not a generator code",
        ),
        (lambda d: rule(d, "binding-source")["shape"].pop(), "must be exactly"),
        (lambda d: d["rule"].pop(), "exactly the rules"),
        (lambda d: d["rule"].append(copy.deepcopy(d["rule"][0])), "exactly the rules"),
        (lambda d: rule(d, "binding-source").update(id="binding-sauce"), "no rule function"),
        (lambda d: d["verified_against"].update(agentic_rev="HEAD"), "full revision"),
        (lambda d: d.update(schema=2), "unknown schema"),
        (lambda d: rule(d, "binding-source").update(generator_evidence=[]), "generator_evidence"),
    ],
)
def test_schema_violations_are_loud(mutate: Any, message: str) -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    mutate(data)
    with pytest.raises(RecordError, match=message):
        load(data)


def test_unknown_outcome_and_context_are_rejected() -> None:
    data = data_with(REFUSED_WITH_PARTNER)
    shape(data, *BINDING)["admission"][0]["outcome"] = "maybe"
    with pytest.raises(RecordError, match="not a Outcome"):
        load(data)
    data = data_with(REFUSED_WITH_PARTNER)
    shape(data, *BINDING)["admission"][0]["context"] = "somewhere"
    with pytest.raises(RecordError, match="not a ContextId"):
        load(data)

"""Every probe the records cite certifies, and the evaluator reproduces it on the probe's model.

The pure half re-judges every stored observation with the one judge (plan P-2) and joins the
probes to the packaged records: a cited probe must exist, be a `record` probe of the same
(rule, shape, context), expect the recorded outcome, certify at the records' pinned identity,
and every certified record probe must be cited. The SysIDE half runs extraction and the
evaluator on each probe's own model.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_profile import (
    PACKAGED_RULES,
    Outcome,
    ProbeRef,
    SubsetFinding,
    SubsetProfileResult,
    evaluate_subset_profile,
    load_rule_records,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from tests.helpers.subset_probe_judge import (
    Probe,
    ProbeKind,
    Refused,
    judge,
    load_observation,
    load_probe,
)
from tests.helpers.subset_records import data_with, dump_records

PROBES_DIR = Path(__file__).parent / "fixtures" / "subset_profile" / "probes"
PROBES = {d.name: load_probe(d) for d in sorted(PROBES_DIR.iterdir()) if d.is_dir()}
SUCCESS_OUTCOMES = {"admitted", "omitted", "excluded"}


Cited = tuple[str, str, str, Outcome, str]


def cited() -> Iterator[Cited]:
    """(rule, shape, context, outcome, probe id) for every probe a record cites."""
    for rule in PACKAGED_RULES.rules:
        for shape in rule.shapes:
            for context, admission in shape.admissions.items():
                for evidence in admission.evidence:
                    if isinstance(evidence, ProbeRef):
                        yield (
                            rule.rule_id,
                            shape.shape_id,
                            context.value,
                            admission.outcome,
                            evidence.probe_id,
                        )


CITED = sorted(cited())
CITED_IDS = {c[-1] for c in CITED}


@pytest.mark.parametrize("probe_id", sorted(PROBES))
def test_stored_observation_re_judges_as_recorded(probe_id: str) -> None:
    probe = PROBES[probe_id]
    obs, recorded = load_observation(PROBES_DIR / probe_id / "observation.json")
    assert judge(probe, obs) == recorded


@pytest.mark.parametrize("entry", CITED, ids=lambda c: c[-1])
def test_cited_probe_certifies_its_own_pair_at_the_pinned_identity(entry: Cited) -> None:
    rule_id, shape_id, context, outcome, probe_id = entry
    probe = PROBES.get(probe_id)
    assert probe is not None, f"records cite {probe_id}, which does not exist"
    assert probe.kind is ProbeKind.RECORD
    assert (probe.rule, probe.shape, probe.context) == (rule_id, shape_id, context)
    assert probe.expected_outcome == outcome.value
    obs, certification = load_observation(PROBES_DIR / probe_id / "observation.json")
    assert certification.certifies, certification.failed_check
    assert judge(probe, obs).certifies
    pinned = PACKAGED_RULES.verified_against
    assert (obs.identity.codegen_rev, obs.identity.syside_version) == (
        pinned.codegen_rev,
        pinned.syside_version,
    )
    assert obs.identity.agentic_rev == pinned.agentic_rev
    if isinstance(probe.expect, Refused):
        shape = PACKAGED_RULES.rule(rule_id).shape(shape_id)
        assert probe.expect.code == shape.expected_code


#: Certified refused probes whose shape has no admitted-context probe yet, so the loader cannot
#: take them (invariant 3). Named one by one; Phases 6-7 land each with its partner and empty it.
AWAITING_ADMITTED_PARTNER: set[str] = set()


def test_every_certified_record_probe_is_cited() -> None:
    assert AWAITING_ADMITTED_PARTNER.isdisjoint(CITED_IDS)
    uncited = []
    for probe_id, probe in PROBES.items():
        _obs, certification = load_observation(PROBES_DIR / probe_id / "observation.json")
        if (
            probe.kind is ProbeKind.RECORD
            and certification.certifies
            and probe_id not in CITED_IDS | AWAITING_ADMITTED_PARTNER
        ):
            uncited.append(probe_id)
    assert uncited == []


def test_example_probes_are_certified_runs_the_generator_completes() -> None:
    for rule in PACKAGED_RULES.rules:
        if rule.example_probe is None:
            continue
        probe = PROBES[rule.example_probe]
        assert probe.rule == rule.rule_id and probe.expected_outcome in SUCCESS_OUTCOMES
        _obs, certification = load_observation(PROBES_DIR / rule.example_probe / "observation.json")
        assert certification.certifies


def test_control_probes_certify() -> None:
    for probe_id, probe in PROBES.items():
        if probe.kind is ProbeKind.CONTROL:
            _obs, certification = load_observation(PROBES_DIR / probe_id / "observation.json")
            assert certification.certifies, (probe_id, certification.failed_check)


# ---- the SysIDE half: the evaluator reproduces each probe on its own model -------------------


def evaluate_probe(probe: Probe) -> SubsetProfileResult:
    model, diagnostics = SysideAdapter.load_model([PROBES_DIR / probe.id / probe.construct.file])
    assert not diagnostics.contains_errors(), [str(d) for d in diagnostics.all]
    return evaluate_subset_profile(extract_subset_facts(model))


def at_construct(result: SubsetProfileResult, probe: Probe) -> list[SubsetFinding]:
    first, last = probe.construct.first_line, probe.construct.last_line
    return [
        f
        for f in result.findings
        if f.rule_id == probe.rule
        and f.location.line is not None
        and first <= f.location.line <= last
    ]


@pytest.mark.parametrize("entry", CITED, ids=lambda c: c[-1])
def test_evaluator_reproduces_each_cited_probe(entry: Cited) -> None:
    rule_id, shape_id, context, outcome, probe_id = entry
    probe = PROBES[probe_id]
    result = evaluate_probe(probe)
    found = [f for f in at_construct(result, probe) if f.shape_id == shape_id]
    assert [(f.context_id.value, f.outcome) for f in found] == [(context, outcome)]
    if outcome is not Outcome.REFUSED:
        refused = [f for f in result.findings if f.outcome is Outcome.REFUSED]
        assert refused == [], "the generator ran this model, so nothing in it may be refused"


@pytest.mark.parametrize(
    "probe_id", sorted(p for p, probe in PROBES.items() if probe.kind is ProbeKind.CONTROL)
)
def test_control_probe_models_draw_no_finding_of_their_rule_and_no_refusal(probe_id: str) -> None:
    probe = PROBES[probe_id]
    result = evaluate_probe(probe)
    assert at_construct(result, probe) == []
    assert [f for f in result.findings if f.outcome is Outcome.REFUSED] == []


@pytest.mark.parametrize("entry", CITED, ids=lambda c: c[-1])
def test_stripping_the_shapes_evidence_makes_it_unconfirmed(entry: Cited) -> None:
    """Without its admissions (and so without any SA-1 statement) the shape is unconfirmed."""
    rule_id, shape_id, _context, _outcome, probe_id = entry
    pairs = {
        (r.rule_id, s.shape_id): {c.value: a.outcome.value for c, a in s.admissions.items()}
        for r in PACKAGED_RULES.rules
        for s in r.shapes
        if s.admissions and (r.rule_id, s.shape_id) != (rule_id, shape_id)
    }
    data = data_with(pairs)
    for rule in data["rule"]:  # data_with drops SA-1 statements; restore the other shapes'
        for shape in rule["shape"]:
            original = PACKAGED_RULES.rule(rule["id"]).shape(shape["id"]).no_admitted_context
            if original is not None and (rule["id"], shape["id"]) != (rule_id, shape_id):
                shape["no_admitted_context"] = {
                    "citation": original.citation,
                    "statement": original.statement,
                }
    stripped = load_rule_records(dump_records(data))
    probe = PROBES[probe_id]
    model, _ = SysideAdapter.load_model([PROBES_DIR / probe.id / probe.construct.file])
    result = evaluate_subset_profile(extract_subset_facts(model), stripped)
    found = [f for f in at_construct(result, probe) if f.shape_id == shape_id]
    assert [f.outcome for f in found] == [Outcome.UNCONFIRMED]

"""The capability/refusal matrix places every named case, classifies and owns it, and joins the records.

Pure: reads `tests/fixtures/subset_profile/` and the packaged rule records only, so it keeps
passing after the item folder under `.project/` is archived.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_mbse.sysml.subset_profile import PACKAGED_RULES, Outcome, ProbeRef
from tests.helpers.subset_matrix import (
    BINDING_KINDS,
    MATRIX_PATH,
    Matrix,
    MatrixError,
    RowClass,
    RowEvidence,
    RowOutcome,
    load_matrix,
)
from tests.helpers.subset_probe_judge import ProbeKind, judge, load_observation, load_probe

PROBES_DIR = Path(__file__).parent / "fixtures" / "subset_profile" / "probes"

PUSH_DOWN_ROWS = {
    "PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS",
    "PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE",
    "PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR",
    "PUSH-DOWN-HIER-PROFILE-REDEF-PRECEDENCE",
    "PUSH-DOWN-HIER-PROFILE-UNSUPPORTED-RHS",
    "PUSH-DOWN-HIER-PROFILE-MULTIPLICITY-SHAPE",
    "PUSH-DOWN-HIER-PROFILE-AMBIG-INHERITED-ATTR",
    "PUSH-DOWN-AGG-PROFILE-SUM-SHAPE",
    "PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE",
    "PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE",
}
FIXED = (
    {f"ES-{n:03d}" for n in range(1, 13)}
    | {
        "SELF-BINDING",
        "INDEXED-REFERENCE",
        "DEEP-QUALIFIED-WIRING",
        "L6-LIBRARY-ALIAS-SOURCE",
        "G1",
        "G2",
    }
    | PUSH_DOWN_ROWS
)

# The spec's mapping (§ Capability/refusal matrix): each dc3 item maps to exactly these rows.
# U1 = B1, U3 = B7, U4 = B4 + B5 + B6 plus min/max, U7 = B9; U2, U5, U6 have no B number.
DC3_MAPPING = {
    "B1": {"ES-001"},
    "B2": {"ES-003"},  # not ES-004: T-001's multiplicity attribution is wrong
    "B3": {"ES-004"},
    "B4": {"ES-005"},
    "B5": {"ES-005"},
    "B6": {"ES-006"},
    "B7": {"ES-010"},
    "B8": {"ES-007"},
    "B9": {"ES-011"},
}
UPSTREAM_MAPPING = {
    "U1": {"ES-001"},
    "U2": {"ES-008"},
    "U3": {"ES-010"},
    "U4": {"ES-005", "ES-006"},
    "U5": {"ES-002"},
    "U6": {"ES-009"},
    "U7": {"ES-011"},
}

# Which probe kind a non-rule row's evidence status requires.
STATUS_PROBE_KIND = {
    RowEvidence.REPRODUCTION_PROBE: ProbeKind.REPRODUCTION,
    RowEvidence.CONTROL_PROBE: ProbeKind.CONTROL,
    RowEvidence.OBSERVED_IN_RECORD_PROBES: ProbeKind.RECORD,
}

MATRIX = load_matrix()


def _cited_probes(rule_id: str) -> set[str]:
    rule = PACKAGED_RULES.rule(rule_id)
    return {
        ref.probe_id
        for shape in rule.shapes
        for admission in shape.admissions.values()
        for ref in admission.evidence
        if isinstance(ref, ProbeRef)
    }


def test_fixed_case_list_and_cross_references() -> None:
    rows = MATRIX
    assert FIXED <= rows.keys()
    assert rows.by_dc3("B2") == {"ES-003"}
    assert rows["ES-011"].outcome is RowOutcome.UNCONFIRMED
    assert {r.rule for r in rows.values() if r.cls is RowClass.SHARED_RULE} == {
        r.rule_id for r in PACKAGED_RULES.rules
    }


@pytest.mark.parametrize("item", sorted(DC3_MAPPING))
def test_dc3_item_maps_to_exactly_its_rows(item: str) -> None:
    assert MATRIX.by_dc3(item) == DC3_MAPPING[item]


@pytest.mark.parametrize("item", sorted(UPSTREAM_MAPPING))
def test_upstream_finding_maps_to_exactly_its_rows(item: str) -> None:
    assert MATRIX.by_upstream(item) == UPSTREAM_MAPPING[item]


def test_u8_points_to_item_4_and_is_not_classified() -> None:
    assert [(p.finding, "Item 4" in p.destination) for p in MATRIX.pointers] == [("U8", True)]
    assert all("U8" not in r.upstream for r in MATRIX.values())


def test_b8_keeps_non_numerical_and_malformed_apart() -> None:
    row = MATRIX["ES-007"]
    splits = {s.label: s for s in row.split}
    assert splits.keys() == {
        "NON_NUMERICAL",
        "MALFORMED_NUMERICAL (block_non_numerical_containment)",
    }
    non_numerical = splits["NON_NUMERICAL"]
    malformed = splits["MALFORMED_NUMERICAL (block_non_numerical_containment)"]
    assert (non_numerical.count, non_numerical.outcome) == (4, RowOutcome.EXCLUDED)
    assert (malformed.count, malformed.outcome) == (4, RowOutcome.REFUSED)
    rule = PACKAGED_RULES.rule("constraint-predicate")
    for split in row.split:
        assert split.shape in row.shapes
        assert Outcome(split.outcome.value) in {
            a.outcome for a in rule.shape(split.shape).admissions.values()
        }


def test_binding_source_classifier_is_fully_placed() -> None:
    placed = {p.kind: p for p in MATRIX.classifier}
    assert tuple(placed) == BINDING_KINDS
    assert placed["literal"].outcome is RowOutcome.ADMITTED
    assert placed["single_reference"].outcome is RowOutcome.ADMITTED
    refused = {
        "self_binding": ("binding-source", "self_reference_source"),
        "indexed": ("indexed-reference", "indexed_reference"),
        "other_expression": ("binding-source", "expression_source"),
    }
    for kind, (rule_id, shape_id) in refused.items():
        placement = placed[kind]
        row = MATRIX[placement.row]
        assert placement.outcome is RowOutcome.REFUSED
        assert (row.rule, shape_id in row.shapes) == (rule_id, True)
        assert PACKAGED_RULES.rule(rule_id).shape(shape_id).expected_code == placement.code
    for placement in MATRIX.classifier:
        if placement.outcome is RowOutcome.ADMITTED:
            assert placement.code == ""


def test_shared_rule_rows_and_records_agree_both_directions() -> None:
    shared = [r for r in MATRIX.values() if r.cls is RowClass.SHARED_RULE]
    for row in shared:
        assert row.rule is not None
        rule = PACKAGED_RULES.rule(row.rule)
        assert row.row_id in rule.matrix_rows, row.row_id
        assert set(row.shapes) <= {s.shape_id for s in rule.shapes}, row.row_id
        assert row.evidence_status.value == rule.evidence_status.value, row.row_id
    for rule in PACKAGED_RULES.rules:
        rows = [r for r in shared if r.rule == rule.rule_id]
        assert {r.row_id for r in rows} == set(rule.matrix_rows), rule.rule_id
        assert {s for r in rows for s in r.shapes} == {s.shape_id for s in rule.shapes}


def test_shared_rule_row_contexts_are_the_record_contexts_with_its_outcome() -> None:
    for row in MATRIX.values():
        if row.cls is not RowClass.SHARED_RULE:
            continue
        assert row.rule is not None
        rule = PACKAGED_RULES.rule(row.rule)
        recorded = {
            context.value
            for shape_id in row.shapes
            for context in rule.shape(shape_id).contexts_with(Outcome(row.outcome.value))
        }
        assert set(row.contexts) == recorded, row.row_id


def test_shared_rule_row_probes_are_cited_by_its_rule_or_are_its_controls() -> None:
    for row in MATRIX.values():
        if row.cls is not RowClass.SHARED_RULE:
            continue
        assert row.rule is not None
        cited = _cited_probes(row.rule)
        for probe_id in row.probe_ids():
            probe = load_probe(PROBES_DIR / probe_id)
            assert probe_id in cited or (
                probe.kind is ProbeKind.CONTROL and probe.rule == row.rule
            ), (row.row_id, probe_id)


@pytest.mark.parametrize("row_id", list(MATRIX))
def test_every_cited_probe_exists_and_certifies(row_id: str) -> None:
    row = MATRIX[row_id]
    for probe_id in row.probe_ids():
        probe = load_probe(PROBES_DIR / probe_id)
        observation, recorded = load_observation(PROBES_DIR / probe_id / "observation.json")
        assert judge(probe, observation).certifies and recorded.certifies, probe_id
        expected_kind = STATUS_PROBE_KIND.get(row.evidence_status)
        if expected_kind is not None:
            assert probe.kind is expected_kind, (row_id, probe_id)


def test_probe_backed_rows_cite_a_probe() -> None:
    for row in MATRIX.values():
        if row.evidence_status in STATUS_PROBE_KIND or row.evidence_status in {
            RowEvidence.PROBE_OBSERVED,
            RowEvidence.PARTIAL,
        }:
            assert row.probe_ids(), row.row_id
        if row.evidence_status is RowEvidence.CORPUS_RECORD:
            assert any(e.startswith("corpus:") for e in row.evidence), row.row_id


def test_every_row_not_implemented_in_item_1_states_its_coverage_limitation() -> None:
    for row in MATRIX.values():
        implemented = row.cls is RowClass.SHARED_RULE
        if not implemented or row.evidence_status is not RowEvidence.PROBE_OBSERVED:
            assert row.coverage_limitation.strip(), row.row_id
        assert row.owner.strip(), row.row_id


def test_self_binding_states_its_relation_to_l2() -> None:
    assert "L2_SELF_NAMED_BINDING" in MATRIX["SELF-BINDING"].l2_relation
    assert [r.row_id for r in MATRIX.values() if r.l2_relation] == ["SELF-BINDING"]


def test_an_unconfirmed_case_is_never_recorded_as_refused_without_a_probe() -> None:
    for row in MATRIX.values():
        if row.outcome is RowOutcome.REFUSED:
            assert row.probe_ids() or row.evidence_status is RowEvidence.CORPUS_RECORD, row.row_id


# ---- the loader rejects a malformed matrix ---------------------------------------------------


def _write(tmp_path: Path, old: str, new: str) -> Path:
    text = MATRIX_PATH.read_text(encoding="utf-8")
    assert old in text
    path = tmp_path / "matrix.toml"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('class = "tracked_gap"', 'class = "maybe"'),
        ('class = "tracked_gap"', 'class = "tracked_gap"\nrule = "binding-source"'),
        ('outcome = "unconfirmed"', 'outcome = "blocked"'),
        ('dc3 = ["B9"]', 'dc3 = ["B10"]'),
        ('evidence_status = "reproduction_probe"', 'evidence_status = "probe_observed"'),
        ('kind = "literal"', 'kind = "constant"'),
        ('owner = "sysml-codegen [DEEP-QUALIFIED-OUTPUT-WIRING]"', 'owner = ""'),
        ('evidence = ["corpus:deep_cross_scope_probe"]', 'evidence = ["somewhere"]'),
    ],
)
def test_loader_rejects(tmp_path: Path, old: str, new: str) -> None:
    with pytest.raises(MatrixError):
        load_matrix(_write(tmp_path, old, new))


def test_matrix_is_a_mapping_in_file_order() -> None:
    assert isinstance(MATRIX, Matrix)
    assert list(MATRIX)[0] == "ES-001"
    assert len(MATRIX) == len(set(MATRIX))

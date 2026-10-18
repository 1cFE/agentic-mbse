"""Closed vocabularies: every enum is closed and every reason is validated at construction."""

from __future__ import annotations

from uuid import uuid4

import pytest

from agentic_mbse.sysml.executable_profile import REASON_CODES
from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.subset_profile import (
    SUBSET_REASON_CODES,
    CaseRef,
    ContextId,
    EvidenceStatus,
    Outcome,
    Qualification,
    SubsetFinding,
    UnverifiedCheck,
    Verdict,
)

SUBJECT = ElementRef(uuid4(), None, "AttributeUsage")
WHERE = SafeLocation("model.sysml", 3, None)


def finding(**changes: object) -> SubsetFinding:
    fields: dict[str, object] = dict(
        rule_id="invocation-callable",
        shape_id="unsupported_callable",
        context_id=ContextId.ATTRIBUTE_VALUE,
        outcome=Outcome.REFUSED,
        reason="invocation_callable_unsupported",
        detail_reasons=(),
        subject=SUBJECT,
        location=WHERE,
        occurrence_count=None,
        via_roots=(),
        evidence=(CaseRef("invocation-callable__unsupported_callable__attribute_value"),),
        qualification=Qualification.NONE,
    )
    fields.update(changes)
    return SubsetFinding(**fields)  # type: ignore[arg-type]


def test_enums_are_the_documented_closed_sets() -> None:
    assert {o.value for o in Outcome} == {
        "refused",
        "admitted",
        "excluded",
        "omitted",
        "unconfirmed",
    }
    assert {v.value for v in Verdict} == {
        "refused_incomplete",
        "incomplete",
        "refused",
        "unconfirmed",
        "clear",
    }
    assert {s.value for s in EvidenceStatus} == {
        "case_observed",
        "partial",
        "code_read_pending_item_2",
    }
    assert len(ContextId) == 18
    with pytest.raises(ValueError):
        ContextId("everywhere")


def test_subset_reasons_are_disjoint_from_the_executable_profiles() -> None:
    assert SUBSET_REASON_CODES.isdisjoint(REASON_CODES)


def test_a_well_formed_finding_constructs() -> None:
    assert finding().outcome is Outcome.REFUSED


@pytest.mark.parametrize(
    ("changes", "error", "message"),
    [
        ({"reason": "made_up"}, ValueError, "unknown subset reason"),
        ({"detail_reasons": ("block_made_up",)}, ValueError, "unknown executable-profile"),
        (
            {"detail_reasons": ("invocation_callable_unsupported",)},
            ValueError,
            "unknown executable-profile",
        ),
        ({"rule_id": "made-up"}, ValueError, "unknown rule or shape"),
        ({"shape_id": "made_up"}, ValueError, "unknown rule or shape"),
        ({"outcome": "refused"}, TypeError, "closed vocabularies"),
        ({"context_id": "attribute_value"}, TypeError, "closed vocabularies"),
        ({"outcome": Outcome.UNCONFIRMED}, ValueError, "evidence exactly when"),
        ({"evidence": ()}, ValueError, "evidence exactly when"),
    ],
)
def test_finding_rejects_anything_outside_its_vocabularies(
    changes: dict[str, object], error: type[Exception], message: str
) -> None:
    with pytest.raises(error, match=message):
        finding(**changes)


def test_unverified_check_takes_only_known_rules_and_closed_causes() -> None:
    with pytest.raises(ValueError, match="unknown rule"):
        UnverifiedCheck("made-up", None, None, ContextId.ATTRIBUTE_VALUE, "")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="closed failure code"):
        UnverifiedCheck("invocation-callable", None, None, "resolved_target_missing", "")  # type: ignore[arg-type]

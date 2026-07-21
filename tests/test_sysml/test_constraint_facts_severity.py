"""Diagnostic severity and closed codes on the wire (Item 4, DD-A01/A02/A05).

`ExtractionDiagnosticFact` carried `kind: str` and `message: str` — no severity, and
`kind` was a bare string with no closed vocabulary. Severity now travels **with the
data**, fixed at construction from the writer's own table, so two readers at different
versions can never disagree about whether the same bytes block (DD-R01, DD-R07).
"""

from __future__ import annotations

import json

import pytest

from agentic_mbse.sysml.constraint_facts import (
    CONSTRAINT_FACTS_SCHEMA_VERSION,
    EXTRACTION_DIAGNOSTIC_KINDS,
    ConstraintFacts,
    DiagnosticSeverity,
    ExtractionDiagnosticFact,
    parse,
    serialize,
)
from agentic_mbse.sysml.executable_profile import REASON_CODES, EligibilityDiagnostic
from agentic_mbse.sysml.expression_facts import IdentityFact


def _facts(diagnostics: list[ExtractionDiagnosticFact]) -> ConstraintFacts:
    return ConstraintFacts(
        definitions=[], usages=[], contexts=[], diagnostics=list(diagnostics)
    )


def _diagnostic(kind: str = "non_finite_literal") -> ExtractionDiagnosticFact:
    return ExtractionDiagnosticFact(
        kind=kind,
        message="non-finite literal operand encountered",
        operand_source="1.0 / 0.0",
        location=None,
    )


# --- DD-A02: severity is a field, fixed at construction ---------------------


def test_severity_is_assigned_at_construction_from_the_writer_table():
    """DD-R01/DD-R07: the writer decides; no reader ever recomputes it."""
    diagnostic = _diagnostic("non_finite_literal")
    assert diagnostic.severity is DiagnosticSeverity.BLOCKING


def test_unknown_kind_is_refused_at_construction():
    """DD-R01: `kind` is a closed vocabulary, enforced in production not by convention."""
    with pytest.raises(ValueError, match="unknown extraction diagnostic kind"):
        _diagnostic("not_a_real_kind")


def test_every_declared_kind_constructs_and_carries_a_severity():
    for kind in EXTRACTION_DIAGNOSTIC_KINDS:
        assert isinstance(_diagnostic(kind).severity, DiagnosticSeverity)


def test_severity_round_trips_byte_identically():
    """DD-A02: serialize -> parse -> serialize is byte-identical at one pinned schema pair."""
    text = serialize(_facts([_diagnostic()]))
    assert serialize(parse(text)) == text
    assert json.loads(text)["diagnostics"][0]["severity"] == "blocking"


# --- DD-A02 / DD-A05: fail closed, before any semantic use ------------------


def test_unrecognized_severity_fails_closed_at_parse():
    payload = json.loads(serialize(_facts([_diagnostic()])))
    payload["diagnostics"][0]["severity"] = "advisory_ish"
    with pytest.raises(ValueError, match="unsupported diagnostic severity"):
        parse(json.dumps(payload))


def test_unrecognized_kind_fails_closed_at_parse():
    payload = json.loads(serialize(_facts([_diagnostic()])))
    payload["diagnostics"][0]["kind"] = "invented_later"
    with pytest.raises(ValueError, match="unknown extraction diagnostic kind"):
        parse(json.dumps(payload))


@pytest.mark.parametrize(
    "foreign_version",
    ["constraint-facts/v1", "constraint-facts/v3"],
    ids=["reader-newer-than-writer", "reader-older-than-writer"],
)
def test_both_skew_directions_fail_closed_before_field_deserialization(foreign_version):
    """DD-A05: exact equality, both directions, no shared setup with the happy path."""
    payload = json.loads(serialize(_facts([_diagnostic()])))
    payload["schema_version"] = foreign_version
    # Corrupt a field too: if the version gate did not run first, this would raise
    # a different error and the "before any semantic use" claim would be false.
    payload["diagnostics"][0]["kind"] = "invented_later"
    with pytest.raises(ValueError, match="unsupported ConstraintFacts schema_version"):
        parse(json.dumps(payload))


def test_schema_version_is_v2():
    assert CONSTRAINT_FACTS_SCHEMA_VERSION == "constraint-facts/v2"


# --- DD-A01: the profile's reason vocabulary, enforced in production --------


def _eligibility(reason: str) -> EligibilityDiagnostic:
    return EligibilityDiagnostic(
        reason=reason,
        construct="OperatorExpression",
        location=None,
        constraint_identity=IdentityFact(kind="ConstraintUsage", name="c", qualified_name="P::c"),
        message="blocked",
    )


def test_eligibility_reason_outside_the_closed_vocabulary_is_refused():
    """DD-R05: refused at construction, not a string that survives into a user message."""
    with pytest.raises(ValueError, match="unknown eligibility reason"):
        _eligibility("block_something_invented")


def test_every_existing_reason_code_is_accepted_unchanged():
    """All 27 declared reasons still construct."""
    for reason in REASON_CODES:
        assert _eligibility(reason).reason == reason


# --- DD-A04: the reason code survives as a branchable field ------------------


def test_validation_issue_carries_a_branchable_reason_code():
    """DD-R10: the discriminator is a field, not only interpolated message text.

    The object DD-A04 pins is the list of `ValidationIssue` the L6 check returns —
    not the terminal rendering, whose five-issue truncation is explicitly out of
    scope.
    """
    from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue

    issue = ValidationIssue(
        level=6,
        severity=Severity.ERROR,
        code=ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL,
        message="Constraint 'P::c' is a malformed numerical statement: X (block_invocation)",
        reason_code="block_invocation",
    )
    # A consumer branches on the field without parsing the message.
    assert issue.reason_code == "block_invocation"
    assert issue.reason_code in REASON_CODES


def test_reason_code_defaults_to_none_for_issues_that_have_no_such_vocabulary():
    from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue

    issue = ValidationIssue(
        level=2,
        severity=Severity.ERROR,
        code=ValidationCode.UNBOUND_INPUT,
        message="Input 'x' has no binding",
    )
    assert issue.reason_code is None

"""The authoring-time half of the vacuous-gate obligation (lifecycle invariant 61).

An asserted gate on a part definition nothing instantiates is a check that cannot fail.
The author is the only one who can act on that, and authoring time is the only moment it
is actionable — so it is an ``ADVISORY`` extraction diagnostic here, not an error, and not
codegen's job. Codegen grades the same condition independently and unconditionally
(invariant 59); this does not replace that and does not feed it.

The two trigger sets are deliberately *not* equal. This layer has no occurrence index, so
it asks the structural question — is the owning part definition typed by any part usage —
which is strictly weaker than "was anything of it ever instantiated". That makes this set
a subset of codegen's, so the advisory can only ever be missing, never false. The
containment test below pins that direction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_mbse.sysml.constraint_extraction import extract_identified_constraint_facts
from agentic_mbse.sysml.constraint_facts import (
    CONSTRAINT_FACTS_SCHEMA_VERSION,
    EXTRACTION_DIAGNOSTIC_SEVERITY,
    DiagnosticSeverity,
    severity_for_kind,
)
from agentic_mbse.sysml.syside_adapter import get_syside

syside = get_syside()

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "vacuous_asserted_gate"
KIND = "vacuous_asserted_gate"


def _advisories(fixture: str) -> list[Any]:
    model, diagnostics = syside.try_load_model([str(FIXTURE_DIR / fixture)])
    assert not list(diagnostics.all)
    facts = extract_identified_constraint_facts(model).facts
    return [item for item in facts.diagnostics if item.kind == KIND]


def test_a_detached_owner_emits_one_advisory_naming_the_usage_and_the_owner():
    (advisory,) = _advisories("detached_owner.sysml")
    assert advisory.severity is DiagnosticSeverity.ADVISORY
    assert "vacuous_detached::Detached::vacuous_gate" in advisory.message
    assert "vacuous_detached::Detached" in advisory.message
    assert advisory.location is not None
    assert advisory.location.line > 0
    assert advisory.location.column > 0


def test_a_typed_but_never_instantiated_owner_stays_silent():
    """Silence here is CORRECT. Codegen still grades this one vacuous."""
    assert _advisories("typed_but_uninstantiated.sysml") == []


def test_a_non_asserted_usage_on_a_detached_owner_stays_silent():
    assert _advisories("non_asserted_on_detached_owner.sysml") == []


def test_the_severity_is_writer_side_and_the_map_stays_closed():
    assert EXTRACTION_DIAGNOSTIC_SEVERITY[KIND] is DiagnosticSeverity.ADVISORY
    assert severity_for_kind(KIND) is DiagnosticSeverity.ADVISORY
    assert set(EXTRACTION_DIAGNOSTIC_SEVERITY) == {"non_finite_literal", KIND}


def test_adding_the_kind_cost_a_schema_bump():
    """A new kind changes the meaning of bytes already on disk, so the version moves."""
    assert CONSTRAINT_FACTS_SCHEMA_VERSION == "constraint-facts/v3"

"""The closed reference-use boundary Agentic must own after `semantic-evidence/v2`.

Phase 1 writes this as a recorded red set.  Nothing here is satisfiable at `A_base`:
`agentic_mbse.sysml.reference_use` does not exist, the evidence vocabulary has no
`INDEXED_REFERENCE_UNSUPPORTED` code, and an indexed feature chain is still representable
as an exact fact carrying a `has_index_segment: bool` marker.  That marker is precisely
the defect: a boolean beside an otherwise-exact path lets a downstream consumer read the
path and ignore the flag, which is how an authored `#(i)` becomes a different expression.

The target, from
`.project/active/stop-reinventing-the-parser/design.md#closed-reference-use-values`:
one total inspection operation returns a closed union.  An `ExactReferenceUse` carries a
path; an `IndexedReferenceUse` has no `path` attribute at all, so an index cannot be
represented as an exact reference even by mistake.  Term construction over an indexed use
raises `SemanticEvidenceError` with `INDEXED_REFERENCE_UNSUPPORTED` before any term exists.

These tests must expose the permissive helpers, not grandfather them.
"""

from __future__ import annotations

import pytest

from agentic_mbse.errors import SemanticEvidenceCode


def _reference_use_module():
    """Import the closed boundary.

    Absent at `A_base`, so this raises `ModuleNotFoundError` — the recorded red.  It is
    deliberately not an `importorskip`: a skip would hide the gap this phase exists to pin.
    """
    import agentic_mbse.sysml.reference_use as reference_use

    return reference_use


def test_the_closed_reference_use_boundary_module_exists() -> None:
    """Recorded red at `A_base`: `agentic_mbse/sysml/reference_use.py` is not written yet."""
    module = _reference_use_module()
    for name in ("ReferenceUse", "ExactReferenceUse", "IndexedReferenceUse", "inspect_reference_uses"):
        assert hasattr(module, name), f"closed boundary omits {name}"


def test_evidence_vocabulary_names_the_indexed_refusal() -> None:
    """Recorded red at `A_base`: the code that refuses an authored index does not exist."""
    assert hasattr(SemanticEvidenceCode, "INDEXED_REFERENCE_UNSUPPORTED")


def test_indexed_reference_use_has_no_path_attribute() -> None:
    """An indexed use must be structurally incapable of carrying an exact path."""
    module = _reference_use_module()
    indexed = module.IndexedReferenceUse
    assert "path" not in getattr(indexed, "__annotations__", {})
    assert not hasattr(indexed, "path")


def test_exact_reference_use_carries_the_path_and_no_index_marker() -> None:
    """The exact variant carries evidence; it never carries a flag about an index."""
    module = _reference_use_module()
    annotations = getattr(module.ExactReferenceUse, "__annotations__", {})
    assert "path" in annotations
    assert "has_index_segment" not in annotations


def test_the_permissive_boolean_index_marker_is_gone() -> None:
    """Recorded red at `A_base`: `has_index_segment` is still a field on the exact fact.

    `ResolvedSemanticReferenceFact.has_index_segment` (`sysml/data_models.py:89`) is the
    marker this item removes.  While it exists, an indexed chain and an exact chain have
    the same type and a consumer can read the path regardless.
    """
    from agentic_mbse.sysml import data_models

    assert "has_index_segment" not in getattr(
        data_models.ResolvedSemanticReferenceFact, "__annotations__", {}
    )


def test_an_indexed_use_cannot_form_an_aggregation_term() -> None:
    """Refusal happens before term construction, with the named code."""
    module = _reference_use_module()

    with pytest.raises(Exception) as caught:
        module.build_aggregation_term(module.IndexedReferenceUse)
    assert getattr(caught.value, "code", None) is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED

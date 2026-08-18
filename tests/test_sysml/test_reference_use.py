"""The closed reference-use boundary Agentic owns after `semantic-evidence/v2`.

Phase 1 wrote the first six tests as a recorded red set.  Nothing there was satisfiable at
`A_base`: `agentic_mbse.sysml.reference_use` did not exist, the evidence vocabulary had no
`INDEXED_REFERENCE_UNSUPPORTED` code, and an indexed feature chain was still representable
as an exact fact carrying a `has_index_segment: bool` marker.  That marker was precisely
the defect: a boolean beside an otherwise-exact path lets a downstream consumer read the
path and ignore the flag, which is how an authored `#(i)` becomes a different expression.

The target, from
`.project/active/stop-reinventing-the-parser/design.md#closed-reference-use-values`:
one total inspection operation returns a closed union.  An `ExactReferenceUse` carries a
path; an `IndexedReferenceUse` has no `path` attribute at all, so an index cannot be
represented as an exact reference even by mistake.  Term construction over an indexed use
raises `SemanticEvidenceError` with `INDEXED_REFERENCE_UNSUPPORTED` before any term exists.

Phase 2 completes the file: the six recorded nodes keep their names and their stated
reasons, and the coverage the plan's checklist requires is added beside them — exact
positive evidence, mapped `IndexExpression` dispatch, operand failure, depth exhaustion,
missing target and missing leaf, document tiers, aggregation refusal, ordered binding
evidence, and ADR002 dynamic handling.
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_mbse.errors import (
    SEMANTIC_EVIDENCE_API_VERSION,
    SemanticEvidenceCode,
    SemanticEvidenceError,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

# --------------------------------------------------------------------------------------
# Recorded Phase-1 red nodes.  Names and reasons are unchanged.
# --------------------------------------------------------------------------------------


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

    Phase 2 deletes `ResolvedSemanticReferenceFact` outright, so the class going away is the
    strongest way to satisfy this.  The lookup is therefore by `getattr`, not attribute
    access: reaching through a deleted class would raise `AttributeError` and leave the test
    permanently red against a correct implementation.  Both endings pass — class absent, or
    class present without the marker — and only today's state fails.
    """
    from agentic_mbse.sysml import data_models

    fact = getattr(data_models, "ResolvedSemanticReferenceFact", None)
    annotations = {} if fact is None else getattr(fact, "__annotations__", {})
    assert "has_index_segment" not in annotations


def test_an_indexed_use_cannot_form_an_aggregation_term() -> None:
    """Refusal happens before term construction, with the named code.

    Audit Minor 11: Phase 1 passed the `IndexedReferenceUse` *class* and caught a broad
    `Exception`, so the test could not tell "refused by name" from "crashed on a bad
    argument".  It now constructs a real indexed use, requires the exact public exception
    type, and proves the refusal precedes term construction: the same call over an
    equivalent *exact* use returns a term, so the refusal is about the index and not about
    the call failing for some other reason.
    """
    module = _reference_use_module()
    indexed = module.IndexedReferenceUse(
        reference="cells#(2).mass", location=("model.sysml", 15)
    )

    with pytest.raises(SemanticEvidenceError) as caught:
        module.build_aggregation_term(indexed)

    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED
    assert caught.value.reference == "cells#(2).mass"
    assert caught.value.location == ("model.sysml", 15)

    # The paired positive: the same operation over an exact use does build a term, so the
    # refusal above is the index being named, not term construction failing generally.
    exact = _exact_use_double("cells.mass")
    term = module.build_aggregation_term(exact)
    assert term.source_path == "cells.mass"
    assert term.resolved_target is exact.path.leaf
    assert term.chain_root is exact.path.root


# --------------------------------------------------------------------------------------
# Helpers: constructed values (no license) and live-model fixtures (licensed).
# --------------------------------------------------------------------------------------


def _target_fact(name: str, *, tier: str = "Project") -> Any:
    from uuid import NAMESPACE_URL, uuid5

    from agentic_mbse.sysml.data_models import ResolvedTargetFact

    return ResolvedTargetFact(
        element_id=uuid5(NAMESPACE_URL, name),
        owner_element_id=None,
        redefined_element_ids=(),
        qualified_name=f"Probe::{name}",
        element_kind="AttributeUsage",
        element_name=name,
        document_url="file:///probe/model.sysml",
        document_tier=tier,
        source_location=("model.sysml", 15),
    )


def _exact_use_double(authored: str) -> Any:
    """An `ExactReferenceUse` built from constructed facts, for license-free assertions."""
    module = _reference_use_module()
    segments = authored.split(".")
    facts = tuple(_target_fact(segment) for segment in segments)
    path = module.ExactSemanticPath(
        root=facts[0],
        segments=facts,
        leaf=facts[-1],
        resolved_member_names=tuple(segments[1:]),
    )
    return module.ExactReferenceUse(
        path=path,
        form="chain" if len(segments) > 1 else "bare",
        authored_text=authored,
        authored_segments=tuple(segments),
        authored_qualifier=None,
        plural=False,
        location=("model.sysml", 15),
    )


PROBE_MODEL = """package Probe {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    part def Cell {
        attribute mass : ScalarValues::Real = 1.0;
    }
    part def Rack {
        part cells : Cell[3];
        attribute local_scale : ScalarValues::Real = 2.0;
        attribute picked : ScalarValues::Real = cells#(2).mass;
        attribute total : ScalarValues::Real = sum(cells.mass);
        attribute scaled : ScalarValues::Real = local_scale * 2.0;
        attribute unit_wrapped : ScalarValues::Real = 3.0 [SI::metre];
        attribute qualified_ref : ScalarValues::Real = Probe::Rack::local_scale;
    }
}
"""


@pytest.fixture(scope="module")
def probe_expressions(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Named `feature_value_expression` nodes from one live, licensed model."""
    root = tmp_path_factory.mktemp("reference_use_probe")
    (root / "model.sysml").write_text(PROBE_MODEL)
    try:
        model, _ = SysideAdapter.load_model([root])
    except Exception as exc:  # pragma: no cover - license-gated
        pytest.skip(f"SysIDE model load unavailable: {exc}")
    found: dict[str, Any] = {}
    for attribute in SysideAdapter.elements_of_type(model, "AttributeUsage"):
        expression = getattr(attribute, "feature_value_expression", None)
        if expression is not None and attribute.name:
            found[str(attribute.name)] = expression
    missing = {
        "picked",
        "total",
        "scaled",
        "unit_wrapped",
        "qualified_ref",
    } - set(found)
    assert not missing, f"probe model did not yield {sorted(missing)}"
    return found


# --------------------------------------------------------------------------------------
# Exact positive evidence.
# --------------------------------------------------------------------------------------


def test_a_bare_reference_yields_one_exact_use_with_authored_evidence(probe_expressions) -> None:
    """`local_scale * 2.0` carries the authored spelling, form, and root-relative location."""
    module = _reference_use_module()
    uses = module.inspect_reference_uses(probe_expressions["scaled"])

    assert len(uses) == 1
    use = uses[0]
    assert isinstance(use, module.ExactReferenceUse)
    assert use.form == "bare"
    assert use.authored_text == "local_scale"
    assert use.authored_segments == ("local_scale",)
    assert use.authored_qualifier is None
    assert use.plural is False
    assert use.location is not None and use.location[1] == 13


def test_a_qualified_reference_records_its_authored_qualifier(probe_expressions) -> None:
    """`Probe::Rack::local_scale` is a qualified authored form, not a bare one."""
    module = _reference_use_module()
    (use,) = module.inspect_reference_uses(probe_expressions["qualified_ref"])

    assert isinstance(use, module.ExactReferenceUse)
    assert use.form == "qualified"
    assert use.authored_text == "Probe::Rack::local_scale"
    assert use.authored_qualifier == "Probe::Rack"
    assert use.path.leaf.element_name == "local_scale"


def test_an_exact_chain_carries_root_members_leaf_and_document_evidence(probe_expressions) -> None:
    """`sum(cells.mass)` — the provenance-complete payload the design requires.

    Root, members, leaf, owner, document, authored form, order, and location, with no
    operator or literal structure anywhere in the value.
    """
    module = _reference_use_module()
    (use,) = module.inspect_reference_uses(probe_expressions["total"])

    assert isinstance(use, module.ExactReferenceUse)
    assert use.form == "chain"
    assert use.authored_text == "cells.mass"
    assert use.authored_segments == ("cells", "mass")
    assert use.plural is True, "a supported sum() invocation marks its uses plural"

    path = use.path
    assert path.root.element_name == "cells"
    assert path.leaf.element_name == "mass"
    assert path.segments[0] is path.root
    assert path.segments[-1] is path.leaf
    assert path.resolved_member_names == ("mass",)

    for fact in (path.root, path.leaf):
        assert fact.element_id is not None
        assert fact.qualified_name.startswith("Probe::")
        assert fact.owner_qualified_name
        assert fact.document_url
        assert fact.document_tier == "Project"
        assert fact.source_location is not None

    # No operator or literal structure rides along on the reference value.
    assert not hasattr(use, "operator")
    assert not hasattr(use, "operands")


def test_an_exact_path_refuses_to_exist_without_a_root_and_leaf() -> None:
    """`ExactSemanticPath` has no public optional-root or optional-leaf state."""
    module = _reference_use_module()
    root = _target_fact("cells")
    leaf = _target_fact("mass")

    with pytest.raises(ValueError):
        module.ExactSemanticPath(
            root=root, segments=(), leaf=leaf, resolved_member_names=()
        )
    with pytest.raises(ValueError):
        module.ExactSemanticPath(
            root=root, segments=(leaf,), leaf=leaf, resolved_member_names=()
        )
    with pytest.raises(ValueError):
        module.ExactSemanticPath(
            root=root, segments=(root,), leaf=leaf, resolved_member_names=()
        )


# --------------------------------------------------------------------------------------
# Indexed refusal and mapped dispatch.
# --------------------------------------------------------------------------------------


def test_an_indexed_chain_returns_the_closed_indexed_variant(probe_expressions) -> None:
    """`cells#(2).mass` is representable only as an indexed use, with the authored text."""
    module = _reference_use_module()
    uses = module.inspect_reference_uses(probe_expressions["picked"])

    assert len(uses) == 1
    use = uses[0]
    assert isinstance(use, module.IndexedReferenceUse)
    assert not hasattr(use, "path")
    assert use.reference == "cells#(2).mass"
    assert use.location is not None and use.location[1] == 11


def test_index_dispatch_comes_from_the_mapped_metatype_not_a_class_name(probe_expressions) -> None:
    """`IndexExpression` is a mapped SysIDE metatype, and the map is the authority.

    The design forbids a runtime class-name comparison here.  Two proofs: the adapter's
    closed type map resolves `IndexExpression` to the installed SysIDE class, and the live
    index node answers the mapped `is_instance` query.
    """
    module = _reference_use_module()
    assert SysideAdapter.get_type("IndexExpression") is get_syside().IndexExpression

    chain = probe_expressions["picked"]
    (head,) = tuple(module.materialize_operands(chain))[:1]
    assert SysideAdapter.is_instance(head, "IndexExpression")

    # The claim is about production dispatch: the boundary must never decide an index by
    # comparing a runtime class name.  The old route did exactly that
    # (`type(first).__name__ == "IndexExpression"`); the new one has no such comparison.
    import inspect as _inspect

    source = _inspect.getsource(module)
    assert "__name__ ==" not in source
    assert '"IndexExpression"' in source  # named only as a mapped type-map key


def test_an_indexed_use_never_reaches_a_binding_path(probe_expressions) -> None:
    """The union is closed: the indexed variant simply has no path to project."""
    module = _reference_use_module()
    (use,) = module.inspect_reference_uses(probe_expressions["picked"])
    assert not hasattr(use, "path")
    with pytest.raises(SemanticEvidenceError) as caught:
        module.require_exact_reference_use(use, operation="binding_evidence")
    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED


# --------------------------------------------------------------------------------------
# Named failures: operand iteration, depth, missing target, missing leaf, tiers.
# --------------------------------------------------------------------------------------


class OperatorExpression:
    """Base for non-live doubles: the adapter matches mapped names in the Python MRO."""


class _RefusingOperands(OperatorExpression):
    """A non-live double whose operand sequence cannot be materialized."""

    @property
    def operands(self) -> Any:
        raise RuntimeError("operand iteration exploded")


def test_operand_iteration_failure_is_a_named_outcome_carrying_its_cause() -> None:
    module = _reference_use_module()
    with pytest.raises(SemanticEvidenceError) as caught:
        module.inspect_reference_uses(_RefusingOperands())
    assert caught.value.code is SemanticEvidenceCode.OPERAND_ITERATION_FAILED
    assert isinstance(caught.value.cause, RuntimeError)
    assert caught.value.__cause__ is caught.value.cause


class _EndlessOperator(OperatorExpression):
    """A non-live double that nests into itself forever."""

    @property
    def operands(self) -> tuple[Any, ...]:
        return (self,)


def test_depth_exhaustion_is_its_own_named_outcome() -> None:
    """Exhaustion raises `EXPRESSION_DEPTH_EXHAUSTED`; no partial result escapes."""
    module = _reference_use_module()
    with pytest.raises(SemanticEvidenceError) as caught:
        module.inspect_reference_uses(_EndlessOperator())
    assert caught.value.code is SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED


def test_the_depth_budget_is_not_caller_selectable() -> None:
    """One shared limit; no consumer may widen or narrow it through the signature."""
    import inspect as _inspect

    module = _reference_use_module()
    parameters = _inspect.signature(module.inspect_reference_uses).parameters
    assert list(parameters) == ["expression"]
    assert isinstance(module.MAX_EXPRESSION_DEPTH, int)


class FeatureReferenceExpression:
    """Base for non-live feature-reference doubles."""


class FeatureChainExpression:
    """Base for non-live feature-chain doubles."""


class _ReferenceWithoutReferent(FeatureReferenceExpression):
    referent = None
    name = "orphan"


def test_a_missing_resolved_target_is_named_and_never_an_empty_result() -> None:
    module = _reference_use_module()
    with pytest.raises(SemanticEvidenceError) as caught:
        module.inspect_reference_uses(_ReferenceWithoutReferent())
    assert caught.value.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING


class _Chained:
    def __init__(self, name: str | None) -> None:
        from uuid import NAMESPACE_URL, uuid5

        self.name = name
        self.qualified_name = f"Probe::{name}" if name else None
        self.element_id = uuid5(NAMESPACE_URL, str(name))
        # Doubles carry a document with a real tier: D6 makes the tier the sole
        # standard-library classifier, so a target without one is a named failure and
        # would mask the leaf failure this double exists to prove.
        self.document = type(
            "Document",
            (),
            {"url": "file:///probe/model.sysml", "document_tier": get_syside().DocumentTier.Project},
        )()
        self.chaining_features: list[Any] = []


class _ChainWithUnusableLeaf(FeatureChainExpression):
    """A chain whose declared leaf carries no qualified name — B8's skip-proof case."""

    def __init__(self) -> None:
        self.operands = [_ReferenceTo("cells")]
        leaf = _Chained(None)
        target = _Chained("mass")
        target.chaining_features = [leaf]
        self.target_feature = target


class _ReferenceTo(FeatureReferenceExpression):
    def __init__(self, name: str) -> None:
        self.name = name
        self.referent = _Chained(name)


def test_a_resolved_fact_without_its_exact_leaf_can_never_be_skipped() -> None:
    """B8: a fact marked resolved but lacking its exact leaf raises, it does not continue."""
    module = _reference_use_module()
    with pytest.raises(SemanticEvidenceError) as caught:
        module.inspect_reference_uses(_ChainWithUnusableLeaf())
    assert caught.value.code is SemanticEvidenceCode.RESOLVED_LEAF_MISSING


def test_a_standard_library_target_is_classified_by_its_document_tier(probe_expressions) -> None:
    """D6: the unit reference in `3.0 [SI::metre]` is StandardLibrary by tier, not by name."""
    module = _reference_use_module()
    uses = module.inspect_reference_uses(probe_expressions["unit_wrapped"])
    tiers = {use.path.leaf.document_tier for use in uses}
    assert tiers == {"StandardLibrary"}, tiers

    project = module.inspect_reference_uses(probe_expressions["scaled"])
    assert {use.path.leaf.document_tier for use in project} == {"Project"}


def test_a_project_package_named_si_is_still_project_evidence(tmp_path) -> None:
    """A real user package named `SI` remains project evidence (D6)."""
    module = _reference_use_module()
    (tmp_path / "model.sysml").write_text(
        "package SI {\n"
        "    part def Holder {\n"
        "        attribute base : ScalarValues::Real = 1.0;\n"
        "        attribute scaled_value : ScalarValues::Real = base * 2.0;\n"
        "    }\n"
        "}\n"
    )
    try:
        model, _ = SysideAdapter.load_model([tmp_path])
    except Exception as exc:  # pragma: no cover - license-gated
        pytest.skip(f"SysIDE model load unavailable: {exc}")
    for attribute in SysideAdapter.elements_of_type(model, "AttributeUsage"):
        if attribute.name == "scaled_value":
            (use,) = module.inspect_reference_uses(attribute.feature_value_expression)
            assert use.path.leaf.document_tier == "Project"
            assert use.path.leaf.qualified_name.startswith("SI::")
            return
    pytest.fail("probe model did not yield the `scaled_value` attribute")


# --------------------------------------------------------------------------------------
# Natural consumers: aggregation, binding, ADR002.
# --------------------------------------------------------------------------------------


def test_aggregation_refuses_an_indexed_operand_before_a_term_exists(probe_expressions) -> None:
    """The aggregation site cannot manufacture an index-free term."""
    from agentic_mbse.sysml.aggregation import decompose_aggregation_expression

    with pytest.raises(SemanticEvidenceError) as caught:
        decompose_aggregation_expression(probe_expressions["picked"])
    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED


def test_aggregation_retains_exact_root_members_and_leaf(probe_expressions) -> None:
    from agentic_mbse.sysml.aggregation import decompose_aggregation_expression

    decomposition = decompose_aggregation_expression(probe_expressions["total"])
    (term,) = decomposition.sum_terms
    assert term.resolved_target is not None and term.resolved_target.element_name == "mass"
    assert term.chain_root is not None and term.chain_root.element_name == "cells"
    assert term.resolved_member_names == ("mass",)


def test_binding_evidence_is_the_ordered_reference_use_tuple() -> None:
    """`BindingInfo` carries ordered closed uses, never a rebuildable `ExpressionRef` list."""
    from agentic_mbse.sysml.types import BindingInfo

    annotations = BindingInfo.model_fields
    assert "references" not in annotations
    assert "reference_uses" in annotations


def test_adr002_counts_an_indexed_reference_as_dynamic_without_flattening_it() -> None:
    """ADR002 treats both variants as a present dynamic reference (D5)."""
    module = _reference_use_module()
    from agentic_mbse.validation.adr002 import reference_is_dynamic

    indexed = module.IndexedReferenceUse(reference="cells#(2).mass", location=None)
    assert reference_is_dynamic(indexed) is True
    assert not hasattr(indexed, "path")

    exact = _exact_use_double("cells.mass")
    assert reference_is_dynamic(exact) is True


# --------------------------------------------------------------------------------------
# Public contract markers.
# --------------------------------------------------------------------------------------


def test_the_public_api_version_advanced_to_v2() -> None:
    assert SEMANTIC_EVIDENCE_API_VERSION == "semantic-evidence/v2"


def test_the_evidence_vocabulary_is_exactly_the_designed_closed_set() -> None:
    assert {code.value for code in SemanticEvidenceCode} == {
        "METATYPE_CHECK_FAILED",
        "EXPRESSION_KIND_UNSUPPORTED",
        "OPERAND_ITERATION_FAILED",
        "EXPRESSION_DEPTH_EXHAUSTED",
        "RESOLVED_TARGET_MISSING",
        "DOCUMENT_TIER_MISSING",
        "DOCUMENT_TIER_UNKNOWN",
        "RESOLVED_LEAF_MISSING",
        "INDEXED_REFERENCE_UNSUPPORTED",
    }


def test_the_closed_boundary_is_exported_from_the_package() -> None:
    import agentic_mbse
    from agentic_mbse import sysml

    for name in (
        "ExactSemanticPath",
        "ExactReferenceUse",
        "IndexedReferenceUse",
        "inspect_reference_uses",
    ):
        assert name in sysml.__all__, f"sysml barrel omits {name}"
        assert hasattr(sysml, name)
    assert agentic_mbse.SEMANTIC_EVIDENCE_API_VERSION == "semantic-evidence/v2"


def test_the_math_only_ir_target_stays_non_authoritative() -> None:
    """`FeatureReferenceFact.target` may describe undecoded math; it is not a dependency."""
    import inspect as _inspect

    from agentic_mbse.sysml import reference_use

    source = _inspect.getsource(reference_use)
    assert "FeatureReferenceFact" not in source
    assert "expression_ir" not in source

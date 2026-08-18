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
from tests.test_sysml.conftest import (
    MockFeatureReferenceExpression,
    MockLiteralRational,
    MockOperatorExpression,
)

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


def _require_a_clean_load(diagnostics: Any) -> None:
    """Assert the probe model parsed.

    Audit m4: the previous form wrapped `load_model` in `except Exception: pytest.skip`,
    which would also have skipped on a genuine regression in the loader.  These probes are
    licensed tests in a licensed lane; a load failure is a failure, and a parse error in the
    probe source is a broken test, not a reason to go quiet.
    """
    errors = [
        item
        for item in diagnostics.all
        if str(getattr(item, "severity", "")).endswith("Error")
    ]
    assert not errors, f"probe model did not parse cleanly: {errors}"


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
        attribute unit_over_reference : ScalarValues::Real = local_scale [SI::metre];
        attribute qualified_ref : ScalarValues::Real = Probe::Rack::local_scale;
    }
}
"""


@pytest.fixture(scope="module")
def probe_expressions(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Named `feature_value_expression` nodes from one live, licensed model."""
    root = tmp_path_factory.mktemp("reference_use_probe")
    (root / "model.sysml").write_text(PROBE_MODEL)
    model, diagnostics = SysideAdapter.load_model([root])
    _require_a_clean_load(diagnostics)
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
        "unit_over_reference",
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
    """A non-live double that nests into itself forever.

    Carries an `operator` so it recurses through the reconstruction and IR-extraction
    entries too, not just the reference walk (audit M1).
    """

    operator = "+"
    name = "endless"

    @property
    def operands(self) -> tuple[Any, ...]:
        return (self,)


def test_depth_exhaustion_is_its_own_named_outcome() -> None:
    """Exhaustion raises `EXPRESSION_DEPTH_EXHAUSTED`; no partial result escapes."""
    module = _reference_use_module()
    with pytest.raises(SemanticEvidenceError) as caught:
        module.inspect_reference_uses(_EndlessOperator())
    assert caught.value.code is SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED


def test_the_shared_budget_covers_expression_ir_extraction() -> None:
    """Audit M1: `extract_expression_ir` raised a bare `RecursionError` on self-nesting.

    The design gives one budget to `inspect_reference_uses`, `extract_expression_ir`, and
    expression reconstruction alike.  A bare `RecursionError` is not the named failure, and
    a caller cannot tell it from an interpreter limit it caused some other way.
    """
    from agentic_mbse.sysml.constraint_extraction import extract_expression_ir

    with pytest.raises(SemanticEvidenceError) as caught:
        extract_expression_ir(_EndlessOperator())
    assert caught.value.code is SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED
    assert caught.value.operation == "extract_expression_ir"


def test_the_shared_budget_covers_expression_reconstruction() -> None:
    """Audit M1: `reconstruct_expression` raised a bare `RecursionError` on self-nesting."""
    from agentic_mbse.sysml.expression import reconstruct_expression

    with pytest.raises(SemanticEvidenceError) as caught:
        reconstruct_expression(_EndlessOperator())
    assert caught.value.code is SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED
    assert caught.value.operation == "reconstruct_expression"


def test_no_recursive_production_entry_reports_a_bare_recursion_error() -> None:
    """Every entry the design names shares one budget and one named outcome.

    Stated as a set rather than three separate assertions, because M1's defect was that two
    of the three entries were simply never wired up.
    """
    from agentic_mbse.sysml.constraint_extraction import extract_expression_ir
    from agentic_mbse.sysml.expression import reconstruct_expression, traverse_expression

    module = _reference_use_module()
    entries = (
        lambda node: module.inspect_reference_uses(node),
        lambda node: extract_expression_ir(node),
        lambda node: reconstruct_expression(node),
        lambda node: traverse_expression(node, lambda inner: None),
    )
    for entry in entries:
        with pytest.raises(SemanticEvidenceError) as caught:
            entry(_EndlessOperator())
        assert caught.value.code is SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED


def test_the_depth_budget_is_not_caller_selectable() -> None:
    """One shared limit; no consumer may widen or narrow it through the signature."""
    import inspect as _inspect

    module = _reference_use_module()
    from agentic_mbse.sysml.constraint_extraction import extract_expression_ir
    from agentic_mbse.sysml.expression import reconstruct_expression

    assert list(_inspect.signature(module.inspect_reference_uses).parameters) == ["expression"]
    assert isinstance(module.MAX_EXPRESSION_DEPTH, int)

    # No public entry offers a depth knob; the private counters are underscore-prefixed and
    # exist only so the recursion can carry its own position.
    for entry in (extract_expression_ir, reconstruct_expression):
        public = [
            name
            for name in _inspect.signature(entry).parameters
            if not name.startswith("_")
        ]
        assert not any("depth" in name for name in public), entry.__name__


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


def test_a_unit_annotation_never_emits_its_unit_operand(probe_expressions) -> None:
    """A structural unit annotation visits its value operand only.

    Audit m3: the unit operand was emitted as a reference use and then filtered downstream
    by document tier.  That works for `SI::metre` and fails for a project-scoped unit, which
    would arrive at a consumer as a design dependency.  The unit is not a data reference at
    all, so it is not emitted here — the tier filter is not what makes it disappear.
    """
    module = _reference_use_module()
    assert module.inspect_reference_uses(probe_expressions["unit_wrapped"]) == ()

    # The value operand is still visited: a reference inside one is real evidence.
    assert len(module.inspect_reference_uses(probe_expressions["unit_over_reference"])) == 1

    project = module.inspect_reference_uses(probe_expressions["scaled"])
    assert {use.path.leaf.document_tier for use in project} == {"Project"}


def test_a_project_scoped_unit_is_not_emitted_either() -> None:
    """The case that proves the fix is at the boundary and not in the tier filter.

    A project-scoped unit (`3.0 [MyUnits::widget]`) carries document tier `Project`, so
    under the old route it survived the standard-library filter and reached a consumer as a
    design dependency.  Now nothing emits it in the first place, whatever its tier.

    Measured at SysIDE 0.8.4: a user-declared unit is *not* accepted in a quantity
    expression — every form tried (`attribute def U :> UnitsAndScales::{Simple,Derived,
    Measurement}Unit`, and the same typings applied directly) fails to parse with
    "expected a measurement unit as the second argument".  So the authored form the audit
    names cannot be reached through a real model, and the test double below is the only way
    to exercise it.  The code path is the same one; only the tier differs from the live
    `SI::metre` case, which is exactly the difference under test.
    """
    module = _reference_use_module()
    unit = MockFeatureReferenceExpression(
        name="widget",
        qualified_name="MyUnits::widget",
        document_tier=get_syside().DocumentTier.Project,
    )
    annotation = MockOperatorExpression(
        operator="[", operands=[MockLiteralRational(value=3.0), unit]
    )

    # The unit really is project-scoped, so a tier filter would have let it through.
    assert (
        module.resolved_target_fact(module.resolved_referent(unit)).document_tier
        == "Project"
    )
    assert module.inspect_reference_uses(annotation) == ()

    # And the value operand is still visited, so this is a boundary rule and not a mute.
    over_reference = MockOperatorExpression(
        operator="[",
        operands=[
            MockFeatureReferenceExpression(name="scale", qualified_name="Probe::scale"),
            unit,
        ],
    )
    (use,) = module.inspect_reference_uses(over_reference)
    assert use.path.leaf.qualified_name == "Probe::scale"


def test_a_malformed_unit_annotation_is_refused_by_name() -> None:
    """Shape validation still happens; it just does not emit the unit as data."""
    module = _reference_use_module()
    with pytest.raises(SemanticEvidenceError) as caught:
        module.inspect_reference_uses(
            MockOperatorExpression(
                operator="[", operands=[MockLiteralRational(value=3.0)]
            )
        )
    assert caught.value.code is SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED


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

"""Tests for V2 false positive prevention.

Tests the _is_calc_output_reference() helper function and integration with
check_static_expressions() to verify false positives are prevented.

Layered verification approach:
1. document_url: Contains 'library/' → calc output, contains 'designs/' → NOT calc output
2. qualified_name: Parent path matches known calc def → calc output
3. owner kind: CalculationDefinition owner → calc output, PartUsage → NOT calc output
4. Conservative fallback: If all methods fail → assume calc output (backwards compatible)

Every signal now comes off the exact evidence the closed reference boundary captured, so
the helper takes an `ExactReferenceUse` rather than a rebuildable `ExpressionRef` carrying
a live parser element.
"""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from agentic_mbse.sysml.data_models import ResolvedTargetFact
from agentic_mbse.sysml.reference_use import ExactReferenceUse, ExactSemanticPath
from agentic_mbse.sysml.syside_adapter import get_syside
from agentic_mbse.sysml.types import ValidationCode
from agentic_mbse.validation.adr002 import (
    _is_calc_output_reference,
    check_static_expressions,
)


def _use(
    *,
    name: str = "output_val",
    qualified_name: str = "",
    document_url: str = "",
    owner_kind: str = "",
) -> ExactReferenceUse:
    """One exact reference use carrying exactly the evidence a case exercises."""
    fact = ResolvedTargetFact(
        element_id=uuid5(NAMESPACE_URL, qualified_name or name),
        owner_element_id=None,
        redefined_element_ids=(),
        qualified_name=qualified_name,
        element_kind="AttributeUsage",
        element_name=name,
        owner_qualified_name=qualified_name.rsplit("::", 1)[0] if "::" in qualified_name else "",
        owner_kind=owner_kind,
        document_url=document_url,
    )
    return ExactReferenceUse(
        path=ExactSemanticPath(
            root=fact, segments=(fact,), leaf=fact, resolved_member_names=()
        ),
        form="bare",
        authored_text=name,
        authored_segments=(name,),
        authored_qualifier=None,
        plural=False,
        location=None,
    )


class TestIsCalcOutputReference:
    """Tests for _is_calc_output_reference() helper function."""

    # =========================================================================
    # Method 1: document_path check (Primary)
    # =========================================================================

    def test_library_path_returns_true(self):
        """Primary check: document_path contains 'library/' → True.

        When a reference's document_path contains 'library/', it's definitively
        from a library calc definition, so it's a calc output.
        """
        ref = _use(
            qualified_name="V2TestLibrary::SimpleCalc::output_val",
            document_url="models/library/analyses/thermal_loads.sysml",
        )
        result = _is_calc_output_reference(ref, set())
        assert result is True

    def test_designs_path_returns_false(self):
        """Primary check: document_path contains 'designs/' → False.

        When a reference's document_path contains 'designs/', it's definitively
        from a design file, so it's NOT a calc output (even if name matches).
        """
        ref = _use(
            qualified_name="CATFMFERadialBuild::plasma_region::output_val",
            document_url="models/designs/catf_mfe/radial_build.sysml",
        )
        result = _is_calc_output_reference(ref, set())
        assert result is False

    # =========================================================================
    # Method 2: qualified_name pattern check (Secondary)
    # =========================================================================

    def test_matching_calc_def_qualified_name(self):
        """Secondary check: qualified_name parent matches calc def → True.

        When the parent path in qualified_name matches a known calc def,
        the reference is to that calc's output.
        """
        ref = _use(qualified_name="V2TestLibrary::SimpleCalc::output_val")
        calc_def_names = {"V2TestLibrary::SimpleCalc"}
        result = _is_calc_output_reference(ref, calc_def_names)
        assert result is True

    def test_non_matching_qualified_name(self):
        """Secondary check: qualified_name parent doesn't match calc def → falls through.

        When the parent path in qualified_name doesn't match any known calc def,
        the check falls through to the owner type check. With no element,
        it falls through to conservative True.
        """
        ref = _use(qualified_name="SomeOtherPackage::SomePart::output_val")
        calc_def_names = {"V2TestLibrary::SimpleCalc"}  # Doesn't include SomeOtherPackage
        result = _is_calc_output_reference(ref, calc_def_names)
        # Falls through to conservative True because no element for owner check
        assert result is True

    # =========================================================================
    # Fallthrough behavior
    # =========================================================================

    def test_no_doc_path_uses_qualified_name(self):
        """When document_path is None, falls through to qualified_name check.

        The layered approach means if document_path doesn't provide a definitive
        answer (None or doesn't contain library/ or designs/), we try qualified_name.
        """
        ref = _use(qualified_name="V2TestLibrary::SimpleCalc::output_val")
        calc_def_names = {"V2TestLibrary::SimpleCalc"}
        result = _is_calc_output_reference(ref, calc_def_names)
        assert result is True

    def test_empty_qualified_name_falls_through(self):
        """When qualified_name is empty or no ::, falls through to owner check.

        If qualified_name can't be parsed for parent path, we try owner type check.
        With no element, falls through to conservative True.
        """
        ref = _use()
        result = _is_calc_output_reference(ref, set())
        # Falls through all checks to conservative True
        assert result is True

    # =========================================================================
    # Method 3: owner type check (Tertiary)
    # =========================================================================

    def test_calc_def_owner_returns_true(self):
        """Tertiary check: owner is CalculationDefinition → True.

        When the reference element's owner is a CalculationDefinition,
        it's definitively a calc output.
        """
        ref = _use(owner_kind="CalculationDefinition")
        result = _is_calc_output_reference(ref, set())
        assert result is True

    def test_part_usage_owner_returns_false(self):
        """Tertiary check: owner is PartUsage → False (explicit negative).

        When the reference element's owner is a PartUsage, it's definitively
        NOT a calc output - it's a design attribute.
        """
        ref = _use(owner_kind="PartUsage")
        result = _is_calc_output_reference(ref, set())
        assert result is False

    # =========================================================================
    # Combined fallthrough scenarios
    # =========================================================================

    def test_full_fallthrough_to_part_usage_returns_false(self):
        """Combined: No doc_path + non-matching qualified_name + PartUsage owner → False.

        This tests the complete fallthrough path where:
        1. document_path is None (no primary signal)
        2. qualified_name doesn't match any calc def (no secondary signal)
        3. owner is PartUsage (tertiary gives definitive False)

        This is the real-world scenario for same-named design attributes.
        """
        ref = _use(
            qualified_name="V2FalsePositiveTest::test_part::output_val",
            owner_kind="PartUsage",
        )
        calc_def_names = {"V2TestLibrary::SimpleCalc"}  # Doesn't match
        result = _is_calc_output_reference(ref, calc_def_names)
        assert result is False

    # =========================================================================
    # Conservative fallback
    # =========================================================================

    def test_no_info_conservative_fallback(self):
        """Fallback: When all methods fail → True (conservative).

        If we can't determine definitively whether it's a calc output,
        we conservatively assume it is to maintain backwards compatibility.
        """
        ref = _use()
        result = _is_calc_output_reference(ref, set())
        assert result is True

    def test_exception_in_owner_check_falls_through(self):
        """When owner.isinstance() raises exception → conservative fallback.

        The owner kind is now captured evidence rather than a live `isinstance` call, so
        there is no exception to swallow: a reference whose owner kind was never resolved
        simply has no tertiary signal, and the conservative fallback applies.
        """
        ref = _use()
        result = _is_calc_output_reference(ref, set())
        assert result is True


# =============================================================================
# Integration Tests
# =============================================================================


class TestV2FalsePositiveIntegration:
    """Integration tests verifying false positives are prevented in real checks."""

    def test_v2_still_flags_actual_calc_output_refs(self):
        """Regression: V2 check still flags actual calc output references.

        Uses fixtures: library/simple_calc.sysml + v2_dynamic_expression.sysml
        The v2_dynamic_expression.sysml file has a real V2 violation where
        derived_value = my_calc.output_val * 0.95 references a calc output.
        """
        # Load library calc def and the violation file
        library_files = list(
            Path("tests/fixtures/adr002_violations/library").glob("*.sysml")
        )
        design_files = [
            Path("tests/fixtures/adr002_violations/v2_dynamic_expression.sysml")
        ]
        files = library_files + design_files
        model, _ = get_syside().try_load_model([str(f) for f in files])

        # Run V2 check
        issues = check_static_expressions(model)
        v2_issues = [i for i in issues if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION]

        # Should still detect the violation for derived_value
        assert len(v2_issues) >= 1, (
            f"Expected at least 1 V2 violation for actual calc output reference, "
            f"but got {len(v2_issues)}"
        )

        # Verify it's the expected violation
        derived_issues = [i for i in v2_issues if "derived_value" in i.element_name]
        assert len(derived_issues) >= 1, (
            f"Expected violation for 'derived_value', but got: "
            f"{[i.element_name for i in v2_issues]}"
        )

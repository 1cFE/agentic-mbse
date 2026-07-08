"""Tests for SysideAdapter."""
from pathlib import Path

import pytest

from agentic_mbse.sysml.syside_adapter import (
    EXCLUDED_CONSTRAINT_TYPES,
    DiagnosticSeverity,
    SysideAdapter,
    is_droppable_constraint,
)


class TestTypeMap:
    """Tests for TYPE_MAP completeness."""

    def test_type_map_has_core_types(self):
        """TYPE_MAP includes all core definition and usage types."""
        core_types = [
            "CalculationDefinition",
            "CalculationUsage",
            "AttributeUsage",
            "PartDefinition",
            "PartUsage",
        ]
        type_map = SysideAdapter._get_type_map()
        for type_name in core_types:
            assert type_name in type_map

    def test_type_map_has_expression_types(self):
        """TYPE_MAP includes expression types."""
        expr_types = [
            "FeatureChainExpression",
            "FeatureReferenceExpression",
            "OperatorExpression",
            "InvocationExpression",
            "LiteralInteger",
            "LiteralRational",
            "LiteralBoolean",
            "LiteralString",
            "LiteralInfinity",
            "NullExpression",
        ]
        type_map = SysideAdapter._get_type_map()
        for type_name in expr_types:
            assert type_name in type_map

    def test_type_map_has_relationship_types(self):
        """TYPE_MAP includes relationship types."""
        type_map = SysideAdapter._get_type_map()
        assert "FeatureTyping" in type_map


class TestIsInstance:
    """Tests for is_instance method."""

    def test_is_instance_with_mock_matching_name(self):
        """is_instance returns True for mocks with matching type name."""
        class MockCalculationDefinition:
            pass

        mock = MockCalculationDefinition()
        assert SysideAdapter.is_instance(mock, "CalculationDefinition")

    def test_is_instance_with_mock_non_matching_name(self):
        """is_instance returns False for mocks without matching type name."""
        class MockOtherThing:
            pass

        mock = MockOtherThing()
        assert not SysideAdapter.is_instance(mock, "CalculationDefinition")


class TestElementsOfType:
    """Tests for elements_of_type method."""

    def test_unknown_type_raises_value_error(self):
        """elements_of_type raises ValueError for unknown types (D6).

        Was KeyError before Item 4; unified to ValueError so both this method and
        is_instance fail the same loud way on an unmapped name.
        """
        with pytest.raises(ValueError, match="Unknown type name"):
            list(SysideAdapter.elements_of_type(None, "UnknownType"))

    def test_unknown_exclude_name_raises_value_error(self):
        """An unmapped name in ``exclude`` is loud, not a silent no-op (D6)."""
        with pytest.raises(ValueError, match="Unknown type name"):
            list(
                SysideAdapter.elements_of_type(
                    None, "ConstraintUsage", exclude=("NotARealType",)
                )
            )


class TestSourceLocation:
    """Tests for get_source_location method."""

    def test_source_location_with_no_document(self):
        """get_source_location returns None for elements without document."""
        class MockElement:
            document = None

        assert SysideAdapter.get_source_location(MockElement()) is None

    def test_source_location_with_document(self):
        """get_source_location extracts path and line."""
        class MockStartPoint:
            line = 41  # 0-indexed

        class MockCstNode:
            start_point = MockStartPoint()

        class MockDocument:
            url = "file:///path/to/model.sysml"

        class MockElement:
            document = MockDocument()
            cst_node = MockCstNode()

        result = SysideAdapter.get_source_location(MockElement())
        # URL stripping leaves some slashes, check line number and path ends correctly
        assert result is not None
        path, line = result
        assert path.endswith("/path/to/model.sysml")
        assert line == 42  # 1-indexed


class TestDiagnosticSeverity:
    """Tests for DiagnosticSeverity stub."""

    def test_diagnostic_severity_enum_values(self):
        """DiagnosticSeverity has expected enum values."""
        assert DiagnosticSeverity.Error == 1
        assert DiagnosticSeverity.Warning == 2
        assert DiagnosticSeverity.Information == 3
        assert DiagnosticSeverity.Hint == 4


class TestDocumentUrl:
    """Tests for get_document_url method."""

    def test_document_url_direct(self):
        """get_document_url returns URL from element's document."""
        class MockDocument:
            url = "file:///path/to/model.sysml"

        class MockElement:
            document = MockDocument()
            owner = None

        result = SysideAdapter.get_document_url(MockElement())
        assert result == "file:///path/to/model.sysml"

    def test_document_url_from_owner(self):
        """get_document_url traverses up ownership chain."""
        class MockDocument:
            url = "file:///owner/path.sysml"

        class MockOwner:
            document = MockDocument()
            owner = None

        class MockElement:
            document = None
            owner = MockOwner()

        result = SysideAdapter.get_document_url(MockElement())
        assert result == "file:///owner/path.sysml"

    def test_document_url_not_found(self):
        """get_document_url returns None when no document found."""
        class MockElement:
            document = None
            owner = None

        result = SysideAdapter.get_document_url(MockElement())
        assert result is None


# --- PIPELINE-TRUTH Item 4: subtype-aware enumeration + droppable policy ---
#
# These exercise the live syside path (license-gated, like TestTypeMap above).
# The fixture carries one of each shape the constraint decision table cares
# about: a plain ConstraintUsage (positive_cost), a RequirementUsage
# (widget_budget), and an AssertConstraintUsage (affordable).

_ITEM4_MODEL = (
    Path(__file__).parent / "fixtures" / "item4_subtype" / "constraints.sysml"
)


@pytest.fixture(scope="module")
def item4_model():
    """Load the Item-4 constraints fixture once for the module."""
    model, _diags = SysideAdapter.load_model([_ITEM4_MODEL])
    return model


class TestTypeMapItem4:
    """TYPE_MAP carries the three ConstraintUsage subtype names (D6)."""

    def test_type_map_has_constraint_subtypes(self):
        type_map = SysideAdapter._get_type_map()
        for name in (
            "AssertConstraintUsage",
            "RequirementUsage",
            "SatisfyRequirementUsage",
        ):
            assert name in type_map


class TestIsInstanceHardError:
    """is_instance raises on an unmapped name instead of a silent False (D6)."""

    def test_is_instance_raises_on_unmapped_name(self):
        class MockCalculationDefinition:
            pass

        with pytest.raises(ValueError, match="Unknown type name"):
            SysideAdapter.is_instance(MockCalculationDefinition(), "NotARealType")

    def test_is_instance_mock_path_survives_for_mapped_name(self):
        """A mapped name still resolves mocks by string match (gate is before it)."""
        class MockCalculationDefinition:
            pass

        assert SysideAdapter.is_instance(
            MockCalculationDefinition(), "CalculationDefinition"
        )


class TestSubtypeSweep:
    """include_subtypes and exclude on the ConstraintUsage sweep."""

    def test_include_subtypes_sweeps_assert(self, item4_model):
        exact = list(
            SysideAdapter.elements_of_type(item4_model, "ConstraintUsage")
        )
        swept = list(
            SysideAdapter.elements_of_type(
                item4_model, "ConstraintUsage", include_subtypes=True
            )
        )
        # Exact-type sees only the plain constraint; the sweep also sees the
        # assert (and the requirement subtype).
        exact_names = {e.name for e in exact}
        swept_names = {e.name for e in swept}
        assert exact_names == {"positive_cost"}
        assert {"positive_cost", "affordable", "widget_budget"} == swept_names
        assert any(
            SysideAdapter.is_instance(e, "AssertConstraintUsage") for e in swept
        )

    def test_exclude_drops_requirement_keeps_predicates(self, item4_model):
        kept = list(
            SysideAdapter.elements_of_type(
                item4_model,
                "ConstraintUsage",
                include_subtypes=True,
                exclude=EXCLUDED_CONSTRAINT_TYPES,
            )
        )
        kept_names = {e.name for e in kept}
        # Requirement excluded; assert + plain predicate kept.
        assert kept_names == {"positive_cost", "affordable"}


class TestIsDroppableConstraint:
    """The single droppable-policy predicate (INV-D)."""

    def test_droppable_excludes_requirement_includes_predicates(self, item4_model):
        swept = list(
            SysideAdapter.elements_of_type(
                item4_model, "ConstraintUsage", include_subtypes=True
            )
        )
        by_name = {e.name: e for e in swept}
        assert is_droppable_constraint(by_name["affordable"])
        assert is_droppable_constraint(by_name["positive_cost"])
        assert not is_droppable_constraint(by_name["widget_budget"])

    def test_droppable_matches_exclude_filter(self, item4_model):
        """ladder-droppable == helper-droppable (INV-D cross-check)."""
        swept = list(
            SysideAdapter.elements_of_type(
                item4_model, "ConstraintUsage", include_subtypes=True
            )
        )
        via_helper = {e.name for e in swept if is_droppable_constraint(e)}
        via_exclude = {
            e.name
            for e in SysideAdapter.elements_of_type(
                item4_model,
                "ConstraintUsage",
                include_subtypes=True,
                exclude=EXCLUDED_CONSTRAINT_TYPES,
            )
        }
        assert via_helper == via_exclude

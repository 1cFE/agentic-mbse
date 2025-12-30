"""Tests for SysideAdapter."""
import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter, DiagnosticSeverity


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

    def test_unknown_type_raises_key_error(self):
        """elements_of_type raises KeyError for unknown types."""
        with pytest.raises(KeyError) as exc_info:
            list(SysideAdapter.elements_of_type(None, "UnknownType"))
        assert "Unknown type" in str(exc_info.value)


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

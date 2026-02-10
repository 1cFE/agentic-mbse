"""Tests for helpers.py functions."""

from pathlib import Path

from agentic_mbse.sysml.helpers import (
    get_calc_def_name,
    get_document_url,
    get_parent_part_name,
    get_source_file,
    get_source_location,
)


class MockFeatureTyping:
    """Mock FeatureTyping relationship."""

    pass


class MockPartUsage:
    """Mock PartUsage element."""

    def __init__(self, name=None):
        self.name = name


class MockDocument:
    """Mock document object."""

    def __init__(self, url=None):
        self.url = url


class MockCstNode:
    """Mock CST node with start point."""

    class StartPoint:
        def __init__(self, line):
            self.line = line

    def __init__(self, line=0):
        self.start_point = self.StartPoint(line)


class TestGetCalcDefName:
    """Tests for get_calc_def_name function."""

    def test_returns_none_without_heritage(self):
        """Returns None if element has no heritage."""

        class MockElement:
            pass

        assert get_calc_def_name(MockElement()) is None

    def test_returns_none_with_empty_heritage(self):
        """Returns None if heritage is empty."""

        class MockElement:
            heritage = []

        assert get_calc_def_name(MockElement()) is None

    def test_returns_target_name_with_feature_typing(self):
        """Returns target name when FeatureTyping relationship exists."""

        class MockTarget:
            name = "MyCalcDef"

        class MockElement:
            heritage = [(MockFeatureTyping(), MockTarget())]

        assert get_calc_def_name(MockElement()) == "MyCalcDef"

    def test_returns_none_when_target_has_no_name(self):
        """Returns None if target has no name attribute."""

        class MockTarget:
            pass

        class MockElement:
            heritage = [(MockFeatureTyping(), MockTarget())]

        assert get_calc_def_name(MockElement()) is None


class TestGetDocumentUrl:
    """Tests for get_document_url function."""

    def test_returns_url_from_element_document(self):
        """Returns URL directly from element's document."""

        class MockElement:
            document = MockDocument("file:///path/to/file.sysml")

        assert get_document_url(MockElement()) == "file:///path/to/file.sysml"

    def test_returns_none_without_document(self):
        """Returns None if no document found."""

        class MockElement:
            document = None
            owner = None

        assert get_document_url(MockElement()) is None

    def test_traverses_ownership_chain(self):
        """Traverses up ownership chain to find document."""

        class MockOwner:
            document = MockDocument("file:///parent.sysml")
            owner = None

        class MockElement:
            document = None
            owner = MockOwner()

        assert get_document_url(MockElement()) == "file:///parent.sysml"


class TestGetSourceFile:
    """Tests for get_source_file function."""

    def test_returns_path_from_document_url(self):
        """Extracts Path from document URL."""

        class MockElement:
            document = MockDocument("file:///path/to/model.sysml")
            owner = None

        result = get_source_file(MockElement())
        assert result == Path("/path/to/model.sysml")

    def test_returns_unknown_without_document(self):
        """Returns Path('unknown') if no document."""

        class MockElement:
            document = None
            owner = None

        assert get_source_file(MockElement()) == Path("unknown")

    def test_strips_file_prefix(self):
        """Strips 'file:' prefix from URL."""

        class MockElement:
            document = MockDocument("file:models/test.sysml")
            owner = None

        result = get_source_file(MockElement())
        assert "file:" not in str(result)


class TestGetSourceLocation:
    """Tests for get_source_location function."""

    def test_returns_path_and_line(self):
        """Returns tuple of (path, line_number)."""

        class MockElement:
            document = MockDocument("file:///path/to/model.sysml")
            owner = None
            cst_node = MockCstNode(line=41)  # 0-indexed

        path, line = get_source_location(MockElement())
        assert path == Path("/path/to/model.sysml")
        assert line == 42  # 1-indexed

    def test_returns_line_zero_without_cst_node(self):
        """Returns line 0 if no CST node."""

        class MockElement:
            document = MockDocument("file:///path.sysml")
            owner = None

        path, line = get_source_location(MockElement())
        assert line == 0


class TestGetParentPartName:
    """Tests for get_parent_part_name function."""

    def test_returns_empty_string_without_namespace(self):
        """Returns empty string if no owning_namespace."""

        class MockElement:
            owning_namespace = None

        # Remove owner to avoid fallback
        elem = MockElement()
        assert get_parent_part_name(elem) == ""

    def test_returns_part_name_from_namespace(self):
        """Returns part name from owning_namespace."""

        class MockElement:
            owning_namespace = MockPartUsage("my_part")

        assert get_parent_part_name(MockElement()) == "my_part"

    def test_returns_empty_when_namespace_has_no_name(self):
        """Returns empty string if part has no name."""

        class MockElement:
            owning_namespace = MockPartUsage(None)

        elem = MockElement()
        assert get_parent_part_name(elem) == ""

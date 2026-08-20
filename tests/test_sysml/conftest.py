"""Shared fixtures for sysml_utils tests.

Provides mock SysML AST elements that simulate syside behavior
without requiring actual SysML parsing.

CRITICAL: Mock classes must implement isinstance() method that takes
a class and returns True if the mock's type matches. This matches
syside's element.isinstance(syside.TypeName) pattern.
"""

from typing import Any
from uuid import NAMESPACE_URL, uuid5

import pytest

from agentic_mbse.sysml.syside_adapter import get_syside


def _mock_document(url: str, tier: Any = None) -> Any:
    if tier is None:
        tier = get_syside().DocumentTier.Project
    return type("MockDocument", (), {"url": url, "document_tier": tier})()


class MockElement:
    """Base mock for syside elements with isinstance support.

    Syside elements use element.isinstance(syside.TypeName) pattern,
    not Python's isinstance(element, TypeName). We simulate this.
    """

    def __init__(
        self, name: str = "", qualified_name: str = "", doc_path: str = ""
    ) -> None:
        self.name = name
        self.qualified_name = qualified_name
        # Real elements carry a stable declaration id, and the closed reference boundary
        # records it as evidence, so a double that omits it is not modelling the shape.
        self.element_id = uuid5(NAMESPACE_URL, f"{qualified_name or name}")
        self._doc_path = doc_path
        self._type_name = self.__class__.__name__

    def isinstance(self, cls: type) -> bool:
        """Simulate syside's isinstance method.

        Matches if the class name is contained in this element's type name.
        Supports both class objects and mock type checking.
        """
        cls_name = cls.__name__ if hasattr(cls, "__name__") else str(cls)
        # Handle mock class names (e.g., MockFeatureReferenceExpression)
        # Remove "Mock" prefix for comparison
        self_type = self._type_name.replace("Mock", "")
        target_type = cls_name.replace("Mock", "")
        return target_type in self_type or self._type_name == cls_name


class MockMembership:
    """Mock for syside Membership element."""

    def __init__(self, member_element: Any = None) -> None:
        self.member_element = member_element


class MockFeatureReferenceExpression(MockElement):
    """Mock for syside FeatureReferenceExpression.

    Represents a simple attribute reference like `volume`.
    """

    def __init__(
        self,
        name: str = "",
        qualified_name: str = "",
        doc_path: str = "",
        target_element: Any = None,
        document_tier: Any = None,
    ) -> None:
        super().__init__(name, qualified_name, doc_path)
        # Match the real SysIDE shape: ``referent`` is the identity authority.
        if target_element:
            target = target_element
        else:
            # Every named SysIDE element carries a qualified name; a double that omits
            # one is under-specified, not a model of a nameless reference.
            target = MockElement(name=name, qualified_name=qualified_name or name or None)
            target.document = _mock_document(doc_path, document_tier)
        self.referent = target
        self.memberships = [MockMembership(target)]


class MockFeatureChainExpression(MockElement):
    """Mock for syside FeatureChainExpression.

    Represents a chained reference like `instance.attribute`.
    """

    def __init__(
        self,
        instance_name: str = "",
        attr_name: str = "",
        qualified_name: str = "",
        doc_path: str = "",
        document_tier: Any = None,
    ) -> None:
        # The name is typically the attribute name
        super().__init__(name=attr_name, qualified_name=qualified_name, doc_path=doc_path)
        self.instance_name = instance_name
        self.attr_name = attr_name

        # Model the real syside FeatureChainExpression shape: operands[0] is the
        # chain-root expression and target_feature carries the terminal feature.
        # Production helpers read only these (plus memberships) — never
        # instance_name/attr_name, which are mock-constructor conveniences.
        if instance_name:
            self.operands = [MockFeatureReferenceExpression(name=instance_name)]
        if attr_name:
            self.target_feature = type(
                "TargetFeature",
                (),
                {
                    "name": attr_name,
                    "qualified_name": qualified_name or attr_name or None,
                    "element_id": uuid5(NAMESPACE_URL, qualified_name or attr_name),
                    "document": _mock_document(doc_path, document_tier),
                },
            )()

        # Create target for the attribute
        target = MockElement(name=attr_name, qualified_name=qualified_name)
        target.document = type("Doc", (), {"url": doc_path})() if doc_path else None
        self.memberships = [MockMembership(target)]


class MockOperatorExpression(MockElement):
    """Mock for syside OperatorExpression.

    Represents an arithmetic expression like `a + b`.
    """

    def __init__(self, operator: str = "", operands: list[Any] | None = None) -> None:
        super().__init__()
        self.operator = operator
        self.operands = operands if operands is not None else []


class MockLiteralRational(MockElement):
    """Mock for syside LiteralRational.

    Represents a floating-point constant like `42.0`.
    """

    def __init__(self, value: float = 0.0) -> None:
        super().__init__()
        self.value = value


class MockLiteralInteger(MockElement):
    """Mock for syside LiteralInteger.

    Represents an integer constant like `42`.
    """

    def __init__(self, value: int = 0) -> None:
        super().__init__()
        self.value = value


class MockDocument:
    """Mock syside Document with URL.

    Represents the document (file) containing a SysML element.
    Used for cross-file reference detection.
    """

    def __init__(self, url: str = "") -> None:
        self.url = url


class MockMember(MockElement):
    """Mock for AttributeUsage/ReferenceUsage member in calc usage.

    Represents a parameter binding in a CalculationUsage element.
    Each member has a name (param name) and optional feature_value_expression
    (the binding expression).
    """

    def __init__(
        self,
        name: str = "",
        feature_value_expression: Any = None,
    ) -> None:
        super().__init__(name=name)
        self.feature_value_expression = feature_value_expression
        self._supported_types = ["AttributeUsage", "ReferenceUsage"]

    def isinstance(self, cls: type) -> bool:
        """Check if this mock matches AttributeUsage or ReferenceUsage."""
        cls_name = cls.__name__ if hasattr(cls, "__name__") else str(cls)
        return cls_name in self._supported_types or super().isinstance(cls)


class MockCalculationUsage(MockElement):
    """Mock for syside CalculationUsage.

    Represents a calculation usage element with its parameters
    and the calculation definition it instantiates.
    """

    def __init__(
        self,
        name: str = "",
        calc_def_name: str = "",
        doc_path: str = "",
        owned_members: list[Any] | None = None,
    ) -> None:
        super().__init__(name=name, doc_path=doc_path)
        self.owned_members = owned_members if owned_members is not None else []
        self.document = MockDocument(doc_path)

        # Mock calculation_definition with name attribute
        self.calculation_definition = MockElement(name=calc_def_name)


# Factory functions for calc usages


def create_mock_calc_usage_with_chain_binding(
    param_name: str,
    source_instance: str,
    source_attr: str,
    usage_file: str = "physics.sysml",
) -> MockCalculationUsage:
    """Create calc usage with a chain binding (instance.attribute).

    Args:
        param_name: Name of the parameter being bound
        source_instance: Name of the source instance
        source_attr: Name of the attribute on the source instance
        usage_file: File path for the calc usage

    Returns:
        MockCalculationUsage with one chain-bound parameter
    """
    chain_expr = MockFeatureChainExpression(
        instance_name=source_instance,
        attr_name=source_attr,
        doc_path=usage_file,  # Same file by default
    )

    member = MockMember(name=param_name, feature_value_expression=chain_expr)

    return MockCalculationUsage(
        name="test_calc",
        calc_def_name="TestCalcDef",
        doc_path=usage_file,
        owned_members=[member],
    )


def create_mock_calc_usage_with_literal_binding(
    param_name: str,
    value: float | int,
    usage_file: str = "physics.sysml",
) -> MockCalculationUsage:
    """Create calc usage with a literal binding (constant value).

    Args:
        param_name: Name of the parameter being bound
        value: Literal value for the binding
        usage_file: File path for the calc usage

    Returns:
        MockCalculationUsage with one literal-bound parameter
    """
    if isinstance(value, int) and not isinstance(value, bool):
        literal_expr = MockLiteralInteger(value=value)
    else:
        literal_expr = MockLiteralRational(value=float(value))

    member = MockMember(name=param_name, feature_value_expression=literal_expr)

    return MockCalculationUsage(
        name="test_calc",
        calc_def_name="TestCalcDef",
        doc_path=usage_file,
        owned_members=[member],
    )


def create_mock_calc_usage_with_expression_binding(
    param_name: str,
    refs: list[str],
    usage_file: str = "physics.sysml",
) -> MockCalculationUsage:
    """Create calc usage with an expression binding (arithmetic).

    Args:
        param_name: Name of the parameter being bound
        refs: List of reference names in the expression
        usage_file: File path for the calc usage

    Returns:
        MockCalculationUsage with one expression-bound parameter
    """
    operands = [
        MockFeatureReferenceExpression(name=ref, doc_path=usage_file) for ref in refs
    ]
    expr = MockOperatorExpression(operator="+", operands=operands)

    member = MockMember(name=param_name, feature_value_expression=expr)

    return MockCalculationUsage(
        name="test_calc",
        calc_def_name="TestCalcDef",
        doc_path=usage_file,
        owned_members=[member],
    )


def create_mock_calc_usage_with_no_binding(
    param_name: str,
    usage_file: str = "physics.sysml",
) -> MockCalculationUsage:
    """Create calc usage with an unbound parameter.

    Args:
        param_name: Name of the parameter (no binding)
        usage_file: File path for the calc usage

    Returns:
        MockCalculationUsage with one unbound parameter
    """
    member = MockMember(name=param_name, feature_value_expression=None)

    return MockCalculationUsage(
        name="test_calc",
        calc_def_name="TestCalcDef",
        doc_path=usage_file,
        owned_members=[member],
    )


def create_mock_calc_usage_with_cross_file_binding(
    param_name: str,
    usage_file: str,
    source_file: str,
) -> MockCalculationUsage:
    """Create calc usage with a cross-file chain binding.

    Args:
        param_name: Name of the parameter being bound
        usage_file: File path for the calc usage
        source_file: File path for the source element (different from usage_file)

    Returns:
        MockCalculationUsage with one cross-file bound parameter
    """
    # Chain expression points to element in different file
    chain_expr = MockFeatureChainExpression(
        instance_name="remote_part",
        attr_name=param_name,
        doc_path=source_file,  # Different from usage_file
    )

    member = MockMember(name=param_name, feature_value_expression=chain_expr)

    return MockCalculationUsage(
        name="test_calc",
        calc_def_name="TestCalcDef",
        doc_path=usage_file,
        owned_members=[member],
    )


# Pytest fixtures


@pytest.fixture
def mock_feature_ref():
    """Factory fixture for creating MockFeatureReferenceExpression."""

    def _factory(
        name: str = "",
        qualified_name: str = "",
        doc_path: str = "",
    ) -> MockFeatureReferenceExpression:
        return MockFeatureReferenceExpression(
            name=name,
            qualified_name=qualified_name,
            doc_path=doc_path,
        )

    return _factory


@pytest.fixture
def mock_operator_expr():
    """Factory fixture for creating MockOperatorExpression."""

    def _factory(
        operator: str = "",
        operands: list[Any] | None = None,
    ) -> MockOperatorExpression:
        return MockOperatorExpression(operator=operator, operands=operands)

    return _factory


@pytest.fixture
def mock_literal():
    """Factory fixture for creating MockLiteralRational."""

    def _factory(value: float = 0.0) -> MockLiteralRational:
        return MockLiteralRational(value=value)

    return _factory


@pytest.fixture
def mock_chain_expr():
    """Factory fixture for creating MockFeatureChainExpression."""

    def _factory(
        instance_name: str = "",
        attr_name: str = "",
        qualified_name: str = "",
        doc_path: str = "",
    ) -> MockFeatureChainExpression:
        return MockFeatureChainExpression(
            instance_name=instance_name,
            attr_name=attr_name,
            qualified_name=qualified_name,
            doc_path=doc_path,
        )

    return _factory

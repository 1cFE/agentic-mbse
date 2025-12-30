"""Tests for error classes."""
import pytest
from agentic_mbse.errors import (
    AgenticMBSEError,
    ModelLoadError,
    ValidationError,
    ConfigurationError,
    AdapterError,
)


class TestAgenticMBSEError:
    """Tests for base error class."""

    def test_is_exception(self):
        """AgenticMBSEError is a proper exception."""
        err = AgenticMBSEError("test message")
        assert isinstance(err, Exception)
        assert str(err) == "test message"

    def test_can_be_raised_and_caught(self):
        """Can raise and catch the error."""
        with pytest.raises(AgenticMBSEError):
            raise AgenticMBSEError("test")


class TestModelLoadError:
    """Tests for ModelLoadError."""

    def test_stores_path_and_reason(self):
        """Stores path and reason attributes."""
        err = ModelLoadError("/path/to/model", "file not found")
        assert err.path == "/path/to/model"
        assert err.reason == "file not found"

    def test_message_format(self):
        """Message includes path and reason."""
        err = ModelLoadError("/path/to/model", "file not found")
        assert "/path/to/model" in str(err)
        assert "file not found" in str(err)

    def test_is_agentic_mbse_error(self):
        """Inherits from AgenticMBSEError."""
        err = ModelLoadError("/path", "reason")
        assert isinstance(err, AgenticMBSEError)


class TestValidationError:
    """Tests for ValidationError."""

    def test_stores_level(self):
        """Stores validation level."""
        err = ValidationError(3, "dataflow issue")
        assert err.level == 3

    def test_message_format(self):
        """Message includes level and message."""
        err = ValidationError(3, "dataflow issue")
        assert "Level 3" in str(err)
        assert "dataflow issue" in str(err)

    def test_is_agentic_mbse_error(self):
        """Inherits from AgenticMBSEError."""
        err = ValidationError(1, "message")
        assert isinstance(err, AgenticMBSEError)


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_stores_config_path(self):
        """Stores config_path attribute."""
        err = ConfigurationError("/path/to/config.yaml", "invalid format")
        assert err.config_path == "/path/to/config.yaml"

    def test_message_format(self):
        """Message includes config path and message."""
        err = ConfigurationError("/path/to/config.yaml", "invalid format")
        assert "/path/to/config.yaml" in str(err)
        assert "invalid format" in str(err)

    def test_is_agentic_mbse_error(self):
        """Inherits from AgenticMBSEError."""
        err = ConfigurationError("/path", "message")
        assert isinstance(err, AgenticMBSEError)


class TestAdapterError:
    """Tests for AdapterError."""

    def test_stores_operation(self):
        """Stores operation attribute."""
        err = AdapterError("load_model", "syside not available")
        assert err.operation == "load_model"

    def test_message_format(self):
        """Message includes operation and message."""
        err = AdapterError("load_model", "syside not available")
        assert "load_model" in str(err)
        assert "syside not available" in str(err)

    def test_is_agentic_mbse_error(self):
        """Inherits from AgenticMBSEError."""
        err = AdapterError("operation", "message")
        assert isinstance(err, AgenticMBSEError)

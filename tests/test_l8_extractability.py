"""
Tests for Level 8: Design Attribute Extractability Validation (FR-8).

Verifies that codegen can extract numeric defaults from design attribute
expressions, and that the configurable path filter works correctly.
"""

from pathlib import Path

import pytest

from agentic_mbse.sysml.types import Severity, ValidationCode
from agentic_mbse.validation.common import discover_sysml_files, load_sysml_model
from agentic_mbse.validation.level8_codegen import (
    check_design_attr_completeness,
    validate_codegen_readiness,
)

FIXTURE_DIR = str(Path(__file__).parent / "fixtures" / "l8_extractability")
DESIGNS_DIR = str(Path(__file__).parent / "fixtures" / "l8_extractability" / "designs")
SAMPLE_MODELS_DIR = str(Path(__file__).parent / "fixtures" / "sample_models")


@pytest.fixture
def valid_model():
    """Load only the valid design fixture."""
    files = discover_sysml_files(DESIGNS_DIR)
    valid_files = [f for f in files if "valid_design" in f.name]
    model, _ = load_sysml_model(valid_files)
    return model


@pytest.fixture
def unextractable_model():
    """Load only the unextractable design fixture."""
    files = discover_sysml_files(DESIGNS_DIR)
    unextractable_files = [f for f in files if "unextractable" in f.name]
    model, _ = load_sysml_model(unextractable_files)
    return model


class TestExtractabilityValidation:
    """Tests for FR-8: design attribute extractability."""

    def test_valid_design_passes_extractability(self, valid_model):
        """Literal defaults (10.0, 5.0) should produce no UNEXTRACTABLE issues."""
        issues, count = check_design_attr_completeness(
            valid_model, design_path_filter="designs"
        )
        unextractable = [
            i for i in issues if i.code == ValidationCode.L8_DESIGN_ATTR_UNEXTRACTABLE
        ]
        assert count > 0, "Expected at least one design attr to be checked"
        assert len(unextractable) == 0, (
            f"Valid literals should not produce UNEXTRACTABLE issues: {unextractable}"
        )

    def test_unextractable_design_produces_error(self, unextractable_model):
        """area = length * width should produce UNEXTRACTABLE ERROR issues."""
        issues, count = check_design_attr_completeness(
            unextractable_model, design_path_filter="designs"
        )
        unextractable = [
            i for i in issues if i.code == ValidationCode.L8_DESIGN_ATTR_UNEXTRACTABLE
        ]
        assert len(unextractable) > 0, "Expected UNEXTRACTABLE issues for area = length * width"
        for issue in unextractable:
            assert issue.severity == Severity.ERROR
            assert "area" in issue.element_name.lower() or "area" in issue.message.lower()


class TestPathFilter:
    """Tests for configurable design_path_filter."""

    def test_default_filter_skips_non_designs_directory(self):
        """Default filter='designs' should skip files in tests/ directory."""
        result = validate_codegen_readiness(FIXTURE_DIR, design_path_filter="designs")
        # The tests/test_design.sysml has 4 attrs — if filter works,
        # count should reflect only designs/ files
        # With both design files loaded: 10 attrs from designs/
        assert result.metrics["Design attrs checked"] == 10

    def test_custom_filter_checks_tests_directory(self):
        """filter='tests' should check only files in tests/ directory."""
        result = validate_codegen_readiness(FIXTURE_DIR, design_path_filter="tests")
        assert result.metrics["Design attrs checked"] > 0

    def test_empty_filter_checks_all_files(self):
        """filter='' should check all files regardless of directory."""
        result = validate_codegen_readiness(FIXTURE_DIR, design_path_filter="")
        assert result.metrics["Design attrs checked"] > 0
        # Should be more than designs-only
        designs_result = validate_codegen_readiness(FIXTURE_DIR, design_path_filter="designs")
        assert result.metrics["Design attrs checked"] > designs_result.metrics["Design attrs checked"]

    def test_none_filter_checks_all_files(self):
        """filter=None should check all files regardless of directory."""
        result = validate_codegen_readiness(FIXTURE_DIR, design_path_filter=None)
        assert result.metrics["Design attrs checked"] > 0
        designs_result = validate_codegen_readiness(FIXTURE_DIR, design_path_filter="designs")
        assert result.metrics["Design attrs checked"] > designs_result.metrics["Design attrs checked"]


class TestMetricsAndRegression:
    """Tests for metrics reporting and backward compatibility."""

    def test_metrics_include_unextractable_count(self):
        """Metrics should include L8_DESIGN_ATTR_UNEXTRACTABLE count."""
        result = validate_codegen_readiness(DESIGNS_DIR, design_path_filter="designs")
        assert "L8_DESIGN_ATTR_UNEXTRACTABLE" in result.metrics
        assert result.metrics["L8_DESIGN_ATTR_UNEXTRACTABLE"] > 0

    def test_existing_l8_behavior_preserved(self):
        """Existing L8 checks on sample_models/ should still work."""
        result = validate_codegen_readiness(SAMPLE_MODELS_DIR)
        # sample_models has no designs/ dir, so design attr count should be 0
        assert "Design attrs checked" in result.metrics
        assert "L8_DESIGN_ATTR_UNEXTRACTABLE" in result.metrics

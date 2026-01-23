"""Example model regression tests.

This file demonstrates how to write pytest-compatible tests that validate
SysML models using the syside library. Tests in tests/models/ verify that
library definition changes don't break existing designs.

Key Pattern:
- Use get_syside().try_load_model() for robustness (tolerates parse errors)
- Load library files AND design files together to test integration
- Use pytest.skip() for optional tests when directories don't exist

Usage:
    pytest tests/models/          # Run all model tests
    pytest tests/models/ -v       # Verbose output
    pytest tests/models/ -k "library"  # Run specific tests
"""
import pytest
from pathlib import Path

# Import syside via the adapter (handles lazy loading and license)
from agentic_mbse.sysml.syside_adapter import get_syside

# Path to models directory (relative to tests/models/)
MODELS_DIR = Path(__file__).parent.parent.parent / "models"


# ============================================================================
# Fixtures - Reusable model loading
# ============================================================================


@pytest.fixture
def library_model():
    """Load all library definitions."""
    library_path = MODELS_DIR / "library"
    if not library_path.exists():
        pytest.skip("No library/ directory found")

    files = list(library_path.glob("**/*.sysml"))
    if not files:
        pytest.skip("No .sysml files in library/")

    model, diagnostics = get_syside().try_load_model([str(f) for f in files])
    return model, diagnostics


@pytest.fixture
def full_model():
    """Load library AND designs together for integration testing."""
    files = list(MODELS_DIR.glob("**/*.sysml"))
    if not files:
        pytest.skip("No .sysml files found in models/")

    model, diagnostics = get_syside().try_load_model([str(f) for f in files])
    return model, diagnostics


# ============================================================================
# Parsing Tests - Verify models parse without errors
# ============================================================================


class TestModelParsing:
    """Basic tests verifying models parse without syntax errors."""

    def test_library_parses_without_errors(self, library_model):
        """Verify library definitions parse successfully.

        A failing test here means library files have syntax errors.
        """
        model, diagnostics = library_model
        syside = get_syside()

        # Check for parse errors (not warnings) - use diagnostics.parser for syntax errors
        errors = [d for d in diagnostics.parser if d.severity == syside.DiagnosticSeverity.Error]

        assert len(errors) == 0, f"Library has {len(errors)} parse errors: {errors}"

    def test_full_model_parses_without_errors(self, full_model):
        """Verify all models (library + designs) parse successfully.

        A failing test here indicates integration issues between
        library definitions and design usages.
        """
        model, diagnostics = full_model
        syside = get_syside()

        # Check parser diagnostics for syntax errors
        errors = [d for d in diagnostics.parser if d.severity == syside.DiagnosticSeverity.Error]

        assert len(errors) == 0, f"Model has {len(errors)} parse errors: {errors}"


# ============================================================================
# Structure Tests - Verify expected elements exist
# ============================================================================


class TestModelStructure:
    """Tests verifying expected model elements exist.

    Customize these tests for your specific model requirements.
    When library definitions change, these tests catch breaking changes.
    """

    def test_example_definition_exists(self, library_model):
        """Example: Verify a specific definition exists in library.

        Replace 'ExampleDef' with actual definition names from your model.
        This pattern catches accidental deletion or renaming.
        """
        model, _ = library_model
        pytest.skip("Customize this test with your actual definition names")

        # Example pattern:
        # syside = get_syside()
        # part_defs = list(model.elements(syside.PartDefinition))
        # names = [p.name for p in part_defs if p.name]
        # assert "Motor" in names, "Motor definition missing from library"


# ============================================================================
# Integration Tests - Verify designs use library correctly
# ============================================================================


class TestDesignIntegration:
    """Tests verifying designs correctly reference library definitions.

    These are the critical regression tests: when you change a library
    definition, these tests verify existing designs still work.
    """

    def test_design_references_resolve(self, full_model):
        """Verify design usages can resolve their library definitions.

        Unresolved references indicate breaking changes to library APIs.
        """
        model, diagnostics = full_model
        syside = get_syside()

        # Check semantic diagnostics for reference errors
        # diagnostics.sema contains semantic analysis results including unresolved references
        unresolved = [
            d for d in diagnostics.sema
            if "unresolved" in str(d.message).lower()
            or "reference-error" in str(getattr(d, 'code', '')).lower()
            or "not found" in str(d.message).lower()
        ]

        assert len(unresolved) == 0, (
            f"Found {len(unresolved)} unresolved references - "
            "library changes may have broken designs"
        )

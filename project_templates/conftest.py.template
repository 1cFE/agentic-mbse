"""Pytest configuration and fixtures for model testing.

This file provides common fixtures used across all model tests.
Place in tests/ to make fixtures available to tests/models/*.
"""
import pytest
from pathlib import Path


@pytest.fixture
def models_dir():
    """Path to the models directory."""
    return Path(__file__).parent.parent / "models"


@pytest.fixture
def load_sysml():
    """Factory fixture for loading SysML models.

    Usage in tests:
        def test_my_model(load_sysml, models_dir):
            model, diagnostics = load_sysml(models_dir / "library")
            assert model is not None
    """
    from agentic_mbse.sysml.syside_adapter import get_syside

    def _load(path: Path | str):
        """Load SysML model from path (file or directory).

        Args:
            path: Single file or directory to load

        Returns:
            (model, diagnostics) tuple
        """
        path = Path(path)
        if path.is_dir():
            files = list(path.glob("**/*.sysml"))
        else:
            files = [path]

        return get_syside().try_load_model([str(f) for f in files])

    return _load

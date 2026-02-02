"""Shared pytest fixtures."""
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load environment variables (for SYSIDE_LICENSE_KEY)
load_dotenv()


@pytest.fixture
def sample_models_path():
    """Path to sample model fixtures."""
    return Path(__file__).parent / "fixtures" / "sample_models"


@pytest.fixture
def valid_model_path(sample_models_path):
    """Path to valid model for testing."""
    return sample_models_path / "valid_calc_def.sysml"


@pytest.fixture
def valid_calc_usage_path(sample_models_path):
    """Path to valid calc usage model."""
    return sample_models_path / "valid_calc_usage.sysml"


@pytest.fixture
def syntax_error_path(sample_models_path):
    """Path to model with syntax errors."""
    return sample_models_path / "syntax_error.sysml"


@pytest.fixture
def circular_import_path(sample_models_path):
    """Path to model with circular imports."""
    return sample_models_path / "circular_import.sysml"

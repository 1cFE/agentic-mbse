"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from typing import Any

import pytest

from doc_ingest.cli import create_pipeline


def pytest_addoption(parser: Any) -> None:
    """Add custom command-line options to pytest."""
    parser.addoption(
        "--run-corpus",
        action="store_true",
        default=False,
        help="run corpus tests (slow, requires test PDFs)",
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests (requires network access)",
    )


def pytest_configure(config: Any) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "corpus: marks tests as corpus tests (run with --run-corpus)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (run with --run-integration)"
    )


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """Skip corpus and integration tests unless appropriate flags are provided."""
    run_corpus = config.getoption("--run-corpus", default=False)
    run_integration = config.getoption("--run-integration", default=False)

    skip_corpus = pytest.mark.skip(reason="need --run-corpus option to run")
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")

    for item in items:
        if "corpus" in item.keywords and not run_corpus:
            item.add_marker(skip_corpus)
        if "integration" in item.keywords and not run_integration:
            item.add_marker(skip_integration)


@pytest.fixture
def integration_pipeline():
    """Create real pipeline for integration tests.

    Returns:
        Tuple of (SourceRouter, ResultWriter) configured with temporary directories
        for output and cache.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        cache_dir = Path(tmpdir) / "cache"
        cache_dir.mkdir()

        router, writer = create_pipeline(output_dir=output_dir, cache_dir=cache_dir)
        yield router, writer

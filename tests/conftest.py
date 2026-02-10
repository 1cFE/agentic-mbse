"""Pytest configuration and fixtures."""

from typing import Any

import pytest


def pytest_addoption(parser: Any) -> None:
    """Add custom command-line options to pytest."""
    parser.addoption(
        "--run-corpus",
        action="store_true",
        default=False,
        help="run corpus tests (slow, requires test PDFs)",
    )


def pytest_configure(config: Any) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "corpus: marks tests as corpus tests (run with --run-corpus)"
    )


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """Skip corpus tests unless --run-corpus flag is provided."""
    if config.getoption("--run-corpus", default=False):
        # Corpus tests should run
        return

    skip_corpus = pytest.mark.skip(reason="need --run-corpus option to run")
    for item in items:
        if "corpus" in item.keywords:
            item.add_marker(skip_corpus)

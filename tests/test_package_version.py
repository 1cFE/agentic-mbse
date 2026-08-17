"""Distribution and runtime package version must describe the same release."""

from pathlib import Path

import tomllib

import agentic_mbse


def test_companion_runtime_and_build_versions_match() -> None:
    project_file = Path(__file__).resolve().parents[1] / "pyproject.toml"
    project = tomllib.loads(project_file.read_text(encoding="utf-8"))

    assert project["project"]["version"] == "0.1.3"
    assert agentic_mbse.__version__ == "0.1.3"

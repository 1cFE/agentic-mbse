"""Integration tests for orchestration bash scripts.

Tests verify that bash scripts correctly integrate with the comment CLI
and follow the orchestration patterns defined in specs/orchestration.md.

NOTE: These are basic smoke tests for the example scripts. Production
deployments should adapt these scripts and write custom tests.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

# Find project root (where pyproject.toml lives)
PROJECT_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture
def git_repo_with_comment_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Create a git repo with comment CLI available in PATH.

    This fixture:
    1. Creates a temporary git repository
    2. Adds the comment CLI to PATH (via Python from venv)
    3. Changes working directory to the repo
    4. Returns dict with repo_path and project_root for tests to use
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Create a sample file
    sample_file = tmp_path / "sample.py"
    sample_file.write_text("def hello():\n    print('hello')\n")

    # Commit the file
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Change to the repo directory FIRST (before creating wrapper)
    monkeypatch.chdir(tmp_path)

    # Add uv run comment to PATH (use Python from venv directly)
    scripts_dir = tmp_path / "bin"
    scripts_dir.mkdir()
    comment_wrapper = scripts_dir / "comment"
    venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
    comment_wrapper.write_text(
        f'#!/usr/bin/env bash\nexec "{venv_python}" -m comment_system.cli "$@"\n'
    )
    comment_wrapper.chmod(0o755)

    # Update PATH
    monkeypatch.setenv("PATH", f"{scripts_dir}:{os.environ['PATH']}")

    # Return dict with both paths for tests to use
    class RepoInfo:
        repo_path = tmp_path
        project_root = PROJECT_ROOT

    return RepoInfo


class TestCheckOpenCommentsScript:
    """Tests for scripts/check_open_comments.sh (AC-1)."""

    def test_no_comments_returns_empty_json(self, git_repo_with_comment_cli):
        """AC-1: Script returns valid JSON array when no comments exist."""
        script = PROJECT_ROOT / "scripts" / "check_open_comments.sh"

        result = subprocess.run(
            [str(script)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout.strip()

        # Verify JSON is valid (AC-1 requirement)
        comments = json.loads(output)
        assert isinstance(comments, list)
        assert len(comments) == 0
        assert "No open comments" in result.stderr

    def test_with_open_comments_returns_valid_json(self, git_repo_with_comment_cli):
        """AC-1: Script returns valid JSON array with open comments."""
        # Add a comment
        sample_file = Path("sample.py")
        subprocess.run(
            ["comment", "add", str(sample_file), "-L", "1:1", "Review this"],
            check=True,
            capture_output=True,
        )

        # Run script
        script = PROJECT_ROOT / "scripts" / "check_open_comments.sh"
        result = subprocess.run(
            [str(script)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout.strip()

        # Verify JSON is valid (AC-1 requirement)
        comments = json.loads(output)
        assert isinstance(comments, list)
        assert len(comments) == 1
        assert comments[0]["status"] == "open"
        assert "Found 1 open comment(s)" in result.stderr

    def test_scripts_exist_and_are_executable(self):
        """Verify all example scripts exist and are executable."""
        script_names = [
            "check_open_comments.sh",
            "agent_review_workflow.sh",
        ]
        hook_names = [
            "post-commit-reconcile.sh",
            "pre-commit-check-comments.sh",
        ]

        for name in script_names:
            script = PROJECT_ROOT / "scripts" / name
            assert script.exists(), f"Script {name} not found"
            assert os.access(script, os.X_OK), f"Script {name} not executable"

        for name in hook_names:
            hook = PROJECT_ROOT / "claude" / "hooks" / name
            assert hook.exists(), f"Hook {name} not found"
            assert os.access(hook, os.X_OK), f"Hook {name} not executable"


class TestDocumentation:
    """Tests for orchestration documentation."""

    def test_orchestration_guide_exists(self):
        """Verify orchestration guide documentation exists."""
        guide = PROJECT_ROOT / "docs" / "orchestration-guide.md"
        assert guide.exists(), "Orchestration guide not found"

        content = guide.read_text()
        # Verify key sections exist
        assert "# Comment System Orchestration Guide" in content
        assert "Git Hooks" in content
        assert "Workflow Patterns" in content
        assert "Examples" in content or "example" in content.lower()

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


class TestRalphLoopIntegration:
    """Tests for Ralph loop integration (Task 9.2, REQ-3, AC-4)."""

    def test_ralph_script_exists_and_is_executable(self):
        """Verify Ralph loop integration script exists and is executable."""
        script = PROJECT_ROOT / "scripts" / "ralph_loop_integration.sh"
        assert script.exists(), "Ralph loop integration script not found"
        assert os.access(script, os.X_OK), "Ralph loop script not executable"

    def test_ralph_workflow_with_no_comments_succeeds(self, git_repo_with_comment_cli):
        """Ralph workflow succeeds when no open comments exist."""
        script = PROJECT_ROOT / "scripts" / "ralph_loop_integration.sh"
        sample_file = Path("sample.py")

        # Run Ralph workflow
        result = subprocess.run(
            [str(script), str(sample_file)],
            capture_output=True,
            text=True,
        )

        # Should succeed (exit 0) when no comments to address
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Verify output includes success message
        assert "No open comments to address" in result.stderr
        assert "Ralph can proceed with task implementation" in result.stderr

        # Verify JSON output is empty array
        output = result.stdout.strip()
        comments = json.loads(output)
        assert isinstance(comments, list)
        assert len(comments) == 0

    def test_ralph_workflow_with_open_comments_exits_with_code_1(
        self, git_repo_with_comment_cli
    ):
        """AC-4: Ralph detects open comments and signals they need addressing (exit 1)."""
        # Add an open comment to the file Ralph will modify
        sample_file = Path("sample.py")
        subprocess.run(
            ["comment", "add", str(sample_file), "-L", "1:1", "Fix this function"],
            check=True,
            capture_output=True,
        )

        # Run Ralph workflow
        script = PROJECT_ROOT / "scripts" / "ralph_loop_integration.sh"
        result = subprocess.run(
            [str(script), str(sample_file)],
            capture_output=True,
            text=True,
        )

        # Should exit with code 1 to signal comments need addressing
        assert result.returncode == 1, "Expected exit code 1 when open comments exist"

        # Verify warning messages
        assert "Found 1 open comment thread(s)" in result.stderr
        assert "should address these 1 comment(s)" in result.stderr

        # Verify JSON output contains the comment
        output = result.stdout.strip()
        comments = json.loads(output)
        assert isinstance(comments, list)
        assert len(comments) == 1
        assert comments[0]["status"] == "open"

    def test_ralph_workflow_reconciles_before_checking(
        self, git_repo_with_comment_cli
    ):
        """Ralph reconciles anchors before checking comments to ensure they're current."""
        # Add a comment
        sample_file = Path("sample.py")
        subprocess.run(
            ["comment", "add", str(sample_file), "-L", "1:1", "Check this"],
            check=True,
            capture_output=True,
        )

        # Modify the file (simulating code changes)
        sample_file.write_text("# Modified\ndef hello():\n    print('hello')\n")

        # Run Ralph workflow
        script = PROJECT_ROOT / "scripts" / "ralph_loop_integration.sh"
        result = subprocess.run(
            [str(script), str(sample_file)],
            capture_output=True,
            text=True,
        )

        # Should still detect the comment (reconciliation should update anchors)
        assert result.returncode == 1
        assert "Reconciling anchors" in result.stderr
        assert "Reconciliation complete" in result.stderr

        # Verify comment was reconciled (anchor should be drifted or anchored)
        output = result.stdout.strip()
        comments = json.loads(output)
        assert len(comments) == 1

    def test_ralph_workflow_handles_all_files_mode(self, git_repo_with_comment_cli):
        """Ralph can check for open comments across all files (not just one)."""
        # Add comments to multiple files
        sample_file = Path("sample.py")
        another_file = Path("another.py")
        another_file.write_text("# Another file\n")

        subprocess.run(
            ["comment", "add", str(sample_file), "-L", "1:1", "Fix this"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["comment", "add", str(another_file), "-L", "1:1", "Fix that"],
            check=True,
            capture_output=True,
        )

        # Run Ralph workflow without specifying a file (check all)
        script = PROJECT_ROOT / "scripts" / "ralph_loop_integration.sh"
        result = subprocess.run(
            [str(script)],
            capture_output=True,
            text=True,
        )

        # Should detect both comments
        assert result.returncode == 1
        assert "Found 2 open comment thread(s)" in result.stderr

        # Verify JSON output contains both comments
        output = result.stdout.strip()
        comments = json.loads(output)
        assert len(comments) == 2

    def test_ralph_workflow_suggests_workflow_steps(self, git_repo_with_comment_cli):
        """Ralph script provides guidance on how to address comments (REQ-3)."""
        # Add a comment
        sample_file = Path("sample.py")
        subprocess.run(
            ["comment", "add", str(sample_file), "-L", "1:1", "Needs review"],
            check=True,
            capture_output=True,
        )

        # Run Ralph workflow
        script = PROJECT_ROOT / "scripts" / "ralph_loop_integration.sh"
        result = subprocess.run(
            [str(script), str(sample_file)],
            capture_output=True,
            text=True,
        )

        # Verify workflow guidance is provided (REQ-3 requirements)
        stderr = result.stderr
        assert "Read each comment thread" in stderr
        assert "Address the feedback" in stderr
        assert "Reply to comments" in stderr
        assert "Resolve comments with decision summaries" in stderr
        assert "Include comment resolutions in commit message" in stderr

    def test_ralph_workflow_respects_no_color_env(self, git_repo_with_comment_cli):
        """Ralph script respects NO_COLOR environment variable."""
        script = PROJECT_ROOT / "scripts" / "ralph_loop_integration.sh"
        sample_file = Path("sample.py")

        # Run with NO_COLOR set
        env = os.environ.copy()
        env["NO_COLOR"] = "1"

        result = subprocess.run(
            [str(script), str(sample_file)],
            capture_output=True,
            text=True,
            env=env,
        )

        # Verify no ANSI color codes in output
        assert "\033[" not in result.stderr, "ANSI codes found despite NO_COLOR"

    def test_ralph_workflow_allows_custom_comment_command(
        self, git_repo_with_comment_cli
    ):
        """Ralph script respects COMMENT_CMD environment variable."""
        script = PROJECT_ROOT / "scripts" / "ralph_loop_integration.sh"
        sample_file = Path("sample.py")

        # Find the comment wrapper we created
        comment_cmd = Path("bin") / "comment"

        # Run with COMMENT_CMD set
        env = os.environ.copy()
        env["COMMENT_CMD"] = str(comment_cmd)

        result = subprocess.run(
            [str(script), str(sample_file)],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should work with custom command
        assert result.returncode == 0


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

"""Tests for git operations (rename detection, deletion handling)."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from comment_system.git_ops import (
    GitNotAvailableError,
    NotAGitRepositoryError,
    detect_file_rename,
    is_git_available,
    is_git_repository,
)


class TestGitAvailability:
    """Tests for git availability checking."""

    def test_git_available_when_installed(self) -> None:
        """Git is detected when installed."""
        # This test assumes git is installed (reasonable for dev environment)
        assert is_git_available() is True

    @patch("subprocess.run")
    def test_git_not_available_when_command_fails(self, mock_run: Mock) -> None:
        """Git is not available when command returns non-zero."""
        mock_run.return_value = Mock(returncode=1)
        assert is_git_available() is False

    @patch("subprocess.run")
    def test_git_not_available_when_not_found(self, mock_run: Mock) -> None:
        """Git is not available when command not found."""
        mock_run.side_effect = FileNotFoundError()
        assert is_git_available() is False

    @patch("subprocess.run")
    def test_git_not_available_on_timeout(self, mock_run: Mock) -> None:
        """Git is not available when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 5)
        assert is_git_available() is False


class TestGitRepository:
    """Tests for git repository detection."""

    def test_is_git_repository_in_actual_repo(self, tmp_path: Path) -> None:
        """Detect git repository when .git directory exists."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        assert is_git_repository(tmp_path) is True

    def test_is_git_repository_in_subdirectory(self, tmp_path: Path) -> None:
        """Detect git repository from subdirectory."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # Create subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        assert is_git_repository(subdir) is True

    def test_not_git_repository_outside_repo(self, tmp_path: Path) -> None:
        """Not a git repository when no .git directory."""
        assert is_git_repository(tmp_path) is False

    @patch("subprocess.run")
    def test_not_git_repository_when_git_unavailable(self, mock_run: Mock, tmp_path: Path) -> None:
        """Not a git repository when git command fails."""
        mock_run.side_effect = FileNotFoundError()
        assert is_git_repository(tmp_path) is False


class TestDetectFileRename:
    """Tests for file rename detection."""

    def test_no_rename_when_file_not_moved(self, tmp_path: Path) -> None:
        """No rename detected when file never moved."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create and commit file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")
        subprocess.run(["git", "add", "test.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Check for rename (should be None)
        result = detect_file_rename(test_file, tmp_path)
        assert result is None

    def test_rename_detected_simple(self, tmp_path: Path) -> None:
        """Rename detected for simple A → B rename."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create and commit file
        old_file = tmp_path / "old.md"
        old_file.write_text("# Test content")
        subprocess.run(["git", "add", "old.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Rename file in git
        new_file = tmp_path / "new.md"
        subprocess.run(
            ["git", "mv", "old.md", "new.md"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Rename file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Detect rename from old path
        result = detect_file_rename(old_file, tmp_path)
        assert result == new_file

    def test_rename_chain_detected(self, tmp_path: Path) -> None:
        """Rename chain A → B → C is detected (AC-5)."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create and commit file A
        file_a = tmp_path / "a.md"
        file_a.write_text("# Test content")
        subprocess.run(["git", "add", "a.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Rename A → B
        subprocess.run(
            ["git", "mv", "a.md", "b.md"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Rename A to B"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Rename B → C
        file_c = tmp_path / "c.md"
        subprocess.run(
            ["git", "mv", "b.md", "c.md"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Rename B to C"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Detect rename from original path A → should find C
        result = detect_file_rename(file_a, tmp_path)
        assert result == file_c

    def test_rename_in_subdirectory(self, tmp_path: Path) -> None:
        """Rename detected for files in subdirectories."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create subdirectory structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create and commit file
        old_file = src_dir / "old.py"
        old_file.write_text("# Python code")
        subprocess.run(["git", "add", "src/old.py"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Rename file
        new_file = src_dir / "new.py"
        subprocess.run(
            ["git", "mv", "src/old.py", "src/new.py"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Rename file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Detect rename
        result = detect_file_rename(old_file, tmp_path)
        assert result == new_file

    def test_no_rename_when_file_deleted_after_rename(self, tmp_path: Path) -> None:
        """No rename detected when renamed file is subsequently deleted."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create and commit file
        old_file = tmp_path / "old.md"
        old_file.write_text("# Test")
        subprocess.run(["git", "add", "old.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Rename file
        subprocess.run(
            ["git", "mv", "old.md", "new.md"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Rename file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Delete renamed file
        subprocess.run(
            ["git", "rm", "new.md"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Delete file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Detect rename (should be None because new file doesn't exist)
        result = detect_file_rename(old_file, tmp_path)
        assert result is None

    def test_raises_git_not_available(self, tmp_path: Path) -> None:
        """Raises GitNotAvailableError when git command not found."""
        with patch("comment_system.git_ops.is_git_available", return_value=False):
            with pytest.raises(GitNotAvailableError):
                detect_file_rename(tmp_path / "test.md", tmp_path)

    def test_raises_not_git_repository(self, tmp_path: Path) -> None:
        """Raises NotAGitRepositoryError when path not in git repo (AC-6)."""
        # Don't initialize git repo
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        with pytest.raises(NotAGitRepositoryError):
            detect_file_rename(test_file, tmp_path)

    def test_file_outside_project_root(self, tmp_path: Path) -> None:
        """Returns None when file is outside project root."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # Create file outside project root
        outside_file = tmp_path.parent / "outside.md"
        outside_file.write_text("# Outside")

        # Detect rename (should be None)
        result = detect_file_rename(outside_file, tmp_path)
        assert result is None

        # Cleanup
        outside_file.unlink()

    def test_max_renames_limit(self, tmp_path: Path) -> None:
        """Respects max_renames parameter (CON-4)."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create initial file
        current_file = tmp_path / "file0.md"
        current_file.write_text("# Test")
        subprocess.run(["git", "add", "file0.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create 5 renames (file0 → file1 → ... → file5)
        for i in range(1, 6):
            old_name = f"file{i-1}.md"
            new_name = f"file{i}.md"
            subprocess.run(
                ["git", "mv", old_name, new_name],
                cwd=tmp_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"Rename to {new_name}"],
                cwd=tmp_path,
                check=True,
                capture_output=True,
            )

        # Detect rename with max_renames=3 (should only follow 3 renames)
        result = detect_file_rename(tmp_path / "file0.md", tmp_path, max_renames=3)
        # Should stop after 3 renames, but file3.md doesn't exist (renamed to file5.md)
        # So result should be None (final file doesn't exist)
        assert result is None

        # Detect rename with max_renames=10 (default, should follow all)
        result = detect_file_rename(tmp_path / "file0.md", tmp_path, max_renames=10)
        # Should find file5.md (all 5 renames)
        assert result == tmp_path / "file5.md"

    def test_file_never_existed(self, tmp_path: Path) -> None:
        """Returns None when file never existed in git history."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # Check for rename of non-existent file
        result = detect_file_rename(tmp_path / "nonexistent.md", tmp_path)
        assert result is None

    @patch("subprocess.run")
    def test_git_timeout_returns_none(self, mock_run: Mock, tmp_path: Path) -> None:
        """Returns None when git command times out."""
        # Mock is_git_available to return True
        with patch("comment_system.git_ops.is_git_available", return_value=True):
            # Mock is_git_repository to return True
            with patch("comment_system.git_ops.is_git_repository", return_value=True):
                # Make subprocess timeout
                mock_run.side_effect = subprocess.TimeoutExpired("git", 10)

                result = detect_file_rename(tmp_path / "test.md", tmp_path)
                assert result is None

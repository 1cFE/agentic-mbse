"""Tests for git operations (rename detection, deletion handling)."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from comment_system.git_ops import (
    GitNotAvailableError,
    NotAGitRepositoryError,
    detect_file_rename,
    is_file_deleted_in_git,
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
            old_name = f"file{i - 1}.md"
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


class TestMoveSidecar:
    """Test sidecar file moving when source files are renamed."""

    def test_move_sidecar_simple_rename(self, tmp_path: Path) -> None:
        """Sidecar moves when source file is renamed (AC-1)."""
        from comment_system.git_ops import move_sidecar
        from comment_system.models import Anchor, Comment, Thread
        from comment_system.storage import SidecarFile, write_sidecar

        # Create source file and sidecar
        old_path = tmp_path / "old.md"
        old_path.write_text("# Old content")

        # Create sidecar with a thread
        thread = Thread(
            comments=[Comment(body="Test comment", author="Test User", author_type="human")],
            anchor=Anchor(
                content_hash="sha256:" + "a" * 64,
                context_hash_before="sha256:" + "b" * 64,
                context_hash_after="sha256:" + "c" * 64,
                line_start=1,
                line_end=1,
                content_snippet="# Old content",
            ),
        )
        sidecar = SidecarFile(
            source_file=old_path.relative_to(tmp_path).as_posix(),
            source_hash="sha256:" + "0" * 64,
            threads=[thread],
        )
        write_sidecar(
            tmp_path / ".comments" / "old.md.json",
            sidecar,
            check_hash=False,
            acquire_lock=False,
        )

        # Move sidecar
        new_path = tmp_path / "new.md"
        result = move_sidecar(old_path, new_path, tmp_path)

        # Verify move succeeded
        assert result is True

        # Verify old sidecar gone
        assert not (tmp_path / ".comments" / "old.md.json").exists()

        # Verify new sidecar exists
        new_sidecar_path = tmp_path / ".comments" / "new.md.json"
        assert new_sidecar_path.exists()

        # Verify source_file field updated
        from comment_system.storage import read_sidecar

        moved_sidecar = read_sidecar(new_sidecar_path)
        assert moved_sidecar.source_file == "new.md"
        assert len(moved_sidecar.threads) == 1
        assert moved_sidecar.threads[0].comments[0].body == "Test comment"

    def test_move_sidecar_nested_path(self, tmp_path: Path) -> None:
        """Sidecar moves correctly for nested directories."""
        from comment_system.git_ops import move_sidecar
        from comment_system.models import Anchor, Comment, Thread
        from comment_system.storage import SidecarFile, write_sidecar

        # Create nested source file and sidecar
        old_path = tmp_path / "src" / "old.md"
        old_path.parent.mkdir(parents=True)
        old_path.write_text("# Old content")

        thread = Thread(
            comments=[Comment(body="Test comment", author="Test User", author_type="human")],
            anchor=Anchor(
                content_hash="sha256:" + "a" * 64,
                context_hash_before="sha256:" + "b" * 64,
                context_hash_after="sha256:" + "c" * 64,
                line_start=1,
                line_end=1,
                content_snippet="# Old content",
            ),
        )
        sidecar = SidecarFile(
            source_file="src/old.md",
            source_hash="sha256:" + "0" * 64,
            threads=[thread],
        )
        write_sidecar(
            tmp_path / ".comments" / "src" / "old.md.json",
            sidecar,
            check_hash=False,
            acquire_lock=False,
        )

        # Move to different directory
        new_path = tmp_path / "lib" / "new.md"
        result = move_sidecar(old_path, new_path, tmp_path)

        # Verify move succeeded
        assert result is True

        # Verify new sidecar exists at correct location
        new_sidecar_path = tmp_path / ".comments" / "lib" / "new.md.json"
        assert new_sidecar_path.exists()

        # Verify source_file updated
        from comment_system.storage import read_sidecar

        moved_sidecar = read_sidecar(new_sidecar_path)
        assert moved_sidecar.source_file == "lib/new.md"

    def test_move_sidecar_no_sidecar_exists(self, tmp_path: Path) -> None:
        """Returns False when no sidecar exists for source file."""
        from comment_system.git_ops import move_sidecar

        old_path = tmp_path / "old.md"
        new_path = tmp_path / "new.md"

        # No sidecar exists
        result = move_sidecar(old_path, new_path, tmp_path)
        assert result is False

    def test_move_sidecar_atomic_operation(self, tmp_path: Path) -> None:
        """Sidecar move uses atomic temp + rename (CON-2)."""
        from comment_system.git_ops import move_sidecar
        from comment_system.models import Anchor, Comment, Thread
        from comment_system.storage import SidecarFile, write_sidecar

        # Create source file and sidecar
        old_path = tmp_path / "old.md"
        old_path.write_text("# Old content")

        thread = Thread(
            comments=[Comment(body="Test comment", author="Test User", author_type="human")],
            anchor=Anchor(
                content_hash="sha256:" + "a" * 64,
                context_hash_before="sha256:" + "b" * 64,
                context_hash_after="sha256:" + "c" * 64,
                line_start=1,
                line_end=1,
                content_snippet="# Old content",
            ),
        )
        sidecar = SidecarFile(
            source_file="old.md",
            source_hash="sha256:" + "0" * 64,
            threads=[thread],
        )
        write_sidecar(
            tmp_path / ".comments" / "old.md.json",
            sidecar,
            check_hash=False,
            acquire_lock=False,
        )

        # Move sidecar
        new_path = tmp_path / "new.md"
        move_sidecar(old_path, new_path, tmp_path)

        # Verify no temp files left behind
        for path in (tmp_path / ".comments").rglob("*.tmp.json"):
            pytest.fail(f"Temp file not cleaned up: {path}")

    def test_move_sidecar_cleans_empty_directory(self, tmp_path: Path) -> None:
        """Removes empty old sidecar directory after move."""
        from comment_system.git_ops import move_sidecar
        from comment_system.models import Anchor, Comment, Thread
        from comment_system.storage import SidecarFile, write_sidecar

        # Create nested source file and sidecar
        old_path = tmp_path / "old_dir" / "file.md"
        old_path.parent.mkdir(parents=True)
        old_path.write_text("# Content")

        thread = Thread(
            comments=[Comment(body="Test comment", author="Test User", author_type="human")],
            anchor=Anchor(
                content_hash="sha256:" + "a" * 64,
                context_hash_before="sha256:" + "b" * 64,
                context_hash_after="sha256:" + "c" * 64,
                line_start=1,
                line_end=1,
                content_snippet="# Content",
            ),
        )
        sidecar = SidecarFile(
            source_file="old_dir/file.md",
            source_hash="sha256:" + "0" * 64,
            threads=[thread],
        )
        write_sidecar(
            tmp_path / ".comments" / "old_dir" / "file.md.json",
            sidecar,
            check_hash=False,
            acquire_lock=False,
        )

        # Move to different directory
        new_path = tmp_path / "new_dir" / "file.md"
        move_sidecar(old_path, new_path, tmp_path)

        # Verify old directory cleaned up
        assert not (tmp_path / ".comments" / "old_dir").exists()


class TestDetectAndMoveAllSidecars:
    """Test project-wide rename detection and sidecar moving."""

    def test_detect_and_move_all_simple_rename(self, tmp_path: Path) -> None:
        """Detects and moves sidecar for single renamed file."""
        from comment_system.git_ops import detect_and_move_all_sidecars
        from comment_system.models import Anchor, Comment, Thread
        from comment_system.storage import SidecarFile, write_sidecar

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
        old_path = tmp_path / "old.md"
        old_path.write_text("# Content")
        subprocess.run(["git", "add", "old.md"], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create sidecar
        thread = Thread(
            comments=[Comment(body="Test comment", author="Test User", author_type="human")],
            anchor=Anchor(
                content_hash="sha256:" + "a" * 64,
                context_hash_before="sha256:" + "b" * 64,
                context_hash_after="sha256:" + "c" * 64,
                line_start=1,
                line_end=1,
                content_snippet="# Content",
            ),
        )
        sidecar = SidecarFile(
            source_file="old.md",
            source_hash="sha256:" + "0" * 64,
            threads=[thread],
        )
        write_sidecar(
            tmp_path / ".comments" / "old.md.json",
            sidecar,
            check_hash=False,
            acquire_lock=False,
        )

        # Rename file in git
        subprocess.run(["git", "mv", "old.md", "new.md"], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Rename file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Run detection and move
        moved = detect_and_move_all_sidecars(tmp_path)

        # Verify one file moved
        assert len(moved) == 1
        assert moved[0] == (tmp_path / "old.md", tmp_path / "new.md")

        # Verify sidecar at new location
        assert (tmp_path / ".comments" / "new.md.json").exists()
        assert not (tmp_path / ".comments" / "old.md.json").exists()

    def test_detect_and_move_all_directory_rename(self, tmp_path: Path) -> None:
        """Handles directory renames affecting multiple files (AC-3)."""
        from comment_system.git_ops import detect_and_move_all_sidecars
        from comment_system.models import Anchor, Comment, Thread
        from comment_system.storage import SidecarFile, write_sidecar

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

        # Create src directory with files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        file1 = src_dir / "file1.md"
        file2 = src_dir / "file2.md"
        file1.write_text("# File 1")
        file2.write_text("# File 2")

        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create sidecars
        for filename in ["file1.md", "file2.md"]:
            thread = Thread(
                comments=[
                    Comment(body=f"Comment on {filename}", author="Test User", author_type="human")
                ],
                anchor=Anchor(
                    content_hash="sha256:" + "a" * 64,
                    context_hash_before="sha256:" + "b" * 64,
                    context_hash_after="sha256:" + "c" * 64,
                    line_start=1,
                    line_end=1,
                    content_snippet=f"# {filename}",
                ),
            )
            sidecar = SidecarFile(
                source_file=f"src/{filename}",
                source_hash="sha256:" + "1" * 64,
                threads=[thread],
            )
            write_sidecar(
                tmp_path / ".comments" / "src" / f"{filename}.json",
                sidecar,
                check_hash=False,
                acquire_lock=False,
            )

        # Rename directory
        subprocess.run(["git", "mv", "src", "lib"], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Rename directory"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Run detection and move
        moved = detect_and_move_all_sidecars(tmp_path)

        # Verify both files moved
        assert len(moved) == 2
        moved_dict = {old: new for old, new in moved}
        assert moved_dict[tmp_path / "src" / "file1.md"] == tmp_path / "lib" / "file1.md"
        assert moved_dict[tmp_path / "src" / "file2.md"] == tmp_path / "lib" / "file2.md"

        # Verify sidecars at new locations
        assert (tmp_path / ".comments" / "lib" / "file1.md.json").exists()
        assert (tmp_path / ".comments" / "lib" / "file2.md.json").exists()
        assert not (tmp_path / ".comments" / "src").exists()

    def test_detect_and_move_all_no_comments_dir(self, tmp_path: Path) -> None:
        """Returns empty list when .comments directory doesn't exist."""
        from comment_system.git_ops import detect_and_move_all_sidecars

        # No .comments directory
        moved = detect_and_move_all_sidecars(tmp_path)
        assert moved == []

    def test_detect_and_move_all_no_renames(self, tmp_path: Path) -> None:
        """Returns empty list when no files have been renamed."""
        from comment_system.git_ops import detect_and_move_all_sidecars
        from comment_system.models import Anchor, Comment, Thread
        from comment_system.storage import SidecarFile, write_sidecar

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

        # Create file and sidecar (file still exists)
        file_path = tmp_path / "file.md"
        file_path.write_text("# Content")

        thread = Thread(
            comments=[Comment(body="Test comment", author="Test User", author_type="human")],
            anchor=Anchor(
                content_hash="sha256:" + "a" * 64,
                context_hash_before="sha256:" + "b" * 64,
                context_hash_after="sha256:" + "c" * 64,
                line_start=1,
                line_end=1,
                content_snippet="# Content",
            ),
        )
        sidecar = SidecarFile(
            source_file="file.md",
            source_hash="sha256:" + "2" * 64,
            threads=[thread],
        )
        write_sidecar(
            tmp_path / ".comments" / "file.md.json",
            sidecar,
            check_hash=False,
            acquire_lock=False,
        )

        # File not renamed (still exists)
        moved = detect_and_move_all_sidecars(tmp_path)
        assert moved == []

    def test_detect_and_move_all_invalid_sidecar(self, tmp_path: Path) -> None:
        """Skips invalid sidecar files gracefully."""
        from comment_system.git_ops import detect_and_move_all_sidecars

        # Create invalid sidecar file
        comments_dir = tmp_path / ".comments"
        comments_dir.mkdir()
        invalid_sidecar = comments_dir / "invalid.json"
        invalid_sidecar.write_text("{ invalid json }")

        # Should not raise, just skip
        moved = detect_and_move_all_sidecars(tmp_path)
        assert moved == []


class TestDeletionDetection:
    """Tests for file deletion detection."""

    def test_file_deleted_after_commit(self, tmp_path: Path) -> None:
        """File deleted in git is detected correctly."""
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
            ["git", "commit", "-m", "Add test file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Delete file and commit
        test_file.unlink()
        subprocess.run(["git", "add", "test.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Delete test file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # File should be detected as deleted
        assert is_file_deleted_in_git(test_file, tmp_path) is True

    def test_file_never_tracked_not_deleted(self, tmp_path: Path) -> None:
        """File that was never tracked is not considered deleted."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # File never tracked (doesn't exist, never in git)
        test_file = tmp_path / "never_existed.md"

        # Should not be detected as deleted (never in history)
        assert is_file_deleted_in_git(test_file, tmp_path) is False

    def test_existing_file_not_deleted(self, tmp_path: Path) -> None:
        """File that still exists is not deleted."""
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
            ["git", "commit", "-m", "Add test file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # File exists, so not deleted
        assert is_file_deleted_in_git(test_file, tmp_path) is False

    def test_renamed_file_not_deleted(self, tmp_path: Path) -> None:
        """File that was renamed is not considered deleted."""
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
            ["git", "commit", "-m", "Add old file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Rename file
        subprocess.run(
            ["git", "mv", "old.md", "new.md"], cwd=tmp_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Rename file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Old file path should not be detected as deleted (it was renamed)
        assert is_file_deleted_in_git(old_file, tmp_path) is False

    def test_file_outside_project_root_not_deleted(self, tmp_path: Path) -> None:
        """File outside project root returns False."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # File outside project root
        outside_file = tmp_path.parent / "outside.md"

        # Should return False
        assert is_file_deleted_in_git(outside_file, tmp_path) is False

    def test_deletion_detection_requires_git_available(self, tmp_path: Path) -> None:
        """Deletion detection raises error when git not available."""
        with patch("comment_system.git_ops.is_git_available", return_value=False):
            test_file = tmp_path / "test.md"
            with pytest.raises(GitNotAvailableError):
                is_file_deleted_in_git(test_file, tmp_path)

    def test_deletion_detection_requires_git_repository(self, tmp_path: Path) -> None:
        """Deletion detection raises error when not in git repo."""
        # Not a git repo
        test_file = tmp_path / "test.md"

        with pytest.raises(NotAGitRepositoryError):
            is_file_deleted_in_git(test_file, tmp_path)

    def test_file_deleted_then_recreated_not_deleted(self, tmp_path: Path) -> None:
        """File that was deleted but then recreated is not deleted."""
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
        test_file.write_text("# Test v1")
        subprocess.run(["git", "add", "test.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add test file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Delete file and commit
        test_file.unlink()
        subprocess.run(["git", "add", "test.md"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Delete test file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Recreate file
        test_file.write_text("# Test v2")

        # File exists, so not deleted (even though it was deleted in history)
        assert is_file_deleted_in_git(test_file, tmp_path) is False

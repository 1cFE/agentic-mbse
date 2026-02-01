"""Tests for storage.py file operations."""

import time
from pathlib import Path

import pytest

from comment_system.storage import (
    compute_source_hash,
    find_project_root,
    get_sidecar_path,
    is_binary_file,
    normalize_path,
)


class TestComputeSourceHash:
    """Tests for compute_source_hash function."""

    def test_hash_simple_file(self, tmp_path: Path) -> None:
        """Hash computation produces sha256: prefix."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!\n")

        result = compute_source_hash(test_file)

        assert result.startswith("sha256:")
        # Known SHA-256 of "Hello, world!\n"
        assert (
            result
            == "sha256:d9014c4624844aa5bac314773d6b689ad467fa4e1d1a50a1b8a99d5a95f72ff5"
        )

    def test_hash_empty_file(self, tmp_path: Path) -> None:
        """Empty file produces valid hash."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        result = compute_source_hash(test_file)

        assert result.startswith("sha256:")
        # Known SHA-256 of empty string
        assert (
            result
            == "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_hash_deterministic(self, tmp_path: Path) -> None:
        """Same content produces same hash."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Deterministic content\n")

        hash1 = compute_source_hash(test_file)
        hash2 = compute_source_hash(test_file)

        assert hash1 == hash2

    def test_hash_different_content(self, tmp_path: Path) -> None:
        """Different content produces different hash."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content A\n")
        file2.write_text("Content B\n")

        hash1 = compute_source_hash(file1)
        hash2 = compute_source_hash(file2)

        assert hash1 != hash2

    def test_hash_multiline_file(self, tmp_path: Path) -> None:
        """Multiline file hashes correctly."""
        test_file = tmp_path / "multiline.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\n")

        result = compute_source_hash(test_file)

        assert result.startswith("sha256:")
        assert len(result) == 71  # "sha256:" (7) + 64 hex chars

    def test_hash_nonexistent_file(self, tmp_path: Path) -> None:
        """Nonexistent file raises FileNotFoundError."""
        nonexistent = tmp_path / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError, match="Source file not found"):
            compute_source_hash(nonexistent)

    def test_hash_directory_raises_error(self, tmp_path: Path) -> None:
        """Directory raises ValueError."""
        with pytest.raises(ValueError, match="Path is not a file"):
            compute_source_hash(tmp_path)

    def test_hash_binary_file_raises_error(self, tmp_path: Path) -> None:
        """Binary file raises ValueError."""
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        with pytest.raises(ValueError, match="Binary files not supported"):
            compute_source_hash(binary_file)

    def test_hash_performance_large_file(self, tmp_path: Path) -> None:
        """10 MB file hashes in < 100ms."""
        # Create 10 MB file
        large_file = tmp_path / "large.txt"
        content = "x" * (10 * 1024 * 1024)  # 10 MB of 'x'
        large_file.write_text(content)

        start_time = time.perf_counter()
        compute_source_hash(large_file)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert elapsed_ms < 100, f"Hash took {elapsed_ms:.2f}ms (expected < 100ms)"


class TestIsBinaryFile:
    """Tests for is_binary_file function."""

    def test_text_file_is_not_binary(self, tmp_path: Path) -> None:
        """Text file returns False."""
        text_file = tmp_path / "text.txt"
        text_file.write_text("This is text\n")

        assert is_binary_file(text_file) is False

    def test_binary_file_is_binary(self, tmp_path: Path) -> None:
        """File with null bytes returns True."""
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"Hello\x00World")

        assert is_binary_file(binary_file) is True

    def test_empty_file_is_not_binary(self, tmp_path: Path) -> None:
        """Empty file is treated as text."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_bytes(b"")

        assert is_binary_file(empty_file) is False

    def test_large_text_file_is_not_binary(self, tmp_path: Path) -> None:
        """Large text file (> 8192 bytes) is still text."""
        large_text = tmp_path / "large.txt"
        large_text.write_text("x" * 20000)  # 20KB of text

        assert is_binary_file(large_text) is False

    def test_binary_after_text_is_binary(self, tmp_path: Path) -> None:
        """File with null byte after text is binary."""
        mixed_file = tmp_path / "mixed.bin"
        mixed_file.write_bytes(b"Text content here\x00binary after")

        assert is_binary_file(mixed_file) is True

    def test_unreadable_file_is_binary(self, tmp_path: Path) -> None:
        """File that can't be read is treated as binary (safe default)."""
        # Create file and remove read permissions
        no_read = tmp_path / "no_read.txt"
        no_read.write_text("content")
        no_read.chmod(0o000)

        try:
            result = is_binary_file(no_read)
            assert result is True
        finally:
            # Restore permissions for cleanup
            no_read.chmod(0o644)


class TestGetSidecarPath:
    """Tests for get_sidecar_path function."""

    def test_simple_file_in_root(self, tmp_path: Path) -> None:
        """File in project root maps correctly."""
        source = tmp_path / "file.txt"
        source.touch()

        result = get_sidecar_path(source, tmp_path)

        expected = tmp_path / ".comments" / "file.txt.json"
        assert result == expected

    def test_nested_file(self, tmp_path: Path) -> None:
        """Nested file preserves directory structure."""
        source = tmp_path / "src" / "models" / "model.py"
        source.parent.mkdir(parents=True)
        source.touch()

        result = get_sidecar_path(source, tmp_path)

        expected = tmp_path / ".comments" / "src" / "models" / "model.py.json"
        assert result == expected

    def test_deeply_nested_file(self, tmp_path: Path) -> None:
        """Deeply nested file works correctly."""
        source = tmp_path / "a" / "b" / "c" / "d" / "file.txt"
        source.parent.mkdir(parents=True)
        source.touch()

        result = get_sidecar_path(source, tmp_path)

        expected = tmp_path / ".comments" / "a" / "b" / "c" / "d" / "file.txt.json"
        assert result == expected

    def test_file_outside_project_raises_error(self, tmp_path: Path) -> None:
        """File outside project root raises ValueError."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        outside_file = tmp_path / "outside.txt"
        outside_file.touch()

        with pytest.raises(ValueError, match="outside project root"):
            get_sidecar_path(outside_file, project_root)

    def test_relative_path_resolution(self, tmp_path: Path) -> None:
        """Relative source paths are resolved correctly."""
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        source = source_dir / "file.py"
        source.touch()

        # Use relative path
        relative_source = Path("src") / "file.py"
        result = get_sidecar_path(tmp_path / relative_source, tmp_path)

        expected = tmp_path / ".comments" / "src" / "file.py.json"
        assert result == expected

    def test_symlink_resolution(self, tmp_path: Path) -> None:
        """Symlinks are resolved to real paths."""
        # Create real file
        real_file = tmp_path / "real.txt"
        real_file.touch()

        # Create symlink
        link = tmp_path / "link.txt"
        link.symlink_to(real_file)

        result = get_sidecar_path(link, tmp_path)

        # Should resolve to real file's sidecar
        expected = tmp_path / ".comments" / "real.txt.json"
        assert result == expected


class TestNormalizePath:
    """Tests for normalize_path function."""

    def test_absolute_path_within_project(self, tmp_path: Path) -> None:
        """Absolute path within project is normalized."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        result = normalize_path(file_path, tmp_path)

        assert result == file_path.resolve()

    def test_relative_path_from_root(self, tmp_path: Path) -> None:
        """Relative path is resolved from project root."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        file_path = subdir / "file.txt"
        file_path.touch()

        relative = Path("subdir") / "file.txt"
        result = normalize_path(relative, tmp_path)

        assert result == file_path.resolve()

    def test_path_with_dot_dot_within_project(self, tmp_path: Path) -> None:
        """Path with .. that stays in project is normalized."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        file_path = tmp_path / "file.txt"
        file_path.touch()

        weird_path = tmp_path / "subdir" / ".." / "file.txt"
        result = normalize_path(weird_path, tmp_path)

        assert result == file_path.resolve()

    def test_path_with_dot_dot_outside_project_raises_error(
        self, tmp_path: Path
    ) -> None:
        """Path with .. that escapes project raises ValueError."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Try to escape with ../..
        escape_path = project_root / ".." / ".." / "etc" / "passwd"

        with pytest.raises(ValueError, match="outside project root"):
            normalize_path(escape_path, project_root)

    def test_absolute_path_outside_project_raises_error(self, tmp_path: Path) -> None:
        """Absolute path outside project raises ValueError."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        outside = tmp_path / "outside.txt"
        outside.touch()

        with pytest.raises(ValueError, match="outside project root"):
            normalize_path(outside, project_root)

    def test_path_normalization_removes_redundant_separators(
        self, tmp_path: Path
    ) -> None:
        """Redundant path separators are normalized."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        # Path with redundant separators
        weird_path = Path(str(tmp_path) + "//file.txt")
        result = normalize_path(weird_path, tmp_path)

        assert result == file_path.resolve()

    def test_nonexistent_path_is_normalized(self, tmp_path: Path) -> None:
        """Nonexistent paths can still be normalized (no file check)."""
        nonexistent = tmp_path / "does_not_exist.txt"

        result = normalize_path(nonexistent, tmp_path)

        assert result == nonexistent.resolve()


class TestFindProjectRoot:
    """Tests for find_project_root function."""

    def test_find_root_from_project_root(self, tmp_path: Path) -> None:
        """Finding root from project root returns that directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        result = find_project_root(tmp_path)

        assert result == tmp_path

    def test_find_root_from_subdirectory(self, tmp_path: Path) -> None:
        """Finding root from subdirectory walks up tree."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        subdir = tmp_path / "src" / "models"
        subdir.mkdir(parents=True)

        result = find_project_root(subdir)

        assert result == tmp_path

    def test_find_root_from_deeply_nested_directory(self, tmp_path: Path) -> None:
        """Finding root from deeply nested directory works."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        deep = tmp_path / "a" / "b" / "c" / "d" / "e"
        deep.mkdir(parents=True)

        result = find_project_root(deep)

        assert result == tmp_path

    def test_no_git_directory_raises_error(self, tmp_path: Path) -> None:
        """No .git directory raises ValueError."""
        # Don't create .git directory

        with pytest.raises(ValueError, match="No .git directory found"):
            find_project_root(tmp_path)

    def test_find_root_defaults_to_cwd(self, tmp_path: Path, monkeypatch) -> None:
        """No start_path defaults to current working directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Change to tmp_path
        monkeypatch.chdir(tmp_path)

        result = find_project_root()

        assert result == tmp_path

    def test_git_file_not_directory(self, tmp_path: Path) -> None:
        """A .git file (not directory) doesn't count as project root."""
        # Create .git as a file (like in git submodules/worktrees)
        git_file = tmp_path / ".git"
        git_file.write_text("gitdir: ../main/.git")

        with pytest.raises(ValueError, match="No .git directory found"):
            find_project_root(tmp_path)


class TestIntegrationScenarios:
    """Integration tests combining multiple functions."""

    def test_full_workflow_compute_and_map(self, tmp_path: Path) -> None:
        """Full workflow: compute hash and get sidecar path."""
        # Setup
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        source = tmp_path / "src" / "model.py"
        source.parent.mkdir(parents=True)
        source.write_text("def hello(): pass\n")

        # Compute hash
        source_hash = compute_source_hash(source)
        assert source_hash.startswith("sha256:")

        # Get sidecar path
        sidecar = get_sidecar_path(source, tmp_path)
        assert sidecar == tmp_path / ".comments" / "src" / "model.py.json"

    def test_security_reject_path_traversal(self, tmp_path: Path) -> None:
        """Security test: reject malicious path traversal attempts."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        git_dir = project_root / ".git"
        git_dir.mkdir()

        # Try various path traversal attacks
        attacks = [
            "../../etc/passwd",
            "../../../etc/shadow",
            "subdir/../../../../../../etc/hosts",
        ]

        for attack in attacks:
            malicious = project_root / attack
            with pytest.raises(ValueError, match="outside project root"):
                normalize_path(malicious, project_root)

    def test_normalize_then_get_sidecar(self, tmp_path: Path) -> None:
        """Normalize path then get sidecar path."""
        source = tmp_path / "src" / "file.py"
        source.parent.mkdir(parents=True)
        source.touch()

        # Normalize first
        normalized = normalize_path(source, tmp_path)

        # Then get sidecar
        sidecar = get_sidecar_path(normalized, tmp_path)

        assert sidecar == tmp_path / ".comments" / "src" / "file.py.json"

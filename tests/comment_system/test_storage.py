"""Tests for storage.py file operations."""

import multiprocessing
import time
from pathlib import Path

import pytest

from comment_system.models import (
    Anchor,
    AnchorHealth,
    AuthorType,
    Decision,
    SidecarFile,
    Thread,
    ThreadStatus,
)
from comment_system.storage import (
    ConcurrencyConflict,
    compute_source_hash,
    find_project_root,
    get_sidecar_path,
    is_binary_file,
    normalize_path,
    read_sidecar,
    write_sidecar,
    write_sidecar_with_retry,
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
        assert result == "sha256:d9014c4624844aa5bac314773d6b689ad467fa4e1d1a50a1b8a99d5a95f72ff5"

    def test_hash_empty_file(self, tmp_path: Path) -> None:
        """Empty file produces valid hash."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        result = compute_source_hash(test_file)

        assert result.startswith("sha256:")
        # Known SHA-256 of empty string
        assert result == "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

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

    def test_path_with_dot_dot_outside_project_raises_error(self, tmp_path: Path) -> None:
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

    def test_path_normalization_removes_redundant_separators(self, tmp_path: Path) -> None:
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


class TestReadSidecar:
    """Tests for read_sidecar function."""

    def test_read_valid_sidecar(self, tmp_path: Path) -> None:
        """Read a valid sidecar JSON file."""
        sidecar_path = tmp_path / "test.json"

        # Create a minimal valid sidecar
        sidecar_data = {
            "source_file": "src/test.py",
            "source_hash": "sha256:" + "a" * 64,
            "schema_version": "1.0",
            "threads": [],
        }

        import json

        sidecar_path.write_text(json.dumps(sidecar_data, indent=2))

        result = read_sidecar(sidecar_path)

        assert isinstance(result, SidecarFile)
        assert result.source_file == "src/test.py"
        assert result.source_hash == "sha256:" + "a" * 64
        assert result.schema_version == "1.0"
        assert result.threads == []

    def test_read_sidecar_with_thread(self, tmp_path: Path) -> None:
        """Read a sidecar with a complete thread."""
        sidecar_path = tmp_path / "test.json"

        import json

        sidecar_data = {
            "source_file": "src/model.py",
            "source_hash": "sha256:" + "b" * 64,
            "schema_version": "1.0",
            "threads": [
                {
                    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                    "status": "open",
                    "created_at": "2026-02-01T10:00:00Z",
                    "resolved_at": None,
                    "comments": [
                        {
                            "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                            "author": "alice",
                            "author_type": "human",
                            "body": "This needs refactoring",
                            "timestamp": "2026-02-01T10:00:00Z",
                        }
                    ],
                    "anchor": {
                        "content_hash": "sha256:" + "c" * 64,
                        "context_hash_before": "sha256:" + "d" * 64,
                        "context_hash_after": "sha256:" + "e" * 64,
                        "line_start": 10,
                        "line_end": 15,
                        "content_snippet": "def calculate_total():",
                        "health": "anchored",
                        "drift_distance": 0,
                    },
                    "decision": None,
                }
            ],
        }

        sidecar_path.write_text(json.dumps(sidecar_data, indent=2))

        result = read_sidecar(sidecar_path)

        assert len(result.threads) == 1
        thread = result.threads[0]
        assert thread.status == ThreadStatus.OPEN
        assert len(thread.comments) == 1
        assert thread.comments[0].author == "alice"
        assert thread.anchor.line_start == 10

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Reading nonexistent file raises FileNotFoundError."""
        nonexistent = tmp_path / "missing.json"

        with pytest.raises(FileNotFoundError, match="Sidecar file not found"):
            read_sidecar(nonexistent)

    def test_read_invalid_json(self, tmp_path: Path) -> None:
        """Reading invalid JSON raises ValueError."""
        sidecar_path = tmp_path / "invalid.json"
        sidecar_path.write_text("{ invalid json content")

        with pytest.raises(ValueError, match="Invalid JSON"):
            read_sidecar(sidecar_path)

    def test_read_schema_validation_failure(self, tmp_path: Path) -> None:
        """Reading JSON that fails schema validation raises ValueError."""
        sidecar_path = tmp_path / "bad_schema.json"

        import json

        # Missing required field source_hash
        bad_data = {
            "source_file": "test.py",
            "schema_version": "1.0",
            "threads": [],
        }

        sidecar_path.write_text(json.dumps(bad_data))

        with pytest.raises(ValueError, match="schema validation"):
            read_sidecar(sidecar_path)

    def test_read_directory_not_file(self, tmp_path: Path) -> None:
        """Reading a directory raises ValueError."""
        directory = tmp_path / "dir"
        directory.mkdir()

        with pytest.raises(ValueError, match="not a file"):
            read_sidecar(directory)


class TestWriteSidecar:
    """Tests for write_sidecar function."""

    def test_write_minimal_sidecar(self, tmp_path: Path) -> None:
        """Write a minimal valid sidecar file."""
        sidecar_path = tmp_path / "test.json"
        sidecar = SidecarFile(
            source_file="src/test.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[],
        )

        write_sidecar(sidecar_path, sidecar)

        assert sidecar_path.exists()
        assert sidecar_path.is_file()

        # Verify content
        result = read_sidecar(sidecar_path)
        assert result.source_file == "src/test.py"
        assert result.source_hash == "sha256:" + "a" * 64

    def test_write_sidecar_with_thread(self, tmp_path: Path) -> None:
        """Write a sidecar with a complete thread."""
        sidecar_path = tmp_path / "test.json"

        anchor = Anchor(
            content_hash="sha256:" + "c" * 64,
            context_hash_before="sha256:" + "d" * 64,
            context_hash_after="sha256:" + "e" * 64,
            line_start=10,
            line_end=15,
            content_snippet="def calculate():",
            health=AnchorHealth.ANCHORED,
            drift_distance=0,
        )

        thread = Thread(
            id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            status=ThreadStatus.OPEN,
            created_at="2026-02-01T10:00:00Z",
            anchor=anchor,
        )

        thread.add_comment(
            author="alice",
            author_type=AuthorType.HUMAN,
            body="Needs refactoring",
            timestamp="2026-02-01T10:00:00Z",
        )

        sidecar = SidecarFile(
            source_file="src/model.py",
            source_hash="sha256:" + "b" * 64,
            threads=[thread],
        )

        write_sidecar(sidecar_path, sidecar)

        # Read back and verify
        result = read_sidecar(sidecar_path)
        assert len(result.threads) == 1
        assert result.threads[0].comments[0].author == "alice"

    def test_write_creates_parent_directories(self, tmp_path: Path) -> None:
        """Writing to deep path creates all parent directories."""
        deep_path = tmp_path / ".comments" / "src" / "foo" / "bar" / "baz.py.json"
        sidecar = SidecarFile(
            source_file="src/foo/bar/baz.py",
            source_hash="sha256:" + "a" * 64,
        )

        write_sidecar(deep_path, sidecar)

        assert deep_path.exists()
        assert deep_path.parent.exists()
        assert deep_path.parent.parent.exists()

    def test_write_deterministic_json(self, tmp_path: Path) -> None:
        """Same sidecar produces byte-for-byte identical JSON."""
        sidecar_path1 = tmp_path / "test1.json"
        sidecar_path2 = tmp_path / "test2.json"

        anchor = Anchor(
            content_hash="sha256:" + "c" * 64,
            context_hash_before="sha256:" + "d" * 64,
            context_hash_after="sha256:" + "e" * 64,
            line_start=10,
            line_end=15,
            content_snippet="def foo():",
            health=AnchorHealth.DRIFTED,
            drift_distance=5,
        )

        thread = Thread(
            id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            status=ThreadStatus.RESOLVED,
            created_at="2026-02-01T10:00:00Z",
            resolved_at="2026-02-01T11:00:00Z",
            anchor=anchor,
            decision=Decision(
                summary="Fixed by refactoring",
                decider="bob",
                timestamp="2026-02-01T11:00:00Z",
            ),
        )

        sidecar = SidecarFile(
            source_file="src/test.py",
            source_hash="sha256:" + "a" * 64,
            threads=[thread],
        )

        # Write twice
        write_sidecar(sidecar_path1, sidecar)
        write_sidecar(sidecar_path2, sidecar)

        # Compare byte-for-byte
        content1 = sidecar_path1.read_bytes()
        content2 = sidecar_path2.read_bytes()

        assert content1 == content2

    def test_write_sorted_keys(self, tmp_path: Path) -> None:
        """JSON output has sorted keys for git-friendly diffs."""
        sidecar_path = tmp_path / "test.json"
        sidecar = SidecarFile(
            source_file="src/test.py",
            source_hash="sha256:" + "a" * 64,
        )

        write_sidecar(sidecar_path, sidecar)

        content = sidecar_path.read_text()
        import json

        data = json.loads(content)

        # Check that keys appear in sorted order
        keys = list(data.keys())
        assert keys == sorted(keys)

    def test_write_2_space_indent(self, tmp_path: Path) -> None:
        """JSON output uses 2-space indentation."""
        sidecar_path = tmp_path / "test.json"
        sidecar = SidecarFile(
            source_file="src/test.py",
            source_hash="sha256:" + "a" * 64,
        )

        write_sidecar(sidecar_path, sidecar)

        content = sidecar_path.read_text()

        # Check for 2-space indentation (look for a nested key)
        assert '  "schema_version"' in content or '  "source_file"' in content

    def test_write_trailing_newline(self, tmp_path: Path) -> None:
        """JSON output ends with newline (POSIX convention)."""
        sidecar_path = tmp_path / "test.json"
        sidecar = SidecarFile(
            source_file="src/test.py",
            source_hash="sha256:" + "a" * 64,
        )

        write_sidecar(sidecar_path, sidecar)

        content = sidecar_path.read_text()
        assert content.endswith("\n")

    def test_write_atomic_operation(self, tmp_path: Path) -> None:
        """Write uses temp file + rename (atomic operation)."""
        sidecar_path = tmp_path / "test.json"

        # Create existing sidecar
        existing = SidecarFile(
            source_file="src/old.py",
            source_hash="sha256:" + "a" * 64,
        )
        write_sidecar(sidecar_path, existing)

        # Write new sidecar
        new_sidecar = SidecarFile(
            source_file="src/new.py",
            source_hash="sha256:" + "b" * 64,
        )
        write_sidecar(sidecar_path, new_sidecar)

        # Verify new content
        result = read_sidecar(sidecar_path)
        assert result.source_file == "src/new.py"

        # Verify no temp files left behind
        temp_files = list(tmp_path.glob(".tmp_*.json"))
        assert len(temp_files) == 0


class TestSidecarRoundTrip:
    """Integration tests for read/write round-trip."""

    def test_roundtrip_minimal(self, tmp_path: Path) -> None:
        """Minimal sidecar survives read/write round-trip."""
        sidecar_path = tmp_path / "test.json"
        original = SidecarFile(
            source_file="src/test.py",
            source_hash="sha256:" + "a" * 64,
        )

        write_sidecar(sidecar_path, original)
        restored = read_sidecar(sidecar_path)

        assert restored.source_file == original.source_file
        assert restored.source_hash == original.source_hash
        assert restored.schema_version == original.schema_version
        assert restored.threads == original.threads

    def test_roundtrip_complex(self, tmp_path: Path) -> None:
        """Complex sidecar with multiple threads survives round-trip."""
        sidecar_path = tmp_path / "complex.json"

        # Create complex sidecar with multiple threads
        threads = []
        for i in range(3):
            anchor = Anchor(
                content_hash=f"sha256:{'a' * 63}{i}",
                context_hash_before=f"sha256:{'b' * 63}{i}",
                context_hash_after=f"sha256:{'c' * 63}{i}",
                line_start=(i + 1) * 10,
                line_end=(i + 1) * 10 + 5,
                content_snippet=f"def func_{i}():",
                health=AnchorHealth.ANCHORED,
            )
            thread = Thread(
                id=f"01ARZ3NDEKTSV4RRFFQ69G5FA{i}",
                anchor=anchor,
            )
            thread.add_comment(
                author=f"user_{i}",
                author_type=AuthorType.HUMAN,
                body=f"Comment {i}",
            )
            threads.append(thread)

        original = SidecarFile(
            source_file="src/complex.py",
            source_hash="sha256:" + "f" * 64,
            threads=threads,
        )

        write_sidecar(sidecar_path, original)
        restored = read_sidecar(sidecar_path)

        assert len(restored.threads) == 3
        for i, thread in enumerate(restored.threads):
            assert thread.anchor.content_snippet == f"def func_{i}():"
            assert thread.comments[0].body == f"Comment {i}"

    def test_roundtrip_preserves_decision(self, tmp_path: Path) -> None:
        """Round-trip preserves decision on resolved thread."""
        sidecar_path = tmp_path / "test.json"

        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )

        thread = Thread(
            id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            anchor=anchor,
        )
        thread.resolve(decider="alice", summary="Fixed in commit abc123")

        original = SidecarFile(
            source_file="src/test.py",
            source_hash="sha256:" + "d" * 64,
            threads=[thread],
        )

        write_sidecar(sidecar_path, original)
        restored = read_sidecar(sidecar_path)

        assert restored.threads[0].status == ThreadStatus.RESOLVED
        assert restored.threads[0].decision is not None
        assert restored.threads[0].decision.summary == "Fixed in commit abc123"
        assert restored.threads[0].decision.decider == "alice"


class TestOptimisticConcurrency:
    """Tests for optimistic concurrency control (Task 6.2)."""

    def test_write_succeeds_when_hash_matches(self, tmp_path: Path) -> None:
        """Write succeeds when source hash matches current file."""
        # Create source file
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\ny = 2\n")
        source_hash = compute_source_hash(source_file)

        # Create sidecar
        sidecar_path = tmp_path / ".comments" / "test.py.json"
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )
        thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
        sidecar = SidecarFile(
            source_file=str(source_file),
            source_hash=source_hash,
            threads=[thread],
        )

        # Write with hash check - should succeed
        write_sidecar(sidecar_path, sidecar, check_hash=True)

        # Verify file was written
        assert sidecar_path.exists()
        restored = read_sidecar(sidecar_path)
        assert len(restored.threads) == 1

    def test_write_fails_when_hash_mismatches(self, tmp_path: Path) -> None:
        """Write fails when source hash doesn't match current file."""
        # Create source file with initial content
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\ny = 2\n")
        old_hash = compute_source_hash(source_file)

        # Modify source file (simulating concurrent modification)
        source_file.write_text("x = 1\ny = 2\nz = 3\n")

        # Create sidecar with OLD hash
        sidecar_path = tmp_path / ".comments" / "test.py.json"
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )
        thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
        sidecar = SidecarFile(
            source_file=str(source_file),
            source_hash=old_hash,  # Stale hash
            threads=[thread],
        )

        # Write with hash check - should fail
        with pytest.raises(ConcurrencyConflict, match="Source file hash mismatch"):
            write_sidecar(sidecar_path, sidecar, check_hash=True)

        # Verify sidecar was NOT written (file may exist from lock but should be empty)
        if sidecar_path.exists():
            # Lock creates file, but no content should be written
            assert sidecar_path.stat().st_size == 0
        # OR file doesn't exist at all (acceptable)

    def test_write_with_check_hash_false_skips_validation(self, tmp_path: Path) -> None:
        """Write with check_hash=False bypasses hash check."""
        # Create source file with initial content
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")
        old_hash = compute_source_hash(source_file)

        # Modify source file
        source_file.write_text("x = 1\ny = 2\n")

        # Create sidecar with OLD hash
        sidecar_path = tmp_path / ".comments" / "test.py.json"
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )
        thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
        sidecar = SidecarFile(
            source_file=str(source_file),
            source_hash=old_hash,  # Stale hash
            threads=[thread],
        )

        # Write with check_hash=False - should succeed despite stale hash
        write_sidecar(sidecar_path, sidecar, check_hash=False)

        # Verify file was written
        assert sidecar_path.exists()

    def test_write_allows_deleted_source_file(self, tmp_path: Path) -> None:
        """Write succeeds if source file is deleted (orphaned anchors scenario)."""
        # Create source file temporarily to get hash
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")
        source_hash = compute_source_hash(source_file)

        # Delete source file (simulating file deletion)
        source_file.unlink()

        # Create sidecar with hash from deleted file
        sidecar_path = tmp_path / ".comments" / "test.py.json"
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )
        thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
        sidecar = SidecarFile(
            source_file=str(source_file),
            source_hash=source_hash,
            threads=[thread],
        )

        # Write with hash check - should succeed (skips check for deleted files)
        write_sidecar(sidecar_path, sidecar, check_hash=True)

        # Verify file was written
        assert sidecar_path.exists()

    def test_write_with_acquire_lock_false_skips_locking(self, tmp_path: Path) -> None:
        """Write with acquire_lock=False bypasses file locking."""
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")
        source_hash = compute_source_hash(source_file)

        sidecar_path = tmp_path / ".comments" / "test.py.json"
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )
        thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
        sidecar = SidecarFile(
            source_file=str(source_file),
            source_hash=source_hash,
            threads=[thread],
        )

        # Write without locking - should succeed quickly
        start = time.time()
        write_sidecar(sidecar_path, sidecar, acquire_lock=False)
        elapsed = time.time() - start

        # Should be fast (no lock acquisition overhead)
        assert elapsed < 0.5
        assert sidecar_path.exists()

    def test_concurrent_writes_with_locking(self, tmp_path: Path) -> None:
        """Concurrent writes serialize when locking is enabled."""
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")

        sidecar_path = tmp_path / ".comments" / "test.py.json"

        def write_process(process_id: int) -> None:
            """Write a sidecar from a separate process."""
            # Recompute hash in child process
            hash_val = compute_source_hash(source_file)
            anchor = Anchor(
                content_hash=f"sha256:{'a' * 64}",
                context_hash_before=f"sha256:{'b' * 64}",
                context_hash_after=f"sha256:{'c' * 64}",
                line_start=process_id,
                line_end=process_id,
                content_snippet=f"line {process_id}",
            )
            thread = Thread(id=f"01ARZ3NDEKTSV4RRFFQ69G5F{process_id:02d}", anchor=anchor)
            sidecar = SidecarFile(
                source_file=str(source_file),
                source_hash=hash_val,
                threads=[thread],
            )
            write_sidecar(sidecar_path, sidecar, check_hash=False, acquire_lock=True)

        # Spawn 3 processes to write concurrently
        processes = []
        for i in range(3):
            p = multiprocessing.Process(target=write_process, args=(i,))
            processes.append(p)
            p.start()

        # Wait for all to complete
        for p in processes:
            p.join()

        # Verify file was written (last writer wins)
        assert sidecar_path.exists()
        restored = read_sidecar(sidecar_path)
        assert len(restored.threads) == 1


class TestWriteSidecarWithRetry:
    """Tests for write_sidecar_with_retry function."""

    def test_retry_succeeds_on_first_attempt(self, tmp_path: Path) -> None:
        """Retry succeeds immediately when no conflict."""
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")
        source_hash = compute_source_hash(source_file)

        sidecar_path = tmp_path / ".comments" / "test.py.json"

        # Create initial sidecar
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )
        thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
        initial = SidecarFile(
            source_file=str(source_file),
            source_hash=source_hash,
            threads=[thread],
        )
        write_sidecar(sidecar_path, initial, check_hash=False, acquire_lock=False)

        # Update function: add a comment
        def add_comment(sidecar: SidecarFile) -> SidecarFile:
            sidecar.threads[0].add_comment("alice", AuthorType.HUMAN, "New comment")
            return sidecar

        # Retry should succeed on first attempt
        result = write_sidecar_with_retry(sidecar_path, add_comment, max_retries=3)

        assert len(result.threads[0].comments) == 1
        assert result.threads[0].comments[0].body == "New comment"

    def test_retry_recovers_from_single_conflict(self, tmp_path: Path) -> None:
        """Retry recovers when external process modifies source file."""
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")
        initial_hash = compute_source_hash(source_file)

        sidecar_path = tmp_path / ".comments" / "test.py.json"

        # Create initial sidecar
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )
        thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
        initial = SidecarFile(
            source_file=str(source_file),
            source_hash=initial_hash,
            threads=[thread],
        )
        write_sidecar(sidecar_path, initial, check_hash=False, acquire_lock=False)

        # Track number of attempts
        attempt_count = 0
        conflict_triggered = False

        def add_comment_with_external_modification(sidecar: SidecarFile) -> SidecarFile:
            nonlocal attempt_count, conflict_triggered

            # On first attempt, simulate external modification AFTER we read the sidecar
            # but BEFORE we write it (classic race condition)
            if attempt_count == 0 and not conflict_triggered:
                # Modify source file (simulates external edit)
                source_file.write_text("x = 1\ny = 2\n")
                conflict_triggered = True
                # DON'T update the hash - this simulates reading stale data

            attempt_count += 1

            # On retry (attempt 2+), update hash to match new file
            if attempt_count >= 2:
                sidecar.source_hash = compute_source_hash(source_file)

            # Add comment
            sidecar.threads[0].add_comment("bob", AuthorType.HUMAN, "Added comment")
            return sidecar

        # Retry should fail first time (stale hash), succeed second time (updated hash)
        result = write_sidecar_with_retry(
            sidecar_path, add_comment_with_external_modification, max_retries=3
        )

        assert attempt_count == 2  # First failed, second succeeded
        assert len(result.threads[0].comments) == 1

    def test_retry_fails_after_max_attempts(self, tmp_path: Path) -> None:
        """Retry raises ConcurrencyConflict after max_retries exceeded."""
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")
        initial_hash = compute_source_hash(source_file)

        sidecar_path = tmp_path / ".comments" / "test.py.json"

        # Create initial sidecar
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="x = 1",
        )
        thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
        initial = SidecarFile(
            source_file=str(source_file),
            source_hash=initial_hash,
            threads=[thread],
        )
        write_sidecar(sidecar_path, initial, check_hash=False, acquire_lock=False)

        # Track attempts
        attempt_count = 0
        # Track modifications per attempt to ensure continuous conflicts
        modifications = {}

        def always_conflict(sidecar: SidecarFile) -> SidecarFile:
            nonlocal attempt_count
            attempt_count += 1

            # On each read (before update_fn is called), source file has current content
            # Modify it to create a new hash that doesn't match what we're about to write
            current_content = source_file.read_text()
            source_file.write_text(current_content + f"# modification {attempt_count}\n")
            modifications[attempt_count] = source_file.read_text()

            # Return sidecar with OLD hash (before our modification)
            # This will fail hash check every time
            sidecar.threads[0].add_comment("eve", AuthorType.AGENT, f"Attempt {attempt_count}")
            return sidecar

        # Should fail after 3 attempts
        with pytest.raises(ConcurrencyConflict, match="after 3 attempts"):
            write_sidecar_with_retry(sidecar_path, always_conflict, max_retries=3)

        assert attempt_count == 3

    def test_retry_handles_missing_sidecar(self, tmp_path: Path) -> None:
        """Retry handles case where sidecar doesn't exist yet."""
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")
        source_hash = compute_source_hash(source_file)

        sidecar_path = tmp_path / ".comments" / "test.py.json"
        # Sidecar doesn't exist yet

        def create_initial(sidecar: SidecarFile | None) -> SidecarFile:
            # Handle None case (missing sidecar)
            if sidecar is None:
                anchor = Anchor(
                    content_hash="sha256:" + "a" * 64,
                    context_hash_before="sha256:" + "b" * 64,
                    context_hash_after="sha256:" + "c" * 64,
                    line_start=1,
                    line_end=1,
                    content_snippet="x = 1",
                )
                thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
                return SidecarFile(
                    source_file=str(source_file),
                    source_hash=source_hash,
                    threads=[thread],
                )
            return sidecar

        # Should create new sidecar
        result = write_sidecar_with_retry(sidecar_path, create_initial, max_retries=3)

        assert result.threads[0].anchor.content_snippet == "x = 1"
        assert sidecar_path.exists()

    def test_retry_respects_custom_timeout(self, tmp_path: Path) -> None:
        """Retry uses custom timeout parameter."""
        source_file = tmp_path / "test.py"
        source_file.write_text("x = 1\n")
        source_hash = compute_source_hash(source_file)

        sidecar_path = tmp_path / ".comments" / "test.py.json"

        def create_sidecar(sidecar: SidecarFile | None) -> SidecarFile:
            anchor = Anchor(
                content_hash="sha256:" + "a" * 64,
                context_hash_before="sha256:" + "b" * 64,
                context_hash_after="sha256:" + "c" * 64,
                line_start=1,
                line_end=1,
                content_snippet="x = 1",
            )
            thread = Thread(id="01ARZ3NDEKTSV4RRFFQ69G5FAV", anchor=anchor)
            return SidecarFile(
                source_file=str(source_file),
                source_hash=source_hash,
                threads=[thread],
            )

        # Should succeed with custom timeout
        result = write_sidecar_with_retry(sidecar_path, create_sidecar, max_retries=1, timeout=10.0)

        assert sidecar_path.exists()
        assert result.source_hash == source_hash

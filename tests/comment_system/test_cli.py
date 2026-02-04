"""Tests for CLI interface."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from comment_system.cli import cli, create_anchor, extract_lines
from comment_system.models import AnchorHealth
from comment_system.storage import read_sidecar


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample source file with known content."""
    content = """Line 1
Line 2
Line 3
Line 4
Line 5
Line 6
Line 7
Line 8
Line 9
Line 10
"""
    file_path = tmp_path / "test.txt"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository and change to it."""
    import os

    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    # Change to git repo directory for tests
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    yield tmp_path

    # Restore original directory
    os.chdir(original_cwd)


# ============================================================================
# Unit Tests: extract_lines()
# ============================================================================


def test_extract_lines_single_line(sample_file):
    """Test extracting a single line with context."""
    content, context_before, context_after = extract_lines(sample_file, 5, 5)

    assert content == "Line 5"
    assert context_before == "Line 2\nLine 3\nLine 4"
    assert context_after == "Line 6\nLine 7\nLine 8"


def test_extract_lines_multiple_lines(sample_file):
    """Test extracting multiple lines."""
    content, context_before, context_after = extract_lines(sample_file, 3, 5)

    assert content == "Line 3\nLine 4\nLine 5"
    assert context_before == "Line 1\nLine 2"
    assert context_after == "Line 6\nLine 7\nLine 8"


def test_extract_lines_at_start(sample_file):
    """Test extracting lines at file start (no context before)."""
    content, context_before, context_after = extract_lines(sample_file, 1, 2)

    assert content == "Line 1\nLine 2"
    assert context_before == ""
    assert context_after == "Line 3\nLine 4\nLine 5"


def test_extract_lines_at_end(sample_file):
    """Test extracting lines at file end (limited context after)."""
    content, context_before, context_after = extract_lines(sample_file, 9, 10)

    assert content == "Line 9\nLine 10"
    assert context_before == "Line 6\nLine 7\nLine 8"
    assert context_after == ""


def test_extract_lines_file_not_found(tmp_path):
    """Test error when file doesn't exist."""
    nonexistent = tmp_path / "nonexistent.txt"
    with pytest.raises(FileNotFoundError, match="Source file not found"):
        extract_lines(nonexistent, 1, 1)


def test_extract_lines_invalid_line_start(sample_file):
    """Test error when line_start is out of range."""
    with pytest.raises(ValueError, match="Invalid line_start: 0"):
        extract_lines(sample_file, 0, 1)

    with pytest.raises(ValueError, match="Invalid line_start: 100"):
        extract_lines(sample_file, 100, 100)


def test_extract_lines_invalid_line_end(sample_file):
    """Test error when line_end is out of range."""
    with pytest.raises(ValueError, match="Invalid line_end: 0"):
        extract_lines(sample_file, 1, 0)

    with pytest.raises(ValueError, match="Invalid line_end: 100"):
        extract_lines(sample_file, 1, 100)


def test_extract_lines_end_before_start(sample_file):
    """Test error when line_end < line_start."""
    with pytest.raises(ValueError, match="line_end .* must be >= line_start"):
        extract_lines(sample_file, 5, 3)


# ============================================================================
# Unit Tests: create_anchor()
# ============================================================================


def test_create_anchor_basic(sample_file):
    """Test creating an anchor with valid line range."""
    anchor = create_anchor(sample_file, 3, 5)

    assert anchor.line_start == 3
    assert anchor.line_end == 5
    assert anchor.content_snippet == "Line 3\nLine 4\nLine 5"
    assert anchor.health == AnchorHealth.ANCHORED
    assert anchor.drift_distance == 0
    assert anchor.content_hash.startswith("sha256:")
    assert anchor.context_hash_before.startswith("sha256:")
    assert anchor.context_hash_after.startswith("sha256:")


def test_create_anchor_single_line(sample_file):
    """Test creating an anchor for a single line."""
    anchor = create_anchor(sample_file, 5, 5)

    assert anchor.line_start == 5
    assert anchor.line_end == 5
    assert anchor.content_snippet == "Line 5"


def test_create_anchor_truncates_long_snippet(tmp_path):
    """Test that snippet is truncated to 500 chars max."""
    long_line = "x" * 600
    file_path = tmp_path / "long.txt"
    file_path.write_text(long_line)

    anchor = create_anchor(file_path, 1, 1)

    assert len(anchor.content_snippet) == 500
    assert anchor.content_snippet.endswith("...")


def test_create_anchor_file_not_found(tmp_path):
    """Test error when file doesn't exist."""
    nonexistent = tmp_path / "nonexistent.txt"
    with pytest.raises(FileNotFoundError):
        create_anchor(nonexistent, 1, 1)


def test_create_anchor_invalid_lines(sample_file):
    """Test error with invalid line numbers."""
    with pytest.raises(ValueError):
        create_anchor(sample_file, 0, 1)

    with pytest.raises(ValueError):
        create_anchor(sample_file, 1, 100)


# ============================================================================
# Integration Tests: comment add
# ============================================================================


def test_add_creates_thread(runner, git_repo):
    """Test AC-1: comment add creates thread and prints ID."""
    # Create sample file
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\n")

    # Run command
    result = runner.invoke(
        cli,
        ["add", str(file_path), "-L", "1:2", "--author", "alice", "Test comment"],
    )

    # Verify success
    assert result.exit_code == 0
    assert "Created thread" in result.output
    assert "File: test.txt" in result.output
    assert "Lines: 1:2" in result.output

    # Verify sidecar was created
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    assert sidecar_path.exists()

    # Verify sidecar content
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads) == 1
    thread = sidecar.threads[0]
    assert len(thread.comments) == 1
    assert thread.comments[0].author == "alice"
    assert thread.comments[0].body == "Test comment"
    assert thread.anchor.line_start == 1
    assert thread.anchor.line_end == 2


def test_add_appends_to_existing_sidecar(runner, git_repo):
    """Test that add appends to existing sidecar."""
    # Create sample file
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\n")

    # Add first thread
    result1 = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "First comment"])
    assert result1.exit_code == 0

    # Add second thread
    result2 = runner.invoke(cli, ["add", str(file_path), "-L", "2:2", "Second comment"])
    assert result2.exit_code == 0

    # Verify both threads exist
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads) == 2
    assert sidecar.threads[0].comments[0].body == "First comment"
    assert sidecar.threads[1].comments[0].body == "Second comment"


def test_add_with_agent_author_type(runner, git_repo):
    """Test adding comment with agent author type."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\n")

    result = runner.invoke(
        cli,
        [
            "add",
            str(file_path),
            "-L",
            "1:1",
            "--author",
            "claude",
            "--author-type",
            "agent",
            "Agent comment",
        ],
    )

    assert result.exit_code == 0

    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].comments[0].author_type.value == "agent"


def test_add_updates_source_hash(runner, git_repo):
    """Test that source hash is updated on each add."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Original content\n")

    # Add first thread
    result1 = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "First"])
    assert result1.exit_code == 0

    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar1 = read_sidecar(sidecar_path)
    hash1 = sidecar1.source_hash

    # Modify file
    file_path.write_text("Modified content\n")

    # Add second thread
    result2 = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Second"])
    assert result2.exit_code == 0

    sidecar2 = read_sidecar(sidecar_path)
    hash2 = sidecar2.source_hash

    # Hash should be updated
    assert hash1 != hash2


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_add_invalid_line_range_format(runner, git_repo):
    """Test error with invalid line range format."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1", "Comment"])

    assert result.exit_code == 1
    assert "Invalid line range format" in result.output


def test_add_invalid_line_numbers(runner, git_repo):
    """Test error with non-integer line numbers."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "abc:def", "Comment"])

    assert result.exit_code == 1
    assert "Invalid line range" in result.output


def test_add_line_out_of_range(runner, git_repo):
    """Test error when line numbers are out of range."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\n")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:100", "Comment"])

    assert result.exit_code == 1
    assert "Invalid line_end: 100" in result.output


def test_add_file_not_found(runner, git_repo):
    """Test error when source file doesn't exist."""
    nonexistent = git_repo / "nonexistent.txt"

    result = runner.invoke(cli, ["add", str(nonexistent), "-L", "1:1", "Comment"])

    # File existence checked by Click before command runs
    assert result.exit_code != 0


def test_add_no_git_repo(runner, tmp_path):
    """Test error when not in a git repository."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\n")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])

    assert result.exit_code == 2
    assert "No .git directory found" in result.output


def test_add_file_outside_repo(runner, git_repo):
    """Test error when file is outside git repository."""
    import tempfile

    # Create file outside git repo in a completely different temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        outside_file = Path(tmpdir) / "outside.txt"
        outside_file.write_text("Line 1\n")

        # We're already in git_repo thanks to the fixture
        result = runner.invoke(cli, ["add", str(outside_file), "-L", "1:1", "Comment"])

        assert result.exit_code == 1
        assert "outside project root" in result.output


# ============================================================================
# Output Format Tests
# ============================================================================


def test_add_output_format(runner, git_repo):
    """Test that add output includes all required information."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\n")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:2", "Test"])

    assert result.exit_code == 0
    # Check for thread ID (26-char ULID)
    assert "Created thread" in result.output
    # Check for file path
    assert "File: test.txt" in result.output
    # Check for line range
    assert "Lines: 1:2" in result.output
    # Check for sidecar path
    assert "Sidecar: .comments/test.txt.json" in result.output


def test_add_nested_file_path(runner, git_repo):
    """Test adding comment to file in nested directory."""
    # Create nested directory structure
    nested_dir = git_repo / "src" / "foo"
    nested_dir.mkdir(parents=True)
    file_path = nested_dir / "bar.py"
    file_path.write_text("def foo():\n    pass\n")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:2", "Fix this"])

    assert result.exit_code == 0

    # Verify sidecar path mirrors structure
    sidecar_path = git_repo / ".comments" / "src" / "foo" / "bar.py.json"
    assert sidecar_path.exists()

    # Verify relative path in sidecar
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.source_file == "src/foo/bar.py"


# ============================================================================
# Edge Cases
# ============================================================================


def test_add_single_line_file(runner, git_repo):
    """Test adding comment to single-line file."""
    file_path = git_repo / "single.txt"
    file_path.write_text("Only one line")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])

    assert result.exit_code == 0

    sidecar_path = git_repo / ".comments" / "single.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads) == 1
    assert sidecar.threads[0].anchor.content_snippet == "Only one line"


def test_add_empty_context(runner, git_repo):
    """Test that empty context creates valid hashes."""
    file_path = git_repo / "single.txt"
    file_path.write_text("Only line")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])

    assert result.exit_code == 0

    sidecar_path = git_repo / ".comments" / "single.txt.json"
    sidecar = read_sidecar(sidecar_path)
    anchor = sidecar.threads[0].anchor

    # Empty context should still produce valid SHA-256 hash
    assert anchor.context_hash_before.startswith("sha256:")
    assert anchor.context_hash_after.startswith("sha256:")


def test_add_multiline_body(runner, git_repo):
    """Test adding comment with multiline body."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    multiline_body = "This is a comment\nwith multiple lines\nof text"

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", multiline_body])

    assert result.exit_code == 0

    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].comments[0].body == multiline_body


def test_add_special_characters_in_body(runner, git_repo):
    """Test adding comment with special characters."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    special_body = "Test \"quotes\" and 'apostrophes' and <tags>"

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", special_body])

    assert result.exit_code == 0

    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].comments[0].body == special_body


def test_add_unicode_content(runner, git_repo):
    """Test adding comment to file with unicode content."""
    file_path = git_repo / "unicode.txt"
    file_path.write_text("Unicode: 你好 🎉\n", encoding="utf-8")

    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment on unicode"])

    assert result.exit_code == 0

    sidecar_path = git_repo / ".comments" / "unicode.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert "Unicode: 你好 🎉" in sidecar.threads[0].anchor.content_snippet


def test_add_with_match_single_occurrence(runner, git_repo):
    """Test --match flag with single text occurrence."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2 unique text\nLine 3\n")

    result = runner.invoke(
        cli, ["add", str(file_path), "--match", "unique text", "Comment on matched line"]
    )

    assert result.exit_code == 0
    assert "Created thread" in result.output
    assert "Lines: 2:2" in result.output

    # Verify sidecar has correct line range
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads) == 1
    assert sidecar.threads[0].anchor.line_start == 2
    assert sidecar.threads[0].anchor.line_end == 2
    assert "unique text" in sidecar.threads[0].anchor.content_snippet


def test_add_with_match_ambiguous(runner, git_repo):
    """Test AC-4: --match flag fails with ambiguous match (multiple occurrences)."""
    file_path = git_repo / "test.txt"
    file_path.write_text("linear scaling\nLine 2\nlinear scaling\n")

    result = runner.invoke(
        cli, ["add", str(file_path), "--match", "linear scaling", "This should fail"]
    )

    assert result.exit_code == 1
    assert "Ambiguous match" in result.output
    assert "2 times" in result.output
    assert "1, 3" in result.output

    # Verify sidecar was NOT created
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    assert not sidecar_path.exists()


def test_add_with_match_not_found(runner, git_repo):
    """Test --match flag fails when text is not found."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\n")

    result = runner.invoke(
        cli, ["add", str(file_path), "--match", "nonexistent", "This should fail"]
    )

    assert result.exit_code == 1
    assert "Text not found: 'nonexistent'" in result.output

    # Verify sidecar was NOT created
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    assert not sidecar_path.exists()


def test_add_with_match_and_lines_mutually_exclusive(runner, git_repo):
    """Test that -L and --match cannot be used together."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\n")

    result = runner.invoke(
        cli,
        [
            "add",
            str(file_path),
            "-L",
            "1:1",
            "--match",
            "Line 2",
            "This should fail",
        ],
    )

    assert result.exit_code == 1
    assert "mutually exclusive" in result.output

    # Verify sidecar was NOT created
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    assert not sidecar_path.exists()


def test_add_with_neither_match_nor_lines(runner, git_repo):
    """Test that either -L or --match must be specified."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\n")

    result = runner.invoke(cli, ["add", str(file_path), "This should fail"])

    assert result.exit_code == 1
    assert "Must specify either -L" in result.output or "must specify" in result.output.lower()

    # Verify sidecar was NOT created
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    assert not sidecar_path.exists()


# ============================================================================
# Tests: list command
# ============================================================================


def test_list_single_file(runner, git_repo):
    """Test listing threads from a single file."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\n")

    # Create two threads
    runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "First comment"])
    runner.invoke(cli, ["add", str(file_path), "-L", "2:2", "Second comment"])

    # List threads
    result = runner.invoke(cli, ["list", str(file_path)])

    assert result.exit_code == 0
    assert "test.txt:1:1" in result.output
    assert "test.txt:2:2" in result.output
    assert "(1 comments)" in result.output


def test_list_no_threads(runner, git_repo):
    """Test listing when no threads exist."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    result = runner.invoke(cli, ["list", str(file_path)])

    assert result.exit_code == 0
    assert "No matching threads found" in result.output


def test_list_filter_by_status(runner, git_repo):
    """Test filtering threads by status."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\n")

    # Create open thread
    result1 = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Open thread"])
    assert result1.exit_code == 0

    # List only open threads
    result = runner.invoke(cli, ["list", str(file_path), "--status", "open"])

    assert result.exit_code == 0
    assert "open" in result.output.lower()


def test_list_filter_by_health(runner, git_repo):
    """Test filtering threads by anchor health."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])

    # List only anchored threads
    result = runner.invoke(cli, ["list", str(file_path), "--health", "anchored"])

    assert result.exit_code == 0
    assert "anchored" in result.output.lower()


def test_list_json_output(runner, git_repo):
    """Test JSON output format."""
    import json

    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])

    result = runner.invoke(cli, ["list", str(file_path), "--json"])

    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 1
    assert "id" in data[0]
    assert "source_file" in data[0]
    assert "status" in data[0]
    assert "anchor" in data[0]
    assert data[0]["source_file"] == "test.txt"


def test_list_all_files(runner, git_repo):
    """Test listing threads from all files."""
    file1 = git_repo / "test1.txt"
    file1.write_text("Line 1\n")
    file2 = git_repo / "test2.txt"
    file2.write_text("Line 1\n")

    runner.invoke(cli, ["add", str(file1), "-L", "1:1", "Comment 1"])
    runner.invoke(cli, ["add", str(file2), "-L", "1:1", "Comment 2"])

    result = runner.invoke(cli, ["list", "--all"])

    assert result.exit_code == 0
    assert "test1.txt:1:1" in result.output
    assert "test2.txt:1:1" in result.output


def test_list_all_and_file_path_error(runner, git_repo):
    """Test error when both --all and file path are specified."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    result = runner.invoke(cli, ["list", str(file_path), "--all"])

    assert result.exit_code == 1
    assert "Cannot specify both --all and a file path" in result.output


def test_list_no_arguments_error(runner, git_repo):
    """Test error when neither --all nor file path is specified."""
    result = runner.invoke(cli, ["list"])

    assert result.exit_code == 1
    assert "Must specify either a file path or --all" in result.output


def test_list_respects_no_color(runner, git_repo, monkeypatch):
    """Test that NO_COLOR environment variable is respected."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])

    # Set NO_COLOR environment variable
    monkeypatch.setenv("NO_COLOR", "1")

    result = runner.invoke(cli, ["list", str(file_path)])

    assert result.exit_code == 0
    # Check that output doesn't contain ANSI escape codes
    assert "\x1b[" not in result.output


def test_list_with_color(runner, git_repo, monkeypatch):
    """Test that color codes are present when NO_COLOR is not set."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])

    # Ensure NO_COLOR is not set
    monkeypatch.delenv("NO_COLOR", raising=False)

    # Use color=True to force color output in test environment
    result = runner.invoke(cli, ["list", str(file_path)], color=True)

    assert result.exit_code == 0
    # Check that output contains ANSI escape codes for color
    assert "\x1b[" in result.output


def test_list_filter_by_author(runner, git_repo):
    """Test filtering threads by author."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\n")

    # Create threads with different authors
    runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "--author", "alice", "Alice's comment"])
    runner.invoke(cli, ["add", str(file_path), "-L", "2:2", "--author", "bob", "Bob's comment"])

    # List only alice's threads
    result = runner.invoke(cli, ["list", str(file_path), "--author", "alice"])

    assert result.exit_code == 0
    assert "test.txt:1:1" in result.output
    assert "test.txt:2:2" not in result.output


# ============================================================================
# Tests: show command
# ============================================================================


def test_show_thread(runner, git_repo):
    """Test showing a single thread."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Test comment"])
    assert result.exit_code == 0

    # Extract thread ID from output
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Show thread
    result = runner.invoke(cli, ["show", thread_id])

    assert result.exit_code == 0
    assert f"Thread: {thread_id}" in result.output
    assert "Status: open" in result.output
    assert "test.txt:1:1" in result.output
    assert "Anchor Health: anchored" in result.output
    assert "Test comment" in result.output


def test_show_thread_not_found(runner, git_repo):
    """Test showing a non-existent thread."""
    result = runner.invoke(cli, ["show", "01HQNONEXISTENT000000000"])

    assert result.exit_code == 1
    assert "Thread not found" in result.output


def test_show_json_output(runner, git_repo):
    """Test JSON output format for show command."""
    import json

    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Test comment"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Show thread as JSON
    result = runner.invoke(cli, ["show", thread_id, "--json"])

    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)
    assert data["id"] == thread_id
    assert data["source_file"] == "test.txt"
    assert data["status"] == "open"
    assert "anchor" in data
    assert "comments" in data
    assert len(data["comments"]) == 1
    assert data["comments"][0]["body"] == "Test comment"


def test_show_respects_no_color(runner, git_repo, monkeypatch):
    """Test that NO_COLOR environment variable is respected in show command."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Set NO_COLOR environment variable
    monkeypatch.setenv("NO_COLOR", "1")

    result = runner.invoke(cli, ["show", thread_id])

    assert result.exit_code == 0
    # Check that output doesn't contain ANSI escape codes
    assert "\x1b[" not in result.output


def test_show_with_color(runner, git_repo, monkeypatch):
    """Test that color codes are present in show command when NO_COLOR is not set."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Comment"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Ensure NO_COLOR is not set
    monkeypatch.delenv("NO_COLOR", raising=False)

    # Use color=True to force color output in test environment
    result = runner.invoke(cli, ["show", thread_id], color=True)

    assert result.exit_code == 0
    # Check that output contains ANSI escape codes for color
    assert "\x1b[" in result.output


def test_show_multiple_comments(runner, git_repo):
    """Test showing thread with multiple comments (future: after reply is implemented)."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread with one comment
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "First comment"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Show thread
    result = runner.invoke(cli, ["show", thread_id])

    assert result.exit_code == 0
    assert "Comments:" in result.output
    assert "[1]" in result.output
    assert "First comment" in result.output


# ============================================================================
# Integration Tests: comment reply
# ============================================================================


def test_reply_adds_comment_to_thread(runner, git_repo):
    """Test adding a reply to an existing thread."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create initial thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "First comment"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Add a reply
    result = runner.invoke(cli, ["reply", thread_id, "Second comment"])
    assert result.exit_code == 0
    assert "Added comment" in result.output
    assert f"to thread {thread_id}" in result.output

    # Verify the reply was added
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads) == 1
    assert len(sidecar.threads[0].comments) == 2
    assert sidecar.threads[0].comments[0].body == "First comment"
    assert sidecar.threads[0].comments[1].body == "Second comment"


def test_reply_with_custom_author(runner, git_repo):
    """Test adding a reply with custom author."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create initial thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "First comment"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Add a reply with custom author
    result = runner.invoke(cli, ["reply", "--author", "alice", thread_id, "Reply from alice"])
    assert result.exit_code == 0

    # Verify the author
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].comments[1].author == "alice"


def test_reply_with_agent_author_type(runner, git_repo):
    """Test adding a reply from an agent."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create initial thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "First comment"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Add a reply from agent
    result = runner.invoke(
        cli, ["reply", "--author-type", "agent", "--author", "bot", thread_id, "Agent response"]
    )
    assert result.exit_code == 0

    # Verify the author type
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].comments[1].author_type.value == "agent"
    assert sidecar.threads[0].comments[1].author == "bot"


def test_reply_thread_not_found(runner, git_repo):
    """Test reply to non-existent thread."""
    result = runner.invoke(cli, ["reply", "01HQNONEXISTENT000000000000", "Some comment"])
    assert result.exit_code == 1
    assert "Thread not found" in result.output


def test_reply_multiple_times(runner, git_repo):
    """Test adding multiple replies to same thread."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create initial thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Initial"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Add multiple replies
    for i in range(1, 4):
        result = runner.invoke(cli, ["reply", thread_id, f"Reply {i}"])
        assert result.exit_code == 0

    # Verify all replies were added
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads[0].comments) == 4
    assert sidecar.threads[0].comments[0].body == "Initial"
    assert sidecar.threads[0].comments[1].body == "Reply 1"
    assert sidecar.threads[0].comments[2].body == "Reply 2"
    assert sidecar.threads[0].comments[3].body == "Reply 3"


# ============================================================================
# Integration Tests: comment resolve
# ============================================================================


def test_resolve_thread_with_decision(runner, git_repo):
    """Test resolving a thread with a decision."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Question"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Resolve with decision
    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Fixed in commit abc123"])
    assert result.exit_code == 0
    assert f"Thread {thread_id} marked as resolved" in result.output
    assert "Fixed in commit abc123" in result.output

    # Verify status and decision
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "resolved"
    assert sidecar.threads[0].decision is not None
    assert sidecar.threads[0].decision.summary == "Fixed in commit abc123"
    assert sidecar.threads[0].decision.decider == "unknown"


def test_resolve_thread_with_custom_decider(runner, git_repo):
    """Test resolving with custom decider name."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Question"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Resolve with custom decider
    result = runner.invoke(
        cli, ["resolve", "--decider", "alice", thread_id, "--decision", "Approved"]
    )
    assert result.exit_code == 0

    # Verify decider
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].decision.decider == "alice"


def test_resolve_thread_as_wontfix(runner, git_repo):
    """Test marking thread as wontfix."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Suggestion"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Resolve as wontfix
    result = runner.invoke(cli, ["resolve", "--wontfix", thread_id])
    assert result.exit_code == 0
    assert f"Thread {thread_id} marked as wontfix" in result.output

    # Verify status
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "wontfix"


def test_resolve_wontfix_with_decision(runner, git_repo):
    """Test marking thread as wontfix with optional decision."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Suggestion"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Resolve as wontfix with decision
    result = runner.invoke(cli, ["resolve", "--wontfix", "--decision", "Out of scope", thread_id])
    assert result.exit_code == 0

    # Verify status and decision
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "wontfix"
    assert sidecar.threads[0].decision is not None
    assert sidecar.threads[0].decision.summary == "Out of scope"


def test_resolve_without_decision_fails(runner, git_repo):
    """Test that resolve without --decision or --wontfix fails."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Question"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Try to resolve without decision
    result = runner.invoke(cli, ["resolve", thread_id])
    assert result.exit_code == 1
    assert "--decision is required unless using --wontfix" in result.output


def test_resolve_thread_not_found(runner, git_repo):
    """Test resolve with non-existent thread."""
    result = runner.invoke(cli, ["resolve", "01HQNONEXISTENT000000000000", "--decision", "Done"])
    assert result.exit_code == 1
    assert "Thread not found" in result.output


def test_resolve_already_resolved_thread(runner, git_repo):
    """Test that resolving an already-resolved thread fails."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create and resolve thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Question"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]
    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Done"])
    assert result.exit_code == 0

    # Try to resolve again
    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Done again"])
    assert result.exit_code == 1
    assert "already resolved" in result.output


# ============================================================================
# Integration Tests: comment reopen
# ============================================================================


def test_reopen_resolved_thread(runner, git_repo):
    """Test reopening a resolved thread."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create and resolve thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Question"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]
    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Fixed"])
    assert result.exit_code == 0

    # Reopen thread
    result = runner.invoke(cli, ["reopen", thread_id])
    assert result.exit_code == 0
    assert f"Thread {thread_id} reopened (was resolved)" in result.output
    assert "Previous decision preserved: Fixed" in result.output

    # Verify status is open and decision is preserved
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "open"
    assert sidecar.threads[0].decision is not None
    assert sidecar.threads[0].decision.summary == "Fixed"


def test_reopen_wontfix_thread(runner, git_repo):
    """Test reopening a wontfix thread."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create and mark as wontfix
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Suggestion"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]
    result = runner.invoke(cli, ["resolve", "--wontfix", thread_id])
    assert result.exit_code == 0

    # Reopen thread
    result = runner.invoke(cli, ["reopen", thread_id])
    assert result.exit_code == 0
    assert f"Thread {thread_id} reopened (was wontfix)" in result.output

    # Verify status is open
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "open"


def test_reopen_already_open_thread(runner, git_repo):
    """Test that reopening an open thread fails."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Question"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Try to reopen already-open thread
    result = runner.invoke(cli, ["reopen", thread_id])
    assert result.exit_code == 1
    assert "already open" in result.output


def test_reopen_thread_not_found(runner, git_repo):
    """Test reopen with non-existent thread."""
    result = runner.invoke(cli, ["reopen", "01HQNONEXISTENT000000000000"])
    assert result.exit_code == 1
    assert "Thread not found" in result.output


# ============================================================================
# Workflow Tests: add → reply → resolve → reopen
# ============================================================================


def test_full_thread_workflow(runner, git_repo):
    """Test complete workflow: create → reply → resolve → reopen → resolve again."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Step 1: Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Initial question"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Step 2: Add replies
    result = runner.invoke(cli, ["reply", thread_id, "Investigating"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["reply", thread_id, "Found the issue"])
    assert result.exit_code == 0

    # Step 3: Resolve thread
    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Fixed in commit abc"])
    assert result.exit_code == 0

    # Verify resolved state
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "resolved"
    assert len(sidecar.threads[0].comments) == 3

    # Step 4: Reopen thread
    result = runner.invoke(cli, ["reopen", thread_id])
    assert result.exit_code == 0

    # Verify reopened state
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "open"
    assert sidecar.threads[0].decision.summary == "Fixed in commit abc"  # Decision preserved

    # Step 5: Add another reply after reopening
    result = runner.invoke(cli, ["reply", thread_id, "Actually, still an issue"])
    assert result.exit_code == 0

    # Step 6: Resolve again with new decision
    result = runner.invoke(
        cli, ["resolve", thread_id, "--decision", "Really fixed this time in commit def"]
    )
    assert result.exit_code == 0

    # Verify final state
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "resolved"
    assert len(sidecar.threads[0].comments) == 4
    # Note: New decision replaces old one (as per spec - frozen=True creates new Decision)
    assert sidecar.threads[0].decision.summary == "Really fixed this time in commit def"


def test_workflow_resolve_wontfix_then_reopen(runner, git_repo):
    """Test workflow: create → resolve as wontfix → reopen."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "Feature request"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Mark as wontfix
    result = runner.invoke(cli, ["resolve", "--wontfix", "--decision", "Out of scope", thread_id])
    assert result.exit_code == 0

    # Reopen
    result = runner.invoke(cli, ["reopen", thread_id])
    assert result.exit_code == 0

    # Verify status and decision preservation
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].status.value == "open"
    assert sidecar.threads[0].decision.summary == "Out of scope"


# ============================================================================
# Tests: reconcile command
# ============================================================================


def test_reconcile_single_file_no_changes(runner, git_repo, sample_file):
    """Reconcile single file that hasn't changed - should remain anchored."""
    # Create thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Comment here"])
    assert result.exit_code == 0

    # Reconcile without making changes
    result = runner.invoke(cli, ["reconcile", str(sample_file)])
    assert result.exit_code == 0
    assert "Total threads: 1" in result.output
    assert "(1)" in result.output  # anchored count
    assert "(0)" in result.output  # drifted and orphaned count

    # Verify anchor health
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].anchor.health == AnchorHealth.ANCHORED
    assert sidecar.threads[0].anchor.drift_distance == 0


def test_reconcile_single_file_after_insertion(runner, git_repo, sample_file):
    """Reconcile single file after inserting lines above anchor."""
    # Create thread anchored to lines 5-7
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "5:7", "Comment here"])
    assert result.exit_code == 0

    # Insert 3 lines at the beginning
    original_content = sample_file.read_text()
    new_content = "Inserted 1\nInserted 2\nInserted 3\n" + original_content
    sample_file.write_text(new_content)

    # Reconcile
    result = runner.invoke(cli, ["reconcile", str(sample_file)])
    assert result.exit_code == 0
    assert "Total threads: 1" in result.output
    assert "(1)" in result.output  # Check for count format
    assert "Max drift: 3 lines" in result.output

    # Verify anchor moved down by 3 lines
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].anchor.health == AnchorHealth.ANCHORED
    assert sidecar.threads[0].anchor.line_start == 8  # 5 + 3
    assert sidecar.threads[0].anchor.line_end == 10  # 7 + 3
    assert sidecar.threads[0].anchor.drift_distance == 3


def test_reconcile_single_file_after_modification(runner, git_repo, sample_file):
    """Reconcile single file after modifying anchor content (should drift)."""
    # Create thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Comment here"])
    assert result.exit_code == 0

    # Modify the anchor content slightly
    lines = sample_file.read_text().splitlines(keepends=True)
    lines[2] = "Line 3 modified\n"  # Change line 3
    sample_file.write_text("".join(lines))

    # Reconcile
    result = runner.invoke(cli, ["reconcile", str(sample_file)])
    assert result.exit_code == 0
    assert "Total threads: 1" in result.output
    # Should either be anchored (exact context match) or drifted (fuzzy match)
    # depending on similarity threshold

    # Verify anchor state
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    # Should be drifted or anchored depending on fuzzy match quality
    assert sidecar.threads[0].anchor.health in [AnchorHealth.ANCHORED, AnchorHealth.DRIFTED]


def test_reconcile_single_file_after_deletion(runner, git_repo, sample_file):
    """Reconcile single file after deleting anchor content (should orphan)."""
    # Create thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Comment here"])
    assert result.exit_code == 0

    # Delete lines 3-5 (replace with completely different content)
    lines = sample_file.read_text().splitlines(keepends=True)
    new_lines = lines[:2] + ["Completely different\n"] + lines[5:]
    sample_file.write_text("".join(new_lines))

    # Reconcile
    result = runner.invoke(cli, ["reconcile", str(sample_file)])
    assert result.exit_code == 0
    assert "Total threads: 1" in result.output
    assert "Orphaned:" in result.output  # Check for orphaned status

    # Verify anchor is orphaned
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].anchor.health == AnchorHealth.ORPHANED


def test_reconcile_json_output(runner, git_repo, sample_file):
    """Reconcile with --json output produces valid JSON."""
    # Create thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Comment here"])
    assert result.exit_code == 0

    # Reconcile with JSON output
    result = runner.invoke(cli, ["reconcile", str(sample_file), "--json"])
    assert result.exit_code == 0

    # Parse JSON
    import json

    data = json.loads(result.output)
    assert "file" in data
    assert "total_threads" in data
    assert data["total_threads"] == 1
    assert "anchored" in data
    assert "drifted" in data
    assert "orphaned" in data
    assert "max_drift" in data
    assert "source_hash_before" in data
    assert "source_hash_after" in data


def test_reconcile_with_custom_threshold(runner, git_repo, sample_file):
    """Reconcile with custom similarity threshold."""
    # Create thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Comment here"])
    assert result.exit_code == 0

    # Modify content slightly
    lines = sample_file.read_text().splitlines(keepends=True)
    lines[2] = "Line 3 slightly modified\n"
    sample_file.write_text("".join(lines))

    # Reconcile with lower threshold (more permissive)
    result = runner.invoke(cli, ["reconcile", str(sample_file), "--threshold", "0.3"])
    assert result.exit_code == 0
    assert "Total threads: 1" in result.output


def test_reconcile_all_no_files(runner, git_repo):
    """Reconcile --all when no comment files exist."""
    result = runner.invoke(cli, ["reconcile", "--all"])
    assert result.exit_code == 0
    assert "No comment files found in project" in result.output


def test_reconcile_all_single_file(runner, git_repo, sample_file):
    """Reconcile --all with one commented file."""
    # Create thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Comment here"])
    assert result.exit_code == 0

    # Reconcile all
    result = runner.invoke(cli, ["reconcile", "--all"])
    assert result.exit_code == 0
    assert "Reconciled 1 files:" in result.output
    assert "Total threads: 1" in result.output
    assert "(1)" in result.output  # Check for count format


def test_reconcile_all_multiple_files(runner, git_repo):
    """Reconcile --all with multiple commented files."""
    # Create two files
    file1 = git_repo / "file1.txt"
    file1.write_text("Line 1\nLine 2\nLine 3\n")
    file2 = git_repo / "file2.txt"
    file2.write_text("Line A\nLine B\nLine C\n")

    # Add comments to both
    result = runner.invoke(cli, ["add", str(file1), "-L", "1:2", "Comment on file1"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["add", str(file2), "-L", "2:3", "Comment on file2"])
    assert result.exit_code == 0

    # Reconcile all
    result = runner.invoke(cli, ["reconcile", "--all"])
    assert result.exit_code == 0
    assert "Reconciled 2 files:" in result.output
    assert "Total threads: 2" in result.output
    assert "(2)" in result.output  # Check for count format


def test_reconcile_all_json_output(runner, git_repo, sample_file):
    """Reconcile --all with JSON output."""
    # Create thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Comment here"])
    assert result.exit_code == 0

    # Reconcile all with JSON
    result = runner.invoke(cli, ["reconcile", "--all", "--json"])
    assert result.exit_code == 0

    # Parse JSON
    import json

    data = json.loads(result.output)
    assert "files" in data
    assert len(data["files"]) == 1
    assert "total_threads" in data
    assert data["total_threads"] == 1
    assert "total_anchored" in data
    assert "total_drifted" in data
    assert "total_orphaned" in data


def test_reconcile_no_file_and_no_all(runner, git_repo):
    """Reconcile without FILE or --all should error."""
    result = runner.invoke(cli, ["reconcile"])
    assert result.exit_code == 1
    assert "Must specify either FILE or --all" in result.output


def test_reconcile_both_file_and_all(runner, git_repo, sample_file):
    """Reconcile with both FILE and --all should error."""
    result = runner.invoke(cli, ["reconcile", str(sample_file), "--all"])
    assert result.exit_code == 1
    assert "Cannot specify both FILE and --all" in result.output


def test_reconcile_invalid_threshold_low(runner, git_repo, sample_file):
    """Reconcile with threshold < 0 should error."""
    result = runner.invoke(cli, ["reconcile", str(sample_file), "--threshold", "-0.1"])
    assert result.exit_code == 1
    assert "Threshold must be between 0 and 1" in result.output


def test_reconcile_invalid_threshold_high(runner, git_repo, sample_file):
    """Reconcile with threshold > 1 should error."""
    result = runner.invoke(cli, ["reconcile", str(sample_file), "--threshold", "1.5"])
    assert result.exit_code == 1
    assert "Threshold must be between 0 and 1" in result.output


def test_reconcile_file_not_found(runner, git_repo):
    """Reconcile on non-existent file should error."""
    result = runner.invoke(cli, ["reconcile", "nonexistent.txt"])
    assert result.exit_code != 0


def test_reconcile_no_comments_for_file(runner, git_repo, sample_file):
    """Reconcile file with no comments should error."""
    result = runner.invoke(cli, ["reconcile", str(sample_file)])
    assert result.exit_code == 1
    assert "No comments found for" in result.output


def test_reconcile_integration_workflow(runner, git_repo, sample_file):
    """Integration test: create comment, edit file, reconcile, verify results."""
    # Step 1: Create comment on lines 4-6
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "4:6", "Check this logic"])
    assert result.exit_code == 0
    # Extract thread ID from output: "Created thread <ID>"
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Step 2: Verify initial state
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].anchor.line_start == 4
    assert sidecar.threads[0].anchor.line_end == 6
    assert sidecar.threads[0].anchor.health == AnchorHealth.ANCHORED

    # Step 3: Edit file - insert 2 lines at beginning
    original_content = sample_file.read_text()
    new_content = "New line 1\nNew line 2\n" + original_content
    sample_file.write_text(new_content)

    # Step 4: Reconcile
    result = runner.invoke(cli, ["reconcile", str(sample_file)])
    assert result.exit_code == 0

    # Step 5: Verify anchor updated
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].anchor.line_start == 6  # 4 + 2
    assert sidecar.threads[0].anchor.line_end == 8  # 6 + 2
    assert sidecar.threads[0].anchor.health == AnchorHealth.ANCHORED
    assert sidecar.threads[0].anchor.drift_distance == 2

    # Step 6: Add reply to thread
    result = runner.invoke(cli, ["reply", thread_id, "Looks good now"])
    assert result.exit_code == 0

    # Step 7: Resolve thread
    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Refactored for clarity"])
    assert result.exit_code == 0

    # Step 8: Verify resolved thread still tracks position
    result = runner.invoke(cli, ["show", thread_id])
    assert result.exit_code == 0
    assert "Location: test.txt:6:8" in result.output
    assert "Status: resolved" in result.output


def test_deleted_file_shows_deleted_marker_in_list(runner, git_repo, sample_file):
    """List command shows [deleted] marker for deleted files."""
    import subprocess

    # Initialize git properly (git_repo fixture only creates .git dir)
    subprocess.run(["git", "init"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Create comment on file
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "Comment on file"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Commit file and sidecar to git (use relative path)
    relative_file = sample_file.relative_to(git_repo)
    subprocess.run(
        ["git", "add", str(relative_file)], cwd=git_repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Delete file and commit deletion
    sample_file.unlink()
    subprocess.run(["git", "rm", str(relative_file)], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Delete file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # List all threads - should show [deleted] marker
    result = runner.invoke(cli, ["list", "--all"])
    assert result.exit_code == 0
    assert "[deleted]" in result.output
    assert thread_id in result.output


def test_deleted_file_shows_deleted_marker_in_show(runner, git_repo, sample_file):
    """Show command shows [deleted] marker for deleted files."""
    import subprocess

    # Initialize git properly (git_repo fixture only creates .git dir)
    subprocess.run(["git", "init"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Create comment on file
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "Comment on file"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Commit file and sidecar to git (use relative path)
    relative_file = sample_file.relative_to(git_repo)
    subprocess.run(
        ["git", "add", str(relative_file)], cwd=git_repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Delete file and commit deletion
    sample_file.unlink()
    subprocess.run(["git", "rm", str(relative_file)], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Delete file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Show thread - should show [deleted] marker
    result = runner.invoke(cli, ["show", thread_id, "--all"])
    assert result.exit_code == 0
    assert "[deleted]" in result.output
    assert thread_id in result.output


def test_missing_file_shows_missing_marker_when_git_unavailable(runner, git_repo, sample_file):
    """List command shows [missing] marker when git is not available."""
    from unittest.mock import patch

    # Create comment on file
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "Comment on file"])
    assert result.exit_code == 0

    # Delete file (without committing to git)
    sample_file.unlink()

    # Mock git operations to raise GitError (not generic exception)
    from comment_system.git_ops import GitError

    with patch("comment_system.cli.is_file_deleted_in_git", side_effect=GitError("Git error")):
        # List all threads - should show [missing] marker (can't determine if deleted)
        result = runner.invoke(cli, ["list", "--all"])
        # Should succeed but show [missing] marker
        if result.exit_code != 0:
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
        assert result.exit_code == 0
        assert "[missing]" in result.output


def test_deleted_file_preserves_thread_data(runner, git_repo, sample_file):
    """Deleted files preserve thread data and show [deleted] marker in list."""
    import subprocess

    # Initialize git properly (git_repo fixture only creates .git dir)
    subprocess.run(["git", "init"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Create comment on file
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "4:6", "Comment on logic"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Verify initial state
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.threads[0].anchor.health == AnchorHealth.ANCHORED
    original_snippet = sidecar.threads[0].anchor.content_snippet

    # Commit file (use relative path)
    relative_file = sample_file.relative_to(git_repo)
    subprocess.run(
        ["git", "add", str(relative_file)], cwd=git_repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Delete file and commit
    sample_file.unlink()
    subprocess.run(["git", "rm", str(relative_file)], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Delete file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # List threads - should show [deleted] marker and preserve thread data
    result = runner.invoke(cli, ["list", "--all"])
    assert result.exit_code == 0
    assert "[deleted]" in result.output
    assert thread_id in result.output

    # Verify sidecar is preserved (not deleted)
    assert sidecar_path.exists()
    sidecar = read_sidecar(sidecar_path)
    # Thread still exists with original data
    assert len(sidecar.threads) == 1
    assert sidecar.threads[0].id == thread_id
    # Snippet is preserved
    assert sidecar.threads[0].anchor.content_snippet == original_snippet


# ============================================================================
# Test Suite: decisions command
# ============================================================================


def test_decisions_command_no_decisions(runner, git_repo):
    """Generate DECISIONS.md when no decisions exist."""
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    assert "Generated" in result.output
    assert "DECISIONS.md" in result.output
    assert "0 decision(s) included" in result.output

    # Verify DECISIONS.md exists and has correct header
    decisions_path = git_repo / "DECISIONS.md"
    assert decisions_path.exists()
    content = decisions_path.read_text()
    assert "# Decision Log" in content
    assert "Auto-generated — do not edit manually" in content


def test_decisions_command_single_decision(runner, git_repo, sample_file):
    """Generate DECISIONS.md with one resolved thread."""
    # Create and resolve a thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "Fix this bug"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    result = runner.invoke(
        cli, ["resolve", thread_id, "--decision", "Fixed by refactoring the logic"]
    )
    assert result.exit_code == 0

    # Generate decisions
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    assert "1 decision(s) included" in result.output

    # Verify DECISIONS.md content
    decisions_path = git_repo / "DECISIONS.md"
    content = decisions_path.read_text()
    assert "## Active Decisions" in content
    assert "test.txt:1" in content
    assert "Fixed by refactoring the logic" in content


def test_decisions_command_multiple_decisions_sorted(runner, git_repo, sample_file):
    """Generate DECISIONS.md with multiple decisions, sorted correctly."""
    # Create three threads with different timestamps (simulate by spacing out operations)
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "First issue"])
    thread_id_1 = result.output.split("Created thread ")[1].split("\n")[0]

    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:3", "Second issue"])
    thread_id_2 = result.output.split("Created thread ")[1].split("\n")[0]

    result = runner.invoke(cli, ["add", str(sample_file), "-L", "5:5", "Third issue"])
    thread_id_3 = result.output.split("Created thread ")[1].split("\n")[0]

    # Resolve in order (newest decision should be thread_id_3)
    result = runner.invoke(cli, ["resolve", thread_id_1, "--decision", "Decision 1"])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["resolve", thread_id_2, "--decision", "Decision 2"])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["resolve", thread_id_3, "--decision", "Decision 3"])
    assert result.exit_code == 0

    # Generate decisions
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    assert "3 decision(s) included" in result.output

    # Verify DECISIONS.md content - newest first
    decisions_path = git_repo / "DECISIONS.md"
    content = decisions_path.read_text()

    # Find positions of each decision in the file
    pos_1 = content.find("Decision 1")
    pos_2 = content.find("Decision 2")
    pos_3 = content.find("Decision 3")

    # Newest first means Decision 3 appears before Decision 2, which appears before Decision 1
    assert pos_3 < pos_2 < pos_1


def test_decisions_command_idempotent(runner, git_repo, sample_file):
    """Running decisions command multiple times produces same result."""
    # Create and resolve a thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "Fix this"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]
    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Fixed it"])

    # Generate decisions first time
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    decisions_path = git_repo / "DECISIONS.md"
    first_content = decisions_path.read_text()

    # Generate decisions second time
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    second_content = decisions_path.read_text()

    # Except for timestamp, content should be deterministic
    # Compare structure (ignore timestamp line)
    first_lines = [line for line in first_content.split("\n") if "Last updated:" not in line]
    second_lines = [line for line in second_content.split("\n") if "Last updated:" not in line]
    assert first_lines == second_lines


def test_decisions_command_reopened_section(runner, git_repo, sample_file):
    """Reopened threads with decisions appear in separate section."""
    # Create, resolve, then reopen a thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "Issue to revisit"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Initial decision"])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["reopen", thread_id])
    assert result.exit_code == 0

    # Generate decisions
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    assert "1 decision(s) included" in result.output

    # Verify reopened section exists
    decisions_path = git_repo / "DECISIONS.md"
    content = decisions_path.read_text()
    assert "## Reopened Decisions" in content
    assert "Initial decision" in content
    assert "previously resolved but have been reopened" in content


def test_decisions_command_deleted_file_marker(runner, git_repo, sample_file):
    """Deleted source files show [deleted] marker in DECISIONS.md."""
    import subprocess

    # Initialize git properly
    subprocess.run(["git", "init"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Create and resolve a thread
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "Fix before delete"])
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]
    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Resolved before deletion"])

    # Commit file to git
    relative_file = sample_file.relative_to(git_repo)
    subprocess.run(
        ["git", "add", str(relative_file)], cwd=git_repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Delete file and commit deletion
    sample_file.unlink()
    subprocess.run(["git", "rm", str(relative_file)], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Delete file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Generate decisions
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    assert "1 decision(s) included" in result.output

    # Verify [deleted] marker
    decisions_path = git_repo / "DECISIONS.md"
    content = decisions_path.read_text()
    assert "[deleted: test.txt]" in content
    assert "Resolved before deletion" in content


def test_decisions_command_multiple_files_grouped(runner, git_repo):
    """Decisions from multiple files are grouped correctly."""
    # Create two files
    file1 = git_repo / "file1.txt"
    file1.write_text("File 1 content\n")
    file2 = git_repo / "file2.txt"
    file2.write_text("File 2 content\n")

    # Create and resolve threads on both files
    result = runner.invoke(cli, ["add", str(file1), "-L", "1:1", "Issue in file1"])
    thread_id_1 = result.output.split("Created thread ")[1].split("\n")[0]
    result = runner.invoke(cli, ["resolve", thread_id_1, "--decision", "Decision for file1"])

    result = runner.invoke(cli, ["add", str(file2), "-L", "1:1", "Issue in file2"])
    thread_id_2 = result.output.split("Created thread ")[1].split("\n")[0]
    result = runner.invoke(cli, ["resolve", thread_id_2, "--decision", "Decision for file2"])

    # Generate decisions
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    assert "2 decision(s) included" in result.output

    # Verify both files appear
    decisions_path = git_repo / "DECISIONS.md"
    content = decisions_path.read_text()
    assert "file1.txt" in content
    assert "file2.txt" in content
    assert "Decision for file1" in content
    assert "Decision for file2" in content


def test_decisions_command_no_git_repo(runner, git_repo):
    """Decisions command works when git is not properly initialized (no [deleted] markers)."""
    # Note: git_repo fixture creates .git dir but doesn't run git init,
    # so git commands fail but project root detection works

    # Create file and comment
    sample_file = git_repo / "test.txt"
    sample_file.write_text("Test content\n")

    result = runner.invoke(cli, ["add", str(sample_file), "-L", "1:1", "Issue"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Resolved"])
    assert result.exit_code == 0

    # Generate decisions - should work even though git commands would fail
    result = runner.invoke(cli, ["decisions"])
    assert result.exit_code == 0
    assert "1 decision(s) included" in result.output

    # Verify DECISIONS.md exists
    decisions_path = git_repo / "DECISIONS.md"
    assert decisions_path.exists()
    content = decisions_path.read_text()
    assert "Resolved" in content
    # Should not have [deleted] marker since git detection failed
    assert "[deleted" not in content


def test_decisions_command_error_no_git_repo_for_project_root(runner):
    """Decisions command fails gracefully when not in a git repo and can't find project root."""
    import os
    import tempfile

    # Save original working directory
    original_cwd = os.getcwd()

    # Create a temporary directory that's NOT a git repo and has no .git parent
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        os.chdir(tmppath)

        # Try to generate decisions - should fail with exit code 2
        result = runner.invoke(cli, ["decisions"])
        assert result.exit_code == 2
        assert "Error:" in result.output

    # Restore original working directory
    os.chdir(original_cwd)


# ============================================================================
# Concurrency Tests: Automatic Retry on Concurrent Modifications
# ============================================================================


def test_add_concurrent_modification_automatic_retry(runner, git_repo):
    """Test that add() automatically retries on concurrent modifications."""
    from unittest.mock import patch

    from comment_system.storage import ConcurrencyConflict, read_sidecar, write_sidecar

    # Create a sample file
    sample_file = git_repo / "test.txt"
    sample_file.write_text("Line 1\nLine 2\nLine 3\n")

    # Create initial thread using CLI
    result = runner.invoke(
        cli, ["add", "test.txt", "-L", "1:1", "-a", "alice", "First comment"]
    )
    assert result.exit_code == 0

    # Track number of write attempts
    write_attempts = []

    # Patch write_sidecar to simulate concurrent modification on first attempt
    original_write = write_sidecar

    def mock_write_sidecar(path, sidecar, *, check_hash=True, acquire_lock=True, timeout=5.0):
        write_attempts.append(1)
        if len(write_attempts) == 1 and check_hash:
            # First attempt with hash check - simulate concurrent modification
            raise ConcurrencyConflict("Simulated concurrent modification")
        # Subsequent attempts succeed
        return original_write(path, sidecar, check_hash=check_hash, acquire_lock=acquire_lock, timeout=timeout)

    with patch("comment_system.storage.write_sidecar", side_effect=mock_write_sidecar):
        # Add second comment - should succeed after automatic retry
        result = runner.invoke(
            cli, ["add", "test.txt", "-L", "2:2", "-a", "bob", "Second comment"]
        )
        assert result.exit_code == 0
        assert "Created thread" in result.output

    # Verify we attempted write twice (once failed, once succeeded)
    assert len(write_attempts) >= 2

    # Verify both threads exist
    sidecar = read_sidecar(git_repo / ".comments" / "test.txt.json")
    assert len(sidecar.threads) == 2


def test_add_concurrent_modification_max_retries_exceeded(runner, git_repo):
    """Test that add() fails gracefully when max retries exceeded."""
    from unittest.mock import patch

    from comment_system.storage import ConcurrencyConflict

    # Create a sample file
    sample_file = git_repo / "test.txt"
    sample_file.write_text("Line 1\nLine 2\nLine 3\n")

    # Create initial thread
    result = runner.invoke(
        cli, ["add", "test.txt", "-L", "1:1", "-a", "alice", "First comment"]
    )
    assert result.exit_code == 0

    # Patch write_sidecar to always fail with ConcurrencyConflict
    def mock_write_sidecar(path, sidecar, *, check_hash=True, acquire_lock=True, timeout=5.0):
        if check_hash:
            raise ConcurrencyConflict("Simulated concurrent modification")
        # Should not reach here in this test
        raise AssertionError("Should have failed before this")

    with patch("comment_system.storage.write_sidecar", side_effect=mock_write_sidecar):
        # Add second comment - should fail after max retries
        result = runner.invoke(
            cli, ["add", "test.txt", "-L", "2:2", "-a", "bob", "Second comment"]
        )
        assert result.exit_code == 2
        assert "Error:" in result.output


def test_reply_concurrent_modification_automatic_retry(runner, git_repo):
    """Test that reply() automatically retries on concurrent modifications."""
    from unittest.mock import patch

    from comment_system.storage import ConcurrencyConflict, read_sidecar, write_sidecar

    # Create a sample file and thread
    sample_file = git_repo / "test.txt"
    sample_file.write_text("Line 1\nLine 2\nLine 3\n")

    result = runner.invoke(
        cli, ["add", "test.txt", "-L", "1:1", "-a", "alice", "Initial comment"]
    )
    assert result.exit_code == 0

    # Extract thread ID from output
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Track write attempts
    write_attempts = []
    original_write = write_sidecar

    def mock_write_sidecar(path, sidecar, *, check_hash=True, acquire_lock=True, timeout=5.0):
        write_attempts.append(1)
        if len(write_attempts) == 1 and check_hash:
            raise ConcurrencyConflict("Simulated concurrent modification")
        return original_write(path, sidecar, check_hash=check_hash, acquire_lock=acquire_lock, timeout=timeout)

    with patch("comment_system.storage.write_sidecar", side_effect=mock_write_sidecar):
        # Reply to thread - should succeed after retry
        result = runner.invoke(cli, ["reply", thread_id, "-a", "bob", "Reply comment"])
        assert result.exit_code == 0
        assert "Added comment" in result.output

    # Verify retry occurred
    assert len(write_attempts) >= 2

    # Verify reply was added
    sidecar = read_sidecar(git_repo / ".comments" / "test.txt.json")
    thread = sidecar.threads[0]
    assert len(thread.comments) == 2


def test_resolve_concurrent_modification_automatic_retry(runner, git_repo):
    """Test that resolve() automatically retries on concurrent modifications."""
    from unittest.mock import patch

    from comment_system.storage import ConcurrencyConflict, write_sidecar

    # Create a sample file and thread
    sample_file = git_repo / "test.txt"
    sample_file.write_text("Line 1\nLine 2\nLine 3\n")

    result = runner.invoke(
        cli, ["add", "test.txt", "-L", "1:1", "-a", "alice", "Initial comment"]
    )
    assert result.exit_code == 0

    # Extract thread ID
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Track write attempts
    write_attempts = []
    original_write = write_sidecar

    def mock_write_sidecar(path, sidecar, *, check_hash=True, acquire_lock=True, timeout=5.0):
        write_attempts.append(1)
        if len(write_attempts) == 1 and check_hash:
            raise ConcurrencyConflict("Simulated concurrent modification")
        return original_write(path, sidecar, check_hash=check_hash, acquire_lock=acquire_lock, timeout=timeout)

    with patch("comment_system.storage.write_sidecar", side_effect=mock_write_sidecar):
        # Resolve thread - should succeed after retry
        result = runner.invoke(
            cli, ["resolve", thread_id, "--decision", "Fixed in commit abc123"]
        )
        assert result.exit_code == 0
        assert "marked as resolved" in result.output

    # Verify retry occurred
    assert len(write_attempts) >= 2


def test_reopen_concurrent_modification_automatic_retry(runner, git_repo):
    """Test that reopen() automatically retries on concurrent modifications."""
    from unittest.mock import patch

    from comment_system.models import ThreadStatus
    from comment_system.storage import ConcurrencyConflict, read_sidecar, write_sidecar

    # Create and resolve a thread
    sample_file = git_repo / "test.txt"
    sample_file.write_text("Line 1\nLine 2\nLine 3\n")

    result = runner.invoke(
        cli, ["add", "test.txt", "-L", "1:1", "-a", "alice", "Initial comment"]
    )
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    result = runner.invoke(cli, ["resolve", thread_id, "--decision", "Fixed"])
    assert result.exit_code == 0

    # Track write attempts
    write_attempts = []
    original_write = write_sidecar

    def mock_write_sidecar(path, sidecar, *, check_hash=True, acquire_lock=True, timeout=5.0):
        write_attempts.append(1)
        if len(write_attempts) == 1 and check_hash:
            raise ConcurrencyConflict("Simulated concurrent modification")
        return original_write(path, sidecar, check_hash=check_hash, acquire_lock=acquire_lock, timeout=timeout)

    with patch("comment_system.storage.write_sidecar", side_effect=mock_write_sidecar):
        # Reopen thread - should succeed after retry
        result = runner.invoke(cli, ["reopen", thread_id])
        assert result.exit_code == 0
        assert "reopened" in result.output

    # Verify retry occurred
    assert len(write_attempts) >= 2

    # Verify thread is open
    sidecar = read_sidecar(git_repo / ".comments" / "test.txt.json")
    assert sidecar.threads[0].status == ThreadStatus.OPEN


# ============================================================================
# Rename Detection Integration Tests (Task 3.1)
# ============================================================================


def test_list_auto_detects_rename(runner, git_repo, sample_file):
    """Test that comment list auto-detects file renames and updates sidecar."""
    import subprocess

    # Initialize git repo with config
    subprocess.run(["git", "init"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Create and commit file
    subprocess.run(["git", "add", "test.txt"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Add a comment
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Test comment"])
    assert result.exit_code == 0

    # Verify sidecar exists at old location
    old_sidecar = git_repo / ".comments" / "test.txt.json"
    assert old_sidecar.exists()
    old_sidecar_data = read_sidecar(old_sidecar)
    assert old_sidecar_data.source_file == "test.txt"

    # Rename file in git
    subprocess.run(
        ["git", "mv", "test.txt", "renamed.txt"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Rename file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Run list command - should detect rename and update sidecar
    result = runner.invoke(cli, ["list", "--all"])
    assert result.exit_code == 0

    # Verify sidecar moved to new location
    new_sidecar = git_repo / ".comments" / "renamed.txt.json"
    assert new_sidecar.exists()
    assert not old_sidecar.exists()

    # Verify source_file updated in sidecar
    new_sidecar_data = read_sidecar(new_sidecar)
    assert new_sidecar_data.source_file == "renamed.txt"

    # Verify thread preserved
    assert len(new_sidecar_data.threads) == 1
    assert new_sidecar_data.threads[0].comments[0].body == "Test comment"


def test_show_auto_detects_rename(runner, git_repo, sample_file):
    """Test that comment show auto-detects file renames and updates sidecar."""
    import subprocess

    # Initialize git repo with config
    subprocess.run(["git", "init"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Create and commit file
    subprocess.run(["git", "add", "test.txt"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Add a comment
    result = runner.invoke(cli, ["add", str(sample_file), "-L", "3:5", "Test comment"])
    assert result.exit_code == 0

    # Get thread ID
    sidecar = read_sidecar(git_repo / ".comments" / "test.txt.json")
    thread_id = sidecar.threads[0].id

    # Rename file in git
    subprocess.run(
        ["git", "mv", "test.txt", "renamed.txt"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Rename file"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Run show command - should detect rename and update sidecar
    result = runner.invoke(cli, ["show", thread_id])
    assert result.exit_code == 0

    # Verify sidecar moved to new location
    new_sidecar = git_repo / ".comments" / "renamed.txt.json"
    assert new_sidecar.exists()
    assert not (git_repo / ".comments" / "test.txt.json").exists()

    # Verify source_file updated in sidecar
    new_sidecar_data = read_sidecar(new_sidecar)
    assert new_sidecar_data.source_file == "renamed.txt"

    # Verify thread preserved
    assert len(new_sidecar_data.threads) == 1
    assert new_sidecar_data.threads[0].id == thread_id


def test_reconcile_all_detects_renames(runner, git_repo):
    """Test that comment reconcile --all detects all file renames."""
    import subprocess

    # Initialize git repo with config
    subprocess.run(["git", "init"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Create two files
    file1 = git_repo / "file1.txt"
    file2 = git_repo / "file2.txt"
    file1.write_text("Line 1\nLine 2\nLine 3\n")
    file2.write_text("Line A\nLine B\nLine C\n")

    subprocess.run(["git", "add", "file1.txt", "file2.txt"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Add comments to both files
    result = runner.invoke(cli, ["add", str(file1), "-L", "1:2", "Comment on file1"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["add", str(file2), "-L", "2:3", "Comment on file2"])
    assert result.exit_code == 0

    # Rename both files in git
    subprocess.run(
        ["git", "mv", "file1.txt", "renamed1.txt"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "mv", "file2.txt", "renamed2.txt"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Rename both files"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Run reconcile --all - should detect both renames
    result = runner.invoke(cli, ["reconcile", "--all"])
    assert result.exit_code == 0
    assert "Detected 2 file rename(s)" in result.output
    assert "file1.txt → renamed1.txt" in result.output
    assert "file2.txt → renamed2.txt" in result.output

    # Verify both sidecars moved
    assert (git_repo / ".comments" / "renamed1.txt.json").exists()
    assert (git_repo / ".comments" / "renamed2.txt.json").exists()
    assert not (git_repo / ".comments" / "file1.txt.json").exists()
    assert not (git_repo / ".comments" / "file2.txt.json").exists()

    # Verify source_file fields updated
    sidecar1 = read_sidecar(git_repo / ".comments" / "renamed1.txt.json")
    sidecar2 = read_sidecar(git_repo / ".comments" / "renamed2.txt.json")
    assert sidecar1.source_file == "renamed1.txt"
    assert sidecar2.source_file == "renamed2.txt"


# ============================================================================
# Delete Command Tests
# ============================================================================


def test_delete_thread(runner, git_repo):
    """Test deleting a thread permanently."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "To delete"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Delete with --force (skip confirmation)
    result = runner.invoke(cli, ["delete", thread_id, "--force"])
    assert result.exit_code == 0
    assert f"Thread {thread_id} deleted" in result.output

    # Verify sidecar file is deleted (was the only thread)
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    assert not sidecar_path.exists()


def test_delete_thread_keeps_sidecar_with_remaining_threads(runner, git_repo):
    """Test that deleting one thread preserves other threads in the sidecar."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\n")

    # Create two threads
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "First thread"])
    assert result.exit_code == 0
    thread_id_1 = result.output.split("Created thread ")[1].split("\n")[0]

    result = runner.invoke(cli, ["add", str(file_path), "-L", "2:2", "Second thread"])
    assert result.exit_code == 0
    thread_id_2 = result.output.split("Created thread ")[1].split("\n")[0]

    # Delete first thread
    result = runner.invoke(cli, ["delete", thread_id_1, "--force"])
    assert result.exit_code == 0

    # Verify sidecar still exists with remaining thread
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    assert sidecar_path.exists()
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads) == 1
    assert sidecar.threads[0].id == thread_id_2


def test_delete_thread_not_found(runner, git_repo):
    """Test delete with non-existent thread."""
    result = runner.invoke(cli, ["delete", "01HQNONEXISTENT000000000000", "--force"])
    assert result.exit_code == 1
    assert "Thread not found" in result.output


def test_delete_thread_confirmation_abort(runner, git_repo):
    """Test that delete without --force prompts for confirmation and can be aborted."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "To delete"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Try delete without --force, respond with 'n'
    result = runner.invoke(cli, ["delete", thread_id], input="n\n")
    assert "Delete cancelled" in result.output

    # Verify thread still exists
    sidecar_path = git_repo / ".comments" / "test.txt.json"
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads) == 1


def test_delete_thread_confirmation_confirm(runner, git_repo):
    """Test that delete without --force prompts and proceeds on confirmation."""
    file_path = git_repo / "test.txt"
    file_path.write_text("Line 1\n")

    # Create thread
    result = runner.invoke(cli, ["add", str(file_path), "-L", "1:1", "To delete"])
    assert result.exit_code == 0
    thread_id = result.output.split("Created thread ")[1].split("\n")[0]

    # Delete without --force, respond with 'y'
    result = runner.invoke(cli, ["delete", thread_id], input="y\n")
    assert result.exit_code == 0
    assert f"Thread {thread_id} deleted" in result.output

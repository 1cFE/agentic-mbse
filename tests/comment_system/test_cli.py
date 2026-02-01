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

"""Tests for decision log generation."""

from datetime import datetime, timezone

import pytest

from comment_system.decisions import (
    DecisionEntry,
    collect_decisions,
    format_decision_entry,
    generate_decisions_markdown,
    write_decisions_file,
)
from comment_system.models import (
    Anchor,
    AnchorHealth,
    AuthorType,
    Comment,
    Decision,
    SidecarFile,
    Thread,
    ThreadStatus,
)
from comment_system.storage import write_sidecar


@pytest.fixture
def sample_thread_with_decision() -> Thread:
    """Create a sample resolved thread with a decision."""
    anchor = Anchor(
        content_hash="sha256:" + "a" * 64,
        context_hash_before="sha256:" + "b" * 64,
        context_hash_after="sha256:" + "c" * 64,
        line_start=10,
        line_end=15,
        content_snippet="def calculate_total(items):\n    return sum(item.price for item in items)",
        health=AnchorHealth.ANCHORED,
    )

    comment = Comment(
        author="Alice",
        author_type=AuthorType.HUMAN,
        body="We should add error handling for empty lists.",
    )

    decision = Decision(
        summary="Add error handling for edge cases",
        decider="Bob",
        timestamp="2026-02-01T14:30:00Z",
    )

    return Thread(
        status=ThreadStatus.RESOLVED,
        created_at="2026-02-01T10:00:00Z",
        resolved_at="2026-02-01T14:30:00Z",
        comments=[comment],
        anchor=anchor,
        decision=decision,
    )


@pytest.fixture
def sample_reopened_thread() -> Thread:
    """Create a thread that was resolved and then reopened."""
    anchor = Anchor(
        content_hash="sha256:" + "d" * 64,
        context_hash_before="sha256:" + "e" * 64,
        context_hash_after="sha256:" + "f" * 64,
        line_start=20,
        line_end=25,
        content_snippet="class UserManager:\n    def authenticate(self, user, password):",
        health=AnchorHealth.ANCHORED,
    )

    decision = Decision(
        summary="Use bcrypt for password hashing",
        decider="Charlie",
        timestamp="2026-02-02T09:00:00Z",
    )

    return Thread(
        status=ThreadStatus.OPEN,  # Reopened
        created_at="2026-02-02T08:00:00Z",
        resolved_at="2026-02-02T09:00:00Z",
        comments=[],
        anchor=anchor,
        decision=decision,
    )


class TestDecisionEntry:
    """Test DecisionEntry class."""

    def test_resolved_timestamp_from_resolved_at(self, sample_thread_with_decision):
        """Test resolved_timestamp uses resolved_at field."""
        entry = DecisionEntry(
            thread=sample_thread_with_decision,
            source_file="src/calculator.py",
        )

        assert entry.resolved_timestamp == datetime(2026, 2, 1, 14, 30, tzinfo=timezone.utc)

    def test_resolved_timestamp_fallback_to_decision(self):
        """Test resolved_timestamp falls back to decision timestamp if resolved_at is None."""
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="test",
        )

        decision = Decision(
            summary="Test decision",
            decider="Tester",
            timestamp="2026-02-03T12:00:00Z",
        )

        thread = Thread(
            status=ThreadStatus.RESOLVED,
            resolved_at=None,  # Missing resolved_at
            comments=[],
            anchor=anchor,
            decision=decision,
        )

        entry = DecisionEntry(thread=thread, source_file="test.py")
        assert entry.resolved_timestamp == datetime(2026, 2, 3, 12, 0, tzinfo=timezone.utc)

    def test_is_deleted_flag(self, sample_thread_with_decision):
        """Test is_deleted flag is stored correctly."""
        entry = DecisionEntry(
            thread=sample_thread_with_decision,
            source_file="deleted.py",
            is_deleted=True,
        )

        assert entry.is_deleted is True

    def test_is_reopened_flag(self, sample_reopened_thread):
        """Test is_reopened flag is stored correctly."""
        entry = DecisionEntry(
            thread=sample_reopened_thread,
            source_file="auth.py",
            is_reopened=True,
        )

        assert entry.is_reopened is True


class TestCollectDecisions:
    """Test collect_decisions function."""

    def test_no_comments_dir(self, tmp_path):
        """Test with no .comments directory."""
        active, reopened = collect_decisions(tmp_path)

        assert active == []
        assert reopened == []

    def test_empty_comments_dir(self, tmp_path):
        """Test with empty .comments directory."""
        (tmp_path / ".comments").mkdir()

        active, reopened = collect_decisions(tmp_path)

        assert active == []
        assert reopened == []

    def test_single_resolved_thread(self, tmp_path, sample_thread_with_decision):
        """Test collecting single resolved thread."""
        # Create sidecar with resolved thread
        source_file = tmp_path / "src" / "calculator.py"
        source_file.parent.mkdir(parents=True)
        source_file.write_text(
            "def calculate_total(items):\n    return sum(item.price for item in items)\n"
        )

        sidecar = SidecarFile(
            source_file="src/calculator.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[sample_thread_with_decision],
        )

        sidecar_path = tmp_path / ".comments" / "src" / "calculator.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo (so is_file_deleted_in_git doesn't raise)
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        active, reopened = collect_decisions(tmp_path)

        assert len(active) == 1
        assert len(reopened) == 0
        assert active[0].source_file == "src/calculator.py"
        assert active[0].thread.decision is not None
        assert active[0].thread.decision.summary == "Add error handling for edge cases"

    def test_reopened_thread(self, tmp_path, sample_reopened_thread):
        """Test collecting reopened thread (has decision but status is OPEN)."""
        source_file = tmp_path / "auth.py"
        source_file.write_text("class UserManager:\n    pass\n")

        sidecar = SidecarFile(
            source_file="auth.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[sample_reopened_thread],
        )

        sidecar_path = tmp_path / ".comments" / "auth.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        active, reopened = collect_decisions(tmp_path)

        assert len(active) == 0
        assert len(reopened) == 1
        assert reopened[0].is_reopened is True
        assert reopened[0].thread.decision is not None

    def test_threads_without_decisions_skipped(self, tmp_path):
        """Test that threads without decisions are skipped."""
        # Create thread without decision
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="test",
        )

        thread_no_decision = Thread(
            status=ThreadStatus.RESOLVED,
            comments=[],
            anchor=anchor,
            decision=None,  # No decision
        )

        source_file = tmp_path / "test.py"
        source_file.write_text("test\n")

        sidecar = SidecarFile(
            source_file="test.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[thread_no_decision],
        )

        sidecar_path = tmp_path / ".comments" / "test.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        active, reopened = collect_decisions(tmp_path)

        assert len(active) == 0
        assert len(reopened) == 0

    def test_invalid_sidecar_skipped(self, tmp_path):
        """Test that invalid sidecar files are skipped."""
        # Create invalid sidecar file
        (tmp_path / ".comments").mkdir()
        invalid_sidecar = tmp_path / ".comments" / "invalid.json"
        invalid_sidecar.write_text('{"invalid": "json without required fields"}')

        active, reopened = collect_decisions(tmp_path)

        # Should return empty lists without raising exception
        assert active == []
        assert reopened == []


class TestFormatDecisionEntry:
    """Test format_decision_entry function."""

    def test_format_single_line_anchor(self, tmp_path, sample_thread_with_decision):
        """Test formatting entry with single-line anchor."""
        # Modify anchor to be single line
        sample_thread_with_decision.anchor.line_start = 10
        sample_thread_with_decision.anchor.line_end = 10

        entry = DecisionEntry(
            thread=sample_thread_with_decision,
            source_file="src/calculator.py",
        )

        result = format_decision_entry(entry, tmp_path)

        assert "### src/calculator.py:10" in result
        assert "**Decision**: Add error handling for edge cases" in result
        assert "**Context**: def calculate_total(items):" in result
        assert "*Decided by Bob on 2026-02-01*" in result

    def test_format_multiline_anchor(self, tmp_path, sample_thread_with_decision):
        """Test formatting entry with multi-line anchor."""
        entry = DecisionEntry(
            thread=sample_thread_with_decision,
            source_file="src/calculator.py",
        )

        result = format_decision_entry(entry, tmp_path)

        assert "### src/calculator.py:10-15" in result

    def test_format_deleted_file(self, tmp_path, sample_thread_with_decision):
        """Test formatting entry for deleted file."""
        entry = DecisionEntry(
            thread=sample_thread_with_decision,
            source_file="old/deleted.py",
            is_deleted=True,
        )

        result = format_decision_entry(entry, tmp_path)

        assert "[deleted: old/deleted.py]" in result

    def test_format_decision_date_extraction(self, tmp_path):
        """Test that decision date is extracted correctly from timestamp."""
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="test snippet",
        )

        decision = Decision(
            summary="Test decision",
            decider="Tester",
            timestamp="2026-02-05T16:45:30Z",
        )

        thread = Thread(
            status=ThreadStatus.RESOLVED,
            comments=[],
            anchor=anchor,
            decision=decision,
        )

        entry = DecisionEntry(thread=thread, source_file="test.py")
        result = format_decision_entry(entry, tmp_path)

        assert "*Decided by Tester on 2026-02-05*" in result


class TestGenerateDecisionsMarkdown:
    """Test generate_decisions_markdown function."""

    def test_empty_project(self, tmp_path):
        """Test generation with no decisions."""
        result = generate_decisions_markdown(tmp_path)

        assert "# Decision Log" in result
        assert "Auto-generated — do not edit manually" in result
        assert "Last updated:" in result

    def test_single_decision(self, tmp_path, sample_thread_with_decision):
        """Test generation with single decision (AC-1 partial)."""
        # Create sidecar
        source_file = tmp_path / "src" / "calculator.py"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("code here\n")

        sidecar = SidecarFile(
            source_file="src/calculator.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[sample_thread_with_decision],
        )

        sidecar_path = tmp_path / ".comments" / "src" / "calculator.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        result = generate_decisions_markdown(tmp_path)

        assert "## Active Decisions" in result
        assert "src/calculator.py:10-15" in result
        assert "Add error handling for edge cases" in result

    def test_multiple_files_sorted(self, tmp_path, sample_thread_with_decision):
        """Test that decisions are grouped by file and files are sorted alphabetically."""
        # Create three files with decisions (in non-alphabetical order)
        for filename in ["zebra.py", "apple.py", "middle.py"]:
            source_file = tmp_path / filename
            source_file.write_text("code\n")

            thread = Thread(
                status=ThreadStatus.RESOLVED,
                comments=[],
                anchor=sample_thread_with_decision.anchor,
                decision=Decision(
                    summary=f"Decision for {filename}",
                    decider="Tester",
                    timestamp="2026-02-01T10:00:00Z",
                ),
            )

            sidecar = SidecarFile(
                source_file=filename,
                source_hash="sha256:" + "a" * 64,
                schema_version="1.0",
                threads=[thread],
            )

            sidecar_path = tmp_path / ".comments" / f"{filename}.json"
            write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        result = generate_decisions_markdown(tmp_path)

        # Find positions of each file in the output
        apple_pos = result.find("apple.py")
        middle_pos = result.find("middle.py")
        zebra_pos = result.find("zebra.py")

        # Verify alphabetical order
        assert apple_pos < middle_pos < zebra_pos

    def test_multiple_decisions_sorted_by_timestamp(self, tmp_path):
        """Test that decisions within a file are sorted by timestamp (newest first) - AC-3."""
        # Create three threads with different resolution times
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="test",
        )

        thread_2026_02_01 = Thread(
            status=ThreadStatus.RESOLVED,
            resolved_at="2026-02-01T10:00:00Z",
            comments=[],
            anchor=anchor,
            decision=Decision(
                summary="Decision from Feb 1",
                decider="Tester",
                timestamp="2026-02-01T10:00:00Z",
            ),
        )

        thread_2026_02_05 = Thread(
            status=ThreadStatus.RESOLVED,
            resolved_at="2026-02-05T14:00:00Z",
            comments=[],
            anchor=anchor,
            decision=Decision(
                summary="Decision from Feb 5",
                decider="Tester",
                timestamp="2026-02-05T14:00:00Z",
            ),
        )

        source_file = tmp_path / "test.py"
        source_file.write_text("code\n")

        sidecar = SidecarFile(
            source_file="test.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[thread_2026_02_01, thread_2026_02_05],  # Order doesn't matter
        )

        sidecar_path = tmp_path / ".comments" / "test.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        result = generate_decisions_markdown(tmp_path)

        # Feb 5 decision should appear before Feb 1 decision
        feb_5_pos = result.find("Decision from Feb 5")
        feb_1_pos = result.find("Decision from Feb 1")

        assert feb_5_pos < feb_1_pos, "Newer decision should appear first"

    def test_reopened_decisions_section(self, tmp_path, sample_reopened_thread):
        """Test that reopened decisions appear in separate section (AC-4)."""
        source_file = tmp_path / "auth.py"
        source_file.write_text("code\n")

        sidecar = SidecarFile(
            source_file="auth.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[sample_reopened_thread],
        )

        sidecar_path = tmp_path / ".comments" / "auth.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        result = generate_decisions_markdown(tmp_path)

        assert "## Reopened Decisions" in result
        assert "These threads were previously resolved but have been reopened" in result
        assert "Use bcrypt for password hashing" in result

    def test_header_format(self, tmp_path):
        """Test header format (AC-6)."""
        result = generate_decisions_markdown(tmp_path)

        assert "# Decision Log" in result
        assert "Auto-generated — do not edit manually" in result
        assert "Last updated:" in result
        # Verify timestamp is ISO 8601 UTC
        assert "Last updated: 2026-" in result
        assert "Z" in result


class TestWriteDecisionsFile:
    """Test write_decisions_file function."""

    def test_file_creation(self, tmp_path, sample_thread_with_decision):
        """Test that DECISIONS.md is created (AC-2 partial)."""
        # Create sidecar with decision
        source_file = tmp_path / "test.py"
        source_file.write_text("code\n")

        sidecar = SidecarFile(
            source_file="test.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[sample_thread_with_decision],
        )

        sidecar_path = tmp_path / ".comments" / "test.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        count = write_decisions_file(tmp_path)

        # Verify file exists
        decisions_path = tmp_path / "DECISIONS.md"
        assert decisions_path.exists()

        # Verify count
        assert count == 1

    def test_file_regeneration(self, tmp_path, sample_thread_with_decision):
        """Test that DECISIONS.md is completely regenerated, not appended (AC-2)."""
        # Create initial DECISIONS.md with old content
        decisions_path = tmp_path / "DECISIONS.md"
        decisions_path.write_text("# Old Content\n\nThis should be replaced.\n")

        # Create sidecar with decision
        source_file = tmp_path / "test.py"
        source_file.write_text("code\n")

        sidecar = SidecarFile(
            source_file="test.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[sample_thread_with_decision],
        )

        sidecar_path = tmp_path / ".comments" / "test.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        write_decisions_file(tmp_path)

        # Verify old content is gone
        new_content = decisions_path.read_text()
        assert "Old Content" not in new_content
        assert "This should be replaced" not in new_content

        # Verify new content is present
        assert "# Decision Log" in new_content
        assert "Auto-generated" in new_content

    def test_decision_count(self, tmp_path, sample_thread_with_decision, sample_reopened_thread):
        """Test that decision count includes both active and reopened decisions."""
        # Create two sidecars
        for filename, thread in [
            ("active.py", sample_thread_with_decision),
            ("reopened.py", sample_reopened_thread),
        ]:
            source_file = tmp_path / filename
            source_file.write_text("code\n")

            sidecar = SidecarFile(
                source_file=filename,
                source_hash="sha256:" + "a" * 64,
                schema_version="1.0",
                threads=[thread],
            )

            sidecar_path = tmp_path / ".comments" / f"{filename}.json"
            write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        count = write_decisions_file(tmp_path)

        # Should count both active and reopened
        assert count == 2

    def test_utf8_encoding(self, tmp_path):
        """Test that unicode in decision summaries is handled correctly (CON-3)."""
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="test",
        )

        # Decision with unicode characters
        decision = Decision(
            summary="Use UTF-8 encoding for émojis 🎉 and spëcial çhars",
            decider="Tëster",
            timestamp="2026-02-01T10:00:00Z",
        )

        thread = Thread(
            status=ThreadStatus.RESOLVED,
            comments=[],
            anchor=anchor,
            decision=decision,
        )

        source_file = tmp_path / "test.py"
        source_file.write_text("code\n")

        sidecar = SidecarFile(
            source_file="test.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[thread],
        )

        sidecar_path = tmp_path / ".comments" / "test.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        write_decisions_file(tmp_path)

        # Verify unicode is preserved
        decisions_path = tmp_path / "DECISIONS.md"
        content = decisions_path.read_text(encoding="utf-8")

        assert "Use UTF-8 encoding for émojis 🎉 and spëcial çhars" in content
        assert "Tëster" in content

    def test_large_decision_log_warning(self, tmp_path, capsys):
        """Test that a warning is printed when DECISIONS.md exceeds 1 MB (CON-4)."""
        # Create a large number of threads with decisions to exceed 1 MB
        # Each decision entry is roughly 300-400 bytes, so we need ~2500-3500 decisions
        # to generate > 1 MB of content
        threads = []
        for i in range(3000):
            anchor = Anchor(
                content_hash=f"sha256:{'a' * 64}",
                context_hash_before=f"sha256:{'b' * 64}",
                context_hash_after=f"sha256:{'c' * 64}",
                line_start=i * 10 + 1,
                line_end=i * 10 + 6,
                content_snippet=f"def function_{i}():\n    # This is a function that does something\n    return result_{i}",
                health=AnchorHealth.ANCHORED,
            )

            decision = Decision(
                summary=f"Decision #{i}: This is a detailed decision summary that explains the architectural choice made for function_{i} and its implications on the system design",
                decider="Tester",
                timestamp=f"2026-02-01T{i % 24:02d}:00:00Z",
            )

            thread = Thread(
                status=ThreadStatus.RESOLVED,
                comments=[],
                anchor=anchor,
                decision=decision,
                resolved_at=f"2026-02-01T{i % 24:02d}:00:00Z",
            )
            threads.append(thread)

        # Create sidecar with all threads
        sidecar = SidecarFile(
            source_file="large_file.py",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=threads,
        )

        sidecar_path = tmp_path / ".comments" / "large_file.py.json"
        write_sidecar(sidecar_path, sidecar)

        # Create source file
        source_file = tmp_path / "large_file.py"
        source_file.write_text("# Large file\n")

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        # Generate decisions file
        write_decisions_file(tmp_path)

        # Verify file size exceeds 1 MB
        decisions_path = tmp_path / "DECISIONS.md"
        file_size_bytes = decisions_path.stat().st_size
        assert file_size_bytes > 1_000_000, f"File size {file_size_bytes} is not > 1 MB"

        # Verify warning was printed to stderr
        captured = capsys.readouterr()
        assert "Warning: DECISIONS.md is" in captured.err
        assert "MB (> 1 MB recommended maximum)" in captured.err

        # Verify file size is shown in the warning
        file_size_mb = file_size_bytes / (1024 * 1024)
        assert f"{file_size_mb:.1f}" in captured.err


class TestAcceptanceCriteria:
    """Test suite for explicit acceptance criteria."""

    def test_ac1_three_decisions_two_files(self, tmp_path):
        """AC-1: Given 3 resolved threads with decisions across 2 files,
        when `comment decisions` runs, then DECISIONS.md contains 3 entries grouped by file.
        """
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="test snippet",
        )

        # File 1: 2 decisions
        decisions_file1 = [
            Decision(summary="Decision 1A", decider="Alice", timestamp="2026-02-01T10:00:00Z"),
            Decision(summary="Decision 1B", decider="Bob", timestamp="2026-02-01T11:00:00Z"),
        ]

        threads_file1 = [
            Thread(
                status=ThreadStatus.RESOLVED,
                comments=[],
                anchor=anchor,
                decision=decisions_file1[0],
            ),
            Thread(
                status=ThreadStatus.RESOLVED,
                comments=[],
                anchor=anchor,
                decision=decisions_file1[1],
            ),
        ]

        # File 2: 1 decision
        decision_file2 = Decision(
            summary="Decision 2A", decider="Charlie", timestamp="2026-02-01T12:00:00Z"
        )
        thread_file2 = Thread(
            status=ThreadStatus.RESOLVED, comments=[], anchor=anchor, decision=decision_file2
        )

        # Create sidecars
        for filename, threads in [("file1.py", threads_file1), ("file2.py", [thread_file2])]:
            source_file = tmp_path / filename
            source_file.write_text("code\n")

            sidecar = SidecarFile(
                source_file=filename,
                source_hash="sha256:" + "a" * 64,
                schema_version="1.0",
                threads=threads,
            )

            sidecar_path = tmp_path / ".comments" / f"{filename}.json"
            write_sidecar(sidecar_path, sidecar)

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)

        count = write_decisions_file(tmp_path)

        # Verify count
        assert count == 3

        # Verify content
        decisions_path = tmp_path / "DECISIONS.md"
        content = decisions_path.read_text()

        # All 3 decisions present
        assert "Decision 1A" in content
        assert "Decision 1B" in content
        assert "Decision 2A" in content

        # Files are mentioned
        assert "file1.py" in content
        assert "file2.py" in content

    def test_ac5_deleted_file_marker(self, tmp_path):
        """AC-5: Given source file deleted, when generating log,
        then decision entry shows '[deleted: old/path.md]'.
        """
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=1,
            line_end=1,
            content_snippet="deleted content",
        )

        decision = Decision(
            summary="Decision for deleted file",
            decider="Tester",
            timestamp="2026-02-01T10:00:00Z",
        )

        thread = Thread(
            status=ThreadStatus.RESOLVED,
            comments=[],
            anchor=anchor,
            decision=decision,
        )

        # Create file, add to git, then delete it
        source_file = tmp_path / "old" / "path.md"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("content\n")

        # Initialize git and commit the file
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add file"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create sidecar before deleting
        sidecar = SidecarFile(
            source_file="old/path.md",
            source_hash="sha256:" + "a" * 64,
            schema_version="1.0",
            threads=[thread],
        )

        sidecar_path = tmp_path / ".comments" / "old" / "path.md.json"
        write_sidecar(sidecar_path, sidecar)

        # Now delete the source file
        source_file.unlink()
        subprocess.run(
            ["git", "add", "-A"],
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

        write_decisions_file(tmp_path)

        # Verify deletion marker
        decisions_path = tmp_path / "DECISIONS.md"
        content = decisions_path.read_text()

        assert "[deleted: old/path.md]" in content

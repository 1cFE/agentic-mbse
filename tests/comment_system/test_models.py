"""Unit tests for comment system data models."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

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


class TestDecision:
    """Tests for immutable Decision model."""

    def test_decision_creation_with_valid_data(self):
        """Decision can be created with valid data."""
        decision = Decision(
            summary="Implemented as suggested",
            decider="alice",
            timestamp="2026-02-01T10:00:00Z",
        )
        assert decision.summary == "Implemented as suggested"
        assert decision.decider == "alice"
        assert decision.timestamp == "2026-02-01T10:00:00Z"

    def test_decision_is_immutable(self):
        """Decision fields cannot be modified after creation (frozen=True)."""
        decision = Decision(
            summary="Test decision",
            decider="bob",
            timestamp="2026-02-01T10:00:00Z",
        )
        with pytest.raises(ValidationError):
            decision.summary = "Modified summary"  # type: ignore

    def test_decision_rejects_empty_summary(self):
        """Decision requires non-empty summary."""
        with pytest.raises(ValidationError) as exc:
            Decision(summary="", decider="alice", timestamp="2026-02-01T10:00:00Z")
        assert "summary" in str(exc.value).lower()

    def test_decision_rejects_too_long_summary(self):
        """Decision rejects summary > 10,000 characters."""
        with pytest.raises(ValidationError) as exc:
            Decision(
                summary="x" * 10001,
                decider="alice",
                timestamp="2026-02-01T10:00:00Z",
            )
        assert "summary" in str(exc.value).lower()

    def test_decision_rejects_invalid_timestamp(self):
        """Decision validates timestamp is valid ISO 8601 UTC."""
        with pytest.raises(ValidationError) as exc:
            Decision(summary="Test", decider="alice", timestamp="not-a-timestamp")
        assert "timestamp" in str(exc.value).lower()

    def test_decision_rejects_non_utc_timestamp(self):
        """Decision rejects timestamps not in UTC."""
        with pytest.raises(ValidationError) as exc:
            Decision(
                summary="Test",
                decider="alice",
                timestamp="2026-02-01T10:00:00+05:00",  # Not UTC
            )
        assert "utc" in str(exc.value).lower()


class TestComment:
    """Tests for Comment model."""

    def test_comment_auto_generates_ulid(self):
        """Comment generates ULID automatically if not provided."""
        comment = Comment(author="alice", author_type=AuthorType.HUMAN, body="Test comment")
        assert len(comment.id) == 26
        assert comment.id.isalnum()

    def test_comment_auto_generates_timestamp(self):
        """Comment generates UTC timestamp automatically if not provided."""
        before = datetime.now(timezone.utc)
        comment = Comment(author="alice", author_type=AuthorType.HUMAN, body="Test comment")
        after = datetime.now(timezone.utc)

        timestamp = datetime.fromisoformat(comment.timestamp.replace("Z", "+00:00"))
        assert before <= timestamp <= after
        assert comment.timestamp.endswith("Z")

    def test_comment_accepts_custom_id(self):
        """Comment accepts custom ULID if provided."""
        custom_id = "01KGDD8QF70FECJ0R0FATKH0SG"
        comment = Comment(
            id=custom_id,
            author="alice",
            author_type=AuthorType.HUMAN,
            body="Test",
        )
        assert comment.id == custom_id

    def test_comment_rejects_invalid_ulid_length(self):
        """Comment validates ULID is exactly 26 characters."""
        with pytest.raises(ValidationError) as exc:
            Comment(
                id="TOO_SHORT",
                author="alice",
                author_type=AuthorType.HUMAN,
                body="Test",
            )
        assert "26 characters" in str(exc.value).lower()

    def test_comment_validates_body_min_length(self):
        """Comment body must be at least 1 character."""
        with pytest.raises(ValidationError) as exc:
            Comment(author="alice", author_type=AuthorType.HUMAN, body="")
        assert "body" in str(exc.value).lower()

    def test_comment_validates_body_max_length(self):
        """Comment body cannot exceed 10,000 characters."""
        with pytest.raises(ValidationError) as exc:
            Comment(author="alice", author_type=AuthorType.HUMAN, body="x" * 10001)
        assert "body" in str(exc.value).lower()

    def test_comment_validates_author_type_enum(self):
        """Comment validates author_type is valid enum value."""
        with pytest.raises(ValidationError):
            Comment(
                author="alice",
                author_type="invalid_type",  # type: ignore
                body="Test",
            )

    def test_comment_ulids_have_correct_format(self):
        """ULIDs have correct format (26 alphanumeric characters)."""
        comment1 = Comment(author="alice", author_type=AuthorType.HUMAN, body="First")
        comment2 = Comment(author="alice", author_type=AuthorType.HUMAN, body="Second")
        comment3 = Comment(author="alice", author_type=AuthorType.HUMAN, body="Third")

        # All ULIDs should be 26 characters and alphanumeric
        for comment in [comment1, comment2, comment3]:
            assert len(comment.id) == 26
            assert comment.id.replace("0", "").replace("1", "").isalnum()


class TestAnchor:
    """Tests for Anchor model."""

    @pytest.fixture
    def valid_anchor_data(self):
        """Fixture providing valid anchor data."""
        return {
            "content_hash": "sha256:" + "a" * 64,
            "context_hash_before": "sha256:" + "b" * 64,
            "context_hash_after": "sha256:" + "c" * 64,
            "line_start": 10,
            "line_end": 15,
            "content_snippet": "def calculate_total():\n    return sum(items)",
        }

    def test_anchor_creation_with_valid_data(self, valid_anchor_data):
        """Anchor can be created with valid data."""
        anchor = Anchor(**valid_anchor_data)
        assert anchor.content_hash == valid_anchor_data["content_hash"]
        assert anchor.line_start == 10
        assert anchor.line_end == 15
        assert anchor.health == AnchorHealth.ANCHORED
        assert anchor.drift_distance == 0

    def test_anchor_validates_hash_format(self, valid_anchor_data):
        """Anchor validates SHA-256 hash format with prefix."""
        # Missing prefix
        with pytest.raises(ValidationError):
            Anchor(**{**valid_anchor_data, "content_hash": "a" * 64})

        # Wrong prefix
        with pytest.raises(ValidationError):
            Anchor(**{**valid_anchor_data, "content_hash": "md5:" + "a" * 64})

        # Wrong length
        with pytest.raises(ValidationError):
            Anchor(**{**valid_anchor_data, "content_hash": "sha256:" + "a" * 32})

    def test_anchor_validates_line_start_positive(self, valid_anchor_data):
        """Anchor requires line_start >= 1 (1-indexed lines)."""
        with pytest.raises(ValidationError):
            Anchor(**{**valid_anchor_data, "line_start": 0})

        with pytest.raises(ValidationError):
            Anchor(**{**valid_anchor_data, "line_start": -1})

    def test_anchor_validates_line_end_gte_line_start(self, valid_anchor_data):
        """Anchor requires line_end >= line_start."""
        with pytest.raises(ValidationError):
            Anchor(**{**valid_anchor_data, "line_start": 15, "line_end": 10})

    def test_anchor_allows_single_line_range(self, valid_anchor_data):
        """Anchor allows line_start == line_end for single-line anchors."""
        anchor = Anchor(**{**valid_anchor_data, "line_start": 10, "line_end": 10})
        assert anchor.line_start == anchor.line_end == 10

    def test_anchor_snippet_min_length(self, valid_anchor_data):
        """Anchor snippet must be at least 1 character."""
        with pytest.raises(ValidationError):
            Anchor(**{**valid_anchor_data, "content_snippet": ""})

    def test_anchor_snippet_max_length(self, valid_anchor_data):
        """Anchor snippet cannot exceed 500 characters."""
        with pytest.raises(ValidationError):
            Anchor(**{**valid_anchor_data, "content_snippet": "x" * 501})

    def test_anchor_health_transitions(self, valid_anchor_data):
        """Anchor can represent different health states."""
        # Anchored (default)
        anchored = Anchor(**valid_anchor_data)
        assert anchored.health == AnchorHealth.ANCHORED
        assert anchored.drift_distance == 0

        # Drifted
        drifted = Anchor(
            **{**valid_anchor_data, "health": AnchorHealth.DRIFTED, "drift_distance": 5}
        )
        assert drifted.health == AnchorHealth.DRIFTED
        assert drifted.drift_distance == 5

        # Orphaned
        orphaned = Anchor(**{**valid_anchor_data, "health": AnchorHealth.ORPHANED})
        assert orphaned.health == AnchorHealth.ORPHANED


class TestThread:
    """Tests for Thread model."""

    @pytest.fixture
    def valid_anchor(self):
        """Fixture providing a valid Anchor."""
        return Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=10,
            line_end=12,
            content_snippet="test code",
        )

    def test_thread_auto_generates_ulid(self, valid_anchor):
        """Thread generates ULID automatically if not provided."""
        thread = Thread(anchor=valid_anchor)
        assert len(thread.id) == 26
        assert thread.id.isalnum()

    def test_thread_defaults_to_open_status(self, valid_anchor):
        """Thread defaults to OPEN status."""
        thread = Thread(anchor=valid_anchor)
        assert thread.status == ThreadStatus.OPEN
        assert thread.resolved_at is None
        assert thread.decision is None

    def test_thread_auto_generates_created_at(self, valid_anchor):
        """Thread generates created_at timestamp automatically."""
        before = datetime.now(timezone.utc)
        thread = Thread(anchor=valid_anchor)
        after = datetime.now(timezone.utc)

        created = datetime.fromisoformat(thread.created_at.replace("Z", "+00:00"))
        assert before <= created <= after

    def test_thread_resolve_sets_status_and_decision(self, valid_anchor):
        """Thread.resolve() sets status to RESOLVED and creates decision."""
        thread = Thread(anchor=valid_anchor)
        thread.resolve(decider="alice", summary="Fixed the bug")

        assert thread.status == ThreadStatus.RESOLVED
        assert thread.resolved_at is not None
        assert thread.decision is not None
        assert thread.decision.decider == "alice"
        assert thread.decision.summary == "Fixed the bug"

    def test_thread_wontfix_sets_status_and_decision(self, valid_anchor):
        """Thread.wontfix() sets status to WONTFIX and creates decision."""
        thread = Thread(anchor=valid_anchor)
        thread.wontfix(decider="bob", summary="Working as intended")

        assert thread.status == ThreadStatus.WONTFIX
        assert thread.resolved_at is not None
        assert thread.decision is not None
        assert thread.decision.decider == "bob"
        assert thread.decision.summary == "Working as intended"

    def test_thread_cannot_resolve_already_resolved(self, valid_anchor):
        """Thread.resolve() raises error if already resolved."""
        thread = Thread(anchor=valid_anchor)
        thread.resolve(decider="alice", summary="First resolution")

        with pytest.raises(ValueError, match="already resolved"):
            thread.resolve(decider="bob", summary="Second resolution")

    def test_thread_reopen_changes_status_to_open(self, valid_anchor):
        """Thread.reopen() changes status back to OPEN."""
        thread = Thread(anchor=valid_anchor)
        thread.resolve(decider="alice", summary="Fixed")
        original_resolved_at = thread.resolved_at
        original_decision = thread.decision

        thread.reopen()

        assert thread.status == ThreadStatus.OPEN
        # Decision and resolved_at preserved for historical record
        assert thread.resolved_at == original_resolved_at
        assert thread.decision == original_decision

    def test_thread_cannot_reopen_already_open(self, valid_anchor):
        """Thread.reopen() raises error if already open."""
        thread = Thread(anchor=valid_anchor)

        with pytest.raises(ValueError, match="already open"):
            thread.reopen()

    def test_thread_reopen_preserves_decision(self, valid_anchor):
        """Thread.reopen() preserves original decision for history."""
        thread = Thread(anchor=valid_anchor)
        thread.resolve(decider="alice", summary="Original decision")
        decision_before = thread.decision

        thread.reopen()

        assert thread.decision == decision_before
        assert thread.decision.summary == "Original decision"

    def test_thread_add_comment_creates_comment(self, valid_anchor):
        """Thread.add_comment() creates and appends a comment."""
        thread = Thread(anchor=valid_anchor)
        comment = thread.add_comment(
            author="alice",
            author_type=AuthorType.HUMAN,
            body="This needs fixing",
        )

        assert len(thread.comments) == 1
        assert thread.comments[0] == comment
        assert comment.author == "alice"
        assert comment.body == "This needs fixing"

    def test_thread_comments_ordered_chronologically(self, valid_anchor):
        """Thread maintains chronological order of comments."""
        thread = Thread(anchor=valid_anchor)
        comment1 = thread.add_comment(
            author="alice", author_type=AuthorType.HUMAN, body="First comment"
        )
        comment2 = thread.add_comment(
            author="bob", author_type=AuthorType.AGENT, body="Second comment"
        )
        comment3 = thread.add_comment(
            author="alice", author_type=AuthorType.HUMAN, body="Third comment"
        )

        assert thread.comments == [comment1, comment2, comment3]

    def test_thread_lifecycle_open_to_resolved_to_reopen(self, valid_anchor):
        """Thread supports full lifecycle: open → resolved → reopen."""
        thread = Thread(anchor=valid_anchor)

        # Initially open
        assert thread.status == ThreadStatus.OPEN

        # Resolve
        thread.resolve(decider="alice", summary="Fixed")
        assert thread.status == ThreadStatus.RESOLVED

        # Reopen
        thread.reopen()
        assert thread.status == ThreadStatus.OPEN


class TestSidecarFile:
    """Tests for SidecarFile model."""

    @pytest.fixture
    def valid_thread(self):
        """Fixture providing a valid Thread."""
        anchor = Anchor(
            content_hash="sha256:" + "a" * 64,
            context_hash_before="sha256:" + "b" * 64,
            context_hash_after="sha256:" + "c" * 64,
            line_start=10,
            line_end=12,
            content_snippet="test code",
        )
        thread = Thread(anchor=anchor)
        thread.add_comment(author="alice", author_type=AuthorType.HUMAN, body="Test comment")
        return thread

    def test_sidecar_creation_with_valid_data(self, valid_thread):
        """SidecarFile can be created with valid data."""
        sidecar = SidecarFile(
            source_file="src/foo/bar.py",
            source_hash="sha256:" + "d" * 64,
            threads=[valid_thread],
        )
        assert sidecar.source_file == "src/foo/bar.py"
        assert sidecar.source_hash == "sha256:" + "d" * 64
        assert sidecar.schema_version == "1.0"
        assert len(sidecar.threads) == 1

    def test_sidecar_validates_hash_format(self, valid_thread):
        """SidecarFile validates source_hash format."""
        with pytest.raises(ValidationError):
            SidecarFile(
                source_file="src/foo/bar.py",
                source_hash="invalid_hash",
                threads=[valid_thread],
            )

    def test_sidecar_defaults_schema_version(self):
        """SidecarFile defaults schema_version to '1.0'."""
        sidecar = SidecarFile(
            source_file="src/foo/bar.py",
            source_hash="sha256:" + "e" * 64,
        )
        assert sidecar.schema_version == "1.0"

    def test_sidecar_defaults_empty_threads(self):
        """SidecarFile defaults to empty threads list."""
        sidecar = SidecarFile(
            source_file="src/foo/bar.py",
            source_hash="sha256:" + "e" * 64,
        )
        assert sidecar.threads == []

    def test_sidecar_serialization_is_deterministic(self, valid_thread):
        """SidecarFile serialization produces identical JSON for same data."""
        sidecar1 = SidecarFile(
            source_file="src/foo/bar.py",
            source_hash="sha256:" + "f" * 64,
            threads=[valid_thread],
        )
        sidecar2 = SidecarFile(
            source_file="src/foo/bar.py",
            source_hash="sha256:" + "f" * 64,
            threads=[valid_thread],
        )

        json1 = sidecar1.model_dump_json(indent=2, by_alias=True)
        json2 = sidecar2.model_dump_json(indent=2, by_alias=True)

        assert json1 == json2


class TestEnums:
    """Tests for enum types."""

    def test_thread_status_values(self):
        """ThreadStatus has correct enum values."""
        assert ThreadStatus.OPEN.value == "open"
        assert ThreadStatus.RESOLVED.value == "resolved"
        assert ThreadStatus.WONTFIX.value == "wontfix"

    def test_author_type_values(self):
        """AuthorType has correct enum values."""
        assert AuthorType.HUMAN.value == "human"
        assert AuthorType.AGENT.value == "agent"

    def test_anchor_health_values(self):
        """AnchorHealth has correct enum values."""
        assert AnchorHealth.ANCHORED.value == "anchored"
        assert AnchorHealth.DRIFTED.value == "drifted"
        assert AnchorHealth.ORPHANED.value == "orphaned"

"""Data models for comment threads, comments, and anchors."""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from ulid import new as new_ulid


class ThreadStatus(str, Enum):
    """Thread lifecycle status."""

    OPEN = "open"
    RESOLVED = "resolved"
    WONTFIX = "wontfix"


class AuthorType(str, Enum):
    """Type of comment author."""

    HUMAN = "human"
    AGENT = "agent"


class AnchorHealth(str, Enum):
    """Health status of an anchor."""

    ANCHORED = "anchored"  # Content matches exactly at line position
    DRIFTED = "drifted"  # Content found nearby (within search window)
    ORPHANED = "orphaned"  # Content not found in file


class Decision(BaseModel, frozen=True):
    """Immutable record of a thread resolution decision.

    Once a decision is recorded, it cannot be modified. If a thread is
    reopened and resolved again, a new Decision object is created.
    """

    summary: str = Field(..., min_length=1, max_length=10000)
    decider: str = Field(..., min_length=1, max_length=200)
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp (e.g., 2026-02-01T10:00:00Z)")

    @field_validator("timestamp")
    @classmethod
    def validate_utc_timestamp(cls, v: str) -> str:
        """Validate that timestamp is valid ISO 8601 UTC format."""
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.tzinfo.utcoffset(None) != timezone.utc.utcoffset(None):
                raise ValueError("Timestamp must be in UTC timezone")
            return v
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ISO 8601 UTC timestamp: {v}") from e


class Comment(BaseModel):
    """A single comment within a thread."""

    id: str = Field(default_factory=lambda: str(new_ulid()))
    author: str = Field(..., min_length=1, max_length=200)
    author_type: AuthorType
    body: str = Field(..., min_length=1, max_length=10000)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    @field_validator("id")
    @classmethod
    def validate_ulid(cls, v: str) -> str:
        """Validate that id is a valid ULID (26 characters)."""
        if len(v) != 26:
            raise ValueError(f"ULID must be exactly 26 characters, got {len(v)}")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_utc_timestamp(cls, v: str) -> str:
        """Validate that timestamp is valid ISO 8601 UTC format."""
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.tzinfo.utcoffset(None) != timezone.utc.utcoffset(None):
                raise ValueError("Timestamp must be in UTC timezone")
            return v
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ISO 8601 UTC timestamp: {v}") from e


class Anchor(BaseModel):
    """Location anchor using multi-signal reconciliation.

    Stores redundant signals to enable robust relocation after file edits:
    - content_hash: SHA-256 of the exact text being commented on
    - context_hash_before: SHA-256 of lines immediately before anchor
    - context_hash_after: SHA-256 of lines immediately after anchor
    - line_start/line_end: Original line positions (1-indexed)
    - content_snippet: Human-readable excerpt of anchored text
    """

    content_hash: str = Field(..., pattern=r"^sha256:[a-fA-F0-9]{64}$")
    context_hash_before: str = Field(..., pattern=r"^sha256:[a-fA-F0-9]{64}$")
    context_hash_after: str = Field(..., pattern=r"^sha256:[a-fA-F0-9]{64}$")
    line_start: int = Field(..., ge=1)
    line_end: int = Field(..., ge=1)
    content_snippet: str = Field(..., min_length=1, max_length=500)
    health: AnchorHealth = AnchorHealth.ANCHORED
    drift_distance: int = Field(
        default=0, description="Lines moved from original position (0 = anchored)"
    )

    @field_validator("line_end")
    @classmethod
    def validate_line_range(cls, v: int, info) -> int:
        """Validate that line_end >= line_start."""
        if "line_start" in info.data and v < info.data["line_start"]:
            raise ValueError(f"line_end ({v}) must be >= line_start ({info.data['line_start']})")
        return v


class Thread(BaseModel):
    """A discussion thread anchored to a location in a source file."""

    id: str = Field(default_factory=lambda: str(new_ulid()))
    status: ThreadStatus = ThreadStatus.OPEN
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    resolved_at: str | None = None
    comments: list[Comment] = Field(default_factory=list)
    anchor: Anchor
    decision: Decision | None = None

    @field_validator("id")
    @classmethod
    def validate_ulid(cls, v: str) -> str:
        """Validate that id is a valid ULID (26 characters)."""
        if len(v) != 26:
            raise ValueError(f"ULID must be exactly 26 characters, got {len(v)}")
        return v

    @field_validator("resolved_at")
    @classmethod
    def validate_utc_timestamp(cls, v: str | None) -> str | None:
        """Validate that resolved_at is valid ISO 8601 UTC format if present."""
        if v is None:
            return v
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.tzinfo.utcoffset(None) != timezone.utc.utcoffset(None):
                raise ValueError("Timestamp must be in UTC timezone")
            return v
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ISO 8601 UTC timestamp: {v}") from e

    def resolve(self, decider: str, summary: str) -> None:
        """Mark thread as resolved with a decision.

        Args:
            decider: Identity of the person/agent making the decision
            summary: Description of the resolution decision

        Raises:
            ValueError: If thread is already resolved
        """
        if self.status == ThreadStatus.RESOLVED:
            raise ValueError("Thread is already resolved")

        self.status = ThreadStatus.RESOLVED
        self.resolved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.decision = Decision(decider=decider, summary=summary, timestamp=self.resolved_at)

    def wontfix(self, decider: str, summary: str) -> None:
        """Mark thread as won't fix with a decision.

        Args:
            decider: Identity of the person/agent making the decision
            summary: Description of the won't fix decision

        Raises:
            ValueError: If thread is already resolved
        """
        if self.status == ThreadStatus.RESOLVED:
            raise ValueError("Thread is already resolved")

        self.status = ThreadStatus.WONTFIX
        self.resolved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.decision = Decision(decider=decider, summary=summary, timestamp=self.resolved_at)

    def reopen(self) -> None:
        """Reopen a resolved or won't fix thread.

        Decision and resolution timestamp are preserved for historical record.

        Raises:
            ValueError: If thread is not in a closed state
        """
        if self.status == ThreadStatus.OPEN:
            raise ValueError("Thread is already open")

        self.status = ThreadStatus.OPEN
        # Preserve resolved_at and decision for historical record

    def add_comment(
        self, author: str, author_type: AuthorType, body: str, timestamp: str | None = None
    ) -> Comment:
        """Add a new comment to the thread.

        Args:
            author: Name or identifier of the comment author
            author_type: Whether author is human or agent
            body: Comment text content
            timestamp: Optional override timestamp (uses current UTC time if None)

        Returns:
            The newly created Comment object
        """
        comment = Comment(
            author=author,
            author_type=author_type,
            body=body,
            timestamp=timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        self.comments.append(comment)
        return comment


class SidecarFile(BaseModel):
    """Root structure for a sidecar JSON file."""

    source_file: str = Field(..., description="Relative path to source file (POSIX separators)")
    source_hash: str = Field(
        ...,
        pattern=r"^sha256:[a-fA-F0-9]{64}$",
        description="SHA-256 hash of source file at last reconciliation",
    )
    schema_version: str = Field(default="1.0")
    threads: list[Thread] = Field(default_factory=list)


class ReconciliationReport(BaseModel):
    """Summary report from a sidecar reconciliation operation.

    Provides statistics about anchor health status changes during reconciliation.
    Used for CLI output and logging.
    """

    total_threads: int = Field(..., ge=0, description="Total number of threads reconciled")
    anchored_count: int = Field(..., ge=0, description="Threads with health=anchored")
    drifted_count: int = Field(..., ge=0, description="Threads with health=drifted")
    orphaned_count: int = Field(..., ge=0, description="Threads with health=orphaned")
    max_drift_distance: int = Field(..., ge=0, description="Maximum drift distance found")
    source_hash_before: str = Field(
        ...,
        pattern=r"^sha256:[a-fA-F0-9]{64}$",
        description="Source hash before reconciliation",
    )
    source_hash_after: str = Field(
        ...,
        pattern=r"^sha256:[a-fA-F0-9]{64}$",
        description="Source hash after reconciliation",
    )

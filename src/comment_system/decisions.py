"""Decision log generation from resolved comment threads."""

import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .git_ops import GitError, is_file_deleted_in_git
from .models import Thread, ThreadStatus
from .storage import read_sidecar


class DecisionEntry:
    """Represents a single decision entry for the log."""

    def __init__(
        self,
        thread: Thread,
        source_file: str,
        is_deleted: bool = False,
        is_reopened: bool = False,
    ):
        """Initialize a decision entry.

        Args:
            thread: Thread containing the decision
            source_file: Relative path to source file
            is_deleted: Whether the source file has been deleted
            is_reopened: Whether the thread was reopened after resolution
        """
        self.thread = thread
        self.source_file = source_file
        self.is_deleted = is_deleted
        self.is_reopened = is_reopened

    @property
    def resolved_timestamp(self) -> datetime:
        """Get resolution timestamp as datetime for sorting."""
        if self.thread.resolved_at:
            return datetime.fromisoformat(self.thread.resolved_at.replace("Z", "+00:00"))
        # Fallback to decision timestamp if resolved_at is missing
        if self.thread.decision:
            return datetime.fromisoformat(self.thread.decision.timestamp.replace("Z", "+00:00"))
        # Shouldn't happen, but use thread creation as last resort
        return datetime.fromisoformat(self.thread.created_at.replace("Z", "+00:00"))


def collect_decisions(project_root: Path) -> tuple[list[DecisionEntry], list[DecisionEntry]]:
    """Collect all decisions from sidecar files.

    Args:
        project_root: Project root directory

    Returns:
        Tuple of (active_decisions, reopened_decisions)
        - active_decisions: Resolved threads with decisions
        - reopened_decisions: Reopened threads that had decisions
    """
    comments_dir = project_root / ".comments"
    if not comments_dir.exists():
        return ([], [])

    active_decisions: list[DecisionEntry] = []
    reopened_decisions: list[DecisionEntry] = []

    # Find all sidecar files
    for sidecar_path in comments_dir.rglob("*.json"):
        try:
            sidecar = read_sidecar(sidecar_path)

            # Check if source file was deleted
            source_path = project_root / sidecar.source_file
            try:
                is_deleted = is_file_deleted_in_git(source_path, project_root)
            except GitError:
                # Git not available or not a git repo - assume not deleted
                is_deleted = False

            # Process each thread
            for thread in sidecar.threads:
                # Skip threads without decisions
                if thread.decision is None:
                    continue

                # Check if thread was reopened (has decision but is open)
                is_reopened = thread.status == ThreadStatus.OPEN

                entry = DecisionEntry(
                    thread=thread,
                    source_file=sidecar.source_file,
                    is_deleted=is_deleted,
                    is_reopened=is_reopened,
                )

                if is_reopened:
                    reopened_decisions.append(entry)
                else:
                    active_decisions.append(entry)

        except Exception:
            # Skip invalid sidecar files
            continue

    return (active_decisions, reopened_decisions)


def format_decision_entry(entry: DecisionEntry, project_root: Path) -> str:
    """Format a single decision entry as markdown.

    Args:
        entry: Decision entry to format
        project_root: Project root for file links

    Returns:
        Markdown formatted decision entry
    """
    thread = entry.thread
    decision = thread.decision
    assert decision is not None  # Type narrowing

    # Format source file path with deletion marker if needed
    if entry.is_deleted:
        source_display = f"[deleted: {entry.source_file}]"
    else:
        source_display = entry.source_file

    # Format anchor location
    anchor = thread.anchor
    line_range = (
        f"{anchor.line_start}"
        if anchor.line_start == anchor.line_end
        else f"{anchor.line_start}-{anchor.line_end}"
    )

    # Format timestamp (extract just the date)
    decision_date = decision.timestamp.split("T")[0]

    # Build entry
    lines = [
        f"### {source_display}:{line_range}",
        "",
        f"**Decision**: {decision.summary}",
        "",
        f"**Context**: {anchor.content_snippet}",
        "",
        f"*Decided by {decision.decider} on {decision_date}*",
        "",
    ]

    return "\n".join(lines)


def generate_decisions_markdown(project_root: Path) -> str:
    """Generate complete DECISIONS.md content.

    Args:
        project_root: Project root directory

    Returns:
        Markdown content for DECISIONS.md
    """
    # Collect all decisions
    active_decisions, reopened_decisions = collect_decisions(project_root)

    # Generate header
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines = [
        "# Decision Log",
        "",
        "**Auto-generated — do not edit manually**",
        "",
        f"Last updated: {now}",
        "",
        "---",
        "",
    ]

    # Group active decisions by file
    if active_decisions:
        decisions_by_file: dict[str, list[DecisionEntry]] = defaultdict(list)
        for entry in active_decisions:
            decisions_by_file[entry.source_file].append(entry)

        # Sort files alphabetically
        sorted_files = sorted(decisions_by_file.keys())

        lines.append("## Active Decisions")
        lines.append("")

        for file_path in sorted_files:
            entries = decisions_by_file[file_path]
            # Sort entries by timestamp (newest first)
            entries.sort(key=lambda e: e.resolved_timestamp, reverse=True)

            for entry in entries:
                lines.append(format_decision_entry(entry, project_root))

    # Add reopened decisions section if any exist
    if reopened_decisions:
        # Sort by timestamp (newest first)
        reopened_decisions.sort(key=lambda e: e.resolved_timestamp, reverse=True)

        lines.append("---")
        lines.append("")
        lines.append("## Reopened Decisions")
        lines.append("")
        lines.append("These threads were previously resolved but have been reopened.")
        lines.append("")

        for entry in reopened_decisions:
            lines.append(format_decision_entry(entry, project_root))

    return "\n".join(lines)


def write_decisions_file(project_root: Path) -> int:
    """Generate and write DECISIONS.md file.

    Args:
        project_root: Project root directory

    Returns:
        Number of decisions included in the log
    """
    # Generate markdown content
    content = generate_decisions_markdown(project_root)

    # Write to file
    decisions_path = project_root / "DECISIONS.md"
    decisions_path.write_text(content, encoding="utf-8")

    # Check file size and warn if it exceeds 1 MB
    file_size_bytes = decisions_path.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)
    if file_size_bytes > 1_000_000:
        print(
            f"Warning: DECISIONS.md is {file_size_mb:.1f} MB (> 1 MB recommended maximum)",
            file=sys.stderr,
        )

    # Count decisions
    active, reopened = collect_decisions(project_root)
    return len(active) + len(reopened)

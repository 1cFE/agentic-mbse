"""CLI entry point for the comment system."""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import click

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
from comment_system.storage import (
    compute_source_hash,
    find_project_root,
    get_sidecar_path,
    normalize_path,
    read_sidecar,
    write_sidecar,
)


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of content with 'sha256:' prefix."""
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


def extract_lines(file_path: Path, line_start: int, line_end: int) -> tuple[str, str, str]:
    """
    Extract content and context from source file for anchor creation.

    Args:
        file_path: Path to source file
        line_start: Starting line number (1-indexed, inclusive)
        line_end: Ending line number (1-indexed, inclusive)

    Returns:
        Tuple of (content, context_before, context_after) where:
        - content: The lines from line_start to line_end (inclusive)
        - context_before: Up to 3 lines before line_start
        - context_after: Up to 3 lines after line_end

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If line numbers are invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    # Read all lines from file
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)

    # Validate line numbers
    if line_start < 1 or line_start > total_lines:
        raise ValueError(
            f"Invalid line_start: {line_start} (file has {total_lines} lines, valid range: 1-{total_lines})"
        )
    if line_end < 1 or line_end > total_lines:
        raise ValueError(
            f"Invalid line_end: {line_end} (file has {total_lines} lines, valid range: 1-{total_lines})"
        )
    if line_end < line_start:
        raise ValueError(f"line_end ({line_end}) must be >= line_start ({line_start})")

    # Extract content (convert from 1-indexed to 0-indexed)
    content_lines = lines[line_start - 1 : line_end]
    content = "".join(content_lines).rstrip("\n")

    # Extract context before (up to 3 lines)
    context_start = max(0, line_start - 4)  # -4 because we want 3 lines before
    context_before_lines = lines[context_start : line_start - 1]
    context_before = "".join(context_before_lines).rstrip("\n")

    # Extract context after (up to 3 lines)
    context_after_lines = lines[line_end : line_end + 3]
    context_after = "".join(context_after_lines).rstrip("\n")

    return content, context_before, context_after


def create_anchor(file_path: Path, line_start: int, line_end: int) -> Anchor:
    """
    Create an anchor for a location in a source file.

    Args:
        file_path: Path to source file
        line_start: Starting line number (1-indexed, inclusive)
        line_end: Ending line number (1-indexed, inclusive)

    Returns:
        Anchor object with computed hashes and snippet

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If line numbers are invalid
    """
    content, context_before, context_after = extract_lines(file_path, line_start, line_end)

    # Compute hashes
    content_hash = compute_content_hash(content)
    context_hash_before = compute_content_hash(context_before)
    context_hash_after = compute_content_hash(context_after)

    # Create snippet (truncate to 500 chars max)
    snippet = content[:500] if len(content) <= 500 else content[:497] + "..."

    return Anchor(
        content_hash=content_hash,
        context_hash_before=context_hash_before,
        context_hash_after=context_hash_after,
        line_start=line_start,
        line_end=line_end,
        content_snippet=snippet,
        health=AnchorHealth.ANCHORED,
        drift_distance=0,
    )


@click.group()
@click.version_option(version="0.1.0", prog_name="comment")
def cli():
    """File-native comment threading system for text files."""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-L",
    "--lines",
    "line_range",
    required=True,
    metavar="START:END",
    help="Line range to anchor comment (e.g., -L 10:15)",
)
@click.option(
    "-a",
    "--author",
    default=lambda: click.get_current_context().params.get("author") or "unknown",
    help="Author name (defaults to 'unknown')",
)
@click.option(
    "--author-type",
    type=click.Choice(["human", "agent"], case_sensitive=False),
    default="human",
    help="Type of author (human or agent)",
)
@click.argument("body", required=True)
def add(file_path: Path, line_range: str, author: str, author_type: str, body: str):
    """
    Create a new comment thread anchored to a source location.

    Examples:

        comment add src/main.py -L 42:45 "Fix this function"

        comment add PLAN.md -L 10:10 --author=alice "Needs clarification"
    """
    try:
        # Parse line range
        try:
            parts = line_range.split(":")
            if len(parts) != 2:
                click.echo(
                    f"Error: Invalid line range format: {line_range}\n"
                    "Expected format: START:END (e.g., 10:15)",
                    err=True,
                )
                sys.exit(1)
            line_start = int(parts[0])
            line_end = int(parts[1])
        except ValueError as e:
            if "invalid literal" in str(e):
                click.echo(
                    f"Error: Invalid line range: {line_range}\n"
                    "Line numbers must be integers (e.g., -L 10:15)",
                    err=True,
                )
                sys.exit(1)
            raise

        # Find project root from current working directory
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        # Normalize file path (validates it's within project root)
        try:
            file_path = normalize_path(file_path, project_root)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        # Create anchor
        try:
            anchor = create_anchor(file_path, line_start, line_end)
        except (FileNotFoundError, ValueError) as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        # Create comment
        comment = Comment(
            author=author,
            author_type=AuthorType(author_type.lower()),
            body=body,
        )

        # Create thread
        thread = Thread(
            status=ThreadStatus.OPEN,
            comments=[comment],
            anchor=anchor,
        )

        # Get sidecar path
        sidecar_path = get_sidecar_path(file_path, project_root)

        # Read existing sidecar or create new one
        if sidecar_path.exists():
            try:
                sidecar = read_sidecar(sidecar_path)
                # Update source hash
                sidecar.source_hash = compute_source_hash(file_path)
            except ValueError as e:
                click.echo(f"Error reading sidecar: {e}", err=True)
                sys.exit(2)
        else:
            # Create new sidecar
            try:
                relative_path = file_path.relative_to(project_root)
                sidecar = SidecarFile(
                    source_file=relative_path.as_posix(),
                    source_hash=compute_source_hash(file_path),
                    threads=[],
                )
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)

        # Add thread to sidecar
        sidecar.threads.append(thread)

        # Write sidecar
        try:
            write_sidecar(sidecar_path, sidecar)
        except (ValueError, OSError) as e:
            click.echo(f"Error writing sidecar: {e}", err=True)
            sys.exit(2)

        # Output success message with thread ID
        relative_sidecar = sidecar_path.relative_to(project_root)
        click.echo(f"Created thread {thread.id}")
        click.echo(f"  File: {file_path.relative_to(project_root)}")
        click.echo(f"  Lines: {line_start}:{line_end}")
        click.echo(f"  Sidecar: {relative_sidecar}")

    except Exception as e:
        # Unexpected error (should not happen in normal operation)
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


@cli.command(name="list")
@click.option(
    "--status",
    type=click.Choice(["open", "resolved", "wontfix"], case_sensitive=False),
    help="Filter by thread status",
)
@click.option(
    "--health",
    type=click.Choice(["anchored", "drifted", "orphaned"], case_sensitive=False),
    help="Filter by anchor health",
)
@click.option(
    "--author",
    help="Filter by author name",
)
@click.option(
    "--all",
    "all_files",
    is_flag=True,
    help="List threads from all files in project",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output as JSON instead of human-readable text",
)
@click.argument("file_path", type=click.Path(exists=True, path_type=Path), required=False)
def list_threads(
    status: str | None,
    health: str | None,
    author: str | None,
    all_files: bool,
    json_output: bool,
    file_path: Path | None,
):
    """
    List comment threads with optional filters.

    Examples:

        comment list src/main.py

        comment list --status=open --health=drifted

        comment list --all --author=alice

        comment list --json --all
    """
    try:
        # Validate arguments
        if all_files and file_path:
            click.echo("Error: Cannot specify both --all and a file path", err=True)
            sys.exit(1)

        if not all_files and not file_path:
            click.echo("Error: Must specify either a file path or --all", err=True)
            sys.exit(1)

        # Find project root
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        # Normalize filters
        status_filter = ThreadStatus(status.lower()) if status else None
        health_filter = AnchorHealth(health.lower()) if health else None

        # Collect sidecar files
        sidecar_paths = []
        if all_files:
            # Find all sidecar files in .comments/
            comments_dir = project_root / ".comments"
            if comments_dir.exists():
                sidecar_paths = list(comments_dir.rglob("*.json"))
        else:
            # Single file
            if file_path:
                file_path = normalize_path(file_path, project_root)
                sidecar_path = get_sidecar_path(file_path, project_root)
                if sidecar_path.exists():
                    sidecar_paths = [sidecar_path]

        # Collect matching threads
        matching_threads = []
        for sidecar_path in sidecar_paths:
            try:
                sidecar = read_sidecar(sidecar_path)
                source_file = sidecar.source_file

                for thread in sidecar.threads:
                    # Apply filters
                    if status_filter and thread.status != status_filter:
                        continue
                    if health_filter and thread.anchor.health != health_filter:
                        continue
                    if author and not any(c.author == author for c in thread.comments):
                        continue

                    matching_threads.append((source_file, thread))
            except ValueError:
                # Skip invalid sidecar files
                continue

        # Output results
        if json_output:
            # JSON output
            output = []
            for source_file, thread in matching_threads:
                output.append(
                    {
                        "id": thread.id,
                        "source_file": source_file,
                        "status": thread.status.value,
                        "anchor": {
                            "line_start": thread.anchor.line_start,
                            "line_end": thread.anchor.line_end,
                            "health": thread.anchor.health.value,
                            "drift_distance": thread.anchor.drift_distance,
                        },
                        "comments": len(thread.comments),
                        "created_at": thread.comments[0].timestamp if thread.comments else None,
                    }
                )
            click.echo(json.dumps(output, indent=2))
        else:
            # Human-readable output
            use_color = os.environ.get("NO_COLOR") is None

            if not matching_threads:
                click.echo("No matching threads found.")
                return

            for source_file, thread in matching_threads:
                # Format status with color
                status_str = thread.status.value
                if use_color:
                    if thread.status == ThreadStatus.OPEN:
                        status_str = click.style(status_str, fg="green")
                    elif thread.status == ThreadStatus.RESOLVED:
                        status_str = click.style(status_str, fg="blue")
                    else:  # wontfix
                        status_str = click.style(status_str, fg="yellow")

                # Format health with color
                health_str = thread.anchor.health.value
                if use_color:
                    if thread.anchor.health == AnchorHealth.ANCHORED:
                        health_str = click.style(health_str, fg="green")
                    elif thread.anchor.health == AnchorHealth.DRIFTED:
                        health_str = click.style(health_str, fg="yellow")
                    else:  # orphaned
                        health_str = click.style(health_str, fg="red")

                # Print thread info
                click.echo(
                    f"{thread.id} [{status_str}] [{health_str}] "
                    f"{source_file}:{thread.anchor.line_start}:{thread.anchor.line_end} "
                    f"({len(thread.comments)} comments)"
                )

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


@cli.command()
@click.argument("thread_id", required=True)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output as JSON instead of human-readable text",
)
@click.option(
    "--all",
    "all_files",
    is_flag=True,
    help="Search all files in project (default: search only current directory)",
)
def show(thread_id: str, json_output: bool, all_files: bool):
    """
    Display full thread history with all comments.

    Examples:

        comment show 01HQABCDEFGHIJKLMNOPQRSTUV

        comment show --json 01HQABCDEFGHIJKLMNOPQRSTUV

        comment show --all 01HQABCDEFGHIJKLMNOPQRSTUV
    """
    try:
        # Find project root
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        # Find thread in sidecar files
        found_thread = None
        found_source_file = None

        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    for thread in sidecar.threads:
                        if thread.id == thread_id:
                            found_thread = thread
                            found_source_file = sidecar.source_file
                            break
                    if found_thread:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_thread:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Output thread details
        if json_output:
            # JSON output
            output = {
                "id": found_thread.id,
                "source_file": found_source_file,
                "status": found_thread.status.value,
                "anchor": {
                    "line_start": found_thread.anchor.line_start,
                    "line_end": found_thread.anchor.line_end,
                    "health": found_thread.anchor.health.value,
                    "drift_distance": found_thread.anchor.drift_distance,
                    "content_snippet": found_thread.anchor.content_snippet,
                },
                "comments": [
                    {
                        "id": comment.id,
                        "author": comment.author,
                        "author_type": comment.author_type.value,
                        "timestamp": comment.timestamp,
                        "body": comment.body,
                    }
                    for comment in found_thread.comments
                ],
            }
            if found_thread.decision:
                output["decision"] = {
                    "summary": found_thread.decision.summary,
                    "decider": found_thread.decision.decider,
                    "timestamp": found_thread.decision.timestamp,
                }
            click.echo(json.dumps(output, indent=2))
        else:
            # Human-readable output
            use_color = os.environ.get("NO_COLOR") is None

            # Header
            status_str = found_thread.status.value
            if use_color:
                if found_thread.status == ThreadStatus.OPEN:
                    status_str = click.style(status_str, fg="green", bold=True)
                elif found_thread.status == ThreadStatus.RESOLVED:
                    status_str = click.style(status_str, fg="blue", bold=True)
                else:  # wontfix
                    status_str = click.style(status_str, fg="yellow", bold=True)

            health_str = found_thread.anchor.health.value
            if use_color:
                if found_thread.anchor.health == AnchorHealth.ANCHORED:
                    health_str = click.style(health_str, fg="green")
                elif found_thread.anchor.health == AnchorHealth.DRIFTED:
                    health_str = click.style(health_str, fg="yellow")
                else:  # orphaned
                    health_str = click.style(health_str, fg="red")

            click.echo(f"Thread: {found_thread.id}")
            click.echo(f"Status: {status_str}")
            click.echo(
                f"Location: {found_source_file}:{found_thread.anchor.line_start}:{found_thread.anchor.line_end}"
            )
            click.echo(f"Anchor Health: {health_str}")
            if found_thread.anchor.drift_distance > 0:
                click.echo(f"Drift Distance: {found_thread.anchor.drift_distance} lines")
            click.echo(f"\nSnippet:\n{found_thread.anchor.content_snippet}\n")

            # Comments
            click.echo("Comments:")
            for i, comment in enumerate(found_thread.comments, 1):
                author_str = f"{comment.author} ({comment.author_type.value})"
                if use_color:
                    if comment.author_type == AuthorType.AGENT:
                        author_str = click.style(author_str, fg="cyan")

                click.echo(f"\n[{i}] {author_str} at {comment.timestamp}")
                click.echo(f"    {comment.body}")

            # Decision (if resolved)
            if found_thread.decision:
                click.echo(f"\nDecision by {found_thread.decision.decider} at {found_thread.decision.timestamp}:")
                click.echo(f"    {found_thread.decision.summary}")

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


@cli.command()
@click.argument("thread_id", required=True)
@click.option(
    "-a",
    "--author",
    default=lambda: click.get_current_context().params.get("author") or "unknown",
    help="Author name (defaults to 'unknown')",
)
@click.option(
    "--author-type",
    type=click.Choice(["human", "agent"], case_sensitive=False),
    default="human",
    help="Type of author (human or agent)",
)
@click.argument("body", required=True)
def reply(thread_id: str, author: str, author_type: str, body: str):
    """
    Add a comment to an existing thread.

    Examples:

        comment reply 01HQABCDEFGHIJKLMNOPQRSTUV "I agree with this"

        comment reply --author=alice 01HQABCDEFGHIJKLMNOPQRSTUV "Fixed in PR #123"
    """
    try:
        # Find project root
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        # Find thread in sidecar files
        found_thread = None
        found_sidecar_path = None
        found_sidecar = None

        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    for thread in sidecar.threads:
                        if thread.id == thread_id:
                            found_thread = thread
                            found_sidecar_path = sidecar_path
                            found_sidecar = sidecar
                            break
                    if found_thread:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_thread:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Type narrowing: if found_thread is not None, the others are also not None
        assert found_sidecar_path is not None
        assert found_sidecar is not None

        # Create new comment
        new_comment = Comment(
            author=author,
            author_type=AuthorType(author_type.lower()),
            body=body,
        )

        # Add comment to thread
        found_thread.comments.append(new_comment)

        # Write updated sidecar
        try:
            write_sidecar(found_sidecar_path, found_sidecar)
        except (ValueError, OSError) as e:
            click.echo(f"Error writing sidecar: {e}", err=True)
            sys.exit(2)

        # Output success message
        click.echo(f"Added comment {new_comment.id} to thread {thread_id}")

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


@cli.command()
@click.argument("thread_id", required=True)
@click.option(
    "--decision",
    help="Decision summary (required unless using --wontfix)",
)
@click.option(
    "--decider",
    default=lambda: click.get_current_context().params.get("decider") or "unknown",
    help="Name of person making the decision (defaults to 'unknown')",
)
@click.option(
    "--wontfix",
    is_flag=True,
    help="Mark thread as wontfix instead of resolved",
)
def resolve(thread_id: str, decision: str | None, decider: str, wontfix: bool):
    """
    Close a thread with an optional decision.

    Examples:

        comment resolve 01HQABCDEFGHIJKLMNOPQRSTUV --decision="Fixed in commit abc123"

        comment resolve --decider=alice 01HQABCDEFGHIJKLMNOPQRSTUV --decision="Not an issue"

        comment resolve --wontfix 01HQABCDEFGHIJKLMNOPQRSTUV
    """
    try:
        # Validate arguments
        if not wontfix and not decision:
            click.echo("Error: --decision is required unless using --wontfix", err=True)
            sys.exit(1)

        # Find project root
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        # Find thread in sidecar files
        found_thread = None
        found_sidecar_path = None
        found_sidecar = None

        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    for thread in sidecar.threads:
                        if thread.id == thread_id:
                            found_thread = thread
                            found_sidecar_path = sidecar_path
                            found_sidecar = sidecar
                            break
                    if found_thread:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_thread:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Type narrowing: if found_thread is not None, the others are also not None
        assert found_sidecar_path is not None
        assert found_sidecar is not None

        # Check if already resolved
        if found_thread.status != ThreadStatus.OPEN:
            click.echo(
                f"Error: Thread is already {found_thread.status.value}. "
                f"Use 'comment reopen' to reopen it first.",
                err=True,
            )
            sys.exit(1)

        # Update thread status
        if wontfix:
            found_thread.status = ThreadStatus.WONTFIX
            if decision:
                # Create decision object if decision summary provided
                found_thread.decision = Decision(
                    summary=decision,
                    decider=decider,
                    timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                )
        else:
            # Type narrowing: decision is guaranteed to be str here due to earlier validation
            assert decision is not None
            found_thread.status = ThreadStatus.RESOLVED
            # Create decision object (required for resolved status)
            found_thread.decision = Decision(
                summary=decision,
                decider=decider,
                timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )

        # Write updated sidecar
        try:
            write_sidecar(found_sidecar_path, found_sidecar)
        except (ValueError, OSError) as e:
            click.echo(f"Error writing sidecar: {e}", err=True)
            sys.exit(2)

        # Output success message
        status_str = "wontfix" if wontfix else "resolved"
        click.echo(f"Thread {thread_id} marked as {status_str}")
        if found_thread.decision:
            click.echo(f"  Decision: {found_thread.decision.summary}")

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


@cli.command()
@click.argument("thread_id", required=True)
def reopen(thread_id: str):
    """
    Reopen a resolved or wontfix thread.

    Examples:

        comment reopen 01HQABCDEFGHIJKLMNOPQRSTUV
    """
    try:
        # Find project root
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        # Find thread in sidecar files
        found_thread = None
        found_sidecar_path = None
        found_sidecar = None

        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    for thread in sidecar.threads:
                        if thread.id == thread_id:
                            found_thread = thread
                            found_sidecar_path = sidecar_path
                            found_sidecar = sidecar
                            break
                    if found_thread:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_thread:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Type narrowing: if found_thread is not None, the others are also not None
        assert found_sidecar_path is not None
        assert found_sidecar is not None

        # Check if already open
        if found_thread.status == ThreadStatus.OPEN:
            click.echo("Error: Thread is already open", err=True)
            sys.exit(1)

        # Store previous status for output message
        previous_status = found_thread.status.value

        # Reopen thread (decision is preserved)
        found_thread.status = ThreadStatus.OPEN

        # Write updated sidecar
        try:
            write_sidecar(found_sidecar_path, found_sidecar)
        except (ValueError, OSError) as e:
            click.echo(f"Error writing sidecar: {e}", err=True)
            sys.exit(2)

        # Output success message
        click.echo(f"Thread {thread_id} reopened (was {previous_status})")
        if found_thread.decision:
            click.echo(f"  Previous decision preserved: {found_thread.decision.summary}")

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


if __name__ == "__main__":
    cli()

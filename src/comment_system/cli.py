"""CLI entry point for the comment system."""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from comment_system.anchors import reconcile_sidecar
from comment_system.git_ops import (
    GitError,
    detect_file_rename,
    is_file_deleted_in_git,
    move_sidecar,
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
from comment_system.storage import (
    ConcurrencyConflict,
    compute_source_hash,
    find_project_root,
    get_sidecar_path,
    normalize_path,
    read_sidecar,
    write_sidecar_with_retry,
)


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of content with 'sha256:' prefix."""
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


def format_source_file(source_file: str, project_root: Path, sidecar_path: Path | None = None) -> tuple[str, Path | None]:
    """
    Format source file path with status indicators and optionally detect renames.

    If a sidecar_path is provided and the file is missing, this function will:
    1. Attempt to detect if the file was renamed via git
    2. If a rename is detected, update the sidecar file automatically
    3. Return the new path in the formatted string

    Args:
        source_file: Relative path to source file from sidecar
        project_root: Project root directory
        sidecar_path: Optional sidecar path for auto-rename detection

    Returns:
        Tuple of (formatted_string, new_path):
        - formatted_string: "path/to/file.py", "path/to/file.py [renamed: old.py → new.py]",
                          "path/to/file.py [deleted]", or "path/to/file.py [missing]"
        - new_path: New absolute path if rename was detected and sidecar updated, None otherwise
    """
    file_path = project_root / source_file

    # If file exists, return path as-is
    if file_path.exists():
        return source_file, None

    # File doesn't exist - check for rename if sidecar provided
    new_path = None
    if sidecar_path is not None:
        try:
            new_path = detect_file_rename(file_path, project_root)
            if new_path is not None:
                # Rename detected - update sidecar
                move_sidecar(file_path, new_path, project_root)
                # Format as relative path
                try:
                    new_relative = new_path.relative_to(project_root)
                    return f"{source_file} [renamed: {source_file} → {new_relative.as_posix()}]", new_path
                except ValueError:
                    # New path outside project root (shouldn't happen, but handle gracefully)
                    return f"{source_file} [renamed: {source_file} → {new_path.as_posix()}]", new_path
        except GitError:
            # Git not available or error during rename detection, continue to check deletion
            pass

    # No rename detected - check if it was deleted in git
    try:
        if is_file_deleted_in_git(file_path, project_root):
            return f"{source_file} [deleted]", None
    except GitError:
        # Git not available or not a git repo - can't determine deletion status
        # Just show that file is missing
        pass

    # File missing but not confirmed deleted (might be renamed or never tracked)
    return f"{source_file} [missing]", None


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
    metavar="START:END",
    help="Line range to anchor comment (e.g., -L 10:15)",
)
@click.option(
    "--match",
    "match_text",
    metavar="TEXT",
    help="Anchor to first occurrence of text (fails if ambiguous)",
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
def add(
    file_path: Path,
    line_range: str | None,
    match_text: str | None,
    author: str,
    author_type: str,
    body: str,
):
    """
    Create a new comment thread anchored to a source location.

    Examples:

        comment add src/main.py -L 42:45 "Fix this function"

        comment add PLAN.md -L 10:10 --author=alice "Needs clarification"

        comment add PLAN.md --match "linear scaling" "Optimize this"
    """
    try:
        # Validate anchoring method: must specify exactly one of -L or --match
        if line_range is None and match_text is None:
            click.echo(
                "Error: Must specify either -L (line range) or --match (text pattern)",
                err=True,
            )
            sys.exit(1)

        if line_range is not None and match_text is not None:
            click.echo(
                "Error: Cannot specify both -L and --match (mutually exclusive)",
                err=True,
            )
            sys.exit(1)

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

        # Determine line range (either from -L or from --match)
        if line_range is not None:
            # Parse line range from -L option
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
        else:
            # Find text match in file
            assert match_text is not None  # Type narrowing for mypy
            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()
            except (FileNotFoundError, OSError) as e:
                click.echo(f"Error reading file: {e}", err=True)
                sys.exit(1)

            # Find all occurrences of match_text
            matches = []
            for line_num, line in enumerate(lines, start=1):
                if match_text in line:
                    matches.append(line_num)

            if len(matches) == 0:
                click.echo(
                    f"Error: Text not found: '{match_text}'",
                    err=True,
                )
                sys.exit(1)
            elif len(matches) > 1:
                click.echo(
                    f"Error: Ambiguous match: text appears {len(matches)} times on lines {', '.join(map(str, matches))}",
                    err=True,
                )
                sys.exit(1)
            else:
                # Single match - anchor to that line
                line_start = matches[0]
                line_end = matches[0]

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

        # Define update function for write_sidecar_with_retry
        def add_thread_to_sidecar(current: SidecarFile | None) -> SidecarFile:
            if current is not None:
                # Update existing sidecar
                current.source_hash = compute_source_hash(file_path)
                current.threads.append(thread)
                return current
            else:
                # Create new sidecar
                try:
                    relative_path = file_path.relative_to(project_root)
                    return SidecarFile(
                        source_file=relative_path.as_posix(),
                        source_hash=compute_source_hash(file_path),
                        threads=[thread],
                    )
                except ValueError as e:
                    click.echo(f"Error: {e}", err=True)
                    sys.exit(1)

        # Write sidecar with automatic retry on concurrency conflicts
        try:
            write_sidecar_with_retry(sidecar_path, add_thread_to_sidecar)
        except ConcurrencyConflict as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)
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

                    matching_threads.append((source_file, thread, sidecar_path))
            except ValueError:
                # Skip invalid sidecar files
                continue

        # Output results
        if json_output:
            # JSON output
            output = []
            for source_file, thread, sidecar_path in matching_threads:
                # Check for renames (will update sidecar if detected)
                formatted_source, new_path = format_source_file(source_file, project_root, sidecar_path)
                # If renamed, use new path for output (strip rename message)
                display_source = source_file
                if new_path:
                    try:
                        display_source = new_path.relative_to(project_root).as_posix()
                    except ValueError:
                        display_source = new_path.as_posix()

                output.append(
                    {
                        "id": thread.id,
                        "source_file": display_source,
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

            for source_file, thread, sidecar_path in matching_threads:
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

                # Format source file with rename detection/deletion indicator
                formatted_source, new_path = format_source_file(source_file, project_root, sidecar_path)

                # For display, use new path if renamed (strip brackets for line numbers)
                display_source = source_file
                if new_path:
                    try:
                        display_source = new_path.relative_to(project_root).as_posix()
                    except ValueError:
                        display_source = new_path.as_posix()
                elif "[" in formatted_source:
                    # Has status indicator [deleted] or [missing], use formatted_source for display
                    display_source = formatted_source

                # Print thread info
                click.echo(
                    f"{thread.id} [{status_str}] [{health_str}] "
                    f"{display_source}:{thread.anchor.line_start}:{thread.anchor.line_end} "
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
        found_sidecar_path = None

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
                            found_sidecar_path = sidecar_path
                            break
                    if found_thread:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_thread:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Type narrowing for mypy
        assert found_source_file is not None, (
            "found_source_file must be set when found_thread is set"
        )
        assert found_sidecar_path is not None, (
            "found_sidecar_path must be set when found_thread is set"
        )

        # Check for rename (will update sidecar if detected)
        formatted_source, new_path = format_source_file(found_source_file, project_root, found_sidecar_path)
        # Update source file path if renamed
        display_source_file = found_source_file
        if new_path:
            try:
                display_source_file = new_path.relative_to(project_root).as_posix()
            except ValueError:
                display_source_file = new_path.as_posix()
        else:
            # No rename detected, use formatted_source which may have [deleted] or [missing] markers
            display_source_file = formatted_source

        # Output thread details
        if json_output:
            # JSON output
            output = {
                "id": found_thread.id,
                "source_file": display_source_file,
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

            # Use the display_source_file which includes status markers
            click.echo(f"Thread: {found_thread.id}")
            click.echo(f"Status: {status_str}")
            click.echo(
                f"Location: {display_source_file}:{found_thread.anchor.line_start}:{found_thread.anchor.line_end}"
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
                click.echo(
                    f"\nDecision by {found_thread.decision.decider} at {found_thread.decision.timestamp}:"
                )
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
        found_sidecar_path = None

        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    for thread in sidecar.threads:
                        if thread.id == thread_id:
                            found_sidecar_path = sidecar_path
                            break
                    if found_sidecar_path:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_sidecar_path:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Create new comment
        new_comment = Comment(
            author=author,
            author_type=AuthorType(author_type.lower()),
            body=body,
        )

        # Define update function for write_sidecar_with_retry
        def add_comment_to_thread(current: SidecarFile | None) -> SidecarFile:
            if current is None:
                click.echo("Error: Sidecar file was deleted", err=True)
                sys.exit(2)

            # Find thread in current sidecar (may have changed since initial search)
            target_thread = None
            for thread in current.threads:
                if thread.id == thread_id:
                    target_thread = thread
                    break

            if target_thread is None:
                click.echo(f"Error: Thread {thread_id} not found in sidecar", err=True)
                sys.exit(1)

            # Add comment to thread
            target_thread.comments.append(new_comment)
            return current

        # Write updated sidecar with automatic retry
        try:
            write_sidecar_with_retry(found_sidecar_path, add_comment_to_thread)
        except ConcurrencyConflict as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)
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
        found_sidecar_path = None

        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    for thread in sidecar.threads:
                        if thread.id == thread_id:
                            found_sidecar_path = sidecar_path
                            break
                    if found_sidecar_path:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_sidecar_path:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Store decision reference for output message (will be set in update function)
        decision_ref: dict[str, Decision | None] = {"decision": None}

        # Define update function for write_sidecar_with_retry
        def resolve_thread(current: SidecarFile | None) -> SidecarFile:
            if current is None:
                click.echo("Error: Sidecar file was deleted", err=True)
                sys.exit(2)

            # Find thread in current sidecar (may have changed since initial search)
            target_thread = None
            for thread in current.threads:
                if thread.id == thread_id:
                    target_thread = thread
                    break

            if target_thread is None:
                click.echo(f"Error: Thread {thread_id} not found in sidecar", err=True)
                sys.exit(1)

            # Check if already resolved
            if target_thread.status != ThreadStatus.OPEN:
                click.echo(
                    f"Error: Thread is already {target_thread.status.value}. "
                    f"Use 'comment reopen' to reopen it first.",
                    err=True,
                )
                sys.exit(1)

            # Update thread status
            if wontfix:
                target_thread.status = ThreadStatus.WONTFIX
                if decision:
                    # Create decision object if decision summary provided
                    target_thread.decision = Decision(
                        summary=decision,
                        decider=decider,
                        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    )
                    decision_ref["decision"] = target_thread.decision
            else:
                # Type narrowing: decision is guaranteed to be str here due to earlier validation
                assert decision is not None
                target_thread.status = ThreadStatus.RESOLVED
                # Create decision object (required for resolved status)
                target_thread.decision = Decision(
                    summary=decision,
                    decider=decider,
                    timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                )
                decision_ref["decision"] = target_thread.decision

            return current

        # Write updated sidecar with automatic retry
        try:
            write_sidecar_with_retry(found_sidecar_path, resolve_thread)
        except ConcurrencyConflict as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)
        except (ValueError, OSError) as e:
            click.echo(f"Error writing sidecar: {e}", err=True)
            sys.exit(2)

        # Output success message
        status_str = "wontfix" if wontfix else "resolved"
        click.echo(f"Thread {thread_id} marked as {status_str}")
        if decision_ref["decision"]:
            click.echo(f"  Decision: {decision_ref['decision'].summary}")

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
        found_sidecar_path = None

        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    for thread in sidecar.threads:
                        if thread.id == thread_id:
                            found_sidecar_path = sidecar_path
                            break
                    if found_sidecar_path:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_sidecar_path:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Store previous status for output message (will be set in update function)
        previous_status_ref: dict[str, str | Decision | None] = {"status": "", "decision": None}

        # Define update function for write_sidecar_with_retry
        def reopen_thread(current: SidecarFile | None) -> SidecarFile:
            if current is None:
                click.echo("Error: Sidecar file was deleted", err=True)
                sys.exit(2)

            # Find thread in current sidecar (may have changed since initial search)
            target_thread = None
            for thread in current.threads:
                if thread.id == thread_id:
                    target_thread = thread
                    break

            if target_thread is None:
                click.echo(f"Error: Thread {thread_id} not found in sidecar", err=True)
                sys.exit(1)

            # Check if already open
            if target_thread.status == ThreadStatus.OPEN:
                click.echo("Error: Thread is already open", err=True)
                sys.exit(1)

            # Store previous status for output message
            previous_status_ref["status"] = target_thread.status.value
            previous_status_ref["decision"] = target_thread.decision

            # Reopen thread (decision is preserved)
            target_thread.status = ThreadStatus.OPEN

            return current

        # Write updated sidecar with automatic retry
        try:
            write_sidecar_with_retry(found_sidecar_path, reopen_thread)
        except ConcurrencyConflict as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)
        except (ValueError, OSError) as e:
            click.echo(f"Error writing sidecar: {e}", err=True)
            sys.exit(2)

        # Output success message
        click.echo(f"Thread {thread_id} reopened (was {previous_status_ref['status']})")
        decision = previous_status_ref["decision"]
        if decision:
            # Type narrowing: decision is Decision here
            assert isinstance(decision, Decision)
            click.echo(f"  Previous decision preserved: {decision.summary}")

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


@cli.command()
@click.argument("thread_id", required=True)
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def delete(thread_id: str, force: bool):
    """
    Delete a thread permanently.

    Removes the thread and all its comments from the sidecar file.
    If the sidecar has no remaining threads after deletion, the
    sidecar file itself is deleted.

    Examples:

        comment delete 01HQABCDEFGHIJKLMNOPQRSTUV
        comment delete 01HQABCDEFGHIJKLMNOPQRSTUV --force
    """
    try:
        # Find project root
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        # Find thread in sidecar files
        found_sidecar_path = None

        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    for thread in sidecar.threads:
                        if thread.id == thread_id:
                            found_sidecar_path = sidecar_path
                            break
                    if found_sidecar_path:
                        break
                except ValueError:
                    # Skip invalid sidecar files
                    continue

        if not found_sidecar_path:
            click.echo(f"Error: Thread not found: {thread_id}", err=True)
            sys.exit(1)

        # Confirm deletion unless --force
        if not force:
            click.confirm(
                f"Delete thread {thread_id}? This cannot be undone.",
                abort=True,
            )

        # Track thread info for output message
        deleted_comment_count = 0

        # Define update function for write_sidecar_with_retry
        def delete_thread(current: SidecarFile | None) -> SidecarFile:
            nonlocal deleted_comment_count
            if current is None:
                click.echo("Error: Sidecar file was deleted", err=True)
                sys.exit(2)

            # Find and remove the thread
            original_count = len(current.threads)
            current.threads = [t for t in current.threads if t.id != thread_id]

            if len(current.threads) == original_count:
                click.echo(f"Error: Thread {thread_id} not found in sidecar", err=True)
                sys.exit(1)

            # Count deleted comments for output message
            deleted_comment_count = original_count - len(current.threads)

            return current

        # Write updated sidecar with automatic retry
        try:
            result = write_sidecar_with_retry(found_sidecar_path, delete_thread)
        except ConcurrencyConflict as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)
        except (ValueError, OSError) as e:
            click.echo(f"Error writing sidecar: {e}", err=True)
            sys.exit(2)

        # If no threads remain, delete the sidecar file
        if len(result.threads) == 0:
            try:
                found_sidecar_path.unlink()
                # Also clean up empty parent directories under .comments/
                parent = found_sidecar_path.parent
                while parent != comments_dir and parent.exists():
                    try:
                        parent.rmdir()  # Only removes if empty
                        parent = parent.parent
                    except OSError:
                        break
            except OSError:
                pass  # Best-effort cleanup

        click.echo(f"Thread {thread_id} deleted")

    except click.Abort:
        click.echo("Delete cancelled")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


def _format_health(health: str, count: int) -> str:
    """Format health status with color coding and count.

    Args:
        health: Health status string ('anchored', 'drifted', 'orphaned')
        count: Number of threads with this health status

    Returns:
        Formatted string with color (if NO_COLOR not set) and count
    """
    use_color = not os.environ.get("NO_COLOR")

    if use_color:
        if health == "anchored":
            health_str = click.style(health, fg="green")
        elif health == "drifted":
            health_str = click.style(health, fg="yellow")
        else:  # orphaned
            health_str = click.style(health, fg="red")
    else:
        health_str = health

    return f"{health_str} ({count})" if count > 0 else f"{health_str} (0)"


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path), required=False)
@click.option("--all", "reconcile_all", is_flag=True, help="Reconcile all files in project")
@click.option("--json", "json_output", is_flag=True, help="Output results as JSON")
@click.option(
    "--threshold",
    type=float,
    default=0.6,
    help="Minimum similarity score for fuzzy matching (0-1, default: 0.6)",
)
def reconcile(
    file: Path | None,
    reconcile_all: bool,
    json_output: bool,
    threshold: float,
) -> None:
    """Reconcile comment anchors to current source file state.

    Updates anchor positions after file edits using multi-signal reconciliation.
    Use --all to reconcile all files in the project.

    Examples:
        comment reconcile src/foo.py
        comment reconcile --all
        comment reconcile src/foo.py --json
    """
    try:
        # Validate arguments
        if not file and not reconcile_all:
            click.echo("Error: Must specify either FILE or --all", err=True)
            sys.exit(1)

        if file and reconcile_all:
            click.echo("Error: Cannot specify both FILE and --all", err=True)
            sys.exit(1)

        # Validate threshold
        if not 0.0 <= threshold <= 1.0:
            click.echo(f"Error: Threshold must be between 0 and 1, got {threshold}", err=True)
            sys.exit(1)

        # Find project root
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        if reconcile_all:
            # Reconcile all sidecar files in project
            comments_dir = project_root / ".comments"
            if not comments_dir.exists():
                if json_output:
                    click.echo(json.dumps({"files": [], "total_threads": 0, "renames": []}))
                else:
                    click.echo("No comment files found in project")
                return

            # Find all sidecar files
            sidecar_paths = list(comments_dir.rglob("*.json"))
            if not sidecar_paths:
                if json_output:
                    click.echo(json.dumps({"files": [], "total_threads": 0, "renames": []}))
                else:
                    click.echo("No comment files found in project")
                return

            # First pass: Detect and apply file renames
            rename_operations = []
            for sidecar_path in sidecar_paths:
                try:
                    sidecar = read_sidecar(sidecar_path)
                    source_path = project_root / sidecar.source_file

                    # If source file doesn't exist, try to detect rename
                    if not source_path.exists():
                        try:
                            new_path = detect_file_rename(source_path, project_root)
                            if new_path is not None:
                                # Rename detected - update sidecar
                                if move_sidecar(source_path, new_path, project_root):
                                    try:
                                        new_relative = new_path.relative_to(project_root).as_posix()
                                        rename_operations.append((sidecar.source_file, new_relative))
                                    except ValueError:
                                        rename_operations.append((sidecar.source_file, new_path.as_posix()))
                        except GitError:
                            # Git not available or error, skip rename detection for this file
                            pass
                except (ValueError, OSError):
                    # Skip invalid sidecar files
                    continue

            # Refresh sidecar paths after renames
            sidecar_paths = list(comments_dir.rglob("*.json"))

            # Second pass: Reconcile anchors
            results = []
            total_threads = 0
            total_anchored = 0
            total_drifted = 0
            total_orphaned = 0
            max_drift = 0

            for sidecar_path in sidecar_paths:
                # Compute source path from sidecar path
                relative_path = sidecar_path.relative_to(comments_dir)
                # Remove .json suffix
                source_relative = Path(str(relative_path)[: -len(".json")])
                source_path = project_root / source_relative

                if not source_path.exists():
                    # Skip if source file no longer exists (orphaned sidecar)
                    continue

                try:
                    report = reconcile_sidecar(
                        sidecar_path=sidecar_path,
                        source_path=source_path,
                        threshold=threshold,
                    )

                    total_threads += report.total_threads
                    total_anchored += report.anchored_count
                    total_drifted += report.drifted_count
                    total_orphaned += report.orphaned_count
                    max_drift = max(max_drift, report.max_drift_distance)

                    results.append(
                        {
                            "file": str(source_relative),
                            "total_threads": report.total_threads,
                            "anchored": report.anchored_count,
                            "drifted": report.drifted_count,
                            "orphaned": report.orphaned_count,
                            "max_drift": report.max_drift_distance,
                        }
                    )
                except (ValueError, OSError) as e:
                    if json_output:
                        results.append({"file": str(source_relative), "error": str(e)})
                    else:
                        click.echo(f"Warning: Failed to reconcile {source_relative}: {e}", err=True)

            if json_output:
                click.echo(
                    json.dumps(
                        {
                            "files": results,
                            "renames": [{"old": old, "new": new} for old, new in rename_operations],
                            "total_threads": total_threads,
                            "total_anchored": total_anchored,
                            "total_drifted": total_drifted,
                            "total_orphaned": total_orphaned,
                            "max_drift": max_drift,
                        },
                        indent=2,
                    )
                )
            else:
                # Report renames first
                if rename_operations:
                    click.echo(f"Detected {len(rename_operations)} file rename(s):")
                    for old_renamed, new_renamed in rename_operations:
                        click.echo(f"  {old_renamed} → {new_renamed}")
                    click.echo()

                click.echo(f"Reconciled {len(results)} files:")
                click.echo(f"  Total threads: {total_threads}")
                click.echo(f"  Anchored: {_format_health('anchored', total_anchored)}")
                click.echo(f"  Drifted: {_format_health('drifted', total_drifted)}")
                click.echo(f"  Orphaned: {_format_health('orphaned', total_orphaned)}")
                if max_drift > 0:
                    click.echo(f"  Max drift: {max_drift} lines")

        else:
            # Reconcile single file
            assert file is not None  # For type checker

            # Normalize and validate file path
            try:
                source_path = normalize_path(file, project_root)
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)

            # Get sidecar path
            sidecar_path = get_sidecar_path(source_path, project_root)

            # Check if sidecar exists
            if not sidecar_path.exists():
                click.echo(f"Error: No comments found for {file}", err=True)
                sys.exit(1)

            # Check for rename before reconciling
            rename_detected = False
            if not source_path.exists():
                try:
                    new_path = detect_file_rename(source_path, project_root)
                    if new_path is not None:
                        # Rename detected - update sidecar
                        if move_sidecar(source_path, new_path, project_root):
                            rename_detected = True
                            # Update source_path and sidecar_path for reconciliation
                            source_path = new_path
                            sidecar_path = get_sidecar_path(source_path, project_root)
                            if not json_output:
                                try:
                                    old_relative = file.relative_to(project_root).as_posix()
                                except ValueError:
                                    old_relative = str(file)
                                try:
                                    new_relative = new_path.relative_to(project_root).as_posix()
                                except ValueError:
                                    new_relative = new_path.as_posix()
                                click.echo(f"Detected file rename: {old_relative} → {new_relative}")
                                click.echo()
                except GitError:
                    # Git not available or error, continue without rename detection
                    pass

            # Reconcile
            try:
                report = reconcile_sidecar(
                    sidecar_path=sidecar_path,
                    source_path=source_path,
                    threshold=threshold,
                )
            except FileNotFoundError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(2)
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)
            except OSError as e:
                click.echo(f"Error writing sidecar: {e}", err=True)
                sys.exit(2)

            if json_output:
                output_dict = {
                    "file": str(source_path.relative_to(project_root) if source_path.is_relative_to(project_root) else source_path),
                    "renamed": rename_detected,
                    "total_threads": report.total_threads,
                    "anchored": report.anchored_count,
                    "drifted": report.drifted_count,
                    "orphaned": report.orphaned_count,
                    "max_drift": report.max_drift_distance,
                    "source_hash_before": report.source_hash_before,
                    "source_hash_after": report.source_hash_after,
                }
                click.echo(json.dumps(output_dict, indent=2))
            else:
                display_file = source_path.relative_to(project_root) if source_path.is_relative_to(project_root) else source_path
                click.echo(f"Reconciled {display_file}:")
                click.echo(f"  Total threads: {report.total_threads}")
                click.echo(f"  Anchored: {_format_health('anchored', report.anchored_count)}")
                click.echo(f"  Drifted: {_format_health('drifted', report.drifted_count)}")
                click.echo(f"  Orphaned: {_format_health('orphaned', report.orphaned_count)}")
                if report.max_drift_distance > 0:
                    click.echo(f"  Max drift: {report.max_drift_distance} lines")

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


@cli.command()
def decisions() -> None:
    """Generate DECISIONS.md from resolved comment threads.

    Aggregates all resolved threads with decisions into a human-readable
    decision log at the project root. Idempotent - safe to run repeatedly.
    """
    from .decisions import write_decisions_file

    try:
        # Find project root
        try:
            project_root = find_project_root()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        # Generate DECISIONS.md
        try:
            decision_count = write_decisions_file(project_root)
        except OSError as e:
            click.echo(f"Error writing DECISIONS.md: {e}", err=True)
            sys.exit(2)

        # Output success message
        decisions_path = project_root / "DECISIONS.md"
        click.echo(f"Generated {decisions_path}")
        click.echo(f"  {decision_count} decision(s) included")

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


if __name__ == "__main__":
    cli()

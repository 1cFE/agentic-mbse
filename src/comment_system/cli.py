"""CLI entry point for the comment system."""

import hashlib
import sys
from pathlib import Path

import click

from comment_system.models import (
    Anchor,
    AnchorHealth,
    AuthorType,
    Comment,
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


if __name__ == "__main__":
    cli()

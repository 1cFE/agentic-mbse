"""Git integration for file rename and deletion tracking.

This module provides utilities to detect file renames via git history,
enabling the comment system to maintain associations when source files move.
"""

import subprocess
from pathlib import Path

from comment_system.storage import get_sidecar_path, read_sidecar


class GitError(Exception):
    """Base exception for git-related errors."""

    pass


class GitNotAvailableError(GitError):
    """Raised when git is not available in the environment."""

    pass


class NotAGitRepositoryError(GitError):
    """Raised when operating outside a git repository."""

    pass


def is_git_available() -> bool:
    """
    Check if git is available in the environment.

    Returns:
        True if git command is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return False


def is_git_repository(path: Path) -> bool:
    """
    Check if the given path is within a git repository.

    Args:
        path: Directory or file path to check

    Returns:
        True if path is within a git repository, False otherwise
    """
    try:
        # Use git rev-parse to check if we're in a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=path if path.is_dir() else path.parent,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return False


def detect_file_rename(old_path: Path, project_root: Path, max_renames: int = 10) -> Path | None:
    """
    Detect if a file has been renamed using git history.

    Uses `git log --all --diff-filter=R` to find all renames in the repository,
    then follows the rename chain forward from the given old_path.
    Handles rename chains (A → B → C) up to max_renames depth.

    Args:
        old_path: Original file path (may no longer exist)
        project_root: Git repository root directory
        max_renames: Maximum number of renames to follow (default 10, per CON-4)

    Returns:
        New file path if rename detected, None if file not renamed or git not available

    Raises:
        GitNotAvailableError: If git command is not available
        NotAGitRepositoryError: If project_root is not a git repository
    """
    # Check git availability
    if not is_git_available():
        raise GitNotAvailableError("Git is not available in the environment")

    # Check if we're in a git repository
    if not is_git_repository(project_root):
        raise NotAGitRepositoryError(f"{project_root} is not a git repository")

    # Make path relative to project root for git operations
    try:
        relative_path = old_path.relative_to(project_root)
    except ValueError:
        # Path is outside project root
        return None

    # Use git log to get all renames in the repository
    # --all: search all branches
    # --diff-filter=R: only show renames
    # --name-status: show old and new names
    # --pretty=format:: suppress commit metadata
    # --find-renames: detect renames
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--all",
                "--diff-filter=R",
                "--name-status",
                "--pretty=format:",
                "--find-renames",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            # Git command failed
            return None

        # Parse output: each line is "R<similarity>\told_name\tnew_name"
        # Example: "R100\told.md\tnew.md"
        lines = [line for line in result.stdout.strip().split("\n") if line]

        if not lines:
            # No renames found
            return None

        # Build a rename mapping: old_path -> new_path
        rename_map: dict[Path, Path] = {}
        for line in lines:
            parts = line.split("\t")
            if len(parts) < 3:
                # Invalid line format, skip
                continue

            # parts[0] is "R<similarity>", parts[1] is old, parts[2] is new
            old_name = Path(parts[1])
            new_name = Path(parts[2])
            rename_map[old_name] = new_name

        # Follow the rename chain from relative_path
        current_path = relative_path
        renames_followed = 0

        while current_path in rename_map and renames_followed < max_renames:
            current_path = rename_map[current_path]
            renames_followed += 1

        # If path changed, return the new absolute path
        if current_path != relative_path:
            new_absolute = project_root / current_path

            # Verify new path exists (might have been deleted after rename)
            if new_absolute.exists():
                return new_absolute

    except subprocess.TimeoutExpired:
        # Git command took too long
        return None
    except (subprocess.SubprocessError, OSError):
        # Other git errors
        return None

    return None


def move_sidecar(old_source_path: Path, new_source_path: Path, project_root: Path) -> bool:
    """
    Move sidecar file when source file is renamed.

    Updates the sidecar's source_file field and moves the sidecar file
    to mirror the new source location. Uses atomic operations (temp + rename).

    Args:
        old_source_path: Original source file path
        new_source_path: New source file path
        project_root: Project root directory

    Returns:
        True if sidecar was moved, False if no sidecar exists

    Raises:
        OSError: If file operations fail
    """
    # Get old and new sidecar paths
    old_sidecar = get_sidecar_path(old_source_path, project_root)
    new_sidecar = get_sidecar_path(new_source_path, project_root)

    # Check if old sidecar exists
    if not old_sidecar.exists():
        return False

    # Read existing sidecar
    sidecar_data = read_sidecar(old_sidecar)

    # Update source_file field to new path (store as relative path)
    try:
        relative_new_path = new_source_path.relative_to(project_root)
        sidecar_data.source_file = relative_new_path.as_posix()
    except ValueError:
        # Path is outside project root, store absolute path
        sidecar_data.source_file = new_source_path.as_posix()

    # Create parent directory for new sidecar if needed
    new_sidecar.parent.mkdir(parents=True, exist_ok=True)

    # Write to new location using atomic operation
    # (we can't use write_sidecar directly here because it would try to update hash,
    #  and we're moving the file without necessarily changing the source content)
    # Instead, we'll write directly with atomic temp + rename pattern
    import json
    import tempfile

    # Serialize sidecar data
    sidecar_dict = sidecar_data.model_dump(mode="json")
    json_str = json.dumps(sidecar_dict, indent=2, sort_keys=True)

    # Write to temp file in same directory (ensures atomic rename on same filesystem)
    temp_fd, temp_path_str = tempfile.mkstemp(dir=new_sidecar.parent, suffix=".tmp.json", text=True)
    temp_path = Path(temp_path_str)

    try:
        # Write content
        with open(temp_fd, "w", encoding="utf-8") as f:
            f.write(json_str)

        # Atomic rename
        temp_path.rename(new_sidecar)

        # Remove old sidecar
        old_sidecar.unlink()

        # Clean up old sidecar directory if empty
        try:
            old_sidecar.parent.rmdir()
        except OSError:
            # Directory not empty or other error, ignore
            pass

        return True

    except Exception:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise


def is_file_deleted_in_git(file_path: Path, project_root: Path) -> bool:
    """
    Check if a file has been deleted from git (not just missing from filesystem).

    A file is considered deleted in git if:
    1. It doesn't exist in the filesystem
    2. It appears in git history (was previously tracked)
    3. It hasn't been renamed (rename detection returns None)

    This distinguishes between:
    - Deleted files (in git history, not renamed, not in filesystem) → True
    - Never-tracked files (not in git history) → False
    - Renamed files (in git history, renamed to new location) → False
    - Existing files → False

    Args:
        file_path: Path to check (may not exist)
        project_root: Git repository root directory

    Returns:
        True if file was deleted from git, False otherwise

    Raises:
        GitNotAvailableError: If git command is not available
        NotAGitRepositoryError: If project_root is not a git repository
    """
    # Check git availability
    if not is_git_available():
        raise GitNotAvailableError("Git is not available in the environment")

    # Check if we're in a git repository
    if not is_git_repository(project_root):
        raise NotAGitRepositoryError(f"{project_root} is not a git repository")

    # If file exists, it's not deleted
    if file_path.exists():
        return False

    # Check if file was renamed (if so, it's not deleted, just moved)
    try:
        renamed_path = detect_file_rename(file_path, project_root)
        if renamed_path is not None:
            # File was renamed, not deleted
            return False
    except GitError:
        # If rename detection fails, continue to check deletion
        pass

    # Make path relative to project root for git operations
    try:
        relative_path = file_path.relative_to(project_root)
    except ValueError:
        # Path is outside project root
        return False

    # Use git log to check if file was ever in history
    # If it appears in history but doesn't exist and wasn't renamed, it was deleted
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--all",
                "--oneline",
                "--",
                str(relative_path),
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            # Git command failed
            return False

        # If output is non-empty, file was in history
        # Since file doesn't exist and wasn't renamed, it was deleted
        return bool(result.stdout.strip())

    except subprocess.TimeoutExpired:
        # Git command took too long
        return False
    except (subprocess.SubprocessError, OSError):
        # Other git errors
        return False


def detect_and_move_all_sidecars(project_root: Path) -> list[tuple[Path, Path]]:
    """
    Detect all file renames and move corresponding sidecars.

    Scans all existing sidecar files, detects if their source files have been
    renamed via git, and moves the sidecars to match. Handles directory renames
    by processing all affected files.

    Args:
        project_root: Project root directory

    Returns:
        List of (old_path, new_path) tuples for all moved sidecars

    Raises:
        GitNotAvailableError: If git is not available
        NotAGitRepositoryError: If not in a git repository
    """
    # Find all sidecar files
    comments_dir = project_root / ".comments"
    if not comments_dir.exists():
        return []

    moved_sidecars: list[tuple[Path, Path]] = []

    # Iterate through all .json files in .comments directory
    for sidecar_path in comments_dir.rglob("*.json"):
        # Skip if not a regular file
        if not sidecar_path.is_file():
            continue

        # Read sidecar to get source file path
        try:
            sidecar_data = read_sidecar(sidecar_path)
        except Exception:
            # Skip invalid sidecar files
            continue

        # Reconstruct source path from sidecar's source_file field
        source_path = project_root / sidecar_data.source_file

        # If source file doesn't exist, try to detect rename
        if not source_path.exists():
            try:
                new_path = detect_file_rename(source_path, project_root)
                if new_path is not None:
                    # Rename detected, move sidecar
                    if move_sidecar(source_path, new_path, project_root):
                        moved_sidecars.append((source_path, new_path))
            except GitError:
                # Skip this file if git operations fail
                continue

    return moved_sidecars

"""Git integration for file rename and deletion tracking.

This module provides utilities to detect file renames via git history,
enabling the comment system to maintain associations when source files move.
"""

import subprocess
from pathlib import Path


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


def detect_file_rename(
    old_path: Path, project_root: Path, max_renames: int = 10
) -> Path | None:
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

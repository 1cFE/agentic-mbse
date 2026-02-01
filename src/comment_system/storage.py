"""Sidecar file I/O — reading and writing .comments/*.json files."""

import hashlib
from pathlib import Path


def compute_source_hash(path: Path) -> str:
    """
    Compute SHA-256 hash of source file contents.

    Args:
        path: Path to source file (must exist and be readable)

    Returns:
        Hash string with "sha256:" prefix (e.g., "sha256:abc123...")

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is binary or unreadable
        PermissionError: If file cannot be read
    """
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    # Check if file is binary
    if is_binary_file(path):
        raise ValueError(
            f"Binary files not supported: {path}\n"
            "The comment system only supports text files."
        )

    # Compute SHA-256 hash
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        # Read in chunks for efficiency with large files
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)

    return f"sha256:{sha256_hash.hexdigest()}"


def is_binary_file(path: Path) -> bool:
    """
    Detect if file contains binary content.

    Uses a heuristic: reads first 8192 bytes and checks for null bytes.
    This is the same approach used by git and many text editors.

    Args:
        path: Path to file

    Returns:
        True if file appears to be binary, False if it appears to be text
    """
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except Exception:
        # If we can't read the file, assume it's binary for safety
        return True


def get_sidecar_path(source_path: Path, project_root: Path) -> Path:
    """
    Map source file path to its sidecar file path.

    The sidecar path mirrors the source tree structure under .comments/:
    - src/foo/bar.py → .comments/src/foo/bar.py.json
    - models/model.sysml → .comments/models/model.sysml.json

    Args:
        source_path: Path to source file (absolute or relative to project_root)
        project_root: Root directory of the project

    Returns:
        Absolute path to sidecar file (.comments/<relative_path>.json)

    Raises:
        ValueError: If source_path is outside project_root
    """
    # Ensure both paths are absolute
    source_abs = source_path.resolve()
    root_abs = project_root.resolve()

    # Check if source is within project root
    try:
        relative = source_abs.relative_to(root_abs)
    except ValueError:
        raise ValueError(
            f"Source file is outside project root:\n"
            f"  Source: {source_abs}\n"
            f"  Root: {root_abs}"
        )

    # Build sidecar path: <project_root>/.comments/<relative_path>.json
    sidecar_path = root_abs / ".comments" / f"{relative}.json"
    return sidecar_path


def normalize_path(path: Path, project_root: Path) -> Path:
    """
    Normalize and validate a file path relative to project root.

    Performs the following:
    1. Resolves relative paths (.. components)
    2. Converts to absolute path
    3. Normalizes path separators (POSIX/Windows)
    4. Validates path is within project root (security check)

    Args:
        path: Path to normalize (can be relative or absolute)
        project_root: Root directory of the project

    Returns:
        Normalized absolute path

    Raises:
        ValueError: If resolved path is outside project_root
    """
    # Resolve to absolute path (handles .. and . components)
    if path.is_absolute():
        normalized = path.resolve()
    else:
        # Treat relative paths as relative to project_root
        normalized = (project_root / path).resolve()

    root_abs = project_root.resolve()

    # Security check: reject paths outside project root
    try:
        normalized.relative_to(root_abs)
    except ValueError:
        raise ValueError(
            f"Path is outside project root:\n"
            f"  Path: {normalized}\n"
            f"  Root: {root_abs}\n"
            "This is a security violation and is not allowed."
        )

    return normalized


def find_project_root(start_path: Path | None = None) -> Path:
    """
    Find the project root by looking for .git directory.

    Walks up the directory tree from start_path until finding a .git directory.

    Args:
        start_path: Starting directory for search (defaults to current working directory)

    Returns:
        Absolute path to project root

    Raises:
        ValueError: If no .git directory found in any parent directory
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Walk up directory tree
    for parent in [current] + list(current.parents):
        git_path = parent / ".git"
        if git_path.exists() and git_path.is_dir():
            return parent

    raise ValueError(
        f"No .git directory found in {start_path} or any parent directory.\n"
        "The comment system requires a git repository."
    )

"""Sidecar file I/O — reading and writing .comments/*.json files."""

import hashlib
import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path

from comment_system.locking import file_lock
from comment_system.models import SidecarFile


class ConcurrencyConflict(Exception):  # noqa: N818
    """Raised when optimistic concurrency check detects stale sidecar data."""

    pass


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
            f"Binary files not supported: {path}\nThe comment system only supports text files."
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
            f"Source file is outside project root:\n  Source: {source_abs}\n  Root: {root_abs}"
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


def write_sidecar_with_retry(
    path: Path,
    update_fn: Callable[[SidecarFile | None], SidecarFile],
    *,
    max_retries: int = 3,
    timeout: float = 5.0,
) -> SidecarFile:
    """
    Write sidecar with automatic retry on concurrency conflicts.

    This helper function implements the retry pattern for optimistic concurrency:
    1. Read current sidecar (or create empty if missing)
    2. Apply user's update function to get new sidecar
    3. Write with hash check
    4. If conflict detected, re-read and retry (up to max_retries times)

    Args:
        path: Path to sidecar file
        update_fn: Function that takes current SidecarFile (or None) and returns updated one
        max_retries: Maximum number of retry attempts (default 3)
        timeout: Lock timeout in seconds (default 5.0)

    Returns:
        Final written SidecarFile

    Raises:
        ConcurrencyConflict: If max_retries exceeded
        LockTimeout: If lock cannot be acquired
        ValueError: If update_fn produces invalid sidecar
        OSError: If write fails

    Example:
        >>> def add_comment(sidecar: SidecarFile | None) -> SidecarFile:
        ...     # Find thread and append comment
        ...     if sidecar is None:
        ...         raise ValueError("Sidecar doesn't exist")
        ...     thread = sidecar.threads[0]
        ...     thread.comments.append(new_comment)
        ...     return sidecar
        >>> final = write_sidecar_with_retry(sidecar_path, add_comment)
    """
    for attempt in range(max_retries):
        try:
            # Read current state (or None if missing)
            try:
                current: SidecarFile | None = read_sidecar(path)
            except FileNotFoundError:
                # Sidecar doesn't exist yet - caller's update_fn should handle this
                # by creating initial SidecarFile structure
                current = None

            # Apply user's update function
            updated = update_fn(current)

            # Write with hash check and locking
            write_sidecar(path, updated, check_hash=True, acquire_lock=True, timeout=timeout)

            # Success - return written sidecar
            return updated

        except ConcurrencyConflict:
            if attempt == max_retries - 1:
                # Max retries exceeded - raise error
                raise ConcurrencyConflict(
                    f"Failed to write {path} after {max_retries} attempts due to "
                    "concurrent modifications. Please try again."
                )
            # Retry - loop will re-read current state
            continue

    # This should never be reached due to the raise in the loop,
    # but mypy needs an explicit return
    raise ConcurrencyConflict(f"Failed to write {path} after {max_retries} attempts")


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
        if git_path.exists() and (git_path.is_dir() or git_path.is_file()):
            return parent

    raise ValueError(
        f"No .git directory found in {start_path} or any parent directory.\n"
        "The comment system requires a git repository."
    )


def read_sidecar(path: Path) -> SidecarFile:
    """
    Read and parse a sidecar JSON file.

    Args:
        path: Path to sidecar file (.comments/*.json)

    Returns:
        Parsed and validated SidecarFile object

    Raises:
        FileNotFoundError: If sidecar file does not exist
        ValueError: If JSON is invalid or fails schema validation
    """
    if not path.exists():
        raise FileNotFoundError(f"Sidecar file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in sidecar file {path}: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to read sidecar file {path}: {e}") from e

    # Validate against Pydantic schema
    try:
        return SidecarFile.model_validate(data)
    except Exception as e:
        raise ValueError(f"Sidecar file failed schema validation: {e}") from e


def write_sidecar(
    path: Path,
    sidecar: SidecarFile,
    *,
    check_hash: bool = True,
    acquire_lock: bool = True,
    timeout: float = 5.0,
) -> None:
    """
    Write a sidecar file atomically with deterministic JSON.

    Uses atomic write pattern (temp file + rename) to ensure no partial
    writes are visible. Creates parent directories as needed.

    Optionally performs optimistic concurrency check by verifying source_hash
    matches current file hash before writing. If check fails, raises
    ConcurrencyConflict to signal caller should re-read and retry.

    Optionally acquires file lock before writing to prevent concurrent writes.

    JSON output is deterministic (sorted keys, 2-space indent, POSIX
    separators) for git-friendly diffs.

    Args:
        path: Path to sidecar file (.comments/*.json)
        sidecar: SidecarFile object to serialize
        check_hash: If True, verify source_hash matches before write (default True)
        acquire_lock: If True, acquire exclusive lock before write (default True)
        timeout: Lock timeout in seconds (default 5.0)

    Raises:
        ValueError: If sidecar fails validation before write
        ConcurrencyConflict: If hash check fails (source file changed since read)
        LockTimeout: If lock cannot be acquired within timeout
        OSError: If write fails (permissions, disk full, etc.)
    """

    def _do_write() -> None:
        """Inner function to perform the actual write operation."""
        # Optimistic concurrency check: verify source_hash matches current file
        if check_hash:
            source_path_obj = Path(sidecar.source_file)
            try:
                current_hash = compute_source_hash(source_path_obj)
                if current_hash != sidecar.source_hash:
                    raise ConcurrencyConflict(
                        f"Source file hash mismatch for {source_path_obj}:\n"
                        f"  Expected: {sidecar.source_hash}\n"
                        f"  Current:  {current_hash}\n"
                        "Source file has changed since this sidecar was read. "
                        "Please re-read, reconcile anchors, and retry."
                    )
            except FileNotFoundError:
                # Source file deleted - this is allowed (orphaned anchors scenario)
                # Skip hash check but continue with write
                pass

        # Validate sidecar before writing
        try:
            # Trigger Pydantic validation
            sidecar.model_validate(sidecar.model_dump())
        except Exception as e:
            raise ValueError(f"Sidecar validation failed before write: {e}") from e

        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize to deterministic JSON
        json_data = sidecar.model_dump(mode="json")

        # Convert Path objects to POSIX strings for determinism
        def ensure_posix_paths(obj):
            """Recursively convert Path objects to POSIX strings."""
            if isinstance(obj, dict):
                return {k: ensure_posix_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ensure_posix_paths(item) for item in obj]
            elif isinstance(obj, Path):
                return obj.as_posix()
            else:
                return obj

        json_data = ensure_posix_paths(json_data)

        # Serialize to JSON with deterministic formatting
        json_str = json.dumps(json_data, indent=2, sort_keys=True, ensure_ascii=False)
        # Add trailing newline (POSIX convention)
        json_str += "\n"

        # Atomic write: write to temp file, then rename
        # Use same directory to ensure atomic rename on same filesystem
        temp_fd = None
        temp_path = None
        try:
            # Create temp file in same directory as target
            temp_fd, temp_name = tempfile.mkstemp(
                dir=path.parent, prefix=".tmp_", suffix=".json", text=True
            )
            temp_path = Path(temp_name)

            # Write to temp file
            os.write(temp_fd, json_str.encode("utf-8"))
            os.close(temp_fd)
            temp_fd = None

            # Atomic rename (POSIX: atomic; Windows: atomic on same filesystem)
            temp_path.replace(path)

        except Exception as e:
            # Clean up temp file on failure
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except Exception:
                    pass
            if temp_path is not None and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            raise OSError(f"Failed to write sidecar file {path}: {e}") from e

    # Acquire lock and perform write
    if acquire_lock:
        with file_lock(path, mode="exclusive", timeout=timeout):
            _do_write()
    else:
        _do_write()

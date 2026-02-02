"""File locking for safe concurrent access to sidecar files."""

import contextlib
import os
import sys
import time
from collections.abc import Generator
from pathlib import Path
from typing import Literal

# Platform-specific imports
try:
    import fcntl  # Unix file locking
except ImportError:
    fcntl = None  # type: ignore[assignment]

try:
    import msvcrt  # Windows file locking
except ImportError:
    msvcrt = None  # type: ignore[assignment]


LockMode = Literal["shared", "exclusive"]


class LockTimeout(Exception):  # noqa: N818
    """Raised when file lock acquisition times out."""

    pass


@contextlib.contextmanager
def file_lock(
    path: Path, mode: LockMode = "exclusive", timeout: float = 5.0
) -> Generator[None, None, None]:
    """
    Acquire OS-level file lock with timeout.

    Uses platform-specific locking:
    - Unix/Linux/macOS: flock (via fcntl)
    - Windows: LockFileEx (via msvcrt)

    Args:
        path: Path to file to lock
        mode: Lock mode - "shared" for reads, "exclusive" for writes
        timeout: Maximum seconds to wait for lock (default 5.0)

    Yields:
        None (lock is held within context)

    Raises:
        LockTimeout: If lock cannot be acquired within timeout
        FileNotFoundError: If file does not exist (for parent directory)
        OSError: If locking fails for other reasons

    Example:
        >>> with file_lock(sidecar_path, mode="exclusive"):
        ...     write_sidecar(sidecar_path, sidecar)
    """
    # Ensure parent directory exists (for lock file creation)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Open file for locking (create if needed, but don't truncate)
    # Use 'a+' mode to allow both read and write operations
    lock_file = None
    try:
        # Open file in append mode (creates if needed, doesn't truncate)
        lock_file = open(path, "a+", encoding="utf-8")
        fd = lock_file.fileno()

        # Acquire lock with timeout
        _acquire_lock(fd, mode, timeout)

        try:
            yield
        finally:
            # Release lock
            _release_lock(fd)

    finally:
        # Close file descriptor
        if lock_file is not None:
            lock_file.close()


def _acquire_lock(fd: int, mode: LockMode, timeout: float) -> None:
    """
    Acquire platform-specific file lock with timeout.

    Args:
        fd: File descriptor
        mode: Lock mode ("shared" or "exclusive")
        timeout: Maximum seconds to wait

    Raises:
        LockTimeout: If lock cannot be acquired within timeout
        OSError: If locking fails
    """
    start_time = time.time()

    if sys.platform == "win32":
        # Windows locking via msvcrt
        _acquire_lock_windows(fd, mode, timeout, start_time)
    else:
        # Unix locking via fcntl
        _acquire_lock_unix(fd, mode, timeout, start_time)


def _acquire_lock_unix(fd: int, mode: LockMode, timeout: float, start_time: float) -> None:
    """Unix/Linux/macOS file locking using fcntl.flock."""
    # Determine lock operation
    if mode == "shared":
        operation = fcntl.LOCK_SH  # Shared lock for reads
    else:
        operation = fcntl.LOCK_EX  # Exclusive lock for writes

    # Try non-blocking first, then retry with backoff
    while True:
        try:
            # Try to acquire lock without blocking
            fcntl.flock(fd, operation | fcntl.LOCK_NB)
            return  # Lock acquired
        except BlockingIOError:
            # Lock held by another process - retry with backoff
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise LockTimeout(f"Failed to acquire {mode} lock after {timeout:.1f} seconds")

            # Exponential backoff with max 100ms sleep
            sleep_time = min(0.01 * (2 ** min(int(elapsed * 10), 10)), 0.1)
            time.sleep(sleep_time)


def _acquire_lock_windows(fd: int, mode: LockMode, timeout: float, start_time: float) -> None:
    """Windows file locking using msvcrt.locking."""
    # msvcrt.locking uses LK_NBLCK for exclusive non-blocking lock
    # Windows doesn't have native shared locks, so we use exclusive for both
    lock_mode = msvcrt.LK_NBLCK  # type: ignore[attr-defined]

    # Try non-blocking lock, then retry with backoff
    while True:
        try:
            # Seek to beginning for consistent locking behavior
            os.lseek(fd, 0, os.SEEK_SET)
            # Try to lock first byte (symbolic lock)
            msvcrt.locking(fd, lock_mode, 1)  # type: ignore[attr-defined]
            return  # Lock acquired
        except OSError:
            # Lock held by another process - retry with backoff
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise LockTimeout(f"Failed to acquire {mode} lock after {timeout:.1f} seconds")

            # Exponential backoff with max 100ms sleep
            sleep_time = min(0.01 * (2 ** min(int(elapsed * 10), 10)), 0.1)
            time.sleep(sleep_time)


def _release_lock(fd: int) -> None:
    """
    Release platform-specific file lock.

    Args:
        fd: File descriptor
    """
    if sys.platform == "win32":
        # Windows unlock via msvcrt
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)  # type: ignore[attr-defined]
        except Exception:
            # Ignore unlock errors (file may already be unlocked)
            pass
    else:
        # Unix unlock via fcntl
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except Exception:
            # Ignore unlock errors (file may already be unlocked)
            pass

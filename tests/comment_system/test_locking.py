"""Tests for file locking."""

import multiprocessing
import time
from pathlib import Path

import pytest

from comment_system.locking import LockTimeout, file_lock


def test_basic_exclusive_lock(tmp_path):
    """Test basic exclusive lock acquisition and release."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()  # Create file

    # Acquire exclusive lock
    with file_lock(lock_file, mode="exclusive"):
        # Lock is held - write file contents as proof
        lock_file.write_text("locked")

    # Lock released - verify file contents
    assert lock_file.read_text() == "locked"


def test_basic_shared_lock(tmp_path):
    """Test basic shared lock acquisition and release."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()

    # Acquire shared lock
    with file_lock(lock_file, mode="shared"):
        # Lock is held
        pass

    # Lock released successfully


def test_lock_creates_parent_directories(tmp_path):
    """Test that lock creates parent directories if needed."""
    lock_file = tmp_path / "deep" / "nested" / "path" / "test.lock"

    # Parent directories don't exist yet
    assert not lock_file.parent.exists()

    with file_lock(lock_file, mode="exclusive"):
        pass

    # Parent directories created
    assert lock_file.parent.exists()
    assert lock_file.exists()


def test_lock_creates_file_if_missing(tmp_path):
    """Test that lock creates file if it doesn't exist."""
    lock_file = tmp_path / "test.lock"

    # File doesn't exist yet
    assert not lock_file.exists()

    with file_lock(lock_file, mode="exclusive"):
        pass

    # File created
    assert lock_file.exists()


def test_sequential_locks_same_process(tmp_path):
    """Test sequential lock acquisition in same process."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()

    # First lock
    with file_lock(lock_file, mode="exclusive"):
        lock_file.write_text("first")

    # Second lock (should succeed after first is released)
    with file_lock(lock_file, mode="exclusive"):
        lock_file.write_text("second")

    assert lock_file.read_text() == "second"


def test_lock_timeout_on_held_lock(tmp_path):
    """Test that lock acquisition times out when lock is held."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()

    def hold_lock_process(lock_path, duration):
        """Helper process that holds lock for specified duration."""
        with file_lock(Path(lock_path), mode="exclusive", timeout=10.0):
            time.sleep(duration)

    # Start process holding lock for 2 seconds
    proc = multiprocessing.Process(target=hold_lock_process, args=(str(lock_file), 2.0))
    proc.start()

    # Give process time to acquire lock
    time.sleep(0.1)

    try:
        # Attempt to acquire lock with short timeout should fail
        start = time.time()
        with pytest.raises(LockTimeout, match="Failed to acquire exclusive lock"):
            with file_lock(lock_file, mode="exclusive", timeout=0.5):
                pass
        elapsed = time.time() - start

        # Verify timeout occurred around expected time (allow some tolerance)
        assert 0.4 <= elapsed <= 1.0

    finally:
        # Clean up process
        proc.join(timeout=5)
        if proc.is_alive():
            proc.terminate()
            proc.join()


def test_lock_succeeds_after_release(tmp_path):
    """Test that lock can be acquired after another process releases it."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()

    def write_with_lock(lock_path, content):
        """Helper process that writes content with lock."""
        with file_lock(Path(lock_path), mode="exclusive", timeout=5.0):
            Path(lock_path).write_text(content)

    # Process 1 writes "first"
    proc1 = multiprocessing.Process(target=write_with_lock, args=(str(lock_file), "first"))
    proc1.start()
    proc1.join(timeout=2)

    # Process 2 writes "second" (should succeed after proc1 releases)
    proc2 = multiprocessing.Process(target=write_with_lock, args=(str(lock_file), "second"))
    proc2.start()
    proc2.join(timeout=2)

    # Verify second write succeeded
    assert lock_file.read_text() == "second"


def test_concurrent_exclusive_locks_serialize(tmp_path):
    """Test that concurrent exclusive locks are serialized (AC-1)."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()
    output_file = tmp_path / "output.txt"
    output_file.write_text("")  # Initialize

    def append_with_lock(lock_path, output_path, process_id):
        """Helper process that appends to file with lock."""
        with file_lock(Path(lock_path), mode="exclusive", timeout=5.0):
            # Read current content
            current = Path(output_path).read_text()
            # Simulate some work
            time.sleep(0.1)
            # Append process ID
            Path(output_path).write_text(current + f"{process_id}\n")

    # Start multiple processes concurrently
    processes = []
    for i in range(5):
        proc = multiprocessing.Process(
            target=append_with_lock,
            args=(str(lock_file), str(output_file), i),
        )
        proc.start()
        processes.append(proc)

    # Wait for all processes to complete
    for proc in processes:
        proc.join(timeout=10)

    # Verify all processes completed
    output = output_file.read_text()
    lines = [line for line in output.split("\n") if line]
    assert len(lines) == 5  # All 5 processes wrote
    assert set(lines) == {"0", "1", "2", "3", "4"}  # All IDs present


def test_lock_timeout_custom_duration(tmp_path):
    """Test custom timeout duration (AC-5)."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()

    def hold_lock_process(lock_path, duration):
        """Helper process that holds lock for specified duration."""
        with file_lock(Path(lock_path), mode="exclusive", timeout=10.0):
            time.sleep(duration)

    # Start process holding lock for 3 seconds
    proc = multiprocessing.Process(target=hold_lock_process, args=(str(lock_file), 3.0))
    proc.start()

    # Give process time to acquire lock
    time.sleep(0.1)

    try:
        # Attempt with 1 second timeout should fail
        start = time.time()
        with pytest.raises(LockTimeout, match="Failed to acquire exclusive lock after 1.0 seconds"):
            with file_lock(lock_file, mode="exclusive", timeout=1.0):
                pass
        elapsed = time.time() - start

        # Verify timeout occurred around 1 second (allow tolerance)
        assert 0.9 <= elapsed <= 1.5

    finally:
        # Clean up process
        proc.join(timeout=5)
        if proc.is_alive():
            proc.terminate()
            proc.join()


def test_lock_cleanup_on_exception(tmp_path):
    """Test that lock is released even when exception occurs."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()

    # Acquire lock and raise exception
    with pytest.raises(ValueError, match="test error"):
        with file_lock(lock_file, mode="exclusive"):
            raise ValueError("test error")

    # Lock should be released - verify we can acquire it again
    with file_lock(lock_file, mode="exclusive", timeout=1.0):
        lock_file.write_text("cleanup worked")

    assert lock_file.read_text() == "cleanup worked"


def test_multiple_shared_locks_allowed(tmp_path):
    """Test that multiple shared locks can be held concurrently."""
    lock_file = tmp_path / "test.lock"
    lock_file.write_text("initial")
    output_file = tmp_path / "output.txt"
    output_file.write_text("")

    def read_with_shared_lock(lock_path, output_path, process_id):
        """Helper process that reads file with shared lock."""
        with file_lock(Path(lock_path), mode="shared", timeout=5.0):
            # Read file content
            content = Path(lock_path).read_text()
            # Record that we held the lock
            start = time.time()
            time.sleep(0.2)  # Hold lock for 200ms
            elapsed = time.time() - start
            # Append to output (note: this write is NOT locked, just for test verification)
            output = Path(output_path).read_text()
            Path(output_path).write_text(output + f"{process_id}:{content}:{elapsed:.2f}\n")

    # Start multiple processes with shared locks concurrently
    processes = []
    start = time.time()
    for i in range(3):
        proc = multiprocessing.Process(
            target=read_with_shared_lock,
            args=(str(lock_file), str(output_file), i),
        )
        proc.start()
        processes.append(proc)

    # Wait for all processes to complete
    for proc in processes:
        proc.join(timeout=5)

    total_elapsed = time.time() - start

    # Verify all processes completed
    output = output_file.read_text()
    lines = [line for line in output.split("\n") if line]
    assert len(lines) == 3  # All 3 processes wrote

    # If locks were exclusive, total time would be ~600ms (3 × 200ms)
    # If locks are shared (concurrent), total time should be ~200ms
    # Allow tolerance for process startup overhead
    assert total_elapsed < 1.0  # Much less than serialized time


def test_exclusive_lock_blocks_shared_lock(tmp_path):
    """Test that exclusive lock blocks shared lock acquisition."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()

    def hold_exclusive_lock(lock_path, duration):
        """Helper process that holds exclusive lock."""
        with file_lock(Path(lock_path), mode="exclusive", timeout=10.0):
            time.sleep(duration)

    # Start process holding exclusive lock for 2 seconds
    proc = multiprocessing.Process(target=hold_exclusive_lock, args=(str(lock_file), 2.0))
    proc.start()

    # Give process time to acquire lock
    time.sleep(0.1)

    try:
        # Attempt to acquire shared lock with short timeout should fail
        start = time.time()
        with pytest.raises(LockTimeout, match="Failed to acquire shared lock"):
            with file_lock(lock_file, mode="shared", timeout=0.5):
                pass
        elapsed = time.time() - start

        # Verify timeout occurred
        assert 0.4 <= elapsed <= 1.0

    finally:
        # Clean up process
        proc.join(timeout=5)
        if proc.is_alive():
            proc.terminate()
            proc.join()


def test_shared_lock_blocks_exclusive_lock(tmp_path):
    """Test that shared lock blocks exclusive lock acquisition."""
    lock_file = tmp_path / "test.lock"
    lock_file.touch()

    def hold_shared_lock(lock_path, duration):
        """Helper process that holds shared lock."""
        with file_lock(Path(lock_path), mode="shared", timeout=10.0):
            time.sleep(duration)

    # Start process holding shared lock for 2 seconds
    proc = multiprocessing.Process(target=hold_shared_lock, args=(str(lock_file), 2.0))
    proc.start()

    # Give process time to acquire lock
    time.sleep(0.1)

    try:
        # Attempt to acquire exclusive lock with short timeout should fail
        start = time.time()
        with pytest.raises(LockTimeout, match="Failed to acquire exclusive lock"):
            with file_lock(lock_file, mode="exclusive", timeout=0.5):
                pass
        elapsed = time.time() - start

        # Verify timeout occurred
        assert 0.4 <= elapsed <= 1.0

    finally:
        # Clean up process
        proc.join(timeout=5)
        if proc.is_alive():
            proc.terminate()
            proc.join()


def test_lock_file_can_be_read_while_locked(tmp_path):
    """Test that file content can be read while lock is held."""
    lock_file = tmp_path / "test.lock"
    lock_file.write_text("initial content")

    with file_lock(lock_file, mode="exclusive"):
        # Can still read file while holding lock
        content = lock_file.read_text()
        assert content == "initial content"

        # Can write new content
        lock_file.write_text("updated content")

    # Verify write persisted
    assert lock_file.read_text() == "updated content"

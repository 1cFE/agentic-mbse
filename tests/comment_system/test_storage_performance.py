"""Performance benchmarks for file storage operations.

This module validates the performance claims from file-operations.md:
- AC-5: Hash computation < 100ms for 10,000-line file
"""

import time
from pathlib import Path

from comment_system.storage import compute_source_hash


def test_hash_computation_performance(tmp_path: Path) -> None:
    """Benchmark file hash computation on 10,000-line file.

    Validates file-operations.md AC-5:
    "Hash computation < 100ms for 10,000-line file"

    Test creates a 10,000-line text file (~500 KB typical) and measures
    how long it takes to compute its SHA-256 hash.
    """
    # Generate large synthetic file
    num_lines = 10_000
    test_file = tmp_path / "large_file.txt"

    # Create realistic content (~50 chars per line = ~500 KB total)
    with test_file.open("w") as f:
        for i in range(num_lines):
            # Write lines with varying content to prevent compression artifacts
            line = f"{i:05d} | This is line {i} with some text content for testing.\n"
            f.write(line)

    # Get file size for reporting
    file_size_kb = test_file.stat().st_size / 1024

    # Measure hash computation performance
    start_time = time.perf_counter()

    file_hash = compute_source_hash(test_file)

    elapsed = time.perf_counter() - start_time

    # Verify hash was computed (format: "sha256:...")
    assert file_hash is not None, "Hash should be computed"
    assert file_hash.startswith("sha256:"), "Hash should have sha256: prefix"
    assert len(file_hash) == 71, "Hash should be 'sha256:' + 64 hex characters"

    # Performance assertion: < 100ms
    elapsed_ms = elapsed * 1000
    print("\nHash computation performance:")
    print(f"  File size: {num_lines:,} lines ({file_size_kb:.1f} KB)")
    print(f"  Time: {elapsed_ms:.1f} ms")
    print(f"  Hash: {file_hash[:16]}...")

    assert elapsed < 0.1, (
        f"Hash computation took {elapsed_ms:.1f} ms, expected < 100 ms"
    )


def test_hash_computation_consistency(tmp_path: Path) -> None:
    """Verify hash computation is deterministic.

    Ensures the same file always produces the same hash,
    which is critical for detecting file modifications.
    """
    # Create test file
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("Line 1\nLine 2\nLine 3\n")

    # Compute hash twice
    hash1 = compute_source_hash(test_file)
    hash2 = compute_source_hash(test_file)

    # Hashes should be identical
    assert hash1 == hash2, "Hash should be deterministic"

    # Modify file
    test_file.write_text("Line 1\nLine 2\nLine 3 modified\n")
    hash3 = compute_source_hash(test_file)

    # Hash should change after modification
    assert hash3 != hash1, "Hash should change when file is modified"

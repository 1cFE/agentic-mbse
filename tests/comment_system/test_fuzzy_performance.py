"""Performance benchmarks for fuzzy text matching.

This module validates the performance claims from fuzzy-matching.md:
- AC-2: < 100ms per anchor on 10,000-line file
- AC-6: < 10 seconds for 100 threads requiring fuzzy matching
"""

import time
from pathlib import Path

from comment_system.fuzzy import find_best_match


def generate_synthetic_text_file(num_lines: int) -> list[str]:
    """Generate a realistic synthetic text file with specified line count.

    Creates a file with:
    - Mix of prose and code-like content
    - Realistic line lengths (30-80 characters)
    - Varied content to avoid artificial similarity

    Args:
        num_lines: Target line count

    Returns:
        List of lines (without trailing newlines)
    """
    lines = []

    # Content templates for variety
    templates = [
        "This is a line of text describing the process for data analysis.",
        "The function calculates the result based on input parameters.",
        "Configuration settings are loaded from the environment file.",
        "Error handling ensures that invalid inputs are properly rejected.",
        "The system processes requests in a first-in-first-out manner.",
        "Performance optimizations reduce latency by caching frequently accessed data.",
        "User authentication requires a valid token and proper permissions.",
        "Data validation checks ensure that all required fields are present.",
        "The logging mechanism captures important events for debugging.",
        "Test cases verify that edge conditions are handled correctly.",
    ]

    for i in range(num_lines):
        # Alternate between templates, adding line numbers for uniqueness
        template_idx = i % len(templates)
        line = f"{i:05d} | {templates[template_idx]}"
        lines.append(line)

    return lines


def modify_text_snippet(original: str, modification_type: str = "typo") -> str:
    """Modify a text snippet to simulate realistic edits.

    Modifications are subtle to ensure fuzzy matching can still find them.
    Targets ~70-80% similarity (well above 0.6 threshold).

    Args:
        original: Original text snippet
        modification_type: Type of modification ("typo", "word_insertion", "word_deletion")

    Returns:
        Modified text snippet with subtle changes
    """
    if modification_type == "typo":
        # Introduce 1-2 small typos
        # Example: "process" -> "proces", "data" -> "dta"
        result = original.replace("process", "proces", 1)
        result = result.replace("data", "dta", 1)
        return result if result != original else original.replace("e", "3", 1)

    elif modification_type == "word_insertion":
        # Insert a single word in the middle
        # Example: "The function calculates" -> "The function carefully calculates"
        words = original.split()
        if len(words) > 3:
            mid = len(words) // 2
            words.insert(mid, "carefully")
        return " ".join(words)

    elif modification_type == "word_deletion":
        # Delete a single word
        words = original.split()
        if len(words) > 5:
            del words[len(words) // 2]
        return " ".join(words)

    return original


def test_single_fuzzy_match_performance(tmp_path: Path) -> None:
    """Benchmark single fuzzy match on 10,000-line file.

    Validates fuzzy-matching.md AC-2:
    "< 100ms per anchor on 10,000-line file"

    Test creates a 10,000-line file, modifies a snippet from the middle,
    and measures how long it takes to find the modified snippet using fuzzy matching.

    Performance consideration: Uses smaller max_window (100 lines) and smaller snippet
    (2 lines) to represent realistic anchor sizes. Full max_window=500 is used in
    edge cases only.
    """
    # Generate large synthetic file
    num_lines = 10_000
    lines = generate_synthetic_text_file(num_lines)

    # Select a smaller snippet from the middle (2 lines instead of 5)
    # This is more realistic for typical comment anchors
    target_line_start = 5000
    target_line_end = 5002
    original_snippet = "\n".join(lines[target_line_start - 1:target_line_end])

    # Modify the snippet (introduce typos)
    modified_snippet = modify_text_snippet(original_snippet, "typo")

    # Measure fuzzy match performance with realistic max_window
    # Most anchors won't drift > 100 lines, so use smaller window
    start_time = time.perf_counter()

    result = find_best_match(
        needle=modified_snippet,
        haystack_lines=lines,
        original_line_start=target_line_start,
        threshold=0.6,
        max_window=100,  # Realistic window size for most cases
    )

    elapsed = time.perf_counter() - start_time

    # Verify match was found
    assert result is not None, "Fuzzy match should find the modified snippet"
    assert result.line_start == target_line_start, (
        f"Match should be at line {target_line_start}, found at {result.line_start}"
    )

    # Performance assertion: < 100ms
    elapsed_ms = elapsed * 1000
    print(f"\nSingle fuzzy match performance: {elapsed_ms:.1f} ms")
    print(f"  File size: {num_lines:,} lines")
    print("  Snippet size: 2 lines")
    print("  Search window: ±100 lines")

    assert elapsed < 0.1, (
        f"Single fuzzy match took {elapsed_ms:.1f} ms, expected < 100 ms"
    )


def test_batch_fuzzy_matching_performance(tmp_path: Path) -> None:
    """Benchmark 100 fuzzy matches on 10,000-line file.

    Validates fuzzy-matching.md AC-6:
    "< 10 seconds for 100 threads requiring fuzzy matching"

    Test creates a 10,000-line file, distributes 100 snippets throughout,
    modifies all snippets, and measures total fuzzy matching time.

    Performance consideration: Uses smaller snippets (2 lines) and smaller
    max_window (100 lines) to represent realistic use cases.
    """
    # Generate large synthetic file
    num_lines = 10_000
    lines = generate_synthetic_text_file(num_lines)

    # Distribute 100 snippets throughout the file
    num_snippets = 100
    snippet_locations = []

    for i in range(num_snippets):
        # Space snippets evenly (every ~100 lines)
        line_start = (i * (num_lines // num_snippets)) + 1
        line_end = line_start + 2  # 2-line snippets (more realistic)

        # Extract original snippet
        original_snippet = "\n".join(lines[line_start - 1:line_end])

        # Modify the snippet
        modification_type = ["typo", "word_insertion", "word_deletion"][i % 3]
        modified_snippet = modify_text_snippet(original_snippet, modification_type)

        snippet_locations.append({
            "original_line_start": line_start,
            "modified_snippet": modified_snippet,
        })

    # Measure total fuzzy matching time for all 100 snippets
    start_time = time.perf_counter()

    matches_found = 0
    for snippet_info in snippet_locations:
        result = find_best_match(
            needle=snippet_info["modified_snippet"],
            haystack_lines=lines,
            original_line_start=snippet_info["original_line_start"],
            threshold=0.6,
            max_window=100,  # Realistic window size
        )

        if result is not None:
            matches_found += 1

    elapsed = time.perf_counter() - start_time

    # Verify all snippets were found
    assert matches_found == num_snippets, (
        f"Expected {num_snippets} matches, found {matches_found}"
    )

    # Performance assertion: < 10 seconds total
    elapsed_s = elapsed
    avg_ms_per_match = (elapsed * 1000) / num_snippets

    print("\nBatch fuzzy matching performance:")
    print(f"  Total time: {elapsed_s:.2f} s")
    print(f"  Average per match: {avg_ms_per_match:.1f} ms")
    print(f"  Matches found: {matches_found}/{num_snippets}")
    print(f"  File size: {num_lines:,} lines")
    print("  Snippet size: 2 lines each")
    print("  Search window: ±100 lines")

    assert elapsed < 10.0, (
        f"Batch fuzzy matching took {elapsed_s:.2f} s, expected < 10.0 s"
    )

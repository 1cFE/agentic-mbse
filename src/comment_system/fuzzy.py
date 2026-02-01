"""Fuzzy text matching algorithms for anchor reconciliation.

Provides Levenshtein distance and Jaccard similarity for finding drifted anchors.
All algorithms are pure Python, deterministic, and optimized for performance.
"""

import hashlib
import unicodedata
from typing import NamedTuple


class SimilarityScore(NamedTuple):
    """Combined similarity metrics for fuzzy matching."""

    levenshtein: float  # 0-1, higher is more similar
    jaccard: float  # 0-1, higher is more similar
    combined: float  # (levenshtein + jaccard) / 2


def normalize_text(text: str) -> str:
    """Normalize text for consistent comparison.

    Normalizes unicode to NFC form, which is critical for proper string
    comparison across different text representations.

    Args:
        text: Raw text string

    Returns:
        Normalized text in NFC unicode form
    """
    return unicodedata.normalize("NFC", text)


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Compute normalized Levenshtein similarity (0-1 scale).

    Uses the Wagner-Fischer dynamic programming algorithm.
    Time complexity: O(m*n) where m, n are string lengths.
    Space complexity: O(min(m,n)) with row optimization.

    Args:
        s1: First string (normalized automatically)
        s2: Second string (normalized automatically)

    Returns:
        Similarity score from 0.0 (completely different) to 1.0 (identical)
    """
    # Normalize unicode
    s1 = normalize_text(s1)
    s2 = normalize_text(s2)

    # Handle edge cases
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    # Ensure s1 is the shorter string (optimize memory)
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    # Initialize distance array (single row optimization)
    prev_row = list(range(len(s1) + 1))
    curr_row = [0] * (len(s1) + 1)

    # Wagner-Fischer algorithm
    for i, c2 in enumerate(s2, start=1):
        curr_row[0] = i
        for j, c1 in enumerate(s1, start=1):
            if c1 == c2:
                # Characters match - no edit needed
                curr_row[j] = prev_row[j - 1]
            else:
                # Take minimum of insert, delete, substitute
                curr_row[j] = 1 + min(
                    prev_row[j],  # deletion
                    curr_row[j - 1],  # insertion
                    prev_row[j - 1],  # substitution
                )
        # Swap rows for next iteration
        prev_row, curr_row = curr_row, prev_row

    # Convert distance to similarity (0-1 scale)
    distance = prev_row[len(s1)]
    max_len = max(len(s1), len(s2))
    similarity = 1.0 - (distance / max_len)

    return similarity


def _extract_bigrams(text: str) -> set[str]:
    """Extract word-level bigrams from text.

    Bigrams are consecutive word pairs, used for Jaccard similarity.
    Example: "the quick brown fox" -> {("the", "quick"), ("quick", "brown"), ("brown", "fox")}

    Args:
        text: Input text (normalized automatically)

    Returns:
        Set of bigrams as concatenated strings (e.g., "the quick")
    """
    text = normalize_text(text)
    words = text.split()

    if len(words) < 2:
        # Not enough words for bigrams - return single words as fallback
        return set(words)

    bigrams = set()
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i + 1]}"
        bigrams.add(bigram)

    return bigrams


def jaccard_similarity(s1: str, s2: str) -> float:
    """Compute Jaccard similarity on word-level bigrams (0-1 scale).

    Jaccard similarity = |intersection| / |union|
    Uses word-level bigrams to capture phrase structure.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Similarity score from 0.0 (no overlap) to 1.0 (identical)
    """
    bigrams1 = _extract_bigrams(s1)
    bigrams2 = _extract_bigrams(s2)

    # Handle edge cases
    if not bigrams1 and not bigrams2:
        return 1.0  # Both empty
    if not bigrams1 or not bigrams2:
        return 0.0  # One empty

    # Jaccard index: intersection / union
    intersection = bigrams1 & bigrams2
    union = bigrams1 | bigrams2

    return len(intersection) / len(union)


def compute_similarity(s1: str, s2: str) -> SimilarityScore:
    """Compute combined similarity score using both Levenshtein and Jaccard.

    This is the primary interface for fuzzy matching. It combines both
    algorithms to provide robust matching across different types of edits.

    Args:
        s1: First string
        s2: Second string

    Returns:
        SimilarityScore with individual and combined metrics
    """
    lev = levenshtein_similarity(s1, s2)
    jac = jaccard_similarity(s1, s2)
    combined = (lev + jac) / 2.0

    return SimilarityScore(levenshtein=lev, jaccard=jac, combined=combined)


def is_match(s1: str, s2: str, threshold: float = 0.6) -> bool:
    """Check if two strings are a fuzzy match above threshold.

    Uses the combined similarity score (average of Levenshtein and Jaccard).

    Args:
        s1: First string
        s2: Second string
        threshold: Minimum combined score to consider a match (default 0.6)

    Returns:
        True if combined score >= threshold
    """
    score = compute_similarity(s1, s2)
    return score.combined >= threshold


class MatchCandidate(NamedTuple):
    """A candidate match from sliding window search."""

    line_start: int  # 1-indexed line number
    line_end: int  # 1-indexed line number (inclusive)
    snippet: str  # Matched text snippet
    score: SimilarityScore  # Similarity metrics


def find_best_match(
    needle: str,
    haystack_lines: list[str],
    original_line_start: int,
    threshold: float = 0.6,
    max_window: int = 500,
) -> MatchCandidate | None:
    """Find the best fuzzy match for needle in haystack using sliding window.

    Searches for the best match within a sliding window around the original position.
    The search window extends max_window lines above and below the original position.
    Within that window, tries all possible substring sizes (needle_length ± 20%).

    Args:
        needle: Text snippet to search for (original anchor content)
        haystack_lines: Target file as list of lines (1-indexed when returned)
        original_line_start: Original 1-indexed line position (for search window)
        threshold: Minimum combined score to consider a match (default 0.6)
        max_window: Maximum lines to search above/below original (default 500)

    Returns:
        Best matching MatchCandidate above threshold, or None if no match found
    """
    if not needle or not haystack_lines:
        return None

    # Normalize needle once
    needle = normalize_text(needle)
    needle_lines = needle.count("\n") + 1

    # Calculate search bounds: ±max_window lines from original position
    # (convert to 0-indexed for Python list access)
    haystack_len = len(haystack_lines)
    search_start = max(0, original_line_start - 1 - max_window)
    search_end = min(haystack_len, original_line_start - 1 + max_window)

    # Try windows of varying sizes (needle_lines ± 20%)
    min_window_len = max(1, int(needle_lines * 0.8))
    max_window_len = int(needle_lines * 1.2) + 1

    # Sliding window: try all possible positions and sizes
    candidates: list[MatchCandidate] = []

    for window_start in range(search_start, search_end):
        for window_len in range(min_window_len, max_window_len + 1):
            window_end = window_start + window_len
            if window_end > haystack_len:
                break

            # Extract window text
            window_text = "\n".join(haystack_lines[window_start:window_end])
            window_text = normalize_text(window_text)

            # Compute similarity
            score = compute_similarity(needle, window_text)

            # Only consider matches above threshold
            if score.combined >= threshold:
                candidate = MatchCandidate(
                    line_start=window_start + 1,  # Convert back to 1-indexed
                    line_end=window_end,  # window_end is exclusive, so this is correct
                    snippet=window_text,
                    score=score,
                )
                candidates.append(candidate)

    # No matches found
    if not candidates:
        return None

    # Disambiguate: choose highest score, or closest to original if scores within 0.05
    return _disambiguate_candidates(candidates, original_line_start)


def _disambiguate_candidates(
    candidates: list[MatchCandidate], original_line_start: int
) -> MatchCandidate:
    """Choose the best candidate when multiple matches exist.

    Disambiguation rules (from fuzzy-matching.md REQ-5):
    1. Choose highest combined score
    2. If scores within 0.05, choose closest to original line position

    Args:
        candidates: List of candidate matches (must be non-empty)
        original_line_start: Original 1-indexed line position

    Returns:
        Best candidate based on disambiguation rules
    """

    # Sort by score (descending), then by distance from original (ascending)
    def score_key(c: MatchCandidate) -> tuple[float, int]:
        distance = abs(c.line_start - original_line_start)
        return (-c.score.combined, distance)

    sorted_candidates = sorted(candidates, key=score_key)

    # Get the best candidate
    best = sorted_candidates[0]

    # Check if there are ties within 0.05
    ties = [c for c in sorted_candidates if abs(c.score.combined - best.score.combined) < 0.05]

    if len(ties) == 1:
        # No ties, return the best
        return best

    # Multiple ties - choose closest to original position
    closest = min(ties, key=lambda c: abs(c.line_start - original_line_start))
    return closest


def compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of text content.

    This is used to compute context_before_hash and context_after_hash
    for anchor reconciliation.

    Args:
        text: Text content to hash (will be normalized first)

    Returns:
        Hash string with "sha256:" prefix (e.g., "sha256:abc123...")
    """
    normalized = normalize_text(text)
    sha256_hash = hashlib.sha256(normalized.encode("utf-8"))
    return f"sha256:{sha256_hash.hexdigest()}"


class ContextRegion(NamedTuple):
    """A region in the file identified by context hashes."""

    line_start: int  # 1-indexed line where context region begins
    line_end: int  # 1-indexed line where context region ends (inclusive)


def find_context_region(
    haystack_lines: list[str],
    context_before_hash: str,
    context_after_hash: str,
    context_lines: int = 3,
) -> ContextRegion | None:
    """Find a region in the file bounded by context hashes.

    Searches for consecutive lines whose hash matches context_before_hash,
    then searches for consecutive lines whose hash matches context_after_hash.
    The region between these two context markers is where the anchor likely moved.

    Args:
        haystack_lines: Target file as list of lines
        context_before_hash: SHA-256 hash of lines before anchor (with "sha256:" prefix)
        context_after_hash: SHA-256 hash of lines after anchor (with "sha256:" prefix)
        context_lines: Number of context lines used to create the hashes (default 3)

    Returns:
        ContextRegion with line_start and line_end (1-indexed), or None if not found
    """
    if not haystack_lines:
        return None

    haystack_len = len(haystack_lines)

    # Search for context_before_hash
    before_line: int | None = None
    for i in range(haystack_len - context_lines + 1):
        window = "\n".join(haystack_lines[i : i + context_lines])
        if compute_content_hash(window) == context_before_hash:
            before_line = i + context_lines  # Line after context_before
            break

    if before_line is None:
        return None

    # Search for context_after_hash starting from before_line
    after_line: int | None = None
    for i in range(before_line, haystack_len - context_lines + 1):
        window = "\n".join(haystack_lines[i : i + context_lines])
        if compute_content_hash(window) == context_after_hash:
            after_line = i  # Line before context_after
            break

    if after_line is None:
        return None

    # Return the region between context markers (1-indexed)
    return ContextRegion(line_start=before_line + 1, line_end=after_line)


def find_best_match_with_context(
    needle: str,
    haystack_lines: list[str],
    original_line_start: int,
    context_before_hash: str,
    context_after_hash: str,
    threshold: float = 0.6,
    context_window: int = 10,
    fallback_window: int = 500,
) -> MatchCandidate | None:
    """Find the best fuzzy match using context-based relocation.

    This implements REQ-3 from fuzzy-matching.md:
    1. Search for context_before_hash + context_after_hash pair
    2. If found, fuzzy-match content within ±context_window lines of that region
    3. If context not found, fall back to standard sliding window search

    Context-based matches are PREFERRED over pure content fuzzy matches
    because they use surrounding code structure to locate the anchor.

    Args:
        needle: Text snippet to search for (original anchor content)
        haystack_lines: Target file as list of lines
        original_line_start: Original 1-indexed line position
        context_before_hash: SHA-256 hash of lines before anchor
        context_after_hash: SHA-256 hash of lines after anchor
        threshold: Minimum combined score to consider a match (default 0.6)
        context_window: Lines to search around context region (default ±10)
        fallback_window: Fallback window if context not found (default ±500)

    Returns:
        Best matching MatchCandidate above threshold, or None if no match found
    """
    # Try context-based relocation first (REQ-3)
    context_region = find_context_region(haystack_lines, context_before_hash, context_after_hash)

    if context_region is not None:
        # Context found! Search within ±context_window lines of the region
        # Use the midpoint of the context region as the search center
        search_center = (context_region.line_start + context_region.line_end) // 2

        # Search within ±context_window lines (AC-4: lines 40-60 for region at line 50)
        match = find_best_match(
            needle=needle,
            haystack_lines=haystack_lines,
            original_line_start=search_center,
            threshold=threshold,
            max_window=context_window,
        )

        if match is not None:
            return match

    # Fall back to standard sliding window search (no context available)
    return find_best_match(
        needle=needle,
        haystack_lines=haystack_lines,
        original_line_start=original_line_start,
        threshold=threshold,
        max_window=fallback_window,
    )

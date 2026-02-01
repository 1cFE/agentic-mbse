"""Fuzzy text matching algorithms for anchor reconciliation.

Provides Levenshtein distance and Jaccard similarity for finding drifted anchors.
All algorithms are pure Python, deterministic, and optimized for performance.
"""

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

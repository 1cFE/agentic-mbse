"""Anchor reconciliation — re-anchoring comments after source file edits.

This module implements the multi-signal reconciliation algorithm for relocating
comment anchors when source files change. It tries multiple strategies in sequence:
1. Exact content hash match (fast path)
2. Context-based fuzzy matching (uses surrounding code)
3. Sliding window fuzzy matching (broader search)
4. Orphan marking (when all strategies fail)
"""

from comment_system.fuzzy import (
    compute_content_hash,
    find_best_match,
    find_best_match_with_context,
)
from comment_system.models import Anchor, AnchorHealth


def reconcile_anchor(
    anchor: Anchor,
    source_lines: list[str],
    threshold: float = 0.6,
    context_window: int = 10,
    fallback_window: int = 500,
) -> Anchor:
    """Reconcile a single anchor to new source file content.

    Implements REQ-2 from anchor-reconciliation.md: multi-signal anchoring with
    progressive fallback strategies. The algorithm tries strategies in order:

    1. EXACT MATCH: Look for exact content hash at original position
    2. EXACT MATCH (MOVED): Scan entire file for exact content hash
    3. CONTEXT-BASED: Use context hashes to find region, then fuzzy match
    4. SLIDING WINDOW: Fuzzy match within ±fallback_window of original position
    5. ORPHAN: Mark as orphaned when all strategies fail

    Args:
        anchor: The anchor to reconcile (with original line positions)
        source_lines: Current source file content as list of lines
        threshold: Minimum similarity score (0-1) for fuzzy matching (default 0.6)
        context_window: Lines to search around context region (default ±10)
        fallback_window: Lines to search in sliding window fallback (default ±500)

    Returns:
        New Anchor instance with updated line positions and health status.
        The returned anchor preserves all original hashes and content_snippet
        for traceability.

    Performance:
        - Exact match: O(1) position check, O(n) full scan fallback
        - Context-based: O(n) for context search + O(m*k) fuzzy match
        - Sliding window: O(m*k*w) where w is window size
        Target: < 100ms per anchor on 10,000-line file
    """
    # Strategy 1: Exact content match at original position
    # This is the fast path for simple edits (whitespace changes, moves)
    original_start_idx = anchor.line_start - 1  # Convert to 0-indexed
    original_end_idx = anchor.line_end  # line_end is inclusive, so this is correct

    if 0 <= original_start_idx < len(source_lines) and original_end_idx <= len(source_lines):
        # Extract content at original position
        content_at_original = "\n".join(source_lines[original_start_idx:original_end_idx])
        content_hash_at_original = compute_content_hash(content_at_original)

        if content_hash_at_original == anchor.content_hash:
            # Perfect match at original position (REQ-3: anchored status)
            return Anchor(
                content_hash=anchor.content_hash,
                context_hash_before=anchor.context_hash_before,
                context_hash_after=anchor.context_hash_after,
                line_start=anchor.line_start,
                line_end=anchor.line_end,
                content_snippet=anchor.content_snippet,
                health=AnchorHealth.ANCHORED,
                drift_distance=0,
            )

    # Strategy 2: Exact content match elsewhere in file (content moved)
    # Scan entire file for exact hash match
    anchor_length = anchor.line_end - anchor.line_start + 1
    for line_idx in range(len(source_lines) - anchor_length + 1):
        candidate_content = "\n".join(source_lines[line_idx : line_idx + anchor_length])
        if compute_content_hash(candidate_content) == anchor.content_hash:
            # Found exact content at different position
            drift = abs(line_idx + 1 - anchor.line_start)
            return Anchor(
                content_hash=anchor.content_hash,
                context_hash_before=anchor.context_hash_before,
                context_hash_after=anchor.context_hash_after,
                line_start=line_idx + 1,  # Convert back to 1-indexed
                line_end=line_idx + anchor_length,
                content_snippet=anchor.content_snippet,
                health=AnchorHealth.ANCHORED,  # Still anchored, just moved
                drift_distance=drift,
            )

    # Strategy 3: Context-based fuzzy matching (REQ-2 from anchor-reconciliation.md)
    # Use surrounding code hashes to locate region, then fuzzy match within it
    context_match = find_best_match_with_context(
        needle=anchor.content_snippet,
        haystack_lines=source_lines,
        original_line_start=anchor.line_start,
        context_before_hash=anchor.context_hash_before,
        context_after_hash=anchor.context_hash_after,
        threshold=threshold,
        context_window=context_window,
        fallback_window=fallback_window,
    )

    if context_match is not None:
        # Found via context-based fuzzy matching (REQ-3: drifted status)
        drift = abs(context_match.line_start - anchor.line_start)
        return Anchor(
            content_hash=anchor.content_hash,  # Preserve original hash
            context_hash_before=anchor.context_hash_before,
            context_hash_after=anchor.context_hash_after,
            line_start=context_match.line_start,
            line_end=context_match.line_end,
            content_snippet=anchor.content_snippet,  # Preserve original snippet
            health=AnchorHealth.DRIFTED,
            drift_distance=drift,
        )

    # Strategy 4: Sliding window fuzzy matching (fallback when context fails)
    # This is already attempted by find_best_match_with_context as a fallback,
    # so if we reached here, context_match is None which means even the fallback
    # failed. But let's be explicit for clarity:
    fallback_match = find_best_match(
        needle=anchor.content_snippet,
        haystack_lines=source_lines,
        original_line_start=anchor.line_start,
        threshold=threshold,
        max_window=fallback_window,
    )

    if fallback_match is not None:
        # Found via pure sliding window fuzzy matching
        drift = abs(fallback_match.line_start - anchor.line_start)
        return Anchor(
            content_hash=anchor.content_hash,  # Preserve original hash
            context_hash_before=anchor.context_hash_before,
            context_hash_after=anchor.context_hash_after,
            line_start=fallback_match.line_start,
            line_end=fallback_match.line_end,
            content_snippet=anchor.content_snippet,  # Preserve original snippet
            health=AnchorHealth.DRIFTED,
            drift_distance=drift,
        )

    # Strategy 5: Orphan the anchor (all strategies failed)
    # REQ-3: Preserve original line numbers and content snippet
    return Anchor(
        content_hash=anchor.content_hash,  # Preserve original hash
        context_hash_before=anchor.context_hash_before,
        context_hash_after=anchor.context_hash_after,
        line_start=anchor.line_start,  # Keep original position
        line_end=anchor.line_end,
        content_snippet=anchor.content_snippet,  # Keep original snippet
        health=AnchorHealth.ORPHANED,
        drift_distance=0,  # No drift since we couldn't find it
    )

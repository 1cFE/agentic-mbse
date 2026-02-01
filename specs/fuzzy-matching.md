# Specification: Fuzzy Text Matching for Anchor Reconciliation

**Purpose:** Provide robust fuzzy matching algorithms to re-anchor comments when exact content hash match fails.

## Requirements

**REQ-1: Matching Algorithms**
- MUST implement normalized Levenshtein distance (0-1 scale)
- MUST implement Jaccard similarity on word-level bigrams
- MUST use sliding window search (anchor_length ± 20%)
- MUST NOT use LLM or ML models (conventional algorithms only)

**REQ-2: Similarity Thresholds**
- Levenshtein > 0.6 → candidate match
- Jaccard > 0.5 → candidate match
- Combined score: `(levenshtein + jaccard) / 2 > 0.6` → accept
- Below threshold → continue search or mark orphaned

**REQ-3: Context-Based Relocation**
- MUST search for context_before_hash + context_after_hash pair
- If found, MUST fuzzy-match content within that region
- Context window: ±10 lines from original position
- MUST prefer context match over pure content fuzzy match

**REQ-4: Performance**
- Fuzzy search MUST complete in < 100ms per anchor on 10,000-line file
- MUST early-exit on exact match (no fuzzy search needed)
- MUST limit sliding window to ±500 lines from original position

**REQ-5: Disambiguation**
- When multiple candidates score above threshold, choose highest score
- If scores within 0.05, choose closest to original line position
- MUST mark as `drifted` (not `anchored`) when disambiguation was needed

## Acceptance Criteria

**AC-1:** Given original text "linear scaling model", when changed to "piecewise linear scaling", then Levenshtein similarity is > 0.6

**AC-2:** Given anchor at line 100, when text moves to line 300, then sliding window search finds match in < 100ms

**AC-3:** Given two candidate matches scoring 0.75 and 0.74, when disambiguating, then highest score (0.75) is chosen

**AC-4:** Given content hash match fails, when context hashes found at line 50, then fuzzy search limited to lines 40-60

**AC-5:** Given fuzzy match with 0.55 combined score, when below threshold, then no match returned (search continues)

**AC-6:** Given 100 threads requiring fuzzy matching on 10,000-line file, when reconciliation runs, then total time < 10 seconds

## Interfaces

**Inputs:**
- Original content snippet (string)
- Target source file content (string)
- Context snippets and hashes
- Original line position (for search window)

**Outputs:**
- List of candidate matches with scores
- Best match location (line range) or null
- Similarity score (0-1)

**References:**
- `anchor-reconciliation.md`: Reconciliation algorithm phases
- `data-model.md`: Anchor snippet fields

## Constraints

**CON-1:** No external dependencies (pure Python/TS implementation)
**CON-2:** Algorithms MUST be deterministic (no randomness)
**CON-3:** Memory usage MUST be O(n) where n is file size
**CON-4:** MUST handle unicode correctly (normalize before comparison)

## Out of Scope

- Semantic similarity (embeddings, transformers)
- Custom trained models
- Language-specific parsing (treat all as plain text)
- Multi-line regex matching
- Phonetic matching algorithms

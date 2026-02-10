# Fix Plain Header Promotion Lookahead

## Purpose
Fix the `_PLAIN_HEADER_RE` regex to handle section headings that flow directly into body text without a trailing blank line.

## Requirements
- The `_PLAIN_HEADER_RE` in `postprocess.py` currently requires `(?=\n\n)` (a blank line after the heading)
- Real academic papers often have headings that flow directly into the next paragraph on the very next line
- The regex should be relaxed to also match a heading followed by a single newline, provided the next line starts with typical body text (uppercase letter starting a sentence)
- The change must NOT promote TOC entries, numbered list items, or bibliography references

## Investigation Steps
1. Read the current `_PLAIN_HEADER_RE` pattern and understand why `(?=\n\n)` was chosen
2. Write a learning test that:
   - Extracts the sparc_overview Section 4 heading context (lines 439-445 of `full_document.md`)
   - Passes it through `promote_plain_headers()` and verifies it's NOT promoted (current behavior)
   - Then applies the fix and verifies it IS promoted (desired behavior)
3. Check what other plain-text headers in the corpus might be affected by relaxing the lookahead
4. Verify TOC entries are still rejected (test with aries_cost_account or delene_2001 which likely have TOC pages)

## Acceptance Criteria
- sparc_overview: `## 4 SPARC scenarios and performance projections` appears in the extracted markdown
- sparc_overview heading count increases from 6 to at least 7
- No new phantom headings introduced in any other corpus paper (heading counts must not increase by more than 3 for any paper)
- All existing corpus tests pass
- The `_is_toc_line()` check still rejects TOC entries

## Verification
```bash
# Run corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check sparc heading count
python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/full_document.md

# Check no regressions
python3 tests/corpus/compare.py

# Specifically check for the Section 4 heading
grep "^## 4" tests/corpus/current/sparc_overview/full_document.md
```

## Constraints
- Must not break any existing corpus tests
- Must not introduce phantom headings in aries_cost_account (which has a TOC and numbered list entries)
- The fix should be minimal — only relax the trailing lookahead, not the leading lookbehind

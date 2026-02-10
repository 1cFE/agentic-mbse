# Bold All-Caps Heading Promotion

## Purpose
Fix heading detection for bold all-caps single-word section headings like `**ABSTRACT**`, `**CONTENTS**`, `**ACRONYMS**` that currently slip through all promotion patterns.

## Requirements
- Bold all-caps standalone lines that match known section heading words should be promoted to `##` headings
- Bold all-caps standalone lines with spaces (multi-word) that are between blank lines should also be promoted
- Must not promote bold labels that happen to be all-caps (e.g., `**MW**`, `**USA**`)
- Must preserve existing all-caps promotion for non-bold text (the `_ALLCAPS_HEADER_RE` pattern)

## Investigation Steps
1. Read `src/agentic_mbse/extraction/postprocess.py` — understand the gap between `_ALLCAPS_HEADER_RE` (matches plain text, not bold) and `_UNNUMBERED_BOLD_HEADER_RE` (requires 14+ chars)
2. Check what bold all-caps patterns exist across the corpus:
   ```
   grep -n '^\*\*[A-Z][A-Z ]*\*\*$' tests/corpus/current/*/full_document.md
   ```
3. Write a learning test: apply `promote_allcaps_headers` to `**ABSTRACT**` — verify it does NOT match (because of `**` markers). Then apply `promote_unnumbered_bold_headers` — verify it does NOT match (too short). This confirms the gap.
4. Design a new pattern or modify existing patterns to catch bold all-caps headings

## Evidence
In `delene_2001`, these headings appear as bold all-caps between blank lines but are NOT promoted:
- Line 91: `**CONTENTS**` (8 chars, below 14-char minimum for unnumbered bold)
- Line 171: `**ACRONYMS**` (8 chars)
- Line 227: `**ABSTRACT**` (8 chars)

The baseline had these as `## CONTENTS`, `## ACRONYMS`, `## ABSTRACT`. The current pipeline drops them to bold text.

Root cause: Two pattern gaps compound:
1. `_ALLCAPS_HEADER_RE` matches `[A-Z][A-Z &/,]{3,59}` — requires NO bold markers
2. `_UNNUMBERED_BOLD_HEADER_RE` matches `\*\*([A-Z][^*]{14,})\*\*` — requires 14+ chars after first letter

Bold all-caps words shorter than 15 chars fall through both patterns.

## Acceptance Criteria
- `delene_2001` heading count increases from 23 to at least 25 (recovering CONTENTS, ABSTRACT, ACRONYMS)
- Heading count for other corpus papers does not decrease
- `uv run pytest tests/test_postprocess.py -v` passes
- `uv run pytest tests/test_corpus.py --run-corpus -v` passes
- No new false positive headings introduced (verify by manual inspection of diff)

## Verification
```bash
# Check heading count improvement
python3 tests/corpus/metrics.py tests/corpus/current/delene_2001/full_document.md | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['heading_count'] >= 25, f'Expected >=25, got {d[\"heading_count\"]}'"

# Run postprocess unit tests
uv run pytest tests/test_postprocess.py -v

# Run corpus regression tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check no regressions in other papers
python3 tests/corpus/compare.py
```

## Constraints
- Do NOT reduce heading counts for hawker_2020, aries_cost_account, or hsu_2020
- Do NOT promote short bold abbreviations like `**MW**`, `**HTS**`, `**QA**`
- Minimum word length or known-word check should prevent false positives
- The fix should be in `postprocess.py` only (pure regex, no ML)

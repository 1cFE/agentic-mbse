# Promote Italic Numbered Section Headers

## Purpose
Add a postprocess pattern to promote italic-formatted numbered section headers (e.g., `4.1. _Full-performance H-mode discharge_`) to proper markdown headings.

## Requirements
- The sparc_overview paper uses italic formatting for subsection headers: `4.1. _Title text_`
- This pattern is not currently handled by any promotion rule in `postprocess.py`
- A new regex should match lines of the form: `{number}.{subnumber}. _Title text_` or `{number}.{subnumber}. _Title text_` between blank lines or at line start
- The heading level should be derived from the section number depth (same as `_header_depth()`)
- Must not match italic text mid-paragraph or italic citations

## Investigation Steps
1. Grep all corpus extractions for the pattern `^\d+\.\d+.*_[A-Z]` to find how many papers use italic numbered headers
2. Check if this pattern appears in non-heading contexts (e.g., italic citations, italic definitions)
3. Write a learning test that:
   - Takes the string `4.1. _Full-performance H-mode discharge_` between blank lines
   - Verifies it's NOT promoted (current behavior)
   - Applies the new pattern and verifies it becomes `### 4.1 Full-performance H-mode discharge`
4. Check sparc_overview specifically: how many italic subsection headers exist?

## Acceptance Criteria
- sparc_overview: `4.1. _Full-performance H-mode discharge_`, `4.2. _Full-performance L-mode discharge_`, `4.3. _Reduced field and current H-mode discharge_` are all promoted to `###` headings
- sparc_overview heading count increases from 6 to at least 9 (6 existing + 3 italic subsections)
- No phantom headings introduced in other corpus papers
- All existing corpus tests pass

## Verification
```bash
# Run corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check sparc heading count
python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/full_document.md

# Check for promoted italic headers
grep "^###" tests/corpus/current/sparc_overview/full_document.md

# Full comparison
python3 tests/corpus/compare.py
```

## Constraints
- Must not break any existing corpus tests
- Must not match italic text that appears mid-paragraph
- The pattern must require the italic text to be on a standalone line (between blank lines or preceded by a blank line)
- Must integrate cleanly into the `postprocess()` orchestrator function — add the call in a logical position after existing header promotion steps

# Italic Numbered Header Promotion in Postprocess

## Purpose
Add a postprocess rule to promote italic-wrapped numbered section headers (e.g., `_3.1. Scoping studies_`) to markdown headings, as a safety net for papers where the custom header detector (spec 02) doesn't fully resolve italic subsections.

## Requirements
- Lines matching the pattern `_X.Y. Title text_` or `_X.Y.Z. Title text_` (italic-wrapped numbered sections) must be promoted to markdown headings at the appropriate depth
- Multi-line italic headings (title split across two lines) should be handled
- Must NOT promote italic text that is mid-paragraph (only standalone lines between blank lines)
- Must NOT promote TOC entries (lines with trailing page numbers or dot leaders)

## Investigation Steps

### Learning test: Current italic patterns in corpus
Run this to see what italic numbered patterns exist across the corpus:

```bash
grep -nP '^_\d+\.\d+' tests/corpus/current/helios_design/full_document.md | head -20
grep -nP '^_\d+\.\d+' tests/corpus/current/sparc_overview/full_document.md | head -20
grep -nP '^_\d+\.\d+' tests/corpus/current/energy_amplifier/full_document.md | head -20
```

This will show which papers have this pattern and how consistently it appears.

### Design notes
The pattern `_X.Y. Title_` (italic numbered section) appears prominently in:
- **helios_design**: 15+ subsection headings like `_3.1. Scoping studies, heating and fueling, and dynamic_` and `_3.2. The stellarator equilibrium_`
- **sparc_overview**: `4.1. _Full-performance H-mode discharge_` (number outside italic)

Two variants to handle:
1. `_X.Y. Title text_` — entire heading in italic
2. `X.Y. _Title text_` — number outside, title in italic

The regex should match standalone lines (between blank lines) that start with an optional italic marker, then a numbered section pattern, then italic text.

This should be added to `postprocess.py` as a new `promote_italic_headers()` function, called in the `postprocess()` orchestrator after `promote_bold_headers()`.

## Acceptance Criteria
- **helios_design**: heading_count >= 20 (currently 7, needs +15 from italic subsections)
- **sparc_overview**: heading_count >= 8 (currently 5, needs subsections like 4.1, 4.2, 4.3)
- No regressions: all existing headings in other papers preserved within -10%
- New headings must have correct depth: `_3.1. Title_` → `### 3.1 Title` (H3), `_3.4.1. Title_` → `#### 3.4.1 Title` (H4)

## Verification
```bash
# Check helios heading count
python3 tests/corpus/metrics.py tests/corpus/current/helios_design/full_document.md
# heading_count >= 20

# Check sparc heading count
python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/full_document.md
# heading_count >= 8

# Verify heading hierarchy is correct (H3 for X.Y, H4 for X.Y.Z)
grep '^### ' tests/corpus/current/helios_design/full_document.md | head -10
# Should show subsections like "### 3.1 Scoping studies..."

# Full test suite
uv run pytest tests/ -v
```

## Constraints
- Add the new function in `src/agentic_mbse/extraction/postprocess.py`
- Call it in the `postprocess()` orchestrator, after `promote_bold_headers()` and before `clean_header_artifacts()`
- Do NOT modify the custom header detector (spec 02) — this is a separate safety net
- The regex must not match mid-paragraph italic text (require blank line boundaries)
- Do NOT break existing unit tests

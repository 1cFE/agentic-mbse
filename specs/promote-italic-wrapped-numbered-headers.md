# Promote Italic-Wrapped Numbered Section Headers

## Purpose
Promote 14 missed subsection headings in helios_design where the section number is INSIDE the italic markers (`_3.1. Title text_`) rather than outside (`3.1. _Title text_`).

## Requirements
- Add a new regex and promotion function for the pattern `_N.M. Title_` (number inside italics)
- Handle multi-line wrapped headers: `_3.1. Long title text_\n_continuation_`
- Handle 3-level depth: `_3.4.1. Title_` → H4
- Preserve existing italic-outside-number promotion for sparc_overview (`4.1. _Title_`)
- No phantom heading creation — only promote lines between blank lines that match the numbered pattern

## Investigation Steps
1. Read `postprocess.py` lines 88–93 — the existing `_ITALIC_NUMBERED_HEADER_RE` regex
2. Write a learning test with representative helios patterns:
   - Single line: `_3.2. The stellarator equilibrium_`
   - Multi-line: `_3.1. Scoping studies, heating and fueling, and dynamic_\n_accessibility_`
   - Three-level: `_3.4.1. A note on the effects_`
3. Verify the new regex does NOT match on other corpus papers (check for false positives by running against all 7 papers)
4. Check the special case `_3.4.1. A note on the e_ ff _ects of an abrupt plasma termi-_` — this has a broken italic due to a ligature split. Decide whether to handle this edge case or accept it as a known limitation

## Acceptance Criteria
- helios_design heading count increases from 7 to ≥20 (currently 7 H2, should gain 14+ H3/H4 subsection headings)
- helios_design `heading_by_level` gains H3 entries (currently only has H2)
- sparc_overview heading count remains at 11 (no regression)
- All promoted headings correspond to real subsection boundaries in the PDF
- No false positives in other corpus papers

## Verification
```bash
# Run full corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check helios_design heading structure
python3 -c "
with open('tests/corpus/current/helios_design/full_document.md') as f:
    text = f.read()
for line in text.split('\n'):
    if line.startswith('#'):
        print(line[:100])
"

# Verify no regressions
python3 tests/corpus/compare.py

# Specific metrics check
python3 tests/corpus/metrics.py tests/corpus/current/helios_design/full_document.md
python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/full_document.md
```

## Constraints
- Do NOT modify the existing `_ITALIC_NUMBERED_HEADER_RE` or `promote_italic_numbered_headers()` — add a NEW pattern alongside it
- Do NOT break sparc_overview's already-promoted italic headers (these use the number-outside-italic format)
- The new function must be called in the `postprocess()` orchestrator in appropriate order (after `promote_bold_headers` and before `reject_noise_headers`)
- Helios baseline must be regenerated after the fix

# Broken Ligature Dictionary Repair

## Purpose
Add a dictionary-based repair step to fix words where PyMuPDF drops the second character of a ligature (e.g., "fi" → "f", producing "feld" instead of "field").

## Requirements
- The existing `repair_ligatures()` function in `postprocess.py` handles Unicode FB00-FB04 ligature codepoints, but some PDFs have fonts where PyMuPDF drops the ligature's second character entirely
- This produces broken words like: "feld" (field), "confnement" (confinement), "efciency" (efficiency), "coefcient" (coefficient)
- A new repair function should use a dictionary of known broken→fixed word patterns to restore these
- The dictionary approach is safer than regex substitution because it targets specific known-broken words rather than guessing

## Investigation Steps
1. Run a comprehensive scan across all corpus extractions to catalog every broken-ligature word:
   ```python
   # Search for common fi/fl/ff ligature drops
   # Pattern: word that becomes nonsense when 'i' or 'l' after 'f' is dropped
   ```
2. Check whether pymupdf4llm's `use_glyphs=True` parameter resolves any of these — run a quick test extracting one affected page with and without `use_glyphs`
3. Determine if the broken words are consistent across runs (they should be, since they're font-encoding issues)
4. Build the repair dictionary from observed broken words

## Acceptance Criteria
- All 8 currently-observed broken-ligature words are fixed:
  - helios_design: "feld"→"field" (4x), "confnement"→"confinement" (2x), "efciency"→"efficiency" (1x)
  - hawker_2020: "coefcient"→"coefficient" (1x)
- No false positives: the repair must not change legitimate words
- Character count changes are minimal (< 0.1% per document)
- All existing corpus tests pass

## Verification
```bash
# Run corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check specific broken words are fixed
grep -c "feld\|confnement\|efciency\|coefcient" tests/corpus/current/helios_design/full_document.md
# Should be 0

grep -c "field\|confinement\|efficiency" tests/corpus/current/helios_design/full_document.md
# Should be > 0

grep -c "coefcient" tests/corpus/current/hawker_2020/full_document.md
# Should be 0

# Full comparison (char counts should be stable)
python3 tests/corpus/compare.py
```

## Constraints
- Must not break any existing corpus tests
- Must not introduce false-positive word changes
- The dictionary should be conservative — only include words that are confirmed broken in the corpus
- First check if `use_glyphs=True` or other pymupdf4llm parameters solve this upstream before implementing a dictionary workaround
- Place the repair function in `postprocess.py` and call it after `repair_ligatures()` in the orchestrator

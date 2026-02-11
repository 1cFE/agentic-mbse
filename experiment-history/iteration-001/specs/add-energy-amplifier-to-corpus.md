# Add Energy Amplifier PDF to Test Corpus

## Purpose
Add FILE_1798.pdf (Rubbia et al., "Conceptual Design of a Fast Neutron Operated High Power Energy Amplifier", CERN, 241 pages) to the test corpus per the challenge rule ADD_PDF_PER_ITERATION=1.

## Requirements
- Move/copy `tests/corpus/pool/FILE_1798.pdf` to `tests/corpus/pdfs/energy_amplifier.pdf` (use a descriptive slug)
- Add an entry to `tests/corpus/papers.jsonl` with appropriate metadata
- Run the full pipeline to generate baseline and current extractions
- Set appropriate per-paper thresholds if needed (this is a 1999-era PDF with potentially tricky formatting)

## Investigation Steps
1. Extract pages 0-5 with pymupdf4llm to understand the document's heading style, table presence, and math content
2. Check text quality: ligature issues, unicode problems, OCR artifacts (this is a Word-generated PDF from 1999)
3. Determine if the document has tables (many landscape pages suggest large tables or figures)
4. Measure extraction time — at 241 pages this could be slow; consider whether a page limit or timeout is needed for the test
5. Generate a baseline extraction and compute metrics

## Acceptance Criteria
- `tests/corpus/papers.jsonl` contains an entry for `energy_amplifier` with correct metadata:
  - `slug`: "energy_amplifier"
  - `pdf_path`: "tests/corpus/pdfs/energy_amplifier.pdf"
  - `source`: "pool"
  - `has_tables`: (determined by investigation)
  - `has_math`: true (nuclear physics paper)
  - `pages`: 241
- Baseline metrics exist at `tests/corpus/baseline/energy_amplifier/metrics.json`
- Current extraction succeeds and produces non-empty markdown
- All corpus tests pass (including the new paper)
- Extraction time for the full corpus remains under 300 seconds

## Verification
```bash
# Run full corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check metrics
python3 tests/corpus/metrics.py tests/corpus/current/energy_amplifier/full_document.md

# Full comparison
python3 tests/corpus/compare.py

# Verify timing
# Total test time should be under 300s
```

## Constraints
- Must not break any existing corpus tests
- If extraction takes >120s for this single paper, add a note about it and consider whether corpus test timeout needs adjustment
- The baseline should be generated from the current pipeline (not imported from another source), since this is a new paper being added
- Copy (don't move) the PDF from pool to pdfs, so the pool directory continues to have it as a record

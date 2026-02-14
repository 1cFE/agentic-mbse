# Add woodruff_2026 to Test Corpus

## Purpose
Add one PDF from the pool to the corpus per the progressive challenge rule (ADD_PDF_PER_ITERATION=1), expanding test coverage to a new document format and publisher.

## Requirements
- Select and add `Woodruff - 2026 - A costing framework for fusion power plants.pdf` from the pool
- This paper was selected because:
  - 25 pages, compact (0.4MB), excellent native text (~90K chars extracted)
  - Different publisher/format than existing corpus (Woodruff Scientific — not a journal paper)
  - Deeply nested heading structure (H2/H3/H4) with 82 headings detected — tests whether the pipeline handles rich hierarchy correctly
  - No ruled tables (tests heading-only extraction)
  - Topically relevant (fusion costing — complements aries_cost_account)
  - Fast extraction (~18s based on similar-sized papers)
- The paper must extract successfully and pass all corpus tests
- Establish baseline metrics for regression testing

## Investigation Steps

**Learning test: Extract and inspect before committing to the corpus**

The build agent should:
1. Copy the PDF to `tests/corpus/pdfs/` with slug `woodruff_2026`
2. Run a standalone extraction to check quality:
```python
import sys
sys.path.insert(0, "src")
from pathlib import Path
from agentic_mbse.extraction.pymupdf_backend import extract
import re, tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    result = extract(Path("tests/corpus/pdfs/woodruff_2026.pdf"), Path(tmpdir))
    md = Path(tmpdir, "full_document.md").read_text()
    headings = re.findall(r'^#{1,6}\s+.+$', md, re.MULTILINE)
    print(f"Chars: {len(md)}")
    print(f"Headings: {len(headings)}")
    for h in headings[:20]:
        print(f"  {h[:80]}")
```
3. Inspect the output for obvious problems (false positive headings, missing structure, garbled text)
4. Set `heading_count_min` and `heading_count_max` based on observed output quality
5. Note: The initial learning test extraction showed 82 headings. After spec-01 (`lines_strict`) and spec-02 (Guard 2 extension) are applied, the count may differ. Set bounds based on the FINAL pipeline output, not the pre-fix count.

## Acceptance Criteria
1. PDF file exists at `tests/corpus/pdfs/woodruff_2026.pdf`
2. Entry exists in `tests/corpus/papers.jsonl` with appropriate metadata
3. Baseline metrics exist at `tests/corpus/baseline/woodruff_2026/metrics.json`
4. `uv run pytest tests/test_corpus.py --run-corpus -v` passes with all 4 tests (including the new paper)
5. Heading count is reasonable for a 25-page deeply-nested paper (expect 30-100 headings)
6. No garbled text or catastrophic extraction failures

## Verification
```bash
# Verify PDF exists
ls -la tests/corpus/pdfs/woodruff_2026.pdf

# Verify papers.jsonl entry
grep woodruff tests/corpus/papers.jsonl

# Run corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check metrics
python3 tests/corpus/metrics.py tests/corpus/current/woodruff_2026/full_document.md
```

## Constraints
- Must use the exact filename convention: slug `woodruff_2026`, PDF at `tests/corpus/pdfs/woodruff_2026.pdf`
- Must establish baseline AFTER applying spec-01 and spec-02 changes (so baselines reflect the improved pipeline)
- heading_count_min and heading_count_max bounds should be set based on observed extraction, not guessed
- Do NOT modify the extraction pipeline to accommodate this paper — it should work with existing code (or with changes from spec-01 and spec-02)
- Apply this spec AFTER spec-01 and spec-02 are implemented, so the baseline reflects the final pipeline state

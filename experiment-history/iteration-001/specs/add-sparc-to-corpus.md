# Add SPARC Paper to Test Corpus

## Purpose
Expand the test corpus by adding "Creely et al. - 2020 - Overview of the SPARC tokamak" from the PDF pool, per the progressive challenge rule (ADD_PDF_PER_ITERATION=1).

## Requirements
- Copy the SPARC PDF from `tests/corpus/pool/` to `tests/corpus/pdfs/`
- Add an entry to `tests/corpus/papers.jsonl` with correct metadata
- Generate a baseline extraction and save to `tests/corpus/baseline/sparc_overview/`
- All corpus tests must pass with the new paper included

## Investigation Steps
1. Verify PDF properties:
   ```python
   import pymupdf
   doc = pymupdf.open("tests/corpus/pool/Creely et al. - 2020 - Overview of the SPARC tokamak.pdf")
   print(f"Pages: {len(doc)}")
   # Check tables, math, layout
   ```
   Known results from investigation: 25 pages, has tables (page 9), has math (Greek letters, equations), single paper, two-column academic layout (Journal of Plasma Physics).

2. Extract with current pipeline and inspect quality:
   ```bash
   uv run python3 -c "
   from doc_ingest.converters.pdf_converter import PyMuPDF4LLMConverter
   from tests.corpus.metrics import compute_metrics
   pdf = open('tests/corpus/pdfs/sparc_overview.pdf', 'rb').read()
   result = PyMuPDF4LLMConverter().convert(pdf)
   metrics = compute_metrics(result.markdown)
   print(metrics)
   "
   ```

3. Verify extraction produces reasonable headings, tables, and character count before establishing as baseline

## Evidence
- Pool contains 2 PDFs: SPARC (25 pages) and FILE_1798 (241 pages)
- SPARC is preferred: manageable size, relevant domain (fusion), has both tables and math, journal paper format
- FILE_1798 is 241 pages and would be slow to process (not suitable for iteration 1)

## Acceptance Criteria
- `tests/corpus/pdfs/sparc_overview.pdf` exists
- `tests/corpus/papers.jsonl` has 6 entries (was 5)
- `tests/corpus/baseline/sparc_overview/full_document.md` exists with non-empty content
- `tests/corpus/baseline/sparc_overview/metrics.json` exists with heading_count >= 3
- `uv run pytest tests/test_corpus.py --run-corpus -v` passes with all 4 tests passing
- No regressions on existing 5 papers

## Verification
```bash
# Verify paper count
python3 -c "
import json
papers = [json.loads(l) for l in open('tests/corpus/papers.jsonl') if l.strip()]
assert len(papers) == 6, f'Expected 6 papers, got {len(papers)}'
assert any(p['slug'] == 'sparc_overview' for p in papers), 'sparc_overview not found'
print('OK: 6 papers including sparc_overview')
"

# Run corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check metrics
python3 tests/corpus/metrics.py tests/corpus/baseline/sparc_overview/full_document.md
python3 tests/corpus/compare.py
```

## Constraints
- Use slug `sparc_overview` for consistency
- Set `has_tables: true`, `has_math: true`, `pages: 25`
- Set `source: "pool"` to distinguish from original fusion-tea papers
- Do NOT modify the extraction pipeline — this spec only adds test data
- If heading detection is weak for this paper (journal format may differ), set appropriate `heading_regression_pct` threshold

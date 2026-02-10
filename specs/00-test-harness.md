# Spec 00: Real-World Test Harness

## Priority: FIRST — Nothing else matters without this

## Problem

All 187 existing tests pass against mocks. The converters were never registered in the pipeline. Nobody ran a real document through the system. We need a test harness that runs real papers and measures quality, and it must exist BEFORE any other work happens.

## Deliverables

### 1. Corpus registry (`tests/corpus/papers.jsonl`)

One line per test document:
```jsonl
{"slug": "hawker_2020", "pdf_path": "tests/corpus/pdfs/hawker_2020.pdf", "source": "fusion-tea", "has_tables": false, "has_math": true, "pages": 11}
{"slug": "aries_cost_account", "pdf_path": "tests/corpus/pdfs/aries_cost_account.pdf", "source": "fusion-tea", "has_tables": true, "has_math": false, "pages": 116}
{"slug": "helios_design", "pdf_path": "tests/corpus/pdfs/helios_design.pdf", "source": "fusion-tea", "has_tables": true, "has_math": true, "pages": 32}
{"slug": "hsu_2020", "pdf_path": "tests/corpus/pdfs/hsu_2020.pdf", "source": "fusion-tea", "has_tables": true, "has_math": false, "pages": 8}
{"slug": "delene_2001", "pdf_path": "tests/corpus/pdfs/delene_2001.pdf", "source": "fusion-tea", "has_tables": true, "has_math": false, "pages": 30}
```

### 2. Baseline extractions (`tests/corpus/baseline/`)

Copy the existing fusion-tea extractions as ground truth:
```
tests/corpus/baseline/{slug}/
  full_document.md    # From fusion-tea knowledge/sources/{slug}/full_document.md
  metrics.json        # Auto-computed on first run
```

### 3. Metrics computation (`tests/corpus/metrics.py`)

```python
@dataclass
class ExtractionMetrics:
    char_count: int
    heading_count: int
    heading_by_level: dict[int, int]  # {2: 5, 3: 12, ...}
    table_row_count: int              # Lines matching |...|...|
    math_symbol_count: int
    figure_ref_count: int
    extraction_time_seconds: float

def compute_metrics(markdown: str, elapsed: float = 0.0) -> ExtractionMetrics: ...
def compare_metrics(baseline: ExtractionMetrics, current: ExtractionMetrics) -> dict: ...
```

### 4. Corpus test runner (`tests/test_corpus.py`)

```python
@pytest.mark.corpus  # Only runs with --run-corpus flag
class TestCorpus:
    def test_all_papers_extract_successfully(self):
        """Every paper in papers.jsonl must produce non-empty output."""

    def test_no_quality_regression_vs_baseline(self):
        """Current extraction must not lose >10% on any key metric vs baseline."""

    def test_table_heavy_papers_have_tables(self):
        """Papers marked has_tables=true must have table_row_count > 0."""

    def test_heading_structure_present(self):
        """Every paper must have heading_count >= 3."""
```

### 5. Comparison report (`tests/corpus/compare.py`)

A CLI script (not just pytest) that prints a human-readable comparison:
```
$ python tests/corpus/compare.py

Document              Headings    Tables      Chars       Time
                      base→curr   base→curr   base→curr
hawker_2020           11→14 (+3)  0→0 (=)     60k→60k     9.3s
aries_cost_account    102→66 (-35%) 137→0 (!!!) 286k→263k  22.6s
helios_design         52→1 (-98%)  25→25 (=)   145k→143k  7.8s
...

REGRESSIONS:
  aries_cost_account: tables dropped from 137 to 0
  helios_design: headings dropped from 52 to 1
```

## Acceptance Criteria

- [ ] `uv run pytest tests/test_corpus.py --run-corpus` runs all 5 papers through the pipeline
- [ ] Metrics are computed and saved to `tests/corpus/current/{slug}/metrics.json`
- [ ] `python tests/corpus/compare.py` prints comparison table
- [ ] Regressions are clearly flagged
- [ ] Adding a new paper requires only: (a) add PDF to `tests/corpus/pdfs/`, (b) add line to `papers.jsonl`, (c) optionally add baseline

## What We Don't Know

- What metric thresholds define "regression"? Start with >10% loss on any metric, adjust based on experience.
- Should we track metrics per-section or whole-document? Start with whole-document, add per-section if needed.
- How to handle papers with no baseline? Extract and manually inspect, then promote to baseline.

## Expanding The Corpus

After initial 5 papers, add at least 2 papers per category:
- [ ] Math-heavy physics paper (arXiv)
- [ ] Scanned/OCR-only PDF
- [ ] Multi-column conference proceedings
- [ ] Very long document (200+ pages)
- [ ] Paper with complex figures + captions

Each addition should be documented: what does this paper test that existing papers don't?

# Design: Document Ingestion Pipeline

## What This Is

A document extraction system that takes academic papers (PDF, HTML, JATS XML) and produces high-quality structured markdown with provenance tracking. The goal is **better extraction quality than raw pymupdf4llm**, measured on real documents.

## What We Have (Two Halves That Need Connecting)

### Half A: Extraction Quality (proven, in `src/agentic_mbse/extraction/`)

A 4-layer extraction pipeline built over months of iteration on real fusion energy papers:

| Layer | Module | What It Does | Status |
|-------|--------|--------------|--------|
| **1. Backend** | `pymupdf_backend.py` | PyMuPDF4LLM with custom academic header detector, page markers, image extraction | Working |
| **1. Backend** | `docling_backend.py` | ML-based extraction with table structure detection (subprocess, OOM-safe) | Working |
| **1. Backend** | `pandoc_backend.py` | Best-in-class DOCX extraction | Working |
| **1b. Postprocess** | `postprocess.py` | Header promotion, page number stripping, running header removal, ligature repair, noise rejection | Working |
| **2. Tables** | `table_extraction.py` | GMFT table detection + DataFrame→pipe table rendering, per-page timeouts | Working, optional dep |
| **2b. Quality gates** | `quality_gates.py` | Broken table detection, garbled equation detection, produces RepairRequests | Working |
| **3. Structure** | `claude_structure.py` | Claude-assisted heading detection via page images + markdown chunks | Working, needs Claude CLI |
| **4. AI Repair** | `ai_repair.py` | Per-region repair with cross-validation (numbers must be preserved) | Working, needs Claude CLI |

**Key insight from real-world testing**: The ARIES Cost Account paper has 137 tables with the old pipeline, 0 with raw pymupdf4llm. Postprocessing alone gives the Helios paper 52 headings vs 1 without it. These layers do real work.

### Half B: Routing/Provenance (new, in `src/doc_ingest/`)

Infrastructure for multi-source discovery, quality-ordered extraction, and failure tracking:

| Component | Module | What It Does | Status |
|-----------|--------|--------------|--------|
| **SourceRouter** | `source_router.py` | Coordinates discovery→extraction→classification→persistence | Working |
| **Orchestrator** | `extraction_orchestrator.py` | Iterates sources by quality tier, records all attempts | Working |
| **Converters** | `converters/*.py` | **BROKEN**: Naive wrappers that ignore Half A entirely | Needs rewrite |
| **Provenance** | `provenance_manager.py` | Atomic JSON provenance records per document | Working |
| **Discovery** | `source_discoverer.py` | Stub — returns mock sources for DOIs, real for local files | Stub only |
| **Triage** | `cli.py` | Batch processing, triage reports, retry logic | Working |
| **Cache** | `discovery_cache.py` | TTL-based source discovery cache | Working |
| **WebFetcher** | `web_fetcher.py` | HTTP(S)/local file fetching with size limits | Working |
| **Types** | `types.py` | DocumentIdentifiers, SourceCandidate, ProvenanceRecord, etc. | Working |

### The Gap

The PDF converter in Half B (`converters/pdf_converter.py`) calls raw `pymupdf4llm.to_markdown()`. It does NOT use:
- The custom academic header detector
- Postprocessing (header promotion, noise rejection, ligature repair)
- GMFT table extraction
- Claude structure repair
- AI quality repair with cross-validation

**This is why the new pipeline produces worse results than the old one.**

## Architecture: Connect The Halves

```
                    doc_ingest routing layer
                    ========================
  identifier → SourceDiscoverer → SourceRouter → ExtractionOrchestrator
                                                        |
                                            ConverterRegistry.get(format)
                                                        |
                                        ┌───────────────┼───────────────┐
                                        ▼               ▼               ▼
                                  PDFConverter    HTMLConverter    JATSConverter
                                        |               |               |
                    ════════════════════╪═══════════════╪═══════════════╪════
                    existing extraction pipeline        │               │
                                        |               │               │
                                   Layer 1: pymupdf_backend.extract()   │
                                        |               │               │
                                   Layer 1b: postprocess()              │
                                        |               │               │
                                   Layer 2: GMFT tables (if available)  │
                                        |               │               │
                                   Quality gates        │               │
                                        |               │               │
                                   Layer 3: Claude structure (optional)  │
                                        |               │               │
                                   Layer 4: AI repair (optional)        │
                                        |               │               │
                                        ▼               ▼               ▼
                                    ConversionResult (markdown + quality_flags)
                                        |
                                   ProvenanceManager → provenance.json
                                   ResultWriter → output.md, summary.json
```

**The PDF converter should delegate to the existing extraction pipeline, not reimplement it.**

HTML and JATS converters are genuinely new formats the old pipeline doesn't handle — those are fine as standalone implementations, but they also need real-world testing.

## What We Know vs. What We Don't

### Known (measured on 5 fusion-tea papers)

| Fact | Evidence |
|------|----------|
| Raw pymupdf4llm loses all GMFT tables | ARIES: 137→0 tables |
| Postprocessing adds significant heading structure | Helios: 1→52 headings |
| Character counts are ~3-8% lower without postprocessing | All 5 papers |
| The converter registration bug means the pipeline was never tested end-to-end | Every extraction failed with `unsupported_format` until manually fixed |
| All 187 unit tests pass against mocks, proving nothing about real quality | Tests mock all converter internals |

### Unknown (needs empirical testing)

| Question | How To Answer |
|----------|---------------|
| Does Layer 1 + postprocess alone close most of the quality gap? | Run test harness, compare metrics |
| Is GMFT actually needed or does pymupdf4llm `table_strategy="lines"` handle most tables? | A/B test on table-heavy papers |
| How much does Claude structure repair improve results on our corpus? | Run with/without, measure heading counts |
| Does the HTML converter produce useful output on real arXiv papers? | Fetch a real arXiv HTML page and run it |
| Does the JATS converter produce useful output on real JATS XML? | Fetch a real PMC JATS file and run it |
| What's the quality ceiling for PDF-only extraction (no structured sources)? | Run full pipeline on diverse PDFs |
| Are there classes of papers where the pipeline fails badly? | Expand test corpus beyond fusion energy |

## Test Harness Design

### Principles

1. **Run real documents, always.** No more mocked converters for quality testing.
2. **Measure before and after every change.** Capture metrics, diff them.
3. **Expand the corpus continuously.** 5 papers is a start, not an end.
4. **Track quality metrics, not just pass/fail.** Headings, tables, math, content volume.
5. **Compare against baseline.** The existing fusion-tea extractions ARE the baseline.

### Quality Metrics (per document)

```python
@dataclass
class ExtractionMetrics:
    char_count: int           # Total characters in output
    heading_count: int        # Lines starting with #
    heading_depth: dict       # {level: count} e.g. {2: 5, 3: 12}
    table_row_count: int      # Lines matching |...|...|
    math_symbol_count: int    # Unicode math symbols found
    figure_ref_count: int     # "Figure N" or "Fig. N" references
    equation_ref_count: int   # "Equation N" or "Eq. N" references
    page_marker_count: int    # <!-- PAGE:N --> markers (structure preservation)
    empty_line_ratio: float   # Whitespace bloat indicator
    extraction_time_seconds: float
```

### Test Corpus Structure

```
tests/corpus/
  papers.jsonl              # Registry: {slug, pdf_path, doi, has_tables, has_math, ...}
  baseline/                 # Existing fusion-tea extractions (ground truth)
    hawker_2020/
      full_document.md      # Copy from fusion-tea knowledge/sources/
      metrics.json           # Pre-computed metrics
    aries_cost_account/
      ...
  current/                  # Latest extraction output (gitignored)
    hawker_2020/
      output.md
      metrics.json
      provenance.json
  reports/                  # Comparison reports (committed)
    LATEST.md               # Most recent comparison
```

### Test Flow

```bash
# 1. Run extraction on all corpus papers
uv run pytest tests/test_corpus.py --run-corpus

# 2. Compare against baseline
uv run pytest tests/test_corpus.py --compare-baseline

# Output:
# hawker_2020:     headings 14→14 (=)  tables 0→0 (=)    chars 60147→60832 (+1.1%)
# aries_cost:      headings 66→102 (+55%)  tables 0→137 (+137)  chars 262880→286314 (+8.9%)
# helios_design:   headings 1→52 (+5100%)  tables 25→25 (=)   chars 142528→145333 (+2.0%)
```

### Expanding The Corpus

Every time you add a paper:
1. Add entry to `papers.jsonl` with metadata (has_tables, has_math, subject area)
2. Run extraction to populate `current/`
3. If quality is acceptable, copy to `baseline/` to lock in as ground truth
4. Run full comparison to check for regressions

Papers should cover diverse categories:
- Table-heavy (cost analyses, data papers)
- Math-heavy (physics, engineering)
- Figure-heavy (experimental results)
- Long documents (100+ pages)
- Scanned PDFs (OCR boundary)
- Multi-column layouts
- Conference proceedings vs journal articles

## Constraints

1. **No mocked quality tests.** Unit tests for routing/provenance logic can mock. Quality tests MUST use real documents.
2. **Measure, don't guess.** Every change must show metrics before and after.
3. **The existing pipeline is the bar to clear.** If we can't beat or match the fusion-tea extractions, we haven't improved anything.
4. **Incremental layers.** Wire in postprocessing first (pure functions, no deps). Then GMFT. Then Claude layers. Measure after each.
5. **Don't break routing.** The provenance/discovery/triage infrastructure works. Don't rewrite it.

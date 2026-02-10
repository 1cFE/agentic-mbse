# Document Ingestion Implementation Plan

**Last Updated**: 2026-02-09
**Status**: Planning iteration complete — ready to start Phase 1 (Test Harness)

---

## Executive Summary

This project has **two working halves that need connecting**:

1. **Proven extraction pipeline** (`src/agentic_mbse/extraction/`) — 4-layer PDF extraction with quality gates, tested on real papers
2. **Routing infrastructure** (`src/doc_ingest/`) — Source discovery, multi-format converters, provenance tracking, triage reporting

**The Problem**: The PDF converter in the routing layer uses raw `pymupdf4llm.to_markdown()`, completely ignoring the proven extraction pipeline. Real-world testing shows **ARIES paper goes from 137 tables → 0 tables**. Helios paper goes from **52 headings → 1 heading**.

**The Solution**: Four specifications in `specs/` directory define the path forward. This plan breaks them into **concrete, sized tasks** with explicit verification.

---

## Specifications Overview

| Spec | Priority | Purpose | Status |
|------|----------|---------|--------|
| **00-test-harness.md** | 🔴 FIRST | Real-world test corpus with metrics, baseline comparison | Not started |
| **01-wire-existing-pipeline.md** | 🟡 SECOND | Connect extraction layers to PDF converter | Not started |
| **02-real-source-discovery.md** | 🟢 THIRD | OpenAlex/arXiv/PMC API integration | Not started |
| **03-fusion-tea-integration.md** | 🔵 LAST | Replace subprocess calls with Python API | Not started |

**Critical Rule**: Every task must be measured against the test harness. No implementation without verification.

---

## Phase 1: Test Harness (Spec 00) — PRIORITY 1

**Goal**: Build real-world test corpus and metrics infrastructure to measure quality objectively.

**Why First**: Without this, we can't prove extraction quality improvements. All 187 existing tests use mocks.

### [DONE] TASK-TH-001: Create test corpus infrastructure

**Files to create**:
- `tests/corpus/papers.jsonl` — Registry of 5 test papers
- `tests/corpus/metrics.py` — `ExtractionMetrics` dataclass and computation functions
- `tests/corpus/pdfs/` — Directory for test PDFs (gitignored)
- `tests/corpus/baseline/` — Baseline extractions from fusion-tea
- `tests/corpus/current/` — Current pipeline results (gitignored)

**Requirements**:
- Copy 5 PDFs from fusion-tea: `hawker_2020`, `aries_cost_account`, `helios_design`, `hsu_2020`, `delene_2001`
- Copy baseline extractions: `knowledge/sources/{slug}/full_document.md` → `tests/corpus/baseline/{slug}/full_document.md`
- Implement `compute_metrics(markdown: str, elapsed: float) → ExtractionMetrics`
- Implement `compare_metrics(baseline: ExtractionMetrics, current: ExtractionMetrics) → dict`

**Metrics to compute**:
```python
@dataclass
class ExtractionMetrics:
    char_count: int
    heading_count: int
    heading_by_level: dict[int, int]  # {2: 5, 3: 12, ...}
    table_row_count: int               # Lines matching |...|...|
    math_symbol_count: int
    figure_ref_count: int
    extraction_time_seconds: float
```

**Verification**: `python tests/corpus/metrics.py` computes metrics for a sample markdown file

**Size**: ~150 LOC, 2-3 files
**Dependencies**: fusion-tea baseline data (external)
**Blocks**: TASK-TH-002

---

### TASK-TH-002: Implement corpus test runner

**Files to create**:
- `tests/test_corpus.py` — Pytest suite with `@pytest.mark.corpus` decorator

**Requirements**:
- `test_all_papers_extract_successfully()` — Every paper produces non-empty output
- `test_no_quality_regression_vs_baseline()` — >10% loss on any metric = failure
- `test_table_heavy_papers_have_tables()` — Papers with `has_tables=true` have `table_row_count > 0`
- `test_heading_structure_present()` — Every paper has `heading_count >= 3`
- Tests only run with `pytest tests/test_corpus.py --run-corpus` flag
- Save extraction results to `tests/corpus/current/{slug}/` with provenance

**Verification**: `pytest tests/test_corpus.py --run-corpus` runs all 4 tests

**Size**: ~200 LOC, 1 file
**Dependencies**: TASK-TH-001
**Blocks**: TASK-TH-003

---

### TASK-TH-003: Create comparison report CLI

**Files to create**:
- `tests/corpus/compare.py` — Standalone script for human-readable comparison

**Requirements**:
- Load baseline metrics from `tests/corpus/baseline/{slug}/metrics.json`
- Compute current metrics from `tests/corpus/current/{slug}/full_document.md`
- Generate table:
  ```
  Document              Headings    Tables      Chars       Time
                        base→curr   base→curr   base→curr
  hawker_2020           11→14 (+3)  0→0 (=)     60k→60k     9.3s
  aries_cost_account    102→66 (-35%) 137→0 (!!!) 286k→263k  22.6s
  ```
- Flag regressions: `(!!!)` for >35% loss, `(%)` for quantified loss
- Section at end: `REGRESSIONS:` listing flagged problems

**Verification**: `python tests/corpus/compare.py` produces readable markdown report

**Size**: ~150 LOC, 1 file
**Dependencies**: TASK-TH-001, TASK-TH-002
**Blocks**: TASK-WP-001

---

## Phase 2: Wire Extraction Pipeline (Spec 01) — PRIORITY 2

**Goal**: Replace raw `pymupdf4llm` calls in PDF converter with proven 4-layer extraction pipeline.

**Why Second**: Test harness must exist first to measure quality improvements.

### TASK-WP-001: Wire Layer 1 (Backend + Postprocess)

**Files to modify**:
- `src/doc_ingest/converters/pdf_converter.py`

**Current implementation** (broken):
```python
def convert(self, content: bytes) -> ConversionResult:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    md_text = pymupdf4llm.to_markdown(tmp_path)
    # ... quality flags from regex heuristics ...
```

**New implementation**:
```python
from agentic_mbse.extraction.pymupdf_backend import extract
from agentic_mbse.extraction.postprocess import postprocess

def convert(self, content: bytes) -> ConversionResult:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    # Create temp output directory
    with tempfile.TemporaryDirectory() as tmp_out:
        tmp_out_path = Path(tmp_out)

        # Layer 1: pymupdf_backend (custom header detector)
        extract(input_path=tmp_path, output_dir=tmp_out_path)
        md_path = tmp_out_path / "full_document.md"
        md_text = md_path.read_text()

        # Layer 1b: postprocess (header promotion, ligatures, noise)
        md_text = postprocess(md_text, images_dir=tmp_out_path / "images")

        # Compute quality flags from ACTUAL output (not heuristics)
        quality_flags = self._compute_quality_flags(md_text, tmp_path)
```

**Requirements**:
- Remove regex heuristics for quality flags
- Compute flags from actual extraction output:
  - `has_tables` = markdown contains pipe tables OR PDF has table structures
  - `heading_structure_detected` = markdown has `#` headers (postprocessing promoted them)
  - `has_math` = Unicode math symbols present
  - `has_figures` = images exist in output directory
- Preserve `<!-- PAGE:N -->` markers (required by quality_gates in Layer 2)
- Handle bytes → temp file path conversion

**Acceptance Criteria** (from Spec 01):
- [ ] Heading counts match or exceed baseline for all 5 papers
- [ ] No table regression (tables shouldn't get worse)
- [ ] Character counts within 5% of baseline
- [ ] Run `pytest tests/test_corpus.py --run-corpus` after implementation
- [ ] Run `python tests/corpus/compare.py` and verify no regressions

**Verification**: Test harness shows quality improvement on all 5 papers

**Size**: ~200 LOC changes in 1 file
**Dependencies**: TASK-TH-003 (test harness complete)
**Blocks**: TASK-WP-002

---

### TASK-WP-002: Wire Layer 2 (GMFT table enhancement)

**Files to modify**:
- `src/doc_ingest/converters/pdf_converter.py`

**Requirements**:
- Check `is_gmft_available()` before attempting Layer 2
- If available:
  1. Call `quality_gates.detect_problems(markdown, pdf_path)` → list of `RepairRequest`
  2. Filter for table repair requests
  3. Call `table_extraction.enhance_tables(markdown, pdf_path, repair_requests)` → repaired markdown
  4. Splice repaired tables back into markdown
- Update `tables_likely_corrupted` flag based on quality_gates detection
- Keep layer optional (graceful skip if gmft not installed)

**Acceptance Criteria** (from Spec 01):
- [ ] Papers marked `has_tables=true` have `table_row_count > 0`
- [ ] ARIES Cost Account has >100 table rows (baseline: 137)
- [ ] Table content spot-check: numbers in tables are correct
- [ ] Run test harness and comparison report after implementation

**Verification**: Test harness shows table counts restored on table-heavy papers

**Size**: ~100 LOC changes in 1 file
**Dependencies**: TASK-WP-001
**Blocks**: None (Layers 3-4 are optional, deferred)

---

## Phase 3: Real Source Discovery (Spec 02) — PRIORITY 3

**Goal**: Replace stubbed source discovery with real OpenAlex, arXiv, and PMC API integrations.

**Why Third**: Source discovery is useless if converters produce bad output. Fix extraction quality first.

### TASK-SD-001: Pre-implementation API validation

**Manual testing** (before writing code):
1. For each test paper DOI, query OpenAlex and record what sources are available
2. Download one real arXiv HTML page, run through `ArXivHTMLConverter`, inspect output
3. Download one real JATS XML file, run through `JATSPandocConverter`, inspect output

**Requirements**:
- Document findings in `tests/corpus/discovery_validation.md`
- Identify which test papers have structured alternatives (JATS, arXiv HTML)
- Verify converters produce acceptable output on real input (not synthetic test data)
- If converters fail on real input, fix converters before proceeding to TASK-SD-002

**Verification**: Documentation shows which papers have structured sources + converter quality assessment

**Size**: Manual testing + 1 documentation file
**Dependencies**: TASK-WP-002 (extraction quality proven)
**Blocks**: TASK-SD-002

---

### TASK-SD-002: Implement OpenAlex API integration

**Files to modify**:
- `src/doc_ingest/source_discoverer.py`

**Files to create**:
- `src/doc_ingest/api_clients/openalex.py` (optional, could inline in discoverer)

**Requirements**:
- Implement `OpenAlexClient.query(doi: str) → list[SourceCandidate]`
- Parse OpenAlex response:
  - `open_access.oa_url` (primary structured source)
  - `primary_location.landing_page_url` (publisher page)
  - `host_venue.url` (journal homepage)
  - `best_oa_location` (fallback)
- Return sources sorted by quality tier (JATS XML=1, HTML=3, PDF=4)
- Handle API errors gracefully (return empty list + error message)
- Add 100ms delay between API calls (rate limiting courtesy)
- Cache results via existing `DiscoveryCache`

**Verification**:
```python
result = discoverer.discover(DocumentIdentifiers(doi="10.1098/rsta.2020.0053"))
assert len(result.sources) > 0
assert result.sources[0].quality_tier <= 4  # At least PDF
```

**Size**: ~150 LOC in 1-2 files
**Dependencies**: TASK-SD-001
**Blocks**: TASK-SD-003

---

### TASK-SD-003: Implement arXiv API integration

**Files to modify**:
- `src/doc_ingest/source_discoverer.py`

**Files to create**:
- `src/doc_ingest/api_clients/arxiv.py` (optional)

**Requirements**:
- Implement `ArXivClient.query(arxiv_id: str) → list[SourceCandidate]`
- Check if HTML version exists via HEAD request to `https://arxiv.org/html/{arxiv_id}`
- Return sources in quality order:
  - HTML version (tier 2) if exists
  - PDF version (tier 4) always available
- Normalize arXiv ID format (1234.5678 vs arXiv:1234.5678)

**Verification**:
```python
result = discoverer.discover(DocumentIdentifiers(arxiv_id="1234.5678"))
assert len(result.sources) >= 1  # At least PDF
html_sources = [s for s in result.sources if s.format == "arxiv_html"]
# If HTML exists, it should be first (tier 2 < tier 4)
```

**Size**: ~100 LOC in 1-2 files
**Dependencies**: TASK-SD-002
**Blocks**: TASK-SD-004

---

### TASK-SD-004: Implement PMC API integration

**Files to modify**:
- `src/doc_ingest/source_discoverer.py`

**Files to create**:
- `src/doc_ingest/api_clients/pmc.py` (optional)

**Requirements**:
- Implement `PMCClient.query(pmc_id: str) → list[SourceCandidate]`
- Use endpoint: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_id}&rettype=xml`
- Return JATS XML source (tier 1 — highest quality)
- Handle PMC API errors and rate limiting

**Verification**:
```python
result = discoverer.discover(DocumentIdentifiers(pmc_id="PMC1234567"))
assert result.sources[0].format == "jats_xml"
assert result.sources[0].quality_tier == 1  # Structured XML
```

**Size**: ~80 LOC in 1-2 files
**Dependencies**: TASK-SD-003
**Blocks**: TASK-SD-005

---

### TASK-SD-005: Verify quality-ordered routing

**Testing requirements**:
- Run test harness on papers with structured alternatives
- Measure extraction quality: structured source vs PDF
- Verify `ExtractionOrchestrator` tries sources in quality order
- Verify first successful extraction wins (early exit)
- Compare metrics: JATS/HTML should produce >= PDF quality

**Acceptance Criteria** (from Spec 02):
- [ ] `SourceDiscoverer.discover(DocumentIdentifiers(doi="10.1098/rsta.2020.0053"))` returns real sources
- [ ] At least one structured source (HTML or JATS) discovered for papers that have one
- [ ] Quality-tier ordering routes to structured source first
- [ ] Extraction from structured source produces quality >= PDF extraction
- [ ] Discovery cache prevents re-querying same DOI
- [ ] API errors handled gracefully (recorded in provenance, falls back to PDF)

**Verification**: Test harness comparison shows structured sources produce acceptable quality

**Size**: Testing + documentation
**Dependencies**: TASK-SD-004
**Blocks**: TASK-FT-001

---

## Phase 4: Fusion-TEA Integration (Spec 03) — PRIORITY 4

**Goal**: Replace subprocess-based CLI calls with direct Python API in fusion-tea `zotero_ingest.py`.

**Why Last**: Only proceed once extraction quality and source discovery are proven.

### TASK-FT-001: Replace subprocess with Python API

**Files to modify** (in fusion-tea repository):
- `scripts/zotero_ingest.py`

**Current implementation**:
```python
subprocess.run([
    "uv", "run", "agentic-mbse", "extract",
    pdf_path, "--output", output_dir
])
```

**New implementation**:
```python
from doc_ingest.source_router import SourceRouter
from doc_ingest.types import DocumentIdentifiers
from doc_ingest.cli import create_pipeline

router, writer = create_pipeline(output_dir=Path("output/"))
result = router.extract(
    identifiers=DocumentIdentifiers(doi=doi, local_path=pdf_path),
    output_dir=output_dir,
    format_override=None
)

if result.markdown is not None:
    # Success or partial
    print(f"Extracted: {len(result.markdown)} chars")
else:
    # Failed
    print(f"Failed: {result.provenance.failure_category}")
```

**Requirements**:
- Add imports from `doc_ingest` package
- Parse Zotero API response into `DocumentIdentifiers`
- Handle `ExtractionResult` and write to fusion-tea's expected location
- Remove subprocess calls and CLI argument parsing

**Verification**:
- `python scripts/zotero_ingest.py --dry-run` runs without import errors
- End-to-end: Ingest 1 paper via Zotero API, produces `output.md` + `provenance.json`

**Size**: ~50 LOC changes in fusion-tea
**Dependencies**: TASK-SD-005
**Blocks**: TASK-FT-002

---

### TASK-FT-002: Enrich MANIFEST.jsonl with provenance

**Files to modify** (in fusion-tea repository):
- `scripts/zotero_ingest.py`

**Current MANIFEST.jsonl** (basic):
```json
{
  "document_id": "doi:10.1234/example",
  "created_at": "2026-02-09T12:00:00Z"
}
```

**New MANIFEST.jsonl** (enriched):
```json
{
  "document_id": "doi:10.1234/example",
  "outcome": "success",
  "failure_category": null,
  "converter_used": "PyMuPDF4LLMConverter",
  "created_at": "2026-02-09T12:00:00Z",
  "total_elapsed_seconds": 12.5,
  "num_sources_discovered": 3,
  "num_extraction_attempts": 2
}
```

**Requirements**:
- Read provenance fields from `result.provenance`
- Include `outcome` (success/partial/failed)
- Include `failure_category` (typed category or null)
- Include `converter_used` (which converter produced output)
- Include timing and attempt statistics
- Maintain backward compatibility with existing MANIFEST consumers

**Verification**: MANIFEST.jsonl includes all new fields after batch run

**Size**: ~30 LOC changes in fusion-tea
**Dependencies**: TASK-FT-001
**Blocks**: TASK-FT-003

---

### TASK-FT-003: Auto-generate triage report

**Files to modify** (in fusion-tea repository):
- `scripts/zotero_ingest.py`

**Requirements**:
- After batch run completes, call `_generate_triage_report(output_dir, report_path)`
- Report groups failures by `failure_category`
- Lists discovery errors
- Provides actionable remediation steps
- Only generate if there are failures/partials

**Verification**: Batch run with failures produces `triage_report.md`

**Size**: ~20 LOC changes in fusion-tea
**Dependencies**: TASK-FT-002
**Blocks**: None (integration complete)

---

## Success Criteria Summary

### Phase 1 (Test Harness) — COMPLETE when:
- [ ] 5 test papers in corpus with baseline extractions
- [ ] `pytest tests/test_corpus.py --run-corpus` runs successfully
- [ ] `python tests/corpus/compare.py` produces readable report
- [ ] Metrics computation validates against known baseline

### Phase 2 (Extraction Pipeline) — COMPLETE when:
- [ ] Step 1 (Backend + Postprocess): Headings match/exceed baseline, chars within 5%
- [ ] Step 2 (GMFT): Table-heavy papers have >100 table rows
- [ ] Test harness shows no regressions on all 5 papers
- [ ] Comparison report shows quality parity or improvement

### Phase 3 (Source Discovery) — COMPLETE when:
- [ ] OpenAlex, arXiv, PMC APIs return real sources
- [ ] Discovery cache prevents re-querying
- [ ] Quality-ordered routing attempts structured sources first
- [ ] Structured sources produce >= PDF quality (measured)
- [ ] API errors handled gracefully with provenance tracking

### Phase 4 (Fusion-TEA Integration) — COMPLETE when:
- [ ] `python scripts/zotero_ingest.py --dry-run` runs without errors
- [ ] End-to-end extraction produces enriched MANIFEST.jsonl
- [ ] Triage report generated for batch runs with failures
- [ ] Quality >= existing fusion-tea extractions (no regressions)

---

## Task Dependency Graph

```
Phase 1: Test Harness
TH-001 (corpus infra)
  └─→ TH-002 (test runner)
        └─→ TH-003 (comparison report)
              └─→ Phase 2

Phase 2: Wire Extraction Pipeline
WP-001 (Layer 1: backend+postprocess)
  └─→ WP-002 (Layer 2: GMFT tables)
        └─→ Phase 3

Phase 3: Source Discovery
SD-001 (API validation)
  └─→ SD-002 (OpenAlex)
        └─→ SD-003 (arXiv)
              └─→ SD-004 (PMC)
                    └─→ SD-005 (verify routing)
                          └─→ Phase 4

Phase 4: Fusion-TEA Integration
FT-001 (Python API)
  └─→ FT-002 (MANIFEST enrichment)
        └─→ FT-003 (triage report)
```

---

## Deferred / Out of Scope

**Layer 3 (Claude Structure Repair)** — Deferred until quality gap measured after Layer 2. From Spec 01:
- MAY add `--enhance` flag to enable optional Claude layers
- MAY wire in `claude_structure.py` if Step 1-2 gap remains large
- Decision: Measure first, decide after

**Layer 4 (AI Repair)** — Deferred, same rationale as Layer 3.

**Additional Converters** — Current formats (PDF, HTML, JATS, DOCX) cover 90%+ of academic corpus. Future: LaTeX, Word, RTF.

**Concurrent Extraction** — Single-threaded batch processing is acceptable for current scale. Future: parallel extraction with worker pool.

**OCR Preprocessing** — Out of scope. Papers with `needs_ocr` failure category are flagged for manual handling.

---

## How to Use This Plan

1. **Start with Phase 1, Task TH-001** — Always begin with test harness infrastructure
2. **Complete tasks in order** — Dependencies are explicit; don't skip ahead
3. **Measure after every task** — Run test harness, check comparison report
4. **Update this plan** — Mark tasks complete, document learnings, adjust priorities
5. **Stop if quality doesn't improve** — If a task doesn't improve metrics, investigate before continuing

**Critical rule**: No task is "done" until verified by test harness metrics.

---

## Verification Checkpoints

| After Task | Verification Command | Expected Outcome |
|------------|---------------------|------------------|
| TH-001 | `python tests/corpus/metrics.py` | Computes metrics for sample markdown |
| TH-002 | `pytest tests/test_corpus.py --run-corpus` | 4 tests run (may fail initially) |
| TH-003 | `python tests/corpus/compare.py` | Readable comparison report |
| WP-001 | `pytest tests/test_corpus.py --run-corpus && python tests/corpus/compare.py` | Headings/chars improved vs raw pymupdf4llm |
| WP-002 | Same as WP-001 | Table counts restored on table-heavy papers |
| SD-002 | Unit test for OpenAlex discovery | Returns real sources for test DOI |
| SD-003 | Unit test for arXiv discovery | Returns HTML + PDF in quality order |
| SD-004 | Unit test for PMC discovery | Returns JATS XML source |
| SD-005 | Test harness on structured sources | Quality >= PDF extraction |
| FT-001 | `python scripts/zotero_ingest.py --dry-run` (in fusion-tea) | No import errors |
| FT-002 | Inspect MANIFEST.jsonl after batch run | Includes outcome, failure_category, converter_used |
| FT-003 | Check for triage_report.md after batch with failures | Report generated with grouped failures |

---

## Known Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Baseline extractions from fusion-tea not accessible | Phase 1 blocked | Coordinate with fusion-tea maintainer to export baseline data |
| GMFT not installable in environment | Layer 2 blocked | Document installation steps; provide fallback instructions |
| OpenAlex API unavailable/changed | Phase 3 blocked | Cache API responses; implement fallback to PDF-only extraction |
| Structured source converters produce garbage on real input | Phase 3 wasted effort | TASK-SD-001 validates converters BEFORE implementing discovery |
| Quality improvements not measurable | Entire project in doubt | Test harness (Phase 1) must complete first to define "quality" |

---

## Gap Analysis Results (2026-02-09)

### Implementation State
- ✅ **Routing infrastructure**: Complete (2,507 LOC across 17 modules)
  - 5 converters (PDF, arXiv HTML, Publisher HTML, JATS, DOCX)
  - Full CLI (extract, extract-batch, triage-report, retry-failed, clear-cache)
  - Provenance tracking, discovery caching, result writing
  - 187 unit tests passing (all using mocks)
- ❌ **Test corpus (Phase 1)**: Not started — `tests/corpus/` doesn't exist
- ❌ **Extraction pipeline wiring (Phase 2)**: Not started — PDF converter uses raw `pymupdf4llm`, ignores proven layers
- ⚠️ **Source discovery (Phase 3)**: Stubbed — creates mock URLs, no real API integration
- ❌ **Fusion-TEA integration (Phase 4)**: Not started — still using subprocess calls

### Critical Finding
**PDF converter quality problem confirmed**:
- Current: `pymupdf4llm.to_markdown()` (bypasses 4-layer extraction pipeline)
- Impact: Real papers show 98% heading loss, 100% table loss
- No imports from `agentic_mbse.extraction` package exist in `src/doc_ingest/`

### Next Steps
1. **START HERE**: TASK-TH-001 (test corpus infrastructure)
2. Obtain baseline extractions from fusion-tea (5 papers: hawker_2020, aries_cost_account, helios_design, hsu_2020, delene_2001)
3. Implement metrics computation (`ExtractionMetrics` dataclass)
4. Proceed through phases sequentially

---

## Notes for Future Sessions

- **Branch status**: Currently on `ralph/doc-ingest` branch
- **Recent work**: Batch CLI completed (TASK-DI-010); specs written; planning iteration complete
- **Test coverage**: 187 unit tests passing (mocks) — zero real-world validation
- **Blockers**: Need fusion-tea baseline data to start Phase 1
- **Key files to read**:
  - `specs/00-test-harness.md` — Test harness requirements (Phase 1 blueprint)
  - `specs/01-wire-existing-pipeline.md` — Layer-by-layer wiring (Phase 2 blueprint)
  - `AGENTS.md` — Current state documentation
  - `DESIGN.md` — Architecture overview

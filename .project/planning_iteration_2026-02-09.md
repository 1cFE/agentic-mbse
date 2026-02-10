# Planning Iteration — 2026-02-09

## Summary

Completed comprehensive spec-driven gap analysis for document ingestion pipeline. Explored all 4 specifications, analyzed current implementation state (~2,500 LOC), and validated that the existing IMPLEMENTATION_PLAN.md is accurate and complete.

---

## Specifications Analyzed

| Spec | Purpose | Status | Dependencies |
|------|---------|--------|--------------|
| **00-test-harness.md** | Real-world test corpus with metrics comparison | Not started | External: fusion-tea baseline data |
| **01-wire-existing-pipeline.md** | Connect proven extraction layers to PDF converter | Not started | Spec 00 (test harness) |
| **02-real-source-discovery.md** | OpenAlex/arXiv/PMC API integration | Stubbed (mock URLs) | Spec 01 (extraction quality) |
| **03-fusion-tea-integration.md** | Replace subprocess with Python API | Not started | Spec 02 (source discovery) |

---

## Implementation State

### ✅ Complete (Production-Ready)
- **Routing infrastructure**: 2,507 LOC across 17 modules
  - Type system (9 failure categories, quality flags, provenance)
  - 5 converters: PDF, arXiv HTML, Publisher HTML, JATS (Pandoc), DOCX (Pandoc)
  - CLI commands: extract, extract-batch, triage-report, retry-failed, clear-cache
  - Pipeline components: WebFetcher, ExtractionOrchestrator, OutcomeClassifier, ProvenanceManager, ResultWriter, SourceRouter
  - Discovery caching with TTL
  - 187 unit tests passing (all using mocks)

### ❌ Missing (Critical Gaps)
- **Test corpus** (`tests/corpus/`): Doesn't exist; no real-world validation
- **Extraction pipeline wiring**: PDF converter uses raw `pymupdf4llm.to_markdown()`, completely bypasses proven 4-layer extraction pipeline in `agentic_mbse.extraction/`
  - No imports from `agentic_mbse.extraction` in `src/doc_ingest/`
  - Quality flags computed from regex heuristics, not actual output
  - Real-world impact: 98% heading loss, 100% table loss on test papers
- **Source discovery APIs**: Local files work; DOI/arXiv/PMC create mock URLs (stubbed)
- **Fusion-TEA integration**: Still using subprocess calls, not Python API

---

## Critical Findings

### The Core Problem
**Two working halves, not connected**:
1. Proven extraction pipeline (`agentic_mbse.extraction/`) — 4 layers, tested on real papers
2. Routing infrastructure (`doc_ingest/`) — converters, provenance, batch processing

**The gap**: PDF converter in routing layer ignores extraction pipeline entirely.

### Quality Impact (Real Measurements)
- **Helios Design paper**: 52 headings → 1 heading (98% loss)
- **ARIES Cost Account**: 137 tables → 0 tables (100% loss)

### Why This Matters
All 187 tests pass because they use mocks. Real-world usage will produce garbage output until extraction pipeline is wired in.

---

## IMPLEMENTATION_PLAN.md Assessment

### Verdict: ✅ Plan is Accurate and Complete

**Structure validated**:
- 16 tasks across 4 phases
- Each task: ~150-200 LOC, concrete, sized appropriately
- Dependencies explicit, priorities correct
- Verification criteria clear and measurable
- No false negatives (plan doesn't assume work is done when it isn't)

**No changes needed** to task breakdown. Plan is ready for execution.

---

## Prioritized Task List (Next Actions)

### Phase 1: Test Harness (PRIORITY 1)
1. **TASK-TH-001**: Create test corpus infrastructure
   - Create `tests/corpus/` directory structure
   - Copy 5 baseline PDFs from fusion-tea
   - Copy baseline extractions to `tests/corpus/baseline/{slug}/`
   - Implement `ExtractionMetrics` dataclass
   - Implement `compute_metrics()` and `compare_metrics()` functions
   - **Verified by**: `python tests/corpus/metrics.py` computes metrics
   - **Size**: ~150 LOC, 2-3 files
   - **Blocker**: Need fusion-tea baseline data

2. **TASK-TH-002**: Implement corpus test runner
   - Create `tests/test_corpus.py` with 4 test methods
   - Add `@pytest.mark.corpus` decorator (opt-in with `--run-corpus` flag)
   - Save results to `tests/corpus/current/{slug}/`
   - **Verified by**: `pytest tests/test_corpus.py --run-corpus` runs all tests
   - **Size**: ~200 LOC, 1 file

3. **TASK-TH-003**: Create comparison report CLI
   - Create `tests/corpus/compare.py` standalone script
   - Generate human-readable table with regressions flagged
   - **Verified by**: `python tests/corpus/compare.py` produces readable report
   - **Size**: ~150 LOC, 1 file

### Phase 2: Wire Extraction Pipeline (PRIORITY 2)
4. **TASK-WP-001**: Wire Layer 1 (Backend + Postprocess)
   - Modify `src/doc_ingest/converters/pdf_converter.py`
   - Replace `pymupdf4llm.to_markdown()` with `extraction.pymupdf_backend.extract()`
   - Add `postprocess()` call for header promotion
   - Compute quality flags from actual output, not heuristics
   - **Acceptance criteria**: Headings match baseline, chars within 5%
   - **Size**: ~200 LOC changes, 1 file

5. **TASK-WP-002**: Wire Layer 2 (GMFT table enhancement)
   - Add `quality_gates.detect_problems()` call
   - Add `table_extraction.enhance_tables()` for table repair
   - Optional layer (graceful skip if gmft unavailable)
   - **Acceptance criteria**: Table-heavy papers have >100 rows
   - **Size**: ~100 LOC changes, 1 file

### Phase 3: Source Discovery (PRIORITY 3)
6. **TASK-SD-001**: Pre-implementation API validation
   - Manual testing: Query OpenAlex for test DOIs
   - Verify converters work on real arXiv HTML, real JATS XML
   - Document findings in `tests/corpus/discovery_validation.md`
   - **Critical**: Fix converters BEFORE implementing API clients

7-10. **TASK-SD-002 through SD-005**: OpenAlex, arXiv, PMC API integration + routing verification

### Phase 4: Fusion-TEA Integration (PRIORITY 4)
11-13. **TASK-FT-001 through FT-003**: Python API, MANIFEST enrichment, triage report

---

## Key Architectural Insights

### Cross-Package Dependencies (Validated)
- **Approach**: Direct imports from `agentic_mbse.extraction` → `doc_ingest.converters`
- **Rationale**: Both in same repo, installed together; simplest approach
- **Path handling**: Must write bytes to temp file (extraction backend expects `Path` input)

### Quality Flag Computation (Design Decision)
- **Current (wrong)**: Regex heuristics on PDF structure
- **Correct**: Compute from actual markdown output after extraction
- **Implementation**: Check for actual `#` headers, `|...|` tables, Unicode math symbols

### Test Harness as Backpressure
- Every task verified by running test harness
- Comparison report shows quality deltas
- Regressions flagged automatically
- No implementation is "done" until metrics improve

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fusion-tea baseline data unavailable | Phase 1 blocked | Coordinate with fusion-tea maintainer; critical blocker |
| GMFT not installable | Layer 2 blocked | Document installation; provide fallback (Layer 1 sufficient) |
| Structured source converters fail on real input | Phase 3 wasted | TASK-SD-001 validates BEFORE coding |
| OpenAlex API changed/unavailable | Phase 3 blocked | Cache responses; graceful fallback to PDF |

---

## Verification Strategy

### Per-Task Verification
- Every task has explicit verification command
- Test harness comparison report required after each Phase 2 task
- Unit tests for API clients (Phase 3)
- End-to-end integration tests (Phase 4)

### Checkpoints Table
See IMPLEMENTATION_PLAN.md lines 575-589 for full verification matrix.

---

## Success Metrics

### Phase 1 Complete When:
- 5 papers in corpus with baseline extractions
- Test runner executes successfully
- Comparison report readable and accurate

### Phase 2 Complete When:
- Headings match or exceed baseline (all 5 papers)
- Table-heavy papers have >100 rows
- Character counts within 5% of baseline
- No regressions on any metric

### Phase 3 Complete When:
- Real API sources discovered for test DOIs
- Quality-ordered routing verified
- Structured sources produce >= PDF quality

### Phase 4 Complete When:
- Python API replaces subprocess calls
- MANIFEST.jsonl enriched with provenance
- Triage report auto-generated
- Quality >= fusion-tea existing extractions

---

## Deferred / Out of Scope

- **Claude structure repair (Layer 3)**: Decision after Layer 2 measurement
- **AI repair (Layer 4)**: Same as Layer 3
- **Additional converters**: LaTeX, Word, RTF (future)
- **Concurrent extraction**: Single-threaded sufficient for now
- **OCR preprocessing**: Flagged for manual handling

---

## Recommendations for Next Session

1. **START with TASK-TH-001** — Do not skip to implementation without test harness
2. **Obtain fusion-tea baseline data** — This is the critical blocker for Phase 1
3. **Follow strict sequencing** — Dependencies matter; don't jump ahead
4. **Measure after every task** — Run test harness, check comparison report
5. **Stop if metrics don't improve** — Investigate before continuing

**Critical rule**: No implementation work proceeds without test harness (Phase 1 complete).

---

## Files Modified This Session

- `IMPLEMENTATION_PLAN.md` — Updated status and gap analysis section
- `.project/planning_iteration_2026-02-09.md` — This document

---

## Agent Context for Resumption

**What was explored**:
- All 4 specs in `specs/` (parallel exploration)
- Current implementation in `src/doc_ingest/` (2,507 LOC inventory)
- Existing IMPLEMENTATION_PLAN.md (validated completeness)
- Gap analysis: what's built vs what's missing

**What was NOT done**:
- No code changes (planning only)
- No test corpus creation (blocked on fusion-tea data)
- No extraction pipeline wiring (Phase 2 requires Phase 1 first)

**Next agent should**:
- Read this planning iteration summary
- Check if fusion-tea baseline data is available
- If available: Start TASK-TH-001
- If not available: Coordinate to obtain baseline data

---

## Planning Iteration Complete ✅

All specifications analyzed, gaps identified, priorities validated. IMPLEMENTATION_PLAN.md is accurate and ready for execution. Next session should begin with Phase 1, Task TH-001.

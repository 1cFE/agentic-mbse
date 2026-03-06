# Requirements & Specifications: PDF Extraction Pipeline (Stage 4)

**Created:** 2026-02-23
**Status:** Draft
**Parent:** `.project/concepts/doc-extraction-development-strategy.md` (Stage 4)
**Branch:** `doc-ingest-clean`

---

## 1. Scope

This document specifies the requirements for designing and implementing the PDF extraction pipeline as production code in `src/agentic_mbse/extraction/`. It covers:

- **In scope:** PDF-to-markdown pipeline, quality gate, per-page routing, GMFT table enhancement, Claude vision enhancement, Pandoc arXiv shortcut, provenance/decision logging, CLI integration, unit and integration tests
- **Out of scope:** HTML/XML structured source converters beyond Pandoc arXiv (Stage 5), source discovery APIs (Stage 5), batch processing and retry logic (Stage 6), triage reports (Stage 6)

Stage 3's winning hypothesis (H5 + H6 pre-check) is the **starting pipeline composition**, not the final one. The design must support iterating on the pipeline — adding new checks, swapping enhancers, adjusting routing logic — without architectural rewrites. This spec defines what the design must achieve, not the specific pipeline shape it must hardcode.

---

## 2. Context

### 2.1 What Exists Today

The existing `src/agentic_mbse/extraction/` module (12 files, ~3,200 LOC) contains:
- Backend extractors: `pymupdf_backend.py`, `docling_backend.py`, `pandoc_backend.py` (DOCX only)
- Quality gates: `quality_gates.py` (full-document, produces `RepairRequest` objects)
- AI repair: `ai_repair.py` (cross-validated Claude repair), `claude_structure.py` (heading detection/insertion)
- Table handling: `table_extraction.py` (GMFT), `table_repair.py` (Claude-based)
- Postprocessing: `postprocess.py` (383 lines, deterministic text transforms)
- Shared types: `base.py` (`ExtractionResult`, `RepairRequest`)
- Index generation: `index.py` (section parsing, INDEX.md generation)

This code follows a three-layer architecture (backend → GMFT → AI repair) that operates on full documents. Stage 3 discovered that **per-page routing** is the correct granularity, and the existing module's interfaces don't match this pattern.

### 2.2 What Stage 3 Proved

The Stage 3 experiments (`tests/corpus/pipelines/`, 6 modules, ~2,300 LOC) demonstrated:

| Pipeline | Heading Avg Error | Table Avg Error | Cost/Doc | Notes |
|----------|--:|--:|--:|---|
| H5 (quality-gated) | 70% | 8% | $0.12 | **Winner** — best composite |
| H1 (pymupdf+GMFT) | 89% | 1% | $0.00 | Best free option |
| H6 (Pandoc shortcut) | 0% | 94% | $0.00 | arXiv papers only |
| Claude vision 1pp | 28% | 1% | $1.46 | Quality ceiling |

The best-performing composition: **H6 pre-check → H5 fallback**. Try Pandoc for arXiv papers first; otherwise run pymupdf4llm base → quality gate → GMFT or Claude per page. This is the starting pipeline — the design must support evolving it as we learn more.

### 2.3 What the Old Branch Got Wrong

The `ralph/doc-ingest` audit (97 commits, ~25,900 lines) identified:
- **Promote-then-demote anti-pattern:** 560 lines of header promotion regex + 170 lines of noise filters to reject false positives
- **Wrong granularity:** Full-document processing instead of per-page routing
- **Premature abstraction:** Interfaces designed before understanding pipeline composition
- **Dormant code:** GMFT, Docling backend, AI repair built but never wired into the active pipeline

### 2.4 What the Table-Image Spike Proved

Before finalizing this spec, a targeted spike tested cropped table images and detection strategies across 5 papers (40 GT tables, ~444 rows). Two rounds of investigation:

**Round 1** (`.project/active/table-image-spike/findings.md`):
- **Claude + cropped images = exact GT match on 4/5 papers** — best table accuracy in any stage
- **GMFT detects but can't extract 7/15 aries tables** — Claude recovers all 7 from the cropped images
- **Multi-pass (vote/resolve, review) adds no value** — Claude should extract independently, never review GMFT output
- **PyMuPDF `find_tables()` does not complement GMFT** — over-detects prose on report-style docs

**Round 2** (`.project/active/table-image-spike/findingsv2.md`): The original 46% detection recall was a tuning problem, not a capability gap:
- **Removing the 0.98 confidence threshold recovers 7 tables** — 46% → 71% recall. 10/11 filtered detections were real tables. Claude handles FP rejection perfectly (caught all 5 FPs).
- **Img2Table (borderless) finds 4 tables GMFT misses entirely** — uses OpenCV text-alignment heuristics vs GMFT's deep learning. Combined GMFT + Img2Table: 24/28 = 86% recall.
- **Docling detects 34 tables** (vs 28 GT) — likely near-complete coverage as a third-pass safety net.
- **Claude is a perfect FP filter** — the confidence threshold is redundant when Claude validates each detection.

This directly informs FR-4 (ensemble detection with Img2Table + optional Docling, no confidence filter, Claude as FP filter) and FR-6 (Claude budget shared between page and table enhancement).

### 2.5 Known Limitations Carried Forward

These are known gaps from Stage 3 and the table-image spike that Stage 4 does NOT need to solve but must not make worse:

1. **Heading over-detection on non-arXiv papers** — paischer_2025: 55 vs GT 23. The quality gate detects it but can't fix all pages within Claude budget.
2. **Remaining missing table detection** — The ensemble detector (GMFT + Img2Table) achieves 86% recall (24/28 on aries). The remaining 4 tables are borderless tables too small for either detector. Docling (34 detections on aries) covers these as an optional third pass. This is a diminishing-returns problem, not a critical gap.
3. **GMFT over-detection on non-journal docs** — delene_2001: 255 vs GT 150. With the confidence threshold removed, more false positives will reach Claude for FP filtering. The spike proved Claude is a perfect FP filter (caught all 5 FPs on aries), so this is a cost concern (more Claude calls), not an accuracy concern.

---

## 3. Functional Requirements

### FR-1: Pipeline Entry Point

The pipeline accepts a single PDF file path and returns structured output (markdown + metadata). Optional inputs include an explicit arXiv HTML path (override for when auto-detection fails or HTML is pre-downloaded).

### FR-2: arXiv Detection and Pandoc Shortcut

The pipeline automatically detects arXiv papers from the PDF itself and, when HTML is available, converts via Pandoc instead of PDF extraction. This produces perfect headings and equations at zero cost.

**Auto-detection sequence** (from Stage 1B, <1s per paper):
1. Extract text from PDF page 1 (via `pdftotext` or pymupdf)
2. Regex match for `arXiv:\d{4}\.\d{4,5}(v\d+)?`
3. If found → HTTP HEAD `https://arxiv.org/html/{id}` to verify HTML availability
4. If match but no HTML → fall through to PDF extraction
5. If no match → check `pdfinfo` Creator field for `arXiv` string (secondary signal)
6. If an explicit HTML path was provided (FR-1), use that instead of fetching

Auto-detection is the default mode. An explicit `--html-path` option is an override for cases where auto-detection fails or the HTML has been pre-downloaded.

**Pandoc configuration** (from Stage 1B/3):
- Input format: `html-native_divs-native_spans`
- Output format: `markdown-header_attributes`
- `--wrap=none`
- Pre-processing: strip `<figure>` tags and CSS transform wrappers
- Post-processing: strip `\hspace{0pt}` and HTML comment artifacts

**Degradation:** If `pdftotext`/`pandoc` are not installed, arXiv detection is silently skipped and the pipeline proceeds to PDF extraction.

### FR-3: Base Extraction (pymupdf4llm)

The pipeline extracts per-page markdown from PDFs using pymupdf4llm with the proven BEST_V1 configuration:
- `page_chunks=True`, `table_strategy="lines"`, `ignore_code=True`
- `CompositeHeaderDetector` (font-size IdentifyHeaders + bold pattern matching)
- `force_text=True`, `write_images=False`, `dpi=150`

Output: a list of per-page markdown results, 0-indexed.

### FR-4: Ensemble Table Detection and Enhancement (GMFT + Img2Table + Docling + Claude)

The pipeline detects tables using an ensemble of complementary detectors, then extracts via GMFT DataFrame or Claude cropped-image vision. All detectors and Claude are optional — the pipeline must work without any of them installed.

**Detection ensemble** (from table detection follow-up):

The detectors use fundamentally different approaches and complement each other:

| Detector | Method | Recall (aries) | Speed | When to run |
|----------|--------|:-:|---|---|
| GMFT (TATR) | Deep learning (PubTables-1M) | 71% (20/28) | ~13s | Always (primary) |
| Img2Table | OpenCV text-alignment heuristics | 39% (11/28) | ~64s | Pages where GMFT finds nothing |
| Docling | DocLayNet-trained detection | ~100% (34 detections) | Slow | Optional third pass for max coverage |

- **Step 1: GMFT detection** — `AutoTableDetector` detects table regions, `AutoTableFormatter` attempts DataFrame extraction, cropped images saved for all detections. **No confidence threshold** — keep all detections, rely on secondary filters and Claude FP rejection. The 0.98 threshold was rejecting 7 real tables on aries (10/11 filtered detections were real).
- **Step 2: Img2Table on GMFT-empty pages** — For pages where GMFT detects nothing, run `Img2TableDetector(borderless_tables=True)`. This finds tables GMFT's deep learning model can't see: small tables, space-aligned tables, tables embedded in text-heavy pages. Adds 4 tables on aries (p35, p37, p39, p94).
- **Step 3: Docling detection (optional)** — For pages where neither GMFT nor Img2Table detects anything, Docling provides a third detection pass using DocLayNet-trained models. Detected 34 tables on aries (vs 28 GT), likely near-complete coverage. This is the safety net for maximum recall.

**Secondary false-positive filters** (retained from Stage 3):
- Reject tables with `avg_cell_length > 80` (prose paragraphs, not tabular data)
- Reject single-row tables with `>4 columns` (layout artifacts)

**Table-level Claude enhancement** (from table-image spike):
- **Primary trigger:** A detector finds a table but DataFrame extraction fails (returns null/empty). On aries, 7/15 GMFT-detected tables fell into this category — Claude recovered all 7.
- **Secondary trigger:** DataFrame extraction succeeds but quality looks suspect (very few rows relative to image size, garbled column names). On aries p4, GMFT produced 7 rows; Claude extracted 22 from the same image.
- **False-positive rejection:** When Claude returns 0 rows or identifies the image as not-a-table, flag the detection as a false positive and drop it. Claude is the FP filter for the entire ensemble — caught all 5 FPs on aries across both confidence ranges.
- **Prompt:** Table-specific extraction prompt ("Extract this table as a markdown pipe table... Output ONLY the markdown table, no commentary"). Zero reasoning leakage across 47 Claude calls in the spike.
- **Cost:** $0.076/table average (Sonnet). Deducted from the shared per-document Claude budget (FR-6).

Output: a mapping of page number → list of enhanced tables (some GMFT-extracted, some Claude-extracted, with source and detector tracking).

### FR-5: Quality Gate (Per-Page Assessment)

The quality gate assesses each page of pymupdf4llm output and produces a routing recommendation. Detection dimensions:

| Dimension | Signal | Threshold | Route |
|-----------|--------|-----------|-------|
| Math garbling | `~~text~~` strikethroughs | 3+ occurrences → severity 2.0 | Claude |
| Math garbling | `\ufffd` replacement chars | 2+ occurrences → severity 2.0 | Claude |
| Math garbling | `[/]` `[+]` bracket operators | 3+ occurrences → severity 1.0 | Claude |
| Table anomaly | `<br>` in pipe table rows | Any → severity 1.0 | GMFT |
| Table anomaly | `ColN` auto-headers | Any → severity 1.0 | Strip (GMFT if available) |
| Text density | < 200 chars on a page | Below threshold → severity 0.5 | Claude |
| Heading anomaly | > 3 headings/page (doc-level) | Over threshold → boost Claude severity +0.5 | Claude |

The quality gate is purely deterministic — no ML or API calls.

### FR-6: Budget-Constrained Claude Enhancement

Claude enhancement operates at two levels within a shared per-document budget:
- Default budget: $2.00/document
- **Table-level enhancement** (FR-4) runs first — higher ROI ($0.076/table, targeted at extraction failures)
- **Page-level enhancement** runs second with remaining budget (~$0.078/page, for math garbling and low density)
- Pages are prioritized by severity (highest first)
- Pages within budget are replaced with Claude vision output
- Pages exceeding budget fall back to GMFT (if table issues) or are kept as-is

Table enhancement uses cropped table images with a table-specific prompt. Page enhancement uses full-page images with a page extraction prompt. Both use pure vision mode (image only, no supplemental text).

### FR-7: Per-Page Routing and Merge

Each page is routed to one of these actions based on quality gate + GMFT availability:
- **keep**: Use pymupdf4llm output as-is (no issues detected)
- **gmft_replace**: Replace pymupdf4llm tables with GMFT tables (table anomaly, no math issues)
- **gmft_append**: Append GMFT tables to page (pymupdf4llm found 0 tables, GMFT found some)
- **strip_false**: Strip false-positive tables (ColN headers detected, no GMFT replacement)
- **strip_broken**: Strip broken tables (`<br>` artifacts, no GMFT replacement)
- **claude_replace**: Replace entire page with Claude vision output (math garbling or low density)

When both table and math issues exist on a page, Claude wins (full-page replacement handles both).

Pages are merged in order to produce the final document markdown.

### FR-8: Decision Logging

Every page routing decision is recorded as structured data: page number, action taken, reasons, and any additional details. This log is written alongside the output for debugging and auditability.

### FR-9: Cost Tracking

When Claude enhancement is used, per-invocation and per-document costs are tracked and persisted alongside the output. The cost data includes: table-level Claude calls (page number + table index), page-level Claude calls (page number), per-call cost, total document cost. Table-level and page-level costs are distinguishable in the log.

### FR-10: CLI Integration

The pipeline is accessible via `agentic-mbse extract <pdf_path>` with options for:
- Output directory
- arXiv HTML path (optional, for Pandoc shortcut)
- Claude budget override
- Dry-run mode (shows quality gate decisions without calling Claude)
- Table detection toggle (disable all detectors)
- Img2Table toggle (disable second-pass detection)
- Docling toggle (enable third-pass detection, off by default)

### FR-11: Metrics Computation

The pipeline computes extraction metrics on its output (heading count by level, table row count, math symbol count, character count, figure reference count) using the same computation as `tests/corpus/metrics.py` for consistency with ground truth scoring.

---

## 4. Non-Functional Requirements

### NFR-1: Optional Dependencies

All table detectors and Claude are optional. The pipeline must produce valid output when:
- GMFT is not installed (skip GMFT detection, Img2Table and Docling may still run)
- Img2Table is not available (skip second-pass detection)
- Docling MCP is not available (skip third-pass detection)
- No detectors are installed (use pymupdf4llm tables as-is)
- Claude is not available or budget is $0 (skip Claude enhancement, fall back to detector output or keep)
- Pandoc is not installed (skip arXiv shortcut, always use PDF extraction)

The only hard dependency is pymupdf4llm.

### NFR-2: Performance

- Full pipeline (without Claude) completes within 2x the time of pymupdf4llm alone for any document
- Claude-enhanced pipeline completes within the time of pymupdf4llm + (N_claude_pages * 35s)
- GMFT extraction adds no more than 60s per document

### NFR-3: Error Isolation

A failure in any enhancement step (GMFT crash, Claude timeout, Pandoc error) must not lose the base extraction. The pipeline degrades to pymupdf4llm output for affected pages and logs the failure.

### NFR-4: No Silent Garbage

The pipeline must never silently produce output that is worse than pymupdf4llm alone. Every enhancement must either improve the output or leave it unchanged. (Exception: Claude pages may have fewer table rows than GMFT for pages with both math and tables — this is an accepted trade-off documented in Stage 3.)

### NFR-5: Deterministic Without AI

With Claude budget set to $0 and GMFT disabled, the pipeline produces identical output on repeated runs with the same input. The quality gate and all routing logic are deterministic.

### NFR-6: Testability

Every component is independently testable:
- Quality gate can be tested with synthetic markdown (no PDFs needed)
- GMFT filter can be tested with synthetic table data
- Routing logic can be tested with mock assessments
- The full pipeline can be integration-tested against the corpus

---

## 5. Success Criteria for the Design

These are the criteria the design document must satisfy before implementation begins. They evaluate the quality of the design itself, not the running code.

### SC-1: Clean Component Boundaries

Each component has a single responsibility, a well-defined interface, and communicates with other components through explicit data types — not through side effects, shared mutable state, or implicit conventions.

**Evaluation:** Can you describe what each component does, what it takes as input, and what it produces as output in one sentence? If not, the boundary is wrong.

### SC-2: Data Types Reflect Reality

The type system captures what actually flows between components — not what we wish flowed. Types are derived from the Stage 3 experiment data flow, not from the old branch's type system.

**Evaluation:** Do the types match the `PageResult → PageAssessment → PageDecision → merged markdown` flow that Stage 3 proved? Are there types that exist but nothing produces or consumes them?

### SC-3: The Per-Page Routing Model Is First-Class

The design must treat per-page routing as a core architectural concept, not an afterthought bolted onto a full-document pipeline. Pages are the unit of enhancement.

**Evaluation:** Can you add a new per-page enhancement (e.g., a hypothetical local-model equation fixer) by implementing one component and updating the routing table? If adding a new enhancement requires touching the merge logic, the quality gate, AND the orchestrator, the design is too coupled.

### SC-3b: The Pipeline Composition Is Not Hardcoded

The current pipeline (H5 + H6 pre-check) is the first composition, not the last. The design must make it straightforward to evolve the pipeline over time — adding new quality checks, adding new enhancement backends, changing routing priorities, or restructuring the flow — without requiring an architectural rewrite.

Concretely, these are plausible near-term iterations the design should accommodate without major surgery:
- Adding a "missing table" detection heuristic to the quality gate
- Adding a heading-accuracy check that routes to a different enhancer
- Swapping Claude for a different LLM (Gemini, a local model) as a page enhancer
- Adding a Pandoc+GMFT hybrid for arXiv papers (Pandoc headings/math, GMFT tables)
- Tuning quality gate thresholds based on new corpus data
- Adding a new document-level check (e.g., "this looks like a scanned document, route all pages to OCR")

**Evaluation:** For each of the above, how many files need to change? If the answer is consistently 1-2 (the check/enhancer itself + a configuration or registration point), the design is evolvable. If each requires coordinated changes across 4+ files, it's too rigid.

### SC-4: Budget Awareness Is Composable

The budget mechanism works for any cost-bearing enhancement, not just Claude. It should be straightforward to add a second budgeted enhancer without duplicating budget logic.

**Evaluation:** Is budget enforcement a reusable mechanism, or is it hardcoded to Claude's pricing?

### SC-5: No Promote-Then-Demote

The design must not replicate the old branch's anti-pattern of aggressive promotion followed by noise filtering. Each transformation should make a confident, targeted change — not a speculative change that needs a subsequent cleanup pass.

**Evaluation:** Are there any components whose primary purpose is to undo or filter the output of a previous component? If so, the earlier component is too aggressive.

### SC-6: Graceful Degradation by Design

The pipeline's degradation path (Claude → GMFT → keep) must be an explicit part of the design, not an error-handling afterthought. Each layer's absence is a normal operating mode, not an exception.

**Evaluation:** Does the design work with zero optional dependencies installed? Is the degradation path visible in the architecture diagram?

### SC-7: Provenance as a Design Concern

Decision logging (FR-8) and cost tracking (FR-9) are first-class design concerns, not post-hoc additions. The data structures should naturally support recording "why this page was routed this way."

**Evaluation:** Can you reconstruct the full decision history for any page from the output artifacts? If decision data is scattered across log files or print statements, it's not a design concern.

### SC-8: Minimal Surface Area

The public API should be small. Ideally: one function to run the pipeline, one to run just the quality gate (for dry-run/debugging), and the types needed to interpret results.

**Evaluation:** How many imports does a caller need? How many configuration objects must they construct? If the answer is more than 3-4, the surface area is too large.

### SC-9: Experiment-to-Production Traceability

Every threshold, heuristic, and decision rule in the design should be traceable to a specific Stage 3 finding or ground truth measurement. No magic numbers without provenance.

**Evaluation:** For any constant in the design (e.g., confidence threshold 0.98, severity 2.0 for strikethroughs, budget $2/doc), can you point to the experiment that established it?

### SC-10: Test Strategy Is Part of the Design

The design document must include a test strategy that covers:
- Unit tests for each component with synthetic inputs (no PDF/network dependencies)
- Integration tests against the corpus that verify metrics match or exceed Stage 3 results
- A clear answer to "how do we know the production code matches what the experiments proved?"

**Evaluation:** Does the test strategy catch a regression where the quality gate stops detecting math garbling? Does it catch a regression where GMFT tables are merged incorrectly?

---

## 6. Success Criteria for the Implementation

These criteria evaluate the running code after implementation.

### IC-1: Quality Parity with Stage 3

The production pipeline produces output whose metrics (heading count, table row count, math symbol count) match or exceed Stage 3's H5 results for the 4 dev-set papers and 3 hold-out papers.

**Measurement:** Run `score_against_ground_truth()` on production output vs Stage 3 `runs/pipeline_h5/` output. No dimension regresses by more than 5%.

### IC-2: Free-Tier Parity

With Claude budget $0 and GMFT enabled, the pipeline matches H1 results (1% average table error on dev set).

**Measurement:** Run against dev set with `--budget=0`, compare table metrics against `runs/pipeline_h1/`.

### IC-3: All Corpus PDFs Extract Successfully

Every PDF in `tests/corpus/pdfs/` (15 files) produces a non-empty markdown output without crashing, including the 241-page `energy_amplifier`.

**Measurement:** Automated integration test.

### IC-4: CLI Works End-to-End

`uv run agentic-mbse extract <pdf_path>` produces: output markdown file, metrics file, decisions file. Optional: cost file when Claude is used.

**Measurement:** Manual verification + CLI test.

### IC-5: Test Coverage

- Every quality gate signal has at least one unit test with a synthetic markdown input that triggers it
- Every routing action (keep, gmft_replace, gmft_append, strip_false, strip_broken, claude_replace) has a unit test
- GMFT false-positive filter has unit tests for each rejection heuristic
- Table quality assessment has unit tests for extraction failure and suspect quality triggers
- Integration test runs the full pipeline on at least 2 corpus PDFs

### IC-6: No Dormant Code

Every module in the extraction package is imported and used by the pipeline or CLI. No modules exist that are "built but not wired in" (the old branch's primary failure mode).

**Measurement:** Remove any module and at least one test or CLI command fails.

---

## 7. Constraints

### C-1: Module Location

Production code goes in `src/agentic_mbse/extraction/`. Tests go in `tests/`. Experiment scripts in `tests/corpus/pipelines/` remain as reference but are not imported by production code.

### C-2: Dependency Management

- pymupdf4llm: required (already in pyproject.toml)
- gmft: optional (guarded by `try/except ImportError`) — includes GMFT TATR detector and Img2Table detector
- img2table: optional (bundled with gmft, guarded by `try/except ImportError`)
- Docling MCP: optional (checked at runtime for MCP availability)
- pandoc: optional (checked at runtime via `shutil.which`)
- Claude: optional (requires `claude` CLI on PATH)
- No new required dependencies

### C-3: Existing Module Disposition

The design must specify what happens to each existing file in `src/agentic_mbse/extraction/`:
- **Keep as-is** (still used by other parts of the system)
- **Refactor** (update to match new pipeline interfaces)
- **Replace** (superseded by new implementation)
- **Remove** (no longer needed)

The `index.py` module (section parsing, INDEX.md generation) is orthogonal to the pipeline and should be preserved.

### C-4: Configuration

Pipeline parameters (quality gate thresholds, GMFT confidence cutoff, Claude budget, model name) must be configurable but must ship with sensible defaults that match Stage 3's proven values. Configuration should not require constructing complex object graphs.

### C-5: Backward Compatibility

The existing `ExtractionResult` type is used elsewhere in the codebase. The design should either preserve it or clearly document the migration path.

---

## 8. Glossary

| Term | Definition |
|------|-----------|
| **Base extraction** | The initial pymupdf4llm pass that produces per-page markdown |
| **Enhancement** | Any improvement applied after base extraction — either per-page (Claude full-page) or per-table (Claude cropped-image) |
| **Table enhancement** | Claude extraction from cropped table images, triggered when GMFT detects but can't extract or produces suspect quality |
| **Quality gate** | Deterministic per-page assessment that recommends routing |
| **Routing** | The per-page decision of which output to use in the final document |
| **Budget** | Maximum dollar spend on cost-bearing enhancements per document |
| **Severity** | Cumulative score from quality gate signals; higher = more likely to receive enhancement |
| **Ground truth** | Human-verified metrics in `tests/corpus/ground_truth.jsonl` |
| **Dev set** | The 4 papers with full ground truth: hawker_2020, hsu_2020, hansen_2025, paischer_2025 |
| **Hold-out set** | The 3 papers with partial ground truth: aries_cost_account, delene_2001, energy_amplifier |

---

## 9. References

| Resource | Location | Relevance |
|----------|----------|-----------|
| Stage 3 findings | `.project/active/pipeline-experimentation/findings.md` | Pipeline shape, component interfaces, quality gate thresholds, cost model |
| Stage 3 comparison | `tests/corpus/pipeline_comparison.md` | Quality metrics for all pipelines vs ground truth |
| Stage 3 experiment scripts | `tests/corpus/pipelines/` | Working prototypes of each component |
| Ground truth | `tests/corpus/ground_truth.jsonl` | 7-document reference for quality measurement |
| Metrics module | `tests/corpus/metrics.py` | `compute_metrics()`, `score_against_ground_truth()` |
| Table-image spike findings (v1) | `.project/active/table-image-spike/findings.md` | Claude cropped-image accuracy, detection coverage, multi-pass results |
| Table-image spike findings (v2) | `.project/active/table-image-spike/findingsv2.md` | Confidence threshold removal, Img2Table complement, Docling safety net, ensemble strategy |
| Table-image spike spec | `.project/active/table-image-spike/spec.md` | Spike design, experiment tracks, success criteria |
| Old branch audit | `.project/research/20260221-094043_doc-ingest-branch-full-audit.md` | Anti-patterns to avoid, strengths to preserve |
| Resilient ingestion concept | `.project/concepts/resilient-document-ingestion.md` | Success criteria and failure categories for the broader system |
| Existing extraction module | `src/agentic_mbse/extraction/` | Current code to refactor/replace/preserve |
| Development strategy | `.project/concepts/doc-extraction-development-strategy.md` | Stage 4 definition of done |

---

## 10. Acceptance Checklist

Before the design is considered ready for implementation:

- [ ] All 10 design success criteria (SC-1 through SC-10) addressed
- [ ] Architecture diagram showing the per-page data flow
- [ ] Disposition of every existing extraction module file (keep/refactor/replace/remove)
- [ ] Type definitions for the core data flow (page result → assessment → decision → output)
- [ ] Public API surface documented (functions, types, configuration)
- [ ] Test strategy with specific test cases enumerated
- [ ] Dependency management approach for optional components

Before the implementation is considered complete:

- [ ] All 6 implementation success criteria (IC-1 through IC-6) met
- [ ] All functional requirements (FR-1 through FR-11) implemented
- [ ] All non-functional requirements (NFR-1 through NFR-6) satisfied
- [ ] Stage 4 definition of done from the development strategy met

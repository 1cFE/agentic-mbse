# Development Strategy: Clean Document Extraction Infrastructure

**Created:** 2026-02-22
**Status:** Draft
**Branch:** `doc-ingest-clean` (fresh from `main`)

---

## Guiding Principles

The `ralph/doc-ingest` branch produced 97 commits and ~25,900 lines of experimental code. The full audit (`.project/research/20260221-094043_doc-ingest-branch-full-audit.md`) surfaced clear lessons:

1. **Understand tools deeply before building pipelines.** The single highest-value change on the old branch was `table_strategy="lines_strict"` — one parameter discovered through reading pymupdf4llm's API. Meanwhile, 560 lines of regex-based postprocessing was built without fully understanding the upstream tools.
2. **Build and test incrementally.** The BART loop infrastructure was well-engineered but jumped straight to orchestrating agents before the extraction fundamentals were solid.
3. **Don't accumulate heuristics.** The promote-then-demote anti-pattern (add header promoters, then add noise filters to reject their false positives) produced fragile code. Prefer structured approaches over regex accumulation.

This strategy is deliberately paced. Each stage builds understanding before adding complexity.

---

## Stage 0: Prerequisites

**Goal:** Ensure the development environment has all necessary tools available.

### Requirements

- [ ] `pymupdf4llm` installed and working (`uv sync` should cover this)
- [ ] Pandoc system binary available (`pandoc --version`)
- [ ] Docling MCP server configured (via `scripts/setup-docling.sh` or `agentic-mbse init --no-docling` to skip)
- [ ] pdf-analysis skill installed in `.claude/skills/pdf-analysis/` (already present on this branch)
- [ ] Test PDFs accessible — the 8-paper corpus from the old branch lives in `../fusion-tea/knowledge/raw/` (per `AGENTS.md` in the worktree)

### Actions

1. Verify `uv run python -c "import pymupdf4llm; print(pymupdf4llm.__version__)"` works
2. Verify `pandoc --version` returns a version
3. Verify Docling MCP is running or decide to defer it
4. Collect 3-5 representative test PDFs covering: text-heavy, table-heavy, math-heavy, scanned/OCR-needed

### References

- pdf-analysis skill: `claude/skills/pdf-analysis/SKILL.md`
- Docling setup: `scripts/setup-docling.sh` (342 lines, Linux-only currently)
- Existing extraction backends on main: `src/agentic_mbse/extraction/`

---

## Stage 1: Deep-Dive into PDF Extraction Engines

**Goal:** Build fundamental understanding of pymupdf4llm, Pandoc, and Docling by experimenting directly with their APIs. Understand what each does well, what it does poorly, and which parameters matter.

This is an **exploration and learning** stage. The deliverable is knowledge (captured in research notes) and a small set of well-tested extractor classes that wrap each engine cleanly.

### 1A: pymupdf4llm

pymupdf4llm is the fast, always-available baseline. It converts PDF pages to markdown using font metadata for heading detection and `lines_strict` for table extraction.

**What to investigate:**

- **`to_markdown()` parameters:** The old branch discovered `table_strategy="lines_strict"` was a huge win. What other parameters exist? Explore: `hdr_info`, `write_images`, `image_path`, `image_size_limit`, `page_chunks`, `margins`, `dpi`, `force_text`. The pymupdf4llm API may have evolved since the old branch.
- **Font-based heading detection:** pymupdf4llm has built-in heading detection via font size. The old branch built a custom `AcademicHeaderDetector` (200+ lines). Understand: when does the default detector work well? When does it fail? Is the custom detector actually needed, or can we tune parameters?
- **Table extraction modes:** `"lines"`, `"lines_strict"`, `"text"` — what exactly does each do? The old branch found `lines_strict` eliminated 252 false `<br>` artifacts. Are there cases where it drops real tables?
- **Page markers and image extraction:** How does pymupdf4llm handle page boundaries? Image extraction quality at different DPI settings? Image path rewriting?

**What to build:**

A clean `PyMuPDFExtractor` class that:
- Wraps `pymupdf4llm.to_markdown()` with the best parameter configuration we discover
- Returns structured output (markdown text, metadata about what was detected)
- Has good test coverage against our test PDFs
- Documents (in code comments or a research note) which parameters we tried and why we chose the values we did

**Key requirement:** Don't just copy the old branch's `pymupdf_backend.py`. Start from the pymupdf4llm API documentation and build up understanding. The old code may have been tuned for specific papers rather than general robustness.

### 1B: Pandoc

Pandoc is the converter for structured formats (JATS XML, DOCX). It's already a system dependency.

**What to investigate:**

- **JATS XML conversion:** `pandoc -f jats -t markdown` — how well does it handle sections, tables, MathML, citations, figures? Try with real PMC JATS files.
- **DOCX conversion:** Quality compared to pymupdf4llm for the same document?
- **Output format options:** `--wrap=none`, `--markdown-headings=atx`, table format options, math rendering options (`--katex`, `--mathml`, `--webtex`). Which combination produces the cleanest markdown?
- **PDF input:** Pandoc can also read PDFs (poorly). Understand why it's not suitable as a primary PDF backend.

**What to build:**

A clean `PandocConverter` class that:
- Handles JATS XML and DOCX input
- Uses subprocess with timeout protection (the old branch used 60s, is that right?)
- Validates input before conversion (e.g., check for `<article>` and `<body>` tags in JATS)
- Returns structured output with quality flags

### 1C: Docling

Docling is the ML-based heavy hitter — best for complex tables and layouts, but slow and resource-intensive.

**What to investigate:**

- **API and configuration:** The old branch used `table_structure=true, picture_images=true, ocr=false`. What other options exist? What does OCR mode look like?
- **Performance characteristics:** How slow is it really? Memory usage? Does it crash on large PDFs? (The old branch's `docling_backend.py` has subprocess + timeout protection, suggesting it does crash.)
- **Table quality:** The audit says GMFT was benchmarked at 83% accuracy. Docling uses a different table model (TableFormer). How do they compare?
- **When to use it:** Docling is overkill for text-heavy pages. What's the right heuristic for "this page needs Docling"?
- **MCP server vs library:** We have both a Docling MCP server (for interactive use via pdf-analysis skill) and the library (for programmatic use). Understand the tradeoffs.

**What to build:**

A clean `DoclingExtractor` class that:
- Wraps Docling with proper timeout and crash protection
- Can operate on single pages (memory safety) or full documents
- Returns structured output with quality flags
- Gracefully degrades when Docling is unavailable

### Stage 1 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| Old pymupdf_backend.py | Worktree: `src/agentic_mbse/extraction/pymupdf_backend.py` | AcademicHeaderDetector implementation, `lines_strict` discovery |
| Old postprocess.py | Worktree: `src/agentic_mbse/extraction/postprocess.py` | Header promotion patterns (what to learn from, what to avoid) |
| Old docling_backend.py | Worktree: `src/agentic_mbse/extraction/docling_backend.py` | Subprocess + timeout pattern, 137 lines |
| Old pdf_converter.py | Worktree: `src/doc_ingest/converters/pdf_converter.py` | 2-layer PDF conversion with GMFT enhancement, 343 lines |
| Branch audit, Capability 2 | `.project/research/20260221-094043_doc-ingest-branch-full-audit.md` (lines 100-146) | Quality assessment of extraction pipeline changes |
| Corpus results | Branch audit, Capability 5 (lines 269-306) | 8-paper test corpus grades and metrics |
| pdf-analysis skill | `claude/skills/pdf-analysis/SKILL.md` | Interactive extraction workflow for ad-hoc testing |
| Existing extraction code on main | `src/agentic_mbse/extraction/` | Current baseline to build on |

### Stage 1 Definition of Done

- Each extractor class has unit tests covering: text-heavy PDF, table-heavy PDF, math-heavy PDF
- A research note documents: parameters explored, quality observations, known limitations per engine
- We can articulate clearly: "Use pymupdf4llm when X, use Docling when Y, use Pandoc when Z"

---

## Stage 2: Identify and Address Gaps

**Goal:** Understand what the three engines still can't handle well, and determine how much Claude's native vision capabilities can fill in.

### Known Gaps (from the old branch audit)

| Gap | Severity | Which Papers | Notes |
|-----|----------|--------------|-------|
| Equations / math notation | Medium | hawker_2020, helios_design, sparc_overview, energy_amplifier | pymupdf4llm produces garbled Unicode; Docling has partial LaTeX support |
| Scanned/image-only PDFs (OCR) | High | (none in current corpus, but common in the wild) | pymupdf4llm returns empty text; Docling has OCR mode but it's untested |
| Complex multi-span tables | Medium | aries_cost_account, helios_design | `lines_strict` handles simple tables; complex spanning cells still break |
| Figure/diagram descriptions | Low | All papers | No engine extracts figure content — they're just image references |

### What to Investigate

- **Equations:** Render equation-heavy pages as images (Tier 3 of pdf-analysis skill). Have Claude transcribe the equations to LaTeX. How accurate is this? Can it be automated, or is it inherently interactive?
- **OCR:** Test Docling with `ocr=true` on a scanned PDF. Quality? Speed? Does Tesseract need separate installation? Is there a simpler path via `pymupdf` page rendering + Claude vision?
- **Complex tables:** Compare `lines_strict` output vs Docling output vs GMFT output for the same complex table. Which handles spanning cells best?
- **Figures:** Claude can describe figures from rendered page images. Is this worth automating, or should it remain interactive?

### What to Build

Nothing necessarily — this stage is about understanding limits. If we find that Claude vision can reliably handle equations and OCR:
- A `ClaudeVisionHelper` utility that renders a PDF region to image and asks Claude to transcribe it
- Integration points in the extractors where this could be called

If we find it can't:
- Document the limitations clearly so we don't waste time trying to automate what requires human judgment

### Stage 2 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| Branch audit "What Didn't Work" | `.project/research/20260221-094043_doc-ingest-branch-full-audit.md` (lines 333-341) | Equations and complex tables never addressed |
| Old ai_repair.py | Worktree: `src/agentic_mbse/extraction/ai_repair.py` | Claude-powered repair with cross-validation pattern |
| Old claude_structure.py | Worktree: `src/agentic_mbse/extraction/claude_structure.py` | Claude-powered heading detection |
| pdf-analysis skill, Tier 3 | `claude/skills/pdf-analysis/SKILL.md` | Image + Vision fallback workflow |
| Old quality_gates.py | Worktree: `src/agentic_mbse/extraction/quality_gates.py` | Broken table detection heuristics |

### Stage 2 Definition of Done

- A clear, documented assessment of what Claude vision can and can't do for: equations, OCR, complex tables, figure description
- If viable, prototype utilities for the automatable cases
- A decision document: "For the pipeline, we will handle X automatically and leave Y for interactive use"

---

## Stage 3: Assemble the PDF Extraction Pipeline

**Goal:** Combine the extractors from Stage 1 and the gap-filling from Stage 2 into a coherent, layered pipeline.

### Pipeline Architecture (Proposed)

```
Input: PDF file
        │
        ▼
┌───────────────────┐
│ Layer 1: pymupdf4llm  │  Fast baseline. Always runs.
│ (PyMuPDFExtractor)     │  Produces: markdown + metadata
└──────────┬────────┘
           │
           ▼
┌───────────────────┐
│ Quality Assessment │  Detect: broken tables, missing headings,
│                    │  equation garbling, scanned pages
└──────────┬────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
  Good enough   Needs enhancement
  → DONE        │
                │
           ┌────┴────┐
           │         │
           ▼         ▼
   ┌──────────┐  ┌──────────┐
   │ Docling   │  │ Claude   │
   │ (tables,  │  │ (equations,│
   │  layout)  │  │  OCR,     │
   │           │  │  structure)│
   └──────┬───┘  └──────┬───┘
          │             │
          └──────┬──────┘
                 │
                 ▼
          ┌──────────┐
          │ Merge &   │  Combine best results from each layer
          │ Validate  │  Cross-validate numbers/structure
          └──────────┘
```

### Key Design Decisions

1. **pymupdf4llm is always Layer 1.** It's fast, reliable, and produces a usable baseline for every PDF. We never skip it.
2. **Quality assessment is deterministic.** No ML or LLM calls — just check the markdown output for known problem patterns (pipe table validation, heading count, math symbol density, text extraction ratio).
3. **Enhancement is targeted.** Don't re-extract the whole document with Docling. Only send pages/regions that need it. This is both faster and more memory-safe.
4. **Claude is a specialized tool, not a cleanup pass.** Use Claude for specific tasks (equation transcription, OCR, structural repair) with cross-validation, not as a general "make it better" step.

### What to Build

- Pipeline orchestrator that runs Layer 1, assesses quality, and selectively applies enhancements
- Quality assessment module (evolve from the old `quality_gates.py` but with cleaner heuristics)
- Merge logic that combines Layer 1 output with targeted enhancements
- Integration tests against the test corpus

### Stage 3 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| Old quality_gates.py | Worktree: `src/agentic_mbse/extraction/quality_gates.py` | Broken table detection, page mapping |
| Old table_extraction.py | Worktree: `src/agentic_mbse/extraction/table_extraction.py` | GMFT integration pattern, 83% accuracy benchmark |
| Old ai_repair.py | Worktree: `src/agentic_mbse/extraction/ai_repair.py` | Cross-validation safety pattern |
| Resilient ingestion concept | `.project/concepts/resilient-document-ingestion.md` | Success criteria, failure categories |
| Branch audit recommendations | `.project/research/20260221-094043_doc-ingest-branch-full-audit.md` (lines 353-361) | Stop regex accumulation, wire up GMFT, add quality metrics |

### Stage 3 Definition of Done

- Pipeline produces markdown for all test PDFs with quality equal to or better than the old branch
- Table-heavy PDFs show measurable improvement from Docling/GMFT enhancement
- No regression on text-heavy PDFs (pymupdf4llm baseline is preserved)
- Quality assessment correctly identifies which pages need enhancement
- Test coverage for the orchestration logic

---

## Stage 4: Build the Scaffolding

**Goal:** Add the routing, provenance, and CLI infrastructure around the PDF pipeline.

### What This Includes

1. **Source format types and converter protocol** — Clean type system for extraction results, quality flags, failure categories. The old branch's `doc_ingest/types.py` (314 lines) and `converters/base.py` (88 lines) are solid references.

2. **Converter registry** — Format-to-converter mapping. Simple, proven pattern from the old branch.

3. **Provenance tracking** — Every extraction records: what was attempted, what succeeded, why failures happened. Atomic writes via `os.replace()`. The old branch's `provenance_manager.py` is well-designed.

4. **CLI integration** — Wire the pipeline into `agentic-mbse extract` (or `agentic-mbse ingest`). Support local file input with format detection.

5. **Resumability** — Skip documents that already succeeded. Retry failed/partial outcomes. Hash-based directory naming for deterministic output paths.

### What NOT to Build Yet

- Source discovery (OpenAlex, arXiv, PMC APIs) — that's Stage 5
- HTML/XML converters — that's Stage 5
- Batch processing — keep it single-document for now
- Triage reports — need provenance data from real runs first

### Stage 4 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| SourceRouter deep dive | `.project/research/20260222-100000_doc-ingest-router-deep-dive.md` | Full architecture walkthrough of old branch's routing |
| Old types.py | Worktree: `src/doc_ingest/types.py` (314 lines) | Type system design |
| Old base.py | Worktree: `src/doc_ingest/converters/base.py` (88 lines) | Converter Protocol |
| Old provenance_manager.py | Worktree: `src/doc_ingest/provenance_manager.py` | Atomic persistence pattern |
| Old source_router.py | Worktree: `src/doc_ingest/source_router.py` (247 lines) | 5-step orchestration with crash-safe persistence |
| Resilient ingestion concept | `.project/concepts/resilient-document-ingestion.md` | Provenance schema, triage, failure categories |

### Stage 4 Definition of Done

- Can run `agentic-mbse extract <pdf_path>` and get: markdown output + provenance JSON
- Provenance records capture: converter used, quality flags, extraction time, any warnings
- Re-running the same document skips extraction (resumability)
- Type system is clean, well-documented, and tested

---

## Stage 5: HTML and Structured Source Routes

**Goal:** Add the non-PDF extraction paths — JATS XML, arXiv HTML, publisher HTML — and the source discovery layer that finds them.

### 5A: HTML/XML Converters

Build converters for structured formats. These are inherently higher quality than PDF extraction because the source has semantic markup.

- **JATS XML via Pandoc** — Highest fidelity. Semantic sections, MathML, tables. The old branch's `JATSPandocConverter` is a clean implementation.
- **arXiv HTML** — HTML5 with MathML, clean semantic markup. The old branch's `ArXivHTMLConverter` uses BeautifulSoup.
- **Publisher HTML** — Variable quality, paywall detection needed. The old branch's `PublisherHTMLConverter` has 8 paywall markers.

Each converter implements the same protocol as the PDF extractors from Stage 3, so they plug into the same registry and provenance infrastructure.

### 5B: Source Discovery

Given a document identifier (DOI, arXiv ID, PMC ID), discover structured alternatives via bibliographic APIs before falling back to PDF.

- **OpenAlex API** — Primary discovery. Batch-capable (50 DOIs/request). Returns PMC IDs, arXiv IDs, OA URLs.
- **arXiv API** — Check HTML availability via HEAD request. PDF always available as fallback.
- **PMC E-utilities** — Fetch JATS XML by PMC ID.
- **Discovery cache** — Cache API results locally (TTL-based) to avoid re-querying.

### 5C: Quality-Ordered Routing

The extraction orchestrator tries sources in quality order with early exit on first success:

```
JATS XML (tier 1) → arXiv HTML (tier 2) → Publisher HTML (tier 3) → PDF (tier 4)
```

This is the core value proposition: for papers with structured sources, the pipeline automatically finds and uses them, producing dramatically better output without any PDF extraction heuristics needed.

### Stage 5 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| HTML/XML research | `.project/research/html-trace.md` | Structured source landscape, API access patterns, converter options |
| Resilient ingestion concept | `.project/concepts/resilient-document-ingestion.md` | Source discovery design, quality tiering, converter recommendations |
| Old html_converter.py | Worktree: `src/doc_ingest/converters/html_converter.py` (504 lines) | ArXiv + Publisher HTML implementations |
| Old markdown_converter.py | Worktree: `src/doc_ingest/converters/markdown_converter.py` (358 lines) | JATS + DOCX Pandoc implementations |
| Old source_discoverer.py | Worktree: `src/doc_ingest/source_discoverer.py` | Multi-API discovery + cache |
| Old API clients | Worktree: `src/doc_ingest/api_clients/` | OpenAlex, arXiv, PMC implementations |
| Old extraction_orchestrator.py | Worktree: `src/doc_ingest/extraction_orchestrator.py` | Quality-ordered extraction loop with early exit |
| Discovery validation report | Worktree: `tests/corpus/discovery_validation.md` | Real API behavior validation |

### Stage 5 Definition of Done

- Can extract from: local PDF, local JATS XML, local HTML, arXiv ID (with API discovery), DOI (with API discovery)
- Quality tiering produces measurably better output for papers with structured sources
- Discovery cache prevents redundant API calls
- Paywall detection correctly rejects access-restricted pages
- All converters have unit tests with realistic input samples

---

## Stage 6: Triage, Batch Processing, and Polish

**Goal:** Build the operational tooling for processing document collections.

### What This Includes

- **Triage report generation** — Aggregate provenance records into a categorized Markdown report (success/partial/failed grouped by failure category)
- **Batch processing** — Process multiple documents from a JSONL manifest
- **Retry logic** — Re-process failed/partial documents, skip successes
- **Cache management** — Clear discovery cache, inspect provenance records
- **CLI commands** — `ingest`, `ingest-batch`, `triage-report`, `retry-failed`, `clear-cache`
- **Integration with fusion-tea** — Update `zotero_ingest.py` to use the new pipeline

### Stage 6 References

| Resource | Location | What It Tells Us |
|----------|----------|------------------|
| Old CLI | Worktree: `src/doc_ingest/cli.py` (759 lines) | 5 subcommands, pipeline construction |
| Old outcome_classifier.py | Worktree: `src/doc_ingest/outcome_classifier.py` | Outcome + failure category logic |
| Old result_writer.py | Worktree: `src/doc_ingest/result_writer.py` | Persistence of markdown + provenance |
| Resilient ingestion concept, user stories | `.project/concepts/resilient-document-ingestion.md` (lines 29-57) | US-1 through US-7 |

---

## What to Carry Forward vs. Rebuild

The old branch has ~10,000 lines of tested code. Not all of it should be ported. Here's the assessment:

### Port (proven, well-designed)

| Component | Old Location | Lines | Why Port |
|-----------|-------------|-------|----------|
| Type system | `doc_ingest/types.py` | 314 | Clean dataclasses, well-thought-out |
| Converter Protocol | `doc_ingest/converters/base.py` | 88 | Simple, correct interface |
| Converter Registry | `doc_ingest/converters/registry.py` | 73 | Straightforward lookup |
| Provenance Manager | `doc_ingest/provenance_manager.py` | 166 | Atomic writes, crash safety |
| Outcome Classifier | `doc_ingest/outcome_classifier.py` | ~100 | Clean categorization logic |
| API clients (OpenAlex, arXiv, PMC) | `doc_ingest/api_clients/` | ~500 | Tested against real APIs |
| GMFT table extraction | `extraction/table_extraction.py` | ~150 | Benchmarked at 83% |
| Cross-validation safety | `extraction/ai_repair.py` (extract_numbers, cross_validate) | ~50 | Prevents AI hallucination acceptance |

### Rebuild (learn from but don't copy)

| Component | Old Location | Lines | Why Rebuild |
|-----------|-------------|-------|-------------|
| pymupdf_backend.py | `extraction/pymupdf_backend.py` | 237 | Need deeper API understanding first (Stage 1) |
| postprocess.py | `extraction/postprocess.py` | 560 | Anti-pattern identified; rebuild with cleaner approach |
| quality_gates.py | `extraction/quality_gates.py` | ~150 | Good concept, but heuristics may change after Stage 1 |
| PDF converter | `doc_ingest/converters/pdf_converter.py` | 343 | Depends on rebuilt pymupdf backend |

### Defer (not needed initially)

| Component | Old Location | Lines | Why Defer |
|-----------|-------------|-------|-----------|
| CLI | `doc_ingest/cli.py` | 759 | Build CLI after pipeline works (Stage 6) |
| Source Router | `doc_ingest/source_router.py` | 247 | Build after all converters work (Stage 5) |
| BART loop | `experiment-history/` | ~1,400 | Out of scope for this branch |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Spending too long exploring APIs in Stage 1 | Timebox each engine to 1-2 focused sessions. Capture findings in research notes. Don't try to be comprehensive — focus on parameters that matter for our use case. |
| Over-engineering the pipeline in Stage 3 | Start with the simplest thing that works: pymupdf4llm only, no enhancement. Add Docling/Claude only for papers where baseline is measurably inadequate. |
| Porting bugs from old branch | Never copy code without understanding it. Read the old implementation, understand the intent, then write clean implementations with tests. |
| Docling availability issues | Docling is always optional. The pipeline must work without it. Enhancement via Docling is a bonus, not a requirement. |
| Scope creep into source discovery before PDF pipeline is solid | Stages are sequential. Don't start Stage 5 until Stage 4 is done. PDF extraction is the foundation — structured sources are an optimization on top. |

---

## Summary

| Stage | Focus | Key Deliverable |
|-------|-------|----------------|
| 0 | Prerequisites | Working dev environment with test PDFs |
| 1 | Deep-dive into engines | Tested extractor classes + research notes on each engine |
| 2 | Gap analysis | Decision document on what Claude vision can/can't automate |
| 3 | PDF pipeline | Layered extraction: pymupdf4llm → quality check → targeted enhancement |
| 4 | Scaffolding | Types, provenance, converter registry, CLI, resumability |
| 5 | HTML/XML routes | Structured source converters + source discovery + quality routing |
| 6 | Operational tooling | Batch processing, triage reports, retry, cache management |

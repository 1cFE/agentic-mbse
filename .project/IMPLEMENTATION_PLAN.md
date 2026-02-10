# Implementation Plan: Document Ingestion Pipeline

**Date**: 2026-02-09
**Status**: Active Development
**Last Updated**: 2026-02-09 23:00
**Branch**: `ralph/doc-ingest`

---

## Executive Summary

**Current State**: All converters + batch CLI complete (17/17 specs + TASK-DI-010)
**Next Milestone**: Full API integration (OpenAlex, arXiv, PMC - P3)
**Critical Path**: Production-ready MVP complete - all P0-P2 tasks done

**Technology Stack**: Python 3.11+, UV package manager, pytest, pydantic
**Verification**: Unit tests + integration tests for each component

---

## Specification Coverage Analysis

### ✅ Completed Specifications (17 specs + batch CLI)

| Spec | Component | Implementation | Lines | Tests |
|------|-----------|----------------|-------|-------|
| **001** | DocumentIdentifiers | `src/doc_ingest/types.py:53-109` | 57 | ✅ |
| **002** | QualityFlags | `src/doc_ingest/types.py:33-51` | 19 | ✅ |
| **003** | SourceCandidate | `src/doc_ingest/types.py:111-150` | 40 | ✅ |
| **004** | ConversionResult | `src/doc_ingest/types.py:182-197` | 16 | ✅ |
| **005** | WebFetcher | `src/doc_ingest/web_fetcher.py` | 134 | ✅ |
| **006** | OutcomeClassifier | `src/doc_ingest/outcome_classifier.py` | 134 | ✅ |
| **007** | SourceRouter | `src/doc_ingest/source_router.py` | 264 | ✅ |
| **008** | ExtractionOrchestrator | `src/doc_ingest/extraction_orchestrator.py` | 207 | ✅ |
| **009** | ProvenanceManager | `src/doc_ingest/provenance_manager.py` | 168 | ✅ |
| **010** | ValidationResult | `src/doc_ingest/types.py:152-180` | 29 | ✅ |
| **011** | CLI (full) | `src/doc_ingest/cli.py` + `src/agentic_mbse/cli/doc_ingest_cli.py` | 728 | ✅ |
| **012** | ResultWriter | `src/doc_ingest/result_writer.py` | 121 | ✅ |
| **013** | DiscoveryCache | `src/doc_ingest/discovery_cache.py` | 162 | ✅ |
| **017** | ConversionError | `src/doc_ingest/types.py:199-216` | 18 | ✅ |
| N/A | ProvenanceRecord | `src/doc_ingest/types.py:254-295` | 42 | ✅ |
| N/A | ExtractionResult | `src/doc_ingest/types.py:297-311` | 15 | ✅ |
| N/A | Converter (protocol) | `src/doc_ingest/converters/base.py` | 91 | ✅ |
| N/A | ConverterRegistry | `src/doc_ingest/converters/registry.py` | 69 | ✅ |
| N/A | SourceDiscoverer (stub) | `src/doc_ingest/source_discoverer.py` | 132 | ✅ |
| **014** | PyMuPDF4LLMConverter | `src/doc_ingest/converters/pdf_converter.py` | 235 | ✅ |
| **015** | ArXiv/PublisherHTMLConverter | `src/doc_ingest/converters/html_converter.py` | 512 | ✅ |
| **016** | JATS/DOCXPandocConverter | `src/doc_ingest/converters/markdown_converter.py` | 362 | ✅ |

**Evidence**: All classes found via code search, commits 756155d through current
**Note**: CLI now includes both single-document (`extract`) and batch processing commands (`extract-batch`, `triage-report`, `retry-failed`, `clear-cache`)

### 🚧 In Progress Specifications (0 specs)

*None currently in progress*

### ✅ Recently Completed

**TASK-DI-010: Batch Processing CLI Commands** — Completed 2026-02-09
- Implemented `cmd_extract_batch()`, `cmd_triage_report()`, `cmd_retry_failed()`, `cmd_clear_cache()`
- JSONL batch processing with progress tracking and error handling
- Automatic triage report generation on batch failures
- Retry logic that skips successful extractions
- Cache invalidation by identifier, age, or full clear
- 15 comprehensive unit tests covering all batch commands (100% pass rate)
- Exit code implementation: 0 (success), 1 (partial batch), 2 (fatal error)
- Files: `cli.py` (+346 lines), `test_doc_ingest_cli.py` (+15 tests)

**TASK-DI-008: Markdown Converters Implementation** — Completed 2026-02-09
- Implemented `JATSPandocConverter` and `DOCXPandocConverter` classes
- JATS XML validation for article/body tags
- DOCX validation via ZIP header magic bytes (PK)
- Pandoc subprocess integration with 60-second timeout
- Quality flags: tables, math, figures, captions, heading structure
- Comprehensive error handling: Pandoc failures, timeouts, missing binary
- 29 unit tests covering all acceptance criteria (100% pass rate)
- Files: `markdown_converter.py` (362 lines), `test_markdown_converter.py` (29 tests)

**TASK-DI-007: HTML Converters Implementation** — Completed 2026-02-09
- Implemented `ArXivHTMLConverter` and `PublisherHTMLConverter` classes
- MathML preservation for arXiv HTML (math_preserved=True flag)
- Paywall detection with 8 common markers
- Truncation detection (< 1KB threshold)
- Quality flags: tables, math, figures, captions, heading structure
- Added beautifulsoup4 dependency
- 28 comprehensive unit tests covering all acceptance criteria (100% pass rate)
- Files: `html_converter.py` (512 lines), `test_html_converter.py` (28 tests)

**TASK-DI-006: PDF Converter Implementation** — Completed 2026-02-09
- Implemented `PyMuPDF4LLMConverter` class with full converter interface
- Scanned PDF detection via text extraction from first 3 pages
- Quality flags: table detection, heading structure, math indicators
- ConversionError with category="needs_ocr" for scanned PDFs
- Warnings for large PDFs (100+ pages) and images
- 17 comprehensive unit tests covering all acceptance criteria (100% pass rate)
- Files: `pdf_converter.py` (235 lines), `test_pdf_converter.py` (17 tests)

**TASK-DI-001: ExtractionOrchestrator Implementation** — Completed 2026-02-09
- Implemented `ExtractionOrchestrator` class with full orchestration logic
- Created converter infrastructure: `Converter` protocol, `ConverterRegistry`
- Quality-ordered source iteration with early exit on success
- Comprehensive error handling: fetch failures, validation failures, conversion errors
- Unexpected exceptions wrapped as `category="unknown"` for crash safety
- 11 unit tests covering all acceptance criteria (100% pass rate)
- Files: `extraction_orchestrator.py`, `converters/base.py`, `converters/registry.py`, `test_extraction_orchestrator.py`

**TASK-DI-002: ProvenanceManager Implementation** — Completed 2026-02-09
- Implemented `ProvenanceManager` class with atomic writes and load functionality
- Added `ProvenanceRecord` dataclass to `types.py` with complete provenance structure
- Atomic writes via temp file + rename pattern (crash-safe)
- UTF-8 encoding for non-ASCII identifiers (verified with Chinese characters)
- Deterministic JSON key ordering for reproducibility
- 11 unit tests covering all acceptance criteria (100% pass rate)
- Files: `provenance_manager.py` (168 lines), `types.py` (ProvenanceRecord), `test_provenance_manager.py`

**TASK-DI-003: ResultWriter Implementation** — Completed 2026-02-09
- Implemented `ResultWriter` class with atomic markdown and summary.json writes
- Added `ExtractionResult` dataclass to `types.py` (markdown + provenance)
- Delegates provenance writing to ProvenanceManager (separation of concerns)
- Writes output.md and summary.json only for successful extractions
- Deterministic directory naming using document hash
- UTF-8 encoding for non-ASCII content (verified with Unicode tests)
- 11 unit tests covering all acceptance criteria (100% pass rate)
- Files: `result_writer.py` (121 lines), `types.py` (ExtractionResult), `test_result_writer.py`

**TASK-DI-005: Minimal CLI Implementation** — Completed 2026-02-09
- Created `agentic-mbse ingest` command for single document extraction
- Identifier validation for DOI, arXiv ID, PMC ID, and local file paths
- Pipeline construction with SourceRouter, ExtractionOrchestrator, and supporting components
- Exit code implementation (0 = success, 2 = fatal error)
- Format override support for skipping discovery
- Comprehensive error handling and user-friendly messages
- 24 unit tests covering validation and command execution (100% pass rate)
- Files: `cli.py` (328 lines), `doc_ingest_cli.py` (54 lines), `test_doc_ingest_cli.py` (24 tests)

### ⏳ Pending Specifications (0 specs)

*All P0-P2 specifications complete - Production-ready MVP*

---

## Priority Definitions

- **P0 (Critical Path)**: Core orchestration components that other specs depend on
- **P1 (High Priority)**: User-facing features required for MVP
- **P2 (Medium Priority)**: Enhancements and secondary features
- **P3 (Low Priority)**: Nice-to-have, documentation, optimizations

---

## Task List

### P0: Critical Path (Core Orchestration)

#### [DONE] TASK-DI-001: ExtractionOrchestrator Implementation
**Addresses**: Spec 008 (extraction_orchestrator.md)
**Priority**: P0
**Complexity**: MEDIUM (~200 lines, 1 file)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `src/doc_ingest/extraction_orchestrator.py` (207 lines)
- ✅ Created `src/doc_ingest/converters/base.py` (Converter protocol, 91 lines)
- ✅ Created `src/doc_ingest/converters/registry.py` (ConverterRegistry, 69 lines)
- ✅ Created `tests/test_extraction_orchestrator.py` (11 tests, 100% pass)
- ✅ Quality-ordered source iteration with early exit on success
- ✅ Comprehensive error handling: fetch, validation, conversion failures
- ✅ Unexpected exceptions wrapped as `category="unknown"`
- ✅ All acceptance criteria met and verified via unit tests

**Key Design Decisions**:
- Used dataclass(order=True) on SourceCandidate for automatic sorting
- Converter protocol allows polymorphic handling by registry
- Empty result on all failures (None) vs. exception (chose None for explicit handling)
- Paywall flag propagation from ValidationResult to ExtractionAttempt

---

#### [DONE] TASK-DI-002: ProvenanceManager Implementation
**Addresses**: Spec 009 (provenance_manager.md)
**Priority**: P0
**Complexity**: SMALL (~150 lines, 1 file)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `src/doc_ingest/provenance_manager.py` (168 lines)
- ✅ Added `ProvenanceRecord` dataclass to `types.py` (42 lines)
- ✅ Created `tests/test_provenance_manager.py` (11 tests, 100% pass)
- ✅ Atomic writes via temp file + rename pattern (crash-safe)
- ✅ Load by document hash with None on missing/corrupted files
- ✅ UTF-8 encoding with Unicode identifier test coverage
- ✅ Deterministic JSON key ordering (sort_keys=True)
- ✅ Directory auto-creation (mkdir -p)
- ✅ All acceptance criteria met and verified via unit tests

**Key Design Decisions**:
- Hash computation uses primary identifier (doi > arxiv_id > pmc_id > local_path)
- Temp file created in same directory as target (ensures same filesystem for atomic rename)
- Corrupted JSON files treated as missing (return None) for resilience
- ProvenanceRecord uses `list[Any]` for attempts field to avoid circular import

---

#### [DONE] TASK-DI-003: ResultWriter Implementation
**Addresses**: Spec 012 (result_writer.md)
**Priority**: P0
**Complexity**: SMALL (~120 lines, 1 file)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `src/doc_ingest/result_writer.py` (121 lines)
- ✅ Added `ExtractionResult` dataclass to `types.py` (15 lines)
- ✅ Created `tests/test_result_writer.py` (11 tests, 100% pass)
- ✅ Delegates provenance writing to ProvenanceManager
- ✅ Writes output.md and summary.json only for successful extractions
- ✅ Deterministic directory naming using document hash
- ✅ UTF-8 encoding for non-ASCII content
- ✅ All acceptance criteria met and verified via unit tests

**Key Design Decisions**:
- ResultWriter receives ExtractionResult (markdown + provenance), not individual components
- summary.json structure includes document_hash, source_info, statistics, outcome, backend_used
- Failed extractions (markdown=None) skip output.md and summary.json writes
- Directory creation handled by both ProvenanceManager and ResultWriter (defensive programming)
- Note: ExtractionAttempt doesn't have warnings field, so warnings not included in summary.json

---

#### [DONE] TASK-DI-004: SourceRouter Implementation
**Addresses**: Spec 007 (source_router.md)
**Priority**: P0
**Complexity**: MEDIUM (~250 lines, 1 file)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `src/doc_ingest/source_router.py` (264 lines)
- ✅ Created `src/doc_ingest/source_discoverer.py` (minimal stub, 132 lines)
- ✅ Created `tests/test_source_router.py` (12 tests, 100% pass)
- ✅ Created `tests/test_source_discoverer.py` (12 tests, 100% pass)
- ✅ Resumability: existing success skips extraction, returns cached markdown
- ✅ Format override: skips discovery, creates single source with specified format
- ✅ Crash-safe: try/finally writes provenance even on exception
- ✅ Discovery phase: delegates to SourceDiscoverer
- ✅ Extraction phase: delegates to ExtractionOrchestrator
- ✅ Classification phase: delegates to OutcomeClassifier
- ✅ All acceptance criteria met and verified via unit tests

**Key Design Decisions**:
- SourceRouter takes WebFetcher as dependency (injected alongside orchestrator)
- Format override creates stub URL ("stub://type/value") when no local_path present
- Provenance written in finally block for crash safety (best-effort on write failure)
- SourceDiscoverer stub: local file discovery + mock API responses for DOI/arXiv
- ExtractionResult dataclass already existed in types.py (no modification needed)
- Pipeline version tracked in provenance ("0.1.0")

**Test Coverage**:
- Resumability: skip success, retry failed
- Format override: with and without local_path
- Crash safety: provenance written even on exception
- Discovery errors: reported in provenance
- All extraction attempts: recorded in provenance
- Timestamps and elapsed time: captured in provenance

---

### P1: High Priority (User Interface & Converters)

#### [DONE] TASK-DI-005: Minimal CLI Implementation
**Addresses**: Spec 011 (cli.md)
**Priority**: P1
**Complexity**: MEDIUM (~350 lines, 3 files)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `src/doc_ingest/cli.py` (328 lines)
- ✅ Created `src/agentic_mbse/cli/doc_ingest_cli.py` (54 lines)
- ✅ Registered `ingest` subcommand in `src/agentic_mbse/cli/__init__.py`
- ✅ Created `tests/test_doc_ingest_cli.py` (24 tests, 100% pass)
- ✅ Identifier validation: DOI, arXiv ID, PMC ID, local file paths
- ✅ Pipeline construction with proper dependency injection
- ✅ Exit code logic: 0 (success), 2 (fatal error)
- ✅ Comprehensive error handling and reporting
- ✅ Output directory auto-creation
- ✅ Format override support
- ✅ All acceptance criteria met and verified via unit tests

**Key Design Decisions**:
- Command name: `ingest` (not `extract` which already exists for PDF/DOCX local extraction)
- Identifier parsing priority: DOI > arXiv > PMC > local path
- Default output directory: `./data/ingested` (not specified in spec)
- Cache TTL: 30 days for discovery cache
- Exit code simplification: no EXIT_PARTIAL (1) in minimal MVP (reserved for future batch operations)

**Test Coverage**:
- Identifier validation: 16 tests covering all formats and edge cases
- Command execution: 8 tests covering success, failure, errors, format override
- All tests pass with mocked pipeline components

---

#### [DONE] TASK-DI-006: PDF Converter Implementation
**Addresses**: Spec 014 (pdf_converter.md)
**Priority**: P1
**Complexity**: MEDIUM (~200 lines, 1 file)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `src/doc_ingest/converters/pdf_converter.py` (235 lines)
- ✅ Updated `src/doc_ingest/converters/__init__.py` to export PyMuPDF4LLMConverter
- ✅ Created `tests/test_pdf_converter.py` (17 tests, 100% pass)
- ✅ Scanned PDF detection: Check first 3 pages for <50 chars of text
- ✅ Quality flags: table detection (markdown + PyMuPDF find_tables), heading structure (markdown headings), math indicators (Unicode symbols + keywords)
- ✅ ConversionError with category="needs_ocr" for scanned PDFs
- ✅ Warnings: Large PDFs (100+ pages), images present
- ✅ All acceptance criteria met and verified via unit tests

**Key Design Decisions**:
- Scanned PDF threshold: <50 characters across first 3 pages (heuristic)
- Table corruption detection: PyMuPDF find_tables vs. markdown table markers, inconsistent column counts
- Math detection: Unicode math symbols (∫∑√π²³·) + keywords (equation, formula) - heuristic since pymupdf4llm doesn't preserve LaTeX
- Unexpected exceptions wrapped as ConversionError(category="unknown")
- Type ignore comments for pymupdf/pymupdf4llm (no type stubs)

---

#### [DONE] TASK-DI-007: HTML Converters Implementation
**Addresses**: Spec 015 (html_converter.md)
**Priority**: P1
**Complexity**: MEDIUM (~300 lines, 2 classes)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `src/doc_ingest/converters/html_converter.py` (512 lines)
- ✅ Created `tests/test_html_converter.py` (28 tests, 100% pass)
- ✅ Updated `src/doc_ingest/converters/__init__.py` to export both converters
- ✅ Added `beautifulsoup4>=4.12` dependency to `pyproject.toml`
- ✅ Implemented `ArXivHTMLConverter` with MathML preservation
- ✅ Implemented `PublisherHTMLConverter` with paywall detection
- ✅ Truncation detection (< 1KB threshold)
- ✅ Paywall detection (8 common markers: "login required", "access denied", etc.)
- ✅ Body content validation for both converter types
- ✅ Quality flags: tables, math, figures, captions, headings
- ✅ All acceptance criteria met and verified via unit tests

**Key Design Decisions**:
- BeautifulSoup HTML parser used for both converters (permissive parsing)
- ArXiv: searches for `ltx_page_content` class or article/section tags
- Publisher: searches for article/main/section elements with class patterns
- MathML detection via `<math>` tags (ArXiv), math_preserved flag set to True
- Publisher math detected but math_preserved=False (varies by publisher)
- Markdown table extraction via pipe syntax with header separators
- Heading structure detection via `h1-h6` tags

**Test Coverage**:
- ArXiv: 12 tests covering validation, conversion, MathML, tables, figures, errors
- Publisher: 16 tests covering validation, paywall detection, conversion, quality flags
- All edge cases: truncation, invalid HTML, missing content, empty extraction
- 100% pass rate (28/28 tests)

---

#### [DONE] TASK-DI-008: Markdown Converters Implementation
**Addresses**: Spec 016 (markdown_converter.md)
**Priority**: P1
**Complexity**: MEDIUM (~300 lines, 2 classes)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `src/doc_ingest/converters/markdown_converter.py` (362 lines)
- ✅ Created `tests/test_markdown_converter.py` (29 tests, 100% pass)
- ✅ Updated `src/doc_ingest/converters/__init__.py` to export both converters
- ✅ Implemented `JATSPandocConverter` with article/body tag validation
- ✅ Implemented `DOCXPandocConverter` with ZIP header validation
- ✅ Pandoc subprocess integration with proper error handling
- ✅ Quality flags: tables, math, figures, captions, headings
- ✅ Comprehensive error handling: timeouts, missing binary, conversion failures
- ✅ All acceptance criteria met and verified via unit tests

**Key Design Decisions**:
- JATS validation: regex search for `<article>` and `<body>` tags
- DOCX validation: check for ZIP magic bytes (b"PK")
- Temp file cleanup: finally block ensures cleanup even on exception
- Pandoc timeout: 60 seconds for both JATS and DOCX
- ConversionError re-raise: avoid double-wrapping typed errors
- Quality detection: regex-based detection in markdown output

**Test Coverage**:
- JATS: 15 tests covering validation, conversion, math, figures, error handling
- DOCX: 14 tests covering validation, conversion, quality flags, error handling
- All edge cases: Pandoc failures, timeouts, missing binary, unexpected errors
- 100% pass rate (29/29 tests)

---

### P2: Medium Priority (Enhancements)

#### [DONE] TASK-DI-009: SourceDiscoverer Stub Implementation
**Addresses**: Discovery phase (referenced in spec 007)
**Priority**: P2
**Complexity**: SMALL (~132 lines, 1 file)
**Completed**: 2026-02-09 (implemented with TASK-DI-004)

**Implementation Summary**:
- ✅ Created `src/doc_ingest/source_discoverer.py` (132 lines)
- ✅ Created `tests/test_source_discoverer.py` (12 tests, 100% pass)
- ✅ Stub implementation for local file discovery + mock API responses
- ✅ Local file format inference from extension (.pdf, .xml, .html, .docx)
- ✅ Mock sources for DOI (JATS + PDF) and arXiv (HTML)
- ✅ Cache integration via DiscoveryCache
- ✅ Quality tier assignment based on format type

**Key Design Decisions**:
- Local file discovery checks file existence before creating SourceCandidate
- DOI stub creates both JATS (tier 1) and PDF (tier 4) sources for testing
- arXiv stub creates HTML source (tier 2)
- Format inference: .pdf → pdf, .xml → jats_xml, .html → publisher_html, .docx → docx
- Quality tiers: PDF=4, others=1 (simplified for stub)
- Sources automatically sorted by quality tier

**Depends On**:
- ✅ Spec 003 (SourceCandidate)
- ✅ Spec 013 (DiscoveryCache)

---

#### [DONE] TASK-DI-010: Batch Processing CLI Commands
**Addresses**: Spec 011 (cli.md) — Full implementation
**Priority**: P2
**Complexity**: MEDIUM (~400 lines)
**Completed**: 2026-02-09

**Implementation Summary**:
- ✅ Created `cmd_extract_batch()` for JSONL batch processing (346 lines total CLI additions)
- ✅ Created `cmd_triage_report()` for provenance analysis and failure categorization
- ✅ Created `cmd_retry_failed()` for retrying failed/partial extractions
- ✅ Created `cmd_clear_cache()` for cache invalidation (specific identifier, all, or expired)
- ✅ Auto-generates triage report on batch failures for failure analysis
- ✅ EXIT_PARTIAL (1) for batch operations with partial success
- ✅ 15 comprehensive unit tests covering all batch commands (100% pass rate)
- ✅ Type checking (mypy) passes, linting (ruff) passes
- ✅ Files: `cli.py` (+346 lines), `test_doc_ingest_cli.py` (+15 tests, 100% pass)

**Implementation Details**:
- JSONL parsing: Skips empty lines, validates JSON, creates DocumentIdentifiers
- Triage report: Groups failures by category, shows discovery errors, provides next steps
- Retry logic: Scans provenance files, skips successes, retries only failures/partials
- Cache clearing: Supports specific identifier, all entries, or age-based clearing
- Exit codes: 0 (all success), 1 (partial batch), 2 (fatal error)
- Progress tracking: Per-document status updates during batch processing

**Test Coverage**:
- Batch: all success, partial success, invalid JSON, missing file, empty lines
- Triage: report generation, missing output dir, custom report path
- Retry: retries only failures, no failures found, missing output dir
- Cache: clear specific, clear all, clear expired, missing cache dir
- 15/15 tests passing (100% pass rate)

**Acceptance Criteria Met**:
- ✅ `extract-batch input.jsonl` → processes all documents, shows progress
- ✅ Partial batch failure → exit 1, auto-generates triage report
- ✅ `retry-failed output_dir` → retries only failed documents, skips successes
- ✅ `clear-cache --identifier=doi:10.x` → removes specific cache entry
- ✅ `clear-cache --max-age-days=30` → removes expired entries
- ✅ `clear-cache` (no args) → removes all cache entries

**Key Design Decisions**:
- Triage report auto-generated on batch failures for immediate visibility
- Retry skips successful extractions to avoid duplicate work
- Cache clearing uses DiscoveryCache.clear() method with optional max_age_days
- Progress messages show document count and display_key for easy tracking
- Error messages include line numbers for JSONL parsing failures

**Depends On**:
- ✅ TASK-DI-005 (Minimal CLI)

---

### P3: Low Priority (Future Enhancements)

#### TASK-DI-011: Full API Integration (OpenAlex, arXiv, PMC)
**Addresses**: Source discovery enhancement
**Priority**: P3
**Complexity**: LARGE (~500+ lines)
**Estimated Time**: 3-5 days

**Problem**: Need real API integration for DOI/arXiv/PMC discovery.

**Requirements**:
- OpenAlex API client for DOI resolution
- arXiv API client for arXiv ID resolution
- PubMed Central API for PMC ID resolution
- Rate limiting and retry logic
- Comprehensive error handling

**Status**: Defer to post-MVP (use stub discoverer for now)

---

## Sequencing & Dependencies

```
Foundation (Complete)
  ├─ Spec 001-006, 010, 013, 017 ✅
  │
  └─ Critical Path (P0)
      ├─ TASK-DI-001 (ExtractionOrchestrator) ──┐
      ├─ TASK-DI-002 (ProvenanceManager) ───────┤
      ├─ TASK-DI-003 (ResultWriter) ────────────┤
      │                                          ├─→ TASK-DI-004 (SourceRouter)
      └─ ConverterRegistry stub ────────────────┘        │
                                                          │
                                                          ├─→ TASK-DI-005 (Minimal CLI)
                                                          │
User Interface (P1)                                       │
  ├─ TASK-DI-006 (PDF Converter) ─────────────────────────┤
  ├─ TASK-DI-007 (HTML Converters) ───────────────────────┤
  └─ TASK-DI-008 (Markdown Converters) ────────────────────┘

Enhancements (P2)
  ├─ TASK-DI-009 (SourceDiscoverer Stub) → TASK-DI-004
  └─ TASK-DI-010 (Batch CLI Commands) → TASK-DI-005

Future (P3)
  └─ TASK-DI-011 (Full API Integration) → TASK-DI-009
```

**Critical Path**: TASK-DI-001 → TASK-DI-002 → TASK-DI-003 → TASK-DI-004 → TASK-DI-005

---

## Recommended Implementation Sequence

### Phase 1: Core Orchestration (Week 1)
**Goal**: Complete the extraction pipeline backbone

1. **TASK-DI-001** (ExtractionOrchestrator) — P0, MEDIUM, 1-2 days
2. **TASK-DI-002** (ProvenanceManager) — P0, SMALL, 0.5-1 day
3. **TASK-DI-003** (ResultWriter) — P0, SMALL, 0.5 day
4. **TASK-DI-009** (SourceDiscoverer Stub) — P2, SMALL, 0.5-1 day
5. **TASK-DI-004** (SourceRouter) — P0, MEDIUM, 1-2 days

**Target**: 5-7 implementation days, full pipeline tested end-to-end

### Phase 2: User Interface & Converters (Week 2-3)
**Goal**: Enable actual document extraction

6. **TASK-DI-006** (PDF Converter) — P1, MEDIUM, 1-2 days
7. **TASK-DI-007** (HTML Converters) — P1, MEDIUM, 1.5-2 days
8. **TASK-DI-008** (Markdown Converters) — P1, MEDIUM, 1.5-2 days
9. **TASK-DI-005** (Minimal CLI) — P1, MEDIUM, 1-2 days

**Target**: 6-8 implementation days, MVP functional

### Phase 3: Enhancements (Week 4+)
**Goal**: Batch processing and production features

10. **TASK-DI-010** (Batch CLI Commands) — P2, MEDIUM, 1-2 days

**Target**: 1-2 implementation days, production-ready

### Phase 4: Future Work (Backlog)
11. **TASK-DI-011** (Full API Integration) — P3, LARGE, defer

---

## Verification Matrix

| Task | Unit Tests | Integration Tests | Manual Verification |
|------|------------|-------------------|---------------------|
| TASK-DI-001 | ✅ Orchestrator logic | ✅ Mock converters | ❌ N/A |
| TASK-DI-002 | ✅ Write/load cycle | ✅ Crash simulation | ✅ Check JSON files |
| TASK-DI-003 | ✅ Write logic | ✅ Success/failure paths | ✅ Check outputs |
| TASK-DI-004 | ✅ Resumability | ✅ Full pipeline mock | ✅ Extract test doc |
| TASK-DI-005 | ✅ Arg parsing | ✅ CLI commands | ✅ Run extract command |
| TASK-DI-006 | ✅ PDF extraction | ✅ Pipeline integration | ✅ Test PDF file |
| TASK-DI-007 | ✅ HTML extraction | ✅ Pipeline integration | ✅ Test HTML file |
| TASK-DI-008 | ✅ Markdown conversion | ✅ Pipeline integration | ✅ Test JATS/DOCX |

---

## Notes

### Implementation Guidelines

1. **Test-First Approach**: Write tests before implementation for each component
2. **Minimal Stubs**: Create minimal stubs (ConverterRegistry, SourceDiscoverer) to unblock critical path
3. **Incremental Integration**: Test each component in isolation before full pipeline integration
4. **Clear Error Messages**: All validation failures should have actionable error messages
5. **Atomic Operations**: Use temp file + rename for all file writes

### Known Dependencies

**External Libraries**:
- `pymupdf4llm` (PDF extraction)
- `requests` or `httpx` (HTTP fetching) — Note: Already implemented in WebFetcher
- `beautifulsoup4` (HTML parsing)
- `pandoc` (system binary, JATS/DOCX conversion)

**Python Standard Library**:
- `dataclasses`, `pathlib`, `json`, `hashlib`, `subprocess`, `tempfile`

### Design Decisions

1. **ConverterRegistry**: Simple dict-based registry mapping format → converter class
2. **SourceDiscoverer**: Stub implementation for MVP, full API integration deferred
3. **Exit codes**: 0=success, 1=partial (batch), 2=fatal (follows CLI conventions)
4. **Provenance format**: JSON with UTF-8 encoding, deterministic field ordering
5. **Quality tiers**: Fixed mapping (JATS=1, arXiv=2, Publisher=3, PDF=4, DOCX=5)

### Missing Data Classes

Based on spec analysis, the following data classes need to be added to `types.py`:

1. **ProvenanceRecord** (spec 009):
   - Fields: document identifiers, discovery info, all attempts, final outcome, failure category, timestamps, pipeline version

2. **ExtractionResult** (spec 007):
   - Fields: markdown (str), provenance (ProvenanceRecord)

**Note**: `ExtractionAttempt` already exists in `outcome_classifier.py:17-33`

---

## Next Steps

**Immediate**: Begin TASK-DI-001 (ExtractionOrchestrator)
**Week 1 Target**: Complete Phase 1 (Tasks 1-5), full pipeline tested
**Week 2-3 Target**: Complete Phase 2 (Tasks 6-9), MVP functional
**Week 4 Target**: Complete Phase 3 (Task 10), production-ready

---

**Last Review**: 2026-02-09 (Planning iteration with spec analysis)
**Next Review**: After TASK-DI-001 completion
**Status**: Ready for implementation — critical path identified, dependencies validated, missing data classes identified

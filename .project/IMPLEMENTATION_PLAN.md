# Implementation Plan: Document Ingestion Pipeline

**Date**: 2026-02-09
**Status**: Active Planning Iteration (Updated)
**Last Updated**: 2026-02-09 17:45
**Branch**: `ralph/doc-ingest`

---

## Executive Summary

**Current State**: Foundation + ExtractionOrchestrator + ProvenanceManager + ResultWriter complete (12/17 specs + converter infrastructure)
**Next Milestone**: Complete core orchestration layer (spec 007 SourceRouter)
**Critical Path**: SourceRouter → CLI → Converters

**Technology Stack**: Python 3.11+, UV package manager, pytest, pydantic
**Verification**: Unit tests + integration tests for each component

---

## Specification Coverage Analysis

### ✅ Completed Specifications (11 specs)

| Spec | Component | Implementation | Lines | Tests |
|------|-----------|----------------|-------|-------|
| **001** | DocumentIdentifiers | `src/doc_ingest/types.py:53-109` | 57 | ✅ |
| **002** | QualityFlags | `src/doc_ingest/types.py:33-51` | 19 | ✅ |
| **003** | SourceCandidate | `src/doc_ingest/types.py:111-150` | 40 | ✅ |
| **004** | ConversionResult | `src/doc_ingest/types.py:182-197` | 16 | ✅ |
| **005** | WebFetcher | `src/doc_ingest/web_fetcher.py` | 134 | ✅ |
| **006** | OutcomeClassifier | `src/doc_ingest/outcome_classifier.py` | 134 | ✅ |
| **008** | ExtractionOrchestrator | `src/doc_ingest/extraction_orchestrator.py` | 207 | ✅ |
| **009** | ProvenanceManager | `src/doc_ingest/provenance_manager.py` | 168 | ✅ |
| **010** | ValidationResult | `src/doc_ingest/types.py:152-180` | 29 | ✅ |
| **012** | ResultWriter | `src/doc_ingest/result_writer.py` | 121 | ✅ |
| **013** | DiscoveryCache | `src/doc_ingest/discovery_cache.py` | 162 | ✅ |
| **017** | ConversionError | `src/doc_ingest/types.py:199-216` | 18 | ✅ |
| N/A | ProvenanceRecord | `src/doc_ingest/types.py:254-295` | 42 | ✅ |
| N/A | ExtractionResult | `src/doc_ingest/types.py:297-311` | 15 | ✅ |
| N/A | Converter (protocol) | `src/doc_ingest/converters/base.py` | 91 | ✅ |
| N/A | ConverterRegistry | `src/doc_ingest/converters/registry.py` | 69 | ✅ |

**Evidence**: All classes found via code search, commits 756155d, 7648660, 2dc70c1, 3626798, 1261e47, ef5a718, [current]
**Note**: `ExtractionAttempt` dataclass exists in `outcome_classifier.py:17-33`, `DocumentOutcome` literal in `types.py:252`

### 🚧 In Progress Specifications (0 specs)

*None currently in progress*

### ✅ Recently Completed

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

### ⏳ Pending Specifications (5 specs)

**Core Pipeline (P0 - Critical Path):**
- **Spec 007**: SourceRouter — Coordinate discovery → extraction → classification → persistence

**CLI Layer (P1 - User Interface):**
- **Spec 011**: CLI interface — `extract`, `extract-batch`, `triage-report`, `retry-failed`, `clear-cache`

**Converters (P1 - Format Support):**
- **Spec 014**: PDF Converter (PyMuPDF4LLMConverter) — Extract scanned/native PDFs
- **Spec 015**: HTML Converters (ArXivHTMLConverter, PublisherHTMLConverter) — Parse structured HTML
- **Spec 016**: Markdown Converters (JATSPandocConverter, DOCXPandocConverter) — Pandoc-based conversion

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

#### TASK-DI-004: SourceRouter Implementation
**Addresses**: Spec 007 (source_router.md)
**Priority**: P0
**Complexity**: MEDIUM (~250 lines, 1 file)
**Estimated Time**: 1-2 days

**Problem**: Need the top-level orchestrator that coordinates discovery → extraction → classification → persistence.

**Requirements** (from spec 007):
- Check existing provenance, skip if outcome="success" (resumability)
- Retry failed/partial documents when re-run
- Call SourceDiscoverer for candidate sources
- Call ExtractionOrchestrator for extraction attempts
- Call OutcomeClassifier for final outcome
- Write provenance via try/finally (crash-safe)
- Support `--format` override to skip discovery

**Implementation Steps**:
1. Create `src/doc_ingest/source_router.py`
2. Define `ExtractionResult` dataclass in `types.py` (markdown, provenance)
3. Implement `SourceRouter.__init__(discoverer, orchestrator, classifier, prov_manager)`
4. Implement `extract(identifiers, output_dir, format_override=None) -> ExtractionResult`
5. Add resumability check (load existing provenance)
6. Add discovery phase (with format override handling)
7. Add extraction phase via orchestrator
8. Add classification phase
9. Add try/finally provenance write
10. Write unit tests for resumability, format override
11. Write integration tests for full pipeline

**Files Created/Modified**:
- `src/doc_ingest/source_router.py` (new, ~250 lines)
- `src/doc_ingest/types.py` (add ExtractionResult dataclass)
- `tests/test_source_router.py` (new, ~300 lines)

**Acceptance Criteria**:
- Existing success → skip extraction, return cached markdown
- Existing failed → retry extraction, update provenance
- `format_override="pdf"` → skip discovery, attempt only PDF
- Crash after discovery → finally writes provenance with attempts
- Successful extraction → return ExtractionResult with markdown + provenance

**Verified By**:
- Unit tests: `test_resumability_skip_success`, `test_format_override`
- Integration tests: `test_full_pipeline_mock`, `test_crash_safety`

**Depends On**:
- ✅ TASK-DI-001 (ExtractionOrchestrator)
- ✅ TASK-DI-002 (ProvenanceManager)
- ✅ TASK-DI-003 (ResultWriter)
- ✅ Spec 006 (OutcomeClassifier)
- ⏳ SourceDiscoverer (create minimal stub)

---

### P1: High Priority (User Interface & Converters)

#### TASK-DI-005: Minimal CLI Implementation
**Addresses**: Spec 011 (cli.md)
**Priority**: P1
**Complexity**: MEDIUM (~300 lines, 1 file)
**Estimated Time**: 1-2 days

**Problem**: Need `agentic-mbse extract` command for single document extraction.

**Requirements** (from spec 011):
- `extract` command: single document with format override
- Typed exit codes: 0 (success), 1 (partial), 2 (fatal)
- Identifier validation (DOI, arXiv ID, local path)
- Auto-create output directories
- Structured error messages

**Implementation Steps** (Minimal MVP):
1. Extend `src/agentic_mbse/cli/__init__.py` with extract subcommand
2. Create `src/doc_ingest/cli.py` for core CLI logic
3. Implement argument parser for `extract` command
4. Implement identifier validation
5. Wire SourceRouter for single-document extraction
6. Implement exit code logic (0/1/2)
7. Write integration tests for CLI commands
8. Defer: `extract-batch`, `triage-report`, `retry-failed`, `clear-cache` (post-MVP)

**Files Created/Modified**:
- `src/doc_ingest/cli.py` (new, ~300 lines)
- `src/agentic_mbse/cli/__init__.py` (register extract subcommand)
- `tests/test_doc_ingest_cli.py` (new, ~200 lines)

**Acceptance Criteria**:
- `agentic-mbse extract 10.1234/foo` → exit 0, write output.md
- Invalid identifier → exit 2 with message "Invalid identifier format"
- Missing output dir → auto-create
- Network failure → exit 2 with clear message

**Verified By**:
- Integration tests: `test_cli_extract_success`, `test_cli_extract_invalid_id`

**Depends On**:
- ✅ TASK-DI-004 (SourceRouter)

---

#### TASK-DI-006: PDF Converter Implementation
**Addresses**: Spec 014 (pdf_converter.md)
**Priority**: P1
**Complexity**: MEDIUM (~200 lines, 1 file)
**Estimated Time**: 1-2 days

**Problem**: Need PDF extraction with scanned document detection.

**Requirements** (from spec 014):
- Implement `Converter` interface with `can_convert()`, `validate_source()`, `convert()`, `name`
- Validate for extractable text (detect scanned PDFs)
- Raise `ConversionError(category="needs_ocr")` for scanned documents
- Report QualityFlags: tables, table_corruption, heading_structure
- Converter name: "PyMuPDF4LLMConverter"
- Use pymupdf4llm library for extraction

**Implementation Steps**:
1. Create `src/doc_ingest/converters/` directory
2. Create `src/doc_ingest/converters/base.py` with `Converter` protocol/ABC
3. Create `src/doc_ingest/converters/pdf_converter.py`
4. Define `PyMuPDF4LLMConverter` class
5. Implement `validate_source(content: bytes) -> ValidationResult`
6. Implement `convert(content: bytes) -> ConversionResult`
7. Add scanned PDF detection (text extraction check)
8. Add QualityFlags population
9. Write unit tests with sample PDFs
10. Create `src/doc_ingest/converters/registry.py` for converter registry

**Files Created/Modified**:
- `src/doc_ingest/converters/__init__.py` (new)
- `src/doc_ingest/converters/base.py` (new, ~50 lines - Converter interface)
- `src/doc_ingest/converters/pdf_converter.py` (new, ~200 lines)
- `src/doc_ingest/converters/registry.py` (new, ~50 lines)
- `tests/test_pdf_converter.py` (new, ~250 lines)
- `tests/fixtures/sample.pdf` (test fixture)

**Acceptance Criteria**:
- Native PDF → ConversionResult with markdown
- Scanned PDF → raises `ConversionError(category="needs_ocr")`
- ValidationResult reports content_length, has_body_content
- QualityFlags reports tables, heading_structure

**Verified By**:
- Unit tests: `test_convert_native_pdf`, `test_convert_scanned_pdf_raises`
- Integration tests: `test_pdf_in_full_pipeline`

**Depends On**:
- ✅ Spec 004 (ConversionResult)
- ✅ Spec 010 (ValidationResult)
- ✅ Spec 017 (ConversionError)

---

#### TASK-DI-007: HTML Converters Implementation
**Addresses**: Spec 015 (html_converter.md)
**Priority**: P1
**Complexity**: MEDIUM (~300 lines, 2 classes)
**Estimated Time**: 1.5-2 days

**Problem**: Need ArXiv and Publisher HTML extraction with paywall detection.

**Requirements** (from spec 015):
- ArXivHTMLConverter: Parse arXiv HTML5 with MathML preservation
- PublisherHTMLConverter: Parse publisher HTML with paywall detection
- Detect paywalls, truncation, missing body content
- Return ValidationResult with is_paywall, is_truncated flags
- Preserve MathML in arXiv (set `quality_flags.has_math=True`, `math_preserved=True`)

**Implementation Steps**:
1. Create `src/doc_ingest/converters/html_converter.py`
2. Implement `ArXivHTMLConverter` class
3. Implement `PublisherHTMLConverter` class
4. Add paywall detection (common markers: "access-denied", "subscribe")
5. Add truncation detection (content_length < 1KB)
6. Add body content detection
7. Add MathML preservation logic for arXiv
8. Write unit tests with mock HTML
9. Add to ConverterRegistry

**Files Created/Modified**:
- `src/doc_ingest/converters/html_converter.py` (new, ~300 lines)
- `tests/test_html_converter.py` (new, ~350 lines)

**Acceptance Criteria**:
- Valid ArXiv HTML → ConversionResult with MathML preserved
- Publisher HTML with paywall → ValidationResult.is_paywall=True
- Truncated response → ValidationResult.is_truncated=True
- Missing body → ValidationResult.has_body_content=False

**Verified By**:
- Unit tests: `test_arxiv_html`, `test_paywall_detection`, `test_truncation`

**Depends On**:
- ✅ Spec 004, 010, 017

---

#### TASK-DI-008: Markdown Converters Implementation
**Addresses**: Spec 016 (markdown_converter.md)
**Priority**: P1
**Complexity**: MEDIUM (~300 lines, 2 classes)
**Estimated Time**: 1.5-2 days

**Problem**: Need JATS XML and DOCX conversion via Pandoc.

**Requirements** (from spec 016):
- JATSPandocConverter: Convert JATS XML to markdown
- DOCXPandocConverter: Convert DOCX to markdown
- Validate for body content in JATS (`<article>`, `<body>` tags)
- Validate DOCX for binary format (ZIP header magic bytes)
- Use Pandoc subprocess for conversion
- Handle Pandoc errors gracefully

**Implementation Steps**:
1. Create `src/doc_ingest/converters/markdown_converter.py`
2. Implement `JATSPandocConverter` class
3. Implement `DOCXPandocConverter` class
4. Add JATS body content validation
5. Add DOCX binary format validation
6. Add Pandoc subprocess wrapper
7. Handle Pandoc errors gracefully
8. Write unit tests with sample files
9. Add to ConverterRegistry

**Files Created/Modified**:
- `src/doc_ingest/converters/markdown_converter.py` (new, ~300 lines)
- `tests/test_markdown_converter.py` (new, ~300 lines)
- `tests/fixtures/sample.jats.xml`, `tests/fixtures/sample.docx`

**Acceptance Criteria**:
- Valid JATS XML → ConversionResult
- JATS missing body → ValidationResult.has_body_content=False
- Valid DOCX → ConversionResult
- Pandoc failure → raises ConversionError

**Verified By**:
- Unit tests: `test_jats_conversion`, `test_docx_conversion`

**Depends On**:
- ✅ Spec 004, 010, 017
- External: Pandoc binary installed

---

### P2: Medium Priority (Enhancements)

#### TASK-DI-009: SourceDiscoverer Stub Implementation
**Addresses**: Discovery phase (referenced in spec 007)
**Priority**: P2
**Complexity**: SMALL (~100 lines, 1 file)
**Estimated Time**: 0.5-1 day

**Problem**: Need basic discovery functionality for testing, defer full API integration.

**Requirements**:
- Stub discoverer that returns local file sources
- Support DOI → mock API response (for testing)
- Defer: Full OpenAlex, arXiv, PMC API integration (post-MVP)

**Implementation Steps**:
1. Create `src/doc_ingest/source_discoverer.py`
2. Implement `SourceDiscoverer.__init__(cache: DiscoveryCache)`
3. Implement `discover(identifiers) -> tuple[list[SourceCandidate], list[str]]`
4. Add local file path → SourceCandidate logic
5. Add DOI stub → mock sources
6. Write unit tests

**Files Created/Modified**:
- `src/doc_ingest/source_discoverer.py` (new, ~100 lines)
- `tests/test_source_discoverer.py` (new, ~150 lines)

**Acceptance Criteria**:
- Local path → single SourceCandidate with local_path set
- DOI → stub sources (for testing pipeline)
- Caches discovered sources via DiscoveryCache

**Verified By**:
- Unit tests: `test_discover_local_file`, `test_discover_doi_stub`

**Depends On**:
- ✅ Spec 003 (SourceCandidate)
- ✅ Spec 013 (DiscoveryCache)

---

#### TASK-DI-010: Batch Processing CLI Commands
**Addresses**: Spec 011 (cli.md) — Full implementation
**Priority**: P2
**Complexity**: MEDIUM (~200 lines)
**Estimated Time**: 1-2 days

**Problem**: Need batch processing, triage reports, and cache management.

**Requirements** (from spec 011):
- `extract-batch` command: Process JSONL file
- `triage-report` command: Analyze provenance records
- `retry-failed` command: Retry failed documents
- `clear-cache` command: Invalidate cache entries

**Implementation Steps**:
1. Extend `src/doc_ingest/cli.py` with batch commands
2. Implement JSONL parsing and validation
3. Implement triage report generation
4. Implement retry-failed logic
5. Implement cache clearing
6. Write integration tests

**Files Created/Modified**:
- `src/doc_ingest/cli.py` (extend, +200 lines)
- `tests/test_doc_ingest_cli.py` (extend, +300 lines)

**Acceptance Criteria**:
- `extract-batch input.jsonl` → processes all documents
- Partial batch failure → exit 1, generate triage report
- `retry-failed output_dir` → retries only failed documents
- `clear-cache --identifier=doi:10.x` → removes cache entry

**Verified By**:
- Integration tests: `test_batch_processing`, `test_retry_failed`

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

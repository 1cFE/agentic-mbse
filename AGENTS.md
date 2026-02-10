# AGENTS.md

## Implementation Status (2026-02-09)

**Production-Ready MVP: 17 specs + batch CLI — All P0-P2 tasks complete**

Completed:
- ✅ Spec 001: DocumentIdentifiers - priority resolution, display_key, cache keying
- ✅ Spec 002: QualityFlags - extraction quality indicators (tables, math, figures, structure)
- ✅ Spec 003: SourceCandidate - format types, quality tiers, sortable prioritization
- ✅ Spec 004: ConversionResult - markdown output, warnings, quality flags, converter provenance
- ✅ Spec 005: WebFetcher - HTTP(S)/local fetching, protocol validation, size limits, timeouts, typed errors
- ✅ Spec 006: OutcomeClassifier - extraction outcome determination, failure category assignment, typed classification
- ✅ Spec 007: SourceRouter - top-level orchestrator, resumability, format override, crash-safe provenance
- ✅ Spec 008: ExtractionOrchestrator - quality-ordered extraction, converter registry integration
- ✅ Spec 009: ProvenanceManager - atomic writes, UTF-8 encoding, hash-based directory naming
- ✅ Spec 010: ValidationResult - source validation outcomes (paywall, truncation, content detection)
- ✅ Spec 011: CLI (full) - Single + batch processing, triage reports, retry logic, cache management
- ✅ Spec 012: ResultWriter - output.md, summary.json, provenance delegation
- ✅ Spec 013: DiscoveryCache - TTL-based caching, freshness checks, per-identifier invalidation, bulk clearing
- ✅ Spec 014: PyMuPDF4LLMConverter - PDF extraction, scanned detection, quality flags
- ✅ Spec 015: ArXivHTMLConverter & PublisherHTMLConverter - HTML extraction, MathML preservation, paywall detection
- ✅ Spec 016: JATSPandocConverter & DOCXPandocConverter - Pandoc-based conversion, quality flag detection
- ✅ Spec 017: ConversionError - typed exception with FailureCategory, structured details

Next: Phase 3 enhancements (full API integration with OpenAlex/arXiv/PMC - P3)

## Build & Run

```bash
# Install dependencies
uv sync

# Run document ingestion (DOI)
uv run agentic-mbse ingest 10.1234/example --output-dir data/ingested

# Run document ingestion (arXiv)
uv run agentic-mbse ingest 2301.12345 --output-dir data/ingested

# Run document ingestion with format override
uv run agentic-mbse ingest 10.1234/example --format pdf

# Directory creation is automatic
# Exit codes: 0 (success), 1 (partial batch), 2 (fatal error)

# Batch processing from JSONL file
uv run agentic-mbse ingest-batch input.jsonl --output-dir data/ingested

# Generate triage report for failed extractions
uv run agentic-mbse triage-report data/ingested

# Retry only failed/partial extractions
uv run agentic-mbse retry-failed data/ingested

# Cache management
uv run agentic-mbse clear-cache data/ingested/.cache --identifier doi:10.1234/example
uv run agentic-mbse clear-cache data/ingested/.cache --max-age-days 30
uv run agentic-mbse clear-cache data/ingested/.cache  # Clear all
```

## Validation

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest --cov=src/doc_ingest tests/

# Type checking
uv run mypy src/

# Linting and formatting
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Codebase Patterns

**Project structure:**
- `src/doc_ingest/`: Core library (CLI, converters, orchestration, provenance)
- `tests/`: Mirror source structure for test discovery
- Converters in `src/doc_ingest/converters/`, each implements `BaseConverter`

**Key conventions:**
- All converters raise `ConversionError(category=FailureCategory)` for typed failures
- Each converter implements `name` property, `convert()`, and `validate_source()`
- `ConversionResult` includes `converter_name` field for provenance tracking
- Use dataclasses (`QualityFlags`, `SourceMetadata`, `ValidationDetails`) not dicts
- `DocumentIdentifiers`: Use `primary_identifier()` for keys, `display_key()` for logs

**Error handling:**
- Converter failures → `ConversionError` with typed category
- Cascade continues on failure (try next converter)
- Provenance saved in try/finally blocks (best-effort crash-safety)

**Import patterns:**
- Absolute imports from `src.doc_ingest.*`
- No circular dependencies (converters → base, orchestrator → converters)

## Known Gotchas

**Type checking dependencies:**
- Third-party libraries without inline types need stub packages for mypy
- `requests` library requires `types-requests` in dev dependencies
- Install via: `uv add --dev types-{package-name}`

**WebFetcher implementation (spec 005):**
- Fetch method supports both URLs and local paths via single interface
- Protocol validation happens early (allowlist: http, https only)
- Size limits enforced twice: from Content-Length header AND during streaming (defense in depth)
- Streaming download prevents memory exhaustion on large files
- All network errors mapped to typed FetchError categories for proper orchestrator handling
- requests.get uses stream=True + iter_content for chunked reading
- Timeout applies to entire request, not per chunk

**Converter implementation:**
- MUST set `self.name` and populate `converter_name` in result
- Validation logic goes in `validate_source()`, NOT in orchestrator
- Raise typed `ConversionError(category="source_validation_failed")`, never bare exceptions
- Category must be from FailureCategory literal (needs_ocr, table_corruption, no_source_found, source_validation_failed, conversion_timeout, unsupported_format, api_error, network_error, unknown)

**PyMuPDF4LLMConverter (spec 014):**
- pymupdf and pymupdf4llm require `# type: ignore[import-untyped]` (no stubs)
- Scanned PDF detection: Check first 3 pages for <50 chars of text (heuristic threshold)
- Table detection: Use both PyMuPDF `find_tables()` AND markdown table markers (`|...|`)
- Table corruption: Detected when PyMuPDF finds tables but markdown has none, or inconsistent column counts
- Math detection: Unicode symbols (∫∑√π²³·) + keywords (equation, formula) - pymupdf4llm doesn't preserve LaTeX
- Test PDFs: Create programmatically with PyMuPDF in fixtures (no need for binary files)

**Batch CLI implementation (TASK-DI-010):**
- ProvenanceRecord serialization: Use `asdict(record)` from dataclasses, NOT `model_dump_json()` (not a Pydantic model)
- FailureCategory type strictness: When assigning to `str` variable, use explicit type annotation to avoid mypy errors
- Empty line handling: Always skip empty/whitespace lines in JSONL parsing (use `line.strip()`)
- Triage report generation: Use markdown with bold fields (`**Total documents**:`) for clarity
- Cache clearing: DiscoveryCache.clear() accepts optional `max_age_days` parameter (no separate clear_all/clear_expired methods)
- Exit codes: Return EXIT_PARTIAL (1) for partial batch success, not EXIT_FATAL (2)
- Large PDF warning: 100+ pages threshold (to alert about potential incompleteness)

**Pandoc Converters (spec 016 - JATSPandocConverter, DOCXPandocConverter):**
- Pandoc invoked as subprocess, not Python library (no Python bindings available)
- Temp file cleanup: Use finally block to ensure cleanup even on exception
- JATS validation: Regex search for `<article>` and `<body>` tags (case-insensitive)
- DOCX validation: Check for ZIP magic bytes (b"PK") at start of content
- Conversion timeout: 60 seconds hardcoded (prevents hangs on malformed documents)
- ConversionError re-raise: Avoid double-wrapping typed errors (check isinstance before wrapping)
- Pandoc stderr: Include as warnings even on success (Pandoc often emits non-fatal warnings)
- Missing Pandoc binary: Raise ConversionError with category="unsupported_format" and details={"missing_dependency": "pandoc"}
- Quality flag detection: Regex-based on markdown output (tables: `\|.*\|`, headings: `^#{1,6}\s+`, math: `\$.*\$`, figures: `!\[.*?\]\(.*?\)`)
- Test strategy: Mock subprocess.run to avoid external Pandoc dependency in tests

**Provenance tracking:**
- `ProvenanceManager` is pure persistence (no staleness logic)
- `DiscoveryCache` handles freshness/staleness checks (injectable, separate class)
- Triage metadata stored alongside discovery_timestamp for staleness detection
- Hash computation in ProvenanceManager reused by ResultWriter via `provenance_manager._compute_hash()`

**CLI implementation (spec 011):**
- Command name: `ingest` (avoids collision with existing `extract` for local PDF/DOCX)
- Identifier parsing priority: DOI > arXiv > PMC > local path (matches DocumentIdentifiers)
- DOI regex: `^10\.\d+/.+$` (strict validation)
- arXiv regex: `^\d{4}\.\d{4,5}(v\d+)?$` (handles versioned IDs)
- PMC regex: `^PMC\d+$` (case-insensitive, normalized to uppercase)
- Local paths: validated via Path.exists() and is_file() checks
- ExtractionOrchestrator.__init__ takes only `registry` parameter (no fetcher)
- ProvenanceManager.__init__ takes no parameters (not base_dir)
- ResultWriter.write signature: `write(output_dir: Path, result: ExtractionResult)`
- DiscoveryCache requires `ttl_days` parameter in __init__
- Document hash computed via: `sha256(f"{id_type}:{id_value}".encode()).hexdigest()[:16]`

**ResultWriter implementation (spec 012):**
- Takes ExtractionResult (markdown + provenance), not individual components
- Delegates provenance writes to ProvenanceManager (separation of concerns)
- Only writes output.md and summary.json for successful extractions (markdown != None)
- summary.json does NOT include warnings field (ExtractionAttempt doesn't have warnings)
- Directory creation defensive: both ProvenanceManager and ResultWriter create dirs (idempotent)

**DiscoveryCache implementation (spec 013):**
- Cache files stored with SHA-256 hash of identifier key for safe filenames
- JSON format with timestamp, identifier_key, and sources list
- Atomic writes via temp file (prevents corruption on crash)
- TTL freshness checks: age_days = (current_time - timestamp) / 86400
- `get()` returns None for missing or stale entries (transparent to caller)
- `clear(max_age_days)` supports selective removal (None = remove all)
- Corrupted cache files treated as missing (no exceptions raised)

**CLI behavior:**
- `--format` controls routing strategy (jina/readability/auto)
- `format_hint` in provenance is local file type declaration (separate concept)
- Batch mode continues on individual failures, reports aggregate status
- Exit code 1 if ANY failure in batch, not just all failures

**Multi-identifier resolution:**
- `all_identifiers()` returns merged list (URL + file path + DOI)
- Cache invalidation targets specific identifier, not all variants
- Use `primary_identifier()` for deduplication/caching, `display_key()` for user-facing logs

**SourceRouter implementation (spec 007):**
- Takes WebFetcher as injected dependency alongside other orchestration components
- Format override creates stub URL (`stub://type/value`) when no local_path present
- Resumability check uses ProvenanceManager.load() to skip existing successes
- try/finally ensures provenance written even on crash (best-effort on write failure)
- Pipeline version tracked in provenance ("0.1.0")
- Elapsed time includes discovery + all extraction attempts

**SourceDiscoverer stub (MVP):**
- Local file discovery: infers format from extension (.pdf → pdf, .xml → jats_xml, etc.)
- Stub API discovery: creates mock sources for DOI/arXiv identifiers (for testing)
- Cache integration: checks cache first, writes on successful discovery
- Quality tiers: PDF=4, others=1 (simplified for MVP)
- Full API integration (OpenAlex, arXiv, PMC) deferred to post-MVP

# AGENTS.md

## Implementation Status (2026-02-09)

**Phase 1 Foundation Progress: 13/17 specs complete**

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
- ✅ Spec 012: ResultWriter - output.md, summary.json, provenance delegation
- ✅ Spec 013: DiscoveryCache - TTL-based caching, freshness checks, per-identifier invalidation, bulk clearing
- ✅ Spec 017: ConversionError - typed exception with FailureCategory, structured details

Next: CLI (spec 011)

## Build & Run

```bash
# Install dependencies
uv sync

# Run extraction (single source)
uv run python -m src.doc_ingest.cli extract <source> --output out/

# Run extraction (batch)
uv run python -m src.doc_ingest.cli extract-batch sources.txt --output out/

# Directory creation is automatic; CLI exits 0 (success), 1 (failures), 2 (invalid input)
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

**Provenance tracking:**
- `ProvenanceManager` is pure persistence (no staleness logic)
- `DiscoveryCache` handles freshness/staleness checks (injectable, separate class)
- Triage metadata stored alongside discovery_timestamp for staleness detection
- Hash computation in ProvenanceManager reused by ResultWriter via `provenance_manager._compute_hash()`

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

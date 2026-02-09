# Design Document: Resilient Document Ingestion System

## 1. Overview

The Resilient Document Ingestion System transforms document extraction from a PDF-only, fail-opaquely process into an intelligent routing system that discovers structured alternatives (HTML, XML), attempts them in quality order with automatic fallback, and produces detailed provenance records for every document. The system makes batch corpus ingestion reliable and debuggable by capturing the complete decision trail (what was discovered, what was tried, what worked, what failed and why) and generating actionable triage reports that group failures by category.

**Primary use cases:**

- **Batch academic corpus ingestion** — Process 50+ papers from Zotero, automatically discovering arXiv HTML/JATS XML where available, falling back to PDF when necessary, with a post-run report showing which documents need manual intervention
- **Quality-aware extraction** — Prefer structured sources (arXiv HTML, PMC JATS) over PDF when available, avoiding table corruption and heading detection failures inherent to visual-rendering formats
- **Incremental re-processing** — Rerun ingestion when new documents are added or new extraction methods become available, automatically retrying previous failures without re-extracting successes
- **Debugging extraction failures** — For any document, inspect its provenance record to understand which sources were discovered, which were attempted, why the final output has its quality level, and what category of problem occurred
- **Extension with new converters** — Add OCR, new publisher XML formats, or other extraction methods without modifying orchestration code

## 2. Data Model

### Core Entities

```typescript
// Unique identifier for a document (at least one must be present)
interface DocumentIdentifiers {
  doi?: string;              // DOI (e.g., "10.1103/PhysRevLett.116.061102")
  arxiv_id?: string;         // arXiv ID (e.g., "1602.03837")
  pmc_id?: string;           // PubMed Central ID (e.g., "PMC4847581")
  local_path?: string;       // Absolute path to local file
  zotero_key?: string;       // Zotero item key (for user reference, not used in routing)
}

// A candidate source for extraction
interface SourceCandidate {
  format: SourceFormat;      // "jats_xml" | "arxiv_html" | "publisher_html" | "pdf" | "docx"
  url?: string;              // Remote URL (null for local files)
  local_path?: string;       // Local file path (null for remote sources)
  quality_tier: number;      // Lower = better quality (1=JATS, 2=arXiv HTML, 3=publisher HTML, 4=PDF, 5=DOCX)
  discovered_via: string;    // "openalex_api" | "arxiv_api" | "local_file" | "zotero_attachment"
  metadata?: {               // Optional source-specific metadata
    content_type?: string;
    publisher?: string;
    license?: string;
  };
}

// Result of attempting extraction from a source
interface ExtractionAttempt {
  source: SourceCandidate;
  started_at: string;        // ISO 8601 timestamp
  elapsed_seconds: number;
  outcome: "success" | "validation_failed" | "conversion_failed" | "fetch_failed" | "timeout";
  converter_used?: string;   // "jats_pandoc" | "arxiv_html_parser" | "pymupdf4llm" | etc.
  failure_category?: FailureCategory;
  error_message?: string;    // Raw error message for debugging
  warnings: string[];        // Non-fatal issues (e.g., "table possibly malformed")
  validation_details?: {     // Present if outcome="validation_failed"
    content_length?: number;
    has_body_content?: boolean;
    detected_content_type?: string;
    is_paywall?: boolean;
    is_truncated?: boolean;
  };
}

// Final document extraction outcome
type DocumentOutcome = "success" | "partial" | "failed";

// Typed failure categories for actionable triage
type FailureCategory = 
  | "needs_ocr"              // Scanned PDF, no extractable text
  | "table_corruption"       // Tables present but garbled in extraction
  | "no_source_found"        // No PDF/structured alternative discovered
  | "source_validation_failed" // All fetched sources were truncated/empty/paywalled
  | "conversion_timeout"     // Extraction exceeded time limit
  | "unsupported_format"     // File format not supported by any converter
  | "api_error"              // Source discovery API failed
  | "network_error"          // Network unreachable during fetch
  | "unknown";               // Unexpected failure

// Complete provenance record for one document
interface ProvenanceRecord {
  document_id: DocumentIdentifiers;
  
  // Discovery phase
  discovered_sources: SourceCandidate[];
  discovery_errors: string[];  // API failures, timeout, etc.
  discovery_cached: boolean;   // Was discovery result from cache?
  
  // Extraction phase
  attempts: ExtractionAttempt[];
  
  // Final outcome
  outcome: DocumentOutcome;
  final_converter?: string;    // Converter that produced the output (if success/partial)
  failure_category?: FailureCategory;
  
  // Metadata
  created_at: string;          // ISO 8601 timestamp
  pipeline_version: string;    // agentic-mbse version
  total_elapsed_seconds: number;
}

// Triage report structure (generated, not persisted)
interface TriageReport {
  generated_at: string;
  total_documents: number;
  
  outcomes: {
    success: number;
    partial: number;
    failed: number;
  };
  
  // Grouped by failure category
  failures_by_category: {
    [category in FailureCategory]: {
      count: number;
      documents: Array<{
        identifiers: DocumentIdentifiers;
        attempts: number;
        error_summary: string;
      }>;
    };
  };
  
  partials: Array<{
    identifiers: DocumentIdentifiers;
    warnings: string[];
  }>;
}

// Discovery cache entry (stored locally, keyed by identifier)
interface DiscoveryCacheEntry {
  identifier_key: string;      // "doi:10.1103/..." or "arxiv:1602.03837"
  discovered_sources: SourceCandidate[];
  cached_at: string;           // ISO 8601 timestamp
  ttl_days: number;            // Default: 30
}
```

### Storage Decisions

**Provenance records:**
- **Format:** JSON (one file per document)
- **Location:** `output_dir/{document_hash}/provenance.json` (alongside existing `summary.json` and `output.md`)
- **Rationale:** Separate file keeps extraction output schema unchanged; easy to regenerate triage reports

**Discovery cache:**
- **Format:** JSON (one file per cache entry, or single JSON lines file)
- **Location:** `~/.cache/agentic-mbse/source_discovery/{identifier_hash}.json` or `~/.cache/agentic-mbse/source_discovery.jsonl`
- **TTL:** 30 days (configurable)
- **Rationale:** Avoid re-querying APIs for the same DOI/arXiv ID across runs; hash-based naming prevents collisions

**Triage report:**
- **Format:** Markdown
- **Location:** `output_dir/TRIAGE_REPORT.md` (in fusion-tea: `ingest/TRIAGE_REPORT.md`)
- **Regeneration:** Can be regenerated from provenance records via `agentic-mbse triage-report output_dir/`
- **Rationale:** Human-readable, greppable, diffable; generated artifact doesn't need structured storage

**Existing formats (unchanged):**
- `summary.json` — Existing extraction metadata (hash, source path, layers applied, quality flags)
- `output.md` — Markdown extraction output
- `MANIFEST.jsonl` (fusion-tea) — List of extracted documents

## 3. Architecture

### Component Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Entry Point                          │
│  agentic-mbse extract <identifiers/path> [--format=auto]    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Source Router                              │
│  Orchestrates discovery → selection → extraction            │
│  - Calls SourceDiscoverer                                   │
│  - Iterates SourceCandidates in quality tier order          │
│  - Validates fetched content via ContentValidator           │
│  - Dispatches to ConverterRegistry                          │
│  - Records attempts in ProvenanceRecord                     │
│  - Returns (output_md, provenance)                          │
└───┬───────────────────────────────────────────┬─────────────┘
    │                                           │
    │                                           │
    ▼                                           ▼
┌─────────────────────────┐       ┌────────────────────────────┐
│   Source Discoverer     │       │   Converter Registry       │
│  - OpenAlexClient       │       │  - JATSPandocConverter     │
│  - ArXivAPIClient       │       │  - ArXivHTMLConverter      │
│  - PMCAPIClient (future)│       │  - PublisherHTMLConverter  │
│  - LocalFileDiscoverer  │       │  - PyMuPDF4LLMConverter    │
│  - DiscoveryCache       │       │  - DoclingConverter        │
│                         │       │  - DOCXPandocConverter     │
└─────────────────────────┘       └────────────────────────────┘
                                                 │
                                                 │
                                                 ▼
                                  ┌────────────────────────────┐
                                  │   Content Validator        │
                                  │  - Check content length    │
                                  │  - Detect paywalls         │
                                  │  - Detect truncation       │
                                  │  - Verify content type     │
                                  └────────────────────────────┘
                                                 
┌─────────────────────────────────────────────────────────────┐
│              Provenance Manager                             │
│  - Writes provenance.json per document                      │
│  - Loads provenance records for triage report generation    │
│  - Provides query interface for resumability                │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Triage Report Generator                        │
│  - Aggregates provenance records                            │
│  - Groups by outcome and failure category                   │
│  - Renders Markdown report                                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Single-document extraction:**

1. **Input:** User provides `DocumentIdentifiers` (DOI, arXiv ID, or local path) + optional `--format` override
2. **Discovery:** `SourceRouter` calls `SourceDiscoverer`, which queries bibliographic APIs (with caching) to resolve identifiers to `SourceCandidate[]`
3. **Selection:** `SourceRouter` sorts candidates by `quality_tier` (ascending)
4. **Extraction loop:** For each candidate:
   - Fetch content (from URL or local file)
   - Validate via `ContentValidator` (length, content type, body presence)
   - If validation fails: record `ExtractionAttempt(outcome="validation_failed")`, continue to next candidate
   - If validation passes: dispatch to `ConverterRegistry.convert(source, content)`
   - If conversion succeeds: record `ExtractionAttempt(outcome="success")`, break loop
   - If conversion fails: record `ExtractionAttempt(outcome="conversion_failed")`, continue to next candidate
5. **Outcome determination:**
   - If any attempt succeeded: `outcome="success"`, return converted markdown
   - If no attempt succeeded but some produced partial output: `outcome="partial"`, return best partial result
   - If all attempts failed: `outcome="failed"`, assign `FailureCategory` based on attempt details
6. **Output:** Write `provenance.json` + `output.md` (if success/partial) + `summary.json`

**Batch extraction:**

1. For each document in batch, run single-document flow
2. After batch completes, `TriageReportGenerator.generate(output_dir)` aggregates all `provenance.json` files
3. Write `TRIAGE_REPORT.md`

**Enhanced resumability:**

1. Before extraction, check if `output_dir/{document_hash}/provenance.json` exists
2. If exists and `outcome="success"`: skip (existing behavior via content hash)
3. If exists and `outcome in ["failed", "partial"]`: retry extraction (new behavior)
4. If not exists: run extraction normally

### Key Interfaces

**SourceDiscoverer API:**
```python
class SourceDiscoverer:
    def discover(self, identifiers: DocumentIdentifiers) -> list[SourceCandidate]:
        """Resolve identifiers to ranked source candidates. Uses cache if available."""
```

**ContentValidator API:**
```python
class ContentValidator:
    def validate(self, content: bytes, expected_format: SourceFormat) -> ValidationResult:
        """Check if fetched content is usable (not truncated, not paywall, has body)."""

class ValidationResult:
    is_valid: bool
    details: dict  # content_length, has_body, detected_content_type, etc.
```

**Converter API (existing, extended):**
```python
class Converter(ABC):
    @abstractmethod
    def can_convert(self, source: SourceCandidate) -> bool:
        """Return True if this converter supports the source format."""
    
    @abstractmethod
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        """Convert content to markdown. May raise ConversionError."""

class ConversionResult:
    markdown: str
    warnings: list[str]  # Non-fatal issues
    quality_flags: dict  # e.g., {"has_tables": True, "tables_likely_corrupted": False}
```

**ConverterRegistry API:**
```python
class ConverterRegistry:
    def register(self, converter: Converter) -> None:
        """Register a new converter."""
    
    def convert(self, source: SourceCandidate, content: bytes) -> ConversionResult:
        """Dispatch to appropriate converter based on source.format."""
```

**ProvenanceManager API:**
```python
class ProvenanceManager:
    def write(self, output_dir: Path, record: ProvenanceRecord) -> None:
        """Write provenance.json for a document."""
    
    def load(self, output_dir: Path, document_hash: str) -> ProvenanceRecord | None:
        """Load existing provenance record."""
    
    def should_retry(self, record: ProvenanceRecord) -> bool:
        """Return True if outcome warrants retry (failed/partial)."""
```

**TriageReportGenerator API:**
```python
class TriageReportGenerator:
    def generate(self, output_dir: Path) -> TriageReport:
        """Aggregate all provenance.json files into a triage report."""
    
    def render_markdown(self, report: TriageReport) -> str:
        """Render triage report as Markdown."""
```

## 4. Core Algorithms

### Source Quality Ranking

**Algorithm:** Assign each `SourceFormat` a `quality_tier` based on empirical extraction quality for academic papers:

```python
QUALITY_TIERS = {
    "jats_xml": 1,         # Structured XML, semantic tags, tables preserved
    "arxiv_html": 2,       # HTML5 with MathML, clean structure
    "publisher_html": 3,   # Varies by publisher, often good tables
    "pdf": 4,              # Visual rendering, table/heading detection fragile
    "docx": 5,             # Legacy, rare in academic corpus
}
```

**Rationale:** Structured formats (JATS, HTML) preserve semantic structure and tables better than PDF extraction. arXiv HTML is higher quality than generic publisher HTML due to LaTeX→HTML5 conversion.

**Edge cases:**
- If multiple sources have the same tier (e.g., multiple publisher HTML URLs), attempt in discovery order
- User can override with `--format=pdf` to force PDF extraction (bypasses discovery)

### Content Validation

**Algorithm:** Before attempting conversion, validate fetched content to avoid wasting time on corrupted/paywalled sources:

```python
def validate(content: bytes, expected_format: SourceFormat) -> ValidationResult:
    # 1. Length check: content must be > 1KB (avoid truncated responses)
    if len(content) < 1024:
        return ValidationResult(is_valid=False, details={"content_length": len(content), "is_truncated": True})
    
    # 2. Content-type check (if HTTP response headers available)
    if detected_content_type and not matches(detected_content_type, expected_format):
        return ValidationResult(is_valid=False, details={"detected_content_type": detected_content_type})
    
    # 3. Paywall detection: check for common paywall markers
    if expected_format in ["jats_xml", "publisher_html"]:
        body_text = content.decode("utf-8", errors="ignore").lower()
        paywall_markers = ["login required", "access denied", "subscribe to read", "institutional access"]
        if any(marker in body_text for marker in paywall_markers):
            return ValidationResult(is_valid=False, details={"is_paywall": True})
    
    # 4. Body content check: HTML/XML must have non-trivial body
    if expected_format in ["jats_xml", "arxiv_html", "publisher_html"]:
        if not has_body_content(content):
            return ValidationResult(is_valid=False, details={"has_body_content": False})
    
    return ValidationResult(is_valid=True, details={"content_length": len(content)})
```

**Edge cases:**
- False positives (legitimate content flagged as paywall): Validation is conservative — if content passes, conversion proceeds; if it fails, we fall through to next source. Worst case is trying one extra source.
- False negatives (paywall page passes validation): Conversion will fail with garbled output, recorded as `outcome="conversion_failed"`, next source attempted.

### Failure Category Assignment

**Algorithm:** Classify extraction failure into actionable category based on attempt details:

```python
def assign_failure_category(attempts: list[ExtractionAttempt]) -> FailureCategory:
    # Check most recent attempt first for specific failures
    last_attempt = attempts[-1]
    
    if last_attempt.outcome == "timeout":
        return "conversion_timeout"
    
    # If all attempts were validation failures, check validation details
    if all(a.outcome == "validation_failed" for a in attempts):
        if any(a.validation_details.get("is_paywall") for a in attempts):
            return "source_validation_failed"
        if any(a.validation_details.get("is_truncated") for a in attempts):
            return "source_validation_failed"
    
    # If PDF extraction failed due to no text, classify as needs_ocr
    pdf_attempts = [a for a in attempts if a.source.format == "pdf"]
    if pdf_attempts:
        last_pdf = pdf_attempts[-1]
        if "no extractable text" in (last_pdf.error_message or "").lower():
            return "needs_ocr"
        if "table" in (last_pdf.error_message or "").lower():
            return "table_corruption"
    
    # If no sources were discovered
    if len(attempts) == 0:
        return "no_source_found"
    
    # If all sources had unsupported formats
    if all("unsupported format" in (a.error_message or "").lower() for a in attempts):
        return "unsupported_format"
    
    # If discovery phase had API errors
    if any("api" in (a.error_message or "").lower() for a in attempts):
        return "api_error"
    
    return "unknown"
```

**Edge cases:**
- Multiple failure modes (e.g., API error + PDF has no text): Categorize by most actionable failure (API error is higher priority than needs_ocr, because fixing API might reveal structured alternatives)
- New converter introduces new failure mode: Extend `FailureCategory` enum and add classification logic

### Discovery Caching

**Algorithm:** Cache source discovery results to avoid redundant API calls:

```python
def discover_with_cache(identifiers: DocumentIdentifiers, cache_ttl_days: int = 30) -> list[SourceCandidate]:
    # Generate cache key from identifier (e.g., "doi:10.1103/PhysRevLett.116.061102")
    cache_key = generate_cache_key(identifiers)
    cache_path = Path.home() / ".cache" / "agentic-mbse" / "source_discovery" / f"{hash(cache_key)}.json"
    
    # Check cache
    if cache_path.exists():
        entry = DiscoveryCacheEntry.parse_file(cache_path)
        if is_fresh(entry.cached_at, cache_ttl_days):
            return entry.discovered_sources
    
    # Cache miss or stale: query APIs
    sources = query_apis(identifiers)  # OpenAlex, arXiv, etc.
    
    # Write cache
    entry = DiscoveryCacheEntry(
        identifier_key=cache_key,
        discovered_sources=sources,
        cached_at=datetime.utcnow().isoformat(),
        ttl_days=cache_ttl_days
    )
    cache_path.write_text(entry.json())
    
    return sources
```

**Performance considerations:**
- Cache hit: O(1) disk read, ~1ms
- Cache miss: O(1) API call per source type (OpenAlex, arXiv), ~200-500ms total
- Cache invalidation: Manual (`agentic-mbse clear-cache`) or TTL-based

**Edge cases:**
- Document has multiple identifiers (DOI + arXiv ID): Use DOI as primary cache key; if DOI cache misses, fall back to arXiv ID lookup
- API returns different results over time (e.g., publisher adds JATS URL): Stale cache will be refreshed after TTL expires

## 5. External Interfaces

### CLI Commands

**Existing (modified):**
```bash
# Extract single document (now uses source router)
agentic-mbse extract <doi|arxiv_id|file_path> [--format=auto|pdf|jats|arxiv_html] [--output-dir=OUTPUT_DIR]

# Extract batch (unchanged interface, new routing behavior)
agentic-mbse extract-batch <input.jsonl> --output-dir OUTPUT_DIR
```

**New:**
```bash
# Generate triage report from existing provenance records
agentic-mbse triage-report OUTPUT_DIR [--output=TRIAGE_REPORT.md]

# Clear source discovery cache
agentic-mbse clear-cache [--max-age-days=30]

# Retry failed/partial documents in a batch output directory
agentic-mbse retry-failed OUTPUT_DIR
```

### API (Python Library)

**For integration into fusion-tea or other projects:**

```python
from agentic_mbse.source_router import SourceRouter
from agentic_mbse.triage import TriageReportGenerator

# Single-document extraction
router = SourceRouter()
result = router.extract(
    identifiers={"doi": "10.1103/PhysRevLett.116.061102"},
    output_dir=Path("output/"),
    format_override=None  # or "pdf" to force PDF
)
# result.markdown, result.provenance, result.outcome

# Batch extraction
results = router.extract_batch(
    documents=[{"doi": "..."}, {"arxiv_id": "..."}, ...],
    output_dir=Path("output/")
)

# Generate triage report
report_gen = TriageReportGenerator()
report = report_gen.generate(output_dir=Path("output/"))
Path("output/TRIAGE_REPORT.md").write_text(report_gen.render_markdown(report))
```

### Input Formats

**Document identifiers (JSONL for batch):**
```jsonl
{"doi": "10.1103/PhysRevLett.116.061102"}
{"arxiv_id": "1602.03837"}
{"doi": "10.1088/1361-6382/aa51f4", "arxiv_id": "1606.04856"}
{"local_path": "/path/to/paper.pdf"}
{"local_path": "/path/to/article.xml", "format_hint": "jats_xml"}
```

**Configuration (optional `.agentic-mbse.yaml` in project root or user home):**
```yaml
source_discovery:
  openalex_api_key: "your_email@example.com"  # Required for OpenAlex
  cache_ttl_days: 30
  timeout_seconds: 60
  
extraction:
  default_format: "auto"  # or "pdf", "jats", etc.
  max_attempts_per_document: 5
  conversion_timeout_seconds: 300
  
triage:
  include_success_summary: true
  group_partials_separately: true
```

### Output Formats

**Provenance record (`provenance.json`):**
```json
{
  "document_id": {"doi": "10.1103/PhysRevLett.116.061102"},
  "discovered_sources": [
    {
      "format": "jats_xml",
      "url": "https://journals.aps.org/prl/accepted/...",
      "quality_tier": 1,
      "discovered_via": "openalex_api"
    },
    {
      "format": "pdf",
      "url": "https://arxiv.org/pdf/1602.03837.pdf",
      "quality_tier": 4,
      "discovered_via": "arxiv_api"
    }
  ],
  "discovery_errors": [],
  "discovery_cached": false,
  "attempts": [
    {
      "source": {"format": "jats_xml", "url": "..."},
      "started_at": "2026-02-09T12:34:56Z",
      "elapsed_seconds": 2.3,
      "outcome": "success",
      "converter_used": "jats_pandoc",
      "warnings": ["Table 2 missing column headers"]
    }
  ],
  "outcome": "success",
  "final_converter": "jats_pandoc",
  "created_at": "2026-02-09T12:34:58Z",
  "pipeline_version": "0.4.0",
  "total_elapsed_seconds": 3.1
}
```

**Triage report (`TRIAGE_REPORT.md`):**
```markdown
# Document Extraction Triage Report

**Generated:** 2026-02-09 14:30:00 UTC
**Total documents:** 52

## Summary

- ✅ Success: 38 (73%)
- ⚠️  Partial: 8 (15%)
- ❌ Failed: 6 (12%)

---

## Failed Documents

### needs_ocr (3 documents)

These documents are scanned PDFs with no extractable text. OCR processing required.

- `doi:10.1234/scanned.paper` — 2 attempts, last error: "no extractable text found"
- `local_path:/papers/old_scan.pdf` — 1 attempt, last error: "empty text extraction"
- ...

### table_corruption (2 documents)

Tables were detected but extraction produced garbled output.

- `doi:10.5678/complex.tables` — 3 attempts (pdf, publisher_html), tables corrupted in both
- ...

### source_validation_failed (1 document)

All discovered sources failed validation (truncated, paywall, or empty).

- `doi:10.9999/paywalled` — 2 attempts, both returned paywall login page

---

## Partial Successes

These documents extracted successfully but have warnings.

- `doi:10.1111/partial.output` — Warnings: "Figure 3 caption missing", "Table 2 footnote truncated"
- ...

---

## Recommendations

1. **needs_ocr**: Run OCR preprocessing (e.g., Tesseract) on 3 scanned PDFs
2. **table_corruption**: Consider manual table extraction for 2 high-priority documents
3. **source_validation_failed**: Check institutional access or contact publisher for 1 document
```

## 6. Constraints & Invariants

### Must-Never-Violate Rules

1. **Provenance completeness** — Every extraction attempt (success or failure) MUST be recorded in `provenance.json`. No silent failures.
2. **Idempotency** — Running extraction on the same document with the same identifiers MUST produce the same `provenance.json` (modulo timestamps) if sources/APIs haven't changed.
3. **Non-destructive retries** — Retrying a failed document MUST NOT delete or overwrite the previous `provenance.json`; instead, append new attempts or replace with cumulative record.
4. **Discovery cache correctness** — If a cache entry exists and is fresh, it MUST be used; API calls for cached identifiers are forbidden (prevents rate limit exhaustion).
5. **Source ordering determinism** — Given the same discovered sources, extraction MUST attempt them in the same order (quality tier, then discovery order). Non-determinism breaks debugging.
6. **No partial provenance** — If extraction crashes mid-attempt, the `provenance.json` MUST still be written with all completed attempts; incomplete records are forbidden.

### Security Considerations

1. **API key exposure** — OpenAlex API key (email) stored in config file or environment variable, never in provenance records or logs
2. **URL validation** — Fetched URLs must be validated (protocol allowlist: `https`, `http`; no `file://`, `ftp://`, etc.) to prevent SSRF
3. **Content sanitization** — Fetched HTML/XML must be sanitized before passing to converters to prevent XXE or script injection
4. **Disk space exhaustion** — Large PDF/XML downloads must be size-limited (e.g., 50MB max) to prevent DoS via disk fill
5. **Command injection** — Pandoc/CLI converters must sanitize file paths and use subprocess argument arrays (not shell strings)

### Determinism Requirements

**Required for reproducibility and debugging:**

1. **Source discovery** — OpenAlex/arXiv APIs return results in arbitrary order; MUST be sorted by quality tier + URL (lexicographic) before storage
2. **Timestamp precision** — ISO 8601 timestamps with UTC timezone, microsecond precision for elapsed time calculations
3. **Error messages** — Converter errors must be deterministic (avoid stack trace address pointers, random UUIDs in error IDs)
4. **Triage report ordering** — Failed documents within a category MUST be sorted by identifier (DOI if present, else arXiv ID, else local path) for diffability

**Allowed non-determinism:**

- Timestamps (`created_at`, `started_at`) — vary by run time
- API response times (`elapsed_seconds`) — vary by network latency
- Discovery cache hits — vary by cache state, but outcome (discovered sources) must be deterministic

## 7. Phasing

### Phase 1: Foundation (Work Items 1–2)

**Scope:**
- Provenance schema and recording (`ProvenanceManager`, `ExtractionAttempt` data model)
- Enhanced resumability (retry failed/partial outcomes)
- Source discovery (`SourceDiscoverer`, OpenAlex API integration, discovery cache)
- Basic routing (`SourceRouter` with validation and fallthrough, no new converters yet)
- Use existing PDF converter as fallback

**Deliverables:**
- `agentic-mbse extract <doi>` produces `provenance.json`
- `agentic-mbse retry-failed` skips successes, retries failures
- Discovery cache speeds up re-runs
- Unit tests for discovery, caching, routing logic

**Why first:** Everything else depends on provenance recording and routing infrastructure. Can be tested with existing PDF pipeline.

### Phase 2: New Converters (Work Item 3)

**Scope:**
- JATS XML converter (pandoc-based)
- arXiv HTML converter (custom HTML parser)
- Publisher HTML converter (BeautifulSoup-based, generic)
- Local structured file support (`--format-hint` for XML/HTML input)

**Deliverables:**
- `agentic-mbse extract <doi>` automatically prefers JATS/arXiv HTML over PDF
- `agentic-mbse extract article.xml --format-hint=jats_xml` works
- Converter registry supports dynamic registration
- Unit tests for each converter

**Why second:** Converters are independent of each other; can be developed in parallel. Require Phase 1 routing to be functional.

### Phase 3: Triage & Failure Categorization (Work Item 4)

**Scope:**
- Failure category assignment (`assign_failure_category()` algorithm)
- Triage report generation (`TriageReportGenerator`)
- `agentic-mbse triage-report` CLI command

**Deliverables:**
- `TRIAGE_REPORT.md` generated after batch extraction
- Failures grouped by actionable category
- Partial successes listed with warnings
- Report regenerable from existing provenance records

**Why third:** Requires provenance records (Phase 1) to exist; orthogonal to converters (Phase 2).

### Phase 4: Integration (Work Item 5)

**Scope:**
- Update `fusion-tea/zotero_ingest.py` to use `SourceRouter`
- Extend `MANIFEST.jsonl` with outcome/failure category summary
- Auto-generate triage report after batch runs

**Deliverables:**
- `python ingest/zotero_ingest.py` uses source routing
- `ingest/TRIAGE_REPORT.md` generated automatically
- End-to-end test with 10-document Zotero batch

**Why last:** Integration requires all library components (Phases 1–3) to be complete and tested.

### Deferred to Future Phases

- **OCR implementation** — Failure categorization identifies "needs_ocr" documents; OCR converter is a separate project
- **PMC API integration** — JATS XML from PMC is a fourth source type, follows same discovery pattern
- **Parallel batch extraction** — ThreadPoolExecutor for concurrent document processing
- **Quality scoring** — Automated rubric (like audit headings/tables scoring) to grade extraction quality
- **Publisher-specific HTML parsers** — Optimized parsers for Elsevier, Springer, IEEE HTML structures
- **Interactive triage** — TUI for reviewing failed documents and launching manual intervention tools

---

## Design Rationale Summary

**Why source routing?** — Empirical data (v3 corpus audit) shows structured sources are consistently higher quality than PDF; automatically discovering and preferring them eliminates an entire class of failures.

**Why provenance records?** — Batch corpus ingestion without provenance is a black box; failures are invisible, debugging requires re-running extraction, and users can't prioritize remediation. Structured provenance makes every decision auditable.

**Why failure categories?** — Raw error messages ("HTTPError 403", "UnicodeDecodeError") are not actionable at scale. Categories ("needs_ocr", "source_validation_failed") tell users what class of fix is needed without reading logs.

**Why separate triage report?** — Aggregating 50+ provenance records manually is tedious; a generated report provides at-a-glance status. Markdown format is human-readable, diffable, and greppable by category.

**Why discovery caching?** — OpenAlex free tier is 100K requests/day; without caching, rerunning a 1000-document batch would exhaust the quota. 30-day TTL balances freshness vs. redundancy.

**Why quality tiers?** — Attempting sources in arbitrary order wastes time (PDF before JATS means table corruption even when JATS is available). Quality tiers encode empirical extraction success rates.

**Why content validation before conversion?** — Fetching a paywalled HTML page costs network time; attempting conversion costs CPU time and produces garbage output. Early validation fails fast and moves to next source.

**Why JSON provenance + Markdown triage?** — Provenance is structured data (easy to query, aggregate, version); triage is a human communication artifact (easy to read, share, diff).

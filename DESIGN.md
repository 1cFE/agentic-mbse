

# Design Document: Resilient Document Ingestion System (V2)

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
  
  // Identifier priority for cache keying and display: doi > arxiv_id > pmc_id > local_path
  // primary_identifier() returns (type, value) tuple for the highest-priority present identifier
}

// A candidate source for extraction
interface SourceCandidate {
  format: SourceFormat;      // "jats_xml" | "arxiv_html" | "publisher_html" | "pdf" | "docx"
  url?: string;              // Remote URL (null for local files)
  local_path?: string;       // Local file path (null for remote sources)
  quality_tier: number;      // Lower = better quality (1=JATS, 2=arXiv HTML, 3=publisher HTML, 4=PDF, 5=DOCX)
  discovered_via: string;    // "openalex_api" | "arxiv_api" | "local_file" | "zotero_attachment"
  http_content_type?: string;   // HTTP Content-Type from discovery response, if available
  publisher?: string;           // Publisher name from discovery metadata, if available
  license?: string;             // License info from discovery metadata, if available
}

// Typed quality flags reported by converters
interface QualityFlags {
  has_tables: boolean;
  tables_likely_corrupted: boolean;
  has_math: boolean;
  math_preserved: boolean;
  has_figures: boolean;
  figure_captions_present: boolean;
  heading_structure_detected: boolean;
}

// Result of a successful conversion
interface ConversionResult {
  markdown: string;
  warnings: string[];          // Non-fatal issues (e.g., "table possibly malformed")
  quality_flags: QualityFlags;
  converter_name: string;      // e.g., "JATSPandocConverter", populated by converter
}

// Typed conversion error raised by converters
interface ConversionError {
  message: string;
  category: FailureCategory;   // Typed category, not inferred from message text
  details: object;             // Converter-specific structured details
}

// Validation result returned by converter's validate_source method
interface ValidationResult {
  is_valid: boolean;
  content_length: number;
  has_body_content?: boolean;
  detected_content_type?: string;
  is_paywall?: boolean;
  is_truncated?: boolean;
}

// Result of attempting extraction from a source
interface ExtractionAttempt {
  source: SourceCandidate;
  started_at: string;        // ISO 8601 timestamp
  elapsed_seconds: number;
  outcome: "success" | "validation_failed" | "conversion_failed" | "fetch_failed" | "timeout";
  converter_used?: string;   // Populated from ConversionResult.converter_name on success
  failure_category?: FailureCategory;  // Populated from ConversionError.category on failure
  error_message?: string;    // Raw error message for debugging
  warnings: string[];        // Non-fatal issues (e.g., "table possibly malformed")
  validation_details?: ValidationResult;  // Present when outcome="validation_failed"
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
  provenance_latest_timestamp: string;  // Latest created_at among included records, for staleness detection
  
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

// Discovery cache entry (stored locally, keyed by primary identifier)
interface DiscoveryCacheEntry {
  identifier_key: string;      // "doi:10.1103/..." or "arxiv:1602.03837"
  discovered_sources: SourceCandidate[];
  cached_at: string;           // ISO 8601 timestamp
  // TTL is a global config, not stored per entry; freshness = now - cached_at < config.cache_ttl_days
}
```

### Multi-Identifier Resolution

When a document has multiple identifiers (e.g., both DOI and arXiv ID):

1. **Primary identifier** is determined by priority order: `doi > arxiv_id > pmc_id > local_path`
2. **Cache keying** uses the primary identifier only
3. **Source discovery** queries APIs for each identifier, unions all discovered sources, deduplicates by URL, and sorts by quality tier
4. **Display** in triage reports uses the primary identifier for brevity

```python
class DocumentIdentifiers:
    doi: str | None
    arxiv_id: str | None
    pmc_id: str | None
    local_path: str | None
    zotero_key: str | None
    
    def primary_identifier(self) -> tuple[str, str]:
        """Return (type, value) for the highest-priority present identifier."""
        if self.doi:
            return ("doi", self.doi)
        if self.arxiv_id:
            return ("arxiv", self.arxiv_id)
        if self.pmc_id:
            return ("pmc", self.pmc_id)
        if self.local_path:
            return ("local", self.local_path)
        raise ValueError("At least one identifier required")
    
    def display_key(self) -> str:
        """Human-readable key for reports: 'doi:10.1103/...' or 'arxiv:1602.03837'."""
        id_type, id_value = self.primary_identifier()
        return f"{id_type}:{id_value}"
```

### Storage Decisions

**Provenance records:**
- **Format:** JSON (one file per document)
- **Location:** `output_dir/{document_hash}/provenance.json` (alongside existing `summary.json` and `output.md`)
- **Rationale:** Separate file keeps extraction output schema unchanged; easy to regenerate triage reports

**Discovery cache:**
- **Format:** JSON (one file per cache entry)
- **Location:** `~/.cache/agentic-mbse/source_discovery/{identifier_hash}.json`
- **TTL:** 30 days (configurable via `source_discovery.cache_ttl_days` in config)
- **Rationale:** Avoid re-querying APIs for the same DOI/arXiv ID across runs; hash-based naming prevents collisions

**Triage report:**
- **Format:** Markdown
- **Location:** `output_dir/TRIAGE_REPORT.md` (in fusion-tea: `ingest/TRIAGE_REPORT.md`)
- **Regeneration:** Can be regenerated from provenance records via `agentic-mbse triage-report output_dir/`; always overwrites existing report
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
│                  Source Router (Facade)                     │
│  Coordinates discovery, orchestration, and provenance       │
│  - Calls SourceDiscoverer for source candidates             │
│  - Delegates extraction loop to ExtractionOrchestrator      │
│  - Delegates outcome classification to OutcomeClassifier    │
│  - Writes provenance via ProvenanceManager                  │
│  - Returns (output_md, provenance)                          │
└───┬──────────────┬───────────────────────────┬──────────────┘
    │              │                           │
    ▼              ▼                           ▼
┌──────────────┐ ┌──────────────────┐ ┌────────────────────────┐
│   Source      │ │  Extraction      │ │ Outcome Classifier     │
│  Discoverer   │ │  Orchestrator    │ │ - Determines success/  │
│  - OpenAlex   │ │  - Loops sources │ │   partial/failed       │
│  - ArXiv API  │ │  - Validates via │ │ - Assigns failure      │
│  - PMC (fut.) │ │    converter     │ │   category from typed  │
│  - LocalFile  │ │  - Converts via  │ │   ExtractionAttempts   │
│              │ │    registry      │ └────────────────────────┘
└──────┬───────┘ │  - Records       │
       │         │    attempts      │
       ▼         └───────┬──────────┘
┌──────────────┐         │
│  Discovery   │         ▼
│  Cache       │ ┌────────────────────────────┐
│  - get/put   │ │   Converter Registry       │
│  - TTL check │ │  - JATSPandocConverter     │
│  - per-id    │ │  - ArXivHTMLConverter      │
│    invalidate│ │  - PublisherHTMLConverter   │
└──────────────┘ │  - PyMuPDF4LLMConverter    │
                 │  - DoclingConverter        │
                 │  - DOCXPandocConverter     │
                 └────────────────────────────┘
                    Each converter implements:
                    - can_convert()
                    - validate_source()
                    - convert()
                                                 
┌─────────────────────────────────────────────────────────────┐
│              Provenance Manager                             │
│  - Writes provenance.json per document                      │
│  - Loads provenance records for triage report generation    │
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

**Key architectural change from V1:** `SourceRouter` is now a thin facade that coordinates three single-purpose components: `SourceDiscoverer` (finds sources), `ExtractionOrchestrator` (runs the extraction loop), and `OutcomeClassifier` (determines final outcome and failure category). `ContentValidator` has been removed as a separate component; validation logic is co-located with each converter via `Converter.validate_source()`. `DiscoveryCache` is a separate class injected into `SourceDiscoverer` rather than embedded within it. `ProvenanceManager` is a pure persistence layer; resumability decisions (`should_retry`) belong to `SourceRouter`.

### Data Flow

**Single-document extraction:**

1. **Input:** User provides `DocumentIdentifiers` (DOI, arXiv ID, or local path) + optional `--format` override
2. **Resumability check:** `SourceRouter` loads existing `provenance.json` if present. If `outcome="success"`, skip. If `outcome in ["failed", "partial"]`, retry.
3. **Discovery:** `SourceRouter` calls `SourceDiscoverer`, which checks `DiscoveryCache` first, then queries bibliographic APIs for each identifier, unions results, deduplicates by URL, and sorts by quality tier
4. **Extraction loop:** `ExtractionOrchestrator` iterates candidates in quality tier order. For each candidate:
   - Fetch content (from URL or local file). On fetch failure: record `ExtractionAttempt(outcome="fetch_failed")`, continue
   - Validate via `converter.validate_source(content)` — format-specific checks co-located with the converter
   - If validation fails: record `ExtractionAttempt(outcome="validation_failed", validation_details=result)`, continue
   - If validation passes: call `converter.convert(content, metadata)`
   - If conversion succeeds: record `ExtractionAttempt(outcome="success", converter_used=result.converter_name)`, break
   - If conversion raises `ConversionError`: record `ExtractionAttempt(outcome="conversion_failed", failure_category=error.category)`, continue
   - If conversion raises unexpected exception: record `ExtractionAttempt(outcome="conversion_failed", failure_category="unknown")`, continue
5. **Outcome classification:** `OutcomeClassifier.classify(attempts)` determines `DocumentOutcome` and `FailureCategory` from the typed attempt records
6. **Output:** Write `provenance.json` via try/finally (ensuring partial provenance on crash) + `output.md` (if success/partial) + `summary.json`

**Batch extraction:**

1. For each document in batch, run single-document flow. Continue on per-document failure.
2. After batch completes, `TriageReportGenerator.generate(output_dir)` aggregates all `provenance.json` files
3. Write `TRIAGE_REPORT.md` (always overwrites if exists)

**Enhanced resumability:**

1. Before extraction, check if `output_dir/{document_hash}/provenance.json` exists
2. If exists and `outcome="success"`: skip (existing behavior via content hash)
3. If exists and `outcome in ["failed", "partial"]`: retry extraction (new behavior)
4. If not exists: run extraction normally

### Key Interfaces

**Converter API (unified validation + conversion):**
```python
class ConversionError(Exception):
    """Typed conversion error with structured failure category."""
    def __init__(
        self,
        message: str,
        category: FailureCategory,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.category = category
        self.details = details or {}

@dataclass
class QualityFlags:
    has_tables: bool = False
    tables_likely_corrupted: bool = False
    has_math: bool = False
    math_preserved: bool = False
    has_figures: bool = False
    figure_captions_present: bool = False
    heading_structure_detected: bool = False

@dataclass
class ConversionResult:
    markdown: str
    warnings: list[str]
    quality_flags: QualityFlags
    converter_name: str          # Populated by each converter (e.g., "JATSPandocConverter")

@dataclass
class ValidationResult:
    is_valid: bool
    content_length: int
    has_body_content: bool | None = None
    detected_content_type: str | None = None
    is_paywall: bool | None = None
    is_truncated: bool | None = None

class Converter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique converter name for provenance records."""

    @abstractmethod
    def can_convert(self, source: SourceCandidate) -> bool:
        """Return True if this converter supports the source format."""
    
    @abstractmethod
    def validate_source(self, content: bytes) -> ValidationResult:
        """Validate fetched content before conversion. Format-specific checks."""
    
    @abstractmethod
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        """
        Convert content to markdown.
        
        Raises:
            ConversionError: Typed exception with failure category and details.
        """
```

**ConverterRegistry API:**
```python
class ConverterRegistry:
    def register(self, converter: Converter) -> None:
        """Register a new converter."""
    
    def get_converter(self, source: SourceCandidate) -> Converter | None:
        """Return the converter that can handle this source, or None."""
```

**DiscoveryCache API:**
```python
class DiscoveryCache:
    def get(self, identifier_key: str) -> list[SourceCandidate] | None:
        """Return cached sources if fresh, None if missing or stale."""
    
    def put(self, identifier_key: str, sources: list[SourceCandidate]) -> None:
        """Cache discovered sources for this identifier."""
    
    def invalidate(self, identifier_key: str) -> bool:
        """Remove a specific identifier's cache entry. Returns True if entry existed."""
    
    def clear(self, max_age_days: int | None = None) -> int:
        """Clear all entries (or only those older than max_age_days). Returns count removed."""
```

**SourceDiscoverer API:**
```python
class SourceDiscoverer:
    def __init__(self, cache: DiscoveryCache, api_clients: list[DiscoveryAPIClient]):
        """Inject cache and API clients separately for testability."""
    
    def discover(self, identifiers: DocumentIdentifiers) -> tuple[list[SourceCandidate], list[str]]:
        """
        Resolve identifiers to ranked source candidates.
        Returns (candidates, discovery_errors).
        Uses cache if available; queries APIs on miss; updates cache on success.
        When multiple identifiers present, queries all and unions/deduplicates results.
        """
```

**ExtractionOrchestrator API:**
```python
class ExtractionOrchestrator:
    def __init__(self, registry: ConverterRegistry):
        """Inject converter registry."""
    
    def orchestrate(
        self,
        sources: list[SourceCandidate],
        fetch_fn: Callable[[SourceCandidate], bytes],
    ) -> tuple[list[ExtractionAttempt], ConversionResult | None]:
        """
        Iterate sources in order, validate, convert, record attempts.
        Returns (all_attempts, successful_result_or_None).
        """
```

**OutcomeClassifier API:**
```python
class OutcomeClassifier:
    def classify(
        self,
        attempts: list[ExtractionAttempt],
        discovery_errors: list[str],
    ) -> tuple[DocumentOutcome, FailureCategory | None]:
        """
        Determine final outcome and failure category from attempts.
        Uses typed failure_category from ExtractionAttempts (set by ConversionError.category),
        with fallback heuristics only for unexpected errors.
        """
```

**ProvenanceManager API:**
```python
class ProvenanceManager:
    def write(self, output_dir: Path, record: ProvenanceRecord) -> None:
        """Write provenance.json for a document."""
    
    def load(self, output_dir: Path, document_hash: str) -> ProvenanceRecord | None:
        """Load existing provenance record."""
```

**TriageReportGenerator API:**
```python
class TriageReportGenerator:
    def generate(self, output_dir: Path) -> TriageReport:
        """Aggregate all provenance.json files into a triage report."""
    
    def render_markdown(self, report: TriageReport) -> str:
        """Render triage report as Markdown. Includes provenance_latest_timestamp for staleness detection."""
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
- If multiple sources have the same tier (e.g., multiple publisher HTML URLs), attempt in discovery order (stable sort by URL for determinism)
- User can override with `--format=pdf` to force PDF extraction (bypasses discovery entirely; see CLI spec below)

### Source Validation (Co-located with Converters)

**Algorithm:** Each converter implements `validate_source()` with format-appropriate checks. This replaces the former standalone `ContentValidator`.

**Base validation (shared via mixin or base class):**

```python
class BaseConverter(Converter):
    def _base_validate(self, content: bytes) -> ValidationResult | None:
        """Common checks; returns ValidationResult if failed, None if passed."""
        if len(content) < 1024:
            return ValidationResult(is_valid=False, content_length=len(content), is_truncated=True)
        return None  # Passed base checks
```

**JATS XML converter validation:**
```python
class JATSPandocConverter(BaseConverter):
    def validate_source(self, content: bytes) -> ValidationResult:
        base = self._base_validate(content)
        if base:
            return base
        
        text = content.decode("utf-8", errors="ignore")
        
        # Check for XML body content
        if "<body" not in text and "<article" not in text:
            return ValidationResult(is_valid=False, content_length=len(content), has_body_content=False)
        
        return ValidationResult(is_valid=True, content_length=len(content), has_body_content=True)
```

**Publisher HTML converter validation:**
```python
class PublisherHTMLConverter(BaseConverter):
    PAYWALL_MARKERS = ["login required", "access denied", "subscribe to read", "institutional access"]
    
    def validate_source(self, content: bytes) -> ValidationResult:
        base = self._base_validate(content)
        if base:
            return base
        
        text = content.decode("utf-8", errors="ignore").lower()
        
        if any(marker in text for marker in self.PAYWALL_MARKERS):
            return ValidationResult(is_valid=False, content_length=len(content), is_paywall=True)
        
        if "<body" not in text:
            return ValidationResult(is_valid=False, content_length=len(content), has_body_content=False)
        
        return ValidationResult(is_valid=True, content_length=len(content))
```

**Rationale for co-location:** Format-specific validation knowledge belongs with the converter that handles that format. This eliminates the dispatch problem (how does a central validator know what checks to run for JATS vs. HTML?) and ensures adding a new converter automatically includes its validation logic — no separate component to update.

### Failure Category Assignment

**Algorithm:** Classify extraction failure into actionable category. Primary source: typed `failure_category` from `ConversionError` (set by converters). Fallback heuristics only for discovery-level failures and unexpected errors.

```python
class OutcomeClassifier:
    def classify(
        self,
        attempts: list[ExtractionAttempt],
        discovery_errors: list[str],
    ) -> tuple[DocumentOutcome, FailureCategory | None]:
        # Success: at least one attempt succeeded
        successful = [a for a in attempts if a.outcome == "success"]
        if successful:
            return ("success", None)
        
        # Partial: at least one attempt produced partial output (future: quality threshold)
        # For now, partial is determined by converter returning low-quality result with warnings
        
        # Failed: determine category
        if not attempts and not discovery_errors:
            return ("failed", "no_source_found")
        
        if not attempts and discovery_errors:
            return ("failed", "api_error")
        
        # Use typed categories from conversion errors (most recent first)
        for attempt in reversed(attempts):
            if attempt.failure_category and attempt.failure_category != "unknown":
                return ("failed", attempt.failure_category)
        
        # Fallback: check validation failures
        if all(a.outcome == "validation_failed" for a in attempts):
            if any(a.validation_details and a.validation_details.is_paywall for a in attempts):
                return ("failed", "source_validation_failed")
            if any(a.validation_details and a.validation_details.is_truncated for a in attempts):
                return ("failed", "source_validation_failed")
            return ("failed", "source_validation_failed")
        
        if all(a.outcome == "fetch_failed" for a in attempts):
            return ("failed", "network_error")
        
        if all(a.outcome == "timeout" for a in attempts):
            return ("failed", "conversion_timeout")
        
        return ("failed", "unknown")
```

**Key change from V1:** Category assignment no longer parses error message strings. Converters set `ConversionError.category` directly when raising errors (e.g., PDF converter raises `ConversionError("...", category="needs_ocr")` when it detects no extractable text). The classifier reads typed fields, with string-parsing fallback only as a last resort for truly unexpected errors.

### Discovery with Separate Cache

**Algorithm:** `SourceDiscoverer` coordinates separate `DiscoveryCache` and API clients, rather than embedding cache logic.

```python
class SourceDiscoverer:
    def __init__(self, cache: DiscoveryCache, api_clients: list[DiscoveryAPIClient]):
        self.cache = cache
        self.api_clients = api_clients
    
    def discover(self, identifiers: DocumentIdentifiers) -> tuple[list[SourceCandidate], list[str]]:
        cache_key = identifiers.display_key()
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            return (cached, [])
        
        # Cache miss: query all API clients for all identifiers
        all_sources: list[SourceCandidate] = []
        errors: list[str] = []
        
        for client in self.api_clients:
            try:
                sources = client.query(identifiers)
                all_sources.extend(sources)
            except DiscoveryError as e:
                errors.append(f"{client.name}: {e}")
        
        # Add local file as source if local_path present
        if identifiers.local_path:
            all_sources.append(SourceCandidate(
                format=detect_format(identifiers.local_path),
                local_path=identifiers.local_path,
                quality_tier=QUALITY_TIERS.get(detect_format(identifiers.local_path), 4),
                discovered_via="local_file",
            ))
        
        # Deduplicate by URL, sort by quality_tier then URL for determinism
        deduped = deduplicate_by_url(all_sources)
        sorted_sources = sorted(deduped, key=lambda s: (s.quality_tier, s.url or s.local_path or ""))
        
        # Update cache (even if some APIs errored, cache what we found)
        if sorted_sources:
            self.cache.put(cache_key, sorted_sources)
        
        return (sorted_sources, errors)
```

**Key change from V1:** `DiscoveryCache` is a separate injectable class. This enables testing API logic without mocking cache internals, and logging cache hits/misses explicitly.

### Provenance Recording with Crash Safety

**Algorithm:** Provenance is written via try/finally to ensure partial records survive crashes.

```python
class SourceRouter:
    def extract(self, identifiers: DocumentIdentifiers, output_dir: Path) -> ExtractionResult:
        provenance = ProvenanceRecord(
            document_id=identifiers,
            created_at=datetime.utcnow().isoformat(),
            pipeline_version=__version__,
        )
        result: ConversionResult | None = None
        
        try:
            # Check resumability
            existing = self.provenance_manager.load(output_dir, hash_identifiers(identifiers))
            if existing and existing.outcome == "success":
                return ExtractionResult.already_complete(existing)
            
            # Discovery
            sources, discovery_errors = self.discoverer.discover(identifiers)
            provenance.discovered_sources = sources
            provenance.discovery_errors = discovery_errors
            provenance.discovery_cached = self.discoverer.last_was_cached  # Set by discoverer
            
            # Extraction (orchestrator records attempts internally)
            attempts, result = self.orchestrator.orchestrate(sources, self._fetch)
            provenance.attempts = attempts
            
            # Classify outcome
            outcome, category = self.classifier.classify(attempts, discovery_errors)
            provenance.outcome = outcome
            provenance.failure_category = category
            if result:
                provenance.final_converter = result.converter_name
                
        except Exception:
            # On unexpected crash, mark as failed with whatever we have
            if not provenance.outcome:
                provenance.outcome = "failed"
                provenance.failure_category = "unknown"
            raise
        finally:
            # Always write provenance — partial is better than missing
            provenance.total_elapsed_seconds = elapsed_since(provenance.created_at)
            self.provenance_manager.write(output_dir, provenance)
        
        return ExtractionResult(
            markdown=result.markdown if result else None,
            provenance=provenance,
        )
```

**Key change from V1:** Constraint #6 is now implementable via try/finally. The provenance record is built incrementally (discovery results, then attempts) and written in the finally block regardless of how the extraction terminates.

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
agentic-mbse clear-cache [--max-age-days=30] [--identifier=IDENTIFIER]

# Retry failed/partial documents in a batch output directory
agentic-mbse retry-failed OUTPUT_DIR
```

### `--format` Override Semantics

The `--format` flag controls source selection:

| Value | Behavior |
|-------|----------|
| `auto` (default) | Run full discovery, attempt sources in quality tier order with fallback |
| `pdf` | Skip discovery entirely, extract from PDF only (local file or URL) |
| `jats` | Skip discovery, only attempt JATS XML extraction; fail if no JATS source available |
| `arxiv_html` | Skip discovery, only attempt arXiv HTML extraction; fail if no arXiv HTML source available |

When `--format` is not `auto`, the router still records provenance (what was attempted and why), but does not discover or attempt other formats.

### `format_hint` for Local Files

For local structured files, `format_hint` declares the file's format (it is not a soft suggestion — it controls which converter handles the file):

```bash
# Local file with format declaration
agentic-mbse extract article.xml --format-hint=jats_xml
```

In batch JSONL:
```jsonl
{"local_path": "/path/to/article.xml", "format_hint": "jats_xml"}
```

`format_hint` applies only to `local_path` sources. For remote sources, format is determined by discovery metadata.

### CLI Error Handling

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | All documents extracted successfully |
| `1` | Partial success — some documents failed; see triage report |
| `2` | Fatal error — invalid arguments, missing config, unrecoverable error |

**Edge case behaviors:**

| Scenario | Behavior |
|----------|----------|
| `--output-dir` doesn't exist | Create it (mkdir -p) |
| Invalid DOI/arXiv ID format | Exit 2, print `"Invalid identifier format: {input}. Expected DOI (10.xxxx/...) or arXiv ID (YYMM.NNNNN)"` |
| `extract-batch` malformed JSONL | Exit 2, print `"Invalid JSON on line {N}: {error}"` |
| `extract-batch` per-document failure | Continue processing remaining documents, record failure in provenance, exit 1 at end |
| `extract-batch` all documents succeed | Exit 0 |
| `triage-report` with existing report | Overwrite (report is a generated artifact, always regenerable) |
| `clear-cache --identifier=X` not found | Print `"No cache entry found for {X}"`, exit 0 (not an error) |

### API (Python Library)

**For integration into fusion-tea or other projects:**

```python
from agentic_mbse.source_router import SourceRouter
from agentic_mbse.triage import TriageReportGenerator

# Single-document extraction
router = SourceRouter()
result = router.extract(
    identifiers=DocumentIdentifiers(doi="10.1103/PhysRevLett.116.061102"),
    output_dir=Path("output/"),
    format_override=None  # or "pdf" to force PDF
)
# result.markdown, result.provenance, result.provenance.outcome

# Batch extraction
results = router.extract_batch(
    documents=[
        DocumentIdentifiers(doi="..."),
        DocumentIdentifiers(arxiv_id="..."),
        ...
    ],
    output_dir=Path("output/")
)
# results: list[ExtractionResult]
# Each document gets its own provenance.json in output_dir/{hash}/

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
      "converter_used": "JATSPandocConverter",
      "warnings": ["Table 2 missing column headers"]
    }
  ],
  "outcome": "success",
  "final_converter": "JATSPandocConverter",
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
**Latest provenance record:** 2026-02-09 14:28:15 UTC

## Summary

- Success: 38 (73%)
- Partial: 8 (15%)
- Failed: 6 (12%)

---

## Failed Documents

### needs_ocr (3 documents)

These documents are scanned PDFs with no extractable text. OCR processing required.

- `doi:10.1234/scanned.paper` — 2 attempts, last error: "no extractable text found"
- `local:/papers/old_scan.pdf` — 1 attempt, last error: "empty text extraction"
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
3. **Non-destructive retries** — Retrying a failed document MUST NOT delete or overwrite the previous `provenance.json`; instead, replace with a cumulative record that includes the new attempts.
4. **Discovery cache correctness** — If a cache entry exists and is fresh, it MUST be used; API calls for cached identifiers are forbidden (prevents rate limit exhaustion).
5. **Source ordering determinism** — Given the same discovered sources, extraction MUST attempt them in the same order (quality tier, then URL/path lexicographic). Non-determinism breaks debugging.
6. **Crash-safe provenance** — If extraction crashes mid-attempt, `provenance.json` MUST still be written with all completed attempts via try/finally block. The record will have `outcome="failed"` and `failure_category="unknown"` if classification didn't complete.

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
4. **Triage report ordering** — Failed documents within a category MUST be sorted by display_key() for diffability

**Allowed non-determinism:**

- Timestamps (`created_at`, `started_at`) — vary by run time
- API response times (`elapsed_seconds`) — vary by network latency
- Discovery cache hits — vary by cache state, but outcome (discovered sources) must be deterministic

## 7. Phasing

### Phase 1: Foundation (Work Items 1–2)

**Scope:**
- Data model: `DocumentIdentifiers`, `SourceCandidate`, `ExtractionAttempt`, `ProvenanceRecord`, `ConversionError`, `ConversionResult`, `QualityFlags`, `ValidationResult`
- `Converter` base class with `validate_source()`, `convert()`, and `name` property
- `ConverterRegistry` with `register()` and `get_converter()`
- `DiscoveryCache` as separate injectable class
- `SourceDiscoverer` with injected cache and API clients (OpenAlex integration)
- `ExtractionOrchestrator` (extraction loop, attempt recording)
- `OutcomeClassifier` (outcome determination, failure categorization from typed attempts)
- `ProvenanceManager` (write/load provenance records, no retry logic)
- `SourceRouter` as thin facade coordinating above components
- Enhanced resumability (retry failed/partial outcomes) in `SourceRouter`
- Wrap existing PDF converter (`PyMuPDF4LLMConverter`) with new `Converter` interface (including `validate_source()` and typed `ConversionError`)
- CLI: `extract`, `retry-failed`, `clear-cache` commands with specified exit codes and error handling

**Deliverables:**
- `agentic-mbse extract <doi>` produces `provenance.json`
- `agentic-mbse retry-failed` skips successes, retries failures
- `agentic-mbse clear-cache --identifier=doi:10.1234/...` invalidates single entry
- Discovery cache speeds up re-runs
- Unit tests for discovery, caching, routing logic, outcome classification, provenance crash-safety

**Why first:** Everything else depends on provenance recording and routing infrastructure. Can be tested with existing PDF pipeline.

### Phase 2: New Converters (Work Item 3)

**Scope:**
- `JATSPandocConverter` — JATS XML converter (pandoc-based), with JATS-specific `validate_source()` and typed `ConversionError`
- `ArXivHTMLConverter` — arXiv HTML converter (custom HTML parser), with arXiv-specific validation
- `PublisherHTMLConverter` — Publisher HTML converter (BeautifulSoup-based, generic), with paywall detection in `validate_source()`
- Local structured file support (`--format-hint` for XML/HTML input)

**Deliverables:**
- `agentic-mbse extract <doi>` automatically prefers JATS/arXiv HTML over PDF
- `agentic-mbse extract article.xml --format-hint=jats_xml` works
- Each converter registers with `ConverterRegistry` and is self-contained (validation + conversion + typed errors)
- Unit tests for each converter

**Why second:** Converters are truly independent — each implements the full `Converter` interface (validation + conversion + error typing) with no shared component to update. Require Phase 1 routing to be functional.

### Phase 3: Triage & Failure Categorization (Work Item 4)

**Scope:**
- `TriageReportGenerator` (aggregate provenance records, group by outcome/category, render Markdown)
- `agentic-mbse triage-report` CLI command
- Report includes `provenance_latest_timestamp` for staleness detection

**Deliverables:**
- `TRIAGE_REPORT.md` generated after batch extraction
- Failures grouped by actionable category
- Partial successes listed with warnings
- Report regenerable from existing provenance records, always overwrites existing

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

**Why validation co-located with converters?** — Format-specific validation (paywall detection for HTML, body checks for XML, text presence for PDF) belongs with the converter that knows the format. This eliminates the dispatch problem and makes converters truly self-contained.

**Why JSON provenance + Markdown triage?** — Provenance is structured data (easy to query, aggregate, version); triage is a human communication artifact (easy to read, share, diff).

---

## Changes from V1

- **Typed `ConversionError` with `category` field**: Converters now raise `ConversionError(message, category=FailureCategory)` instead of generic exceptions. `OutcomeClassifier` reads typed fields instead of parsing error message strings. — Addresses Critical Issue #1 (converter error contract underspecified).

- **Removed standalone `ContentValidator`; validation moved to `Converter.validate_source()`**: Each converter implements format-specific validation co-located with its conversion logic. Eliminates the dispatch problem (how does a central validator know format-specific checks?). — Addresses Critical Issue #2 (ContentValidator dispatch mechanism missing).

- **Added `converter_name` to `ConversionResult` and `name` property to `Converter`**: Each converter populates its name in results, enabling unambiguous provenance recording. — Addresses Critical Issue #3 (ExtractionAttempt.converter_used provenance ambiguous).

- **Provenance writing via try/finally with incremental record building**: `SourceRouter.extract()` builds the `ProvenanceRecord` incrementally and writes it in a finally block. Constraint #6 reworded to specify try/finally mechanism. — Addresses Critical Issue #4 (crash-safety requirement unimplementable as specified).

- **Split `SourceRouter` into facade + `ExtractionOrchestrator` + `OutcomeClassifier`**: `SourceRouter` is now a thin coordinator. Orchestration logic (looping sources, recording attempts) is in `ExtractionOrchestrator`. Outcome determination and failure categorization is in `OutcomeClassifier`. Each component is single-purpose and independently testable. — Addresses Major Issue #5 (SourceRouter overloaded with responsibilities).

- **Added `primary_identifier()` and `display_key()` to `DocumentIdentifiers`; specified multi-identifier merge logic**: Discovery queries all identifiers, unions and deduplicates sources. Cache keyed by primary identifier (doi > arxiv_id > pmc_id > local_path). — Addresses Major Issue #6 (multi-identifier semantics underspecified).

- **Added CLI error handling specification**: Exit codes (0/1/2), edge case behaviors (missing dir, invalid input, per-document failure), error message formats all documented in a table. — Addresses Major Issue #7 (CLI error handling unspecified).

- **Specified `--format` override semantics**: `auto` = full discovery; `pdf`/`jats`/`arxiv_html` = skip discovery, force single format. Documented in table format. — Addresses Major Issue #8 (`--format` ambiguous).

- **Typed `QualityFlags` dataclass replaces untyped dict; typed `ValidationResult` replaces optional untyped dict**: Both now have explicit fields. `SourceCandidate.metadata` replaced with named fields (`http_content_type`, `publisher`, `license`). — Addresses Major Issue #9 (untyped dumping grounds).

- **`DiscoveryCache` extracted as separate injectable class**: `SourceDiscoverer` receives `DiscoveryCache` via constructor injection instead of embedding caching internally. Cache has explicit `get`/`put`/`invalidate`/`clear` API. — Addresses Minor Issue #10 (caching embedded in discoverer).

- **`should_retry()` removed from `ProvenanceManager`**: Resumability logic stays in `SourceRouter` (which already decides what to extract). `ProvenanceManager` is a pure persistence layer. — Addresses Minor Issue #11 (unclear responsibility boundary).

- **Removed `ttl_days` from `DiscoveryCacheEntry`**: TTL is a global config setting. Freshness computed from `cached_at` + config value. No per-entry TTL storage. — Addresses Minor Issue #12 (redundant TTL storage).

- **Triage report always overwrites; includes `provenance_latest_timestamp`**: Report header shows latest provenance timestamp for staleness detection. Overwrite is default (report is a generated artifact). — Addresses Minor Issue #13 (triage regeneration idempotency).

- **Added `clear-cache --identifier=IDENTIFIER` option**: Per-identifier cache invalidation for debugging bad discovery results. — Addresses Minor Issue #14 (no per-identifier invalidation).

- **Phase 2 independence confirmed by co-located validation**: Since validation moved into converters, adding new converters in Phase 2 is truly independent — no shared `ContentValidator` to update. — Addresses Minor Issue #15 (Phase 2 independence conflicts with shared validation).

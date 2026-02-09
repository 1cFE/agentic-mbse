# Design Review

## Dimensional Assessment

### 1. Concept Compliance
**Assessment:** Pass

**Findings:**

The design comprehensively addresses all six success criteria from the concept:

1. **Best-available source** (SC-1): Covered by `SourceRouter` + `SourceDiscoverer` with quality tier ordering and automatic fallthrough on validation failure
2. **Processing provenance** (SC-2): Complete `ProvenanceRecord` schema captures all required data (sources discovered, attempts, converter used, failure category, warnings)
3. **Graceful degradation** (SC-3): Three-level outcome taxonomy ("success"/"partial"/"failed") with typed `FailureCategory` enum
4. **Triage report** (SC-4): `TriageReportGenerator` groups by failure category, generated from provenance records, regenerable
5. **Extensibility** (SC-5): `ConverterRegistry` with `Converter` interface allows new converters via registration, demonstrated by three new converters (JATS, arXiv HTML, publisher HTML)
6. **Enhanced resumability** (SC-6): `ProvenanceManager.should_retry()` enables retry logic, discovery cache prevents re-querying APIs

All seven user stories map to specific components:
- US-1 (fire-and-forget): `SourceRouter.extract_batch()` with quality tier ordering
- US-2 (post-run triage): `TriageReportGenerator.generate()` + Markdown output
- US-3 (incremental re-processing): `should_retry()` + discovery cache
- US-4 (understand what happened): `provenance.json` per document
- US-5 (debug source discovery): `discovered_sources` + `discovery_errors` in provenance
- US-6 (add new converter): `ConverterRegistry.register()` + `Converter` interface
- US-7 (process local structured files): `LocalFileDiscoverer` + `format_hint` parameter

Edge cases from concept are addressed:
- Documents without identifiers fall through to PDF (via empty `discovered_sources`)
- API rate limit handling is deferred (open question #3), but cache reduces likelihood
- Offline mode silently degrades (no API calls = empty discovery results = local file only)

### 2. Abstraction Quality
**Assessment:** Concerns

**Findings:**

**Strengths:**
- Clean separation of concerns: discovery (`SourceDiscoverer`), validation (`ContentValidator`), conversion (`ConverterRegistry`), orchestration (`SourceRouter`), reporting (`TriageReportGenerator`)
- `Converter` interface is minimal and appropriately abstract (can_convert + convert)
- `ProvenanceRecord` is self-contained and comprehensible

**Concerns:**

1. **SourceRouter is overloaded** — The router handles orchestration, validation coordination, attempt recording, outcome determination, and fallthrough logic. This is 5+ responsibilities in one component. A developer debugging "why did this source fail validation?" has to read through all the orchestration code to understand the validation call.

2. **ContentValidator abstraction is too thin** — The validator has one method (`validate()`) but the design shows it needs format-specific logic (HTML paywall detection, XML body checks, PDF text detection). This will either bloat into a mega-function with format switches, or need subclasses (`HTMLValidator`, `XMLValidator`, etc.), but that's not reflected in the API.

3. **SourceDiscoverer combines API clients and caching** — The `discover()` method hides whether results come from cache or API. This makes testing harder (can't test API logic without mocking cache) and obscures cache behavior in logs. `SourceDiscoverer` should coordinate separate `DiscoveryCache` and API clients, not embed caching logic.

4. **ProvenanceManager has unclear scope** — It writes/loads records, but also has `should_retry()` logic. Is it a persistence layer or a decision engine? The resumability logic (`should_retry()`) arguably belongs in `SourceRouter` (which already decides what to extract), not the storage layer.

### 3. Duplication Avoidance
**Assessment:** Pass

**Findings:**

No significant duplication detected:

- Source quality ranking is centralized in `QUALITY_TIERS` constant
- Validation logic is unified in `ContentValidator` (avoiding per-converter validation)
- Failure categorization is a single algorithm (`assign_failure_category()`) rather than per-converter error mapping
- Triage report generation aggregates from a single source of truth (`provenance.json` files)
- Converter registration uses a single registry rather than parallel routing structures

**Minor note:** The design mentions both `summary.json` (existing extraction metadata) and `provenance.json` (new). There's potential conceptual overlap (e.g., both might store "source path"), but the design explicitly keeps them separate to avoid breaking existing output schema. This is acceptable given backward compatibility constraint.

### 4. Data Structure Clarity
**Assessment:** Concerns

**Findings:**

**Strengths:**
- `ProvenanceRecord` is well-specified with clear field types and semantics
- `SourceCandidate` cleanly separates remote (`url`) vs. local (`local_path`) sources
- `ExtractionAttempt` captures all relevant attempt metadata
- `TriageReport` structure is explicit and matches Markdown output format

**Concerns:**

1. **DocumentIdentifiers is ambiguous under multiple identifiers** — The schema allows `{doi: "...", arxiv_id: "...", pmc_id: "..."}` simultaneously, but the design doesn't specify:
   - Which identifier is "primary" for cache keying? (Design mentions "Use DOI as primary cache key; if DOI cache misses, fall back to arXiv ID" but this isn't in the data model)
   - When multiple identifiers resolve to different source sets, how are they merged?
   - If `doi` and `arxiv_id` point to different versions of the same paper, does the system detect this?

2. **ConversionResult.quality_flags is untyped dict** — The schema shows `quality_flags: dict` with example `{"has_tables": True, "tables_likely_corrupted": False}`, but there's no specification of valid keys or value types. This will drift over time as converters add arbitrary flags. Should be a typed dataclass or at minimum a documented schema.

3. **ExtractionAttempt.validation_details is optional and untyped** — Similar issue: `validation_details?: { content_length?: number, ... }` is partial and inconsistent. When `outcome="validation_failed"`, these details should be mandatory, not optional. The type should enforce this (e.g., a discriminated union based on outcome).

4. **Metadata field in SourceCandidate is vague** — `metadata?: { content_type?: string, publisher?: string, license?: string }` — this is a dumping ground. What is `content_type` used for? Is it the HTTP Content-Type header, or a semantic type? Should it be a separate field? This will become a junk drawer.

5. **DiscoveryCacheEntry.ttl_days is stored per entry but appears to be a global config** — The config file shows `cache_ttl_days: 30` as a system-wide setting, but each cache entry stores its own `ttl_days`. If TTL is per-entry, why? If it's global, why store it redundantly?

### 5. Interface Completeness
**Assessment:** Concerns

**Findings:**

**Strengths:**
- CLI commands are well-specified with argument formats
- Python API shows clear entry points (`SourceRouter.extract()`, `TriageReportGenerator.generate()`)
- Input formats (JSONL, YAML config) are explicit with examples
- Output formats (JSON, Markdown) are specified with schemas/examples

**Concerns:**

1. **Missing error handling in CLI spec** — The CLI section doesn't specify:
   - Exit codes (0 for success, 1 for failure, 2 for partial?)
   - What happens if `--output-dir` doesn't exist (create it? error?)
   - What happens if `extract <doi>` is given an invalid DOI (error message format?)
   - Does `extract-batch` continue on per-document failure or halt the batch?

2. **Ambiguous `--format` override behavior** — The CLI shows `--format=auto|pdf|jats|arxiv_html`, but:
   - Does `--format=jats` skip discovery and only try JATS? Or does it just prioritize JATS but still fall back?
   - If a user specifies `--format=jats` but no JATS source is discovered, does extraction fail or fall back to PDF?
   - The design rationale says "User can override with `--format=pdf` to force PDF extraction (bypasses discovery)", but this isn't in the API spec.

3. **`format_hint` vs. `format` is confusing** — The input format shows `{"local_path": "...", "format_hint": "jats_xml"}` and the CLI shows `--format-hint=jats_xml`, but the config shows `default_format: "auto"`. Are these the same concept? If `format_hint` is "this file is JATS XML", why is it a hint (implying optional) rather than a declaration?

4. **Triage report regeneration isn't idempotent** — The CLI shows `agentic-mbse triage-report OUTPUT_DIR [--output=TRIAGE_REPORT.md]`, but:
   - What if `TRIAGE_REPORT.md` already exists (overwrite? error? append?)?
   - Can you regenerate for a subset of documents (e.g., only failed ones)?
   - The design says "regenerable from provenance records" but doesn't specify whether the report includes a "last generated" timestamp or hash of included provenance records (needed to detect staleness).

5. **Missing batch extraction output specification** — `extract-batch` input format is specified (JSONL with identifiers), but output is unclear:
   - Does it write one `provenance.json` per document (implied by single-document behavior)?
   - Does it produce a batch-level summary (like MANIFEST.jsonl)?
   - Does it write `TRIAGE_REPORT.md` automatically, or do you have to run `triage-report` afterward?
   - The fusion-tea integration (Phase 4) says "Auto-generate triage report after batch runs", but that's project-specific behavior, not library behavior.

### 6. Implementability
**Assessment:** Concerns

**Findings:**

**Strengths:**
- Phase 1 is genuinely standalone (provenance + routing without new converters)
- No circular dependencies detected
- Phasing is logical (foundation → converters → reporting → integration)

**Concerns:**

1. **SourceRouter depends on ContentValidator, but ContentValidator needs source-specific validation logic** — The `ContentValidator.validate()` algorithm shows format-specific checks (e.g., paywall detection for HTML, body content checks for XML). But `SourceCandidate.format` is just a string enum. How does `ContentValidator` dispatch format-specific logic? Either:
   - It needs a reference to `ConverterRegistry` to ask "which converter handles this format?" (creates coupling), OR
   - It needs to duplicate format knowledge (violates DRY), OR
   - Validation logic should be part of `Converter.convert()` (but then you can't validate before fetching).

2. **ExtractionAttempt records converter_used, but converter selection happens in ConverterRegistry** — The flow is: `SourceRouter` → `ConverterRegistry.convert()` → returns `ConversionResult`. Where does the converter name come from? The design shows `converter_used: "jats_pandoc"` in the provenance, but `ConverterRegistry.convert()` returns `ConversionResult`, not `(converter_name, ConversionResult)`. Either:
   - `ConversionResult` needs a `converter_name` field, OR
   - `ConverterRegistry.convert()` needs to return metadata, OR
   - `SourceRouter` has to track which converter was invoked (fragile).

3. **Failure category assignment requires interpreting error messages** — The `assign_failure_category()` algorithm has logic like:
   ```python
   if "no extractable text" in (last_pdf.error_message or "").lower():
       return "needs_ocr"
   ```
   This assumes converters return structured error messages with predictable substrings. But `Converter.convert()` is specified to raise `ConversionError`, which is a generic exception. How does the router get the error message? Does `ConversionError` have a `message` field? What if a converter raises `ValueError` instead? The design doesn't specify error handling contract between converters and router.

4. **Discovery caching creates implicit state** — The `discover_with_cache()` algorithm writes cache entries, but there's no specified way to invalidate them except `agentic-mbse clear-cache` (which clears all) or waiting for TTL expiry. If a user discovers that OpenAlex returned a wrong URL for DOI X, how do they force a re-query for just that DOI? The design doesn't specify per-identifier cache invalidation, making debugging harder.

5. **Provenance record writing happens at the end, but design requires recording partial attempts** — The design's must-never-violate rule #6 says "If extraction crashes mid-attempt, the `provenance.json` MUST still be written with all completed attempts." But the data flow shows provenance is written at the end (step 6: "Output: Write provenance.json"). How is partial provenance persisted if Python crashes during step 4? Either:
   - Provenance must be written incrementally after each attempt (but design doesn't specify this), OR
   - The crash-safety requirement is unimplementable without transactional writes or write-ahead logging.

6. **Phase 2 "converters are independent" conflicts with shared validation** — Phase 2 says "Converters are independent of each other; can be developed in parallel." But if `ContentValidator` has format-specific logic (concern #1 above), adding a new converter in Phase 2 might require updating `ContentValidator`, violating the independence claim. This suggests a design gap.

---

## Issues by Severity

### Critical (Must address before implementation)

1. **Converter error contract is underspecified** — (Implementability) `assign_failure_category()` depends on parsing error messages, but `Converter.convert()` API doesn't specify error types or message format. Without this, failure categorization is brittle. **Fix:** Define `ConversionError` exception with typed fields (`category: FailureCategory`, `details: dict`), update `Converter` interface to document raised exceptions.

2. **ContentValidator dispatch mechanism is missing** — (Implementability) `ContentValidator.validate()` needs format-specific logic, but there's no specified way to dispatch based on `SourceFormat`. **Fix:** Either make `ContentValidator` an abstract class with subclasses per format, OR add `Converter.validate_source(content)` method and have `SourceRouter` call it before `convert()`.

3. **ExtractionAttempt.converter_used provenance is ambiguous** — (Implementability) No specified mechanism to capture which converter was used. **Fix:** Add `converter_name: str` field to `ConversionResult`, populated by each converter.

4. **Crash-safety requirement for provenance is unimplementable as specified** — (Implementability) Constraint #6 requires partial provenance on crash, but data flow writes provenance once at the end. **Fix:** Either relax constraint to "best-effort partial provenance" with try/finally block, OR specify incremental provenance writes (append attempts to `.provenance.partial.json` during extraction, rename to `.provenance.json` on success).

### Major (Should address)

5. **SourceRouter is overloaded with responsibilities** — (Abstraction Quality) Mixes orchestration, validation coordination, attempt recording, and outcome logic. **Fix:** Extract `ExtractionOrchestrator` (handles loop over sources) and `OutcomeClassifier` (determines success/partial/failed + category) as separate classes, leave `SourceRouter` as thin facade.

6. **DocumentIdentifiers multi-identifier semantics are underspecified** — (Data Structure Clarity) No clear priority rules or merge logic when multiple identifiers present. **Fix:** Add `primary_identifier()` method to `DocumentIdentifiers`, specify merge behavior in `SourceDiscoverer` (e.g., union of all discovered sources, deduplicated by URL).

7. **CLI error handling and edge cases are unspecified** — (Interface Completeness) Exit codes, missing directory behavior, invalid input handling not documented. **Fix:** Add "Error Handling" subsection to External Interfaces specifying exit codes, error message formats, and edge case behaviors.

8. **`--format` override semantics are ambiguous** — (Interface Completeness) Unclear whether it forces one format or just prioritizes. **Fix:** Specify: `--format=pdf` means "skip discovery, only try PDF fallback"; `--format=auto` (default) means "use discovery + quality tier ordering."

9. **ConversionResult.quality_flags and metadata fields are untyped dumping grounds** — (Data Structure Clarity) Will accumulate inconsistent keys over time. **Fix:** Define typed schemas: `QualityFlags(has_tables: bool, tables_corrupted: bool, ...)` and `SourceMetadata(content_type: str, publisher: str, ...)` as dataclasses.

### Minor (Consider addressing)

10. **SourceDiscoverer embeds caching instead of coordinating it** — (Abstraction Quality) Makes testing and logging harder. **Fix:** Make `DiscoveryCache` a separate class, inject into `SourceDiscoverer`, call explicitly: `cache.get() → API.query() → cache.put()`.

11. **ProvenanceManager has unclear responsibility boundary** — (Abstraction Quality) Mixes persistence and retry logic. **Fix:** Move `should_retry()` to `SourceRouter` or new `ResumabilityPolicy` class.

12. **DiscoveryCacheEntry.ttl_days redundancy** — (Data Structure Clarity) TTL appears to be global config but stored per entry. **Fix:** Either remove `ttl_days` from entry (compute from config + `cached_at` timestamp), OR document why per-entry TTL is needed (e.g., different TTLs for DOI vs. arXiv cache).

13. **Triage report regeneration idempotency is underspecified** — (Interface Completeness) Overwrite behavior and staleness detection not documented. **Fix:** Add `--force` flag to overwrite, include "Generated from N provenance records as of <latest timestamp>" header in report.

14. **Discovery cache lacks per-identifier invalidation** — (Implementability) Can only clear entire cache, making debugging hard. **Fix:** Add `agentic-mbse clear-cache --identifier=doi:10.1234/...` option.

15. **Phase 2 independence claim conflicts with shared validation** — (Implementability) If `ContentValidator` is centralized with format-specific logic, new converters aren't truly independent. **Fix:** Move validation into converters (concern #2 resolution).

---

## Specific Recommendations

### 1. Define Converter Error Contract (Critical Issue #1)

**Current problem:** `Converter.convert()` can raise arbitrary exceptions, but `assign_failure_category()` parses error messages with substring matching, which is fragile.

**Recommendation:**

```python
class ConversionError(Exception):
    def __init__(
        self, 
        message: str, 
        category: FailureCategory,
        details: dict[str, Any] = None
    ):
        super().__init__(message)
        self.category = category
        self.details = details or {}

class Converter(ABC):
    @abstractmethod
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        """
        Convert content to markdown.
        
        Raises:
            ConversionError: Typed exception with failure category
        """
```

Then `assign_failure_category()` becomes:

```python
def assign_failure_category(attempts: list[ExtractionAttempt]) -> FailureCategory:
    # If any attempt has a typed category, use the most specific one
    for attempt in reversed(attempts):  # Most recent first
        if attempt.failure_category:
            return attempt.failure_category
    
    # Fallback heuristics for unexpected errors
    # ...
```

This makes failure categorization deterministic and extensible.

### 2. Resolve ContentValidator Dispatch (Critical Issue #2)

**Current problem:** `ContentValidator` needs format-specific logic, but no dispatch mechanism specified.

**Recommendation:** Move validation into converters, remove `ContentValidator` as separate component:

```python
class Converter(ABC):
    @abstractmethod
    def validate_source(self, content: bytes) -> ValidationResult:
        """Validate fetched content before conversion attempt."""
    
    @abstractmethod
    def convert(self, content: bytes, metadata: dict) -> ConversionResult:
        """Convert validated content to markdown."""
```

Then `SourceRouter` flow becomes:

```python
for candidate in sorted_candidates:
    content = fetch(candidate)
    
    converter = registry.get_converter(candidate.format)
    validation = converter.validate_source(content)
    
    if not validation.is_valid:
        record_attempt(outcome="validation_failed", validation_details=validation.details)
        continue
    
    try:
        result = converter.convert(content, metadata)
        record_attempt(outcome="success", converter_used=converter.name)
        break
    except ConversionError as e:
        record_attempt(outcome="conversion_failed", failure_category=e.category)
        continue
```

This eliminates the dispatch problem and makes validation logic co-located with conversion logic (better cohesion).

### 3. Add converter_name to ConversionResult (Critical Issue #3)

**Simple fix:**

```python
class ConversionResult:
    markdown: str
    warnings: list[str]
    quality_flags: dict  # (fix with Issue #9)
    converter_name: str  # NEW: populated by each converter
```

Each converter sets `converter_name = self.__class__.__name__` in `convert()` method.

### 4. Specify Incremental Provenance Writes (Critical Issue #4)

**Current constraint:** "If extraction crashes mid-attempt, provenance.json MUST still be written."

**Recommendation:** Relax to best-effort and document explicitly:

```python
class SourceRouter:
    def extract(self, identifiers: DocumentIdentifiers, output_dir: Path) -> ExtractionResult:
        provenance = ProvenanceRecord(document_id=identifiers)
        
        try:
            # Discovery
            provenance.discovered_sources = self.discoverer.discover(identifiers)
            
            # Extraction loop
            for candidate in sorted_sources:
                attempt = self._try_extract(candidate)
                provenance.attempts.append(attempt)  # Record immediately
                
                if attempt.outcome == "success":
                    break
        finally:
            # Write provenance even if loop crashes
            self.provenance_manager.write(output_dir, provenance)
        
        return ExtractionResult(provenance=provenance, ...)
```

Update constraint #6 to: "If extraction crashes, provenance.json MUST be written with all completed attempts using a try/finally block."

### 5. Split SourceRouter Responsibilities (Major Issue #5)

**Current design:** `SourceRouter` does orchestration + validation coordination + attempt recording + outcome classification.

**Recommendation:**

```python
class ExtractionOrchestrator:
    """Coordinates discovery → validation → conversion loop."""
    def orchestrate(self, identifiers, sources, registry) -> list[ExtractionAttempt]:
        attempts = []
        for source in sources:
            attempt = self._try_source(source, registry)
            attempts.append(attempt)
            if attempt.outcome == "success":
                break
        return attempts

class OutcomeClassifier:
    """Determines final outcome and failure category from attempts."""
    def classify(self, attempts: list[ExtractionAttempt]) -> tuple[DocumentOutcome, FailureCategory]:
        if any(a.outcome == "success" for a in attempts):
            return ("success", None)
        # ... other logic

class SourceRouter:
    """Facade coordinating discovery, orchestration, and provenance recording."""
    def extract(self, identifiers, output_dir):
        sources = self.discoverer.discover(identifiers)
        attempts = self.orchestrator.orchestrate(identifiers, sources, self.registry)
        outcome, category = self.classifier.classify(attempts)
        
        provenance = ProvenanceRecord(
            document_id=identifiers,
            discovered_sources=sources,
            attempts=attempts,
            outcome=outcome,
            failure_category=category
        )
        
        self.provenance_manager.write(output_dir, provenance)
        return ExtractionResult(...)
```

This makes each component single-purpose and testable in isolation.

### 6. Specify Multi-Identifier Resolution (Major Issue #6)

**Add to Data Model section:**

```python
class DocumentIdentifiers:
    doi: str | None
    arxiv_id: str | None
    pmc_id: str | None
    local_path: str | None
    
    def primary_identifier(self) -> tuple[str, str]:
        """Return (type, value) for primary identifier (used for cache keys)."""
        if self.doi:
            return ("doi", self.doi)
        if self.arxiv_id:
            return ("arxiv", self.arxiv_id)
        if self.pmc_id:
            return ("pmc", self.pmc_id)
        if self.local_path:
            return ("local", self.local_path)
        raise ValueError("At least one identifier required")
```

**Add to Source Discovery algorithm:**

When multiple identifiers present:
1. Query APIs for each identifier in parallel
2. Union all discovered sources, deduplicated by URL
3. Sort by quality tier
4. Cache result under primary identifier

### 7. Add CLI Error Handling Specification (Major Issue #7)

**Add to External Interfaces → CLI Commands:**

**Exit codes:**
- `0` — Success (all documents extracted successfully)
- `1` — Partial success (some documents failed, see triage report)
- `2` — Fatal error (invalid arguments, missing config, API auth failure)

**Error handling:**
- If `--output-dir` doesn't exist: create it (mkdir -p behavior)
- If input DOI/arXiv ID is malformed: exit code 2, print "Invalid identifier format: <input>"
- If `extract-batch` input JSONL is malformed: exit code 2, print line number and error
- `extract-batch` continues on per-document failure (records failure in provenance), exits 0 if at least one document succeeded

---

**Overall:** **Revise**

The design is architecturally sound and comprehensively addresses the concept, but has critical implementability gaps (error contracts, validation dispatch, provenance crash-safety) and abstraction concerns (overloaded SourceRouter, untyped dicts) that will cause problems during Phase 1 implementation. Addressing the 4 critical issues + splitting SourceRouter responsibilities will make this implementation-ready.

The phasing strategy is logical and the external interfaces are well-thought-out. With the recommended fixes, this design will deliver a robust, extensible document ingestion system.

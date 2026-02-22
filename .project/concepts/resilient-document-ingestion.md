# Concept: Resilient Document Ingestion

**Created:** 2026-02-09
**Status:** Draft

---

## Problem Statement

The current document extraction pipeline (agentic-mbse `extract` + fusion-tea `zotero_ingest.py`) treats PDF extraction as the universal path for all documents. The first corpus ingestion quality audit revealed that **all 5 sources failed on tables and 4/5 failed on headings** — problems inherent to extracting structured content from a format designed for visual rendering, not semantic representation.

Meanwhile, research shows that 40–60% of a typical scientific corpus has structured alternatives available (arXiv HTML, PMC JATS XML, publisher HTML) where every one of these failure modes disappears. The current pipeline doesn't look for these alternatives.

When extraction does fail — whether from scanned-only PDFs, corrupted tables, or unsupported document formats — there is no structured way to discover what went wrong, what was tried, or which documents need attention. Failures surface as CLI output lines that scroll past and are forgotten. A user processing 50+ documents from Zotero has no practical way to identify which ones need manual intervention, what kind of intervention they need, or whether a newly added extraction tool might resolve previously failed documents.

## Success Criteria

When this work is complete:

1. **Best-available source** — For documents with DOIs or arXiv IDs, the system discovers structured alternatives via bibliographic APIs and attempts them in quality order before falling back to PDF. If a structured source is fetched but fails validation (truncated, login page, empty body), it falls through to the next candidate automatically.
2. **Processing provenance** — Every document records a provenance trail containing, at minimum: sources discovered (format + URL), sources attempted (format + outcome + elapsed time), converter that produced the final output, failure category if applicable, and any warnings. This is stored as JSON alongside the extraction output.
3. **Graceful degradation** — When extraction cannot produce a high-quality result (e.g., scanned PDF, corrupted tables), the system extracts what it can and classifies the document outcome as "success", "partial", or "failed" with a failure category, rather than silently producing garbage or failing with only a CLI error message.
4. **Triage report** — After batch processing, a Markdown report groups failed and partial documents by failure category (e.g., "needs OCR", "table corruption", "no digital text", "source discovery failed", "timeout"). The report is generated from provenance records and can be regenerated at any time.
5. **Extensibility** — Adding a new source type or converter does not require modifying the orchestration logic. Demonstrated by the fact that the three new converters (JATS, arXiv HTML, publisher HTML) are added through the same mechanism as existing backends.
6. **Enhanced resumability** — Beyond the existing hash-based skip logic, rerunning ingestion retries documents that previously resulted in "failed" or "partial" outcomes. Source discovery results are cached locally so successful documents are not re-queried.

---

## User Stories

### Batch Ingestion

**US-1: Fire-and-forget corpus processing**
As a researcher, I can point the ingestion pipeline at my Zotero library and walk away, so that it processes every document using the best available method without me choosing backends or formats per-document.

**US-2: Post-run triage**
As a researcher, after a batch run completes, I can open a single Markdown report that shows me which documents failed, which are partial, and what category of problem each one has, so that I can prioritize remediation.

**US-3: Incremental re-processing**
As a researcher, when I add new documents to Zotero or when a new extraction capability becomes available, I can rerun ingestion and it processes new documents plus retries previously-failed ones, without re-extracting or re-querying APIs for documents that already succeeded.

### Debugging and Transparency

**US-4: Understand what happened**
As a researcher, for any extracted document, I can inspect its provenance record to see which source formats were discovered, which were attempted, which converter produced the final output, and any warnings, so that I can understand why a document's quality is what it is.

**US-5: Debug source discovery**
As a developer, I can see which API calls were made and what identifiers were resolved for a given document, so that I can diagnose why source discovery failed or chose an unexpected route.

### Extensibility

**US-6: Add a new converter**
As a developer, I can add support for a new extraction method (e.g., OCR, a new publisher XML format) by implementing the converter interface and registering it, so that all matching documents automatically benefit on the next run without changes to orchestration code.

**US-7: Process local structured files**
As a researcher, I can point the pipeline at a local HTML or XML file (not just PDF/DOCX), so that pre-downloaded structured sources are converted without requiring API-based discovery.

---

## Key Concepts

### 1. Source Router

The source router determines the best extraction route for a document without user intervention. Given a document's identifiers (DOI, arXiv ID, PMC ID, local file path), it discovers structured alternatives via bibliographic APIs, then attempts extraction in quality order with automatic fallthrough on failure. Each attempt is validated — fetched content must pass sanity checks (non-trivial length, correct content type, body content present) before conversion proceeds. The router produces a provenance record regardless of outcome.

From the user's perspective: you give it a document, it figures out the best way to extract it.

### 2. Provenance Record

Every document's extraction produces a provenance record: the complete decision trail from discovery through conversion. This record is the foundation for the triage report, enhanced resumability, and debugging. It is stored as structured JSON alongside the extraction output (extending or accompanying the existing `summary.json`).

From the user's perspective: you can always answer "what happened to this document?" by looking at its provenance record.

### 3. Triage Report

After batch processing, the triage report aggregates provenance records into a failure-categorized Markdown document. Documents are grouped by outcome (success, partial, failed) and failure category. The report is a generated artifact — it can be regenerated from provenance records at any time. Because it is Markdown, it is human-readable, diffable, and greppable by category.

From the user's perspective: one file tells you exactly what needs attention and why.

### 4. Failure Categories

The system classifies extraction outcomes into actionable categories rather than raw error messages. Categories like "needs OCR" (scanned PDF, no extractable text), "table corruption" (tables present but garbled), "timeout" (extraction exceeded time limit), "no source found" (no PDF or structured alternative available), or "source validation failed" (fetched content was truncated/empty/paywalled) help users understand what class of fix is needed. Categories are extensible — new converters can introduce new failure categories.

---

## Scope of Behavior Changes

*Note: This section describes the expected shape of changes, not binding design decisions.*

### New capabilities in agentic-mbse (reusable library)
- Source discovery — resolve DOI/arXiv ID to structured source candidates via bibliographic APIs
- HTML/XML converters — JATS XML, arXiv HTML, and publisher HTML conversion to markdown
- Source routing — orchestrate discovery → selection → conversion with fallthrough and provenance
- Provenance record — structured JSON capturing the full decision trail per document
- Triage report generation — produce categorized failure report from provenance records
- Local structured file support — accept HTML/XML as direct input, not just PDF/DOCX

### New capabilities in fusion-tea (project-specific pipeline)
- Updated ingestion script — uses source router instead of directly calling `agentic-mbse extract`
- Triage report output — generated after each batch run alongside MANIFEST.jsonl

### Behavior changes by workflow stage
- **Source identification**: Before extraction begins, the system resolves identifiers to structured alternatives (new step)
- **Extraction**: The router tries sources in quality order with validation and automatic fallthrough (replaces direct backend call)
- **Failure handling**: Outcomes are categorized as success/partial/failed with typed failure categories (replaces binary pass/fail)
- **Post-run**: A triage report is generated summarizing all outcomes (new artifact)
- **Re-run**: Provenance records plus cached discovery results enable intelligent skip/retry (enhanced resumability)

---

## Out of Scope

- **OCR implementation** — The system categorizes "needs OCR" as a failure type; implementing OCR is separate.
- **LLM enhancement improvements** — The v3 pipeline's Layer 3/4 (Claude structure repair, AI quality repair) is unchanged.
- **Publisher XML agreements** — Requesting text mining access from IOP or others is a manual process.
- **Zotero plugin development** — The pipeline reads from Zotero via API; no Zotero plugins.
- **Per-document quality scoring** — Automated quality grading (like the audit's headings/tables/images scoring) is a future enhancement.
- **Docling MCP auto-configuration** — Already scoped as ITEM-DOCLING-001.
- **Quality comparison between routes** — The system does not A/B test structured vs. PDF extraction for the same document. It trusts the quality tier ordering.
- **Content de-duplication** — If a document exists as both preprint and published version, the system does not reconcile versions.
- **Authenticated/credentialed source access** — Only freely accessible sources are attempted.
- **Parallel extraction** — Documents are processed sequentially within a batch run.
- **Formal offline mode** — Without internet, source discovery silently degrades to local-file-only extraction. No explicit offline flag.

---

## Assumptions & Prerequisites

- **OpenAlex API access** — Free tier (100K requests/day with API key) is sufficient. An email address is required.
- **Pandoc installed** — Already a system dependency for DOCX; JATS conversion uses the same binary.
- **Internet access during ingestion** — Source discovery requires API calls; silently degrades to PDF without connectivity.
- **agentic-mbse v3 pipeline is stable** — This concept layers on top of the existing 4-layer extraction pipeline.
- **Zotero items have DOIs or arXiv IDs** — Documents without identifiers fall straight through to PDF extraction.

## Open Questions

1. Should the provenance record extend `summary.json` or live as a separate file (e.g., `provenance.json`)?
2. What cache TTL is appropriate for source discovery results? (Days? Weeks? Indefinite until manually cleared?)
3. Should API rate limit exhaustion mid-batch degrade to PDF-only for remaining documents, or pause and retry?

---

## Decomposition Guidance

This concept splits into **five work items** with dependencies:

### Work Item 1: Provenance Schema & Enhanced Resumability (agentic-mbse)
Define the provenance record schema and integrate it into the extraction output. Extend the existing skip logic to retry "failed" and "partial" outcomes. This is foundational — everything else builds on it. No external API dependencies; can be tested entirely with the existing PDF pipeline.

### Work Item 2: Source Discovery & Routing (agentic-mbse)
Implement bibliographic API integration (OpenAlex), source candidate resolution, and the routing/fallthrough logic with content validation. Includes discovery result caching. Depends on Work Item 1 for provenance recording.

### Work Item 3: HTML/XML Converters (agentic-mbse)
Implement the three new converters (JATS XML via pandoc, arXiv HTML, publisher HTML) plus local structured file input support. Each converter is independently testable. Can be developed in parallel with Work Item 2 once the converter interface from Work Item 1 is defined.

### Work Item 4: Triage Report & Failure Categories (agentic-mbse)
Implement failure categorization and triage report generation from provenance records. Depends on Work Item 1 for provenance data. Can be developed in parallel with Work Items 2–3.

### Work Item 5: Fusion-tea Integration (fusion-tea)
Update `zotero_ingest.py` to use the source router, extend MANIFEST.jsonl with provenance summary, and generate the triage report after batch runs. Depends on Work Items 1–4.

**Parallelism:** After Work Item 1 is complete, Work Items 2, 3, and 4 can proceed in parallel. Work Item 5 integrates everything.

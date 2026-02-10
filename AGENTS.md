# AGENTS.md

## Build & Run

```bash
uv sync

# Run document ingestion (local PDF)
uv run agentic-mbse ingest /path/to/paper.pdf --output-dir data/ingested --format pdf

# Batch processing
uv run agentic-mbse ingest-batch input.jsonl --output-dir data/ingested

# Triage / retry / cache
uv run agentic-mbse triage-report data/ingested
uv run agentic-mbse retry-failed data/ingested
uv run agentic-mbse clear-cache data/ingested/.cache

# Run unit tests
uv run pytest tests/ -v

# Run corpus quality tests (after test harness is built)
uv run pytest tests/test_corpus.py --run-corpus

# Run integration tests (requires network access for API calls)
uv run pytest tests/test_quality_routing.py --run-integration

# Linting
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Codebase Layout

```
src/doc_ingest/           # Routing/provenance layer (new)
  cli.py                  # CLI commands
  source_router.py        # Top-level orchestrator
  extraction_orchestrator.py
  converters/             # Format-specific converters (NEED FIXING)
    pdf_converter.py      # Currently raw pymupdf4llm — must delegate to extraction pipeline
    html_converter.py     # ArXiv + Publisher HTML
    markdown_converter.py # JATS + DOCX via Pandoc
  provenance_manager.py
  discovery_cache.py
  source_discoverer.py    # Real API integration (OpenAlex, arXiv, PMC)
  api_clients/
    openalex.py           # OpenAlex Works API (DOI → PDF/HTML)
    arxiv.py              # arXiv HTML availability + PDF fallback
    pmc.py                # PMC E-utilities API (PMC ID → JATS XML)
  web_fetcher.py
  types.py

src/agentic_mbse/extraction/   # Proven extraction pipeline (existing)
  pymupdf_backend.py      # Layer 1: PyMuPDF4LLM + academic header detector
  postprocess.py          # Layer 1b: Header promotion, noise rejection, ligatures
  table_extraction.py     # Layer 2: GMFT table detection + repair
  quality_gates.py        # Problem detection between layers
  claude_structure.py     # Layer 3: Claude-assisted heading repair
  ai_repair.py            # Layer 4: Per-region AI repair with cross-validation
```

## Known Gotchas

**Converter registration**: `create_pipeline()` in `cli.py` MUST register all converters. This was missing and caused every extraction to fail with `unsupported_format`.

**Cross-package imports**: `doc_ingest` converters need to import from `agentic_mbse.extraction` to use the proven pipeline. Both packages are in the same repo.

**GMFT availability**: `gmft` is an optional dependency. Check `table_extraction.is_gmft_available()` before attempting Layer 2.

**Claude layers**: Layers 3-4 require the Claude CLI (`claude -p`). Gate behind `--enhance` flag.

**PMC rate limiting**: PMC E-utilities requires courtesy rate limiting (3 req/sec without API key, 10 req/sec with). Use `pmc_api_key` parameter if available.

**arXiv HTML availability**: Not all arXiv papers have HTML versions. Client checks via HEAD request (lightweight). PDF always available as fallback.

**PMC ID normalization**: PMC client normalizes IDs (adds "PMC" prefix if missing, case-insensitive). Accepts "PMC7463680", "pmc7463680", or "7463680".

**postprocess.py is pure functions**: Can be called on any markdown string with zero dependencies. This is the easiest quality win.

**pymupdf_backend.extract() takes a Path**: The doc_ingest converter receives `bytes`. Must write to temp file first, then call the backend.

**Page markers**: pymupdf_backend emits `<!-- PAGE:N -->` markers. quality_gates.py depends on these. Don't strip them.

**Test corpus setup**: PDFs copied from `../fusion-tea/knowledge/raw/`, baselines from `../fusion-tea/knowledge/sources/{dir}/full_document.md`. The fusion-tea directory structure uses long descriptive names; map to short slugs in `papers.jsonl`.

**Pytest custom markers**: Custom command-line options (like `--run-corpus`) must be registered in `tests/conftest.py` via `pytest_addoption()`, `pytest_configure()`, and `pytest_collection_modifyitems()`. Defining them in test files won't work — pytest won't recognize the option.

**Standalone scripts in tests/**: Scripts like `compare.py` that need to run both standalone (`python3 tests/corpus/compare.py`) and as modules need careful import handling. Use `sys.path.insert(0, str(Path(__file__).parent))` in `if __name__ == "__main__"` block, then import with `# type: ignore[import-not-found]` to satisfy both runtime and mypy.

**Custom header detectors in pymupdf_backend**: The `_academic_header_detector` was too conservative (only detected bold headers). Default pymupdf4llm font-size-based detection provides better coverage. Use default detector unless specific header patterns need custom handling.

**Plain header regex**: `_PLAIN_HEADER_RE` in postprocess.py must handle trailing periods (e.g., "1. Introduction" not just "1 Introduction"). Pattern needs `\.?` after section number: `(\d+(?:\.\d+)*)\.?\s+`.

**GMFT integration**: Layer 2 should be optional and graceful. Check `is_gmft_available()` before use. Wrap `enhance_tables()` call in try-except to prevent GMFT failures from breaking entire conversion. GMFT adds ~10-15% processing time but provides insurance for complex table layouts where line-based extraction fails.

**OpenAlex API client**: Rate limiting is built into the client (100ms delay between requests). No need for external throttling. `requests` library is already a dependency. Deduplication of PDF URLs is critical - OpenAlex returns the same PDF in multiple response fields (`oa_url`, `pdf_url`, `best_oa_location`). Skip landing pages that are just DOI resolvers (https://doi.org/...). Publisher HTML sources have quality tier 3 (lower than JATS/arXiv HTML tier 1-2, higher than PDF tier 4).

**Testing API clients**: Mock `requests.get()` with `patch("requests.get")` to avoid real API calls in unit tests. Use real OpenAlex response data from validation for mock responses. Test error cases (404, 500, network failures) separately. Verify timeout is set (prevents hanging on slow networks).

**Integration tests for quality routing**: Use `--run-integration` flag to test real API calls and quality-ordered routing. Integration tests use `tmp_path` fixture for isolated output directories. Tests verify: (1) sources are discovered in quality tier order, (2) extraction attempts sources in order (best first), (3) early exit on first success, (4) error handling is graceful (no crashes). Integration tests skip by default to keep CI fast.

**Unnumbered bold heading detection**: `promote_unnumbered_bold_headers()` in postprocess.py matches standalone bold lines like `**Site Improvements, Account 21.01**` and promotes to `###`. Filter function `_is_bold_heading_candidate()` rejects Table/Figure captions, definitions with `=`, split bold patterns, and non-alphanumeric separators. Minimum 15 chars to avoid short labels.

**All-caps heading detection**: `promote_allcaps_headers()` matches standalone all-caps lines between blank lines (e.g., ABSTRACT, REFERENCES). Uses `_is_allcaps_heading_candidate()` which rejects TOC entries (dot leaders) and requires either a space in the text or membership in a known single-word heading set. Promotes to `##` with title-casing.

**Corpus test heading thresholds**: The regression test in test_corpus.py uses per-paper heading thresholds from `heading_regression_pct` in papers.jsonl (default -10%). Papers whose baselines were generated with Claude Layer 3 have relaxed thresholds (helios: -90%, hsu: -50%). This prevents false regression failures while still catching actual regressions in the postprocessor.

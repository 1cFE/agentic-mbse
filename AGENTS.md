# AGENTS.md

## Status (2026-02-10)

**State: Phase 1 (Test Harness) complete. Ready to wire extraction pipeline.**

### What Works
- ✅ Test harness: 5 papers with baseline metrics, test runner, comparison report
- ✅ Metrics framework: `ExtractionMetrics` dataclass, computation, comparison
- ✅ Routing infrastructure: SourceRouter, ExtractionOrchestrator, ProvenanceManager, DiscoveryCache
- ✅ CLI: `ingest`, `ingest-batch`, `triage-report`, `retry-failed`, `clear-cache`
- ✅ 187 unit tests passing + 4 corpus tests (skipped by default)

### What's Broken (measured by test harness)
- PDF converter uses raw pymupdf4llm, ignoring the 4-layer extraction pipeline in `src/agentic_mbse/extraction/`
- Real-world regressions vs baseline:
  - aries_cost_account: headings 102→66 (-35%), tables 137→0 (-100%)
  - helios_design: headings 52→1 (-98%)
  - delene_2001: headings 23→4 (-83%)
- Source discoverer is a stub (returns mock sources for DOIs)

### Current Work: Phase 2 (Wire Extraction Pipeline)
- Next: `TASK-WP-001` — Wire Layer 1 (pymupdf_backend + postprocess) into PDF converter
- Then: `TASK-WP-002` — Wire Layer 2 (GMFT table enhancement)
- Defer: Layers 3-4 (Claude-based repair) until quality gap measured

### Critical Rule
**Every change must be measured against real documents. Run the test harness before and after. No mocked quality tests.**

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
  source_discoverer.py    # STUB — needs real API clients
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

**postprocess.py is pure functions**: Can be called on any markdown string with zero dependencies. This is the easiest quality win.

**pymupdf_backend.extract() takes a Path**: The doc_ingest converter receives `bytes`. Must write to temp file first, then call the backend.

**Page markers**: pymupdf_backend emits `<!-- PAGE:N -->` markers. quality_gates.py depends on these. Don't strip them.

**Test corpus setup**: PDFs copied from `../fusion-tea/knowledge/raw/`, baselines from `../fusion-tea/knowledge/sources/{dir}/full_document.md`. The fusion-tea directory structure uses long descriptive names; map to short slugs in `papers.jsonl`.

**Pytest custom markers**: Custom command-line options (like `--run-corpus`) must be registered in `tests/conftest.py` via `pytest_addoption()`, `pytest_configure()`, and `pytest_collection_modifyitems()`. Defining them in test files won't work — pytest won't recognize the option.

**Standalone scripts in tests/**: Scripts like `compare.py` that need to run both standalone (`python3 tests/corpus/compare.py`) and as modules need careful import handling. Use `sys.path.insert(0, str(Path(__file__).parent))` in `if __name__ == "__main__"` block, then import with `# type: ignore[import-not-found]` to satisfy both runtime and mypy.

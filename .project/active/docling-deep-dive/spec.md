# Spec: Docling & GMFT Deep-Dive (Stage 1C)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-22 13:47 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`

---

## Business Goals

### Why This Matters

The pymupdf4llm deep-dive (Stage 1A) established a strong baseline but identified four gap categories where pymupdf4llm cannot produce adequate output regardless of parameter tuning:

| Gap | Documents Affected | pymupdf4llm Behavior |
|-----|--------------------|----------------------|
| Complex tables (spanning cells, borderless) | aries_cost_account, araiinejad_2024, paischer_2025 | 333 `<br>` artifacts, lost cell structure |
| Math equations | hawker_2020, helios_design, sparc_overview, energy_amplifier, paischer_2025 | Garbled Unicode, replacement chars |
| OCR-quality documents | schulte_1978 | "~aboratory", "p r e p a d" — fundamental OCR errors |
| Scanned/image-only pages | (none in corpus, common in the wild) | Empty text extraction |

Docling (ML-based, TableFormer + DocLayNet) and GMFT (lightweight, DETR-based Table Transformer) are the two candidates for filling these gaps. The current `docling_backend.py` (136 lines) was written with a fixed config before these gaps were characterized. We need to understand both tools empirically — their actual quality on our corpus, their speed, their failure modes — before we can build a pipeline that routes pages to the right tool.

### Success Criteria

- [ ] Findings report documenting every Docling and GMFT configuration tested, with quality observations and comparative analysis
- [ ] Head-to-head comparison: pymupdf4llm vs Docling vs GMFT on the same tables/pages
- [ ] Clear understanding of when Docling adds value vs when it doesn't (and at what cost)
- [ ] Clear understanding of GMFT's accuracy and failure modes on our corpus
- [ ] A recommended configuration for each tool, backed by evidence
- [ ] Tested `DoclingExtractor` class ready for pipeline integration

### Priority

Foundation work. Directly unblocks Stage 2 (gap analysis) and Stage 3 (pipeline assembly). The pymupdf4llm baseline is solid but incomplete — this fills the remaining knowledge gaps in the extraction engine landscape.

---

## Problem Statement

### Current State

The existing `docling_backend.py` uses a hardcoded configuration:

```python
pipeline_opts = PdfPipelineOptions(
    do_table_structure=True,
    generate_picture_images=True,
    do_ocr=False,
)
```

This was written as a basic subprocess wrapper without investigating:
- What other `PdfPipelineOptions` parameters exist and what they do
- Whether `do_ocr=True` improves schulte_1978 or other difficult documents
- Docling's per-page vs full-document behavior and memory characteristics
- Table quality compared to GMFT (which benchmarks at 83% on the old branch's corpus)
- Performance across document sizes (9-page hsu_2020 vs 241-page energy_amplifier)

GMFT has no wrapper at all in the current codebase (the old branch had `table_extraction.py` but it was not carried forward).

### Desired Outcome

A **findings report** and **experiment results** that systematically evaluate Docling and GMFT against the 14-document corpus. The report characterizes both tools thoroughly — their strengths, weaknesses, speed, memory behavior, and the specific documents/pages where they add value over pymupdf4llm.

A clean `DoclingExtractor` class replaces the current basic wrapper with the best-discovered configuration, proper single-page support, and quality metadata in its output.

---

## Scope

### In Scope

- **Docling API exploration**: Investigate `PdfPipelineOptions` parameters beyond the current fixed set — OCR mode, table model options, image handling, acceleration options, chunk/page-level control
- **GMFT API exploration**: Investigate `AutoTableDetector` and `AutoTableFormatter` parameters — `enable_multi_header`, `semantic_spanning_cells`, confidence thresholds, output formats
- **Performance characterization**: Speed and memory behavior across document sizes for both Docling and GMFT. Crash/timeout behavior. Single-page vs full-document extraction.
- **Table quality head-to-head**: For every document with table content (aries_cost_account, araiinejad_2024, paischer_2025, helios_design, sparc_overview, energy_amplifier, hsu_2020), compare table output from pymupdf4llm, Docling, and GMFT
- **OCR mode testing**: Run Docling with `do_ocr=True` on schulte_1978 and evaluate improvement
- **Math handling assessment**: Evaluate how Docling handles equation-heavy pages vs pymupdf4llm baseline
- **MCP server vs library**: Document tradeoffs for interactive (MCP via pdf-analysis skill) vs programmatic (library) use
- **Experiment harness extension**: Extend the existing `tests/corpus/experiment.py` harness to support Docling and GMFT extraction (not just pymupdf4llm)
- **DoclingExtractor class**: Rebuild `docling_backend.py` with best-discovered config, single-page support, structured output, graceful degradation
- **GMFT wrapper**: Build a clean `GMFTExtractor` class for targeted table re-extraction
- **Findings report**: `.project/active/docling-deep-dive/findings.md` — living document updated after each experiment

### Out of Scope

- Pipeline assembly or quality gate heuristics (Stage 3)
- Postprocessing or merge logic (Stage 3)
- Pandoc investigation (Stage 1B — separate spec)
- Claude vision investigation (Stage 2)
- Changes to the pymupdf4llm backend (Stage 1A Phase 3 — separate work)
- Equation-specific tools (UniMERNet, Surya, Nougat — Stage 2)
- MCP server setup automation (separate spec exists at `.project/active/pdf-skill-deployment/`)

### Edge Cases & Considerations

- Docling downloads ~500MB of model weights on first run — this is a one-time cost that must be accounted for in timing
- Docling can hang or OOM on large documents — the subprocess timeout pattern from the existing backend MUST be preserved
- GMFT uses PyPDFium2 as its PDF backend, not PyMuPDF — page numbering/rendering may differ slightly
- The 241-page energy_amplifier may be too large for Docling full-document extraction — single-page mode may be required
- woodruff_2026 and woodruff_2026b are duplicates (same MD5) — treat as 14 unique documents, not 15
- Some papers have no tables (hawker_2020, delene_2001, hansen_2025, seo_2024, tajima, schulte_1978, woodruff_2026/b) — Docling's value for these is primarily in heading detection and page artifact removal, not tables

---

## Requirements

### Functional Requirements

#### FR-1: Docling API Reference

Document the Docling v2.71.0 API surface relevant to extraction:

1. `PdfPipelineOptions` — all parameters, defaults, and what they control
2. `DocumentConverter` — format options, conversion modes
3. `DoclingDocument` — export methods (markdown, JSON, text), iteration over elements
4. OCR configuration — what backends are available, how to enable, performance implications
5. Table structure options — TableFormer configuration, accuracy/speed tradeoffs
6. Image/picture handling — extraction modes, format options

The API reference SHOULD be captured in `.project/active/docling-deep-dive/api-reference.md` (following the pattern from Stage 1A).

#### FR-2: GMFT API Reference

Document the GMFT v0.4.2 API surface:

1. `AutoTableDetector` — detection parameters, confidence thresholds
2. `AutoTableFormatter` — formatting options, `enable_multi_header`, `semantic_spanning_cells`
3. Output formats — DataFrame, CSV, Markdown, LaTeX, HTML
4. `PyPDFium2Document` — page-level access, rendering

#### FR-3: Experiment Harness Extension

Extend `tests/corpus/experiment.py` to support Docling and GMFT extraction alongside pymupdf4llm:

1. Add a `--backend` flag: `pymupdf4llm` (default), `docling`, `gmft`
2. Docling backend: run `DocumentConverter.convert()` and export to markdown
3. GMFT backend: detect and format tables per page, output as markdown
4. Both backends MUST compute the same metrics via existing `metrics.py`
5. Results saved to the same `tests/corpus/runs/{config_name}/` structure
6. Timeout protection for Docling (configurable, default 600s per document)
7. GMFT runs SHOULD be per-page with table-level output alongside full-document markdown

The harness MUST support comparing Docling/GMFT runs against the pymupdf4llm baseline using the existing `--compare` mechanism.

#### FR-4: Systematic Experimentation

Run experiments covering at minimum:

**Docling experiments:**

1. **Baseline Docling**: Current config (`do_table_structure=True, generate_picture_images=True, do_ocr=False`) against all 14 unique documents
2. **Docling OCR mode**: `do_ocr=True` — test on schulte_1978 plus 2-3 other documents to assess impact on born-digital PDFs
3. **Docling tables-only**: If Docling supports table-focused mode, test extraction of only table regions
4. **Docling single-page**: Extract individual pages from 3-5 documents and compare output to full-document extraction (especially for large documents)

**GMFT experiments:**

5. **GMFT baseline**: Default `AutoTableDetector` + `AutoTableFormatter` against all documents with tables
6. **GMFT multi-header**: `enable_multi_header=True` on table-heavy documents
7. **GMFT spanning cells**: `semantic_spanning_cells=True` on documents with known complex tables

**Head-to-head comparisons:**

8. **Table comparison**: For every page containing a table across the corpus, capture the table output from pymupdf4llm, Docling, and GMFT side by side. The findings report MUST include specific examples with the actual markdown output from each tool.
9. **Full-document comparison**: For 3-5 representative documents (one text-heavy, one table-heavy, one math-heavy, one OCR-quality, one large), compare full markdown output quality across all three tools.

Additional experiments MAY be added based on discoveries during investigation.

#### FR-5: Findings Report

A living document at `.project/active/docling-deep-dive/findings.md` containing:

1. **Docling API observations**: What parameters exist, which ones matter, which are irrelevant
2. **GMFT API observations**: Same
3. **Per-experiment results**: Configuration, metrics, quality observations, specific examples
4. **Head-to-head table analysis**: Side-by-side comparison of table output from all three tools with commentary on which handles each case best
5. **Performance data**: Extraction time per document for each tool, memory observations, crash/timeout incidents
6. **OCR assessment**: Does Docling OCR mode meaningfully improve schulte_1978? At what speed cost?
7. **Math assessment**: How does Docling handle equations compared to pymupdf4llm?
8. **Failure catalog**: Specific pages/documents where each tool fails, with the actual output showing the failure
9. **Recommendations**: When to use each tool, with evidence. Clear heuristics like "Use GMFT when X, use Docling when Y, use pymupdf4llm when Z"
10. **MCP vs library tradeoffs**: When interactive (MCP) use is appropriate vs programmatic (library) use

#### FR-6: DoclingExtractor Class

Rebuild `src/agentic_mbse/extraction/docling_backend.py` with:

1. Best-discovered `PdfPipelineOptions` configuration (documented with rationale)
2. Single-page extraction support (extract a specific page, not the whole document)
3. Full-document extraction with timeout protection (preserved from existing code)
4. Structured `ExtractionResult` output with quality metadata (table count, image count, OCR confidence if available)
5. Graceful degradation when Docling is not installed (`ImportError` → clear error message)
6. Code comments documenting why each configuration value was chosen, referencing findings

#### FR-7: GMFTExtractor Class

Build a new `src/agentic_mbse/extraction/gmft_backend.py` with:

1. Table detection and formatting using best-discovered GMFT configuration
2. Page-level extraction (detect and format all tables on a given page)
3. Output as markdown pipe tables and/or DataFrames
4. Graceful degradation when GMFT is not installed
5. Performance suitable for use as a targeted enhancement (fast enough to run on flagged pages, not full documents)

### Non-Functional Requirements

- **Reproducibility**: Each experiment run MUST be reproducible from the saved `config.json`
- **Incremental**: Results accumulate — earlier findings are not lost when running new experiments
- **Evidence-based**: Every recommendation in the findings report MUST reference specific experiment results and specific document examples
- **Timeout safety**: Docling extraction MUST run in a subprocess with configurable timeout (existing pattern preserved)
- **Optional dependencies**: Both Docling and GMFT MUST remain optional — the extraction package works without them, just with reduced capability

---

## Acceptance Criteria

### Core Functionality

- [ ] Docling API reference document captures all relevant `PdfPipelineOptions` and conversion parameters
- [ ] GMFT API reference captures detection and formatting parameters
- [ ] Experiment harness supports `--backend docling` and `--backend gmft`
- [ ] At least 4 Docling configurations tested and documented
- [ ] At least 3 GMFT configurations tested and documented
- [ ] Head-to-head table comparison covers all 7 table-bearing documents in the corpus
- [ ] Findings report includes specific markdown output examples (not just metrics)
- [ ] OCR mode tested on schulte_1978 with quality assessment
- [ ] Performance data (seconds per document) captured for all three tools
- [ ] Final recommendations backed by comparative evidence
- [ ] `DoclingExtractor` class has single-page support and best-discovered config
- [ ] `GMFTExtractor` class provides page-level table extraction

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] Both new extractor classes have unit tests (mocked, following existing test patterns in `test_extraction.py`)
- [ ] Graceful degradation tested for both tools when not installed
- [ ] Timeout/crash protection tested for Docling

---

## Related Artifacts

- **Development strategy**: `.project/concepts/doc-extraction-development-strategy.md` (Stage 1C, lines 94-132)
- **pymupdf4llm findings**: `.project/active/pymupdf4llm-deep-dive/findings.md` (establishes baseline and identifies gaps)
- **pymupdf4llm spec**: `.project/active/pymupdf4llm-deep-dive/spec.md` (format template)
- **Existing Docling backend**: `src/agentic_mbse/extraction/docling_backend.py` (136 lines, to be rebuilt)
- **Existing tests**: `tests/test_extraction.py` (lines 353-431, Docling tests)
- **Experiment harness**: `tests/corpus/experiment.py` (to be extended)
- **Test corpus**: `tests/corpus/papers.jsonl` (14 unique documents)
- **Extraction research**: `.project/research/20260206_scientific-pdf-extraction.md` (tool landscape, benchmarks)
- **Docling setup script**: `scripts/setup-docling.sh` (MCP server configuration)
- **pdf-analysis skill**: `claude/skills/pdf-analysis/SKILL.md` (interactive extraction using Docling MCP)

---

**Next Steps:** After approval, proceed to `/_my_design` (harness extension design, experiment plan) then implementation.

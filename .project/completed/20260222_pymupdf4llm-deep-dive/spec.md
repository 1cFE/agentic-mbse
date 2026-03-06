# Spec: pymupdf4llm Deep-Dive (Stage 1A)

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-02-22 11:23 PST
**Complexity:** MEDIUM
**Branch:** `doc-ingest-clean`

---

## Business Goals

### Why This Matters

The old `doc-ingest` branch built 560 lines of regex postprocessing without deeply understanding pymupdf4llm's API. A single parameter discovery (`table_strategy="lines_strict"`) eliminated 252 `<br>` artifacts. There are likely more parameter wins in the API that would reduce or eliminate downstream complexity.

This is Stage 1A of the [development strategy](../../concepts/doc-extraction-development-strategy.md). Everything downstream — quality gates, Docling enhancement, pipeline assembly — depends on knowing what pymupdf4llm can and can't do well on its own.

### Success Criteria

- [ ] Comprehensive findings report documenting every configuration tested, observations, and reasoning
- [ ] Clear understanding of which parameters matter and which don't for our corpus
- [ ] A recommended "best config" backed by evidence from multiple iterations
- [ ] Expanded test corpus (15 PDFs) exercising diverse document types

### Priority

Foundation work. Blocks all subsequent stages.

---

## Problem Statement

### Current State

The existing `pymupdf_backend.py` uses this configuration:

```python
chunks = to_markdown(
    str(input_path),
    write_images=True,
    image_path=str(images_dir),
    image_format="png",
    dpi=150,
    page_chunks=True,
    hdr_info=_academic_header_detector,
    table_strategy="lines",
)
```

This was carried forward from earlier work without systematic evaluation. Notably:
- Uses `table_strategy="lines"` (not `"lines_strict"` which the old branch found superior)
- Custom `_academic_header_detector` may duplicate or conflict with pymupdf4llm's built-in detection
- Parameters like `margins`, `force_text`, `image_size_limit` are unexplored
- No documented evidence for why current values were chosen

### Desired Outcome

A **findings report** and **test harness** that systematically evaluates pymupdf4llm parameter configurations against a 15-document corpus. The report is the primary deliverable — it captures institutional knowledge that prevents future developers from re-discovering the same things.

---

## Scope

### In Scope

- **Test corpus expansion**: Download 7 new PDFs from Zotero (1cfe group) and add to `tests/corpus/`
- **Parameter experimentation harness**: Script/notebook that runs pymupdf4llm with varied configs and captures metrics
- **Iterative experimentation**: Run many configurations, inspect output quality, record observations after each run
- **Findings report**: Living document updated after each experiment iteration
- **Baseline comparison**: Use existing `tests/corpus/metrics.py` and `compare.py` infrastructure to measure impact
- **Refined `PyMuPDFExtractor`**: Update the existing backend with the best-discovered configuration

### Out of Scope

- Docling investigation (Stage 1B)
- Pandoc investigation (Stage 1C)
- Postprocessing / regex cleanup — we want to understand raw API output first
- Pipeline assembly (Stage 3)
- New quality gates or heuristics

### Edge Cases & Considerations

- Some parameters may interact (e.g., `hdr_info` + font-based detection)
- Very large documents (energy_amplifier: 241pp, schulte_1978: ~300pp trimmed to 10pp) may behave differently
- Scanned vs. born-digital PDFs may respond differently to same parameters
- pymupdf4llm v0.2.9 API may have changed since old branch experiments

---

## Requirements

### Functional Requirements

#### FR-1: Test Corpus Expansion

Download these 7 PDFs from Zotero group 5428393 and add to `tests/corpus/pdfs/`:

| Zotero ID | First Author | Year | Title (short) | Why included |
|-----------|-------------|------|---------------|--------------|
| IH9ZSRF8 | Araiinejad | 2024 | Techno-Economic Analysis of DT Magnetic Confinement Fusion | TEA content |
| LL7Q6PSU | Paischer | 2025 | GyroSwin: 5D Surrogates for Gyrokinetic Plasma Turbulence | ML/physics mix |
| 3IPQSG8C | Hansen | 2025 | Exploring the Physics of the Plasma Liner Experiment (FLASH/OSIRIS) | Multi-dimensional study |
| AMPD8BWX | Seo | 2024 | Avoiding fusion plasma tearing instability with deep RL | Short, figure-heavy |
| 2H5CJVB8 | Woodruff | 2026 | A costing framework for fusion power plants | Tables + equations |
| BXDIV83P | Tajima | N/A | Conversion of High-Energy Photons into Electricity | Older formatting |
| UQMRDJ6D | Schulte | 1978 | Fusion Reactor Design Studies — Standard Accounts for Cost Estimates | **Trim to 10 pages** |

Each PDF MUST be registered in `papers.jsonl` with slug, source, page count, and characteristics.

The UQMRDJ6D document MUST be manually trimmed to 10 pages before inclusion (it's a large reference document; we want a representative sample, not the full thing).

#### FR-2: Experimentation Harness

Build a script or notebook that:

1. Takes a parameter configuration dict as input
2. Runs `pymupdf4llm.to_markdown()` with those parameters against all corpus PDFs
3. Computes metrics using existing `tests/corpus/metrics.py`
4. Saves results to a timestamped output directory
5. Supports running the current baseline config as the reference point

The harness SHOULD reuse the existing `metrics.py` and `compare.py` infrastructure rather than building new metrics.

#### FR-3: Iterative Configuration Testing

The workflow MUST support running many iterations:

1. Define a configuration variant (change one or more parameters)
2. Run the harness against the corpus
3. Inspect output quality — both metrics AND manual review of markdown output
4. Record observations in the findings report
5. Repeat with next variant

Parameters to investigate (from the development strategy):

| Parameter | Current Value | Investigate |
|-----------|--------------|-------------|
| `table_strategy` | `"lines"` | `"lines_strict"`, `"text"`, omit |
| `hdr_info` | custom callback | `None` (built-in), custom, different thresholds |
| `dpi` | 150 | 72, 100, 200, 300 |
| `write_images` | True | False (speed impact?) |
| `margins` | default | Various margin tuples |
| `force_text` | default | True/False |
| `page_chunks` | True | False (single output) |
| `image_size_limit` | default | Various limits |

This list is NOT exhaustive — the pymupdf4llm API SHOULD be explored for additional parameters not listed here.

#### FR-4: Findings Report

A living document updated after each experiment, containing:

1. **Configuration log**: Every config tested, with timestamp and rationale
2. **Per-config observations**: What changed? What improved? What broke?
3. **Comparative metrics**: Side-by-side numbers across configurations
4. **Manual quality notes**: Observations from reading the actual markdown output (not just metrics)
5. **Cumulative conclusions**: What we've learned so far, updated as experiments progress
6. **Final recommendation**: The best configuration and why, with evidence

The report MUST be in `.project/active/pymupdf4llm-deep-dive/findings.md`.

The report is as important as the code. It captures institutional knowledge.

#### FR-5: [INFERRED] Updated PyMuPDFExtractor

After experimentation concludes, update `src/agentic_mbse/extraction/pymupdf_backend.py` with:
- The best-discovered parameter configuration
- Code comments documenting why each parameter value was chosen, referencing findings
- Updated baseline metrics in `tests/corpus/baseline/`

---

### Non-Functional Requirements

- **Reproducibility**: Each experiment run SHOULD be reproducible from the configuration log
- **Incremental**: Results accumulate — we don't lose earlier findings when running new experiments
- **Low ceremony**: The harness should be lightweight. A Python script is fine; no need for a framework.

---

## Acceptance Criteria

### Core Functionality

- [ ] 7 new PDFs downloaded from Zotero and added to `tests/corpus/pdfs/` with `papers.jsonl` entries
- [ ] UQMRDJ6D trimmed to 10 pages
- [ ] Experimentation harness runs a given config against all 15 corpus PDFs and produces metrics
- [ ] At least 5 distinct parameter configurations tested and documented
- [ ] Findings report captures observations, metrics, and reasoning for each configuration
- [ ] Final "best config" recommendation backed by comparative evidence

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] Baseline metrics updated for expanded corpus
- [ ] `pymupdf_backend.py` updated with best config + documented rationale

---

## Related Artifacts

- **Concept**: `.project/concepts/doc-extraction-development-strategy.md` (Stage 1A, lines 54-73)
- **Existing backend**: `src/agentic_mbse/extraction/pymupdf_backend.py`
- **Metrics tooling**: `tests/corpus/metrics.py`, `tests/corpus/compare.py`
- **Test corpus**: `tests/corpus/pdfs/`, `tests/corpus/papers.jsonl`
- **Zotero download**: `/home/reid/1cfe/fusion-tea/scripts/zotero_group_download.py`
- **Findings report**: `.project/active/pymupdf4llm-deep-dive/findings.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` (lightweight — mostly harness design) then implementation.

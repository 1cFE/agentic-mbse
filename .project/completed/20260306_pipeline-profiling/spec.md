# Spec: Pipeline Profiling & Route Instrumentation

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-03-01 15:33 PST
**Complexity:** MEDIUM
**Branch:** doc-ingest-clean

---

## Business Goals

### Why This Matters

The v4 pipeline has ~8 steps with complex per-page routing (KEEP, CLAUDE_REPLACE, GMFT_REPLACE, GMFT_APPEND, STRIP_FALSE, STRIP_BROKEN), but there's zero visibility into where wall-clock time goes or whether routing decisions match expectations across document types. Claude enhancement is expected to dominate runtime, but that's an assumption — table detection, quality gate evaluation, or postprocessing could have surprising costs on certain document types.

Before investing in performance optimization (parallelism, caching, selective skipping), the pipeline needs measurement infrastructure. Without it, optimization work is guesswork.

### Success Criteria

- [x] Per-step timing captured for each of the ~8 pipeline steps, per document
- [x] Route distribution summarized per document (count of each `PageAction`)
- [x] Summary table produced for a curated corpus covering clean, scanned, 2-column, table-heavy, equation-heavy, short, and long documents
- [x] Results identify which steps dominate wall-clock time
- [x] `--profile` flag works on any extraction run (single file, directory, or corpus), not just the curated set
- [x] Profiling adds negligible overhead when disabled (< 1ms total)

### Priority

P1 — Item 3 in EPIC-PDFV4-002. Depends on Item 2 (unified image output) so the profile reflects the final pipeline shape. Does not block any other items.

---

## Problem Statement

### Current State

The pipeline tracks only one timing metric: total `elapsed_seconds` on `PipelineResult`. There is no breakdown of time spent in individual steps (base extraction, table detection, table filter/enhance, quality gate, GMFT cross-reference, budget allocation, Claude enhancement, route+merge, postprocess). There is also no aggregated view of routing decisions across a document set — you can read `decisions.json` per document but there's no summary.

The existing `--check` flag runs component *probes* (individual tool tests) against a small check corpus, but does not run the full pipeline or measure timing. It answers "are components installed?" not "how does the pipeline perform?"

### Desired Outcome

Two things:

1. **`--profile` flag**: Any `agentic-mbse extract` run can produce a `PipelineProfile` alongside the normal output. The profile captures per-step wall-clock durations and is saved as `profile.json` in the output directory. When extracting multiple documents, a summary table is printed to stderr showing timing breakdown and route distribution per document.

2. **Curated profile corpus**: A dedicated set of ~10 diverse PDFs in `profile_corpus/` that can be run with `--profile` to produce a baseline performance report. This corpus is separate from `check_corpus/` (which exists for component probing, not full pipeline benchmarking).

---

## Scope

### In Scope

- `PipelineProfile` dataclass with per-step timing (separate from `PipelineResult`)
- `time.perf_counter()` instrumentation around each pipeline step in `extract_pdf()`
- `--profile` CLI flag that enables profiling on any extraction run
- `profile.json` output alongside `output.md` when profiling is enabled
- Route distribution summary (aggregate `PageDecision.action` counts per document)
- Summary table printed to stderr when profiling multiple documents
- Curated `profile_corpus/` directory with ~10 diverse PDFs
- `agentic-mbse extract profile_corpus/ --profile` as the canonical profiling invocation
- Unit tests for timing instrumentation

### Out of Scope

- Performance optimization (this measures; optimization is future work)
- Memory profiling
- Parallel/async pipeline execution
- Changes to pipeline routing or quality gate logic
- Modifications to `--check` behavior
- Integration with CI/CD (automated regression detection on timing)

### Edge Cases & Considerations

- **arXiv shortcut early return**: When the pipeline takes the Pandoc/arXiv shortcut, only Step 1 has meaningful timing. The profile MUST still be valid (other steps show 0.0s).
- **Error early return**: When `extract_pages()` fails, the pipeline returns early with an error. The profile SHOULD still capture what ran (Step 2 duration includes the failure).
- **Dry run mode**: `--dry-run --profile` SHOULD work — timing captures everything up to Claude enhancement (which is skipped), showing the "cost of assessment" without enhancement.
- **Zero-cost steps**: Some steps (budget allocation, route+merge) are pure computation and will show ~0ms. This is correct — the profile should not hide fast steps.
- **Profiling overhead when disabled**: When `--profile` is not set, the pipeline MUST NOT wrap steps in timers. No `time.perf_counter()` calls in the default path.

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED].

1. **FR-1**: A `PipelineProfile` dataclass MUST capture per-step wall-clock durations for each pipeline step. Steps: `arxiv_shortcut`, `base_extraction`, `table_detection`, `table_filter_enhance`, `quality_gate`, `gmft_xref`, `budget_allocation`, `claude_enhancement`, `route_merge`, `postprocess`.

2. **FR-2**: `PipelineProfile` MUST be a separate dataclass from `PipelineResult`. It SHOULD be returned via an optional field on `PipelineResult` (e.g., `profile: PipelineProfile | None`, default `None`).

3. **FR-3**: `extract_pdf()` MUST accept a `profile` parameter (boolean or config) that enables timing instrumentation. When disabled (default), no timing calls occur.

4. **FR-4**: The `--profile` CLI flag MUST enable profiling for any extraction run — single file, directory, or corpus.

5. **FR-5**: When profiling is enabled, a `profile.json` file MUST be written alongside `output.md` in each document's output directory. It MUST contain per-step durations in seconds and the route distribution.

6. **FR-6**: Route distribution MUST be computed from `PipelineResult.decisions` as a count of each `PageAction` value (e.g., `{"keep": 8, "claude_replace": 3, "gmft_replace": 1}`).

7. **FR-7**: When profiling a multi-document run, a summary table MUST be printed to stderr showing per-document timing breakdown and route distribution. Format per the epic:

   ```
   Document                  Pages  KEEP  CLAUDE  GMFT  Time(s)  Base  Tables  Gate  Claude  Post
   ────────────────────────  ─────  ────  ──────  ────  ───────  ────  ──────  ────  ──────  ────
   araiinejad_2024 (clean)      12     3       6     3    14.2   1.1     2.3   0.1     9.8   0.2
   ```

8. **FR-8**: A curated `profile_corpus/` directory MUST contain ~10 diverse PDFs. The corpus MUST cover: clean born-digital, two-column academic, scanned/degraded, table-heavy, equation-heavy, short (2-5pp), and long (30+pp) document types.

9. **FR-9**: [INFERRED] `PipelineConfig` MUST have a `profile: bool = False` field to thread the profiling flag through to `extract_pdf()`.

10. **FR-10**: [INFERRED] `profile.json` MUST include the route distribution alongside per-step timing, so a single file captures the complete profile for a document.

### Non-Functional Requirements

- Profiling MUST add negligible overhead when disabled (no timing calls in default path, < 1ms total if any)
- No new external dependencies
- Existing tests MUST continue to pass
- Profile corpus PDFs SHOULD be small enough that a full profiling run completes in reasonable time (< 5 minutes with Claude enabled, < 30 seconds without)

---

## Acceptance Criteria

### Core Functionality

- [x] `PipelineProfile` captures timing for all ~10 pipeline steps
- [x] `PipelineProfile` is separate from `PipelineResult` and attached via optional field
- [x] `extract_pdf()` with `profile=False` (default) does not call `time.perf_counter()`
- [x] `extract_pdf()` with `profile=True` populates `result.profile` with per-step durations
- [x] Route distribution correctly counts each `PageAction` from decisions
- [x] arXiv shortcut early-return produces valid profile (other steps 0.0s)

### CLI Integration

- [x] `--profile` flag accepted on `agentic-mbse extract`
- [x] `profile.json` written per document when `--profile` is active
- [x] Summary table printed to stderr for multi-document profiling runs
- [x] `agentic-mbse extract profile_corpus/ --profile` works end-to-end

### Corpus

- [x] `profile_corpus/` contains ~10 diverse PDFs covering specified document types
- [x] Corpus is separate from `check_corpus/`
- [x] Corpus PDFs are committed to the repo (or documented acquisition instructions if too large)

### Quality & Integration

- [x] Existing tests continue to pass
- [x] Pipeline without `--profile` produces identical output to current behavior
- [x] Unit tests verify timing instrumentation with mocked pipeline steps
- [x] No new external dependencies added

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pdf-extraction-improvements.md` (EPIC-PDFV4-002, Item 3)
- **Dependency:** `.project/active/unified-image-output/` (Item 2 — image pipeline should be in place)
- **Reference:** `src/agentic_mbse/extraction/check.py` — existing `--check` corpus/probe pattern
- **Key source files:**
  - `src/agentic_mbse/extraction/pipeline.py:275-566` — `extract_pdf()` with step comments
  - `src/agentic_mbse/extraction/types.py` — `PipelineResult`, `PageDecision`, `PageAction`
  - `src/agentic_mbse/cli/extract_cli.py:192-451` — `cmd_extract()`, CLI flag registration
  - `src/agentic_mbse/extraction/check.py:115-120` — `get_check_corpus()` pattern to follow

---

**Next Steps:** After approval, proceed to `/_my_design`

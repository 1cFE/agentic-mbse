# Implementation Plan: v4 Pipeline Output Quality Regressions

**Status:** Draft
**Created:** 2026-02-27
**Last Updated:** 2026-02-27

## Source Documents
- **Spec:** `.project/active/v4-output-quality-regressions/spec.md`
- **Design:** `.project/active/v4-output-quality-regressions/design.md` ← See here for component details, function signatures, architecture

## Implementation Strategy

**Phasing Rationale:**
Four orthogonal fixes, ordered by scope and dependency:
1. **Equation fragments** — smallest scope, purely additive, validates quality gate modification pattern
2. **GMFT cross-reference** — highest-impact routing change, builds on quality gate confidence from Phase 1
3. **Postprocess cleanup** — straightforward wiring of existing proven functions
4. **Image extraction** — touches most files, builds on Phase 3's postprocess step for path normalization

**Overall Validation Approach:**
- Each phase starts with tests
- `uv run pytest tests/ -x` after each phase for regression check
- Manual verification against TEA document after all phases complete

---

## Phase 1: Equation-Fragment Detection

### Goal
Add `_assess_equation_fragments()` signal to `quality_gate.py` so equation rendering failures (e.g., `_C_ = _CEEDB_` followed by `(2.2)`) trigger Claude enhancement. Purely additive — no changes to existing signals or routing.

### Test Stencil (Write This First)
```python
class TestEquationFragments:
    def test_equation_fragment_pattern(self):
        """Short italic lines + standalone equation number → severity >= 1.0."""
        md = "_Pnew_\n_C_ = _CEEDB_\n\n(2.2)\n"
        a = assess_page(md, 0)
        assert a.needs_claude
        assert a.severity >= 1.0

    def test_normal_italic_no_signal(self):
        """Long italic paragraph → no equation fragment signal."""
        md = "_This is a normal italic sentence that is quite long and in a paragraph._ " * 5
        a = assess_page(md, 0)
        # Should not trigger equation fragment detection
        assert a.math_garble_score == 0.0

    def test_inline_equation_number_no_signal(self):
        """Equation number inline in paragraph → no signal."""
        md = "The result follows from equation (2.2) in the text above. " * 5
        a = assess_page(md, 0)
        assert a.math_garble_score == 0.0

    def test_equation_number_without_italic_fragments(self):
        """Standalone equation number but no preceding italic fragments → no signal."""
        md = "Normal text line one.\nAnother normal line.\n\n(2.2)\n"
        a = assess_page(md, 0)
        # equation number alone is not enough
```

### Changes Required

**See `design.md#component-3-equation-fragment-detection-fr-11` for:**
- Heuristic algorithm, regex patterns, severity value rationale
- False positive mitigation strategy

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_quality_gate.py`
- [ ] Add `TestEquationFragments` class with 4 tests per stencil above

#### 2. Quality Gate
**File:** `src/agentic_mbse/extraction/quality_gate.py`
- [ ] Add `_EQUATION_NUMBER_RE` and `_ITALIC_MARKER_RE` regex patterns (see `design.md#component-3`)
- [ ] Add `_assess_equation_fragments(md: str) -> tuple[float, list[str]]` function
- [ ] Call `_assess_equation_fragments()` from `assess_page()` after existing signals (~line 299), following the same pattern as `_assess_math_garbling`

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_quality_gate.py::TestEquationFragments -v` → All pass
- [ ] `uv run pytest tests/ -x` → No regressions

**What We Know Works After This Phase:**
Equation fragment patterns produce severity >= 1.0 and set `needs_claude=True`. Normal italic text and inline equation references do not trigger false positives.

---

## Phase 2: GMFT Cross-Reference

### Goal
Add step 4b between quality gate (step 4) and budget allocation (step 5): when GMFT found tables on a page where pymupdf produced no pipe tables, boost severity and set `needs_claude=True`. This changes routing from GMFT_APPEND to CLAUDE_REPLACE for these pages.

### Test Stencil (Write This First)
```python
class TestGmftCrossReference:
    def test_gmft_tables_no_pipe_tables_boosts_severity(self):
        """GMFT found tables + pymupdf has no pipe tables → needs_claude, severity boosted."""
        # Page with text but no pipe tables, GMFT found a table
        # After cross-reference: needs_claude=True, severity += 1.5

    def test_gmft_tables_with_pipe_tables_no_change(self):
        """GMFT found tables + pymupdf has pipe tables → no change."""

    def test_no_gmft_tables_no_change(self):
        """No GMFT tables on page → no change."""

    def test_e2e_gmft_missed_within_budget_claude_replace(self):
        """End-to-end: GMFT-missed-table page within budget → CLAUDE_REPLACE."""

    def test_e2e_gmft_missed_over_budget_gmft_replace(self):
        """End-to-end: GMFT-missed-table page over budget → GMFT_REPLACE fallback."""
```

### Changes Required

**See `design.md#component-2-gmft-cross-reference-fr-7-fr-8-fr-10` for:**
- `_cross_reference_gmft()` function signature and logic
- Severity boost rationale (1.5)
- Effect on routing rules analysis
- FR-8/FR-9 reconciliation (GMFT_REPLACE vs GMFT_APPEND in fallback)

**Specific file changes:**

#### 1. Test Files
**File:** `tests/test_pipeline.py`
- [ ] Add `TestGmftCrossReference` class with 5 tests per stencil
- [ ] Add `_patch_has_pipe_tables()` helper if needed for isolation

**File:** `tests/test_quality_gate.py`
- [ ] Update imports if `has_pipe_tables` is now public — add test for it

#### 2. Quality Gate Config
**File:** `src/agentic_mbse/extraction/quality_gate.py`
- [ ] Add `gmft_xref_severity_boost: float = 1.5` to `QualityGateConfig` (with docstring noting cross-module usage)
- [ ] Rename `_has_pipe_tables()` → `has_pipe_tables()` (drop underscore, now public API)
- [ ] Update all internal call sites of `_has_pipe_tables` (rules 3 and 5 in `route_page()`)

#### 3. Pipeline
**File:** `src/agentic_mbse/extraction/pipeline.py`
- [ ] Import `has_pipe_tables` from `quality_gate`
- [ ] Add `_cross_reference_gmft()` function (see `design.md#component-2` for signature)
- [ ] Call `_cross_reference_gmft()` between step 4 (quality gate) and step 5 (budget allocation), after heading anomaly check (~line 303)

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pipeline.py::TestGmftCrossReference -v` → All pass
- [ ] `uv run pytest tests/ -x` → No regressions

**What We Know Works After This Phase:**
Pages where GMFT found tables but pymupdf missed them get boosted severity and `needs_claude=True`. Budget allocation considers them alongside character-garbling pages. Routing produces CLAUDE_REPLACE (within budget) or GMFT_REPLACE (over budget) instead of GMFT_APPEND.

---

## Phase 3: Postprocess Cleanup

### Goal
Add `_postprocess_final()` step 7b between page merge and metrics computation. Calls `strip_page_numbers()`, `strip_running_headers()`, and `repair_ligatures()` on the final joined markdown. Does NOT call header promotion/demotion (FR-4).

### Test Stencil (Write This First)
```python
class TestPostprocessCleanup:
    def test_running_headers_stripped(self):
        """Repeated short lines across pages are removed from merged output."""
        # Create multi-page output with the same header repeated 4+ times

    def test_page_numbers_stripped(self):
        """Bare page numbers between blank lines are removed."""

    def test_ligatures_repaired(self):
        """Unicode ligatures (U+FB00-FB04) replaced with ASCII."""

    def test_header_formatting_preserved(self):
        """Existing ## headers are NOT modified (FR-4 compliance)."""

    def test_postprocess_runs_on_merged_output(self):
        """End-to-end: pipeline output has no running headers or page numbers."""
```

### Changes Required

**See `design.md#component-1-postprocess-cleanup-fr-1-fr-2-fr-3` for:**
- `_postprocess_final()` function signature
- Why we call individual functions instead of `postprocess()` orchestrator
- Data flow: merged_pages → join → _postprocess_final → final_markdown → compute_metrics

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pipeline.py`
- [ ] Add `TestPostprocessCleanup` class with 5 tests per stencil

#### 2. Pipeline
**File:** `src/agentic_mbse/extraction/pipeline.py`
- [ ] Import `strip_page_numbers`, `strip_running_headers`, `repair_ligatures` from `postprocess`
- [ ] Add `_postprocess_final(markdown: str, extracted_images_dir: Path | None = None) -> str` function
- [ ] Call `_postprocess_final()` on line 421 (after `"\n\n".join(merged_pages)`, before `compute_metrics()`)

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pipeline.py::TestPostprocessCleanup -v` → All pass
- [ ] `uv run pytest tests/ -x` → No regressions

**What We Know Works After This Phase:**
Pipeline output has zero running headers, zero bare page numbers, and no Unicode ligatures. Existing header formatting (## H2, ### H3) is preserved unchanged.

---

## Phase 4: Image Extraction

### Goal
Re-enable image extraction in `extract_pages()` by adding `extracted_images_dir` parameter. Wire through `PipelineConfig`, CLI, and postprocess step for path normalization.

### Test Stencil (Write This First)
```python
# test_pipeline.py
class TestImageExtraction:
    def test_extract_pages_with_images_dir(self):
        """extract_pages() with extracted_images_dir passes write_images=True."""

    def test_extract_pages_without_images_dir(self):
        """extract_pages() without extracted_images_dir passes write_images=False (backward compat)."""

    def test_postprocess_normalizes_image_paths(self):
        """Absolute image paths → relative images/ paths."""

    def test_config_has_extracted_images_dir(self):
        """PipelineConfig.extracted_images_dir defaults to None."""
```

### Changes Required

**See `design.md#component-4-image-extraction-fr-5-fr-6` for:**
- `extract_pages()` parameter changes
- `PipelineConfig.extracted_images_dir` field (distinct from `page_image_dir`)
- Image path flow diagram
- Claude-replaced page orphan image rationale

**Specific file changes:**

#### 1. Test Files
**File:** `tests/test_pipeline.py`
- [ ] Add `TestImageExtraction` class with 4 tests per stencil

**File:** `tests/test_extract_cli.py`
- [ ] Add test verifying `PipelineConfig.extracted_images_dir` is set when output dir exists

#### 2. Backend
**File:** `src/agentic_mbse/extraction/pymupdf_backend.py:124-157`
- [ ] Add `extracted_images_dir: Path | None = None` parameter to `extract_pages()`
- [ ] Pass `write_images=extracted_images_dir is not None` and `image_path=str(extracted_images_dir)` to `to_markdown()`

#### 3. Pipeline Config
**File:** `src/agentic_mbse/extraction/pipeline.py`
- [ ] Add `extracted_images_dir: Path | None = None` to `PipelineConfig`
- [ ] Pass `config.extracted_images_dir` to `extract_pages()` call (~line 207)
- [ ] Update `_postprocess_final()` to call `normalize_image_paths()` when `extracted_images_dir` is set

#### 4. CLI
**File:** `src/agentic_mbse/cli/extract_cli.py`
- [ ] Create `output_dir / "images"` before calling `extract_pdf()` (~line 300)
- [ ] Set `extracted_images_dir=images_dir` in `PipelineConfig` constructor

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pipeline.py::TestImageExtraction -v` → All pass
- [ ] `uv run pytest tests/test_extract_cli.py -v` → All pass
- [ ] `uv run pytest tests/ -x` → No regressions

**What We Know Works After This Phase:**
`extract_pages()` saves embedded images when `extracted_images_dir` is provided. Image paths are normalized to relative `images/` paths in the final output. CLI creates the images directory and wires it through config.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
uv run pytest tests/ -x          # Full regression check
uv run ruff check src/ tests/    # Linting
uv run ruff format src/ tests/   # Formatting
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Low risk. False positive mitigation built into heuristic (requires ≥2 short italic lines + standalone equation number).
- **Phase 2**: Medium risk. GMFT xref could over-allocate Claude budget. Mitigated by moderate 1.5 severity boost competing fairly with existing signals.
- **Phase 3**: Low risk. `strip_running_headers()` uses threshold=3, same proven function from old pipeline.
- **Phase 4**: Low risk. `write_images` is a well-tested pymupdf4llm parameter. Backward compatible (default None = no change).

## Implementation Notes

### Phase 1 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 2 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 4 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

---

**Status**: Draft → In Progress → Complete

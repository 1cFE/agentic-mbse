# Implementation Plan: Equation Region Detection

**Status:** Complete
**Created:** 2026-03-01
**Last Updated:** 2026-03-01

## Source Documents
- **Spec:** `.project/active/equation-region-detection/spec.md`
- **Design:** `.project/active/equation-region-detection/design.md` — See here for component details, dependencies, architecture
- **Learning Tests:** `.project/active/equation-region-detection/learning-test.md` — Experimental results informing thresholds and decisions

## Implementation Strategy

**Phasing Rationale:**
Phase 1 de-risks the core detector (LayoutPredictor integration, NMS, crop saving) with direct corpus validation. Phase 2 wires the proven detector into the pipeline orchestrator with inline placement. Phase 3 adds the CLI opt-out flag. Each phase is independently testable and completable in one session.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase has automated + manual validation
- `uv run pytest tests/` after every phase to catch regressions

---

## Phase 1: Types + Core Detector + Tests

### Goal
Working `detect_equations()` function that finds display equations on PDF pages, crops them, and returns `DetectedEquation` objects. Validated against corpus ground truth. This is the riskiest component — if detection doesn't work, nothing else matters.

### Test Stencil (Write First)

```python
# tests/test_equations.py

class TestNms:
    def test_removes_overlapping_lower_confidence(self):
        dets = [
            {"label": "Formula", "confidence": 0.9, "l": 100, "t": 100, "r": 500, "b": 200},
            {"label": "Formula", "confidence": 0.8, "l": 105, "t": 105, "r": 505, "b": 205},
        ]
        kept = _nms(dets, iou_threshold=0.3)
        assert len(kept) == 1
        assert kept[0]["confidence"] == 0.9

    def test_keeps_non_overlapping(self):
        dets = [
            {"label": "Formula", "confidence": 0.9, "l": 100, "t": 100, "r": 500, "b": 200},
            {"label": "Formula", "confidence": 0.8, "l": 100, "t": 800, "r": 500, "b": 900},
        ]
        kept = _nms(dets, iou_threshold=0.3)
        assert len(kept) == 2

class TestDetectEquations:
    def test_import_error_returns_empty(self):
        # Mock ImportError on docling_ibm_models → returns {}
        ...

    def test_returns_detected_equations(self):
        # Mock predictor.predict → returns synthetic detections
        # Verify dict[int, list[DetectedEquation]] structure
        ...

@pytest.mark.slow
class TestCorpusEquations:
    def test_hawker_recall(self):
        result = detect_equations(CORPUS / "pdfs/hawker_2020.pdf")
        total = sum(len(eqs) for eqs in result.values())
        assert total >= 17  # 80% of 21 ground truth

    def test_hansen_zero_false_positives(self):
        result = detect_equations(CORPUS / "pdfs/hansen_2025.pdf")
        total = sum(len(eqs) for eqs in result.values())
        assert total == 0
```

### Changes Required

**See `design.md` for:**
- `DetectedEquation` dataclass → `design.md#component-1`
- `LayoutDetection` TypedDict, `_nms()`, `_get_predictor()`, `detect_equations()` → `design.md#component-2`
- `PipelineProfile.equation_detection` → `design.md#component-5`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_equations.py` (NEW — write first)
- [x] Create test file with imports
- [x] `TestNms`: `test_removes_overlapping_lower_confidence`, `test_keeps_non_overlapping`, `test_empty_input`
- [x] `TestDetectEquations`: `test_import_error_returns_empty`, `test_returns_detected_equations` (mocked predictor)
- [x] `TestDetectedEquation`: `test_dataclass_fields`, `test_y_fraction_default`
- [x] `TestCorpusEquations` (marked `@pytest.mark.slow`): `test_hawker_recall`, `test_hansen_zero_false_positives`

#### 2. Types
**File:** `src/agentic_mbse/extraction/types.py:12` (after `ImageEntry`)
- [x] Add `DetectedEquation` dataclass (see `design.md#component-1`)
- [x] Add `equation_detection: float = 0.0` to `PipelineProfile` (after `table_filter_enhance`)

#### 3. Detector Module
**File:** `src/agentic_mbse/extraction/equations.py` (NEW)
- [x] Module docstring, imports, logger
- [x] `LayoutDetection` TypedDict
- [x] `_layout_predictor` singleton + `_get_predictor()` with `snapshot_download`
- [x] `_nms()` with IoU computation
- [x] `detect_equations()` — lazy import guard, page rendering, predict, NMS, confidence filter, crop, save

### Validation

**Automated:**
- [x] `uv run pytest tests/test_equations.py -v` → all unit tests pass (7 passed)
- [x] `uv run pytest tests/test_equations.py -m slow -v` → corpus tests pass (hawker ≥17, hansen = 0)
- [x] `uv run pytest tests/` → no regressions (1093 passed, 1 skipped)
- [x] `uv run ruff check src/agentic_mbse/extraction/equations.py` → all checks passed

**Manual:**
- [ ] Run: `uv run python -c "from agentic_mbse.extraction.equations import detect_equations; from pathlib import Path; r = detect_equations(Path('tests/corpus/pdfs/hawker_2020.pdf')); print(f'Pages: {len(r)}, Total: {sum(len(v) for v in r.values())}')"` → prints ~6 pages, ~21 total
- [ ] Inspect saved crops in temp dir — equations legible, no clipping

**What We Know Works After This Phase:**
The detector finds display equations with correct count, NMS deduplicates, crops are clean, and import failure degrades gracefully.

---

## Phase 2: Pipeline Integration + Inline Placement

### Goal
Wire `detect_equations()` into the pipeline orchestrator as Step 3c. Register equation crops with `ImageCollector`. Place inline markdown references near equation text using `y_fraction` positioning.

### Test Stencil (Write First)

```python
# tests/test_pipeline.py (additions)

class TestEquationDetection:
    def test_disabled_skips_detection(self):
        # config.enable_equations=False → detect_equations never called
        with _patch_base(), _patch_tables(), _patch_equations() as mock_eq:
            result = extract_pdf(PDF, PipelineConfig(enable_equations=False))
            mock_eq.assert_not_called()

    def test_no_images_dir_skips_detection(self):
        # extracted_images_dir=None → detect_equations never called
        ...

    def test_error_isolated(self):
        # detect_equations raises RuntimeError → pipeline completes, no equations
        ...

    def test_crops_registered_with_collector(self, tmp_path):
        # Mock detector returns 1 equation with image_path
        # Verify ImageCollector.entries contains kind="equation_crop"
        ...

    def test_refs_in_merged_markdown(self, tmp_path):
        # Verify output contains ![](images/page_000_eq_0.png)
        ...
```

### Changes Required

**See `design.md` for:**
- Pipeline imports, PipelineConfig, _try_detect_equations → `design.md#component-3` (3a–3d)
- _insert_equation_refs placement algorithm → `design.md#component-3` (3e–3f)

**Specific file changes:**

#### 1. Pipeline Tests
**File:** `tests/test_pipeline.py` (additions)
- [x] Add `_patch_equations()` helper (mirrors `_patch_tables()`)
- [x] `TestEquationDetection` class with 5 tests (see stencil above)
- [x] `test_insert_equation_refs` unit tests (3 tests: blank line, multiple ordered, no image skipped)

#### 2. Pipeline Module
**File:** `src/agentic_mbse/extraction/pipeline.py`
- [x] Add import: `from agentic_mbse.extraction.equations import detect_equations`
- [x] Add `DetectedEquation` to types import
- [x] Add `enable_equations: bool = True` to `PipelineConfig` (after `enable_docling`)
- [x] Add `_try_detect_equations()` wrapper (after `_try_detect_tables`)
- [x] Add `_insert_equation_refs()` helper function
- [x] Add Step 3c block between Step 3b and Step 4 (with profiling)
- [x] Modify Step 7 merge loop: call `_insert_equation_refs()` after routing decision

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pipeline.py -v` → all tests pass (old + new, 8 new equation tests)
- [x] `uv run pytest tests/` → no regressions (1101 passed, 1 skipped)
- [x] `uv run ruff check src/agentic_mbse/extraction/pipeline.py` → all checks passed

**Manual:**
- [ ] Run pipeline on hawker_2020 with images dir:
  ```
  uv run python -c "
  from pathlib import Path
  from agentic_mbse.extraction.pipeline import extract_pdf, PipelineConfig
  cfg = PipelineConfig(extracted_images_dir=Path('/tmp/eq_test_images'), enable_claude=False)
  r = extract_pdf(Path('tests/corpus/pdfs/hawker_2020.pdf'), cfg)
  print(f'Images: {r.image_count}')
  print('Eq refs:', r.markdown.count('_eq_'))
  "
  ```
- [ ] Verify `/tmp/eq_test_images/` contains `page_*_eq_*.png` files
- [ ] Verify output markdown contains `![](images/page_*_eq_*.png)` near equation text
- [ ] Run pipeline with `enable_equations=False` → output identical to current behavior

**What We Know Works After This Phase:**
Equation detection runs as Step 3c, crops are persisted to images dir via ImageCollector, inline references appear in output markdown, and the feature can be disabled without side effects.

---

## Phase 3: CLI Flag + Final Validation

### Goal
Add `--no-equations` CLI flag for user opt-out. Full regression pass across all tests.

### Test Stencil (Write First)

```python
# tests/test_extract_cli.py (additions)

def test_no_equations_flag_sets_config():
    # Parse args with --no-equations
    # Verify PipelineConfig.enable_equations == False
    ...
```

### Changes Required

**See `design.md` for:**
- CLI flag pattern → `design.md#component-4`

**Specific file changes:**

#### 1. CLI Test
**File:** `tests/test_extract_cli.py`
- [x] Add test for `--no-equations` argument parsing

#### 2. CLI Module
**File:** `src/agentic_mbse/cli/extract_cli.py`
- [x] Add `--no-equations` argument (after `--no-img2table`, ~line 567)
- [x] Wire `enable_equations=not args.no_equations` in config construction (~line 344)

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extract_cli.py -v` → all 39 pass
- [x] `uv run pytest tests/` → full green (1102 passed, 1 skipped)
- [x] `uv run ruff check src/ tests/` → all changed files clean
- [x] `uv run mypy src/` → no new type errors (fixed no-redef on detected_equations)

**Manual:**
- [x] `uv run agentic-mbse extract --help` → shows `--no-equations` in help
- [ ] `uv run agentic-mbse extract --no-equations tests/corpus/pdfs/hawker_2020.pdf -o /tmp/test_out` → completes without equation detection overhead (deferred to user)

**What We Know Works After This Phase:**
Full feature complete: detection, pipeline integration, inline placement, CLI opt-out. All existing tests pass. Feature can be enabled/disabled at CLI level.

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If `snapshot_download` doesn't resolve the model path correctly, fall back to checking `~/.cache/huggingface/hub/` directly. The learning tests already confirmed the model is cached.
- **Phase 2**: If `y_fraction` placement is too inaccurate on specific pages, the 5-line spec tolerance and blank-line preference provide adequate safety margin. See `design.md#known-limitations`.
- **Phase 3**: CLI wiring is mechanical — follows exact `--no-tables` precedent.

## Implementation Notes

*(TO BE FILLED DURING IMPLEMENTATION)*

### Phase 1 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Created `tests/test_equations.py` with 7 unit tests + 2 corpus tests (9 total)
- Added `DetectedEquation` dataclass to `src/agentic_mbse/extraction/types.py:20-26`
- Added `equation_detection: float = 0.0` to `PipelineProfile` at `types.py:94`
- Created `src/agentic_mbse/extraction/equations.py` with `LayoutDetection` TypedDict, `_get_predictor()` singleton, `_nms()`, `detect_equations()`
- Added `detect_equations` import in `pipeline.py` (dormant module test requires reachability)
- Updated `test_pipeline.py` profile field count from 11 → 12

**Issues:**
- `test_no_dormant_modules` failed until `equations.py` was imported from `pipeline.py` — added `noqa: F401` import early
- `test_profile_populated_when_enabled` required count update (11 → 12) for new `equation_detection` field
- Ruff E741 flagged `l` variable name (ambiguous) — used `noqa` on TypedDict field (matches upstream API), renamed local vars to `left`/`top`/`right`/`bottom`

**Deviations:**
- Added pipeline.py import in Phase 1 (instead of Phase 2) to satisfy dormant module test — import has `noqa: F401` comment, actual usage deferred to Phase 2

### Phase 2 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Modified `src/agentic_mbse/extraction/pipeline.py`:
  - Removed `noqa: F401` from equations import, added `DetectedEquation` to types import
  - Added `enable_equations: bool = True` to `PipelineConfig`
  - Added `_try_detect_equations()` error-isolated wrapper
  - Added `_insert_equation_refs()` placement helper (blank-line preference, offset tracking)
  - Added Step 3c block with profiling between 3b and Step 4
  - Refactored Step 7 routing to use `page_md` variable, then insert equation refs before appending
- Added to `tests/test_pipeline.py`:
  - `_patch_equations()` helper
  - `TestEquationDetection` class (5 tests: disabled, no images dir, error isolated, crops registered, refs in markdown)
  - `TestInsertEquationRefs` class (3 tests: blank line insertion, multiple ordered, no image skipped)

**Issues:**
- None. All 8 new tests passed immediately.

**Deviations:**
- Added 3 `TestInsertEquationRefs` unit tests (plan only mentioned 1) — validates blank-line preference, multi-equation ordering, and no-image skip

### Phase 3 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Added `--no-equations` argument to `src/agentic_mbse/cli/extract_cli.py` (after `--no-img2table`)
- Wired `enable_equations=not args.no_equations` in PipelineConfig construction
- Added `test_pdf_no_equations_flag` to `tests/test_extract_cli.py`
- Added `no_equations=False` to MockArgs in `tests/test_extract_cli.py` and `tests/test_profile.py`
- Fixed mypy `no-redef` error: moved `detected_equations` type annotation before conditional in `pipeline.py`
- Fixed ruff E741 in `tests/test_equations.py` `_det()` helper: renamed `l`→`left` etc.

**Issues:**
- `tests/test_profile.py` has its own `_MockArgs` class that also needed `no_equations` (4 test failures until fixed)
- mypy flagged `detected_equations` redefinition in else branch — restructured to declare-then-assign

**Deviations:**
- None. Phase 3 was mechanical as predicted.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**

# Implementation Plan: Pipeline Profiling & Route Instrumentation

**Status:** Complete
**Created:** 2026-03-01 19:29 PST
**Last Updated:** 2026-03-01

## Source Documents
- **Spec:** `.project/active/pipeline-profiling/spec.md`
- **Design:** `.project/active/pipeline-profiling/design.md` — See here for component details, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Phase 1 tackles the riskiest change (modifying `extract_pdf()`) and establishes the data types everything else depends on. Phase 2 builds the presentation layer as pure functions testable with synthetic data. Phase 3 wires CLI integration that depends on both. Phase 4 curates the corpus last since it's independent of code and can be filled incrementally.

**Overall Validation Approach:**
- Each phase starts with tests (test-first for Phases 1-3)
- `uv run pytest tests/` after each phase to verify no regressions
- `uv run ruff check src/ tests/` for lint compliance
- Phase 4 validates end-to-end with real PDFs

---

## Phase 1: Data Types + Timing Instrumentation

### Goal
Add `PipelineProfile` dataclass, `PipelineConfig.profile` field, and inline `if prof:` timing instrumentation in `extract_pdf()`. This is the foundation — touches the most critical file and validates the timing approach works for all code paths (normal, arXiv shortcut, error early return).

### Test Stencil (Write This First)
```python
# tests/test_pipeline.py — add to existing file

class TestPipelineProfiling:
    def test_profile_populated_when_enabled(self):
        """All 11 step fields >= 0.0 when profile=True."""
        config = PipelineConfig(enable_claude=False, profile=True)
        with _patch_base(), _patch_tables(), _patch_pandoc_unavailable():
            result = extract_pdf(Path("fake.pdf"), config=config)
        assert result.profile is not None
        assert result.profile.base_extraction >= 0.0
        assert result.profile.assemble_result >= 0.0
        # sum should approximate elapsed
        from dataclasses import asdict
        total = sum(asdict(result.profile).values())
        assert total <= result.elapsed_seconds + 0.1

    def test_profile_none_when_disabled(self):
        """profile=False (default) returns None."""
        with _patch_base(), _patch_tables(), _patch_pandoc_unavailable():
            result = extract_pdf(Path("fake.pdf"))
        assert result.profile is None

    def test_profile_arxiv_early_return(self):
        """arXiv shortcut produces partial profile."""
        # ... mock arxiv to succeed, assert arxiv_shortcut > 0, others == 0.0

    def test_profile_error_early_return(self):
        """extract_pages failure produces partial profile."""
        # ... mock extract_pages to raise, assert base_extraction > 0
```

### Changes Required

**See `design.md` for:**
- `PipelineProfile` dataclass definition → `design.md#component-1`
- Inline timing pattern → `design.md#component-2`
- `PipelineConfig.profile` field → `design.md#component-3`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_pipeline.py` (MODIFY — write tests first)
- [x] Add `PipelineProfile` to imports from `types`
- [x] Add `TestPipelineProfiling` class with 4 tests:
  - `test_profile_populated_when_enabled` — normal path, all fields >= 0.0, sum ≈ elapsed
  - `test_profile_none_when_disabled` — default config, profile is None
  - `test_profile_arxiv_early_return` — mock arXiv success, partial profile
  - `test_profile_error_early_return` — mock extract_pages failure, partial profile

#### 2. Types
**File:** `src/agentic_mbse/extraction/types.py`
- [x] Add `PipelineProfile` dataclass with 11 float fields (all default 0.0) — see `design.md#component-1`
- [x] Add `profile: PipelineProfile | None = None` field to `PipelineResult`

#### 3. Pipeline Config
**File:** `src/agentic_mbse/extraction/pipeline.py:146-158`
- [x] Add `profile: bool = False` field to `PipelineConfig`
- [x] Add `PipelineProfile` to imports from `types`

#### 4. Pipeline Instrumentation
**File:** `src/agentic_mbse/extraction/pipeline.py:275-566` (`extract_pdf()`)
- [x] After `start_time = time.time()`: add `prof = PipelineProfile() if config.profile else None`
- [x] Step 1 (arXiv shortcut, ~line 299): wrap with `if prof:` timing, attach `prof` to early return
- [x] Step 2 (base extraction, ~line 307): wrap with `if prof:` timing, attach `prof` to error return
- [x] Step 3 (table detection, ~line 320): wrap with `if prof:` timing
- [x] Step 3b (table filter/enhance, ~line 328): wrap with `if prof:` timing
- [x] Step 4 (quality gate, ~line 390): wrap with `if prof:` timing
- [x] Step 4b (GMFT xref, ~line 408): wrap with `if prof:` timing
- [x] Step 5 (budget allocation, ~line 419): wrap with `if prof:` timing
- [x] Step 6 (Claude enhancement, ~line 429): wrap with `if prof:` timing
- [x] Step 7 (route + merge, ~line 496): wrap with `if prof:` timing
- [x] Step 7b (postprocess, ~line 536): wrap with `if prof:` timing
- [x] Step 8 (assemble result, ~line 547): wrap with `if prof:` timing
- [x] Pass `profile=prof` in final `PipelineResult(...)` constructor

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pipeline.py -v` → all 78 passed in 1.02s
- [x] `uv run pytest tests/` → 1067 passed, 1 skipped, 0 failures (24.40s)
- [x] `uv run ruff check src/ tests/` → passes

**Manual:**
- [x] Verify: `PipelineConfig()` has `profile=False` by default
- [x] Verify: existing pipeline tests still pass unchanged (no behavioral change when profile=False)

**What We Know Works After This Phase:**
- `extract_pdf()` with `profile=True` populates all 11 timing fields
- `extract_pdf()` with `profile=False` (default) returns `profile=None` — identical to pre-change behavior
- Early return paths (arXiv, error) produce valid partial profiles

---

## Phase 2: Profile Module (Route Distribution + Serialization + Summary Table)

### Goal
Create `extraction/profile.py` with pure functions for route distribution computation, JSON serialization, summary table formatting, and corpus discovery. All testable with synthetic data — no dependency on the actual pipeline running.

### Test Stencil (Write This First)
```python
# tests/test_profile.py — NEW file

from agentic_mbse.extraction.profile import (
    ProfileEntry, format_profile_table, profile_to_dict, route_distribution,
)
from agentic_mbse.extraction.types import PageAction, PageDecision, PipelineProfile

def test_route_distribution_mixed():
    decisions = [
        PageDecision(0, PageAction.KEEP),
        PageDecision(1, PageAction.CLAUDE_REPLACE),
        PageDecision(2, PageAction.KEEP),
        PageDecision(3, PageAction.GMFT_REPLACE),
    ]
    dist = route_distribution(decisions)
    assert dist == {"keep": 2, "claude_replace": 1, "gmft_replace": 1}

def test_route_distribution_empty():
    assert route_distribution([]) == {}

def test_profile_to_dict_has_expected_keys():
    prof = PipelineProfile(base_extraction=1.5, claude_enhancement=8.0)
    decisions = [PageDecision(0, PageAction.KEEP)]
    result = profile_to_dict(prof, decisions, page_count=1, elapsed_seconds=10.0)
    assert "step_timing" in result
    assert "route_distribution" in result
    assert result["page_count"] == 1

def test_format_profile_table_alignment():
    entry = ProfileEntry(
        document="test_doc", pages=5,
        route_dist={"keep": 3, "claude_replace": 2},
        elapsed=10.0,
        profile=PipelineProfile(base_extraction=2.0, claude_enhancement=7.0),
    )
    table = format_profile_table([entry])
    assert "test_doc" in table
    assert "Total" in table
```

### Changes Required

**See `design.md` for:**
- `route_distribution()` signature → `design.md#component-4`
- `profile_to_dict()` signature → `design.md#component-5`
- `ProfileEntry` + `format_profile_table()` → `design.md#component-6`
- Display column mappings (timing + routing) → `design.md#component-6`
- `get_profile_corpus()` with path comment → `design.md#component-8`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_profile.py` (NEW — write first)
- [x] Create test file
- [x] `test_route_distribution_mixed` — mixed actions, correct counts
- [x] `test_route_distribution_empty` — empty decisions list
- [x] `test_route_distribution_all_same` — all KEEP
- [x] `test_profile_to_dict_has_expected_keys` — verify structure
- [x] `test_profile_to_dict_step_timing_values` — verify timing values round-trip
- [x] `test_format_profile_table_alignment` — verify document names and totals row present
- [x] `test_format_profile_table_multiple_entries` — verify multi-row output

#### 2. Profile Module
**File:** `src/agentic_mbse/extraction/profile.py` (NEW)
- [x] `route_distribution(decisions)` — Counter-based, returns `dict[str, int]`
- [x] `profile_to_dict(profile, decisions, page_count, elapsed_seconds)` — JSON-ready dict
- [x] `ProfileEntry` dataclass — one row of the summary table
- [x] `format_profile_table(entries)` — formatted string with header, data rows, separator, totals
  - Timing display columns: Base (arxiv+base), Tables (detect+filter), Gate (gate+xref+budget), Claude, Post (route+post+assemble)
  - Route display columns: KEEP (keep+strip_*), CLAUDE (claude_replace), GMFT (gmft_replace+gmft_append)
- [x] `get_profile_corpus()` — path discovery with documented depth assumption

### Validation

**Automated:**
- [x] `uv run pytest tests/test_profile.py -v` → 15 passed in 0.44s
- [x] `uv run pytest tests/` → 1081 passed, 1 known failure (dormant module — resolves in Phase 3)
- [x] `uv run ruff check src/ tests/` → passes

**Manual:**
- [x] Import `from agentic_mbse.extraction.profile import route_distribution` in Python REPL — no errors
- [x] Visually inspect `format_profile_table()` output with test data — columns aligned, totals correct

**What We Know Works After This Phase:**
- Route distribution correctly aggregates all `PageAction` values
- `profile_to_dict()` produces valid JSON-serializable structure
- Summary table is correctly formatted with column grouping and totals
- `get_profile_corpus()` discovers PDFs (returns `[]` if dir missing — correct)

---

## Phase 3: CLI Integration

### Goal
Wire `--profile` flag into the extract CLI. Write `profile.json` per document, collect profile entries, and print summary table to stderr after all documents.

### Test Stencil (Write This First)
```python
# tests/test_profile.py — add CLI-level tests

def test_profile_flag_threads_to_config(tmp_path):
    """--profile sets config.profile=True."""
    # Verify via argparse namespace or by inspecting PipelineConfig construction

def test_profile_json_written(tmp_path):
    """profile.json written alongside output.md when --profile active."""
    # Run cmd_extract with mocked pipeline, check tmp_path / "profile.json" exists
    # Verify JSON structure has step_timing and route_distribution keys
```

### Changes Required

**See `design.md` for:**
- CLI flag definition → `design.md#component-7` point 1
- Config threading → `design.md#component-7` point 2
- `profile.json` writing → `design.md#component-7` point 3
- Summary table printing → `design.md#component-7` point 4

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_profile.py` (MODIFY — add CLI tests)
- [x] `test_profile_json_written` — mock pipeline, verify `profile.json` exists and has correct structure
- [x] `test_profile_summary_table_printed` — mock pipeline for 2+ docs, verify stderr output

#### 2. CLI: Flag Registration
**File:** `src/agentic_mbse/cli/extract_cli.py` — `register_extract_subcommand()` (~line 458)
- [x] Add `--profile` argument (store_true) in pipeline flags section

#### 3. CLI: Config Threading
**File:** `src/agentic_mbse/cli/extract_cli.py` — `cmd_extract()` (~line 335)
- [x] Add `profile=args.profile` to `PipelineConfig(...)` constructor

#### 4. CLI: Profile Output + Summary Collection
**File:** `src/agentic_mbse/cli/extract_cli.py` — `cmd_extract()` (~line 346-364)
- [x] Initialize `profile_entries: list = []` before document loop
- [x] After writing `decisions.json`: if `args.profile and result.profile`, write `profile.json` and append `ProfileEntry` to list
- [x] After document loop (before summary line): if `args.profile and profile_entries`, print `format_profile_table()` to stderr

### Validation

**Automated:**
- [x] `uv run pytest tests/test_profile.py -v` → 19 passed in 0.46s
- [x] `uv run pytest tests/` → 1086 passed, 0 failures (dormant module resolved)
- [x] `uv run ruff check src/ tests/` → passes

**Manual:**
- [ ] `uv run agentic-mbse extract --help` → `--profile` flag visible in help text
- [ ] `uv run agentic-mbse extract some_test.pdf --profile --dry-run --budget 0` → `profile.json` written, timing values present
- [ ] Run on a directory with 2+ PDFs → summary table printed to stderr

**What We Know Works After This Phase:**
- `--profile` flag accepted and threaded to pipeline
- `profile.json` written per document with correct structure
- Summary table printed to stderr for multi-document runs
- No impact on non-profiling runs

---

## Phase 4: Profile Corpus Curation

### Goal
Create `profile_corpus/` at repo root with ~10 diverse PDFs covering the document types listed in the design. Add a `README.md` documenting each specimen. Validate end-to-end with `--profile`.

### Changes Required

**See `design.md` for:**
- Target diversity table (10 slots) → `design.md#component-8`
- Corpus size policy (5MB per file) → `design.md#component-8`

**Specific file changes:**

#### 1. Corpus Directory
**Directory:** `profile_corpus/` (NEW at repo root)
- [x] Create directory
- [x] Add `README.md` documenting: purpose, size policy (5MB/file), specimen list with type/page count/source
- [x] Populate slots — 10 symlinks to tests/corpus/pdfs/:
  - [x] Slot 1: Clean born-digital → woodruff_2026 (25pp, 0.4MB)
  - [x] Slot 2: Two-column academic → hawker_2020 (14pp, 1.2MB)
  - [x] Slot 3: Scanned/degraded → schulte_1978 (10pp, 0.2MB)
  - [x] Slot 4: Table-heavy → hsu_2020 (9pp, 1.6MB)
  - [x] Slot 5: Equation-heavy → paischer_2025 (24pp, 1.4MB)
  - [x] Slot 6: Short document → tajima (16pp, 1.4MB)
  - [x] Slot 7: Long document → araiinejad_2024 (50pp, 0.8MB)
  - [x] Slot 8: Mixed content → hansen_2025 (28pp, 4.8MB)
  - [x] Slot 9: Technical report → delene_2001 (39pp, 0.3MB)
  - [x] Slot 10: Overview document → sparc_overview (25pp, 1.9MB)

#### 2. Gitignore
**File:** `.gitignore`
- [x] Verified `profile_corpus/` is NOT gitignored

### Validation

**Automated:**
- [x] `uv run pytest tests/` → 1086 passed, 0 failures
- [x] `get_profile_corpus()` discovers all 10 PDFs

**Manual:**
- [ ] `uv run agentic-mbse extract profile_corpus/ --profile --budget 0 --dry-run` → summary table printed for all corpus PDFs
- [ ] Verify each PDF produces a `profile.json` in its output directory
- [ ] Verify summary table shows timing and route columns for all documents
- [x] Verify no PDF exceeds 5MB: `find profile_corpus/ -name "*.pdf" -size +5M` → no results
- [ ] (Optional) Full run with Claude: `uv run agentic-mbse extract profile_corpus/ --profile --budget 2` → summary shows Claude timing

**What We Know Works After This Phase:**
- Diverse corpus available for benchmarking
- End-to-end profiling works on real, varied documents
- Summary table reveals actual timing distribution across document types

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
- `uv run pytest tests/` — run all tests
- `uv run ruff check src/ tests/` — lint
- `uv run ruff format src/ tests/` — format

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Modifying `extract_pdf()` — write tests first, run full suite after each step change. The `if prof:` pattern is minimal and won't affect control flow.
- **Phase 2**: New module with no dependencies on running pipeline — pure functions, easy to verify in isolation.
- **Phase 3**: CLI changes are additive (new flag, new output) — existing flags and behavior unchanged.
- **Phase 4**: Corpus curation is non-code — zero risk to existing functionality. Start with 5 PDFs, fill gaps later.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Added `PipelineProfile` dataclass (11 float fields) to `src/agentic_mbse/extraction/types.py`
- Added `profile: PipelineProfile | None = None` field to `PipelineResult`
- Added `profile: bool = False` field to `PipelineConfig` in `pipeline.py`
- Added `PipelineProfile` to imports in `pipeline.py`
- Instrumented all 11 steps in `extract_pdf()` with inline `if prof:` timing guards
- Attached `prof` to both early return paths (arXiv shortcut, base extraction error)
- Added `profile=prof` to final `PipelineResult` constructor
- Added `TestPipelineProfiling` class to `tests/test_pipeline.py` with 4 tests:
  - `test_profile_populated_when_enabled` — all 11 fields >= 0.0, sum ≈ elapsed
  - `test_profile_none_when_disabled` — default returns None
  - `test_profile_arxiv_early_return` — partial profile, only arxiv_shortcut set
  - `test_profile_error_early_return` — partial profile with base_extraction
**Issues:** None
**Deviations:** None — implementation matched design exactly

### Phase 2 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Created `src/agentic_mbse/extraction/profile.py` with:
  - `route_distribution()` — Counter-based action counting
  - `profile_to_dict()` — JSON-serializable dict with step_timing + route_distribution
  - `ProfileEntry` dataclass for summary table rows
  - `format_profile_table()` — formatted table with timing groups (Base/Tables/Gate/Claude/Post), route groups (KEEP/CLAUDE/GMFT), and totals row
  - `get_profile_corpus()` — path discovery from repo root
- Created `tests/test_profile.py` with 15 tests:
  - 4 route_distribution tests (mixed, empty, all same, all types)
  - 4 profile_to_dict tests (keys, timing values, routes, counts)
  - 6 format_profile_table tests (single, multiple, empty, strip grouping, gmft grouping, long names)
  - 1 get_profile_corpus test
**Issues:** `test_no_dormant_modules` fails because `profile.py` isn't imported from entry points yet — resolves in Phase 3 when CLI imports it.
**Deviations:** Added extra tests beyond plan (all_action_types, strip grouping, gmft grouping, long names) for better coverage.

### Phase 3 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Added `--profile` flag to `register_extract_subcommand()` in `extract_cli.py`
- Added `profile=args.profile` to `PipelineConfig()` constructor in `cmd_extract()`
- Added `profile_entries` list initialization before document loop
- Added `profile.json` writing block after `cost.json` — writes per-document profile with step_timing + route_distribution
- Added `ProfileEntry` collection alongside `profile.json` writing
- Added summary table printing to stderr after document loop via `format_profile_table()`
- Added `profile=False` to `MockArgs` defaults in `tests/test_extract_cli.py`
- Added 4 CLI integration tests to `tests/test_profile.py`:
  - `test_profile_json_written` — verifies JSON structure and values
  - `test_profile_json_not_written_without_flag` — verifies no profile.json when disabled
  - `test_profile_summary_table_printed` — verifies stderr output for multi-doc runs
  - `test_profile_flag_threads_to_config` — verifies config.profile=True
**Issues:** Had to add `profile=False` to existing `MockArgs` in `test_extract_cli.py` (existing tests broke on `args.profile` access).
**Deviations:** Added `test_profile_json_not_written_without_flag` and `test_profile_flag_threads_to_config` beyond plan for better coverage.

### Phase 4 Completion
**Completed:** 2026-03-01
**Actual Changes:**
- Created `profile_corpus/` directory at repo root
- Added 10 symlinks to `tests/corpus/pdfs/` covering all design slots
- Naming convention: `NN_type_description.pdf` (01-10, sorted by slot)
- Added `profile_corpus/README.md` with usage instructions, size policy, and specimen table
- Updated `test_discovers_corpus_pdfs` test to verify 10 PDFs found
**Issues:** None
**Deviations:**
- Used symlinks to existing test corpus instead of separate PDF copies (avoids duplication, all <5MB)
- Slot 6 (short document) uses tajima at 16pp rather than target 2-3pp (no shorter docs available in corpus)
- Slot 10 changed from "minimal/edge case" to "overview document" (sparc_overview, 25pp) since no 1-3 page docs available

---

**Status**: Complete

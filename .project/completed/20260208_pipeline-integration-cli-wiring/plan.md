# Implementation Plan: Pipeline Integration + CLI Wiring

**Status:** Complete
**Created:** 2026-02-08
**Last Updated:** 2026-02-08

## Source Documents
- **Spec:** `.project/active/pipeline-integration-cli-wiring/spec.md`
- **Design:** `.project/active/pipeline-integration-cli-wiring/design.md` — See here for component details, API signatures, pipeline code blocks

## Implementation Strategy

**Phasing Rationale:**
Phase 1 is mechanical but load-bearing — every existing test breaks if we add CLI args without updating MockArgs, so we fix that first and verify green. Phase 2 is the actual feature insertion. Phase 3 locks down the new behavior with targeted tests. This ordering means we never have a broken test suite during development.

**Overall Validation Approach:**
- Run `uv run pytest tests/test_extract_cli.py -v` after each phase
- Run `uv run pytest tests/` (full suite) after Phase 2 and Phase 3
- CLI smoke test after Phase 2

---

## Phase 1: Test Infrastructure + MockArgs Update

### Goal
Update all existing `MockArgs` instantiations with `structure_only=False` and `model=None` defaults, add `_make_extraction_result` helper. This is mechanical but must be done first — existing tests will fail without it once we add CLI args.

### Test Stencil (Write This First)
```python
# No new tests in Phase 1 — we're updating existing test infrastructure.
# Validation: all existing tests pass with new MockArgs attrs.
```

### Changes Required

**See `design.md#4-test-changes` for:** MockArgs update strategy, test fixture pattern

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_extract_cli.py`
- [x] Add `structure_only=False, model=None` to every `MockArgs(...)` call (~10 sites, lines: 124, 141, 167, 207, 236, 282, 335, 380, 415, 458)
- [x] Add `_make_extraction_result(tmp_path, md_content=...)` helper function (see `design.md#4-test-changes` for implementation)

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extract_cli.py -v` → All existing tests pass
- [x] `uv run ruff check tests/test_extract_cli.py` → No lint issues

**What We Know Works After This Phase:**
Test infrastructure is ready for new CLI args. No production code touched yet.

---

## Phase 2: CLI Args + Pipeline Wiring

### Goal
Add `--structure-only` and `--model` arguments, insert L3 structural pass block between L2 and L4, modify L4 guard. This is the entire production code change.

### Test Stencil (Write This First)
```python
# Phase 2 relies on existing tests for regression safety.
# New tests come in Phase 3 — here we verify existing tests still pass
# after the production code change.
```

### Changes Required

**See `design.md#1-cli-argument-changes` for:** Argument definitions, help text updates
**See `design.md#2-pipeline-modification` for:** Full L3 code block, flag computation, L4 guard change

**Specific file changes:**

#### 1. CLI Arguments
**File:** `src/agentic_mbse/cli/extract_cli.py:366-383`
- [x] Update `--enhance` help text (line 369)
- [x] Add `--structure-only` argument after `--no-tables` block
- [x] Add `--model` argument after `--structure-only`

#### 2. Pipeline Logic
**File:** `src/agentic_mbse/cli/extract_cli.py:219-278`
- [x] Add `structure_only` and `model` to flag extraction block (after line 222), compute `run_structural` and `run_ai_repair` booleans
- [x] Insert L3 block between L2 (line ~250) and current L3/AI repair (line ~252) — see `design.md#2-pipeline-modification` for full code block
- [x] Change L4 guard from `if enhance and remaining_problems:` to `if run_ai_repair and remaining_problems:`

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extract_cli.py -v` → All existing tests still pass
- [x] `uv run pytest tests/` → Full suite, no regressions
- [x] `uv run ruff check src/agentic_mbse/cli/extract_cli.py` → No lint issues

**Manual:**
- [x] `uv run agentic-mbse extract --help` → Shows `--structure-only`, `--model`, updated `--enhance` help
- [x] Verify `--model` shows choices: `{opus,sonnet,haiku}`

**What We Know Works After This Phase:**
Production code is complete. Existing behavior preserved (verified by existing tests). New CLI flags registered and visible. Pipeline ordering correct in code.

---

## Phase 3: New Tests for L3 Integration

### Goal
Add 6 targeted tests covering all new flag combinations, gate skip logic, model passthrough, and failure fallback. This locks down the Phase 2 implementation.

### Test Stencil (Write This First)
```python
class TestStructuralPass:
    """Tests for L3 Claude structural pass integration."""

    def test_enhance_triggers_structural_pass(self, tmp_path):
        """--enhance runs L3 (structure) then L4 (AI repair) in order."""
        # Mock: needs_claude_structure → True, enhance_structure → modified md
        # Mock: repair_document → modified md
        # Assert: both called, enhance_structure before repair_document

    def test_enhance_skips_structure_when_not_needed(self, tmp_path):
        """--enhance with well-structured doc skips L3, still runs L4."""
        # Mock: needs_claude_structure → False
        # Mock: detect_problems → some problems
        # Assert: enhance_structure NOT called, repair_document called

    def test_structure_only_skips_ai_repair(self, tmp_path):
        """--structure-only runs L3 without L4."""
        # Mock: needs_claude_structure → True, enhance_structure → modified md
        # Assert: enhance_structure called, repair_document NOT called

    def test_model_flag_passed_through(self, tmp_path):
        """--model sonnet overrides both Phase A and Phase B."""
        # Mock: needs_claude_structure → True
        # Assert: enhance_structure called with phase_a_model="sonnet", phase_b_model="sonnet"

    def test_structure_failure_continues_pipeline(self, tmp_path):
        """L3 failure → warning, pipeline continues to L4."""
        # Mock: needs_claude_structure → True, enhance_structure raises Exception
        # Mock: detect_problems → some problems, repair_document → success
        # Assert: no crash, repair_document still called

    def test_default_mode_no_structural_pass(self, tmp_path):
        """Default mode (no --enhance/--structure-only) never calls L3 or L4."""
        # No enhancement flags
        # Assert: neither enhance_structure nor repair_document called
```

### Changes Required

**See `design.md#4-test-changes` for:** Test case descriptions, mocking approach, fixture pattern

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_extract_cli.py`
- [x] Add `TestStructuralPass` class with 6 test methods
- [x] Each test uses `_make_extraction_result` helper from Phase 1
- [x] Each test patches `_run_extraction`, `needs_claude_structure`, `enhance_structure`, and/or `repair_document` as needed
- [x] Import `patch` from `unittest.mock` (already imported)

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extract_cli.py::TestStructuralPass -v` → All 6 new tests pass
- [x] `uv run pytest tests/test_extract_cli.py -v` → All tests pass (old + new)
- [x] `uv run pytest tests/` → Full suite, no regressions
- [x] `uv run ruff check tests/test_extract_cli.py` → No lint issues

**What We Know Works After This Phase:**
All spec acceptance criteria covered by automated tests. L3→L4 ordering verified. Gate skip path verified. Model passthrough verified. Failure fallback verified. Default mode unchanged.

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Run tests after every MockArgs update to catch missed sites immediately
- **Phase 2**: Diff against design.md code blocks to ensure faithful implementation
- **Phase 3**: If lazy-import patching fails, switch patch target from `agentic_mbse.extraction.claude_structure.X` to `agentic_mbse.cli.extract_cli.X` (depends on where the name is resolved)

## Implementation Notes

*TO BE FILLED DURING IMPLEMENTATION*

### Phase 1 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Added `structure_only=False, model=None` to all 10 `MockArgs(...)` calls in `tests/test_extract_cli.py`
- Added `_make_extraction_result()` helper function at module level (after `MockArgs` class)
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Updated `--enhance` help text in `register_extract_subcommand()` (line ~369)
- Added `--structure-only` and `--model` arguments after `--no-tables`
- Added flag computation block: `structure_only`, `run_structural`, `run_ai_repair`, `model` (lines 222-226)
- Inserted L3 structural pass block (lines 256-294) between L2 GMFT and L4 AI repair
- Changed L4 guard from `if enhance and remaining_problems:` to `if run_ai_repair and remaining_problems:`
**Issues:** None
**Deviations:** None — faithful to design.md code blocks

### Phase 3 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Added `TestStructuralPass` class with 6 test methods in `tests/test_extract_cli.py`
- Tests patch at source module (`agentic_mbse.extraction.claude_structure.*`) since `extract_cli.py` uses lazy imports
- All tests use `_make_extraction_result` helper and `no_tables=True` to isolate L3/L4 behavior
**Issues:** One ruff F841 lint warning for unused `mock_repair` variable in `test_model_flag_passed_through` — fixed by dropping the `as mock_repair` binding
**Deviations:** None

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**

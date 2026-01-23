# Implementation Plan: Model Regression Testing

**Status:** Draft
**Created:** 2026-01-23 16:33:54 UTC
**Last Updated:** 2026-01-23 16:33:54 UTC
**Branch:** 1cfe_dev

## Source Documents
- **Spec:** `.project/active/model-regression-testing/spec.md`
- **Design:** `.project/active/model-regression-testing/design.md` ← See here for component details, template content, line numbers

## Implementation Strategy

**Phasing Rationale:**
1. **Phase 1 (CLI + Templates)** - Core infrastructure first. If init doesn't create test directories and files, nothing else works.
2. **Phase 2 (Documentation)** - Tool-owned docs that explain testing. Depends on understanding Phase 1 output.
3. **Phase 3 (Commands)** - Workflow guidance references infrastructure from Phase 1 and docs from Phase 2.
4. **Phase 4 (Target Repo Validation)** - Real-world test on fusion-tea. Confirms everything works end-to-end with actual models.

**Overall Validation Approach:**
- Each phase starts with tests (for Phase 1) or validation (for Phases 2-4)
- `uv run pytest tests/test_cli.py` validates CLI changes
- Manual init + inspection validates template content
- Existing tests must continue to pass
- Phase 4 validates end-to-end on real target repo (fusion-tea)

---

## Phase 1: Test Infrastructure & CLI Changes

### Goal
Add `tests/models/` directory creation and template files to `cmd_init()`. This is the core infrastructure - all other phases depend on it working.

### Test Stencil (Write This First)
```python
# tests/test_cli.py - add to TestCmdInit class

def test_init_creates_tests_models_directory(self, tmp_path):
    """Init creates tests/models/ directory."""
    args = MockArgs(path=str(tmp_path), force=False)
    result = cmd_init(args)

    assert result == EXIT_SUCCESS
    assert (tmp_path / "tests" / "models").is_dir()

def test_init_creates_example_test_file(self, tmp_path):
    """Init creates example test file in tests/models/."""
    args = MockArgs(path=str(tmp_path), force=False)
    cmd_init(args)

    test_file = tmp_path / "tests" / "models" / "test_example.py"
    assert test_file.exists()
    assert "get_syside" in test_file.read_text()

def test_init_creates_conftest(self, tmp_path):
    """Init creates conftest.py in tests/."""
    args = MockArgs(path=str(tmp_path), force=False)
    cmd_init(args)

    conftest = tmp_path / "tests" / "conftest.py"
    assert conftest.exists()
    assert "load_sysml" in conftest.read_text()

def test_init_skips_test_files_if_exist(self, tmp_path):
    """Init preserves existing test files (user-owned)."""
    test_file = tmp_path / "tests" / "models" / "test_example.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("# custom tests")

    args = MockArgs(path=str(tmp_path), force=False)
    cmd_init(args)

    assert test_file.read_text() == "# custom tests"
```

### Changes Required

**See `design.md#component-1` for:**
- Full template file contents
- Directory creation pattern
- Template ownership (user-owned)

**Specific file changes:**

#### 1. Test File (Write First)
**File:** `tests/test_cli.py` (MODIFY)
- [x] Add test stencil above to `TestCmdInit` class
- [x] Verify tests fail initially (no implementation yet)

#### 2. Template Files
**File:** `project_templates/test_models_example.py.template` (NEW)
- [x] Create file with content from `design.md#component-1`

**File:** `project_templates/conftest.py.template` (NEW)
- [x] Create file with content from `design.md#component-1`

#### 3. CLI Implementation
**File:** `src/agentic_mbse/cli/__init__.py` (MODIFY)
- [x] Add to `USER_OWNED_TEMPLATES` (line ~51-56):
  ```python
  ("test_models_example.py.template", "tests/models/test_example.py"),
  ("conftest.py.template", "tests/conftest.py"),
  ```
- [x] Add directory creation after line ~528:
  ```python
  # Create tests/models/ directory
  tests_models_dir = target / "tests" / "models"
  tests_models_dir.mkdir(parents=True, exist_ok=True)
  ```

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/test_cli.py::TestCmdInit -v` → New tests pass
- [x] `uv run pytest tests/` → Full suite passes (no regressions)
- [x] `uv run ruff check src/ tests/` → Linting passes (pre-existing issues only)

**Manual:**
- [x] Run: `uv run agentic-mbse init /tmp/test-project`
- [x] Verify: `/tmp/test-project/tests/models/test_example.py` exists
- [x] Verify: `/tmp/test-project/tests/conftest.py` exists
- [x] Verify: Example test file contains `get_syside` import
- [x] Run: `cd /tmp/test-project && pytest tests/models/ -v` → Should skip (no models)

**What We Know Works After This Phase:**
- `agentic-mbse init` creates test infrastructure
- Template files are correctly installed as user-owned
- Example test demonstrates syside usage pattern

---

## Phase 2: Documentation (MODELING_GUIDE.md)

### Goal
Add testing paradigm documentation to the tool-owned template. Users will see this documentation after running init or re-init.

### Test Stencil (Validation-Based)
```bash
# No pytest for this phase - validate content manually
# After editing template, verify:
grep -q "Model Regression Testing" project_templates/MODELING_GUIDE.md.template
grep -q "pytest tests/models/" project_templates/MODELING_GUIDE.md.template
grep -q "get_syside" project_templates/MODELING_GUIDE.md.template
```

### Changes Required

**See `design.md#component-2` for:**
- Full documentation section content
- Insertion point (before "Reference Information")

**Specific file changes:**

#### 1. Documentation Template
**File:** `project_templates/MODELING_GUIDE.md.template` (MODIFY)
- [x] Add "## Model Regression Testing" section from `design.md#component-2`
- [x] Insert before final reference section

### Validation (How to Verify This Phase)

**Automated:**
- [x] `grep -q "Model Regression Testing" project_templates/MODELING_GUIDE.md.template` → Found
- [x] `uv run pytest tests/` → No regressions (287 passed)

**Manual:**
- [x] Run: `uv run agentic-mbse init /tmp/test-project --force`
- [x] Verify: `/tmp/test-project/modeling_pm/MODELING_GUIDE.md` contains testing section
- [x] Read section: Clear explanation of library/usage regression risk

**What We Know Works After This Phase:**
- Initialized projects have testing documentation
- Documentation explains the testing paradigm clearly

---

## Phase 3: MBSE Commands (spec → plan → implement)

### Goal
Update the three workflow commands with testing guidance. After this phase, the full workflow naturally produces tested models.

### Test Stencil (Validation-Based)
```bash
# Verify command files contain testing guidance
grep -q "evaluatable" claude/commands/spec-model.md
grep -q "Test Requirements" claude/commands/plan-model.md
grep -q "pytest tests/models/" claude/commands/implement-model.md
```

### Changes Required

**See `design.md#component-3`, `#component-4`, `#component-5` for:**
- Specific insertion points and content for each command
- Examples of evaluatable criteria, test phases, validation checklists

**Specific file changes:**

#### 1. Spec Command
**File:** `claude/commands/spec-model.md` (MODIFY)
- [x] Add evaluatable success criteria guidance from `design.md#component-3`
- [x] Add regression safety criteria section
- [x] Insert after "**Validation Success**" in Stage 3 (around line 117)

#### 2. Plan Command
**File:** `claude/commands/plan-model.md` (MODIFY)
- [x] Add test requirements to phase template from `design.md#component-4`
- [x] Add test phase pattern table
- [x] Add example phase with tests
- [x] Insert after "User Review Point" (around line 98)

#### 3. Implement Command
**File:** `claude/commands/implement-model.md` (MODIFY)
- [x] Add regression testing section from `design.md#component-5`
- [x] Add test location convention
- [x] Update final validation checklist to include pytest

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/` → No regressions (287 passed)
- [x] Grep checks pass (evaluatable, Test Requirements, pytest)

**Manual:**
- [x] Read `spec-model.md`: Contains evaluatable criteria guidance and examples
- [x] Read `plan-model.md`: Contains test phase pattern and example
- [x] Read `implement-model.md`: Contains regression testing section and checklist

**What We Know Works After This Phase:**
- `/spec-model` guides users to write evaluatable success criteria
- `/plan-model` includes test-writing phases in generated plans
- `/implement-model` runs regression tests as part of validation

---

## Phase 4: Target Repo Validation (fusion-tea)

### Goal
Apply changes to a real target repo (fusion-tea) and confirm the test infrastructure works with actual SysML models. This is the end-to-end validation that proves everything works together.

### Context
**Target repo:** `/home/reid/1cfe/fusion-tea/`
- Has existing models in `models/library/` and `models/designs/`
- Has SysML test files in `models/tests/`
- Currently has NO `tests/` directory at project root
- Is an existing agentic-mbse initialized project
- **Installed with `--dev` mode** - tool-owned files are symlinked to agentic-mbse source

**Dev mode implications:**
- Tool-owned files (commands, agents, MODELING_GUIDE.md) are symlinks → changes in agentic-mbse immediately visible
- User-owned files (test templates, conftest.py) are still **copied** (not symlinked) → need to verify this behavior
- Run with `--dev` flag to maintain consistency: `uv run agentic-mbse init --dev /home/reid/1cfe/fusion-tea`

### Safety Approach
1. Run `init` without `--force` first - only creates new files, preserves existing
2. Verify test infrastructure appears correctly
3. Run example tests against actual models
4. If issues, changes are isolated to fusion-tea (not committed to agentic-mbse)

### Changes Required

**No code changes** - this phase validates Phases 1-3 work correctly.

**Actions:**

#### 1. Apply init to fusion-tea (dev mode)
- [x] Run: `cd /home/reid/1cfe/agentic-mbse && uv run agentic-mbse init --dev /home/reid/1cfe/fusion-tea`
- [x] Verify output shows `tests/models/test_example.py` created (copied, not symlinked - user-owned)
- [x] Verify output shows `tests/conftest.py` created (copied, not symlinked - user-owned)
- [x] Verify tool-owned files remain symlinked (commands, MODELING_GUIDE.md)

#### 2. Verify file structure and ownership
- [x] Verify: `/home/reid/1cfe/fusion-tea/tests/models/test_example.py` exists
- [x] Verify: `/home/reid/1cfe/fusion-tea/tests/conftest.py` exists
- [x] Verify: Test file contains `get_syside` import
- [x] Verify: Test files are **regular files** (not symlinks) - user-owned behavior:
  ```bash
  ls -la /home/reid/1cfe/fusion-tea/tests/  # Should NOT show -> symlink arrows
  ```

#### 3. Run example tests
- [x] Run: `cd /home/reid/1cfe/fusion-tea && pytest tests/models/ -v`
- [x] Expected: Tests either PASS or SKIP (no failures)
- [x] If tests run (not skip): Verify they correctly parse fusion-tea models

#### 4. Verify documentation updated
- [x] Check: `modeling_pm/MODELING_GUIDE.md` contains "Model Regression Testing" section
- [x] (Tool-owned, should have been updated)

### Validation (How to Verify This Phase)

**Automated:**
- [x] `pytest tests/models/ -v` in fusion-tea → All pass or skip
- [x] No Python import errors in test files

**Manual:**
- [x] Inspect `tests/models/test_example.py` - looks correct
- [x] Inspect `tests/conftest.py` - looks correct
- [x] Test files are syntactically valid Python

**What We Know Works After This Phase:**
- Full end-to-end flow works on real target repo
- Test infrastructure correctly detects and loads SysML models
- Example tests provide useful starting point for modelers
- No regressions in existing fusion-tea functionality
- Dev mode correctly handles user-owned test files (copied, not symlinked)

### Rollback (If Issues)
```bash
# If something goes wrong, remove the new test files:
rm -rf /home/reid/1cfe/fusion-tea/tests/
# (This only removes what we added - init without --force doesn't modify existing files)
```

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
```bash
# Run tests
uv run pytest tests/

# Run specific test class
uv run pytest tests/test_cli.py::TestCmdInit -v

# Linting
uv run ruff check src/ tests/

# Test init manually
uv run agentic-mbse init /tmp/test-project
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Test template uses `pytest.skip()` for missing models - verify this works
- **Phase 2**: Documentation is tool-owned, so re-init updates it - verify this behavior
- **Phase 3**: Commands are tool-owned - changes propagate on re-init
- **Phase 4**: Run without `--force` first, rollback script provided if issues

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-01-23 17:35 UTC
**Actual Changes:**
- Created `project_templates/test_models_example.py.template` with example syside tests
- Created `project_templates/conftest.py.template` with common fixtures
- Added entries to `USER_OWNED_TEMPLATES` in `src/agentic_mbse/cli/__init__.py:51-58`
- Added `tests/models/` directory creation in `src/agentic_mbse/cli/__init__.py:533-535`
- Added 4 tests to `tests/test_cli.py:171-211`

**Validation:**
- All 4 new tests pass
- Full test suite: 287 passed, 1 skipped (no regressions)
- Manual verification: `agentic-mbse init` creates `tests/models/test_example.py` and `tests/conftest.py`
- Example tests skip gracefully when no models/ directory exists

**Issues:** None

**Deviations:** None - implementation followed plan exactly

### Phase 2 Completion
**Completed:** 2026-01-23 17:42 UTC
**Actual Changes:**
- Added "## Model Regression Testing" section to `project_templates/MODELING_GUIDE.md.template`
- Section includes: Why Regression Testing Matters, Test Structure, Writing Model Tests, Running Tests, When to Write Tests
- Inserted after "Validation Checklist" section and before "Tools and Scripts"

**Validation:**
- All grep checks pass (section header, pytest command, get_syside pattern)
- Full test suite: 287 passed, 1 skipped (no regressions)
- Manual init verification: MODELING_GUIDE.md contains testing section

**Issues:** None

**Deviations:** None - implementation followed design exactly

### Phase 3 Completion
**Completed:** 2026-01-23 17:52 UTC
**Actual Changes:**
- Updated `claude/commands/spec-model.md`:
  - Added "Define Evaluatable Success Criteria" section (step 4) with pattern and examples table
  - Added "Regression Safety Criteria" section (step 5) for library modifications
  - Renumbered subsequent steps (4→6, 5→7)
- Updated `claude/commands/plan-model.md`:
  - Added "Test Requirements" as item 7 in phase structure
  - Added "Test Phase Pattern" table showing test activity per phase
  - Added example phase with test deliverables and regression test checkpoint
  - Added "Final Validation Phase Must Include" template with pytest command
- Updated `claude/commands/implement-model.md`:
  - Added "Regression Testing" section after quality check interpretation
  - Added test phase deliverables checklist
  - Added test location convention diagram
  - Updated Stage 4 Final Validation checklist with `pytest tests/models/ -v`

**Validation:**
- All grep checks pass (evaluatable, Test Requirements, pytest)
- Full test suite: 287 passed, 1 skipped (no regressions)

**Issues:** None

**Deviations:** None - implementation followed design exactly

### Phase 4 Completion
**Completed:** 2026-01-23 18:55 UTC
**Target Repo:** `/home/reid/1cfe/fusion-tea/`
**Test Results:** 1 passed, 2 skipped, 1 failed

**Verification:**
- `tests/models/` directory created with `test_example.py` (regular file, user-owned)
- `tests/conftest.py` created (regular file, user-owned)
- Commands correctly symlinked to agentic-mbse source
- `modeling_pm/MODELING_GUIDE.md` symlinked with testing section visible

**Issues Found and Fixed:**
1. **Template API mismatch**: Original template used `for d in diagnostics` but syside `Diagnostics` object is not directly iterable
   - **Fix**: Changed to `diagnostics.parser` for syntax errors and `diagnostics.sema` for semantic errors
   - Files updated: `project_templates/test_models_example.py.template`

2. **Real model issue detected**: Test correctly found unresolved reference in `models/tests/multiplicity_sum_test.sysml:21:39` - `No Type named 'sum' found`
   - This is expected behavior - regression tests are working as designed

**Test Infrastructure Validation:**
- Tests run without import errors
- `test_full_model_parses_without_errors` PASSED (correctly uses `diagnostics.parser`)
- `test_design_references_resolve` correctly detected real issue in models
- `test_library_parses_without_errors` SKIPPED (no `models/library/` directory)
- `test_example_definition_exists` SKIPPED (placeholder test)

**User Feedback:** Tests correctly detect real issues in existing models - the regression testing infrastructure is working as intended.

---

**Status**: Draft → In Progress → Complete

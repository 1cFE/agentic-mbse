# Implementation Plan: D1.7 Test Updates

**Status:** Complete
**Created:** 2026-02-02
**Last Updated:** 2026-02-02

## Source Documents
- **Spec:** `.project/active/d1.7-test-updates/spec.md`
- **Design:** N/A (mechanical test path updates — no design phase needed)

## Implementation Strategy

**Phasing Rationale:**
Phase 1 fixes all broken tests to establish a green baseline. Phase 2 adds new coverage on top. This ordering ensures we never confuse pre-existing failures with regressions from new test code.

**Overall Validation Approach:**
- Run `uv run pytest tests/test_cli.py -v` after each phase
- Run `uv run pytest tests/` after Phase 2 to confirm no regressions

---

## Phase 1: Fix Broken Tests (9 failures → 0)

### Goal
Get all 70 existing tests passing by updating path assertions from old `modeling_pm/` and root-level paths to the new 4-directory structure, and deleting the 2 obsolete `TestLocalGuide` tests.

### Test Stencil (Write This First)
No new tests in this phase — we're fixing existing tests. The "test-first" principle is satisfied because the 9 failing tests already define the expected behavior; we're updating them to match the implemented behavior.

### Changes Required

All changes in `tests/test_cli.py`:

#### 1. SOURCE_INDEX.md path fixes (FR-1, FR-2, FR-3, FR-9)

**`test_creates_source_index`** (line ~75–84):
- [x] Change `tmp_path / "SOURCE_INDEX.md"` → `tmp_path / "knowledge" / "SOURCE_INDEX.md"`
- [x] Keep assertion `"Source Index" in content`

**`test_skips_source_index_if_exists_without_force`** (line ~95–106):
- [x] Pre-create at `tmp_path / "knowledge" / "SOURCE_INDEX.md"` (mkdir `knowledge/` first)
- [x] Assert content preserved at new path

**`test_overwrites_source_index_with_force`** (line ~108–118):
- [x] Pre-create at `tmp_path / "knowledge" / "SOURCE_INDEX.md"` (mkdir `knowledge/` first)
- [x] Assert overwritten content at new path

**`test_uses_current_directory_if_no_path`** (line ~120–127):
- [x] Assert `(tmp_path / "knowledge" / "SOURCE_INDEX.md").exists()`

#### 2. Dev mode path fixes (FR-4, FR-5, FR-10)

**`test_dev_creates_symlinks_for_tool_templates`** (line ~416–422):
- [x] Change `tmp_path / "modeling_pm" / "MODELING_GUIDE.md"` → `tmp_path / "modeling_project" / "MODELING_GUIDE.md"`

**`test_dev_updates_gitignore`** (line ~490–505):
- [x] Change `"modeling_pm/MODELING_GUIDE.md"` → `"modeling_project/MODELING_GUIDE.md"`
- [x] Change `"modeling_pm/MODELING_PROCESS.md"` → `"modeling_project/MODELING_PROCESS.md"`

**`test_dev_copies_user_owned_files`** (line ~424–433):
- [x] Change `tmp_path / "SOURCE_INDEX.md"` → `tmp_path / "knowledge" / "SOURCE_INDEX.md"`

#### 3. Modification detection path fixes (FR-7, FR-8)

**`test_reinit_with_modification_prompts`** (line ~845–866):
- [x] Change `tmp_path / "modeling_pm" / "MODELING_GUIDE.md"` → `tmp_path / "modeling_project" / "MODELING_GUIDE.md"`

**`test_force_flag_skips_prompts`** (line ~868–887):
- [x] Change `tmp_path / "modeling_pm" / "MODELING_GUIDE.md"` → `tmp_path / "modeling_project" / "MODELING_GUIDE.md"`

#### 4. Delete obsolete tests (FR-6)

- [x] Delete entire `TestLocalGuide` class (lines ~574–599) — `LOCAL_GUIDE.md` removed per D1.3

### Validation

**Automated:**
- [x] `uv run pytest tests/test_cli.py -v` → 0 failures (68 tests — 70 minus 2 deleted)
- [x] `uv run ruff check tests/test_cli.py` → no new lint errors (6 pre-existing)

**What We Know Works After This Phase:**
All pre-existing test coverage is green and aligned with the 4-directory architecture.

---

## Phase 2: Add New Coverage Tests

### Goal
Add tests for the 6 new templates, CSV installation, and full directory structure — covering spec FR-11 through FR-14.

### Test Stencil (Write This First)

```python
class TestNewTemplates:
    """Tests for templates added in D1.1/D1.2."""

    def test_init_creates_knowledge_registry(self, tmp_path):
        """Init creates KNOWLEDGE.md in knowledge/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        knowledge = tmp_path / "knowledge" / "KNOWLEDGE.md"
        assert knowledge.exists()

    def test_init_creates_architecture(self, tmp_path):
        """Init creates ARCHITECTURE.md in modeling_project/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "modeling_project" / "ARCHITECTURE.md").exists()

    # ... REQUIREMENTS.md, VALIDATION_MATRIX.md similarly

    def test_init_creates_epic_guide(self, tmp_path):
        """Init creates EPIC_GUIDE.md in work/ (tool-owned)."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "work" / "EPIC_GUIDE.md").exists()

    def test_init_creates_epic_template(self, tmp_path):
        """Init creates epic_template.md in work/backlog/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        assert (tmp_path / "work" / "backlog" / "epic_template.md").exists()


class TestDataTemplates:
    """Tests for data/ directory templates."""

    def test_init_creates_traceability_csv(self, tmp_path):
        """Init creates traceability_matrix.csv in data/."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        csv_path = tmp_path / "data" / "traceability_matrix.csv"
        assert csv_path.exists()
        header = csv_path.read_text().splitlines()[0]
        assert "Element" in header
        assert "Requirement" in header


class TestDirectoryStructure:
    """Tests for full directory structure creation."""

    def test_init_creates_full_directory_structure(self, tmp_path):
        """Init creates all 16 expected directories."""
        args = MockArgs(path=str(tmp_path), force=False)
        cmd_init(args)
        expected_dirs = [
            "knowledge",
            "knowledge/research/pending",
            "knowledge/research/approved",
            "knowledge/research/impacts",
            "knowledge/sources",
            "modeling_project",
            "modeling_project/intent",
            "work",
            "work/backlog",
            "work/active",
            "work/completed",
            "work/analysis",
            "work/learnings",
            "data",
            "models/library",
            "models/designs",
        ]
        for d in expected_dirs:
            assert (tmp_path / d).is_dir(), f"Missing directory: {d}"
```

### Changes Required

All changes in `tests/test_cli.py`:

#### 1. New template tests (FR-11, FR-12)

- [x] Add `TestNewTemplates` class with tests for:
  - `knowledge/KNOWLEDGE.md` (user-owned)
  - `modeling_project/ARCHITECTURE.md` (user-owned)
  - `modeling_project/REQUIREMENTS.md` (user-owned)
  - `modeling_project/VALIDATION_MATRIX.md` (user-owned)
  - `work/EPIC_GUIDE.md` (tool-owned)
  - `work/backlog/epic_template.md` (tool-owned)
- [x] Add test that user-owned new templates are skipped on re-init
- [x] Add test that tool-owned new templates are updated on re-init

#### 2. CSV test (FR-13)

- [x] Add `TestDataTemplates` class with test for `data/traceability_matrix.csv`
- [x] Assert file exists and header contains expected columns
- [x] Add test that CSV is skipped on re-init (user-owned)

#### 3. Directory structure test (FR-14)

- [x] Add `TestDirectoryStructure` class with test for all 16 directories
- [x] Assert each directory exists via `is_dir()`

### Validation

**Automated:**
- [x] `uv run pytest tests/test_cli.py -v` → 0 failures, 79 tests total
- [x] `uv run pytest tests/ -v` → 341 passed, 1 skipped, no regressions
- [x] `uv run ruff check tests/test_cli.py` → no new lint errors

**What We Know Works After This Phase:**
Full test coverage for the 4-directory architecture: all old paths updated, all new templates verified, directory structure validated, CSV installation confirmed.

---

## Environment Setup

See CLAUDE.md: `uv run pytest tests/test_cli.py -v` for targeted runs, `uv run pytest tests/` for full suite.

---

## Risk Management

**Phase-Specific Mitigations:**
- **Phase 1**: Run tests after each sub-group of fixes (SOURCE_INDEX, dev mode, modification detection, delete) to catch mistakes incrementally rather than all at once
- **Phase 2**: Each new test class is independent — if one fails, others still provide signal

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Updated 4 SOURCE_INDEX.md path assertions from root to `knowledge/SOURCE_INDEX.md`
- Updated `test_skips_source_index_if_exists_without_force` to pre-create at `knowledge/` (FR-9)
- Updated `test_overwrites_source_index_with_force` to pre-create at `knowledge/` (FR-2)
- Updated `test_dev_creates_symlinks_for_tool_templates` from `modeling_pm/` to `modeling_project/` (FR-4)
- Updated `test_dev_copies_user_owned_files` from root to `knowledge/SOURCE_INDEX.md` (FR-10)
- Updated `test_dev_updates_gitignore` from `modeling_pm/` to `modeling_project/` (FR-5)
- Updated `test_reinit_with_modification_prompts` from `modeling_pm/` to `modeling_project/` (FR-7)
- Updated `test_force_flag_skips_prompts` from `modeling_pm/` to `modeling_project/` (FR-8)
- Deleted `TestLocalGuide` class (2 tests) (FR-6)
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added `TestNewTemplates` class (8 tests): 6 existence checks + re-init skip/update tests (FR-11, FR-12)
- Added `TestDataTemplates` class (2 tests): CSV existence + re-init skip (FR-13)
- Added `TestDirectoryStructure` class (1 test): all 16 directories verified (FR-14)
**Issues:** None
**Deviations:** None. Final count: 79 tests (68 fixed + 11 new), all passing.

---

**Status**: Draft → In Progress → Complete

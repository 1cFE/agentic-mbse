# Spec: D1.7 Test Updates

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02
**Complexity:** LOW
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-001 (Architecture Redesign — Structure)

---

## Business Goals

### Why This Matters

D1.4 rewired `cmd_init()` to produce the new 4-directory structure (`knowledge/`, `modeling_project/`, `work/`, `data/`), replacing the old `modeling_pm/` layout. 9 tests in `tests/test_cli.py` now fail because they still assert old paths. Until these tests pass, the epic cannot be considered complete and D1.6 (fusion-tea migration) cannot proceed with confidence.

### Success Criteria

- [ ] `uv run pytest tests/test_cli.py` passes with 0 failures
- [ ] All new templates introduced in D1.1/D1.2 have test coverage
- [ ] CSV installation to `data/` has test coverage
- [ ] Full directory structure creation is verified

### Priority

P0 — blocks epic completion and D1.6.

---

## Problem Statement

### Current State

9 of 70 tests fail after D1.4's `cmd_init()` rewiring:

| # | Test | Failure Reason |
|---|------|----------------|
| 1 | `test_creates_source_index` | Asserts `SOURCE_INDEX.md` at root; now at `knowledge/SOURCE_INDEX.md` |
| 2 | `test_overwrites_source_index_with_force` | Pre-creates at root; init writes to `knowledge/` |
| 3 | `test_uses_current_directory_if_no_path` | Asserts `SOURCE_INDEX.md` at root |
| 4 | `test_dev_creates_symlinks_for_tool_templates` | Asserts `modeling_pm/MODELING_GUIDE.md`; now `modeling_project/` |
| 5 | `test_dev_updates_gitignore` | Asserts `modeling_pm/MODELING_GUIDE.md` in gitignore; now `modeling_project/` |
| 6 | `test_init_creates_local_guide` | `LOCAL_GUIDE.md` removed per D1.3 |
| 7 | `test_local_guide_skipped_if_exists` | `LOCAL_GUIDE.md` removed per D1.3 |
| 8 | `test_reinit_with_modification_prompts` | References `modeling_pm/MODELING_GUIDE.md`; path doesn't exist |
| 9 | `test_force_flag_skips_prompts` | References `modeling_pm/MODELING_GUIDE.md`; path doesn't exist |

Additionally, 6 new templates (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, EPIC_GUIDE.md, epic_template.md) and the CSV install have no test coverage.

### Desired Outcome

All tests pass and reflect the 4-directory architecture. New templates and data files have coverage.

---

## Scope

### In Scope

1. Fix 9 broken tests by updating path assertions
2. Delete `TestLocalGuide` class (2 tests for removed `LOCAL_GUIDE.md`)
3. Add tests for 6 new templates
4. Add test for `data/traceability_matrix.csv` installation
5. Add test for full directory structure creation (16 directories)
6. Update `test_dev_copies_user_owned_files` assertion from root `SOURCE_INDEX.md` to `knowledge/SOURCE_INDEX.md`

### Out of Scope

- Changes to `cmd_init()` or any production code
- Changes to templates themselves
- fusion-tea migration (D1.6)

### Edge Cases & Considerations

- `test_skips_source_index_if_exists_without_force` currently passes because it pre-creates the file at root and init skips it (the init doesn't find it at `knowledge/` so creates a new one). This test should be updated to use the correct path even though it happens to pass.

---

## Requirements

### Functional Requirements

> All requirements below are derived from the D1.7 deliverable definition in EPIC-ARCH-001.

1. **FR-1**: Fix `test_creates_source_index` — assert `knowledge/SOURCE_INDEX.md` exists
2. **FR-2**: Fix `test_overwrites_source_index_with_force` — pre-create at `knowledge/SOURCE_INDEX.md`, assert overwrite there
3. **FR-3**: Fix `test_uses_current_directory_if_no_path` — assert `knowledge/SOURCE_INDEX.md`
4. **FR-4**: Fix `test_dev_creates_symlinks_for_tool_templates` — assert `modeling_project/MODELING_GUIDE.md`
5. **FR-5**: Fix `test_dev_updates_gitignore` — assert `modeling_project/MODELING_GUIDE.md` and `modeling_project/MODELING_PROCESS.md` (not `modeling_pm/`)
6. **FR-6**: Delete `TestLocalGuide` class (`test_init_creates_local_guide`, `test_local_guide_skipped_if_exists`)
7. **FR-7**: Fix `test_reinit_with_modification_prompts` — use `modeling_project/MODELING_GUIDE.md`
8. **FR-8**: Fix `test_force_flag_skips_prompts` — use `modeling_project/MODELING_GUIDE.md`
9. **FR-9**: Fix `test_skips_source_index_if_exists_without_force` — pre-create at `knowledge/SOURCE_INDEX.md`
10. **FR-10**: Fix `test_dev_copies_user_owned_files` — assert `knowledge/SOURCE_INDEX.md` not symlink (not root)
11. **FR-11**: Add test for new user-owned templates (KNOWLEDGE.md at `knowledge/`, ARCHITECTURE.md/REQUIREMENTS.md/VALIDATION_MATRIX.md at `modeling_project/`)
12. **FR-12**: Add test for new tool-owned templates (EPIC_GUIDE.md at `work/`, epic_template.md at `work/backlog/`)
13. **FR-13**: Add test for `data/traceability_matrix.csv` installation
14. **FR-14**: Add test for full 16-directory structure creation

---

## Acceptance Criteria

### Core Functionality
- [ ] All 9 currently-failing tests pass after fixes
- [ ] `TestLocalGuide` class removed
- [ ] `test_skips_source_index_if_exists_without_force` updated to correct path
- [ ] `test_dev_copies_user_owned_files` updated to correct path

### New Coverage
- [ ] Test verifies KNOWLEDGE.md created at `knowledge/KNOWLEDGE.md`
- [ ] Test verifies ARCHITECTURE.md created at `modeling_project/ARCHITECTURE.md`
- [ ] Test verifies REQUIREMENTS.md created at `modeling_project/REQUIREMENTS.md`
- [ ] Test verifies VALIDATION_MATRIX.md created at `modeling_project/VALIDATION_MATRIX.md`
- [ ] Test verifies EPIC_GUIDE.md created at `work/EPIC_GUIDE.md`
- [ ] Test verifies epic_template.md created at `work/backlog/epic_template.md`
- [ ] Test verifies `data/traceability_matrix.csv` created with correct header
- [ ] Test verifies all 16 directories created by init

### Quality & Integration
- [ ] `uv run pytest tests/test_cli.py` — 0 failures
- [ ] `uv run pytest tests/` — no regressions in other test files

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-structure.md` (D1.7)
- **Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` § 1.9
- **Depends on:** D1.4 (`cmd_init()` rewiring) — complete
- **Design:** Not needed (straightforward test path updates)

---

**Next Steps:** Proceed directly to implementation (no design phase needed — changes are mechanical path updates and new assertions following existing test patterns).

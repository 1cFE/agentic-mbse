# Implementation Plan: D2.3 — Skill Registration

**Status:** Complete
**Created:** 2026-02-02
**Last Updated:** 2026-02-02

## Source Documents
- **Spec:** `.project/active/d2.3-skill-registration/spec.md`
- **Design:** N/A (LOW complexity — no design doc needed)

## Implementation Strategy

**Phasing Rationale:**
Test-first in Phase 1 to define "correct" for all 9 skills, then register in Phase 2 to make tests pass. Two phases because the test changes and registration changes are independent concerns, but they're small enough to land in a single commit.

**Overall Validation Approach:**
- Phase 1: new test assertions fail (6 missing skills detected)
- Phase 2: all tests pass after registration
- Final: full test suite + manual `init` verification

---

## Phase 1: Update Tests

### Goal
Define assertions for all 9 skills in both normal and dev mode tests. These will fail until Phase 2 completes.

### Test Stencil (Write This First)
```python
# In test_creates_skills_directory: assert all 9 skill dirs exist with SKILL.md
ALL_SKILLS = [
    "epic-decomposition", "model-validation", "project-structure",
    "python-debugger", "record-learning", "requirements-tracking",
    "source-traceability", "sysml-conventions", "toolkit-awareness",
]
skills_dir = tmp_path / ".claude" / "skills"
for skill in ALL_SKILLS:
    assert (skills_dir / skill).is_dir()
    assert (skills_dir / skill / "SKILL.md").exists()

# In test_dev_creates_symlinks_for_skills: assert all 9 are symlinks
for skill in ALL_SKILLS:
    skill_path = tmp_path / ".claude" / "skills" / skill
    assert skill_path.is_symlink()
    assert skill_path.is_dir()
```

### Changes Required

#### 1. `tests/test_cli.py:144-152` — `test_creates_skills_directory`
- [x] Replace single `python-debugger` assertion with loop over all 9 skills
- [x] Each skill dir must exist and contain `SKILL.md`

#### 2. `tests/test_cli.py:403-410` — `test_dev_creates_symlinks_for_skills`
- [x] Replace single `python-debugger` assertion with loop over all 9 skills
- [x] Each must be a symlink to a directory

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_cli.py::TestInit::test_creates_skills_directory -v` → FAILS (6 skills missing)
- [ ] `uv run pytest tests/test_cli.py::TestInit::test_dev_creates_symlinks_for_skills -v` → FAILS (6 skills missing)

**What We Know Works After This Phase:**
Tests correctly detect the registration gap.

---

## Phase 2: Register Skills

### Goal
Add 6 new skills to both installation paths so all 9 skills are installed.

### Changes Required

#### 1. `src/agentic_mbse/cli/__init__.py:40-44` — `MBSE_SKILLS`
- [x] Add 6 new entries, all 9 sorted alphabetically:
  ```python
  MBSE_SKILLS = [
      "epic-decomposition",
      "model-validation",
      "project-structure",
      "python-debugger",
      "record-learning",
      "requirements-tracking",
      "source-traceability",
      "sysml-conventions",
      "toolkit-awareness",
  ]
  ```

#### 2. `scripts/replicate_setup.sh:71` — skill loop
- [x] Update `for skill in ...` to list the same 9 skills alphabetically

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_cli.py -v` → All pass (including updated skill tests)
- [ ] `uv run pytest tests/` → Full suite passes, no regressions

**Manual:**
- [ ] `uv run agentic-mbse init /tmp/test-d23` → verify 9 dirs under `.claude/skills/`, each with `SKILL.md`
- [ ] `uv run agentic-mbse init --dev` on this repo → verify 9 symlinks under `.claude/skills/`
- [ ] Spot-check: `ls /tmp/test-d23/.claude/skills/sysml-conventions/references/` → `stencils.md` exists

**What We Know Works After This Phase:**
All 9 skills are registered and installed by both `cmd_init()` and `replicate_setup.sh`. Tests verify the full set.

---

## Risk Management

No significant risks. The `_install_directory()` helper already handles recursive directory copy/symlink — no new code paths needed.

## Implementation Notes

### Phase 1 & 2 Completion (combined — LOW complexity)
**Completed:** 2026-02-02
**Actual Changes:**
- Modified `tests/test_cli.py:144-160` — `test_creates_skills_directory` now loops over all 9 skills
- Modified `tests/test_cli.py:403-419` — `test_dev_creates_symlinks_for_skills` now loops over all 9 skills
- Modified `src/agentic_mbse/cli/__init__.py:40-50` — `MBSE_SKILLS` expanded to 9 entries (alphabetical)
- Modified `scripts/replicate_setup.sh:71-73` — skill loop expanded to 9 entries (alphabetical, line-wrapped)
**Issues:** None
**Deviations:** Combined both phases since all changes are trivial and independent

---

**Status**: Draft → In Progress → Complete

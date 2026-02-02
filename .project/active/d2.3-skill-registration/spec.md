# Spec: D2.3 — Skill Registration

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02T03:53:06Z
**Complexity:** LOW
**Branch:** revamp-architecture

---

## Business Goals

### Why This Matters

D2.1 created 6 new skills and D2.2 revised 2 existing skills, but none of the new skills are installed by `agentic-mbse init`. The `MBSE_SKILLS` list still contains only 3 entries (python-debugger, record-learning, toolkit-awareness). Target projects that run `agentic-mbse init` don't get the knowledge layer — the skills exist in the source tree but never reach users.

### Success Criteria

- [ ] `agentic-mbse init` installs all 9 skill directories to `.claude/skills/`
- [ ] `agentic-mbse init --dev` creates symlinks for all 9 skills
- [ ] `replicate_setup.sh` installs the same 9 skills
- [ ] Existing tests pass, updated to verify the full skill set

### Priority

P0 — this is the gate between "skills exist" and "skills are usable." Blocks Epic 3 (command refactoring) which depends on skills being available in target repos.

---

## Problem Statement

### Current State

`MBSE_SKILLS` in `src/agentic_mbse/cli/__init__.py` (line ~39) lists 3 skills:
```python
MBSE_SKILLS = [
    "python-debugger",
    "record-learning",
    "toolkit-awareness",
]
```

`scripts/replicate_setup.sh` (line ~70) mirrors the same 3:
```bash
for skill in python-debugger record-learning toolkit-awareness; do
```

6 new skill directories exist in `claude/skills/` but are not registered:
- `epic-decomposition`
- `model-validation`
- `project-structure`
- `requirements-tracking`
- `source-traceability`
- `sysml-conventions`

### Desired Outcome

Both installation paths register all 9 skills. Tests verify the full set.

---

## Scope

### In Scope

1. Update `MBSE_SKILLS` list in `src/agentic_mbse/cli/__init__.py`
2. Update skill loop in `scripts/replicate_setup.sh`
3. Update test assertions in `tests/test_cli.py` to verify all 9 skills are installed

### Out of Scope

- Skill content changes (completed in D2.1 and D2.2)
- Context window measurement (completed in D2.4)
- Command refactoring to reference skills (Epic 3)
- New test files or test infrastructure

### Edge Cases & Considerations

- Skills with `references/` subdirectories (sysml-conventions, python-debugger, toolkit-awareness) must have the entire directory tree copied/symlinked, not just SKILL.md. The existing `_install_directory()` helper already handles recursive directory copy, so no special handling is needed.
- Alphabetical ordering of the new skills in `MBSE_SKILLS` for readability (existing skills first for compatibility, new skills appended alphabetically — or all skills sorted alphabetically).

---

## Requirements

### Functional Requirements

> Requirements below are from the epic's D2.3 section and D2.4 measurement report unless marked [INFERRED].

1. **FR-1**: `MBSE_SKILLS` list MUST include all 9 skills: epic-decomposition, model-validation, project-structure, python-debugger, record-learning, requirements-tracking, source-traceability, sysml-conventions, toolkit-awareness
2. **FR-2**: `replicate_setup.sh` skill loop MUST match the `MBSE_SKILLS` list exactly
3. **FR-3**: `agentic-mbse init` MUST install all 9 skill directories (each containing at minimum SKILL.md) to `.claude/skills/`
4. **FR-4**: `agentic-mbse init --dev` MUST create symlinks for all 9 skill directories
5. **FR-5**: [INFERRED] Tests MUST be updated to verify all 9 skills are installed in both normal and dev modes

---

## Acceptance Criteria

### Core Functionality

- [ ] `MBSE_SKILLS` contains exactly 9 entries
- [ ] `replicate_setup.sh` skill loop iterates over the same 9 skill names
- [ ] Running `agentic-mbse init /tmp/test-project` creates 9 subdirectories under `.claude/skills/`, each with a `SKILL.md`
- [ ] Running `agentic-mbse init --dev` on the repo creates 9 symlinks under `.claude/skills/`
- [ ] Skills with `references/` subdirectories have those subdirectories installed

### Quality & Integration

- [ ] All existing tests pass (`uv run pytest tests/`)
- [ ] `test_creates_skills_directory` updated to verify all 9 skills
- [ ] `test_dev_creates_symlinks_for_skills` updated to verify all 9 skill symlinks

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-knowledge.md` (D2.3 section)
- **D2.4 Measurement Report:** `.project/active/d2.4-context-measurement/measurement-report.md`
- **Source code:** `src/agentic_mbse/cli/__init__.py` (MBSE_SKILLS, cmd_init)
- **Script:** `scripts/replicate_setup.sh`
- **Tests:** `tests/test_cli.py`

---

**Next Steps:** After approval, proceed to `/_my_design` (though given LOW complexity, this may go directly to `/_my_plan` or `/_my_implement`)

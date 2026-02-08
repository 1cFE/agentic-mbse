# Spec: D2.2 — Existing Skill Evaluation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02T02:33:26Z
**Complexity:** LOW
**Branch:** revamp-architecture

---

## Business Goals

### Why This Matters

D2.1 created 6 new skills following the new architecture (4-directory model, entity formats, cross-reference conventions). The two existing non-debugger skills — `toolkit-awareness` and `record-learning` — still reference stale paths (`modeling_pm/`), outdated tooling (`syside check`), and are missing awareness of new commands and project files. Until these skills are updated and their dispositions confirmed, D2.3 (registration) cannot finalize the `MBSE_SKILLS` list.

### Success Criteria

- [ ] `toolkit-awareness` accurately reflects the full command surface (CLI + slash commands) and the 4-directory architecture
- [ ] `record-learning` disposition is decided with clear rationale, and the skill is updated accordingly
- [ ] Both skills follow the patterns established by D2.1 (frontmatter format, body < 200 lines, knowledge-only content)
- [ ] No stale `modeling_pm/` paths remain in either skill

### Priority

P0 — on the critical path. D2.3 (registration) and D2.4 (measurement) depend on this deliverable being complete.

---

## Problem Statement

### Current State

**`toolkit-awareness`** (104 lines):
- References only the original slash commands (`/spec-model`, `/design-model`, `/plan-model`, `/implement-model`, `/audit-models`, `/research`, `/manage-sources`, `/backlog`)
- Missing 5 new slash commands: `/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`
- Missing PM CLI commands: `agentic-mbse status`, `agentic-mbse pm <operation>` (9 operations)
- Directory references point to pre-Epic 1 structure (no `knowledge/`, `modeling_project/`, `work/`, `data/` awareness)
- No mention of key project files (SOURCE_INDEX.md, KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, BACKLOG.md)

**`record-learning`** (156 lines):
- Writes to `modeling_pm/learnings/RAW_LEARNINGS.md` — stale path (should be `work/learnings/RAW_LEARNINGS.md`)
- References `syside check` for verification — should be `agentic-mbse validate`
- No scope boundary with the new `add-insight` mechanism (DI-XXX entries in KNOWLEDGE.md)
- No cross-suggestion of DI-XXX candidates when a learning has domain implications

### Desired Outcome

Both skills updated to match the architecture, with clear scope boundaries, correct paths, and complete command coverage. `record-learning` disposition confirmed and documented.

---

## Scope

### In Scope

- Revise `toolkit-awareness/SKILL.md` with new commands, paths, and project files
- Evaluate `record-learning` disposition and implement revisions
- Add DI-XXX cross-suggestion capability to `record-learning`
- Update all stale paths and tool references
- Document disposition rationale for `record-learning`

### Out of Scope

- Skill registration in `cmd_init()` or `replicate_setup.sh` (D2.3)
- Context window measurement (D2.4)
- Building the PM engine CLI commands referenced in `toolkit-awareness` (Epic 4)
- Command refactoring (Epic 3)
- Changes to `python-debugger` skill (unchanged per epic)

### Edge Cases & Considerations

- PM CLI commands (`agentic-mbse status`, `agentic-mbse pm <operation>`) do not exist yet (Epic 4). `toolkit-awareness` MUST include them as if they exist — pre-positioned for Epic 4. This is intentional: the skill describes the full planned command surface so it doesn't need another update when Epic 4 lands.
- `record-learning` currently has `user-invocable: true`. This MUST be preserved — it's the only user-invocable MBSE skill besides `python-debugger`.

---

## Requirements

### Functional Requirements

#### `toolkit-awareness` Revision

1. **FR-1**: Add new slash commands to the Slash Commands section: `/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`
2. **FR-2**: Add PM CLI commands section: `agentic-mbse status` (project status dashboard), `agentic-mbse pm <operation>` with all 9 operations (close-item, approve-research, trace-element, promote-requirement, register-decision, update-validation, add-insight, impact-query, supersede-insight)
3. **FR-3**: Update directory structure references to the 4-directory model (`knowledge/`, `modeling_project/`, `work/`, `data/`)
4. **FR-4**: Add key project files section listing files and their roles: `knowledge/SOURCE_INDEX.md`, `knowledge/KNOWLEDGE.md`, `modeling_project/ARCHITECTURE.md`, `modeling_project/REQUIREMENTS.md`, `modeling_project/VALIDATION_MATRIX.md`, `modeling_project/OVERVIEW.md`, `work/BACKLOG.md`, `data/traceability_matrix.csv`
5. **FR-5**: Preserve existing validation framework and Python environment sections (these are still accurate)
6. **FR-6**: Preserve `references/python-environment.md` reference
7. **FR-7**: Body MUST remain under 200 lines after additions

#### `record-learning` Revision

8. **FR-8**: Update file path from `modeling_pm/learnings/RAW_LEARNINGS.md` to `work/learnings/RAW_LEARNINGS.md` (all occurrences)
9. **FR-9**: Update `syside check` reference to `agentic-mbse validate`
10. **FR-10**: Add scope clarification section distinguishing process/tooling learnings (this skill) from domain insights (`add-insight` → `knowledge/KNOWLEDGE.md`)
11. **FR-11**: Add DI-XXX cross-suggestion: when a learning has domain implications (e.g., "this SysML limitation means we need a different modeling approach for X"), the skill SHOULD suggest creating a DI-XXX candidate via `add-insight` in addition to recording the process learning
12. **FR-12**: Preserve `user-invocable: true` and existing `allowed-tools: Read, Write, AskUserQuestion`
13. **FR-13**: Preserve existing learning categories, entry format, and example
14. **FR-14**: Body MUST remain under 200 lines after revisions

#### Documentation

15. **FR-15**: Document `record-learning` disposition rationale: KEEP with revisions, because process/tooling learnings (syntax gotchas, import patterns, parser behavior) serve a different audience and purpose than domain insights (DI-XXX). The two mechanisms are complementary, not overlapping.

---

## Acceptance Criteria

### `toolkit-awareness`

- [ ] Contains all 13 slash commands (8 existing + 5 new)
- [ ] Contains PM CLI section with `agentic-mbse status` and `agentic-mbse pm` with 9 operations
- [ ] All directory references use 4-directory paths (`knowledge/`, `modeling_project/`, `work/`, `data/`)
- [ ] Key project files section lists at least 8 files with their roles
- [ ] No stale `modeling_pm/` paths
- [ ] Body < 200 lines
- [ ] YAML frontmatter valid with all 4 fields

### `record-learning`

- [ ] All file path references point to `work/learnings/RAW_LEARNINGS.md`
- [ ] No references to `syside check` — uses `agentic-mbse validate`
- [ ] Scope clarification section distinguishes process learnings from domain insights
- [ ] DI-XXX cross-suggestion guidance present
- [ ] `user-invocable: true` preserved
- [ ] Body < 200 lines
- [ ] YAML frontmatter valid with all 4 fields

### Cross-Cutting

- [ ] Disposition rationale documented in implementation notes or plan
- [ ] No stale `modeling_pm/` paths in either skill
- [ ] Both skills contain knowledge only (no workflow logic, no agent prompts)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-knowledge.md` (D2.2 section)
- **D2.1 (predecessor):** `.project/active/d2.1-new-skills/plan.md` — establishes skill patterns
- **Design:** `.project/active/d2.2-existing-skill-eval/design.md` (to be created)
- **Architecture docs:** `.project/concepts/architecture-redesign/information-architecture.md`, `workflows.md`

---

**Next Steps:** After approval, proceed to `/_my_design`

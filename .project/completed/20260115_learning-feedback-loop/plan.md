# Implementation Plan: Learning Feedback Loop

**Status:** Complete
**Created:** 2026-01-15
**Last Updated:** 2026-01-15

## Source Documents

- **Design:** `.project/active/learning-feedback-loop/design.md` ← See here for skill content, entry format, data flow

## Implementation Strategy

**Phasing Rationale:**
1. Create skill first → immediately testable via `/record-learning`
2. Then integrate into init → new projects get it automatically
3. Finally validate end-to-end → both invocation paths work

**Overall Validation Approach:**
- Phase 1: Manual test of skill invocation
- Phase 2: Run `agentic-mbse init` and verify outputs
- Phase 3: Full workflow test in real session

---

## Phase 1: Create the Skill

### Goal

Create `claude/skills/record-learning/SKILL.md` with complete functionality for both user-triggered and agent-initiated learning capture.

### Changes Required

**See `design.md` for:**
- Full SKILL.md content → `design.md#skillmd-content`
- Entry format template → `design.md#entry-format`
- Learning categories → `design.md#learning-categories`
- Process for user-invoked vs agent-invoked → `design.md#process`

**Specific file changes:**

#### 1. Create Skill Directory
- [x] Create `claude/skills/record-learning/` directory

#### 2. Create SKILL.md
**File:** `claude/skills/record-learning/SKILL.md` (NEW)
- [x] Add YAML frontmatter with name, description, allowed-tools, user-invocable
- [x] Add "When to Use" section
- [x] Add "Process" section with user-invoked and agent-invoked paths
- [x] Add "Learning Categories" table
- [x] Add "Entry Format" template
- [x] Add "Example Recording"
- [x] Add "Guidelines" section

### Validation

**Manual:**
- [ ] In a Claude Code session, run `/record-learning`
- [ ] Verify: Skill loads and Claude begins reflection process
- [ ] Verify: Claude presents learning candidates (or says none found)
- [ ] Verify: AskUserQuestion used for approval

**What We Know Works After This Phase:**
- Skill file structure is correct
- Skill is discoverable via `/record-learning`
- Reflection and approval flow works

---

## Phase 2: Create Template & Update Init

### Goal

Create the RAW_LEARNINGS.md template and update `cmd_init()` to:
1. Add `record-learning` to MBSE_SKILLS list
2. Create `project/learnings/` directory
3. Install RAW_LEARNINGS.md template (user-owned)

### Changes Required

**See `design.md` for:**
- RAW_LEARNINGS.md initial content → `design.md#raw_learningsmd-initial-content`
- File ownership rules → `design.md#implementation-changes`

**Specific file changes:**

#### 1. Create Template
**File:** `project_templates/RAW_LEARNINGS.md.template` (NEW)
- [x] Create file with header content from design.md

#### 2. Update MBSE_SKILLS List
**File:** `src/agentic_mbse/cli/__init__.py:37-39`
- [x] Add `"record-learning"` to `MBSE_SKILLS` list

#### 3. Add to USER_OWNED_TEMPLATES
**File:** `src/agentic_mbse/cli/__init__.py:49-53`
- [x] Add `("RAW_LEARNINGS.md.template", "project/learnings/RAW_LEARNINGS.md")` to `USER_OWNED_TEMPLATES`

#### 4. Create Learnings Directory
**File:** `src/agentic_mbse/cli/__init__.py:519-524`
- [x] Add `(project_dir / "learnings").mkdir(exist_ok=True)` alongside other project subdirs

### Validation

**Automated:**
- [x] `uv run pytest tests/test_cli.py` → All pass (39 tests)
- [x] `uv run ruff check src/` → Passes (fixed import sorting)

**Manual:**
- [x] Create temp directory: `mkdir /tmp/test-init && cd /tmp/test-init`
- [x] Run: `uv run agentic-mbse init .`
- [x] Verify: `.claude/skills/record-learning/SKILL.md` exists
- [x] Verify: `project/learnings/RAW_LEARNINGS.md` exists with correct content
- [x] Verify: Re-running init skips RAW_LEARNINGS.md (user-owned)
- [x] Verify: Re-running init updates SKILL.md (tool-owned)

**What We Know Works After This Phase:**
- New projects get skill and learnings directory
- Existing projects can be updated via `agentic-mbse init`
- File ownership rules respected

---

## Phase 3: End-to-End Testing

### Goal

Validate complete workflow in real usage scenarios.

### Test Scenarios

#### Scenario A: User-Triggered Reflection
- [ ] Have a modeling conversation with some problem-solving
- [ ] Run `/record-learning`
- [ ] Verify: Claude reflects on conversation
- [ ] Verify: Claude presents learning candidates
- [ ] Approve one learning
- [ ] Verify: Entry appended to `project/learnings/RAW_LEARNINGS.md`
- [ ] Verify: Entry format matches template (timestamp, category, problem, solution, generalization)

#### Scenario B: Agent-Initiated (if naturally occurs)
- [ ] During modeling work, if agent discovers something noteworthy
- [ ] Verify: Agent invokes skill via Skill tool
- [ ] Verify: Agent presents for approval before recording
- [ ] Verify: User can veto

#### Scenario C: No Learnings Found
- [ ] Start fresh conversation
- [ ] Run `/record-learning` immediately
- [ ] Verify: Claude indicates no learnings found (graceful handling)

### What We Know Works After This Phase
- Complete user workflow functional
- Both invocation paths work correctly
- User approval required in all cases

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
# Run tests
uv run pytest tests/test_cli.py

# Lint
uv run ruff check src/

# Test init manually
mkdir /tmp/test-init && uv run agentic-mbse init /tmp/test-init
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Check skill frontmatter against existing `python-debugger` skill
- **Phase 2**: Follow exact pattern of existing project subdirectory creation (line 519-524)

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-01-15
**Actual Changes:**
- Created `claude/skills/record-learning/SKILL.md` with full content from design.md
- YAML frontmatter: name, description (with triggers), allowed-tools, user-invocable
- All sections: When to Use, Process (user/agent paths), Categories, Entry Format, Example, Guidelines

**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-01-15
**Actual Changes:**
- Created `project_templates/RAW_LEARNINGS.md.template`
- Added `"record-learning"` to `MBSE_SKILLS` list (line 39)
- Added template tuple to `USER_OWNED_TEMPLATES` (line 54)
- Added `(project_dir / "learnings").mkdir(exist_ok=True)` (line 527)
- Fixed pre-existing import sorting issue via `ruff check --fix`

**Issues:** None
**Deviations:** None

### Phase 3 Completion
**Completed:** 2026-01-15 (automated portions only)
**Notes:** Phase 3 is manual end-to-end testing that requires a real Claude Code session.
The automated validations (init creates files, re-init preserves user-owned) all pass.

Manual testing to be done by user:
- Run `/record-learning` in a real session
- Verify reflection, candidate presentation, and recording flow

---

**Status**: Complete (code implementation done, manual E2E testing pending)

# Implementation Plan: Rename `project/` to `modeling_pm/`

**Status:** Complete
**Created:** 2026-01-16
**Last Updated:** 2026-01-16

## Source Documents

- **Spec:** `.project/active/project-rename/spec.md`
- **Backlog:** `.project/backlog/BACKLOG.md` (ITEM-RENAME-001)

## Implementation Strategy

**Phasing Rationale:**
Start with source-of-truth files (CLI + script) that generate the directory, then update consumers (templates, docs, commands) in dependency order, and finally perform the physical rename.

**Overall Validation Approach:**
- Each phase uses targeted grep to verify changes
- Final validation confirms no stray `project/` references remain (excluding `.project/`)
- Test suite must pass after Phase 1

---

## Phase 1: Core Code Changes (CLI + Script)

### Goal
Update the two source files that generate the directory structure. These are the "source of truth" - everything else references what they create.

### Changes Required

#### 1. CLI Module
**File:** `src/agentic_mbse/cli/__init__.py`

- [x] Line 53: `"project/OVERVIEW.md"` → `"modeling_pm/OVERVIEW.md"`
- [x] Line 54: `"project/backlog/BACKLOG.md"` → `"modeling_pm/backlog/BACKLOG.md"`
- [x] Line 55: `"project/learnings/RAW_LEARNINGS.md"` → `"modeling_pm/learnings/RAW_LEARNINGS.md"`
- [x] Line 59: `"project/MODELING_GUIDE.md"` → `"modeling_pm/MODELING_GUIDE.md"`
- [x] Line 60: `"project/MODELING_PROCESS.md"` → `"modeling_pm/MODELING_PROCESS.md"`
- [x] Line 73: `"project/MODELING_GUIDE.md"` → `"modeling_pm/MODELING_GUIDE.md"`
- [x] Line 74: `"project/MODELING_PROCESS.md"` → `"modeling_pm/MODELING_PROCESS.md"`
- [x] Line 319: Comment about `project/` structure → `modeling_pm/`
- [x] Line 522: Comment `=== Create project/ structure ===` → `=== Create modeling_pm/ structure ===`

#### 2. Replicate Setup Script
**File:** `scripts/replicate_setup.sh`

- [x] Line 12: Comment update
- [x] Line 109-111: `mkdir -p "$REPO_ROOT/project/..."` → `"$REPO_ROOT/modeling_pm/..."`
- [x] Line 114: Log message update
- [x] Line 119-120: Path + log for MODELING_GUIDE.md
- [x] Line 123-124: Path + log for MODELING_PROCESS.md
- [x] Line 131: Path for OVERVIEW.md heredoc
- [x] Line 205: Log message update
- [x] Line 221: User instruction update

### Validation

**Automated:**
- [x] `uv run pytest tests/` → All tests pass (283 passed)
- [x] `grep -r "project/" src/agentic_mbse/cli/__init__.py | grep -v "\.project"` → No hits

**Manual:**
- [x] `uv run agentic-mbse init --help` → Runs without error
- [ ] (Optional) Test init in temp directory → Creates `modeling_pm/` not `project/`

**What We Know Works After This Phase:**
CLI and script will create `modeling_pm/` directory structure correctly.

---

## Phase 2: Documentation & Templates

### Goal
Update CLAUDE.md and all project_templates to reference `modeling_pm/`.

### Changes Required

#### 1. CLAUDE.md
**File:** `CLAUDE.md`

- [x] Line 89-92: Template output paths in list
- [x] Line 132-133: Directory clarification table
- [x] Line 136-137: "In short" summary

#### 2. Project Templates
**File:** `project_templates/OVERVIEW.md.template`
- [x] Line 74: Directory structure example

**File:** `project_templates/MODELING_PROCESS.md.template`
- [x] Lines 808-809: Related documents references

**File:** `project_templates/BACKLOG.md.template`
- [x] Line 13: Completed location
- [x] Lines 98-100: Related documents

**File:** `project_templates/README.md.template`
- [x] Lines 33-37: Documentation table
- [x] Lines 44, 48-50, 54-55: Getting started paths
- [x] Line 167: Directory structure example
- [x] Lines 206-211: Resources links

### Validation

**Automated:**
- [x] `grep -r "project/" CLAUDE.md | grep -v "\.project"` → No hits (only .project/ refs remain)
- [x] `grep -r "project/" project_templates/ | grep -v "\.project"` → No hits

**What We Know Works After This Phase:**
Documentation and templates are consistent with new naming.

---

## Phase 3: Claude Commands

### Goal
Update all command files referencing `project/` paths.

### Changes Required

**Files to update** (use `replace_all` for efficiency):

- [x] `claude/commands/research.md` - 7 occurrences
- [x] `claude/commands/onboard.md` - 14 occurrences
- [x] `claude/commands/audit-models.md` - 7 occurrences
- [x] `claude/commands/backlog.md` - 17 occurrences
- [x] `claude/commands/design-model.md` - 25 occurrences
- [x] `claude/commands/plan-model.md` - 9 occurrences
- [x] `claude/commands/implement-model.md` - 4 occurrences
- [x] `claude/commands/spec-model.md` - 17 occurrences

**Pattern:** Replace `project/` with `modeling_pm/` where it refers to the modeling PM directory (not `.project/`).

### Validation

**Automated:**
- [x] `grep -r "project/" claude/commands/ | grep -v "\.project"` → No hits

**What We Know Works After This Phase:**
All commands reference correct `modeling_pm/` paths.

---

## Phase 4: Claude Agents + Physical Rename

### Goal
Update agents and perform the physical directory rename.

### Changes Required

#### 1. Python Debugger Agent
**File:** `claude/agents/python-debugger.md`

- [x] Line 55: `project/agent_debug_scripts/` → `modeling_pm/agent_debug_scripts/`
- [x] Line 87: Path in example command
- [x] Line 159: Output location reference
- [x] Line 234: Example file path

#### 2. Physical Rename
- [x] `git mv project/ modeling_pm/`

### Validation

**Automated:**
- [x] `grep -r "project/" claude/agents/ | grep -v "\.project"` → No hits
- [x] `ls -d modeling_pm/` → Exists
- [x] `ls -d project/` → Does not exist

**Final Validation (All Phases):**
- [x] `grep -rn "project/" --include="*.py" --include="*.sh" --include="*.md" . | grep -v "\.project" | grep -v ".git"` → Only expected hits (historical research docs, external URLs)
- [x] `uv run pytest tests/` → All tests pass (283 passed, 1 skipped)
- [x] `uv run ruff check src/` → Pre-existing issues only (not related to rename)

**What We Know Works After This Phase:**
Complete rename is done. No stray `project/` path references remain.

---

## Environment Setup

Per CLAUDE.md:
```bash
uv run pytest tests/           # Run tests
uv run ruff check src/ tests/  # Linting
uv run ruff format src/ tests/ # Formatting
```

---

## Implementation Notes

*[TO BE FILLED DURING IMPLEMENTATION]*

### Phase 1 Completion
**Completed:** 2026-01-23
**Actual Changes:**
- Modified `src/agentic_mbse/cli/__init__.py`:
  - Updated `USER_OWNED_TEMPLATES` paths (OVERVIEW.md, BACKLOG.md, RAW_LEARNINGS.md)
  - Updated `TOOL_OWNED_TEMPLATES` paths (MODELING_GUIDE.md, MODELING_PROCESS.md)
  - Updated `DEV_MODE_GITIGNORE_PATHS` list
  - Updated `cmd_init()` comment and `modeling_pm_dir` variable
- Modified `scripts/replicate_setup.sh`:
  - Updated header comment
  - Updated `create_project_structure()` mkdir paths and log messages
  - Updated `create_overview_md()` output path and log message
  - Updated `print_summary()` user instructions
- Modified `tests/test_cli.py`:
  - Updated `test_dev_creates_symlinks_for_tool_templates` to expect `modeling_pm/`
  - Updated `test_dev_updates_gitignore` to expect `modeling_pm/`

**Issues:** None
**Deviations:** Added test file updates (not in original plan but necessary for tests to pass)

### Phase 2 Completion
**Completed:** 2026-01-23
**Actual Changes:**
- Modified `CLAUDE.md`:
  - Updated template output paths list (lines 89-92)
  - Updated directory clarification table (lines 132-133)
  - Updated "In short" summary (lines 136-137)
- Modified `project_templates/OVERVIEW.md.template`:
  - Updated directory structure example
- Modified `project_templates/MODELING_PROCESS.md.template`:
  - Updated related documents references
- Modified `project_templates/BACKLOG.md.template`:
  - Updated completed location path
  - Updated documentation references
- Modified `project_templates/README.md.template`:
  - Used `replace_all` to update all 17 occurrences of `project/` → `modeling_pm/`

**Issues:** None
**Deviations:** None

### Phase 3 Completion
**Completed:** 2026-01-23
**Actual Changes:**
- Modified 8 command files with `replace_all`:
  - `claude/commands/research.md` - 7 occurrences replaced
  - `claude/commands/onboard.md` - 14 occurrences replaced
  - `claude/commands/audit-models.md` - 7 occurrences replaced
  - `claude/commands/backlog.md` - 17 occurrences replaced
  - `claude/commands/design-model.md` - 25 occurrences replaced
  - `claude/commands/plan-model.md` - 9 occurrences replaced
  - `claude/commands/implement-model.md` - 4 occurrences replaced
  - `claude/commands/spec-model.md` - 17 occurrences replaced

**Issues:** None
**Deviations:** None

### Phase 4 Completion
**Completed:** 2026-01-23
**Actual Changes:**
- Modified `claude/agents/python-debugger.md` with `replace_all`
- Executed `git mv project/ modeling_pm/` to physically rename directory
- **Additional files discovered and updated:**
  - `README.md` (root) - 2 occurrences
  - `claude/skills/record-learning/SKILL.md` - 4 occurrences
  - `.claude/commands/*.md` (all 8 installed copies) - these are tracked copies for this repo's dev use
  - `.claude/agents/python-debugger.md` - installed copy
  - `docs/patterns/README.md` - 1 occurrence
  - `modeling_pm/MODELING_PROCESS.md` - actual generated file (not template)

**Issues:** None
**Deviations:**
- Discovered `.claude/` directory contains tracked copies of commands/agents (separate from `claude/` source)
- Updated additional files not in original plan (README.md, record-learning skill, docs/patterns/README.md)
- Left historical research docs and external URLs unchanged (appropriate)

---

**Status**: Complete

# Implementation Plan: D2.2 — Existing Skill Evaluation

**Status:** Complete
**Created:** 2026-02-02
**Last Updated:** 2026-02-02

## Source Documents
- **Spec:** `.project/active/d2.2-existing-skill-eval/spec.md`
- **Design:** `.project/active/d2.2-existing-skill-eval/design.md` ← See here for section structure, PM operations table, scope clarification content, change summary

## Implementation Strategy

**Phasing Rationale:**
Start with the surgical edits (`record-learning` — 4 replacements + 1 new section) to build confidence quickly, then tackle the larger extension (`toolkit-awareness` — new sections + restructured command list). Final phase validates both skills against all acceptance criteria. This mirrors D2.1's pattern of validating per-phase then running comprehensive checks at the end.

**Overall Validation Approach:**
- Each phase ends with body line count check and stale-path grep
- Phase 3 runs full automated validation suite + manual checklist
- `uv run pytest tests/` once at end (skills are markdown — zero Python impact expected)

---

## Phase 1: `record-learning` — Surgical Edits + New Section

### Goal
Fix stale paths/tools and add the scope clarification section. This is the smaller skill change, confirming the disposition decision (KEEP with revisions) before moving to the larger `toolkit-awareness` revision.

### Test Stencil (Write This First)

No pytest tests (markdown-only). Validation is structural:

```bash
# After editing, verify:
# 1. Body line count
awk '/^---$/{n++; next} n>=2' claude/skills/record-learning/SKILL.md | wc -l
# Target: < 200

# 2. No stale paths
grep -n 'modeling_pm/' claude/skills/record-learning/SKILL.md
# Should return nothing

# 3. No stale tools
grep -n 'syside check' claude/skills/record-learning/SKILL.md
# Should return nothing

# 4. user-invocable preserved
python3 -c "
import yaml
with open('claude/skills/record-learning/SKILL.md') as f:
    content = f.read()
fm = content.split('---')[1]
data = yaml.safe_load(fm)
assert data['user-invocable'] == True, 'user-invocable must be True'
print('OK:', data['name'], 'user-invocable:', data['user-invocable'])
"
```

### Changes Required

**See `design.md` for:**
- Path replacement locations → `design.md` § `record-learning/SKILL.md — Revised Structure`
- Scope clarification content → `design.md` § `New section: "Scope: Process Learnings vs Domain Insights"`
- Disposition rationale → `design.md` § `Disposition Rationale: record-learning`

**Specific file changes:**

#### 1. record-learning/SKILL.md
**File:** `claude/skills/record-learning/SKILL.md` (EDIT)

**Path replacements** (FR-8) — replace all 3 occurrences:
- [x] Line 50: `modeling_pm/learnings/RAW_LEARNINGS.md` → `work/learnings/RAW_LEARNINGS.md`
- [x] Line 80: `modeling_pm/learnings/RAW_LEARNINGS.md` → `work/learnings/RAW_LEARNINGS.md`
- [x] Line 146: `modeling_pm/learnings/RAW_LEARNINGS.md` → `work/learnings/RAW_LEARNINGS.md`

**Tool replacement** (FR-9):
- [x] Line 154: `syside check` → `uv run agentic-mbse validate`

**New section** (FR-10, FR-11):
- [x] Insert "## Scope: Process Learnings vs Domain Insights" section after "## When to Use" (after line 25)
- [x] Content: comparison table + cross-suggestion guidance (see `design.md` for exact content)

### Validation

**Automated:**
- [x] Body line count < 200 (154 lines)
- [x] No `modeling_pm/` references
- [x] No `syside check` references
- [x] `user-invocable: true` preserved in frontmatter

**Manual:**
- [x] Scope clarification table present with 4 comparison dimensions
- [x] Cross-suggestion subsection present with example
- [x] Existing learning categories, entry format, and example unchanged
- [x] `allowed-tools: Read, Write, AskUserQuestion` unchanged

**What We Know Works After This Phase:**
`record-learning` fully updated with correct paths, correct tool references, clear scope boundary, and DI-XXX cross-suggestion. Disposition confirmed as KEEP.

---

## Phase 2: `toolkit-awareness` — Extend with New Commands, PM Ops, Project Files

### Goal
Add the 5 new slash commands, PM CLI section, key project files section, and 4-directory architecture awareness. This is the larger change — extending a 93-body-line skill to ~165-175 lines.

### Test Stencil (Write This First)

```bash
# After editing, verify:
# 1. Body line count
awk '/^---$/{n++; next} n>=2' claude/skills/toolkit-awareness/SKILL.md | wc -l
# Target: < 200

# 2. All 14 slash commands present
for cmd in spec-model design-model plan-model implement-model audit-models research manage-sources backlog onboard quick-model review-model analyze-models status formalize-intent; do
  grep -q "/$cmd" claude/skills/toolkit-awareness/SKILL.md || echo "MISSING: /$cmd"
done

# 3. All 9 PM operations present
for op in close-item approve-research trace-element promote-requirement register-decision update-validation add-insight impact-query supersede-insight; do
  grep -q "$op" claude/skills/toolkit-awareness/SKILL.md || echo "MISSING: $op"
done

# 4. 4-directory paths present
for dir in knowledge/ modeling_project/ work/ data/; do
  grep -q "$dir" claude/skills/toolkit-awareness/SKILL.md || echo "MISSING: $dir"
done

# 5. No stale paths
grep -n 'modeling_pm/' claude/skills/toolkit-awareness/SKILL.md
# Should return nothing
```

### Changes Required

**See `design.md` for:**
- Section order → `design.md` § `toolkit-awareness/SKILL.md — Revised Structure`
- PM operations table → `design.md` § `PM CLI Operations (from architecture docs)`
- Frontmatter trigger phrases → `design.md` § `Frontmatter changes`
- Project files list → `design.md` § `New "Project Files" section`

**Specific file changes:**

#### 1. toolkit-awareness/SKILL.md
**File:** `claude/skills/toolkit-awareness/SKILL.md` (EDIT — significant extension)

**Frontmatter** (FR-1, FR-2):
- [x] Add trigger phrases to `description`: "PM operations", "project management", "agentic-mbse pm", "agentic-mbse status", "project files", "directory structure"

**"Before Answering Tooling Questions"** (FR-3):
- [x] Update authority sources to reference 4-directory architecture and key project files

**"CLI Tools"** (FR-2):
- [x] Add `agentic-mbse status` and `agentic-mbse pm <operation>` to CLI commands block

**New "PM Operations" subsection** (FR-2):
- [x] Add after CLI Tools section
- [x] Table with all 9 operations and one-line descriptions (from `design.md` PM operations table)
- [x] Preface with atomic/tolerant semantics note

**"Slash Commands"** (FR-1):
- [x] Replace hand-curated list with comprehensive table of all 14 commands
- [x] Group by function: Modeling workflow, Project management, Knowledge management

**New "Project Files" subsection** (FR-3, FR-4):
- [x] Add after Slash Commands section
- [x] Table with 8 key files, directory, and role

**Preserved sections** (FR-5, FR-6):
- [x] Validation Framework — no changes
- [x] Python Environment — no changes
- [x] Anti-Patterns — no changes
- [x] Reference Files — no changes

#### 2. references/python-environment.md
**File:** `claude/skills/toolkit-awareness/references/python-environment.md` (EDIT)
- [x] Line 20-21: Update `syside check` example to `agentic-mbse validate`

### Validation

**Automated:**
- [x] Body line count < 200 (151 lines)
- [x] All 14 slash commands present (test stencil script)
- [x] All 9 PM operations present (test stencil script)
- [x] 4-directory paths present (test stencil script)
- [x] No `modeling_pm/` references
- [x] No `syside check` references in either SKILL.md or references/ (remaining refs are in anti-pattern sections)

**Manual:**
- [x] PM operations table has correct operation names and descriptions
- [x] Project files table lists all 8 files with correct paths
- [x] Existing validation framework section unchanged
- [x] Existing Python environment section unchanged
- [x] `user-invocable: false` preserved

**What We Know Works After This Phase:**
`toolkit-awareness` fully updated with complete command surface, PM operations, project files, and 4-directory awareness.

---

## Phase 3: Cross-Cutting Validation

### Goal
Run full automated validation suite and verify both skills against all spec acceptance criteria. Matches D2.1's final validation pattern.

### Changes Required

No file changes. Validation only.

### Validation

**Automated** (from `design.md` § Validation Approach):
- [x] Body line counts < 200 for both skills (toolkit-awareness: 151, record-learning: 154)
- [x] YAML frontmatter validates for both skills (4 required fields each)
- [x] No `modeling_pm/` in either skill directory
- [x] No `syside check` in either skill directory (anti-pattern refs are intentional)
- [x] `uv run pytest tests/` passes (342 passed, 1 skipped)

**Manual — spec acceptance criteria:**

`toolkit-awareness`:
- [x] Contains all 14 slash commands (8 existing + 5 new + `/onboard`)
- [x] Contains PM CLI section with `agentic-mbse status` and 9 `pm` operations
- [x] All directory references use 4-directory paths
- [x] Key project files section lists 8+ files with roles
- [x] YAML frontmatter valid with all 4 fields

`record-learning`:
- [x] All file path references point to `work/learnings/RAW_LEARNINGS.md`
- [x] No `syside check` references
- [x] Scope clarification section present
- [x] DI-XXX cross-suggestion guidance present
- [x] `user-invocable: true` preserved
- [x] YAML frontmatter valid with all 4 fields

Cross-cutting:
- [x] Both skills contain knowledge only (no workflow logic, no agent prompts)
- [x] Disposition rationale documented (in `design.md` § Disposition Rationale)

**What We Know Works After This Phase:**
All spec acceptance criteria verified. Both skills aligned with new architecture. Existing tests unaffected. D2.2 complete — ready for D2.3 (registration) and D2.4 (measurement).

---

## Environment Setup

**See CLAUDE.md for full environment rules.**

No special setup needed — this deliverable is markdown-only. The only tool command is:
```bash
uv run pytest tests/   # Final regression check
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 1**: If `record-learning` exceeds 200 lines after adding scope section, trim the example recording (lines 111-142) — it's illustrative, not essential.
- **Phase 2**: If `toolkit-awareness` exceeds 200 lines, move PM operations table to `references/pm-operations.md` and add a one-line reference in SKILL.md. Budget analysis suggests this won't be needed (~165-175 lines).

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Replaced 3 occurrences of `modeling_pm/learnings/RAW_LEARNINGS.md` → `work/learnings/RAW_LEARNINGS.md` in `claude/skills/record-learning/SKILL.md`
- Replaced `syside check` → `uv run agentic-mbse validate` in Guidelines section
- Inserted "Scope: Process Learnings vs Domain Insights" section (with comparison table + cross-suggestion subsection) after "When to Use"
**Issues:** None
**Deviations:** None — all changes matched plan exactly

### Phase 2 Completion
**Completed:** 2026-02-02
**Actual Changes:**
- Added trigger phrases to frontmatter description: "PM operations", "project management", "agentic-mbse pm", "agentic-mbse status", "project files", "directory structure"
- Added bullet 3 to "Before Answering Tooling Questions" referencing 4-directory architecture
- Added `agentic-mbse status` and `agentic-mbse pm` to CLI Tools code block
- Added "PM Operations" subsection with 9-operation table and atomic/tolerant semantics note
- Replaced hand-curated slash command list with comprehensive 14-command table grouped by function (Modeling Workflow, Project Management, Knowledge Management)
- Added "Project Files" subsection with 8-file table showing directory and role
- Updated `references/python-environment.md` line 19-20: replaced `syside check` example with `agentic-mbse validate`
**Issues:** None
**Deviations:** None — final body line count (151) well within 200-line budget

### Phase 3 Completion (Validation)
**Completed:** 2026-02-02
**Validation Results:**
- Body line counts: toolkit-awareness 151, record-learning 154 (both < 200) ✓
- YAML frontmatter: both valid with all 4 required fields ✓
- No stale `modeling_pm/` paths in either skill directory ✓
- Remaining `syside check` references are all in anti-pattern/incorrect-usage sections (intentional) ✓
- `uv run pytest tests/` — 342 passed, 1 skipped ✓
- toolkit-awareness: all 14 commands, 9 PM ops, 4 directory paths present ✓
- record-learning: user-invocable true, scope section present, cross-suggestion present ✓
**Issues:** None

---

**Status**: Complete

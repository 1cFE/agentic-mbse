# Design: D2.2 — Existing Skill Evaluation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02T02:34:31Z
**Complexity:** LOW
**Branch:** revamp-architecture

---

## Overview

Revise `toolkit-awareness` and `record-learning` to align with the new architecture. Both are in-place edits to existing SKILL.md files with well-defined additions from the spec.

## Related Artifacts

- **Spec:** `.project/active/d2.2-existing-skill-eval/spec.md`
- **Epic:** `.project/backlog/epic_architecture-knowledge.md` (D2.2 section)
- **D2.1 patterns:** `.project/active/d2.1-new-skills/plan.md`
- **Architecture docs:** `.project/concepts/architecture-redesign/information-architecture.md`, `workflows.md`, `components.md`, `main.md`

---

## Research Findings

### Current File States

| File | Current Lines | Body Lines | Stale Paths | Stale Tools |
|------|-------------|------------|-------------|-------------|
| `claude/skills/toolkit-awareness/SKILL.md` | 104 | 93 | None (no `modeling_pm/`) | None |
| `claude/skills/toolkit-awareness/references/python-environment.md` | 42 | N/A | None | Has `syside check` in examples |
| `claude/skills/record-learning/SKILL.md` | 156 | 144 | 3 occurrences of `modeling_pm/` | 1 occurrence of `syside check` |

### D2.1 Patterns Observed

All 6 new skills follow this structure:
1. **Frontmatter**: `name`, `description` (with trigger phrases), `allowed-tools`, `user-invocable`
2. **Title heading**: `# Skill Name`
3. **Subtitle**: One-line description
4. **Core Principle**: 1-2 sentences establishing the key mental model
5. **When to Reference**: Bulleted list of commands that use this skill
6. **Content sections**: Tables, code blocks, concise prose
7. **Anti-Patterns**: `| Instead of | Do |` table
8. **Related Skills**: Cross-references using format `For {topic}, see the **{skill-name}** skill.`

### `toolkit-awareness` Structure Analysis

The current skill has a different structure from D2.1 skills — it lacks "Core Principle" and "When to Reference" (has "When This Skill Triggers" instead), and uses "Required Actions" framing. This is appropriate: `toolkit-awareness` is a meta-skill about tooling, not a domain knowledge skill. The structure should be **preserved and extended**, not restructured to match D2.1 patterns.

Specific additions needed:
- New slash commands (5): `/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`
- New PM CLI section with `agentic-mbse status` and `agentic-mbse pm <operation>` (9 operations)
- Key project files section (8 files with roles)
- 4-directory model awareness

**Budget**: Current body is 93 lines. Adding ~70-80 lines of new content pushes to ~165-175 lines — within the 200-line limit.

### `record-learning` Structure Analysis

The current skill has a clear process-oriented structure (user-invoked vs agent-invoked flows). Changes are surgical:
- 3 path replacements (`modeling_pm/` → `work/`)
- 1 tool replacement (`syside check` → `agentic-mbse validate`)
- 1 new section (scope clarification + DI-XXX cross-suggestion, ~20 lines)

**Budget**: Current body is 144 lines. Adding ~20 lines and changing a few existing lines pushes to ~164 lines — within the 200-line limit.

### PM CLI Operations (from architecture docs)

Operations sourced from `main.md:59-72` and `workflows.md`:

| Operation | One-Line Description |
|-----------|---------------------|
| `close-item <name>` | Archive completed work item from active to completed |
| `approve-research <file> --insights '<json>'` | Approve pending research and register domain insights |
| `trace-element --element <name> --file <path> ...` | Record model element traceability to matrix |
| `promote-requirement --requirement <text> --source <ID>` | Promote per-item requirement to project-wide PR-XXX |
| `register-decision --title <text> --decision <text> --rationale <text>` | Record architectural decision as AD-XXX |
| `update-validation <SV-XXX> --status <status>` | Update verification criterion status |
| `add-insight --title <text> --source <source> ...` | Capture domain insight as DI-XXX during work |
| `impact-query <ID>` | Find model elements affected by DI-XXX or PR-XXX change |
| `supersede-insight <DI-XXX> --new-insight '<json>' --reason '<text>'` | Replace domain insight and report impact |

---

## Proposed Design

### `toolkit-awareness/SKILL.md` — Revised Structure

The file is restructured into clear sections. Existing content is preserved; new content is added in logical positions.

**Section order** (preserving existing, inserting new):

```
[Frontmatter — update description to add new trigger phrases]
# Toolkit Awareness
## Core Principle                    [KEEP — unchanged]
## When This Skill Triggers          [KEEP — unchanged]
## Required Actions
### Before Answering Tooling Questions [KEEP — update authority sources]
### Validation Framework             [KEEP — unchanged]
### CLI Tools                        [KEEP — add PM commands]
### PM Operations (NEW)              [NEW — agentic-mbse pm <operation>]
### Slash Commands                   [KEEP — add 5 new commands]
### Project Files (NEW)              [NEW — 8 key files with roles]
### Python Environment               [KEEP — unchanged]
## Anti-Patterns to Avoid            [KEEP — unchanged]
## Reference Files                   [KEEP — unchanged]
```

**Frontmatter changes** (FR-1, FR-2):
- Add trigger phrases to `description`: "PM operations", "project management", "agentic-mbse pm", "agentic-mbse status", "project files", "directory structure"

**"Before Answering Tooling Questions" changes** (FR-3):
- Add bullet 1a: Read key project files section below for the 4-directory architecture

**"CLI Tools" changes** (FR-2):
- Add `agentic-mbse status` and `agentic-mbse pm` to the CLI commands block
- Keep existing `validate` and `--help` entries

**New "PM Operations" section** (FR-2):
- Table with operation name and one-line description (from research findings above)
- Prefaced with: "All PM operations are atomic (mutations succeed fully or not at all) or tolerant (queries return partial results with warnings)."
- Format: `uv run agentic-mbse pm <operation> [args]`

**"Slash Commands" changes** (FR-1):
- Replace the current hand-curated list with a comprehensive table of all 14 commands (8 existing + 5 new + `/onboard`)
- Format: `| Command | Purpose |` table
- Group by workflow function: Modeling workflow, Project management, Knowledge management

**New "Project Files" section** (FR-3, FR-4):
- Header: "Key project files in the 4-directory architecture"
- Table: `| File | Directory | Role |`
- Files: SOURCE_INDEX.md, KNOWLEDGE.md, OVERVIEW.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, BACKLOG.md, traceability_matrix.csv

**`references/python-environment.md` change**:
- Update `syside check` example to `agentic-mbse validate` (line 20-21 of current file)

### `record-learning/SKILL.md` — Revised Structure

Surgical edits to existing content plus one new section.

**Path replacements** (FR-8) — 3 occurrences:
- Line 50: `modeling_pm/learnings/RAW_LEARNINGS.md` → `work/learnings/RAW_LEARNINGS.md`
- Line 80: `modeling_pm/learnings/RAW_LEARNINGS.md` → `work/learnings/RAW_LEARNINGS.md`
- Line 146: `modeling_pm/learnings/RAW_LEARNINGS.md` → `work/learnings/RAW_LEARNINGS.md`

**Tool replacement** (FR-9) — 1 occurrence:
- Line 154: `syside check` → `uv run agentic-mbse validate`

**New section: "Scope: Process Learnings vs Domain Insights"** (FR-10, FR-11):

Insert after "## When to Use" section (after line 25). Content:

```markdown
## Scope: Process Learnings vs Domain Insights

This skill captures **process/tooling learnings** — discoveries about how to use the tools and language correctly. These are distinct from **domain insights**, which capture what the domain teaches us.

| | Process Learnings (this skill) | Domain Insights (`add-insight`) |
|---|---|---|
| **What** | SysML syntax, parser behavior, import patterns, workflow patterns | Domain facts, parameter values, design constraints from sources |
| **Where** | `work/learnings/RAW_LEARNINGS.md` | `knowledge/KNOWLEDGE.md` (as DI-XXX) |
| **Format** | Append-only, timestamped entries | Structured DI-XXX entities with status tracking |
| **Consumer** | Future modeling sessions, retrospectives | Model requirements, design decisions, traceability |

### Cross-Suggestion

When a learning has domain implications, **also suggest creating a DI-XXX entry**. Example: "This SysML limitation means we need a different modeling approach for thermal components" is both a process learning (SysML limitation) and a domain insight (modeling approach change). Record the process learning here, then suggest: "This also has domain implications — consider capturing a DI-XXX via `add-insight`."
```

**Frontmatter**: No changes needed. The `description` trigger phrases and `allowed-tools` are already correct.

### Change Summary

| File | Change Type | Lines Added | Lines Changed | Estimated Final Body |
|------|------------|-------------|---------------|---------------------|
| `toolkit-awareness/SKILL.md` | Restructure + extend | ~70-80 | ~10 | ~165-175 |
| `toolkit-awareness/references/python-environment.md` | Fix stale tool ref | 0 | 1 | N/A |
| `record-learning/SKILL.md` | Surgical edits + new section | ~20 | 4 | ~164 |

---

## Disposition Rationale: `record-learning`

**Decision**: KEEP with revisions.

**Rationale**: Process/tooling learnings and domain insights serve different purposes with different consumers:

1. **Different content**: Process learnings are about *how to use the tools* (syntax gotchas, import patterns, parser quirks). Domain insights are about *what the domain teaches us* (parameter values, design constraints, physical relationships).

2. **Different consumers**: Process learnings improve future modeling sessions (any project). Domain insights feed model requirements and design decisions (this project).

3. **Different lifecycle**: Process learnings are append-only raw notes for retrospective mining. Domain insights are structured, tracked entities (DI-XXX) with status, supersession, and impact queries.

4. **Complementary, not overlapping**: The `add-insight` mechanism captures domain knowledge during any command. `record-learning` captures tooling knowledge. The cross-suggestion feature (FR-11) bridges the two when a single discovery has both process and domain implications.

---

## Potential Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| `toolkit-awareness` exceeds 200 body lines after additions | Low | Budget analysis shows ~165-175 lines. If tight, move PM operations to `references/pm-operations.md` |
| PM CLI commands don't match final Epic 4 implementation | Low | Acceptable — toolkit-awareness describes the planned surface. Epic 4 may refine operation signatures, requiring a minor update |
| `record-learning` scope boundary is unclear to users | Low | The comparison table makes it explicit. Cross-suggestion bridges ambiguous cases |

---

## Validation Approach

### Automated Checks

```bash
# Body line counts (both must be < 200)
for skill in toolkit-awareness record-learning; do
  lines=$(awk '/^---$/{n++; next} n>=2' claude/skills/$skill/SKILL.md | wc -l)
  echo "$skill: $lines body lines"
done

# YAML frontmatter validation
for skill in toolkit-awareness record-learning; do
  python3 -c "
import yaml
with open('claude/skills/$skill/SKILL.md') as f:
    content = f.read()
fm = content.split('---')[1]
data = yaml.safe_load(fm)
assert 'name' in data and 'description' in data
assert 'allowed-tools' in data and 'user-invocable' in data
print('$skill OK:', data['name'], 'user-invocable:', data['user-invocable'])
"
done

# Stale path check
grep -rn 'modeling_pm/' claude/skills/toolkit-awareness/ claude/skills/record-learning/
# Should return nothing

# Stale tool check
grep -rn 'syside check' claude/skills/toolkit-awareness/ claude/skills/record-learning/
# Should return nothing

# Existing tests still pass
uv run pytest tests/
```

### Manual Verification

- [ ] `toolkit-awareness` lists all 14 slash commands (8 original + 5 new + `/onboard`)
- [ ] `toolkit-awareness` lists `agentic-mbse status` and all 9 `pm` operations
- [ ] `toolkit-awareness` mentions all 8 key project files with correct paths
- [ ] `toolkit-awareness` references 4-directory architecture
- [ ] `record-learning` has `user-invocable: true`
- [ ] `record-learning` scope clarification table present
- [ ] `record-learning` cross-suggestion guidance present
- [ ] Both skills contain knowledge only (no workflow logic)

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement` (given LOW complexity, direct implementation may be appropriate)

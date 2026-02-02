# Implementation Plan: D2.1 — New Skills (6 Skills)

**Status:** Draft
**Created:** 2026-02-02
**Last Updated:** 2026-02-02

## Source Documents
- **Spec:** `.project/active/d2.1-new-skills/spec.md`
- **Design:** `.project/active/d2.1-new-skills/design.md` ← See here for template structure, section outlines, cross-reference map, overlap resolution

## Implementation Strategy

**Phasing Rationale:**
Front-load the largest/riskiest skill (`sysml-conventions`) to validate the template at scale. Then batch extraction-heavy skills (Phase 2), tackle the most distributed extraction (Phase 3), and finish with primarily-new-content skills (Phase 4). Each phase validates a different risk dimension: size limits, extraction quality, distributed source coherence, and authoring judgment.

**Overall Validation Approach:**
- Each phase ends with line count check (body < 200 lines) and content boundary review
- Cross-reference integrity checked incrementally (only references to skills that exist so far)
- Final validation in Phase 4 covers all acceptance criteria from `spec.md`
- `uv run pytest tests/` run once at end (skills are markdown — zero Python impact expected)

---

## Phase 1: `sysml-conventions` (Riskiest Skill)

### Goal
Write the largest skill with the most extraction sources. Validates that the template works at scale and the `references/` escape valve keeps SKILL.md under 200 body lines. This skill is the foundation — 3 other skills cross-reference it.

### Test Stencil (Write This First)

No pytest tests for skills (markdown-only deliverable). Validation is structural:

```bash
# After writing, verify:
# 1. Body line count (everything after closing ---)
awk '/^---$/{n++; next} n>=2' claude/skills/sysml-conventions/SKILL.md | wc -l
# Target: < 200

# 2. YAML frontmatter parses
python3 -c "
import yaml
with open('claude/skills/sysml-conventions/SKILL.md') as f:
    content = f.read()
fm = content.split('---')[1]
data = yaml.safe_load(fm)
assert data['name'] == 'sysml-conventions'
assert 'description' in data
assert data['user-invocable'] == False
print('Frontmatter OK:', list(data.keys()))
"

# 3. No stale paths
grep -n 'modeling_pm/' claude/skills/sysml-conventions/SKILL.md
# Should return nothing
```

### Changes Required

**See `design.md` for:**
- Section structure → `design.md` § Skill-by-Skill Design, skill #1
- Cross-references → `design.md` § Cross-Reference Map (sysml-conventions → source-traceability, sysml-conventions → project-structure)
- Overlap boundaries → `design.md` § Content Overlap Resolution (doc comments: FORMAT here, CONTENT in source-traceability; ADR-002: RULE here, FILE STRUCTURE in project-structure)

**Content sources to read and extract from:**
- [ ] `claude/commands/design-model.md` lines ~580-643 (common pitfalls)
- [ ] `claude/commands/implement-model.md` lines ~163-177 (pre-flight syntax, doc comment template)
- [ ] `claude/commands/plan-model.md` lines ~155-175 (ADR-002, constraint/import/binding patterns)
- [ ] `project_templates/MODELING_GUIDE.md.template` lines 107-152 (standard imports, key syntax — `<!-- SKILL: moves to sysml-conventions -->`)
- [ ] `project_templates/MODELING_GUIDE.md.template` lines 264-283 (pattern documentation index — `<!-- SKILL: moves to sysml-conventions -->`)

**Specific file changes:**

#### 1. SKILL.md
**File:** `claude/skills/sysml-conventions/SKILL.md` (NEW)
- [ ] Create directory `claude/skills/sysml-conventions/`
- [ ] Write SKILL.md with frontmatter (`name`, `description` with trigger phrases, `allowed-tools: Read, Grep, Glob`, `user-invocable: false`)
- [ ] Sections per design: Core Principle, When to Reference, Naming Conventions, Definition vs Usage Rule, Calculation Architecture (ADR-002), Standard Imports, Doc Comment Format, Common Pitfalls, Key Syntax Patterns, Anti-Patterns, Related Skills
- [ ] Include cross-refs to source-traceability and project-structure per design cross-reference map
- [ ] Verify body ≤ 200 lines — if exceeding, move code stencils and pattern index to references/

#### 2. references/stencils.md
**File:** `claude/skills/sysml-conventions/references/stencils.md` (NEW)
- [ ] Create directory `claude/skills/sysml-conventions/references/`
- [ ] Write code stencils: part def, calc def, constraint def, connection def
- [ ] Write pattern documentation index (pointer to `docs/patterns/` files)
- [ ] Add "Reference Files" section to SKILL.md pointing here

### Validation

**Automated:**
- [ ] Body line count < 200 (awk command above)
- [ ] YAML frontmatter parses correctly (python3 command above)
- [ ] No `modeling_pm/` references (grep command above)

**Manual:**
- [ ] All 7 MUST-include topics from spec FR-4.1 are covered: naming, def/usage separation, imports, syntax patterns, pitfalls, ADR-002, doc comment format
- [ ] SHOULD-include items (stencils, pattern index) are in references/
- [ ] Content is knowledge only — no workflow logic, no project-specific data, no agent prompts
- [ ] Cross-references use standard phrase format from design
- [ ] Trigger phrases in `description` match design list

**What We Know Works After This Phase:**
Template validated at maximum scale. references/ subdirectory pattern established. The hardest skill is done.

---

## Phase 2: `model-validation` + `project-structure`

### Goal
Write two medium-complexity skills that are primarily extraction-heavy. Validates the template for extraction-focused skills and confirms the ADR-002 overlap split works in practice (rule in sysml-conventions, file structure in project-structure).

### Test Stencil

```bash
# Repeat for each skill:
for skill in model-validation project-structure; do
  echo "=== $skill ==="
  awk '/^---$/{n++; next} n>=2' claude/skills/$skill/SKILL.md | wc -l
  python3 -c "
import yaml
with open('claude/skills/$skill/SKILL.md') as f:
    content = f.read()
fm = content.split('---')[1]
data = yaml.safe_load(fm)
assert data['name'] == '$skill', f'name mismatch: {data[\"name\"]}'
assert data['user-invocable'] == False
print('OK:', list(data.keys()))
"
  grep -c 'modeling_pm/' claude/skills/$skill/SKILL.md || echo "No stale paths"
done
```

### Changes Required

**See `design.md` for:**
- model-validation section structure → `design.md` § skill #2
- project-structure section structure → `design.md` § skill #3
- Cross-references → `design.md` § Cross-Reference Map
- ADR-002 overlap → `design.md` § Content Overlap Resolution

**Content sources for `model-validation`:**
- [ ] `claude/commands/design-model.md` lines ~645-811 (quality pyramid, validation checkpoints)
- [ ] `claude/commands/implement-model.md` lines ~145-349 (parse validation, quality validation, regression testing)
- [ ] `claude/commands/plan-model.md` lines ~146-220 (feasibility validation, prototype baseline)
- [ ] `claude/commands/audit-models.md` lines ~30-234 (verification standards, thresholds)
- [ ] `claude/commands/spec-model.md` lines ~119-149 (evaluatable success criteria)
- [ ] `project_templates/MODELING_GUIDE.md.template` lines 167-232 (regression testing — `<!-- SKILL: moves to model-validation -->`)

**Content sources for `project-structure`:**
- [ ] `claude/commands/design-model.md` lines ~132-147 (library vs designs)
- [ ] `claude/commands/implement-model.md` lines ~105-144 (parallel vs sequential, batch validation)
- [ ] `claude/commands/spec-model.md` lines ~14-43 (models README)
- [ ] `claude/commands/plan-model.md` lines ~70-143 (phasing principles, library before instances)
- [ ] `claude/commands/onboard.md` lines ~115-119, 224-245, 283-289 (directory state, project structure)
- [ ] `project_templates/MODELING_GUIDE.md.template` lines 28-43 (EXPOSE pattern — `<!-- SKILL: moves to project-structure -->`)
- [ ] `.project/concepts/architecture-redesign/information-architecture.md` § 2 (4-directory model)
- [ ] `.project/concepts/architecture-redesign/information-architecture.md` § 3 Role 3 (intent formalization)

**Specific file changes:**

#### 1. model-validation/SKILL.md
**File:** `claude/skills/model-validation/SKILL.md` (NEW)
- [ ] Create directory `claude/skills/model-validation/`
- [ ] Write SKILL.md with frontmatter (`allowed-tools: Read, Grep, Glob, Bash`)
- [ ] Sections per design: Core Principle, When to Reference, 8-Level Validation Pyramid, CLI Invocation, When to Validate, Verification Thresholds, Reading Validation Output, Regression Testing, Anti-Patterns, Related Skills
- [ ] Include cross-ref to toolkit-awareness per design cross-reference map

#### 2. project-structure/SKILL.md
**File:** `claude/skills/project-structure/SKILL.md` (NEW)
- [ ] Create directory `claude/skills/project-structure/`
- [ ] Write SKILL.md with frontmatter (`allowed-tools: Read, Grep, Glob`)
- [ ] Sections per design: Core Principle, When to Reference, The 4-Directory Model, Key Project Files, Model File Organization, Library vs Designs Separation, Cross-File Dependencies, EXPOSE Pattern, Intent Formalization, Anti-Patterns, Related Skills
- [ ] Include cross-ref to sysml-conventions per design cross-reference map

### Validation

**Automated:**
- [ ] Body line count < 200 for each
- [ ] YAML frontmatter parses for each
- [ ] No `modeling_pm/` references
- [ ] `model-validation` has `Bash` in allowed-tools; `project-structure` does not

**Manual:**
- [ ] `model-validation` covers 6 MUST-include topics from spec FR-4.2
- [ ] `project-structure` covers 7 MUST-include topics from spec FR-4.3
- [ ] ADR-002 split is clean: sysml-conventions has the rule/expression taxonomy, project-structure has the file structure consequence (library/analyses/)
- [ ] Content boundaries respected (no workflow logic)

**What We Know Works After This Phase:**
3 of 6 skills complete. Template validated for extraction-heavy and mixed-content skills. ADR-002 overlap confirmed clean.

---

## Phase 3: `source-traceability`

### Goal
Write the most widely-distributed extraction skill — content pulled from 6 commands + 2 architecture documents. Validates that extracting small sections from many sources produces a coherent, self-contained skill. Also confirms the doc comment overlap split with sysml-conventions works bidirectionally.

### Test Stencil

```bash
awk '/^---$/{n++; next} n>=2' claude/skills/source-traceability/SKILL.md | wc -l
python3 -c "
import yaml
with open('claude/skills/source-traceability/SKILL.md') as f:
    content = f.read()
fm = content.split('---')[1]
data = yaml.safe_load(fm)
assert data['name'] == 'source-traceability'
assert data['user-invocable'] == False
print('OK:', list(data.keys()))
"
grep -c 'modeling_pm/' claude/skills/source-traceability/SKILL.md || echo "No stale paths"
```

### Changes Required

**See `design.md` for:**
- Section structure → `design.md` § skill #4
- Cross-references → `design.md` § Cross-Reference Map (source-traceability → sysml-conventions)
- Doc comment overlap → `design.md` § Content Overlap Resolution (CONTENT here, FORMAT in sysml-conventions)

**Content sources:**
- [ ] `claude/commands/design-model.md` lines ~293-315, 356-379, 461-512, 889-934
- [ ] `claude/commands/implement-model.md` lines ~190-222
- [ ] `claude/commands/spec-model.md` lines ~78-82, 283-293
- [ ] `claude/commands/audit-models.md` lines ~108-137, 271-301
- [ ] `claude/commands/research.md` lines ~51-58, 113-129, 161-223
- [ ] `claude/commands/manage-sources.md` lines ~49-320
- [ ] `.project/concepts/architecture-redesign/information-architecture.md` § 5 (traceability model)
- [ ] `docs/source-index.md` (SOURCE_INDEX format guide)

**Specific file changes:**

#### 1. source-traceability/SKILL.md
**File:** `claude/skills/source-traceability/SKILL.md` (NEW)
- [ ] Create directory `claude/skills/source-traceability/`
- [ ] Write SKILL.md with frontmatter (`allowed-tools: Read, Grep, Glob`)
- [ ] Sections per design: Core Principle, When to Reference, The Durable Traceability Chain, SOURCE_INDEX.md Format, Doc Comment Content Requirements, Citation Patterns, Traceability Matrix Schema, When to Record Traceability, Anti-Patterns, Related Skills
- [ ] Include cross-ref to sysml-conventions per design cross-reference map

### Validation

**Automated:**
- [ ] Body line count < 200
- [ ] YAML frontmatter parses
- [ ] No `modeling_pm/` references

**Manual:**
- [ ] Covers 6 MUST-include topics from spec FR-4.4
- [ ] SHOULD-include items covered (source type taxonomy, confidence assessment)
- [ ] Doc comment split is clean: sysml-conventions has FORMAT (syntax, field list), this skill has CONTENT (what fields must contain, citation patterns)
- [ ] Verify cross-ref to sysml-conventions reads naturally from this side

**What We Know Works After This Phase:**
4 of 6 skills complete. Distributed extraction validated. All bidirectional cross-references in place (sysml-conventions ↔ source-traceability, sysml-conventions ↔ project-structure).

---

## Phase 4: `epic-decomposition` + `requirements-tracking` + Final Validation

### Goal
Write the two primarily-new-content skills (80% and 75% from architecture docs), then run comprehensive validation across all 6 skills against every acceptance criterion in the spec.

### Test Stencil

```bash
# Per-skill checks
for skill in epic-decomposition requirements-tracking; do
  echo "=== $skill ==="
  awk '/^---$/{n++; next} n>=2' claude/skills/$skill/SKILL.md | wc -l
  python3 -c "
import yaml
with open('claude/skills/$skill/SKILL.md') as f:
    content = f.read()
fm = content.split('---')[1]
data = yaml.safe_load(fm)
assert data['name'] == '$skill'
assert data['user-invocable'] == False
print('OK:', list(data.keys()))
"
  grep -c 'modeling_pm/' claude/skills/$skill/SKILL.md || echo "No stale paths"
done

# Full validation across all 6
echo "=== All 6 skills ==="
for skill in sysml-conventions model-validation project-structure source-traceability epic-decomposition requirements-tracking; do
  lines=$(awk '/^---$/{n++; next} n>=2' claude/skills/$skill/SKILL.md | wc -l)
  echo "$skill: $lines body lines"
done

# Existing tests still pass
uv run pytest tests/
```

### Changes Required

**See `design.md` for:**
- epic-decomposition section structure → `design.md` § skill #5
- requirements-tracking section structure → `design.md` § skill #6
- Cross-references → `design.md` § Cross-Reference Map (epic-decomposition → requirements-tracking, requirements-tracking → source-traceability)

**Content sources for `epic-decomposition`:**
- [ ] `.project/concepts/architecture-redesign/workflows.md` § 2.1 (scale taxonomy)
- [ ] `.project/concepts/architecture-redesign/workflows.md` § 3.6 (epic tracking)
- [ ] `project_templates/EPIC_GUIDE.md.template` (Goldilocks principle, decomposition process, anti-patterns)
- [ ] `claude/commands/backlog.md` lines ~54-87 (work item extraction, scope sizing)
- [ ] `claude/commands/spec-model.md` lines ~29-31 (epic context)

**Content sources for `requirements-tracking`:**
- [ ] `.project/concepts/architecture-redesign/information-architecture.md` § 3 Role 4 (two-tier, PR-XXX format)
- [ ] `.project/concepts/architecture-redesign/workflows.md` § 3.5 (close flow triggers)
- [ ] `claude/commands/spec-model.md` lines ~101-149 (MR-XXX, EARS format)
- [ ] `claude/commands/implement-model.md` lines ~366-421 (acceptance criteria, completion gates)
- [ ] `claude/commands/backlog.md` lines ~86-151 (status tracking, priority, completion)

**Specific file changes:**

#### 1. epic-decomposition/SKILL.md
**File:** `claude/skills/epic-decomposition/SKILL.md` (NEW)
- [ ] Create directory `claude/skills/epic-decomposition/`
- [ ] Write SKILL.md with frontmatter (`allowed-tools: Read, Grep, Glob`)
- [ ] Sections per design: Core Principle, When to Reference, Scale Taxonomy, Goldilocks Indicators, Decomposition Process, Epic File Structure, Anti-Patterns, Related Skills
- [ ] Include cross-ref to requirements-tracking per design cross-reference map

#### 2. requirements-tracking/SKILL.md
**File:** `claude/skills/requirements-tracking/SKILL.md` (NEW)
- [ ] Create directory `claude/skills/requirements-tracking/`
- [ ] Write SKILL.md with frontmatter (`allowed-tools: Read, Grep, Glob`)
- [ ] Sections per design: Core Principle, When to Reference, Two-Tier Requirements, PR-XXX Entity Format, Requirement Sub-Types, Promotion Path: MR-XXX → PR-XXX, Enforcement Methods, Compliance Checking, EARS Format Reference, Anti-Patterns, Related Skills
- [ ] Include cross-ref to source-traceability per design cross-reference map

### Validation

**Automated:**
- [ ] Body line count < 200 for each new skill
- [ ] YAML frontmatter parses for each
- [ ] No `modeling_pm/` references in any skill
- [ ] `uv run pytest tests/` passes (regression check)

**Manual — per-skill content completeness (spec acceptance criteria):**
- [ ] `epic-decomposition` covers: scale taxonomy, Goldilocks indicators, decomposition process, anti-patterns, epic file structure
- [ ] `requirements-tracking` covers: two-tier structure, PR-XXX format, promotion path, enforcement methods, compliance checking

**Manual — cross-cutting acceptance criteria:**
- [ ] All 6 directories exist in `claude/skills/`
- [ ] All SKILL.md files have valid frontmatter with all 4 fields
- [ ] All body line counts < 200
- [ ] `sysml-conventions` has `references/` subdirectory
- [ ] All skills use Epic 1 paths (`knowledge/`, `modeling_project/`, `work/`, `data/`)
- [ ] No skill contains workflow logic, project-specific data, or agent prompts
- [ ] `MODELING_GUIDE.md.template` `<!-- SKILL: moves to ... -->` content incorporated (3× sysml-conventions, 1× project-structure, 1× model-validation)
- [ ] Each `description` field includes trigger phrases from design
- [ ] `allowed-tools` minimal and correct (only `model-validation` has Bash)
- [ ] No duplicate content between skills (cross-references used instead)
- [ ] All 7 cross-references from design cross-reference map are present
- [ ] Cross-references use standard phrase: "For {topic}, see the **{skill-name}** skill."

**What We Know Works After This Phase:**
All 6 skills complete. All spec acceptance criteria verified. Existing tests unaffected.

---

## Environment Setup

**See CLAUDE.md for full environment rules.**

No special setup needed — this deliverable is markdown-only. The only tool command is:
```bash
uv run pytest tests/   # Final regression check
```

---

## Risk Management

**See `design.md` § Potential Risks for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 1**: If `sysml-conventions` exceeds 200 body lines, aggressively move code stencils and pattern index to `references/stencils.md`. Keep SKILL.md to principles, rules, and tables only.
- **Phase 2**: If ADR-002 overlap feels awkward, revisit the split boundary — the design's resolution is a starting point, not a constraint.
- **Phase 3**: If distributed extraction produces a disjointed skill, restructure around the traceability chain narrative rather than mirroring source command structure.
- **Phase 4**: New-content skills may need multiple drafts to hit the right abstraction level. Use EPIC_GUIDE.md.template as the primary source for `epic-decomposition` tone and content density.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 2 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 4 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

---

**Status**: Draft → In Progress → Complete

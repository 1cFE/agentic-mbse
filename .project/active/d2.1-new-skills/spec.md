# Spec: D2.1 — New Skills (6 Skills)

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02T01:34:57Z
**Complexity:** MEDIUM
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-002 (Architecture Redesign — Knowledge)

---

## Business Goals

### Why This Matters

Commands are too long because they embed shared knowledge inline (P1). `design-model.md` is 1,345 lines — analysis shows ~600 lines of SysML patterns, ~200 lines of validation guidance, ~150 lines of file structure rules, ~100 lines of citation/source patterns. The remaining 8 commands average 443 lines with similar embedded knowledge across 4,887 total lines.

Skills are the **knowledge contracts** between the information architecture (Epic 1) and the commands (Epic 3). Without skills, Epic 3's command refactoring would just be rearranging the same inline content. With skills, commands can reference shared knowledge concisely, reducing average length from 543 to ~250 lines.

### Success Criteria

- [ ] 6 new skill directories exist in `claude/skills/` with correct structure
- [ ] Each SKILL.md is under 200 lines with correct YAML frontmatter
- [ ] Skills contain ONLY knowledge (no workflow logic, no project-specific data)
- [ ] Skills reference Epic 1's directory paths (`knowledge/`, `modeling_project/`, `work/`, `data/`)
- [ ] Content sources are identified for each skill (extracted from commands OR new from architecture docs)
- [ ] No knowledge is invented — all content traces to existing commands or architecture documents

### Priority

P0 — on the critical path. Epic 3 (Commands) and Epic 4 (PM Engine) both depend on this epic. D2.1 is the first deliverable within the epic.

---

## Problem Statement

### Current State

9 existing commands embed shared knowledge inline, leading to:
- **Duplication**: SysML syntax patterns appear in `design-model` (600+ lines), `implement-model` (~40 lines), `plan-model` (~25 lines), and `quick-model` (will need them)
- **Inconsistency**: Source traceability patterns differ between `design-model`, `manage-sources`, and `research`
- **Bloat**: Average command length is 543 lines; target is 200–300
- **Missing knowledge**: `requirements-tracking` (PR-XXX format, promotion path) and `epic-decomposition` (scale taxonomy, decomposition process) don't exist in any command yet — they are new capabilities from the architecture redesign

3 skills currently exist (`python-debugger`, `record-learning`, `toolkit-awareness`) but none address the shared modeling knowledge that commands need.

### Desired Outcome

6 new skills that:
1. **Extract** shared knowledge from existing commands into reusable, consistent references
2. **Create** new knowledge for capabilities the architecture introduces (requirements tracking, epic decomposition)
3. **Enable** Epic 3 to refactor commands from 543 → ~250 lines average by replacing inline knowledge with skill references

---

## Scope

### In Scope

- Creating 6 new skill directories in `claude/skills/`
- Writing SKILL.md files (<200 lines each) with correct frontmatter
- Creating `references/` subdirectories where SKILL.md content would exceed 200 lines
- Identifying extraction sources (which command lines map to which skill content)
- Incorporating content from `MODELING_GUIDE.md.template` (which has `<!-- SKILL: moves to ... -->` markers from D1.2)

### Out of Scope

- Modifying existing commands (Epic 3, D3.1)
- Updating `MBSE_SKILLS` registration (D2.3)
- Context window measurement (D2.4)
- Existing skill revisions — `toolkit-awareness` and `record-learning` (D2.2)
- Writing the extraction mapping document (D2.5 — depends on D2.1 + D2.4)

### Edge Cases & Considerations

- **sysml-conventions size risk**: This skill has the most source material (~600 lines from design-model alone). Plan for `references/` subdirectory from the start.
- **New vs extracted content**: `epic-decomposition` and `requirements-tracking` are primarily NEW content from architecture documents, not extracted from existing commands. They have less source material to work from.
- **MODELING_GUIDE.md.template overlap**: D1.2 already marked sections with `<!-- SKILL: moves to ... -->` comments. Skills MUST incorporate this flagged content, not duplicate it.

---

## Requirements

### Functional Requirements

> Requirements below trace to the epic (EPIC-ARCH-002 D2.1), architecture documents, and codebase investigation.

#### FR-1: Skill Directory Structure

Each skill MUST follow the established pattern from existing skills:

```
claude/skills/{skill-name}/
├── SKILL.md          # Required: <200 lines, YAML frontmatter
└── references/       # Optional: deep reference material
    └── *.md
```

#### FR-2: SKILL.md YAML Frontmatter

Each SKILL.md MUST include YAML frontmatter with these fields:

```yaml
---
name: {skill-name}
description: >
  {Multi-line description including trigger phrases for Claude Code's
  skill discovery. Should describe WHEN this skill is relevant.}
allowed-tools: {comma-separated tool list}
user-invocable: false
---
```

- `name` MUST match the directory name
- `description` MUST include trigger phrases that describe when the skill is relevant (following `toolkit-awareness` and `record-learning` patterns)
- `allowed-tools` MUST be minimal — read-only tools (`Read, Grep, Glob`) unless the skill needs Bash (only `model-validation` needs Bash for running `agentic-mbse validate`)
- All 6 new skills MUST be `user-invocable: false` (they are referenced by commands, not invoked directly)

#### FR-3: Content Boundaries

Each skill MUST contain ONLY:
- **Principles**: When and why to apply this knowledge
- **Rules**: Concrete, actionable rules (naming conventions, format specifications, structural constraints)
- **Patterns**: Code examples, templates, format references
- **Anti-patterns**: What to avoid and why

Each skill MUST NOT contain:
- **Workflow logic**: Stage sequences, decision trees, user interaction patterns (stays in commands)
- **Project-specific data**: File paths that vary by project, entity IDs (stays in information architecture)
- **Agent prompts**: Role definitions, personality, output formatting (stays in commands/agents)

#### FR-4: Six Specific Skills

##### FR-4.1: `sysml-conventions`

**Content sources**:
- Extract from `design-model.md` lines ~580-643 (common pitfalls: attribute declarations, units notation, unicode errors, part definitions, doc comments)
- Extract from `implement-model.md` lines ~163-177 (pre-flight syntax validation, doc comment template)
- Extract from `plan-model.md` lines ~155-175 (ADR-002 compliance, constraint/import/binding patterns)
- Extract from `MODELING_GUIDE.md.template` lines 107-152 (standard imports, key syntax patterns — marked with `<!-- SKILL: moves to sysml-conventions -->`)
- Extract from `MODELING_GUIDE.md.template` lines 264-283 (pattern documentation index — marked with `<!-- SKILL: moves to sysml-conventions -->`)

**MUST include**:
1. Naming conventions (definitions: `'Title Case'`, usages: `snake_case`, attributes: `snake_case`, packages: `lowercase_underscores`)
2. Definition vs usage separation rule (definitions in `library/`, usages in `designs/`)
3. Standard import patterns (`ScalarValues::*`, `ISQ::*`, `SI::*`, `NumericalFunctions::sum`)
4. Key syntax patterns (conditionals, constraints, cross-file binding, semantic operators)
5. Common pitfalls with corrections (qualified names in expressions, missing imports, unicode unit errors, redefines vs specializes)
6. Doc comment format (Source, Reference, Last Updated fields)
7. ADR-002: calc defs in library/ only; designs contain values and wiring

**SHOULD include** (in `references/` if SKILL.md exceeds 200 lines):
- Code stencils for common definition types (part def, calc def, constraint def, connection def)
- Pattern documentation index (pointer to `docs/patterns/` files)

**Trigger phrases for description**: "SysML syntax", "naming conventions", "how to write", "part def", "calc def", "imports", "syntax error", "parse error", "common mistakes"

##### FR-4.2: `model-validation`

**Content sources**:
- Extract from `design-model.md` lines ~645-811 (7-level quality pyramid, validation checkpoints, design validation report)
- Extract from `implement-model.md` lines ~145-349 (parse validation, quality validation, regression testing)
- Extract from `plan-model.md` lines ~146-220 (feasibility validation, prototype baseline validation)
- Extract from `audit-models.md` lines ~30-234 (verification standards, baseline comparison, pass/warn/fail thresholds)
- Extract from `spec-model.md` lines ~119-149 (evaluatable success criteria, test assertion patterns)
- Extract from `MODELING_GUIDE.md.template` lines 167-232 (regression testing — marked with `<!-- SKILL: moves to model-validation -->`)

**MUST include**:
1. 8-level validation pyramid (one-line summary per level with blocking status)
2. CLI invocation patterns (`agentic-mbse validate models/`, `--level=N`, `--complete`, `--verbose`)
3. When to validate: after prototype (Levels 1-3), after implementation phase (Levels 1-5), final (all levels)
4. Verification thresholds: PASS (≤1% deviation), WARN (1-5%), FAIL (>5%)
5. Regression test patterns (pytest with syside, test structure in `tests/models/`)
6. Reading validation output (interpreting errors, warnings, info messages)

**SHOULD include**:
- Skip convention for codegen-dependent tests (`codegen_available` pytest marker)
- Validation report template structure

**Trigger phrases for description**: "validate", "validation levels", "quality checks", "run checks", "test models", "regression test", "Level 1", "Level 8"

##### FR-4.3: `project-structure`

**Content sources**:
- Extract from `design-model.md` lines ~132-147 (library vs designs, file organization)
- Extract from `implement-model.md` lines ~105-144 (parallel vs sequential implementation, batch validation)
- Extract from `spec-model.md` lines ~14-43 (models README, existing model catalog)
- Extract from `plan-model.md` lines ~70-143 (phasing principles, library before instances, bottom-up dependencies)
- Extract from `onboard.md` lines ~115-119, 224-245, 283-289 (directory state assessment, project structure)
- Extract from `MODELING_GUIDE.md.template` lines 28-43 (EXPOSE pattern — marked with `<!-- SKILL: moves to project-structure -->`)
- Architecture document: `information-architecture.md` § 2 (4-directory file structure)
- Architecture document: `information-architecture.md` § 3 Role 3 (intent formalization, G-XXX/AQ-XXX formats)

**MUST include**:
1. The 4-directory information architecture (`knowledge/`, `modeling_project/`, `work/`, `data/`) with what goes where
2. Model file organization (`models/library/` subdivisions, `models/designs/` per-config)
3. Library vs designs separation rule (definitions in library/, usages in designs/)
4. Cross-file dependency rules (unidirectional imports, package boundaries)
5. EXPOSE pattern (expose calc outputs as design attributes for cross-file access)
6. Key project files and their roles (OVERVIEW.md → goals, ARCHITECTURE.md → decisions, REQUIREMENTS.md → rules, VALIDATION_MATRIX.md → verification, KNOWLEDGE.md → insights, BACKLOG.md → work tracking)
7. Intent formalization context (`modeling_project/intent/` → OVERVIEW.md G-XXX/AQ-XXX extraction)

**Trigger phrases for description**: "project structure", "where does this go", "library vs designs", "file organization", "directory", "EXPOSE pattern", "project files"

##### FR-4.4: `source-traceability`

**Content sources**:
- Extract from `design-model.md` lines ~293-315, 356-379, 461-512, 889-934 (doc comment format, parameter extraction, citation requirements, confidence assessment)
- Extract from `implement-model.md` lines ~190-222 (codebase source citations with line numbers)
- Extract from `spec-model.md` lines ~78-82, 283-293 (codebase traceability, traceability matrix updates)
- Extract from `audit-models.md` lines ~108-137, 271-301 (baseline verification, traceability linking)
- Extract from `research.md` lines ~51-58, 113-129, 161-223 (domain source investigation, citation patterns)
- Extract from `manage-sources.md` lines ~49-320 (source type definitions, format specification)
- Architecture document: `information-architecture.md` § 5 (traceability model, durable chain)
- Architecture document: `docs/source-index.md` (SOURCE_INDEX format guide)

**MUST include**:
1. The durable traceability chain: DI-XXX → PR-XXX → model element → authority source
2. SOURCE_INDEX.md entity format (Name, Type, Location, Use For, Validation)
3. Doc comment requirements (Source, Reference, Last Updated fields)
4. Citation patterns by source type (file:line for codebases, section for specs, URL for online)
5. Traceability matrix schema (`data/traceability_matrix.csv` — all 11 columns and their meaning)
6. When to record traceability (during implementation, not after — traceability is a byproduct of work, not a separate phase)

**SHOULD include**:
- Source type taxonomy (codebase, documentation, database, reference)
- Confidence assessment guidance (High/Medium/Low with criteria)

**Trigger phrases for description**: "traceability", "source", "citation", "doc comment", "SOURCE_INDEX", "where did this come from", "reference", "traceability matrix"

##### FR-4.5: `epic-decomposition`

**Content sources**:
- Architecture document: `workflows.md` § 2.1 (scale taxonomy — Trivial/Standard/Epic)
- Architecture document: `workflows.md` § 3.6 (epic tracking, BACKLOG.md format)
- Template: `EPIC_GUIDE.md.template` (Goldilocks principle, decomposition process, anti-patterns)
- Extract from `backlog.md` lines ~54-87 (work item extraction, prioritization, scope sizing)
- Extract from `spec-model.md` lines ~29-31 (epic context reading)

**Note**: This skill is primarily NEW content from architecture documents, not extracted from existing commands. The existing `backlog.md` command has basic work item structure but no scale taxonomy or decomposition methodology.

**MUST include**:
1. Scale taxonomy with routing: Trivial → `/quick-model`, Standard → `/spec-model`, Epic → `/backlog decompose`
2. Goldilocks indicators for modeling work (too large, too small, just right)
3. Decomposition by domain concern (NOT by workflow phase, NOT by validation level)
4. 5-step decomposition process (review scope, identify sources, sketch items, check independence, define criteria)
5. Anti-patterns (phase-as-item, validation-level decomposition, separating authority source integration, vague criteria, no goal traceability)
6. Epic file structure summary (YAML frontmatter: Status, Priority, Goal, Created, Updated)

**SHOULD include**:
- Relationship between BACKLOG.md (dashboard) and epic files (decomposition detail)

**Trigger phrases for description**: "epic", "decompose", "too large", "too small", "scale", "work item size", "backlog", "how to break down"

##### FR-4.6: `requirements-tracking`

**Content sources**:
- Architecture document: `information-architecture.md` § 3 Role 4 (two-tier structure, PR-XXX format, sub-types)
- Architecture document: `workflows.md` § 3.5 (close flow trigger questions)
- Architecture document: `main.md` AP-7 operations table (promote-requirement)
- Extract from `spec-model.md` lines ~101-149 (MR-XXX numbering, EARS format, requirement types)
- Extract from `implement-model.md` lines ~366-421 (acceptance criteria tracking, completion gates)
- Extract from `backlog.md` lines ~86-151 (status tracking, priority levels, completion criteria)

**Note**: This skill is primarily NEW content from architecture documents. The existing commands have basic MR-XXX patterns in spec-model but no PR-XXX format, no promotion path, no enforcement methodology.

**MUST include**:
1. Two-tier requirements structure: MODELING_GUIDE.md (tool-owned baseline) + REQUIREMENTS.md (user-owned project extensions)
2. PR-XXX entity format (ID, Requirement, Source, Enforcement, Validation Method)
3. Promotion path: when a per-feature MR-XXX becomes a project-wide PR-XXX
4. Sub-types (modeling patterns, structural rules, documentation rules, enforcement rules, naming conventions, domain requirements)
5. Enforcement methods (validation rule, design review, regression test)
6. Compliance checking: how commands verify model work against REQUIREMENTS.md

**SHOULD include**:
- MR-XXX format reference (per-feature requirements in spec.md — ephemeral, NOT tracked at project level)
- EARS format ("The model SHALL...") for writing clear requirements

**Trigger phrases for description**: "requirement", "PR-XXX", "project rule", "modeling rule", "compliance", "enforcement", "promote requirement", "REQUIREMENTS.md"

### Non-Functional Requirements

1. **NFR-1: Consistency** — All 6 skills MUST follow the same structural pattern (frontmatter, section ordering, reference to related skills)
2. **NFR-2: Self-containment** — Each skill MUST be understandable without reading other skills. Cross-references are pointers, not dependencies.
3. **NFR-3: Stability** — Skills SHOULD be written to minimize change frequency. Domain-agnostic content is preferred over fusion-tea-specific examples.

---

## Acceptance Criteria

### Core Functionality

- [ ] 6 directories exist: `claude/skills/{sysml-conventions,model-validation,project-structure,source-traceability,epic-decomposition,requirements-tracking}/`
- [ ] Each directory contains `SKILL.md` with valid YAML frontmatter (`name`, `description`, `allowed-tools`, `user-invocable`)
- [ ] Each SKILL.md is under 200 lines (excluding frontmatter)
- [ ] `sysml-conventions` has `references/` subdirectory if SKILL.md would otherwise exceed 200 lines
- [ ] All 6 skills reference Epic 1 directory paths (`knowledge/`, `modeling_project/`, `work/`, `data/`) — NOT `modeling_pm/`
- [ ] No skill contains workflow logic (stage sequences, user interaction patterns, decision trees)
- [ ] No skill contains project-specific data (entity IDs, project-specific file contents)
- [ ] Content from `MODELING_GUIDE.md.template` `<!-- SKILL: moves to ... -->` markers is incorporated

### Content Completeness

- [ ] `sysml-conventions` covers: naming, definition/usage separation, imports, syntax patterns, pitfalls, ADR-002, doc comment format
- [ ] `model-validation` covers: 8-level pyramid, CLI invocation, validation timing, thresholds, regression testing
- [ ] `project-structure` covers: 4-directory model, library/designs separation, EXPOSE pattern, key project files, intent formalization
- [ ] `source-traceability` covers: durable chain, SOURCE_INDEX format, doc comments, citation patterns, traceability matrix schema
- [ ] `epic-decomposition` covers: scale taxonomy, Goldilocks indicators, decomposition process, anti-patterns, epic file structure
- [ ] `requirements-tracking` covers: two-tier structure, PR-XXX format, promotion path, enforcement methods, compliance checking

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] Each skill's `description` field includes trigger phrases for Claude Code discovery
- [ ] `allowed-tools` is minimal and correct for each skill
- [ ] No duplicate content between skills (cross-reference instead)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-knowledge.md` (EPIC-ARCH-002)
- **Architecture — Skills:** `.project/concepts/architecture-redesign/workflows.md` § 1
- **Architecture — Components:** `.project/concepts/architecture-redesign/components.md` § 2
- **Architecture — Information:** `.project/concepts/architecture-redesign/information-architecture.md`
- **Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` § 2.1
- **Existing Skills:** `claude/skills/{python-debugger,record-learning,toolkit-awareness}/`
- **Design:** `.project/active/d2.1-new-skills/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`

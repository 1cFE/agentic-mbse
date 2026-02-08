# Design: D2.1 — New Skills (6 Skills)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-02T01:38:47Z
**Branch:** revamp-architecture
**Commit:** 437aa9a

## Overview

Create 6 new skill directories in `claude/skills/` that extract shared modeling knowledge from existing commands and architecture documents. Each skill follows the established pattern (SKILL.md + optional references/) and stays under 200 lines.

## Related Artifacts

- **Spec:** `.project/active/d2.1-new-skills/spec.md`
- **Epic:** `.project/backlog/epic_architecture-knowledge.md` (EPIC-ARCH-002)
- **Architecture — Skills:** `.project/concepts/architecture-redesign/workflows.md` § 1
- **Architecture — Components:** `.project/concepts/architecture-redesign/components.md` § 2
- **Existing skills:** `claude/skills/{toolkit-awareness,record-learning,python-debugger}/`

## Research Findings

### Existing Skill Pattern (from `toolkit-awareness`)

The established skill structure is:

```
claude/skills/{name}/
├── SKILL.md          # YAML frontmatter + markdown body
└── references/       # Optional deep reference
    └── *.md
```

**SKILL.md anatomy** (from `toolkit-awareness/SKILL.md`, 103 lines):
1. YAML frontmatter: `name`, `description` (multi-line with trigger phrases), `allowed-tools`, `user-invocable`
2. `# {Title}` — one-line purpose statement
3. `## Core Principle` — the single most important rule (1-2 sentences)
4. `## When This Skill Triggers` — bullet list of contexts
5. Content sections — rules, patterns, tables, code blocks
6. `## Anti-Patterns to Avoid` — table of wrong → right
7. `## Reference Files` — pointers to `references/` subdirectory

**Key pattern observations**:
- Frontmatter `description` is verbose and keyword-rich — this is how Claude Code discovers the skill
- Content is direct and imperative ("Never guess...", "Always ground...")
- Code blocks are used for concrete examples, not abstract patterns
- Anti-patterns table is an effective format for "don't do X, do Y"
- References subdirectory holds extended content that doesn't fit in SKILL.md

### Content Overlap Resolution

Four overlap zones were identified and resolved:

| Overlap | Resolution |
|---------|-----------|
| **Doc comments** | `sysml-conventions` owns the FORMAT (`doc /* ... */`, field list, syntax). `source-traceability` owns the CONTENT (what each field must contain, citation patterns, traceability chain integration). Cross-reference: "For field content requirements, see source-traceability skill." |
| **Definitions vs usages** | `sysml-conventions` owns the SysML SYNTAX (`part def 'Title Case'` vs `part snake_case : 'Def'`, naming rules). `project-structure` owns the DIRECTORY ORGANIZATION (`library/` vs `designs/`, subdivision patterns). Cross-reference: "For directory placement, see project-structure skill." |
| **ADR-002** | `sysml-conventions` owns the RULE (calc defs in library/ only, expression taxonomy). `project-structure` owns the FILE STRUCTURE consequence (library/analyses/ subdivision, library-first phasing). |
| **Validation CLI** | `toolkit-awareness` keeps basic CLI invocation (how to run it). `model-validation` owns the METHODOLOGY (per-level criteria, timing, thresholds, interpretation). Cross-reference: "For detailed level descriptions, see model-validation skill." |

### Content Source Classification

All estimated line counts below are **body-only** (excluding YAML frontmatter).

| Skill | Extraction (from commands) | New (from architecture docs) | Estimated lines (body) |
|-------|---------------------------|------------------------------|------------------------|
| `sysml-conventions` | ~80% (design-model, implement-model, plan-model, MODELING_GUIDE) | ~20% (consolidation) | 150-180 + references/ |
| `model-validation` | ~70% (design-model, implement-model, audit-models, MODELING_GUIDE) | ~30% (8-level summary, timing) | 140-170 |
| `project-structure` | ~50% (design-model, spec-model, onboard, MODELING_GUIDE) | ~50% (4-directory model from info-arch) | 130-160 |
| `source-traceability` | ~60% (design-model, manage-sources, research, audit-models) | ~40% (durable chain from info-arch § 5) | 130-160 |
| `epic-decomposition` | ~20% (backlog command) | ~80% (workflows.md § 2.1, § 3.6, EPIC_GUIDE) | 120-150 |
| `requirements-tracking` | ~25% (spec-model, implement-model, backlog) | ~75% (info-arch § 3 Role 4) | 120-150 |

---

## Proposed Design

### Standard SKILL.md Template

All 6 skills follow this section ordering for consistency (NFR-1):

```markdown
---
name: {skill-name}
description: >
  {Trigger-phrase-rich description for Claude Code discovery.
  Should list concrete keywords and question patterns.}
allowed-tools: {tools}
user-invocable: false
---

# {Skill Title}

{One-line purpose statement.}

## Core Principle

{The single most important rule — 1-3 sentences. What a reader
MUST internalize even if they skip everything else.}

## When to Reference

{Bullet list: which commands reference this skill and in what contexts.}

## {Content Section 1}

{Rules, patterns, tables, code blocks organized by topic.}

## {Content Section N}

...

## Anti-Patterns

{Table: Instead of X → Do Y}

## Related Skills

{Cross-references to other skills with one-line reason.}
```

**Design decisions in this template**:
- "Core Principle" replaces toolkit-awareness's "Core Principle" — same concept, proven pattern
- "When to Reference" replaces "When This Skill Triggers" — these skills are not auto-triggered, they're referenced by commands
- "Related Skills" is new — handles cross-references between skills (NFR-2: self-containment with explicit pointers)
- No "Reference Files" section unless the skill has a `references/` subdirectory

### Skill-by-Skill Design

#### 1. `sysml-conventions/SKILL.md`

**Estimated lines**: 160-180 (may need references/)

**Section structure**:
```
# SysML Conventions
## Core Principle
## When to Reference
## Naming Conventions
  - Table: Definitions ('Title Case'), Usages (snake_case), Attributes (snake_case), Packages (lowercase_underscores)
## Definition vs Usage Rule
  - Decision question: "Could this apply to multiple designs?"
  - Syntax examples for each
  - Cross-ref → project-structure for directory placement
## Calculation Architecture (ADR-002)
  - Rule: calc defs in library/ only
  - Expression taxonomy table: Literal OK, Static OK, EXPOSE OK, Derived VIOLATION
## Standard Imports
  - Code block: ScalarValues, ISQ, SI, NumericalFunctions::sum
## Doc Comment Format
  - Template with Source, Reference, Last Updated
  - Cross-ref → source-traceability for field content requirements
## Common Pitfalls
  - Table: Pitfall → Correction (unicode units, missing imports, qualified names in expressions, redefines vs specializes)
## Key Syntax Patterns
  - Conditional expressions, constraints, cross-file binding, semantic operators (=, default :=, :>>, :>)
  - One example each (brief)
## Anti-Patterns
## Related Skills
```

**references/ subdirectory**: `references/stencils.md` — full code stencils for part def, calc def, constraint def, connection def. Also the pattern documentation index (pointer to `docs/patterns/` files). Create this upfront — line estimates (160-180 body lines) are close to the 200-line limit, and the spec recommends planning for `references/` from the start.

**Frontmatter description triggers**: "SysML syntax", "naming conventions", "how to write", "part def", "calc def", "imports", "syntax error", "parse error", "common mistakes", "pitfalls", "SysML patterns"

**allowed-tools**: `Read, Grep, Glob`

#### 2. `model-validation/SKILL.md`

**Estimated lines**: 140-160

**Section structure**:
```
# Model Validation
## Core Principle
## When to Reference
## The 8-Level Validation Pyramid
  - Table: Level | Name | Checks | Blocking | Command
  - One-line summary per level
## CLI Invocation
  - Code block: validate, --level, --complete, --verbose
  - Cross-ref → toolkit-awareness for uv run prefix and environment rules
## When to Validate
  - Table: After prototype (L1-3), After implementation phase (L1-5), Final (all), After audit (focused)
## Verification Thresholds
  - Table: PASS ≤1%, WARN 1-5%, FAIL >5%
  - Action for each: proceed / investigate / stop and fix
## Reading Validation Output
  - Error vs warning vs info interpretation
  - Common error patterns and their meanings
## Regression Testing
  - Test structure: tests/models/ with pytest + syside
  - Test pattern: parse → check structure → verify values
  - Codegen skip convention: codegen_available pytest marker
## Anti-Patterns
## Related Skills
```

**No references/ subdirectory expected** — content fits within 160 lines.

**Frontmatter description triggers**: "validate", "validation levels", "quality checks", "run checks", "test models", "regression test", "Level 1", "Level 8", "validation pyramid", "model quality"

**allowed-tools**: `Read, Grep, Glob, Bash` (Bash for running `uv run agentic-mbse validate`)

#### 3. `project-structure/SKILL.md`

**Estimated lines**: 140-160

**Section structure**:
```
# Project Structure
## Core Principle
## When to Reference
## The 4-Directory Model
  - Table: knowledge/ ("What do we know?"), modeling_project/ ("What are we building?"), work/ ("What's in progress?"), data/ (machine-readable evidence)
  - ASCII tree of full project structure (condensed — key files only)
## Key Project Files
  - Table: File | Role | Entity format
  - OVERVIEW.md (G-XXX goals, AQ-XXX questions), ARCHITECTURE.md (AD-XXX decisions), REQUIREMENTS.md (PR-XXX rules), VALIDATION_MATRIX.md (SV-XXX criteria), KNOWLEDGE.md (DI-XXX insights), BACKLOG.md (work tracking)
## Model File Organization
  - models/library/ subdivisions (foundation/, components/, analyses/)
  - models/designs/{config-name}/ for specific configurations
  - Cross-ref → sysml-conventions for definition vs usage syntax
## Library vs Designs Separation
  - Definitions in library/, usages in designs/
  - ADR-002 structural consequence: calc defs only in library/analyses/
  - Library-first phasing principle: always design library before designs
## Cross-File Dependencies
  - Unidirectional imports rule (designs → library, never reverse)
  - Package boundaries align with directory structure
## EXPOSE Pattern
  - Code block: expose calc output as design attribute
  - When to use: any time a calc output needs cross-file access
## Intent Formalization
  - modeling_project/intent/ holds raw user documents
  - /formalize-intent extracts G-XXX and AQ-XXX into OVERVIEW.md
## Anti-Patterns
## Related Skills
```

**No references/ subdirectory expected**.

**Frontmatter description triggers**: "project structure", "where does this go", "library vs designs", "file organization", "directory", "EXPOSE pattern", "project files", "4-directory model", "knowledge directory", "modeling_project"

**allowed-tools**: `Read, Grep, Glob`

#### 4. `source-traceability/SKILL.md`

**Estimated lines**: 140-160

**Section structure**:
```
# Source Traceability
## Core Principle
## When to Reference
## The Durable Traceability Chain
  - Diagram: DI-XXX → PR-XXX → Model Element → Authority Source
  - Each link: what produces it, where it's recorded, what verifies it
## SOURCE_INDEX.md Format
  - Entity format: Name, Type, Location, Use For, Validation
  - Source types: codebase, documentation, database, reference
  - Location at knowledge/SOURCE_INDEX.md
## Doc Comment Content Requirements
  - What each field must contain (Source: citation, Reference: locator, Last Updated: date)
  - Cross-ref → sysml-conventions for doc comment syntax/format
## Citation Patterns
  - Table: Source Type | Pattern | Example
  - Codebase: file.py:line X-Y
  - Documentation: Document Name, Section X.Y
  - Online: URL with date accessed
## Traceability Matrix Schema
  - Location: data/traceability_matrix.csv
  - All 11 columns with descriptions
  - Knowledge (DI-XXX) and Requirement (PR-XXX) columns enable impact queries
## When to Record Traceability
  - During implementation (byproduct of work, not separate phase)
  - trace-element AP-7 script records rows
  - Confidence assessment: High/Medium/Low criteria
## Anti-Patterns
## Related Skills
```

**No references/ subdirectory expected**.

**Frontmatter description triggers**: "traceability", "source", "citation", "doc comment", "SOURCE_INDEX", "where did this come from", "reference", "traceability matrix", "DI-XXX", "PR-XXX"

**allowed-tools**: `Read, Grep, Glob`

#### 5. `epic-decomposition/SKILL.md`

**Estimated lines**: 120-150

**Section structure**:
```
# Epic Decomposition
## Core Principle
## When to Reference
## Scale Taxonomy
  - Table: Scale | Behavior | Entry Point | Tracking
  - Trivial → /quick-model (no work item directory)
  - Standard → /spec-model (full pipeline, work/active/)
  - Epic → /backlog decompose (must decompose first)
## Goldilocks Indicators
  - Too Large: spans multiple subsystems, 4+ authority sources, 25+ definitions, mixed concerns
  - Too Small: single definition, no cross-file deps, spec overhead exceeds value
  - Just Right: one domain concern, 1-3 sources, 5-20 definitions, independently validatable
## Decomposition Process
  1. Review scope (goals G-XXX, decisions AD-XXX)
  2. Identify authority source dependencies (from SOURCE_INDEX)
  3. Sketch items by domain concern (NOT by phase, NOT by validation level)
  4. Check item independence (can each be spec'd and implemented alone?)
  5. Define success criteria and sequencing
## Epic File Structure
  - Location: work/backlog/epic-{name}.md
  - YAML frontmatter: Status, Priority, Goal, Created, Updated
  - BACKLOG.md is the dashboard; epic files hold decomposition detail
## Anti-Patterns
  - Table: 6 anti-patterns from EPIC_GUIDE (phase-as-item, validation-level decomposition, separating authority sources, ignoring AD-XXX, vague criteria, no goal traceability)
## Related Skills
```

**No references/ subdirectory expected** — EPIC_GUIDE.md remains the detailed user-facing reference. This skill is the concise command-context version.

**Frontmatter description triggers**: "epic", "decompose", "too large", "too small", "scale", "work item size", "backlog", "how to break down", "Goldilocks", "standard vs epic"

**allowed-tools**: `Read, Grep, Glob`

#### 6. `requirements-tracking/SKILL.md`

**Estimated lines**: 120-150

**Section structure**:
```
# Requirements Tracking
## Core Principle
## When to Reference
## Two-Tier Requirements
  - MODELING_GUIDE.md: tool-owned baseline (rules ALL projects follow)
  - REQUIREMENTS.md: user-owned extensions (project-specific rules)
  - Table showing what belongs in each tier with examples
## PR-XXX Entity Format
  - Table: ID | Requirement | Source | Enforcement | Validation Method
  - Example row: PR-001 | All costed components SHALL expose capital_cost | G-001 | Design review + validation rule | AST check
## Requirement Sub-Types
  - Table: modeling patterns, structural rules, documentation rules, enforcement rules, naming conventions, domain requirements
  - Each with description and example
## Promotion Path: MR-XXX → PR-XXX
  - MR-XXX: per-feature, ephemeral, in spec.md (archived with work item)
  - PR-XXX: project-wide, durable, in REQUIREMENTS.md (outlives work items)
  - Promotion criteria: durable, project-wide, worth tracking long-term
  - promote-requirement AP-7 script handles the mechanical promotion
## Enforcement Methods
  - Table: Method | Description | Example
  - Validation rule (machine-checkable via agentic-mbse validate)
  - Design review (human-checked during /review-model or /audit-models)
  - Regression test (pytest test that verifies compliance)
## Compliance Checking
  - Commands read REQUIREMENTS.md before executing
  - /design-model checks compliance during design
  - /audit-models verifies across features
  - /review-model checks design against rules
## EARS Format Reference
  - "The model SHALL..." pattern for writing clear requirements
## Anti-Patterns
## Related Skills
```

**No references/ subdirectory expected**.

**Frontmatter description triggers**: "requirement", "PR-XXX", "MR-XXX", "project rule", "modeling rule", "compliance", "enforcement", "promote requirement", "REQUIREMENTS.md", "two-tier", "MR-XXX to PR-XXX"

**allowed-tools**: `Read, Grep, Glob`

---

### Cross-Reference Map

Skills reference each other using a standard phrase: "For {topic}, see the **{skill-name}** skill."

| From | To | Cross-reference |
|------|----|-----------------|
| sysml-conventions | source-traceability | "For doc comment field content requirements and citation patterns, see the **source-traceability** skill." |
| sysml-conventions | project-structure | "For directory placement of definitions and usages, see the **project-structure** skill." |
| source-traceability | sysml-conventions | "For doc comment syntax and format, see the **sysml-conventions** skill." |
| project-structure | sysml-conventions | "For definition vs usage SysML syntax, see the **sysml-conventions** skill." |
| model-validation | toolkit-awareness | "For `uv run` prefix and environment rules, see the **toolkit-awareness** skill." |
| epic-decomposition | requirements-tracking | "For PR-XXX format used in success criteria, see the **requirements-tracking** skill." |
| requirements-tracking | source-traceability | "For the DI-XXX → PR-XXX traceability chain, see the **source-traceability** skill." |

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `sysml-conventions` exceeds 200 lines | Medium | Low | Create `references/stencils.md` for code stencils and pattern index. SKILL.md keeps principles and rules only. |
| Content extraction from commands is imprecise | Low | Medium | Line ranges in spec are approximate. During implementation, read each command section fully and extract the knowledge content, not mechanical line copies. |
| Skills feel too abstract without examples | Medium | Medium | Each content section should include at least one concrete code block or table. Domain-agnostic examples preferred (NFR-3). |
| Cross-references create circular dependencies | Low | Low | Each skill is self-contained (NFR-2). Cross-references are optional "see also" pointers, not required reading. |

## Integration Strategy

These skills integrate into the existing `claude/skills/` directory alongside the 3 existing skills. No changes to existing skills are needed (that's D2.2 — note: `python-debugger` frontmatter alignment to include `allowed-tools` and `user-invocable` fields is also deferred to D2.2). No changes to `MBSE_SKILLS` registration (that's D2.3).

**Implementation order** (recommended):
1. `sysml-conventions` — largest skill, most extraction work, may need references/
2. `model-validation` — second-largest extraction surface
3. `project-structure` — mix of extraction and new content
4. `source-traceability` — widely distributed extraction (8 commands)
5. `epic-decomposition` — mostly new content, less extraction
6. `requirements-tracking` — mostly new content, less extraction

This order front-loads the highest-risk skills (size and extraction complexity) so problems are discovered early.

## Validation Approach

1. **Line count check**: Each SKILL.md under 200 lines (body, excluding frontmatter)
2. **Frontmatter validation**: YAML parses correctly, `name` matches directory, `description` includes trigger phrases
3. **Content boundary check**: Manual review — no workflow logic, no project-specific data, no agent prompts
4. **Cross-reference integrity**: Every cross-reference points to a skill that exists and covers the referenced topic
5. **Path verification**: All directory paths reference Epic 1 structure (`knowledge/`, `modeling_project/`, `work/`, `data/`), NOT `modeling_pm/`
6. **Existing tests**: `uv run pytest tests/` still passes (skills are markdown files — should have zero impact, but verify)

---

**Next Step:** After approval → `/_my_implement` (write the 6 skills in the recommended order)

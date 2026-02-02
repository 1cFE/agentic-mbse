# Design: New Project Templates (D1.1)

**Status:** Draft
**Created:** 2026-02-01
**Updated:** 2026-02-01
**Related Artifacts:**
  Spec: ./spec.md

---

## Overview

This design specifies the exact content for 6 new template files. The 4 registry templates (FR-1 through FR-4) are mechanical translations of entity formats already defined in information-architecture.md section 3. The 2 work management templates (FR-5, FR-6) require adaptation from the coding-focused originals in `.project/EPIC_GUIDE.md` and `.project/epic_template.md` to the SysML modeling context.

### Design Approach

**Registry templates**: Transcribe the entity format from information-architecture.md, wrap in empty-state structure following existing template conventions (HTML comments for format examples, no fake data, `---` section dividers).

**EPIC_GUIDE.md**: Adapt the coding-focused guide with these key deltas:
- Replace task-type cohesion (scraping/code/integration) with modeling-domain decomposition (domain subsystems, authority sources, validation scope)
- Replace time-based sizing (0.5-2 days) with modeling-appropriate sizing (definition count, authority source scope, validation complexity, independent validatability)
- Add authority source dependency awareness (not present in coding version)
- Add anti-patterns specific to modeling (decomposing by validation level, separating authority source integration from modeling, ignoring AD-XXX decisions)
- Remove coding-specific examples; use domain-agnostic modeling examples

**epic_template.md**: Adapt the coding-focused template with these key deltas:
- Replace markdown metadata with YAML frontmatter per workflows.md section 3.6
- Replace `Epic ID` / `Estimated Effort` with `Goal` (G-XXX link) / `Priority` enum
- Add Authority Source Dependencies section (new — not in coding version)
- Replace coding-style item breakdown (Type: Scraping/Code/Integration) with modeling-style (scope described in terms of definitions, constraints, validation levels)
- Add per-item MR-XXX candidates (high-level requirements that `/spec-model` will refine)
- Replace `.project/active/` paths with `work/active/WI-XXX_{name}/` paths
- Remove Lessons Learned section (close flow handles this via trigger questions per workflows.md section 3.5)
- Remove Timeline/effort estimates (AP-5: toolkit, not pipeline — no time commitments)

---

## Template Designs

### T1: `KNOWLEDGE.md.template` (FR-1)

```markdown
# Domain Knowledge

Curated domain insights that have passed through the research approval gate or been captured inline during modeling work. Each entry is a structured record of something we know about the domain that affects how we model it.

This file is the actionable feed for modeling work. Raw research lives in `knowledge/research/`; only approved, structured insights belong here.

<!-- Entry format reference:

### DI-XXX: [Title]
- **Source**: [approved research doc | user note | authority source | work-item:{WI-XXX}/{artifact}]
- **Rationale**: [only for inline-captured insights: why this was recognized and what evidence supports it]
- **Context**: [1-3 sentences: the domain fact and why it matters]
- **Model implications**: [what the models must capture because of this insight]
- **Analysis implications**: [what analyses this enables or requires]
- **Status**: captured | addressed | superseded
- **Superseded-by**: [DI-XXX ID, only when status = superseded]
- **Supersedes**: [DI-XXX ID, when this insight replaces an earlier one]

-->
```

**Design notes:**
- Single H1 header with purpose description.
- Entity format in an HTML comment so it is invisible when rendered but available as a reference when editing.
- No sections or table structure — entries are appended as H3 headings with bullet-list fields (matching the format in information-architecture.md section 3 Role 2).
- The `Rationale` field is documented as optional per the architecture's note about inline vs. research-pipeline provenance.

---

### T2: `ARCHITECTURE.md.template` (FR-2)

```markdown
# Model Architecture

Structural decisions about how the domain is decomposed into model packages. These are the architectural choices that shape the model ecosystem — decisions that outlive any single work item and that new work must respect.

---

## Domain Decomposition

<!-- How is the physical system decomposed into model packages?
     What are the subsystem boundaries?
     What's shared (library/) vs. configuration-specific (designs/)?

     This section is prose — describe the high-level structure
     and the reasoning behind it. -->

---

## Package Organization

| Package | Purpose | Domain Scope | Dependencies |
|---------|---------|--------------|--------------|

<!-- Add rows as packages are created. Example:
     | library/foundation/ | Base types, units, materials | Cross-cutting | None |
     | library/calculations/ | Shared calc defs | Cross-cutting | foundation/ |
     | designs/{config}/ | Specific configuration | Full system | All library packages | -->

---

## Key Decisions

<!-- Decision format reference:

### AD-XXX: [Title]
**Decision**: [What was decided]
**Rationale**: [Why — what evidence or reasoning supports this]
**Date**: YYYY-MM-DD
**Status**: active | revised | superseded

-->
```

**Design notes:**
- Three sections matching information-architecture.md section 3 Role 5.
- Package Organization uses a table (empty, header-only). The HTML comment shows example rows to illustrate the pattern without polluting the rendered view.
- Key Decisions uses the same HTML-comment pattern as KNOWLEDGE.md — format reference in a comment, no real entries.
- AD-XXX entries are H3 headings with bold-label fields (matching the architecture doc's example format exactly).

---

### T3: `REQUIREMENTS.md.template` (FR-3)

```markdown
# Modeling Requirements

Project-specific rules that all modeling work must follow. These extend the standard rules in [MODELING_GUIDE.md](MODELING_GUIDE.md) with rules discovered through this project's goals and domain knowledge.

> This file replaces the former LOCAL_GUIDE.md. Project-specific patterns, validated findings, and structural rules all belong here as PR-XXX entries.

## Requirements

| ID | Requirement | Source | Enforcement | Validation Method |
|----|-------------|--------|-------------|-------------------|

<!-- Add rows as project-specific rules are established. Example:
     | PR-001 | All costed components SHALL expose capital_cost | G-001 | Design review + validation rule | AST check for cost attributes |
     | PR-002 | Calc defs SHALL cite source file:line in doc comment | G-003 | Validation Level 6 | Doc comment parser | -->
```

**Design notes:**
- Brief intro explaining the two-tier relationship with MODELING_GUIDE.md.
- Blockquote note about LOCAL_GUIDE.md replacement (per D1.3 FR-2).
- Single table, header-only. Example rows in HTML comment.
- Uses RFC 2119 SHALL in the example to model the expected convention.

---

### T4: `VALIDATION_MATRIX.md.template` (FR-4)

```markdown
# Validation Matrix

Verification criteria for the integrated system — checks that go beyond individual work items. Each entry defines what to verify, how to verify it, and what constitutes success.

## Verification Types

| Type | What it checks |
|------|---------------|
| reasonableness | Output is in expected ballpark (order-of-magnitude sanity) |
| baseline | Output matches a reference implementation or known-good value |
| physical | Conservation laws or physical constraints hold |
| relationship | Input/output vary in expected direction (sensitivity) |
| rollup | Aggregations are internally consistent |

## Verification Mechanisms

| Mechanism | How the check runs |
|-----------|--------------------|
| model | Verifiable by model inspection or `agentic-mbse validate` |
| test | Verifiable by pytest (may include codegen + simulation) |
| manual | Requires human judgment |

## Verification Registry

| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |
|----|-------------|------|-----------|----------|-----------|--------|------|--------|

<!-- Add rows as verification criteria are established. Example:
     | SV-001 | Total capital cost ballpark | reasonableness | test | $3B-$15B | range | engineering judgment | test_capital_cost_range | pending |
     | SV-002 | Energy balance conservation | physical | test | sum = total | ±0.1% | physics | test_energy_balance | pending | -->
```

**Design notes:**
- Type and Mechanism reference tables before the registry table. These are static reference content (tool-owned in spirit — the definitions come from information-architecture.md section 3 Role 6). Placed above the registry so users see the vocabulary before adding entries.
- Registry table is header-only with HTML comment examples.
- Status values (pending/passing/failing) are not enumerated explicitly in the template — they are self-evident from the column name and examples.

---

### T5: `EPIC_GUIDE.md.template` (FR-5)

This is the largest template and requires the most adaptation from the coding-focused original. Below is the section-by-section design with content guidance.

#### Section Structure

```
# Epic Guide
## When to Use Epics
## The Goldilocks Principle
### Too Large (needs decomposition into an epic)
### Too Small (doesn't need the full workflow)
### Just Right (standard work item)
## Decomposition Process
### Step 1: Review Epic Scope
### Step 2: Identify Authority Source Dependencies
### Step 3: Sketch Sub-Items by Domain Concern
### Step 4: Check Each Item's Independence
### Step 5: Define Success Criteria and Sequencing
## Epic File Structure
## Relationship to BACKLOG.md
## Anti-Patterns
```

#### Section Content Guidance

**Introduction** (brief):
- What an epic is: a body of modeling work too large for a single work item, requiring decomposition into independently-executable standard items.
- When to create one: scope spans multiple domain subsystems, multiple authority sources, or requires architectural decisions before work can begin.

**When to Use Epics** — the scale taxonomy adapted for modeling:

| Scale | When to use | Entry point | Modeling examples |
|-------|-------------|-------------|-------------------|
| Trivial | Single attribute change, doc comment fix, value update | Direct edit + validate (planned: `/quick-model`) | Fix a naming convention violation; add a missing doc comment citing a source; update a constant from an authority source revision |
| Standard | A cohesive modeling feature: new subsystem, integration, refactor | `/spec-model` | Model the magnet costing subsystem; integrate power balance with turbine plant; refactor cost hierarchy to match updated CAS standard |
| Epic | Multiple domain concerns requiring decomposition before execution | `/backlog` | End-to-end costing pipeline across all subsystems; full reactor model with multiple design configurations; architecture migration to new domain taxonomy |

> **Note on forward references**: The Trivial scale references `/quick-model`, which is an Epic 3 deliverable — it does not exist when D1.1 ships. The template should use phrasing like "direct edit + validate" as the current entry point and note `/quick-model` as planned. Same applies to any other Epic 3 commands (`/review-model`, `/analyze-models`, `/status`, `/formalize-intent`) if referenced in prose.

**The Goldilocks Principle** — adapted from coding to modeling:

The coding version uses time estimates (0.5-2 days) as the primary sizing heuristic. This does not transfer well to modeling, where complexity is driven by domain scope rather than implementation hours. The modeling version uses these indicators instead:

**Too Large** (decompose into an epic):
- Spans multiple domain subsystems that could be modeled independently
- Depends on 4+ authority sources
- Would produce 25+ new definitions (part defs, calc defs, constraint defs)
- Success criteria mix structural concerns with validation concerns with codegen concerns
- Cannot describe the scope without referencing multiple architectural decisions (AD-XXX)

**Too Small** (use `/quick-model` instead):
- Single definition change or addition
- No new interfaces or cross-file dependencies
- Success criteria are a single validation check
- The spec/design/plan cycle would produce more overhead than value

**Just Right** (standard work item):
- Models one domain subsystem or concern end-to-end
- Depends on 1-3 authority sources
- Produces 5-20 new definitions
- Can be validated independently through applicable validation levels
- If paused and resumed later, the spec.md provides enough context to continue
- A change to a domain insight (DI-XXX) affecting this item would be localized — not cascading

**Decomposition Process** — 5 steps (streamlined from the coding version's 6):

1. **Review Epic Scope**: What domain concern does this epic address? Which project goals (G-XXX) does it serve? What architectural decisions (AD-XXX) constrain it?

2. **Identify Authority Source Dependencies**: List which sources from `knowledge/SOURCE_INDEX.md` constrain the work. Flag any that are unstable or need `/research` before items can proceed. This step has no equivalent in the coding version — it is specific to modeling where external knowledge is a first-class constraint.

3. **Sketch Sub-Items by Domain Concern**: Decompose by domain subsystem or model package — NOT by workflow phase (spec/design/plan) and NOT by validation level. Each item should produce a complete, independently-validatable piece of the model. Align with architectural decisions: if AD-001 defines subsystem boundaries, items should respect those boundaries.

4. **Check Each Item's Independence**: Can the item be spec'd, designed, and implemented without waiting for other items (besides declared dependencies)? Does it produce clear deliverables (model files, tests)? Is the scope right-sized per the Goldilocks indicators?

5. **Define Success Criteria and Sequencing**: Each item gets high-level success criteria (MR-XXX candidates that `/spec-model` will refine). Map dependencies between items — which can run in parallel, which must sequence. Identify the critical path.

**Epic File Structure**:
- Reference to the epic_template.md format (YAML frontmatter + body sections)
- Explain the YAML frontmatter fields and their allowed values
- Explain the recommended body sections and what each should contain
- Note that the body is free-form — the user structures it as needed

**Relationship to BACKLOG.md**:
- BACKLOG.md is the dashboard — summary of all epics and standalone items
- BACKLOG.md is script-managed (AP-7) — agents don't edit it directly for state transitions
- Epic files hold the decomposition detail — scope, reasoning, per-item breakdowns
- When a sub-item moves to execution, it gets a directory in `work/active/WI-XXX_{name}/`
- The `Epic` field in spec.md YAML links back to the epic

**Anti-Patterns** — 6 modeling-specific anti-patterns (replacing the coding version's 5):

1. **Decomposing by Validation Level** — "Item 1: Levels 1-3, Item 2: Levels 4-6, Item 3: Levels 7-8." Validation levels are quality gates applied to model elements, not separable units of work. Each item should be validated through all applicable levels.

2. **Separating Authority Source Integration** — "Item 1: Model the structure, Item 2: Integrate the data from PyFECONS." Authority sources constrain the model from the start. Separating them creates rework when the data contradicts the structure.

3. **Ignoring Architectural Decisions** — Decomposition that cuts across AD-XXX boundaries. If the architecture says subsystems A and B are separate packages, don't put both in one work item.

4. **Phase-as-Item (Waterfall)** — "Item 1: Design phase, Item 2: Implementation phase, Item 3: Testing phase." Each item should go through its own full spec/design/plan/implement cycle.

5. **Vague Success Criteria** — "Models are complete" or "validation passes." Success criteria should reference specific domain constraints, authority source alignment, or verification entries (SV-XXX).

6. **No Goal Traceability** — Epic file doesn't link to project goals (G-XXX) or domain insights (DI-XXX). The PM dashboard can't explain why the epic matters.

---

### T6: `epic_template.md.template` (FR-6)

#### Delta from Coding Version

| Aspect | Coding (`.project/epic_template.md`) | Modeling (`epic_template.md.template`) |
|--------|---------------------------------------|----------------------------------------|
| Metadata | Markdown bold fields (Epic ID, Status, Priority, Created, Estimated Effort) | YAML frontmatter (Status, Priority, Goal, Created, Updated) |
| Status values | Draft / Ready / In Progress / Complete | draft / active / completed |
| Priority values | High / Medium / Low | P0 / P1 / P2 / P3 |
| ID scheme | `[SHORT-NAME]` | No ID — epic file name is the identifier |
| Goal traceability | None | `Goal: G-XXX` field linking to OVERVIEW.md |
| Effort estimates | `Estimated Effort: [X days/weeks]` per epic and per item | Removed (AP-5: toolkit, not pipeline) |
| "Why This Epic?" section | Current State / Future State | Renamed to "Context" — broader scope including goal/insight references |
| Authority sources | Not present | New section: Authority Source Dependencies table |
| Item breakdown | Type: Research / Implementation / Integration / Testing | Scale: standard (always — epic items are standard by definition) |
| Item deliverables | `.project/active/[item_name]/` paths | `work/active/WI-XXX_{name}/` paths |
| Item requirements | Not present | MR-XXX candidates (high-level requirements for `/spec-model`) |
| Dependencies section | External / Internal / Dependency Graph | Simplified: per-item Blocks/Blocked-by + Sequencing section |
| Timeline section | Effort table | Replaced by Sequencing section (no time estimates) |
| Lessons Learned | Post-completion section | Removed — close flow trigger questions (workflows.md § 3.5) handle this |

#### Template Content

```markdown
---
Status: draft
Priority: P1
Goal: G-XXX  # from project/OVERVIEW.md
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
---

# Epic: <!-- Epic Name -->

## Executive Summary

<!-- 2-3 sentences: What does this epic deliver and why does it matter?
     What domain challenge does it address? -->

**Critical Success Factor**: <!-- Single most important measure of success -->

---

## Context

<!-- Why is this epic needed? What domain challenge does it address?
     Link to project goals (G-XXX), domain insights (DI-XXX),
     or architectural decisions (AD-XXX) that motivate this work.

     What is the current state? What will exist after this epic? -->

---

## Authority Source Dependencies

<!-- What external knowledge constrains this epic's work items?
     Identifying these early surfaces risks and may trigger /research tasks. -->

| Source | Use For | Items Depending On | Status |
|--------|---------|--------------------|--------|

---

## Success Criteria

- [ ] <!-- Measurable outcome 1 -->
- [ ] <!-- Measurable outcome 2 -->
- [ ] <!-- Quality gate: validation levels pass, no regressions -->

---

## Items

<!-- Per-item breakdowns. Each item becomes a Standard work item
     when it moves to execution (work/active/WI-XXX_{name}/).
     /spec-model reads this section for baseline requirements. -->

### Item 1: <!-- Item Name -->

**Scale**: standard
**Dependencies**: <!-- None | Item N | /research task needed -->

**Scope**:
<!-- What does this item deliver? 2-3 sentences.
     Describe in terms of model elements: definitions, constraints, interfaces. -->

**Success Criteria (MR-XXX candidates)**:
- [ ] <!-- High-level requirement that /spec-model will refine -->
- [ ] <!-- Another requirement -->

**Deliverables**:
- <!-- Model files created or modified -->
- <!-- Tests for validation -->

---

### Item 2: <!-- Item Name -->

<!-- Same structure as Item 1 -->

---

## Sequencing

<!-- Which items can run in parallel? Which must sequence?
     What is the critical path?

     Example:
     Item 1 (no dependencies)
       └─> Item 3 (depends on Item 1)
     Item 2 (no dependencies, parallel with Item 1)
       └─> Item 3 (depends on Item 2) -->

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|

---

**Last Updated**: <!-- YYYY-MM-DD -->
**Next Action**: <!-- What to do next -->
```

**Design notes:**
- YAML frontmatter uses the exact schema from workflows.md section 3.6: `Status`, `Priority`, `Goal`, `Created`, `Updated`.
- YAML placeholders use YAML-native syntax: `G-XXX` as a placeholder string with `# comment` for guidance, and `YYYY-MM-DD` as a self-documenting placeholder. No HTML comments in the YAML block — this keeps the frontmatter parseable even in empty state, which supports testing and PM engine robustness.
- Status enum values are lowercase (`draft`, `active`, `completed`) matching the workflows.md specification.
- Priority uses P0-P3 (matching BACKLOG.md format) instead of High/Medium/Low.
- No Epic ID field — the architecture explicitly decided against E-XXX IDs (file name is the identifier).
- No effort estimates anywhere — removed per AP-5.
- Authority Source Dependencies is a new section not in the coding template. Placed early (after Context) because source dependencies shape the entire decomposition.
- Item breakdown is simplified vs. the coding version: removed Type field (items are always "standard" scale), removed Location field (implied by WI-XXX convention), removed Estimated Effort. Added MR-XXX candidates.
- Sequencing replaces the coding template's Timeline table — captures ordering without time commitments.
- Lessons Learned section removed — the close flow's trigger questions (workflows.md section 3.5) provide a structured opportunity to surface learnings when each item completes.

---

## Consistency Conventions

Applied across all 6 templates to match existing template patterns:

| Convention | Decision | Rationale |
|------------|----------|-----------|
| Section dividers | `---` between major sections | Matches all existing templates |
| Placeholders | HTML comments `<!-- ... -->` | Matches OVERVIEW.md.template, BACKLOG.md.template pattern |
| Format examples | HTML comments with example rows | Invisible when rendered; available when editing |
| Dates | `YYYY-MM-DD` | ISO format, matches existing templates |
| Table format | Pipe-delimited markdown | Matches all existing templates |
| Last Updated | Only on epic_template (user-owned, long-lived) | Registry templates grow via appending — last-updated is per-entry, not per-file |
| File naming | `{NAME}.md.template` | Matches existing naming convention |

---

## What This Design Does NOT Decide

- **EPIC_GUIDE.md prose**: The section structure and content guidance above define *what* each section must cover. The exact wording is an implementation concern — the implementer writes the prose to match the guidance.
- **Installation mechanics**: How `cmd_init()` handles epic_template.md (D1.4 scope).
- **Parser compatibility**: Whether the PM engine can parse these formats (Epic 4 scope — but the formats are designed to match the schemas in workflows.md section 3.6 and information-architecture.md section 3, which are the PM engine's input contracts).

---

## Validation Plan

1. **Render check**: Each template renders as valid markdown (no broken tables, no unclosed HTML comments).
2. **Empty-state check**: Each template, when viewed in a markdown previewer, shows a useful document with no fake data.
3. **Entity format check**: Compare each entity format field-by-field against information-architecture.md section 3.
4. **YAML frontmatter check**: Validate epic_template.md frontmatter against workflows.md section 3.6 schema.
5. **Existing tests**: `uv run pytest tests/` passes (templates are new files — no existing tests should break).

---

**Next Steps:** After approval, proceed to `/_my_plan` to sequence the implementation (likely straightforward: create 6 files, verify).

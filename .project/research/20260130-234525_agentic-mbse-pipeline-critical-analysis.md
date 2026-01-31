---
date: 2026-01-30T23:45:25-07:00
researcher: Claude
topic: "Agentic MBSE Pipeline: Critical Analysis and Redesign Vision"
tags: [research, architecture, commands, pipeline, redesign, skills, agents]
status: working-design
last_updated: 2026-01-31
---

# Research: Agentic MBSE Pipeline - Critical Analysis and Working Design Concept

**Date**: 2026-01-30 23:45 MST
**Researcher**: Claude
**Research Type**: Architecture / Process / Design
**Revised**: 2026-01-31 (incorporated discussion on work item taxonomy, information architecture scaling, agent strategy, research split, PM reliability, git trade-offs)

## Research Questions

1. What are the key jobs-to-be-done at each pipeline stage, from a hardware engineer's perspective?
2. Do we have a practical approach for large projects (like fusion-tea)?
3. Does our strategy align with Claude Code best practices?
4. Is our system robust for non-linear development?

## Executive Summary

After thorough analysis of the current MBSE commands, the Python agentic system, fusion-tea as a real-world case study, and Claude Code platform documentation, I identify **five structural problems** with the current system:

1. **Commands are bloated with mixed concerns** - domain knowledge (SysML syntax), workflow logic, and output templates are tangled together in 400-1300 line commands
2. **Project definition templates design for "1", not "N"** - OVERVIEW.md is a skeleton; real projects like fusion-tea need 400+ lines of charter alone, structured requirements registries, analysis angles, and validation criteria matrices
3. **No concept of project scale or work intent** - the same heavyweight pipeline applies to a 3-line attribute fix and a 6-month fusion plant epic, with no distinction between building new, fixing known issues, or investigating unknowns
4. **The pipeline assumes linear progression** - but real work is iterative, involves refactoring, and often skips or revisits stages
5. **Project management is disconnected and unreliable** - state tracking relies on agent commands (which may not execute), with no script-backed reliability, no visual dashboards, and no structured agile process

The redesign vision centers on **four principles**: design information architecture for N (following SOURCE_INDEX.md's pattern), extract shared knowledge into skills, make commands job-focused with work-intent-aware routing, and split PM into script-driven state queries and agent-driven state changes.

---

## Part 1: Jobs To Be Done (Hardware Engineer's Perspective)

### The User Profile

A hardware engineer using this system:
- Knows their domain deeply (fusion physics, thermal management, materials)
- May be familiar with MBSE concepts (requirements, traceability, V&V)
- Does NOT know SysMLv2 syntax
- Wants to build models that capture their engineering knowledge
- Needs confidence that models are correct (validated against known sources)
- Needs to explain their models to other engineers

### Jobs at Each Stage

#### Spec: "Help me define WHAT I need to model"

**Key jobs:**
- Articulate what physical system/behavior needs to be captured
- Identify what sources of truth exist (codes, papers, test data)
- Define what "correct" means (validation criteria)
- Scope the work to something achievable
- Understand what already exists in the model library

**What the user reviews:** "Does this capture what I need? Are the success criteria right?"

**De-risking role:** Prevents building the wrong thing. The spec is a contract between the engineer's intent and what gets built.

**Current problem:** `spec-model.md` (393 lines) buries the core job under SysML-specific details (MR-XXX format, EARS syntax, validation pyramid levels). A hardware engineer shouldn't need to know about "Level 6 documentation checks" to specify what they want.

**Design concept — work-intent-aware routing:** The spec stage should behave differently depending on what the user is trying to do. Not all work items need the same spec depth:

| Work Intent | Spec Behavior | Example |
|-------------|---------------|---------|
| **Model** (build new) | Full pipeline: scope, requirements, success criteria | "Model the magnet system with costing" |
| **Fix** (correct known issue) | Lightweight: describe what's wrong, what "fixed" looks like | "cost_model calc is missing explicit redefines" |
| **Investigate** (unknown) | Detour to `/research` first, then return to spec with findings | "We need LCOE breakdown but aren't sure what intermediate calcs exist" |
| **Refactor** (reorganize) | Structural: what changes, what must be preserved, regression criteria | "Extract common cost patterns into library definitions" |
| **Integrate** (connect pieces) | Interface-focused: what connects, what contracts must hold | "Wire magnet costs into system-level rollup" |

The spec command should determine intent early (interactively or via tag) and adapt its flow accordingly. A "Fix" doesn't need a full requirements section. An "Investigate" needs research before it can even define requirements.

#### Design: "Help me figure out HOW to model it"

**Key jobs:**
- Understand the engineering decomposition (what components, what interfaces)
- Decide what calculations are needed and where they live
- Map from domain concepts to model structure
- Identify what can be reused vs. what's new
- Validate the approach works (prototype)

**What the user reviews:** "Does this model structure capture the physics correctly? Are the interfaces right?"

**De-risking role:** Catches structural mistakes before detailed implementation. The prototype proves the approach works.

**Current problem:** `design-model.md` (1,345 lines) is doing too many jobs simultaneously: discovery, architecture, specification, prototyping, AND validation. It's also heavily loaded with SysML syntax guidance that should be shared knowledge, not embedded in one command.

#### Plan: "Help me organize the work"

**Key jobs:**
- Break the work into verifiable chunks
- Identify dependencies and ordering
- Define what "done" looks like for each chunk
- Anticipate what might go wrong

**What the user reviews:** "Does this ordering make sense? Is each phase independently verifiable?"

**De-risking role:** Prevents the "big bang" approach where nothing works until everything works. Each phase should be checkpointable.

**Current problem:** `plan-model.md` (676 lines) is reasonable but duplicates information from design. Its biggest issue is that it doesn't differentiate between small (1-file) and large (20-file) efforts.

#### Implement: "Help me build it correctly"

**Key jobs:**
- Execute the plan faithfully
- Validate continuously (don't wait until the end)
- Adapt when reality differs from plan
- Track progress so it's clear what's done

**What the user reviews:** "Does each phase pass validation? Are there issues I need to decide on?"

**De-risking role:** Incremental validation catches problems early. Progress tracking prevents "I think it's mostly done" syndrome.

**Current problem:** `implement-model.md` (493 lines) lacks the Python system's "understand before acting" discipline (Stage 0). It also embeds batch editing patterns that are operational detail, not job-to-be-done.

#### Audit: "Help me verify it's right"

**Key jobs:**
- Compare model outputs against known-good sources
- Check that nothing was broken (regression)
- Verify traceability is complete
- Generate a report for stakeholders

**What the user reviews:** "Are there discrepancies? Are they acceptable?"

**De-risking role:** Final verification gate before work is considered "done."

**Current assessment:** `audit-models.md` (446 lines) is actually reasonably well-focused on its job.

### Key Insight

The commands should be organized around **user decisions**, not process steps. At each stage, the user needs to make specific decisions. Everything else (SysML syntax, validation commands, file organization) is implementation detail that should be pulled into shared skills.

---

## Part 2: Practical Approach for Large Projects

### The Fusion-Tea Case Study

Fusion-tea is modeling an entire fusion power plant for techno-economic analysis. Key stats:

- **Scale:** ~37 cost account categories, ~300 parameters per design, multiple reactor types (MFE, IFE, MIF)
- **Current state:** 18 SysML files (5 production library, 13 tests), 4 Python test files
- **Completed:** Foundation package (types, units, materials) + power balance calculations
- **Backlog:** 15+ work items across P0-P3 priorities
- **Research:** 17 research documents informing design decisions
- **Dependencies:** PyFECONS (validation baseline), sysml-codegen, teax-simkit

This project will have dozens of model files across library and design directories, with complex cross-file dependencies.

### Current Gaps

#### 1. No solid definition of "epic" vs "work item"

The current backlog has entries like:
- "Epic: Power Core Components" (huge scope - magnets, blanket, shield, divertor)
- "Feature: Costed Component Interface" (small, specific scope)

But there's no guidance on:
- When something is an "epic" vs. a "feature" vs. a "task"
- How to decompose a massive epic like "Power Core" into right-sized work items
- What a right-sized work item even is for modeling (unlike coding, modeling has different granularity)

The Python system's EPIC_GUIDE.md (328 lines) provides this with the Goldilocks principle (0.5-2 days per item), task type cohesion, and clear anti-patterns. The MBSE system has nothing equivalent.

#### 2. No architectural vision concept

When you model a fusion power plant, you need an **architectural vision** before you start individual work items. Something like:

- "We'll organize the library around physics domains (power balance, thermal, structural)"
- "Each design configuration (CATF, compact stellarator) gets its own directory"
- "Cross-file bindings flow: geometry -> structural -> physics -> system"

The fusion-tea OVERVIEW.md captures some of this, but there's no command or process that helps create and maintain it. The spec/design/plan pipeline only works at the feature level.

#### 3. No incremental verification strategy across work items

Individual work items have validation (quality pyramid). But there's no concept of:
- "After power balance is done, what integration tests prove it works with the foundation?"
- "Before starting magnets, what interfaces must be stable?"
- "How do we know the overall architecture is still sound after 10 work items?"

The Python system's test-first approach addresses this for code. For models, we need equivalent "model integration tests" that grow with the project.

#### 4. No concept of when to refactor

Fusion-tea is 3 weeks old and already has refactoring needs (cost pattern fixes, explicit types/redefines). As models grow, technical debt accumulates:
- Duplicated definitions across files
- Inconsistent naming conventions
- Cross-file coupling that should be simplified
- Library definitions that are too specific or too general

There's no guidance on when to stop building and refactor, or how to scope a refactoring work item.

#### 5. Project definition templates design for "1", not "N"

There is an old CS adage: design for 0, 1, or N. `SOURCE_INDEX.md` already designs for N — it handles many sources with a structured, repeatable format. But the rest of the project definition is designed for "1":

- `OVERVIEW.md` has one goals section, one success criteria list — but fusion-tea needs a 400-line project charter plus structured requirements, analysis angles, and validation criteria
- No requirements registry — MR-XXX identifiers exist per-feature in spec.md files but there's no project-wide aggregation. You can't ask "which requirements trace to the LCOE goal?" or "which requirements have passing tests?"
- No domain insights register — analysis angles (interpretive perspectives that imply both model and analysis requirements) exist only in conversation and research prose, with no structured capture or downstream links
- No validation criteria matrix — targets, tolerances, sources, and tests are scattered across specs and research docs with no unified view
- No architecture vision document — the structural decisions that shape the entire model ecosystem have no home

The information-role taxonomy research identified six roles (Authority Sources, Domain Knowledge, Project Intent, Modeling Requirements, Modeling Decisions, Model Artifacts). Currently only Authority Sources (SOURCE_INDEX.md) and Modeling Requirements (per-feature spec.md) have structured homes. The other four roles store information in prose, conversation, or not at all.

### What We Need

**A project-level workflow** that complements the feature-level pipeline:

1. **Project initialization** (`/onboard` - exists, needs enhancement)
   - Establish architectural vision
   - Define library organization strategy
   - Set up information architecture (all six roles have homes)
   - Set up initial integration test structure

2. **Epic decomposition** (missing)
   - Adapted Goldilocks principle for modeling (different granularity than code)
   - Clear epic -> work item decomposition process
   - Dependency mapping across work items
   - Work items tagged with intent and scale

3. **Architecture health checks** (missing)
   - Periodic review of cross-file coupling
   - Integration test coverage growth
   - Refactoring trigger criteria

4. **Project status reporting** (missing)
   - Where are we relative to the architectural vision?
   - What's been validated end-to-end vs. in isolation?
   - What technical debt is accumulating?
   - Requirements coverage (traced vs untraced, tested vs untested)

---

## Part 3: Alignment with Claude Code Best Practices

### Current Architecture vs. Platform Design Intent

Claude Code's platform provides three tiers:

| Tier | Purpose | Context Model |
|------|---------|---------------|
| **Skills** | Reusable knowledge/workflows | Inline (loaded into main conversation) |
| **Commands** | Task-specific step-by-step workflows | Inline (loaded into main conversation) |
| **Agents** | Isolated specialist work | Separate context (cheap) |

The platform's design intent is clear:
- **Skills for shared knowledge** - loaded on demand, referenced by multiple commands
- **Commands for focused workflows** - single-purpose, under 500 lines
- **Agents for context isolation** - keep expensive exploration out of main conversation
- **CLAUDE.md for essentials only** - just what Claude can't figure out on its own

### Where We're Misaligned

#### Problem 1: Commands contain shared knowledge

`design-model.md` embeds:
- SysMLv2 syntax rules (lines 580-645) - should be a skill
- Sub-agent usage patterns (lines 1214-1290) - should be a skill
- Output template with SysML code stencils (lines 815-1140) - should be a skill
- Common pitfalls and quick reference (lines 579-644) - should be a skill

This same knowledge is needed by `implement-model.md` and `audit-models.md`, but it's only in `design-model.md`. Result: inconsistency and duplication.

#### Problem 2: Commands are too long

Claude Code docs explicitly recommend commands under 500 lines. Current state:

| Command | Lines | Recommendation |
|---------|-------|----------------|
| design-model | 1,345 | Should be ~300 + skills |
| plan-model | 676 | Should be ~250 + skills |
| implement-model | 493 | Should be ~200 + skills |
| onboard | 578 | Should be ~300 + skills |
| spec-model | 393 | Should be ~200 + skills |
| audit-models | 446 | Should be ~200 + skills |
| backlog | 359 | Should be ~200 + skills |
| manage-sources | 357 | Should be ~150 |
| research | 243 | OK |

#### Problem 3: Skills are underutilized

Current skills:
- `python-debugger` - operational tool, not shared knowledge
- `record-learning` - good, captures session insights
- `toolkit-awareness` - right idea, ensures accurate toolchain knowledge

Missing skills (shared knowledge that should be extracted):
- **SysML conventions** - syntax rules, naming, patterns (referenced by design, implement, audit)
- **Model validation** - quality pyramid, validation commands, level descriptions (referenced by design, implement, audit)
- **Source management** - SOURCE_INDEX patterns, traceability approach (referenced by design, audit, research)
- **Project structure** - library vs designs, file organization, cross-file patterns (referenced by all)
- **Output templates** - spec template, design template, plan template (referenced by respective commands)

#### Problem 4: Agents — keep specialists, standardize references

Current MBSE-specific agents: `kerml-expert`, `sysml-expert`, `syside-expert`, `sysmlv2-validator`, `sysmlv2-doc-analyzer`

**Revised position (from discussion):** The original analysis recommended consolidating from 4 SysML agents to 2. However, empirical evidence shows that parallel specialist agents have better recall than a single unified agent. When agents are launched in parallel and results synthesized by the main agent, the quality is higher than a single agent trying to cover all documentation.

The real problem isn't too many agents — it's **inconsistent references** to them across commands. The solution is to:
1. Keep all existing specialist agents
2. Standardize when each agent is invoked and with what prompt focus
3. Document agent usage patterns (which agent for which question type)
4. Ensure commands reference agents consistently

### What Claude Code Best Practices Suggest

The redesigned architecture should look like:

```
claude/
├── commands/               # FOCUSED workflows (~200-300 lines each)
│   ├── spec-model.md       # Job: define WHAT to model
│   ├── design-model.md     # Job: decide HOW to model
│   ├── plan-model.md       # Job: organize the WORK
│   ├── implement-model.md  # Job: BUILD it correctly
│   ├── audit-models.md     # Job: VERIFY it's right
│   ├── research.md         # Job: LEARN from external sources
│   ├── analyze-models.md   # Job: UNDERSTAND current model state (NEW)
│   ├── quick-model.md      # Job: make a SMALL change quickly (NEW)
│   ├── review-model.md     # Job: REVIEW a design before implementing (NEW)
│   ├── status.md           # Job: UNDERSTAND project state (NEW)
│   ├── backlog.md          # Job: manage WORK ITEMS
│   ├── onboard.md          # Job: SET UP a project
│   └── manage-sources.md   # Job: configure SOURCES
│
├── skills/                 # SHARED KNOWLEDGE (loaded on demand)
│   ├── sysml-conventions/  # SysML v2 syntax, naming, patterns
│   │   ├── SKILL.md        # Overview + when to reference
│   │   └── reference.md    # Detailed patterns and examples
│   ├── model-validation/   # Quality pyramid, commands, levels
│   │   └── SKILL.md
│   ├── project-structure/  # Library vs designs, file org, cross-file
│   │   └── SKILL.md
│   ├── source-traceability/ # SOURCE_INDEX, traceability patterns
│   │   └── SKILL.md
│   ├── epic-decomposition/ # How to break down large modeling work
│   │   └── SKILL.md
│   ├── requirements-tracking/ # Registry format, MR lifecycle, aggregation (NEW)
│   │   └── SKILL.md
│   └── toolkit-awareness/  # CLI commands, validation tools
│       └── SKILL.md
│
└── agents/                 # ISOLATED SPECIALISTS (keep all, standardize refs)
    ├── kerml-expert.md          # KerML standard library functions
    ├── sysml-expert.md          # SysML modeling patterns
    ├── syside-expert.md         # syside parser/tooling
    ├── sysmlv2-doc-analyzer.md  # Cross-cutting SysML documentation
    ├── sysmlv2-validator.md     # Syntax validation + fix suggestions
    └── python-debugger.md       # Python debugging
```

Key changes from current state:
1. Commands shrink by 50-70% (knowledge moves to skills)
2. Skills provide consistent, shared knowledge across commands
3. Agents kept as-is but referenced consistently across commands
4. Each command focuses on **one job** with clear user decision points
5. Research split into external (research) and internal (analyze-models)
6. New commands for gaps: quick-model, review-model, status, analyze-models

---

## Part 4: Robustness for Non-Linear Development

### How Development Actually Happens

The current pipeline assumes: research -> spec -> design -> plan -> implement -> audit

Reality looks more like:

```
Day 1: /spec-model power-balance
Day 2: /design-model power-balance
Day 3: /plan-model power-balance
Day 4: /implement-model power-balance (phase 1 of 3)
Day 5: Discover design flaw → need to go back to design
Day 6: /implement-model power-balance (phase 2 - adapted)
Day 7: New urgent work item appears → switch to foundation-fix
Day 8: /spec-model foundation-fix (quick, small scope)
Day 9: Just fix it directly (too small for full pipeline)
Day 10: Back to power-balance phase 3
Day 11: /audit-models → find issues → need more implementation
Day 12: Realize 3 completed features need refactoring together
```

### Current System's Weak Points

**1. No "quick fix" path**

Every change, no matter how small, is funneled through the full pipeline. Adding a doc comment to an existing definition doesn't need spec -> design -> plan -> implement. The Python system has `/_my_quick_edit` for this. We have nothing.

**2. No way to "go back"**

If the design is wrong during implementation, there's no defined process for:
- Updating the design document
- Re-validating the prototype
- Adjusting the plan
- Resuming implementation from the right point

Each command operates independently. They don't know about each other's state.

**3. No concurrent work item support**

What if you're implementing power-balance and need to pause for a foundation-fix? The system doesn't track:
- What was in progress (power-balance phase 2 of 3)
- What was paused vs. completed
- How to resume after the interruption

The backlog command has "clear" mode for archiving completed work, but nothing for tracking active/paused state.

**4. No refactoring workflow**

After several work items complete, models may need restructuring:
- Extract common patterns into library definitions
- Simplify cross-file bindings
- Fix naming inconsistencies
- Reorganize file structure

This doesn't fit the spec -> design -> plan -> implement pattern because:
- The "spec" is about code health, not business requirements
- The "design" is about reorganization, not new modeling
- The scope cuts across multiple features

**5. No regression safety net across work items**

Individual work items have validation. But when work item B modifies something that work item A depends on, there's no systematic check. The Python system's test-first approach handles this through accumulated test coverage. We have `pytest tests/models/` but it's not woven into the workflow.

### What Robustness Requires

**Principle: The pipeline should be a set of tools, not a rigid sequence.**

1. **Scale-aware entry points:**
   - Trivial change (< 1 hour): Direct edit with validation check
   - Small feature (< 1 day): Lightweight spec + implement
   - Standard feature (1-3 days): Full pipeline
   - Epic (> 3 days): Decompose first, then pipeline per item

2. **State tracking:**
   - Know what's in-progress, paused, completed
   - Know which pipeline stage each work item is at
   - Resume from where you left off

3. **Backward navigation:**
   - "This design doesn't work" -> update design, re-validate
   - "The spec was wrong" -> update spec, cascade to design/plan
   - Clear process for each backward step

4. **Cross-cutting workflows:**
   - Refactoring (reorganize existing models)
   - Migration (update patterns across all models)
   - Integration testing (verify cross-feature interactions)

---

## Part 5: Work Item Taxonomy

This section is new, driven by the observation that the pipeline treats all work identically when real work items differ on two orthogonal dimensions.

### Dimension 1: Work Intent

What is the user trying to accomplish? This determines which pipeline stages are needed and how they behave.

| Intent | Description | Required Artifacts | Pipeline Path |
|--------|-------------|-------------------|---------------|
| **Model** | Build new model elements | spec, design, plan | Full pipeline: spec → design → plan → implement → audit |
| **Fix** | Correct something known-wrong | spec (lightweight) | Short path: spec → implement (skip design, user knows what's wrong) |
| **Investigate** | Unknown that needs research first | research output | Detour: research → spec (may stop here if investigation answers the question) |
| **Refactor** | Reorganize without behavior change | refactoring spec | Structural: spec → plan → implement (skip design — structure is changing, not being invented) |
| **Integrate** | Connect existing pieces across files | integration spec | Interface-focused: spec → design → implement (design focuses on interfaces, not components) |

Each intent changes what the spec command asks for, which stages are required, and what the output documents emphasize.

### Dimension 2: Work Scale

How big is the work? This determines how much process overhead is appropriate.

| Scale | Description | Pipeline Adaptation |
|-------|-------------|-------------------|
| **Trivial** | Single attribute, doc comment, value fix | `/quick-model` — no spec/design/plan, just understand → execute → validate |
| **Small** | Single file, clear scope, < 1 day | Lightweight spec → implement (abbreviated artifacts) |
| **Standard** | Multi-file feature, 1-3 days | Full pipeline per the intent's path |
| **Epic** | > 3 days, needs decomposition | Decompose into sub-items first, then pipeline per sub-item |

### Intent × Scale Matrix

Not every combination is common, but the system should handle them:

| | Trivial | Small | Standard | Epic |
|---|---------|-------|----------|------|
| **Model** | quick-model | lite spec → implement | full pipeline | decompose → full pipeline |
| **Fix** | quick-model | spec → implement | spec → implement | unusual (suggests deeper problem) |
| **Investigate** | just ask | research | research → spec | research → decompose |
| **Refactor** | quick-model | spec → implement | spec → plan → implement | decompose → spec → plan → implement |
| **Integrate** | quick-model | spec → implement | spec → design → implement | decompose → spec → design → implement |

### How Intent and Scale Are Determined

Options (to be resolved during design):
1. **User-provided tag**: `/spec-model --intent=fix --scale=small "Fix missing redefines in cost_model"`
2. **Interactive determination**: Spec command asks "What are you trying to do?" and "How big is this?"
3. **Auto-detected with confirmation**: Command reads the description, suggests intent/scale, user confirms

Option 2 is likely best for usability — the user describes what they want, the system classifies and confirms.

---

## Part 6: Information Architecture — Designing for N

This section is new, driven by the observation that project definition templates are placeholders designed for "1" when real projects need "N".

### The "0, 1, N" Principle

`SOURCE_INDEX.md` already designs for N — it has a repeatable structure per source entry, works when empty, and scales to dozens of sources. The rest of the project definition needs the same treatment.

### The Six Information Roles Need Homes

From the information-role taxonomy research, six types of information flow through the workflow:

| Role | Information Type | Current Home | Designed for N? | Gap |
|------|-----------------|-------------|-----------------|-----|
| **1. Authority Sources** | External ground truth | `SOURCE_INDEX.md` | Yes | Good |
| **2. Domain Knowledge** | Synthesized understanding | `research/*.md`, `CLAUDE.md` | Partially (research docs scale, but insights are unstructured) | Domain Insights have no home |
| **3. Project Intent** | Goals, scope, priorities | `OVERVIEW.md` | No (single prose section) | Analysis questions not captured; goals not traceable |
| **4. Modeling Requirements** | Verifiable statements | `active/{feature}/spec.md` | Per-feature only | No project-wide registry or aggregation |
| **5. Modeling Decisions** | Architecture & patterns | `design.md`, `MODELING_GUIDE.md` | Partially | No architecture vision; no promotion path |
| **6. Model Artifacts** | SysML models, tests | `models/`, `tests/` | Yes | Good |

### Proposed Project Definition Document Set

Each document follows SOURCE_INDEX.md's pattern: structured, repeatable entries that work when empty and scale gracefully.

| Document | Role | Designs for | Key Sections |
|----------|------|-------------|--------------|
| `OVERVIEW.md` (revised) | Role 3: Project Intent | N goals, N analysis questions | Project Charter, Goals Registry (G-XXX), Analysis Questions, Scope, Success Criteria |
| `ARCHITECTURE.md` (new) | Role 5: Decisions (project-level) | N structural decisions | Model Ecosystem Vision, Package Organization, Dataflow Rules, Interface Contracts, Decision Log |
| `REQUIREMENTS.md` (new) | Role 4: Requirements (cross-feature) | N requirements with traceability | Requirements Registry table (MR-XXX, source, test, status), aggregated from per-feature specs |
| `INSIGHTS.md` (new) | Role 2: Domain Insights | N analysis angles / domain insights | Structured entries (AA-XXX or DI-XXX) with context, model implications, derived requirements |
| `VALIDATION_MATRIX.md` (new) | Cross-cutting | N validation criteria | Target, tolerance, source, requirement, test, status per criterion |
| `MODELING_GUIDE.md` (existing) | Role 5: Conventions | N patterns | Adequate — already designs for N |
| `SOURCE_INDEX.md` (existing) | Role 1: Authority Sources | N sources | Good — reference pattern for others |

### Scaling Strategy

Documents should work at three scales:

**Empty (new project):** Document has section headers and one example entry. Not intimidating, shows the pattern.

**Growing (active project, 10-30 items):** Single markdown file with structured tables. Easy to scan, searchable.

**Large (mature project, 50+ items):** At this point, consider whether the file should split. But markdown tables with 50 rows are still manageable, so the threshold is probably higher than we think. Fusion-tea with ~37 cost categories and ~15 requirements per feature is still well within single-file territory.

If splitting is ever needed, the pattern would be: table-of-contents file with summary rows, linking to individual detail files (like how `active/{feature}/spec.md` already works for per-feature detail).

### Relationship Map

```
OVERVIEW.md (Goals, Analysis Questions)
    │
    │ "we want to answer X" → "models must support X"
    ▼
INSIGHTS.md (Domain Insights / Analysis Angles)
    │
    │ "this insight implies these requirements"
    ▼
REQUIREMENTS.md (Registry, aggregated from per-feature specs)
    │
    │ "requirement MR-XXX is satisfied by..."
    ▼
VALIDATION_MATRIX.md (target, tolerance, test per criterion)
    │
    │ "criterion VC-XXX passes/fails"
    ▼
Model Artifacts (models/, tests/)

ARCHITECTURE.md ←→ MODELING_GUIDE.md
(project decisions)   (standard patterns)
    │
    │ constrains all feature-level work
    ▼
Per-feature: spec.md → design.md → plan.md → implementation
```

### What `/onboard` Should Establish

The enhanced onboard command should set up not just files but the information architecture:

1. Create all documents with scaffold structure (section headers + example entries)
2. Walk the user through:
   - Defining initial goals and analysis questions (OVERVIEW.md)
   - Identifying authority sources (SOURCE_INDEX.md) — already does this
   - Sketching the architecture vision (ARCHITECTURE.md)
   - Capturing any initial domain insights from prior knowledge (INSIGHTS.md)
3. Leave REQUIREMENTS.md and VALIDATION_MATRIX.md empty — these grow as features are specced

### Per-Feature Specs vs. Requirements Registry

**Both should exist.** They serve different purposes:

- **Per-feature spec.md**: Focused context during implementation. Contains the full rationale, the detailed requirements for one feature, and the design constraints. This is what the agent reads when executing `/implement-model`.
- **REQUIREMENTS.md registry**: Aggregated view across all features. Contains the ID, one-line description, source, test, and status for every requirement. This is what `/status` reads for coverage reporting and what `/audit-models` reads for cross-feature verification.

The registry should be maintained by the workflow: when `/spec-model` creates MR-XXX entries in a feature spec, it also adds summary rows to the registry. When `/status close` archives a feature, it updates registry status.

---

## Part 7: Research Split — Internal vs. External

This section is new, driven by the observation that `/research` serves two fundamentally different jobs.

### Two Distinct Jobs

| Aspect | External Research | Internal Analysis |
|--------|------------------|-------------------|
| **Job** | "Learn about a domain topic from authority sources" | "Understand the current state of our models" |
| **Inputs** | Authority sources (SOURCE_INDEX.md), papers, codebases | Model files, test files, existing artifacts |
| **Outputs** | Research document with findings, domain insights | Model state report, health indicators, pattern usage |
| **Agent usage** | sysmlv2-doc-analyzer, source exploration agents | Explore agent, model parsing |
| **Example** | "What does PyFECONS do for magnet costing?" | "What cross-file dependencies exist? Which library defs are unused?" |
| **Downstream** | Feeds INSIGHTS.md, informs specs | Feeds /status, informs refactoring decisions |

### Proposed Split

**`/research`** (external, revised):
- Explore authority sources, extract domain knowledge
- At completion, prompt: "What domain insights or analysis angles emerged?"
- Offer to add structured entries to INSIGHTS.md
- Output: timestamped research document + optional INSIGHTS.md updates

**`/analyze-models`** (internal, new):
- Examine current model state: files, definitions, usages, cross-file dependencies
- Pattern usage analysis: which MODELING_GUIDE patterns are used, which are violated
- Health indicators: test coverage, validation levels passing, technical debt markers
- Output: model state report (feeds into /status and refactoring decisions)

---

## Part 8: Project Management — Script-Backed Reliability

This section is new, driven by the observation that agent-driven PM is unreliable.

### The Reliability Problem

Currently, PM operations rely on agent commands:
- Agent updates backlog status → but might forget or hallucinate
- Agent archives completed work → but might miss files or corrupt structure
- Agent reports project status → but reconstructs state from memory, not file system

**Design principle: State queries should be deterministic (scripts), state changes should be guided (agent commands).**

| Operation | Should Be | Why |
|-----------|-----------|-----|
| "What's the project status?" | Script (read file system) | Deterministic, no hallucination risk |
| "How many requirements have tests?" | Script (parse REQUIREMENTS.md + test files) | Countable, exact answer needed |
| "What should we work on next?" | Agent (interpret data, apply judgment) | Requires context and prioritization |
| "Create a spec for magnet modeling" | Agent (creative, interactive) | Requires user interaction and domain knowledge |
| "Archive this completed feature" | Script with agent confirmation | File operations should be deterministic; agent confirms what to archive |

### Script-Backed Status Engine

A Python module (`src/agentic_mbse/pm/`) that reads the file system and computes status deterministically:

```
$ agentic-mbse status

## Project Dashboard

### Epic: Power Core Components [3/8 items done]
├── [x] Foundation types .............. completed 2026-01-15
├── [x] Power balance calcs .......... completed 2026-01-22
├── [x] Cost pattern fix ............. completed 2026-01-28
├── [ ] Magnet modeling .............. in-progress (phase 2/3)
├── [ ] Blanket & shield ............ ready
├── [ ] Divertor .................... blocked by: Blanket
├── [ ] Turbine plant ............... ready
└── [ ] System integration .......... blocked by: all above

### Requirements Coverage
- Total: 42 MR-XXX across 5 features
- Tested: 31 (74%)
- Untested: 11
- Traced to goals: 38 (90%)
- Untraced: 4

### Architecture Health
- Library files: 5 (3 with full test coverage)
- Cross-file bindings: 12 (2 untested)
- Technical debt items: 3
```

The `/status` **command** then layers agent intelligence on top:
- "Magnet modeling is in-progress but blocked on a design question — consider revisiting the design"
- "4 requirements are untraced to goals — these may be orphaned or the goals need updating"
- "Recommended next action: complete magnet modeling phase 3, then start blanket & shield"

### Visual Output

Markdown-based visualization that renders well in both terminal and IDE preview:
- Text-based progress bars and tree views
- Tables with status indicators
- 80-column compatible for terminal use
- Can be piped to a file for sharing

### Git Integration — Trade-offs

**Revised position (from discussion):** Git should be available as an explicit tool, not automatic.

Trade-offs:
- Power users (like the developer) prefer to withhold commits for IDE diff review
- Less git-savvy users need guided checkpointing
- Automatic commits would break the diff-review workflow

**Approach:**
- Do NOT make git automatic/implicit
- Provide an explicit `/checkpoint` or `/save-progress` command that creates a well-messaged commit when the user asks for it
- For "going back" (backward navigation), the command handles git operations under the hood — the user thinks in workflow terms ("revert to the design phase"), not git terms ("git revert HEAD~3")
- `/onboard` includes a brief section on "how to review changes" pointing users at IDE diff views
- Defer full git integration to a separate design effort

---

## Part 9: Redesign Vision (Revised)

### Core Principles

1. **Design for N** — project definition scales from 3 requirements to 300
2. **Commands do ONE job, informed by shared skills** — knowledge extracted, commands focused
3. **Work-intent-aware routing** — the pipeline adapts based on what the user is doing and at what scale
4. **Non-linear development is the normal case** — backward navigation, concurrent items, refactoring are first-class
5. **Script-backed reliability for PM** — deterministic state queries, agent-driven state changes

### The Redesigned System

```
                    ┌──────────────────────────────────────────────┐
                    │         PROJECT MANAGEMENT LAYER              │
                    │  /status (script-backed + agent intelligence) │
                    │  /backlog (intent + scale tags per item)      │
                    │  agentic-mbse status (CLI, deterministic)     │
                    └──────┬──────────────────────────┬────────────┘
                           │                          │
         ┌─────────────────┼──────────────────────────┼──────────────────┐
         │                 │    FEATURE PIPELINE       │                  │
         │                 │  (adapted per intent      │                  │
         │                 │   and scale)              │                  │
         │    ┌────────────▼──────────────┐            │                  │
         │    │  /spec-model              │            │                  │
         │    │  Job: Define WHAT         │            │                  │
         │    │  Routes by intent:        │            │                  │
         │    │   Model → full spec       │            │                  │
         │    │   Fix → lightweight spec  │            │                  │
         │    │   Investigate → research  │            │                  │
         │    │   Refactor → structural   │            │                  │
         │    │   Integrate → interfaces  │            │                  │
         │    └────────┬──────────────────┘            │                  │
         │             │                               │                  │
         │    ┌────────▼──────────────┐                │                  │
         │    │  /design-model        │◄───────────────┘                  │
         │    │  Job: Decide HOW      │  (backward navigation)            │
         │    └────────┬──────────────┘                                   │
         │             │                                                  │
         │    ┌────────▼──────────────┐                                   │
         │    │  /plan-model          │                                   │
         │    │  Job: Organize WORK   │                                   │
         │    │  (scale-aware phasing)│                                   │
         │    └────────┬──────────────┘                                   │
         │             │                                                  │
         │    ┌────────▼──────────────┐                                   │
         │    │  /implement-model     │──────► /audit-models              │
         │    │  Job: BUILD it        │         Job: VERIFY               │
         │    │  (Stage 0: Understand)│         (checks registry +        │
         │    └───────────────────────┘          validation matrix)       │
         │                                                                │
         │    CROSS-CUTTING                                               │
         │    /quick-model        (trivial/small changes)                 │
         │    /review-model       (design review before implement)        │
         │    /research           (external: domain knowledge)            │
         │    /analyze-models     (internal: model state analysis)        │
         └────────────────────────────────────────────────────────────────┘

         INFORMATION ARCHITECTURE (designed for N):
         [OVERVIEW.md]    [ARCHITECTURE.md]   [REQUIREMENTS.md]
         [INSIGHTS.md]    [VALIDATION_MATRIX]  [SOURCE_INDEX.md]

         SHARED SKILLS (loaded on demand by any command):
         [sysml-conventions] [model-validation] [project-structure]
         [source-traceability] [epic-decomposition] [requirements-tracking]
         [toolkit-awareness]

         AGENTS (parallel specialists, consistently referenced):
         [kerml-expert] [sysml-expert] [syside-expert]
         [sysmlv2-doc-analyzer] [sysmlv2-validator]
```

### Skills: The Knowledge Layer

The biggest architectural change is extracting shared knowledge into skills. This is the single most impactful improvement because it:
- Reduces command size by 50-70%
- Ensures consistency across commands
- Makes knowledge maintainable (change once, applies everywhere)
- Aligns with Claude Code platform design

**Skill: sysml-conventions**
```
Contains:
- Definitions vs usages pattern
- Naming conventions (Title Case, snake_case)
- Attribute declaration syntax
- Units notation rules
- Import patterns
- Documentation requirements (doc comments)
- ADR-002 calculation placement rules
- Common pitfalls and fixes
- Code stencils for common patterns

Referenced by: design-model, implement-model, audit-models, quick-model
```

**Skill: model-validation**
```
Contains:
- 8-level quality pyramid description
- CLI commands for validation
- Level-by-level criteria and interpretation
- Regression testing patterns (pytest tests/models/)
- Integration test patterns
- What constitutes pass/warn/fail

Referenced by: design-model, implement-model, audit-models, plan-model
```

**Skill: project-structure**
```
Contains:
- Library vs designs organization
- File naming and placement rules
- Cross-file binding patterns (EXPOSE pattern)
- Unidirectional dataflow rules
- models/README.md structure guidance
- When to add new library files vs extend existing

Referenced by: design-model, implement-model, spec-model, onboard
```

**Skill: source-traceability**
```
Contains:
- SOURCE_INDEX.md format and management
- Traceability approach (codebase -> model -> test)
- Doc comment requirements for traceability
- How to cite sources (line numbers, equations, sections)
- Traceability matrix maintenance

Referenced by: design-model, spec-model, audit-models, research
```

**Skill: epic-decomposition**
```
Contains:
- Goldilocks principle adapted for modeling (0.5-2 days per item)
- Work item taxonomy (intent × scale matrix)
- Task type cohesion for modeling work:
  - Research (domain exploration, source analysis)
  - Foundation (library definitions, base types)
  - Feature (specific model components)
  - Integration (cross-file bindings, system assembly)
  - Validation (testing, auditing, documentation)
  - Refactoring (reorganization, pattern fixes)
  - Fix (correct known issues)
  - Investigation (explore unknowns)
- Epic template for modeling projects
- Decomposition process and checklist
- Anti-patterns to avoid
- When to decompose vs. just do it

Referenced by: backlog (decompose mode), status, onboard
```

**Skill: requirements-tracking** (new)
```
Contains:
- REQUIREMENTS.md registry format
- MR-XXX lifecycle (created in spec → tested in implement → verified in audit)
- Aggregation from per-feature specs to project registry
- Traceability links (goal → requirement → test)
- VALIDATION_MATRIX.md format
- Coverage metrics and reporting

Referenced by: spec-model, audit-models, status
```

### Commands: The Job Layer

Each command becomes focused on its JOB, referencing skills for knowledge:

**`/spec-model` (~200 lines)**
```
Job: Help the user define WHAT needs to be modeled

Work-intent-aware routing:
- Determine intent (Model/Fix/Investigate/Refactor/Integrate) and scale
- Adapt stages based on intent (see taxonomy)

Stages (for "Model" intent, Standard scale):
1. Context: Read existing models, check backlog, check INSIGHTS.md for relevant angles
2. Scope: Interactively define boundaries with user
3. Requirements: Define success criteria (human + machine-checkable)
4. Document: Create spec.md + update REQUIREMENTS.md registry

References skills: project-structure, source-traceability, requirements-tracking

User decisions: Scope boundaries, success criteria, priority, intent confirmation
```

**`/design-model` (~300 lines)**
```
Job: Help the user decide HOW to model it

Stages:
1. Setup: Read spec, check library, identify gaps
2. Research: Parallel discovery (library + SysML docs + sources)
3. Architecture: Present alternatives, get user decisions
4. Prototype: Build working prototype, validate (Levels 1-3)
5. Approve: Present design + validation evidence

References skills: sysml-conventions, project-structure,
                   model-validation, source-traceability

User decisions: Architecture approach, component interfaces,
                where definitions live, constraint placement
```

**`/plan-model` (~200 lines)**
```
Job: Help the user organize the implementation WORK

Scale-aware: Small items get 1-2 phases; Standard items get 3-5; Epic items get decomposed first

Stages:
1. Read: Understand design + prototype state
2. Phase: Break refinement into verifiable chunks
3. Validate: Check plan feasibility
4. Document: Create plan.md with checkboxes

References skills: model-validation

User decisions: Phase ordering, scope per phase, risk priorities
```

**`/implement-model` (~200 lines)**
```
Job: Help the user BUILD the model correctly

Stages:
0. Understand: Read design rationale, offer exploration (from Python pattern)
1. Scope: Confirm which phases, one-by-one vs batch
2. Execute: Implement per plan, validate after each phase
3. Complete: Final validation, update progress, update REQUIREMENTS.md status

Backward navigation: If design flaw discovered, offer to update design.md,
re-validate prototype, adjust plan, then resume

References skills: sysml-conventions, model-validation, project-structure

User decisions: Execution approach, deviation handling,
                phase completion approval, backward navigation triggers
```

**`/audit-models` (~200 lines)**
```
Job: Help the user VERIFY model correctness

Checks against: REQUIREMENTS.md registry (cross-feature), VALIDATION_MATRIX.md,
per-feature spec, authority sources

Stages:
1. Scope: What to audit, what baseline to compare against
2. Inspect: Extract model parameters systematically
3. Compare: Check against sources with clear pass/warn/fail
4. Report: Generate actionable audit report, update VALIDATION_MATRIX.md

References skills: model-validation, source-traceability, requirements-tracking

User decisions: Audit scope, acceptable deviations, action items
```

### New Commands

**`/quick-model` (~120 lines)**
```
Job: Make a small, well-understood change quickly

When to use: Trivial or Small scale, any intent
Guard rails: Scope check — if change is bigger than expected, redirect to full pipeline

Process:
1. Understand what needs to change
2. Make the change
3. Validate (quality pyramid + regression)
4. Document what changed

References skills: sysml-conventions, model-validation
```

**`/review-model` (~250 lines)**
```
Job: Review a design before implementation

6 review dimensions (adapted from Python _my_review_design):
1. Spec Compliance — does design address all MR-XXX requirements?
2. Pattern Consistency — does it follow MODELING_GUIDE patterns?
3. Library/Designs Separation — are definitions vs usages correct?
4. Traceability Completeness — are all sources cited?
5. Constraint Coverage — are physics/engineering limits defined?
6. Validation Readiness — will it pass quality pyramid levels 1-3?

Output: Pass/Concerns/Fail per dimension with actionable feedback
```

**`/analyze-models` (~200 lines)**
```
Job: Understand the current state of the models (internal research)

Outputs:
- Model state report: files, definitions, usages, cross-file dependencies
- Pattern usage analysis: which MODELING_GUIDE patterns are used/violated
- Health indicators: test coverage, validation levels, technical debt markers
- Feeds into /status and refactoring decisions
```

**`/status` (~250 lines)**
```
Job: Understand project state and decide what to do next

Runs `agentic-mbse status` (script-backed) then adds agent intelligence

Modes:
- Default: Script data + intelligent interpretation + recommended next action
- /status decompose <epic>: Break epic into work items with intent/scale tags
- /status close [item]: Verify completion, archive, update registry

References skills: epic-decomposition (for decompose mode),
                   requirements-tracking (for coverage reporting)
```

### Project Templates: Enhanced for N

New and revised templates:

| Template | Type | Scaling Pattern |
|----------|------|-----------------|
| `OVERVIEW.md.template` (revised) | User-owned | N goals (G-XXX), N analysis questions, structured charter |
| `ARCHITECTURE.md.template` (new) | User-owned | N structural decisions, vision statement, dataflow rules |
| `REQUIREMENTS.md.template` (new) | User-owned | N requirements (MR-XXX) with source/test/status columns |
| `INSIGHTS.md.template` (new) | User-owned | N domain insights (DI-XXX) with context/implications/derived reqs |
| `VALIDATION_MATRIX.md.template` (new) | User-owned | N criteria (VC-XXX) with target/tolerance/source/test/status |
| `EPIC_GUIDE.md.template` (new) | Tool-owned | Work item taxonomy, Goldilocks principle, decomposition process |
| `epic_template.md.template` (new) | Tool-owned | Standard epic structure with intent/scale fields |

---

## Part 10: Answering the Original Questions (Revised)

### Q1: Jobs to be done and user expectations?

Each stage has a clear **user decision** at its core:
- **Spec**: "Is this the right scope?" (scope approval) — **now adapted by work intent**
- **Design**: "Is this the right approach?" (architecture approval with prototype evidence)
- **Plan**: "Is this the right order?" (phase approval) — **now scale-aware**
- **Implement**: "Does each phase pass?" (phase completion approval) — **now with Stage 0 and backward navigation**
- **Audit**: "Is this correct?" (verification approval) — **now checks cross-feature registry**

The user reviews documents focused on ENGINEERING decisions, not SysML syntax. SysML knowledge lives in skills that inform Claude's work without burdening the user.

**De-risking role of each stage**: Each stage catches a different class of error:
- Spec catches "wrong thing" errors (building what wasn't needed)
- Design catches "wrong structure" errors (modeling that won't scale/validate)
- Plan catches "wrong order" errors (attempting things before prerequisites)
- Implement catches "wrong details" errors (syntax, values, bindings)
- Audit catches "wrong results" errors (values don't match sources)

### Q2: Practical approach for large projects?

Yes, with the additions described:

1. **Information architecture designed for N** — structured registries for requirements, insights, validation criteria
2. **Architecture vision document** — project-level structural decisions before feature work begins
3. **Epic decomposition** via the `epic-decomposition` skill with work item taxonomy (intent × scale)
4. **Script-backed status** with visual dashboard — deterministic state tracking, no hallucination
5. **Scale-aware entry points** — `/quick-model` for trivial changes, abbreviated pipeline for small items
6. **Refactoring and integration** as recognized work intents with their own pipeline paths
7. **Integration testing** growing with the project via `pytest tests/models/`

The fusion-tea project needs:
- An architecture vision document (ARCHITECTURE.md)
- Populated REQUIREMENTS.md registry aggregating across features
- INSIGHTS.md capturing the analysis angles that currently live in conversation
- Epic decomposition of "Power Core Components" with intent/scale tags per sub-item
- `agentic-mbse status` producing a reliable dashboard

### Q3: Alignment with Claude Code best practices?

The redesign aligns by:

1. **Skills for shared knowledge** (sysml-conventions, model-validation, requirements-tracking, etc.) — platform's primary reuse mechanism
2. **Commands under 500 lines** (target: 200-300 each) — recommended by Claude Code docs
3. **Agents for context isolation** (kept as parallel specialists with standardized references) — empirically better recall than consolidated agents
4. **CLAUDE.md stays lean** — only project-specific essentials, not general SysML knowledge

The current system violates platform intent by:
- Embedding 600+ lines of shared knowledge directly in commands
- Referencing agents inconsistently across commands
- Not using skills at all for reusable domain knowledge

### Q4: Robustness for non-linear development?

The redesign handles non-linearity through:

1. **Work intent taxonomy**: Fix, Investigate, Refactor, Integrate each get their own pipeline path — not everything goes through full spec → design → plan → implement
2. **Scale-aware entry points**: `/quick-model` for trivial changes, abbreviated pipelines for small items, decomposition for epics
3. **Script-backed state tracking**: `/status` knows what's in-progress, paused, completed — deterministically, not from agent memory
4. **Backward navigation**: `/implement-model` can detect design flaws and route back to design update → re-validate → adjust plan → resume
5. **Concurrent work items**: Status engine tracks multiple active/paused items; work items have explicit states
6. **Cross-cutting workflows**: Refactoring and Integration are recognized intent types with defined pipeline paths
7. **Regression safety**: `pytest tests/models/` integrated into implement and audit commands via the `model-validation` skill; VALIDATION_MATRIX.md tracks what's passing

The key philosophical shift is from "pipeline" to "toolkit with recommended paths." The recommended path IS spec → design → plan → implement → audit. But the system also supports:
- Skip spec for trivially-scoped work → `/quick-model`
- Skip design for known fixes → Fix intent routes spec → implement
- Go back from implement to design when approach doesn't work → backward navigation
- Pause one work item to handle another → status engine tracks states
- Refactor across multiple completed features → Refactor intent with its own pipeline

---

## Recommendations (Revised Priority Order)

### Priority 0: Information Architecture Design (prerequisite for everything)

Design the document set, relationships, and scaling strategy. This must be resolved before skills, commands, or PM can be designed — they all depend on knowing where information lives.

Key decisions:
- Document set and structure (proposed in Part 6)
- Scaling strategy per document
- What `/onboard` creates and walks through
- Per-feature spec.md vs. requirements registry relationship (both, as proposed)

### Priority 1: Skills Extraction (highest implementation impact)

Create 6-7 skills from knowledge currently embedded in commands. This alone would:
- Reduce average command length from ~476 to ~250 lines
- Ensure consistency across commands
- Make knowledge maintainable
- Align with Claude Code platform design

### Priority 2: Work Item Taxonomy + Scale Awareness

Define and implement the intent × scale matrix. This changes how `/spec-model` routes work, what `/quick-model` handles, and how the backlog tracks items.

### Priority 3: Script-Backed PM

Build `agentic-mbse status` as a Python CLI command that reads file system state deterministically. Then build the `/status` command that layers agent intelligence on top.

### Priority 4: Command Redesign

With skills extracted, information architecture defined, and taxonomy in place, refactor all commands to be job-focused, skill-referencing, and intent-aware.

### Priority 5: Project Definition Templates

Create/revise templates for the full document set. Add to `agentic-mbse init`.

### Priority 6: Agent Reference Standardization

Audit all commands for agent references. Standardize invocation patterns. Document when to use which agent. Keep all existing agents.

## Open Questions

1. **Document scaling strategy**: Should the requirements registry be a single markdown table or a directory of per-requirement files? Proposed answer: single file up to ~100 items, then consider splitting. Validate against fusion-tea.

2. **Architecture Vision placement**: New standalone `ARCHITECTURE.md`? A major section of `OVERVIEW.md`? Proposed answer: standalone — it's a distinct concern (structural "how") from project intent ("what" and "why").

3. **Domain Insights capture UX**: Explicit command? Prompt at end of `/research`? Section in `/spec-model`? Proposed answer: prompt at end of `/research` (most natural point of discovery) + `/spec-model` reads INSIGHTS.md for relevant angles. Explicit `/capture-insight` command is nice-to-have but may be overkill — a user can always add to INSIGHTS.md directly.

4. **Skill loading strategy**: Skills are loaded into the main conversation context. With 6-7 skills, what's the context window impact? Should commands load all referenced skills or only the ones needed for the current stage? Needs measurement.

5. **Backward navigation mechanism**: When implementation reveals a design flaw, what's the concrete process? Proposed: command detects the problem → offers to update design.md → re-validates prototype → updates plan.md → resumes implementation. How much automation vs. guidance needs testing.

6. **Work intent determination UX**: User-provided tag vs. interactive determination vs. auto-detection? Proposed: interactive — command asks "What are you trying to do?" with clear options, user confirms. Tags can be optional shorthand for power users.

7. **Should prototyping stay in design or become its own command?** Current design embeds it (Stages 6-8). It could be a separate `/prototype-model` for cleaner separation, but this adds another step to the pipeline. Proposed: keep embedded — it's the strongest part of the design command.

8. **Is there a role for hooks in the workflow?** E.g., auto-running validation after model file writes, blocking commits with parse errors. Deferred to separate design effort.

9. **How do we handle the "two contexts" problem?** This repo serves both as the toolkit (Python code) and as a template for target repos. Skills/commands that reference `docs/` paths need to be rewritten during `agentic-mbse init` with correct absolute paths. Existing mechanism works but needs extension for new skills.

---

## Related Research

| Document | Contribution to This Design |
|----------|-----------------------------|
| `20260126-161628_python-vs-mbse-command-comparison.md` | Quantified gaps: commands 2x too long, PM missing, 7 command types absent |
| `20260126-202931_requirements-goal-tracking-pipeline.md` | Requirements dropping problem, Analysis Angles concept, validation criteria lifecycle |
| `20260130-235423_information-role-taxonomy.md` | Six information roles, traceability gaps, domain insights as weakest link |

---

**Last Updated**: 2026-01-31
**Status**: Working design concept — ready for epic scoping when appropriate

---
date: 2026-01-30T23:54:23-08:00
researcher: Claude
topic: "Information Role Taxonomy for MBSE Modeling Projects"
tags: [research, taxonomy, information-architecture, requirements, workflow]
status: draft-v2
last_updated: 2026-01-31
---

# Research: Information Role Taxonomy for MBSE Modeling Projects

**Date**: 2026-01-30 23:54 PST (v2: 2026-01-31)
**Researcher**: Claude
**Research Type**: Concept / Information Architecture

## Research Question

What types of information exist in an agentic-mbse modeling project, what roles do they play, and how do they relate to each other through the workflow?

## Context

This taxonomy was developed by examining:
- The agentic-mbse templates and commands (`project_templates/`, `claude/commands/`, `docs/`)
- The fusion-tea project as a real-world application (`modeling_pm/`, `SOURCE_INDEX.md`, `models/`)
- 14 research documents totaling ~9,000 lines in fusion-tea
- Active work items (specs, designs) across 3 features
- The requirements-tracking pipeline research (20260126-202931)

The goal is to formalize what types of information flow through the MBSE workflow, identify where structured support exists vs. where information falls through the cracks, and inform the design of revised commands and project management tooling.

---

## The Five Information Roles

```
                    ┌──────────────────────┐
                    │   PROJECT INTENT     │
                    │  (goals, scope,      │
                    │   analysis questions) │
                    └─────────┬────────────┘
                              │ drives
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    │                         v                         │
    │            ┌────────────────────────┐              │
    │            │  MODELING REQUIREMENTS │              │
    │            │  (patterns, rules,     │              │
    │            │   validation criteria) │              │
    │            └────────────┬───────────┘              │
    │                         │ constrains              │
    │                         │                         │
    │   ┌─────────────────────┼──────────────────┐      │
    │   │                     v                  │      │
    │   │        ┌────────────────────────┐      │      │
    │   │        │  MODEL IMPLEMENTATION  │      │      │
    │   │        │  (architecture, epics, │      │      │
    │   │        │   spec/design/plan/    │      │      │
    │   │        │   implement cycle)     │      │      │
    │   │        └────────────┬───────────┘      │      │
    │   │                     │                  │      │
    │   │    informs ┌────────┘                  │      │
    │   │            │                           │      │
    │   │            v                           │      │
    │   │  ┌─────────────────────┐               │      │
    │   │  │ SYSTEM VERIFICATION │               │      │
    │   │  │ (reasonableness,    │               │      │
    │   │  │  energy balances,   │               │      │
    │   │  │  output probing)    │               │      │
    │   │  └─────────────────────┘               │      │
    │   │                                        │      │
    │   └────────────────────────────────────────┘      │
    │                                                   │
    │   ┌───────────────────────────────────────────┐   │
    │   │          DATA SOURCES                     │   │
    │   │  (external refs, agent research,          │   │
    │   │   user notes)                             │   │
    │   │                                           │   │
    │   │        ┌─── curation gate ───┐            │   │
    │   │        v                     │            │   │
    │   │  DOMAIN KNOWLEDGE BASE       │            │   │
    │   │  (approved, actionable       │            │   │
    │   │   information for modeling)  │            │   │
    │   └──────────────┬───────────────┘────────────┘   │
    │                  │                                │
    │                  │ feeds                          │
    └──────────────────┼────────────────────────────────┘
                       │
           (feeds into Modeling Requirements,
            Model Implementation, and
            System Verification)
```

### Feedback Loops

```
MODEL IMPLEMENTATION ──discoveries──> DATA SOURCES
    (new findings during design/implement feed back as data)

MODEL IMPLEMENTATION ──learnings───> PROCESS KNOWLEDGE (separate concern)
    (modeling patterns, tool usage — captured via /record-learning)

SYSTEM VERIFICATION ──gaps─────────> PROJECT INTENT
    (verification failures may refine goals or reveal new analysis questions)

SYSTEM VERIFICATION ──failures─────> MODEL IMPLEMENTATION
    (specific failures drive new work items)

DOMAIN KNOWLEDGE BASE ──feasibility──> PROJECT INTENT
    (what's possible may refine what we aim for)
```

---

## Role 1: Project Intent

**Purpose**: The starting point. Why this project exists, what it aims to achieve, what questions the models must answer. This exists before any data, research, or modeling work. It is the demand signal that everything else serves.

**Current storage**: `OVERVIEW.md`, `BACKLOG.md`, `CLAUDE.md` (project goals)

### Sub-types

| Sub-type | What it contains | Example (fusion-tea) | Current home |
|----------|-----------------|----------------------|--------------|
| **Goals** | High-level objectives | "Bottom-up LCOE estimation from components" | OVERVIEW.md success criteria |
| **Scope boundaries** | What's in and out | "MVP: CAS20 direct costs; defer CAS70-90 to Phase 2" | OVERVIEW.md, BACKLOG.md |
| **Priorities** | Ordering of work | P0: Foundation + Power Balance; P1: Power Core | BACKLOG.md |
| **Analysis questions** | What the models must be able to answer | "What's the capital vs O&M breakdown in LCOE?" | **Not captured** |
| **Acceptance criteria** | How we know we're done (project-level) | "LCOE within +/-5% of PyFECONS" | OVERVIEW.md (prose) |

### Analysis Questions

Analysis Questions deserve special attention. They express the *analytical purpose* of the models — not just "build a cost model" but "the cost model must let us compare energy capture methods side-by-side" or "we need to see sensitivity of LCOE to conversion efficiency."

These are distinct from Goals (which are broader) and from Modeling Requirements (which are specific technical constraints). Analysis Questions sit between the two: they translate goals into implications for model structure and output visibility.

Examples:
- "Compare LCOE across energy capture methods" → models must support parametric comparison
- "Show capital vs O&M vs fuel breakdown" → LCOE calc must expose intermediate values
- "What's the steam turbine contribution to OpEx?" → turbine costs must be tracked separately

Currently these live only in conversation or prose. They are the primary mechanism by which goals get "dropped" — a goal says "LCOE estimation" but nobody writes down that the estimation must support breakdown analysis, so the breakdown outputs never get built.

### Relationships

- **Drives** Modeling Requirements — goals and analysis questions determine what patterns and rules to enforce
- **Drives** Model Implementation — scope and priorities determine what gets built and in what order
- **May be refined by** Domain Knowledge Base — feasibility discoveries may adjust goals
- **May be refined by** System Verification — verification gaps may surface new analysis questions

### Current Support

- OVERVIEW.md captures goals and success criteria in prose
- BACKLOG.md provides prioritized work breakdown
- Gaps:
  - Goals are prose with no structured IDs or traceability
  - Analysis Questions are not captured at all
  - No mechanism to verify that goals are actually addressed by the final models
  - Project-level acceptance criteria are vague rather than specific

---

## Role 2: Data Sources

**Purpose**: All external and internal information that could inform modeling work. This is a broad category that encompasses everything from authoritative reference implementations to agent-generated research to user notes. Crucially, **data sources are not automatically trusted** — they must pass through an explicit curation gate before becoming part of the Domain Knowledge Base.

**Current storage**: `SOURCE_INDEX.md`, `modeling_pm/research/*.md`, user notes

### Sub-types by Origin

| Sub-type | Description | Trust level | Example (fusion-tea) |
|----------|-------------|-------------|----------------------|
| **Reference implementations** | Existing codebases with known algorithms | High (but still requires review) | PyFECONS |
| **Published documentation** | Papers, specs, standards, textbooks | High (peer-reviewed) | ITER Physics Basis, ARPA-E CAS standard |
| **Data files** | Parameter tables, material properties, cost databases | Medium (depends on provenance) | Material properties CSV |
| **Agent research** | Research reports generated by AI agents via `/research` | **Requires approval** — not ground truth | `research/20260123-pyfecons-library-mapping.md` |
| **User notes** | 1st-degree authored observations, meeting notes, domain expertise | Medium-high (direct human authorship) | "Steam turbine alone = 0.5 cents/kWh" |
| **Web/external search** | Information retrieved by agents from external sources | **Requires approval** — provenance uncertain | Search results, fetched documentation |

### The Curation Gate

The key distinction in this taxonomy is that raw Data Sources do not directly feed modeling work. There is an explicit step — the **curation gate** — where information is reviewed and approved before entering the Domain Knowledge Base:

```
DATA SOURCES (raw, mixed trust)
    │
    ├─ Agent produces research report
    ├─ User provides notes or references
    ├─ External source registered in SOURCE_INDEX
    │
    v
┌─────────────────────────────┐
│       CURATION GATE         │
│                             │
│  - User reviews & approves  │
│  - "Incorporate this data"  │
│  - Explicit acceptance      │
└─────────────┬───────────────┘
              │
              v
   DOMAIN KNOWLEDGE BASE
   (approved, actionable)
```

Mechanisms for passing through the gate:
- User explicitly states "we want to incorporate this data"
- User approves an agent research report's recommendations
- User registers a source in SOURCE_INDEX.md with validation criteria
- User marks specific findings as accepted

### Current Support

- SOURCE_INDEX.md tracks external sources with type/location/use-for/validation
- `/manage-sources` command handles source registration
- `/research` command produces research documents
- Gaps:
  - No formal distinction between "raw research" and "approved knowledge"
  - Agent research output is treated the same as user-provided information
  - No approval/status tracking on research documents
  - No mechanism to track which parts of a source have been explored

---

## Role 3: Domain Knowledge Base

**Purpose**: The curated, approved body of information that the models should represent. This is what has passed through the curation gate — the team has decided this information is trustworthy and relevant. It is the **feed** for modeling work.

**Current storage**: Implicitly spread across `CLAUDE.md` (domain concepts), approved research docs, `SOURCE_INDEX.md` (validated sources), `LOCAL_GUIDE.md`

### Sub-types

| Sub-type | What it contains | Example (fusion-tea) |
|----------|-----------------|----------------------|
| **Structural knowledge** | How the domain system is organized | CAS hierarchy with 37 cost categories; reactor type taxonomy (MFE/IFE/MIF) |
| **Formulas & algorithms** | Specific calculations the models must replicate | `LCOE = (C900000 + (C700000+C800000)*inflation) / (8760*p_net*avail)` |
| **Parameters & constants** | Approved numerical values | `plant_availability = 0.85`, `discount_rate = 0.09` |
| **Domain patterns** | Recurring structures in the problem domain | Leaf vs Assembly costing, CAS-aligned rollups, component reuse patterns |
| **Domain insights** | Interpretive knowledge that shapes analysis priorities | "Steam turbine alone contributes ~0.5 cents/kWh — energy capture method is a key cost driver" |
| **Estimation metadata** | Confidence and accuracy context for values | AACE Class 4: -30% to +50% for magnets; Class 3 for buildings |
| **Validation baselines** | Known-good values for comparison | "CATF baseline: p_net = 520 MW, total capital cost = $X B" |

### Domain Insights

Domain Insights are a sub-type that warrants specific tooling support. They are:
- **Not requirements** (they don't say "the model SHALL...")
- **Not formulas** (they don't specify a calculation)
- **Not parameters** (they aren't a single value)

They are **interpretive perspectives** that bridge Domain Knowledge and Project Intent. They say "here's something important about the domain that has implications for what our models need to capture and how we analyze results."

Examples:
- "Steam turbine OpEx dominates — 0.5 cents/kWh contribution" → implies turbine costs must be tracked separately
- "60% of PyFECONS code is shared across reactor types" → implies library/specialization architecture
- "AACE Class 4 estimates have -30/+50% uncertainty" → implies validation tolerances should reflect this

Domain Insights often originate as Analysis Questions (Role 1) meeting domain facts (Role 2/3). The insight is the synthesis: "Given our goal to compare energy capture methods, and given that steam turbine costs dominate, the models must track turbine costs as a separate visible output."

### Relationships

- **Curated from** Data Sources — passes through the curation gate
- **Feeds** Modeling Requirements — domain patterns and formulas become enforceable rules
- **Feeds** Model Implementation — formulas, parameters, and structural knowledge are directly used during spec/design/implement
- **Feeds** System Verification — validation baselines define expected outputs
- **May refine** Project Intent — feasibility discoveries may adjust goals

### Current Support

- No single home for the Domain Knowledge Base as a concept
- Closest existing mechanism: `CLAUDE.md` domain concepts section + approved research docs
- `LOCAL_GUIDE.md` could serve this role but is currently minimal
- Gaps:
  - No explicit curation/approval status on research documents
  - Domain Knowledge is scattered across many files with no aggregation
  - No structured capture for Domain Insights
  - Formulas, parameters, patterns, and insights are mixed together in prose

---

## Role 4: Modeling Requirements

**Purpose**: High-level requirements and patterns that derive from Project Intent and are informed by the Domain Knowledge Base. These are the rules and constraints that govern *how* modeling is done — not individual feature specs (those live within Model Implementation), but the project-wide standards that all modeling work must follow.

These are **extensions** of the default requirements provided by `agentic-mbse` (the standard MODELING_GUIDE patterns, validation pyramid levels, etc.). Projects add their own on top.

**Current storage**: Partially in `MODELING_GUIDE.md` (defaults), `COST_MODELING.md` (project patterns), scattered in research docs (enforcement rules E1-E6)

### How Requirements Derive from Intent

| Project Intent (Goal/Analysis Question) | Derived Modeling Requirement |
|-----------------------------------------|------------------------------|
| "Traceable LCOE outputs with cost breakdown" | Enforce Costed Component pattern; all cost-bearing parts must expose capital_cost, raw_material_cost, etc. |
| "Compare energy capture methods side-by-side" | EXPOSE pattern required for all intermediate cost values; multi-output calc defs mandatory |
| "Validate against PyFECONS within tolerance" | All calc defs must cite PyFECONS source file:line; numerical validation criteria required |
| "Support multiple reactor types" | Library/Designs separation enforced; shared vs. specific component taxonomy |

### Sub-types

| Sub-type | Description | Example | Enforcement |
|----------|-------------|---------|-------------|
| **Modeling patterns** | Required SysML idioms for this project | Costed Component interface, EXPOSE pattern for cost visibility | Design review, validation rules |
| **Structural rules** | Package organization, file naming, import conventions | "Calc defs in library/calculations/; unidirectional imports only" | Validation Level 7 |
| **Documentation rules** | What model elements must document | "Every calc def must have doc comment with Source, Reference, Last Updated" | Validation Level 6 |
| **Enforcement rules** | Machine-checkable constraints | E1: Every :> 'Costed Component' must expose capital_cost | Validation tooling (future) |
| **Naming conventions** | Standardized names for elements | "'cost_model' as standard calc usage name" | Design review |

### Each Requirement Has Validation

Every modeling requirement should specify both criteria and method:

- **Criteria**: What constitutes compliance (e.g., "all leaf parts have a cost_model calc usage")
- **Method**: How to check it (e.g., "AST traversal via validation Level 9 rule", "design review checklist", "regression test")

This is distinct from per-work-item verification (which happens within Model Implementation) and from System Verification (which checks the running system).

### Relationships

- **Driven by** Project Intent — goals and analysis questions determine what patterns to enforce
- **Informed by** Domain Knowledge Base — domain patterns shape what rules make sense
- **Constrains** Model Implementation — all implementation work must comply
- **Extends** agentic-mbse defaults — projects add their own rules on top of MODELING_GUIDE

### Current Support

- MODELING_GUIDE.md provides baseline patterns (EXPOSE, Definitions vs Usages, ADR-002)
- COST_MODELING.md captures fusion-tea-specific patterns (Costed Component, Leaf vs Assembly)
- Enforcement rules E1-E6 identified in research but not formalized
- Gaps:
  - No single registry of project-level modeling requirements
  - No explicit link from requirements back to the goals they serve
  - Enforcement rules live in research prose, not connected to validation tooling
  - No distinction between agentic-mbse defaults and project extensions

---

## Role 5: Model Implementation

**Purpose**: The entire process of building models — from high-level architecture through epics and work items to the spec/design/plan/implement cycle. This is a large category encompassing multiple stages and sub-processes, all of which produce artifacts along the way.

**Current storage**: `modeling_pm/active/`, `modeling_pm/backlog/`, `models/`

### Stages

#### 5a. Architecture

High-level decisions about model organization that span multiple features.

| What | Example | Current home |
|------|---------|--------------|
| Package structure | `models/library/` vs `models/designs/` split | MODELING_PROCESS.md, OVERVIEW.md |
| Dataflow architecture | Geometry → Structural → Physics → System (unidirectional) | MODELING_PROCESS.md |
| Component taxonomy | Shared (buildings, turbine) vs Specific (magnets/lasers) | Research docs, design.md files |
| Cross-cutting patterns | Costed Component interface, EXPOSE visibility | COST_MODELING.md |

#### 5b. Epics (Chunks of Work)

Scoped units of modeling work with clear verification criteria.

| What | Example | Current home |
|------|---------|--------------|
| Epic definition | "Foundation Package: types, units, materials" | BACKLOG.md |
| Scope | Which model elements, which files | Epic description |
| Verification approach | How to know the epic is done | Epic acceptance criteria |
| Dependencies | What must be built first | Epic ordering in BACKLOG.md |

#### 5c. Work Item Cycle (per feature)

The spec → design → plan → implement subprocess for each work item:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌─────────────┐
│   SPEC   │────>│  DESIGN  │────>│   PLAN   │────>│  IMPLEMENT  │
│          │     │          │     │          │     │             │
│ - MR-XXX │     │ - Arch   │     │ - Phases │     │ - SysML     │
│ - Success│     │ - Pattern│     │ - Gates  │     │ - Tests     │
│   criteria     │ - Trade  │     │ - Verify │     │ - Doc       │
│ - Source │     │   offs   │     │   steps  │     │   comments  │
│   refs   │     │ - Proto  │     │          │     │             │
└──────────┘     └──────────┘     └──────────┘     └─────────────┘
```

Each stage produces artifacts in `modeling_pm/active/{feature}/`:
- `spec.md` — Feature-level modeling requirements (MR-XXX) with validation methods
- `design.md` — Architecture decisions, SysML patterns, prototype
- `plan.md` — Implementation phases with verification gates
- SysML files in `models/` — The actual model artifacts

**Per-work-item verification** happens within this cycle: the spec defines what to check, the plan defines verification gates, and implementation runs the checks. This is internal to the work item and does not need separate formalization — it is governed by the MBSE workflow process.

#### 5d. Model Artifacts (Outputs)

The tangible products of implementation:

| Sub-type | What it contains | Example |
|----------|-----------------|---------|
| **Definitions** | Reusable types (part def, calc def, enum def) | `library/foundation/types.sysml` |
| **Usages** | Specific design instances | `designs/catf_mfe/reactor.sysml` |
| **Tests** | Regression tests validating model structure and values | `tests/models/test_foundation.py` |
| **In-model documentation** | Doc comments with source citations | `doc /* Source: PyFECONS PowerBalance.py:94 */` |

#### Decision Lifecycle (Feedback)

Discoveries during implementation have a promotion path:

```
Feature-specific decision (design.md)
    │
    │ validated through implementation
    v
Project pattern (LOCAL_GUIDE.md, COST_MODELING.md)
    │
    │ generalized across projects
    v
Standard pattern (MODELING_GUIDE.md)
```

Implementation discoveries also feed back to Data Sources (new findings about the domain) and may surface new requirements.

### Relationships

- **Constrained by** Modeling Requirements — all work must comply with project-level rules
- **Informed by** Domain Knowledge Base — formulas, parameters, structural knowledge used directly
- **Driven by** Project Intent — scope and priorities determine what gets built
- **Feeds back to** Data Sources — discoveries during implementation become new source material
- **Produces inputs for** System Verification — implemented models are what gets verified

### Current Support

- Well-established spec/design/plan/implement workflow
- BACKLOG.md for work item tracking
- Detailed spec and design templates
- 8-level validation pyramid for model quality
- Gaps:
  - No EPIC_GUIDE for modeling work decomposition
  - No formal architecture stage (happens ad-hoc in early designs)
  - No project-wide view of implementation status across features

---

## Role 6: System Verification

**Purpose**: Dedicated checks on the implemented system that go beyond per-work-item verification. These verify the model *as a whole* against expectations — reasonableness, physical consistency, and output behavior. These are specific to the model implementation and the downstream pipeline (sysml-codegen → teax).

**Current storage**: No dedicated home. Partially in spec.md validation criteria, partially in research docs (validation layers from cost-patterns research).

### Sub-types

| Sub-type | What it checks | Example | When it runs |
|----------|---------------|---------|--------------|
| **Reasonableness checks** | Outputs are in expected ballpark | "Total capital cost between $3B-$15B", "LCOE between 30-200 $/MWh" | After teax simulation |
| **Relationship probing** | Inputs and outputs vary in expected directions | "Increasing magnet field strength increases magnet cost", "Higher availability reduces LCOE" | Sensitivity analysis |
| **Physical consistency** | Conservation laws, balance equations hold | "Sum of subsystem powers = total thermal power (energy balance)" | After model integration |
| **Cross-system checks** | Aggregation and rollup consistency | "Sum of child costs = parent cost", "CAS subtotals sum to CAS total" | After teax simulation |
| **Baseline comparison** | Outputs match reference implementation | "LCOE within +/-5% of PyFECONS CATF configuration" | After teax simulation |

### Registry Concept

System Verifications warrant a dedicated registry because they:
- Apply to the integrated system, not individual features
- Need to be run repeatedly as the models evolve
- Have specific expected values, tolerances, and pass/fail criteria
- May require specific test configurations (input sets, parameter sweeps)

Proposed structure:

| ID | Description | Type | Expected | Tolerance | Source | Status |
|----|-------------|------|----------|-----------|--------|--------|
| SV-001 | Total capital cost ballpark | Reasonableness | $3B-$15B | Range | Engineering judgment | Pending |
| SV-002 | LCOE range | Reasonableness | 30-200 $/MWh | Range | Industry benchmarks | Pending |
| SV-003 | Increasing field → higher magnet cost | Relationship | Monotonic increasing | Direction | Physics | Pending |
| SV-004 | Energy balance | Physical consistency | Sum = total | +/-0.1% | Conservation of energy | Pending |
| SV-005 | CAS rollup consistency | Cross-system | Children = parent | +/-0.01% | Accounting rules | Pending |
| SV-006 | LCOE vs PyFECONS CATF | Baseline comparison | PyFECONS value | +/-5% | PyFECONS CATF config | Pending |

### Relationships

- **Informed by** Model Implementation — must know what's been built to verify it
- **Informed by** Domain Knowledge Base — expected values and relationships come from domain knowledge
- **Driven by** Project Intent — analysis questions determine what to verify
- **Feeds back to** Project Intent — failures may surface new questions or refine goals
- **Feeds back to** Model Implementation — specific failures drive new work items

### Current Support

- Validation pyramid (Levels 1-8) covers model quality but not system-level behavior
- Research docs identified 3-layer validation (structure, design-time, runtime) but this isn't implemented
- Some baseline comparison values in spec.md files
- Gaps:
  - No dedicated verification registry
  - No automated reasonableness checks
  - No relationship probing / sensitivity analysis framework
  - No integration with teax output for post-simulation verification

---

## Process Knowledge (Separate Concern)

**Purpose**: Knowledge about *how to model effectively* — tool usage patterns, SysML gotchas, workflow lessons. This is distinct from domain knowledge and modeling requirements.

**Current storage**: `modeling_pm/learnings/RAW_LEARNINGS.md`, `LOCAL_GUIDE.md`

Process Knowledge is captured via `/record-learning` and covers things like:
- "SysIDE doesn't support X syntax — use Y workaround"
- "Always run validation Level 1 before committing"
- "When modeling assemblies, add NumericalFunctions import first"

This is explicitly **not** domain knowledge. It does not feed into Modeling Requirements or Model Implementation content. It improves the *process* of modeling, not the *models themselves*. It follows the same promotion path as modeling decisions (feature discovery → project pattern → standard pattern) but on a different axis.

---

## Summary: Role Comparison

| Role | Primary Question | Independence | Key Output |
|------|-----------------|--------------|------------|
| **Project Intent** | "What do we want to achieve?" | Fully independent — exists first | Goals, scope, analysis questions |
| **Data Sources** | "What information is available?" | Independent — can grow anytime | Raw research, references, notes |
| **Domain Knowledge Base** | "What approved information should our models represent?" | Dependent on Data Sources + curation | Curated formulas, parameters, patterns |
| **Modeling Requirements** | "What rules must our models follow?" | Derived from Intent + Knowledge | Patterns, enforcement rules, validation criteria |
| **Model Implementation** | "How do we build the models?" | Constrained by Requirements, fed by Knowledge | Architecture, epics, artifacts |
| **System Verification** | "Does the implemented system behave correctly?" | Driven by Intent, informed by Knowledge + Implementation | Verification registry, test results |

---

## Traceability Links

| Link | From | To | Current support |
|------|------|----|----------------|
| Goal → Requirement | Project Intent | Modeling Requirements | **Not supported** |
| Goal → Analysis Question | Project Intent | Project Intent (internal) | **Not supported** |
| Source → Knowledge | Data Sources | Domain Knowledge Base | **Not supported** (no curation gate) |
| Knowledge → Requirement | Domain Knowledge Base | Modeling Requirements | Implicit (via research → spec) |
| Requirement → Implementation | Modeling Requirements | Model Implementation | Partially (patterns referenced in design.md) |
| Intent → Verification | Project Intent | System Verification | **Not supported** |
| Knowledge → Verification | Domain Knowledge Base | System Verification | Partially (baseline values in specs) |
| Implementation → Source | Model Implementation | Data Sources | Partially (doc comments cite sources) |
| Verification → Intent | System Verification | Project Intent | **Not supported** (feedback loop) |
| Verification → Implementation | System Verification | Model Implementation | **Not supported** (feedback loop) |

---

## Open Questions

1. **What should the Domain Knowledge Base look like as an artifact?** It needs a concrete home. Options:
   - An enhanced `LOCAL_GUIDE.md` with structured sections (formulas, parameters, insights)
   - A separate `KNOWLEDGE_BASE.md` or `DOMAIN_MODEL.md`
   - A directory (`modeling_pm/knowledge/`) with categorized files
   - Structured sections within `CLAUDE.md`

2. **What does the curation gate look like in practice?** It could be:
   - A status field on research documents (draft → reviewed → approved)
   - An explicit "incorporate" command that pulls findings into the Knowledge Base
   - A review step in the `/research` command where the user approves findings

3. **How granular should the System Verification registry be?** The examples above (SV-001 through SV-006) are relatively coarse. Should every baseline comparison value be a separate entry, or should they be grouped?

4. **Should Modeling Requirements have IDs?** Currently the enforcement rules (E1-E6) have ad-hoc IDs from a research document. If we formalize a project-level requirements registry, what's the ID scheme? (Distinct from per-feature MR-XXX which are work-item-scoped.)

5. **Where does the boundary between Modeling Requirements and Model Implementation sit?** The per-feature MR-XXX requirements in spec.md are part of the implementation workflow (they're created during the spec stage of a work item). But they're also "requirements." The taxonomy places them in Model Implementation because they're feature-scoped — Modeling Requirements are project-wide patterns and rules. Is this distinction clear enough?

---

## Sources Consulted

### agentic-mbse
- `docs/source-index.md` — SOURCE_INDEX concept and 4-type taxonomy
- `project_templates/MODELING_PROCESS.md.template` — Four Integrated Views, 4-phase workflow
- `project_templates/OVERVIEW.md.template` — Project goals/success criteria template
- `project_templates/LOCAL_GUIDE.md.template` — Project-specific patterns template
- `project_templates/MODELING_GUIDE.md.template` — SysML syntax and patterns
- `claude/commands/research.md` — Research command inputs/outputs
- `claude/commands/spec-model.md` — Spec command inputs/outputs
- `claude/commands/manage-sources.md` — Source management workflow
- `claude/commands/onboard.md` — Project setup workflow

### fusion-tea
- `modeling_pm/OVERVIEW.md` — Project goals and success criteria
- `SOURCE_INDEX.md` — PyFECONS as primary authority source
- `modeling_pm/research/20260126-lcoe-visibility-requirements-analysis.md` — LCOE gap analysis
- `modeling_pm/research/20260123-pyfecons-library-mapping-strategy.md` — CAS hierarchy, reactor types
- `modeling_pm/research/20260106-050051_cost-modeling-lcoe-strategy.md` — Multi-output calc patterns
- `modeling_pm/research/20260110-strategic-cost-patterns.md` — Enforcement rules E1-E6, AACE classes
- `modeling_pm/docs/COST_MODELING.md` — Costed Component interface, calc patterns
- `modeling_pm/LOCAL_GUIDE.md` — Currently minimal
- `modeling_pm/learnings/RAW_LEARNINGS.md` — Append-only process knowledge log
- `modeling_pm/active/*/spec.md` — 3 feature specs (foundation, power-balance, cost-patterns)
- `modeling_pm/active/*/design.md` — 3 feature designs

### Prior Research
- `.project/research/20260126-202931_requirements-goal-tracking-pipeline.md` — Analysis Angles concept, requirements dropping problem
- `.project/research/20260126-161628_python-vs-mbse-command-comparison.md` — Command structure comparison

---

**Last Updated**: 2026-01-31

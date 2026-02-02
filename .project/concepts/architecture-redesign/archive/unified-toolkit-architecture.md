# Unified Concept: MBSE Toolkit Architecture

**Date**: 2026-01-31
**Status**: Concept — synthesized from research, ready for design-phase detailing
**Synthesized from**: 5 research/concept documents (see [References](#references))

---

## 1. Problem Statement

Five structural problems, established through comparison with the Python agentic system, analysis of fusion-tea as a real-world case, and examination of Claude Code platform design intent:

| # | Problem | Evidence | Impact |
|---|---------|----------|--------|
| P1 | **Commands embed shared knowledge** | Avg 476 lines/command; design-model is 1,345 lines; SysML syntax repeated across 3+ commands | Inconsistency, bloat, unmaintainable |
| P2 | **Project definition doesn't scale** | OVERVIEW.md is a skeleton; no requirements registry; domain insights live in conversation | Requirements get "dropped"; no cross-feature traceability |
| P3 | **Rigid pipeline** | Same spec→design→plan→implement for a 1-line fix and a 6-month epic | Overhead kills small work; large work isn't decomposed |
| P4 | **Linear assumption** | No backward navigation, no concurrent item tracking, no refactoring workflow | Real development is non-linear; system can't keep up |
| P5 | **PM depends on agent memory** | Status tracking, archival, coverage reporting all rely on LLM execution | Hallucinated state, missed updates, no reliable dashboard |

These are not independent. P1 makes commands hard to evolve, blocking fixes for P3/P4. P2 prevents P5 (script-backed PM needs structured files to parse). The architecture below addresses them as an integrated system.

---

## 2. Architectural Principles

Six principles govern the design. Every decision below should trace to at least one.

| ID | Principle | Derived from |
|----|-----------|-------------|
| **AP-1** | **Design for 0, 1, N** — every structured artifact works when empty, works with one entry, scales to many | P2, SOURCE_INDEX.md as existence proof |
| **AP-2** | **One job per command** — commands focus on a user decision; shared knowledge lives in skills | P1, Claude Code platform design |
| **AP-3** | **Behavior-justified taxonomy** — every category (intent, scale, information role) must change downstream behavior; if it doesn't, delete it | P3, avoiding bureaucratic overhead |
| **AP-4** | **Deterministic state, intelligent interpretation** — state queries are scripts; state changes are agent-guided | P5, reliability requirement |
| **AP-5** | **Toolkit, not pipeline** — recommended paths exist, but the system supports skipping, going back, and working on multiple items | P3, P4, non-linear reality |
| **AP-6** | **Explicit curation** — information passes from raw sources to actionable knowledge through user-approved gates, not automatically | P2, trust model for AI-generated content |
| **AP-7** | **Script-mechanized transitions** — when a workflow step involves structured file mutations (moving files, updating registry rows, changing status), the mutation is executed by a deterministic script, not by instructing an agent to edit markdown. Agents decide *what* to change and generate *content*; scripts execute the change correctly. | P5, reliability requirement |

### AP-7 Implementation Tiers

AP-7 applies wherever the system mutates structured project state. Three implementation tiers exist, chosen based on whether content generation is needed:

| Tier | When to use | Mechanism | Example |
|------|-------------|-----------|---------|
| **T1: Fully deterministic** | No content generation needed; pure file ops + structured field updates | Python script only | Move file from `pending/` to `approved/`; update status column in registry |
| **T2: Script + headless LLM** | File ops are deterministic but new content must be generated (summaries, structured entries) | Script handles file ops, calls `claude -p` with structured output for content | Approve research: move file, generate DI-XXX summary entry, append to KNOWLEDGE.md |
| **T3: Command invokes script** | Agent is already in conversation and needs to trigger a state transition mid-workflow | Slash command instructs agent to invoke a CLI subcommand | `/research` at completion calls `agentic-mbse pm approve-research` after user approves insights |

**The key constraint**: The script is the source of truth for *where* files go, *what format* registry entries use, and *which files* get updated. The agent never directly edits registry files for state transitions — it calls the script, which does the edit. This eliminates the class of bugs where an agent forgets a field, uses the wrong format, or updates one file but not another.

**Operations that require AP-7 treatment** (identified so far):

| Operation | Tier | What the script does |
|-----------|------|---------------------|
| Approve research | T2 | Move `pending/` → `approved/`, generate DI-XXX entries, append to KNOWLEDGE.md |
| Register project requirement | T1 | Append PR-XXX row to REQUIREMENTS.md with correct columns (rare — project-level rules only) |
| Archive work item | T1 | Move `active/{item}/` → `completed/YYYYMMDD_{item}/`, update BACKLOG.md status |
| Update validation status | T1 | Update Status column in VALIDATION_MATRIX.md for specified SV-XXX |
| Project status query | T1 | Parse all structured files, produce dashboard markdown |

---

## 3. Foundation: Information Architecture

### 3.1 The Information Flow Model

Six information roles flow through the system. Each role has a **producer**, a **consumer**, and a **structured home**. The model is a directed graph with explicit feedback loops.

```
                         ┌──────────────────────┐
                         │   PROJECT INTENT      │
                         │  Goals (G-XXX)        │
                         │  Analysis Questions   │
                         │  Scope, Priorities    │
                         └─────────┬─────────────┘
                                   │ drives
                    ┌──────────────┼──────────────────┐
                    │              │                   │
                    v              v                   v
          ┌─────────────┐  ┌──────────────┐  ┌────────────────┐
          │ DATA SOURCES │  │ DOMAIN       │  │ MODELING       │
          │ (raw,        │  │ KNOWLEDGE    │  │ REQUIREMENTS   │
          │  external)   │──│ (curated,    │──│ (verifiable    │
          │              │  │  approved)   │  │  statements)   │
          └──────────────┘  └──────┬───────┘  └───────┬────────┘
                 ▲ curation gate   │                  │ constrains
                 │                 │ feeds             │
                 │                 v                   v
                 │         ┌──────────────────────────────┐
                 │◄────────│    MODEL IMPLEMENTATION       │
                 │ feedback│  Architecture → Epics →       │
                 │         │  spec → design → plan →       │
                 │         │  implement cycle               │
                 │         └──────────────┬────────────────┘
                 │                        │ produces
                 │                        v
                 │         ┌──────────────────────────────┐
                 └─────────│    SYSTEM VERIFICATION        │
                  failures │  Reasonableness, balances,    │
                  refine   │  baseline comparison,         │
                  intent   │  regression                   │
                           └──────────────────────────────┘
```

### 3.2 Project File Structure

A target project after `agentic-mbse init` and as it grows:

```
project-root/
├── .claude/
│   ├── settings.json
│   ├── commands/              # MBSE workflow commands (tool-owned)
│   │   ├── spec-model.md
│   │   ├── design-model.md
│   │   ├── plan-model.md
│   │   ├── implement-model.md
│   │   ├── audit-models.md
│   │   ├── research.md
│   │   ├── quick-model.md
│   │   ├── review-model.md
│   │   ├── analyze-models.md
│   │   ├── status.md
│   │   ├── backlog.md
│   │   ├── onboard.md
│   │   └── manage-sources.md
│   ├── skills/                # Shared knowledge (tool-owned)
│   │   ├── sysml-conventions/
│   │   ├── model-validation/
│   │   ├── project-structure/
│   │   ├── source-traceability/
│   │   ├── epic-decomposition/
│   │   ├── requirements-tracking/
│   │   └── toolkit-awareness/
│   └── agents/                # Specialist agents (tool-owned)
│       ├── sysmlv2-doc-analyzer.md
│       ├── kerml-expert.md
│       ├── sysml-expert.md
│       ├── syside-expert.md
│       ├── sysmlv2-validator.md
│       └── python-debugger.md
│
├── models/                    # Role 6: Model Artifacts
│   ├── library/               #   Reusable definitions (part defs, calc defs)
│   │   ├── foundation/
│   │   └── calculations/
│   └── designs/               #   Specific configurations (usages)
│       └── {config-name}/
│
├── tests/
│   └── models/                #   Model validation tests (pytest)
│
├── modeling_pm/               # Project management home
│   ├── OVERVIEW.md            # Role 3: Formalized goals & questions (user-owned)
│   ├── ARCHITECTURE.md        # Role 5: Project-level structural decisions (user-owned)
│   ├── KNOWLEDGE.md           # Role 2: Curated domain knowledge (user-owned)
│   ├── REQUIREMENTS.md        # Role 4: Project-specific modeling rules (user-owned)
│   ├── VALIDATION_MATRIX.md   # Role 6: System verification criteria (user-owned)
│   ├── MODELING_GUIDE.md      # Role 4: Baseline modeling rules (tool-owned)
│   ├── MODELING_PROCESS.md    # Workflow reference (tool-owned)
│   ├── EPIC_GUIDE.md          # Work decomposition guide (tool-owned)
│   │
│   ├── intent/                # Role 3: Raw user documents (user-owned)
│   │   ├── project-charter.md #   User-written/uploaded, any length
│   │   └── *.md               #   Stakeholder notes, mission docs, etc.
│   │
│   ├── research/              # Role 2: Research outputs (data management below)
│   │   ├── pending/           #   Raw research, not yet curated
│   │   │   └── YYYYMMDD-HHMMSS_topic.md
│   │   └── approved/          #   User-approved research
│   │       └── YYYYMMDD-HHMMSS_topic.md
│   │
│   ├── active/                # In-progress work items (ephemeral, not a Role)
│   │   └── {work-item-name}/
│   │       ├── spec.md
│   │       ├── design.md
│   │       └── plan.md
│   │
│   ├── backlog/
│   │   └── BACKLOG.md         # Prioritized work items with intent/scale
│   │
│   ├── completed/             # Archived work
│   │   └── YYYYMMDD_{item}/
│   │
│   └── learnings/
│       └── RAW_LEARNINGS.md   # Process knowledge (append-only)
│
├── SOURCE_INDEX.md            # Role 1: Authority sources (user-owned)
├── CLAUDE.md                  # Project-specific essentials
└── README.md
```

**Key structural decisions**:

- **`research/pending/` and `research/approved/`**: Research reports start in `pending/`. The approval script (AP-7, T2) moves them to `approved/` and extracts insights into `KNOWLEDGE.md`. This makes the curation gate a visible file system operation, not an invisible metadata change.
- **`modeling_pm/` as the PM home**: All project management artifacts live here. The PM script engine (`agentic-mbse status`) knows to look here.
- **`.claude/` as the tooling home**: Commands, skills, agents are all tool-owned and updated on `agentic-mbse init --update`.
- **`models/` and `tests/` at project root**: Model artifacts are the primary output; they belong at the top level alongside source code conventions.

### 3.3 Role Definitions and Data Models

Each role has a concrete entity format. These are the **data models** — the structured records that commands produce, consume, and maintain.

#### Role 1: Authority Sources — `SOURCE_INDEX.md`

**Status**: Already designed for N. No changes needed.

**Entity format** (existing):
```markdown
### [Source Name]
- **Type**: reference-implementation | documentation | data | research
- **Location**: path or URL
- **Use For**: what this source informs
- **Validation**: how to verify against this source
```

**Producer**: `/manage-sources`, `/onboard`
**Consumer**: `/research`, `/spec-model`, `/audit-models`, `/implement-model`

---

#### Role 2: Domain Knowledge — `KNOWLEDGE.md` (new) + `research/` directory

**Purpose**: Curated, approved knowledge that has passed through the curation gate. Captures domain insights — interpretive perspectives that bridge raw data and model requirements.

**Two artifacts**:

| Artifact | Purpose | Trust level |
|----------|---------|-------------|
| `research/pending/*.md` | Raw research output. May contain errors, hallucinations, or irrelevant findings. Explicitly **not trusted** until approved. | Untrusted |
| `research/approved/*.md` | User-reviewed research. The user has confirmed the findings are accurate and relevant. | Trusted |
| `KNOWLEDGE.md` | Structured domain insights extracted from approved research. The actionable feed for modeling work. | Trusted, structured |

**Entity format** (`KNOWLEDGE.md`):
```markdown
### DI-XXX: [Title]
- **Source**: [approved research doc, user note, or authority source]
- **Context**: [1-3 sentences: the domain fact and why it matters]
- **Model implications**: [what the models must capture because of this insight]
- **Analysis implications**: [what analyses this enables or requires]
- **Derived requirements**: [MR-XXX IDs, if specs have been written; "pending" otherwise]
- **Status**: captured | requirements-derived | addressed
```

**Scaling**: Single markdown file. Each entry is ~8 lines. At 50 entries = ~400 lines, still scannable. Split threshold: ~100 entries (unlikely for most projects).

#### Data Management: The Research-to-Knowledge Flow

This is the primary curation gate (AP-6), mechanized via scripts (AP-7).

```
User runs /research
        │
        v
Agent explores authority sources,
produces research document
        │
        v
Script writes to: research/pending/YYYYMMDD-HHMMSS_topic.md
(deterministic path — agent does not choose where to save)
        │
        v
Agent presents findings to user,
suggests domain insights (DI-XXX candidates)
        │
        v
┌─────────────────────────────────────────────────┐
│ USER DECISION POINT                             │
│                                                 │
│ For the research report:                        │
│   "Approve" → proceed to approval flow          │
│   "Revise"  → agent edits, re-presents          │
│   "Reject"  → file stays in pending/ (or delete)│
│                                                 │
│ For each suggested insight:                     │
│   "Accept"  → included in approval              │
│   "Modify"  → user edits, then accept           │
│   "Skip"    → not added to KNOWLEDGE.md         │
└──────────────────────┬──────────────────────────┘
                       │
                       v
Agent calls: agentic-mbse pm approve-research <file>
  --insights '<structured JSON of approved DI-XXX entries>'
        │
        v
┌─────────────────────────────────────────────────┐
│ SCRIPT EXECUTION (AP-7, Tier 2)                 │
│                                                 │
│ 1. Move file: pending/ → approved/              │
│ 2. For each insight in --insights:              │
│    a. Assign next DI-XXX ID                     │
│    b. Format as structured entry                │
│    c. Append to KNOWLEDGE.md                    │
│ 3. Print confirmation with file paths + IDs     │
│                                                 │
│ Script guarantees:                              │
│ - Correct ID sequencing (no duplicates)         │
│ - Correct entry format (no missing fields)      │
│ - Atomic: all-or-nothing (no partial updates)   │
│ - File paths follow convention                  │
└─────────────────────────────────────────────────┘
```

**Why this design**:
- The agent generates the *content* (research findings, insight summaries) — this is what LLMs are good at
- The script handles the *state transition* (file moves, registry appends, ID assignment) — this must be deterministic
- The user makes the *approval decision* — no information enters the knowledge base without explicit consent
- Research in `pending/` is visible in the file system — the user can review it in their IDE, share it, or come back to it later

**Alternative entry points for KNOWLEDGE.md**:
- User can add entries directly (manual edit)
- `/spec-model` can suggest adding insights discovered during scoping (same script invocation, different trigger)

**Producer**: `/research` → approval script → `KNOWLEDGE.md`; user direct entry
**Consumer**: `/spec-model` (surfaces relevant insights), `/status` (coverage reporting)

---

#### Role 3: Project Intent — `intent/` directory + `OVERVIEW.md` (revised)

**Purpose**: Why this project exists. What questions the models must answer. This is the demand signal.

**Two concerns, separated**:

| Concern | What it is | Where it lives |
|---------|-----------|----------------|
| **Raw intent documents** | User-authored or uploaded prose: project charters, mission statements, stakeholder notes, meeting summaries. These can be lengthy (400+ lines) and are the user's own words. | `modeling_pm/intent/` directory |
| **Formalized goals and questions** | Structured, ID'd entries extracted from the raw documents. These are what the rest of the system references. | `OVERVIEW.md` (Goals Registry, Analysis Questions tables) |

**Raw intent documents** (`modeling_pm/intent/`):
```
modeling_pm/intent/
├── project-charter.md          # User-written or uploaded, any length
├── stakeholder-notes.md        # Meeting notes, requirements discussions
├── mission-statement.md        # High-level framing
└── ...                         # Any user documents that express project intent
```

These are **user-owned, unstructured** files. The system does not parse them directly. They are the raw input from which goals and questions are formalized.

**Formalized output** (`OVERVIEW.md`):
```markdown
# [Project Name]

## Project Summary
[Brief prose context — 2-3 paragraphs, not the full charter]

## Goals Registry

| ID | Goal | Priority | Status | Source | Traced Requirements |
|----|------|----------|--------|--------|---------------------|
| G-001 | [goal statement] | P0 | active | project-charter.md | MR-001, MR-005, MR-012 |
| G-002 | ... | P1 | active | stakeholder-notes.md | MR-003 |

## Analysis Questions

Questions the models must be able to answer. Each implies structural requirements on the models.

| ID | Question | Implies | Source | Status |
|----|----------|---------|--------|--------|
| AQ-001 | "What's the capital vs O&M breakdown in LCOE?" | LCOE calc must expose intermediate values | project-charter.md | open |
| AQ-002 | "How does energy capture method affect cost?" | Turbine and DEC must be separate costed components | stakeholder-notes.md | open |

## Scope
### In Scope
### Out of Scope
### Future Phases

## Success Criteria
[Project-level acceptance criteria — when is the project "done enough"?]
```

#### Data Management: Intent Formalization

The flow from raw documents to structured goals/questions follows the same pattern as Role 2 (raw → curation gate → structured output). This requires its own control flow combining agent intelligence (reading prose, proposing goals) with script-backed state transitions (AP-7, assigning G-XXX / AQ-XXX IDs, appending to OVERVIEW.md).

**Control flow needed** (to be detailed during design):
- User uploads/writes documents in `intent/`
- An agent-driven process reads the documents, proposes structured G-XXX goals and AQ-XXX analysis questions
- User reviews, approves, modifies, or rejects each
- A script registers approved entries in OVERVIEW.md (correct IDs, format, source traceability)
- This process can be triggered during `/onboard` (initial project setup) or run standalone when new intent documents are added

**Not yet designed**: The specific command/script interface, whether this is part of `/onboard` or a separate command, and how incremental updates work (user adds a new document to `intent/` after initial setup — how do new goals get extracted without re-processing everything). These are Phase 1A design questions.

**Producer**: `/onboard` (initial formalization), intent formalization flow (TBD), user direct editing
**Consumer**: `/spec-model` (reads goals/questions to inform scoping), `/status` (reports goal coverage), `/audit-models` (checks that goals are addressed)

---

#### Role 4: Modeling Requirements — `MODELING_GUIDE.md` (tool-owned baseline) + `REQUIREMENTS.md` (user-owned extensions)

**Purpose**: Project-wide rules, patterns, and constraints that govern how *all* modeling work is done. These are durable standards that derive from Project Intent and Domain Knowledge — not per-feature specs (those are ephemeral artifacts of individual work items, living within Model Implementation).

**This is NOT a registry of every MR-XXX from every work item.** Per-feature requirements (MR-XXX in spec.md) are part of Model Implementation (the work item cycle defined in Sections 5-7). They are ephemeral — a work item may be tried, completed, later revised, or abandoned. Tracking every one at the project level would be untenable.

**Two-tier structure**:

```
Role 4: Modeling Requirements
│
├── MODELING_GUIDE.md  (tool-owned baseline)
│   │
│   │  Rules that ALL agentic-mbse projects follow.
│   │  Updated by `agentic-mbse init`. Not user-edited.
│   │
│   │  Contains:
│   │  - Definitions vs Usages separation rule
│   │  - ADR-002 calculation placement
│   │  - Package structure requirements
│   │  - Naming conventions
│   │  - Documentation standards (doc comment format)
│   │  - Validation checklist
│   │
│   │  NOTE: MODELING_GUIDE.md currently also contains reference/how-to
│   │  material (syntax patterns, imports, testing patterns). That content
│   │  moves to skills (sysml-conventions, model-validation, etc.) during
│   │  the redesign. What remains is pure rules.
│   │
└── REQUIREMENTS.md  (user-owned extensions)
    │
    │  Project-specific rules added on top of the baseline.
    │  These derive from the project's goals and domain knowledge.
    │
    │  Contains: PR-XXX entries (few in number, durable, enforceable)
```

**What belongs in MODELING_GUIDE.md (baseline)**: Rules that are universally correct for SysML v2 modeling with agentic-mbse. These don't depend on the project's domain. Example: "calc defs go in library/, not in designs/."

**What belongs in REQUIREMENTS.md (extensions)**: Rules that are specific to this project's goals and domain. Example: "all costed components must expose capital_cost" — this only applies to projects doing cost modeling.

**Entity format** (`REQUIREMENTS.md`):
```markdown
# Modeling Requirements

Project-specific rules that all modeling work must follow.
These extend the standard rules in MODELING_GUIDE.md.

## Requirements

| ID | Requirement | Source | Enforcement | Validation Method |
|----|-------------|--------|-------------|-------------------|
| PR-001 | All costed components SHALL expose capital_cost, raw_material_cost | G-001 (LCOE traceability) | Design review + validation rule | AST check: :> 'Costed Component' has cost attributes |
| PR-002 | All calc defs SHALL cite source file:line in doc comment | G-003 (PyFECONS validation) | Validation Level 6 | Doc comment parser |
| PR-003 | Intermediate cost values SHALL use EXPOSE pattern | AQ-001 (cost breakdown visibility) | Design review | Pattern check in audit |
```

**Sub-types** (from the taxonomy research):

| Sub-type | Description | Example |
|----------|-------------|---------|
| **Modeling patterns** | Required SysML idioms for this project | Costed Component interface, EXPOSE pattern |
| **Structural rules** | Package organization, file naming, imports | Unidirectional imports; calc defs in library/ |
| **Documentation rules** | What model elements must document | Doc comments with Source, Reference, Last Updated |
| **Enforcement rules** | Machine-checkable constraints | E1-E6 from cost patterns research |
| **Naming conventions** | Standardized element names | 'cost_model' as standard calc usage name |

**Each requirement specifies both criteria and method**: What constitutes compliance, and how to check it (validation rule, design review checklist, regression test). This is what makes them enforceable rather than aspirational.

**Lifecycle**:
- **Baseline (MODELING_GUIDE.md)**: Ships with agentic-mbse. Updated across versions. Users don't edit.
- **Extensions (REQUIREMENTS.md)**: Discovered through implementation experience → proposed (often promoted from a per-feature pattern) → reviewed → added. These grow slowly and deliberately — a new entry means a new project-wide standard.

**Producer**: `agentic-mbse init` (MODELING_GUIDE.md), `/onboard` (initial REQUIREMENTS.md from intent), user direct editing, promoted from per-feature experience
**Consumer**: `/design-model` (checks compliance), `/implement-model` (enforces during work), `/audit-models` (verifies across features), `/review-model` (checks design against rules)

---

#### Role 5: Modeling Decisions — `ARCHITECTURE.md` (new)

**Purpose**: Domain-level architectural decisions about the models themselves — the structural choices that shape how the system is decomposed and organized. Think of these as **ADRs (Architecture Decision Records) for the model ecosystem**.

These are distinct from Role 4 in kind, not just scope:
- **Role 4** answers: "What modeling rules do we follow?" (methodology — derived from goals)
- **Role 5** answers: "What structural choices have we made about the domain?" (architecture — derived from domain understanding)

**Example (fusion-tea)**:

| Role 4 (Modeling Requirements) | Role 5 (Modeling Decisions) |
|-------------------------------|---------------------------|
| "All costed components must expose capital_cost" (because we want LCOE traceability) | "Turbine plant is BOP, not power core" (domain taxonomy decision) |
| "EXPOSE pattern required for intermediate cost values" (because we want side-by-side comparison) | "Reactor types are MFE, IFE, MIF — each gets its own designs/ directory" (domain decomposition) |
| "Calc defs must cite source file:line" (traceability rule) | "Plant-level vs component-level costs follow the CAS hierarchy" (domain structure) |

Role 4 rules tend to be stable once established. Role 5 decisions **evolve** — as the project learns more about the domain, architectural decisions get refined, split, or revised. Early decisions may be rough ("magnets are in power core") and later get more nuanced ("HTS vs LTS magnets have different cost structures, requiring separate library packages").

Per-feature design.md files are **not** part of this role. They are ephemeral artifacts of individual work items. ARCHITECTURE.md captures the decisions that outlive any single work item — the ones that would be expensive to reverse and that new work items need to know about.

**`ARCHITECTURE.md` structure**:
```markdown
# Model Architecture

## Domain Decomposition
[How the physical system is decomposed into model packages.
 What's "plant-level" vs "component-level." What the subsystem boundaries are.]

## Package Organization
| Package | Purpose | Domain Scope | Dependencies |
|---------|---------|-------------|-------------|
| library/foundation/ | Base types, units, materials | Cross-cutting | None |
| library/power_balance/ | Power flow calculations | Plasma → grid | foundation/ |
| library/magnets/ | Magnet costing & sizing | TF + PF coils | foundation/ |
| designs/catf_mfe/ | CATF compact tokamak | Full plant | All library packages |

## Key Decisions

### AD-001: Reactor type taxonomy
**Decision**: MFE, IFE, MIF as top-level reactor categories. Each gets a separate designs/ subdirectory.
**Rationale**: Different reactor types share ~60% of components (buildings, turbine, BOP) but diverge on power core. Shared components live in library/; type-specific assemblies in designs/.
**Date**: 2026-01-15
**Status**: Active

### AD-002: Plant vs BOP boundary
**Decision**: "Plant" includes everything inside the reactor building. BOP (Balance of Plant) is everything outside — turbine, cooling, electrical.
**Rationale**: Aligns with CAS hierarchy (CAS20 = direct plant, CAS23 = turbine plant equipment).
**Date**: 2026-01-20
**Status**: Active

### AD-003: Cost aggregation follows CAS hierarchy
**Decision**: Cost rollup mirrors the ARPA-E CAS standard. Each cost account maps to a model package or component.
**Rationale**: Enables direct validation against PyFECONS which uses the same hierarchy.
**Date**: 2026-01-22
**Status**: Active — may need revision when CAS70-90 (indirect costs) are added
```

**Lifecycle**: Initial decisions established during `/onboard`. Refined as the project matures — new decisions added when complexity demands codification, existing decisions updated when understanding evolves. Unlike Role 4 rules (which are added and rarely changed), Role 5 decisions are living documents.

**Producer**: `/onboard` (initial), user direct editing, codified when complexity demands it
**Consumer**: `/design-model` (reads before designing), `/implement-model` (respects structure), `/analyze-models` (checks adherence), `/spec-model` (understands existing architecture when scoping new work)

---

#### Role 6: System Verification — `VALIDATION_MATRIX.md` (new)

**Purpose**: Verification criteria for the integrated system — beyond per-work-item checks.

**Entity format**:
```markdown
## Verification Registry

| ID | Description | Type | Expected | Tolerance | Source | Test | Status |
|----|-------------|------|----------|-----------|--------|------|--------|
| SV-001 | Total capital cost ballpark | reasonableness | $3B-$15B | range | engineering judgment | - | pending |
| SV-002 | p_net output accuracy | baseline | PyFECONS value | ±1% | PowerBalance.py:94 | test_pnet | passing |
| SV-003 | Energy balance conservation | physical | sum = total | ±0.1% | physics | test_energy_balance | pending |
```

**Verification types** (each changes what the check does):

| Type | What it checks | When it runs |
|------|---------------|-------------|
| reasonableness | Output is in expected ballpark | After any simulation |
| baseline | Output matches reference implementation | After feature implementation |
| physical | Conservation laws hold | After model integration |
| relationship | Input/output vary in expected direction | Sensitivity analysis |
| rollup | Aggregations are consistent | After cost rollup features |

**Producer**: `/spec-model` (creates entries from requirements), `/audit-models` (updates status)
**Consumer**: `/audit-models`, `/status`, PM script engine

---

### 3.3 Document Relationship Map

```
intent/                        SOURCE_INDEX.md
  raw user documents               Authority sources
       │                               │
       │ formalization flow             │ explored by /research
       │ (agent + AP-7 script)          v
       v                          research/pending/
OVERVIEW.md                           │
  G-XXX goals ──────────────►         │ user approves (AP-7 script)
  AQ-XXX questions                    v
       │                         research/approved/  ──►  KNOWLEDGE.md
       │◄── refines ──────────────────────────────────  DI-XXX domain insights
       │                                                 │
       │                                                 │ "this insight implies..."
       v                                                 v
Role 4: Modeling Requirements       Role 5: Modeling Decisions
  (methodology — HOW to model)        (architecture — WHAT structure)
  MODELING_GUIDE.md (baseline)         ARCHITECTURE.md
  REQUIREMENTS.md (extensions)           AD-XXX decisions
       │                                     │
       │  constrains methodology             │ constrains structure
       │                                     │
       v                                     v
                   Model Implementation
                    (per-feature spec/design/plan —
                     ephemeral, work-item-scoped)
                              │
                              │ produces
                              v
                         Model Artifacts
                          (models/, tests/)
                              │
                                      │ verified against
                                      v
                              VALIDATION_MATRIX.md
                                SV-XXX criteria
```

---

## 4. Foundation: Knowledge Layer (Skills)

### 4.1 Design Pattern: Skill Extraction

**Pattern**: Extract knowledge that is (a) referenced by 2+ commands and (b) would otherwise be duplicated or inconsistent into a named skill with a `SKILL.md` entry point.

**What a skill contains**:
- `SKILL.md`: Overview, when to reference, key principles (loaded into context)
- Optional `references/*.md`: Detailed reference material (loaded on demand)

**What a skill does NOT contain**:
- Workflow logic (that's in commands)
- Project-specific data (that's in the information architecture)
- Agent prompts (that's in agent definitions)

### 4.2 Skill Catalog

| Skill | What it contains | Referenced by | Justification |
|-------|-----------------|---------------|---------------|
| **sysml-conventions** | Syntax rules, naming, patterns, pitfalls, code stencils | design-model, implement-model, audit-models, quick-model | Currently duplicated across design-model (600+ lines) and partially in others |
| **model-validation** | Quality pyramid (8 levels), CLI commands, pass/fail criteria, regression patterns | design-model, implement-model, audit-models, plan-model | Currently embedded in design-model and implement-model separately |
| **project-structure** | Library vs designs, file organization, cross-file patterns, EXPOSE pattern | design-model, implement-model, spec-model, onboard | Currently scattered; inconsistent between commands |
| **source-traceability** | SOURCE_INDEX format, citation patterns, doc comment requirements | design-model, spec-model, audit-models, research | Currently partially in design-model, partially in manage-sources |
| **epic-decomposition** | Goldilocks principle (adapted for modeling), work item taxonomy, decomposition process, anti-patterns | backlog, status, onboard | Currently missing entirely (identified as CRITICAL gap) |
| **requirements-tracking** | REQUIREMENTS.md format (project-wide PR-XXX rules), promotion path from per-feature patterns, enforcement methods, compliance checking | design-model, audit-models, review-model, status | Currently missing; project-level rules scattered in research docs |
| **toolkit-awareness** | CLI commands, validation tools, environment | all commands | Already exists; needs updates for new PM commands |

### 4.3 Skill Loading Strategy

**Decision needed**: How many skills can be loaded concurrently without context window pressure?

**Proposed approach** (needs measurement):
- Commands declare their skill dependencies in a header comment
- At command start, load the skills needed for the current stage only
- Skills are designed to be concise (<200 lines for SKILL.md) with optional deep references

**Constraint**: If measurement shows context pressure, skills may need to be more granular (principles only in SKILL.md, examples only on demand). This is an iteration target — the skill boundaries can shift without changing the architecture.

---

## 5. Foundation: Work Item Model

### 5.1 The Two Dimensions

Every work item has an **intent** (what kind of work) and a **scale** (how much process). These are not metadata — they change downstream behavior (AP-3).

### 5.2 Intent Dimension

Each intent changes: (a) which pipeline stages run, (b) what the spec asks for, and (c) what validation emphasizes.

| Intent | Pipeline path | Spec behavior | Validation emphasis |
|--------|--------------|---------------|---------------------|
| **Model** | spec → design → plan → implement → audit | Full: scope, requirements, success criteria | Correctness against sources |
| **Fix** | spec → implement | Lightweight: what's wrong, what "fixed" looks like | Regression (don't break other things) |
| **Investigate** | research → (optional: spec) | Deferred: research must complete before requirements can be written | N/A (may not produce implementation) |
| **Refactor** | spec → plan → implement | Structural: what changes, what must be preserved | Regression (behavior unchanged) |
| **Integrate** | spec → design → implement | Interface-focused: what connects, what contracts must hold | Cross-file consistency |

**Behavioral differences that justify each intent**:

- **Model vs Fix**: Fix skips design (user knows the structure) and has a lightweight spec (no requirements registry — just "before/after"). Model needs full design because structural decisions haven't been made.
- **Investigate vs Model**: Investigate may terminate after research without producing implementation. The system shouldn't pressure the user into spec→design→plan when they're still learning.
- **Refactor vs Model**: Refactor skips design (no new structure is being invented) but needs a plan (regression safety requires careful ordering). The spec focuses on preservation criteria, not business requirements.
- **Integrate vs Model**: Integrate focuses on interfaces between existing components. Design is about contracts, not component internals.

### 5.3 Scale Dimension

Each scale changes: how much artifact overhead is appropriate.

| Scale | Artifact behavior | Entry point |
|-------|------------------|-------------|
| **Trivial** | No spec/design/plan. Direct: understand → execute → validate | `/quick-model` |
| **Small** | Abbreviated spec (inline in backlog or 1-page). No separate design doc for Fix/Refactor | `/spec-model` (abbreviated mode) |
| **Standard** | Full artifacts per intent's pipeline path | `/spec-model` (full mode) |
| **Epic** | Must decompose into sub-items first, then each sub-item enters pipeline | `/backlog decompose` → sub-items |

### 5.4 Control Flow: Work Item Routing

When work begins, the system determines intent and scale. This is the **routing decision tree**:

```
User describes what they want to do
        │
        v
┌─────────────────────────────────┐
│ DETERMINE INTENT                │
│                                 │
│ System infers from description, │
│ presents to user for            │
│ confirmation:                   │
│                                 │
│ "It sounds like you want to     │
│  [fix/build/investigate/        │
│   refactor/integrate].          │
│  Is that right?"                │
└───────────────┬─────────────────┘
                │
                v
┌─────────────────────────────────┐
│ DETERMINE SCALE                 │
│                                 │
│ System assesses from scope:     │
│                                 │
│ Trivial: single attribute,      │
│   doc comment, value change     │
│ Small: single file, clear scope │
│ Standard: multi-file feature    │
│ Epic: > 3 days, multiple        │
│   concerns, needs decomposition │
│                                 │
│ "This looks like a [scale]      │
│  change. Agree?"                │
└───────────────┬─────────────────┘
                │
                v
┌─────────────────────────────────┐
│ ROUTE TO PIPELINE PATH          │
│                                 │
│ Intent × Scale → entry point    │
│ (see matrix in 5.2/5.3)        │
└─────────────────────────────────┘
```

**UX principle**: The system infers and confirms. The user never fills out a form. For power users, tags can shortcut: `/spec-model --intent=fix "missing redefines in cost_model"`.

### 5.5 Backward Navigation

When implementation reveals a design flaw, the system supports going back:

```
Implementing phase 2 of 3
        │
        │ "The approach from the design doesn't work because..."
        v
┌─────────────────────────────────┐
│ BACKWARD NAVIGATION TRIGGER     │
│                                 │
│ Agent detects or user declares  │
│ that current design is flawed   │
│                                 │
│ Options presented:              │
│ 1. Update design.md, re-validate│
│    prototype, adjust plan,      │
│    resume implementation        │
│ 2. Continue with workaround     │
│    (document deviation)         │
│ 3. Pause this item, work on     │
│    something else               │
└─────────────────────────────────┘
```

**Concrete process for option 1**:
1. Open design.md, identify the flawed section
2. Revise the design with the new understanding
3. Re-run validation on the prototype (Levels 1-3)
4. Update plan.md (adjust remaining phases)
5. Resume implementation from the current phase

**Further design needed**: Exact mechanism for tracking "went back" state. Options include git-based checkpointing (deferred) or explicit state markers in plan.md.

---

## 6. Control Flow: Project Management

### 6.1 The Split: Scripts vs. Agent

**Design pattern**: State queries are deterministic (Python scripts). State changes are agent-guided (commands). Intelligence layers on top.

```
┌──────────────────────────────────────────────────┐
│  CLI Layer: `agentic-mbse status`                │
│  (Python script — deterministic, testable)       │
│                                                  │
│  Reads: BACKLOG.md, REQUIREMENTS.md, active/,    │
│         completed/, VALIDATION_MATRIX.md,        │
│         models/, tests/                          │
│                                                  │
│  Produces: Markdown dashboard with:              │
│  - Epic progress (items done/total)              │
│  - Work item states (pending/active/paused/done) │
│  - Requirements coverage (tested/untested)       │
│  - Validation status (passing/failing/pending)   │
│                                                  │
│  Guarantees: Deterministic, no hallucination,    │
│              same input → same output            │
└──────────────────────┬───────────────────────────┘
                       │
                       │ script output fed to
                       v
┌──────────────────────────────────────────────────┐
│  Command Layer: `/status`                        │
│  (Agent command — intelligent, interactive)      │
│                                                  │
│  Reads: Script output + project context          │
│                                                  │
│  Adds:                                           │
│  - Interpretation ("magnet modeling is blocked    │
│    on a design question")                        │
│  - Recommendations ("complete phase 3, then      │
│    start blanket & shield")                      │
│  - Gap analysis ("4 requirements untraced to     │
│    goals — may be orphaned")                     │
│                                                  │
│  Modes:                                          │
│  - default: dashboard + interpretation           │
│  - decompose <epic>: break into work items       │
│  - close [item]: verify + archive                │
└──────────────────────────────────────────────────┘
```

### 6.2 PM Script Engine: Data Model

The script engine needs to parse structured files. This defines **what it expects**:

**Work item state** (derived from file system):

| State | Determined by |
|-------|-------------- |
| **backlog** | Entry in BACKLOG.md, no directory in `active/` |
| **active** | Directory exists in `active/{item}/` |
| **active:stage** | Which artifact files exist: spec.md only = speccing; design.md = designing; plan.md = planning; implementation started = implementing |
| **paused** | Explicit marker in BACKLOG.md or `active/{item}/STATUS` |
| **completed** | Directory in `completed/` |

**Project requirements compliance** (derived from REQUIREMENTS.md):

| Metric | Computed by |
|--------|-------------|
| Total project rules | Count rows in REQUIREMENTS.md |
| With validation method | Count rows where Validation Method column is non-empty |
| Enforceable (machine-checkable) | Count rows where Enforcement = validation rule (vs. design review) |

Note: Per-feature MR-XXX requirements are NOT tracked at the project level. They are ephemeral artifacts of individual work items in `active/{item}/spec.md` and are archived with the work item when complete.

**Validation status** (derived from VALIDATION_MATRIX.md):

| Metric | Computed by |
|--------|-------------|
| Total criteria | Count rows |
| Passing | Count rows where Status = "passing" |
| Failing | Count rows where Status = "failing" |
| Pending | Count rows where Status = "pending" |

### 6.3 PM Script Engine: Output Format

```
## Project: [name]

### Work Items
Epic: Power Core Components                    [3/8 done]
  [x] Foundation types .................. completed 2026-01-15
  [x] Power balance calcs .............. completed 2026-01-22
  [x] Cost pattern fix (fix) ........... completed 2026-01-28
  [ ] Magnet modeling (model) .......... active:implementing (phase 2/3)
  [ ] Blanket & shield (model) ........ backlog
  [ ] Divertor (model) ................ backlog (blocked by: blanket)
  [ ] Turbine plant (model) ........... backlog
  [ ] System integration (integrate) .. backlog (blocked by: all above)

### Project Rules (REQUIREMENTS.md)
Total: 8 | With validation method: 7 | Machine-enforceable: 4

### Validation Status
Total: 12 | Passing: 7 | Failing: 1 | Pending: 4
Failing: SV-006 (LCOE vs PyFECONS: got 48.2, expected 45.1, tolerance ±5%)
```

### 6.4 Visual Representation

The dashboard uses plain markdown that renders in both terminal and IDE preview. No dependencies on external tools. ASCII trees, markdown tables, and inline metrics.

**Further design needed**: Exact CLI flags, output format options (--json for programmatic use?), and what constitutes the minimum viable dashboard.

---

## 7. Control Flow: Research Split

Two distinct functions, each with a clear job:

### 7.1 External Research: `/research`

The research flow is the primary instance of the curation gate (AP-6) mechanized via scripts (AP-7). The full data management flow is defined in [Role 2: Domain Knowledge](#role-2-domain-knowledge--knowledgemd-new--research-directory).

```
Input:  Research question + SOURCE_INDEX.md
        │
        v
   Agent explores authority sources using specialist agents
   (sysmlv2-doc-analyzer, Explore, etc.)
        │
        v
   Agent writes research document content.
   Script saves to: research/pending/YYYYMMDD-HHMMSS_topic.md
   (agent does not choose file path — script enforces convention)
        │
        v
   Agent presents findings + suggests DI-XXX insight candidates
        │
        v
   User reviews: approve/revise/reject report; accept/modify/skip insights
        │
        v
   Agent calls: agentic-mbse pm approve-research <file> --insights '...'
   (AP-7, Tier 2 script: moves file, assigns IDs, appends to KNOWLEDGE.md)
```

**Key**: The agent's job is content generation and user interaction. The script's job is file operations and registry maintenance. This separation is the core application of AP-7.

### 7.2 Internal Analysis: `/analyze-models`

```
Input:  Model files (models/), test files (tests/),
        MODELING_GUIDE.md + REQUIREMENTS.md (Role 4 rules)
        │
        v
   Parse model structure: files, definitions, usages, cross-file deps
   Check rules compliance: which Role 4 rules are followed/violated
   Compute health indicators: test coverage, validation levels, debt markers
        │
        v
   Produce model state report
   (feeds into /status for architecture health section)
```

**Further design needed**: Should `/analyze-models` be a command (agent-driven, interactive) or a script subcommand (deterministic, like `agentic-mbse analyze`)? The answer depends on how much interpretation vs. parsing is involved. Likely: script for metrics, agent command for interpretation.

---

## 8. Component Catalog

### 8.1 Commands (target: 200-300 lines each)

| Command | Job | Key user decision | Skills referenced |
|---------|-----|-------------------|-------------------|
| `/spec-model` | Define WHAT to model | Scope, success criteria, intent confirmation | project-structure, source-traceability |
| `/design-model` | Decide HOW to model | Architecture approach, interfaces, where things live | sysml-conventions, project-structure, model-validation, source-traceability |
| `/plan-model` | Organize the WORK | Phase ordering, scope per phase, risk priorities | model-validation |
| `/implement-model` | BUILD it correctly | Execution approach, deviation handling, phase approval | sysml-conventions, model-validation, project-structure |
| `/audit-models` | VERIFY it's right | Audit scope, acceptable deviations, action items | model-validation, source-traceability, requirements-tracking |
| `/research` | LEARN from external sources | Research scope, insight capture | source-traceability |
| `/quick-model` | Make a SMALL change | Change scope (guard: redirect if too big) | sysml-conventions, model-validation |
| `/review-model` | REVIEW design before implementing | Pass/concerns/fail per dimension | sysml-conventions, model-validation, project-structure |
| `/analyze-models` | UNDERSTAND current model state | Analysis scope | project-structure, model-validation |
| `/status` | Understand PROJECT STATE | What to do next | epic-decomposition, requirements-tracking |
| `/backlog` | Manage WORK ITEMS | Add, prioritize, decompose, close | epic-decomposition |
| `/onboard` | SET UP a project | Initial goals, architecture sketch, sources | project-structure, source-traceability, epic-decomposition |
| `/manage-sources` | Configure SOURCES | Source additions, validation criteria | source-traceability |

### 8.2 Skills (target: <200 lines SKILL.md each)

See Section 4.2 for the full catalog. Each skill follows the pattern:

```
claude/skills/{skill-name}/
├── SKILL.md        # Principles, key rules, when to apply (~100-200 lines)
└── references/     # Optional deep reference material (loaded on demand)
    └── *.md
```

### 8.3 Agents (unchanged; standardize references)

| Agent | Question types | When to invoke |
|-------|---------------|----------------|
| `sysmlv2-doc-analyzer` | Cross-cutting SysML v2 questions, specification lookups | Broad SysML questions, pattern recommendations |
| `kerml-expert` | KerML standard library functions, base types | Import questions, standard function signatures |
| `sysml-expert` | SysML modeling patterns, part/port/connection | Structural modeling, SysML idioms |
| `syside-expert` | syside parser API, expression evaluation | Parser errors, expression tree questions |
| `sysmlv2-validator` | Syntax validation, error interpretation | Parse failures, validation error triage |
| `python-debugger` | Python debugging | Test failures, CLI issues |

**Invocation principle**: Launch relevant agents in parallel with focused prompts. Synthesize results in main context. This produces higher recall than a single unified agent.

### 8.4 Project Templates

| Template | Ownership | New/Revised |
|----------|-----------|-------------|
| `OVERVIEW.md.template` | User-owned | Revised (add Goals Registry, Analysis Questions) |
| `ARCHITECTURE.md.template` | User-owned | **New** |
| `REQUIREMENTS.md.template` | User-owned | **New** |
| `KNOWLEDGE.md.template` | User-owned | **New** |
| `VALIDATION_MATRIX.md.template` | User-owned | **New** |
| `EPIC_GUIDE.md.template` | Tool-owned | **New** |
| `epic_template.md.template` | Tool-owned | **New** |
| `BACKLOG.md.template` | User-owned | Revised (add intent/scale columns) |
| `MODELING_GUIDE.md.template` | Tool-owned | Revised (reference/how-to material extracted to skills; what remains is pure rules) |
| `MODELING_PROCESS.md.template` | Tool-owned | Revised (reference new documents) |

---

## 9. Implementation Sequencing

### Dependency Graph

```
 ┌───────────────────────────────────────────────────────────────┐
 │                                                               │
 │  PHASE 1: Foundations (can be parallel)                       │
 │                                                               │
 │  ┌─────────────────────┐    ┌─────────────────────┐          │
 │  │ A: Information       │    │ B: Work Item         │          │
 │  │    Architecture      │    │    Taxonomy           │          │
 │  │                      │    │                       │          │
 │  │ - Validate 6 roles   │    │ - Validate intents    │          │
 │  │ - Define entity      │    │ - Validate scales     │          │
 │  │   formats            │    │ - Define routing      │          │
 │  │ - Define document    │    │   logic               │          │
 │  │   set                │    │ - Define UX for       │          │
 │  │ - Create templates   │    │   determination       │          │
 │  └──────────┬───────────┘    └──────────┬────────────┘          │
 │             │                           │                       │
 └─────────────┼───────────────────────────┼───────────────────────┘
               │                           │
               v                           v
 ┌───────────────────────────────────────────────────────────────┐
 │                                                               │
 │  PHASE 2: Knowledge Layer                                    │
 │                                                               │
 │  ┌─────────────────────────────────────────────────────┐      │
 │  │ C: Skills Extraction                                 │      │
 │  │                                                      │      │
 │  │ - Extract shared knowledge from existing commands    │      │
 │  │ - Create SKILL.md for each skill                    │      │
 │  │ - Measure context window impact                     │      │
 │  │ - Adjust granularity based on measurement           │      │
 │  └──────────────────────────┬──────────────────────────┘      │
 │                             │                                 │
 └─────────────────────────────┼─────────────────────────────────┘
                               │
                               v
 ┌───────────────────────────────────────────────────────────────┐
 │                                                               │
 │  PHASE 3: Commands + PM (can be parallel)                    │
 │                                                               │
 │  ┌─────────────────────┐    ┌─────────────────────┐          │
 │  │ D: Command Redesign  │    │ E: PM Script Engine  │          │
 │  │                      │    │                       │          │
 │  │ - Refactor existing  │    │ - Python module       │          │
 │  │   commands to use    │    │   (src/agentic_mbse/  │          │
 │  │   skills             │    │    pm/)               │          │
 │  │ - Add new commands   │    │ - CLI subcommand      │          │
 │  │ - Add intent routing │    │ - Unit tests          │          │
 │  │ - Standardize agent  │    │ - Dashboard output    │          │
 │  │   references         │    │                       │          │
 │  └──────────────────────┘    └───────────────────────┘          │
 │                                                               │
 └───────────────────────────────────────────────────────────────┘
```

### Phase Details

**Phase 1A: Information Architecture** — The prerequisite. Without knowing what entities exist and where they live, skills can't reference them and commands can't produce/consume them. Deliverables: validated role taxonomy, entity formats, document templates, relationship map.

**Phase 1B: Work Item Taxonomy** — Can proceed in parallel with 1A. Defines how pipeline routing works. Deliverables: validated intent types, scale levels, routing decision tree, UX for determination.

**Phase 2C: Skills Extraction** — Depends on 1A (skills reference the information architecture) and 1B (epic-decomposition skill references the taxonomy). Deliverables: 7 skills with SKILL.md files, context window measurements.

**Phase 3D: Command Redesign** — Depends on 2C (commands reference skills). Deliverables: refactored commands at ~200-300 lines, new commands (quick-model, review-model, analyze-models, status).

**Phase 3E: PM Script Engine** — Depends on 1A (needs to know what files to parse). Can proceed in parallel with 3D. Deliverables: `agentic-mbse status` CLI subcommand, unit tests, `/status` command.

---

## 10. Open Design Questions

Grouped by phase. These are the areas where **further work and detailing must be done**.

### Phase 1A: Information Architecture

| # | Question | Options | Recommendation | Must resolve before |
|---|----------|---------|----------------|---------------------|
| Q1 | Are six roles right, or should Domain Knowledge and Project Intent merge? | (a) Keep six (b) Merge to five (c) Different split | Validate against fusion-tea: try to classify every existing artifact into a role. If a role has <3 items, it may not justify its existence | Phase 2C |
| Q2 | Where does Architecture Vision live? | (a) Standalone `ARCHITECTURE.md` (b) Section of `OVERVIEW.md` | Standalone — it's a distinct concern (structural "how" vs project "what/why"). But validate: does fusion-tea have enough content for a standalone file? | Phase 1A completion |
| Q3 | What's the right format for domain insights? | (a) Full AA-XXX format from earlier research (b) Simpler DI-XXX as proposed here (c) Just free-form markdown sections | DI-XXX (b) — enough structure for traceability, not so much that capture becomes burdensome | Phase 1A completion |
| Q4 | How do project-level rules (REQUIREMENTS.md) get promoted from per-feature experience? | (a) Manual — user adds after noticing a recurring pattern (b) Agent-suggested — `/audit-models` proposes promotions (c) Both | Start with (a); add (b) as a future enhancement when patterns are clearer | Phase 1A completion |
| Q5 | When does a registry file become unwieldy? | Need empirical validation | Probably ~100 entries. Fusion-tea with ~37 CAS categories and ~15 requirements/feature is well within single-file territory | Defer to experience |
| Q5a | What is the control flow for intent formalization? | Agent reads `intent/` docs, proposes G-XXX/AQ-XXX entries, user approves, script registers in OVERVIEW.md. Needs: command/script interface, incremental update strategy (new docs added after initial setup), integration with `/onboard` | Follows same pattern as research approval (AP-7 T2) but details TBD | Phase 1A completion |

### Phase 1B: Work Item Taxonomy

| # | Question | Options | Recommendation | Must resolve before |
|---|----------|---------|----------------|---------------------|
| Q6 | Are five intents right, or is that too many? | (a) All five (b) Three: Model/Fix/Investigate (c) Four: drop Integrate | Validate each against AP-3: does it change downstream behavior that another intent doesn't? Start with all five, cut what fails the test | Phase 2C |
| Q7 | How is intent/scale determined? | (a) Interactive prompt (b) User-provided tag (c) Auto-detect with confirmation | (c) with (b) as power-user shortcut — system reads description, suggests, user confirms | Phase 3D |
| Q8 | Is the intent × scale matrix too complex? | (a) Keep full matrix (b) Scale determines entry point, intent is advisory | Start with (a) but monitor: if users ignore it, simplify to (b) | Phase 3D |

### Phase 2C: Skills

| # | Question | Must resolve before |
|---|----------|---------------------|
| Q9 | What's the context window impact of loading 3-4 skills simultaneously? | Phase 3D (commands depend on knowing if skills can be co-loaded) |
| Q10 | Should skills load all content upfront or stage-by-stage? | Phase 3D |
| Q11 | What's the right granularity? If sysml-conventions is 400 lines, is that one skill or two? | Phase 2C completion |

### Phase 3: Commands + PM

| # | Question | Must resolve before |
|---|----------|---------------------|
| Q12 | How do we validate that refactored commands don't lose implicit knowledge? | Phase 3D completion — walkthrough against fusion-tea workflows |
| Q13 | What's the minimum viable PM dashboard? | Phase 3E start |
| Q14 | Should `/analyze-models` be a script or agent command? | Phase 3E start |
| Q15 | Should there be a formal command template (structure all commands must follow)? | Phase 3D start |

### Deferred (not blocking any phase)

| # | Question |
|---|----------|
| Q16 | Git integration for backward navigation and checkpointing |
| Q17 | Hook integration (auto-validation on model file writes) |
| Q18 | Cross-project sharing of insights and patterns |
| Q19 | Should prototyping remain embedded in design or become `/prototype-model`? |

---

## References

| Document | Key Contribution to This Concept |
|----------|--------------------------------|
| `.project/research/20260126-161628_python-vs-mbse-command-comparison.md` | Quantified the gaps: commands 2x too long, PM missing, 7 command types absent |
| `.project/research/20260126-202931_requirements-goal-tracking-pipeline.md` | Requirements dropping problem, Analysis Angles concept, pipeline flow analysis |
| `.project/research/20260130-234525_agentic-mbse-pipeline-critical-analysis.md` | Five structural problems, jobs-to-be-done analysis, redesign vision with command sketches |
| `.project/research/20260130-235423_information-role-taxonomy.md` | Six information roles, traceability gaps, curation gate concept, feedback loops |
| `.project/concepts/toolkit-redesign.md` | Initial concept organization into 7 design concepts with sequencing |

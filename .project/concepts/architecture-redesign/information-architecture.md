# Information Architecture

**Parent**: [main.md](main.md) — Problem, principles, implementation plan
**Concern**: What data exists, where it lives, how it flows between roles

This document defines the six information roles, their entity formats, the project file structure, and the document relationship map. It is the data model reference for the architecture redesign.

---

## 1. The Information Flow Model

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

---

## 2. Project File Structure

A target project after `agentic-mbse init` and as it grows. Four top-level content directories, each answering a different question:

| Directory | Question | Information roles |
|-----------|----------|-------------------|
| `knowledge/` | "What do we know?" | Roles 1-2: Authority Sources, Domain Knowledge |
| `modeling_project/` | "What are we building and how?" | Roles 3-6: Intent, Requirements, Decisions, Verification |
| `work/` | "What's in progress?" | Work management: backlog, active, completed |
| `models/` | "The models themselves" | Model artifacts |

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
│       ├── kerml-expert.md
│       ├── sysml-expert.md
│       ├── syside-expert.md
│       ├── sysmlv2-validator.md
│       └── python-debugger.md
│
├── knowledge/                 # "What do we know?"
│   ├── SOURCE_INDEX.md        #   Role 1: Authority sources registry (user-owned)
│   ├── KNOWLEDGE.md           #   Role 2: Curated domain insights, DI-XXX (user-owned)
│   ├── sources/               #   Local reference materials (PDFs, data tables)
│   │   └── ...                #   External repos stay external, referenced by path
│   └── research/              #   Research pipeline
│       ├── pending/           #     Unapproved research
│       │   └── YYYYMMDD-HHMMSS_topic.md
│       ├── approved/          #     User-approved research
│       │   └── YYYYMMDD-HHMMSS_topic.md
│       └── impacts/           #     Impact reports from knowledge supersession
│           └── DI-XXX_superseded.md
│
├── modeling_project/           # "What are we building and how?"
│   ├── OVERVIEW.md            #   Role 3: Goals (G-XXX), questions (AQ-XXX) (user-owned)
│   ├── ARCHITECTURE.md        #   Role 5: Structural decisions, AD-XXX (user-owned)
│   ├── REQUIREMENTS.md        #   Role 4: Project-specific rules, PR-XXX (user-owned)
│   ├── VALIDATION_MATRIX.md   #   Role 6: Verification criteria, SV-XXX (user-owned)
│   ├── MODELING_GUIDE.md      #   Role 4: Baseline modeling rules (tool-owned)
│   ├── MODELING_PROCESS.md    #   Workflow reference (tool-owned)
│   └── intent/                #   Raw user documents (user-owned)
│       ├── project-charter.md #     User-written/uploaded, any length
│       └── *.md               #     Stakeholder notes, mission docs, etc.
│
├── work/                      # "What's in progress?"
│   ├── BACKLOG.md             #   Dashboard: YAML frontmatter for machine state, body for human view (user-owned)
│   ├── EPIC_GUIDE.md          #   Decomposition guide (tool-owned)
│   ├── backlog/               #   Epic decomposition files (user-owned)
│   │   └── epic-{name}.md    #     Detailed scope, items, sequencing, risks
│   ├── active/                #   In-progress work items
│   │   └── {WI-XXX}_{name}/
│   │       ├── spec.md
│   │       ├── design.md
│   │       └── plan.md
│   ├── completed/             #   Archived work
│   │   └── YYYYMMDD_{WI-XXX}_{name}/
│   ├── analysis/              #   /analyze-models output (operational intelligence)
│   │   └── YYYYMMDD-HHMMSS_topic.md
│   └── learnings/
│       └── RAW_LEARNINGS.md   #   Process knowledge (append-only)
│
├── models/                    # Model artifacts
│   ├── library/               #   Reusable definitions (part defs, calc defs)
│   │   ├── foundation/
│   │   └── calculations/
│   └── designs/               #   Specific configurations (usages)
│       └── {config-name}/
│
├── tests/
│   └── models/                #   Model validation tests (pytest)
│
├── data/                      # Machine-readable evidence
│   └── traceability_matrix.csv
│
├── CLAUDE.md                  # Project-specific essentials
└── README.md
```

**Key structural decisions**:

- **`knowledge/`**: Home for Roles 1-2. SOURCE_INDEX.md, KNOWLEDGE.md, and the research pipeline all live here. The `sources/` subdirectory is for project-local reference materials; external repos stay external and are referenced by path in SOURCE_INDEX.md. Research reports start in `pending/`; the approval script (AP-7, T2) moves them to `approved/` and extracts insights into `KNOWLEDGE.md` — a visible file system operation, not an invisible metadata change.
- **`modeling_project/`**: The project's "constitution" — Roles 3-6 together. Formalized intent (OVERVIEW.md) sits next to the standards and decisions that derive from it (ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md). Raw intent documents nest in `modeling_project/intent/`, preserving the derivation relationship. MODELING_GUIDE.md and MODELING_PROCESS.md are methodology references that constrain how work is done.
- **`work/`**: Purely operational — tracking and executing work. BACKLOG.md, active items, completed archives, analysis reports, and learnings. Nothing here defines standards or project identity.
- **`.claude/`**: Tooling home. Commands, skills, agents are all tool-owned and updated on `agentic-mbse init --update`.
- **`models/` and `tests/`** at project root: Model artifacts are the primary output.
- **`data/`**: Machine-readable evidence (traceability_matrix.csv). Grows naturally if codegen/simulation artifacts land here (B-004).

---

## 3. Role Definitions and Data Models

Each role has a concrete entity format. These are the **data models** — the structured records that commands produce, consume, and maintain.

### Role 1: Authority Sources — `knowledge/SOURCE_INDEX.md`

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

### Role 2: Domain Knowledge — `knowledge/KNOWLEDGE.md` (new) + `knowledge/research/` directory

**Purpose**: Curated, approved knowledge that has passed through the curation gate. Captures domain insights — interpretive perspectives that bridge raw data and model requirements.

**Two artifacts**:

| Artifact | Purpose | Trust level |
|----------|---------|-------------|
| `knowledge/research/pending/*.md` | Raw research output. May contain errors, hallucinations, or irrelevant findings. Explicitly **not trusted** until approved. | Untrusted |
| `knowledge/research/approved/*.md` | User-reviewed research. The user has confirmed the findings are accurate and relevant. | Trusted |
| `knowledge/KNOWLEDGE.md` | Structured domain insights extracted from approved research. The actionable feed for modeling work. | Trusted, structured |

**Entity format** (`KNOWLEDGE.md`):
```markdown
### DI-XXX: [Title]
- **Source**: [approved research doc, user note, authority source, or work-item:{WI-XXX}/{artifact}]
- **Rationale**: [only for inline-captured insights: why this was recognized and what evidence supports it]
- **Context**: [1-3 sentences: the domain fact and why it matters]
- **Model implications**: [what the models must capture because of this insight]
- **Analysis implications**: [what analyses this enables or requires]
- **Status**: captured | addressed | superseded
- **Superseded-by**: [DI-XXX ID, only when status = superseded]
- **Supersedes**: [DI-XXX ID, when this insight replaces an earlier one]
```

The `Rationale` field is optional — present only when the source is a work item artifact (inline capture via the `add-insight` script) rather than an approved research document (which provides its own provenance through the full research pipeline). It records *why* the insight was recognized and *what evidence* supports it, compensating for the lighter provenance chain of the inline path.

**Status values**:
- `captured`: Insight recorded in KNOWLEDGE.md, not yet reflected in models
- `addressed`: Model elements exist that trace to this insight (verified via `data/traceability_matrix.csv`)
- `superseded`: Replaced by a newer insight; `Superseded-by` field identifies the replacement

**Design note**: The `Derived requirements` field from earlier drafts has been removed. Back-references from DI-XXX to model elements are not maintained on the KNOWLEDGE.md side — that would create a maintenance burden with no query benefit. Instead, impact queries go through `data/traceability_matrix.csv` (Knowledge column), which maps DI-XXX directly to model elements. See [§ 5. Traceability Model](#5-traceability-model).

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
Script writes to: knowledge/research/pending/YYYYMMDD-HHMMSS_topic.md
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
│ 1. Move file: knowledge/research/pending/ →     │
│    knowledge/research/approved/                  │
│ 2. For each insight in --insights:              │
│    a. Assign next DI-XXX ID                     │
│    b. Format as structured entry                │
│    c. Append to knowledge/KNOWLEDGE.md          │
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
- Research in `knowledge/research/pending/` is visible in the file system — the user can review it in their IDE, share it, or come back to it later

**Alternative entry points for KNOWLEDGE.md**:
- User can add entries directly (manual edit)
- Any command (`/spec-model`, `/design-model`, `/implement-model`, etc.) can capture insights inline via the `add-insight` script (AP-7, T1 with T3 invocation). The agent proposes a DI-XXX candidate, the user approves, and the agent calls the script with pre-formed content — no LLM call needed. Source uses the `work-item:{WI-XXX}/{artifact}` convention. See [backlog.md B-008](backlog.md) for the full control flow.

**Producer**: `/research` → approval script → `knowledge/KNOWLEDGE.md`; inline capture via `add-insight` script; user direct entry
**Consumer**: `/spec-model` (surfaces relevant insights), `/status` (coverage reporting)

---

### Role 3: Project Intent — `modeling_project/intent/` directory + `modeling_modeling_project/OVERVIEW.md` (revised)

**Purpose**: Why this project exists. What questions the models must answer. This is the demand signal.

**Two concerns, separated**:

| Concern | What it is | Where it lives |
|---------|-----------|----------------|
| **Raw intent documents** | User-authored or uploaded prose: project charters, mission statements, stakeholder notes, meeting summaries. These can be lengthy (400+ lines) and are the user's own words. | `modeling_project/intent/` directory |
| **Formalized goals and questions** | Structured, ID'd entries extracted from the raw documents. These are what the rest of the system references. | `modeling_modeling_project/OVERVIEW.md` (Goals Registry, Analysis Questions tables) |

**Raw intent documents** (`modeling_project/intent/`):
```
modeling_project/intent/
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
- User uploads/writes documents in `modeling_project/intent/`
- An agent-driven process reads the documents, proposes structured G-XXX goals and AQ-XXX analysis questions
- User reviews, approves, modifies, or rejects each
- A script registers approved entries in `modeling_modeling_project/OVERVIEW.md` (correct IDs, format, source traceability)
- This process can be triggered during `/onboard` (initial project setup) or run standalone when new intent documents are added

A dedicated command — `/formalize-intent` — handles this flow. It can be triggered during `/onboard` (initial project setup) or run standalone when new intent documents are added to `modeling_project/intent/`. The command reads intent documents, proposes G-XXX/AQ-XXX entries, the user reviews and approves, and a script registers them in OVERVIEW.md (AP-7 T2: script assigns IDs and enforces format; agent generates the structured entries from prose). Incremental updates (new docs added after initial setup) use the same command — the agent reads OVERVIEW.md to see what's already formalized and proposes only new entries. Detailed command design is a Phase 3C concern.

**Producer**: `/onboard` (triggers `/formalize-intent`), `/formalize-intent` (standalone), user direct editing
**Consumer**: `/spec-model` (reads goals/questions to inform scoping), `/status` (reports goal coverage), `/audit-models` (checks that goals are addressed)

---

### Role 4: Modeling Requirements — `modeling_modeling_project/MODELING_GUIDE.md` (tool-owned baseline) + `modeling_modeling_project/REQUIREMENTS.md` (user-owned extensions)

**Purpose**: Project-wide rules, patterns, and constraints that govern how *all* modeling work is done. These are durable standards that derive from Project Intent and Domain Knowledge — not per-feature specs (those are ephemeral artifacts of individual work items, living within Model Implementation).

**This is NOT a registry of every MR-XXX from every work item.** Per-feature requirements (MR-XXX in spec.md) are part of Model Implementation (the work item cycle defined in → [workflows.md](workflows.md)). They are ephemeral — a work item may be tried, completed, later revised, or abandoned. Tracking every one at the project level would be untenable.

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
| **Domain requirements** | Promoted from per-work-item specs; trace to DI-XXX domain insights or G-XXX goals | "Power balance must account for recirculating power fraction" (promoted from MR-XXX in a power balance spec) |

**Requirement promotion path**: Not all per-feature MR-XXX requirements stay ephemeral. Significant domain requirements — those worth tracking long-term because they constrain all future modeling work — are promoted to PR-XXX in REQUIREMENTS.md during `/implement-model`. The promotion is selective: fine-grained implementation details ("use ISQ::mass for weight attributes") stay in spec.md and are archived with the work item. Only requirements that represent durable project-wide standards get promoted. The `trace-element` AP-7 script handles the promotion mechanically. See [§ 5. Traceability Model](#5-traceability-model) for the full promotion flow.

**Each requirement specifies both criteria and method**: What constitutes compliance, and how to check it (validation rule, design review checklist, regression test). This is what makes them enforceable rather than aspirational.

**Lifecycle**:
- **Baseline (MODELING_GUIDE.md)**: Ships with agentic-mbse. Updated across versions. Users don't edit.
- **Extensions (REQUIREMENTS.md)**: Discovered through implementation experience → proposed (often promoted from a per-feature pattern) → reviewed → added. These grow slowly and deliberately — a new entry means a new project-wide standard.

**Producer**: `agentic-mbse init` (MODELING_GUIDE.md), `/onboard` (initial REQUIREMENTS.md from intent), user direct editing, promoted from per-feature experience
**Consumer**: `/design-model` (checks compliance), `/implement-model` (enforces during work), `/audit-models` (verifies across features), `/review-model` (checks design against rules)

---

### Role 5: Modeling Decisions — `modeling_modeling_project/ARCHITECTURE.md` (new)

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

### Role 6: System Verification — `modeling_modeling_project/VALIDATION_MATRIX.md` (new)

**Purpose**: Verification criteria for the integrated system — beyond per-work-item checks.

**Entity format**:
```markdown
## Verification Registry

| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |
|----|-------------|------|-----------|----------|-----------|--------|------|--------|
| SV-001 | Total capital cost ballpark | reasonableness | test | $3B-$15B | range | engineering judgment | test_capital_cost_range | pending |
| SV-002 | p_net output accuracy | baseline | test | PyFECONS value | ±1% | PowerBalance.py:94 | test_pnet | passing |
| SV-003 | Energy balance conservation | physical | test | sum = total | ±0.1% | physics | test_energy_balance | pending |
| SV-004 | All calc defs have doc comments | model | model | present | exact | MODELING_GUIDE.md | - | passing |
```

**Verification types** (each describes **what** is being checked):

| Type | What it checks | When it runs |
|------|---------------|-------------|
| reasonableness | Output is in expected ballpark | After any simulation |
| baseline | Output matches reference implementation | After feature implementation |
| physical | Conservation laws hold | After model integration |
| relationship | Input/output vary in expected direction | Sensitivity analysis |
| rollup | Aggregations are consistent | After cost rollup features |

**Verification mechanisms** (each describes **how** the check is performed):

| Mechanism | Meaning | Example |
|-----------|---------|---------|
| `model` | Verifiable by model inspection / `agentic-mbse validate` | Structural completeness, naming conventions |
| `test` | Verifiable by pytest (may include codegen + simulation) | p_net accuracy, energy balance conservation |
| `manual` | Requires human judgment | "Architecture is reasonable for CATF concept" |

Mechanism is orthogonal to type: a `baseline` check might be verified by `model` inspection (comparing structure) or by `test` (running codegen + teax and comparing output). The distinction matters because `test` entries that exercise the downstream pipeline (sysml-codegen → teax) cannot be verified until that pipeline is operational. The `/status` dashboard uses the Mechanism column to report: "N entries require simulation tests and are not yet verifiable."

**Producer**: `/spec-model` (creates entries from requirements), `/audit-models` (updates status)
**Consumer**: `/audit-models`, `/status`, PM script engine

---

## 4. Document Relationship Map

```
modeling_project/intent/        knowledge/SOURCE_INDEX.md
  raw user documents               Authority sources
       │                               │
       │ formalization flow             │ explored by /research
       │ (agent + AP-7 script)          v
       v                          knowledge/research/pending/
modeling_project/OVERVIEW.md                    │
  G-XXX goals ──────────────►         │ user approves (AP-7 script)
  AQ-XXX questions                    v
       │                         knowledge/research/approved/
       │◄── refines ──────────────────────────────────────────►
       │                                                knowledge/KNOWLEDGE.md
       │                                                DI-XXX domain insights
       │                                                 │
       │                                                 │ "this insight implies..."
       v                                                 v
Role 4: Modeling Requirements       Role 5: Modeling Decisions
  (methodology — HOW to model)        (architecture — WHAT structure)
  modeling_project/MODELING_GUIDE.md            modeling_project/ARCHITECTURE.md
  modeling_project/REQUIREMENTS.md               AD-XXX decisions
       │                                     │
       │  constrains methodology             │ constrains structure
       │                                     │
       v                                     v
                   Work Execution
                    (per-feature spec/design/plan —
                     ephemeral, work-item-scoped)
                    work/active/{WI-XXX}_{name}/
                              │
                              │ produces
                              v
                         Model Artifacts
                          (models/, tests/)
                              │
                    ┌─────────┼──────────────────────┐
                    │         │                       │
                    │         │ verified against       │ consumed by
                    │         v                       v
                    │  modeling_project/VALIDATION_MATRIX.md  Downstream Pipeline
                    │    SV-XXX criteria             (sysml-codegen → teax)
                    │         ^                       │
                    │         │  simulation results   │
                    │         │  feed back via tests/ │
                    │         └───────────────────────┘
                    │
                    │ Level 8 validates codegen readiness
                    │ (contract: derived from sysml-codegen requirements)
                    v
```

### 4.1 Downstream Pipeline Boundary

The modeling workflow does not end at `models/`. The full value chain is:

```
models/ ──► sysml-codegen ──► teax ──► analysis results
```

However, agentic-mbse **defines the boundary, not the other side of it**. sysml-codegen and teax are separate tools with their own architectures, CLIs, and error reporting. agentic-mbse's responsibility is:

- **Outbound**: Produce models that are codegen-ready (validated by Level 8)
- **Inbound**: Accept verification evidence from the downstream pipeline (via pytest tests that exercise codegen + teax, reported through VALIDATION_MATRIX.md)

The feedback path is through `tests/` — pytest tests written during the normal work PM flow that may exercise the full pipeline. These tests are the link between downstream results and SV-XXX verification status. No separate feedback mechanism is needed.

**What agentic-mbse does NOT do**:
- Orchestrate or manage sysml-codegen or teax execution
- Automatically create backlog items from codegen errors (those are compile errors — fix immediately)
- Persist simulation results (teax tracks its own provenance)

---

## 5. Traceability Model

The information roles defined above are connected by explicit, typed links. These links are the primary mechanism for impact analysis when knowledge evolves. Traceability is not an information role — it is the *connective tissue between roles*.

### 5.1 Design Principle: Durable Chain Only

The traceability chain must use only durable artifacts. Per-work-item spec.md files are where requirements are *discovered* and promotion decisions are *made*, but they are not load-bearing for traceability. The durable chain is:

```
DI-XXX (domain insight, in KNOWLEDGE.md)
   |
   | Source column in REQUIREMENTS.md
   v
PR-XXX (promoted requirement, in REQUIREMENTS.md)
   |
   | Requirement column in traceability_matrix.csv
   v
Model element (part def, calc def, constraint)
   |
   | Source/Reference fields in doc comment
   v
Authority source (file:line in PyFECONS, section in spec doc)
```

Every node in this chain is durable. Specs are numerous, fine-grained, and may be superseded or archived. If the traceability chain depended on spec.md being present and parseable, it would break when work items are completed and archived.

**How this works in practice**:
- `/spec-model` writes spec.md with many fine-grained MR-XXX requirements (ephemeral)
- Some MR-XXX are significant enough to be durable — the agent or user flags these for promotion
- `/implement-model` calls the `trace-element` AP-7 script, which:
  1. Promotes flagged MR-XXX to PR-XXX in `modeling_project/REQUIREMENTS.md` (if not already there)
  2. Records the model element → PR-XXX link in `data/traceability_matrix.csv`
  3. The PR-XXX entry's `Source` column records the DI-XXX or G-XXX it derives from

### 5.2 Link Types

| Link | From | To | Recorded in | Verified by |
|------|------|----|-------------|-------------|
| **derives** | DI-XXX (insight) | PR-XXX (requirement) | REQUIREMENTS.md `Source` column | /audit-models (coverage check) |
| **satisfies** | Model element | PR-XXX (requirement) | traceability_matrix.csv `Requirement` column | /audit-models (completeness check) |
| **sources** | Model element | Authority source | Doc comment `Source`/`Reference` fields | Level 6 validation (existence + format) |
| **traces-to** | PR-XXX (requirement) | G-XXX (goal) or AQ-XXX (question) | REQUIREMENTS.md `Source` column | /status (goal coverage) |
| **justifies** | AD-XXX (decision) | Model structure | ARCHITECTURE.md `Rationale` field | /audit-models (adherence check) |
| **supersedes** | DI-XXX (new) | DI-XXX (old) | KNOWLEDGE.md `Superseded-by` field | approval script (automatic) |

All links are between durable artifacts. Per-work-item spec.md files may reference these IDs but are not part of the durable traceability chain.

### 5.3 The Traceability Matrix

`data/traceability_matrix.csv` is the authoritative record of model-element-level traceability. It maps each significant model element to its justifying requirements and authority sources.

**Schema**:

| Column | Description | Example |
|--------|-------------|---------|
| Element | Model element name | `MagnetSystemCostCalc` |
| File | SysML file path | `models/library/calculations/magnet_cost.sysml` |
| Type | Element kind | `calc def` |
| Knowledge | DI-XXX IDs this element traces to | `DI-003, DI-012` |
| Requirement | PR-XXX IDs this element satisfies | `PR-005` |
| Source_Type | Authority source kind | `codebase` |
| Source_Document | Authority source name | `PyFECONS` |
| Source_Location | Specific location | `CAS220103/magnet_cost.py:94` |
| Confidence | Assessment | `High` |
| Assumptions | Known approximations | `Uses 2024 material costs` |
| Last_Verified | Date of last audit | `2026-01-28` |

The matrix has both `Knowledge` (DI-XXX) and `Requirement` (PR-XXX) columns. Either or both may be populated for a given element. The `Knowledge` column enables direct impact queries when a DI-XXX is superseded, without requiring an intermediate requirement hop. The `Requirement` column enables requirement coverage checking.

**Ownership**: Tool-owned schema (columns), user-owned data (rows).

**Populated by**: `/implement-model` calls `agentic-mbse pm trace-element` (AP-7 T1 script) to append rows. Agent supplies content; script enforces schema, prevents duplicates, validates PR-XXX IDs exist in REQUIREMENTS.md and DI-XXX IDs exist in KNOWLEDGE.md.

**Verified by**: `/audit-models` (checks completeness). Future: `agentic-mbse validate` traceability level (parses SysML via syside, checks all definitions have entries).

**Queried by**: PM script engine (impact analysis).

### 5.4 Traceability Diagrams

**Forward path** (durable chain):

```
KNOWLEDGE.md               REQUIREMENTS.md
  DI-XXX ───derives───>  PR-XXX
                             |
                             | satisfies (traceability_matrix.csv)
                             v
                        Model elements ──sources──> Authority sources
                         (models/)                  (SOURCE_INDEX.md)
```

**Impact propagation** (reverse path):

```
DI-XXX superseded
  |
  | traceability_matrix.csv Knowledge column (direct lookup)
  v
Model elements needing review
  |
  | work/active/ directory scan
  v
Impact report -> user decides on action
```

### 5.5 Traceability Validation

**Architectural requirement**: The validation pyramid must include programmatic traceability checking. This is the enforcement mechanism that makes the traceability model reliable.

Level 6 validation (`level6_traceability.py`) currently only checks doc comment *existence*. It must be extended with the following sub-checks:

1. **Format check**: Doc comments on definitions contain `Source` and `Reference` fields
2. **Resolvability check**: Referenced source documents exist in SOURCE_INDEX.md
3. **Completeness check**: `traceability_matrix.csv` has an entry for each definition (parsed via syside adapter)
4. **Requirement coverage check**: Every PR-XXX in `modeling_project/REQUIREMENTS.md` has at least one satisfying element in `traceability_matrix.csv`

Sub-checks 1-3 extend Level 6. Sub-check 4 is a cross-file check that may belong in Level 7 (architectural integrity) or as a standalone `agentic-mbse validate --traceability` flag.

**Implementation**: Phase 3D. The syside adapter already parses SysML files and can enumerate definitions. The new check compares that list against `traceability_matrix.csv` entries.

### 5.6 Remaining Open Questions

1. **Traceability validation level number**: Should this be a sub-level of Level 6 (traceability & documentation) or a new level? Level 6 currently checks doc comment existence; adding traceability matrix completeness and source resolvability is a natural extension. Recommend: extend Level 6 with sub-checks rather than adding a new level. Resolve during Phase 3D.

2. **`trace-element` script interface**: Exact CLI arguments and behavior for the AP-7 script that `/implement-model` calls, including the promotion step. Resolve during Phase 3D when implementing the PM script engine.

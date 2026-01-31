# Architecture Backlog

**Date**: 2026-01-31
**Status**: Active — items to resolve before finalizing unified-toolkit-architecture.md

---

## Index

| ID | Title | Severity | Resolve before | Status |
|----|-------|----------|----------------|--------|
| B-001 | [Model Implementation as a first-class concern](#b-001-model-implementation-as-a-first-class-concern) | High | Phase 1A | New |
| B-002 | [Knowledge evolution and traceability are incomplete](#b-002-knowledge-evolution-and-traceability-are-incomplete) | High | Phase 1A | Approved |
| B-003 | [Delete intent dimension; simplify work item taxonomy](#b-003-delete-intent-dimension-simplify-work-item-taxonomy) | Medium | Phase 1A | Approved |
| B-004 | [Downstream pipeline is invisible](#b-004-downstream-pipeline-is-invisible) | Medium-High | Phase 1A | New |
| B-005 | [Markdown parsing as state store is fragile](#b-005-markdown-parsing-as-state-store-is-fragile) | Medium | Phase 1A | New |
| B-006 | [No decision promotion path from design.md to ARCHITECTURE.md](#b-006-no-decision-promotion-path) | Low | Phase 3D | New |
| B-007 | [/review-model vs /audit-models boundary underspecified](#b-007-review-model-vs-audit-models-boundary) | Low | Phase 3D | New |
| B-008 | [No inline knowledge capture during non-research commands](#b-008-no-inline-knowledge-capture) | Low-Medium | Phase 3D | New |
| B-009 | [SOURCE_INDEX.md placement inconsistent](#b-009-source_indexmd-placement-inconsistent) | Low | Phase 1A | Closed |
| B-010 | [No migration strategy for existing projects](#b-010-no-migration-strategy-for-existing-projects) | Medium-High | Phase 3E | New |
| B-011 | [AP-7 Tier 2 claude -p dependency unaddressed](#b-011-ap-7-tier-2-claude--p-dependency) | Medium | Phase 3E | New |
| B-012 | [File structure should reflect information flow model](#b-012-file-structure-should-reflect-information-flow-model) | High | Phase 1A | Complete |

---

## B-001: Model Implementation as a first-class concern

**Severity**: High
**Resolve before**: Phase 1A
**Status**: New
**Context**: The unified architecture doc currently labels `active/` as "ephemeral, not a Role." This is wrong. The management of work items, epics, and their lifecycle is a core architectural concern.

### The Problem

The current unified-toolkit-architecture.md defines six information roles. Five of them (Authority Sources, Domain Knowledge, Project Intent, Modeling Requirements, Modeling Decisions) have detailed data models, control flows, and structured homes. The sixth — what the original taxonomy research called "Model Implementation" — was collapsed to a footnote.

The justification was: "per-feature spec/design/plan files are ephemeral, so they don't need a role in the information architecture." This confused two things:

1. **The artifacts** (spec.md, design.md, plan.md) — yes, these are scoped to a work item and archived when done
2. **The process** of creating, managing, and completing work — this is not ephemeral at all; it is the central activity the entire toolkit exists to support

The original taxonomy (`.project/research/20260130-235423_information-role-taxonomy.md`) had this as a full role with sub-stages: Architecture, Epics, Work Item Cycle, Model Artifacts, and a Decision Lifecycle with feedback loops. All of that was dropped.

### What "Role" means in this architecture

A Role in the information architecture is a **category of information with defined producers, consumers, data models, and lifecycle management**. The question is not whether the individual artifacts are long-lived — it's whether the system needs structured management of this category.

By this definition, Model Implementation is unambiguously a Role:
- It has producers (the entire command set: `/spec-model`, `/design-model`, etc.)
- It has consumers (`/status`, `/audit-models`, the PM script engine)
- It needs data models (what is an epic? what is a work item? what states can they be in?)
- It needs lifecycle management (creation, execution, pausing, resuming, archiving, feedback)

### What Must Be Managed

#### 1. Epic Lifecycle

Epics are scoped chunks of modeling work aligned to goals and architecture.

**Data model needed**:
- What is an epic? (scope, goal alignment, decomposition into work items)
- What states can an epic be in? (proposed, active, paused, completed, revised)
- How does an epic relate to Goals (G-XXX) and Architecture Decisions (AD-XXX)?
- Where does an epic live in the file system?

**Control flows needed**:
- Creation: How are epics proposed and approved? Must align with OVERVIEW.md goals and ARCHITECTURE.md structure.
- Decomposition: How is an epic broken into work items? (The `epic-decomposition` skill covers the methodology, but the actual mechanics — where items go, how they're tracked — need definition.)
- Completion: How is an epic closed? What gets archived? What gets updated?

#### 2. Work Item Lifecycle

Work items are the individual units that go through the pipeline (spec -> design -> plan -> implement).

**Data model needed**:
- What is a work item? (intent, scale, current stage, parent epic)
- What states can a work item be in? (backlog, active:speccing, active:designing, active:planning, active:implementing, paused, completed, abandoned)
- What artifacts does a work item produce at each stage? (spec.md, design.md, plan.md, model files)
- How is state tracked? (File system conventions that the PM script engine can parse)

**Control flows needed**:
- Creation: From epic decomposition, or standalone (quick fix, investigation).
- Stage transitions: What triggers moving from spec -> design -> plan -> implement? Who/what validates that a stage is complete?
- Pausing and resuming: How does the system track that a work item was paused at "implementing, phase 2 of 3"? How does it resume?
- Abandonment: What happens when a work item is abandoned? (Different from completion — no archive celebration, but the artifacts may still be useful.)

#### 3. The Pipeline Execution Process

The spec -> design -> plan -> implement cycle itself.

**Already partially defined** in the unified architecture (Sections 5-7: Work Item Model, PM, Research Split). But the current treatment focuses on *routing* (which stages to run based on intent/scale) and says little about:

- **Stage completion criteria**: How does the system know a spec is "done enough" to move to design? Is it purely user approval, or are there structural checks? (E.g., "spec must have at least one MR-XXX" or "design must have a validated prototype.")
- **Artifact conventions**: What exactly goes in each artifact file? Not the templates (those are in commands), but the file system conventions that make artifacts parseable by scripts.
- **Inter-stage data flow**: What does design.md read from spec.md? What does plan.md read from design.md? These dependencies define the contract between pipeline stages.

#### 4. Feedback Loops

The most architecturally important and currently least defined aspect.

**4a. Keeping PM documents up to date**

When a work item completes, what project-level documents need updating?
- BACKLOG.md status
- REQUIREMENTS.md (if the work item revealed a new project-wide rule — Role 4 promotion)
- ARCHITECTURE.md (if the work item produced a new architectural decision — Role 5 evolution)
- VALIDATION_MATRIX.md (if new system-level verification criteria emerged)
- KNOWLEDGE.md (if new domain insights were discovered during implementation)

**This is a non-trivial coordination problem.** Currently nothing ensures these updates happen. The PM script engine (AP-7) can detect *staleness* (e.g., "work item X completed but BACKLOG.md still shows it as active"), but someone needs to trigger the updates.

**Options**:
- Agent-prompted: At work item completion, the `/status close` flow prompts "do any project documents need updating?" and walks through each
- Script-checked: The PM engine detects inconsistencies and flags them in the dashboard
- Both: Script detects, agent helps resolve

**4b. Revising strategies based on learnings**

As work items complete, the team learns things that may invalidate earlier decisions:
- An epic's scope was wrong -> revise the epic, re-decompose
- An architectural decision doesn't hold -> revise ARCHITECTURE.md
- A goal turns out to be infeasible -> revise OVERVIEW.md
- A modeling rule is too strict or too loose -> revise REQUIREMENTS.md

**This is the "going back" problem at the project level** (distinct from the per-work-item backward navigation already described in Section 5.5 of the architecture doc).

**Control flow needed**: When a work item reveals a project-level issue, how does the system:
1. Surface the issue (detection — could be agent insight or user observation)
2. Scope the impact (which documents are affected? which other work items depend on the flawed decision?)
3. Execute the revision (update the document, re-validate affected work items)
4. Track the revision (so it's clear the project evolved, not that someone made an error)

**4c. Non-linear development**

Already partially addressed by the Work Item Taxonomy (intent x scale) and backward navigation. But some scenarios need more definition:

- **Quick fixes that bypass the pipeline**: `/quick-model` handles trivial changes, but what if a quick fix reveals a deeper problem? How does it escalate to a full work item?
- **Refactoring across work items**: A refactoring work item touches artifacts produced by multiple completed work items. How does it interact with the archived artifacts?
- **"Undo" at the work item level**: A completed work item turns out to be wrong. What's the process? Create a new "Fix" work item that references the original? Reopen the original?
- **Concurrent work items**: Two work items are active simultaneously and touch overlapping model files. How are conflicts detected and resolved?

### Proposed Strategy

**Recommendation: Option C (Hybrid)** — Add a brief Role entry in Section 3 that defines the data models (epic, work item, states, file system conventions). Then create a dedicated section that defines the process (pipeline execution, feedback loops, non-linear development). The Role entry points to the process section for control flows.

This aligns with how we've already structured other roles: Role 2 (Domain Knowledge) has a data model in Section 3 and a control flow (research-to-knowledge flow) described separately. Role 3 (Project Intent) has a data model in Section 3 and a deferred control flow (intent formalization).

See also: [B-001 Open Questions](#b-001-open-questions)

### B-001 Open Questions

1. **Epic data model**: What fields does an epic have? The `epic-decomposition` skill covers methodology, but the actual data model (ID scheme, required fields, relationship to goals) needs definition.

2. **Work item state derivation**: The current PM script engine section (6.2) derives state from file system structure. Is this sufficient, or do we need an explicit state file (e.g., `work/active/{item}/STATUS.md`) for states that can't be inferred from file existence alone (paused, abandoned)?

3. **Stage completion criteria**: Are these purely user-approved ("I'm done with the spec, let's move on") or do we add structural checks ("spec must contain at least one MR-XXX before moving to design")? Structural checks add rigor but also friction.

4. **Feedback loop automation**: How much of the "keep PM documents up to date" flow should be automated vs. prompted? The AP-7 principle says scripts handle state transitions, but detecting *which* transitions are needed may require agent judgment.

5. **Concurrent work item conflicts**: Is this a real problem for modeling projects, or is it rare enough to handle ad-hoc? Fusion-tea has had ~3 concurrent active items — conflicts have been manageable.

6. **Relationship to existing Sections 5-7**: If we adopt Option C, the existing Work Item Model (Section 5), PM (Section 6), and Research Split (Section 7) sections need consolidation. How much restructuring is appropriate at this stage vs. deferring to when we actually implement?

### References

- `.project/research/20260130-235423_information-role-taxonomy.md` — Original Role 5: Model Implementation (Sections 5a-5d)
- `.project/concepts/unified-toolkit-architecture.md` — Current treatment (collapsed to footnotes)
- `.project/research/20260130-234525_agentic-mbse-pipeline-critical-analysis.md` — Part 4: Robustness for Non-Linear Development

---

## B-002: Knowledge evolution and traceability are incomplete

**Severity**: High
**Resolve before**: Phase 1A
**Status**: Approved

This item covers three related problems that must be solved together: (A) knowledge can't evolve, (B) model-to-knowledge traceability isn't formalized in the architecture, and (C) there's no impact propagation when knowledge changes.

### Problem A: Knowledge evolution is one-directional

The curation gate (AP-6) is carefully designed for forward flow: raw research -> approval -> KNOWLEDGE.md. But knowledge evolves. Later research may contradict or supersede earlier insights.

- DI-XXX status has `captured | requirements-derived | addressed` — but no `superseded` or `revised` state
- No mechanism for linking a new DI-XXX to an older one it replaces
- No control flow for "DI-003 turned out to be wrong based on DI-017"

This matters because KNOWLEDGE.md feeds into specs and designs. If an insight is wrong, downstream artifacts may be silently based on bad information.

### Problem B: Model-to-knowledge traceability is not formalized in the architecture

The architecture describes traceability *aspirationally* but doesn't formalize it as a structural concern. Currently:

**What exists** (scattered across commands, not in the architecture doc):
- Doc comments with `Source`, `Reference`, `Last Updated` fields — prescribed by commands, partially enforced by Level 6 validation
- `data/traceability_matrix.csv` — maps model elements to source documents with confidence levels
- `/audit-models` manually extracts parameters and compares to baseline sources
- SOURCE_INDEX.md registers authority sources

**What the architecture doc says about it**: Almost nothing. The Document Relationship Map (Section 3.3) shows information flowing *down* from knowledge to models, but:
- No entity or data model for the traceability links themselves
- No description of how model elements reference DI-XXX insights or MR-XXX requirements
- `traceability_matrix.csv` exists in the project templates but isn't mentioned anywhere in the architecture
- Level 6 validation only checks that doc comments *exist* — it doesn't verify they *cite sources* or that cited sources are *valid*
- The architecture defines the information roles (what DI-XXX looks like, what MR-XXX looks like) but not the *links between them and model elements*

The traceability chain actually has four hops, and only the first two are structurally defined:

```
DI-XXX (domain insight)
   |
   | "Derived requirements" field in KNOWLEDGE.md
   v
MR-XXX (per-feature requirement in spec.md)
   |
   | ??? (not structurally defined — lives in doc comments as prose)
   v
Model element (part def, calc def, constraint)
   |
   | Source/Reference fields in doc comment
   v
Authority source (file:line in PyFECONS, section in spec doc)
```

Hop 1 (DI -> MR): KNOWLEDGE.md's `Derived requirements` field references MR-XXX IDs. This is defined.
Hop 2 (MR -> model): **Not structurally defined.** The spec.md lists MR-XXX requirements, and the model is supposed to satisfy them, but nothing in the architecture says how the link is recorded or verified.
Hop 3 (model -> source): Doc comment conventions exist in commands/templates but aren't part of the architecture. `traceability_matrix.csv` partially covers this but isn't connected to the information architecture.

### Problem C: No impact propagation when knowledge changes

When a DI-XXX insight is superseded, the system has no way to answer: "what model elements depend on this insight and need review?"

The query path would be:
1. DI-003 is superseded by DI-017
2. DI-003's `Derived requirements` field says MR-005, MR-012
3. MR-005 and MR-012 are in `active/magnet-model/spec.md`
4. Which model elements satisfy MR-005 and MR-012?
5. Those elements need review

Steps 1-3 are answerable if the data model is complete. Step 4 requires a formalized link from MR-XXX to model elements — which doesn't exist (Problem B).

### Proposed Architecture Changes

#### Change 1: Add traceability as a cross-cutting concern in the architecture doc

Traceability is not an information role — it's the *connective tissue between roles*. The architecture should define the link types, not just the roles.

**Add to Section 3 (after the Document Relationship Map) a new subsection: "3.4 Traceability Model"**

```
### 3.4 Traceability Model

The information roles defined above are connected by explicit, typed links.
These links are the primary mechanism for impact analysis when knowledge evolves.

#### Link Types

| Link | From | To | Recorded in | Verified by |
|------|------|----|-------------|-------------|
| **derives** | DI-XXX (insight) | MR-XXX (requirement) | KNOWLEDGE.md `Derived requirements` field | /status (coverage check) |
| **satisfies** | Model element | MR-XXX (requirement) | traceability_matrix.csv `Requirement` column | /audit-models (completeness check) |
| **sources** | Model element | Authority source | Doc comment `Source`/`Reference` fields | Level 6 validation (existence + format) |
| **traces-to** | MR-XXX (requirement) | G-XXX (goal) or AQ-XXX (question) | spec.md traceability section | /status (goal coverage) |
| **justifies** | AD-XXX (decision) | Model structure | ARCHITECTURE.md `Rationale` field | /audit-models (adherence check) |
| **supersedes** | DI-XXX (new) | DI-XXX (old) | KNOWLEDGE.md `Superseded-by` field | approval script (automatic) |

#### The Traceability Matrix

`data/traceability_matrix.csv` is the authoritative record of model-element-level traceability.
It maps each significant model element to its justifying requirements and authority sources.

Schema:

| Column | Description | Example |
|--------|-------------|---------|
| Element | Model element name | `MagnetSystemCostCalc` |
| File | SysML file path | `models/library/calculations/magnet_cost.sysml` |
| Type | Element kind | `calc def` |
| Requirements | MR-XXX IDs this element satisfies | `MR-005, MR-012` |
| Source_Type | Authority source kind | `codebase` |
| Source_Document | Authority source name | `PyFECONS` |
| Source_Location | Specific location | `CAS220103/magnet_cost.py:94` |
| Confidence | Assessment | `High` |
| Assumptions | Known approximations | `Uses 2024 material costs` |
| Last_Verified | Date of last audit | `2026-01-28` |

**Key addition vs. current template**: The `Requirements` column. This is what makes
hop 2 (MR -> model element) queryable.

**Ownership**: Tool-owned schema (columns), user-owned data (rows).
**Populated by**: `/implement-model` calls `agentic-mbse pm trace-element` (AP-7 T1 script)
  to append rows. Agent supplies content (element, file, requirements, source); script
  enforces schema, prevents duplicates, validates MR-XXX IDs against spec.md.
**Requirements identified by**: `/spec-model` — spec.md lists MR-XXX requirements and
  names which model elements (existing or planned) must satisfy them.
**Verified by**: `/audit-models` (checks completeness against spec.md MR-XXX list).
  Future: `agentic-mbse validate` traceability level (parses SysML via syside, checks
  all definitions have traceability entries).
**Queried by**: PM script engine (impact analysis).
```

#### Change 2: Formalize knowledge supersession in the DI-XXX data model

**Modify Role 2 entity format in Section 3.3**:

```markdown
### DI-XXX: [Title]
- **Source**: [approved research doc, user note, or authority source]
- **Context**: [1-3 sentences: the domain fact and why it matters]
- **Model implications**: [what the models must capture because of this insight]
- **Analysis implications**: [what analyses this enables or requires]
- **Derived requirements**: [MR-XXX IDs, if specs have been written; "pending" otherwise]
- **Status**: captured | requirements-derived | addressed | superseded
- **Superseded-by**: [DI-XXX ID, only when status = superseded]
- **Supersedes**: [DI-XXX ID, when this insight replaces an earlier one]
```

#### Change 3: Define the knowledge evolution control flow

**Add to Section 7.1 (Research Split) or new Section 7.3: "Knowledge Evolution Flow"**

```
#### Knowledge Supersession Flow

When new research contradicts or refines an existing domain insight:

User runs /research (or discovers contradiction during any command)
        |
        v
Agent identifies conflict with existing DI-XXX
Presents: "DI-003 states [X]. New findings suggest [Y]. Supersede?"
        |
        v
+-------------------------------------------------+
| USER DECISION POINT                             |
|                                                 |
| "Supersede DI-003"  -> proceed                  |
| "Keep both"         -> new DI with no link      |
| "Revise DI-003"     -> update in place (rare)   |
+-------------------------------------------------+
        |
        v
Agent calls: agentic-mbse pm supersede-insight DI-003
  --new-insight '<structured JSON for DI-017>'
  --reason 'New research on HTS vs LTS cost structures'
        |
        v
+-------------------------------------------------+
| SCRIPT EXECUTION (AP-7, Tier 2)                 |
|                                                 |
| 1. Assign DI-017 ID                            |
| 2. Add DI-017 entry with Supersedes: DI-003    |
| 3. Update DI-003: Status = superseded,          |
|    Superseded-by = DI-017                       |
| 4. Query: what MR-XXX referenced DI-003?        |
|    (from DI-003's Derived requirements field)   |
| 5. Query: what model elements satisfy those      |
|    MR-XXX? (from traceability_matrix.csv)       |
| 6. Produce IMPACT REPORT:                       |
|    - Affected requirements: MR-005, MR-012      |
|    - Affected model elements: MagnetCostCalc,   |
|      TFCoilDefinition (with file paths)         |
|    - Affected work items: magnet-model (active)  |
| 7. Write impact report to                       |
|    knowledge/research/impacts/DI-003_superseded.md         |
+-------------------------------------------------+
        |
        v
Agent presents impact report to user:
"DI-003 superseded. 2 requirements and 3 model elements affected.
 Recommend: create a Fix work item for magnet-model to update
 cost structure assumptions."
        |
        v
+-------------------------------------------------+
| USER DECISION POINT                             |
|                                                 |
| "Create fix item"  -> /backlog add (Fix intent) |
| "Review later"     -> impact report in pending  |
| "No action needed" -> close (user judgment)     |
+-------------------------------------------------+
```

#### Change 4: Add impact analysis to the PM script engine

**Extend Section 6.2 (PM Script Engine: Data Model)**:

Add new operations to the AP-7 operations table:

| Operation | Tier | What the script does |
|-----------|------|---------------------|
| Trace element | T1 | Append row to `traceability_matrix.csv`. Validates schema, prevents duplicates, checks MR-XXX IDs exist in spec.md. Called by `/implement-model` as elements are created. |
| Supersede insight | T2 | Mark old DI-XXX as superseded, create new DI-XXX, query derived requirements + traceability matrix, produce impact report |
| Impact query | T1 | Given a DI-XXX or MR-XXX, traverse links to find all affected model elements and work items |

**Impact query** is the key primitive. It's a graph traversal:
```
DI-XXX -> [Derived requirements] -> MR-XXX
  -> [traceability_matrix.csv Requirements column] -> model elements
  -> [work/active/ directory] -> affected work items
```

This is fully deterministic (AP-4) — it parses structured files and follows ID references. No LLM needed.

#### Change 5: Traceability validation as an architectural requirement

**Architectural requirement**: The validation pyramid must include programmatic traceability checking. This is not optional — it's the enforcement mechanism that makes the traceability model reliable.

Level 6 validation (`level6_traceability.py`) currently only checks doc comment *existence*. It must be extended with the following sub-checks:

1. **Format check**: Doc comments on definitions contain `Source` and `Reference` fields
2. **Resolvability check**: Referenced source documents exist in SOURCE_INDEX.md
3. **Completeness check**: `traceability_matrix.csv` has an entry for each definition (parsed via syside adapter)
4. **Requirement coverage check**: Every MR-XXX in the work item's spec.md has at least one satisfying element in `traceability_matrix.csv`

Sub-checks 1-3 extend Level 6. Sub-check 4 is a cross-file check that may belong in Level 7 (architectural integrity) or as a standalone `agentic-mbse validate --traceability` flag.

**Architecture doc impact**: Add to Section 3.4 (Traceability Model): "Traceability links are verified programmatically by the validation pyramid. Level 6 validates element-level traceability (doc comments, matrix completeness). Requirement coverage is validated as part of architectural integrity checks."

**Implementation**: Phase 3E. The syside adapter already parses SysML files and can enumerate definitions. The new check compares that list against `traceability_matrix.csv` entries.

#### Change 6: Update Document Relationship Map

**Modify the diagram in Section 3.3** to show traceability links as bidirectional:

```
KNOWLEDGE.md                        spec.md (per work item)
  DI-XXX ----derives----->  MR-XXX
                             |
                             | satisfies (traced in traceability_matrix.csv)
                             v
                        Model elements ----sources----> Authority sources
                         (models/)                      (SOURCE_INDEX.md)
                             |
                             | verified against
                             v
                        VALIDATION_MATRIX.md
                          SV-XXX criteria
```

And add reverse arrows showing the impact propagation path:

```
DI-XXX superseded
  |
  | impact query (script)
  v
MR-XXX affected
  |
  | traceability_matrix.csv lookup
  v
Model elements needing review
  |
  | work item lookup (work/active/ directory)
  v
Impact report -> user decides on action
```

### Summary of architecture doc changes

| Section | Change |
|---------|--------|
| 3.3 (after Document Relationship Map) | **New subsection 3.4**: Traceability Model — link types, traceability matrix schema, validation requirements |
| 3.3 Role 2 entity format | Add `superseded` status, `Superseded-by` and `Supersedes` fields |
| 3.3 Document Relationship Map | Add traceability links as bidirectional arrows |
| 3.4 (new) | State architectural requirement: programmatic traceability checking in validation pyramid |
| 6.2 PM Script Engine | Add `trace-element`, `supersede-insight`, and `impact-query` operations |
| 7.1 or new 7.3 | Add Knowledge Evolution Flow (supersession control flow) |
| AP-7 Operations table (Section 2) | Add `Trace element` (T1), `Supersede insight` (T2), and `Impact query` (T1) |

### Resolved decisions

1. **Traceability matrix format**: **CSV**. Easier to parse programmatically. The PM script engine can generate a markdown view for the `/status` dashboard if needed, but CSV is the source of truth.

2. **Granularity of the `satisfies` link**: **Element-level** (every `def` gets an entry). Start here; if it proves too verbose in practice, introduce a threshold later (e.g., usages inherit from their def). This is a tuning knob, not an architectural decision — the schema supports either granularity.

3. **Traceability maintenance flow**: Two-stage, split across commands per AP-7:
   - **`/spec-model` identifies the requirements**: spec.md lists MR-XXX requirements and names which model elements (existing or planned) must satisfy them. This is the *what* — the agent generates it, the user approves it.
   - **`/implement-model` records the links using a script**: As the agent creates model elements, it calls an AP-7 script (e.g., `agentic-mbse pm trace-element`) to append rows to `traceability_matrix.csv`. The script enforces schema, prevents duplicates, and validates that referenced MR-XXX IDs exist in the work item's spec.md. The agent supplies the content (element name, file path, which MR-XXX it satisfies, source citation); the script handles the structured mutation.

4. **Detecting missing traceability**: Two levels:
   - **Near-term (command-level)**: `/audit-models` checks spec.md's MR-XXX list against `traceability_matrix.csv` entries. Any MR-XXX without a satisfying element is flagged. This is a straightforward set-difference operation.
   - **Future (validation-level)**: Extend `agentic-mbse validate` with a traceability validation level that parses SysML files (via syside adapter) to find all definitions, then checks each against `traceability_matrix.csv`. Definitions without entries are flagged. **This is an architectural requirement**: the architecture doc should state that programmatic traceability checking is a required capability of the validation pyramid, to be implemented as a validation level or sub-level.

5. **Impact report persistence**: **Persist** to `knowledge/research/impacts/`. The impact report is evidence of why a work item was created and enables later review of how knowledge evolution affected the project.

### Remaining open questions

1. **Traceability validation level number**: Should this be a sub-level of Level 6 (traceability & documentation) or a new level? Level 6 currently checks doc comment existence; adding traceability matrix completeness and source resolvability is a natural extension. Recommend: extend Level 6 with sub-checks rather than adding a new level. Resolve during Phase 3E.

2. **`trace-element` script interface**: Exact CLI arguments and behavior for the AP-7 script that `/implement-model` calls. Resolve during Phase 3E when implementing the PM script engine.

---

## B-003: Delete intent dimension; simplify work item taxonomy

**Severity**: Medium
**Resolve before**: Phase 1A
**Status**: Approved
**Supersedes**: Original B-003 ("Undefined intent x scale combinations") and architecture doc Section 5.2 (Intent Dimension), Q6, Q7, Q8

### The Problem (original)

The architecture defines a 5-intent x 4-scale matrix (20 combinations) for work item routing. Analysis against AP-3 (behavior-justified taxonomy) reveals that most intents do not change downstream behavior in any architectural sense:

| Intent | Claimed difference | Actual architectural impact |
|--------|-------------------|---------------------------|
| **Model** | Full pipeline | Default — baseline, not a category |
| **Fix** | Skips design/plan, lightweight spec | User can skip stages manually. Spec difference is a prompt variation. No data model or control flow change. |
| **Investigate** | Research-first, may not produce artifacts | Genuinely different entry point and lifecycle. |
| **Refactor** | Preservation-focused spec, skips design | Prompt variation in spec-model. Architecturally identical to Model with stages skipped. |
| **Integrate** | Interface-focused design | Prompt guidance for design-model. No structural difference. |

Only **Investigate** changes something the architecture must know about: different entry point (`/research` or `/analyze-models`), different lifecycle (may terminate without model artifacts), different output destination.

But if only one intent is architecturally distinct, it's not a "category in a taxonomy" — it's a **different command**. The intent dimension should be deleted.

### Decision: Delete the intent dimension

**Remove from the architecture**:
- Section 5.2 (Intent Dimension) — delete entirely
- Section 5.4 (Work Item Routing) — remove intent determination step
- Open questions Q6, Q7, Q8 — resolved by deletion
- BACKLOG.md intent column — remove
- The 5x4 matrix — gone

**What remains**: Work items have a **scale** only: Trivial, Standard, or Epic (3 values, reduced from 4 — Small is absorbed into Standard, as the agent naturally adjusts depth).

| Scale | Behavior | Entry point | Architectural difference |
|-------|----------|-------------|------------------------|
| **Trivial** | No spec/design/plan. Direct change + validate. | `/quick-model` | Different command. No work item directory. PM doesn't track. |
| **Standard** | Full pipeline: spec -> design -> plan -> implement -> audit. Agent adjusts depth naturally. | `/spec-model` | Default pipeline. Work item in `active/`. |
| **Epic** | Must decompose into sub-items before entering pipeline. | `/backlog decompose` -> sub-items | Different control flow. Parent-child tracking in PM. |

**What happens to Fix/Refactor/Integrate guidance**: This is prompt-level concern, not architecture. The `/spec-model` command can internally ask "what kind of change is this?" and adjust its questions accordingly — but that's a command design decision (Phase 3D), not an information architecture or control flow concern.

### Decision: Investigate becomes two distinct commands

The "investigate" concept actually covers two different activities that the architecture already distinguishes:

| Activity | Command | Reads | Produces | Output destination |
|----------|---------|-------|----------|--------------------|
| **External research** | `/research` | `knowledge/SOURCE_INDEX.md`, authority sources, raw external data | Domain insights (DI-XXX) | `knowledge/research/pending/` -> `knowledge/research/approved/` -> `knowledge/KNOWLEDGE.md` |
| **Model analysis** | `/analyze-models` | Existing models, approved `knowledge/KNOWLEDGE.md`, `project/ARCHITECTURE.md`, `project/REQUIREMENTS.md` | Understanding of current model state: what exists, patterns in use, gaps, health | `work/analysis/` (standalone artifact, NOT tied to a work item) |

These are fundamentally different:
- `/research` builds **domain knowledge** (Role 2) — "what does the physics say?"
- `/analyze-models` builds **model understanding** — "what have we built so far and what state is it in?"

**Critical**: Their outputs must NOT go to the same place. Research produces curated domain insights (KNOWLEDGE.md). Analysis produces model state assessments that inform future specs but are not domain knowledge.

`/analyze-models` output lives in `work/analysis/` as standalone artifacts (timestamped, like research: `YYYYMMDD-HHMMSS_topic.md`). These are **not** associated with a specific work item — they're project-level understanding that any future spec can reference.

### Architecture doc changes

| Section | Change |
|---------|--------|
| 5.1-5.2 | Delete intent dimension. Section 5 becomes "Work Item Scale" only. |
| 5.3 | Renumber. Three scales: Trivial, Standard, Epic. |
| 5.4 | Simplify routing: determine scale only, no intent step. |
| 7.2 | Expand `/analyze-models` description: standalone artifacts in `work/analysis/`, distinct from `/research`. |
| 8.1 | Remove intent column from command catalog. Update `/analyze-models` entry. |
| 3.2 | Add `work/analysis/` to file structure. |
| Open questions | Delete Q6, Q7, Q8. |

### Relationship to B-012

The output destinations for `/research` and `/analyze-models` connect to B-012 (file structure should reflect information flow). **Resolved by B-012**: Research output moves to `knowledge/research/`, KNOWLEDGE.md moves to `knowledge/KNOWLEDGE.md`. Analysis output goes to `work/analysis/` (operational intelligence about model state).

---

## B-004: Downstream pipeline is invisible

**Severity**: Medium-High
**Resolve before**: Phase 1A
**Status**: New

### The Problem

The architecture treats `models/` as the terminal output. But the real pipeline is:

```
models/ -> sysml-codegen -> teax -> analysis results -> (feedback)
```

This creates gaps:

1. **Validation Level 8** is "code generation readiness" but there's no feedback path from sysml-codegen failures back to the modeling workflow
2. **VALIDATION_MATRIX.md** verification types (reasonableness, baseline, physical, relationship, rollup) have no `codegen` or `simulation` type
3. No mechanism for a sysml-codegen error to create a Fix work item in the backlog
4. No mechanism for simulation results (teax) to feed back as verification evidence

The models aren't the end product — executable simulations and analysis results are. The architecture should at minimum acknowledge this boundary and define what information flows back.

### Recommendation

1. Add verification type `codegen` to VALIDATION_MATRIX.md types table (Section 3.3, Role 6)
2. Add verification type `simulation` for teax results
3. Define a feedback path in the Document Relationship Map (Section 3.3): sysml-codegen/teax errors -> VALIDATION_MATRIX entry -> work item in backlog
4. This doesn't require building the integration now, but the architecture should have the slots for it

### Architecture doc impact

Section 3.3 Role 6: add `codegen` and `simulation` verification types.
Section 3.3 Document Relationship Map: extend beyond Model Artifacts to show downstream tools.
Section 2: consider whether this warrants a new principle or falls under AP-1 (design for N).

---

## B-005: Markdown parsing as state store is fragile

**Severity**: Medium
**Resolve before**: Phase 1A
**Status**: New

### The Problem

The PM script engine (Section 6.2) derives all state from parsing markdown tables. This is elegant but brittle:

- Markdown tables break easily (user adds a column, extra space misaligns pipes, prose between table rows)
- No schema validation is described — the script either parses correctly or silently produces wrong data
- No error recovery: what does `agentic-mbse status` do when BACKLOG.md has a malformed row?
- Agent-edited markdown may drift from expected format over time

AP-4 says "deterministic state" but markdown parsing is only deterministic if the input is well-formed.

### Recommendation

The PM script engine should include a `validate-structure` check that runs before any state query:

1. Define a schema for each structured file (required columns, valid values per column, row format)
2. `agentic-mbse status` validates structure first, reports malformed files before producing dashboard
3. AP-7 scripts validate the structure of files they **read** (not just files they write)
4. Consider whether YAML frontmatter in markdown files would be more robust for machine-parsed fields (human-readable body, machine-parsed header)

### Architecture doc impact

Section 6.2: add schema validation as a requirement for the PM script engine.
AP-7: extend the "script guarantees" to include input validation, not just output correctness.

---

## B-006: No decision promotion path

**Severity**: Low
**Resolve before**: Phase 3D
**Status**: New

### The Problem

The architecture defines promotion for Rules (per-feature pattern -> REQUIREMENTS.md via Q4). But there's no equivalent for Decisions.

When writing `work/active/{item}/design.md`, an engineer makes structural decisions. Some turn out to be reusable across work items. The architecture says ARCHITECTURE.md captures "decisions that outlive any single work item" — but that's only knowable in retrospect. There's no mechanism for:

- Detecting that design.md decisions recur across work items
- Promoting a design.md decision to ARCHITECTURE.md
- `/audit-models` flagging "this pattern appears in 3 work items but isn't in ARCHITECTURE.md"

This is the same class of problem as Rule promotion (Q4) but for structural decisions rather than methodology rules.

### Recommendation

Define a promotion path parallel to Rule promotion:
1. During `/audit-models`, check for recurring structural patterns across completed work items
2. Suggest promotion to ARCHITECTURE.md when a pattern appears in 3+ work items
3. Use the same approval flow (agent suggests, user approves, script registers)

Can defer to Phase 3D since it requires `/audit-models` to exist.

---

## B-007: /review-model vs /audit-models boundary

**Severity**: Low
**Resolve before**: Phase 3D
**Status**: New

### The Problem

Both commands verify correctness. The catalog (Section 8.1) implies the distinction is temporal:
- `/review-model`: before implementing (design review)
- `/audit-models`: after implementing (verification)

But their skill sets overlap heavily (both reference sysml-conventions, model-validation, project-structure). The architecture doesn't define:
- What specifically `/review-model` checks that `/audit-models` doesn't (and vice versa)
- Whether `/review-model` is a gate (blocks progression to implement) or advisory
- How their outputs differ structurally

### Recommendation

Define during Phase 3D command design:
- `/review-model` = **pre-implementation gate**: checks design.md against REQUIREMENTS.md and ARCHITECTURE.md, validates prototype, produces pass/concerns/fail verdict. Focuses on "will this design work?"
- `/audit-models` = **post-implementation verification**: checks model artifacts against spec requirements (MR-XXX), runs validation pyramid, checks source traceability. Focuses on "did we build it right?"
- Make the distinction explicit in Section 8.1 with separate "checks" columns

---

## B-008: No inline knowledge capture during non-research commands

**Severity**: Low-Medium
**Resolve before**: Phase 3D
**Status**: New

### The Problem

During any command — spec, design, implement — the agent may discover domain knowledge that doesn't fit the current work item. Example: "While implementing the magnet model, I realized HTS and LTS have fundamentally different cost structures — this should be a domain insight."

The only structured entry point for KNOWLEDGE.md is `/research` -> approval flow. The architecture mentions `/spec-model` "can suggest adding insights" but doesn't define the control flow. Specifically:

- Does the agent pause the current command, invoke the research approval script, then resume?
- Does it queue insights for later capture?
- Is there a lightweight inline path that skips the full research flow?

### Recommendation

Define a lightweight capture path:
1. During any command, the agent can propose a DI-XXX candidate
2. User approves inline (no separate research doc needed — the work item context IS the source)
3. Agent calls `agentic-mbse pm add-insight --source work/active/{item}/design.md --context "..."` (AP-7 T2)
4. Script assigns ID, appends to KNOWLEDGE.md with source = the work item artifact

This is a simpler variant of the research approval flow — same script, different trigger.

---

## B-009: SOURCE_INDEX.md placement inconsistent

**Severity**: Low
**Resolve before**: Phase 1A
**Status**: Closed

### The Problem

`SOURCE_INDEX.md` lives at project root. Every other PM-related artifact lives in `modeling_pm/`. The architecture doesn't explain this inconsistency.

### Recommendation

Either:
- (a) Move to `modeling_pm/SOURCE_INDEX.md` for consistency, update all references
- (b) Keep at root and document the rationale explicitly (e.g., "SOURCE_INDEX.md is the most frequently referenced file and benefits from top-level visibility, similar to README.md")

If (b), add a note in Section 3.2 explaining the exception.

---

## B-010: No migration strategy for existing projects

**Severity**: Medium-High
**Resolve before**: Phase 3E
**Status**: New

### The Problem

The architecture introduces new structural conventions:
- BACKLOG.md gets new columns (intent, scale)
- OVERVIEW.md gets new sections (Goals Registry, Analysis Questions)
- New files appear (KNOWLEDGE.md, REQUIREMENTS.md, ARCHITECTURE.md, VALIDATION_MATRIX.md)

What happens to fusion-tea (the real validation case) when these changes ship? The architecture defines user-owned vs tool-owned, and `--force` for overwrites. But it doesn't address **structural migration**: updating an existing BACKLOG.md to add columns while preserving existing rows.

### Scenarios that need handling

1. **New tool-owned files**: Easy — `init --update` creates them. No conflict.
2. **New user-owned files**: Easy — `init` creates templates, user fills them in. No conflict.
3. **Modified tool-owned files**: Easy — `init --update` overwrites. No conflict.
4. **Modified user-owned file structure**: Hard — BACKLOG.md has existing rows but needs new columns. `init` skips user-owned files; `--force` would destroy existing content.

### Recommendation

Add a migration concept to the architecture:
1. `agentic-mbse init --update` should detect version mismatches (current vs. installed)
2. For structural changes to user-owned files, provide a `migrate` subcommand that adds new columns/sections while preserving existing data
3. Define migration as an AP-7 T1 operation (deterministic file transformation, no content generation)

---

## B-011: AP-7 Tier 2 claude -p dependency

**Severity**: Medium
**Resolve before**: Phase 3E
**Status**: New

### The Problem

Tier 2 scripts call `claude -p` for content generation. This creates a hard dependency on Claude CLI availability:

- CI/CD environments may not have Claude CLI
- Testing requires either mocking the LLM call or fixture-based approaches
- Cost implications of LLM calls during automated operations
- Failure modes: what happens when `claude -p` fails (rate limit, network, auth)?

### Recommendation

Define the Tier 2 contract:
1. **Content generation is optional**: The script must succeed (file moves, ID assignment, format enforcement) even if content generation fails. Missing content gets a placeholder ("Summary pending — run `agentic-mbse pm regenerate DI-XXX`").
2. **Testability**: Tier 2 scripts accept a `--dry-run` flag (shows what would change) and a `--no-llm` flag (skips content generation, uses placeholders).
3. **Mockability**: The LLM call is isolated behind a function that tests can stub.

### Architecture doc impact

Section 2, AP-7 Implementation Tiers: add failure mode and testability requirements for Tier 2.

---

## B-012: File structure should reflect information flow model

**Severity**: High
**Resolve before**: Phase 1A
**Status**: Complete
**Related**: B-003 (research vs. analysis output destinations), B-009 (SOURCE_INDEX.md placement)

### The Problem

The current file structure (architecture doc Section 3.2) groups things by administrative convenience, not by information role. Several artifacts are under `modeling_pm/` that don't belong there:

| Artifact | Current location | Information role | Problem |
|----------|-----------------|-----------------|---------|
| `research/pending/`, `research/approved/` | `modeling_pm/research/` | Role 2: Domain Knowledge | Research is knowledge building, not project management |
| `KNOWLEDGE.md` | `modeling_pm/KNOWLEDGE.md` | Role 2: Domain Knowledge | Curated knowledge is not PM |
| `intent/` | `modeling_pm/intent/` | Role 3: Project Intent | Raw intent documents define the project's purpose, not its management |
| `SOURCE_INDEX.md` | project root | Role 1: Authority Sources | Inconsistent with other role artifacts (B-009) |
| `ARCHITECTURE.md` | `modeling_pm/ARCHITECTURE.md` | Role 5: Modeling Decisions | Project-defining, not work-tracking |
| `REQUIREMENTS.md` | `modeling_pm/REQUIREMENTS.md` | Role 4: Modeling Requirements | Project-defining, not work-tracking |
| `VALIDATION_MATRIX.md` | `modeling_pm/VALIDATION_MATRIX.md` | Role 6: System Verification | Defines "done," doesn't manage progress |

`modeling_pm/` conflated two concerns: **project definition** (what we're building and how) and **work management** (tracking execution). These must be separated because they have different producers, consumers, and lifecycles.

The information flow model (Section 3.1) has a clear structure:

```
knowledge/ (what we know)  ──→  project/ (standards)  ──→  work/ (execution)  ──→  models/ (artifacts)
     ↑                                                          │
     └──────────────────────── feedback ────────────────────────┘
```

Each directory is a stage in the information flow. The file structure should mirror this flow.

### Decision: Four top-level content directories

The organizing principle: each directory answers a different question.

| Directory | Question it answers | Information roles |
|-----------|-------------------|-------------------|
| `knowledge/` | "What do we know?" | Roles 1-2: Authority Sources, Domain Knowledge |
| `project/` | "What are we building and how?" | Roles 3-6: Intent, Requirements, Decisions, Verification |
| `work/` | "What's in progress?" | Work management: backlog, active, completed |
| `models/` | "The models themselves" | Model artifacts |

### Approved file structure

```
project-root/
├── .claude/                     # Tooling (unchanged)
│   ├── commands/
│   ├── skills/
│   └── agents/
│
├── knowledge/                   # "What do we know?"
│   ├── SOURCE_INDEX.md          #   Role 1: Authority sources registry
│   ├── KNOWLEDGE.md             #   Role 2: Curated domain insights (DI-XXX)
│   ├── sources/                 #   Local reference materials (PDFs, data tables)
│   │   └── ...                  #   External repos stay external, referenced by path
│   └── research/                #   Research pipeline
│       ├── pending/             #     Unapproved research
│       └── approved/            #     User-approved research
│
├── project/                     # "What are we building and how?"
│   ├── OVERVIEW.md              #   Role 3: Goals (G-XXX), questions (AQ-XXX), scope
│   ├── ARCHITECTURE.md          #   Role 5: Structural decisions (AD-XXX)
│   ├── REQUIREMENTS.md          #   Role 4: Project-specific rules (PR-XXX)
│   ├── VALIDATION_MATRIX.md     #   Role 6: Verification criteria (SV-XXX)
│   ├── MODELING_GUIDE.md        #   Role 4 baseline (tool-owned)
│   ├── MODELING_PROCESS.md      #   Workflow reference (tool-owned)
│   └── intent/                  #   Raw user documents (charters, notes, etc.)
│       └── *.md
│
├── work/                        # "What's in progress?"
│   ├── BACKLOG.md               #   Prioritized items with scale
│   ├── EPIC_GUIDE.md            #   Decomposition guide (tool-owned)
│   ├── active/                  #   In-progress work items
│   │   └── {item}/
│   │       ├── spec.md
│   │       ├── design.md
│   │       └── plan.md
│   ├── completed/               #   Archived work
│   │   └── YYYYMMDD_{item}/
│   ├── analysis/                #   /analyze-models output (operational intelligence)
│   │   └── YYYYMMDD-HHMMSS_topic.md
│   └── learnings/
│       └── RAW_LEARNINGS.md
│
├── models/                      # Model artifacts
│   ├── library/
│   └── designs/
│
├── tests/
│   └── models/
│
├── data/                        # Machine-readable evidence
│   └── traceability_matrix.csv
│
├── CLAUDE.md
└── README.md
```

### Key structural decisions

1. **`knowledge/`** is the home for Roles 1-2. SOURCE_INDEX.md moves here (resolves B-009). Research output moves here. KNOWLEDGE.md moves here. The `sources/` subdirectory provides a conventional place for project-local reference materials (PDFs, excerpts, data tables). External repos (like PyFECONS) stay external and are referenced by path in SOURCE_INDEX.md.

2. **`project/`** groups the project's "constitution" — Roles 3-6 together. OVERVIEW.md (formalized intent) sits next to ARCHITECTURE.md and REQUIREMENTS.md because they derive from intent and are always consumed together when starting new work. Raw intent documents nest in `project/intent/` — they're the source material from which OVERVIEW.md was formalized, preserving the derivation relationship. MODELING_GUIDE.md and MODELING_PROCESS.md are methodology references that constrain how work is done, not work-tracking artifacts.

3. **`work/`** is purely operational — tracking and executing work. BACKLOG.md flattened (no `backlog/` subdirectory — one file doesn't need a wrapper). EPIC_GUIDE.md stays here because it's about *how to decompose work*, not modeling standards. `analysis/` stays here because `/analyze-models` output is operational intelligence (what state are the models in, what work should we do next).

4. **`data/`** at project root for machine-readable evidence (traceability_matrix.csv). Grows naturally if codegen/simulation artifacts land here (B-004 feedback path).

5. **Naming: `project/` not `modeling_pm/`**. In target repos (Context B), there is no `.project/` directory, so no conflict. The name clearly communicates "this is what defines this project." `work/` replaces `modeling_pm/` for the operational subset — shorter, clearer, and doesn't redundantly say "modeling" when all PM in a target repo is modeling PM.

### Why Roles 4-5-6 moved out of PM

The original B-012 proposal kept ARCHITECTURE.md, REQUIREMENTS.md, and VALIDATION_MATRIX.md in `modeling_pm/` with an open question about whether this was right. The answer is: **these are project-defining, not project-managing.**

| Document | What it is | Why it's not PM |
|----------|-----------|-----------------|
| ARCHITECTURE.md | Structural decisions about the domain model | Consumed when designing, not when tracking work |
| REQUIREMENTS.md | Project-specific modeling rules | Constrains all work, doesn't track any work |
| VALIDATION_MATRIX.md | Success criteria for the system | Defines "done," doesn't manage progress toward it |
| MODELING_GUIDE.md | Baseline methodology rules | Reference material, not work state |
| MODELING_PROCESS.md | Workflow reference | Describes how to work, not what's being worked on |

These derive from intent + knowledge and *constrain* work execution. Grouping them with OVERVIEW.md in `project/` means one sweep of that directory gives the agent (or user) the full project definition — goals, standards, decisions, success criteria.

### Subsumes B-009

B-009 (SOURCE_INDEX.md placement inconsistent) is resolved: SOURCE_INDEX.md moves to `knowledge/SOURCE_INDEX.md`.

### Architecture doc impact

| Section | Change |
|---------|--------|
| 3.2 | Replace entire file structure diagram with approved structure |
| 3.3 Role 1 | Update paths: `knowledge/SOURCE_INDEX.md` |
| 3.3 Role 2 | Update paths: `knowledge/KNOWLEDGE.md`, `knowledge/research/` |
| 3.3 Role 3 | Update paths: `project/OVERVIEW.md`, `project/intent/*.md` |
| 3.3 Role 4 | Update paths: `project/REQUIREMENTS.md`, `project/MODELING_GUIDE.md` |
| 3.3 Role 5 | Update paths: `project/ARCHITECTURE.md` |
| 3.3 Role 6 | Update paths: `project/VALIDATION_MATRIX.md` |
| 7.1 | Update research output paths to `knowledge/research/` |
| 7.2 | Update `/analyze-models` output path to `work/analysis/` |
| All references to `modeling_pm/` | Replace with `project/` or `work/` as appropriate |

### Resolved open questions

1. **ARCHITECTURE.md and REQUIREMENTS.md placement**: Resolved — moved to `project/`. They are project-defining documents that derive from intent and constrain all work. They belong with the project definition, not with work tracking.

2. **`data/` directory scope**: Keep `data/` as the name. Currently just `traceability_matrix.csv`. If codegen/simulation artifacts land here (B-004), the name generalizes naturally.

3. **`knowledge/sources/` convention**: `sources/` is for project-local reference materials only (PDFs, excerpts, data tables). External repos stay external and are referenced by path in SOURCE_INDEX.md.

4. **`analysis/` placement**: `work/analysis/`. The output of `/analyze-models` is operational intelligence — "what state are the models in" — which informs what work to do next. It's not domain knowledge (that's `knowledge/`), it's project state assessment.

---

## References

- `.project/research/20260130-235423_information-role-taxonomy.md` — Original information role taxonomy
- `.project/concepts/unified-toolkit-architecture.md` — Current architecture doc
- `.project/research/20260130-234525_agentic-mbse-pipeline-critical-analysis.md` — Critical analysis including non-linear development
- `.project/research/20260126-161628_python-vs-mbse-command-comparison.md` — Command comparison analysis

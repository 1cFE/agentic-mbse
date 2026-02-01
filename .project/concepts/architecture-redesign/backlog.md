# Architecture Backlog

**Date**: 2026-01-31
**Status**: Active — items to resolve before finalizing unified-toolkit-architecture.md

---

## Index

| ID | Title | Severity | Resolve before | Status |
|----|-------|----------|----------------|--------|
| B-001 | [Model Implementation as a first-class concern](#b-001-model-implementation-as-a-first-class-concern) | High | Phase 1A | Complete |
| B-002 | [Knowledge evolution and traceability are incomplete](#b-002-knowledge-evolution-and-traceability-are-incomplete) | High | Phase 1A | Complete |
| B-003 | [Delete intent dimension; simplify work item taxonomy](#b-003-delete-intent-dimension-simplify-work-item-taxonomy) | Medium | Phase 1A | Complete |
| B-004 | [Downstream pipeline is invisible](#b-004-downstream-pipeline-is-invisible) | Medium-High | Phase 1A | Complete |
| B-005 | [Markdown parsing as state store is fragile](#b-005-markdown-parsing-as-state-store-is-fragile) | Medium | Phase 1A | Complete |
| B-006 | [No decision promotion path from design.md to ARCHITECTURE.md](#b-006-no-decision-promotion-path) | Low | Phase 3C | Complete |
| B-007 | [/review-model vs /audit-models boundary underspecified](#b-007-review-model-vs-audit-models-boundary) | Low | Phase 3C | Complete |
| B-008 | [No inline knowledge capture during non-research commands](#b-008-no-inline-knowledge-capture) | Low-Medium | Phase 3C | Complete |
| B-009 | [SOURCE_INDEX.md placement inconsistent](#b-009-source_indexmd-placement-inconsistent) | Low | Phase 1A | Closed |
| B-010 | [No migration strategy for existing projects](#b-010-no-migration-strategy-for-existing-projects) | Medium-High | Phase 1A | Complete |
| B-011 | [AP-7 Tier 2 claude -p dependency unaddressed](#b-011-ap-7-tier-2-claude--p-dependency) | Medium | Phase 3D | Closed |
| B-012 | [File structure should reflect information flow model](#b-012-file-structure-should-reflect-information-flow-model) | High | Phase 1A | Complete |
| B-013 | [MR-XXX → PR-XXX promotion trigger ambiguous](#b-013-mr-xxx--pr-xxx-promotion-trigger-ambiguous) | Medium | Phase 3C | Closed |
| B-014 | [Work item name resolution needs a reliable lookup mechanism](#b-014-work-item-name-resolution-needs-a-reliable-lookup-mechanism) | Medium | Phase 3D | Complete |
| B-015 | [AP-7 error model: atomic vs tolerant not distinguished](#b-015-ap-7-error-model-atomic-vs-tolerant-not-distinguished) | Low-Medium | Phase 3D | Complete |

---

## Instuctions

1. Align on conceptual intent
2. Identify architectural impacts and changes required
3. Keep status up-to-date:
  - New: gap identified
  - Approved: all changes identified and agreed on in the backlog item
  - Complete: all changes implemented in the architecture documents

---

## B-001: Model Implementation as a first-class concern

**Severity**: High
**Resolve before**: Phase 1A
**Status**: Complete — decisions made, pending integration into architecture documents

### The Problem

The architecture defines six information roles with detailed data models, control flows, and structured homes. But the *process* of creating, managing, and completing work — epics, work items, their lifecycle, feedback loops — was collapsed to scattered mentions across workflows.md and main.md. This confused the artifacts (spec.md, design.md, plan.md — ephemeral) with the process of managing them (not ephemeral at all).

B-001 raised four concerns and six open questions. Analysis grounded in fusion-tea's actual practice resolved all of them.

### Key Structural Decision: Not a New Role

Work items are **operational process**, not an information role. The `work/` directory is already in the file structure (B-012). The information architecture already covers the data (files in `work/`). What was missing is the **lifecycle** of those files — entity models, state machines, conventions, and feedback flows. This belongs in **workflows.md** as a new section, not in information-architecture.md as a new Role.

### Resolved Concerns

#### Concern 1: Epic Lifecycle — Two artifacts, two jobs

**Decision**: Epics have two artifacts: a dedicated decomposition file (`work/backlog/epic-{name}.md`) and a summary entry in `work/BACKLOG.md`. No E-XXX ID scheme. No formal state machine beyond draft/active/completed.

**Why dedicated files**: Real epic decompositions are substantial (~650 lines in fusion-tea's pipeline de-risking epic). They contain: executive summary, context, system design, success criteria, risks, and detailed per-item breakdowns with scope, deliverables, and dependencies. This is the working document where the decomposition is iterated. Trying to fit that into a BACKLOG.md section would make BACKLOG.md unreadable.

**The workflow**: Start with research/spec → realize it's too big → write epic file → iterate on decomposition → epic file has per-item requirements → move to item-by-item execution → each `/spec-model` reads the epic file for its baseline → BACKLOG.md tracks progress.

**BACKLOG.md** is the dashboard: summary entries for both epics and standalone items. Epic files provide the depth; BACKLOG.md provides the breadth.

**Epic state is derived**: draft (file exists, no items in pipeline), active (at least one sub-item active), completed (all sub-items completed).

#### Concern 2: Work Item Lifecycle — Consolidated entity model

**Decision**: Define a single authoritative work item entity model with spec.md as the state-bearing file.

**Work item entity model** — parseable metadata header in spec.md:

```yaml
---
Status: active | paused | abandoned | failed | completed
Scale: standard
Epic: [epic name, matching BACKLOG.md section header]
Owner: [who is working on this]
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
---
```

**spec.md is the authoritative state-bearing file** for each work item. It is the first artifact created and the last one relevant. The PM script engine reads `work/active/{item}/spec.md` metadata header as the single source of truth for work item state. Other files (design.md, plan.md) may have their own Status fields for stage-level tracking, but the work item's overall state comes from spec.md. This gives the dashboard a single read point per work item.

**Work item states** (consolidated):

| State | Determined by | Mechanism |
|-------|--------------|-----------|
| **backlog** | Entry in `work/BACKLOG.md`, no directory in `work/active/` | BACKLOG.md row |
| **active** | Directory exists in `work/active/{item}/`, spec.md Status = `active` | File system + header |
| **active:stage** | Which artifact files exist: spec.md only = speccing; +design.md = designing; +plan.md = planning; implementation started = implementing | File system |
| **paused** | spec.md Status = `paused` | Metadata header |
| **abandoned** | spec.md Status = `abandoned` | Metadata header |
| **failed** | spec.md Status = `failed` (work attempted, approach didn't work) | Metadata header |
| **completed** | Directory in `work/completed/YYYYMMDD_{item}/` | File system (post-archive) |

**Key**: File-system-derived state (which files exist → which stage) is sufficient for active items. The Status field in spec.md handles states that can't be inferred from file existence: paused, abandoned, failed. The PM script reads both.

#### Concern 3: Pipeline Execution — Conventions, not enforcement

**Stage completion criteria**: User-approved only. No structural gates. AP-5 (toolkit, not pipeline) says don't add friction. The agent guides quality through command prompts; the user decides when to proceed. Adding structural checks ("spec must have at least one MR-XXX") would be validation theater — the agent can't truly verify completeness, only field presence.

**Inter-stage data flow contract** (documentation of what commands already do, not enforcement):

| Stage file | Produces (for downstream) | Consumes (from upstream) |
|-----------|--------------------------|-------------------------|
| spec.md | MR-XXX requirements, success criteria, scope boundaries | G-XXX goals, DI-XXX insights, existing model state |
| design.md | Architecture approach, interface decisions, prototype validation results | MR-XXX from spec.md, AD-XXX from ARCHITECTURE.md, PR-XXX from REQUIREMENTS.md |
| plan.md | Phased implementation plan, per-phase scope, risk mitigations | Design decisions from design.md, model dependency analysis |

This table serves three purposes: (a) skills can reference it for what to load at each stage, (b) commands can be validated against it during Phase 3C, (c) the PM script engine knows what metadata to expect in each file.

**Artifact conventions** — each file has a YAML frontmatter header with at minimum:

```yaml
---
Status: [stage-specific status]
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Related Artifacts:
  Spec: ./spec.md          # (in design.md and plan.md)
  Design: ./design.md      # (in plan.md)
---
```

The body structure is defined by the command prompts (Phase 3C concern), not the architecture. The architecture only constrains the parseable header.

#### Concern 4: Feedback Loops — Hybrid close flow

**Decision**: Script handles deterministic parts (archive + BACKLOG.md update). Agent prompts for judgment parts (project document updates). This is the "both" option.

**Close flow**:

```
/status close <item>
  │
  ├─► Script (AP-7 T1): Archive work item
  │     1. Move work/active/{item}/ → work/completed/YYYYMMDD_{item}/
  │     2. Update BACKLOG.md status to completed
  │     3. Return confirmation with archive path
  │
  └─► Agent: Project document review prompt
        "This work item is archived. Before we're done,
         let's check if any project-level documents should be updated."

        Trigger questions (concrete, answerable from recent experience):
        - REQUIREMENTS.md: "Did you discover a pattern that should
          be a project-wide rule?"
        - ARCHITECTURE.md: "Did you make a structural decision that
          future work items need to know?"
        - VALIDATION_MATRIX.md: "Should any new system-level
          verification criteria be added?"
        - KNOWLEDGE.md: "Did you learn something about the domain
          that isn't captured yet?"

        For each "yes": agent helps draft the update,
        calls the appropriate AP-7 script.
```

**Project-level revisions** (4b from original): When a work item reveals a project-level issue (flawed architecture decision, infeasible goal), the system does not automate detection — this requires human judgment or agent insight. The close flow's trigger questions are the structured opportunity to surface these. For mid-work-item discoveries, the existing backward navigation (workflows.md § 2.3) handles the per-item response; project-level impact is surfaced at close time.

**Non-linear development** (4c from original): Already adequately covered by existing mechanisms:
- Quick fix escalation: `/quick-model` user recognizes complexity → creates standard work item via `/backlog add`
- Cross-item refactoring: New standard work item that references originals; archived artifacts in `work/completed/` are readable
- Undo: Create a new work item that references and corrects the original; don't reopen
- Concurrent items: Git handles file-level conflicts; not an architectural concern at this scale

#### Resumability Convention

When a paused work item resumes, the convention is:
- **Resume = re-read the existing artifact files for the current stage + the plan**
- `/status` dashboard shows paused items with their current stage
- The user picks one; the relevant command (`/design-model`, `/implement-model`, etc.) reads existing artifacts to reconstruct context
- No separate "resume" command needed — existing commands handle "artifact already exists, continue from where we left off"
- spec.md Status field is updated from `paused` back to `active` (PM script or manual)

### Resolved Open Questions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Epic data model | Two artifacts: dedicated file (`work/backlog/epic-{name}.md`) for decomposition + summary entry in BACKLOG.md for tracking. State derived from sub-items (draft/active/completed). No E-XXX IDs. | Fusion-tea's epics are ~650 lines — they need dedicated files. BACKLOG.md is the dashboard, not the decomposition workspace. |
| 2 | Work item state derivation | File-system state for active/completed/backlog. spec.md YAML frontmatter Status field for paused/abandoned/failed. spec.md is the single authoritative state-bearing file. | States that can't be inferred from file existence need an explicit field. Single read point per item keeps the PM engine simple. |
| 3 | Stage completion criteria | User-approved only. No structural gates. | AP-5 (toolkit, not pipeline). Agent guides quality; user decides progression. Structural checks are validation theater. |
| 4 | Feedback loop automation | Hybrid: script archives + agent prompts trigger-question checklist at close time. Knowledge supersession already solved (B-002). | Deterministic part (archive) = script. Judgment part (which documents need updating) = agent-prompted with concrete questions. |
| 5 | Concurrent work items | Not an architectural concern. Git handles conflicts. | Fusion-tea: ~3-5 concurrent items, no structural problems. |
| 6 | Relationship to existing sections | No new Role in information-architecture.md. Add work item lifecycle section to workflows.md between § 2 (Work Item Model) and § 3 (Project Management). | Work items are operational process, not information architecture. File structure already settled (B-012). |

### Architecture Document Changes

**In workflows.md** — new section between § 2 (Work Item Model) and § 3 (Project Management):

1. **Work item entity model** — the parseable YAML frontmatter header that spec.md must have (Status, Scale, Epic, Owner, Created, Updated), consolidated from fusion-tea's actual practice
2. **Work item states** — consolidated state table including paused/abandoned/failed with their mechanisms, spec.md as authoritative state-bearing file
3. **Stage artifacts and conventions** — what each file contains (YAML header requirements), inter-stage data flow contract table, what the PM script engine can parse
4. **Resumability convention** — paused items resume by re-reading artifacts, no special machinery
5. **Work item close flow** — archive (AP-7 T1) + feedback prompt checklist with trigger questions
6. **Epic tracking** — two artifacts: dedicated file in `work/backlog/epic-{name}.md` for decomposition, summary entry in BACKLOG.md for tracking. State derived from sub-items.

**In information-architecture.md file structure** — add `work/backlog/` subdirectory for epic decomposition files.

**In main.md AP-7 operations table** — one update:

| Operation | Tier | What the script does |
|-----------|------|---------------------|
| Close work item | T1 | Move `work/active/{item}/` → `work/completed/YYYYMMDD_{item}/`, update `work/BACKLOG.md` status. Agent handles feedback prompt separately. |

Note: "Archive work item" already exists in the AP-7 table. Rename to "Close work item" and clarify that the agent-driven feedback prompt is a separate concern (not part of the script).

**In information-architecture.md** — no changes. Work items are not a new Role. The `work/` directory description is already adequate.

### Coupling with other backlog items

- **B-002 (Knowledge evolution)**: B-002's supersession flow is a specific instance of the feedback loop pattern. The close-flow trigger question for KNOWLEDGE.md is the general case.
- **B-005 (Markdown parsing)**: The YAML frontmatter decision for spec.md metadata directly addresses B-005's concern about parseable state. B-005 should reference this as the established pattern.
- **B-012 (File structure)**: Already resolved. The `work/` directory structure is settled. B-001 defines what goes *in* those files.

### References

- `.project/research/20260130-235423_information-role-taxonomy.md` — Original Role 5: Model Implementation (Sections 5a-5d)
- `.project/concepts/unified-toolkit-architecture.md` — Current treatment (collapsed to footnotes)
- `.project/research/20260130-234525_agentic-mbse-pipeline-critical-analysis.md` — Part 4: Robustness for Non-Linear Development

---

## B-002: Knowledge evolution and traceability are incomplete

**Severity**: High
**Resolve before**: Phase 1A
**Status**: Complete — integrated into information-architecture.md § 5, workflows.md § 6, main.md AP-7 operations

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

**Fundamental problem with the four-hop chain**: It routes through ephemeral working documents (spec.md). Specs are numerous, fine-grained, and may be superseded or archived. If the traceability chain depends on spec.md being present and parseable, it breaks when work items are completed and archived. The durable traceability infrastructure must not depend on ephemeral artifacts.

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

#### Key design decision: spec.md is a working document, not a traceability link

The original analysis (Problem B) proposed a four-hop traceability chain routing through MR-XXX in spec.md. This has a fundamental problem: **specs are ephemeral working documents**. They are numerous, fine-grained, and get archived or superseded. Durable traceability must not depend on ephemeral artifacts.

**Revised approach**: The durable traceability chain uses only durable artifacts:

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

Every node in this chain is durable. spec.md is where requirements are *discovered* and promotion decisions are *made*, but it is not load-bearing for traceability.

**How this works in practice**:
- `/spec-model` writes spec.md with many fine-grained MR-XXX requirements (ephemeral)
- Some MR-XXX are significant enough to be durable — the agent or user flags these for promotion
- `/implement-model` calls the `trace-element` AP-7 script, which:
  1. Promotes flagged MR-XXX to PR-XXX in `project/REQUIREMENTS.md` (if not already there)
  2. Records the model element → PR-XXX link in `data/traceability_matrix.csv`
  3. The PR-XXX entry's `Source` column records the DI-XXX or G-XXX it derives from

**What "promotion" means**: Not all MR-XXX get promoted. Fine-grained implementation details ("use ISQ::mass for weight attributes") stay in spec.md and die with the work item. Significant domain requirements ("power balance must account for recirculating power fraction") get promoted to PR-XXX because they're worth tracking long-term. The spec.md flags which MR-XXX should be promoted; `/implement-model` executes the promotion.

**New PR-XXX sub-type**: Add `domain requirement` to the existing sub-types in Role 4 (modeling patterns, structural rules, documentation rules, enforcement rules, naming conventions). Domain requirements are promoted from per-work-item specs and trace to DI-XXX domain insights or G-XXX goals.

#### Change 1: Add traceability as a cross-cutting concern in the architecture doc

Traceability is not an information role — it's the *connective tissue between roles*. The architecture should define the link types, not just the roles.

**Add a new section: "Traceability Model"**

```
### Traceability Model

The information roles defined above are connected by explicit, typed links.
These links are the primary mechanism for impact analysis when knowledge evolves.

#### Link Types

| Link | From | To | Recorded in | Verified by |
|------|------|----|-------------|-------------|
| **derives** | DI-XXX (insight) | PR-XXX (requirement) | REQUIREMENTS.md `Source` column | /audit-models (coverage check) |
| **satisfies** | Model element | PR-XXX (requirement) | traceability_matrix.csv `Requirement` column | /audit-models (completeness check) |
| **sources** | Model element | Authority source | Doc comment `Source`/`Reference` fields | Level 6 validation (existence + format) |
| **traces-to** | PR-XXX (requirement) | G-XXX (goal) or AQ-XXX (question) | REQUIREMENTS.md `Source` column | /status (goal coverage) |
| **justifies** | AD-XXX (decision) | Model structure | ARCHITECTURE.md `Rationale` field | /audit-models (adherence check) |
| **supersedes** | DI-XXX (new) | DI-XXX (old) | KNOWLEDGE.md `Superseded-by` field | approval script (automatic) |

All links are between durable artifacts. Per-work-item spec.md files may reference
these IDs but are not part of the durable traceability chain.

#### The Traceability Matrix

`data/traceability_matrix.csv` is the authoritative record of model-element-level traceability.
It maps each significant model element to its justifying requirements and authority sources.

Schema:

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

The matrix has both `Knowledge` (DI-XXX) and `Requirement` (PR-XXX) columns.
Either or both may be populated for a given element. The `Knowledge` column enables
direct impact queries when a DI-XXX is superseded, without requiring an intermediate
requirement hop. The `Requirement` column enables requirement coverage checking.

**Ownership**: Tool-owned schema (columns), user-owned data (rows).
**Populated by**: `/implement-model` calls `agentic-mbse pm trace-element` (AP-7 T1 script)
  to append rows. Agent supplies content; script enforces schema, prevents duplicates,
  validates PR-XXX IDs exist in REQUIREMENTS.md and DI-XXX IDs exist in KNOWLEDGE.md.
**Verified by**: `/audit-models` (checks completeness). Future: `agentic-mbse validate`
  traceability level (parses SysML via syside, checks all definitions have entries).
**Queried by**: PM script engine (impact analysis).
```

#### Change 2: Formalize knowledge supersession in the DI-XXX data model

**Modify Role 2 entity format**:

```markdown
### DI-XXX: [Title]
- **Source**: [approved research doc, user note, or authority source]
- **Context**: [1-3 sentences: the domain fact and why it matters]
- **Model implications**: [what the models must capture because of this insight]
- **Analysis implications**: [what analyses this enables or requires]
- **Status**: captured | addressed | superseded
- **Superseded-by**: [DI-XXX ID, only when status = superseded]
- **Supersedes**: [DI-XXX ID, when this insight replaces an earlier one]
```

Key changes vs. original entity format:
- **Dropped `Derived requirements` field**: Back-references to MR-XXX/PR-XXX are not maintained on the DI-XXX side. The link from DI-XXX to model elements goes through `traceability_matrix.csv` (Knowledge column) directly.
- **Dropped `requirements-derived` status**: Without the back-reference, this status has no meaning. Simplified to three states: `captured` (insight recorded), `addressed` (model elements exist that trace to it), `superseded` (replaced by newer insight).
- **Added `Superseded-by` and `Supersedes` fields**: Bidirectional links for knowledge evolution.

#### Change 3: Define the knowledge evolution control flow

**Add to workflows.md: "Knowledge Evolution Flow"**

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
| 4. Query traceability_matrix.csv:               |
|    which elements have Knowledge = DI-003?      |
| 5. Produce IMPACT REPORT:                       |
|    - Affected model elements (with file paths)  |
|    - Affected PR-XXX requirements               |
|    - Affected work items (from work/active/)    |
| 6. Write impact report to                       |
|    knowledge/research/impacts/                   |
|    DI-003_superseded.md                         |
+-------------------------------------------------+
        |
        v
Agent presents impact report to user:
"DI-003 superseded. 3 model elements affected.
 Recommend: create a work item to update
 cost structure assumptions."
        |
        v
+-------------------------------------------------+
| USER DECISION POINT                             |
|                                                 |
| "Create work item" -> /backlog add              |
| "Review later"     -> impact report persists    |
| "No action needed" -> close (user judgment)     |
+-------------------------------------------------+
```

#### Change 4: Add impact analysis to the PM script engine

Add new operations to the AP-7 operations table:

| Operation | Tier | What the script does |
|-----------|------|---------------------|
| Trace element | T1 | Append row to `traceability_matrix.csv`. Validates schema, prevents duplicates, validates PR-XXX IDs exist in REQUIREMENTS.md and DI-XXX IDs exist in KNOWLEDGE.md. Called by `/implement-model` as elements are created. |
| Promote requirement | T1 | Append PR-XXX row to `project/REQUIREMENTS.md`. Validates format, assigns ID, records Source (DI-XXX or G-XXX). Called by `/implement-model` when spec.md flags an MR-XXX for promotion. |
| Supersede insight | T2 | Mark old DI-XXX as superseded, create new DI-XXX, query traceability_matrix.csv for affected elements, produce impact report. |
| Impact query | T1 | Given a DI-XXX or PR-XXX, traverse traceability_matrix.csv to find all affected model elements and work items. |

**Impact query** is the key primitive. It's a direct lookup:
```
DI-XXX -> [traceability_matrix.csv Knowledge column] -> model elements
PR-XXX -> [traceability_matrix.csv Requirement column] -> model elements
```

No intermediate hops through ephemeral documents. Fully deterministic (AP-4).

#### Change 5: Traceability validation as an architectural requirement

**Architectural requirement**: The validation pyramid must include programmatic traceability checking. This is not optional — it's the enforcement mechanism that makes the traceability model reliable.

Level 6 validation (`level6_traceability.py`) currently only checks doc comment *existence*. It must be extended with the following sub-checks:

1. **Format check**: Doc comments on definitions contain `Source` and `Reference` fields
2. **Resolvability check**: Referenced source documents exist in SOURCE_INDEX.md
3. **Completeness check**: `traceability_matrix.csv` has an entry for each definition (parsed via syside adapter)
4. **Requirement coverage check**: Every PR-XXX in `project/REQUIREMENTS.md` has at least one satisfying element in `traceability_matrix.csv`

Sub-checks 1-3 extend Level 6. Sub-check 4 is a cross-file check that may belong in Level 7 (architectural integrity) or as a standalone `agentic-mbse validate --traceability` flag.

**Implementation**: Phase 3D. The syside adapter already parses SysML files and can enumerate definitions. The new check compares that list against `traceability_matrix.csv` entries.

#### Change 6: Add traceability diagrams

Add traceability link diagrams to the new Traceability Model section (supplementary to the main Document Relationship Map, which was updated by B-004):

```
Traceability forward path (durable chain):

KNOWLEDGE.md               REQUIREMENTS.md
  DI-XXX ───derives───>  PR-XXX
                             |
                             | satisfies (traceability_matrix.csv)
                             v
                        Model elements ──sources──> Authority sources
                         (models/)                  (SOURCE_INDEX.md)
```

```
Impact propagation (reverse path):

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

### Summary of architecture doc changes

| Section | Change |
|---------|--------|
| information-architecture.md (new section) | **Traceability Model**: link types, traceability matrix schema (with Knowledge + Requirement columns), traceability diagrams, validation requirements |
| information-architecture.md Role 2 entity format | Drop `Derived requirements` field. Add `superseded` status, `Superseded-by` and `Supersedes` fields. Simplify status to `captured \| addressed \| superseded`. |
| information-architecture.md Role 4 | Add `domain requirement` sub-type to PR-XXX. Note promotion path from per-work-item MR-XXX. |
| information-architecture.md file structure | Add `knowledge/research/impacts/` subdirectory for impact reports. |
| workflows.md | Add Knowledge Evolution Flow (supersession control flow). |
| main.md AP-7 Operations table | Add `Trace element` (T1), `Promote requirement` (T1), `Supersede insight` (T2), and `Impact query` (T1). |

### Resolved decisions

1. **Traceability matrix format**: **CSV**. Easier to parse programmatically. The PM script engine can generate a markdown view for the `/status` dashboard if needed, but CSV is the source of truth.

2. **Granularity of the `satisfies` link**: **Element-level** (every `def` gets an entry). Start here; if it proves too verbose in practice, introduce a threshold later (e.g., usages inherit from their def). This is a tuning knob, not an architectural decision — the schema supports either granularity.

3. **Traceability chain must use only durable artifacts**: The chain routes through KNOWLEDGE.md (DI-XXX), REQUIREMENTS.md (PR-XXX), traceability_matrix.csv, doc comments, and SOURCE_INDEX.md. Per-work-item spec.md files are working documents — useful for planning but not load-bearing for traceability.

4. **Requirement promotion**: Significant MR-XXX requirements in spec.md are promoted to PR-XXX in REQUIREMENTS.md during `/implement-model`. The promotion is selective — fine-grained implementation details stay in spec.md and are archived with the work item. Only requirements worth long-term tracking get promoted. The `trace-element` AP-7 script handles the promotion.

5. **DI-XXX does not maintain back-references**: The `Derived requirements` field is dropped from the DI-XXX entity. Impact queries go through traceability_matrix.csv's Knowledge column (direct: DI-XXX → model elements) rather than through an intermediate MR-XXX/PR-XXX hop maintained on KNOWLEDGE.md. This eliminates a maintenance burden without losing query capability.

6. **Detecting missing traceability**: Two levels:
   - **Near-term (command-level)**: `/audit-models` checks PR-XXX entries in REQUIREMENTS.md against `traceability_matrix.csv`. Any PR-XXX without a satisfying element is flagged.
   - **Future (validation-level)**: Extend `agentic-mbse validate` with a traceability validation level that parses SysML files (via syside adapter) to find all definitions, then checks each against `traceability_matrix.csv`. Definitions without entries are flagged.

7. **Impact report persistence**: **Persist** to `knowledge/research/impacts/`. The impact report is evidence of why a work item was created and enables later review of how knowledge evolution affected the project.

### Remaining open questions

1. **Traceability validation level number**: Should this be a sub-level of Level 6 (traceability & documentation) or a new level? Level 6 currently checks doc comment existence; adding traceability matrix completeness and source resolvability is a natural extension. Recommend: extend Level 6 with sub-checks rather than adding a new level. Resolve during Phase 3D.

2. **`trace-element` script interface**: Exact CLI arguments and behavior for the AP-7 script that `/implement-model` calls, including the promotion step. Resolve during Phase 3D when implementing the PM script engine.

### Coupling with other backlog items

- **B-001 (Model Implementation)**: B-002's impact query traverses `work/active/` to find affected work items. B-001 will formalize the work item lifecycle. Not blocking — B-002 uses the already-established file system conventions. When B-001 defines feedback loops, it should reference B-002's supersession flow as a concrete instance.
- **B-004 (Downstream pipeline)**: Complete. Document Relationship Map already updated. B-002's traceability diagrams are supplementary to the main map.
- **B-005 (Markdown parsing fragility)**: B-002's CSV decision for traceability_matrix.csv is consistent with B-005's concerns. B-005 should note this as a precedent.
- **B-008 (Inline knowledge capture)**: B-008 builds on B-002's infrastructure (same scripts, different trigger). Implement B-002 first.

---

## B-003: Delete intent dimension; simplify work item taxonomy

**Severity**: Medium
**Resolve before**: Phase 1A
**Status**: Complete — integrated into workflows.md § 2, main.md § 4-5, components.md § 4. Work item lifecycle consolidated in workflows.md § 3.
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

**What happens to Fix/Refactor/Integrate guidance**: This is prompt-level concern, not architecture. The `/spec-model` command can internally ask "what kind of change is this?" and adjust its questions accordingly — but that's a command design decision (Phase 3C), not an information architecture or control flow concern.

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
**Status**: Complete

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

### Analysis

The four gaps are real, but the original recommendation over-engineers the solution. Three distinct concerns are conflated:

**Concern 1: Codegen failures are a compile loop, not a workflow concern.** A sysml-codegen error is like a compiler error — the user fixes the model and re-runs. Creating backlog items for compile errors is overhead that serves no one. The real gap is that Level 8 validation and sysml-codegen can **drift apart**: Level 8 checks FR-2 through FR-7 today, but if sysml-codegen adds new requirements, Level 8 won't catch them until updated.

**Concern 2: Verification types conflate intent with mechanism.** The existing types (`baseline`, `reasonableness`, `physical`, `relationship`, `rollup`) describe **what you're checking**. "Simulation" describes **how you check it**. An SV-XXX entry like "p_net output accuracy" is a `baseline` check regardless of whether you verify it by model inspection, running codegen + teax, or manual calculation. The missing dimension is **mechanism** — some SV-XXX entries can only be verified after the full pipeline runs, and today they sit as `Status: pending` forever with no explanation of why.

**Concern 3: The Document Relationship Map stops at models/.** The full value chain continues through codegen and teax, with results feeding back through tests. The diagram should show this.

### Decisions

#### Decision 1: State the Level 8 / sysml-codegen contract

Level 8 validation checks are **derived from** sysml-codegen's extraction and analysis requirements. When sysml-codegen rejects a model pattern that Level 8 accepts, that's a bug — Level 8 must be updated to match. This is a development coordination obligation, not an information architecture change.

**No new data models, verification types, or automation.** Just a stated contract.

#### Decision 2: Add `Mechanism` column to VALIDATION_MATRIX.md

Instead of new verification types, add an orthogonal dimension that captures **how** each criterion is verified:

| Mechanism | Meaning | Example |
|-----------|---------|---------|
| `model` | Verifiable by model inspection / `agentic-mbse validate` | Structural completeness, naming conventions |
| `test` | Verifiable by pytest (may include codegen + simulation) | p_net accuracy, energy balance conservation |
| `manual` | Requires human judgment | "Architecture is reasonable for CATF concept" |

Updated entity format:
```markdown
| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |
|----|-------------|------|-----------|----------|-----------|--------|------|--------|
| SV-001 | Total capital cost ballpark | reasonableness | test | $3B-$15B | range | engineering judgment | test_capital_cost_range | pending |
| SV-002 | p_net output accuracy | baseline | test | PyFECONS value | ±1% | PowerBalance.py:94 | test_pnet | passing |
| SV-003 | All calc defs have doc comments | model | model | present | exact | MODELING_GUIDE.md | - | passing |
```

This lets `/status` report: "4 SV-XXX entries require simulation tests and are not yet verifiable" — which is real information the user needs.

#### Decision 3: Pytest skip pattern for pre-codegen verifications

Users should be able to write verification tests (SV-XXX entries with `Mechanism: test`) through the normal work PM flow (`/spec-model` → `/implement-model`), even before codegen is operational. These tests are the **primary feedback path** from the downstream pipeline back to the modeling workflow.

**Pattern**: Tests that exercise the downstream pipeline use a `pytest.mark` skip condition based on codegen availability:

```python
import pytest

# Convention: tests/conftest.py defines the marker
codegen_available = pytest.mark.skipif(
    not _codegen_pipeline_ready(),
    reason="Codegen pipeline not yet operational"
)

@codegen_available
def test_capital_cost_range():
    """SV-001: Total capital cost in $3B-$15B range."""
    result = run_codegen_and_simulate("designs/catf_mfe/")
    assert 3e9 <= result.total_capital_cost <= 15e9
```

The skip detection function (`_codegen_pipeline_ready()`) checks for the presence of generated code or a sentinel file — details are an implementation concern, not an architectural one.

**Why this matters**: It lets the modeling workflow produce verification tests as natural artifacts of the spec→implement cycle. The tests exist and document expectations even while codegen is in development. When the downstream pipeline becomes operational, the tests automatically activate and `VALIDATION_MATRIX.md` entries transition from `pending` to `passing`/`failing`.

#### Decision 4: Extend Document Relationship Map

Show the downstream boundary and the feedback path through tests:

```
                         Model Artifacts
                          (models/, tests/)
                              │
                    ┌─────────┼──────────────────┐
                    │         │                   │
                    │         │ verified against   │ consumed by
                    │         v                   v
                    │  project/VALIDATION_MATRIX  Downstream Pipeline
                    │    SV-XXX criteria          (sysml-codegen → teax)
                    │         ^                   │
                    │         │                   │ simulation results
                    │         │                   │ feed back via tests/
                    │         └───────────────────┘
                    │
                    │ Level 8 validates codegen readiness
                    │ (contract: checks derived from sysml-codegen requirements)
                    v
```

#### What this intentionally does NOT add

- **No orchestration of the downstream pipeline.** sysml-codegen and teax have their own CLIs, error reporting, and architecture. agentic-mbse doesn't wrap or manage them.
- **No automated backlog creation from codegen errors.** Compile errors are fixed immediately. If a codegen error reveals a systemic model problem, the user creates a work item — that's judgment, not automation.
- **No persistence of simulation results in `data/`.** TEAx tracks its own provenance. Tests capture pass/fail. No need for agentic-mbse to duplicate this.
- **No new verification types.** The existing five types cover every verification intent. Mechanism (model/test/manual) is the missing orthogonal dimension.
- **No new architectural principles.** This falls naturally under the existing framework — AP-1 (design for N) already covers extensibility.

### Architecture doc impact

| Section | Change |
|---------|--------|
| information-architecture.md § Role 6 | Add `Mechanism` column to VALIDATION_MATRIX.md entity format. Three values: `model`, `test`, `manual`. |
| information-architecture.md § Document Relationship Map | Extend diagram to show downstream pipeline boundary and test-based feedback path. |
| main.md § validation pyramid or new note | State the Level 8 / sysml-codegen contract: "Level 8 checks are derived from sysml-codegen requirements. Drift is a bug." |
| workflows.md or components.md | Document the pytest skip pattern for pre-codegen verification tests as a convention that `/implement-model` follows when producing SV-XXX tests. |

---

## B-005: Markdown parsing as state store is fragile

**Severity**: Medium
**Resolve before**: Phase 1A
**Status**: Complete — decisions made, pending integration into architecture documents

### The Problem

The PM script engine derives all state from parsing markdown files. This is elegant but brittle:

- Markdown tables break easily (user adds a column, extra space misaligns pipes, prose between table rows)
- No schema validation is described — the script either parses correctly or silently produces wrong data
- No error recovery: what does `agentic-mbse status` do when BACKLOG.md has a malformed row?
- Agent-edited markdown may drift from expected format over time

AP-4 says "deterministic state" but markdown parsing is only deterministic if the input is well-formed.

### Analysis: File-by-file fragility assessment

B-001 already resolved the highest-risk case by establishing YAML frontmatter for spec.md and epic files. The remaining files have varying risk levels:

| File | What PM engine reads | Format | Fragility risk |
|------|---------------------|--------|---------------|
| `work/active/{item}/spec.md` | Status, Scale, Epic, Owner | YAML frontmatter (B-001) | **Low** |
| `work/backlog/epic-{name}.md` | Status, Priority, Goal | YAML frontmatter (B-001) | **Low** |
| `data/traceability_matrix.csv` | Full schema | CSV (B-002) | **Low** |
| `project/REQUIREMENTS.md` | PR-XXX rows, column values | Markdown table | **Low** — few rows, rarely hand-edited |
| `project/VALIDATION_MATRIX.md` | SV-XXX rows, Status/Mechanism | Markdown table | **Low** — few rows, script-updated |
| `knowledge/KNOWLEDGE.md` | DI-XXX entries, Status field | Structured markdown sections | **Low-Medium** — section-based |
| `work/BACKLOG.md` | Epic sections, item rows, status | Markdown tables + section headers | **Medium** — highest frequency read/write, most complex structure |

The real vulnerability is **BACKLOG.md** — most frequently read, most frequently edited (by both humans and agents), and most structurally complex (section headers for epics + nested tables for items).

### Decisions

#### Decision 1: YAML frontmatter is the standard pattern for machine-parsed markdown

All markdown files that AP-7 scripts read should use YAML frontmatter for machine-parsed fields. The markdown body holds human-readable content. Scripts parse frontmatter; they do not parse the body.

This is already established by B-001 for spec.md and epic files. B-005 makes it the **universal convention** across the project.

| File | Machine-parsed fields (YAML frontmatter) | Human-readable body |
|------|------------------------------------------|---------------------|
| spec.md | Status, Scale, Epic, Owner, Created, Updated | Requirements, scope, success criteria |
| design.md | Status, Created, Updated, Related Artifacts | Architecture approach, decisions |
| plan.md | Status, Created, Updated, Related Artifacts | Phases, scope, risks |
| epic-{name}.md | Status, Priority, Goal, Created, Updated | Decomposition, per-item breakdowns |
| BACKLOG.md | Structured epic/item data (see Decision 2) | Human-readable rendered view |

Files that are **not markdown** (traceability_matrix.csv) or are **registry-style** (REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md) continue with their existing formats. These are low-risk: few rows, script-maintained, and their tabular structure is simple enough that parse validation catches errors easily.

#### Decision 2: BACKLOG.md uses YAML frontmatter for machine state

BACKLOG.md is the highest-risk file for parse fragility. It's also the most frequently read by the PM engine. Move the structured data to YAML frontmatter; the markdown body is a human-readable rendered view that the agent maintains for readability but scripts do not parse.

**BACKLOG.md format**:

```markdown
---
epics:
  - name: "End-to-End Pipeline De-Risking"
    goal: G-001
    priority: P0
    status: active
    file: backlog/epic-end-to-end-pipeline-derisking.md
    items:
      - name: "Solar+Battery SysML Model"
        scale: standard
        status: completed
        completed: 2026-02-05
      - name: "Codegen Chain Spike"
        scale: standard
        status: active
        work_dir: active/codegen-chain-spike
      - name: "Cost Evaluation & Entry Points"
        scale: standard
        status: backlog

standalone:
  - name: "Fix cost_model redefines"
    scale: trivial
    priority: P1
    status: completed
    completed: 2026-01-28
  - name: "Add missing doc comments"
    scale: standard
    priority: P2
    status: backlog
---

# Project Backlog

## Epic: End-to-End Pipeline De-Risking
**Goal**: G-001 (LCOE traceability) | **Priority**: P0 | **Status**: active
**Epic file**: [epic-end-to-end-pipeline-derisking.md](backlog/epic-end-to-end-pipeline-derisking.md)

| Item | Scale | Status | Notes |
|------|-------|--------|-------|
| Solar+Battery SysML Model | standard | completed | 2026-02-05 |
| Codegen Chain Spike | standard | active | |
| Cost Evaluation & Entry Points | standard | backlog | |
...

## Standalone Items

| Item | Scale | Priority | Status | Notes |
|------|-------|----------|--------|-------|
| Fix cost_model redefines | trivial | P1 | completed | 2026-01-28 |
| Add missing doc comments | standard | P2 | backlog | |
```

**Why this works**:
- The PM script reads only the frontmatter — structured YAML, trivially parseable, schema-validatable
- The markdown body is a rendered dashboard maintained by the agent for human readability
- If the body drifts from the frontmatter, the frontmatter wins — it's the source of truth
- AP-7 scripts that update BACKLOG.md update the frontmatter; the agent can re-render the body
- Human edits go through the frontmatter; the body is a view, not a source

**Trade-off**: The frontmatter duplicates some information that appears in the body. This is intentional — the body is a convenience view, not a data store. The duplication cost is small (BACKLOG.md is a single file) and the reliability gain is large (no markdown table parsing for state queries).

#### Decision 3: AP-7 scripts validate input structure before reading

Extend the AP-7 contract: scripts guarantee not only output correctness but also **input validation**. When a script reads a structured file, it validates the expected structure before proceeding.

**Behavior on validation failure**:
- Scripts report what they *can* read and flag what they can't
- "3 of 5 work items parsed; BACKLOG.md frontmatter has invalid status value at epic[1].items[2]" is more useful than a crash
- The PM engine produces a partial dashboard with warnings, not a hard failure

This is a **graceful degradation** principle: malformed input is reported, not silently misinterpreted or fatally crashed.

#### Decision 4: Schema validation is an implementation concern, not an architecture one

The original recommendation to "define a schema for each structured file" is sound but is Phase 3D work (PM script engine implementation). The architecture states the requirement (scripts validate input) and the convention (YAML frontmatter). The exact schema definitions, validation libraries, and error message formats are implementation details.

### Architecture Document Changes

**In main.md AP-7 section** — extend script guarantees:

Add to the AP-7 key constraint paragraph: "Scripts validate the structure of files they read before parsing. Malformed input produces clear error messages, not silent wrong data or crashes. Partial results with warnings are preferred over hard failures."

**In workflows.md § 4.2** (PM Script Engine: Data Model) — add input validation requirement:

Add a note that the PM engine validates BACKLOG.md frontmatter schema before producing the dashboard. On validation failure, it reports warnings and produces partial results.

**In workflows.md § 3.6** (Epic Tracking) — update BACKLOG.md format:

Replace the current BACKLOG.md example with the YAML-frontmatter-based format.

**In information-architecture.md § 2** (Project File Structure) — update BACKLOG.md description:

Change from "Prioritized items with scale" to "Dashboard with YAML frontmatter for machine state, markdown body for human view."

### Coupling with other backlog items

- **B-001**: B-001 established YAML frontmatter for spec.md and epic files. B-005 extends this as the universal convention and applies it to BACKLOG.md specifically.
- **B-002**: B-002's CSV decision for traceability_matrix.csv is consistent — machine-parsed data uses machine-friendly formats. B-005 completes the picture for markdown files.
- **B-012**: File structure is settled. B-005 defines what goes *inside* BACKLOG.md, not where it lives.

---

## B-006: No decision promotion path

**Severity**: Low
**Resolve before**: Phase 3C
**Status**: Complete — decision promotion is a check within `/audit-models` (see B-007)

### The Problem

The architecture defines promotion for Rules (per-feature pattern -> REQUIREMENTS.md via Q4). But there's no equivalent for Decisions.

When writing `work/active/{item}/design.md`, an engineer makes structural decisions. Some turn out to be reusable across work items. The architecture says ARCHITECTURE.md captures "decisions that outlive any single work item" — but that's only knowable in retrospect. There's no mechanism for:

- Detecting that design.md decisions recur across work items
- Promoting a design.md decision to ARCHITECTURE.md
- `/audit-models` flagging "this pattern appears in 3 work items but isn't in ARCHITECTURE.md"

### Decision: Subsume into `/audit-models`

Decision promotion does not need its own mechanism. It is one of `/audit-models`' checks — the same command that already handles requirement promotion (Q4). The flow:

```
/audit-models reads: models/, project/ARCHITECTURE.md,
  project/REQUIREMENTS.md, work/completed/
        │
        v
Among other checks:
  "AD-002 says turbine is BOP. 4 completed work items
   use a pattern where cooling components are also BOP
   but this isn't codified. Promote to ARCHITECTURE.md?"
        │
        v
User approves → agent drafts AD-XXX entry →
  AP-7 script appends to ARCHITECTURE.md
```

This parallels requirement promotion exactly: the audit command detects, suggests, user approves, script registers.

No separate mechanism, command, or control flow is needed. See B-007 for the full `/audit-models` specification.

### Architecture doc impact

None beyond B-007. Decision promotion is listed as one of `/audit-models`' checks in the B-007 specification.

---

## B-007: /review-model vs /audit-models boundary

**Severity**: Low
**Resolve before**: Phase 3C
**Status**: Complete — boundary defined, output artifacts specified

### The Problem

Both commands verify correctness. The catalog implies the distinction is temporal:
- `/review-model`: before implementing (design review)
- `/audit-models`: after implementing (verification)

But their skill sets overlap heavily (both reference sysml-conventions, model-validation, project-structure). The architecture doesn't define:
- What specifically `/review-model` checks that `/audit-models` doesn't (and vice versa)
- Whether `/review-model` is a gate (blocks progression to implement) or advisory
- How their outputs differ structurally

### Decisions

#### The boundary: temporal, with distinct outputs and feedback paths

| Dimension | `/review-model` | `/audit-models` |
|-----------|-----------------|-----------------|
| **When** | Pre-implementation (after design, before implement) | Post-implementation (after model artifacts exist) |
| **Reads** | design.md, prototype, `project/REQUIREMENTS.md`, `project/ARCHITECTURE.md` | `models/`, `tests/`, spec.md (MR-XXX), `project/REQUIREMENTS.md`, `project/ARCHITECTURE.md`, `project/VALIDATION_MATRIX.md`, `data/traceability_matrix.csv`, `work/completed/` |
| **Question** | "Will this design work?" | "Did we build it right? Are project docs current?" |
| **Checks** | Design compliance with project rules, interface consistency, prototype validation (Levels 1-3), feasibility assessment | Spec requirement satisfaction (MR-XXX), source traceability, validation pyramid, requirement promotion (Q4), decision promotion (B-006) |
| **Output artifact** | `work/active/{item}/review.md` (user-curated findings) | Updates to project docs via AP-7 scripts; backlog entries for gaps |
| **Gate behavior** | Advisory — user decides whether to address findings before proceeding | Advisory — produces action items, may create backlog entries |
| **Feedback path** | review.md → `/design-model` reads and applies accepted changes | Project document updates propagate to all future work items |

#### `/review-model`: User-curated review artifact

**Problem with current practice**: The user reads terminal output and manually copy-pastes findings back to `/design-model`. This is friction-heavy and loses information.

**Solution**: `/review-model` writes a persistent review artifact with user curation.

**Flow**:

```
/review-model reads design.md, prototype, REQUIREMENTS.md, ARCHITECTURE.md
        │
        v
Agent presents findings organized by dimension:
  - Structural compliance (does design follow ARCHITECTURE.md?)
  - Requirements coverage (does design address all MR-XXX?)
  - Interface consistency (do ports/connections make sense?)
  - Prototype validation (do Levels 1-3 pass?)
  - Feasibility (are there known risks?)
        │
        v
┌─────────────────────────────────────────────────┐
│ USER DECISION POINT                             │
│                                                 │
│ For each finding:                               │
│   "Accept"  → included in review.md             │
│   "Skip"    → not worth addressing              │
│   "Defer"   → noted but not blocking            │
│                                                 │
│ Why user curation matters:                      │
│ - Agent sometimes misunderstands design intent  │
│ - Agent may flag minor issues not worth the     │
│   cost of changing                              │
│ - User has context the agent lacks              │
└──────────────────────┬──────────────────────────┘
        │
        v
review.md written to work/active/{item}/review.md
  Contains:
  - Overall verdict: pass / concerns / fail
  - Accepted changes (user-selected, actionable)
  - Deferred items (noted, not blocking)
  - Skipped items (not recorded)
        │
        v
/design-model reads review.md, applies accepted changes
```

**review.md format**:

```yaml
---
Verdict: pass | concerns | fail
Reviewed: YYYY-MM-DD
Design: ./design.md
---
```

Body contains the accepted and deferred findings in free-form markdown. The verdict is the machine-parseable field; the findings are human-readable.

**Key design choice**: The review is advisory, not a gate. The user can proceed to `/plan-model` or `/implement-model` even with a "concerns" verdict. AP-5 (toolkit, not pipeline) — don't force the user through a gate they may not need.

#### `/audit-models`: Project document updates

`/audit-models` is the post-implementation verification command. Its distinctive feature vs. `/review-model` is that it looks **across** work items and models, not just within a single design, and it **proposes updates to project-level documents**.

**Checks**:

1. **Spec requirement satisfaction**: For the audited scope, check that MR-XXX requirements from spec.md are satisfied by the model artifacts. Flag unsatisfied requirements.

2. **Source traceability**: Check that model elements have entries in `data/traceability_matrix.csv` and that doc comments cite sources registered in `knowledge/SOURCE_INDEX.md`.

3. **Validation pyramid**: Run `agentic-mbse validate` on the audited models. Report results by level.

4. **Requirement promotion** (Q4): Detect patterns that recur across work items but aren't in `project/REQUIREMENTS.md`. Propose promotion to PR-XXX.

5. **Decision promotion** (B-006): Detect structural decisions that recur across work items but aren't in `project/ARCHITECTURE.md`. Propose promotion to AD-XXX.

6. **Verification criteria**: Identify model behaviors that should have SV-XXX entries in `project/VALIDATION_MATRIX.md` but don't.

**Output**: Not a single artifact file. Instead, `/audit-models` proposes specific updates to project documents:

```
/audit-models reads models, project docs, completed work items
        │
        v
Agent presents findings:
  "3 unsatisfied MR-XXX in magnet-system spec"
  "Pattern: all assemblies use sum() rollup — promote to REQUIREMENTS.md?"
  "Cooling subsystem boundary used in 4 items — promote to ARCHITECTURE.md?"
  "No SV-XXX for energy balance conservation — add to VALIDATION_MATRIX.md?"
        │
        v
┌─────────────────────────────────────────────────┐
│ USER DECISION POINT                             │
│                                                 │
│ For each proposal:                              │
│   "Accept"  → agent drafts update,              │
│               calls AP-7 script                 │
│   "Skip"    → not acted on                      │
│   "Defer"   → added to backlog                  │
└─────────────────────────────────────────────────┘
```

For accepted proposals, the agent calls the appropriate AP-7 script: `register-requirement` for PR-XXX promotion, a new `register-decision` for AD-XXX promotion, `update-validation` for SV-XXX additions.

### Architecture doc changes

**In components.md § 1** — update command catalog:

| Command | Job | Key user decision | Skills referenced | Output |
|---------|-----|-------------------|-------------------|--------|
| `/review-model` | REVIEW design before implementing | Which findings to accept/skip/defer | sysml-conventions, model-validation, project-structure | `review.md` (user-curated) |
| `/audit-models` | VERIFY models + update project docs | Audit scope, which promotions to accept | model-validation, source-traceability, requirements-tracking | Project doc updates via AP-7 |

**In main.md AP-7 operations** — add one new operation:

| Operation | Tier | What the script does |
|-----------|------|---------------------|
| Register decision | T1 | Append AD-XXX entry to `project/ARCHITECTURE.md`. Validates format, assigns ID. Called by `/audit-models` when user approves a decision promotion. |

**In workflows.md § 3.3** (Stage Artifacts) — add review.md to the artifact list:

review.md is an optional artifact produced by `/review-model` between design and implementation. It feeds back into `/design-model` if changes are needed.

### Coupling with other items

- **B-006**: Fully subsumed. Decision promotion is check #5 in `/audit-models`.
- **B-001**: The close flow (§ 3.5) prompts for project doc updates at work item completion. `/audit-models` is the more thorough version — it checks systematically rather than relying on the user's memory.
- **B-002**: `/audit-models` check #2 (source traceability) uses the traceability infrastructure from B-002.

---

## B-008: No inline knowledge capture during non-research commands

**Severity**: Low-Medium
**Resolve before**: Phase 3C
**Status**: Complete — decisions made, pending integration into architecture documents

### The Problem

During any command — spec, design, implement — the agent may discover domain knowledge that doesn't fit the current work item. Example: "While implementing the magnet model, I realized HTS and LTS have fundamentally different cost structures — this should be a domain insight."

The only structured entry point for KNOWLEDGE.md is `/research` → approval flow. The architecture mentions `/spec-model` "can suggest adding insights" but doesn't define the control flow. Specifically:

- Does the agent pause the current command, invoke the research approval script, then resume?
- Does it queue insights for later capture?
- Is there a lightweight inline path that skips the full research flow?

### Decision: Lightweight inline capture via `add-insight` script

Define a lightweight capture path that reuses the existing AP-7 infrastructure but avoids the full `/research` flow. The agent proposes, the user approves, the script persists.

#### Control flow

```
Agent discovers domain insight during any command
(e.g., /design-model, /implement-model, /spec-model)
        │
        v
Agent presents the insight to the user:
  "I noticed that HTS and LTS magnets have fundamentally
   different cost structures. This seems like a domain
   insight worth capturing. Add to KNOWLEDGE.md?"
        │
        v
┌─────────────────────────────────────────────────┐
│ USER DECISION POINT                             │
│                                                 │
│ "Yes, capture it"  → proceed to script call     │
│ "Not now"          → continue current command   │
│ "Modify first"     → user edits, then capture   │
└──────────────────────┬──────────────────────────┘
        │
        v
Agent calls: agentic-mbse pm add-insight
  --title 'HTS vs LTS cost structure divergence'
  --context '1-3 sentences: the domain fact and why it matters'
  --model-implications 'what the models must capture'
  --analysis-implications 'what analyses this enables or requires'
  --source 'work-item:magnet-system/design.md'
  --rationale 'Discovered during design: PyFECONS treats all
    magnets uniformly but CATF data shows 3x cost difference
    between HTS and LTS at scale'
        │
        v
┌─────────────────────────────────────────────────┐
│ SCRIPT EXECUTION (AP-7, T1 invoked via T3)      │
│                                                 │
│ 1. Assign next DI-XXX ID                       │
│ 2. Format as structured entry                   │
│    (all fields passed by agent — no LLM call)   │
│ 3. Append to knowledge/KNOWLEDGE.md             │
│ 4. Print confirmation with DI-XXX ID            │
│                                                 │
│ Script guarantees:                              │
│ - Correct ID sequencing (no duplicates)         │
│ - Correct entry format (no missing fields)      │
│ - Atomic append                                 │
│ - Source field uses work-item: convention        │
└─────────────────────────────────────────────────┘
        │
        v
Agent confirms: "Captured as DI-017."
Resumes current command where it left off.
```

#### Key decisions

**1. AP-7 tier: T1 mechanics, T3 invocation pattern.** The agent is already in conversation and has already formulated the insight content. The user has already approved it. The script receives all DI-XXX fields pre-formed — no `claude -p` call needed. This is purely deterministic file ops (ID assignment, format enforcement, atomic append). This avoids the B-011 dependency (`claude -p` availability) entirely for this path.

**2. Source reference uses `work-item:` convention.** The source field records the work item directory name (the stable identifier across the lifecycle) plus the specific artifact where the insight was discovered:

```
- **Source**: work-item:magnet-system/design.md
```

The `work-item:` prefix is a convention the PM script can resolve — scan `work/active/` then `work/completed/*/` by the name segment. The directory name is stable: `work/active/magnet-system/` → `work/completed/20260215_magnet-system/`. This leverages the existing work item formality (spec.md as state-bearing file, directory name as identifier) without inventing a new ID scheme.

**3. Rationale field captures discovery context.** The inline path has weaker provenance than the `/research` path (no research document as evidence). The `--rationale` field compensates: it records *why* this insight was recognized and *what evidence* supports it. This goes into the DI-XXX entry as an additional field:

```markdown
### DI-017: HTS vs LTS cost structure divergence
- **Source**: work-item:magnet-system/design.md
- **Rationale**: Discovered during design: PyFECONS treats all magnets
  uniformly but CATF data shows 3x cost difference between HTS and LTS at scale
- **Context**: [the domain fact]
- **Model implications**: [what models must capture]
- **Analysis implications**: [what analyses this enables]
- **Status**: captured
```

The `Rationale` field is only present on inline-captured insights (research-sourced insights have the full research document as provenance). It answers "where did this come from?" when someone reviews KNOWLEDGE.md later.

**4. Immediate inline capture, not queued.** When the agent discovers an insight mid-command, it proposes immediately. The capture is fast (one script call, no LLM) and the insight is freshest in context. Queueing to end-of-command risks losing the context that made the insight recognizable. The user can always say "not now" to stay in flow.

**5. Add-only — no supersession.** The inline path only adds new DI-XXX entries. If the agent discovers a *contradiction* with an existing DI-XXX, it captures the new insight via inline path and flags the conflict for the user, but the supersession flow (B-002: mark old DI-XXX superseded, run impact analysis, produce impact report) happens through the full `/research` or explicit supersession command. The inline path should not bear that complexity.

**6. No deduplication gate.** The script does not attempt to detect near-duplicate insights. Reliable deduplication requires semantic comparison that is beyond a deterministic script's scope. Knowledge maintenance — deduplication, reorganization, staleness review — is a separate concern that operates on KNOWLEDGE.md periodically (e.g., during `/audit-models` or a future `/maintain-knowledge` command), not as a gate on the capture path. Capture should be low-friction.

#### DI-XXX entity format update

The inline capture path adds one optional field to the DI-XXX entity format (information-architecture.md Role 2):

```markdown
### DI-XXX: [Title]
- **Source**: [approved research doc, user note, authority source, or work-item:{name}/{artifact}]
- **Rationale**: [only for inline-captured insights: why this was recognized and what evidence supports it]
- **Context**: [1-3 sentences: the domain fact and why it matters]
- **Model implications**: [what the models must capture because of this insight]
- **Analysis implications**: [what analyses this enables or requires]
- **Status**: captured | addressed | superseded
- **Superseded-by**: [DI-XXX ID, only when status = superseded]
- **Supersedes**: [DI-XXX ID, when this insight replaces an earlier one]
```

The `Rationale` field is optional — only present when the source is a work item artifact (inline capture) rather than an approved research document (which provides its own provenance).

### Architecture document changes

**In main.md AP-7 operations table** — add one new operation:

| Operation | Tier | What the script does |
|-----------|------|---------------------|
| Add insight (inline) | T1 (T3 invocation) | Assign DI-XXX ID, format entry from agent-supplied fields, append to `knowledge/KNOWLEDGE.md`. All content pre-formed by agent — no LLM call. Source uses `work-item:` convention. |

**In information-architecture.md Role 2 entity format** — add optional `Rationale` field. Update `Source` field documentation to include `work-item:{name}/{artifact}` as a valid source type.

**In workflows.md** — add brief note in § 6 (Knowledge Evolution) or as new § 6.3:

"Domain insights can also be captured inline during any command via the `add-insight` script (AP-7, T1). This is a lightweight alternative to the full `/research` flow for insights discovered during spec, design, or implementation work. The inline path is add-only; supersession uses the full flow (§ 6.1)."

**In components.md** — no changes needed. The inline capture is a capability of existing commands, not a new command.

### Coupling with other backlog items

- **B-002 (Knowledge evolution)**: B-008's inline capture feeds into B-002's infrastructure. New DI-XXX entries from inline capture are immediately available for supersession queries and impact analysis. The inline path is add-only; B-002 handles supersession.
- **B-011 (AP-7 T2 `claude -p` dependency)**: B-008 explicitly avoids the T2 path. The agent passes pre-formed content; the script is pure T1. No `claude -p` dependency.
- **B-005 (Markdown parsing)**: The `add-insight` script appends structured entries to KNOWLEDGE.md following the same section-based format. KNOWLEDGE.md remains a low-fragility file (section-based, not table-based).

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
**Resolve before**: Phase 3D
**Status**: Complete — requirement captured in implementation sequencing

### The Problem

The architecture introduces new structural conventions:
- BACKLOG.md gets YAML frontmatter, new format
- OVERVIEW.md gets new sections (Goals Registry, Analysis Questions)
- New files appear (KNOWLEDGE.md, REQUIREMENTS.md, ARCHITECTURE.md, VALIDATION_MATRIX.md)
- File structure changes from `modeling_pm/` to `knowledge/`, `project/`, `work/`

What happens to fusion-tea (the real validation case) when these changes ship?

### Decision: Manual one-time migration, not automated tooling

This is a one-time structural change, not a recurring migration concern. Automated migration tooling (`agentic-mbse migrate`, version detection, schema diffing) is over-engineering for a single transition that affects one active project (fusion-tea).

**The migration is done manually** as part of the implementation plan. The implementation sequencing must explicitly identify **when** and **how** the fusion-tea repo is restructured to match the new architecture. This includes:

1. **File moves**: `modeling_pm/` content → `knowledge/`, `project/`, `work/` as appropriate
2. **Format changes**: BACKLOG.md → YAML frontmatter format; OVERVIEW.md → Goals Registry + Analysis Questions
3. **New files**: Create KNOWLEDGE.md, REQUIREMENTS.md, ARCHITECTURE.md, VALIDATION_MATRIX.md from templates, populated from existing fusion-tea content (research docs, established patterns, existing validation criteria)
4. **Content preservation**: Existing research docs, work items, backlog entries, and model artifacts must survive the restructuring intact

**Sequencing requirement**: The fusion-tea migration should happen during or immediately after Phase 1A (Information Architecture), when the file structure and entity formats are finalized but before Phase 2B (Skills Extraction) and Phase 3C (Command Redesign) need a conforming target repo to test against.

### Architecture doc impact

Added migration milestone to main.md § 4 (Implementation Sequencing) Phase 1A deliverables.

---

## B-011: AP-7 Tier 2 claude -p dependency

**Severity**: Medium
**Resolve before**: Phase 3D
**Status**: Closed — not an issue

### The Problem (original)

Tier 2 scripts call `claude -p` for content generation. This creates a hard dependency on Claude CLI availability:

- CI/CD environments may not have Claude CLI
- Testing requires either mocking the LLM call or fixture-based approaches
- Cost implications of LLM calls during automated operations
- Failure modes: what happens when `claude -p` fails (rate limit, network, auth)?

### Resolution

Claude Code is already a prerequisite for the entire agentic-mbse workflow — the commands, agents, and skills all run within Claude Code. The T2 scripts that call `claude -p` are invoked from within that environment, so CLI availability is guaranteed during normal use.

Testing and CI/CD concerns are implementation-level (mock the LLM call, use `--dry-run` flags) and don't require architectural treatment. These are standard practices that can be applied during Phase 3D without architectural decisions.

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
│   ├── BACKLOG.md               #   Dashboard: all epics + standalone items
│   ├── EPIC_GUIDE.md            #   Decomposition guide (tool-owned)
│   ├── backlog/                 #   Epic decomposition files
│   │   └── epic-{name}.md      #     Detailed scope, items, sequencing, risks
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

---

## B-013: MR-XXX → PR-XXX promotion trigger ambiguous

**Severity**: Medium
**Resolve before**: Phase 3C
**Status**: Closed — the promotion concept is fully specified in B-002 and information-architecture.md § 5. The "flagging" language in the architecture is imprecise but refers to agent-proposed, user-approved promotion at the moment of recognition. The concrete mechanism (how the agent decides what to propose, what the script arguments look like) is a Phase 3C command-design detail, not an architectural gap.

### The Problem

The architecture describes `trace-element` (an AP-7 T1 script called by `/implement-model`) as the mechanism that "promotes flagged MR-XXX to PR-XXX in REQUIREMENTS.md." But the *flagging* mechanism is unspecified:
- Who flags an MR-XXX for promotion? The agent during `/spec-model`? The user? The agent during `/implement-model`?
- How is the flag stored? A marker in spec.md? An argument to the `trace-element` script?
- When does the flag get evaluated?

Additionally, the close flow (workflows.md § 3.5) asks "Did you discover a modeling pattern that should be a project-wide rule?" — this is a second promotion path. The relationship between the two paths is not clarified.

### Where `trace-element` is discussed

The `trace-element` script appears in three architectural locations:

1. **main.md § 2 (AP-7 Operations table)**: `Trace element | T1 | Append row to data/traceability_matrix.csv. Validates schema, prevents duplicates, validates PR-XXX IDs exist in REQUIREMENTS.md and DI-XXX IDs exist in KNOWLEDGE.md. Called by /implement-model as elements are created.`

2. **information-architecture.md § 5.1 (Durable Chain Only)**: Describes the three-step flow — `/spec-model` writes MR-XXX, some get flagged for promotion, `/implement-model` calls `trace-element` which (a) promotes flagged MR-XXX to PR-XXX in REQUIREMENTS.md, (b) records element → PR-XXX link in traceability_matrix.csv, (c) PR-XXX's Source column records the DI-XXX or G-XXX it derives from.

3. **information-architecture.md § 5.6 (Open Questions)**: Acknowledges that the exact CLI arguments and behavior are a Phase 3D implementation concern.

The concern here is not the script interface (that's deferred), but the *conceptual design* of how promotion decisions are made and when they fire.

### Proposed resolution

Clarify that there are exactly two promotion paths:

1. **Inline during `/implement-model`**: As the agent creates model elements and calls `trace-element`, it can simultaneously propose a PR-XXX promotion if the requirement being satisfied is significant enough to be project-wide. User approves inline. The promotion and traceability registration happen in the same script call.

2. **At close time (workflows.md § 3.5)**: The "Did you discover a pattern?" trigger question catches things missed during implementation. Agent helps draft the PR-XXX, calls `promote-requirement` AP-7 script (or a mode of `trace-element`).

Both paths feed into the same REQUIREMENTS.md output. No "flagging" mechanism in spec.md is needed — promotion is always an immediate, user-approved decision at the moment it's recognized.

### Open questions

1. Should `trace-element` handle both traceability registration AND requirement promotion in one call, or should promotion be a separate script (`promote-requirement`)? The main.md AP-7 table already lists `Promote requirement | T1` as a separate operation — that suggests separate scripts.
2. Does the agent need to check whether a PR-XXX already exists (idempotency) before proposing promotion?

---

## B-014: Work item name resolution needs a reliable lookup mechanism

**Severity**: Medium
**Resolve before**: Phase 3D
**Status**: New

### The Problem

Several places in the architecture reference work items by name:
- Inline knowledge capture uses `work-item:{name}/{artifact}` as the DI-XXX source convention (workflows.md § 6.4)
- BACKLOG.md YAML references items by `name` field
- The PM engine needs to map names to directories

Active items have a predictable path: `work/active/{name}/`. But completed items are archived as `work/completed/YYYYMMDD_{name}/`, making direct lookup by name impossible — resolving `magnet-system` requires scanning `work/completed/*/` with a glob.

More broadly, work item names serve as **stable identifiers** throughout the architecture (in BACKLOG.md, traceability sources, knowledge provenance). But there's no explicit guarantee of uniqueness, no normalization convention (does "Codegen Chain Spike" become `codegen-chain-spike`?), and no lookup mechanism.

### Decisions

1. **Work item IDs**: Work items get immutable IDs following the pattern `WI-XXX` (e.g., `WI-001`, `WI-002`). IDs are assigned by the PM script that creates the item (same pattern as DI-XXX, PR-XXX, etc.). The ID is the stable, unique identifier used everywhere: BACKLOG.md YAML, traceability sources, knowledge provenance.

2. **Directory naming convention**: `{WI-XXX}_{descriptive-str}` — e.g., `WI-003_magnet-system-cost`. The ID prefix guarantees uniqueness and enables direct lookup. The descriptive string provides human readability when browsing the file system. Normalization for the descriptive part: lowercase, hyphens for spaces, strip special chars.

3. **Completed items retain the date prefix**: `work/completed/YYYYMMDD_{WI-XXX}_{descriptive-str}/`. The date prefix is useful for chronological sorting; the WI-XXX prefix enables lookup via glob `work/completed/*_WI-003_*/`.

4. **Active items**: `work/active/{WI-XXX}_{descriptive-str}/`.

5. **Source convention update**: Inline knowledge capture uses `work-item:WI-XXX` (not the descriptive string). This is a direct key — scripts resolve it via glob against `work/active/WI-XXX_*/` or `work/completed/*_WI-XXX_*/`.

### Proposed resolution

Add a `resolve-work-item` capability to the PM script engine. This is not a standalone command but a reusable internal function:

1. **ID assignment**: PM scripts that create work items (e.g., during `/spec-model` or `/backlog add`) assign the next WI-XXX ID. The ID is recorded in BACKLOG.md YAML and in spec.md frontmatter.
2. **Uniqueness**: Enforced by the ID scheme — sequential, no duplicates.
3. **Lookup**: `resolve-work-item WI-XXX` searches: `work/active/WI-XXX_*/` → `work/completed/*_WI-XXX_*/`. Returns the path or "not found." This is a utility used by other scripts (e.g., `add-insight` needs to validate the source work item exists).

This replaces the need for scripts to each independently implement path resolution. The ID is the stable identifier; the path is derived.

### Architecture doc impact

| Section | Change |
|---------|--------|
| workflows.md § 3.1 | Add `ID: WI-XXX` to spec.md YAML frontmatter |
| workflows.md § 3.6 | Update BACKLOG.md YAML example: items get `id: WI-XXX` field, directory names use `WI-XXX_` prefix |
| workflows.md § 3.2 | Update state derivation: directories are `WI-XXX_{descriptive-str}` |
| workflows.md § 6.4 | Update source convention: `work-item:WI-XXX` (not name) |
| information-architecture.md § 2 | Update file structure: `work/active/{WI-XXX}_{item}/`, `work/completed/YYYYMMDD_{WI-XXX}_{item}/` |
| main.md AP-7 operations | Add `resolve-work-item` as a query utility |
| B-015 | Add `resolve-work-item` to query scripts table |

### Resolved questions

1. **spec.md frontmatter**: Separate fields. `ID: WI-003` and `Name: "Magnet System Cost"`. The directory name is derived (`WI-003_magnet-system-cost`) and the PM engine handles resolution.
2. **BACKLOG.md YAML**: Separate fields. `id: WI-003` and `name: "Magnet System Cost"`. The human-readable name stays clean; the ID is the machine key.

---

## B-015: AP-7 error model: atomic vs tolerant not distinguished

**Severity**: Low-Medium
**Resolve before**: Phase 3D
**Status**: New

### The Problem

The architecture states two properties for AP-7 scripts:
- "Atomic: all-or-nothing (no partial updates)" — from the research-to-knowledge flow (information-architecture.md § 2)
- "Partial results with warnings are preferred over hard failures" — from the input validation guarantee (main.md § 2, AP-7)

These are contradictory when applied to the same system without distinction. Some scripts must be atomic (a half-completed file move is worse than no move). Other scripts should be tolerant (a status dashboard that crashes on one malformed file is worse than one that skips it with a warning).

### Proposed resolution

Distinguish two categories of AP-7 scripts based on their operation type:

**Mutation scripts** (atomic — all-or-nothing):
| Script | What it mutates |
|--------|----------------|
| `approve-research` | Moves file, appends to KNOWLEDGE.md |
| `close-item` | Moves directory, updates BACKLOG.md |
| `trace-element` | Appends to traceability_matrix.csv |
| `promote-requirement` | Appends to REQUIREMENTS.md |
| `register-decision` | Appends to ARCHITECTURE.md |
| `supersede-insight` | Updates KNOWLEDGE.md (two entries), writes impact report |
| `add-insight` | Appends to KNOWLEDGE.md |
| `update-validation` | Updates row in VALIDATION_MATRIX.md |

**Query scripts** (tolerant — partial results with warnings):
| Script | What it reads |
|--------|--------------|
| `status` | BACKLOG.md, spec.md frontmatter, REQUIREMENTS.md, VALIDATION_MATRIX.md, file system |
| `impact-query` | traceability_matrix.csv, KNOWLEDGE.md, REQUIREMENTS.md |
| `resolve-work-item` (B-014) | work/active/, work/completed/ |

The principle: **writes are atomic, reads are best-effort.** This aligns with standard database transaction semantics. Mutation scripts validate inputs and either succeed completely or fail with no side effects. Query scripts report what they can parse and warn about what they can't.

### Architecture doc impact

Add a sentence to main.md § 2 (AP-7 input validation guarantee) clarifying the distinction: "Mutation scripts are atomic — they succeed completely or fail with no side effects. Query scripts are tolerant — they produce partial results with warnings when inputs are malformed."

4. **`analysis/` placement**: `work/analysis/`. The output of `/analyze-models` is operational intelligence — "what state are the models in" — which informs what work to do next. It's not domain knowledge (that's `knowledge/`), it's project state assessment.

---

## References

- `.project/research/20260130-235423_information-role-taxonomy.md` — Original information role taxonomy
- `.project/concepts/unified-toolkit-architecture.md` — Current architecture doc
- `.project/research/20260130-234525_agentic-mbse-pipeline-critical-analysis.md` — Critical analysis including non-linear development
- `.project/research/20260126-161628_python-vs-mbse-command-comparison.md` — Command comparison analysis

# Unified Concept: MBSE Toolkit Architecture

**Date**: 2026-01-31
**Status**: Concept — synthesized from research, ready for design-phase detailing
**Synthesized from**: 5 research/concept documents (see [References](#references))

This is the strategic spine of the architecture redesign. It defines the problem, principles, implementation plan, and open questions. For detailed data models, workflows, and component catalogs, see the linked documents.

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
| **AP-3** | **Behavior-justified taxonomy** — every category (scale, information role, etc.) must change downstream behavior; if it doesn't, delete it | P3, avoiding bureaucratic overhead |
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

**Input validation guarantee**: Scripts validate the structure of files they read before parsing. Malformed input produces clear error messages, not silent wrong data or crashes. Partial results with warnings are preferred over hard failures — "3 of 5 work items parsed; BACKLOG.md frontmatter has invalid status at epic[1].items[2]" is more useful than a crash.

Mutation scripts (approve-research, close-item, trace-element, promote-requirement, register-decision, supersede-insight, add-insight, update-validation) are **atomic** — they succeed completely or fail with no side effects. Query scripts (status, impact-query, resolve-work-item) are **tolerant** — they produce partial results with warnings when inputs are malformed.

**Operations that require AP-7 treatment** (identified so far):

| Operation | Tier | What the script does |
|-----------|------|---------------------|
| Approve research | T2 | Move `knowledge/research/pending/` → `approved/`, generate DI-XXX entries, append to `knowledge/KNOWLEDGE.md` |
| Register project requirement | T1 | Append PR-XXX row to `modeling_project/REQUIREMENTS.md` with correct columns (rare — project-level rules only) |
| Close work item | T1 | Move `work/active/{WI-XXX}_{name}/` → `work/completed/YYYYMMDD_{WI-XXX}_{name}/`, update `work/BACKLOG.md` status. Agent handles project-document feedback prompt separately (see [workflows.md § 3.5](workflows.md)). |
| Update validation status | T1 | Update Status column in `modeling_project/VALIDATION_MATRIX.md` for specified SV-XXX |
| Project status query | T1 | Parse all structured files, produce dashboard markdown |
| Trace element | T1 | Append row to `data/traceability_matrix.csv`. Validates schema, prevents duplicates, validates PR-XXX IDs exist in `modeling_project/REQUIREMENTS.md` and DI-XXX IDs exist in `knowledge/KNOWLEDGE.md`. Called by `/implement-model` as elements are created. |
| Promote requirement | T1 | Append PR-XXX row to `modeling_project/REQUIREMENTS.md`. Validates format, assigns ID, records Source (DI-XXX or G-XXX). Called by `/implement-model` when spec.md flags an MR-XXX for promotion. |
| Register decision | T1 | Append AD-XXX entry to `modeling_project/ARCHITECTURE.md`. Validates format, assigns ID. Called by `/audit-models` when user approves a decision promotion. |
| Supersede insight | T2 | Mark old DI-XXX as superseded, create new DI-XXX, query `data/traceability_matrix.csv` for affected elements, produce impact report to `knowledge/research/impacts/`. See [workflows.md § 6.1](workflows.md). |
| Impact query | T1 | Given a DI-XXX or PR-XXX, traverse `data/traceability_matrix.csv` to find all affected model elements and work items. Returns structured result for agent interpretation. |
| Add insight (inline) | T1 (T3 invocation) | Assign DI-XXX ID, format entry from agent-supplied fields (title, context, model/analysis implications, source, rationale), append to `knowledge/KNOWLEDGE.md`. All content pre-formed by agent — no LLM call. Source uses `work-item:{WI-XXX}/{artifact}` convention. Called by any command when agent discovers a domain insight mid-workflow. |
| Resolve work item | T1 (query) | Given WI-XXX, search `work/active/{WI-XXX}_*/` then `work/completed/*_{WI-XXX}_*/`. Returns path or not-found. Internal utility used by other scripts. |

---

## 3. Architecture Overview

The architecture addresses five concerns, each detailed in its own document:

**Information Architecture** → See [information-architecture.md](information-architecture.md)
Six information roles flow through the system: Authority Sources, Domain Knowledge, Project Intent, Modeling Requirements, Modeling Decisions, and System Verification. Each role has a producer, consumer, structured home, and entity format. The file structure mirrors the information flow model with four top-level content directories: `knowledge/` (Roles 1-2), `modeling_project/` (Roles 3-6), `work/` (execution tracking), and `models/` (artifacts).

**Downstream Pipeline Boundary** → See [information-architecture.md § 4.1](information-architecture.md#41-downstream-pipeline-boundary)
The modeling workflow produces models that feed into sysml-codegen and teax. agentic-mbse defines the boundary — not the other side of it. Verification evidence from the downstream pipeline flows back through pytest tests into VALIDATION_MATRIX.md. Level 8 validation is governed by a contract: its checks are derived from sysml-codegen's requirements, and drift between them is a bug.

**Workflows** → See [workflows.md](workflows.md)
The behavioral layer: how knowledge is delivered to commands (skills), how work items are classified and routed (scale taxonomy), how work items move through their lifecycle (entity model, states, artifact conventions, close flow), how project state is tracked (PM script engine + agent commands), and how research and analysis work.

**Components** → See [components.md](components.md)
The inventory of everything we're building: 13 commands, 7 skills, 6 agents, and 10 project templates, each with its role and relationships.

**Backlog** → See [backlog.md](backlog.md)
12 open items to resolve before implementation, ranging from high-severity (Model Implementation as a first-class concern, knowledge evolution) to low-severity (command boundary clarification).

---

## 4. Implementation Plan

**Moved to**: [implementation-plan.md](implementation-plan.md) — Epic structure, sequencing, deliverables, exit criteria, risk register.

**Summary**: Four epics with a strict dependency chain:

```
Epic 1: Structure (Phase 1A)
  Templates, cmd_init, fusion-tea migration, frontmatter schemas
    │
    ▼
Epic 2: Knowledge (Phase 2B)
  7 skills extracted from commands, context window measurement
    │
    ├──────────────────────────────┐
    ▼                              ▼
Epic 3: Commands (Phase 3C)    Epic 4: PM Engine (Phase 3D)
  9 refactored, 5 new             Parsers, state, operations,
  Validation walkthroughs         dashboard, CLI subcommands
    │                              │
    └──────── /status ◄────────────┘
```

Every individual change is enumerated in [delta-checklist.md](delta-checklist.md) (~111 items).

---

## 5. Open Design Questions

Questions resolved during the concept phase are recorded here for traceability, then the remaining open questions that must be resolved during implementation.

### Resolved during concept phase

| # | Question | Resolution | Where documented |
|---|----------|------------|------------------|
| Q1 | Are six roles right? | Yes — validated against fusion-tea. Every role has real content. | information-architecture.md § 3 |
| Q2 | Where does Architecture Vision live? | Standalone `modeling_project/ARCHITECTURE.md` (Role 5). | information-architecture.md § 3 Role 5 |
| Q3 | Domain insight format? | DI-XXX with 7 fields (Source, Rationale, Context, Model/Analysis implications, Status, Superseded-by/Supersedes). | information-architecture.md § 3 Role 2 |
| Q4 | How do project-level rules get promoted? | Both paths: `/implement-model` promotes MR-XXX → PR-XXX via `Promote requirement` (AP-7 T1); `/audit-models` proposes pattern-based promotions. | B-002, B-006/B-007, main.md AP-7 table |
| Q5 | When does a registry file become unwieldy? | ~100 entries. Deferred to experience. | information-architecture.md § 3 Role 2 scaling note |
| Q5a | Intent formalization control flow? | Dedicated `/formalize-intent` command (AP-7 T2). Can be triggered by `/onboard` or run standalone. | information-architecture.md § 3 Role 3, components.md § 1 |

### Open — Phase 2B: Skills

| # | Question | Must resolve before |
|---|----------|---------------------|
| Q9 | What's the context window impact of loading 3-4 skills simultaneously? | Phase 3C (commands depend on knowing if skills can be co-loaded) |
| Q10 | Should skills load all content upfront or stage-by-stage? | Phase 3C |
| Q11 | What's the right granularity? If sysml-conventions is 400 lines, is that one skill or two? | Phase 2B completion |

### Open — Phase 3: Commands + PM

| # | Question | Must resolve before |
|---|----------|---------------------|
| Q12 | How do we validate that refactored commands don't lose implicit knowledge? | Phase 3C completion — walkthrough against fusion-tea workflows |
| Q13 | What's the minimum viable PM dashboard? | Phase 3D start |
| Q14 | Should `/analyze-models` be a script or agent command? | Phase 3D start |
| Q15 | Should there be a formal command template (structure all commands must follow)? | Phase 3C start |

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

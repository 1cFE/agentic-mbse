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

## 3. Architecture Overview

The architecture addresses five concerns, each detailed in its own document:

**Information Architecture** → See [information-architecture.md](information-architecture.md)
Six information roles flow through the system: Authority Sources, Domain Knowledge, Project Intent, Modeling Requirements, Modeling Decisions, and System Verification. Each role has a producer, consumer, structured home, and entity format. The file structure mirrors the information flow model, with `knowledge/`, `intent/`, and `modeling_pm/` as top-level directories.

**Workflows** → See [workflows.md](workflows.md)
The behavioral layer: how knowledge is delivered to commands (skills), how work items move through the system (scale taxonomy and routing), how project state is tracked (PM script engine + agent commands), and how research and analysis work.

**Components** → See [components.md](components.md)
The inventory of everything we're building: 13 commands, 7 skills, 6 agents, and 10 project templates, each with its role and relationships.

**Backlog** → See [backlog.md](backlog.md)
12 open items to resolve before implementation, ranging from high-severity (Model Implementation as a first-class concern, knowledge evolution) to low-severity (command boundary clarification).

---

## 4. Implementation Sequencing

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

## 5. Open Design Questions

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

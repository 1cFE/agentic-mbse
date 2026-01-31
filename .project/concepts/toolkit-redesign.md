# Concept: MBSE Toolkit Redesign

**Date**: 2026-01-31
**Status**: Draft concept — establishing direction, not committing to specifics
**Basis**: Research documents listed in [References](#references)

---

## Problem Statement

The current agentic-mbse toolkit has five structural problems:

1. **Commands embed shared knowledge** — domain knowledge (SysML syntax), workflow logic, and output templates are tangled together in 400-1300 line commands instead of being extracted into reusable skills
2. **Project definition doesn't scale** — templates are placeholders designed for a single set of goals and requirements, but real projects need structured, growing registries (the "0, 1, N" problem)
3. **The pipeline is rigid** — every change, regardless of type or size, is funneled through the same spec → design → plan → implement sequence
4. **Development is assumed to be linear** — but real work involves going back, pausing, switching context, and refactoring
5. **Project management is unreliable** — state tracking depends on agent memory rather than deterministic file-system reads

---

## Design Concept 1: Shared Knowledge via Skills

### Problem

Commands contain hundreds of lines of domain knowledge (SysML conventions, validation patterns, project structure rules) that is:
- Duplicated or inconsistent across commands
- Unavailable to commands that need it but don't embed it
- Bloating commands well past the 500-line recommendation

### Concept

Extract shared knowledge into Claude Code skills. Skills are loaded on demand into the main conversation, referenced by multiple commands.

**Candidate skills** (to be refined during design):
- SysML conventions (syntax, naming, patterns, pitfalls)
- Model validation (quality pyramid, CLI commands, pass/fail criteria)
- Project structure (library vs designs, file organization, cross-file patterns)
- Source traceability (SOURCE_INDEX format, citation patterns, doc comments)
- Epic decomposition (Goldilocks principle, task types, decomposition process)
- Requirements tracking (registry format, lifecycle, aggregation)
- Toolkit awareness (CLI commands, environment) — already exists

**Key constraint**: Each skill must justify its existence by being referenced by 2+ commands. A skill that only one command uses should remain in that command.

**Expected impact**: Command sizes drop from ~476 average to ~250 average. Knowledge becomes consistent and maintainable.

### Open Questions

- What's the context window impact of loading multiple skills? Needs measurement.
- Should commands load all referenced skills upfront, or only the ones needed for the current stage?
- What's the right granularity? Too many small skills = overhead; too few large skills = back to the same problem.

---

## Design Concept 2: Information Taxonomy and Structured Project Definition

### Problem

There is an old CS adage: design for 0, 1, or N. `SOURCE_INDEX.md` already designs for N — many sources, structured format, works when empty, scales gracefully. The rest of the project definition designs for 1:

- `OVERVIEW.md` has one goals section — but fusion-tea needs a 400-line charter plus structured requirements, analysis angles, and validation criteria
- Requirements exist per-feature (MR-XXX in spec.md) but have no project-wide aggregation
- Domain insights and analysis angles exist only in conversation and research prose
- There is no architecture vision document

### Concept

**Define an information taxonomy for MBSE projects.** Each entity type in the taxonomy:
1. Has a defined role in the data flow (what produces it, what consumes it, what it enables)
2. Has a structured home (a document or document section designed for N entries)
3. Has a skill that captures correct usage patterns (so commands interact with it consistently)

The information-role taxonomy research identified six roles. The design work is to:
- Validate and refine these roles (are six right? too many? too few? wrong boundaries?)
- For each role, define the entity format, storage location, and lifecycle
- For each role, define what produces it and what consumes it in the workflow
- Ensure the taxonomy is minimal — every entity type must earn its place by enabling a downstream action that wouldn't work without it

The research identified these candidate roles:

| # | Role | Produces → Consumes | Currently Structured? |
|---|------|---------------------|----------------------|
| 1 | Authority Sources | External references → research, validation | Yes (SOURCE_INDEX.md) |
| 2 | Domain Knowledge | Research findings → specs, designs | Partially (research docs, but insights unstructured) |
| 3 | Project Intent | Goals, scope → requirements, priorities | No (prose in OVERVIEW.md) |
| 4 | Modeling Requirements | Verifiable statements → implementation, validation | Partially (per-feature only) |
| 5 | Modeling Decisions | Architecture, patterns → implementation | Partially (design.md, MODELING_GUIDE) |
| 6 | Model Artifacts | SysML models, tests → validation, analysis | Yes (models/, tests/) |

The "design for N" principle means each structured home must:
- Work when empty (new project — just headers and an example entry)
- Work at moderate scale (10-30 entries — single file, structured tables)
- Have a strategy for large scale (50+ entries — when/how to split)

### Litmus Test

Every entity type must have a clear answer to: **"What downstream action does structuring this enable that doesn't work today?"**

For example:
- Structuring requirements in a registry enables `/status` to report coverage and `/audit-models` to verify cross-feature
- Structuring domain insights enables `/spec-model` to surface relevant angles and prevents "dropping"
- If structuring something doesn't change any command's behavior or output, it's documentation overhead, not architecture

### Open Questions

- Are six roles right? The boundary between "Domain Knowledge" and "Project Intent" may be fuzzy.
- Where does the architecture vision live? Standalone document vs. section of OVERVIEW.md?
- What's the right format for domain insights? The "Analysis Angles" (AA-XXX) proposal from earlier research is one option but may be over-specified.
- When does a single registry file become unwieldy? Probably higher than we think (markdown tables with 50 rows are still scannable), but needs validation.
- Do per-feature spec.md files coexist with a project-wide requirements registry, or does one replace the other?

---

## Design Concept 3: Work Item Taxonomy and Adaptive Pipeline

### Problem

The pipeline treats all work identically. But a one-line attribute fix, a multi-file feature, a research investigation, and a cross-cutting refactoring are fundamentally different types of work. They need different amounts of process, different pipeline stages, and different artifacts.

### Concept

**Define a work item taxonomy that controls pipeline routing.** Each work item is tagged along two dimensions — intent (what kind of work) and scale (how big) — and the pipeline adapts accordingly.

How it works in practice:
- When work begins (via `/spec-model` or `/backlog`), the system determines the item's intent and scale — interactively, by tag, or by inference
- The intent determines which pipeline stages are required and how each stage behaves (what it asks for, what it produces, what it skips)
- The scale determines how much process overhead is appropriate (full artifacts vs. lightweight vs. none)
- The taxonomy is defined in a skill so that all commands route consistently

**The litmus test for adding a new intent or scale level**: it must change downstream behavior. Specifically, it must specialize some combination of prompt content, required data/artifacts, or control flow (which stages run). If a tag doesn't change what the system actually does, it's categorization overhead and should not exist. This is how the current system got to 1,345 lines in design-model.md — accumulated specificity without clear behavioral differentiation.

**Candidate intent types** (illustrative, not final):

| Intent | Why it exists (what changes downstream) |
|--------|-----------------------------------------|
| Model (build new) | Full pipeline; design needed for structural decisions; plan needed for phasing |
| Fix (correct known issue) | Design can be skipped — the user already knows the structure; spec is lightweight |
| Investigate (explore unknown) | Research must happen before spec can be written; may not produce implementation at all |
| Refactor (reorganize) | Design is about reorganization, not invention; regression criteria are primary concern |
| Integrate (connect pieces) | Design focuses on interfaces, not components; cross-file dependencies are the core challenge |

**Candidate scale levels** (illustrative, not final):

| Scale | Why it exists (what changes downstream) |
|-------|-----------------------------------------|
| Trivial | No spec/design/plan needed — `/quick-model` handles directly with validation |
| Small | Abbreviated artifacts; single-file scope |
| Standard | Full pipeline per the intent's path |
| Epic | Must decompose before entering pipeline |

These are starting points. The design work is to validate each candidate against the litmus test and cut anything that doesn't earn its keep.

### Open Questions

- How does the system determine intent and scale? Interactive prompting seems most natural but adds friction. Auto-detection with confirmation may be better.
- Is the intent × scale matrix too complex? Maybe scale is sufficient and intent is implicit in the user's description.
- Where does the taxonomy live? In the `epic-decomposition` skill? In its own skill? In a project template?
- How do we avoid the taxonomy becoming bureaucratic overhead? The user should feel like the system is adapting to them, not that they're filling out a form.

---

## Design Concept 4: Research Split

### Problem

`/research` currently serves two fundamentally different jobs:
1. **External**: "Learn about a domain topic from authority sources" (explore PyFECONS, read papers, understand physics)
2. **Internal**: "Understand the current state of our models" (what files exist, what patterns are used, what's healthy/unhealthy)

These have different inputs (authority sources vs. model files), different outputs (domain knowledge document vs. model state report), and different agent usage patterns.

### Concept

Split into two functions. The external research function also serves as a natural capture point for domain insights — at the end of research, the system prompts for any insights that emerged and offers to add them to the structured taxonomy (Concept 2).

The internal analysis function feeds project management — its output is what `/status` uses for architecture health indicators.

### Open Questions

- Naming: `/research` + `/analyze-models`? `/research` + `/model-health`? Something else?
- Does the internal function belong as a command, or as part of the script-backed status engine (Concept 5)?

---

## Design Concept 5: Script-Backed Project Management

### Problem

PM operations currently rely on agent commands. The agent might forget to update the backlog, might hallucinate status, or might archive incompletely. State tracking should not depend on LLM memory.

### Concept

**Design principle: State queries should be deterministic (scripts), state changes should be guided (agent commands).**

| Operation Type | Mechanism | Why |
|----------------|-----------|-----|
| Read state ("what's the status?") | Python script reads file system | Deterministic, no hallucination |
| Count/aggregate ("how many requirements have tests?") | Python script parses files | Exact answer needed |
| Interpret state ("what should we do next?") | Agent reads script output, applies judgment | Requires context and prioritization |
| Create artifacts ("write a spec for X") | Agent command | Creative, interactive |
| Archive/move files ("close this work item") | Python script with agent confirmation | File ops should be deterministic |

**Implementation**: A Python module (`src/agentic_mbse/pm/`) and CLI subcommand (`agentic-mbse status`) that:
- Scans project directories for work item states
- Parses markdown files for checkbox completion, requirement counts, etc.
- Produces a markdown dashboard (terminal-friendly, IDE-preview-friendly)
- Is tested with unit tests against known project structures

The `/status` agent command then layers intelligence on top of the script output.

**Visual output**: Markdown tables and text-based trees that render well in both terminal (80-column) and IDE preview. Even if simple, having a visual representation of epics, tickets, and project progress is valuable for orientation.

### Git Integration — Deferred with Notes

Git could serve as the mechanism for "going back" (backward navigation) and checkpointing progress. However, there are real trade-offs:
- Power users prefer to withhold commits for IDE diff review
- Less git-savvy users (the primary audience) need guidance
- Automatic commits would break existing workflows

**Deferred decision**: Git integration should be designed separately. For now, the concept is:
- No automatic/implicit git operations
- A potential explicit `/checkpoint` command for users who want it
- If we want users to review changes via git, we should instruct them how (in `/onboard`)

### Open Questions

- How much of the status engine depends on the information architecture (Concept 2) being implemented first? Probably a lot — it needs to know what files to parse.
- Should the PM module be a hard dependency (must have structured files) or gracefully degrade (works with whatever exists)?
- What's the minimum viable dashboard? Epic progress + work item states? Or does it need requirements coverage too?

---

## Design Concept 6: Agent Strategy

### Problem

Commands reference agents inconsistently. Some commands use `sysml-expert`, others use `sysmlv2-doc-analyzer`, with no clear guidance on when to use which.

### Concept

**Keep all existing specialist agents. Standardize how commands reference them.**

The original analysis recommended consolidating from 4+ SysML agents to 2. However, empirical testing shows parallel specialist agents have better recall than a unified agent — when launched in parallel with focused prompts, results are higher quality than a single agent covering all documentation.

The fix is not consolidation but standardization:
1. Document when each agent should be invoked (which question types)
2. Define focused prompt patterns per agent
3. Update all commands to reference agents consistently
4. Create an agent usage guide

### Open Questions

- Are there agents that truly overlap and could be merged without recall loss? Needs testing.
- Should the agent usage guide be a skill (loaded by commands) or a reference doc (for developers)?

---

## Design Concept 7: Command Redesign

### Problem

Commands are too long (avg 476 lines), structurally inconsistent, and embed knowledge that should be in skills.

### Concept

With skills extracted (Concept 1), information architecture defined (Concept 2), and taxonomy in place (Concept 3), commands can be redesigned to focus on their job.

**Each command should:**
- Focus on one job (a user decision to be made)
- Reference skills for domain knowledge instead of embedding it
- Follow a consistent structure (header format, stage naming, checkpoint language)
- Adapt behavior based on work intent and scale where applicable
- Target 200-300 lines

**New commands needed** (identified from gap analysis against Python agentic system):
- `/quick-model` — small changes without full pipeline (from Python's `_my_quick_edit`)
- `/review-model` — design review before implementation (from Python's `_my_review_design`)
- `/status` — project state + recommendations (from Python's `_my_project_manage`)
- Internal analysis function — model state examination (split from `/research`)

**Command redesign depends on Concepts 1-3 being resolved.** The specific command structures in the research document are illustrative of the direction, not specifications. The actual command designs will be driven by what the skills contain, what the information architecture looks like, and what the taxonomy defines.

### Open Questions

- Should there be a formal command template document, or is consistency enforced by example?
- How do we validate that refactored commands don't lose implicit knowledge? Walkthrough against fusion-tea workflows?

---

## Sequencing

These concepts have dependencies:

```
Concept 2 (Information Taxonomy)  ──┐
                                    ├──► Concept 1 (Skills) ──► Concept 7 (Commands)
Concept 3 (Work Item Taxonomy)  ───┘         │
                                             │
Concept 4 (Research Split) ─────────────────►│
                                             │
Concept 5 (Script-Backed PM) ◄──────────────┘

Concept 6 (Agent Strategy) ──────────────────► Concept 7 (Commands)
```

The information taxonomy (Concept 2) and work item taxonomy (Concept 3) are foundational — they define what information exists and how work is categorized. Skills (Concept 1) depend on knowing what information architecture they'll reference. Commands (Concept 7) depend on everything else.

Concept 5 (PM) and Concept 6 (Agents) are somewhat independent and can proceed in parallel with other work.

---

## References

| Document | Key Contribution |
|----------|-----------------|
| `.project/research/20260126-161628_python-vs-mbse-command-comparison.md` | Quantified gaps vs. Python system |
| `.project/research/20260130-234525_agentic-mbse-pipeline-critical-analysis.md` | Structural problems, redesign vision, command sketches |
| `.project/research/20260126-202931_requirements-goal-tracking-pipeline.md` | Requirements dropping, Analysis Angles, validation criteria |
| `.project/research/20260130-235423_information-role-taxonomy.md` | Six information roles, traceability gaps |

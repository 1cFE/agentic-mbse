---
name: my-concept
description: Develop a feature concept with scope and success criteria. Use when an idea needs definition before specification.
---

Generated from `claude-pack/commands/_my_concept.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Concept Command

**Purpose:** Develop a feature concept with success criteria, user stories, and scope definition
**Input:** Brief description of what the user wants (via `User-provided arguments are supplied when this skill is invoked.`)
**Output:** `.project/concepts/{feature-name}.md` (main body ≤300 lines; optional appendices excluded)

## Overview

You are a research partner helping the user develop a feature concept. The user drives the thinking — you collect data, present options, and synthesize.

**Your primary role is to help the user build understanding of the problem and solution space. You do NOT decide the solution. You do NOT jump to writing deliverables. You research, present alternatives, ask questions, and capture decisions the user makes.**

**A good concept lets a cold reader answer four things quickly:** what problem matters, why this shape is promising, what is deliberately out, and what the next stage needs to resolve.

When invoked:
- If feature description provided via `User-provided arguments are supplied when this skill is invoked.`: proceed to concept process
- If no description: ask "What would you like to build?" and request a brief description of the desired outcome

## Core Values

- **Technical but outcome-focused.** You understand the codebase deeply (via subagents) to scope accurately, but you do NOT jump to solutions. You may identify components and behaviors that likely need to change to help manage scope, but you don't specify exact implementation changes.
- **UX expertise.** You think through clean and intuitive product design. User stories reflect real user workflows.
- **Simplicity.** Strongly prefer the simplest approach that achieves the outcome. If the main body of a concept can't be captured in ≤300 lines, the scope needs to shrink.
- **End outcomes and behaviors.** Every section should describe what the user experiences or what the system does — not how the code achieves it.

## Process

### Stage 1: Understand Context

1. **Read User's Request**
   - Parse `User-provided arguments are supplied when this skill is invoked.` for the feature description
   - Note every detail the user provides

2. **Explore the Codebase**
   - Use a fresh-context `explorer` subagent to understand current state
   - Identify relevant components, existing patterns, and integration points
   - Understand what exists today so the concept is grounded in reality

3. **Check Project Context**
   - Read `.project/CURRENT_WORK.md` if it exists
   - Read `.project/backlog/BACKLOG.md` if relevant
   - Check `.project/concepts/` for related prior concepts

### Stage 2: Build Understanding

**The human drives. You are a research partner, not a decision-maker.**

Your job is to help the user think through the problem top-down — starting broad and getting specific only as understanding deepens. You do NOT decide the solution. You do NOT jump to drafting. You stay in this stage until the user explicitly tells you to write the concept.

**This stage progresses through three levels of depth. Do NOT skip ahead.** Start at Level 1. Only move deeper as the current level becomes clear through conversation with the user.

#### Level 1: The Problem (WHY)

Focus: What is wrong or missing today? What pain does this cause? Why does it matter?

- Research the current state — how things work today, what breaks or is missing
- Present your understanding of the problem back to the user
- Ask questions about: Who is affected? What triggers the pain? What does "solved" look like?
- **Do NOT discuss solutions yet.** Stay on the problem until the user is satisfied you understand it.

#### Level 2: Broad Approach (HOW, broadly)

Focus: What are the high-level ways this could be solved? What are the tradeoffs?

- Only enter this level once the problem is well-understood
- Present broad approaches as options: "One way this could work is... Alternatively we could..."
- Ask questions about: Which tradeoffs matter? What constraints exist? What's the simplest version?
- Stay at the level of approaches and strategies — not implementation details

#### Level 3: Fit and Shape (WHERE / WHAT specifically)

Focus: Where does the chosen approach land in the codebase? What does it touch? How does it fit existing patterns and flows?

- Only enter this level once the user has indicated a direction
- Research the specific areas of the codebase that would be involved
- Present findings on: existing patterns to follow, integration points, components affected, scope boundaries
- Ask questions about: edge cases, scope boundaries, what's in vs. out

#### At every level:

- **Research** — use subagents to explore the codebase. Go where the conversation points.
- **Present and ask** — share findings with specific references, ask questions to deepen understanding
- **Synthesize** — after the user responds, summarize what you've learned so far and what's still unclear
- **If corrected:** Go back and research more. Do NOT paraphrase the correction and proceed. Show corrected understanding with evidence.

**EXIT CONDITION: The user explicitly says to write/draft the concept. Do NOT self-promote to the next stage.**

### Stage 3: Write Concept

Only enter this stage when the user tells you to.

1. **Draft the Concept Document**
   - Write to `.project/concepts/{feature-name}.md` using the template below
   - Ground every section in the understanding built during Stage 2
   - Stay within the 300-line main-body limit

2. **Critical Review**
   - Re-read the entire document
   - Verify all success criteria are specific and measurable
   - Verify user stories describe real user workflows
   - Verify scope boundaries are clear
   - Use a fresh-context `default` subagent to critically evaluate: vague criteria, missing edge cases, scope creep, solution-prescribing, unclear user stories
   - Incorporate review feedback

3. **Present to User**
   - Share the concept for approval
   - Iterate if the user has feedback

### Stage 4: Document Creation

1. **Create Concepts Directory** (if needed)
   ```bash
   mkdir -p .project/concepts
   ```

2. **Write Concept File**

   Write to `.project/concepts/{feature-name}.md` using this template:

   ```markdown
   # Concept: [Feature Name]

   **Created:** [Date]
   **Status:** Draft

   ---

   ## Problem Statement

   [1-3 paragraphs explaining what's wrong or missing today, grounded in real user pain or project need]

   ## Owner's Words

   [Optional but default when sourced from a live conversation. The owner's key
   statements, verbatim. Later sections paraphrase; this is the record they trace to.
   Mark owner-given examples/referents with their force — see the guidelines below.]

   - **[OWNER-VERBATIM]** "[exact quote]"

   ## Success Criteria

   When this work is complete:

   1. **[Criterion 1]** — [Specific, observable outcome]
   2. **[Criterion 2]** — [Specific, observable outcome]
   3. **[Criterion 3]** — [Specific, observable outcome]

   ---

   ## Why This Shape

   - **Key bet:** [What direction or workflow shape this concept is betting on]
   - **Why this shape is promising:** [Why this seems simpler/better than obvious alternatives]
   - **Constraint to preserve downstream:** [A boundary or behavior spec/design should not violate]

   ---

   ## User Stories

   ### [Category]

   **US-1: [Story title]**
   As a [role], I can [action], so that [benefit].

   **US-2: [Story title]**
   As a [role], I can [action], so that [benefit].

   ---

   ## Key Concepts

   ### 1. [Concept Name]

   [Description of the concept — what it is and how it behaves from the user's perspective. NOT implementation details.]

   ---

   ## Scope of Behavior Changes

   ### New artifacts to create
   - [New file, component, or capability]

   ### Existing artifacts to modify
   - [Existing component and what changes about its behavior]

   ### Behavior changes by workflow stage
   - [Stage]: [What changes from the user's perspective]

   ---

   ## Non-Goals / Out of Scope

   [Grade each: [OWNER] the owner excluded it, [AGENT] you inferred the boundary.
   Record a rejected path as a decision (why), never as a prohibition — see correction
   discipline in the guidelines.]

   - **[OWNER]** [Explicit exclusion and why]
   - **[AGENT]** [Future enhancement deferred]

   ---

   ## Assumptions & Prerequisites

   - [Environmental or technical assumption]
   - [Dependency on existing capability]

   ## Open Questions

   1. [Unresolved question for spec phase]

   ---

   ## Next-Stage Handoff

   **Settled here:** (owner-grade only — see the settled rule in the guidelines)
   - **[OWNER]** [Decision or scope boundary downstream stages should treat as fixed]

   **Needs spec next:**
   - [Requirement or ambiguity the spec must resolve]

   **Decomposition guidance:**
   - [How this concept should break into work items, if relevant]

   ---

   ## Appendix (Optional - does not count toward the main-body budget)

   [Use only for supporting evidence, references, or alternative shapes that would bloat the main concept.]
   ```

3. **Line Count Check**
   - Verify the main body through "Next-Stage Handoff" is ≤300 lines
   - Optional "Appendix" sections do not count toward the main-body budget
   - If over, tighten scope or split into multiple concepts

## Guidelines

### What You MUST Do
- Explore the codebase before scoping (ground the concept in reality)
- Present alternatives as options ("One way... Alternatively..."), not as decisions
- Stay in Stage 2 until the user explicitly says to write the concept
- After a correction, go back and research more — demonstrate corrected understanding with specifics
- Preserve the owner's payload — examples, referents, numbers, named standards — verbatim or by path, with its force marked (illustrative vs binding); unclear force → ask. See `claude-pack/rules/capture-fidelity.md`.
- Record a rejected path as a one-line decision (why it's out), never as a prohibition aimed at future agents (correction discipline, same rule).
- Keep success criteria specific and observable
- Run a critical review before finalizing
- Stay within the 300-line main-body limit

### What You MUST NOT Do
- **Jump to drafting.** Do NOT write the concept document until the user says to. Stage 2 is for understanding only.
- **Decide the solution.** You collect data, present options, and synthesize. The user decides.
- **Self-certify understanding.** Never say "now I understand" and proceed. After a correction, go back to the code, research more, and show what you missed. Wait for the user to confirm.
- **Rush past corrections.** If the user says you missed the point, that is a STOP signal. Do not restate their words and continue — go deeper.
- Prescribe implementation solutions (no "use library X" or "add column Y")
- Skip the codebase exploration
- Write vague success criteria ("improve performance")
- Let the concept drift into a mini-spec or execution plan
- Exceed the 300-line main-body limit — if you can't capture it, the scope is too big
- Make assumptions about user priorities without asking

### Quality Standards
- Success criteria are specific enough that someone could verify each one
- User stories describe real workflows, not system behaviors
- Scope boundaries are clear — someone reading "Out of Scope" knows what NOT to build
- The "Why This Shape" section makes the main bets legible
- Key concepts explain behavior from the user's perspective
- The handoff makes clear what the next phase should treat as fixed vs open

---

**Related Commands:**
- Before concept: ``my-research`` for deep exploration of a topic
- After concept: ``my-spec`` for detailed requirements per work item

**Last Updated**: 2026-02-09


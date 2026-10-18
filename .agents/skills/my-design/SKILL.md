---
name: my-design
description: Create a technical design for an approved feature spec. Use when a feature needs architecture, interfaces, and tradeoff analysis.
---

Generated from `claude-pack/commands/_my_design.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Design Command

**Purpose:** Technical design for code implementation
**Input:** Spec document (`.project/active/{feature-name}/spec.md`), research findings
**Output:** `.project/active/{feature-name}/design.md` (main body target ~300 lines; optional appendices excluded)

## Overview

You are a specialist design agent. Your goal is to create technical specifications that someone unfamiliar with the codebase could use to guide implementation.

**This is a DESIGN DOCUMENT — conceptual architecture, not implementation:**
- Articulate WHAT the system IS before describing its parts
- Explain HOW parts relate and WHY this approach is right
- Describe interfaces, data flows, and integration points
- Code snippets: interfaces/schemas/pseudo-code only, ~10 lines max each. If you're writing implementation, stop — that belongs in the plan.
- Optimize the main body for mental alignment. Use optional appendices for supporting evidence that would otherwise bloat the design.

**Critical Research Requirements:**
- **MUST** thoroughly explore the codebase for existing patterns and utilities
- **MUST** search for relevant technical information as needed
- **MUST** present alternatives when design approach is uncertain
- **MUST** solicit user guidance on design decisions

Your design will be used for:
1. **User sign-off** on technical approach
2. **Code review** by those who need to understand the architecture
3. **Implementation planning** with specific file changes

When invoked:
- If feature name provided: proceed to design process
- If no feature: ask for feature name in `.project/active/` to design

## Design Process

This is an **iterative, self-critical refinement** approach. The agent cycles through research and reflection until confident in the design, engaging the user only at genuine decision points.

**Adapt your effort to task complexity**: Simple tasks may need one cycle, complex tasks need multiple iterations.

```
SETUP → enter cycle

CYCLE:
  RESEARCH → CONCEPT → REFINE → REFLECT → [Decision]

  From REFLECT, three possible outcomes:

  (a) Need user decision
      → Present alternatives
      → USER DECISION checkpoint
      → Return to RESEARCH

  (b) Need more research
      → Return to RESEARCH

  (c) High confidence
      → Exit cycle
      → SELF-REVIEW → [pass] → FINALIZE
                     → [fail] → one revision cycle → FINALIZE
```

### Stage 1: Setup

**Goal**: Prepare for design work without premature commitment

**Actions**:

1. **Read context**:
   - Check `CLAUDE.md` for project-specific conventions, patterns, and commands
   - Check any project documentation referenced in CLAUDE.md
   - Feature spec: `.project/active/{feature-name}/spec.md` (read FULLY)
     - Pay special attention to **Success Criteria** - your design must serve these
     - Note all requirements (tagged `[HARD]`, `[NEED]`, `[INFERRED]`, `[INHERITED]`) and open questions
     - Upstream `[INFERRED]`/`[INHERITED]` items are challengeable, not settled — a design bet may overturn one with evidence. When a challengeable item conflicts with owner-grade intent, don't resolve it silently: invoke the surfacing duty (see `claude-pack/rules/capture-fidelity.md`).
   - Product design: `.project/active/{feature-name}/product-design.md` (if it exists, read FULLY)
     - This is an optional artifact from ``my-product-design`` that settles experience and interaction decisions
     - Treat its decisions as settled input — flag only where a genuine technical constraint conflicts
   - Required Reading from the epic: if this item belongs to an epic, find it in the epic's Backlog Items section and read the files listed under its `**Required Reading**:` field. Treat them as **background context** — check your design decisions against the upstream shaping intent, but don't re-derive requirements (spec already did that). If a listed file doesn't exist, note it and move on. If the item has no epic or no Required Reading, skip this.
   - Decision records: read `.project/adr/INDEX.md` if present. Read in full any entry whose seams overlap this item's area, and cite them in Research Findings. If a design decision would contradict an active entry, that is a premise conflict — surface it (see `claude-pack/rules/capture-fidelity.md`): supersede the entry openly at acceptance or change the design, never resolve it silently. An absent or empty index means "no prior decisions," not an error.
   - Related research files in `.project/research/` (if they exist)

2. **Create design file** at `.project/active/{feature-name}/design.md`:
   - Get metadata:
     ```bash
     .project/scripts/get-metadata.sh
     ```
   - Add header (feature name, status: Draft, owner, dates, git info)
   - Add overview (1-2 sentence summary from spec)
   - Add "Related Artifacts" section linking to spec, research, epic, and Required Reading files (if any)
   - Create empty sections: "The Point", "Research Findings", "Core Concept", "Key Bets", "Key Decisions", "Architecture", "Required Invariants", "Component Overview", "Non-Goals", "Implementation Notes"

3. **Identify investigation areas**:
   - What existing code might be relevant?
   - What patterns or utilities should you look for?
   - What technical questions need answers?

**If inputs unclear**: STOP and ask for feature name, spec path, or missing context.

**Do NOT present anything to user yet** - proceed to Stage 2.

### Stage 2: Research → Refine → Reflect (Iterative Cycle)

**Goal**: Develop a well-vetted design through iterative research and critical self-evaluation

**This is a CYCLE - repeat until you reach one of the three outcomes below.**

#### Step A: RESEARCH

**Gather information to inform design**:

- **Analyze existing codebase**:
  - **For complex tasks or broad searches**: Use a fresh-context `explorer` subagent to find related code
  - **For targeted investigation**: Use Grep/Read to examine specific files
  - Extract: Reusable utilities, patterns, conventions, error handling approaches
  - Identify: Integration points with specific file:line references
  - Document: Testing patterns, validation approaches

- **Research technical requirements** (as needed):
  - External libraries/frameworks to consider
  - Best practices for this problem domain
  - Integration constraints or compatibility needs

#### Step B: CONCEPT

**Articulate the core design idea before describing parts:**

- Write a plain-language paragraph: what IS this system and how does it work conceptually?
- State the key insight or principle that makes the design work
- Explain why this is the RIGHT approach, not just a working one
- Name the existing pieces this design composes with and what each handles. Route concerns to existing pieces where they fit; do not design parallel mechanisms.

On the first cycle, draft the "Core Concept" section in the design document. On subsequent cycles, revisit and sharpen it based on new research.

**Do NOT proceed to REFINE until the concept is articulated.** If you can't explain the design in one paragraph, you need more research.

#### Step C: REFINE

**Re-read the Core Concept before drafting.** It is the anchor for every section that follows. While drafting, if a section starts to introduce mechanisms, components, or behaviors not foreshadowed by the Core Concept, **STOP and ask: are we making this too complicated?** The honest answer is one of two:

- The new mechanism belongs but the Core Concept didn't capture it — sharpen the concept first, then resume drafting against the updated anchor.
- The new mechanism doesn't belong — drop it.

Drift between the concept and the supporting sections is the signal that structure is being used to hide a gap in understanding. Treat it as a stop condition, not a refinement opportunity.

**Update design document based on research and concept:**

- **Update "Research Findings"** with what you learned:
  - Files analyzed, reusable patterns found (with file:line references)
  - Integration points, technical approaches considered

- **Draft/update design sections** (add detail progressively):
  - **Architecture**: How parts relate — boundaries, data flows, integration points. Focus on relationships, not code.
  - **Key Bets**: The beliefs about reality this design rests on, stated as claims, each with its "if false → what fails" failure mode
  - **Key Decisions**: The mechanism choices we made (X over Y), each naming the alternative considered and why it was rejected
  - **Required Invariants**: What must remain true for the design to work
  - **Component Overview**: Brief description of each part — purpose, location, responsibility. No implementation detail.
  - **Non-Goals**: What this design explicitly does not try to solve
  - **Implementation Notes**: Only critical gotchas, patterns to follow, constraints for the plan phase

**Code cap**: Snippets limited to ~10 lines — interfaces, schemas, type signatures, or pseudo-code only. If you're writing more than ~10 lines, you're writing implementation, not design. Stop and describe the concept instead.
**Main-body budget**: Prefer the main body to stay within ~300 lines. If supporting evidence would push it beyond that, move the extra material to an optional appendix.

#### Step D: REFLECT

**Critically evaluate your design — ask yourself**:

- **Simplicity**: "Could this be done with fewer moving parts? What is the minimum viable design?"
- **Abstraction quality**: "For each new abstraction: what happens if I just don't have it? Would inline/direct code be clearer?"
- **Right problem**: "Am I solving the spec's actual problem, or a more 'interesting' adjacent one?"
- **Proportionality**: "Does the complexity of this design match the complexity of the problem?"
- **Completeness**: "What parts of the codebase haven't I checked that might be relevant?"
- **Edge cases**: "What could go wrong? What failure modes exist?"
- **Assumptions**: "What am I assuming? Do these need validation? If a cheap-to-test bet rests on how something actually behaves, offer a ``my-spike`` (confirm a specific assumption with throwaway code) or ``my-learning-test`` (map an unfamiliar surface with kept tests) before locking the design on it."
- **Integration**: "Have I fully understood how this connects to existing systems?"
- **Business Goals**: "Does this design serve the business goals stated in the spec?"

**Now decide which outcome applies**:

#### OUTCOME (a): Design Decisions Needed → USER CHECKPOINT

**Conditions**:
- Multiple architecturally distinct approaches exist with meaningful trade-offs
- Choice impacts other systems or future maintainability
- User judgment needed (e.g., performance vs simplicity, new file vs extend existing)

**Actions**:
1. Add alternatives to the "Key Decisions" section with:
   - Context (why this decision matters)
   - 2-3 options with structure, pros/cons, code reuse, integration approach
   - Your recommendation with rationale
   - Open questions

2. **Present alternatives to user**:
   - Explain trade-offs clearly
   - Make reasoned recommendation
   - **WAIT for user's decision** - do NOT proceed

3. **After user responds**:
   - Document decision in "Key Decisions" section (what was chosen and why)
   - If user asks for more investigation → return to RESEARCH
   - If decision is clear → continue to OUTCOME (c) or more cycles if needed

#### OUTCOME (b): More Research Needed → LOOP BACK

**Conditions**:
- Found gaps in understanding during reflection
- Discovered new integration points or dependencies to examine
- Need to validate assumptions or investigate edge cases
- Questions arose that require codebase investigation

**Actions**:
- Identify specific questions to answer
- Return to RESEARCH step with focused investigation
- Continue cycle

#### OUTCOME (c): High Confidence in Approach → PROCEED

**Conditions**:
- Core concept is clear and the approach is justified (not just "works")
- Design is grounded in concrete codebase research with file:line references
- Complexity is proportional to the problem — no unjustified abstractions
- Integration points are clear and well-understood
- Edge cases and failure modes identified and addressed
- No significant unknowns or unvalidated assumptions
- Design satisfies all spec requirements AND serves business goals
- Can be understood by developers unfamiliar with the codebase

**Actions**:
- Proceed to Stage 3 (Finalization)

**Note**: Simple tasks may reach this outcome in one cycle. Complex tasks may take 2-4 cycles as detail is progressively added.

### Stage 2.5: Self-Review Gate

**Goal**: Catch over-engineering and conceptual gaps before presenting to user

**This is a single-pass critical read, not an iterative cycle.**

**Actions**:

1. **Re-read the complete design document from disk** (use Read tool on the design file)
2. **Evaluate honestly** — pretend you are a skeptical reviewer seeing this for the first time:
   - Is this the right approach? Could the spec be satisfied with a fundamentally simpler design?
   - Are core abstractions justified? For each new component/module/interface: what happens if it didn't exist?
   - Does complexity match the problem? A simple feature should have a simple design.
   - Would a senior engineer look at this and say "why?"
3. **If significant issues found**: return to Stage 2 for ONE revision cycle, then proceed to Stage 3 regardless
4. **If design holds up**: proceed to Stage 3

### Stage 3: Finalization

**Goal**: Complete the design document and get final user approval

**Actions**:

1. **Add final sections** to design file:
   - **"Potential Risks"**: What could go wrong, mitigation strategies
   - **"Integration Strategy"**: How this fits into existing workflows, what it complements/replaces
   - **"Validation Approach"**: Testing strategy, success criteria, manual verification steps
   - **"Next-Stage Handoff"**: What the plan/implementation stage should treat as fixed, open, and risky
   - **"Next Steps"**: Typically ``my-implement`` or ``my-plan`` for implementation after approval

2. **Review complete document**:
   - All spec requirements addressed
   - Business goals from spec are served by this design
   - Technical clarity throughout
   - All code references in file:line format
   - Alternatives and decisions documented (if any)
   - Logical flow from high-level to detail

3. **Present to user for final approval**:
   - Summarize the design approach
   - Highlight key decisions made (if any)
   - Note what existing code is being reused
   - **WAIT for approval** before suggesting next steps

4. **After approval — file decision records.** For each decision *this design itself
   settled* that passes the density bar in `.project/adr/README.md`: run
   `.project/scripts/adr.sh new <slug>`, fill in the body, set the provenance grade.
   Supersede entries this design was approved to replace (`adr.sh supersede <old> <new>`).
   Zero entries is the common case; decisions settled upstream (concept-design, spec) are
   cited, never re-filed. If the script is missing, note the gap; don't hand-mint ids.

**Expected final document structure**:
```
# Design: [Feature Name]
[Header: status, owner, dates, git info]

## Overview
[1-2 sentences]

## Related Artifacts
[Links to spec, research, epic]

## The Point
[The product obligation this work serves — the problem, and how it ladders up to the
bigger goal — stated in full, not reduced to a pointer. Every later stage checks against
this, so it must stay legible here rather than living only in the spec. Grade the governing
obligation by its source authority (capture-fidelity). This is the obligation to serve,
carried deliberately — not a prose recap of the spec.]

## Research Findings
[Codebase analysis, reusable patterns found, technical research]

## Core Concept
[Plain-language description of the approach. Key insight. Why this is right.]

## Key Bets

> A bet is a *belief about reality* this design rests on. If the bet is wrong,
> the design fails — not "we'd pick a different mechanism," but "we built the
> wrong thing." State each bet as a claim about the world, then explicitly name
> the failure mode: "If false → <what breaks>."
>
> Bets are NOT: choices between mechanisms, naming conventions, file layouts,
> or anything where "we could swap X for Y" would still leave the design intact.
> Those are Decisions.

- **B1.** [Claim about reality]. *If false → [what fails].*
- **B2.** ...

## Key Decisions

> A decision is a mechanism choice: we picked X over Y for these reasons.
> Decisions are reversible without invalidating the design's premise. Each
> decision must name the alternative considered and why it was rejected.

- **D1.** [Chosen mechanism]. *Rejected: [alternative] ([reason]).*
- **D2.** ...

## Architecture
[How parts relate — boundaries, data flows, integration points. No code listings.]

## Required Invariants
[What must remain true for the design to work. Testable assertions or strong constraints.]

## Component Overview
[Brief description of each part — purpose, location, responsibility.
 No implementation detail. No code.]

## Non-Goals
[What this design explicitly does not solve.]

## Implementation Notes
[Critical gotchas only. Patterns to follow. Constraints for the plan phase.
 Code snippets only for interfaces/schemas, ~10 lines max.]

## Potential Risks
[What could go wrong, mitigations]

## Integration Strategy
[How this fits into workflows]

## Validation Approach
[Testing strategy, success criteria]

## Next-Stage Handoff
[What the plan should treat as fixed. What remains open. What risk to de-risk first.]

## Appendix (Optional - does not count toward the main-body budget)
[Detailed file inventories, longer codebase evidence, or alternative approaches that would clutter the main design.]

---
Next Step: After approval → ``my-implement`` or ``my-plan``
```

## Guidelines

### Anti-Patterns — Avoid These

- **No concept, just components**: If you can't explain the design in one paragraph, it's not ready for parts
- **Implementation code in design**: Save complete scripts, code diffs, and detailed implementations for the plan
- **Unjustified abstractions**: For each new abstraction, articulate what would break without it. If nothing breaks, remove it
- **More components than the problem needs**: Simpler is always better. Ask "would I want to maintain this?"
- **"Technically works" is not good design**: A design that works but is awkward, unintuitive, or fragile is a bad design
- **Solving the wrong problem**: If you're drawn to a more "interesting" adjacent problem, check yourself against the spec
- **Restating the spec or research in prose**: If a section is mostly repeated context, link to the source artifact and keep the design focused on strategy. Exception: **The Point** is carried deliberately — state the product obligation the design serves in full rather than linking away, because every later stage checks against it (see capture-fidelity, "carry the problem")
- **Mechanism dressed as a bet**: If your "bet" reads like "we use X to do Y," it's a decision, not a bet. Bets are claims about reality ("Opus can produce better cross-concept judgment than a fixed pipeline"). Decisions are mechanism choices ("we orchestrate via Codex subagents rather than a Python fan-out loop"). If you can't state a clean "if false → ..." failure mode for a bullet, it's a decision.

### Critical Requirements
- Read spec FULLY before starting, especially business goals
- Use a fresh-context `explorer` subagent for complex codebase searches
- Present alternatives when approach is uncertain
- Get user approval on major decisions
- Include specific file:line references
- Never use placeholder values

### Design Quality
- Articulates what the system IS, not just what files to create
- Makes the main bets, invariants, and non-goals obvious on a skim
- Explains interfaces, data flows, and WHY decisions were made
- Every abstraction earns its existence
- Code in design: interfaces/schemas/pseudo-code only, ~10 lines max per snippet

### Iterative Approach
- **Adapt to complexity**: Simple tasks need less detail, complex tasks need more iteration
- **Research thoroughly**: Don't guess - explore codebase and search for information
- **Progressive refinement**: Add detail in multiple passes, one component at a time
- **Continuous updates**: Keep document current as decisions emerge
- **Minimize redundancy**: Use references instead of duplicating information

### Error Handling
- If spec doesn't exist: STOP and ask user to create it (suggest ``my-spec``)
- If approach uncertain: Present options to user
- If codebase integration unclear: Use a fresh-context `explorer` subagent

### Success Criteria
- Core concept is clear and justified — not just "works"
- Complexity is proportional to the problem
- Addresses all spec requirements; serves the business goals
- Can be understood by developers unfamiliar with the codebase
- Main body is concise enough to skim; supporting detail lives in an appendix if needed
- Architecture, data flows, and rationale clearly described
- Existing code thoroughly analyzed with specific references
- Passed self-review gate before presentation to user
- No unresolved technical questions

---

**Related Commands:**
- Before design: ``my-research`` or ``my-spec``
- Review: ``my-design-review`` for a critical review — in a fresh session, not this one
- After design: ``my-implement`` or ``my-plan`` for implementation

**Last Updated**: 2026-07-19 — added decision-record touch points (INDEX.md skim at setup, acceptance write-back for design-settled decisions).


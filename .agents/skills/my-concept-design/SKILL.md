---
name: my-concept-design
description: Develop a design concept describing architecture, patterns, and responsibilities. Use when a design area needs a critiqueable, auditable conceptual sketch before detailed design.
---

Generated from `claude-pack/commands/_my_concept_design.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Concept Design Command

**Purpose:** Develop a design concept that describes architecture, patterns, and responsibilities at a level that can be critiqued and audited
**Input:** Brief description of the design area (via `User-provided arguments are supplied when this skill is invoked.`)
**Output:** `.project/concepts/{design-name}.md` (main body ≤250 lines; optional appendices excluded)

> **⛔ The input document is READ-ONLY — never edit, append to, or overwrite it.** Always `Write` a NEW file. Give `{design-name}` a name distinct from any input file (append `-design` if needed) so the output can never collide with it; after writing, the input must show zero changes in `git status`.

## Overview

You are a design partner helping the user develop a design concept. The output should describe **how things should work together** — not implementation details, not execution steps.

A good design concept is:
- **Readable cold by someone who does not know the codebase.** The Problem and Goals sections should land without any prior knowledge of identifiers, classes, or file layout.
- **Conceptual upfront, specific downstream.** Problem/Goals/Principles describe the *system's* behavior and meanings. Core Model/Invariants name the *code* that enforces them. The reader understands what's wrong before meeting any field name.
- **Specific enough to critique.** "Where does this pattern fail?" should be answerable.
- **Clean.** If you can't describe the design simply, it's probably a bad design.
- **Decision-centered.** It makes the few load-bearing choices about boundaries,
  responsibilities, invariant ownership, and system semantics explicit. Those decisions,
  not template completion, are the work.

A good design concept is NOT:
- A wall of backticked identifiers. If every bullet in Problem or Goals starts with a code name, you're writing a spec.
- A detailed spec with field names, file paths, and implementation steps.
- A problem statement with success criteria (that's ``my-concept``).
- An execution plan with slices and dependencies (that's ``my-spec`` → ``my-plan``).

When invoked:
- If design area provided via `User-provided arguments are supplied when this skill is invoked.`: proceed to design process
- If no description: ask "What design problem are you trying to solve?"

## Core Values

- **Two registers, one document.** The upper half (Overview, Problem, Goals, Principles) describes what the *system* does — meanings, behaviors, outcomes. The lower half (Core Model, Invariants, Vocabulary, Scenarios) names the *code* that enforces it. Identifiers, class names, field names, and specific metrics do not appear in the upper half. This is the defining property of a good concept doc — violate it and the reader cannot follow.
- **Goals are functionality. Invariants are mechanism.** A goal describes an outcome the system delivers ("support stale-market replans without reinterpretation"). An invariant describes the code rule that makes it true ("`dispatch_valid_steps` is the sole authority for plan validity"). Never swap them.
- **Decision clarity.** The primary goal is to make clear what key decisions we are committing to. Implementation details obscure this — strip them. A reader should finish knowing exactly what bets we're making.
- **Root repair before compensation.** When the system has a semantic gap, first examine
  the component that should own the invariant and what existing machinery can be deleted
  or replaced. A downstream adapter or parallel mechanism must justify why repairing the
  real owner is impossible or wrong.
- **Current code is evidence, not authority.** Code, tests, pipelines, research, and
  compatibility baselines show what exists. They do not prove that the current semantics
  or architecture are correct.
- **Architectural clarity.** The design should explain how responsibilities are separated and how components interact.
- **Pattern-focused.** Name the patterns. Define the vocabulary. Make the mental model explicit.
- **Critiqueable.** Every design decision should be specific enough that someone could say "that won't work because..."
- **Minimal.** If a section isn't pulling its weight, cut it. The main body stays within 250 lines; optional appendices are for evidence, not the core design.

## The Two-Register Rule

This is the single most important rule in this command. Read the contrast before writing.

**Upper half** (Overview, Problem, Goals, Principles) — describe the WORLD:
- Use prose and plain-language bullets.
- Describe meanings being conflated, behaviors that fail, outcomes that drift.
- No backticked identifiers. No class names. No field names. No metrics from test runs.
- A colleague on another team should be able to follow.

**Lower half** (Core Model, Invariants, How It Works, Vocabulary, Validation) — describe the CODE:
- Identifiers, types, field names, and specific mechanisms belong here.
- This is where concepts get wired to the codebase.

**The test:** hand the doc to someone who has never read this codebase. They should finish Problem and Goals knowing what's wrong and what we want. If they need to look up a type or field name to follow, the register has leaked.

**Contrast (from real concept docs):**

Bad Problem bullet (spec register, identifier-heavy):
> **Validity is inferred, not signaled.** `RHBPerfModelSimple` computes pointer bounds from `DispatchGuidanceConfig.horizon_step_count` (a static config value, typically 24). The interface field `dispatch_valid_steps` exists but no controller emits it.

Good Problem bullet (conceptual register):
> The cache stores upstream payload timing. Replans reuse that timing as plan timing. The consumer's pointer clamp then masks the resulting expiry rather than surfacing it.

Bad Goal (mechanism masquerading as goal):
> `dispatch_valid_steps` is the sole authority for plan validity — no config fallbacks.

Good Goal (outcome):
> Make the consumer's expiry behavior correct by construction.

The bad versions aren't *wrong* — they're in the wrong section. Move them to Invariants.

## Process

> **The work is small — don't pad it.** A concept-design phase is: read the input and
> everything it references, inventory what's settled in your own head, resolve the 2–3
> genuinely open questions, write the doc. A good run lands in a handful of exchanges,
> not twenty. Manufactured questions, abstract restatements, and code forensics are
> motion substituting for the work.
>
> While discussing with the user:
> - **Don't manufacture questions.** Most "open questions" are already answered in the
>   input or the docs it references — you just read them (Stage 1). Find the answer there
>   first. Only raise a question you can tie to a specific gap: quote the input sentence
>   that *should* settle it but doesn't. Can't find that sentence? You haven't read
>   carefully, or the question is invented — either way, don't ask it.
> - **The two-register rule governs the document, not the conversation.** Ask the most
>   concrete question that settles the point: show two candidate dicts and ask "which
>   one," not "should the registry encode the distinction explicitly." Work out what a
>   thing must contain *before* asking about it — arrive at "an entry needs
>   `provenance: direct | derived`" by thinking, don't hand the user an abstract regress
>   to narrow. A question that takes two messages to parse is a bad question.
> - **When the user corrects a premise, drop it — don't re-encode it one layer up.** "The
>   library isn't poor, don't model around it" means abandon that framing, not "then the
>   registry must encode the distinction." Doubling down on a rejected premise wastes rounds.
> - **Don't turn design discussion into implementation forensics.** State the invariant you
>   need from existing code, verify only that, move on. Before escalating a suspected
>   dependency bug into a design prerequisite, check whether a cited report already
>   explains the behavior.

### Stage 1: Understand the Design Problem

**MANDATORY: You MUST explore the codebase before discussing ANY design ideas.**

A design concept that isn't grounded in the actual codebase is useless. You cannot design what you don't understand.

1. **Parse the Request**
   - What area of the system is this design for?
   - Is this a new design or a redesign of something broken?

2. **Explore the Codebase (REQUIRED — DO NOT SKIP)**

   Use a fresh-context `explorer` subagent to understand:
   - How the relevant area currently works
   - What patterns exist today
   - What's broken or missing
   - How components interact
   - **Prior decisions**: sweep the repo's official documentation (wherever its norms put
     it — docs/, ADRs, README; discover, don't assume) AND `.project/adr/INDEX.md`. Pull
     the full text of decision entries relevant to the design area. An absent or empty
     `.project/adr/` reads as "no prior decisions" — never an error. These feed the
     Prior Art section of the output.

   **You MUST complete this exploration before moving to Stage 2.**
   **You MUST report your findings to the user before proceeding.**

   If you cannot explore the codebase (no access, empty repo, etc.), STOP and tell the user. Do not proceed with abstract design work.

3. **Read Referenced Documents (REQUIRED — DO NOT SKIP)**

   Before any design discussion, gather every document reference recursively:
   the input/concept doc itself, every file path and "Related:" entry it names,
   and every reference inside those, followed to its source. Read all of them in
   full — not a grep, not a subagent skim. A "Related:" or "see report X" line is
   an explicit reference, not a speculative one: mandatory.

   Then report a one-line summary of each before proceeding. Not optional, not
   conditional. If a cited document answers a question, you have your answer — do
   NOT "rediscover" it by re-deriving from code.
   - The only thing you don't read: unreferenced docs you merely guess might be relevant.

### Stage 2: Build Design Understanding

**The user drives. You help think through the design.**

Progress through these levels. Do not skip ahead.

#### Level 1: The Structural Problem

Focus: What is structurally wrong or missing? Why do current approaches fail?

- Research how things work today
- Identify the failure modes or gaps
- Present your understanding of why the current design is inadequate
- Ask whether the existing pipeline or mechanism is part of the defect rather than a fixed
  constraint. Name what could be removed if the semantic problem were fixed at its owner.
- **Stay on the structural problem until clear.** Don't discuss solutions yet.

#### Level 2: Design Direction

Focus: What are the possible design approaches? What are the tradeoffs?

- Present design alternatives as options
- Include repair-at-owner and deletion/replacement as the first alternatives when they are
  plausible. Do not begin from coexistence with every current mechanism.
- Discuss tradeoffs: complexity vs. flexibility, coupling, extensibility
- Ask: What constraints matter? What's the simplest shape that works?
- Stay at the level of patterns and responsibilities, not implementation

#### Level 3: Design Shape

Focus: What are the key abstractions? Who does what? How do they interact?

- Define the core concepts/components
- Define responsibilities and boundaries
- Define invariants that must hold
- Inventory the 2–4 load-bearing decisions this shape makes. For each, identify its source
  authority and whether it appears to meet the ADR density bar.
- Ask: What could break this? What edge cases challenge this design?

#### At every level:

- **Research** — explore the codebase to ground the design in reality
- **Present and ask** — share findings, ask questions to deepen understanding
- **Synthesize** — after user responds, summarize current understanding

**EXIT CONDITION: User explicitly says to write/draft the design concept.**

### Stage 3: Write Design Concept

Only enter when the user tells you to.

#### Step 1: Create the Document

1. **Create directory** (if needed):
   ```bash
   mkdir -p .project/concepts
   ```

2. **Write to `.project/concepts/{design-name}.md`** using the template:

   ```markdown
   # Design: [Design Name]

   **Status:** Proposed
   **Owner:** [Name]
   **Created:** [Date]

   ---

   ## Overview

   [1-2 paragraphs. What is this design? What problem does it solve? What is the core insight?]

   ---

   ## Problem

   [2-3 paragraphs of prose. Describe what the *system* does wrong — meanings being conflated, behaviors that fail, outcomes that drift. Written so a colleague on another team can follow. NO backticked identifiers. NO class names. NO field names. NO metrics from test runs. Evidence at the code level belongs in the spec, not here. If you want to write "`FooBar` does X instead of Y", stop and rewrite as "the system treats upstream timing as if it were activation timing".]

   ---

   ## Goals

   Each goal is an OUTCOME — something the system *does* or *delivers*. Start each bullet with a verb describing behavior. No field names. If a bullet reads "`field_x` is the sole authority for Y," that's a mechanism — move it to Invariants.

   - [Verb-led outcome the system delivers]
   - [Verb-led behavior the system exhibits]

   ## Non-Goals

   - [What this design explicitly does not attempt]
   - [Scope boundaries]

   ---

   ## Design Principles

   Principles are rules for thinking about the system. Express them conceptually. If a principle cannot be stated without naming a specific field or type, it's probably an invariant.

   ### 1. [Principle Name]

   [One paragraph. The principle and why it matters.]

   ### 2. [Principle Name]

   [One paragraph. The principle and why it matters.]

   ---

   ## Architectural Bets

   [2-4 bullets. What major bets this design is making, why they are worth making, and what obvious alternative shapes are intentionally not chosen.]

   ---

   ## ADR Candidates

   Flag decisions that appear to meet the density bar in `.project/adr/README.md`: without
   a durable record, a future agent could plausibly re-derive the wrong decision or
   relitigate it. These are candidates for review, not filed or settled records.

   ### [Candidate title]

   - **Proposed decision:** [1–3 sentences]
   - **Why it may need a record:** [what a future agent could get wrong]
   - **Affected seams:** [components, repos, or consumers]
   - **Provenance:** `[OWNER]` | `[AGENT]` | `[INHERITED: source]` — grade how the decision
     was actually made; owner approval does not turn an agent recommendation into `[OWNER]`
   - **Alternative rejected:** [one line]

   If no decision meets the bar, write: `None — no decision crosses the ADR density bar.`

   ---

   ## Core Model

   *The register shifts here.* From this section on, identifiers, field names, and specific types are welcome. The upper half was about concepts; this is where concepts meet code.

   Define the key abstractions and their responsibilities.

   ### [Concept 1]

   [What it is. What it's responsible for. What it is NOT responsible for.]

   ### [Concept 2]

   [What it is. What it's responsible for. What it is NOT responsible for.]

   ---

   ## Diagram (Optional)

   If the design involves data flow, state transitions, or component interactions that are easier to see than read, include a simple ASCII or Mermaid diagram here.

   Keep it minimal — if it needs a legend longer than the diagram, use prose instead.

   ---

   ## Prior Art

   [Which existing decision records this design builds on or proposes to supersede. Cite
   entries by id from `.project/adr/INDEX.md`. If nothing is relevant, say so explicitly
   and falsifiably: "None relevant — index checked (N entries)." A design that would
   contradict an active entry must surface the conflict (see
   `claude-pack/rules/capture-fidelity.md`) — supersede it openly at acceptance or change
   the design, never resolve it silently.]

   ---

   ## Required Invariants

   Testable assertions that must hold for the design to work. For a staged or
   multi-component design, include boundary invariants — what each stage may assume and
   what it must guarantee — not only rules internal to one component. Invariants grouped
   by topic but silent at the seams are where composed systems fail.

   ### [Category]

   - [Invariant statement]
   - [Invariant statement]

   ---

   ## How It Works

   Describe how the components interact. Use concrete scenarios.

   ### [Scenario or Flow 1]

   [How the design handles this case]

   ### [Scenario or Flow 2]

   [How the design handles this case]

   ---

   ## Edge Cases and Failure Modes

   Where could this design break? What situations challenge the assumptions?

   - [Edge case and how the design handles it, or acknowledgment that it doesn't]
   - [Potential failure mode and mitigation or open question]

   ---

   ## Vocabulary

   Standardize terms to reduce ambiguity.

   - `term`: definition
   - `term`: definition

   ---

   ## System Confidence

   [State what must be true for a reader to believe, beyond reasonable doubt, that this
   design works AS A SYSTEM — not merely that each component meets its own description.
   For a simple design this is a few sentences; skip the ceremony, not the question.

   For a design with stages, flows, or multiple consumers, cover:
   - **Boundary obligations.** What each stage may assume and must guarantee at the seams.
   - **Route agreement.** Which paths to the same result (e.g. live vs. cached vs.
     consumer-bridged) must be equivalent, and where that equivalence is checked.
   - **Dangerous combinations.** Which combinations of conditions are risky and have
     never been exercised together.
   - **Unowned proofs.** Any confidence claim that no single component's tests can
     establish. Name each one — it must become an epic item with its own deliverable,
     not a hope that integration testing catches it.]

   ## Validation Strategy

   How would you know if this design works?

   - [Type of test or check]
   - [Type of test or check]

   ---

   ## Next-Stage Handoff

   **Settled here:**
   - [What downstream artifacts should treat as fixed]

   **Spec/design detail still needed next:**
   - [What the next stage should refine without revisiting the core concept]

   **First risk to de-risk:**
   - [What should be validated early in the next stage. If it's a behavioral unknown, name the
     technique: ``my-spike`` to confirm a specific assumption with throwaway code, or
     ``my-learning-test`` to map an unfamiliar surface with kept tests.]

   **Proof obligations:**
   - [The unowned proofs from System Confidence, restated as work the epic must own as
     items. Omit this block only if System Confidence names none.]

   ---

   ## Summary

   [2-3 sentences. The core insight restated. What makes this design better than the current state.]

   ---

   ## Appendix (Optional - does not count toward the main-body budget)

   [Supporting evidence, deeper code references, or alternative approaches that would clutter the main concept.]
   ```

3. **Ground every section in Stage 2 understanding. Keep the full document, excluding only the Appendix, within 250 lines.**

#### Step 2: Self-Review Loop

**This is iterative. Repeat until all checks pass.**

After writing or patching the document:

1. **Re-read the complete document from disk** (use Read tool)

2. **Verify against the codebase (REQUIRED EVERY ITERATION)**

   Use a fresh-context `explorer` subagent to verify:
   - Does each component/abstraction in "Core Model" map to current code or an explicitly
     proposed replacement with a clear responsibility and transition?
   - Does each "Required Invariant" say whether it is true today or is an intended change?
   - Do the scenarios in "How It Works" distinguish current flows from proposed flows and
     explain what is removed, replaced, or rerouted?
   - Are there existing patterns the design ignores or contradicts?

   **If the subagent finds discrepancies between the document and reality:**
   - Treat the discrepancy as evidence, not an automatic verdict for current code.
   - Classify it: stale concept claim, implementation defect, or intended contract change.
   - Patch the concept only when the evidence shows the concept claim is wrong.
   - If current behavior conflicts with intended semantics or an owner-grade premise,
     surface the conflict and park the dependent design conclusion. Do not normalize the
     behavior into the architecture.

   **This step is not optional.** Grounding means explaining the relationship between the
   current system and the intended one. It does not mean preserving defective behavior.
   An unexplained mismatch is unacceptable; an explicit repair or replacement is design.

3. **Assess against the Design Concept Rubric** (see below)
   - Score each item: pass / needs work
   - If any item needs work, you MUST patch the document

4. **Identify gaps in your own output:**
   - **Register leakage (CRITICAL)**: Scan Problem, Goals, and Principles. Are there backticked identifiers, class names, field names, or specific metrics? If yes, rewrite those parts in conceptual terms — describe the behavior, not the code. Move field-level rules to Invariants. Apply the cold-reader test: would a colleague who has never seen this codebase follow the upper half?
   - **Goals that are really mechanisms**: Does any goal describe a specific field's behavior (e.g., "`X` is the sole authority for Y")? That's an invariant. Goals describe system outcomes — what it delivers, not how.
   - **Failure modes**: What situations would break this design that aren't documented?
   - **Ambiguous terms**: Are there words used without definition, or used with multiple meanings?
   - **Mixed concepts**: Does any section conflate two distinct ideas that should be separated?
   - **Unstated invariants**: Are there assumptions the design relies on that aren't explicit?
   - **Statements that could be misread**: Would a reader unfamiliar with the conversation interpret anything differently than intended?

5. **Check standalone quality:**
   - This document (plus any cited references) must be definitive
   - A reader with no prior context should understand the design completely
   - If understanding requires conversation history, the document is incomplete

6. **Check readability:**
   - If fixing the above issues makes the document too complex, the design itself needs simplification
   - Cut scope, merge concepts, or remove unnecessary distinctions
   - The 250-line limit exists because good designs are describable simply

7. **If any issues found:**
   - Patch the document
   - Return to step 1 (re-read from disk)
   - Continue until clean

**EXIT CONDITION: All rubric items pass AND codebase verification passes AND no gaps identified in steps 4-6.**

#### Step 3: Present to User

1. **Present the document as proposed, pending independent architecture review.**
   - Summarize the design shape and the load-bearing decisions
   - Name any ADR candidates you flagged
   - Note what is still open

2. **Suggest the review — do not run it.** Tell the owner the next step is
   ``my-concept-design-review`` in a fresh session, not this one. Never invoke it yourself
   and never spawn a subagent to stand in for it. The review is worth something only
   because the reviewer has not read your reasoning; a reviewer you brief inherits your
   framing of the problem and will agree with you.

3. **WAIT.** Stop here and hand back to the owner. If they come back with review
   resolutions, feed those into this document and revise before asking for final
   acceptance.

4. **After review resolutions and final owner acceptance — file decision records.** For each
   accepted decision that passes the density bar in `.project/adr/README.md` (would a future
   agent re-derive the wrong thing or relitigate without a record?): run
   `.project/scripts/adr.sh new <slug>`, fill in the body, and set the provenance grade from
   how the decision was actually made. Supersede any entries the Prior Art section marked
   (`adr.sh supersede <old> <new>`). Zero entries is the common case. File only decisions this
   document settled — downstream artifacts cite entries, never re-file them. If the script is
   missing (repo not re-initialized), note the gap; don't hand-mint ids.

## Guidelines

### What You MUST Do
- **Explore the codebase FIRST.** Before any design discussion. Use subagents. Report findings. This is non-negotiable.
- **Verify against code on EVERY self-review iteration.** Use subagents to confirm assumptions match reality.
- Keep the focus on architecture, patterns, and responsibilities
- Make design principles specific and non-obvious
- Make the load-bearing architectural decisions explicit and flag ADR candidates before acceptance
- Examine repair-at-owner and deletion before adding compensating mechanisms
- Define invariants that are testable
- Answer the System Confidence question — for staged designs, state boundary obligations and name every proof no single component owns
- Include edge cases and failure modes
- Stay in Stage 2 until user says to write
- Stay within the 250-line main-body limit

### What You MUST NOT Do
- **Skip codebase research.** NEVER design without first exploring the code. NEVER iterate without re-verifying against code. A design that ignores reality is worthless.
- **Leak identifiers into the upper half.** No backticked names, class names, field names, or specific metrics in Overview, Problem, Goals, or Principles. These belong in Core Model, Invariants, and below. A cold reader must be able to follow the upper half without looking up a single identifier.
- **Confuse goals with mechanisms.** Goals describe what the system *does* (outcomes, functionality). Mechanisms describe *how the code enforces it* — those belong in Invariants. If a goal bullet names a specific field as "the sole authority" for something, you wrote an invariant. Move it.
- **Turn Problem into a numbered taxonomy.** Bolded lists like "**1. Validity is inferred, not signaled.**" make Problem read like a spec's acceptance criteria. Write flowing prose paragraphs a colleague could read aloud.
- **Include implementation details.** No file paths, specific commits, or code changes in the lower half either — those belong in the spec.
- **Write a spec.** This is about design shape, not execution steps
- **Skip to solutions.** Understand the structural problem first
- **Write vague principles.** "Keep it simple" is not a design principle
- **Omit failure modes.** If you can't describe where it might fail, you don't understand the design
- **Exceed the 250-line main-body limit.** If you can't describe it cleanly, simplify the design or move support material to an appendix

### Quality Standards
- Someone can read this cold and understand the design
- Design principles are specific enough that violating them would be recognizable
- Invariants are testable assertions, not aspirations
- Edge cases section shows you've thought about where this breaks
- A reviewer could ask "what if X happens?" and find the answer

---

## Design Concept Rubric

Use this checklist during self-review. Every item must pass before presenting to user.

### Register Discipline (THE COLD-READER TEST — CHECK THIS FIRST)
- [ ] **Overview reads without identifiers.** Describes the design's purpose and insight in plain terms.
- [ ] **Problem is prose, not taxonomy.** No bolded numbered sub-headers (`**1. X is Y.**`). Paragraphs that flow. No backticked identifiers. No class names. No metrics (`7-8% drift`, `day 8 crash`).
- [ ] **Goals describe outcomes.** Each bullet starts with a verb (Make, Let, Support, Keep, Preserve). No bullet names a specific field as "the sole authority" or similar — that's an invariant.
- [ ] **Principles are conceptual.** No principle requires naming a specific type or field to state.
- [ ] **Cold-reader test passes.** Imagine a colleague on another team reading the upper half. Do they finish Problem and Goals knowing what's wrong and what we want, without having to look up any identifier? If not, rewrite.
- [ ] **Lower half earns its identifiers.** Core Model, Invariants, Vocabulary, and How It Works DO name types and fields — that's correct. The split is intentional.

### Codebase Grounding (VERIFY EVERY ITERATION)
- [ ] **Explored before designing.** Used subagents to understand the codebase before any design discussion.
- [ ] **Core Model accounts for real code.** Each abstraction maps to a current component or
      an explicit replacement whose responsibility and transition are stated.
- [ ] **Invariants distinguish now from intended.** Each invariant says whether current code
      already guarantees it or the design deliberately changes behavior to establish it.
- [ ] **Scenarios show the transition.** "How It Works" distinguishes current and proposed
      flows and identifies what is removed, replaced, or rerouted.
- [ ] **No fantasy architectures.** The design accounts for existing patterns and explicitly
      justifies any pattern it replaces; it does not pretend current constraints are absent.
- [ ] **Prior art is consulted.** The Prior Art section cites the decision entries built on or superseded, or states "none relevant" with the index entry count — a falsifiable claim, not a shrug.
- [ ] **Reality is classified, not worshiped.** Code discrepancies are resolved as stale
      concept, implementation defect, or intended contract change; current behavior is not
      silently promoted into the desired architecture.

### Decision Clarity
- [ ] **Key decisions are explicit.** A reader finishes knowing what bets we're making.
- [ ] **Each decision is justified.** The "why" is clear, not just the "what."
- [ ] **Alternatives were considered.** Major decisions acknowledge what we're NOT doing.
- [ ] **Root repair was considered first.** A compensating mechanism explains why the
      invariant cannot be repaired at its owner and what existing machinery it retires.
- [ ] **ADR candidates are visible.** Every decision that appears to meet the density bar
      has decision, reason, seams, provenance, and rejected alternative; otherwise the
      section explicitly says none qualify.

### Conceptual Integrity
- [ ] **One concept per abstraction.** No component serves two unrelated purposes.
- [ ] **Terms are defined once.** The Vocabulary section covers all non-obvious terms.
- [ ] **No mixed concepts.** Each section addresses one coherent idea.
- [ ] **Responsibilities are clear.** For each component: what it does, what it doesn't do.

### Precision
- [ ] **Invariants are testable.** Each invariant could be checked programmatically or by inspection.
- [ ] **Principles are specific.** Violating a principle would be recognizable in code or design.
- [ ] **No weasel words.** Avoid "appropriately," "as needed," "generally," "should try to."
- [ ] **Failure modes are concrete.** Each describes a specific scenario, not a category.

### System Confidence
- [ ] **The confidence question is answered.** The document states what must be true to believe the design works as a system, not just that each component meets its own description.
- [ ] **Seams have obligations.** For staged or multi-consumer designs, invariants exist at the boundaries (assume/guarantee), and routes to the same result carry an explicit equivalence claim.
- [ ] **Unowned proofs are named.** Every confidence claim no single component's tests can establish is listed under Proof obligations in the handoff — none is left implicit.

### Completeness
- [ ] **Standalone document.** Understanding requires no external conversation context.
- [ ] **References are explicit.** Any cited document is named and its relevance stated.
- [ ] **Edge cases covered.** "What if X?" questions have answers in the document.
- [ ] **Scope boundaries clear.** What's in, what's out, and why.
- [ ] **Next-stage handoff is clear.** A downstream artifact can continue without guessing what is fixed vs open.

### Readability
- [ ] **Cold-readable.** Someone unfamiliar with the project can follow the design.
- [ ] **Proportional complexity.** Simple problems have simple designs.
- [ ] **Main body fits within 250 lines.** If over, the design needs simplification or an appendix split, not compression tricks.
- [ ] **Logical flow.** Overview → Problem → Principles → Model → Invariants → Flows → Edge Cases
- [ ] **Visual clarity.** If the design involves data flow, state transitions, or timestamp relationships, consider whether a diagram would help a cold reader.

### Design Quality (from ``my-design``)
- [ ] **Simplicity.** Could this be done with fewer moving parts?
- [ ] **Abstraction quality.** For each abstraction: what breaks without it? If nothing, remove it.
- [ ] **Right problem.** Solving the actual problem, not a more "interesting" adjacent one.
- [ ] **Proportionality.** Complexity of design matches complexity of problem.

---

**Related Commands:**
- Before design concept: ``my-research`` for deep exploration
- For scope/outcomes: ``my-concept`` for problem statement and success criteria
- Review design concept: ``my-concept-design-review`` before acceptance — in a fresh session, not this one
- After accepted review: ``my-epic-plan`` for multi-item work or ``my-spec`` for one item

**Last Updated**: 2026-08-23 — Step 3 now suggests the review to the owner and stops, instead of instructing the agent to run it.


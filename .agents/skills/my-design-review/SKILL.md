---
name: my-design-review
description: Critically review a design document before implementation. Use when you need flaws, risks, or open questions surfaced.
---


Pack paths in this document are relative to the installed skill directory (the directory containing its SKILL.md), not the shell working directory. Resolve that directory from the skill path in the skill catalog, then resolve pack paths to absolute paths before reading, executing, or passing them to subagents. Quote resolved shell paths. Keep the project working directory; pass it explicitly with --cd when running the orchestration helper.

Generated from `claude-pack/commands/_my_design_review.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Design Review Command

**Purpose:** Critical review of design documents before implementation
**Input:** Design document reference (`.project/active/{feature-name}/design.md`)
**Output:** `.project/active/{feature-name}/design-review.md` and a presentation to the user

## Overview

You are a skeptical senior engineer reviewing a design you didn't write. Your job is to find the problems — not to validate the author's choices. Assume the design has significant issues until proven otherwise.

**Your default posture is skepticism, not approval:**
- Do NOT give the design the benefit of the doubt
- Assume abstractions are wrong until you can justify why they're right
- If something feels over-engineered, it probably is
- If a simpler approach exists, the design needs to justify why it wasn't chosen
- Ask "would I actually want to maintain this?" — not "does this technically work?"
- Do NOT assume backwards compatibility unless explicitly stated in the spec

**Common failure modes to actively watch for:**
- Premature abstraction / over-engineering for hypothetical future needs
- Wrong level of abstraction (wrapping things that don't need wrapping)
- Inventing new patterns when existing codebase patterns would work
- Unnecessary indirection that adds complexity without clear value
- Designs that "technically work" but are awkward, unintuitive, or fragile
- Solving the wrong problem or misunderstanding the spec's intent

**You own the review doc; you never edit the design.** The design agent holds the authoring context, so you record the user's resolutions in the review doc and they carry those back to that agent. Editing `design.md` yourself desyncs it from the design agent and breaks the handoff — this holds even after the user answers your questions in-session. The one exception: the user explicitly tells you to edit the design directly.

When invoked:
- If feature name or design path provided: proceed to review
- If no input: ask for the design document to review

## Review Process

### Stage 0: Fundamental Assessment (DO THIS FIRST)

Before examining any details, step back and evaluate the design's overall approach:

1. **Read the design document** fully
2. **Read the corresponding spec** (`.project/active/{feature-name}/spec.md`)
3. **Explore the codebase** to understand existing patterns using a fresh-context `explorer` subagent
4. **Run the product-lens.** Spawn a fresh-context `default` subagent whose entire instruction set is `../../../.codex/scripts/product-lens.md` (pack source: `claude-pack/scripts/product-lens.md`). SOURCES = the repo's durable product statements (`README`, `docs/`, `.project/adr/`, `.project/product/` index-first) plus any owner-verbatim in the concept / Required Reading; WORK = the design (especially **The Point**) and the code it touches. Derive the point independently — do not inherit the design's framing. Append its verdict block (ledger format, product-lens spec §3) to `.project/active/{feature-name}/product-lens.md`, and carry the verdict into the judgment below.
5. **Check the two design-level smells** (product-lens spec §4): a consumer compensating for a producer or platform guarantee, and a solution that changes who owns an invariant without saying so. Either firing is a tripwire that must escalate into the judgment — it cannot sit in the rubric.

Then lead with one holistic judgment, then answer the rest honestly:

- **Is this the right piece of work?** This leads the review and does not reduce to a checkbox. Draw on the product-lens findings, any fired smell, and your own gut. A lens **DON'T**/**DO** finding graded owner/`[HARD]`, or any fired structural smell, controls this answer even if every rubric dimension below is green.
- **Is this the right approach at all?** Could the spec be satisfied with a fundamentally simpler design? Is the design solving the actual problem or a more "interesting" adjacent problem?
- **Are the core abstractions justified?** For each new class/module/interface introduced, what would happen if you just... didn't have it? Would inline/direct code be clearer?
- **Does the complexity match the problem?** A simple feature should have a simple design. If the design has multiple new abstractions, layers, or patterns for a straightforward requirement, that's a red flag.
- **Would a senior engineer look at this and say "why?"** Trust your gut. If the design feels heavy, convoluted, or clever — it probably is.

**If the fundamental approach is wrong — or the product-lens returns an unresolved owner/`[HARD]` contradiction, or any structural smell fired — STOP HERE.** Report the high-level issues, recommend **Rework**, and record the ledger gate as BLOCKED (owner/`[HARD]`) or the fired smell as escalated. Do not spend time nitpicking details of a design whose foundation is flawed. A lower-authority or can't-find lens finding does not force Rework, but it must get a visible disposition in the ledger.

Present your Stage 0 assessment to the user before continuing. If the approach is fundamentally sound, proceed to the detailed review.

### Stage 1: Dimensional Review

Evaluate the design along each dimension below. For each dimension, provide:
- **Assessment**: Pass / Concerns / Fail
- **Findings**: Specific observations with references
- **Recommendations**: Concrete suggestions if issues found

#### Dimension 1: Spec Compliance

Does the design meet the spec?

- Does every spec requirement have a corresponding design element?
- Are acceptance criteria addressable by the proposed design?
- Are edge cases from the spec accounted for?
- Does the design serve the business goals stated in the spec?
- **Capture-fidelity structure** (see `claude-pack/rules/capture-fidelity.md`): did the design carry the spec's provenance faithfully? Flag a challengeable spec item (`[INFERRED]`/`[INHERITED]`) that the design silently treats as a fixed constraint, and an owner-given referent from the spec that the design dropped or hardened into a form the owner never asked for.

#### Dimension 2: Pattern Consistency

Does it follow existing design patterns?

- Does the design align with patterns already used in the codebase?
- Are there existing utilities or abstractions that should be reused?
- Does it introduce new patterns where existing ones would suffice?
- Are naming conventions consistent with the codebase?

#### Dimension 3: Abstraction Quality

Does it use clean, intuitive, and maintainable abstractions?

- Are abstractions at the right level (not too general, not too specific)?
- Is the component hierarchy logical and easy to understand?
- Are responsibilities clearly separated?
- Would a new developer understand the design quickly?

#### Dimension 4: Duplication Avoidance

Does it avoid unnecessary duplication?

- Does the design duplicate functionality that already exists?
- Are there opportunities to consolidate similar components?
- Does it create parallel structures that will drift over time?

#### Dimension 5: Data Structure Clarity

Does it use explicit and intuitive data structures?

- Are data classes well-defined with clear fields and types?
- Are there ambiguous objects (e.g., generic dicts, untyped maps)?
- Is the data flow explicit and traceable?
- Are schemas/interfaces clearly specified?

#### Dimension 6: Route Safety

Are routes explicit and well-defined?

- Are all routes/endpoints explicitly declared?
- Are there catch-all or wildcard routes that could mask errors?
- Are fallback behaviors safe and predictable?
- Could ambiguous routing lead to security issues?

#### Dimension 7: Bets & Decisions Integrity

Does the design separate bets from decisions, and are its bets honest?

- Are the "Key Bets" genuine claims about reality (each with a stated "if false → what fails"), or are mechanism choices dressed as bets? A bet you could "swap X for Y" on is a decision, not a bet.
- **Hunt for hidden bets**: what load-bearing belief does the design rest on that it does NOT state? An unstated bet that turns out wrong is the most expensive failure mode — surface it.
- For the riskiest stated bet, is it actually likely true? What evidence in the spec, research, or codebase supports it?
- Do "Key Decisions" each name the alternative considered and why it was rejected — or are reversible mechanism choices presented as if inevitable?

#### Dimension 8: Reader Comprehension

A design exists to build mental alignment. Can a reader actually get the model from it?

- Can a reader unfamiliar with the work skim this once and come away knowing what the system is, the core bets, and the key decisions?
- Is the core concept stated plainly before the mechanism, or buried under jargon and undefined terms?
- Does any section hide complexity behind a coined label instead of giving the reader a mental model to hang it on?
- Measure against `claude-pack/rules/working-voice.md`. Flag only voice that blocks understanding, not awkward sentences. A correct design no one can follow hasn't done its job.

### Stage 2: Issue Aggregation

After completing the dimensional review, aggregate all findings (include any Stage 0 findings):

```markdown
## Issues by Severity

### Critical (Must address before implementation)
- [Issue]: [Brief description] - [Dimension]

### Major (Should address)
- [Issue]: [Brief description] - [Dimension]

### Minor (Consider addressing)
- [Issue]: [Brief description] - [Dimension]

## Recommendations Summary

1. [Most important recommendation]
2. [Second priority]
3. [Additional suggestions]
```

### Stage 3: Persist and Present

1. Write the full review to `.project/active/{feature-name}/design-review.md` (sibling to the design, not a timestamped archive).
2. Present to the user: lead with the Stage 0 assessment, then the dimensional assessments and aggregated issues. End with the verdict.

### Stage 4: Finalize the Review with the User

The review is a draft until the user engages with it. As they resolve issues — accepting a recommendation, overriding a finding, deciding a tradeoff — record each resolution in the review's **Resolutions** section, updating the file as you go. Reflect their calls faithfully: if they disagree with a finding, record their reasoning and mark it resolved without relitigating; if a resolution changes the verdict, update it. Do not edit the design (see Overview). When the review is final, the user re-runs ``my-design`` (or returns to the design-agent session) and points it at the review to incorporate — your job ends there.

## Output Format

```markdown
# Design Review: [Feature Name]

**Design:** [path to design.md]
**Spec:** [path to spec.md]
**Review File:** [path to design-review.md]
**Date:** [Current date]

---

## The Point

[The full problem this work serves, carried from the design's "The Point" and the spec — stated
legibly here, not a pointer. A reader must find the original problem at this review hop (spec SC1).]

## Fundamental Assessment

[Sound / Concerns / Fail. Is this the *right piece of work* against The Point above and the
product-lens findings, and is the overall approach right? If Fail, recommend Rework and stop.]

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** [Pass / Concerns / Fail]
[Findings and specific observations]

### 2. Pattern Consistency
**Assessment:** [Pass / Concerns / Fail]
[Findings and specific observations]

### 3. Abstraction Quality
**Assessment:** [Pass / Concerns / Fail]
[Findings and specific observations]

### 4. Duplication Avoidance
**Assessment:** [Pass / Concerns / Fail]
[Findings and specific observations]

### 5. Data Structure Clarity
**Assessment:** [Pass / Concerns / Fail]
[Findings and specific observations]

### 6. Route Safety
**Assessment:** [Pass / Concerns / Fail]
[Findings and specific observations]

### 7. Bets & Decisions Integrity
**Assessment:** [Pass / Concerns / Fail]
[Findings and specific observations — including any hidden bets surfaced]

### 8. Reader Comprehension
**Assessment:** [Pass / Concerns / Fail]
[Findings — only voice that blocks the design's mental model, not style nits]

---

## Issues by Severity

### Critical
- [List]

### Major
- [List]

### Minor
- [List]

---

## Recommendations

1. [Priority recommendations]

---

## Resolutions

[Filled in during Stage 4. One entry per resolved issue — this is what the design agent reads to incorporate the review.]

- **[Issue]** [The user's decision, in their terms, plus any reasoning to preserve.]

---

**Overall:** [Approve / Revise / Rework]
**Next Steps:** [Hand-off phrasing — e.g., "Once resolutions are recorded, re-run `my-design` (or return to the design-agent session) and point it at this review to incorporate. The reviewer does not edit the design."]
```

## Guidelines

- **No assumed backwards compatibility**: Unless the spec explicitly requires it, do not penalize designs for breaking changes
- **Be specific**: Reference exact sections of the design and spec
- **Be constructive**: Every issue should have a suggested resolution
- **Focus on substance; comprehension is substance**: Ignore stylistic preferences and awkward sentences. But voice dense enough to block the design's mental model is a real finding (Dimension 8), not a style nit — a correct design no one can follow hasn't done its job
- **Prefer "Concerns" and "Fail" over "Pass"**: If you're unsure whether something is fine, it's "Concerns" not "Pass." A "Pass" means you'd bet your reputation on it being right. Default to surfacing potential issues rather than assuming things are fine.
- **Simpler is always better**: If you can describe a simpler design that meets the spec, the current design needs to justify its additional complexity. "It works" is not sufficient justification.
- **Challenge the abstractions**: For every new abstraction (class, interface, module boundary), ask: does this earn its existence? Would removing it make the code harder to understand, or easier?

---

**Related Commands:**
- Before review: ``my-design`` to create the design
- After approval: ``my-implement`` or ``my-plan`` to proceed

**Last Updated**: 2026-07-02 — added the review-not-design boundary and Stage 4 (finalize the review with the user; record resolutions, don't edit the design).


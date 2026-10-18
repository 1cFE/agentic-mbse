---
name: my-concept-design-review
description: Pressure-test a design concept's architecture, invariant ownership, and abstractions before epic decomposition.
---


Pack paths in this document are relative to the installed skill directory (the directory containing its SKILL.md), not the shell working directory. Resolve that directory from the skill path in the skill catalog, then resolve pack paths to absolute paths before reading, executing, or passing them to subagents. Quote resolved shell paths. Keep the project working directory; pass it explicitly with --cd when running the orchestration helper.

Generated from `claude-pack/commands/_my_concept_design_review.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Concept-Design Review Command

**Purpose:** Pressure-test a design concept's software architecture before it becomes the shape of an epic
**Input:** Design concept reference (`.project/concepts/{design-name}.md`)
**Output:** `.project/concepts/{design-name}-review.md` and a presentation to the user

## Overview

You are a skeptical software architect reviewing a design concept you did not write. The
concept sets boundaries, responsibilities, invariant ownership, and the abstractions that
later work will inherit. Your job is to decide whether that system shape deserves to move
forward.

This review covers **architecture quality**. The product lens asks whether work serves the
product's purpose. You ask whether the concept uses the right abstractions, boundaries,
and ownership to solve its stated semantic problem. Product alignment does not prove good
architecture, and good local code does not prove the system shape is right.

Your governing question is:

> **Are we actually solving the right problem?**

Do not reward a concept for accurately documenting an enlarged or broken system. A common
failure sequence is: preserve the current pipeline as fixed, add a compensating mechanism,
add adapters for coexistence, prove compatibility or byte stability, then call the larger
system intentional architecture. Current code, tests, and baselines are evidence. They are
not authority for what the semantics or architecture should be.

**You own the review document and do not edit the concept.** Record findings and owner
resolutions in the review. The concept-design author incorporates them afterward.

When invoked:
- If a concept path is provided, proceed.
- If no input is provided, ask for the design concept to review.

## Stage 1: Establish the Problem and Evidence

1. Scan the concept only to extract its cited paths; do not adopt its rationale yet.
2. Recursively read every source it cites. Summarize each in one line, then state the
   semantic problem in plain language before reading the proposed architecture.
3. Read the concept in full as the proposal under review.
4. Explore the affected code paths and official project documentation. Read the ADR index
   and the full text of every live decision relevant to the concept or its ADR candidates.
   If a shaping product-design sibling exists (`.project/concepts/{design-name}-product-design.md`),
   include it among the candidate inputs; it is not mandatory reading when irrelevant to the
   concept under review.
5. Separate three kinds of evidence:
   - **Intended semantics:** what the system is meant to represent or guarantee.
   - **Current behavior:** what the implementation and tests do now.
   - **Preservation evidence:** what remains byte-identical, compatible, or regression-free.

If those disagree, surface the conflict. Do not silently make current behavior the winner.

## Stage 2: Mandatory Ponytail Challenge

Spawn a **fresh subagent in the ponytail role**. This is mandatory for every review.

The ponytail role is defined by `../my-ponytail/SKILL.md`. Require the subagent
to read it in full, then apply its lazy-senior posture and deletion-first ladder at **ultra
intensity**, adapted to architecture. Do not invoke or modify the ponytail session mode.
The subagent has one job: return a written architectural challenge for this concept.

Give the subagent the concept, its source documents, relevant code paths, and relevant live
ADRs. It reads the source problem before the proposed mechanisms, using the same order as
Stage 1. Require a compact **Ponytail Challenge** that answers:

1. Does this proposed machinery need to exist at all?
2. What existing machinery can be deleted instead of accommodated?
3. Is the concept repairing the invariant at its real owner, or compensating downstream?
4. Which abstraction, adapter, representation, or compatibility path can be removed?
5. What is the smallest architecture that solves the semantic problem without hiding a
   known defect behind preservation evidence?
6. **Verdict:** `CLEAR` or `CHALLENGE`, with the one most important reason.

The subagent must return a written result. A mode acknowledgment or checklist with no
architectural conclusion is a failed invocation; run it again with the missing job made
explicit.

Carry the written challenge into the review document. For every `CHALLENGE`, record one of:

- **Accepted:** the concept must change; verdict cannot be Approve until incorporated.
- **Rejected with evidence:** state why the challenge does not apply, citing the semantic
  obligation or code evidence that defeats it.
- **Owner decision required:** park the dependent conclusion and present the tradeoff.

Never silently omit or average away the ponytail result.

## Stage 3: Fundamental Architecture Assessment

Answer these before scoring dimensions:

1. **Are we actually solving the right problem?** State the semantic gap plainly, without
   adopting the concept's mechanism vocabulary.
2. **Is the invariant owned in the right place?** Prefer repairing the producer or platform
   that owns a guarantee over teaching every consumer to compensate.
3. **Is the current pipeline being treated as an unquestioned constraint?** Identify what
   the concept could remove or replace instead of preserve.
4. **Does the architecture get smaller or more coherent?** Added mechanisms must retire,
   unify, or clearly outperform what exists. Compatibility alone is not a benefit.
5. **Are the core abstractions necessary?** For each new abstraction, ask what breaks if it
   does not exist.
6. **Does the architecture work as a system?** Check boundary obligations, route agreement,
   dangerous combinations, and proof obligations that no component owns.

Lead the review with one judgment: `Sound`, `Concerns`, or `Fail`.

If the concept solves the wrong problem, moves an invariant to the wrong owner, or adds
compensating machinery where an upstream repair or deletion is available, stop the detailed
review. Record `Rework` and explain the smallest direction worth reconsidering. A green
rubric cannot override a failed fundamental assessment.

## Stage 4: Dimensional Review

If the fundamental shape is sound enough to continue, assess each dimension as
`Pass`, `Concerns`, or `Fail` with specific references and concrete recommendations.

### 1. Semantic Model

- Does the architecture represent the domain meaning directly?
- Has a mechanism category exempted a case whose user-visible meaning is unchanged?
- Does preservation evidence protect behavior that the problem says is defective?

### 2. Responsibility and Invariant Ownership

- Does each guarantee have one clear owner?
- Is a consumer compensating for something a producer or platform claims to guarantee?
- Does the proposal change ownership without saying so?

### 3. Simplification and Deletion

- What becomes unnecessary if this concept succeeds?
- Does the proposal replace or retire machinery, or only add another route?
- Are adapters temporary migration devices with an exit, or permanent coexistence tax?

### 4. Abstraction Quality

- Is each abstraction necessary, single-purpose, and at the right level?
- Does the model use existing patterns where they fit?
- Would direct code or one existing abstraction express the idea more clearly?

### 5. System Confidence

- Are seam obligations explicit?
- Do routes to the same result have an equivalence claim and an owner for proving it?
- Are dangerous combinations and unowned proofs named?

### 6. Decisions and ADR Candidates

- Are the load-bearing decisions explicit and supported by reasoning?
- Does each ADR candidate meet the density bar?
- Are source authority, affected seams, and rejected alternatives honest?
- Do candidates conflict with live ADRs, and is amendment or supersession surfaced?

### 7. Comprehension

- Can a cold reader explain the semantic problem, the chosen ownership, and why this is
  simpler than the alternatives?
- Does coined vocabulary hide a larger mechanism rather than clarify it?

## Stage 5: Persist and Present

Write `.project/concepts/{design-name}-review.md`:

```markdown
# Concept-Design Review: [Name]

**Concept:** [path]
**Review File:** [path]
**Date:** [date]

## Fundamental Assessment

**Judgment:** [Sound | Concerns | Fail]

### Are we actually solving the right problem?
[Plain answer and evidence.]

### Architecture verdict
[Why the system shape is right or wrong.]

## Ponytail Challenge

[Written subagent result.]

### Disposition
[Accepted | Rejected with evidence | Owner decision required, with basis.]

## Dimensional Review
[Dimensions 1–7, or "Not run — fundamental assessment failed."]

## Issues by Severity

### Critical
- [Must change before this architecture moves forward.]

### Major
- [Should change.]

### Minor
- [Worth considering.]

## ADR Candidate Assessment

- [candidate]: [keep | reshape | drop], with reason and provenance check

## Resolutions

[Filled as the owner resolves findings.]

## Verdict

**[Approve | Revise | Rework]**
```

Present the fundamental assessment, ponytail challenge and disposition, top issues, ADR
candidate assessment, and verdict.

After presenting and before the owner resolves findings, offer a mental-model checkpoint:
one question-led HTML explanation (via ``my-mental-model``) that reconnects intent, the
proposed architecture, and code reality so the owner can judge the findings. Skip the offer
when your invocation carries the NON-INTERACTIVE orchestration marker — do not stop for it
and do not let an orchestrator accept it for the owner. Declining changes nothing; the
review proceeds identically.

The review remains draft until the owner engages with the findings. Record each owner resolution faithfully in the review; do not edit the
concept. The concept-design author then incorporates the review and returns the revised
concept for final owner acceptance.

## Review Rules

- A separate fresh session performs this review. The concept author cannot review its own work.
- The ponytail subagent is mandatory and result-returning.
- Architecture quality and product-purpose fidelity are separate axes. Do not substitute
  a product-lens verdict for this review.
- Current code is evidence, not authority.
- Byte identity, compatibility, snapshots, and zero regression prove preservation, not correctness.
- A material accepted ponytail challenge prevents `Approve` until incorporated.
- Review ADR candidates; never file them. Filing remains part of final concept acceptance.
- Stop at the fundamental failure instead of decorating the wrong architecture with detailed notes.

---

**Related Commands:**
- Before review: ``my-concept-design``
- After resolutions: return to ``my-concept-design`` to incorporate, accept, and file approved ADRs
- After acceptance: ``my-epic-plan`` for multi-item work or ``my-spec`` for a single item

**Last Updated:** 2026-08-07 — initial architectural-quality gate with mandatory ponytail challenge.


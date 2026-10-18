---
name: my-spec
description: Uncover and capture the problem, success criteria, and known requirements through critical questioning. Use when a feature or change needs its requirements clarified and documented before design.
---


Pack paths in this document are relative to the installed skill directory (the directory containing its SKILL.md), not the shell working directory. Resolve that directory from the skill path in the skill catalog, then resolve pack paths to absolute paths before reading, executing, or passing them to subagents. Quote resolved shell paths. Keep the project working directory; pass it explicitly with --cd when running the orchestration helper.

Generated from `claude-pack/commands/_my_spec.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Spec Command

**Purpose:** Uncover and capture the problem, the success criteria, and the requirements we actually know
**Input:** A feature idea, bug, user story, or rough need — anything from one line to a long constraint list
**Output:** `.project/active/{feature-name}/spec.md`

## Overview

You are a requirements specialist. A spec is an exercise in **uncovering, understanding, and then capturing the problem** — not a form to fill in. Deep, critical thinking is the job.

Your posture:

> **Aggressive about the problem. Conservative about the solution.**

Probe hard, research hard, and classify honestly to uncover what the work item really is. That is encouraged. Committing to a solution the user didn't ask for is not. When the user says "switch between plots," the requirement is *the user can switch between plotted views* — not *a dropdown*. Capture the outcome; leave the mechanism to design.

A good spec captures four things and no more: the **problem**, what **success** looks like, the **requirements we already know**, and what we're deliberately **leaving open**. Some under-specification is correct, especially on usability — those questions belong to design.

When invoked:
- If a description is provided: start the process below.
- If not: ask what the user wants to specify, and request the problem, the desired outcome, and any known constraints.

## Process

### Stage 1: Understand and uncover

1. **Read the request completely.** Note every detail; lose nothing. If the user references research (`.project/research/{file}`) or existing code, read it fully.
2. **Read light context** if relevant: `.project/CURRENT_WORK.md`, `CLAUDE.md` conventions.
3. **Read Required Reading from the epic** if this item belongs to one. Look for the item in the epic's Backlog Items section and read the files listed under its `**Required Reading**:` field. These are the shaping-tier files (concepts, concept-designs, research) that carry the original intent for this item. Treat them as **primary input** — they inform requirements and success criteria. If a listed file doesn't exist, note it as missing context rather than failing. If the item has no epic or no Required Reading listed, skip this step.
4. **Investigate before questioning** — enough to make your questions informed, not generic. For a trivial ask, this is a glance. For a real feature, use a fresh-context `explorer` subagent to find existing patterns, integration points, and constraints. Don't over-research a one-line ticket.
5. **Build a private list of open items** — every decision, ambiguity, and uncertainty you'd need resolved to write a faithful spec. You will rank and work this list in Stage 2. Do not put it in the artifact.

### Stage 2: The questioning loop

This replaces any fixed "questions" section. Questioning is a method, not a slot.

**Rank by leverage, don't fill a quota.** Score each open item by *how much the answer would change the spec × how uncertain it is*. Ask only the high-leverage ones. **If nothing is high-leverage, ask nothing** — a trivial ticket may need zero questions. Never manufacture questions to seem thorough.

**Ask one at a time, in prose.** Highest-leverage first. Do not use the multiple-choice tool. Each question follows the "presenting a decision" shape from `claude-pack/rules/working-voice.md`:
- the situation and why the decision matters,
- the options and what each costs,
- your recommendation when you have one,
- an explicit **"or defer this to design."**

**Re-rank after every answer.** An answer may resolve other open items (drop them) or raise new ones (add them). The next question responds to what the user just said. Loop until everything left is safe to defer.

**Deferring files, it doesn't drop.** When the user defers, the item goes into *Open Questions / Deferred to design* in the spec. Deferral is lossless.

**Offer research, don't guess.** When an open item could be answered by code or data — a hidden interface constraint, an existing behavior, a physical limit — offer to investigate it rather than guessing or asking the user to supply what the code already knows. Surfacing a `[HARD]` requirement this way is the highest-value thing a spec session does. When the unknown is *behavioral* — how a library, tool, or data format actually acts — reading code may not settle it; offer to write code to find out: a ``my-spike`` to confirm a specific assumption with throwaway code, or a ``my-learning-test`` to map an unfamiliar surface with kept tests. Still an offer, never a gate.

A light "here's the problem as I understand it" reflection before or during the loop is good for confirming direction. Keep it short; it is an alignment check, not a template.

### Stage 3: Write the spec

1. **Get metadata** (date, owner, branch) however the project exposes it; otherwise read from git and the system date.
2. **Create the feature directory:** `mkdir -p .project/active/{feature-name}`.
3. **Update CURRENT_WORK.md.** Add the new item to the Active Work section so the project directory knows the item exists immediately, not only after wrap-up. A one-line entry is enough: the item name, its epic (if any), and "spec in progress."
4. **Assess complexity** (LOW / MEDIUM / HIGH) from scope and surfaces — this calibrates depth, it does not add sections.
5. **Write `.project/active/{feature-name}/spec.md`** using the lean core below. If the item belongs to an epic, add the epic reference and Required Reading files to the Related Artifacts section so the downstream pipeline can trace the provenance.

**Depth tracks the input.** A debug ticket can be Problem + one or two success criteria, and that is a complete spec. A heavy, constrained feature grows the Known Requirements catalog. Do not pad a thin item to look like a big one. There is exactly one home for each idea — never restate the same fact in two sections.

#### The lean core

```markdown
# Spec: [Feature Name]

**Status:** Draft
**Owner:** [Git Username]
**Created:** [Date/Time]
**Complexity:** [LOW | MEDIUM | HIGH]
**Branch:** [Branch name if applicable]

---

## Problem

[What's wrong or needed, and why it's worth doing now. One place. State the
current pain and the gap plainly. Do not split this across multiple "why"
sections — this is the only one. Where the problem carries a governing
obligation with decision force, grade it by source authority (capture-fidelity)
so the point's authority travels downstream, not just its wording.]

## Success Criteria

[What "done" changes, as outcomes. Concrete targets (numbers, reproduction
checks) stay concrete and testable. This is the single home for "what done
looks like" — there is no separate acceptance-criteria list.]

- [ ] [Outcome 1]
- [ ] [Outcome 2]

## Known Requirements

[Only what we have actually decided must be true. Each item carries exactly
one tag. Omit this section entirely if the ask has no hard requirements yet.]

- **[HARD]** [Forced by an interface, physics, or an existing system. Non-negotiable.]
- **[NEED]** [An outcome a stakeholder actually stated. Stated as an outcome —
  a reader must not mistake it for an implementation choice. An outcome you
  inferred rather than heard is **[INFERRED]**, not [NEED].]
- **[INFERRED]** [Implied by the ask, not stated by the user. Tagged so the
  reviewer can scan for and confirm your inferences.]
- **[INHERITED]** [Absorbed from an upstream artifact (concept, prior spec),
  not independently validated here. Cite the source. Not [HARD] — its authority
  is a document, not reality. See `claude-pack/rules/capture-fidelity.md`.]

## Non-Goals

- [What this work item deliberately does not try to solve.]

## Open Questions / Deferred to design

- [Anything intentionally left open — especially usability and mechanism
  choices. Deferred items from the questioning loop land here.]

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_{name}.md` (if this item belongs to an epic)
- **Required Reading:** [List the files from the epic's Required Reading for this item, if any]
- **Research:** `.project/research/{file}.md` (if any)
- **Design:** `.project/active/{feature-name}/design.md` (to be created)

---

**Next Steps:** After approval, proceed to ``my-design``.
```

### Stage 4: Review and present

Before presenting, check:
- Does each fact live in exactly one section? (No "why" repeated four times; no outcome repeated as a requirement.)
- Does every requirement carry a tag, and do `[NEED]` items read as outcomes, not mechanisms?
- Does every `[INHERITED]` item cite its upstream source, and is each `[NEED]` one the owner actually stated (not an inference that should be `[INFERRED]`)?
- Did I capture every detail the user gave, and mark my inferences `[INFERRED]`?
- Is the depth proportional to the ask — thin where the input was thin?
- Did I keep solution choices out of the requirements, and park them in Open Questions instead?

**Run the product-lens on the drafted spec.** The spec is a place scope narrows, so an
independent check re-derives the point here. Spawn a fresh-context `default` subagent whose entire
instruction set is `../../../.codex/scripts/product-lens.md` (pack source:
`claude-pack/scripts/product-lens.md`). SOURCES = the repo's durable product statements
(`README`, `docs/`, `.project/adr/`, `.project/product/` index-first) plus any owner-verbatim
in the concept / Required Reading;
WORK = the drafted spec, especially Problem and Success Criteria. It checks both directions —
does the spec contradict or narrow the point, and does it omit an obligation the point requires?
Append its verdict block (ledger format, product-lens spec §3) to
`.project/active/{feature-name}/product-lens.md` (append-only), and add a one-line pointer to the
spec's Related Artifacts. An unresolved owner/`[HARD]` contradiction blocks the spec until
dispositioned; a lower-authority or can't-find finding needs a visible disposition and may
proceed. Do not embed the findings in the spec body — the pointer is enough.

If the item belongs to an epic, **always** record the parent epic in this item's ledger — write
`Epic: <id>` in the first block — whether or not the epic has a finding yet. This unconditional
record is what lets ship gates and audit find the epic's live gate even for a BLOCK the epic raises
*after* this item exists (a reference written only when a finding already exists would miss late
epic findings). Then, for any epic finding that already exists, add a one-line **reference** — the
finding and its **original source grade preserved exactly** (an owner/`[HARD]` finding stays
owner/`[HARD]`; never downgrade at the hop) — *not* a restatement (copying duplicates and drifts,
smell 1). The epic file stays the source of truth; gates resolve `Epic: <id>` against the epic's
live gate. An epic BLOCK is not cleared by item creation.

Then present the spec, take feedback, and iterate.

## Guidelines

- **Aggressive about the problem, conservative about the solution.** Uncover relentlessly; don't invent mechanisms.
- **One home per idea.** The structure prevents redundancy; rely on it instead of restating.
- **Tag honestly.** `[HARD]` only when something truly forces it. Default a desire to `[NEED]`, phrased as an outcome.
- **Under-specification is allowed.** Usability and mechanism questions belong in design. File them in Open Questions and move on.
- **Don't manufacture content.** No quota of questions, no quota of requirements. If it isn't load-bearing, leave it out.

---

**Related Commands:**
- Before spec: ``my-research`` for deeper exploration
- After spec (optional): ``my-product-design`` for experience/interaction design on UX-heavy items
- After spec: ``my-design`` for technical design
- Review: ``my-spec-review`` for an adversarial audit before design — in a fresh session, not this one

**Last Updated**: 2026-07-06


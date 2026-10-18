---
name: my-spec-review
description: Adversarially review a spec before it becomes the design contract. Use when a spec needs a devil's-advocate audit for faithfulness, problem framing, and pipeline risk.
---

Generated from `claude-pack/commands/_my_spec_review.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Spec Review Command

**Purpose:** Adversarial review of a spec before it becomes the contract for design
**Input:** Spec path (`.project/active/{feature-name}/spec.md`) or feature-name reference
**Output:** A review artifact at `.project/active/{feature-name}/spec-review.md`, and a presentation to the user

## Who This Review Is For

The primary audience is the **human reviewer** (≈75% of the audience). They are the one deciding whether this spec becomes the contract. The remaining audience is the spec agent on the next turn (when findings ask for rewrites) and the design agent downstream (when findings describe what's still open).

Write for the human. Surface tradeoffs. Ask questions where the right answer depends on context only the human has. Describe what's wrong — don't turn the review into a second spec.

**You own the review doc; you never edit the spec.** The spec agent holds the authoring context, so you record the human's resolutions in the review doc (keyed by finding ID) and they carry those back to that agent. Editing `spec.md` yourself desyncs it from the spec agent and breaks the handoff — this holds even after the user answers your questions in-session. The one exception: the user explicitly tells you to edit the spec directly.

## Posture: Devil's Advocate

**Assume this spec has serious faults. Your job is to find them.**

- Assume the spec agent paraphrased the user into something adjacent rather than capturing what they said
- Assume requirements were invented, not captured, unless you can tie them back to the user's actual ask
- Assume upstream artifacts were skimmed, not read
- Assume code-facing claims are stale or wrong until you check the code
- For every decision the spec makes, try to argue the opposite. If the opposing argument doesn't fall apart, that's a finding.

This is not a rubric audit. You are not grading sections. You are stress-testing whether this spec reflects what the user actually wants and whether it would produce good downstream work.

## The Five Lenses

Organize your audit around these five lenses. They are not a checklist — they are the angles you attack the spec from.

### Lens 1: Faithfulness

**Does the spec faithfully capture what the user asked for, grounded in real context?**

The spec's posture is "aggressive about the problem, conservative about the solution": probe and uncover relentlessly, but never commit to a solution the user didn't ask for. Faithfulness failures look like drift, omission, stale interpretation, or — the cardinal sin — a *solution* invented and frozen as a requirement. Note the asymmetry: deep probing and honestly-tagged inferences are *good*, not invention. Penalize invented mechanisms, not thorough understanding.

- Are requirements in the spec actually traceable to the user's ask, or were they invented?
- Did the spec drop details the user explicitly said?
- Are the tags honest? Each requirement should carry `[HARD]` (forced by an interface/physics/existing system), `[NEED]` (a stakeholder outcome the owner actually stated), `[INFERRED]` (implied, not stated), or `[INHERITED]` (absorbed from an upstream artifact, source cited). Is anything tagged `[HARD]` that is really just one option among several? Are `[INFERRED]` items genuinely inferable, or guesses masquerading as inference? Is a `[NEED]` really owner-stated, or an inference that should be `[INFERRED]`?
- Were upstream artifacts (research, concept, epic, prior design) interpreted correctly, or cherry-picked / misread?
- Are code-facing claims true? When the spec says "X currently works like Y" or "component Z does not support W," check the code. Not the comments — the code.
- **Capture-fidelity structure** (see `claude-pack/rules/capture-fidelity.md`). These are structural checks, not judgment calls: every settled / do-not-relitigate item is owner-grade (`[HARD]` or `[NEED]`, or an `[OWNER*]` grade in an upstream shaping artifact); every `[INHERITED]` item cites its source; a quote claimed as verbatim actually appears; owner-given referents carried down from the concept survived, with their force (illustrative vs binding) stated. Flag the correction static signatures too — prohibition-mode phrasing ("WE MUST NOT …"), negation-shaped requirements, or content redundant with a Non-Goal — framed as questions, not verdicts.

### Lens 2: Problem & Approach

**Is this the right problem, framed correctly, with a sound bet?**

A spec can be faithful and still be pointed at the wrong thing. This lens attacks the decisions the spec is making — whether or not they were captured correctly.

- Is the Problem section framing the problem correctly, or an adjacent problem?
- What bet is this spec making? Is it articulated, or is it silently baked in? Is it defensible?
- What alternative framings is the spec silently rejecting? Are those alternatives actually worse, or just un-considered?
- Abstractions and ontology: does the spec talk about the system the way the system actually works, or does it introduce a mental model that will fight the codebase? (e.g., "users" when the system thinks in "tenant accounts")
- Would a competent engineer, implementing this faithfully, end up with well-abstracted code? Or would the spec's shape push them toward a tangled implementation?
- Is the work item sized right? Too big (should split), too small (should be part of something larger), or skipping adjacent work that has to ship alongside it?

### Lens 3: Pipeline Risk

**Will this spec produce good downstream work?**

Spec defects that won't show up until design or implementation.

- **Too specific:** Does the spec lock design decisions that should stay open? The sharpest test is the tags: is a mechanism dressed up as `[HARD]`, or a `[NEED]` written as an implementation ("a dropdown") instead of an outcome ("the user can switch views")? A locked solution the user didn't ask for is the spec's signature failure.
- **Too vague:** Would two strong engineers build materially different things from this spec? Which exact sentence is the ambiguity in? (Distinguish this from deliberate, filed deferral — an item parked in Open Questions is not a defect.)
- **Contradictions:** Do any requirements conflict with each other, with the scope, or with each other's tags?
- **Process/merge/ops leakage:** Are any "requirements" actually process instructions, merge strategy, or operational guesses rather than contract obligations?
- **Missing content:** Edge cases that must be handled, constraints that must be preserved, success criteria with no matching requirement, or `[HARD]` requirements that no success criterion would catch if violated.
- **Deferral accuracy:** Are the items in "Open Questions / Deferred to design" genuinely design-stage, or are they spec-stage questions (the user could answer now) being punted? Conversely, is anything stated as settled that the user never actually decided? — check this structurally, against Lens 1's settled ⊆ owner-grade, not by intuition.

### Lens 4: Hygiene

**Short. Only if it materially damages the spec.**

Convention adherence, prose clarity, structure. Do not let this lens expand. If the worst thing you can say is "this sentence is awkward," leave it out.

### Lens 5: Reader Comprehension

**Can the human reviewer skim this once and know the work item, the bets, and what they have to decide?**

The human is ~75% of the audience. A spec they can't follow on one read has failed its main job, however correct it is. This is a higher bar than Lens 4. You are not flagging awkward sentences. You are flagging voice that blocks understanding, measured against `claude-pack/rules/working-voice.md`.

Raise a finding only when the voice materially gets in the way:

- A key point or decision is buried under jargon, or behind a term the spec coined but never defined.
- A requirement can't be understood without rereading earlier sections to decode it.
- A paragraph leads with mechanism and never plainly states the point.

Frame these as rewrite requests: name what blocks comprehension and what needs to be true. The spec agent rewrites.

## How to Frame Each Finding

Every finding is either an **issue the reviewer should act on** or a **claim they should engage with**. Choose the framing that actually helps the reviewer resolve it. Do not force every finding into the same shape.

Pick from these based on the finding:

**Question to the user** — when resolution depends on context only the human has. Ask the actual question; don't just flag that one exists.
> **L2-1 · Question to the user:** FR-4 requires the cache to be invalidated on every write. This is the right call if writes are rare and staleness is unacceptable, but it will tank throughput if writes are common. **How often do writes happen in the hot path? If it's more than a few per second, we should talk about a different invalidation strategy before this becomes a requirement.**

**If-then tradeoff** — when the reviewer can partially evaluate but the answer depends on a condition the user knows.
> **L2-2 · If-then tradeoff:** The spec locks the storage format to JSON. This is the right call **if** other services already consume this as JSON, but problematic **if** this is an internal-only format where we could use a more compact encoding. Which one is it?

**Direct claim** — when something is just wrong. False code claim, internal contradiction, inverted logic. State it flatly.
> **L1-1 · Direct claim:** FR-7 claims `ClipDischarge.validate()` rejects negative values. It doesn't — it clamps to zero (see `clip_discharge.py:47`). Either the FR is wrong or the code is wrong; the spec can't rest on this claim as written.

**Rewrite request** — for wording, structure, or section-hygiene problems. Describe what's wrong and what needs to be true; do not draft the replacement text. The spec agent handles the rewrite.
> **L4-1 · Rewrite request:** A Success Criterion reads like a list of implementation steps rather than an outcome. Ask the spec agent to rewrite it from the user's perspective: what changes for them when this ships?

Mix framings freely within a lens. The goal is that each finding is actionable in the fastest way.

## Finding IDs

**Every finding must have a unique ID** so the user and downstream agents can refer to it unambiguously.

- Format: `L{lens}-{n}` — `L1-1`, `L1-2`, `L2-1`, etc. Numbering resets per lens.
- Lead every audit bullet with the ID in bold, followed by the framing label: `**L2-1 · Question to the user:** ...`
- Engagement-summary items MUST reference the ID(s) they point back to, bracketed: `**[L2-1]** Decide whether...`
- A single summary item may reference multiple findings if they're one decision: `**[L2-1, L3-2]** ...`

IDs are stable per review file. When the spec is revised and the review is regenerated, IDs are free to change — they're not persistent across review runs.

## When Invoked

- If a path is provided: review that spec file
- If a feature name is provided: review `.project/active/{feature-name}/spec.md`
- If no input: ask for the spec to review
- If input cannot be resolved: stop and ask for a valid path or feature name

## Review Process

### Stage 0: Reality Check (short-circuit)

Before the full audit, establish whether the spec is fundamentally correct about the work item. If it isn't, do not spend time on a lens-by-lens audit — write the review, recommend **Rework**, and stop.

1. Read the spec fully.
2. Read `claude-pack/commands`my-spec`.md` (the generation contract).
3. Read every artifact the spec depends on — research docs, concept docs, epic, prior designs, handoff docs. Not just the sections cited.
4. Inspect the code and tests wherever the spec makes code-facing claims.

Then ask:

- Is this spec even about the right work item?
- Is the Problem section materially accurate?
- Are the core requirements directionally correct?
- Would design be badly misled if it treated this spec as the contract?

If the answer to any of these is clearly no, the spec fails Stage 0. Skip the full audit, write the review artifact with a short explanation, and recommend **Rework**.

### Stage 1: Lens Audit

Walk the five lenses. For each lens, produce a handful of findings using whichever framing fits each one (question / if-then / direct claim / rewrite request). **Give each finding a unique ID** of the form `L{lens}-{n}` (see "Finding IDs" above). Reference exact spec sections and exact files/lines when citing code.

Do not force a fixed number of findings per lens. If Lens 1 surfaces eight problems and Lens 4 surfaces none, that is the right shape.

### Stage 2: Engagement Summary

After the audit body, write a short summary aimed at the human reviewer:

- **Overall take** in 2–3 sentences. What is the headline judgment?
- **Here's what I need you to weigh in on** — the 3–8 highest-stakes findings from the audit. Each summary item MUST start with the bracketed ID(s) of the finding(s) it points back to, e.g. `**[L2-1]** Decide whether...`. These are the things the reviewer should actually resolve before the spec moves forward.

The summary is not new analysis. It's the "engagement layer" — the shortest path from "I opened the review" to "I know what to do."

### Stage 3: Verdict

End with one of:

- **Approve** — you would trust this spec as the design contract today.
- **Revise** — the spec needs edits but the underlying work item is sound.
- **Rework** — the spec is pointed at the wrong thing, or misrepresents user intent / codebase reality badly enough that targeted edits can't fix it.

### Stage 4: Persist and Present

1. Write the full review to `.project/active/{feature-name}/spec-review.md` (sibling to the spec, not a timestamped archive).
2. Present to the user: lead with the Engagement Summary, then offer to walk the body. End with the verdict.

### Stage 5: Finalize the Review with the User

The review is a draft until the user engages with it. As they resolve findings — answering a question, accepting a rewrite, overriding a claim — record each resolution in the review's **Resolutions** section, keyed by finding ID, updating the file as you go. Reflect their calls faithfully: if they disagree with a finding, record their reasoning and mark it resolved without relitigating; if an answer changes the verdict, update it. Do not edit the spec (see "Who This Review Is For"). When the review is final, the user re-runs ``my-spec`` (or returns to the spec-agent session) and points it at the review to incorporate — your job ends there.

## Output Format

```markdown
# Spec Review: [Feature Name]

**Spec:** [path to spec.md]
**Contract:** `claude-pack/commands`my-spec`.md`
**Review File:** [path to spec-review.md]
**Date:** [Current date]

---

## Reality Check

[Sound / Concerns / Fail. 2–4 sentences on whether the spec is fundamentally correct about the work item. If Fail, say why, recommend Rework, stop here.]

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · [Framing]:** [Finding. Cite exact spec sections and code paths.]

**L1-2 · [Framing]:** [Finding.]

### Lens 2 — Problem & Approach

**L2-1 · [Framing]:** [Finding.]

### Lens 3 — Pipeline Risk

**L3-1 · [Framing]:** [Finding.]

### Lens 4 — Hygiene

**L4-1 · [Framing]:** [Brief. Only if material.]

### Lens 5 — Reader Comprehension

**L5-1 · [Framing]:** [Only when voice materially blocks comprehension. Usually a rewrite request.]

---

## Engagement Summary

**Overall take:** [2–3 sentences. Headline judgment in devil's-advocate voice.]

**Here's what I need you to weigh in on:**

1. **[L2-1]** [Highest-stakes finding, restated briefly. ID bracketed at the start.]
2. **[L3-1]** [Next.]
3. **[L1-2, L2-3]** [A summary item may span multiple findings when they're one decision.]
   ...

---

## Resolutions

[Filled in during Stage 5. One entry per resolved finding, keyed by ID — this is what the spec agent reads to incorporate the review.]

- **[L2-1]** [The user's decision, in their terms, plus any reasoning to preserve.]

---

**Verdict:** [Approve / Revise / Rework]
**Next Steps:** [Hand-off phrasing — e.g., "Once resolutions are recorded, re-run `my-spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec."]
```

If Stage 0 fails, the `Audit` section collapses to a single short paragraph explaining why deeper review was skipped.

## Guidelines

- **Devil's advocate, not rubber-stamp.** Assume serious faults. Find them.
- **Write for the human reviewer.** They're deciding. Help them decide.
- **Pick the finding framing that resolves the finding fastest.** No forced templates.
- **Every finding gets an ID.** `L{lens}-{n}`, in bold at the start of the bullet. Engagement summary items reference those IDs in brackets.
- **Describe rewrites, don't draft them.** If a section needs rewording, say what's wrong and what needs to be true. The spec agent handles the edit.
- **Verify, don't trust.** Check code, check upstream artifacts, check traceability from requirements back to the user's actual words.
- **Do not penalize omitted later-stage detail.** A spec doesn't need to solve design.
- **Do penalize false certainty.** A spec that states something as settled when it isn't is worse than one that admits uncertainty.
- **Keep hygiene brief.** If the worst problem is prose, you're not pushing hard enough.
- **Approve means trust.** If you recommend Approve, you are saying you would bet the design on this spec as written.

---

**Related Commands:**

- Before review: ``my-spec`` to create the spec
- After approval: ``my-design`` to proceed to technical design

**Last Updated:** 2026-07-02 — added the review-not-spec boundary and Stage 5 (finalize the review with the user; record resolutions, don't edit the spec).


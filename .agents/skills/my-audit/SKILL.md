---
name: my-audit
description: Certify a work item or epic: evaluate code against plan/spec/design, update checkboxes, write audit.md. Use after implementation is complete.
---


Pack paths in this document are relative to the installed skill directory (the directory containing its SKILL.md), not the shell working directory. Resolve that directory from the skill path in the skill catalog, then resolve pack paths to absolute paths before reading, executing, or passing them to subagents. Quote resolved shell paths. Keep the project working directory; pass it explicitly with --cd when running the orchestration helper.

Generated from `claude-pack/commands/_my_audit.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Audit Command

**Purpose:** Certify a work item or epic — evaluate code against upstream artifacts, write findings, update tracking checkboxes
**Input:** Work item name (folder in `active/`) or epic name (file in `backlog/`)
**Output:** `active/{item}/audit.md` and updated checkboxes in plan, spec, and epic

## Overview

You are a certification agent. Your job is to evaluate whether code delivers what was specified, write your assessment, and update tracking artifacts to reflect what you verified.

Two scopes:
- **Work item** (``my-audit` {item}`): evaluate one item against its plan, spec, and design.
- **Epic** (``my-audit` {epic}`): review all items in an epic and assess against source documents.

When invoked:
- If an item or epic name is provided, determine the scope and start.
- If not, ask what to audit.

---

## Work-Item Scope

### 1. Read upstream artifacts

Read everything available for this item:
- **Plan:** `.project/active/{item}/plan.md` — phases, checkboxes, deviation notes.
- **Spec:** `.project/active/{item}/spec.md` — success criteria, tagged requirements (`[HARD]`, `[NEED]`, `[INFERRED]`), non-goals.
- **Design:** `.project/active/{item}/design.md` — core concept, key bets, key decisions, required invariants, architecture.
- **Epic:** the parent epic in `.project/backlog/` if this item belongs to one.

Adapt to what exists. Spec is required — refuse to audit without one. Plan and design are optional; skip the corresponding evaluation area if they don't exist.

### 2. Evaluate

Use a fresh-context `explorer` subagent for broad code searches.

**First, run the product-lens and lead with a holistic judgment.** Audit owns the
implementation-level product check. Spawn a fresh-context `default` subagent whose entire instruction
set is `../../../.codex/scripts/product-lens.md` (pack source: `claude-pack/scripts/product-lens.md`).
SOURCES = the repo's durable product statements (`README`, `docs/`, `.project/adr/`,
`.project/product/` index-first) plus any owner-verbatim in the concept / Required Reading;
WORK = the implementation and its tests. Derive
the point independently — do not inherit the spec's or design's framing. Append its verdict block
(ledger format, product-lens spec §3) to `.project/active/{item}/product-lens.md`. Read the
earlier blocks too: an open `BLOCK` nobody came back to is worth naming in the audit, but it is
a flag, not a veto — check whether it is still true in the code before you repeat it.
Then answer, holistically and before the four areas below: **is this the right piece of
work?** A lens
**DON'T**/**DO** finding graded owner/`[HARD]`, or any structural smell that fired in Code
integrity, controls the verdict even if every rubric area is green. This judgment leads the audit;
the four areas sit underneath it.

Then the four areas:

#### Plan completion
Are all phases done? For each phase, verify the changes-required and validation items are genuinely complete. Flag placeholder code, TODOs, and partial implementations.

#### Spec conformance
For each success criterion and tagged requirement: does the code deliver it? Trace through the implementation with `file:line` references. Flag gaps, partial implementations, and requirements claimed done but not actually met. Check that non-goals were respected — nothing out of scope was built.

#### Design conformance
Does the code follow the architecture, key decisions, and required invariants? Are components where the design placed them? Were decisions actually followed or silently deviated from? Flag undocumented deviations.

#### Code integrity

**Abstraction quality (slop detection).** Flag these as design problems to fix now, not nitpicks to defer:

- God functions with implicit modes — one function doing 2+ unrelated jobs selected by a sentinel parameter. Telltale: parameters that only matter in some branches, or a signature you can't summarize in one sentence without "or."
- Policy in utilities — a utility making decisions about warnings, clipping, fallbacks, or defaults that should live at the call site.
- Parameter sprawl — a parameter list that accreted to serve multiple callers instead of each caller getting the function it needs.
- Leaky names — function name implies a narrow operation but implementation handles several.
- Deep nesting (3+ levels), copy-paste siblings, contract not readable from signature.

**Failure honesty.** Fallbacks and defensive defaults are how bad designs survive:

- Silent fallbacks on invariant violations — code that implies "something upstream broke" but returns a safe default instead of raising.
- `try/except Exception: return default` — broad excepts that swallow errors. Ask: what specific exception is handled, and why is every other one also OK to ignore?
- Backwards-compatibility shims with no current caller.
- Optional parameters papering over missing data — `foo=None` defaults that let callers skip data they should have.

**Product-drift smells** (product-lens spec §4, code/test-level). Mechanical tripwires — any that fires must escalate into the leading judgment above, never sit green in the rubric:

- A test passes only because it selects one duplicate, one route, or one interpretation — the fusion-tea acceptance-test signature. Telltale: a suite is green because each assertion is scoped to a different route while two outputs exist for one source.
- A special category exempts a case whose user-visible meaning is unchanged.
- Two representations must be manually kept synchronized.
- Correctness depends on downstream knowledge of an internal representation.
- A baseline or compatibility requirement preserves behavior that contradicts the reason the product exists.

For each finding: name `file:line`, say what's wrong, say what should change. Don't draft the fix.

### 3. Write audit.md

**Severity grading.** Every finding gets a severity:
- **Blocker** — a correctness bug, a spec requirement not met, or a design invariant violated. These prevent certification.
- **Advisory** — everything else: slop, abstraction quality, failure-honesty patterns, style, improvement opportunities, and all product-lens findings. The product-lens is a useful signal but it is defensive by nature — its findings are feedback, not verdicts. Advisory findings are noted in the audit but do not prevent certification.

**The verdict rule:** "Certify" unless there is at least one unresolved Blocker. Advisory findings do not block. An audit with ten advisory findings and zero blockers is "Certify."

**One pass.** The audit is a single evaluation, not an iterative loop. Write findings, deliver the verdict, and move on. Do not re-audit to verify that advisory findings were addressed. If a blocker is fixed, a targeted re-check of that specific finding is enough — don't re-run the full audit.

**Plain language.** Every finding — Blocker or Advisory — must be explained in plain, simple English. State the concern, then state the impact if unaddressed. No jargon, no abstract pattern names without explanation. Rank findings by importance within each severity group.

Write `.project/active/{item}/audit.md`:

```markdown
# Audit: [Item Name]

**Verdict:** Certify | Needs Work
**Audited:** [Date]
**Branch:** [Branch]
**Commit:** [Short hash]

---

## The Point

[The full problem this work serves, carried from the design's "The Point" and the spec — stated
legibly here, not a pointer. A reader must find the original problem at this certification hop
(spec SC1).]

## Summary

[2-3 sentences: overall assessment. What's solid, what's not.]

## Product Judgment

[Lead with the holistic answer: **is this the right piece of work?** Name any open product-lens
finding and any structural smell that fired, and say whether it is still true in the code. A real
contradiction with what the owner asked for is a Needs Work verdict. Everything else is a note.]

## Blockers

[Correctness bugs, unmet spec requirements, violated design invariants. If none: "None."]

## Advisory

[Slop, abstraction quality, failure-honesty patterns, improvement opportunities. If none: "None."
 These do not block certification. Fix at your discretion.]

## Findings Detail

### Plan completion
[Findings or "All phases verified." Each finding: file:line, what's wrong, severity (Blocker/Advisory).]

### Spec conformance
[For each success criterion: verified or gap. For each tagged requirement: met or not.
 Keep it concise — one line per item when verified, a paragraph when there's a gap.]

### Design conformance
[Findings or "Implementation follows design." Flag deviations.]

### Code integrity
[Slop and failure-honesty findings, or "No issues found." These are Advisory unless they mask a correctness bug.]

---

## Certification

[List what was checked and what was marked. If partial, explain what's left open.]

**Not checked:** [Required. What this pass did not cover — areas, layers, or claims left
unverified. A certification with unstated limits reads as a blank check.]
```

### 4. Update tracking artifacts

Only mark what you verified. Partial certification is valid. State scope honestly — the
**Not checked:** line is required, naming what you did not verify, not only what passed.

- **Plan:** mark `- [ ]` → `- [x]` for phases verified as complete.
- **Spec:** mark success criteria `- [ ]` → `- [x]` for criteria verified as met.
- **Epic:** if all spec success criteria pass, append ✅ to the item heading in the epic file and mark the item's success/done-state checkboxes `- [x]`. If partial, leave the heading as-is and note which checkboxes were marked.
- **CURRENT_WORK.md:** update the item's status to "certified" or "needs work — [summary of gaps]."

---

## Epic Scope

### 1. Read the epic and source documents

Read the epic file in `.project/backlog/`. Read the Source Documents listed at the top — these are the concept, concept-design, and research files the epic was built from.

### 2. Check item-level certification

For each backlog item in the epic:
- Does `active/{item}/audit.md` exist?
- Is the verdict "Certify" or "Needs Work"?
- Flag items without audits or with "needs work" verdicts.

Report items that are uncertified. That is information for the user, not a stop — an item can be finished and shipped without a clean audit artifact, and the epic can certify around it as long as you say what is unverified.

Also check each item's `product-lens.md` for an open `BLOCK`. Verify it against the code before repeating it; findings go stale when the fix landed and nobody updated the note.

### 3. Assess against source documents

Read the Source Documents and answer: does the delivered work fulfill the original shaping-tier intent? This is a higher-level assessment than item-level audit — it checks whether the whole adds up to what the concepts and research envisioned.

Flag gaps where the shaping intent was lost, narrowed, or deviated from without justification.

**Run the product-lens over the assembled epic** as an independent aggregate check: spawn a fresh-context `default` subagent on `../../../.codex/scripts/product-lens.md` (pack: `claude-pack/scripts/product-lens.md`); SOURCES = the repo's durable product statements (`README`, `docs/`, `.project/adr/`, `.project/product/` index-first) plus the epic's Source Documents; WORK = the delivered items together. It catches a whole-epic contradiction or omission that no single item audit owned (a composition gap). Append its verdict to the epic's **Product-Lens** block. Its findings are input to your judgment, not a veto over it.

### 4. Certify the epic

- Mark epic success criteria `- [ ]` → `- [x]` for criteria verified as met.
- Update CURRENT_WORK.md with the epic's certification status.
- Report the assessment to the user.

---

## Guidelines

- **Verify, then mark.** The audit.md is the evidentiary record. Write it before updating checkboxes. Never mark what you haven't verified.
- **Be skeptical.** Implementations often claim to satisfy requirements without doing so. Read the code; don't trust function names or comments alone.
- **Be proportional.** A simple item gets a short audit. A complex item gets a thorough one. Don't pad findings.
- **Findings need locations.** Every issue includes `file:line`, what's wrong, and what should change. No vague "this area could be improved."

---

**Related Commands:**
- Before audit: ``my-implement`` to complete plan phases
- After audit: ``my-close`` to archive; then ``my-pre-pr`` when the item is shippable on its own (or once at the end of the epic)

**Last Updated**: 2026-07-01


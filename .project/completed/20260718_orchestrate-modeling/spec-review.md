# Spec Review: Orchestrate Modeling

**Spec:** `.project/active/orchestrate-modeling/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/orchestrate-modeling/spec-review.md`
**Date:** 2026-07-18

---

## Reality Check

Sound. The spec is about the right work item: a modeling counterpart to the software
orchestrator, adapting `_my_orchestrate.md` rather than copying it. The Problem section is
accurate — the reference implementation exists and works the way the spec describes, and the
`[HARD]` registration claim checks out against `MBSE_COMMANDS` in
`src/agentic_mbse/cli/__init__.py:18` and the command list in `scripts/replicate_setup.sh:55`.
Design would not be misled by treating this as the contract.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Question to the user:** The fourth `[NEED]` states the run "must use the software
orchestrator's autonomy pattern" and then enumerates its four parts (one alignment checkpoint,
autonomous execution details, parked reserved gates, premise surfacing). Did you state that
four-part decomposition, or did you say "follow the software orchestrator's pattern" and the
spec agent expanded it from `_my_orchestrate.md`? If the latter, the expansion is
`[INHERITED: _my_orchestrate.md]` content riding under an owner grade — the adoption is yours,
but the specifics would then be challengeable against the referent rather than settled as
stated. This matters downstream because the design treats the four parts as fixed.

**L1-2 · Direct claim:** Everything else checks out. The `[INFERRED]` items are genuinely
inferable from the referent, not guesses dressed up. The `[REFERENT]` tag on
`_my_orchestrate.md` carries its force explicitly ("the behavior and judgment bar to adapt,
not a template to copy mechanically") — capture-fidelity compliant. No prohibition-mode
phrasing; Non-Goals read as decision records. The command list in Open Questions
(`review-model` included) matches `claude/commands/` on disk.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** The relationship to `epic_command-refresh.md` (CMDREF-001) is
parked as "not yet decided" in Related Artifacts rather than filed as an open question. The
design has since proceeded standalone. This is a decision only you can make: does this work
item live under CMDREF-001, or is it standalone and the epic reference merely context? Worth
settling before close, because CMDREF-001's success criteria (leaner commands, working-voice
skill) and this item's deliverables (a new command) will otherwise both claim the same
`cmd_init`/`replicate_setup.sh` surfaces.

**L2-2 · Direct claim:** The sizing is right. The spec resists the temptation to solve the
pipeline definition itself and defers six genuinely design-stage questions. The Non-Goals
correctly fence off the workflow-engine failure mode, which is the signature risk of this
work item.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** The third Open Question presumes a mechanism: "launching fresh stage
agents, **resuming them** when they ask the orchestrator for a decision." Built-in Task agents
have not historically been resumable — the software reference needs a shell helper and session
IDs precisely for this. The question as phrased quietly imports the software mechanism's shape
into the design space. The design has in fact hit this ambiguity (see design review). Not a
spec defect per se — it is filed as open — but the phrasing biased the design toward assuming
continuation is available.

**L3-2 · Direct claim:** Requirements and success criteria map cleanly: every `[NEED]` has a
criterion that would catch its violation, and criterion 6 covers the `[HARD]` registration
requirement. No contradictions found. "The orchestration stays thin" is subjective but is
anchored by the Non-Goals, which is the right way to bound it.

### Lens 4 — Hygiene

Nothing material.

### Lens 5 — Reader Comprehension

Nothing material. The spec reads in one pass; tags are anchored, deferrals are explicit.

---

## Engagement Summary

**Overall take:** This is a faithful, well-fenced spec. The requirements trace, the tags are
honest, the one code-facing claim is true, and the deferrals are genuinely design-stage. The
two things worth your attention are provenance questions, not structural defects.

**Here's what I need you to weigh in on:**

1. **[L1-1]** Did you state the four-part autonomy pattern yourself, or just point at the
   software orchestrator? If the latter, the enumeration should carry
   `[INHERITED: _my_orchestrate.md]` so future agents challenge it against the referent
   instead of treating it as settled.
2. **[L2-1]** Decide whether this item lives under CMDREF-001 or standalone. The design has
   proceeded standalone; if that's right, say so and the epic reference becomes pure context.

---

## Resolutions

- **L1-1:** The owner adopted the detailed autonomy pattern after the spec agent presented its four-part
  decomposition. Under capture-fidelity rules, the decomposition remains agent-derived and ratified,
  not owner-originated. The spec now grades it `[INFERRED]`, cites the reference, and records the
  2026-07-17 ratification.
- **L2-1:** Unresolved. Whether this item belongs to CMDREF-001 remains an owner decision before close.

---

**Verdict:** Approve — the two open findings are provenance clarifications, not blockers; I
would trust this spec as the design contract today, and the design built on it has not been
misled by it.
**Next Steps:** L1-1 is incorporated. Resolve the standalone-versus-CMDREF-001 relationship in L2-1
before close; it does not block planning or implementation.

# Brief: spec (revision) — pm-registry-integrity

**Sent:** 2026-10-04 by the orchestrator. **Stage:** `/_my_spec`, revising an existing draft. **Target:** `.project/active/pm-registry-integrity/spec.md`.

## Your task

Revise the existing draft spec in place to incorporate the spec review at `.project/active/pm-registry-integrity/spec-review.md`. Read the review's **Resolutions** section first: every finding has a recorded orchestrator call, and all of them are "Accept." Apply each one. Do not reopen them, do not add findings of your own, and do not touch `work/`, the backlog, or `CURRENT_WORK.md`.

Also read `.project/active/pm-registry-integrity/briefs/spec_review.md` for the intent, the owner rulings, and the verified fusion-tea facts. Treat those facts as given; you cannot read fusion-tea, but read-only copies are at `.orchestrate-logs/ft-snapshot/` if you want to look.

## What this work is for

[AGENT, re-derived] Registry entries and their IDs are stable referents that other artifacts cite by spelling. A silently dropped row, a silently deleted record, or a twice-minted ID makes those citations ambiguous. Every criterion should be readable as protecting that outcome.

## Provenance rules for this revision

- Nothing in this spec is owner-originated. Do not write `[NEED]` or `[HARD]` anywhere. The grades available to you are `[INHERITED: source]` and `[INFERRED]`, plus the exact ratified form the review prescribes for the four acceptance checks: `[INFERRED] (ratified by owner, 2026-10-04: "those hold. proceed.")`.
- Orchestrator decisions are recorded as `[AGENT] (orchestrator, 2026-10-04)` with the reasoning in one line, so a later agent can challenge them by re-deriving.
- A correction deletes or amends; it does not add compensating prose. Where the review says a fact was wrong, replace it.

## Shape I want

- Status stays Draft; header Branch becomes `pm-registry-integrity`; Next Steps points at `/_my_design` then `/_my_design_review`.
- Problem: two defects, one line each, then the evidence for each.
- Success Criteria: the contract from L3-1 as its own criterion; the escape criterion with the GFM reference from L3-4; the second-splitter criterion from L3-2; the round-trip criterion from L3-3; the no-record-loss criterion from L2-2; the concrete criterion 4 from L3-5. Each criterion names the evidence that proves it, drawing on the four ratified checks per L3-6.
- Known Requirements: the per-registry exposure table from L2-1 (copy the reviewer's or write your own; it must be accurate to the code).
- Non-Goals: unchanged, plus the three one-line limits from L3-7.
- Open Questions: OQ1 reworded per L2-3; OQ2 narrowed to the `\\|` and write-side mechanism choices; OQ3 closed and moved out of Open Questions into a short "Decisions" list.
- Related Artifacts: add the two code locations from L4-1 and this review.

Keep it tight. The spec is the contract design reads; it is not a place to restate the review. One line per paragraph, no hard wraps.

When done, end with `ARTIFACT: .project/active/pm-registry-integrity/spec.md`.

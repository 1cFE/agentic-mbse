.project/active/native-skill-distribution/spec.md — revise the existing spec (do not start a new one)

## Brief from the orchestrator

A fresh spec review returned **Revise** (`.project/active/native-skill-distribution/spec-review.md`). Its **Resolutions** section, written by the orchestrator, says how each finding is settled. Apply those resolutions and the owner decisions in `briefs/00-align.md` together, in one revision of `spec.md`. You are the spec author for this pass; the reviewer does not edit the spec.

### What to change

1. `spec.md` — apply every resolution keyed L1-1 … L4-1. The ones that add or reshape success criteria: L2-1 (one place to register: no hand-maintained list), L3-1/L5-1 (SC2 pass condition first, closed adaptation list, no reflow, all three changed templates and the pattern docs), L3-2 (no `claude/` folder, and `init`, `init --dev` and a built wheel still install everything including the hook), L3-3 (legacy-symlink adoption boundary, five parts), L3-4 and L3-6 (owner runbook: pin move first, mode choice presented with rehearsed effects, keep `MODELING_PROCESS.md`), L3-5 (SC8 ends at a branch ready for the owner to merge; `[HARD]` no branch switching in `/home/reid/1cfe/agentic-mbse`), L1-3 (target-owned fusion-tea text moved by an owner-applied change, with ledger rows, before any re-init).
2. Provenance. Carry the owner's ask as `[NEED]` with the verbatim quote and a path cite to `briefs/00-align.md`. Carry the three ratified Align decisions as `[INFERRED] (ratified by owner 2026-10-09)`, not settled. Carry the rename quote verbatim with its force stated as permission. Carry the L3-6 pin move as `[INHERITED: .project/CURRENT_WORK.md]`. Everything the orchestrator decided in the Resolutions is agent-grade: grade it `[INFERRED]`, never `[NEED]`.
3. **Ratified decision 3 needs surfacing, not silent change.** The Align record says the owner runs `init --dev`. The Resolutions' new fact (fusion-tea tracks its Codex install in git; `--dev` would replace tracked files with machine-specific symlinks) is evidence against that choice. The spec must not hard-wire either mode. It states that the mode is the owner's choice at the reserved post-merge step, that the rehearsal reports each mode's effects, and that the orchestrator recommends plain `init` and why. Keep the ratified decision visible with a one-line note that its mode is reopened by this evidence and parked for the owner.
4. Epic `.project/backlog/epic_wrap-split.md` — keep it consistent with the revised spec, touching only what this item owns:
   - § Item 1: Current State line on pattern copying (L1-2); Effort to 2 days; Scope and Success Criteria wording to match the spec (envelope without reflow, runtime adaptation, no `claude/`, legacy adoption, runbook, branch ready for owner merge).
   - § Timeline: Item 1 row to 2 d and the total to match; the epic integration row notes that fusion-tea's Claude-side switch moves to Item 1's merge.
   - The rule "Items 2, 4 and 5 can write specs and designs while Item 1 runs, but must not register or edit shipped files until the merge lands" moves here from the spec's Open Questions (L3-8), under Epic Strategy or Dependencies.
5. Re-run the product-lens pass your process calls for and append the new verdict to `product-lens.md`. The procedure file is staged read-only at `.orchestrate-logs/nsd-inputs/product-lens.md`, because you cannot read `~/.claude/scripts/`.

### Constraints

- Follow the markdown rule: one line per paragraph or bullet, no hard wraps.
- Write for a tired engineer. SC2 in particular must be applicable on one read.
- Do not prescribe mechanisms the spec defers to design (the diff script, how dangling legacy links are recognized, the classification field, merge vs rebase).
- Read-only inputs: `.orchestrate-logs/nsd-inputs/` (native branch at `86921f9`, fusion-tea files at `403716ee3`). Do not run or edit them. Do not read or write sibling repos.
- Update the spec's `Updated` line and `Next Steps` (next: design).

When done, end with `ARTIFACT: .project/active/native-skill-distribution/spec.md`, and summarize in your final message what changed per finding ID and anything you could not apply.

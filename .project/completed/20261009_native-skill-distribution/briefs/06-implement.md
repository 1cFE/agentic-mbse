.project/active/native-skill-distribution/plan.md — Phases 1–3 in this session, then stop and report

## Brief from the orchestrator

Implement `WRAP-SPLIT` Item 1 by its plan (`plan.md`), which follows the reviewed design (`design.md`) against the spec (`spec.md`, SC1–SC12). This first session covers **Phases 1, 2 and 3 only**. Stop after Phase 3's commit and report; the orchestrator inspects the merge, the B2 probe result and the regenerated text before the installer work starts. You will be resumed for later phases.

### Where you are

- You run in the integration worktree `/home/reid/1cfe/agentic-mbse-nsd`, branch `nsd-integration`, cut from `wrap-split` at the commit that carries this brief. `.env` is in place and `uv sync` has run.
- `.orchestrate-logs/` (gitignored) holds the read-only inputs: `nsd-inputs/` (native snapshot at `86921f9`, fusion-tea files, fork diffs), `rehearsal/make-copy.sh` (run it, do not edit it), and a pristine rehearsal copy at `rehearsal/fusion-tea/` (fallback source for Phase 7 copies via `cp -a`). The native branch itself is reachable through git in this worktree (`native-claude-codex-skills` at `86921f9`).

### Hard rules

- Work only in `/home/reid/1cfe/agentic-mbse-nsd` and in scratch directories you create under `.orchestrate-logs/` or `/tmp`. Never write to `/home/reid/1cfe/agentic-mbse` (fusion-tea reads its `claude/` live), to `/home/reid/1cfe/agentic-mbse-native-skills`, or to `/home/reid/1cfe/fusion-tea`. Never switch branches in the first two.
- Never push, never open a PR, never merge into `main`. Those are the owner's.
- Commit per the plan's commit structure on `nsd-integration`, messages leading with the outcome. Check off the plan's boxes as you finish them and fill in each phase's Implementation Notes (what changed, deviations, surprises).
- Follow the plan's stop rules. In particular, if the B2 probe's plain-install run fails for a reason that is not the `metadata.kind` field, stop and return the log rather than guessing.
- Do not run background tasks; you are non-interactive and they do not survive your turn.

### The bar

The owner asked to simplify. Write code a maintainer reads once and understands. Prefer deleting to adding. If the plan or design is wrong against the code, stop and say so loudly rather than working around it silently; record the evidence in Implementation Notes.

### What to report when you stop

For each of Phases 1–3: done or not, the commit SHA, the checks you ran and their results. The B2 decision and its evidence (probe output paths). The number of conflicted paths in the merge and how each class was resolved. Phase 2's `check` result before and after `write`. Anything you deviated from and why. End with `ARTIFACT: .project/active/native-skill-distribution/plan.md`.

# Align record — goal-layer-port (`WRAP-SPLIT` Item 2)

**Date**: 2026-10-11. **Orchestrator**: Claude (Opus 5.5), `/_my_orchestrate .project/backlog/epic_wrap-split.md Item 2`. **Base**: `origin/main` at `33511c4`, branch `goal-layer-port`, worktree `/home/reid/1cfe/agentic-mbse-goal-layer`.

## Meaning of the work

[AGENT] (owner did not object at Align) Item 2 serves three outcomes: a non-fusion target gets a working goal layer from `agentic-mbse init` with nothing pointing at fusion-tea; MR-7 enforcement no longer depends on a hand-edited tool-owned file; fusion-tea can move to the installed copies and lose nothing. The port preserves the runbook's method; it replaces consumer paths with general wording and does not redesign the procedure.

## Owner decisions

- **fusion-tea writes.** [OWNER-VERBATIM] "just do it yourself." The orchestrator makes the fusion-tea change in a separate fusion-tea worktree on its own branch, commits only its own paths, and never touches the owner's main fusion-tea checkout. The owner pushes and merges.
- **MR-7 may change, and the general rule must sit at the right level.** [OWNER-VERBATIM] "yes. in fact, it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". This supersedes the epic's criterion that fusion-tea's `REQUIREMENTS.md` MR-7 stays byte-identical and its out-of-scope line about MR-7 text. The design-choice rule enters agentic-mbse's existing enforcement system; MR-7 becomes fusion-tea's application of it.
- **Shipped goal contract test.** [AGENT] (ratified by owner 2026-10-11, "fine") Ship only the narrative-link check. The ADR-register check tests the target's own `.project/adr/`, which `init` does not create and the goal layer no longer needs once the decisions doc ships; fusion-tea keeps its full test.
- **Research result mapping.** [AGENT] (ratified by owner 2026-10-11, "fine") The research-result → task-outcome table that Item 5's spec assigns to Item 2's runbook lands with Item 5's relabel step, because the names it maps exist only once Item 5 ships.

## Reserved gates

- Merge and push of `goal-layer-port` in agentic-mbse, and of the fusion-tea branch: the owner's.
- No other gate reserved. The wording of the shipped design-choice rule gets an independent review against MR-7; the owner reads it at PR time.

# Align record — research-seam-port (`WRAP-SPLIT` Item 5)

**Date**: 2026-10-12. **Orchestrator**: Claude (Opus 5.5), `/_my_orchestrate .project/backlog/epic_wrap-split.md item 5`. **Base**: `main` at `ac5fb1a` (Items 1 and 2 merged), branch `research-seam-port`, worktree `/home/reid/1cfe/agentic-mbse-research-seam`.

## Owner's run instruction

[OWNER-VERBATIM] 2026-10-12: "please be practical aobut it. e.g. decide whether you really need a spec-review, and limit the design reviews". The owner replied "proceed" to the Align message below, accepting every default it proposed.

## Meaning of the work

[AGENT] (owner did not object at Align) Two outcomes. A fresh target brings an outside source into `knowledge/` through one checked door: the installed `research-acquire` skill plus `agentic-mbse research open|log|close|register|retire|verify`. fusion-tea switches to the installed package with no data migration and no lost instruction. The port keeps behaviour: classes, refusal ladder, request-key rule, receipt, return and manifest shapes. New parts are the hold-out hook, a neutral replacement for the Zotero source kind, and `/manage-sources` reworked to follow the registry's rules.

## Pipeline decisions

- **No spec review.** [AGENT] (owner did not object) The spec passed product-lens twice (CLEAR) and records the owner's rulings; its open questions are design questions, which a design review checks against code. The orchestrator refreshed the spec for ground Items 1 and 2 moved, as factual corrections.
- **One design review round.** Must-fix points go back to the design author. A second check runs only if the fixes change the architecture, and then as a targeted check.
- **Audit kept**, because the port runs against live registry data. The run stops before `close` and `pre_pr`.

## Owner decisions (defaults accepted with "proceed")

- **fusion-tea side.** The orchestrator prepares a fusion-tea branch in its own worktree, never in the owner's main checkout: delete the two scripts, point Zotero ingest at the package, wire the ARIES-CS guard into the hook, ledger rows. It is tested against this branch installed editable, and merges after the owner merges agentic-mbse and the pin moves, by runbook. Same pattern as Item 2.
- **The two ITER Cryoplant entries** stay as visible `verify` findings; the owner decides later. Nothing waits on it.
- **"May a goal delegate insight approval?"** filed to the backlog as `GOAL-DELEGATED-INSIGHT-APPROVAL`; not this item.
- **Malformed requests.** Port as is; correct the shipped guide's BLOCKER example (the spec's lean).
- **Class-to-outcome mapping** lands in this item's relabel step. [AGENT] (ratified by owner at Item 2's Align, 2026-10-11, "fine").

## Reserved gates

- Merge and push of `research-seam-port` in agentic-mbse, and of the fusion-tea branch: the owner's.
- No other gate reserved. The orchestrator decides the spec's design questions and records each one.

## Facts the orchestrator verified at Align (2026-10-12)

- fusion-tea `main` at `0a833b9f7`; its seam files have the same line counts as when the spec was written. Its main checkout was clean.
- Since Item 1: `/manage-sources` is `skills/manage-sources/SKILL.md`; `scripts/replicate_setup.sh` is a six-line wrapper around `init`. Since Item 2: `docs/goal-layer-decisions.md` exists; the run-goal interim wording is at `skills/run-goal/SKILL.md:66`; the goal runbook has the six task outcomes but no seam-class mapping (`project_templates/GOAL_RUNBOOK.md.template:142-150`).
- Baseline at `ac5fb1a` in this worktree, synced with `uv sync --all-extras`: 2,217 passed, 1 skipped, 1 xfailed; ruff 118 findings; mypy 88 findings in 18 files. Without the `web` extra, 18 tests fail on missing modules.
- The auto-mode classifier refused copying fusion-tea's registry data and hold-out material into this worktree. Code, prompt, guide, ADR-0008, tests and the original seam spec and design were copied to `.orchestrate-logs/fusion-tea-snapshot/` (gitignored, read-only for stages). fusion-tea tracks `knowledge/` in git, so registry parity runs in a fusion-tea worktree instead.

# Align record — native-skill-distribution (WRAP-SPLIT Item 1)

Orchestrated run started 2026-10-09 from `/_my_orchestrate`, owner present at launch. This file records what the owner settled at the one checkpoint, so later stages and the human auditor can see where each decision came from.

## Entry

Single item; spec exists. Pipeline: `spec_review` (fresh) → spec revision → `design` → `design_review` → `plan` → `implement` → `audit`. The orchestrator stops before `close` and `pre_pr`.

## Premise found while orienting

[AGENT, verified by orchestrator 2026-10-09] fusion-tea's Claude Code side does not run the native install. Its `.claude/commands/*.md` (15 of 17; `manage-concept.md` and `research-acquire.md` are fusion-tea's own), `.claude/skills/*` (10), `.claude/agents/*.md` (5) and `.claude/hooks/ruff-format.sh` are symlinks into this checkout's source folder, `/home/reid/1cfe/agentic-mbse/claude/`, made 2026-03-02 by `main`'s `agentic-mbse init --dev` (added in `f92a62a`; `replicate_setup.sh` always copied). Only the Codex side (`.agents/skills/`, tracked in `.agentic-mbse/install.json`) is a native install. The spec's Problem bullet "fusion-tea runs `main`'s content in the native shape, by hand" holds for Codex only. Listing: `.orchestrate-logs/nsd-inputs/fusion-tea/runtime-entries.txt`.

Consequence: the native branch has already removed `claude/` (except `claude/hooks/ruff-format.sh`), so merging it to `main` breaks fusion-tea's Claude side as soon as this checkout moves to that `main`. The native installer's legacy-command retirement (`installation.py:202`, gated by `permit` at `installation.py:66`) skips entries it does not recognize as its own, and these symlinks are not in any manifest.

Operational rule this creates: no integration work runs in `/home/reid/1cfe/agentic-mbse`, because fusion-tea reads it live.

## Owner decisions

- [OWNER-VERBATIM] 2026-10-09: "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this" — every workflow is a skill, installed the same way for both runtimes.
- [AGENT] (ratified by owner, 2026-10-09, "yeah that's fine"): the plan that answers it.
  1. The merge removes `claude/` with no transitional shim.
  2. The installer recognizes legacy symlinks that point into an agentic-mbse `claude/` folder as its own and replaces them with the installed skills (and agents, hook), instead of preserving them as owner files. Tested by installing over a copy of fusion-tea's tree.
  3. When Item 1 merges, the owner runs `agentic-mbse init --dev` once in fusion-tea, so both runtimes install the same way from the source and live editing continues. This moves one step of the epic's integration forward to Item 1's merge.
- [OWNER-VERBATIM] 2026-10-09: "to be modle-agnostic, you can rename the folder hosting skills on the agentic-mbse side" — source-side folder names are tool-neutral. The one Claude-named source folder left on the branch is `claude/hooks/`; it moves so `claude/` disappears. Renaming or regrouping `skills/`, `agents/`, `adapters/` is permitted, not required.

## Reserved gates

[AGENT] (proposed at Align 2026-10-09; owner did not object)

1. Merging to `main`, and anything pushed to GitHub. The run ends with an audited branch ready for `pre_pr`; spec SC8's merge is the owner's.
2. Writes to fusion-tea's real tree, including the post-merge `init --dev`. The run reads fusion-tea and tests on copies only.

## Housekeeping done at launch

- `b2d077b` on `wrap-split`: committed the 2026-10-09 spec rewrite, product-lens, epic and CURRENT_WORK edits as the review baseline.
- `86921f9` on `native-claude-codex-skills`: committed the uncommitted A–K remediation (spec's `[INFERRED]` requirement), audit verdict unchanged.
- Read-only inputs for stage agents (which cannot read sibling repos) staged under the gitignored `.orchestrate-logs/nsd-inputs/`: native branch snapshot at `86921f9`, fusion-tea files at `403716ee3`, and `product-lens.md`.

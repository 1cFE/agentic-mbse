.project/active/native-skill-distribution/design.md

## Brief from the orchestrator

Write `plan.md` for `WRAP-SPLIT` Item 1 from the reviewed design (`design.md`, revised after `design-review.md`; resolutions recorded there). The contract is `spec.md` (SC1–SC12). The design's decisions are agent-grade and fixed for planning; challenge one only with evidence, and say so loudly.

### The point, and the bar

One place to register a skill: one tool-neutral source tree carrying `main`'s current text, installed the same way for Claude Code and Codex (point as read at Align, `briefs/00-align.md` § "The point, as read at Align"; owner ask at `:19`). The plan must lead an implementer to clean, well-shaped code: mostly deletion, one predicate inside `permit`, no new parallel mechanisms, tests that pin properties rather than inventories.

### Logistics the orchestrator will set up before implement (plan around these, do not plan to create them)

- **Worktree:** `/home/reid/1cfe/agentic-mbse-nsd` on new branch `nsd-integration`, cut from `wrap-split` at the commit that carries this plan. `.env` (syside licence key) copied in and `uv sync` run. All implementation happens there. [HARD] nothing runs in `/home/reid/1cfe/agentic-mbse` (fusion-tea reads its `claude/` live).
- **Rehearsal copy of fusion-tea:** fusion-tea is 16 GB without `.venv`, so the design's `rsync -a --exclude .venv` is replaced by a selective copy. The orchestrator builds it at `/home/reid/1cfe/agentic-mbse-nsd/.orchestrate-logs/rehearsal/fusion-tea/` (gitignored in the worktree) from fusion-tea at `403716ee3`: `.claude/` (legacy links copied as links, unchanged), `.agents/`, `.agentic-mbse/`, `.codex/`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `README.md`, `pyproject.toml`, `uv.lock`, `modeling_project/`, `data/`, `tests/conftest.py`, `tests/models/`, and from `work/` and `knowledge/` only the files the installer can touch (top-level files, `work/backlog/epic_template.md`, `work/learnings/RAW_LEARNINGS.md`). It is initialized as its own git repo with a baseline commit of exactly the files fusion-tea tracks among those paths, so `git status` after an install shows the git-visible effect against fusion-tea's tracked state. The orchestrator's script `.orchestrate-logs/rehearsal/make-copy.sh <dest>` makes a fresh pristine copy in seconds (tested 2026-10-09: 11 MB, 165 tracked baseline files, clean `git status`); plan each rehearsal run (plain `init`, `init --dev`) on its own pristine copy. The script already performs the design's D12 step: it rewrites all 31 legacy links from `/home/reid/1cfe/agentic-mbse/claude/…` to `/home/reid/1cfe/agentic-mbse-nsd/claude/…`, which no longer exists after the `git rm`, so the copy reproduces the post-merge dangling state and no rehearsal can reach the live tree. The script is read-only for the implementer: run it, do not edit it.
- **Reading fusion-tea's real tree is allowed; writing it is a reserved gate.** The proposed fusion-tea change (SC9) is a patch file in the evidence folder, never applied to fusion-tea.

### What the plan must contain

- Phases in the order the design's integration flow and commit structure (S1) require: mechanical merge commit; `reconcile.py write` alone; `git mv` hook and `git rm` of `claude/` plus this repo's tracked `.claude/` shipped-name copies; then installer changes; then evidence (SC2 check with its negative self-check, rehearsals, runbook, ledger rows, fusion-tea patch); then CLAUDE.md/README; then the full gate.
- **Phase 1 de-risks bet B2** (`metadata.kind` tolerated by both clients) with the discovery probe before any code depends on it; state the fallback (top-level `kind:`) and the decision rule.
- For each phase: the files touched, the checks that prove it (commands to run and what passing looks like), and which SC it serves. Every SC1–SC12 maps to at least one checkbox.
- Evidence lands under `.project/active/native-skill-distribution/evidence/` (disposition table, adaptation list, `reconcile.py`, check output, probe output, rehearsal reports, runbook, fusion-tea patch). The migration-ledger rows go to `.project/active/wrap-split-migration-ledger.md` (create it if absent; Item 2 owns it).
- The SC12 gate: `uv run pytest tests/` passes; ruff and mypy follow the parity rule (`spec.md:64`): no findings beyond `main`'s baseline and every added or edited file clean. Name the commands and how the baseline is captured.
- What stays parked for the owner and must appear in the runbook rather than be decided: the fusion-tea install mode (plain `init` recommended, both rehearsed) and keeping or dropping the pattern note after runbook step 1. The merge, push and any write to fusion-tea are the owner's.
- Commit per phase on `nsd-integration`, messages leading with the decision or outcome.

Keep markdown one line per paragraph or bullet. Do not run background tasks; you are non-interactive. End with `ARTIFACT: .project/active/native-skill-distribution/plan.md`.

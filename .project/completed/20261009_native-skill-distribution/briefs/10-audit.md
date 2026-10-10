.project/active/native-skill-distribution/plan.md

## Brief from the orchestrator

Independent audit of `WRAP-SPLIT` Item 1 on branch `nsd-integration` (worktree `/home/reid/1cfe/agentic-mbse-nsd`, HEAD `beceb6f`). You did not write any of it. The contract is `spec.md` (SC1–SC12); the design is `design.md` (decisions D1–D13, invariants I1–I9) as revised after `design-review.md`; the plan with implementation notes is `plan.md`. Write `audit.md` beside them with a verdict.

### The point, and the bar

One place to register a skill: one tool-neutral source tree (`skills/`, `agents/`, `adapters/`, `hooks/`, `project_templates/`) carrying `main`'s current text, installed the same way for Claude Code and Codex; fusion-tea switches over with nothing lost (`briefs/00-align.md`; owner ask at `:19`). Audit against that point, not only against checkboxes. The owner asked to simplify: judge whether the code a maintainer inherits is clean, minimal and obvious, and whether anything is placeholder, dead, duplicated or over-built.

### Scope (design D11, `evidence/audit-scope.md`)

- **The installer as it now stands**, diffed against the fork `88e2489`: this covers the native branch's A–K remediations together with this item's changes (tree-derived inventory, `is_source_checkout`, legacy-link adoption in `permit`, `expose_to_claude`, report-once). Spec SC11 requires this audit to update the native audit's verdict: after your verdict, change `.project/active/native-skills/audit.md`'s verdict line (`:3`, "Needs Work") to your verdict for the installer, with a one-line pointer to your `audit.md`. Edit nothing else in that file.
- **The tests**: do they pin behaviour and properties derived from the tree, or inventories (SC5, I4)? Try mutations: for example drop the `..` check, normalize the link text, make `permit` adopt on shape alone, re-add a hand list, break `bundle_kind`, skip `retire_command`. Record which the suite catches.
- **The content tooling**: `evidence/reconcile.py` (transform and `check`) and `evidence/adaptations.yaml` (entry A1 is flagged for review). Is `check` independent of `write`, and does the recorded negative self-check hold if you re-run it?
- **The evidence**: `dispositions.md` (SC1), `check.txt`/`check-negative.txt` (SC2), probe JSONs (SC7), `rehearsal.md` and `evidence/rehearsal/` (SC8, SC10), `fusion-tea-target-owned.patch` and `.project/active/wrap-split-migration-ledger.md` (SC9), `fusion-tea-runbook.md` (SC10), `lint-parity.md` (SC12), CLAUDE.md/README (SC12).
- **Out of scope**: workflow body text beyond the adaptation list (SC2 makes it mechanical).

### Known items the orchestrator accepted as follow-ups (challenge any you think should block)

- `docs/syside/python/v0.8.4/syside/` is missing from the wheel; pre-existing (present before this item); strict xfail in the wheel test keeps it visible.
- Under `init --dev`, Codex lists none of the 25 shipped skills (each `SKILL.md` is a file link outside the project); pre-existing on the native branch; SC6 requires `--dev` to install every asset, which it does; the runbook states the Codex effect and recommends plain `init`.
- The second-run report lists every existing file as Updated though bytes match; pre-existing.
- This repo's tracked init scaffold (`modeling_project/`, `work/`, `knowledge/`, `data/`) holds stale template copies; out of scope (R7).
- `--dev`'s `.gitignore` list still names `.claude/commands/` and `.claude/.tool-hashes.json`; cut from scope (design-review S3).

### Owner-reserved items (not yours to decide; check only that they are presented, not decided)

The fusion-tea install mode and the pattern note after runbook step 1 (both in `fusion-tea-runbook.md`); the merge to `main`, any push, any write to fusion-tea.

### Rules

Run anything read-only, plus `uv run pytest`, `ruff`, `mypy`, `reconcile.py check`, and installs into scratch folders you create under `.orchestrate-logs/audit-scratch/`. Mutations go in a scratch copy of the tree or are reverted before you finish; leave the worktree's tracked files as you found them except `audit.md` and the one verdict line. Do not write to `/home/reid/1cfe/agentic-mbse`, the native worktree or fusion-tea. Do not commit (the orchestrator commits). No background tasks. End with `ARTIFACT: .project/active/native-skill-distribution/audit.md`, after a summary: verdict, findings by severity with file:line, SC-by-SC status, and mutation results.

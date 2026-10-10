# SC1 dispositions: every difference between the native branch's shipped files and `main`

**Measured against:** `main` at `06ac41d` (one commit past the planned `8f43a09`: PR #17 changed one line of `MODELING_PROCESS.md.template`), fork `88e2489`, native branch `86921f9`. **Integration branch:** `nsd-integration`.

**The four dispositions (SC1):** *take main* (portable content); *keep the branch* (envelope, runtime adaptation or installer behaviour); *merge* (changed on both sides: `main`'s content with the branch's runtime adaptation applied); *target-owned* (stays in fusion-tea, with a ledger row).

## Inventory

Reproduce with:

```bash
git diff --name-status 88e2489 06ac41d -- claude project_templates docs/patterns
git diff --name-status -M 88e2489 86921f9 -- claude skills agents adapters project_templates docs/patterns hooks
```

- **Changed on `main` since the fork:** 16 bundles (11 workflows: `audit-models`, `backlog`, `design-model`, `implement-model`, `orchestrate-modeling`, `plan-model`, `quick-model`, `research`, `review-model`, `spec-model`, `status`; 5 supporting: `epic-decomposition`, `model-validation`, `project-structure`, `requirements-tracking`, `toolkit-awareness`), 3 tool-owned templates (`MODELING_PROCESS`, `MODELING_GUIDE`, `EPIC_GUIDE`), 2 pattern docs (`adr002-calculations.md`, `mbse-concepts.md`).
- **Changed only on the branch:** 2 user-owned templates (`README.md.template`, `OVERVIEW.md.template`), 2 agents by reflow (`python-debugger` R088, `sysml-expert` R095), the adapters (added), and the envelope on all 25 bundles.

## Generated rows: bundles, tool-owned templates, agents

[`check-rows.md`](check-rows.md) has one row per compared file (40), written by `reconcile.py check --main 06ac41d --rows`, with the `main` source, whether the envelope applies, and the disposition. `check.txt` shows that run: 55 files compared, 0 mismatches. `check-negative.txt` shows the same check exiting 1 on a changed body byte, a count raised by one, an extra bundle file, and CRLF line endings in a reference file or a `SKILL.md` (`check` compares raw bytes; audit advisory 9).

- Every file is *take main* except the ten files the adaptation list names, which are *merge: main + A…* (`onboard` A1–A4, `manage-sources` A5–A7, `pdf-analysis` A8 and its `extraction-details.md` A9, `python-debugger` A10, `record-learning` A11–A12, `sysml-conventions/references/stencils.md` A13, `toolkit-awareness` A14–A15, `agents/python-debugger.md` A16, `MODELING_GUIDE.md.template` A17).
- The 25 `SKILL.md` rows carry the envelope (frontmatter and preface), which is the branch's shape. That part of each file is *keep the branch*; the rest is the row's disposition.
- **`main`'s `skills:` frontmatter key is dropped by the envelope** (inherited from the native branch; `check` expects it gone, `reconcile.py:140`). 8 workflows named their supporting skills only there (audit advisory 2). [AGENT] (orchestrator, 2026-10-09) Accepted with no change: Claude Code treats `skills:` as subagent preloading metadata, not a command dependency loader (`.project/research/20260907-162310_native-claude-codex-skills.md:54-56`), so no runtime behaviour is lost.

## Hand rows

| Path | Disposition | Evidence |
|---|---|---|
| `adapters/claude.md`, `adapters/codex.md` | keep the branch, plus the SC3 edit | `f6eab7a`; `tests/test_shipped_text.py::test_adapter_keeps_a_continuing_author_and_a_fresh_independent_reviewer` |
| `project_templates/README.md.template`, `OVERVIEW.md.template` | keep the branch (user-owned; changed only on the branch) | merge `df75d26` |
| `src/agentic_mbse/cli/__init__.py`, `cli/installation.py`, `pyproject.toml`, `scripts/replicate_setup.sh` | keep the branch, plus this item's changes | `b961e56`, `0d01117`, and the report-once step |
| `CLAUDE.md`, `README.md`, `scripts/README.md` | keep the branch, plus the Phase 8 edits | Phase 8 docs step |
| `tests/test_cli.py`, `tests/test_installation.py`, `tests/test_packaged_guidance_contract.py` | keep the branch, with inventories derived from the tree | `b961e56` |
| `tests/test_modeling_command_contracts.py` | take main, re-pointed to `skills/<n>/SKILL.md`. **Its `:72` is the `main` test whose contract the envelope changes:** it expected `Task` in `orchestrate-modeling`'s frontmatter, and the envelope grants `Agent` | `ea64232` |
| `hooks/ruff-format.sh` | moved from `claude/hooks/`, `main`'s bytes and mode `100755` | `ea64232` (R100); `check` compares the installed hook with `main`'s |
| `docs/patterns/adr002-calculations.md`, `mbse-concepts.md` | take main (git's clean merge) | `check` compares the source bytes with `main`'s |
| `.project/CURRENT_WORK.md` | `wrap-split`'s side (merge conflict) | merge `df75d26` |
| `.project/active/spike-native-skill-install/findings.md`, `installer-findings.md` | take main where they differ: `main` adds one 2026-10-04 status line to each | merge `df75d26` |
| `.project/research/20260907-162310_native-claude-codex-skills.md` | identical on both sides | merge `df75d26` |
| fusion-tea `.agentic-mbse/codex.md:11` (the `.codex-test` worktree paragraph) | target-owned: moves to fusion-tea's `AGENTS.md` | `fusion-tea-target-owned.patch`; ledger row |
| fusion-tea `modeling_project/MODELING_GUIDE.md:276` (the pattern-location note) | target-owned: moves to fusion-tea's `AGENTS.md` | `fusion-tea-target-owned.patch`; ledger row (with the conflict and refresh facts, D10) |
| fusion-tea `modeling_project/MODELING_PROCESS.md:17` and `:34` (the MR-7 paragraphs) | target-owned: stay in place, kept by answering the re-init prompt (runbook step 4) until Item 2 lands the general section | ledger row; rehearsal confirmations |
| This repo's tracked `.claude/` copies (9 commands, the absolute `pdf-analysis` link, 3 supporting skills, 5 agents, the hook) | removed (D13); `.claude/settings.json` stays | `ea64232` |
| This repo's tracked tool-owned template copies (`modeling_project/MODELING_GUIDE.md`, `modeling_project/MODELING_PROCESS.md`, `work/EPIC_GUIDE.md`, `work/backlog/epic_template.md`) | kept, known stale (R7); cleanup is a follow-up | unchanged by this item |
| The branch's reflow-only changes (`agents/sysml-expert.md`, `skills/python-debugger/references/debugging_internals.md` and the bodies the branch reflowed) | dropped: the regenerated text takes `main`'s bytes | `f68ae0a`; `check` |
| The branch adaptations `main` made unnecessary (`audit-models` `AskUserQuestion`; `implement-model`, `orchestrate-modeling`, `plan-model` `Task`) | dropped: `main`'s rewrite no longer has the text | design Appendix A, last paragraph |

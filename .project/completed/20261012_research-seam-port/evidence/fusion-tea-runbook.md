# fusion-tea switch to the installed research seam (O3)

O3 moves fusion-tea's agentic-mbse pin to the merged `research-seam-port` and re-runs `init`, so fusion-tea's branch `research-seam-port` runs on the installed package and receives the `research-acquire` skill. It runs after the owner merges and pushes agentic-mbse `research-seam-port`, by the orchestrator or the owner. The owner then pushes and merges the fusion-tea branch.

The branch already holds the content change, commit `940500788`: Zotero ingest registers through `agentic_mbse.research`, the two seam scripts, the local command and the old guide are deleted, the guard is named in `pyproject.toml`, and `CLAUDE.md:11` points at the installed skill (`evidence/o1-fusion-tea-branch.md`). That commit cannot run on the current pin, because `ac5fb1a` has no `agentic_mbse.research`. So the branch merges only together with this pin move.

`FT=/home/reid/1cfe/fusion-tea-research-seam`, the worktree holding the branch. Run every command from `$FT`. Never touch the owner's main fusion-tea checkout.

## Before you start

- agentic-mbse `research-seam-port` is merged to `main` and pushed. Record the merge commit's full SHA as M. A pin can name only a pushed commit.
- `git status --short` in `$FT` is empty, and `git log --oneline c42ed1d8a..HEAD` shows `940500788`.
- agentic-mbse's dependencies are unchanged since the current pin: `git -C /home/reid/1cfe/agentic-mbse diff ac5fb1a M -- pyproject.toml` prints nothing. It printed nothing at the branch tip on 2026-10-12. If it prints a change, the hand-edited lock below is not enough; stop and re-plan the pin move.
- fusion-tea `main` may have moved. `git fetch origin && git log --oneline c42ed1d8a..origin/main -- scripts/research_seam.py scripts/source_registry.py scripts/zotero_ingest.py scripts/zotero_lib.py scripts/holdout_guard.py tests/research .claude/commands/research-acquire.md docs/research_seam_operator_guide.md CLAUDE.md pyproject.toml`. If it lists a commit, rebase the branch onto `origin/main` and reconcile: a change to a deleted script must reach agentic-mbse's package first, or this switch drops it.

## Step 1: move the pin

1. `uv pip list > /tmp/o3-pip-before.txt`.
2. In `pyproject.toml` (`[tool.uv.sources]`, line 36), set agentic-mbse's `rev` to M.
3. In `uv.lock`, replace `ac5fb1adfab0bc10e0010211275269f9f82d8e99` with M by hand (`sed -i`). It sits at `:48` (the `source =` line) and `:761` (fusion-tea's requires-dist entry, extras `extract-full` and `web`). `grep -c` the old SHA before (2) and after (0). Do not run `uv lock`: under uv 0.10 it fails on sysml-codegen's path source.
4. `uv sync --frozen --extra e2e`, then `uv pip install --no-deps syside-license==0.3.6`.
5. `uv pip list > /tmp/o3-pip-after.txt` and diff the two lists. The only expected change is agentic-mbse's own version. If anything else was removed, restore it.
6. `uv lock --check` reports the lock fresh.

## Step 2: update the provenance test

`tests/test_dependency_provenance.py:15` (`A_FINAL`) hard-codes `ac5fb1adfab0bc10e0010211275269f9f82d8e99`. Set it to M. One of its tests needs the four `STOP_PARSER_*` paths from `docs/integration_seam_operator_guide.md`. Then `uv run --no-sync pytest tests/test_dependency_provenance.py -q` passes.

## Step 3: re-run init

`uv run --no-sync agentic-mbse init . < /dev/null`

It installs the `research-acquire` skill under `.claude/skills/` and `.agents/skills/`, and refreshes `manage-sources`, `run-goal`, `research`, `source-traceability`, `onboard` and `toolkit-awareness` to the merged text. The goal runbook (`work/orchestration/GOAL_RUNBOOK.md`) gains the class-to-outcome table. `.gitignore` already has the two registry lines (`:35-36`), so `init` reports nothing to append. The local `/research-acquire` command was deleted in `940500788`, so no command and skill share the name.

In this worktree, `init` renders the worktree venv's absolute docs path into `.codex/agents/{kerml,syside,sysml}-expert.toml` (tracked) and their manifest hashes. The role sources did not change in this item. So restore those three files and their `.agentic-mbse/install.json` entries from `HEAD`, keeping the main checkout's paths, as goal-layer-port's F2 did.

## Step 4: verify

- `uv run --no-sync agentic-mbse install-commands --list` names `research-acquire`.
- `uv run --no-sync agentic-mbse research verify` exits 0. It prints the three legacy findings from before plus the two `legacy block_without_row` lines (`evidence/o1-parity-early.md`): `0 fault(s), 5 legacy entry(ies)`.
- `uv run --no-sync pytest tests/research -m "" -q`: 34 passed at `940500788`.
- `git status --short` shows only `pyproject.toml`, `uv.lock`, `tests/test_dependency_provenance.py`, the installed skill paths `init` wrote, `.agentic-mbse/install.json`, and refreshed managed files. No `knowledge/` change. No role-file path change after the restore.

## Step 5: commit, then merge

Check that `git diff --cached --name-only` is empty, then commit with explicit paths: "Pin agentic-mbse to M and re-init: research-acquire installs from the toolkit". The owner pushes the branch and merges it.

After the merge, in the owner's main checkout: pull, `uv sync --frozen --extra e2e`, `uv pip install --no-deps syside-license==0.3.6`, `uv run --no-sync agentic-mbse init . < /dev/null`. `git status` is clean.

## Owner decisions left open by this item

- **The ITER Cryoplant and Demattè & Bruzzone index blocks.** They point into baseline legacy orphan directories, so `verify` reports them as `legacy`. Register them properly, or leave them as legacy (Align, 2026-10-12).
- **`docs/exploratory-modeling/part-3-harness.html`**, the published write-up, still names the deleted scripts in its narrative and layout tables. It was treated as a historical publication and left unchanged. Whether to refresh it is the owner's call.

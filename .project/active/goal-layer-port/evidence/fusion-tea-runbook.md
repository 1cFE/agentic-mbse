# fusion-tea switch to the installed goal layer (F2)

F2 is the second fusion-tea commit on `goal-layer-mr7` (design D13). It moves fusion-tea's pin to the merged agentic-mbse, removes fusion-tea's local goal skills and its copies of the tool-owned goal and process files, and re-runs `init`, so that every one of them is the installed copy. It runs after the owner merges and pushes agentic-mbse `goal-layer-port`, by the orchestrator or the owner (design § Integration Strategy). The owner then pushes and merges `goal-layer-mr7`.

The steps follow design Appendix D4 and Item 1's pin move (`.project/completed/20261009_native-skill-distribution/evidence/fusion-tea-runbook.md`). Orchestrator phase O2 rehearses steps 3 to 5 on a disposable copy of the F1 tip, with `init` run from the agentic-mbse branch instead of a moved pin; it fills each "Observed in the rehearsal" slot from `fusion-tea/rehearsal/`. Steps 1 and 2 need the merged SHA, so the rehearsal cannot run them.

`FT=/home/reid/1cfe/fusion-tea-goal-layer`, the worktree holding `goal-layer-mr7`. Run every command from `$FT`. An agent that must not `cd` there can prefix `git -C "$FT"` and `uv --directory "$FT"` instead. Never touch the owner's main fusion-tea checkout.

## Before you start

- agentic-mbse `goal-layer-port` is merged to `main` and pushed. Record the merge commit's full SHA as M. A pin can name only a pushed commit.
- `git status --short` in `$FT` is empty, and `git log --oneline b06585709..HEAD` shows the F1 commit (`32bd4529a`), the narrative-link commit (`1b8d6fbff`) and the runbook re-sync after the audit follow-ups (`715a11e6e`). If agentic-mbse changes a goal or process template again before M, step 3's deletions let `init` write the new bytes ("MR-7 applies agentic-mbse's design-choice pattern; goal files at the shipped bytes").
- agentic-mbse's dependencies have not changed since the current pin: `git -C /home/reid/1cfe/agentic-mbse diff adbef75 M -- pyproject.toml` prints nothing. It printed nothing at this branch's tip when this runbook was written. If it prints a change, the hand-edited lock in step 1 is not enough; stop and re-plan the pin move.
- Check whether fusion-tea `main` changed the files F1 and F2 replace since `2b1e9f9d5`: `git fetch origin && git diff 2b1e9f9d5 origin/main -- .claude/skills/run-goal .claude/skills/narrate-goal work/orchestration/GOAL_RUNBOOK.md work/orchestration/goal-templates modeling_project/MODELING_PROCESS.md modeling_project/REQUIREMENTS.md`. If it prints a change to a goal file or `MODELING_PROCESS.md`, stop: that change must reach agentic-mbse or its fusion-tea home first, or this switch drops it. A change to MR-7 must be reconciled with F1's MR-7 text when the branch merges.

**Observed in the rehearsal (O2, 2026-10-12):** fusion-tea `main` had moved to `b06585709` (its PR #122) before F1, so `goal-layer-mr7` is cut from `b06585709`, not `2b1e9f9d5`; read `2b1e9f9d5..HEAD` above as `b06585709..HEAD`. The branch holds two commits: F1 `32bd4529a` and `1b8d6fbff`, which repoints 21 goal-narrative links that PR #122's archive of `demo-depth-rubric` missed (without it, fusion-tea's own `test_goal_contract.py` fails on `main`). PR #122 changed only path citations in the files F1 replaces; F1 carries them. Re-run the `origin/main` diff from `b06585709` before F2.

## Step 1: move the pin

1. Save the environment's package list: `uv pip list > /tmp/f2-pip-before.txt`.
2. In `pyproject.toml` (`[tool.uv.sources]`), set agentic-mbse's `rev` to M.
3. In `uv.lock`, replace the old SHA `adbef75981f7b30657efe37718a20b4b77da4e26` with M by hand, for example with `sed -i`. It sits on the agentic-mbse `source =` line and in fusion-tea's own requires-dist entry. `grep -c` the old SHA before and after; after must be 0. Do not run `uv lock`: under uv 0.10 it fails on sysml-codegen's path source.
4. `uv sync --frozen --extra e2e`. The sync is exact, so it removes anything outside the lock's selection.
5. `uv pip list > /tmp/f2-pip-after.txt` and `diff /tmp/f2-pip-before.txt /tmp/f2-pip-after.txt`. Restore every removed package except agentic-mbse's own version change. Earlier moves had to restore `syside-license==0.3.6` with `uv pip install --no-deps syside-license==0.3.6`, and `greenlet` 3.3.2, which `--no-deps` restores do not bring back; the `e2e` extra should now keep it.
6. `uv lock --check` reports the lock fresh.

**Observed in the rehearsal:** not rehearsed (O2 runs `init` from this worktree's environment; no pin moved). Verified 2026-10-12: `grep -c adbef75 uv.lock` → 2, at the agentic-mbse `source =` line (`:48`) and fusion-tea's requires-dist entry (`:761`), both with the full SHA `adbef75981f7b30657efe37718a20b4b77da4e26`.

## Step 2: update the provenance test

`tests/test_dependency_provenance.py` hard-codes the agentic-mbse SHA (`A_FINAL`, near the top). Set it to M, then run `uv run --no-sync pytest tests/test_dependency_provenance.py -q`; it passes.

**Observed in the rehearsal:** not rehearsed (no pin moved).

## Step 3: remove the local goal layer and the tool-owned copies

This is design Appendix D2 step 1, done for real.

1. `git rm -r -q .claude/skills/run-goal .claude/skills/narrate-goal .agents/skills/run-goal .agents/skills/narrate-goal`
2. In `.gitignore`, delete the two whitelist lines `!.claude/skills/narrate-goal/` (`:25`) and `!.claude/skills/run-goal/` (`:27`). Find them by text; the other lines stay.
3. In `AGENTS.md:5`, change "Local goal and study skills" to "Local study skills". Nothing else on the line changes.
4. `rm modeling_project/MODELING_PROCESS.md work/orchestration/GOAL_RUNBOOK.md work/orchestration/goal-templates/{goal,trail,learnings}.md`

Why remove the five files when F1 already set them to the shipped bytes: `init` then writes the merged bytes and records each in the install manifest. If agentic-mbse changed one of them after F1, `git diff` shows that change in step 5. It is expected, and it is not a loss.

**Observed in the rehearsal:** applied on a detached copy of `32bd4529a` exactly as written: `git rm` of the four goal-skill paths, the two `.gitignore` lines removed, `AGENTS.md:5` reworded, the five tool-owned files removed.

## Step 4: re-run init

`uv run --no-sync agentic-mbse init . < /dev/null`

This is fusion-tea's own CLI at M. With no terminal, `init` keeps a differing file it does not manage instead of prompting. After step 3 none of the goal or process files should hit that rule.

**Observed in the rehearsal:** `uv run --project <agentic-mbse worktree> agentic-mbse init <copy> < /dev/null`, rc 0 (`fusion-tea/rehearsal/init.txt`). No "Preserving" line at all. Created: the two `.agents/skills` bundles, `MODELING_PROCESS.md`, the runbook, the three goal templates, `tests/orchestration/test_narrative_links.py`; `MODELING_GUIDE.md` updated with no prompt; `.claude/skills/run-goal` and `narrate-goal` became links. Fourteen user files skipped, `REQUIREMENTS.md` among them. Because `init` ran from this worktree's environment, the three `.codex/agents/*.toml` roles were re-rendered with this worktree's docs path; fusion-tea's own CLI at M keeps its venv path, so expect no such diff in F2.

## Step 5: verify

- The init output has no "Preserving" line for the goal runbook, the three goal templates or `MODELING_PROCESS.md`. `modeling_project/MODELING_GUIDE.md` is updated with no prompt, because its manifest baseline matches.
- `git status --short` matches the rehearsal's `fusion-tea/rehearsal/git-status.txt`. Add the step 1 and 2 files (`pyproject.toml`, `uv.lock`, `tests/test_dependency_provenance.py`) and any shipped file agentic-mbse changed between the rehearsal and M.
- `.agentic-mbse/install.json` has an entry for `work/orchestration/GOAL_RUNBOOK.md`, the three goal templates, `tests/orchestration/test_narrative_links.py` and `modeling_project/MODELING_PROCESS.md`, each equal to the file's `sha256sum`.
- `git status --short -- work/orchestration/goals work/narratives` prints nothing.
- `uv run --no-sync pytest tests/orchestration -q` passes both tests over the 12 narratives: fusion-tea's own `test_goal_contract.py`, with its ADR-register check, and the installed `test_narrative_links.py`.
- `grep -n '^## ' work/orchestration/GOAL_RUNBOOK.md` still lists the headings fusion-tea records cite (`modeling_project/STUDY_POLICY.md:162`, the run-study runbook `:75` and `:219`, the goal files): "What \"fresh\" means", "Review scope and evidence reuse", "Grounding a goal", "The pre-execution disposition checkpoint", "The fresh review", "When a cited artifact moves", "Limits".
- `.agents/skills/run-goal/SKILL.md` and `.agents/skills/narrate-goal/SKILL.md` are the installed bundles, and `ls -l .claude/skills/run-goal .claude/skills/narrate-goal` shows links into `.agents/skills/`, as for every shipped skill.
- The resolver hop, in fusion-tea's own environment: `uv run --no-sync python -c 'from agentic_mbse.cli import get_docs_dir; p = get_docs_dir() / "patterns" / "design-choices.md"; print(p, p.exists())'` prints a path inside fusion-tea's environment and `True`. The rehearsal could show this hop only from the agentic-mbse branch's environment, because the old pin lacks the file. This run is the proof that MR-7's chain resolves in fusion-tea.
- The MR-7 chain, each link resolving:
  - `CLAUDE.md:5` links to the MR-7 anchor, and `grep -nx '### MR-7: Preserve Design Choices; Separate Evaluation from Design Selection' modeling_project/REQUIREMENTS.md` finds the heading;
  - MR-7 cites `design-choices.md` through the resolver, which the previous check resolved;
  - `grep -c 'design-choices.md' modeling_project/MODELING_PROCESS.md` prints 3: the "Process Selection" row, the "Architecture & Design" clause and the technical-pattern row;
  - the installed goal template (`goal.md:29`), runbook (`GOAL_RUNBOOK.md:85`) and `.agents/skills/run-goal/SKILL.md:58` name `design-choices.md` or the design-choice pattern, and `modeling_project/REQUIREMENTS.md`.
- fusion-tea's `repair-goal-prompt.md:18` still says `MODELING_PROCESS.md` holds "MR-7 evidence and independent review obligations". It is left as it is (design § Potential Risks): a reader following it lands on the design-choice trigger and row.

**Observed in the rehearsal:** every check passed (`fusion-tea/rehearsal/`). `manifest.txt`: all six entries MATCH their `sha256sum`. `goal-data-status.txt`: empty after `init`. `pytest.txt`: 3 passed (`test_register_is_coherent`, fusion-tea's narrative check and the installed one over the 12 narratives), once `1b8d6fbff` is applied; before it, both narrative checks failed on the same archived link, as they do on fusion-tea `main`. `headings.txt`: all 16 H2 headings identical to fusion-tea's runbook at `2b1e9f9d5`, including every heading fusion-tea records cite. `chain.md`: every link resolves; the resolver hop ran in this worktree's environment, because the pin `adbef75` has no `design-choices.md`, so the in-environment check above is F2's real proof. `git-status.txt` beyond the expected paths: `.agentic-mbse/install.json`, five `.agents/skills` files this item changed (model-validation, orchestrate-modeling, requirements-tracking, review-model, sysml-conventions and its `references/stencils.md`), and the three `.codex/agents/*.toml` noted in step 4.

## Step 6: commit

Stage the paths from step 5's `git status` by name, not with `git add -A`. Include the new installed files: `.agents/skills/run-goal/`, `.agents/skills/narrate-goal/` and `tests/orchestration/test_narrative_links.py`. A subject that fits: "Use agentic-mbse's installed goal layer at M". Do not push.

The owner then pushes `goal-layer-mr7` and merges it. That is step 3 of the merge order in `.project/active/wrap-split-migration-ledger.md` § Item 2.

**Observed in the rehearsal:** not committed; the copy was discarded.

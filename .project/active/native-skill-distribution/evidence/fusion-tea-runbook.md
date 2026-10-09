# fusion-tea switch-over after the native-skill merge

Every step here is the owner's. Nothing in this item writes to fusion-tea. The observed effects come from rehearsals on copies of fusion-tea at `403716ee3` (`evidence/rehearsal.md`, raw outputs in `evidence/rehearsal/`).

Two choices are yours and are not decided here: the install mode (step 3) and what to do with fusion-tea's pattern note (last section).

## Before you start

- Merge `nsd-integration` to `main` and push. The PR description should say the branch also carries `wrap-split`'s planning commits for other items (`research-seam-port`, the epic).
- Do not delete or move any agentic-mbse checkout before step 3. A legacy link is adopted only while its checkout root still has `src/agentic_mbse` (R4).
- If fusion-tea has moved past `403716ee3`, the rehearsal's numbers may differ slightly. Step 2's `git apply --check` tells you whether the patch still applies.

**Warning: Claude Code in fusion-tea is broken between two moments.** fusion-tea's `.claude/` holds 31 absolute links into `/home/reid/1cfe/agentic-mbse/claude/`. The merge removes `claude/`, so the links dangle from the moment that checkout moves to the merged `main` until step 3 finishes.

- Plain `init` runs from fusion-tea's own environment after step 1, so it can run **before** you move `/home/reid/1cfe/agentic-mbse`. Adoption reads only the link text and the checkout root, not the targets. That removes the broken window.
- `init --dev` must run from the moved checkout, so its window is the minutes between `git pull` and `init`.

## Step 1: move the pin

agentic-mbse's dependencies are unchanged between `c37ff53` and this branch: `git diff c37ff53 <merged SHA> -- pyproject.toml` changes only the packaged folders. [INHERITED: the 2026-10-04 pin move, fusion-tea commit `a2abea8df`]

1. In fusion-tea's `pyproject.toml` (`[tool.uv.sources]`), set `rev` to the merged SHA.
2. In `uv.lock`, replace the old SHA with the new one by hand (two occurrences, on the agentic-mbse `source =` line). Do not run `uv lock`: under uv 0.10 it fails on sysml-codegen's path source.
3. Run `uv sync --frozen`. It is exact: last time it removed `playwright`, `pyee` and `syside-license`. Restore them with `uv pip install --no-deps playwright==1.58.0 pyee==13.0.1 syside-license==0.3.6`.
4. `uv lock --check` reports the lock fresh.

Why first: PR #16's `/research` step relies on `--insights '[]'`, which `c37ff53` lacks, and the installed text should match the runtime that runs it.

## Step 2: land the target-owned text

1. `git apply --check <path>/fusion-tea-target-owned.patch` (this folder; built against `403716ee3`).
2. Apply it and commit it, citing the ledger rows (`.project/active/wrap-split-migration-ledger.md` in agentic-mbse, Item 1).

The patch appends two passages to `AGENTS.md`, which no re-init touches: the `.codex-test` worktree paragraph from `.agentic-mbse/codex.md:11`, and the pattern-location note from `modeling_project/MODELING_GUIDE.md:276`. Step 3 then replaces `codex.md` and the guide with no prompt, and nothing is lost: the rehearsal's provenance check found both passages in `AGENTS.md` and no other target-owned line removed.

## Step 3: choose the install mode and run it (your decision)

Both modes adopt all 31 legacy links, keep `MODELING_PROCESS.md` with both MR-7 paragraphs, leave fusion-tea's own skills, commands and agent alone, leave `pyproject.toml`, `uv.lock` and `.gitignore` unchanged, and change nothing on a second run. They differ here:

| Observed in the rehearsal | plain `init` | `init --dev` |
|---|---|---|
| Codex catalog | all 25 shipped skills, plus fusion-tea's 5 | **none of the 25 shipped skills**, only fusion-tea's 5 |
| Claude catalog | 18 shipped workflows and skills, 5 roles | same |
| Tracked files rewritten in place | 34: 26 under `.agents/skills/`, `.agentic-mbse/{codex.md,install.json}`, 5 `.codex/agents/*.toml`, `modeling_project/MODELING_GUIDE.md` | 7: `.agentic-mbse/{codex.md,install.json}` and the 5 Codex roles |
| Tracked files turned into absolute links | none | 33: all 31 files under `.agents/skills/`, `MODELING_GUIDE.md`, `work/EPIC_GUIDE.md`, each pointing into `/home/reid/1cfe/agentic-mbse/` |
| New untracked file | `.agentic-mbse/claude.md` | same |
| Prompts | 2: `MODELING_PROCESS.md`, `work/backlog/epic_template.md` | 1: `MODELING_PROCESS.md` |
| Hook | installed copy | link into the checkout's `hooks/` |
| Picking up later skill or template edits | another re-init | live, for skills and templates only; agents and adapters are copies [INHERITED: spec Open Questions] |
| Can run before the checkout moves | yes | no |

**Why Codex sees nothing under `--dev`.** `--dev` makes each `.agents/skills/<n>/SKILL.md` a file link to an absolute path in the checkout. Codex 0.160.0 lists no such skill; it does list fusion-tea's own skills, which are relative directory links inside the project. The behaviour predates this item and is filed as a follow-up. Until it is fixed, `--dev` leaves Codex in fusion-tea without the shipped workflows.

**Recommendation (agent-grade, `spec.md:99`): plain `init`.** fusion-tea commits its Codex install. `--dev` would turn 33 of those tracked files into machine-specific links, and the rehearsal shows Codex then loses every shipped skill. fusion-tea's Codex adapter also says these instruction assets are separate from the pinned runtime (`codex.md:11`). Ratified decision 3 named `--dev`; this evidence counts against it, and the choice is yours.

Commands:

- **Plain:** `cd /home/reid/1cfe/fusion-tea && uv run --no-sync agentic-mbse init .` This is fusion-tea's own CLI at the merged SHA.
- **`--dev`:** after moving the checkout, `uv run --project /home/reid/1cfe/agentic-mbse agentic-mbse init --dev /home/reid/1cfe/fusion-tea`. It needs the source checkout, so fusion-tea's own CLI cannot run it.

## Step 4: answer each prompt

Answer each prompt on its own. Do not use `S` or `O` (skip all, overwrite all).

- **`modeling_project/MODELING_PROCESS.md`: answer `s` (skip).** Not `b`: backup would replace the live file. Skipping keeps both MR-7 paragraphs (`:17`, `:34`) in force until Item 2 lands the general section.
- **`work/backlog/epic_template.md` (plain `init` only): answer `o` (overwrite).** [AGENT: orchestrator call, 2026-10-09] The entry is a link that an old `--dev` install made into the agentic-mbse checkout's tool-owned `project_templates/epic_template.md.template`. fusion-tea never wrote its content, and git does not track it (fusion-tea `.gitignore:32`). Overwriting removes the link, without writing through it, and installs the managed copy; nothing fusion-tea wrote is lost. Skipping would keep a live link into the checkout. This is not target-owned text, so it has no ledger row. `--dev` does not ask: it wants exactly that link.

The rehearsal saw no other prompt.

## Step 5: verify and commit

- The init report shows `Adopted (31)`, each line naming the old link.
- Check `git status`, not the report's Updated count. The installer lists every managed file it rewrites as Updated even when the bytes are unchanged (a known reporting quirk; a second run shows Updated (46) and changes nothing).
- `git status` should match the rehearsal's:
  - Plain: the 34 modified files in the step 3 table, and `?? .agentic-mbse/claude.md` (rehearsal: `evidence/rehearsal/plain-git-status.txt`).
  - `--dev`: 33 typechanges to links, 7 modified files, and `?? .agentic-mbse/claude.md` (`evidence/rehearsal/dev-git-status.txt`).
- `modeling_project/MODELING_PROCESS.md` still has its two MR-7 lines (`grep -c MR-7` prints 2).
- Claude Code lists the workflows. Under plain `init`, Codex lists all 25 shipped skills.
- Commit the result, including `.agentic-mbse/claude.md`.

## This repo

After moving `/home/reid/1cfe/agentic-mbse` to the merged `main`, run this from its root to get the workflows there (D13):

```bash
uv run agentic-mbse install-commands --assistant claude --link-mode symlink
```

It copies the skills, so re-run it after editing `skills/`. The rehearsal on a scratch clone of the branch printed `Installed: 38, Skipped: 0, Removed: 0, Adopted: 0`, left `git status` empty, kept `CLAUDE.md`, resolved all 25 bundles at `.claude/skills/<n>/SKILL.md` with the 5 agents and the hook, and left pytest at 2166 passed before and after.

## Your choice, does not block: fusion-tea's pattern note

After step 2, fusion-tea's pattern-location note lives in `AGENTS.md`. After step 1, you can keep it, drop it, or copy it into `CLAUDE.md`. The ledger row records the facts:

- After the re-init, Codex reads two conflicting instructions: the shipped guide says to locate pattern docs with the `get_docs_dir()` resolver, and `AGENTS.md` says to use `.agentic-mbse/patterns/`.
- That worktree copy equals `main`'s `docs/patterns/` today, but no installer refreshes it any more.
- The note's stated reason, that the copy is versioned separately from the pinned runtime, ends at step 1, when the pin moves to the merged SHA.

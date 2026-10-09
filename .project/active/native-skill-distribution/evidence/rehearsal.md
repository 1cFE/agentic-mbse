# fusion-tea rehearsal and fresh-install probes (plan 6.3, 7.4–7.7)

**Result.** Both install modes adopt all 31 legacy links, lose no target-owned text, keep `MODELING_PROCESS.md` with both MR-7 paragraphs, and leave fusion-tea's own entries, `pyproject.toml`, `uv.lock` and `.gitignore` alone. A second run changes nothing in git. The modes differ in what lands in git and in what Codex can see:

- Plain `init` rewrites 33 tracked files in place. Claude and Codex both discover every shipped skill.
- `init --dev` turns 33 tracked files into absolute links into the source checkout. **Codex then discovers none of the 25 shipped skills** (found case 1 below).

Raw outputs are in `evidence/rehearsal/`. The orchestrator ran `.orchestrate-logs/rehearsal/rehearse.sh` and `.orchestrate-logs/probe/probes.sh` on 2026-10-09 (the stage could not run `git init`, `git -C` or `cp -a`). The stage only read the outputs. The CLI was the worktree's at `2e04752`; nothing in `src/` changed after that commit.

## Setup

- **Pristine copy:** `.orchestrate-logs/rehearsal/fusion-tea/`, its own git repo, built by the orchestrator's `make-copy.sh` from fusion-tea at `403716ee3`. The orchestrator fixed that script during this item to re-point every link into `/home/reid/1cfe/agentic-mbse/`, not only `.claude/` links, and rebuilt the copy: 32 links re-pointed (the 31 `.claude/` links into the worktree's `claude/`, and `work/backlog/epic_template.md` into the worktree's `project_templates/`).
- **One copy per mode:** `cp -a` of the pristine copy (`rehearse.sh` `make_copy`). Before installing, the script stops if any link still points into the live checkout or the copy's git status is not clean.
- **Safety check, both copies** (`plain-setup.txt`, `dev-setup.txt`): clean; no link into the live checkout; 31 legacy links into `/home/reid/1cfe/agentic-mbse-nsd/claude/`, which does not exist, so every legacy link dangles.
- **Patch:** `git apply --check` passed on both copies (`*-patch-check.txt`). The patch was applied and committed in each copy before the install, so the install's effects stand alone. `AGENTS.md` is tracked by fusion-tea.
- **Install command:** `uv run agentic-mbse init <copy> [--dev] < /dev/null` from the worktree root. With no terminal, each would-be prompt prints a `Preserving …` line and keeps the file.

## The two modes side by side

| Effect | plain `init` | `init --dev` |
|---|---|---|
| Adopted (B3) | 31 | 31 |
| Created | `.agentic-mbse/claude.md` (untracked, not ignored) | same |
| Prompts (`Preserving` lines) | 2: `modeling_project/MODELING_PROCESS.md`, `work/backlog/epic_template.md` | 1: `modeling_project/MODELING_PROCESS.md` |
| Tracked files rewritten in place (`M`) | 33, plus `.agentic-mbse/install.json` (machine state): 26 files under `.agents/skills/` (25 `SKILL.md` and `python-debugger/references/debugging_internals.md`), `.agentic-mbse/codex.md`, 5 `.codex/agents/*.toml`, `modeling_project/MODELING_GUIDE.md` | 6, plus `install.json`: `.agentic-mbse/codex.md` and the 5 Codex roles |
| Tracked files turned into absolute links (`mode change … => 120000`) | none | 33: all 31 files under `.agents/skills/`, `MODELING_GUIDE.md`, `work/EPIC_GUIDE.md`. Here they point into the worktree; in the real run, into `/home/reid/1cfe/agentic-mbse/` |
| Report's Updated list | 39 (6 of them rewritten with identical bytes) | 6 |
| `.gitignore` | unchanged | unchanged (R5 holds) |
| `MODELING_PROCESS.md` | byte-identical to the reference; 2 MR-7 lines | same |
| Both SC9 passages in `AGENTS.md` | yes | yes |
| fusion-tea's own entries (`owner-entries.py`, 17 lines) | unchanged | unchanged |
| `pyproject.toml`, `uv.lock`, `CLAUDE.md`, user-owned files, `.claude/settings.json`, `.codex/config.toml` | unchanged | unchanged |
| Claude roles | rendered files | rendered files |
| Hook | real executable file | link to the worktree's `hooks/ruff-format.sh` |
| Worktree written through a link | no | no |
| Claude catalog | 18 shipped + fusion-tea's 6; 5 roles | same |
| **Codex catalog** | **25 shipped** + fusion-tea's 5 | **0 shipped** + fusion-tea's 5 |
| 7 reference skills at `.claude/skills/<n>/SKILL.md` | present | present |
| Second run | nothing adopted or created; same prompts; git status identical; report says Symlinked 25, Updated 46 | nothing adopted or created; same prompt; git status identical; report says Symlinked 60, Updated 12 |

## Plain `init` (7.4)

- **Adoption (`plain-init1.txt`):** `Adopted (31)`, each line naming its old link text. No adopted entry appears in another list. Symlinked (15) are the workflow aliases; the 10 supporting-skill aliases are listed only under Adopted.
- **Git (`plain-git-status.txt`, `plain-git-diff-summary.txt` empty, `plain-gitignore.diff` empty):** 34 tracked files modified and one untracked file, as in the table. No mode changes.
- **Rewritten with identical bytes:** 6 of the 39 Updated entries are not in git status: the 5 bundle resources under `pdf-analysis`, `python-debugger/scripts`, `sysml-conventions` and `toolkit-awareness`, and `work/EPIC_GUIDE.md`.
- **Confirmations (`plain-confirm.txt`):** every check in the stencil passed. `work/backlog/epic_template.md` is still fusion-tea's link (the prompt kept it).
- **On disk (`plain-disk.txt`):** the 7 reference skills are present and the hook is a real executable.
- **Second run (`plain-init2.txt`, `plain-git-status-after-init2.txt`):** git status is byte-identical to the first run's. See found case 2 for the report's numbers.

## `init --dev` (7.5)

- **Adoption (`dev-init1.txt`):** `Adopted (31)`, as in plain mode.
- **Links:** `dev-git-diff-summary.txt` lists the 33 typechanges. Each `.agents/skills/<n>/` is a real folder whose files are absolute links into the worktree's `skills/<n>/`.
- **`.gitignore` (`dev-gitignore.diff` empty):** unchanged. The old dev block's marker is already present, so `--dev` appends nothing (R5).
- **Hook (`dev-disk.txt`):** a link to `/home/reid/1cfe/agentic-mbse-nsd/hooks/ruff-format.sh`.
- **Worktree (`dev-worktree.txt`):** git status unchanged by the install, so nothing was written through a link into the source.
- **Prompt:** only `MODELING_PROCESS.md`. `--dev` wants `work/backlog/epic_template.md` to be exactly the link fusion-tea already has, so it matches and needs no prompt.
- **Second run:** git status identical.

## B4: nothing target-owned is lost (`*-provenance.txt`)

`provenance.py` compares every replaced file with the pristine copy and flags each removed line that no agentic-mbse revision of its source carries (`git log --all`). Plain mode flags 129 lines. Dev mode flags the same 129; only the order of two file entries differs, because dev lists `MODELING_GUIDE.md` and `EPIC_GUIDE.md` under Symlinked instead of Updated.

| Flagged lines | Count | What they are |
|---|---|---|
| The `.codex-test` paragraph (`codex.md:11`), in `codex.md` and in each of the 5 Codex roles | 6 | Target-owned; now in `AGENTS.md` (SC9) |
| The pattern-location note (`MODELING_GUIDE.md:276`) | 1 | Target-owned; now in `AGENTS.md` (SC9) |
| Block-list `allowed-tools:` lines in 11 workflows | 102 | Envelope output of an earlier, uncommitted native build |
| `Supporting skills: … Read their installed guidance when relevant.` | 11 | Same; one generated line per workflow |
| Quoted `description:` lines and their `'` continuation lines (4 supporting skills), and `backlog`'s description with `—` | 9 | Same; YAML quoting from that build |

Every flagged line is either one of the two SC9 passages, now in `AGENTS.md`, or tool text from an earlier native build. No target-owned text is lost.

**The 13 hand-updated payloads** (`.orchestrate-logs/nsd-inputs/fusion-tea/harness-right-size/installed.json`):

- The 11 `.agents/skills/*/SKILL.md` files are replaced with no prompt: rewritten in plain mode, turned into links in dev mode. Their flagged lines are all in the envelope rows above.
- `work/EPIC_GUIDE.md` is replaced with no prompt: rewritten with identical bytes in plain mode (fusion-tea's copy already equals this branch's template), a link in dev mode.
- `modeling_project/MODELING_PROCESS.md` is kept at its prompt in both modes.

## Fresh-install probes (6.3, SC7)

`probes.sh` made three `git init`ed targets with `init --assistant <a>` and ran the discovery probe (Claude Code 2.1.295, codex-cli 0.160.0). Log: `.orchestrate-logs/probe/probes.log`.

| Target | Claude skills | Claude roles | Codex skills | Errors | Probe exit |
|---|---|---|---|---|---|
| `claude` (`evidence/probe-fresh-claude.json`) | 18 | 5 | 25 | none | 0 |
| `codex` (`evidence/probe-fresh-codex.json`) | 0 | 0 | 25 | none | 1, by design: there is no `.claude/` |
| `both` (`evidence/probe-fresh-both.json`) | 18 | 5 | 25 | none | 0 |

The 18 are every bundle not marked `user-invocable: false`. On disk, in `claude` and `both`, each of the 7 `user-invocable: false` bundles has `.claude/skills/<n>/SKILL.md` and the hook is present.

## The scratch clone of this repo (7.6, D13)

- **Clone:** `nsd-integration` at `2e04752` (`clone-head.txt`), with `.env` copied and `uv sync --frozen --all-extras`.
- **Pytest before and after the install:** 2166 passed, 1 skipped, 5 deselected, 1 xfailed (`clone-pytest-before.txt`, `clone-pytest-after.txt`).
- **Install:** `uv run agentic-mbse install-commands --assistant claude --link-mode symlink` printed `Installed: 38, Skipped: 0, Removed: 0, Adopted: 0` and preserved `CLAUDE.md` (`clone-install.txt`).
- **Git:** `git status --porcelain` is empty (`clone-git-status.txt`), so the D13 ignore block covers everything the install writes.
- **Resolution (`clone-resolve.txt`):** all 25 bundles resolve at `.claude/skills/<n>/SKILL.md`; the 5 agents and the hook are present; `CLAUDE.md` is unchanged.

## Found cases

1. **`--dev` hides every shipped skill from Codex.** In the dev copy, Codex's catalog holds only fusion-tea's 5 skills. Under `--dev` each `.agents/skills/<n>/SKILL.md` is a file link to an absolute path outside the project, and Codex 0.160.0 lists none of them. Codex does list fusion-tea's own skills, which are relative directory links inside the project. Which property makes Codex skip them (a file link, or a target outside the project) was not isolated. The behaviour predates this item: native `86921f9` makes the same per-file links (`installation.py:107-109` there). No earlier probe ran Codex on a `--dev` install, and SC7's probes use plain `init`, so SC7 holds. It bears directly on the owner's install-mode choice (runbook step 3), and it is a product defect for any `--dev` user who runs Codex. Filed as a follow-up in `audit-scope.md`.
2. **The second run's report lists unchanged files as Updated.** `Installer.write` deletes and rewrites every existing managed file it is permitted to touch and reports it as Updated, whether or not the bytes changed (`installation.py:159-169`; the same in native `86921f9`). The plan's stencil expected "nothing updated" on a second run. Git status after the second run is identical to the first in both modes, so no tracked content changed. The runbook verifies by git status, not by the report's counts. Reporting only real changes is a follow-up.
3. **fusion-tea's `work/backlog/epic_template.md` is a link, not a file.** It is an absolute link into the checkout's tool-owned `project_templates/epic_template.md.template`, left by the old `--dev`. It is untracked and ignored (fusion-tea `.gitignore:32`). Design-review S8 and the design's Non-Goals assumed fusion-tea's template copies are real files. The legacy predicate covers only `.claude/<location>/<name>`, so plain `init` does not adopt the link and prompts for it; `--dev` matches it and does not. Replacing it with the installed copy loses nothing fusion-tea wrote; the runbook's step 4 records the answer.

## Known differences from the real run

- **CLI and docs path (R3).** The rehearsal ran the worktree's CLI, so rendered agents and `.claude/settings.json` record the worktree's `docs/` path. fusion-tea's own CLI at the merged SHA records its `.venv`'s packaged docs. Those packaged docs lack `docs/syside/python/v0.8.4/syside/` (the strict xfail in `tests/test_packaged_guidance_contract.py`; an open owner question).
- **Dangling links.** The copies' legacy links dangle. In the real run, a plain `init` before the checkout moves sees live links; Phase 5's existing-target cases cover that, and adoption never reads the target.
- **Link targets under `--dev`.** The dev copy's links point into the worktree. In the real run they point into `/home/reid/1cfe/agentic-mbse/`, as does `epic_template.md`'s, so step 4's prompts are the same.

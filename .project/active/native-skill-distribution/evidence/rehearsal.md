# fusion-tea rehearsal and fresh-install probes (plan 6.3, 7.4–7.7)

**Result.** Both install modes adopt all 31 legacy links, lose no target-owned text, keep `MODELING_PROCESS.md` with both MR-7 paragraphs, and leave fusion-tea's own entries, `pyproject.toml`, `uv.lock` and `.gitignore` alone. A second run changes nothing in git. Claude and Codex both discover every shipped skill in both modes. The modes differ in what lands in git:

- Plain `init` rewrites 33 tracked files in place.
- `init --dev` replaces the 31 tracked files under `.agents/skills/` with 25 absolute folder links into the source checkout, one per bundle, and turns 2 tracked templates into absolute links.

Raw outputs are in `evidence/rehearsal/`. **Current run (plan Phase 9, 2026-10-09):** the stage ran `.orchestrate-logs/rehearsal/rehearse.sh` with the CLI at `a42c4c9`, after `--dev` changed to link each bundle folder. Plain-mode outputs are byte-identical to the first run's, apart from the probe's Claude Code version (2.1.295 → 2.1.296). **First run:** the orchestrator ran `rehearse.sh` and `.orchestrate-logs/probe/probes.sh` with the CLI at `2e04752` (the stage then could not run `git init`, `git -C` or `cp -a`); its dev-mode numbers are kept below where they changed, marked "first run".

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
| Tracked files under `.agents/skills/` replaced by folder links | none | all 31 (git: 31 `D`), replaced by 25 untracked absolute folder links `.agents/skills/<n>`, one per bundle (git: 25 `??`). Committing them records 25 links in place of 31 files. First run: the 31 files became 31 file links (`T`) |
| Other tracked files turned into absolute links (`mode change … => 120000`) | none | 2: `MODELING_GUIDE.md`, `work/EPIC_GUIDE.md` |
| Where the links point | n/a | here, into the worktree; in the real run, into `/home/reid/1cfe/agentic-mbse/` |
| Report's Symlinked list | 15 (the workflow aliases) | 43: 25 bundle folders, 15 workflow aliases, 3 templates. First run: 49 |
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
| **Codex catalog** | **25 shipped** + fusion-tea's 5 | **25 shipped** + fusion-tea's 5 (first run: 0 shipped) |
| 7 reference skills at `.claude/skills/<n>/SKILL.md` | present | present |
| Second run | nothing adopted or created; same prompts; git status identical; report says Symlinked 25, Updated 46 | nothing adopted or created; same prompt; git status identical; report says Symlinked 54, Updated 12 |

## Plain `init` (7.4)

- **Adoption (`plain-init1.txt`):** `Adopted (31)`, each line naming its old link text. No adopted entry appears in another list. Symlinked (15) are the workflow aliases; the 10 supporting-skill aliases are listed only under Adopted.
- **Git (`plain-git-status.txt`, `plain-git-diff-summary.txt` empty, `plain-gitignore.diff` empty):** 34 tracked files modified and one untracked file, as in the table. No mode changes.
- **Rewritten with identical bytes:** 6 of the 39 Updated entries are not in git status: the 5 bundle resources under `pdf-analysis`, `python-debugger/scripts`, `sysml-conventions` and `toolkit-awareness`, and `work/EPIC_GUIDE.md`.
- **Confirmations (`plain-confirm.txt`):** every check in the stencil passed. `work/backlog/epic_template.md` is still fusion-tea's link (the prompt kept it).
- **On disk (`plain-disk.txt`):** the 7 reference skills are present and the hook is a real executable.
- **Second run (`plain-init2.txt`, `plain-git-status-after-init2.txt`):** git status is byte-identical to the first run's. See found case 2 for the report's numbers.

## `init --dev` (7.5)

- **Adoption (`dev-init1.txt`):** `Adopted (31)`, as in plain mode.
- **Links:** each `.agents/skills/<n>` is one absolute folder link into the worktree's `skills/<n>/`. Every shipped bundle folder was installer-owned, so each became a link and no "Copied … instead of linking it" line appears. `dev-git-diff-summary.txt` lists the 31 deletions under `.agents/skills/` and the 2 template typechanges; `dev-git-status.txt` adds the 25 untracked folder links. fusion-tea's own 5 `.agents/skills/` links (relative, into its `.claude/skills/`) are unchanged.
- **Codex (`dev-probe.json`):** 30 skills, the 25 shipped and fusion-tea's 5. Claude: 24 skills (18 shipped, fusion-tea's 6) and 5 roles. No errors.
- **`.gitignore` (`dev-gitignore.diff` empty):** unchanged. The old dev block's marker is already present, so `--dev` appends nothing (R5).
- **Hook (`dev-disk.txt`):** a link to `/home/reid/1cfe/agentic-mbse-nsd/hooks/ruff-format.sh`.
- **Worktree (`dev-worktree.txt`):** git status unchanged by the install, so nothing was written through a link into the source.
- **Prompt:** only `MODELING_PROCESS.md`. `--dev` wants `work/backlog/epic_template.md` to be exactly the link fusion-tea already has, so it matches and needs no prompt.
- **Second run:** git status identical.

## B4: nothing target-owned is lost (`*-provenance.txt`)

`provenance.py` compares every replaced file with the pristine copy and flags each removed line that no agentic-mbse revision of its source carries (`git log --all`). A replaced entry that was a real folder in the pristine copy, as each `--dev` bundle folder now is, stands for every file the pristine copy had in it (added in Phase 9; without it the dev run checked only 8 files). Plain mode flags 129 lines. Dev mode flags the same 129, and `dev-provenance.txt` is byte-identical to the first run's; only the order of two file entries differs from plain mode, because dev lists `MODELING_GUIDE.md` and `EPIC_GUIDE.md` under Symlinked instead of Updated.

| Flagged lines | Count | What they are |
|---|---|---|
| The `.codex-test` paragraph (`codex.md:11`), in `codex.md` and in each of the 5 Codex roles | 6 | Target-owned; now in `AGENTS.md` (SC9) |
| The pattern-location note (`MODELING_GUIDE.md:276`) | 1 | Target-owned; now in `AGENTS.md` (SC9) |
| Block-list `allowed-tools:` lines in 11 workflows | 102 | Envelope output of an earlier, uncommitted native build |
| `Supporting skills: … Read their installed guidance when relevant.` | 11 | Same; one generated line per workflow |
| Quoted `description:` lines and their `'` continuation lines (4 supporting skills), and `backlog`'s description with `—` | 9 | Same; YAML quoting from that build |

Every flagged line is either one of the two SC9 passages, now in `AGENTS.md`, or tool text from an earlier native build. No target-owned text is lost.

**The 13 hand-updated payloads** (`.orchestrate-logs/nsd-inputs/fusion-tea/harness-right-size/installed.json`):

- The 11 `.agents/skills/*/SKILL.md` files are replaced with no prompt: rewritten in plain mode, replaced with their bundle's folder link in dev mode. Their flagged lines are all in the envelope rows above.
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

**Fresh `init --dev` (plan 9.7, `evidence/probe-dev-folder-links.json`).** The stage ran `init --dev` (`--assistant both`) into a `git init`ed target, `.orchestrate-logs/probe/dev-folder-links/`, with the CLI at `a42c4c9`, then the probe (Claude Code 2.1.296, codex-cli 0.160.0): Claude 18 skills and 5 roles, Codex 25, no errors, probe exit 0. Each `.agents/skills/<n>` is one absolute folder link into the worktree's `skills/<n>`, no `SKILL.md` under `.agents/skills/` is a file link, the Claude aliases are relative links to `.agents/skills/<n>`, and the 7 `user-invocable: false` bundles have `.claude/skills/<n>/SKILL.md`.

## The scratch clone of this repo (7.6, D13)

- **Clone:** `nsd-integration` at `a42c4c9` (`clone-head.txt`; first run `2e04752`), with `.env` copied and `uv sync --frozen --all-extras`.
- **Pytest before and after the install:** 2177 passed, 1 skipped, 5 deselected, 1 xfailed (`clone-pytest-before.txt`, `clone-pytest-after.txt`; first run 2166). The install output, git status and resolution files are byte-identical to the first run's.
- **Install:** `uv run agentic-mbse install-commands --assistant claude --link-mode symlink` printed `Installed: 38, Skipped: 0, Removed: 0, Adopted: 0` and preserved `CLAUDE.md` (`clone-install.txt`).
- **Git:** `git status --porcelain` is empty (`clone-git-status.txt`), so the D13 ignore block covers everything the install writes.
- **Resolution (`clone-resolve.txt`):** all 25 bundles resolve at `.claude/skills/<n>/SKILL.md`; the 5 agents and the hook are present; `CLAUDE.md` is unchanged.

## Found cases

1. **`--dev` hid every shipped skill from Codex. Fixed in plan Phase 9.** In the first run's dev copy, Codex listed only fusion-tea's 5 skills, because `--dev` made each `.agents/skills/<n>/SKILL.md` a file link and Codex 0.160.0 lists no skill whose `SKILL.md` is a file link (the orchestrator's spike, `evidence/spike-dev-codex-links.md`). The behaviour predated this item (native `86921f9`, `installation.py:107-109` there). The owner chose to fix it (audit B1). `--dev` now links each bundle folder whole, and the re-run's dev copy shows Codex listing all 25 shipped skills plus fusion-tea's 5.
2. **The second run's report lists unchanged files as Updated.** `Installer.write` deletes and rewrites every existing managed file it is permitted to touch and reports it as Updated, whether or not the bytes changed (`installation.py:159-169`; the same in native `86921f9`). The plan's stencil expected "nothing updated" on a second run. Git status after the second run is identical to the first in both modes, so no tracked content changed. The runbook verifies by git status, not by the report's counts. Reporting only real changes is a follow-up.
3. **fusion-tea's `work/backlog/epic_template.md` is a link, not a file.** It is an absolute link into the checkout's tool-owned `project_templates/epic_template.md.template`, left by the old `--dev`. It is untracked and ignored (fusion-tea `.gitignore:32`). Design-review S8 and the design's Non-Goals assumed fusion-tea's template copies are real files. The legacy predicate covers only `.claude/<location>/<name>`, so plain `init` does not adopt the link and prompts for it; `--dev` matches it and does not. Replacing it with the installed copy loses nothing fusion-tea wrote; the runbook's step 4 records the answer.

## Known differences from the real run

- **CLI and docs path (R3).** The rehearsal ran the worktree's CLI, so rendered agents and `.claude/settings.json` record the worktree's `docs/` path. fusion-tea's own CLI at the merged SHA records its `.venv`'s packaged docs. Those packaged docs lack `docs/syside/python/v0.8.4/syside/` (the strict xfail in `tests/test_packaged_guidance_contract.py`; an open owner question).
- **Dangling links.** The copies' legacy links dangle. In the real run, a plain `init` before the checkout moves sees live links; Phase 5's existing-target cases cover that, and adoption never reads the target.
- **Link targets under `--dev`.** The dev copy's links point into the worktree. In the real run they point into `/home/reid/1cfe/agentic-mbse/`, as does `epic_template.md`'s, so step 4's prompts are the same.

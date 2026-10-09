# Implementation Plan: Reconcile the native installer source with `main` (WRAP-SPLIT Item 1)

**Status:** In Progress
**Created:** 2026-10-09
**Last Updated:** 2026-10-09
**Branch:** `nsd-integration` in the worktree `/home/reid/1cfe/agentic-mbse-nsd`, cut from `wrap-split` at the commit that carries this plan (set up by the orchestrator)

## Source Documents

- **Spec (the contract):** `spec.md`, SC1–SC12
- **Design:** `design.md`, revised after `design-review.md` ← decisions D1–D13, invariants I1–I9, architecture, Appendix A (adaptation list) and Appendix B (file-level changes)
- **Design review:** `design-review.md` § Resolutions
- **Align record:** `briefs/00-align.md`. Plan brief: `briefs/05-plan.md`
- **Read-only inputs:** `.orchestrate-logs/nsd-inputs/` (native branch at `86921f9`, fusion-tea files at `403716ee3`)

Paths above are in `.project/active/native-skill-distribution/`. "Native `file:line`" cites the native snapshot in `.orchestrate-logs/nsd-inputs/native/`; after the merge those files are the branch side, so the same lines apply.

## The Point

[NEED] (owner, verbatim, `briefs/00-align.md:19`) "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this".

[AGENT] (the orchestrator's reading at Align; the owner did not object; `briefs/00-align.md:41`, `spec.md:77`) One place to register a skill. After this item, one tool-neutral source tree (`skills/`, `agents/`, `adapters/`, `hooks/`, `project_templates/`) carries `main`'s current text. It is the only thing the installer reads, and `agentic-mbse init` installs it the same way for Claude Code and Codex.

Why now: Items 2 and 5 register new skills, and Item 4 edits shipped text. Until the two installer sources become one, each of those edits lands twice, or lands behind a 58-commit gap.

fusion-tea carries two owner criteria (`[NEED]`, epic `:65-66`): no loss of information, and MR-7 enforcement intact after re-init. Its Claude side is 31 absolute links into `/home/reid/1cfe/agentic-mbse/claude/`, which this merge deletes. So the installer must take those links over, and the owner needs a rehearsed runbook.

The bar for the code (`briefs/05-plan.md:9`): mostly deletion, one predicate inside `permit`, no new parallel mechanisms, tests that pin properties rather than inventories. If a step tempts you to add a list, a registry, a second removal path or a hard-coded count, stop. That is the thing this item removes.

## Ground rules for the implementer

- **Where:** run every command from the worktree root `/home/reid/1cfe/agentic-mbse-nsd` unless a step says otherwise.
- **[HARD] Never touch `/home/reid/1cfe/agentic-mbse`.** No `cd`, no git command, no install, no write there. fusion-tea's Claude Code reads its `claude/` live.
- **Never install into the worktree root.** Until commit 3 the worktree tracks `.claude/skills/pdf-analysis` as an absolute link into the live checkout. Every `init` or `install-commands` targets a scratch folder under `.orchestrate-logs/` (gitignored).
- **Never write fusion-tea.** Rehearse on copies only. The SC9 change is a patch file.
- **Never run `uv` inside a fusion-tea copy.** fusion-tea's own `pyproject.toml` would be synced. Pass the copy as the `init` path argument from the worktree root. The only nested `uv` runs are the lint-baseline export (1.2) and the scratch clone of this repo (7.6).
- **Installs are non-interactive.** Redirect stdin from `/dev/null`. Each would-be prompt then prints as a `Preserving modified or untracked file:` line (native `cli/__init__.py:410-414`).
- **Claude CLI subprocesses:** redirect output to a file and read it back (CLAUDE.md, "Extract commands inside Claude Code"). The discovery probe writes its JSON with `--output`.
- **Sandbox:** stage agents may be denied reads outside the worktree. Each step that could hit this names its fallback. If none applies, stop and return the blocker.
- **Owner-reserved, never done here:** merging to `main`, pushing, any write to fusion-tea, choosing fusion-tea's install mode, and keeping or dropping fusion-tea's pattern note.
- **Stop rules are real.** When a decision rule below says stop, stop and return the evidence to the orchestrator. Do not improvise a resolution on code or shipped text.
- **Commits:** on `nsd-integration`, as listed per phase, each message leading with the outcome. No push.

## Evidence layout

`evidence/` means `.project/active/native-skill-distribution/evidence/`. Scratch work goes under `.orchestrate-logs/` (gitignored) and is not evidence.

| File | What it proves | Phase |
|---|---|---|
| `adaptations.yaml`, `reconcile.py` | The one-time tooling (D2–D4) | 2 |
| `probe-b2-*.json` | B2: both clients tolerate the kind field | 1 |
| `check-commit2.txt`, `check.txt`, `check-rows.md`, `check-negative.txt` | SC2, and SC1's generated rows | 2, 6 |
| `probe-fresh-{claude,codex,both}.json` | SC7 discovery | 6 |
| `dispositions.md` | SC1 | 6 |
| `fusion-tea-target-owned.patch` | SC9 | 7 |
| `rehearsal.md` and `rehearsal/` (raw outputs) | SC8, SC10, the D13 scratch clone | 7 |
| `fusion-tea-runbook.md` | SC10 | 7 |
| `lint-parity.md` | SC12 | 8 |
| `audit-scope.md` | SC11 hand-off | 8 |

Migration-ledger rows go to `.project/active/wrap-split-migration-ledger.md` (7.3). This item creates the file; Item 2 owns it.

## Implementation Strategy

**Phasing rationale.** The commit order is fixed by the design's integration flow and S1. A reviewer of the PR sees a mechanical merge, then the regenerated text alone, then the deletion of `claude/` alone, then installer code. Inside that order, each risk is retired as early as possible:

1. B2 (`metadata.kind`) is probed right after the merge, before `reconcile.py` writes the field into 25 files.
2. `reconcile.py check` is written before `write`. It must fail on the branch's old text before it is trusted to pass on the regenerated text.
3. Installer work comes in two passes: first the deletions that make the tree the inventory, then the one new predicate.
4. Evidence that needs the final installer (probes, rehearsals) comes after both passes, then docs and the gate.

**Critical path.** Merge → B2 decision → `check`, then `write` (commit 2) → remove `claude/` (commit 3) → tree as inventory (Phase 4) → legacy adoption (Phase 5) → content evidence (Phase 6) → fusion-tea rehearsal and runbook (Phase 7) → docs and gate (Phase 8) → independent audit (orchestrator).

**First proof point.** The B2 probe lists the same names with the field as without it. Then `reconcile.py check --main 8f43a09` exits 0 on a fresh install of commit 2. Together these show the content half is mechanical.

**Biggest risks.**

- B2: a client drops bundles with the field (Phase 1 probe; fallback named).
- B1: the adaptation list is incomplete (Phase 2 exact counts; Phase 4 text property tests).
- The sandbox blocks the probe or the fusion-tea copy script (fallbacks named in 1.6 and Phase 7).
- B3/B4: links not adopted, or target-owned text lost at re-init (Phase 7 rehearsal).
- Lint parity makes pre-existing findings in files this item edits its job (Phase 8).

### SC traceability

| SC | Proven by (checkbox IDs) |
|---|---|
| SC1 | 1.4 (merge resolutions recorded), 6.4 (`dispositions.md`) |
| SC2 | 2.4–2.6 (`check` fails on commit 1, passes on commit 2), 6.1–6.2 (final `check`, negative self-check) |
| SC3 | 5.6–5.7 (adapter text, property test) |
| SC4 | 2.6 (guide equals `main` plus A17, through `check`), 4.7 (installed guide names no `.claude/settings.json`) |
| SC5 | 4.4–4.6 (derived tests, fake-root test, I7 test, `--list` by kind) |
| SC6 | 3.1 (hook `git mv`, `claude/` gone), 4.8–4.9 (hook, `--dev`, wheel tests) |
| SC7 | 4.6–4.7 (reachability and text property tests), 6.3 (probes on three fresh installs) |
| SC8 | 5.1–5.5 (predicate and adoption tests), 7.4–7.5, 7.7 (rehearsal: 31 adopted, catalogs, owner entries untouched) |
| SC9 | 7.2–7.3 (patch, ledger), 7.4 (passages present after re-init) |
| SC10 | 7.4–7.8 (both modes rehearsed, scratch clone, runbook) |
| SC11 | 8.6–8.7 (audit scope; dated verdict after the audit stage) |
| SC12 | 1.2 (lint baseline), 3.3 (I9), 8.1–8.5 (docs, pytest, parity, history) |

Product-lens falsifiers (`product-lens.md:35`): (a) by 4.5; (b) by 6.1–6.3; (c) by 7.4–7.5.

### Refinements to the design (no decision changed)

These sharpen how a fixed decision is carried out. They are listed so the auditor does not read them as drift.

- **Merge resolution is per conflicted path, not per folder** (D2). Taking the branch's whole `project_templates/` or `src/` would silently revert `main`'s post-fork changes there (`main` changed `EPIC_GUIDE.md.template`, `pm_cli.py` and more; `.orchestrate-logs/nsd-inputs/fork-to-main.names`). Only conflicted paths get a side; git's clean merge stands elsewhere.
- **Two `.project/`-only commits sit before commit 2:** the B2 evidence, and the tooling. Commit 2 still carries only `write`'s output (S1).
- **`check` compares the installed hook, not the source hook,** against `main`'s bytes and mode. The installed copy is what users get, and `check` then runs unchanged before and after the hook moves.
- **`check` takes the expected preface from the native commit `86921f9`,** not from `write`'s constant. That keeps the two independent (M4).
- **Probe expectations on the fusion-tea copy are supersets.** fusion-tea's own skills and commands also appear in both catalogs, so the probe's built-in exact-count asserts fail there by design. Read the JSON instead.
- **Codex role discovery is checked structurally.** It cannot be observed without model turns (spike `findings.md:29`). pytest checks the rendered TOML and its registration.

---

## Phase 1: Merge mechanically, then settle B2

### Goal
Commit the merge of the native branch with a mechanical resolution, capture `main`'s lint baseline, and decide the kind field's form with the discovery probe before any code writes it.

### Assumption Under Test
- The merge conflicts only where the design predicts (design § Implementation Notes, "Merge commit").
- B2: Claude Code and Codex both still list every bundle when its `SKILL.md` frontmatter carries an unrecognized `metadata:` map.

### Test Stencil (the probe decision; write the field-injection snippet first)
```
control  = probe(fresh install of commit 1)          # must pass the probe's own asserts: Codex 25, Claude 18, roles 5, no errors
metadata = probe(same install + "metadata:\n  kind: <k>" as the last frontmatter key of every .agents/skills/*/SKILL.md)
if control fails:                                     stop: environment problem, B2 not judged
elif metadata.names == control.names and no errors:  keep metadata.kind (D6)
else:
    toplevel = probe(same install + top-level "kind: <k>")
    if toplevel.names == control.names and no errors: use top-level kind (D6's fallback); record the deviation
    else:                                             stop: evidence against spike findings.md:28
```

### Steps

**Pre-flight**

- [x] **1.1** Confirm the worktree. `git status --porcelain` is empty. `git branch --show-current` prints `nsd-integration`. `git log -1 --format=%h -- .project/active/native-skill-distribution/plan.md` prints a commit. `git rev-parse --short main native-claude-codex-skills` prints `8f43a09` and `86921f9`. If `main` moved, use the new SHA wherever this plan says `8f43a09`, and refresh SC1's inventory in 6.4 (design R2).
- [x] **1.2** [SC12] Capture `main`'s lint baseline in a scratch export. This needs no worktree bookkeeping and touches nothing in the live checkout:
  ```bash
  mkdir -p .orchestrate-logs/lint-baseline/main && git archive main | tar -x -C .orchestrate-logs/lint-baseline/main
  cd .orchestrate-logs/lint-baseline/main && uv sync --frozen -q
  uv run --frozen ruff check src/ tests/ --output-format concise > ../ruff-check-main.txt
  uv run --frozen ruff format --check src/ tests/ > ../ruff-format-main.txt
  uv run --frozen mypy src/ > ../mypy-main.txt
  ```
  Expected: 118 ruff findings, 78 files to reformat, 91 mypy errors (`spec.md:64`). If the numbers differ, record the measured ones under "Phase 1 Completion" and use them; SC12 needs same-tool parity. If `uv sync` cannot run there, run the worktree's `.venv/bin/ruff` and `.venv/bin/mypy` with that folder as the working directory, and note it.

**Merge**

- [x] **1.3** `git merge --no-ff --no-commit native-claude-codex-skills`. Resolve each path with the side in this table, and nothing else by hand:

  | Path | Side | Command |
  |---|---|---|
  | `claude/**` (git's rename detection moves it away) | `main`'s, through `HEAD` | `git checkout HEAD -- claude` |
  | `skills/`, `agents/` | branch | `git checkout native-claude-codex-skills -- skills agents` |
  | `project_templates/MODELING_GUIDE.md.template`, `MODELING_PROCESS.md.template` (changed on both) | branch; commit 2 regenerates them | `git checkout native-claude-codex-skills -- <the two>` |
  | `tests/test_modeling_command_contracts.py` (changed on both) | `main`'s; re-pointed in commit 3 | `git checkout HEAD -- <it>` |
  | `.project/CURRENT_WORK.md` | `wrap-split`'s | `git checkout HEAD -- <it>` |
  | `.project/active/spike-native-skill-install/*`, `.project/research/20260907-162310_native-claude-codex-skills.md` (added on both) | `main`'s where they differ | `git checkout HEAD -- <path>`; note each differing path for 6.4 |
  | Any other conflict | not predicted | `.project/` prose: take `HEAD` and note it. Code or shipped text: stop and return it |

  Do not check out whole folders from the branch beyond `skills` and `agents`. `main` changed other files in `project_templates/`, `src/` and `tests/` after the fork, and git's clean merge already carries them.
- [x] **1.4** [SC1] Verify the resolution, then commit.
  - `git diff --cached HEAD -- claude` is empty: `main`'s `claude/` is intact.
  - `git diff --cached native-claude-codex-skills -- skills agents adapters src/agentic_mbse/cli/__init__.py src/agentic_mbse/cli/installation.py pyproject.toml scripts README.md CLAUDE.md tests/test_cli.py tests/test_installation.py tests/test_packaged_guidance_contract.py` is empty: the branch side, which `main` did not touch since the fork.
  - `git diff --cached main -- src tests docs .gitignore project_templates/EPIC_GUIDE.md.template ':!src/agentic_mbse/cli/__init__.py' ':!src/agentic_mbse/cli/installation.py' ':!tests/test_cli.py' ':!tests/test_installation.py' ':!tests/test_packaged_guidance_contract.py'` is empty: `main`'s other changes are intact.
  - `uv run pytest tests/` passes. The branch installer still finds `claude/hooks/` and its `claude/` marker, and `main`'s contract test reads `main`'s `claude/`.
  - Record the resolution table, with any extra notes, under "Phase 1 Completion". Step 6.4 copies it into `dispositions.md`.
  - Commit: `Merge native-claude-codex-skills: native installer and skills/ tree, main's claude/ kept for regeneration`.

**B2 probe**

- [x] **1.5** Build two scratch targets. Make each its own git repo, so neither client walks up into the worktree's `.claude/` or root:
  ```bash
  for t in control metadata; do mkdir -p .orchestrate-logs/probe/b2-$t && git -C .orchestrate-logs/probe/b2-$t init -q && uv run agentic-mbse init .orchestrate-logs/probe/b2-$t --assistant both < /dev/null > .orchestrate-logs/probe/b2-$t.init.log 2>&1; done
  ```
  In `b2-metadata`, append `metadata:` and `  kind: workflow` or `  kind: supporting` as the last frontmatter key of every `.agents/skills/*/SKILL.md`. Use a throwaway snippet kept in `.orchestrate-logs/probe/`. Take the kind from `main`'s location (`git ls-tree main claude/commands claude/skills`). The Claude alias points into `.agents/skills/`, so one edit covers both clients.
- [x] **1.6** Run the probe on each target and keep the JSON as evidence:
  ```bash
  uv run python .project/active/native-skills/discovery_probe.py .orchestrate-logs/probe/b2-control --output .project/active/native-skill-distribution/evidence/probe-b2-control.json > .orchestrate-logs/probe/b2-control.log 2>&1; echo "exit $?"
  ```
  Do the same for `b2-metadata`. Apply the decision rule in the stencil.
  - A control run that fails is an environment problem: a client missing, a sandbox denial, or a client upgrade. Stop and return the log. The orchestrator can run the probe itself; it needs no model turns.
  - If the control run shows extra names (a client picked up the worktree's own `.claude/`), retry with targets under `/tmp` if the sandbox allows, and note it.
  - If the top-level fallback is needed, build `b2-toplevel` the same way and keep its JSON. Then `write` and `check` (Phase 2), `bundle_kind` (4.1), the I7 test (4.5) and CLAUDE.md (8.1) all use a top-level `kind:` key.
- [x] **1.7** Commit the probe JSON: `B2 holds: both clients list every bundle carrying metadata.kind` (or the fallback's outcome).

### Validation
- **Automated:** `uv run pytest tests/` passes at the merge commit.
- **Manual:** the three `git diff --cached` checks in 1.4 are empty. `probe-b2-metadata.json` lists the same names as `probe-b2-control.json` (Codex 25, Claude 18, roles 5).

### What We Know Works After This Phase
The branch's installer runs on `main`'s history with `main`'s `claude/` still present. `main`'s unrelated changes are intact. The kind field's form is decided on evidence.

---

## Phase 2: Regenerate the shipped text from `main` (commit 2)

### Goal
Write the adaptation list and `reconcile.py`. Prove `check` can fail. Then let `write` regenerate `skills/**`, `agents/*.md` and the tool-owned templates from `main`'s files in one commit.

### Assumption Under Test
- B1: `main`'s text needs only the Appendix A adaptations, at exactly the listed body counts.
- The envelope is mechanical (design § Research Findings, first bullet).

### Test Stencil (`check` is the test; write it before `write`)
```
assert check(main=8f43a09, fresh_install(commit 1)) != 0     # the branch's text is old; check must see it
write(main=8f43a09)
assert check(main=8f43a09, fresh_install(commit 2)) == 0
# Phase 6 records the negative self-check: one flipped byte, one count + 1, one extra file → each != 0
```

### Changes Required

**See `design.md` for:** the path rule and `check`'s comparison rules (§ One-time integration flow); the envelope (D3); the list's scope and fields (D4); the 17 starting entries (Appendix A).

#### `evidence/adaptations.yaml` (NEW)
- [x] **2.1** Seed the 17 entries from Appendix A with fields `id`, `file`, `old`, `new`, `count`, `why` and `origin`. Copy every `old` and `new` verbatim from the branch. Expand A4, A7 and A9 to verbatim strings using the word diffs (`.orchestrate-logs/nsd-design-scratch/wdiff.py`, and `.orchestrate-logs/nsd-inputs/fork-to-branch.diff`). Mark A1 `review: true` (design § Implementation Notes). A header comment states the semantics both commands implement:
  - The body is the text below the frontmatter when a file starts with `---\n`, otherwise the whole file. Frontmatter is never adapted (C1).
  - Entries apply in list order. `count` is the exact number of occurrences of `old` in the body at the moment the entry applies.

#### `evidence/reconcile.py` (NEW; one-time; retires with the item)
- [x] **2.2** Shared helpers only: read a file and its mode at a revision (`git show <rev>:<path>`, `git ls-tree -r <rev>`); load the YAML; split frontmatter by lines (the opening `---\n` and the next line equal to `---`; never `split("---", 2)`, which breaks on a `---` inside a value). Reading `main` through git, never through the working tree's `claude/`, lets both commands run after commit 3 and after `main` moves (R2).
- [x] **2.3** `check --main <rev> [--preface-from 86921f9] [--adaptations PATH] [--rows PATH] <installed-target>`. It shares no envelope code with `write`.
  - **Frontmatter, as data:** `yaml.safe_load` the installed frontmatter. It must equal `main`'s parsed frontmatter with `skills` removed, `Task` replaced by `Agent` in `allowed-tools` (string or list form), and the kind field added. The kind comes from `main`'s location: `claude/commands/` is `workflow`, `claude/skills/` is `supporting`.
  - **Preface:** taken from `--preface-from`, as the paragraph after the frontmatter in `86921f9:skills/<n>/SKILL.md`. Assert it is one string across all 25 bundles.
  - **Body, as bytes:** the installed text after the frontmatter equals `"\n" + preface + "\n\n" + adapt(main_body)`, with every entry hitting its exact `count`.
  - **Other bundle files and the four tool-owned templates:** installed bytes equal `main`'s bytes plus their adaptations.
  - **Agents:** source `agents/<n>.md` equals `main`'s `claude/agents/<n>.md` plus adaptations. Installed agents are rendered, so they are not compared.
  - **Hook:** the installed `.claude/hooks/<h>` equals `main`'s `claude/hooks/<h>` bytes.
  - **Pattern docs:** source `docs/patterns/*` equals `main`'s.
  - **Modes:** every compared file's executable bit equals `main`'s git mode.
  - **Sets:** the bundle set, each bundle's file set and the agent set match exactly.
  - **Output:** print every mismatch and exit 1 if there is any. With `--rows`, write one markdown row per compared file: path, `main` source, envelope applied (yes/no), and disposition in SC1's words (`take main`, or `merge: main + A6, A7`).
- [x] **2.4** [SC2] Run `check` on a fresh install of commit 1. It must exit non-zero, because the branch's text is older than `main`'s. Keep the output in `.orchestrate-logs/check/commit1.txt`. If it exits 0, `check` is broken: fix it before writing `write`.
- [x] **2.5** `write --main <rev>`:
  - Applies the path rule.
  - For each `SKILL.md`, applies the D3 text transform: delete the `skills:` line, failing if indented continuation lines follow it; replace `Task` with `Agent` on the `allowed-tools` line only; append the kind field as the last key; then write `---\n\n<preface>\n\n` followed by the adapted body.
  - Applies adaptations to bodies and asserts every count.
  - Sets each written file's mode from `main`'s git mode.
  - Skips `claude/hooks/*`, which commit 3 moves with `git mv`. Fails on any other unexpected `claude/` path.
  - Lists, and does not delete, any file under `skills/` or `agents/` with no `main` counterpart. `check` will fail on it, and it needs a disposition in 6.4.
  - Commit the two evidence files alone (`git add` them by path): `Add one-time reconcile tooling and the reviewed adaptation list`. Fix commits to the tooling are fine later; commit 2 stays `write`'s output alone.
- [x] **2.6** [SC2, SC4] Regenerate, install and check:
  ```bash
  uv run python .project/active/native-skill-distribution/evidence/reconcile.py write --main 8f43a09
  mkdir -p .orchestrate-logs/check/commit2 && uv run agentic-mbse init .orchestrate-logs/check/commit2 --assistant both < /dev/null > /dev/null
  uv run python .project/active/native-skill-distribution/evidence/reconcile.py check --main 8f43a09 .orchestrate-logs/check/commit2 > .project/active/native-skill-distribution/evidence/check-commit2.txt 2>&1; echo "exit $?"
  ```
  Expected: `git status` shows changes only under `skills/`, `agents/` and `project_templates/` (the tool-owned templates), and `check` exits 0. A count mismatch means B1 is false for that file. Inspect it. If `main` holds another runtime-specific instance, add a reviewed entry with `origin: item1` and a `why`, then re-run. Never hand-edit `write`'s output.
- [x] **2.7** `uv run pytest tests/` passes. A failure here is a branch test pinning the branch's old text. Point it at `main`'s text, as the design does for the contract test.
- [x] **2.8** Commit `write`'s output alone: `Regenerate shipped skills, agents and tool-owned templates from main 8f43a09`.

### Validation
- **Automated:** `check` exits non-zero on commit 1's fresh install and 0 on commit 2's. pytest passes.
- **Manual:** `git show --stat HEAD` lists only regenerated files. Read `skills/onboard/SKILL.md` once: frontmatter, then the preface, then `main`'s body with A1–A4 applied.

### What We Know Works After This Phase
The shipped text is `main`'s, wrapped in the envelope, with exactly the reviewed adaptations. A script that has been shown to fail says so.

---

## Phase 3: Remove `claude/` and this repo's tracked install (commit 3)

### Goal
Delete the old source and this repo's stale `.claude/` copies in one commit, so the PR diff shows each `claude/…` file renamed into the tree.

### Assumption Under Test
After this commit, the only things that break are the code paths keyed on `claude/`, which Phase 4 replaces.

### Test Stencil (the expected-red check)
```
failures = pytest(tests/)
assert failures ⊆ {hook-install tests, every test that runs init --dev, test_bundle_retirement_prunes_only_unchanged_resources, the wheel-build test}
# anything else failing means commit 3 broke something it should not have
```

### Changes Required
**See `design.md` for:** D7 (the hook), D13 (this repo's install), and Appendix B's rows for `claude/**`, `.claude/…` and `.gitignore`.

- [x] **3.1** [SC6] `git mv claude/hooks/ruff-format.sh hooks/ruff-format.sh`, then `git rm -r -q claude`. `git ls-files -s hooks/ruff-format.sh` shows mode `100755`, and `test ! -e claude` succeeds.
- [x] **3.2** `git rm` every tracked `.claude/` entry except `.claude/settings.json` (D13): `git ls-files .claude | grep -vx '.claude/settings.json' | xargs git rm -q`. First check the list against Appendix B: 9 commands; `.claude/skills/pdf-analysis` (the absolute link), `python-debugger`, `record-learning` and `toolkit-awareness`; 5 agents; the hook. `settings.local.json` is untracked: leave it.
- [x] **3.3** [SC12, I9] Add the D13 block to `.gitignore`, with a one-line comment saying it covers `install-commands --assistant claude` in this checkout: `.agents/skills/`, `.agentic-mbse/`, `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`. Then `git ls-files .claude` prints only `.claude/settings.json`.
- [x] **3.4** Re-point `tests/test_modeling_command_contracts.py` (`main`'s version): `claude/commands/<n>.md` becomes `skills/<n>/SKILL.md`, and `"Task"` becomes `"Agent"` at `:72`. Take nothing else from the branch's version of this test.
- [x] **3.5** Run `uv run pytest tests/`. Compare the failures with the stencil's set and record their IDs under "Phase 3 Completion". Investigate anything outside the set before committing.
- [x] **3.6** Stage everything and check the rename view: `git diff --cached -M --name-status main -- claude skills agents hooks` shows an `R` line for every `SKILL.md`, every agent and the hook. An `A`/`D` pair instead of an `R` means a file lost similarity, most likely through reflow: investigate.
- [x] **3.7** Commit. It is intentionally red; Phase 4 restores green. `Remove claude/: hook moves to hooks/, this repo stops tracking its own install`.

### Validation
- **Automated:** pytest fails only in the expected set.
- **Manual:** `git ls-files .claude` prints `.claude/settings.json`; `test ! -e claude`; the rename view from 3.6.

### What We Know Works After This Phase
The source tree has no `claude/`. This repo tracks no copy of its own install. The only breakage is the set of `claude/` keys that Phase 4 removes.

---

## Phase 4: The tree is the inventory (SC5, SC6, SC7)

### Goal
Remove every hand-kept list and every `claude/` key, add the one source-checkout predicate, and replace inventory tests with property tests. This phase is mostly deletion.

### Assumption Under Test
- Nothing in `src/` or `tests/` needs a list of skills, agents or hooks (I4).
- `src/agentic_mbse` is a sound source-checkout marker for data-root detection and for `--dev` (D8).

### Test Stencil (write these first; they fail until the code lands)
```python
def test_added_skill_and_role_need_no_other_edit(tmp_path, monkeypatch, capsys):          # SC5
    data = fake_data_root(tmp_path)   # copies skills/ and agents/; links adapters, hooks, docs, project_templates; makes src/agentic_mbse/
    write_bundle(data / "skills/new-skill", kind="workflow")
    (data / "agents/new-role.md").write_text(role("new-role"))
    monkeypatch.setattr("agentic_mbse.cli._get_data_root", lambda: data)
    assert init(tmp_path / "t", assistant="both") == 0
    assert (tmp_path / "t/.claude/skills/new-skill/SKILL.md").is_file()
    assert "new-role" in tomllib.loads((tmp_path / "t/.codex/config.toml").read_text())["agents"]
    cmd_install_commands(Namespace(list=True, directory=str(tmp_path), force=False))
    assert "new-skill" in section(capsys.readouterr().out, "Workflows")
```

### Changes Required
**See `design.md` for:** D6 and D8; Architecture § End state; Component Overview, "Removed" and "Changed"; I4–I7; Implementation Notes on the retirement-test fixture and the exec bit.

**Helper signatures (open for the plan; chosen here):**

- `is_source_checkout(root: Path) -> bool` in `installation.py`: true when `(root / "src" / "agentic_mbse").is_dir()`.
- `bundle_kind(bundle: Path) -> str` in `installation.py`: reads the kind field from `bundle / "SKILL.md"`'s frontmatter, and raises `ValueError` if it is missing or not `workflow` or `supporting`.

**`--list` layout (open for the plan; chosen here).** Every count is computed:
```
Available MBSE skills:

Workflows (15):
  - analyze-models
  ...

Supporting skills (10):
  - epic-decomposition
  ...

Total: 25 skills
```

#### Code
- [x] **4.1** `src/agentic_mbse/cli/installation.py`: add `is_source_checkout` and `bundle_kind`. Hooks come from `data / "hooks"` (native `:339`).
- [x] **4.2** `src/agentic_mbse/cli/__init__.py`:
  - Delete `MBSE_COMMANDS` and `MBSE_SKILLS` (native `:17-48`).
  - `_get_data_root` (`:97-117`) and `_check_dev_mode_prerequisites` (`:274-280`) use `is_source_checkout`. Their docstrings and comments stop mentioning `claude/`.
  - `get_hooks_dir` (`:135-137`) returns `hooks`.
  - `--list` (`:677-684`) groups by `bundle_kind`.
  - Leave `get_docs_dir` as is (I6). Leave `DEV_MODE_GITIGNORE_PATHS` as is (design Non-Goals; follow-up in 8.6).
  - `grep -rn "MBSE_COMMANDS\|MBSE_SKILLS" src tests scripts` prints nothing.
- [x] **4.3** `pyproject.toml`: `"claude"` becomes `"hooks"` in the wheel force-include (`:54`), and `"claude/"` becomes `"hooks/"` in the sdist include (`:62`). Fix the comment at `:52`.

#### Tests (inventories become properties)
Derive every expected set with the test's own glob over `REPO_ROOT / "skills"`, `"agents"` and `"hooks"`, not with the installer's `skill_bundles()`. A test must be able to disagree with the installer.

- [x] **4.4** [SC5] Remove the `MBSE_*` imports (`test_cli.py:8`, `test_installation.py:12`) and the assertions built on them (`test_cli.py:283-289`, `test_installation.py:35`). Replace the literal skill lists (`test_cli.py:150-160`, `:454-464`) and the counts (`test_cli.py:257-258`, `:268`; `test_installation.py:53`) with derived values. In `test_bundle_retirement_prunes_only_unchanged_resources` (`test_installation.py:285`), create `src/agentic_mbse/` in the fake root and link `hooks` instead of `claude`.
- [x] **4.5** [SC5] Add the stencil's fake-root test. Add the I7 test: every `skills/*/SKILL.md` has `name` equal to its folder, a `description`, a kind of `workflow` or `supporting`, no `skills:` key, and the shared preface as its first paragraph.
- [x] **4.6** [SC5, SC7] Add a `--list` test: every installed bundle is listed exactly once, under the section that matches its kind, and the total equals the number of `skills/*/SKILL.md`. Extend `test_native_install_catalog_and_roles` (`test_installation.py:31-59`): every file under every source bundle is present and byte-equal at `.agents/skills/<n>/…` and, for `claude` and `both`, at `.claude/skills/<n>/…`. The role count is the number of `agents/*.md`.
- [x] **4.7** [SC4, SC7] Text property tests over a fresh `--assistant both` install:
  - **Reference integrity (the deletion guard, D6 and S4):** every backticked reference whose whole content matches `^/[a-z0-9-]+$` names an installed bundle. Every `.agents/skills/<n>/…` path, with `<n>` matching `[a-z0-9-]+`, names an installed bundle, and its sub-path exists when it names a file.
  - **No `.claude/` paths:** no installed `SKILL.md`, bundle file, tool-owned template or Codex role TOML contains `.claude/`. Claude agents carry the Claude adapter, which may name `.claude/settings.json`; they are excluded by design.
  - **The guide (SC4):** the installed `modeling_project/MODELING_GUIDE.md` does not contain `.claude/settings.json`.
  - If a hit appears that is explicitly conditional on the runtime, do not add an exemption list. Return it as a B1 finding, and add a reviewed adaptation instead.
- [x] **4.8** [SC6] In `tests/test_cli.py`:
  - `init` installs `.claude/hooks/ruff-format.sh` with the exec bit.
  - `init --dev` links it to a path ending in `hooks/ruff-format.sh` under the repo root.
  - `--dev` is refused, with the "requires a source checkout" message, when `_get_data_root` is monkeypatched to a folder without `src/agentic_mbse`.
  - Add `test_source_tree_has_no_claude_folder` (I5): `REPO_ROOT / "claude"` does not exist, and neither include list in `pyproject.toml` names `claude`.
- [x] **4.9** [SC6] In `tests/test_packaged_guidance_contract.py`, with one wheel build:
  - Read the force-included folder set from `pyproject.toml` with `tomllib`. Every file under each folder is byte-equal to its wheel member. No member starts with `agentic_mbse_data/claude/`.
  - Extract the wheel with `zipfile` into `tmp_path`. In a subprocess (`sys.executable`, `PYTHONPATH=<extracted>`), run a short script that asserts `agentic_mbse.__file__` is under the extracted folder, calls `cmd_init` on a fresh target, and prints `get_docs_dir()`. Assert every bundle, every agent and the hook are installed, and that the docs dir is under `agentic_mbse_data/docs` (I6).
  - Do not assert the exec bit here: `extractall` drops modes. Optionally, in the same build, assert that `init --dev` from the wheel is refused.

### Validation
- **Automated:** `uv run pytest tests/` passes, including the Phase 3 red set. The existing ownership tests stay green (`test_forced_command_install_never_writes_through_symlink`, `test_parent_symlink_is_preserved_even_under_force`, `test_native_owner_configuration_preserved_with_force`), which covers SC7's "re-init preserves protected files and does not write through symlinks".
- **Inventory check (I4):** `grep -rnE "MBSE_COMMANDS|MBSE_SKILLS" src tests scripts` and `grep -nE "== 25|\(25\)|Total: 25|== 18|== 5\b" tests/test_cli.py tests/test_installation.py` print nothing.
- **Manual:** `uv run agentic-mbse install-commands --list` shows Workflows (15) and Supporting skills (10), total 25.

- [ ] **4.10** (Saved as commit step `1-phase4`; commit pending, see Phase 4 Completion.) Commit: `Make the source tree the only inventory: MBSE lists and claude/ keys removed, hooks/ packaged`.

### What We Know Works After This Phase
Adding a skill is adding a folder. `init`, `init --dev` and the wheel all install the hook from `hooks/`. No list or count of skills remains in `src/` or `tests/`.

---

## Phase 5: Adopt the old installer's links; fix the adapters' agent rule (SC8, SC3)

### Goal
Add the one legacy predicate inside `permit`, report what it adopts, and correct the adapters' delegation sentence.

### Assumption Under Test
- B3: every link the old installer made has the exact shape the predicate accepts, and nothing else passes it.
- I1 and I2 still hold: adoption only unlinks the link, and only for entries derived from the source tree.

### Test Stencil
```python
@pytest.mark.parametrize("text, adopted", [
    ("{old}/claude/commands/{cmd}.md", True),
    ("{old}/claude/skills/{cmd}.md", False),           # tail does not mirror the entry
    ("{plain}/claude/commands/{cmd}.md", False),       # root lacks src/agentic_mbse
    ("../../old/claude/commands/{cmd}.md", False),     # relative text
    ("{old}/x/../claude/commands/{cmd}.md", False),    # '..' segment
    ("{old}/./claude/commands/{cmd}.md", False),       # '.' segment, which pathlib would hide
    ("{old}/claude/commands/{cmd}.md/", False),        # empty segment
])
def test_legacy_link_target_accepts_exactly_what_the_old_installer_wrote(tmp_path, text, adopted): ...
```

### Changes Required
**See `design.md` for:** D5 and D9; Architecture § Legacy adoption (the predicate, why each part of SC8's boundary holds, where adoption happens for each kind, the report); I1–I3; Implementation Notes (the predicate gotcha, `permit` ordering, fixtures).

**Signatures and wording (open for the plan; chosen here):**

- `legacy_link_target(target: Path, relative: str) -> str | None`, module-level in `installation.py`, so it is unit-testable without an `Installer`.
- `expose_to_claude(installer: Installer, source: Path, *, link_mode: str, dev: bool) -> None`. It calls `retire_command(source.name)`. If that returns true, it makes the alias: `alias`, or `copy_tree` in copy mode, keeping the existing fallback to `copy_tree` when a real directory is in the way.
- `init` prints, after the "Symlinked" block, `Adopted (N) - links from the pre-native installer replaced:` and then one `  A <entry> (was -> <old target>)` line per entry. The hyphen matches the existing headers. `install-commands` adds `Adopted: N` to its summary line and prints the same entry lines.

- [x] **5.1** [SC8] Write the stencil's unit test. Use a fake checkout root `<tmp>/old/src/agentic_mbse/` and a plain folder `<tmp>/plain/`. Take `{cmd}` from the source tree (the first bundle whose kind is `workflow`).
- [x] **5.2** [SC8] Write the end-to-end test, parametrized over the four kinds × target existing or dangling. Take the names from the source tree: a workflow, a supporting skill, an agent stem and the hook. For each case:
  - Create the absolute link `.claude/<kind>/<name>` into `<tmp>/old/claude/<kind>/<name>`, and run a non-interactive `init`.
  - The entry is now the installed thing. Commands: the link is gone and `.claude/skills/<n>` is the relative alias. Skills: the relative alias. Agents: a real rendered file. Hook: a real executable file.
  - The output lists `(was -> <link text>)`.
  - When the target exists, its bytes are unchanged.
- [x] **5.3** [SC8] Negative end-to-end cases keep today's prompt-or-preserve: an unshipped name (never visited), a non-checkout root, a non-mirrored tail, a relative link, a `..` link, a real file and a real directory. Each is left exactly as it was, and no alias shadows a preserved command.
- [x] **5.4** [SC8] A mixed legacy tree built from the source inventory: a dangling link for every shipped command, supporting skill, agent and hook name, plus owner entries (an unshipped command link, a real owner skill directory, a relative `.agents/skills/` owner link). Assert that the adopted count equals the number of shipped-name links created, every bundle resolves at `.claude/skills/<n>/SKILL.md`, and the owner entries are byte- and link-identical. Repeat once through `cmd_install_commands` to cover its report.
- [x] **5.5** [SC8] Implement.
  - `legacy_link_target` follows the design's pseudo-code exactly. Split the raw `os.readlink` text on `/`. Never use `Path(text).parts`, never normalize, and never stat the referent.
  - `permit` checks it after the manifest/desired match and before `force`/`decide`. On a match it appends to a new `actions["adopted"]` bucket and returns true.
  - The loop in `install_assistants` calls `expose_to_claude` in place of the side effect inside the boolean condition at native `:311`. `retire_command` is unchanged.
  - Add the report lines, and include `adopted` in `cmd_init`'s "Everything up to date" and "Next steps" conditions (native `:659-661`).
  - Size check: `permit` grows by a few lines. `grep -n "def " src/agentic_mbse/cli/installation.py` shows only `legacy_link_target` and `expose_to_claude` as new in this phase, and no new removal API.
  - Commit: `Adopt the old installer's links inside permit, and report them`. (Saved as commit step `2-adoption`; commit pending.)
- [x] **5.6** [SC3] Edit `adapters/claude.md:7` and `adapters/codex.md:7`. Replace the sentence that requires a new agent for every fresh stage with the continuity rule from fusion-tea's `.agentic-mbse/codex.md:7`. Read it in the pristine rehearsal copy, `.orchestrate-logs/rehearsal/fusion-tea/.agentic-mbse/codex.md`. The rule: keep a continuing author while its context is useful; independent review uses a fresh non-author agent. Word it for each runtime's delegation tool. Keep the surrounding sentences, including "do not resume an author for its audit".
- [x] **5.7** [SC3] Add a property test over both installed adapters. Neither says that every stage, or each fresh stage, needs a new agent (check the old phrasings, and `fresh stage` near `new agent`). Both say an author may continue while its context is useful. Both require a fresh non-author agent for independent review. Commit: `Adapters keep a continuing author and require a fresh agent only for independent review`. (Saved as commit step `3-adapters`; commit pending.)

### Validation
- **Automated:** `uv run pytest tests/` passes. As a one-off local check, apply `os.path.normpath` to the link text, watch the `.` and `..` cases fail, then revert.
- **Manual:** build a three-link legacy tree under `.orchestrate-logs/adopt-demo/`, run `uv run agentic-mbse install-commands .orchestrate-logs/adopt-demo --assistant claude`, and read the Adopted lines.

### What We Know Works After This Phase
A re-init over an old `--dev` install replaces its shipped-name links with the native install and reports each old target. Everything else is left to the existing ownership rule.

---

## Phase 6: Content and catalog evidence (SC1, SC2, SC4, SC7)

### Goal
Record the final `check` run and its negative self-check, the discovery probes on fresh installs, and the disposition table.

### Assumption Under Test
The final installer writes exactly `main`'s text in the native shape, and both clients discover everything under each runtime choice.

### Check Stencil
```
check(main, fresh both-install of HEAD) == 0
check(main, copy with one flipped body byte) != 0
check(main, copy, adaptations with one count + 1) != 0
check(main, copy with one extra bundle file) != 0
probe(fresh claude): Claude lists every bundle not marked user-invocable: false (18) and 5 roles
probe(fresh codex):  Codex lists 25
probe(fresh both):   the probe's own asserts pass
```

### Steps
- [x] **6.1** [SC2] Fresh `init --assistant both` of HEAD into `.orchestrate-logs/check/final`. Run `check --main 8f43a09 --rows .project/active/native-skill-distribution/evidence/check-rows.md` with output to `evidence/check.txt`. It exits 0.
- [x] **6.2** [SC2] Negative self-check (M4). For each case, `cp -a` the final install to its own folder, apply one mutation and run `check`. Keep the command, the exit code and the first mismatch line in `evidence/check-negative.txt`.
  1. Flip one byte in the body of one installed `SKILL.md`.
  2. Run with `--adaptations` pointing at a temp copy of the list with one `count` raised by 1.
  3. Add one extra file inside one installed bundle.

  All three must exit non-zero. One that exits 0 is a bug in `check`: fix it, then re-run 6.1 and 6.2.
- [ ] **6.3** (Waiting: `probes.sh` in `.orchestrate-logs/orchestrator-run.md`; needs `git init`.) [SC7] Probe three fresh installs. Each is a `git init`ed target under `.orchestrate-logs/probe/fresh-<a>/` for `a` in `claude`, `codex` and `both`, with JSON to `evidence/probe-fresh-<a>.json`.
  - **`claude`:** Claude lists every bundle not marked `user-invocable: false` (derive the number; 18 today) and the 5 roles. Codex also lists all 25, because `.agents/skills/` is always written; record it.
  - **`codex`:** Codex lists all 25, and Claude lists none (there is no `.claude/`). The probe's own asserts fail by design here; read the JSON.
  - **`both`:** the probe's own asserts pass.
  - **On disk, for `claude` and `both`:** each `user-invocable: false` bundle (7 today) has `.claude/skills/<n>/SKILL.md`; the hook is present and executable.
  - **Codex roles:** covered structurally by 4.6 (the TOML parses and is registered in `.codex/config.toml`). Client-side role discovery needs model turns (spike `findings.md:29`).
- [x] **6.4** [SC1] Write `evidence/dispositions.md`.
  - **Inventory against `main` at `8f43a09`,** reproduced by command (`git diff --name-only 88e2489 8f43a09 -- claude project_templates docs/patterns`, and the fork-to-branch equivalent): 16 bundles changed on `main` (11 workflows, 5 supporting), 3 tool-owned templates, 2 pattern docs. Branch-only: 2 user-owned templates, 2 agents (`python-debugger`, `sysml-expert`), the adapters. Refresh if `main` moved.
  - **Generated rows:** `check-rows.md` (bundles, templates, agents), included or linked.
  - **Hand rows:**
    - Adapters: keep the branch, plus the SC3 edit.
    - `README.md.template`, `OVERVIEW.md.template`: keep the branch.
    - Installer code, `pyproject.toml`, `scripts/replicate_setup.sh`: keep the branch, plus this item's changes.
    - `CLAUDE.md`, `README.md`: keep the branch, plus the Phase 8 edits.
    - `test_cli.py`, `test_installation.py`, `test_packaged_guidance_contract.py`: keep the branch, with inventories derived.
    - `test_modeling_command_contracts.py`: take `main`, re-pointed. Its `:72` is the `main` test whose contract the envelope changes (`Task` → `Agent`).
    - The hook: moved, with `main`'s bytes. Pattern docs: take `main`.
    - The `.project/` conflicts from 1.3.
    - The three target-owned passages: `codex.md:11` and `MODELING_GUIDE.md:276` go to fusion-tea's `AGENTS.md`, with ledger rows. The MR-7 paragraphs at `MODELING_PROCESS.md:17` and `:34` are kept at runbook step 4 until Item 2.
    - This repo's `.claude/` copies: removed (D13). This repo's tracked tool-owned template copies: kept, known stale (R7).
    - The branch's reflow-only changes, and the branch adaptations `main` made unnecessary: dropped (design Appendix A, last paragraph).
- [ ] **6.5** (Saved as commit step `6-content-evidence`; the probe JSONs follow after 6.3 runs.) Commit: `Evidence: shipped text equals main except the reviewed list; both clients discover every bundle`.

### Validation
`check.txt` shows exit 0. `check-negative.txt` shows three non-zero exits. The three probe JSONs meet the expectations. Every row category in 6.4 is present.

### What We Know Works After This Phase
SC2 is shown by a check that is itself shown to fail. SC7's discovery holds under each runtime choice.

---

## Phase 7: fusion-tea switch-over evidence (SC8, SC9, SC10; D13)

### Goal
Produce the fusion-tea patch and ledger rows. Rehearse both install modes on copies of fusion-tea's tree. Rehearse this repo's own reinstall on a scratch clone. Write the owner's runbook from what was observed.

### Assumption Under Test
- B3: all 31 legacy links are adopted.
- B4: the two SC9 passages are the only target-owned text a re-init replaces without a prompt.
- R5: `--dev` leaves fusion-tea's `.gitignore` unchanged.

### Check Stencil (per mode, on its own pristine copy)
```
apply the patch, commit it in the copy
out = init(copy[, --dev]) < /dev/null
assert out.adopted == 31
assert no no-prompt replacement loses target-owned text (B4 provenance check)
assert MODELING_PROCESS.md byte-identical to the reference copy (both MR-7 paragraphs kept)
assert both SC9 passages present in AGENTS.md
assert fusion-tea's own entries byte- and link-identical
assert pyproject.toml and uv.lock untouched
probe(copy): Claude ⊇ 18 shipped + 5 roles; Codex ⊇ 25; 7 reference skills on disk; hook present
second init: nothing adopted, created or updated
```

### Copies
- **The pristine reference** is `.orchestrate-logs/rehearsal/fusion-tea/`, built by the orchestrator. Never install into it.
- **One copy per run:** `.orchestrate-logs/rehearsal/make-copy.sh .orchestrate-logs/rehearsal/ft-<run>`. Its last line should report 165 tracked baseline files and 31 re-pointed links. Do not edit the script.
- **Fallback** if the script cannot read `/home/reid/1cfe/fusion-tea` (sandbox): `cp -a .orchestrate-logs/rehearsal/fusion-tea .orchestrate-logs/rehearsal/ft-<run>`. Record which method you used.
- **Safety check before any install into a copy:** `find .orchestrate-logs/rehearsal/ft-<run> -type l -lname '/home/reid/1cfe/agentic-mbse/*'` prints nothing; `git -C .orchestrate-logs/rehearsal/ft-<run> status --porcelain` is empty; the 31 links point into `/home/reid/1cfe/agentic-mbse-nsd/claude/`, which no longer exists.

### Steps
- [x] **7.1** Write two throwaway scripts in `.orchestrate-logs/rehearsal/` (not evidence):
  - `owner-entries.py <copy>`: for every entry under `.claude/{commands,skills,agents,hooks}` and `.agents/skills` whose name the installer does not ship, print the link text, or the sha256 of every file beneath it. Derive the shipped names from `skills/`, `agents/` and `hooks/`.
  - `provenance.py <reference-file> <new-file> <tool-path>`: list each line removed from the reference that appears in none of the tool's versions of that file (`main` at `c37ff53` and `8f43a09`, fork `88e2489`, branch `86921f9`, read with `git show`). For `.codex/agents/*.toml`, compare the decoded `developer_instructions` text, not raw lines. Skip `.agentic-mbse/install.json` (machine state).
- [x] **7.2** [SC9] Build the patch on a copy `ft-patch`. Append to `AGENTS.md` a one-line heading naming where the text came from, then the `.codex-test` worktree paragraph (`.agentic-mbse/codex.md:11`) and the pattern-location note (`modeling_project/MODELING_GUIDE.md:276`), each verbatim. Then `git -C .orchestrate-logs/rehearsal/ft-patch diff > .project/active/native-skill-distribution/evidence/fusion-tea-target-owned.patch`. For I8, `grep '^+++ ' <patch>` shows only `b/AGENTS.md`. Do not touch `codex.md` or `MODELING_GUIDE.md` (D10).
- [x] **7.3** [SC9] Create `.project/active/wrap-split-migration-ledger.md` if it is absent, with a one-line header (Item 2 owns this file; Item 1 created it) and a section `## Item 1 — native-skill-distribution`. Add one row per passage: what moved, where it was, its new fusion-tea home, and the evidence (patch, rehearsal).
  - **The `.codex-test` paragraph** → `AGENTS.md`.
  - **The pattern-location note** → `AGENTS.md`. Per D10 and S2, the row also records: after re-init, Codex reads two conflicting instructions (the guide's `get_docs_dir()` resolver, and `AGENTS.md`'s `.agentic-mbse/patterns/`); that worktree copy equals `main`'s docs today, but no installer refreshes it; the note's stated reason, separation from the pinned runtime, ends at runbook step 1; whether to keep it, drop it or copy it into `CLAUDE.md` after step 1 is the owner's choice.
  - **The MR-7 paragraphs** (`MODELING_PROCESS.md:17`, `:34`) → stay in place, kept at runbook step 4; Item 2 lands the general section.
- [ ] **7.4** (Waiting: `rehearse.sh` in `.orchestrate-logs/orchestrator-run.md`.) [SC8, SC9, SC10] Rehearse plain `init` on `ft-plain`. Raw outputs go to `evidence/rehearsal/`.
  1. Record the pre-state: the `owner-entries.py` output, and `find .claude -maxdepth 2 -type l -printf '%p -> %l\n'` run in the copy.
  2. `git -C <copy> apply --check <patch>` (SC9's apply check). Then apply it and commit it in the copy.
  3. From the worktree root: `uv run agentic-mbse init .orchestrate-logs/rehearsal/ft-plain < /dev/null > .project/active/native-skill-distribution/evidence/rehearsal/plain-init1.txt 2>&1`.
  4. Record: `git status --porcelain` and `git diff --summary` (tracked files changed, and any `mode change … => 120000`); the `.gitignore` diff; the Adopted list (expect 31; B3); the Updated list, which is the set replaced with no prompt; and the `Preserving` lines, each one a prompt in a real run.
  5. **B4:** run `provenance.py` on every file in the Updated list against the reference copy. Review each flagged line by hand. The two SC9 passages, now in `AGENTS.md`, are expected. Tool text from an earlier native build is not target-owned; say so per line. Any other flagged line is possible loss: stop and return it.
  6. Confirm:
     - `modeling_project/MODELING_PROCESS.md` appears in a `Preserving` line and is byte-identical to the reference, so both MR-7 paragraphs are present.
     - `.agentic-mbse/codex.md` and `modeling_project/MODELING_GUIDE.md` were replaced with no prompt.
     - `AGENTS.md` contains both passages (`grep -F`).
     - The `owner-entries.py` output is unchanged.
     - `pyproject.toml`, `uv.lock` and every user-owned file are unchanged.
     - Which of the 13 hand-updated payloads (`.orchestrate-logs/nsd-inputs/fusion-tea/harness-right-size/installed.json`) were replaced with no prompt.
  7. Probe: `uv run python .project/active/native-skills/discovery_probe.py .orchestrate-logs/rehearsal/ft-plain --output .project/active/native-skill-distribution/evidence/rehearsal/plain-probe.json`. Its exact-count asserts fail, because fusion-tea's own skills and commands also appear; read the JSON. Claude's names include every shipped bundle not marked `user-invocable: false` (18), there are 5 roles, Codex's names include all 25, and there are no errors. On disk: the 7 reference skills at `.claude/skills/<n>/SKILL.md`, and `.claude/hooks/ruff-format.sh` as a real executable file.
  8. Run the same `init` a second time, with output to `plain-init2.txt`: nothing adopted, created or updated, and the same `Preserving` lines.
- [ ] **7.5** (Waiting: `rehearse.sh`.) [SC8, SC10] Rehearse `init --dev` on `ft-dev`: the same steps with `--dev`, outputs named `dev-*`. Also record:
  - The tracked Codex files that became absolute links into the worktree's `skills/`. In the real run they would point into `/home/reid/1cfe/agentic-mbse/skills/`.
  - The `.gitignore` diff. R5 predicts none, because the old dev block's marker line is already present.
  - The hook is a link to `hooks/ruff-format.sh`.
  - `git -C /home/reid/1cfe/agentic-mbse-nsd status --porcelain` is unchanged by the run, so nothing was written through a `--dev` link into the source.
- [ ] **7.6** (Waiting: `rehearse.sh`.) [SC10, D13] Rehearse this repo's own reinstall on a scratch clone (design § Implementation Notes, "The scratch-clone check"):
  ```bash
  git clone -q --branch nsd-integration /home/reid/1cfe/agentic-mbse-nsd .orchestrate-logs/rehearsal/repo-clone && cp .env .orchestrate-logs/rehearsal/repo-clone/
  cd .orchestrate-logs/rehearsal/repo-clone && uv sync --frozen -q && uv run pytest tests/ -q | tail -1     # baseline
  uv run agentic-mbse install-commands --assistant claude --link-mode symlink
  git status --porcelain                  # must be empty; any ?? line means an ignore line is missing
  uv run pytest tests/ -q | tail -1       # must equal the baseline
  ```
  Also confirm that every bundle resolves at `.claude/skills/<n>/SKILL.md`, that the agents and the hook are present, and that `CLAUDE.md` was preserved. If `uv sync` cannot run in the clone, run both pytest passes as `uv run --project /home/reid/1cfe/agentic-mbse-nsd --directory .orchestrate-logs/rehearsal/repo-clone pytest tests/ -q` and note it.
- [ ] **7.7** (Waiting on 7.4-7.6 results.) [SC8, SC10] Write `evidence/rehearsal.md`:
  - Setup: the copy method and the safety check.
  - The patch's apply check.
  - One section per mode with the results of steps 4–8.
  - A side-by-side table of the two modes' observed effects. Runbook step 3 uses it.
  - The scratch-clone results.
  - Known differences from the real run. The rehearsal used the worktree's CLI, so rendered agents and `.claude/settings.json` record the worktree's docs path; fusion-tea's own CLI would record its `.venv` (R3). The copy's links dangle; plain `init` run before the checkout moves sees live links, which 5.2's existing-target cases cover.
- [ ] **7.8** (Waiting on 7.4-7.6 results.) [SC10] Write `evidence/fusion-tea-runbook.md` for the owner. Every step in it is the owner's.
  - **Before:** the owner merges `nsd-integration` to `main` and pushes. The PR description says the branch also carries `wrap-split`'s planning commits for other items (`research-seam-port`, the epic). Do not delete or move any agentic-mbse checkout before step 3 (R4).
  - **Warning:** fusion-tea's Claude side is broken from the moment `/home/reid/1cfe/agentic-mbse` moves to the merged `main` until step 3 finishes. Plain `init` from fusion-tea's own environment can run before that move, which removes the window (R6). `--dev` must run after it.
  - **Step 1, move the pin.** [INHERITED: the 2026-10-04 pin move to `c37ff53`, fusion-tea commit `a2abea8df`] First confirm agentic-mbse's dependencies are unchanged between `c37ff53` and the merged SHA. Edit the `rev` in fusion-tea's `pyproject.toml` (`[tool.uv.sources]`). Replace the old SHA with the new one in `uv.lock` by hand (two occurrences on the agentic-mbse `source =` line). Do not run `uv lock`: under uv 0.10 it fails because of sysml-codegen's path source. Run `uv sync --frozen`. That sync is exact; last time it removed `playwright`, `pyee` and `syside-license`, restored with `uv pip install --no-deps playwright==1.58.0 pyee==13.0.1 syside-license==0.3.6`. `uv lock --check` then reports the lock fresh. PR #16's `/research` step needs this move (`--insights '[]'`).
  - **Step 2:** `git apply --check`, then apply `fusion-tea-target-owned.patch` (built against `403716ee3`), and commit it with a reference to the ledger rows.
  - **Step 3, choose the install mode (owner decision).** Show both modes with the rehearsal's observed effects (the table from 7.7), and the recommendation: plain `init` (agent-grade, `spec.md:99`, with its reason). Give the exact commands:
    - Plain: `cd /home/reid/1cfe/fusion-tea && uv run --no-sync agentic-mbse init .`, using fusion-tea's own CLI at the merged SHA.
    - `--dev`: after moving the checkout, `uv run --project /home/reid/1cfe/agentic-mbse agentic-mbse init --dev /home/reid/1cfe/fusion-tea`. It needs the source checkout (native `cli/__init__.py:275-279`), so fusion-tea's own CLI cannot run it.
  - **Step 4, answer each prompt:** keep `modeling_project/MODELING_PROCESS.md` (`s`, not `b`), which keeps both MR-7 paragraphs in force until Item 2. List the other prompts the rehearsal saw.
  - **Step 5, verify:** the Adopted count is 31; `git status` matches the rehearsal's; Claude Code lists the workflows.
  - **This repo:** after moving `/home/reid/1cfe/agentic-mbse` to the merged `main`, run `uv run agentic-mbse install-commands --assistant claude --link-mode symlink` from its root. Re-run it after editing `skills/` (D13).
  - **Owner choice, does not block:** keep, drop, or copy into `CLAUDE.md` fusion-tea's pattern note after step 1, with the ledger row's facts.
- [ ] **7.9** (Patch and ledger saved as commit step `7-fusion-tea-prep`; rehearsal evidence follows.) Commit: `Evidence: fusion-tea rehearsal adopts 31 links with no loss; runbook and patch for the owner`.

### Validation
`rehearsal.md` shows, for both modes: Adopted (31); no unexplained B4 flags; `MODELING_PROCESS.md` kept; owner entries unchanged; catalogs as expected; an idempotent second run. The scratch clone stays clean with an unchanged pytest result. The patch passes `git apply --check`. The runbook covers steps 1–5, the warning, this repo's step and both parked owner choices.

### What We Know Works After This Phase
The owner can switch fusion-tea and this repo over in a known order, with each mode's effects observed rather than predicted, and with nothing target-owned lost.

---

## Phase 8: Docs, the full gate and the audit hand-off (SC12, SC11)

### Goal
Describe the one remaining installer, prove the branch meets SC12, and bound the independent audit.

### Assumption Under Test
The parity rule holds: no findings beyond `main`'s baseline, and every file this item adds or edits is clean.

### Gate Stencil
```
pytest(tests/) passes
ruff check, ruff format and mypy on changed files: clean
findings in unchanged files == main's findings in those files
git merge-base --is-ancestor main HEAD
git ls-files .claude == [.claude/settings.json]; claude/ absent
```

### Steps
- [x] **8.1** [SC12] Edit `CLAUDE.md` (the branch's version):
  - **Architecture § Assistant Integration:** name `skills/` (each bundle declares its kind), `agents/`, `adapters/`, `hooks/` and `cli/installation.py`, with legacy adoption in one sentence.
  - **Change Coordination:** there is one installer. Adding a skill is adding its folder with the kind field, and nothing else. Delete the "keep `MBSE_COMMANDS` and `MBSE_SKILLS` aligned" sentence. `scripts/replicate_setup.sh` is the six-line `init` wrapper that installs the product into a checkout under the target-repo policy, and it also writes project scaffold. `uv run agentic-mbse install-commands --assistant claude` is what a developer runs to get the workflows in this repo, re-run after editing `skills/`.
  - **Init File Ownership and the Directory Clarification table:** use `hooks/` and `skills/`; no row names `claude/`.
  - `README.md`'s installer paragraph matches. `scripts/README.md:125` describes `replicate_setup.sh`; make that line match too.
- [ ] **8.2** (Saved as commit step `8a-docs`.) Commit: `Docs describe the one installer and how a developer installs the workflows here`.
- [x] **8.3** [SC12] `uv run pytest tests/` passes. Record the summary line.
- [x] **8.4** [SC12] Lint parity against the baseline from 1.2:
  ```bash
  git diff --name-only --diff-filter=AMR main -- 'src/*.py' 'tests/*.py' > .orchestrate-logs/lint-baseline/changed.txt
  echo .project/active/native-skill-distribution/evidence/reconcile.py >> .orchestrate-logs/lint-baseline/changed.txt
  uv run ruff check $(cat .orchestrate-logs/lint-baseline/changed.txt); uv run ruff format --check $(cat .orchestrate-logs/lint-baseline/changed.txt)
  uv run mypy src/ > .orchestrate-logs/lint-baseline/mypy-branch.txt; uv run mypy .project/active/native-skill-distribution/evidence/reconcile.py
  uv run ruff check src/ tests/ --output-format concise > .orchestrate-logs/lint-baseline/ruff-check-branch.txt
  uv run ruff format --check src/ tests/ > .orchestrate-logs/lint-baseline/ruff-format-branch.txt
  ```
  Passing looks like this:
  - The changed files are clean for `ruff check` and `ruff format --check`, and no mypy line names a changed `src/` file. mypy is scoped to `src/`, as in CLAUDE.md, plus `reconcile.py`.
  - For files not in `changed.txt`, the branch's findings equal `main`'s line for line; the files are byte-identical, so compare the filtered, sorted lists. Totals are at most `main`'s.
  - Fixing a pre-existing finding in a file this item edits (for example `cli/__init__.py`) is in scope. Fixing other files is not.

  Write `evidence/lint-parity.md`: the commands, `main`'s and the branch's totals, the changed-file list and the comparison result.
- [ ] **8.5** (Checks done; saved as commit step `8b-gate-evidence`. `git fetch` waits in `orchestrator-run.md`.) [SC12] `git merge-base --is-ancestor main HEAD && echo ok`; `git ls-files .claude` prints only `.claude/settings.json`; `test ! -e claude`. If anything after Phase 6 touched `skills/`, `agents/` or the templates, re-run 6.1. Commit: `Gate: pytest passes and lint holds main's parity`.
- [x] **8.6** [SC11] Write `evidence/audit-scope.md` for the orchestrator's audit stage (D11).
  - **In scope:** the installer diff, `git diff 88e2489 HEAD -- src/agentic_mbse/cli pyproject.toml tests/test_installation.py tests/test_cli.py tests/test_packaged_guidance_contract.py`, which covers A–K and this item together; the A–K checklist (`.project/active/native-skills/remediation.md`); `adaptations.yaml` (A1 flagged); `reconcile.py`'s transform and check code; `check.txt` and `check-negative.txt`; `rehearsal.md`, the runbook and the patch.
  - **Out of scope:** body text beyond the list, which SC2 makes mechanical.
  - **Who:** a fresh non-author agent.
  - **Follow-ups for close:** tidy `--dev`'s `.gitignore` list (`.claude/commands/`, `.claude/.tool-hashes.json`); this repo's tracked init scaffold and its stale template copies (R7).
- [ ] **8.7** [SC11] After the audit stage returns, not during implement: append a dated verdict update to `.project/active/native-skills/audit.md` (its `:3` reads "Needs Work"), citing this item's audit.

### Validation
Steps 8.3–8.5 pass. `lint-parity.md` and `audit-scope.md` exist.

### What We Know Works After This Phase
The branch is ready for the owner's merge decision, pending the independent audit.

---

## Environment Setup

See CLAUDE.md for the development commands. The orchestrator creates the worktree, copies `.env`, runs `uv sync` and builds the pristine fusion-tea copy before implement. Nothing in this plan creates them.

## Risk Management

See `design.md#potential-risks` (R1–R7) for the full analysis. Phase-specific mitigations:

- **Phase 1:** B2 is decided by comparing a treatment run with a control run. A sandbox or client failure stops the phase instead of producing a false result.
- **Phase 2:** `check` must fail on commit 1 before it is trusted on commit 2. Count mismatches grow the list by reviewed entries only.
- **Phase 3:** the red set is named in advance. Anything else blocks the commit.
- **Phase 4:** tests derive expectations with their own globs, so they can disagree with the installer.
- **Phase 5:** the predicate's unit table includes the `.`, `..` and relative cases a normalizing implementation would wrongly accept.
- **Phase 7:** the safety check runs before every install into a copy. B4's provenance check stops the phase on any unexplained removed line.
- **Phase 8:** pre-existing findings in edited files are fixed, not baselined.
- **R2 (`main` moves before the owner merges):** merge `main` again, re-run `write` and `check` with the new SHA, and refresh SC1's inventory.

## Implementation Notes

**`main` moved before integration (1.1, design R2).** `main` is `06ac41d`, one commit past `8f43a09`: PR #17 drops a `;` inside backticks on one line of `project_templates/MODELING_PROCESS.md.template` (`:71`). Every later step uses `06ac41d` where this plan says `8f43a09`. SC1's inventory in 6.4 is measured against `06ac41d`; the only difference is that one template line. `wrap-split` already carries `06ac41d` (`40bfca6`), so the merge base with `main` is `main` itself.

**Environment: 18 tests fail for missing optional modules.** The worktree's venv was synced without extras. 17 tests in `tests/test_web_backend.py` need `trafilatura` (extra `web`) and `tests/test_equations.py::TestDetectEquations::test_returns_detected_equations` needs `PIL` (only through the heavy `extract-full`/`extract-tables` extras). The same 18 fail on `main`'s export with the same no-extras sync (`.orchestrate-logs/lint-baseline/main`, `uv run --frozen pytest tests/test_web_backend.py tests/test_equations.py`: 18 failed, 14 passed). Below, "pytest passes" means nothing fails outside this environmental set. The final gate (8.3) should run with the `web` extra, or record this set the same way.

### Phase 1 Completion
**Completed:** 2026-10-09. Merge `df75d26`; B2 evidence in the Phase 1 evidence commit.

**Actual Changes:**
- 1.2 lint baseline of `main` (`06ac41d`) in `.orchestrate-logs/lint-baseline/` via `git archive` + `uv sync --frozen`: ruff check 118 findings (matches), ruff format 78 files to reformat (matches), **mypy 101 errors in 21 files, not 91**. SC12's parity uses the measured 101.
- 1.3 merge: 14 conflicted paths, each resolved by the plan's table and nothing else by hand.

  | Class | Paths | Resolution |
  |---|---|---|
  | `claude/**` | `claude/commands/orchestrate-modeling.md` (modify/delete). Rename detection had also moved `main`'s edits of the other renamed commands onto `skills/` | `git checkout HEAD -- claude`; `git ls-files claude` is 37 files, equal to `HEAD` |
  | `skills/` content conflicts | `skills/{audit-models,design-model,implement-model,plan-model,quick-model,review-model,spec-model}/SKILL.md` (7) | `git checkout native-claude-codex-skills -- skills agents`. No index path under `skills/` or `agents/` was missing from the branch tree, so no `main`-only file was carried in by directory-rename detection |
  | Templates changed on both | `project_templates/MODELING_GUIDE.md.template`, `MODELING_PROCESS.md.template` | branch side; commit 2 regenerates them |
  | `main` test changed on both | `tests/test_modeling_command_contracts.py` | `main`'s side; re-pointed in commit 3 |
  | Planning state | `.project/CURRENT_WORK.md` | `wrap-split`'s side |
  | Added on both, differ | `.project/active/spike-native-skill-install/findings.md`, `installer-findings.md` | `main`'s side. They differ only by `main`'s added 2026-10-04 status line (2 lines each). For 6.4 |
  | Added on both, identical | `.project/research/20260907-162310_native-claude-codex-skills.md` | no conflict; same bytes on both sides |

- 1.4 the three `git diff --cached` checks printed nothing (`claude` vs `HEAD`; branch-side paths vs the branch; `main`'s other changes vs `main`).
- 1.5–1.6 B2 probe. Two `git init`ed targets under `.orchestrate-logs/probe/`, each a fresh `init --assistant both` of the merge. `b2-metadata` got `metadata:` / `  kind: <k>` as the last frontmatter key of all 25 `.agents/skills/*/SKILL.md` (throwaway `.orchestrate-logs/probe/inject_kind.py`; kind from `main`'s `claude/commands/` vs `claude/skills/`: 15 workflow, 10 supporting; all 25 still parse as YAML). Probe on each, Claude Code 2.1.295 and codex-cli 0.160.0: both exit 0 with the probe's own asserts passing. Claude 18 names, Codex 25, roles 5, no errors, and **the name lists are identical between control and treatment**. Evidence: `evidence/probe-b2-control.json`, `evidence/probe-b2-metadata.json`.

**B2 decision:** keep `metadata.kind` (D6). No top-level fallback needed.

**Issues:**
- pytest at the merge: 20 failed, 2081 passed. 18 are the environmental set above. The other two are direct consequences of the plan's own resolution, not merge defects:
  - `tests/test_modeling_command_contracts.py::test_canonical_flow_marks_optional_and_completion_stages`: `main`'s test reads `project_templates/MODELING_PROCESS.md.template`, which 1.3 deliberately takes from the branch side (old text). Commit 2 regenerates it from `main`.
  - `tests/test_packaged_guidance_contract.py::test_built_wheel_carries_the_authoritative_guidance_bytes`: the branch's test asserts no `agentic_mbse_data/claude/commands/` member, and the merge keeps `main`'s `claude/` for regeneration, which the wheel force-includes. Commit 3 removes `claude/`; Phase 4 fixes the force-include.

**Deviations:**
- 1.4 expected `uv run pytest tests/` to pass at the merge. It cannot, for the two reasons above; the plan's own resolution table predicts both. No resolution was changed.
- `main` SHA `06ac41d` replaces `8f43a09` throughout (plan step 1.1 rule).
- 1.2's mypy count is 101, not 91. Recorded and used.

### Phase 2 Completion
**Completed:** 2026-10-09. Tooling `e3eb308`; commit 2 (`write`'s output alone) `f68ae0a`; `check` evidence and these notes in the following `.project/`-only commit.

**Actual Changes:**
- 2.1 `evidence/adaptations.yaml`: the 17 Appendix A entries with `id`, `file`, `old`, `new`, `count`, `why`, `origin` (A1 also `review: true`); a header comment states the body-only, in-order, exact-count semantics. A4 and A7 are whole-sentence/whole-paragraph replacements (one line each in `main`); A9 is A8's strings. Before writing any code, a throwaway pass confirmed every `old` occurs exactly `count` times in `main`'s body and every `new` occurs the same number of times in the branch's body (A17's `new` is absent there by design, `origin: item1`). No `.orchestrate-logs/nsd-design-scratch/` exists in this worktree, so the word diffs were re-run with `git diff --no-index --word-diff=plain --word-diff-regex='[^[:space:]]+'` between `88e2489` and `86921f9`.
- 2.2–2.3 and 2.5 `evidence/reconcile.py` (392 lines after `ruff format`; ruff check/format and mypy clean). Shared code is only `show`, `tree`, `load_adaptations` and `split_frontmatter`. `check` is a `Checker` class that collects mismatches; it has its own adaptation pass (reports) and its own frontmatter expectation (parsed YAML). `write` has `destination` (the path rule), `envelope` (D3 text transform), `adapt` (raises on a count mismatch) and computes every output before writing any file. `check` takes the preface from `86921f9` and asserts it is one string across the 25 bundles; `write` uses its own constant, so a typo in either fails `check`. Beyond the plan's comparisons, `check` also compares the hook set and the pattern-doc set, and reports a list entry whose file is never compared.
- 2.4 `check --main 06ac41d` on a fresh install of commit 1 (`.orchestrate-logs/check/commit1`): **exit 1**, 55 files compared, 52 mismatches (`.orchestrate-logs/check/commit1.txt`): all 25 `SKILL.md` frontmatters (no kind yet), 23 bodies (old text or reflow), `debugging_internals.md`, `sysml-expert.md` (reflow), and the guide and process templates. `python-debugger/SKILL.md` and `source-traceability/SKILL.md` failed on frontmatter only, which shows the body comparison passes text that already equals `main` plus the list.
- 2.6 `write --main 06ac41d`: 40 files regenerated, no file under `skills/` or `agents/` without a `main` counterpart (the mapped inventories were confirmed identical before writing). Git shows 29 changed (26 under `skills/`, `agents/sysml-expert.md`, the guide and process templates); the other 11 were already byte-equal. No mode changes. `check --main 06ac41d` on a fresh install of commit 2: **exit 0**, 55 files compared, 0 mismatches (`evidence/check-commit2.txt`). Read `skills/onboard/SKILL.md`: frontmatter with `kind: workflow` last, the preface, then `main`'s body with A1–A4.
- The large deletion count in commit 2 (396+/1831−) is `main`'s September rewrite condensing the text, not truncation: e.g. the process template is 104 lines on `main` and after `write`, 843 on the branch; `design-model` is 39 on `main`, 43 after `write` (the envelope adds 4 lines).
- 2.7 pytest: 19 failed, 2082 passed. 18 are the environmental set. The 19th is the wheel test seeing `main`'s `claude/` (Phase 1 note); commit 3 removes it. The contract test now passes on the regenerated template. No branch test pinned the branch's old text, so nothing was re-pointed.

**B1:** holds for the 17 listed entries: every count matched on the first run, and no new entry was needed. (Unlisted runtime-specific text is not something `check` can see; Phase 4's text property tests are the guard.)

**Deviations:**
- `main` is `06ac41d` (Phase 1 note), so every command used `--main 06ac41d`.
- `check-commit2.txt` and these notes go in a `.project/`-only commit after commit 2, so commit 2 stays `write`'s output alone.

### Phase 3 Completion
**Completed:** 2026-10-09. Commit 3 `ea64232` (intentionally red); these notes in the following `.project/`-only commit.

**Actual Changes:**
- 3.1 `git mv claude/hooks/ruff-format.sh hooks/ruff-format.sh` (`git ls-files -s`: `100755`), then `git rm -r -q claude`. `test ! -e claude` holds.
- 3.2 `git rm` of the 22 tracked shipped-name `.claude/` entries, matching Appendix B exactly: 9 commands; the absolute link `.claude/skills/pdf-analysis` (only the link was removed; its referent in the live checkout was not touched) and the `python-debugger`, `record-learning` and `toolkit-awareness` skill files; 5 agents; the hook. No `settings.local.json` exists in this worktree.
- 3.3 `.gitignore` gains the D13 block with a one-line comment: `.agents/skills/`, `.agentic-mbse/`, `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`. `git ls-files .claude` prints only `.claude/settings.json`.
- 3.4 `tests/test_modeling_command_contracts.py`: 7 `claude/commands/<n>.md` paths become `skills/<n>/SKILL.md`; `:72` expects `Agent`. Nothing else changed.
- 3.6 Rename view against `main`: all 37 `claude/` files show as `R` (25 `SKILL.md`, 5 agents, the hook, 6 other bundle files), no `A`/`D` pairs. Lowest similarity `R065` (`manage-sources`, which carries A5–A7), then `R075` (`python-debugger/SKILL.md`, A10); 9 are `R100`.

**3.5 Expected-red check:** pytest 35 failed, 2066 passed. 18 are the environmental set. The other 17 all fall in the stencil's set:
- Hook install: `test_cli.py::TestCmdInit::test_creates_hooks_directory`.
- `init --dev`: the 10 `test_cli.py::TestCmdInitDevMode::*` tests that fail (`test_dev_creates_symlinks_for_{commands,skills,hooks,tool_templates}`, `test_dev_symlinks_orchestrator_command`, `test_dev_idempotent`, `test_dev_replaces_regular_file_with_symlink`, `test_dev_agents_resolve_placeholders`, `test_dev_updates_gitignore`, `test_dev_gitignore_idempotent`); `TestModificationDetectionIntegration::test_dev_mode_tracks_hashes`; `TestCmdInstallCommands::test_symlink_summary_describes_both_install_modes[True]` (the `dev=True` case); `test_installation.py::test_copy_link_dev_transitions_preserve_owner_additions` (calls `cmd_init(..., dev=True)`).
- `test_installation.py::test_bundle_retirement_prunes_only_unchanged_resources[True-symlink]` and `[True-copy]` (the `[False-*]` cases pass).
- The wheel test: `uv build` exits 2 because `pyproject.toml` force-includes the missing `claude`.

Mechanism, read in the code: `--dev` is refused by `_check_dev_mode_prerequisites`' `claude/` check (`cli/__init__.py:274`), and hooks are read from `data / "claude/hooks"` (`installation.py:339`). Non-dev installs still work only because `_get_data_root` falls through to its "last resort" source root (`cli/__init__.py:116`) once its `claude/` marker is gone. Phase 4 replaces all three keys.

**Deviations:**
- `git mv` needs the destination folder: `mkdir hooks` first. It left an empty `claude/hooks/` behind, removed with `rmdir` (git tracked nothing there).

**Commits for Phases 4–5 were made from saved steps, not by the implementer.** In the session that implemented Phases 4 and 5, `git add` required interactive approval, which a non-interactive stage cannot give. Each planned commit was saved instead as an exact copy of its files under `.orchestrate-logs/commit-steps/<step>/`, with a `<step>.paths` list and a `<step>.msg` message: `1-phase4` (4.10), `2-adoption` (5.5), `3-adapters` (5.7), then this notes step. `verify.py` there extracted `HEAD` into a scratch folder, overlaid the steps in order and ran the whole suite at each boundary: after `1-phase4` 2140 passed; after `2-adoption` 2164 passed; after `3-adapters` 2166 passed; each with 1 skipped (already skipped before this item) and 1 strict xfail (the docs packaging gap, Phase 4 notes). The three steps together equal the worktree's 10 changed files byte for byte.

### Phase 4 Completion
**Completed:** 2026-10-09. Commit step `1-phase4`.

**Environment re-check before starting:** after the orchestrator's `uv sync --all-extras`, pytest on commit 3 was 17 failed, 2085 passed: exactly Phase 3's expected red set, and the 18 environmental failures are gone.

**Actual Changes:**
- 4.1 `installation.py`: `is_source_checkout(root)` (`root/src/agentic_mbse` is a directory) and `bundle_kind(bundle)` (parses the `SKILL.md` frontmatter by lines, raises `ValueError` on missing frontmatter or a kind outside `BUNDLE_KINDS`). Hooks install from `data / "hooks"`.
- 4.2 `cli/__init__.py`: `MBSE_COMMANDS` and `MBSE_SKILLS` deleted. `_get_data_root` and `_check_dev_mode_prerequisites` use `is_source_checkout`; their `claude/` comments are gone. `get_hooks_dir` returns `hooks`. `--list` prints Workflows (15), Supporting skills (10), Total: 25, all computed. `get_docs_dir` and `DEV_MODE_GITIGNORE_PATHS` untouched.
- 4.3 `pyproject.toml`: `hooks` replaces `claude` in the wheel force-include and the sdist include; the comment names the purpose instead of listing folders.
- 4.4–4.6 Tests derive the inventory from `tests/helpers/shipped.py` (new): `SKILLS`, `AGENTS`, `HOOKS` by the tests' own globs, plus `frontmatter`, `kind` and `bundle_files`. In `test_cli.py`: the two literal skill lists, the counts 25, and the `MBSE_*` manifest test are gone (its `replicate_setup.sh` assertion stays as `test_replicate_setup_wraps_init`); the `--list` test checks every installed bundle appears once under the heading its own frontmatter declares. In `test_installation.py`: `fake_data_root` (skills and agents copied, the rest linked, `src/agentic_mbse/` made) serves both the retirement test and the new SC5 test (`test_added_skill_and_role_need_no_other_edit`: a new workflow bundle and a new role are installed for both runtimes, the role registered in `.codex/config.toml`, the bundle listed under Workflows). The catalog test checks every file of every bundle byte-equal at `.agents/skills/` and the Claude alias, roles by name for both runtimes, and read-only sandboxing as a property (roles without `Bash`) instead of three named roles. The retirement fixture's dead `pyproject.toml` and `.git` lines are gone.
- 4.5, 4.7 `tests/test_shipped_text.py` (new): I7 per bundle and one shared preface; over one fresh `both` install, every backticked `/name` and every `.agents/skills/<n>/…` path in installed text names an installed bundle and an existing file; no `.claude/` in bundles, tool-owned templates or decoded Codex role instructions; the guide carries `get_docs_dir()` and no `.claude/settings.json` (SC4). A pre-check scan of a fresh install found no unknown references and no `.claude/` outside the Claude adapter, so no B1 finding and no new adaptation.
- 4.8 `test_cli.py`: hooks installed executable (derived from `hooks/`); `--dev` links each hook to `REPO_ROOT/hooks/<h>`; `test_dev_refused_without_source_checkout` (a packaged-style data root with `skills/` but no `src/agentic_mbse` is refused, target untouched); `test_source_tree_has_no_claude_folder` (I5: no `claude/` folder, no include entry with a `claude` path segment).
- 4.9 `test_packaged_guidance_contract.py`: one module-scoped wheel build; byte equality parametrized per force-included entry read from `pyproject.toml`; the authoritative pattern doc and no `agentic_mbse_data/claude/` member; the extracted wheel run in a subprocess with `PYTHONPATH` asserts it imports from the extraction, refuses `--dev`, installs every bundle, role and hook, and resolves docs under `agentic_mbse_data/docs` (I6). No exec-bit assertion after `extractall`.

**Checks:** full pytest 2140 passed, 1 skipped, 1 xfailed. `grep -rnE "MBSE_COMMANDS|MBSE_SKILLS" src tests scripts` and the count grep print nothing. `install-commands --list` shows Workflows (15), Supporting skills (10), Total: 25. ruff check, ruff format and mypy are clean on every file Phase 4 touched (two import-order findings from `tomllib` under `target-version = py310` were fixed).

**Issues: a docs packaging gap that predates this item (needs an owner decision).** The plan's wheel test compares every file under every force-included folder. For `docs/` that fails: the wheel omits all of `docs/syside/python/v0.8.4/syside/` (340 tracked files; the other 789 docs files are present). The venv's `agentic_mbse_data` copy, built from the merge commit before any Phase 4 change, lacks the same folder, so this item did not cause it. No ignore rule matches and the folder is a plain directory; the root cause is inside hatchling, whose source this session could not read. It matters because the syside-expert role's `{SYSIDE_DOCS_PATH}` resolves into the packaged docs on wheel installs, fusion-tea's included. The `docs` case is marked `xfail(strict=True)` with that reason, so the suite stays green and the mark fails loudly once the folder is packaged. Fixing the packaging is outside SC6, which concerns the installed assets.

**Deviations:**
- `_get_data_root` now raises `FileNotFoundError` when neither a source checkout nor `agentic_mbse_data` exists, instead of returning the source root "and let caller handle missing files". Phase 3 showed that fallback hiding a missing marker; with `is_source_checkout` it only fires on a broken install, where installing nothing silently is worse than an error.
- The SC5 and I7 tests and the text properties live in a new `tests/test_shipped_text.py` and `tests/helpers/shipped.py` rather than spread over `test_cli.py` and `test_installation.py`.
- 4.9's per-folder comparison is parametrized so the docs gap can be marked on its own case (above).

### Phase 5 Completion
**Completed:** 2026-10-09. Commit steps `2-adoption` (5.1–5.5) and `3-adapters` (5.6–5.7).

**Actual Changes:**
- 5.5 `installation.py`: `legacy_link_target(target, relative)` exactly as designed. The entry must be `.claude/<location>/<name>` with `<location>` in `LEGACY_LOCATIONS` (commands, skills, agents, hooks), and a symlink (lstat only). The raw `os.readlink` text, split on `/`, must start empty (absolute) with no empty, `.` or `..` segment after it. Its last three segments must be `claude/<location>/<name>`, and the rest must be a source checkout. The text is never normalized and the referent is never read. `permit` gains four lines after the manifest/desired check and before `force`/`decide`: on a match it records `"<relative> (was -> <text>)"` in a new `adopted` action and returns true; the existing callers then unlink and install as for any permitted entry. `expose_to_claude` takes the alias step out of the loop's boolean condition; `retire_command` is unchanged. `grep -n "def "` shows only `legacy_link_target` and `expose_to_claude` as new in this phase, and no removal API.
- `cli/__init__.py`: `init` prints `Adopted (N) - links from the pre-native installer replaced:` after the Symlinked block, one `  A <entry> (was -> <old target>)` line each; `adopted` joins the "Everything up to date" / "Next steps" condition (the redundant `elif` became `else`). `install-commands` adds `Adopted: N` to its summary and prints the same lines.
- 5.1–5.4 tests in `test_installation.py`, all names from the tree (`WORKFLOW`, `SUPPORTING`, `AGENTS[0]`, `HOOKS[0]`): the 7-row predicate table; each of the four locations with a live or dangling referent (adopted, reported with the old target, replaced by the alias, rendered agent or executable hook, referent bytes unchanged); the seven never-adopted cases at the command location left exactly as they were (`entry_state` compares link text, bytes or child trees), with no alias shadowing a preserved command; and a mixed legacy tree with a link for every shipped workflow, supporting skill, agent and hook plus three owner entries, through `init` (`Adopted (31)`) and `install-commands` (`Adopted: 31`).
- 5.6 `adapters/codex.md:7` now carries fusion-tea's `.agentic-mbse/codex.md:7` sentences verbatim, so the file equals fusion-tea's copy up to fusion-tea's own target-owned paragraph. `adapters/claude.md:7` says the same for the Agent tool: "Keep a continuing author across stages and clarifications while its context remains useful. Independent criticism requires a fresh non-author agent with only its self-contained brief; never resume an author for its audit." "Independent criticism" matches `main`'s `MODELING_PROCESS.md.template:98`.
- 5.7 `test_adapter_keeps_a_continuing_author_and_a_fresh_independent_reviewer` over both installed adapters: no sentence pairs "stage" with "new agent" (both old sentences did), and both carry the continuity, fresh non-author and no-resume rules.

**Checks:** full pytest 2164 passed after adoption, 2166 after the adapters (1 skipped, 1 xfailed). Normalizing the link text with `os.path.normpath` made the `..`, `.` and trailing-slash rows fail; reverted. Manual demo (`.orchestrate-logs/adopt-demo/`, three dangling links into a fake old checkout): `install-commands --assistant claude` reported `Adopted: 3` with each old target; the command link was gone, both skills were relative aliases, and the hook was a real executable file. ruff check, ruff format and mypy clean on the touched files.

**Deviations:** none in behaviour. Adopted agents and hooks also appear in the Updated list, because `write` reports any replaced entry there; the Adopted list says which of them were legacy links.

**Report-once change (orchestrator call after Phase 5, commit step `5-report-once`).** Adopted agents, hooks and skill aliases were also listed under Updated or Symlinked, so a reader counting "replaced with no prompt" counted them twice. The installer now keeps adoptions as a map (entry → the link text it replaced) and routes `write`'s and `alias`'s reporting through `Installer.report`, which skips an entry already listed as adopted; the `actions` dict is back to its six buckets. The per-location adoption test asserts the entry appears under no other bucket; making `report` list everything fails it for skills, agents and hooks (commands were never double-listed). Suite 2166 passed.

**Commands this session could not run.** In this session `git add`/`commit`, `git init`, `git -C <other repo>`, `git clone`, `git fetch`, `cp -a`, `bash -n` and `uv sync --directory` all needed approval. Prepared commits are in `.orchestrate-logs/commit-steps/` as before; the rest is written, with exact commands and output locations, in `.orchestrate-logs/orchestrator-run.md` (probes for 6.3, `rehearse.sh` for 7.4-7.6, `git fetch` for 8.5).

### Phase 6 Completion
**Status:** 6.1, 6.2 and 6.4 done; 6.3 waits on the orchestrator's `probes.sh`. Commit step `6-content-evidence`.

- 6.1 `check --main 06ac41d --rows` on a fresh `both` install (`.orchestrate-logs/check/final`): 55 files compared, 0 mismatches (`evidence/check.txt`); 40 rows in `evidence/check-rows.md`, 10 of them "merge: main + A…".
- 6.2 `evidence/check-negative.txt` (`.orchestrate-logs/negative_check.py`, each case on its own copy): baseline exit 0; one body byte changed in `onboard/SKILL.md` exit 1 ("body is not the preface plus main's adapted body"); A6 count 4 → 5 exit 1 ("A6 … occurs 4x, list says 5"); an extra `onboard/extra.md` exit 1 ("bundle onboard: extra extra.md").
- 6.3 **Not done here; the first attempt is discarded.** `git init` is gated, so the probes ran on plain folders. The Codex-only target, which has no `.claude/`, showed Claude listing 12 skills and 5 roles: the old tracked `.claude/` set of this repo (9 commands, 3 supporting skills, 5 agents), found above the worktree (the sandbox does not let the stage look there). So plain-folder results cannot show isolated role discovery, and all three JSONs were moved to `.orchestrate-logs/probe/contaminated-nogit/`. `.orchestrate-logs/probe/probes.sh` repeats the step on `git init`ed targets, as the plan requires, and adds the on-disk checks.
- 6.4 `evidence/dispositions.md`: the inventory by command against `06ac41d` (16 bundles, 3 templates, 2 pattern docs changed on `main`; branch-only: 2 user-owned templates, 2 agents by reflow, the adapters), the generated rows, and the hand rows from the plan, including the `main` test whose contract the envelope changes (`test_modeling_command_contracts.py:72`).

### Phase 7 Completion
**Status:** 7.1-7.3 done; 7.4-7.9 wait on the orchestrator's `rehearse.sh`. Commit step `7-fusion-tea-prep` (patch and ledger).

- 7.1 `.orchestrate-logs/rehearsal/owner-entries.py` (unshipped entries as link text or file hashes; on the pristine copy: fusion-tea's 2 commands, 9 skill files across 6 skills, 1 agent, and the 5 relative `.agents/skills/` links) and `provenance.py`. `provenance.py` reads the init output's Updated, Symlinked and Removed lists. For each replaced file it lists removed lines that no agentic-mbse revision of the file's source carries (`git log --all`), compares Codex roles on decoded instructions with doc paths folded back to placeholders, and marks whether each flagged line now sits in `AGENTS.md`.
- 7.2 `evidence/fusion-tea-target-owned.patch`, generated by `.orchestrate-logs/rehearsal/make_patch.py` from the pristine copy (the plan's `git -C ft-patch diff` is gated). It appends a heading naming both sources, then `codex.md:11` and `MODELING_GUIDE.md:276` verbatim; `+++` names only `b/AGENTS.md` (I8). `git apply --check` runs in `rehearse.sh`.
- 7.3 `.project/active/wrap-split-migration-ledger.md` created with the Item 1 section: three rows, the pattern-note row carrying D10's conflict, refresh and stated-reason facts and the owner's keep/drop/copy choice.
- **Script dry run (not evidence).** To make the orchestrator's single run reliable, the stage made one Python copy of the pristine tree, ran a plain `init` into it and ran `provenance.py` on the output, then deleted the copy. Results to expect from the real run:
  - Adopted 31; Updated 39 with no adopted entry repeated; Symlinked 15 (the workflow aliases).
  - Two would-be prompts: `modeling_project/MODELING_PROCESS.md`, as planned, and `work/backlog/epic_template.md`, which the plan did not predict (next bullet).
  - `provenance.py` flagged both SC9 passages, as "NOT KEPT" only because the dry copy had no patch, and the same `codex.md:11` paragraph inside each Codex role's instructions.
  - The other flagged lines are envelope text from an earlier, uncommitted native build: YAML block-list `allowed-tools` lines, quoted descriptions, and a generated "Supporting skills: …" line, identical across the workflows. No other text was flagged.
- **Safety finding: the pristine copy links into the live checkout.** fusion-tea's `work/backlog/epic_template.md` is an absolute link to `/home/reid/1cfe/agentic-mbse/project_templates/epic_template.md.template`. `make-copy.sh` re-points only `.claude/` links, so the plan's safety check (`find … -lname '/home/reid/1cfe/agentic-mbse/*'` prints nothing) fails on every copy. The design's Non-Goals assumed fusion-tea's template copies are real files; this one is not. The stage found it after the dry-run install, because the sandbox blocks that `find` for the stage. The dry install did not write through it: the link is not managed, so `permit` preserved it non-interactively ("Preserving modified or untracked file: work/backlog/epic_template.md"), and the installer never writes through links (I1); the link was unchanged. `rehearse.sh` now re-points every live-checkout link into the worktree, where the same template exists, commits that as setup, and stops before installing if any remain. The runbook must cover this prompt.

### Phase 8 Completion
**Status:** 8.1, 8.3, 8.4 and 8.6 done; 8.5's checks done except `git fetch`; 8.7 follows the audit. Commit steps `8a-docs` and `8b-gate-evidence`.

- 8.1 `CLAUDE.md`:
  - `cli/` describes `init` and `install-commands`.
  - Assistant Integration names `skills/` with `metadata.kind`, `hooks/`, and `installation.py` as the one installer, with legacy adoption in one sentence. The skill counts are gone, since they would go stale when a skill is added.
  - The Directory table gains `agents/`, `adapters/`, `hooks/`.
  - Change Coordination states the one installer, that adding a skill, role or hook is adding its file and nothing else, what `replicate_setup.sh` is (the six-line `init` wrapper that also writes scaffold), and that a developer runs `install-commands --assistant claude` here and re-runs it after editing `skills/`. The `MBSE_*` sentence is gone.
  - `README.md` gains the hook bullet and one sentence on adoption; `scripts/README.md:125` now describes `replicate_setup.sh` truthfully.
- 8.3 `uv run pytest tests/`: 2166 passed, 1 skipped, 1 xfailed.
- 8.4 `evidence/lint-parity.md`: changed files clean; ruff check 118 = 118; ruff format 78 → 77 (`tests/test_cli.py` now formatted); mypy 101 → 98 with the other 98 equal to `main` line for line. mypy is compared in the baseline's own no-extras environment, because the worktree's all-extras venv changes mypy's findings in unchanged modules (14 import errors fewer, 4 attr errors more).
- 8.5 `git merge-base --is-ancestor main HEAD` exits 0; `git ls-files .claude claude` prints only `.claude/settings.json`; `claude/` is absent. Nothing after Phase 6 touched `skills/`, `agents/` or the templates, so 6.1 stands. `main` and `origin/main` are both `06ac41d` as of the last fetch; a fresh `git fetch` waits in `orchestrator-run.md`.
- 8.6 `evidence/audit-scope.md`: the scope, what to press on (I1-I3, `permit`'s order), out of scope, and follow-ups (the `--dev` gitignore list, R7, the docs packaging gap, `make-copy.sh`'s link gap).

### Phase 7 Completion

### Phase 8 Completion

---

**Status:** Draft → In Progress → Complete

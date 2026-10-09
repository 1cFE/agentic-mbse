# Design: Reconcile the native installer source with `main` (WRAP-SPLIT Item 1)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-09 10:00 PDT
**Planning branch:** `wrap-split` @ `b7aba20` (this file). Implementation: new branch `nsd-integration` in a fresh worktree (D1).
**Spec:** `spec.md` (revised after `spec-review.md`; Align decisions in `briefs/00-align.md`)

## Overview

Bring the native branch onto `main` so the tool-neutral source tree carries `main`'s current text and is the only thing the installer reads. Extend the installer's ownership rule so it takes over the links the old installer left in fusion-tea, and give the owner a rehearsed runbook for switching fusion-tea over.

## Related Artifacts

- Spec: `.project/active/native-skill-distribution/spec.md`; review: `spec-review.md`; Align: `briefs/00-align.md`; brief: `briefs/03-design.md`
- Epic: `.project/backlog/epic_wrap-split.md` § Item 1
- Required Reading: native `.project/active/native-skills/{plan,remediation,audit}.md`; fusion-tea `.project/active/harness-right-size/{report.md,installed.json}`; `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 4
- Read-only inputs: `.orchestrate-logs/nsd-inputs/` (native at `86921f9`, fusion-tea at `403716ee3`). Cited below as "native" and "fusion-tea".
- Product-lens: `product-lens.md` (CLEAR; falsifiers (a)–(c) at `:35` are checked in Validation)
- No `.project/adr/` exists, so no decision records apply.

## The Point

[NEED] (owner, verbatim, `briefs/00-align.md:19`) "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this".

[AGENT] (orchestrator's reading, confirmed with the owner at Align 2026-10-09) One place to register a skill. After this item:

- The tool-neutral source tree is the only installer source.
- It carries `main`'s current text.
- `agentic-mbse init` installs it the same way for Claude Code and Codex.

Why it matters now: Items 2 and 5 register new skills and Item 4 edits shipped text. Until the two installer sources become one, each of those edits must be made twice or stranded behind a 58-commit gap. The fusion-tea side carries two owner criteria (`[NEED]`, epic `:65-66`): no loss of information, and MR-7 enforcement intact after re-init.

## Research Findings

**Content (measured 2026-10-09 against fork `88e2489`, `main` `8f43a09`, native `86921f9`).** Evidence scripts are in `.orchestrate-logs/nsd-design-scratch/` (gitignored).

- **The branch's envelope is fully mechanical.** For workflows it drops the `skills:` line and changes `Task` to `Agent` in `allowed-tools`. Supporting-skill frontmatter is unchanged. Every bundle gets the same preface paragraph (native audit F-I confirmed all 25 byte-identical). Agents keep their frontmatter.
- **The branch's other body changes are runtime adaptations plus reflow.** Word-level diffs (fork → branch) show adaptations in 10 bundles, two reference files and one agent. Everything else differs only in whitespace, which is the reflow that SC2 drops.
- **`main`'s rewrite already removed the Claude-only text the branch adapted in four workflows.** A token scan of `main`'s bodies finds no `Task`, `AskUserQuestion`, `.claude/` or "Skill tool" in `audit-models`, `implement-model`, `orchestrate-modeling`, `plan-model` or `MODELING_PROCESS.md.template`. Those files become "take `main`".
- **Adaptations are still needed in 10 files.** Runtime-specific text remains in `main`'s `manage-sources`, `onboard`, `pdf-analysis` (+ `references/extraction-details.md`), `python-debugger`, `record-learning`, `sysml-conventions/references/stencils.md`, `toolkit-awareness`, `claude/agents/python-debugger.md`, and `MODELING_GUIDE.md.template:282`. Appendix A lists the 17 starting entries.
- **`user-invocable` cannot serve as the classification.** `pdf-analysis` and `record-learning` are supporting skills marked `user-invocable: true`, and `python-debugger` has no such line.
- Agents and supporting-skill reference/script files are unchanged on `main` since the fork. The two pattern docs and `EPIC_GUIDE` changed only on `main`.

**Installer (native snapshot).**

- **The ownership gate is `Installer.permit`** (native `installation.py:66-84`). It accepts an entry whose fingerprint matches the manifest baseline or the desired state. Otherwise it asks, skips non-interactively, or replaces under `--force`. Every replacement passes through it: `write` `:98`, `copy_tree` `:124`, `alias` `:193`, `retire_command` `:208`.
- **The installer already recognizes the old installer's copied files.** It imports the legacy hash manifest (`installation.py:49-52`). It has no rule for the old installer's links.
- **Three places key on `claude/`:**
  - Data-root detection, `cli/__init__.py:108`.
  - The `--dev` prerequisite, `:275`.
  - Hook discovery, `get_hooks_dir` `:137` and `installation.py:339`.
- **Packaging also keys on it:** `pyproject.toml:54` (wheel) and `:65` (sdist).
- **Alias creation is gated by a side effect.** `install_assistants` creates the Claude alias only inside `if shared_ready and "claude" in runtimes and installer.retire_command(...)` (`installation.py:311`).
- **Hand-maintained inventories:**
  - `MBSE_COMMANDS`/`MBSE_SKILLS` (`cli/__init__.py:18-48`).
  - Tests asserting them: `test_cli.py:289`, `test_installation.py:35`.
  - Literal skill lists in `test_cli.py:150-160` and `:454-464`.
  - Counts in `test_cli.py:257-258`, `:268` and `test_installation.py:53`.
- `get_hooks_dir` and `get_agents_dir` have no callers. `get_docs_dir` is public: `main`'s guide template tells agents to import it (`MODELING_GUIDE.md.template:279`).

**Legacy links.**

- **What made them.** fusion-tea's 31 links (`runtime-entries.txt`) were made by `main`'s `init --dev`, which calls `dst.symlink_to(src.resolve())` (`src/agentic_mbse/cli/__init__.py:436`, `:464`, `:491`). `replicate_setup.sh` has always copied (`git show becb459:scripts/replicate_setup.sh:59`). The spec attributes the links to the script; the link shape is the same either way.
- **Their shape.** Every link is absolute, `<checkout>/claude/<kind>/<name>`, with `<kind>` and `<name>` mirroring the entry's own `.claude/<kind>/<name>` location.
- **What they cover.** All 31 names are shipped: 15 commands, 10 skills, 5 agents and 1 hook.

**fusion-tea.**

- Its manifest lists `AGENTS.md` (`install.json`). But `install_assistants` skips an existing entry file before `permit` runs (native `installation.py:325`), so `AGENTS.md` is never overwritten.
- Its `.agentic-mbse/codex.md:7` carries the portable author-continuity rule; `:11` is target-owned.
- `MODELING_GUIDE.md:276` holds the target-owned pattern note.

**Baseline the spec did not record.** `main` itself does not pass ruff or mypy today. `uv run ruff check src/ tests/` reports 118 findings, `ruff format --check` would reformat 78 files, and `uv run mypy src/` reports 91 errors in 19 files. The files this item touches pass ruff today. See Risk R5.

## Core Concept

The end state is a single path: **source tree → `install_assistants` → target.** The source tree holds `skills/`, `agents/`, `adapters/`, `hooks/` and `project_templates/`. The installer has one ownership rule: it replaces what it made and asks about everything else. It already recognizes the old installer's *copied* files by hash. This item teaches it to recognize the old installer's *links* by shape: a link at `.claude/<kind>/<name>` whose target text ends in `claude/<kind>/<name>`, inside an agentic-mbse source checkout. The check lives inside `permit`, as one more answer to "did we make this?". Never writing through links, the prompts and the manifest are untouched.

The content is not hand-merged. A one-time script regenerates the shipped text from `main`'s files: it applies the fixed envelope and a short, reviewed list of literal runtime adaptations. The same script checks a fresh install against that definition. "`main`'s text in the native shape" becomes something a script verifies, not a judgment call over 25 files. After the merge, `claude/` is gone and the tree is the only copy, so the script retires with this item's evidence.

**Why this is the right shape.** Both halves extend something that already exists instead of adding a parallel mechanism. Adoption is the link counterpart of the existing hash rule. Regeneration is the native branch's own envelope applied to new bodies. Most of the installer work is deletion: lists, `claude/` keys, a side-effecting gate.

## Key Bets

- **B1. `main`'s bodies need only the adaptations in Appendix A to work under both runtimes.** The token scan supports this. Tool names such as `Explore` and `WebSearch` that remain in shared text are mapped by the adapters, as the native design intended (native `plan.md:8`). *If false → an instruction points a Codex install at something it lacks. The SC7 property tests or the discovery probe flag it, and the list grows by a reviewed entry.*
- **B2. Claude Code and Codex both ignore an unrecognized `metadata` map in `SKILL.md` frontmatter.** It is the Agent Skills field reserved for custom properties. *If false → bundles vanish from one client's catalog. The discovery probe run on a fresh install shows it, and the field moves (D6 is reversible).*
- **B3. Every link the old installer made is still recognizable when the owner re-inits.** It has the mirrored `claude/<kind>/<name>` shape, and its checkout root still contains `src/agentic_mbse`. *If false → some links are not adopted and fall to prompt-or-preserve, leaving clutter. The rehearsal's adopted count (expected 31) shows it.*
- **B4. Only the two passages named in SC9 are target-owned text that a re-init would silently replace.** *If false → information is lost at re-init. The rehearsal diffs every file replaced without a prompt against its pre-init content to confirm it.*

## Key Decisions

- **D1. Integrate by merging into a new branch.** In a fresh worktree on a new branch `nsd-integration` cut from `wrap-split`, run `git merge native-claude-codex-skills`.
  - **Why this way:** `wrap-split` is `main` plus this item's planning artifacts, so they arrive with the branch. The native branch stays at its audited `86921f9`. First-parent history reads as `main`'s.
  - *Rejected: rebase (replays every branch commit through rename and reflow conflicts, and rewrites the SHAs the native audit cites). Also rejected: merging `wrap-split` into the existing native worktree (moves the audited baseline and makes the native line first-parent).*
- **D2. Resolve content conflicts by regenerating, not by hand.** `reconcile.py write` rewrites `skills/**`, `agents/*.md`, the tool-owned templates and `hooks/` from `main`'s files. `claude/` is then removed. *Rejected: resolving 25+ rename/modify conflicts file by file, which is a judgment per file and invites reflow noise.*
- **D3. The envelope is a text-level transform.**
  - **Workflow frontmatter:** delete the `skills:` line, change `Task` to `Agent` on the `allowed-tools` line, and append `metadata:` / `kind: workflow`. Supporting skills get `kind: supporting`. The kind comes from `main`'s location (`claude/commands/` or `claude/skills/`).
  - **Preface:** the branch's preface paragraph goes after the frontmatter, followed by one blank line.
  - **Everything else is `main`'s bytes.**
  - *Rejected: a YAML round-trip (it reformats folded descriptions, creating differences outside the envelope). Rejected: injecting the preface at install time (it breaks `--dev` links, and installed bytes would no longer equal source bytes).*
- **D4. The adaptation list is `adaptations.yaml` in this item's folder.** Each entry has `id`, `file`, `old`, `new`, `count`, `why` and `origin` (`branch` or `item1`). One script, `reconcile.py`, applies the list (`write`) and verifies it (`check`). *Rejected: a markdown table (a machine cannot check it). Rejected: regex rules (harder to review, and they can over-match).*
- **D5. Legacy links are recognized by path shape plus an agentic-mbse checkout root, inside `permit`.** See Architecture § Legacy adoption. *Rejected: shape alone (any folder named `claude/` would qualify, such as a personal copy of a command). Rejected: a recorded list of checkout roots (a machine-specific list in source that misses other clones and worktrees).*
- **D6. The workflow/supporting split is `metadata.kind` in each bundle's frontmatter.** `install-commands --list` groups by it, and a property test requires it. The deletion guard is a skill-reference integrity test, which needs no edit when a skill is added. *Rejected: reusing `user-invocable` (it does not match the split). Rejected: a count floor (an inventory number that has to be bumped).*
- **D7. The hook moves to a top-level `hooks/`.** It is still installed only for Claude. *Rejected: `adapters/claude/hooks/` (turns a folder of adapter files into a mixed tree for one script).*
- **D8. One predicate defines "a source checkout": `is_source_checkout(root)`.** It is true when `root/src/agentic_mbse` exists. Data-root detection, the `--dev` prerequisite and legacy adoption all use it. *Rejected: swapping the `claude/` marker for `skills/` (the wheel's data folder also has `skills/`, so `--dev` would wrongly pass on a wheel install).*
- **D9. Replace `retire_command` with two pieces.**
  - **`Installer.remove(relative)`:** removes an entry only after `permit` allows it, never writes through a link, and drops the manifest key.
  - **`expose_to_claude(...)`:** the helper holds the Claude policy. If the owner keeps a same-name legacy command, it reports that (keeping the F-F message) and returns. Otherwise it creates the alias, or a copy.
  - *Rejected: keeping a side effect inside the loop's boolean condition, with Claude policy spread across installer methods.*
- **D10. Both target-owned passages go to fusion-tea's `AGENTS.md` (SC9).** The proposed change appends them verbatim. It does not touch `.agentic-mbse/codex.md` or `MODELING_GUIDE.md`: those must still match their manifest hash so the re-init replaces them with the reconciled text.
  - **Why `AGENTS.md`:** both passages exist for the Codex sandbox, which reads pattern docs from a copy inside the worktree.
  - **Effect on Claude:** Claude will follow the guide's `get_docs_dir()` resolver instead. After runbook step 1, that resolver points at the same-version docs. The ledger row states this, so the owner can also copy the note into `CLAUDE.md` if they want it there.
  - *Rejected: `CLAUDE.md` plus `AGENTS.md` (duplicate text). Rejected: `REQUIREMENTS.md` (it holds model requirements, not tool setup). Rejected: deleting the passages from the tool-owned files in the patch (their hash would stop matching, the re-init would prompt or skip, and the reconciled text would not land).*
- **D11. The SC11 audit is bounded to the installer, the list and the evidence.**
  - **In scope:** the installer diffed against the fork `88e2489`, which covers A–K and this item together. Also the A–K checklist, the adaptation list, the `reconcile.py check` output, and the rehearsal, runbook and patch.
  - **Out of scope:** body text beyond the list. SC2 makes that mechanical.
  - **Who runs it:** a fresh non-author agent, via the orchestrator's audit stage.
  - *Rejected: re-reading all 25 bodies. Rejected: a separate A–K review of a target that is still moving.*
- **D12. `--dev`'s `.gitignore` block stops listing `.claude/commands/` and `.claude/.tool-hashes.json`.** The installer no longer writes either path. *Rejected: keeping them (the installer would claim paths it does not manage, and re-ignore owner commands such as fusion-tea's).*
- **D13. The rehearsal re-points the copy's legacy links at the integration worktree's `claude/` folder, which no longer exists.** This reproduces the post-merge dangling state. *Rejected: leaving links into `/home/reid/1cfe/agentic-mbse/claude/` (a write-through bug would edit what fusion-tea reads live, and the dangling case would never run).*

## Architecture

### End state: one source, one path

```
skills/<n>/SKILL.md (+ references/, scripts/)  ─┐
agents/<n>.md   adapters/{claude,codex}.md      ├─ install_assistants ─┬─ .agents/skills/<n>/   (canonical, both runtimes)
hooks/<h>       project_templates/*.template   ─┘   (Installer: permit) ├─ .claude/skills/<n> → alias, .claude/agents/, .claude/hooks/
                                                                        └─ .codex/agents/*.toml + config.toml, .agentic-mbse/<rt>.md
```

- **`init` and `install-commands` both call `install_assistants`.** `scripts/replicate_setup.sh` is a six-line wrapper that runs `init` on this checkout.
- **The data root comes from `_get_data_root()`.** It is the source checkout when `is_source_checkout` holds, otherwise `site-packages/agentic_mbse_data/`. The wheel force-includes `skills`, `agents`, `adapters`, `hooks`, `docs`, `project_templates` and `SOURCE_INDEX.md.template`.
- **The inventory is the tree.** `skill_bundles()` globs `skills/*/SKILL.md`, agents glob `agents/*.md`, and hooks glob `hooks/*`. `bundle_kind()` reads `metadata.kind` for `--list`.

### Legacy adoption (code-level behaviour)

The rule is one predicate, consulted in `permit` after the manifest check:

```
legacy_link_target(relative) -> str | None:
  parts = relative's path parts
  require len(parts) == 3, parts[0] == ".claude", parts[1] in {commands, skills, agents, hooks}
  require (target / relative) is a symlink                       # never stat the referent
  old = normpath(entry's parent / os.readlink(entry))            # textual; works when dangling
  require old's last three parts == ("claude", parts[1], parts[2])
  require is_source_checkout(old.parents[2])                     # the checkout root, not claude/
  return old
permit: ... if fingerprint matches → True; elif legacy_link_target → record adopted, True; else ask/skip/force
```

**Why each part of SC8's boundary holds:**

- **Shipped name.** `permit` is only reached for entries the installer is about to install or retire, and those are all derived from the source tree (Invariant I2). The owner's `manage-concept.md`, `research-acquire.md`, unshipped skills and the five `.agents/skills/` owner links therefore never reach it.
- **Old location and link-only.** These are checked directly in the predicate.
- **Points into an agentic-mbse `claude/` folder.** The shape check and the checkout-root check cover it. After the merge, the root still exists (`/home/reid/1cfe/agentic-mbse` with `src/agentic_mbse`); only `claude/` has gone.

**Where adoption happens for each kind of entry:**

- **Commands:** `expose_to_claude` calls `remove(".claude/commands/<n>.md")`. `permit` adopts the link, it is unlinked, and the alias follows.
- **Skills:** `alias` calls `permit` on `.claude/skills/<n>`. The link is adopted, unlinked, and replaced by a relative alias. In copy mode, `copy_tree` does the same.
- **Agents and the hook:** `write` calls `permit`, then unlinks and writes the rendered agent or the hook.

**The report.** A new action bucket, `adopted`, holds `"<relative> (was -> <old target>)"`. `cmd_init` prints it under "Adopted (N) — links from the pre-native installer replaced", and `install-commands` reports it too. For fusion-tea the expected count is 31.

### One-time integration flow

```
main@8f43a09: claude/commands/*.md, claude/skills/**, claude/agents/*.md, claude/hooks/*, 3 templates, docs/patterns/*
      │  reconcile.py write  (path rule + envelope + adaptations.yaml)
      ▼
skills/<n>/SKILL.md …, agents/*.md, hooks/*, project_templates/*  ──►  git rm -r claude/
      │  uv run agentic-mbse init <tmp> --assistant both
      ▼
reconcile.py check: installed bytes == expected; every adaptation applied exactly `count` times; file sets equal → SC2 pass + SC1 rows
```

**The path rule:**

- `claude/commands/<n>.md` → `skills/<n>/SKILL.md` (workflow).
- `claude/skills/<n>/**` → `skills/<n>/**` (supporting).
- `claude/agents/<n>.md` → `agents/<n>.md`.
- `claude/hooks/<h>` → `hooks/<h>`.
- Templates and `docs/patterns/` keep their paths.

**How `check` compares.** Bundles and templates are compared against the fresh install. Agents, the hook and pattern docs are compared against the source tree: agents are rendered at install, and pattern docs are packaged rather than installed. `--main <rev>` lets both commands re-run if `main` moves.

## Required Invariants

- **I1.** The installer never writes through a symlink. Adoption only unlinks the link itself.
- **I2.** `permit` and `remove` are reached only for entries derived from the source tree. This is what makes "the installer ships its name" true by construction.
- **I3.** Recognition never reads the referent. It uses `os.readlink` text and the checkout root's `src/agentic_mbse`.
- **I4.** No list in `src/` or `tests/` names a skill, agent or hook. Tests derive the inventory from the tree.
- **I5.** No `claude/` folder exists in the source tree, the sdist or the wheel.
- **I6.** `get_docs_dir()` stays importable from `agentic_mbse.cli` and resolves for source and wheel installs. The guide's resolver text depends on it.
- **I7.** Every `SKILL.md` carries `name` equal to its folder, a `description`, a `metadata.kind` of `workflow` or `supporting`, no `skills:` key, and the shared preface as its first paragraph.
- **I8.** The proposed fusion-tea change edits only fusion-tea-owned files.

## Component Overview

**Removed**

- `claude/` entirely. Its last file, `claude/hooks/ruff-format.sh`, moves to `hooks/`.
- `MBSE_COMMANDS` and `MBSE_SKILLS` (`cli/__init__.py:18-48`), with their test imports and assertions.
- `retire_command` (`installation.py:202-221`).
- The `claude` keys in `_get_data_root`, `_check_dev_mode_prerequisites` and `pyproject.toml`.
- Two lines of `DEV_MODE_GITIGNORE_PATHS` (D12).
- The literal skill lists and counts in `test_cli.py` and `test_installation.py`.

**Changed**

- **`installation.py`:**
  - `permit` gains adoption.
  - New `is_source_checkout`, `legacy_link_target`, `remove`, `expose_to_claude` and `bundle_kind`.
  - `install_assistants` reads `hooks/` and calls `expose_to_claude`.
- **`cli/__init__.py`:**
  - The data root and the `--dev` check use `is_source_checkout`.
  - `get_hooks_dir` points at `hooks/`.
  - `--list` groups by kind.
  - Both commands print the adopted entries.
- **`pyproject.toml`:** `hooks` replaces `claude` in the wheel force-include and the sdist include.
- **`adapters/claude.md:7` and `adapters/codex.md:7`:** the "fresh stages require new agents" sentence becomes fusion-tea `codex.md:7`'s rule. Keep a continuing author while its context is useful; independent review needs a fresh non-author agent (SC3).
- **25 `SKILL.md`, 5 agents and 3 templates:** regenerated from `main` (D2–D4).
- **`tests/test_modeling_command_contracts.py`:** take `main`'s version, change paths from `claude/commands/<n>.md` to `skills/<n>/SKILL.md`, and change `Task` to `Agent` at `:72`.
- **`CLAUDE.md`:** Architecture, Change Coordination and Init File Ownership describe the one installer, the `kind` field, `hooks/`, legacy adoption and the `replicate_setup.sh` wrapper (SC12). README's installer paragraph changes to match.

**Added (evidence, not shipped), in `.project/active/native-skill-distribution/`**

- `reconcile.py` and `adaptations.yaml`.
- `dispositions.md` (SC1; the bundle, template and agent rows are emitted by `check`).
- `rehearsal.md` (SC8, SC10) and `fusion-tea-runbook.md` (SC10).
- `fusion-tea-target-owned.patch` (SC9).
- The Item 1 section of `.project/active/wrap-split-migration-ledger.md`. This item creates the file.

Appendix B maps each change to a file.

## Non-Goals

- **The post-merge install mode.** That choice is parked for the owner. Both modes are made to work, and the rehearsal reports both.
- **Pattern-doc installation.** The guide takes `main`'s `get_docs_dir()` resolver text.
- **fusion-tea's local same-name skills.** When Items 2 and 5 ship `run-goal`, `narrate-goal` or `research-acquire`, fusion-tea's local copies will meet prompt-or-preserve. The epic's integration step handles them.
- **Clearing `main`'s pre-existing ruff and mypy debt** (Risk R5).
- **Editing tool names that the adapters already map** (`Explore`, `WebSearch`, `Glob` in shared prose).

## Implementation Notes

- **Worktree setup is the orchestrator's job, from `/home/reid/1cfe/agentic-mbse`, with no branch switch:**
  1. `git worktree add -b nsd-integration /home/reid/1cfe/agentic-mbse-nsd-integration wrap-split`, after the plan is committed on `wrap-split`. Later planning commits come in with `git merge wrap-split`.
  2. Copy the gitignored `.env` (it holds `SYSIDE_LICENSE_KEY`), then run `uv sync`.
  3. Stage a copy of fusion-tea's working tree with `rsync -a --exclude .venv` into the worktree's gitignored `.orchestrate-logs/rehearsal/`. It has to be a filesystem copy, not a clone: the legacy links are gitignored and would be lost in a clone.
- **Merge conflict rules:**
  - Installer code, `pyproject.toml`, `scripts/`, `README.md` and `CLAUDE.md`: take the branch side, since `main` did not change them.
  - `claude/**` content: regenerate (D2), then delete. `orchestrate-modeling` is a modify/delete conflict and resolves the same way.
  - `.project/CURRENT_WORK.md`: keep the `wrap-split` side.
  - The spike and research files that both sides added: keep `main`'s copy if they differ, and record that in `dispositions.md`.
- **Envelope details:**
  - The preface constant is the branch's text verbatim, including the typographic apostrophe.
  - Insert one blank line after the preface. Do not alter `main`'s leading body bytes.
  - Write `kind` as the last frontmatter key.
- **Adaptation entries:**
  - Copy each `new` string verbatim from the branch (word diffs in `.orchestrate-logs/nsd-design-scratch/wdiff.py`).
  - A1 is the onboard `OVERVIEW.md` change, which the reviewer called a content change. It stays in the list as an adaptation. The installer's entry files point to `OVERVIEW.md` (native `installation.py:328`), so it is the one context file both runtimes read. Flag A1 for the one-time review.
- **Test fixture updates:**
  - `test_bundle_retirement_prunes_only_unchanged_resources` builds a fake data root that symlinks `claude`. It now creates `src/agentic_mbse/` and symlinks `hooks` instead.
  - Legacy-adoption fixtures build a fake checkout root (`<tmp>/old/src/agentic_mbse/`) and create links with or without `<tmp>/old/claude/`.
  - `test_dev_updates_gitignore` and `test_dev_gitignore_idempotent` assert and count `.claude/commands/`. After D12 they key on `.claude/skills/` instead.
- **Ordering inside `permit`:** adoption sits after the manifest/desired check and before `force`/`decide`, so `--force` is never needed.

## Potential Risks

- **R1. A client rejects `metadata`** (B2). Run the native discovery probe (native `.project/active/native-skills/discovery_probe.py`, which needs no model turns) on a fresh install right after content regeneration, before the installer work. If it fails, move the field and re-run.
- **R2. `main` moves before the owner merges.** Merge `main` again and re-run `write` and `check` with `--main main`. The exact adaptation counts make drift fail loudly.
- **R3. The rehearsal cannot do runbook step 1 for real**, because the merged SHA is not on GitHub yet. The rehearsal runs the worktree's CLI instead, and the wheel test proves the packaged bytes equal the source. The report notes one difference. Rendered agents and `.claude/settings.json` record the docs path of whichever CLI runs. That path is fusion-tea's `.venv` if the owner uses fusion-tea's own CLI.
- **R4. A link whose checkout was deleted is not adopted.** This fails safe: the link is prompted for or preserved. The runbook says to re-init before deleting or moving any old checkout.
- **R5. SC12 as written cannot pass** (premise conflict, surfaced). `main` fails ruff and mypy before this item. The design's gate:
  - pytest passes;
  - ruff check, ruff format and mypy report no findings beyond `main`'s baseline at the merge base;
  - every file this item changes is clean.

  The orchestrator or owner must confirm this reading of SC12.
- **R6. `--dev` effects on fusion-tea's `.gitignore` and tracked Codex files.** The rehearsal reports them. The decision is the owner's.
- **R7. The broken Claude window.** Plain `init` from fusion-tea's own environment (after step 1) works before `/home/reid/1cfe/agentic-mbse` moves, because adoption does not need the targets to exist. The runbook orders it first, which removes the window. `--dev` must run from the moved canonical checkout, so its window is the minutes between `git pull` and `init`.

## Integration Strategy

- **What this replaces:** `main`'s `claude/` + `MBSE_*` installer and the branch's leftover lists.
- **What it builds on:** the native installer, its manifest and its tests.
- **What comes next:** Items 2 and 5 register skills by adding `skills/<n>/` with `metadata.kind`. Item 4 edits `skills/` text directly. The epic's integration step later removes fusion-tea's local skills.
- **What fusion-tea receives:** the patch, the ledger rows and the runbook. The owner applies all three.

## Validation Approach

| SC | Evidence | Kind |
|---|---|---|
| SC1 | `dispositions.md`. `check` emits the bundle, template and agent rows; hand rows cover adapters, user-owned templates, installer, tests, the `.project/` conflicts and the 3 target-owned passages | evidence |
| SC2 | `reconcile.py check --main 8f43a09` on a fresh `--assistant both` install exits 0. `adaptations.yaml` is reviewed once in the audit | evidence |
| SC3 | Property test: neither adapter says every stage needs a new agent, and both carry the continuity and independent-review rule | pytest |
| SC4 | Covered by SC2: the guide equals `main` plus adaptation A17. A test asserts the installed guide contains no `.claude/settings.json` | pytest + evidence |
| SC5 | Behaviour test on a fake data root with no other edit. An extra `skills/new-skill/` (kind workflow) is installed for both runtimes and listed under workflows. An extra `agents/new-role.md` is rendered for both runtimes and registered in `.codex/config.toml`. Invariant I7 test | pytest |
| SC6 | Test that `claude/` is absent from the repo. `init` installs an executable hook. `init --dev` links the hook into `hooks/`. `--dev` is refused on a non-checkout data root. Wheel test (one build): every file under each force-included folder is byte-equal, there is no `claude/` member, and running `cmd_init` from the extracted wheel (subprocess, `PYTHONPATH`) installs all bundles, agents and the hook | pytest |
| SC7 | The existing claude/codex/both × symlink/copy matrix with the inventory derived from the tree. Every file in every bundle is reachable through `.agents/skills/` and the Claude alias. Every backticked `` `/name` `` and every `.agents/skills/<n>/` path in installed text resolves. No installed skill, template or Codex role names `.claude/`. The discovery probe runs on the 3 fresh installs | pytest + evidence |
| SC8 | Parametrized over commands, skills, agents and hooks, with the target existing or dangling: adopted, reported with the old target, referent unchanged. Negative cases (unshipped name, non-checkout root, non-mirrored tail, real file, real dir) keep prompt-or-preserve. A mixed legacy tree built from the source inventory. The rehearsal on the fusion-tea copy: Adopted (31); probe shows 25 skills and 5 agents; hook present; fusion-tea's own entries hash-identical | pytest + evidence |
| SC9 | `fusion-tea-target-owned.patch` passes `git apply --check` on the copy at `403716ee3`. Ledger rows exist. After rehearsal re-init, both passages are present in `AGENTS.md` | evidence |
| SC10 | `rehearsal.md` for each mode on its own copy (patch first, then a non-interactive `init`, then a second `init`). It reports `git status`, the `.gitignore` diff, the files replaced with no prompt (each diffed for target-owned loss, B4), the preserve lines (each one a prompt in an interactive run), and the MR-7 paragraphs present in `MODELING_PROCESS.md`. The runbook cites the observed results | evidence |
| SC11 | Audit stage per D11. The native `audit.md` gains a dated verdict update | audit |
| SC12 | The merged branch carries `main`'s history (`git merge-base --is-ancestor main HEAD`). The R5 gate holds. CLAUDE.md is updated | evidence |

Product-lens falsifiers (`product-lens.md:35`): (a) is covered by SC5, (b) by SC2 and SC7, and (c) by SC8 and SC10.

## Next-Stage Handoff

**Fixed:**

- D1–D13.
- The envelope definition.
- The legacy predicate and where it sits in `permit`.
- `AGENTS.md` as the SC9 home.
- The evidence-folder location of the reconcile tooling.

**Open for the plan:**

- Exact helper signatures.
- `--list` output layout.
- Wording of the adopted report line.
- Final `adaptations.yaml` content. Start from Appendix A, and let `check` prove the counts.

**Open for the owner:**

- The install mode (parked).
- The SC12 ruff/mypy reading (R5).

**Suggested phases:**

1. **Worktree, merge and content.** Run `write`, delete `claude/`, port the contract test, `check` passes, and run the discovery probe to de-risk B2 first.
2. **Source-tree shape.** The `hooks/` move, `is_source_checkout`, packaging, removing `MBSE_*`, `kind` and `--list`, and the derived tests.
3. **Legacy adoption.** `permit`, `remove`/`expose_to_claude`, the report, and the SC8 tests.
4. **Text.** Adapters (SC3), then CLAUDE.md and README.
5. **Evidence.** The wheel test, probes, the rehearsal in both modes, the patch, the ledger, the runbook and the dispositions.

Then comes the independent audit stage.

---

## Appendix A — Starting adaptation list (applied to `main`'s text)

Taken from fork→branch word diffs; `main` equals the fork for every file below except `toolkit-awareness` and the guide template.

| ID | Source path | Change (old → new, verbatim from branch unless noted) | Count |
|---|---|---|---|
| A1 | `skills/onboard/SKILL.md` | `` **`CLAUDE.md`** `` → `` **`modeling_project/OVERVIEW.md` and the current assistant’s entry file (`CLAUDE.md` or `AGENTS.md`)** `` (flag for review) | 1 |
| A2 | `skills/onboard/SKILL.md` | `` `README.md` and `CLAUDE.md` `` → `` `README.md` and the current assistant’s entry file `` | 1 |
| A3 | `skills/onboard/SKILL.md` | `in text, not AskUserQuestion` → `in text, not the host question interface` | 1 |
| A4 | `skills/onboard/SKILL.md` | `:57` read-permission sentence → adapter external-source sentence | 1 |
| A5 | `skills/manage-sources/SKILL.md` | `` (and optionally `.claude/settings.json` permissions) `` → `(and optionally native read-access settings)` | 1 |
| A6 | `skills/manage-sources/SKILL.md` | `AskUserQuestion` → `the host question interface` | 4 |
| A7 | `skills/manage-sources/SKILL.md` | `:52` "Offer permissions for local paths" paragraph → adapter-based access paragraph | 1 |
| A8 | `skills/pdf-analysis/SKILL.md` | `.claude/skills/pdf-analysis/` → `.agents/skills/pdf-analysis/` | 6 |
| A9 | `skills/pdf-analysis/references/extraction-details.md` | same as A8 | 3 |
| A10 | `skills/python-debugger/SKILL.md` | `python scripts/claude_debugger.py` → `uv run python .agents/skills/python-debugger/scripts/claude_debugger.py` | 7 |
| A11 | `skills/record-learning/SKILL.md` | `AskUserQuestion` → `the host question interface` | 2 |
| A12 | `skills/record-learning/SKILL.md` | `(via Skill tool)` → `(through the host’s skill-loading interface)` | 1 |
| A13 | `skills/sysml-conventions/references/stencils.md` | `` Agents have read permissions via `.claude/settings.json`. `` → `` Consult the current assistant adapter in `.agentic-mbse/` for external-document access. `` | 1 |
| A14 | `skills/toolkit-awareness/SKILL.md` | `` **Read `CLAUDE.md`** `` → `` **Read the current assistant’s project instructions (`CLAUDE.md` or `AGENTS.md`)** `` | 1 |
| A15 | `skills/toolkit-awareness/SKILL.md` | `` documented in `CLAUDE.md`. `` → `` documented in the current assistant’s project instructions (`CLAUDE.md` or `AGENTS.md`). `` | 1 |
| A16 | `agents/python-debugger.md` | `.claude/skills/python-debugger/` → `.agents/skills/python-debugger/` | 14 |
| A17 | `project_templates/MODELING_GUIDE.md.template` | `` Agents have read permissions via `.claude/settings.json`; permission alone `` → `` Consult the current assistant adapter in `.agentic-mbse/` for external-document access; access alone `` (origin `item1`, wording from branch `:273`) | 1 |

Dropped from the branch's list because `main` already removed the text: `audit-models` (`AskUserQuestion`), `implement-model`, `orchestrate-modeling` and `plan-model` (`Task`). Reflow-only changes (`sysml-expert`, `debugging_internals.md` and the rest) are dropped as well.

## Appendix B — File-level change list (integration branch vs `wrap-split`)

| Path | Change |
|---|---|
| `claude/**` | Deleted (content regenerated elsewhere; hook moved) |
| `skills/<25>/**`, `agents/<5>.md` | Added by merge, then regenerated by `reconcile.py write` |
| `hooks/ruff-format.sh` | Moved from `claude/hooks/` (bytes equal to `main`) |
| `adapters/{claude,codex}.md` | Added by merge; line 7 edited (SC3) |
| `project_templates/MODELING_GUIDE.md.template`, `MODELING_PROCESS.md.template`, `EPIC_GUIDE.md.template` | `main` text + A17 (guide only) |
| `project_templates/{README,OVERVIEW}.md.template` | Branch side (user-owned; branch-only change) |
| `src/agentic_mbse/cli/installation.py` | Branch side + adoption, `is_source_checkout`, `remove`, `expose_to_claude`, `bundle_kind`, `hooks/` |
| `src/agentic_mbse/cli/__init__.py` | Branch side − `MBSE_*` − `claude` keys − 2 gitignore lines; `--list` by kind; adopted report |
| `pyproject.toml` | Branch side; `claude` → `hooks` in wheel and sdist includes |
| `scripts/replicate_setup.sh` | Branch side (6-line `init` wrapper), unchanged |
| `tests/test_installation.py`, `tests/test_cli.py` | Branch side; lists and counts derived; SC5/SC6/SC7/SC8 tests added |
| `tests/test_packaged_guidance_contract.py` | Branch side; folder set from `pyproject.toml`; no `claude/` member; extracted-wheel init |
| `tests/test_modeling_command_contracts.py` | `main` side; paths re-pointed; `Task` → `Agent` |
| `CLAUDE.md`, `README.md` | Branch side; installer sections updated (SC12) |
| `.project/active/native-skill-distribution/*` | Evidence files listed in Component Overview |
| `.project/active/wrap-split-migration-ledger.md` | Created with the Item 1 section |
| `.project/active/native-skills/audit.md` | Arrives by merge; dated verdict update from this item's audit |

---

Next Step: `/_my_design_review` in a fresh session, then `/_my_plan`.

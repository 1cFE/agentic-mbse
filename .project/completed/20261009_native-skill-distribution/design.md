# Design: Reconcile the native installer source with `main` (WRAP-SPLIT Item 1)

**Status:** Draft (revised after design review)
**Owner:** Reid W
**Created:** 2026-10-09 10:00 PDT
**Updated:** 2026-10-09: applied the design review's Resolutions (`design-review.md`, verdict Revise). The `--dev` gitignore decision was cut (S3), so the rehearsal decision moved from D13 to D12, and D13 is new (this repo's tracked `.claude/` copies, C2). The first draft is at `fc0bcb9`. 2026-10-09, later: applied two orchestrator calls. This repo's reinstall is `install-commands --assistant claude`, not `replicate_setup.sh` (D13). Its tracked scaffold cleanup is a follow-up (R7, Non-Goals). 2026-10-09, after the audit: D14 amends how `--dev` installs the shared bundles (audit B1, plan Phase 9).
**Planning branch:** `wrap-split` (this file). Implementation: new branch `nsd-integration` in a fresh worktree (D1).
**Spec:** `spec.md` (revised after `spec-review.md`; Align decisions in `briefs/00-align.md`)

## Overview

Bring the native branch onto `main` so the tool-neutral source tree carries `main`'s current text and is the only thing the installer reads. Extend the installer's ownership rule so it takes over the links the old installer left in fusion-tea, and give the owner a rehearsed runbook for switching fusion-tea, and this repo's own install, over.

## Related Artifacts

- Spec: `.project/active/native-skill-distribution/spec.md`; spec review: `spec-review.md`; design review: `design-review.md`; Align: `briefs/00-align.md`; brief: `briefs/03-design.md`
- Epic: `.project/backlog/epic_wrap-split.md` § Item 1
- Required Reading: native `.project/active/native-skills/{plan,remediation,audit}.md`; fusion-tea `.project/active/harness-right-size/{report.md,installed.json}`; `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 4
- Read-only inputs: `.orchestrate-logs/nsd-inputs/` (native at `86921f9`, fusion-tea at `403716ee3`). Cited below as "native" and "fusion-tea".
- Product-lens: `product-lens.md` (falsifiers (a)–(c) at `:35` are checked in Validation; design-F1 to F3 are disposed by S9, S2 and M4 here)
- No `.project/adr/` exists, so no decision records apply.

## The Point

[NEED] (owner, verbatim, `briefs/00-align.md:19`) "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this".

[AGENT] (stated by the orchestrator in the Align message 2026-10-09; the owner did not object, and the verbatim ask above supports it; `briefs/00-align.md` § "The point, as read at Align", `:41`; carried as agent-grade, not settled, at `spec.md:77`) One place to register a skill. After this item:

- The tool-neutral source tree is the only installer source.
- It carries `main`'s current text.
- `agentic-mbse init` installs it the same way for Claude Code and Codex.

Why it matters now: Items 2 and 5 register new skills and Item 4 edits shipped text. Until the two installer sources become one, each of those edits must be made twice or stranded behind a 58-commit gap. The fusion-tea side carries two owner criteria (`[NEED]`, epic `:65-66`): no loss of information, and MR-7 enforcement intact after re-init.

## Research Findings

**Content (measured 2026-10-09 against fork `88e2489`, `main` `8f43a09`, native `86921f9`).** Evidence scripts are in `.orchestrate-logs/nsd-design-scratch/` and the reviewer's in `.orchestrate-logs/design-review-scratch/` (both gitignored).

- **The branch's envelope is fully mechanical.** For workflows it drops the `skills:` line and changes `Task` to `Agent` in `allowed-tools`. Supporting-skill frontmatter is unchanged. Every bundle gets the same preface paragraph (native audit F-I confirmed all 25 byte-identical). Agents keep their frontmatter. The reviewer re-ran this transform from the fork and reproduced the branch's frontmatter for all 25 bundles.
- **The branch's other body changes are runtime adaptations plus reflow.** Word-level diffs (fork → branch) show adaptations in 10 bundles, two reference files and one agent. Everything else differs only in whitespace, which is the reflow that SC2 drops.
- **`main`'s rewrite already removed the Claude-only text the branch adapted in four workflows.** A token scan of `main`'s bodies finds no `Task`, `AskUserQuestion`, `.claude/` or "Skill tool" in `audit-models`, `implement-model`, `orchestrate-modeling`, `plan-model` or `MODELING_PROCESS.md.template`. Those files become "take `main`".
- **Adaptations are still needed in 10 files.** Runtime-specific text remains in `main`'s `manage-sources`, `onboard`, `pdf-analysis` (+ `references/extraction-details.md`), `python-debugger`, `record-learning`, `sysml-conventions/references/stencils.md`, `toolkit-awareness`, `claude/agents/python-debugger.md`, and `MODELING_GUIDE.md.template:282`. Appendix A lists the 17 starting entries. Their counts are body counts; the reviewer confirmed all 17 against `main`.
- **`user-invocable` cannot serve as the classification.** `pdf-analysis` and `record-learning` are supporting skills marked `user-invocable: true`, and `python-debugger` has no such line.
- Agents and supporting-skill reference/script files are unchanged on `main` since the fork. The two pattern docs and `EPIC_GUIDE` changed only on `main`.
- **Two files are executable.** `claude/hooks/ruff-format.sh` and `claude/skills/pdf-analysis/scripts/extract_page.py` are mode `100755` in git.

**Installer (native snapshot).**

- **The ownership gate is `Installer.permit`** (native `installation.py:66-84`). It accepts an entry whose fingerprint matches the manifest baseline or the desired state. Otherwise it asks, skips non-interactively, or replaces under `--force`. Every replacement passes through it: `write` `:98`, `copy_tree` `:124`, `alias` `:193`, `retire_command` `:208`.
- **The installer already recognizes the old installer's copied files.** It imports the legacy hash manifest (`installation.py:49-52`). It has no rule for the old installer's links.
- **Three places key on `claude/`:**
  - Data-root detection, `cli/__init__.py:108`.
  - The `--dev` prerequisite, `:275`.
  - Hook discovery, `get_hooks_dir` `:137` and `installation.py:339`.
- **Packaging also keys on it:** `pyproject.toml:54` (wheel) and `:65` (sdist).
- **Alias creation is gated by a side effect.** `install_assistants` creates the Claude alias only inside `if shared_ready and "claude" in runtimes and installer.retire_command(...)` (`installation.py:311`). `retire_command` already calls `permit`, so adoption reaches legacy commands with no change there.
- **Hand-maintained inventories:**
  - `MBSE_COMMANDS`/`MBSE_SKILLS` (`cli/__init__.py:18-48`).
  - Tests asserting them: `test_cli.py:289`, `test_installation.py:35`.
  - Literal skill lists in `test_cli.py:150-160` and `:454-464`.
  - Counts in `test_cli.py:257-258`, `:268` and `test_installation.py:53`.
- `get_hooks_dir` and `get_agents_dir` have no callers. `get_docs_dir` is public: `main`'s guide template tells agents to import it (`MODELING_GUIDE.md.template:279`).
- **Claude's catalog lists only user-invocable skills.** The native discovery probe found 18 skills in Claude and 25 in Codex (native `.project/active/native-skills/remediation-discovery.json`). The seven `user-invocable: false` reference skills never appear in Claude's catalog.

**Legacy links.**

- **What made them.** fusion-tea's 31 links (`runtime-entries.txt`) were made by `main`'s `init --dev`, which calls `dst.symlink_to(src.resolve())` (`src/agentic_mbse/cli/__init__.py:436`, `:464`, `:491`). `replicate_setup.sh` has always copied (`git show becb459:scripts/replicate_setup.sh:59`). The spec attributes the links to the script; the link shape is the same either way.
- **Their shape.** Every link is absolute and `resolve()`-clean (no `.` or `..`), of the form `<checkout>/claude/<kind>/<name>`, with `<kind>` and `<name>` mirroring the entry's own `.claude/<kind>/<name>` location.
- **What they cover.** All 31 names are shipped: 15 commands, 10 skills, 5 agents and 1 hook.

**This repo's own install (found by the design review, C2).**

- `git ls-files .claude` lists 23 tracked entries, last touched at `becb459`, before the fork. Neither side has changed them since.
- 21 of them are stale copies: 9 commands, 3 supporting skills with their reference and script files, the 5 agents and the hook.
- One is a tracked absolute symlink, `.claude/skills/pdf-analysis -> /home/reid/1cfe/agentic-mbse/claude/skills/pdf-analysis`. It dangles in every clone once `claude/` is gone.
- The last is `.claude/settings.json`, which stays.
- No install manifest exists in this repo. So any reinstall would prompt for or preserve the 9 real command files, and a preserved command blocks its Claude alias (native `installation.py:311`).
- **Two install commands exist, and only one is assistant-only.** `install-commands` runs only `install_assistants` and writes no project scaffold (native `cli/__init__.py:686-697`). `init`, which `scripts/replicate_setup.sh` wraps, also writes the user-owned scaffold. That scaffold includes `tests/models/test_example.py`, which pytest would collect.
- This repo also tracks a whole init scaffold (`modeling_project/`, `work/`, `knowledge/`, `data/`). That includes copies of the tool-owned templates (`modeling_project/MODELING_GUIDE.md`, `modeling_project/MODELING_PROCESS.md`, `work/EPIC_GUIDE.md`, `work/backlog/epic_template.md`), and the first three differ from `project_templates/` today. See Risk R7.

**fusion-tea.**

- Its manifest lists `AGENTS.md` (`install.json`). But `install_assistants` skips an existing entry file before `permit` runs (native `installation.py:325`), so `AGENTS.md` is never overwritten.
- Its `.agentic-mbse/codex.md:7` carries the portable author-continuity rule; `:11` is target-owned.
- `MODELING_GUIDE.md:276` holds the target-owned pattern note. Its 14 manifest hashes for `.agentic-mbse/patterns/*` all equal `main`'s `docs/patterns/` at `8f43a09` (reviewer, `nsd_patterns.py`).

**Lint baseline.** `main` fails ruff (118 findings, 78 files unformatted) and mypy (91 errors). SC12 now carries the parity rule for this (`spec.md:64`).

## Core Concept

The end state is a single path: **source tree → `install_assistants` → target.** The source tree holds `skills/`, `agents/`, `adapters/`, `hooks/` and `project_templates/`. The installer has one ownership rule: it replaces what it made and asks about everything else. It already recognizes the old installer's *copied* files by hash. This item teaches it to recognize the old installer's *links* by shape: a link at `.claude/<kind>/<name>` whose absolute target text ends in `claude/<kind>/<name>`, inside an agentic-mbse source checkout. The check lives inside `permit`, as one more answer to "did we make this?". Never writing through links, the prompts and the manifest are untouched.

The content is not hand-merged. A one-time script regenerates the shipped text from `main`'s files: it applies the fixed envelope and a short, reviewed list of literal runtime adaptations to bodies. A separate check, written independently of the generator's envelope code, compares a fresh install against `main`. "`main`'s text in the native shape" becomes something a script verifies, not a judgment call over 25 files. After the merge, `claude/` is gone, this repo's own stale `.claude/` copies are untracked, and the tree is the only copy. The script retires with this item's evidence.

**Why this is the right shape.** Both halves extend something that already exists instead of adding a parallel mechanism. Adoption is the link counterpart of the existing hash rule. Regeneration is the native branch's own envelope applied to new bodies. Most of the installer work is deletion: lists and `claude/` keys.

## Key Bets

- **B1. `main`'s bodies need only the adaptations in Appendix A to work under both runtimes.** The token scans support this. Tool names such as `Explore` and `WebSearch` that remain in shared text are mapped by the adapters, as the native design intended (native `plan.md:8`). *If false → an instruction points a Codex install at something it lacks. The SC7 property tests or the discovery probe flag it, and the list grows by a reviewed entry.*
- **B2. Claude Code and Codex both ignore an unrecognized `metadata` map in `SKILL.md` frontmatter.** It is the Agent Skills field reserved for custom properties, and OpenAI's own skill-creator uses `metadata:` in `SKILL.md`. The native spike proved tolerance of an unknown *top-level* key only (`.project/active/spike-native-skill-install/findings.md:28`). The probe sees Claude's user-invocable skills and all 25 in Codex. Every bundle carries the same field, so the visible ones stand in for the seven reference skills. *If false → bundles vanish from one client's catalog. The probe on a fresh install shows it, and the field falls back to a top-level `kind:` key (D6 is reversible).*
- **B3. Every link the old installer made is still recognizable when the owner re-inits.** It is absolute and `..`-free, has the mirrored `claude/<kind>/<name>` shape, and its checkout root still contains `src/agentic_mbse`. *If false → some links are not adopted and fall to prompt-or-preserve, leaving clutter. The rehearsal's adopted count (expected 31) shows it.*
- **B4. Only the two passages named in SC9 are target-owned text that a re-init would silently replace.** *If false → information is lost at re-init. The rehearsal diffs every file replaced without a prompt against its pre-init content to confirm it.*

## Key Decisions

These are agent-grade design decisions. They are fixed for the plan; each can be challenged by re-deriving against its recorded reason.

- **D1. Integrate by merging into a new branch.** In a fresh worktree on a new branch `nsd-integration` cut from `wrap-split`, run `git merge native-claude-codex-skills`.
  - **Why this way:** `wrap-split` is `main` plus the planning artifacts, so they arrive with the branch. The native branch stays at its audited `86921f9`. First-parent history reads as `main`'s.
  - *Rejected: rebase (replays every branch commit through rename and reflow conflicts, and rewrites the SHAs the native audit cites). Also rejected: merging `wrap-split` into the existing native worktree (moves the audited baseline and makes the native line first-parent).*
- **D2. Resolve the merge mechanically, then regenerate in its own commit.**
  - **Merge commit:** take the branch side for `skills/`, `agents/` and the templates, and keep `main`'s `claude/`.
  - **Next commit:** `reconcile.py write` rewrites `skills/**`, `agents/*.md` and the tool-owned templates from `main`'s files.
  - **Next commit:** `git mv` the hook and `git rm -r claude/`.
  - **What a reviewer then sees:** the PR diff against `main` shows each `claude/commands/<n>.md → skills/<n>/SKILL.md` as a rename that carries only the envelope and the adaptations. That diff is the human-readable SC2 evidence.
  - *Rejected: resolving 25+ rename/modify conflicts by hand (a judgment per file, and it invites reflow noise). Rejected: regenerating inside the merge commit (it mixes mechanical resolution with content and hides the renames).*
- **D3. The envelope is a text-level transform of the frontmatter, plus the preface.**
  - **Workflow frontmatter:** delete the `skills:` line, change `Task` to `Agent` on the `allowed-tools` line, and append `metadata:` / `kind: workflow`. Supporting skills get `kind: supporting`. The kind comes from `main`'s location (`claude/commands/` or `claude/skills/`).
  - **Preface:** the closing `---`, a blank line, the branch's preface paragraph, a blank line, then `main`'s body bytes unchanged. This matches the branch's `---\n\n<preface>\n\n` spacing.
  - **Ownership of the frontmatter:** the envelope alone governs it. Adaptations never touch it.
  - *Rejected: a YAML round-trip (it reformats folded descriptions, creating differences outside the envelope). Rejected: injecting the preface at install time (it breaks `--dev` links, and installed bytes would no longer equal source bytes).*
- **D4. The adaptation list is `adaptations.yaml` in this item's folder.**
  - **Fields:** `id`, `file`, `old`, `new`, `count`, `why` and `origin` (`branch` or `item1`). `old` and `new` are verbatim strings for every entry.
  - **Body-only scope:** adaptations apply only to the body below the frontmatter, and `count` is a body count.
  - **Why the scope matters:** A6's and A11's `old` (`AskUserQuestion`) also appears once in `allowed-tools`. There it must stay, because it is Claude's tool grant.
  - **Tooling:** `reconcile.py write` applies the list. `reconcile.py check` verifies the result independently (Architecture § One-time integration flow).
  - *Rejected: a markdown table (a machine cannot check it). Rejected: regex rules (harder to review, and they can over-match).*
- **D5. Legacy links are recognized by exact path shape plus an agentic-mbse checkout root, inside `permit`.**
  - **What qualifies:** absolute link text with no `.` or `..` segments, which is exactly what the old installer's `resolve()` wrote. The text is never normalized. See Architecture § Legacy adoption.
  - **Which checkouts count:** any agentic-mbse checkout, other clones and worktrees included. A link into another clone's `claude/` was made by that clone's `init --dev`, so it is installer-made in the same sense.
  - **How this reads the spec:** "points anywhere else, such as a personal fork" (`spec.md:46`) means a link outside every agentic-mbse checkout.
  - *Rejected: shape alone (any folder named `claude/` would qualify, such as a personal copy of a command). Rejected: a recorded list of checkout roots (a machine-specific list in source that misses other clones and worktrees). Rejected: normalizing relative or `..` text (the producer never wrote it, and textual normalization after a symlinked component can name a root the link does not point into).*
- **D6. The workflow/supporting split is `metadata.kind` in each bundle's frontmatter.** `install-commands --list` groups by it, and a property test requires it. The deletion guard is a skill-reference integrity test, which needs no edit when a skill is added. *Rejected: reusing `user-invocable` (it does not match the split). Rejected: a count floor (an inventory number that has to be bumped).*
- **D7. The hook moves to a top-level `hooks/` with `git mv`.** It keeps its `100755` mode and is still installed only for Claude. *Rejected: `adapters/claude/hooks/` (turns a folder of adapter files into a mixed tree for one script).*
- **D8. One predicate defines "a source checkout": `is_source_checkout(root)`.** It is true when `root/src/agentic_mbse` exists. Data-root detection, the `--dev` prerequisite and legacy adoption all use it. *Rejected: swapping the `claude/` marker for `skills/` (the wheel's data folder also has `skills/`, so `--dev` would wrongly pass on a wheel install).*
- **D9. Keep `retire_command`, and move the Claude step into a small named helper.**
  - **`retire_command` is unchanged.** It stays scoped to `.claude/commands/<name>.md`, and it needs no change for adoption because it already calls `permit` (native `installation.py:208`).
  - **The helper:** the alias step leaves the loop's boolean condition for `expose_to_claude`. It calls `retire_command`, then `alias`, or `copy_tree` in copy mode. It adds no removal surface.
  - *Rejected: a generic `Installer.remove(relative)` (it widens the set of paths that can reach adoption, which Invariant I2 relies on, and adds audit scope to reviewed A–K code for a style point).*
- **D10. Both target-owned passages go to fusion-tea's `AGENTS.md` (SC9).** The proposed change appends them verbatim. It does not touch `.agentic-mbse/codex.md` or `MODELING_GUIDE.md`: those must still match their manifest hash so the re-init replaces them with the reconciled text.
  - **Why `AGENTS.md`:** both passages exist for the Codex sandbox, which reads pattern docs from a copy inside the worktree.
  - **Effect on Claude:** Claude will follow the guide's `get_docs_dir()` resolver instead. After runbook step 1, that resolver points at the same-version docs.
  - **What the pattern-note ledger row records:**
    - After re-init, Codex reads two conflicting instructions. The shipped guide says to use the `get_docs_dir()` resolver; `AGENTS.md` says to use `.agentic-mbse/patterns/`.
    - That worktree copy equals `main`'s docs today, but no installer refreshes it any more.
    - The note's stated reason, "versioned separately from the pinned executable runtime", ends at runbook step 1.
    - The runbook offers the owner a choice: keep or drop the note after step 1, or copy it into `CLAUDE.md`. The choice is about fusion-tea's own text and does not block this item.
  - *Rejected: `CLAUDE.md` plus `AGENTS.md` (duplicate text). Rejected: `REQUIREMENTS.md` (it holds model requirements, not tool setup). Rejected: deleting the passages from the tool-owned files in the patch (their hash would stop matching, the re-init would prompt or skip, and the reconciled text would not land).*
- **D11. The SC11 audit is bounded to the installer, the reconcile tooling and the evidence.**
  - **In scope:**
    - The installer diffed against the fork `88e2489`, which covers A–K and this item together.
    - The A–K checklist and the adaptation list.
    - `reconcile.py`'s transform and check code, the `check` output, and the recorded negative self-check.
    - The rehearsal, the runbook and the patch.
  - **Out of scope:** body text beyond the list. SC2 makes that mechanical.
  - **Who runs it:** a fresh non-author agent, via the orchestrator's audit stage.
  - *Rejected: re-reading all 25 bodies. Rejected: a separate A–K review of a target that is still moving.*
- **D12. The rehearsal re-points the copy's legacy links at the integration worktree's `claude/` folder, which no longer exists.** This reproduces the post-merge dangling state. *Rejected: leaving links into `/home/reid/1cfe/agentic-mbse/claude/` (a write-through bug would edit what fusion-tea reads live, and the dangling case would never run).*
- **D13. This repo stops tracking its own install.**
  - **What is removed:** `git rm` the shipped-name entries under `.claude/`: the 9 commands; the `pdf-analysis` link and the `python-debugger`, `record-learning` and `toolkit-awareness` skill files; the 5 agents; and the hook.
  - **What stays:** `.claude/settings.json`. The untracked `settings.local.json` is untouched.
  - **Restoring the workflows:** after moving the checkout, the owner runs `uv run agentic-mbse install-commands --assistant claude --link-mode symlink` from the checkout root (runbook step for this repo). The command writes only the assistant install and no project scaffold.
  - **Why `--assistant claude`:** this repo's install today is Claude-only (`.claude/`, no `.codex/`). `claude` also writes no root `AGENTS.md`. A developer who wants Codex here can re-run it with `both` and add ignore lines for `.codex/` and `AGENTS.md`.
  - **Why `--link-mode symlink` (the default):** the Claude aliases are relative links into `.agents/skills/`, so the bundles are not stored twice and nothing machine-specific is written.
  - **Picking up source edits:** `install-commands` always copies (it has no `--dev`). A developer re-runs it after editing `skills/` to see the change in this repo.
  - **Keeping it untracked:** `.gitignore` lines cover exactly what that command writes: `.agents/skills/`, `.agentic-mbse/`, `.claude/skills/`, `.claude/agents/` and `.claude/hooks/`. `.claude/settings.json` stays tracked; `install-commands` never writes it.
  - *Rejected: keeping the copies tracked (a dangling, machine-specific link in every clone, and a stale second registration surface that Items 2, 4 and 5 will not reach). Rejected: removing only the dangling link (the 9 stale commands would still block their aliases on the next reinstall). Rejected: reinstalling with `scripts/replicate_setup.sh` (a full `init` also writes project scaffold, including a test file pytest collects).*
- **D14. Under `--dev`, each shared bundle is one folder link** (amendment after the audit, 2026-10-09; plan Phase 9). `.agents/skills/<n>` is an absolute link to the checkout's `skills/<n>`, instead of a real folder of per-file links. Claude's `.claude/skills/<n>` alias is unchanged: a relative link to `.agents/skills/<n>`.
  - **Why:** Codex 0.160.0 lists no skill whose `SKILL.md` is a file link, and lists every skill whose folder is a link. Claude Code lists both shapes (`evidence/spike-dev-codex-links.md`). With per-file links, `--dev` gave Codex none of the shipped skills (audit B1). [OWNER] 2026-10-09: the owner asked for the spike and then chose the fix over the deferral the orchestrator had made.
  - **How:** `Installer.alias` becomes `Installer.link_directory(relative, link)`, with the caller passing the link text. The Claude alias and the `--dev` folder share its ownership rule: a real folder is replaced only when every entry in it is installer-owned. A real folder holding an owner file or an edit gets a plain copy of that bundle instead, and `init` prints one line saying so. The link text is absolute, like `--dev`'s template and hook links.
  - *Rejected: linking `.agents/skills/<n>` through `.claude/skills/<n>` (Claude's alias already points at `.agents/`, so the chain adds a hop; both shapes were proven). Rejected: falling back to per-file links (Codex skips them). Rejected: linking over a folder that holds owner files (it deletes them).*

## Architecture

### End state: one source, one path

```
skills/<n>/SKILL.md (+ references/, scripts/)  ─┐
agents/<n>.md   adapters/{claude,codex}.md      ├─ install_assistants ─┬─ .agents/skills/<n>/   (canonical, both runtimes)
hooks/<h>       project_templates/*.template   ─┘   (Installer: permit) ├─ .claude/skills/<n> → alias, .claude/agents/, .claude/hooks/
                                                                        └─ .codex/agents/*.toml + config.toml, .agentic-mbse/<rt>.md
```

- **`init` and `install-commands` both call `install_assistants`.** `init` also writes the project scaffold; `install-commands` writes only the assistant install.
- **`scripts/replicate_setup.sh` stays the branch's six-line wrapper around `init`.** Its stated purpose is installing the product into this checkout with the target-repo ownership policy.
- **This repo's developers get the workflows from `install-commands --assistant claude` (D13).** That install is untracked.
- **The data root comes from `_get_data_root()`.** It is the source checkout when `is_source_checkout` holds, otherwise `site-packages/agentic_mbse_data/`. The wheel force-includes `skills`, `agents`, `adapters`, `hooks`, `docs`, `project_templates` and `SOURCE_INDEX.md.template`.
- **The inventory is the tree.** `skill_bundles()` globs `skills/*/SKILL.md`, agents glob `agents/*.md`, and hooks glob `hooks/*`. `bundle_kind()` reads `metadata.kind` for `--list`.
- **The Claude step for each bundle:** `expose_to_claude` calls `retire_command`, then `alias` (D9).

### Legacy adoption (code-level behaviour)

The rule is one predicate, consulted in `permit` after the manifest check:

```
legacy_link_target(relative) -> str | None:
  require relative == ".claude/<kind>/<name>" with kind in {commands, skills, agents, hooks}
  require (target / relative) is a symlink                    # never stat the referent
  text = os.readlink(target / relative)                       # raw text, never normalized
  require text starts with "/" and every "/"-segment after it is non-empty and not "." or ".."
  require text's last three segments == ["claude", kind, name]
  require is_source_checkout(text minus those three segments) # the checkout root
  return text
permit: ... fingerprint matches → True; elif legacy_link_target → record adopted, True; else ask/skip/force
```

**Why each part of SC8's boundary holds:**

- **Shipped name.** `permit` and `retire_command` are only reached for entries the installer is about to install or retire, and those are all derived from the source tree (Invariant I2). The owner's `manage-concept.md`, `research-acquire.md`, unshipped skills and the five `.agents/skills/` owner links therefore never reach it.
- **Old location and link-only.** These are checked directly in the predicate.
- **Points into an agentic-mbse `claude/` folder.** The exact-shape check and the checkout-root check cover it. After the merge, the root still exists (`/home/reid/1cfe/agentic-mbse` with `src/agentic_mbse`); only `claude/` has gone.
- **No more than the producer wrote.** Only absolute, `..`-free text qualifies. A relative or `..`-bearing link falls to prompt-or-preserve.

**Where adoption happens for each kind of entry:**

- **Commands:** `expose_to_claude` calls `retire_command(n)`, which calls `permit(".claude/commands/<n>.md")`. The link is adopted, unlinked and dropped from the manifest, and the alias follows.
- **Skills:** `alias` calls `permit` on `.claude/skills/<n>`. The link is adopted, unlinked, and replaced by a relative alias. In copy mode, `copy_tree` does the same.
- **Agents and the hook:** `write` calls `permit`, then unlinks and writes the rendered agent or the hook.

**The report.** A new action bucket, `adopted`, holds `"<relative> (was -> <old target>)"`. `cmd_init` prints it under "Adopted (N) — links from the pre-native installer replaced", and `install-commands` reports it too. For fusion-tea the expected count is 31.

### One-time integration flow

```
commit 1  merge native-claude-codex-skills: branch side for skills/, agents/, templates; main's claude/ kept
commit 2  reconcile.py write --main 8f43a09   (main's claude/** text + 3 templates → skills/, agents/, templates)
commit 3  git mv claude/hooks/ruff-format.sh hooks/; git rm -r claude/; git rm this repo's shipped-name .claude/ copies; .gitignore lines
commit 4+ installer changes, tests, adapters, docs, evidence
check     uv run agentic-mbse init <tmp> --assistant both  →  reconcile.py check --main 8f43a09 <tmp>
```

**The path rule:**

- `claude/commands/<n>.md` → `skills/<n>/SKILL.md` (workflow).
- `claude/skills/<n>/**` → `skills/<n>/**` (supporting).
- `claude/agents/<n>.md` → `agents/<n>.md`.
- Templates and `docs/patterns/` keep their paths.
- The hook is moved with `git mv`, not regenerated.

**How `check` compares.** It shares no envelope code with `write`.

- **Frontmatter, as parsed data.** For each installed `SKILL.md`, parse the frontmatter as YAML. It must equal `main`'s parsed frontmatter with `skills` removed, `Task` replaced by `Agent` in `allowed-tools`, and `metadata: {kind: …}` added.
- **Preface and body, as exact bytes.** The bytes after the frontmatter must be exactly a blank line, the preface, a blank line, then `main`'s body with the adaptation list applied. Each entry must apply to the body exactly `count` times.
- **Other files.** Non-`SKILL.md` bundle files and the templates must equal `main`'s bytes plus their adaptations, compared against the fresh install. Agents, the hook and the pattern docs are compared against the source tree, because agents are rendered at install and pattern docs are packaged rather than installed.
- **Modes.** Every compared file's executable bit must match `main`'s git mode.
- **File sets.** The expected and actual sets must match, with no extra or missing files.
- **Moving `main`.** `--main <rev>` lets both commands re-run if `main` moves.
- **Negative self-check.** A run is recorded showing that one mutated byte, one count off by one, and one extra file each make `check` exit non-zero.

## Required Invariants

- **I1.** The installer never writes through a symlink. Adoption only unlinks the link itself.
- **I2.** `permit` and `retire_command` are reached only for entries derived from the source tree. This is what makes "the installer ships its name" true by construction. No generic removal API is added.
- **I3.** Recognition never reads the referent. It uses the raw `os.readlink` text, which must be absolute and free of `.` and `..`, plus the checkout root's `src/agentic_mbse`.
- **I4.** No list in `src/` or `tests/` names a skill, agent or hook. Tests derive the inventory from the tree.
- **I5.** No `claude/` folder exists in the source tree, the sdist or the wheel.
- **I6.** `get_docs_dir()` stays importable from `agentic_mbse.cli` and resolves for source and wheel installs. The guide's resolver text depends on it.
- **I7.** Every `SKILL.md` carries `name` equal to its folder, a `description`, a `metadata.kind` of `workflow` or `supporting`, no `skills:` key, and the shared preface as its first paragraph.
- **I8.** The proposed fusion-tea change edits only fusion-tea-owned files.
- **I9.** This repo tracks no shipped-name entry under `.claude/`. `git ls-files .claude` lists only `settings.json`.

## Component Overview

**Removed**

- `claude/` entirely. Its last file, `claude/hooks/ruff-format.sh`, moves to `hooks/`.
- This repo's tracked shipped-name `.claude/` copies (D13).
- `MBSE_COMMANDS` and `MBSE_SKILLS` (`cli/__init__.py:18-48`), with their test imports and assertions.
- The `claude` keys in `_get_data_root`, `_check_dev_mode_prerequisites` and `pyproject.toml`.
- The literal skill lists and counts in `test_cli.py` and `test_installation.py`.

**Changed**

- **`installation.py`:**
  - `permit` gains adoption.
  - New `is_source_checkout`, `legacy_link_target`, `expose_to_claude` and `bundle_kind`.
  - `install_assistants` reads `hooks/` and calls `expose_to_claude`. `retire_command` is unchanged.
- **`cli/__init__.py`:**
  - The data root and the `--dev` check use `is_source_checkout`.
  - `get_hooks_dir` points at `hooks/`.
  - `--list` groups by kind.
  - Both commands print the adopted entries.
- **`pyproject.toml`:** `hooks` replaces `claude` in the wheel force-include and the sdist include.
- **`.gitignore`:** new lines for this repo's dev install (D13).
- **`adapters/claude.md:7` and `adapters/codex.md:7`:** the "fresh stages require new agents" sentence becomes fusion-tea `codex.md:7`'s rule. Keep a continuing author while its context is useful; independent review needs a fresh non-author agent (SC3).
- **25 `SKILL.md`, 5 agents and 3 templates:** regenerated from `main` (D2–D4).
- **`tests/test_modeling_command_contracts.py`:** take `main`'s version, change paths from `claude/commands/<n>.md` to `skills/<n>/SKILL.md`, and change `Task` to `Agent` at `:72`.
- **`CLAUDE.md`:** Architecture, Change Coordination and Init File Ownership describe the one installer, the `kind` field, `hooks/`, legacy adoption and both install commands for this repo (SC12). `scripts/replicate_setup.sh` is the `init` wrapper for its stated purpose. `install-commands --assistant claude` is what a developer runs to get the workflows in this repo. README's installer paragraph changes to match.

**Added (evidence, not shipped), in `.project/active/native-skill-distribution/`**

- `reconcile.py` and `adaptations.yaml`, plus the recorded negative self-check.
- `dispositions.md` (SC1; the bundle, template and agent rows are emitted by `check`).
- `rehearsal.md` (SC8, SC10, including the scratch-clone `install-commands` run) and `fusion-tea-runbook.md` (SC10, including this repo's step).
- `fusion-tea-target-owned.patch` (SC9).
- The Item 1 section of `.project/active/wrap-split-migration-ledger.md`. This item creates the file.

Appendix B maps each change to a file.

## Non-Goals

- **The post-merge install mode.** That choice is parked for the owner. Both modes are made to work, and the rehearsal reports both.
- **Pattern-doc installation.** The guide takes `main`'s `get_docs_dir()` resolver text.
- **fusion-tea's local same-name skills.** When Items 2 and 5 ship `run-goal`, `narrate-goal` or `research-acquire`, fusion-tea's local copies will meet prompt-or-preserve. The epic's integration step handles them.
- **Clearing `main`'s pre-existing ruff and mypy debt.** SC12's parity rule governs (`spec.md:64`).
- **Editing tool names that the adapters already map** (`Explore`, `WebSearch`, `Glob` in shared prose).
- **Out of scope: tidying `--dev`'s `.gitignore` list.** It still names `.claude/commands/` and `.claude/.tool-hashes.json`, which the installer no longer writes. This is a follow-up, because it changes nothing for fusion-tea (R5) and touches two tests.
- **Adopting old template links.** `main`'s `init --dev` also symlinked the four tool-owned templates into `project_templates/` (`cf23443`). SC8 does not cover those links, so such a target sees a prompt for them under plain `init`. fusion-tea's are real files. This is a known limit.
- **Out of scope: tidying this repo's own tracked init scaffold** (`modeling_project/`, `work/`, `knowledge/`, `data/`), including the stale tool-owned template copies (R7). This is a follow-up for dev-repo hygiene, because it is an older condition unrelated to skill registration (orchestrator, 2026-10-09).

## Implementation Notes

- **Worktree setup is the orchestrator's job, from `/home/reid/1cfe/agentic-mbse`, with no branch switch:**
  1. `git worktree add -b nsd-integration /home/reid/1cfe/agentic-mbse-nsd-integration wrap-split`, after the plan is committed on `wrap-split`. Later planning commits come in with `git merge wrap-split`.
  2. Copy the gitignored `.env` (it holds `SYSIDE_LICENSE_KEY`), then run `uv sync`.
  3. Stage a copy of fusion-tea's working tree with `rsync -a --exclude .venv` into the worktree's gitignored `.orchestrate-logs/rehearsal/`. It has to be a filesystem copy, not a clone: the legacy links are gitignored and would be lost in a clone.
- **Commit structure (S1):** follow the four commits in Architecture § One-time integration flow.
  - **Merge commit, resolved mechanically:**
    - Branch side for `skills/`, `agents/`, the templates, installer code, `pyproject.toml`, `scripts/`, `README.md` and `CLAUDE.md`. `main` did not change the last five.
    - `main`'s side for `claude/**`, which also settles `orchestrate-modeling`'s modify/delete conflict.
    - `wrap-split`'s side for `.project/CURRENT_WORK.md`.
    - For the spike and research files both sides added, keep `main`'s copy if they differ, and record that in `dispositions.md`.
  - **No reflow anywhere,** so git's rename detection keeps the regenerated files paired with their `claude/` originals.
- **Envelope details:**
  - The preface constant is the branch's text verbatim, including the typographic apostrophe.
  - Write `---\n\n<preface>\n\n`, then `main`'s body bytes unchanged.
  - Write `kind` as the last frontmatter key.
- **Adaptation entries:**
  - Copy each `new` string verbatim from the branch (word diffs in `.orchestrate-logs/nsd-design-scratch/wdiff.py`). Apply them to the body only.
  - A1 is the onboard `OVERVIEW.md` change, which the spec reviewer called a content change. It stays in the list as an adaptation, because the installer's entry files point to `OVERVIEW.md` (native `installation.py:328`), making it the one context file both runtimes read. Flag A1 for the one-time review.
- **Predicate gotcha:** `pathlib` silently drops `.` segments (`Path("/a/./b").parts` has no `.`). Check the raw `os.readlink` string, split on `/`, not `Path(text).parts`.
- **File modes:**
  - The hook is moved with `git mv`. `write` overwrites existing files in place, so `extract_page.py` keeps `100755`.
  - `check` compares modes.
  - The extracted-wheel test must not assert the executable bit after `zipfile.extractall`, which drops modes. Either extract preserving modes, or assert the bit only on the in-process `init`.
- **Skill-reference integrity test (S4):** a backticked reference counts only when its whole content matches `^/[a-z0-9-]+$`. That excludes path-like hits such as `` `/tmp/...` `` in `pdf-analysis` and `extraction-details.md`, the only non-skill matches in `main`'s shipped text.
- **Test fixture updates:**
  - `test_bundle_retirement_prunes_only_unchanged_resources` builds a fake data root that symlinks `claude`. It now creates `src/agentic_mbse/` and symlinks `hooks` instead.
  - Legacy-adoption fixtures build a fake checkout root (`<tmp>/old/src/agentic_mbse/`). They create absolute links with and without `<tmp>/old/claude/`, plus relative and `..`-bearing links as negative cases.
- **Ordering inside `permit`:** adoption sits after the manifest/desired check and before `force`/`decide`, so `--force` is never needed.
- **The scratch-clone check for this repo (D13):**
  1. Clone the integration branch into `.orchestrate-logs/rehearsal/` and run `uv run pytest tests/` there as the baseline.
  2. In the clone, run `uv run agentic-mbse install-commands --assistant claude --link-mode symlink`.
  3. Confirm `git status` is clean apart from the intended untracking, which is already committed on the branch. Any other untracked path means the ignore lines are wrong.
  4. Confirm every bundle resolves under `.claude/skills/<n>/SKILL.md`, and the agents and hook are present.
  5. Confirm `uv run pytest tests/` gives the same result as the baseline.

## Potential Risks

- **R1. A client rejects `metadata`** (B2). Run the native discovery probe (native `.project/active/native-skills/discovery_probe.py`, which needs no model turns) on a fresh install right after commit 2, before the installer work. If it fails, fall back to a top-level `kind:` key and re-run.
- **R2. `main` moves before the owner merges.** Merge `main` again and re-run `write` and `check` with `--main main`. The exact body counts make drift fail loudly.
- **R3. The rehearsal cannot do runbook step 1 for real**, because the merged SHA is not on GitHub yet. The rehearsal runs the worktree's CLI instead, and the wheel test proves the packaged bytes equal the source. The report notes one difference. Rendered agents and `.claude/settings.json` record the docs path of whichever CLI runs. That path is fusion-tea's `.venv` if the owner uses fusion-tea's own CLI.
- **R4. A link whose checkout was deleted is not adopted.** This fails safe: the link is prompted for or preserved. The runbook says to re-init before deleting or moving any old checkout.
- **R5. `--dev` in fusion-tea likely leaves its `.gitignore` unchanged.**
  - **Why:** fusion-tea's old dev block was written by `main`'s `init --dev`, whose first line is `# Tool-owned files (managed by agentic-mbse init --dev)` (`src/agentic_mbse/cli/__init__.py:92`). The native installer's idempotence check keys on that same line (native `cli/__init__.py:78`, `:336-338`). So `--dev` very likely appends nothing.
  - **What the owner would see instead:** tracked Codex files turning into absolute symlinks.
  - **Confirmation:** the rehearsal reports both. The mode decision stays the owner's.
- **R6. The broken Claude window.** Plain `init` from fusion-tea's own environment (after step 1) works before `/home/reid/1cfe/agentic-mbse` moves, because adoption does not need the targets to exist. The runbook orders it first, which removes the window. `--dev` must run from the moved canonical checkout, so its window is the minutes between `git pull` and `init`.
- **R7. This repo's tracked tool-owned template copies stay stale.**
  - **What they are:** `modeling_project/MODELING_GUIDE.md`, `modeling_project/MODELING_PROCESS.md`, `work/EPIC_GUIDE.md` and `work/backlog/epic_template.md` are tracked, and three of them already differ from `project_templates/`.
  - **Why they stay stale:** no manifest covers them. The assistant-only reinstall (D13) never touches them, and a full `init` would prompt for them or, non-interactively, preserve them.
  - **Why this item leaves them:** they belong to this repo's tracked init scaffold, an older condition unrelated to skill registration (orchestrator, 2026-10-09). This item keeps them tracked and untouched, records them as a known stale copy in `dispositions.md`, and names the cleanup as a follow-up in Non-Goals.

## Integration Strategy

- **What this replaces:** `main`'s `claude/` + `MBSE_*` installer, the branch's leftover lists, and this repo's tracked copies of its own install.
- **What it builds on:** the native installer, its manifest and its tests.
- **What comes next:** Items 2 and 5 register skills by adding `skills/<n>/` with `metadata.kind`. Item 4 edits `skills/` text directly. The epic's integration step later removes fusion-tea's local skills.
- **What fusion-tea receives:** the patch, the ledger rows and the runbook. The owner applies all three.
- **What this repo's developers do:** after pulling the merge, run `uv run agentic-mbse install-commands --assistant claude` (runbook step for this repo). Re-run it after editing `skills/` to see the change locally.
- **The PR carries more than this item.** The integration branch is cut from `wrap-split`, so it also carries `wrap-split`'s planning commits for other items (`research-seam-port`, the epic). The owner's PR description must say so.

## Validation Approach

| SC | Evidence | Kind |
|---|---|---|
| SC1 | `dispositions.md`. `check` emits the bundle, template and agent rows. Hand rows cover: adapters, user-owned templates, installer, tests, the `.project/` conflicts, the 3 target-owned passages, this repo's `.claude/` copies (removed) and its tracked template copies (kept, known stale) | evidence |
| SC2 | `reconcile.py check --main 8f43a09` on a fresh `--assistant both` install exits 0. The negative self-check is recorded: one mutated byte, one count off by one and one extra file each exit non-zero. `adaptations.yaml` and the transform code are reviewed once in the audit | evidence |
| SC3 | Property test: neither adapter says every stage needs a new agent, and both carry the continuity and independent-review rule | pytest |
| SC4 | Covered by SC2: the guide equals `main` plus adaptation A17. A test asserts the installed guide contains no `.claude/settings.json` | pytest + evidence |
| SC5 | Behaviour test on a fake data root with no other edit. An extra `skills/new-skill/` (kind workflow) is installed for both runtimes and listed under workflows. An extra `agents/new-role.md` is rendered for both runtimes and registered in `.codex/config.toml`. Invariant I7 test | pytest |
| SC6 | Test that `claude/` is absent from the repo. `init` installs an executable hook. `init --dev` links the hook into `hooks/`. `--dev` is refused on a non-checkout data root. Wheel test (one build): every file under each force-included folder is byte-equal, there is no `claude/` member, and running `cmd_init` from the extracted wheel (subprocess, `PYTHONPATH`) installs all bundles, agents and the hook | pytest |
| SC7 | The existing claude/codex/both × symlink/copy matrix, with the inventory derived from the tree. Every file in every bundle is reachable through `.agents/skills/` and the Claude alias. Every backticked `` `/name` `` (S4 pattern) and every `.agents/skills/<n>/` path in installed text resolves. No installed skill, template or Codex role names `.claude/`. The discovery probe runs on the 3 fresh installs: Claude's catalog lists every bundle not marked `user-invocable: false` (18 today) plus the 5 roles; Codex lists all 25. The 7 reference skills are checked on disk at `.claude/skills/<n>/SKILL.md` | pytest + evidence |
| SC8 | Parametrized over commands, skills, agents and hooks, with the target existing or dangling: adopted, reported with the old target, referent unchanged. Negative cases keep prompt-or-preserve: unshipped name, non-checkout root, non-mirrored tail, relative text, `..` text, real file, real dir. A mixed legacy tree built from the source inventory. The rehearsal on the fusion-tea copy: Adopted (31); Claude probe shows the user-invocable skills (18) and 5 roles; Codex shows 25; the 7 reference skills on disk; hook present; fusion-tea's own entries hash-identical | pytest + evidence |
| SC9 | `fusion-tea-target-owned.patch` passes `git apply --check` on the copy at `403716ee3`. Ledger rows exist, including the pattern-note row's conflict and refresh facts (D10). After the rehearsal re-init, both passages are present in `AGENTS.md` | evidence |
| SC10 | `rehearsal.md` for each mode on its own copy: patch first, then a non-interactive `init`, then a second `init`. It reports `git status`, the `.gitignore` diff (R5 prediction), the files replaced with no prompt (each diffed for target-owned loss, B4), the preserve lines (each one a prompt in an interactive run), and the MR-7 paragraphs present in `MODELING_PROCESS.md`. It also covers the scratch-clone `install-commands --assistant claude` check: `git status` clean, workflows resolve, pytest unchanged. The runbook cites the observed results and includes this repo's step and the pattern-note choice | evidence |
| SC11 | Audit stage per D11. The native `audit.md` gains a dated verdict update | audit |
| SC12 | The merged branch carries `main`'s history (`git merge-base --is-ancestor main HEAD`). pytest passes. Ruff and mypy meet the parity rule (`spec.md:64`). `git ls-files .claude` lists only `settings.json`. CLAUDE.md describes the one installer, `replicate_setup.sh` and `install-commands`, and says which one a developer runs to get the workflows in this repo | evidence |

Product-lens falsifiers (`product-lens.md:35`): (a) is covered by SC5, (b) by SC2 and SC7, and (c) by SC8 and SC10.

## Next-Stage Handoff

**Fixed for the plan** (agent-grade design decisions; challengeable by re-deriving against their recorded reasons, not settled):

- D1–D14.
- The envelope definition and the body-only adaptation scope.
- The exact legacy predicate and where it sits in `permit`.
- `AGENTS.md` as the SC9 home.
- The evidence-folder location of the reconcile tooling.

**Open for the plan:**

- Exact helper signatures.
- `--list` output layout.
- Wording of the adopted report line.
- Final `adaptations.yaml` content. Start from Appendix A, and let `check` prove the counts.
- None for `.gitignore`: the lines are fixed by D13 and confirmed by the scratch-clone run.

**Open for the owner:**

- The install mode (parked).
- Whether fusion-tea keeps its pattern note after runbook step 1. This is fusion-tea's own text and does not block the item.

**Suggested phases:**

1. **Worktree, merge and content.** Commits 1–3. `check` passes and the negative self-check is recorded. Run the discovery probe to de-risk B2 first.
2. **Source-tree shape.** `is_source_checkout`, packaging, removing `MBSE_*`, `kind` and `--list`, and the derived tests.
3. **Legacy adoption.** The predicate in `permit`, `expose_to_claude`, the report, and the SC8 tests.
4. **Text.** Adapters (SC3), then CLAUDE.md and README.
5. **Evidence.** The wheel test, probes, the rehearsal in both modes, the scratch-clone check, the patch, the ledger, the runbook and the dispositions.

Then comes the independent audit stage.

---

## Appendix A — Starting adaptation list (applied to the body of `main`'s text)

These come from fork→branch word diffs. `main` equals the fork for every file below except `toolkit-awareness` and the guide template.

- **Body only.** Every entry applies to the body below the frontmatter, and every count is a body count.
- **A6 and A11:** `AskUserQuestion` also appears once in `allowed-tools`, which the envelope governs and which keeps it.
- **Verbatim in the YAML.** Cells shown here as a paraphrase (A4, A7) or a cross-reference (A9) carry verbatim strings in `adaptations.yaml`.

| ID | Source path | Change (old → new, verbatim from branch unless noted) | Body count |
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
| `claude/**` | Deleted in commit 3 (content regenerated elsewhere; hook moved) |
| `skills/<25>/**`, `agents/<5>.md` | Added by the merge (branch side), then regenerated by `reconcile.py write` in commit 2 |
| `hooks/ruff-format.sh` | `git mv` from `claude/hooks/` (bytes and mode `100755` equal to `main`) |
| `.claude/commands/*.md` (9), `.claude/skills/{pdf-analysis,python-debugger,record-learning,toolkit-awareness}` (incl. the absolute `pdf-analysis` link), `.claude/agents/*.md` (5), `.claude/hooks/ruff-format.sh` | `git rm` (D13) |
| `.claude/settings.json` | Kept tracked, unchanged |
| `.gitignore` | Lines for exactly what `install-commands --assistant claude` writes: `.agents/skills/`, `.agentic-mbse/`, `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` (D13) |
| `modeling_project/{MODELING_GUIDE,MODELING_PROCESS}.md`, `work/EPIC_GUIDE.md`, `work/backlog/epic_template.md` | Unchanged and still tracked; recorded as a known stale copy (R7); cleanup is a follow-up (Non-Goals) |
| `adapters/{claude,codex}.md` | Added by merge; line 7 edited (SC3) |
| `project_templates/MODELING_GUIDE.md.template`, `MODELING_PROCESS.md.template`, `EPIC_GUIDE.md.template` | `main` text + A17 (guide only) |
| `project_templates/{README,OVERVIEW}.md.template` | Branch side (user-owned; branch-only change) |
| `src/agentic_mbse/cli/installation.py` | Branch side + adoption in `permit`, `is_source_checkout`, `legacy_link_target`, `expose_to_claude`, `bundle_kind`, `hooks/`; `retire_command` kept |
| `src/agentic_mbse/cli/__init__.py` | Branch side − `MBSE_*` − `claude` keys; `--list` by kind; adopted report |
| `pyproject.toml` | Branch side; `claude` → `hooks` in wheel and sdist includes |
| `scripts/replicate_setup.sh` | Branch side (6-line `init` wrapper), unchanged |
| `tests/test_installation.py`, `tests/test_cli.py` | Branch side; lists and counts derived; SC5/SC6/SC7/SC8 tests added |
| `tests/test_packaged_guidance_contract.py` | Branch side; folder set from `pyproject.toml`; no `claude/` member; extracted-wheel init (no exec-bit assertion after `zipfile.extractall`) |
| `tests/test_modeling_command_contracts.py` | `main` side; paths re-pointed; `Task` → `Agent` |
| `CLAUDE.md`, `README.md` | Branch side; installer sections updated, including `replicate_setup.sh` vs `install-commands` for this repo (SC12) |
| `.project/active/native-skill-distribution/*` | Evidence files listed in Component Overview |
| `.project/active/wrap-split-migration-ledger.md` | Created with the Item 1 section |
| `.project/active/native-skills/audit.md` | Arrives by merge; dated verdict update from this item's audit |

---

Next Step: `/_my_plan`. No design re-review is needed unless these edits go beyond the review's Resolutions.

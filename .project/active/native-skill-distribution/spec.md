# Spec: Reconcile the native installer source with `main`

**Status:** Draft (revised after spec review)
**Owner:** Reid W
**Created:** 2026-10-04 09:28 PDT
**Updated:** 2026-10-09: revised to apply the spec review's Resolutions (`spec-review.md`, verdict Revise) and the Align decisions (`briefs/00-align.md`). Earlier versions: the 2026-10-09 rewrite at `b2d077b`, the 2026-10-04 original at `67c4d23`.
**Complexity:** HIGH
**Branch:** planning on `wrap-split`. Implementation on `native-claude-codex-skills` (worktree `/home/reid/1cfe/agentic-mbse-native-skills`). Integration happens in a worktree, never by switching branches in `/home/reid/1cfe/agentic-mbse` (see the `[HARD]` requirement).
**Backlog Item:** NATIVE-DISTRIBUTION-RECONCILIATION
**Epic:** `WRAP-SPLIT`, Item 1

---

## Problem

agentic-mbse has two installer sources, and neither is right on its own.

- **`main` has the right content in the old shape.** It holds the current workflow instructions: the September process rewrite, the workflow repairs, and PR #16's `/research` change (`8f43a09`). It installs them the old way, as `claude/` symlinks listed in `MBSE_*` constants in `src/agentic_mbse/cli/__init__.py`, for Claude Code only.
- **The native branch has the right shape with old content.** Branch `native-claude-codex-skills` (`86921f9`, with the A–K remediation now committed) holds the new installer: one `skills/` + `agents/` + `adapters/` tree installed for both Claude Code and Codex, bundle discovery, a hash manifest, and Codex role registration. It forked from `main` at `88e2489`; `main` is 58 commits ahead. Eleven workflow bodies are 30–110 lines behind `main`, and the process template is about 865 lines behind (audit § 4). It also still keeps the `MBSE_COMMANDS` and `MBSE_SKILLS` lists (native `cli/__init__.py:18-48`), which tests compare against `skills/*/SKILL.md` (native `tests/test_cli.py:289`, `tests/test_installation.py:35`). So adding a skill there still takes two edits.
- **fusion-tea runs both shapes at once.**
  - Its Codex side is a native install from a native wheel, with 13 payloads hand-updated to `main`'s bodies (fusion-tea `.project/active/harness-right-size/installed.json`). fusion-tea tracks this install in git.
  - Its Claude side is not a native install. 31 entries in `.claude/` (15 commands, 10 skills, 5 agents, 1 hook) are absolute symlinks into this checkout's `/home/reid/1cfe/agentic-mbse/claude/`, made 2026-03-02 by `main`'s `agentic-mbse init --dev` (added in `f92a62a`; `replicate_setup.sh` always copied) (`.orchestrate-logs/nsd-inputs/fusion-tea/runtime-entries.txt`). Claude Code in fusion-tea reads whatever branch this checkout has checked out.
  - The merge removes `claude/`. Once this checkout moves to that `main`, all 31 links dangle, and today's native installer treats them as owner files and leaves them in place.

This blocks the rest of the epic. Items 2 and 5 register new skills, and Item 4 edits shipped text. Doing that on `main`'s layout means doing it again on the native layout. Doing it on the branch first strands it behind the 58-commit gap. The owner asked for one way to install every workflow (first Known Requirement). This item delivers it: `main`'s content in the native shape, one place to register a skill, ready for the owner to merge, plus what fusion-tea needs to switch over without losing anything.

## Success Criteria

### Content: `main`'s text in the native shape

- [ ] **SC1. Every difference has a recorded disposition.** Each difference between the native branch's shipped files and `main`'s gets one of four dispositions: take `main` (portable content); keep the branch (envelope, runtime adaptation, or installer behaviour); merge (changed on both sides, so `main`'s content with the branch's runtime adaptation applied); or target-owned (stays in fusion-tea, with a row in `.project/active/wrap-split-migration-ledger.md`). The starting inventory, measured against `main` at `8f43a09`, is: 16 bundles `main` changed since the fork (11 workflows, 5 supporting skills); 3 tool-owned templates (`MODELING_PROCESS`, `MODELING_GUIDE`, `EPIC_GUIDE`); 2 pattern docs; and the branch-only changes (2 user-owned templates, 2 agents, the adapters). The table also lists each `main` test whose contract the envelope changes, such as `tests/test_modeling_command_contracts.py:72`, which expects `Task` where the envelope names `Agent`. Refresh the inventory if `main` moves before integration.
- [ ] **SC2. Shipped text equals `main` except for one reviewed list of allowed changes.** The check passes only when nothing outside that list differs. Applying it needs no per-file judgment beyond one review of the list. It compares the 25 bundles and the three changed tool-owned templates, as a fresh install writes them, plus the packaged pattern docs. The allowed changes are:
  - **Envelope:** frontmatter and the "Before executing this skill" preface. Nothing else. There is no paragraph reflow, so whitespace in a body matches `main`.
  - **Runtime adaptation:** a closed list of named body changes that make a file work under both Claude Code and Codex, such as `.agents/skills/<name>/scripts/` in place of `.claude/skills/<name>/scripts/`. The list is recorded once in the item's evidence and reviewed once. A difference not on the list fails the check. (The spec review measured about seven files that need adaptation, L3-1.)
- [ ] **SC3. Both adapters describe agent use the way `main`'s process does.** `adapters/claude.md` and `adapters/codex.md` say to keep a continuing author while its context is useful, and to use a fresh non-author agent for independent review. Neither says that every stage needs a new agent, as both do today (`adapters/claude.md:7`, `adapters/codex.md:7`).
- [ ] **SC4. The guide template tells a reader under either runtime how to find pattern docs.** `MODELING_GUIDE.md.template` carries `main`'s `get_docs_dir()` resolver text (`MODELING_GUIDE.md.template:276-282`), and its permissions sentence, which names `.claude/settings.json` (`:282`), reads correctly under Codex.

### Installer

- [ ] **SC5. A skill registers in one place.** Adding a workflow, supporting skill or expert role means adding its directory or file under the source tree, and nothing else. No list in source or tests has to change for `init`, `install-commands --list` and `uv run pytest tests/` to pick it up. Whether a bundle is a workflow or a supporting skill is recorded in the bundle itself. A guard against accidental deletion is allowed only if adding a skill never requires editing it.
- [ ] **SC6. No `claude/` folder remains in the source, and every install path still works.** The hook moves out of `claude/hooks/`. With `claude/` gone, each of these installs every asset, including the hook: plain `init`, `init --dev` from a source checkout, and an installed built wheel.
- [ ] **SC7. Fresh installs work under each runtime choice.** Fresh installs into a scratch target with `--assistant claude`, `codex` and `both` each discover every workflow and expert role, and reach every bundled supporting resource (scripts, reference docs). No instruction directs the agent to a path or tool the chosen install does not provide. Text that is explicitly conditional on the runtime is allowed, such as the preface's "read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex". `install-commands --list` names the bundles that are actually installed. Re-init preserves protected files and does not write through symlinks.
- [ ] **SC8. Installing over a legacy install adopts the old installer's symlinks, and nothing else.**
  - **What is adopted.** An entry qualifies when all of these hold: it sits where the old installer put it (`.claude/commands/<name>.md`, `.claude/skills/<name>`, `.claude/agents/<name>.md` or `.claude/hooks/<name>`); it is a symlink; the installer ships its name; and its target path lies under an agentic-mbse `claude/` folder. Recognition works when the target no longer exists, because after the merge every such link dangles.
  - **What "replaces" means.** The link itself is removed, and the installed skill alias, agent or hook takes its place. Nothing is written through the link. No `--force` and no prompt are needed.
  - **What is never adopted.** A symlink whose name the installer does not ship, such as fusion-tea's five `.agents/skills/` links into its own `.claude/skills/`. fusion-tea's own `manage-concept` and `research-acquire` commands. Real files and directories. A shipped-name link that points anywhere else, such as a personal fork. All of these keep today's prompt-or-preserve behaviour.
  - **What the owner sees.** The install report lists each adopted entry with its old target, so a deliberate link can be recreated.
  - **The evidence.** After installing over a copy of fusion-tea's tree, Claude Code discovers all 25 skills, the 5 agents and the hook, and fusion-tea's own skills and commands are byte-for-byte untouched.

### fusion-tea: switch over with no loss

- [ ] **SC9. fusion-tea's target-owned text has a home it owns before any re-init.** The installer cannot protect it. fusion-tea's edited `.agentic-mbse/codex.md` and `modeling_project/MODELING_GUIDE.md` match their manifest hashes, so a re-init replaces them with no prompt (native `installation.py:72-73`). Two passages are target-owned: the `.codex-test` worktree paragraph (fusion-tea `codex.md:11`) and the pattern-location note (fusion-tea `MODELING_GUIDE.md:276`). Each gets a ledger row and a proposed fusion-tea change that moves it into a file fusion-tea owns. The owner applies that change.
- [ ] **SC10. The owner has a post-merge runbook for fusion-tea, rehearsed on a copy of its tree.** The runbook covers, in order:
  1. **Move the pin.** Move fusion-tea's agentic-mbse pin to the merged SHA (hand-edit `uv.lock`, then `uv sync --frozen`), so installed text and the runtime it calls agree. PR #16's `/research` step is the live case: it relies on `--insights '[]'` behaviour that `c37ff53` lacks.
  2. **Land the fusion-tea change from SC9**, with its ledger rows.
  3. **Choose the install mode and run it.** The runbook presents plain `init` and `init --dev`, each with the effects the rehearsal observed, and the recommendation (see Open Questions). It gives the exact command and says which agentic-mbse installation runs it. `--dev` needs a source checkout (native `cli/__init__.py:275-279`), so fusion-tea's own installed CLI cannot run it.
  4. **Answer each prompt.** In particular, keep `modeling_project/MODELING_PROCESS.md`; do not back it up. That keeps its two MR-7 paragraphs (fusion-tea `MODELING_PROCESS.md:17`, `:34`) in force until Item 2 lands the general section.

  It also warns that fusion-tea's Claude side is broken between moving `/home/reid/1cfe/agentic-mbse` to the merged `main` and finishing step 3. For each mode, the rehearsal reports: `git status` on the copy, including tracked files that change or become symlinks; the `.gitignore` additions; the files replaced with no prompt; the prompts a real run would ask; and that `MODELING_PROCESS.md` was kept with both MR-7 paragraphs present. Of the 13 hand-updated payloads (fusion-tea `installed.json`), those that still match their manifest hash are replaced with no prompt, which is intended, because the reconciled text supersedes them. `MODELING_PROCESS.md` is the exception: the MR-7 paragraphs added after the hand-update make it differ from its manifest hash, so a re-init prompts for it, and step 4 keeps it. The other 12 are expected to match; only `MODELING_PROCESS.md` was checked, and the rehearsal's no-prompt list confirms the real set. User-owned files are preserved, and `init` does not modify fusion-tea's `pyproject.toml` or `uv.lock`; moving the pin is only ever the explicit step 1.

### Integration

- [ ] **SC11. An independent audit covers the installer as it now stands.** This item's own audit, run by an agent independent of the author, covers the A–K remediations together with this item's installer changes (legacy adoption, `claude/` removal, registration). The native audit's verdict (`audit.md:3`, "Needs Work") is updated from it.
- [ ] **SC12. An integration branch is ready for the owner to merge.** It carries `main`'s full history plus the native work, and `uv run pytest tests/` passes on it. Ruff and mypy follow the repo's parity rule (pre-PR brief `d693589`), because `main` already fails both (118 ruff findings, 78 unformatted files, 91 mypy errors): no findings beyond `main`'s baseline, and every file this item adds or edits is clean. CLAUDE.md's Architecture and Change Coordination sections describe the one installer that remains, including what `scripts/replicate_setup.sh` is.

## Known Requirements

- **[NEED]** (owner, 2026-10-09, verbatim at `briefs/00-align.md:19`) "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this". Read as an outcome: every workflow is a skill, installed the same way for both runtimes.
- **[INFERRED] (ratified by owner 2026-10-09; `briefs/00-align.md:21`)** The merge removes `claude/` with no transitional shim.
- **[INFERRED] (ratified by owner 2026-10-09; `briefs/00-align.md:22`)** The installer recognizes legacy symlinks that point into an agentic-mbse `claude/` folder as its own, and replaces them with the installed skills, agents and hook instead of preserving them as owner files. It is tested by installing over a copy of fusion-tea's tree. SC8 states the boundary.
- **[INFERRED] (ratified by owner 2026-10-09; `briefs/00-align.md:23`)** When Item 1 merges, the owner runs `agentic-mbse init --dev` once in fusion-tea. **The mode is reopened:** later evidence counts against `--dev`, so the choice is parked for the owner (Open Questions). The timing, at Item 1's merge, stands.
- **Owner permission, not a requirement** (owner, 2026-10-09, verbatim at `briefs/00-align.md:24`): "to be modle-agnostic, you can rename the folder hosting skills on the agentic-mbse side". Renaming or regrouping `skills/`, `agents/` or `adapters/` is allowed. Nothing requires it.
- **[INFERRED]** (follows from the ratified `claude/` removal) No Claude-named folder remains in the source tree. The last one on the branch is `claude/hooks/`.
- **[INFERRED] (proposed at Align, owner did not object; `briefs/00-align.md:28-31`)** Merging to `main`, pushing to GitHub, and any write to fusion-tea's real tree, including the post-merge re-init, are the owner's. The item reads fusion-tea and tests on copies only.
- **[HARD]** No integration work switches branches in `/home/reid/1cfe/agentic-mbse`. fusion-tea's Claude side reads that checkout's `claude/` folder live through its symlinks until the owner's post-merge step.
- **[INHERITED: `.project/CURRENT_WORK.md`]** "fusion-tea's pin is still at `c37ff53` (verified 2026-10-09): move it and re-run init to pick up the `/research` text." The runbook's first step does this (SC10).
- **[INFERRED]** (orchestrator for the owner, spec review Resolutions 2026-10-09; agent-grade, not settled) These choices shape the success criteria. "One place to register" means no hand-maintained list (L2-1). The guide template takes `main`'s resolver text, and no pattern installation is added (L1-2). The envelope is frontmatter and preface only, and runtime adaptation is a closed reviewed list (L3-1). SC8's five-part adoption boundary (L3-3). The A–K re-review folds into this item's audit (L2-2). The runbook keeps `MODELING_PROCESS.md` and reports each mode's effects (L3-4). Challenge one by re-deriving against its reasoning in `spec-review.md`.
- **[NEED]** (owner, the two `[OWNER]` criteria at `.project/backlog/epic_wrap-split.md:65-66`; their wording there governs) No loss of information for fusion-tea, and fusion-tea's MR-7 enforcement intact after re-init. This item writes its rows to `.project/active/wrap-split-migration-ledger.md`. Item 2 owns that file; if this item needs a row first, it creates the file.
- **[NEED]** (owner, epic header "Owner decisions carried in", 2026-10-06) The goal layer (`run-goal`, `narrate-goal`) and the research seam ship from agentic-mbse; the study layer ships from sysml-codegen. Only fusion-specific procedures stay owned by fusion-tea. This replaces the 2026-10-04 inference that goal and study procedures stay target-owned.
- **[INHERITED: `../harness-right-size/requirements.md`, owner `[NEED]`s]** The main agent keeps skills and delegates scoped work to preserve its context. Every stage can be brief or skipped when its job is already done. Review effort follows risk, and complex changes still get substantial independent review. `main`'s process template carries these (`MODELING_PROCESS.md.template:98`, `claude/commands/orchestrate-modeling.md:25`). Where the native plan's `[INFERRED]` "preserve fresh stage/audit contexts" conflicts with them, they govern.
- **[INHERITED: native `plan.md`, `remediation.md`, `audit.md`]** The native installer's behaviour contract keeps its grades. It ships 15 workflows and 10 supporting bundles from `skills/`, installed canonically under `.agents/skills/` with Claude aliases. It tracks managed files in a neutral manifest, imports legacy hashes, preserves owner additions, and never writes through destination symlinks. The plan's `[AGENT]` choices (`plan.md:10`: workflow names including `status`, unchanged extraction providers) hold unless evidence warrants a change; a challenge re-derives against `plan.md`'s reasoning. The owner's ask (first Known Requirement) now backs the skills-for-both-runtimes shape.
- **[INHERITED: CLAUDE.md "Change Coordination"; epic-F2]** `cmd_init` and `scripts/replicate_setup.sh` must not drift apart. On the branch the script is already a 6-line wrapper around `init` (native `CLAUDE.md:212`); on `main` it is a full script that creates directories itself.
- **[INFERRED]** `main`'s content is the reconciliation target, not fusion-tea's installed copy. fusion-tea is pinned at `c37ff53` and predates PR #16. Its installed copy is evidence of two things: what is portable (the author-continuity sentence at fusion-tea `.agentic-mbse/codex.md:7`) and what is target-owned (the MR-7 paragraphs, the `.codex-test` worktree paragraph at `codex.md:11`, the pattern-location note at `modeling_project/MODELING_GUIDE.md:276`).

## Non-Goals

- A second native migration, new workflow names, new runtimes, runtime upgrades, token-savings measurement, or fusion-tea's full study suite.
- Registering `run-goal` or `narrate-goal` (Item 2), `research-acquire` (Item 5), or anything study-related (Item 3). Removing consumer-specific text from shipped files (Item 4).
- Pattern-doc installation into targets. Not needed because `main`'s resolver text already locates the packaged pattern docs for source and packaged installs.
- The rest of fusion-tea's integration. Only the Claude-side switch moves to Item 1's merge. Removing fusion-tea's local skills and their gitignore whitelist lines, and the sysml-codegen install, stay with the epic's integration step after Items 1–5.

## Open Questions / Deferred to design

- **For the owner, not design: which install mode the post-merge step uses.** Ratified decision 3 says `init --dev`. Evidence found after Align counts against it (spec review Resolutions, verified by the orchestrator 2026-10-09):
  - fusion-tea tracks its Codex install in git (`.agents/skills/*/SKILL.md`, `.agentic-mbse/{codex.md,install.json}`, `.agentic-mbse/patterns/*`). `--dev` would replace those tracked files with absolute symlinks into `/home/reid/1cfe/agentic-mbse/skills/`, which are machine-specific and visible in git.
  - `--dev` keeps live editing for skills and templates only. Agents and adapters are copied (native `installation.py:321`, `:335`).
  - `--dev` appends entries to fusion-tea's `.gitignore`, which already carries an old dev-mode block with whitelist lines for its own commands and skills (fusion-tea `.gitignore:17-33`).
  - Plain `init` keeps both runtimes on installed copies; the Claude aliases are symlinks into `.agents/skills/` (native `installation.py:310-318`). Picking up later text changes takes another re-init.
  - **Recommendation (orchestrator, agent-grade): plain `init`.** fusion-tea commits its Codex install, and its adapter states "These instruction assets are separate from the pinned runtime" (`codex.md:11`). The rehearsal (SC10) reports both modes' effects so the owner decides on observed results. Design does not depend on the answer: SC6 requires `--dev` to work either way.
- How to bring the branch onto `main` (rebase, or merge with `main`'s bodies taken file by file), in a worktree. And how to apply the envelope to `main`'s bodies without hand-editing 25 files.
- How the SC2 check is built, and where the runtime-adaptation list lives in the evidence.
- How the installer recognizes a link "under an agentic-mbse `claude/` folder" once that folder is gone: path shape plus shipped name, or a recorded list of known checkout roots.
- Which field in a bundle records workflow vs supporting skill, and whether a deletion guard exists at all.
- Which fusion-tea-owned file receives each target-owned passage (SC9). fusion-tea's `AGENTS.md`, which the installer never overwrites (native `installation.py:325`), is one candidate.
- How the SC11 audit is bounded, and who runs it.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_wrap-split.md` § Item 1
- **Required Reading:** `/home/reid/1cfe/agentic-mbse-native-skills/.project/active/native-skills/{plan,remediation,audit}.md`; fusion-tea `.project/active/harness-right-size/{report.md,installed.json}`; `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 4
- **Align record:** `.project/active/native-skill-distribution/briefs/00-align.md`
- **Spec review:** `.project/active/native-skill-distribution/spec-review.md` (Revise; Resolutions applied in this revision)
- **Staged read-only inputs:** `.orchestrate-logs/nsd-inputs/` (native branch at `86921f9`, fusion-tea files at `403716ee3`; see `SNAPSHOT.txt`)
- **Process requirements:** `.project/active/harness-right-size/requirements.md`
- **Migration ledger:** `.project/active/wrap-split-migration-ledger.md` (Item 2 owns it; this item creates it if it needs a row first)
- **Evidence (2026-10-04):** `.project/reports/2026-10-04-0901-status-report.md` § "What is actually broken or missing", item 4
- **Product-lens:** `.project/active/native-skill-distribution/product-lens.md` (latest verdict 2026-10-09: CLEAR, after spec-F3 to spec-F5 were fixed)
- **Design:** `.project/active/native-skill-distribution/design.md` (to be created)

---

**Next Steps:** `/_my_design`. The install-mode question is parked for the owner and does not block design.

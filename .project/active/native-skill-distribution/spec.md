# Spec: Reconcile the native installer source with `main`

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-04 09:28 PDT
**Updated:** 2026-10-09: rewritten to the scope of `WRAP-SPLIT` Item 1; the 2026-10-04 version is in git history (`67c4d23`)
**Complexity:** MEDIUM
**Branch:** planning on `wrap-split`; the work happens on `native-claude-codex-skills` (worktree `/home/reid/1cfe/agentic-mbse-native-skills`)
**Backlog Item:** NATIVE-DISTRIBUTION-RECONCILIATION
**Epic:** `WRAP-SPLIT`, Item 1

---

## Problem

agentic-mbse has two installer sources, and neither is right on its own.

- **`main` has the right content in the old shape.** It holds the current workflow instructions: the September process rewrite, the workflow repairs, and PR #16's `/research` change (`8f43a09`). It installs them the old way, as `claude/` symlinks listed in `MBSE_*` constants in `src/agentic_mbse/cli/__init__.py`, for Claude Code only.
- **The native branch has the right shape with old content.** Branch `native-claude-codex-skills` (`955295b`, plus uncommitted A–K remediation in 8 modified and 4 untracked files) holds the new installer: one `skills/` + `agents/` + `adapters/` tree installed for both Claude Code and Codex, bundle discovery, a hash manifest, and Codex role registration. It forked from `main` at `88e2489`; `main` is 58 commits ahead. Eleven workflow bodies are 30–110 lines behind `main`, and the process template is about 865 lines behind (audit § 4).
- **fusion-tea runs `main`'s content in the native shape, by hand.** It installed from a native wheel, then had 13 payloads hand-updated to `main`'s bodies (fusion-tea `.project/active/harness-right-size/installed.json`). Re-installing from the native branch today would put the older procedures back.

This blocks the rest of the epic. Items 2 and 5 register new skills, and Item 4 edits shipped text. Doing that on `main`'s layout means doing it again on the native layout. Doing it on the branch first strands it behind the 58-commit gap. This item makes one installer source: `main`'s content in the native shape, merged to `main`.

## Success Criteria

- [ ] Every difference between the native branch's shipped files and `main`'s has a recorded disposition: take `main` (portable content); keep the branch (envelope, runtime adaptation, or installer behaviour); merge (changed on both sides, so `main`'s content with the branch's runtime adaptation applied); or target-owned (stays in fusion-tea, with a row in `.project/active/wrap-split-migration-ledger.md`). The sixteen differences observed on 2026-10-04 are the starting inventory, refreshed against `main` at reconciliation time, which now includes PR #16.
- [ ] After a fresh install from the reconciled source, the 15 workflow bodies, the 10 supporting skills and the process template equal `main`'s content apart from the envelope and runtime adaptation. The envelope is frontmatter, the "Before executing this skill" preface and paragraph reflow. Runtime adaptation is the branch's rewrites that make a body work under both runtimes: the host's question interface for `AskUserQuestion`, a subagent for `Task`, `.agents/skills/<name>/scripts/` paths, "`CLAUDE.md` or `AGENTS.md`". The branch made these in 10 of the 25 bundles, and five of those are unchanged on `main` since the fork (`pdf-analysis`, `python-debugger`, `record-learning`, `onboard`, `manage-sources`). A diff script in the item's evidence shows the result.
- [ ] Both adapters (`adapters/claude.md`, `adapters/codex.md`) agree with `main`'s process on agent use: keep a continuing author while its context is useful, and use a fresh non-author agent for independent review. Neither says that every stage needs a new agent, as both do today (`adapters/claude.md:7`, `adapters/codex.md:7`).
- [ ] `MODELING_GUIDE.md.template` tells a reader where pattern files are under either install: the copy installed in `.agentic-mbse/patterns/`, or the package's `docs/patterns/` (the only location it names today, `MODELING_GUIDE.md.template:279`).
- [ ] Fresh installs into a scratch target with `--assistant claude`, `codex` and `both` each discover every workflow and expert role, and reach every bundled supporting resource (scripts, reference docs). No installed text names a path or tool that the chosen install does not provide. `install-commands --list` names the bundles that are actually installed. Re-init preserves protected files and does not write through symlinks.
- [ ] Installing over a copy of fusion-tea's current tree preserves its user-owned files and runtime pin. Any tool-owned file fusion-tea has edited (the two MR-7 paragraphs in `MODELING_PROCESS.md`, the adapter's worktree paragraph) is kept or backed up under the installer's ownership rules, not silently overwritten. The install report says which files it would replace.
- [ ] The A–K remediations have an independent re-review bounded to installer behaviour, and the native audit's verdict (`audit.md:3`, "Needs Work") is updated from it.
- [ ] The branch is merged to `main`, and `uv run pytest tests/`, ruff and mypy pass there. CLAUDE.md's Architecture and Change Coordination sections describe the one installer that remains, including what `scripts/replicate_setup.sh` is.

## Known Requirements

- **[INHERITED: epic header, owner 2026-10-06]** No loss of information for fusion-tea: anything removed from shipped text because it is consumer-specific is migrated into fusion-tea's own files and recorded in `.project/active/wrap-split-migration-ledger.md`. Item 2 owns that file; if this item needs a row first, it creates the file. And fusion-tea's MR-7 enforcement stays intact after re-init.
- **[INHERITED: epic header, owner 2026-10-06]** The goal layer (`run-goal`, `narrate-goal`) and the research seam ship from agentic-mbse; the study layer ships from sysml-codegen. Only fusion-specific procedures stay owned by fusion-tea. This replaces the 2026-10-04 inference that goal and study procedures stay target-owned.
- **[INHERITED: `../harness-right-size/requirements.md`, owner `[NEED]`s]** The main agent keeps skills and delegates scoped work to preserve its context. Every stage can be brief or skipped when its job is already done. Review effort follows risk, and complex changes still get substantial independent review. `main`'s process template carries these (`MODELING_PROCESS.md.template:98`, `claude/commands/orchestrate-modeling.md:25`). Where the native plan's `[INFERRED]` "preserve fresh stage/audit contexts" conflicts with them, they govern.
- **[INHERITED: native `plan.md`, `remediation.md`, `audit.md`]** The native installer's behaviour contract keeps its grades. It ships 15 workflows and 10 supporting bundles from `skills/`, installed canonically under `.agents/skills/` with Claude aliases. It tracks managed files in a neutral manifest, imports legacy hashes, preserves owner additions, and never writes through destination symlinks. Its `[AGENT]` choices (workflow names including `status`, unchanged extraction providers) are not reopened.
- **[INHERITED: CLAUDE.md "Change Coordination"; epic-F2]** `cmd_init` and `scripts/replicate_setup.sh` must not drift apart. On the branch the script is already a 6-line wrapper around `init` (native `CLAUDE.md:212`); on `main` it is a full script that creates directories itself.
- **[INFERRED]** `main`'s content is the reconciliation target, not fusion-tea's installed copy. fusion-tea is pinned at `c37ff53` and predates PR #16. Its installed copy is evidence of two things: what is portable (the author-continuity sentence at fusion-tea `.agentic-mbse/codex.md:7`, the pattern-location note at fusion-tea `modeling_project/MODELING_GUIDE.md:276`) and what is target-owned (the MR-7 paragraphs, the `.codex-test` worktree paragraph at `codex.md:11`).
- **[INFERRED]** The uncommitted remediation on the branch is committed before integration, so no accepted repair is lost.

## Non-Goals

- A second native migration, new workflow names, new runtimes, runtime upgrades, token-savings measurement, or fusion-tea's full study suite.
- Registering `run-goal` or `narrate-goal` (Item 2), `research-acquire` (Item 5), or anything study-related (Item 3). Removing consumer-specific text from shipped files (Item 4).
- Re-installing fusion-tea for real. That is the epic's integration step, after Items 1–5.

## Open Questions / Deferred to design

- How to bring the branch onto `main`: rebase, or merge with `main`'s bodies taken file by file. And how to apply the envelope to `main`'s bodies without hand-editing 25 files.
- How bounded the A–K re-review is, and who runs it. It must be independent of the author.
- Whether `main`'s `claude/` tree and `MBSE_*` lists are removed in the merge or kept for one release as a compatibility path. Keeping them means two copies of all 25 bodies kept in sync by hand, which works against this item's point (product-lens smell 1); design must justify it if chosen.
- Items 2, 4 and 5 can write specs and designs while this item runs, but must not register or edit shipped files until the merge lands.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_wrap-split.md` § Item 1
- **Required Reading:** `/home/reid/1cfe/agentic-mbse-native-skills/.project/active/native-skills/{plan,remediation,audit}.md`; fusion-tea `.project/active/harness-right-size/{report.md,installed.json}`; `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 4
- **Process requirements:** `.project/active/harness-right-size/requirements.md`
- **Evidence (2026-10-04):** `.project/reports/2026-10-04-0901-status-report.md` § "What is actually broken or missing", item 4
- **Product-lens:** `.project/active/native-skill-distribution/product-lens.md`
- **Design:** `.project/active/native-skill-distribution/design.md` (to be created)

---

**Next Steps:** `/_my_spec_review` in a fresh session, then `/_my_design`.

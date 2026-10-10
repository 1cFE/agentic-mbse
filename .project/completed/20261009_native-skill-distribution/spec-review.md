# Spec Review: Reconcile the native installer source with `main` (WRAP-SPLIT Item 1)

**Spec:** `.project/active/native-skill-distribution/spec.md` (rev `b2d077b`)
**Contract:** `claude-pack/commands/_my_spec.md`. It could not be read in this sandbox (permission denied), so the spec was reviewed against this command's five lenses and `capture-fidelity.md`.
**Review File:** `.project/active/native-skill-distribution/spec-review.md`
**Date:** 2026-10-09
**Inputs:** Align record `briefs/00-align.md`; epic § Item 1; native branch snapshot at `86921f9` (`.orchestrate-logs/nsd-inputs/native/`, cited below as "native"); fusion-tea files at `403716ee3` (`.orchestrate-logs/nsd-inputs/fusion-tea/`); `main` via git (`88e2489` fork point, `8f43a09` main, `c37ff53` fusion-tea's pin).

---

## Reality Check

**Concerns.** The spec targets the right item, and its core move is right: put `main`'s content into the native shape. But three of its factual premises are wrong in ways that would mislead design:

- fusion-tea's Claude side is legacy symlinks, not a native install (L1-1).
- The `.agentic-mbse/patterns/` install location that SC4 names does not exist in the reconciled installer (L1-2).
- SC6 assumes the installer protects fusion-tea's edited adapter. It does not (L1-3).

The spec also does not yet carry the Align decisions. Targeted edits fix all of this, so the verdict is Revise, not Rework.

**What I checked, and the result:**

- **Brief fact 1 (fusion-tea's 31 Claude entries are symlinks into this checkout's `claude/`): confirmed.** One small correction that changes nothing: the five `.agents/skills/` symlinks are `browser-inspect`, `concept-research-navigation`, `narrate-goal`, `run-goal` and `run-study`, not only goal, study and browser skills.
- **Fact 2: confirmed.** The branch has 25 bundles (31 files), and its `claude/` holds only `hooks/ruff-format.sh`.
- **Fact 3: confirmed, with more detail.**
  - Legacy `.claude/skills/<name>` and `.claude/agents/<name>.md` symlinks go through the same `permit` check, via native `installation.py:193` and `:98`.
  - Non-interactive runs skip them (native `cli/__init__.py:410-414`). Interactive runs prompt once per file. `--force` replaces them, but `--force` also replaces user-owned project documents (`:427`, `:561`).
  - Exception: under `--dev`, the legacy hook symlink matches the expected link and is accepted silently, but only while the hook stays at `claude/hooks/`.
- **Fact 4: confirmed.** But `--dev` requires a `claude/` folder to exist (L3-2).
- **Fact 5: confirmed.** Since the fork, `main` changed 16 bundles, 3 tool-owned templates and 2 pattern docs.
- **Fact 6:** the spec's Branch line does not assume work in `/home/reid/1cfe/agentic-mbse`, but Open Question 1 does not rule it out (L3-5).
- **SC2's counts are right.**
  - **15 + 10 bundles:** the names match one-to-one on both trees.
  - **"10 of 25 adapted":** the branch rewrote body text in `audit-models`, `implement-model`, `manage-sources`, `onboard`, `orchestrate-modeling`, `pdf-analysis`, `plan-model`, `python-debugger`, `record-learning` and `toolkit-awareness`. The other 15 differ from the fork only in frontmatter, preface and reflow.
  - **"Five unchanged on `main`":** `manage-sources`, `onboard`, `pdf-analysis`, `python-debugger` and `record-learning`.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** Problem bullet 3 describes only fusion-tea's Codex side.

- **What is actually there:** fusion-tea's Claude side is 31 absolute symlinks into `/home/reid/1cfe/agentic-mbse/claude/` (`runtime-entries.txt`), made by the old `replicate_setup.sh`. fusion-tea's `.agentic-mbse/install.json` has no `.claude/` entries.
- **Consequences the spec does not state:**
  - fusion-tea's Claude Code reads, live, whatever branch that checkout has checked out.
  - Merging the branch deletes `claude/`. Once that checkout moves to the new `main`, all 31 links dangle.
  - Today's installer does not take these links over (fact 3).
- **Why it matters:** this is the premise the Align decisions rest on.
- **Rewrite request:** describe both sides in bullet 3.

**L1-2 · Direct claim:** SC4 and Known Requirement 6 rely on a pattern location that the reconciled installer never creates.

- **The claim:** SC4 asks the guide to name "the copy installed in `.agentic-mbse/patterns/`".
- **The code:** the native installer has no code that installs pattern docs anywhere. A search for `patterns` in native `src/` finds nothing. `install_assistants` (native `installation.py:303-342`) installs skills, adapters, entry files, agents and hooks only.
- **Where the location comes from:** fusion-tea set up `.agentic-mbse/patterns/` (14 manifest rows) for itself.
  - Its own `codex.md:11` introduces the folder with "For this worktree".
  - Its guide (`MODELING_GUIDE.md:276`) cites its local `.project/workflow-installation-20260913.md`.
  - The error starts in the epic's Item 1 Current State: "the native installer copies patterns to `.agentic-mbse/patterns/`".
- **The contradiction:** as written, SC4 conflicts with SC5's "no installed text names a path … the chosen install does not provide".
- **Two ways out:**
  - **(a)** SC4 takes `main`'s resolver text. `main`'s `MODELING_GUIDE.md.template:276-282` already names `get_docs_dir()/patterns`, which works for both source and packaged installs. Line 282 still needs the branch's Codex adaptation, because it names `.claude/settings.json`. fusion-tea's pattern note becomes target-owned, with a ledger row.
  - **(b)** The item adds pattern installation to the installer.
- **Recommendation: (a).** It adds no installer behaviour, which fits "not a mandate to polish the native installer". Known Requirement 6's "portable" label for fusion-tea's guide note should flip to target-owned.

**L1-3 · Direct claim:** SC6's protection claim is false for one of its two named files.

- **The claim:** SC6 says fusion-tea's edited tool-owned files are "kept or backed up under the installer's ownership rules, not silently overwritten". It names the MR-7 paragraphs and the adapter's worktree paragraph.
- **Checked against fusion-tea's manifest:**

| File | Current file vs manifest hash | What a re-init does |
|---|---|---|
| `modeling_project/MODELING_PROCESS.md` (MR-7 paragraphs) | differs | prompts, or preserves when non-interactive |
| `.agentic-mbse/codex.md` (worktree paragraph) | equal | overwrites with no prompt |
| `modeling_project/MODELING_GUIDE.md` (pattern note) | equal | overwrites with no prompt |

- **Why the last two are overwritten:** the 2026-09-13 install recorded fusion-tea's edited versions as the baseline. `permit` accepts any file that matches its manifest hash (native `installation.py:72-73`). So a plain re-init loses the `.codex-test` worktree paragraph (`codex.md:11`) and the pattern note (`MODELING_GUIDE.md:276`).
- **The 13 hand-updated payloads behave the same way.** The manifest records their "after" hashes (`installed.json`), so a re-init replaces them silently. That is the desired result for them, but the spec should know it happens.
- **What follows:** the installer's ownership rules cannot meet the owner's no-loss criterion here.
  - The target-owned text has to move first into a file fusion-tea owns, such as `AGENTS.md`, which the installer never overwrites (native `installation.py:325`). Each move needs a ledger row.
  - The re-init now happens at Item 1's merge, so this move becomes Item 1's job.
  - Writes to fusion-tea are reserved to the owner. The item produces the ledger rows and the proposed fusion-tea edits; the owner applies them.

**L1-4 · Direct claim:** Known Requirement 4 puts a do-not-relitigate marker on agent-grade items.

- **The text:** "Its `[AGENT]` choices (workflow names including `status`, unchanged extraction providers) are not reopened."
- **The source grades:** native `plan.md:10` grades these `[AGENT]`. The rest of the installer contract the requirement inherits is `[INFERRED]` (`plan.md:7-9`).
- **The rule:** capture-fidelity law 1 lets only owner-originated items be marked settled.
- **Rewrite request:** say these items hold unless evidence warrants a change, and that any challenge re-derives against `plan.md`'s reasoning.
- **Owner source now available:** the skills-for-both-runtimes shape this requirement inherits as `[INFERRED]` now has owner backing in the Align quote (L1-5). Cite it.
- **Stakes:** low in practice, since nobody is arguing to rename workflows. It is still a structural violation.

**L1-5 · Rewrite request:** carry the Align decisions, each at its true grade.

- **The owner's ask, as `[NEED]` with the quote:** "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this". This becomes the owner-grade source for the item's point. Today that point traces only to inherited and agent sources.
- **Three decisions, each `[INFERRED] (ratified by owner 2026-10-09)` and none marked settled:**
  - The merge removes `claude/` with no shim. This resolves the `claude/` half of Open Question 3.
  - The installer adopts legacy symlinks, tested over a copy of fusion-tea (see L3-3 for the boundary).
  - The owner runs `init --dev` once in fusion-tea after the merge. This makes Non-Goal 3 ("Re-installing fusion-tea for real … after Items 1–5") wrong. Amend it so the Claude-side switch happens at Item 1's merge, while the epic's later integration step keeps the rest (removing local skills, the sysml-codegen install).
- **The rename quote is a permission, not a mandate:** "to be modle-agnostic, you can rename the folder hosting skills on the agentic-mbse side".
  - Carry it verbatim, with its force stated as permission.
  - The derived requirement, that no Claude-named source folder remains and the hook moves, follows from the ratified `claude/` removal. Grade it `[INFERRED]`.
  - Do not harden "rename `skills/`, `agents/`, `adapters/`" into a requirement.
- **Reserved gates:** merging and pushing are the owner's, and so are writes to fusion-tea's real tree. They change how SC8 and the post-merge step are phrased (L3-5).

**L1-6 · Direct claim (minor):** SC1's "sixteen differences observed on 2026-10-04" were measured against fusion-tea, not against `main`.

- **Evidence:** the status report says "Sixteen native source bundles differ from current Fusion TEA" (`.project/reports/2026-10-04-0901-status-report.md:66`).
- **The real inventory against `main`:**
  - 16 bundles that `main` changed since the fork (11 workflows and 5 supporting skills).
  - 3 tool-owned templates (`MODELING_PROCESS`, `MODELING_GUIDE`, `EPIC_GUIDE`).
  - 2 pattern docs.
  - Changes made only on the branch: 2 user-owned templates, 2 agents, and the adapters.
- **Rewrite request:** drop the "sixteen" anchor, or label it as fusion-tea-relative.
- **Also stale:** Problem bullet 2 ("uncommitted A–K remediation") and Known Requirement 7. The remediation is now committed at `86921f9`, so Known Requirement 7 can become a stated fact.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** the item's point has no success criterion.

- **The point:** one place to register a skill (Align). The product-lens falsifier says the same thing in reverse: "a new skill still has two inventories to register in".
- **The branch fails it today.** `MBSE_COMMANDS` and `MBSE_SKILLS` (native `cli/__init__.py:18-48`) survive only as a test inventory. `tests/test_cli.py:289` and `tests/test_installation.py:35` assert that these lists equal `skills/*/SKILL.md`. So adding a skill means adding a bundle and a list entry, or the tests fail.
- **The spec misreads this.** Open Question 3 treats `MBSE_*` as `main`'s legacy, but the branch still has the lists.
- **If-then tradeoff:**
  - **If** the owner wants the lists kept as a deliberate guard, which forces a conscious choice between workflow and supporting skill, say so. "One place" then means a bundle plus one classification line.
  - **If not,** the bundle itself carries the classification and the lists go.
- **Either way:** add a success criterion that names the registration outcome.

**L2-2 · If-then tradeoff on effort:** 1.5 days no longer fits as scoped. About 2 days does, with three things shed.

**What the Align decisions add** (my estimate, about 4–6 hours):
- Legacy-symlink adoption across four kinds of entry, with negative cases.
- The ripple from removing `claude/` through five code sites and packaging (L3-2).
- A rehearsal on the fusion-tea copy, plus an owner runbook.
- Moving target-owned text out of fusion-tea's overwritten files (L1-3).

**What the evidence lets you take away:**
- **Most bundles are "take `main`", not merges.**
  - `main`'s September rewrite already removed the Claude-only text the branch had adapted in `audit-models`, `implement-model`, `orchestrate-modeling`, `plan-model` and the process template. My token scan of `main`'s changed bodies found no `Task`, `AskUserQuestion`, `.claude/` or `Skill tool` in them.
  - So those files are "take `main`, add the envelope". The branch's 144-line process-template change no longer matters.
  - Only `toolkit-awareness` and `MODELING_GUIDE.md.template` need real three-way merges. Scope 1 is much smaller than "25 files" suggests.
- **Drop reflow** from the envelope (L3-1).
- **Fold the A–K re-review into the item's own independent audit.** Adoption changes the installer again after A–K, so a separate A–K review would examine a moving target.
- **Take option (a) for SC4** (L1-2).

**Recommendation:** re-estimate to 2 days with those three sheds. That is the epic's per-item ceiling. **If** the owner holds 1.5 days, the next things to cut are SC4 as a separate requirement (take `main`'s guide text plus the Codex fix at line 282) and the A–K re-review as its own gate.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request:** SC2 cannot be checked by a script without judging each file. There are three reasons.

**(a) "Runtime adaptation" is defined by four example kinds, but the branch made more.**
- `plan-model`: "delegation tool" for `Task tool`.
- `record-learning`: "the host's skill-loading interface" for "Skill tool".
- `manage-sources` and `onboard`: whole-paragraph rewrites of the permission text.
- `onboard`: adds `modeling_project/OVERVIEW.md` next to the entry file. That is a content change, not an adaptation.
- A script will flag every one of these, and a person must judge each.

**(b) "Paragraph reflow" forces a whitespace-blind comparison, and the branch's reflow already broke a code sample.**
- In the process template, it joined two lines of a fenced `python` block into one: native `MODELING_PROCESS.md.template:404` reads `intermediate = param_a * factor result = intermediate + param_b`. The fork had these on two lines (`:473-474`).
- A whitespace-blind diff passes that breakage.
- `main`'s September rewrite removed nearly all hard wrapping, so reflow buys nothing now.

**(c) SC2 covers "the process template" only.** `main` also changed `MODELING_GUIDE.md.template` (13 lines, and one of the two real merges) and `EPIC_GUIDE.md.template` (27 lines, which fusion-tea hand-updated).

**What needs to be true:** the allowed difference is a closed list that is reviewed once, so the script passes only when nothing else remains.
- One way to get there: the envelope is frontmatter plus preface only, with no reflow. The adaptation is the branch's own fork-to-branch changes in named files, recorded once in evidence. Everything else is byte-equal to `main`.
- By my measurement, that leaves adaptation changes in 7 files: the five bundles changed only on the branch, `toolkit-awareness`, and `MODELING_GUIDE`.
- The spec should not prescribe the mechanism. It should say that the check needs no per-file judgment beyond reviewing that one list.

**L3-2 · Direct claim:** removing `claude/` breaks `--dev` and the wheel build unless five places change. The owner's post-merge step depends on `--dev`.

**Where the branch depends on `claude/`:**
- `_get_data_root` decides it is running from a source checkout only when `claude/` exists (native `cli/__init__.py:108`).
- `_check_dev_mode_prerequisites` refuses `--dev` without `claude/` (`:275`).
- The installer reads the hook from `claude/hooks` (`get_hooks_dir` at `:137`; `install_assistants` at native `installation.py:339`).
- The wheel build force-includes `claude` (native `pyproject.toml:54`, `:65`).
- Tests pin `.claude/hooks/` creation (native `tests/test_cli.py:166-175`, `:470-475`).

**What the spec must say:** with no `claude/` folder in the source, `init`, `init --dev` from a source checkout, and a built wheel all still install every asset, including the hook. Without this, ratified decision 1 (remove `claude/`) silently breaks ratified decision 3 (`init --dev`).

**L3-3 · Rewrite request:** SC5 and SC6 do not cover legacy-symlink adoption. SC5 covers fresh installs only. SC6 installs over the fusion-tea copy but says nothing about the 31 legacy entries. A criterion is needed that states five things.

1. **What is adopted.** An entry qualifies when all of these hold:
   - It sits where the old installer put it: `.claude/commands/<name>.md`, `.claude/skills/<name>`, `.claude/agents/<name>.md` or `.claude/hooks/<name>`.
   - It is a symlink.
   - The installer ships its name.
   - Its target path lies under an agentic-mbse `claude/` folder.

   This must work when the target no longer exists. After the merge every one of these links dangles, so recognition cannot depend on reading the target.
2. **What "replaces" means.** The link itself is removed, and the installed skill alias, agent or hook takes its place. Nothing is written through the link, which keeps Known Requirement 4's "never writes through destination symlinks" true. No `--force` and no prompt.
3. **What is never adopted:**
   - A symlink with a name the installer does not ship, such as fusion-tea's five `.agents/skills/` links into its own `.claude/skills/`.
   - fusion-tea's own `manage-concept` and `research-acquire` commands.
   - Real files and directories.
   - A shipped-name link that points anywhere else, such as a personal fork.

   These keep today's prompt-or-preserve behaviour. This answers the orchestrator's question about symlinks the owner made on purpose. A shipped-name link into an agentic-mbse `claude/` folder counts as installer-made, which the owner ratified. A link pointing anywhere else belongs to the owner.
4. **What the owner sees.** The install report lists each adopted entry with its old target, so a deliberate link can be recreated.
5. **The evidence.** After installing over the fusion-tea copy:
   - Claude Code discovers all 25 skills, the 5 agents and the hook.
   - fusion-tea's own skills and commands are byte-for-byte untouched.

How to recognise "under an agentic-mbse `claude/` folder" once that folder is gone stays a design choice: path shape plus shipped name, or a recorded list of known checkout roots. The spec should state the boundary above.

**L3-4 · Direct claim:** SC6 allows "kept or backed up". Now that the re-init moves to Item 1's merge, "backed up" breaks the inherited MR-7 owner criterion.

- **The failure path:**
  - The owner answers "backup" at the `MODELING_PROCESS.md` prompt.
  - The MR-7 paragraphs (fusion-tea `MODELING_PROCESS.md:17`, `:34`) move to `MODELING_PROCESS.md.backup`.
  - The live file becomes the shipped template, a symlink under `--dev`.
  - "MR-7 enforcement stays intact after re-init" (Known Requirement 1; epic `:66`) fails until Item 2 lands the general section.
- **What follows:** the post-merge runbook must keep (skip) that file. The non-interactive rehearsal skips by default (native `cli/__init__.py:411-413`), so it never exercises this prompt. The runbook therefore has to say what to answer.
- **Two other `--dev` side effects belong in the rehearsal:**
  - **`.gitignore` additions.** `_update_gitignore_for_dev_mode` appends `.claude/skills/`, `.agents/skills/`, `.agentic-mbse/` and the tool-owned template paths to fusion-tea's `.gitignore` (native `cli/__init__.py:77-91`). fusion-tea whitelists its own skills under `.claude/skills/` (epic, Item 2 Current State). A later `.claude/skills/` rule can override those whitelist entries for new, untracked files. I could not read fusion-tea's `.gitignore`; the rehearsal on the copy should check it.
  - **Live links cover skills and templates only.** `--dev` links skills and templates to the source but copies agents and adapters, because those writes pass no source (native `installation.py:321`, `:335`). "Live editing continues" holds for skills and templates, not for agents or adapters.

**L3-5 · Rewrite request:** SC8 and Non-Goal 3 describe owner actions as item outcomes.

- **SC8 rephrase.** Today it says "The branch is merged to `main`". The run ends at an audited branch ready for `pre_pr`, and the merge and push are reserved to the owner. Rephrase so that the integration branch carries `main`'s full history plus the native work, passes pytest, ruff and mypy, and is ready for the owner to merge.
- **Add a runbook outcome for the post-merge step.** The owner receives a runbook, rehearsed on the fusion-tea copy, that covers four points:
  1. **The command, and which agentic-mbse it runs.** fusion-tea's own `agentic-mbse` is the pinned `c37ff53` build, which is `main`'s old installer. A non-editable install cannot use `--dev` at all (native `cli/__init__.py:275-279`). The step must run the merged checkout's CLI against fusion-tea's path.
  2. **The fusion-tea edits that must land first.** These are L1-3's moved text and its ledger rows.
  3. **The answer for each prompt.** In particular, skip `MODELING_PROCESS.md` (L3-4).
  4. **The broken window.** fusion-tea's Claude side is broken between updating `/home/reid/1cfe/agentic-mbse` to the merged `main` and running the step.
- **Add a `[HARD]` constraint**, forced by fusion-tea's live symlinks: no integration work switches branches in `/home/reid/1cfe/agentic-mbse`. Open Question 1 should say that integration happens in a worktree.
- **Small test-porting point.** `main`'s `tests/test_modeling_command_contracts.py` reads `claude/commands/*.md` and asserts `Task` in the orchestrator's frontmatter (`:72`). The branch's envelope renames that tool to `Agent`. "pytest passes" hides this judgment call; the disposition table should list it.

**L3-6 · Question to the user:** should the post-merge step also move fusion-tea's agentic-mbse pin? This is the version skew between installed skill text and the pinned CLI.

- **The skew.** After `init --dev`, fusion-tea's skill text comes live from `main`, while the CLI those skills call stays pinned at `c37ff53` (Known Requirement 6). fusion-tea keeps instruction text and its pinned runtime separate on purpose (`codex.md:11`).
- **PR #16 is a live case of it.**
  - `main`'s `research.md:81` tells the agent to approve with `--insights '[]'`.
  - The behaviour behind that is in `pm/operations.py`, which PR #16 changed (65 lines between `c37ff53` and `8f43a09`).
  - The status report (item 3) recorded the older runtime refusing `[]` with "No insights provided".
  - fusion-tea's Claude side already has this skew today, because it reads this checkout live. The re-init would extend it to Codex.
- **Questions:**
  - Should the post-merge step also move fusion-tea's pin to the merged SHA (hand-edit `uv.lock`, then `uv sync --frozen`)? Or is the skew accepted and recorded?
  - What does SC6's "preserves its runtime pin" mean? `init` never touches `uv.lock`, so as written it is always true.
    - If it means the item leaves the pinned runtime alone, say so.
    - If the owner wants pin and text kept in line, the outcome is the opposite.

**L3-7 · Rewrite request (minor):** SC5's "No installed text names a path or tool that the chosen install does not provide" is absolute, and two engineers would read it differently.

- The branch's own preface names `.agentic-mbse/codex.md` in a Claude-only install, conditionally ("in Codex").
- `project-structure` draws `CLAUDE.md` in its tree diagram (native `SKILL.md:70`) in a Codex-only install.
- **Rewrite request:** say "no instruction directs the agent to …", or name the runtime-conditional exception.

**L3-8 · Rewrite request (minor):** two open questions are misfiled.

- Open Question 3 is now answered for `claude/`. Reduce it to the `MBSE_*` question (L2-1).
- The fourth open question ("Items 2, 4 and 5 … must not register or edit shipped files until the merge lands") is a process rule for the epic, not a design question. Move it to the epic or to a Non-Goal.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** fix the stale facts.

- Problem bullet 2: "`955295b`, plus uncommitted A–K remediation in 8 modified and 4 untracked files".
- Known Requirement 7.
- The epic's Item 1 Current State line about pattern copying (L1-2), so Items 2 and 4 do not inherit the error.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** SC2 is one dense paragraph that a reader cannot apply on one read.

- **What it mixes:** the criterion itself, two definitions, a count, a list of five bundle names and an instruction about evidence.
- **The result:** a reader cannot tell what passes.
- **Rewrite request:** lead with the pass condition. Put the envelope and adaptation definitions after it, as short lists.

---

## Engagement Summary

**Overall take:** the item's direction is right, and the spec's counts hold up against both trees. The trouble is the fusion-tea side. The spec assumes installer protections and an install location that do not exist. Now that the owner moved the fusion-tea re-init to Item 1's merge, those gaps turn into information loss at the owner's first post-merge command. Fix the premises, carry the Align decisions, and re-estimate.

**Here's what I need you to weigh in on:**

1. **[L1-1, L1-5, L3-5] Carry the Align decisions.**
   - Fix Problem bullet 3.
   - Add the owner's ask as `[NEED]` and the three ratified decisions as `[INFERRED] (ratified)`.
   - Amend Non-Goal 3.
   - Rephrase SC8 so the item ends at a branch ready for the owner to merge.
   - Add a rehearsed runbook for the owner's post-merge `init --dev`, run with the merged checkout's CLI rather than fusion-tea's pinned one.
2. **[L1-3, L3-4] No-loss at the post-merge re-init.**
   - fusion-tea's edited `codex.md` and `MODELING_GUIDE.md` match their manifest hashes, so a re-init overwrites them silently.
   - Their target-owned text needs moving into fusion-tea-owned files, with ledger rows, before the owner runs the step.
   - The runbook must skip `MODELING_PROCESS.md`; "backed up" breaks MR-7.
3. **[L3-3] Define legacy-symlink adoption.** Adopt only shipped-name symlinks at old-installer locations that point into an agentic-mbse `claude/` folder, even when dangling. Replace the link, never write through it, and report each adopted link with its old target. Never adopt anything else.
4. **[L3-2] Removing `claude/` breaks `--dev` and packaging.** Five places key on `claude/`. Add the outcome that `init`, `init --dev` and a built wheel still work with no `claude/` folder.
5. **[L1-2] SC4 names a location that does not exist.** No installer creates `.agentic-mbse/patterns/`. I recommend taking `main`'s `get_docs_dir()` resolver text, plus the Codex fix at line 282, and making fusion-tea's note target-owned.
6. **[L3-1, L5-1] Make SC2 checkable.**
   - Drop reflow; it already broke a code block.
   - Make the adaptation a closed list.
   - Cover all three changed templates.
   - Lead with the pass condition.
7. **[L3-6] Pin skew.** Should the post-merge step move fusion-tea's pin to the merged SHA, given that PR #16's `/research` instruction needs runtime behaviour `c37ff53` lacks? And what does "preserves its runtime pin" mean?
8. **[L2-1, L2-2] The point and the budget.**
   - Add a criterion for "one place to register a skill". Decide whether the `MBSE_*` test lists stay as a deliberate guard.
   - Re-estimate to about 2 days, shedding reflow, a separate A–K re-review, and new pattern installation.

---

## Resolutions

Resolved 2026-10-09 by the orchestrator acting for the owner. Every call below is [AGENT] (orchestrator) unless it cites an owner source; none is settled. Reserved gates from `briefs/00-align.md` (merge/push; writes to fusion-tea's real tree) are respected throughout.

**New fact the reviewer could not check** [AGENT, verified by orchestrator 2026-10-09]: fusion-tea tracks its Codex install in git: `.agents/skills/*/SKILL.md`, `.agentic-mbse/{codex.md,install.json}` and `.agentic-mbse/patterns/*` are all in `git ls-files`. Its `.gitignore:17-33` already carries an old dev-mode block that ignores `.claude/{commands,agents,skills,hooks}` with whitelist lines for its own commands and skills, plus the four tool-owned templates. Its Codex adapter says "These instruction assets are separate from the pinned runtime" (`codex.md:11`). Consequence: `init --dev` would replace tracked Codex files with absolute symlinks into `/home/reid/1cfe/agentic-mbse/skills/`, which is machine-specific and git-visible. A plain `init` keeps both runtimes on installed copies (Claude aliases are symlinks into `.agents/skills/`, `installation.py:310-318`). This is evidence against ratified decision 3's choice of `--dev`; it is surfaced to the owner and not resolved here (see L3-4).

- **L1-1** — Accept. Problem bullet 3 describes both sides.
- **L1-2** — Accept option (a). The guide template carries `main`'s `get_docs_dir()` resolver text; its line about `.claude/settings.json` gets the runtime adaptation so it reads correctly under Codex. fusion-tea's `.agentic-mbse/patterns/` note is target-owned with a ledger row. Known Requirement 6's label flips. No pattern installation is added. The epic's Item 1 Current State line is corrected in the same revision.
- **L1-3** — Accept. The author-continuity sentence (`codex.md:7`) is portable and lands in both shipped adapters (SC3). The `.codex-test` worktree paragraph (`codex.md:11`) and the pattern note (`MODELING_GUIDE.md:276`) are target-owned. Item 1 writes their ledger rows and a proposed fusion-tea change that moves them into fusion-tea-owned files before any re-init; the owner applies it (reserved gate). The silent replacement of the 13 hand-updated payloads is the intended result and should be stated as such.
- **L1-4** — Accept. Known Requirement 4 drops the do-not-reopen marker: the native plan's `[AGENT]` choices hold unless evidence warrants, challenged by re-deriving against `plan.md`. Cite the Align quote as owner backing for the skills-for-both-runtimes shape.
- **L1-5** — Accept as written, including the force of the rename quote (permission, not mandate) and the `[INFERRED]` grade on "no Claude-named source folder remains".
- **L1-6** — Accept. Drop the "sixteen" anchor in favour of the inventory against `main`: 16 bundles changed on `main` since the fork, 3 tool-owned templates, 2 pattern docs, and the branch-only changes. Refresh the remediation facts (committed at `86921f9`).
- **L2-1** — Decide: one place means no hand-maintained list. Adding a workflow, supporting skill or expert role means adding its directory or file under the source tree, and nothing else in source or tests must change for install, `install-commands --list` and the suite to pick it up. The workflow-vs-supporting classification lives in the bundle itself; design picks the field. A guard against accidental deletion is allowed only if it never needs editing when a skill is added. Add a success criterion for this.
- **L2-2** — Accept. Re-estimate to 2 days. Shed reflow from the envelope; fold the A–K re-review into this item's own independent audit (which then updates the native `audit.md` verdict); add no pattern installation. Update the epic's Item 1 effort and timeline total to match.
- **L3-1, L5-1** — Accept. SC2 leads with the pass condition. The envelope is frontmatter plus preface only. Runtime adaptation is a closed list of named changes recorded once in the evidence and reviewed once; the check passes only when nothing outside that list differs from `main`. It covers every bundle, all three tool-owned templates `main` changed, and the pattern docs. The spec does not prescribe the script.
- **L3-2** — Accept as an outcome: with no `claude/` folder in the source, `init`, `init --dev` from a source checkout, and an installed built wheel each install every asset, including the hook.
- **L3-3** — Accept the five-part boundary as the success criterion, including recognition of dangling links and the install report listing each adopted entry with its old target. The recognition mechanism stays a design choice.
- **L3-4** — Accept, widened by the new fact above. The runbook says to keep (skip) `MODELING_PROCESS.md` until Item 2 lands the general section. The rehearsal on the fusion-tea copy reports the git-visible effect (`git status` on the copy) and the `.gitignore` effect of each mode it supports. The "live editing" claim is narrowed to what `--dev` actually links (skills and templates). Which mode the owner runs (`init` or `init --dev`) is the owner's choice at the reserved post-merge step; the runbook presents both with their effects and recommends plain `init`, because fusion-tea commits its Codex install and states that instruction assets are separate from the runtime. The spec does not hard-wire `--dev`.
- **L3-5** — Accept. SC8 becomes: an integration branch carrying `main`'s full history plus the native work, passing pytest, ruff and mypy, ready for the owner to merge. Add the runbook outcome with the reviewer's four points. Add the `[HARD]` constraint that no integration work switches branches in `/home/reid/1cfe/agentic-mbse` (forced by fusion-tea's live symlinks until the post-merge step). The `Task`→`Agent` contract-test port gets a row in the disposition table.
- **L3-6** — Resolve from recorded intent: [INHERITED: `.project/CURRENT_WORK.md`, "fusion-tea's pin is still at `c37ff53` … move it and re-run init"]. The runbook's first step moves fusion-tea's agentic-mbse pin to the merged SHA (per project memory: hand-edit `uv.lock`, then `uv sync --frozen`), so installed text and runtime agree, then re-inits. SC6's "preserves its runtime pin" becomes: `init` does not modify fusion-tea's `pyproject.toml` or `uv.lock`; moving the pin is a separate, explicit runbook step.
- **L3-7** — Accept. "No instruction directs the agent to a path or tool the chosen install does not provide", with runtime-conditional text named as allowed.
- **L3-8** — Accept. Open Question 3 shrinks to nothing once L2-1 is decided; remove it. The "Items 2, 4 and 5 must not register…" rule moves to the epic (or a Non-Goal).
- **L4-1** — Accept.

Verdict after resolutions: Revise; the revision stage applies all of the above together with `briefs/00-align.md`.

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded, run the spec revision stage, which applies these findings together with the Align decisions in `briefs/00-align.md`. The reviewer does not edit the spec. The epic's Item 1 Current State (pattern copying) and its "Epic integration" timing also need a matching edit outside this spec.

# Design Review: Reconcile the native installer source with `main` (WRAP-SPLIT Item 1)

**Design:** `.project/active/native-skill-distribution/design.md` (at `fc0bcb9`)
**Spec:** `.project/active/native-skill-distribution/spec.md` (SC1–SC12, revised after `spec-review.md`)
**Review File:** `.project/active/native-skill-distribution/design-review.md`
**Date:** 2026-10-09
**Reviewer:** fresh non-author agent, orchestrated stage (`briefs/04-design_review.md`)
**Inputs read:** the design, spec, Align record, spec review, product-lens ledger; native snapshot at `86921f9` (`.orchestrate-logs/nsd-inputs/native/`, cited as "native"); fusion-tea files at `403716ee3` (cited as "fusion-tea"); `main` at `8f43a09` and the fork `88e2489` via git. My measurement scripts are in `.orchestrate-logs/design-review-scratch/nsd_*.py` (gitignored).

---

## The Point

[NEED] (owner, verbatim, `briefs/00-align.md:19`) "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this".

[AGENT] (orchestrator's reading, confirmed with the owner at Align) One place to register a skill. After this item, one tool-neutral source tree carries `main`'s current text and is the only thing the installer reads, and `agentic-mbse init` installs it the same way for Claude Code and Codex. Items 2, 4 and 5 then edit one tree instead of two.

fusion-tea carries two owner criteria (`[NEED]`, epic `:65-66`): no loss of information, and MR-7 enforcement intact after re-init. Its Claude side today is 31 absolute symlinks into this checkout's `claude/`, which the merge deletes, so the installer must take those links over and the owner needs a rehearsed runbook.

The orchestrator's bar for this review: is the end-state installer clean and obvious to a maintainer, is each mechanism the smallest one that works, and does anything here add machinery the item does not need.

## Fundamental Assessment

**Sound, with concerns. Verdict: Revise (targeted edits, no rework).**

The approach is right. Both halves extend something the native installer already has instead of adding a parallel mechanism:

- **Content.** Regenerate the shipped text from `main` with a fixed envelope plus a short reviewed list, rather than hand-merging 25 files. I re-ran the envelope against the real branch: deleting the `skills:` line and changing `Task` to `Agent` on `allowed-tools` reproduces the branch's frontmatter for all 25 bundles from the fork, including the supporting skills and `python-debugger`'s two-key frontmatter (`nsd_fmcmp.py`). The adaptation list's counts match `main`'s bodies exactly (`nsd_counts.py`). A wider token scan (`nsd_tokens2.py`) finds no Claude-only instruction outside Appendix A except tool names the adapters already map (`Explore`, `general-purpose`, `WebSearch`, `WebFetch`), which the design names as a Non-Goal.
- **Legacy links.** Recognizing the old installer's links inside `Installer.permit` is the link counterpart of the existing legacy-hash import (native `installation.py:49-52`). It is the smallest place that covers commands, skills, agents and the hook at once.
- **Most installer work is deletion.** The `MBSE_*` lists, the `claude/` keys and the hand-maintained counts go.

Three things keep this from Approve. Each is a targeted edit:

1. **A third copy of the shipped text is invisible to the design.** This repo tracks its own `.claude/` install: 21 copied files (9 commands, 3 supporting skills with their reference and script files, 5 agents and the hook), plus a tracked absolute symlink `.claude/skills/pdf-analysis -> /home/reid/1cfe/agentic-mbse/claude/skills/pdf-analysis` (`git ls-files .claude`). Neither side changed these since the fork, so the merge keeps them. After the merge that symlink dangles in every clone of `main`, and the 9 stale command copies are a second registration surface for Claude Code inside this repo. That works directly against the point. Finding C2.
2. **The adaptation list's scope is unstated, and two entries also match the frontmatter.** `AskUserQuestion` appears in `allowed-tools` for `manage-sources` and `record-learning`. Appendix A's counts (4 and 2) are body-only counts. A whole-file replace finds 5 and 3. The natural "fix", raising the count, rewrites Claude's tool grant. Finding C1.
3. **Some machinery is not needed.** D9 replaces `retire_command` with a generic `Installer.remove` plus `expose_to_claude`. Adoption needs no change there, because `retire_command` already passes through `permit` (native `installation.py:208`). A generic `remove` also widens the surface that Invariant I2 depends on. The legacy predicate also normalizes and accepts relative link text the old installer never wrote. Findings M1 and M2.

**Product-lens:** gate DISPOSED (design-F1 to F3). No finding is owner-grade. design-F2 and design-F3 independently reach my S2 and M4. design-F1 is a provenance tag (S9). Details in "Product-lens verdict" below and in `product-lens.md`.

**Design smells (product-lens §4):**

- **A consumer compensates for a producer guarantee:** not fired. Moving fusion-tea's target-owned passages into `AGENTS.md` (D10) is the consumer keeping its own text out of tool-owned files. That is the ownership rule working as stated, not compensation for a broken guarantee.
- **Who owns an invariant changes without saying so:** not fired, but close. SC8's "the installer ships its name" moves out of the predicate and into caller discipline (I2). The design says so explicitly, which is what keeps it from firing. D9's generic `remove` would quietly weaken that discipline (M1).

---

## Dimensional Review

### 1. Spec Compliance

**Assessment: Concerns**

Every SC has a design element and a validation row. The gaps are in evidence and scope, not in coverage.

- **SC1/SC2: the adaptation scope is unstated (C1).** D3 and D4 never say whether adaptations apply to the whole file or the body below the frontmatter. Measured on `main` at `8f43a09`:

  | Entry | `old` in frontmatter | in body | Appendix A count |
  |---|---|---|---|
  | A6 `manage-sources` `AskUserQuestion` | 1 (`allowed-tools`, `:5`) | 4 | 4 |
  | A11 `record-learning` `AskUserQuestion` | 1 (`allowed-tools`) | 2 | 2 |

  The branch keeps `AskUserQuestion` in both frontmatters and replaces it only in the bodies. The design author's own script measured body text (`nsd-design-scratch/wdiff.py:20`), so the counts are right for the body. The design must say so.
- **SC6/SC12 and the point: the repo's tracked `.claude/` tree (C2).** No row in Appendix B or in SC1's disposition table covers it. Details under Duplication.
- **SC8 evidence: the Claude probe cannot show 25 skills (M3).** The validation row expects "probe shows 25 skills and 5 agents". The native discovery probe reads Claude's catalog, which lists only user-invocable skills. The native results show 18 for Claude and 25 for Codex (native `.project/active/native-skills/remediation-discovery.json`). The seven `user-invocable: false` reference skills never appear in Claude's catalog. Expect Claude 18 plus 5 roles, Codex 25. Prove the seven reference skills with a filesystem check through `.claude/skills/<n>/SKILL.md`.
- **SC8 wording against D5 (M2, last bullet).** The spec says a shipped-name link "that points anywhere else, such as a personal fork" is never adopted (`spec.md:46`). D5 adopts links into any agentic-mbse checkout, including other clones and worktrees (D5's rejected alternative at `design.md:103` says a recorded list "misses other clones and worktrees"). I think D5's reading is right: a link into another clone's `claude/` was made by that clone's `init --dev`, so it is installer-made in the same sense. But "personal fork" can be read as a fork of agentic-mbse. State the reading in D5 so the auditor does not flag it.
- **SC9 (S2).** Verbatim is right for "no loss". But the moved pattern note now contradicts the shipped guide for Codex. Details under Bets.
- **SC12: R5 is settled.** The spec now carries the parity rule (`spec.md:64`). Drop R5's "must confirm" and the "Open for the owner" line at `design.md:332`.

**Capture fidelity.** The owner quote is carried verbatim as `[NEED]` and the orchestrator's reading is graded `[AGENT]`. D1–D13 are design decisions, agent-grade by construction, and the handoff lists them as "Fixed" for the plan. That is the right use of the word. No spec `[INFERRED]` item is silently hardened. The one spec item the design reinterprets (SC8 "personal fork") is noted above.

### 2. Pattern Consistency

**Assessment: Pass**

- Adoption sits in `permit`, the one ownership gate every replacement already passes (native `installation.py:98`, `:124`, `:193`, `:208`). It reuses the action-bucket report pattern (`installation.py:45-47`). That is the existing pattern.
- `is_source_checkout` replaces three ad hoc `claude/` checks with one predicate (D8). D8's rejected alternative is correct: the wheel's data folder also has `skills/`, so a `skills/` marker would let `--dev` pass on a wheel install.
- The brief asks whether the `--dev` prerequisite really needs the same predicate as adoption. It does. Both ask "is this directory an agentic-mbse source checkout?" Sharing the predicate means a future layout change breaks data-root detection, `--dev` and adoption together, and loudly, instead of one of them silently.
- `src/agentic_mbse` is a sound marker. In a source checkout it holds by construction, since `_get_data_root` derives the root from `__file__` (native `cli/__init__.py:107`). From a wheel, `<site-packages>/../src/agentic_mbse` never exists.
- `skill_bundles()` globbing the tree, agents globbing `agents/*.md` and hooks globbing `hooks/*` already follow the native discovery pattern.

### 3. Abstraction Quality

**Assessment: Concerns**

- **`legacy_link_target` is the right size, apart from its normalization (M2).** It is one pure function behind `permit`.
- **D9 adds two abstractions the item does not need (M1).**
  - Adoption works through today's `retire_command` with no edit. `retire_command` calls `permit(".claude/commands/<n>.md")` (native `installation.py:208`). `permit` adopts the link, `retire_command` unlinks it and pops the manifest key (`:215-220`), and the alias follows.
  - The stated reason for D9 is "a side effect inside the loop's boolean condition" (`design.md:110`). That is a style point about audited A–K code. Fixing it costs a new public `Installer.remove(relative)`, a new `expose_to_claude`, test churn, and a larger D11 audit surface.
  - It also costs safety. `retire_command` can only touch `.claude/commands/{name}.md`. A generic `remove(relative)` is exactly the kind of API a later change could call with an owner path. That would let adoption reach a non-shipped link, the case I2 exists to rule out.
  - If D9 stays, `remove` must call `self.parents(relative)` before `permit`, as every other caller does (`:90`, `:121`, `:170`, `:208`). The design does not say so (`design.md:108`). That check is what keeps the entry's parent a real directory, which the predicate relies on (M2).
- **`bundle_kind()` and the `--list` grouping are small and earn their place.** The grouping gives `metadata.kind` a consumer, so the field is not dead data.

### 4. Duplication Avoidance

**Assessment: Fail, on one item (C2). The rest passes.**

- **The repo's own tracked `.claude/` is a third copy of shipped text (C2).** `git ls-files .claude` lists 23 entries:
  - Copies of 9 workflows (`audit-models`, `backlog`, `design-model`, `implement-model`, `manage-sources`, `onboard`, `plan-model`, `research`, `spec-model`).
  - Copies of 3 supporting skills (`python-debugger`, `record-learning`, `toolkit-awareness`), with reference and script files.
  - Copies of the 5 agents and `ruff-format.sh`, plus `settings.json`.
  - The symlink `.claude/skills/pdf-analysis -> /home/reid/1cfe/agentic-mbse/claude/skills/pdf-analysis`.
  - The last commit to touch them is `becb459`, before the fork. Neither side changed them since, so the merge carries them unchanged.
- **What goes wrong after the merge:**
  - The tracked symlink dangles in every checkout of `main`, including the integration worktree. It is also machine-specific.
  - The 9 command copies stay a stale Claude Code registration surface inside this repo, and Items 2, 4 and 5 will not reach them.
  - `scripts/replicate_setup.sh`, now an `init` wrapper on this checkout, would adopt the `pdf-analysis` link. But it would prompt for or preserve the 9 real command files, since no manifest covers them. Preserved commands also block their Claude alias (native `installation.py:311`).
- **Recommendation:**
  - `git rm` the shipped-name entries under `.claude/{commands,skills,agents,hooks}`. Keep `.claude/settings.json`.
  - Let `scripts/replicate_setup.sh` produce the dev install, and gitignore it.
  - Record the decision as a row in `dispositions.md`.
  - If the owner wants the dev install committed, at minimum remove the dangling link, and record the rest as a known second copy.
- **Elsewhere the design removes duplication well:**
  - `MBSE_*` and the literal test lists go (I4).
  - One `is_source_checkout` replaces three checks.
  - `claude/` goes entirely (I5).
  - `reconcile.py` retires with the item, so no generator survives to drift from the tree.

### 5. Data Structure Clarity

**Assessment: Pass**

- `adaptations.yaml` has explicit fields (`id`, `file`, `old`, `new`, `count`, `why`, `origin`). Exact counts make drift fail loudly (R2).
- The `adopted` bucket holds strings, `"<relative> (was -> <old target>)"`. That matches the existing `actions` lists, which are strings too (native `installation.py:45-47`), so no new type is warranted.
- `metadata.kind` takes two values, enforced by the I7 test. It is explicit.

### 6. Route Safety

**Assessment: Concerns** (read as "what does the ownership gate let through")

- **I2 holds in today's code.** I traced every `permit` caller in the native snapshot:

  | Caller | Relative path | Derived from |
  |---|---|---|
  | `write` from `copy_tree` (`installation.py:133`) | `.agents/skills/<n>/<file>`, `.claude/skills/<n>/<file>` | bundle files (4+ parts, so never adoption-shaped) |
  | `copy_tree` (`:124`) | `.agents/skills/<n>`, `.claude/skills/<n>` (copy mode) | `skill_bundles()` |
  | `alias` (`:193`) | `.claude/skills/<n>` | `skill_bundles()` |
  | `retire_command` (`:208`) | `.claude/commands/<n>.md` | `skill_bundles()` |
  | `write` for agents (`:335`), adapters (`:321`), hook (`:340`) | `.claude/agents/<stem>.md`, `.agentic-mbse/<rt>.md`, `.claude/hooks/<h>` | `agents/*.md`, `adapters/`, hook folder |
  | `write` for the entry file (`:326`) | `CLAUDE.md`/`AGENTS.md`, only when absent | constant |
  | `write` for tool-owned templates (`cli/__init__.py:582-585`) | `modeling_project/...`, `work/...` | `TOOL_OWNED_TEMPLATES` |

  - `install-commands` (native `cli/__init__.py:691-698`) calls the same `install_assistants`.
  - `--force` changes only `permit`'s answer, not which paths reach it.
  - Retired-bundle pruning (`prune_bundle`, `:142-166`) never calls `permit`. It unlinks only manifest keys under a bundle prefix whose fingerprint still matches, and refuses any key whose parent is a symlink (`:150-157`).
  - So no current path reaches `permit` for a non-shipped `.claude/<kind>/<name>`.
  - fusion-tea's five `.agents/skills/` owner links fail the `.claude` prefix. Its own `.claude/skills/{run-goal,…}` are real directories and its own commands are never visited.
- **I2 is a convention, not a check.** It holds because of how callers are written. That is acceptable with the SC8 negative test for an unshipped name, which passes trivially today but guards a future loop over `.claude/commands/*`. Do not widen the API that could break it (M1).
- **The predicate accepts more than the old installer ever wrote (M2).** Details under Bets.

### 7. Bets & Decisions Integrity

**Assessment: Concerns**

**The brief's question on the predicate (M2).** The design writes `old = normpath(entry's parent / os.readlink(entry))` and calls it "textual; works when dangling" (`design.md:147`).

- **What the old installer actually wrote.** Every link `main`'s installer ever made is `dst.symlink_to(src.resolve())`, in both commits that create links (`f92a62a`, `cf23443`; today `src/agentic_mbse/cli/__init__.py:436`, `:464`, `:491`). `resolve()` returns an absolute path with no `.` or `..`. fusion-tea's 31 links all have that shape (`runtime-entries.txt`).
- **Is textual normalization safe here?** In practice yes, but only by luck of the population.
  - The entry's parent is a real directory: `target` is resolved (native `cli/__init__.py:390`), and callers run `parents()` first.
  - So `normpath` changes nothing for these links.
  - It diverges from the OS only when the link text itself contains `..` after a symlinked component. That is the recorded hazard (CHANGELOG 2026-10-06, "Behavior found"). In that case `is_source_checkout` stats a textual root the link does not actually point into.
- **Relative targets.** The design handles them. The old installer never made them, so handling them buys nothing and widens what gets adopted.
- **Cost of each error.**
  - A false positive unlinks an owner link. The link is not written through, and it is reported with its old target, so the owner can recreate it.
  - A false negative is today's behaviour: a prompt, or a preserved link that dangles.
  - Both costs are small. But a false positive is silent until the owner reads the report, so the predicate should accept exactly what the producer wrote and nothing more.
- **Recommendation: no normalization at all.**
  - Require `os.path.isabs(text)`.
  - Require that `Path(text).parts` contains no `.` or `..`.
  - Compare the last three parts, and check `is_source_checkout(Path(text).parents[2])`.
  - This is shorter, closes the hazard by construction, and matches the producer exactly.

**B2 (`metadata.kind`).** Likely true. Cheap to confirm, and the design already orders the probe first (R1, phase 1).

- **The spike tested tolerance, not this field.** It proved that both installed clients load a `SKILL.md` carrying an unrecognized top-level key (`skills: [missing-probe-dependency]`, `.project/active/spike-native-skill-install/findings.md:28`). It never tested a nested `metadata` map. Native `plan.md` and the native skills carry no `metadata` key.
- **Outside evidence.**
  - The Agent Skills specification defines `metadata` as an optional free-form map for custom properties ([agentskills.io specification](https://agentskills.io/specification), [spec overview](https://www.mintlify.com/anthropics/skills/spec/overview)).
  - OpenAI's bundled skill-creator uses `metadata: short-description:` inside `SKILL.md` ([skill-creator (openai/skills)](https://moltchat-agent-commons.onrender.com/wiki/skill-creator_skill_(openai%2Fskills)); [Codex Agent Skills docs](https://developers.openai.com/codex/skills)).
  - I did not verify the installed client versions against these.
- **Cost to de-risk.** One run of native `discovery_probe.py`, which makes no model turns, on a fresh install with the field, before any installer work. Allow about 10 minutes.
- **The probe's blind spot does not hurt B2.** The probe cannot see Claude's seven reference skills. But all 25 bundles carry the same field, so the 18 visible ones stand in for them.
- **Alternatives.** A top-level `kind:` key is the only option that needs no new bet, because the spike already proved both clients tolerate an unknown top-level key. `metadata` is the better-standardized home. Keep D6, and fall back to top-level `kind:` if the probe fails. D6 already calls itself reversible.

**Hidden bets the design does not state:**

- **HB1. Adaptations apply to bodies only (C1).** This is load-bearing for A6 and A11.
- **HB2. The repo's own `.claude/` is unaffected by removing `claude/` (C2).** It is affected.
- **HB3. The Claude probe reports reference skills (M3).** It does not.
- **HB4. `--dev` adds its `.gitignore` block in fusion-tea (S3).**
  - Native `_update_gitignore_for_dev_mode` is idempotent on its first line, `# Tool-owned files (managed by agentic-mbse init --dev)` (native `cli/__init__.py:78`, `:336-338`). `main`'s `init --dev` wrote that same marker (`src/agentic_mbse/cli/__init__.py:92`, `:515-517`).
  - fusion-tea's old dev-mode block (`.gitignore:17-33`, per spec-review Resolutions) was written by `main`'s `init --dev`, so it very likely carries that marker. If it does, `--dev` appends nothing in fusion-tea: no `.agents/skills/`, `.codex/agents/` or `.agentic-mbse/` lines. The tracked Codex files simply turn into absolute symlinks.
  - D12 then has no effect on the only known consumer.
  - The design should predict this in R6. It bears on the owner's mode choice. The rehearsal confirms it.
- **HB5. `reconcile.py write` preserves file modes (S5).**
  - `claude/hooks/ruff-format.sh` and `pdf-analysis/scripts/extract_page.py` are mode 0775.
  - Bundle files arrive by the merge with their modes, and overwriting an existing file keeps its mode.
  - But D2 says `write` rewrites `hooks/`. A newly created `hooks/ruff-format.sh` would be 0644.
  - `git mv` the hook, and have `check` compare modes.
  - Separately, an extracted-wheel test that unpacks with `zipfile.extractall` drops modes, so the SC6 "executable hook" assertion would fail there for the wrong reason.

**B4 and SC9, the pattern note (S2).**

- D10 appends fusion-tea's pattern note verbatim to `AGENTS.md`. Verbatim is right for "no loss". But after re-init, Codex in fusion-tea reads two conflicting instructions:
  - The shipped guide says to locate pattern docs with `get_docs_dir()`.
  - `AGENTS.md` says to use `.agentic-mbse/patterns/`, the copy "named by skills and the guide".
- **The copy matches today, but nothing will keep it current.** I checked fusion-tea's 14 manifest hashes for `.agentic-mbse/patterns/*`: all equal `main`'s `docs/patterns/` at `8f43a09` (`nsd_patterns.py`). No installer refreshes that folder, and pruning never touches it (orchestrator-verified). So it goes stale the first time Item 4 or later edits a pattern doc.
- **The note's stated reason ends at runbook step 1.** Its reason is "versioned separately from the pinned executable runtime" (fusion-tea `MODELING_GUIDE.md:276`). Step 1 moves the pin to the merged SHA, so the resolver's docs become the current ones and the worktree copy becomes the stale one.
- **What to do.** This is a premise conflict to surface, not to resolve. The ledger row should state it and ask the owner whether to keep the note after step 1. Patch the note verbatim either way.
- **What Claude loses.** Nothing today. Claude follows the resolver, and those docs are byte-equal to the copy at the merged SHA. The design discloses this at `design.md:113`.

**Decisions.** Each of D1–D13 names a rejected alternative. D1, D2, D3, D5, D6, D7, D8 and D10 have sound reasons. D9 and D12 are the two whose cost the item does not need to pay (M1, S3).

### 8. Reader Comprehension

**Assessment: Pass**

- The design reads well once. The structure helps: Point, then a Core Concept stated in plain words ("it replaces what it made and asks about everything else"), then the decisions, then a pseudo-code predicate with a reason for each clause.
- Two small things slow a reader:
  - **"Fixed" in the handoff could be misread as settled.** D1–D13 are listed as "Fixed" (`design.md:316`). Readers who know the capture-fidelity vocabulary may take that as settled or do-not-relitigate. They are agent-grade design decisions, fixed for the plan only. One clause would say so.
  - **Appendix A mixes three kinds of `old`.** Some `old` values are verbatim strings, some are paraphrases ("`:57` read-permission sentence", A4, A7), and some are "same as A8". That is fine for a design. Say that the YAML carries verbatim strings for all of them.

---

## Issues by Severity

### Critical (must fix before plan)

- **C1. Adaptation scope is unstated, and A6/A11 also match the frontmatter.** Say that adaptations apply to the body below the frontmatter, and that `count` is a body count. A whole-file replace finds 5 and 3, not 4 and 2. Raising the counts to match would rewrite `allowed-tools` and break Claude's tool grant for `manage-sources` and `record-learning`. Measured at `8f43a09`: `manage-sources.md:5`, and `record-learning/SKILL.md`'s `allowed-tools`. *(Spec compliance; hidden bet HB1)*
- **C2. The repo's own tracked `.claude/` tree is unaddressed.** It holds 21 stale tracked copies of shipped commands, skill files, agents and the hook, plus a tracked absolute symlink `.claude/skills/pdf-analysis -> /home/reid/1cfe/agentic-mbse/claude/skills/pdf-analysis`. That link dangles in every clone after the merge. Add an Appendix B row and a dispositions row. Recommended: `git rm` the shipped-name entries, keep `settings.json`, and let `replicate_setup.sh` install and gitignore them. *(Duplication; hidden bet HB2)*

### Major (should fix)

- **M1. Cut D9.** Keep `retire_command`. Adoption already reaches it through `permit` (native `installation.py:208`). A generic `Installer.remove` widens the surface that I2 relies on, and adds audit scope to reviewed A–K code for a style point. If D9 is kept, `remove` must call `parents()` before `permit` and must stay private to `.claude/commands/<name>.md`. *(Abstraction; Route safety)*
- **M2. Narrow the legacy predicate to exactly what the producer wrote.**
  - Accept only absolute link text with no `.` or `..` parts. Drop `normpath` and relative-target handling. This closes the recorded `normpath`-after-symlink hazard by construction.
  - State in D5 that links into any agentic-mbse checkout, including other clones and worktrees, count as installer-made, as distinct from the spec's "personal fork" (`spec.md:46`).

  *(Bets; Route safety; Spec compliance)*
- **M3. Fix the SC8 and SC7 probe expectations.** Claude's catalog lists only user-invocable skills: 18 of 25 (native `remediation-discovery.json`). Expect Claude 18 plus 5 roles, and Codex 25. Verify the seven reference skills through `.claude/skills/<n>/SKILL.md` on disk. *(Spec compliance; hidden bet HB3)*
- **M4. Make the SC2 check able to fail, and audit what defines it (also product-lens design-F3).** `check` recomputes expected bytes with the same transform `write` used. So it proves that install is faithful and the list is exact, but it cannot catch a bug in the envelope code itself. Add `reconcile.py`'s envelope code to D11's audit scope. Add a recorded negative self-check: one mutated byte, one count off by one, and one extra file must each make `check` exit non-zero. A pytest is not needed, since the script is evidence tooling. *(Bets & Decisions)*

### Minor (consider)

- **S1. Commit structure for a reviewable PR.**
  - Commit the merge with a mechanical resolution: branch side for `skills/`, `agents/` and templates, and `main`'s `claude/` kept.
  - Then commit `reconcile.py write` on its own, then `git rm claude/` with the hook move, then the installer changes.
  - The PR diff against `main` then shows `claude/commands/<n>.md → skills/<n>/SKILL.md` as renames carrying only the envelope and the adaptations. That diff is the human-readable SC2 evidence. Keep similarity high: no reflow.
  - Also note that the PR carries `wrap-split`'s planning commits for other items (`research-seam-port`, the epic).

  *(Integration)*
- **S2. Pattern-note ledger row (also product-lens design-F2).** Record that the moved note conflicts with the shipped guide for Codex, and that the worktree copy stops being refreshed by any installer. Today all 14 copies equal `main`. The note's stated reason, separation from the pinned runtime, ends at runbook step 1. Ask the owner whether to keep the note after step 1. *(Bets, SC9)*
- **S3. Predict the `.gitignore` marker effect in R6, and consider cutting D12.** fusion-tea's old block likely carries the same marker line, so `--dev` would append nothing there. D12 then changes nothing for fusion-tea, and touches two tests. *(Hidden bet HB4; scope)*
- **S4. Specify the backticked-`/name` integrity test's pattern.** Exclude path-like hits. The only non-skill match in `main`'s shipped text is `` `/tmp/...` `` in `pdf-analysis` and its `extraction-details.md` (`nsd_slashrefs.py`). *(Validation)*
- **S5. Preserve modes.** `git mv` the hook instead of regenerating it. Have `check` compare modes. Do not assert the exec bit after a `zipfile.extractall` in the wheel test. *(Hidden bet HB5)*
- **S6. Drop R5's open question.** The spec now states the SC12 parity rule. *(Spec compliance)*
- **S7. Match the branch's preface spacing.** The branch writes `---\n\n<preface>\n\n` before the body. The design writes `---\n<preface>\n\n`. Either passes `check` and the native preamble test, which strips leading whitespace (native `tests/test_installation.py:389-390`). Matching the branch keeps the merge-resolution diff free of spacing noise. *(Note)*
- **S8. Old `--dev` targets also linked the four tool-owned templates.** `main`'s `init --dev` also symlinked them into `project_templates/` (`cf23443`). SC8 does not cover those links, and fusion-tea's are real files. Other old `--dev` targets would see a prompt for them under plain `init`. Record this as a known limit. *(Note)*
- **S9. Fix The Point's provenance tag (product-lens design-F1).** `design.md:26` says "confirmed with the owner at Align", but `briefs/00-align.md` does not record it, and the spec grades the reading `[INFERRED]` (`spec.md:77`). Record the confirmation in `00-align.md` or cite `spec.md:77`. *(Capture fidelity)*

---

## Answers to the orchestrator's seven attack points

1. **Legacy predicate.**
   - Textual normalization is safe for the real population, because every old link is an absolute `resolve()` path. It is unnecessary, though, and it admits relative and `..` text the producer never wrote.
   - Drop it: accept absolute, `..`-free text only (M2). Relative targets need no handling.
   - A false positive unlinks and reports an owner link. A false negative is today's prompt. Keep the predicate exact so the first case cannot happen.
   - `src/agentic_mbse` is the right checkout marker. The `--dev` check should share it, because it is the same question.
2. **Invariant I2.**
   - Verified for every current path: `init`, `install-commands`, copy mode, `--force`, and pruning (table under Route Safety). No path reaches `permit` for a non-shipped `.claude/<kind>/<name>`.
   - D9's generic `remove` is the one proposed change that weakens it (M1).
3. **B2.**
   - The spike proved tolerance of an unknown top-level key, not of a `metadata` map.
   - Outside evidence supports `metadata`: the Agent Skills spec defines it, and OpenAI's own skill-creator uses it.
   - The probe in phase 1 de-risks it in about 10 minutes, before any code depends on it.
   - The no-new-bet fallback is a top-level `kind:` key.
4. **`reconcile.py` and `adaptations.yaml`.**
   - A one-time script is the right tool, and it should retire with the item.
   - The envelope transform is correct for all 25 bundles (verified).
   - Appendix A is complete and minimal against `main`'s text. All 17 counts match the bodies, and no other Claude-only instruction remains.
   - It needs a body-only scope (C1) and a recorded negative self-check plus audit of the transform (M4).
   - `check` needs no per-file judgment once the list is reviewed.
5. **Merge topology.**
   - The code sides are disjoint. `main` changed no installer, `CLAUDE.md`, `README.md`, `pyproject.toml` or `scripts/` since the fork. The only test changed on both sides is `test_modeling_command_contracts.py`, and the design ports it.
   - `wrap-split` adds only `.project/` files.
   - The design calls out every hand-merge path: `CURRENT_WORK.md`, the spike and research files, and the contract test.
   - Missing: the repo's tracked `.claude/` (C2) and a commit structure (S1).
6. **fusion-tea side.**
   - `AGENTS.md` loses nothing for Claude today, but it creates a Codex-versus-guide conflict and a copy that will go stale (S2).
   - The rehearsal faithfully reproduces the dangling `--dev` case. The not-yet-dangling plain-`init` case is covered by the SC8 pytest, which runs with the link target both existing and dangling.
   - The runbook ordering holds. Plain `init` can run from fusion-tea's environment right after step 1, while `/home/reid/1cfe/agentic-mbse` is untouched, because adoption reads neither referent and that root keeps `src/agentic_mbse`. That removes the broken window for plain `init`.
   - `--dev` must still follow the move.
   - Step 1 needs the merged SHA on GitHub, which is the owner's push.
7. **Scope against 2 days.**
   - Cut D9 (M1) and D12 (S3).
   - Keep the extracted-wheel `cmd_init` test, since SC6 needs an installed wheel, but mind modes (S5).
   - Everything else is spec-driven and fits in about 2 days. Phase 1's probe-first ordering is right.

---

## Recommendations

1. State the body-only scope for adaptations and counts (C1).
2. Add the repo's tracked `.claude/` tree to Appendix B and the dispositions, with a recommended `git rm` of the shipped-name entries (C2).
3. Drop D9 and keep `retire_command` (M1).
4. Make the legacy predicate exact: absolute, no `.` or `..`, no normalization. Write the "other clones count" reading into D5 (M2).
5. Correct the probe expectations to Claude 18 plus 5 roles and Codex 25, with an on-disk check for the seven reference skills (M3).
6. Add `reconcile.py` to the audit scope, and record a negative self-check (M4).
7. Apply the minor items S1–S9 as the plan sees fit.

---

## Product-lens verdict

**Gate: DISPOSED (design-F1, design-F2, design-F3).** The full block is appended to `product-lens.md` ("design — 2026-10-09"). Nothing is owner-grade, so nothing forces Rework. Each finding needs a visible disposition.

- **design-F1 (provenance).** The Point tags "One place to register a skill" as "confirmed with the owner at Align" (`design.md:26`). `briefs/00-align.md` records no such confirmation. The spec grades the same reading `[INFERRED]`, "agent-grade, not settled" (`spec.md:77`). The orchestrator's brief makes the same claim (`briefs/04-design_review.md:9`). If the confirmation happened in chat, record it in `00-align.md` and cite that line. Otherwise cite `spec.md:77` and drop the parenthetical. No decision depends on it. Listed below as S9.
- **design-F2 (the runtimes split on pattern docs).** This is my S2, framed against the owner's "install them in the same way". Same disposition: the ledger row and the runbook name the two-copy outcome and give the owner the choice.
- **design-F3 (`check` certifies itself).** This is my M4. Same disposition: put the transform code in D11's audit scope. The lens's alternative also works: `check` compares `main`'s body with the installed body after stripping only the frontmatter and preface, which is independent of `write`.

The lens checked both design smells and fired neither. That matches my Stage 0 result.

---

## Resolutions

Resolved 2026-10-09 by the orchestrator. Every call is [AGENT] (orchestrator) unless it cites an owner source. Reserved gates (`briefs/00-align.md`) are respected.

- **C1** — Accept. Adaptations apply to the body below the frontmatter only; `count` is a body count. Frontmatter is governed by the envelope alone.
- **C2** — Accept, verified by orchestrator (`git ls-files .claude`: 21 tracked copies plus the absolute `.claude/skills/pdf-analysis` symlink into `claude/`). `git rm` the shipped-name entries under `.claude/` (commands, the four skills, five agents, the hook) and keep `.claude/settings.json` (and the untracked `settings.local.json`). Add `.gitignore` lines so a developer's `scripts/replicate_setup.sh` install is not re-tracked. Add Appendix B and disposition rows. Add a step to the owner's post-merge runbook for this repo: after moving `/home/reid/1cfe/agentic-mbse` to the merged `main`, run `scripts/replicate_setup.sh` so this repo's own Claude Code has the workflows again. The rehearsal checks that command on a scratch clone of the integration branch.
- **M1** — Accept. Drop D9's generic `Installer.remove`; keep `retire_command`, scoped to `.claude/commands/<name>.md`. Moving the Claude-exposure step out of the loop's boolean condition into a small named helper is allowed only if it adds no new removal surface (the helper calls `retire_command`, then `alias`).
- **M2** — Accept. The predicate accepts only absolute link text with no `.` or `..` parts, and never normalizes. D5 states that a link into any agentic-mbse checkout (other clones and worktrees included) counts as installer-made, which is how the design reads the spec's "personal fork".
- **M3** — Accept. Expect Claude's catalog to list the 18 user-invocable skills plus the 5 roles, and Codex 25; verify the seven reference skills on disk at `.claude/skills/<n>/SKILL.md`.
- **M4** — Accept. Put `reconcile.py`'s transform code in D11's audit scope. Record a negative self-check (one mutated byte, one count off by one, one extra file each make `check` exit non-zero). Prefer making `check` independent of `write`'s envelope code: compare `main`'s body with the installed body after stripping only frontmatter and preface, then applying the adaptation list.
- **S1** — Accept the commit structure (mechanical merge resolution; `reconcile.py write` alone; `git rm claude/` with the hook `git mv`; then installer changes). The PR also carries `wrap-split`'s planning commits for other items; the owner's PR description must say so.
- **S2** — Accept. The ledger row records the Codex-versus-guide conflict and that the worktree pattern copy is no longer refreshed by any installer. The runbook presents keeping or dropping the note after step 1 as an owner choice about fusion-tea's own text; it does not block the item.
- **S3** — Accept. Cut D12; record the stale `.claude/commands/` and `.claude/.tool-hashes.json` entries in the `--dev` gitignore list as a one-line follow-up, not this item's work. Predict the marker effect in R6.
- **S4–S8** — Accept as written.
- **S9 / design-F1** — Accept. The Align record now states the point's provenance exactly: stated by the orchestrator in the Align message, owner did not object, and the owner's verbatim ask supports it. Cite `briefs/00-align.md` and `spec.md:77`; drop "confirmed with the owner".

Verdict after resolutions: Revise, applied by the design author in its own session. No re-review unless the edits go beyond this list.

---

**Overall:** Revise
**Next Steps:** Record resolutions here. Then re-run `/_my_design`, or return to the design-agent session, and point it at this review to incorporate them. The reviewer does not edit the design. C1, C2 and M1–M4 are each one or two sentences in the design plus one Appendix B row. A re-review is not needed if the fixes are verified against this list.

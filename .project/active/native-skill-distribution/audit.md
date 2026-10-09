# Audit: Reconcile the native installer source with `main` (WRAP-SPLIT Item 1)

**Verdict:** Needs Work
**Audited:** 2026-10-09
**Branch:** `nsd-integration` (worktree `/home/reid/1cfe/agentic-mbse-nsd`)
**Commit:** `739a296` (code identical to `beceb6f`; `739a296` adds only `briefs/10-audit.md`)

---

## The Point

[NEED] (owner, verbatim, `briefs/00-align.md:19`) "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this".

[AGENT] (orchestrator's reading at Align, not objected to; `briefs/00-align.md:41`, `spec.md:77`) One place to register a skill. One tool-neutral source tree (`skills/`, `agents/`, `adapters/`, `hooks/`, `project_templates/`) carries `main`'s current text. It is the only thing the installer reads, and `agentic-mbse init` installs it the same way for Claude Code and Codex. Items 2, 4 and 5 then land their edits once, in one place.

[NEED] (owner, `.project/backlog/epic_wrap-split.md:65-66`) fusion-tea switches over with no loss of information, and its MR-7 enforcement is intact after re-init. Its Claude side today is 31 absolute links into `/home/reid/1cfe/agentic-mbse/claude/`, which the merge deletes, so the installer must take those links over and the owner needs a rehearsed runbook.

## Summary

The work is the right work, and most of it is clean. There is one source tree. The inventory comes from that tree, with no hand list left in `src/` or `tests/`. Adoption is one small predicate inside `permit`. The shipped text was regenerated mechanically, and an independent check confirms it: I re-ran that check and mutated its input 14 ways. The fusion-tea rehearsal adopts all 31 links, loses nothing and keeps MR-7.

One thing holds certification. `init --dev`, a documented install mode whose default is both runtimes, gives Codex none of the 25 shipped skills and still reports success. The item did not cause this, and the implementer found and surfaced it. But this audit certifies the installer as it now stands (SC11). So before merge it needs either a fix or an honest, visible limitation. Everything else is advisory. The most useful advisory: the tests would not notice if two parts of the legacy predicate were removed.

## Product Judgment

**Is this the right piece of work? Yes.** It answers the owner's ask directly:

- Every workflow is now a skill bundle under `skills/`, and each records its own kind (`metadata.kind`).
- Claude and Codex both install from that one tree. Claude's entry is a relative alias to the same `.agents/skills/<n>` (`installation.py:358-368`).
- Adding a skill or role is adding a file. The SC5 test proves it on a fake data root (`tests/test_installation.py:349-373`), and the hand-list mutants M4 and M20 fail it.
- The item's code is mostly deletion. The installer grows by about 60 lines against the audited native branch (`git diff 86921f9 HEAD -- src/agentic_mbse/cli/installation.py`): the predicate, `expose_to_claude`, `report`, `is_source_checkout` and `bundle_kind`. No second removal path, registry or count was added.

**Product-lens (run for this audit; block in the appendix):** Gate BLOCKED on audit-F1, the `--dev` Codex gap. It is still true in the code (`installation.py:162-164`) and in the evidence (`evidence/rehearsal/dev-probe.json`, Codex lists only fusion-tea's own 5 skills). I agree it contradicts the point for that mode, and it is this audit's one Blocker (B1). Lens audit-F2 (README count) and audit-F3 (`epic_template.md` link) are advisories 3 and 7 below.

**Structural smells that fired:**

- **A test passes only because it picks one route.** SC7's "both clients discover every workflow" is green only because every discovery probe used plain `init`. The `--dev` tests check that files exist, not that either client discovers them (`tests/test_cli.py:415-462`). This escalates into B1.
- **A baseline keeps behaviour that works against the point.** The `--dev` tests require each bundle file to be an absolute link (`tests/test_cli.py:421-424`, `tests/test_installation.py:181-183`). That is the shape the rehearsal ties to Codex listing nothing. This also escalates into B1.
- **Two representations kept in sync by hand.** `README.md:25` hard-codes "15 modeling workflows and ten supporting skills". Advisory 3.

**Earlier lens blocks for this item:** none is open. spec-F3 was fixed, and design-F1 and F3 are resolved in the code and the design. design-F2 (Codex and Claude read different pattern-doc copies after re-init) is still true in outcome. It is presented to the owner in the runbook's last section and the ledger, as designed.

**The orchestrator's accepted follow-ups.** I challenge one and accept four:

- **Challenged: `--dev` hides every shipped skill from Codex.** This is B1.
- **Accepted: the wheel omits `docs/syside/python/v0.8.4/syside/`.** No shipped instruction names that folder. The syside role names only `api/`, `automator/` and `examples/` (`agents/syside-expert.md:15-18`). The strict xfail keeps the gap visible.
- **Accepted: the second-run report lists unchanged files as Updated.** This is cosmetic, and the runbook verifies by `git status` instead.
- **Accepted: this repo's tracked init scaffold is stale.** The design scoped it out (R7).
- **Accepted: `--dev`'s `.gitignore` list still names `.claude/commands/` and `.claude/.tool-hashes.json`** (`cli/__init__.py:53`, `:57`). These are dead lines and they do no harm.

**Owner-reserved items** are presented, not decided:

- The install mode is in `fusion-tea-runbook.md` step 3. It shows both modes' observed effects and labels its recommendation of plain `init` agent-grade.
- The pattern note is in the runbook's last section, "Your choice, does not block".
- Nothing here merges, pushes or writes to fusion-tea.

## Blockers

**B1. `init --dev` leaves Codex with no shipped skills, and says nothing about it.**

- **What happens.** Under `--dev`, `Installer.write` makes every bundle file an absolute link into the source checkout (`installation.py:162-164`, called per file from `copy_tree` at `:184-193`). Codex lists none of those skills. In the dev rehearsal, Codex's catalog held only fusion-tea's 5 own skills (`evidence/rehearsal/dev-probe.json`); under plain `init` it held all 25 (`plain-probe.json`). Claude still sees the skills through its relative alias.
- **Why it blocks.** The default is `--assistant both`, and the command exits 0. Its closing message tells the user to "Run /onboard in Claude or $onboard in Codex" (`cli/__init__.py:641`), a skill Codex cannot find under `--dev`. README's `--dev` paragraph (`README.md:49`) carries no caveat. The owner asked that both runtimes install the same way (`briefs/00-align.md:19`). The spec says SC6 "requires `--dev` to work either way" (`spec.md:99`). SC11 makes this audit certify the installer as it now stands, so a defect inherited from the native branch is in scope here.
- **What is not at fault.** The item did not cause this: native `86921f9` links the same way. The implementer found it, recorded it (`rehearsal.md` found case 1) and gave the owner the evidence (runbook step 3). Plain `init`, the recommended mode for fusion-tea, is unaffected.
- **Impact if left as is.** Anyone who runs `init --dev` and uses Codex gets no modeling workflows in Codex, and no warning. That includes fusion-tea if the owner picks `--dev` at runbook step 3.
- **What clears it (either one):**
  - (a) Fix `--dev` so Codex discovers the bundles. Prove it with the discovery probe on a fresh `init --dev --assistant both` target.
  - (b) The owner records the fix as deferred, and the limitation is stated where users meet `--dev`. That means README's `--dev` paragraph, plus a notice from `init --dev` when Codex is selected that does not tell the user to run `$onboard` in Codex. File the fix as a follow-up.
  - Either way, a targeted re-check of this finding is enough. A full re-audit is not needed.

## Advisory

Ranked by importance. None of these blocks certification.

1. **Tests would not notice if two parts of the legacy predicate were removed.** The code is correct; I checked both cases directly (`.orchestrate-logs/audit-scratch/m1_demo.py`).
   - **The `..` check (mutant M1).** The `..` rows use `{old}/x/../claude/...` (`tests/test_installation.py:469`, `:543`), but no folder `x` exists. So the OS cannot resolve `{old}/x/../src/agentic_mbse`, and the checkout-root check rejects the link before the `..` check matters.
   - **The name-mirroring check (mutant M7).** No row points a shipped entry at a different name inside a checkout's `claude/` folder, so dropping the name comparison (`installation.py:55`) passes the whole suite.
   - **Impact:** invariant I3 can quietly regress. A future edit could adopt, without a prompt, a link the old installer never wrote.
   - **Fix:** create `{old}/x/` in both fixtures, and add a `{old}/claude/commands/<other-name>.md` row that must not be adopted.
2. **The envelope drops `main`'s `skills:` frontmatter key, and with it the only record of which supporting skills 8 of the 15 workflows use.**
   - **The affected workflows:** `audit-models`, `design-model`, `implement-model`, `orchestrate-modeling`, `plan-model`, `quick-model`, `review-model` and `spec-model` name supporting skills only in that key, never in their bodies (`.orchestrate-logs/audit-scratch/skills_key.py`).
   - **Where it comes from:** the drop is inherited from the native branch's envelope, and SC2 allows it as a frontmatter change. An earlier native build carried the mapping as a body line ("Supporting skills: …"). The rehearsal's provenance check flagged that line in fusion-tea's copy as old tool text (`rehearsal.md` § B4), so fusion-tea's agents lose it at re-init. No design or review records why it was dropped.
   - **What I did not check:** whether Claude Code acts on `skills:` in command frontmatter on `main`.
   - **Impact:** agents may not consult the supporting skills a workflow was written to use.
   - **Fix:** the owner decides whether the mapping should survive, for example as one reviewed body line per workflow.
3. **`README.md:25` hard-codes the inventory: "all 15 modeling workflows and ten supporting skills".** Adding a skill makes it wrong, against `CLAUDE.md`'s "Nothing else changes". Plan 8.1 removed the same counts from CLAUDE.md for this reason. Drop the numbers or point to `install-commands --list`.
4. **Adaptation A1 is acceptable as a runtime adaptation, but its wording writes the same context into two files.** `skills/onboard/SKILL.md:83` tells onboard to put the system, domain and goals into both `modeling_project/OVERVIEW.md` and the entry file. The installer's own entry files already point to `OVERVIEW.md` (`installation.py:389`), so the context only needs to live there. As written, a target ends up with two copies to keep in sync. Consider wording that writes `OVERVIEW.md` and has the entry file point to it.
5. **`installation.py` parses frontmatter three different ways.**
   - `bundle_kind` splits by lines (`:25-35`).
   - `render_agent` (`:292`) and `register_codex_agents` (`:329`) use `split("---", 2)`. That form breaks on a `---` inside a value, which plan 2.2 warns against.
   - `bundle_kind` also raises `AttributeError`, not its documented `ValueError`, when `metadata:` is present but not a mapping.
   - **Fix:** one small helper would serve all three. That fits the owner's ask to simplify.
6. **Four names in `cli/__init__.py` have no callers:** `get_agents_dir` (`:97`), `get_hooks_dir` (`:107`), `HASH_FILE` (`:68`) and `PROJECT_TEMPLATES` (`:48`, "for backwards compatibility"). All four predate this item, and the design kept `get_hooks_dir` on purpose. They are dead code a maintainer has to read past. Delete them in a follow-up.
7. **Adoption does not cover fusion-tea's other old `--dev` link.** `work/backlog/epic_template.md` points into the checkout's `project_templates/`, so plain `init` prompts for it (`rehearsal/plain-init1.txt`). Runbook step 4 answers it (`o`), and nothing fusion-tea wrote is lost. Extend adoption only if other targets turn out to have the same shape.
8. **Some tests name individual shipped skills and roles as fixtures.** Examples: `design-model`, `pdf-analysis`, `research`, `sysml-expert` at `tests/test_installation.py:94`, `:109`, `:174`, `:259`, `:276`, and `tests/test_cli.py:143-144`, `:279-281`. They are not inventories. Adding a skill never touches them, so SC5 and I4 hold. Renaming one of those skills will break unrelated tests.
9. **`reconcile.py check` compares decoded text, not raw bytes.** It reads with `Path.read_text` (`reconcile.py:120`), which turns CRLF into LF, so a CRLF-converted file passes. No shipped file contains a carriage return today, and the tool retires with this item, so this is cosmetic. It means the "exact bytes" wording in the design is not literally true.

## Findings Detail

### Plan completion

Phases 1–8 are complete as recorded. Each claim I spot-checked held:

- The merge, regenerate and remove-`claude/` commits are `df75d26`, `f68ae0a` and `ea64232`.
- The tree-as-inventory and adoption commits are `b961e56`, `0d01117`, `f6eab7a` and `cae6688`.
- The docs and gate commits are `ae1dc53` and `9d4901b`.
- `git ls-files .claude claude` prints only `.claude/settings.json`. `hooks/ruff-format.sh` and `extract_page.py` are mode `100755`.
- Step 8.7 is the native verdict update, which this audit makes per the brief.

No placeholder, TODO or partial implementation was found in the changed files.

The deviations are recorded in the plan and none changes a decision:

- `main` moved to `06ac41d`.
- The mypy baseline is 101, not 91.
- `_get_data_root` now raises instead of falling back.
- The text-property tests live in a new file.
- The orchestrator made the Phase 4–8 commits from saved steps.
- The report-once change was added.

### Spec conformance

- **SC1: verified.** I reproduced the inventory (`git diff --name-status 88e2489 06ac41d -- claude project_templates docs/patterns`): 11 workflows, 5 supporting skills, 3 templates and 2 pattern docs. `dispositions.md` has the generated rows, the hand rows and the `main` test whose contract the envelope changes (`test_modeling_command_contracts.py:72`).
- **SC2: verified.** On a fresh `both` install of HEAD, `reconcile.py check --main 06ac41d` reports 55 files compared and 0 mismatches. The recorded negative self-check holds when re-run, and 11 further mutations fail it too (Mutation results). A1 was reviewed and is accepted as an adaptation; see advisory 4 for its wording.
- **SC3: verified.** Both adapters carry the continuity and independent-review rules (`adapters/claude.md:7`, `adapters/codex.md:7`). `tests/test_shipped_text.py:81-90` pins them.
- **SC4: verified.** The guide carries `main`'s `get_docs_dir()` text with A17 applied. `tests/test_shipped_text.py:93-97` pins it.
- **SC5: verified.**
  - The inventory is derived by the tests' own globs (`tests/helpers/shipped.py:13-15`).
  - The kind lives in the bundle.
  - The deletion guard is the reference-integrity test (`tests/test_shipped_text.py:57-72`), which adding a skill never touches.
  - The only hard-coded count left is in the README (advisory 3).
- **SC6: met as written.**
  - `claude/` is gone from the tree and from both package include lists (`tests/test_cli.py:885-891`).
  - Plain `init` installs every asset, and so do `init --dev` and an extracted wheel (`tests/test_packaged_guidance_contract.py:109-134`).
  - `--dev` is refused off a source checkout.
  - The spec's recorded intent that `--dev` "work either way" (`spec.md:99`) fails for Codex. See B1.
- **SC7: partly met.**
  - Under plain `init`, the `claude`, `codex` and `both` installs discover every workflow and role (`probe-fresh-*.json`). The catalog test checks every file of every bundle under each runtime choice and link mode (`tests/test_installation.py:59-89`). No runtime-neutral text names `.claude/` (`tests/test_shipped_text.py:75-78`).
  - Under `init --dev` with Codex selected, Codex discovers nothing, and the closing message points the user at `$onboard` (B1).
- **SC8: verified.**
  - The predicate matches the design (`installation.py:38-59`) and sits after the manifest check, before force and decide (`:117-123`).
  - Tests cover the four locations, with the referent existing and dangling, and seven never-adopted cases.
  - A mixed tree is tested through both commands.
  - The rehearsal shows `Adopted (31)` in both modes, with fusion-tea's own entries unchanged.
  - Two predicate checks are not pinned by tests (advisory 1).
- **SC9: verified.** The patch touches only `b/AGENTS.md`. `git apply --check` passed on both copies (`rehearsal/*-patch-check.txt`). The ledger rows exist, including the pattern note's conflict and refresh facts. Both passages are present after re-init (`rehearsal/*-confirm.txt`).
- **SC10: verified.**
  - Both modes were rehearsed on their own copies.
  - `MODELING_PROCESS.md` is byte-identical with both MR-7 lines in each.
  - The B4 table in `rehearsal.md` matches `*-provenance.txt`: 169 lines each.
  - The runbook covers the pin, the patch, both modes with observed effects, the prompts, verification and this repo's own step.
  - The step 1 claim holds: `git diff c37ff53 HEAD -- pyproject.toml` changes only the packaged folders.
- **SC11: met by this audit.** It covers the installer diffed against `88e2489`, the A–K checklist, the tooling and the evidence. The native verdict line is updated.
- **SC12: verified.**
  - `git merge-base --is-ancestor main HEAD` succeeds.
  - `uv run pytest tests/` gives 2166 passed, 1 skipped, 1 xfailed (the known docs gap).
  - ruff check, ruff format and mypy are clean on all nine changed files. I re-ran them. My all-extras `mypy` reports 88 errors outside the changed files, matching `lint-parity.md`.
  - CLAUDE.md's Architecture, Change Coordination and ownership sections describe the one installer, `replicate_setup.sh` and `install-commands`.
- **Owner `[NEED]`s.** No loss for fusion-tea holds, with the caveat in advisory 2. MR-7 stays intact when the owner answers `s` (runbook step 4). The harness `[NEED]`s are carried by SC3's adapter text.
- **Non-goals respected.** No new workflows or runtimes. No goal, study or research-acquire registration. No pattern-doc installation. No `--dev` gitignore tidy.

### Design conformance

The implementation follows the design.

- **D1–D4: followed.** The commit order is merge, then tooling, then `write`'s output alone, then the removal. The envelope is a text transform, and adaptations apply to the body only.
- **D5: followed.** The predicate checks exact text and the checkout root, without normalizing.
- **D6: followed.** `metadata.kind` is the field, and the deletion guard is reference integrity.
- **D7: followed.** The hook moved with `git mv` and kept mode `100755`.
- **D8: followed.** `is_source_checkout` serves the data root, the `--dev` prerequisite and adoption.
- **D9: followed.** `retire_command` is byte-unchanged from `86921f9`, and `expose_to_claude` only moves the alias step.
- **D10–D13: followed.** The patch goes to `AGENTS.md`, the audit scope matches, the rehearsal re-points links at a missing `claude/`, and this repo untracks its install with the `.gitignore` block.

The invariants:

- **I1: holds.** Adoption unlinks, then installs. The referent bytes are unchanged in the tests, and the worktree was untouched by the `--dev` rehearsal.
- **I2: holds.** Every `permit` caller with a three-part `.claude/` path takes its name from `skills/`, `agents/` or `hooks/` (`installation.py:376-403`).
- **I3: holds in the code.** The tests pin only part of it (advisory 1).
- **I4: holds.** No inventory is left. Single-name fixtures remain (advisory 8).
- **I5–I9: hold.**

The report-once change adds `Installer.adopted` and `report`. That is an orchestrator refinement recorded in the plan, and it is small.

### Code integrity

- **The installer's new code is small and readable.** `permit` gained four lines. There is no god function, no parameter sprawl and no new removal API.
- **Failure honesty improved.** `_get_data_root` now raises when no data is found (`cli/__init__.py:86-89`), instead of returning a root that installs nothing.
- **The one honesty gap is B1:** a mode that succeeds silently while one selected runtime gets nothing.
- **Simplification left on the table:** advisories 5 and 6.
- **The content tooling is independent of what it checks:**
  - `reconcile.py check` shares only `show`, `tree`, `load_adaptations` and `split_frontmatter` with `write`.
  - It compares frontmatter as parsed YAML through its own transform.
  - It takes the preface from `86921f9`, not from `write`'s constant.
  - It compares each body exactly.
  - The shared frontmatter splitter is the one place a bug would hit both sides; it is ten lines and I read it.

### Mutation results

**Content check:** each case was run on a copy of a fresh install (`.orchestrate-logs/audit-scratch/check_mutations.py`, output `check-mutations.txt`).

| Mutation | `check` |
|---|---|
| Baseline | exit 0 (55 files, 0 mismatches) |
| A body byte in `onboard`; a reference-file byte; a template byte | exit 1 |
| A frontmatter description; a re-added `skills:` key; a swapped kind | exit 1 |
| A preface word; a reverted A8 adaptation | exit 1 |
| The exec bit dropped on `extract_page.py`; the hook removed; a bundle file removed; an extra bundle | exit 1 |
| A6 count + 1 (the recorded case), A8 count + 1 | exit 1 |
| An extra bundle file (the recorded case) | exit 1 (`check-negative.txt`'s three cases all reproduce) |
| A reference file converted to CRLF | **exit 0** (advisory 9) |

**Installer:** 20 mutants in a scratch export of HEAD against `test_installation.py`, `test_cli.py` and `test_shipped_text.py`. The baseline was 163 passed (`installer_mutations.py`, output `installer-mutations.txt`). 15 were killed and 5 survived.

| Mutant | Result | Caught by |
|---|---|---|
| M1 drop the `..` check (brief) | **survived** | none (advisory 1) |
| M2 normalize the link text (brief) | killed | predicate table, `x/..` row |
| M3 adopt on shape alone (brief) | killed | predicate table, plain-root row |
| M4 re-add a hand list of skills (brief) | killed | `test_added_skill_and_role_need_no_other_edit` |
| M5 break `bundle_kind` (brief) | killed | `test_list_groups_every_installed_skill_under_its_kind` |
| M6 skip `retire_command` (brief) | killed | `test_migrate_legacy_command_without_shadowing` |
| M7 drop name mirroring | **survived** | none (advisory 1) |
| M8 require the referent to exist | killed | predicate table, adopt row |
| M9 remove adoption from `permit` | killed | per-location adoption test |
| M10 report adopted entries twice | killed | per-location adoption test, skills |
| M11 `is_source_checkout` checks only `src/` | killed | never-adopted, non-checkout root |
| M12 `--dev` prerequisite always passes | killed | `test_dev_refused_without_source_checkout` |
| M13 hooks read from `claude/hooks` | killed | per-location adoption test, hooks |
| M14 accept relative link text | survived; redundant | every relative text the old installer could write contains `..`, or rebuilds to a root without `src/agentic_mbse` |
| M15 adoption before the manifest check | survived; equivalent | changes only which branch reports a link the native manifest never records |
| M16 adoption only under `--force` | killed | per-location adoption test |
| M17 drop the empty-segment check | survived; redundant | `//` text names the same checkout, and a trailing slash fails the name check |
| M18 drop the `.` check | killed | predicate table, `.` row |
| M19 `--list` ignores kind | killed | `--list` test |
| M20 agents from a hand list | killed | `test_added_skill_and_role_need_no_other_edit` |

---

## Certification

**Checked:**

- The upstream spec, design and plan.
- The installer diff against `88e2489` and `86921f9`.
- The A–K checklist: F-A to F-K all still hold in the code and CLAUDE.md.
- The tests.
- `reconcile.py` and `adaptations.yaml`: `check` re-run, with 15 content mutations.
- Every evidence file named in the brief.
- The full pytest suite, plus ruff and mypy on the changed files.
- 20 installer mutants.
- An independent product-lens pass.

**Marked:** only the native audit's verdict line (`.project/active/native-skills/audit.md:3`), as the brief directs.

**Not marked:** per the brief, I left the plan, spec, epic, `CURRENT_WORK.md` and `product-lens.md` untouched; the orchestrator owns those writes. Once B1 clears, these are verified and can be marked:

- Plan Phases 1–8, with 8.7 done by the verdict-line edit.
- Spec SC1–SC5, SC8–SC12.
- SC6 and SC7 after B1's re-check.

The lens block in the appendix is ready to append to `product-lens.md`.

**Not checked:**

- **Discovery.** I did not re-run the Claude or Codex discovery probes, because the sandbox gates `git init` for this stage. Discovery results come from the recorded JSON (`probe-*.json`, `rehearsal/*-probe.json`).
- **The fusion-tea rehearsals.** I did not re-run them. I read their raw outputs and spot-checked counts, confirmations, patch checks and prompts.
- **Workflow body text** beyond the adaptation list. It is out of scope, because SC2 makes it mechanical.
- **Claude Code's handling of `skills:`** in command frontmatter on `main` (advisory 2).
- **Platforms.** Behaviour off Linux, and full modeling sessions in either client.
- **The runbook's step 1 `uv` commands** in fusion-tea's environment.
- **Whole-repo lint.** I ran ruff and mypy on the changed files only, and relied on `lint-parity.md` for the rest.

---

## Appendix: product-lens verdict block (for the orchestrator to append to `product-lens.md`)

```
## audit — 2026-10-09 — rev nsd-integration @ beceb6f
Epic: WRAP-SPLIT

Point (re-derived): Every shipped workflow, supporting skill and expert role is a skill that lives once, in one tool-neutral source tree. Both Claude Code and Codex install it the same way and can use it, so adding a skill is one act in one place. fusion-tea switches over with no information lost, and its MR-7 enforcement is intact after re-init.   [source: `briefs/00-align.md:19` (owner-verbatim); `00-align.md:24` rename (owner-verbatim, a permission only); `00-align.md:21-23` decisions 1–3, including :23 "so both runtimes install the same way from the source and live editing continues" (agent/ratified); `.project/backlog/epic_wrap-split.md:65-66` (owner); `harness-right-size/requirements.md` [NEED]s (owner); `CLAUDE.md:215` and "Init File Ownership", `README.md:3`, `docs/source-index.md:7` (INHERITED). No `.project/adr/`, no `.project/product/`.]

Falsifier: (1) `init` in any documented mode with `--assistant both`, and one runtime's listing lacks a shipped skill the other lists; (2) adding `skills/x/SKILL.md` requires editing another file for install, listing, tests or docs to stay true; (3) re-init over a fusion-tea copy removes target-owned text with no recorded home, or `MODELING_PROCESS.md` ends without its two MR-7 lines.

Findings:
- audit-F1 [DO] `init --dev` does not serve both runtimes: Claude discovers 18 shipped skills, Codex 0 (`evidence/rehearsal/dev-probe.json`). Under `--dev`, `Installer.write` links each bundle file by absolute path (`installation.py:162-164`, from `copy_tree` `:188-193`). `--dev` is documented with no Codex caveat (`README.md:47-49`) and was the owner-ratified switch-over route (`00-align.md:23`). Tests check links exist and pin the absolute per-file shape (`tests/test_cli.py:421-424`, `:432-434`; `tests/test_installation.py:181-183`); nothing checks Codex discovery under `--dev`. Surfaced honestly (rehearsal.md found case 1, plan.md:832, audit-scope.md:27) but parked; "predates this item" cannot clear an owner-grade contradiction. — `00-align.md:19` (owner-verbatim) — disposition: BLOCK. Clears by owner disposition (e.g. DEFERRED with the limitation stated at `README.md:47`) or FIXED (a dev-mode Codex discovery probe shows 25).
- audit-F2 [DON'T] `README.md:25` hard-codes a second inventory ("15 modeling workflows and ten supporting skills"); adding a skill makes it wrong, against `CLAUDE.md:215`. — `CLAUDE.md:215` (INHERITED) serving `00-align.md:19` — disposition: DISPOSE (drop the count or point to `install-commands --list`).
- audit-F3 [DON'T] Adoption covers only `.claude/{commands,skills,agents,hooks}/` (`installation.py:17`, `:46`); fusion-tea's old `--dev` link `work/backlog/epic_template.md` is not adopted, so plain `init` prompts (`rehearsal/plain-init1.txt:4`). No information lost; runbook step 4 answers `o`. — design Non-Goals assumption, disproved by rehearsal.md found case 3 (AGENT) — disposition: DISPOSE.

Smells fired: 6 (test passes by selecting one route) on audit-F1: SC7 discovery holds only because probes use plain `init`; SC6's `--dev` is checked by files on disk (`tests/test_cli.py:415-462`). 5 (baseline preserves behaviour against the point) on audit-F1: the `--dev` tests enforce the per-file absolute-link shape. 1 (two representations synced by hand) on audit-F2. 3 (special category exempts a case) on audit-F3, and on the strict xfail `DOCS_GAP` (`tests/test_packaged_guidance_contract.py:39-43`), disposed AGENT: no shipped instruction names the missing `docs/syside/python/v0.8.4/syside/`. 4 not fired: adoption reads only link text and the checkout root (`installation.py:57`).

Checked, no finding: one tree, one act (`installation.py:353-379`, `:290-310`, `:393-396`; `cli/__init__.py:654-663`; `tests/helpers/shipped.py:13-15`; `tests/test_installation.py:349-373`); no `claude/` and no `MBSE_*` in `src/`. No loss for fusion-tea: only the `record-learning` example is consumer-flavoured, present on both sides; both target-owned passages have ledger rows and a patch into `AGENTS.md`; provenance finds no other target-owned line removed. MR-7: `MODELING_PROCESS.md` byte-identical with 2 MR-7 lines in both modes, provided the owner answers `s` (runbook step 4 rules out `S`/`O`).

Resolves:
- design-F1: FIXED — authority: AGENT — basis: `design.md:27` carries the reading as agent-grade, citing `00-align.md:41` and `spec.md:77`.
- design-F3: FIXED — authority: AGENT — basis: `reconcile.py` `check` applies adaptations through its own `Checker.expected` (`:100`), separate from `write`'s `envelope`/`adapt` (`:293`, `:310`); `audit-scope.md:13` puts both in audit scope.
- design-F2: still true in outcome (Claude follows the guide's resolver, Codex the `AGENTS.md` note); remains an owner choice parked in the runbook and ledger.

Gate: BLOCKED (audit-F1); DISPOSE (audit-F2, audit-F3)
```

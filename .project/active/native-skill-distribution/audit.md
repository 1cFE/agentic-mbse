# Audit: Reconcile the native installer source with `main` (WRAP-SPLIT Item 1)

**Verdict:** Certify (after the 2026-10-09 Phase 9 re-check: `init --dev` now gives Codex every shipped skill, and product-lens audit-F1 is FIXED on the owner's direction; the first pass was Needs Work on B1, the first re-check Certify)
**Audited:** 2026-10-09 (first pass, targeted re-check, and Phase 9 re-check)
**Branch:** `nsd-integration` (worktree `/home/reid/1cfe/agentic-mbse-nsd`)
**Commit:** first pass `739a296` (code identical to `beceb6f`); re-check `46a45a1` (code identical to `2c65dda`; `46a45a1` adds only `briefs/12-audit-recheck.md`); Phase 9 re-check `2e320e1` (code identical to `d314b6e`; `2e320e1` adds only `briefs/14-audit-recheck-dev.md`)

---

## Re-check: Phase 9 (`--dev` folder links), 2026-10-09: Certify

**Result.** The fix holds. A fresh `init --dev` now gives Codex all 25 shipped skills, the same as plain `init`, under every `--assistant` choice and both link modes. The installer never deletes an owner file to make the link. The B1 warning is gone. No blockers; five advisories, none about the fix's correctness.

**Authority for resolving audit-F1.** [OWNER] 2026-10-09, in chat: the owner asked for a spike ([OWNER-VERBATIM] "can you run a spike to figure it out? … would symlinking directly to .claude in the same repo work?"), then answered "yes" to the orchestrator's "Want me to run the fix?". So the disposition is fix, not defer.
- This supersedes the first re-check's open owner decision and its warning table below.
- The link shape is the orchestrator's choice [AGENT]: `.agents/skills/<n>` links straight to the checkout, not through `.claude/skills/`. D14 records the chain as the rejected alternative. The spike answers the owner's question: the chained shape also lists in Codex.

**Scope.** `b2ff7cf..d314b6e`: `a42c4c9` (code, tests, README), `5b93cac` (evidence, rehearsal re-run), `d314b6e` (plan Phase 9, design D14, spec status). My scripts and outputs are in `.orchestrate-logs/audit-scratch/p9/`.

### 1. The fix, run independently

I ran `init --dev` into fresh targets and probed each with `.project/active/native-skills/discovery_probe.py` (Claude Code 2.1.296, codex-cli 0.160.0; `p9/probe_all.py`, outputs `p9/*.probe.json`). `git init` is gated for this stage, so each target got a copy of a pristine `git init` `.git`. One extra target had no `.git` of its own.

| `init --dev` target | Claude skills | Claude roles | Codex skills | Errors |
|---|---|---|---|---|
| `--assistant both` | 18 | 5 | 25 | none |
| `--assistant codex` | 0 | 0 | 25 | none |
| `--assistant claude` | 18 | 5 | 25 | none |
| `both`, no `.git` of its own | 18 | 5 | 25 | none |
| `both --link-mode copy` | 18 | 5 | 25 | none |

- The names equal `evidence/probe-dev-folder-links.json` exactly. For the `codex` target, the Codex names do.
- Each choice gives the same numbers as plain `init` for that choice (`probe-fresh-*.json`). Codex sees 25 under `--assistant claude` in both modes, because `.agents/skills/` is always installed.
- On disk, in every target, each of the 25 `.agents/skills/<n>` is an absolute folder link to the checkout's `skills/<n>`. No `SKILL.md` under `.agents/skills/` is a file link. No "Copied" line printed. The Next steps match plain `init`.

### 2. The code

- **`link_directory` is a true generalization.** The diff removes only the line that built the link text (`installation.py:232-263`). `expose_to_claude` now passes `os.path.relpath(shared, destination.parent)` (`:395`), the same text `alias` built. Nothing outside the staged native inputs still calls `alias`.
- **The fallback never loses owner files and never makes per-file links.**
  - `install_dev_bundle` (`:365-383`) falls back only when the destination is a real folder. It copies with `copy_tree` and no `dev` flag.
  - A link or file that `permit` refused is not retried, so the owner is asked once. I checked this with a `decide` that counts its calls.
  - Under `--force`, an added owner file still survives, and the folder is copied, not linked.
- **The printed reason is not accurate in every case that reaches it.** See advisory 1.

**Transitions** (`p9/transitions.py`). For the per-file case I exported the pre-fix code (`b2ff7cf`) to scratch and let it make a real per-file `--dev` install.

| Transition | Result |
|---|---|
| Fresh, each assistant, both link modes | Folder links (probe table above) |
| Over a real per-file `--dev` install made by `b2ff7cf` | Every bundle becomes one folder link. No per-file manifest keys remain. The old source tree is untouched. The Claude alias is unchanged. |
| The same, with an owner file added in one bundle | That bundle is copied plainly. The owner file is kept, no file links remain, and one "Copied" line prints. |
| Over a plain install | Folder links, no prompt |
| Plain `init` over `--dev`; `install-commands` over `--dev` | Real copies, no prompt. Nothing is written through the link: the worktree's `git status` stays clean. |
| `--assistant codex --dev`, then `both --dev` | Folder links; the second run adds the relative Claude alias with no prompt |
| `--dev --link-mode copy`, a second run, then symlink mode | Claude's copy holds per-file links, which Claude lists (probe above). Symlink mode then makes the alias the relative folder link, with no prompt. |
| A second `--dev` run | No prompt, no "Copied" line, links intact |
| The owner's own folder link at `.agents/skills/<n>` | Preserved with one prompt. No Claude alias for it, the same as plain `init`. |
| `--force --dev` with an owner file in a bundle | Copied, not linked; the owner file is kept |

### 3. Mutations

I ran `p9/mutations.py` on a scratch export of HEAD, against `test_installation.py`, `test_cli.py` and `test_shipped_text.py`. The unmutated baseline was 174 passed. Each mutant was reverted after its run, and the export was checked byte-equal to HEAD at the end. 12 of 14 were killed.

| Mutant | Result | Killed by |
|---|---|---|
| P1 `--dev` links per file again | killed (13 tests) | the property test and the transition tests |
| P2 no fallback: an unowned folder returns False | killed | `test_dev_copies_a_bundle_folder_holding_owner_files` |
| P3 the fallback makes per-file links | killed | the same test |
| P4 `link_directory` skips the ownership check | killed | the same test, `test_empty_owner_directory_survives_copy_to_link`, `test_copy_link_dev_transitions_preserve_owner_additions` |
| P5 drop the manifest key cleanup | killed | `test_dev_over_per_file_dev_install_links_each_folder` |
| P6 relative link text for the `--dev` folder | killed | the property test |
| P7 the fallback prints nothing | killed | the owner-files test |
| P8 `--force` lets the link replace an unowned folder | killed | the owner-files test, `force=True` |
| P9 empty sub-folders count as owned | killed | the empty-owner-directory test |
| P10 the Claude alias gets absolute link text | killed (9 tests) | the catalog and adoption tests |
| P11 plain `copy_tree` writes through a `--dev` folder link | killed | `test_plain_init_over_dev_copies_every_bundle` |
| P12 the fallback also retries a link or file `permit` refused | **survived** | none. Same outcome noninteractively; an interactive owner would be asked twice (advisory 2). |
| P13 `--dev` skips the Claude alias | killed | the property test |
| P14 a `--dev`-only line printed before "Next steps:" | **survived** | none. The Next-steps test compares only the text from "Next steps:" on (advisory 2). |

### 4. The tests

The tests pin the property Codex needs, and they take it from the tree (SC5, I4 hold).
- `test_dev_links_each_bundle_folder_to_the_checkout` (`tests/test_cli.py:424`) runs every bundle in `skills/` (`tests/helpers/shipped.py`), under `claude`, `codex` and `both`, in both link modes. It asserts one folder link that reads exactly `<checkout>/skills/<n>`, its `link:` manifest entry, no per-file manifest keys, and no `SKILL.md` file link.
- The fallback test checks that every file of a blocked bundle is a real file (`tests/test_installation.py:214`).
- Fixtures pick bundles by kind from the tree (`WORKFLOW`, `OTHER_WORKFLOW`), not by name.
- No test pins per-file links under `.agents/skills/` any more. The per-file shape survives only in Claude's copy mode, which Claude lists.
- The suite still runs no live client, as before (advisory 4).

### 5. Evidence and docs

- **The rehearsal re-run.** I compared every file in `evidence/rehearsal/` with the first run's outputs (`.orchestrate-logs/rehearsal/prev-outputs/`).
  - Plain mode: every file is byte-identical except the probe's Claude Code version (2.1.295 → 2.1.296).
  - Dev mode: Codex lists 30, the 25 shipped plus fusion-tea's 5. Claude lists 24 skills and 5 roles. No errors. Adopted 31, one prompt, no "Copied" line, and git status is identical after the second run.
- **The `provenance.py` extension does not weaken the check.** I ran the current script and a copy with the folder expansion turned off, on both re-run copies.
  - Current script, dev mode: 39 files checked, 129 lines flagged. The output is byte-identical to the first run's `dev-provenance.txt`, and matches plain mode.
  - Expansion off, dev mode: 8 files, 7 lines. Without the extension the check was blind.
  - Plain mode: 129 lines either way.
  - The expansion reads only the real files of the pristine folder, as the per-file listing did before.
- **Runbook step 3 and step 5 match the raw outputs.**
  - Plain: 34 `M` (26 under `.agents/skills/`), plus `?? .agentic-mbse/claude.md`, 2 prompts.
  - Dev: 7 `M`, 31 `D`, 25 untracked folder links, 2 `T`, `?? .agentic-mbse/claude.md`, 1 prompt, the hook a link.
  - The install mode is still the owner's choice. The recommendation is labelled agent-grade and no longer cites the Codex gap. It now rests on committing machine-specific links.
  - One stale count, in the "This repo" section: advisory 3.
- **The other docs match the code.**
  - `README.md:47` is accurate against the code and the probes.
  - D14 and plan Phase 9 match the code. Plan 9.3's claim holds: the Next-steps line is byte-equal to `783b00e~1`'s.
  - `audit-scope.md` drops the follow-up and records the fix. The `lint-parity.md` numbers hold (§6).
  - `spec.md` changed only its status. SC6 and SC7 now hold under `--dev` too.
- **Leftovers.**
  - `DEV_CODEX_WARNING` is gone from `src/` and `tests/`.
  - The only now-false live claim is the native item's verdict line (advisory 3).
  - Plan Phase 7's notes and its "Audit fixes" section are dated, and the latter is marked superseded. This file's earlier sections are kept as written.

### 6. Gate

- `uv run pytest tests/`: 2177 passed, 1 skipped, 5 deselected, 1 xfailed.
- ruff check and ruff format --check are clean on the 9 files `lint-parity.md` lists. Repo-wide, ruff check reports 118 (recorded 118) and ruff format 77 files (recorded 77).
- mypy in the baseline's no-extras environment reports 98 (recorded 98), and 88 in the all-extras worktree (recorded 88). None are in `cli/__init__.py` or `cli/installation.py`.
- This re-check changed no tracked file except this one and `product-lens.md`.

### Advisories (Phase 9)

1. **The "Copied … instead of linking it" line can be wrong.** `install_dev_bundle` prints it whenever `copy_tree` returns, and `copy_tree` returns True even when it wrote nothing (`installation.py:377-382`). Three cases reach it (`p9/transitions.py`):
   - **An empty real folder at `.agents/skills/<n>`.** The line says the installer "does not own everything in that folder", but the folder held nothing. The copy fills it with installer-owned files, so the next `--dev` run links it anyway.
   - **Every file in the bundle owner-edited, without `--force`.** Nothing is copied, and each file also prints "Preserving".
   - **A per-file `--dev` folder whose manifest was deleted.** The file links stay, so Codex lists none of those bundles, while the report says "Copied" for all 25. This needs the pre-fix `--dev` shape and a lost manifest together, so it is unlikely.
   - **Impact:** a reader trusts a line that misstates what happened.
   - **Fix:** print the line only when a file was written, and say "kept" otherwise. Linking an empty folder would also remove the first case.
2. **Two behaviours are not pinned by tests (mutants P12 and P14).**
   - **No retry after a refusal.** The guard at `installation.py:375-376` keeps a link or file that `permit` refused from being retried as a copy. Nothing tests it. Dropping it would ask an interactive owner twice about one entry.
   - **The Next-steps test is too narrow.** `test_next_steps_are_the_same_with_and_without_dev` (`tests/test_cli.py:467`) compares only the text from "Next steps:" on. The old warning printed above that block, so a returned warning would pass.
   - **Fix:** add a test with a `decide` that counts its calls. Compare the whole closing output, not just the Next-steps block.
3. **Two records still describe the old state.**
   - `.project/active/native-skills/audit.md:3`, the native item's verdict line, says "`init --dev` now warns that Codex cannot see its linked skills and the fix is a follow-up". Both halves are now false. A later agent would read it as a live Codex gap.
   - `evidence/fusion-tea-runbook.md:89` says the clone's pytest stayed at 2166. The re-run shows 2177 (`rehearsal/clone-pytest-after.txt`; `rehearsal.md:101` has it right).
   - **Fix:** amend the verdict line to cite Phase 9, and update the count. I left both alone, because the brief limits my writes to this file and `product-lens.md`.
4. **Codex discovery under `--dev` rests on an undocumented Codex rule.** Codex 0.160.0 lists a skill whose folder is a link and skips one whose `SKILL.md` is a file link. That rule is known only from the spike, observed from outside. B1 was this kind of rule failing silently, and the default suite runs no client.
   - **Fix:** keep the versions named in the evidence. Re-run `discovery_probe.py` on a `--dev` target when the Codex version in use changes. This is lens smell 4.
5. **A redirected `.agents/skills` is reported twice (cosmetic).** When `.agents/skills` is itself a link, a bundle that exists behind it prints "Skipped … parent … is not a real directory" twice. It is also listed twice under Skipped. The cause: the fallback calls `parents()` a second time, through `copy_tree` (`installation.py:372-377`). Nothing is written, and the outside folder is untouched.

### Product-lens (Phase 9 re-check)

The block is appended to `product-lens.md`.
- **audit-F1: FIXED.** The authority is the owner's, as quoted above. The lens's own clearing condition holds: a dev-mode Codex probe shows 25.
- **Smells 5 and 6 on audit-F1 no longer fire.** The per-file baseline tests are gone, and the `--dev` route is pinned by the property Codex needs.
- **New, all DISPOSE:** audit-F4 (advisory 1), audit-F5 (advisory 3) and smell 4 (advisory 4).
- **Gate:** DISPOSED. No BLOCK remains in the ledger.

### Certification (Phase 9 re-check)

**Checked:**
- The Phase 9 diff and the code around it.
- Five fresh `--dev` probes.
- 14 transitions and edge cases on the live code, including three over real installs made by the pre-fix code.
- 14 mutants.
- The tests, the rehearsal outputs against the first run, `provenance.py` with and without its extension, the runbook, README, D14, plan Phase 9, `audit-scope.md` and `lint-parity.md`.
- The full gate and an independent product-lens pass.

**Marked:** this file's verdict line and the product-lens block.

**Not marked** (the orchestrator owns these writes); verified and ready to mark:
- Plan Phase 9 (already checked off).
- Spec SC6 and SC7, which now hold under `--dev` for Codex too.
- `CURRENT_WORK.md`: certified, with audit-F1 resolved.
- The native item's verdict line (advisory 3).

**Not checked:**
- **Probes on targets made by `git init`.** Mine used a copied pristine `.git`, plus one nested target. Both agree with the orchestrator's probe of a `git init`ed target.
- **An interactive run.** The ask-once claim rests on a counting `decide` and on reading the code.
- **Other versions and platforms.** Codex versions other than 0.160.0, and platforms other than Linux.
- **A fresh rehearsal.** I compared the rehearsal's outputs and re-ran `provenance.py`, but did not re-run `rehearse.sh`.

---

## Re-check, 2026-10-09: Certify

*Superseded in part by the Phase 9 re-check above. The owner chose the fix, so the warning, its table and the open owner decision below no longer describe the code.*

**Result.** B1's defect is fixed. `init --dev` no longer fails silently for Codex, and the product states the limitation where users meet `--dev`. The six advisories the orchestrator chose to fix are fixed, and I verified each one. Where the code was meant to behave the same, it does: I compared it byte for byte.

**One decision is left, and it is the owner's.** It concerns whether to defer real `--dev` support for Codex. No code work is outstanding for it.
- The orchestrator recorded that deferral as agent-grade (`briefs/11-audit-fixes.md`).
- The product-lens ledger accepts only an owner disposition for a BLOCK, so it keeps audit-F1 open until the owner rules.
- `_my_pre_pr` and `_my_close` enforce that. The merge gate, where the owner rules, is owner-reserved anyway.

**Scope.** Only what changed: `783b00e`, `728a4fe`, `b5fb2ed`, `7cf6c41` and `2c65dda`.

**Checks.**
- The full suite on HEAD gives 2174 passed, 1 skipped, 1 xfailed.
- ruff check and ruff format are clean on the 9 changed files.
- mypy reports nothing in the changed files. Its all-extras total is unchanged at 88.

### B1: cleared

- **The warning and the next step behave as stated.** I ran `init` for each runtime, with and without `--dev`, twice each (`.orchestrate-logs/audit-scratch/b1_matrix.py`, output `b1-matrix.txt`):

  | Install | Warning | Next step 1 |
  |---|---|---|
  | plain `init`, `claude` / `codex` / `both` | none | "Run /onboard in Claude or $onboard in Codex …" |
  | `--dev`, `claude` | none | same |
  | `--dev`, `codex` | printed | "Re-run init without --dev, then run $onboard in Codex …" |
  | `--dev`, `both` | printed | "Run /onboard in Claude … (Codex cannot see $onboard under --dev)" |

  The second run prints the same lines.
- **The warning's advice works.** The warning text (`cli/__init__.py:65-69`) says to use plain `init` for Codex. A plain `init --assistant codex` over a `--dev` Codex install replaced all 31 links with real files, with no prompt.
- **The README sentence is accurate.** `README.md:47` says Codex does not list skills installed as such links, says to use a normal install for Codex, and says `init --dev` warns. That matches the evidence (`evidence/rehearsal/dev-probe.json`). The evidence is for Codex 0.160.0, which the code comment names; the README states it without a version.
- **The test pins it.** `test_dev_warns_that_codex_cannot_see_linked_skills` (`tests/test_cli.py:471`) covers all six combinations. All three mutants I aimed at it are killed:
  - warning only for `codex`;
  - warning printed but the plain `$onboard` step kept;
  - warning for every `--dev` install.
- **What stays open.** Codex discovery under `--dev` is a follow-up with a spike (`evidence/audit-scope.md`).
- **Why I clear B1 anyway.** My clearing route (b) asked the owner to record the deferral; the orchestrator recorded it instead. The harm B1 named was silent success plus a false instruction, and both are gone. The deferral itself is owner-visible at the owner-reserved merge gate, and the lens ledger holds it for the owner's word.

### Advisories fixed (1, 3, 5, 6, 8, 9)

- **Advisory 1, predicate pins: fixed.**
   - `old_checkout` now creates `x/` (`tests/test_installation.py:448`), so the `..` rows name a real checkout.
   - The predicate table and the never-adopted cases gain an "another entry's name" row (`:466`, `:525`, `:543`).
   - I re-ran the mutant set on a scratch export of HEAD (171 passed unmutated). M1 (drop `..`) is now killed by the `x/..` row, and M7 (drop name mirroring) by the `{other}` row.
   - Overall, 20 of 23 mutants are killed. The three survivors (M14, M15, M17) are the same redundant or equivalent ones as the first pass (`recheck-installer-mutations.txt`).
- **Advisory 3, README count: fixed.** `README.md:25` points to `install-commands --list` instead of counting.
   - Residual nit: `README.md:29` still says "five native expert roles", the same kind of count for roles.
- **Advisory 5, one frontmatter parser: fixed, with no behaviour change.**
   - One `frontmatter()` (`installation.py:25`) serves `bundle_kind`, `render_agent` and `register_codex_agents`.
   - I ran the old module (`739a296`) and the new one through `install_assistants` on the same data, for every runtime, link mode and `--dev` setting. All 12 installs are byte-identical, including the manifest and every report list (`parser_equivalence.py`). `bundle_kind` agrees on all 25 bundles.
   - Only the two intended changes differ. A `---` inside a frontmatter value used to raise `KeyError` and now parses. A non-mapping `metadata` used to raise `AttributeError` and now raises the documented `ValueError`.
- **Advisory 6, caller-less names: fixed.**
   - `PROJECT_TEMPLATES`, `HASH_FILE`, `get_agents_dir` and `get_hooks_dir` are gone. Nothing names them in `src/`, `tests/`, `scripts/`, `hooks/`, shipped text, `docs/`, `CLAUDE.md`, `README.md`, `pyproject.toml`, or the staged fusion-tea inputs.
   - `get_docs_dir` stays, and its I6 test passes.
   - One stale reference remains, in a finished spike's throwaway probe (`.project/active/spike-native-skill-install/installer_probe.py:41`, `cli.HASH_FILE`). It would fail if anyone re-ran it.
- **Advisory 8, sample names in tests: fixed.**
   - Samples now come from the tree. Where a test only checked that a few things exist, it now checks every bundle file or every role.
   - Tests that are about one skill keep its name, correctly: the two `orchestrate-modeling` tests and the two `syside-expert` placeholder tests.
   - Residual nit: `test_force_overwrites_agents` (`tests/test_cli.py:223`) still uses `syside-expert` as a plain sample. It is not about the placeholder, although the plan counts it among them.
- **Advisory 9, byte-exact `check`: fixed.**
   - On a fresh install of HEAD, `reconcile.py check` reports 55 files and 0 mismatches.
   - All 15 of my content mutations now fail it, the CRLF reference file included (`recheck-check-mutations.txt`).
   - The recorded negatives agree: `check-negative.txt` adds two CRLF cases, and both exit 1.

### Advisories accepted (2, 4, 7): I agree

- **2, the `skills:` key.**
  - The cited research (`.project/research/20260907-162310_native-claude-codex-skills.md:54`) records that Claude documents `skills` as subagent preloading metadata, not a command dependency loader. Codex was not a runtime on `main`.
  - So nothing a runtime acted on is lost against `main`.
  - What is lost is a written mapping, for 8 workflows, that a reader could use. The research's own `[AGENT]` line allowed removing it (`:56`). The disposition is now in `dispositions.md`.
- **4, A1.** Both runtimes see the context. Writing it to two files is a style point.
- **7, `epic_template.md`.** Runbook step 4 answers it, and nothing fusion-tea wrote is lost.

### Product-lens

The first-pass block and a re-check block are appended to `product-lens.md`. The re-check block records:

- **audit-F2:** FIXED.
- **audit-F3:** DEFERRED, agent-grade.
- **audit-F1:** still BLOCK, waiting only on the owner's disposition. The limitation is now visible and pinned; the deferral of the fix is agent-grade.

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

The sections from here to the appendix are the first pass, kept as written. The re-check above records what changed.

**B1. `init --dev` leaves Codex with no shipped skills, and says nothing about it.** *Status: cleared on the 2026-10-09 re-check (limitation now stated and pinned; the fix is a follow-up whose deferral awaits the owner).*

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

**Marked:**

- **First pass:** the native audit's verdict line (`.project/active/native-skills/audit.md:3`).
- **Re-check:** that line again, now Certify, and the two lens blocks appended to `product-lens.md`. Both briefs direct these writes.

**Not marked:** the plan, spec, epic and `CURRENT_WORK.md`, per both briefs; the orchestrator owns those writes. As of the re-check, these are verified and can be marked:

- Plan Phases 1–8 and the "Audit fixes" notes.
- Spec SC1–SC12.
- **SC7 holds for the standard install under every runtime choice.** Under `--dev` with Codex, the install no longer points the user at a skill Codex cannot see. Codex discovery under `--dev` remains a documented limitation and a follow-up, and its deferral awaits the owner (lens audit-F1).

**Not checked in the re-check:**

- External importers of the four removed names, such as sysml-codegen. They are outside this worktree, and only fusion-tea's staged inputs were searched.
- A live Codex probe of the new `--dev` install. The warning's claim rests on the first pass's recorded `dev-probe.json`.

**Not checked:**

- **Discovery.** I did not re-run the Claude or Codex discovery probes, because the sandbox gates `git init` for this stage. Discovery results come from the recorded JSON (`probe-*.json`, `rehearsal/*-probe.json`).
- **The fusion-tea rehearsals.** I did not re-run them. I read their raw outputs and spot-checked counts, confirmations, patch checks and prompts.
- **Workflow body text** beyond the adaptation list. It is out of scope, because SC2 makes it mechanical.
- **Claude Code's handling of `skills:`** in command frontmatter on `main` (advisory 2).
- **Platforms.** Behaviour off Linux, and full modeling sessions in either client.
- **The runbook's step 1 `uv` commands** in fusion-tea's environment.
- **Whole-repo lint.** I ran ruff and mypy on the changed files only, and relied on `lint-parity.md` for the rest.

---

## Appendix: first-pass product-lens verdict block (appended to `product-lens.md` at the re-check, followed by the re-check block)

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

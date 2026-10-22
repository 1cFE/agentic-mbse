# Audit: retire the copied generator rules (Phase 6, fresh reviewer)

**Date:** 2026-10-21. **Audited:** agentic-mbse `retire-subset-profile` at `1b65ecbe` (diff from `e268357f`); sysml-codegen `subset-profile-screen` at `4e037a88` (commits after `529830cf`). No code was edited.

## Verdict: Needs Work

No blocker. Every requirement R1-R9 is met and the generator's behaviour is unchanged, which I confirmed by running the suites, the byte manifest, the refusal records, the TEAx lane, the probes and dc3. The work needs a short round of fixes before the owner merges. The most important ones: L6's passing output still reads like a generation answer under `generated`; a silent wrong-count generator bug found in Phase 2 has no backlog row; and the records do not say that the copy's "omitted" findings (silent losses in models that build) are now reported by nothing.

## What I ran

- agentic-mbse `uv run pytest tests/ -q` (license sourced): 5 failed, 3567 passed, 8 skipped, 1 xfailed. The 5 failures are the 5 base IDs in `evidence/suite-baseline-agentic.md`. mypy 88 errors and ruff `src/ tests/` 118, the counts the plan records as unchanged from base; I did not re-run them on `e268357f`.
- sysml-codegen `uv run --all-extras pytest tests/ -q -rfEs` (Phase 9 command, license sourced), against this agentic-mbse branch: 8442 passed, 9 failed, 9 skipped, 124 deselected. The 9 failures are exactly the base 9 in `evidence/baseline.md`.
- Byte manifest (`scripts/package_manifest.py record`, then `compare` against `d7366431:.project/active/subset-profile-screen/evidence/package-manifest-base.json`): 0 differences. Refusal records (`scripts/refusal_records.py compare`): 0 of 173 differ.
- TEAx lane: Item 2b's `evidence/execution-lane/lane.sh` with agentic-mbse pinned to `1b65ecbe` instead of `e268357f` (copies in my scratchpad): 124 passed, 124 distinct IDs.
- `sysml-codegen check` on all 12 probes and 10 guidance examples: every exit code and first answer line matches `evidence/probes.md` and `evidence/guidance-examples/README.md`. dc3 (`60b44d5`) `check --models models`: exit 0, "Generator: builds (140 modules)", same as the baseline.
- `git grep` in both repos for every retired module name and `L6_SUBSET`: hits only under `.project/`. The built wheel contains no subset or occurrence module.

## RG-1: the moved and dropped stored answers

- The 154 case models are byte-identical to agentic-mbse `e268357f` `subset_cases/`. All 246 stored generator answers are unchanged in every field except added witnesses; no codegen witness was lost.
- 65 agentic-side witnesses: 49 now in `generator.witnesses`, 16 dropped. I re-ran the generator half of each dropped case with its site recorded (`mutate.recording_sites`, with a positive control on four kept witnesses that did fire). None of the 15 dropped sites that still exist fires; the 16th is in deleted `subset_extraction.py`. So the drop hides no generator regression. One dropped site is `reference_use._invocations`, which is dead code (finding S4).
- Deleted sysml-codegen tests (agreement, screen-half, screen-mutation, tripwire, occurrence parity, screen faults, screen import) each compared or guarded the copy; the generator-side assertions survive in `test_generator_half.py`, `test_generator_mutations.py`, `test_witnesses.py` and `test_check_command.py`.

## Findings

### Blocker

None.

### Should-fix

**S1. L6's passing output still reads as a generation answer.** `src/agentic_mbse/validation/level6_architecture.py:68` titles L6 "Architecture & Codegen Conventions", and under `generated` `_target_note` (`:1069-1079`) adds nothing, so a run ends "✅ Level 6: Architecture & Codegen Conventions ... All quality checks passed!" with no pointer to `sysml-codegen check`. I ran it on `guidance-examples/m_attr`, a model the generator builds wrongly: L6 passes clean. This is the dc3 failure mode (a green L6 titled after the pipeline, read as the generation answer), only softer, and P-0005 promises L6 makes no generation claim. The old `pass_note` qualifier ("generated compatibility not established") was removed and nothing replaced it. Fix: under `generated` and unset, set `pass_note` to "generation not checked by L6; run sysml-codegen check --models <path>" so the final line carries it; and either drop "Codegen" from the title (for example "Architecture & Conventions") or have the owner confirm the title, since the plan lists it as an open assumption.

**S2. The default-count bug has no backlog row.** Reproduced: `generate` on `evidence/guidance-examples/m_attr` and `m_attr_spec` (`attribute cell_count : Integer default := 2;` redefined to 3) writes `pack__cells[0]` and `[1]` only, exit 0, no warning; `m_ok` writes three. sysml-codegen `.project/backlog/BACKLOG.md` has no row for it. Fix: file a sysml-codegen backlog row (silent wrong part count; a fix changes what builds, so RG-1, owner's call), citing these two models.

**S3. Losing the copy's "omitted" findings is not recorded.** The copy reported silent losses in models that build: `calc-usage-result` bare result, `string-value-omission`, and the omitted contexts of conditional, indexed-reference and invocation rules (`e268357f:src/agentic_mbse/sysml/subset_profile_rules.toml:224,326,483,546`). `check` exits 0 on those, and the new guidance covers only refusals, so nothing tells a modeller now. ADR 0004 Consequences does not say so, and `.project/adr/0004-generator-is-the-only-generation-authority.md:29` says the copy "has never flagged a model the generator builds", which is wrong: it flagged omissions on built models. Fix: reword `:29` to "never reported a refusal for a model the generator builds"; add a Consequences line naming the lost omission reports; route the question (guidance lines, or `check` warning on known silent losses) to the epic or a backlog row.

**S4. Dead code.** `reference_use.invocation_uses` and `_invocations` (`src/agentic_mbse/sysml/reference_use.py:455-500`) and `InvocationUse` (`src/agentic_mbse/sysml/invocation_allowlist.py:38-54`, docstring `:7-8`) have no caller in either repo's `src/`; only `tests/test_sysml/test_invocation_uses.py` and two lines of `test_invocation_allowlist.py` use them. Fix: delete them and those tests.

**S5. Spec grades.** `spec.md:16-19` mark R1-R4 `[NEED]`, but each comes from an approved agent recommendation ("owner approval of recommendation step N"), which capture-fidelity law 1 grades `[INFERRED] (ratified by owner, 2026-10-21)`, not settled. ADR 0004 grades the same decision correctly. P-0004 Authority repeats "R3, R4 [NEED]". Fix: regrade R1-R4 and P-0004's citation; R9 ("document it") stays `[NEED]`.

**S6. Stale records.** `.project/CURRENT_WORK.md:20` says the deletion and rewire "are Phase 4" (done). `.project/product/0005-l6-no-generation-claim.md:12,27` still say checked null until Phase 4 lands; `0004-generator-answers-generation.md:33` says re-check after Phase 4. Fix: update the row; stamp both promises at close, and change the scope sentences now. Note that `main` has moved `CURRENT_WORK.md` since `e268357f` (`359a63be`), so expect a conflict.

**S7. sysml-codegen leftovers.**
- `tests/expectations/refusal_cases/site_account.csv` columns `matrix_row` and `rule` hold the copy's IDs (11 rule rows, 21 matrix rows), and `tests/helpers/refusal_cases/witnesses.py:63-91` (`shared_rule_sites`, `r3_row_sites`, "the contract has no rule") and `site_scan.py:511-513,563-570` still use them to pick mutated sites. Fix: add a header line to the CSV saying these are frozen labels from agentic-mbse `e268357f` used only to choose mutation groups, and rename the helpers and docstrings to say that; a full redesign can wait.
- `.project/backlog/BACKLOG.md:49` `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` is moot; move it to a disposition with one line why. `:47` still says "The screen reports these models clear" and "a `rg1_pending` disagreement" (`disagreements.json` is deleted).
- `docs/architecture/modeling-assumptions.md:687` "The contract reports it (rule `calc-usage-result`, outcome `omitted` ...)": the contract is gone; delete the sentence.
- `.project/CURRENT_WORK.md:7` still says `check` "prints the same report; the screen's findings are information". Fix: say `check` prints only the generator's answer.

### Notes

- **N1.** L6 still carries generator knowledge: `L6_ANONYMOUS_RETURN` "Mirrors codegen's V8 diagnostic" (`level6_architecture.py:600`), `L6_ATTR_REDEF_EXPR_DROPPED`, and the four folded codes. ADR 0004 invariant 1 (`:49`, "No agentic-mbse module decides, predicts or reports whether the generator will refuse a model") is broader than what was built. Narrow it to "keeps no copy of the generator's refusal rules beyond the legacy L6 checks", or file their review.
- **N2.** Guidance limit 3 says not to pass a list-valued attribute to a calculation, but probe g4 shows `Real[3] = (1.0, 2.0, 3.0)` is refused even when nothing reads it (`MODELING_GUIDE.md.template:108`, `skills/sysml-conventions/SKILL.md:131`, `docs/patterns/adr002-calculations.md:150`). Saying so would prevent the same mistake earlier.
- **N3.** The JSON report key `profile` became `detail` (`src/agentic_mbse/validation/report.py:64`) under the same `validate-report/v1`. Nothing in either repo or dc3 reads it, but a shape change under an unchanged schema string breaks the usual contract; bump to v2 or keep the key.
- **N4.** `element_ref` (`src/agentic_mbse/sysml/element_refs.py:30-37`) now reads `str(qualified_name)` outside the `try`, where the old `_element_ref` read it inside, so a `ValueError` from that read would no longer become `ElementIdentityError`. No known SysIDE path raises there; Item 4 tests pass. Fine to leave or to move the read back inside the `try`.
- **N5.** ADR 0004 `:34` says "about 80 minutes of rework"; its source (`03-challenge.md` § 1) says about an hour (21:07 to 22:06).
- **N6.** `element_refs.py` and `execution_target.fold()` read clearly and are named for what they do.
- **N7.** Schema names `subset-mutations/2` and `subset-fixture-classes/1` in sysml-codegen keep "subset"; harmless.

## Not checked

- mypy and ruff on the base commits (I compared with the counts the plan records).
- Slow corpus tests (`-m slow`) in agentic-mbse.
- fusion-tea's L2/L6 output on this branch.
- The pre-repair dc3 tree (`808464d`).
- Whether every shipped skill and template outside the files this item touched still reads correctly; I read the diffs and the files they changed.

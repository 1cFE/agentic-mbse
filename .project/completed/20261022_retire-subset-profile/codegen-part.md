# sysml-codegen side of retiring the subset profile (parts 4 and 6)

Read-only. Worktree `/home/reid/src/subset-conformance/sysml-codegen`, branch `subset-profile-screen` at `529830cf`, compared with `main`. Line numbers are at branch HEAD unless marked `main:`.

## 0. A fact the parent needs first (agentic-mbse branch state)

agentic-mbse `main` is **not** "shipped-example-contract minus 2 doc commits". `git merge-base main shipped-example-contract` is `1a3d67c6`; `main` is 24 commits ahead (`e268357f Merge pull request #33 from 1cFE/subset-conformance`, Item 2a). Only `main` has `src/agentic_mbse/sysml/conformance_case.py` (312 lines) and `src/agentic_mbse/sysml/subset_cases/` (154 case folders, each `case.json` + `model.sysml`). sysml-codegen imports both. The sibling checkout `/home/reid/src/subset-conformance/agentic-mbse` (at `e268357f`) is what sysml-codegen's path dependency resolves to, and it has the 154 cases.

## 1. Dependency on agentic-mbse (main and branch identical)

- `pyproject.toml:24` `"agentic-mbse>=0.1.3,<0.2"`; `pyproject.toml:121-122` `[tool.uv.sources] agentic-mbse = { path = "../agentic-mbse", editable = true }`.
- `uv.lock:6-8` `name = "agentic-mbse"`, `version = "0.1.3"`, `source = { editable = "../agentic-mbse" }`; `uv.lock:926` listed in sysml-codegen's deps.
- `src/sysml_codegen/_upstream_pins.py:39` `AGENTIC_MBSE_PACKAGE_VERSION = "0.1.3"`; `:65-69` `SUBSET_PROFILE_VERSION = "subset-profile/v2"` (main: `:64-68`); `:18-19` docstring says it is compared by `assess_screen` and by the adapter; `:78` in `__all__`. Pinned by `tests/conformance/test_upstream_pins.py:18` (imports `SUBSET_PROFILE_VERSION` from agentic_mbse).
- sysml-codegen also depends on agentic-mbse for things that are not the profile and must stay: `orchestration/elaborated_pipeline.py:24-25` (`SemanticEvidenceCode`, `get_syside`), `cli/install.py:54-59` (installer), `_upstream_pins.py` `CONSTRAINT_FACTS_SCHEMA_VERSION`, `EXPRESSION_IR_SCHEMA_VERSION`, `PROFILE_SEMANTIC_VERSION` (`agentic_mbse.sysml.executable_profile`, `:62`; this is the executable profile, a different module from the subset profile, not checked whether it belongs to the copy). So `cmd_generate`'s and `cmd_check`'s "agentic-mbse is not installed" guards (`cli/__init__.py:58-65`, `:103-110`, `:155-159` for snapshot) stay valid after retirement.

## 2. Every import of agentic-mbse subset-profile modules

Modules imported: `subset_profile`, `subset_extraction`, `subset_coverage`, `conformance_case`, `occurrence_extraction`, `occurrence_facts`.

src (branch):
- `src/sysml_codegen/subset_screen.py:28` (TYPE_CHECKING `Verdict`), `:118` `from agentic_mbse.sysml import subset_profile`, `:131` `extract_subset_facts`.
- `src/sysml_codegen/cli/report.py:114` `Outcome`, `:153` `Outcome, Qualification, Verdict`, `:195` `Qualification`.
- `src/sysml_codegen/subset_profile_adapter.py:25-33` (`subset_profile` and its names; main `:24`). Its import-time pin check is the site recorded at `site_account.csv:501` (main).

tests/helpers (branch; main same minus noted):
- `tests/helpers/subset_profile/cases.py:32-41` (`conformance_case.*`, `PACKAGED_RULES, Outcome, RuleRecords`); branch also `:43` imports `DisagreementKind, RefusedFinding, disagreement_kind` from `sysml_codegen.cli.report`, `:45` `REASON_MAPPING, NoRefusal`.
- `capture.py:26`, `witnesses.py:24` (conformance_case); `observe.py:40,379-380` (main `:39,371-372`); `occurrence_parity.py:41` (`occurrence_facts`); `mutate.py:57-58` (patches `subset_profile._RULES`, `_Recognized`).
- `tests/helpers/blocked_screen_import.py:17` `BLOCKED = "agentic_mbse.sysml.subset_profile"` (branch only).

tests (branch; `*` = also on main):
- `tests/conformance/subset_profile/`: `test_assess_screen.py:19`, `test_candidate_refusal_marks.py:14`*, `test_case_store.py:20`*, `test_fixture_agreement.py:31-33`*, `test_mutation_record.py:11`*, `test_occurrence_parity.py:22`* (`occurrence_extraction`), `test_reason_mapping.py:14`*, `test_record_coverage.py:21`*, `test_screen_half.py:16`*, `test_screen_mutations.py:21-22`*, `test_shared_load_screen.py:17-19`, `test_site_account.py:15-16`* (`subset_coverage.FOLLOW_UP_SITES`, `PACKAGED_RULES`), `test_site_reason_reaches_harness.py:38`* (`packaged_case_dir`), `test_site_reason_vocabulary.py:6`* (`SUBSET_REASON_CODES`), `test_tripwire.py:20`*, `test_witnesses.py:13`*.
- `tests/conformance/test_check_screen_faults.py:29`, `test_screen_import_failure.py:4`, `test_upstream_pins.py:18`*.
- `tests/unit/test_cli_module_boundary.py:39-40`, `test_report.py:16`, `test_subset_case_answers.py:14-15`*.
- scripts: none import the profile directly; `scripts/_generate_corpus.py:38` and `scripts/refusal_records.py:54,62` import `tests.helpers.subset_profile.cases` / `observe` (indirect).

## 3. Item 2b code that runs the screen after generate/check (branch only)

All of this is new on the branch versus main except the adapter.

- `src/sysml_codegen/subset_screen.py` (181 lines, branch only). `NotAssessedCause` `:43-49`, `ScreenNotAssessed` `:52-58`, `UnverifiedEntry` `:61-70`, `ScreenAssessed` `:73-81`, `assess_screen(loaded)` `:84-110` (never raises), `_screen` `:113-158` (pin compare `:115-128`, `extract_subset_facts` + `evaluate_subset_profile` `:137-140`, `render_finding` `:146`), `_not_importable` `:161`, `_portable`/`_referent` `:169-181`.
- `src/sysml_codegen/cli/report.py` (218 lines, branch only). `DisagreementKind` `:48-51`, `RefusedFinding` `:54-60`, `disagreement_kind` `:63-78` (Item 2a's agreement rule moved into src), `Disagreement` `:80-87`, `Report` `:89-94`, `model_builds` `:97`, `generator_codes` `:102`, `build_report` `:108-128`, `log_report` `:131-134` (generator answer then screen), `log_screen_section` `:137-145`, `_log_screen` `:148-190`, `_log_finding` `:193-212`, `_location` `:215`. Note `log_report` calls `prepare.log_generator_answer` (`:133`); that is the generator's own answer line and is what `check` must keep printing.
- `src/sysml_codegen/subset_profile_adapter.py` (157 lines; on main too, 143 lines in 2a). `NoRefusal` `:50`, `ReasonMapping` `:58-70`, `REASON_MAPPING` (around `:72-100`), `SubsetDiagnostic` `:105`, `render_finding` `:125`. Branch change (`+22/-?`) only docstring `:11-14` (only `assess_screen` imports it) and the import list.
- `src/sysml_codegen/cli/__init__.py`:
  - `:23-24` TYPE_CHECKING import of `Report`; `:26-32` comment block naming the screen rule (D17).
  - `cmd_check` `:94-123`: docstring `:95-99` ("with the screen's findings"; "The screen never changes the code"), `:112` imports `report`, `:122` `report.log_report(checked)`, `:123` exit code from `prepare.Prepared` only.
  - `CheckRequest` `:83-92` (kept). `run_check` `:126-142`: docstring `:127-131` mentions the screen; `:133` imports `subset_screen`; `:142` `return report.build_report(generator, subset_screen.assess_screen(loaded))`. Without the screen this returns the generator answer (`Prepared | Refused`) and `cmd_check` calls `prepare.log_generator_answer`.
  - `run_codegen` `:456-505`: docstring `:466-469` (screen after the seal); `:504` `_report_after_the_seal(loaded, generator)`.
  - `_report_after_the_seal` `:508-523`: the guarded step to delete.
  - CLI help: `:356` comment "Check subcommand — generate's answer without writing, plus the screen (Item 2b design D6)"; `check` help string `:358` "Report whether generate would build or refuse a model, without writing" (does not mention the screen; can stay). No `--help` text mentions the profile.
- Other src touched by 2b that are generator-only and stay: `cli/prepare.py` (637), `cli/emit.py` (560), `cli/destination.py` (43; `:6` docstring says it imports nothing from the screen), `orchestration/elaborated_pipeline.py:145,171` (`LiveLoad` docstrings say "elaboration and the screen both read", wording only), `orchestration/exact_pipeline_context.py:309` (wording "also screens the model").

### Tests for the screen step (branch only unless marked)

Delete outright (screen-only):
- `tests/unit/test_subset_screen.py` (81).
- `tests/unit/test_report.py` (253). Tests the report's totality and agreement rule; all screen.
- `tests/conformance/subset_profile/test_assess_screen.py` (105), `test_shared_load_screen.py` (49), `test_check_matches_stored_answers.py` (90; its generator half, `test_check_reports_the_stored_generator_answer` `:61`, is worth keeping as a generator test), `test_report_form.py` (69; "check gives generate's answer ... on every 2a case"; generator half worth keeping).
- `tests/conformance/test_check_screen_faults.py` (180): skew, failing screen, screen-only refusal.
- `tests/conformance/test_screen_import_failure.py` (120) and `tests/helpers/blocked_screen_import.py` (37).

Edit (mixed):
- `tests/conformance/test_check_command.py` (227): keep `:79` writes nothing, `:89`, `:99`, `:126`, `:142`, `:208` never loads emit; edit `:109` (parse errors: asserts screen not assessed), `:165` `test_generate_survives_a_report_failure` and `:184` `test_check_has_no_guard` (patch `assess_screen`/`log_screen_section`, `:160-162`, `:190`) and `:195` `test_generate_prints_the_report_after_writing` (looks for "Screen " line `:202`): delete or rewrite. `:33` imports `tests.helpers.subset_profile.cases` for case models.
- `tests/conformance/test_check_snapshots.py` (164): `:97` and `:118` assert "screen not assessed for the snapshot reason"; the replay-equality tests `:92,:106,:127,:154` are generator tests.
- `tests/unit/test_cli_module_boundary.py` (154): keep `:59` (read-only modules import nothing that writes), `:85`, `:149` (emit only inside run_codegen); delete `:68`, `:72` (screen unimported, list at `:39-40`), `:111`.
- Branch generator-only tests that stay: `test_refusal_before_first_write.py` (169), `test_emit_writer_failures.py` (56), `test_emit_leaves_the_graph_unchanged.py` (32), `test_live_load.py` (115), `tests/unit/test_prepare_steps.py` (67), `test_relay_public_failures.py` (60), `tests/conformance/subset_profile/test_call_closure.py` (151) and `test_emit_reachability.py` (83) (site reachability after first write; generator facts that use the 2a site scan).

### Docs and .project mentions of the screen step (branch)

- `CLAUDE.md:32-33` check command line (keep); `CLAUDE.md:77` "After the seal, `generate` runs the subset screen on the same load and prints its findings ... `check` ... prints the same report. The screen never changes either com[mand]" (edit).
- `docs/architecture/reference/02-orchestration.md:76-87` new section "The route: read first, write last, then report": step 4 at `:83` (`assess_screen`, `cli/report.py`, guard `cli/__init__.py:522`), `:87` `check` "runs steps 1, 2 and 4 ... prints the same report. The screen's findings never change the exit code" (edit).
- `.project/active/subset-profile-screen/`: `spec.md` (138), `design.md` (294), `design-review.md`, `spec-review.md`, `product-lens.md`, `plan.md` (946; Phases 6-8 add screen, Phase 10 "no readiness rule"), `audit.md`, `briefs/`, `evidence/`, `spike-snapshot/`.
- `.project/CURRENT_WORK.md:7` (Item 2b status), `:13` (2a closed), `:21` (L6 verdict line names `subset-profile/v2, subset-coverage/v2`).
- `.project/backlog/BACKLOG.md:49-51` `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` (carry the screen in snapshots). Becomes moot. Other 2a-filed items `:29-47` (CALC-USAGE-BINDING-LOST..., CALC-DEF-KEYWORD-MEMBER-STUB, REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP, SI-TYPE-INVALID-MESSAGE-PRINTS-QN-OBJECT, ITEM-OWNED-PART-REFUSED) are generator defects and stay.
- Architecture review (the last two commits, `1019e208`, `529830cf`): `.project/active/subset-profile-screen/architecture-review/01-current-system.md` (212), `02-alternatives.md` (300; option G "correct guidance plus an early generator check" `:196`; option C keeps list at `:127-133`: 2a per-site reasons, site account and corpus as plain generator regression tests; discards agreement, disagreement, screen-mutation and occurrence parity tests), `03-challenge.md` (126; `:52` notes deletion breaks agentic-mbse Item 4: `parameter_redefinition_extraction.py` imports `safe_location` from `occurrence_extraction` `:39` and `_element_ref`, `_IdentityError` from `subset_extraction` `:53`; `:59` 0 of 136 disagreements are screen-refuses-generator-builds; `:64` the list's unique value is three families B1 calc-owned assertions, B2 sequence inputs, open part multiplicities), `index.html` (460, the published design page).

## 4. Item 2a agreement-test system

Locations (main and branch):
- Stored generator answers: `tests/expectations/subset_profile/cases/*.json`, **246 files**. 92 have `"home": "codegen"` (model in `tests/fixtures/subset_profile/<id>/`, 93 files incl. a two-file case) and **154 have `"home": "agentic"`** (model is agentic-mbse package data `agentic_mbse/sysml/subset_cases/<id>/model.sysml`, located via `conformance_case.packaged_case_dir`, `tests/helpers/subset_profile/cases.py:415-418`). Generator outcomes: 169 refused, 77 generated. Each JSON has a `screen` half (verdict, findings) and a `generator` half (`outcome`, `codes`, `reasons` = SiteReason values, `witnesses` = site-account ids), plus `construct`.
- `tests/expectations/subset_profile/disagreements.json`: schema `subset-disagreements/2`, 136 entries: `generator_refuses_screen_silent`/`reproduced_gap` 95, `.../codegen_owned` 33, `.../rg1_pending` 1, `code_unmapped`/`reproduced_gap` 7. Same count on branch.
- `tests/expectations/subset_profile/site_account.csv`: main 502 lines, branch 498 (header comment at `:1-2`: "one row per site `site_scan.py` finds under `src/sysml_codegen/` ... ported from agentic-mbse `scripts/subset_profile/scan_sites.py`"). Two rows are the adapter's own sites (main `:501-502`).
- `tests/expectations/subset_profile/mutations.json` (schema `subset-mutations/1`; generator-site mutations and screen-detector mutations), `fixture_classes.json` (schema `subset-fixture-classes/1`, class of every `tests/fixtures/` dir: generating/refusing + codes).
- Branch only: `tests/expectations/subset_profile/refusal_records.json` (3224 lines), written by `scripts/refusal_records.py`, read by `tests/helpers/refusal_records.py` (101): base-commit log records of every refusal (message + structured `Refusal`). Used by `test_check_command.py`, `test_check_snapshots.py`, `test_emit_writer_failures.py`, `test_refusal_before_first_write.py`. Also `scripts/_generate_corpus.py` (subjects for those scripts).
- Reason codes: `src/sysml_codegen/elaboration/diagnostics.py:40` `class SiteReason(StrEnum)` (about 86 members, `<stage>_<condition>`), added in `06f938fc` (Item 2a P1.3); its docstring `:41-46` says it stays distinct from agentic-mbse's `SUBSET_REASON_CODES`. Carried in `src/sysml_codegen/cli/refusal.py` (90 lines, `Refusal` logged as `extra={"refusal": ...}`, Item 2a D2). Both generator-owned.
- Helpers: `tests/helpers/subset_profile/` `__init__.py`, `capture.py` (99), `cases.py` (558), `fixture_classes.py` (124), `mutate.py` (442), `observe.py` (386), `occurrence_parity.py` (344), `site_scan.py` (805), `witnesses.py` (228). Plus `tests/unit/test_subset_case_answers.py` (315).
- Test files in `tests/conformance/subset_profile/` on main (27): listed in split below.
- `docs/architecture/modeling-assumptions.md:668-690` § 10 "What Generates but Is Not Carried Through" cites the stored answers in `tests/expectations/subset_profile/` as the pins for silent-loss behaviour (keep, update path if moved).

### (a) Only makes sense with the copy (delete)

- `src/sysml_codegen/subset_profile_adapter.py` (whole), `subset_screen.py`, `cli/report.py`, `_upstream_pins.py:65-69,78` and docstring `:18-19`, `test_upstream_pins.py` subset assertion.
- The `screen` half of every stored case JSON; `disagreements.json`; the screen-detector half of `mutations.json`.
- Tests: `test_agreement.py` (40), `test_candidate_refusal_marks.py` (47), `test_disagreement_record.py` (120), `test_fixture_agreement.py` (103), `test_occurrence_parity.py` (88) + `helpers/occurrence_parity.py` (agentic-mbse occurrence port vs codegen; ADR 0018's parity gate), `test_reason_mapping.py` (229), `test_record_coverage.py` (135; record outcomes rest on cases), `test_screen_half.py` (28), `test_screen_mutations.py` (59), `test_tripwire.py` (60; generator never runs the screen), `test_site_reason_vocabulary.py` (18; SiteReason distinct from `SUBSET_REASON_CODES`), `tests/unit/test_subset_case_answers.py` (mostly agreement), plus the 2b screen tests in section 3.
- Parts of `test_site_account.py` that import `subset_coverage.FOLLOW_UP_SITES` and `PACKAGED_RULES` (`:15-16`) to cross-check with the copy.
- Helper code: `cases.py` agreement/record readers (`:438-558`, `mapped_code`, `disagreement`, `read_disagreements`, `recorded`), `mutate.py` screen targets `:57-58`, `observe.py` screen half (`:40`, `:379-380`).

### (b) Generator regression assets worth keeping

- The 246 models and their generator answers (`outcome`, `codes`, `reasons`, `witnesses`) as plain generator tests: `test_generator_half.py` (119, "live generator half equals its stored answer, and refuses only on its construct"), `test_case_store.py` (94, after dropping the screen side), `test_witnesses.py` (37). **Blocker: 154 of the models live in agentic-mbse `subset_cases/` and are read through `agentic_mbse.sysml.conformance_case`; they must be moved into `tests/fixtures/subset_profile/` (or a renamed folder) before agentic-mbse deletes them.**
- `SiteReason` (`elaboration/diagnostics.py:40`) and `Refusal` (`cli/refusal.py`): stable refusal reason codes in structured log records.
- Site account and its tests: `site_account.csv`, `helpers/site_scan.py`, `test_site_account.py`, `test_site_account_completeness.py` (44), `test_site_reach.py` (40), `test_site_reasons.py` (85), `test_site_reason_reaches_harness.py` (208; uses `packaged_case_dir` `:38`, needs the moved models), `test_site_scan_mutations.py` (127), `test_emit_reachability.py`, `test_call_closure.py`.
- Generator mutations: `test_generator_mutations.py` (38), `test_mutation_record.py` (60) and `test_mutator.py` (289), with the generator half of `mutations.json` and `helpers/witnesses.py`.
- `fixture_classes.json`, `helpers/fixture_classes.py`, `test_fixture_classes.py` (81): every fixture dir classed generating/refusing.
- `test_committed_snapshots_have_no_diagnostics.py` (27), `test_silent_loss_seams.py` (58).
- `refusal_records.json` + `scripts/refusal_records.py` + `helpers/refusal_records.py` (branch).
- `helpers/subset_profile/capture.py` (writes stored generator answers).
- The folder and helper names say `subset_profile`; renaming is optional and not checked for cost.

## 5. ADR 0018 and other ADRs

- ADR 0018 is **not on main and not on `subset-profile-screen`**. It exists only on branch `adr-0012-occurrence-summary-amendment` (local and `origin/`), one commit `8396cb23` "ADR 0018 amends 0012: occurrence reads gain a second reviewed owner in agentic-mbse, held by parity", checked out in `/home/reid/src/sysml-codegen`. That branch's base predates the Item 2a merge (its diff to main deletes the whole 2a system), so it is unmerged and stale.
- File: `.project/adr/0018-occurrence-summary-shared-with-agentic.md`. Title (`:3`) "Occurrence summary has a second reviewed owner in agentic-mbse, held by a parity test"; `:9` provenance `[AGENT] (ratified by owner, 2026-10-18)`. Decision `:17`: ADR 0012's invariant that raw parser reads for declaration discrimination, slot construction and multiplicity keep "narrow codegen ownership" is amended; agentic-mbse `sysml/occurrence_extraction.py` does the same reads; a permanent parity test in codegen CI compares them (end condition ii). Invariants `:25-27`. Rejected `:31-32`. Branch also edits `0012-...md` (`amended_by`, 4 lines) and `INDEX.md`.
- Retiring the copy removes 0018's subject (the second owner and the parity test, `test_occurrence_parity.py`). Unless agentic-mbse keeps `occurrence_extraction.py` for something else (03-challenge says Item 4 uses `safe_location` from it), ADR 0018 should not be merged; ADR 0012 stands unamended on main (`main:.project/adr/0012-...md:7 amended_by: []`).
- No ADR on main or the branch (0001-0017) mentions the subset profile (`git grep -i subset main -- .project/adr` finds nothing). ADR 0007 (agentic-mbse owns neutral facts, codegen owns rendering) is cited by 0018 as why agentic-mbse cannot import codegen; unchanged.

## Not checked

- Whether `agentic_mbse.sysml.executable_profile` (`PROFILE_SEMANTIC_VERSION`) is part of the copy.
- Exact line ranges of `REASON_MAPPING` inside the adapter (approximate).
- Did not run any tests.

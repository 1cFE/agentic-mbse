# Implementation Plan: L6 integration and execution-target settings (EXEC-SUBSET-CONTRACT Item 3)

**Status:** Phases 1–5 complete; Phase 6 next
**Created:** 2026-10-18
**Last Updated:** 2026-10-18

## Source Documents

- **Spec:** `.project/active/l6-subset-profile/spec.md` (revised after spec review; success criteria are the contract)
- **Design:** `.project/active/l6-subset-profile/design.md` (rev 1; review resolutions in `design-review.md`). Component details, data model, severity table, issue codes, report schema and appendices live there. This plan links to them and does not repeat them.
- **Spike:** `spikes/findings.md`, `spikes/f4-codegen-citations.md` (consumer-tree results, advisory shapes, String ids, codegen citations at `b5663c07`)
- **Owner decisions and gates:** `briefs/align.md`. Owner boundary: nothing in Item 2, no writes in sysml-codegen. dc3 and fusion-tea are read only through `git archive` copies.

## The Point

`agentic-mbse validate` should tell a modeler up front which model shapes the pinned code generator will refuse, using Item 1's contract (`src/agentic_mbse/sysml/subset_profile.py`, `subset-profile/v1`). Today nothing calls that contract, so a modeler finds refusals one generator run at a time: dc3 found its blockers over five runs, and the contract reports 236 refused findings on that baseline in one pass. [AGENT] (ratified by owner, 2026-10-18; `briefs/align.md`)

Each project says in its committed `pyproject.toml` how it runs: `[tool.agentic-mbse] execution-target = "generated" | "native"`. The target only decides how loud a finding is, never what is true:

- Unset (the default): generator findings are warnings, with a note naming the setting.
- `native`: generator-only findings fold into one INFO summary line.
- `generated`: confirmed refusals are errors.

Two things must hold in everything a user reads:

- Nothing claims a model "will generate". `clear` means only "no refusals found by the implemented rules", and L6 is not `sysml-codegen check` (ADR 0001 invariant 2).
- A broken check never passes. Under every target, a crash or a failed inspection fails the run ([AGENT] delegated by owner, 2026-10-18, gate R3-2). The safeguard for that decision is the before/after run in Phase 11: any consumer tree that goes from pass to fail goes to the owner before merge.

This ladders to the epic (`.project/backlog/epic_executable-subset-contract.md`): Item 1 built the contract, this item makes `validate` its first consumer, Item 2 (another agent, not touched here) builds `sysml-codegen check`.

## Implementation Strategy

**Phasing rationale.** The riskiest change touches every level, not just L6: one model load and one constraint extraction shared across the run (`design.md` D14, bet B5). It goes first and alone, against a recorded baseline, so any change in another level's results is caught before anything is built on it. Then the pieces L6 needs, smallest and purest first: the settings reader, the severity table, the runner and report. Then L6 itself in three steps: the contract and its presentation, the advisories, the exception sites. The audit, `init` and docs follow, because they depend on the codes and wording settled earlier. The before/after safeguard is last because it measures the finished branch.

**Critical path.** Phase 1 (baseline + session) → Phase 2 (settings) → Phase 3 (severity table) → Phase 4 (runner, report, target in L6) → Phase 5 (contract in L6) → Phase 7 (exception sites) → Phase 11 (safeguard). Phases 6, 8, 9 and 10 hang off that path: 6 and 8 need Phase 5; 9 needs Phase 2; 10 needs the wording from Phases 5 and 6.

**First proof point.** Phase 1's with/without test: each of L2–L6 on the fixture models gives the same result with and without the shared session, and one fusion-tea `validate --complete` on the branch is no more than 10% slower than at `ebb3d467` (it should be faster, since L6 stops extracting a second time).

**Overall validation approach.**

- Each phase starts by writing its tests from the stencil, and the design's fixtures where it gives them.
- **Green rule, every phase:** no test failure that is not in the Phase 1 baseline list; every new or modified file passes `uv run ruff check <files>`, `uv run ruff format --check <files>` and `uv run mypy src/`. Format only the files the phase touched (`uv run ruff format <files>`). Never run repo-wide `ruff format`.
- An existing test whose assertion changes because a swallowed failure now reports, or because of the L6 rename, is the intended change. Record each one in that phase's Implementation Notes with the reason.
- Fixture projects for CLI tests are built in `tmp_path` with a `work/BACKLOG.md` marker, so the project root is never this checkout or `$HOME` (`design.md#validation-approach`).
- Tests that need a parsed model carry the label-only `syside` marker added in Phase 1. It never skips. Tests that can use fakes do (`design.md` Validation Approach, review S4).

**Spec criteria trace.** Each phase's "Done when" names the spec criteria it closes, by the bold group heading in `spec.md` § Success Criteria. The table at the end maps every criterion to its phase and test file.

---

## Phase 1: Baseline, then the shared extraction session alone

### Goal

Record what passes and fails at `ebb3d467`, then land `ValidationSession` (`design.md` D14) with no other change, and prove each level's results are unchanged.

### Assumption Under Test

Bet B5: levels 2–6 only read the loaded model, so one shared load and one shared constraint extraction give each level exactly the result it gets today. And sharing does not make fusion-tea slower.

### Step 1a: Baseline (no code change)

- [x] Confirm `git diff --stat ebb3d467 HEAD -- src tests pyproject.toml uv.lock` is empty. If it is not, take the repository baseline from a `git archive ebb3d467` export instead of the checkout, and say so in the evidence. *Done: empty; checkout used (`evidence/baseline.md`).*
- [x] Run `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/`. Record pass/fail counts and the exact list of failing test ids, mypy errors and ruff findings in `evidence/baseline.md`. This list is the green rule's reference for every later phase. Record whether `SYSIDE_LICENSE_KEY` was present. *Done: 6 failed / 3947 passed, 97 mypy errors, 118 ruff findings; licence present (`evidence/baseline.md`).*
- [x] Write the export-and-run core of `scripts/l6_subset/run_consumers.py` (NEW) now, because Phase 11 extends it: Appendix C steps 2–8 (export a code revision and each consumer tree with Item 4's rules from `scripts/positional_binding/run_trees.py`, check the extraction parent is not a project root, record each tree's root and `pyproject.toml` table, run `-m agentic_mbse validate --complete models` with `PYTHONPATH=<code export>/src` and `cwd=<tree>`, check `agentic_mbse.__file__` is inside the export, capture stdout, stderr, exit code and wall time, parse per-level status from text). Subcommand `baseline --base ebb3d467` runs only the base revision on all three trees. *Done: `baseline` subcommand. Also added `session-equality` (see notes).*
- [x] Run `baseline` once, alone on an idle machine. Write `evidence/baseline-consumers.{json,md}`: per tree and level, pass/fail or "crashed, recorded as pass"; exit code; wall time; the L1–L6 issue lines. Expected from the spike: fusion-tea and dc3 `808464d` fail L6, dc3 `60b44d5` passes. Record SysIDE version. *Done: matches the spike (fusion-tea and dc3 `808464d` fail L6, `60b44d5` passes); SysIDE 0.8.4; fusion-tea 410.9 s (`evidence/baseline-consumers.md`).*

### Step 1b: Test stencil (write before the session code)

```python
# tests/test_validation/test_session.py
@pytest.mark.syside
@pytest.mark.parametrize("level", [2, 3, 4, 5, 6])
@pytest.mark.parametrize("fixture", SESSION_FIXTURES)  # sample_models, sump_pump, adr002_violations, l6_negative, ...
def test_level_result_is_identical_with_and_without_session(level, fixture):
    without = run_level(level, fixture)
    with ValidationSession():
        with_session = run_level(level, fixture)
    assert result_view(with_session) == result_view(without)   # success, issues, warnings, metrics

def test_constraint_facts_extracted_once_per_model_in_a_run(monkeypatch, fixture_files):
    calls = count_calls(monkeypatch, "extract_identified_constraint_facts")
    with ValidationSession() as session:
        run_all_levels(fixture_files)
    assert calls.n == 1 and session.constraint_extractions == 1

def test_memo_reraises_the_same_extraction_error_on_every_call(): ...
def test_cached_load_is_dropped_when_a_file_size_or_mtime_changes(tmp_path): ...
def test_extract_subset_facts_default_keyword_matches_todays_output(): ...   # I4
def test_no_session_means_todays_behaviour(): ...
```

`result_view` compares `success`, `issues`, `warnings` and `metrics` exactly. L1 is not in the list: it does not call `load_sysml_model` (D14).

### Changes Required

**See `design.md` for:** D14, Implementation Notes "Session details", I10, B5.

- [x] `pyproject.toml:103-106`: register the label-only `syside` marker (no skip logic). *Done, committed `1058e4dc`.*
- [x] `tests/test_validation/test_session.py` (NEW): the stencil above. *Done, committed `1058e4dc`.*
- [x] `src/agentic_mbse/validation/session.py` (NEW): `ValidationSession` as a context variable; load cache keyed by resolved path, size and `mtime_ns`; constraint-fact memo keyed by `id(model)` holding a strong model reference; stores facts or the raised exception; counts real extractions. *Done, committed `1058e4dc`.*
- [x] `src/agentic_mbse/validation/common.py:102` `load_sysml_model`: consult the active session. *Done, committed `1058e4dc`.*
- [x] `src/agentic_mbse/validation/level4_constraints.py:65` and `level6_architecture.py:650`: get facts through the session (direct call when no session is active). *Done, committed `1058e4dc`.*
- [x] `src/agentic_mbse/sysml/subset_extraction.py:466`: add the `constraint_facts` keyword, default `extract_identified_constraint_facts`, used at `:454`. Not called by L6 yet. *Done, committed `1058e4dc`.*
- [x] `src/agentic_mbse/validation/runner.py:58` `run_all_checks`: wrap the level loop in `ValidationSession()`. *Done, committed `1058e4dc`.*

### Validation

**Automated:**
- [x] `uv run pytest tests/test_validation/test_session.py` passes. *Done: 24 pass after `sump_pump` was split into its three subfolders (orchestrator decision 2, below). Before that, 21 of 22 passed.*
- [x] Full suite: green rule against `evidence/baseline.md`. *Done: the 6 baseline failures only.*
- [x] ruff check, ruff format --check on touched files; `uv run mypy src/`. *Done: no new mypy errors or ruff findings.*

**Manual (the stop condition):**
- [x] Commit the session change. Run `run_consumers.py before-after --base ebb3d467 --branch HEAD --trees fusion-tea` (a first cut of Phase 11's subcommand: steps 1–9 of Appendix C for one tree, plus the timing in step 10). Record both wall times and the L1–L6 issue-line comparison in `evidence/session-check.md`. *Done: session `1058e4dc`; run at `00adb102` (after Phases 2–3, which add no code on the validate path). fusion-tea 411.4 s → 206.0 s (0.501), L1–L6 identical, no flags (`evidence/session-check-before-after.md`).*
- [x] **Stop and report to the orchestrator** if any level's result differs in the with/without test, if any fusion-tea L1–L6 issue line differs from base, or if branch wall time is more than 1.10 × base. Do not start Phase 2. *Fired: the with/without test differs on `sump_pump`. Stopped before the commit and before Phase 2.* *Resolved by the orchestrator's answers (below); the subprocess check passed.*

**What we know works after this phase:** one load and one extraction per run, with every level's result unchanged and fusion-tea not slower. Every later phase builds on that.

**Done when:** I10 and B5 hold on fixtures and on fusion-tea. Spec trace: supports § Consumer evidence (`before-after.md` time and per-level comparison); no spec criterion closes here.

---

## Phase 2: Shared settings module and the holdout guard

### Goal

One definition of the keys allowed in `[tool.agentic-mbse]`, read by both research and validation (`design.md` D1).

### Assumption Under Test

The holdout guard can switch to the shared reader without changing any research behaviour except accepting `execution-target` (the intended relaxation in `design.md#potential-risks`).

### Test Stencil

```python
# tests/test_project_settings.py
def test_toolkit_keys_are_exactly_execution_target_and_research():
    assert TOOLKIT_KEYS == {"execution-target", "research"}

@pytest.mark.parametrize("key", ["execution_target", "executiontarget"])
def test_unknown_key_is_a_defect_naming_key_and_allowed_set(tmp_path, key): ...
def test_underscore_table_is_a_defect(tmp_path): ...
def test_reseach_subtable_typo_is_a_defect(tmp_path): ...   # [tool.agentic-mbse.reseach]
def test_absent_file_or_table_is_an_empty_table_not_a_defect(tmp_path): ...
def test_malformed_toml_is_a_defect_with_path_and_parse_error(tmp_path): ...
def test_reader_never_checks_values(tmp_path): ...   # execution-target = 1 is not a reader defect

# tests/test_research/test_holdout.py (add)
def test_both_keys_pass_the_guard(tmp_path): ...
def test_bad_execution_target_value_does_not_refuse_register(tmp_path): ...
def test_misspelled_key_fails_the_guard(tmp_path): ...
```

### Changes Required

**See `design.md` for:** D1, I6, Implementation Notes "Settings reader", Data model (`SettingsFault`).

- [x] `tests/test_project_settings.py` (NEW), additions in `tests/test_research/test_holdout.py`: stencil above. *Done `8e455049`.*
- [x] `src/agentic_mbse/project_settings.py` (NEW): `TOOLKIT_KEYS`, `read_toolkit_table(root)`, `SettingsDefect` with `SettingsFault`. Standard library only. `add_execution_target` comes in Phase 9. *Done.*
- [x] `src/agentic_mbse/research/holdout.py:241` `_research_table`: call `read_toolkit_table`; turn a defect into `HoldoutGuardError`; keep validating only `holdout-guard`. Replace the "its only key is 'research'" message (`:283`) with the allowed set, and update the research tests that assert the old text (record them). *Done; `test_hook_config.py:172` expected text updated to the allowed-set message.*

### Validation

- [x] New and research test suites pass; full suite green rule. *Done: 594 research + settings tests pass; full suite = baseline 6.*
- [x] ruff and mypy on touched files. *Done: no new findings.*
- [x] Manual: a `tmp_path` project with both `execution-target = "generated"` and a valid `holdout-guard` passes the guard. *Done as a test instead: `test_holdout.py::test_both_keys_pass_the_guard`.*

**What we know works:** one key set, two readers, each checking only its own value.

**Done when:** spec § One key set, two readers: bullets 1, 2, 4, 5 (the "bad holdout-guard does not fail validate" bullet closes in Phase 4, when L6 reads the table).

---

## Phase 3: The pure severity policy

### Goal

`validation/execution_target.py` with the target types, `resolve_target()`, `Category`, `Display`, `display()` and `LEGACY_CATEGORY` (`design.md` D2, Data model, The severity table).

### Assumption Under Test

The whole target behaviour fits one pure table, and check failures cannot reach the native summary (I2).

### Test Stencil

```python
# tests/test_validation/test_execution_target.py
EXPECTED = {  # copied cell by cell from design.md "The severity table"
    (Category.REFUSED, Target.UNSET): Display.WARNING,
    (Category.REFUSED, Target.GENERATED): Display.ERROR,
    ...
}
def test_display_matches_every_cell():
    assert {(c, t): display(c, t) for c in Category for t in Target} == EXPECTED

def test_check_failure_and_setting_invalid_are_error_everywhere(): ...   # I2
def test_legacy_category_covers_exactly_the_17_l6_codes(): ...
def test_lowered_set_equals_native_lowered_fixture():
    assert lowered(LEGACY_CATEGORY) == load_toml("tests/fixtures/l6/native_lowered.toml")   # empty now

def test_resolve_target_from_file_override_and_unset(tmp_path): ...
def test_override_with_malformed_file_is_still_an_error(tmp_path): ...
def test_invalid_value_names_value_and_both_allowed(tmp_path): ...   # "generate", 1, ""
def test_no_root_resolves_unset_with_looked_at_none(tmp_path): ...
def test_subdirectory_reads_root_file_and_ignores_nested_pyproject(tmp_path): ...
```

### Changes Required

**See `design.md` for:** D2, D3, Data model, The severity table, `LEGACY_CATEGORY` paragraph, Appendix A.

- [x] `tests/test_validation/test_execution_target.py` (NEW). *Done `00adb102`.*
- [x] `tests/fixtures/l6/native_lowered.toml` (NEW): an empty lowered set. Codes move into it only in Phase 8, each with its audit row (review S3). *Done.*
- [x] `src/agentic_mbse/validation/execution_target.py` (NEW). Every generator-only candidate in `LEGACY_CATEGORY` starts as `LEGACY_KEPT`. `resolve_target` uses `find_project_root` (`project_root.py:19`) unchanged and `read_toolkit_table`. *Done.*

### Validation

- [x] New tests pass; full suite green rule; ruff and mypy on touched files. *Done: severity table test passes cell by cell; full suite = baseline 6; no new mypy or ruff findings.*

**What we know works:** severity is one tested table; target resolution covers file, override, unset, no root and every fault.

**Done when:** the policy level of two spec criteria is proven by unit test: § Check failures fail under every target ("under `native`, none is counted in the INFO summary") and § Where the setting is read from (root file used, nested file ignored, no root gives unset). Both close end to end through the CLI in Phase 4, together with § Settings states bullets 4–7.

---

## Phase 4: Runner crash handling, JSON report, and the target in L6

### Goal

A crashed level fails the run. `validate` gains `--execution-target` and `--json-report`. L6 resolves the target first, prints the target metric, and stops with `L6_SETTING_INVALID` on any setting error (`design.md` D3, D6, D8, Runner and report).

### Assumption Under Test

The runner can record a crash and carry the override and pass notes without knowing anything about targets. The report schema can hold every issue of every level, including crashed ones and unstructured strings.

### Test Stencil

```python
# tests/test_validation/test_runner_crash.py
@pytest.mark.parametrize("level", [3, 6])
def test_level_that_raises_is_failed_and_named(monkeypatch, level, fixture_project):
    make_level_raise(monkeypatch, level, RuntimeError("boom"))
    code, out = run_cli("validate", f"--level={level}", fixture_project)
    assert code == 1 and f"Level {level} crashed: RuntimeError: boom" in out
    assert "All quality checks passed" not in out

# tests/test_validation/test_json_report.py
def test_report_holds_every_issue_warning_and_pass_note(tmp_path, fixture_project): ...
def test_unstructured_plus_structured_equals_issues_per_level(): ...   # design note m3
def test_crashed_level_appears_with_status_crashed(): ...
def test_missing_report_parent_exits_2(): ...
def test_report_is_byte_identical_across_runs(): ...   # I8

# tests/test_validation/test_l6_settings_cli.py
@pytest.mark.parametrize("override", [None, "generated", "native"])
def test_malformed_pyproject_exits_1_naming_file_and_parse_error(override, tmp_path): ...
def test_unknown_value_exits_1_naming_value_and_allowed(tmp_path): ...
def test_unknown_key_or_underscore_table_exits_1_naming_key(tmp_path): ...
def test_override_wins_and_output_says_so(tmp_path): ...   # both directions
def test_no_root_metric_names_execution_target_option(tmp_path): ...
def test_target_metric_names_source_every_run(tmp_path): ...
def test_bad_holdout_guard_does_not_fail_validate(tmp_path): ...
def test_execution_target_with_level_1_to_5_is_accepted_and_unused(tmp_path): ...
```

### Changes Required

**See `design.md` for:** Runner and report, D3, D6, D8, Implementation Notes "JSON report schema", "What a user sees in L6" item 1.

- [x] Tests above (NEW files). A shared fixture-project builder in `tests/helpers/l6_projects.py` (NEW): writes `work/BACKLOG.md`, a `models/` tree and an optional `pyproject.toml`; later phases add model shapes to it. *Done `2afa2a2c`.*
- [x] `src/agentic_mbse/sysml/types.py`: add `L6_CHECK_ERROR`, `L6_SETTING_INVALID`, `LEVEL_CRASHED` (the `L6_SUBSET_*` codes land in Phase 5). *Done.*
- [x] `src/agentic_mbse/validation/common.py`: `QualityCheckResult` gains `summarized`, `pass_note`, `report_detail` (default empty); `AggregatedResult` collects pass notes and joins them with the pinned note; `check_error_issue()`. *Done; `AggregatedResult` also carries `constraint_extractions` and `wall_time_s` for the report's `run_info`.*
- [x] `src/agentic_mbse/validation/runner.py:128-137`: crash → failed result with one `LEVEL_CRASHED` ERROR, level number from its `QUALITY_CHECKS` position, traceback only with `--verbose`, fail-fast stops. Thread the override to L6 with `functools.partial` like L2 (`:94-100`). Final line at `:155-157` prints all notes. *Done.*
- [x] `src/agentic_mbse/validation/report.py` (NEW): `validate-report/v1` per the schema note. *Done.*
- [x] `src/agentic_mbse/validation/level6_architecture.py` `validate_architecture` (`:930` area): new `execution_target` keyword; resolve first; on `TargetSettingError` emit `L6_SETTING_INVALID` and the target metric, run no checks, fail. Otherwise emit the target metric and continue with today's checks. *Done.*
- [x] `src/agentic_mbse/cli/__init__.py` (`cmd_validate` `:338`, argparse near `:758`): `--execution-target {generated,native}`, `--json-report PATH` (parent must exist, else exit 2; write failure exits 1). *Done.*

### Validation

- [x] New tests pass; full suite green rule; ruff and mypy on touched files. *Done: full suite = baseline 6; mypy 97 (baseline set).*
- [x] Manual: `uv run agentic-mbse validate --level=6 --json-report /tmp/r.json tests/fixtures/sample_models` writes a report; `jq '.levels[0].status'` reads `passed` or `failed`, never missing. *Done: `levels[0].status` = `passed`; `run_info.constraint_extractions` = 1.*

**What we know works:** a crash can no longer read as a pass; every setting fault fails L6 under every target and override; the report exists for every run.

**Done when:** spec § Settings states bullets 4–7; § One key set, two readers bullet 3; § Where the setting is read from (all three); § Check failures fail under every target bullet 3 (crashed level, L6 and one other); § Structured report except the profile content and the dc3-sized count (Phase 5).

---

## Phase 5: L6 consumes the contract

### Goal

L6 runs the contract first over the shared model and facts, passes the String subject ids to the legacy design-attribute check, and presents every result through `display()`: verdict, coverage and scope lines, the native summary, issue order, the final-line note, the report's `profile`, "shadowed by", and the renamed title.

### Assumption Under Test

The contract's result alone is enough to render every spec presentation criterion with no outcome logic in L6 (I3). Suppressing the legacy String error by subject id loses no String anywhere (B6).

### Test Stencil (write first; one fixture model per verdict)

```python
# tests/test_validation/test_l6_contract.py
VERDICT_FIXTURES = {  # tests/fixtures/l6/contract/<name>/models/*.sysml
    "refused": ..., "refused_incomplete": ..., "incomplete": ..., "unconfirmed": ...,
    "clear": ..., "clear_unassessed": ..., "b8_shadowed": ..., "strings_both_spellings": ...,
    "excluded_non_numerical": ..., "native_correctness_error": ..., "string_outside_roots": ...,
    "invocation_rhs_and_multiplicity": ...,
}
BANNED = ["generated-ready", "generation-ready", "ready to generate", "will generate",
          "generator accepts", "readiness"]

@pytest.mark.syside
@pytest.mark.parametrize("target", ["unset", "generated", "native"])
@pytest.mark.parametrize("name", VERDICT_FIXTURES)
def test_stdout_and_report_have_no_banned_wording(name, target, tmp_path): ...   # I9

def test_one_refused_finding_exit_code_by_target(): ...   # generated 1, native 0, unset 0 + note
def test_unset_note_printed_even_with_no_generator_findings(): ...
def test_native_summary_findings_all_in_report_with_rule_reason_location(): ...
def test_verdict_line_fields_and_never_clean_ready_passed(): ...
def test_refused_incomplete_puts_refused_count_before_incomplete(): ...
def test_clear_line_and_coverage_limit_line(): ...
def test_incomplete_fails_under_generated_and_warns_under_unset(): ...
def test_unconfirmed_is_never_error_and_names_by_design_context(): ...
def test_b8_shadowed_by_names_the_refused_finding_and_outcome_stays_unconfirmed(): ...
def test_unverified_error_generated_warning_unset_separate_warning_native(): ...
def test_excluded_is_warning_with_reason_under_generated(): ...
def test_unassessed_count_in_verdict_line_and_one_warning(): ...
def test_final_line_says_generated_compatibility_not_established(): ...
def test_level_title_is_architecture_and_generator_subset(): ...
def test_both_string_spellings_inside_and_outside_designs_are_omitted_no_unextractable(): ...
def test_string_outside_every_generator_root_is_still_omitted(): ...   # B6
def test_native_correctness_error_stays_error_under_native(): ...
def test_invocation_callable_at_attribute_and_part_multiplicity_unresolved_reported(): ...
def test_contract_crash_is_check_error_under_every_target(monkeypatch): ...
def test_dc3_sized_report_holds_every_evaluator_finding(): ...   # synthetic, tests/helpers/subset_synthetic.py

# tests/test_subset_coverage.py
def test_coverage_list_pinned_to_its_version(): ...
def test_coverage_list_matches_no_rule_rows_of_the_matrix_fixture(): ...   # as tests/test_subset_matrix.py does
def test_subset_profile_version_and_digest_unchanged_from_ebb3d467(): ...   # I4
```

The `unconfirmed` and `beneath_refused_multiplicity` shapes can be taken from Item 1's matrix fixtures under `tests/fixtures/subset_profile/`. B8 copies dc3's calc-owned-assertion shape (Item 1 `evidence/acceptance.md:21-31`).

### Changes Required

**See `design.md` for:** Core Concept, D8, D9, D10, D11, D13, "What a user sees in L6", Final line, I3, I5, I9, Implementation Notes "Matrix row closing".

- [x] Tests and fixtures above (NEW). *Done: 13 fixtures (the stencil's 12 plus `beneath_refused_multiplicity`), `test_l6_contract.py` (112 cases), `test_subset_coverage.py` (4).*
- [x] `src/agentic_mbse/sysml/subset_coverage.py` (NEW): `SUBSET_COVERAGE_VERSION`, the list (DEEP-QUALIFIED-WIRING, ES-002, ES-008, ES-009, ES-010 refusal side, CALC-DEF-BARE-RESULT, the follow-up sites).
- [x] `src/agentic_mbse/sysml/types.py`: the `L6_SUBSET_*` codes from D8 except the two advisory codes (Phase 6). Rename the `:82` comment.
- [x] `src/agentic_mbse/validation/subset_presentation.py` (NEW): `present(...)` returning issues, `summarized`, metrics, `pass_note`, report detail; shadowed-by from subject ids (D9); D13 ordering.
- [x] `src/agentic_mbse/validation/level6_architecture.py`: contract first (`extract_subset_facts(model, constraint_facts=session...)`, `evaluate_subset_profile`), wrapped so a crash is `L6_CHECK_ERROR` and the verdict line reads `not computed`; pass `string_subjects` into `check_design_attr_completeness` (D10; `None` if the contract failed); title rename at `:3`, `:935`, `:943`, `:951`, `:963`, `:1015`.
- [x] `src/agentic_mbse/validation/runner.py:54`: title rename. Update `tests/test_sysml_quality_checks.py:742`, `:751` (record in notes).
- [x] `src/agentic_mbse/validation/report.py`: fill L6's `profile`. *Done without editing `report.py`: L6 puts the profile in `report_detail`, which the report already writes as `profile`.*
- [x] Matrix: close MULTIPLICITY-SHAPE in `tests/fixtures/subset_profile/inventory/matrix.toml` citing the new test; regenerate `matrix.md` with `scripts/subset_profile/render_matrix.py`; `tests/test_subset_matrix.py` still passes.
- [x] Grep tests, `skills/` and `scripts/` for the old title and for strings the new L6 output changes (design risk "text output changes"); fix or record each hit.

### Validation

- [x] New tests pass; full suite green rule; ruff and mypy on touched files. *Done: see Phase 5 Completion.*
- [x] Manual: `--level=6 --execution-target=generated` on `tests/fixtures/l6/contract/refused_incomplete` prints the verdict line with the refused count first, and the first printed issue lines are refusals. *Done: verdict line `refused_incomplete: 1 refused, then incomplete: 1 unverified; 0 unassessed constraints; not a generation check`; first issue line `ERROR: refused (subset-profile/v1): invocation-callable/unsupported_callable in attribute_value: ...`, then the unverified ERROR.*

**What we know works:** the contract is wired into L6, with every target's presentation, the String replacement and the report profile.

**Done when:** spec § Settings states bullets 1–3; § Presentation (all); § Structured report (all); § Both String spellings (test half); § Library additions bullets 1, 2, 4; § Check failures bullets 4 (contract crash) and 5 (native-correctness error stays ERROR).

---

## Phase 6: Advisories and the extracted `falls_to_text_fallback`

### Goal

The two routed advisories (UNSUPPORTED-SHAPE-MESSAGE, WRAPPER-SHAPE) in `sysml/subset_advisories.py`, detected through the walkers' own code, with `reconstruct_expression`'s output proven unchanged (`design.md` D12, D15).

### Assumption Under Test

`reconstruct_expression`'s dispatch can be refactored into a shared predicate without changing a single output text. Item 2's agent depends on that function, so this is the one place this item edits shared library logic.

### Test Stencil

```python
# tests/test_sysml/test_text_fallback.py
@pytest.mark.syside
def test_reconstruct_expression_output_unchanged_on_every_fixture_expression():
    recorded = json.loads(Path("tests/fixtures/l6/reconstruct_texts_ebb3d467.json").read_text())
    assert reconstruct_all("tests/fixtures/**/*.sysml") == recorded

def test_falls_to_text_fallback_true_for_constructor_false_for_if_as_istype(): ...
def test_text_fallback_nodes_raises_where_reconstruction_raises(): ...   # Cell.metadata

# tests/test_validation/test_l6_advisories.py
@pytest.mark.parametrize("target", ["unset", "generated", "native"])
def test_opaque_expression_fires_on_new_cell_and_not_on_plain_ref(target): ...
def test_wrapper_fires_on_collect_select_and_not_on_bare_sum(target): ...
def test_wrapper_ignores_abs_inside_sum(): ...   # ES-005's refusal, not this advisory
def test_advisory_at_most_warning_info_under_native(): ...
def test_walker_semantic_evidence_error_is_advisory_unverified_warning(): ...
    # sum(cells.?{ in c : Cell; c.ok }.mass) and Cell.metadata; L6 passes under unset
def test_other_walker_exception_is_check_error(monkeypatch): ...
```

### Changes Required

**See `design.md` for:** D12, D15, I1, I4, Implementation Notes "The reconstruction predicate".

- [ ] **First, before touching `expression.py`:** confirm `git diff ebb3d467 -- src/agentic_mbse/sysml/expression.py` is empty, then record `reconstruct_expression`'s text for every value expression in `tests/fixtures/**/*.sysml` into `tests/fixtures/l6/reconstruct_texts_ebb3d467.json` with a small recording script in `scripts/l6_subset/record_reconstruct_texts.py` (NEW). Commit the fixture before the refactor.
- [ ] Tests above (NEW), advisory fixtures from `spikes/s2_advisory_shapes.py`'s candidates in `tests/fixtures/l6/advisories/`.
- [ ] `src/agentic_mbse/sysml/expression.py:298-356`: one ordered dispatch; `falls_to_text_fallback`; `text_fallback_nodes`. Additive public names only.
- [ ] `src/agentic_mbse/sysml/subset_advisories.py` (NEW): opaque-expression and wrapper advisories over the contract's expression sites; wrapper filtered to `KNOWN_WRAPPER_FUNCTIONS` (`aggregation.py:72`); `SemanticEvidenceError` → advisory-unverified record.
- [ ] `src/agentic_mbse/sysml/types.py`: `L6_SUBSET_ADVISORY`, `L6_SUBSET_ADVISORY_UNVERIFIED`.
- [ ] `level6_architecture.py` and `subset_presentation.py`: call the advisories after the legacy checks; render; native summary counts advisories; advisory-unverified stays a WARNING outside the summary.

### Validation

- [ ] Output-unchanged test passes against the recorded fixture; new tests pass; full suite green rule; ruff and mypy.
- [ ] Manual: `--level=6` on the spike's `sum(cells.?{...}.mass)` fixture under unset passes with one `L6_SUBSET_ADVISORY_UNVERIFIED` WARNING.

**What we know works:** both advisories fire where they should, never block, and the shared reconstruction function is byte-for-byte unchanged.

**Done when:** spec § Library additions bullet 3 (each advisory fires and does not fire, at most WARNING, INFO under native); I4's `expression.py` clause.

---

## Phase 7: Exception sites

### Goal

Every site in `design.md` Appendix B reports `L6_CHECK_ERROR` at the narrowest safe scope, makes no dependent finding, and shows `not computed` for an affected count. D16 narrows the unextractable catch.

### Assumption Under Test

The propagated helpers reach a per-element handler, not the whole check (verified by reading in the design review; proven here by test). Retyping the evaluator's deliberate raises misses none.

### Test Stencil

```python
# tests/test_validation/test_l6_check_errors.py
SITES = [  # one entry per Appendix B row; how each forces its exception
    Site("level6_architecture.py:191", force=raise_in("elements_of_type", ...), check="..."),
    ...
    Site("level6_architecture.py:723", force=..., no_finding="L6_CALC_DEF_NO_INSTANTIATION"),
    Site("adr002.py:423", force=..., no_finding={"V2_DYNAMIC_EXPRESSION", "V4_UNSUPPORTED_OPERATOR",
                                                 "L6_DESIGN_ATTR_UNEXTRACTABLE"}),
]
@pytest.mark.parametrize("target", ["unset", "generated", "native"])
@pytest.mark.parametrize("site", SITES, ids=str)
def test_site_failure_is_check_error_naming_check(site, target, monkeypatch):
    result = run_l6_with(site.force, target, monkeypatch)
    assert has_issue(result, "L6_CHECK_ERROR", names=site.check) and not result.success
    assert site.no_finding is None or not has_code(result, site.no_finding)
    assert not in_native_summary(result, "L6_CHECK_ERROR")

def test_failed_counts_print_not_computed(): ...   # :973, :978
def test_unextractable_catch_only_takes_evaluator_signal(monkeypatch): ...   # D16, :540
def test_evaluator_deliberate_raises_are_unextractable_subclasses(): ...
def test_existing_value_type_error_callers_still_catch(): ...
```

Drive each site with fakes (`SysideAdapter.elements_of_type`, `SysideAdapter.is_instance`, or the wrapped helper) where possible; mark the rest `syside` (S4).

### Changes Required

**See `design.md` for:** Appendix B (the site list and each change), D4, D16, I1, Implementation Notes "Exception-site pattern".

- [ ] `tests/test_validation/test_l6_check_errors.py` (NEW).
- [ ] `src/agentic_mbse/sysml/expression.py:466-567`: `Unextractable`, `UnextractableValueError`, `UnextractableTypeError`; each deliberate raise uses the subclass of its current type.
- [ ] `src/agentic_mbse/validation/level6_architecture.py`: every Appendix B site; `:540` catches `Unextractable` only; `validate_architecture` wraps each top-level check call; counts at `:973`, `:978` become `not computed` plus `L6_CHECK_ERROR`. Keep the display-only fallbacks in `get_qualified_name` and `get_element_location`.
- [ ] `src/agentic_mbse/validation/adr002.py`: every Appendix B site; delete `_get_calc_usage_names` (`:268`).
- [ ] Before editing, reconcile Appendix B's line numbers with the current file (they are at `ebb3d467`; Phase 5 moved some). Record the mapping in notes.

### Validation

- [ ] New tests pass; full suite green rule (existing tests that asserted a swallowed failure now see `L6_CHECK_ERROR`: record each); ruff and mypy.
- [ ] Manual: `grep -n "except Exception" src/agentic_mbse/validation/level6_architecture.py src/agentic_mbse/validation/adr002.py` lists only sites that report, plus the two display-only fallbacks.

**What we know works:** no failed inspection in L6 reads as clean, as zero, or as a model defect.

**Done when:** spec § Check failures fail under every target bullets 1 and 2 (every site under every target; the five over-reporting sites make no dependent finding).

---

## Phase 8: Legacy-check audit dispositions and codegen citations

### Goal

`evidence/legacy-l6-audit.md` with one row per L6 code plus manifest and setup failures, the four native lowerings moved into `LEGACY_CATEGORY` together with their rows, and every codegen citation corrected or removed.

### Assumption Under Test

Appendix A's four confirmed rows are the only lowerings with evidence. The table test from Phase 3 keeps code and evidence in step.

### Test Stencil

```python
# tests/test_validation/test_execution_target.py (extend)
def test_lowered_set_is_exactly_the_four_evidenced_codes():
    assert lowered(LEGACY_CATEGORY) == {"L6_MISSING_QUALIFIED_NAME", "L6_ANONYMOUS_RETURN",
                                        "L6_CALC_DEF_NO_INSTANTIATION", "L6_BODY_ASSIGNMENT_IMPL_LOSS"}
    assert lowered(LEGACY_CATEGORY) == load_toml("tests/fixtures/l6/native_lowered.toml")

def test_audit_lowered_table_matches_fixture():   # parses the evidence file's "lowered under native" table
    ...
# tests/test_validation/test_l6_contract.py (extend)
def test_lowered_code_is_native_summary_under_native_and_unchanged_under_others(): ...
def test_kept_code_unchanged_under_every_target(): ...
```

### Changes Required

**See `design.md` for:** Appendix A, B2, `LEGACY_CATEGORY` paragraph, Implementation Notes "Codegen citations", I5.

- [ ] `evidence/legacy-l6-audit.md` (NEW): from Appendix A and `spikes/f4-codegen-citations.md`. Columns: what the check does, today's severity, category, severity per target, evidence. Separate table of lowerings under `native`. Note the simple-name collision in `L6_CALC_DEF_NO_INSTANTIATION` (`level6_architecture.py:700-762`) and the "kept (follow-up)" rows pointing at backlog `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES`.
- [ ] `tests/fixtures/l6/native_lowered.toml`: add the four codes. `execution_target.py`: move the same four to `LEGACY_GENERATOR_ONLY`, in the same commit.
- [ ] `level6_architecture.py` (`:847`, the "codegen's V8" reference near `:584`, others in `f4-codegen-citations.md`), `adr002.py:478`, `common.py:82`: correct or delete each citation. Never cite a working-tree line; read codegen only from a `git archive b5663c07` export.

### Validation

- [ ] Tests pass; full suite green rule; ruff and mypy.
- [ ] Manual: `grep -n "codegen\|V8\|hierarchy_resolver" src/agentic_mbse/validation/level6_architecture.py src/agentic_mbse/validation/adr002.py src/agentic_mbse/validation/common.py`; every hit matches a row in `f4-codegen-citations.md` marked accurate, or is a pointer to the follow-up.

**What we know works:** `native` relaxes only what has evidence, and the code and the audit cannot drift apart.

**Done when:** spec § Audit and docs bullets 1 and 2.

---

## Phase 9: `init` writes the setting

### Goal

`init --execution-target`, the interactive prompt, and the noninteractive message, with byte-preserving insertion and every refusal case (`design.md` D7, the `init` table, I7).

### Assumption Under Test

Bet B3: a text insert verified by `tomllib` against the whole parsed document is enough to add one key safely.

### Test Stencil

```python
# tests/test_init_execution_target.py
GOLDEN = Path("tests/fixtures/l6/init_golden")   # <case>/before.toml, <case>/after.toml
@pytest.mark.parametrize("force", [False, True])
@pytest.mark.parametrize("case", ["comments_and_blank_lines", "existing_research_table",
                                  "table_present_no_key", "no_table", "crlf", "no_final_newline"])
def test_golden_insert_is_byte_exact_and_parses(case, force, tmp_path):
    run_init(tmp_path, case, "--execution-target=generated", force=force)
    assert (tmp_path / "pyproject.toml").read_bytes() == (GOLDEN / case / "after.toml").read_bytes()
    assert parsed(after) == parsed(before) | one_key

def test_no_file_creates_only_the_table(): ...
@pytest.mark.parametrize("layout", ["symlink", "hardlink", "bom", "not_utf8", "inline_table",
                                    "dotted_keys", "two_headers", "existing_defect"])
def test_refused_layout_writes_nothing_prints_line_and_exits_1(layout): ...
def test_existing_value_never_changed_by_reinit_force_or_disagreeing_option(): ...
def test_interactive_prompt_default_leaves_unset(monkeypatch): ...
def test_noninteractive_no_option_writes_nothing_and_prints_line_and_init_form(): ...
def test_rest_of_install_completes_when_setting_step_refuses(): ...
def test_install_commands_leaves_pyproject_untouched(): ...
```

### Changes Required

**See `design.md` for:** D7, the `init` section and its table, refused layouts, Implementation Notes "Insert algorithm".

- [ ] Tests and golden files (NEW).
- [ ] `src/agentic_mbse/project_settings.py`: `add_execution_target(file, value) -> SettingWrite`.
- [ ] `src/agentic_mbse/cli/__init__.py` `cmd_init` (`:369`, argparse near `:804`): `--execution-target`; settings step after the installer saves; prompt only when stdin is a terminal; exit 1 only when the option was given and could not be written, or on a disagreement or defect with the option. `install-commands` never calls it.

### Validation

- [ ] Tests pass; full suite green rule; ruff and mypy.
- [ ] Manual (review m9): in an empty `tmp` directory, run `init --execution-target=native`, then `uv run --directory <dir> python -c pass` and `uv lock --directory <dir>`. Record what uv does with a `pyproject.toml` that has no `[project]`. If uv errors where it would not with no file, stop and report: the "create a file holding only the table" row then needs an owner call.
- [ ] Manual: `init` in a `tmp` copy of a project, then `validate --level=6` shows `generated (from <path>)` or `native (...)`, confirming `init` and L6 read the same file.

**What we know works:** `init` can set the target without ever damaging a committed file.

**Done when:** spec § `init` (all seven bullets).

---

## Phase 10: Docs and the CLAUDE.md L6 line

### Goal

README, `skills/model-validation/SKILL.md` and L6 output each state the profile version, what was assessed, that it is incomplete relative to the generator, and that L6 is not `sysml-codegen check` (described as the future boundary, no command shown). `docs/research-seam.md` describes the shared key set.

### Assumption Under Test

The shipped text can state the boundary without any banned wording.

### Test Stencil

```python
# tests/test_shipped_text.py (extend)
@pytest.mark.parametrize("path", ["README.md", "skills/model-validation/SKILL.md"])
def test_doc_states_profile_version_scope_incompleteness_and_not_codegen_check(path):
    text = Path(path).read_text().lower()
    assert "subset-profile/v1" in text and "not a generation check" in text ...
    assert not any(b in text for b in BANNED)

def test_research_seam_describes_shared_key_set(): ...
def test_model_validation_table_row_uses_new_l6_title(): ...
```

The L6 output half is already asserted in Phase 5.

### Changes Required

**See `design.md` for:** Component Overview "Docs"; spec § Docs.

- [ ] `tests/test_shipped_text.py`: additions above.
- [ ] `README.md`, `skills/model-validation/SKILL.md` (including its level table row): the four statements; the setting and how to set it.
- [ ] `docs/research-seam.md:350`, `:414-415`: the shared key set; the guard now accepts `execution-target` (the intended relaxation).
- [ ] `CLAUDE.md` § Architecture, Level 6 bullet: change "Architecture & pipeline readiness (ADR-002, manifests, codegen)" to the new title with a short description. One line only; not the Change Coordination proposal Item 6 reserves.
- [ ] Re-run `uv run agentic-mbse install-commands --assistant claude` so the local install matches `skills/` (CLAUDE.md § Change Coordination).

### Validation

- [ ] Tests pass; full suite green rule; ruff on touched test files.

**What we know works:** every user-facing text states the boundary the same way.

**Done when:** spec § Audit and docs bullet 3.

---

## Phase 11: The before/after safeguard and consumer evidence

### Goal

Run Appendix C in full on the finished branch, and write the dc3 evidence from the JSON report.

### Assumption Under Test

Bet B4: nothing that passes `validate --complete` today on the three consumer trees hides a crash or a swallowed failure. If it does, that is the R3-2 case the owner reserved.

### Test Stencil

```python
# tests/test_l6_run_consumers.py (NEW): the script's pure parts, no consumer trees needed
def test_parses_base_level_status_including_crashed_recorded_as_pass(): ...
def test_flags_pass_to_fail_and_l1_l5_difference_first(): ...
def test_time_criterion_fails_above_1_10(): ...
def test_refuses_dirty_branch_or_head_mismatch(): ...
```

### Changes Required

**See `design.md` for:** Appendix C (all 12 steps; stop-and-show in steps 9 and 10), risk "Retyping the evaluator's raises".

- [ ] `scripts/l6_subset/run_consumers.py`: complete `before-after` (all trees; steps 1, 9–12) and `l6-evidence`.
- [ ] `tests/test_l6_run_consumers.py` (NEW).
- [ ] Commit everything; run `before-after --base ebb3d467 --branch HEAD` alone on an idle machine. Writes `evidence/before-after.{json,md}`.
- [ ] Run `l6-evidence`. Writes `evidence/dc3-baseline-l6.md` (generated and unset runs) and `evidence/dc3-repaired-l6.md`, every count read from the report.
- [ ] `evidence/repository-checks.md`: final `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/` results against `evidence/baseline.md`; the `syside`-marked tests (`uv run pytest -m syside --collect-only -q`); whether the licence was present; anything skipped.

### Validation

- [ ] Expected (from the spike and design): dc3 baseline 236 refused / 32 omitted / 6 unconfirmed / 50 unverified, `refused_incomplete`, B1–B6 refused ERROR, B7 omitted WARNING, B8 unconfirmed WARNING shadowed by B1. dc3 `60b44d5` `clear` with 30 omitted. New omitted WARNINGs 131 / 30 / 32. `L6_DESIGN_ATTR_UNEXTRACTABLE` fusion-tea 108 → 108, dc3 baseline 3 → 0. `run_info.constraint_extractions == 1`. Any difference is explained in the evidence.
- [ ] dc3 and fusion-tea HEAD and `git status` unchanged before and after.
- [ ] **Stop-and-show.** If the script exits 1 (any level or run goes from pass to fail, any L1–L5 issue line differs, or fusion-tea branch time exceeds 1.10 × base), stop. Do not merge, do not "fix" toward a pass. Report to the orchestrator with the flagged rows from `before-after.md`; the orchestrator shows the owner before merge.

**What we know works:** the branch's effect on real consumer trees is measured, and any pass→fail is in the owner's hands.

**Done when:** spec § Consumer evidence (all three); § Both String spellings (evidence half); § Audit and docs bullet 4.

---

## Spec criteria trace

| Spec group (`spec.md` § Success Criteria) | Phase | Test or evidence |
|---|---|---|
| Settings states 1–3 (generated, native, unset with a refused finding) | 5 | `tests/test_validation/test_l6_contract.py` |
| Settings states 4–7 (malformed, unknown value, unknown key, override) | 4 | `tests/test_validation/test_l6_settings_cli.py` |
| One key set, two readers 1, 2, 4, 5 | 2 | `tests/test_project_settings.py`, `tests/test_research/test_holdout.py` |
| One key set, two readers 3 (bad holdout-guard does not fail validate) | 4 | `test_l6_settings_cli.py` |
| Where the setting is read from (3) | 3, 4 | `test_execution_target.py`, `test_l6_settings_cli.py` |
| `init` (7) | 9 | `tests/test_init_execution_target.py` |
| Presentation (12) | 5 | `test_l6_contract.py` |
| Structured report | 4, 5 | `test_json_report.py`, `test_l6_contract.py` |
| Check failures 1, 2 (sites, no dependent finding) | 7 | `test_l6_check_errors.py` |
| Check failures 3 (crashed level) | 4 | `test_runner_crash.py` |
| Check failures 4, 5 (evaluator crash; native-correctness stays ERROR) | 5 | `test_l6_contract.py` |
| Both String spellings | 5, 11 | `test_l6_contract.py`, `evidence/dc3-baseline-l6.md` |
| Library additions 1, 2 (coverage version; profile version unchanged) | 5 | `tests/test_subset_coverage.py` |
| Library additions 3 (advisories) | 6 | `tests/test_validation/test_l6_advisories.py` |
| Library additions 4 (UNSUPPORTED-RHS, MULTIPLICITY-SHAPE; matrix row closed) | 5 | `test_l6_contract.py`, `matrix.toml` |
| Consumer evidence (3) | 11 | `evidence/dc3-baseline-l6.md`, `dc3-repaired-l6.md`, `before-after.md` |
| Audit and docs 1, 2 (audit; citations) | 8 | `evidence/legacy-l6-audit.md` |
| Audit and docs 3 (docs) | 10 | `tests/test_shipped_text.py` |
| Audit and docs 4 (repo checks) | 11 | `evidence/repository-checks.md` |

---

## Environment Setup

See CLAUDE.md. All commands through `uv run`. Model-loading tests need `SYSIDE_LICENSE_KEY` in `.env`. Consumer trees are read only through `git archive` exports under `/tmp`, never the checkouts in `~/src/dc3` or `~/src/fusion-tea`. sysml-codegen is read only from a `git archive b5663c07` export.

## Risk Management

See `design.md#potential-risks`. Phase-specific mitigations:

- **Phase 1:** the session is the only change, measured against a recorded baseline, with an explicit stop. If B5 fails, the remedy is a design question, not a local patch.
- **Phase 5:** the largest phase. If it runs past one session, split at the boundary between "contract in, verdict lines and String" and "native summary, shadowed-by, final line, report profile", and check off what is done.
- **Phase 6:** the reconstruction texts are recorded and committed before `expression.py` changes, so the comparison cannot drift with the code.
- **Phase 7:** Appendix B's line numbers are at `ebb3d467`; reconcile them first. A deliberate evaluator raise that was missed shows up as a new `L6_CHECK_ERROR` in Phase 11's UNEXTRACTABLE count.
- **Phase 9:** uv's handling of a `[project]`-less file is checked by hand before the "no file" row is relied on.
- **Phase 11:** a pass→fail is the owner's call, not the implementer's.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-10-19. Stopped 2026-10-18 at the stop condition; resumed on the orchestrator's answers.
**Actual Changes:**
- Step 1a, committed: `evidence/baseline.md` (repo checks at `ebb3d467`), `scripts/l6_subset/run_consumers.py` (`baseline`, and `session-equality`), `evidence/baseline-consumers.{json,md}`.
- Session, committed `1058e4dc` after the orchestrator's answers: `validation/session.py` (`ValidationSession`, `active_session()`, `constraint_facts(model)`), `load_sysml_model` consults the session (`common.py`), L4 and L6 call `constraint_facts` (`level4_constraints.py:65`, `level6_architecture.py:650`), `extract_subset_facts(..., constraint_facts=...)` keyword (`subset_extraction.py`), `run_all_checks` wraps the level loop (`runner.py`), `syside` marker (`pyproject.toml`), `tests/test_validation/test_session.py`. Two existing tests now patch `constraint_facts` instead of the removed module name (`test_item12_checks.py:211`, `test_level4_reconciliation.py:71`).
- Stop evidence: `evidence/session-check.md`, `evidence/session-equality.json`, `evidence/session-check-scripts/`.

**Issues:**
- The with/without test fails on `tests/fixtures/sump_pump`. That folder holds three copies of the same packages, and today's code, with no session, gives different L2, L4 and L6 results from one fresh load to the next on it (L6's `pump_fit` ERROR on 5 to 10 of 10 loads). Its three subfolders, and every other fixture, are stable. So the session is not the cause, but the plan's rule is "any difference stops", so this is the owner's call.
- On all three consumer trees, every level's full result is identical with and without the session, with one load and one extraction, in about half the time (fusion-tea 407.8 s → 205.7 s, in process).

**Orchestrator decisions, 2026-10-18** (each [AGENT]):
1. Accepted: the `sump_pump` difference comes from the fixture already varying between loads with today's code (three copies of the same packages loaded together), not from the session. B5 holds.
2. Approved: the with/without test uses `sump_pump/right`, `sump_pump/seed` and `sump_pump/wrong` as three separate fixtures, with a comment pointing to the backlog row. No double-run tolerance.
3. Already filed: backlog `VALIDATE-SUMP-PUMP-NONDETERMINISM` (since Item 1's close); the orchestrator added the L2/L4 evidence. No new row.

**Phase 1 close:** `run_consumers.py before-after --base ebb3d467 --branch HEAD --trees fusion-tea --out session-check-before-after` at `00adb102`: base 411.4 s, branch 206.0 s (ratio 0.501, limit 1.10); every level's status and printed block identical; resolved root agrees; siblings unchanged. A first run at `62621ad7` gave the same timing (414.8 → 206.4 s) but flagged a wrong expected root, a bug in the script's comparison (fixed in `5d0bf73c`), so it was rerun. Another agent's test suites ran on the machine during both runs; base and branch ran back to back under the same load.

**Deviations:**
- `sump_pump` (combined) stays in the count and `extract_subset_facts` tests as `sump_pump/right`, which is stable.
- The with/without test runs L2–L6 in order inside one session per fixture, rather than one level per session as in the stencil. This also tests that a level is not changed by an earlier level's use of the shared model, which is what B5 claims.
- The session raises `ValueError` if handed a directory instead of files, because a directory's mtime does not track its files. The levels always pass discovered files.
- Added a `model_loads` counter next to `constraint_extractions`, so the test can check one load per run.
- `run_all_checks` imports `ValidationSession` absolutely, outside the relative/direct-execution `try`, so mypy gets no new errors (`common.py` already uses absolute imports, so direct execution already needed the installed package).
- `run_consumers.py session-equality` was added: the full-result comparison on the consumer trees, which the text-based `before-after` cannot do (text shows only the first five issues per level).
- The repository baseline was taken in the checkout with the Phase 1 edits set aside. A `git archive` export run added 8 environment-only failures from console-script paths, so it was not used.


### Phase 2 Completion
**Completed:** 2026-10-19, `8e455049`.
**Changes:** `src/agentic_mbse/project_settings.py` (`TOOLKIT_KEYS`, `read_toolkit_table`, `ToolkitTable`, `SettingsDefect`, `SettingsFault`, `dotted`); `research/holdout.py` reads through it and keeps its own `holdout-guard` and research-table checks; `tests/test_project_settings.py`; three tests added to `tests/test_research/test_holdout.py`.
**Changed assertion:** `tests/test_research/test_hook_config.py:172` expected "its only key is 'research'"; it now expects "allowed keys are 'execution-target', 'research'" (the design's intended message change).
**Deviations:** `ToolkitTable` carries the file path as well as the table, so the guard's messages still name the file. The reader also reports a non-UTF-8 file as `UNREADABLE` (the guard already treated it as unreadable).

### Phase 3 Completion
**Completed:** 2026-10-19, `00adb102`.
**Changes:** `src/agentic_mbse/validation/execution_target.py`; `tests/test_validation/test_execution_target.py`; `tests/fixtures/l6/native_lowered.toml` (empty).
**Deviations:** `describe_target` (the `Execution target` metric text) lives here beside `resolve_target`, so the metric and the resolution cannot drift. An invalid `execution-target` value is an error even with an override, like a malformed file (the spec names only the malformed case; the same reasoning applies). `resolve_target` raises `ValueError` if handed `Target.UNSET` as an override, since unset is the absence of an override. The legacy-code test reads the 17 codes from the L6 source files, so a new legacy code cannot be missed.


### Phase 4 Completion
**Completed:** 2026-10-19, `2afa2a2c`.
**Changes:** `sysml/types.py` (`L6_CHECK_ERROR`, `L6_SETTING_INVALID`, `LEVEL_CRASHED`); `validation/common.py` (`summarized`, `pass_note`, `report_detail`; `AggregatedResult.pass_notes`, `constraint_extractions`, `wall_time_s`; `check_error_issue()`); `validation/runner.py` (`crashed_result`, override threading, final line); `validation/report.py` (NEW); L6 resolves the target first (`_setting_invalid_result`, `_target_detail`); `cli/__init__.py` (`--execution-target`, `--json-report`). Tests: `tests/helpers/l6_projects.py`, `test_runner_crash.py`, `test_json_report.py`, `test_l6_settings_cli.py`.
**Changed assertions:** `tests/test_cli.py` `TestCmdValidate` builds the argument object by hand; its three tests now also pass `execution_target=None, json_report=None`.
**Deviations:**
- **I8 versus the report schema.** The schema has `run_info.wall_time_s`, a measured time, so the report cannot be byte-identical across runs. The I8 test compares reports with that one field blanked. Everything else is byte-identical. Surfaced here per the capture-fidelity rule; the alternative is to drop `wall_time_s` from the schema.
- The `[tool.agentic_mbse]` defect message now also lists the allowed keys, because the spec asks that the error name "the key and the allowed keys" for that case too (`project_settings.py`, a Phase 2 file).
- The crashed level no longer prints the old `❌ Error running Level N` line; it prints as a failed level with its `LEVEL_CRASHED` issue. `run_consumers.py`'s base-side parser still reads the old line for the base revision.
- The report's per-issue `display` is the issue's severity: an issue reaches `issues` only as ERROR or WARNING, and summarized results are in `summarized`.
- `agentic_mbse.version` in the report is the source tree's `__version__`, so an export run reports its own version, not the venv's metadata.


### Phase 5 Completion
**Completed:** 2026-10-19, commit recorded in git log ("L6 runs the subset contract first ...").
**Changes:** `sysml/types.py` (six `L6_SUBSET_*` codes; L6 comment renamed); `sysml/subset_coverage.py` (NEW); `validation/subset_presentation.py` (NEW: `present`, `string_subjects`, `shadowed_by`); L6 runs the contract first (`_run_contract`, crash → `L6_CHECK_ERROR` from `subset_profile`), passes `string_subjects` to `check_design_attr_completeness`, shows every issue through `present`, and is titled through `LEVEL_NAME`; `runner.py` title. Fixtures `tests/fixtures/l6/contract/*`; tests `test_l6_contract.py`, `test_subset_coverage.py`. Matrix row closed in `matrix.toml`; `matrix.md` re-rendered.
**Checks:** full suite 6 failed / 4196 passed; the 6 are the baseline list. mypy 97 errors (baseline). Touched files pass `ruff format --check`; `ruff check` is clean except the baseline E712s below.
**Changed assertions:** `tests/test_sysml_quality_checks.py:742`, `:751` (and the class docstring at `:781`) now expect "Architecture & Generator Subset" (the rename). The file was not `ruff format`-clean before; formatting it, per the green rule, reflowed 58 lines without changing any test. Its four E712 findings are baseline findings and were left alone.
**Decisions and deviations:**
- **No Item 1 probe gives verdict `unconfirmed`** (every probe is evidence for a listed pair). The `unconfirmed` fixture is a non-numerical asserted constraint owned by an action def (`constraint-predicate` / `non_numerical_predicate` / `owner_other`). The B8 fixture is the same predicate under a calc usage with an asserted constraint, dc3's shape, not dc3's text.
- **`beyond_generator_roots` cannot reach L6**, which always uses the generator's roots. Its message is tested through `present()` on Item 1's `widened_roots.sysml` with a caller root. `beneath_refused_multiplicity` has its own L6 fixture.
- **The native summary line leaves out "0 advisories"** until Phase 6 adds the advisories, so it never prints a count of something that did not run.
- **Shadowed-by applies to any outcome** (D9 says every finding not refused by the shadowing rule), and the report's `shadowed_by` also carries the refused finding's element id.
- **The unassessed WARNING sorts after the contract's omitted findings.** D13 does not place it.
- **The report's severities are the enum's lowercase values** (`error`, `warning`, `info`). Each profile finding's `display` is the table's value (`error`, `warning`, `native_summary`, `count_only`). Admitted findings appear only in the profile, as `count_only`.
- **`pass_note` is set only when L6 passes.**
- **String suppression is by element id.** If SysIDE gives an attribute no id, the legacy error stays.
- **The coverage module's docstring was corrected:** its follow-up sites include agentic-mbse's shared-evidence walkers, not only sysml-codegen sites. `NO_RULE_FAMILIES` keeps the design's printed order, so the test compares it to the matrix as a set.
- **Re-rendering `matrix.md` also fixed one stale `doc:` path** that `matrix.toml` already had right (left over from Item 1's archive move).
- **Grep for the old title:** only `skills/model-validation/SKILL.md:28` and `CLAUDE.md:124` remain. Both are Phase 10 items, so they are unchanged. No test, skill or script asserts the final-line text that unset runs now change.
- **Location text:** contract findings use the contract's `SafeLocation.file`, which prints as `///tmp/...` for a `/tmp` project, as the existing `L6_CONSTRAINT_NON_NUMERICAL` warnings already do. Not normalized here.

---

**Status:** Phases 1–5 complete; Phase 6 next

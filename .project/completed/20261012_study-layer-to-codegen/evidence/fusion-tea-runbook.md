# fusion-tea switch to the study layer installed from sysml-codegen

This runbook moves fusion-tea from its local study layer to the one sysml-codegen ships: the run-study skill, the study-policy template, and the tools in `sysml_codegen.study`. Its local tools become aliases of the installed modules, its nine route modules import the installed package, it declares its two repo-scope gates for `integrate`, and `sysml-codegen install-commands` replaces its local skill. Every committed study record stays valid as written.

It runs after the owner merges and pushes agentic-mbse `study-layer-to-codegen` and then sysml-codegen `study-layer-to-codegen`, in that order (ADR-0008), by the orchestrator or the owner. It runs on the fusion-tea branch that orchestrator step O4 created, which already holds the fusion-tea homes of every line the shipped text dropped. The owner then pushes and merges that branch.

**Sources.** The steps are spec SC9's nine, in its order, with design Appendix H3's actions, rehearsal and expected observations. The drafts cited below live beside this runbook, in agentic-mbse `.project/completed/20261012_study-layer-to-codegen/evidence/` (`$EV`), copied there at close from sysml-codegen's item folder (D10). The rest of that folder (spec, design, plan, audit, dry run, parity cases) is in sysml-codegen git at `4dfe275`, under `.project/active/study-layer-to-codegen/`. Phase 5 wrote this draft while Phase 4 ran in parallel, and Phase 6 checked every citation of Phase 4's files against the files themselves: `$EV/fusion-tea/wrappers/scripts/`, `routes.sed`, `declaration.toml`, `step5-tests.patch`, `SMOKE.md`, and `$EV/rehearsal/{env.sh.example,junit-diff.py}`.

**Names used below.**

- `FT` — the fusion-tea worktree holding the O4 branch. Run every command from `$FT`. Never touch the owner's main fusion-tea checkout.
- `M_AMBSE`, `M_CODEGEN` — the full SHAs of the two merge commits. A pin can name only a pushed commit.
- `EV` — this runbook's directory, `.project/completed/20261012_study-layer-to-codegen/evidence/` in an agentic-mbse checkout.
- `FTC` — in the rehearsal only, a disposable worktree of the O4 branch tip, its venv built on `/usr/bin/python3.12`, fusion-tea's own interpreter (`$EV/rehearsal/README.md` says why).

## Before you start

- `git status --short` in `$FT` is empty, and `git log --oneline b06585709..HEAD` shows O4's text commits, `699b0a74d` and `aab9b9ba3` (with main's commits since `b06585709` when the branch's base is newer): the policy's § 6 "Execution routes", § 12 and § 13, the integration-guide supplement, the `CLAUDE.md` "Study layer" section and the stellarator annex's line 5 (`$EV/fusion-tea/text/`).
- The environment file `$EV/rehearsal/env.sh` (copied from `env.sh.example`, its `FTC` line filled in, kept out of git) is sourced: the licence (present, never printed), fusion-tea's `STOP_PARSER_*` values, and `TEAX_SIMKIT_PATH=$STOP_PARSER_TEAX_ROOT/packages/teax-simkit`.

**Observed in the rehearsal:** rehearsed on 2026-10-12, evidence in `$R=/tmp/study-rehearsal-20261012-124407`. `$FTC` was a detached worktree of O4's tip `699b0a74d`, whose base is fusion-tea `origin/main` `c42ed1d8a`, so `git log b06585709..HEAD` listed 11 commits: O4's one text commit and 10 main commits (`$R/setup-log.txt`). The wheels were built from sysml-codegen `310dfc6` and agentic-mbse `db032d6` (`$R/wheels/sources.json`). sysml-codegen moved to `4a9628c` during the rehearsal (the audit fix pass, which changed `src/sysml_codegen/study/read_coverage.py` and five shipped texts), so these observations cover `310dfc6`. `env.sh` was sourced with the licence present, and `uv sync --frozen --extra e2e` installed agentic-mbse `ac5fb1a` and sysml-codegen `8a758e9`. The Bash tool keeps no shell state between calls, so each call re-sourced `$R/session.sh` (Setup's variables plus `env.sh`) in place of one long-lived shell. That venv ran on uv's managed CPython 3.12.11, not fusion-tea's `/usr/bin/python3.12`; its missing `getrandom` and its zone data outside `sys.base_prefix` explain the original observer's `/dev/urandom` refusals in A and B (`$R/diag/`). The re-rehearsal of steps 5, 8a and 8c kept that venv, so C stays comparable with B, and used wheels rebuilt from sysml-codegen `4d6c2ab` (src as `4a9628c`) and agentic-mbse `130a483`, with step 7's install re-run (`$R/wheels-head/sources.json`, `$R/install-head.txt`).

## Step 1: drift check

fusion-tea's local copies stay in use until this switch, so a fix made to them since `b06585709` must reach sysml-codegen or its fusion-tea home first, or this switch drops it.

```bash
git fetch origin
git diff b06585709 origin/main -- .claude/skills/run-study modeling_project/STUDY_POLICY.md scripts/study scripts/integrate.py docs/integration_seam_operator_guide.md
```

**Expected:** it prints nothing. If it prints a change, stop until that change is in sysml-codegen (an ordinary change there) or in its fusion-tea home (`$EV/read-through.md` names each one).

**Rehearsal:** the same, on `$FT`. **Observed in the rehearsal:** rehearsed; matched. `git fetch origin` exited 0, `origin/main` was `c42ed1d8a`, and the diff printed nothing (`$R/step1-drift.txt`, 0 bytes).

## Step 2: agentic-mbse pin check

sysml-codegen's `install-commands` uses agentic-mbse's installer through the API marked `installer/v1`, which fusion-tea's agentic-mbse pin `adbef75` predates. The agentic-mbse version stays 0.1.3; only the SHA moves (design DD5, Appendix B).

```bash
uv run --no-sync python -c "from agentic_mbse.cli.installation import INSTALLER_API_VERSION as v; print(v)"
```

**Expected:** `installer/v1`. If it raises or prints anything else, move fusion-tea's agentic-mbse pin to `M_AMBSE` first, as Item 2's runbook moved it (`[tool.uv.sources]` `rev`, the hand-edited `uv.lock`, `uv sync --frozen --extra e2e`, restore removed packages, `uv lock --check`) and set `A_FINAL` in `tests/test_dependency_provenance.py`. If Item 2's pin move has not run yet, pin straight to `M_AMBSE`.

**Rehearsal:** after `uv pip install --python $FTC/.venv/bin/python --no-deps $AMBSE_WHEEL $CODEGEN_WHEEL`, wheels built from the two branch heads; this is run B's state. Run B does not keep it: the original seam's gate 2 runs `uv run sysml-codegen generate` without `--no-sync` (`scripts/integrate.py:1006`, B3), which re-syncs `.venv` to the old lock, so the rehearsal re-runs this install before step 5. In the real adoption, step 4 moves the lock first, so a re-sync installs `M_CODEGEN` and this does not arise. **Observed in the rehearsal:** rehearsed; matched, with one deviation. After the wheel install it printed `installer/v1` (`$R/step2.txt`). Before the install, at fusion-tea's current pin `ac5fb1a` (Item 2 moved it from `adbef75`), the same command raised `ImportError: cannot import name 'INSTALLER_API_VERSION'` (`$R/step2-before-extra.txt`), so the real switch does need the pin move to `M_AMBSE`. Deviation: the wheel install did not survive run B. The original seam's gate 2 runs `uv run sysml-codegen generate` without `--no-sync` (O4's `scripts/integrate.py:1006`, closed-list item B3). The first suite test to reach gate 2 therefore re-synced `.venv` to `uv.lock` at 13:48:18, putting back sysml-codegen `8a758e9` and agentic-mbse `ac5fb1a`. Step 5's first check then failed, and the step 2 install command was re-run unchanged before step 5's checks (`$R/step2-reinstall.txt`). In the real switch, step 4 moves the lock, so a re-sync installs `M_CODEGEN`; only the rehearsal's stand-in breaks.

## Step 3: no-loss check

Before anything local is removed, every ledger destination must be in fusion-tea's tree. Each `moved` row of `$EV/read-through.md` names its home and a fixed-string anchor; the shared ledger's Item 3 rows (`$EV/ledger-rows.md`, appended by O4) group them.

```bash
python3 $EV/fusion-tea/text/check_anchors.py $EV/read-through.md .
```

The script greps all 75 anchors in their homes in the working tree and exits non-zero naming any it cannot find. By hand, one row: `git grep -nF 'Two routes, and no third.' -- modeling_project/STUDY_POLICY.md`.

**Expected:** `75 anchors found, 0 missing`, exit 0, at O4's tip `aab9b9ba3` or later: 74 from O4's text commit `699b0a74d`, plus IG-43, which `aab9b9ba3` adds from `fusion-tea/text/audit-f8-supplement.patch`. If one is missing, the script names it: stop, because the branch's text is incomplete.

**Rehearsal:** on `$FTC` with O4's text commits applied. **Observed in the rehearsal:** rehearsed; did not match. It printed `74 anchors found, 1 missing` and exited 1, naming `IG-43: "step numbers of fusion-tea's integration-seam requirements" is not in docs/integration_seam_operator_guide.md` (`$R/step3.txt`). IG-43 and `audit-f8-supplement.patch` were added in sysml-codegen `7cf5a7c` during the rehearsal, after `$FTC` was made at `699b0a74d`. The patch passes `git apply --check` on `$FTC`, and with it applied to a copy of the guide the anchor greps once (`$R/step3-f8-probe/`). The O4 branch has since gained the line as `aab9b9ba3`, so the step should pass at that tip; this rehearsal did not re-run it there. Re-checked against `aab9b9ba3`'s policy and supplement as the anchor homes: `75 anchors found, 0 missing`, exit 0 (`$R/step3-aab9b9ba3/`).

## Step 4: move the sysml-codegen pin

This is the step that needs `M_CODEGEN`.

1. Save the package list: `uv pip list > /tmp/study-switch-pip-before.txt`.
2. In `pyproject.toml` (`[tool.uv.sources]`), set sysml-codegen's `rev` to `M_CODEGEN`. Do not change `sysml-codegen==0.1.1`: the version is unchanged.
3. In `uv.lock`, replace the old SHA `8a758e9240707b58fe32a509c3b509941ca4fa01` with `M_CODEGEN` by hand. `grep -c` the old SHA before and after; after must be 0. Do not run `uv lock`.
4. `uv sync --frozen --extra e2e`, then `uv pip list > /tmp/study-switch-pip-after.txt` and diff the two lists. Restore every removed package except sysml-codegen's own change.
5. `uv lock --check` reports the lock fresh.
6. In `tests/test_dependency_provenance.py`, set `C_PROD` to `M_CODEGEN`. Then `uv run --no-sync pytest tests/test_dependency_provenance.py -q` passes with the environment of "Before you start".

**What this item changed in sysml-codegen's `pyproject.toml`, and the lock.** Re-check before the move with `git -C <sysml-codegen> diff aa35f06 M_CODEGEN -- pyproject.toml`. At the time of drafting:

- `jsonschema` joined the `dev` extra. fusion-tea does not request that extra, so its lock does not change.
- `[tool.mypy]` overrides and `[tool.ruff.lint.per-file-ignores]` entries for the study modules. Tool tables do not enter dependency metadata.
- No runtime dependency was added, the agentic-mbse bound stays `>=0.1.3,<0.2`, no console script was added, and the skill files, policy template and schemas are package data inside `sysml_codegen`.

So the hand-edited lock holds. If the re-check shows a new runtime dependency or a changed agentic-mbse bound, it does not: stop and re-plan the pin move.

**Rehearsal:** not rehearsable — it needs `M_CODEGEN`. **Observed in the rehearsal:** not run.

## Step 5: switch

1. **Wrappers.** Copy each module alias over its namesake: `cp $EV/fusion-tea/wrappers/scripts/study/*.py scripts/study/` (the seven `common`, `manifest`, `identity`, `indicators`, `preflight`, `verify` and `read_coverage`) and `cp $EV/fusion-tea/wrappers/scripts/integrate.py scripts/integrate.py`. Each pins fusion-tea's root in-process from its own location, never touches `os.environ`, runs `main()` when executed, and otherwise replaces itself in `sys.modules` (design DD14).
2. **Route modules.** Rewrite the import in the nine live `study_route.py` files that import `scripts.study` (`CONSUMER_SURFACE.md:43,50,57,62,67,72,89,97,106`). They then import `sysml_codegen.study`, which keeps read coverage inside its permitted sources (B8). Name the nine files; never use a pathspec glob. git's pathspec `*` crosses `/`, so in a git command a pattern such as `exploration/*/studies/study_route.py` also matches the route copies inside committed records (`<record>/results/sources/`, `<record>/preparation/`), which must never change.

   ```bash
   ROUTES=(
     exploration/aries_integrated/studies/study_route.py
     exploration/component_alternatives/studies/study_route.py
     exploration/costed_loop_brayton/studies/study_route.py
     exploration/exchanger_architecture/thermal_requirements/studies/study_route.py
     exploration/ife_e2e/studies/study_route.py
     exploration/magnet_materials/studies/study_route.py
     exploration/stellarator_e2e/studies/study_route.py
     exploration/stellarator_materials/studies/study_route.py
     exploration/whole_plant_conversion/studies/study_route.py
   )
   sed -i -f $EV/fusion-tea/routes.sed "${ROUTES[@]}"
   ```

3. **Schemas.** `git rm -r scripts/study/schemas`. They ship in `sysml_codegen/study/schemas/`, byte-identical.
4. **Tests.** Apply `patch -p1 < $EV/fusion-tea/step5-tests.patch` (17 files). It applies with no reject, fuzz or offset to `b06585709`, and so to O4's tip, where its 17 files are unchanged. It carries design Appendix H3's edits: schema home, tool paths, `TEAX_SIMKIT_PATH`, `REQUIRED_ENV` plus the declared environment, and `tests/models/test_model_family_spines.py` importing `by_entry_type` from `sysml_codegen.study.census`, so gates 4 and 5 share one implementation. It also gives `test_integrate_restore.py`'s backup test a request carrying `package`, as argparse's `--package` does, and an `assert_environment` fake with the installed signature. Do not apply `step5-guide-contract.patch`: its reduction of `tests/study/test_integrate_guide_contract.py` to the supplement's own facts (the sealed-wheel home, `WHEEL_HASHES` and ADR-0009) is already in O4's commit `699b0a74d`, and applying it again rejects both hunks.

**Expected:**

```bash
uv run --no-sync python -c "import scripts.study.manifest as m, sysml_codegen.study.manifest as n; print(m is n)"   # True
git grep -n 'from scripts.study' -- "${ROUTES[@]}"            # nothing: no live route imports scripts.study
git grep -c 'from sysml_codegen.study' -- "${ROUTES[@]}"      # each of the nine files listed
git status --porcelain --untracked-files=all -- exploration/ | cut -c4- | grep -vxF -f <(printf '%s\n' "${ROUTES[@]}")   # nothing: no other file under exploration/ changed, record copies included
```

**Rehearsal:** applied on `$FTC`; `$EV/fusion-tea/SMOKE.md` records the drafts' smoke test in the parity layout. **Observed in the rehearsal:** rehearsed; two deviations. (1) `step5-tests.patch` applied to all 17 files with no reject, but `step5-guide-contract.patch` did not apply: patch reported "Reversed (or previously applied) patch detected", skipped both hunks, wrote `tests/study/test_integrate_guide_contract.py.rej` and exited 1 (`$R/step5.txt`). O4's commit `699b0a74d` already holds that change; its file is byte-identical to `b06585709`'s plus the patch, so the file ended in the intended state. (2) The first `m is n` check failed with `ModuleNotFoundError: No module named 'sysml_codegen.study'` (from the wrapper `scripts/study/manifest.py:13`), because the venv had been re-synced to the lock (step 2). After step 2's install was re-run, every check matched: `True`; no `from scripts.study` in the nine routes; one `from sysml_codegen.study` in each of the nine; nothing else changed under `exploration/` (`$R/step5-checks.txt`, `$R/step5-checks-after-reinstall.txt`). Re-rehearsed after the kit fixes: the fixed `step5-tests.patch` applies to `b06585709` with no reject, fuzz or offset, and its delta applied on `$FTC` left all 17 files equal to that result (`$R/step5-delta.patch`, `$R/step5-delta2.patch`); the restore test then passes on its own (`$R/restore-test-alone.txt`).

## Step 6: declare

1. Append `$EV/fusion-tea/declaration.toml` to `pyproject.toml`. It is design Appendix D's fusion-tea table: both repo-scope gates with today's `checked` texts, the five `STOP_PARSER_*` variables, `record-distributions = { costingfe = "1costingfe" }` and the backup prefix `fusion-tea-integration-backup-`. With it, fusion-tea's returns keep rows 1a and 5, the environment sweep, the toolchain block and the prefix byte for byte (B4–B6, B10, B12; SC12).
2. Add `TEAX_SIMKIT_PATH=$STOP_PARSER_TEAX_ROOT/packages/teax-simkit` to `.venv/integration.env`, written with the expanded path. Gate 1b reads the teax revision there, and without it gate 1b blocks (B7, DD10).

**Expected:** `uv lock --check` still reports the lock fresh: a `[tool]` table does not enter it.

**Rehearsal:** applied on `$FTC`. **Observed in the rehearsal:** rehearsed; matched. The declaration was appended, `.venv/integration.env` was created holding the one `TEAX_SIMKIT_PATH` line, and `uv lock --check` printed `Resolved 179 packages` and exited 0 (`$R/step6.txt`).

## Step 7: re-install

1. `git rm -r -q .claude/skills/run-study .agents/skills/run-study`
2. In `.gitignore`, delete the whitelist line `!.claude/skills/run-study/`. Find it by text; the other lines stay.
3. `uv run --no-sync sysml-codegen install-commands . < /dev/null`

Both assistants are the default. With no terminal, the installer keeps a differing file it does not manage instead of prompting. fusion-tea's ratified `modeling_project/STUDY_POLICY.md` is a project document, so it is kept.

**Expected:**

- five files under `.agents/skills/run-study/`: `SKILL.md`, `runbook.md`, `record-template.md`, `annex-template.md`, `integration-guide.md`;
- `.claude/skills/run-study` is a link into `.agents/skills/run-study`;
- the output says "Preserved modeling_project/STUDY_POLICY.md";
- `.sysml-codegen/install.json` exists and lists the installed files; `.agentic-mbse/install.json` names none of them.
- If fusion-tea's `.claude/commands/teax-completion.md` differs from the shipped file, the output says "Preserved .claude/commands/teax-completion.md: …" and the file stays. That is the installer's first-run rule (DD6), not a failure. A copy the old installer left differs, because the shipped file has since lost a machine path. Do not re-run with `--force` to replace it: `--force` also replaces fusion-tea's ratified `modeling_project/STUDY_POLICY.md`. To take the shipped command, delete the file and re-run, or re-run at a terminal and answer `o` for that file alone.

fusion-tea's own tests that read the skill text keep passing on the installed copy, as Phase 5 checked against the shipped files: `tests/study/test_annex.py` (the runbook cites only the four annex sections), `tests/study/test_record_template.py` (two full `source_digest` blocks) and `tests/study/test_policy_path.py` (the skill and runbook name `modeling_project/STUDY_POLICY.md`).

**Rehearsal:** the same, on `$FTC`. **Observed in the rehearsal:** rehearsed; matched. `install-commands` exited 0 and printed "Preserved modeling_project/STUDY_POLICY.md: it is this project's document; --force replaces it". The five files are under `.agents/skills/run-study/`, `.claude/skills/run-study` reads `../../.agents/skills/run-study`, `.sysml-codegen/install.json` lists the five files, the link and `.claude/commands/teax-completion.md`, and `.agentic-mbse/install.json` names none of them (`$R/install.txt`, `$R/step7-checks.txt`). `teax-completion.md` was Created, not Preserved, because a fresh worktree has no untracked copy, so the first-run rule was not exercised.

## Step 8: verify

### 8a. The study suite (cut 1)

```bash
uv run --no-sync pytest tests/study tests/models/test_model_family_spines.py -q -rs --continue-on-collection-errors --junitxml=<run>/junit.xml
```

fusion-tea's suite has one collection error that is not this item's, hence `--continue-on-collection-errors`: `tests/study/test_stellarator_materials_policy.py` imports `exploration/stellarator_materials/oracle_glue.py`, whose `PIN_INPUTS_PATH` (line 85) names `work/active/WI-098_whole-plant-conversion-comparison/…`, and fusion-tea `421966070` archived that item to `work/completed/20261006_WI-098_…`. Without the flag, pytest stops there and runs no test.

**Pass rule:** compare run C (after step 7) with run B (dependencies moved, nothing switched) using `$EV/rehearsal/junit-diff.py`. B to C differs only in gate-2 refusals that the generator move causes, and in nothing else. In the rehearsal those are exactly these 21 integrate tests. Each fails in C at gate 2 (`regeneration`, `package-not-integrated`), because the moved generator rewrites 3 files of the stellarator package: `generated/contracts/package_contract.json`, `generated/modules/mfe_fuel_cycle/fuel_inventory.py` and `generated/schemas/fuel_inventory_output.py`.

- Passed in B, fail in C: `test_integrate_internal_error.py` `test_a_seam_internal_error_exits_two_and_names_where_it_died`, `test_the_gates_that_passed_before_the_crash_survive_in_the_return` and `test_the_traceback_is_deposited_and_cited_by_path`; `test_integrate_refusals.py` `test_absent_census_file_could_not_run_rather_than_pass`, `test_doctored_census_refuses_gate_4`, `test_doctored_pin_refuses_gate_6` and `test_two_snapshots_beside_the_models_root_are_input_invalid`.
- Fail in both, now at gate 2: `test_integrate_lineage.py` `test_absent_expected_fingerprints_could_not_run_rather_than_pass` and `test_wrong_expected_fingerprint_refuses_at_gate_9`; `test_integrate_refusals.py` `test_drifted_recorded_provenance_refuses_gate_7`; `test_integrate_rerun.py` `test_the_second_run_is_a_candidate_not_a_refusal` and `test_two_runs_return_the_same_identity`; `test_integrate_stock_route.py` `test_the_return_rebuilds_the_stock_commands`; and all eight tests of `test_integrate_success.py`, whose fixture refuses.

In the rehearsal, B's integrate tests ran the old generator (step 2) and got past gate 2. In the real adoption, step 4 puts the moved generator under B as well, so these refusals should appear in B and drop out of B to C. That was not rehearsed.

**Stop rule for the real adoption** (re-audit R1): step 4 puts the moved generator under both B and C, so in the real run B to C should show no change at all. Any test whose outcome differs between B and C is a stop: diagnose it before step 8b. Do not wave it through as one of the 21 above, whose refusals belong to B as well in the real run. B against A (as-is) is recorded and classified for step 9; it is not a gate on the move.

**Rehearsal:** runs A, B and C on `$FTC`, one shell, `env.sh` sourced, each run's `env.txt` written by `record_env <run>` (`python -V`, `uv pip list`, teax HEAD, the licence by presence, and `env | grep -E '^(STOP_PARSER_[A-Z_]*|TEAX_SIMKIT_PATH|SYSML_CODEGEN_PROJECT_ROOT|PYTHONPATH)='`). Design Appendix H3's pattern `'^(STOP_PARSER_|…)='` needs `=` straight after the prefix, so it matches no `STOP_PARSER_` name; `STOP_PARSER_[A-Z_]*` is the corrected form. Compare with `python3 $EV/rehearsal/junit-diff.py <B>/junit.xml <C>/junit.xml` and check that every line it reports is on the list above. It masks pytest's per-run temporary directory in both its absolute and its relative form. **Observed in the rehearsal:** rehearsed; after the kit fixes, matches the pass rule. As first written, the suite ran no test in A, B or C: pytest stopped at the collection error above and exited 2. With `--continue-on-collection-errors`, A had 1844 passed, 6 failed, 9 errors and 2 skipped (1 skip, 1 xfail), and B the same (`$R/A-cce/`, `$R/B-cce/`). A and B share a gate 7 refusal in the integrate tests (`undeclared dependency read: /dev/urandom`), which comes from the rehearsal venv's interpreter (see "Before you start"). The first `junit-diff.py` called A to B BROKEN on 11 messages that differ only in pytest's relative temp path; with that path masked, A to B holds (`$R/A-to-B-cce-fixed.txt`). The first run C (1836 passed, 14 failed) also failed `test_integrate_restore.py::test_run_retains_external_backup_and_recovery_pointer`, on two fakes the patch had not updated. Re-run after the patch fix: C had 1837 passed, 13 failed, 9 errors and 2 skipped (`$R/C2/`), and B to C reports exactly the 21 listed tests and nothing else (`$R/B-to-C2.txt`, checked against `$R/expected-21.txt`).

### 8b. Re-verify one existing record

Use the newest record whose sealed identity recomputes. At O4's tip that is `exploration/magnet_materials/studies/20260929-magnet-material-comparison`, the only one of the 40 records with a results identity that does. The earlier choice, `exploration/stellarator_e2e/studies/20260916-primary-loop-sizing`, does not: its package, `exploration/stellarator_e2e/generated`, has had 10 commits since the record sealed it (`69653c9dd`), so it recomputes to `83ea3b6c…`, not the declared `f52729e6…`.

1. Before and after step 5, run `identity.assert_matches` over the record's identity document and its package. The digest is the same both times: no sealed identity changes, because every route calls `build_sealed`, whose digest is the package's sealed fingerprint (DD14).
2. Run the installed `verify` with the arguments of the record's own `command` in `results/verification_summary.json` (its package, manifest, identity, stores, and seed and sample size where given), and a new `--out`: `PYTHONPATH=$FT:$TEAX_SIMKIT_PATH uv run --no-sync sysml-codegen study verify --package … --manifest … --identity … --store … --out /tmp/reverify.json`. `verify` imports teax's simkit, which fusion-tea's venv does not install, and the record's oracle module, which imports `exploration.…` from the repository root; a console script does not put the working directory on `sys.path`, hence both entries.
3. Compare `/tmp/reverify.json` with the record's `results/verification_summary.json`. The sampled cases, the re-derived verdicts and the worst deviation agree. Only `tool.path`, `tool.source_digest` and `command[0]` differ, from `scripts/study/verify.py` to `sysml_codegen/study/verify.py` (B2): that is expected, not a failure.
4. `git status --short -- <record directory>` prints nothing: the record's committed files are untouched.
5. List every committed `package_identity.json` of kind `effective` whose adapter sources name a rewritten route file. None is expected.

**Rehearsal:** on `$FTC`. Items 2 and 3 are not rehearsable there: no record that recomputes has a committed store. **Observed in the rehearsal:** partly rehearsed. The named record `20260916-primary-loop-sizing` does not recompute: `assert_matches` raises `IdentityError` (declares `f52729e6…`, recomputes `83ea3b6c…`), the same over `pkg/stellarator_tea` and over the record's own package `exploration/stellarator_e2e/generated`, before and after step 5 (`$R/8b-before-primary-loop*`, `$R/8b-after-primary-loop.txt`). Of the 40 records with a results identity, scanned newest first, only `exploration/magnet_materials/studies/20260929-magnet-material-comparison` recomputes (`$R/8b-candidate-scan-full.txt`). Identity half, on that record and its package `exploration/magnet_materials/magnet_materials_tea`: `7075e929…` before and after step 5, `cmp` equal, as expected (`$R/8b-before.txt`, `$R/8b-after.txt`). Verify half: not rehearsable. That record's two stores (`results/native/20260929-magnet-material-comparison.db`, `results/_work/magnet-materials-baseline-point-v1.db`) are not committed, and no record whose store is present recomputes. A diagnostic verify on the primary-loop record showed two more facts (`$R/8b-verify.txt`, `$R/8b-verify-diag.txt`). As written, `sysml-codegen study verify` exits 1 with `No module named 'simkit'`, because the 8b command does not put `$TEAX_SIMKIT_PATH` on `PYTHONPATH` as 8c's driver does. With it set inline, verify refuses on the identity mismatch (exit 1). `git status --short` on both record directories printed nothing. No committed identity of kind `effective` exists, so the last command printed nothing, as expected (`$R/8b-effective.txt`). The verify command needs the repository root on `PYTHONPATH` as well as simkit. With `PYTHONPATH=$TEAX_SIMKIT_PATH` alone, verify on the magnet record stops at `No module named 'exploration'`, raised importing the record's oracle module. With both entries, it reaches the absent store and fails there with an uncaught `sqlite3.OperationalError` (`$R/8b-verify-cmdtest*.txt`).

### 8c. `integrate` on a real package (needs teax and the licence)

In run B (local tools) and run C (installed), run `integrate` with the supplement's full stellarator request (`docs/integration_seam_operator_guide.md` § The full invocation in fusion-tea). In C, also run the gate-7 driver directly:

```bash
mkdir -p /tmp/rc/read-coverage-tmp
TMPDIR=/tmp/rc/read-coverage-tmp PYTHONPATH=$FTC:$TEAX_SIMKIT_PATH SYSML_CODEGEN_PROJECT_ROOT=$FTC uv run --no-sync python -c 'import sys; from sysml_codegen.study.read_coverage import run_route; run_route(*sys.argv[1:])' exploration/stellarator_e2e/studies study_route execute_baseline /tmp/rc exploration/stellarator_e2e/pkg/stellarator_tea exploration/stellarator_e2e/studies/manifest.json rehearsal
```

`TMPDIR` points inside the out directory, as both seams arrange: the route's first `tempfile.mkdtemp` makes tempfile probe its directory with a new file, and that probe has to land in the out directory, where the observer admits it as new output; in `/tmp` it is refused as an undeclared read. `SYSML_CODEGEN_PROJECT_ROOT` is set to match what the seam hands its producers; the driver does not need it. The package is in `$FTC`'s git work tree, and since sysml-codegen `2e21955` the driver resolves the root from the package before it observes the route. Only a package in no work tree needs the variable, and the driver then refuses with a message naming it.

**Expected:** B and C stop at the same gate with the same class and condition, or both return `CANDIDATE`. Their returns differ only in closed-list fields under SC12's comparator (`$EV/parity/`). The C driver writes `read_coverage.json` with `outcome: pass` and `violations: []`.

**Rehearsal:** the orchestrator runs it on `$FTC`. **Observed in the rehearsal:** `integrate` rehearsed and matched; the driver did not match. Both runs used the supplement's full stellarator request with `--groups exploration/stellarator_e2e/studies/axes.supplied_design.json` (`$R/integrate-args.txt`). B and C both returned `BLOCKER` at gate 1b `teax-revision`, mode `refused`, condition `toolchain-drift`, exit 1 (`$R/8c-classes.txt`). The request's `--expected-teax-revision 744745f8…` is a historical value, and teax HEAD is `8d877460…`. Gate 1a passed in both; B ran with the venv re-synced to the lock (step 2), C with the wheels. The returns differ only in closed-list fields: tool path, `command[0]`, source digests and producers (B2), gate 4's census producer (B11), and gate 1b's detail naming the simkit root (B7). The `--out-dir` path and its junit evidence path differ by construction (`$R/8c-return-diff.txt`). Gate 1b stops both runs, so gates 2–9 were not compared. The gate-7 driver first failed without `TMPDIR`: `outcome: fail`, `undeclared dependency read: /tmp/frcvddch`, exit 1 (`$R/rc/`). The read is tempfile's first-use probe (`tempfile._get_default_tempdir`, from `mkdtemp` at `study_route.py:241`), which lands in `/tmp` when `TMPDIR` is unset. Both seams set `TMPDIR` inside the out directory, and the original observer fails and passes the same way once the venv's interpreter effects are removed (`$R/diag/`). Re-run with `TMPDIR`, from the `4d6c2ab` wheel: `pass []`, exit 0, with the probe admitted as new output (`$R/rc2/`).

## Step 9: consequence note

Moving the sysml-codegen pin also moves the code generator fusion-tea's packages are built with, from `8a758e9` to the merge commit `M_CODEGEN` (count `git rev-list --count 8a758e9..M_CODEGEN`). 142 of those commits take it to sysml-codegen `main` as this branch found it (`aa35f06`); the branch adds its own (214 at `310dfc6`). `integrate`'s regeneration gate requires regeneration to move no byte, so gate 2 may refuse fusion-tea packages, and gate 4's snapshots may drift, until each package is regenerated in its own modeling item. That is the pin move's consequence, not this switch's. Record what B against A (8a) and 8c showed, so the owner decides the pin move with it in view. In the rehearsal, B falls back to the old generator (step 2), so 8a's B to C list shows it instead.

**Observed in the rehearsal:** the generator moved 214 commits from `8a758e9` to the wheel's `310dfc6` (225 to sysml-codegen HEAD `4a9628c`), not about 142. A to B (8a) showed nothing, because gate 2's re-sync put the old generator back in B (step 2); no test passed in A and failed in B. Run C, on the new generator, shows the consequence. Gate 2 refuses the stellarator package with `package-not-integrated`, because regeneration rewrites 3 files: `generated/contracts/package_contract.json`, `generated/modules/mfe_fuel_cycle/fuel_inventory.py` and `generated/schemas/fuel_inventory_output.py` (`$R/C-cce/gate2-moved_files.txt`). That refusal accounts for 21 failing or changed integrate tests in C. Gate 4 snapshot drift was not observable, because gate 2 stops first. The model-family spine suite passed 15 of 15 on the new generator. 8c's B run stopped at gate 1b, so it adds nothing here.

**After regeneration** (re-audit R2): the rehearsal exercised `integrate` on a real fusion-tea package only up to gate 2 (8a) or gate 1b (8c, a historical teax revision in the request). Gates 3–9 on a real package were covered only by parity on the neutral station. Once fusion-tea's packages are regenerated under the new generator, re-run 8a's 21 integrate tests and 8c with the current teax revision, and treat any refusal past gate 2 as a finding.

**Record identities** (re-audit R3): at O4's tip only 1 of fusion-tea's 40 study records still recomputes its sealed identity (`exploration/magnet_materials/studies/20260929-magnet-material-comparison`); the rest stopped recomputing before this item, as packages were regenerated. The move does not change that, and it is why 8b names that one record.

## Commit

Stage the paths from `git status --short` by name, never with `git add -A`: the step 2 and step 4 files if those steps ran, `pyproject.toml`, `uv.lock`, `tests/test_dependency_provenance.py`, the eight wrappers, the nine route modules (`"${ROUTES[@]}"`), the removed `scripts/study/schemas/`, the step-5 test files, `.gitignore`, the removed `.claude/skills/run-study` and `.agents/skills/run-study`, the installed `.agents/skills/run-study/`, and `.sysml-codegen/install.json`. The `.claude/skills/run-study` link and `.claude/commands/teax-completion.md` stay untracked: fusion-tea's `.gitignore` ignores `.claude/skills/*` and `.claude/commands/*`, and a link is not matched by a directory whitelist, so this is how Item 2 left `run-goal`'s link. `install-commands` makes them in each checkout. `.venv/integration.env` is gitignored and stays out. A subject that fits: "Use the study layer installed from sysml-codegen at M_CODEGEN". Do not push; the owner pushes and merges the branch.

# Spec: L6 integration and execution-target settings

**Status:** Implementation complete, plan Phases 1–11 (2026-10-19); awaiting `/_my_audit`
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Complexity:** HIGH. The parts: a settings reader shared with research, a byte-preserving `pyproject.toml` writer and `init` prompt, evaluator wiring and presentation for 5 verdicts × 3 targets, two small additive library pieces, an audit of 17 L6 issue codes plus manifest and setup failures, per-site work on 28 exception sites (26 broad, 2 `AttributeError`) and the runner, a structured report, docs, and four evidence files. Expect several implementation sessions. The plan must be persistent (`plan.md`).
**Branch:** `l6-subset-profile` (off `main` at `ebb3d467`)

---

## Problem

`agentic-mbse validate` does not tell a modeler whether the code generator will accept their model. Item 1 shipped the contract that can say so (`src/agentic_mbse/sysml/subset_profile.py`, `subset-profile/v1`), but nothing calls it. A modeler finds generator refusals only by running the generator. dc3 found its blocker categories B1–B8 through five sequential generation runs (dc3 T-001). Item 1's evaluator now reports 236 refused findings on that same baseline in one pass. That figure is the evaluator's count, not a count of refusals the generator produced.

[AGENT] (ratified by owner, 2026-10-18; `briefs/align.md`) `validate` should report that contract up front. Projects that only run natively must not be buried in generator noise, so each project declares its execution target.

Today's L6 makes this harder in four ways. All were checked by reading code; nothing was run.

- **Hand-written generator checks overlap the contract and disagree with it.** L6 flags `attribute x : String = "abc"` as an error, but only under `designs/`. It never sees the `:>> x = "abc"` spelling, which SysIDE parses as a reference usage (`level6_architecture.py:476-575`, `:853`). On dc3 baseline that is 3 flagged against 32 String declarations (`completed/20261018_exec-subset-profile/evidence/acceptance.md:27`).
- **Failed inspections read as clean, or as model defects.** There are 26 broad `except Exception` sites in `level6_architecture.py` (17) and `adr002.py` (9), plus two `AttributeError` catches. Most turn a failure into "no issue" or a zero count. Others turn it into a false model-defect finding.
- **A crashed level counts as a pass.** When a level raises, `runner.py:128-137` prints the error but never records the level, so `overall_success` (`common.py:66`) stays true and the exit code is 0. With `--level=6` alone the run prints "Checks run: 0" and "All quality checks passed!". The comment at `runner.py:135` says "Treat exceptions as failures".
- **There is no setting,** and nothing writes `pyproject.toml`.

## Terms used below

- **Verdict:** the evaluator's one-word summary of a run: `clear`, `unconfirmed`, `refused`, `incomplete` or `refused_incomplete` (`subset_profile.py:160-172`).
- **Outcome:** what the evaluator says about one finding: `refused` (a retained generator probe saw this refusal), `admitted`, `excluded` (a non-numerical constraint), `omitted` (a String value the generator drops), `unconfirmed` (the rule matches but no probe covers this context).
- **Unverified check:** the evaluator could not decide a rule at a site (`UnverifiedCheck`, `subset_profile.py:678`). This is "could not decide", not a crash.
- **Unassessed constraints:** a count (`counts.unassessed_constraints`) of constraints the executable profile could not assess. They do not produce unverified checks and do not change the verdict (`subset_profile.py:1276-1282`, `:1360`).
- **Coverage limit:** the families of generator refusals the contract has no rule for, so a `clear` verdict cannot speak to them.
- **impl-F1 / impl-F2:** Item 1's product-lens findings. impl-F1: `clear` must carry its coverage limit. impl-F2: incompleteness must not hide refusals (`completed/20261018_exec-subset-profile/product-lens.md:80-81`).
- **dc3 categories:** B1 calc-owned assertions, B2 expression binding sources, B3 unresolved part multiplicity, B4 and B5 unsupported callables, B6 conditional expressions, B7 String omissions, B8 constraint predicates (unconfirmed). Item 1's table with rule, shape, context and count for each: `completed/20261018_exec-subset-profile/evidence/acceptance.md:21-31`.

## Success Criteria

"Test" means a pytest test under `tests/`. "Evidence" means a file under `.project/active/l6-subset-profile/evidence/`.

**Settings states** (CLI tests that run `validate --level=6` on a fixture project with one refused finding)

- [ ] `generated`: exit 1. The refusal is ERROR.
- [ ] `native`: exit 0. Generator-only findings appear as one INFO summary line. A test reads every one of them, with rule, reason and location, from the structured report (below).
- [ ] Unset (no `pyproject.toml`, no table, or no key): exit 0. The refusal is WARNING. The unset note, naming the setting and both ways to set it, is printed. A second fixture with no generator findings also prints the note.
- [ ] Malformed `pyproject.toml`: exit 1, with an error naming the file and the parse error, under every target and with an override. It does not fall back to unset.
- [ ] Unknown value (`"generate"`, `1`, `""`): exit 1, with an error naming the value and the two allowed values.
- [ ] Unknown key (`execution_target`, `executiontarget`, `[tool.agentic-mbse.reseach]`) or a `[tool.agentic_mbse]` table: exit 1, with an error naming the key and the allowed keys.
- [ ] `--execution-target=native` on a file that says `generated` runs as native, and the output says an override was used. The reverse also holds.

**One key set, two readers** (tests in the research and validation suites)

- [ ] One definition lists the keys allowed in `[tool.agentic-mbse]` (`execution-target`, `research`). A test fails if a reader accepts a key outside it.
- [ ] A project with both `execution-target = "generated"` and `[tool.agentic-mbse.research] holdout-guard = …` passes both readers.
- [ ] A bad `holdout-guard` value (a path that does not exist) does not fail `validate`.
- [ ] A bad `execution-target` value does not refuse research `register`.
- [ ] A misspelled key fails both readers.

**Where the setting is read from** (tests)

- [ ] The file read is `<project root>/pyproject.toml`, with the root from `find_project_root(start=<validated path>)` (`project_root.py:19`). A test validates a subdirectory and shows the root's file is used, and that a `pyproject.toml` below the root is ignored.
- [ ] With no project root above the validated path, L6 runs as unset. A metric says no root was found and names `--execution-target`.
- [ ] Every L6 run has a metric stating the target in effect and its source: file path, override, or unset with the path looked at.

**`init`** (tests)

- [ ] `init --execution-target=generated` (or `native`) writes the key under `[tool.agentic-mbse]`. With no `pyproject.toml`, it creates one holding only that table.
- [ ] Interactive `init` (stdin is a terminal, no option, no existing value) offers generated, native or leave unset, and writes the choice. "Leave unset" is the default.
- [ ] Noninteractive `init` with no option writes nothing. Its output says the target is unset and gives the TOML line and the `init --execution-target` form.
- [ ] An existing value, valid or not, is never changed: not by re-init, not under `--force`, not by a disagreeing option. A disagreement or an invalid existing value is reported with the allowed values.
- [ ] Golden-file test: every byte outside the added key, including comments, blank lines, key order and an existing `[tool.agentic-mbse.research]` table, is unchanged, with and without `--force`. The written file parses with `tomllib`.
- [ ] `init` refuses to write, never rewrites, and prints the line to add with the reason, in each of these cases: `pyproject.toml` is a symlink; it does not parse; `agentic-mbse` is an inline table; `agentic-mbse` is defined through dotted keys under `[tool]`; or any other layout where the key cannot be added as a plain line in an existing `[tool.agentic-mbse]` table or as a new table at the end. Each case has a test.
- [ ] `install-commands` leaves `pyproject.toml` untouched (test).

**Presentation** (tests on rendered stdout, one fixture per verdict, run under each target)

- [ ] **Banned wording.** A case-insensitive scan of the whole `validate` stdout finds none of: "generated-ready", "generation-ready", "ready to generate", "will generate", "generator accepts", "readiness". This covers L6's lines, the level title and the final line.
- [ ] **Verdict line.** L6 prints one verdict line. It contains the profile version (`subset-profile/v1`), the coverage-list version, the verdict word, the refused count, the unverified count, the unassessed-constraint count, and the words "not a generation check". It never contains "clean", "ready" or "passed".
- [ ] **`refused_incomplete`.** In the verdict line, the refused count comes before the word "incomplete".
- [ ] **`clear`.** The verdict line reads "no refusals found by the implemented rules". The next line names the coverage limit. Both lines are asserted.
- [ ] **`incomplete`** (no refusals, some unverified checks): the verdict line says "incomplete". Under `generated` the level fails. Under unset the unverified checks are WARNING and the unset note is printed.
- [ ] **`unconfirmed`.** Under `generated` and unset, an unconfirmed finding is WARNING, never ERROR. Its message says no generator probe has observed it. For the two contexts that are unconfirmed by design (`beyond_generator_roots`, `beneath_refused_multiplicity`), the message names the context.
- [ ] **Shadowed.** The dc3 B8 fixture shape (a constraint predicate owned by a calc usage that has a refused calc-owned-assertion finding) prints "shadowed by" and names the refused finding. Its outcome stays `unconfirmed`.
- [ ] **Unverified by target.** ERROR under `generated`. WARNING under unset. Under `native`, a separate WARNING line with its own count, outside the INFO summary.
- [ ] **Excluded.** Under `generated`, an excluded non-numerical predicate is WARNING with reason `constraint_predicate_non_numerical`.
- [ ] **Unassessed constraints.** A fixture with unassessed constraints and verdict `clear` shows the count in the verdict line. Under `generated` and unset it gets one WARNING naming the count. Under `native` it is part of the INFO summary.
- [ ] **Final line.** When the run passes and the target is unset, or the target is `generated` and the verdict is anything but `refused`, the final line includes "generated compatibility not established". Item 4's pinned-positional note is the precedent (`common.py:161-176`, `runner.py:156-157`).
- [ ] **Level title.** The level is titled "Level 6: Architecture & Generator Subset" in `runner.py:54`, `level6_architecture.py:3`, `:935` and its `level_name` uses, and the `sysml/types.py:82` comment.

**Structured report** (test and evidence)

- [ ] `validate` can write a JSON report holding every issue of every level that ran, with no truncation, plus L6's full profile result: verdict, scope, coverage version and list, every finding with rule, shape, context, outcome, reason, location, remedy and severity, every unverified check, and counts. A test checks that the dc3-sized fixture's report holds as many findings as the evaluator returned. The text output keeps its current truncation.

**Check failures fail under every target** (tests)

- [ ] Each site listed under "Check failures" has a test that forces its exception and asserts `L6_CHECK_ERROR` naming the check, under each of the three targets. Under `native`, none is counted in the INFO summary. A count the failure affected prints "not computed", not 0.
- [ ] For the five sites that over-report today (`level6_architecture.py:520`, `:723`; `adr002.py:277`, `:335`, `:423`), the test also asserts that no dependent model-defect finding is emitted. For example, a failure at `:723` produces no `L6_CALC_DEF_NO_INSTANTIATION`.
- [ ] A level that raises is recorded as failed. The run exits 1 and names the level. Tested for L6 and for one other level.
- [ ] An evaluator or fact-extraction crash gives `L6_CHECK_ERROR` and exit 1 under every target.
- [ ] Under `native`, a native-correctness error stays ERROR (test on one retained native-correctness code).

**Both String spellings** (test plus evidence)

- [ ] `attribute x : String = "abc"` and `:>> x = "abc"`, each inside and outside `designs/`, give the same outcome (`omitted`), the same reason (`string_value_not_generated`) and the same severity: WARNING under `generated` and unset, INFO summary under `native`. Neither raises `L6_DESIGN_ATTR_UNEXTRACTABLE`.

**Library additions** (tests)

- [ ] The coverage list has its own version string, printed in the verdict line. A test pins its content to that version. Another test checks the list against the no-rule rows of Item 1's matrix fixture under `tests/fixtures/subset_profile/`, the way `tests/test_subset_matrix.py` does.
- [ ] `SUBSET_PROFILE_VERSION` and its pinned digest are unchanged from `ebb3d467` (test).
- [ ] Each routed advisory (UNSUPPORTED-SHAPE-MESSAGE, WRAPPER-SHAPE) has a fixture where it fires and a nearby fixture where it does not. It is at most WARNING under any target, and INFO under `native`.
- [ ] UNSUPPORTED-RHS and MULTIPLICITY-SHAPE: a fixture shows L6 reporting the `invocation-callable` finding at an attribute value and the `part-multiplicity/unresolved_bound` finding. The MULTIPLICITY-SHAPE row is marked closed in the matrix, citing that test.

**Consumer evidence** (`git archive` copies, never the consumer checkouts; every run records the resolved project root and the `pyproject.toml` path read)

- [ ] `evidence/dc3-baseline-l6.md`: from the JSON report of one `validate --level=6 --execution-target=generated` run on dc3 `808464d`, every confirmed category appears with location, reason and remedy. B1–B6 are refused ERROR, B7 omitted WARNING, B8 unconfirmed WARNING and shadowed by B1. Counts match Item 1's record (`evidence/dc3-baseline.md`): 236 refused, 32 omitted, 6 unconfirmed, 50 unverified, verdict `refused_incomplete`. Any difference is explained. A second run with the target unset is recorded too.
- [ ] `evidence/dc3-repaired-l6.md`: dc3 `60b44d5` under `generated` gives verdict `clear` with 30 omitted-String warnings, and the `clear` wording and coverage limit asserted above.
- [ ] `evidence/before-after.md`: full `validate --complete` runs before and after this change, with the target unset, on dc3 `808464d`, dc3 `60b44d5` and fusion-tea `f96ad312`. It records per-level pass/fail and the exit code. **Stop-and-show:** if any run goes from pass to fail, implementation stops, and the orchestrator shows the owner before merge.

**Audit and docs**

- [ ] `evidence/legacy-l6-audit.md` has one row per L6 issue code (17), plus manifest failures and setup failures. Each row gives what the check does, today's severity, its category, its severity under each target, and the evidence for its category. A separate table lists every severity lowered under `native` (ERROR→INFO and WARNING→INFO).
- [ ] Every codegen citation in `level6_architecture.py` and `adr002.py` (`:847`, `adr002.py:478`, the "codegen's V8" reference near `level6_architecture.py:584`) is checked read-only at codegen `b5663c07` and corrected or removed. The dead citation at `common.py:82` is fixed.
- [ ] README, `skills/model-validation/SKILL.md` and the L6 output each state the profile version, what was assessed, that the assessment is incomplete relative to the generator, and that L6 is not `sysml-codegen check`. A shipped-text test checks each statement. `docs/research-seam.md:350` and `:414-415` describe the shared key set.
- [ ] `uv run pytest tests/`, `uv run mypy src/` and `uv run ruff check src/ tests/` pass. The evidence says which tests needed the SysIDE licence and which were skipped.

## Known Requirements

### Owner gate outcomes (`briefs/align.md` § Gate outcomes)

- **[INFERRED]** [AGENT] (delegated by owner, 2026-10-18) **String values (R3-1):** the legacy `L6_DESIGN_ATTR_UNEXTRACTABLE` error for String values (`attribute` form, `designs/` only) is replaced by the contract's `omitted` outcome. That outcome is a warning in both forms and in every folder.
- **[INFERRED]** [AGENT] (delegated by owner, 2026-10-18) **Malformed constraints (R3-1):** `L6_CONSTRAINT_MALFORMED_NUMERICAL` keeps its current error severity and scope under every target. The contract's constraint outcomes are reported alongside it, never instead of it, so no constraint error is relaxed.
- **[INFERRED]** [AGENT] (delegated by owner, 2026-10-18) **Check failures (R3-2):** a check that crashes or cannot inspect what it was asked to inspect fails the run under every target, including unset. A crashed level is recorded as failed. Safeguard: the before/after runs in Success Criteria, with stop-and-show on any pass→fail.
- **[INFERRED]** [AGENT] (delegated by owner, 2026-10-18) **Unverified contract checks under unset** are warnings: they are the contract's "could not decide", not a crash. Under `generated` they follow the contract's verdict presentation.

### The setting

- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") The setting is `[tool.agentic-mbse] execution-target = "generated" | "native"` in the target project's `pyproject.toml`. It is committed, so owner, teammates and CI get the same result. An environment variable is out because it differs per machine.
- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") A one-run override (`validate --execution-target=…`) takes precedence over the file.
- **[INHERITED]** (epic Item 3 scope 1) A malformed TOML file and an unknown value are errors, not unset.
- **[HARD]** `research/holdout.py:241-260` rejects every `[tool.agentic-mbse]` key except `research`, and rejects a `[tool.agentic_mbse]` table. The research seam documents this closed set as the defense against a misspelled key silently switching a check off (`docs/research-seam.md:350`).
- **[INFERRED]** One closed key set for `[tool.agentic-mbse]`, defined once and used by both readers. Each reader rejects keys outside the set, but checks the value of its own key only. *Reason:* the guard fails closed (`docs/research-seam.md:412-419`). If it validated the target, a target typo would refuse every research `register`. If L6 validated the guard path, a research fault would fail `validate`.
- **[INFERRED]** An unknown key, or the underscore table, is an L6 configuration error. *Reason:* otherwise `execution_target = "generated"` silently gives unset, the exact failure the closed set exists to stop. It fails projects that pass today, so it falls under the R3-2 check-failure outcome and its safeguard.
- **[INFERRED]** The file is read only at the project root, using `find_project_root` unchanged. *Reason:* the brief asks for Item 4's discovery, which reads only at the root (ADR 0002, D11). A tree under `$HOME` with no marker of its own resolves to `$HOME`, because `~/.claude/` counts as a marker (Item 4 audit finding 7). The metric shows the path read.
- **[INFERRED]** The override accepts only `generated` and `native`. A malformed file or bad key or value is still an error with an override. *Reason:* the override picks a target. It does not repair a file that the holdout guard and uv also read.
- **[INFERRED]** The setting is read only when L6 runs. `--execution-target` with `--level` 1–5 is accepted and has no effect.

### Severity by target

- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") Unset is the default. It shows generator findings as warnings, with a note naming the setting, and never labels a model generated-ready.
- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") `native` turns generator-only findings into an INFO summary. `generated` makes confirmed refusals errors.
- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") Under `generated`, exclusions and omissions are warnings, each with its own reason. String policy stays with Item 2.
- **[INHERITED]** (epic Item 3 scope 3) Check and configuration failures are errors for requested checks under every target. An inspection failure is never folded into a native summary. Native correctness errors stay errors.
- **[INHERITED]** (epic principle 1; Item 1 `design.md:70-74`, `:341`; ADR 0001 invariant 3) L6 owns severity and rendering. It does not re-derive a decision the contract holds. No agentic-mbse module imports sysml-codegen.
- **[INFERRED]** `unconfirmed` is WARNING under `generated` and unset, and INFO summary under `native`, never ERROR. *Reason:* P-0001 allows blocking only with a retained probe.
- **[INFERRED]** Unverified checks are ERROR under `generated`. *Reason:* the gate outcome says they follow the verdict presentation there. `incomplete` and `refused_incomplete` are never clean, and under `generated` the capability checks are the checks requested. Under `native` they get their own WARNING line, outside the INFO summary (epic scope 3).
- **[INFERRED]** Unassessed constraints are shown as a count in the verdict line, and as one WARNING under `generated` and unset when the count is above zero. Under `native` the count is part of the INFO summary. They are never turned into unverified checks or ERROR. *Reason:* the contract reports them as a count, outside the verdict. Making them a check failure would mean L6 re-deriving a decision. A warning keeps a `clear` with unassessed constraints from reading as complete. The legacy `L6_CONSTRAINT_MALFORMED_NUMERICAL` error is unaffected.
- **[INFERRED]** "Shadowed by": a finding is labelled shadowed when its subject's owner is the subject of a `refused` finding from another rule. dc3 B8 is the known case. The label is presentation only and the outcome does not change. L6 computes it from the findings' subjects. If that needs owner facts the result lacks, design adds them in the additive way (below) or drops the label and records why.

### How results are presented

- **[INHERITED]** (ADR 0001 invariant 2; r3-proposal §2, owner-ratified) `clear` means no refusals over the implemented rules, not "will generate". No line is worded as generated-ready. Only the future `sysml-codegen check` (Item 2) could support that claim.
- **[INHERITED]** (impl-F2; Item 1 audit S3) Worst outcome and completeness are shown as two facts. Refusals lead.
- **[INHERITED]** (impl-F1; Item 1 audit S2) The coverage limit is shown with the verdict. Known no-rule families: DEEP-QUALIFIED-WIRING, ES-002, ES-008, ES-009, the ES-010 refusal side, CALC-DEF-BARE-RESULT, plus the explicit follow-up sites. `SubsetProfileResult` does not carry this today (`ScopeReport`, `subset_profile.py:716`).
- **[INFERRED]** The coverage list lives in agentic-mbse's `sysml/` layer as a packaged list with its own version string, separate from `subset_profile_rules.toml`. L6 does not keep its own copy. *Reason:* putting it in the rule records changes the digest and so `SUBSET_PROFILE_VERSION`, which Item 2 pins. A separate version means "same profile version" is never read as "same coverage".
- **[INFERRED]** Library additions only add. `SUBSET_PROFILE_VERSION`, its digest, existing result fields and every decision stay unchanged. If a need cannot be met that way, design stops and asks the owner. *Reason:* the Item 2 agent consumes this surface.
- **[INFERRED]** The L6 level is renamed "Architecture & Generator Subset". *Reason:* "Pipeline Readiness" claims readiness that L6 cannot establish. The new name says what it checks without a readiness claim. The `skills/model-validation/SKILL.md` table row and the descriptive L6 line in CLAUDE.md § Architecture change to match. That CLAUDE.md edit is a one-line description fix, not the Change Coordination proposal Item 6 reserves.
- **[INFERRED]** Every profile run prints the profile and executable-profile versions, the roots used, whether the selection was narrowed, and the fact kinds not enumerated. Each finding prints rule, reason, location, and the record's `remedy` and `semantic_limits`. No link to `docs/patterns/generator-subset.md` is printed until Item 5 creates it.
- **[INFERRED]** The full set of findings is available as a JSON report written on request. The text output keeps its truncation (`common.py:141-156`). *Reason:* 236+ findings cannot be shown in a terminal. Changing truncation for every level is not this item's job, while a report gives evidence and native users one complete source.

### Legacy L6 checks

- **[INHERITED]** (epic Item 3 scope 4) Every existing L6 check is audited. Duplicates are replaced by the contract's findings. Retained generator-specific checks go through target policy. ADR-002 placement and manifests keep their own applicability. `native` must not leave contradictory generator-only errors.
- **[INFERRED]** R3-1 covers unset and `generated` only, so lowering a generator-only check under `native` is not an R3-1 case. Instead, each row's category needs evidence: what the native route does with the construct (a SysIDE evaluation or fixture result), or a cause that exists only in the generator (codegen naming, extraction or emission). A row without that evidence keeps today's severity under `native`. *Reason:* without this, a wrong classification relaxes a native project's errors with no check.
- **[INFERRED]** Where a legacy check and a contract rule cover the same site, the combined severity under unset and `generated` is not lower than today's, except for the String case the gate decided.

Provisional dispositions. The audit evidence confirms or corrects each one.

| Legacy code (today) | Disposition | unset | generated | native |
|---|---|---|---|---|
| `V1_CALC_DEF_LOCATION`, `V2_DYNAMIC_EXPRESSION`, `V4_UNSUPPORTED_OPERATOR` (ERROR) | ADR-002, own applicability | ERROR | ERROR | ERROR |
| `V4_STATIC_FUNCTION_INVOCATION` (WARNING) | Kept. It is a duplicate of `invocation-callable` only if a boundary fixture (an allowlisted call in a design attribute) shows the same result. V4 fires on any call; the contract fires only off the allowlist (`subset_profile.py:921-934`) | WARNING | WARNING | INFO |
| `L6_CONSTRAINT_MALFORMED_NUMERICAL` (ERROR) | Kept unchanged by the gate outcome; contract outcomes alongside | ERROR | ERROR | ERROR |
| `L6_CONSTRAINT_NON_NUMERICAL` (WARNING) | Kept, contract `excluded` alongside, the same treatment as its sibling | WARNING | WARNING | INFO |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` on String values (ERROR, `attribute` form, `designs/`) | Replaced by contract `omitted` (gate outcome) | WARNING | WARNING | INFO |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` other values, `L6_DESIGN_ATTR_INCOMPLETE` (ERROR) | Generator-specific if evidence shows it | ERROR | ERROR | INFO |
| `L6_MISSING_QUALIFIED_NAME`, `L6_INVALID_QUALIFIED_NAME`, `L6_ANONYMOUS_RETURN`, `L6_CALC_DEF_NO_INSTANTIATION`, `L6_INVALID_BINDING_FORMAT` (ERROR) | Generator-specific if evidence shows it | ERROR | ERROR | INFO |
| `L6_BODY_ASSIGNMENT_IMPL_LOSS`, `L6_ATTR_REDEF_EXPR_DROPPED` (WARNING) | Generator-specific if evidence shows it | WARNING | WARNING | INFO |
| `L6_CALC_DEF_NO_OUTPUT` (ERROR), `L6_CALC_DEF_NO_DIRECTION` (WARNING) | Native correctness unless evidence shows otherwise | unchanged | unchanged | unchanged |
| Manifest failures; model-load and missing-path failures | Own applicability | fail | fail | fail |
| New: `calc-owned-assertion`, `part-multiplicity`, `binding-source`, `indexed-reference`, `conditional-expression` | Contract findings | WARNING | by outcome | INFO |

The `native` lowerings this proposes: 7 ERROR→INFO (`L6_DESIGN_ATTR_UNEXTRACTABLE` for non-String values, `L6_DESIGN_ATTR_INCOMPLETE`, and the five naming, return and wiring codes) and 4 WARNING→INFO (`V4_STATIC_FUNCTION_INVOCATION`, `L6_CONSTRAINT_NON_NUMERICAL`, `L6_BODY_ASSIGNMENT_IMPL_LOSS`, `L6_ATTR_REDEF_EXPR_DROPPED`). Each needs its row's evidence.

### Check failures

- **[INHERITED]** (epic Item 3 scope 5) A failed check reports `L6_CHECK_ERROR`, keeps safe display-only fallbacks, and keeps failed metrics distinct from clean counts. All independent failures are reported. No dependent conclusions are made up.
- **[INHERITED]** (epic Item 3 scope 5) The stale resolver citation is fixed.
- **[INFERRED]** Site-by-site classification, from code reading. Design may challenge any entry. The epic says 27 sites; the reading finds 26 `except Exception` sites plus 2 `AttributeError` catches. The audit reconciles the counts by site.
  - **Hide a failure as clean, so they become `L6_CHECK_ERROR`:** `level6_architecture.py` 191, 246, 320, 374, 418, 470, 502, 572, 623, 759, 832, 907; `adr002.py` 87, 177, 207, 254, 624.
  - **Hide a failed count as 0, so the count shows "not computed" and `L6_CHECK_ERROR` is raised:** `level6_architecture.py` 973, 978.
  - **Turn a failure into a false model defect, so they become `L6_CHECK_ERROR` with no dependent finding:** `level6_architecture.py` 520 (skipping calc usages is bypassed), 723 (the instantiated set comes out partial or empty), 230 and 289 (`AttributeError` read as a missing name); `adr002.py` 277, 335, 423 (type and EXPOSE tests return False).
  - **Already reports the failure:** `level6_architecture.py` 960. Kept.
  - **Dead code:** `adr002.py` 268. Deleted.
- **[INFERRED]** A level that raises is recorded as failed for every level (`runner.py:128-137`). An evaluator or fact-extraction crash is `L6_CHECK_ERROR`. Both follow the R3-2 gate outcome.

### Routed obligations from Item 1 (r3-proposal, owner-ratified "agreed on all")

- **[INHERITED]** (r3-proposal §1) L6 reports ES-001, ES-003, ES-004, ES-005, ES-006, ES-007 and ES-010 in one run. String omission is flagged the same way for both spellings.
- **[INHERITED]** (r3-proposal §4) L6 consumes ES-005 for UNSUPPORTED-RHS and the part-multiplicity rule for MULTIPLICITY-SHAPE. The MULTIPLICITY-SHAPE row closes here.
- **[INHERITED]** (r3-proposal §4) UNSUPPORTED-SHAPE-MESSAGE and WRAPPER-SHAPE become advisories, separate from generation behavior.
- **[INFERRED]** Their detection lives in an advisory module in agentic-mbse's `sysml/` layer, next to the contract. It sits outside `subset_profile_rules.toml` and its digest. L6 only renders the advisories. *Reason:* hand-written generator checks in L6 are the defect this item removes, and the rule records are frozen by the version rule. Design defines each advisory's exact shape from Item 1's matrix rows.
- **[INHERITED]** (P-0001 scope) P-0001 says no consumer is wired yet. At close it is updated to describe L6 as a consumer.

### `init`

- **[INHERITED]** (epic Item 3 scope 2) `init` offers an explicit target option, and an interactive choice where it fits. Noninteractive `init` keeps existing values and leaves the target unset with actionable output when none is given. It keeps unrelated TOML, comments, existing settings and symlink ownership even under `--force` (CLAUDE.md § Init File Ownership: native settings are preserved, "when the TOML layout permits").
- **[INFERRED]** `init` adds the key only as a plain line inside an existing `[tool.agentic-mbse]` table, or as a new table at the end of the file. Any other layout is refused, and the line to add is printed. The written file must parse, and every existing value must be unchanged. *Reason:* adding a header next to an inline or dotted-key definition produces a duplicate-table error.
- **[INFERRED]** The rest of the install completes when the setting step refuses. `init` exits non-zero only when `--execution-target` was given and could not be written. *Reason:* a missing setting is recoverable by hand. A failed explicit request should not look like success.
- **[INFERRED]** Interactive re-init asks again while the target is unset, with "leave unset" as the default. *Reason:* nothing records an earlier "leave unset" choice, and adding such a record is more state than the prompt is worth.
- **[INFERRED]** `install-commands` does not read or write the setting (CLAUDE.md § Change Coordination).

### Docs

- **[INHERITED]** (epic Item 3 scope 6) README, model-validation guidance and CLI output state the profile version, assessed scope, incompleteness and the L6 vs `sysml-codegen check` boundary. That check does not exist yet, so it is described as the future boundary, with no command shown (align record, owner boundary).
- **[INFERRED]** `docs/research-seam.md:350` and `:414-415` are updated to the shared key set.

## Non-Goals

- Changing generator behavior, or writing anything in sysml-codegen or Item 2 artifacts (owner boundary, 2026-10-18). Reading codegen at `b5663c07` to check citations is allowed.
- Deciding String metadata policy (Item 2).
- The PUSH-DOWN rows waiting on Item 2: CHAIN-SEGMENTS, UNSUPPORTED-OPERATOR, REDEF-PRECEDENCE, AMBIG-INHERITED-ATTR, SUM-SHAPE, LITERAL-SHAPE.
- `docs/patterns/generator-subset.md` and the guidance fence harness (Item 5). Workflow gates and MODELING_PROCESS (Item 6).
- Changing the project-root marker rule.
- Fixing the simple-name collision in `L6_CALC_DEF_NO_INSTANTIATION` (`level6_architecture.py:700-762`). The audit records it.
- Changing text-output truncation for levels other than L6, and changing other levels' checks. Only the runner's crash handling reaches them.
- Editing dc3 or fusion-tea.

## Open Questions / Deferred to design

- Exact wording of the verdict line, unset note, native summary and final-line qualifier, within the asserted phrases above.
- The JSON report's option name, schema and whether it nests per level.
- One issue per finding or per declaration (dc3 B8 shows 4 legacy diagnostics for 2 constraints), and how legacy and contract findings on the same site are grouped in the text output.
- How `pyproject.toml` is edited byte-preservingly (`tomlkit` is not a dependency; a careful text insert is the alternative).
- Where the shared key set is defined, and how the holdout guard imports it without a dependency cycle (compare `project_root.py`'s reason for living outside `cli/`).
- The exact shapes of the two advisories, and whether "shadowed by" needs owner facts the result lacks.
- Override option name and prompt text.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_executable-subset-contract.md` (Item 3; principles; Success Criteria; Items 1, 2, 5, 6 for boundaries)
- **Align record:** `.project/active/l6-subset-profile/briefs/align.md` (owner decisions; § Gate outcomes)
- **Spec review:** `.project/active/l6-subset-profile/spec-review.md` (Resolutions section)
- **Required Reading:** none listed for Item 3. Inputs used: Item 1 archive `.project/completed/20261018_exec-subset-profile/` (`design.md`, `audit.md` S2/S3, `product-lens.md` impl-F1/F2, `evidence/r3-proposal.md`, `evidence/acceptance.md`, `evidence/dc3-baseline.md`, `evidence/dc3-repaired.md`); Item 4 archive `.project/completed/20261018_positional-binding-check/` (`audit.md` finding 7); ADR 0001; P-0001; `docs/research-seam.md`
- **Code read:** `validation/level6_architecture.py`, `adr002.py`, `runner.py`, `common.py`, `positional_check.py`, `positional_pins.py`; `project_root.py`; `research/holdout.py:205-270`; `cli/__init__.py` (`cmd_validate`, `cmd_init`, argparse); `sysml/subset_profile.py`
- **Product-lens:** `.project/active/l6-subset-profile/product-lens.md`
- **Design:** `.project/active/l6-subset-profile/design.md` (to be created)

Not checked: sysml-codegen (so the codegen citations are unconfirmed); whether the consumer trees pass `validate --complete` today (`evidence/before-after.md` measures it); whether a conditional `if` reaches `V4_UNSUPPORTED_OPERATOR`; whether calc-owned asserts reach the constraint extractor; whether finding subjects carry enough to compute "shadowed by". Nothing was executed.

---

**Next Steps:** `/_my_design`.

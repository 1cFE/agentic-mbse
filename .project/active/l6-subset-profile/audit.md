# Audit: EXEC-SUBSET-CONTRACT Item 3 — L6 integration and execution-target settings

**Verdict:** Needs Work
**Audited:** 2026-10-19
**Branch:** `l6-subset-profile` (base `ebb3d467`)
**Commit:** `d0b9fb12`

---

## The Point

`agentic-mbse validate` did not tell a modeler whether the code generator would accept their model. They found generator refusals only by running the generator: dc3 found its blocker categories B1–B8 through five generation runs. Item 1 shipped a contract that can name those refusals in one pass (`subset-profile/v1`), but nothing called it. This item makes L6 run that contract and report it up front, without ever claiming the model "will generate".

Projects that only run natively must not be buried in generator noise. So each project declares its execution target in its committed `pyproject.toml` (`[tool.agentic-mbse] execution-target = "generated" | "native"`), and the target decides only how loud a result is. Unset is the default: generator findings are warnings, with a note naming the setting. The owner's ratified rule for unset is "nothing that passes today starts failing" (`briefs/align.md:16`).

The item also fixes four ways today's L6 misleads: hand-written generator checks that disagree with the contract (the String case), failed inspections that read as clean or as model defects (26 broad `except` sites plus 2 `AttributeError` catches), a crashed level that counted as a pass, and no setting at all.

## Summary

Most of this is solid. The severity table matches the spec and the align decisions cell by cell. The settings reader and the `init` writer are careful: a closed key set, every defect is an error, and the insert is verified by re-parsing. The session cache is sound. A crashed level now fails the run. The before/after evidence shows no consumer tree went from pass to fail.

One thing blocks certification. The implementer flagged it in Phase 7, and it is a misclassification. A design attribute that calls any function but `sum` now fails L6 with an ERROR under every target, including `native`. The cause is a limit that only the generator has, so it contradicts the requirement that `native` never leaves generator-only errors. It also breaks the owner's "nothing that passes today starts failing" rule for unset projects. The fix is small and the design already contains it (D15).

I did not run any command. pytest, ruff, mypy and uv all needed approval this session, and none was available. Every test and check result below comes from the implementer's recorded evidence, not from a run of mine.

## Product Judgment

**Is this the right piece of work? Yes.** It delivers what the owner asked for: the contract runs inside `validate`, refusals lead, and `clear` always carries its coverage limit and "not a generation check". The target changes loudness, never truth.

**One finding goes against what the owner asked for, and it controls the verdict.** That is Blocker B1 below. Under `native`, `attribute x : Real = abs(2.0);` in `designs/` now fails L6 with `L6_CHECK_ERROR`. The only reason is that the shared reference walker refuses every non-`sum` call. That refusal is the generator's ES-005 boundary (`reference_use.py:427-452`; its docstring calls it "a capability decision ... the generator's ES-005 refusal path"). Two recorded requirements forbid this outcome:

- The owner-ratified unset rule, "Nothing that passes today starts failing" (`briefs/align.md:16`). At `ebb3d467` this model passed L6 with one WARNING.
- The inherited rule "`native` must not leave contradictory generator-only errors" (`spec.md:169`).

The R3-2 gate outcome ("a check that ... cannot inspect what it was asked to inspect fails the run") was decided for tool faults. Here no tool is faulty: the walker is doing its job, which is refusing a shape the generator refuses. Reading the gate as covering that case turns a generator limit into a native failure. That is the exact product failure this item exists to prevent.

**Structural smells.** One fired, in a mild form: a special category exempts a case whose user-visible meaning is unchanged. D15 treats a walker's own `SemanticEvidenceError` as "could not decide" (a WARNING) for the advisories. The same signal from the same kind of walker inside V2 is treated as a crash (an ERROR). To the user both mean the same thing: "this check could not read this attribute". That inconsistency is B1. No other smell fired. No test passes only because it picks one route, and no code relies on a hidden internal representation. The two copies of the lowered-code list (`native_lowered.toml`, the audit table) are kept equal by a test, so they cannot drift apart unnoticed.

**Product-lens.** I ran it independently, and its block is appended to `product-lens.md`. It could not read its instruction file (access denied), so it ran inline and read-only, using the ledger's earlier entries as the format. Its gate is BLOCKED on impl-F1, which is the same finding as B1 here, reached independently. It also adds a test gap: the pinning test's docstring says "every target", but it runs only `Target.NATIVE`. impl-F2 is the uv question. The lens prefers writing nothing and printing the lines, or at least warning about the uv effect. My recommendation in Decision 2 is narrower: refuse only in the nested case. impl-F3 is the `wall_time_s` versus I8 point (Advisory 6). The lens found that none of the earlier conditional BLOCKs in the ledger is true in the code.

## Blockers

**B1 (must-fix). A non-`sum` call in a design attribute fails L6 under every target, including `native` and unset.** `adr002.py:524-597` (`check_static_expressions`) reads references through `design_reference_uses`, which raises `SemanticEvidenceError` on any call outside the allowlist (`reference_use.py:427-452`). The element handler at `adr002.py:596-597` turns that into `L6_CHECK_ERROR`, and `CHECK_FAILURE` is ERROR in every column (`execution_target.py:189`).

- **Failure scenario.** A native project has `attribute area : Real = sqrt(2.0);` (or `abs(...)`, `max(...)`) in a `designs/` file. At `ebb3d467`, L6 passed with one `V4_STATIC_FUNCTION_INVOCATION` WARNING. Now `validate` exits 1 under `native`, `generated` and unset, with "check_static_expressions could not inspect ... is not supported by this executable subset". The contract already reports the same site, as a refused `invocation-callable` finding, which `native` correctly folds into its INFO summary. The legacy path then fails the run anyway. The pinning test `tests/test_validation/test_l6_check_errors.py:429-446` asserts this failure under `NATIVE`.
- **Why the three consumer trees did not catch it.** None of them has a non-`sum` call in a design attribute (0 check errors on all three). That shows they are unaffected, not that the outcome is right.
- **What should change.** See Decision 1 below. In short: inside a legacy check, the shared walker's own `SemanticEvidenceError` should be a WARNING saying V2 could not inspect the attribute. It should be WARNING under every target, never in the native summary, and never silent. That is D15's rule. Any other exception stays `L6_CHECK_ERROR`. The pinning test flips to assert that. It should also be parametrized over all three targets: today it runs only `NATIVE`, although its docstring says "every target".

## The two flagged decisions

### Decision 1: Phase 7 Surprise 1. It is a misclassification, so make it a WARNING

**Recommendation:** treat it like D15. When a legacy check's call into a shared walker raises that walker's own `SemanticEvidenceError`, report a WARNING that the check could not inspect the attribute. Use WARNING under every target, never fold it into the native summary, and never make it silent. Keep `L6_CHECK_ERROR` for every other exception.

Why:

- **The raise is a decision, not a crash.** `_require_supported_invocation` (`reference_use.py:427-452`) raises on purpose for any well-formed call outside the allowlist. Its docstring calls it a capability decision kept because it is the generator's ES-005 refusal path. Nothing failed. V2 just has no answer for that attribute.
- **The design already made this call twice.** D15 (`design.md:96`) gives an advisory walker's `SemanticEvidenceError` a WARNING. It rejects "`L6_CHECK_ERROR` for every walker exception" because that "fails valid models over a WARNING-level check". D16 (`design.md:97`) separates the evaluator's own "not a static number" signal from a real failure. V2's walker refusal is the same kind of signal. I1 (`design.md:205`) names D15 as its only exception only because nobody had yet seen the V2 path.
- **Nothing is relaxed.** At `ebb3d467`, V2 skipped this attribute silently (`adr002.py:624`, the old broad `except`). A WARNING is strictly louder than that, so R3-1 is untouched. The ERROR the implementation produces now is a new failure of the R3-2 kind for unset projects, and a generator-only error under `native`.
- **The generator side is already covered.** Under `generated`, the contract's `invocation-callable` refusal is an ERROR. So a generated project still fails on this attribute, for the right reason.

Scope of the change: only `SemanticEvidenceError` raised by a shared walker inside a legacy check. A raise from SysIDE accessors, an `AttributeError` or anything else stays `L6_CHECK_ERROR`. One more test is needed: the walker raises a non-`SemanticEvidenceError` and the result is still `L6_CHECK_ERROR`.

### Decision 2: Phase 9 uv side effect. Keep creating the file, but refuse when it would split a parent uv project

**Recommendation:** keep the spec's behaviour (create a table-only `pyproject.toml`) when no parent directory has a `pyproject.toml`. When one does, refuse and print the line to add by hand. Say that writing the file would make uv treat this folder as a separate project. Grade: should-fix, not a blocker. The current code meets the spec as written (`spec.md:64`).

Why:

- **The standalone case does no harm.** In a folder that is not inside a uv project, the file only means that `uv run` there would create a `.venv` and print a `requires-python` warning. `uv lock` succeeding instead of exiting 2 changes nothing a modeling project relies on. Refusing here would make the user write the same file by hand, with no benefit.
- **The nested case breaks things.** Say a model folder sits inside a repo whose `pyproject.toml` depends on agentic-mbse, and the user runs `init --execution-target=native` in that folder. The new file makes it a separate uv project. After that, `uv run agentic-mbse validate` there uses a new, empty `.venv` and no longer finds the tool (plan.md Phase 9 notes, third uv bullet). `init` reports success, but the user's next command breaks for a reason they cannot see.
- **Refusing in that case is honest, not a dead end.** The note tells the user the real choice. They can put the setting in the parent's `pyproject.toml`, if the parent should be the project root, or accept a separate project. `init` cannot know which one they want.

Implementation note (not drafted): this needs a walk up the parent directories looking for `pyproject.toml`, in `inspect_execution_target` (`project_settings.py:181-189`), as a new `Blocked` layout reason. It also needs one golden or CLI test.

## Advisory

1. **(should-fix) Two early L6 exits drop the target metric.** `level6_architecture.py:1142-1150` (path discovery `ValueError`) and `:1163-1171` (model load failure) return a failed result with no `Execution target` metric and no `report_detail`. The spec says every L6 run states the target and its source (`spec.md:60`). *Scenario:* a model with a fatal load error. L6 fails correctly, but the JSON report's L6 `profile` is `null`, and nothing records which target or file was read. The run still fails, so the risk is low.
2. **(should-fix) One failed enumeration in `check_qualified_names` skips an independent check.** `level6_architecture.py:225-228` returns as soon as calc-def enumeration fails, so the calc-usage half (`:271-317`) never runs. The spec asks that "all independent failures are reported" (`spec.md:193`). *Scenario:* the `CalculationDefinition` listing raises. The user sees one check error, and any `L6_INVALID_QUALIFIED_NAME` on calc usages stays hidden until the first failure is fixed. The run fails either way.
3. **(note) `L6_CALC_DEF_NO_INSTANTIATION`'s native lowering rests on weak evidence.** `evidence/legacy-l6-audit.md:34` records a caveat against its own category: "a native route that evaluates instances has nothing to evaluate either". `L6_MISSING_QUALIFIED_NAME` (`:22`) is marked "Confirmed (weak)" too. Both meet the spec's second test, "a cause that exists only in the generator" (`spec.md:170`). Neither has a SysIDE or fixture result for the native route. *Scenario:* a native project with an uninstantiated calc-bearing part def sees one INFO count instead of an ERROR. That is defensible, because nothing fails natively, but it is a judgment call. The owner may want to know that 2 of the 4 lowerings are judgment calls.
4. **(note) A permission error on `pyproject.toml` crashes `init` after the install.** `project_settings.py:194` calls `read_bytes()` without catching `OSError`. The reader at `:71` does catch it. *Scenario:* `pyproject.toml` is unreadable (mode 000). `init` installs everything, then exits with a traceback instead of a `Blocked` message. Rare.
5. **(note) The evaluator's `float(None)` TypeError now reads as a check error, not UNEXTRACTABLE.** `expression.py:590-593` converts only `ValueError`. A literal whose `value` is `None` or not a number raises a plain `TypeError`, which `check_design_attr_completeness` now reports as `L6_CHECK_ERROR` (`level6_architecture.py:596-597`). Both are ERROR, so pass/fail is unchanged. Only the label differs. Not seen on any consumer tree.
6. **(note) `wall_time_s` breaks byte-identical reports.** The implementer surfaced this (plan.md Phase 4 deviations). The I8 test blanks the field. That is acceptable. Recorded here so the owner sees the trade.

## Findings Detail

### Plan completion

All 11 phases are ticked, each with notes. I checked the code each phase claims against the diff. I found no placeholder code, TODO, dead branch or stub. The one deleted dead helper (`_get_calc_usage_names`, which was `adr002.py:268`) is gone, as Appendix B planned. Every former broad `except` in `level6_architecture.py` and `adr002.py` now reports an `L6_CHECK_ERROR` at element or check scope, except three. `level6_architecture.py:105` catches named manifest exceptions. `:564` catches the evaluator's `Unextractable` signal (D16). `:605` catches the `ValueError` from `element_id` that marks "no id", in which case the legacy String error stays. All three are deliberate and narrow. `_guarded` (`:1009-1014`) is the only broad catch left, and it always emits an `L6_CHECK_ERROR`.

### Spec conformance

- **Settings states.** Met by reading: generated exit 1 / native exit 0 / unset exit 0 with note (`test_l6_contract.py:139`, `:149`). Malformed, unknown value, unknown key and the underscore table are errors even with an override (`execution_target.py:97-109`; `test_l6_settings_cli.py:21-64`). The override wins and says so (`describe_target`, `execution_target.py:127-132`).
- **One key set, two readers.** Met. `TOOLKIT_KEYS` (`project_settings.py:28`) is the only definition. The reader checks keys, never values (`:64-107`). The holdout guard reads through it and validates only `holdout-guard` (`holdout.py:220-235`). A bad guard does not fail validate (`test_l6_settings_cli.py:114`).
- **Where the setting is read from.** Met. `find_project_root(start=models_path)` is used unchanged (`execution_target.py:91`). A run with no root is unset and names `--execution-target` (`:133-134`).
- **`init`.** Met as specified. The writer re-parses its own output and writes only if the result equals the original plus one key (`project_settings.py:244-252`). It writes atomically and keeps the file mode (`:277-289`). Symlinks, hard links, a BOM, non-UTF-8 text, a broken file, an inline table, dotted keys and duplicate headers are all refused (`:184-223`). No `--force` path reaches the writer (`cli/__init__.py:721-747`). Golden tests run with and without `--force` (`test_init_execution_target.py:51-65`). See Decision 2 for the uv case.
- **Presentation.** Met, with B1 as the exception. Banned wording is scanned across stdout and the report for every fixture × target (`test_l6_contract.py:105`). The verdict line carries both versions, the counts and "not a generation check" (`subset_presentation.py:199-220`). `clear` is followed by the coverage limit (`:223-228`). The final-line qualifier fires for unset, and for generated with any verdict but `refused` (`:433-434`).
- **Structured report.** Met. Every level's structured issues, its unstructured strings and its summarized results are written untruncated, plus L6's full profile (`report.py:53-64`). A dc3-sized fixture is checked against the evaluator's count (`test_l6_contract.py:497`).
- **Check failures fail under every target.** Met. `CHECK_FAILURE` is E/E/E (`execution_target.py:189`). A crashed level is a failed level named `LEVEL_CRASHED` (`runner.py:64-77`, `:146-151`). The five over-reporting sites no longer produce dependent findings (`adr002.py:315-405`; `level6_architecture.py:746-755`). The native summary prints "not computed" for a step that failed (`subset_presentation.py:473-481`). **But see B1:** one class of "cannot inspect" is not a failure at all.
- **Both String spellings.** Met. Suppression is by the contract's omitted subject ids (`level6_architecture.py:560-561`; `subset_presentation.py:110-114`). If the contract did not run, every legacy error stays.
- **Library additions.** Met by reading. `subset_coverage.py` is new with its own version. `SUBSET_PROFILE_VERSION` is unchanged (spec test cited in plan Phase 5). Advisories are at most WARNING, and they go to the INFO summary under native (`execution_target.py:184-185`).
- **Consumer evidence.** Met. `dc3-baseline-l6.md` matches Item 1's counts (236 / 32 / 6 / 50, `refused_incomplete`). `dc3-repaired-l6.md` shows `clear` with 30 omitted. `before-after.md` shows no pass→fail.
- **Audit and docs.** Met. `legacy-l6-audit.md` has 17 code rows plus manifest and setup failures, and the lowered table. A test keeps the code, the fixture and the audit equal.
- **Repo checks.** Recorded as met in `evidence/repository-checks.md`: 6 known failures, mypy 97, ruff 118, the same sets as the baseline. **I did not re-run any of these.**

**The severity table, cell by cell** (`execution_target.py:176-191`, against `spec.md:144-153` and `briefs/align.md:15-19`, `:37-39`):

| Category | unset / generated / native | Matches |
|---|---|---|
| refused | W / E / summary | spec "generated makes confirmed refusals errors", native summary |
| unconfirmed | W / W / summary | never ERROR (P-0001) |
| excluded, omitted | W / W / summary | owner: warnings under generated with own reasons |
| admitted | count only | — |
| unverified | W / E / own WARNING | gate outcome; native keeps it outside the summary |
| unassessed | W / W / summary | spec `:153` |
| advisory | W / W / summary | spec `:107` |
| advisory unverified | W / W / W | D15; never folded |
| legacy own-applicability, legacy kept | own severity everywhere | — |
| legacy generator-only | own / own / summary | exactly the four codes plan Phase 8 names (`execution_target.py:209`, `:216`, `:217`, `:220`) |
| check failure, setting invalid | E / E / E | epic scope 3 |

An unknown legacy code falls back to "kept" (`subset_presentation.py:256`), so a new code can never be lowered by accident.

**The R3-1 gate outcome holds.** I traced each changed catch. No existing L6 ERROR becomes a non-ERROR under unset or `generated`, except the String replacement the gate recorded. Every former "return False" or "skip on failure" now gives `L6_CHECK_ERROR` (still ERROR). The `except (ValueError, TypeError)` narrowed to `Unextractable` sends everything else to `L6_CHECK_ERROR` (still ERROR). The before/after record agrees: `L6_DESIGN_ATTR_UNEXTRACTABLE` went from 3 to 0 on dc3 `808464d`, and those 3 are its String errors. fusion-tea stayed at 108 → 108.

### Design conformance

The implementation follows the design: contract first, then the legacy checks, advisories, manifests and presentation (`level6_architecture.py:1173-1221`). The modules sit where the design put them. D3, D4, D9, D10, D13, D14, D15 and D16 are each visible in the code. The recorded deviations (`describe_target` placement, invalid value under override, `wall_time_s`, header probe) are documented in plan notes and are reasonable. The one place the code follows the letter of the design against its own reasoning is I1 versus D15, which is B1.

D9 "shadowed by" matches on the same subject id, not the spec's owner-based condition. The design records this choice and its reason (`design.md:44`, `:90`). dc3 shows all 6 B8 findings shadowed by B1.

### Code integrity

- **Session (`validation/session.py`).** Sound. The cache key is the resolved path list. A hit also needs every file's size and `mtime_ns` to match (`:75-83`), so a changed file reloads. Stamps are taken before the load, so a file edited during a load reloads next time. Directories are refused (`:33-36`). The facts memo keys on `id(model)` and holds the model, so ids cannot be reused while the session is open (`:47-50`). `__exit__` resets the context variable and clears both caches whatever the outcome (`:61-71`), and sessions refuse to nest (`:56-57`). One session per `run_all_checks` call (`runner.py:141`), so nothing carries over between runs. A stored extraction error is re-raised, never swallowed (`:91-99`).
- **Settings reader and writer.** Closed key set, every defect named, no value checks in the reader. The writer verifies its insert by re-parsing (`project_settings.py:244-252`). Advisory 4 is the one hole.
- **Presentation.** No outcome logic. Every severity goes through `display()`. The native summary never prints 0 for a step that did not run.
- **Tests.** The forced-exception tests patch only the named function's read (by caller frame) on a real model, and a no-fault control run shows each site is reached (plan Phase 7 notes). These are not tests of the mock. The init golden files were written by hand, so they are not generated from the code they test.
- **Not slop, but worth knowing:** `validate_architecture` (`level6_architecture.py:1109-1264`) is about 150 lines. It reads in order, and each step is one guarded call. It does not need splitting now.

---

## Certification

**Checked:** spec, design rev 1, plan (all 11 phases and notes), `briefs/align.md`; the full `src/` diff `ebb3d467..HEAD` for `execution_target.py`, `project_settings.py`, `session.py`, `subset_presentation.py`, `report.py`, `runner.py`, `common.py`, `cli/__init__.py`, `holdout.py`, `adr002.py`, `level6_architecture.py` and the evaluator's `Unextractable` raises in `expression.py`; the names and scope of the tests in the new test files; `evidence/legacy-l6-audit.md`, `repository-checks.md`, `dc3-baseline-l6.md`, `dc3-repaired-l6.md`, and the before/after table in plan Phase 11.

**Marked:** nothing. The verdict is Needs Work. The brief also asks for `audit.md` only to be committed. So I did not tick spec success criteria, change the epic heading or edit `CURRENT_WORK.md`. Once B1 is fixed, a targeted re-check of B1 is enough to certify, and the success-criteria ticks can be made then.

**Not checked:**

- I ran nothing: no pytest, ruff, mypy, uv or `validate`. Every pass/fail number comes from the implementer's evidence files.
- I did not read `subset_advisories.py`, `subset_coverage.py`, `subset_extraction.py`, the `expression.py` refactor (`_reconstruction_branch`, `falls_to_text_fallback`), or `scripts/l6_subset/run_consumers.py` line by line.
- I did not verify the reconstruction-text record (`reconstruct_texts_ebb3d467.json`).
- I did not check whether docs edits (README, `skills/model-validation/SKILL.md`, `docs/research-seam.md`, CLAUDE.md) say exactly what the shipped-text tests assert.
- I re-read no codegen citation at `b5663c07`.
- I did not check whether other `SemanticEvidenceError` raise sites besides `_require_supported_invocation` can reach legacy checks. That matters for the scope of the B1 fix.
- I did not check the consumer trees myself.

# Spec: L6 integration and execution-target settings

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Complexity:** MEDIUM (one evaluator wired into one level, one setting, one `init` option, an audit of 19 existing L6 codes, docs)
**Branch:** `l6-subset-profile` (off `main` at `ebb3d467`)

---

## Problem

`agentic-mbse validate` does not tell a modeler whether the code generator will accept their model. Item 1 shipped the contract that can say so (`src/agentic_mbse/sysml/subset_profile.py`, `subset-profile/v1`), but nothing calls it. A modeler finds generator refusals only by running the generator. dc3 found its blocker categories B1–B8 through five sequential generation runs (dc3 T-001). Item 1's evaluator now reports 236 refused findings on that same baseline in one pass. That figure is the evaluator's count, not a count of refusals the generator produced.

[AGENT] (ratified by owner, 2026-10-18; `briefs/align.md`) `validate` should report that contract up front. Projects that only run natively must not be buried in generator noise, so each project declares its execution target.

Today's L6 makes this harder in four ways (all verified by reading the code; nothing was run):

- **Hand-written generator checks overlap the contract and disagree with it.** For example, L6 flags `attribute x : String = "abc"` as an error, but only under `designs/`, and never sees the `:>> x = "abc"` spelling, which SysIDE parses as a reference usage (`level6_architecture.py:476-575`, `:853`). On dc3 baseline that is 3 flagged against 32 String declarations (`completed/20261018_exec-subset-profile/evidence/acceptance.md:27`).
- **Failed inspections read as clean.** There are 26 broad `except Exception` sites in `level6_architecture.py` (17) and `adr002.py` (9). 19 of them turn a failure into "no issue" or a zero count (listed under Known Requirements, check failures).
- **A crashed level counts as a pass.** When a level raises, `runner.py:128-137` prints the error but never records the level, so `overall_success` (`common.py:66`) stays true and exit is 0. The comment at `runner.py:135` says "Treat exceptions as failures". `check_constraint_executability` lets its errors reach this path on purpose (`level6_architecture.py:647-650`). No test covers it.
- **There is no setting.** Nothing in `src/` reads or writes an execution target, and nothing writes `pyproject.toml`.

## Success Criteria

Each criterion names the test or evidence file that shows it. "Test" means a pytest test under `tests/`. "Evidence" means a file under `.project/active/l6-subset-profile/evidence/`. Where a criterion asserts ERROR for a check or configuration failure with the target unset, it holds only if the owner accepts that R3-2 proposal (Open Questions). Otherwise the test asserts the behavior the owner chose instead.

**Settings states** (CLI tests that run `agentic-mbse validate --level=6` on a fixture project)

- [ ] `execution-target = "generated"`: a fixture with a refused finding exits 1, with that finding at ERROR.
- [ ] `execution-target = "native"`: the same fixture exits 0. Generator-only findings appear as one INFO summary, and the detailed results are still available (design picks how).
- [ ] Unset (no `pyproject.toml`, no table, or no key): the same fixture shows the refusal as a WARNING, plus a note naming the setting and how to set it. A fixture with no generator findings at all also shows the note. No output line says or implies the model is generated-ready.
- [ ] When L6 passes with generator findings at WARNING (unset), or with a `clear`, `unconfirmed`-only or omissions-only result (`generated`), the run's final summary line includes a qualifier that generated compatibility is not established. Today that line reads "All quality checks passed!" with no qualifier. Item 4's pinned-positional note is the precedent (`common.py:161-176`, `runner.py:156-157`).
- [ ] Malformed `pyproject.toml`: exits 1 with an error naming the file and the parse error. It does not fall back to unset.
- [ ] Unknown value (e.g. `"generate"`, `1`, `""`): exits 1 with an error naming the value and the two allowed values.
- [ ] `--execution-target=native` on a project whose file says `generated` behaves as native for that run, and the output says the override was used. The same holds the other way round.
- [ ] A project that also has `[tool.agentic-mbse.research] holdout-guard = …` keeps working. Both the research holdout guard and L6 accept the combined table (test in the research tests plus a CLI test).

**Where the setting is read from** (tests)

- [ ] The setting is read from `<project root>/pyproject.toml`, where the root comes from `find_project_root(start=<validated path>)` (`src/agentic_mbse/project_root.py:19`). A test validates a subdirectory and shows that the root's file is used. A `pyproject.toml` closer to the models, below the root, is ignored.
- [ ] With no project root above the validated path, L6 runs as unset. A metric says no root was found and that `--execution-target` sets the target for one run. This mirrors the L2 pin-list metric (`positional_check.py:187-189`).
- [ ] The L6 metrics always state the target in effect and where it came from: file path, override, or unset with the path that was looked at.

**`init`** (tests)

- [ ] `init --execution-target=generated` (or `native`) writes `execution-target` under `[tool.agentic-mbse]` in the target's `pyproject.toml`.
- [ ] Interactive `init` (stdin is a terminal, no option, no existing value) asks for generated, native or leave unset, and writes what was chosen.
- [ ] Noninteractive `init` with no option leaves the target unset. Its output says the target is unset and gives both ways to set it: the TOML line, and `init --execution-target`.
- [ ] An existing value is never changed, not by a re-init, not under `--force`, and not by an option that disagrees with it. A disagreement is reported in the output.
- [ ] A golden-file test: unrelated tables, keys, comments, blank lines and key order in `pyproject.toml`, including an existing `[tool.agentic-mbse.research]` table, are byte-for-byte unchanged after `init` adds the key, with and without `--force`.
- [ ] `init` does not replace a symlinked `pyproject.toml` with a regular file.

**Consumer evidence** (git archive copies, never the consumer checkouts)

- [ ] `evidence/dc3-baseline-l6.md`: one `validate --level=6 --execution-target=generated` run on dc3 `808464d` shows every confirmed category in one output. B1–B6 appear as refused errors, B7 as omitted warnings and B8 as unconfirmed, labelled as shadowed by B1. Each finding has a location, a stable reason and a remedy. The counts match Item 1's record (`evidence/dc3-baseline.md`): 236 refused, 32 omitted, 6 unconfirmed and 50 unverified, under verdict `refused_incomplete`. Any difference is explained.
- [ ] The same file records a second run on dc3 `808464d` with the target unset, at WARNING.
- [ ] `evidence/dc3-repaired-l6.md`: dc3 `60b44d5` under `generated` reports verdict `clear` with 30 omitted-String warnings. The output words it as "no refusals found by the implemented rules", followed by the coverage limit, and not as ready to generate.
- [ ] `evidence/r3-2-before-after.md`: with the target unset, L6 pass/fail and exit codes before and after this change, for dc3 `808464d`, dc3 `60b44d5` and fusion-tea `f96ad312`. Every result that changes from pass to fail is listed as an R3-2 case. It is not fixed silently.

**Both String spellings** (test plus evidence)

- [ ] A fixture with `attribute x : String = "abc"` and one with `:>> x = "abc"`, both inside and outside `designs/`, give the same subset outcome (`omitted`), the same reason (`string_value_not_generated`) and the same severity for each target. Whatever the legacy String error (`L6_DESIGN_ATTR_UNEXTRACTABLE`) still does is listed by spelling in `evidence/legacy-l6-audit.md` and stays an open R3-1 case until the owner decides it.

**Presentation** (tests on rendered output)

- [ ] For each verdict and each target, the whole rendered `validate` output contains none of the wording below. That includes L6's lines, the level title (today "Architecture & Pipeline Readiness") and the run's final line. The banned wording is "generated-ready", "ready to generate", "will generate", "generator accepts", or an unqualified "clean"/"pass" next to the profile verdict. A test checks the rendered output for all five verdicts.
- [ ] A `refused_incomplete` result leads with the refusal count and states the incompleteness next to it (impl-F2).
- [ ] A `clear` result prints the profile version, the assessed scope and the coverage limit (impl-F1).
- [ ] A test checks the contract's coverage list against the no-rule rows of Item 1's matrix. Another test shows that `SUBSET_PROFILE_VERSION` and its pinned digest are unchanged from `main` at `ebb3d467`.

**Native never hides check failures** (tests)

- [ ] Under `native`, an injected L6 inspection failure (monkeypatched) is reported as `L6_CHECK_ERROR` at ERROR and fails the level. It is not counted in the INFO summary.
- [ ] Under `native`, a native-correctness error (for example `L6_CALC_DEF_NO_OUTPUT`, if the audit keeps it as native correctness) stays ERROR.
- [ ] Each fake-clean exception site, and the two `AttributeError` catches at `level6_architecture.py:230` and `:289`, has a test that forces the exception and asserts `L6_CHECK_ERROR` with the check's name, under every target. Under `native`, none of them is counted in the INFO summary. The affected count says "not computed" rather than 0.

**Legacy audit and docs**

- [ ] `evidence/legacy-l6-audit.md` lists every L6 check and issue code, including manifests and setup, as a table. Each row gives what the check does today, its severity today, its category (shared-decision duplicate, retained generator-specific, native correctness, ADR-002, manifest), and its severity under generated, unset and native. A final column flags any R3-1 or R3-2 case.
- [ ] README, `skills/model-validation/SKILL.md` and the L6 CLI output each state the profile version (`subset-profile/v1`), what was assessed, that the assessment is incomplete relative to the generator, and that L6 is not `sysml-codegen check`. A shipped-text test checks for each of these statements.
- [ ] `uv run pytest tests/`, `uv run mypy src/` and `uv run ruff check src/ tests/` pass. The evidence says which tests needed the SysIDE licence and which were skipped.

## Known Requirements

### The setting

- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good"; `briefs/align.md`) The setting is `[tool.agentic-mbse] execution-target = "generated" | "native"` in the target project's `pyproject.toml`. It is committed, so the owner, teammates and CI get the same result. An environment variable was considered and is out because it differs per machine.
- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") A one-run command-line override (`validate --execution-target=…`) takes precedence over the file for that run.
- **[INHERITED]** (epic Item 3 scope 1) A malformed TOML file and an unknown value are errors, not unset.
- **[HARD]** `research/holdout.py:241-260` already owns `[tool.agentic-mbse]` and rejects every key there except `research`. It also rejects a `[tool.agentic_mbse]` table. Adding `execution-target` without changing that guard breaks the research seam for any project that sets the target. Both readers must agree on one closed set of keys.
- **[INFERRED]** The setting is read only from the project root's `pyproject.toml`, using `find_project_root` unchanged. *Reason:* the brief says to reuse Item 4's discovery, and Item 4 reads only at the root (ADR 0002, D11). A tree under `$HOME` with no marker of its own resolves to `$HOME` because `~/.claude/` counts as a marker (Item 4 audit finding 7). The metric shows the path that was looked at, so this stays visible. Changing the marker rule is out of scope.
- **[INFERRED]** The override accepts only `generated` and `native`. *Reason:* "unset" is the absence of a decision, and the owner described the override as choosing a target.
- **[INFERRED]** A malformed file or an unknown file value is still an error when an override is given. *Reason:* the file is shared with the holdout guard and with uv. An override chooses this run's target; it does not make a broken file valid.
- **[INFERRED]** The setting is read only when L6 runs. A setting error is an L6 issue. `--execution-target` with `--level` 1–5 is accepted and has no effect. *Reason:* "errors for checks actually requested" (epic Item 3 scope 3).
- **[INFERRED]** The `[tool.agentic_mbse]` underscore spelling is rejected, as the holdout guard already does.

### Severity by target

- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") Unset is the default. It shows generator findings as warnings, with a note naming the setting. Unset never labels a model generated-ready.
- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") `native` turns generator-only findings into an INFO summary. `generated` makes confirmed refusals errors.
- **[INFERRED]** [AGENT] (ratified by owner, 2026-10-18, owner reply "yes, good") Under `generated`, exclusions (non-numerical predicates) and omissions (dropped String values) are warnings, each with its own reason, not errors. String policy itself stays with Item 2.
- **[INHERITED]** (epic Item 3 scope 3) Check and configuration failures are errors for checks actually requested, whatever the target. An inspection failure is never folded into a native summary. Native correctness errors stay errors.
- **[INHERITED]** (epic principle 1; Item 1 `design.md:70-74`, `:341`) L6 owns severity. It maps the evaluator's verdict and outcomes to severity and does not re-derive a decision the contract holds. No agentic-mbse module imports sysml-codegen (ADR 0001 invariant 3).
- **[INFERRED]** `unconfirmed` findings are WARNING under `generated` and unset, and part of the INFO summary under `native`. They are never ERROR. *Reason:* P-0001 allows `refused` only with a retained generator probe, so an unconfirmed finding has no evidence that would justify blocking. The two contexts that are unconfirmed by design (`beyond_generator_roots`, `beneath_refused_multiplicity`; r3-proposal §3 row :60) say which context made them unconfirmed. B8 is labelled as shadowed by B1 (`acceptance.md:31`).
- **[INFERRED]** The evaluator's unverified checks (rule-level "could not assess") are ERROR under `generated`. Under `native` they get their own WARNING line, never part of the INFO summary. *Reason:* under `generated` the capability checks are the checks requested, so not finishing them is a check failure. Under `native`, epic scope 3 forbids folding them into the summary.
- **Pending owner (R3-2): unverified checks under unset.** The epic's rule says check failures are errors whatever the target. Applied to unset, that fails any project with an unverified check that passes today, which is an R3-2 case. The proposal is WARNING under unset, matching the owner's unset-is-warnings decision. The alternative is ERROR, following the epic's rule. Either way they are never counted as clean. This spec does not choose (see Open Questions, R3-2).
- **[INHERITED]** (epic Item 3 scope 5) A crash of the evaluator itself, or of fact extraction as a whole, is `L6_CHECK_ERROR` at ERROR under `generated` and `native`. Under unset it is the same proposal, pending R3-2.

### How results are presented (impl-F1, impl-F2, r3-proposal §2 row :44)

- **[INHERITED]** (ADR 0001 invariant 2; r3-proposal :44, owner-ratified) `clear` means no refusals over the implemented rules, not "will generate". No verdict, target or summary line is worded as generated-ready.
- **[INHERITED]** (Item 1 product-lens impl-F2; audit S3) L6 shows the worst outcome and completeness as two separate facts. `refused_incomplete` leads with the refusals, so an author with `generated` sees "the generator will refuse this", not "we couldn't finish".
- **[INHERITED]** (Item 1 product-lens impl-F1; audit S2: "consumer wording is Item 3") Next to the verdict, L6 shows the coverage limit: the families the contract has no rule for, such as DEEP-QUALIFIED-WIRING, ES-002, ES-008, ES-009, the ES-010 refusal side, CALC-DEF-BARE-RESULT and the explicit follow-up sites. `SubsetProfileResult` does not carry this today (`ScopeReport`, `subset_profile.py:716`).
- **[INFERRED]** The coverage limit comes from the contract (Item 1's library or its packaged records), not from a list maintained by hand in L6. *Reason:* impl-F1 names a list kept in the consumer as the defect ("a consumer compensating for a missing producer guarantee").
- **[INFERRED]** That library change only adds. It does not change `SUBSET_PROFILE_VERSION`, the digest pinned to it, existing result fields or any decision. *Reason:* the Item 2 agent consumes this result shape and pins this version, and Item 2 is off limits. If design finds the coverage limit cannot be added without changing the version or digest, it stops and asks the owner. It does not bump the version.
- **[INFERRED]** When the run passes, its final line carries the generated-compatibility qualifier whenever the target is unset, or whenever the target is `generated` and the verdict is not `refused`. Under unset, the note naming the setting appears even when there are no generator findings. *Reason:* L6 passes on WARNING, so without this an unset run with refusals ends in "All quality checks passed!" under a level titled "Pipeline Readiness". Item 4 qualifies the final line for pinned warnings the same way.
- **[INFERRED]** Every L6 run that assesses the profile prints the profile version, the executable-profile version, the roots used, whether the selection was narrowed, and the fact kinds not enumerated (`ScopeReport`). Each finding prints its rule, reason, location (`SafeLocation`) and the record's `remedy` and `semantic_limits`. A finding is not linked to `docs/patterns/generator-subset.md` while that file does not exist; Item 5 creates it.
- **[INFERRED]** "Generated-ready" never appears in this item's output for any state. *Reason:* only the future `sysml-codegen check` (Item 2) can support that claim, and L6 states that boundary.

### Legacy L6 checks

- **[INHERITED]** (epic Item 3 scope 4) Every existing L6 check is audited. Duplicates of shared decisions are replaced by the contract's findings. Retained generator-specific checks go through the target policy. ADR-002 placement (`V1`, `V2`, `V4_UNSUPPORTED_OPERATOR`) and manifest checks keep their own documented applicability under every target. `native` must not leave contradictory generator-only errors in place.
- **[INHERITED]** (align record, R3-1) The audit may replace duplicates with shared decisions. A net relaxation under unset or `generated` goes to the owner. Lowering a legacy generator-only error to INFO under `native` is not an R3-1 case, because R3-1 covers only unset and `generated`.
- **[INFERRED]** Where a legacy check and a contract rule report the same site, the combined severity under unset and `generated` is never lower than today's, unless the owner decides otherwise under R3-1.

What the inventory shows (read from code, not run; `evidence/legacy-l6-audit.md` will be the full record):

| Legacy code | Today | Proposed disposition | Gate |
|---|---|---|---|
| `V1_CALC_DEF_LOCATION`, `V2_DYNAMIC_EXPRESSION`, `V4_UNSUPPORTED_OPERATOR` (ERROR) | ADR-002 placement and static design attributes | Unchanged under every target | — |
| `V4_STATIC_FUNCTION_INVOCATION` (WARNING) | Function call in a design attribute | Duplicate of `invocation-callable`. Replaced: WARNING unset, ERROR generated, INFO native | — |
| `L6_CONSTRAINT_MALFORMED_NUMERICAL` (ERROR) | `executable_profile` BLOCK. `UNASSESSED` produces no issue (`level6_architecture.py:674`) | Duplicate of `constraint-predicate`. Replacing it would make unset a WARNING, which is a relaxation. `UNASSESSED` becomes visible as unverified | **R3-1** |
| `L6_CONSTRAINT_NON_NUMERICAL` (WARNING) | Non-numerical predicate | Duplicate of `constraint-predicate` excluded: WARNING generated and unset, INFO native | — |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (ERROR), String values, `attribute` spelling, `designs/` only | Indirect String error | Duplicate of `string-value-omission`. Owner policy says omissions are warnings under `generated`, so replacing it relaxes an error | **R3-1** |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (other values), `L6_DESIGN_ATTR_INCOMPLETE` (ERROR) | Design attribute with no value, or one the evaluator cannot read | Retained generator-specific: ERROR unset and generated, INFO native | — |
| `L6_MISSING_QUALIFIED_NAME`, `L6_INVALID_QUALIFIED_NAME`, `L6_ANONYMOUS_RETURN`, `L6_CALC_DEF_NO_INSTANTIATION`, `L6_INVALID_BINDING_FORMAT` (ERROR) | Generator naming, return and wiring rules | Retained generator-specific: ERROR unset and generated, INFO native | — |
| `L6_BODY_ASSIGNMENT_IMPL_LOSS`, `L6_ATTR_REDEF_EXPR_DROPPED` (WARNING) | Generator silent-loss warnings | Retained: WARNING unset and generated, INFO native | — |
| `L6_CALC_DEF_NO_OUTPUT` (ERROR), `L6_CALC_DEF_NO_DIRECTION` (WARNING) | Calc def structure | Native correctness: unchanged under every target (design confirms the category) | — |
| Manifest strings; model-load and missing-path failures | Fail the level | Unchanged under every target | — |
| `part-multiplicity`, `calc-owned-assertion` (new) | No L6 counterpart today | New findings: WARNING unset, by outcome under `generated` | — |

### Check failures (epic Item 3 scope 5)

- **[INHERITED]** (epic Item 3 scope 5) A failed check reports `L6_CHECK_ERROR`, keeps safe display-only fallbacks, and keeps failed metrics distinct from clean counts. All independent failures are reported. No dependent conclusions are made up.
- **[INHERITED]** (epic, "27 broad exception sites") The epic's count is 27. The inventory finds 26 `except Exception` sites. The 19 that make a failure read as clean are `level6_architecture.py` 191, 246, 320, 374, 418, 470, 502, 572, 623, 759, 832, 907, 973 and 978 (the last two affect counts only), and `adr002.py` 87, 177, 207, 254 and 624. The other 7 over-report rather than hide (`level6_architecture.py` 520, 723; `adr002.py` 277, 335, 423), report the failure already (`level6_architecture.py` 960), or are dead code (`adr002.py` 268). The audit reconciles 26 against 27 by site. The two narrower `AttributeError` catches at `level6_architecture.py:230` and `:289` turn an inspection failure into a model-defect finding (`L6_MISSING_QUALIFIED_NAME`); they are in scope too.
- **Pending owner (R3-2): an exception that escapes a level** (`runner.py:128-137`). The proposal is that it fails the level and the run. It is a check failure for a check that was requested (epic scope 3), and the code's own comment says it should be. By construction it fails some project that passes today, so it waits for the owner.
- **[INHERITED]** (epic Item 3 scope 5) The stale resolver citation is fixed. The one candidate is `level6_architecture.py:847`, which cites codegen's `hierarchy_resolver._extract_single_redefinition`. It could not be confirmed, because sysml-codegen was not readable in this session. Design confirms it read-only at the pinned codegen revision `b5663c07`. The dead citation at `common.py:84` (`test_sysml_parsing.py:82-100`, which does not exist) is fixed in the same pass.

### Routed obligations from Item 1 (r3-proposal, owner-ratified "agreed on all")

- **[INHERITED]** (r3-proposal §1 :16-20, :23, :24) L6 reports ES-001, ES-003, ES-004, ES-005, ES-006, ES-007 and ES-010 in one run. String omission is flagged the same way for both spellings.
- **[INHERITED]** (r3-proposal §4 :70, :71) L6 consumes ES-005 for UNSUPPORTED-RHS and the part-multiplicity rule for MULTIPLICITY-SHAPE. The MULTIPLICITY-SHAPE row closes here.
- **[INHERITED]** (r3-proposal §4 :67, :74) UNSUPPORTED-SHAPE-MESSAGE and WRAPPER-SHAPE become L6 advisories, separate from generation behavior. Design decides their wording and severity, which is at most WARNING under any target, because they are not refusals.
- **[INHERITED]** (P-0001 scope, `.project/product/0001-*.md:32`) P-0001 says no consumer is wired yet. It is updated at close to describe L6 as a consumer.

### `init`

- **[INHERITED]** (epic Item 3 scope 2) `init` offers an explicit target option, and an interactive choice where it fits. Noninteractive `init` keeps existing values and, when no target is given, leaves it unset with actionable output. It keeps unrelated TOML, comments, existing settings and symlink ownership, even under `--force`, following the native-settings rule in CLAUDE.md § Init File Ownership.
- **[INFERRED]** If the target has no `pyproject.toml` and a target was chosen, `init` creates one containing only the `[tool.agentic-mbse]` table. With no target chosen it creates nothing. *Reason:* the setting must live in that file, and an unset target needs no file.
- **[INFERRED]** If `pyproject.toml` is a symlink or will not parse, `init` does not write it. It prints the line to add and finishes the rest of the install. *Reason:* the link's target may be owned elsewhere, and rewriting a file that will not parse risks corrupting the owner's content.
- **[INFERRED]** `install-commands` does not read or write the setting. *Reason:* it installs only the assistant integrations (CLAUDE.md § Change Coordination).

### Docs

- **[INHERITED]** (epic Item 3 scope 6) README, model-validation guidance and CLI output state the profile version, the assessed scope, that the assessment is incomplete, and the boundary between L6 and the full `sysml-codegen check`. That check does not exist yet (Item 2), so the docs describe it as the future boundary and do not show a command to run (align record, owner boundary).

## Non-Goals

- Changing generator behavior, or writing anything in sysml-codegen or in Item 2 artifacts (align record, owner boundary 2026-10-18).
- Deciding String metadata policy. It belongs to Item 2; this item only flags String omissions the same way for both spellings.
- The PUSH-DOWN rows that wait on Item 2 (r3-proposal :66, :68, :69, :72, :73, :75: CHAIN-SEGMENTS, UNSUPPORTED-OPERATOR, REDEF-PRECEDENCE, AMBIG-INHERITED-ATTR, SUM-SHAPE, LITERAL-SHAPE).
- Rendering `docs/patterns/generator-subset.md` and the guidance fence harness (Item 5). Workflow gates and MODELING_PROCESS changes (Item 6).
- Changing the project-root marker rule. The `~/.claude` effect is pre-existing and shared with L2.
- Fixing the simple-name collision in `L6_CALC_DEF_NO_INSTANTIATION` (`level6_architecture.py:700-762`). The audit records it; a fix is a separate item.
- L4's executable coverage and other levels. Only the runner's crash handling outside L6 is touched.
- Editing dc3 or fusion-tea. Evidence uses `git archive` copies.

## Open Questions / Deferred to design

**Owner gates. These are recorded and not decided here.**

- **R3-1: relaxing an existing L6 error under unset or `generated`.** Known cases so far, from the audit table:
  - `L6_DESIGN_ATTR_UNEXTRACTABLE` on `attribute`-spelling Strings under `designs/`: today ERROR. The owner's omission policy plus the shared decision would make it WARNING.
  - `L6_CONSTRAINT_MALFORMED_NUMERICAL`: today ERROR. Replacing it with `constraint-predicate` refused would make it WARNING under unset.

  Until the owner decides, both legacy errors stay. The full audit may find more cases. **Conflict to surface:** while R3-1 is open, the "both String spellings agree" criterion holds for the contract's findings, but the legacy layer still errors on one spelling only.
- **R3-2: a project that passes today fails with the target unset.** Each source below fails some project by construction, so each needs the owner's decision before it is implemented under unset. The proposal for each follows the epic's inherited rule except where noted. The owner may accept it, or reject it so that unset keeps today's behavior.
  - an exception escaping a level now fails the run (`runner.py:128-137`); proposed ERROR;
  - `L6_CHECK_ERROR` at the 19 fake-clean sites and the two `AttributeError` sites; proposed ERROR;
  - an evaluator or fact-extraction crash; proposed ERROR;
  - the evaluator's unverified checks; proposed WARNING under unset, which departs from the epic's rule to avoid R3-2;
  - a malformed `pyproject.toml` or unknown value; proposed ERROR.

  **Conflict to surface:** the epic's inherited rule ("check failures are errors regardless of target") and the owner's R3-2 gate point in opposite directions for the same projects. Under `generated` and `native` the epic's rule applies without a gate. `evidence/r3-2-before-after.md` measures the effect on the three pinned consumer trees, but a clean result there does not take the place of the owner's decision.

**Mechanism and wording, for design**

- How the coverage limit is carried: a new field on `ScopeReport`, a versioned packaged list, or a pointer into the records.
- Exact wording of the verdict line, the unset note and the native INFO summary. Where the native details live: `--verbose`, the metrics, or a structured output.
- One issue per finding or per declaration (dc3 B8 shows 4 legacy diagnostics for 2 constraints). Deduplication between legacy checks and contract findings on the same site.
- How `pyproject.toml` is edited while keeping every other byte. `tomlkit` is not a dependency; a careful text insert is the alternative.
- `init`'s exit status when `pyproject.toml` will not parse or an option disagrees with an existing value.
- Whether `L6_CALC_DEF_NO_OUTPUT` is native correctness or generator-specific, and whether `V2` and `V4_UNSUPPORTED_OPERATOR` are pure ADR-002 rules or also generator rules.
- How the CLI names the override option and the interactive prompt text.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_executable-subset-contract.md` (Item 3; Design principles; Success Criteria, execution-target bullet; Items 1, 2, 5, 6 for boundaries)
- **Align record:** `.project/active/l6-subset-profile/briefs/align.md`
- **Required Reading:** none listed for Item 3 in the epic. Inputs used: Item 1 archive `.project/completed/20261018_exec-subset-profile/` (`design.md`, `audit.md` S2/S3, `product-lens.md` impl-F1/F2, `evidence/r3-proposal.md`, `evidence/acceptance.md`, `evidence/dc3-baseline.md`, `evidence/dc3-repaired.md`); Item 4 archive `.project/completed/20261018_positional-binding-check/` (`audit.md` finding 7); `.project/adr/0001-subset-profile-capability-ownership.md`; `.project/product/0001-executable-subset-contract.md`
- **Code read:** `src/agentic_mbse/validation/level6_architecture.py`, `adr002.py`, `runner.py`, `common.py`, `positional_check.py`, `positional_pins.py`; `src/agentic_mbse/project_root.py`; `src/agentic_mbse/research/holdout.py:205-270`; `src/agentic_mbse/cli/__init__.py` (`cmd_validate`, `cmd_init`, argparse); `src/agentic_mbse/sysml/subset_profile.py` (public API)
- **Product-lens:** `.project/active/l6-subset-profile/product-lens.md`
- **Design:** `.project/active/l6-subset-profile/design.md` (to be created)

Not checked: sysml-codegen (access denied, so the resolver citation is unconfirmed); whether dc3 and fusion-tea pass L6 today (that is what `evidence/r3-2-before-after.md` will measure); whether a conditional `if` reaches `V4_UNSUPPORTED_OPERATOR`; whether calc-owned asserts reach the constraint extractor. Nothing was executed; every count is from code reading or Item 1's recorded evidence.

---

**Next Steps:** `/_my_spec_review`, then `/_my_design`.

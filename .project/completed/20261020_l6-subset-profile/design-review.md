# Design Review: L6 integration and execution-target settings (EXEC-SUBSET-CONTRACT Item 3)

**Design:** `.project/active/l6-subset-profile/design.md` (at `3d8541db`)
**Spec:** `.project/active/l6-subset-profile/spec.md` (with `spec-review.md` Resolutions)
**Owner decisions and gates:** `.project/active/l6-subset-profile/briefs/align.md`
**Review File:** `.project/active/l6-subset-profile/design-review.md`
**Product-lens:** `.project/active/l6-subset-profile/product-lens.md` (design entry, 2026-10-18)
**Date:** 2026-10-18

---

## The Point

`agentic-mbse validate` should tell a modeler up front which model shapes the pinned code generator will refuse, using Item 1's contract (`sysml/subset_profile.py`), instead of the modeler finding out one generator run at a time. dc3 found its blockers over five generation runs; the contract reports 236 refused findings on that baseline in one pass.

Each project states in its committed `pyproject.toml` how it runs (`[tool.agentic-mbse] execution-target`). The target decides only how loud a finding is, never what is true:

- unset (default): generator findings are warnings, with a note naming the setting;
- `native`: generator-only findings fold into one INFO summary;
- `generated`: confirmed refusals are errors.

Two things must hold in everything a user reads. Nothing claims a model "will generate" (`clear` means only "no refusals found by the implemented rules", and L6 is not `sysml-codegen check`). And a broken check never passes, under any target. The owner's gate outcomes add: String omissions are warnings in both spellings, and `L6_CONSTRAINT_MALFORMED_NUMERICAL` stays exactly as it is.

Sources: `briefs/align.md` reading and owner decisions, `[AGENT] (ratified by owner, 2026-10-18)`; gate outcomes R3-1 and R3-2, `[AGENT] (delegated by owner, 2026-10-18)`; owner boundary (no Item 2, no sysml-codegen writes), owner statement; epic Item 3 scope 1-6, inherited.

## Fundamental Assessment

**Sound.** This is the right piece of work and the approach is right.

The core idea is simple and correct: the contract decides, a single table maps (category, target) to display, and check failures are ERROR in every column. That is the smallest design that satisfies "L6 owns severity, the contract owns decisions" (ADR 0001) and makes the severity behavior testable as one table. I checked every cell of the severity table against the owner decisions, the gate outcomes and the spec; all of them match (Dimension 1).

The product-lens found no owner or `[HARD]` contradiction and neither structural smell fired (gate OPEN). Its four DO findings are real but local; they are carried below as M1, M3, S1 and a traceability note.

Where the design is heavier than needed, it is in places the spec asked for (the JSON report, the audit, the per-site exception work), not invented scope. The new modules each earn their place: `project_settings.py` exists because two packages need one key set; `subset_presentation.py` keeps a large L6 file from growing further; `subset_coverage.py` keeps the coverage list off the profile digest.

What keeps this from Approve is a set of gaps where the design says *what* but not *how*, in places where the "how" decides whether a guarantee holds: the advisory hook into a shared fact function, `init`'s handling of a table that already has a defect, the report dropping warnings and pass notes, and the order in which the String suppression gets its input. None needs a redesign.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

**The severity table, every cell.** Checked against `align.md` § Owner decisions and § Gate outcomes, and `spec.md` § Severity by target.

- `REFUSED` W / E / summary: matches "generated makes confirmed refusals errors", "unset shows warnings", "native turns into an info summary".
- `UNCONFIRMED` W / W / summary, never ERROR: matches `spec.md:151` (P-0001 allows blocking only with a retained probe).
- `EXCLUDED`, `OMITTED` W / W / summary: matches the owner decision that exclusions and omissions are warnings under `generated`, and the R3-1 String outcome ("a warning in both forms and every folder").
- `UNVERIFIED` W / E / separate WARNING: matches the gate outcome (unset = warnings) and `spec.md:152` (ERROR under `generated`; own WARNING line under `native`).
- `UNASSESSED` W / W / summary when count > 0: matches `spec.md:153` and spec-review L1-2.
- `ADVISORY` W / W / summary: matches "at most WARNING, INFO under native".
- `ADMITTED` count only: fine.
- `LEGACY_OWN_APPLICABILITY`, `LEGACY_KEPT` base in all columns; `LEGACY_GENERATOR_ONLY` base / base / summary: matches R3-1 (no change under unset or `generated`) and `spec.md:170` (native lowering only with evidence).
- `CHECK_FAILURE`, `SETTING_INVALID` ERROR everywhere: matches the R3-2 outcome and epic scope 3.

**Legacy relaxation.** I looked for any change that lowers a result that errors today under unset or `generated`. I found none beyond the String gate outcome.

- `L6_CONSTRAINT_MALFORMED_NUMERICAL` stays ERROR under every target (Appendix A), as the gate outcome requires.
- Every exception-site change in Appendix B replaces a swallowed failure or a false ERROR with `L6_CHECK_ERROR`, which is also ERROR. For example, `:723` today produces false `L6_CALC_DEF_NO_INSTANTIATION` errors; afterwards it produces one `L6_CHECK_ERROR`. Pass/fail does not loosen.
- The propagated helpers (`_is_calc_usage`, `_is_part_usage`, `is_expose_binding`, `_is_invocation`) are all called inside per-element `try` blocks today (`adr002.py:153`, `:215`, `:236`, `:548`, `:585`; `level6_architecture.py:536`), and `traverse_expression` has no `except` of its own. So removing their catches reaches an element handler, not the whole check. The design's claim holds.
- The native column lowers nothing without an evidence row, and the design is stricter than the spec on two rows (`L6_DESIGN_ATTR_INCOMPLETE`, `L6_CONSTRAINT_NON_NUMERICAL` default to kept). That deviation is in the safe direction and is stated.

**"Shadowed by" correction (D9).** Verified against `completed/20261018_exec-subset-profile/evidence/dc3-baseline.json`. All 6 `unconfirmed` findings are `constraint-predicate` (4 `non_numerical_predicate`, 2 `blocked_predicate`), and each shares its `subject_id` with a `calc-owned-assertion/asserted_constraint` refused finding. No other subject in dc3 carries findings from two rules. The calc-owned-assertion rule does use the constraint itself as subject (`subset_profile.py:892-902`). So the spec's owner-based condition would match nothing, and D9's same-subject condition matches exactly the B8 case. The spec marked this `[INFERRED]` and invited design to correct it, so the design was right to. The spec's B8 criterion fixture still passes under D9.

**Gaps against the spec:**

- The JSON report omits `QualityCheckResult.warnings` (M3). The spec requires "every issue of every level that ran". L1 puts parser warnings there (`level1_syntax.py:80`), and L6 puts "No SysML files found" there (`level6_architecture.py:953`).
- D10's fallback ("if the contract did not flag it, the legacy error stays") conflicts with the String criterion, which says neither spelling raises `L6_DESIGN_ATTR_UNEXTRACTABLE` in any folder (S2).
- The unknown-key and underscore-table faults are classified in the spec (`spec.md:139`, `[INFERRED]`, under the R3-2 check-failure outcome), but the design does not cite that. The product-lens raised this as design-F3. It is a traceability gap, not an unclassified gate case (minor m1).

**Capture fidelity.** Provenance is carried correctly. The Point is `[AGENT] (ratified by owner)`, D9 corrects an `[INFERRED]` item with evidence rather than treating it as fixed, and Appendix A's categories are marked provisional. No owner referent was dropped.

### 2. Pattern Consistency
**Assessment:** Pass

- `project_settings.py` at package top level follows `project_root.py`'s stated reason (`project_root.py:1-8`).
- Option threading through `functools.partial` matches L2's pin options (`runner.py:94-100`).
- The final-line qualifier extends `pinned_note` (`common.py:166-176`, `runner.py:155-159`).
- Append-and-verify for owner TOML follows `register_codex_agents` (`installation.py:344-381`), and improves on it: whole-document equality, not just "parses".
- `ValidationCode` additions per outcome, with the reason in `reason_code`, follow the `types.py` precedent.

### 3. Abstraction Quality
**Assessment:** Concerns

- **D12's "hook" into `reconstruct_expression` is undefined (M1).** `reconstruct_expression` (`sysml/expression.py:298-356`) is public (`sysml/__init__.py:70`) and feeds `hierarchy.py:120` and the constraint and aggregation extraction the contract reads. "Hooks the last-resort branch" could mean editing that function (a side effect in a function the contract depends on, and possibly one sysml-codegen imports) or re-implementing its dispatch (the second classifier D12 rejects). The design must say which. Recommended: extract a pure predicate from the existing dispatch, such as `falls_to_text_fallback(node) -> bool`, used by both `reconstruct_expression` and the advisory, with a test that `reconstruct_expression`'s output is unchanged on the existing expression fixtures. Add `expression.py` to the Component Overview and to I4.
- **`display(category, target, base: Severity | None = None)`** mixes two kinds of input: `base` is required for the three legacy categories and ignored for the rest. A call with a legacy category and no base is a runtime error the types do not catch. Simpler: return a `KEEP_BASE` display for legacy rows and let the caller apply the base, or take `base` as a required argument for a separate `legacy_display()` (minor m2).
- **`TargetSettingError.fault: SettingsFault | Literal["invalid_value"]`** mixes an enum and a string literal. Add `INVALID_VALUE` to the enum, or give L6 its own small enum (minor m2).
- `CHECK_FAILURE` and `SETTING_INVALID` in the table are constant rows. They earn their place only as the anchor for invariant I2's test. That is fine; keep them.

### 4. Duplication Avoidance
**Assessment:** Pass

- L6 consumes the contract rather than re-deriving it: D10 keys on the String finding's subject, D9 is computed from findings alone, I3 limits severity inputs to outcomes and counts.
- The key set is defined once (D1). The holdout guard keeps only its value check.
- Remedy and semantic limits come from `RuleRecord`, not new text.
- One risk of future duplication: "shadowed by" lives only in L6 presentation. If Item 5's guidance needs it, it should move to an additive field on the contract result rather than be computed again (product-lens design-F5; minor m7).

### 5. Data Structure Clarity
**Assessment:** Concerns

- **The JSON report drops warnings and pass notes (M3).** The schema lists `issues`, `unstructured`, `summarized` and `profile`, but not `warnings`. And the run-level `overall_success: true` has no `pass_notes` field, so a CI job reading the report sees a bare pass on an unset run (product-lens design-F1). Add `warnings: [str]` per level and `pass_notes: [str]` at top level, and extend the I9 banned-wording scan to the report text.
- **`unstructured` as "issues minus `str()` of each structured issue, as a multiset"** is clever but fragile: it depends on `add_issue` (`common.py:42-52`) always appending `str(issue)`, and on no level appending the same string as a raw issue. It works with today's code. A sentence in the design saying so, and a test that `len(unstructured) + len(structured) == len(issues)` per level, would make it safe to keep (minor m3).
- `LEGACY_CATEGORY` is a static mapping, but the design says each native lowering is conditional on evidence. The design does not say how the mapping and the evidence file are kept in step (S3).
- The data model is otherwise explicit: typed enums, dataclasses, a defined report schema with a version string.

### 6. Route Safety
**Assessment:** Concerns

Routes here are CLI options and file-write paths.

- `--execution-target {generated,native}` and `--json-report PATH` are explicit, argparse-validated, and a bad value is exit 2. Good.
- **`init`'s insert algorithm has an unhandled branch (M2).** It handles "exactly one `[tool.agentic-mbse]` header" and "none", but not "two or more". Two matches happen when a multi-line string contains a header-shaped line and a real header also exists. The verification would likely catch a bad insert, but the algorithm should not depend on that: two or more matches must refuse.
- **`init` writes a key next to an existing defect (M2).** If the table already has `execution_target` (misspelled) or the file has a `[tool.agentic_mbse]` table, `init --execution-target=generated` would add the key, verification would pass (original plus one key), `init` would report success, and the next `validate` would fail with `L6_SETTING_INVALID`. `init` should call `read_toolkit_table` first, and on any `SettingsDefect` write nothing, print the defect, and exit 1 when the option was given.
- **Appending to a CRLF file** adds LF lines (`\n[tool.agentic-mbse]\n...`). The insert-after-header case uses that line's newline bytes; the append case should use the file's newline style too (minor m4).
- A UTF-8 BOM decodes to `﻿`; check that `tomllib` accepts it, or treat a BOM as a refused layout (minor m4).
- `os.replace` breaks a hardlink to `pyproject.toml`. That is rare; mention it with the symlink refusal or accept it explicitly (minor m4).
- **The settings-step target vs. L6's root.** `init` writes `<init target>/pyproject.toml`; L6 reads `find_project_root(models)/pyproject.toml`. They agree because `init` writes `.agentic-mbse/install.json`, a root marker, into the target. State that as the reason they agree (minor m5).
- **`TypeError` in `check_design_attr_completeness` (S1).** The legacy check catches `(ValueError, TypeError)` from `evaluate_true_static_expression` (`level6_architecture.py:540`) and reports `L6_DESIGN_ATTR_UNEXTRACTABLE`. The evaluator raises `TypeError` deliberately for "cannot evaluate this type" (`expression.py:497`, `:565`), but an evaluator bug or a SysIDE accessor failure would also arrive as `TypeError`. Under `native`, if the row is lowered, that inspection failure lands in the INFO summary, which epic scope 3 forbids. Narrow the catch to the evaluator's own signals (for example a dedicated `UnextractableValue` subclass raised at `:497`-`:565`, which is an additive library change) and route anything else to `L6_CHECK_ERROR` (product-lens design-F2, second half).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets are genuine claims with "if false" consequences. B1 and B2 are being checked by the parallel spike, which I did not duplicate. B3 is sound: whole-document equality is a strong check, and its failure mode is a needless refusal. Decisions name their rejected alternatives.

**Hidden bets:**

- **H1: the contract flags every attribute the legacy check flags as a String value (S2).** D10 suppresses the legacy error only for attributes that are subjects of a `string-value-omission` finding. If the contract does not evaluate some `designs/` attribute (outside the selected roots, or a fact kind not enumerated), the legacy ERROR stays for that String. The design treats that as the safe fallback, and it is safe. But it would break the spec criterion that neither spelling raises `L6_DESIGN_ATTR_UNEXTRACTABLE`, and the gate outcome's "every folder". Spike Q3 checks ID equality on dc3 `60b44d5`; it does not check coverage. State the bet, and add a test that a String attribute outside any generator root is still an `omitted` subject (or record which positions keep the legacy error and why).
- **H2: the contract runs before the legacy design-attribute check, or its result is passed in (S2).** The Architecture section runs legacy checks first, then the contract. D10 needs the contract's String subjects inside `check_design_attr_completeness`. Either reorder (contract first, pass the subject-ID set as a parameter) or apply the suppression as a post-filter in `subset_presentation.py`. The post-filter is simpler and keeps the legacy check unaware of the contract.
- **H3: the advisory can be detected without changing the fact layer (M1).** See Dimension 3.
- **H4: tests that force exceptions can run without a SysIDE licence.** The per-site tests (28 sites) are the evidence for the R3-2 "broken check never passes" promise. If they need a loaded model, they skip in an environment without `SYSIDE_LICENSE_KEY`, and the promise goes untested there. Most sites can be driven by monkeypatching `SysideAdapter.elements_of_type` to return fake elements. The design should say which tests need the licence (S4).

**Decisions.** D3 (setting error stops L6) is right and its rejected alternative is the spec's forbidden fallback. D7 (no `tomlkit`) is a reasonable call. D13 orders contract findings within tiers, but does not say how legacy and contract warnings interleave within the WARNING tier (minor m6).

### 8. Reader Comprehension
**Assessment:** Pass, with small concerns

The design gives a mental model first ("read the target, collect results, present them") and states the key idea plainly ("the contract decides what is true, and the target decides only how loud it is"). The severity table and the "what a user sees" list make the behavior concrete.

Small blockers for a cold reader:

- "impl-F2" (D13) is used without saying what it is. One clause fixes it: "incompleteness must not hide refusals".
- B1 refers to "spike S1" before S1 is defined in Next-Stage Handoff.
- Appendix A is dense, but it is reference material and is labelled provisional.

---

## Issues by Severity

### Critical (must fix before planning)

None.

### Major (must fix, small edits)

- **M1. D12's advisory "hook" is undefined and may change a shared fact function.** Say whether `sysml/expression.py` changes. Recommended: extract a pure predicate from `reconstruct_expression`'s existing dispatch, used by both it and the advisory, and add a test that `reconstruct_expression`'s output is unchanged. List `expression.py` in the Component Overview and under I4. Grep sysml-codegen at `b5663c07` for importers when access allows. (Dimension 3; product-lens design-F4)
- **M2. `init` gaps.** (a) Two or more header matches must refuse. (b) `init` must run `read_toolkit_table` first; on any defect (unknown key, underscore table, not a table) it writes nothing, prints the defect, and exits 1 when `--execution-target` was given. Add both to the refused-layout table and give each a test. (Dimension 6)
- **M3. JSON report drops warnings and pass notes.** Add per-level `warnings` and top-level `pass_notes` to `validate-report/v1`, and run the I9 banned-wording scan over the report too. (Dimensions 1, 5; product-lens design-F1)

### Should-fix

- **S1. `TypeError` catch at `level6_architecture.py:540`.** Narrow `L6_DESIGN_ATTR_UNEXTRACTABLE` to the evaluator's own "cannot extract" signals and route any other exception to `L6_CHECK_ERROR`, so an inspection failure cannot reach the native summary. (Dimension 6; product-lens design-F2)
- **S2. D10 data flow and coverage.** Say where the String suppression gets the contract's subjects (recommended: a post-filter in `subset_presentation.py`). State hidden bet H1 and add a test for a String attribute outside the generator roots, or record which positions keep the legacy error. (Dimension 7)
- **S3. Keep `LEGACY_CATEGORY` in step with the evidence.** Say that every generator-only candidate starts as `LEGACY_KEPT` and moves to `LEGACY_GENERATOR_ONLY` only in the change that adds its row to `legacy-l6-audit.md`. Add a test that compares the mapping's lowered set to the audit's "lowered under native" table. (Dimension 5)
- **S4. Licence-free test coverage for the exception sites.** Say which per-site tests need SysIDE, and drive as many as possible with fakes so the R3-2 promise is tested without a licence. (Dimension 7)

### Minor (consider)

- **m1.** Cite `spec.md:139` for unknown-key and underscore-table faults as configuration errors under the R3-2 outcome. (product-lens design-F3)
- **m2.** Tighten `display()`'s `base` argument and `TargetSettingError.fault` typing.
- **m3.** Document the `unstructured` multiset rule and test `len(unstructured) + len(structured) == len(issues)`.
- **m4.** `init` edge cases: CRLF newline style on append, BOM, hardlinks under `os.replace`.
- **m5.** State why `init`'s target and L6's resolved root agree (the install manifest is a root marker).
- **m6.** Say how legacy and contract warnings are ordered within the WARNING tier (D13); define impl-F2 in D13 and S1 before B1 uses it.
- **m7.** Note that "shadowed by" moves to an additive contract field if a second consumer needs it; say whether the report's `shadowed_by` applies to every outcome or only `unconfirmed`. (product-lens design-F5)
- **m8 (consider; would change the spec).** The product-lens suggests requiring a native-route result for every native lowering, not only a generator-only cause (design-F2, first half). `spec.md:170` (`[INFERRED]`) accepts either. Raising the bar would likely leave most rows unlowered, which conflicts with epic scope 4 ("native must not leave contradictory generator-only errors"). I would keep the spec's rule and let the audit's lowered-rows table carry the risk visibly.
- **m9 (consider; spec-required).** `init` with no `pyproject.toml` creates a file holding only `[tool.agentic-mbse]`. uv treats a `pyproject.toml` without `[project]` differently from no file at all. Not checked in this review; worth one line in the plan's `init` phase.

---

## Recommendations

1. Fix M1 first: decide the advisory detection mechanism so nothing the contract reads changes. This is the only finding that touches the surface the Item 2 agent consumes.
2. Fix M2 and M3. Both are a few lines in the design: two more refused-layout rows for `init`, and two more fields in the report schema.
3. Apply S1-S4 in the design or carry them as explicit plan tasks. S2 and S3 change what the plan's tests must assert.
4. Fold the minor items into the plan where they are cheap.

No owner question is needed. Every finding is a design-level gap the design agent can close; none reopens an owner decision or a gate outcome.

Not checked in this review: sysml-codegen (no access; the spike's Q5 covers citations); dc3 and fusion-tea trees and consumer runs (the spike covers them); whether `tomllib` accepts a BOM; uv's behavior with a `[project]`-less `pyproject.toml`. Nothing was run except `jq` over Item 1's dc3 JSON and `grep`/`sed` reads of source.

---

## Resolutions

Recorded 2026-10-18 in the design revision. The calls are the orchestrator's, made with the spike in hand (`spikes/findings.md`, `spikes/f4-codegen-citations.md`): [AGENT] (orchestrator call, 2026-10-18). The owner has not engaged with this review.

**Major**

- **M1 — accepted.** D12a: a pure predicate `falls_to_text_fallback(node)` is extracted from `reconstruct_expression`'s dispatch in `expression.py`. Both `reconstruct_expression` and the advisory's `text_fallback_nodes` call it. A test over every value expression in the existing fixtures shows `reconstruct_expression`'s output is unchanged (Implementation Notes, "The reconstruction predicate"). I4 lists it as additive.
- **M2 — accepted.** `init` runs `read_toolkit_table` first and refuses on any existing defect: it writes nothing, and exits 1 when the option was given (`init` table, new row). Two or more `[tool.agentic-mbse]` header matches is a refused layout. I7 now says `init` never writes when the table has a defect.
- **M3 — accepted.** The report schema has per-level `warnings` and top-level `pass_notes`. I9's banned-wording scan covers the JSON report as well as stdout.

**Should-fix**

- **S1 — accepted.** D16: `expression.py` gains `Unextractable` with `UnextractableValueError` and `UnextractableTypeError`, subclasses of today's types so existing callers are unaffected. The legacy check catches only `Unextractable`; anything else is `L6_CHECK_ERROR` (Appendix B, `:540`).
- **S2 — accepted.** D10: the contract runs before the legacy checks and passes its `string-value-omission` subject ids into `check_design_attr_completeness`. Coverage assumption B6 is stated with the spike's evidence: no tree has a String the legacy check flags and the contract misses. If the contract misses one, that String keeps its legacy ERROR. If the contract fails, every legacy error stays.
- **S3 — accepted.** Every generator-only candidate starts as `LEGACY_KEPT`. A row moves only in the change that adds it to `evidence/legacy-l6-audit.md` and `tests/fixtures/l6/native_lowered.toml`, and a test requires the mapping to equal that fixture.
- **S4 — accepted, with a premise difference surfaced.** The orchestrator asked for "the existing licence-gated marker pattern". None exists: `pyproject.toml` registers only `corpus` and `slow`, and model-loading tests read `SYSIDE_LICENSE_KEY` from `.env` (`tests/conftest.py`) and fail without it rather than skip. The design follows that real practice. Most exception-site tests use fakes or monkeypatching and need no licence. Tests that need a parsed model carry a new label-only `syside` marker that never skips, and the evidence lists them with `pytest -m syside --collect-only`. If a skip-when-no-licence marker is wanted instead, that is a separate call.

**Minor** (all accepted)

- m1: D3 cites `spec.md:139`. m2: `Display.BASE` replaces the `base` argument, and `TargetFault.INVALID_VALUE` is an enum member. m3: the `unstructured` multiset rule and its length test are in the schema note. m4: CRLF handling on append, BOM refusal and the hard-link refusal are in the insert algorithm and refused layouts. m5: the `init` section states that the install manifest makes the `init` target a root, so `init` and L6 read the same file. m6: D13 orders within each tier and defines impl-F2. m7: D9's `shadowed_by` covers every finding not refused by that rule and is null otherwise. m8: the spec's evidence rule is kept (Validation Approach). m9: the plan's `init` phase checks that a `[project]`-less `pyproject.toml` does not disturb `uv`.

**Spike questions**

- **Q1 — walker exceptions.** D15: a walker's own `SemanticEvidenceError` is `L6_SUBSET_ADVISORY_UNVERIFIED`, a WARNING under every target that names the shape. Any other exception stays `L6_CHECK_ERROR`. I1 names this as its one exception. The spike's `sum(cells.?{...}.mass)` and `Cell.metadata` shapes are fixtures. The wrapper advisory is filtered to `KNOWN_WRAPPER_FUNCTIONS`.
- **Q2 — rows the spike did not confirm.** `L6_INVALID_QUALIFIED_NAME`, `L6_INVALID_BINDING_FORMAT` and `L6_ATTR_REDEF_EXPR_DROPPED` keep today's severity under every target, `native` included. Appendix A is rewritten from the citation results. Only four rows lower under `native` (three ERROR→INFO, one WARNING→INFO). Follow-up: backlog `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES`.
- **Q3 — extraction cost.** D14: one model load and one constraint extraction per `validate` run, shared by L4, L6's legacy checks and the contract through a run-scoped session. No new extraction pass. B5 and I10 require each level's results to stay identical, tested with and without the session. Appendix C step 10 fails the criterion if fusion-tea's `validate --complete` is more than 10% slower. Step 11 lists the new String warnings (131 on fusion-tea, 30 on dc3 `60b44d5`) as expected. The slow loop itself is backlog `CONSTRAINT-EXTRACTION-INHERITED-SCAN`.
- **Q4 — roots and settings.** Each tree resolves its own root and none has a `[tool.agentic-mbse]` table at its pin, so all three run as unset. No design change.

---

**Overall:** Revise

**Next Steps:** Return to the design agent with this review. It should resolve M1-M3 in `design.md` and either apply S1-S4 or carry them as plan tasks, then record the dispositions. The minor items can go straight to `/_my_plan`. The reviewer does not edit the design. A re-review is not needed if M1-M3 are fixed as described; record the verification instead.

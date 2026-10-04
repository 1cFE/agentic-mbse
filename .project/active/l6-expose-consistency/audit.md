# Audit: L6 EXPOSE Validation Consistency

**Verdict:** Certify
**Audited:** 2026-10-04
**Branch:** harness-right-size
**Commit:** 3f442ce (implementation); audited at HEAD fd27c4f, which adds only the audit brief

---

## The Point

[INHERITED: spec, from the 2026-10-04 status report] Level 6 contradicted itself on the documented EXPOSE pattern. A design attribute bound directly to a calculation output (`attribute x : Real = my_calc.output_val;`) passed the static-expression check (V2). The same attribute failed the supported-operator check (V4) with `V4_UNSUPPORTED_OPERATOR` for `.`, and failed the design-attribute completeness check with `L6_DESIGN_ATTR_UNEXTRACTABLE`. Level 6 is the codegen-readiness gate, so a modeler who followed the docs was told their supported dataflow was broken.

[INHERITED: spec, design] The repair is consistency, not new support. V4 and completeness now ask the one existing EXPOSE predicate first. Every non-EXPOSE expression keeps exactly the diagnostics it had. Arithmetic over a calc output stays rejected. There are no codegen or modeling-workflow changes.

[AGENT] (ratified by orchestrator 2026-10-04, design D6) The existing predicate is wider than the calc-output example. It accepts any design attribute whose whole value is one feature chain headed by a sibling calc usage or sibling part usage, of any length. So Level 6 now also passes part-headed relays such as `x = sibling_part.attr`.

## Summary

The implementation does what the design says, in the places the design says, and nothing more. I re-ran the fixtures against both the pre-fix and post-fix source:

- **The false positives are gone.** `shapes/` went from 6 issues to 0, and the referent's `exposed_output` went from 2 issues to 0.
- **Every non-EXPOSE diagnostic is unchanged.** `controls/` returns the identical 13 (code, element) pairs before and after.
- **The gate shows no growth.** Lint, format, and type counts are at or below baseline, and the four touched Python files are ruff-clean.

The one thing that needs attention is not in the code. The D6 boundary decision was made by the orchestrator, not the owner. This commit is the one that makes that decision visible to users.

## Product Judgment

**This is the right piece of work.** The completeness check's own docstring already promised "values or EXPOSE bindings" (`level6_architecture.py:481`), and V2 already accepted them. The fix makes the code keep a promise it already stated, through the existing predicate and two small guards. Both documented EXPOSE shapes (on a part definition, on a part usage) now pass the full Level 6 route.

**Product lens (this audit's run): gate CLEAR.** It has no owner-grade or `[HARD]` finding, so nothing controls the verdict. The full block is appended to [product-lens.md](product-lens.md). Its findings, checked against the code:

- **Still true: Level 6 now passes dotted paths that the shipped modeling guide calls violations.** (Lens DON'T, `[INHERITED]` grade.)
  - `project_templates/MODELING_GUIDE.md.template:57`, `docs/patterns/adr002-calculations.md:44`, and `docs/patterns/common-mistakes.md:166` list `= a.b.c` as a violation. `docs/patterns/plant-idiom.md:347` says multi-hop EXPOSE is supported.
  - Before this commit, the overall Level 6 result on `p = subsystem.rotor.power` was "fail", even though only V2 passed it. After this commit, Level 6 passes it with no diagnostic.
  - This is D6 working as recorded. I am not re-litigating it. But the design review said this call belongs to the owner (`design-review.md:72`). That review's Resolutions section still reads "Pending" (`design-review.md:290`), and the ruling lives in `briefs/design_revision.md` as an orchestrator decision. See Advisory 1.
- **Still true: the boundary also admits chains that reach through a sibling part into its internal calc**, for example `x = sub.inner_calc.out`. `docs/patterns/expose-pattern.md:28` says consumers should bind to the exposed attribute, not `part.calc.output`. That doc line is about calc-input bindings, so it applies here only by analogy. It is part of the same D6 decision.
- **Still true: the docs follow-up exists only inside this item's folder.** It is not in `.project/backlog/` or `CURRENT_WORK.md` (lens CAN'T-FIND). See Advisory 3.
- **Not verifiable here: the codegen evidence behind B1 and B2.** It lives in the sysml-codegen repo, which this session cannot read. See Advisory 2.

**Structural smells.** The lens reports four as firing. None changes the verdict:

- **"A test passes only under one interpretation"**: fires, deliberately. `shapes/` and its `relayed` case (`test_l6_expose_consistency.py:151`) pin D6's reading of docs that disagree with each other. Pinning the decision is what the design review asked for. This is a recorded choice that can be reversed in one place, not an accidental green.
- **"A special category exempts a case whose meaning is unchanged"**: weak. The sibling rule accepts `subsystem.rotor.power` but rejects `producer.producer_calc.scaled` from an unrelated part. The difference is ownership: the first reads a part you own, the second reads a stranger's part. That is a real modeling distinction, but no doc states it. It belongs to the docs follow-up.
- **"Correctness depends on an internal representation"**: fires, but it is old behavior. The predicate tests a SysIDE runtime class name and owner object identity. Those lines predate this item, and design D4 kept the body unchanged on purpose. This commit gives them two more callers. See Advisory 4.
- **"A baseline preserves behavior that contradicts the product"**: fires for an adjacent shape outside this item. Completeness still rejects the inline FORMULA `area = length * width`, which the guide calls OK and V2 accepts. That is a recorded design Non-Goal, pinned by `tests/test_l8_extractability.py:58`.

## Blockers

None.

## Advisory

1. **Put the D6 boundary decision in front of the owner before the PR.**
   - **Concern.** The design review escalated C1 ("is a chain headed by a sibling part EXPOSE?") as an owner call. The orchestrator ratified option (a), keep the boundary, at `[AGENT]` grade. The decision is recorded honestly in design D6, but the owner has not seen it.
   - **Impact if unaddressed.** After this merges, Level 6 in every target repo will pass model shapes that the tool-owned `MODELING_GUIDE.md` installed into those same repos calls violations. A modeler gets opposite answers from the guide and the gate. Before this commit the two agreed on the verdict, if not the reason.
   - **What should change.** Have the owner confirm or reverse D6 before `/_my_pre_pr`. If confirmed, record it under `design-review.md` Resolutions, which still reads "Pending". If reversed, narrow `is_expose_binding` (`adr002.py:339`). That is the one place the boundary lives, and the change would also alter V2.

2. **Multi-hop chains are accepted but not tested, and an in-repo doc says codegen does not handle them.**
   - **Concern.** D6 includes multi-hop sibling chains. The tests pin only a two-segment part-headed relay (`relayed`, `test_l6_expose_consistency.py:151`). `docs/patterns/plant-idiom.md:406-413` says a multi-hop cross-part chain "truncates", and that codegen Item 5 turned the worst case into a loud reject (D3-2). B2 says codegen's conformance tests prove multi-hop chains reach their producer. That evidence is in another repo, and this audit could not re-read it.
   - **Impact if unaddressed.** If the plant-idiom passage applies to design-attribute chains, Level 6 passes a model that codegen then rejects. The failure would be loud in codegen, not a silent mis-wire, so the harm is bounded.
   - **What should change.** When the docs follow-up runs, settle the multi-hop question against codegen. Then pin the answer with a three-segment case in `shapes/` (accepted) or `controls/` (rejected).

3. **Carry the follow-ups into the backlog at close.**
   - **Concern.** The design's Non-Goals list five follow-ups: docs reconciliation (R1), the calc-usage `in attribute x = source.result;` V4 `.` error, per-check scope selection, FORMULA completeness, and the dead helpers `_get_calc_usage_names` (`adr002.py:260`) and `_is_calc_output_reference` (`adr002.py:292`, still imported by `tests/test_validation/test_v2_false_positive.py`). None has a backlog entry.
   - **Impact if unaddressed.** They are lost when the item is archived. The docs reconciliation matters most, because the guide and the gate now disagree (Advisory 1).
   - **What should change.** `/_my_close` should file them in `.project/backlog/BACKLOG.md`. This audit did not touch that file.

4. **The predicate decides by runtime class name, against the module's own stated rule.**
   - **Concern.** `is_expose_binding` checks `"FeatureChain" in type(expr).__name__` (`adr002.py:366-367`). In the same module, `_is_calc_output_reference` says "runtime Python class names have no classification force" (`adr002.py:300-302`). The line predates this item, and D4 kept the body unchanged on purpose. It now feeds three checks instead of one.
   - **Impact if unaddressed.** If SysIDE renames the class, every EXPOSE binding fails the predicate, and all three checks bring back the false positives. That failure is visible (B3's failure mode), not silent.
   - **What should change.** In a later cleanup, use the adapter's metatype test instead of the class name. It is out of scope here.

## Findings Detail

### Plan completion

All four phases verified. Each plan claim below was re-checked against the commit or by re-running it.

- **Phase 1.** The four fixture files match design Appendix A byte for byte (script comparison). The test module exists with the stencil's assertions. The recorded red output ("1 passed, 3 failed") is consistent with my pre-fix run: controls 13 pairs, shapes 6 issues, referent 2 issues on `exposed_output`.
- **Phase 2.** The rename, the parameter drop, and the deletion of `_build_calc_output_catalog` all landed (`adr002.py:339`). `grep` finds `_is_expose_pattern` and `_build_calc_output_catalog` nowhere outside `.project/` history files. The two `test_adr002.py` tests are renamed.
- **Phase 3.** Both guards are in place (`adr002.py:153`, `level6_architecture.py:536`). The new module has 10 tests and all pass.
- **Phase 4.** The gate numbers in the plan's table match my run exactly (see Certification). The plan's claim that no `ruff format --diff` hunk touches a changed line holds:
  - The two source files' hunks are all on pre-existing lines.
  - `test_adr002.py`'s top hunk (a missing blank line after the module docstring) is identical at the parent commit.
- **Recorded deviations.** All five are honest and doc-only: the predicate body comment, the completeness docstring clause, the two V2 doc lines, the I001 blank line, and the plan's 2/2-vs-1/3 arithmetic slip. I found no undocumented deviation.
- **Placeholders and TODOs.** None in code. The added lines contain no TODO, FIXME, placeholder, or `NotImplemented`. Trivial: `plan.md:291` still carries the template line "[To be filled during implementation.]" above the filled notes.

### Spec conformance

- **SC1 (retained referent, individual checks and combined route): met.**
  - `test_referent_individual_checks` (`test_l6_expose_consistency.py:75-82`) runs V2, V4, and completeness (`design_path_filter=None`) on the original fixture.
  - `test_referent_combined_route` (`:85-92`) copies the referent into a temporary `designs/` + `library/` layout and runs `validate_architecture` with the default filter.
  - Both assert, by exact equality, that no issue names `exposed_output`, and that `combined` gets exactly `{V2: 1, V4: 2, UNX: 1}` (`:63-66`). That is stronger than the design's "still gets V2, V4, and unextractable". The positive `combined` assertion also proves the checks actually ran on the file. A path that silently skipped the file would fail it.
- **SC2 (both EXPOSE shapes accepted; arithmetic over a calc output rejected): met.**
  - `test_shapes_pass_combined_route` (`:102-106`) asserts `result.issues == []`, `success is True`, and "Design attrs checked" `== 3`, exactly as the Validation Approach states.
  - `derated` keeps V2, V4, and unextractable in the controls Counter (`:52`).
- **SC3 (controls keep their diagnostics; no dotted reference admitted for containing `.`): met.**
  - `test_controls_keep_every_diagnostic` (`:115-127`) compares a `Counter` over every structured issue to the 13 Appendix B pairs, with no code filter.
  - It also asserts `len(result.issues) == 13`, "Design attrs checked" `== 6`, and exactly one V4 issue on `powered` whose message names `'^'`.
  - `test_is_expose_binding_boundary` (`:146-159`) returns `True` for `module_result`, `exposed_output`, and `relayed`, and `False` for `remote`, `payload_mass`, and `derated`.
  - None of these assertions uses a weaker "contains" or `>=` form, except the `'^'` message check, which is the form the design specified.
- **Known Requirement [INHERITED], existing classification is the boundary: met.** The predicate's logic is unchanged. The diff touches only its signature, docstring, and one comment.
- **Known Requirement [INFERRED], a supported EXPOSE attribute needs no numeric default: met.** The completeness guard returns early before the numeric evaluator (`level6_architecture.py:536-537`).
- **Non-Goals respected.** No new expression support. No codegen, workflow, or doc changes. `src/agentic_mbse/sysml/` is untouched.

### Design conformance

Implementation follows design.

- **D1.** No enum and no shared classifier. Each check gained one predicate call, and V2's decision order is unchanged (`adr002.py:577-598`).
- **D2.** The V4 guard sits after the calc-def-owner, `library/`, and has-expression skips, and before `extract_operators` (`adr002.py:150-157`). The docstring line was added at `:100`.
- **D3.** The completeness guard sits inside `if has_value:` and before the evaluator (`level6_architecture.py:532-539`).
- **D4.** The signature is `is_expose_binding(attr: Any, expr: Any) -> bool` (`adr002.py:339`). `calc_outputs` and its catalog builder are gone.
  - The docstring (`:340-361`) states Invariant 3 exactly: a top-level feature chain, a head that resolves to a `CalculationUsage` or `PartUsage`, the same owner, chain length and final target not checked, never raises. It names its three consumers.
  - The "single attribute/output target" and "transitive EXPOSE" claims are gone. Nit: the intro sentence says the binding aliases a value "on a sibling". For a multi-hop chain, the value is reached through a sibling, not held on it. The numbered criteria are exact.
- **D5.** Two standalone fixture directories, plus the referent copied into a checked layout. The Counter covers every structured issue, with the total checked via `result.issues`.
- **D6.** The predicate body is unchanged, so part-headed and multi-hop sibling chains stay accepted. `relayed` pins the part-headed case. The multi-hop case is not pinned (Advisory 2).
- **Invariant 1 (one predicate): holds.** `is_expose_binding` has exactly three call sites (`adr002.py:153`, `:585`, `level6_architecture.py:536`). The added lines contain no `"."` string test and no new chain-type test. The only `'.'` hits are in comments. `_contains_feature_chain` is untouched.
- **Invariant 2 (fail closed): holds.** The whole body is inside `try ... except Exception: return False` (`adr002.py:362-425`).
- **Invariant 3 (unchanged boundary): holds.** The body diff is one comment line.
- **Invariant 4 (non-EXPOSE behavior unchanged): holds.** It was proven by the controls test, and independently by my pre-fix/post-fix run: identical 13 pairs, and an identical `combined` result on the referent.
- **Invariant 5 (shared utilities untouched): holds.** `git diff 3f442ce~1 3f442ce -- src/agentic_mbse/sysml/` is empty. That covers `extract_operators` (`expression.py:98`), `STATIC_OPERATORS` (`expression.py:213`), and `evaluate_true_static_expression` (`expression.py:466`). `SUPPORTED_OPERATORS` (`adr002.py:39`) is outside every diff hunk.
- **Invariant 6 (metric still counts): holds.** `attrs_checked += 1` (`level6_architecture.py:523`) runs before the guard. Shapes count 3 before and after.
- **Invariant 7 (FORMULA unchanged): holds.** `tests/test_l8_extractability.py` is unchanged in the commit and passes.
- **Appendix C must-fix items: all landed.**
  - C1: `relayed` is in `shapes/`.
  - M1: the docstring is rewritten.
  - m1: the controls assertion uses a Counter plus `len(result.issues)`.
  - m8: the tests are renamed, the `'^'` assertion is present, and the dead helpers are left alone.
  - m2–m7 are design-text edits and are present in `design.md`.
- **Work the design did not describe.** These are the five doc-only deviations listed under Plan completion. Each tightens a docstring or comment that would otherwise contradict the new boundary. No logic outside the two guards and the rename changed.

### Code integrity

No issues found in the new code.

- **Guards.** Both are one-line early `continue`s with a comment in the module's existing `D# (ITEM)` style. They add no new parameters, modes, or fallbacks.
- **Broad except.** The predicate's `except Exception: return False` is old code and is the design's required fail-closed behavior (Invariant 2). It fails toward the check's normal diagnostic, which is visible, not toward a silent pass.
- **Smells.** The runtime-class-name and object-identity tests are old code (Advisory 4).
- **Dead code.** The commit removed dead code (`_build_calc_output_catalog`) and introduced none. The two remaining dead helpers are a recorded Non-Goal.
- **Test module.** It caches loaded models in a module-level dict (`test_l6_expose_consistency.py:134`). That is harmless at two fixtures.

---

## Certification

**Checked:**

- Every spec success criterion against its committed test, read line by line against the design's Validation Approach.
- All seven invariants and D1–D6 against the code.
- Every Appendix C must-fix item.
- Every plan checkbox and implementation note against the commit.
- The fixtures against Appendix A, byte for byte.
- An independent before/after run of `shapes/`, `controls/`, and the referent through `validate_architecture`, using a scratch copy of the parent commit's `src/` under the gitignored `build/`. The scratch copy has been deleted.
- The product lens (fallback procedure, see `product-lens.md`).

**Gate (run by this audit, 2026-10-04):**

| Check | Baseline | Now |
|---|---|---|
| `uv run pytest tests/ -q` | 1922 passed, 1 skipped, 33 deselected | 1932 passed, 1 skipped, 33 deselected, 0 failed (10 new tests) |
| `uv run ruff check src/ tests/` | 119 errors | 118 errors |
| `uv run ruff format --check src/ tests/` | 78 would reformat | 78 would reformat, 77 formatted |
| `uv run mypy src/` | 91 errors in 19 files | 91 errors in 19 files |
| mypy in `adr002.py` / `level6_architecture.py` | 3, at `adr002.py:31` | the same 3 |
| `ruff check` on the touched Python files | 1 (I001 in `test_adr002.py`) | All checks passed |
| `ruff format --check` on the new test file | n/a | already formatted |

The brief says "five touched/new Python files". The commit changes four Python files: `adr002.py`, `level6_architecture.py`, `test_adr002.py`, and `test_l6_expose_consistency.py`. The rest of the commit is the fixture tree, which has no Python.

**Marked:**

- `spec.md`: SC1, SC2, and SC3 → `[x]`; Status → certified.
- `plan.md`: every phase checkbox was already `[x]` and is verified; Status → certified.
- `product-lens.md`: audit block appended.
- Per the brief, `CURRENT_WORK.md`, `BACKLOG.md`, and `active/README.md` were not touched.

**Not checked:**

- **The codegen evidence for B1 and B2.** This covers `sysml-codegen/docs/architecture/reference/16-computed-attributes.md` and `tests/conformance/test_elaboration_expose_shapes.py`. That repo is outside this session's permissions. Whether codegen really wires multi-hop and part-headed design-attribute chains rests on the orchestrator's 2026-10-04 verification (Advisory 2).
- **The slow corpus tests** (`-m slow`, 33 deselected). They were not run.
- **The B4 / R4 library part-definition alias-target edge case.** It is recorded in the design and has no test. It was not probed.
- **Behavior on real target-repo models** beyond the committed fixtures.
- **The product-lens instructions file.** `~/.claude/scripts/product-lens.md` was permission-denied, so the lens ran the fallback procedure already used in this item's ledger.

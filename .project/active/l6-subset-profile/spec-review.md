# Spec Review: L6 integration and execution-target settings (EXEC-SUBSET-CONTRACT Item 3)

**Spec:** `.project/active/l6-subset-profile/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/l6-subset-profile/spec-review.md`
**Date:** 2026-10-18

Method: read the spec, the epic (Item 3, principles, success criteria, open decisions, Items 1, 2, 5 and 6 for boundaries), `briefs/align.md`, `briefs/spec.md`, `product-lens.md`, ADR 0001, Item 1's `acceptance.md`, `dc3-baseline.md`, `dc3-repaired.md` and `r3-proposal.md`, and `docs/research-seam.md`. Checked the code-facing claims by reading `level6_architecture.py`, `adr002.py`, `runner.py`, `common.py`, `cli/__init__.py` (`cmd_validate`, `cmd_init`), `project_root.py`, `positional_pins.py`, `positional_check.py`, `research/holdout.py`, `subset_profile.py` and `subset_profile_rules.toml`, and dc3's and fusion-tea's working-tree `pyproject.toml`. Nothing was run. sysml-codegen was not read. R3-1 and R3-2 are not decided here.

Each finding is marked **must-fix** (the spec is wrong or a criterion cannot be met as written) or **should-fix** (the spec is ambiguous enough that design could go two ways, or a gap would surface late).

---

## Reality Check

**Sound.** The spec is about the right work item and its Problem section is accurate. These claims check out against the code:

- The holdout guard rejects every key in `[tool.agentic-mbse]` except `research` (`research/holdout.py:241-260`).
- There are 26 `except Exception` sites, 17 in `level6_architecture.py` and 9 in `adr002.py`, at the lines the spec lists.
- A level that raises is never recorded, so the run passes. With `--level=6` alone it prints "Checks run: 0" and "All quality checks passed!" (`runner.py:128-137`, `common.py:66`).
- `UNASSESSED` produces no legacy issue (`level6_architecture.py:674`).
- The dc3 counts (236 / 32 / 6 / 50, `refused_incomplete`; repaired: `clear`, 30 omitted) match Item 1's evidence.
- R3-1 and R3-2 are recorded and left open. The Item 2 boundary holds.

The defects are specific. One R3-1 case is understated. One claim about `UNASSESSED` is false. A class of exception sites that can hide failures under `native` has no requirement. The `[tool.agentic-mbse]` closed key set has no criterion. And the output pagination makes the dc3 evidence criterion impossible to meet as written.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (must-fix):** The R3-1 case for `L6_CONSTRAINT_MALFORMED_NUMERICAL` is understated. The spec says that replacing it with `constraint-predicate` "would make unset a WARNING" (audit table row; Open Questions R3-1, second bullet). The relaxation is wider than that, and it also happens under `generated`. The packaged records give `blocked_predicate` an outcome of `refused` only for `owner_instantiated` and `owner_package`. For `owner_uninstantiated` the outcome is **`admitted`**, so there is no finding at all. For any other owner context there is no record, so the finding is `unconfirmed`, which the spec makes WARNING under `generated` and never ERROR (`subset_profile_rules.toml:230-256`). The legacy check errors in every one of these contexts (`level6_architecture.py:654-668`). dc3 baseline B8 is exactly this case: 2 constraints that the legacy check marks as ERROR today become `unconfirmed` WARNINGs under `generated` (`acceptance.md:31`). The R3-1 entry needs to name all three effects so the owner decides the right question:
- under unset, refused becomes WARNING;
- under `generated`, an unconfirmed context becomes WARNING;
- under every target, an uninstantiated owner gives no finding at all.

**L1-2 · Direct claim (must-fix):** The audit table says "`UNASSESSED` becomes visible as unverified". The contract does not do that. `UNASSESSED` constraints only increase `counts.unassessed_constraints` (`subset_profile.py:1276-1282`, `:1360`). They produce no `UnverifiedCheck` and do not affect the verdict (`_verdict`, `:1261-1273`). So a model with unassessed constraints can be `CLEAR`. To make the table's claim true, L6 would have to turn a count into a check failure itself, which conflicts with the spec's own `[INHERITED]` rule that L6 does not re-derive a decision the contract holds. Or the contract would have to change, which conflicts with the frozen-version rule. The spec needs a requirement that states how `unassessed_constraints` is shown and at what severity under each target, using the count the contract already gives. Today that severity is set nowhere, so a `CLEAR` with unassessed constraints would print as clean.

**L1-3 · Direct claim (should-fix):** "`V4_STATIC_FUNCTION_INVOCATION` … Duplicate of `invocation-callable`" is stated as fact, but the two checks do different things:
- V4 warns on **any** function call in a static design attribute, because the result cannot be pulled out as a static default (`adr002.py:183-257`).
- `invocation-callable` fires only on callables **outside the allowlist** (`subset_profile.py:921-934`).

If the design attribute calls an allowlisted function, V4 warns today and the contract reports nothing. That is not an R3-1 case, because it is a warning. But it is a lost diagnostic, which the table hides by calling the two checks duplicates. The table should say this is a hypothesis for the audit to confirm with a boundary fixture: an allowlisted call in a design attribute.

**L1-4 · Direct claim (should-fix):** Two stale-citation details:
- The dead citation is at `common.py:82`, not `:84`.
- The audit names only one codegen citation to confirm (`level6_architecture.py:847`). `adr002.py:478` also cites a codegen module (`computed_attribute_extractor.py`), and it is just as unconfirmed.

Epic scope 5 says "the stale resolver citation", so `:847` is the required one. But the "read at `b5663c07`" check should list every codegen citation in the two files, so design does not confirm one and leave the other.

**L1-5 · Rewrite request (should-fix, provenance):** The check-failure bullet is tagged `[INHERITED] (epic, "27 broad exception sites")`, but most of its content is the agent's own inventory: the 19 fake-clean sites, the 7 others and their sub-classes. The bullet should be split. The obligation stays `[INHERITED]`. The classification of each site becomes `[INFERRED]`, so design can challenge it. The second sentence of the R3-1 bullet ("Lowering … under `native` is not an R3-1 case") is a fair reading of the align record, but it is the spec's reading, so tag it `[INFERRED]`. It matters because of L2-1.

**What holds:** the five owner decisions are correctly regraded to `[INFERRED] [AGENT] (ratified …)` (product-lens spec-F4). Nothing is marked settled that is not owner-grade. The `[HARD]` holdout claim is true. The inherited items cite their sources.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff (should-fix):** Under `native`, the only thing that decides whether a legacy ERROR becomes INFO is the audit's classification of the check as "generator-specific" or "native correctness". The spec reads R3-1 as not covering `native` (L1-5). So a misclassification relaxes a native project's errors with no gate at all. The spec defines neither "native correctness" nor the evidence a row needs. It flags only `L6_CALC_DEF_NO_OUTPUT` for design to confirm. Several rows are just as open:
- `L6_DESIGN_ATTR_INCOMPLETE`: a design attribute with no value. Does the native route fail on that too?
- `L6_CONSTRAINT_MALFORMED_NUMERICAL`: its `native` severity is missing from the table altogether.

**If** the owner is content for the agent to classify, the spec should require each row of `legacy-l6-audit.md` to state its evidence (what happens on the native route), and should list every ERROR→INFO change under `native` in one place so the owner can see them. **If** the owner wants to approve native relaxations, that is a third gate. My recommendation is the first: evidence for each row plus a visible list, with no new gate.

**L2-2 · Rewrite request (should-fix):** "B8 is labelled as shadowed by B1" names a dc3 category, not a rule. dc3's B8 constraints sit in the `owner_other` context, not in either of the two unconfirmed-by-design contexts. So the label has to come from a relationship between two findings: the constraint's owner is a calc usage that has a refused `calc-owned-assertion` finding. Two engineers would build this differently. One would hard-code a reason string. The other would correlate findings, and that is close to L6 re-deriving a decision. The spec should state the general condition for "shadowed by", and say whether the contract supplies the relationship or L6 computes it from finding subjects alone.

**L2-3 · If-then tradeoff (should-fix):** The routed advisories UNSUPPORTED-SHAPE-MESSAGE and WRAPPER-SHAPE (r3-proposal §4) are required but have no success criterion. The spec also does not say where their detection lives:
- **If** L6 writes the detection itself, Item 3 adds new hand-written generator checks to L6, which is the defect its Problem section opens with.
- **If** the contract does, it is an Item 1 library change. A change to the rule records moves the digest and so the version (L2-4).

The same applies to "the MULTIPLICITY-SHAPE row closes here" and to consuming ES-005 for UNSUPPORTED-RHS: there is no criterion that shows either. Each routed obligation should get a criterion, and the spec should say which layer holds the advisory logic.

**L2-4 · If-then tradeoff (should-fix):** The coverage limit has to come from the contract, and `SUBSET_PROFILE_VERSION` and its digest must not move. Those two requirements can pull against each other. The version pins a digest of the rule records and the allowlist (`subset_profile.py:118-120`).
- **If** the coverage list goes into `subset_profile_rules.toml`, the digest changes, and the spec's stop-and-ask rule triggers.
- **If** it goes in a separate packaged list, the version stays put, but the list can then change while the version string stays `subset-profile/v1`. Two runs could report the same version and claim different coverage.

The second option is probably right. But the spec should say outright that the coverage list is versioned apart from the decisions (with its own pinned test), so nobody later reads "same version" as "same coverage".

**L2-5 · If-then tradeoff (should-fix):** The spec rates the work MEDIUM. The scope is:
- a settings reader shared with research;
- a byte-preserving TOML writer and an interactive `init` prompt;
- evaluator wiring and presentation for 5 verdicts × 3 targets;
- an additive change to Item 1's library;
- an audit of 17 issue codes;
- per-site tests for 21 exception sites, and the runner change;
- docs and four evidence files.

**If** this is meant to fit one design and plan cycle, it is closer to LARGE, and the plan should expect several sessions. Splitting does not help much: the exception-site work has to land before `native` can demote anything (L3-1).

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (must-fix):** The 7 exception sites the spec leaves unaddressed can hide inspection failures under `native`, which epic scope 3 forbids. The spec says these 7 "over-report rather than hide". Over-reporting means a failed inspection turns into a **model-defect finding on a generator-specific check**, which `native` then demotes into the INFO summary. Two examples:
- If enumeration fails at `level6_architecture.py:723`, `instantiated` is left empty. Every calc-bearing part definition is then flagged `L6_CALC_DEF_NO_INSTANTIATION`, which the spec maps to INFO under `native`.
- If `is_instance` fails at `:520`, the calc-usage skip is bypassed, and that can produce `L6_DESIGN_ATTR_INCOMPLETE` or `UNEXTRACTABLE`, also INFO under `native`.

The `adr002.py` sites 277, 335 and 423 have the same shape. The spec already brings the two `AttributeError` catches into scope for exactly this reason ("turn an inspection failure into a model-defect finding"). The 7 sites need the same treatment: a disposition for each site, and a test that the failure is reported as `L6_CHECK_ERROR` and never counted in the native summary. Two exceptions: `:960`, which already reports the failure, and `adr002.py:268`, which is dead code and can simply be deleted.

**L3-2 · Direct claim (must-fix):** The spec's own `[HARD]` item requires one closed key set, but no criterion tests it. The spec does say that unknown values and the `[tool.agentic_mbse]` spelling are errors. But nothing says what L6 does with an unknown **key**, such as `execution_target` or `executiontarget`. If L6 ignores it, a misspelled key silently gives unset (warnings) for a project that meant `generated`. That is the failure `docs/research-seam.md:350` gives as the reason for the guard's closed set. Three more gaps sit here:
- **Who validates what.** The spec does not say whether each reader checks only that a key belongs to the set, or also the other key's value. If L6 validates `research.holdout-guard`, a bad guard path fails `validate`. If the holdout guard validates `execution-target`, a typo in the target refuses every `register`, because the guard fails closed (`research-seam.md:412-419`). The spec should say that each reader checks set membership for both keys but checks the value only of its own key.
- **R3-2 list.** Rejecting an unknown key or the underscore table at L6 fails projects that pass `validate` today. Those cases are missing from the R3-2 list, which names only "a malformed `pyproject.toml` or unknown value".
- **Docs.** `docs/research-seam.md:350` and `:414-415` state the old closed set ("`[tool.agentic-mbse]` holds only `research`"). They are not in the spec's Docs section, but they become wrong as soon as the guard changes.

**L3-3 · Direct claim (must-fix):** The dc3 evidence criterion cannot be met with today's renderer. `print_result` prints the first 5 issues and the first 3 warnings, then "... and N more" (`common.py:141-156`). The `--verbose` flag does not change that. On dc3 baseline that is 236+ refused findings. The criterion says one run "shows every confirmed category in one output … Each finding has a location, a stable reason and a remedy". The native criterion ("detailed results are still available") has the same problem. The spec must say which output carries the full list (verbose, metrics or structured output), and the evidence criterion must name that output. Otherwise design either changes the renderer for every level without saying so, or the criterion is quietly met by the metrics alone.

**L3-4 · Rewrite request (must-fix):** The presentation criteria do not cover what the brief asked for ("how `CLEAR`, `REFUSED_INCOMPLETE`, `unconfirmed` and `unverified` are presented"), and some cannot be checked:
- **Unconfirmed:** no test checks that an `unconfirmed` finding is never ERROR under `generated`, or that it says no probe has observed it and, for the two by-design contexts, which context caused it. The requirement exists; the criterion does not.
- **Unverified and `incomplete`:** no test covers how unverified checks are shown under each target (ERROR under `generated`; a separate WARNING line under `native`; R3-2-dependent under unset). No test covers the `incomplete` verdict (no refusals, some checks unverified).
- **Exclusions:** owner decision 5 covers both exclusions and omissions. Only omissions have a test (the String criterion). Nothing shows that an `excluded` non-numerical predicate under `generated` is a WARNING carrying its own reason.
- **Unassessed constraints:** see L1-2.
- **Uncheckable wording:** "an unqualified 'clean'/'pass' **next to** the profile verdict" and "no output line … **implies**" cannot be tested mechanically. The spec should say what the test actually scans for.
- **Level title:** the banned list cannot fail on "Architecture & Pipeline Readiness". Product-lens spec-F1 left the title to design "through the wording test", but as written the test cannot reject the title, so in practice it stays. The spec should either decide the title or say plainly that it stays.

**L3-5 · Direct claim (should-fix):** The R3-2 before/after evidence measures "L6 pass/fail and exit codes". The runner change is the one R3-2 source that reaches every level (`runner.py:128-137`). A level 2 or level 4 crash that passes today would fail afterwards, and an L6-only measurement would not catch it. The evidence should compare full `validate --complete` runs.

Separately, both evidence files run on `git archive` copies. Where the copy is extracted decides which project root is found. Under `$HOME`, a copy with no marker of its own resolves to `$HOME` (spec, discovery bullet, Item 4 audit finding 7), and L6 would then read `$HOME/pyproject.toml`. The evidence should record the root that was resolved and the file it read for every run.

**L3-6 · Rewrite request (should-fix):** For `init`, the spec covers a symlinked file and a file that will not parse. It does not cover a file that parses but cannot safely take a new key. Examples: `agentic-mbse` defined as an inline table or with dotted keys under `[tool]`. In those layouts, adding a `[tool.agentic-mbse]` header produces a duplicate-table TOML error. CLAUDE.md's rule for native settings has the same caveat ("when the TOML layout permits"). The requirement should be: the written file parses, and every value already in it is unchanged; otherwise `init` prints the line to add instead. Two cases are also unspecified:
- an existing value that is invalid (e.g. `"generate"`) at `init` time;
- whether an interactive re-init asks again every time when the owner chose "leave unset" before. Nothing records that choice, so it would ask on every re-init.

**L3-7 · Direct claim (should-fix):** A criterion and its requirement disagree:
- The final-line criterion requires the qualifier under unset only "with generator findings at WARNING".
- The requirement says the final line carries the qualifier "whenever the target is unset".

An unset run with no findings is covered by the second and not the first. One of them should change.

**L3-8 · Rewrite request (should-fix):** "The detailed results are still available (design picks how)" passes whatever is built. Leaving the mechanism to design is fine. The criterion should still require that a test reads the details from whatever place the design chooses.

**What holds:** the `init` preservation requirements match CLAUDE.md § Init File Ownership: existing values are kept even under `--force`, there is a golden-file test for byte preservation, and symlinks are not replaced. `install-commands` is correctly kept away from the setting. The rule that the version must not move has a checkable criterion against `ebb3d467`. The coverage-list test can read the matrix from `tests/fixtures/subset_profile/`, which is how `tests/test_subset_matrix.py` already works, so it does not depend on the archive folder. The non-goals keep Item 2 (String policy, the PUSH-DOWN rows that wait on it) and Item 5 (the pattern doc, the fence harness) out.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** "An audit of 19 existing L6 codes" (Complexity line). `sysml/types.py` defines 17 issue codes that L6 emits: `V1`, `V2`, `V4_UNSUPPORTED_OPERATOR`, `V4_STATIC_FUNCTION_INVOCATION` and 13 `L6_*` codes. The spec should say what the 19 counts (probably the 17 plus manifest failures and model-load failures), or correct the number.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The success criteria rely on labels that the reader has to decode from other documents: B1–B8, ES-00x, impl-F1/F2, D11, and r3-proposal line numbers (":44", ":60"). The dc3 criterion ("B1–B6 appear as refused errors, B7 as omitted warnings and B8 as unconfirmed") cannot be checked without `acceptance.md`'s table open. The spec should give a one-line mapping (B# → rule/shape) or a direct pointer to that table, and say what impl-F1/F2 are in plain words the first time they appear in the criteria.

---

## Engagement Summary

**Overall take:** The spec has the right work item and an accurate problem statement. It records R3-1 and R3-2 honestly and leaves them open, and its code claims mostly check out. But it understates one R3-1 case by a whole target, makes one false claim about the contract, leaves one way open for `native` to hide inspection failures, and has criteria that cannot be met or checked as written. Those are targeted edits, not a rework.

**Here's what I need you to weigh in on:**

1. **[L1-1]** The `L6_CONSTRAINT_MALFORMED_NUMERICAL` R3-1 case also relaxes under `generated`: unconfirmed contexts become WARNING and uninstantiated owners get no finding. dc3 B8 is this case. The R3-1 entry the owner sees has to say so. (must-fix)
2. **[L1-2]** `UNASSESSED` does not become unverified in the contract. A requirement is needed for how the existing count is shown and at what severity, without L6 re-deriving anything. (must-fix)
3. **[L3-1, L2-1]** Under `native`, a failed inspection can still reach the INFO summary through the 7 "over-report" sites, and nothing gates a misclassified "generator-specific" check. Require a disposition and a test for each site, plus evidence for each audit row. (must-fix / should-fix)
4. **[L3-2]** The closed `[tool.agentic-mbse]` key set has no criterion. A misspelled key gives silent unset. Each reader's value checks could break the other reader. The R3-2 list and `docs/research-seam.md` both miss this. (must-fix)
5. **[L3-3]** The output shows 5 issues and 3 warnings, so the dc3 "every finding in one output" criterion cannot be met. Name the output that carries the full list. (must-fix)
6. **[L3-4]** Add presentation criteria for unconfirmed, unverified, `incomplete` and excluded. Make the banned-wording test checkable, and decide the "Pipeline Readiness" title. (must-fix)
7. **[L2-3, L2-4]** Say which layer detects the two routed advisories, and say that the coverage list is versioned apart from `SUBSET_PROFILE_VERSION`. (should-fix)
8. **[L3-5]** Measure R3-2 with full `validate --complete` runs, and record the resolved project root for each archive copy. (should-fix)

Should-fix only, no decision needed: L1-3, L1-4, L1-5, L2-2, L2-5, L3-6, L3-7, L3-8, L4-1, L5-1.

---

## Resolutions

[None yet. R3-1 and R3-2 are with the owner and are not decided in this review. Record resolutions here by finding ID.]

---

**Verdict:** Revise

**Next Steps:** Once resolutions are recorded, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review. The must-fix items are L1-1, L1-2, L3-1, L3-2, L3-3 and L3-4. The reviewer does not edit the spec. L1-1 and L3-2 change what the owner is asked under R3-1 and R3-2, so the revised gate entries should reach the owner before R3-1 and R3-2 are decided.

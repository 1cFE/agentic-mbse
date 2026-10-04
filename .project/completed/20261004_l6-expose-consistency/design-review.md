# Design Review: L6 EXPOSE Validation Consistency

**Design:** `.project/active/l6-expose-consistency/design.md` (commit 2d4b165, Draft)
**Spec:** `.project/active/l6-expose-consistency/spec.md`
**Brief:** `.project/active/l6-expose-consistency/briefs/design_review.md`
**Review File:** `.project/active/l6-expose-consistency/design-review.md`
**Date:** 2026-10-04

---

## The Point

A design attribute bound directly to a calculation output (`attribute x : Real = my_calc.output_val;`) is the documented EXPOSE pattern (`docs/patterns/expose-pattern.md`). Today Level 6 contradicts itself on it. The static-expression check (V2) accepts it through `_is_expose_pattern` (`adr002.py:389`). The supported-operator check (V4, `adr002.py:94`) reports `.` as an unsupported operator. The completeness check (`level6_architecture.py:475`) reports `L6_DESIGN_ATTR_UNEXTRACTABLE`. Level 6 is the codegen-readiness gate, so a modeler following the documented pattern is told their supported dataflow is broken.

The obligation, from the spec: make validation agree with itself and with the documented pattern. Accept exactly what the existing EXPOSE classification accepts; reject everything else the way it is rejected today. Arithmetic over a calc output stays rejected. No new expression support, no codegen change, no workflow change.

## Fundamental Assessment

**Sound approach, with one decision the owner must make before implementation (C1).**

- **Right piece of work.** The completeness check's own docstring already promises "values or EXPOSE bindings" (`level6_architecture.py:480`), and its suggestion text says "bind to calc output" (`:561`). The code never implemented that half. For the reported defect (calc-headed EXPOSE on a part def and on a part usage), the fix makes the code keep a promise it already states.
- **Right approach.** V4 and completeness each gain one guard that asks the existing predicate. Nothing new is invented. The shared utilities (`extract_operators`, the numeric evaluator, `SUPPORTED_OPERATORS`) stay untouched. A senior engineer would not ask "why?" of this mechanism.
- **Independently verified.** I re-ran the design's Appendix A fixtures through `validate_architecture` against the live parser, before and after a faithful simulation of the two guards (same position, same effect). Results match the design exactly (Brief Item 3).
- **But the fix accepts more than the documented pattern, and the design doesn't say so.** The predicate accepts any chain headed by a sibling *part* usage, of any length. Today Level 6 fails those chains (through V4 and completeness). After this fix, Level 6 passes them with zero diagnostics. The repo's shipped modeling guide calls that shape a violation. This is C1 below. It does not change the mechanism; it changes what the design must state, pin in tests, and hand off as follow-up.
- **Product lens:** gate CLEAR (no owner or `[HARD]` contradiction). It returned one DON'T finding at `[INHERITED]` grade, which is C1. Ledger entry and disposition are appended to `product-lens.md`.
- **Structural smells (product-lens spec §4):** neither fires.
  - *Consumer compensating for a producer guarantee:* no. `extract_operators` faithfully reports SysIDE's typing (a feature chain is an operator expression with `.`). V4 treating an EXPOSE binding as outside its scope is a scope rule, not a workaround for a broken producer. Same for completeness and the numeric evaluator.
  - *Invariant ownership changing silently:* no. The EXPOSE boundary moves from a V2-private helper to a public predicate with three consumers, and D4 says so explicitly.

---

## C1 — Decision required: is a chain headed by a sibling part EXPOSE?

**Situation.** The predicate returns `True` for any top-level feature chain whose head is a sibling `CalculationUsage` *or* `PartUsage`. It never checks chain length or what the chain ends on (`adr002.py:458-478`). My probe confirms it for three shapes:

- `attribute relayed_lit : Real = sub.lit;`, where `sub` is a sibling part and `lit` is a plain literal
- `attribute relayed : Real = sub.out_v;`, where `sub.out_v` is itself an EXPOSE
- `attribute hop : Real = inner.c.result;`, multi-hop through a sibling part

Today each gets V4 `.` plus `L6_DESIGN_ATTR_UNEXTRACTABLE`, so Level 6 fails them. V2 already accepts them. After this fix, each gets zero diagnostics. The same applies to `attribute p : Real = subsystem.rotor.power;` inside the part that owns `subsystem`. The design never mentions this change. It treats part-headed chains only as a codegen-support question (B2), and none of its fixtures or predicate tests includes a part-headed chain.

**The repo's own product statements disagree about this shape.**

- *Calc output only; other dotted paths fail:*
  - `docs/patterns/expose-pattern.md:152-153`: EXPOSE_PURE is "a plain attribute bound directly to a single calc output".
  - `docs/patterns/adr002-calculations.md:39` and `:44`: EXPOSE row is "1 (calc output)"; "Self / dotted reference … `= a.b.c`" is **FAIL**.
  - `project_templates/MODELING_GUIDE.md.template:57`: "Self-reference or dotted path: `= self.x`, `= a.b.c` | **VIOLATION**". This file is tool-owned and shipped to every target repo.
  - `docs/patterns/common-mistakes.md:166`: `attribute p : Real = subsystem.rotor.power; // VIOLATION!`
  - `docs/patterns/adr002-calculations.md:116` and `:208` say the same, but under "What an inline FORMULA may NOT do". Those two are scoped to FORMULA; the three above are general.
- *Part-headed and multi-hop EXPOSE supported:*
  - `docs/patterns/plant-idiom.md:347`: "Multi-hop EXPOSE (through a nested part) … supported."
  - The predicate's own docstring: "transitive EXPOSE" under an "ADR-002 amendment" (`adr002.py:397-402`). No doc contains that amendment.
  - Codegen, per the orchestrator's B2 verification. I am not re-raising B2. This conflict is about our docs, not codegen.
- *Unclear:* `docs/patterns/plant-idiom.md:406-413` says to keep cross-part references to one hop because multi-hop chains truncate. That needs reconciling under either option.

**The crux.** The spec's Known Requirement (`spec.md:22`, `[INHERITED]`) cites the predicate (`adr002.py:389`) and `expose-pattern.md` as one boundary. They are two boundaries. Following the recorded rule ("the existing classification defines the boundary") works against the recorded goal ("agree with the documented pattern") for part-headed chains. Under capture-fidelity law 4 this gets surfaced, not settled by the reviewer or the design agent.

**Options.**

- **(a) Keep the predicate's boundary; align the docs later.**
  - No mechanism change.
  - The design must:
    - restate The Point (today it says "bound directly to a calculation output", which is narrower than what the fix accepts);
    - add one part-headed chain to `shapes/` as a deliberately accepted case, so the new pass is pinned rather than incidental;
    - add a Non-Goal plus follow-up to align the five doc locations above and `plant-idiom.md:406-413`.
  - Cost: until that follow-up lands, Level 6 passes shapes the shipped guide calls violations.
- **(b) Narrow the one predicate to calc-headed chains.** This is the design's own R1 response.
  - Cost: V2 changes too. It starts flagging part-headed chains it accepts today, which goes beyond the spec's "consistency, no new support" framing.
  - Models that follow `plant-idiom.md:347` get new errors, and codegen (per the orchestrator) handles those models.
  - Controls gain a rejected part-headed case, and the predicate test changes.

**Recommendation `[AGENT]`: (a).** Three of the sources that describe actual behaviour accept these chains: V2 today, codegen per the orchestrator, and `plant-idiom.md:347`. Narrowing would add errors to models the toolchain handles. The doc FAIL rows look stale relative to the undocumented "transitive EXPOSE" amendment. **But the owner should make this call.** The shipped guide is the user-facing promise, and on a literal reading the spec's goal sides with it. The design agent should not pick between (a) and (b) on its own.

---

## Brief Items (the six pressure tests)

### 1. D1: share the predicate, not a four-way classifier

**The conclusion is right. The rejection reasoning is half right.**

- **The hazard D1 cites is real.** I probed `attribute s : Real = sqrt(2.0);`. The reference walk raises on any non-`sum` call (`_require_supported_invocation`, `reference_use.py:396`). V2 swallows that raise and reports nothing for `s` today. Completeness reports `L6_DESIGN_ATTR_UNEXTRACTABLE` only because it never walks references. A classifier that routed completeness through the walk would drop that diagnostic.
- **"Making the enum safe would need a new unclassifiable kind, which is new policy" is overstated.** A fail-closed "unknown" result, where each check falls back to its current rule, is exactly what the predicate's `return False` already does. That is mechanism, not policy.
- **The stronger reason to reject the enum is simpler.** V4 and completeness need one bit. The other three rungs (true static, FORMULA, derived) and their order have one consumer, V2. A four-way enum would be an abstraction built for one caller.
- **"Policy lives in one place" holds for the question the repaired checks ask.** "Is this an EXPOSE binding?" has exactly one answer site. Three call sites of one predicate are consumers, not duplicated policy. This is also why C1 is cheap to act on: under either option the boundary changes in one place.
- **The thin seam holds, with one caveat to write down.** The FORMULA follow-up ("extract V2's FORMULA condition into a predicate beside `is_expose_binding`") cannot be walk-free, because `_is_supported_formula` needs the reference uses (`adr002.py:637`, `:651-655`). That future predicate must catch the walk's errors and return `False`. State Invariant 2 ("never raises; fail closed") as the rule for every shared predicate, not just this one.
- **Duplication does remain, in scope selection rather than classification.** Each check decides "is this a design attribute I check?" differently:

| Check | Skips calc-usage owners | Skips calc-def owners | File scope |
|---|---|---|---|
| V2 (`adr002.py:606-625`) | yes | yes | not `library/` (substring) |
| V4 (`adr002.py:125-138`) | **no** | yes | not `library/` (substring) |
| Completeness (`level6_architecture.py:505-519`) | yes | **no** | `designs` path part (default) |

This divergence is the next defect in this family (Item 6, second bullet). It is out of scope here. The design should still name it as a follow-up so nobody reads this seam as "the three checks are now consistent."

### 2. D4: rename, drop `calc_outputs`, delete `_build_calc_output_catalog`

**Confirmed safe.**

- `calc_outputs` is never read inside the predicate body (`adr002.py:419-482`).
- `_build_calc_output_catalog` has exactly three callers: `adr002.py:600` (V2, feeding the predicate) and `tests/test_sysml/test_adr002.py:193` and `:223` (both only to feed the predicate). Nothing in `src/`, `claude/`, `docs/`, or `scripts/` references it.
- V2 already discards the catalog's second element (`calc_outputs, _ = ...` at `:600`).
- Rename the two test functions named `test_is_expose_pattern_*` (`test_adr002.py:186`, `:216`) along with the predicate.
- A public helper in `adr002.py` imported across modules has precedent: `reference_is_dynamic` (`adr002.py:331`).
- Adjacent dead code, not for this item: `_get_calc_usage_names` (`adr002.py:310`) has zero callers. `_is_calc_output_reference` (`adr002.py:342`) is called only from `tests/test_validation/test_v2_false_positive.py`. After D4, nothing in production can build its `calc_def_qualified_names` argument. Note both as follow-up cleanup.

**One thing D4 misses: the docstring states a stricter boundary than the code enforces.** The current docstring (`adr002.py:395-417`) claims two criteria the body never checks: "the target is a single attribute/output reference" and "a sibling part's attribute that is itself an EXPOSE (transitive)". The three probe shapes in C1 all return `True`, and so does `attribute read_input : Real = c.value;` (reads a sibling calc's *input*). Invariant 3 in the design describes the real boundary correctly. But Component Overview says only that the docstring "loses the `calc_outputs` argument and names the three consumers." The design's own brief already carried the wrong version forward once (`briefs/design.md:20`: "and a single attribute/output target"). D4 makes this predicate public so that its boundary is visible. A docstring that misstates the boundary defeats that purpose. See M1.

### 3. D5 and the controls table (Appendix B)

**The 13 pairs are correct and they are the right controls. The assertion needs two small tightenings, and C1 adds one fixture case.**

Verified by probe (live parser, 2026-10-04, scratch under the gitignored `build/`):

- `controls/` returns exactly the 13 Appendix B pairs, each exactly once, both before and after the simulated fix. "Design attrs checked" is 6. `result.issues` has 13 entries and no unstructured strings.
- `shapes/` returns the four predicted issues before the fix and zero after. "Design attrs checked" is 2 both times. `success` is true after.
- The retained referent, copied into `designs/` + `library/` and run through `validate_architecture` with the default filter: `exposed_output` goes from two issues (V4 `.`, unextractable) to zero. `combined` keeps V2, unextractable, and **two** V4 `.` issues (one per chain operand).

**What `validate_architecture` runs, and why none of it fires here.** It runs 13 structured checks (`level6_architecture.py:975-995`) plus manifest checks (`:998`). On these fixtures:

- V1 calc-def location: the calc defs are in `library/`.
- C5 static function invocation: no function calls.
- Qualified names, calc-def structure, anonymous returns, body assignment: `ScaleCalc` has a named `out` with an inline value.
- Constraint executability: no constraints.
- C4 calc-bearing instantiation: `ExposingModule` is instantiated, and the controls have no part defs.
- C7 attribute-redefinition drop: no `:>>` redefinitions.
- Binding formats: the calc-usage parameters bind literals.
- Manifests: `_check_manifests` globs `designs/*/manifest.yaml` (`:135`), and the fixtures have none.

**Are these the right controls for SC3?** Yes. Each SC3 clause has a control:

- unsupported operator: `powered` (`^`)
- absent value: `missing`
- unextractable static default: `divzero`
- invalid reference targets: `remote` (head is a part that is not a sibling) and `payload_mass` (head is a sibling item)
- arithmetic over a calc output: `derated`

They also catch the plausible wrong implementations:

- "Skip any feature chain" loses V4 and unextractable on `remote` and `payload_mass`.
- "Head is a calc or part usage", without the sibling test, loses them on `remote`.
- A `"." in text` test loses them on all three dotted controls.

**Does an exact set prove "no unrelated diagnostic hides the result"?** For unrelated *codes*, yes, as long as the comparison covers every structured issue with no pre-filter. Two gaps:

- **Counts.** A set of (code, element) pairs cannot see a count change, and the referent's `combined` already shows that V4 can emit the same pair twice. Compare a sorted list or a `Counter` instead, so the test pins "exactly once."
- **Wording.** The Validation Approach row says "over the four affected codes … and no other code appears." That reads as filter-then-compare plus a separate check. State it as one equality over every structured issue, and add `len(result.issues) == 13`. `result.issues` carries manifest strings too (`:1070`), so this closes the manifest gap for controls the same way `issues == []` does for shapes.

Under C1 option (a), add one part-headed chain (for example `sub.out_v`) to `shapes/` as an accepted case. Under (b), add it to `controls/` as a rejected one. Either way, the tests should pin the decision.

Nice-to-have: put the V4 operator in the compared tuple (`^` for `powered`, `.` for the chains). SC3's "unsupported operators" clause is proven by `powered` firing for `^`, and the (code, element) pair alone doesn't say which operator fired.

### 4. Invariant 2: the predicate never raises

**Holds.**

- The whole body (`adr002.py:420-478`) is inside `try` / `except Exception: return False` (`:480-482`).
- Every return is a literal `True` or `False`.
- The helpers it calls, `_is_calc_usage` (`:323`) and `_is_part_usage` (`:381`), catch internally and return `bool`.
- `resolved_referent` is a `getattr` with a default (`reference_use.py:190-192`).
- Only `BaseException` (for example `KeyboardInterrupt`) escapes, which is correct.

The sibling test uses Python identity (`attr_owner is not source_owner`, `:472`). That relies on SysIDE returning the same Python object for the same element. The probe confirms it does: both shapes return `True`. B3 already covers this.

### 5. Guard placement

**Correct as specified.**

- **V4.** The existing skips (`adr002.py:125-145`) are side-effect-free `continue`s. Putting the EXPOSE guard after them cannot change behaviour for calc-def-owned or `library/` attributes; the order only affects cost.
- **Completeness, invariant 6.** `attrs_checked += 1` (`level6_architecture.py:521`) runs before `if has_value:` (`:530`), so a guard inside that branch is still counted. The probe confirms it: "Design attrs checked" for shapes stays 2 after the fix.
- **Completeness, path filter.** The `design_path_filter` test (`:509-511`) runs before the count and before the guard. I probed an EXPOSE binding in `other/outside_designs.sysml`. With the default filter, completeness neither counts nor diagnoses it, before or after the fix. With `design_path_filter=None`, it is counted, and the fix clears it.
- **Implementation detail.** The guard should `continue`, or the evaluator call should move to an `else`. The trailing `if not has_value:` (`:552`) can't fire for an attribute that has a value, so either form is correct.

### 6. Parser and code claims I could disprove

- **"The V4 `**` orchestrator test (`tests/test_sysml_quality_checks.py:1087`) uses a fixture with no chains."** Wrong. The test runs `validate_architecture("tests/fixtures/adr002_violations")` (`:923`), and that directory includes `v2_expose_pattern.sysml` with its chains. The conclusion still holds: the test asserts `>= 1` V4 issues and `any("**" in message)` (`:1097-1098`). After the fix the run loses the two `exposed_output` issues and still passes. Correct the Research Findings sentence.
- **"Calc-usage parameter bindings (`in value = producer.exposed;`) parse as `ReferenceUsage` … They never reach V4 or completeness."** True for that bare spelling. But `docs/patterns/semantic-operators.md:127`, `:350`, and `:355` still show the `in attribute x = source.result;` spelling, and I probed it:
  - It parses as an `AttributeUsage` owned by the calc usage.
  - It reaches V4, which reports `.`. V2 and completeness skip it by owner, and C7 also warns on it.
  - The fix doesn't clear the V4 report, because the attribute's owner is the calc usage and the chain head is not its sibling.

  This is not an EXPOSE binding, so it is out of scope. It has the same symptom ("V4 reports `.` on a binding"), and the cause is the scope divergence in Item 1. Add it as a Non-Goal / follow-up so a user report about it isn't read as a regression of this fix.
- **Scan of the existing corpus.** Across all 31 fixture roots under `tests/fixtures/`, the predicate accepts exactly two attributes: the referent's `exposed_output`, and `RescueLib::RescuePlant::throughput` in `item12/self_named_rescue/library/`. V4 skips the second one because it is under `library/`, and completeness skips it under the default filter. No existing test calls V4 or completeness on it. This supports the Integration Strategy claim that only the two renamed `test_adr002.py` tests change.
- Everything else I checked holds: the line citations, the three swallow sites, the C4 instantiation requirement, and `extract_operators` having one production caller. The evaluator raises an explicit `ValueError` on division by zero (`expression.py:555-559`), so R3's control is safe.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- **SC1** (the retained referent through the individual checks and the combined route in a checked location): covered by Validation Approach row 1, and both halves are verified by probe. The positive assertion that `combined` still gets V2, V4, and unextractable is what proves the checks actually ran on the file. Keep it.
- **SC2** (both shapes accepted, arithmetic stays rejected): covered by `shapes/` and `derated`. Verified.
- **SC3** (controls; no arbitrary dotted reference admitted): covered by `controls/` and the parametrized predicate test. Verified. SC3 is met to the letter, but part-headed chains are newly admitted without being named (C1).
- **Capture fidelity.**
  - The design treats the spec's `[INHERITED]` boundary requirement (`spec.md:22`) as fixed. That requirement merges two sources that disagree (C1). Inherited items are challengeable, and this one needed challenging.
  - The design's Point quotes the narrower source ("bound directly to a calculation output") while its mechanism implements the wider one.
  - The brief's `[AGENT]` four-way-classifier goal was challenged with recorded reasoning (D1), which is the right handling for an agent-grade item.
- **Implementer note for SC1 part (1).** With `design_path_filter=None`, completeness also checks the library calc def's own attributes, because it does not skip calc-def owners. The probe shows `ScaleCalc::value` (INCOMPLETE) and `ScaleCalc::result` (UNEXTRACTABLE) firing under `None`. Assertions in that test must stay scoped to `exposed_output` and `combined`, as the design already says.

### 2. Pattern Consistency
**Assessment:** Pass

- The fixture layout (`<case>/library/` + `<case>/designs/`, loaded per directory) matches `tests/fixtures/item12/` and `tests/fixtures/l8_extractability/`.
- A public cross-module helper in `adr002.py` has precedent (`reference_is_dynamic`).
- Nice-to-have, not for this item: the predicate's first test is a class-name string match (`"FeatureChain" not in type(expr).__name__`, `adr002.py:423-425`). The codebase idiom is `SysideAdapter.is_instance(expr, "FeatureChainExpression")` (for example `level6_architecture.py:439`). "Logic unchanged" is the right discipline here, so leave it.

### 3. Abstraction Quality
**Assessment:** Pass

No new abstraction: one rename that makes an existing cross-module contract visible. The enum was correctly rejected (Item 1).

### 4. Duplication Avoidance
**Assessment:** Concerns

The EXPOSE decision is single-sourced. The scope-selection logic is still triplicated and divergent across V2, V4, and completeness (table in Item 1), and that divergence already produces one adjacent false positive (Item 6). It is out of scope here; name it as a follow-up.

### 5. Data Structure Clarity
**Assessment:** Pass

A `bool` predicate over live parser objects. No new data, no caching, no shared state.

### 6. Route Safety
**Assessment:** Pass

The only route is the combined Level 6 route, and it is unchanged. The new branch fails closed: on any analysis failure the predicate returns `False` and the check applies its current rule. No new swallow sites are added.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **Hidden bet: the predicate's boundary is the documented boundary.** It isn't, for part-headed chains. This is C1.
- **B3 is a genuine bet** with an honest failure mode (visible, not silent). Verified.
- **B1's wording is narrower than the boundary it justifies.** B1, the Core Concept ("a wire to a calculation output channel"), and D3 ("codegen surfaces the output channel") justify accepting EXPOSE through the calc output channel. That covers calc-headed chains only. Part-headed chains have no calc output channel; the orchestrator-verified fact that covers them is that codegen turns any feature chain into an alias node resolved by occurrence identity. When the author folds in the B2 resolution:
  - restate B1, D3, and the Core Concept in alias terms;
  - remove the stale Non-Goal ("Verifying codegen's handling of part-headed chains") and the "De-risk first" handoff line.

  This is bookkeeping for the fold, not a re-raise of B2.
- **Hidden bet: an alias's target gets checked somewhere else.** Completeness will treat `x = sibling.attr` as complete without looking at `attr`.
  - Safe for calc outputs, because the calc def computes them.
  - Safe for targets declared in `designs/`, because completeness flags those at their own declaration.
  - Not safe for a target declared in a `library/` part def. I probed `part sub : LibPart; attribute aliased : Real = sub.unset;`, where `LibPart::unset` has no value. Before the fix: V4 `.` and unextractable, both for the wrong reason. After: nothing anywhere.

  ADR-002 puts calc defs, not part defs, in `library/`, so this is an edge case. It only applies if C1 resolves to (a). Record it as a stated bet: *if false → Level 6 passes an exposed attribute whose source has no value.*
- **D2's second rejection reason is imprecise.** D2 says removing `.` from the extractor would "silence V4 on every dotted path … which admits a dotted reference merely because it contains `.`." It would not admit `remote`, because V2 and completeness would still fire. The accurate reason is Invariant 4: it would change diagnostics on non-EXPOSE expressions, which the controls pin. The same correction applies to the Non-Goal line "changing it would widen V4."
- **D1's reasoning:** see Item 1. Lead with "two of three consumers need one bit", and keep the swallow hazard as the concrete risk.

### 8. Reader Comprehension
**Assessment:** Pass

The Point, Core Concept, and Architecture sketch give a reader the model in one pass. Decisions name their rejected alternatives, and identifiers carry `file:line` locations. The comprehension risks are in what the design states, not how: the Point is narrower than the mechanism (C1), and the predicate's docstring overstates its checks (M1).

---

## Issues by Severity

### Critical
- **C1. Decision required: the fix newly passes sibling-part-headed chains, which the shipped guide calls violations, and the design doesn't say so.** Today Level 6 fails `x = sub.lit`, `x = sub.out_v`, `x = inner.c.result`, and `p = subsystem.rotor.power`. After the fix it passes all four with zero diagnostics. `MODELING_GUIDE.md.template:57`, `adr002-calculations.md:44`, and `common-mistakes.md:166` call that shape a violation. `plant-idiom.md:347` and the predicate say it is supported. The owner picks (a) keep the boundary and align the docs later, or (b) narrow the one predicate. Reviewer recommends (a). Either way, the design must restate The Point, pin the decision in a fixture, and record the doc follow-up or the V2 change. (Spec Compliance / Bets)

### Major
- **M1. The predicate's docstring publishes a stricter boundary than the code enforces.** It claims a "single attribute/output target" and "transitive EXPOSE (the sibling part's attribute is itself EXPOSE)". Neither is checked: `c.value`, `sub.lit`, and `inner.c.result` all return `True`. Fix: Component Overview says the docstring is rewritten to state Invariant 3 exactly, with those two criteria removed. Under C1 (b), the docstring states the narrowed boundary instead. (Abstraction / Reader Comprehension)

### Minor
- **m1. Controls assertion shape.** Compare a multiset (a sorted list or a `Counter`) over *all* structured issues, and add `len(result.issues) == 13`. Drop the set over four codes plus the separate "no other code" check. (Item 3)
- **m2. Fold-in bookkeeping for B2.** Restate B1, D3, and the Core Concept in alias terms, and delete the stale Non-Goal and the "De-risk first" handoff. (Dimension 7)
- **m3. Record the hidden bet** that an alias target's value is checked at its own declaration, with the library part-def counterexample and its failure mode. This applies only under C1 (a). (Dimension 7)
- **m4. FORMULA follow-up note.** State that a future FORMULA predicate needs the reference walk, so it must catch the walk's errors and return `False`. Generalize Invariant 2 to "every shared predicate fails closed." (Item 1)
- **m5. Name the scope-selection divergence as a follow-up Non-Goal.** Its concrete symptom is the `in attribute x = source.result;` calc-usage binding (`semantic-operators.md:127`): V4 reports `.`, V2 and completeness skip it, and this fix doesn't change that. (Items 1 and 6)
- **m6. Correct the Research Findings claim** that the V4 `**` orchestrator test's fixture has no chains. It loads the whole `adr002_violations/` directory, including the referent. The conclusion (unaffected) stands. (Item 6)
- **m7. Base D2's rejection reason** (and the matching Non-Goal line) on Invariant 4, not on "widening." (Dimension 7)
- **m8. Nice-to-haves:** rename the `test_is_expose_pattern_*` tests; include the V4 operator in the controls tuple; list `_get_calc_usage_names` and `_is_calc_output_reference` as dead-code follow-ups. Do not do the dead-code cleanup in this item.

---

## Recommendations

1. **Get the owner's decision on C1** before the design agent folds anything. The design agent should not choose between (a) and (b) on its own.
2. Fold M1: the docstring states the real boundary, nothing more.
3. Fold the B2 resolution completely (m2), restate The Point to match the C1 decision, and pin that decision with one part-headed fixture case.
4. Tighten the controls assertion to a multiset over all structured issues plus `len(result.issues)` (m1).
5. Add the follow-up Non-Goal lines (m4 FORMULA fails closed, m5 scope divergence, and under C1 (a) the doc alignment), and correct the two factual sentences (m6, m7).

Once C1 is decided, every remaining item is a wording or test-shape edit that can be checked against this list. Per the pipeline rule for minor, verifiable fixes, the fold can be verified without rerunning a design review. If C1 resolves to (b), the predicate logic and V2 behaviour change. In that case a short re-review of the narrowed boundary and its controls is worth it.

---

## Resolutions

Recorded by the orchestrator on 2026-10-04. The owner reserved no gates at Align ("no gates needed unless there is a surprising result that you genuinely need my judgement for"), so C1 was decided at execution-detail tier and is surfaced in the run summary for the owner to reverse if they disagree.

- **C1 → option (a), keep the predicate's boundary.** Recorded as design D6, graded `[AGENT]` (ratified by orchestrator; not owner-originated; reversible in one place, `is_expose_binding`). Reasoning: the spec's inherited requirement names the existing classification as the boundary; V2 has always accepted part-headed and multi-hop sibling chains; codegen resolves any design-attribute feature chain as an alias node by exact occurrence identity (`sysml-codegen/docs/architecture/reference/16-computed-attributes.md`, `tests/conformance/test_elaboration_expose_shapes.py`, orchestrator-verified); narrowing would change V2's accepted set, which is new policy. The three dotted-path doc rows are a pre-existing doc defect and a recorded follow-up (design Non-Goals).
- **M1** folded into D4: the predicate docstring now claims only what the code checks. Verified in the implementation commit `3f442ce` and by the audit.
- **Minor items** (Counter-based controls assertion plus `len(result.issues) == 13`, B2 wording in B1/D3/Core Concept, the `test_sysml_quality_checks.py:1087` correction, the calc-usage `in attribute` binding follow-up) all landed; design Appendix C maps each to its location.
- **Audit Advisory 2 (chains of three or more segments).** `plant-idiom.md:406-413` describes calc *input binding* truncation, which codegen now rejects loudly (D3-2). EXPOSE design attributes take codegen's alias walk, which lands on one exact node or refuses with a diagnostic. V2 accepted deep sibling chains before this item. Disposition: pre-existing boundary, not a regression; no change.

---

**Overall:** Revise. The mechanism is sound and verified. C1 needs an owner decision, and M1 plus the minor items fold in the same pass.
**Next Steps:** The owner decides C1. Record the decision under Resolutions. Then re-run `/_my_design` (or return to the design-agent session) and point it at this review together with the B2 resolution the orchestrator already supplied. The reviewer does not edit the design.

**Review evidence:** scratch probe and fixtures under the gitignored `build/l6probe/`: the Appendix A fixtures, an `edges/` probe for the boundary cases, and an `adjacent/` probe for the calc-usage binding and the library-target bet. Nothing in the repo depends on them.

# Design: L6 EXPOSE Validation Consistency

**Status:** Revised — design review incorporated (2026-10-04); ready for planning
**Owner:** Reid W
**Created:** 2026-10-04 09:53 PDT
**Revised:** 2026-10-04 (fold of [design-review.md](design-review.md) and orchestrator decisions)
**Branch:** harness-right-size
**Commit:** 2d4b165
**Backlog Item:** L6-EXPOSE-CONSISTENCY

## Overview

Two Level 6 checks reject an EXPOSE binding (`attribute x : Real = my_calc.output_val`) that the static-expression check accepts. This design makes all three checks consult the one existing EXPOSE predicate. The supported-operator check and the design-attribute completeness check then stop reporting false positives on EXPOSE bindings, and every non-EXPOSE expression keeps its current diagnostics.

## Related Artifacts

- **Spec:** [spec.md](spec.md)
- **Product lens:** [product-lens.md](product-lens.md) (CLEAR; the review appended one `[INHERITED]` finding, resolved as D6)
- **Design review:** [design-review.md](design-review.md) (verdict Revise; dispositions in [Appendix C](#appendix-c--review-dispositions))
- **Design brief:** [briefs/design.md](briefs/design.md)
- **Evidence:** [October 4 status report](../../reports/2026-10-04-0901-status-report.md#what-is-actually-broken-or-missing)
- **Pattern docs:** [expose-pattern.md](../../../docs/patterns/expose-pattern.md), [plant-idiom.md](../../../docs/patterns/plant-idiom.md), [adr002-calculations.md](../../../docs/patterns/adr002-calculations.md)
- **Epic / Required Reading:** none (standalone backlog item)
- **Decision records:** there is no `.project/adr/` register in this repo, so there are no prior entries to cite.

## The Point

[INHERITED: product-lens.md, from docs/patterns/expose-pattern.md] A design attribute bound directly to a calculation output is a supported EXPOSE interface. Arithmetic over a calculation output is not; it stays rejected as a derived expression.

[INHERITED: spec] Today a modeler who follows the documented EXPOSE pattern gets two Level 6 errors for it: `V4_UNSUPPORTED_OPERATOR` for `.`, and `L6_DESIGN_ATTR_UNEXTRACTABLE`. Level 6 is the codegen-readiness gate, so these errors tell the modeler their supported dataflow is broken when it is not. The obligation is to make validation agree with itself: accept exactly what the existing EXPOSE classification accepts, and reject everything else the way it is rejected today.

[AGENT] (ratified by orchestrator 2026-10-04; see D6) The existing classification is wider than the calc-output example. It accepts any design attribute whose whole value is one feature chain headed by a sibling calculation usage *or* a sibling part usage, of any length. So after this fix, Level 6 also accepts part-headed relays such as `x = sibling_part.exposed`. V2 already accepts them, and codegen supports them.

[INHERITED: spec] The repair is consistency. It adds no new expression support, does not change codegen, and does not change modeling workflows.

## Research Findings

**The three checks and what each does with `x = my_calc.output_val`:**

- **Static-expression check (V2)**, `check_static_expressions` (`src/agentic_mbse/validation/adr002.py:563`). It walks the references, then asks `_is_expose_pattern` (`adr002.py:389`) and accepts the binding (`adr002.py:644`). This is correct today.
- **Supported-operator check (V4)**, `check_supported_operators` (`adr002.py:94`). It calls `extract_operators` (`src/agentic_mbse/sysml/expression.py:98`) on every design attribute's expression. In SysIDE a feature chain is a subtype of operator expression with operator `.` (noted at `expression.py:318`), so the chain reports `.` and V4 flags it (`adr002.py:153`).
- **Design-attribute completeness check**, `check_design_attr_completeness` (`src/agentic_mbse/validation/level6_architecture.py:475`). It calls `evaluate_true_static_expression` (`expression.py:466`) on any value expression. That evaluator raises on any feature reference (`expression.py:506`), so the binding is reported as `L6_DESIGN_ATTR_UNEXTRACTABLE` (`level6_architecture.py:538`).
- All three run in the combined route `validate_architecture` (`level6_architecture.py:976`, `:977`, `:992`).

**The completeness check already intends to accept EXPOSE.** Its docstring says "Validate design attributes have values or EXPOSE bindings" (`level6_architecture.py:480`). Its own incomplete-attribute suggestion says "bind to calc output" (`:561`). The code never implemented the binding half.

**What the predicate actually checks.** `_is_expose_pattern` (`adr002.py:389`) checks three things:

- the expression is a feature chain;
- the chain's first member resolves to a `CalculationUsage` or `PartUsage`;
- that head has the same owner as the attribute (it is a sibling).

It does not check chain length or what the chain ends on. Any failure returns `False` (`adr002.py:480-482`). Its docstring claims two checks the code never makes: "a single attribute/output target" and "transitive EXPOSE" (`adr002.py:395-417`). Its `calc_outputs` parameter is never read. The catalog V2 builds at `adr002.py:600` exists only to feed that parameter.

**The reference walk can raise.** `design_reference_uses` (`expression.py:83`) goes through `inspect_reference_uses` (`src/agentic_mbse/sysml/reference_use.py:291`). That walk raises `SemanticEvidenceError` on any function call other than `sum` (`reference_use.py:395`); confirmed live on `sqrt(2.0)`. It also raises on unresolved targets (`:442`, `:475`). Every check swallows per-attribute exceptions (`adr002.py:170`, `adr002.py:683`, `level6_architecture.py:565`), so an exception silently drops that attribute's diagnostics.

**The three checks pick different sets of attributes to look at.** This is the duplication that remains after this fix. It is in scope selection, not classification (from the review):

| Check | Skips calc-usage owners | Skips calc-def owners | File scope |
|---|---|---|---|
| V2 (`adr002.py:606-625`) | yes | yes | not `library/` (substring) |
| V4 (`adr002.py:125-138`) | no | yes | not `library/` (substring) |
| Completeness (`level6_architecture.py:505-519`) | yes | no | `designs` path part (default) |

One visible effect: `in attribute x = source.result;` inside a calc usage parses as an `AttributeUsage` owned by the calc usage. V4 reports `.` on it; V2 and completeness skip it. The bare spelling `in x = source.result;` parses as a `ReferenceUsage` and reaches none of the three checks.

**Codegen side.** [AGENT, verified by orchestrator 2026-10-04] sysml-codegen turns any feature reference or feature chain in a design attribute's value into an alias node, resolved by exact occurrence identity (`sysml-codegen/docs/architecture/reference/16-computed-attributes.md`). Its conformance tests prove that part-headed, multi-hop, and cross-package chains reach their producer (`sysml-codegen/tests/conformance/test_elaboration_expose_shapes.py`). Codegen's supported set is wider than our predicate.

**The repo's docs disagree about dotted paths. They already disagreed before this fix.**

- *Called a violation:* `= a.b.c` in `project_templates/MODELING_GUIDE.md.template:57` (tool-owned, shipped to target repos), `docs/patterns/adr002-calculations.md:44`, and `subsystem.rotor.power` in `docs/patterns/common-mistakes.md:166`.
- *Called supported:* `docs/patterns/plant-idiom.md:347` says multi-hop EXPOSE is supported. V2 already accepts these chains, and codegen supports them.
- *Unclear:* `docs/patterns/plant-idiom.md:406-413` says to keep cross-part chains to one hop because deeper ones truncate.

**Live-parser probes (2026-10-04, scratch files under the gitignored `build/`):**

- The revised `shapes/` fixture (Appendix A) passes Level 1 with no errors or load warnings. Through the combined route it returns 6 issues before the fix: V4 `.` and unextractable on each of `module_result`, `exposed_output`, and `relayed`. It returns 0 issues after a faithful simulation of the two guards. "Design attrs checked" is 3 both times.
- The `controls/` fixture returns the same 13 (code, element) pairs before and after, each exactly once. `len(result.issues)` is 13. "Design attrs checked" is 6.
- The review's probe ran the retained referent copied into a `designs/` + `library/` layout. `exposed_output` went from two issues to zero. `combined` kept V2, unextractable, and two V4 `.` issues (one per chain operand).
- Across all 31 fixture roots under `tests/fixtures/`, the predicate accepts exactly two attributes: the referent's `exposed_output`, and `RescueLib::RescuePlant::throughput`. The second is under `library/`, so V4 and default-filter completeness never look at it.
- A part definition that carries a calc must be instantiated, or the calc-instantiation check (C4, `level6_architecture.py:693`) fires. Both part definitions in `shapes/` are instantiated.

**Callers and tests.**

- `extract_operators` has one production caller (V4). It is exported from `src/agentic_mbse/sysml/__init__.py:66` and unit-tested in `tests/test_sysml/test_expression.py:423`.
- `_is_expose_pattern` and `_build_calc_output_catalog` are imported by `tests/test_sysml/test_adr002.py:16-17`.
- The FORMULA rejection is pinned by `tests/test_l8_extractability.py:58`.
- The V4 orchestrator test (`tests/test_sysml_quality_checks.py:1087`) runs `validate_architecture` on all of `tests/fixtures/adr002_violations/`, including the referent and its chains. It still passes after the fix, because it asserts at least one V4 issue and a `**` message (`:1097-1098`). Only the two `exposed_output` issues disappear from that run.

**Fixture conventions.** Item 12 cases use `tests/fixtures/item12/<case>/library/` plus `<case>/designs/`, loaded per directory (`tests/test_validation/test_item12_checks.py:45`).

## Core Concept

An EXPOSE binding is an alias. The attribute's value is an upstream value that already exists elsewhere in the model: a calculation output, or an attribute on a sibling part. Codegen resolves the alias to that upstream value by exact occurrence identity. One predicate decides whether an attribute is an EXPOSE binding: its whole value is one feature chain headed by a sibling calculation or part usage. The static-expression check already uses that predicate. The fix makes the other two checks ask the same predicate first. Their own rules are about static values, and an alias is not a static value.

- **The supported-operator check** polices arithmetic in static expressions. An alias contains no arithmetic, so it is outside that check's scope.
- **The completeness check** asks whether a design attribute has a value codegen can use. An alias is such a value, because codegen wires it to its source. It needs no numeric default.
- **Anything that is not EXPOSE** goes through each check exactly as it does today.

**The key insight.** Two of the three checks need only one bit: is this an EXPOSE binding? The predicate answers that from the chain's head and its ownership, without the full reference walk. So it is the one classification those checks can use without inheriting the walk's failure modes. The full ordering (true static, EXPOSE, FORMULA, derived) has one consumer, V2, so it stays in V2 (D1).

**What this composes with.** The predicate stays where the ADR-002 rules live (`adr002.py`). Each check keeps its own scope filters. The operator extractor and the numeric evaluator stay untouched; they keep answering the questions they were built for.

## Key Bets

- **B1. Codegen wires an EXPOSE binding as an alias, so it needs no numeric default.** [AGENT, verified by orchestrator 2026-10-04] Codegen turns any feature reference or chain in a design attribute's value into an alias node, resolved by exact occurrence identity (`16-computed-attributes.md`; `test_elaboration_expose_shapes.py`). *If false → completeness would stop flagging attributes codegen cannot wire, and Level 6 would pass models that fail in codegen.*
- **B2. Codegen supports everything the predicate accepts.** [AGENT, verified by orchestrator 2026-10-04] Codegen's conformance tests cover part-headed, multi-hop, and cross-package chains, which is wider than the predicate's sibling-headed set. So accepting the predicate's set in all three checks never admits a chain codegen cannot wire. *If false → Level 6 would pass a chain codegen rejects. The response would be to narrow the one predicate.*
- **B3. SysIDE resolves a chain's head and its owner reliably enough to decide EXPOSE without the full reference walk.** The sibling test relies on SysIDE returning the same Python object for the same element (`adr002.py:472`). Live probes confirmed this on both shapes, the part-headed relay, and both invalid-head variants. *If false → the predicate would return `False` for valid EXPOSE bindings and the false positives would persist. That failure is visible, not silent.*
- **B4. An alias's target value is checked where the target is declared.** This holds for calc outputs, because the calc definition computes them. It holds for targets declared under `designs/`, because completeness checks them at their own declaration. It does not hold for a target on a part definition in `library/`. In the review's probe, `part sub : LibPart; attribute aliased : Real = sub.unset;` (where `LibPart::unset` has no value) gets no diagnostic anywhere after this fix. ADR-002 puts calc definitions in `library/`, not part definitions, so this is an edge case. *If false more broadly → Level 6 would pass an exposed attribute whose source has no value.*

## Key Decisions

- **D1. Share the EXPOSE verdict, not a four-way classification enum.**
  - V4 and completeness each add one guard that asks the predicate.
  - V2's existing decision order (true static → EXPOSE → FORMULA → derived, `adr002.py:640-681`) stays in V2.
  - *Rejected: a `DesignExpressionKind` enum shared by all three checks.* V4 and completeness need only one bit, and the four-way ordering has one consumer (V2). An enum would be an abstraction built for one caller.
  - There is also a concrete hazard. The other branches need the reference walk, which raises on shapes like `sqrt(2.0)`. Because every check swallows per-attribute exceptions, routing V4 and completeness through the walk would silently drop their diagnostics. For example, `x = sqrt(2.0)` would lose its `L6_DESIGN_ATTR_UNEXTRACTABLE`.
  - FORMULA can still be added to completeness later without restructuring (see Non-Goals and Invariant 2).
- **D2. V4 skips EXPOSE bindings. `extract_operators` and `SUPPORTED_OPERATORS` stay unchanged.**
  - *Rejected: dropping `.` from `extract_operators`' output.* It is a public, unit-tested utility. Changing it would also change V4's diagnostics on non-EXPOSE expressions such as `remote` and `derated`. Invariant 4 forbids that, and the controls pin it.
  - *Rejected: adding `.` to `SUPPORTED_OPERATORS`.* Same reason.
- **D3. Completeness treats an EXPOSE binding as complete before it tries to evaluate.**
  - The attribute still counts toward "Design attrs checked".
  - *Rejected: teaching `evaluate_true_static_expression` to accept chains.* It is a numeric evaluator, and an alias has no static number. Merging them would confuse "has a value codegen wires as an alias" with "has a numeric default".
- **D4. Rename the predicate to `is_expose_binding(attr, expr)`, keep it in `adr002.py`, drop the unused `calc_outputs` parameter, and rewrite its docstring to state Invariant 3 exactly.**
  - The rewritten docstring describes only what the code checks: a top-level feature chain; a head that resolves to a sibling `CalculationUsage` or `PartUsage`; the same owner; any chain length. It drops the "single attribute/output target" and "transitive EXPOSE" claims, because the code checks neither.
  - With the parameter gone, `_build_calc_output_catalog` (`adr002.py:253`) has no caller left and is deleted.
  - The two tests named `test_is_expose_pattern_*` (`tests/test_sysml/test_adr002.py:186`, `:216`) are renamed to match.
  - *Rejected: importing the private `_is_expose_pattern` across modules.* A private name used as a cross-module contract hides that it is one. Precedent for a public cross-module helper in `adr002.py`: `reference_is_dynamic` (`adr002.py:331`).
  - *Rejected: moving the predicate to `sysml/expression.py`.* It is ADR-002 policy, not a generic expression utility.
- **D5. Prove the fix through the combined route with two standalone fixture directories, plus the retained referent copied into a checked layout.**
  - `shapes/` holds shape A, shape B, and one part-headed sibling relay. It must produce zero issues.
  - For `controls/`, a `Counter` of (code, element) over *every* structured issue must equal the 13 expected pairs, each exactly once. Also assert `len(result.issues) == 13`, which catches manifest strings too.
  - The retained `v2_expose_pattern.sysml` is copied with its library into a temporary `designs/` + `library/` layout, so the referent itself runs through the combined route under the default filter.
  - *Rejected: moving or duplicating the referent into a committed `designs/` path.* `tests/test_sysml/test_adr002.py` globs it where it is now.
  - *Rejected: comparing a set over selected codes.* A set cannot see a duplicated issue, and a code filter cannot see an unrelated diagnostic.
- **D6. Keep the predicate's existing boundary, including part-headed and multi-hop sibling chains.** [AGENT] (ratified by orchestrator 2026-10-04; not owner-originated; reversible in one place, the predicate)
  - The spec's inherited requirement names the existing classification as the supported boundary.
  - V2 has always accepted part-headed and multi-hop sibling chains. Codegen accepts them (B2), and `plant-idiom.md:347` documents them as supported.
  - The three doc rows that call `= a.b.c` a violation already contradict V2, codegen, and `plant-idiom.md`. That is a pre-existing doc defect, recorded in Non-Goals.
  - *Rejected: narrowing the predicate to calc-headed chains.* That would change V2's accepted set. It is new policy outside this repair, and it would add errors to models that codegen handles.

## Architecture

```
design AttributeUsage + value expression
        │
        ├── is_expose_binding(attr, expr)   ← the one EXPOSE predicate (adr002.py); walk-free; never raises
        │
        ├── V2  check_static_expressions:       true static? → EXPOSE? → FORMULA? → else V2_DYNAMIC_EXPRESSION   (unchanged)
        ├── V4  check_supported_operators:      [existing skips] → EXPOSE? skip → extract_operators → V4 per unsupported op
        └── L6  check_design_attr_completeness: [existing filters] → no value? INCOMPLETE → EXPOSE? complete
                                                                   → else evaluate → UNEXTRACTABLE on failure
```

- **Boundary.** The predicate owns "is this an EXPOSE binding". Each check owns its scope filters and the rule it applies to non-EXPOSE expressions.
- **Data flow.** Each check calls the predicate once per attribute, passing the live `AttributeUsage` and its `feature_value_expression`. There is no shared state and no caching. The predicate reads only the chain's first member and two owners, so it is cheap.
- **Integration point.** `validate_architecture` (`level6_architecture.py:909`) does not change. It already runs all three checks over one loaded model.

## Required Invariants

1. **One predicate.** No check decides EXPOSE any other way. That means no `"."` string test and no ad hoc chain-type test for EXPOSE purposes. `_contains_feature_chain` (`adr002.py:510`) stays; it serves FORMULA exclusion, not EXPOSE.
2. **Every shared classification predicate fails closed.** It never raises, and on any analysis failure it returns `False`, so the check applies its normal rule. `is_expose_binding` meets this without walking references. A future FORMULA predicate needs the reference walk, so it must catch the walk's errors and return `False`.
3. **Unchanged boundary.** EXPOSE means: a top-level feature chain; the head resolves to a `CalculationUsage` or `PartUsage`; the head's owner is the attribute's owner. Chain length and the chain's final target are not constrained. Nothing else is EXPOSE.
4. **Non-EXPOSE behavior is unchanged.** Every non-EXPOSE expression gets the same diagnostics from all three checks as before. The controls fixture pins this.
5. **Shared utilities are untouched.** `extract_operators`, `SUPPORTED_OPERATORS`, `STATIC_OPERATORS`, and `evaluate_true_static_expression` do not change.
6. **The metric still counts.** An EXPOSE attribute counts toward "Design attrs checked".
7. **FORMULA is unchanged.** `tests/test_l8_extractability.py` passes unmodified, including the unextractable assertion on `area = length * width`.

## Component Overview

- **`is_expose_binding`** (`src/agentic_mbse/validation/adr002.py`, renamed from `_is_expose_pattern`). The single EXPOSE predicate. Its logic does not change. Its docstring is rewritten to state Invariant 3 exactly and names its three consumers (D4).
- **`check_static_expressions`** (`adr002.py:563`). Call-site update only. The catalog build at `:600` goes away with the parameter.
- **`check_supported_operators`** (`adr002.py:94`). Adds an EXPOSE guard before operator extraction. Its docstring says EXPOSE bindings are outside V4's scope.
- **`check_design_attr_completeness`** (`level6_architecture.py:475`). Adds an EXPOSE guard inside the has-value branch, before evaluation. Imports the predicate from `.adr002`.
- **Fixtures** (`tests/fixtures/l6_expose_consistency/{shapes,controls}/{library,designs}/`). Contents are in Appendix A.
- **Tests** (`tests/test_validation/test_l6_expose_consistency.py`, new). Covers the regression referent, `shapes/` and `controls/` through the combined route, and the predicate boundary. `tests/test_sysml/test_adr002.py` updates its imports, calls, and two test names for the rename.

## Non-Goals

- **FORMULA completeness.** Out of scope: completeness still rejects `area = length * width`, which V2 accepts as a supported FORMULA (`adr002.py:651-657`). The spec covers EXPOSE only, and `tests/test_l8_extractability.py:58` asserts the rejection. Follow-up path: extract V2's FORMULA condition into a fail-closed predicate beside `is_expose_binding` (Invariant 2), then add it to completeness's guard.
- **V4's `.` report on non-EXPOSE chains** (for example `d_calc.scaled * 0.95`). Out of scope: it is unchanged, because changing it would alter diagnostics on non-EXPOSE expressions (Invariant 4).
- **Dotted-path doc rows.** Out of scope: reconcile the dotted-path rows (`MODELING_GUIDE.md.template:57`, `adr002-calculations.md:44`, `common-mistakes.md:166`) and the one-hop advice (`plant-idiom.md:406-413`) with `plant-idiom.md:347` and the predicate boundary. Follow-up; these rows were already inconsistent before this fix.
- **Calc-usage binding spelling.** Out of scope: `in attribute x = source.result;` inside a calc usage still gets a V4 `.` error after this fix, because V4 does not skip calc-usage owners while V2 and completeness do. Follow-up.
- **Per-check scope selection.** Follow-up candidate: the remaining duplication across the three checks is in scope selection (the table in Research Findings), not classification.
- **Dead helpers.** Out of scope: `_get_calc_usage_names` (`adr002.py:310`) and `_is_calc_output_reference` (`adr002.py:342`) are left for a cleanup follow-up.
- **Spec Non-Goals.** New expression support, codegen behavior, and modeling-workflow changes.

## Implementation Notes

- **Signature:** `def is_expose_binding(attr: Any, expr: Any) -> bool`. The body is today's `_is_expose_pattern` body.
- **V4 guard placement:** after the existing calc-definition-owner, `library/`, and has-expression skips (`adr002.py:125-147`), and before `extract_operators` (`:150`).
- **Completeness guard placement:** inside `if has_value:` (`level6_architecture.py:530`), before `evaluate_true_static_expression`. Either `continue` or an `else` around the evaluator works, because the trailing `if not has_value:` (`:552`) cannot fire for an attribute that has a value. `attrs_checked` has already incremented by this point (`:521`), which satisfies Invariant 6.
- **Referent test with `design_path_filter=None`:** completeness also checks the library calc definition's own attributes under this filter, because it does not skip calc-definition owners. Expect `SimpleCalc::input_val` (incomplete) and `SimpleCalc::output_val` (unextractable). Scope the assertions in that test to `exposed_output` and `combined`.
- **Fixture naming:** each fixture directory uses its own package names. The calc output is named `scaled`, because `result` shadows `Performances::Evaluation::result` and produces a load warning. `first` is a SysML keyword and does not parse as an attribute name. Use the Appendix A text as given.
- **Assertions:** read `result.structured_issues` for codes and element names. Use `result.issues` for totals, because it also carries manifest strings.

## Potential Risks

- **R1. Docs and Level 6 disagree until the doc follow-up lands.** Level 6 will now pass part-headed and multi-hop sibling chains that the shipped modeling guide calls violations. V2 and codegen already accepted them, so behavior stays consistent and the docs are the outlier. Mitigation: the doc reconciliation is recorded in Non-Goals.
- **R2. The zero-issue assertion on `shapes/` could break when a future Level 6 check fires on it.** That is the intended signal, because an unrelated diagnostic would hide this result. Keep the fixture minimal so such a failure is easy to read.
- **R3. The divide-by-zero control depends on the evaluator raising** (`expression.py:555-559`). It is the only pure-static unextractable shape with no other diagnostic. If evaluator semantics change, swap it for a string default on a `String` attribute. A probe confirmed that shape fires only `L6_DESIGN_ATTR_UNEXTRACTABLE`.
- **R4. A library part-definition alias target escapes the value check (B4).** This is an edge case under ADR-002. It is recorded, not fixed here.

## Integration Strategy

There is no CLI, API, or metric-name change. Models that use EXPOSE bindings, including part-headed sibling relays, stop receiving the two false-positive errors at Level 6. Nothing else in their output changes. Target repos pick this up on their next toolkit update, with no migration or re-init. Existing tests stay green, except the two `test_adr002.py` predicate tests, which need the mechanical rename.

## Validation Approach

| Spec success criterion | Proof |
|---|---|
| Retained referent: no false positive, through the individual checks and the combined route in a checked design location | (1) Load `v2_expose_pattern.sysml` plus `library/simple_calc.sysml`. Run V2, V4, and completeness (`design_path_filter=None`). Assert that no issue names `exposed_output`, and that `combined` still gets V2, V4, and unextractable. (2) Copy both files into `tmp_path/designs/` and `tmp_path/library/`, run `validate_architecture(tmp_path)` with the default filter, and assert the same. |
| Both EXPOSE shapes stay accepted; arithmetic over a calc output stays rejected | `validate_architecture(shapes/)`: `success` is true, `issues == []`, and "Design attrs checked" is 3. That includes the part-headed `relayed` (D6). In the controls, `derated` gets `V2_DYNAMIC_EXPRESSION`. |
| Controls keep their diagnostics; no arbitrary dotted reference is admitted | `validate_architecture(controls/)`: a `Counter` of (code, element) over every structured issue equals the 13 pairs in Appendix B, each once. `len(result.issues) == 13`. `powered`'s V4 message names `^`. A parametrized predicate test returns `True` for `module_result`, `exposed_output`, and `relayed`, and `False` for `remote`, `payload_mass`, and `derated`. |

Then run the full gate: `uv run pytest tests/`, `uv run ruff check src/ tests/`, `uv run mypy src/`.

## Next-Stage Handoff

- **Fixed:** D1–D6, the fixture texts in Appendix A, and the expected results in Appendix B. FORMULA stays out of scope.
- **Open:** test names and helper structure inside the new test module. I recommend keeping the regression-referent tests in the new module rather than in `test_adr002.py`, so the spec's proof lives in one place.
- **Check first:** write the `controls/` `Counter` test before the guards. It should pass unchanged before and after the change, which is the direct proof of Invariant 4.

---
Next Step: `/_my_plan` (or `/_my_implement` directly; the change is small). C1 resolved to keeping the predicate unchanged, so the review's own guidance applies: the fold consists of verifiable wording and test-shape edits and does not need another design review. There is no `.project/adr/` register or `adr.sh` script, so no decision records are filed. D1, D2, and D6 would be the candidates if a register is added.

## Appendix A — Control fixtures (probe-verified)

Both directories passed Level 1 with zero errors and no load warnings under the live parser on 2026-10-04.

`tests/fixtures/l6_expose_consistency/shapes/library/expose_calc.sysml`
```sysml
package ExposeShapesLibrary {
    public import ScalarValues::*;
    calc def ScaleCalc {
        in attribute value : Real;
        out attribute scaled : Real = value * 2.0;
    }
}
```

`tests/fixtures/l6_expose_consistency/shapes/designs/expose_shapes.sysml`
```sysml
package ExposeShapesDesign {
    public import ScalarValues::*;
    public import ExposeShapesLibrary::*;

    // Shape A: EXPOSE on a part definition, instantiated so C4 stays quiet.
    part def ExposingModule {
        calc module_calc : ScaleCalc { in value = 3.0; }
        attribute module_result : Real = module_calc.scaled;
    }
    part module_instance : ExposingModule;

    // Shape B: EXPOSE on a part usage (the v2_expose_pattern.sysml shape).
    part expose_test_part {
        calc my_calc : ScaleCalc { in value = 10.0; }
        attribute exposed_output : Real = my_calc.scaled;
    }

    // Part-headed sibling chain: the head is a sibling part whose definition exposes a calc output.
    part relay_part {
        part sub_module : ExposingModule;
        attribute relayed : Real = sub_module.module_result;
    }
}
```

`tests/fixtures/l6_expose_consistency/controls/library/expose_calc.sysml`
```sysml
package ExposeControlsLibrary {
    public import ScalarValues::*;
    calc def ScaleCalc {
        in attribute value : Real;
        out attribute scaled : Real = value * 2.0;
    }
    item def Payload {
        attribute mass : Real = 1.0;
    }
}
```

`tests/fixtures/l6_expose_consistency/controls/designs/expose_controls.sysml`
```sysml
package ExposeControlsDesign {
    public import ScalarValues::*;
    public import ExposeControlsLibrary::*;

    part producer {
        calc producer_calc : ScaleCalc { in value = 4.0; }
    }

    // Invalid target: head is a calc-bearing part that is not a sibling.
    part remote_reader {
        attribute remote : Real = producer.producer_calc.scaled;
    }

    // Invalid target: head is a sibling item usage, not a calc or part usage.
    part item_head_reader {
        item payload : Payload;
        attribute payload_mass : Real = payload.mass;
    }

    // Arithmetic over a calc output: derived, not EXPOSE.
    part derived_part {
        calc d_calc : ScaleCalc { in value = 1.0; }
        attribute derated : Real = d_calc.scaled * 0.95;
    }

    part controls {
        attribute powered : Real = 2.0 ^ 3.0;   // unsupported operator
        attribute missing : Real;               // absent value
        attribute divzero : Real = 1.0 / 0.0;   // unextractable static default
    }
}
```

## Appendix B — Expected results

**`controls/`.** The combined route returns exactly these 13 (code, element) pairs, each once, both before and after the fix. `len(result.issues)` is 13 and "Design attrs checked" is 6. Element names are relative to `ExposeControlsDesign::`.

| Element | V2_DYNAMIC_EXPRESSION | V4_UNSUPPORTED_OPERATOR | L6_DESIGN_ATTR_UNEXTRACTABLE | L6_DESIGN_ATTR_INCOMPLETE |
|---|---|---|---|---|
| `remote_reader::remote` | ✓ | ✓ (`.`) | ✓ | |
| `item_head_reader::payload_mass` | ✓ | ✓ (`.`) | ✓ | |
| `derived_part::derated` | ✓ | ✓ (`.`) | ✓ | |
| `controls::powered` | | ✓ (`^`) | ✓ | |
| `controls::missing` | | | | ✓ |
| `controls::divzero` | | | ✓ | |

**`shapes/`.** Before the fix the combined route returns 6 issues: V4 `.` and unextractable on each of `ExposingModule::module_result`, `expose_test_part::exposed_output`, and `relay_part::relayed`. After the fix it returns none. "Design attrs checked" is 3 both times.

## Appendix C — Review dispositions

| Review item | Disposition |
|---|---|
| C1 part-headed chains | Kept the predicate's boundary (D6); stated in The Point and Core Concept; pinned by `relayed` in `shapes/`; doc reconciliation recorded in Non-Goals |
| M1 docstring overstates the boundary | D4: docstring rewritten to state Invariant 3 exactly |
| m1 controls assertion shape | D5 and Validation Approach: `Counter` over every structured issue, plus `len(result.issues) == 13` |
| m2 B2 fold-in | B1 and B2 restated as verified facts with codegen citations; Core Concept and D3 restated in alias terms; old R1, old Non-Goal, and the de-risk handoff removed |
| m3 alias-target bet | Added as B4 and R4 |
| m4 FORMULA must fail closed | Invariant 2 generalized; FORMULA Non-Goal references it |
| m5 scope-selection divergence | Research Findings table; two Non-Goal lines (calc-usage binding, scope selection) |
| m6 wrong `:1087` claim | Corrected in Research Findings |
| m7 D2 rejection reason | D2 now rests on Invariant 4 |
| m8 nice-to-haves | Test rename (D4); `^` assertion on `powered`; dead-helper Non-Goal |

# Design: L6 EXPOSE Validation Consistency

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-04 09:53 PDT
**Branch:** harness-right-size
**Commit:** 2d4b165
**Backlog Item:** L6-EXPOSE-CONSISTENCY

## Overview

Two Level 6 checks reject a pure EXPOSE binding (`attribute x : Real = my_calc.output_val`) that the static-expression check accepts. This design makes all three checks consult the one existing EXPOSE predicate, so the supported-operator check and the design-attribute completeness check stop reporting false positives on it, while every non-EXPOSE expression keeps its current diagnostics.

## Related Artifacts

- **Spec:** [spec.md](spec.md)
- **Product lens:** [product-lens.md](product-lens.md) (CLEAR)
- **Design brief:** [briefs/design.md](briefs/design.md)
- **Evidence:** [October 4 status report](../../reports/2026-10-04-0901-status-report.md#what-is-actually-broken-or-missing)
- **Pattern docs:** [expose-pattern.md](../../../docs/patterns/expose-pattern.md), [adr002-calculations.md](../../../docs/patterns/adr002-calculations.md)
- **Epic / Required Reading:** none (standalone backlog item)
- **Decision records:** no `.project/adr/` register exists in this repo, so there are no prior entries to cite.

## The Point

[INHERITED: product-lens.md, from docs/patterns/expose-pattern.md] A design attribute bound directly to a calculation output is a supported EXPOSE interface. Arithmetic over a calculation output is not; it stays rejected as a derived expression.

[INHERITED: spec] Today a modeler who follows the documented EXPOSE pattern gets two Level 6 errors for it (`V4_UNSUPPORTED_OPERATOR` for `.` and `L6_DESIGN_ATTR_UNEXTRACTABLE`). Level 6 is the codegen-readiness gate, so these errors tell the modeler their supported dataflow is broken when it is not. The obligation is to make validation agree with itself and with the documented pattern: accept exactly what the existing EXPOSE classification accepts, and reject everything else the way it is rejected today.

[INHERITED: spec] The repair is consistency. It adds no new expression support, does not change codegen, and does not change modeling workflows.

## Research Findings

**The three checks and what each does with `x = my_calc.output_val`:**

- Static-expression check (V2), `check_static_expressions` at `src/agentic_mbse/validation/adr002.py:563`. Walks references, then asks `_is_expose_pattern` (`adr002.py:389`) and accepts the binding (`adr002.py:644`). Correct today.
- Supported-operator check (V4), `check_supported_operators` at `adr002.py:94`. Calls `extract_operators` (`src/agentic_mbse/sysml/expression.py:98`) on every design attribute's expression. In SysIDE a feature chain is a subtype of operator expression with operator `.` (noted at `expression.py:318`), so the chain reports `.` and V4 flags it (`adr002.py:153`).
- Design-attribute completeness check, `check_design_attr_completeness` at `src/agentic_mbse/validation/level6_architecture.py:475`. Calls `evaluate_true_static_expression` (`expression.py:466`) on any value expression. That evaluator raises on any feature reference (`expression.py:506`), so the binding becomes `L6_DESIGN_ATTR_UNEXTRACTABLE` (`level6_architecture.py:538`).
- All three run in the combined route `validate_architecture` (`level6_architecture.py:976`, `:977`, `:992`).

**The completeness check already intends to accept EXPOSE.** Its docstring says "Validate design attributes have values or EXPOSE bindings" (`level6_architecture.py:480`), and its own incomplete-attribute suggestion says "bind to calc output" (`:561`). The code never implemented the binding half. This fix makes the code match its stated contract.

**The EXPOSE predicate is structural and cannot raise.** `_is_expose_pattern` (`adr002.py:389`) requires: the expression is a feature chain; the chain's first member resolves to a `CalculationUsage` or `PartUsage`; that head has the same owner as the attribute (a sibling). Any failure returns `False` (`adr002.py:480`). Its `calc_outputs` parameter is unused, and the catalog V2 builds at `adr002.py:600` exists only to feed it.

**The reference walk can raise.** `design_reference_uses` (`expression.py:83`) goes through `inspect_reference_uses` (`src/agentic_mbse/sysml/reference_use.py:291`). That walk raises `SemanticEvidenceError` for any function call other than `sum` (`reference_use.py:395`) and for unresolved targets (`:442`, `:475`). Every check swallows per-attribute exceptions (`adr002.py:170`, `adr002.py:683`, `level6_architecture.py:565`), so a raise silently drops that attribute's diagnostics.

**Live-parser probe (2026-10-04, scratch files under the gitignored `build/`, since deleted).** Run against the fixtures in the [Appendix](#appendix-a--control-fixtures-probe-verified):

- Both EXPOSE shapes (on a part definition, on a part usage) got `V4_UNSUPPORTED_OPERATOR` for `.` plus `L6_DESIGN_ATTR_UNEXTRACTABLE`. V2 was silent. This reproduces the reported defect on both shapes.
- With the EXPOSE verdict applied to V4 and completeness (simulated by filtering), the shapes fixture passed the combined route with zero issues, and the controls fixture produced the same 13 diagnostics as before the fix.
- A chain whose head is a non-sibling part, or a sibling item usage, is not EXPOSE by the predicate. It gets V2, V4, and unextractable, both before and after.
- Calc-usage parameter bindings (`in value = producer.exposed;`) parse as `ReferenceUsage`, not `AttributeUsage`. They never reach V4 or completeness, so they are not part of this defect.
- A part definition carrying a calc must be instantiated, or the calc-instantiation check (C4, `level6_architecture.py:693`) fires. The shapes fixture instantiates it.

**Callers and tests.** `extract_operators` has one production caller (V4). It is exported from `src/agentic_mbse/sysml/__init__.py:66` and unit-tested in `tests/test_sysml/test_expression.py:423`. `_is_expose_pattern` and `_build_calc_output_catalog` are imported by `tests/test_sysml/test_adr002.py:16-17`. The FORMULA rejection is pinned by `tests/test_l8_extractability.py:58`. The V4 `**` orchestrator test (`tests/test_sysml_quality_checks.py:1087`) uses a fixture with no chains and is unaffected.

**Fixture conventions.** Item 12 cases use `tests/fixtures/item12/<case>/library/` plus `<case>/designs/`, loaded per directory (`tests/test_validation/test_item12_checks.py:45`). The `l8_extractability` fixture uses `designs/` plus `tests/` to exercise the path filter.

**Codegen side.** [AGENT, verified by orchestrator 2026-10-04, per brief] sysml-codegen's `OutputAlias` (`sysml-codegen/src/sysml_codegen/resolution/models.py:243`) surfaces EXPOSE_PURE in shape A (part definition) and shape B (part usage). I could not read sysml-codegen in this session because access was denied. So I have not verified how codegen treats a part-headed chain (`x = sibling_part.attr`). See B2.

## Core Concept

EXPOSE is a structural fact about a design attribute's expression: the whole expression is one feature chain whose head is a sibling calculation or part usage. One predicate already decides this, and the static-expression check already uses it. The fix makes the other two checks ask the same predicate first. Their own rules are about static values, and an EXPOSE binding is not a static value. It is a wire to a calculation output channel.

- The supported-operator check polices arithmetic in static expressions. An EXPOSE binding contains no arithmetic, so it is outside that check's scope.
- The completeness check asks whether a design attribute has a value codegen can use. An EXPOSE binding is such a value, because codegen surfaces the output channel. It needs no numeric default.
- Anything that is not EXPOSE goes through each check exactly as it does today.

**The key insight:** the EXPOSE verdict is decided from the chain's head and its ownership, without the full reference walk. So it is the one classification every check can consume without inheriting the walk's failure modes. The other classifications (true static, FORMULA, derived) need that walk, and only V2 uses them. That is why the shared unit is the EXPOSE predicate and not a four-way classifier (D1).

**What this composes with.** The predicate stays where the ADR-002 rules live (`adr002.py`). Each check keeps its own context filters: calc-definition owners, `library/` paths, and `design_path_filter`. The operator extractor and the numeric evaluator stay untouched; they keep answering the questions they were built for.

## Key Bets

- **B1.** [AGENT, verified by orchestrator for shapes A and B] Codegen wires a pure EXPOSE design attribute through the calculation output channel, so the attribute needs no numeric default. *If false → completeness would stop flagging attributes codegen cannot extract, and Level 6 would pass models that fail in codegen.*
- **B2.** [INHERITED: spec] The existing predicate's boundary is the supported boundary for all three checks. That boundary includes the part-headed chain (`x = sibling_part.attr`), which V2 already accepts. Codegen support for that sub-shape is unverified in this session. *If false for the part-headed sub-shape → Level 6 would newly pass a part-headed chain that codegen rejects. Today it fails V4 and completeness. The right response is to narrow the one predicate, not to make the checks disagree.*
- **B3.** SysIDE resolves a chain's head member and its owner reliably enough to decide EXPOSE without the full reference walk. The live probe confirmed this on both shapes and on both invalid-head variants. *If false → the predicate would return `False` for valid EXPOSE bindings and the false positives would persist. That is a visible failure, not a silent one.*

## Key Decisions

- **D1. Share the EXPOSE verdict, not a four-way classification enum.** V4 and completeness each add one guard that consults the predicate. V2's existing decision sequence (true static → EXPOSE → FORMULA → derived, `adr002.py:640-681`) stays in V2. *Rejected: a `DesignExpressionKind` enum consumed by all three checks.* V4 and completeness only branch on EXPOSE. The other rungs need the reference walk, which raises on shapes such as `sqrt(2.0)`. Because every check swallows per-attribute exceptions, routing V4 and completeness through that walk would silently drop their diagnostics on those shapes. For example, `x = sqrt(2.0)` would lose its `L6_DESIGN_ATTR_UNEXTRACTABLE`. Making the enum safe would need a new "unclassifiable" kind, which is new policy. FORMULA can still be added to completeness later without restructuring (see Non-Goals).
- **D2. V4 skips EXPOSE bindings. `extract_operators` and `SUPPORTED_OPERATORS` stay unchanged.** *Rejected: removing `.` from `extract_operators`' output.* That changes a public, unit-tested utility. It would also silence V4 on every dotted path, including non-EXPOSE ones like `producer.producer_calc.result`, which admits a dotted reference merely because it contains `.`. *Rejected: adding `.` to `SUPPORTED_OPERATORS`.* That causes the same widening.
- **D3. Completeness treats an EXPOSE binding as complete before it tries to evaluate.** The attribute still counts toward "Design attrs checked". *Rejected: teaching `evaluate_true_static_expression` to accept chains.* It is a numeric evaluator, and an EXPOSE binding has no static number. Folding the two together would confuse "has a value codegen wires" with "has a numeric default".
- **D4. Rename the predicate to `is_expose_binding(attr, expr)`, keep it in `adr002.py`, and drop the unused `calc_outputs` parameter.** The predicate now crosses a module boundary into `level6_architecture.py`, which already imports from `.adr002`. With the parameter gone, `_build_calc_output_catalog` (`adr002.py:253`) has no caller left and is deleted. *Rejected: importing the private `_is_expose_pattern` across modules.* A private name used as a cross-module contract hides that it is one. *Rejected: moving it to `sysml/expression.py`.* It is ADR-002 policy, not a generic expression utility.
- **D5. Prove the fix through the combined route with two standalone fixture directories, plus the retained reproduction copied into a checked layout.**
  - `shapes/` must produce zero issues.
  - `controls/` must produce an exact, known set of (code, element) pairs.
  - The retained `v2_expose_pattern.sysml` is copied with its library into a temporary `designs/` + `library/` layout, so the referent itself runs through the combined route under the default filter.

  *Rejected: moving or duplicating the referent into a committed `designs/` path.* `tests/test_sysml/test_adr002.py` globs it at its current location. *Rejected: "contains" assertions on the controls.* They cannot prove that no unrelated diagnostic is hiding the result.

## Architecture

```
design AttributeUsage + value expression
        │
        ├── is_expose_binding(attr, expr)   ← the one EXPOSE predicate (adr002.py); structural; never raises
        │
        ├── V2  check_static_expressions:     true static? → EXPOSE? → FORMULA? → else V2_DYNAMIC_EXPRESSION   (unchanged)
        ├── V4  check_supported_operators:    [existing skips] → EXPOSE? skip → extract_operators → V4 per unsupported op
        └── L6  check_design_attr_completeness: [existing filters] → no value? INCOMPLETE → EXPOSE? complete
                                                                  → else evaluate → UNEXTRACTABLE on failure
```

- **Boundary.** The predicate owns "is this an EXPOSE binding". Each check owns its context filters and the rule it applies to non-EXPOSE expressions.
- **Data flow.** Each check calls the predicate per attribute with the live `AttributeUsage` and its `feature_value_expression`. No shared state, no caching. The predicate reads only the chain's first member and two owners, so it is cheap.
- **Integration point.** `validate_architecture` (`level6_architecture.py:909`) is unchanged. It already runs all three checks over one loaded model.

## Required Invariants

1. **One predicate.** No check decides EXPOSE any other way: no `"."` string test and no ad hoc chain-type test for EXPOSE purposes. `_contains_feature_chain` (`adr002.py:510`) stays; it serves FORMULA exclusion, not EXPOSE.
2. **Fail closed.** The predicate never raises. On any analysis failure it returns `False`, so the check applies its normal rule.
3. **Unchanged boundary.** A top-level feature chain; the head resolves to a `CalculationUsage` or `PartUsage`; the head's owner is the attribute's owner. Nothing else is EXPOSE.
4. **Non-EXPOSE behavior is unchanged.** Every non-EXPOSE expression gets the same diagnostics from all three checks as before. The controls fixture pins this.
5. **Shared utilities are untouched.** `extract_operators`, `SUPPORTED_OPERATORS`, `STATIC_OPERATORS`, and `evaluate_true_static_expression` do not change.
6. **The metric still counts.** An EXPOSE attribute counts toward "Design attrs checked".
7. **FORMULA is unchanged.** `tests/test_l8_extractability.py` passes unmodified, including the unextractable assertion on `area = length * width`.

## Component Overview

- **`is_expose_binding`** (`src/agentic_mbse/validation/adr002.py`, renamed from `_is_expose_pattern`). The single EXPOSE predicate. Its logic is unchanged. Its docstring loses the `calc_outputs` argument and names the three consumers.
- **`check_static_expressions`** (`adr002.py:563`). Call-site update only. The catalog build at `:600` goes away with the parameter.
- **`check_supported_operators`** (`adr002.py:94`). Adds an EXPOSE guard before operator extraction. The docstring states that EXPOSE bindings are out of scope for V4.
- **`check_design_attr_completeness`** (`level6_architecture.py:475`). Adds an EXPOSE guard inside the has-value branch, before evaluation. Imports the predicate from `.adr002`.
- **Fixtures** (`tests/fixtures/l6_expose_consistency/{shapes,controls}/{library,designs}/`). Contents are in Appendix A.
- **Tests** (`tests/test_validation/test_l6_expose_consistency.py`, new). Covers the regression referent, the shapes and controls through the combined route, and the predicate boundary. `tests/test_sysml/test_adr002.py` updates its imports and calls for the rename.

## Non-Goals

- **FORMULA completeness.** Completeness still rejects `area = length * width`, which V2 accepts as a supported FORMULA (`adr002.py:651-657`). This is out of scope because the spec covers EXPOSE only, and `tests/test_l8_extractability.py:58` asserts the rejection. Follow-up path: extract V2's FORMULA condition into a predicate beside `is_expose_binding`, then add it to completeness's guard.
- **V4's `.` report on non-EXPOSE chains** (for example `d_calc.result * 0.95`) is unchanged. It duplicates the V2 signal, and changing it would widen V4.
- New expression support, codegen behavior, and modeling-workflow or documentation changes. These are spec Non-Goals.
- Verifying codegen's handling of part-headed chains. Tracked as B2 and R1, not resolved here.

## Implementation Notes

- **Signature:** `def is_expose_binding(attr: Any, expr: Any) -> bool`. The body is today's `_is_expose_pattern` body.
- **V4 guard placement:** after the existing calc-definition-owner, `library/`, and has-expression skips (`adr002.py:125-147`), before `extract_operators` (`:150`).
- **Completeness guard placement:** inside `if has_value:` (`level6_architecture.py:530`), before `evaluate_true_static_expression`. `attrs_checked` has already incremented by then, which satisfies invariant 6.
- **Package names:** use distinct names per fixture directory (`ExposeShapesLibrary`, `ExposeControlsLibrary`, and so on) so the two directories never collide if loaded together.
- **Reserved word:** `first` is a SysML keyword. The probe's first attempt failed to parse with it as an attribute name. Use the Appendix text as given.
- **Assertions:** read `result.structured_issues` for codes and element names. Assert `result.issues == []` for the shapes fixture, which covers manifest strings too.
- **Scratch probe:** files under `build/` were used for research and deleted. Nothing in the repo depends on them.

## Potential Risks

- **R1. Part-headed EXPOSE may be unsupported in codegen (B2).** Mitigation: verify in sysml-codegen before implementing (see Next-Stage Handoff). If codegen rejects it, stop and surface the conflict. Do not narrow only V4 and completeness, because that recreates the inconsistency.
- **R2. The zero-issue assertion on `shapes/` could break when a future L6 check fires on it.** That breakage is the point: an unrelated diagnostic would hide this result. Keep the fixture minimal so such a failure is easy to read.
- **R3. The divide-by-zero control depends on the evaluator raising at `expression.py:556`.** It is the only pure-static unextractable shape with no other diagnostic. If evaluator semantics change, swap it for another isolated unextractable literal, such as a string default on a `String` attribute (`attribute label : String = "abc";`). The probe confirmed that shape fires only `L6_DESIGN_ATTR_UNEXTRACTABLE`.

## Integration Strategy

No CLI, API, or metric-name change. Models that use the documented EXPOSE pattern stop receiving the two false-positive errors at Level 6, and nothing else in their output changes. Target repos pick this up on their next toolkit update. No migration or re-init is needed. Existing tests stay green except the two `test_adr002.py` predicate tests, which need the mechanical rename.

## Validation Approach

| Spec success criterion | Proof |
|---|---|
| Retained reproduction: no false positive, through the individual checks and the combined route in a checked design location | (1) Load `v2_expose_pattern.sysml` + `library/simple_calc.sysml`. Run V2, V4, and completeness (`design_path_filter=None`). Assert no issue names `exposed_output`, and that `combined` still gets V2, V4, and unextractable. (2) Copy both files into `tmp_path/designs/` and `tmp_path/library/`, run `validate_architecture(tmp_path)` with the default filter, and assert the same. |
| Both pure EXPOSE shapes stay accepted; arithmetic over a calc output stays rejected | `validate_architecture(shapes/)`: `success` is true, `issues == []`, "Design attrs checked" == 2. Controls: `derated` gets `V2_DYNAMIC_EXPRESSION`. |
| Controls keep their diagnostics; no arbitrary dotted reference is admitted | `validate_architecture(controls/)`: the set of (code, element) pairs over the four affected codes equals the 13 pairs in Appendix B, and no other code appears. A parametrized predicate test: `True` for `module_result` and `exposed_output`; `False` for `remote`, `payload_mass`, and `derated`. |

Then run the full gate: `uv run pytest tests/`, `uv run ruff check src/ tests/`, `uv run mypy src/`.

## Next-Stage Handoff

- **Fixed:** the shared unit is the EXPOSE predicate (D1). V4 changes in the check, not the extractor (D2). Completeness accepts EXPOSE as complete (D3). The rename and parameter drop (D4). The fixture layout and expected sets (D5, Appendix). FORMULA stays out of scope.
- **Open:** test names and helper structure inside the new test module. Whether to fold the regression-referent tests into `tests/test_sysml/test_adr002.py` next to the existing EXPOSE tests or keep them in the new module. I recommend the new module, so the spec's proof lives in one place.
- **De-risk first:** confirm in sysml-codegen that a part-headed chain (`x = sibling_part.attr`) is classified and surfaced as EXPOSE_PURE (R1/B2). It is a read-only check. If it fails, surface it to the owner before implementing.

---
Next Step: `/_my_design_review` in a fresh session, then `/_my_plan` (or `/_my_implement` directly; the change is small). There is no `.project/adr/` register or `adr.sh` script, so no decision records are filed. D1 and D2 would be the candidates if a register is added.

## Appendix A — Control fixtures (probe-verified)

Both directories passed Level 1 with zero errors under the live parser on 2026-10-04.

`tests/fixtures/l6_expose_consistency/shapes/library/expose_calc.sysml`
```sysml
package ExposeShapesLibrary {
    public import ScalarValues::*;
    calc def ScaleCalc {
        in attribute value : Real;
        out attribute result : Real = value * 2.0;
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
        attribute module_result : Real = module_calc.result;
    }
    part module_instance : ExposingModule;

    // Shape B: EXPOSE on a part usage (the v2_expose_pattern.sysml shape).
    part expose_test_part {
        calc my_calc : ScaleCalc { in value = 10.0; }
        attribute exposed_output : Real = my_calc.result;
    }
}
```

`tests/fixtures/l6_expose_consistency/controls/library/expose_calc.sysml`
```sysml
package ExposeControlsLibrary {
    public import ScalarValues::*;
    calc def ScaleCalc {
        in attribute value : Real;
        out attribute result : Real = value * 2.0;
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
        attribute remote : Real = producer.producer_calc.result;
    }

    // Invalid target: head is a sibling item usage, not a calc or part usage.
    part item_head_reader {
        item payload : Payload;
        attribute payload_mass : Real = payload.mass;
    }

    // Arithmetic over a calc output: derived, not EXPOSE.
    part derived_part {
        calc d_calc : ScaleCalc { in value = 1.0; }
        attribute derated : Real = d_calc.result * 0.95;
    }

    part controls {
        attribute powered : Real = 2.0 ^ 3.0;   // unsupported operator
        attribute missing : Real;               // absent value
        attribute divzero : Real = 1.0 / 0.0;   // unextractable static default
    }
}
```

## Appendix B — Expected controls diagnostics

The combined route on `controls/` returns exactly these 13 (code, element) pairs, both today and after the fix. "Design attrs checked" is 6. Elements are relative to `ExposeControlsDesign::`.

| Element | V2_DYNAMIC_EXPRESSION | V4_UNSUPPORTED_OPERATOR | L6_DESIGN_ATTR_UNEXTRACTABLE | L6_DESIGN_ATTR_INCOMPLETE |
|---|---|---|---|---|
| `remote_reader::remote` | ✓ | ✓ (`.`) | ✓ | |
| `item_head_reader::payload_mass` | ✓ | ✓ (`.`) | ✓ | |
| `derived_part::derated` | ✓ | ✓ (`.`) | ✓ | |
| `controls::powered` | | ✓ (`^`) | ✓ | |
| `controls::missing` | | | | ✓ |
| `controls::divzero` | | | ✓ | |

Before the fix, `shapes/` returns four issues: V4 `.` and unextractable on `ExposingModule::module_result` and on `expose_test_part::exposed_output`. After the fix it returns none.

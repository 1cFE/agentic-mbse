# Audit: L6 EXPOSE Validation Consistency

**Verdict:** Certify
**Audited:** 2026-10-04 — independent second pass requested by owner
**Branch:** harness-right-size
**Commit:** 86ea739; implementation 3f442ce

---

## The Point

[INHERITED: spec.md; docs/patterns/expose-pattern.md] A modeler following the documented EXPOSE pattern should not receive architecture errors for a design attribute bound directly to a calculation output. Previously, V2 accepted that binding, but V4 reported an unsupported `.` operator and completeness demanded a numeric static default. This repair makes those checks share the existing EXPOSE classification. Arithmetic over calculation outputs and other non-EXPOSE expressions retain their diagnostics.

[AGENT] (ratified by orchestrator 2026-10-04, design D6) The existing classification includes whole feature chains headed by a sibling calculation usage or part usage, without a chain-length or terminal-target restriction. The owner requested independent scrutiny of this decision and its documentation cost; this audit does not regrade D6 as owner-originated.

## Summary

The implementation satisfies all three success criteria and follows the design with two small guards and a shared predicate. Independent live-parser probes confirm deep sibling chains and the recorded library-source completeness limitation. Certification covers the specified consistency repair; it does not certify universal alias-source completeness or the contradictory documentation as correct.

## Product Judgment

**This is the right piece of work within the stated scope.** Direct calc-output EXPOSE now passes both affected checks, and exact negative controls still fail. The fresh-context product lens derived its oracle from product documentation before reading implementation; its lower-authority findings are explicitly disposed in the appended [ledger block](product-lens.md).

**D6 is defensible and should stand for this repair.** An AST comparison against `3f442ce^` proves that the renamed predicate's executable body is identical. A fresh three-member `p = subsystem.rotor.power` model passes full L6 with no issues. Codegen creates aliases for references/chains and resolves their exact target (`/home/reid/1cfe/sysml-codegen/src/sysml_codegen/elaboration/elaborate.py:982`, `:2511`), independently of whether the leaf is a calc output or an ordinary attribute. Its conformance tests verify part-definition aliases and cross-package alias-to-producer resolution (`/home/reid/1cfe/sysml-codegen/tests/conformance/test_elaboration_expose_shapes.py:268`, `:339`). These codegen files were read, not executed. Narrowing the predicate would introduce new V2 policy beyond this repair.

**The documentation conflict remains real.** `project_templates/MODELING_GUIDE.md.template:57`, `docs/patterns/adr002-calculations.md:44`, and `docs/patterns/common-mistakes.md:166` call dotted paths violations, while `docs/patterns/plant-idiom.md:347` supports nested-part EXPOSE. Prior V2 acceptance and codegen's alias implementation support D6, but do not make those guide rows accurate. Disposition: preserve the recorded boundary and carry documentation reconciliation as follow-up. No owner-grade or external HARD source requires narrowing it.

**Structural smells were checked and disposed.** The sibling-head exemption applies to ordinary part values too; that is the inherited alias policy, not proof of a calc-output leaf. Runtime-class matching and owner identity are existing parser dependencies (`src/agentic_mbse/validation/adr002.py:366`, `:415`); live-parser controls and the AST comparison support preserving them here. Manual synchronization remains between docs and policy and between the checks' scope filters; both are recorded follow-ups. The adjacent inline-FORMULA completeness contradiction is pre-existing and explicitly excluded (`design.md:181`, `tests/test_l8_extractability.py:58`). No duplicate-output or route-selection smell was found: the regression exercises individual checks and the combined route, and controls compare every issue.

## Findings

### Plan completion

All four implementation phases are verified against the committed diff, fixtures, tests, and current checks. The red-test history remains historical evidence in `plan.md`; this pass did not replay the pre-fix suite. Recorded deviations concern comments/docstrings, import formatting, and correction of the red-test count; no unrecorded production behavior change was found.

The full gate's historical green pytest result could not be reproduced exactly: this pass returned **1,931 passed, 1 skipped, 33 deselected, 1 failed**. The failure is `tests/test_packaged_guidance_contract.py:47`: `uv build` cannot fetch `hatchling` because DNS resolution fails. A separate build reproduced that infrastructure error before building the wheel. This is not evidence of an L6 regression; wheel packaging remains unverified in this pass.

### Spec conformance

- **SC1 — verified.** The retained referent is checked individually and after copying into a default-filter `designs/` layout (`tests/test_validation/test_l6_expose_consistency.py:75`, `:85`). Assertions require no issue on `exposed_output` and exactly four retained diagnostics on arithmetic `combined`, proving the checks ran.
- **SC2 — verified.** Full L6 returns zero issues and counts three design attributes on part-definition, part-usage, and sibling-part relay shapes (`tests/test_validation/test_l6_expose_consistency.py:102`). Calculation-output arithmetic retains V2, V4, and unextractable diagnostics (`:49`, `:115`).
- **SC3 — verified.** Controls assert all 13 diagnostic pairs and the total count, including unsupported `^`, absent values, division by zero, non-sibling heads, and item heads (`tests/test_validation/test_l6_expose_consistency.py:115`). Boundary tests reject arithmetic too (`:146`).
- **[INHERITED] Existing classification defines the boundary — met.** Predicate executable-body AST is unchanged; the unused catalog parameter and builder were removed (`src/agentic_mbse/validation/adr002.py:339`).
- **[INFERRED] An EXPOSE binding needs no numeric static default — met.** Completeness counts the attribute, then skips numeric evaluation for EXPOSE (`src/agentic_mbse/validation/level6_architecture.py:523`, `:535`).
- **Non-goals — respected.** The implementation commit changes no expression utilities, codegen implementation, modeling workflows, or product guidance.

### Design conformance

D1–D6 and all seven invariants hold. One predicate has exactly three production callers. V4's guard follows existing filters and precedes operator extraction (`src/agentic_mbse/validation/adr002.py:153`, `:585`); completeness guards evaluation after incrementing its metric (`src/agentic_mbse/validation/level6_architecture.py:523`, `:536`). The predicate fails closed, its documented boundary matches its executable body, and shared utilities and FORMULA behavior are unchanged.

**Advisory: source completeness is not guaranteed for library part attributes.** A fresh probe with `part sub : LibPart; attribute aliased : Real = sub.unset;`, where unset `LibPart::unset` is declared in `library/`, passes L6 without issues. The equivalent source declared in `designs/` gets `L6_DESIGN_ATTR_INCOMPLETE`. Completeness filters the source declaration by path and skips the alias (`src/agentic_mbse/validation/level6_architecture.py:511`, `:536`). This confirms recorded B4/R4 (`design.md:109`, `:203`), rather than an undisclosed implementation deviation. A later readiness item should decide how required values on referenced library parts are verified; alias classification alone does not prove a source value exists.

**Advisory: persist deep-chain coverage in the boundary/docs follow-up.** The committed positive relay has two authored members (`tests/test_validation/test_l6_expose_consistency.py:151`). D6's three-or-more-member claim is supported here by a scratch live-parser probe and unchanged code, not a retained regression test. Add a retained deep sibling-chain case in that follow-up. This audit did not draft or implement a fix.

### Code integrity

No new abstraction, utility-policy, parameter-sprawl, or silent-success fallback problem was found. The predicate's existing broad catch returns `False`, leaving the normal checks active (`src/agentic_mbse/validation/adr002.py:423`); the explorer independently confirmed this with an exception-raising object. Existing outer exception handling and divergent scope filters remain outside this small change. The deleted catalog has no remaining consumer, and no placeholder implementation was introduced.

---

## Certification

Checked: spec, design, review dispositions, plan, implementation diff, fixture/test assertions, independent product lens, live-parser deep-chain and missing-source probes, unchanged predicate AST, and codegen alias source/documentation. A fresh-context explorer independently found no in-scope blocker and ran the focused selection: **51 passed, 1 skipped**.

| Independent check | Result |
|---|---|
| Default pytest suite | 1,931 passed; 1 skipped; 33 deselected; one wheel-build infrastructure failure |
| Ruff on four touched Python files | Clean |
| New test module format | Clean |
| Repository Ruff | 118 errors; below recorded baseline of 119 |
| Repository format | 78 files would reformat; matches baseline |
| Repository mypy | 91 errors in 19 files; matches baseline |
| Mypy in affected validation modules | Same three pre-existing errors at `adr002.py:31` |

Marked: all three spec criteria and plan phases remain checked. Spec/plan status identifies this independent certification. Updated the item's CURRENT_WORK and backlog status and preserved other ongoing work. Appended a product-lens block with explicit dispositions. No implementation changes were made.

**Not checked:** isolated wheel packaging (build dependency unavailable due DNS), the 33 slow corpus tests, execution of sysml-codegen tests or generated packages, real consumer repositories beyond fixtures, universal alias-source value completeness, and repair of contradictory guide rows or adjacent FORMULA/scope-selection issues. The pre-fix suite was not rerun; its predicate body was compared directly.

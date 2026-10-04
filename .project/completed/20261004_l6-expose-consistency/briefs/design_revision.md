# Resume: design — fold in review and orchestrator decisions

The fresh-session review is at `.project/active/l6-expose-consistency/design-review.md`. Verdict: Revise. Read it in full, then revise `design.md`. Mechanism (D1–D5) stands; the review verified it independently. Changes below.

## Orchestrator decisions (execution-detail tier, [AGENT]; owner gave no reserved gates)

**B2 / R1 is verified and closed.** In sysml-codegen, `docs/architecture/reference/16-computed-attributes.md` states any feature reference or feature chain in a design attribute value becomes an alias node resolved by exact occurrence identity; `tests/conformance/test_elaboration_expose_shapes.py` proves part-headed, multi-hop, and cross-package chains reach their producer. Codegen's supported shape is wider than our predicate. Rewrite B1/B2 as verified facts with that citation, drop R1, and fix the Core Concept / D3 wording that says "calc output channel" so it covers a part-headed alias too (an EXPOSE binding is an alias to an upstream value; codegen resolves it by occurrence identity).

**C1 → option (a): keep the predicate's boundary.** Reasoning to record in the design, graded [AGENT] (ratified by orchestrator 2026-10-04, not owner-originated, reversible in one place):
- The spec's inherited requirement names the existing classification as the supported boundary. V2 has accepted part-headed and multi-hop sibling chains all along; codegen accepts them; `docs/patterns/plant-idiom.md:347` documents them as supported.
- Narrowing the predicate (option b) would change V2's accepted set, which is new policy and outside this repair.
- The three doc rows calling `= a.b.c` a violation (`project_templates/MODELING_GUIDE.md.template:57`, `docs/patterns/adr002-calculations.md:44`, `docs/patterns/common-mistakes.md:166`) are inconsistent with V2, codegen, and plant-idiom.md today, before this fix. That is a pre-existing doc defect. Record it in Non-Goals as a follow-up ("reconcile the dotted-path rows with plant-idiom.md and the predicate boundary"), one line, decision-record phrasing, no instruction to future agents.
- State the wider boundary plainly in The Point / Core Concept so nobody reads the design as calc-head-only. Add one part-headed sibling case to the `shapes/` fixture as accepted (e.g. a sibling part exposing a calc output, and an attribute `x = sibling_part.exposed`), and update the shapes expectations ("Design attrs checked" count, zero issues). Keep the fixture minimal.

## Must-fix from the review

- **M1.** Rewrite the predicate docstring at rename time to match Invariant 3 exactly: top-level feature chain; head resolves to a sibling `CalculationUsage` or `PartUsage`; same owner; chain length unconstrained; no single-target or "transitive EXPOSE" claims that the code does not check.
- **Controls assertion.** Compare a `Counter` (or sorted list) of (code, element) over *every* structured issue, equal to the 13 expected pairs each once, plus `len(result.issues) == 13`. Drop the "over the four affected codes" phrasing.
- **Invariant 2 generalised.** State "never raises; fail closed to False" as the rule for every shared classification predicate (the future FORMULA predicate cannot be walk-free and must catch the walk's errors).
- **Correct the wrong claim** about `tests/test_sysml_quality_checks.py:1087`: its fixture directory does include `v2_expose_pattern.sysml`; the test still passes because it asserts `>= 1` V4 issues and a `**` message.
- **Follow-up note (Non-Goals):** `in attribute x = source.result;` bindings inside a calc usage still receive a V4 `.` error after this fix because each check selects its attributes differently (V4 does not skip calc-usage owners; V2 and completeness do). One line; out of scope.
- **Implementer note:** with `design_path_filter=None`, completeness also checks the library calc def's own attributes; the referent test must scope its assertions to `exposed_output` and `combined`.
- Record the review's observation that the remaining duplication is in per-check scope selection, not classification, as a known follow-up candidate.

Keep the design in the working voice (plain, one idea per sentence, one line per paragraph). Update Status to reflect review incorporated. Finish with the ARTIFACT line.

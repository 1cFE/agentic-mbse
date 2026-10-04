# Brief: design_review — l6-expose-consistency

Review `.project/active/l6-expose-consistency/design.md` against `spec.md` in the same folder. The design brief that produced it is `briefs/design.md`. You are a fresh session; the design author is not you.

## Intent (orchestrator, provenance marked)

[INHERITED: spec] Three L6 checks classify the same design-attribute expression; two reject a pure EXPOSE binding the third accepts. The repair is consistency with the existing EXPOSE boundary, with no widening and no new expression support.

[AGENT, orchestrator-verified 2026-10-04] The design's bet B2 / risk R1 is resolved: in sysml-codegen, `docs/architecture/reference/16-computed-attributes.md` states that any feature reference or feature chain in a design attribute value becomes an alias node resolved by exact occurrence identity, and `tests/conformance/test_elaboration_expose_shapes.py` proves part-headed, multi-hop, and cross-package chains reach their producer. Codegen's supported shape is therefore wider than our predicate, not narrower. Treat B2 as verified; do not spend review effort re-raising it. The author will fold this into the design.

## What I want from the review

Hold the engineering bar, not just the artifact checklist. Specifically pressure-test:

1. **D1 (share the predicate, not a four-way classifier).** The brief asked for one place that owns the classification; the author argued that a shared classifier would inherit the reference walk's raise-and-swallow failure mode and silently drop diagnostics. Is that reasoning sound, and is the resulting shape still "policy lives in one place" for the question the two repaired checks actually ask? Would a thin seam (predicate now, FORMULA predicate later beside it) hold up, or is it a half-step that leaves duplication?
2. **D4 (rename + drop `calc_outputs` + delete `_build_calc_output_catalog`).** Confirm from the code that the parameter and catalog really have no other consumer, including tests (`tests/test_sysml/test_adr002.py` imports both names).
3. **D5 and the controls table (Appendix B).** Are the 13 expected pairs actually the right controls for the spec's third success criterion, and does an exact-set assertion over four codes prove "no unrelated diagnostic hides the result" through the combined route? Check whether `validate_architecture` runs manifest checks or other L6 checks that could fire on these fixtures.
4. **Invariant 2 (predicate never raises).** Verify against `_is_expose_pattern`'s body (`adr002.py:389`) that every path is inside the try/except and returns bool.
5. **Guard placement.** For V4, check the EXPOSE guard sits after the existing skips and does not change behaviour for calc-def-owned or `library/` attributes. For completeness, check that `attrs_checked` increments before the guard (invariant 6) and that an EXPOSE attribute with `design_path_filter` excluded is still skipped.
6. Anything the design asserts about the parser that you can disprove by reading the code or the existing fixtures.

Must-fix items only need to be must-fix if they would cause wrong behaviour, a silent diagnostic drop, a test that cannot prove what it claims, or an architectural smell the implementer would have to work around. Keep nice-to-haves clearly separated.

Produce `.project/active/l6-expose-consistency/design-review.md`.

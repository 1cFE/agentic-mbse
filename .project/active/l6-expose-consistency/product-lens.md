## spec — 2026-10-04 — rev .project/active/l6-expose-consistency/spec.md

Point (re-derived): Pure design attributes bound directly to calculation outputs are supported EXPOSE interfaces; arithmetic on calculation outputs remains rejected. [source: docs/patterns/expose-pattern.md; docs/patterns/adr002-calculations.md, grade: INHERITED]
Falsifier: The spec permits L6 to reject a valid pure EXPOSE binding or accept calculation-output arithmetic as EXPOSE.
Findings:
- None.
Gate: CLEAR

## design — 2026-10-04 — rev .project/active/l6-expose-consistency/design.md

Lens provenance: `~/.claude/scripts/product-lens.md` and the pack source were permission-denied in this session, so the lens subagent ran the fallback procedure from the design-review brief (derive the point independently, falsifier, graded findings, gate).

Point (re-derived): A design attribute bound directly to one sibling calc output is a supported EXPOSE, on a part definition or a part usage, and it surfaces as an output. Arithmetic over a calc output, self-reference, and dotted paths that reach into another part are rejected. [source: docs/patterns/expose-pattern.md:152-175; docs/patterns/adr002-calculations.md:39,43-44,113-116,241-245; docs/patterns/common-mistakes.md:164-166, grade: INHERITED]
Falsifier: The work keeps Level 6 rejecting either documented EXPOSE shape, or lets arithmetic over a calc output pass, or makes Level 6 pass a design attribute the docs list as a failing dotted path.
Findings:
- DO [INHERITED: expose-pattern.md:170-171]: Both documented shapes (part def, part usage) are accepted through the combined route; `shapes/` asserts zero issues (design.md:160, :195-206).
- DO [INHERITED: expose-pattern.md:173-175; adr002-calculations.md:43]: Arithmetic over a calc output stays rejected; `derated` keeps V2, V4 `.`, and unextractable before and after (design.md Appendix B).
- DO [INHERITED: spec.md:27]: No change to modeling workflows, docs, or codegen (design.md:132).
- DON'T [INHERITED: adr002-calculations.md:44,116,208,244; common-mistakes.md:166; project_templates/MODELING_GUIDE.md.template:57]: The design makes the Level 6 gate pass dotted paths the docs call failures. The predicate accepts any top-level chain whose head is a sibling calc or part usage, whatever the chain length or leaf (adr002.py:424-478). Today Level 6 still fails these because V4 and completeness fire on every chain; after the design, `attribute p : Real = subsystem.rotor.power;` inside the part that owns `subsystem` passes with zero diagnostics, as does `x = sibling_part.attr`. The design treats part-headed chains only as a codegen question (B2/R1), does not cite the docs' FAIL rule, and pins no part-headed or multi-hop shape in a control or predicate test (design.md:161). This is a conflict between two INHERITED sources (the code predicate and the pattern docs) that spec.md:22 merged by citing both as one boundary.
- CAN'T-FIND [INHERITED]: No doc defines a part-headed design-attribute EXPOSE. The predicate docstring calls it "transitive EXPOSE" under an "ADR-002 amendment" (adr002.py:395-408) that no doc contains. Only plant-idiom.md:347 says multi-hop EXPOSE through a nested part is supported, with no syntax; that conflicts with adr002-calculations.md:44 and with plant-idiom.md:406-413 ("keep cross-part references to one hop").
Gate: CLEAR

Reviewer disposition (design-review, 2026-10-04): the DON'T finding is INHERITED-grade, so it does not force Rework, but it is a premise conflict under capture-fidelity law 4. Escalated as **C1 (decision required)** in `design-review.md`. Reviewer verified every citation and reproduced the effect by probe (`sub.lit`, `sub.out_v`, and `inner.c.result` go from V4 `.` + unextractable to zero diagnostics). Reviewer recommendation is [AGENT]-grade: keep the predicate boundary and record a docs-alignment follow-up. The decision itself belongs to the owner.

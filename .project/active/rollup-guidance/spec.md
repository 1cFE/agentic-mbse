# Spec: Rollup guidance

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-25
**Complexity:** LOW
**Branch:** rollup-guidance

---

## Premise conflict (for the owner)

The brief asks the guidance to state that the two-term same-name rollup (`sum(panel.capital_cost) + sum(caster.capital_cost)`) is refused with `SI_RENDERING_COLLISION`. On sysml-codegen main `e6c20bca` it is not refused. It builds, and the generated code keeps the panel and caster inputs apart (probe p3 in [evidence/probes.md](evidence/probes.md)). sysml-codegen's own test for it is `test_a_two_term_same_name_rollup_keeps_both_resolved_source_families` (`tests/integration/test_costed_component_exact_route.py:324`), which asserts the build succeeds. The test the brief names, `test_a_two_term_same_name_rollup_is_refused`, does not exist on main.

The source of the wrong claim is sysml-codegen's `docs/architecture/modeling-assumptions.md` § 4, which still says the form is refused and names that missing test. The fixture's own doc comment (`tests/fixtures/costed_cart_d5/library.sysml:17-23`) already says named intermediates are "no longer required".

This spec follows the tools, per the owner's standing goal: the guidance does not state the refusal and has no wrong-way example for it. Named intermediates are taught as optional. Fixing § 4 belongs to sysml-codegen, which is out of scope here.

## Problem

The toolkit's only costing example is `sum(child.capital_cost)` over identical children (`docs/patterns/adr002-calculations.md:176-200`). It is a fragment, marked "parser-validated" only, and `tests/test_validation/test_tool_examples.py` does not run it. The same fragment is copied in `docs/patterns/mbse-concepts.md:121-134` and `:246-256`. A modeler costing a real assembly (children of different kinds, several levels) gets no working shape, and dc3 dropped the toolkit's costing pattern for that reason (dc3 WI-008 design P6, P8). The generator supports more than the docs show.

[OWNER] 2026-10-25: fix this with a complete, tested rollup example in `docs/patterns/adr002-calculations.md`, plus a short paragraph in `project_templates/MODELING_GUIDE.md.template` and `skills/sysml-conventions/SKILL.md`, all marked so both tools run them.

[OWNER] standing goal, 2026-10-23 ([P-0007](../../product/0007-shipped-examples-run-both-tools.md)): the shipped guidance teaches what the tools actually do, and every complete shipped example is marked and run through both tools.

## Success Criteria

- [ ] `docs/patterns/adr002-calculations.md` has one complete costed rollup example, marked `<!-- @tool-example -->`, that shows every behaviour in the table below marked "marked example".
- [ ] Under `SYSML_CODEGEN=/home/reid/src/sysml-codegen/.venv/bin/sysml-codegen uv run --env-file .env pytest tests/test_validation/test_tool_examples.py`, every test passes: the 121 that pass today plus the new example's validate and check cases. The check output for the new example reports more than 0 modules.
- [ ] The old fragment and its "Parser-validated" status block are gone from `adr002-calculations.md`, not kept beside the new example.
- [ ] `MODELING_GUIDE.md.template` and `sysml-conventions/SKILL.md` each carry a short rollup paragraph that links to the new section, and every complete fence in them is marked.
- [ ] No shipped file states that the two-term same-name rollup is refused, or that the generator needs the rollup in `library/`.

### Behaviours the guidance states, and how each is verified

| behaviour | verified by |
|---|---|
| `sum()` over a group with an exact count (`part panel : Panel[4];`) adds one term per child occurrence | marked example; probe p2 generated body has four terms |
| children of different kinds, one of each, can be read directly in one expression (`rail.capital_cost + brace.capital_cost`) | marked example; probes p2, p3 |
| two `sum()` terms reading the same-named attribute off different groups also build | probe p3; sysml-codegen test above. The marked example may show it (design choice) |
| a named intermediate per child role (`panel_capital = sum(panel.capital_cost)`) works and is optional, useful for readability and a separately inspectable module | probe p2; sysml-codegen fixture `Deck Assembly` |
| rollups nest: an assembly adds its sub-assemblies' rolled-up values, three levels deep | marked example; probe p2 |
| put the rollup on a part def in `library/`, because validate level 6 rejects `sum()` over children in `designs/` (`V2_DYNAMIC_EXPRESSION`, `V4_UNSUPPORTED_OPERATOR`, `L6_DESIGN_ATTR_UNEXTRACTABLE`); the generator builds it in either place | probes p4a-p4e |

## Known Requirements

- **[HARD]** The marked example includes at least one part usage of the top assembly. A file of definitions only passes `sysml-codegen check` by building 0 modules (probe p1), so it would prove nothing about the generator.
- **[HARD]** The marked example is one fence that parses on its own or in the test's standard wrapper, because the test writes each fence to one file under one folder (`test_tool_examples.py`, `write_models`). Probe p2 is such a file: one `library/` file with the usage at the end, no validate errors, 15 modules.
- **[HARD]** The guidance does not state the `SI_RENDERING_COLLISION` refusal or carry a `fails="SI_RENDERING_COLLISION"` example (probe p3; see the premise conflict above). This replaces the brief's [AGENT] request for one.
- **[HARD]** The guidance repeats no § 4 condition as a generator rule unless a probe shows it holds. Probed: the `library/`-only condition does not hold for the generator (p4a-p4e); it holds for validate only, and the guidance attributes it to validate.
- **[NEED]** The guide and skill paragraphs are short ([OWNER] "a short paragraph").
- **[INFERRED]** The guide and skill paragraphs point to the pattern doc section rather than restating the example, so the example has one home.
- **[INFERRED]** The guidance claims only what is verified. The example test checks build or refuse, not numbers; any claim about computed totals cites sysml-codegen's arithmetic tests (`test_the_deck_rollup_sums_its_four_panels_and_the_allocation`, the two-term test above) rather than implying our test checks them.
- **[INFERRED]** The copies of the old fragment in `docs/patterns/mbse-concepts.md` (§ "Cost Aggregation Over Multiplicities" and the "Using hardcoded values instead of sum()" mistake) are replaced by a pointer to the new section. This is a fourth file beyond the three the owner named. [AGENT] I included it because leaving it keeps a second, incomplete costing example, which the standing goal rules out. Drop it if the owner wants the change kept to the three named files.

## Non-Goals

- dc3 and sysml-codegen are out of scope ([OWNER]). That includes the stale § 4 in `modeling-assumptions.md`; it is reported here for the owner to route.
- Changing validate's level 6 rules. Out because the item is guidance only.
- The design-file taxonomy row in `skills/sysml-conventions/SKILL.md:80` ("dotted path `= a.b.c`: VIOLATION"). Probes p4b, p4c and p4e saw validate accept a bare dotted child reference in `designs/`. Whether that row is wrong, or validate is missing a check, is a separate question; out because this item is about rollups in `library/`.

## Open Questions / Deferred to design

- Which shape the main example shows for same-kind groups: per-role named intermediates (the fixture's shape) or the direct `sum(a.x) + sum(b.x)` form, or both. Both build.
- Whether to add a wrong-way example for `sum()` in `designs/` (`dir="designs" fails="V2_DYNAMIC_EXPRESSION"`), or state the rule in prose only.
- How the example presents the usage line, since in a real project it belongs in `designs/` but the test puts one fence in one folder (a comment saying so is one option).
- Whether the "hardcoded placeholder" anti-pattern fragment stays in `adr002-calculations.md`.
- Whether the example test should fail a marked example whose check builds 0 modules. Recommend a separate item; it changes the test, not the guidance.

---

## Related Artifacts

- **Brief:** `.project/active/rollup-guidance/briefs/spec.md`
- **Evidence:** `.project/active/rollup-guidance/evidence/probes.md` (probes p1-p4e, models and tool output beside it)
- **Source of truth read:** sysml-codegen `e6c20bca`: `tests/fixtures/costed_cart_d5/library.sysml`, `docs/architecture/modeling-assumptions.md` § 4 and § 6, `tests/integration/test_costed_component_exact_route.py`
- **Consumer:** `/home/reid/src/dc3/work/completed/20261024_WI-008_generator-idiom/design.md` (cited by the brief; not re-read for this spec)
- **Product-lens:** not run. The brief limits this stage to writing the spec and its evidence folder, and the product-lens writes `product-lens.md`.
- **Design:** `.project/active/rollup-guidance/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.

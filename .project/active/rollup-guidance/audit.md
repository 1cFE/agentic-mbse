# Audit: Rollup guidance

**Verdict:** Needs Work
**Audited:** 2026-10-25
**Branch:** rollup-guidance
**Commit:** d2f441a3

---

## The Point

The toolkit's only costing example was a fragment, `sum(child.capital_cost)` over identical children, that no tool ran. A modeller costing a real assembly (children of different kinds, several levels deep) got no working shape, and dc3 dropped the toolkit's costing pattern for that reason (dc3 WI-008 design P6, P8). The owner asked for one complete, tested rollup example in `docs/patterns/adr002-calculations.md`, plus a short paragraph in `MODELING_GUIDE.md.template` and `skills/sysml-conventions/SKILL.md`. The standing goal ([P-0007](../../product/0007-shipped-examples-run-both-tools.md)) is that shipped guidance teaches what the tools actually do, and every complete example runs through both tools.

## Summary

The main cart example is correct. I re-ran it through both tools, and every claim about what the generator does with it holds: four terms per `sum()`, panel and caster inputs kept apart, named totals each becoming a module, and the same rollup building in `designs/`. Two things the text tells the modeller are not what the tools do. First, the "Where the rollup goes" rule describes validate wrongly for the form the example itself teaches. Second, the generator refuses any model with two of the same sub-assembly (a group like `Deck[2]`, or two named `Deck` parts), which is dc3's case (`racks[2]`, each with its own servers), and nothing in the guidance says so.

## Product Judgment

This is the right piece of work, and most of it is done well. But the owner's test for it is "a modeller with dc3's shape gets a working shape", and on that test it falls short. A modeller who follows "let each level add the totals of the level below" and puts two racks in a facility gets a clean validate and a generator refusal (must-fix 2). That is a premise conflict with the item's goal, not a polish issue, so it should go to the owner. The product-lens subagent was not run: my brief limited writes to this file, and the lens writes `product-lens.md`.

## Blockers

Ranked must-fix. Each one is a sentence in shipped guidance that disagrees with what a tool does.

**1. Validate does not reject the taught form in `designs/`.** `docs/patterns/adr002-calculations.md:260` says that in a `designs/` file validate level 6 rejects a `sum()` over child parts with `V2_DYNAMIC_EXPRESSION`. That is true only for a newly declared attribute (`attribute capital_cost : Real = sum(...)`), which is what the wrong-way example at `:271` uses. The example above it teaches the redefinition form (`:>> capital_cost = sum(...)`), and validate accepts that form in `designs/` with no error:

- The whole cart example under `designs/`: no `V2_DYNAMIC_EXPRESSION`, no `V4_UNSUPPORTED_OPERATOR` (only `V1_CALC_DEF_LOCATION` and `L6_DESIGN_ATTR_*` for the calc def and leaf inputs).
- Leaves in `library/`, the `Deck` part def with `:>> capital_cost = sum(panel.capital_cost) + sum(caster.capital_cost)` plus its usage in `designs/`: validate clean, check builds 9 modules.
- A minimal `Axle :> Costed { part wheel : Wheel[2]; :>> capital_cost = sum(wheel.capital_cost); }` in `designs/`: no V2/V4 errors.

Impact: a modeller who moves the taught `Deck` into `designs/` sees no error, so the doc's "this is validate's rule" is wrong as stated. Either validate is missing a check for redefinitions, or the rule only covers declared attributes. What should change: state what validate actually checks (declared attributes, which includes the optional named-total form), or surface the gap to the owner as a validate question. The guide and skill paragraphs (`MODELING_GUIDE.md.template:124`, `SKILL.md:149`) say "put the rollup in `library/`" without a reason, which is still fine as advice.

**2. Two of the same sub-assembly is refused by the generator, and the guidance is silent.** Starting from the cart example, each of these passes validate with no errors and fails `sysml-codegen check` (exit 1) with `REGISTRY_CLASS_NAME_COLLISION ... (grandparent collision): 'Deck_capital_costModule' <- ['cartcosting.deck.capital_costModule', 'cartcosting.deck.capital_costModule']`:

- `part deck_assembly : Deck[2];` with `sum(deck_assembly.capital_cost)` in `Cart`.
- The same `Deck[2]` with `Cart` not reading it at all (so the cause is the second occurrence, not the sum).
- Two named singletons, `part deck_assembly : Deck; part spare_deck : Deck;`, read directly.
- Two named `Frame` parts (the same fault on `Frame_capital_costModule`).
- The named-total form with two decks (three colliding modules).
- A plain facility model: `Rack { part servers : Server[3]; :>> capital_cost = sum(servers.capital_cost); }`, `Facility { part racks : Rack[2]; :>> capital_cost = sum(racks.capital_cost); }`, one usage.

Leaf groups (`Panel[4]`) are fine because a leaf's `capital_cost` is a plain binding to its calc output, not a generated module. Impact: dc3's case (P8: `racks[2]`, each rack holding named servers) is exactly this shape, so the item's stated goal is not met. A modeller following the guide's "let each level add the totals of the level below" hits an unexplained refusal. What should change: surface it to the owner as a premise conflict (it is a sysml-codegen limit or bug, out of scope to fix here), and have the guidance state the limit. If it is shown as a wrong-way example, note that `test_tool_examples.py` only treats codes starting `SI_` or `block_` as generator codes, so `fails="REGISTRY_CLASS_NAME_COLLISION"` would be looked for in validate's output and fail. The test needs a change, or the limit stays in prose.

## Advisory

Ranked should-fix, then notes.

**3. Should-fix: the guide and skill paragraph sits under a heading about refusals.** `MODELING_GUIDE.md.template:124` and `skills/sysml-conventions/SKILL.md:149` put "Costing an assembly" inside "Three Structures the Code Generator Refuses" (`:63` and `:88`). A rollup is something the generator builds, so a reader scanning headings will either miss it or read it as a fourth refusal. Move it under its own short heading or next to the calculation architecture section.

**4. Should-fix: the arithmetic citation reads broader than the test.** `adr002-calculations.md:256` says `test_the_deck_rollup_sums_its_four_panels_and_the_allocation` "checks the arithmetic of a rollup like `Deck`". That test runs the fixture's deck, which names each group's total and adds an allocation cost (`4x45 + 4x90 + 110 = 650`). It does not run the direct `sum(a) + sum(b)` form the example teaches. The two-term test cited at `:248` checks input wiring and that the package builds and verifies, not numbers. I generated the cart example and its `Deck` body is `(panel_0 + ... + panel_3) + (caster_0 + ... + caster_3)`, so the form is correct, but no cited test computes it. Say "the fixture's deck, which names each group's total" so the reader does not assume the direct form's numbers are pinned.

**5. Note: the wrong-way example's generator claim is prose only.** `:260` says the generator would build the rollup in `designs/`. That is true (the wrong-way example builds 1 module; the whole cart example under `designs/` builds 13, the same as in `library/`). But `test_example_under_generator_check` asserts nothing for an example whose `fails` codes are all validate codes, so no test keeps this claim true.

**6. Note: dc3's other shapes are not covered.** The guide covers named singletons of different kinds (direct reads), same-kind leaf groups and nesting through singletons. It does not say whether `sum()` works over a `[*]` library collection whose count is fixed by redefinition in a specializing def (dc3 P8's `part :>> racks[2]`), or over named parts that subset a collection. My one probe of the redefinition shape hit the same collision as finding 2, so I could not test it on its own.

## Findings Detail

### Plan completion

No plan or design: design, plan and spec review were skipped as a guidance-only item (commit 17523379). The implement brief settled the spec's open questions. All six decisions there are followed: direct form shown with one named-total sentence (`:252`), one wrong-way `designs/` example (`:262`), usage line with a comment (`:240`), placeholder anti-pattern reduced to one sentence (`:254`), backlog row `TOOL-EXAMPLE-ZERO-MODULES` added, and both `mbse-concepts.md` fragments replaced by pointers (`:123`, `:237`).

### Spec conformance

- SC1, one complete marked example showing every "marked example" behaviour: met. Exact-count `sum()`, direct reads of different kinds, and three-level nesting are all in the fence at `:178-243`.
- SC2, all example tests pass and check reports more than 0 modules: met. 125 passed; the cart example builds 13 modules. `tests/test_validation` overall: 580 passed.
- SC3, old fragment and "Parser-validated" block gone: met.
- SC4, guide and skill paragraphs link to the section, every complete fence marked: met (the marker test passes). See finding 3 on placement.
- SC5, no shipped file says the two-term rollup is refused or that the generator needs `library/`: met. Grep of `docs`, `skills`, `agents`, `project_templates` found no such statement. The existing `library/` statements (`adr002-calculations.md:45`, `:154`, `SKILL.md:81`, the guide's item 3) all attribute the rule to validate.
- [HARD] usage in the example: met (`part cart : Cart;`).
- [HARD] one fence that loads on its own: met.
- [HARD] no `SI_RENDERING_COLLISION` refusal stated: met.
- [HARD] no section 4 condition repeated as a generator rule unless probed: met for the generator. The attribution to validate is overbroad (finding 1).
- [NEED] short paragraphs: met (two sentences each).
- [INFERRED] paragraphs point to the section rather than copying the example: met.
- [INFERRED] numeric claims cite sysml-codegen's arithmetic tests: met in form, overbroad in wording (finding 4).
- [INFERRED] `mbse-concepts.md` copies replaced: met.
- Non-goals respected: no changes to dc3, sysml-codegen, validate rules, or the `SKILL.md:80` dotted-path row.

### Design conformance

No design document. Checked against the implement brief's decisions instead (see Plan completion).

### Code integrity

No code changed. The new prose is plain and short and follows `working-voice.md` and one-line paragraphs.

---

## Certification

Checked, against the tools directly:

- `SYSML_CODEGEN=... uv run --env-file .env pytest tests/test_validation/test_tool_examples.py -q`: 125 passed.
- sysml-codegen at `e6c20bca` (clean tree): both cited tests exist at `tests/integration/test_costed_component_exact_route.py:295` and `:324`, ran, and passed (licensed, not skipped). Each asserts what the text says, with the scope caveat in finding 4.
- Cart example in `library/`: validate clean, check builds 13 modules. Generated `Deck` body adds four panel and four caster terms under separate names.
- Named-total variant: 15 modules; `panel_capital_impl.py` and `caster_capital_impl.py` appear as their own modules. "Each named total becomes its own generated module" holds.
- Whole cart example in `designs/`: check builds 13 modules. "The generator would build the same rollup in `designs/`" holds.
- Wrong-way example wrapped in `designs/`: validate reports exactly `V2_DYNAMIC_EXPRESSION`, `V4_UNSUPPORTED_OPERATOR`, `L6_DESIGN_ATTR_UNEXTRACTABLE`, as stated; check builds 1 module.
- Library defs with the usage in a separate `designs/` file (the layout the comment at `:240` tells a project to use): validate clean, 13 modules.
- `[1..4]` instead of `[4]`: check refuses with `SI_MULTIPLICITY_UNSUPPORTED`, so "the count must be exact" holds.
- The redefinition-form and duplicate-sub-assembly probes in findings 1 and 2.

Probe models and tool output are in `/tmp/claude-1000/-home-reid-src-agentic-mbse/9366fe1c-453c-484d-b30e-782bbdd1390c/scratchpad/audit/` (A-F, C2-C4, G-G9). That folder is temporary; the shapes that matter are written out in findings 1 and 2.

Spec checkboxes, `CURRENT_WORK.md` and `product-lens.md` were not updated: my brief limited writes to this file.

**Not checked:** computed numbers for the direct form beyond reading the generated body; quantity-typed costs; a count given by an `Integer` attribute; why the duplicate-sub-assembly collision happens inside sysml-codegen (I only showed when it fires); whether validate's acceptance of `:>> x = sum(...)` in `designs/` is intended; the product-lens pass; rendering of the guide's reference-style link `[patterns/adr002-calculations.md]` (an existing convention in that template, not new here).

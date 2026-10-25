# Rollup probes, 2026-10-25

Run against sysml-codegen main `e6c20bca` (`/home/reid/src/sysml-codegen/.venv/bin/sysml-codegen`) and agentic-mbse branch `rollup-guidance` (base `eecfac3f`). Scratch copies lived under `/tmp/claude-1000/.../scratchpad/probes/`; each folder here holds the probe's `models/`, the full `check.txt`, and `validate-errors.txt` (validate's ERROR-severity issues plus each level's status).

`run.sh` is the runner as used (its paths point at the scratch folder). It runs the same two commands as `tests/test_validation/test_tool_examples.py`: `agentic-mbse validate --complete --execution-target=generated --json-report=...` and `sysml-codegen check --models ...`. For p2 and p3, `sysml-codegen generate` was also run with `.env` loaded, and the generated rollup function bodies are in `generated-returns.txt`.

The base model (p2) is a three-level cart: four leaf part defs (`Panel`, `Caster`, `Rail`, `Brace`) each costed by one calc usage; `Deck` sums four panels and four casters; `Frame` adds two singleton children of different kinds; `Cart` adds the two assemblies; one bare usage `part cart : Cart;`.

| probe | what changed from p2 | validate errors | check |
|---|---|---|---|
| p1 | no part usage at all (defs only) | none | exit 0, "builds (0 modules)" |
| p2 | base: `Deck` uses per-role named intermediates, `Frame` and `Cart` reference children directly, all in `library/` | none | exit 0, 15 modules |
| p3 | `Deck` writes `:>> capital_cost = sum(panel.capital_cost) + sum(caster.capital_cost);` directly | none | exit 0, 13 modules; generated body adds all eight occurrences, panel and caster inputs kept distinct |
| p4a | the whole p2 file under `designs/` | 13, incl. `V1_CALC_DEF_LOCATION`, `V2_DYNAMIC_EXPRESSION`, `V4_UNSUPPORTED_OPERATOR`, `L6_DESIGN_ATTR_UNEXTRACTABLE` | exit 0, 15 modules |
| p4b | leaf and sub-assembly defs in `library/`; `Cart` part def with direct child references, plus the usage, in `designs/` | none | exit 0, 15 modules |
| p4c | as p4b, but the rollup sits on a `designs/` part usage, not a part def | none | exit 0, 15 modules |
| p4d | `Deck` (with its two `sum()` intermediates) and its usage in `designs/` | `V2_DYNAMIC_EXPRESSION` x2, `V4_UNSUPPORTED_OPERATOR` x2, `L6_DESIGN_ATTR_UNEXTRACTABLE` x2 | exit 0, 11 modules |
| p4e | as p4b, but `Cart` names dotted intermediates (`deck_capital = deck_assembly.capital_cost`) | none | exit 0, 15 modules |

What this shows:

- The generator builds every rollup form tried, in `library/` or `designs/`. None gave `SI_RENDERING_COLLISION`.
- Validate level 6 rejects `sum()` over child parts in `designs/`. It did not reject a bare dotted child reference (`deck_assembly.capital_cost`) in `designs/`, on a part def or a part usage.
- A defs-only file passes `sysml-codegen check` by building nothing, so it says nothing about whether the generator handles the rollup.

Not checked: computed numbers (sysml-codegen's own `test_the_deck_rollup_sums_its_four_panels_and_the_allocation` and `test_a_two_term_same_name_rollup_keeps_both_resolved_source_families` cover arithmetic); quantity-typed costs; a count given by an `Integer` attribute rather than a literal (`[4]`); any form that still raises `SI_RENDERING_COLLISION`.

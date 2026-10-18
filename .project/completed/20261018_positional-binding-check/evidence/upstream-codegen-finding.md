# DRAFT upstream finding for sysml-codegen: calculation inputs wired by declared name, not by position

**Status: DRAFT, UNFILED.** Written in agentic-mbse only, for the owner (or Item 2's agent) to route. Nothing has been written in sysml-codegen. This draft proposes no change to how either route binds (gate R4-2).

**Written:** 2026-10-18, EXEC-SUBSET-CONTRACT Item 4 (`.project/active/positional-binding-check/`). Linked from the register entry `docs/patterns/semantic-hazards.md#positional-input-binding`.

## Summary

For a calculation usage whose unprefixed inputs are written in a different order from the definition, sysml-codegen `b5663c07` wires each input to the definition parameter with the same declared name. Native SysIDE 0.8.4 binds the same inputs by position, as KerML `checkFeatureParameterRedefinition` says. The two routes then compute different values for one model: generated 7, native -7.

## The case

```sysml
calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
// usage, inputs reversed and unprefixed; big = 10, small = 3
calc c : Sub { in b = small; in a = big; }
```

| Fixture (agentic-mbse) | Native SysIDE 0.8.4 | Generated, codegen `b5663c07` + TEAx `8d877460` | Generated wiring |
|---|---|---|---|
| `tests/fixtures/positional_binding/native_values/gen_byname/` | 7 | 7 | `a` from `big`, `b` from `small` |
| `tests/fixtures/positional_binding/native_values/gen_reversed/` | -7 | 7 | `a` from `big`, `b` from `small` |

- Native values: `tests/test_validation/test_positional_binding_native_values.py` (SysIDE `Compiler.evaluate_feature`). Natively, in `gen_reversed`, `b` lands on `Sub::a` and `a` lands on `Sub::b`.
- Generated values and wiring: `.project/active/positional-binding-check/evidence/cross-route/eval_generated.log`, produced by `eval_generated.py` beside it. Both sysml-codegen `b5663c07` and TEAx `8d877460` were exported with `git archive` and imported from the exports, with dc3's interpreter. The same result was first seen by the prototype (`.project/concepts/convince-me-exec-subset/evidence/04-eval.log`).
- Positional reading on the parser side, per input: `tests/fixtures/positional_binding/prototype/calc_reversed.sysml` and the learning tests in `tests/learning/test_syside_input_redefinition.py`.

Not traced: which sysml-codegen code site does the by-name wiring. The observation is the wiring the generated package printed.

## Why it matters

- A passing generated run says nothing about native correctness for such a model. For the reversed case the generated route computes what the author meant, and the native model computes something else.
- Real trees carry the shape. fusion-tea `f96ad312` has 125 positional mismatches whose value effect is unknown (`.project/active/positional-binding-check/evidence/run-trees.md`). dc3 recorded the same native swap in its own learnings (`dc3@60b44d5:work/learnings/RAW_LEARNINGS.md`, line 29).
- agentic-mbse now reports these inputs at validate level 2 (`L2_POSITIONAL_BINDING`). The check does not depend on how this finding is resolved.

## Relation to POSITIONAL-FORMAL-REDEFINITION, and a conflict to resolve

sysml-codegen's backlog entry POSITIONAL-FORMAL-REDEFINITION (`sysml-codegen@b5663c07:.project/backlog/BACKLOG.md`, line 21, as corrected by `bd352744`) says: "Current elaboration follows parser redefinition identity." It also says the August 21 filing's "name-matching/positional-codegen premise is superseded; it does not establish a binding defect."

The case above conflicts with that text. The parser's redefinition for `gen_reversed` is positional (`b` redefines `Sub::a`), and following it would give -7. The generated route gives 7 by wiring by name. Both statements cannot describe this case. Either elaboration does not follow parser redefinition identity for calculation usages, or the observed wiring comes from a path the backlog text does not cover. The codegen owner decides which is right.

sysml-codegen's fixture notes also record that constraint actuals bind positionally there (`sysml-codegen@b5663c07:tests/fixtures/modeled_default_fidelity/PROVENANCE.md`, "Authoring note — formal order is load-bearing"). So the divergence is claimed for calculation usages only; constraint usages were not run through both routes.

## A related observation in agentic-mbse's fact layer (for the owner and Item 2's agent)

agentic-mbse Item 1's constraint facts record, for each constraint-usage actual, `ActualFact.formal_targets`, read from `owned_redefinitions`. SysIDE lists implied (positional) redefinitions there too, and the fact carries no implied or explicit mark. So a consumer of `formal_targets` gets the native positional reading. On all six constraint fixtures this item checked, `formal_targets` equals the full target set the positional check reads (`tests/test_sysml/test_parameter_redefinition_extraction.py`, D21 test). That agrees with native SysIDE; for calculation usages it would disagree with codegen's by-name wiring above. Item 4 changes neither module.

## What is asked

Only that the codegen owner record which reading sysml-codegen intends for unprefixed calculation-usage inputs, and reconcile the POSITIONAL-FORMAL-REDEFINITION text with the observed wiring. No binding change is proposed here.

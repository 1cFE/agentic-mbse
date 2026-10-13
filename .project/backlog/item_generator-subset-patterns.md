# GENERATOR-SUBSET-PATTERNS — capture, teach and enforce the patterns a consumer project hit

**Status**: [AGENT] Filed 2026-10-13 at owner request ("file a ticket in its backlog to make sure these patterns are captured, known and enforced"). Priority not assigned.
**Origin**: consumer project dc3, goal `study-ready-baseline`, work item WI-008. The project rewrote an audited native SysML comparison so sysml-codegen `b5663c07` could generate it, with agentic-mbse `8b027bbc` and SysIDE 0.8.4.
**Evidence** (dc3 is a local repository; paths are cited at its commit `67d5d7b`):
- `work/learnings/RAW_LEARNINGS.md`: 10 dated entries.
- `models/README.md` § "Generated package and generator constraints (WI-008)".
- `.project/active/toolkit-upstream-findings.md`: U1-U7.
- `work/active/WI-008_generator-idiom/{design,review,audit}.md`.
- `work/orchestration/goals/study-ready-baseline/{learnings.md,evidence/T-001-blocker-inventory.md}`.

## Problem

agentic-mbse's validator, pattern docs and skills let a modeler write a fully native-valid model that passes L1-L6 and then fails generation one construct at a time. One semantic rule, positional parameter binding, produced a silent wrong-value risk that neither validation nor skill guidance mentions. The patterns that worked exist only in the consumer project.

## 1. Positional binding of calc-usage inputs (the most important)

- **What happens.**
  - KerML (`docs/sysmlv2/SysML_KerMLSpec/full_document.md`, about line 5234) says a parameter of a Step redefines its type's parameter **at the same position**. A calc usage is a Step.
  - So `calc c : D { in b_in = y; in a_in = x; }` binds D's first parameter `a_in` to `y`.
  - SysIDE confirms it: an `a − b` probe returned −7 instead of 7. Each usage input's `owned_redefinitions[].redefined_feature` is the positional parameter, not the same-named one.
  - Name-based binding checks pass the swap. sysml-codegen refuses some swaps (`cross_scope_binding_disagreement`) but not all.
- **Capture.**
  - A section in `docs/patterns/plant-idiom.md`, beside the authoritative calculation-binding rule, and in `docs/patterns/semantic-operators.md`: input order is semantic.
  - The by-name alternative `in :>> b_in = y;` should be verified with SysIDE and the generator before it is recommended.
- **Know.** Add a one-line rule to the `sysml-conventions` skill and to the modeling-guide template.
- **Enforce.** A validation check, L2 or L3 like `L2_SELF_NAMED_BINDING`, that fails when a calc-usage or constraint-usage input's implied redefinition targets a differently named parameter. This is reproducible from the dc3 evidence: the mutation tests in `tests/models/test_engineering_costs.py` and the out-of-order domain probe in the WI-008 audit (P4).

## 2. The generator's executable subset is not visible before generation

The constructs below pass L1-L6 (or pass with only some flagged) and are then refused by the generator. They appeared one per run, and a T-001 inventory needed stub-and-retry probing to find them all.

| Construct | Generator refusal | Working pattern (proven in dc3) |
|---|---|---|
| `assert constraint` owned by a calc def **or calc usage** | `SI_CONSTRAINT_UNATTACHED` | Part-owned assertion on the part that owns the calc usage. Binding the same source as the calc input is required, because a guard cannot bind `calc.input` (`SI_OCCURRENCE_MISSING`) |
| Boolean attributes / Boolean constraint inputs | L6 `NON_NUMERICAL` / `MALFORMED_NUMERICAL` | Numeric margin plus a `>= 0` assertion |
| `product`, `size`, `min`/`max`, `if … ? … else` | `SI_EXPRESSION_SOURCE_UNSUPPORTED` / `SI_EVIDENCE_INCOMPLETE` | Explicit fixed-arity products; `min(a,b) = (a+b−((a−b)^2)^0.5)/2`, with parity to about 1e-15 at dc3 magnitudes |
| `Real[0..*] ordered nonunique` calc inputs | `SI_MULTIPLICITY_UNSUPPORTED` | Fixed-arity calc defs with named inputs |
| `[*]` collections instantiated by designs | `SI_MULTIPLICITY_UNRESOLVED` | The library keeps `[*]`; the design states exact counts (`part :>> racks[2] { … }`) |
| A named subset nested inside a named subset | `SI_REDEFINITION_INVALID` (incomparable value writers) | One level of named subsetting; inner named parts do not subset, and the inner collection is `[0]` |
| Composition by subsetting a top-level usage (`part facility :> ac_facility`) | `SI_OCCURRENCE_MISSING` | The configured assembly becomes a specialized `part def`, typed by the composing usage |
| String design attributes | Silently dropped; L6 flags only the `attribute :>> x = "…"` spelling | Keep as native metadata, out of calculations |

- **Capture.** A pattern doc, for example `docs/patterns/generator-subset.md`, with the table above and links to the sysml-codegen fixtures. Revisit as `[CALCDEF-GATE-IMPLEMENTATION]` and `[SCALAR-FUNCTION-VOCABULARY]` land in sysml-codegen.
- **Know.** The `sysml-conventions`, `design-model`, `implement-model` and `quick-model` skills should point to it whenever a model is meant to be generated.
- **Enforce.** L6 ("Architecture & Pipeline Readiness") should report every row above, all at once and with locations, so readiness agrees with what the generator refuses. Today L6 passes calc-usage-owned asserts, `product`/`size`/conditionals, sequence inputs, unresolved multiplicities, nested subsets and usage-subsetting composition. It also flags the two String spellings inconsistently.

## 3. Notes for evaluator authors (SysIDE 0.8.4)

- A constraint definition's parameters have `name == None` in `.features`. Use the usage's owned bindings.
- `ExactReferenceUse.path` segments are facts carrying element ids, not nodes, and `model.nodes(...)` does not enumerate inherited or redefined features. Resolve by `authored_segments`.
- A named subset occurrence exposes both the library `[*]` collection feature and the design's `[0]` redefinition. Topology walkers must skip both as templates.
- An output cannot be overridden with `:>>` (load error: feature-value-overriding). Only an attribute can shadow it.

**Capture:** a short reference section, for example in `docs/patterns/adr002-calculations.md` or a new evaluator-authoring note.

## 4. Process gap: expert agents were not consulted

During this work the shipped `kerml-expert`, `sysml-expert` and `syside-expert` agents were never invoked. All delegation went to general-purpose agents, and the positional rule was found empirically by a mutation test instead of from the spec. The `run-goal` and modeling-stage skills could name when a semantics question (binding, redefinition, multiplicity) must go to `kerml-expert` or `sysml-expert` before a model or evaluator change.

## Done when

1. The pattern docs carry § 1 and § 2, with verified examples.
2. Skills reference them.
3. A validator check enforces § 1, with tests that include the swapped-input probe.
4. L6 reports each § 2 construct before generation, tested against the sysml-codegen refusals.
5. The § 4 dispatch guidance is in the skills.

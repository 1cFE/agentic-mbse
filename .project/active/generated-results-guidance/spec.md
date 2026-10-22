# Spec: Guidance that keeps generated results honest (EXEC-SUBSET-CONTRACT Item 5, rescoped)

**Status:** Draft (product lens DISPOSED, findings F1-F5 folded in)
**Owner:** Reid Westwood
**Created:** 2026-10-22
**Complexity:** MEDIUM
**Branch:** agentic-mbse `generated-results-guidance` (worktree `/home/reid/src/subset-conformance/agentic-mbse`, base `4eed77d5`, the `retire-subset-profile` close, in PR #35)

---

## Problem

Since ADR 0004, a model the generator refuses is cheap: the workflow runs `sysml-codegen check` early, the refusal is loud, and the fix is rework on a small model. The remaining risk is a model that passes `check`, generates, and gives numbers that differ from the native model, or a package whose failed checks nobody reads. That failure looks like success. [AGENT] (ratified by owner, 2026-10-22: "agreed", in answer to the four-risk proposal below.)

Four risks, in order of harm:

1. **Patterns that generate but compute something different.** Known instances: a part count given by a redefined `default` builds the default count (sysml-codegen backlog `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]`, 2 parts instead of 3); String values and some calc-usage result expressions are left out of a built package without a report (`[SILENT-LOSSES-UNREPORTED]`); calculation inputs written out of order bind by position natively and by name in the generator, giving native −7 and generated 7 on one model (agentic-mbse `.project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md`, still a draft that was never filed; sysml-codegen's `[POSITIONAL-FORMAL-REDEFINITION]` says the premise does not establish a defect, so the two records disagree). `check` cannot see any of these. dc3 caught its own only because it compares native and generated results (`tests/models/test_generated_parity.py`).
2. **The shipped advice weakens safety without saying so.** The guide now says to put an `assert constraint` on a part (`project_templates/MODELING_GUIDE.md.template`, "Three Structures the Code Generator Refuses"). In a generated package a part-owned assert reports a verdict and the computation continues; natively a failed assert stops evaluation. dc3 lost its stop-on-failure guards this way and rebuilt them as a consumer-side adapter (dc3 `scripts/models/package_comparison.py`, `PackageGateError`). The guide does not mention it. The `min(a, b) = (a + b − ((a − b)^2)^0.5) / 2` rewrite dc3 uses is not numerically identical to `min` either.
3. **Guidance still teaches functions the generator refuses.** About 18 places in `docs/patterns/conditionals.md`, `docs/patterns/syntax-reference.md`, `docs/patterns/README.md`, `skills/sysml-conventions/SKILL.md` and `project_templates/MODELING_GUIDE.md.template` show conditionals, `min`, `max`, `product` or `size` without saying the generator refuses them. `check` catches these early, so the cost is small rework, but the guidance should not lead there.
4. **The guidance goes stale when the generator changes.** If an owner-held generator change lifts a limit (`CALCDEF-GATE-IMPLEMENTATION`; the function-vocabulary change named in the architecture review), the guide becomes stricter than the generator. Low harm, but nothing ties the two together now that the agreement tests are gone.

## Success Criteria

- [ ] A modeller following the shipped workflow for a project that targets generated code keeps a test that compares native and generated results on their own model, and the workflow says what to do when they differ. When the generator is missing or fails, the comparison reports "not compared", never a pass or a silent skip (ADR 0004 invariant 3).
- [ ] The remedies the guidance offers (the part-owned assert, the `min` identity) and the patterns risk 1 names have each been run natively and through the generated package, with results recorded; any mismatch is fixed in the guidance or filed upstream. This is a bounded set chosen by risk, not a coverage target over all examples.
- [ ] The guidance says, where it tells modellers to move an assert onto a part, that a generated package reports the verdict and keeps computing, so whatever reads the package must check verdicts before using values; dc3's adapter is cited as a worked pattern.
- [ ] Every remedy the guidance offers for a refused form states what it does not preserve (at least the part-owned assert and the `min` identity).
- [ ] No shipped guidance presents a conditional, `min`, `max`, `product` or `size` as usable in generated models. Where it teaches them, it says to run `sysml-codegen check` before relying on them in a generated model, rather than restating which functions the generator accepts today; native-only teaching stays where it is useful.
- [ ] Each known generate-but-wrong case is either warned against in the guidance or filed upstream with a reproducer, and the positional-binding draft finding is reconciled with sysml-codegen's `[POSITIONAL-FORMAL-REDEFINITION]`.
- [ ] The guidance's claims about what the generator does today are limited to the three structural limits (kept by owner decision 2026-10-21), and each owner-held sysml-codegen change that would lift one of them carries a note naming the guidance to update.
- [ ] Shipped-text tests pin the new statements; the suite stays at its base failures.

## Known Requirements

- **[NEED]** Mitigate actual risk, not ceremony (owner, 2026-10-22: "what is risk that remains that we should mitigate? not ceremony, actual risk").
- **[INHERITED: ADR 0004]** The generator is the only authority on whether a model generates. agentic-mbse keeps no copy of its rules; evidence about generation comes from running the generator.
- **[INHERITED: RG-1, epic owner gates]** No change to what the generator accepts, refuses or builds. Generator defects are filed in sysml-codegen, not fixed here.
- **[INFERRED]** Statements in the guidance about generated behaviour are backed by a run (`check`, `generate`, or a native-vs-generated comparison) recorded as evidence, as `retire-subset-profile` did for the three limits.
- **[INFERRED]** dc3-specific code is cited, not copied into shipped assets; anything shipped is general.
- **[INHERITED: ADR 0004 invariant 2]** No agentic-mbse module imports sysml-codegen. A comparison helper either lives in sysml-codegen or runs the generator as a separate command.

## Non-Goals

- The 212-fence inventory, per-fence categories, exemption manifests, marker mutation tests and the 100% coverage target (original Item 5 scopes 1–3 and 8). Out by owner decision 2026-10-22: `check` and the parser already catch stale or refused examples cheaply.
- Rendering a generator-capability doc (original scope 4). Out since ADR 0004.
- Evaluator-author notes in `adr002-calculations.md` (original scope 7). Out of this item unless design finds one is needed to state a preservation obligation.
- Fixing the generator bugs themselves (RG-1, RG-2).
- Workflow gates beyond the comparison test (Item 6).

## Open Questions / Deferred to design

- What the comparison test looks like for a user project: guidance only, a project template test, or a helper shipped by agentic-mbse or sysml-codegen. Which repo would own a helper.
- Which examples count as "recommended for generated use", and how a native evaluation is run for them (SysIDE evaluation route, as Item 4 did with `native_values/`).
- Tolerances for comparing native and generated numbers (dc3 uses 1e-9 relative).
- Where the warnings live so there is one home per fact (the modelling guide, the pattern docs, or the "Generated code" section).
- How to reconcile the positional-binding disagreement: re-run Item 4's cross-route fixture against current sysml-codegen `main` first.
- Whether the function-vocabulary change exists as a sysml-codegen backlog row; if not, where the note for risk 4 goes.
- How to keep the guidance from becoming a second, hand-synced statement of the generator's rules (product-lens spec-F2). The spec's answer is to point at `check` instead of listing refused functions and to keep only the three structural limits as stated claims; design confirms or improves on that.
- At close: whether "native and generated results match for a model that generates" becomes a product promise (product-lens spec-F5; no current entry states it).

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_executable-subset-contract.md` (Item 5)
- **Decision:** `.project/adr/0004-generator-is-the-only-generation-authority.md`; sysml-codegen `.project/research/2026-10-21-generator-check-architecture-review/`
- **Prior item:** `.project/completed/20261022_retire-subset-profile/` (the three limits, generator probes in `evidence/probes.md`, checked guidance examples in `evidence/guidance-examples/`)
- **Positional binding:** `.project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md`
- **Product lens:** [product-lens.md](product-lens.md)
- **Design:** `.project/active/generated-results-guidance/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.

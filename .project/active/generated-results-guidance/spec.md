# Spec: Guidance that keeps generated results honest (EXEC-SUBSET-CONTRACT Item 5, rescoped)

**Status:** Draft, revised after spec review (verdict Revise; resolutions in [spec-review.md](spec-review.md) § Resolutions)
**Owner:** Reid Westwood
**Created:** 2026-10-22
**Complexity:** MEDIUM
**Branch:** agentic-mbse `generated-results-guidance` (worktree `/home/reid/src/subset-conformance/agentic-mbse`, base `4eed77d5`, the `retire-subset-profile` close, in PR #35)

---

## Problem

Since ADR 0004, a model the generator refuses is cheap: the workflow runs `sysml-codegen check` early, the refusal is loud, and the fix is rework on a small model. The remaining risk is a model that passes `check`, generates, and gives numbers that differ from the native model, or a package whose failed checks nobody reads. That failure looks like success. [AGENT] (ratified by owner, 2026-10-22: "agreed", in answer to the four-risk proposal below.)

Four risks, in order of harm:

1. **Patterns that generate but compute something different.** `check` cannot see these; only running both routes can.
   - Confirmed today: a part count given by a redefined `default` builds the default count (sysml-codegen backlog `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]`, 2 parts instead of 3); String values are left out of a built package without a report (`[SILENT-LOSSES-UNREPORTED]`); a calc usage with its own result expression drops that expression and also its input binding, which becomes an entry point with a null default (`[CALC-USAGE-BINDING-LOST-WITH-RESULT-EXPRESSION]`).
   - Unconfirmed at current sysml-codegen `main`: calculation inputs written out of order gave native −7 and generated 7 at sysml-codegen `b5663c07` (agentic-mbse `.project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md`, an unfiled draft), but sysml-codegen's `[POSITIONAL-FORMAL-REDEFINITION]` describes a refusal for this shape and dc3's WI-008 audit records the generator refusing it (`work/active/WI-008_generator-idiom/audit.md:14`); two calc defs with one simple name may leave one module unreachable (`[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`, read from code); and three places the retired copy reported as `omitted` (an unresolved conditional branch, an indexed reference, an unsupported callable outside a constraint predicate; `[SILENT-LOSSES-UNREPORTED]`) have not been re-checked.
   - Already warned in the shipped guide: the default count (`project_templates/MODELING_GUIDE.md.template:106`) and out-of-order inputs (`:216`, also reported by validate level 2 as `L2_POSITIONAL_BINDING`).
   - Nobody runs the comparison today. dc3 has a native-vs-generated parity test (`tests/models/test_generated_parity.py`) and its record shows only passes; it has not caught a case. Shipped guidance does not ask target projects for one.
2. **An assert never stops a computation, and the guidance does not say so.** The guide tells modellers to put an `assert constraint` on a part (`project_templates/MODELING_GUIDE.md.template`, "Three Structures the Code Generator Refuses"). In a generated package each constraint records satisfied, violated or indeterminate and never raises (sysml-codegen `templates/constraint_module.py.jinja2:33-48`); the outputs are computed anyway. SysIDE's native evaluation does not run assertions at all (dc3 `scripts/models/evaluate_paths.py:6-7`). dc3's stop-on-failure came from its own wrapper scripts natively and from its `PackageGateError` adapter for the package (dc3 `scripts/models/package_comparison.py:93-103`). So whatever reads the values must check the verdicts first, on either route. The guide does not mention it.
3. **Guidance teaches forms the generator refuses without saying so.** Conditionals are taught in about 10 examples: `docs/patterns/conditionals.md` (lines 28, 35, 44, 56, 99), `docs/patterns/syntax-reference.md:288,292`, `skills/sysml-conventions/SKILL.md:196`, `project_templates/MODELING_GUIDE.md.template:192`, and a table row in `docs/patterns/README.md:18`. `min`, `max`, `product` and `size` appear in `agents/kerml-expert.md:28,88-89` and `agents/sysmlv2-validator.md:298`. The generator refuses every invocation except `NumericalFunctions::sum` (sysml-codegen backlog `[SCALAR-FUNCTION-VOCABULARY]`); the conditional refusal has no recorded `check` run yet. `check` catches these early, so the cost is small rework, but the guidance should not lead there.
4. **The guidance goes stale when the generator changes.** If an owner-held generator change lifts one of the three structural limits (`[CALCDEF-GATE-IMPLEMENTATION]` would lift the assert-in-calc limit), the guide becomes stricter than the generator. Low harm, but nothing ties the two together now that the agreement tests are gone.

## Success Criteria

Each criterion names the risk it reduces.

- [ ] (Risk 1) A target project that sets `execution-target = "generated"` gets, from the shipped workflow, a comparison of native and generated results on its own model, and the workflow says what to do when they differ. The comparison is something a test can inspect: a template test `init` installs, a step in a named skill backed by a command, or a sysml-codegen command. Falsifier: in a project where the generator or the native evaluation is missing or fails, the comparison does not pass and reports "not compared" (ADR 0004 invariant 3).
- [ ] (Risk 2) Where the guidance tells modellers to put an assert on a part, it says that no route stops on a failed assert: the generated package records a verdict and keeps computing, and SysIDE's native evaluation does not run assertions. Whatever reads the values must check the verdicts first; dc3's adapter is cited as a worked pattern. A recorded run backs the generated half: a generated package returns outputs while a verdict is violated.
- [ ] (Risk 1) Each generate-but-wrong case listed in Risk 1 is re-run on current sysml-codegen `main`, and the result is recorded. A confirmed case is warned against in the guidance (except where that is a reserved decision, below) and has an upstream row with a reproducer; an unconfirmed case is recorded as such and its upstream row updated. For positional binding, the item records what current `main` does and files or updates `[POSITIONAL-FORMAL-REDEFINITION]` with the result; which reading the generator should follow stays with the codegen owner (RG-1).
- [ ] (Risk 3) No shipped guidance presents a conditional, `min`, `max`, `product` or `size` as usable in generated models. Where it teaches them, it says to run `sysml-codegen check` before relying on them in a generated model, rather than restating which functions the generator accepts today. Native-only teaching stays where it is useful. The conditional refusal is backed by a recorded `check` run.
- [ ] (Risk 4) The guidance's claims about what the generator does today are limited to the three structural limits and the named behaviours in criteria 2 and 3, each backed by a recorded run and an upstream row. Each owner-held sysml-codegen change that would lift one of the three limits (today `[CALCDEF-GATE-IMPLEMENTATION]`) carries a note naming the guidance to update.

Protection for the criteria above, not a risk reduction on its own: shipped-text tests pin the new statements so they are not deleted by accident, and the suite stays at its base failures.

## Known Requirements

- **[NEED]** Mitigate actual risk, not ceremony (owner, 2026-10-22: "what is risk that remains that we should mitigate? not ceremony, actual risk").
- **[INFERRED]** (ratified by owner at orchestration launch, 2026-10-22: "That's good, proceed") A modeller following the shipped workflow would catch a model that passes `check` and generates but computes different numbers than the native model; better docs alone do not meet it. The wording is the orchestrator's.
- **[INHERITED: ADR 0004]** The generator is the only authority on whether a model generates. agentic-mbse keeps no copy of its rules; evidence about generation comes from running the generator.
- **[INHERITED: ADR 0004 invariant 2]** No agentic-mbse module imports sysml-codegen. A comparison helper either lives in sysml-codegen or runs the generator as a separate command.
- **[INHERITED: RG-1, epic owner gates]** No change to what the generator accepts, refuses or builds. Generator defects are filed in sysml-codegen, not fixed here.
- **[INHERITED: RG-2, epic owner gates]** Whether the guidance warns about dropped String values, and about dropped calc-usage result expressions (sysml-codegen RG1-3), is the owner's call while those decisions are open; `[SILENT-LOSSES-UNREPORTED]` lists guidance lines as one of the options. Until decided, this item files and flags those two cases and does not add guidance about them.
- **[INFERRED]** Statements in the guidance about generated behaviour are backed by a run (`check`, `generate`, or a native-vs-generated comparison) recorded as evidence, as `retire-subset-profile` did for the three limits.
- **[INFERRED]** dc3-specific code is cited, not copied into shipped assets; anything shipped is general.

## Non-Goals

- The 212-fence inventory, per-fence categories, exemption manifests, marker mutation tests and the 100% coverage target (original Item 5 scopes 1–3 and 8). Out by owner decision 2026-10-22: `check` and the parser already catch stale or refused examples cheaply.
- Errors where native and generated agree but both are wrong, such as an input bound to the wrong feature when the two features happen to hold equal values. A comparison cannot see them; validate level 2 and the modeller's native checks own them.
- The `min` identity `(a + b − ((a − b)^2)^0.5) / 2`. It is dc3's own rewrite, not shipped advice; whether to ship a remedy for refused functions waits on `[SCALAR-FUNCTION-VOCABULARY]`.
- Rendering a generator-capability doc (original scope 4). Out since ADR 0004.
- Evaluator-author notes in `adr002-calculations.md` (original scope 7). Out unless design finds one is needed to state a preservation obligation.
- Fixing the generator bugs themselves (RG-1, RG-2).
- Workflow gates beyond the comparison (Item 6).

## Open Questions / Deferred to design

- Who provides the native half of the comparison for a target project: the modeller, agentic-mbse, or sysml-codegen. SysIDE's native evaluation needs explicit feature paths and runs no assertions, so dc3 wrote model-specific wrapper scripts. This answer sizes the item. A new sysml-codegen command is allowed if it does not change what the generator builds (owner-delegated at launch).
- What form the comparison takes (template test, skill step plus command, or generator command), and which repo owns it.
- Tolerances for comparing native and generated numbers (dc3 uses 1e-9 relative).
- Where the warnings live so there is one home per fact (the modelling guide, the pattern docs, or the "Generated code" section).
- How to keep the guidance from becoming a second, hand-synced statement of the generator's rules (product-lens spec-F2). The spec's answer is to point at `check` instead of listing refused functions and to keep only the claims in criterion 5; design confirms or improves on that.
- At close: whether "native and generated results match for a model that generates" becomes a product promise (product-lens spec-F5; no current entry states it).

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_executable-subset-contract.md` (Item 5)
- **Decision:** `.project/adr/0004-generator-is-the-only-generation-authority.md`; sysml-codegen `.project/research/2026-10-21-generator-check-architecture-review/`
- **Prior item:** `.project/completed/20261022_retire-subset-profile/` (the three limits, generator probes in `evidence/probes.md`, checked guidance examples in `evidence/guidance-examples/`)
- **Positional binding:** `.project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md`
- **Product lens:** [product-lens.md](product-lens.md)
- **Spec review:** [spec-review.md](spec-review.md)
- **Design:** `.project/active/generated-results-guidance/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.

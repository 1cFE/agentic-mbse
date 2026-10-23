# Spec Review: Guidance that keeps generated results honest (EXEC-SUBSET-CONTRACT Item 5, rescoped)

**Spec:** `.project/active/generated-results-guidance/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/generated-results-guidance/spec-review.md`
**Date:** 2026-10-22

---

## Reality Check

**Concerns.** The spec is about the right work item, and the four risks match the owner's rescope. But three of the Problem section's factual claims are wrong or unsupported when checked against dc3 and sysml-codegen: dc3's parity test never caught a generate-but-wrong case, a native assert does not stop evaluation by itself, and the shipped guidance does not offer the `min` identity. Each one changes what a success criterion should test, so they need fixing before design. None of them makes the item the wrong item, so this is Revise, not Rework.

What I checked: the spec, the product-lens ledger, epic Item 5, ADR 0004, the positional-binding draft finding, the sysml-codegen backlog rows the spec cites, the shipped guidance files, dc3's parity test and adapter, and (through one read-only agent) the sysml-codegen constraint and expression code. What I did not check: I could not run Python or the generator in this session (permission denied), so the `min` numbers below are worked out by hand, not measured. I did not confirm in generator code that every conditional is refused. I did not read the product entries P-0004 and P-0005.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim · must-fix:** Risk 1 says "dc3 caught its own only because it compares native and generated results (`tests/models/test_generated_parity.py`)". I found no record of that. dc3's parity results on record are all passes (WI-008 `audit.md:8`, "Parity tests: 16 passed"; `review.md:14`; learnings L-005). dc3's own adapter says the opposite about one class of error: "a misbinding with equal values generates a package that reports full satisfaction. The native evaluator checks them" (dc3 `scripts/models/package_comparison.py:15-19`). Nine of ten planted misbindings were caught by the native evaluator, not by parity (WI-008 `audit.md:14`). The comparison test is still the right answer to the owner's launch goal. But the spec should not justify it with a catch that did not happen, and design should know dc3's evidence is "parity passes", not "parity caught something".

**L1-2 · Direct claim · must-fix:** Risk 2 says "natively a failed assert stops evaluation". That is false as written. SysIDE does not run assertions: dc3 says so in code ("Raw Compiler evaluation does not execute assertions", dc3 `scripts/models/evaluate_paths.py:6-7`). dc3's stop-on-failure came from its own wrapper scripts, which evaluate each constraint and raise if it is not true (`evaluate_paths.py:97-100`, `evaluate_annual.py:33-37,95-96`, `evaluate_costs.py:116-120`). The generated half of the claim is true: each generated constraint module records satisfied, violated or indeterminate and never raises (sysml-codegen `src/sysml_codegen/templates/constraint_module.py.jinja2:33-48`), the package rolls them into a headline (`templates/report_aggregator.py.jinja2:54-73`), and the outputs are computed anyway. So the real risk is: an assert never stops anything on either route. Something has to read the verdicts before using the values. dc3 had that for native runs and had to add it for generated runs (`PackageGateError`, `package_comparison.py:93-103`). The spec and Success Criterion 3 should be restated on that basis. As written, the guidance would tell modellers native evaluation protects them when it does not.

**L1-3 · Direct claim · must-fix:** Success Criteria 2 and 4 speak of "the remedies the guidance offers (the part-owned assert, the `min` identity)". The shipped guidance does not offer the `min` identity. A search of `docs/patterns`, `skills`, `agents` and `project_templates` finds no `^ 0.5` rewrite and no `min`/`max` identity. The identity appeared only in the retired subset profile's remedy text ("arithmetic min/max identities", `.project/completed/20261020_l6-subset-profile/evidence/dc3-baseline-l6.md:59`) and lives on in dc3's models (dc3 `models/library/analyses/energy/annual_energy_balance.sysml:46,55-58`). Risk 2 correctly says "the rewrite dc3 uses". The criteria then treat it as shipped advice. The spec needs to say which it is: (a) the item will add the identity to the guidance as a remedy, with its limits; (b) the identity is out of the guidance and only needs a warning where `min` is taught; or (c) the risk is that modellers or agents reach for it unprompted, as dc3 did.

**L1-4 · Direct claim · should-fix:** Risk 3 says "about 18 places" in five files "show conditionals, `min`, `max`, `product` or `size`". In those five files I found only conditionals, in about 10 examples over 14 lines: `docs/patterns/conditionals.md` (5 examples, lines 28, 35, 44, 56, 99), `docs/patterns/syntax-reference.md` (2, lines 288, 292), `skills/sysml-conventions/SKILL.md:196`, `project_templates/MODELING_GUIDE.md.template:192`, and a table row in `docs/patterns/README.md:18`. `min`, `max`, `product` and `size` appear in two files the spec does not name: `agents/kerml-expert.md:28,88-89` and `agents/sysmlv2-validator.md:298`. Please correct the count and file list. Also, the claim that the generator refuses conditionals needs a recorded `check` run. dc3 recorded its conditional refusal as `SI_EVIDENCE_INCOMPLETE` with an inferred cause (dc3 `T-001-blocker-inventory.md:21`), and I did not find the refusal site in generator code.

**L1-5 · Direct claim · must-fix:** The owner's launch goal is not in the spec: a modeller following the shipped workflow would catch a model that passes `check` and generates but computes different numbers, and "better docs alone do not meet it". Success Criterion 1 reflects it, but Known Requirements does not carry it as a `[NEED]`. The first Open Question then offers "guidance only" as an option for the comparison test, which that goal rules out. Add the goal as a `[NEED]` with the owner's words and drop "guidance only" from the options.

**L1-6 · Direct claim · should-fix:** Risk 1 lists the positional-binding case (native −7, generated 7) as a known instance. That evidence is from sysml-codegen `b5663c07` on 2026-10-18. dc3's later WI-008 audit records an "out-of-order domain parameter (the generator refuses it too)" (`audit.md:14`). This fits `[POSITIONAL-FORMAL-REDEFINITION]`, which describes a refusal, not a by-name build. The current generator may refuse this shape rather than build it wrong. The spec already defers the re-run to design. It should also label the instance "unconfirmed at current sysml-codegen `main`" rather than "known".

**L1-7 · Direct claim · should-fix:** Risk 1 and Success Criterion 6 read as if no known case is warned about yet. Two of the three already are. The default-count case is warned at `project_templates/MODELING_GUIDE.md.template:106`. Out-of-order inputs are warned at `:216` and reported by validate level 2 (`L2_POSITIONAL_BINDING`). State that starting point so design does not redo it, and so Success Criterion 6's remaining work is visible.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff · must-fix:** A native-versus-generated comparison only catches cases where the two routes disagree. It cannot catch a model where both routes agree and both are wrong. dc3 documents two such cases: equal-value misbindings (`package_comparison.py:15-19`) and the `min` identity, which native SysIDE and the generated package both compute from the same expression. Success Criterion 2 asks for the `min` identity to be "run natively and through the generated package". That run will match and say nothing about whether the identity equals `min`. Checking the identity needs a comparison with the function it replaces, for example native SysIDE evaluating `min` on the same inputs. **If** the owner's goal is strictly "generated differs from native", the agree-but-wrong class is out of scope, and the spec should say so in Non-Goals. **If** the goal is "generated results are trustworthy", Success Criterion 2 has to compare each remedy with what it replaces, not native with generated. Which one is it?

**L2-2 · Direct claim · should-fix:** "The `min` identity is not numerically identical to `min`" is true, but the spec should say how and when it differs, or Success Criterion 4 has nothing concrete to state. These figures are worked out by hand and were not run. `(a + b − ((a − b)^2)^0.5) / 2` cancels badly when the smaller value is much smaller than the larger one. The error is about one rounding step of the larger value, so with values near 1e12 and 1e-3 the result can be several percent off. With values of similar size the relative error is about 1e-16, far inside dc3's 1e-9 tolerance. `(a − b)^2` overflows once `|a − b|` passes about 1.3e154 (plain Python raises an error; NumPy returns infinity, which gives −infinity). The generator accepts the form: `^` is rendered as `**` with no check on the exponent (sysml-codegen `extraction/calc_compat_renderer.py:47`, `elaboration/project.py:815`). I did not check which numeric library dc3's package runs on.

**L2-3 · Direct claim · should-fix (missing risks):** Risk 1 lists three generate-but-wrong instances. The backlog it cites lists more, and the spec should either include them or say why not:
- `[SILENT-LOSSES-UNREPORTED]` names three more places the retired copy reported as `omitted`, which nobody has re-checked since: an unresolved conditional branch, an indexed reference, and an unsupported callable outside a constraint predicate (sysml-codegen `.project/backlog/BACKLOG.md:55`).
- `[CALC-USAGE-BINDING-LOST-WITH-RESULT-EXPRESSION]`: a calc usage with its own result expression also loses its input binding, which becomes an entry point with a null default (`BACKLOG.md:29-31`). That is a wrong number, not only a missing expression.
- `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`: two calc defs with the same simple name may leave one module unreachable without any report (unconfirmed, `BACKLOG.md:37-39`).

**L2-4 · Question to the user · should-fix:** Success Criterion 1 needs a native evaluation of the modeller's own model, and that is where most of the item's cost and risk is. dc3 had to write model-specific wrapper scripts to evaluate natively (`evaluate_paths.py`, `evaluate_annual.py`, `evaluate_costs.py`), because raw SysIDE evaluation needs explicit feature paths and runs no assertions. A target project has none of that. The Open Questions mention native evaluation only for "examples". Make it an explicit design question for user projects. The "not compared" rule should also cover the native side failing (for example a missing SysIDE licence), not only a missing generator. **Is a per-project native harness something you expect modellers to write, or should agentic-mbse or sysml-codegen provide one?** That answer sizes the item.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim · must-fix (contradiction):** Success Criterion 7 limits the guidance's claims about current generator behaviour to the three structural limits. But Success Criterion 3 requires a claim about current behaviour (the package reports the verdict and keeps computing). Success Criterion 6 requires warnings that are claims about current behaviour (for example the default count). The guide already makes one such claim (`MODELING_GUIDE.md.template:106`). As written, Success Criteria 3 and 6 cannot both be met alongside Success Criterion 7. One way to resolve it: widen Success Criterion 7 to "the three structural limits, plus each named generate-but-wrong behaviour, each backed by a recorded run and an upstream row". The spec agent should choose the wording.

**L3-2 · Question to the user · must-fix (reserved decision):** Success Criterion 6 lets this item handle each generate-but-wrong case by "warned against in the guidance". For String values that is one of your open RG-2 options. The `[SILENT-LOSSES-UNREPORTED]` row says "Whether to report these (a `check` warning, guidance lines, or a refusal) is the owner's call", and names RG-2 for String and RG1-3 for the result expression (`BACKLOG.md:55`). **Is a factual guidance line ("String values do not reach the generated package today; see the backlog row") fine while RG-2 is open, or should this item only file and flag those two cases?** The spec should not decide this for you.

**L3-3 · Rewrite request · should-fix:** Success Criterion 6 requires the positional-binding draft to be "reconciled" with `[POSITIONAL-FORMAL-REDEFINITION]`. The draft itself says "The codegen owner decides which is right." Deciding which reading the generator intends is RG-1. This item can re-run the reproducer on current `main`, record what happens, and file or update the upstream row with the result (filing is delegated). Rewrite the criterion so the item can succeed without an owner ruling.

**L3-4 · Rewrite request · should-fix (testability):** Success Criterion 1 says a modeller "keeps a test". Nothing can check what a modeller keeps. Name what a test can inspect: a shipped template test that `init` installs, a workflow step in a named skill, or a sysml-codegen command. Give the falsifier from product-lens F3: in a project without sysml-codegen (or without a working native evaluation), the comparison does not pass and says "not compared". Note that dc3's test errors when the package is missing rather than skipping (dc3 `tests/models/test_generated_parity.py:45-47`). That is not a false pass, but it is not a clear "not compared" either, so it should not be copied as is.

**L3-5 · Direct claim · should-fix (ceremony check):** Success Criterion 2 is bounded now, but two parts of it do not reduce a risk as written. (a) Running the part-owned assert natively and generated shows no numeric difference: neither route stops, and both compute. What needs evidence is that a generated package returns outputs while a verdict is violated. Test that. (b) "With results recorded" is only worth doing when the record backs a guidance statement or an upstream row. It also overlaps Success Criterion 6's "filed upstream with a reproducer". Tie each run to the claim it backs, and merge the overlap with Success Criterion 6.

**L3-6 · Direct claim · should-fix:** The Open Question "whether the function-vocabulary change exists as a sysml-codegen backlog row" can be answered now. It exists: `[SCALAR-FUNCTION-VOCABULARY]`, P2, `[OWNER, 2026-08-18]` (sysml-codegen `.project/backlog/BACKLOG.md:25`). It lifts none of the three structural limits, so under Success Criterion 7 it needs no note. Success Criterion 5's "run `check`" wording already covers it. Remove the question. Risk 4 should name `[CALCDEF-GATE-IMPLEMENTATION]` (structural limit 1) as the one change Success Criterion 7's note applies to.

**L3-7 · Direct claim · should-fix:** Success Criterion 8 ("shipped-text tests pin the new statements") stops the warnings being deleted by accident. That is worth having and costs little. It does not reduce any of the four risks on its own, so it should not count toward the owner's "actual risk" bar. Name it as protection for the other criteria.

### Lens 4 — Hygiene

**L4-1 · Rewrite request · should-fix:** The `[SILENT-LOSSES-UNREPORTED]` row's reproduction path still says `.project/active/retire-subset-profile/evidence/...` (sysml-codegen `BACKLOG.md:51`). That item has moved to `.project/completed/20261022_retire-subset-profile/`. This is not the spec's text, but Success Criterion 6 relies on that row's reproducer, so the filing step should fix the path.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request · should-fix:** The success criteria do not say which risk each one reduces. A reader therefore cannot apply the owner's "not ceremony" test without mapping them by hand. Tag each criterion with its risk number. Also, Risk 2's last sentence about the `min` identity is a different problem (numbers, not safety) and is lost inside the assert paragraph. Give it its own line, or move it under Risk 1 or wherever L1-3's answer puts it.

---

## Engagement Summary

**Overall take:** The four risks are the right ones, and the main bet is sound: give modellers a native-versus-generated comparison, plus honest warnings. But the spec supports that bet with three claims that did not survive checking. dc3's parity test caught nothing. A native assert stops nothing on its own. The guidance does not offer the `min` identity. And a comparison test cannot catch the agree-but-wrong errors dc3 actually hit. Fix the facts, settle the scope of the agree-but-wrong class, and remove the Success Criterion 7 contradiction. Then this is a good contract.

**Here's what I need you to weigh in on:**

1. **[L2-1]** Is the goal strictly "generated differs from native", or "generated results are trustworthy"? A parity test misses errors where both routes agree, such as equal-value misbindings and the `min` identity. Either record that as a Non-Goal, or make Success Criterion 2 compare each remedy with the function it replaces.
2. **[L3-2]** May this item add a factual guidance line about String values and calc-usage result expressions being dropped, while RG-2 and RG1-3 are open? Or should it only file and flag them?
3. **[L2-4]** Who provides the native half of the comparison for a user project: the modeller, agentic-mbse, or sysml-codegen? dc3 needed model-specific wrapper scripts for it.
4. **[L1-1, L1-2, L1-3]** Correct the Problem section. dc3 caught nothing through parity. A native assert stops nothing by itself, so whatever reads the values must check the verdicts. The `min` identity is dc3's own rewrite, not shipped advice, so the spec must decide whether the item adds it, warns against it, or neither.
5. **[L1-5]** Record your launch goal ("better docs alone do not meet it") as a `[NEED]`, and drop "guidance only" from the comparison-test options.
6. **[L3-1]** Make Success Criteria 3, 6 and 7 consistent about which claims on current generator behaviour the guidance may make.

---

## Resolutions

Resolved by the orchestrator, 2026-10-22. The spec author (the orchestrating session) revised the spec directly.

- **L1-1, L1-2, L1-3, L1-4, L1-6, L1-7:** accepted; Problem rewritten. Checked L1-2 independently: dc3 `scripts/models/evaluate_paths.py:6-7` says raw evaluation does not execute assertions. L1-1 was the orchestrator's own error in the first draft.
- **L1-5:** accepted, recorded as `[INFERRED]` ratified by owner at launch rather than `[NEED]`, because the wording was the orchestrator's (capture-fidelity: an approved agent statement stays agent-grade). "Guidance only" removed from the comparison options.
- **L2-1:** scope is "generated differs from native", the launch goal. Agree-but-wrong errors moved to Non-Goals. The `min` identity is not shipped advice, so it leaves the criteria and goes to Non-Goals, waiting on `[SCALAR-FUNCTION-VOCABULARY]`. L2-2 is moot with it.
- **L2-3:** accepted; the extra cases are in Risk 1, split confirmed / unconfirmed, and criterion 3 re-runs each.
- **L2-4:** made the first design question; "not compared" now covers the native side failing too.
- **L3-1:** criterion 5 widened to the three limits plus the behaviours in criteria 2 and 3, each backed by a run and an upstream row.
- **L3-2:** reserved owner decision (RG-2 / sysml-codegen RG1-3). Parked: the spec records that the item files and flags the String and result-expression cases and adds no guidance about them until the owner decides. Question raised to the owner.
- **L3-3:** accepted; the item records what current `main` does and updates the upstream row; the ruling stays with the codegen owner.
- **L3-4:** accepted; criterion 1 names inspectable forms and the falsifier. Design is told dc3's erroring test is not the model to copy.
- **L3-5:** accepted; the assert run now tests "outputs returned while a verdict is violated"; runs are tied to the claim they back and merged into criterion 3.
- **L3-6:** accepted; question removed, `[CALCDEF-GATE-IMPLEMENTATION]` named in Risk 4.
- **L3-7:** accepted; shipped-text tests are listed as protection, not a criterion.
- **L4-1:** passed to design/implement: fix the stale reproducer path when the upstream row is updated.
- **L5-1:** accepted; each criterion is tagged with its risk.

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded, return to the spec-agent session (or re-run `/_my_spec`) and point it at this review to incorporate. The reviewer does not edit the spec.

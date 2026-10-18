# Acceptance runs (plan Phase 10)

All runs at agentic-mbse `ce0ad1ffbc4070004d8a7a5a1b3e834f4e483508` (the final implementation revision after the audit fixes; re-run 2026-10-18 from the Phase 10 run at `9b123cf3`), judged against sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`, SysIDE 0.8.4, default (generator) roots. Each tree was read from a `git archive` export. Full outputs: `dc3-baseline.{json,md}`, `dc3-repaired.{json,md}`, `corpus.{json,md}` (written by `scripts/subset_profile/run_trees.py`).

**What the audit-fix rerun changed:** every count, location and finding is identical to the `9b123cf3` run. Two verdicts changed name, because of the new `refused_incomplete` verdict (audit S3): dc3 baseline and the corpus refusal fixture `invocation_binding_probe`, both of which hold probe-backed refusals and unverified checks, were `incomplete` and are now `refused_incomplete`. `incomplete` now means no refusal.

Counts: a **declaration** is one finding, keyed by (rule, shape, context, declaration UUID); **occurrences** are the generator occurrences of instantiation-dependent findings, summed from each finding's `occurrence_count` (model-wide rules carry none).

| Tree | Verdict | Declarations | Occurrences | refused | omitted | admitted | excluded | unconfirmed | unverified |
|---|---|---|---|---|---|---|---|---|---|
| dc3 baseline `808464df` | **REFUSED_INCOMPLETE** | 274 | 101 | 236 | 32 | 0 | 0 | 6 | 50 |
| dc3 repaired `60b44d53` | **CLEAR** | 45 | 0 | **0** | 30 | 15 | 0 | 0 | **0** |
| codegen corpus, 37 fixtures | 14/14 snapshot fixtures CLEAR | 203 | 167 | 0 on snapshot fixtures; 82 on refusal fixtures | 69 | 51 | 1 | 0 | 2 (both on refusal fixture `invocation_binding_probe`) |

## dc3 baseline: B1-B8

Roots used: all 8 generator roots (`dc_native_site::dc_site`, `dc3_source_load_example::illustrative_scenario`, `dc3_baseline_annual::reference_operation`, `dc3_baseline_annual::annual_reference`, `ac_coupled_site::ac_site`, `dc_native_facility::dc_facility`, `dc3_baseline_costs::cost_reference`, `ac_coupled_facility::ac_facility`); not narrowed; every fact kind enumerated.

| T-001 | Rule / shape / context | Outcome | Declarations (occurrences) | Where | Against T-001 |
|---|---|---|---|---|---|
| B1 calc-usage-owned `assert constraint` | `calc-owned-assertion` / `asserted_constraint` / `calc_usage_owner` | refused | 164 | all designs | T-001: 164. Same. |
| B2 sequence calc input | `binding-source` / `expression_source` / `owner_instantiated` | refused | 29 (29) | the sequence actuals: 21 `efficiencies_in`, 8 cost inputs (`capital_costs_in`, `fixed_om_costs_in`, `category_*`) | T-001 counts the 5 input declarations; the contract reports the 29 bindings that feed them, which is what the generator refuses (ES-003, not ES-004). |
| B3 `[*]` part multiplicity | `part-multiplicity` / `unresolved_bound` / `expanded_part_usage` | refused | 15 (72) | `cooling.sysml:192-198`, `facility.sysml:142-143`, `it.sysml:103-119` | Every `[*]` part usage in `models/` at `808464df` (a grep finds exactly these 15). T-001's "(20)" is a different count, not reconciled (T-001 ran at agentic-mbse `8b027bbc`). No range multiplicity is reached. |
| B4 `NumericalFunctions::product` | `invocation-callable` / `unsupported_callable` / `calc_definition_feature_value` | refused | 1 | `path_efficiency.sysml:52` | Same site. |
| B5 `SequenceFunctions::size` | `invocation-callable` / `unsupported_callable` / `binding_value` | refused | 22 | designs, `nonempty_path::stage_count_in` | T-001: 22. Same. |
| B6 conditional `if … ? … else` | `conditional-expression` / `conditional_unresolved_branch` / `calc_definition_feature_value` | refused | 5 | `annual_energy_balance.sysml:46, 55, 56, 57, 58` | T-001: `:46,55-58` (5). Same. |
| B7 String attributes | `string-value-omission` / `string_value` / `attribute_value` | omitted | 32 | 29 `:>>` shorthand, 3 `attribute` declarations; designs and `baseline_costs.sysml` | T-001 says 10 and L6 flagged 3 (one spelling only). The contract counts every valued String feature in both spellings. |
| B8 4 NON_NUMERICAL | `constraint-predicate` / `non_numerical_predicate` / `owner_other` | **unconfirmed** | 4 | `baseline_annual.sysml:57, 84, 97, 124` | Same four constraints L6 reported. The matrix's ES-007 split now states this (audit S4). |
| B8 4 MALFORMED_NUMERICAL | `constraint-predicate` / `blocked_predicate` / `owner_other` | **unconfirmed** | 2 | `baseline_costs.sysml:74, 134` (`block_non_numerical_containment`) | L6's 4 diagnostics are 2 constraints reported twice each (L6's own summary line says "Malformed numerical: 2"). Same two constraints. The matrix's ES-007 split now states 2, `unconfirmed`, `owner_other` (audit S4; it said 4, `refused`). |

**B8 appears only as `unconfirmed`. Listed for the owner.** All six constraints are owned by calc usages, so their context is `owner_other` (an owner kind that attaches nothing). The generator refuses those constraints first for their owner (B1, `SI_CONSTRAINT_UNATTACHED`), so it never reaches the predicate check; no probe has observed a blocked or non-numerical predicate under a calc-usage owner, and the records list no outcome for `owner_other`. The missing probe would be `constraint-predicate__blocked_predicate__owner_other` (and its non-numerical twin), which the generator would refuse with ES-001's code, not ES-007's. Both B8 kinds stay apart, as the matrix requires.

**The verdict is REFUSED_INCOMPLETE: 236 probe-backed refusals, and 50 `unverified` checks, all on sites the contract already refuses.** (Before the audit fixes the single verdict read INCOMPLETE, which outranked the refusals; S3.) Phase 7 noted that a refused conditional or invocation leaves the reference walk failed on the same site. Itemized:

| Rule left unverified | Context | Cause | Count | The site, already refused as |
|---|---|---|---|---|
| `binding-source` | (binding not classifiable) | `EXPRESSION_KIND_UNSUPPORTED` | 22 | B5: `stage_count_in = size(…)`; the binding's reference walk meets `size` |
| `indexed-reference` | `binding_value` | `EXPRESSION_KIND_UNSUPPORTED` | 22 | the same 22 B5 sites |
| `indexed-reference` | `calc_definition_feature_value` | `RESOLVED_TARGET_MISSING` | 5 | the 5 B6 conditionals |
| `indexed-reference` | `calc_definition_feature_value` | `EXPRESSION_KIND_UNSUPPORTED` | 1 | the B4 `product` site |

In words: on a site whose walk failed, the contract cannot say whether the expression also holds an indexed reference (or, for a binding, which binding kind it is), so it says `unverified` rather than clean. Every unverified location equals the location of a refused finding. The evaluator was not tuned to reach CLEAR.

## dc3 repaired: zero refused

- Verdict **CLEAR**: 0 refused, 0 unverified, 0 unconfirmed. Roots used: all 6 generator roots.
- 30 String omissions (`string_value`, `attribute_value`, all `:>>` shorthand), as the prototype saw.
- 15 `admitted`: the same 15 library `[*]` part usages, now `unexpanded_part_usage` (templates the designs never expand; designs state exact counts).

## Codegen corpus: the regression floor holds

- Manifest `tests/fixtures/v6_recapture_batch/batch.json` at `b5663c07`: **37 fixtures, 14 snapshot records, 23 typed refusal records** (the batch README says 15 and 22; the manifest governs).
- **14 snapshot fixtures: zero `refused`, every verdict CLEAR.** One `excluded` (the non-numerical constraint in `constraint_non_numerical`) and one `omitted` String.
- **23 refusal fixtures: every `refused` finding's code is in the fixture's recorded code list, or is a probe-recorded pair.** 21 report `refused`, 1 `clear`, 1 `refused_incomplete`. One fixture (`plant_value_shapes`) has an `SI_SELF_BINDING` finding whose code is not in its record's list (the inventory stops at its first error, so the list is a lower bound); `binding-source/self_reference_source` is a probe-recorded pair, so it passes and is not R2. `invocation_binding_probe` is REFUSED_INCOMPLETE for the same reason as dc3 baseline (an invocation refused, so binding-source and indexed-reference are unverified on that site). `deep_cross_scope_probe` is **CLEAR although the generator refuses it**: its shape (DEEP-QUALIFIED-WIRING) is a tracked gap with no rule. **Recorded for the owner:** CLEAR means no rule of the contract refuses and nothing was left unverified; it does not mean the generator accepts the model. The tracked-gap rows without a rule (ES-002, ES-008, ES-009, ES-010-REFUSAL, CALC-DEF-BARE-RESULT, DEEP-QUALIFIED-WIRING and the 85 explicit follow-up sites) can still refuse a CLEAR model. Since the audit fixes (S2) this limit is stated in `subset_profile.py`'s module docstring and on `Verdict.CLEAR`.
- The snapshot fixtures prove admission through elaboration and projection, not full generation, and contain no invocations, `ordered`/`nonunique` or range multiplicities; the admitted-context probes carry the "not overbroad" proof.

## R2 check

No `refused` finding on any snapshot fixture or on dc3 repaired. No R2.

## Occurrence parity at the final revision

`occurrence_parity.py compare --all --agentic-rev ce0ad1ff`: **73/73 match** (`occurrence-parity.log`, identity line names `ce0ad1ff`).

## Same-generator and consumer output at the final revision

- Probes 80/80 certify at `a718efec` (base), `b1e95ec9` (canonical, cited by the records) and `ce0ad1ff` (final); observations differ only in `identity.agentic_rev`. Codegen's suite: 2754 tests, 0 differ (`same-generator.md`).
- `validate` diff: see `validate-diff.md`.

# dc3 baseline: L6 under `generated`, and unset

Written by `scripts/l6_subset/run_consumers.py l6-evidence`. agentic-mbse branch `0ba0bf0215bc3177e724d1cfe2d42aa2480f34b1`; SysIDE 0.8.4; dc3 `808464df85d50521e4fbb9ba7cceb63d382aa832` from a `git archive` export under /tmp. Settings input: root `dc3-baseline`, `dc3-baseline/pyproject.toml`, tables {"agentic-mbse": "absent", "agentic_mbse": "absent"}. Sibling checkouts unchanged: True. Every count below is read from the run's `--json-report`.

## `validate --level=6 --execution-target=generated models`

- Exit 1 (report 1); L6 failed; wall time 18.1 s; constraint extractions 1; resolved root `trees/dc3-baseline`.
- Pass notes: none.
- Against Item 1's record: same (verdict refused_incomplete, refused 236, omitted 32, unconfirmed 6, unverified 50).
- Verdict `refused_incomplete`. Findings 274, by outcome {"refused": 236, "admitted": 0, "excluded": 0, "omitted": 32, "unconfirmed": 6} (declarations 274, occurrences 101); unverified 50 {"binding-source": 22, "indexed-reference": 28}; unassessed constraints 0; advisories 0; check errors 0.

Metrics as printed:

```text
Execution target: generated (override --execution-target; /tmp/l6-evidence-8wa9w5vg/trees/dc3-baseline/pyproject.toml sets none)
Generator subset (subset-profile/v1, subset-coverage/v1): refused_incomplete: 236 refused, then incomplete: 50 unverified; 0 unassessed constraints; not a generation check
Coverage limit: no rule yet for DEEP-QUALIFIED-WIRING, ES-002, ES-008, ES-009, ES-010-REFUSAL, CALC-DEF-BARE-RESULT, and 85 follow-up sites; a clear verdict says nothing about these
Generator subset scope: executable profile executable-profile/v4; roots used 8 of 8 (not narrowed); fact kinds not enumerated: none
Calc defs checked: 6
Calc usages checked: 41
Bindings validated: 134
Design attrs checked: 49
Manifests checked: 0
L6_MISSING_QUALIFIED_NAME: 0
L6_INVALID_QUALIFIED_NAME: 0
L6_CALC_DEF_NO_OUTPUT: 0
L6_CALC_DEF_NO_DIRECTION: 0
L6_INVALID_BINDING_FORMAT: 0
L6_DESIGN_ATTR_INCOMPLETE: 0
L6_DESIGN_ATTR_UNEXTRACTABLE: 0
L6_ANONYMOUS_RETURN: 0
L6_BODY_ASSIGNMENT_IMPL_LOSS: 0
V4_STATIC_FUNCTION_INVOCATION: 0
L6_CONSTRAINT_MALFORMED_NUMERICAL: 4
L6_CONSTRAINT_NON_NUMERICAL: 4
L6_CALC_DEF_NO_INSTANTIATION: 0
L6_ATTR_REDEF_EXPR_DROPPED: 0
```

| Category | Rule / shape / context | Declarations (occurrences) | Outcome | Shown as | Shadowed by |
|---|---|---|---|---|---|
| B1 | `calc-owned-assertion / asserted_constraint / calc_usage_owner` | 164 | refused | error | - |
| B2 | `binding-source / expression_source / owner_instantiated` | 29 (29) | refused | error | - |
| B3 | `part-multiplicity / unresolved_bound / expanded_part_usage` | 15 (72) | refused | error | - |
| B4 | `invocation-callable / unsupported_callable / calc_definition_feature_value` | 1 | refused | error | - |
| B5 | `invocation-callable / unsupported_callable / binding_value` | 22 | refused | error | - |
| B6 | `conditional-expression / conditional_unresolved_branch / calc_definition_feature_value` | 5 | refused | error | - |
| B7 | `string-value-omission / string_value / attribute_value` | 32 | omitted | warning | - |
| B8 | `constraint-predicate / non_numerical_predicate / owner_other` | 4 | unconfirmed | warning | calc-owned-assertion/asserted_constraint (4 of 4) |
| B8 | `constraint-predicate / blocked_predicate / owner_other` | 2 | unconfirmed | warning | calc-owned-assertion/asserted_constraint (2 of 2) |

L6 issue codes by display: `L6_CONSTRAINT_MALFORMED_NUMERICAL (error)` 4, `L6_CONSTRAINT_NON_NUMERICAL (warning)` 4, `L6_SUBSET_OMITTED (warning)` 32, `L6_SUBSET_REFUSED (error)` 236, `L6_SUBSET_UNCONFIRMED (warning)` 6, `L6_SUBSET_UNVERIFIED (error)` 50.

### One finding per category: location, reason, remedy

- **B1** `ac_coupled_facility::ac_facility::rack_1_server_1_efficiency::nonempty_path` at `models/designs/ac_coupled/ac_facility.sysml:210`: refused, reason `calc_owned_asserted_constraint`. Remedy: Move the constraint to the part definition or part usage that owns the calculation, binding it to the calculation's inputs or result there.
- **B2** `ac_coupled_facility::ac_facility::rack_1_server_1_efficiency::efficiencies_in` at `models/designs/ac_coupled/ac_facility.sysml:213`: refused, reason `binding_source_expression`. Remedy: Bind the input to a literal or to one plain reference to a feature that holds the value; compute tuples and arithmetic in a named attribute and bind that.
- **B3** `dc3_cooling::'Cooling System'::cold_plate_loops` at `models/library/components/compute/cooling.sysml:192`: refused, reason `part_multiplicity_unresolved_bound`. Remedy: Give the part usage an exact literal multiplicity, unordered and unique, or remove the multiplicity; model a variable count as an attribute.
- **B4** `dc3_path_efficiency::'Path Efficiency'::path_efficiency` at `models/library/analyses/energy/path_efficiency.sysml:52`: refused, reason `invocation_callable_unsupported`. Remedy: Write the computation with operators the subset supports (explicit multiplication, arithmetic min/max identities) or with NumericalFunctions::sum; or move it into a calculation definition's bare result expression (a handwritten stub).
- **B5** `ac_coupled_facility::ac_facility::rack_1_server_1_efficiency::nonempty_path::stage_count_in` at `models/designs/ac_coupled/ac_facility.sysml:211`: refused, reason `invocation_callable_unsupported`. Remedy: Write the computation with operators the subset supports (explicit multiplication, arithmetic min/max identities) or with NumericalFunctions::sum; or move it into a calculation definition's bare result expression (a handwritten stub).
- **B6** `dc3_annual_energy_balance::'Annual Energy Balance'::direct_pv_wh` at `models/library/analyses/energy/annual_energy_balance.sysml:46`: refused, reason `conditional_expression_unsupported`. Remedy: Compute each branch as its own attribute and select with arithmetic the subset supports, or move the choice into a calculation definition's bare result expression (a handwritten stub).
- **B7** `ac_coupled_facility::ac_facility::electrical::mv_transformer::conversion_level` at `models/designs/ac_coupled/ac_facility.sysml:43`: omitted, reason `string_value_not_generated`. Remedy: Keep String values as documentation; the generated catalog and contract carry numeric and Boolean values only. Do not bind a String to a calculation input (the ES-010 refusal side).
- **B8** `dc3_baseline_annual::annual_reference::ac_demand::input_domain` at `models/designs/examples/baseline_annual.sysml:57`: unconfirmed, reason `constraint_predicate_non_numerical`. Remedy: Split Boolean data out of numerical assertions, or rewrite the predicate as a numerical comparison the profile admits; the finding's detail reasons name the profile's diagnosis.
- **B8** `dc3_baseline_costs::cost_reference::ac_total::delivered_domain` at `models/designs/examples/baseline_costs.sysml:74`: unconfirmed, reason `constraint_predicate_blocked`. Remedy: Split Boolean data out of numerical assertions, or rewrite the predicate as a numerical comparison the profile admits; the finding's detail reasons name the profile's diagnosis.

## `validate --level=6 models`

- Exit 1 (report 1); L6 failed; wall time 18.1 s; constraint extractions 1; resolved root `trees/dc3-baseline`.
- Pass notes: none.
- Against Item 1's record: same (verdict refused_incomplete, refused 236, omitted 32, unconfirmed 6, unverified 50).
- Verdict `refused_incomplete`. Findings 274, by outcome {"refused": 236, "admitted": 0, "excluded": 0, "omitted": 32, "unconfirmed": 6} (declarations 274, occurrences 101); unverified 50 {"binding-source": 22, "indexed-reference": 28}; unassessed constraints 0; advisories 0; check errors 0.

Metrics as printed:

```text
Execution target: unset (no execution-target in /tmp/l6-evidence-8wa9w5vg/trees/dc3-baseline/pyproject.toml)
Execution target note: generator findings are shown as warnings because execution-target is not set. Add execution-target = "generated" or "native" under [tool.agentic-mbse] in pyproject.toml, or run agentic-mbse init --execution-target=generated|native.
Generator subset (subset-profile/v1, subset-coverage/v1): refused_incomplete: 236 refused, then incomplete: 50 unverified; 0 unassessed constraints; not a generation check
Coverage limit: no rule yet for DEEP-QUALIFIED-WIRING, ES-002, ES-008, ES-009, ES-010-REFUSAL, CALC-DEF-BARE-RESULT, and 85 follow-up sites; a clear verdict says nothing about these
Generator subset scope: executable profile executable-profile/v4; roots used 8 of 8 (not narrowed); fact kinds not enumerated: none
Calc defs checked: 6
Calc usages checked: 41
Bindings validated: 134
Design attrs checked: 49
Manifests checked: 0
L6_MISSING_QUALIFIED_NAME: 0
L6_INVALID_QUALIFIED_NAME: 0
L6_CALC_DEF_NO_OUTPUT: 0
L6_CALC_DEF_NO_DIRECTION: 0
L6_INVALID_BINDING_FORMAT: 0
L6_DESIGN_ATTR_INCOMPLETE: 0
L6_DESIGN_ATTR_UNEXTRACTABLE: 0
L6_ANONYMOUS_RETURN: 0
L6_BODY_ASSIGNMENT_IMPL_LOSS: 0
V4_STATIC_FUNCTION_INVOCATION: 0
L6_CONSTRAINT_MALFORMED_NUMERICAL: 4
L6_CONSTRAINT_NON_NUMERICAL: 4
L6_CALC_DEF_NO_INSTANTIATION: 0
L6_ATTR_REDEF_EXPR_DROPPED: 0
```

| Category | Rule / shape / context | Declarations (occurrences) | Outcome | Shown as | Shadowed by |
|---|---|---|---|---|---|
| B1 | `calc-owned-assertion / asserted_constraint / calc_usage_owner` | 164 | refused | warning | - |
| B2 | `binding-source / expression_source / owner_instantiated` | 29 (29) | refused | warning | - |
| B3 | `part-multiplicity / unresolved_bound / expanded_part_usage` | 15 (72) | refused | warning | - |
| B4 | `invocation-callable / unsupported_callable / calc_definition_feature_value` | 1 | refused | warning | - |
| B5 | `invocation-callable / unsupported_callable / binding_value` | 22 | refused | warning | - |
| B6 | `conditional-expression / conditional_unresolved_branch / calc_definition_feature_value` | 5 | refused | warning | - |
| B7 | `string-value-omission / string_value / attribute_value` | 32 | omitted | warning | - |
| B8 | `constraint-predicate / non_numerical_predicate / owner_other` | 4 | unconfirmed | warning | calc-owned-assertion/asserted_constraint (4 of 4) |
| B8 | `constraint-predicate / blocked_predicate / owner_other` | 2 | unconfirmed | warning | calc-owned-assertion/asserted_constraint (2 of 2) |

L6 issue codes by display: `L6_CONSTRAINT_MALFORMED_NUMERICAL (error)` 4, `L6_CONSTRAINT_NON_NUMERICAL (warning)` 4, `L6_SUBSET_OMITTED (warning)` 32, `L6_SUBSET_REFUSED (warning)` 236, `L6_SUBSET_UNCONFIRMED (warning)` 6, `L6_SUBSET_UNVERIFIED (warning)` 50.

### One finding per category: location, reason, remedy

- **B1** `ac_coupled_facility::ac_facility::rack_1_server_1_efficiency::nonempty_path` at `models/designs/ac_coupled/ac_facility.sysml:210`: refused, reason `calc_owned_asserted_constraint`. Remedy: Move the constraint to the part definition or part usage that owns the calculation, binding it to the calculation's inputs or result there.
- **B2** `ac_coupled_facility::ac_facility::rack_1_server_1_efficiency::efficiencies_in` at `models/designs/ac_coupled/ac_facility.sysml:213`: refused, reason `binding_source_expression`. Remedy: Bind the input to a literal or to one plain reference to a feature that holds the value; compute tuples and arithmetic in a named attribute and bind that.
- **B3** `dc3_cooling::'Cooling System'::cold_plate_loops` at `models/library/components/compute/cooling.sysml:192`: refused, reason `part_multiplicity_unresolved_bound`. Remedy: Give the part usage an exact literal multiplicity, unordered and unique, or remove the multiplicity; model a variable count as an attribute.
- **B4** `dc3_path_efficiency::'Path Efficiency'::path_efficiency` at `models/library/analyses/energy/path_efficiency.sysml:52`: refused, reason `invocation_callable_unsupported`. Remedy: Write the computation with operators the subset supports (explicit multiplication, arithmetic min/max identities) or with NumericalFunctions::sum; or move it into a calculation definition's bare result expression (a handwritten stub).
- **B5** `ac_coupled_facility::ac_facility::rack_1_server_1_efficiency::nonempty_path::stage_count_in` at `models/designs/ac_coupled/ac_facility.sysml:211`: refused, reason `invocation_callable_unsupported`. Remedy: Write the computation with operators the subset supports (explicit multiplication, arithmetic min/max identities) or with NumericalFunctions::sum; or move it into a calculation definition's bare result expression (a handwritten stub).
- **B6** `dc3_annual_energy_balance::'Annual Energy Balance'::direct_pv_wh` at `models/library/analyses/energy/annual_energy_balance.sysml:46`: refused, reason `conditional_expression_unsupported`. Remedy: Compute each branch as its own attribute and select with arithmetic the subset supports, or move the choice into a calculation definition's bare result expression (a handwritten stub).
- **B7** `ac_coupled_facility::ac_facility::electrical::mv_transformer::conversion_level` at `models/designs/ac_coupled/ac_facility.sysml:43`: omitted, reason `string_value_not_generated`. Remedy: Keep String values as documentation; the generated catalog and contract carry numeric and Boolean values only. Do not bind a String to a calculation input (the ES-010 refusal side).
- **B8** `dc3_baseline_annual::annual_reference::ac_demand::input_domain` at `models/designs/examples/baseline_annual.sysml:57`: unconfirmed, reason `constraint_predicate_non_numerical`. Remedy: Split Boolean data out of numerical assertions, or rewrite the predicate as a numerical comparison the profile admits; the finding's detail reasons name the profile's diagnosis.
- **B8** `dc3_baseline_costs::cost_reference::ac_total::delivered_domain` at `models/designs/examples/baseline_costs.sysml:74`: unconfirmed, reason `constraint_predicate_blocked`. Remedy: Split Boolean data out of numerical assertions, or rewrite the predicate as a numerical comparison the profile admits; the finding's detail reasons name the profile's diagnosis.

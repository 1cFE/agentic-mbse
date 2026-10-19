# dc3 repaired: L6 under `generated`

Written by `scripts/l6_subset/run_consumers.py l6-evidence`. agentic-mbse branch `0ba0bf0215bc3177e724d1cfe2d42aa2480f34b1`; SysIDE 0.8.4; dc3 `60b44d53460fccd2f44811d8abfd42bc270e90b2` from a `git archive` export under /tmp. Settings input: root `dc3-repaired`, `dc3-repaired/pyproject.toml`, tables {"agentic-mbse": "absent", "agentic_mbse": "absent"}. Sibling checkouts unchanged: True. Every count below is read from the run's `--json-report`.

## `validate --level=6 --execution-target=generated models`

- Exit 0 (report 0); L6 passed; wall time 13.2 s; constraint extractions 1; resolved root `trees/dc3-repaired`.
- Pass notes: generated compatibility not established.
- Against Item 1's record: same (verdict clear, refused 0, omitted 30, unconfirmed 0, unverified 0).
- Verdict `clear`. Findings 45, by outcome {"refused": 0, "admitted": 15, "excluded": 0, "omitted": 30, "unconfirmed": 0} (declarations 45, occurrences 0); unverified 0 {}; unassessed constraints 0; advisories 0; check errors 0.

Metrics as printed:

```text
Execution target: generated (override --execution-target; /tmp/l6-evidence-8wa9w5vg/trees/dc3-repaired/pyproject.toml sets none)
Generator subset (subset-profile/v1, subset-coverage/v1): clear: no refusals found by the implemented rules; 0 refused; 0 unverified; 0 unassessed constraints; not a generation check
Coverage limit: no rule yet for DEEP-QUALIFIED-WIRING, ES-002, ES-008, ES-009, ES-010-REFUSAL, CALC-DEF-BARE-RESULT, and 85 follow-up sites; a clear verdict says nothing about these
Generator subset scope: executable profile executable-profile/v4; roots used 6 of 6 (not narrowed); fact kinds not enumerated: none
Calc defs checked: 14
Calc usages checked: 40
Bindings validated: 228
Design attrs checked: 72
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
L6_CONSTRAINT_MALFORMED_NUMERICAL: 0
L6_CONSTRAINT_NON_NUMERICAL: 0
L6_CALC_DEF_NO_INSTANTIATION: 0
L6_ATTR_REDEF_EXPR_DROPPED: 0
```

| Category | Rule / shape / context | Declarations (occurrences) | Outcome | Shown as | Shadowed by |
|---|---|---|---|---|---|
| B1 | `calc-owned-assertion / asserted_constraint / calc_usage_owner` | 0 | - | - | - |
| B2 | `binding-source / expression_source / owner_instantiated` | 0 | - | - | - |
| B3 | `part-multiplicity / unresolved_bound / expanded_part_usage` | 0 | - | - | - |
| B4 | `invocation-callable / unsupported_callable / calc_definition_feature_value` | 0 | - | - | - |
| B5 | `invocation-callable / unsupported_callable / binding_value` | 0 | - | - | - |
| B6 | `conditional-expression / conditional_unresolved_branch / calc_definition_feature_value` | 0 | - | - | - |
| B7 | `string-value-omission / string_value / attribute_value` | 30 | omitted | warning | - |
| B8 | `constraint-predicate / non_numerical_predicate / owner_other` | 0 | - | - | - |
| B8 | `constraint-predicate / blocked_predicate / owner_other` | 0 | - | - | - |

Findings outside B1-B8: `part-multiplicity / unresolved_bound / unexpanded_part_usage (admitted)` 15.

L6 issue codes by display: `L6_SUBSET_OMITTED (warning)` 30.

### One finding per category: location, reason, remedy

- **B7** `ac_coupled_facility::'AC Coupled Facility'::electrical::mv_transformer::conversion_level` at `models/designs/ac_coupled/ac_facility.sysml:45`: omitted, reason `string_value_not_generated`. Remedy: Keep String values as documentation; the generated catalog and contract carry numeric and Boolean values only. Do not bind a String to a calculation input (the ES-010 refusal side).

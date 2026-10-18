# Consumer baseline: `validate --complete models` at the base revision

Written by `scripts/l6_subset/run_consumers.py baseline --base ebb3d467`. agentic-mbse base `ebb3d46710a4c1476bb12fa0e9decf0088ddb2c5`; SysIDE 0.8.4. Each tree is a `git archive` export under /tmp; target unset. Sibling checkouts unchanged: True.

| Tree | Commit | Exit | Wall time (s) | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|---|---|---|
| fusion-tea | `f96ad312` | 1 | 410.9 | passed (0 issues) | failed (465 issues) | passed (0 issues) | passed (0 issues) | passed (0 issues) | failed (408 issues) |
| dc3-baseline | `808464df` | 1 | 35.0 | passed (0 issues) | passed (0 issues) | passed (0 issues) | passed (0 issues) | passed (0 issues) | failed (11 issues) |
| dc3-repaired | `60b44d53` | 0 | 25.7 | passed (0 issues) | passed (0 issues) | passed (0 issues) | passed (0 issues) | passed (0 issues) | passed (0 issues) |

## Settings input per tree

- fusion-tea: root `fusion-tea`, `fusion-tea/pyproject.toml`, tables {"agentic-mbse": "absent", "agentic_mbse": "absent"}
- dc3-baseline: root `dc3-baseline`, `dc3-baseline/pyproject.toml`, tables {"agentic-mbse": "absent", "agentic_mbse": "absent"}
- dc3-repaired: root `dc3-repaired`, `dc3-repaired/pyproject.toml`, tables {"agentic-mbse": "absent", "agentic_mbse": "absent"}

## fusion-tea level blocks

### Level 1: passed

```text
✅ Level 1: Syntax Validation
   Files checked: 80
   Errors: 0
   Warnings: 0
```

### Level 2: failed

```text
❌ Level 2: Structural Completeness
   Unused definitions: 9
   Unbound inputs: 0
   Undefined bindings: 0
   Placeholder bindings: 331
   Self-named bindings: 0
   Orphaned elements: 0
   Positional inputs inspected: 7654
   Positional input outcomes: explicit 0, anonymous 0, implicit_matching 5573, implicit_mismatch 125, new_parameter 1956, special_parameter 0, anonymous_target 0
   Positional bindings (blocking): 125
   Positional bindings pinned (legacy warning): 0
   Positional pins stale: 0
   Positional pins out of scope: 0
   Positional pins not judged (inspection failed): 0
   Positional unverifiable: 0
   Positional pin list: none (looked at /tmp/l6-consumers-xyjqtobp/trees/fusion-tea/positional-pins.toml)

   Issues found: 465
   - WARN: Unused calc def: integrated_heat_electricity::'Heat Driven Closure' at file:models/library/analyses/integrated_heat_electricity.sysml:46
   - WARN: Unused calc def: mfe_account_costs::'Power Supplies Cost' at file:models/library/analyses/mfe_account_costs.sysml:196
   - WARN: Unused calc def: mfe_account_costs::'Divertor Cost' at file:models/library/analyses/mfe_account_costs.sysml:224
   - WARN: Unused calc def: mfe_account_costs::'Aux Cooling Cost' at file:models/library/analyses/mfe_account_costs.sysml:617
   - WARN: Unused calc def: mfe_conductor_current::'Current Driven Pack Sizing' at file:models/library/analyses/mfe_conductor_current.sysml:39
   ... and 460 more
```

### Level 3: passed

```text
✅ Level 3: Dataflow Integrity
   Documents analyzed: 34
   Circular dependencies: 0
```

### Level 4: passed

```text
✅ Level 4: Constraint Coverage
   Total constraints: 345
   ConstraintUsage: 345
   ConstraintDefinition: 42
   Constraint usages assessed (incl. satisfy): 345
   Admitted numerical: 345
   Malformed numerical: 0
   Non-numerical: 0
   Unassessed (satisfy/require/plain): 0
   Executable share: 100.0%
```

### Level 5: passed

```text
✅ Level 5: Traceability & Documentation
   Total elements: 243
   Documented: 243
   Missing docs: 0
   Coverage: 100.0%
```

### Level 6: failed

```text
❌ Level 6: Architecture & Pipeline Readiness
   Calc defs checked: 173
   Calc usages checked: 705
   Bindings validated: 5149
   Design attrs checked: 6180
   Manifests checked: 0
   L6_MISSING_QUALIFIED_NAME: 0
   L6_INVALID_QUALIFIED_NAME: 0
   L6_CALC_DEF_NO_OUTPUT: 0
   L6_CALC_DEF_NO_DIRECTION: 0
   L6_INVALID_BINDING_FORMAT: 0
   L6_DESIGN_ATTR_INCOMPLETE: 119
   L6_DESIGN_ATTR_UNEXTRACTABLE: 108
   L6_ANONYMOUS_RETURN: 0
   L6_BODY_ASSIGNMENT_IMPL_LOSS: 0
   V4_STATIC_FUNCTION_INVOCATION: 0
   L6_CONSTRAINT_MALFORMED_NUMERICAL: 0
   L6_CONSTRAINT_NON_NUMERICAL: 0
   L6_CALC_DEF_NO_INSTANTIATION: 0
   L6_ATTR_REDEF_EXPR_DROPPED: 0

   Issues found: 408
   - ERROR: Derived expression references design attributes: ['electric'] at file:models/designs/aries_cs_integrated/plant.sysml:35
   - ERROR: Derived expression references design attributes: ['electric'] at file:models/designs/aries_cs_integrated/plant.sysml:36
   - ERROR: Derived expression references design attributes: ['electric'] at file:models/designs/aries_cs_integrated/plant.sysml:37
   - ERROR: Derived expression references design attributes: ['ua'] at file:models/designs/aries_cs_integrated/plant.sysml:248
   - ERROR: Derived expression references design attributes: ['ua'] at file:models/designs/aries_cs_integrated/plant.sysml:252
   ... and 403 more
```


## dc3-baseline level blocks

### Level 1: passed

```text
✅ Level 1: Syntax Validation
   Files checked: 23
   Errors: 0
   Warnings: 0
```

### Level 2: passed

```text
✅ Level 2: Structural Completeness
   Unused definitions: 0
   Unbound inputs: 0
   Undefined bindings: 0
   Placeholder bindings: 0
   Self-named bindings: 0
   Orphaned elements: 0
   Positional inputs inspected: 357
   Positional input outcomes: explicit 0, anonymous 0, implicit_matching 302, implicit_mismatch 0, new_parameter 55, special_parameter 0, anonymous_target 0
   Positional bindings (blocking): 0
   Positional bindings pinned (legacy warning): 0
   Positional pins stale: 0
   Positional pins out of scope: 0
   Positional pins not judged (inspection failed): 0
   Positional unverifiable: 0
   Positional pin list: none (looked at /tmp/l6-consumers-xyjqtobp/trees/dc3-baseline/positional-pins.toml)
```

### Level 3: passed

```text
✅ Level 3: Dataflow Integrity
   Documents analyzed: 17
   Circular dependencies: 0
```

### Level 4: passed

```text
✅ Level 4: Constraint Coverage
   Total constraints: 164
   ConstraintUsage: 164
   ConstraintDefinition: 5
   Constraint usages assessed (incl. satisfy): 164
   Admitted numerical: 158
   Malformed numerical: 2
   Non-numerical: 4
   Unassessed (satisfy/require/plain): 0
   Executable share: 96.3%
```

### Level 5: passed

```text
✅ Level 5: Traceability & Documentation
   Total elements: 70
   Documented: 70
   Missing docs: 0
   Coverage: 100.0%
```

### Level 6: failed

```text
❌ Level 6: Architecture & Pipeline Readiness
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
   L6_DESIGN_ATTR_UNEXTRACTABLE: 3
   L6_ANONYMOUS_RETURN: 0
   L6_BODY_ASSIGNMENT_IMPL_LOSS: 0
   V4_STATIC_FUNCTION_INVOCATION: 0
   L6_CONSTRAINT_MALFORMED_NUMERICAL: 4
   L6_CONSTRAINT_NON_NUMERICAL: 4
   L6_CALC_DEF_NO_INSTANTIATION: 0
   L6_ATTR_REDEF_EXPR_DROPPED: 0

   Issues found: 11
   - WARN: Constraint 'dc3_baseline_annual::annual_reference::ac_demand::input_domain' is not a numerical statement and will not execute: warn_non_numerical_predicate at models/designs/examples/baseline_annual.sysml:57
   - ERROR: Constraint 'dc3_baseline_costs::cost_reference::ac_total::delivered_domain' is a malformed numerical statement: feature_ref (block_non_numerical_containment) at models/designs/examples/baseline_costs.sysml:74
   - ERROR: Constraint 'dc3_baseline_costs::cost_reference::ac_total::delivered_domain' is a malformed numerical statement: feature_ref (block_non_numerical_containment) at models/designs/examples/baseline_costs.sysml:74
   - WARN: Constraint 'dc3_baseline_annual::annual_reference::ac_balance::input_domain' is not a numerical statement and will not execute: warn_non_numerical_predicate at models/designs/examples/baseline_annual.sysml:84
   - WARN: Constraint 'dc3_baseline_annual::annual_reference::dc_demand::input_domain' is not a numerical statement and will not execute: warn_non_numerical_predicate at models/designs/examples/baseline_annual.sysml:97
   ... and 6 more
```


## dc3-repaired level blocks

### Level 1: passed

```text
✅ Level 1: Syntax Validation
   Files checked: 24
   Errors: 0
   Warnings: 0
```

### Level 2: passed

```text
✅ Level 2: Structural Completeness
   Unused definitions: 0
   Unbound inputs: 0
   Undefined bindings: 0
   Placeholder bindings: 0
   Self-named bindings: 0
   Orphaned elements: 0
   Positional inputs inspected: 528
   Positional input outcomes: explicit 0, anonymous 0, implicit_matching 391, implicit_mismatch 0, new_parameter 137, special_parameter 0, anonymous_target 0
   Positional bindings (blocking): 0
   Positional bindings pinned (legacy warning): 0
   Positional pins stale: 0
   Positional pins out of scope: 0
   Positional pins not judged (inspection failed): 0
   Positional unverifiable: 0
   Positional pin list: none (looked at /tmp/l6-consumers-xyjqtobp/trees/dc3-repaired/positional-pins.toml)
```

### Level 3: passed

```text
✅ Level 3: Dataflow Integrity
   Documents analyzed: 15
   Circular dependencies: 0
```

### Level 4: passed

```text
✅ Level 4: Constraint Coverage
   Total constraints: 99
   ConstraintUsage: 99
   ConstraintDefinition: 6
   Constraint usages assessed (incl. satisfy): 99
   Admitted numerical: 99
   Malformed numerical: 0
   Non-numerical: 0
   Unassessed (satisfy/require/plain): 0
   Executable share: 100.0%
```

### Level 5: passed

```text
✅ Level 5: Traceability & Documentation
   Total elements: 80
   Documented: 80
   Missing docs: 0
   Coverage: 100.0%
```

### Level 6: passed

```text
✅ Level 6: Architecture & Pipeline Readiness
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

# Constraint Patterns

Syntax and patterns for SysML v2 constraints including prefix keywords, assertion types, and common use cases.

## When to Use This Document

Reference this document when:
- Writing constraints in models
- Understanding constraint prefix keywords
- Debugging "constraint not recognized" issues
- Choosing between assert, require, and assume

## Quick Reference

```sysml
// Basic constraint syntax
assert constraint ConstraintName {
    doc /* Description of what this constraint enforces */
    expression_that_must_be_true
}
```

**Critical:** Constraints require a prefix keyword (`assert`, `require`, or `assume`).

**An `assert` constraint's predicate is eligible for execution, not automatically dropped.**
The **executable profile v4** (`agentic_mbse.sysml.executable_profile`) assigns exactly one of four
outcomes per constraint usage:

- **`ADMIT`** — the predicate uses only supported constructs (comparisons, `and`/`or`/`not`,
  arithmetic, feature references, unit-annotated literals) and lowers into a real check
  downstream (sysml-codegen). L4 counts it eligible; L6 stays silent.
- **`BLOCK`** — some construct in the predicate isn't in the admitted set. Generation stops, and
  L6 emits one named ERROR per blocked construct (the construct, its source location, and a reason code like
  `block_feature_chain` or `block_real_equality_requires_tolerance`) — see
  [Executable Profile: Block List](#executable-profile-block-list) below.
- **`NON_NUMERICAL`** — a valid Boolean, string, or enumeration statement is outside numerical
  execution. Validation and generation warn, and codegen catalogs it without an executable module.
- **`UNASSESSED`** — `satisfy` constraints, requirement-side usages, and plain (unprefixed)
  constraints aren't run through the profile at all; they're cataloged separately, not blocked.

`require` and `assume` constraints are unassessed today (only `assert` predicates are walked).
If a constraint expresses a value the pipeline needs and its predicate blocks, move that
computation into a calc def instead.

---

## Constraint Prefix Keywords

| Prefix | Purpose | When to Use |
|--------|---------|-------------|
| `assert` | Invariant that must always hold | Physical laws, design rules |
| `require` | Precondition that must be satisfied | Input validation, prerequisites |
| `assume` | Assumption made by the model | Environmental conditions, simplifications |

---

## Syntax Examples

### Assert Constraint (Most Common)

```sysml
assert constraint EnergyConservation {
    doc /* Input energy must equal output energy within 0.1% */
    energy_in > energy_out * 0.999 and
    energy_in < energy_out * 1.001
}

assert constraint PositiveValue {
    doc /* Value must be positive */
    value > 0
}

assert constraint OperatingLimit {
    doc /* Must not exceed operating limit */
    temperature < max_temperature
}
```

### Require Constraint

```sysml
require constraint ValidInput {
    doc /* Input parameters must be within valid range */
    input_power > 0 [MW] and input_power < 10000 [MW]
}

require constraint NonZeroDenominator {
    doc /* Divisor must not be zero */
    divisor != 0
}
```

### Assume Constraint

```sysml
assume constraint SteadyState {
    doc /* Model assumes steady-state operation */
    d_temperature_dt == 0
}

assume constraint IdealGas {
    doc /* Assumes ideal gas behavior */
    pressure * volume == n * R * temperature
}
```

---

## Constraint in Different Contexts

### In Part Definitions

```sysml
part def 'Pressure Vessel' {
    attribute pressure : Pressure;
    attribute max_pressure : Pressure;

    assert constraint PressureLimit {
        doc /* Operating pressure must not exceed design limit */
        pressure <= max_pressure
    }
}
```

### In Calc Definitions

```sysml
calc def PowerCalculation {
    in attribute voltage : Real;
    in attribute current : Real;
    out attribute power : Real = voltage * current;

    assert constraint ReasonablePower {
        doc /* Output power must be reasonable */
        power > 0 and power < 1e9
    }
}
```

### In Design Usages

```sysml
part my_vessel : 'Pressure Vessel' {
    attribute pressure = 10 [MPa];
    attribute max_pressure = 15 [MPa];

    // Can add design-specific constraints
    assert constraint SafetyMargin {
        doc /* Maintain 30% safety margin */
        pressure < max_pressure * 0.7
    }
}
```

---

## Compound Constraints

### Logical Operators

```sysml
assert constraint ComplexCondition {
    doc /* Multiple conditions must hold */
    temperature > 0 [K] and
    temperature < 1000 [K] and
    (pressure < 10 [MPa] or is_reinforced)
}
```

### Range Constraints

```sysml
assert constraint InRange {
    doc /* Value must be within range */
    value >= min_value and value <= max_value
}
```

### Equality Constraints

```sysml
assert constraint Conservation {
    doc /* Conservation law */
    mass_in == mass_out
}
```

---

## Common Mistakes

### Wrong: Plain constraint block (no prefix)

```sysml
// WRONG: Not recognized as ConstraintUsage!
constraint TempLimit {
    temperature < 1000 [K]
}
```

**Error:** Parser does not create proper AST node without prefix.

### Correct: With prefix

```sysml
// CORRECT: Creates ConstraintUsage
assert constraint TempLimit {
    doc /* Operating temperature must not exceed limit */
    temperature < 1000 [K]
}
```

### Wrong: Missing doc comment

```sysml
// BAD: No explanation
assert constraint X {
    a < b
}

// GOOD: Documented
assert constraint SafeLimit {
    doc /* Safety limit per standard XYZ-123 */
    a < b
}
```

### Wrong: Overly complex single constraint

```sysml
// BAD: Too much in one constraint
assert constraint Everything {
    a > 0 and b > 0 and c > 0 and a + b > c and
    temp < max_temp and pressure < max_pressure and
    efficiency > 0.8 and ...
}

// GOOD: Separate concerns
assert constraint PositiveValues {
    a > 0 and b > 0 and c > 0
}

assert constraint TriangleInequality {
    a + b > c
}

assert constraint ThermalLimits {
    temp < max_temp
}
```

---

## Constraint Expression Operators

| Operator | Meaning | Example | Executable profile |
|----------|---------|---------|---------------------|
| `==` | Equal | `mode == 1` | Never admitted. Boolean, string, and enumeration equality is `NON_NUMERICAL`; integer, real, and quantity equality is `BLOCK` — see below. |
| `!=` | Not equal | `divisor != 0` | Never admitted. It follows the same `NON_NUMERICAL`/`BLOCK` type split as `==`. |
| `<`, `<=` | Less than | `temp < max_temp` | Admitted only for Integer/Real operands or two Quantity operands with the same exact unit. |
| `>`, `>=` | Greater than | `power > 0` | Admitted only for Integer/Real operands or two Quantity operands with the same exact unit. |
| `and`, `or`, `not` | Logical connectives | `a > 0 and b > 0` | Admitted; each operand is walked as its own predicate. |
| `xor`, `implies` | Logical XOR/implication | — | A valid binary expression is classified by numerical containment: a purely non-numerical statement is `NON_NUMERICAL`, while one containing a numerical assertion is `BLOCK`. Any arity other than two default-denies as `BLOCK`. |

### The four executable-profile outcomes

Executable-profile v4 assigns exactly one outcome to each constraint usage:

- `ADMIT`: the predicate is in the numerical execution subset and may be lowered.
- `BLOCK`: generation stops with an error and repair guidance.
- `NON_NUMERICAL`: the statement is valid but is not a numerical execution claim. Validation and
  generation warn, and code generation catalogs it without an executable module.
- `UNASSESSED`: the usage kind or source form is outside the profile. Code generation catalogs it
  without walking or executing its predicate.

Assertion polarity is classified separately from the positive predicate. A positive assertion
expects the unchanged positive predicate to be true; a negated assertion expects that same positive
predicate to be false. Generated execution preserves the predicate's raw value and applies polarity
exactly once when deriving status and the sign of a simple margin. A malformed non-Boolean polarity
blocks with repair guidance before the predicate body is walked.

Ordering is a numerical operation. Boolean, String, enumeration, unresolved, unknown, and mixed
Quantity/scalar pairs do not inherit host-language comparison semantics. They block with a stable
diagnostic that asks the author to use Integer/Real operands or two Quantity operands.

### Real-valued equality: use a two-inequality band, not `==`

No equality or inequality enters numerical execution. Boolean, string, and enumeration equality
or inequality is a `NON_NUMERICAL` statement and produces a warning. Integer equality or
inequality is `BLOCK` because the generated float path cannot preserve integer equality semantics.
Real equality or inequality is `BLOCK` because it has no modeled tolerance. Quantity equality or
inequality is also `BLOCK`: identical units still need a tolerance, while mismatched or unknown
units retain their specific unit diagnostic. Express a real or quantity equality intent as an
explicit tolerance band with two inequalities:

```sysml
// WRONG: blocks — real-valued equality has no tolerance
assert constraint EnergyBalance {
    energy_in == energy_out
}

// CORRECT: explicit two-inequality band
assert constraint EnergyBalance {
    energy_in > energy_out * 0.999 and
    energy_in < energy_out * 1.001
}
```

### Executable profile: block list

Besides numerical equality/inequality and unit mismatches, these constructs block:

| Construct | Reason code | Why |
|-----------|-------------|-----|
| Dotted feature chain (e.g. `part.sub.attr`) | `block_feature_chain` | Not resolvable to a single operand fact. |
| Function/operation call | `block_invocation` | No evaluator for arbitrary invocations. |
| Reference to a named constraint usage (no inline predicate) | `block_assert_by_reference` | Nothing to walk without an inline or definition-typed predicate. |
| Unresolved or unrecognized operand/expression shape | `block_unresolved_operand`, `block_unsupported_node`, `block_unsupported_operand_category` | Default-deny — the profile only admits constructs it recognizes. |

`require` and `assume` constraints, `satisfy` usages, and plain (unprefixed) constraints are
`UNASSESSED`: the profile does not walk their predicates, so they are neither admitted nor
blocked.

---

## Constraint Definitions (Reusable)

For reusable constraint patterns:

```sysml
// Library: Define constraint pattern
constraint def PositiveReal {
    in attribute value : Real;
    value > 0
}

// Usage: Apply constraint
part component {
    attribute mass : Real;
    assert constraint mass_positive : PositiveReal {
        in value = mass;
    }
}
```

---

## Subtype-aware validation: `assert` constraints are now visible (Item 4)

The validators enumerate constraint usages with a subtype-aware sweep, so an
`assert constraint` (an `AssertConstraintUsage`, a `ConstraintUsage` *subtype*) is now seen
everywhere a plain `ConstraintUsage` is:

- **L4** (constraint coverage) reports all four eligibility counts — admitted, blocked,
  non-numerical, and unassessed —
  across all `assert`/`require`/`assume`/`satisfy` constraints, via the executable profile
  (Item 3): `assert` predicates land in admitted, blocked, or non-numerical; everything else lands
  in unassessed. Before Item 4 it undercounted asserts; before Item 3 it reported a 0%
  attribute-coverage placeholder that never parsed a predicate.
- **L6** emits one named ERROR per blocked construct (not one blanket error per constraint
  usage) — see [Executable profile: block list](#executable-profile-block-list) above.

Requirement-side usages (`RequirementUsage` and its `satisfy` subtype) are deliberately
excluded from the eligibility sweep — they are requirement-side, cataloged unassessed, not
walked as predicates. The full per-call-site rationale is the reference table:
`docs/subtype-enumeration-decision-table.md`.

Modeler takeaway: an `assert constraint` you write is now surfaced by construct and reason if
its predicate blocks, not collapsed into a blanket "not executable" warning. Move any
computation an ineligible predicate expresses into a calc def instead.

---

## Related Patterns

- [semantic-operators.md](semantic-operators.md) - Constraint syntax requirements
- [syntax-reference.md](syntax-reference.md) - General constraint syntax
- [mbse-concepts.md](mbse-concepts.md) - Parametric constraint pattern
- [common-mistakes.md](common-mistakes.md) - Constraint anti-patterns

---

## Verification

Constraints are syntax-checked by the parser:

```bash
syside check <file.sysml>
```

**Note:** The parser verifies syntax; it does not itself evaluate constraint truth values. Run
`agentic-mbse validate --level=4` for executable-profile eligibility counts, or
`--level=6` for named per-construct diagnostics on blocked predicates. Actual runtime evaluation
of admitted predicates happens downstream, in the generated pipeline (sysml-codegen).

---

*Last Updated: 2026-07-13*

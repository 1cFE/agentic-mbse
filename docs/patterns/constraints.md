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

**Constraints are not executable.** They document intent — they are dropped at
extraction and produce no computation in the generated pipeline (the validator WARNs when
a model carries constraint usages). If a constraint expresses a value the pipeline needs,
move that computation into a calc def. Canonical rule: modeling-assumptions §8
("constraints are not executable"), in the sysml-codegen repo.

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

| Operator | Meaning | Example |
|----------|---------|---------|
| `==` | Equal | `mass_in == mass_out` |
| `!=` | Not equal | `divisor != 0` |
| `<`, `<=` | Less than | `temp < max_temp` |
| `>`, `>=` | Greater than | `power > 0` |
| `and` | Logical AND | `a > 0 and b > 0` |
| `or` | Logical OR | `mode == 1 or mode == 2` |
| `not` | Logical NOT | `not is_disabled` |

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

**Note:** Parser verifies syntax but does not evaluate constraint truth values. Runtime evaluation requires execution framework.

---

*Last Updated: 2026-01-15*

# SysML v2 Conditional Expressions

Definitive syntax reference for conditional expressions in SysML v2 / KerML.

## Quick Reference

| Syntax | Status |
|--------|--------|
| `if CONDITION? TRUE_VALUE else FALSE_VALUE` | **CORRECT** |
| `condition ? trueValue : falseValue` | WRONG (C-style ternary) |
| `if condition then trueValue else falseValue endif` | WRONG |

## Syntax Rules

1. **`if`** keyword starts the conditional
2. **`?`** separates condition from true branch (NOT after true value like C-style)
3. **`else if`** for additional conditions
4. **`else`** for final fallback
5. **NO `then` keyword**
6. **NO `endif` terminator**
7. **NO C-style ternary `? :`**

## Examples

### Basic Conditional

```sysml
attribute diff : Real = if x > y? x - y else y - x;
```

### Chained Conditionals

```sysml
attribute factor : Real =
    if mode == 1? 0.95
    else if mode == 2? 0.85
    else 0.60;
```

### Enum Conditionals

```sysml
attribute alpha_fraction : Real =
    if fuel_type == FuelType::DT? 0.2002
    else if fuel_type == FuelType::DD? 0.5001
    else if fuel_type == FuelType::DHE3? 0.8033
    else 1.0;
```

### In Calc Definitions

```sysml
calc def ConditionalTest {
    in attribute x : Real;
    in attribute y : Real;
    out attribute diff : Real = if x > y? x - y else y - x;
}
```

## Common Mistakes

### C-style Ternary (WRONG)

```sysml
// WRONG - will not parse
attribute x = condition ? trueValue : falseValue;
```

**Error:** Parser fails at `?` - unexpected token

### if-then-else-endif (WRONG)

```sysml
// WRONG - will not parse
attribute x = if condition then trueValue else falseValue endif;
```

**Error:** `then` creates invalid parse tree

### Missing ? After Condition (WRONG)

```sysml
// WRONG - missing ?
attribute x = if condition trueValue else falseValue;
```

## When to Use Conditionals vs Type Specialization

| Approach | Use When |
|----------|----------|
| **Conditional expressions** | Simple parameter selection, few variants, values differ by condition |
| **Type specialization** | Complex variant behavior, many variants, need separate documentation per variant |

### Conditional Expression Example

```sysml
// Good for simple parameter variation
attribute efficiency : Real =
    if temperature < 100? 0.95
    else if temperature < 300? 0.85
    else 0.60;
```

### Type Specialization Example

```sysml
// Good for complex variants with different behaviors
abstract calc def PowerBalanceCalcBase {
    attribute alpha_fraction : Real;  // To be specialized
}

calc def PowerBalanceCalcDT :> PowerBalanceCalcBase {
    :>> alpha_fraction = 0.2002;
    // Can add DT-specific behavior here
}

calc def PowerBalanceCalcDD :> PowerBalanceCalcBase {
    :>> alpha_fraction = 0.5001;
    // Can add DD-specific behavior here
}
```

## Verification

All examples verified with syside v0.8.1 parser.

**Test command:**
```bash
syside check <file.sysml>
```

Exit code 0 indicates successful parse.

## Sources

- **Official KerML Examples:** [SysML-v2-Release/kerml/src/examples/Simple Tests/Expressions.kerml](https://github.com/Systems-Modeling/SysML-v2-Release)
- **Research:** `.project/research/20260109-213422_sysmlv2-conditional-expressions-definitive.md`

---

*Last Updated: 2026-01-09*

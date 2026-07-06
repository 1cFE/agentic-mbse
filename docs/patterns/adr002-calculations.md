# Calculation Architecture (ADR-002)

Architectural decision record for calculation placement: `calc def` in library, values and wiring in designs.

## When to Use This Document

Reference this document when:
- Deciding where to place calculation logic
- Understanding what expressions are valid in design files
- Resolving "derived expression" violations
- Building cost/analysis calculation hierarchies

## Core Principle

> **Calculation definitions belong in `library/`. Design files contain values and wiring. Expressions that resolve to constants are evaluated at extraction time.**

This extends the Definitions vs Usages pattern:
- `library/` = Reusable algorithms (calc defs) + type definitions (part defs)
- `designs/` = Configuration (values, bindings, calc usages)

---

## Calculation Location Rules

| Rule | Specification |
|------|---------------|
| **Rule 1** | `calc def` declarations SHALL be in `models/library/` only |
| **Rule 2** | Calc usages in `designs/` wire library calc defs to design values |
| **Rule 3** | Design attributes contain literals, bindings, static expressions, or a simple **inline FORMULA** over same-part siblings — reserve real calculations for calc defs |

---

## Expression Taxonomy

| Expression Type | Location | Feature Refs | Result | Example |
|-----------------|----------|--------------|--------|---------|
| **Literal value** | `designs/` attribute | 0 | PASS | `= 3.0 [m]` |
| **True static** | `designs/` attribute | 0 | PASS | `= 3.14159 * 2.0` |
| **EXPOSE pattern** | `designs/` attribute | 1 (calc output) | PASS | `= my_calc.output` |
| **Calc def formula** | `library/` calc def | N/A | N/A | `out result : Real = input * 0.2;` |
| **Binding reference** | Calc usage binding | N/A | N/A | `in value = system.property;` |
| **Inline FORMULA** | `designs/` attribute | ≥1 (same-part sibling) | PASS¹ | `= radius * 2.0` |
| **Computation on calc output** | `designs/` attribute | ≥1 (calc output) | **FAIL** | `= calc.power * 0.95` |
| **Self / dotted reference** | `designs/` attribute | self, or a dotted path | **FAIL** | `= self.x`, `= a.b.c` |

¹ Accepted as a convenience for simple arithmetic and unit conversions over same-part
sibling attributes. For any real or reusable calculation, use a calc def in `library/`
(see [Inline FORMULA vs Calc Def](#inline-formula-vs-calc-def) below).

---

## Valid Patterns in Design Files

```sysml
part component {
    // Literal values (entry points)
    attribute dimension_a : Real = 3.0 [m];
    attribute dimension_b : Real = 5.0 [m];

    // True static expressions (ONLY literals)
    attribute pi_squared : Real = 3.14159 * 3.14159;

    // Inline FORMULA (simple arithmetic over same-part siblings)
    attribute area : Real = dimension_a * dimension_b;

    // EXPOSE pattern (pure value propagation from calc output)
    attribute result : Real = my_calc.output;
}
```

---

## Inline FORMULA vs Calc Def

A design attribute may reference **same-part sibling** attributes — a supported "inline
FORMULA" computed attribute. Reserve it for simple arithmetic and unit conversions:

```sysml
part component {
    attribute length : Real = 3.0 [m];
    attribute width  : Real = 4.0 [m];

    // Inline FORMULA: fine for simple arithmetic over same-part siblings.
    attribute area : Real = length * width;
}
```

For any real or reusable calculation, still prefer a `calc def` in `library/`. It is
named, testable, and reused across designs — the inline form is a convenience, not a
replacement:

```sysml
// library/geometry.sysml
calc def AreaCalculation {
    in length : Real;
    in width : Real;
    out area : Real = length * width;
}

// designs/component.sysml
part component {
    attribute length : Real = 3.0 [m];
    attribute width : Real = 4.0 [m];

    calc area_calc : AreaCalculation {
        in length = component::length;
        in width = component::width;
    }
    attribute area : Real = area_calc.area;  // EXPOSE pattern
}
```

**What an inline FORMULA may NOT do** — these still fail and must move into a calc def:
- compute on a calc output — `= power_calc.power * 0.95`
- reference itself — `= area * 2` inside `area`
- reach through a dotted path — `= subsystem.rotor.power`

---

## Supported Static Operators

| Operator | Example |
|----------|---------|
| `+`, `-`, `*`, `/` | `a + b`, `a * 2.0` |
| `[` (unit annotation) | `3.0 [m]` |

**Not supported in design attributes** (require calc def):
- Exponentiation (`**`, `^`)
- Functions (`sin`, `sqrt`, `abs`)
- Conditionals (`if ... else`)
- A reference to a calc output inside arithmetic, a self-reference, or a dotted path
  (a plain same-part sibling reference is an inline FORMULA — allowed)

---

## No Loops (rule A-3)

The computation graph must be a DAG — no calc may depend, directly or transitively, on
its own output. A cycle (`A` binds an input from `B`'s output, `B` binds an input from
`A`'s output) has no valid execution order and is rejected. Break the cycle: introduce an
intermediate value, or restructure so one calc produces what the other consumes. See the
circular-dependency example in `semantic-operators.md`.

---

## Validated Patterns

### Multiplicity Cost Aggregation

**Status:** Validated CORRECT (2026-01-12)
**Evidence:** `syside check` passes with no errors or warnings

Use `import NumericalFunctions::sum` then `sum(child.capital_cost)` to aggregate costs from parts with multiplicity `[N]`.

**Correct Pattern:**
```sysml
private import NumericalFunctions::sum;

part def 'Assembly' :> 'Costed Component' {
    part child : 'Child Component' [N];
    :>> capital_cost = sum(child.capital_cost);  // Automatic aggregation!
}
```

**Anti-Pattern (DO NOT USE):**
```sysml
// BROKEN: Hardcoded values that will drift
attribute child_total_cost : Real;  // Placeholder
:>> capital_cost = child_total_cost;  // Bound in design with hardcoded value
```

**Why:** The `sum()` function automatically aggregates over the multiplicity, keeping the model DRY and accurate.

---

## Common Mistakes

### Putting calc def in designs

```sysml
// WRONG: Calc def in design file
package MyDesign {
    calc def MyFormula {  // VIOLATION of ADR-002!
        in x : Real;
        out y : Real = x * 2;
    }
}

// CORRECT: Calc def in library
package MyLibrary::Analyses {
    calc def MyFormula {
        in x : Real;
        out y : Real = x * 2;
    }
}
```

### Self-reference or dotted path in an inline FORMULA

An inline FORMULA may read same-part siblings only — not itself, and not through a
dotted path into another part.

```sysml
// WRONG: self-reference (a FORMULA may not read its own value)
attribute total : Real = total + 1.0;

// WRONG: dotted path into another part
attribute p : Real = subsystem.rotor.power;

// OK: same-part siblings
attribute margin : Real = revenue - cost;
```

### Computation on calc output

```sysml
// WRONG: Further computation on calc output
attribute adjusted_power : Real = power_calc.power * 0.95;  // Computation!

// CORRECT: Include adjustment in calc def
calc def AdjustedPowerCalc {
    in raw_power : Real;
    in efficiency : Real default := 0.95;
    out adjusted_power : Real = raw_power * efficiency;
}
```

---

## Decision Flow

```
Is this expression in a design attribute?
|
+-- Only literals? -> Static expression -> OK
|   (e.g., = 3.14159 * 2.0)
|
+-- Only same-part siblings? -> Inline FORMULA -> OK for simple arithmetic
|   (e.g., = length * width; prefer a calc def for real calculations)
|
+-- Just exposing one calc output? -> EXPOSE pattern -> OK
|   (e.g., = my_calc.output)
|
+-- Calc output in arithmetic, self-reference, or dotted path -> EXTRACT TO CALC DEF
    (e.g., = calc.power * 0.95)
```

---

## Related Patterns

- [definitions-usages.md](definitions-usages.md) - Definition vs Usage distinction
- [expose-pattern.md](expose-pattern.md) - EXPOSE pattern for calc outputs
- [semantic-operators.md](semantic-operators.md) - Binding operators
- [mbse-concepts.md](mbse-concepts.md) - Cost calculation patterns

---

## Verification

All examples verified with syside parser.

**Test command:**
```bash
syside check <file.sysml>
```

---

*Last Updated: 2026-01-15*

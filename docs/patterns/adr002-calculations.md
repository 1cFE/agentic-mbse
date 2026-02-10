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
| **Rule 3** | Design attributes contain literals, bindings, static expressions, or **FORMULA expressions** (sibling-only arithmetic per [ADR-002 Amendment](#formula-computed-attributes)) |

---

## Expression Taxonomy

| Expression Type | Location | Feature Refs | Result | Example |
|-----------------|----------|--------------|--------|---------|
| **Literal value** | `designs/` attribute | 0 | PASS | `= 3.0 [m]` |
| **True static** | `designs/` attribute | 0 | PASS | `= 3.14159 * 2.0` |
| **FORMULA expression** | `designs/` attribute | >=1 (sibling attrs only) | **PASS** | `= length * width` |
| **EXPOSE pattern** | `designs/` attribute | 1 (calc output) | PASS | `= my_calc.output` |
| **Calc def formula** | `library/` calc def | N/A | N/A | `out result : Real = input * 0.2;` |
| **Binding reference** | Calc usage binding | N/A | N/A | `in value = system.property;` |
| **Derived expression** | `designs/` attribute | >=1 (calc output refs) | **FAIL** | `= calc.output * 0.95` |

---

## Valid Patterns in Design Files

```sysml
part component {
    // Literal values (entry points)
    attribute dimension_a : Real = 3.0 [m];
    attribute dimension_b : Real = 5.0 [m];

    // True static expressions (ONLY literals, no design attribute refs)
    attribute pi_squared : Real = 3.14159 * 3.14159;

    // FORMULA expressions (sibling attributes only, per ADR-002 Amendment)
    attribute area : Real = dimension_a * dimension_b;

    // EXPOSE pattern (pure value propagation from calc output)
    attribute result : Real = my_calc.output;
}
```

---

## Invalid Pattern: Derived Expression

> **Amendment (2026-02-09):** The expression below (`length * width`) is now **valid** as a FORMULA computed attribute when all references are sibling attributes on the same part. The codegen pipeline auto-generates a module for it (see ADR-004). The CalcDef resolution shown below remains a valid alternative for reusable or complex formulas. See [FORMULA Computed Attributes](#formula-computed-attributes) below.

```sysml
part component {
    attribute length : Real = 3.0 [m];
    attribute width : Real = 4.0 [m];

    // VALID as FORMULA (all refs are siblings on same part)
    // OR extract to CalcDef for reusable/complex formulas
    attribute area : Real = length * width;
}
```

**When this is still a violation:** If the expression references calc outputs (e.g., `calc.output * 0.95`) or attributes on other parts (cross-part references), it remains a derived expression violation. Only sibling attribute references on the same part qualify as FORMULA.

### Resolution: Extract to Calc Def

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
- Cross-part attribute references or calc output references

**Supported via FORMULA** (per ADR-002 Amendment):
- References to sibling attributes on the same part (`+`, `-`, `*`, `/`)
- Example: `attribute area = length * width` where `length` and `width` are siblings

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

### Derived expressions in attributes

```sysml
// STILL WRONG: Computation on a calc output
attribute adjusted_power : Real = power_calc.power * 0.95;  // Calc output ref!

// NOW VALID: FORMULA — all refs are sibling attributes (per ADR-002 Amendment)
attribute diameter : Real = radius * 2.0;  // 'radius' is a sibling on same part

// ALSO VALID: CalcDef alternative (preferred for reusable/complex formulas)
calc diameter_calc : DiameterCalc {
    in radius = component::radius;
}
attribute diameter : Real = diameter_calc.diameter;
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

### Using CalcDef when FORMULA suffices

```sysml
// UNNECESSARY: CalcDef ceremony for a one-off sibling formula
calc def AreaCalc {
    in length : Real;
    in width : Real;
    out area : Real = length * width;
}
calc area_calc : AreaCalc {
    in length = component::length;
    in width = component::width;
}
attribute area : Real = area_calc.area;

// SIMPLER: FORMULA attribute expression (per ADR-002 Amendment)
attribute area : Real = length * width;  // All refs are siblings — valid!
```

**When to use CalcDef instead:** Reusable formulas shared across parts, complex logic with multiple intermediates, or expressions referencing calc outputs.

---

## Decision Flow

```
Is this expression in a design attribute?
|
+-- Does it reference other features (attributes, calc outputs)?
    |
    +-- NO: Static expression -> OK
    |   (e.g., = 3.14159 * 2.0)
    |
    +-- YES: Are ALL references sibling attributes on the same part?
        |
        +-- YES: FORMULA computed attribute -> OK
        |   (e.g., = length * width)
        |   Generates a pipeline module (ADR-004)
        |
        +-- NO: Is it a single reference exposing a calc output?
            |
            +-- YES: EXPOSE pattern -> OK
            |   (e.g., = my_calc.output)
            |
            +-- NO: Derived expression -> EXTRACT TO CALC DEF
                (e.g., = calc.output * 0.95)
```

---

## FORMULA Computed Attributes

> **Added 2026-02-09 per ADR-002 Amendment, ADR-004, ADR-005**

Design attributes MAY contain arithmetic expressions referencing **only sibling attributes** on the same part. These are classified as FORMULA computed attributes and generate synthetic pipeline modules with auto-implemented code.

### Conditions (all must hold)

- All feature references resolve to sibling attributes (same owning part)
- No `FeatureChainExpression` nodes (no calc output references, no cross-part references)
- Supported operators: `+`, `-`, `*`, `/`

### Examples

```sysml
part plant {
    attribute length : Real = 10.0;
    attribute width : Real = 5.0;
    attribute rate : Real = 12.0;
    attribute p_net_mw : Real = 0.008;

    // FORMULA: simple binary (siblings only)
    attribute area : Real = length * width;

    // FORMULA: chain — references another computed attr (still a sibling)
    attribute cost : Real = area * rate;

    // FORMULA: unit conversion with literal
    attribute p_net_kw : Real = p_net_mw * 1000.0;
}
```

### FORMULA vs CalcDef

| Use | When |
|-----|------|
| **FORMULA** (attribute expression) | One-off formula, sibling attrs only, simple arithmetic |
| **CalcDef** (library/) | Reusable logic, complex expressions, calc output refs, functions |

### Related ADRs

- **ADR-002 Amendment**: Rule 3 relaxation conditions, modeling guidance
- **ADR-004**: Pipeline integration — Option C, Step 4.5, synthetic module naming
- **ADR-005**: 5-way classification scheme (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE)

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

*Last Updated: 2026-02-09*

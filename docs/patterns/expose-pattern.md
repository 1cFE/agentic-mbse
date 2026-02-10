# The EXPOSE Pattern

The EXPOSE pattern makes calculation outputs accessible as design attributes, enabling cross-file access and encapsulation.

## When to Use This Document

Reference this document when:
- Making calc outputs accessible to other parts of the model
- Establishing cross-file dataflow
- Encapsulating internal calculations
- Designing stable interfaces for components

## Quick Reference

```sysml
part geometry {
    // Calc produces a value
    calc dimension_calc : DimensionCalculation {
        in length = geometry::input_length;
        in width = geometry::input_width;
    }

    // EXPOSE: Design attribute exposes the calc output
    attribute calculated_area : Real = dimension_calc.area;
}
```

Consumers bind to `geometry.calculated_area`, not `geometry.dimension_calc.area`.

---

## Why Use EXPOSE

### 1. Encapsulation

Other parts reference `geometry.calculated_area` without knowing it comes from a calc. The internal implementation is hidden.

### 2. Cross-File Access

Design attributes are visible across files via imports. Calc outputs are not directly accessible cross-file.

```sysml
// File: consumer.sysml
private import GeometryPackage::geometry;

calc my_calc {
    in area = geometry.calculated_area;  // Works!
    // in area = geometry.dimension_calc.area;  // Doesn't work cross-file
}
```

### 3. Interface Stability

You can change the internal calculation without affecting consumers. As long as the exposed attribute name stays the same, consumers don't need to change.

---

## How to Use

### Producer Side (EXPOSE)

```sysml
part producer_part {
    // Internal calculation
    calc some_calc : SomeCalcDef {
        in input_a = producer_part::param_a;
        in input_b = producer_part::param_b;
    }

    // EXPOSE: Make output accessible as design attribute
    attribute exposed_value : Real = some_calc.output;
}
```

### Consumer Side (Transitive Binding)

```sysml
// Import the producer instance
private import ProducerPackage::producer_part;

calc consumer_calc : OtherCalcDef {
    // Bind to EXPOSED attribute
    in x = producer_part.exposed_value;
}
```

---

## Complete Example

### Library: Calculation Definition

```sysml
// library/analyses/geometry.sysml
package MyProject::Library::Analyses {
    calc def AreaCalculation {
        in attribute length : Real;
        in attribute width : Real;
        out attribute area : Real = length * width;
    }
}
```

### Design: Producer with EXPOSE

```sysml
// designs/my_design/geometry.sysml
package MyProject::Designs::MyDesign::Geometry {
    private import MyProject::Library::Analyses::AreaCalculation;

    part geometry_module {
        // Input parameters
        attribute input_length : Real = 10.0 [m];
        attribute input_width : Real = 5.0 [m];

        // Internal calculation
        calc area_calc : AreaCalculation {
            in length = geometry_module::input_length;
            in width = geometry_module::input_width;
        }

        // EXPOSE: Make area accessible
        attribute total_area : Real = area_calc.area;
    }
}
```

### Design: Consumer Using EXPOSED Value

```sysml
// designs/my_design/cost.sysml
package MyProject::Designs::MyDesign::Cost {
    private import MyProject::Designs::MyDesign::Geometry::geometry_module;
    private import MyProject::Library::Analyses::CostCalculation;

    part cost_module {
        calc cost_calc : CostCalculation {
            // Use EXPOSED attribute from geometry
            in area = geometry_module.total_area;
            in cost_per_sqm = 100.0;
        }

        attribute total_cost : Real = cost_calc.cost;
    }
}
```

---

## Anti-Patterns

### DON'T: Create Circular EXPOSE Chains

```sysml
// BAD: Circular reference (will cause resolution error)
part a {
    attribute value_a : Real = b.value_b;
}

part b {
    attribute value_b : Real = a.value_a;
}
```

### DON'T: Expose and Re-bind Directly

```sysml
// BAD: Redundant - use one or the other
part producer {
    calc my_calc : SomeCalc { ... }
    attribute exposed : Real = my_calc.out;
}

part consumer {
    calc consumer_calc {
        in x = producer.my_calc.out;  // Should use 'exposed' instead
    }
}

// GOOD: Use the exposed attribute consistently
part consumer {
    calc consumer_calc {
        in x = producer.exposed;  // Use the EXPOSED interface
    }
}
```

### DON'T: Expose Without Clear Naming

```sysml
// BAD: Unclear what 'x' represents
attribute x : Real = my_calc.output;

// GOOD: Descriptive name indicates purpose
attribute calculated_power : Real = power_calc.total_power;
```

---

## EXPOSE vs Direct Binding

| Approach | Use When | Pros | Cons |
|----------|----------|------|------|
| **EXPOSE** | Cross-file access needed | Encapsulation, stable interface | Extra attribute |
| **Direct binding** | Same-file, simple cases | Less code | Tight coupling |

### Same-file (Direct OK)

```sysml
part component {
    calc calc_a : CalcA { ... }
    calc calc_b : CalcB {
        in x = calc_a.output;  // Direct is fine within same part
    }
}
```

### Cross-file (EXPOSE Required)

```sysml
// Producer file
part producer {
    calc calc_a : CalcA { ... }
    attribute result : Real = calc_a.output;  // EXPOSE for cross-file
}

// Consumer file
part consumer {
    private import ProducerPackage::producer;
    calc calc_b : CalcB {
        in x = producer.result;  // Use exposed attribute
    }
}
```

---

## Common Mistakes

### Forgetting to import the instance

```sysml
// WRONG: Importing the definition, not the instance
private import MyLibrary::'Component Type';
// Then trying to access: 'Component Type'.exposed_value  // Error!

// CORRECT: Import the instance
private import MyDesign::my_component;
// Then access: my_component.exposed_value  // Works!
```

### Exposing with wrong type

```sysml
// WRONG: Type mismatch
calc my_calc : CalcDef {
    out power : Power;  // Type is Power
}
attribute exposed_power : Real = my_calc.power;  // Type is Real!

// CORRECT: Match types
attribute exposed_power : Power = my_calc.power;
```

---

## FORMULA vs EXPOSE

> **Added 2026-02-09 per ADR-002 Amendment, ADR-005**

Modelers encounter two patterns that look similar — `attribute x = a * b` and `attribute x = calc.output` — but they serve different purposes and receive different pipeline treatment. This section clarifies the distinction.

### Classification

| Pattern | Example | What It Does | Pipeline Treatment | Validation |
|---------|---------|-------------|-------------------|------------|
| **FORMULA** | `attribute area = length * width` | Arithmetic on sibling attributes | Generates synthetic pipeline module (ADR-004) | PASS |
| **EXPOSE (pure)** | `attribute x = calc.output` | Forwards a calc output as a design attribute | Channel alias (no module) | PASS |
| **EXPOSE_COMPUTED** | `attribute x = calc.output * 2.0` | Calc output + arithmetic | **Not yet supported** | FAIL |

### Key Distinction

- **FORMULA** references **sibling attributes** (same part, no dotted paths). All refs have the same owner.
- **EXPOSE** references a **calc output** via a dotted path (`calc_usage.output_name`). This is a `FeatureChainExpression` in the AST.
- **EXPOSE_COMPUTED** mixes both: a calc output ref wrapped in arithmetic. This is deferred — use a CalcDef as a workaround.

### When to Use Each

```sysml
part plant {
    attribute length : Real = 10.0;
    attribute width : Real = 5.0;

    // FORMULA: simple arithmetic on siblings → OK
    attribute area : Real = length * width;

    calc cost_calc : CostCalc {
        in area = plant::area;
    }

    // EXPOSE (pure): forward calc output → OK
    attribute total_cost : Real = cost_calc.cost;

    // EXPOSE_COMPUTED: calc output + arithmetic → NOT YET SUPPORTED
    // attribute adjusted_cost : Real = cost_calc.cost * 1.15;
    // Workaround: create a CalcDef for the adjustment
}
```

See [adr002-calculations.md](adr002-calculations.md) for the full expression taxonomy and decision flow.

---

## Related Patterns

- [cross-file-binding.md](cross-file-binding.md) - Cross-file import patterns
- [adr002-calculations.md](adr002-calculations.md) - Calculation architecture
- [semantic-operators.md](semantic-operators.md) - Binding operators
- [definitions-usages.md](definitions-usages.md) - Definition vs Usage

---

## Verification

All examples verified with syside parser.

**Test command:**
```bash
syside check <file.sysml>
```

---

*Last Updated: 2026-02-09*

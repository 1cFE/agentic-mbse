# SysML v2 Syntax Quick Reference

Comprehensive syntax patterns for common SysML v2 constructs. Each pattern includes examples and common variations.

## When to Use This Document

Reference this document when:
- Writing SysML v2 code and need syntax examples
- Reviewing unfamiliar SysML syntax
- Looking up import, calc, part, or attribute syntax

For higher-level MBSE concepts, see [mbse-concepts.md](mbse-concepts.md).

---

## Syntax 1: Package Imports

```sysml
// Import specific calc def (preferred)
private import AnalysisCalcs::MyCalculation;

// Import all from package (use sparingly)
public import AnalysisCalcs::*;

// Import component definition
private import Components::'Component Type';

// Import instance for cross-file binding
private import MyDesign::my_component;
```

**When to use:**
- `private`: Default (keeps namespace clean)
- `public`: Only when re-exporting for downstream packages

**Common Mistake:** Forgetting to import instances (not just definitions) when doing cross-file binding.

---

## Syntax 2: Calc Def Definition

```sysml
/**
 * [Title]
 *
 * [Description of what it calculates]
 *
 * Formula:
 *   [Mathematical formula or pseudo-code]
 *
 * Source: [Reference to original derivation]
 * Reference: [Source file:line or paper citation]
 * Typical Values: [Expected ranges]
 * Assumptions:
 *   - [List key assumptions]
 * Last Updated: [Date]
 */
calc def MyCalculation {
    in attribute input_param : Real;  // [units] - Description

    attribute intermediate : Real = input_param * 2.0;  // Optional

    out attribute result : Real = intermediate * 1.5;  // [units] - Description

    assert constraint Reasonable {
        doc /* Description of constraint */
        result > 0 and result < 1000
    }
}
```

**Key Points:**
- `in attribute` for inputs
- `out attribute` for outputs
- Internal `attribute` for intermediate values
- `assert constraint` for validation rules

---

## Syntax 3: Calc Def Instantiation

```sysml
package MyDesign {
    private import MyPackage::MyCalculation;

    part my_component {
        // Input parameter
        attribute my_input : Real = 50.0;

        // Create calc instance
        calc my_calc : MyCalculation {
            // Bind input
            in input_param = my_component::my_input;
        }

        // Access output (optional)
        attribute my_result : Real = my_calc.result;
    }
}
```

**Key Points:**
- Import the calc def first
- Bind inputs using `=` (not `:>>`)
- Access outputs via dot notation
- Use EXPOSE pattern to make outputs accessible to other parts

---

## Syntax 4: Cross-File Attribute Binding

```sysml
// File 1: component.sysml
package MyComponent {
    part my_part {
        attribute exposed_value : Real = 42.0;  // EXPOSED
    }
}

// File 2: consumer.sysml
package MyConsumer {
    private import MyComponent::my_part;  // Import the INSTANCE

    part consumer_part {
        calc some_calc : SomeCalc {
            in some_input = my_part.exposed_value;  // Bind to cross-file attribute
        }
    }
}
```

**Key:** Import the package containing the INSTANCE, not the definition.

For detailed cross-file patterns, see [cross-file-binding.md](cross-file-binding.md).

---

## Syntax 5: Attribute with Units

```sysml
attribute power : Real = 2600.0 [MW];       // Power in megawatts
attribute radius : Real = 3.5 [m];          // Radius in meters
attribute temperature : Real = 300 [K];     // Temperature in Kelvin
attribute fraction : Real = 0.85;           // Dimensionless (no units)
```

**Standard units:** Use SI units from `import SI::*`

**Common Units:**
| Quantity | Unit | Example |
|----------|------|---------|
| Length | `[m]` | `3.5 [m]` |
| Mass | `[kg]` | `1000 [kg]` |
| Time | `[s]` | `60 [s]` |
| Temperature | `[K]` | `300 [K]` |
| Power | `[W]`, `[MW]` | `2600 [MW]` |
| Pressure | `[Pa]`, `[MPa]` | `0.1 [MPa]` |

---

## Syntax 6: Constraints

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

**Best practice:** Always include `doc /* description */`

**Constraint Prefixes:**
- `assert constraint` - Must always hold
- `require constraint` - Precondition
- `assume constraint` - Assumption

For detailed constraint patterns, see [constraints.md](constraints.md).

---

## Syntax 7: Geometry Calculations

```sysml
// Rectangular area
attribute area : Real = length * width;  // m^2

// Cylindrical volume
attribute volume : Real = 3.14159 * radius * radius * height;  // m^3

// Annular area (ring)
attribute area_annular : Real =
    3.14159 * (outer_radius * outer_radius - inner_radius * inner_radius);

// Surface area of cylinder
attribute surface_area : Real =
    2.0 * 3.14159 * radius * height + 2.0 * 3.14159 * radius * radius;
```

**Note:** Use `3.14159` as literal. For complex geometry, extract to a `calc def` in library.

---

## Syntax 8: Part Definition

```sysml
part def 'Component Type' {
    doc /*
    [Description]

    **Source**: [Where it comes from]
    **Reference**: [Citations]
    **Used For**: [Purpose]
    **Assumptions**: [List assumptions]
    **Last Updated**: [Date]
    */

    // Geometric attributes
    attribute length : Real {
        doc /* Description */
    }

    attribute width : Real {
        doc /* Description */
    }

    // Physical properties
    attribute mass : Real {
        doc /* Description */
    }

    // Constraints
    assert constraint GeometryPositive {
        doc /* Dimensions must be positive */
        length > 0 and width > 0
    }
}
```

**Key Points:**
- Use Title Case with quotes for definitions
- Include doc comment with source/reference
- Define attributes with types
- Add constraints for valid ranges

---

## Syntax 9: Part Instantiation

```sysml
package MyDesign {
    private import MyLibrary::'Component Type';

    part my_component : 'Component Type' {
        doc /* Specific component instance description */

        // Bind attributes
        attribute length = 5.0 [m];
        attribute width = 0.8 [m];
        attribute mass = 12000 [kg];
    }
}
```

**Key Points:**
- Use snake_case for usage names
- Import the definition first
- Bind attribute values with `=`

---

## Syntax 10: Conditional Expressions

```sysml
// Basic: if CONDITION? TRUE_VALUE else FALSE_VALUE
attribute diff : Real = if x > y? x - y else y - x;

// Chained conditions
attribute factor : Real =
    if mode == 1? 0.95
    else if mode == 2? 0.85
    else 0.60;
```

**Key syntax:** `if CONDITION?` (note the `?` after condition, not C-style ternary)

> **Full reference:** See [conditionals.md](conditionals.md) for complete syntax rules, common mistakes, and guidance on conditionals vs type specialization.

---

## Common Mistakes

### Wrong: Missing import for cross-file binding

```sysml
// WRONG: Trying to reference without import
calc my_calc {
    in x = OtherPackage::other_part.value;  // Won't resolve!
}

// CORRECT: Import the instance first
private import OtherPackage::other_part;
calc my_calc {
    in x = other_part.value;
}
```

### Wrong: Using definition instead of instance

```sysml
// WRONG: Importing the definition
private import MyLibrary::'Component Type';
// Then trying to reference instance attributes

// CORRECT: Import the instance
private import MyDesign::my_component;
```

### Wrong: Forgetting units

```sysml
// BAD: Missing units
attribute temperature = 300;

// GOOD: Units specified
attribute temperature = 300 [K];
```

---

## Related Patterns

- [conditionals.md](conditionals.md) - Detailed conditional expression syntax
- [constraints.md](constraints.md) - Constraint patterns and prefixes
- [cross-file-binding.md](cross-file-binding.md) - Cross-file import patterns
- [semantic-operators.md](semantic-operators.md) - `=` vs `default :=` vs `:>>`
- [mbse-concepts.md](mbse-concepts.md) - Higher-level MBSE patterns

---

## Verification

All examples verified with syside parser.

**Test command:**
```bash
syside check <file.sysml>
```

Exit code 0 indicates successful parse.

---

*Last Updated: 2026-01-15*

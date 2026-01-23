# Definitions vs Usages Pattern

The fundamental organizing principle of SysML v2 modeling: separating reusable type definitions from specific design instances.

## When to Use This Document

Reference this document when:
- Deciding whether to create a definition or usage
- Organizing model files between library/ and designs/
- Understanding naming conventions
- Creating type specializations

## Quick Reference

| Aspect | Definitions (Library) | Usages (Designs) |
|--------|----------------------|------------------|
| **Purpose** | Reusable types | Specific instances |
| **Location** | `models/library/` | `models/designs/{name}/` |
| **Naming** | `'Title Case'` with quotes | `snake_case` |
| **Example** | `part def 'Pump'` | `part my_pump : 'Pump'` |
| **Question** | "Could this apply to multiple designs?" | "Is this THE specific thing?" |

---

## Definitions (Library)

**When**: Creating reusable types that could apply to multiple designs

**Naming**: Title Case with single quotes
**Location**: `models/library/`

```sysml
// Library definition - describes what a component CAN be
part def 'Component Type' {
    doc /*
    Description of this component type

    **Source**: Reference for this definition
    **Reference**: Path to source document
    */

    attribute property_a : Length;
    attribute property_b : Mass;
}

// Specialized variant
part def 'Specialized Component' :> 'Component Type' {
    doc /* Specialized version with additional constraints */
    attribute additional_property : Real;
}
```

### What Goes in Definitions

- `part def` - Component type definitions
- `calc def` - Calculation formulas (per ADR-002)
- `constraint def` - Reusable constraint patterns
- `port def` - Interface definitions
- `action def` - Function/behavior definitions
- `attribute def` - Custom attribute types

---

## Usages (Designs)

**When**: Defining specific instances in a particular design

**Naming**: snake_case
**Location**: `models/designs/{design_name}/`

```sysml
// Specific design instance - THE component in this design
part my_system : 'System Type' {

    part subsystem : 'Subsystem Type' {
        // These are the actual components in this design
        part components : 'Component Type' [12] {
            attribute property_a = 4.15 [m];      // Specific value
            attribute property_b = 1000 [kg];     // Specific value
        }
    }
}
```

### What Goes in Usages

- `part` - Specific component instances
- `calc` - Calculation instances with bound values
- `attribute` values - Specific design parameters
- Bindings between components
- Design-specific constraints

---

## Decision Tree

```
Am I modeling...
|-- A TYPE that could be reused?
|   -> Definition (part def) in library/
|
|-- A CALCULATION formula?
|   -> Calc def in library/ (per ADR-002)
|
|-- A SPECIFIC thing in this design?
|   -> Usage (part) in designs/
|
|-- A PATTERN/CONTRACT?
|   -> Abstract definition in library/
|
+-- A VARIANT of existing type?
    -> Specialized definition (with :>)
```

---

## Specialization Patterns

### Simple Specialization

```sysml
// Base definition
part def 'Component' {
    attribute mass : Mass;
    attribute cost : Cost;
}

// Specialized definition - adds constraints
part def 'Heavy Component' :> 'Component' {
    doc /* Component with mass > 100 kg */

    assert constraint HeavyWeight {
        mass > 100 [kg]
    }
}
```

### Abstract Base Pattern

```sysml
// Abstract base - cannot be instantiated directly
abstract part def 'Abstract Component' {
    attribute required_property : Real;  // Must be set by specializations
}

// Concrete specialization
part def 'Concrete Component' :> 'Abstract Component' {
    :>> required_property = 42.0;  // Provide required value
}
```

### Usage Specialization

```sysml
// In design file
part my_component : 'Component' {
    // Override inherited attributes
    :>> mass = 150 [kg];
    :>> cost = 5000 [USD];

    // Add design-specific attributes
    attribute installation_date : String;
}
```

---

## Package Organization

```
models/
├── library/              # All definitions
│   ├── foundation/       # Base types, materials, units
│   ├── components/       # Component definitions
│   └── analyses/         # Calc definitions
├── designs/              # All usages
│   └── {design_name}/    # Specific design instances
└── tests/                # Test models
```

---

## Common Mistakes

### Mixing definitions and usages in same package

```sysml
// WRONG: Definition and usage together
package MyProject::Components {
    part def 'Component Type' { ... }
    part my_component : 'Component Type' { ... }  // Wrong place!
}
```

### Correct: Separate library and designs

```sysml
// CORRECT: Definition in library
package MyProject::Library::Components {
    part def 'Component Type' { ... }
}

// CORRECT: Usage in design
package MyProject::Designs::MyDesign {
    import MyProject::Library::Components::*;
    part my_component : 'Component Type' { ... }
}
```

### Using wrong naming convention

```sysml
// WRONG: snake_case for definition
part def component_type { ... }

// WRONG: Title Case for usage
part 'My Component' : 'Component Type' { ... }

// CORRECT
part def 'Component Type' { ... }
part my_component : 'Component Type' { ... }
```

### Putting calc defs in designs

```sysml
// WRONG: Calc def in design file
package MyDesign {
    calc def MyCalculation { ... }  // Violates ADR-002!
}

// CORRECT: Calc def in library
package MyLibrary::Analyses {
    calc def MyCalculation { ... }
}
```

---

## Related Patterns

- [adr002-calculations.md](adr002-calculations.md) - Calculation location rules
- [package-naming.md](package-naming.md) - Package organization
- [expose-pattern.md](expose-pattern.md) - Exposing calc outputs as design attributes
- [semantic-operators.md](semantic-operators.md) - `:>` for type specialization

---

## Verification

All examples verified with syside parser.

**Test command:**
```bash
syside check <file.sysml>
```

---

*Last Updated: 2026-01-15*

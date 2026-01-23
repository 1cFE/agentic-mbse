# Cross-File Binding

Patterns for importing and binding to elements across SysML v2 files.

## When to Use This Document

Reference this document when:
- Binding calc inputs to values from another file
- Importing instances (not just definitions)
- Setting up cross-file dataflow
- Debugging "unresolved reference" errors

## Quick Reference

```sysml
// File 1: producer.sysml
package ProducerPackage {
    part producer_part {
        attribute exposed_value : Real = 42.0;  // EXPOSED
    }
}

// File 2: consumer.sysml
package ConsumerPackage {
    private import ProducerPackage::producer_part;  // Import the INSTANCE

    part consumer_part {
        calc some_calc : SomeCalc {
            in input = producer_part.exposed_value;  // Cross-file binding
        }
    }
}
```

**Key:** Import the INSTANCE, not the definition.

---

## The Problem

SysML v2 models often span multiple files. To reference a value from another file, you must:

1. **Export** the value (make it accessible via an exposed attribute)
2. **Import** the specific instance that holds the value
3. **Bind** to the imported instance's attribute

---

## Step-by-Step Pattern

### Step 1: Create Producer with EXPOSED Attribute

```sysml
// File: geometry_module.sysml
package MyProject::Designs::Geometry {

    part geometry_module {
        // Internal calculations
        calc area_calc : AreaCalculation {
            in length = geometry_module::input_length;
            in width = geometry_module::input_width;
        }

        // EXPOSE: Make result accessible cross-file
        attribute total_area : Real = area_calc.area;
    }
}
```

### Step 2: Import Instance in Consumer

```sysml
// File: cost_module.sysml
package MyProject::Designs::Cost {
    // Import the INSTANCE (not the package, not a definition)
    private import MyProject::Designs::Geometry::geometry_module;

    part cost_module {
        // Now can reference geometry_module.total_area
        calc cost_calc : CostCalculation {
            in area = geometry_module.total_area;  // Cross-file binding!
        }
    }
}
```

---

## Import Types

### Import Instance (For Cross-File Binding)

```sysml
// Import specific instance
private import MyPackage::my_instance;

// Use it
calc my_calc {
    in x = my_instance.some_attribute;
}
```

### Import Definition (For Type Usage)

```sysml
// Import type definition
private import MyLibrary::'Component Type';

// Use it to create instance
part my_component : 'Component Type' { ... }
```

### Import All (Use Sparingly)

```sysml
// Import everything from package
public import MyPackage::*;
```

---

## Import Visibility

| Visibility | Keyword | Re-exportable? | Use Case |
|------------|---------|----------------|----------|
| Private | `private import` | No | Internal use only (default) |
| Public | `public import` | Yes | Re-export for downstream |

**Best Practice:** Use `private import` by default to keep namespace clean.

---

## Common Patterns

### Pattern 1: Direct Instance Import

```sysml
// Import single instance
private import SourcePackage::source_instance;

// Bind directly
in value = source_instance.output;
```

### Pattern 2: Nested Instance Import

```sysml
// Import parent, access nested
private import SystemPackage::system;

// Bind to nested part's attribute
in value = system.subsystem.component.output;
```

### Pattern 3: Multiple Imports

```sysml
// Import multiple instances
private import ThermalPackage::thermal_module;
private import ElectricalPackage::electrical_module;

// Bind from both
calc combined_calc {
    in thermal_power = thermal_module.power_output;
    in electrical_power = electrical_module.power_output;
}
```

---

## Common Mistakes

### Wrong: Importing definition instead of instance

```sysml
// WRONG: This imports the TYPE, not an instance
private import MyLibrary::'Component Type';

// Cannot do this - no instance to reference!
in value = 'Component Type'.some_attribute;  // Error!
```

### Correct: Import the instance

```sysml
// CORRECT: Import the specific instance
private import MyDesign::my_component;

// Can reference instance attributes
in value = my_component.some_attribute;  // Works!
```

### Wrong: Qualified reference without import

```sysml
// WRONG: Trying to reference without importing
calc my_calc {
    in x = OtherPackage::other_part.value;  // Won't resolve!
}
```

### Correct: Import first, then reference

```sysml
// CORRECT: Import, then reference
private import OtherPackage::other_part;

calc my_calc {
    in x = other_part.value;  // Works!
}
```

### Wrong: Missing EXPOSE in producer

```sysml
// Producer without EXPOSE
part producer {
    calc internal_calc : SomeCalc { ... }
    // No exposed attribute!
}

// Consumer can't access calc output directly
private import ProducerPkg::producer;
in x = producer.internal_calc.output;  // May not work cross-file!
```

### Correct: EXPOSE the output

```sysml
// Producer with EXPOSE
part producer {
    calc internal_calc : SomeCalc { ... }
    attribute result : Real = internal_calc.output;  // EXPOSE
}

// Consumer uses exposed attribute
private import ProducerPkg::producer;
in x = producer.result;  // Works!
```

---

## Debugging Import Issues

### Error: "No Type named 'X' found"

**Cause:** Import path is wrong or element doesn't exist.

**Fix:** Verify the full qualified name:
```sysml
// Check: Does this path exist?
private import MyProject::Designs::MyDesign::my_component;
```

### Error: "Unresolved reference"

**Cause:** Imported definition instead of instance, or missing import.

**Fix:** Ensure you're importing the instance:
```sysml
// If you need the instance 'my_pump', import it directly
private import MyDesign::my_pump;  // Not the definition 'Pump'
```

### Error: Circular import

**Cause:** File A imports from B, B imports from A.

**Fix:** Restructure to break cycle, possibly with intermediate aggregator.

---

## Related Patterns

- [expose-pattern.md](expose-pattern.md) - EXPOSE pattern for cross-file access
- [package-naming.md](package-naming.md) - Package organization
- [syntax-reference.md](syntax-reference.md) - Import syntax
- [semantic-operators.md](semantic-operators.md) - Binding operators

---

## Verification

Cross-file binding issues manifest as import/resolution errors:

```bash
syside check models/
```

Look for:
- "No Type named 'X' found"
- "Unresolved reference"
- Missing elements in AST

---

*Last Updated: 2026-01-15*

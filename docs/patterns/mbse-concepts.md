# MBSE Concept Patterns

Higher-level patterns for common Model-Based Systems Engineering (MBSE) concepts in SysML v2.

## When to Use This Document

Reference this document when:
- Modeling function-to-component allocation
- Creating parametric constraints
- Building cost/analysis calculation hierarchies
- Defining component interfaces with ports

For basic SysML syntax, see [syntax-reference.md](syntax-reference.md).

---

## Pattern 1: Allocation (Function to Component)

Allocation connects functions (what the system does) to components (what performs the function).

### Library: Define the Pattern

```sysml
action def 'Perform Function' {
    doc /* Function description */
}

part def 'Component Type' {
    doc /* Performs the function */
    perform action function_instance : 'Perform Function';
}
```

### Design: Specific Allocation

```sysml
part my_component : 'Component Type' {
    perform action my_function : 'Perform Function' {
        // Specific parameters for this design
    }
}
```

### When to Use

- Tracing requirements to implementation
- Documenting which component performs which function
- Supporting V&V activities with clear allocation

---

## Pattern 2: Parametric Constraint

Parametric constraints express engineering relationships between properties.

```sysml
part def 'Constrained Component' {
    attribute material : Material;
    attribute temperature_operating : Temperature;
    attribute load : Force;

    constraint TemperatureLimit {
        doc /* Operating temperature must not exceed material limit */
        temperature_operating <= material.temperature_max
    }

    constraint LoadLimit {
        doc /* Load limited by material properties */
        load <= material.yield_strength * area / safety_factor
    }
}
```

### When to Use

- Material selection constraints
- Operating limits based on physics
- Safety margin enforcement
- Design rule checking

### Best Practices

1. Always include `doc` comment explaining the constraint
2. Reference material properties or other typed attributes
3. Use meaningful constraint names
4. Group related constraints together

---

## Pattern 3: Cost/Analysis Calculation

Hierarchical cost aggregation pattern for system cost analysis.

```sysml
part def 'Costed Component' {
    attribute geometry : Geometry;
    attribute material : Material;

    calc volume : Volume {
        doc /* Calculate volume from geometry */
        // Implementation
    }

    calc mass : Mass {
        doc /* Mass from volume and density */
        return volume * material.density;
    }

    calc material_cost : Cost {
        doc /* Material cost from mass and unit price */
        return mass * material.cost_per_kg;
    }

    calc total_cost : Cost {
        return material_cost * complexity_factor;
    }
}
```

### Cost Aggregation Over Multiplicities

For assemblies with multiple child components:

```sysml
private import NumericalFunctions::sum;

part def 'Assembly' :> 'Costed Component' {
    part child : 'Child Component' [N];
    :>> capital_cost = sum(child.capital_cost);  // Automatic aggregation!
}
```

**Note:** Requires `import NumericalFunctions::sum` for the `sum()` function.

### When to Use

- System cost rollup
- Mass budget tracking
- Power budget analysis
- Any hierarchical aggregation

---

## Pattern 4: Interface Definition

Port-based interfaces for component connections.

```sysml
port def 'Flow Port' {
    doc /* Port for flow connections */

    attribute flow_rate : VolumeFlowRate;
    attribute temperature : Temperature;
    attribute pressure : Pressure;
}

part def 'Flow Component' {
    port inlet : 'Flow Port';
    port outlet : 'Flow Port';

    constraint FlowBalance {
        inlet.flow_rate == outlet.flow_rate
    }
}
```

### Connection Pattern

```sysml
part system {
    part component_a : 'Flow Component';
    part component_b : 'Flow Component';

    // Connect outlet of A to inlet of B
    connect component_a.outlet to component_b.inlet;
}
```

### When to Use

- Fluid/thermal systems
- Electrical connections
- Data interfaces
- Any typed connection between components

### Interface Types

| Port Type | Use For |
|-----------|---------|
| Flow port | Fluid, thermal, material flow |
| Signal port | Control signals, data |
| Power port | Electrical power |
| Mechanical port | Force, torque, motion |

---

## Validated Patterns

### Parameterized Multiplicity Pattern

**Status:** Validated CORRECT (2026-01-12)
**Evidence:** `syside check` passes

Multiplicity can be an attribute, allowing design files to set counts without modifying definitions.

```sysml
part def 'Assembly' {
    attribute child_count : Integer default := 2;
    part child : 'Child Component' [child_count];  // Parameterized!
}

part my_assembly : 'Assembly' {
    :>> child_count = 3;  // Override count in design
}
```

**Why:** This pattern enables configuration-driven multiplicity without duplicating definitions. Useful for:
- Scalable system designs
- Trade studies with different component counts
- Parameterized architecture exploration

---

## Common Mistakes

### Allocation: Forgetting action in definition

```sysml
// WRONG: Action not allocated to component
part def 'Component' {
    // Missing: perform action ...
}

// CORRECT: Explicit allocation
part def 'Component' {
    perform action my_function : 'Perform Function';
}
```

### Cost: Using hardcoded values instead of sum()

```sysml
// WRONG: Hardcoded placeholder
attribute child_total_cost : Real;  // Manual binding required
:>> capital_cost = child_total_cost;

// CORRECT: Automatic aggregation
private import NumericalFunctions::sum;
:>> capital_cost = sum(child.capital_cost);
```

### Interface: Missing conservation constraints

```sysml
// WRONG: No flow balance
part def 'Flow Component' {
    port inlet : 'Flow Port';
    port outlet : 'Flow Port';
    // Missing constraint!
}

// CORRECT: Conservation enforced
part def 'Flow Component' {
    port inlet : 'Flow Port';
    port outlet : 'Flow Port';

    constraint FlowBalance {
        inlet.flow_rate == outlet.flow_rate
    }
}
```

---

## Related Patterns

- [syntax-reference.md](syntax-reference.md) - Basic SysML syntax
- [adr002-calculations.md](adr002-calculations.md) - Calculation architecture rules
- [constraints.md](constraints.md) - Constraint syntax details
- [definitions-usages.md](definitions-usages.md) - Definition vs Usage distinction

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

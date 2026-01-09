# SysML Modeling Guide

**Quick Links:**
- **Navigation & finding code** → [models/README.md](../models/README.md)
- **You are here** - SysML syntax & semantic patterns
- **Design workflow** → See `/design-model`, `/plan-model`, `/implement-model` commands
- **Architecture overview** → [OVERVIEW.md](OVERVIEW.md)

**Use this document for:**
- Learning SysML v2 syntax and semantics
- Understanding Definitions vs Usages pattern (core principle)
- Documentation standards and citation patterns
- Semantic patterns (allocation, constraints, interfaces)
- Validation requirements

---

## Core Principle: Definitions vs Usages

### Definitions (Library)

**When**: Creating reusable types that could apply to multiple designs

**Naming**: Title Case with single quotes
**Location**: `models/library/`

```sysmlv2
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

### Usages (Designs)

**When**: Defining specific instances in a particular design

**Naming**: snake_case
**Location**: `models/designs/{design_name}/`

```sysmlv2
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

### Decision Tree

```
Am I modeling...
├─ A TYPE that could be reused? → Definition (part def) in library/
├─ A CALCULATION formula? → Calc def in library/ (per ADR-002)
├─ A SPECIFIC thing in this design? → Usage (part) in designs/
├─ A PATTERN/CONTRACT? → Abstract definition in library/
└─ A VARIANT of existing type? → Specialized definition (with :>)
```

---

## The EXPOSE Pattern

### What It Is

The EXPOSE pattern is when a design attribute's value comes from a calc output, making that output accessible to other parts of the model through the design attribute reference.

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

### Why Use It

1. **Encapsulation**: Other parts reference `geometry.calculated_area` without knowing it comes from a calc
2. **Cross-file access**: Design attributes are visible across files; calc outputs are not
3. **Interface stability**: You can change the internal calc without affecting consumers

### How to Use It

**Producer side (EXPOSE):**
```sysml
part producer_part {
    calc some_calc : SomeCalcDef { ... }
    attribute exposed_value : Real = some_calc.output;  // EXPOSE
}
```

**Consumer side (transitive binding):**
```sysml
calc consumer_calc : OtherCalcDef {
    in x = producer_part.exposed_value;  // Binds to EXPOSED attr
}
```

### Anti-patterns

**DON'T** create circular EXPOSE chains:
```sysml
// BAD: Circular reference (will cause resolution error)
attribute a = b.value;
attribute b = a.value;
```

**DON'T** expose a calc output and then re-bind directly:
```sysml
// BAD: Redundant - use one or the other
attribute exposed : Real = my_calc.out;
calc consumer {
    in x = my_calc.out;  // Should use 'exposed' if cross-part access needed
}
```

---

## Calculation Architecture (ADR-002)

### Core Principle

> **Calculation definitions belong in `library/`. Design files contain values and wiring. Expressions that resolve to constants are evaluated at extraction time.**

This extends the Definitions vs Usages pattern:
- `library/` = Reusable algorithms (calc defs) + type definitions (part defs)
- `designs/` = Configuration (values, bindings, calc usages)

### Calculation Location Rules

| Rule | Specification |
|------|---------------|
| **Rule 1** | `calc def` declarations SHALL be in `models/library/` only |
| **Rule 2** | Calc usages in `designs/` wire library calc defs to design values |
| **Rule 3** | Design attributes contain literals, bindings, or **static expressions** |

### Expression Taxonomy

| Expression Type | Location | Feature Refs | Result | Example |
|-----------------|----------|--------------|--------|---------|
| **Literal value** | `designs/` attribute | 0 | PASS | `= 3.0 [m]` |
| **True static** | `designs/` attribute | 0 | PASS | `= 3.14159 * 2.0` |
| **EXPOSE pattern** | `designs/` attribute | 1 (calc output) | PASS | `= my_calc.output` |
| **Calc def formula** | `library/` calc def | N/A | N/A | `out result : Real = input * 0.2;` |
| **Binding reference** | Calc usage binding | N/A | N/A | `in value = system.property;` |
| **Derived expression** | `designs/` attribute | ≥1 (design attr) | FAIL | `= radius * 2.0` |
| **Computation on calc** | `designs/` attribute | ≥1 | FAIL | `= calc.power * 0.95` |

### Valid Patterns in Design Files

```sysml
part component {
    // Literal values (entry points)
    attribute dimension_a : Real = 3.0 [m];
    attribute dimension_b : Real = 5.0 [m];

    // True static expressions (ONLY literals, no design attribute refs)
    attribute pi_squared : Real = 3.14159 * 3.14159;

    // EXPOSE pattern (pure value propagation from calc output)
    attribute result : Real = my_calc.output;
}
```

### Invalid Pattern: Derived Expression

```sysml
part component {
    attribute length : Real = 3.0 [m];
    attribute width : Real = 4.0 [m];

    // VIOLATION: References design attributes (length, width)
    attribute area : Real = length * width;
}
```

**Resolution:** Extract computation to calc def in `library/`:

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

### Supported Static Operators

| Operator | Example |
|----------|---------|
| `+`, `-`, `*`, `/` | `a + b`, `a * 2.0` |
| `[` (unit annotation) | `3.0 [m]` |

**Not supported** (require calc def): exponentiation, functions (`sin`, `sqrt`), conditionals.

---

## Package Structure

**Principle**: Separate definitions (library) from usages (designs)
- **models/library/** - All definitions (reusable templates)
- **models/designs/** - All usages (specific design instances)
- **models/tests/** - Test and example models

---

## Naming Conventions

**Core rules:**
- **Definitions** (library): Title Case with quotes → `part def 'Component Type'`
- **Usages** (designs): snake_case → `part my_component : 'Component Type'`
- **Attributes**: snake_case → `attribute major_radius : Length`
- **Packages**: lowercase_underscores → `package power_balance`

---

## Documentation Standards

### Every Major Element Needs Doc Comment

**Required for**:
- All `part def`, `attribute def`, `calc def`, `constraint def`
- Requirements
- Key usages (especially top-level design instances)

**Doc comment must include**:

```sysmlv2
part def 'Component Type' {
    doc /*
    [1. DESCRIPTION]
    Brief description of what this component represents

    [2. SOURCE/CITATION]
    **Source**: Document or standard this is based on
    **Reference**: path/to/source/document.pdf
    **Section**: Relevant section number

    [3. KEY DATA/RATIONALE]
    Key parameters and why they were chosen

    [4. ASSUMPTIONS/LIMITATIONS]
    **Assumptions**:
    - List assumptions made
    **Limitations**:
    - List known limitations

    [5. VALIDATION STATUS]
    **Validated**: How this was validated
    **Confidence**: High/Medium/Low

    [6. LAST UPDATED]
    **Last Updated**: YYYY-MM-DD
    */

    // ... element definition
}
```

### Citation Patterns

**Physical Laws** (no external citation):
```sysmlv2
constraint EnergyConservation {
    doc /* First law of thermodynamics */
    P_in == P_out + P_stored
}
```

**Literature**:
```sysmlv2
calc def 'Empirical Scaling' {
    doc /*
    Empirical scaling law for system behavior

    **Citation**: Author et al. (Year)
    "Paper Title", Journal Name, Volume(Issue), Pages
    **DOI**: 10.xxxx/xxxxx
    **Local Copy**: data/documents/paper.pdf
    **Equation**: (7) on page 42
    */
    // ...
}
```

**Codebase-derived**:
```sysmlv2
calc def 'Algorithm Implementation' {
    doc /*
    Algorithm description

    **Source**: Reference codebase
    **File**: path/to/source/file.py
    **Lines**: 14-72
    **Original References**: List original papers if applicable
    */
    // ...
}
```

---

## Standard Imports

Every model file should start with:

```sysmlv2
package MyProject::Library::Components {
    import ScalarValues::*;
    import ISQ::*;
    import SI::*;
    import MyProject::Library::Foundation::*;

    // ... definitions
}
```

---

## SysML Syntax Quick Reference

Quick patterns for common SysML v2 syntax. For MBSE concept patterns, see the next section.

### Syntax 1: Package Imports

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

**When to use**:
- `private`: Default (keeps namespace clean)
- `public`: Only when re-exporting for downstream packages

### Syntax 2: Calc Def Definition

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

### Syntax 3: Calc Def Instantiation

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

### Syntax 4: Cross-File Attribute Binding

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

**Key**: Import the package containing the INSTANCE, not the definition.

### Syntax 5: Attribute with Units

```sysml
attribute power : Real = 2600.0 [MW];       // Power in megawatts
attribute radius : Real = 3.5 [m];          // Radius in meters
attribute temperature : Real = 300 [K];     // Temperature in Kelvin
attribute fraction : Real = 0.85;           // Dimensionless (no units)
```

**Standard units**: Use SI units from `import SI::*`

### Syntax 6: Constraints

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

**Best practice**: Always include `doc /* description */`

### Syntax 7: Geometry Calculations

```sysml
// Rectangular area
attribute area : Real = length * width;  // m²

// Cylindrical volume
attribute volume : Real = 3.14159 * radius * radius * height;  // m³

// Annular area (ring)
attribute area_annular : Real =
    3.14159 * (outer_radius * outer_radius - inner_radius * inner_radius);

// Surface area of cylinder
attribute surface_area : Real =
    2.0 * 3.14159 * radius * height + 2.0 * 3.14159 * radius * radius;
```

### Syntax 8: Part Definition

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

### Syntax 9: Part Instantiation

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

### Syntax 10: Conditional Logic

```sysml
// Use boolean for conditional state
attribute is_active : Boolean = power > threshold;

// Ternary-like logic with derived attributes
attribute mode_factor : Real =
    is_active ? 0.95 : 0.60;

// More complex: multiple conditions
attribute efficiency : Real =
    (temperature < 100) ? 0.95 :  // Cold
    (temperature < 300) ? 0.85 :  // Warm
    0.60;  // Hot
```

**Note**: SysMLv2 supports conditional expressions in attribute definitions.

---

## MBSE Concept Patterns

Higher-level patterns for common MBSE concepts.

### Pattern 1: Allocation (Function → Component)

```sysmlv2
// Library: define the pattern
action def 'Perform Function' {
    doc /* Function description */
}

part def 'Component Type' {
    doc /* Performs the function */
    perform action function_instance : 'Perform Function';
}

// Design: specific allocation
part my_component : 'Component Type' {
    perform action my_function : 'Perform Function' {
        // Specific parameters for this design
    }
}
```

### Pattern 2: Parametric Constraint

```sysmlv2
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

### Pattern 3: Cost/Analysis Calculation

```sysmlv2
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

### Pattern 4: Interface Definition

```sysmlv2
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

---

## SysML v2 Semantic Operators: Critical Distinctions

### Overview

SysML v2 syntax that appears similar can create vastly different AST structures with different semantic meanings. Understanding these distinctions is **critical** for:
- Correct code generation from models
- Dependency analysis and traceability
- Parameter validation and constraint checking
- Static analysis and tooling

**Key Principle:** *Syntax determines semantics.* The operators you use (`=`, `default :=`, `:>>`, `:>`) create different AST node types with different runtime and structural behavior.

---

### Assignment vs Default vs Redefinition

#### Operator 1: `=` (Binding/Assignment)

**Purpose:** Concrete value assignment for runtime evaluation
**AST Result:** Creates `FeatureValue` with `is_default=False`
**Use Case:** Fixed values, computed expressions, bindings

```sysmlv2
calc def SimpleCalculation {
    in attribute radius : Real;
    out attribute area : Real = 3.14159 * radius * radius;  // Correct usage
}

part def Component {
    attribute fixed_mass : Mass = 1000 [kg];  // Fixed value
}
```

**When to use `=`:**
- Computed expressions (arithmetic, function calls)
- Fixed design values that should not be overridden
- Output attribute calculations

#### Operator 2: `default :=` (Default Value)

**Purpose:** Overridable default parameter value
**AST Result:** Creates `FeatureValue` with `is_default=True`
**Use Case:** Input parameters with sensible defaults

```sysmlv2
calc def AdvancedCalculation {
    in attribute safety_factor : Real default := 1.5;  // Can be overridden
    in attribute margin : Real default := 0.1;         // Can be overridden

    out attribute adjusted_value : Real = input_value * safety_factor;
}

// Usage can override:
calc usage my_calc : AdvancedCalculation {
    in attribute safety_factor = 2.0;  // Override default
}
```

**When to use `default :=`:**
- Optional input parameters
- Parameters with standard/typical values
- Values that users may want to customize

#### Operator 3: `:>>` (Redefinition)

**Purpose:** Structural identity relationship - declares this feature redefines another
**AST Result:** Creates entry in `owned_redefinitions` list
**Use Case:** Type specialization within hierarchies, usage-based dataflow

**Correct Use Case: Type Specialization (Within Hierarchy)**

```sysmlv2
// Base calc def
calc def BaseCalculation {
    in attribute input : Real;
    out attribute output : Real;
}

// Specialized calc def
calc def SpecializedCalculation :> BaseCalculation {
    // CORRECT: Redefinition within specialization hierarchy
    in attribute input :>> BaseCalculation::input;
}
```

**Correct Use Case: Usage-Based Dataflow**

```sysmlv2
// Definitions (no cross-type references)
calc def SourceCalc {
    out attribute result : Real;
}

calc def ConsumerCalc {
    in attribute input : Real;  // Just declare type
}

// Usages (establish dataflow)
part system {
    calc source : SourceCalc { ... }
    calc consumer : ConsumerCalc {
        // CORRECT: Usage binding creates redefinition + expression
        in attribute input = source.result;
    }
}
```

#### Operator 4: `:>` (Subsetting)

**Purpose:** Declares this feature is a subset of another
**AST Result:** Creates subsetting relationship (different from redefinition)
**Use Case:** Specialization, type hierarchies

```sysmlv2
part def 'Specialized Component' :> 'Base Component' {
    // This is a specialized subset of the base component
}
```

---

### Operator Comparison Table

| Operator | Purpose | AST Result | is_default | Use For |
|----------|---------|------------|------------|---------|
| `=` (in usages) | Binding | FeatureValue + FeatureChainExpression | False | Runtime dataflow |
| `=` (in defs) | Fixed value | FeatureValue | False | Computed values |
| `default :=` | Default | FeatureValue | **True** | Optional parameters |
| `:>>` | Redefines | Redefinition | N/A | Type specialization |
| `:>` | Subsets | Subsetting | N/A | Type hierarchies |

---

### VALIDATED CORRECT PATTERN: Usage-Based Dataflow

**Key Discovery:** Usage-based bindings create BOTH structural and runtime AST elements, enabling dual navigation and avoiding semantic warnings.

**For establishing dependencies and dataflow between calculations, use USAGES with BINDINGS:**

#### Definitions (Declare Structure ONLY)

```sysmlv2
// Library: Pure type declarations
package AnalysisCalcs {
    calc def SourceCalculation {
        in attribute input_value : Real;
        out attribute result : Real;
    }
}

package ConsumerCalcs {
    calc def ConsumerCalculation {
        in attribute source_input : Real;  // Just declare type - NO cross-ref here!
        out attribute output : Real = source_input * 2.0;
    }
}
```

**Key Point:** Definitions have **NO** `:>>` cross-type references. They're pure type templates.

#### Usages (Establish Dataflow)

```sysmlv2
// Design: Create instances and establish dataflow
part my_system {
    // Create instances
    calc source_instance : SourceCalculation {
        in attribute input_value = 500.0;
    }

    calc consumer_instance : ConsumerCalculation {
        // CORRECT: Binding creates dataflow!
        in attribute source_input = source_instance.result;
        //                          ^^^^^^^^^^^^^^^^^^^^^^^^
        //                          Binding expression - creates FeatureChainExpression
    }
}
```

**What Happens in AST:**
1. **Redefinition Created**: `consumer_instance.source_input` redefines `ConsumerCalculation.source_input` (inherited feature)
2. **Binding Expression Created**: FeatureValue contains FeatureChainExpression pointing to `source_instance.result`
3. **Dual Navigation Works**: Can trace via structural (redefinitions) AND runtime (expressions)
4. **No Warnings**: This is semantically correct SysML v2!

#### DEPRECATED: Cross-Type Redefinition in Definitions

```sysmlv2
// OLD PATTERN - DO NOT USE!
calc def ConsumerCalculation {
    in attribute source_input : Real :>> SourceCalculation::result;
    // Problem: Cross-type redefinition generates semantic warnings
    // Status: Functional but semantically incorrect
}

// NEW PATTERN - USE THIS!
// See usage-based approach above
```

**Why deprecated:**
- Generates semantic warnings (`subsetting-featuring-types`)
- Violates SysML v2 intent: definitions are type declarations, not dataflow specifications
- Confuses structural identity with runtime dataflow

---

### Dual Navigation for Calc Usages

**Key Discovery:** Usage-based bindings create BOTH structural and runtime AST elements, enabling dual navigation!

#### Navigation Method 1: Structural (via Redefinitions)

Usage features automatically redefine their definition counterparts:

```python
# Navigate via owned_redefinitions (works for BOTH defs and usages!)
for calc in list(model.nodes(CalculationDefinition)) + list(model.nodes(CalculationUsage)):
    for feature in calc.inputs + calc.outputs:
        for redef in feature.owned_redefinitions:
            redefined = redef.redefined_feature
            if redefined.owning_type:
                dependency = redefined.owning_type  # Structural reference!
                print(f"Depends on: {dependency.name}")
```

**Use for:**
- Type resolution and inheritance
- Structural identity tracking
- Import resolution

#### Navigation Method 2: Runtime (via Binding Expressions)

Binding values create expression trees pointing to sources:

```python
# Navigate via FeatureChainExpression (from calc USAGES!)
for calc_usage in model.nodes(CalculationUsage):
    for feature in calc_usage.inputs:
        for membership in feature.owned_memberships:
            if isinstance(membership, syside.FeatureValue):
                expr = membership.value
                if isinstance(expr, syside.FeatureChainExpression):
                    # Extract source reference
                    for m in expr.memberships:
                        if type(m).__name__ == "Membership":
                            target = m.member_element  # Runtime dataflow!
                            print(f"Binds to: {target.name}")
```

**Use for:**
- Dependency graph construction (dataflow edges)
- Pipeline YAML generation (module connections)
- Dataflow tracing and validation

#### Recommended: Support BOTH for Robust Analysis

**Usage-based bindings give you the best of both worlds:**
1. **Structural**: `owned_redefinitions` → Type relationships
2. **Runtime**: `FeatureChainExpression` → Dataflow connections

---

### Multi-Level Aliasing Patterns

Multi-level dependency chains work correctly with usage-based bindings:

```sysmlv2
// Definitions (pure type declarations)
package Level1 {
    calc def SourceCalc {
        out attribute result : Real = 42.0;
    }
}

package Level2 {
    calc def AliasCalc {
        in attribute x : Real;  // Just declare type
        out attribute y : Real = x * 2;
    }
}

package Level3 {
    calc def DeepAliasCalc {
        in attribute z : Real;  // Just declare type
        out attribute w : Real = z + 10;
    }
}

// Usages (establish dataflow)
part system {
    calc source_instance : SourceCalc;

    calc alias_instance : AliasCalc {
        // Level 1 → Level 2 binding
        in attribute x = source_instance.result;
    }

    calc deep_instance : DeepAliasCalc {
        // Level 2 → Level 3 binding
        in attribute z = alias_instance.y;
    }
}
```

**Result:** 3-level dependency chain fully traceable!
- **Structural**: Via `owned_redefinitions` (usage features redefine definition features)
- **Runtime**: Via `FeatureChainExpression` (binding expressions)

**Dependency analysis output:**
```
deep_instance depends on:
  → alias_instance (via z = alias_instance.y)
    → source_instance (via x = source_instance.result)
```

---

### Circular Dependencies

**Definition:** A circular dependency occurs when calc usages depend on each other in a loop (e.g., calc_a → calc_b → calc_c → calc_a), making execution order impossible to determine.

**Important Behavior:**
- **SysML v2 WILL parse circular dependencies** - SysIDE does not reject them (exit code 0)
- **Execution frameworks CANNOT run circular models** - No valid execution order exists
- **Cycles ARE detectable** via `owned_redefinitions` and binding expressions before code generation

**Example (DO NOT DO THIS):**
```sysmlv2
// Definitions (pure types - no issues here)
calc def CalcA {
    in attribute x : Real;
    out attribute output : Real;
}

calc def CalcB {
    in attribute y : Real;
    out attribute output : Real;
}

// Usages (this is where circular dependency is created!)
part system {
    calc calc_a : CalcA {
        in attribute x = calc_b.output;  // A depends on B
    }

    calc calc_b : CalcB {
        in attribute y = calc_a.output;  // B depends on A → CIRCULAR!
    }
}
```

**Validation:**
Code generation tools MUST detect cycles before generating pipeline configurations. Use depth-first search on the dependency graph built from binding expressions and `owned_redefinitions` in calc usages.

**Best Practice:** Keep dependency graphs acyclic (DAG). If you encounter a circular dependency during modeling, refactor to break the cycle by introducing intermediate calculations or rethinking the dataflow.

---

### Binding Expressions vs Redefinitions: When to Use Each

**Critical Architectural Distinction:** Bindings and redefinitions serve different purposes in code generation.

#### Binding Expressions (`=`) - For Runtime Dataflow

**Purpose:** Express runtime dataflow connections between calc instances
**AST Result:** Creates `FeatureReferenceExpression` or `FeatureChainExpression`
**Code Generation Use:** Dataflow tracing, pipeline configuration generation

```sysmlv2
part my_system {
    calc source_calc : SourceCalculation {
        out result = 500.0;
    }

    calc consumer_calc : ConsumerCalculation {
        // BINDING: Runtime dataflow connection
        in input_value = source_calc.result;  // FeatureChainExpression!
        in config_value = config_system.setting;

        out output = input_value * config_value;
    }
}
```

**Generated Configuration (from binding expressions):**
```yaml
modules:
  consumer_calc:
    module_type: ConsumerCalculationModule
    inputs:
      input_value: source_calc.result     # From binding expression!
      config_value: config_system.setting
```

#### Redefinitions (`:>>`) - For Structural Identity

**Purpose:** Declare structural identity/specialization relationships
**AST Result:** Creates entry in `owned_redefinitions` list
**Code Generation Use:** Type resolution, inheritance, structural analysis

```sysmlv2
// Library definition
calc def BaseCalculation {
    in input : Real;
    in config : Real;
    out output : Real;
}

// Design specialization
calc def ExtendedCalculation :>> BaseCalculation {
    // REDEFINITION: Structural specialization
    in input :>> BaseCalculation::input;  // "This IS that parameter"

    // Add design-specific constraints
    assert constraint ReasonableOutput {
        output > 0
    }
}
```

#### Decision Matrix: Binding vs Redefinition

| Use Case | Operator | Creates | For Code Gen |
|----------|----------|---------|--------------|
| Connect calc outputs to inputs (runtime) | `=` | FeatureChainExpression | Pipeline config, dataflow |
| Declare parameter identity (structural) | `:>>` | Redefinition | Type checking, inheritance |
| Specialize calc def | `:>>` | Redefinition | Module variants |
| Default parameter value | `default :=` | FeatureValue (is_default=True) | Input templates |
| Fixed computed value | `=` | FeatureValue (is_default=False) | Implementation logic |

---

### Constraint Syntax Requirements

**Critical Rule:** Constraints require prefix keywords to create proper AST nodes.

#### Wrong: Plain constraint block

```sysmlv2
calc def WrongConstraint {
    in attribute temperature : Temperature;

    constraint TempLimit {  // Not recognized as ConstraintUsage!
        temperature < 1000 [K]
    }
}
```

#### Correct: Assert/require prefix

```sysmlv2
calc def CorrectConstraint {
    in attribute temperature : Temperature;

    assert constraint TempLimit {  // Creates ConstraintUsage!
        doc /* Operating temperature must not exceed limit */
        temperature < 1000 [K]
    }
}
```

**Constraint Prefix Keywords:**
- `assert constraint` - Invariants that must always hold
- `require constraint` - Preconditions that must be satisfied
- `assume constraint` - Assumptions made by the model

---

### Quick Reference: Which Operator?

```
What are you doing?
├─ Connecting calc outputs to inputs (runtime dataflow)?
│  → Use `=` in CALC USAGE (binding expression)
│
├─ Defining optional parameter with default?
│  → Use `default :=` (default value)
│
├─ Specializing a calc def within type hierarchy?
│  → Use `:>>` on CALC DEF declaration (inheritance)
│
├─ Specializing a type definition?
│  → Use `:>` (subsetting)
│
├─ Setting a computed/fixed value?
│  → Use `=` (binding)
│
└─ Creating a constraint?
   → Use `assert constraint` or `require constraint` (with prefix!)
```

---

## Package Naming and Multi-File Organization

### Critical Rule: Unique Package Names

**In SysML v2, each `package` declaration creates a new package element with its own UUID.** Multiple files declaring the same package name create DISTINCT packages, not a single merged package. This breaks qualified name resolution and type checking.

### Incorrect: Multiple Files, Same Package Name

```sysmlv2
// File: file_a.sysml
package MyPackage {  // Collision!
    calc def CalcA { ... }
}

// File: file_b.sysml
package MyPackage {  // Same name - creates DISTINCT package!
    calc def CalcB { ... }
}

// Result: Only first MyPackage has valid qualifiedName
```

### Correct Patterns

#### Pattern 1: Nested Sub-Packages (Hierarchical Organization)

```sysmlv2
// File: my_domain.sysml
package MyDomain {
    package SubdomainA {
        calc def CalcA { ... }
    }

    package SubdomainB {
        calc def CalcB { ... }
    }
}
```

#### Pattern 2: Unique Top-Level Names with Aggregator

```sysmlv2
// File: subdomain_a.sysml
package MyDomain_SubdomainA {  // Unique name!
    calc def CalcA { ... }
}

// File: subdomain_b.sysml
package MyDomain_SubdomainB {  // Unique name!
    calc def CalcB { ... }
}

// File: my_domain.sysml - AGGREGATOR
package MyDomain {  // Public API
    public import MyDomain_SubdomainA::CalcA;
    public import MyDomain_SubdomainB::CalcB;
}
```

#### Pattern 3: Single File Per Package

```sysmlv2
// File: subdomain_a.sysml
package SubdomainA {
    calc def CalcA { ... }
}

// File: subdomain_b.sysml
package SubdomainB {
    calc def CalcB { ... }
}
```

---

## Validation Requirements

### Every Model Must

1. **Parse correctly** - Use `agentic-mbse validate` or `syside check`
2. **Have documentation** - All major definitions have doc comments
3. **Cite sources** - Traceability to papers/reports/assumptions
4. **Define constraints** - Physical laws and engineering limits
5. **Enable validation** - Comparable to reference baseline

### Validation Checklist

```markdown
- [ ] Model parses without errors
- [ ] All definitions have doc comments
- [ ] Sources cited for data and equations
- [ ] Assumptions explicitly marked
- [ ] Constraints defined where applicable
- [ ] Units specified correctly
- [ ] Naming conventions followed
- [ ] Traceability documented
```

---

## File Organization

### One file per major subsystem

**Good**:
```
models/library/components/
├── subsystem_a.sysml      # All subsystem A definitions
├── subsystem_b.sysml      # All subsystem B definitions
└── subsystem_c.sysml      # All subsystem C definitions
```

**Not**:
```
models/library/components/
├── component_1.sysml
├── component_2.sysml      # Too fragmented
├── component_3.sysml
└── ...
```

### Keep files under ~500 lines

If file grows too large, split by:
- Functionality
- Level of detail (basic vs detailed)
- Concern (structure vs analysis vs cost)

---

## Common Mistakes to Avoid

### Don't: Mix definitions and usages

```sysmlv2
// BAD: Definition and usage in same package
package MyProject::Components {
    part def 'Component Type' { ... }
    part my_component : 'Component Type' { ... }  // Wrong place!
}
```

### Do: Separate library and designs

```sysmlv2
// GOOD: Definition in library
package MyProject::Library::Components {
    part def 'Component Type' { ... }
}

// GOOD: Usage in design
package MyProject::Designs::MyDesign {
    import MyProject::Library::Components::*;
    part my_component : 'Component Type' { ... }
}
```

### Don't: Omit documentation

```sysmlv2
// BAD: No doc comment
part def 'Component' {
    attribute property : Length;
}
```

### Do: Document thoroughly

```sysmlv2
// GOOD: Full documentation
part def 'Component' {
    doc /*
    Component description
    **Source**: Reference document
    */
    attribute property : Length {
        doc /* Property description and typical range */
    }
}
```

---

## Tools and Scripts

**Validation**:
```bash
# Validate using agentic-mbse
agentic-mbse validate models/

# Or use SysIDE directly
syside check models/library/file.sysml
```

---

## Questions?

- Check examples in `models/library/`
- Review `OVERVIEW.md` for project status
- Review `SOURCE_INDEX.md` for domain knowledge sources
- Use `/research` command to explore sources

---

## Pattern Validation Status

**Important:** When you discover correct patterns through implementation and testing, document validation status here to prevent regression.

**Format:**
```markdown
### [Pattern Name]
**Status**: Validated CORRECT
**Date**: YYYY-MM-DD
**Evidence**: X/X tests passing, no semantic warnings
**Summary**: Brief description of what was validated
```

**Example:**
```markdown
### Usage-Based Dataflow Pattern
**Status**: Validated CORRECT
**Date**: 2025-11-25
**Evidence**: 5/5 API validation tests passing
**Summary**: Binding expressions in calc usages (not definitions) create
FeatureChainExpression AST nodes that enable dual navigation without
semantic warnings. This is the recommended pattern for all cross-calc
dependencies.
```

**Active Validations:**

<!-- Add validated patterns here as they are confirmed through testing -->

---

**Last Updated**: <!-- YYYY-MM-DD -->

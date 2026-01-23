# SysML v2 Semantic Operators

Critical distinctions between SysML v2 operators that appear similar but create vastly different AST structures with different semantic meanings.

## When to Use This Document

Reference this document when:
- Choosing between `=`, `default :=`, `:>>`, and `:>`
- Establishing dataflow between calculations
- Understanding semantic warnings from the parser
- Building code generation or analysis tools

## Quick Reference

| Operator | Purpose | AST Result | Use For |
|----------|---------|------------|---------|
| `=` (in usages) | Binding | FeatureValue + FeatureChainExpression | Runtime dataflow |
| `=` (in defs) | Fixed value | FeatureValue | Computed values |
| `default :=` | Default | FeatureValue (is_default=True) | Optional parameters |
| `:>>` | Redefines | Redefinition | Type specialization |
| `:>` | Subsets | Subsetting | Type hierarchies |

---

## Overview

SysML v2 syntax that appears similar can create vastly different AST structures with different semantic meanings. Understanding these distinctions is **critical** for:
- Correct code generation from models
- Dependency analysis and traceability
- Parameter validation and constraint checking
- Static analysis and tooling

**Key Principle:** *Syntax determines semantics.* The operators you use (`=`, `default :=`, `:>>`, `:>`) create different AST node types with different runtime and structural behavior.

---

## Operator 1: `=` (Binding/Assignment)

**Purpose:** Concrete value assignment for runtime evaluation
**AST Result:** Creates `FeatureValue` with `is_default=False`
**Use Case:** Fixed values, computed expressions, bindings

```sysml
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

---

## Operator 2: `default :=` (Default Value)

**Purpose:** Overridable default parameter value
**AST Result:** Creates `FeatureValue` with `is_default=True`
**Use Case:** Input parameters with sensible defaults

```sysml
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

---

## Operator 3: `:>>` (Redefinition)

**Purpose:** Structural identity relationship - declares this feature redefines another
**AST Result:** Creates entry in `owned_redefinitions` list
**Use Case:** Type specialization within hierarchies, usage-based dataflow

### Correct Use Case: Type Specialization (Within Hierarchy)

```sysml
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

### Correct Use Case: Usage-Based Dataflow

```sysml
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

---

## Operator 4: `:>` (Subsetting)

**Purpose:** Declares this feature is a subset of another
**AST Result:** Creates subsetting relationship (different from redefinition)
**Use Case:** Specialization, type hierarchies

```sysml
part def 'Specialized Component' :> 'Base Component' {
    // This is a specialized subset of the base component
}
```

---

## VALIDATED CORRECT PATTERN: Usage-Based Dataflow

**Key Discovery:** Usage-based bindings create BOTH structural and runtime AST elements, enabling dual navigation and avoiding semantic warnings.

**For establishing dependencies and dataflow between calculations, use USAGES with BINDINGS:**

### Definitions (Declare Structure ONLY)

```sysml
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

### Usages (Establish Dataflow)

```sysml
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

### DEPRECATED: Cross-Type Redefinition in Definitions

```sysml
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

## Dual Navigation for Calc Usages

**Key Discovery:** Usage-based bindings create BOTH structural and runtime AST elements, enabling dual navigation!

### Navigation Method 1: Structural (via Redefinitions)

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

### Navigation Method 2: Runtime (via Binding Expressions)

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

### Recommended: Support BOTH for Robust Analysis

**Usage-based bindings give you the best of both worlds:**
1. **Structural**: `owned_redefinitions` - Type relationships
2. **Runtime**: `FeatureChainExpression` - Dataflow connections

---

## Multi-Level Aliasing Patterns

Multi-level dependency chains work correctly with usage-based bindings:

```sysml
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
        // Level 1 -> Level 2 binding
        in attribute x = source_instance.result;
    }

    calc deep_instance : DeepAliasCalc {
        // Level 2 -> Level 3 binding
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
  -> alias_instance (via z = alias_instance.y)
    -> source_instance (via x = source_instance.result)
```

---

## Circular Dependencies

**Definition:** A circular dependency occurs when calc usages depend on each other in a loop (e.g., calc_a -> calc_b -> calc_c -> calc_a), making execution order impossible to determine.

**Important Behavior:**
- **SysML v2 WILL parse circular dependencies** - SysIDE does not reject them (exit code 0)
- **Execution frameworks CANNOT run circular models** - No valid execution order exists
- **Cycles ARE detectable** via `owned_redefinitions` and binding expressions before code generation

**Example (DO NOT DO THIS):**

```sysml
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
        in attribute y = calc_a.output;  // B depends on A -> CIRCULAR!
    }
}
```

**Validation:**
Code generation tools MUST detect cycles before generating pipeline configurations. Use depth-first search on the dependency graph built from binding expressions and `owned_redefinitions` in calc usages.

**Best Practice:** Keep dependency graphs acyclic (DAG). If you encounter a circular dependency during modeling, refactor to break the cycle by introducing intermediate calculations or rethinking the dataflow.

---

## Binding Expressions vs Redefinitions: When to Use Each

**Critical Architectural Distinction:** Bindings and redefinitions serve different purposes in code generation.

### Binding Expressions (`=`) - For Runtime Dataflow

**Purpose:** Express runtime dataflow connections between calc instances
**AST Result:** Creates `FeatureReferenceExpression` or `FeatureChainExpression`
**Code Generation Use:** Dataflow tracing, pipeline configuration generation

```sysml
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

### Redefinitions (`:>>`) - For Structural Identity

**Purpose:** Declare structural identity/specialization relationships
**AST Result:** Creates entry in `owned_redefinitions` list
**Code Generation Use:** Type resolution, inheritance, structural analysis

```sysml
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

### Decision Matrix: Binding vs Redefinition

| Use Case | Operator | Creates | For Code Gen |
|----------|----------|---------|--------------|
| Connect calc outputs to inputs (runtime) | `=` | FeatureChainExpression | Pipeline config, dataflow |
| Declare parameter identity (structural) | `:>>` | Redefinition | Type checking, inheritance |
| Specialize calc def | `:>>` | Redefinition | Module variants |
| Default parameter value | `default :=` | FeatureValue (is_default=True) | Input templates |
| Fixed computed value | `=` | FeatureValue (is_default=False) | Implementation logic |

---

## Constraint Syntax Requirements

**Critical Rule:** Constraints require prefix keywords to create proper AST nodes.

### Wrong: Plain constraint block

```sysml
calc def WrongConstraint {
    in attribute temperature : Temperature;

    constraint TempLimit {  // Not recognized as ConstraintUsage!
        temperature < 1000 [K]
    }
}
```

### Correct: Assert/require prefix

```sysml
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

## Quick Reference Decision Tree

```
What are you doing?
|-- Connecting calc outputs to inputs (runtime dataflow)?
|   -> Use `=` in CALC USAGE (binding expression)
|
|-- Defining optional parameter with default?
|   -> Use `default :=` (default value)
|
|-- Specializing a calc def within type hierarchy?
|   -> Use `:>>` on CALC DEF declaration (inheritance)
|
|-- Specializing a type definition?
|   -> Use `:>` (subsetting)
|
|-- Setting a computed/fixed value?
|   -> Use `=` (binding)
|
+-- Creating a constraint?
    -> Use `assert constraint` or `require constraint` (with prefix!)
```

---

## Validated Patterns

### Part Redefinition Pattern

**Status:** Validated CORRECT (2026-01-12)
**Evidence:** `syside check` passes with no shadowing warnings

Use dot notation for simple attribute binding, explicit `redefines` keyword when adding features. Avoid re-declaring parts in usages.

**Pattern A - Dot Notation (for simple binding):**

```sysml
part my_assembly : 'Assembly' {
    :>> child.power_rating = 1000.0;  // No shadowing warning
}
```

**Pattern B - Explicit Redefines (when adding features):**

```sysml
part my_assembly : 'Assembly' {
    part redefines child {
        :>> power_rating = 1000.0;
        attribute extra_feature : Real;  // Can add features
    }
}
```

**Anti-Pattern (DO NOT USE):**

```sysml
part my_assembly : 'Assembly' {
    part child : 'Child Component' [N] {  // Causes shadowing warning!
        :>> power_rating = 1000.0;
    }
}
```

**Why:** Re-declaring the part creates a new element that shadows the inherited one, causing semantic warnings and potential resolution issues.

---

## Common Mistakes

### Using `:>>` for dataflow in definitions

```sysml
// WRONG: Creates semantic warnings
calc def Consumer {
    in attribute x : Real :>> OtherCalc::output;  // Don't do this!
}

// CORRECT: Bind in usages
calc consumer : Consumer {
    in attribute x = other_instance.output;  // Do this!
}
```

### Forgetting constraint prefix

```sysml
// WRONG: Not a proper constraint
constraint MyConstraint { x > 0 }

// CORRECT: Use assert/require/assume
assert constraint MyConstraint { x > 0 }
```

### Confusing `=` and `default :=`

```sysml
// Use `=` for computed values that shouldn't change
out attribute area : Real = length * width;

// Use `default :=` for overridable defaults
in attribute safety_factor : Real default := 1.5;
```

---

## Related Patterns

- [conditionals.md](conditionals.md) - Conditional expression syntax
- [constraints.md](constraints.md) - Detailed constraint patterns
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

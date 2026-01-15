# Package Naming and Multi-File Organization

Rules for organizing SysML v2 models across multiple files with unique package names.

## When to Use This Document

Reference this document when:
- Organizing models across multiple files
- Resolving "duplicate package" issues
- Setting up package hierarchies
- Creating aggregator packages

## Critical Rule: Unique Package Names

> **In SysML v2, each `package` declaration creates a new package element with its own UUID.** Multiple files declaring the same package name create DISTINCT packages, not a single merged package.

This breaks qualified name resolution and type checking.

---

## Incorrect Pattern: Same Package Name in Multiple Files

```sysml
// File: file_a.sysml
package MyPackage {  // Creates package with UUID-A
    calc def CalcA { ... }
}

// File: file_b.sysml
package MyPackage {  // Creates DIFFERENT package with UUID-B!
    calc def CalcB { ... }
}
```

**Result:** Only the first `MyPackage` has a valid `qualifiedName`. The second creates a collision.

**Symptoms:**
- Imports don't resolve: `import MyPackage::CalcB` fails
- Type checking errors
- Unexpected "not found" errors

---

## Correct Patterns

### Pattern 1: Nested Sub-Packages (Hierarchical Organization)

Put everything in one file with nested packages:

```sysml
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

**Use when:** Related content fits in one file (<500 lines)

### Pattern 2: Unique Top-Level Names with Aggregator

Use unique package names per file, then aggregate:

```sysml
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

**Use when:** Content is large, need separate files, want clean public API

### Pattern 3: Single File Per Package

Each package lives in exactly one file:

```sysml
// File: subdomain_a.sysml
package SubdomainA {
    calc def CalcA { ... }
}

// File: subdomain_b.sysml
package SubdomainB {
    calc def CalcB { ... }
}
```

**Use when:** Packages are independent, no need for aggregation

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Top-level package | `ProjectName::Category` | `FusionTea::Library` |
| Sub-package | `lowercase_underscores` | `thermal_analysis` |
| Definition | `'Title Case'` | `part def 'Heat Exchanger'` |
| Usage | `snake_case` | `part primary_exchanger` |

### Package Hierarchy Example

```
MyProject::Library::Components
MyProject::Library::Analyses
MyProject::Designs::BaselineDesign
MyProject::Designs::AlternativeDesign
```

---

## File Organization Best Practices

### One File Per Major Subsystem

**Good:**
```
models/library/components/
├── thermal_system.sysml      # All thermal definitions
├── electrical_system.sysml   # All electrical definitions
└── structural_system.sysml   # All structural definitions
```

**Not:**
```
models/library/components/
├── pump.sysml
├── valve.sysml       # Too fragmented
├── pipe.sysml
└── ...
```

### Keep Files Under ~500 Lines

If a file grows too large, split by:
- Functionality (thermal vs electrical)
- Level of detail (basic vs detailed)
- Concern (structure vs analysis vs cost)

### Directory Structure

```
models/
├── library/              # All definitions
│   ├── foundation/       # Base types, materials, units
│   ├── components/       # Component definitions
│   └── analyses/         # Calc definitions
├── designs/              # All usages
│   └── {design_name}/    # Specific design
└── tests/                # Test models
```

---

## Common Mistakes

### Reusing package name across files

```sysml
// WRONG: Same name in different files
// thermal.sysml
package Analyses { ... }

// electrical.sysml
package Analyses { ... }  // Collision!

// CORRECT: Unique names
// thermal.sysml
package ThermalAnalyses { ... }

// electrical.sysml
package ElectricalAnalyses { ... }
```

### Deep nesting without need

```sysml
// WRONG: Unnecessary depth
package A {
    package B {
        package C {
            package D {
                calc def MyCalc { ... }
            }
        }
    }
}

// CORRECT: Flat where possible
package MyProject::Analyses {
    calc def MyCalc { ... }
}
```

### Inconsistent naming hierarchy

```sysml
// WRONG: Inconsistent structure
package FusionTea_Components { ... }
package Library::Analyses { ... }
package fusion_tea_designs { ... }

// CORRECT: Consistent hierarchy
package FusionTea::Library::Components { ... }
package FusionTea::Library::Analyses { ... }
package FusionTea::Designs::Baseline { ... }
```

---

## Related Patterns

- [definitions-usages.md](definitions-usages.md) - Library vs designs separation
- [cross-file-binding.md](cross-file-binding.md) - Cross-file imports
- [syntax-reference.md](syntax-reference.md) - Import syntax

---

## Verification

Package naming issues often manifest as import errors:

```bash
syside check models/
```

Look for errors like:
- "No Type named 'X' found"
- "Unresolved reference"
- "Ambiguous reference"

---

*Last Updated: 2026-01-15*

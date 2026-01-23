# Package Naming and Multi-File Organization

Rules for organizing SysML v2 models across multiple files with unique package names.

## When to Use This Document

Reference this document when:
- Organizing models across multiple files
- Resolving "duplicate package" issues
- Setting up package hierarchies
- Creating aggregator packages

## Invalid Syntax: Qualified Package Names

> **Important:** The syntax `package A::B::C { }` is **invalid per the SysML v2 specification** - not just unsupported by syside.

The SysML v2 grammar rule is:
```
PackageDeclaration = 'package' Identification
```

Where `Identification` accepts only a simple `NAME`, not a `QualifiedName`. Qualified names (`::`) are for **references** (imports, type paths), not **declarations**.

```sysml
// INVALID SysML v2 syntax - will not parse
package MyProject::Library::Components { ... }

// CORRECT - use simple names
package MyProject_Library_Components { ... }

// CORRECT - use hierarchical nesting
package MyProject {
    package Library {
        package Components { ... }
    }
}
```

Use underscores or hierarchical nesting for namespace organization.

---

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
| Top-level package | `ProjectName_Category` | `FusionTea_Library` |
| Sub-package | `lowercase_underscores` | `thermal_analysis` |
| Definition | `'Title Case'` | `part def 'Heat Exchanger'` |
| Usage | `snake_case` | `part primary_exchanger` |

### Package Hierarchy Example

Using underscore-separated unique names:
```
FusionTea_Library_Components
FusionTea_Library_Analyses
FusionTea_Designs_BaselineDesign
FusionTea_Designs_AlternativeDesign
```

Or using hierarchical nesting in a single file:
```sysml
package FusionTea {
    package Library {
        package Components { ... }
        package Analyses { ... }
    }
    package Designs {
        package BaselineDesign { ... }
    }
}
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
package MyProject_Analyses {
    calc def MyCalc { ... }
}
```

### Inconsistent naming hierarchy

```sysml
// WRONG: Inconsistent naming structure
package FusionTea_Components { ... }
package LibraryAnalyses { ... }
package fusion_tea_designs { ... }

// CORRECT: Consistent underscore-separated hierarchy
package FusionTea_Library_Components { ... }
package FusionTea_Library_Analyses { ... }
package FusionTea_Designs_Baseline { ... }
```

### Using `::` in package declarations

```sysml
// WRONG: Invalid SysML v2 syntax - qualified names cannot be used in declarations
package FusionTea::Library::Components { ... }

// CORRECT: Use underscores for unique names
package FusionTea_Library_Components { ... }

// ALSO CORRECT: Use hierarchical nesting
package FusionTea {
    package Library {
        package Components { ... }
    }
}
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

*Last Updated: 2026-01-23*

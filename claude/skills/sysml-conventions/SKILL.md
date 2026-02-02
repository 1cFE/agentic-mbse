---
name: sysml-conventions
description: >
  Use when writing SysML v2 code, asking about "SysML syntax", "naming conventions",
  "how to write" a part def or calc def, "imports", "syntax error", "parse error",
  "common mistakes", "pitfalls", "SysML patterns", attribute declarations, units notation,
  doc comment format, ADR-002, or definition vs usage rules.
  Provides the canonical syntax rules and patterns for SysML v2 modeling.
allowed-tools: Read, Grep, Glob
user-invocable: false
---

# SysML Conventions

Canonical syntax rules, naming conventions, and patterns for writing correct SysML v2 models.

## Core Principle

Every SysML element is either a **definition** (reusable type in `library/`) or a **usage** (specific instance in `designs/`). This distinction drives naming, file placement, and calculation architecture. When unsure, ask: "Could this apply to multiple designs?" Yes = definition, No = usage.

## When to Reference

- `/design-model` — when specifying SysML structure and syntax in designs
- `/implement-model` — when writing SysML files (pre-flight syntax validation)
- `/plan-model` — when reviewing planned changes for syntax compliance
- `/audit-models` — when checking naming and syntax conformance

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Definitions | `'Title Case'` with single quotes | `part def 'Pump'` |
| Usages | `snake_case` | `part my_pump : 'Pump'` |
| Attributes | `snake_case` | `attribute flow_rate : Real` |
| Packages | `lowercase_underscores` | `package thermal_components` |

## Definition vs Usage Rule

**Decision question**: "Could this apply to multiple designs?"

```sysml
// DEFINITION — reusable type (library/)
part def 'Heat Exchanger' {
    attribute heat_transfer_area : Real;
    attribute pressure_drop : Real;
}

// USAGE — specific instance (designs/)
part primary_hx : 'Heat Exchanger' {
    attribute heat_transfer_area : Real = 50.0 [m^2];
}
```

For directory placement of definitions and usages, see the **project-structure** skill.

## Calculation Architecture (ADR-002)

> `calc def` declarations belong in `library/` only. Design files contain values and wiring.

**Expression taxonomy for design files:**

| In Design Files | Status |
|-----------------|--------|
| Literal: `= 3.0 [m]` | OK |
| Static expr: `= 3.14 * 2.0` | OK |
| EXPOSE: `= my_calc.output` | OK |
| Derived: `= radius * 2.0` | **VIOLATION** — extract to calc def |

When a design attribute depends on another attribute's value, that relationship must be expressed as a `calc def` in `library/analyses/`, not inline in the design.

## Standard Imports

```sysml
package MyProject::Library::Components {
    import ScalarValues::*;    // Real, Integer, Boolean
    import ISQ::*;             // Physical quantities
    import SI::*;              // SI units

    // For cost aggregation over multiplicities:
    private import NumericalFunctions::sum;
}
```

## Doc Comment Format

Every `part def`, `calc def`, and `constraint def` requires a doc comment:

```sysml
part def 'Component' {
    doc /*
    Description of component.

    **Source**: Reference document
    **Reference**: path/to/source.pdf
    **Last Updated**: YYYY-MM-DD
    */
}
```

Required fields: **Source** (what authority), **Reference** (where to find it), **Last Updated** (when verified).

For doc comment field content requirements and citation patterns, see the **source-traceability** skill.

## Common Pitfalls

| Pitfall | Correction |
|---------|-----------|
| `attribute radius = 0.5 [m];` | `attribute radius : Real = 0.5 [m];` — always declare type |
| `[m^3]` written as `[m³]` | Use ASCII only: `[m^3]`, `[kg/m^3]`, `[K]` — syside rejects unicode |
| `[°C]` for temperature | Use Kelvin: `= 300 [K]` — convert Celsius, or use comment |
| `:>> radius = 0.5 [m];` without parent | Redefinition (`:>>`) requires a parent type that declares `radius` |
| `material : Material = SS316;` | Use `material : String = "SS316";` unless Material type is imported |
| Qualified names in calc expressions | Use local bindings: `in x = other.value;` not `other.value` inline |
| `redefines` when meaning `specializes` | `redefines` replaces a feature; `:>` specializes a type — different semantics |
| Missing imports for cross-file refs | Every cross-file reference needs explicit `import` or `private import` |

## Key Syntax Patterns

**Conditional expressions:**
```sysml
attribute diff : Real = if x > y? x - y else y - x;
```

**Constraints:**
```sysml
assert constraint TempLimit { temperature < 1000 [K] }
```

**Cross-file binding:**
```sysml
private import OtherPackage::other_part;
calc my_calc { in value = other_part.exposed_attr; }
```

**Semantic operators:**
- `=` — fixed value (cannot be overridden)
- `default :=` — default value (can be overridden by specialization)
- `:>>` — redefinition (replaces inherited feature)
- `:>` — specialization (extends a type)

## Anti-Patterns

| Instead of | Do |
|------------|-----|
| Inline derived expressions in designs | Extract to `calc def` in `library/analyses/` |
| Unicode unit symbols (`m³`, `°C`) | ASCII equivalents (`m^3`, `K`) |
| Bare attributes without types | Always declare type: `attribute x : Real` |
| `part x : 'Base' { ... }` without import | Add `import` for the package containing `'Base'` |
| Copying definitions into design files | Import from library; keep one source of truth |
| Skipping doc comments on definitions | Every def needs Source, Reference, Last Updated |

## Related Skills

- For doc comment field content requirements and citation patterns, see the **source-traceability** skill.
- For directory placement of definitions and usages, see the **project-structure** skill.

## Reference Files

For extended code stencils and the pattern documentation index:
- **`references/stencils.md`** — Code stencils for common definition types and pattern doc index

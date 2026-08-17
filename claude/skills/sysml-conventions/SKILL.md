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

**Quoted names are fine.** Multi-word quoted names (`'Fusion Power Plant'`, `'HIF Driver'`)
are supported everywhere a name appears. Codegen sanitizes them to valid identifiers
(`Fusion_Power_Plant`) — the identifier is *derived*, you do not write it. Use the
readable quoted name.

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
| Inline FORMULA: `= radius * 2.0` (same-part siblings) | OK for simple arithmetic |
| Computation on calc output: `= calc.power * 0.95` | **VIOLATION** — extract to calc def |
| Self-reference or dotted path: `= self.x`, `= a.b.c` | **VIOLATION** — extract to calc def |

A design attribute may reference same-part siblings inline (a FORMULA) for simple
arithmetic and unit conversions. For any real or reusable calculation — and always when
the value depends on a calc output or another part — express it as a `calc def` in
`library/analyses/`, not inline.

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
| Self-named binding `in x = x` | Refused (`SI_SELF_BINDING` / L2 error): the RHS resolves to the calc's own input, never an outer feature. Rename the input — `in x_in = x;` — so the bare RHS lands on the part attribute |
| `redefines` when meaning `specializes` | `redefines` replaces a feature; `:>` specializes a type — different semantics |
| Missing imports for cross-file refs | Every cross-file reference needs explicit `import` or `private import` |

## Key Syntax Patterns

**Conditional expressions:**
```sysml
attribute diff : Real = if x > y? x - y else y - x;
```

**Constraints — the blessed shape is bindings-only:**
```sysml
// A constraint def with formals, asserted with every formal bound to a real value in scope.
constraint def TempLimit { in temperature : Real; in limit : Real; temperature < limit }
// ...
assert constraint temp_ok : TempLimit {
    in temperature = reactor.wall_temperature_k;
    in limit = 1000.0;
}
```

Three rules, and each one bites:

1. **Only the assert family executes.** A bare `constraint`, a `require constraint`, an
   `assume constraint`, and a `satisfy` reference are visible, cataloged descriptions that **never
   run**. Writing one where you meant a gate is the single most common way a model ships with no
   check at all. Use them when you mean to describe; use `assert` when you mean to check.
2. **Bind formals; don't inline the predicate.** `assert constraint TempLimit { temperature < 1000
   [K] }` parses, but an inline predicate resolves its names by reaching into surrounding scope, and
   a unit literal inside the predicate is a frequent block. Binding every formal to a real value in
   scope makes the wiring explicit and lowerable. It is also the form `@inapplicable:` works on —
   see below.
3. **Units go on the binding, not inside the predicate.** `in temperature = wall_temp_k;` where the
   attribute carries `[K]`. Codegen carries the authored unit text into port metadata and performs
   **no conversion**; two consumers of one shared value that annotate different units fail closed
   with `SI_RENDERING_COLLISION`, naming the key. Fix the model, not the diagnostic.

**Marking a constraint inapplicable** — the marker goes on a gate that **does not run**:
```sysml
// The direct-drive variant instantiates no VacuumSystem, so this definition has zero
// occurrences and the gate below reaches nothing. That is what lets the marker stand.
part def VacuumSystem {
    attribute pumping_speed_total : Real = 12.0;
    attribute pumping_speed_required : Real = 20.0;

    assert constraint vac_ok : ProductWithinBand {
        doc /* @inapplicable: no vacuum system in the direct-drive variant */
        in actual = pumping_speed_total;
        in reference = pumping_speed_required;
    }
}
```
An `@inapplicable:` marker is the **only** way a gate leaves the feasibility denominator. Without
one, an asserted gate that never ran keeps the report at `partial_coverage` rather than
`full_satisfaction` — which is the point: an unassessed gate must not read as a passing one.

⚠️ **Marking a gate that actually runs is refused, not honoured.** Put this same marked constraint on
a part that *is* instantiated and generation fails by name: *"marked inapplicable but produced 1
executable entries."* That is D9. A marker states a gate is out of the feasible set; it is not a
switch that silences a live check. Accepted and refused shapes are both pinned as sysml-codegen
fixtures — `constraint_coverage_all_inapplicable` and `constraint_coverage_eligible_inapplicable`.

⚠️ **The marker only reaches the domain on the bindings form.** On an inline-predicate constraint
SysIDE silently drops the doc comment, so the marker never arrives and the gate stays in the
denominator with no warning. This is `[INLINE-PREDICATE-MARKER-DROP]`, open. Until it closes, an
inline-form disposition has to be recorded in the fixture's `PROVENANCE.md` instead of in source.
**Decide before you author:** bindings form → the marker works; inline form → PROVENANCE carries it.
Worked case: sysml-codegen `tests/fixtures/catf_mfe_gated`, B1–B5 — five markers written, zero
carried. The loud detector is `tests/conformance/test_constraint_population_oracle.py` rule 3.

**Equality intent — check which of four you have before writing `==`.** An equality gate over a
parameter you meant to vary does not judge the design, it deletes the degree of freedom.

| Intent | Do this instead |
|---|---|
| Structural identity | Derive it. Do not constrain it. |
| Cross-check of two independently computed values | A loose, physically motivated validity band. |
| Feasibility gate | Prefer a one-sided inequality; if a quantity must equal a value, fix it as an input rather than search for it and then constrain it. |
| Composition closure | Derive the last term by construction, or fall back to a banded check. |

The authority copy is the lifecycle contract's "Equality intent and authoring policy" in
sysml-codegen (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`).

**Cross-file binding:**
```sysml
private import OtherPackage::other_part;
calc my_calc { in value = other_part.exposed_attr; }
```

**Calculation input binding — pick the form by where the value lives:**
- attribute on the part that owns the calc → make the names differ: `in radius_in = radius;`
  (never the self-named `in radius = radius` — refused, not reinterpreted);
- value on another part → name the occurrence path: `in driver_cost = driver.cost;`;
- owner-qualified (`comp_a::length`) → resolves to the exact feature owned by that usage;
  a definition-owned leaf falls back to positional occurrence search instead.

The authoritative copy of this rule is agentic-mbse `docs/patterns/plant-idiom.md`,
"Binding a modelled value into a calculation".

**Semantic operators:**
- `=` — fixed value (cannot be overridden)
- `default :=` — default value (can be overridden by specialization)
- `:>>` — redefinition (replaces inherited feature)
- `:>` — specialization (extends a type)

## Anti-Patterns

| Instead of | Do |
|------------|-----|
| Real calculations inline, or computing on a calc output in a design attribute | Extract to `calc def` in `library/analyses/` (inline FORMULA over same-part siblings is fine for simple arithmetic) |
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

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
metadata:
  kind: supporting
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


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

<!-- @tool-example -->
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
| Sum over child parts: `= sum(cells.capacity)` | **VIOLATION** — put it on the `part def` in `library/` |

A design attribute may reference same-part siblings inline (a FORMULA) for simple
arithmetic and unit conversions. For any real or reusable calculation — and always when
the value depends on a calc output or another part — express it as a `calc def` in
`library/analyses/`, not inline.

## Three Structures the Code Generator Refuses

The code generator (sysml-codegen) refuses three structures that parse and validate without complaint, so nothing warns you until it runs. A model built around one of them is expensive to rework. Avoid all three from the first line whenever the project targets generated code (`execution-target = "generated"`); `modeling_project/MODELING_PROCESS.md`, "Generated code", says when to run the generator's own check.

**1. An `assert constraint` goes on a part, not inside a calculation.** Put it in a `part def` or a part usage, bound to the calculation's result there. Not in a `calc def`, and not in a calc usage.

<!-- @tool-example fails="SI_CONSTRAINT_UNATTACHED" -->
```sysml
constraint def Positive { in amount : Real; amount > 0.0 }

// Correct: the part owns the check
part def Heater {
    attribute voltage : Real = 230.0;
    attribute current : Real = 4.0;
    calc power_calc : PowerCalc { in voltage_in = voltage; in current_in = current; }
    attribute power : Real = power_calc.power;
    assert constraint power_ok : Positive { in amount = power; }
}

// Incorrect: the check is inside the calculation
calc def PowerCalc {
    in voltage_in : Real;
    in current_in : Real;
    return power : Real = voltage_in * current_in;
    assert constraint power_ok : Positive { in amount = power; }
}
```

A failed assert does not stop anything. In a generated package each constraint records satisfied, violated or indeterminate, and every output is still computed; SysIDE's own evaluation does not run asserts at all. Whatever reads the results must check the constraint verdicts before using the numbers.

**2. Part multiplicities are exact.** Give a fixed count: a number (`[3]`), or an `Integer` attribute declared with a value in the part def that owns the parts (`[cell_count]`). Not an open range like `[*]`, `[0..*]` or `[1..*]`, and not an attribute declared at package level.

```sysml
// Correct: a number
part cells : Cell[3];

// Correct: an attribute of the owning part def, with its value
part def Pack {
    attribute cell_count : Integer = 3;
    part cells : Cell[cell_count];
}

// Incorrect: no upper bound
part cells : Cell[0..*];
```

Give the count attribute a fixed value (`= 3`) when it never changes. To vary it, give the base a default (`attribute cell_count : Integer default 2;`) and override it in a specializing part def with the `attribute` keyword: `attribute :>> cell_count = 3;` (or `default 3`) builds three parts. Two overrides build the default count (two parts) and nothing warns you: one written without the keyword (`:>> cell_count = 3;`), and any override in a part usage. A base written with `= 2` cannot be overridden at all; the parser refuses the override.

**3. A calculation input receives one value.** Do not pass a calculation a sequence of values: not a feature that spans several parts (`cells.capacity` when there are three cells), not a list-valued attribute (`Real[3] = (1.0, 2.0, 3.0)`), and not a tuple (`(a, b)`). To work over many parts, total them on the part with `sum(cells.capacity)` and pass the total in. Write the total on a `part def` in `library/`; in a `designs/` attribute, validate level 6 rejects the call and the dotted path. A list-valued attribute is refused even when no calculation reads it, so do not declare one at all.

```sysml
// Correct: the part def (in library/) sums its cells; the calculation receives one value
attribute total_capacity : Real = sum(cells.capacity);
calc usable_calc : UsableCapacity { in total_capacity_in = total_capacity; in dod_in = depth_of_discharge; }

// Incorrect: the calculation receives the three cells' values as a sequence
calc total_calc : TotalCapacity { in capacities = cells.capacity; }
```

**Attribute types are scalar.** The generator's typing admits only `Boolean`, `Integer`, `Real` and `String`. An assert that reads a quantity-typed attribute such as `mass : ISQ::MassValue` is refused (`SI_EDGE_DANGLING ... unsupported exact type`), and a custom type such as `attribute def Cost :> Real;` does not accept a literal value (`= 2.0` is a type error in the parser). Write `attribute mass : Real = 2.0 [kg];` and keep the unit in the value and the doc comment. A `String` attribute bound to a calculation input is refused too (`SI_RENDERING_COLLISION`, non-numeric default).

Fuller treatment: agentic-mbse `docs/patterns/constraints.md` (where an assert goes) and `docs/patterns/adr002-calculations.md` (multiplicities and calculation inputs).

## Standard Imports

```sysml
package MyProject::Library::Components {
    import ScalarValues::*;    // Real, Integer, Boolean, String: the only attribute types the generator accepts
    import SI::*;              // SI units, for unit literals such as [kg] and [K]

    // For cost aggregation over multiplicities:
    private import NumericalFunctions::sum;
}
```

## Doc Comment Format

Every `part def`, `calc def`, and `constraint def` requires a doc comment:

<!-- @tool-example -->
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
| `material : Material = SS316;` | Use `material : String = "SS316";` unless Material type is imported. The generator refuses a `String` bound to a calculation input (`SI_RENDERING_COLLISION`), so give a calculation a number instead |
| Qualified names in calc expressions | Use local bindings: `in x = other.value;` not `other.value` inline |
| Self-named binding `in x = x` | Refused by the generator (`SI_SELF_BINDING`): the RHS resolves to the calc's own input, never an outer feature. Rename the parameter in the `calc def` and bind `in x_in = x;` in the usage, so the bare RHS lands on the part attribute. Renaming only the usage's input does not rename the parameter; it still binds by position |
| Calc usage inputs out of definition order | An unprefixed input binds by position, not by name, so correctly named inputs written out of order swap silently (L2 `L2_POSITIONAL_BINDING`). Bind by name, `in :>> a = big;`, or keep definition order; rename on purpose with `redefines`. See agentic-mbse `docs/patterns/semantic-hazards.md#positional-input-binding` |
| `redefines` when meaning `specializes` | `redefines` replaces a feature; `:>` specializes a type — different semantics |
| Missing imports for cross-file refs | Every cross-file reference needs explicit `import` or `private import` |

## Key Syntax Patterns

**Conditional expressions:**
```sysml
attribute diff : Real = if x > y? x - y else y - x;
```
The code generator does not accept this today. If the model will be generated, run `sysml-codegen check` before relying on it.

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
2. **Bind formals; don't inline the predicate.** An inline predicate resolves its names by reaching
   into surrounding scope. Binding every formal to a real value in
   scope makes the wiring explicit and lowerable. It is also the form `@inapplicable:` works on —
   see below.
3. **In a predicate, annotate both operands with a unit, or neither.** `temperature [K] < 1000 [K]`
   and `temperature < 1000.0` both build, and the first compares dimensions (`temperature [m] < 1000
   [K]` is refused, `block_incompatible_dimensions`). One annotated operand, `temperature < 1000 [K]`
   with `temperature : Real`, is refused (`block_ordering_category_pair`). A unit on a binding
   (`in limit = 1000.0 [K];`) is accepted and dropped: the generated check compares plain numbers,
   with no unit check or conversion.

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

Its binding-side sibling is agentic-mbse `docs/patterns/design-choices.md`: a calculation or binding that sets installed capacity from demand deletes a design choice in the same way.

**Cross-file binding:**
```sysml
private import OtherPackage::other_part;
calc my_calc { in value = other_part.exposed_attr; }
```

**Calculation input binding — pick the form by where the value lives:**
- attribute on the part that owns the calc → make the names differ: `in radius_in = radius;`
  (never the self-named `in radius = radius` — refused, not reinterpreted). Rename the parameter in the `calc def`, or rename the attribute; renaming only the usage's input leaves it bound by position;
- value on another part → name the occurrence path: `in driver_cost = driver.cost;`;
- owner-qualified (`comp_a::length`) → resolves to the exact feature owned by that usage;
  a definition-owned leaf falls back to positional occurrence search instead.

The authoritative copy of this rule is agentic-mbse `docs/patterns/plant-idiom.md`,
"Binding a modelled value into a calculation".

Input order on a calc usage matters: an input without `:>>` or `redefines` binds to the definition's parameter at the same position. Bind by name (`in :>> radius_in = radius;`) or keep the definition's order; rename on purpose with `redefines`. See agentic-mbse `docs/patterns/semantic-hazards.md#positional-input-binding`.

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

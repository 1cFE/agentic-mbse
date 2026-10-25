# Calculation Architecture (ADR-002)

Architectural decision record for calculation placement: `calc def` in library, values and wiring in designs.

## When to Use This Document

Reference this document when:
- Deciding where to place calculation logic
- Understanding what expressions are valid in design files
- Resolving "derived expression" violations
- Building cost/analysis calculation hierarchies

## Core Principle

> **Calculation definitions belong in `library/`. Design files contain values and wiring. Expressions that resolve to constants are evaluated at extraction time.**

This extends the Definitions vs Usages pattern:
- `library/` = Reusable algorithms (calc defs) + type definitions (part defs)
- `designs/` = Configuration (values, bindings, calc usages)

---

## Calculation Location Rules

| Rule | Specification |
|------|---------------|
| **Rule 1** | `calc def` declarations SHALL be in `models/library/` only |
| **Rule 2** | Calc usages in `designs/` wire library calc defs to design values |
| **Rule 3** | Design attributes contain literals, bindings, static expressions, or a simple **inline FORMULA** over same-part siblings — reserve real calculations for calc defs |

---

## Expression Taxonomy

| Expression Type | Location | Feature Refs | Result | Example |
|-----------------|----------|--------------|--------|---------|
| **Literal value** | `designs/` attribute | 0 | PASS | `= 3.0 [m]` |
| **True static** | `designs/` attribute | 0 | PASS | `= 3.14159 * 2.0` |
| **EXPOSE pattern** | `designs/` attribute | 1 (calc output) | PASS | `= my_calc.output` |
| **Calc def formula** | `library/` calc def | N/A | N/A | `out result : Real = input * 0.2;` |
| **Binding reference** | Calc usage binding | N/A | N/A | `in value = system.property;` |
| **Inline FORMULA** | `designs/` attribute | ≥1 (same-part sibling) | PASS¹ | `= radius * 2.0` |
| **Computation on calc output** | `designs/` attribute | ≥1 (calc output) | **FAIL** | `= calc.power * 0.95` |
| **Self / dotted reference** | `designs/` attribute | self, or a dotted path | **FAIL** | `= self.x`, `= a.b.c` |
| **Sum over child parts** | `designs/` attribute | dotted path in a function call | **FAIL** | `= sum(cells.capacity)` |
| **Sum over child parts** | `library/` part def | dotted path in `sum` | PASS (generated) | `= sum(cells.capacity)` |

¹ Accepted as a convenience for simple arithmetic and unit conversions over same-part
sibling attributes. For any real or reusable calculation, use a calc def in `library/`
(see [Inline FORMULA vs Calc Def](#inline-formula-vs-calc-def) below).

---

## Valid Patterns in Design Files

```sysml
part component {
    // Literal values (entry points)
    attribute dimension_a : Real = 3.0 [m];
    attribute dimension_b : Real = 5.0 [m];

    // True static expressions (ONLY literals)
    attribute pi_squared : Real = 3.14159 * 3.14159;

    // Inline FORMULA (simple arithmetic over same-part siblings)
    attribute area : Real = dimension_a * dimension_b;

    // EXPOSE pattern (pure value propagation from calc output)
    attribute result : Real = my_calc.output;
}
```

---

## Inline FORMULA vs Calc Def

A design attribute may reference **same-part sibling** attributes — a supported "inline
FORMULA" computed attribute. Reserve it for simple arithmetic and unit conversions:

<!-- @tool-example -->
```sysml
part component {
    attribute length : Real = 3.0 [m];
    attribute width  : Real = 4.0 [m];

    // Inline FORMULA: fine for simple arithmetic over same-part siblings.
    attribute area : Real = length * width;
}
```

For any real or reusable calculation, still prefer a `calc def` in `library/`. It is
named, testable, and reused across designs — the inline form is a convenience, not a
replacement:

<!-- @tool-example -->
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

**What an inline FORMULA may NOT do** — these still fail and must move into a calc def:
- compute on a calc output — `= power_calc.power * 0.95`
- reference itself — `= area * 2` inside `area`
- reach through a dotted path — `= subsystem.rotor.power`

---

## Supported Static Operators

| Operator | Example |
|----------|---------|
| `+`, `-`, `*`, `/` | `a + b`, `a * 2.0` |
| `[` (unit annotation) | `3.0 [m]` |

**Not supported in design attributes** (require calc def):
- Exponentiation (`**`, `^`)
- Functions (`sin`, `sqrt`, `abs`)
- Conditionals (`if ... else`)
- A reference to a calc output inside arithmetic, a self-reference, or a dotted path
  (a plain same-part sibling reference is an inline FORMULA — allowed)

---

## No Loops (rule A-3)

The computation graph must be a DAG — no calc may depend, directly or transitively, on
its own output. A cycle (`A` binds an input from `B`'s output, `B` binds an input from
`A`'s output) has no valid execution order and is rejected. Break the cycle: introduce an
intermediate value, or restructure so one calc produces what the other consumes. See the
circular-dependency example in `semantic-operators.md`.

---

## Calculation Inputs and Part Counts

The code generator (sysml-codegen) refuses two calculation-shaped structures that parse and validate without complaint. Avoid both from the start when the project targets generated code. The third limit, where an `assert constraint` goes, is in [constraints.md](constraints.md#checking-a-calculations-result-assert-on-the-part).

**A calculation input receives one value.** Do not pass a calculation a sequence of values: not a feature that spans several parts (`cells.capacity` when there are three cells), not a list-valued attribute (`Real[3] = (1.0, 2.0, 3.0)`), and not a tuple (`(a, b)`). To work over many parts, total them on the part with `sum(cells.capacity)` and pass the total in. Write the total on a `part def` in `library/`; in a `designs/` attribute, validate level 6 rejects the call and the dotted path. A list-valued attribute is refused even when no calculation reads it, so do not declare one at all.

```sysml
// Correct: the part def (in library/) sums its cells; the calculation receives one value
attribute total_capacity : Real = sum(cells.capacity);
calc usable_calc : UsableCapacity { in total_capacity_in = total_capacity; in dod_in = depth_of_discharge; }

// Incorrect: the calculation receives the three cells' values as a sequence
calc total_calc : TotalCapacity { in capacities = cells.capacity; }
```

**Part multiplicities are exact.** Give a fixed count: a number (`[3]`), or an `Integer` attribute declared with a fixed value (`= 3`) in the part def that owns the parts. Not an open range like `[*]`, `[0..*]` or `[1..*]`, and not an attribute declared at package level. To vary the count, give the base a default (`attribute cell_count : Integer default 2;`) and override it in a specializing part def with the `attribute` keyword (`attribute :>> cell_count = 3;` or `default 3`): that builds three parts. An override written without the keyword (`:>> cell_count = 3;`), or any override in a part usage, builds the default count with no warning. A base written with `= 2` cannot be overridden; the parser refuses the override.

```sysml
part cells : Cell[3];       // Correct: exactly three
part cells : Cell[0..*];    // Incorrect: no upper bound
```

---

## Costing an Assembly (Rollups)

An assembly's cost is the sum of its children's costs (a rollup). Write the rollup on each assembly's `part def` in `library/`, and let each level add up the totals of the level below. The example is a three-level cart: four kinds of leaf part each cost themselves, two sub-assemblies add up their children, and the cart adds up the sub-assemblies. It passes `agentic-mbse validate` and `sysml-codegen check`.

<!-- @tool-example -->
```sysml
package CartCosting {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    abstract part def 'Costed Item' {
        attribute capital_cost : Real;
    }

    calc def UnitCost {
        in size_in : Real;
        in rate_in : Real;
        out attribute cost : Real = size_in * rate_in;
    }

    // Leaves: each part costs itself with one calc usage
    part def Panel :> 'Costed Item' {
        attribute area : Real;
        calc cost_model : UnitCost { in size_in = area; in rate_in = 12.0; }
        :>> capital_cost = cost_model.cost;
    }

    part def Caster :> 'Costed Item' {
        attribute load_rating : Real;
        calc cost_model : UnitCost { in size_in = load_rating; in rate_in = 0.75; }
        :>> capital_cost = cost_model.cost;
    }

    part def Rail :> 'Costed Item' {
        attribute length : Real;
        calc cost_model : UnitCost { in size_in = length; in rate_in = 25.0; }
        :>> capital_cost = cost_model.cost;
    }

    part def Brace :> 'Costed Item' {
        attribute brace_count : Real;
        calc cost_model : UnitCost { in size_in = brace_count; in rate_in = 5.0; }
        :>> capital_cost = cost_model.cost;
    }

    // Groups of the same kind: sum() adds one term per child occurrence
    part def Deck :> 'Costed Item' {
        part panel : Panel[4];
        part caster : Caster[4];
        :>> capital_cost = sum(panel.capital_cost) + sum(caster.capital_cost);
    }

    // One child of each kind: read each one directly
    part def Frame :> 'Costed Item' {
        part rail : Rail;
        part brace : Brace;
        :>> capital_cost = rail.capital_cost + brace.capital_cost;
    }

    // Rollups nest: the cart adds its sub-assemblies' totals
    part def Cart :> 'Costed Item' {
        part deck_assembly : Deck;
        part frame_assembly : Frame;
        :>> capital_cost = deck_assembly.capital_cost + frame_assembly.capital_cost;
    }

    // In a project this usage lives in designs/; the example keeps it here so it is one file
    part cart : Cart;
}
```

What each assembly shows:

- **A group of the same kind** (`Deck`). `part panel : Panel[4];` with `sum(panel.capital_cost)` adds one term per panel, four in all. The count must be exact (see [Calculation Inputs and Part Counts](#calculation-inputs-and-part-counts)).
- **Two groups in one expression** (`Deck`). Two `sum()` terms may read the same-named attribute (`capital_cost`) off different groups. The generator keeps the panel and caster inputs apart; sysml-codegen's `test_a_two_term_same_name_rollup_keeps_both_resolved_source_families` pins this.
- **One child of each kind** (`Frame`). Read each child's attribute directly: `rail.capital_cost + brace.capital_cost`.
- **Nesting** (`Cart`). An assembly adds its sub-assemblies' rolled-up values the same way it adds leaves. Each sub-assembly here appears once; for two or more copies, see [Repeated sub-assemblies](#repeated-sub-assemblies).

Naming each group's total first also works and is optional: `attribute panel_capital : Real = sum(panel.capital_cost);`, then `:>> capital_cost = panel_capital + caster_capital;`. It reads well in a long rollup, and each named total becomes its own generated module you can inspect. sysml-codegen's `costed_cart_d5` fixture uses this form.

Where the children are modelled, roll their values up as above. Do not declare a placeholder total on the assembly and bind a hand-typed number to it in a design; it drifts from the children.

Both tools check that this example builds, not what it computes. sysml-codegen's `test_the_deck_rollup_sums_its_four_panels_and_the_allocation` checks the numbers of its fixture's deck, which names each group's total and adds an allocation cost. No test checks the numbers of the direct `sum() + sum()` form shown here.

### Where the rollup goes

ADR-002 keeps calculations, rollups included, on `part def`s in `library/`. Validate level 6 catches a `sum()` on an attribute declared in a `designs/` file (`V2_DYNAMIC_EXPRESSION`, below), but not the `:>>` redefinition form used in the example above, so the placement is a convention validate only partly enforces. The generator builds the rollup in either place.

<!-- @tool-example dir="designs" fails="V2_DYNAMIC_EXPRESSION" -->
```sysml
part def Wheel {
    attribute capital_cost : Real = 40.0;
}

// Wrong in designs/: validate level 6 rejects sum() over child parts here
part def Axle {
    part wheel : Wheel[2];
    attribute capital_cost : Real = sum(wheel.capital_cost);
}

part axle : Axle;
```

### Repeated sub-assemblies

The generator refuses two or more copies of a sub-assembly whose own cost is a computed rollup: a group such as `part deck_assembly : Deck[2];`, or two named parts typed `Deck`. `sysml-codegen check` fails with `REGISTRY_CLASS_NAME_COLLISION`, though validate passes. One copy builds, and so do several copies whose cost is a plain value (a leaf group such as `Panel[4]`). This is a current limit of sysml-codegen, not a modelling rule. When it is lifted, the example below stops failing and its test turns red, which is the signal to update this section.

<!-- @tool-example fails="REGISTRY_CLASS_NAME_COLLISION" -->
```sysml
part def Shelf {
    attribute capital_cost : Real = 30.0;
}

part def Rack {
    part shelf : Shelf[3];
    attribute capital_cost : Real = sum(shelf.capital_cost);
}

// Refused by the generator: two racks, each with a computed rollup of its own
part def Facility {
    part rack : Rack[2];
    attribute capital_cost : Real = sum(rack.capital_cost);
}

part facility : Facility;
```

---

## Common Mistakes

### Putting calc def in designs

```sysml
// WRONG: Calc def in design file
package MyDesign {
    calc def MyFormula {  // VIOLATION of ADR-002!
        in x : Real;
        out y : Real = x * 2;
    }
}

// CORRECT: Calc def in library
package MyLibrary::Analyses {
    calc def MyFormula {
        in x : Real;
        out y : Real = x * 2;
    }
}
```

### Self-reference or dotted path in an inline FORMULA

An inline FORMULA may read same-part siblings only — not itself, and not through a
dotted path into another part.

```sysml
// WRONG: self-reference (a FORMULA may not read its own value)
attribute total : Real = total + 1.0;

// WRONG: dotted path into another part
attribute p : Real = subsystem.rotor.power;

// OK: same-part siblings
attribute margin : Real = revenue - cost;
```

### Computation on calc output

```sysml
// WRONG: Further computation on calc output
attribute adjusted_power : Real = power_calc.power * 0.95;  // Computation!

// CORRECT: Include adjustment in calc def
calc def AdjustedPowerCalc {
    in raw_power : Real;
    in efficiency : Real default := 0.95;
    out adjusted_power : Real = raw_power * efficiency;
}
```

---

## Decision Flow

```
Is this expression in a design attribute?
|
+-- Only literals? -> Static expression -> OK
|   (e.g., = 3.14159 * 2.0)
|
+-- Only same-part siblings? -> Inline FORMULA -> OK for simple arithmetic
|   (e.g., = length * width; prefer a calc def for real calculations)
|
+-- Just exposing one calc output? -> EXPOSE pattern -> OK
|   (e.g., = my_calc.output)
|
+-- Calc output in arithmetic, self-reference, or dotted path -> EXTRACT TO CALC DEF
    (e.g., = calc.power * 0.95)
```

---

## Related Patterns

- [definitions-usages.md](definitions-usages.md) - Definition vs Usage distinction
- [expose-pattern.md](expose-pattern.md) - EXPOSE pattern for calc outputs
- [semantic-operators.md](semantic-operators.md) - Binding operators
- [mbse-concepts.md](mbse-concepts.md) - Cost calculation patterns

---

## Verification

All examples verified with syside parser.

**Test command:**
```bash
syside check <file.sysml>
```

---

*Last Updated: 2026-01-15*

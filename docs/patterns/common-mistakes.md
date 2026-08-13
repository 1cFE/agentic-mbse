# Common Mistakes to Avoid

Anti-patterns and corrections for SysML v2 modeling.

## When to Use This Document

Reference this document when:
- Reviewing models for issues
- Learning SysML v2 best practices
- Debugging unexpected model behavior
- Onboarding new team members

---

## Mistake 1: Mixing Definitions and Usages

### Don't: Definition and usage in same package

```sysml
// BAD: Definition and usage together
package MyProject::Components {
    part def 'Component Type' { ... }
    part my_component : 'Component Type' { ... }  // Wrong place!
}
```

### Do: Separate library and designs

```sysml
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

**Why:** Separation enables reuse, cleaner dependencies, and follows SysML v2 intent.

---

## Mistake 2: Omitting Documentation

### Don't: Undocumented elements

```sysml
// BAD: No doc comment - where does this come from?
part def 'Component' {
    attribute property : Length;
}
```

### Do: Document thoroughly

```sysml
// GOOD: Full documentation
part def 'Component' {
    doc /*
    Component description

    **Source**: Reference document
    **Last Updated**: 2026-01-15
    */
    attribute property : Length {
        doc /* Property description and typical range */
    }
}
```

**Why:** Traceability, maintainability, and enabling future users to understand the model.

---

## Mistake 3: Wrong Naming Conventions

### Don't: Inconsistent naming

```sysml
// BAD: snake_case for definition
part def component_type { ... }

// BAD: Title Case for usage
part 'My Component' : 'Component Type' { ... }
```

### Do: Follow conventions

```sysml
// GOOD: Title Case with quotes for definitions
part def 'Component Type' { ... }

// GOOD: snake_case for usages
part my_component : 'Component Type' { ... }
```

**Convention Summary:**
| Element | Convention | Example |
|---------|------------|---------|
| Definitions | `'Title Case'` | `part def 'Heat Exchanger'` |
| Usages | `snake_case` | `part primary_exchanger` |
| Attributes | `snake_case` | `attribute flow_rate` |
| Packages | `PascalCase::path` | `MyProject::Library` |

---

## Mistake 4: Calc Defs in Design Files

### Don't: Put calc defs in designs

```sysml
// BAD: Calc def in design file (violates ADR-002)
package MyDesign {
    calc def AreaCalculation {
        in length : Real;
        in width : Real;
        out area : Real = length * width;
    }
}
```

### Do: Keep calc defs in library

```sysml
// GOOD: Calc def in library
package MyLibrary::Analyses {
    calc def AreaCalculation {
        in length : Real;
        in width : Real;
        out area : Real = length * width;
    }
}

// GOOD: Calc usage in design
package MyDesign {
    private import MyLibrary::Analyses::AreaCalculation;

    part component {
        calc area_calc : AreaCalculation { ... }
    }
}
```

**Why:** Enables reuse, maintains separation of concerns, follows ADR-002.

---

## Mistake 5: Computing on a Calc Output (or Reaching Outside the Part)

A design attribute may reference **same-part siblings** inline — `attribute area : Real =
length * width` is a supported inline FORMULA, fine for simple arithmetic. What still fails
is computing on a calc output, referencing the attribute itself, or reaching through a dotted
path.

### Don't: Compute on a calc output or reach outside the part

```sysml
// BAD: arithmetic on a calc output in a design attribute
attribute adjusted : Real = power_calc.power * 0.95;  // VIOLATION!

// BAD: self-reference / dotted path
attribute total : Real = total + 1.0;                 // VIOLATION!
attribute p : Real = subsystem.rotor.power;           // VIOLATION!
```

### Do: Use calc def with EXPOSE

```sysml
// GOOD: fold the adjustment into a calc def
calc def AdjustedPowerCalc {
    in raw_power : Real;
    in efficiency : Real default := 0.95;
    out adjusted : Real = raw_power * efficiency;
}

part component {
    calc adj : AdjustedPowerCalc {
        in raw_power = power_calc.power;
    }
    attribute adjusted : Real = adj.adjusted;  // EXPOSE
}
```

**Why:** Same-part arithmetic is a convenience; real calculations and anything reading a calc
output belong in the library, keeping design files clean and the computation reusable.

---

## Mistake 6: Missing Units

### Don't: Omit units

```sysml
// BAD: No units - what is this?
attribute temperature = 300;
attribute power = 2600;
```

### Do: Always specify units

```sysml
// GOOD: Units specified
attribute temperature = 300 [K];
attribute power = 2600 [MW];
attribute efficiency = 0.85;  // Dimensionless OK
```

**Why:** Prevents unit confusion, enables dimensional analysis.

---

## Mistake 7: Cross-Type Redefinition in Definitions

### Don't: Use `:>>` across types in definitions

```sysml
// BAD: Cross-type redefinition (causes warnings)
calc def ConsumerCalc {
    in x : Real :>> SourceCalc::result;  // Don't do this!
}
```

### Do: Bind in usages

```sysml
// GOOD: Clean definitions
calc def ConsumerCalc {
    in x : Real;  // Just declare type
}

// GOOD: Bind in usage
calc consumer : ConsumerCalc {
    in x = source_instance.result;  // Bind here
}
```

**Why:** Avoids semantic warnings, follows SysML v2 intent.

---

## Mistake 8: Expecting a Plain Constraint to Be Checked

### Don't: Plain constraint block

```sysml
// BAD: parses fine, but never executes
constraint TempLimit {
    temperature < 1000 [K]
}
```

### Do: Use the assert prefix

```sysml
// GOOD: an executed check
assert constraint TempLimit {
    doc /* Operating temperature limit */
    temperature < 1000 [K]
}
```

**Why:** the parser does create a ConstraintUsage without the prefix — it is classified
`plain_usage`, cataloged, and visible, but the form gate stops it before the predicate is walked.
The assert family is the only enforcement opt-in; `require` and `assume` are cataloged and visible
too, and neither executes.

---

## Mistake 9: Same Package Name in Multiple Files

### Don't: Reuse package names

```sysml
// thermal.sysml
package Analyses { ... }

// electrical.sysml
package Analyses { ... }  // Creates DIFFERENT package!
```

### Do: Unique package names

```sysml
// thermal.sysml
package ThermalAnalyses { ... }

// electrical.sysml
package ElectricalAnalyses { ... }
```

**Why:** Each package declaration creates a new element with unique UUID.

---

## Mistake 10: Importing Definition Instead of Instance

### Don't: Import type when you need instance

```sysml
// BAD: Importing the definition
private import MyLibrary::'Component Type';
// Can't access: 'Component Type'.some_attribute

// BAD: Trying to reference without import
calc my_calc {
    in x = OtherPackage::other_part.value;  // Won't resolve!
}
```

### Do: Import the instance

```sysml
// GOOD: Import the instance
private import MyDesign::my_component;
// Can access: my_component.some_attribute

// GOOD: Import then reference
private import OtherPackage::other_part;
calc my_calc {
    in x = other_part.value;  // Works!
}
```

**Why:** Cross-file binding requires importing the actual instance.

---

## Quick Checklist

```markdown
Model Review Checklist:
- [ ] Definitions in library/, usages in designs/
- [ ] All definitions have doc comments
- [ ] Naming conventions followed
- [ ] No calc defs in design files
- [ ] No calc-output arithmetic, self-references, or dotted paths in design attributes (inline FORMULA over same-part siblings is OK)
- [ ] Units specified on all physical quantities
- [ ] Constraints have assert/require prefix
- [ ] Package names unique across files
- [ ] Instances imported for cross-file binding
```

---

## Related Patterns

- [definitions-usages.md](definitions-usages.md) - Separation pattern
- [adr002-calculations.md](adr002-calculations.md) - Calculation rules
- [semantic-operators.md](semantic-operators.md) - Operator usage
- [package-naming.md](package-naming.md) - Package organization
- [doc-comments.md](doc-comments.md) - Documentation standards

---

*Last Updated: 2026-01-15*

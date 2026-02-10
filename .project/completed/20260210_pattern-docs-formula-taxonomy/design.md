# Design: Pattern Documentation — Expression Taxonomy and Decision Flow

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-09 23:52 UTC
**Branch:** adr004-005
**Commit:** 201723d

## Overview

Update two pattern docs (`adr002-calculations.md`, `expose-pattern.md`) to reflect the ADR-002 amendment permitting FORMULA computed attributes. This is a pure documentation change — no code, no design alternatives. The content is fully determined by three authority sources (ADR-002 amendment, ADR-004, ADR-005) and must be consistent with the implemented `_is_formula_pattern()` in `adr002.py:393-452`.

## Related Artifacts

- **Spec:** `.project/active/pattern-docs-formula-taxonomy/spec.md`
- **Epic:** `.project/backlog/epic_computed-attribute-integration.md` (EPIC-COMPATTR-001, Item 2)
- **Implementation (Item 1):** `src/agentic_mbse/validation/adr002.py:393-452` (`_is_formula_pattern()`)
- **Authority sources:**
  - ADR-002 Amendment (§ "Amendment: FORMULA Computed Attributes")
  - ADR-004 (pipeline integration, module naming)
  - ADR-005 (5-way classification: FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE)

## Research Findings

### Current Document Structure

**`docs/patterns/adr002-calculations.md`** (242 lines):
- Lines 24-29: Calculation Location Rules table (Rule 1, 2, 3)
- Lines 33-43: Expression Taxonomy table (7 rows)
- Lines 47-61: Valid Patterns code block
- Lines 65-101: "Invalid Pattern: Derived Expression" section with CalcDef resolution
- Lines 104-116: "Supported Static Operators" section
- Lines 119-146: "Validated Patterns" section (Multiplicity Cost Aggregation — untouched)
- Lines 149-196: "Common Mistakes" section (3 subsections)
- Lines 200-217: "Decision Flow" ASCII tree
- Lines 221-226: "Related Patterns" links
- Lines 230-241: "Verification" + "Last Updated"

**`docs/patterns/expose-pattern.md`** (288 lines):
- Lines 1-28: Header, "When to Use", Quick Reference
- Lines 32-55: "Why Use EXPOSE" (3 subsections)
- Lines 58-85: "How to Use" (Producer/Consumer)
- Lines 89-146: "Complete Example" (Library + Producer + Consumer)
- Lines 150-196: "Anti-Patterns" (3 subsections)
- Lines 200-234: "EXPOSE vs Direct Binding" with table + examples
- Lines 238-263: "Common Mistakes" (2 subsections)
- Lines 267-287: "Related Patterns", "Verification", "Last Updated"

### Implemented FORMULA Logic (consistency check)

The validator (`adr002.py:545-558`) checks in this order:
1. `len(refs) == 0` → true static → OK
2. `_is_expose_pattern()` → EXPOSE → OK
3. `_is_formula_pattern()` → FORMULA → OK
4. Everything else → V2_DYNAMIC_EXPRESSION violation

`_is_formula_pattern()` (`adr002.py:393-452`) returns True when:
- Top-level expression is NOT a FeatureChainExpression
- Has >=1 ref
- All refs have the same owner as the attribute (sibling check via `ref_owner is attr_owner`)
- No ref is a calc output (`_is_calc_output_reference()` returns False for all refs)

This matches the ADR-005 FORMULA definition exactly. The pattern docs must describe the same conditions.

## Proposed Design

No design alternatives — the changes are prescribed by the spec with content sourced from the authority ADRs. Below is the exact edit plan for each section.

### File 1: `docs/patterns/adr002-calculations.md`

#### Edit 1: Rule 3 in Calculation Location Rules (FR-1)

**Location:** Line 29

**Current:**
```
| **Rule 3** | Design attributes contain literals, bindings, or **static expressions** |
```

**Replace with:**
```
| **Rule 3** | Design attributes contain literals, bindings, static expressions, or **FORMULA expressions** (sibling-only arithmetic per [ADR-002 Amendment](#formula-computed-attributes)) |
```

#### Edit 2: Expression Taxonomy Table (FR-2)

**Location:** Lines 35-43

**Current:** 7-row table with "Derived expression" (FAIL) and "Computation on calc" (FAIL) as the last two rows.

**Replace with:** 8-row table. Insert FORMULA row between "True static" and "EXPOSE pattern". Merge the two FAIL rows into one "Derived expression" row that covers all non-FORMULA, non-EXPOSE refs:

```markdown
| Expression Type | Location | Feature Refs | Result | Example |
|-----------------|----------|--------------|--------|---------|
| **Literal value** | `designs/` attribute | 0 | PASS | `= 3.0 [m]` |
| **True static** | `designs/` attribute | 0 | PASS | `= 3.14159 * 2.0` |
| **FORMULA expression** | `designs/` attribute | >=1 (sibling attrs only) | **PASS** | `= length * width` |
| **EXPOSE pattern** | `designs/` attribute | 1 (calc output) | PASS | `= my_calc.output` |
| **Calc def formula** | `library/` calc def | N/A | N/A | `out result : Real = input * 0.2;` |
| **Binding reference** | Calc usage binding | N/A | N/A | `in value = system.property;` |
| **Derived expression** | `designs/` attribute | >=1 (calc output refs) | **FAIL** | `= calc.output * 0.95` |
```

**Rationale:** The old "Derived expression" and "Computation on calc" rows both represented expressions with refs that aren't sibling-only. Merging them into one row simplifies the table and reflects the actual validator logic: anything that isn't true-static, EXPOSE, or FORMULA is a violation.

#### Edit 3: Valid Patterns Code Block (FR-3 supporting)

**Location:** Lines 47-61

**Add** a FORMULA example to the existing code block:

```sysml
part component {
    // Literal values (entry points)
    attribute dimension_a : Real = 3.0 [m];
    attribute dimension_b : Real = 5.0 [m];

    // True static expressions (ONLY literals, no design attribute refs)
    attribute pi_squared : Real = 3.14159 * 3.14159;

    // FORMULA expressions (sibling attributes only, per ADR-002 Amendment)
    attribute area : Real = dimension_a * dimension_b;

    // EXPOSE pattern (pure value propagation from calc output)
    attribute result : Real = my_calc.output;
}
```

#### Edit 4: "Invalid Pattern" Section Amendment (FR-3)

**Location:** Lines 65-101

**Approach:** Keep the entire existing section (code block, explanation, CalcDef resolution) but add an amendment callout at the top between the heading and the code block. The callout explains that `area = length * width` is now valid as a FORMULA pattern, while preserving the CalcDef path as an alternative.

Insert after line 65 (`## Invalid Pattern: Derived Expression`):

```markdown
> **Amendment (2026-02-09):** The expression below (`length * width`) is now **valid** as a FORMULA computed attribute when all references are sibling attributes on the same part. The codegen pipeline auto-generates a module for it (see ADR-004). The CalcDef resolution shown below remains a valid alternative for reusable or complex formulas. See [FORMULA Computed Attributes](#formula-computed-attributes) below.
```

Update the code block comment from "VIOLATION" to conditional:

```sysml
part component {
    attribute length : Real = 3.0 [m];
    attribute width : Real = 4.0 [m];

    // VALID as FORMULA (all refs are siblings on same part)
    // OR extract to CalcDef for reusable/complex formulas
    attribute area : Real = length * width;
}
```

Update the explanation paragraph:

```markdown
**When this is still a violation:** If the expression references calc outputs (e.g., `calc.output * 0.95`) or attributes on other parts (cross-part references), it remains a derived expression violation. Only sibling attribute references on the same part qualify as FORMULA.
```

Keep the "Resolution: Extract to Calc Def" subsection unchanged — it remains a valid alternative.

#### Edit 5: "Supported Static Operators" Section (FR-4)

**Location:** Lines 104-116

**Current "Not supported" list:**
```
**Not supported in design attributes** (require calc def):
- Exponentiation (`**`, `^`)
- Functions (`sin`, `sqrt`, `abs`)
- Conditionals (`if ... else`)
- References to other design attributes
```

**Replace with:**
```markdown
**Not supported in design attributes** (require calc def):
- Exponentiation (`**`, `^`)
- Functions (`sin`, `sqrt`, `abs`)
- Conditionals (`if ... else`)
- Cross-part attribute references or calc output references

**Supported via FORMULA** (per ADR-002 Amendment):
- References to sibling attributes on the same part (`+`, `-`, `*`, `/`)
- Example: `attribute area = length * width` where `length` and `width` are siblings
```

#### Edit 6: "Common Mistakes" Section (FR-6)

**Location:** Lines 171-182 (subsection "Derived expressions in attributes")

**Replace** the "Derived expressions in attributes" subsection with:

```markdown
### Derived expressions in attributes

```sysml
// STILL WRONG: Computation on a calc output
attribute adjusted_power : Real = power_calc.power * 0.95;  // Calc output ref!

// NOW VALID: FORMULA — all refs are sibling attributes (per ADR-002 Amendment)
attribute diameter : Real = radius * 2.0;  // 'radius' is a sibling on same part

// ALSO VALID: CalcDef alternative (preferred for reusable/complex formulas)
calc diameter_calc : DiameterCalc {
    in radius = component::radius;
}
attribute diameter : Real = diameter_calc.diameter;
```​
```

**Add** a new subsection after "Computation on calc output" (after line 196):

```markdown
### Using CalcDef when FORMULA suffices

```sysml
// UNNECESSARY: CalcDef ceremony for a one-off sibling formula
calc def AreaCalc {
    in length : Real;
    in width : Real;
    out area : Real = length * width;
}
calc area_calc : AreaCalc {
    in length = component::length;
    in width = component::width;
}
attribute area : Real = area_calc.area;

// SIMPLER: FORMULA attribute expression (per ADR-002 Amendment)
attribute area : Real = length * width;  // All refs are siblings — valid!
```​

**When to use CalcDef instead:** Reusable formulas shared across parts, complex logic with multiple intermediates, or expressions referencing calc outputs.
```

#### Edit 7: Decision Flow (FR-5)

**Location:** Lines 200-217

**Replace** the entire decision flow code block:

```markdown
## Decision Flow

```
Is this expression in a design attribute?
|
+-- Does it reference other features (attributes, calc outputs)?
    |
    +-- NO: Static expression -> OK
    |   (e.g., = 3.14159 * 2.0)
    |
    +-- YES: Are ALL references sibling attributes on the same part?
        |
        +-- YES: FORMULA computed attribute -> OK
        |   (e.g., = length * width)
        |   Generates a pipeline module (ADR-004)
        |
        +-- NO: Is it a single reference exposing a calc output?
            |
            +-- YES: EXPOSE pattern -> OK
            |   (e.g., = my_calc.output)
            |
            +-- NO: Derived expression -> EXTRACT TO CALC DEF
                (e.g., = calc.output * 0.95)
```​
```

This mirrors the validator logic order: true static → EXPOSE → FORMULA → violation. Note: the decision flow reorders FORMULA before EXPOSE for readability (the "are all refs siblings?" question is the natural first branch for a modeler), but both paths are independent checks in the validator.

#### Edit 8: Add FORMULA Section (FR-7)

**Location:** Insert before "Related Patterns" (before line 221)

Add a new section that serves as the link target for the Rule 3 anchor and collects FORMULA guidance in one place:

```markdown
## FORMULA Computed Attributes

> **Added 2026-02-09 per ADR-002 Amendment, ADR-004, ADR-005**

Design attributes MAY contain arithmetic expressions referencing **only sibling attributes** on the same part. These are classified as FORMULA computed attributes and generate synthetic pipeline modules with auto-implemented code.

### Conditions (all must hold)

- All feature references resolve to sibling attributes (same owning part)
- No `FeatureChainExpression` nodes (no calc output references, no cross-part references)
- Supported operators: `+`, `-`, `*`, `/`

### Examples

```sysml
part plant {
    attribute length : Real = 10.0;
    attribute width : Real = 5.0;
    attribute rate : Real = 12.0;

    // FORMULA: simple binary (siblings only)
    attribute area : Real = length * width;

    // FORMULA: chain — references another computed attr (still a sibling)
    attribute cost : Real = area * rate;

    // FORMULA: unit conversion with literal
    attribute p_net_kw : Real = p_net_mw * 1000.0;
}
```​

### FORMULA vs CalcDef

| Use | When |
|-----|------|
| **FORMULA** (attribute expression) | One-off formula, sibling attrs only, simple arithmetic |
| **CalcDef** (library/) | Reusable logic, complex expressions, calc output refs, functions |

### Related ADRs

- **ADR-002 Amendment**: Rule 3 relaxation conditions, modeling guidance
- **ADR-004**: Pipeline integration — Option C, Step 4.5, synthetic module naming
- **ADR-005**: 5-way classification scheme (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE)
```

#### Edit 9: Last Updated (FR-8)

**Location:** Line 241

Change `*Last Updated: 2026-01-15*` to `*Last Updated: 2026-02-09*`.

---

### File 2: `docs/patterns/expose-pattern.md`

#### Edit 10: Add "FORMULA vs EXPOSE" Section (FR-9, FR-10)

**Location:** Insert before "Related Patterns" (before line 267)

```markdown
## FORMULA vs EXPOSE

> **Added 2026-02-09 per ADR-002 Amendment, ADR-005**

Modelers encounter two patterns that look similar — `attribute x = a * b` and `attribute x = calc.output` — but they serve different purposes and receive different pipeline treatment. This section clarifies the distinction.

### Classification

| Pattern | Example | What It Does | Pipeline Treatment | Validation |
|---------|---------|-------------|-------------------|------------|
| **FORMULA** | `attribute area = length * width` | Arithmetic on sibling attributes | Generates synthetic pipeline module (ADR-004) | PASS |
| **EXPOSE (pure)** | `attribute x = calc.output` | Forwards a calc output as a design attribute | Channel alias (no module) | PASS |
| **EXPOSE_COMPUTED** | `attribute x = calc.output * 2.0` | Calc output + arithmetic | **Not yet supported** | FAIL |

### Key Distinction

- **FORMULA** references **sibling attributes** (same part, no dotted paths). All refs have the same owner.
- **EXPOSE** references a **calc output** via a dotted path (`calc_usage.output_name`). This is a `FeatureChainExpression` in the AST.
- **EXPOSE_COMPUTED** mixes both: a calc output ref wrapped in arithmetic. This is deferred — use a CalcDef as a workaround.

### When to Use Each

```sysml
part plant {
    attribute length : Real = 10.0;
    attribute width : Real = 5.0;

    // FORMULA: simple arithmetic on siblings → OK
    attribute area : Real = length * width;

    calc cost_calc : CostCalc {
        in area = plant::area;
    }

    // EXPOSE (pure): forward calc output → OK
    attribute total_cost : Real = cost_calc.cost;

    // EXPOSE_COMPUTED: calc output + arithmetic → NOT YET SUPPORTED
    // attribute adjusted_cost : Real = cost_calc.cost * 1.15;
    // Workaround: create a CalcDef for the adjustment
}
```​

See [adr002-calculations.md](adr002-calculations.md) for the full expression taxonomy and decision flow.
```

#### Edit 11: Last Updated (FR-11)

**Location:** Line 287

Change `*Last Updated: 2026-01-15*` to `*Last Updated: 2026-02-09*`.

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Examples use SysML syntax that doesn't parse | Low — modelers copy-paste broken code | Examples reuse patterns from ADR-005 §Examples (already validated in sysml-codegen spike). Keep existing verified examples where possible. |
| FORMULA section anchor (`#formula-computed-attributes`) conflicts with existing anchors | Low — breaks Rule 3 internal link | Verify no existing anchor matches before finalizing. |
| "Invalid Pattern" amendment confuses readers who expect a clear valid/invalid binary | Low — modelers unsure whether the example is valid or not | The amendment callout is placed above the code block with explicit "this is now valid" language. The "When this is still a violation" paragraph clarifies the boundary. |

## Integration Strategy

These two files ship as part of the `agentic_mbse_data` package. They're installed into target repos via `agentic-mbse init` and are also referenced directly by the Claude agents (kerml-expert, sysml-expert, sysmlv2-validator). No changes to the packaging or installation mechanism are needed — updating the source files in `docs/patterns/` is sufficient.

Items 3 (agent commands) and 4 (project templates) will reference the new FORMULA section by anchor link, so the anchor name `#formula-computed-attributes` should be treated as stable.

## Validation Approach

1. **Visual review**: Read through each edited section to confirm it matches the authority ADR content
2. **Consistency check**: Verify the decision flow order matches the validator logic in `adr002.py:545-558`
3. **Cross-doc check**: Verify no contradictions between the two pattern docs
4. **Test suite**: `uv run pytest tests/` — docs-only change should not affect any tests

---

**Next Step:** After approval → `/_my_implement` (straightforward edits, no planning phase needed)

---
date: 2026-01-09T21:34:22-08:00
researcher: Claude
topic: "SysMLv2 Conditional Expressions - Definitive Syntax Reference"
tags: [research, sysmlv2, conditionals, expressions, syntax, kerml]
status: complete
last_updated: 2026-01-09
---

# Research: SysMLv2 Conditional Expressions - Definitive Reference

**Date**: 2026-01-09 21:34:22 PST
**Researcher**: Claude
**Research Type**: Language Syntax / Specification Verification

## Research Question

Original user query:
> The fusion-tea project had confusion about conditional expressions. The MODELING_GUIDE was updated to say SysML v2 does NOT support conditionals, but a research document claimed they DO work with `if COND? VALUE else VALUE` syntax. Settle this definitively.

## Summary

**VERDICT: SysML v2 DOES support conditional expressions, but the syntax is unique.**

| Syntax | Status | Parser Result |
|--------|--------|---------------|
| `if CONDITION? TRUE_VALUE else FALSE_VALUE` | **CORRECT** | Parses successfully (exit code 0) |
| `condition ? trueValue : falseValue` | **WRONG** | Parse error |
| `if condition then trueValue else falseValue endif` | **WRONG** | Parse error |

**The original fusion-tea research document (20260105-172101) was CORRECT.** The MODELING_GUIDE was incorrectly updated to say conditionals don't work.

## Detailed Findings

### Verified CORRECT Syntax

The SysML v2 / KerML conditional expression syntax is:

```sysml
// Basic conditional
attribute result : Real = if x > y? x - y else y - x;

// Chained conditionals
attribute factor : Real =
    if mode == 1? 0.95
    else if mode == 2? 0.85
    else 0.60;

// Enum conditionals (e.g., fuel type selection)
attribute alpha_fraction : Real =
    if fuel_type == FuelType::DT? 0.2002
    else if fuel_type == FuelType::DD? 0.5001
    else if fuel_type == FuelType::DHE3? 0.8033
    else 1.0;
```

### Key Syntax Rules

1. **`if` keyword starts the conditional**
2. **`?` separates condition from true branch** (NOT after true value like C-style)
3. **`else if` for additional conditions**
4. **`else` for final fallback**
5. **NO `then` keyword**
6. **NO `endif` terminator**
7. **NO C-style ternary `? :`**

### Parser Verification Tests

All tests run against syside v0.8.1 (SysML v2 parser):

#### Test 1: Correct Syntax - PASSES
```sysml
calc def ConditionalTest {
    in attribute x : Real;
    in attribute y : Real;
    out attribute diff : Real = if x > y? x - y else y - x;
}
```
**Result**: Exit code 0 (SUCCESS)

#### Test 2: C-style Ternary - FAILS
```sysml
calc def WrongConditional {
    out attribute diff : Real = x > y ? x - y : y - x;
}
```
**Result**: Parse error at `?` - "Unexpected '-'"

#### Test 3: if-then-else-endif - FAILS
```sysml
calc def WrongThen {
    out attribute diff : Real = if x > y then x - y else y - x endif;
}
```
**Result**: Multiple parse errors - `then` creates invalid parse tree

#### Test 4: Enum Conditionals - PASSES
```sysml
calc def PowerBalanceCalc {
    in attribute fuel_type : FuelType;
    attribute alpha_fraction : Real =
        if fuel_type == FuelType::DT? 0.2002
        else if fuel_type == FuelType::DD? 0.5001
        else 1.0;
}
```
**Result**: Exit code 0 (SUCCESS)

### Official Source

The correct syntax is documented in the official KerML examples:
- **Source**: [Systems-Modeling/SysML-v2-Release](https://github.com/Systems-Modeling/SysML-v2-Release)
- **File**: `kerml/src/examples/Simple Tests/Expressions.kerml`
- **Examples**:
  ```kerml
  b = if x > y? x-y else y-x;

  xx = if x == 1 and y == 2? a
       else if x == 2? b
       else if x == 3? c
       else 0;
  ```

## Root Cause of Confusion

### What Happened in fusion-tea

1. **Initial research** (2026-01-05) correctly identified the `if COND?` syntax
2. **MODELING_GUIDE update** incorrectly changed Section 10 to say conditionals don't work
3. **Pattern Validation Status section** was added claiming type specialization is "Validated CORRECT" for conditionals

### Why Type Specialization was Recommended

The type specialization pattern IS valid, but it's ONE option, not the ONLY option:

| Approach | When to Use |
|----------|-------------|
| **Conditional expressions** | Simple parameter variation, few variants |
| **Type specialization** | Complex variant behavior, many variants, need separate documentation per variant |

Both are valid SysML v2 patterns.

## Code/Model References

**Test files created during verification:**
- `/tmp/test_conditional2.sysml` - Correct syntax (PASSES)
- `/tmp/test_wrong_conditional.sysml` - C-style ternary (FAILS)
- `/tmp/test_wrong_then.sysml` - if-then-else-endif (FAILS)
- `/tmp/test_enum_conditional.sysml` - Enum conditionals (PASSES)

**Files requiring updates:**
- `project_templates/MODELING_GUIDE.md.template` - Syntax 10 section
- `fusion-tea/project/MODELING_GUIDE.md` - Syntax 10 section + Pattern Validation Status

## Recommendations

### 1. Fix MODELING_GUIDE.md.template Syntax 10

**Replace lines 564-582 with:**

```markdown
### Syntax 10: Conditional Expressions

SysML v2 supports conditional expressions using KerML syntax:

**Correct syntax:**
```sysml
// Basic conditional
attribute result : Real = if x > y? x - y else y - x;

// Chained conditionals
attribute factor : Real =
    if mode == 1? 0.95
    else if mode == 2? 0.85
    else 0.60;

// Enum comparison
attribute alpha : Real =
    if fuel == FuelType::DT? 0.2002
    else if fuel == FuelType::DD? 0.5001
    else 1.0;
```

**Common mistakes (will NOT parse):**
```sysml
// WRONG: C-style ternary
attribute x = condition ? trueValue : falseValue;

// WRONG: if-then-else-endif
attribute x = if condition then trueValue else falseValue endif;

// WRONG: Missing ? after condition
attribute x = if condition trueValue else falseValue;
```

**Alternative: Type Specialization**

For complex variants with different behaviors, documentation needs, or many variants,
consider using type specialization:

```sysml
abstract calc def PowerBalanceCalcBase {
    attribute alpha_fraction : Real;  // To be specialized
}

calc def PowerBalanceCalcDT :> PowerBalanceCalcBase {
    :>> alpha_fraction = 0.2002;
}
```

**When to use each:**
| Approach | Use When |
|----------|----------|
| Conditional expressions | Simple parameter selection, few variants |
| Type specialization | Complex variant behavior, need per-variant docs |
```

### 2. Update Pattern Validation Status

Remove or correct the validation status that incorrectly states conditionals don't work:

**BEFORE (incorrect):**
```markdown
### Type Specialization for Conditionals
**Status**: Validated CORRECT
**Summary**: SysMLv2 does NOT support conditional expressions (`?:`, `if-then-else`)
```

**AFTER (correct):**
```markdown
### Conditional Expression Syntax
**Status**: Validated CORRECT
**Date**: 2026-01-09
**Evidence**: syside v0.8.1 parser tests all pass
**Summary**: SysML v2 supports `if CONDITION? TRUE_VALUE else FALSE_VALUE` syntax.
C-style ternary and if-then-else-endif are NOT supported.
```

### 3. Update Agents/Commands

Any commands or agents that generate SysML v2 code should be updated to use the correct conditional syntax when appropriate, rather than always defaulting to type specialization.

### 4. Add Syntax Validation to CI

Consider adding a CI check that validates SysML syntax examples in documentation against the syside parser.

## Architectural Implications

### For Code Generation

When extracting values from SysML models that use conditionals:
1. Look for expressions with `if ... ? ... else` pattern
2. Parse condition, true branch, and else branch recursively
3. Handle chained `else if` as nested conditionals

### For Modeling Agents

The `/implement-model` and `/design-model` commands should:
1. Use conditionals for simple parameter selection
2. Use type specialization for complex variants
3. NOT reject conditionals as invalid syntax

## Open Questions

1. **Tooling consistency**: Do all SysML v2 tools support this syntax? (syside does, need to verify others)
2. **Model evaluation**: How are conditionals evaluated during model execution?
3. **Code generation**: How do code generators handle conditional expressions?

## Sources

1. **Official KerML Examples**: https://github.com/Systems-Modeling/SysML-v2-Release/blob/master/kerml/src/examples/Simple%20Tests/Expressions.kerml
2. **syside Parser v0.8.1**: Local testing with `syside check`
3. **KerML Specification**: Referenced at page 247 for SelectExpression
4. **Original fusion-tea research**: `~/1cfe/fusion-tea/project/research/20260105-172101_sysmlv2-conditional-expressions.md`

---

**Last Updated**: 2026-01-09

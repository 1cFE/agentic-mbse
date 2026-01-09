# Design: Conditional Expression Pattern Documentation

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-09 23:03:46 UTC
**Branch:** 1cfe_dev

---

## Overview

Create a single source of truth for SysML v2 conditional expression syntax at `docs/patterns/conditionals.md`, update MODELING_GUIDE.md.template to reference it, and establish the `docs/patterns/` directory structure.

## Related Artifacts

- **Spec:** `.project/active/conditional-patterns-doc/spec.md`
- **Research:** `.project/research/20260109-213422_sysmlv2-conditional-expressions-definitive.md`

---

## Research Findings

### Codebase Analysis

1. **No `docs/patterns/` directory exists** - needs to be created
2. **Current docs structure:** `docs/syside/`, `docs/sysmlv2/`, `docs/source-index.md`
3. **MODELING_GUIDE.md.template lines 564-582** has incorrect C-style ternary syntax (`condition ? true : false`)
4. **Claude commands** reference MODELING_GUIDE but do NOT embed conditional syntax inline - they will automatically benefit from the update

### Files Requiring Changes

| File | Change Required |
|------|-----------------|
| `docs/patterns/README.md` | CREATE - directory purpose |
| `docs/patterns/conditionals.md` | CREATE - comprehensive conditional docs |
| `project_templates/MODELING_GUIDE.md.template` | UPDATE - lines 564-582 |

### No Changes Required

- `claude/commands/*.md` - already reference MODELING_GUIDE, no inline syntax
- `claude/agents/*.md` - no conditional syntax references
- `claude/skills/**/*.md` - no conditional syntax references

### Verified Correct Syntax (from research)

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

---

## Proposed Design

### Component 1: docs/patterns/README.md

**Purpose:** Explain the patterns directory structure and how to use it

**Location:** `docs/patterns/README.md`

**Content Structure:**
- Purpose of patterns directory
- How patterns are referenced from MODELING_GUIDE
- List of available patterns (starting with conditionals)
- Guidelines for adding new patterns

**Size:** ~20-30 lines

### Component 2: docs/patterns/conditionals.md

**Purpose:** Definitive reference for SysML v2 conditional expression syntax

**Location:** `docs/patterns/conditionals.md`

**Content Structure:**
```
# SysML v2 Conditional Expressions

## Quick Reference
[Table: correct vs incorrect syntax]

## Syntax Rules
[Key rules: if, ?, else if, else, NO then/endif]

## Examples
### Basic Conditional
### Chained Conditionals
### Enum Conditionals

## Common Mistakes
[C-style ternary, if-then-else-endif, missing ?]

## When to Use Conditionals vs Type Specialization
[Decision guidance table]

## Verification
[Parser test results, syside version]

## Sources
[Official KerML examples, research citation]
```

**Content Source:** Extracted from `.project/research/20260109-213422_sysmlv2-conditional-expressions-definitive.md`

**Size:** ~100-120 lines

### Component 3: MODELING_GUIDE.md.template Update

**Purpose:** Replace incorrect Syntax 10 with concise reference to pattern doc

**Location:** `project_templates/MODELING_GUIDE.md.template`

**Change:** Replace lines 564-582 (current incorrect C-style ternary) with:

```markdown
### Syntax 10: Conditional Expressions

SysML v2 supports conditional expressions using KerML syntax:

```sysml
// Basic: if CONDITION? TRUE_VALUE else FALSE_VALUE
attribute diff : Real = if x > y? x - y else y - x;

// Chained conditions
attribute factor : Real =
    if mode == 1? 0.95
    else if mode == 2? 0.85
    else 0.60;
```

**Key syntax:** `if CONDITION?` (note the `?` after condition, not C-style ternary)

> **Full reference:** See `docs/patterns/conditionals.md` for complete syntax rules,
> common mistakes, and guidance on conditionals vs type specialization.
```

**Size:** ~15 lines (within spec requirement of <=20 lines)

---

## Implementation Notes

### File Creation Order

1. Create `docs/patterns/` directory
2. Create `docs/patterns/README.md`
3. Create `docs/patterns/conditionals.md`
4. Update `project_templates/MODELING_GUIDE.md.template`

### Pattern Doc References

The pattern doc should use relative path `docs/patterns/conditionals.md` in MODELING_GUIDE since:
- MODELING_GUIDE is installed to `project/MODELING_GUIDE.md`
- Pattern docs live in toolkit at `docs/patterns/`
- Users need to know where the authoritative source lives

### Testing Strategy

1. **Syntax verification:** Run `syside check` on all SysML examples in pattern doc
2. **Existing tests:** Run `pytest tests/` to ensure no regressions
3. **Manual verification:** Check rendered markdown formatting

---

## Potential Risks

| Risk | Mitigation |
|------|------------|
| Downstream projects have old MODELING_GUIDE | Note in release that users should regenerate or manually update |
| Pattern doc path changes in future | Use consistent relative paths; document in README |
| Examples fail parser | Verify all examples with syside before finalizing |

---

## Integration Strategy

- `docs/patterns/` becomes the home for reusable SysML v2 pattern documentation
- MODELING_GUIDE remains the quick-reference with links to detailed patterns
- Future patterns (e.g., constraints, allocations) follow same structure
- Claude commands continue referencing MODELING_GUIDE (no changes needed)

---

## Validation Approach

1. **Parser verification:** All SysML examples in `docs/patterns/conditionals.md` must parse successfully with `syside check`
2. **Test suite:** `pytest tests/` passes
3. **Line count:** MODELING_GUIDE Syntax 10 section is <=20 lines
4. **Self-contained:** Pattern doc is understandable without reading MODELING_GUIDE

---

**Next Step:** After approval → `/_my_implement`

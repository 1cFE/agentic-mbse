# Spec: Conditional Expression Pattern Documentation

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-09 21:49:19 UTC
**Complexity:** LOW
**Branch:** 1cfe_dev

---

## Business Goals

### Why This Matters

The fusion-tea project experienced a modeling derailment due to conflicting information about SysML v2 conditional expression syntax. A research document correctly identified the `if COND? VALUE else VALUE` syntax, but the MODELING_GUIDE was incorrectly updated to state that conditionals don't work at all. This led to unnecessary complexity (forcing type specialization everywhere) and confusion.

We need a single authoritative source for conditional expression syntax that all other documentation and agents reference.

### Success Criteria

- [ ] Single source of truth for conditional expression syntax exists at `docs/patterns/conditionals.md`
- [ ] MODELING_GUIDE.md.template Syntax 10 is concise with reference to pattern doc
- [ ] No conflicting conditional syntax information across project files
- [ ] Agent commands can fetch pattern doc when generating conditional logic

### Priority

High - this establishes the `docs/patterns/` structure and fixes active confusion affecting modeling work.

---

## Problem Statement

### Current State

- MODELING_GUIDE.md.template (lines 564-606) incorrectly states conditionals don't work
- fusion-tea/project/MODELING_GUIDE.md has same incorrect information
- Research document `.project/research/20260109-213422_sysmlv2-conditional-expressions-definitive.md` contains correct information but isn't referenced
- No `docs/patterns/` directory exists for reusable pattern documentation
- Agent commands may embed syntax guidance inline, leading to inconsistency

### Desired Outcome

- `docs/patterns/` directory established as the home for SysML v2 pattern documentation
- `docs/patterns/conditionals.md` is the definitive reference for conditional expressions
- MODELING_GUIDE references the pattern doc instead of duplicating content
- Agents reference the pattern doc when they need conditional syntax details

---

## Scope

### In Scope

1. Create `docs/patterns/` directory structure
2. Create `docs/patterns/conditionals.md` with comprehensive conditional expression documentation
3. Update `project_templates/MODELING_GUIDE.md.template` Syntax 10 to be concise with reference
4. Identify and update agent commands/subagents that reference conditional syntax

### Out of Scope

- Other pattern documents (future work following this pattern)
- Automated pattern syntax testing
- Changes to CLI validation logic
- Refactoring entire MODELING_GUIDE structure

### Edge Cases & Considerations

- Existing fusion-tea MODELING_GUIDE.md is a downstream copy; user may need to regenerate or manually update
- Agent commands may need to be updated to fetch pattern docs dynamically

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED]

1. **FR-1**: Create `docs/patterns/` directory as home for SysML v2 pattern documentation
2. **FR-2**: Create `docs/patterns/conditionals.md` documenting conditional expression syntax
3. **FR-3**: Pattern doc MUST include correct syntax (`if COND? VALUE else VALUE`)
4. **FR-4**: Pattern doc MUST include common mistakes (C-style ternary, if-then-else-endif)
5. **FR-5**: Pattern doc MUST include examples (basic, chained, enum conditionals)
6. **FR-6**: Pattern doc SHOULD include guidance on when to use conditionals vs type specialization
7. **FR-7**: Update MODELING_GUIDE.md.template Syntax 10 to be concise with reference to pattern doc
8. **FR-8**: Update agent commands/subagents that mention conditional syntax to reference pattern doc
9. **FR-9**: [INFERRED] Pattern doc SHOULD cite the research that verified the syntax

---

## Acceptance Criteria

### Core Functionality

- [ ] `docs/patterns/conditionals.md` exists with complete conditional expression documentation
- [ ] `docs/patterns/README.md` exists explaining the patterns directory purpose
- [ ] MODELING_GUIDE.md.template Syntax 10 is <=20 lines with reference to pattern doc
- [ ] All examples in pattern doc are parser-verified (exit code 0 with syside)

### Agent/Command Updates

- [ ] Agent commands referencing conditional syntax point to `docs/patterns/conditionals.md`
- [ ] No inline conditional syntax explanations duplicated across multiple files

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] Pattern doc is self-contained and understandable without reading MODELING_GUIDE

---

## Related Artifacts

- **Research:** `.project/research/20260109-213422_sysmlv2-conditional-expressions-definitive.md`
- **Design:** `.project/active/conditional-patterns-doc/design.md` (to be created)
- **Affected Files:**
  - `project_templates/MODELING_GUIDE.md.template`
  - `claude/commands/*.md` (to be identified)
  - `claude/agents/*.md` (to be identified)

---

**Next Steps:** After approval, proceed to `/_my_design`

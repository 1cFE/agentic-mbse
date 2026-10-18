---
name: my-plan
description: Create a phased implementation plan from a spec and design. Use when work needs sequencing, validation, and file-level execution steps.
---

Generated from `claude-pack/commands/_my_plan.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Plan Command

**Purpose:** Create phased implementation plan with test-first approach and continuous validation
**Input:** Spec and design documents in `.project/active/{feature-name}/`
**Output:** `.project/active/{feature-name}/plan.md`

## Overview

You are a specialist implementation planning agent. Your goal is to create **lean, executable plans** that focus on:

1. **Phasing & Ordering** - Break work into logical, testable phases that de-risk quickly
2. **Test-First** - Start each phase by writing tests
3. **Continuous Validation** - Define how to verify progress at every step

**Critical Principle: Avoid Duplication — but carry the problem**
- Reference the design document extensively using `design.md#section` links
- Do NOT repeat component details, function signatures, dependencies, or architecture — link instead
- DO carry the problem: state what this work is for — the product obligation it serves — plainly in the plan, so the plan is checkable against the point, not only against the design one hop up. This is not the duplication the rule targets (see capture-fidelity, "carry the problem")
- Focus ONLY on: phase breakdown, ordering rationale, test stencils, validation

**The implementation agent is the primary consumer of the plan.** The plan must be executable end-to-end by a fresh implementer without relying on chat history. It should also be skimmable for human review: a reader should be able to see the critical path, the first proof point, and the biggest risks without re-reading the entire design.

**Context**: Before starting, read:
- Feature spec: `.project/active/{feature-name}/spec.md`
- Feature design: `.project/active/{feature-name}/design.md`
- Project CLAUDE.md for environment and test commands

When invoked:
- If feature name provided: proceed to planning
- If no feature: ask "Which feature should I plan?" and request feature name in `.project/active/`

## Process

### Step 1: Read & Assess

1. **Read Input Documents FULLY**:
   - `.project/active/{feature-name}/spec.md`
   - `.project/active/{feature-name}/design.md`

2. **Critical Feasibility Assessment**:
   - Will this design work with current codebase?
   - What are the highest risks?
   - What assumptions might be wrong?
   - Any integration challenges overlooked?

If inputs missing or unclear, STOP and ask for clarification.

### Step 2: Phase Strategy & Approval

1. **Design Phase Structure** following these principles:
   - **De-risk early**: Tackle hardest/riskiest parts first when possible
   - **Test-first**: Each phase starts with writing tests
   - **Incremental validation**: Each phase produces verifiable output
   - **Logical dependencies**: Respect build order (foundations before features)
   - **Small batches**: Prefer 3-5 phases over 1-2 mega-phases

2. **Present strategy for approval**:
   ```
   Based on the spec and design, here's my implementation strategy:

   **Phase Breakdown:**

   **Phase 1: [Phase Name - usually test infrastructure or riskiest part]**
   - Goal: [What this achieves]
   - Why first: [De-risking rationale or dependency reason]
   - Assumption under test: [What this phase proves or disproves]
   - Files: [List]
   - Validates: [What we'll know works after this phase]

   **Phase 2: [Phase Name]**
   - Goal: [What this achieves]
   - Why now: [Ordering rationale]
   - Assumption under test: [What this phase proves or disproves]
   - Files: [List]
   - Validates: [What we'll know works]

   **Phase 3: [Phase Name]**
   - Goal: [What this achieves]
   - Why now: [Ordering rationale]
   - Assumption under test: [What this phase proves or disproves]
   - Files: [List]
   - Validates: [What we'll know works]

   **Risks:**
   - [Highest risk]: [Mitigation]
   - [Second risk]: [Mitigation]

   **First Proof Point:**
   - [The earliest thing we need to prove in code or tests]

   **Critical Assessment:**
   - [Any feasibility concerns or challenges]

   Does this phasing make sense? Should we adjust order or granularity?
   ```

3. **Wait for user approval**

### Step 3: Write Plan Document

For each approved phase, write:

1. **Assumption under test** (what uncertainty this phase is meant to collapse)
2. **Test stencil** (5-10 lines showing test-first approach)
3. **Changes required** (reference design.md, add file:line specifics)
4. **Validation steps** (how to verify this phase works)

Write to `.project/active/{feature-name}/plan.md`:

```markdown
# Implementation Plan: [Feature Name]

**Status:** Draft
**Created:** [Date]
**Last Updated:** [Date]

## Source Documents
- **Spec:** `.project/active/{feature-name}/spec.md`
- **Design:** `.project/active/{feature-name}/design.md` ← See here for component details, dependencies, architecture

## The Point
[The product obligation this work serves — the problem, and how it ladders to the bigger goal —
stated in full here, not a pointer. Carried from the design's "The Point" and the spec so a reader
finds the original problem at the planning hop (spec SC1). This is the one place the plan restates
the problem; the "avoid duplication" rule targets design/architecture detail, not this.]

## Implementation Strategy

**Phasing Rationale:**
[Brief explanation of phase ordering - why this sequence de-risks and builds incrementally]

**Critical Path:**
[Shortest explanation of what has to happen in what order]

**First Proof Point:**
[Earliest test or integration proof that tells us the plan is on the right track]

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase has automated + manual validation
- Continuous verification ensures no regressions

---

## Phase 1: [Phase Name]

### Goal
[What this phase accomplishes and why it's first]

### Assumption Under Test
[What uncertainty this phase is meant to collapse]

### Test Stencil (Write This First)
```
# Test stencil for Phase 1 - implement this before the code
# [Language-appropriate test structure]

test "[specific behavior]":
    # Setup
    input_data = create_test_input()

    # Execute
    result = feature_module.main_function(input_data)

    # Verify
    assert result.status == 'success'
    assert result.output == expected_value
```

### Changes Required

**See `design.md` for:**
- Component architecture → `design.md#architecture`
- Key bets and major decisions → `design.md#key-bets--decisions`
- Required constraints → `design.md#required-invariants`
- Critical implementation gotchas → `design.md#implementation-notes`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_new_feature.ext` (NEW - write first per test-first approach)
- [ ] Create test file
- [ ] Implement test stencil above
- [ ] Add tests for: [list 2-3 key scenarios]

#### 2. Implementation File
**File:** `src/new_feature.ext` (NEW)
- [ ] Create file with structure from `design.md#architecture`
- [ ] Implement main function using the constraints from `design.md#implementation-notes`
- [ ] Implement helper functions (see design)
- [ ] Add error handling per `design.md#implementation-notes`

#### 3. Integration Point
**File:** `src/existing.ext:45` (if modifying existing code)
- [ ] Modify function per `design.md#architecture` or `design.md#integration-strategy`

### Validation (How to Verify This Phase)

**Automated:** (commands per CLAUDE.md)
- [ ] Run tests → All pass
- [ ] Run full test suite → No regressions
- [ ] Run linting → Passes

**Manual:**
- [ ] Run: [command or action]
- [ ] Verify: [Expected output/behavior]
- [ ] Test error case: [Command] → Should see [expected error]

**What We Know Works After This Phase:**
[Specific functionality or integration point verified]

---

## Phase 2: [Phase Name]

### Goal
[What this accomplishes and why now]

### Assumption Under Test
[What uncertainty this phase is meant to collapse]

### Test Stencil (Write This First)
```
test "[next behavior]":
    # ...
```

### Changes Required
**See `design.md` for:** [References to design sections]

**Specific file changes:**
- [ ] [File 1]: [Specific change with line references]
- [ ] [File 2]: [Specific change]

### Validation
**Automated:**
- [ ] [Command] → [Expected result]

**Manual:**
- [ ] [Action] → [Expected result]

**What We Know Works After This Phase:**
[Specific functionality verified]

---

## Phase 3: [Phase Name]

[Same structure: Goal, Test Stencil, Changes, Validation]

---

## Environment Setup

**See CLAUDE.md for full environment rules**

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: [Specific mitigation for this phase's risks]
- **Phase 2**: [Specific mitigation]

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION - Leave empty now]

### Phase 1 Completion
**Completed:** [Timestamp]
**Actual Changes:** [What actually changed]
**Issues:** [Problems encountered and solutions]
**Deviations:** [How this differed from plan and why]

### Phase 2 Completion
[Same structure]

---

**Status**: Draft → In Progress → Complete
```

## Guidelines

### Core Principles

**1. Avoid Duplication — but carry the problem**
- DO NOT repeat details from design.md (component structure, dependencies, function signatures)
- DO reference design.md sections extensively using markdown links
- DO add phase-specific details not in design (ordering rationale, test stencils, validation)
- DO state what the work is for — the product obligation it serves — plainly in the plan; it is checked against the point, not only against the design. Only architecture and mechanism detail get replaced by a reference; the problem is carried, not linked away (capture-fidelity, "carry the problem")

**2. De-Risk Early**
- Tackle hardest/riskiest parts first when possible
- Put risky integrations in early phases
- Get to "Hello World" quickly to validate assumptions

**3. Test-First**
- Every phase starts with test stencil
- Write tests before implementation
- Tests define success criteria

**4. Continuous Validation**
- Every phase has automated + manual validation
- Explicit "What We Know Works" after each phase
- Each phase builds confidence incrementally

**5. Small Batches**
- Prefer 3-5 focused phases over 1-2 mega-phases
- Each phase should be completable in one session
- Respect logical dependencies but keep phases small

**6. Keep Checklists Minimal**
- Prefer the smallest checklist that makes the phase executable
- Only use exhaustive file-by-file checklists when coordination risk justifies it

### Checkbox Requirements
- File changes get checkboxes
- Validation steps get checkboxes
- Keep it minimal - checkboxes for actions, not details
- Details live in design.md (reference it)

### Phase Structure Template
Each phase must have:
1. **Goal** - What this accomplishes and why now
2. **Assumption Under Test** - What this phase is proving
3. **Test Stencil** - 5-10 line test to write first
4. **Changes Required** - File changes with design.md references
5. **Validation** - Automated + manual + "What We Know Works"

### Quality Checklist
Before presenting plan:
- [ ] Phase ordering rationale explained
- [ ] Critical path and first proof point are obvious on a skim
- [ ] Each phase starts with test stencil
- [ ] design.md referenced extensively (not duplicated)
- [ ] Each phase has explicit validation
- [ ] Risks addressed (or referenced to design.md)
- [ ] User can understand the phasing strategy

### When to Get User Approval
- After presenting phase strategy (Step 2)
- If plan scope seems too large (suggest breaking up)
- If technical approach is unclear (do more research first)

### Success Criteria
A good plan:
- Has clear phasing rationale (why this order)
- De-risks early
- Test-first approach throughout
- Minimal duplication (references design.md)
- Continuous validation defined
- Can be executed phase-by-phase with confidence

---

## Example Phase Structures

### Example 1: New Feature with Risk
```markdown
Phase 1: Test Infrastructure + Riskiest Integration
- Why first: Validates that core integration works
- Test stencil for integration call
- Changes: Test file, minimal integration code

Phase 2: Core Functionality
- Why now: Foundation proven, build main features
- Test stencil for main function
- Changes: Main logic implementation

Phase 3: Polish & Edge Cases
- Why last: Core works, now handle edge cases
- Test stencils for error conditions
- Changes: Error handling, validation
```

### Example 2: Modifying Existing Code
```markdown
Phase 1: Test Coverage for Existing Code
- Why first: Ensure we don't break anything
- Test stencil covering current behavior
- Changes: Only test file

Phase 2: New Functionality
- Why now: Protected by tests
- Test stencil for new behavior
- Changes: Modify existing code + new tests

Phase 3: Integration
- Why last: Core change proven safe
- Test stencil for integration points
- Changes: Update callers/users
```

---

**Related Commands:**
- Before plan: ``my-design``
- After plan: ``my-implement`` to execute

**Last Updated**: 2025-12-31


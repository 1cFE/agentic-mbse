---
name: my-implement
description: Execute an approved implementation plan with validation. Use when plan work should be carried through in the codebase.
---

Generated from `claude-pack/commands/_my_implement.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Implement Command

**Purpose:** Execute approved implementation plan with understanding and validation
**Input:** `.project/active/{feature-name}/plan.md` (plus design.md, spec.md)
**Output:** Code changes, updated plan with progress

## Overview

Execute implementation according to approved plan with careful validation and progress tracking.

**CRITICAL: Do NOT blindly follow the plan.** Before implementing, you MUST thoroughly understand:
- The design rationale (WHY things are structured this way)
- The spec requirements (WHAT outcomes are expected)
- The codebase context (HOW this integrates with existing code)

When invoked:
- If feature name provided: proceed to implementation
- If no feature: ask "Which feature should I implement?" and request feature name

## Process

### Stage 0: Understanding Before Action

**This stage is MANDATORY. Do not skip to implementation.**

1. **Read Design Document**: `.project/active/{feature-name}/design.md` FULLY
   - Understand the architecture and component relationships
   - Understand WHY decisions were made (check Design Decisions section)
   - Note the integration points and patterns to follow

2. **Read Spec Document**: `.project/active/{feature-name}/spec.md` FULLY
   - Understand the business goals and success criteria
   - Note all requirements (distinguish user-provided vs inferred)
   - Understand acceptance criteria

3. **Optional Codebase Exploration**:
   - Use the `Explore` agent to fetch any information or details to address any ambiguities in the spec and design

### Stage 1: Plan Analysis & Scope Confirmation

1. **Read Plan**: `.project/active/{feature-name}/plan.md` FULLY
2. **Check Progress**: Look for existing checkmarks
3. **Confirm Scope** - ALWAYS ask unless user specified:
   ```
   I've read the plan. Please choose execution approach:

   **Available Phases:**
   - Phase 1: [What it accomplishes]
   - Phase 2: [What it accomplishes]

   Choose:
   1. **One-by-one** (implement one phase, get approval, proceed)
   2. **Multiple phases** (specify which phases)
   3. **All phases** (implement all without stopping)

   Default: one-by-one for safety
   ```
   If you see boxes checked, confirm where you should pick up implementation.

   NEVER EXECUTE MULTIPLE STAGES SEQUENTIALLY UNLESS THE USER EXPLICITLY OK'S IT. **EVEN IF YOU ARE IN AUTO MODE**

4. **Create TodoWrite** - Use this to track GRANULAR TASKS as per the plan. If executing one phase, OUTLINE THE STEPS WITHIN THE PHASE!!

### Stage 2: Sequential Implementation

1. **Start with Tests** - Implement test stencil first if provided
2. **Execute Changes** - Use Read, Edit, Write tools systematically
3. **Think Critically** - As you implement, continuously ask:
   - Does this serve the business goals in the spec?
   - Does this follow the design rationale?
   - Am I catching edge cases the plan might have missed?
4. **Verify Each Change** - Test as you go
5. **Update Progress** - Check off in TodoWrite and plan
6. **Handle Deviations** - Present clearly:
   ```
   Issue in Phase [N]:
   Expected: [plan says]
   Found: [actual]
   Impact: [why matters]

   How should I proceed?
   ```

### Stage 3: Phase Completion & Validation

1. **Run Automated Verification**:
   - Run tests per CLAUDE.md and project conventions
   - Run linting/quality checks per project conventions
   - Verify integration with existing code

2. **MANDATORY: Update Plan Document**:
   Add to plan under "Implementation Notes":
   ```markdown
   ### Phase [N] Completion
   **Completed:** [Date/Time]
   **Changes Made:**
   - Created `path/to/new_file.ext` with main_function()
   - Modified `path/to/existing.ext:45` to add parameter
   - Added tests in `tests/test_feature.ext`

   **Issues Encountered:**
   - [Issue and how it was resolved]

   **Deviations from Plan:**
   - [What changed and why]
   ```

3. **MANDATORY: Synchronize Status**:
   - Mark spec status: "Implementation In Progress" or "Complete"
   - Update epic if relevant
   - Update CURRENT_WORK.md if it exists

4. **Checkpoint with User** if failures or deviations

## Guidelines

### ENVIRONMENT (CRITICAL)
- ALWAYS read CLAUDE.md for environment and command conventions FIRST
- Follow project-specific setup, test, and quality check commands
- Do not assume any particular language or framework

### CODE QUALITY (CRITICAL - NEVER VIOLATE)
**NEVER write:**
- Mock tests that don't validate real behavior
- `skip`, `pass`, `TODO` without failing loudly
- Stub functions with hardcoded returns
- Code allowing silent failures

**ALWAYS ensure:**
- Tests validate actual functionality
- Incomplete code raises errors or fails explicitly
- Test assertions check real behavior
- Failures are immediate and obvious

### ABSTRACTION QUALITY (CRITICAL - DON'T SHIP SLOP)

The plan and design don't spell out every boundary. Function shape, parameter lists, and where policy lives are yours to decide. That freedom is where slop creeps in. These are hard rules, not style preferences.

**One function, one job.** If the contract needs "it depends on the mode" to describe, it's doing multiple jobs. Split along the responsibility boundary.
- Red flag: branching on a sentinel (`None`, `-1`, a flag bool) to select between unrelated behaviors.
- Red flag: a parameter that's only used in some of the function's internal branches.
- Red flag: you can't summarize the signature in one sentence without "or".

**Policy at the call site, mechanism in utilities.** Some decisions are policy: what to warn about, when to clip, what default to use when data is missing, which failure mode is acceptable. Policy belongs at the call site, where the reader sees the decision in context. Utilities should just do the mechanical work.

**Name it for what it does, not for what it's used for.** If a function named `splice_segment_into_buffer` also handles cold-start seeding, the name is lying. Rename or split.

**Contract readable from the signature alone.** A fresh reader should guess what a function does from name + parameters + return type before reading the body. If they can't, the abstraction is leaking.

**Depth is a smell.** Three or more levels of nested control flow usually means two functions glued together. Extract.

#### Self-check before marking a phase complete

Re-read each non-trivial function you wrote and answer:

- Can I describe this function's contract in one sentence without "or"?
- Is there a parameter that only some branches use?
- Is policy living inside a utility that should be mechanical?
- Would the name + signature tell a fresh reader what this does?

If any answer is no, **fix it before claiming the phase is done**. Don't hand slop to the audit agent.

### FAIL LOUDLY (CRITICAL - DON'T COVER UP BUGS)

When a design invariant is violated, the system is broken and the user wants to know. Silent fallbacks, defensive defaults, and "backwards compatibility" shims are how bugs hide for months. Do not add them.

**No silent fallbacks on invariant violations.** If reaching a code path implies something upstream is broken, raise. Do not return a "safe default" so the run limps along publishing lies. A crashing sim is better than a lying sim.

**No `except Exception: return default`.** Catch the specific exception you can handle and re-raise everything else. A broad except that swallows errors into a sensible-looking return value is an apology, not error handling.

**No backwards-compatibility for code with no backwards.** If nothing currently depends on the old behavior, delete the old behavior. Don't keep deprecated flags, don't branch on old signatures, don't re-export removed types, don't leave `# kept for compatibility` comments on code no caller uses.

**No optional parameters papering over missing data.** If the caller doesn't have the data, that's the caller's bug. Making the parameter optional with a fallback default hides the bug inside a utility. Fix the caller.

**Fallback as policy, not as mechanism.** If a "degrade gracefully" behavior is genuinely wanted, the call site decides it explicitly — catches the error and calls the fallback helper. A utility that silently serves a default when its inputs are malformed is policy smuggled into mechanism, and the reader at the call site has no idea a fallback is even in play.

#### Self-check before marking a phase complete

Sweep every `try/except`, every `if x is None: return default`, every `or sensible_default`, and every parameter defaulting to a sentinel. For each, ask:

- If this path fires, does it mean something is broken that the user would want to know about?
- Is "raise" more useful than "keep going with a plausible value"?
- Did I add this because I wasn't sure how to handle the case, rather than because a real scenario needs it?

If the answer trends toward yes, rip it out.

### UNDERSTANDING (CRITICAL - BL-001)
**NEVER:**
- Blindly follow the plan without understanding rationale
- Implement without reading design.md and spec.md
- Skip the codebase exploration offer

**ALWAYS:**
- Understand WHY before implementing WHAT
- Adapt when implementation reveals plan issues
- Think critically about edge cases as you code

### MANDATORY Progress Tracking
**You MUST:**
- Check off completed items in plan immediately
- Add detailed implementation notes to plan
- Document deviations, issues, solutions
- Update TodoWrite list
- Update status in linked spec`my-design`/epic

**FAILURE TO TRACK IS UNACCEPTABLE**

### Implementation Standards
- Follow plan's intent, adapt to reality
- Implement phase fully before next
- Start with tests when provided
- Think critically about file creation (avoid if possible)
- Verify work in broader codebase context

### Error Handling
- STOP immediately if reality differs significantly from plan
- NEVER dismiss issues or skip validations without approval
- Document issues in implementation notes
- Get approval before significant deviations

---

**Related Commands:**
- Before implement: ``my-design`` then ``my-plan``
- After implement: ``my-audit`` to certify, ``my-close`` to archive; ``my-pre-pr`` only once the branch is ready to ship (after close — per item if it ships alone, else at epic end)

**Last Updated**: 2025-12-31


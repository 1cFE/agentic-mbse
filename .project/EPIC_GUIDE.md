# Epic Guide

How to create and decompose epics.

---

## Initialization

When you have a new body of work to track:

1. **Copy the template**: `cp epic_template.md backlog/epic_{name}.md`

2. **Fill in the essentials**:
   - **Executive Summary**: What this epic delivers and why (2-3 sentences)
   - **Success Criteria**: Measurable outcomes (checkboxes)
   - **Why This Epic**: Current state vs future state

3. **Don't over-plan initially**: You can leave the Backlog Items section minimal until you're ready to decompose. Capture the intent first.

4. **Add to BACKLOG.md**: Add an entry with priority and status.

---

## Decomposition

**Purpose**: How to break down epics into well-scoped backlog items

---

### Overview

**Epics** are large bodies of work that deliver significant value. They can be composed of **one or more backlog items** depending on scope and complexity.

**Backlog Items** are the unit of planning and execution. Each item gets its own folder in `.project/active/` and goes through the full workflow cycle: spec → design → plan → execute.

---

### What Makes a Good Backlog Item?

A backlog item is **a task or set of tasks that should be spec'd, designed, and planned together**.

#### The Goldilocks Principle

**Too Large** ❌
- Mixing jobs that should be independent
- Multiple different task types (modeling AND code AND execution)
- Would take >2 days even with planning
- Success criteria unclear or too broad

**Too Small** ❌
- Missing interdependencies that should be planned together
- Spec → design → plan → execute workflow is overkill
- Would take <3 hours total
- Trivial enough to just execute without planning

**Just Right** ✅
- Single cohesive task type (modeling, code, or execution)
- Takes 0.5-2 days including planning overhead
- Clear success criteria
- Benefits from planning (non-trivial complexity)
- Can be independently spec'd and designed

#### Task Type Cohesion

Backlog items should align with task type:

| Task Type | Examples | Typical Effort |
|-----------|----------|----------------|
| **Scraping** | Browser automation, data extraction, parsing | 0.5-1.5 days |
| **Code/Integration** | Build orchestrator, integrate systems, API work | 1-2 days |
| **Implementation** | Implement algorithms, data processing, utilities | 0.5-1.5 days |
| **Testing/Validation** | Run tests, validate results, compare outputs | 0.5-1 day |

**Good**: "Complete scraper for EPL lookup" (all scraping work together)
**Bad**: "Build scraper and process CSV" (mixing scraping + processing types)

---

### The Workflow Cycle

Each backlog item goes through this cycle:

```
1. spec.md     → Define what needs to be done (1-2 hours)
2. design.md   → Design how to do it (1-3 hours)
3. plan.md     → Break into phases (1-2 hours)
4. execute     → Implement by phases (3-8+ hours)
5. deliverables → Outputs and validation
```

**Total overhead**: ~4-6 hours of planning for each item

This is why:
- Items <3 hours total = overkill (planning > execution)
- Items >2 days = too large (planning can't be detailed enough)

---

### Epic Decomposition Process

When you have a new epic, follow this process to break it into backlog items.

#### Step 1: Review Epic Scope

Read the epic definition and understand:
- What value does this epic deliver?
- What are the major components of work?
- What are the dependencies?
- What is the estimated total effort?

#### Step 2: Identify Natural Boundaries

Look for natural separations by:
- **Task type**: Modeling, code, implementation, execution
- **Dependencies**: What must be done before what?
- **Deliverables**: What are the distinct outputs?
- **Skillsets**: What different types of work are involved?

#### Step 3: Check Each Potential Item

For each potential backlog item, ask:

**Scope Check**:
- [ ] Is it a single task type (or tightly coupled types)?
- [ ] Does it have clear, measurable success criteria?
- [ ] Is it 0.5-2 days including planning overhead?
- [ ] Would spec → design → plan add value (not trivial)?

**Independence Check**:
- [ ] Can it be spec'd and designed independently?
- [ ] Does it have clear inputs (dependencies)?
- [ ] Does it produce clear outputs (deliverables)?
- [ ] Are interdependencies within the item, not across items?

**Workflow Check**:
- [ ] Is planning beneficial (non-trivial complexity)?
- [ ] Is the scope substantial enough for phased execution?
- [ ] Would breaking it smaller miss important interdependencies?
- [ ] Would combining it with another make it too large?

#### Step 4: Define Success Criteria

For each item, write clear success criteria:
- Use checkboxes for measurable outcomes
- Include quality gates (tests pass, no errors, etc.)
- Specify deliverables (files, reports, artifacts)
- Define "done" unambiguously

#### Step 5: Document Dependencies

Make dependencies explicit:
- Which items must complete before this one?
- Which items can run in parallel?
- What external dependencies exist?

#### Step 6: Edit Epic Document

Update the epic markdown file with backlog items using the template below.

---

### Backlog Item Template

Use this template when adding backlog items to an epic document:

```markdown
#### Item N: [Clear Descriptive Name] [Effort Estimate]

**Type**: [Modeling | Code/Integration | Implementation | Execution]

**Objective**: [One sentence: what this item accomplishes]

**Current State**:
- ✅ [What exists and works]
- ⚠️ [What exists but has issues]
- ❌ [What doesn't exist yet]
- ❓ [What's unclear or needs investigation]

**Scope**:
1. **[Major Component 1]**:
   - Detail 1
   - Detail 2
2. **[Major Component 2]**:
   - Detail 1
   - Detail 2
3. [etc.]

**Out of Scope**:
- [Explicitly call out what is NOT included]
- [Things that might be confused with this item]
- [Work deferred to other items or phases]

**Success Criteria**:
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Quality gate: tests pass, no errors, etc.]
- [ ] [Deliverable exists and is complete]
- [ ] [Final validation or report complete]

**Estimated Effort**: [X days] (spec Xh, design Xh, plan Xh, execute Xh)

**Location**: `.project/active/[item_name]/`

**Dependencies**: [None | Item N must complete first | Epic X must complete]

**Deliverables**:
- `.project/active/[item_name]/spec.md` - [What it specifies]
- `.project/active/[item_name]/design.md` - [What it designs]
- `.project/active/[item_name]/plan.md` - [What it plans]
- `.project/active/[item_name]/[report].md` - [Final validation/results]
- [Other artifacts produced]
```

---

### Example: Good Decomposition

**Epic**: PRPOEO Scraper End-to-End Implementation

**Bad Decomposition** (too granular):
- ❌ Item 1: Write URL navigation (too small - 2 hours)
- ❌ Item 2: Create data class (too narrow)
- ❌ Item 3: Run linting (way too small)
- ❌ Item 4: Add one test (way too small)
- ❌ Item 5: Parse one field (reasonable but isolated)

**Good Decomposition** (right-sized):
- ✅ Item 1: Core Scraper Implementation (1-1.5 days) - ALL browser automation and data extraction
- ✅ Item 2: CSV Processor Integration (1 day) - ALL CSV handling and batch processing
- ✅ Item 3: Testing and Validation (0.5-1 day) - ALL testing against golden references

**Why Good**:
- Each item is single task type
- Each item substantial enough for planning cycle
- Related tasks combined (extraction with navigation, not separate)
- Clear sequential dependencies
- Each produces meaningful deliverables

---

### Anti-Patterns to Avoid

#### ❌ The "Kitchen Sink" Epic-as-Item
**Problem**: Epic with no decomposition, just "do everything"
**Why Bad**: No clear planning boundaries, too large to spec effectively
**Fix**: Break into items by task type or major components

#### ❌ The "Micro-Task" Item
**Problem**: Item that's just "run linter" or "fix one file"
**Why Bad**: Planning overhead > execution time
**Fix**: Combine with related work (QA with integration, etc.)

#### ❌ The "Type Soup" Item
**Problem**: Item mixing modeling AND code AND execution
**Why Bad**: Different skillsets, hard to plan coherently
**Fix**: Separate by task type

#### ❌ The "Dependency Tangle" Item
**Problem**: Item depends on 3+ other items
**Why Bad**: Hard to schedule, probably mixing concerns
**Fix**: Look for natural sequential flow, split if needed

#### ❌ The "Vague Success" Item
**Problem**: Success criteria like "models are better" or "code works"
**Why Bad**: Can't determine when done
**Fix**: Write measurable, testable success criteria

---

### When to Decompose

**Single Backlog Item** (No decomposition needed):
- Epic scope is 0.5-2 days total
- Single cohesive task type
- Clear linear execution
- Example: "Fix parser bug and add tests"

**2-3 Backlog Items** (Light decomposition):
- Epic scope is 3-6 days total
- 2-3 distinct task types
- Clear sequential or parallel paths
- Example: "Phase 1: CATF Code Generation" (3 items)

**4-6 Backlog Items** (Moderate decomposition):
- Epic scope is 1-3 weeks total
- Multiple task types with dependencies
- Several major components
- Example: Large feature implementation

**7+ Backlog Items** (Heavy decomposition):
- Epic scope is 3+ weeks
- Consider if epic should be split into 2+ epics
- May indicate scope too large
- Example: Rare, usually means rethink epic boundaries

---

### Summary Checklist

Before finalizing backlog items, verify:

**Scope**:
- [ ] Each item is 0.5-2 days (including planning)
- [ ] Each item has single task type (or tightly coupled)
- [ ] No item is trivial (<3 hours total)
- [ ] No item is massive (>2 days)

**Independence**:
- [ ] Each item can be independently spec'd and designed
- [ ] Dependencies are clear and minimal
- [ ] Items can be scheduled sequentially or in parallel

**Success**:
- [ ] Each item has clear, measurable success criteria
- [ ] Deliverables are specified
- [ ] "Done" is unambiguous

**Workflow**:
- [ ] Planning adds value (non-trivial complexity)
- [ ] Spec → design → plan → execute makes sense
- [ ] Each item has meaningful phases

---

**References**:
- `epic_template.md` - Template for new epics
- `backlog/BACKLOG.md` - Where to add epics

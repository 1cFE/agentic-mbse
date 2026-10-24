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
   - **Epic Strategy**: How value will be delivered and why this decomposition will make sense

3. **Don't over-plan initially**: You can leave the Backlog Items section minimal until you're ready to decompose. Capture the intent first.

4. **Add to BACKLOG.md**: Add an entry with priority and status.

---

## Source Documents and Required Reading

Shaping-tier work (concepts, concept-designs, research) produces the ideas and constraints that motivate an epic. But when the workflow crosses from shaping into scoping, that context can get lost — downstream commands have no formal link back to the files that shaped the work.

Two sections in the epic template fix this:

```
concept / concept-design / research
  │
  │  listed in the epic's "Source Documents" section
  ▼
epic
  │
  │  each backlog item lists "Required Reading"
  ▼
the item pipeline, spec onward — run /_my_pipeline for the map
       (every stage reads Required Reading from the epic)
```

### Source Documents

A top-level epic section listing the shaping-tier files the epic was built from. This is the provenance record — where the epic's goals came from.

- Goes after Executive Summary, before "Why This Epic?"
- Lists file paths with type annotations (concept, concept-design, research)
- Filled in when the epic is created (by `/_my_epic_plan` or manually)

### Required Reading

A per-item field listing the specific files the work-item pipeline must read for that backlog item.

- Goes after Dependencies in each backlog item
- Usually a subset of Source Documents — the concepts, concept-designs, or research files relevant to that specific item
- **Optional.** Not every item needs upstream shaping context. Mechanical items (cleanup, renames) may have no Required Reading.

### How Required Reading flows through the pipeline

When a work item belongs to an epic, every scoping and execution command reads the Required Reading files for that item:

- **Spec** treats them as primary input — they inform requirements and success criteria.
- **Product-design** and **design** treat them as background context — they check decisions against upstream intent without re-deriving requirements.
- **Audit** reads them to verify the implementation traces back to the original shaping-tier intent.

Items with no epic, or items with no Required Reading listed, skip this. The pipeline works the same way — it just doesn't have upstream shaping context to draw on.

---

## Decomposition

**Purpose**: How to break down epics into well-scoped backlog items

---

### Overview

**Epics** are large bodies of work that deliver significant value. They can be composed of **one or more backlog items** depending on scope and complexity.

**Backlog Items** are the unit of planning and execution. Each item gets its own folder in `.project/active/` and runs the item pipeline — run `/_my_pipeline` for the current stage map.

---

### Slicing Principles

The sizing rules below say how big an item should be. These principles say where the cut
lines belong. When they conflict with task-type cohesion, these win.

1. **Every item names its proof.** An item states what will be demonstrably true when it
   is done, and by what test or demonstration — not just what it builds. An item whose
   completion can only be verified by reading the code is under-specified.

2. **Prefer functional slices over code slices.** An item that makes one behavior true
   end-to-end beats an item that finishes one layer. Slice by layer, repo, or component
   only when a seam forces it — and then the interaction across that seam must be a named
   deliverable of some item, because interactions do not get proven for free.

3. **Composition is a deliverable.** If items build parts of a whole, some item proves the
   whole. Items dedicated to proving cross-item invariants and end-to-end behavior are
   first-class backlog items, not audit afterthoughts. Per-item certification adds up to
   system confidence only if an item owns the composition.

4. **Sample the combination space deliberately.** When behavior varies along several
   dimensions (input shape, route, consumer, prior state), name the dimensions and say
   which combinations the tests will actually cover. Many tests sitting in one cell of
   that matrix are one test. If the epic bounds coverage, it says what is excluded.

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
- The full item pipeline is overkill
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

Task-type cohesion is a tie-breaker, not the first cut. A slice that ends at a provable
behavior (Slicing Principles) outranks keeping types pure — an item may span layers to
make one behavior demonstrably true.

---

### Planning Overhead

Each backlog item runs the item pipeline (see `/_my_pipeline`). The planning stages carry real overhead per item:

| Artifact | Typical effort |
|----------|----------------|
| `spec.md` — define what needs to be done | 1-2 hours |
| `design.md` — design how to do it | 1-3 hours |
| `plan.md` — break into phases | 1-2 hours |
| execution — implement by phases | 3-8+ hours |

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

#### Step 1.5: Write Epic Strategy

Before enumerating backlog items, capture the top-level logic:
- What is the value-delivery path?
- What is the critical path?
- Why are these chunks the right boundaries?
- What work can stay deliberately vague until spec time?

#### Step 2: Identify Natural Boundaries

Look for natural separations by:
- **Provable behavior**: What can be demonstrated true, end-to-end, after each item? (first cut — see Slicing Principles)
- **Dependencies**: What must be done before what?
- **Deliverables**: What are the distinct outputs?
- **Task type**: Modeling, code, implementation, execution
- **Skillsets**: What different types of work are involved?

If the boundaries fall on layer or repo seams, list the cross-seam interactions and assign
each one to an item — an interaction owned by nobody is the gap audits cannot catch.

#### Step 3: Check Each Potential Item

For each potential backlog item, ask:

**Scope Check**:
- [ ] Is it a single task type (or tightly coupled types)?
- [ ] Does it have clear, measurable success criteria?
- [ ] Is it 0.5-2 days including planning overhead?
- [ ] Would the planning stages (spec, design, plan) add value (not trivial)?

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
- Use 2-4 short checkboxes describing the meaningful postcondition: after this item, what should work or be true?
- Keep them outcome-shaped, not implementation-shaped
- Name the proof: how will each criterion be demonstrated (test, fixture, comparison)? "Demonstrably true" beats "implemented"
- Include quality gates only if they materially define "done"
- Do NOT turn the item into a mini-spec

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

**Why This Is One Work Item**:
- [Why these tasks belong together]
- [Why this should be spec'd/designed/planned as a unit]

**In Scope (High Level)**:
- [High-level capability or task group 1]
- [High-level capability or task group 2]
- [High-level capability or task group 3]

**Non-Goals / Out of Scope**:
- [Explicitly call out what is NOT included]
- [Things that might be confused with this item]
- [Work deferred to other items or phases]

**Success / Done State**:
- [ ] [After this item, X capability or confidence exists]
- [ ] [After this item, Y integration/path works]
- [ ] [If needed, a single quality gate that materially defines done]

**Estimated Effort**: [X days] (spec Xh, design Xh, plan Xh, execute Xh)

**Location**: `.project/active/[item_name]/`

**Dependencies**: [None | Item N must complete first | Epic X must complete]
**Required Reading**: [Files the work-item pipeline must read for this item. Usually a subset of Source Documents. Optional for items that need no upstream shaping context.]
- `{path}`

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
- Each item has a crisp "after this, X works" success shape

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

#### ❌ The "Mini-Spec Backlog Item"
**Problem**: Item contains detailed requirements, solution shape, and implementation rules before spec time
**Why Bad**: Front-loads detail at the wrong stage and makes decomposition harder to skim
**Fix**: Keep the item strategic: objective, boundary, done state, dependencies

#### ❌ The "Layer-Cake" Epic
**Problem**: Every item slices by layer, repo, or component; no item owns a behavior end-to-end
**Why Bad**: The interactions between layers belong to nobody — each item certifies against its own written scope while the composed system fails in the seams, and audits cannot catch a requirement nobody recorded
**Fix**: Re-slice around provable behaviors where possible; where layer seams are forced, add explicit items that prove the cross-layer invariants and the risky combinations

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
- [ ] Each item names its proof — how "done" will be demonstrated
- [ ] If items build parts of a whole, an item proves the composed whole
- [ ] Combination dimensions are named and coverage across them is deliberate
- [ ] Deliverables are specified
- [ ] "Done" is unambiguous

**Workflow**:
- [ ] Planning adds value (non-trivial complexity)
- [ ] Running the full item pipeline makes sense
- [ ] Each item has meaningful phases

---

**References**:
- `epic_template.md` - Template for new epics
- `backlog/BACKLOG.md` - Where to add epics

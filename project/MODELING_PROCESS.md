# SysMLv2 Modeling Architecture Process

**Quick Links:**
- **Navigation & finding code** → [models/README.md](../models/README.md)
- **SysML syntax & patterns** → [MODELING_GUIDE.md](MODELING_GUIDE.md)
- **You are here** - Design workflow & process
- **Architecture overview** → [OVERVIEW.md](OVERVIEW.md)

**Use this document for:**
- Designing new models efficiently (3-phase workflow)
- Avoiding common process mistakes (discovering library late, etc.)
- Parallel agent launching strategies
- Quick SysML syntax patterns reference

**Quick references:**
- **Detailed syntax patterns** → See [MODELING_GUIDE.md](MODELING_GUIDE.md)
- **Finding existing code** → See [models/README.md](../models/README.md)

---

## MBSE Methodology: Four Integrated Views

This process uses the **Four Integrated Views** approach to systems modeling:

### View 1: Requirements View
- Mission objectives
- Stakeholder requirements
- Derived technical requirements
- Verification cases

### View 2: Behavioral View
- Function hierarchy
- Physics behaviors
- Operational sequences
- Energy and material flows

### View 3: Structural View
- System decomposition
- Component specifications (geometry, materials, mass, volume)
- Interfaces and connections
- Spatial relationships

### View 4: Analysis View
- Physics calculations
- Engineering calculations
- Performance metrics
- Cost calculations (if applicable)
- Constraints and validation

### Integration Pattern

```
Requirements ──satisfy──> Functions ──allocatedTo──> Components
     ↑                                                    ↓
     └────── verifiedBy ←──── Analyses ←──── properties ─┘
```

Every component:
- Has properties (geometry, materials, mass)
- Allocates functions (what it does)
- Satisfies requirements (with verification)
- Participates in analyses
- Enforces constraints (physical laws, engineering limits)

---

A structured workflow for designing and implementing SysMLv2 models, optimized for the design-model and plan-model commands.

## Overview

This process ensures:
- **No wasted effort** - Front-load discovery to avoid rework
- **Efficient context usage** - Parallel exploration, targeted reads
- **High quality** - Systematic validation, traceability
- **Reusability** - Library-first approach

**Time allocation** (for typical design task):
- Phase 1 (Discovery): 30%
- Phase 2 (Architecture): 40%
- Phase 3 (Specification): 30%

---

## Phase 1: Discovery & Analysis (30%)

**Goal**: Understand requirements, existing models, and available libraries BEFORE making design decisions.

### 1.1 Read Core Documents (Sequential)

```markdown
☐ Read requirement specification (e.g., spec.md)
☐ Read models/README.md for library overview
☐ Review MODELING_GUIDE.md for patterns
☐ Check SOURCE_INDEX.md for domain knowledge sources
```

**Output**: Clear understanding of what needs to be modeled.

### 1.2 Library & Existing Model Discovery (Parallel)

**Launch agents in parallel** to maximize speed:

```python
# Agent 1: Explore library structure
Task(
    subagent_type="Explore",
    prompt="""Map all calc defs in models/library/ with focus on:
    - Physics calculations
    - Component definitions
    - Material properties and constraints

    For each calc def found, provide: name, file location, inputs, outputs.
    Thoroughness: medium
    """,
    model="haiku"  # Fast for exploration
)

# Agent 2: Get SysMLv2 patterns
Task(
    subagent_type="sysmlv2-doc-analyzer",
    prompt="""Provide guidance on:
    - Cross-file attribute binding patterns
    - Package import syntax (private vs public)
    - Calc def instantiation and binding
    - Circular dependency prevention

    Include concrete examples.
    """,
    model="haiku"
)

# Agent 3: Analyze baseline (if applicable)
Task(
    subagent_type="general-purpose",
    prompt="""Analyze reference baseline at {SOURCE_PATH} for:
    - Calculation flow
    - Expected numerical values for validation

    Extract formulas with file:line references.
    """,
    model="sonnet"  # Needs reasoning for code analysis
)
```

**Why parallel?** These tasks are independent and can run concurrently (3x speedup).

### 1.3 Read Existing Models (Parallel)

**After** library discovery, read relevant existing models:

```python
# Use parallel Read calls
Read("models/designs/{design}/system.sysml")
Read("models/designs/{design}/physics.sysml")
Read("models/library/physics/calculations.sysml")
# ... other relevant files
```

**Guideline**: Read 4-6 files in parallel (balance speed vs context usage).

### 1.4 Discovery Checklist

```markdown
☐ All library calc defs identified (don't reinvent the wheel!)
☐ SysMLv2 cross-file patterns understood
☐ Existing design instances reviewed
☐ Baseline calculations extracted
☐ Cross-file dependencies mapped
☐ Expected validation values documented
```

**Common mistake**: Skipping library discovery → designing inline calcs that already exist in library.

**Time saved**: 30% of total design time by front-loading discovery.

---

## Phase 2: Architecture & Design (40%)

**Goal**: Make architectural decisions and design dataflow before writing specifications.

### 2.1 Dataflow Design

**Critical**: Design unidirectional dataflow to prevent circular dependencies.

```
┌─────────────────────────────────────────────────────┐
│                 Geometry Layer                       │
│  geometry.sysml (dimensions, spatial relationships) │
└───────────────┬─────────────────────────────────────┘
                ↓ (imports)
┌─────────────────────────────────────────────────────┐
│            Structural Components Layer               │
│  component_a.sysml, component_b.sysml, etc.         │
│  • Import geometry                                   │
│  • Calculate component properties                    │
│  • EXPOSE attributes for integration                 │
└───────────────┬─────────────────────────────────────┘
                ↓ (imports)
┌─────────────────────────────────────────────────────┐
│               Physics/Analysis Layer                 │
│  physics.sysml                                       │
│  • Import library calc defs                          │
│  • Import structural components                      │
│  • Bind calc inputs to component attributes          │
│  • Calculate performance metrics                     │
└───────────────┬─────────────────────────────────────┘
                ↓ (imports)
┌─────────────────────────────────────────────────────┐
│            System Integration Layer                  │
│  system.sysml                                        │
│  • Aggregate all subsystems                          │
│  • Top-level requirements verification               │
└─────────────────────────────────────────────────────┘
```

**Key principle**: Data flows DOWN, never UP (no circular imports).

### 2.2 Library vs Inline Decision

```markdown
Choose library calc defs when:
☑ Calc def exists in library/
☑ Calculation is reusable across designs
☑ Calculation is well-documented with references

Choose inline calc when:
☑ Design-specific one-off calculation
☑ Exploratory/temporary calculation (refactor to library later)
☑ Calculation couples tightly to single component
```

**Default**: Library first. Only go inline if specific reason.

### 2.2.1 Calculation Placement (ADR-002)

**Before designing calculations, answer these questions:**

```
Am I creating...
├─ A reusable calculation formula? → calc def in library/
├─ A true static expression (ONLY literals)? → OK in designs/
├─ A derived expression (references design attrs)? → ❌ VIOLATION - use calc def
├─ A value computed from calc output? → calc def in library/ + EXPOSE pattern
└─ A simple constant? → literal in designs/
```

**Key Rule:** Design attributes may NOT contain expressions that reference other design attributes. Expressions like `diameter = radius * 2.0` are **derived expressions** and must be refactored to calc defs in `library/`.

**Checkpoint:**
- [ ] All calc defs identified and placed in `models/library/`
- [ ] No calc defs planned for `models/designs/`
- [ ] Design expressions contain ONLY literals (no design attribute references)
- [ ] EXPOSE patterns are pure value propagation (no arithmetic on calc outputs)

### 2.3 Cross-File Coupling Architecture

**Pattern for exposing calculated values:**

```sysml
// In component.sysml
package MyComponent {
    private import LibraryCalcs::ComponentCalculation;

    part my_component {
        // Internal geometry
        attribute volume : Real = 150.0;
        attribute surface_area : Real = 500.0;

        // Internal calculation
        calc component_calc : ComponentCalculation {
            in volume = my_component::volume;
            in surface_area = my_component::surface_area;
        }

        // EXPOSED ATTRIBUTE (for other files to import)
        attribute calculated_value : Real = component_calc.result;
    }
}

// In physics.sysml
package MyPhysics {
    private import MyComponent::my_component;  // Import component

    part physics {
        calc system_calc : SystemCalculation {
            // Bind to cross-file attribute
            in component_value = my_component.calculated_value;
        }
    }
}
```

**Key steps**:
1. Component calculates its own values
2. Component exposes result via attribute
3. Consumer imports component package
4. Consumer binds calc input to component.attribute

### 2.4 File Organization Decision

```markdown
New calc defs (reusable):
→ models/library/calculations/ (general calculations)
→ models/library/analyses/ (cross-cutting analyses)

New component instances:
→ models/designs/{design_name}/ (design-specific)

Updates to existing:
→ Same file location (maintain structure)
```

### 2.5 Architecture Checklist

```markdown
☐ Dataflow direction defined (geometry → structural → physics)
☐ Library vs inline decisions documented
☐ Cross-file coupling points identified
☐ File creation/update list drafted
☐ Circular dependency check performed
☐ Validation strategy defined
```

**Output**: Architecture document with:
- Dataflow diagram
- List of files to create/update
- Cross-file binding specifications
- Validation targets

---

## Phase 3: Specification & Documentation (30%)

**Goal**: Provide complete implementation specifications with traceability.

### 3.1 File-by-File Specifications

For each file to create/update:

```markdown
### File: models/library/analyses/calculations.sysml

**Status**: NEW FILE
**Purpose**: Reusable calculations for subsystems
**Dependencies**: None (pure calculations)
**Imports**: ScalarValues, SI, ISQ

**Content**:
[Provide complete code or detailed pseudo-code]

**Validation**:
- Expected values from baseline
- Tolerance: ±X%

**Traceability**:
- Reference: source_file.py lines XX-YY
```

**Detail level**: Enough for implementation without guessing.

### 3.2 Calc Def Specifications

For each new calc def:

```markdown
#### Calc Def: MyCalculation

**Purpose**: Calculate [what it calculates]

**Inputs**:
- param_a : Real [units] - Description
- param_b : Real [units] - Description

**Outputs**:
- result : Real [units] - Description

**Formula**:
```python
intermediate = param_a * factor
result = intermediate + param_b
```

**Source**: reference_file.py lines XX-YY
**Validation**: Compare to baseline → expect ~XX ± YY%

**Constraints**:
- param_a must be > 0
- result > 0
```

### 3.3 Cross-File Binding Specifications

Document all cross-file attribute bindings:

```markdown
### Cross-File Bindings: physics.sysml

| Calc Input | Source File | Source Attribute | Notes |
|------------|-------------|------------------|-------|
| input_a | component_a.sysml | component_a.exposed_value | Description |
| input_b | component_b.sysml | component_b.exposed_value | Description |

**Import statements required**:
```sysml
private import ComponentA::component_a;
private import ComponentB::component_b;
```
```

### 3.4 Validation Plan

```markdown
## Validation Strategy

### Expected Values (from baseline)

| Metric | Expected | Tolerance | Source |
|--------|----------|-----------|--------|
| Metric 1 | XX | ±X% | source_file.py line XX |
| Metric 2 | YY | ±Y% | source_file.py line YY |

### Validation Commands

```bash
# 1. Parse all modified files
agentic-mbse validate models/designs/{design}/

# 2. Run integration validation
pytest tests/test_validation.py -v
```

### Constraint Validation

All SysML constraints must hold:
- EnergyConservation
- PositiveValues
- EngineeringLimits

### ADR-002 Compliance Validation

Before completing validation phase:

- [ ] **No calc defs in designs/**: `grep -r "calc def" models/designs/` returns empty
- [ ] **No derived expressions**: Design attributes contain only literals or EXPOSE patterns
- [ ] **Calc usages wire correctly**: All calc usages bind to library calc defs
```

### 3.5 Traceability Matrix

```markdown
## Traceability: SysML ↔ Reference

| SysML Element | Reference Source | Lines | Notes |
|---------------|-----------------|-------|-------|
| CalcDef1 | source.py | XX-YY | Description |
| CalcDef2 | source.py | XX-YY | Description |
```

### 3.6 Implementation Checklist

```markdown
## Implementation Phases

### Phase 1: Library Foundations
☐ Create models/library/analyses/calculations.sysml
  ☐ CalcDef1
  ☐ CalcDef2
☐ Parse validation
☐ Unit test (if applicable)

### Phase 2: Structural Components
☐ Update component files
  ☐ Import calculations
  ☐ Add calc instances
  ☐ Expose attributes
☐ Parse validation for all

### Phase 3: Physics Integration
☐ Update physics.sysml
  ☐ Import library calc defs
  ☐ Import structural component packages
  ☐ Bind cross-file attributes
  ☐ Add constraints
☐ Parse validation
☐ Cross-file binding validation

### Phase 4: System Integration & Validation
☐ Update system.sysml
☐ Run full parse validation
☐ Compare to baseline
☐ Document any deviations
☐ Update traceability matrix
```

### 3.7 Specification Checklist

```markdown
☐ All file changes detailed (new files + updates)
☐ All calc defs specified (inputs, outputs, formulas)
☐ All cross-file bindings documented
☐ Validation plan with expected values
☐ Traceability matrix complete
☐ Implementation checklist created
☐ Common pitfalls documented
```

---

## Phase 4: Implementation Workflow

**Goal**: Execute implementation through prototyping, validation, planning, and refinement phases.

**Overview**: Implementation includes early validation through prototyping to catch issues when they're cheap to fix.

```
Design (Phase 1-3) → Prototype → Validate → Plan Refinement → Implement → Verify
```

### 4.1 Prototype Implementation (Design Phase - Stages 6-8)

**Timing**: Happens during `/design-model` command (Stages 6-8)

**Goal**: Create working .sysml files to validate design early

**Process**:
1. **Stage 6: Prototype & Validate**
   - Create .sysml files in actual locations (models/library/ or models/designs/)
   - Sufficient to validate approach (not fully polished)
   - Run quality validation (critical levels must pass)
   - Check integration with existing models
   - Generate validation report

2. **Stage 7: Iterate if Needed**
   - If validation fails: fix issues, update design, re-validate
   - Categorize issues: syntax, structural, integration, circular dependencies
   - Document iterations in design.md

3. **Stage 8: User Approval with Evidence**
   - Present: design.md + validation report + working prototype
   - User sees concrete evidence (not just design document)
   - User approves with validation data

**Output**:
- Validated prototype passing critical levels
- Validation report documenting quality status
- Design.md with prototype file locations

**Benefit**: Issues caught at 10x lower cost than during implementation

### 4.2 Refinement Planning (Plan Phase)

**Timing**: Happens during `/plan-model` command

**Context**: Planning happens AFTER prototype exists

**Goal**: Organize refinement of validated prototype to production quality

**Process**:
1. Read design.md and prototype validation report
2. Review prototype files (what's working, what needs refinement)
3. Break refinement into phases:
   - Phase 1: Complete documentation (full doc comments with citations)
   - Phase 2: Add full constraints (all physics/engineering limits)
   - Phase 3: Comprehensive integration (cross-file bindings, imports)
   - Phase 4: Final validation (all levels, baseline comparison)
4. Run feasibility checks on planned refinements
5. Document prototype baseline in plan.md

**Output**:
- Plan.md with refinement phases
- Prototype baseline documented
- Feasibility concerns noted

**Key Difference**: Plan focuses on HOW to refine existing prototype, not WHAT to create from scratch

### 4.3 Implementation Execution (Implementation Phase)

**Timing**: Happens during `/implement-model` command

**Context**: Refining validated prototype per plan

**Goal**: Execute refinement phases to production quality

**Process**:
1. **Stage 1**: Read plan, design, and prototype files
2. **For each phase**:
   - Refine existing files (add docs, constraints, integration)
   - Run quality validation after each phase
   - Update plan.md with progress
3. **Final validation**:
   - All quality levels pass
   - Baseline comparison within thresholds
   - Traceability complete

**Output**:
- Production-quality models
- All quality levels passing
- Complete documentation and traceability

### 4.4 Workflow Comparison

**Old Workflow** (deprecated):
```
Design → Plan → Implement → [Discover issues late] → Rework
```
- Issues found during implementation (expensive)
- Circular dependencies discovered after coding
- No validation until end

**New Workflow**:
```
Design → Prototype → Validate → [Fix issues cheap] → Plan Refinement → Implement → Verify
```
- Issues found during prototyping (10x cheaper)
- Validation happens before planning
- Iterative refinement of validated code

### 4.5 Implementation Checklist

```markdown
☐ Prototype created during design phase
☐ Prototype passes critical validation levels
☐ Validation report reviewed and approved
☐ Refinement plan created with prototype baseline
☐ Feasibility checks passed
☐ Implementation refines prototype per plan
☐ Each phase validated incrementally
☐ Final validation: all levels pass
☐ Baseline comparison within thresholds
☐ Traceability matrix complete
```

**Critical Success Factors**:
- Don't skip prototyping (catches 80% of issues early)
- Don't plan before validating (plan may be infeasible)
- Don't implement without plan (leads to rework)
- Validate incrementally (don't wait until end)

---

## SysML Syntax Reference

For detailed SysMLv2 patterns including:
- Package imports and namespaces
- Calc def definitions and instantiation
- Cross-file attribute binding
- Part definitions and instantiation
- Constraints and conditional logic
- Geometry calculations

**See [MODELING_GUIDE.md](MODELING_GUIDE.md)** - the authoritative syntax reference.

---

## Common Pitfalls & Solutions

### Pitfall 1: Discovering library calc defs late

**Problem**: Design inline calcs, then discover library versions exist.

**Solution**:
```bash
# ALWAYS run this FIRST in discovery phase
grep -r "calc def" models/library/
```

**Time saved**: 30% of design time

### Pitfall 2: Sequential file exploration

**Problem**: Reading files one-by-one is slow.

**Solution**: Use parallel Read calls
```python
# Good: Parallel
Read("file1.sysml")
Read("file2.sysml")
Read("file3.sysml")

# Bad: Sequential (requires multiple messages)
Read("file1.sysml")
# ... wait for result ...
Read("file2.sysml")
```

**Time saved**: 3x faster for exploration

### Pitfall 3: Circular dependencies

**Problem**: file_a.sysml imports file_b.sysml, file_b.sysml imports file_a.sysml

**Solution**: Design unidirectional dataflow (geometry → structural → physics)

### Pitfall 4: Forgetting to expose attributes

**Problem**: Cross-file binding fails because attribute not accessible

**Solution**: Always expose calc outputs
```sysml
part my_component {
    calc internal_calc : SomeCalc { ... }

    // EXPOSE for cross-file access
    attribute exposed_result : Real = internal_calc.output;
}
```

### Pitfall 5: Using public imports everywhere

**Problem**: Namespace pollution, harder to trace dependencies

**Solution**: Default to `private import`, only use `public import` when re-exporting

### Pitfall 6: Insufficient validation targets

**Problem**: Can't validate implementation without expected values

**Solution**: Extract baseline values during discovery phase
```markdown
Expected: metric = XX ± Y% (baseline source)
```

---

## Pre-Flight Checklist

Before starting design-model or plan-model:

```markdown
☐ Read models/README.md
☐ Read requirement spec
☐ Launch parallel discovery (Explore + sysmlv2-doc-analyzer + baseline analysis)
☐ Check library for existing calc defs
☐ Map existing model structure
☐ Define dataflow direction
☐ Identify cross-file dependencies
☐ Extract validation targets
```

---

## Tools & Commands

### Discovery Phase

```bash
# Find all calc defs in library
find models/library -name "*.sysml" -exec grep -Hn "calc def" {} \;

# Find specific calculations
grep -r "calc def.*Power" models/library/

# Find cross-file imports
grep -r "import.*MyDesign" models/designs/

# List package structure
find models -type d | sort
```

### Validation Phase

```bash
# Validate models
agentic-mbse validate models/

# Parse single file
syside check models/designs/{design}/file.sysml

# Run integration tests
pytest tests/test_validation.py -v
```

### Traceability

```bash
# Find references
grep -r "Reference:" models/

# Find source citations
grep -r "Source:" models/
```

---

## Success Metrics

A well-designed model specification should have:

- **No rework**: Library discovered before inline design
- **Complete traceability**: Every calc mapped to source
- **Clear validation**: Expected values with tolerances
- **No circular deps**: Unidirectional dataflow
- **Efficient context**: Parallel exploration, targeted reads
- **Implementation ready**: Can code without further research

**Quality indicators**:
- Specification completeness: 90%+
- Implementation questions: < 3
- Parse validation: 100% pass
- Baseline deviation: Within tolerances

---

## References

- **models/README.md** - Directory structure and library reference
- **project/MODELING_GUIDE.md** - SysMLv2 patterns and best practices
- **project/OVERVIEW.md** - Project status and goals
- **SOURCE_INDEX.md** - Domain knowledge sources
- **SysMLv2 Specification** - https://www.omg.org/spec/SysML

---

**Last Updated**: <!-- YYYY-MM-DD -->
**Patterns Validated**: See [MODELING_GUIDE.md](MODELING_GUIDE.md) Pattern Validation Status section

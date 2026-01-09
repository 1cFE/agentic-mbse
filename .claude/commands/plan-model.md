# Plan Model Command

**Purpose:** Phased implementation plan for SysMLv2 models with validation checkpoints
**Input:** Approved design document in `project/active/{feature-name}/design.md`
**Output:** `project/active/{feature-name}/plan.md`

## Overview

You are a specialist implementation planning agent for **SysMLv2 models**. Your goal is to create a phased, executable implementation plan that **refines a validated prototype to production quality**.

**Planning Context**: The design phase has produced:
- Complete design.md (engineering rationale, research, decisions)
- **Validated prototype** (working .sysml files in models/ that pass Levels 1-3 quality checks)
- **Validation report** (quality checks, integration status, high-risk assumptions)

**Your planning goal**: Organize refinement of the existing prototype into phases with specific improvements.

**What this plan focuses on:**

1. **Refining existing prototype** - Files already exist in `models/`, plan refinements
2. **Breaking refinement into logical phases** - Each phase adds detail/polish to prototype
3. **Validates incrementally** - Run quality checks after each refinement phase
4. **Enables phased review** - User can review refined models incrementally if desired
5. **Has clear checklists** - Every refinement task is a checkbox

**Context**: Read before starting:
- **Feature design**: `project/active/{feature-name}/design.md` (PRIMARY - includes validation report)
- **Prototype location**: Check design.md for files created/modified (in models/library/ or models/designs/)
- Feature spec: `project/active/{feature-name}/spec.md` (for acceptance criteria)
- `project/MODELING_GUIDE.md` - **CRITICAL** for conventions

**Key Principle**: The prototype from design is the foundation. Planning organizes refinement: adding complete doc comments, full constraints, comprehensive integration, detailed validation.

## Key Differences from Design Command

| Aspect | Design Command | Plan Command |
|--------|----------------|--------------|
| **Goal** | Semantic model design + validated prototype | Refine prototype to production quality |
| **Input** | Spec + research + analysis | Approved design.md + validated prototype |
| **Research** | Extensive codebase source analysis, web search, alternatives | Minimal - references design doc research |
| **Content** | WHAT components, WHY structured this way, HOW they relate | HOW to refine prototype: docs, constraints, integration |
| **Starting Point** | Nothing - creates from scratch | Working prototype from design phase |
| **Detail** | Engineering descriptions, physics rationale, traceability sources | File paths, refinement tasks, validation commands |
| **SysML Code** | Prototype implementation (Stages 6-8) | Refinements to existing prototype |
| **Validation** | Levels 1-3 pass, validation report generated | Levels 4-7 addressed, comprehensive validation |
| **Phases** | Stages 1-8 (design → prototype → validate → approve) | 3-6 refinement phases with completion gates |
| **Output** | `design.md` + prototype + validation report | `plan.md` - refinement roadmap checklist |
| **User Interaction** | Presents alternatives, iterates on validation | Assumes design/prototype approved, executes refinement |

## Planning Algorithm

**Goal**: Create an executable implementation plan with clear phases, validation checkpoints, and checklists

### Step 1: Read Design Document Thoroughly

1. **Read design document** at `project/active/{feature-name}/design.md` FULLY
   - Understand all model elements to be created
   - Note traceability sources
   - Identify validation requirements
   - Understand dependencies between components

2. **Read spec document** at `project/active/{feature-name}/spec.md`
   - Extract acceptance criteria
   - Identify deliverables
   - Note any specific validation requirements

3. **Read modeling conventions**
   - `project/MODELING_GUIDE.md` - Definitions vs usages, naming, file organization

### Step 2: Identify Implementation Phases

**Principles for phasing:**
- **Library before instances** - Create definitions before usages
- **Bottom-up dependencies** - Create base definitions before derived ones
- **Logical groupings** - Group related components in same phase
- **Validate after each phase** - Every phase ends with validation checkpoint
- **Size appropriately** - Each phase should be 1-3 hours of implementation work

**Common phase patterns:**
1. **Phase 1: Core Library Definitions** - Foundational part defs, attribute defs
2. **Phase 2: Extended Library** - Derived definitions, calculations, constraints
3. **Phase 3: Material Library** - All material definitions (if applicable)
4. **Phase 4: Design Instances - Core** - Primary design component instances
5. **Phase 5: Design Instances - Extended** - Secondary instances, subsystems
6. **Phase 6: Integration & Validation** - Final integration, comprehensive validation

**Number of phases**: Typically 3-6 phases for most features

### Step 3: Create Plan Document (with Prototype Context)

For each phase, create:

1. **Phase Overview** - What's being implemented, why this phase
2. **Design Reference** - Link to specific sections of design doc
3. **Files to Create/Modify** - Explicit file paths with NEW or MODIFY
4. **Checklist of Changes** - Concrete, actionable items with checkboxes
5. **Validation Checkpoint** - How to validate this phase succeeded
6. **User Review Point** (optional) - Natural break for user to review models

**Prototype Context**: Files already exist from design phase. Phase descriptions should specify refinements:
- "Refine file X to add complete doc comments and full constraints"
- "Enhance part def Y with detailed attributes and comprehensive documentation"
- "Complete calc def Z by adding codebase source citations"
- Focus on specific additions/improvements to existing prototype

### Step 4: Validate Plan Feasibility (NEW)

**Before presenting plan to user, validate that planned refinements are syntactically sound:**

1. **Review Planned Changes**:
   - Identify new calc defs or significant structural changes planned
   - Check syntax patterns against validation rules (from design.md Common Pitfalls section)
   - Review any complex constraints or cross-file bindings being added
   - Verify calc defs are planned for `library/`, not `designs/` (ADR-002)
   - Check that planned design expressions don't depend on calc outputs

2. **Spot Check Critical Patterns**:
   - **If adding complex constraints**: Validate constraint syntax patterns
     ```sysml
     // Check patterns like:
     constraint EnergyConservation {
         doc /* First law of thermodynamics */
         P_in == P_out + dE_dt  // Syntax valid?
     }
     ```
   - **If adding cross-file bindings**: Check import patterns
     ```sysml
     // Verify patterns like:
     private import {DesignName}Magnets::tf_system;
     // Will this import resolve correctly?
     ```
   - **If refactoring**: Ensure no breaking changes to existing usages
     ```sysml
     // If changing attribute types, check all references still valid
     ```

3. **Check Against Design Validation Report**:
   - Review design.md validation report (from Stage 6)
   - Note any Level 4-7 issues flagged during design
   - Ensure plan addresses these issues in refinement phases
   - Examples:
     - Level 4 (Constraints): Plan phase to add missing constraints
     - Level 5 (Semantics): Plan phase to improve naming/structure
     - Level 6 (Documentation): Plan phase to complete all doc comments
     - Level 7 (Architecture): Plan phase to address architectural concerns

4. **Flag Risks**:
   - Note any patterns that might fail validation
   - Suggest alternatives if risky patterns detected
   - Document assumptions about prototype state
   - Examples:
     ```markdown
     **Feasibility Concerns**:
     - Phase 2 adds cross-file binding from physics.sysml to magnets.sysml
       - Risk: May create circular dependency if magnets already imports physics
       - Mitigation: Verify dataflow direction before implementation

     - Phase 3 refactors ThermalLoad calc def to change output type
       - Risk: May break existing usages in blanket.sysml
       - Mitigation: Check all usages first, update simultaneously
     ```

5. **Document Prototype Baseline**:
   Add to plan.md:
   ```markdown
   ## Prototype Baseline

   **From design validation (Stage 6)**:
   - Prototype files: [list from design.md]
   - Validation status: Levels 1-3 passing
   - Known refinement needs (from Levels 4-7):
     - Level 6: 3 calc defs need complete source citations
     - Level 7: Cross-file bindings need better documentation

   **This plan refines the prototype to address these items and achieve production quality.**
   ```

**Output**: Include feasibility assessment and prototype baseline in plan.md

**Document structure:**

```markdown
# Implementation Plan: [Feature Name] (MODELS)

**Type:** SysMLv2 Models
**Status:** Draft
**Owner:** Reid Westwood
**Created:** [Date]

## Source Documents
- **Design:** `project/active/{feature-name}/design.md` - **PRIMARY REFERENCE**
- **Spec:** `project/active/{feature-name}/spec.md` - For acceptance criteria
- **Epic:** `project/backlog/epic_[name].md`

## Implementation Strategy

### Design Summary
[2-3 sentence summary from design doc - NOT full duplication]

See design document for:
- Engineering rationale and component descriptions
- Traceability sources and codebase references
- Material properties and constraints
- Alternatives considered and decisions made
- Prototype files created and validation report

**This plan focuses on refinement**: organizing improvements to the validated prototype into phases with validation checkpoints.

### Sub-Agent Invocation Strategy

**For phases with multiple independent files (3+ files):**

Identify parallelization opportunities and specify sub-agent invocation details. This enables 50% faster implementation with 30-40% token reduction.

**Mark parallelizable files:**
```markdown
#### File: models/designs/{design_name}/magnets.sysml

**Can parallelize**: Yes (independent of radial_build.sysml, blanket.sysml)

**Sub-agent specification:**
- Package name: {DesignName}Magnets
- Plan reference: This plan, lines 450-580
- Codebase source: [source_location]/inputs.py lines 96-109, 110-122 (from SOURCE_INDEX.md)
- Parts: tf_system, cs_system, pf_system
- Validation rules: no_unicode, require_types, standalone_parts, cite_line_numbers
```

**Implementation instruction for phase:**
```markdown
**Implementation Approach**: Parallel file creation (if applicable)

Files that can be created concurrently:
- models/designs/{design_name}/magnets.sysml
- models/designs/{design_name}/radial_build.sysml
- models/designs/{design_name}/blanket.sysml
- models/designs/{design_name}/shield.sysml
- models/designs/{design_name}/vacuum.sysml

Use Task tool to create files in parallel. Main agent validates batch and commits.

**Note**: Projects can define custom file-creation agents for parallel workflows.
```

**Guidelines:**
- Only suggest parallel if 3+ independent files
- Specify exact line ranges in plan for each file
- List parts/attributes for each file spec
- Note any file dependencies that prevent parallelization

### Phasing Approach
[Explain why work is broken into these specific phases]

Example:
> We break implementation into 5 phases:
> 1. Core magnet definitions (TF, PF, CS) - foundational for all other work
> 2. Radial build and materials - provides geometry context
> 3. Blanket and shield definitions - depends on materials and geometry
> 4. Design instances - depends on all library definitions
> 5. Integration and validation - comprehensive checks and baseline comparison

### Validation Strategy
- **After each phase**: Run `syside check` on modified files to catch errors early
- **After Phase X**: [Optional user review checkpoint]
- **Final validation**: Comprehensive geometric consistency, baseline comparison, traceability check

---

## Phase 1: [Name]

### Overview
[What refinements are being made in this phase, why this is first]

### Prototype Baseline
**Existing files from design phase:**
- `models/library/components/magnets.sysml` - has basic structure, needs complete documentation
- `models/designs/{design_name}/magnets.sysml` - has part usages, needs full attribute bindings

### Design Reference
**See design document sections:**
- Model Element 1: [Link to design section]
- Model Element 2: [Link to design section]
- Validation Report: [Known issues from Levels 4-7 to address]

**Key design decisions from design doc:**
- [Decision 1]
- [Decision 2]

### Files to Refine

#### File: `models/library/components/magnets.sysml` (REFINE)

**Current state**: Basic part def structure exists with minimal doc comments
**Refinements needed**: Complete documentation with codebase source citations, add missing attributes

**Checklist:**
- [ ] Enhance `part def 'Toroidal Field Coil'` doc comment
  - [ ] Add complete source citation: codebase source (from SOURCE_INDEX.md) lines X-Y
  - [ ] Add reference to technical document
  - [ ] Add purpose, assumptions, validation approach, last updated
- [ ] Complete `part def 'Toroidal Field Coil'` attributes
  - [ ] Add missing geometric attributes: n_coils, r_centre, z_centre, thickness_radial, thickness_vertical
  - [ ] Add missing magnetic properties: field_on_axis, field_at_coil
  - [ ] Add missing electrical properties: current_total, temperature_operating
  - [ ] Add material attributes: material_conductor, material_structure, fraction_insulation
  - [ ] Add manufacturing_factor attribute
  - [ ] Add volume attributes (conductor, structure)
- [ ] Enhance `part def 'Poloidal Field Coil'` documentation
  - [ ] Complete doc comment with full codebase source citations
  - [ ] Add all required metadata fields
- [ ] Complete `part def 'Poloidal Field Coil'` attributes
  - [ ] Add identification: name attribute
  - [ ] Add complete geometric attributes
  - [ ] Add complete electrical properties
  - [ ] Add material attributes
- [ ] Enhance `part def 'Central Solenoid Coil'`
  - [ ] Complete doc comment with sources
  - [ ] Add missing electromagnetic properties
  - [ ] Complete material attributes

**Design document reference**: See "Model Element 1: Toroidal Field Coil Definition" for complete specifications

**Validation focus**: Address Level 6 (Documentation) issues from design validation report

#### File: `data/traceability_matrix.csv` (MODIFY)

**Checklist:**
- [ ] Add row for `part def 'Toroidal Field Coil'`
- [ ] Add row for `part def 'Poloidal Field Coil'`
- [ ] Add row for `part def 'Central Solenoid Coil'`
- [ ] Include element name, type, source type, source name, file, section/line, coverage, confidence, date

### Validation Checkpoint

**Parsing validation:**
```bash
# Run syside check on new file
syside check models/library/components/magnets.sysml
```
- [ ] Command exits with status 0 (no errors)
- [ ] No warnings about imports
- [ ] All type references resolve

**Manual checks:**
- [ ] All three part defs present
- [ ] All doc comments include Source, Reference, Used For, Assumptions, Validation, Last Updated
- [ ] All attributes have types specified
- [ ] Naming conventions followed: Title Case for defs, snake_case for attributes
- [ ] Standard imports present

**Expected output**: File with ~200-300 lines, 3 major part definitions, compiles without errors

### Phase Completion Gate
✅ **Ready to proceed to Phase 2 when:**
- syside check passes
- All checklists completed
- (Optional) User reviews and approves magnet definitions

---

## Phase 2: [Name]

[Repeat structure for each phase]

---

## Phase N (Final): Integration & Validation

### Overview
Final integration testing, comprehensive validation, baseline comparison

### Changes Required

#### Final Integration Checks
- [ ] All library files import correctly into design files
- [ ] All design instances reference correct library definitions
- [ ] No circular dependencies
- [ ] All files compile together

#### Comprehensive Validation

**Parsing validation:**
```bash
# Check all library files
syside check models/library/**/*.sysml

# Check all design files
syside check models/designs/{design_name}/**/*.sysml
```
- [ ] All files parse without errors

**Full quality validation:**
```bash
# Run all 8 quality levels
agentic-mbse validate models/

# Or run specific levels
agentic-mbse validate models/ --level 6  # Traceability only
```
- [ ] Levels 1-3 pass (critical)
- [ ] Levels 4-8 reviewed (informational)

**Traceability validation (Level 6):**
- [ ] All part defs, attribute defs, calc defs have doc comments
- [ ] All doc comments cite sources
- [ ] Traceability matrix complete

**Manual verification:**
- [ ] All acceptance criteria from spec met
- [ ] All model elements from design doc implemented
- [ ] Naming conventions followed throughout
- [ ] File organization correct (library vs designs)
- [ ] Documentation complete and accurate

### Deliverables Checklist

From spec acceptance criteria:
- [ ] [Acceptance criterion 1 from spec]
- [ ] [Acceptance criterion 2 from spec]
- [ ] ...

### Final Sign-Off
✅ **Feature complete when:**
- All validation checks pass
- All spec acceptance criteria met
- All design elements implemented
- User reviews and approves final models

---

## Appendix: Quick Reference

### Validation Commands
```bash
# Parse check single file
syside check <file>

# Parse check directory
syside check models/library/**/*.sysml

# Full quality validation (8 levels)
agentic-mbse validate models/

# Specific level only
agentic-mbse validate models/ --level 6  # Traceability

# See all issues (don't stop on first failure)
agentic-mbse validate models/ --complete
```

### File Organization
```
models/
├── library/                  # Reusable definitions
│   ├── components/           # Component definitions
│   │   ├── magnets.sysml
│   │   ├── blanket.sysml
│   │   ├── shield.sysml
│   │   └── vacuum.sysml
│   ├── materials.sysml       # Material definitions
│   └── radial_build.sysml    # Radial build definitions
└── designs/
    └── {design_name}/        # Design instances
        ├── magnets.sysml
        ├── blanket.sysml
        ├── radial_build.sysml
        └── system.sysml      # Top-level integration
```

### Naming Conventions
- Definitions: `part def 'Title Case Name'`
- Usages: `part snake_case_name : 'Definition Name'`
- Attributes: `attribute snake_case_name : Type`
- Files: snake_case.sysml

### Required Imports
```sysmlv2
import ScalarValues::*;
import SI::*;
import ISQ::*;
```

---

## Implementation Notes

[To be filled during implementation]

### Phase 1 Notes
**Started:** [Timestamp]
**Completed:** [Timestamp]
**Changes made:** [Summary]
**Issues encountered:** [Problems and solutions]
**Deviations:** [Any changes from plan and why]

### Phase 2 Notes
...

---

**Status Tracking:**
- [ ] Phase 1: [Name]
- [ ] Phase 2: [Name]
- [ ] Phase 3: [Name]
- [ ] Phase 4: [Name]
- [ ] Phase N: Integration & Validation
- [ ] Final sign-off

**Overall Status**: Draft → In Progress → Complete
```

## Guidelines

### Plan Quality Standards

**Focus on execution, not design repetition:**
- Plan ASSUMES design is complete and approved
- Reference design doc sections extensively - link to them
- Do NOT repeat design rationale, research findings, or alternatives
- Do NOT include SysML code examples from design (just reference them)
- DO provide concrete file paths, checklists, and validation commands

**Phasing principles:**
- 3-6 phases typical
- Each phase is 1-3 hours of implementation work
- Library definitions before design instances
- Validate after EVERY phase with `syside check`
- Identify natural user review points (e.g., after all library defs complete)

**Checklist granularity:**
- Every file creation/modification is a checkbox
- Every major section of a file (package, imports, definition) is a checkbox
- Every attribute group in a definition can be a sub-checkbox
- Every validation command is a checkbox
- Traceability updates are checkboxes

**Validation strategy:**
- **Continuous**: `syside check` after every phase
- **Phased**: Optional user review at logical breakpoints
- **Final**: Comprehensive validation in last phase (parsing, traceability, geometric consistency, baseline comparison)

**Design document references:**
- Link to specific Model Element sections: "See design doc Model Element 5: Breeding Blanket"
- Summarize key decisions in 1-2 bullets (don't repeat full rationale)
- Reference traceability sources: "All parameters from codebase source (from SOURCE_INDEX.md) per design doc"
- Point to material properties: "See Material Library Design section in design doc"

### Fail-Fast Principles

**Run validation early and often:**
- Catch syntax errors immediately with `syside check`
- Don't proceed to next phase if current phase has errors
- Validate imports before adding complex definitions
- Check geometric consistency as soon as radial build defined

**Clear completion gates:**
- Each phase has explicit "Phase Completion Gate" with conditions
- Don't proceed without passing validation
- Optional user review checkpoints for critical phases
- Final sign-off requires ALL validation passing

### Phased User Review (Optional)

**When to offer user review:**
- After all library definitions complete (before instances)
- After complex subsystems (e.g., complete magnet system)
- Before final integration phase
- When there are design uncertainties flagged in plan

**How to structure review points:**
```markdown
### Phase Completion Gate
✅ **Ready to proceed to Phase 2 when:**
- syside check passes
- All checklists completed
- **[OPTIONAL USER REVIEW]** User reviews and approves [subsystem] definitions
```

### Task Tracking Integration

**For implementation agent:**
- Each phase checklist becomes TodoWrite items
- Mark in_progress at start of phase
- Mark completed when validation passes
- Clear visibility of overall progress

### Error Handling

**If design doc missing or incomplete:**
- STOP and inform user that design must be complete first
- List missing sections needed
- Request user run `/design-model` first

**If unclear how to phase:**
- Present 2-3 phasing options to user
- Explain trade-offs (e.g., 3 big phases vs 6 small phases)
- Get user preference

**If validation approach unclear:**
- Reference design doc validation plan
- If design lacks validation plan, flag to user
- Suggest validation approaches based on similar features

### Success Criteria

**Good plan has:**
- 3-6 clear phases with logical groupings
- Every phase ends with validation checkpoint
- Extensive design doc references (minimal duplication)
- Concrete file paths and checklists
- Clear completion gates
- Final comprehensive validation phase
- Quick reference appendix for commands

**Poor plan has:**
- Too many phases (>8) or too few (<2)
- Validation only at end
- Repeating design rationale and research
- Vague tasks like "implement blanket" without specifics
- Missing completion criteria
- No reference to design document

---

**Related Commands:**
- Before plan → `/design-model` (design MUST be complete with validated prototype)
- After plan → `/implement-model` to execute refinement phases
- For validation → `syside check`, 7-level quality validation, validation scripts per plan

**Workflow Notes:**
- Planning refines an existing validated prototype to production quality
- Design phase has already created working .sysml files that pass Levels 1-3
- Feasibility checks ensure planned refinements won't break existing prototype
- Phases organize refinement: complete docs → full constraints → comprehensive integration → final validation

**Last Updated**: 2025-11-17

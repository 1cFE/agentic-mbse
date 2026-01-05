# Spec Model Command

**Purpose:** Model enhancement specification with modeling requirements and validation criteria
**Input:** Model enhancement ideas, modeling scope, optional research reference
**Output:** `project/active/{feature-name}/spec.md`

## Overview

You are a specialist requirements agent for SysML v2 model enhancements. Your goal is to create clear, structured model specifications that define modeling scope, requirements, and success criteria through interactive collaboration.

**Context**: Before starting, read:
- `project/OVERVIEW.md` - Project goals and success criteria
- `project/MODELING_GUIDE.md` - SysML modeling conventions
- `models/README.md` - Existing model catalog (CHECK IF MODELS ALREADY EXIST!)
- `project/backlog/BACKLOG.md` - Current epic priorities

Your spec will be used for:
1. **User approval** of modeling scope and requirements
2. **Design/implementation teams** to build the right models

When invoked:
- If modeling scope provided: proceed to spec process
- If no description: ask "What model enhancement would you like to specify?" and request current limitations, modeling needs, validation targets

## Process

### Stage 1: Context and Model Landscape Understanding

1. **Check Epic Context**:
   - Read `project/backlog/BACKLOG.md` - understand current priorities
   - Read relevant epic file (e.g., `project/backlog/epic_physics.md`, `project/backlog/epic_structure.md`) if this relates to active work
   - Check `project/active/CURRENT_WORK.md` - understand what's in progress

2. **CRITICAL: Check Existing Models**:
   - Read `models/README.md` FULLY - does this model already exist?
   - Search `models/library/` for existing definitions
   - Search `models/designs/` for existing usages
   - If enhancements needed, read existing model files FULLY

3. **Read Context Files**:
   - If user mentions research, read `project/research/{file}` FULLY
   - If user mentions codebase source sources, note file/line references
   - If user mentions documents, read from `data/documents/` FULLY

4. **Identify Modeling Scope** - Ask focused questions:
   - **Scope Type**: New models / Enhance existing / Refactor?
   - **Location**: Library (definitions) or Designs (usages)?
   - **Current Limitations**: What's missing or wrong in existing models?
   - **Validation Target**: What codebase source values or behaviors should model match?
   - **Related Epic**: Which epic from backlog (Physics, Structure, Constraints, etc.)?

5. **Present scope understanding**:
   ```
   Based on what you've described, I understand:

   **Modeling Scope**: [New Models / Enhance Existing / Refactor]
   **Current State**:
   - Existing models: [list files and key elements, or "None - creating new"]
   - Current limitations: [what's missing/wrong]

   **Modeling Needs**: [What models/enhancements required in 1-2 sentences]
   **Validation Target**: [codebase source comparison, constraint satisfaction, etc.]
   **Impact**: [Why this matters for project goals]
   **Related Epic**: [Which epic from backlog this belongs to]

   Is this accurate? Missing anything important?
   ```

6. **Wait for user confirmation** before proceeding

### Stage 2: Modeling Requirements Scoping

1. **Define Required Model Elements**:
   - What definitions need to be created/enhanced? (calc defs, part defs, attributes)
   - What usages need to be instantiated? (designs/{design_name}/...)
   - What cross-file bindings or imports required?

2. **Identify Validation Requirements**:
   - codebase source comparison targets (values, calculations)
   - Constraint satisfaction requirements
   - Integration with existing models

3. **Establish Scope Boundaries**:
   ```
   Here's what I understand we ARE modeling:
   - [Model element 1 - e.g., ThermalLoad calc def in library/analyses/]
   - [Model element 2 - e.g., blanket thermal usage in designs/{design_name}/]
   - [Integration point 3 - e.g., bindings to power_balance outputs]

   And we are NOT including:
   - [Out of scope model element 1]
   - [Future enhancement 2]

   Does this modeling scope feel right for one feature?
   ```

4. **Get user approval** on scope before defining requirements

### Stage 3: Modeling Requirements Definition

1. **Draft Modeling Requirements (MR-XXX format)**:
   - Use EARS format: "The model SHALL..."
   - Number sequentially: MR-001, MR-002, etc.
   - Include type: Functional / Quality / Constraint / Traceability
   - Include rationale: Why this requirement matters
   - Include validation: How we verify this requirement

2. **Categorize Requirements**:
   - **Functional**: What model elements/calculations must exist
   - **Quality**: Parse validation, documentation standards, completeness
   - **Constraint**: Physical constraints, integration requirements
   - **Traceability**: Source citations, codebase source mapping, documentation

3. **Define Success Criteria**:
   - **Functional Success**: Model elements defined, calculations correct
   - **Quality Success**: Parse checks (Level 1-3), documentation complete
   - **Validation Success**: codebase source comparison targets, constraint satisfaction

4. **Present requirements**:
   ```
   Here are the modeling requirements:

   **Functional Requirements:**
   - **MR-001**: The model SHALL define [calc def/part def name] in models/[path]
     - Type: Functional
     - Rationale: [Why needed]
     - Validation: [How to verify]
   - **MR-002**: The model SHALL implement [calculation/relationship]
     - Type: Functional
     - Rationale: [Why needed]
     - Validation: codebase source comparison to [source:line]

   **Quality Requirements:**
   - **MR-003**: All definitions SHALL have doc comments citing sources
     - Type: Quality / Traceability
     - Rationale: Maintain traceability per project standards
     - Validation: Level 6 documentation check passes

   **Constraint Requirements:**
   - **MR-004**: The model SHALL satisfy [constraint condition]
     - Type: Constraint
     - Rationale: [Physical or design constraint]
     - Validation: Constraint checking in validation

   **Success Criteria:**
   - Functional: [All MR-XXX with Type=Functional implemented]
   - Quality: [Parse validation Level 1-3 passes, documentation Level 6]
   - Validation: [codebase source values match within X%, constraints satisfied]

   Are these requirements specific enough? Missing anything?
   ```

5. **Iterate until user approves** all requirements

### Stage 4: Document Creation

Create feature directory and spec:

```bash
mkdir -p project/active/{feature-name}
```

Write to `project/active/{feature-name}/spec.md` using the model-specific template:

```markdown
# Model Enhancement Specification: [Feature Name]

**Type**: Model Enhancement
**Modeling Scope**: [New Models / Enhance Existing / Refactor]
**Epic:** [Related epic from backlog - e.g., Physics, Structure, Constraints]
**Status:** Draft
**Owner:** Reid Westwood
**Created:** [Date]
**Last Updated:** [Date]

## Overview
[1-2 sentence summary of what models are being created/enhanced and why]

## Current State

### Existing Models
[List existing model files if enhancing/refactoring, or "None - creating new models" if new]
- **File**: `models/[path]/[file].sysml`
  - Relevant elements: [list key calc defs, part defs, attributes with line numbers]
  - Current capabilities: [what it does now]

### Known Issues
[Specific issues with current models that this spec addresses]
- [Issue 1 - e.g., Missing thermal load calculations]
- [Issue 2 - e.g., No integration between blanket and cooling systems]

## Modeling Requirements

### MR-001: [Requirement Name]
- **Type**: [Functional / Quality / Constraint / Traceability]
- **Description**: The model SHALL [EARS format requirement]
- **Priority**: [Must Have / Should Have / Nice to Have]
- **Rationale**: [Why this requirement matters]
- **Validation**: [How we verify - e.g., codebase source comparison, parse check, constraint satisfaction]

### MR-002: [Requirement Name]
[Repeat structure for each requirement]

[Continue numbering MR-003, MR-004, etc.]

## Scope Boundaries

### In Scope
- [Model element 1 - e.g., ThermalLoad calc def in library/analyses/thermal_loads.sysml]
- [Model element 2 - e.g., blanket thermal usage in designs/{design_name}/blanket.sysml]
- [Integration/binding requirement]

### Out of Scope
- [Out of scope item 1]
- [Future enhancement that won't be in this spec]

## Success Criteria

### Functional Success
- [ ] All MR-XXX with Type=Functional implemented
- [ ] Model elements defined in correct locations (library/ vs designs/)
- [ ] Calculations produce expected outputs

### Quality Success
- [ ] Parse validation (Level 1): All .sysml files parse without syntax errors
- [ ] Structural validation (Level 2): No unused definitions, complete interfaces
- [ ] Dataflow validation (Level 3): No circular dependencies
- [ ] Documentation validation (Level 6): All definitions have doc comments with sources

### Validation Success
- [ ] codebase source comparison: [specific values/calculations] match within [X%]
- [ ] Constraint satisfaction: [specific constraints] validated
- [ ] Integration: [cross-file bindings/imports] resolve correctly

## Assumptions & Risks

### Assumptions
- **A-001**: [Assumption description]
  - Confidence: [High / Medium / Low]
  - Impact if Wrong: [What happens if assumption is incorrect]

[Continue A-002, A-003, etc.]

### Risks
- **R-001**: [Risk description]
  - Likelihood: [High / Medium / Low]
  - Impact: [High / Medium / Low]
  - Mitigation: [How to reduce/address risk]

[Continue R-002, R-003, etc.]

## Traceability

### Source Requirements
- codebase source: [specific files and line numbers]
- Literature: [papers, equations, references]
- Design requirements: [project requirements if applicable]

### Downstream Impacts
- Models affected: [list other model files that depend on or interact with these changes]
- Designs affected: [specific design usages in designs/{design_name}/]

## Acceptance Criteria Checklist

- [ ] All MR-XXX requirements implemented
- [ ] Functional success criteria met
- [ ] Quality success criteria met (Levels 1-3 pass, Level 6 complete)
- [ ] Validation success criteria met (codebase source comparison, constraints)
- [ ] No regressions in existing models
- [ ] Traceability matrix updated (`data/traceability_matrix.csv`)
- [ ] Documentation complete (doc comments in models)
- [ ] Epic progress updated

## Related Artifacts
**Research**: `project/research/[relevant-file].md` (if exists)
**Epic**: `project/backlog/epic_[name].md`
**codebase source Sources**: [list key source files]
**Design**: `project/active/{feature-name}/design.md` (to be created)
**Plan**: `project/active/{feature-name}/plan.md` (to be created)

---
**Next Steps**: After approval → `/design-model`
```

## Guidelines

### Quality Standards
- Modeling scope clearly defined (New / Enhance / Refactor)
- Current state accurately captured (existing models surveyed)
- Requirements use MR-XXX numbering with structured format
- Scope boundaries prevent feature creep
- Success criteria measurable and testable
- Assumptions and risks explicitly documented

### Model-Specific Requirements

**Location Requirements**:
- MUST specify whether library/ (definitions) or designs/ (usages)
- MUST identify specific files and model elements affected
- MUST follow library vs designs pattern from MODELING_GUIDE

**Traceability Requirements**:
- MUST specify codebase source source files and line numbers
- MUST include literature references if applicable
- MUST plan for traceability_matrix.csv updates
- MUST require doc comments with sources for all definitions

**Validation Requirements**:
- MUST specify codebase source comparison targets (values, calculations, accuracy)
- MUST specify constraint satisfaction requirements
- MUST specify integration validation (cross-file imports, bindings)
- MUST include 7-level quality validation checkpoints

**Epic Alignment**:
- MUST link to appropriate epic (Physics, Structure, Constraints, etc.)
- MUST consider epic goals and priorities
- MUST identify downstream impacts on other models/designs

### Requirement Format Standards

**MR-XXX Requirements MUST include**:
- Type (Functional / Quality / Constraint / Traceability)
- Description (EARS format: "The model SHALL...")
- Priority (Must Have / Should Have / Nice to Have)
- Rationale (Why this matters)
- Validation (How to verify)

**Good MR Examples**:
- MR-001: The model SHALL define ThermalLoad calc def in library/analyses/thermal_loads.sysml
  - Type: Functional
  - Rationale: Required for blanket thermal analysis
  - Validation: Parse check passes, calc def present in file

- MR-002: The model SHALL compute thermal load matching codebase source ThermalPower.py:125 within 2%
  - Type: Functional / Validation
  - Rationale: Ensure numerical accuracy
  - Validation: codebase source comparison test

### Error Handling
- If modeling scope vague, STOP and request clarification
- If existing models not found in models/README.md, STOP and search thoroughly
- If scope too large (>5 model files), STOP and suggest breaking into phases
- If codebase source sources not specified, STOP and ask for traceability sources
- If conflicts with existing models, note and discuss integration strategy

### Critical Rules
- ALWAYS read models/README.md FIRST to check for existing models
- ALWAYS read project context (OVERVIEW, MODELING_GUIDE, BACKLOG)
- ALWAYS create feature directory: `project/active/{feature-name}/`
- ALWAYS use MR-XXX numbering for modeling requirements
- ALWAYS specify codebase source traceability sources
- ALWAYS link to relevant epic
- NEVER use vague criteria like "model works well" - specify measurable validation targets

---

**Related Commands:**
- Before spec-model → `/research` for exploration of modeling approaches
- After spec-model → `/design-model` for technical design and prototyping

**Last Updated**: 2025-11-17

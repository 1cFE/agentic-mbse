---
name: plan-model
description: Create phased implementation plan for SysMLv2 models with validation checkpoints
skills: [model-validation, sysml-conventions, project-structure]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Plan Model Command

**Purpose:** Organize the WORK — break model implementation into phased, executable steps with validation checkpoints.
**Input:** Approved design at `work/active/{WI-XXX}_{name}/design.md`
**Output:** `work/active/{WI-XXX}_{name}/plan.md`

The design phase produced a working prototype (Levels 1-3 passing) and a validation report. Your job is to organize the refinement of that prototype to production quality: complete documentation, full constraints, comprehensive integration, verification tests.

When invoked without a work item, ask which item in `work/active/` to plan.

## Skills Referenced

- **model-validation**: Quality pyramid, CLI usage, regression testing patterns. Consult for validation checkpoints (which levels per phase vs final), test phase planning, and interpreting Level 4-6 issues from the design validation report.
- **sysml-conventions**: Syntax rules, naming, pitfalls. Consult when checking feasibility of planned syntax patterns (constraints, cross-file bindings, refactoring).
- **project-structure**: Library vs designs, file organization. Consult when determining phase ordering (library before instances) and file placement.

## Process

### 1. Understand

Read the design, spec, and prototype files:
- `work/active/{WI-XXX}_{name}/design.md` — primary input. Understand all model elements, dependencies, traceability sources, and the validation report (prototype files, Level 4-6 issues to address).
- `work/active/{WI-XXX}_{name}/spec.md` — acceptance criteria, SV-XXX verification entries, scope boundaries.
- Prototype files listed in the design's validation report — understand what already works and what needs refinement.
- `modeling_project/MODELING_PROCESS.md` — project methodology context.

If the design doesn't exist or hasn't been approved, stop and ask the user to complete `/design-model` first.

### 2. Phase the Work

Break the refinement into 3-6 phases following these principles:
- **Library before instances** — definitions before usages
- **Bottom-up dependencies** — base definitions before derived ones
- **Logical groupings** — related components in the same phase
- **Validate after each phase** — every phase ends with a validation checkpoint
- **Test alongside implementation** — each phase includes test activities per the **model-validation** skill's regression testing patterns (new library defs get structural tests, design instances get integration tests, final phase runs full regression)

If phasing is unclear, present 2-3 options to the user with trade-offs.

### 3. Assess Feasibility

Before presenting the plan, validate that planned refinements are sound:

1. **Review planned changes** — identify new calc defs, structural changes, complex constraints, cross-file bindings. Check syntax patterns against the **sysml-conventions** skill. Verify calc defs are planned for `library/` not `designs/`.
2. **Check against design validation report** — the design flagged Level 4-6 issues. Map each issue to a specific phase that addresses it (e.g., Level 5 documentation gaps → Phase N, Level 6 architectural concerns → Phase M).
3. **Flag risks** — circular dependency risks from cross-file bindings, breaking changes to existing usages, patterns that might fail validation. Include mitigations for each.
4. **Document prototype baseline** — list prototype files from design phase, their current validation status (Levels 1-3 passing), and specific refinement needs from Levels 4-6.

### 4. Write the Plan

Create the plan file at `work/active/{WI-XXX}_{name}/plan.md`:
```yaml
---
Status: draft
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>
Related Artifacts:
  Spec: ./spec.md
  Design: ./design.md
---
```

Present the plan to the user. Options:
- **Approve** — proceed to `/implement-model`
- **Adjust** — change phasing, scope per phase, risk handling
- **Need more design work** — return to `/design-model`

## What Good Output Looks Like

A plan.md should contain:

- **YAML Frontmatter** — Status, Created, Updated, Related Artifacts (Spec, Design)
- **Source Documents** — links to design (primary), spec, epic file
- **Design Summary** — 2-3 sentences only. Reference design doc for rationale, sources, and alternatives — do NOT repeat them.
- **Prototype Baseline** — files from design phase, current validation status, specific Level 4-6 issues to address with phase mapping
- **Phasing Approach** — why work is broken into these specific phases
- **Validation Strategy** — per-phase (Levels 1-3 after each phase), optional user review points, final (comprehensive Levels 1-6)

**Per-Phase Sections** — each phase must include:

- **Overview** — what refinements are being made and why this phase comes here in the sequence
- **Design Reference** — cite **specific sections** of the design doc by name (e.g., "See design doc 'Model Element 5: Breeding Blanket' for parameters and constraints"). Summarize key design decisions in 1-2 bullets — do not repeat the full rationale. The implementing agent should be able to read *only* the cited sections, not the entire design.
- **Prototype Baseline** (per phase) — existing files with their current state and what specific refinements are needed (e.g., "has basic structure, needs complete doc comments and source citations")
- **Files to Create/Modify** — explicit file paths marked NEW or REFINE
- **Checklist** — concrete, actionable items with checkboxes at this granularity:
  - Every file creation/modification
  - Every definition within a file (each part def, calc def, etc.)
  - Attribute groups within definitions (geometric, electrical, material, etc.)
  - Doc comment completions with source citation targets
  - Traceability matrix row additions (`data/traceability_matrix.csv`)
  - Every validation command to run
- **Test Requirements** — what tests to write or verify this phase, per the **model-validation** skill
- **Validation Checkpoint** — parsing validation (`uv run syside check` on modified files), quality validation (Levels 1-3 must pass), manual checks (naming, imports, types), expected output
- **Phase Completion Gate** — explicit conditions that must hold before proceeding

**Parallelization** (when 3+ independent files exist in a phase):
- Mark which files can be created concurrently
- For each parallelizable file, specify: package name, plan section reference, codebase source with file:line ranges from `knowledge/SOURCE_INDEX.md`, parts/attributes to create, validation rules to follow
- Implementation instruction: "Use Task tool to create files in parallel. Main agent validates batch."

**Final Phase: Integration & Validation** must include:
- All files parse without errors
- Quality validation: Levels 1-3 pass (critical), Levels 4-8 reviewed
- Traceability: all defs have doc comments with source citations, traceability matrix complete
- Regression tests pass: `uv run pytest tests/models/ -v`
- All spec acceptance criteria verified (list them explicitly from spec.md)
- SV-XXX verification tests written for entries created during `/spec-model`

**Feasibility Concerns** — risks with mitigations, assumptions about prototype state

The depth should match the complexity. A simple refinement needs fewer phases than a multi-subsystem production push.

## Guidelines

- The plan is an instruction manual for the implementing agent — it must be precise enough that the agent can execute each phase by reading only the plan and the cited design sections
- Reference design doc by **specific section names and element names** — never "see the design doc" generically
- Do NOT repeat design rationale, research findings, codebase analysis, or SysML code examples — reference them
- Every file, definition, and validation step is a checkbox
- Validation is continuous — Levels 1-3 after every phase, don't let errors accumulate
- Offer user review at natural breakpoints (after all library defs, after complex subsystems, before final integration)
- If the design lacks a validation report, flag this to the user — the plan depends on knowing prototype state
- The final phase is not optional — every plan ends with comprehensive integration and validation

---

**Related Commands:** Before -> `/design-model` | After -> `/implement-model`

---
name: design-model
description: Create semantic design document for SysMLv2 models with prototyping and validation
skills: [sysml-conventions, project-structure, model-validation, source-traceability, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion, WebSearch]
user-invocable: true
---

# Design Model Command

**Purpose:** Design SysMLv2 models — decide WHAT components exist, HOW they relate, and WHY.
**Input:** Spec at `work/active/{WI-XXX}_{name}/spec.md`
**Output:** `work/active/{WI-XXX}_{name}/design.md` + working prototype + validation report

Focus on engineering semantics, not SysML syntax. The design should be understandable by an engineer who doesn't know SysMLv2. Syntax examples are helpful but secondary.

When invoked without a work item, ask which item in `work/active/` to design.

## Skills Referenced

- **sysml-conventions**: Syntax rules, naming, definition vs usage, pitfalls, doc comments. Consult when writing SysML stencils or reviewing prototype code.
- **project-structure**: Library vs designs separation, file organization, 4-directory model. Consult when deciding where elements belong.
- **model-validation**: Quality pyramid, CLI usage, regression testing. Consult when validating prototypes.
- **source-traceability**: SOURCE_INDEX format, citation patterns, traceability matrix. Consult when establishing source citations.
- **requirements-tracking**: PR-XXX format, EARS syntax. Consult when referencing requirements.

## Process

### 1. Understand

Read the spec fully. It tells you what to design and points to what else matters — specific goals (G-XXX), requirements (PR-XXX), DI-XXX insights, and prior research. Read those selectively.

Read `modeling_project/ARCHITECTURE.md` to understand the full structural decision landscape (AD-XXX). The spec references specific requirements, but the design needs to respect *all* relevant architectural decisions — domain decomposition, package organization, calculation placement rules — not just the ones the spec explicitly called out.

Read `models/README.md` to understand what already exists. Read `knowledge/SOURCE_INDEX.md` to know what domain sources are available. Read `modeling_project/MODELING_PROCESS.md` for the project's design methodology.

Create the design file at `work/active/{WI-XXX}_{name}/design.md`:
```yaml
---
Status: draft
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>
Related Artifacts:
  Spec: ./spec.md
---
```

If the spec doesn't exist, stop and ask the user to create one (`/spec-model`).

### 2. Design

This is where the real work happens. Research, draft, refine — iterate until the design is solid.

**Research thoroughly.** Use parallel agents:
- Explore agent to map existing calc defs and patterns in `models/library/`
- kerml-expert + sysml-expert for SysML modeling patterns and standard library functions
- general-purpose agent to analyze codebase sources from SOURCE_INDEX.md (extract parameters, formulas, validation data)
- Web search for physics, material properties, standards not covered by configured sources

**Build up the design iteratively.** Start with high-level component structure, then progressively add detail — parameters, constraints, cross-file bindings, traceability. One subsystem at a time.

**Present alternatives when genuinely uncertain.** If multiple architecturally distinct approaches exist with real trade-offs, present them to the user with a recommendation. Wait for their direction. Don't ask about things you can resolve yourself.

**Key architectural constraints** (from MODELING_PROCESS.md):
- Dataflow must be unidirectional (geometry → structural → physics)
- Calc defs belong in `library/`; design expressions must be static-evaluable (ADR-002)
- Library for reusable definitions, designs for project-specific instances
- Minimize cross-file coupling; document all bindings

### 3. Validate

Prototype the design in actual .sysml files — enough to confirm the architecture works, not production-polished.

Run validation per the **model-validation** skill. Levels 1-3 must pass. Check that cross-file imports resolve and no circular dependencies exist. Note Level 4-8 issues for implementation.

If validation fails, fix the design and re-validate. Document what you found and changed.

Add a validation report to design.md: quality check results, integration status, files created/modified, prototype status (PASS/FAIL).

### 4. Approve

Present the complete design.md and validation results to the user. Options:
- **Approve** → proceed to `/plan-model`
- **Iterate** → address concerns, return to design/validate
- **Need more data** → use `/research`

Document approval in design.md. Note that `/review-model` is available for independent design review.

## What Good Output Looks Like

A design.md should contain:

- **YAML Frontmatter** — Status, Created, Updated, Related Artifacts (Spec)
- **Overview** — what's being designed and why
- **Research Findings** — what you learned from codebase sources, existing models, web research
- **Design Decisions** — user-approved choices with rationale (if any)
- **Proposed Design** — per-element: engineering description, parameters with units and sources, constraints with formulas, traceability to sources, file location and type (definition vs usage). SysML stencils per **sysml-conventions** skill.
- **Cross-File Bindings** — table of bindings (input → source file → attribute), required imports, dataflow diagram
- **Validation Plan** — how to verify correctness (parsing, constraints, baseline comparison)
- **Validation Report** — prototype results
- **Implementation Checklist** — phased: library → components → integration → validation
- **Risks** — what could go wrong, mitigations

The depth should match the complexity. A simple library addition needs less than a multi-component system design.

## Sub-Agent Usage

| Question Type | Agent |
|--------------|-------|
| Standard library functions (sum, size, collect) | `kerml-expert` |
| Modeling patterns (parts, ports, interfaces) | `sysml-expert` |
| Parser/tooling questions | `syside-expert` |
| Syntax validation, error interpretation | `sysmlv2-validator` |
| Codebase exploration | `Explore` |
| Deep code analysis from SOURCE_INDEX sources | `general-purpose` |

Spawn multiple agents in parallel for independent questions. Cross-reference findings before making recommendations.

## Guidelines

- Focus on **engineering semantics** — clear enough for someone who doesn't know SysMLv2
- The spec defines what to design; the skills define how to do it correctly
- Always analyze codebase sources from `knowledge/SOURCE_INDEX.md`
- Comply with referenced AD-XXX decisions and PR-XXX requirements
- Specify traceability for all claims (codebase source with file:line, papers, web)
- Define how correctness will be verified

---

**Related Commands:** Before → `/research` or `/spec-model` | After → optionally `/review-model`, then `/plan-model`

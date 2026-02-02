---
name: implement-model
description: Execute approved plan to implement SysMLv2 models with validation and progress tracking
skills: [sysml-conventions, model-validation, project-structure, source-traceability, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Implement Model Command

**Purpose:** Execute an approved implementation plan — refine a validated prototype to production quality.
**Input:** Plan at `work/active/{WI-XXX}_{name}/plan.md`
**Output:** Production-quality model files, updated plan with progress

The design phase produced a working prototype (passing Levels 1-3). The plan defines what refinements to make. Your job is to execute those refinements: complete documentation, full constraints, comprehensive integration.

When invoked without a work item, ask which item in `work/active/` to implement.

## Skills Referenced

- **sysml-conventions**: Naming, definition vs usage pattern, doc comment format, common pitfalls. Consult before writing any SysML and when fixing validation errors. Use `references/stencils.md` for definition templates.
- **model-validation**: Quality pyramid, CLI usage, regression testing patterns. Consult when running validation or interpreting results.
- **project-structure**: File organization, library vs designs. Consult when deciding where files go.
- **source-traceability**: Citation patterns, traceability matrix format. Consult when writing doc comments and updating traceability.
- **requirements-tracking**: PR-XXX format. Consult when discovered modeling requirements should be promoted to project requirements.

## Process

### 1. Understand the Plan

Read the plan, design, and spec fully. Review the prototype files listed in the design's validation report — understand what already works and what needs refinement.

Check for existing progress (checkmarks in plan.md). Read any PR-XXX requirements from `modeling_project/REQUIREMENTS.md` that the spec references.

Confirm scope with the user:
- One phase at a time (safer) vs multiple phases vs all phases

### 2. Implement

Work through the plan phase by phase, task by task.

**For each task:**
1. Write or modify the .sysml file following the plan's specification
2. Follow **sysml-conventions** skill for naming, syntax, and doc comment format. Follow **source-traceability** skill for citation patterns.
3. Validate after each file: `uv run syside check models/path/to/file.sysml`
4. Update progress immediately — check off the task in plan.md (`- [ ]` → `- [x]`)

**De-risk unfamiliar syntax** by testing in a temp file first:
```bash
cat > /tmp/test_snippet.sysml << 'EOF'
package TestSnippet {
    // Your uncertain syntax here
}
EOF
uv run syside check /tmp/test_snippet.sysml
```

**When validation fails**, use specialized agents: `sysmlv2-validator` for error interpretation, `kerml-expert` for standard library questions, `sysml-expert` for modeling patterns. Spawn the validator + relevant expert in parallel for "why doesn't this work?" questions.

**For large plans**, read the full plan once, then work from the relevant phase section. Use Task agents to extract/condense sections from very large documents. For 3+ independent files, consider parallel creation with Task agents (each creates one file, main agent validates the batch).

**Capture discoveries during implementation:**
- When you discover a domain insight worth preserving:
  `agentic-mbse pm add-insight --title "<title>" --source "work-item:<WI-XXX>/<artifact>" --context "<context>" --model-implications "<implications>" --analysis-implications "<implications>" --rationale "<why captured>"`
- When creating a significant model element, record traceability:
  `agentic-mbse pm trace-element --element "<name>" --file "<path>" --type "<kind>" --knowledge DI-XXX --requirement PR-XXX --source-type "<type>" --source-doc "<name>" --source-location "<loc>"`
- When a modeling requirement proves durable enough to promote to a project requirement:
  `agentic-mbse pm promote-requirement --requirement "<text>" --source <DI-XXX or G-XXX>`

### 3. Validate Each Phase

At the end of each phase:

1. Run quality validation per the **model-validation** skill. Levels 1-3 must pass. Review Level 4-8 warnings.
2. Run regression tests: `uv run pytest tests/models/ -v`
3. Check ADR-002 compliance: no calc defs in `models/designs/`
4. Update traceability files (`data/traceability_matrix.csv`, assumption register if applicable)

Document phase completion in plan.md: models created/modified, validation results, issues encountered, deviations from plan.

If validation fails, fix the issue and re-validate before moving to the next phase.

**When implementation reveals a design flaw**, present the user with options:
- **Revise**: Update design.md with the new understanding, re-validate the prototype, adjust plan.md, resume implementation
- **Workaround**: Continue with a documented deviation from the design
- **Pause**: Set aside this work item, work on something else

### 4. Write Verification Tests

The spec created SV-XXX entries in `modeling_project/VALIDATION_MATRIX.md` with status `pending`. Write pytest tests in `tests/models/` that verify those criteria. Tests that exercise the downstream pipeline (sysml-codegen → teax) should use the `codegen_available` skip marker so they activate automatically when the pipeline is operational.

### 5. Complete

When all phases are done:
- All models parse, Levels 1-3 pass, regression tests pass
- All definitions have doc comments with source citations (per **sysml-conventions** and **source-traceability** skills)
- Traceability matrix updated
- Verification tests written for SV-XXX criteria
- All plan checkboxes marked complete
- All spec acceptance criteria met

Report completion to the user with a summary of what was built and validation status.

## Guidelines

- Follow **sysml-conventions** strictly — every definition needs doc comments with sources, correct naming (Title Case for defs, snake_case for usages), standard imports
- Track progress continuously — update plan checkboxes after each task, not in batches
- Validate continuously — don't let errors accumulate across multiple files
- Document deviations — if you do something differently from the plan, explain why
- Stop on major issues — parse failures, traceability gaps, significant baseline deviations. Get user approval before continuing.

---

**Related Commands:** Before → `/plan-model` | After → verify, update epic, move to completed

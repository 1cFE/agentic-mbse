---
name: audit-models
description: Verify SysML model accuracy against baseline sources, project requirements, and architectural decisions
skills: [model-validation, source-traceability, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Audit Models Command

**Purpose:** VERIFY models — independent verification against baseline sources, project standards, and architectural decisions.
**Input:** A work item in `work/active/`, OR specific model files/directory to audit
**Output:** Audit report saved to `work/analysis/`

The audit operates at two scopes:

- **Work item audit** — the final stage of the `spec → design → plan → implement → audit` pipeline. Verifies a specific work item's models against its spec's acceptance criteria AND project-level standards. Invoke with a work item path.
- **Project audit** — a health check across models. Verifies against project-level standards only (no per-item spec). Invoke with model file paths or a directory.

When invoked without arguments, ask which scope the user wants.

## Skills Referenced

- **model-validation**: Quality pyramid (8 levels), verification thresholds (PASS ≤1%, WARN 1-5%, FAIL >5%), CLI commands. Consult for threshold definitions, validation commands, and interpreting results.
- **source-traceability**: Citation patterns, confidence assessment, traceability matrix schema. Consult when evaluating doc comment quality and traceability completeness.
- **requirements-tracking**: PR-XXX format, EARS syntax, compliance checking. Consult when assessing models against project requirements.

## Verification Obligations

Every audit must evaluate the following against the models in scope. Present the audit scope and applicable obligations to the user before starting.

### Numerical Accuracy

For every parameter value in the audited models, trace back to its baseline source from `knowledge/SOURCE_INDEX.md` and compare. Apply thresholds per the **model-validation** skill. For each parameter, report: model value with file:line, baseline value with source file:line, discrepancy %, and PASS/WARN/FAIL status.

Special cases:
- **Calculated values**: Evaluate the baseline calculation, show steps
- **Unit mismatches**: Convert and note the conversion
- **Arrays/lists**: Compare element-by-element, report max discrepancy
- **Model param not in baseline**: Report as "design-specific"
- **Baseline param not in model**: Report as "not implemented"

### Source Traceability

Every definition (part def, calc def, attribute def) in the audited models must have:
- A doc comment citing its authority source with file:line references (per **source-traceability** skill)
- An entry in `data/traceability_matrix.csv` linking it to DI-XXX knowledge and/or PR-XXX requirements

Report definitions missing citations and definitions missing traceability matrix entries as separate categories.

### Programmatic Validation

Run `agentic-mbse validate` against the audited models. Report results for all 8 levels. Levels 1-3 failures are critical and must be resolved. Level 4-8 issues are findings to report.

### PR-XXX Compliance

Read `modeling_project/REQUIREMENTS.md`. For **each** PR-XXX that applies to the audited scope, determine whether the models satisfy it. Report pass/fail per requirement with specific evidence — which model elements satisfy or violate, with file:line references.

### AD-XXX Adherence

Read `modeling_project/ARCHITECTURE.md`. For **each** AD-XXX decision relevant to the audited scope, verify the models are consistent. Report deviations with specific evidence — what the decision requires vs what the models actually do.

### SV-XXX Evaluation

Read `modeling_project/VALIDATION_MATRIX.md`. For each SV-XXX criterion the audit can evaluate, determine current status and update it:
`agentic-mbse pm update-validation <SV-XXX> --status <passing|failing|pending>`

SV-XXX entries with `Mechanism: test` that require the downstream pipeline (codegen → teax) — report as "not yet verifiable" if the pipeline isn't operational.

### Work Item Acceptance (work item audit only)

When auditing a specific work item, also read:
- `work/active/{WI-XXX}_{name}/spec.md` — MR-XXX requirements and acceptance criteria
- `work/active/{WI-XXX}_{name}/design.md` — design decisions and validation report
- `work/active/{WI-XXX}_{name}/plan.md` — implementation plan and completion gates

Verify **each** MR-XXX requirement is satisfied by the implemented models. Verify all spec acceptance criteria are met. Verify all plan completion gates passed. This is the independent verification that implementation is complete.

## Process

1. **Scope** — determine work item audit vs project audit. Identify target models, locate baseline sources, load project standards (REQUIREMENTS.md, ARCHITECTURE.md, VALIDATION_MATRIX.md, traceability_matrix.csv). For work item audits, read the spec/design/plan chain. Present scope and get user confirmation.

2. **Verify** — execute each applicable verification obligation. Use parallel reads for multiple model files. Read baseline source files once and cache values. For large audits, work incrementally by file or subsystem.

3. **Analyze** — for each WARN/FAIL: check doc comments for deviation rationale, check for unit issues, determine if design decision or error. Every FAIL needs a concrete recommendation: correct the value, document the intentional deviation, or confirm it's by design.

4. **Promote patterns** — if the audit reveals a recurring structural pattern worth codifying as an architectural decision, propose it to the user. If approved:
   `agentic-mbse pm register-decision --title "<title>" --decision "<text>" --rationale "<text>"`

5. **Report** — generate the audit report and save to `work/analysis/YYYYMMDD-HHMMSS_audit_{scope}.md`. Present summary to user with overall status, statistics per category, and critical findings. Offer follow-ups: fix FAILs and re-audit, add traceability for gaps, create work items for significant issues (`/backlog`).

6. **Close offer** (work item audit only) — if the audit verdict is positive (all MR-XXX satisfied, all spec acceptance criteria met, Levels 1-3 passing), ask the user whether they want to close the work item. Use `AskUserQuestion` with options: "Close this work item" (archives to completed, updates all Status fields) and "Keep open" (no state change — user may want further work or re-audit). If the user confirms close:
   ```
   agentic-mbse pm close-item <WI-XXX>
   ```
   Then proceed to the project document review trigger questions (same as `/backlog close` and `/status close`):
   - "Did you discover a modeling pattern that should be a project-wide rule?" → `agentic-mbse pm promote-requirement`
   - "Did you make a structural decision that future work needs to know?" → `agentic-mbse pm register-decision`
   - "Should any new verification criteria be added?" → `agentic-mbse pm add-validation`
   - "Did you learn something about the domain not yet captured?" → `agentic-mbse pm add-insight`

## What Good Output Looks Like

An audit report should contain:

- **Executive Summary** — overall status, statistics per category, key findings
- **Validation Results** — `agentic-mbse validate` output for all 8 levels
- **Numerical Verification Table** — every parameter: model value + location, baseline value + source, discrepancy %, status
- **Critical Issues (FAIL)** — each with: values, locations, discrepancy, analysis, recommendation
- **Warnings (WARN)** — same structure, lighter analysis
- **Traceability Gaps** — definitions missing citations, definitions missing traceability matrix entries
- **PR-XXX Compliance** — per-requirement pass/fail with evidence (file:line)
- **AD-XXX Adherence** — deviations with evidence
- **SV-XXX Status Updates** — criteria evaluated, new statuses, criteria not yet verifiable
- **MR-XXX Verification** (work item audit only) — per-requirement pass/fail, spec acceptance criteria results
- **Recommendations** — immediate actions, follow-up actions, promotable patterns
- **Audit Metadata** — models audited with paths, baseline source, thresholds, date

## Guidelines

- If baseline source is not accessible, stop — cannot verify numerical accuracy without it
- If models don't parse, stop — request parse error fixes before auditing
- If traceability is missing for a parameter, attempt name-based matching and ask the user to confirm
- Unmapped parameters are a traceability gap, not necessarily an accuracy issue — report separately
- The audit report is evidence — be specific with file paths, line numbers, exact values, percentage discrepancies
- For work item audits: the spec defines what "done" means. If the spec says it, the audit verifies it.

---

**Related Commands:** Before → `/implement-model` (work item pipeline) or ensure models parse (`agentic-mbse validate --level 1`) | After → fix issues, re-audit | Related → `/research` (knowledge updates may trigger re-audit)

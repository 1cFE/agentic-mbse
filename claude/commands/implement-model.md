---
name: implement-model
description: Execute approved plan to implement SysMLv2 models with validation and progress tracking
skills: [sysml-conventions, model-validation, project-structure, source-traceability, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Implement Model

Produce the authorized model and test changes. Apply “Process Selection” in `modeling_project/MODELING_PROCESS.md`; use existing requirements and design evidence, including a combined work record. Maintain progress in the existing checklist; do not create missing stage documents solely to enter implementation.

## Resume from Evidence

Read the plan, spec acceptance conditions, and the design/source sections relevant to the current work. Expand those reads when an unexpected dependency appears. Inspect existing files and results before repeating completed steps. Implementation may begin from an existing prototype or directly from a design whose approach is understood.

Use the scope already authorized by the owner or coordinator. Do not add routine approval pauses between checklist entries.

## Implement and Check

Work in dependency order. Before changing calculations, bindings, interfaces, or semantic operators, read the applicable reference selected by the technical-pattern table in `modeling_project/MODELING_PROCESS.md`, unless already loaded and current. Follow project requirements and the **sysml-conventions**, **project-structure**, and **source-traceability** guidance as applicable. Keep physical ownership, interfaces, and analytical bindings consistent with the design, including affected consumers outside the edited file.

Validate at useful change boundaries: focused parsing or tests while editing, relevant integration/regression checks when the change is coherent. Use **model-validation** to distinguish structural checks from source, numerical, and engineering evidence. Check repaired behavior through the actual supported route; preserve meaningful failure cases as tests where feasible. Unavailable or skipped checks remain unverified.

For unfamiliar syntax or execution behavior, use a small probe or ask a specialist a concrete question. Delegate independent work only with clear ownership, and integrate shared writes sequentially. Keep useful author context through clarifications and repairs.

Update the plan as meaningful work completes. Record evidence paths, actual outcomes, deviations, and remaining obligations. Maintain citations and applicable verification/traceability records through the project's native PM operations. Before handoff, carry consequential reusable decisions into `modeling_project/ARCHITECTURE.md` and warranted discoveries into the applicable knowledge/requirement records through native PM operations. Preserve source authority and owner-reserved approvals; routine corrections need no new project-wide entries.

If evidence invalidates a design premise, surface the conflict and park dependent work. Revise the design and checklist where ordinary implementation reasoning is sufficient; obtain the owner decision where scope, source meaning, or a reserved gate changes.

## Return

Report implemented behavior, checks run, limitations, and downstream handoffs. Complete the applicable final checklist on the integrated change. Implementation evidence is ready for review when the spec outcomes are supported and outstanding work is explicit. Completion requires acceptance evidence and the independent reviews triggered by “Process Selection”; a separate audit is not required for every item. Reuse applicable evidence and review repair diffs without repeating unaffected batteries.

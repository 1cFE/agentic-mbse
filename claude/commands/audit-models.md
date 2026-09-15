---
name: audit-models
description: Verify SysML model accuracy against baseline sources, project requirements, and architectural decisions
skills: [model-validation, source-traceability, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Audit Models

Use the assigned scope and “Review Brief and Context Limits” in `modeling_project/MODELING_PROCESS.md`. For a focused question, read only the supplied entry sections and primary evidence within the brief’s budget; return missing evidence before expanding. Apply the broader checks below only to claims in scope. Save a short finding in the existing work record or requested evidence path; a separate report is useful for a substantive assessment.

Independently assess whether the model supports its promised outcomes and intended use. Run as a fresh non-author reviewer without inherited author conversation. For a substantive audit, save `work/analysis/YYYYMMDD-HHMMSS_audit_{scope}.md` and link it from the work item or epic.

## Choose the Scope

- **Work item audit:** verify the spec outcomes, changed behavior, and affected dependencies/consumers. Read the plan's evidence and relevant design sections; expand where a finding requires it.
- **Epic audit:** verify epic success criteria, item audit evidence, dependency handoffs, and cross-item integration. Positive item audits do not establish the integrated outcome by themselves.
- **Project audit:** assess the requested broader system claims against project requirements, source evidence, and actual model coverage.

Use the already authorized scope or clarify what is to be assessed. State the examined revision, supported use, and evidence limits. A narrow audit must not read as certification of every parameter or engineering assumption.

## Verify the Outcome

Read the four-view completion obligation and relevant architecture/pattern rules in `modeling_project/MODELING_PROCESS.md`, the applicable requirements and architectural decisions, and the implementation. Check the physical and behavioral relationships behind the calculations where they matter to the claim. Trace the affected claim through requirements, behavior, component occurrences/interfaces, analytical bindings, and verification evidence. Component ownership, interfaces, analytical bindings, and consumer interpretation must agree. Check that documented approximations still support the claim; an inventory of declarations does not establish this. When calculation wiring changes, inspect which occurrence each input resolves to and check that relevant public-input changes reach its consumers.

Read `modeling_project/VALIDATION_MATRIX.md` and identify existing criteria affected by this change, including those omitted from the supplied spec or plan. Assess their evidence within scope; retain applicable unchanged evidence and mark unresolved coverage unverified.

Select independent checks for the real risks: original defect counterexamples, changed public-input behavior, source-image comparisons, dimensional identities, numerical boundaries, or an affected consumer's outputs. Use justified tolerances. A copied formula, a preserved graph, or a baseline match alone cannot establish independent physical validity.

Inspect deposited validation and regression results using **model-validation** guidance. Independently reproduce a check only for missing evidence or a concrete doubt; name that reason. Do not rerun full batteries as a default audit step. Reuse unchanged evidence where its scope, revision, and environment remain applicable; explain gaps, skips, and inherited failures rather than counting them as passes.

Follow the target project's citation requirements. Check that relevant references resolve and support the claim; documentation presence and source accuracy are different checks. Update evaluable SV-XXX entries through `agentic-mbse pm update-validation` using `passing`, `failing`, or `pending`. Required evidence that cannot be obtained stays unverified.

## Report and Resolve

Report the scope, outcome-by-outcome verdict with evidence, material findings, and remaining limitations. Distinguish source fidelity, translation agreement, numerical accuracy, engineering applicability, and consumer behavior where relevant; no separate report per category is required.

A positive verdict requires the applicable completion contract to be met, with no unresolved finding that defeats it. A failed check needs a concrete explanation and repair or owner decision. After repair, independently recheck the finding and affected relationships; repeat broader checks only when the change warrants it.

Check that consequential reusable decisions and discoveries have reached their applicable durable records. The owner decides whether to close or archive. On explicit authorization, follow “Durable Handoff and Closure” in `modeling_project/MODELING_PROCESS.md` and use `agentic-mbse pm close-item <WI-XXX>`.

---
name: spec-model
description: Define modeling requirements and success criteria for SysMLv2 model enhancements
skills: [project-structure, source-traceability, model-validation, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Spec Model

Use “Process Selection” in `modeling_project/MODELING_PROCESS.md`. This stage may be brief or skipped when its responsibility is already satisfied. For a bounded tracked change, use sections in the existing `spec.md` instead of creating separate design/plan documents; retain required native metadata. The instructions below describe a separate artifact when it is useful.

Define the intended modeling outcome, requirements, and supported use. Write `work/active/{WI-XXX}_{name}/spec.md` using the project's native work-item registration and metadata conventions.

## Understand the Need

Inspect `knowledge/SOURCE_INDEX.md` and `knowledge/KNOWLEDGE.md` for relevant current authority and insights, unless already loaded and current. Read the request, relevant epic outcomes, project requirements, and existing research/models. Follow their source references selectively. Identify what someone needs to understand, change, compare, or decide using the model, and what currently prevents that.

Ask only questions whose answers materially change scope, meaning, or success. Use existing authorization; under orchestration, route questions to the coordinator. Leave implementation choices to design unless an owner decision or an existing interface requires them.

## Capture the Contract

Keep the spec proportional to the work:

- Problem and intended use, including the structural or behavioral understanding needed alongside numerical results.
- Requirements and success criteria with source provenance, meaningful expected behavior, and applicable preservation obligations.
- Scope and supported-domain limits, affected consumers, assumptions, and unresolved questions.
- References to the epic, research, and governing project decisions.

Use the project's requirement identifiers and traceability conventions. Distinguish source facts, owner needs, inherited requirements, and agent inferences. Register system verification criteria in `modeling_project/VALIDATION_MATRIX.md` through native PM operations when applicable, with status `pending` until evidenced. A source quotation, formula, or example keeps its original force; it does not automatically prescribe an implementation.

For a changed public input or a broader supported use, ask what must stay physically and semantically consistent beyond the immediate calculation. Define observable outcomes instead of counting model elements or requiring particular SysML constructs. Choose numerical expectations and tolerances from their basis, not a generic quality score.

## Durable Output

The spec is the state-bearing work-item artifact. Preserve required YAML fields:

```yaml
---
Status: active
Scale: standard
Epic: <epic name or project's standalone convention>
Owner: <owner>
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>
---
```

Present the contract for review. Carry already authorized scope forward; resolve material open questions before dependent design work. The canonical workflow is in `modeling_project/MODELING_PROCESS.md`.

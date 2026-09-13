---
name: orchestrate-modeling
description: Drive a modeling objective or Epic through the appropriate model-building stages
skills: [epic-decomposition, project-structure, source-traceability, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Orchestrate Modeling

Drive a modeling objective through the appropriate artifact and evidence contracts in `modeling_project/MODELING_PROCESS.md`. Keep the outcome and owner decisions clear, choose work from evidence, and obtain independent completion review. The owner decides whether to close or archive.

## Orient

Read the objective and relevant native work/epic records, project requirements, architecture decisions, and sources. Decide whether the work is Trivial, Standard, or Epic. Resume at the earliest unmet obligation based on artifact contents and actual evidence, not filename presence.

## Align Once

Alignment is the only planned owner checkpoint. Confirm the intended outcome, supported scope, provenance conflicts, and reserved decisions before launching any stage. Reuse explicit alignment already supplied by the owner or enclosing goal; ask only for unresolved decisions.

Record that authority in `work/orchestration/<objective-slug>.md`, or cite an existing equivalent alignment record. Preserve owner-originated statements, inherited constraints, and agent choices at their own grades. Keep progress in native item/epic artifacts rather than creating another stage log. Later scope or premise changes need an explicit decision record.

## Author Continuity and Delegation

Use one continuing author for a bounded item while its context remains useful. The coordinator may author the item or delegate it. Resume the author after clarifications and repairs; replace it when a distinct job or stale context warrants a fresh start. Stage names do not require new agents.

Give a delegated author a self-contained brief: outcome, relevant artifact/source references, provenance and reserved gates, owned write surfaces, and required evidence. It routes blocking questions to the coordinator and continues independent authorized work. Routine stage approvals are coordinator decisions under this overlay.

Independent design criticism and completion audits use a fresh non-author context without inherited author conversation. A fork may help related authoring work but is not an independent critic. When replacing an author, preserve the remaining work and consequential decisions in native artifacts first.

Delegate specialists only for concrete questions. Parallel tasks need independent dependencies and coordinated write ownership; conclusions as well as writes can conflict. Integrate shared model/package and registry changes sequentially. Queue tasks within host capacity. Use the actual host delegation interface; do not build a separate dispatcher to satisfy a prescribed agent roster.

## Standard route

Have the author satisfy the spec, design, and plan contracts at the depth the item needs, then implement and validate. Research and prototype only material uncertainties; request an optional design review for a real architectural or integration risk. Follow the canonical flow rather than copying its steps into a second control system.

Obtain a fresh independent `/audit-models` assessment before reporting completion. Return concrete findings to the author, then independently verify the repair and affected dependencies. A narrow item result does not close a broader outcome whose consumer migration or integration remains outstanding.

## Epic route

Use `/backlog` and native PM operations to register the epic and its independently useful Standard items (`pm add-epic`, `pm add-item`). Carry applicable epic outcomes into each item. Execute ready items in parallel only where their semantic and write dependencies permit it.

Each item needs independent completion evidence. Once ready, obtain an independent Epic audit of epic success criteria and cross-item integration, using item audits as evidence and investigating gaps. Do not repeat all item preparation just to produce an epic verdict.

For Trivial work, use `/quick-model` and verify its targeted evidence. Reclassify when a consequential design or scope question emerges.

## Decision Policy

- **Execution detail:** decide within the aligned meaning, record consequential choices where they belong, and continue.
- **Reserved gate:** park dependent work until the owner decides; continue independent authorized work.
- **Premise surprise:** surface conflicting evidence and its consequence before dependent conclusions proceed.

Source conflicts, supported-scope changes, and intentional major baseline deviations require explicit treatment rather than routine approval. Preserve any interpretation checkpoints imposed by the target project's goal or study workflow.

## Bound Repair and Finish

After two unsuccessful repair-and-audit rounds for the same finding, or sooner with no material progress, surface the attempted fixes and unresolved evidence. Do not relabel an unchanged failure to restart the bound.

Report the outcome, artifact/evidence references, independent verdict, and remaining limitations or owner decisions. Close and archive remain owner actions through the native workflow.

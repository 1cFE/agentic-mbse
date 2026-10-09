---
name: orchestrate-modeling
description: Drive a modeling objective or Epic through the appropriate model-building stages
allowed-tools: [Read, Grep, Glob, Bash, Agent, Write, Edit, AskUserQuestion]
user-invocable: true
metadata:
  kind: workflow
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Orchestrate Modeling

Drive a modeling objective through the appropriate artifact and evidence contracts in `modeling_project/MODELING_PROCESS.md`. Keep the outcome and owner decisions clear, choose work from evidence, and select independent review using the canonical process thresholds. The owner decides whether to close or archive.

## Orient

Read the objective and relevant native work/epic records, project requirements, architecture decisions, and sources. Decide whether the work is Trivial, Standard, or Epic. Resume at the earliest unmet obligation based on artifact contents and actual evidence, not filename presence.

## Align Once

Alignment is the only planned owner checkpoint. Confirm the intended outcome, supported scope, provenance conflicts, and reserved decisions before launching any stage. Reuse explicit alignment already supplied by the owner or enclosing goal; ask only for unresolved decisions.

Record that authority in `work/orchestration/<objective-slug>.md`, or cite an existing equivalent alignment record. Preserve owner-originated statements, inherited constraints, and agent choices at their own grades. Keep progress in native item/epic artifacts rather than creating another stage log. Later scope or premise changes need an explicit decision record.

## Author Continuity and Delegation

Use one continuing author for a bounded item while its context remains useful. The coordinator may author the item or delegate it. Resume the author after clarifications and repairs; replace it when a distinct job or stale context warrants a fresh start. Stage names do not require new agents.

Give a delegated author a self-contained brief: outcome, relevant artifact/source references, provenance and reserved gates, owned write surfaces, and required evidence. It routes blocking questions to the coordinator and continues independent authorized work. Routine stage approvals are coordinator decisions under this overlay.

When review is triggered, use a fresh non-author context without inherited author conversation and the “Review Brief and Context Limits” contract in `modeling_project/MODELING_PROCESS.md`. Default other delegated jobs to fresh self-contained briefs too; reserve forks for jobs that need the actual conversation. Give focused research and review jobs explicit read scope and tool-call budgets. When replacing an author, preserve the remaining work and consequential decisions in native artifacts first.

Delegate specialists only for concrete questions. Parallel tasks need independent dependencies and coordinated write ownership; conclusions as well as writes can conflict. Integrate shared model/package and registry changes sequentially. Queue tasks within host capacity. Use the actual host delegation interface; do not build a separate dispatcher to satisfy a prescribed agent roster.

## Standard route

Have the author apply “Process Selection” before editing and record the affected consumers, uncertainty, and chosen checks. Skip or combine preparation stages already satisfied; one short native work record can hold requirements, decisions, checklist, and evidence. Research or prototype only a material uncertainty.

Obtain only the independent reviews triggered by that selection, combining overlapping questions. A source or design check need not become a full completion audit. Complex changes need independent assessment of integrated behavior. Return findings to the author and send the repair diff to the same reviewer. A narrow item result does not close a broader outcome whose consumer migration or integration remains outstanding.

## Epic route

Use `/backlog` and native PM operations to register the epic and its independently useful Standard items (`pm add-epic`, `pm add-item`). Carry applicable epic outcomes into each item. Execute ready items in parallel only where their semantic and write dependencies permit it.

Each item needs acceptance evidence and any risk-triggered review. Assess epic success criteria and cross-item integration using that evidence; commission independent review of consequential interactions not already covered. Do not add item and epic audits that judge the same evidence twice.

For Trivial work, use `/quick-model` and verify its targeted evidence. A new uncertainty triggers the relevant investigation or review, not an automatic full pipeline.

## Decision Policy

- **Execution detail:** decide within the aligned meaning, record consequential choices where they belong, and continue.
- **Reserved gate:** park dependent work until the owner decides; continue independent authorized work.
- **Premise surprise:** surface conflicting evidence and its consequence before dependent conclusions proceed.

Source conflicts, supported-scope changes, and intentional major baseline deviations require explicit treatment rather than routine approval. Preserve any interpretation checkpoints imposed by the target project's goal or study workflow.

## Bound Repair and Finish

After two unsuccessful repair-and-audit rounds for the same finding, or sooner with no material progress, surface the attempted fixes and unresolved evidence. Do not relabel an unchanged failure to restart the bound.

Report the outcome, artifact/evidence references, independent verdict, and remaining limitations or owner decisions. Close and archive remain owner actions through the native workflow.

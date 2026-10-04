---
name: plan-model
description: Create phased implementation plan for SysMLv2 models with validation checkpoints
skills: [model-validation, sysml-conventions, project-structure]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Plan Model

Use “Process Selection” in `modeling_project/MODELING_PROCESS.md`. This stage may be brief or skipped when its responsibility is already satisfied. For a bounded tracked change, use sections in the existing `spec.md` instead of creating separate design/plan documents; retain required native metadata. The instructions below describe a separate artifact when it is useful.

Turn the agreed outcomes and design into a checklist of work and evidence. Write `work/active/{WI-XXX}_{name}/plan.md`; retain Status, Created, Updated, and Related Artifacts metadata.

## Understand What Remains

Read the spec's acceptance conditions, the relevant design sections, and actual existing work. Reuse valid prototype or prior implementation evidence. If a consequential design question remains unresolved, address it before planning dependent execution.

## Write an Executable Checklist

Group work by meaningful behavior and dependencies. One phase is enough for a small change. Name affected files or model surfaces, their owners when work is delegated, and the checks that establish each outcome. Avoid repeating the design or enumerating every attribute.

For each acceptance condition, identify:

| Outcome or requirement | Check and expected observation | Basis | Evidence/status |
|---|---|---|---|
| Relevant spec reference | Runnable test or focused inspection, with expected behavior/tolerance | Source, identity, independent reference, or governing decision | Result location or remaining work |

Use this table or the project's equivalent; its purpose is to keep the acceptance evidence traceable. Include structural/analytical agreement and affected consumers where the change concerns them. Tests should expose plausible mistakes, including the original counterexample for a defect, rather than merely reproduce current wiring or copied formulas.

Choose validation checkpoints where they can catch errors usefully. Run focused checks during editing and integrated validation when a coherent change is ready. Repeating a full suite requires changed inputs, new failures, or another concrete reason. The final checklist must cover applicable regression checks, spec outcomes, and registered verification criteria; see **model-validation** for interpreting results and skips.

## Keep It Resumable

Link specific design/source sections so an implementer can load the relevant context. Record completed work, remaining checks, meaningful deviations, and any downstream migration needed for the broader outcome. Reference existing evidence instead of copying its results into several artifacts.

Parallel work requires independent dependencies and coordinated write ownership; follow the canonical process guidance. Preserve existing owner approvals and gates rather than creating routine phase-approval pauses. Implementation may refine the checklist as evidence develops without silently changing the agreed outcome.

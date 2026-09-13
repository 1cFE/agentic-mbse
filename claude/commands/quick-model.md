---
name: quick-model
description: Make a small SysML model change without the full spec-design-plan-implement pipeline
skills: [sysml-conventions, model-validation]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Quick Model

Make an understood local correction with proportionate evidence. This is the Trivial entry point; it creates no new work-item directory or item state.

Read the affected model and enough source/consumer context to understand the change. Judge scope by semantic uncertainty and impact. A companion test or synchronized family copy does not by itself require Standard work; a small edit that changes a physical assumption or shared interface may.

State the change and its basis, using the user's existing authorization. If a consequential architectural choice, source conflict, or broader outcome emerges, route to Standard work before making dependent changes.

Read relevant project requirements and use the technical-pattern table in `modeling_project/MODELING_PROCESS.md` to load guidance for the constructs being changed, unless already current. Maintain affected existing traceability and verification records through native PM operations. Apply the correction using project conventions. Verify the affected behavior and relevant consumers, including a counterexample or source check when fixing a defect. Use **model-validation** to select checks; report what ran and what remains unverified. Keep the rationale and evidence in the change record or an existing project artifact so the correction is traceable.

Report the result concisely. Follow the canonical `modeling_project/MODELING_PROCESS.md` when the work needs a larger scope.

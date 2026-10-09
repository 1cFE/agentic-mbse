---
name: quick-model
description: Make a small SysML model change without the full spec-design-plan-implement pipeline
allowed-tools: [Read, Grep, Glob, Bash, Agent, Write, Edit, AskUserQuestion]
user-invocable: true
metadata:
  kind: workflow
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Quick Model

Make an understood local correction with proportionate evidence. This is the Trivial entry point; it creates no new work-item directory or item state.

Read the affected model and enough source/consumer context to understand the change. Judge scope by semantic uncertainty and impact. A companion test or synchronized family copy does not by itself require Standard work; a small edit that changes a physical assumption or shared interface may.

State the change and its basis, using the user's existing authorization. If a consequential architectural choice, source conflict, or broader outcome emerges, apply “Process Selection” in `modeling_project/MODELING_PROCESS.md` before dependent changes. Add the needed review or investigation; create a Standard record when scope tracking needs it, without automatically running every stage.

Read relevant project requirements and use the technical-pattern table in `modeling_project/MODELING_PROCESS.md` to load guidance for the constructs being changed, unless already current. Maintain affected existing traceability and verification records through native PM operations. Apply the correction using project conventions. Verify the affected behavior and relevant consumers, including a counterexample or source check when fixing a defect. Use **model-validation** to select checks; report what ran and what remains unverified. Keep the rationale and evidence in the change record or an existing project artifact so the correction is traceable.

Report the result concisely. Follow the canonical `modeling_project/MODELING_PROCESS.md` when the work needs a larger scope.

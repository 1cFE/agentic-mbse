---
name: design-model
description: Create semantic design document for SysMLv2 models with prototyping and validation
allowed-tools: [Read, Grep, Glob, Bash, Agent, Write, Edit, AskUserQuestion, WebSearch]
user-invocable: true
metadata:
  kind: workflow
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Design Model

Use “Process Selection” in `modeling_project/MODELING_PROCESS.md`. This stage may be brief or skipped when its responsibility is already satisfied. For a bounded tracked change, use sections in the existing `spec.md` instead of creating separate design/plan documents; retain required native metadata. The instructions below describe a separate artifact when it is useful.

Explain the system architecture and dependencies needed to meet `spec.md`. Write `work/active/{WI-XXX}_{name}/design.md`; retain Status, Created, Updated, and Related Artifacts metadata.

## Understand the Affected System

For direct entry, inspect `knowledge/SOURCE_INDEX.md` and `knowledge/KNOWLEDGE.md` for relevant authority and insights unless discovery is already current. Read the spec and the “MBSE Methodology: Four Integrated Views” and “Architecture & Design” sections of `modeling_project/MODELING_PROCESS.md`. Use its technical-pattern table to read the references relevant to changed constructs, especially calculation placement and input binding. Read relevant architecture decisions, model definitions, consumers, and cited source evidence. Explain the physical components, responsibilities, interfaces, and operating behavior involved in the change, then relate them to the analysis. Inspect inherited structure as well as the local file.

Identify where shared quantities are owned and how consumers obtain them. Make physical structure and analytical dependencies consistent enough to inspect and check. Choose structural depth and SysML mechanisms where they clarify or constrain the intended model; additional declarations that carry no useful meaning are not the objective.

## Resolve the Actual Uncertainty

Use existing patterns and knowledge first. Research a missing source, consult a specialist, or prototype an uncertain language/execution capability when that evidence changes the design. Prototype only enough to answer the question, and record what was and was not demonstrated. A working prototype is not required for an already understood change.

Present consequential alternatives with their tradeoffs when owner direction is needed. Ordinary implementation choices remain with the author or coordinator. Surface source conflicts, changes to supported meaning, and premise surprises before proceeding with dependent work.

## Write the Design

The design should let an engineer understand:

- The chosen architecture and why it fits the outcome; a small change may need only an impact note.
- The path from the affected requirements through functions, component occurrences/interfaces, and analytical bindings to verification evidence. Reference model elements and existing traceability records; explain approximations or unsupported relationships and their effect on the claim.
- Source-supported equations, units, assumptions, domains, and any purposeful approximation of physical structure.
- Meaningful risks and how to check them, including relevant public-input changes, boundary cases, or structural/analytical consistency.
- Any prototype evidence, remaining uncertainty, and downstream handoffs.

Reference the spec rather than repeating requirements. Use `MODELING_GUIDE.md` and the **sysml-conventions** skill for technical patterns; follow project-specific library/design and traceability rules. Verify numerical source material against the authoritative representation when extraction may have lost equations or table values.

Review the design under the existing authorization. Use `/review-model` when independent criticism addresses a meaningful architectural or integration risk. Planning consumes the design and its remaining work, whether or not a prototype was needed.

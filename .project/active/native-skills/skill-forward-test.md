# Bounded forward review

This is a read-only behavioral walkthrough of the staged skills and Codex adapter. No target work item artifacts were supplied, so stage completion evidence, installed role availability, and actual CLI execution were not tested. No modeling, external service access, or source edits were performed.

## First executable handoff

Reuse the owner's existing alignment and its immutable brief. If the brief was not yet written, record the already supplied alignment without asking the owner to repeat it. Inspect the existing spec, design, prototype validation, and plan to verify that implementation is the earliest incomplete obligation. Link the spec to the alignment brief if needed.

Launch a fresh default agent with `fork_turns: "none"`. Its brief names `.agents/skills/implement-model/SKILL.md`, `.agentic-mbse/codex.md`, the alignment brief, the work item spec/design/plan, both model file paths, applicable source/requirement paths, provenance, and reserved decisions. The concrete job is to complete the pending plan and return changed-file evidence, updated checkboxes, validation and regression output, SV tests, and traceability evidence. Include the orchestration overlay verbatim. State that all pending plan phases are authorized so the implementation skill's routine scope-confirmation request can be resolved by the parent.

Two independent model files do not force parallel authors: implementation only suggests parallel creation for three or more files, while the orchestration parallel rule concerns Epic items. One fresh implementation agent can execute the two files serially. If a source conflict blocks one file, the parent can assign the independent remaining work in a fresh stage brief, keeping shared plan/traceability writes coordinated.

## Returned source conflict

Treat it as an owner-reserved gate, not routine approval. Preserve both competing sources and their provenance, record which model conclusions depend on the choice, and park those conclusions. Continue useful independent work. Research can gather evidence but cannot make the reserved source choice. Surface the choice to the owner when independent work is exhausted. After an answer, launch a fresh authoring agent with the original brief plus the answer.

## Completion after repair

A fresh work-item audit must cover MR requirements, spec acceptance criteria, plan completion gates, baseline comparisons, traceability, PR/AD obligations, SV evaluation, and all six validation levels. A failed audit produces concrete findings for a fresh repair author; inspect repair validation, then use another fresh audit agent. A repair author's success statement does not establish completion. Track each finding across at most two unsuccessful repair-and-audit rounds and park sooner on no material progress. Report Standard completion only with fresh positive evidence for the whole scope. Closing and archiving remain owner-held after that report.

## Findings

- The first per-file validation instruction is contradictory. `skills/implement-model/SKILL.md:47` requires `uv run syside check`, while its referenced validation guidance leads to `skills/toolkit-awareness/SKILL.md:72`, which explicitly prohibits suggesting that standalone step. Both cannot be followed literally. This is a concrete instruction conflict, not evidence that either executable is absent. Use one consistent validation entry point or document an explicit allowance for syntax probes.
- `adapters/codex.md:7` requires closing finished agents to release slots, but this evaluation host exposes spawn, interrupt, message, and wait tools with no close-agent operation. The same paragraph's schema-inspection guidance avoids inventing a tool, but the close action itself cannot be executed here. A native host with a close operation would not have this limitation. The bounded scenario can start with the tools exposed; this does not establish whether a long repair loop will exhaust this host's slots.
- The first implementation and audit skills contain owner questions and a close offer, but the orchestrator expressly overrides stage-local routine approvals and reserves close/archive. Those are resolvable precedence relationships, not execution blockers. The auditor should return its report and reserved close gate to the parent rather than contact the owner or archive.
- The package contains the Codex adapter and every skill followed in this review. Installed target paths such as `.agentic-mbse/codex.md` and `.agents/skills/...` are an installation contract; the staging directory is not itself an installed target. No missing target asset was demonstrated by this test.

The tested decision sequence supports resumed implementation, owner-held source choices, fresh repair/audit contexts, and an owner-held close action. This review does not certify modeling behavior or the installer.

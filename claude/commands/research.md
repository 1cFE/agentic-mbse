---
name: research
description: Explore authority sources and capture approved domain insights into the knowledge base
skills: [source-traceability]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion, WebSearch, WebFetch]
user-invocable: true
---

# Research Command

**Purpose:** LEARN from external sources — explore authority sources, produce a research document, and capture approved domain insights (DI-XXX) into the knowledge base.
**Input:** Research question or topic
**Output:** Research document in `knowledge/research/pending/` (moved to `approved/` on approval) + DI-XXX entries in `knowledge/KNOWLEDGE.md`

Research is the primary curation gate (AP-6): raw findings pass through user review before entering the knowledge base. The agent generates content; scripts handle file operations and registry updates (AP-7); the user makes approval decisions.

When invoked without a topic, ask "What would you like me to research?" and wait.

## Skills Referenced

- **source-traceability**: SOURCE_INDEX format, source types, citation patterns. Consult when reading `knowledge/SOURCE_INDEX.md` to discover available sources, and when writing citations in the research document.

## Process

### 1. Gather Context

Read to understand what's already known and what sources are available:

- `knowledge/SOURCE_INDEX.md` — authority sources available for this project (see **source-traceability** skill for source types)
- `knowledge/KNOWLEDGE.md` — existing DI-XXX insights. Are any relevant? Does the topic overlap with existing insights?
- `modeling_project/OVERVIEW.md` — project goals (G-XXX) and analysis questions (AQ-XXX). Which does this research serve?
- `knowledge/research/` — check `pending/` and `approved/` for prior research on related topics to avoid duplication

If the user mentions specific files, read them fully before proceeding. Check related epics in `work/backlog/` for background that shapes the research question.

For system or model research, read “MBSE Methodology: Four Integrated Views” in `modeling_project/MODELING_PROCESS.md`. Capture source-supported components, functions, interfaces, operating modes, and their relationship to the analysis where relevant to the question. Identify missing evidence and distinguish source facts from proposed modeling choices. For a syntax or execution question, use the process's technical-pattern table to select the relevant reference.

### 2. Resolve the Research Question

Use existing sources and patterns first. Consult a specialist for a concrete uncertainty that warrants it; the question-to-agent table below is a guide, not a roster. Parallelize independent questions with clear scope and write ownership within host capacity. Reuse useful context for follow-up questions.

Read relevant local materials and registered codebase sources. Use WebSearch / WebFetch where local authority is insufficient. Follow dependencies in the evidence before relying on a conclusion.

### 3. Synthesize and Write

Read the source sections needed to assess the findings, expanding when dependencies or conflicts require it. Cross-reference findings across sources. Extract actionable insights — focus on what matters for modeling decisions.

Write the research document content. The agent calls a script to save it — do not write the file directly:
```
agentic-mbse pm save-research --topic "<topic-kebab-case>" --content-file <temp-file>
```
The script saves to `knowledge/research/pending/YYYYMMDD-HHMMSS_topic.md` with the correct path and naming convention.

Present findings to the user: summary of key discoveries, feasibility assessment, and recommendations.

**Check for knowledge conflicts.** Compare findings against existing DI-XXX entries in `knowledge/KNOWLEDGE.md`. If new findings contradict or refine an existing insight, flag it:
> "DI-003 states [X]. New findings suggest [Y]. Should we supersede DI-003?"

If the user confirms supersession:
```
agentic-mbse pm supersede-insight DI-XXX --new-insight '<structured JSON for new DI>' --reason '<why superseded>'
```
This marks the old insight as superseded, creates the replacement, and produces an impact report at `knowledge/research/impacts/`.

### 4. Approve and Capture Insights

**Suggest DI-XXX insight candidates** — domain facts from the research worth preserving as structured knowledge. For each candidate, propose: title, context, model implications, and analysis implications.

The user reviews each element separately:
- **Research report**: Approve / Revise / Reject
- **Each insight**: Accept / Modify / Skip

If revisions are needed, edit the document and re-present.

On approval, call:
```
agentic-mbse pm approve-research <file> --insights '<structured JSON of approved DI-XXX entries>'
```
The script moves the file from `pending/` to `approved/`, assigns DI-XXX IDs, formats entries, and appends them to `knowledge/KNOWLEDGE.md`. Report the assigned IDs to the user.

If the user approves the report with no accepted insights (every candidate skipped, or none proposed), still make the call, with `--insights '[]'`. The file moves to `approved/` and no DI-XXX entries are created, so tell the user that instead of reporting IDs.

If the user rejects the report, the file stays in `pending/` (or delete if requested).

## What Good Output Looks Like

A research document should contain:

- **Frontmatter** — date, researcher, topic, tags, research type
- **Research Question** — the original query
- **Summary** — 3-5 bullet points answering the question
- **Detailed Findings** — per-area sections with file:line or model element references for all claims
- **Code/Model/Domain References** — specific paths and locations cited
- **Architecture/Modeling Insights** — patterns, conventions, design decisions discovered
- **Feasibility Assessment** (when applicable) — can it be done, challenges, dependencies
- **Recommendations** — suggested approach, alternatives, next steps
- **Open Questions** — areas needing further investigation

Depth should match the research scope. A targeted syntax question needs less than a domain-wide feasibility study.

## Sub-Agent Usage

| Question Type | Agent |
|--------------|-------|
| SysMLv2 modeling patterns, structural modeling | `sysml-expert` |
| KerML standard library functions, base types | `kerml-expert` |
| Parser/tooling questions | `syside-expert` |
| Codebase exploration | `Explore` |
| Deep code analysis | `general-purpose` |

Use agents when their concrete questions justify delegation. Cross-reference findings before making recommendations.

## Guidelines

- Read SOURCE_INDEX.md first — know what sources exist before researching
- All claims must include specific file:line, model element, or literature references
- Check for conflicts with existing DI-XXX before suggesting new insights
- Never save research documents by writing directly — always use the save-research script
- If insufficient information is found, document gaps and stop
- If conflicting patterns are discovered, document all and ask the user

---

**Related Commands:** After research → `/spec-model` to define requirements | `/design-model` for technical design | `/manage-sources` to configure sources

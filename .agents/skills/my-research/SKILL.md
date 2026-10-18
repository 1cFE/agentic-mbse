---
name: my-research
description: Research a topic or code area deeply and save findings. Use when you need investigation before design or implementation.
---

Generated from `claude-pack/commands/_my_research.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Research Command

**Purpose:** Deep codebase exploration and feasibility analysis
**Input:** Topic, rough idea, or area of investigation
**Output:** `.project/research/{YYYYMMDD-HHMMSS}_{topic-kebab-case}.md`

## Overview

You are a specialist research agent. Your goal is to create thorough research documents about the codebase that eliminate the need for repeated analysis.

**Context**: Before starting, check CLAUDE.md for:
- Project structure and conventions
- Key documentation locations
- Important patterns or architectural decisions

When invoked:
- If topic provided: proceed to research process
- If no topic: ask "What would you like me to research?" and wait

## Process

### Stage 1: Context Gathering

1. **Read Project Context** - Read CLAUDE.md and any referenced project documentation
2. **Read Referenced Files Completely** - If user mentions specific files, read them FULLY
3. **Check Existing Research** - Search `.project/research/` for related topics
4. **Create Research Plan** - Use TodoWrite to track subtasks

### Stage 2: Parallel Research

Spawn appropriate agents:

- **fresh-context `explorer` subagent** (thoroughness: "medium"): Find all files related to topic
- **fresh-context `default` subagent**: Analyze implementation details
- **fresh-context `explorer` subagent** (thoroughness: "quick"): Find similar patterns

**Wait for all agents to complete** before proceeding.

### Stage 3: Analysis and Synthesis

1. **Read Identified Files Completely** - Read ALL files found by agents (no limit/offset)
2. **Cross-Reference Findings** - Connect discoveries across components
3. **Extract Actionable Insights** - Focus on implementation-relevant patterns
4. **Check Against Project Conventions** - Verify alignment with patterns in CLAUDE.md

### Stage 4: Document Creation

Create research document at `.project/research/{YYYYMMDD-HHMMSS}_{topic-kebab-case}.md`:

```markdown
---
date: [ISO format with timezone]
researcher: [Your name or "Claude"]
topic: "[research topic]"
tags: [research, relevant-area]
status: complete
last_updated: [YYYY-MM-DD]
---

# Research: [Topic]

**Date**: [date with timezone]
**Researcher**: [name]
**Research Type**: [Codebase / Architecture / Domain / Integration]

## Research Question
[Original user query]

## Summary
[High-level findings answering the question - 3-5 bullet points]

## Detailed Findings

### [Component/Area 1]
- Finding with reference (file.ext:line)
- Implementation details
- Relevant constraints or patterns

### [Component/Area 2]
- Additional findings
- Cross-references to related components

## Code References
- `path/to/file.ext:123` - Description of what it does
- `tests/test_file.ext:45-67` - Test coverage notes

## Architecture Insights
[Patterns, conventions, design decisions discovered]
[How this aligns with project conventions]

## Feasibility Assessment
[Can the proposed feature/change be implemented?]
[What challenges or risks exist?]
[What dependencies or prerequisites are needed?]

## Recommendations
[Suggested approach based on findings]
[Alternatives to consider]
[Next steps]

## Open Questions
[Areas needing further investigation]
[Decisions that require stakeholder input]
```

Present summary:
```
Research complete! I've created a comprehensive analysis at:
`.project/research/{filename}`

Key findings:
- {major insight 1}
- {major insight 2}
- {feasibility assessment}

Recommendations:
- {suggested next steps}

This research provides a complete answer to "{original question}".
```

## Guidelines

### Quality Standards
- Research must answer user's question clearly and completely
- Document should be readable by someone unfamiliar with the project
- All claims must include specific file:line references
- Research should be comprehensive enough to avoid redundant analysis

### Sub-Agent Usage

**fresh-context `explorer` subagents:**
- Use parallel agents to maximize efficiency
- Specify thoroughness level ("quick", "medium", "very thorough")
- Find files, patterns, and related components

**fresh-context `default` subagents:**
- Complex analysis tasks
- Implementation detail examination
- Cross-component integration analysis

**WebSearch:**
- Finding recommended methods or best practices
- Finding up-to-date documentation on external packages

**Coordination:**
- Launch related agents in parallel when possible
- Wait for all agents before synthesis
- Cross-reference findings from multiple sources

### Error Handling
- If insufficient information found, document gaps and STOP
- If conflicting patterns discovered, document all and ask user
- For unexpected issues, STOP and consult user

### Critical Rules
- ALWAYS read CLAUDE.md and project documentation first
- ALWAYS read mentioned files before spawning sub-agents
- ALWAYS wait for all sub-agents to complete before synthesis
- NEVER write documents with placeholder values
- Ensure research completely answers the original question before concluding

---

**Related Commands:**
- After research → ``my-spec`` to define requirements
- After research → ``my-design`` for technical design
- Read-only vs write-to-learn: research analyzes *existing* code. To write code to learn how something behaves, use ``my-spike`` (confirm a known assumption with throwaway code) or ``my-learning-test`` (map an unfamiliar surface with kept tests).

**Last Updated**: 2026-07-06


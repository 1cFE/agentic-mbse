# Research Command

**Purpose:** Deep codebase/model exploration and feasibility analysis
**Input:** Topic, rough idea, or area of investigation
**Output:** `project/research/{YYYYMMDD-HHMMSS}_{topic-kebab-case}.md`

## Overview

You are a specialist research agent for MBSE projects. Your goal is to create thorough research documents about the codebase (Python), models (SysMLv2), or domain knowledge that eliminates the need for repeated analysis. Read SOURCE_INDEX.md to discover what domain sources are available for research.

**Context**: Before starting, read these project documents:
- `project/OVERVIEW.md` - Project goals and approach
- `project/MODELING_GUIDE.md` - SysML conventions

When invoked:
- If topic provided: proceed to research process
- If no topic: ask "What would you like me to research?" and wait

## Process

### Stage 1: Context Gathering

1. **Read Project Context** - Read OVERVIEW, MODELING_GUIDE, REFERENCE if not recently read
2. **Read Referenced Files Completely** - If user mentions specific files, read them FULLY
3. **Check Existing Research** - Search `project/research/` for related topics from past 30 days
4. **Check Related Epics** - Look in `project/backlog/epic_*.md` for relevant background
5. **Create Research Plan** - Use TodoWrite to track subtasks

### Stage 2: Parallel Research

Depending on research type, spawn appropriate agents:

**For Codebase Research** (Python scripts, tests):
- **Explore agent** (thoroughness: "medium"): Find all files related to topic
- **general-purpose agent**: Analyze implementation details
- **Explore agent** (thoroughness: "quick"): Find similar patterns

**For Model Research** (SysMLv2 files):
- **Explore agent**: Find relevant model files in `models/library/` or `models/designs/`
- **general-purpose agent**: Parse and analyze SysML definitions
- **Explore agent**: Find related requirements, constraints, or analyses
- **sysmlv2-doc-analyzer agent**: Get official SysMLv2 modeling patterns
  - **Use PROACTIVELY when researching:**
    - How to model specific physical systems or processes in SysMLv2
    - Proper patterns for requirements, constraints, or interfaces
    - Best practices for component decomposition
    - Questions about SysMLv2 language features or syntax
  - **Provide:** Detailed description of what needs to be modeled
  - **Returns:** Official spec guidance with examples and recommendations

**For Domain Research** (domain-specific sources from SOURCE_INDEX.md):
- Read SOURCE_INDEX.md to discover domain sources
- Search `data/documents/` for relevant papers
- Check `data/documents/synthesis/` for existing summaries
- Use WebSearch for recent information if needed
- Analyze codebase sources from SOURCE_INDEX.md if integration question

**Wait for all agents to complete** before proceeding.

### Stage 3: Analysis and Synthesis

1. **Read Identified Files Completely** - Read ALL files found by agents (no limit/offset)
2. **Cross-Reference Findings** - Connect discoveries across components
3. **Extract Actionable Insights** - Focus on implementation-relevant patterns
4. **Check Against Project Conventions** - Verify alignment with MODELING_GUIDE and REFERENCE

### Stage 4: Document Creation

Create research document at `project/research/{YYYYMMDD-HHMMSS}_{topic-kebab-case}.md`:

```markdown
---
date: [ISO format with timezone]
researcher: [Your name or "Claude"]
topic: "[research topic]"
tags: [research, codebase|models|domain, relevant-area]
status: complete
last_updated: [YYYY-MM-DD]
---

# Research: [Topic]

**Date**: [date with timezone]
**Researcher**: [name]
**Research Type**: [Codebase / Models / Domain / Integration]

## Research Question
[Original user query]

## Summary
[High-level findings answering the question - 3-5 bullet points]

## Detailed Findings

### [Component/Area 1]
- Finding with reference ([file.ext:line](link) or model element reference)
- Implementation/modeling details
- Relevant constraints or patterns

### [Component/Area 2]
- Additional findings
- Cross-references to related components

## Code/Model References
**For Code:**
- `path/to/script.py:123` - Description of what it does
- `tests/test_file.py:45-67` - Test coverage notes

**For Models:**
- `models/library/foundation.sysml` - `part def 'Fusion Power Plant'`
- `models/designs/{design_name}/system.sysml` - `part design_system`

**For Domain:**
- `data/documents/iter_physics_basis_1999.pdf` - Section 4.2, Eq. 7
- `data/documents/synthesis/first_wall_design_basis.md`

## Architecture/Modeling Insights
[Patterns, conventions, design decisions discovered]
[How this aligns with project MODELING_GUIDE]

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
`project/research/{filename}`

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
- All claims must include specific file:line or model element references
- Respect project conventions from MODELING_GUIDE and REFERENCE
- Research should be comprehensive enough to avoid redundant analysis

### Research Type Guidelines

**Codebase Research** (Python):
- Focus on `scripts/`, `tests/`, configuration files
- Check existing patterns in parent repos (mbse_ai, sysml-ai, m-scout)
- Identify test coverage and validation approaches

**Model Research** (SysMLv2):
- Search in `models/library/` for definitions
- Search in `models/designs/` for specific instances
- Pay attention to definitions vs usages distinction (see MODELING_GUIDE)
- Check traceability (doc comments, sources)

**Domain Research** (domain-specific):
- Read SOURCE_INDEX.md first to discover domain sources
- Check `data/documents/` for papers and references
- Review `data/documents/synthesis/` for prior work
- Check codebase sources (from SOURCE_INDEX.md) for validation baseline
- Use WebSearch only if local documents insufficient

### Sub-Agent Usage (Detailed)

**Explore agents:**
- Use parallel agents to maximize efficiency
- Specify thoroughness level ("quick", "medium", "very thorough")
- Find files, patterns, and related components

**general-purpose agents:**
- Complex analysis tasks
- Implementation detail examination
- Cross-component integration analysis

**sysmlv2-doc-analyzer agent:**
- **INVOKE WHEN:** Researching SysMLv2 modeling approaches or patterns
- **HOW TO USE:**
  ```
  Task(
    description="SysMLv2 modeling guidance for [topic]",
    prompt="[Detailed description of physical system or modeling question]
           Example: How should I model thermal management for a fusion
           reactor blanket with heat generation, coolant flow, temperature
           limits, and heat transfer through multiple layers?",
    subagent_type="sysmlv2-doc-analyzer"
  )
  ```
- **Agent searches:** Official SysMLv2 specs, guides, and examples
- **Agent returns:** Recommended patterns with citations and examples
- **When to use:**
  - Before deciding on component structure
  - When uncertain about interface or constraint modeling
  - For requirements traceability patterns
  - For general SysMLv2 syntax or semantics questions

**WebSearch:**
- Physics models and equations not in local documents
- Recent fusion reactor design information
- Material properties and engineering standards

**Coordination:**
- Launch related agents in parallel when possible
- Wait for all agents before synthesis
- Cross-reference findings from multiple sources

### Error Handling
- If insufficient information found, document gaps and STOP
- If conflicting patterns discovered, document all and ask user
- For unexpected issues, STOP and consult user
- If research reveals project convention violations, note them

### Critical Rules
- ALWAYS read project context docs (OVERVIEW, MODELING_GUIDE, REFERENCE) first
- ALWAYS read mentioned files before spawning sub-agents
- ALWAYS wait for all sub-agents to complete before synthesis
- NEVER write documents with placeholder values
- Ensure research completely answers the original question before concluding

---

**Related Commands:**
- After research → `/spec` to define requirements
- After research → `/design-code` or `/design-model` for technical design

**Last Updated**: 2025-10-27

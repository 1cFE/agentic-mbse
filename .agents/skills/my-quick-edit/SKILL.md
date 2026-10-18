---
name: my-quick-edit
description: Implement a small, scoped code change when the user explicitly invokes this skill to bypass the full spec/design/plan process. Do not use for routine documentation or .project artifact edits.
---

Generated from `claude-pack/commands/_my_quick_edit.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Quick Edit Command

**Purpose:** Implement changes and features too small to warrant the full pipeline (see ``my-pipeline``)
**Input:** Direct engagement with user
**Output:** Code changes, optional `.project/active/{feature-name}/change.md`

## Overview

For good software development process, we usually prescribe a methodical pipeline of staged artifacts — specification, design, phased plan, then implementation with progress tracking (``my-pipeline`` has the canonical map).

When the user invokes this command, they wish to abbreviate this process. Your goal as the expert software engineer is to expediently meet the user's interests in executing the task. Follow the workflow below closely.

## Workflow

### Stage 1. Understand Objectives and Context

1. **User Request**
   - Ask the user to describe the edit, task, or feature of interest

2. **Collect Context**
   - Read any files and methods mentioned
   - Navigate the codebase, reading related files as needed until you sufficiently understand how the code works

3. **Process**
   - Once you have a good understanding of the code, think through what needs to be done
   - **IMPORTANT**: the user may overlook certain edge cases or complexities. As the expert, your job is to flag anything that may be more challenging than they realize

4. **Propose**
   - Succinctly summarize
   - Then provide a succinct list of changes that you believe are needed to deliver this (make sure file, component, method are clear)
     - For new methods, include the proposed signature
   - Make sure rationale is clear without being overly verbose
   - Highlight any risks or corner cases you may have concerns about
   - At the end, ask the user if:
     a) you missed anything
     b) they are ready to plan
     c) they want to go straight to implementation
   - If (a), with any new information they provide, go back to Step 2
   - If (b), move to Stage 2
   - If (c), skip straight to Stage 3

### Stage 2. Plan

- In this stage, you need to make sure you have a clear plan for implementation to get sign-off from the user
- Provide a proposal, keeping it easy to follow for the user. E.g. Each step should identify the file, component, and change. Include running tests or scripts as discrete steps
- Iterate with the user until they are happy

### Stage 3. Execute

- Use your internal todo tool to plan out and track the execution of this task
- **IMPORTANT** if you run into any surprises or issues, check with the user before proceeding

### Stage 4. Review and Document

- When your task is completed, review the changes with the user
- Offer to write up the changes in a summary document. If the user accepts:

Get metadata:
```bash
.project/scripts/get-metadata.sh
```

Write to `.project/active/{feature-name}/change.md`:

```markdown
# Feature Change: [Feature Name]

**Status:** Complete
**Owner:** [Git Username]
**Created:** [Date/Time]
**Last Updated:** [Date/Time]
**Git Branch:** [Branch name]
**Git Hash:** [Current Git Commit Hash]

## Overview
[Feature description and value to project]

## Problem Statement
[Bullet point context for the rationale of the change]

## Related Artifacts
[List any other artifacts referenced, like prior specs, research reports, or failing tests]

## Changes
[List the files affected, along with methods/classes/functions and line numbers to reference.
Concisely describe changes made and impact]

## Validation
[Describe steps taken to validate the implementation]
```

---

**Related Commands:**
- For larger changes: enter the full pipeline at ``my-spec`` (run ``my-pipeline`` for the map)
- After changes: ``my-pre-pr`` for quality checks

**Last Updated**: 2026-08-08


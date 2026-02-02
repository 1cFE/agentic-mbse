---
name: formalize-intent
description: Extract structured goals and analysis questions from raw intent documents into OVERVIEW.md
skills: [project-structure]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Formalize Intent Command

**Purpose:** EXTRACT goals (G-XXX) and analysis questions (AQ-XXX) from raw intent documents, turning project prose into the structured entries that drive all downstream modeling work.
**Input:** Documents in `modeling_project/intent/` + existing `modeling_project/OVERVIEW.md`
**Output:** Updated `modeling_project/OVERVIEW.md` (Goals Registry and Analysis Questions tables)

This is the bridge between "why are we doing this project?" and "what must the models do?" Goals and questions formalized here become the demand signal that `/spec-model` reads when scoping work items. Every G-XXX eventually drives modeling requirements (MR-XXX in specs, PR-XXX in project rules). Every AQ-XXX implies structural requirements on the models — if the models can't answer the question, they're incomplete.

Can be triggered by `/onboard` during initial setup or run standalone when new intent documents are added.

When invoked without arguments, scan `modeling_project/intent/` for documents and proceed.

## Skills Referenced

- **project-structure**: 4-directory model, file organization. Consult when understanding where formalized output goes and how it connects to downstream artifacts.

## Process

### 1. Read Intent and Existing State

If the user pointed to specific documents or provided intent directly in conversation, use that as the input. Otherwise, scan all documents in `modeling_project/intent/` — these are user-authored prose (project charters, stakeholder notes, mission statements, meeting summaries). Use Explore agents to process multiple documents in parallel for efficiency.

Read `modeling_project/OVERVIEW.md` to see what's already formalized. For incremental runs, the existing Goals Registry and Analysis Questions tables show what's been extracted before — propose only new entries, not duplicates.

Read `modeling_project/REQUIREMENTS.md` and `modeling_project/ARCHITECTURE.md` for context on what the project has already established. Read `knowledge/KNOWLEDGE.md` for existing DI-XXX domain insights — if insights already relate to the intent documents, surface them during formalization to help the user connect goals to existing knowledge. This helps you understand the current level of formalization and avoid proposing goals that are already captured as requirements, decisions, or insights.

### 2. Extract Candidates

From the intent documents, identify two kinds of entries:

**Goals (G-XXX candidates)** — Statements of what the project must achieve. Look for:
- Explicit objectives ("validate thermal performance", "compare reactor concepts")
- Implicit goals embedded in scope descriptions or success criteria
- Stakeholder needs that translate to modeling deliverables

For each goal candidate, draft: a concise goal statement, a priority (P0-P3), and the source document.

**Analysis Questions (AQ-XXX candidates)** — Questions the models must be able to answer. Look for:
- Explicit questions ("What drives LCOE differences between reactor types?")
- Comparative needs ("how does X affect Y?" → the model must expose both X and Y)
- Decision-support needs ("which concept has the lowest capital cost?" → comparable cost models)

For each question candidate, draft: the question, the source document, and critically — **what it implies for model structure**. This is the "Implies" column and it's where intent becomes actionable:
- "Compare fusion technologies side-by-side" → all designs must share common calculation interfaces; structural library components should inherit shared base types
- "What's the capital vs O&M breakdown?" → LCOE calculation must expose intermediate cost values, not just a final number
- "How does reactor type affect balance-of-plant costs?" → BOP components must be parameterized by reactor type, not hardcoded

Think through the structural consequences. A question that seems simple ("what's the total cost?") may imply significant model structure ("every subsystem needs a cost rollup path"). Surface these implications — they will become MR-XXX requirements in future `/spec-model` runs and eventually PR-XXX project-wide rules.

### 3. Curate with User

Present each candidate to the user. For each G-XXX and AQ-XXX:
- Show the proposed entry (ID, statement/question, priority, source, implies)
- Explain why you extracted it and what it implies for the models
- User decides: **Accept**, **Modify** (edit the statement, priority, or implications), or **Skip**

Group related entries — a goal often has companion analysis questions. Present them together so the user sees the full picture.

If the user identifies goals or questions you missed, add them.

### 4. Register Approved Entries

Call the AP-7 script to register approved entries in OVERVIEW.md:

```bash
agentic-mbse pm register-intent --goals '<structured JSON of approved G-XXX entries>' --questions '<structured JSON of approved AQ-XXX entries>'
```

The script assigns sequential IDs (G-001, G-002... / AQ-001, AQ-002...), enforces the table format, and appends to the correct sections in OVERVIEW.md. The agent does not directly edit the Goals Registry or Analysis Questions tables — the script ensures correct IDs and format.

### 5. Suggest Follow-Up Actions

After registration, suggest next steps based on what was formalized:
- **For AQ-XXX questions**: `/research` to investigate — the question needs domain knowledge before it can become a modeling requirement
- **For actionable G-XXX goals**: `/spec-model` to scope a work item — the goal is clear enough to start modeling
- **For broad G-XXX goals**: `/backlog` to decompose into an epic — the goal spans multiple work items

## Guidelines

- **Think through implications deeply.** The "Implies" column for AQ-XXX and the structural consequences of G-XXX goals are the most valuable output. A goal without implications is just a wish; a goal with clear implications drives concrete modeling requirements.
- Don't create PR-XXX requirements directly — that's the job of `/spec-model` (per-feature MR-XXX) and `/implement-model` (promotion to PR-XXX). This command creates the *demand signal* that those commands consume.
- Handle incremental updates naturally. If OVERVIEW.md already has G-001 through G-003, propose new entries starting conceptually where the previous ones left off. Don't re-propose existing goals.
- Intent documents may be messy — meeting notes, bullet lists, stream-of-consciousness. Extract the signal from the noise. When intent is ambiguous, present your interpretation and let the user correct it.
- Keep goal statements concise and actionable. "Model the power balance" is better than "Create a comprehensive and detailed model of all aspects of the power balance subsystem."
- Source traceability matters. Every G-XXX and AQ-XXX must reference which intent document it came from.

---

**Related Commands:** Triggered by → `/onboard` | Follow-up → `/research` (for AQ-XXX), `/spec-model` (for G-XXX) | Project view → `/status`

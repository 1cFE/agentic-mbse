---
name: onboard
description: Set up a new MBSE project with goals, sources, architecture sketch, and initial backlog
skills: [project-structure, source-traceability, epic-decomposition]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Onboard Command

**Purpose:** SET UP a new project — configure the project structure, establish goals and sources, sketch initial architecture, and create a starting backlog.
**Input:** None (interactive)
**Output:** Populated project files across `knowledge/`, `modeling_project/`, `work/`, and `models/`

Onboarding bridges the gap between `agentic-mbse init` (which creates empty templates) and productive modeling work. By the end, the project has enough context for `/spec-model` to produce meaningful specs.

When invoked, begin with Stage 0.

## Skills Referenced

- **project-structure**: 4-directory model, library vs designs, file organization. Consult when explaining project structure to the user and when populating directory-related content.
- **source-traceability**: SOURCE_INDEX format, source types, citation patterns. Consult when helping the user register authority sources.
- **epic-decomposition**: Scale taxonomy (Trivial/Standard/Epic), decomposition principles. Consult when helping the user create initial backlog items.

## Process

### 0. Version Control Safety

Check if the directory is a git repo (`git rev-parse --git-dir`). If not, offer to initialize one — explain that `git diff` lets the user review all changes made during onboarding.

If it is a repo, check for uncommitted changes to files we'll edit. If any exist, ask the user to commit or stash first, then re-run `/onboard`. Stop here until resolved.

### 1. Discover What Exists

List directory contents. Use Glob to find `*.md`, `models/**/*.sysml`, config files. Report findings to the user — what files exist, what's populated vs template-only, what content directories are present.

Determine the state: fresh (empty templates only), partially configured (some files populated), or fully configured (review and enhance).

### 2. Gather Project Context

Ask the user three questions together (in text, not AskUserQuestion — let them answer naturally):

> **1. What are you modeling?** Describe the system — what it is, its domain, what it does.
>
> **2. What are your goals?** What should the models enable? (e.g., cost analysis, design optimization, requirements traceability)
>
> **3. What sources do you have?** Reference materials — codebases, papers, databases, specs. Include paths or URLs where possible. It's okay to have none yet.

If existing content was found in Stage 1, also ask how it relates to the modeling effort.

Wait for the user to respond before proceeding.

### 3. Configure Sources

If the user listed sources, register them in `knowledge/SOURCE_INDEX.md`. Format entries per the **source-traceability** skill (Name, Type, Location, Use For, Validation).

If sources have file paths, offer to add read permissions to `.claude/settings.json`. See **toolkit-awareness** skill for permission path format rules (use `~/path` format, not absolute paths).

If no sources yet, leave SOURCE_INDEX.md with guidance on adding them later via `/manage-sources`.

### 4. Populate Project Files

Use the user's answers to populate the template files created by `agentic-mbse init`. The **project-structure** skill describes the 4-directory model and what each file is for.

**`modeling_project/OVERVIEW.md`** — Fill in the project summary, scope, and success criteria from the user's answers. Leave the Goals Registry and Analysis Questions tables empty for now — `/formalize-intent` will populate them with proper G-XXX and AQ-XXX entries.

**`modeling_project/ARCHITECTURE.md`** — Write an initial architecture sketch: domain decomposition (what subsystems exist), preliminary package organization (what goes in `library/` vs `designs/`), and any obvious structural decisions from the user's description. Mark all decisions as preliminary — they'll be refined as modeling progresses.

**`knowledge/KNOWLEDGE.md`** — Leave empty (insights come from `/research` and inline capture during modeling).

**`modeling_project/REQUIREMENTS.md`** — Add any obvious project-wide rules from the user's goals (e.g., "all costed components must expose capital_cost" for cost analysis projects). Most requirements emerge during modeling.

**`modeling_project/VALIDATION_MATRIX.md`** — Add any obvious system-level verification criteria. Most entries come from `/spec-model`.

**`work/BACKLOG.md`** — Create an initial epic based on the user's primary goal. Decompose into 3-5 starter work items per the **epic-decomposition** skill. Create the epic file at `work/backlog/epic-{name}.md`.

**`README.md`** — Project name, one-line description, directory structure overview, getting-started pointers.

**`CLAUDE.md`** — System being modeled, domain, goals, key domain concepts and terminology, project structure summary, command workflow overview. Point to `knowledge/SOURCE_INDEX.md` for domain sources.

**`models/`** — Create `library/` and `designs/` subdirectories if they don't exist. Create `models/README.md` describing the structure per **project-structure** skill.

### 5. Intent Formalization

If the user has existing project documents (charters, mission statements, stakeholder notes), guide them to place these in `modeling_project/intent/`.

Suggest running `/formalize-intent` to extract structured G-XXX goals and AQ-XXX analysis questions from these documents into `modeling_project/OVERVIEW.md`. This can be done now or later.

If the user provided clear goals in Stage 2, offer to run `/formalize-intent` immediately to formalize them.

### 6. Summary

Present what was created/modified. Show `git diff` if in a repo. Explain the workflow:

- `/spec-model` to define the first work item's requirements
- `/research` to explore domain sources when knowledge is needed
- `/manage-sources` to add more reference sources
- `/backlog` to manage and prioritize work items

## What Good Output Looks Like

After onboarding, the project should have:

- `knowledge/SOURCE_INDEX.md` with registered authority sources (or guidance for adding them)
- `modeling_project/OVERVIEW.md` with project summary, scope, and placeholders for G-XXX/AQ-XXX
- `modeling_project/ARCHITECTURE.md` with preliminary domain decomposition and package organization
- `work/BACKLOG.md` with an initial epic and 3-5 starter work items
- `README.md` and `CLAUDE.md` with project context
- `models/library/` and `models/designs/` directories ready for use

The depth should match how much context the user provides. A user with detailed goals and sources gets a richer setup than one exploring.

## Guidelines

- Don't skip the git safety check — the user needs `git diff` to review changes
- Don't overwhelm the user — onboarding should feel like a conversation, not a form
- Populate files with real content from the user's answers, not placeholder text
- Mark architectural decisions as preliminary — they're starting points, not commitments
- If the user seems unsure about goals or scope, suggest `/research` before committing to a structure
- Always explain what each file is for when creating it — the user should understand the project layout

---

**Related Commands:** After onboard → `/formalize-intent` for G-XXX/AQ-XXX extraction | `/spec-model` to start modeling | `/manage-sources` to add sources | `/research` for domain exploration

# Onboard Command

**Purpose:** Configure MBSE project and learn the workflow
**Input:** None (interactive)
**Output:** README.md, CLAUDE.md, SOURCE_INDEX.md, models/

## Overview

You are an MBSE onboarding assistant. Your job is to help users:
1. Understand what agentic-mbse does
2. Configure their project for MBSE modeling
3. Learn how to use the MBSE commands

Execute each stage sequentially. Do not skip stages.

---

## Stage 0: Version Control Safety

**Goal:** Ensure user can review changes with `git diff`

### Step 1: Check if git repository

Use Bash to check:
```bash
git rev-parse --git-dir 2>/dev/null
```

**If NOT a git repo:**

Tell the user:
> I notice this directory isn't a git repository. Version control is helpful because:
> - You can review changes I make with `git diff`
> - You can undo changes with `git checkout`
> - You have a history of your modeling work

Use AskUserQuestion:
- Question: "Would you like me to initialize a git repository?"
- Header: "Git Init"
- Options:
  - "Yes, initialize git (default)"
  - "No, continue without git"

If user says yes: run `git init -b main`

If user says no: warn that `git diff` won't work, proceed anyway

### Step 2: Check for uncommitted changes

For files we'll edit (README.md, CLAUDE.md, SOURCE_INDEX.md):
```bash
git status --porcelain README.md CLAUDE.md SOURCE_INDEX.md 2>/dev/null
```

**If any file has uncommitted changes (output not empty):**

Tell user:
> I found uncommitted changes to files I need to edit:
> - {list files with changes}
>
> Please commit or stash these changes first so you can review my edits with `git diff`.
>
> **Commands to resolve:**
> ```bash
> # Option 1: Commit current changes
> git add README.md CLAUDE.md SOURCE_INDEX.md
> git commit -m "Save current state before onboarding"
>
> # Option 2: Stash changes
> git stash
> ```
>
> Run `/onboard` again after resolving.

**STOP HERE - do not proceed until resolved**

---

## Stage 1: Directory Discovery

**Goal:** Understand what's already in this directory

### List Existing Content

Use Bash to list contents:
```bash
ls -la | grep -v "^d.*\\.git$" | grep -v "^d.*\\.claude$" | grep -v "^d.*\\.venv$" | grep -v "^d.*__pycache__$"
```

Also use Glob to find key files:
- `*.md` files
- `models/**/*.sysml`
- `pyproject.toml`, `package.json`
- Any existing source code

### Report findings to user:

> Here's what I found in your project directory:
>
> **Existing files:**
> - {list files found}
>
> **Configuration files:**
> - README.md: {exists | doesn't exist}
> - CLAUDE.md: {exists | doesn't exist}
> - SOURCE_INDEX.md: {exists | template only}
>
> **Other content:**
> - {describe any significant directories or files}

### Determine Directory State

| State | Indicators | Approach |
|-------|------------|----------|
| Fresh (empty) | Only `.claude/`, `SOURCE_INDEX.md` template | Full onboarding flow |
| Has existing content | Other files/directories present | Ask how it relates to modeling |
| Partially configured | Has some of README/CLAUDE/SOURCE_INDEX | Fill gaps, review existing |
| Fully configured | All three files with content | Review and enhance if needed |

---

## Stage 2: Project Context

**Goal:** Gather all context in 3 simple questions

Ask the user these 3 questions together (in text, not using AskUserQuestion):

> I need to understand your project. Please answer these 3 questions:
>
> **1. What are you modeling?**
> Describe the hardware system you want to model - what it is, what it does, its domain.
> (Example: "A compact tokamak fusion reactor for commercial power generation")
>
> **2. What are your goals?**
> What do you want to achieve with this modeling effort?
> (Example: "Techno-economic analysis to estimate cost of electricity")
>
> **3. What sources do you have?**
> List any reference materials - codebases, documentation, databases.
> Include file paths or URLs where possible.
> (Example: "PyFECONS at ~/PyFECONS for physics calculations")
>
> It's okay if you don't have sources yet - you can add them later with `/manage-sources`.

Wait for user to respond with all 3 answers.

### Processing User Responses

After receiving answers:

1. **Parse system description** → Use for:
   - CLAUDE.md system context and domain concepts
   - README overview section

2. **Parse goals** → Use for:
   - README goals section
   - CLAUDE.md workflow priorities

3. **Parse sources** → For each source mentioned:
   - Extract name, type (codebase/documentation/database), and path/URL
   - Add to SOURCE_INDEX.md with appropriate categorization

### If Directory Has Existing Content

If you found existing content in Stage 1 beyond init files, also ask:
> "How does the existing content ({list files}) relate to your modeling effort? Should any of it be referenced in SOURCE_INDEX.md?"

---

## Stage 2.5: Claude Settings for Sources

**Goal:** Help user avoid permission prompts for source paths

If the user provided file paths for sources (e.g., `/home/user/PyFECONS`):

Tell the user:
> I noticed you have sources at these locations:
> - {path1}
> - {path2}
>
> To avoid permission prompts each session, I can add these to `.claude/settings.json`:
>
> ```json
> {
>   "permissions": {
>     "allow": [
>       "Read({path1}/**)",
>       "Read({path2}/**)"
>     ]
>   }
> }
> ```

Use AskUserQuestion:
- Question: "Would you like me to add read permissions for your source paths to .claude/settings.json?"
- Header: "Permissions"
- Options:
  - "Yes, add permissions (recommended)"
  - "No, I'll handle permissions manually"

**If yes:**
- Read existing `.claude/settings.json` if it exists
- Merge new permissions with existing ones
- Write updated settings file

**If no:**
- Proceed without adding permissions
- User will see prompts when accessing source paths

---

## Stage 3: File Generation

**Goal:** Create files that make MBSE commands work effectively

### 3.1 Create README.md

Use the template at `project_templates/README.md.template`, filling in placeholders from conversation:

| Placeholder | Replace With |
|-------------|--------------|
| `<!-- PROJECT_NAME -->` | Project name from conversation |
| `<!-- PROJECT_DESCRIPTION -->` | One-line description: "SysML v2 model of {system} for {goal}" |
| `<!-- PROJECT_STRUCTURE -->` | Directory structure including models/ and any existing directories |

**Example PROJECT_STRUCTURE replacement:**
```
project/
├── models/                  # SysML v2 model files
│   ├── library/             # Reusable definitions
│   └── designs/             # Specific system instances
├── project/                 # Project documentation
├── SOURCE_INDEX.md          # Domain knowledge sources
├── CLAUDE.md                # Context for Claude Code
└── README.md                # This file
```

Customize the structure based on what was discovered in Stage 1.

### 3.2 Create CLAUDE.md

Use this template, filling in from conversation:

```markdown
# CLAUDE.md

## System Being Modeled

**System**: {Hardware system name from conversation}
**Domain**: {Engineering domain - e.g., "Fusion Energy", "Aerospace"}
**Type**: {System type from structured question}

{2-3 sentence description of the system from user's input}

### Modeling Goals

{User's stated goals from the conversation}

### Key Domain Concepts

{From user's "what do you know about the system" response}

Key terminology:
- {Term 1}: {Definition/context}
- {Term 2}: {Definition/context}

Key physics/principles:
- {Principle 1}
- {Principle 2}

Key constraints:
- {Constraint 1}
- {Constraint 2}

## Project Structure

- `models/` - SysML v2 models
  - `library/` - Reusable definitions (part defs, calc defs, materials)
  - `designs/` - Specific system design instances
- `SOURCE_INDEX.md` - **Read this for domain knowledge sources**
{Other directories from discovery - add if found}

## MBSE Workflow

When helping with MBSE tasks:

1. **Always check SOURCE_INDEX.md first** for reference sources
2. **Use `/research` to explore sources** when domain knowledge is needed
3. **Follow the workflow**: spec → design → plan → implement
4. **Validate against sources** using `/audit-models`

### Command Guidance

- `/spec-model`: Help user define clear, testable requirements
- `/design-model`: Create SysML structure that traces to requirements
- `/plan-model`: Break implementation into phases with validation gates
- `/implement-model`: Generate correct SysML v2 syntax
- `/audit-models`: Compare outputs against reference sources

## Domain Sources

**Primary reference**: {Main source name and what it provides}

See `SOURCE_INDEX.md` for complete listing with:
- Source locations (paths/URLs)
- What each source is used for
- How to validate against each source

## Special Considerations

{Any domain-specific notes from user}
{Any gotchas or constraints mentioned}
{Validation requirements if specified}
```

### 3.3 Create/Update SOURCE_INDEX.md

Use this template, populating with sources from conversation:

```markdown
# Source Index

This file tells MBSE commands where to find domain knowledge for {system} modeling.

## Primary Sources

{For each source the user mentioned, create an entry:}

### {Source Name}
- **Type**: {codebase | documentation | database | reference}
- **Location**: {path or URL}
- **Use for**: {What questions/tasks this source helps with}
- **Validation**: {How to verify model outputs against this, or "N/A"}

{Repeat for each source...}

## How MBSE Commands Use This File

When you run commands like `/design-model` or `/audit-models`, they:

1. **Read this file** to discover what reference sources exist
2. **Explore sources** to find relevant patterns, formulas, parameters
3. **Validate outputs** by comparing against authoritative sources

### Source Types Explained

- **codebase**: Source code to extract patterns, formulas, implementations
  - Example: Reference implementation with physics calculations
  - Claude can read and analyze the code

- **documentation**: PDFs, papers, specs that define requirements or physics
  - Example: Design specification, academic paper
  - Claude can read if path is accessible

- **database**: Data files, CSVs, parameter databases
  - Example: Material properties, cost factors
  - Claude can read and extract values

- **reference**: General reference material
  - Example: Standards documents, textbooks
  - Provides context and definitions

### Adding More Sources

Use `/manage-sources` to add, remove, or update sources, or edit this file directly.

Good sources to consider:
- Reference implementations in your domain
- Academic papers defining physics/requirements
- Industry standards or specifications
- Data from similar projects or systems
```

**If user has no sources yet**, use this alternative content for the Primary Sources section:

```markdown
## Primary Sources

No sources configured yet. Add your reference sources here to enable:
- Domain knowledge extraction during `/design-model`
- Validation during `/audit-models`
- Research via `/research`

### Example Entry

```
### PyFECONS Reference Implementation
- **Type**: codebase
- **Location**: /path/to/pyfecons
- **Use for**: Physics equations, cost algorithms, parameter validation
- **Validation**: Compare calculation outputs against PyFECONS results
```

Use `/manage-sources` to add sources interactively.
```

### 3.4 Create models/ Directory

If models/ doesn't exist:
```bash
mkdir -p models/library models/designs
```

Create `models/README.md`:

```markdown
# SysML v2 Models

This directory contains SysML v2 textual models.

## Structure

- `library/` - Reusable definitions
  - Part definitions
  - Calculation definitions
  - Material properties

- `designs/` - Specific system designs
  - System instances
  - Design configurations

## Getting Started

Use `/design-model {feature}` to start creating models.
```

### 3.5 Update Project Templates

The `agentic-mbse init` command created template files in `project/` with `<!-- placeholder -->` comments. Update these files with content from the user's answers:

**Check if project/ files exist.** If they do, update them:

#### Update project/OVERVIEW.md

Find and replace these placeholders with user's answers:

| Placeholder | Replace With |
|-------------|--------------|
| `<!-- Your project name -->` | Project name from conversation |
| `<!-- One-line purpose statement -->` | Brief purpose based on system + goals |
| `<!-- YYYY-MM-DD -->` (Start Date) | Today's date |
| `<!-- your system -->` | System description from Q1 |
| `<!-- TEA, performance analysis, etc. -->` | Primary goal from Q2 |
| `<!-- Your primary design/configuration -->` | First design name (if known) or leave for later |
| `<!-- What you validate against -->` | Primary reference source from Q3 |
| `<!-- Current focus -->` | "Initial setup complete" |
| `<!-- Brief status -->` | "Ready to start modeling" |
| `<!-- What's next -->` | "Run /spec-model to define first feature" |
| `<!-- Name -->` (Project Owner) | User's name if known, or leave as placeholder |

#### Update project/BACKLOG.md

| Placeholder | Replace With |
|-------------|--------------|
| First P0 epic | "Initial Model Development" |
| Goal | User's primary goal from Q2 |
| Scope tasks | Based on system complexity - suggest 3-5 initial tasks |

**Example tasks to suggest based on goal:**
- If TEA/cost analysis: "Define cost calculation framework", "Model key components", "Implement cost rollup"
- If design optimization: "Define design parameters", "Model constraints", "Create parameter sweep"
- If requirements traceability: "Define requirements", "Model system structure", "Create traceability links"

#### project/MODELING_GUIDE.md and project/MODELING_PROCESS.md

These files are methodology guides and don't need user-specific updates. Leave as-is - they provide the SysML v2 syntax patterns (MODELING_GUIDE) and design workflow (MODELING_PROCESS) guidance users need.

**After updating files**, tell the user:

> I've updated the project documentation files with your project context:
> - `project/OVERVIEW.md` - Project overview with your system and goals
> - `project/backlog/BACKLOG.md` - Initial work backlog
>
> Review these files and customize further as needed.

---

## Stage 4: Summary & Education

**Goal:** Confirm what was done and help user understand next steps

Present this summary to the user:

---

## Onboarding Complete!

### Files Created/Modified

- **README.md** - Project overview and MBSE workflow guide
- **CLAUDE.md** - Domain context for Claude Code
- **SOURCE_INDEX.md** - {N} reference sources configured (or "guidance for adding sources")
- **models/** - Directory structure for SysML models
- **project/OVERVIEW.md** - Project overview (updated with your context)
- **project/BACKLOG.md** - Work backlog (updated with initial tasks)
- **project/MODELING_GUIDE.md** - SysML v2 syntax patterns guide
- **project/MODELING_PROCESS.md** - MBSE workflow and methodology guide

### Review Your Changes

You can see exactly what I changed:
```bash
git diff
```

If you're happy with the changes:
```bash
git add -A
git commit -m "Configure MBSE project with onboarding"
```

### Understanding the MBSE Workflow

You now have access to these commands:

```
┌─────────────────────────────────────────────────────────────┐
│                    MBSE Workflow                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  /spec-model {feature}                                      │
│       │                                                     │
│       ▼                                                     │
│  /design-model {feature}                                    │
│       │                                                     │
│       ▼                                                     │
│  /plan-model {feature}                                      │
│       │                                                     │
│       ▼                                                     │
│  /implement-model {feature}                                 │
│       │                                                     │
│       ▼                                                     │
│  /audit-models ─────────────► Validates against             │
│                               SOURCE_INDEX.md sources       │
│                                                             │
│  /research ─────────────────► Explores sources when         │
│                               you need information          │
└─────────────────────────────────────────────────────────────┘
```

### Suggested First Steps

1. **Review the generated files** - Make sure they capture your project correctly
2. **Check SOURCE_INDEX.md** - Ensure your reference sources are listed
3. **Start modeling** - Run `/spec-model {your-first-feature}` to begin

### Need Help?

- `/research` - Explore your domain sources for information
- `/manage-sources` - Add or update reference sources
- Edit files directly - README.md, CLAUDE.md, SOURCE_INDEX.md are just markdown

You're ready to start MBSE modeling!

---

## Edge Cases Reference

| Scenario | Detection | Handling |
|----------|-----------|----------|
| Not a git repo | `git rev-parse` fails | Offer to init with `-b main`, explain benefits |
| Uncommitted changes | `git status --porcelain` non-empty | STOP, ask to commit/stash |
| User declines git | User selects "No" | Warn about no diff, proceed |
| Empty directory | Only `.claude/`, template SOURCE_INDEX | Full flow, skip existing content question |
| Has existing content | Other files/dirs found | Ask how it relates in Stage 2 |
| Has existing README/CLAUDE | Files exist with content | Read first, propose enhancements |
| No sources listed | User has none | Create guidance-focused SOURCE_INDEX, skip Stage 2.5 |
| Sources with file paths | Paths like `/home/...` | Offer to add permissions in Stage 2.5 |
| User new to MBSE | Unclear on terminology | Extra explanation, simpler language |

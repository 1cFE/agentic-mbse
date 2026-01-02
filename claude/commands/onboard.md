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

If user says yes: run `git init`

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

## Stage 2: Domain Context Gathering

**Goal:** Understand what the user is modeling and what sources they have

### Question Set 1: The System (Structured)

Use AskUserQuestion with BOTH questions together:

Question 1:
- Question: "What type of hardware system do you want to model?"
- Header: "System Type"
- Options:
  - "Energy system (fusion, fission, solar, battery) (default)"
  - "Aerospace system (satellite, rocket, aircraft)"
  - "Industrial system (manufacturing, process plant)"
  - "Other"

Question 2:
- Question: "What's your primary goal for modeling this system?"
- Header: "Goal"
- Options:
  - "Techno-economic analysis (TEA) (default)"
  - "Design optimization"
  - "Requirements traceability"
  - "System validation"

### Question Set 2: System Details (Conversational)

After structured questions, ask conversationally:

1. "Can you describe the specific system you're modeling in a few sentences?"
   - Example: "A compact tokamak fusion reactor for commercial power generation"
   - Used for: README overview, CLAUDE.md system description

2. "What do you already know about this system?"
   - Prompts to offer:
     - Physical principles / governing equations?
     - Design specifications or requirements?
     - Key components or subsystems?
     - Performance targets or constraints?
   - Used for: CLAUDE.md domain concepts

3. "What's the most important thing you want to get out of this modeling effort?"
   - Used for: README goals, guides command priorities

### Question Set 3: Reference Sources (Critical)

Explain why this matters:
> MBSE commands like `/design-model` and `/audit-models` need reference sources to:
> - Extract domain knowledge (formulas, parameters, patterns)
> - Validate model outputs against authoritative baselines
> - Research how similar systems are implemented

Ask about each source type:

**Codebases:**
> "Do you have any reference **codebases** I should know about?"
> Examples: "PyFECONS for fusion physics", "OpenMDAO for optimization"

For each codebase, ask:
- What is it?
- Where is it? (path or URL)
- What do I use it for?
- Can I validate against it?

**Documentation:**
> "Do you have any **documentation** - papers, specs, standards?"
> Examples: "ITER Physics Basis PDF", "System requirements document"

For each document, ask:
- What is it?
- Where is it?
- What does it define?

**Data sources:**
> "Do you have any **data sources** - databases, parameter files?"
> Examples: "Material properties database", "Cost factor spreadsheet"

For each data source, ask:
- What is it?
- Where is it?
- What parameters does it contain?

**If user has no sources yet:**
> That's okay! You can add sources later with `/manage-sources`.
>
> For now, I'll create SOURCE_INDEX.md with guidance on what makes good sources.
>
> Common sources to consider:
> - Reference implementations in your domain
> - Academic papers defining the physics/requirements
> - Industry standards or specifications
> - Existing data from similar projects

### Question Set 4: Existing Content (If Applicable)

If directory has content beyond init files:

> "I see you have some existing content in this directory. Can you tell me about it?"
> - {list what we found}
> - How does this relate to the modeling effort?
> - Should any of this be referenced in SOURCE_INDEX.md?
> - Are there any directories I should know about?

---

## Stage 3: File Generation

**Goal:** Create files that make MBSE commands work effectively

### 3.1 Create README.md

Use this template, filling in from conversation:

```markdown
# {Project Name}

{One-line description}: SysML v2 model of {system} for {goal}.

## What This Project Does

This project uses **Model-Based Systems Engineering (MBSE)** to model {system description from conversation}.

Using SysML v2 and the agentic-mbse toolkit, you can:
- Define formal models of system structure and behavior
- Trace requirements to design elements
- Validate designs against reference sources
- {Goal-specific benefit based on user's stated goal}

### Modeling Goals

{User's stated goals from conversation - what they want to get out of modeling}

## Getting Started

### MBSE Commands

This project includes AI-assisted commands for the complete MBSE workflow:

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/spec-model` | Define what to model | Starting a new model feature |
| `/design-model` | Design model structure | After spec, before implementation |
| `/plan-model` | Plan implementation phases | Complex features needing phasing |
| `/implement-model` | Create SysML files | Ready to write actual models |
| `/audit-models` | Validate against sources | Verify correctness |
| `/research` | Explore domain sources | Need information from references |

### Typical Workflow

```
1. /spec-model {feature}     → Define requirements
2. /design-model {feature}   → Design the model
3. /plan-model {feature}     → Plan implementation
4. /implement-model {feature} → Generate SysML files
5. /audit-models             → Validate results
```

### First Steps

1. Review `SOURCE_INDEX.md` - ensure your reference sources are listed
2. Run `/spec-model {first-feature}` to start defining your first model
3. Follow the workflow through design → plan → implement

## Project Structure

```
{project}/
├── models/                  # SysML v2 model files
│   ├── library/             # Reusable definitions (part defs, calc defs)
│   └── designs/             # Specific system instances
├── SOURCE_INDEX.md          # Domain knowledge sources (CRITICAL)
├── CLAUDE.md                # Context for Claude Code
├── README.md                # This file
└── .claude/commands/        # MBSE slash commands
```

## Domain Sources

This project draws from the following reference sources:

{List sources from SOURCE_INDEX.md - name and brief purpose for each}

See `SOURCE_INDEX.md` for details on each source.

## Learn More

- **MBSE Workflow**: The commands guide you through spec → design → plan → implement
- **SysML v2**: Models use the SysML v2 textual notation
- **Validation**: Use `/audit-models` to verify against reference sources
```

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
| Not a git repo | `git rev-parse` fails | Offer to init, explain benefits |
| Uncommitted changes | `git status --porcelain` non-empty | STOP, ask to commit/stash |
| User declines git | User selects "No" | Warn about no diff, proceed |
| Empty directory | Only `.claude/`, template SOURCE_INDEX | Full flow, no existing content questions |
| Has existing content | Other files/dirs found | Ask how it relates, incorporate |
| Has existing README/CLAUDE | Files exist with content | Read first, propose enhancements |
| No sources identified | User has none yet | Create guidance-focused SOURCE_INDEX |
| User new to MBSE | Unclear on terminology | Extra explanation, simpler language |

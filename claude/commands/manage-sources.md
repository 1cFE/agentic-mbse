# Manage Sources Command

**Purpose:** Add or remove sources from SOURCE_INDEX.md
**Input:** None (interactive)
**Output:** Updated SOURCE_INDEX.md

## Overview

You are a source management assistant for MBSE projects. Help users maintain their SOURCE_INDEX.md file, which tells MBSE commands where to find domain knowledge.

When invoked:
- Read current SOURCE_INDEX.md state
- Determine what action user wants
- Execute the action (add, remove, or view)
- Confirm changes

---

## Process

### Stage 1: Read Current State

**Check if SOURCE_INDEX.md exists:**

Use Glob or Read to check:
```
SOURCE_INDEX.md
```

**If SOURCE_INDEX.md doesn't exist:**
```
I don't see a SOURCE_INDEX.md file in this project.

This file is essential for MBSE commands - it tells them where to find domain knowledge.

Would you like to:
1. Run `/onboard` to set up your project (recommended for new projects)
2. Create a minimal SOURCE_INDEX.md here

**Use AskUserQuestion:**
Question: "How would you like to proceed?"
Header: "Setup"
Options:
  - "Run /onboard for full project setup (default)"
  - "Create minimal SOURCE_INDEX.md here"
```

**If SOURCE_INDEX.md exists:**

Parse the file to identify:
- Number of sources defined
- Source names, types, and locations
- Overall structure

Report to user:
```
Found SOURCE_INDEX.md with {N} source(s):

{For each source:}
  • {Name} ({type}) - {location}

What would you like to do?
```

---

### Stage 2: Determine Action

**Use AskUserQuestion:**
Question: "What would you like to do with your sources?"
Header: "Action"
Options:
  - "Add a new source (default)"
  - "Remove an existing source"
  - "View source details"

---

### Stage 3: Execute Action

#### Option A: Add a New Source

**Step 1 - Source Type:**
```
**Use AskUserQuestion:**
Question: "What type of source are you adding?"
Header: "Source Type"
Options:
  - "Codebase - source code to extract patterns, formulas, implementations (default)"
  - "Documentation - PDFs, papers, specs that define requirements or physics"
  - "Database - data files, CSVs, parameter databases"
  - "Reference - general reference material, standards, textbooks"
```

**Step 2 - Source Details (Conversational):**
Ask the user:

1. "What's the name of this source?"
   - Example: "PyFECONS", "ITER Physics Basis", "Material Properties DB"

2. "Where is it located?"
   - For codebases: path like `/home/user/project` or URL like `https://github.com/...`
   - For documentation: path to file or URL
   - For databases: path to file(s)
   - For reference: path, URL, or "N/A" if conceptual

3. "What should I use this source for?"
   - What questions/tasks does this source help answer?
   - What domain knowledge does it contain?
   - Example: "Extract physics formulas for plasma confinement"

4. "How can I validate model outputs against this source?"
   - If codebase: "Compare calculation results to function outputs"
   - If documentation: "Check parameters match spec values"
   - If database: "Verify values fall within database ranges"
   - Or: "N/A" if validation not applicable

**Step 3 - Validate Location:**
```bash
# For local paths, check if location exists
ls -la {location} 2>/dev/null
```

If location doesn't exist:
```
Note: I couldn't verify the location "{location}" exists.
This might be fine if:
  - It's a URL you'll access later
  - The path will be created
  - It's on a different machine

Proceeding anyway - you can update it later.
```

**Step 4 - Append to SOURCE_INDEX.md:**

Read current SOURCE_INDEX.md content, then append new source under "## Primary Sources":

```markdown
### {Source Name}
- **Type**: {type}
- **Location**: {location}
- **Use for**: {use-for description}
- **Validation**: {validation approach}
```

Use Edit tool to add the new source section.

**Step 5 - Confirm:**
```
Added "{Source Name}" to SOURCE_INDEX.md.

You now have {N} source(s) configured.

This source will be available to commands like:
  - `/design-model` - for extracting patterns and formulas
  - `/audit-models` - for validating outputs
  - `/research` - for exploring domain knowledge
```

---

#### Option B: Remove an Existing Source

**Step 1 - List Sources:**
```
Current sources in SOURCE_INDEX.md:

1. {Source 1 Name} ({type})
2. {Source 2 Name} ({type})
3. {Source 3 Name} ({type})
...

Which source would you like to remove?
```

**Use AskUserQuestion** with numbered options:
Question: "Which source do you want to remove?"
Header: "Remove"
Options:
  - "{Source 1 Name} (default)"
  - "{Source 2 Name}"
  - "{Source 3 Name}"
  - (up to 4 options based on sources)

If more than 4 sources, ask conversationally: "Enter the name of the source to remove"

**Step 2 - Confirm Removal:**
```
**Use AskUserQuestion:**
Question: "Are you sure you want to remove '{Source Name}'?"
Header: "Confirm"
Options:
  - "Yes, remove it (default)"
  - "No, keep it"
```

**Step 3 - Remove from File:**

Use Edit tool to remove the entire source section (from `### {Name}` to next `###` or section end).

**Step 4 - Confirm:**
```
Removed "{Source Name}" from SOURCE_INDEX.md.

You now have {N} source(s) configured.

Note: If you need this source again later, you can add it back with `/manage-sources`.
```

---

#### Option C: View Source Details

**List all sources with full details:**
```
## Source Details

### {Source 1 Name}
- **Type**: {type}
- **Location**: {location}
- **Use for**: {use-for}
- **Validation**: {validation}

### {Source 2 Name}
...

---

Would you like to:
- Add a source → `/manage-sources` and select "Add"
- Edit a source → Edit SOURCE_INDEX.md directly
- Remove a source → `/manage-sources` and select "Remove"
```

---

### Stage 4: Offer Next Steps

After any action completes:

```
---

**What's next?**

- Add another source: Run `/manage-sources` again
- Start modeling: Run `/spec-model {feature}` to begin
- Research sources: Run `/research {topic}` to explore your sources
- Edit manually: Open SOURCE_INDEX.md in your editor
```

---

## Edge Cases

| Scenario | Detection | Handling |
|----------|-----------|----------|
| No SOURCE_INDEX.md | File not found | Offer /onboard or create minimal |
| Empty SOURCE_INDEX.md | File exists but no sources parsed | Treat as 0 sources, proceed normally |
| Invalid source format | Can't parse existing sources | Report issue, suggest manual edit |
| Location doesn't exist | ls/stat fails | Warn but don't block |
| Duplicate source name | Name already exists | Warn, ask for different name |
| User cancels mid-flow | Selects cancel/back option | Return to action selection |

---

## SOURCE_INDEX.md Format Reference

Sources should follow this format:

```markdown
# Source Index

This file tells MBSE commands where to find domain knowledge.

## Primary Sources

### {Source Name}
- **Type**: {codebase | documentation | database | reference}
- **Location**: {path or URL}
- **Use for**: {what this source helps with}
- **Validation**: {how to verify against this source, or N/A}

### {Another Source}
...

## How MBSE Commands Use This File
...
```

---

## Minimal SOURCE_INDEX.md Template

If user chooses to create minimal file (instead of /onboard):

```markdown
# Source Index

This file tells MBSE commands where to find domain knowledge sources.

## Primary Sources

(No sources configured yet. Use `/manage-sources` to add sources.)

## How MBSE Commands Use This File

When you run commands like `/design-model` or `/audit-models`, they:

1. **Read this file** to discover what reference sources exist
2. **Explore sources** to find relevant patterns, formulas, parameters
3. **Validate outputs** by comparing against authoritative sources

### Source Types

- **codebase**: Source code to extract patterns, formulas, implementations
- **documentation**: PDFs, papers, specs that define requirements or physics
- **database**: Data files, CSVs, parameter databases
- **reference**: General reference material, standards, textbooks

### Adding Sources

Run `/manage-sources` to add your first source, or edit this file directly.
```

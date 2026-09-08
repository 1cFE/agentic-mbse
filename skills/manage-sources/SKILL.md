---
name: manage-sources
description: Add, remove, or review authority sources in SOURCE_INDEX.md
allowed-tools: [Read, Grep, Glob, Bash, Agent, Write, Edit, AskUserQuestion]
user-invocable: true
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Manage Sources Command

**Purpose:** Configure SOURCES — add, remove, or review authority sources that MBSE commands use for domain knowledge. **Input:** None (interactive) **Output:** Updated `knowledge/SOURCE_INDEX.md` (and optionally native read-access settings)

SOURCE_INDEX.md is the registry of authority sources for the project. Commands like `/research`, `/design-model`, and `/audit-models` read it to discover what domain knowledge is available.

When invoked, begin by reading the current state.

## Skills Referenced

- **source-traceability**: SOURCE_INDEX format, source types (codebase/documentation/database/reference), citation patterns. Consult for entry format and source type definitions when adding or reviewing sources.

## Process

### 1. Read Current State

Check if `knowledge/SOURCE_INDEX.md` exists.

**If it doesn't exist:** Offer two options via the host question interface — run `/onboard` for full project setup (recommended for new projects) or create a minimal SOURCE_INDEX.md here.

**If it exists:** Parse the file, report the number of sources with a brief listing (name, type, location for each), and ask what action the user wants.

### 2. Determine Action

Use the host question interface with options: Add a new source, Remove an existing source, View source details.

### 3. Execute Action

#### Add a Source

Gather details conversationally:
1. **Source type** — use the host question interface with the four types from the **source-traceability** skill
2. **Name** — what to call this source
3. **Location** — file path or URL
4. **Use for** — what domain knowledge it provides
5. **Validation** — how to verify model outputs against it (or N/A)

Validate the location if it's a local path (`ls -la {location}`). Warn but don't block if it doesn't exist.

Append the new entry to `knowledge/SOURCE_INDEX.md` formatted per the **source-traceability** skill.

**Offer access for local paths.** Follow the current assistant adapter’s external-source instructions. In Claude, offer to merge read permissions into existing settings. In Codex, check access under the active sandbox and use its approval path when needed; preserve owner configuration.

Confirm: report the addition and how many sources are now configured.

#### Remove a Source

List sources by number. Use the host question interface to select which one (or ask conversationally if more than 4). Confirm removal. Use Edit to remove the section from `knowledge/SOURCE_INDEX.md`. Report the result.

#### View Source Details

Display all sources with full details. Offer next steps: add, edit directly, or remove.

### 4. Next Steps

After any action, suggest:
- Add another source: run `/manage-sources` again
- Start modeling: `/spec-model`
- Research sources: `/research`
- Edit manually: open `knowledge/SOURCE_INDEX.md` in your editor

## Guidelines

- Always read `knowledge/SOURCE_INDEX.md` before making changes — don't assume its state
- Format entries per the **source-traceability** skill — consistent format enables other commands to parse sources reliably
- Warn on duplicate source names
- Warn but don't block on unresolvable locations — the path may be on another machine or not yet created
- If creating a minimal SOURCE_INDEX.md (no `/onboard`), include the "How MBSE Commands Use This File" guidance section

---

**Related Commands:** For full project setup → `/onboard` | To explore sources → `/research` | To audit against sources → `/audit-models`

# Design: Init File Ownership

| Field | Value |
|-------|-------|
| Status | Implemented |
| Owner | reid |
| Created | 2025-01-10 |
| Branch | 1cfe_dev |
| Commit | 839bac0 |

## Overview

Modify `agentic-mbse init` to distinguish between user-owned files (customized by users) and tool-owned files (managed by the tool), so that re-running `init` updates tool files while preserving user customizations.

## Related Artifacts

- Source request: User conversation about updating MODELING_GUIDE in fusion-tea project
- No formal spec exists - this design documents the feature from user request

## Business Goals

1. Users can update their projects with latest tool improvements by re-running `init`
2. User customizations (OVERVIEW.md, SOURCE_INDEX.md, etc.) are never accidentally overwritten
3. Clear feedback showing what was updated vs. preserved

## Research Findings

### Files Analyzed

**`src/agentic_mbse/cli/__init__.py`** - Main implementation file

Current structure:
- `MBSE_COMMANDS` (lines 14-24): List of command files
- `MBSE_AGENTS` (lines 27-30): List of agent files
- `MBSE_SKILLS` (lines 33-35): List of skill directories
- `MBSE_HOOKS` (lines 38-40): List of hook files
- `PROJECT_TEMPLATES` (lines 43-49): List of (template, dest) tuples

Current `cmd_init` behavior (lines 182-430):
- All files treated identically
- Skip if exists, overwrite only with `--force`
- Tracks `created` and `skipped` lists for summary output

### Identified File Categories

Based on intended usage patterns:

| Category | Files | Rationale |
|----------|-------|-----------|
| **User-owned** | `.gitignore`, `SOURCE_INDEX.md`, `README.md`, `project/OVERVIEW.md`, `project/backlog/BACKLOG.md`, `.claude/settings.json` | Users customize these with project-specific content (settings.json may have user-added permissions) |
| **Tool-owned** | All commands, agents, skills, hooks, `MODELING_GUIDE.md`, `MODELING_PROCESS.md` | Tool manages these; users should get updates |

### Patterns to Reuse

- Existing file copy logic at lines 303-312 (commands), 319-331 (agents)
- Template processing at lines 371-381
- Summary output format at lines 408-429

## Proposed Design

### High-Level Architecture

```
cmd_init()
    │
    ├── Process user-owned files (skip if exists)
    │   ├── .gitignore
    │   ├── SOURCE_INDEX.md
    │   ├── .claude/settings.json
    │   └── USER_OWNED_TEMPLATES
    │
    ├── Process tool-owned files (always update)
    │   ├── MBSE_COMMANDS
    │   ├── MBSE_AGENTS
    │   ├── MBSE_SKILLS
    │   ├── MBSE_HOOKS
    │   └── TOOL_OWNED_TEMPLATES
    │
    └── Print summary (created / updated / skipped)
```

### Data Structures

**New constants** (replace `PROJECT_TEMPLATES` at line 43):

```python
# User-owned templates: only initialize, never auto-update
USER_OWNED_TEMPLATES = [
    ("README.md.template", "README.md"),
    ("OVERVIEW.md.template", "project/OVERVIEW.md"),
    ("BACKLOG.md.template", "project/backlog/BACKLOG.md"),
]

# Tool-owned templates: auto-update on every init
TOOL_OWNED_TEMPLATES = [
    ("MODELING_GUIDE.md.template", "project/MODELING_GUIDE.md"),
    ("MODELING_PROCESS.md.template", "project/MODELING_PROCESS.md"),
]

# Combined for backwards compatibility (if needed elsewhere)
PROJECT_TEMPLATES = USER_OWNED_TEMPLATES + TOOL_OWNED_TEMPLATES
```

**New tracking lists** in `cmd_init`:

```python
created: list[str] = []   # New files (didn't exist before)
updated: list[str] = []   # Tool-owned files refreshed
skipped: list[str] = []   # User-owned files preserved
```

### Modified Logic

#### User-owned file handling

For `.gitignore`, `SOURCE_INDEX.md`, `.claude/settings.json`, and `USER_OWNED_TEMPLATES`:

```python
if dst.exists() and not args.force:
    skipped.append(item_name)
else:
    existed = dst.exists()
    # ... write file ...
    if existed:
        updated.append(item_name)  # Only happens with --force
    else:
        created.append(item_name)
```

#### Tool-owned file handling

For commands, agents, skills, hooks, and `TOOL_OWNED_TEMPLATES`:

```python
# No existence check - always write
existed = dst.exists()
# ... write file ...
if existed:
    updated.append(item_name)
else:
    created.append(item_name)
```

### Output Format

```
Initialized MBSE project in /path/to/project

Created (2):
  + .gitignore
  + SOURCE_INDEX.md

Updated (13) - tool-managed files refreshed:
  ~ .claude/commands/design-model.md
  ~ .claude/commands/plan-model.md
  ~ project/MODELING_GUIDE.md
  ...

Skipped (4) - user files preserved:
  . README.md
  . project/OVERVIEW.md
  . project/backlog/BACKLOG.md
  . .claude/settings.json
```

### Files to Modify

| File | Changes |
|------|---------|
| `src/agentic_mbse/cli/__init__.py` | Replace `PROJECT_TEMPLATES`, modify `cmd_init()`, update `--force` help text |
| `CLAUDE.md` | Add "Init File Ownership" section documenting user-owned vs tool-owned files |

### Detailed Changes

**Lines 43-49**: Replace `PROJECT_TEMPLATES` with split lists

**Lines 205-207**: Change tracking from 2 lists to 3:
```python
created: list[str] = []
updated: list[str] = []  # NEW
skipped: list[str] = []
```

**Lines 209-270** (`.gitignore`): Add `existed` tracking, categorize output

**Lines 272-297** (`SOURCE_INDEX.md`): Add `existed` tracking, categorize output

**Lines 299-312** (commands): Remove existence check, always copy, track as updated/created

**Lines 314-331** (agents): Remove existence check, always copy, track as updated/created

**Lines 333-346** (skills): Remove existence check, always copy, track as updated/created

**Lines 348-362** (hooks): Remove existence check, always copy, track as updated/created

**Lines 371-381** (templates): Split into two loops - one for `USER_OWNED_TEMPLATES` (skip if exists), one for `TOOL_OWNED_TEMPLATES` (always update)

**Lines 383-406** (settings.json): Keep existence check (user-owned), skip if exists unless `--force`

**Lines 408-429** (summary): Add "Updated" section to output

**Line 531**: Update `--force` help text to clarify it affects user-owned files

**CLAUDE.md**: Add new section documenting the ownership strategy:

```markdown
## Init File Ownership

When adding new files to `cmd_init()`, categorize them as:

| Category | Behavior | Examples |
|----------|----------|----------|
| **User-owned** | Create once, skip on re-init (preserve customizations) | `SOURCE_INDEX.md`, `OVERVIEW.md`, `BACKLOG.md`, `README.md`, `.gitignore`, `.claude/settings.json` |
| **Tool-owned** | Always update on re-init (get latest versions) | Commands, agents, skills, hooks, `MODELING_GUIDE.md`, `MODELING_PROCESS.md` |

Use `--force` to overwrite user-owned files.
```

## Potential Risks

| Risk | Mitigation |
|------|------------|
| Users expect `init` to be idempotent (no changes if run twice) | Clear output showing what was "updated" makes behavior transparent |
| Breaking change for users who modified tool-owned files | These files aren't meant to be modified; if users have, `--force` wasn't protecting them anyway since they'd need to re-run init eventually |
| New permissions needed but settings.json already exists | User must manually add permissions or use `--force` (acceptable trade-off for preserving user customizations) |

## Integration Strategy

- This modifies the existing `init` command, no new commands needed
- `replicate_setup.sh` is separate and doesn't need changes (it's for development, not user projects)
- No changes to validation, other CLI commands, or Claude integration

## Validation Approach

### Automated Testing

Add tests to `tests/test_cli.py`:

1. **Test user-owned files skipped on re-init**:
   - Run init, modify a user-owned file, run init again
   - Verify user file unchanged, tool files updated

2. **Test tool-owned files updated on re-init**:
   - Run init, run init again
   - Verify tool files are in "updated" list

3. **Test --force overwrites user files**:
   - Run init, modify user file, run init --force
   - Verify user file overwritten

### Manual Verification

1. Run `agentic-mbse init` on fresh directory → all files created
2. Run `agentic-mbse init` again → tool files updated, user files skipped
3. Modify `SOURCE_INDEX.md`, run init → SOURCE_INDEX.md preserved
4. Run `agentic-mbse init --force` → all files overwritten

---

**Next Step**: After approval → `/_my_implement`

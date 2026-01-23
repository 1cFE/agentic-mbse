# Spec: Tool-Owned File Safety

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-23 17:13 UTC
**Complexity:** MEDIUM
**Branch:** 1cfe_dev
**Backlog Item:** ITEM-SYMLINK-001

---

## Business Goals

### Why This Matters

Tool-owned files (MODELING_GUIDE.md, MODELING_PROCESS.md, commands, agents) are managed by agentic-mbse but users may add valuable local customizations - validated patterns, project-specific guidance, domain knowledge. Currently, re-running `init` can silently overwrite these customizations:

- **`--dev` mode**: Files are removed from git and replaced with symlinks
- **Normal mode**: Tool-owned files are always overwritten on re-init

This happened in fusion-tea where local additions to MODELING_GUIDE.md (validated patterns with dates and evidence) were lost when switching to dev mode. While the *content* was separately backported to agentic-mbse's `docs/patterns/`, the local file was deleted without warning.

### Success Criteria

- [ ] Users have a dedicated space for local customizations that won't be overwritten
- [ ] In `--dev` mode, edits to tool-owned files go directly to agentic-mbse source (bidirectional)
- [ ] In normal mode, users are warned before tool-owned files with local modifications are overwritten
- [ ] No content loss occurs during the implementation (audit confirms all fusion-tea content was ported)

### Priority

P1 - Prevents data loss and improves developer experience for both modes.

---

## Problem Statement

### Current State

**`--dev` mode behavior:**
- Commands, agents, skills, hooks → symlinked (good)
- MODELING_GUIDE.md, MODELING_PROCESS.md → symlinked (good, but transition lost local changes)
- No local customization space exists

**Normal mode behavior:**
- All tool-owned files are copied fresh on every `init`
- No detection of local modifications
- User customizations silently overwritten

**What was lost in fusion-tea (commit ef11ada):**
- Local additions to `project/MODELING_GUIDE.md` from commit `a103596`:
  - "Cost Model Imports" section (NumericalFunctions::sum)
  - "Multiplicity Cost Aggregation Pattern" with validation date/evidence
  - "Part Redefinition Pattern" (dot notation vs explicit redefines)
  - "Parameterized Multiplicity Pattern"
- These patterns exist in `docs/patterns/` now, but with different formatting

### Desired Outcome

1. **Local customization space**: A user-owned file where project-specific patterns and guidance can live without being overwritten
2. **`--dev` mode**: All tool-owned files symlinked - edits flow to agentic-mbse source for easy backporting
3. **Normal mode**: Detect local modifications to tool-owned files and warn before overwriting

---

## Scope

### In Scope

1. **Audit fusion-tea history** (implementation phase):
   - Review commits around ef11ada, 4590874, 6ab7b7d
   - Verify all local content was properly backported to agentic-mbse
   - Document any gaps found

2. **Local customization space**:
   - Add `LOCAL_GUIDE.md` template to `modeling_pm/` (user-owned)
   - Document its purpose: project-specific patterns, validated findings, backport candidates
   - Reference it from MODELING_GUIDE.md

3. **`--dev` mode improvements**:
   - Ensure ALL tool-owned files are symlinked (verify current behavior)
   - Document that edits flow to source repo

4. **Normal mode modification detection**:
   - Before overwriting a tool-owned file, compare to expected content
   - If different, warn user and offer options (skip, backup, force)
   - Track expected content via hash or template comparison

### Out of Scope

- Automatic merge of local changes with updated templates
- Migration tooling for existing projects
- Changes to user-owned file handling (already skip-if-exists)

### Edge Cases & Considerations

- **First init**: No existing files, no detection needed
- **Re-init after template update**: File differs because template changed, not local edit - need to distinguish
- **Multiple edits**: User may have edited multiple tool-owned files
- **Partial dev mode**: What if user runs `--dev` on a project that was previously normal mode?

---

## Requirements

### Functional Requirements

1. **FR-1**: `agentic-mbse init` MUST create `modeling_pm/LOCAL_GUIDE.md` as a user-owned file for project-specific customizations
2. **FR-2**: In `--dev` mode, ALL tool-owned files (commands, agents, skills, hooks, MODELING_GUIDE.md, MODELING_PROCESS.md) MUST be symlinked to agentic-mbse source
3. **FR-3**: In normal mode, before overwriting a tool-owned file that exists, the init command MUST check if the file has been modified from its original installed content
4. **FR-4**: If a tool-owned file has local modifications (normal mode), the init command MUST warn the user and offer options: skip this file, backup and overwrite, or force overwrite
5. **FR-5**: [INFERRED] A mechanism MUST exist to track the "original" content of tool-owned files for modification detection (e.g., hash file, marker comment)
6. **FR-6**: During implementation, a thorough audit of fusion-tea git history MUST be performed to verify no content was lost

### Non-Functional Requirements

- **NFR-1**: Modification detection SHOULD NOT significantly slow down init (< 1 second overhead)
- **NFR-2**: The warning message SHOULD clearly explain what was modified and recommend backing up

---

## Acceptance Criteria

### Core Functionality

- [ ] `agentic-mbse init` creates `modeling_pm/LOCAL_GUIDE.md` with template explaining its purpose
- [ ] `LOCAL_GUIDE.md` is user-owned (skipped if exists on re-init)
- [ ] `--dev` mode symlinks all tool-owned files including templates
- [ ] Normal mode detects modifications to tool-owned files before overwriting
- [ ] Warning is displayed with options when local modifications detected
- [ ] User can skip individual files, backup and overwrite, or force

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] New tests cover modification detection logic
- [ ] Audit report documents fusion-tea content verification

---

## Design Considerations

### Modification Detection Approaches

**Option A: Hash file**
- Store `.claude/.tool-hashes.json` with SHA256 of each tool-owned file at install time
- On re-init, compare current file hash to stored hash
- Pros: Simple, reliable
- Cons: Another file to manage

**Option B: Template marker comment**
- Add comment at end of tool-owned files: `<!-- agentic-mbse:v1.2.3:sha256abc123 -->`
- Check marker on re-init
- Pros: Self-contained
- Cons: Modifying source files, fragile if user deletes marker

**Option C: Content comparison to template**
- Compare current file content to template (with placeholder substitution)
- If different, assume modified
- Pros: No extra files or markers
- Cons: Can't distinguish "user edited" from "template updated since install"

**Recommendation**: Option A (hash file) - cleanest separation of concerns.

### LOCAL_GUIDE.md Template

```markdown
# Local Modeling Guide

Project-specific patterns, validated findings, and customizations for this modeling project.

**Purpose**: This file is for YOUR project's unique patterns and lessons learned. It won't be overwritten by `agentic-mbse init`.

**Backporting**: If you discover patterns that would benefit all agentic-mbse users, consider contributing them back to the main project.

---

## Validated Patterns

<!-- Add project-specific validated patterns here -->

## Project-Specific Guidance

<!-- Add domain-specific modeling guidance here -->

## Lessons Learned

<!-- Document modeling discoveries and gotchas -->

---

**See also**: [MODELING_GUIDE.md](MODELING_GUIDE.md) for standard patterns
```

---

## Related Artifacts

- **Backlog:** `.project/backlog/BACKLOG.md` (ITEM-SYMLINK-001)
- **Design:** `.project/active/tool-owned-file-safety/design.md` (to be created)
- **Reference:** fusion-tea commits ef11ada, a103596, 4590874, 6ab7b7d

---

**Next Steps:** After approval, proceed to `/_my_design`

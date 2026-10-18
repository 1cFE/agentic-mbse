---
name: my-git-manage
description: Manage parallel Git worktrees with this project's .project state-isolation workflow. Use only when the user explicitly invokes this skill for worktree creation, preparation, merging, reconciliation, listing, or removal. Do not use for ordinary branches, commits, pushes, or pull requests.
---

Generated from `claude-pack/commands/_my_git_manage.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Git Management Command

**Purpose**: Git workflow helpers including worktree management, merging, and conflict resolution
**Input**: Action and target (e.g., "create new worktree for feature-x", "merge in feature-x worktree")
**Output**: Executes git operations and reports status

## Overview

This command provides git workflow assistance, with a focus on worktree management for parallel development. It handles creation, merging, and cleanup of worktrees while integrating with project management documentation.

**When to use**:
- Creating worktrees for parallel branch development
- Merging worktree branches back to main
- Resolving merge conflicts with project context
- General git workflow assistance

---

## User Request

User-provided arguments are supplied when this skill is invoked.

---

## Action Routing

Parse the user's request and route to the appropriate action:

### Action: Create Worktree

**Trigger phrases**: "create", "new worktree", "add worktree"

**Process**:

1. **Parse branch name and target epic** from user request
   - Extract the intended branch name (e.g., "feature-x" from "create new worktree for feature-x")
   - Normalize to valid git branch name (replace spaces with hyphens, lowercase)
   - Identify which epic this worktree will focus on (check `.project/backlog/`)

2. **Determine worktree path**
   - Get repo name: `basename $(git rev-parse --show-toplevel)`
   - Default location: `../{repo-name}-{branch-name}`

3. **Create the worktree**:
   ```bash
   # Check if branch already exists
   git branch --list {branch-name}

   # If branch exists, use it
   git worktree add ../{repo-name}-{branch-name} {branch-name}
   # OR for new branch, create from current HEAD (not main)
   git worktree add ../{repo-name}-{branch-name} -b {branch-name}
   ```

   **Important**: New branches are created from the current HEAD, not from main. This preserves the user's current working context.

4. **Add worktree to permissions scope**:

   Update `.claude/settings.local.json` to allow file operations in the new worktree directory.

   - Read the current `settings.local.json`
   - Add the worktree absolute path to `permissions.additionalDirectories` array
   - If `additionalDirectories` doesn't exist, create it

   ```json
   {
     "permissions": {
       "allow": [...],
       "additionalDirectories": [
         "/path/to/{repo-name}-{branch-name}"
       ],
       ...
     }
   }
   ```

5. **Copy and adapt settings to worktree**:

   The `.claude/settings.local.json` file is gitignored, so it won't exist in the new worktree. Copy it and update paths.

   **5a. Copy settings file**:
   ```bash
   cp .claude/settings.local.json ../{repo-name}-{branch-name}/.claude/settings.local.json
   ```

   **5b. Update path references**:
   - Read the copied `settings.local.json` in the worktree
   - Replace all instances of the original repo path with the worktree path
   - This ensures environment paths point to the worktree, not the original repo

6. **Setup the worktree environment**:
   - Run environment setup commands per CLAUDE.md
   - Install dependencies as needed for the project

7. **Initialize worktree isolation** (Project Management Files):

   This step prevents merge conflicts and keeps Claude agents oriented in the worktree.

   **Files to isolate**:
   - `.project/active/CURRENT_WORK.md` (if exists)
   - `.project/backlog/BACKLOG.md`
   - `.project/completed/CHANGELOG.md` (if exists)

   **7a. Create backup of origin state** (in the new worktree):
   ```bash
   cd ../{repo-name}-{branch-name}
   cp .project/active/CURRENT_WORK.md .project/active/_origin_CURRENT_WORK.md 2>/dev/null || true
   cp .project/backlog/BACKLOG.md .project/backlog/_origin_BACKLOG.md
   cp .project/completed/CHANGELOG.md .project/completed/_origin_CHANGELOG.md 2>/dev/null || true
   ```

   **7b. Create worktree metadata file**: `.project/active/_WORKTREE_INFO.md`
   ```markdown
   # Worktree Information

   **Branch**: {branch-name}
   **Origin Branch**: {current-branch-name}
   **Created**: {date}
   **Epic Focus**: {epic-name}

   ## Origin State Reference
   The following files were backed up at worktree creation:
   - `.project/active/_origin_CURRENT_WORK.md`
   - `.project/backlog/_origin_BACKLOG.md`
   - `.project/completed/_origin_CHANGELOG.md`

   ## Merge Instructions
   Before merging back to origin branch, run:
   ``my-git-manage` prepare-merge`

   This will restore origin files to avoid conflicts, while preserving
   your worktree progress for manual reconciliation.
   ```

   **7c. Reset CURRENT_WORK.md** for new epic (if exists):
   - Update to reflect target epic focus
   - Clear parallel work items (those belong to origin branch)
   - Add note at top: `> **Worktree**: This is a parallel development branch. See `_WORKTREE_INFO.md` for details.`

   **7d. Update BACKLOG.md** for worktree:
   - Move target epic to active status
   - Add note about parallel development
   - Add note at top: `> **Worktree**: This is a parallel development branch.`

   **7e. Commit the isolation setup**:
   ```bash
   cd ../{repo-name}-{branch-name}
   git add .project/
   git commit -m "Initialize worktree isolation for {epic-name}

   - Backed up origin project management files
   - Reset for {epic-name} focus
   - Updated BACKLOG.md for parallel development"
   ```

8. **Report success**:
   - Confirm worktree created at path
   - Confirm dependencies installed
   - Confirm project management files isolated
   - Remind user to open a new Claude Code session there:
     ```
     cd ../{repo-name}-{branch-name}
     claude
     ```
   - Note: "When ready to merge, run ``my-git-manage` prepare-merge` first"

---

### Action: Prepare Merge

**Trigger phrases**: "prepare merge", "prepare-merge", "pre-merge"

**Purpose**: Restore origin project management files before merging to avoid conflicts.

**Prerequisites**:
- Must be run FROM the worktree (not the main repo)
- `_WORKTREE_INFO.md` must exist

**Process**:

1. **Verify worktree context**:
   ```bash
   ls .project/active/_WORKTREE_INFO.md
   ls .project/active/_origin_CURRENT_WORK.md 2>/dev/null || ls .project/backlog/_origin_BACKLOG.md
   ```
   - If files don't exist, abort with error

2. **Save worktree progress**:
   ```bash
   cp .project/active/CURRENT_WORK.md .project/active/_worktree_CURRENT_WORK.md 2>/dev/null || true
   cp .project/backlog/BACKLOG.md .project/backlog/_worktree_BACKLOG.md
   cp .project/completed/CHANGELOG.md .project/completed/_worktree_CHANGELOG.md 2>/dev/null || true
   ```

3. **Restore origin files**:
   ```bash
   mv .project/active/_origin_CURRENT_WORK.md .project/active/CURRENT_WORK.md 2>/dev/null || true
   mv .project/backlog/_origin_BACKLOG.md .project/backlog/BACKLOG.md
   mv .project/completed/_origin_CHANGELOG.md .project/completed/CHANGELOG.md 2>/dev/null || true
   ```

4. **Commit the pre-merge state**:
   ```bash
   git add .project/
   git commit -m "Pre-merge: restore origin project management files

   Worktree progress saved in:
   - _worktree_CURRENT_WORK.md
   - _worktree_BACKLOG.md
   - _worktree_CHANGELOG.md

   Ready for clean merge to {origin-branch}"
   ```

5. **Report status**:
   - Confirm origin files restored
   - Confirm worktree progress saved in `_worktree_*.md` files
   - Instruct: "Now merge from the main repo using ``my-git-manage` merge`"
   - Note: "After merge, run ``my-git-manage` reconcile` to integrate worktree progress"

---

### Action: Merge Worktree

**Trigger phrases**: "merge", "merge in", "merge from"

**Prerequisites**:
- Must be run FROM the main repo (not the worktree)
- The worktree should have run ``my-git-manage` prepare-merge` first

**Process**:

1. **Parse branch name** from user request

2. **Verify prepare-merge was run**:
   ```bash
   git show {branch-name}:.project/active/_worktree_CURRENT_WORK.md 2>/dev/null || \
   git show {branch-name}:.project/backlog/_worktree_BACKLOG.md 2>/dev/null
   ```
   - If not found, warn user: "Run ``my-git-manage` prepare-merge` in the worktree first"

3. **Gather context** before merging:

   **IMPORTANT**: Use explicit SHA comparison to avoid ref caching issues.

   ```bash
   git worktree list
   git branch --show-current
   git rev-parse HEAD
   git rev-parse {branch-name}
   git merge-base HEAD {branch-name}
   ```

   **Interpret the relationship**:
   - If `merge-base` equals `{branch-name}` SHA → branch is ancestor (already merged)
   - If `merge-base` equals `HEAD` SHA → fast-forward possible
   - If `merge-base` differs from both → true divergence (real merge needed)

   ```bash
   MERGE_BASE=$(git merge-base HEAD {branch-name})
   git log --oneline $MERGE_BASE..{branch-name}  # Commits to merge
   git log --oneline $MERGE_BASE..HEAD           # Parallel work
   ```

4. **Review project context**:
   - Read `.project/active/CURRENT_WORK.md` to understand current main branch state
   - Read worktree's `_worktree_CURRENT_WORK.md` (via git show) to see worktree progress

5. **Confirm merge strategy** with user:
   - Show commits that will be merged
   - Ask: merge commit vs rebase vs squash?
   - Default to merge commit for traceability

6. **Execute merge**:
   ```bash
   git branch --show-current
   git pull --ff-only  # Fail if not fast-forward
   git merge {branch-name}
   ```

7. **Handle merge conflicts** (if any):
   - List conflicted files: `git diff --name-only --diff-filter=U`
   - **Note**: If prepare-merge was run correctly, project management files should NOT conflict
   - For each conflict:
     a. Read the conflicted file
     b. Consult project documentation for context
     c. Analyze both versions and recommend resolution
     d. Ask user to confirm resolution approach
     e. Apply resolution and mark resolved: `git add {file}`
   - After all conflicts resolved: `git commit`

8. **Report result**:
   - Confirm successful merge
   - Show merged commits
   - **Important**: Remind user to run ``my-git-manage` reconcile {branch-name}` to integrate worktree progress

---

### Action: Reconcile

**Trigger phrases**: "reconcile", "integrate worktree progress"

**Purpose**: After merging, integrate the worktree's project management progress into main files.

**Prerequisites**:
- Must be run FROM the main repo (after merge completed)
- `_worktree_*.md` files must exist from the merged branch

**Process**:

1. **Verify reconciliation files exist**:
   ```bash
   ls .project/active/_worktree_CURRENT_WORK.md 2>/dev/null || \
   ls .project/backlog/_worktree_BACKLOG.md
   ls .project/active/_WORKTREE_INFO.md
   ```

2. **Read worktree info** for context

3. **Reconcile each file**:
   - Read `_worktree_*.md` to see worktree progress
   - Read current files (updated during parallel work on main)
   - **Integration approach**:
     - Add worktree's completed items appropriately
     - Preserve main's current state
   - Present diff to user for approval

4. **User approval** for each reconciliation

5. **Commit reconciliation**:
   ```bash
   git add .project/
   git commit -m "Reconcile project management files after {branch-name} merge

   Integrated progress from {epic-name} epic"
   ```

6. **Cleanup** (after user approval):
   ```bash
   rm .project/active/_worktree_CURRENT_WORK.md 2>/dev/null || true
   rm .project/active/_WORKTREE_INFO.md
   rm .project/backlog/_worktree_BACKLOG.md
   rm .project/completed/_worktree_CHANGELOG.md 2>/dev/null || true
   git add -A .project/
   git commit -m "Cleanup worktree isolation files after reconciliation"
   ```

7. **Report completion**:
   - Confirm all files reconciled
   - Suggest: "You can now remove the worktree with ``my-git-manage` remove {branch-name}`"

---

### Action: Remove Worktree

**Trigger phrases**: "remove", "delete", "cleanup worktree"

**Process**:

1. **Parse worktree identifier** from user request

2. **Safety checks**:
   ```bash
   git worktree list
   git -C ../{repo-name}-{branch-name} status --porcelain
   git -C ../{repo-name}-{branch-name} log --oneline @{upstream}..HEAD 2>/dev/null
   ```

3. **Warn user** if:
   - Uncommitted changes exist
   - Unpushed commits exist
   - Branch not merged to main

4. **Remove worktree**:
   ```bash
   git worktree remove ../{repo-name}-{branch-name}
   ```

5. **Optionally delete branch**:
   - Ask user if they want to delete the branch too
   - If merged: `git branch -d {branch-name}`
   - If not merged (force): `git branch -D {branch-name}` (only with explicit confirmation)

6. **Cleanup**:
   ```bash
   git worktree prune
   ```

---

### Action: List Worktrees

**Trigger phrases**: "list", "show worktrees", "status"

**Process**:
```bash
git worktree list
```

For each worktree, also show:
- Current branch
- Uncommitted changes count
- Commits ahead/behind main

---

## Worktree Isolation Pattern

This section documents how project management files are handled across worktrees to prevent merge conflicts.

### Why Isolation?

`.project/active/CURRENT_WORK.md`, `.project/backlog/BACKLOG.md`, and `.project/completed/CHANGELOG.md` are "global project state" files. Without isolation:
1. Claude agents in worktrees will be confused about which epic is active
2. Both branches will independently modify these files
3. Merge conflicts will be messy and hard to reconcile

### File Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CREATE WORKTREE                               │
├─────────────────────────────────────────────────────────────────────┤
│  CURRENT_WORK.md ──copy──> _origin_CURRENT_WORK.md                  │
│  BACKLOG.md ──copy──> _origin_BACKLOG.md                            │
│  CHANGELOG.md ──copy──> _origin_CHANGELOG.md                        │
│                                                                      │
│  CURRENT_WORK.md ──reset──> [new epic focus]                        │
│  BACKLOG.md ──update──> [new epic active]                           │
│  Create _WORKTREE_INFO.md                                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DURING DEVELOPMENT                              │
├─────────────────────────────────────────────────────────────────────┤
│  CURRENT_WORK.md ──updated──> [worktree progress]                   │
│  BACKLOG.md ──updated──> [epic progress]                            │
│  CHANGELOG.md ──updated──> [new entries]                            │
│                                                                      │
│  _origin_*.md files remain unchanged (for merge reference)          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PREPARE-MERGE (in worktree)                    │
├─────────────────────────────────────────────────────────────────────┤
│  CURRENT_WORK.md ──save──> _worktree_CURRENT_WORK.md                │
│  BACKLOG.md ──save──> _worktree_BACKLOG.md                          │
│  CHANGELOG.md ──save──> _worktree_CHANGELOG.md                      │
│                                                                      │
│  _origin_CURRENT_WORK.md ──restore──> CURRENT_WORK.md               │
│  _origin_BACKLOG.md ──restore──> BACKLOG.md                         │
│  _origin_CHANGELOG.md ──restore──> CHANGELOG.md                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        MERGE (in main repo)                          │
├─────────────────────────────────────────────────────────────────────┤
│  git merge {branch} → Clean merge (origin files match)              │
│  Project management files should NOT conflict                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RECONCILE (in main repo)                        │
├─────────────────────────────────────────────────────────────────────┤
│  Read _worktree_CURRENT_WORK.md → See worktree accomplishments      │
│  Read _worktree_BACKLOG.md → See epic progress                      │
│  Read _worktree_CHANGELOG.md → See new entries                      │
│                                                                      │
│  Integrate worktree progress into main files                         │
│  User approves each change                                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          CLEANUP                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Delete _worktree_*.md files                                        │
│  Delete _WORKTREE_INFO.md                                           │
│  Optionally remove worktree: git worktree remove                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Quick Reference

| Step | Where | Command |
|------|-------|---------|
| Create worktree | Main repo | ``my-git-manage` create worktree for {epic}` |
| Work on epic | Worktree | Normal development |
| Prepare for merge | Worktree | ``my-git-manage` prepare-merge` |
| Merge | Main repo | ``my-git-manage` merge {branch}` |
| Reconcile | Main repo | ``my-git-manage` reconcile` |
| Cleanup | Main repo | ``my-git-manage` remove {branch}` |

---

## Conflict Resolution Guidelines

When resolving merge conflicts, follow this process:

### 1. Understand the Context

Read project management files to understand:
- **What work was being done** on the branch being merged
- **What decisions were made** that led to the conflicting changes
- **What the intended behavior** should be

Key files to consult:
- `.project/active/CURRENT_WORK.md`
- `.project/active/{feature}/spec.md`
- `.project/active/{feature}/design.md`
- `.project/backlog/BACKLOG.md`

### 2. Analyze the Conflict

For each conflicted file:
- Show both versions (ours vs theirs)
- Explain what each version is trying to accomplish
- Identify if changes are:
  - **Independent**: Both can coexist (combine them)
  - **Competing**: Same goal, different approach (pick better one)
  - **Contradictory**: Mutually exclusive (need decision)

### 3. Recommend Resolution

Based on project context:
- Reference relevant specs`my-designs` to justify recommendation
- Explain trade-offs if applicable
- Present clear options to user

### 4. Apply Resolution

After user confirms:
- Edit the file to resolve conflict
- Remove conflict markers
- Stage the resolved file
- Continue with remaining conflicts

---

## Safety Guidelines

### Safety First
- Never force-push without explicit user confirmation
- Always check for uncommitted changes before destructive operations
- Prefer --ff-only pulls to avoid unexpected merges

### User Communication
- Explain what each git command does before running it
- Show command output and interpret results
- Ask for confirmation before irreversible operations

### Integration with Project Management
- This command works alongside ``my-status``
- Reference the same documentation structure
- Update project files when significant git operations complete

---

**Last Updated**: 2025-12-31


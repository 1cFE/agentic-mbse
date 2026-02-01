# Specification: File Rename and Deletion Tracking

**Purpose:** Maintain comment associations when source files are renamed or deleted through git operations.

## Requirements

**REQ-1: Rename Detection**
- MUST detect file renames via `git log --follow --diff-filter=R`
- MUST update sidecar `source_file` field to new path
- MUST move sidecar file to mirror new source location
- MUST preserve all thread data during rename

**REQ-2: Deletion Handling**
- MUST mark all threads as `orphaned` when source file is deleted
- MUST preserve sidecar file (no automatic deletion)
- MUST report orphaned-by-deletion in reconciliation output

**REQ-3: Rename Reconciliation**
- MUST run automatically on `comment list` or `comment show` when source missing
- MUST run automatically after git checkout (via optional hook)
- MUST handle rename chains (A → B → C)

**REQ-4: Multi-File Operations**
- `comment reconcile --all` MUST process all sidecar files
- MUST handle directory renames (multiple affected files)
- MUST report all rename operations in summary

**REQ-5: Git Dependency**
- MUST gracefully handle non-git repositories (skip rename detection)
- MUST work with shallow clones (best-effort rename detection)
- MUST not require specific git version > 2.0

## Acceptance Criteria

**AC-1:** Given file `old.md` renamed to `new.md` in git, when `comment reconcile old.md` runs, then sidecar moves from `.comments/old.md.json` to `.comments/new.md.json`

**AC-2:** Given file deleted in git, when reconciliation runs, then all threads have health `orphaned` and anchor.content_snippet preserved

**AC-3:** Given directory `src/` renamed to `lib/`, when `comment reconcile --all` runs, then all sidecars under `.comments/src/` move to `.comments/lib/`

**AC-4:** Given file rename outside git (filesystem only), when reconciliation runs, then threads become orphaned (no rename detection)

**AC-5:** Given file renamed twice (A → B → C), when reconciling with path A, then sidecar updates to path C

**AC-6:** Given non-git repository, when rename detection runs, then operation succeeds with warning "Git not available, rename detection skipped"

## Interfaces

**Inputs:**
- Source file path (potentially old path)
- Git repository root
- Optional: Explicit old → new path mapping

**Outputs:**
- Updated sidecar file location
- Rename detection report (old path → new path)

**References:**
- `file-operations.md`: Sidecar file moves
- `anchor-reconciliation.md`: Orphaning logic
- `data-model.md`: source_file field update

## Constraints

**CON-1:** Rename detection MUST NOT modify git history
**CON-2:** Sidecar moves MUST be atomic (temp + rename)
**CON-3:** MUST handle case-only renames on case-insensitive filesystems
**CON-4:** MUST detect renames across up to 10 intermediate renames

## Out of Scope

- Cross-repository file moves
- Rename detection outside git (filesystem-only operations)
- Automatic commit of sidecar moves
- Rename tracking across branches (only current HEAD)
- Handling of `.gitignore` patterns

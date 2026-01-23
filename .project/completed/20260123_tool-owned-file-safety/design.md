# Design: Tool-Owned File Safety

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-23 17:30 UTC
**Updated:** 2026-01-23 17:55 UTC
**Branch:** 1cfe_dev
**Commit:** 7a40de3

---

## Overview

Add modification detection for tool-owned files in normal mode and introduce a user-owned `LOCAL_GUIDE.md` for project-specific customizations that won't be overwritten on re-init.

## Related Artifacts

- **Spec:** `.project/active/tool-owned-file-safety/spec.md`
- **Backlog:** `.project/backlog/BACKLOG.md` (ITEM-SYMLINK-001)
- **Reference:** fusion-tea commits ef11ada, a103596, 4590874, 6ab7b7d

---

## Research Findings

### Current File Ownership Model

The CLI already has a clean split between user-owned and tool-owned files (cli/__init__.py:48-66):

```python
USER_OWNED_TEMPLATES = [
    ("README.md.template", "README.md"),
    ("OVERVIEW.md.template", "modeling_pm/OVERVIEW.md"),
    ("BACKLOG.md.template", "modeling_pm/backlog/BACKLOG.md"),
    # ... etc
]

TOOL_OWNED_TEMPLATES = [
    ("MODELING_GUIDE.md.template", "modeling_pm/MODELING_GUIDE.md"),
    ("MODELING_PROCESS.md.template", "modeling_pm/MODELING_PROCESS.md"),
]
```

- **User-owned**: Skipped if exists (preserves customizations)
- **Tool-owned**: Always overwritten (gets latest versions)

### Existing Helper Functions

- `_install_file()` (cli/__init__.py:210-232): Handles copy vs symlink for files
- `_install_directory()` (cli/__init__.py:235-259): Handles copy vs symlink for directories
- These are the natural extension points for modification detection

### Tool-Owned Files (Full List)

From `cmd_init()`, these are always updated:
1. **Commands** - `MBSE_COMMANDS` list → `.claude/commands/`
2. **Agents** - `MBSE_AGENTS` list → `.claude/agents/`
3. **Skills** - `MBSE_SKILLS` list → `.claude/skills/`
4. **Hooks** - `MBSE_HOOKS` list → `.claude/hooks/`
5. **Templates** - `TOOL_OWNED_TEMPLATES` → `modeling_pm/`

### Dev Mode Behavior

In `--dev` mode, tool-owned files **should** be symlinked to source repo. However:
- **fusion-tea note**: Currently missing symlinks for `MODELING_GUIDE.md` and `MODELING_PROCESS.md` (likely initialized before symlink feature was added). **Manual fix needed**: run `agentic-mbse init --dev` in fusion-tea to create the symlinks.
- For symlinked files, modification detection is not needed (edits go to source repo)
- For non-symlinked files in dev mode repos, modification detection still applies

### Testing Patterns

Tests use `MockArgs` class and `tmp_path` fixture. Existing tests cover:
- Skipping if exists
- Force overwriting
- Dev mode symlinks
- Idempotency

---

## Design Decisions

### DD-1: Use Hash File Approach

**Decision**: Store SHA256 hashes in `.claude/.tool-hashes.json`

**Rationale**: The spec analyzed three approaches:
- **Option A (Hash file)**: Store hash at install time, compare on re-init
- **Option B (Marker comment)**: Add comment to files with version/hash
- **Option C (Content comparison)**: Compare file to template each time

Option A is cleanest because:
1. Correctly distinguishes user edits from template updates
2. Doesn't modify source file content
3. Works for all file types (including .sh hooks)
4. Contained in `.claude/` directory (already tool-managed)

**Key insight**: Storing the **installed content hash** (not template hash) means:
- If user edits: current hash ≠ stored hash → **detect modification**
- If template updates but user didn't edit: current hash = stored hash → **safe to update**

**Why store commit**: The commit hash tells you which agentic-mbse version installed the file. If modifications are detected, the user can diff their changes against that commit to see exactly what they customized:

```
agentic-mbse    |    Target repo (non-dev mode)
[commit A]      -----> [File installed]
[commit B]
                       [User modifies file]
[commit C]      -----> [Re-init detects modification]
```

The stored commit (A) lets the user know "diff my changes against commit A" rather than guessing which version they started from.

### DD-2: Interactive Prompts for Modified Files

**Decision**: When modifications detected, prompt user for each file with options.

**Options presented**:
1. **Skip** (s) - Keep user's version, don't update this file
2. **Backup** (b) - Save current file to `.backup`, then update
3. **Overwrite** (o) - Replace with new version (lose changes)
4. **Skip All** (S) - Skip all remaining modified files
5. **Overwrite All** (O) - Overwrite all remaining (like `--force`)

**Rationale**: Mirrors common behaviors in package managers and installers. Gives user control without requiring them to restart with `--force`.

### DD-3: LOCAL_GUIDE.md as User-Owned File

**Decision**: Add `LOCAL_GUIDE.md.template` → `modeling_pm/LOCAL_GUIDE.md`

This becomes a user-owned file where project-specific patterns live. The spec's template is appropriate.

---

## Proposed Design

### Component 1: Hash Storage Module

**Location**: `src/agentic_mbse/cli/__init__.py` (new functions)

```python
import hashlib
from pathlib import Path
from typing import TypedDict

class ToolHashes(TypedDict):
    version: str  # agentic-mbse version that created hashes
    commit: str   # agentic-mbse git commit that created hashes
    files: dict[str, str]  # relative_path -> sha256_hex

HASH_FILE = ".claude/.tool-hashes.json"

def _compute_file_hash(path: Path) -> str:
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _get_git_commit() -> str:
    """Get short git commit hash of agentic-mbse source.

    Returns 'unknown' if not in a git repo or git not available.
    """
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=_get_data_root(),  # Run in agentic-mbse source dir
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"

def _load_tool_hashes(target: Path) -> ToolHashes | None:
    """Load hash file, return None if doesn't exist."""
    hash_path = target / HASH_FILE
    if not hash_path.exists():
        return None
    return json.loads(hash_path.read_text())

def _save_tool_hashes(target: Path, hashes: ToolHashes) -> None:
    """Save hash file."""
    hash_path = target / HASH_FILE
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    hash_path.write_text(json.dumps(hashes, indent=2) + "\n")
```

### Component 2: Modification Detection

**Location**: `src/agentic_mbse/cli/__init__.py` (new function)

```python
def _check_modification(
    path: Path,
    stored_hashes: ToolHashes | None,
    relative_path: str
) -> bool:
    """Check if file was modified since install.

    Returns True if file exists AND has been modified from installed version.
    Returns False if file doesn't exist OR matches stored hash.
    """
    if not path.exists():
        return False
    if stored_hashes is None:
        # First time tracking - treat as not modified
        # (backwards compatibility: existing installs without hashes)
        return False
    stored_hash = stored_hashes.get("files", {}).get(relative_path)
    if stored_hash is None:
        # File not in hash store - new file type, treat as not modified
        return False
    current_hash = _compute_file_hash(path)
    return current_hash != stored_hash
```

### Component 3: User Prompt for Modified Files

**Location**: `src/agentic_mbse/cli/__init__.py` (new function)

```python
def _prompt_for_modified_file(path: str) -> str:
    """Prompt user for action on modified file.

    Returns: 'skip', 'backup', 'overwrite', 'skip_all', 'overwrite_all'
    """
    print(f"\nModified: {path}")
    print("  This file has local modifications that will be lost if updated.")
    print("  Options:")
    print("    [s]kip      - Keep your version")
    print("    [b]ackup    - Save to .backup, then update")
    print("    [o]verwrite - Replace with new version")
    print("    [S]kip all  - Skip all modified files")
    print("    [O]verwrite all - Update all (like --force)")

    while True:
        choice = input("  Choice [s/b/o/S/O]: ").strip()
        if choice == 's':
            return 'skip'
        elif choice == 'b':
            return 'backup'
        elif choice == 'o':
            return 'overwrite'
        elif choice == 'S':
            return 'skip_all'
        elif choice == 'O':
            return 'overwrite_all'
        else:
            print("  Invalid choice. Please enter s, b, o, S, or O.")
```

### Component 4: Backup Function

**Location**: `src/agentic_mbse/cli/__init__.py` (new function)

```python
def _backup_file(path: Path) -> Path:
    """Create backup of file with .backup extension.

    If .backup exists, uses .backup.1, .backup.2, etc.
    Returns path to backup file.
    """
    backup_path = path.with_suffix(path.suffix + ".backup")
    counter = 1
    while backup_path.exists():
        backup_path = path.with_suffix(f"{path.suffix}.backup.{counter}")
        counter += 1
    shutil.copy(path, backup_path)
    return backup_path
```

### Component 5: Modified `_install_file()`

**Location**: `src/agentic_mbse/cli/__init__.py` (modify existing function)

The existing `_install_file()` function needs to be extended to:
1. Accept modification check results
2. Handle skip/backup/overwrite decisions
3. Return hash of installed content for storage

```python
def _install_file(
    src: Path,
    dst: Path,
    is_dev_mode: bool,
    was_modified: bool = False,
    user_action: str = "overwrite"
) -> tuple[str, str | None]:
    """Install a file by copying or symlinking.

    Args:
        src: Source file path
        dst: Destination file path
        is_dev_mode: If True, create symlink; if False, copy
        was_modified: If True, file had local modifications
        user_action: 'skip', 'backup', or 'overwrite'

    Returns:
        Tuple of (action_taken, content_hash_or_none)
        - action_taken: "created", "updated", "symlinked", "skipped", "backed_up_and_updated"
        - content_hash_or_none: SHA256 of installed content (None if symlinked or skipped)
    """
    existed = dst.exists() or dst.is_symlink()

    # Handle modified file based on user choice
    if was_modified and user_action == 'skip':
        return ("skipped", None)

    if was_modified and user_action == 'backup':
        backup_path = _backup_file(dst)
        print(f"    Backed up to: {backup_path.name}")

    # Remove existing file or symlink before creating new one
    if existed:
        dst.unlink()

    if is_dev_mode:
        dst.symlink_to(src.resolve())
        return ("re-symlinked" if existed else "symlinked", None)
    else:
        shutil.copy(src, dst)
        content_hash = _compute_file_hash(dst)
        if was_modified and user_action == 'backup':
            return ("backed_up_and_updated", content_hash)
        return ("updated" if existed else "created", content_hash)
```

### Component 6: Modified `cmd_init()`

**Key changes to `cmd_init()`**:

1. Load existing hashes at start
2. Build list of modified files before installing
3. Prompt user once for modified files (batch)
4. Track user's "skip all" / "overwrite all" state
5. Collect new hashes during installation
6. Save updated hashes at end

**Pseudocode flow**:
```python
def cmd_init(args):
    # ... existing setup ...

    # Load existing hashes
    stored_hashes = _load_tool_hashes(target) if not is_dev_mode else None

    # Collect all tool-owned files that would be modified
    modified_files: list[str] = []

    # Check each tool-owned file
    for cmd in MBSE_COMMANDS:
        rel_path = f".claude/commands/{cmd}"
        if _check_modification(target / rel_path, stored_hashes, rel_path):
            modified_files.append(rel_path)
    # ... similar for agents, skills, hooks, templates ...

    # If any modified and not force, prompt user
    user_decisions: dict[str, str] = {}  # path -> action
    default_action = "overwrite" if args.force else None

    if modified_files and not args.force and not is_dev_mode:
        print(f"\n{len(modified_files)} tool-owned file(s) have local modifications:")
        for f in modified_files:
            print(f"  - {f}")

        for f in modified_files:
            if default_action:
                user_decisions[f] = default_action
            else:
                action = _prompt_for_modified_file(f)
                if action == 'skip_all':
                    default_action = 'skip'
                    user_decisions[f] = 'skip'
                elif action == 'overwrite_all':
                    default_action = 'overwrite'
                    user_decisions[f] = 'overwrite'
                else:
                    user_decisions[f] = action

    # New hash tracking
    new_hashes: dict[str, str] = {}

    # ... existing installation code, modified to use user_decisions ...
    # Each _install_file call returns (action, hash)
    # Collect hashes into new_hashes

    # Save hashes at end (only in normal mode)
    if not is_dev_mode:
        _save_tool_hashes(target, {
            "version": _get_version(),
            "commit": _get_git_commit(),  # Short hash of agentic-mbse repo
            "files": new_hashes
        })

    # ... existing summary output ...
```

### Component 7: LOCAL_GUIDE.md Template

**Location**: `project_templates/LOCAL_GUIDE.md.template`

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

**Registry update** (cli/__init__.py):
```python
USER_OWNED_TEMPLATES = [
    # ... existing ...
    ("LOCAL_GUIDE.md.template", "modeling_pm/LOCAL_GUIDE.md"),  # NEW
]
```

### Component 8: Reference from MODELING_GUIDE.md

**Location**: `project_templates/MODELING_GUIDE.md.template`

Add near the top of the file:
```markdown
> **Note**: For project-specific patterns and customizations, see [LOCAL_GUIDE.md](LOCAL_GUIDE.md).
```

---

## Potential Risks

### R-1: Backwards Compatibility (First Run After Update)

**Risk**: Existing projects don't have `.claude/.tool-hashes.json`. First run after this update will have no stored hashes.

**Mitigation**: `_check_modification()` treats missing hash file or missing file entry as "not modified". This means first run after update will overwrite without prompting (same as before), but will create the hash file for future runs.

**Alternative considered**: Could force-prompt on first run with "we don't know if these were modified, proceed?" But this would be annoying for every existing project.

### R-2: Hash File in Version Control

**Risk**: Should `.claude/.tool-hashes.json` be in `.gitignore`?

**Analysis**:
- If committed: All team members have same baseline, but may conflict if different team members run init at different times
- If gitignored: Each developer has their own tracking, no conflicts

**Decision**: Add to generated `.gitignore`. Hash file is machine-local state, like `.env`. Each developer tracks their own modifications.

### R-3: Non-Interactive Mode

**Risk**: In CI/CD or scripted environments, interactive prompts will hang.

**Mitigation**: The `--force` flag already exists and bypasses all prompts. Users running in CI should use `--force`. Could also add `--no-prompt` flag that defaults to skip (fail-safe).

### R-4: Partial Install on Skip

**Risk**: If user skips some files, project may have inconsistent state (some new, some old).

**Mitigation**: This is user choice. The summary output clearly shows what was skipped. Users can re-run with `--force` to sync everything.

---

## Integration Strategy

### Files to Modify

1. **`src/agentic_mbse/cli/__init__.py`**:
   - Add hash utility functions
   - Add modification detection
   - Add prompt function
   - Add backup function
   - Modify `_install_file()` signature and logic
   - Modify `cmd_init()` to use modification detection
   - Update `USER_OWNED_TEMPLATES` with LOCAL_GUIDE.md

2. **`project_templates/LOCAL_GUIDE.md.template`** (new file)

3. **`project_templates/MODELING_GUIDE.md.template`**:
   - Add reference to LOCAL_GUIDE.md

4. **`.gitignore` generation in `cmd_init()`**:
   - Add `.claude/.tool-hashes.json` to generated .gitignore

### Integration with Existing Workflows

- `--dev` mode: Symlinked files don't need hashes (edits go to source). No hash file created.
- `--force` mode: Overwrites everything without prompting, creates hash file
- Normal mode: New behavior (detect modifications, prompt if found, create hash file)

### Audit Task (Implementation Phase)

Per FR-6, during implementation: audit fusion-tea history to verify no content was lost. This is a manual verification task, not code.

---

## Validation Approach

### Unit Tests

1. **Hash computation**: Test `_compute_file_hash()` returns consistent SHA256
2. **Hash storage**: Test `_load_tool_hashes()` and `_save_tool_hashes()` round-trip
3. **Modification detection**:
   - No hash file → returns False
   - Hash file but file missing → returns False
   - Hash matches → returns False
   - Hash differs → returns True
4. **Backup function**: Creates `.backup`, handles existing backups
5. **LOCAL_GUIDE.md**: Created on init, skipped on re-init

### Integration Tests

1. **Full flow without modifications**: Init → re-init → no prompts, hashes updated
2. **Full flow with modifications**: Init → modify file → re-init → detect modification
3. **Skip behavior**: Modify → re-init with skip → original file preserved
4. **Backup behavior**: Modify → re-init with backup → backup created, file updated
5. **Force flag**: Modify → re-init with --force → no prompts, file overwritten
6. **Dev mode**: --dev mode → no hash file created

### Manual Verification

1. Fresh init in new directory
2. Modify MODELING_GUIDE.md
3. Re-run init without --force
4. Verify prompt appears
5. Test each option (skip, backup, overwrite)
6. Verify LOCAL_GUIDE.md created and preserved on re-init

---

**Next Step:** After approval → `/_my_implement` or `/_my_plan`

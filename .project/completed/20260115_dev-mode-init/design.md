# Design: Development Mode for Init Command

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-15 19:57:30 UTC
**Branch:** 1cfe_dev

---

## Overview

Add a `--dev` flag to `agentic-mbse init` that creates symlinks for tool-owned files instead of copies, enabling bidirectional synchronization between the agentic-mbse source repo and domain projects during development.

## Related Artifacts

- **Spec:** `.project/active/dev-mode-init/spec.md`
- **Research:** `project/research/20260113-150000_progressive-disclosure-architecture.md` (Part 2)
- **Backlog:** `.project/backlog/BACKLOG.md` (ITEM-DEVMODE-001)
- **Implementation:** `src/agentic_mbse/cli/__init__.py`

---

## Research Findings

### Codebase Analysis

**File:** `src/agentic_mbse/cli/__init__.py`

The current `cmd_init()` function (lines 193-469) handles file installation in distinct sections:

| Section | Lines | Type | Files |
|---------|-------|------|-------|
| Commands | 314-328 | TOOL_OWNED | `MBSE_COMMANDS` list (9 files) |
| Agents | 330-348 | TOOL_OWNED | `MBSE_AGENTS` list (5 files) |
| Skills | 350-364 | TOOL_OWNED | `MBSE_SKILLS` list (1 directory) |
| Hooks | 366-381 | TOOL_OWNED | `MBSE_HOOKS` list (1 file) |
| User templates | 392-402 | USER_OWNED | `USER_OWNED_TEMPLATES` (3 files) |
| Tool templates | 404-415 | TOOL_OWNED | `TOOL_OWNED_TEMPLATES` (2 files) |
| Settings | 417-440 | USER_OWNED | `.claude/settings.json` |
| Gitignore | 224-285 | USER_OWNED | `.gitignore` |
| SOURCE_INDEX | 287-312 | USER_OWNED | `SOURCE_INDEX.md` |

**Key existing patterns:**

1. **Source checkout detection** (`_get_data_root()`, lines 63-83):
   - Checks if `claude/` exists at source root → source checkout
   - Falls back to `agentic_mbse_data/` → pip installed
   - Already returns the source root path we need for symlinks

2. **Tracking arrays** (lines 220-222):
   - `created[]` - new files
   - `updated[]` - refreshed tool-owned files
   - `skipped[]` - preserved user-owned files
   - Will add `symlinked[]` for dev mode

3. **Agent special handling** (lines 341-344):
   - Agents have placeholder substitution (`{SYSML_DOCS_PATH}`, `{SYSIDE_DOCS_PATH}`)
   - In dev mode, symlink without substitution (source files have placeholders)
   - Document this as a known limitation

**Test patterns** (`tests/test_cli.py`):
- Uses `MockArgs` class for argparse namespace (lines 13-17)
- `tmp_path` fixture for isolated directories
- Tests both success paths and edge cases

### Technical Constraints

1. **Symlinks require source checkout**: `_get_data_root()` returns pip data location when installed via pip, but symlinks must point to the actual source repo where files can be edited.

2. **Agent placeholder substitution incompatible with symlinks**: When symlinking agents, the placeholders `{SYSML_DOCS_PATH}` remain in the file. This is acceptable because:
   - Dev mode is for agentic-mbse developers who understand the repo structure
   - Agents still function (Claude Code reads from source docs/ directly in dev mode)

3. **Skills are directories**: `MBSE_SKILLS` contains directory names, not files. Symlink the directory itself, not individual files.

---

## Proposed Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     cmd_init(args)                               │
├─────────────────────────────────────────────────────────────────┤
│  1. Validate preconditions (existing)                            │
│  2. NEW: Check dev mode prerequisites                            │
│     - Windows → error                                            │
│     - Not source checkout → error                                │
│  3. Process each file category:                                  │
│     - USER_OWNED: always copy (existing behavior)                │
│     - TOOL_OWNED: if --dev → symlink, else copy                 │
│  4. NEW: If --dev, add tool-owned paths to .gitignore            │
│  5. Print summary with symlink indication                        │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. CLI Argument Addition

**Location:** `src/agentic_mbse/cli/__init__.py`, lines 557-572

Add `--dev` flag to init parser:

```python
init_parser.add_argument(
    "--dev",
    action="store_true",
    help="Development mode: symlink tool-owned files instead of copying (requires source checkout)",
)
```

#### 2. Precondition Checks

**Location:** `src/agentic_mbse/cli/__init__.py`, insert after line 217 (target validation)

**Function:** `_check_dev_mode_prerequisites(data_root: Path) -> tuple[bool, str | None]`

```python
def _check_dev_mode_prerequisites(data_root: Path) -> tuple[bool, str | None]:
    """Check if dev mode can be used.

    Returns:
        (can_use, error_message) - error_message is None if can_use is True
    """
    import platform

    # Check Windows
    if platform.system() == "Windows":
        return False, "Dev mode is not supported on Windows (symlinks require admin privileges)"

    # Check source checkout (claude/ directory exists at root)
    if not (data_root / "claude").exists():
        return False, (
            "Dev mode requires a source checkout of agentic-mbse.\n"
            "Pip-installed packages cannot use dev mode.\n"
            "Clone the repo and install with: pip install -e /path/to/agentic-mbse"
        )

    return True, None
```

**Integration in `cmd_init()`:**

```python
# After line 217 (target validation)
is_dev_mode = getattr(args, 'dev', False)
data_root = _get_data_root()

if is_dev_mode:
    can_use, error_msg = _check_dev_mode_prerequisites(data_root)
    if not can_use:
        print(f"Error: {error_msg}", file=sys.stderr)
        return EXIT_FAILURE
```

#### 3. File Installation Helper

**Function:** `_install_file(src: Path, dst: Path, is_dev_mode: bool) -> str`

Centralizes the copy-vs-symlink logic:

```python
def _install_file(src: Path, dst: Path, is_dev_mode: bool) -> str:
    """Install a file by copying or symlinking.

    Args:
        src: Source file path
        dst: Destination file path
        is_dev_mode: If True, create symlink; if False, copy

    Returns:
        Action taken: "created", "updated", "symlinked", or "re-symlinked"
    """
    existed = dst.exists() or dst.is_symlink()

    # Remove existing file or symlink before creating new one
    if existed:
        dst.unlink()

    if is_dev_mode:
        dst.symlink_to(src.resolve())
        return "re-symlinked" if existed else "symlinked"
    else:
        shutil.copy(src, dst)
        return "updated" if existed else "created"
```

**For directories (skills):**

```python
def _install_directory(src: Path, dst: Path, is_dev_mode: bool) -> str:
    """Install a directory by copying or symlinking.

    Args:
        src: Source directory path
        dst: Destination directory path
        is_dev_mode: If True, create symlink; if False, copy tree

    Returns:
        Action taken: "created", "updated", "symlinked", or "re-symlinked"
    """
    existed = dst.exists() or dst.is_symlink()

    if existed:
        if dst.is_symlink():
            dst.unlink()
        else:
            shutil.rmtree(dst)

    if is_dev_mode:
        dst.symlink_to(src.resolve())
        return "re-symlinked" if existed else "symlinked"
    else:
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return "updated" if existed else "created"
```

#### 4. Modified File Installation Sections

**Commands section** (lines 314-328):

```python
source_commands = get_commands_dir()
for cmd in MBSE_COMMANDS:
    src = source_commands / cmd
    dst = commands_dir / cmd
    if src.exists():
        action = _install_file(src, dst, is_dev_mode)
        if "symlink" in action:
            symlinked.append(f".claude/commands/{cmd}")
        elif action == "updated":
            updated.append(f".claude/commands/{cmd}")
        else:
            created.append(f".claude/commands/{cmd}")
```

**Agents section** (lines 330-348):

```python
for agent in MBSE_AGENTS:
    src = source_agents / agent
    dst = agents_dir / agent
    if src.exists():
        if is_dev_mode:
            # Symlink directly - placeholders remain in source
            action = _install_file(src, dst, is_dev_mode=True)
            symlinked.append(f".claude/agents/{agent}")
        else:
            # Copy with placeholder substitution
            existed = dst.exists()
            content = src.read_text()
            content = content.replace("{SYSML_DOCS_PATH}", f"{docs_path}/sysmlv2")
            content = content.replace("{SYSIDE_DOCS_PATH}", f"{docs_path}/syside")
            dst.write_text(content)
            if existed:
                updated.append(f".claude/agents/{agent}")
            else:
                created.append(f".claude/agents/{agent}")
```

**Skills section** (lines 350-364):

```python
for skill in MBSE_SKILLS:
    src = source_skills / skill
    dst = skills_dir / skill
    if src.exists() and src.is_dir():
        action = _install_directory(src, dst, is_dev_mode)
        if "symlink" in action:
            symlinked.append(f".claude/skills/{skill}/")
        elif action == "updated":
            updated.append(f".claude/skills/{skill}/")
        else:
            created.append(f".claude/skills/{skill}/")
```

**Hooks section** (lines 366-381):

```python
for hook in MBSE_HOOKS:
    src = source_hooks / hook
    dst = hooks_dir / hook
    if src.exists():
        action = _install_file(src, dst, is_dev_mode)
        if "symlink" in action:
            symlinked.append(f".claude/hooks/{hook}")
        elif action == "updated":
            updated.append(f".claude/hooks/{hook}")
        else:
            created.append(f".claude/hooks/{hook}")
        # Preserve execute permission (symlinks inherit from target)
        if not is_dev_mode:
            dst.chmod(src.stat().st_mode)
```

**Tool-owned templates** (lines 404-415):

```python
for template_name, dest_path in TOOL_OWNED_TEMPLATES:
    src = templates_dir / template_name
    dst = target / dest_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        action = _install_file(src, dst, is_dev_mode)
        if "symlink" in action:
            symlinked.append(dest_path)
        elif action == "updated":
            updated.append(dest_path)
        else:
            created.append(dest_path)
```

#### 5. Updated Summary Output

**Location:** Lines 442-468

Add `symlinked` tracking list and update summary:

```python
# At line 220, add:
symlinked: list[str] = []  # Dev mode symlinks

# In summary section:
if symlinked:
    print(f"\nSymlinked ({len(symlinked)}) - dev mode, points to source:")
    for item in symlinked:
        print(f"  @ {item}")

# Update header message:
if is_dev_mode:
    print(f"\nInitialized MBSE project in {target} (dev mode)")
else:
    print(f"\nInitialized MBSE project in {target}")
```

#### 6. Gitignore Update for Dev Mode

**Rationale:** Symlinks use absolute paths pointing to the developer's local agentic-mbse checkout. If committed to git:
- Other developers cloning the repo would have broken symlinks
- Git shows "typechange" for files that became symlinks

**Solution:** When `--dev` is specified, append tool-owned paths to `.gitignore`.

**Function:** `_update_gitignore_for_dev_mode(target: Path) -> bool`

```python
# Tool-owned paths to add to .gitignore in dev mode
DEV_MODE_GITIGNORE_PATHS = [
    "# Tool-owned files (managed by agentic-mbse init --dev)",
    ".claude/commands/",
    ".claude/agents/",
    ".claude/skills/",
    ".claude/hooks/",
    "project/MODELING_GUIDE.md",
    "project/MODELING_PROCESS.md",
]

def _update_gitignore_for_dev_mode(target: Path) -> bool:
    """Add tool-owned paths to .gitignore for dev mode.

    Returns True if .gitignore was modified, False if paths already present.
    """
    gitignore_path = target / ".gitignore"

    # Read existing content
    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text()

    # Check if already has dev mode section (idempotent)
    marker = DEV_MODE_GITIGNORE_PATHS[0]
    if marker in existing_content:
        return False

    # Append dev mode paths
    new_section = "\n" + "\n".join(DEV_MODE_GITIGNORE_PATHS) + "\n"
    gitignore_path.write_text(existing_content.rstrip() + new_section)
    return True
```

**Integration in `cmd_init()`:**

```python
# After symlink creation, before summary output
if is_dev_mode:
    if _update_gitignore_for_dev_mode(target):
        created.append(".gitignore (dev mode paths)")
```

### Data Flow

```
User runs: agentic-mbse init --dev /path/to/project
                    │
                    ▼
┌─────────────────────────────────────┐
│ 1. Parse args (is_dev_mode = True)  │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│ 2. Check prerequisites              │
│    - Not Windows? ✓                 │
│    - Source checkout? ✓             │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│ 3. For each TOOL_OWNED file:        │
│    - Remove existing (if any)       │
│    - Create symlink to source       │
│    - Track in symlinked[]           │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│ 4. For each USER_OWNED file:        │
│    - Copy (never symlink)           │
│    - Track in created[]/skipped[]   │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│ 5. If dev mode:                     │
│    - Add tool paths to .gitignore   │
│    - Idempotent (skip if present)   │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│ 6. Print summary with:              │
│    - Symlinked (N) - dev mode       │
│    - Created (N)                    │
│    - Skipped (N)                    │
└─────────────────────────────────────┘
```

### Error Handling

| Scenario | Detection | Response |
|----------|-----------|----------|
| Windows platform | `platform.system() == "Windows"` | Exit with error explaining Windows limitation |
| Pip-installed package | `not (data_root / "claude").exists()` | Exit with error explaining source checkout requirement |
| Target doesn't exist | Existing check at line 214 | Exit with error (unchanged) |
| Source file missing | `if src.exists()` | Skip with implicit warning (unchanged) |
| Symlink target exists | `dst.exists() or dst.is_symlink()` | Remove before creating new symlink |

### Testing Strategy

**File:** `tests/test_cli.py`

**New test class:** `TestCmdInitDevMode`

```python
class TestCmdInitDevMode:
    """Tests for init --dev mode."""

    def test_dev_creates_symlinks_for_commands(self, tmp_path):
        """--dev creates symlinks for command files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        result = cmd_init(args)

        assert result == EXIT_SUCCESS
        cmd_path = tmp_path / ".claude" / "commands" / "design-model.md"
        assert cmd_path.is_symlink()
        # Verify symlink points to source repo
        assert "agentic-mbse" in str(cmd_path.resolve())

    def test_dev_creates_symlinks_for_agents(self, tmp_path):
        """--dev creates symlinks for agent files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        agent_path = tmp_path / ".claude" / "agents" / "python-debugger.md"
        assert agent_path.is_symlink()

    def test_dev_creates_symlinks_for_skills(self, tmp_path):
        """--dev creates symlinks for skill directories."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        skill_path = tmp_path / ".claude" / "skills" / "python-debugger"
        assert skill_path.is_symlink()
        assert skill_path.is_dir()  # Symlink to directory

    def test_dev_creates_symlinks_for_hooks(self, tmp_path):
        """--dev creates symlinks for hook files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        hook_path = tmp_path / ".claude" / "hooks" / "ruff-format.sh"
        assert hook_path.is_symlink()

    def test_dev_creates_symlinks_for_tool_templates(self, tmp_path):
        """--dev creates symlinks for tool-owned templates."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        guide_path = tmp_path / "project" / "MODELING_GUIDE.md"
        assert guide_path.is_symlink()

    def test_dev_copies_user_owned_files(self, tmp_path):
        """--dev still copies (not symlinks) user-owned files."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        # User-owned files should be regular files, not symlinks
        assert not (tmp_path / "SOURCE_INDEX.md").is_symlink()
        assert not (tmp_path / ".gitignore").is_symlink()
        assert not (tmp_path / ".claude" / "settings.json").is_symlink()
        assert not (tmp_path / "README.md").is_symlink()

    def test_dev_idempotent(self, tmp_path):
        """Running --dev twice succeeds and updates symlinks."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)

        # First run
        result1 = cmd_init(args)
        assert result1 == EXIT_SUCCESS

        # Second run
        result2 = cmd_init(args)
        assert result2 == EXIT_SUCCESS

        # Symlinks should still work
        cmd_path = tmp_path / ".claude" / "commands" / "design-model.md"
        assert cmd_path.is_symlink()

    def test_dev_replaces_regular_file_with_symlink(self, tmp_path):
        """--dev replaces existing regular files with symlinks."""
        # First init without dev
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        cmd_path = tmp_path / ".claude" / "commands" / "design-model.md"
        assert not cmd_path.is_symlink()  # Regular file

        # Second init with dev
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        cmd_init(args)

        assert cmd_path.is_symlink()  # Now a symlink

    @pytest.mark.skipif(
        __import__("platform").system() != "Windows",
        reason="Windows-specific test"
    )
    def test_dev_fails_on_windows(self, tmp_path):
        """--dev fails with clear error on Windows."""
        args = MockArgs(path=str(tmp_path), force=False, dev=True)
        result = cmd_init(args)
        assert result == EXIT_FAILURE

    def test_without_dev_copies_files(self, tmp_path):
        """Init without --dev still copies files (regression test)."""
        args = MockArgs(path=str(tmp_path), force=False, dev=False)
        cmd_init(args)

        cmd_path = tmp_path / ".claude" / "commands" / "design-model.md"
        assert not cmd_path.is_symlink()
        assert cmd_path.exists()
```

**Integration test:**

```python
def test_cli_init_dev_help(self):
    """init --help shows --dev option."""
    result = subprocess.run(
        ["agentic-mbse", "init", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--dev" in result.stdout
```

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Stale symlinks if source moved | Low | Medium | Symlinks use absolute paths; user would notice immediately |
| Agent placeholders not substituted in dev mode | Expected | Low | Document in help text; agents still work via direct source access |
| Accidental use in production | Low | Low | Requires explicit `--dev` flag |

---

## Integration Strategy

**Fits into existing workflows:**
- Normal users: `agentic-mbse init` unchanged
- Developers: `agentic-mbse init --dev` for bidirectional sync

**Complements:**
- `--force` flag (still works, allows overwriting user-owned files)
- Existing file ownership model (USER_OWNED vs TOOL_OWNED)

**Does not affect:**
- `agentic-mbse validate`
- `agentic-mbse install-commands`

---

## Validation Approach

### Automated Testing

1. **Unit tests** (see Testing Strategy above):
   - Symlink creation for each file category
   - User-owned files still copied
   - Idempotent behavior
   - Error cases (Windows, pip-installed)

2. **Integration tests**:
   - CLI help shows `--dev` option
   - Full init workflow with `--dev`

### Manual Verification

1. Run `agentic-mbse init --dev /tmp/test-project`
2. Verify with `ls -la /tmp/test-project/.claude/commands/` shows symlinks
3. Edit a command in agentic-mbse source, verify change visible in test project
4. Run `agentic-mbse init --dev` again, verify no errors

---

**Next Step:** After approval → `/_my_implement`

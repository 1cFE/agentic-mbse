# agentic-mbse Backlog

## P0: Ready

### Handle .env and SYSIDE_LICENSE_KEY at initialization
**Status**: READY

The `init` command should:
- Check if `.env` exists, create template if not
- Prompt user for `SYSIDE_LICENSE_KEY` or note it's required
- Document the license key requirement in generated README

### Add --dev flag for symlinked commands/agents/skills
**Status**: READY

**Problem**: When developing `agentic-mbse`, changes to commands/agents/skills must be made in two places:
1. The working project's `.claude/` directory (to test)
2. The `agentic-mbse/claude/` source directory (to commit)

**Solution**: Add `--dev` flag to `init` that symlinks instead of copies:
```bash
agentic-mbse init --dev
```

Would create:
- `.claude/commands/` → symlink to `agentic-mbse/claude/commands/`
- `.claude/agents/` → symlink to `agentic-mbse/claude/agents/`
- `.claude/skills/` → symlink to `agentic-mbse/claude/skills/`
- `.claude/hooks/` → symlink to `agentic-mbse/claude/hooks/`

Or symlink individual files for more granular control.

**Benefits**:
- Edit in working project, changes appear in source repo
- `git diff` in agentic-mbse shows changes immediately
- Single source of truth during development

**Caveats**:
- Symlinks use absolute paths, so project not portable to other machines
- Only for development, not production use
- May need to detect if running from source checkout vs pip install

---

## Recently Completed

### Add bundled docs permissions to init (2025-01-05)
**Status**: COMPLETE

The `init` command now always creates `.claude/settings.json` with permissions for the bundled docs directory:
- `Read(~/agentic-mbse/docs/**)`
- `Grep(~/agentic-mbse/docs/**)`
- `Glob(~/agentic-mbse/docs/**)`

This allows specialist agents to search/read documentation without permission prompts.

### Fix Claude settings permission path format (2025-01-05)
**Status**: COMPLETE

**Problem**: Permission paths like `Read(/home/user/foo/**)` were interpreted as relative to settings.json, not absolute. Users got permission prompts even with paths in settings.json.

**Root cause**: Claude Code permission format is:
- `/path` = relative to settings.json (NOT absolute!)
- `//path` = absolute filesystem path
- `~/path` = from $HOME

**Fix applied**:
- Added `_to_claude_permission_path()` helper in `cli/__init__.py`
- Converts `/home/user/foo` → `~/foo` for portability
- Falls back to `//path` for paths not under $HOME
- Updated `/onboard` command with format documentation
- Updated `/manage-sources` to offer permissions when adding sources

---

## P1: Next

(empty)

---

## P2: Later

(empty)

---

**Last Updated**: 2025-01-05

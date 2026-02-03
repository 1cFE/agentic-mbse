# File-Native Comment System - VSCode Extension

Thread-based code comments stored in `.comments/` directory with intelligent anchor reconciliation.

## Features

- **Inline comment threads** displayed in VSCode editor gutters
- **Persistent storage** in `.comments/` directory (never modifies source files)
- **Intelligent anchoring** with 5-tier fallback strategy (exact hash → context hash → fuzzy matching → line offset → orphaned)
- **Git-aware** rename and deletion tracking
- **Status management** for threads (open/resolved/wontfix)
- **Decision logging** generates `DECISIONS.md` from resolved threads

## Installation

### From VSIX (Recommended)

1. Download the latest `.vsix` file from releases
2. In VSCode: Extensions → ... → Install from VSIX
3. Reload VSCode

### From Source

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VSCode to launch Extension Development Host
```

## Usage

This extension works in conjunction with the `comment_system` CLI tool.

### Create a comment thread

1. Select code in editor
2. Right-click → "Add Comment Thread" (TODO: not yet implemented)
3. Enter comment text in sidebar panel

### View threads

- **Gutter icons** show thread status (open/resolved/wontfix)
- **Inline highlights** show anchored code ranges
- **Sidebar panel** lists all threads for current file

### CLI Integration

```bash
# List all threads
uv run python -m comment_system.cli list

# Reconcile anchors after file edits
uv run python -m comment_system.cli reconcile src/myfile.py

# Generate decision log
uv run python -m comment_system.cli decisions
```

## Development Status

**Version 0.1.0** — Scaffolding phase

- ✅ TypeScript project setup
- ✅ Extension manifest and build configuration
- ❌ CommentController registration (planned)
- ❌ Sidecar file reader (planned)
- ❌ UI components (planned)

## License

MIT

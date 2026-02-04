# File-Native Comment System - VSCode Extension

Thread-based code comments stored in `.comments/` sidecar files. Comments live alongside your code in version control without modifying source files.

## Features

- **Inline comment threads** in the native VSCode Comments panel (gutter icons, thread sidebar)
- **Persistent sidecar storage** in `.comments/` directory — commit to git for team collaboration
- **Intelligent anchor reconciliation** with 5-tier fallback (exact hash → context hash → fuzzy match → line offset → orphaned)
- **Git-aware rename tracking** — committed file renames are detected and sidecars moved automatically
- **Optimistic concurrency** — detects external sidecar changes and prompts before overwriting
- **Status management** — open, resolved (with required decision), reopen
- **Decision log** — resolved threads generate a `DECISIONS.md` summary
- **Visual health indicators** — gutter icons and text decorations show anchor health (anchored/drifted/orphaned)

## Installation

### From VSIX

1. Build or download the `.vsix` file
2. In VSCode: Extensions → `...` → Install from VSIX
3. Reload VSCode

### From Source

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 to launch Extension Development Host
```

### Prerequisites

The extension requires the `comment` CLI tool on your PATH. Install it from the parent project:

```bash
cd ..
uv sync
uv run pip install -e .
```

The extension also requires a git repository — it finds the project root by walking up from the workspace folder to the nearest `.git` directory.

## Setup

### Author Identity

Comments are attributed using your **OS username** from `vscode.env.username`. There is currently no setting to override this. If your OS username isn't what you want appearing on comments, be aware of this before your first commit of `.comments/`.

The CLI fallback (when `--author` is not passed) is `unknown`. The extension always passes your username explicitly.

### Committing Comments

The `.comments/` directory should be committed to your repository so the team shares comment threads:

```bash
git add .comments/
git commit -m "Add comment threads"
```

## Usage

### Adding a Comment

1. Select code in the editor
2. Right-click → **Add Comment** (or `Ctrl+K Ctrl+M` / `Cmd+K Cmd+M`)
3. Enter your comment text
4. The thread appears in the gutter and Comments panel

### Replying

Click the reply icon on any thread in the Comments panel. The extension checks for external changes before writing — if someone else modified the sidecar, you'll be prompted to reload, overwrite, or cancel.

### Resolving a Thread

Click the checkmark (✓) icon on an open thread's title bar. You'll be prompted for a **required decision** explaining why the thread was resolved. The thread label changes to `[Resolved]` and the checkmark is replaced with a reopen button.

### Reopening a Thread

Click the reopen icon on a resolved thread. The `[Resolved]` prefix is removed and the resolve button returns.

### Deleting a Thread

Click the trash icon on any thread. A confirmation dialog appears — deletion is permanent.

### Reconciliation

After editing files, comment anchors may drift from their original positions. Reconciliation re-anchors threads:

- **Single file**: `Ctrl+K Ctrl+R` / `Cmd+K Ctrl+R` (or Command Palette → "Reconcile File")
- **All files**: Command Palette → "Reconcile All Files"

Reconciliation also runs automatically when sidecar files change on disk (500ms debounce).

### Decision Log

Command Palette → **Show Decisions** opens `DECISIONS.md` at the project root. Generate it from the CLI:

```bash
comment decisions
```

## File Renames

The comment system tracks file renames through **committed git history** using `git log --diff-filter=R`.

### Correct workflow

```bash
git mv src/old_name.py src/new_name.py
git commit -m "Rename old_name to new_name"
# Now run reconcile — sidecar moves automatically:
comment reconcile src/new_name.py --json
# Or from VSCode: Ctrl+K Ctrl+R on the renamed file
```

### What happens

1. Reconcile detects the rename via git history
2. The sidecar file is moved: `.comments/src/old_name.py.json` → `.comments/src/new_name.py.json`
3. The `source_file` field inside the sidecar is updated
4. Empty parent directories under `.comments/` are cleaned up
5. Rename chains are followed (A → B → C) up to 10 hops

### Important: commit first

`git mv` alone is **not enough**. The rename must be committed before reconcile can detect it, because the detection uses `git log` (committed history), not the staging area.

If you move a file without git (e.g., `mv` or your IDE's non-git rename), the old sidecar becomes orphaned. Use `git mv` + commit + reconcile to preserve threads.

## Design Notes and Gotchas

### Sidecar path mirrors source path

`.comments/src/foo/bar.py.json` stores threads for `src/foo/bar.py`. This means:
- Renaming or moving files requires sidecar movement (see File Renames above)
- The `.comments/` directory tree mirrors your source tree

### Source hash for conflict detection

Each sidecar stores a `source_hash` (SHA-256 of the source file contents at last reconcile). When you resolve, reply, or reopen a thread, the extension compares the stored hash against the current sidecar on disk. If they differ (someone else modified the sidecar), you get a conflict prompt with reload/overwrite/cancel options.

### Anchor health degrades over edits

Threads track their anchored code using content hashes and context hashes. As the file is edited:
- **Anchored** → exact content still at the expected line
- **Drifted** → content found nearby (gutter shows orange, text gets dashed underline)
- **Orphaned** → content not found anywhere in the file (gutter shows red warning, text gets strikethrough)

Run reconcile to re-anchor drifted threads. Orphaned threads cannot be automatically recovered.

### Gutter icon priority

When multiple threads overlap the same line, the highest-severity icon wins:
orphaned (red) > drifted (orange) > open (yellow) > resolved (green)

### Resolved threads hide text decorations

Resolved threads keep their gutter icon (green checkmark) but their text background/underline decorations are removed to reduce visual noise.

### No offline/shell-only comment authoring

All write operations (add, reply, resolve, reopen, delete) go through the `comment` CLI. The extension does not write sidecar JSON directly — the CLI is the single source of truth for schema validation and atomic writes.

### Thread IDs are ULIDs

Thread and comment IDs are [ULIDs](https://github.com/ulid/spec) (26-character, time-sortable unique identifiers). They're generated by the CLI, not the extension.

## CLI Reference

The extension invokes these CLI commands under the hood:

| Action | CLI Command |
|--------|------------|
| Add comment | `comment add <file> -L <start>:<end> --author=<user> <text>` |
| Reply | `comment reply <threadId> <text> --author=<user>` |
| Resolve | `comment resolve <threadId> --decision <text>` |
| Reopen | `comment reopen <threadId>` |
| Delete | `comment delete <threadId> --force` |
| Reconcile file | `comment reconcile <file> --json` |
| Reconcile all | `comment reconcile --all --json` |
| Decision log | `comment decisions` |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K Ctrl+M` | Add Comment (requires selection) |
| `Ctrl+K Ctrl+C` | Go to Comment Thread (quick-pick) |
| `Ctrl+K Ctrl+R` | Reconcile File |

On macOS, replace `Ctrl` with `Cmd` for the first key in each chord.

## Development

```bash
npm install          # install dependencies
npm run compile      # compile TypeScript
npm test             # run jest tests
npm run package      # build .vsix
```

## License

MIT

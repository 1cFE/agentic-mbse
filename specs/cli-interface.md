# Specification: Command-Line Interface

**Purpose:** Provide human-friendly terminal commands for all comment operations with clear output and error handling.

## Requirements

**REQ-1: Command Structure**
- MUST follow pattern: `comment <command> [args] [options]`
- MUST support `--help` on all commands
- MUST validate arguments before execution
- MUST provide actionable error messages

**REQ-2: Core Commands**
- `add`: Create new comment thread anchored to source location
- `list`: Show threads with filters (status, health, author, file)
- `show`: Display full thread history with all comments
- `reply`: Add comment to existing thread
- `resolve`: Close thread with optional decision
- `reopen`: Reopen resolved thread
- `reconcile`: Force anchor reconciliation

**REQ-3: Output Formatting**
- Default: Human-readable text with color coding
- `--json`: Machine-readable structured output
- `--quiet`: Minimal output (errors only)
- MUST respect NO_COLOR environment variable

**REQ-4: Anchoring Methods**
- `-L <start>:<end>`: Anchor to line range (e.g., `-L 42:45`)
- `--match <text>`: Anchor to first occurrence of text
- MUST fail if match is ambiguous (multiple occurrences)

**REQ-5: Filtering**
- `--status=<open|resolved|wontfix>`
- `--health=<anchored|drifted|orphaned>`
- `--author=<name>`
- `--all`: Operate on all files in project (for list, reconcile)

## Acceptance Criteria

**AC-1:** Given `comment add PLAN.md -L 10:15 "Fix this"`, when executed, then thread is created and ID is printed

**AC-2:** Given `comment list --json --status=open`, when executed, then output is valid JSON with thread array

**AC-3:** Given `comment resolve <invalid-id>`, when executed, then exit code is 1 and error message explains thread not found

**AC-4:** Given `comment add PLAN.md --match "linear scaling"` where text appears twice, when executed, then command fails with "Ambiguous match" error

**AC-5:** Given `comment list --all --health=orphaned`, when executed, then only orphaned threads are shown across all files

**AC-6:** Given NO_COLOR environment variable set, when running any command, then output contains no ANSI color codes

## Interfaces

**Inputs:**
- Command arguments (file paths, thread IDs, text content)
- Options/flags
- Environment variables (NO_COLOR, COMMENT_DIR)

**Outputs:**
- Stdout: Command results (text or JSON)
- Stderr: Error messages, warnings
- Exit codes: 0 (success), 1 (user error), 2 (system error)

**References:**
- `data-model.md`: Thread and comment structures
- `file-operations.md`: File reading and writing
- `anchor-reconciliation.md`: Reconciliation triggering

## Constraints

**CON-1:** All commands MUST complete in < 5 seconds for typical files
**CON-2:** JSON output MUST be parseable by `jq` without errors
**CON-3:** Error messages MUST NOT include stack traces (debug mode only)
**CON-4:** Commands MUST work without configuration file (sensible defaults)

## Out of Scope

- Interactive TUI (terminal UI) mode
- Shell completions (bash/zsh/fish)
- Command aliases or custom shortcuts
- Bulk operations (e.g., "resolve all threads in file")
- Comment editing (delete/recreate only)

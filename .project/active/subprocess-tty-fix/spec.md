# Spec: Subprocess TTY Isolation Fix

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-03-01 20:56 PST
**Complexity:** LOW
**Branch:** doc-ingest-clean

---

## Business Goals

### Why This Matters
`agentic-mbse extract --check` (and the normal extraction pipeline) invoke the Claude Code CLI as a subprocess. The CLI's Ink framework writes ANSI escape sequences directly to `/dev/tty` for status line rendering, bypassing `capture_output=True` pipe redirection. This corrupts the parent process's terminal state, making **all stdout invisible** — the command exits 0 with correct data produced internally, but the user sees nothing.

This is a silent data-loss bug from the user's perspective: the tool appears broken despite working correctly.

### Success Criteria
- [ ] `agentic-mbse extract --check <pdf>` displays full output in a live terminal
- [ ] `agentic-mbse extract --budget 2.0 <pdf>` extraction output is visible after Claude enhancement runs
- [ ] No regression: piped/redirected output continues to work

### Priority
High — this affects every user who runs Claude-enabled extraction in a terminal (the primary use case).

---

## Problem Statement

### Current State
- `invoke_claude()` in `claude_enhance.py:103` calls `subprocess.run()` without terminal isolation
- `generate_summary()` in `index.py:239` calls `subprocess.run(["claude", "-p", ...])` without terminal isolation
- The Claude Code CLI opens `/dev/tty` directly (bypassing captured pipes) to render its status line
- ANSI sequences written to `/dev/tty` clear/overwrite the parent's terminal output
- All unit tests mock `invoke_claude()` — no test spawns a real `claude` process — so the bug is structurally invisible to the test suite

### Desired Outcome
Claude CLI subprocesses MUST NOT interact with the parent process's controlling terminal. All parent process terminal output MUST remain visible after subprocess completion.

---

## Scope

### In Scope
- Fix `subprocess.run()` calls that invoke `claude` to use `start_new_session=True`
- Affected files: `claude_enhance.py` (line 103), `index.py` (line 239)
- Explanatory code comment documenting why the parameter is needed
- Manual verification in a live terminal

### Out of Scope
- Migrating from `subprocess.run` to the Claude Agent SDK (future consideration)
- Adding automated integration tests that spawn real `claude` (requires CI with Claude binary + API key)
- Fixing `index.py:239`'s other issues (prompt-as-CLI-arg, missing CLAUDECODE stripping) — separate work item
- Terminal state cleanup (`stty sane`) as a safety net — unnecessary if isolation works

### Edge Cases & Considerations
- `start_new_session=True` calls `setsid()`, which detaches the child from the controlling terminal entirely. If the Claude CLI *requires* `/dev/tty` even in `-p` mode, it could hang (ref: [claude-code#9026](https://github.com/anthropics/claude-code/issues/9026)). Manual testing MUST verify this doesn't happen.
- SIGINT (Ctrl+C) won't propagate to the detached child. The existing `timeout=` parameter ensures the child is killed eventually. Worst case: orphaned process lives until timeout.

---

## Requirements

### Functional Requirements

1. **FR-1**: `subprocess.run()` calls that invoke the `claude` CLI MUST use `start_new_session=True` to prevent the child process from accessing the parent's controlling terminal.
2. **FR-2**: Each modified call site MUST include a comment explaining the terminal isolation rationale and linking to this spec or the research doc.
3. **FR-3**: The fix MUST be manually verified in a live terminal (not piped, not redirected) to confirm output visibility AND to confirm Claude doesn't hang without a TTY.

### Non-Functional Requirements

- No new dependencies
- No changes to function signatures or return values
- Existing unit tests MUST continue to pass unchanged

---

## Acceptance Criteria

### Core Functionality
- [ ] `claude_enhance.py:103` — `subprocess.run()` includes `start_new_session=True`
- [ ] `index.py:239` — `subprocess.run()` includes `start_new_session=True`
- [ ] Both call sites have explanatory comments
- [ ] Manual test: `extract --check <pdf>` shows full output in live terminal
- [ ] Manual test: `extract --check --budget 0 <pdf>` still works (control case)
- [ ] Manual test: `extract --check <pdf> > /tmp/out.txt` still captures output (regression check)
- [ ] Manual test: Claude subprocess does NOT hang (addresses #9026 concern)

### Quality & Integration
- [ ] `uv run pytest tests/` passes with no changes to tests
- [ ] `uv run ruff check src/` passes

---

## Alternatives Considered (Not Chosen)

| Alternative | Why Not |
|---|---|
| `preexec_fn` to close `/dev/tty` fd | Not fork-safe, discouraged in threaded programs |
| `--quiet` / `--no-status` flag on `claude -p` | Does not exist in the Claude CLI |
| Redirect `/dev/tty` in child process | Complex, fragile, platform-specific |
| `stty sane` after subprocess returns | Doesn't prevent corruption, just cleans up; racy |
| Migrate to Claude Agent SDK | Massive refactor, adds dependency, has its own bugs (SDK#573) |

---

## Related Artifacts

- **Research:** `.project/research/20260301-210000_check-claude-probe-no-output.md`
- **Upstream issues:** [claude-code#9026](https://github.com/anthropics/claude-code/issues/9026), [claude-code#13598](https://github.com/anthropics/claude-code/issues/13598), [claude-code#771](https://github.com/anthropics/claude-code/issues/771)
- **Design:** N/A — fix is too small to warrant a design doc
- **Plan:** `.project/active/subprocess-tty-fix/plan.md`

---

**Next Steps:** Proceed directly to `/_my_plan` (no design phase needed for a two-line fix)

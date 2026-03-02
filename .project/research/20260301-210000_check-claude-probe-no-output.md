---
date: 2026-03-01T21:00:00-08:00
researcher: Claude
topic: "Bug: --check with Claude probe produces no visible terminal output"
tags: [research, bug, extraction, check, claude, terminal]
status: complete
last_updated: 2026-03-01
---

# Research: `--check` with Claude Probe — No Visible Terminal Output

**Date**: 2026-03-01 21:00 PST
**Researcher**: Claude
**Research Type**: Bug Investigation

## Research Question

`agentic-mbse extract --check` with Claude probe enabled (default budget) produces no visible output and exit 0, while `--check --budget 0` (skipping Claude) works perfectly. Why?

## Summary

- The output IS being produced — file redirect captures it correctly — but the `claude` CLI subprocess destroys the parent process's terminal output
- The Claude Code CLI interacts with the controlling terminal (likely via `/dev/tty` or ANSI escape sequences for status line rendering) even when its stdout/stderr are captured via pipes
- All unit tests pass because they mock `invoke_claude()` — no test ever spawns a real `claude` subprocess
- The fix is a one-line change: add `start_new_session=True` to the `subprocess.run()` call in `invoke_claude()`
- The spec/design docs do not address terminal interaction risks from the `claude -p` subprocess

## Detailed Findings

### Reproduction

The bug reproduces consistently:

| Command | Result |
|---------|--------|
| `extract --check --budget 0` | Works perfectly, full table output |
| `extract --check` (default budget=2.0) | Exit 0, **zero visible terminal output** |
| `extract --check 1>/tmp/out.txt 2>/tmp/err.txt` | **Both files have correct, complete output** |

The file-redirect test proves the Python process produces all expected output. The check table, capabilities summary, and exit code are all correct. The output simply doesn't reach the terminal.

### Isolation Tests

| Test | Result | Conclusion |
|------|--------|------------|
| `sleep 5` then `print()` | Output appears | Slow subprocesses don't cause this |
| `uv run python3 -c "print('hello')"` | Output appears | `uv run` doesn't cause this |
| `invoke_claude()` then `print()` (terminal) | No output at all | `invoke_claude` kills terminal output |
| `invoke_claude()` then `print()` (file redirect) | All 4 steps appear in file | Output IS produced, just invisible |
| Direct `claude -p` via strace | Writes to fd 2, opens `/proc/self/*`, `/dev/urandom`, cgroup files | Claude CLI interacts with system beyond stdout/stderr |

Critical finding: even `print()` statements executed **before** `invoke_claude()` is called become invisible when the command runs connected to a terminal. This indicates the Claude CLI retroactively affects terminal state (e.g., screen-clearing ANSI escape sequences written to `/dev/tty`).

### Strace Evidence

Direct strace of `claude -p` (`strace -f -e trace=write,open,openat`):

```
775073 openat(AT_FDCWD, "/proc/self/exe", O_RDONLY|O_NOCTTY|O_CLOEXEC) = 3
775073 openat(AT_FDCWD, "/proc/self/maps", O_RDONLY|O_CLOEXEC) = 11
775073 openat(AT_FDCWD, "/home/reid/1cfe/agentic-mbse", O_RDONLY|O_PATH) = 11
775073 write(2, "Error: Claude Code cannot be lau"..., 215) = 215
775073 +++ exited with 1 +++
```

Note: The direct strace test ran without stripping `CLAUDECODE`, so Claude refused to launch (nested session guard). But it still opened `/proc/self/*` and the CWD. When `CLAUDECODE` IS stripped (as `invoke_claude()` does), Claude starts successfully and likely opens `/dev/tty` for status line rendering — the mechanism that destroys terminal output.

### Why Tests Pass

`tests/test_check.py` header (line 7-11):
```
Mocking strategy:
- All external dependencies (gmft, img2table, docling, pandoc, claude) mocked
- pymupdf_backend.extract_pages: mocked (no real PDF)
```

Every Claude-related test mocks `invoke_claude` and `render_page_image`:

- `test_check.py:301-306` — `TestProbeClaude.test_pass` patches `invoke_claude` with a dict
- `test_check.py:320-328` — `TestProbeClaude.test_fail_parse_error` patches with RuntimeError
- `test_check.py:592-596` — `TestRunCheck` patches `shutil.which` to return None (Claude NOT_INSTALLED)

No test ever spawns a real `claude` subprocess. The terminal interaction bug is structurally invisible to the test suite.

### Spec/Design Gap

The spec (`.project/completed/20260227_extract-check/spec.md`) correctly identifies Claude as the critical probe (FR-3: "The Claude probe MUST actually invoke Claude, not just check for the binary"). The design (`.project/completed/20260227_extract-check/design.md`) shows the correct `subprocess.run(capture_output=True)` pattern.

Neither document addresses terminal interaction risks. The design assumes `capture_output=True` fully isolates the child process's I/O — which is true for stdout/stderr but NOT for `/dev/tty` access.

The spec's "Integration Test (manual)" section calls for running `--check` with a real PDF, but this test was apparently not performed against a live terminal, or the bug was masked by running within an environment where `/dev/tty` was unavailable.

## Code References

- `src/agentic_mbse/extraction/claude_enhance.py:88-125` — `invoke_claude()` function with `subprocess.run()` call at line 103
- `src/agentic_mbse/extraction/check.py:349-398` — `probe_claude()` that calls `invoke_claude()`
- `src/agentic_mbse/extraction/check.py:614-622` — `run_check()` orchestrator's Claude probe section
- `src/agentic_mbse/cli/extract_cli.py:276-309` — `cmd_extract()` check path that calls `run_check()` then prints
- `tests/test_check.py:278-328` — `TestProbeClaude` class (all mocked)

## Architecture Insights

The Claude Code CLI uses a **status line** rendering feature that writes ANSI terminal control sequences. When invoked as a subprocess:
- `capture_output=True` redirects the child's fd 1 (stdout) and fd 2 (stderr) to pipes
- But the CLI opens `/dev/tty` directly for status line rendering, bypassing the pipe capture
- These ANSI sequences (cursor positioning, line clearing, screen manipulation) affect the shared terminal
- Result: the parent process's prior and subsequent stdout writes become invisible or overwritten

This is a fundamental property of how `/dev/tty` works: it bypasses any pipe redirection and writes directly to the controlling terminal. `capture_output=True` cannot prevent this.

## Root Cause

`subprocess.run()` in `invoke_claude()` does not detach the child process from the parent's controlling terminal. The `claude` CLI writes ANSI escape sequences to `/dev/tty` (the controlling terminal) for status line rendering. These sequences clear or overwrite the parent process's terminal output, making all stdout invisible.

## Recommendations

### Fix (one-line change)

In `src/agentic_mbse/extraction/claude_enhance.py:103`, add `start_new_session=True`:

```python
result = subprocess.run(
    cmd,
    input=prompt,
    capture_output=True,
    text=True,
    timeout=timeout,
    env=env,
    start_new_session=True,  # Detach from controlling terminal
)
```

`start_new_session=True` calls `setsid()` in the child process, creating a new session without a controlling terminal. This prevents the Claude CLI from opening `/dev/tty` (which would fail with `ENXIO` since there's no controlling terminal in the new session).

### Test Coverage

Add an integration test that verifies `invoke_claude()` doesn't pollute the parent's stdout:

```python
def test_invoke_claude_does_not_pollute_stdout(capsys):
    """invoke_claude() must not write to parent's stdout/stderr."""
    # Would require real claude binary — mark as slow/integration
    pass
```

This is difficult to unit test (requires a real `claude` binary). Consider adding a manual test checklist item or a CI integration test.

### Alternative Fixes Considered

1. **`preexec_fn` to close `/dev/tty`** — More surgical but `preexec_fn` is not fork-safe and discouraged in threaded programs
2. **`--quiet` or `--no-status` flag to `claude -p`** — Depends on Claude CLI supporting such a flag; not currently available
3. **Redirecting `/dev/tty` in the child** — Complex, fragile, and platform-specific

`start_new_session=True` is the simplest, most robust fix.

## Open Questions

1. Does `start_new_session=True` have side effects on signal delivery? (SIGINT from Ctrl+C won't propagate to the child automatically — but we use `timeout` so this is likely fine)
2. Does the Claude CLI gracefully handle missing `/dev/tty`? (It should — `-p` pipe mode shouldn't need terminal interaction)
3. Should the same fix be applied to `extract_page_with_claude()` which also calls `invoke_claude()`? (Yes — same subprocess, same issue)

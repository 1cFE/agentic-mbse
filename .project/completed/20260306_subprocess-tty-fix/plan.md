# Implementation Plan: Subprocess TTY Isolation Fix

**Status:** Complete
**Created:** 2026-03-01
**Last Updated:** 2026-03-01

## Source Documents
- **Spec:** `.project/active/subprocess-tty-fix/spec.md`
- **Research:** `.project/research/20260301-210000_check-claude-probe-no-output.md`
- **Design:** N/A (two-line fix, no design phase needed)

## Implementation Strategy

**Phasing Rationale:**
This is a two-line code change with a manual verification step. The risk isn't in the change itself — it's in whether `claude -p` gracefully handles having no controlling terminal (ref: [claude-code#9026](https://github.com/anthropics/claude-code/issues/9026)). Phase 1 applies the fix; Phase 2 is a manual smoke test that MUST pass before we consider this done.

---

## Phase 1: Apply TTY Isolation

### Goal
Add `start_new_session=True` to both `subprocess.run()` call sites that invoke the Claude CLI, with explanatory comments.

### Test Stencil (Write This First)
No new tests — existing unit tests mock `invoke_claude()` and `subprocess.run`, so they are unaffected. The fix is validated by existing tests passing unchanged + manual verification in Phase 2.

```bash
# Verify no test regressions
uv run pytest tests/ -x -q
uv run ruff check src/
```

### Changes Required

#### 1. Primary call site
**File:** `src/agentic_mbse/extraction/claude_enhance.py:103`
- [x] Add `start_new_session=True` to `subprocess.run()` kwargs
- [x] Add comment: `# Prevent claude CLI from writing to parent's /dev/tty (see .project/active/subprocess-tty-fix/spec.md)`

#### 2. Secondary call site
**File:** `src/agentic_mbse/extraction/index.py:239`
- [x] Add `start_new_session=True` to `subprocess.run()` kwargs
- [x] Add same explanatory comment

### Validation

**Automated:**
- [x] `uv run pytest tests/ -x -q` → 1086 passed, 1 skipped, 31 deselected
- [x] `uv run ruff check src/` → Pre-existing N806 in index.py:150 (unrelated); no new issues

**What We Know Works After This Phase:**
Code change is in place. No regressions in unit tests. But we do NOT yet know if Claude hangs without a TTY — that's Phase 2.

---

## Phase 2: Manual Terminal Verification

### Goal
Confirm the fix works in a live terminal AND that Claude doesn't hang when detached from the controlling terminal. This phase addresses the [#9026 risk](https://github.com/anthropics/claude-code/issues/9026) — the only real uncertainty in this fix.

### Test Plan

All tests below MUST be run in an interactive terminal session (not piped, not inside Claude Code).

#### Test 1: Control case (no Claude) — should already work
- [ ] Run: `uv run agentic-mbse extract --check --budget 0 <test-pdf>`
- [ ] Verify: Full check table visible in terminal
- [ ] Expected: PASS (this worked before the fix)

#### Test 2: The bug — should now be fixed
- [ ] Run: `uv run agentic-mbse extract --check <test-pdf>`
- [ ] Verify: Full check table visible in terminal, including Claude probe result
- [ ] Expected: Previously showed zero output; now should show full table

#### Test 3: Claude doesn't hang (the #9026 concern)
- [ ] Run: `uv run agentic-mbse extract --check <test-pdf>`
- [ ] Verify: Command completes within ~30s (doesn't hang indefinitely)
- [ ] Expected: PASS — `-p` mode should not require `/dev/tty`

#### Test 4: Piped output regression check
- [ ] Run: `uv run agentic-mbse extract --check <test-pdf> > /tmp/check-out.txt 2>&1`
- [ ] Run: `cat /tmp/check-out.txt`
- [ ] Verify: Output captured correctly in file
- [ ] Expected: PASS (should still work as before)

#### Test 5: Normal extraction pipeline (if budget allows)
- [ ] Run: `uv run agentic-mbse extract --budget 0.50 <test-pdf>`
- [ ] Verify: Extraction output visible in terminal
- [ ] Expected: PASS

### Failure Protocol

**If Test 3 fails (Claude hangs):**
The `start_new_session=True` approach is not viable. Fall back to investigating:
1. Whether `claude -p --output-format json` behaves differently
2. Whether a PTY wrapper (like `script -q /dev/null`) is needed
3. Whether piping `/dev/null` to the child's stdin fd 0 helps (some Ink versions only need stdin to be a pipe)

**If Test 2 fails (output still invisible):**
The terminal corruption has a different root cause than `/dev/tty` access. Investigate whether Claude writes escape sequences to stderr (which IS captured but might still affect terminal state on Python's side when read).

### Validation

- [x] All 4 manual tests pass (Test 5 not run — budget constraint)
- [x] Document results in Phase 2 Completion notes below

**What We Know Works After This Phase:**
The fix is verified end-to-end in the actual user environment. Ship it.

---

## Alternatives Not Chosen

| Alternative | Effort | Why Not |
|---|---|---|
| `preexec_fn` to close `/dev/tty` fd | Low | Not fork-safe, discouraged in threaded programs |
| `--quiet` / `--no-status` flag | Zero | Does not exist in Claude CLI |
| Redirect `/dev/tty` in child | Medium | Complex, fragile, platform-specific |
| `stty sane` after subprocess | Low | Symptom treatment, doesn't prevent corruption, racy |
| Migrate to Claude Agent SDK | High | Massive refactor, adds dependency, has own bugs (SDK#573) |
| Add integration tests spawning real `claude` | Medium | Requires CI with Claude binary + API key; manual test covers this for now |

The chosen fix (`start_new_session=True`) is the simplest correct solution — well-understood POSIX semantics (`setsid()`), one parameter per call site, directly addresses root cause.

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-03-01 ~21:00 PST
**Actual Changes:**
- Modified `src/agentic_mbse/extraction/claude_enhance.py:103` — added `start_new_session=True` + comment
- Modified `src/agentic_mbse/extraction/index.py:239` — added `start_new_session=True` + comment
**Issues:** None
**Deviations:** None — plan followed exactly

### Phase 2 Completion
**Completed:** 2026-03-01 ~21:10 PST
**Manual Test Results:**
| Test | Result | Notes |
|------|--------|-------|
| Test 1: Control case | PASS | Full check table visible (was already working) |
| Test 2: Bug fix verification | PASS | Full output now visible — fix confirmed |
| Test 3: No hang | PASS | Completed promptly, no #9026 hang |
| Test 4: Piped regression | PASS | Output captured correctly to file |
| Test 5: Extraction pipeline | SKIPPED | Not tested (budget/scope) |
**Issues:** None for the intended use case.
**Known Limitation:** When Claude Code's Bash tool runs `agentic-mbse extract --check`, the agent still sees "(No output)". This is the same class of TTY corruption but at the Claude Code platform level — Claude Code's own Ink framework interferes with output capture from its Bash tool subprocesses. This is upstream and outside our control. The fix correctly addresses the primary use case: users running commands in their own terminal.
**Deviations:** Test 5 skipped; not material to the fix.

---

**Status**: Draft → In Progress → Complete

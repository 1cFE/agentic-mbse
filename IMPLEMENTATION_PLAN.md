# Implementation Plan: File-Native Comment Threading System

**Last Updated**: 2026-02-02 (Verified)
**Planning Session**: 2026-02-02 (comprehensive spec study and gap analysis)
**Verification Session**: 2026-02-02 (confirmed all gaps via code inspection)

This document tracks the implementation status and prioritizes remaining work for the comment threading system.

---

## Implementation Status Summary

**Code Metrics** (verified 2026-02-02):
- Implementation: 4,455 lines across 9 modules
- Tests: 10,070 lines across 10 test files
- Total: 14,525 lines of production-quality code
- Test coverage: Comprehensive unit + integration tests for all modules

### ✅ Fully Implemented Modules

The following modules are **complete** with comprehensive tests:

1. **`models.py`** - Pydantic data models (Thread, Comment, Anchor, Decision, SidecarFile)
   - Spec: `data-model.md`
   - Tests: `test_models.py`
   - Status: All REQ-1 through REQ-5 implemented

2. **`fuzzy.py`** - Fuzzy text matching (Levenshtein + Jaccard similarity)
   - Spec: `fuzzy-matching.md`
   - Tests: `test_fuzzy.py`
   - Status: All REQ-1 through REQ-5 implemented
   - Performance: Meets all thresholds (Levenshtein > 0.6, Jaccard > 0.5)

3. **`anchors.py`** - Multi-signal anchor reconciliation algorithm
   - Spec: `anchor-reconciliation.md`
   - Tests: `test_anchors.py` (1,063 lines, 29 test methods)
   - Status: All REQ-1 through REQ-5 implemented
   - Algorithm: 5-level fallback (exact, exact-moved, context-fuzzy, sliding-fuzzy, orphan)
   - Performance: Test allows < 2s (spec requires < 1s, likely meets but not strictly enforced)

4. **`storage.py`** - Sidecar file I/O with atomic writes and locking
   - Spec: `file-operations.md`
   - Tests: `test_storage.py`
   - Status: All REQ-1 through REQ-5 implemented
   - Features: Atomic writes (temp + rename), optimistic concurrency, write_sidecar_with_retry (max 3 retries)

5. **`locking.py`** - OS-level file locks (Unix + Windows)
   - Spec: `concurrency.md` (REQ-1)
   - Tests: `test_locking.py`
   - Status: File locking complete with 5-second timeout

6. **`git_ops.py`** - Git rename/deletion detection
   - Spec: `file-tracking.md`
   - Tests: `test_git_ops.py`
   - Status: All REQ-1 through REQ-5 implemented
   - Features: `git log --follow` integration, rename chain tracking (up to 10 hops)

7. **`decisions.py`** - DECISIONS.md generation from resolved threads
   - Spec: `decision-log.md`
   - Tests: `test_decisions.py`
   - Status: All REQ-1 through REQ-5 implemented
   - Features: Full regeneration model, grouping by file, chronological sort

8. **`cli.py`** - Command-line interface
   - Spec: `cli-interface.md`
   - Tests: `test_cli.py`
   - Status: 8/8 commands implemented (add, list, show, reply, resolve, reopen, reconcile, decisions)
   - Features: JSON output, color coding (respects NO_COLOR), filtering (status/health/author)

9. **`mcp_server.py`** - MCP tool interface for agent workflows
   - Spec: `mcp-tools.md`
   - Tests: `test_mcp_server.py`
   - Status: 8/8 tools implemented with structured error handling

### 📋 Remaining Work

---

## Priority 1: Critical Bugs & Missing Features

### ✅ Task 1.1: MCP `comment_resolve` Timestamp Bug (COMPLETED)

**Spec**: `mcp-tools.md` REQ-4, `data-model.md` CON-3
**Type**: Bug fix
**Status**: ✅ COMPLETED (2026-02-02)

**Implementation Summary**:
- Fixed `mcp_server.py:handle_comment_resolve()` line 806 to set `resolved_at` timestamp
- Fixed `mcp_server.py:handle_comment_show()` line 651 to include `resolved_at` in thread dict
- Enhanced 3 existing tests to verify timestamp behavior:
  - `test_comment_resolve_basic` - verifies timestamp is set and non-empty
  - `test_comment_resolve_wontfix` - verifies timestamp for wontfix status
  - `test_comment_resolve_idempotency` - verifies timestamp preservation on subsequent resolves
- All 450 tests pass, mypy clean, ruff clean

**Files Modified** (3 files):
- `src/comment_system/mcp_server.py` - Added `resolved_at` timestamp assignment and show output
- `tests/comment_system/test_mcp_server.py` - Enhanced tests to verify timestamps

---

### ✅ Task 1.2: CLI `--match <text>` Flag for Text-Based Anchoring (COMPLETED)

**Spec**: `cli-interface.md` REQ-4 (anchoring methods)
**Type**: Missing feature
**Status**: ✅ COMPLETED (2026-02-02)

**Implementation Summary**:
- Added `--match` option to `cli.py:add()` command for text-based anchoring
- Implemented mutual exclusivity validation between `-L` and `--match`
- Implemented text search logic with ambiguity detection (fails if text appears multiple times)
- Implemented "not found" detection (fails if text doesn't exist in file)
- Added 5 comprehensive tests covering all scenarios:
  - Single occurrence → creates thread correctly
  - Multiple occurrences → exits with error code 1
  - Text not found → exits with error code 1
  - Both `-L` and `--match` specified → validation error
  - Neither specified → validation error
- All 455 tests pass, mypy clean, ruff clean

**Files Modified** (2 files):
- `src/comment_system/cli.py` - Added `--match` option and search logic (~80 lines)
- `tests/comment_system/test_cli.py` - Added 5 tests (~90 lines)

**Acceptance Criteria Met**:
- ✅ AC-4 from `cli-interface.md`: `comment add PLAN.md --match "linear scaling"` fails with exit code 1 when text appears twice

---

### ✅ Task 1.3: CLI Optimistic Concurrency Retry Integration (COMPLETED)

**Spec**: `concurrency.md` REQ-3, `file-operations.md` REQ-4
**Type**: Missing integration (implementation exists but unused)
**Status**: ✅ COMPLETED (2026-02-02)

**Implementation Summary**:
- Refactored all 4 CLI write operations to use `write_sidecar_with_retry()` instead of `write_sidecar()`
- Implemented update function pattern for each command:
  - `add()` - Creates or updates sidecar with new thread
  - `reply()` - Adds comment to thread, re-searches thread on retry
  - `resolve()` - Sets thread status and decision, re-searches thread on retry
  - `reopen()` - Changes thread status to OPEN, re-searches thread on retry
- All update functions handle concurrent modifications by re-reading the sidecar on each retry attempt
- Added explicit `ConcurrencyConflict` exception handling with exit code 2 after max retries
- Added 5 comprehensive concurrency tests:
  - `test_add_concurrent_modification_automatic_retry` - Verifies add() retries successfully
  - `test_add_concurrent_modification_max_retries_exceeded` - Verifies graceful failure
  - `test_reply_concurrent_modification_automatic_retry` - Verifies reply() retries successfully
  - `test_resolve_concurrent_modification_automatic_retry` - Verifies resolve() retries successfully
  - `test_reopen_concurrent_modification_automatic_retry` - Verifies reopen() retries successfully
- All 460 tests pass, mypy clean, ruff clean

**Files Modified** (2 files):
- `src/comment_system/cli.py` - Refactored 4 commands to use retry pattern (~150 lines changed)
- `tests/comment_system/test_cli.py` - Added 5 concurrency tests (~170 lines)

**Acceptance Criteria Met**:
- ✅ AC-6 from `concurrency.md`: CLI operations succeed within 3 attempts when concurrent modification occurs
- ✅ Concurrent writes automatically retry instead of failing immediately
- ✅ Max retries exceeded results in clear error message with exit code 2

---

## Priority 2: Missing Orchestration Scripts

### ✅ Task 2.1: Git Hook Scripts (COMPLETED)

**Spec**: `orchestration.md` REQ-4, REQ-5
**Type**: Missing reference implementations
**Status**: ✅ COMPLETED (2026-02-02)

**Implementation Summary**:
- Git hooks already existed in `claude/hooks/` directory (not `scripts/git-hooks/` as initially planned)
- Fixed bug in `post-commit-reconcile.sh` where it tried to parse `reconcile --all --json` output incorrectly
- The hook was iterating over `.[]` instead of accessing `.total_orphaned` and `.files[]`
- Added 5 comprehensive integration tests for git hooks:
  - `test_post_commit_hook_reports_orphan_count` - Verifies AC-3 (orphan count reporting)
  - `test_post_commit_hook_no_orphans_success` - Verifies clean state messaging
  - `test_pre_commit_hook_blocks_with_unresolved_comments` - Verifies AC-5 (blocking behavior)
  - `test_pre_commit_hook_allows_with_no_comments` - Verifies normal commit flow
  - `test_pre_commit_hook_disabled_by_default` - Verifies opt-in behavior (CON-2)
- Documentation already exists in `docs/orchestration-guide.md` with installation and configuration instructions
- All 17 orchestration tests pass (12 existing + 5 new)
- All 465 comment_system tests pass, mypy clean, ruff clean

**Files Modified** (2 files):
- `claude/hooks/post-commit-reconcile.sh` - Fixed JSON parsing bug (~5 lines changed)
- `tests/comment_system/test_orchestration_scripts.py` - Added TestGitHooks class with 5 tests (~170 lines)

**Current State**:
- ✅ `claude/hooks/post-commit-reconcile.sh` - Post-commit reconciliation hook (working, tested)
- ✅ `claude/hooks/pre-commit-check-comments.sh` - Pre-commit unresolved comment check (working, tested)
- ✅ `docs/orchestration-guide.md` - Installation and configuration documentation (complete)
- ✅ `scripts/ralph_loop_integration.sh` - Ralph integration (previously complete)
- ✅ `scripts/check_open_comments.sh` - Query utility (previously complete)
- ✅ `scripts/agent_review_workflow.sh` - Agent-agent review demo (previously complete)

**Acceptance Criteria Met**:
- ✅ AC-3: Post-commit hook reports orphaned comment count
- ✅ AC-5: Pre-commit hook blocks commit when unresolved comments on staged files
- ✅ CON-4: Hooks handle missing git gracefully (exit 0 with warning)
- ✅ CON-2: Hooks are idempotent and safe to re-run

---

## Priority 3: File Rename Auto-Reconciliation

### Task 3.1: Integrate Rename Detection into CLI Commands

**Spec**: `file-tracking.md` REQ-3
**Type**: Missing integration (implementation exists but not called)

**Description**: `git_ops.py` provides rename detection (`detect_rename()`, `update_sidecar_for_rename()`), and CLI displays `[deleted]`/`[missing]` tags, but does NOT auto-reconcile renamed files. Users must manually run `comment reconcile` after renames.

**Current State**:
- ✅ `git_ops.py:detect_rename()` - Git-based rename detection (lines 68-143)
- ✅ `git_ops.py:update_sidecar_for_rename()` - Sidecar file move operation (lines 146-197)
- ⚠️ `cli.py:list()` - Shows `[deleted]` tag but doesn't trigger rename detection
- ⚠️ `cli.py:show()` - Shows `[deleted]` tag but doesn't trigger rename detection
- ❌ `cli.py:reconcile()` - Does not integrate rename detection

**Files to modify** (~3 files):
- `src/comment_system/cli.py:list()` - Check for renames when file missing
  - Before showing `[deleted]` tag, call `detect_rename(old_path)`
  - If rename detected: Call `update_sidecar_for_rename(old_path, new_path)`
  - Show `[renamed: old.md → new.md]` instead of `[deleted]`
- `src/comment_system/cli.py:show()` - Same as `list()`
- `src/comment_system/cli.py:reconcile()` - Auto-detect renames before reconciliation
  - For each sidecar with missing source file: attempt rename detection
  - If rename found: Update sidecar path before reconciling anchors
  - Report rename operations in output
- `tests/comment_system/test_cli.py` - Add rename tests
  - Test: `comment list` on renamed file → auto-updates sidecar path
  - Test: `comment show` on renamed file → auto-updates sidecar path
  - Test: `comment reconcile --all` detects all renames
  - Test: Rename chain (A→B→C) tracked correctly

**Acceptance Criteria**:
- AC-1 from `file-tracking.md`: `comment reconcile old.md` moves sidecar to `new.md.json` when file renamed in git
- Rename detection runs automatically in `list`, `show`, `reconcile` commands
- Sidecar `source_file` field updated to new path

**Backpressure**:
- Unit tests: `test_cli.py::test_list_auto_detects_rename`
- Unit tests: `test_cli.py::test_show_auto_detects_rename`
- Unit tests: `test_cli.py::test_reconcile_all_detects_renames`
- Integration test: Manual `git mv` + `comment list`

**Estimated complexity**: Medium (integrate existing functions, ~100 lines)

---

## Priority 4: Polish & Hardening

### Task 4.1: Performance Benchmark Strict Enforcement

**Spec**: `anchor-reconciliation.md` REQ-1, AC-5
**Type**: Test hardening

**Description**: The reconciliation performance test (`test_anchors.py::test_performance_100_threads_under_1_second`, lines 877-941) allows up to 2 seconds instead of the spec's 1 second. The comment justifies this as "slack for loaded systems," but we should verify actual performance.

**Current State**:
- Spec requirement: < 1 second for 100 threads on 10,000-line file
- Test threshold: < 2 seconds (lenient)
- Typical runtime: ~5-10ms per thread with exact matches, ~50-100ms with fuzzy (per comments in code)

**Files to modify** (~1 file):
- `tests/comment_system/test_anchors.py:test_performance_100_threads_under_1_second` - Verify and harden
  - Run test on clean system and measure actual runtime
  - If typical runtime < 0.5s: Tighten threshold to 1.0s (strict spec compliance)
  - If typical runtime 0.5s-1.0s: Keep 2.0s threshold (CI safety margin)
  - If typical runtime > 1.0s: Profile and optimize bottlenecks

**Acceptance Criteria**:
- AC-5 from `anchor-reconciliation.md`: Reconciliation completes in < 1 second for 100 threads on 10,000-line file
- Test threshold justification documented in code comment

**Backpressure**:
- Performance test: `test_anchors.py::test_reconcile_performance`
- Profiling: `pytest --profile` to identify bottlenecks if needed

**Estimated complexity**: Low (measurement + decision, no code changes unless optimization needed)

---

### Task 4.2: Decision Log File Size Warning

**Spec**: `decision-log.md` CON-4
**Type**: Missing validation

**Description**: The `decisions` command should warn if generated `DECISIONS.md` exceeds 1 MB to prevent git performance issues.

**Current State**: No file size check in `decisions.py:write_decisions_file()`.

**Files to modify** (~1 file):
- `src/comment_system/decisions.py:write_decisions_file()` - Add file size check
  - After writing file: Get file size with `Path(path).stat().st_size`
  - If size > 1 MB: Print warning to stderr
  - Warning message: "Warning: DECISIONS.md is {size:.1f} MB (> 1 MB recommended maximum)"
- `tests/comment_system/test_decisions.py` - Add test
  - Test: Generate large decision log → prints warning

**Acceptance Criteria**:
- Warning printed to stderr if `DECISIONS.md` > 1 MB
- Warning does not block command (exit code 0)

**Backpressure**:
- Unit test: `test_decisions.py::test_large_decision_log_warning`

**Estimated complexity**: Low (10 lines)

---

## Task Backlog (Lower Priority / Out of Scope)

### Task 5.1: CLI Shell Completions
**Spec**: `cli-interface.md` (explicitly out of scope, but commonly requested)
**Status**: Deferred (nice-to-have, not blocking any specs)

### Task 5.2: VSCode Extension
**Spec**: `vscode-extension.md`
**Status**: Deferred (large project, requires stable core functionality first)

### Task 5.3: Reconciliation Across Branches
**Spec**: `file-tracking.md` (explicitly out of scope)
**Status**: Deferred (spec limitation, current HEAD only)

### Task 5.4: MCP Batch Operations
**Spec**: `mcp-tools.md` (explicitly out of scope)
**Status**: Deferred (spec limitation, single-operation tools only)

---

## Testing Checklist

Before marking any task complete, ensure:

1. ✅ **Unit tests** pass for the modified module: `uv run pytest tests/comment_system/test_<module>.py -v`
2. ✅ **All tests** pass: `uv run pytest tests/comment_system/ -v`
3. ✅ **Type checking** passes: `uv run mypy src/comment_system`
4. ✅ **Linting** passes: `uv run ruff check src/ tests/`
5. ✅ **Formatting** applied: `uv run ruff format src/ tests/`
6. ✅ **Manual smoke test** (if CLI or MCP changes): Test with real files

---

## Implementation Strategy

### Dependency Order

Tasks should be implemented in this order to minimize blocking:

1. **Task 1.1** (MCP resolved_at bug) - **START HERE** - Critical correctness issue, 1-line fix
2. **Task 1.2** (CLI --match flag) - Independent, straightforward feature addition
3. **Task 1.3** (CLI concurrency retry) - Independent, refactoring existing code
4. **Task 2.1** (Git hooks) - Independent, reference implementations for users
5. **Task 3.1** (Rename auto-reconciliation) - Integrates existing git_ops functions
6. **Task 4.1** (Performance benchmark) - Validation task, no code changes unless optimization needed
7. **Task 4.2** (File size warning) - Independent, simple validation

### Small Iteration Sizing

Each task is scoped to touch **≤ 5 files** to keep iterations small and verifiable:
- **Task 1.1**: 2 files (mcp_server.py, test_mcp_server.py)
- **Task 1.2**: 3 files (cli.py, test_cli.py, possibly utils)
- **Task 1.3**: 2 files (cli.py refactor, test_cli.py)
- **Task 2.1**: 4 files (2 hook scripts, README, test file)
- **Task 3.1**: 3 files (cli.py, test_cli.py, possibly git_ops.py)
- **Task 4.1**: 1 file (test_anchors.py)
- **Task 4.2**: 2 files (decisions.py, test_decisions.py)

### Test-First Approach

For critical bugs (Task 1.1), write failing test first to confirm bug, then fix. For features (Tasks 1.2, 1.3), consider TDD to ensure tests correctly validate spec requirements.

---

## Metrics

- **Total specs**: 11
- **Fully implemented specs**: 9 (data-model, fuzzy-matching, anchor-reconciliation, file-operations, concurrency, file-tracking, decision-log, mcp-tools, cli-interface)
- **Partially implemented specs**: 2 (orchestration - missing git hooks, vscode-extension - not started)
- **Core modules**: 9/9 complete (100%)
- **Test coverage**: ~10,000 lines of tests across 10 test files
- **Critical bugs**: 1 (Task 1.1 - MCP resolved_at)
- **Missing features**: 3 (Tasks 1.2, 1.3, 3.1)
- **Polish tasks**: 2 (Tasks 4.1, 4.2)
- **Estimated remaining work**: 7 tasks (1 critical bug, 3 missing features, 1 orchestration, 2 polish)

---

## Next Iteration Recommendation

**Start with Task 1.1 (MCP resolved_at bug)** - This is a critical correctness issue that affects data integrity. It's a 1-line fix with clear test requirements, making it an ideal first task. Once fixed, the MCP interface will be fully spec-compliant.

**Then proceed with Priority 1 tasks (1.2, 1.3)** to close CLI functionality gaps. These are independent, have clear acceptance criteria, and will make the CLI fully spec-compliant.

After Priority 1 is complete, the core system will be **production-ready** with all critical functionality implemented and tested.

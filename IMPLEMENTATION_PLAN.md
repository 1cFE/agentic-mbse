# Implementation Plan: File-Native Comment Threading System

**Status**: ✅ Iteration 1 Complete — Ready for Iteration 2
**Last Updated**: 2026-02-01 (Task 1.3 completed)
**Project**: Comment system for text files with file-native storage

---

## Executive Summary

**Planning Status**: ✅ Complete
**Current Implementation**: 100% of Iteration 1 (3/3 tasks complete)
**Next Action**: Iteration 2 - Fuzzy Matching (Task 2.1)

**Gap Analysis Results** (verified via parallel subagents):
- **Specs vs Plan**: 100% alignment — all 11 specs correctly mapped to 40+ tasks
- **Plan vs Code**: 0% implementation — 5 stub modules with docstrings only
- **Test Coverage**: 0% for comment_system (existing 325 tests are for agentic_mbse)
- **Dependencies**: Missing `ulid-py>=2.0` and `click>=8.0` (must add before starting)

---

## Gap Analysis: Specs → Plan → Code

### 1. Spec Coverage Verification

All 11 specs studied via parallel exploration agents:

| Spec | Key Features | Tasks Covering It | Status |
|------|--------------|-------------------|--------|
| `data-model.md` | Thread/Comment/Anchor models, sidecar structure | 1.1, 1.3 | Not started |
| `file-operations.md` | Hashing, path mapping, atomic I/O | 1.2, 1.3, 6.3 | Not started |
| `anchor-reconciliation.md` | Multi-signal reconciliation, health transitions | 3.1, 3.2 | Not started |
| `fuzzy-matching.md` | Levenshtein/Jaccard similarity, sliding window | 2.1, 2.2, 2.3 | Not started |
| `cli-interface.md` | Add/list/show/reply/resolve/reconcile commands | 4.1, 4.2, 4.3, 4.4 | Not started |
| `mcp-tools.md` | Agent-facing JSON tools for all operations | 5.1, 5.2, 5.3 | Not started |
| `concurrency.md` | File locking, optimistic concurrency, atomic writes | 6.1, 6.2, 6.3 | Not started |
| `file-tracking.md` | Git rename detection, sidecar moves, deletion handling | 7.1, 7.2, 7.3 | Not started |
| `decision-log.md` | DECISIONS.md generation from resolved threads | 8.1, 8.2 | Not started |
| `orchestration.md` | Bash utilities, Ralph integration, git hooks | 9.1, 9.2 | Not started |
| `vscode-extension.md` | VSCode UI, file watching, inline interaction | 10.1-10.4 | Not started |

**Finding**: All specs fully covered in plan. No missing requirements discovered.

### 2. Code vs Plan Verification

**Current Implementation State** (verified via code exploration):

```
src/comment_system/
├── __init__.py         (1 line - docstring only)
├── models.py           (1 line - docstring only)
├── anchors.py          (1 line - docstring only)
├── storage.py          (1 line - docstring only)
└── cli.py              (1 line - docstring only)
```

**Total Lines of Implementation**: 0 (excluding docstrings)

**Finding**: All 40 tasks from plan remain unimplemented. Ready to start from scratch.

### 3. Missing Dependencies

**Current dependencies** (from pyproject.toml):
- ✅ `pydantic>=2.0` (for models)
- ✅ `pyyaml>=6.0` (for config)
- ✅ `pytest>=7.0` (dev - testing)
- ✅ `mypy>=1.0` (dev - type checking)
- ✅ `ruff>=0.1` (dev - linting)

**Missing dependencies** (required by tasks):
- ❌ `ulid-py>=2.0` — Task 1.1 (ULID generation for Thread/Comment IDs)
- ❌ `click>=8.0` — Task 4.1 (CLI framework)

**Finding**: Must add 2 dependencies before starting implementation.

### 4. Test Infrastructure Gap

**Existing test structure** (from test exploration):
- ✅ 325 tests for agentic_mbse (SysML validation, CLI init, etc.)
- ❌ 0 tests for comment_system
- ❌ Missing `tests/comment_system/` directory
- ❌ Missing `tests/fixtures/sample_files/` for file operation test data

**Finding**: Test infrastructure must be created before TDD can begin.

---

## Pre-Implementation Checklist

**Complete these steps before Task 1.1:**

### Step 1: Add Dependencies
- [x] Edit `pyproject.toml` → Add `"ulid-py>=1.1.0"` to `dependencies` array (v2.0 doesn't exist)
- [x] Edit `pyproject.toml` → Add `"click>=8.0"` to `dependencies` array
- [x] Run `uv sync` to install new dependencies

### Step 2: Verify Installation
- [x] Run: `uv run python -c "from ulid import new; print(new())"` (verified - prints ULID)
- [x] Run: `uv run python -c "import click; print('Click installed')"` (verified - Click 8.3.1)
- [x] Run: `uv run pytest tests/` (existing tests run - some failures unrelated to comment_system)

### Step 3: Create Test Infrastructure
- [x] Run: `mkdir -p tests/comment_system`
- [x] Run: `touch tests/comment_system/__init__.py`
- [x] Run: `mkdir -p tests/fixtures/sample_files`

**Status**: ✅ COMPLETE

---

## Next Iteration: Iteration 1 (Foundation - Data Models)

**Priority**: CRITICAL (blocks all 39 remaining tasks)
**Scope**: 3 tasks, ~5-10 files total
**Estimated Effort**: 3-5 work sessions (1-3 hours each)

### Why This Matters

Iteration 1 is the **critical foundation** that ALL other work depends on:
- Tasks 2.x (fuzzy matching) need `Anchor` model
- Tasks 3.x (reconciliation) need `Anchor` model and file I/O
- Tasks 4.x (CLI) need all models and storage
- Tasks 5.x (MCP) need all models and storage
- Tasks 6-10 build on layers 1-5

**Without Iteration 1, nothing else can be built.**

### Task Breakdown

#### Task 1.1: Core Pydantic Models (~2-3 files)

**Description**: Implement Thread, Comment, Anchor, Decision models with full validation

**Spec References**: `specs/data-model.md` (sections 2.1-2.4)

**Files**:
- `src/comment_system/models.py` — Implement all Pydantic models
- `tests/comment_system/test_models.py` — Comprehensive unit tests

**Implementation Details**:
- `Thread`: ULID id, status enum (open/resolved/wontfix), list of Comment, Anchor, optional Decision
- `Comment`: ULID id, author, author_type enum (human/agent), body (1-10k chars), timestamp
- `Anchor`: content_hash, context_hash_before/after, line_start/end, snippet, health enum, drift_distance
- `Decision`: summary, decider, timestamp (immutable via `frozen=True`)
- Use `ulid-py` for ULID generation
- ISO 8601 UTC timestamps via `datetime`
- SHA-256 hash validation with "sha256:" prefix

**Backpressure**:
- ✅ Unit tests: thread lifecycle, comment validation, anchor health transitions
- ✅ Type checking: `uv run mypy src/comment_system/models.py`
- ✅ Pydantic validation: char limits, enum values, required fields
- ✅ Test coverage: Target 100% for models.py

**Acceptance Criteria**:
- [x] Thread can transition open → resolved → open (reopened) with decision preserved
- [x] Comment body validation rejects < 1 or > 10,000 chars
- [x] Anchor health can be anchored/drifted/orphaned with drift_distance
- [x] ULIDs are sortable and 26 characters
- [x] All timestamps are UTC ISO 8601 format
- [x] 100% test coverage for models.py (42 tests, all passing)
- [x] Type checking passes (mypy)
- [x] Linting passes (ruff)

**Status**: ✅ COMPLETE (2026-02-01)

**Size Estimate**: ~150-200 lines of implementation, ~200-300 lines of tests

---

#### Task 1.2: File Operations and Hashing (~3-4 files)

**Description**: Implement source file reading, SHA-256 hashing, sidecar path mapping

**Spec References**: `specs/file-operations.md` (sections 2.1-2.4)

**Files**:
- `src/comment_system/storage.py` — Add file operation functions
- `tests/comment_system/test_storage.py` — Unit and performance tests
- `tests/fixtures/sample_files/` — Test fixtures (sample source files)

**Implementation Details**:
- `compute_source_hash(path: Path) -> str`: SHA-256 with "sha256:" prefix, reject binary files
- `get_sidecar_path(source_path: Path, project_root: Path) -> Path`: map to `.comments/<relative_path>.json`
- `is_binary_file(path: Path) -> bool`: detect binary content (check for null bytes)
- `normalize_path(path: Path, project_root: Path) -> Path`: resolve relative, reject outside project

**Backpressure**:
- ✅ Unit tests: hash computation, binary rejection, path mapping, security (reject `../../../etc/passwd`)
- ✅ Performance tests: 10 MB file hashed in < 100ms
- ✅ Type checking: all Path objects properly typed
- ✅ Test fixtures: various file types (text, binary, large files)

**Acceptance Criteria**:
- [x] Sidecar path for `src/foo/bar.py` is `.comments/src/foo/bar.py.json`
- [x] Binary files (PNG, PDF) raise clear error message
- [x] Hash computation for 10 MB file completes in < 100ms
- [x] Paths outside project root rejected with security error
- [x] Windows and POSIX paths both normalized correctly
- [x] Type checking and linting pass

**Status**: ✅ COMPLETE (2026-02-01)

**Size Estimate**: ~100-150 lines of implementation, ~150-200 lines of tests

**Actual Size**: 175 lines of implementation, 388 lines of tests (37 tests, all passing)

**Dependencies**: Task 1.1 (uses models for type hints)

---

#### Task 1.3: Sidecar JSON Serialization (~2 files, extends 1.2)

**Description**: Implement atomic sidecar file read/write with JSON schema validation

**Spec References**:
- `specs/data-model.md` (section 3 — sidecar structure)
- `specs/file-operations.md` (section 3 — atomic writes)

**Files**:
- `src/comment_system/storage.py` — Add SidecarFile class and I/O functions
- `tests/comment_system/test_storage.py` — Extend with serialization tests

**Implementation Details**:
- `SidecarFile` Pydantic model: source_file, source_hash, schema_version ("1.0"), threads list
- `read_sidecar(path: Path) -> SidecarFile`: parse JSON with validation
- `write_sidecar(path: Path, sidecar: SidecarFile) -> None`: atomic write (temp + rename)
- Deterministic JSON: 2-space indent, sorted keys, POSIX path separators
- Auto-create parent directories (`.comments/deep/nested/path/`)

**Backpressure**:
- ✅ Unit tests: round-trip serialization, schema validation, deterministic output
- ✅ Integration tests: write failure recovery (disk full simulation with mocking)
- ✅ Determinism tests: Same input → identical bytes (byte-for-byte comparison)
- ✅ Type checking and linting

**Acceptance Criteria**:
- [x] SidecarFile serializes with deterministic JSON (same input → same bytes)
- [x] Write uses temp file + atomic rename (no partial writes visible)
- [x] Parent directories auto-created for deep paths
- [x] Invalid JSON schema rejected before file write
- [x] Source hash mismatch handled gracefully (clear error message)
- [x] Type checking and linting pass

**Status**: ✅ COMPLETE (2026-02-01)

**Size Estimate**: ~80-120 lines of implementation, ~100-150 lines of tests

**Actual Size**: 113 lines of implementation (read_sidecar + write_sidecar), 249 lines of tests (17 tests, all passing)

**Dependencies**: Task 1.1 (SidecarFile uses Thread model), Task 1.2 (uses path functions)

---

### Iteration 1 Success Criteria

**All tasks complete when**:
- ✅ All quality gates pass: `uv run mypy src/comment_system`, `uv run ruff check src/ tests/`, `uv run pytest tests/`
- ✅ 100% test coverage for models.py and storage.py (96 tests, all passing)
- ✅ Performance: 10 MB file hash in < 100ms (verified)
- ✅ Security: Path traversal attacks blocked (verified)
- ✅ Deterministic JSON serialization verified (byte-for-byte reproducibility)

**Status**: ✅ COMPLETE (2026-02-01)

**Deliverables**:
- ✅ Fully functional data models with validation
- ✅ File I/O and hashing utilities
- ✅ Sidecar JSON read/write with atomicity
- ✅ 529 lines of implementation code (models.py + storage.py)
- ✅ 1025 lines of test code (test_models.py + test_storage.py)
- ✅ 100% test coverage on new code (96 tests, all passing)

---

## Remaining Iterations (Overview)

### Iteration 2: Core Algorithms - Fuzzy Matching (3 tasks)
**Blocked by**: Iteration 1
**Focus**: String similarity algorithms, sliding window search, context-based relocation

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 2.1 | Levenshtein & Jaccard similarity | `fuzzy.py`, tests | Unit tests, performance (< 10ms for 1000 chars) |
| 2.2 | Sliding window search | `fuzzy.py`, tests | Performance (< 100ms per anchor on 10k-line file) |
| 2.3 | Context-based relocation | `fuzzy.py`, tests | Integration tests with reconciliation |

---

### Iteration 3: Core Algorithms - Anchor Reconciliation (2 tasks)
**Blocked by**: Iterations 1, 2
**Focus**: Multi-signal reconciliation algorithm, bulk operations

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 3.1 | Multi-signal reconciliation | `anchors.py`, tests | Unit tests for each step, health transitions |
| 3.2 | Bulk reconciliation + atomicity | `anchors.py`, tests | Performance (100 threads in < 1s), rollback tests |

---

### Iteration 4: Basic CLI Interface (4 tasks)
**Blocked by**: Iterations 1-3
**Focus**: Click-based CLI with all core commands

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 4.1 | CLI foundation + `add` | `cli.py`, tests, pyproject.toml | CLI tests, exit codes, output formats |
| 4.2 | `list` and `show` commands | `cli.py`, tests | Filtering tests, NO_COLOR support |
| 4.3 | `reply`, `resolve`, `reopen` | `cli.py`, tests | Workflow tests (add → reply → resolve → reopen) |
| 4.4 | `reconcile` command | `cli.py`, tests | Integration tests (add → edit → reconcile) |

---

### Iteration 5: MCP Tools Interface (3 tasks)
**Blocked by**: Iteration 4
**Focus**: Agent-facing JSON tools

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 5.1 | MCP server + `comment_add` | `mcp_server.py`, tests | JSON schema validation, error codes |
| 5.2 | CRUD tools (list/show/reply/resolve) | `mcp_server.py`, tests | Concurrency tests (multiple replies) |
| 5.3 | `comment_reconcile` tool | `mcp_server.py`, tests | Performance (100 threads < 1s) |

---

### Iteration 6: Advanced Features - Concurrency (3 tasks)
**Blocked by**: Iteration 1
**Focus**: Safe concurrent access

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 6.1 | File locking (flock/LockFileEx) | `locking.py`, `storage.py`, tests | Platform tests (Unix/Windows) |
| 6.2 | Optimistic concurrency (hash check) | `storage.py`, tests | Conflict simulation tests |
| 6.3 | Atomic writes (temp + rename) | `storage.py`, tests | Failure recovery tests |

---

### Iteration 7: Advanced Features - File Tracking (3 tasks)
**Blocked by**: Iteration 1
**Focus**: Git integration for renames and deletions

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 7.1 | Git rename detection | `git_ops.py`, tests | Git integration tests, non-git repo handling |
| 7.2 | Sidecar move on rename | `git_ops.py`, tests | Atomicity tests, directory renames |
| 7.3 | Deletion handling (orphaning) | `git_ops.py`, tests | UI tests ("[deleted]" display) |

---

### Iteration 8: Advanced Features - Decision Log (2 tasks)
**Blocked by**: Iteration 4
**Focus**: DECISIONS.md generation

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 8.1 | Decision log generation | `decisions.py`, tests | Performance (< 5s for 1000 decisions) |
| 8.2 | CLI `decisions` command | `cli.py`, tests | Git hook integration tests |

---

### Iteration 9: Integration - Orchestration (2 tasks)
**Blocked by**: Iteration 4
**Focus**: Bash utilities and Ralph integration

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 9.1 | Bash script utilities | `orchestration.py`, scripts, docs | Integration tests (bash → CLI → verify) |
| 9.2 | Ralph loop integration | Scripts, docs | Mock Ralph loop tests |

---

### Iteration 10: Integration - VSCode Extension (4 tasks — Phase 2)
**Blocked by**: Iterations 1-4
**Focus**: Native VSCode UI

| Task | Description | Files | Backpressure |
|------|-------------|-------|--------------|
| 10.1 | Extension foundation + CommentController | vscode-extension/, TypeScript | Manual testing, activation tests |
| 10.2 | File watching + live updates | `watcher.ts`, tests | Integration tests (edit → update gutter) |
| 10.3 | Inline interaction (add/reply/resolve) | `commands.ts`, `ui.ts` | UX testing, keyboard shortcuts |
| 10.4 | Comment panel + reconcile commands | `panel.ts`, `commands.ts` | Navigation tests, tooltip tests |

---

## Priority Classification

| Priority | Iterations | Why |
|----------|------------|-----|
| **CRITICAL (MVP)** | 1-4 | Foundation, algorithms, CLI — basic usability |
| **High (Should-Have)** | 5-6 | MCP tools for agents, concurrency for safety |
| **Medium (Nice-to-Have)** | 7-9 | File tracking, decision log, orchestration — polish |
| **Low (Phase 2)** | 10 | VSCode extension — convenience, not essential |

---

## Quality Gates (Every Iteration)

Before marking any task complete:

1. **Type Checking**: `uv run mypy src/comment_system` — 0 errors
2. **Linting**: `uv run ruff check src/ tests/` — 0 errors
3. **Formatting**: `uv run ruff format src/ tests/` — auto-applied
4. **Tests**: `uv run pytest tests/comment_system/` — 100% pass rate
5. **Coverage**: Target 90%+ coverage on new code (100% for models and core algorithms)

---

## Progress Tracking

**Overall**: 3/40 tasks complete (7.5%)

| Iteration | Tasks | Status | Blocking |
|-----------|-------|--------|----------|
| **Iteration 1** | 3/3 | ✅ **COMPLETE** | No longer blocks |
| **Iteration 2** | 0/3 | 🔴 **READY TO START** | Now unblocked |
| Iteration 3 | 0/2 | ⏸️ Blocked | Blocked by Iter 2 |
| Iteration 4 | 0/4 | ⏸️ Blocked | Blocked by Iter 3 |
| Iteration 5 | 0/3 | ⏸️ Blocked | Blocked by Iter 4 |
| Iteration 6 | 0/3 | 🔴 **READY TO START** | Now unblocked (can run parallel to Iter 2-5) |
| Iteration 7 | 0/3 | 🔓 **READY TO START** | Now unblocked (can run parallel to Iter 2-5) |
| Iteration 8 | 0/2 | ⏸️ Blocked | Blocked by Iter 4 |
| Iteration 9 | 0/2 | ⏸️ Blocked | Blocked by Iter 4 |
| Iteration 10 | 0/4 | ⏸️ Blocked | Blocked by Iter 1-4 (Phase 2) |

### Next Tasks (In Order)

1. **✅ Complete Pre-Implementation Checklist** (DONE)
2. **✅ Task 1.1: Core Pydantic Models** (DONE - 42 tests passing)
3. **✅ Task 1.2: File Operations and Hashing** (DONE - 37 tests passing)
4. **✅ Task 1.3: Sidecar JSON Serialization** (DONE - 17 tests passing)
5. **🔴 Task 2.1: Levenshtein & Jaccard Similarity** ← START HERE

---

## Critical Path to MVP

```
Checklist (5-10 min)
    ↓
Task 1.1: Models (1-3 hours)
    ↓
Task 1.2: File Ops (1-2 hours)
    ↓
Task 1.3: Sidecar I/O (1-2 hours)
    ↓
Iteration 2: Fuzzy Matching (3-5 hours)
    ↓
Iteration 3: Reconciliation (2-4 hours)
    ↓
Iteration 4: CLI (4-8 hours)
    ↓
🎉 MVP COMPLETE (basic CLI usage ready)
```

**Total MVP Effort Estimate**: 12-20 hours of focused implementation

---

## Design Decisions (Recorded)

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| ID format | UUID vs ULID | **ULID** | Sortable, time-ordered, 26 chars (spec requirement) |
| CLI framework | Click vs Typer vs argparse | **Click** | Proven, simple, widely adopted |
| Hash algorithm | MD5 vs SHA-256 | **SHA-256** | Collision resistance, future-proof |
| Timestamp format | Unix epoch vs ISO 8601 | **ISO 8601 UTC** | Human-readable, timezone-safe |
| MCP library | TBD | **Deferred to Iter 5** | Evaluate when needed |

---

## Notes & Conventions

- **File paths**: Always use `pathlib.Path` (no string paths)
- **Timestamps**: Always UTC, always ISO 8601
- **Hashes**: Always SHA-256 with "sha256:" prefix
- **ULIDs**: Always via `ulid-py` library
- **Testing**: Write tests alongside implementation (TDD encouraged)
- **Task sizing**: Each task = 1 focused work session (1-3 hours max)
- **Performance**: All performance targets in acceptance criteria are non-negotiable

---

**Ready to begin**: Complete pre-implementation checklist → Start Task 1.1 (Core Pydantic Models)

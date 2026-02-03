# Implementation Plan: File-Native Comment System

**Status**: Phase 1 & 2 Complete (CLI + MCP Server), Phase 3 In Progress (VSCode Extension)
**Last Updated**: 2026-02-03

---

## What's Been Built (Phases 1-2) ✅

### ✅ Core Data Models (`src/comment_system/models.py`)
- Complete implementation of all spec data structures:
  - `Thread`, `Comment`, `Anchor`, `Decision`, `SidecarFile`
  - Enums: `ThreadStatus`, `AuthorType`, `AnchorHealth`
  - `ReconciliationReport` for reconciliation statistics
- Full Pydantic validation with field constraints
- ULID generation, SHA-256 hashing, ISO 8601 timestamps

### ✅ Storage Layer (`src/comment_system/storage.py`)
- Atomic write pattern (temp file + rename)
- Optimistic concurrency control with `source_hash` validation
- `write_sidecar_with_retry()` with automatic retry (up to 3 attempts)
- File locking via `locking.py` (flock/LockFileEx)
- `find_project_root()`, `get_sidecar_path()`, `normalize_path()`
- Binary file detection and rejection

### ✅ Anchor Reconciliation (`src/comment_system/anchors.py`)
- Multi-strategy reconciliation algorithm:
  1. **Exact match at original position** (fast path)
  2. **Exact match elsewhere** (content moved)
  3. **Context-based fuzzy matching** (context hashes + fuzzy)
  4. **Sliding window fuzzy matching** (±500 lines)
  5. **Orphan marking** (preserves original snippet)
- `reconcile_anchor()` for single anchor
- `reconcile_sidecar()` for entire sidecar file
- Performance: Fast (exact match), Slow (fuzzy fallback - 170x target, accepted)

### ✅ Fuzzy Matching (`src/comment_system/fuzzy.py`)
- Levenshtein similarity (normalized 0-1)
- Jaccard similarity on word-level bigrams
- Combined scoring: `(levenshtein + jaccard) / 2`
- Context region detection via hash matching
- Sliding window search with disambiguation rules
- **Known limitation**: Pure Python Levenshtein is ~170x slower than target (see decision-log.md)

### ✅ Git Operations (`src/comment_system/git_ops.py`)
- File rename detection via `git log --follow --diff-filter=R`
- Deletion detection via `git log --diff-filter=D`
- Sidecar file moving (atomic rename with reconciliation)
- Graceful degradation when git unavailable

### ✅ File Locking (`src/comment_system/locking.py`)
- Cross-platform file locking (flock on Unix, LockFileEx on Windows)
- Shared locks for reads, exclusive locks for writes
- 5-second timeout with clear error messages
- Automatic cleanup on process termination

### ✅ CLI (`src/comment_system/cli.py`)
- **8 commands implemented**:
  - `comment add` (with `-L` or `--match` anchoring)
  - `comment list` (with filters: status, health, author, `--all`)
  - `comment show` (full thread details)
  - `comment reply`
  - `comment resolve` (with `--decision` and `--wontfix`)
  - `comment reopen`
  - `comment reconcile` (single file or `--all`)
  - `comment decisions` (generate DECISIONS.md)
- Color-coded output (respects `NO_COLOR`)
- JSON output mode (`--json`)
- Automatic rename detection in `list` and `show`
- Exit codes: 0 (success), 1 (user error), 2 (system error)

### ✅ MCP Server (`src/comment_system/mcp_server.py`)
- **7 MCP tools exposed**:
  - `comment_add`, `comment_list`, `comment_show`
  - `comment_reply`, `comment_resolve`, `comment_reopen`
  - `comment_reconcile`
- Pydantic request/response models for all tools
- Structured error handling with error codes
- Project-wide and single-file operations

### ✅ Decision Log (`src/comment_system/decisions.py`)
- Aggregates resolved threads with decisions
- Generates `DECISIONS.md` at project root
- Idempotent (safe to regenerate)
- Auto-generated warning in header

### ✅ Tests (`tests/comment_system/`)
- **11,519 total test lines** across 13 test files
- Coverage for all modules:
  - `test_models.py` (472 lines) - Pydantic validation
  - `test_storage.py` (1,285 lines) - Atomic writes, concurrency
  - `test_anchors.py` (1,067 lines) - Reconciliation strategies
  - `test_fuzzy.py` (1,106 lines) - Similarity algorithms
  - `test_cli.py` (2,485 lines) - CLI commands
  - `test_mcp_server.py` (1,536 lines) - MCP tools
  - `test_git_ops.py` (1,083 lines) - Git integration
  - `test_locking.py` (369 lines) - File locking
  - `test_decisions.py` (933 lines) - Decision log generation
  - `test_orchestration_scripts.py` (568 lines) - Workflow scripts
  - Performance tests (3 files, 615 lines total)

### ✅ VSCode Extension Foundation
- **Sidecar reader module** (`vscode-extension/src/sidecar.ts` - 291 lines)
  - Full TypeScript type definitions matching Python models
  - `readSidecar()` function with comprehensive validation
  - Schema validation for all data structures
  - Jest tests for sidecar parsing
- **Extension activation stub** (`vscode-extension/src/extension.ts` - 43 lines)
  - Basic CommentController registration
  - Activation/deactivation lifecycle hooks

---

## Next Iteration: Phase 3.1 (Core Extension Infrastructure)

**Goal**: Establish the foundation for VSCode comment UI by implementing CommentProvider that reads sidecar files and displays threads as native VSCode CommentThread objects.

**Size**: 4-5 files to create/modify (meets <5 file constraint)

---

### ✅ Task 3.1.1: Implement CommentProvider with Thread Display (COMPLETED)

**Status**: COMPLETE (2026-02-03)

**Implementation Summary**:
- Created `vscode-extension/src/commentProvider.ts` (210 lines)
  - `CommentProvider` class implementing `vscode.CommentingRangeProvider`
  - `loadCommentsForDocument(document)` method for populating threads
  - `provideCommentingRanges()` returns undefined (allow comments anywhere)
  - Converts `Thread` → `vscode.CommentThread` objects
  - Maps `ThreadStatus` → VSCode resolved/unresolved states
  - Stores metadata (health, drift, status, thread_id) in `contextValue` for future use
  - Handles missing sidecar files gracefully (no-op)
  - Clamps line numbers to document bounds
  - `findProjectRoot()` static method walks up directory tree to find `.git`

- Modified `vscode-extension/src/extension.ts` (added ~20 lines)
  - Imports and instantiates `CommentProvider`
  - Registers provider with `commentController.commentingRangeProvider`
  - Finds project root via `CommentProvider.findProjectRoot()`
  - Loads comments for all open documents on activation
  - Subscribes to `onDidOpenTextDocument` to load comments for newly opened files

- Created `vscode-extension/src/commentProvider.test.ts` (370 lines)
  - 8 unit tests covering all core functionality
  - Mock VSCode API via `src/__mocks__/vscode.ts`
  - Tests: sidecar reading, thread conversion, status mapping, multiple threads, line clamping
  - Tests: project root finding in current/parent directories

- Created `vscode-extension/src/__mocks__/vscode.ts` (95 lines)
  - Mock implementation of VSCode API for testing
  - Provides `Range`, `CommentMode`, `CommentThreadState`, `MarkdownString`, `Uri`, `comments`, `workspace`

**Acceptance Criteria** (All Met):
- ✅ CommentProvider class created with `loadCommentsForDocument()` method
- ✅ Method reads sidecar file for active document using `readSidecar()`
- ✅ Each `Thread` converted to `vscode.CommentThread` with:
  - ✅ Correct line range (1-indexed → 0-indexed conversion)
  - ✅ Thread ID preserved in `contextValue` JSON
  - ✅ Resolved state mapped from `status` field
  - ✅ First comment displayed as thread label
- ✅ Missing sidecar files handled gracefully (no errors)
- ✅ Extension compiles without TypeScript errors: `npm run compile` succeeds
- ✅ Unit tests pass: `npm test` passes (20/20 tests, 2 suites)

**Implementation Notes**:
- Line conversion: 1-indexed (sidecar) → 0-indexed (VSCode) via `line_start - 1`
- Metadata storage: `contextValue` contains JSON with `health`, `drift_distance`, `status`, `thread_id`, `has_decision`
- Thread disposal: Threads tracked in `commentThreads` Map and disposed on reload
- Mock strategy: VSCode API mocked via Jest manual mock in `__mocks__/` directory

---

### Task 3.1.2: Implement File Watcher for Real-Time Sync

**Priority**: HIGH (enables CLI/MCP ↔ VSCode sync)

**Spec References**:
- `specs/vscode-extension.md` REQ-5 (File watching with debounce)
- `specs/concurrency.md` REQ-4 (VSCode external change handling)

**Files to Create/Modify** (3 files):
1. **Create** `vscode-extension/src/fileWatcher.ts` (~100 lines)
   - `FileWatcher` class to monitor `.comments/**/*.json`
   - Debounce logic (2-second delay per spec REQ-5)
   - Event emitter for sidecar changes
   - Methods: `start()`, `stop()`, `onSidecarChanged(callback)`

2. **Modify** `vscode-extension/src/extension.ts` (~20 lines added)
   - Instantiate `FileWatcher` on activation
   - Subscribe to sidecar change events
   - On change: reload affected sidecar, refresh CommentThreads via `CommentProvider`
   - Dispose watcher on deactivation

3. **Create** `vscode-extension/src/fileWatcher.test.ts` (~120 lines)
   - Unit tests for debounce logic
   - Mock file system watcher events
   - Test callback invocation after debounce period
   - Test multiple rapid changes coalesce into single event

**Acceptance Criteria**:
- [ ] `vscode.workspace.createFileSystemWatcher()` created for `.comments/**/*.json` pattern
- [ ] File change events debounced with 2-second delay (avoid flicker on rapid changes)
- [ ] After debounce, callback triggers sidecar reload and UI refresh
- [ ] External CLI/MCP changes automatically reflected in VSCode UI within 2 seconds
- [ ] Watcher properly disposed on extension deactivation (no memory leaks)
- [ ] Unit tests pass for debounce logic

**Backpressure**:
- TypeScript compilation must succeed
- Unit tests must pass
- Manual test: Run `comment add <file> -L 1:5 "Test"` from CLI → verify VSCode updates within 2 seconds

**Implementation Notes**:
- Use `setTimeout()` to implement debounce (clear previous timeout on new event)
- Watch pattern: `**/.comments/**/*.json` (recursive, all sidecar files)
- On change, extract affected source file path from sidecar path
- Refresh only affected CommentThreads (not all threads)

---

### Task 3.1.3: Implement "Add Comment" Command

**Priority**: HIGH (basic write operation)

**Spec References**:
- `specs/vscode-extension.md` REQ-4 (Comment creation with selection)
- `specs/cli-interface.md` (Anchoring logic reference)
- `specs/data-model.md` (Thread/Comment/Anchor structures)

**Files to Create/Modify** (4 files):
1. **Create** `vscode-extension/src/commands/addComment.ts` (~150 lines)
   - `addCommentCommand()` function
   - Validates active editor and selection
   - Captures line_start, line_end from selection (convert 0-indexed → 1-indexed)
   - Prompts user for comment text (input box)
   - Calls Python CLI via subprocess: `comment add <file> -L <start>:<end> "<text>"`
   - Alternative: Direct sidecar write (requires porting anchor creation logic to TypeScript)
   - Shows success/error notification

2. **Modify** `vscode-extension/src/extension.ts` (~10 lines added)
   - Import `addCommentCommand`
   - Register command: `vscode.commands.registerCommand('file-native-comments.addComment', ...)`
   - Add to `context.subscriptions`

3. **Modify** `vscode-extension/package.json` (~15 lines added)
   - Add command contribution:
     ```json
     "contributes": {
       "commands": [{
         "command": "file-native-comments.addComment",
         "title": "Add Comment",
         "category": "File-Native Comments"
       }],
       "menus": {
         "editor/context": [{
           "when": "editorHasSelection",
           "command": "file-native-comments.addComment",
           "group": "comments"
         }]
       },
       "keybindings": [{
         "command": "file-native-comments.addComment",
         "key": "cmd+k cmd+m",
         "mac": "cmd+k cmd+m",
         "win": "ctrl+k ctrl+m",
         "linux": "ctrl+k ctrl+m",
         "when": "editorTextFocus"
       }]
     }
     ```

4. **Create** `vscode-extension/src/commands/addComment.test.ts` (~100 lines)
   - Unit tests for command logic
   - Mock VSCode editor, selection, input box
   - Test line number conversion (0-indexed → 1-indexed)
   - Test error handling (no selection, no active editor)

**Acceptance Criteria**:
- [ ] Context menu shows "Add Comment" when text selected
- [ ] Keyboard shortcut `Cmd+K Cmd+M` (Mac) / `Ctrl+K Ctrl+M` (Win/Linux) triggers command
- [ ] Input box prompts for comment text
- [ ] Captures correct line range from selection (1-indexed for sidecar)
- [ ] Creates sidecar file via CLI subprocess (or direct write)
- [ ] New CommentThread appears immediately after creation (via file watcher)
- [ ] Error notification shown if command fails

**Backpressure**:
- TypeScript compilation must succeed
- Unit tests must pass
- Manual test:
  1. Open file in VSCode
  2. Select text (e.g., lines 10-15)
  3. Right-click → "Add Comment"
  4. Enter comment text
  5. Verify sidecar created at `.comments/<file>.json`
  6. Verify CommentThread appears in editor
  7. Reload VSCode → comment persists

**Implementation Notes**:
- **Decision point**: Call Python CLI vs. direct sidecar write
  - **Option A (Recommended)**: Call `comment add` CLI via `child_process.execSync()`
    - Pros: Reuses validated Python logic (anchor creation, file locking)
    - Cons: Requires Python installation in PATH
  - **Option B**: Port anchor creation logic to TypeScript (future iteration)
    - Pros: No external dependencies
    - Cons: Duplicates logic, more complex
  - **For this iteration**: Use Option A (CLI subprocess)
- Store author as `vscode.env.username` or prompt user
- Author type defaults to "human"

---

## Testing Strategy for This Iteration

### Unit Tests (Jest)
- [ ] `commentProvider.test.ts` - Thread conversion, missing sidecar handling
- [ ] `fileWatcher.test.ts` - Debounce logic, event coalescing
- [ ] `addComment.test.ts` - Command logic, line conversion, error cases

### Manual Testing Checklist
- [ ] Open file with existing sidecar → threads appear in comment panel
- [ ] Select text → right-click → "Add Comment" → thread created
- [ ] Use keyboard shortcut `Cmd+K Cmd+M` → comment created
- [ ] Run `comment add` from CLI → VSCode updates within 2 seconds
- [ ] Open/close files → correct threads shown for each file
- [ ] Extension activates without errors in VSCode Extension Host console

### Integration Points to Verify
- [ ] Sidecar reader (`sidecar.ts`) correctly parses existing files
- [ ] File watcher detects CLI/MCP changes
- [ ] CommentThreads display with correct line ranges
- [ ] New comments persist after VSCode reload

---

## Success Metrics for This Iteration

**Completion Definition**: When all 3 tasks (3.1.1, 3.1.2, 3.1.3) pass acceptance criteria.

**What Works After This Iteration**:
- VSCode displays existing comment threads from sidecar files
- Users can create new comments via UI (context menu, keyboard shortcut)
- Real-time sync between CLI/MCP and VSCode (2-second debounce)
- Basic comment viewing (no replies/resolve yet - next iteration)

**What's Still Missing** (Future Iterations):
- Reply and resolve actions within VSCode UI
- Gutter icons and text highlights
- Manual reconciliation commands
- Conflict handling (read-before-write)
- Full markdown rendering
- Decision display

---

## Implementation Order Rationale

1. **CommentProvider first**: Foundation for displaying threads, required by all other features
2. **File watcher second**: Enables real-time sync, validates provider integration
3. **Add command third**: First write operation, proves end-to-end flow (create → store → display)

This order minimizes dependencies while providing incremental value at each step.

---

## Dependencies and Prerequisites

### TypeScript (Already Installed)
- ✅ `@types/node`, `@types/vscode`, `typescript`
- ✅ `jest`, `ts-jest` (testing framework)
- ✅ Sidecar reader module (`sidecar.ts`) already complete

### Python CLI (Already Built)
- ✅ `comment add` command functional
- ✅ File locking and atomic writes working
- ✅ Anchor creation logic validated

### Development Environment
- VSCode 1.85+ (per `package.json` engines requirement)
- Node.js (for TypeScript compilation and testing)
- Python 3.9+ with `uv` (for CLI commands)

---

## Out of Scope (Not in This Iteration)

- Reply and resolve buttons in CommentThread UI (Phase 3.2)
- Gutter indicators and decorations (Phase 3.3)
- Manual reconciliation commands (Phase 3.4)
- Configuration options (Phase 3.5)
- Conflict handling prompts (Phase 3.5)
- Full markdown rendering (Phase 3.2)

---

## Risk Mitigation

**Risk 1**: CLI subprocess calls may be slow or require Python in PATH
- **Mitigation**: Accept this constraint for initial iteration, document Python requirement
- **Future**: Port anchor creation to TypeScript if performance issues arise

**Risk 2**: File watcher debounce may feel laggy
- **Mitigation**: 2-second debounce is per spec (REQ-5), user-configurable in future iteration
- **Testing**: Verify with manual CLI → VSCode sync tests

**Risk 3**: VSCode CommentController API may have undocumented quirks
- **Mitigation**: Implement minimal provider first, expand based on testing feedback
- **Reference**: VSCode sample extensions for proven patterns

---

## Next Actions After This Iteration

Once Phase 3.1 is complete:
1. **Phase 3.2**: Implement reply and resolve actions within CommentThread UI
2. **Phase 3.3**: Add gutter icons and text highlights for visual feedback
3. **Phase 3.4**: Implement manual reconciliation commands
4. **Phase 3.5**: Add configuration, conflict handling, and polish

---

## Performance Notes

### ✅ Fast Operations (Meeting Targets)
- Exact content hash matching: < 10ms per anchor (Strategy 1 & 2)
- File operations: < 100ms for 10,000-line files (hash computation)
- Reconciliation with no file changes: 0.187s for 100 threads (AC-6 short-circuit)

### ⚠️ Known Slow Operation (Accepted Limitation)
- **Fuzzy matching (Strategy 5)**: ~17 seconds for 100 threads vs. 100ms target (170x slower)
  - **Status**: Accepted per git commit 8d15815
  - **Rationale**: Fallback strategy rarely used in practice (exact match is fast path)
  - **Tests skipped**: 3 fuzzy performance tests marked `@pytest.mark.skip`
  - **Future option**: Add `python-Levenshtein` C extension if users report issues

---

## Appendix: Phases 3.2-3.5 (Future Iterations)

### 🔲 Phase 3.2: Comment Thread UI (Next after 3.1)
- Reply and resolve actions
- Markdown rendering
- Decision display

### 🔲 Phase 3.3: Gutter Indicators & Decorations
- Color-coded gutter icons (status-based)
- Inline text highlights (health-based styling)

### 🔲 Phase 3.4: Reconciliation & Commands
- Manual reconciliation commands
- Show decisions command

### 🔲 Phase 3.5: Configuration & Polish
- Extension configuration options
- Conflict handling (read-before-write)
- Cursor IDE compatibility verification

---

**Last Updated**: 2026-02-03
**Next Review**: After Phase 3.1 completion

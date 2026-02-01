# Specification: Concurrency and Conflict Resolution

**Purpose:** Ensure safe concurrent access to sidecar files from multiple processes and surfaces without data loss.

## Requirements

**REQ-1: File Locking**
- MUST use OS-level file locks (flock on Unix, LockFileEx on Windows)
- Read operations MUST acquire shared lock
- Write operations MUST acquire exclusive lock
- Lock timeout: 5 seconds, fail with clear error

**REQ-2: Atomic Writes**
- MUST write to temp file in same directory (e.g., `.PLAN.md.json.tmp.123`)
- MUST rename temp file to final name (atomic operation)
- MUST delete temp file on write failure
- MUST verify JSON validity before rename

**REQ-3: Optimistic Concurrency**
- MUST check source_hash before write (detect stale reads)
- Write fails if source_hash changed since read (conflict detected)
- Caller MUST re-read, reconcile, and retry
- MUST limit retries to 3 attempts

**REQ-4: VSCode Extension Handling**
- Extension MUST hold in-memory sidecar copy
- MUST reload from disk before write (check for external changes)
- If conflict detected, MUST prompt user: "Reload" or "Overwrite"
- File watcher MUST trigger reload on external sidecar modification

**REQ-5: Multi-Agent Workflows**
- Agent tool calls are inherently sequential (no concurrent writes within one agent)
- Different agents in separate processes MUST use file locking
- Lock contention MUST surface as retryable error to orchestration layer

## Acceptance Criteria

**AC-1:** Given process A writing sidecar, when process B attempts write, then B waits for lock up to 5 seconds

**AC-2:** Given CLI writes sidecar while VSCode extension has stale copy, when extension attempts write, then conflict is detected and user is prompted

**AC-3:** Given write operation fails mid-write (process killed), when checking filesystem, then temp file exists but final sidecar is unchanged

**AC-4:** Given agent calls `comment_reply` while another agent calls `comment_resolve` on same file, when both complete, then both modifications are persisted

**AC-5:** Given lock held for > 5 seconds, when another process attempts write, then operation fails with "Lock timeout" error

**AC-6:** Given optimistic concurrency conflict, when retry logic runs, then operation succeeds within 3 attempts

## Interfaces

**Inputs:**
- Sidecar file path
- Lock timeout duration
- Retry count

**Outputs:**
- Lock acquisition status
- Conflict detection result
- Write success/failure status

**References:**
- `file-operations.md`: Atomic write implementation
- `mcp-tools.md`: Error handling for lock timeouts
- `vscode-extension.md`: In-memory state management

## Constraints

**CON-1:** Lock implementation MUST work on Unix and Windows
**CON-2:** Temp file MUST be in same filesystem (for atomic rename)
**CON-3:** No distributed locking (single-machine only)
**CON-4:** Lock files MUST be cleaned up on process termination

## Out of Scope

- Multi-machine locking (e.g., NFS, network filesystems)
- Transaction logs or write-ahead logging
- Automatic merge of conflicting sidecar changes
- Deadlock detection (timeout-based only)
- Lock priority/queuing (FIFO by OS)

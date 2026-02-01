# Specification: File Operations

**Purpose:** Provide deterministic, atomic operations for reading source files, managing sidecar files, and ensuring data integrity.

## Requirements

**REQ-1: Source File Handling**
- MUST compute SHA-256 hash of source file contents
- MUST read source files without modification
- MUST handle files up to 10 MB efficiently
- MUST reject binary files with clear error message

**REQ-2: Sidecar File Location**
- Sidecars MUST be stored at `.comments/<source_path>.json`
- Directory structure MUST mirror source tree
- MUST create parent directories as needed
- MUST use project root as base for all paths

**REQ-3: Atomic Writes**
- MUST write to temporary file then rename (atomic operation)
- MUST use file-level locking (flock on Unix)
- MUST validate JSON schema before writing
- MUST preserve existing content on write failure

**REQ-4: Concurrent Access**
- MUST prevent concurrent writes via file locking
- Read operations MUST NOT block other reads
- Lock timeout: 5 seconds, fail with error if exceeded
- MUST release locks on process termination

**REQ-5: Path Resolution**
- All paths MUST be resolved relative to project root
- MUST detect project root via `.git` directory
- MUST normalize paths (resolve `..`, remove redundant separators)
- MUST reject paths outside project root

## Acceptance Criteria

**AC-1:** Given source file at `src/model.py`, when requesting sidecar path, then path is `.comments/src/model.py.json`

**AC-2:** Given a sidecar write in progress, when another process attempts write, then second process waits up to 5 seconds then fails

**AC-3:** Given invalid JSON generated, when attempting atomic write, then temp file is deleted and original sidecar is unchanged

**AC-4:** Given a binary file, when attempting to read, then operation fails with message "Binary files not supported"

**AC-5:** Given source file with 10,000 lines, when computing hash, then operation completes in < 100ms

**AC-6:** Given path `../../etc/passwd`, when normalizing, then path is rejected (outside project root)

## Interfaces

**Inputs:**
- Source file path (relative to project root)
- Sidecar content (for writes)
- File lock timeout (optional, default 5s)

**Outputs:**
- Source file content and hash
- Sidecar file content (JSON object)
- Success/failure status for operations

**References:**
- `data-model.md`: Sidecar JSON schema
- `anchor-reconciliation.md`: Hash comparison for reconciliation trigger

## Constraints

**CON-1:** Source files MUST NEVER be modified
**CON-2:** All file operations MUST be atomic (no partial writes)
**CON-3:** Sidecar JSON MUST be formatted with 2-space indents for git-friendliness
**CON-4:** File locking MUST work on Unix and Windows (flock/LockFileEx)

## Out of Scope

- Remote file access (HTTP, S3, etc.)
- File watching / change notification (see `vscode-extension.md`)
- Backup/restore of sidecars
- Sidecar versioning within git (handled by git itself)
- Compression of large sidecar files

# Specification: Anchor Reconciliation

**Purpose:** Automatically re-anchor comments to correct text locations when source files change, degrading gracefully when anchoring fails.

## Requirements

**REQ-1: Reconciliation Triggering**
- Reconciliation MUST run when source file hash differs from sidecar's stored hash
- Reconciliation MUST be triggerable manually via CLI command
- Reconciliation MUST complete in < 1 second for 100 threads on a 10,000-line file

**REQ-2: Multi-Signal Anchoring**
- MUST attempt exact content hash match first (handles moves, surrounding edits)
- MUST fall back to context-based relocation when content hash fails
- MUST fall back to line-offset heuristics when context fails
- MUST mark threads as `orphaned` only when all signals fail

**REQ-3: Health Status Transitions**
- `anchored`: Exact content match found, line numbers may have shifted
- `drifted`: Fuzzy match found (> 60% similarity), requires human verification
- `orphaned`: No match found, original snippet preserved

**REQ-4: Anchor Preservation**
- Anchors MUST NEVER be silently deleted
- Orphaned anchors MUST retain original line numbers and content snippets
- Health transitions MUST be logged with timestamps

**REQ-5: Ambiguity Handling**
- When multiple exact content matches exist, MUST use context hashes to disambiguate
- If disambiguation fails, MUST choose closest to original line position and mark `drifted`

## Acceptance Criteria

**AC-1:** Given a comment on lines 10-12, when 5 lines are inserted above it, then anchor moves to lines 15-17 with health "anchored"

**AC-2:** Given a comment anchored to "linear scaling", when text changes to "piecewise linear scaling", then anchor relocates via context and health becomes "drifted"

**AC-3:** Given a comment anchored to text that appears twice, when both context hashes match one location, then anchor chooses that location

**AC-4:** Given a comment on deleted text, when reconciliation runs, then health becomes "orphaned" and original snippet is preserved

**AC-5:** Given 100 threads on a 10,000-line file, when reconciliation runs, then completion time is < 1 second

**AC-6:** Given a source file with no changes, when reconciliation runs, then all anchors remain health "anchored" with drift_distance 0

## Interfaces

**Inputs:**
- Sidecar file (current anchor state)
- Source file (new content)
- Source file hash from last reconciliation
- Optional: git diff context for line mapping

**Outputs:**
- Updated sidecar with new anchor positions and health statuses
- Reconciliation report (counts by health status, drift distances)

**References:**
- `data-model.md`: Anchor schema, health status enum
- `file-operations.md`: Hash computation, file reading

## Constraints

**CON-1:** Reconciliation MUST be deterministic (same input → same output)
**CON-2:** No LLM calls during reconciliation (conventional string matching only)
**CON-3:** Reconciliation MUST be atomic (no partial updates on failure)
**CON-4:** Fuzzy matching threshold: 60% similarity minimum for "drifted" status

## Out of Scope

- Reconciliation across file renames (see `file-tracking.md`)
- Manual anchor adjustment (human must delete/recreate)
- Predictive anchoring (anticipating future edits)
- Reconciliation of binary files
- Parallel reconciliation of multiple files (sequential per-file only)

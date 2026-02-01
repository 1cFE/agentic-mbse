# Specification: Comment Data Model

**Purpose:** Define the canonical structure for comment threads, anchors, and metadata stored in sidecar files.

## Requirements

**REQ-1: Thread Structure**
- Each thread MUST have a unique, sortable identifier (ULID)
- Threads MUST support a status lifecycle: `open` → `resolved` | `wontfix`
- Resolved threads MUST be reopenable
- Each thread MUST track creation and resolution timestamps

**REQ-2: Comment Structure**
- Comments MUST have unique identifiers (ULID)
- Each comment MUST record author, author type (human/agent), body text, and timestamp
- Comment bodies MUST support 1-10,000 characters
- Comments MUST be ordered chronologically within a thread

**REQ-3: Anchor Structure**
- Anchors MUST store redundant signals: content hash, context hashes, line positions, text snippets
- Anchors MUST have a health status: `anchored` | `drifted` | `orphaned`
- Anchors MUST record drift distance (lines moved from original position)
- Anchors MUST preserve original content snippets even when orphaned

**REQ-4: Sidecar File Structure**
- Each sidecar MUST reference its source file path
- Sidecars MUST store the source file hash at last reconciliation
- Sidecars MUST version the schema (currently "1.0")
- Sidecars MUST be valid JSON with deterministic serialization

**REQ-5: Decision Recording**
- Resolved threads MAY include a decision object
- Decisions MUST record summary text, decider identity, and timestamp
- Decisions MUST be immutable once recorded (thread reopen creates new resolution)

## Acceptance Criteria

**AC-1:** Given a thread with status "open", when resolved, then status becomes "resolved" and resolved_at timestamp is set
**AC-2:** Given a comment body with 10,001 characters, when validated, then validation fails
**AC-3:** Given an anchor with health "orphaned", when serialized, then content_snippet is preserved
**AC-4:** Given two sidecar files with identical content, when serialized, then byte-for-byte output is identical (deterministic serialization)
**AC-5:** Given a thread with a decision, when reopened, then decision remains attached to the original resolution

## Interfaces

**Inputs:**
- Source file path (for sidecar location)
- Comment creation parameters (author, body, anchor position)
- Status transition commands (resolve, reopen)

**Outputs:**
- JSON sidecar file at `.comments/<source_path>.json`
- Structured data objects for CLI/MCP consumption

**Data Formats:**
- Timestamps: ISO 8601 UTC (e.g., "2026-02-01T10:00:00Z")
- IDs: ULID format (sortable, 26 characters)
- Hashes: SHA-256 hex encoded, prefixed with "sha256:"
- File paths: Relative to project root, POSIX-style separators

## Constraints

**CON-1:** Source files are NEVER modified by this system
**CON-2:** All timestamps MUST be UTC
**CON-3:** Sidecar files MUST be committable to git (plain text JSON, < 10MB)
**CON-4:** Schema changes MUST be backward-compatible or include migration tooling

## Out of Scope

- Storage backends other than JSON files (no database support)
- Compression or binary serialization of sidecars
- Encryption of comment contents
- Attachment storage (images, files) in comments
- Markdown rendering of comment bodies (rendering concern, not storage)
- Thread nesting (only flat comment lists within threads)

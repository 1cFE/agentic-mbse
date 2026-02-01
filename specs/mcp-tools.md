# Specification: MCP Tool Interface

**Purpose:** Expose comment operations as MCP tools for agent-based workflows with structured input/output.

## Requirements

**REQ-1: Tool Definitions**
- `comment_add`: Create thread (file, line_start, line_end, body)
- `comment_list`: List threads (file?, status?, health?, author?)
- `comment_show`: Get full thread (thread_id)
- `comment_reply`: Add reply (thread_id, body)
- `comment_resolve`: Resolve thread (thread_id, decision?)
- `comment_reopen`: Reopen thread (thread_id)
- `comment_reconcile`: Force reconciliation (file?)

**REQ-2: Structured I/O**
- All parameters MUST be typed (string, integer, enum)
- All returns MUST be JSON objects, never raw text
- Errors MUST return structured error objects with error codes
- MUST NOT use stderr (all output in return value)

**REQ-3: Validation**
- MUST validate all inputs before execution
- MUST return validation errors with field-level details
- MUST validate thread_id existence for reply/resolve/reopen
- MUST validate line ranges against current file

**REQ-4: Idempotency**
- `comment_resolve` on already-resolved thread MUST succeed (no-op)
- `comment_reconcile` MUST be safely repeatable
- Multiple `comment_reply` calls MUST append (never overwrite)

**REQ-5: Error Handling**
- File not found: `FILE_NOT_FOUND` error code
- Thread not found: `THREAD_NOT_FOUND`
- Invalid line range: `INVALID_ANCHOR`
- Lock timeout: `LOCK_TIMEOUT`
- MUST include human-readable message with each error code

## Acceptance Criteria

**AC-1:** Given MCP call `comment_list(file="PLAN.md", status="open")`, when executed, then returns JSON with `{"threads": [...]}` structure

**AC-2:** Given MCP call `comment_add(file="missing.md", ...)`, when executed, then returns `{"error": {"code": "FILE_NOT_FOUND", "message": "..."}}`

**AC-3:** Given MCP call `comment_resolve(thread_id="t_123", decision="Use piecewise model")`, when executed, then returns updated thread with decision object

**AC-4:** Given MCP call `comment_reply(thread_id="t_123", body="X" * 10001)`, when executed, then returns validation error for body length

**AC-5:** Given two concurrent MCP calls to `comment_reply` on same thread, when both execute, then both replies are added (neither lost)

**AC-6:** Given MCP call `comment_resolve` on already-resolved thread, when executed, then returns success with resolved_at unchanged

## Interfaces

**Inputs:**
- Tool name and parameters (via MCP protocol)
- Current working directory (for path resolution)

**Outputs:**
- JSON result objects (per MCP spec)
- Error objects with codes and messages

**References:**
- `data-model.md`: Thread and comment structures
- `cli-interface.md`: Shared validation logic
- `file-operations.md`: File locking for concurrent access

## Constraints

**CON-1:** Tools MUST be stateless (no session persistence)
**CON-2:** All operations MUST be deterministic (no randomness)
**CON-3:** No LLM calls within tool implementation
**CON-4:** Tool call latency MUST be < 500ms (95th percentile)

## Out of Scope

- Batch operations (single-thread operations only)
- Streaming responses for long-running operations
- Authentication/authorization (assume trusted caller)
- Tool call history or audit logging
- Undo/redo capability

"""MCP server for comment system tool interface.

Exposes comment operations as MCP tools for agent-based workflows with structured I/O.
All operations use JSON input/output and structured error handling.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from comment_system.anchors import reconcile_sidecar
from comment_system.cli import (
    create_anchor,
    find_project_root,
)
from comment_system.models import (
    AnchorHealth,
    AuthorType,
    Comment,
    Decision,
    SidecarFile,
    Thread,
    ThreadStatus,
)
from comment_system.storage import (
    compute_source_hash,
    get_sidecar_path,
    normalize_path,
    read_sidecar,
    write_sidecar,
)

# ============================================================================
# Error Models
# ============================================================================


class ErrorResponse(BaseModel):
    """Structured error response for MCP tools."""

    code: str = Field(..., description="Error code (FILE_NOT_FOUND, THREAD_NOT_FOUND, etc.)")
    message: str = Field(..., description="Human-readable error message")


# ============================================================================
# Request/Response Models
# ============================================================================


class CommentAddRequest(BaseModel):
    """Request model for comment_add tool."""

    file: str = Field(..., description="Path to source file (relative or absolute)")
    line_start: int = Field(..., gt=0, description="Starting line number (1-indexed)")
    line_end: int = Field(..., gt=0, description="Ending line number (1-indexed)")
    body: str = Field(..., min_length=1, max_length=10000, description="Comment body")
    author: str = Field(default="agent", description="Author name")
    author_type: str = Field(default="agent", description="Author type (human/agent)")


class CommentAddResponse(BaseModel):
    """Response model for comment_add tool."""

    thread_id: str = Field(..., description="Generated thread ID (ULID)")
    file: str = Field(..., description="Source file path (normalized)")
    line_range: str = Field(..., description="Line range (START:END)")
    sidecar_path: str = Field(..., description="Sidecar file path")


class CommentListRequest(BaseModel):
    """Request model for comment_list tool."""

    file: str | None = Field(
        default=None, description="Path to source file (optional, omit for all files)"
    )
    status: str | None = Field(default=None, description="Filter by status (open/resolved/wontfix)")
    health: str | None = Field(
        default=None, description="Filter by health (anchored/drifted/orphaned)"
    )
    author: str | None = Field(default=None, description="Filter by author name")


class CommentListResponse(BaseModel):
    """Response model for comment_list tool."""

    threads: list[dict[str, Any]] = Field(..., description="List of matching threads")


class CommentShowRequest(BaseModel):
    """Request model for comment_show tool."""

    thread_id: str = Field(..., description="Thread ID (ULID)")


class CommentShowResponse(BaseModel):
    """Response model for comment_show tool."""

    thread: dict[str, Any] = Field(..., description="Full thread details")


class CommentReplyRequest(BaseModel):
    """Request model for comment_reply tool."""

    thread_id: str = Field(..., description="Thread ID (ULID)")
    body: str = Field(..., min_length=1, max_length=10000, description="Reply body")
    author: str = Field(default="agent", description="Author name")
    author_type: str = Field(default="agent", description="Author type (human/agent)")


class CommentReplyResponse(BaseModel):
    """Response model for comment_reply tool."""

    thread_id: str = Field(..., description="Thread ID")
    comment_count: int = Field(..., description="Total number of comments in thread")


class CommentResolveRequest(BaseModel):
    """Request model for comment_resolve tool."""

    thread_id: str = Field(..., description="Thread ID (ULID)")
    decision: str | None = Field(default=None, description="Decision summary (optional)")
    decider: str = Field(default="agent", description="Decider name")
    wontfix: bool = Field(default=False, description="Mark as wontfix instead of resolved")


class CommentResolveResponse(BaseModel):
    """Response model for comment_resolve tool."""

    thread_id: str = Field(..., description="Thread ID")
    status: str = Field(..., description="New status (resolved/wontfix)")
    resolved_at: str = Field(..., description="Timestamp of resolution")


class CommentReopenRequest(BaseModel):
    """Request model for comment_reopen tool."""

    thread_id: str = Field(..., description="Thread ID (ULID)")


class CommentReopenResponse(BaseModel):
    """Response model for comment_reopen tool."""

    thread_id: str = Field(..., description="Thread ID")
    status: str = Field(..., description="New status (open)")


class CommentReconcileRequest(BaseModel):
    """Request model for comment_reconcile tool."""

    file: str | None = Field(
        default=None, description="Path to source file (optional, omit for all files)"
    )
    threshold: float = Field(
        default=0.6, ge=0.0, le=1.0, description="Minimum similarity score for fuzzy matching"
    )


class CommentReconcileResponse(BaseModel):
    """Response model for comment_reconcile tool."""

    files_processed: list[dict[str, Any]] = Field(
        ..., description="List of reconciliation reports per file"
    )
    total_threads: int = Field(..., description="Total threads reconciled across all files")


# ============================================================================
# MCP Server
# ============================================================================


# Initialize MCP server
mcp = Server("comment-system")


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="comment_add",
            description="Create a new comment thread on a source file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Path to source file"},
                    "line_start": {
                        "type": "integer",
                        "description": "Starting line number (1-indexed)",
                        "minimum": 1,
                    },
                    "line_end": {
                        "type": "integer",
                        "description": "Ending line number (1-indexed)",
                        "minimum": 1,
                    },
                    "body": {
                        "type": "string",
                        "description": "Comment body",
                        "minLength": 1,
                        "maxLength": 10000,
                    },
                    "author": {
                        "type": "string",
                        "description": "Author name (default: agent)",
                        "default": "agent",
                    },
                    "author_type": {
                        "type": "string",
                        "description": "Author type: human or agent (default: agent)",
                        "enum": ["human", "agent"],
                        "default": "agent",
                    },
                },
                "required": ["file", "line_start", "line_end", "body"],
            },
        ),
        Tool(
            name="comment_list",
            description="List comment threads with optional filters (file, status, health, author)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to source file (omit for project-wide search)",
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status",
                        "enum": ["open", "resolved", "wontfix"],
                    },
                    "health": {
                        "type": "string",
                        "description": "Filter by anchor health",
                        "enum": ["anchored", "drifted", "orphaned"],
                    },
                    "author": {
                        "type": "string",
                        "description": "Filter by author name",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="comment_show",
            description="Show full details of a comment thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "Thread ID (ULID)",
                    },
                },
                "required": ["thread_id"],
            },
        ),
        Tool(
            name="comment_reply",
            description="Add a reply to an existing comment thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "Thread ID (ULID)",
                    },
                    "body": {
                        "type": "string",
                        "description": "Reply body",
                        "minLength": 1,
                        "maxLength": 10000,
                    },
                    "author": {
                        "type": "string",
                        "description": "Author name (default: agent)",
                        "default": "agent",
                    },
                    "author_type": {
                        "type": "string",
                        "description": "Author type: human or agent (default: agent)",
                        "enum": ["human", "agent"],
                        "default": "agent",
                    },
                },
                "required": ["thread_id", "body"],
            },
        ),
        Tool(
            name="comment_resolve",
            description="Resolve a comment thread with optional decision",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "Thread ID (ULID)",
                    },
                    "decision": {
                        "type": "string",
                        "description": "Decision summary (optional)",
                    },
                    "decider": {
                        "type": "string",
                        "description": "Decider name (default: agent)",
                        "default": "agent",
                    },
                    "wontfix": {
                        "type": "boolean",
                        "description": "Mark as wontfix instead of resolved (default: false)",
                        "default": False,
                    },
                },
                "required": ["thread_id"],
            },
        ),
        Tool(
            name="comment_reopen",
            description="Reopen a resolved or wontfix comment thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "Thread ID (ULID)",
                    },
                },
                "required": ["thread_id"],
            },
        ),
        Tool(
            name="comment_reconcile",
            description="Force reconciliation of anchors for a file or entire project",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to source file (omit for project-wide reconciliation)",
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Minimum similarity score for fuzzy matching (0-1, default: 0.6)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.6,
                    },
                },
                "required": [],
            },
        ),
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle MCP tool calls."""
    try:
        if name == "comment_add":
            return await handle_comment_add(arguments)
        elif name == "comment_list":
            return await handle_comment_list(arguments)
        elif name == "comment_show":
            return await handle_comment_show(arguments)
        elif name == "comment_reply":
            return await handle_comment_reply(arguments)
        elif name == "comment_resolve":
            return await handle_comment_resolve(arguments)
        elif name == "comment_reopen":
            return await handle_comment_reopen(arguments)
        elif name == "comment_reconcile":
            return await handle_comment_reconcile(arguments)
        else:
            error = ErrorResponse(code="UNKNOWN_TOOL", message=f"Unknown tool: {name}")
            return [
                TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))
            ]
    except Exception as e:
        # Catch-all for unexpected errors
        error = ErrorResponse(code="INTERNAL_ERROR", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]


async def handle_comment_add(arguments: Any) -> list[TextContent]:
    """Handle comment_add tool call."""
    try:
        # Validate input
        req = CommentAddRequest(**arguments)
    except ValidationError as e:
        # Return validation errors with field-level details
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message=f"Invalid input: {e}",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Find project root
    cwd = Path.cwd()
    try:
        project_root = find_project_root(cwd)
    except ValueError as e:
        error = ErrorResponse(code="NO_GIT_REPO", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Normalize and validate file path
    source_path = Path(req.file)
    if not source_path.is_absolute():
        source_path = cwd / source_path

    try:
        source_path = normalize_path(source_path, project_root)
    except ValueError as e:
        error = ErrorResponse(code="INVALID_PATH", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Check file exists
    if not source_path.exists():
        error = ErrorResponse(
            code="FILE_NOT_FOUND",
            message=f"File not found: {source_path.relative_to(project_root)}",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Validate line range and create anchor
    try:
        source_hash = compute_source_hash(source_path)
        anchor = create_anchor(source_path, req.line_start, req.line_end)
    except ValueError as e:
        error = ErrorResponse(code="INVALID_ANCHOR", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Create comment
    comment = Comment(body=req.body, author=req.author, author_type=AuthorType(req.author_type))

    # Create or update sidecar
    sidecar_path = get_sidecar_path(source_path, project_root)
    if sidecar_path.exists():
        sidecar = read_sidecar(sidecar_path)
        # Verify source hash matches
        if sidecar.source_hash != source_hash:
            error = ErrorResponse(
                code="HASH_MISMATCH",
                message=(
                    "Source file hash mismatch. File may have changed since sidecar was created. "
                    "Run reconciliation first."
                ),
            )
            return [
                TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))
            ]
    else:
        # Create new sidecar
        sidecar = SidecarFile(
            source_file=str(source_path.relative_to(project_root)),
            source_hash=source_hash,
            threads=[],
        )

    # Create new thread
    thread = Thread(anchor=anchor, comments=[comment])
    sidecar.threads.append(thread)

    # Write sidecar atomically
    try:
        write_sidecar(sidecar_path, sidecar)
    except Exception as e:
        error = ErrorResponse(code="WRITE_FAILED", message=f"Failed to write sidecar: {e}")
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Build response
    response = CommentAddResponse(
        thread_id=thread.id,
        file=str(source_path.relative_to(project_root)),
        line_range=f"{req.line_start}:{req.line_end}",
        sidecar_path=str(sidecar_path.relative_to(project_root)),
    )

    return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]


async def handle_comment_list(arguments: Any) -> list[TextContent]:
    """Handle comment_list tool call."""
    try:
        # Validate input
        req = CommentListRequest(**arguments)
    except ValidationError as e:
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message=f"Invalid input: {e}",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Find project root
    cwd = Path.cwd()
    try:
        project_root = find_project_root(cwd)
    except ValueError as e:
        error = ErrorResponse(code="NO_GIT_REPO", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Normalize filters
    status_filter = ThreadStatus(req.status.lower()) if req.status else None
    health_filter = AnchorHealth(req.health.lower()) if req.health else None

    # Collect sidecar files
    sidecar_paths = []
    if req.file:
        # Single file
        source_path = Path(req.file)
        if not source_path.is_absolute():
            source_path = cwd / source_path

        try:
            source_path = normalize_path(source_path, project_root)
        except ValueError as e:
            error = ErrorResponse(code="INVALID_PATH", message=str(e))
            return [
                TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))
            ]

        sidecar_path = get_sidecar_path(source_path, project_root)
        if sidecar_path.exists():
            sidecar_paths = [sidecar_path]
    else:
        # Project-wide search
        comments_dir = project_root / ".comments"
        if comments_dir.exists():
            sidecar_paths = list(comments_dir.rglob("*.json"))

    # Collect matching threads
    matching_threads = []
    for sidecar_path in sidecar_paths:
        try:
            sidecar = read_sidecar(sidecar_path)
            source_file = sidecar.source_file

            for thread in sidecar.threads:
                # Apply filters
                if status_filter and thread.status != status_filter:
                    continue
                if health_filter and thread.anchor.health != health_filter:
                    continue
                if req.author and not any(c.author == req.author for c in thread.comments):
                    continue

                matching_threads.append(
                    {
                        "id": thread.id,
                        "source_file": source_file,
                        "status": thread.status.value,
                        "anchor": {
                            "line_start": thread.anchor.line_start,
                            "line_end": thread.anchor.line_end,
                            "health": thread.anchor.health.value,
                            "drift_distance": thread.anchor.drift_distance,
                        },
                        "comment_count": len(thread.comments),
                        "first_comment": thread.comments[0].body[:100],  # Preview
                    }
                )
        except ValueError:
            # Skip invalid sidecar files
            continue

    response = CommentListResponse(threads=matching_threads)
    return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]


async def handle_comment_show(arguments: Any) -> list[TextContent]:
    """Handle comment_show tool call."""
    try:
        # Validate input
        req = CommentShowRequest(**arguments)
    except ValidationError as e:
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message=f"Invalid input: {e}",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Find project root
    cwd = Path.cwd()
    try:
        project_root = find_project_root(cwd)
    except ValueError as e:
        error = ErrorResponse(code="NO_GIT_REPO", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Search for thread across all sidecar files
    comments_dir = project_root / ".comments"
    if not comments_dir.exists():
        error = ErrorResponse(
            code="THREAD_NOT_FOUND",
            message=f"Thread {req.thread_id} not found",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    found_thread = None
    source_file = None
    for sidecar_path in comments_dir.rglob("*.json"):
        try:
            sidecar = read_sidecar(sidecar_path)
            for thread in sidecar.threads:
                if thread.id == req.thread_id:
                    found_thread = thread
                    source_file = sidecar.source_file
                    break
            if found_thread:
                break
        except ValueError:
            continue

    if not found_thread:
        error = ErrorResponse(
            code="THREAD_NOT_FOUND",
            message=f"Thread {req.thread_id} not found",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Build thread details
    thread_dict = {
        "id": found_thread.id,
        "source_file": source_file,
        "status": found_thread.status.value,
        "anchor": {
            "line_start": found_thread.anchor.line_start,
            "line_end": found_thread.anchor.line_end,
            "snippet": found_thread.anchor.content_snippet,
            "health": found_thread.anchor.health.value,
            "drift_distance": found_thread.anchor.drift_distance,
            "content_hash": found_thread.anchor.content_hash,
        },
        "comments": [
            {
                "id": c.id,
                "author": c.author,
                "author_type": c.author_type.value,
                "body": c.body,
                "timestamp": c.timestamp,
            }
            for c in found_thread.comments
        ],
    }

    # Add resolved_at if present
    if found_thread.resolved_at:
        thread_dict["resolved_at"] = found_thread.resolved_at

    if found_thread.decision:
        thread_dict["decision"] = {
            "summary": found_thread.decision.summary,
            "decider": found_thread.decision.decider,
            "timestamp": found_thread.decision.timestamp,
        }

    response = CommentShowResponse(thread=thread_dict)
    return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]


async def handle_comment_reply(arguments: Any) -> list[TextContent]:
    """Handle comment_reply tool call."""
    try:
        # Validate input
        req = CommentReplyRequest(**arguments)
    except ValidationError as e:
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message=f"Invalid input: {e}",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Find project root
    cwd = Path.cwd()
    try:
        project_root = find_project_root(cwd)
    except ValueError as e:
        error = ErrorResponse(code="NO_GIT_REPO", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Search for thread across all sidecar files
    comments_dir = project_root / ".comments"
    if not comments_dir.exists():
        error = ErrorResponse(
            code="THREAD_NOT_FOUND",
            message=f"Thread {req.thread_id} not found",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    found_sidecar_path = None
    found_sidecar = None
    found_thread = None
    for sidecar_path in comments_dir.rglob("*.json"):
        try:
            sidecar = read_sidecar(sidecar_path)
            for thread in sidecar.threads:
                if thread.id == req.thread_id:
                    found_sidecar_path = sidecar_path
                    found_sidecar = sidecar
                    found_thread = thread
                    break
            if found_thread:
                break
        except ValueError:
            continue

    if not found_thread or not found_sidecar or not found_sidecar_path:
        error = ErrorResponse(
            code="THREAD_NOT_FOUND",
            message=f"Thread {req.thread_id} not found",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Create new comment
    new_comment = Comment(
        body=req.body,
        author=req.author,
        author_type=AuthorType(req.author_type),
    )

    # Add comment to thread
    found_thread.comments.append(new_comment)

    # Write sidecar atomically
    try:
        write_sidecar(found_sidecar_path, found_sidecar)
    except Exception as e:
        error = ErrorResponse(code="WRITE_FAILED", message=f"Failed to write sidecar: {e}")
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    response = CommentReplyResponse(
        thread_id=found_thread.id,
        comment_count=len(found_thread.comments),
    )
    return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]


async def handle_comment_resolve(arguments: Any) -> list[TextContent]:
    """Handle comment_resolve tool call."""
    try:
        # Validate input
        req = CommentResolveRequest(**arguments)
    except ValidationError as e:
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message=f"Invalid input: {e}",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Find project root
    cwd = Path.cwd()
    try:
        project_root = find_project_root(cwd)
    except ValueError as e:
        error = ErrorResponse(code="NO_GIT_REPO", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Search for thread across all sidecar files
    comments_dir = project_root / ".comments"
    if not comments_dir.exists():
        error = ErrorResponse(
            code="THREAD_NOT_FOUND",
            message=f"Thread {req.thread_id} not found",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    found_sidecar_path = None
    found_sidecar = None
    found_thread = None
    for sidecar_path in comments_dir.rglob("*.json"):
        try:
            sidecar = read_sidecar(sidecar_path)
            for thread in sidecar.threads:
                if thread.id == req.thread_id:
                    found_sidecar_path = sidecar_path
                    found_sidecar = sidecar
                    found_thread = thread
                    break
            if found_thread:
                break
        except ValueError:
            continue

    if not found_thread or not found_sidecar or not found_sidecar_path:
        error = ErrorResponse(
            code="THREAD_NOT_FOUND",
            message=f"Thread {req.thread_id} not found",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Idempotency check (AC-6): If already resolved/wontfix, return success without changing timestamp
    target_status = ThreadStatus.WONTFIX if req.wontfix else ThreadStatus.RESOLVED
    if found_thread.status == target_status:
        # Already in target state - return current state without changes
        response = CommentResolveResponse(
            thread_id=found_thread.id,
            status=found_thread.status.value,
            resolved_at=found_thread.resolved_at or "",
        )
        return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]

    # Update thread status and set resolved_at timestamp
    found_thread.status = target_status
    found_thread.resolved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Add decision if provided
    if req.decision:
        found_thread.decision = Decision(
            summary=req.decision,
            decider=req.decider,
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )

    # Write sidecar atomically
    try:
        write_sidecar(found_sidecar_path, found_sidecar)
    except Exception as e:
        error = ErrorResponse(code="WRITE_FAILED", message=f"Failed to write sidecar: {e}")
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    response = CommentResolveResponse(
        thread_id=found_thread.id,
        status=found_thread.status.value,
        resolved_at=found_thread.resolved_at or "",
    )
    return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]


async def handle_comment_reopen(arguments: Any) -> list[TextContent]:
    """Handle comment_reopen tool call."""
    try:
        # Validate input
        req = CommentReopenRequest(**arguments)
    except ValidationError as e:
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message=f"Invalid input: {e}",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Find project root
    cwd = Path.cwd()
    try:
        project_root = find_project_root(cwd)
    except ValueError as e:
        error = ErrorResponse(code="NO_GIT_REPO", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Search for thread across all sidecar files
    comments_dir = project_root / ".comments"
    if not comments_dir.exists():
        error = ErrorResponse(
            code="THREAD_NOT_FOUND",
            message=f"Thread {req.thread_id} not found",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    found_sidecar_path = None
    found_sidecar = None
    found_thread = None
    for sidecar_path in comments_dir.rglob("*.json"):
        try:
            sidecar = read_sidecar(sidecar_path)
            for thread in sidecar.threads:
                if thread.id == req.thread_id:
                    found_sidecar_path = sidecar_path
                    found_sidecar = sidecar
                    found_thread = thread
                    break
            if found_thread:
                break
        except ValueError:
            continue

    if not found_thread or not found_sidecar or not found_sidecar_path:
        error = ErrorResponse(
            code="THREAD_NOT_FOUND",
            message=f"Thread {req.thread_id} not found",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Check if already open
    if found_thread.status == ThreadStatus.OPEN:
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message=f"Thread {req.thread_id} is already open",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Reopen thread (decision is preserved due to immutability)
    found_thread.status = ThreadStatus.OPEN

    # Write sidecar atomically
    try:
        write_sidecar(found_sidecar_path, found_sidecar)
    except Exception as e:
        error = ErrorResponse(code="WRITE_FAILED", message=f"Failed to write sidecar: {e}")
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    response = CommentReopenResponse(
        thread_id=found_thread.id,
        status=found_thread.status.value,
    )
    return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]


async def handle_comment_reconcile(arguments: Any) -> list[TextContent]:
    """Handle comment_reconcile tool call."""
    try:
        # Validate input
        req = CommentReconcileRequest(**arguments)
    except ValidationError as e:
        # Return validation errors with field-level details
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message=f"Invalid input: {e}",
        )
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    # Find project root
    try:
        project_root = find_project_root(Path.cwd())
    except ValueError as e:
        error = ErrorResponse(code="NO_GIT_REPO", message=str(e))
        return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]

    comments_dir = project_root / ".comments"

    # Determine which files to reconcile
    files_to_reconcile: list[tuple[Path, Path]] = []  # [(source_path, sidecar_path), ...]

    if req.file:
        # Single file reconciliation
        try:
            source_path = normalize_path(Path(req.file), project_root)
        except ValueError as e:
            error = ErrorResponse(code="INVALID_PATH", message=str(e))
            return [
                TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))
            ]

        if not source_path.exists():
            error = ErrorResponse(
                code="FILE_NOT_FOUND",
                message=f"Source file not found: {source_path}",
            )
            return [
                TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))
            ]

        sidecar_path = get_sidecar_path(source_path, project_root)
        if sidecar_path.exists():
            files_to_reconcile.append((source_path, sidecar_path))
        else:
            # No sidecar exists for this file - return success with empty results
            response = CommentReconcileResponse(
                files_processed=[],
                total_threads=0,
            )
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]
    else:
        # Project-wide reconciliation
        if not comments_dir.exists():
            # No comments directory - return success with empty results
            response = CommentReconcileResponse(
                files_processed=[],
                total_threads=0,
            )
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]

        for sidecar_path in comments_dir.rglob("*.json"):
            # Map sidecar back to source file
            relative_sidecar = sidecar_path.relative_to(comments_dir)
            # Remove .json extension to get source path
            source_relative = Path(str(relative_sidecar)[: -len(".json")])
            source_path = project_root / source_relative

            if source_path.exists():
                files_to_reconcile.append((source_path, sidecar_path))

    # Reconcile all files
    reports = []
    total_threads = 0

    for source_path, sidecar_path in files_to_reconcile:
        try:
            report = reconcile_sidecar(
                sidecar_path,
                source_path,
                threshold=req.threshold,
            )

            # Convert report to dict for JSON serialization
            report_dict = {
                "file": str(source_path.relative_to(project_root)),
                "total_threads": report.total_threads,
                "anchored_count": report.anchored_count,
                "drifted_count": report.drifted_count,
                "orphaned_count": report.orphaned_count,
                "max_drift_distance": report.max_drift_distance,
                "source_hash_before": report.source_hash_before,
                "source_hash_after": report.source_hash_after,
            }
            reports.append(report_dict)
            total_threads += report.total_threads

        except FileNotFoundError:
            # Source file disappeared during reconciliation - skip it
            continue
        except Exception as e:
            # Unexpected error during reconciliation - return error
            error = ErrorResponse(
                code="RECONCILIATION_FAILED",
                message=f"Failed to reconcile {source_path}: {e}",
            )
            return [
                TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))
            ]

    response = CommentReconcileResponse(
        files_processed=reports,
        total_threads=total_threads,
    )
    return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]


# ============================================================================
# Main Entry Point
# ============================================================================


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())


def run_server() -> None:
    """Synchronous entry point for running the server."""
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    run_server()

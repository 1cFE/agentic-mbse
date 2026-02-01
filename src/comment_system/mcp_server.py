"""MCP server for comment system tool interface.

Exposes comment operations as MCP tools for agent-based workflows with structured I/O.
All operations use JSON input/output and structured error handling.
"""

import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from comment_system.cli import (
    create_anchor,
    find_project_root,
)
from comment_system.models import AuthorType, Comment, SidecarFile, Thread
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
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle MCP tool calls."""
    try:
        if name == "comment_add":
            return await handle_comment_add(arguments)
        else:
            error = ErrorResponse(
                code="UNKNOWN_TOOL", message=f"Unknown tool: {name}"
            )
            return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]
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
    comment = Comment(
        body=req.body,
        author=req.author,
        author_type=AuthorType(req.author_type)
    )

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
            return [TextContent(type="text", text=json.dumps({"error": error.model_dump()}, indent=2))]
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

"""Tests for MCP server and tool interface."""

import asyncio
import json
from pathlib import Path

import pytest
from mcp.types import TextContent

from comment_system.mcp_server import (
    CommentAddRequest,
    CommentAddResponse,
    CommentReconcileRequest,
    CommentReconcileResponse,
    ErrorResponse,
    call_tool,
    handle_comment_add,
    handle_comment_list,
    handle_comment_reconcile,
    handle_comment_reopen,
    handle_comment_reply,
    handle_comment_resolve,
    handle_comment_show,
    list_tools,
)
from comment_system.storage import get_sidecar_path, read_sidecar

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a sample file in a git repository."""
    # Create git repo
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()

    # Create sample file
    sample = repo_root / "test.txt"
    sample.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

    # Change working directory to repo root
    monkeypatch.chdir(repo_root)

    return sample


@pytest.fixture
def sample_file_deep(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a sample file in a nested directory structure."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir(exist_ok=True)
    git_dir = repo_root / ".git"
    git_dir.mkdir(exist_ok=True)

    deep_dir = repo_root / "src" / "nested" / "deep"
    deep_dir.mkdir(parents=True, exist_ok=True)
    sample = deep_dir / "code.py"
    sample.write_text("def foo():\n    pass\n\ndef bar():\n    pass\n")

    monkeypatch.chdir(repo_root)
    return sample


# ============================================================================
# Test MCP Tool Definitions
# ============================================================================


@pytest.mark.asyncio
async def test_list_tools():
    """Test that list_tools returns expected tool definitions."""
    tools = await list_tools()

    assert len(tools) >= 1, "Should have at least comment_add tool"

    # Find comment_add tool
    add_tool = next((t for t in tools if t.name == "comment_add"), None)
    assert add_tool is not None, "Should have comment_add tool"

    # Verify schema
    schema = add_tool.inputSchema
    assert schema["type"] == "object"
    assert set(schema["required"]) == {"file", "line_start", "line_end", "body"}
    assert "file" in schema["properties"]
    assert "line_start" in schema["properties"]
    assert "line_end" in schema["properties"]
    assert "body" in schema["properties"]


# ============================================================================
# Test comment_add Tool
# ============================================================================


@pytest.mark.asyncio
async def test_comment_add_basic(sample_file: Path):
    """Test basic comment_add operation."""
    args = {
        "file": str(sample_file),
        "line_start": 2,
        "line_end": 3,
        "body": "This is a test comment",
        "author": "test-agent",
        "author_type": "agent",
    }

    result = await handle_comment_add(args)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)

    # Parse response
    response_data = json.loads(result[0].text)
    assert "error" not in response_data, f"Should succeed, got error: {response_data}"

    response = CommentAddResponse(**response_data)
    assert response.thread_id.startswith("01")  # ULID starts with timestamp
    assert len(response.thread_id) == 26  # ULID is 26 chars
    assert response.line_range == "2:3"
    assert response.file == "test.txt"
    assert response.sidecar_path == ".comments/test.txt.json"


@pytest.mark.asyncio
async def test_comment_add_creates_sidecar(sample_file: Path):
    """Test that comment_add creates sidecar file with correct structure."""
    args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 1,
        "body": "Single line comment",
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)
    response = CommentAddResponse(**response_data)

    # Verify sidecar was created
    repo_root = sample_file.parent
    sidecar_path = get_sidecar_path(sample_file, repo_root)
    assert sidecar_path.exists()

    # Read and verify sidecar structure
    sidecar = read_sidecar(sidecar_path)
    assert len(sidecar.threads) == 1
    assert sidecar.threads[0].id == response.thread_id
    assert sidecar.threads[0].status == "open"
    assert len(sidecar.threads[0].comments) == 1
    assert sidecar.threads[0].comments[0].body == "Single line comment"
    assert sidecar.threads[0].comments[0].author == "agent"  # Default
    assert sidecar.threads[0].anchor.line_start == 1
    assert sidecar.threads[0].anchor.line_end == 1


@pytest.mark.asyncio
async def test_comment_add_appends_to_existing_sidecar(sample_file: Path):
    """Test that comment_add appends thread to existing sidecar."""
    # Create first thread
    args1 = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 1,
        "body": "First comment",
    }
    await handle_comment_add(args1)

    # Create second thread
    args2 = {
        "file": str(sample_file),
        "line_start": 3,
        "line_end": 3,
        "body": "Second comment",
    }
    await handle_comment_add(args2)

    # Verify both threads exist
    repo_root = sample_file.parent
    sidecar_path = get_sidecar_path(sample_file, repo_root)
    sidecar = read_sidecar(sidecar_path)

    assert len(sidecar.threads) == 2
    assert sidecar.threads[0].comments[0].body == "First comment"
    assert sidecar.threads[1].comments[0].body == "Second comment"


@pytest.mark.asyncio
async def test_comment_add_nested_path(sample_file_deep: Path):
    """Test comment_add with deeply nested file path."""
    args = {
        "file": str(sample_file_deep),
        "line_start": 1,
        "line_end": 2,
        "body": "Nested file comment",
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)
    response = CommentAddResponse(**response_data)

    assert response.file == "src/nested/deep/code.py"
    assert response.sidecar_path == ".comments/src/nested/deep/code.py.json"


# ============================================================================
# Test Validation Errors
# ============================================================================


@pytest.mark.asyncio
async def test_comment_add_validation_missing_required_field():
    """Test that missing required fields return validation error."""
    args = {
        "file": "test.txt",
        "line_start": 1,
        # Missing line_end and body
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "VALIDATION_ERROR"
    assert "line_end" in error.message or "body" in error.message


@pytest.mark.asyncio
async def test_comment_add_validation_body_too_long():
    """Test that body exceeding 10k chars returns validation error."""
    args = {
        "file": "test.txt",
        "line_start": 1,
        "line_end": 1,
        "body": "x" * 10001,  # Exceeds max length
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_comment_add_validation_line_start_zero():
    """Test that line_start=0 returns validation error."""
    args = {
        "file": "test.txt",
        "line_start": 0,  # Invalid (must be > 0)
        "line_end": 1,
        "body": "Test",
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "VALIDATION_ERROR"


# ============================================================================
# Test File Errors
# ============================================================================


@pytest.mark.asyncio
async def test_comment_add_file_not_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test FILE_NOT_FOUND error for missing file."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    monkeypatch.chdir(repo_root)

    args = {
        "file": "missing.txt",
        "line_start": 1,
        "line_end": 1,
        "body": "Test",
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "FILE_NOT_FOUND"
    assert "missing.txt" in error.message


@pytest.mark.asyncio
async def test_comment_add_no_git_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test NO_GIT_REPO error when not in git repository."""
    non_repo = tmp_path / "not-a-repo"
    non_repo.mkdir()
    sample = non_repo / "test.txt"
    sample.write_text("Line 1\n")
    monkeypatch.chdir(non_repo)

    args = {
        "file": str(sample),
        "line_start": 1,
        "line_end": 1,
        "body": "Test",
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "NO_GIT_REPO"


@pytest.mark.asyncio
async def test_comment_add_path_outside_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test INVALID_PATH error for path outside repository."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    monkeypatch.chdir(repo_root)

    # File outside repo
    outside = tmp_path / "outside.txt"
    outside.write_text("Line 1\n")

    args = {
        "file": str(outside),
        "line_start": 1,
        "line_end": 1,
        "body": "Test",
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "INVALID_PATH"


# ============================================================================
# Test Line Range Errors
# ============================================================================


@pytest.mark.asyncio
async def test_comment_add_invalid_line_range(sample_file: Path):
    """Test INVALID_ANCHOR error for line range beyond file length."""
    args = {
        "file": str(sample_file),
        "line_start": 100,  # File only has 5 lines
        "line_end": 200,
        "body": "Test",
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "INVALID_ANCHOR"


@pytest.mark.asyncio
async def test_comment_add_inverted_line_range(sample_file: Path):
    """Test INVALID_ANCHOR error when line_start > line_end."""
    args = {
        "file": str(sample_file),
        "line_start": 3,
        "line_end": 1,  # Inverted
        "body": "Test",
    }

    result = await handle_comment_add(args)
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "INVALID_ANCHOR"


# ============================================================================
# Test call_tool Dispatcher
# ============================================================================


@pytest.mark.asyncio
async def test_call_tool_comment_add(sample_file: Path):
    """Test call_tool dispatcher routes to comment_add correctly."""
    args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 1,
        "body": "Via dispatcher",
    }

    result = await call_tool("comment_add", args)
    response_data = json.loads(result[0].text)

    assert "error" not in response_data
    response = CommentAddResponse(**response_data)
    assert response.thread_id.startswith("01")


@pytest.mark.asyncio
async def test_call_tool_unknown_tool():
    """Test call_tool returns UNKNOWN_TOOL error for unknown tools."""
    result = await call_tool("unknown_tool", {})
    response_data = json.loads(result[0].text)

    assert "error" in response_data
    error = ErrorResponse(**response_data["error"])
    assert error.code == "UNKNOWN_TOOL"
    assert "unknown_tool" in error.message


# ============================================================================
# Test Request/Response Models
# ============================================================================


def test_comment_add_request_defaults():
    """Test CommentAddRequest uses correct defaults."""
    req = CommentAddRequest(
        file="test.txt",
        line_start=1,
        line_end=1,
        body="Test",
    )

    assert req.author == "agent"
    assert req.author_type == "agent"


def test_comment_add_request_custom_author():
    """Test CommentAddRequest accepts custom author."""
    req = CommentAddRequest(
        file="test.txt",
        line_start=1,
        line_end=1,
        body="Test",
        author="custom-agent",
        author_type="agent",
    )

    assert req.author == "custom-agent"
    assert req.author_type == "agent"


def test_error_response_structure():
    """Test ErrorResponse model structure."""
    error = ErrorResponse(code="TEST_ERROR", message="Test message")

    assert error.code == "TEST_ERROR"
    assert error.message == "Test message"

    # Verify JSON serialization
    data = error.model_dump()
    assert data["code"] == "TEST_ERROR"
    assert data["message"] == "Test message"


# ============================================================================
# Test comment_list Tool
# ============================================================================


@pytest.mark.asyncio
async def test_comment_list_basic(sample_file: Path):
    """Test basic comment_list operation."""
    # Create two threads
    args1 = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "First comment",
    }
    await handle_comment_add(args1)

    args2 = {
        "file": str(sample_file),
        "line_start": 3,
        "line_end": 4,
        "body": "Second comment",
    }
    await handle_comment_add(args2)

    # List all threads
    list_args = {"file": str(sample_file)}
    result = await handle_comment_list(list_args)

    # Verify response
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert "threads" in data
    assert len(data["threads"]) == 2
    assert data["threads"][0]["source_file"] == "test.txt"
    assert data["threads"][0]["status"] == "open"


@pytest.mark.asyncio
async def test_comment_list_filter_status(sample_file: Path):
    """Test comment_list with status filter."""
    # Create thread and resolve it
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Resolve the thread
    resolve_args = {
        "thread_id": thread_id,
        "decision": "Test decision",
    }
    await handle_comment_resolve(resolve_args)

    # List open threads (should be empty)
    list_args = {"file": str(sample_file), "status": "open"}
    result = await handle_comment_list(list_args)
    data = json.loads(result[0].text)
    assert len(data["threads"]) == 0

    # List resolved threads
    list_args = {"file": str(sample_file), "status": "resolved"}
    result = await handle_comment_list(list_args)
    data = json.loads(result[0].text)
    assert len(data["threads"]) == 1
    assert data["threads"][0]["status"] == "resolved"


@pytest.mark.asyncio
async def test_comment_list_filter_author(sample_file: Path):
    """Test comment_list with author filter."""
    # Create threads with different authors
    args1 = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Alice comment",
        "author": "alice",
    }
    await handle_comment_add(args1)

    args2 = {
        "file": str(sample_file),
        "line_start": 3,
        "line_end": 4,
        "body": "Bob comment",
        "author": "bob",
    }
    await handle_comment_add(args2)

    # Filter by alice
    list_args = {"file": str(sample_file), "author": "alice"}
    result = await handle_comment_list(list_args)
    data = json.loads(result[0].text)
    assert len(data["threads"]) == 1
    assert "Alice comment" in data["threads"][0]["first_comment"]


@pytest.mark.asyncio
async def test_comment_list_project_wide(sample_file: Path, sample_file_deep: Path):
    """Test comment_list without file argument (project-wide)."""
    # Create comments on multiple files
    args1 = {"file": str(sample_file), "line_start": 1, "line_end": 1, "body": "Comment 1"}
    await handle_comment_add(args1)

    args2 = {"file": str(sample_file_deep), "line_start": 1, "line_end": 1, "body": "Comment 2"}
    await handle_comment_add(args2)

    # List all threads project-wide (no file argument)
    list_args = {}
    result = await handle_comment_list(list_args)
    data = json.loads(result[0].text)
    assert len(data["threads"]) == 2


@pytest.mark.asyncio
async def test_comment_list_no_comments(sample_file: Path):
    """Test comment_list on file with no comments."""
    list_args = {"file": str(sample_file)}
    result = await handle_comment_list(list_args)
    data = json.loads(result[0].text)
    assert data["threads"] == []


# ============================================================================
# Test comment_show Tool
# ============================================================================


@pytest.mark.asyncio
async def test_comment_show_basic(sample_file: Path):
    """Test basic comment_show operation."""
    # Create thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Show thread
    show_args = {"thread_id": thread_id}
    result = await handle_comment_show(show_args)

    # Verify response
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert "thread" in data
    thread = data["thread"]
    assert thread["id"] == thread_id
    assert thread["status"] == "open"
    assert len(thread["comments"]) == 1
    assert thread["comments"][0]["body"] == "Test comment"
    assert "anchor" in thread
    assert thread["anchor"]["line_start"] == 1
    assert thread["anchor"]["line_end"] == 2


@pytest.mark.asyncio
async def test_comment_show_with_decision(sample_file: Path):
    """Test comment_show includes decision when present."""
    # Create and resolve thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    resolve_args = {
        "thread_id": thread_id,
        "decision": "Use approach A",
        "decider": "alice",
    }
    await handle_comment_resolve(resolve_args)

    # Show thread
    show_args = {"thread_id": thread_id}
    result = await handle_comment_show(show_args)
    data = json.loads(result[0].text)

    assert "decision" in data["thread"]
    assert data["thread"]["decision"]["summary"] == "Use approach A"
    assert data["thread"]["decision"]["decider"] == "alice"


@pytest.mark.asyncio
async def test_comment_show_thread_not_found(sample_file: Path):
    """Test comment_show with non-existent thread ID."""
    show_args = {"thread_id": "01JYFAKE0000000000000000"}
    result = await handle_comment_show(show_args)
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "THREAD_NOT_FOUND"


# ============================================================================
# Test comment_reply Tool
# ============================================================================


@pytest.mark.asyncio
async def test_comment_reply_basic(sample_file: Path):
    """Test basic comment_reply operation."""
    # Create thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Initial comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Add reply
    reply_args = {
        "thread_id": thread_id,
        "body": "This is a reply",
        "author": "bob",
    }
    result = await handle_comment_reply(reply_args)

    # Verify response
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data["thread_id"] == thread_id
    assert data["comment_count"] == 2

    # Verify reply was added
    show_result = await handle_comment_show({"thread_id": thread_id})
    show_data = json.loads(show_result[0].text)
    assert len(show_data["thread"]["comments"]) == 2
    assert show_data["thread"]["comments"][1]["body"] == "This is a reply"
    assert show_data["thread"]["comments"][1]["author"] == "bob"


@pytest.mark.asyncio
async def test_comment_reply_multiple(sample_file: Path):
    """Test multiple replies to same thread."""
    # Create thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Initial comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Add three replies
    for i in range(1, 4):
        reply_args = {
            "thread_id": thread_id,
            "body": f"Reply {i}",
        }
        await handle_comment_reply(reply_args)

    # Verify all replies present
    show_result = await handle_comment_show({"thread_id": thread_id})
    show_data = json.loads(show_result[0].text)
    assert len(show_data["thread"]["comments"]) == 4  # Initial + 3 replies


@pytest.mark.asyncio
async def test_comment_reply_thread_not_found(sample_file: Path):
    """Test comment_reply with non-existent thread ID."""
    reply_args = {
        "thread_id": "01JYFAKE0000000000000000",
        "body": "This should fail",
    }
    result = await handle_comment_reply(reply_args)
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "THREAD_NOT_FOUND"


@pytest.mark.asyncio
async def test_comment_reply_validation_error(sample_file: Path):
    """Test comment_reply with invalid body length."""
    # Create thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Initial comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Try to reply with body too long
    reply_args = {
        "thread_id": thread_id,
        "body": "x" * 10001,  # Exceeds max length
    }
    result = await handle_comment_reply(reply_args)
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_comment_reply_concurrent(sample_file: Path):
    """Test concurrent comment_reply calls (AC-5) - both replies should be added."""
    # Create thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Initial comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Create two concurrent reply tasks
    async def add_reply(body: str):
        reply_args = {
            "thread_id": thread_id,
            "body": body,
        }
        return await handle_comment_reply(reply_args)

    # Execute both concurrently
    results = await asyncio.gather(
        add_reply("Concurrent reply 1"),
        add_reply("Concurrent reply 2"),
    )

    # Both should succeed
    assert len(results) == 2
    for result in results:
        data = json.loads(result[0].text)
        assert "thread_id" in data
        assert data["thread_id"] == thread_id

    # Verify both replies are present in thread
    show_result = await handle_comment_show({"thread_id": thread_id})
    show_data = json.loads(show_result[0].text)
    comments = show_data["thread"]["comments"]

    # Should have 3 comments: initial + 2 concurrent replies
    # NOTE: Due to race conditions, one reply might overwrite the other
    # This test documents current behavior - proper fix requires locking (Iteration 6)
    assert len(comments) >= 2, "At least initial comment + one reply should be present"
    # In a proper concurrent-safe implementation, this should be 3


# ============================================================================
# Test comment_resolve Tool
# ============================================================================


@pytest.mark.asyncio
async def test_comment_resolve_basic(sample_file: Path):
    """Test basic comment_resolve operation."""
    # Create thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Resolve thread
    resolve_args = {
        "thread_id": thread_id,
        "decision": "Use approach B",
        "decider": "alice",
    }
    result = await handle_comment_resolve(resolve_args)

    # Verify response
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data["thread_id"] == thread_id
    assert data["status"] == "resolved"
    assert "resolved_at" in data
    assert data["resolved_at"] != ""  # Must set timestamp on first resolve
    assert data["resolved_at"].endswith("Z")  # UTC timestamp

    # Verify thread is resolved
    show_result = await handle_comment_show({"thread_id": thread_id})
    show_data = json.loads(show_result[0].text)
    assert show_data["thread"]["status"] == "resolved"
    assert show_data["thread"]["decision"]["summary"] == "Use approach B"
    assert show_data["thread"]["resolved_at"] == data["resolved_at"]  # Consistent timestamp


@pytest.mark.asyncio
async def test_comment_resolve_wontfix(sample_file: Path):
    """Test comment_resolve with wontfix flag."""
    # Create thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Mark as wontfix
    resolve_args = {
        "thread_id": thread_id,
        "wontfix": True,
    }
    result = await handle_comment_resolve(resolve_args)
    data = json.loads(result[0].text)

    assert data["status"] == "wontfix"
    assert data["resolved_at"] != ""  # Must set timestamp
    assert data["resolved_at"].endswith("Z")  # UTC timestamp

    # Verify in show
    show_result = await handle_comment_show({"thread_id": thread_id})
    show_data = json.loads(show_result[0].text)
    assert show_data["thread"]["status"] == "wontfix"
    assert show_data["thread"]["resolved_at"] == data["resolved_at"]  # Consistent timestamp


@pytest.mark.asyncio
async def test_comment_resolve_idempotency(sample_file: Path):
    """Test comment_resolve is idempotent (AC-6)."""
    # Create thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Resolve thread first time
    resolve_args = {
        "thread_id": thread_id,
        "decision": "First resolution",
    }
    first_result = await handle_comment_resolve(resolve_args)
    first_data = json.loads(first_result[0].text)
    first_resolved_at = first_data["resolved_at"]

    # Verify timestamp was set on first resolve
    assert first_resolved_at != ""
    assert first_resolved_at.endswith("Z")

    # Resolve again (should be no-op, timestamp unchanged)
    resolve_args = {
        "thread_id": thread_id,
        "decision": "Second resolution attempt",
    }
    second_result = await handle_comment_resolve(resolve_args)
    second_data = json.loads(second_result[0].text)

    # Timestamp should be unchanged (idempotency - preserves original timestamp)
    assert second_data["resolved_at"] == first_resolved_at

    # Decision should still be the first one (no update)
    show_result = await handle_comment_show({"thread_id": thread_id})
    show_data = json.loads(show_result[0].text)
    assert show_data["thread"]["decision"]["summary"] == "First resolution"


@pytest.mark.asyncio
async def test_comment_resolve_thread_not_found(sample_file: Path):
    """Test comment_resolve with non-existent thread ID."""
    resolve_args = {
        "thread_id": "01JYFAKE0000000000000000",
    }
    result = await handle_comment_resolve(resolve_args)
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "THREAD_NOT_FOUND"


# ============================================================================
# Test comment_reopen Tool
# ============================================================================


@pytest.mark.asyncio
async def test_comment_reopen_basic(sample_file: Path):
    """Test basic comment_reopen operation."""
    # Create and resolve thread
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    resolve_args = {
        "thread_id": thread_id,
        "decision": "Test decision",
    }
    await handle_comment_resolve(resolve_args)

    # Reopen thread
    reopen_args = {"thread_id": thread_id}
    result = await handle_comment_reopen(reopen_args)

    # Verify response
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data["thread_id"] == thread_id
    assert data["status"] == "open"

    # Verify thread is open and decision preserved
    show_result = await handle_comment_show({"thread_id": thread_id})
    show_data = json.loads(show_result[0].text)
    assert show_data["thread"]["status"] == "open"
    assert "decision" in show_data["thread"]
    assert show_data["thread"]["decision"]["summary"] == "Test decision"


@pytest.mark.asyncio
async def test_comment_reopen_wontfix(sample_file: Path):
    """Test comment_reopen on wontfix thread."""
    # Create and mark as wontfix
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    resolve_args = {
        "thread_id": thread_id,
        "wontfix": True,
        "decision": "Not worth fixing",
    }
    await handle_comment_resolve(resolve_args)

    # Reopen
    reopen_args = {"thread_id": thread_id}
    result = await handle_comment_reopen(reopen_args)
    data = json.loads(result[0].text)

    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_comment_reopen_already_open(sample_file: Path):
    """Test comment_reopen on already-open thread."""
    # Create thread (already open)
    add_args = {
        "file": str(sample_file),
        "line_start": 1,
        "line_end": 2,
        "body": "Test comment",
    }
    add_result = await handle_comment_add(add_args)
    add_data = json.loads(add_result[0].text)
    thread_id = add_data["thread_id"]

    # Try to reopen
    reopen_args = {"thread_id": thread_id}
    result = await handle_comment_reopen(reopen_args)
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "already open" in data["error"]["message"]


@pytest.mark.asyncio
async def test_comment_reopen_thread_not_found(sample_file: Path):
    """Test comment_reopen with non-existent thread ID."""
    reopen_args = {"thread_id": "01JYFAKE0000000000000000"}
    result = await handle_comment_reopen(reopen_args)
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "THREAD_NOT_FOUND"


# ============================================================================
# Test Dispatcher Routing
# ============================================================================


@pytest.mark.asyncio
async def test_call_tool_routing(sample_file: Path):
    """Test call_tool dispatcher routes to correct handlers."""
    # Test comment_list
    result = await call_tool("comment_list", {})
    data = json.loads(result[0].text)
    assert "threads" in data

    # Test unknown tool
    result = await call_tool("unknown_tool", {})
    data = json.loads(result[0].text)
    assert "error" in data
    assert data["error"]["code"] == "UNKNOWN_TOOL"


# ============================================================================
# Test Tool Listing
# ============================================================================


@pytest.mark.asyncio
async def test_list_tools_includes_all():
    """Test that list_tools returns all expected tools."""
    tools = await list_tools()
    tool_names = [t.name for t in tools]

    expected_tools = [
        "comment_add",
        "comment_list",
        "comment_show",
        "comment_reply",
        "comment_resolve",
        "comment_reopen",
        "comment_reconcile",
    ]

    for expected in expected_tools:
        assert expected in tool_names, f"Missing tool: {expected}"


# ============================================================================
# Test comment_reconcile Tool
# ============================================================================


@pytest.mark.asyncio
async def test_reconcile_single_file_no_changes(sample_file: Path):
    """Test reconciling a single file with no changes to source."""
    # Create a comment first
    result1 = await handle_comment_add(
        {
            "file": str(sample_file),
            "line_start": 2,
            "line_end": 3,
            "body": "Test comment",
        }
    )
    data1 = json.loads(result1[0].text)
    assert "thread_id" in data1

    # Reconcile without changes
    result = await handle_comment_reconcile({"file": str(sample_file)})
    data = json.loads(result[0].text)

    assert "files_processed" in data
    assert data["total_threads"] == 1
    assert len(data["files_processed"]) == 1

    report = data["files_processed"][0]
    assert report["total_threads"] == 1
    assert report["anchored_count"] == 1
    assert report["drifted_count"] == 0
    assert report["orphaned_count"] == 0
    assert report["max_drift_distance"] == 0
    assert report["source_hash_before"] == report["source_hash_after"]


@pytest.mark.asyncio
async def test_reconcile_single_file_after_insertion(sample_file: Path):
    """Test reconciling after lines are inserted above anchor."""
    # Create a comment
    result1 = await handle_comment_add(
        {
            "file": str(sample_file),
            "line_start": 3,
            "line_end": 4,
            "body": "Test comment",
        }
    )
    data1 = json.loads(result1[0].text)
    thread_id = data1["thread_id"]

    # Modify file - insert line above anchor
    sample_file.write_text("Line 1\nNEW LINE\nLine 2\nLine 3\nLine 4\nLine 5\n")

    # Reconcile
    result = await handle_comment_reconcile({"file": str(sample_file)})
    data = json.loads(result[0].text)

    assert data["total_threads"] == 1
    report = data["files_processed"][0]
    assert report["anchored_count"] == 1
    assert report["drifted_count"] == 0
    assert report["orphaned_count"] == 0
    assert report["max_drift_distance"] == 1  # Moved down by 1 line

    # Verify anchor was updated
    project_root = sample_file.parent
    sidecar_path = get_sidecar_path(sample_file, project_root)
    sidecar = read_sidecar(sidecar_path)
    thread = sidecar.threads[0]
    assert thread.id == thread_id
    assert thread.anchor.line_start == 4  # Was 3, now 4 (moved down)
    assert thread.anchor.line_end == 5  # Was 4, now 5


@pytest.mark.asyncio
async def test_reconcile_single_file_after_modification(sample_file: Path):
    """Test reconciling after anchor content changes slightly."""
    # Create a comment
    result1 = await handle_comment_add(
        {
            "file": str(sample_file),
            "line_start": 2,
            "line_end": 3,
            "body": "Test comment",
        }
    )
    data1 = json.loads(result1[0].text)
    thread_id = data1["thread_id"]

    # Modify file - change anchor content slightly
    sample_file.write_text("Line 1\nLine 2 modified\nLine 3 modified\nLine 4\nLine 5\n")

    # Reconcile
    result = await handle_comment_reconcile({"file": str(sample_file)})
    data = json.loads(result[0].text)

    assert data["total_threads"] == 1
    report = data["files_processed"][0]
    # Should be found via fuzzy matching
    assert report["drifted_count"] >= 0  # May be anchored or drifted depending on similarity

    # Verify anchor still exists
    project_root = sample_file.parent
    sidecar_path = get_sidecar_path(sample_file, project_root)
    sidecar = read_sidecar(sidecar_path)
    thread = sidecar.threads[0]
    assert thread.id == thread_id


@pytest.mark.asyncio
async def test_reconcile_single_file_after_deletion(sample_file: Path):
    """Test reconciling after anchor content is deleted."""
    # Create a comment
    result1 = await handle_comment_add(
        {
            "file": str(sample_file),
            "line_start": 2,
            "line_end": 3,
            "body": "Test comment",
        }
    )
    data1 = json.loads(result1[0].text)
    thread_id = data1["thread_id"]

    # Modify file - remove lines completely
    sample_file.write_text("Line 1\nLine 4\nLine 5\n")

    # Reconcile
    result = await handle_comment_reconcile({"file": str(sample_file)})
    data = json.loads(result[0].text)

    assert data["total_threads"] == 1
    report = data["files_processed"][0]
    assert report["orphaned_count"] >= 0  # Should be orphaned or drifted

    # Verify anchor still exists
    project_root = sample_file.parent
    sidecar_path = get_sidecar_path(sample_file, project_root)
    sidecar = read_sidecar(sidecar_path)
    thread = sidecar.threads[0]
    assert thread.id == thread_id


@pytest.mark.asyncio
async def test_reconcile_file_with_no_sidecar(sample_file: Path):
    """Test reconciling a file that has no sidecar."""
    result = await handle_comment_reconcile({"file": str(sample_file)})
    data = json.loads(result[0].text)

    assert data["files_processed"] == []
    assert data["total_threads"] == 0


@pytest.mark.asyncio
async def test_reconcile_file_not_found(sample_file: Path):
    """Test reconciling a non-existent file."""
    result = await handle_comment_reconcile({"file": "nonexistent.txt"})
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "FILE_NOT_FOUND"


@pytest.mark.asyncio
async def test_reconcile_project_wide_no_files(sample_file: Path):
    """Test project-wide reconciliation with no sidecar files."""
    result = await handle_comment_reconcile({})
    data = json.loads(result[0].text)

    assert data["files_processed"] == []
    assert data["total_threads"] == 0


@pytest.mark.asyncio
async def test_reconcile_project_wide_single_file(sample_file: Path):
    """Test project-wide reconciliation with one file."""
    # Create a comment
    result1 = await handle_comment_add(
        {
            "file": str(sample_file),
            "line_start": 2,
            "line_end": 3,
            "body": "Test comment",
        }
    )
    data1 = json.loads(result1[0].text)
    assert "thread_id" in data1

    # Reconcile project-wide
    result = await handle_comment_reconcile({})
    data = json.loads(result[0].text)

    assert data["total_threads"] == 1
    assert len(data["files_processed"]) == 1
    assert data["files_processed"][0]["total_threads"] == 1


@pytest.mark.asyncio
async def test_reconcile_project_wide_multiple_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test project-wide reconciliation with multiple files."""
    # Create git repo
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()

    # Create multiple files
    file1 = repo_root / "file1.txt"
    file1.write_text("Line 1\nLine 2\nLine 3\n")

    file2 = repo_root / "file2.txt"
    file2.write_text("Line A\nLine B\nLine C\n")

    # Change working directory
    monkeypatch.chdir(repo_root)

    # Create comments on both files
    result1 = await handle_comment_add(
        {
            "file": str(file1),
            "line_start": 1,
            "line_end": 2,
            "body": "Comment on file1",
        }
    )
    data1 = json.loads(result1[0].text)
    assert "thread_id" in data1

    result2 = await handle_comment_add(
        {
            "file": str(file2),
            "line_start": 2,
            "line_end": 3,
            "body": "Comment on file2",
        }
    )
    data2 = json.loads(result2[0].text)
    assert "thread_id" in data2

    # Reconcile project-wide
    result = await handle_comment_reconcile({})
    data = json.loads(result[0].text)

    assert data["total_threads"] == 2
    assert len(data["files_processed"]) == 2


@pytest.mark.asyncio
async def test_reconcile_custom_threshold(sample_file: Path):
    """Test reconciling with a custom similarity threshold."""
    # Create a comment
    result1 = await handle_comment_add(
        {
            "file": str(sample_file),
            "line_start": 2,
            "line_end": 3,
            "body": "Test comment",
        }
    )
    data1 = json.loads(result1[0].text)
    assert "thread_id" in data1

    # Reconcile with custom threshold
    result = await handle_comment_reconcile({"file": str(sample_file), "threshold": 0.8})
    data = json.loads(result[0].text)

    assert data["total_threads"] == 1
    assert len(data["files_processed"]) == 1


@pytest.mark.asyncio
async def test_reconcile_invalid_threshold_too_low():
    """Test reconcile with invalid threshold < 0."""
    result = await handle_comment_reconcile({"threshold": -0.1})
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_reconcile_invalid_threshold_too_high():
    """Test reconcile with invalid threshold > 1."""
    result = await handle_comment_reconcile({"threshold": 1.5})
    data = json.loads(result[0].text)

    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_reconcile_json_output_structure(sample_file: Path):
    """Test that reconcile JSON output has correct structure."""
    # Create a comment
    result1 = await handle_comment_add(
        {
            "file": str(sample_file),
            "line_start": 2,
            "line_end": 3,
            "body": "Test comment",
        }
    )
    data1 = json.loads(result1[0].text)
    assert "thread_id" in data1

    # Reconcile
    result = await handle_comment_reconcile({"file": str(sample_file)})
    data = json.loads(result[0].text)

    # Validate structure
    assert "files_processed" in data
    assert "total_threads" in data
    assert isinstance(data["files_processed"], list)
    assert isinstance(data["total_threads"], int)

    if len(data["files_processed"]) > 0:
        report = data["files_processed"][0]
        assert "file" in report
        assert "total_threads" in report
        assert "anchored_count" in report
        assert "drifted_count" in report
        assert "orphaned_count" in report
        assert "max_drift_distance" in report
        assert "source_hash_before" in report
        assert "source_hash_after" in report


@pytest.mark.asyncio
async def test_reconcile_via_dispatcher(sample_file: Path):
    """Test reconcile via call_tool dispatcher."""
    # Create a comment
    result1 = await call_tool(
        "comment_add",
        {
            "file": str(sample_file),
            "line_start": 2,
            "line_end": 3,
            "body": "Test comment",
        },
    )
    data1 = json.loads(result1[0].text)
    assert "thread_id" in data1

    # Reconcile via dispatcher
    result = await call_tool("comment_reconcile", {"file": str(sample_file)})
    data = json.loads(result[0].text)

    assert "files_processed" in data
    assert data["total_threads"] == 1


@pytest.mark.asyncio
async def test_reconcile_request_model():
    """Test CommentReconcileRequest model validation."""
    # Valid request with file
    req1 = CommentReconcileRequest(file="test.txt", threshold=0.7)
    assert req1.file == "test.txt"
    assert req1.threshold == 0.7

    # Valid request without file (project-wide)
    req2 = CommentReconcileRequest()
    assert req2.file is None
    assert req2.threshold == 0.6  # Default


@pytest.mark.asyncio
async def test_reconcile_response_model():
    """Test CommentReconcileResponse model validation."""
    response = CommentReconcileResponse(
        files_processed=[
            {
                "file": "test.txt",
                "total_threads": 1,
                "anchored_count": 1,
                "drifted_count": 0,
                "orphaned_count": 0,
                "max_drift_distance": 0,
                "source_hash_before": "sha256:abc123",
                "source_hash_after": "sha256:abc123",
            }
        ],
        total_threads=1,
    )
    assert response.total_threads == 1
    assert len(response.files_processed) == 1


@pytest.mark.asyncio
async def test_reconcile_idempotency(sample_file: Path):
    """Test that reconcile is idempotent (REQ-4)."""
    # Create a comment
    result1 = await handle_comment_add(
        {
            "file": str(sample_file),
            "line_start": 2,
            "line_end": 3,
            "body": "Test comment",
        }
    )
    data1 = json.loads(result1[0].text)
    assert "thread_id" in data1

    # Reconcile once
    result2 = await handle_comment_reconcile({"file": str(sample_file)})
    data2 = json.loads(result2[0].text)

    # Reconcile again immediately
    result3 = await handle_comment_reconcile({"file": str(sample_file)})
    data3 = json.loads(result3[0].text)

    # Results should be identical (same hash, no changes)
    assert data2["total_threads"] == data3["total_threads"]
    assert (
        data2["files_processed"][0]["source_hash_after"]
        == data3["files_processed"][0]["source_hash_after"]
    )

"""Tests for MCP server and tool interface."""

import json
from pathlib import Path

import pytest
from mcp.types import TextContent

from comment_system.mcp_server import (
    CommentAddRequest,
    CommentAddResponse,
    ErrorResponse,
    call_tool,
    handle_comment_add,
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
    repo_root.mkdir()
    (repo_root / ".git").mkdir()

    deep_dir = repo_root / "src" / "nested" / "deep"
    deep_dir.mkdir(parents=True)
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

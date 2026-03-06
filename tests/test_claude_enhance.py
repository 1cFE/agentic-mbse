"""Tests for claude_enhance module."""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_mbse.extraction.claude_enhance import (
    _extract_result_event,
    extract_page_with_claude,
    invoke_claude,
    validate_claude_output,
)
from agentic_mbse.extraction.types import CostRecord


# ---------------------------------------------------------------------------
# Fixtures: actual JSON payloads from Claude Code 2.1.62
# ---------------------------------------------------------------------------

_JSON_ARRAY_PAYLOAD = [
    {"type": "system", "subtype": "init", "apiKeySource": "env"},
    {
        "type": "assistant",
        "message": {
            "id": "msg_abc",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "# Extracted Content"}],
        },
    },
    {
        "type": "result",
        "subtype": "success",
        "result": "# Extracted Content\n\nSome markdown.",
        "total_cost_usd": 0.015,
        "usage": {"input_tokens": 3000, "output_tokens": 150},
        "model": "claude-sonnet-4-20250514",
    },
]

_JSON_DICT_PAYLOAD = {
    "result": "# Old Format\n\nText.",
    "total_cost_usd": 0.012,
    "usage": {"input_tokens": 2000, "output_tokens": 100},
    "model": "claude-sonnet-4-20250514",
}


# ---------------------------------------------------------------------------
# TestExtractResultEvent — unit tests for _extract_result_event
# ---------------------------------------------------------------------------


class TestExtractResultEvent:
    def test_json_array_format(self):
        """New format (JSON array) → extracts the result event."""
        result = _extract_result_event(_JSON_ARRAY_PAYLOAD)
        assert result["result"] == "# Extracted Content\n\nSome markdown."
        assert result["total_cost_usd"] == 0.015
        assert result["usage"]["input_tokens"] == 3000

    def test_json_dict_format(self):
        """Old format (single dict) → returned as-is."""
        result = _extract_result_event(_JSON_DICT_PAYLOAD)
        assert result["result"] == "# Old Format\n\nText."
        assert result["total_cost_usd"] == 0.012

    def test_error_event_raises(self):
        """Result event with is_error=true → RuntimeError."""
        payload = [
            {"type": "result", "is_error": True, "result": "Rate limit exceeded"},
        ]
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            _extract_result_event(payload)

    def test_empty_array_raises(self):
        with pytest.raises(RuntimeError, match="unexpected JSON structure"):
            _extract_result_event([])

    def test_no_result_event_raises(self):
        """Array with no type=result entry → RuntimeError."""
        payload = [
            {"type": "system", "subtype": "init"},
            {"type": "assistant", "message": {}},
        ]
        with pytest.raises(RuntimeError, match="no result event"):
            _extract_result_event(payload)

    def test_non_list_non_dict_raises(self):
        with pytest.raises(RuntimeError, match="unexpected JSON structure"):
            _extract_result_event("not a dict or list")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# TestInvokeClaude — integration test with subprocess mock
# ---------------------------------------------------------------------------


class TestInvokeClaude:
    @patch("agentic_mbse.extraction.claude_enhance.subprocess.run")
    def test_parses_json_array(self, mock_run):
        """invoke_claude handles the JSON array format from Claude Code >=2.1."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=json.dumps(_JSON_ARRAY_PAYLOAD), stderr="",
        )
        result = invoke_claude("test prompt")
        assert result["result"] == "# Extracted Content\n\nSome markdown."
        assert result["total_cost_usd"] == 0.015

    @patch("agentic_mbse.extraction.claude_enhance.subprocess.run")
    def test_parses_json_dict(self, mock_run):
        """invoke_claude handles the old single-dict format."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=json.dumps(_JSON_DICT_PAYLOAD), stderr="",
        )
        result = invoke_claude("test prompt")
        assert result["result"] == "# Old Format\n\nText."

    @patch("agentic_mbse.extraction.claude_enhance.subprocess.run")
    def test_non_zero_returncode_raises(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="auth error",
        )
        with pytest.raises(RuntimeError, match="rc=1"):
            invoke_claude("test prompt")

    @patch("agentic_mbse.extraction.claude_enhance.subprocess.run")
    def test_timeout_raises(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=120)
        with pytest.raises(RuntimeError, match="timed out"):
            invoke_claude("test prompt")

    @patch("agentic_mbse.extraction.claude_enhance.subprocess.run")
    def test_invalid_json_raises(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="not json", stderr="",
        )
        with pytest.raises(RuntimeError, match="non-JSON"):
            invoke_claude("test prompt")


class TestValidateClaudeOutput:
    def test_accept_normal_output(self):
        accept, reason = validate_claude_output("y " * 450, "x " * 500, 0)
        assert accept
        assert reason == ""

    def test_reject_empty(self):
        accept, reason = validate_claude_output("", "x " * 500, 0)
        assert not accept
        assert "empty" in reason.lower()

    def test_reject_whitespace_only(self):
        accept, reason = validate_claude_output("   \n\t  ", "x " * 500, 0)
        assert not accept
        assert "empty" in reason.lower()

    def test_reject_truncated(self):
        original = "x " * 500  # 1000 chars
        claude = "y " * 100  # 200 chars < 500 (50% of 1000)
        accept, reason = validate_claude_output(claude, original, 0)
        assert not accept
        assert ">50% character drop" in reason

    def test_accept_short_page_exempt(self):
        # Original < 200 chars → ratio check is exempt
        accept, _ = validate_claude_output("[Figure 3: Reactor]", "[Figure 3]", 0)
        assert accept

    def test_reject_prompt_leak(self):
        # Leaked text must be long enough to not trigger >50% drop first
        leaked = "Read the image file at /tmp/page_001.png and extract..." + "x " * 500
        accept, reason = validate_claude_output(leaked, "x " * 500, 0)
        assert not accept
        assert "prompt leak" in reason.lower()

    def test_accept_at_boundary(self):
        # Exactly 50% should pass (< 0.5 is the threshold, not <=)
        original = "x" * 200
        claude = "y" * 100  # exactly 50%
        accept, _ = validate_claude_output(claude, original, 0)
        assert accept

    def test_page_num_in_reason(self):
        accept, reason = validate_claude_output("", "x " * 500, 42)
        assert "42" in reason


class TestExtractPageWithClaude:
    @patch("agentic_mbse.extraction.claude_enhance.invoke_claude")
    @patch("agentic_mbse.extraction.claude_enhance.render_page_image")
    def test_returns_cost_record(self, mock_render, mock_claude):
        mock_render.return_value = Path("/tmp/fake_page.png")
        mock_claude.return_value = {
            "result": "# Page Content\n\nSome text here.",
            "total_cost_usd": 0.078,
            "usage": {"input_tokens": 5000, "output_tokens": 200},
            "model": "claude-sonnet-4-20250514",
        }

        markdown, cost = extract_page_with_claude(Path("/tmp/fake.pdf"), page_num=3)

        assert markdown == "# Page Content\n\nSome text here."
        assert isinstance(cost, CostRecord)
        assert cost.page_num == 3
        assert cost.cost_usd == 0.078
        assert cost.input_tokens == 5000
        assert cost.output_tokens == 200
        assert "sonnet" in cost.model

    @patch("agentic_mbse.extraction.claude_enhance.invoke_claude")
    def test_uses_provided_image_path(self, mock_claude):
        mock_claude.return_value = {
            "result": "# Content",
            "total_cost_usd": 0.05,
            "usage": {"input_tokens": 1000, "output_tokens": 100},
            "model": "sonnet",
        }

        image_path = Path("/tmp/existing_image.png")
        markdown, cost = extract_page_with_claude(
            Path("/tmp/fake.pdf"),
            page_num=0,
            image_path=image_path,
        )

        # Verify the prompt references the provided image path
        call_args = mock_claude.call_args
        assert str(image_path.resolve()) in call_args[0][0]

    @patch("agentic_mbse.extraction.claude_enhance.invoke_claude")
    @patch("agentic_mbse.extraction.claude_enhance.render_page_image")
    def test_custom_prompt(self, mock_render, mock_claude):
        mock_render.return_value = Path("/tmp/fake_page.png")
        mock_claude.return_value = {
            "result": "| a | b |",
            "total_cost_usd": 0.01,
            "usage": {"input_tokens": 500, "output_tokens": 50},
            "model": "sonnet",
        }

        custom_prompt = "Extract only tables from this page."
        extract_page_with_claude(
            Path("/tmp/fake.pdf"),
            page_num=0,
            prompt=custom_prompt,
        )

        call_args = mock_claude.call_args
        assert custom_prompt in call_args[0][0]

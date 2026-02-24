"""Tests for claude_enhance module."""

from pathlib import Path
from unittest.mock import patch

from agentic_mbse.extraction.claude_enhance import (
    extract_page_with_claude,
    validate_claude_output,
)
from agentic_mbse.extraction.types import CostRecord


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

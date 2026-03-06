"""Claude vision enhancement for PDF page extraction.

Provides page image rendering, Claude CLI invocation, page-level extraction,
and output validation.  The ``invoke_claude()`` helper is shared with
``tables.py`` for table-level Claude extraction.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

from agentic_mbse.extraction.types import CostRecord

# ---------------------------------------------------------------------------
# Prompt constant — embedded from tests/corpus/prompts/extract_baseline.txt
# ---------------------------------------------------------------------------

_PAGE_EXTRACTION_PROMPT = """\
You are extracting the content of a scientific/technical document from page images.
Produce clean markdown following these rules:

FORMAT:
- ATX headings (# ## ###) matching the document's section hierarchy
- Pipe tables (| col1 | col2 |) for tabular data, with separator row
- LaTeX math: inline $...$ and display $$...$$
- Figure placeholders: [Figure N: <caption text>]
- No page numbers, running headers, or footers

FIDELITY:
- Preserve ALL numerical values exactly as printed
- Preserve ALL equation content — transcribe to LaTeX
- Preserve table structure including merged cells (use colspan/rowspan if needed)
- If text is ambiguous or partially obscured, include best guess with [?] marker

OUTPUT:
- Output ONLY the markdown content, no commentary or explanation
- Pages should flow continuously (no page break markers unless a table/section splits)"""


# ---------------------------------------------------------------------------
# Claude CLI invocation
# ---------------------------------------------------------------------------


def _extract_result_event(data: dict | list) -> dict:
    """Extract the result event from ``claude -p --output-format json`` output.

    Claude Code >=2.1 returns a JSON array of typed events::

        [{"type":"system",...}, {"type":"assistant",...}, {"type":"result",...}]

    Older versions returned a single dict with ``result``, ``total_cost_usd``,
    etc. directly.  This function handles both formats.
    """
    if isinstance(data, dict):
        return data

    if not isinstance(data, list) or not data:
        raise RuntimeError("claude -p returned unexpected JSON structure")

    for event in data:
        if isinstance(event, dict) and event.get("type") == "result":
            if event.get("is_error"):
                msg = event.get("result", "unknown error")
                raise RuntimeError(f"claude -p returned error: {msg}")
            return event

    raise RuntimeError(
        "claude -p JSON output contained no result event"
    )


def invoke_claude(
    prompt: str,
    model: str = "sonnet",
    timeout: int = 120,
) -> dict:
    """Invoke ``claude -p`` with prompt via stdin, return parsed JSON response.

    Must unset ``CLAUDECODE`` env var to avoid nested session guard.
    """
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    cmd = [
        "claude",
        "-p",
        "--model",
        model,
        "--output-format",
        "json",
        "--dangerously-skip-permissions",
        "--no-session-persistence",
        "--allowedTools",
        "Read",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            # Detach child from controlling terminal so claude CLI's status
            # line rendering (writes to /dev/tty) can't corrupt parent output.
            start_new_session=True,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude -p timed out after {timeout}s")

    if result.returncode != 0:
        stderr = result.stderr[:500] if result.stderr else "(no stderr)"
        raise RuntimeError(f"claude -p failed (rc={result.returncode}): {stderr}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"claude -p returned non-JSON output: {result.stdout[:300]}"
        )

    return _extract_result_event(data)


# ---------------------------------------------------------------------------
# Page image rendering
# ---------------------------------------------------------------------------


def render_page_image(
    pdf_path: Path,
    page_num: int,
    dpi: int = 200,
    output_dir: Path | None = None,
) -> Path:
    """Render a single PDF page as PNG using pymupdf.

    When *output_dir* is provided, saves to
    ``output_dir/page_{page_num:03d}.png``.  Otherwise writes to a
    temporary file.  Caller is responsible for cleanup.
    """
    import pymupdf  # type: ignore[import-untyped]

    doc = pymupdf.open(str(pdf_path))
    try:
        page = doc[page_num]
        mat = pymupdf.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / f"page_{page_num:03d}.png"
            pix.save(str(out_path))
            return out_path
        else:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            pix.save(tmp.name)
            return Path(tmp.name)
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# Claude page extraction
# ---------------------------------------------------------------------------


def extract_page_with_claude(
    pdf_path: Path,
    page_num: int,
    model: str = "sonnet",
    prompt: str | None = None,
    image_path: Path | None = None,
    timeout: int = 120,
) -> tuple[str, CostRecord]:
    """Extract a single page using Claude vision.

    If *image_path* is provided, uses that image.  Otherwise renders
    the page from the PDF.

    Returns ``(markdown, CostRecord)``.
    """
    if prompt is None:
        prompt = _PAGE_EXTRACTION_PROMPT

    if image_path is None:
        image_path = render_page_image(pdf_path, page_num)
        cleanup_image = True
    else:
        cleanup_image = False

    try:
        full_prompt = (
            f"Read the image file at {image_path.resolve()} "
            f"and extract its content.\n\n{prompt}"
        )
        start = time.time()
        response = invoke_claude(full_prompt, model=model, timeout=timeout)
        elapsed = time.time() - start

        markdown = response.get("result", "")
        cost = CostRecord(
            page_num=page_num,
            cost_usd=response.get("total_cost_usd", 0),
            input_tokens=response.get("usage", {}).get("input_tokens", 0),
            output_tokens=response.get("usage", {}).get("output_tokens", 0),
            model=response.get("model", model),
            elapsed_seconds=elapsed,
        )
        return markdown, cost
    finally:
        if cleanup_image and image_path is not None:
            image_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Output validation
# ---------------------------------------------------------------------------


def validate_claude_output(
    claude_markdown: str,
    original_markdown: str,
    page_num: int,
) -> tuple[bool, str]:
    """Sanity-check Claude output before accepting.

    Rejects if:
    1. Empty or whitespace-only
    2. >50% character drop vs original (unless original < 200 chars)
    3. Contains literal prompt text (prompt leak)

    Returns ``(accept, reason)``.
    """
    if not claude_markdown or not claude_markdown.strip():
        return False, f"Page {page_num}: Claude output is empty"

    orig_len = len(original_markdown.strip())
    claude_len = len(claude_markdown.strip())

    if orig_len >= 200 and claude_len < orig_len * 0.5:
        return False, (
            f"Page {page_num}: >50% character drop "
            f"({claude_len} vs {orig_len} original)"
        )

    # Check for prompt leak (first line of our prompt)
    if "Read the image file at" in claude_markdown[:200]:
        return False, f"Page {page_num}: prompt leak detected"

    return True, ""

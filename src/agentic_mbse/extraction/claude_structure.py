"""Claude-powered document structure detection and repair.

Phase A detects document style (heading convention, doc type, running headers)
from page images + markdown.  Phase B inserts missing markdown headers via
text-anchored structured diffs processed in chunks.

This module is standalone — pipeline integration is done in extract_cli.py.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_mbse.extraction.ai_repair import render_page_image
from agentic_mbse.extraction.postprocess import _is_noise_header

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PAGE_MARKER_RE = re.compile(r"^<!--\s*PAGE:(\d+)\s*-->$", re.MULTILINE)
_HEADER_RE = re.compile(r"^(#{2,6}) (.+)$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class DocumentStyle:
    """Style classification for a PDF document."""

    doc_type: str
    heading_convention: str
    has_toc: bool = False
    running_headers: list[str] | None = None
    page_number_format: str = "none"

    def __post_init__(self) -> None:
        if self.running_headers is None:
            self.running_headers = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_type": self.doc_type,
            "heading_convention": self.heading_convention,
            "has_toc": self.has_toc,
            "running_headers": self.running_headers,
            "page_number_format": self.page_number_format,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DocumentStyle:
        return cls(
            doc_type=d.get("doc_type", "unknown"),
            heading_convention=d.get("heading_convention", "unknown"),
            has_toc=d.get("has_toc", False),
            running_headers=d.get("running_headers", []),
            page_number_format=d.get("page_number_format", "none"),
        )


@dataclass
class HeaderInsertion:
    """A text-anchored header insertion instruction."""

    anchor_text: str
    level: int  # 2–6, mapping to ## through ######
    title: str
    insert_position: str  # "before" | "after"


# ---------------------------------------------------------------------------
# JSON response parser
# ---------------------------------------------------------------------------

_FENCED_JSON_RE = re.compile(r"```(?:json)?\s*\n(.*?)\n\s*```", re.DOTALL)


def _parse_json_response(text: str) -> Any | None:
    """Parse JSON from Claude's stdout, stripping common wrappers.

    Handles: bare JSON, markdown-fenced JSON (```json ... ```),
    leading/trailing prose around a JSON block.  Returns None if
    no valid JSON found.
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # Try bare JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try fenced JSON
    m = _FENCED_JSON_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find a JSON object or array in the text
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        if start == -1:
            continue
        end = text.rfind(end_char)
        if end <= start:
            continue
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            continue

    return None


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


@dataclass
class _Chunk:
    """A page-aligned window of the document for chunked processing."""

    start_page: int  # 1-indexed page number
    end_page: int  # 1-indexed, last page included in chunk
    start_line: int  # line index in full markdown
    end_line: int  # line index (exclusive)
    text: str  # the chunk's markdown text


def _chunk_by_pages(
    lines: list[str],
    chunk_size: int = 25,
    overlap: int = 3,
) -> list[_Chunk]:
    """Split markdown lines into page-aligned chunks with overlap."""
    # Build page_number → line_index mapping
    page_starts: dict[int, int] = {}
    for i, line in enumerate(lines):
        m = _PAGE_MARKER_RE.match(line.strip())
        if m:
            page_starts[int(m.group(1))] = i

    if not page_starts:
        # No page markers — return entire document as one chunk
        text = "\n".join(lines)
        return [_Chunk(start_page=1, end_page=1, start_line=0, end_line=len(lines), text=text)]

    sorted_pages = sorted(page_starts.keys())
    chunks: list[_Chunk] = []
    i = 0
    stride = chunk_size - overlap

    while i < len(sorted_pages):
        start_page = sorted_pages[i]
        end_idx = min(i + chunk_size, len(sorted_pages)) - 1
        end_page = sorted_pages[end_idx]

        start_line = page_starts[start_page]
        # End line: start of next page after end_page, or end of document
        if end_idx + 1 < len(sorted_pages):
            end_line = page_starts[sorted_pages[end_idx + 1]]
        else:
            end_line = len(lines)

        text = "\n".join(lines[start_line:end_line])
        chunks.append(
            _Chunk(
                start_page=start_page,
                end_page=end_page,
                start_line=start_line,
                end_line=end_line,
                text=text,
            )
        )

        i += stride
        # If advancing by stride still covers the rest, stop
        if i >= len(sorted_pages) and chunks:
            break

    return chunks


# ---------------------------------------------------------------------------
# Gate heuristic
# ---------------------------------------------------------------------------


def needs_claude_structure(md: str) -> bool:
    """Return True if the markdown likely needs Claude-powered structure repair.

    Computes three metrics:
    1. headers_per_page — if < 0.1, too sparse
    2. noise_fraction — if > 0.3, headers are garbage
    3. depth_variance — if zero AND hpp >= 0.1, headers are flat
    """
    # Count pages
    page_count = len(_PAGE_MARKER_RE.findall(md))
    if page_count == 0:
        return True

    # Find all headers
    header_matches = _HEADER_RE.findall(md)  # list of (prefix, text) tuples
    total_headers = len(header_matches)

    headers_per_page = total_headers / page_count

    # Sparse headers
    if headers_per_page < 0.1:
        return True

    # Noise fraction
    noise_count = sum(1 for _, text in header_matches if _is_noise_header(text))
    noise_fraction = noise_count / total_headers if total_headers > 0 else 0.0
    if noise_fraction > 0.3:
        return True

    # Depth variance — check if multiple heading levels exist among valid headers
    valid_levels: set[int] = set()
    for prefix, text in header_matches:
        if not _is_noise_header(text):
            valid_levels.add(len(prefix))

    if len(valid_levels) <= 1 and headers_per_page >= 0.1:
        return True

    return False


# ---------------------------------------------------------------------------
# Header insertion
# ---------------------------------------------------------------------------


def apply_insertions(md: str, insertions: list[HeaderInsertion]) -> tuple[str, int, int, list[str]]:
    """Apply header insertions to markdown text.

    Returns (modified_md, inserted_count, skipped_count, warnings).

    Algorithm: locate each anchor, sort by position descending (reverse
    order), insert headers from bottom to top so indices stay valid.
    """
    if not insertions:
        return md, 0, 0, []

    lines = md.split("\n")
    warnings: list[str] = []
    located: list[tuple[int, HeaderInsertion]] = []

    for ins in insertions:
        # Find lines containing the anchor text
        matches = [i for i, line in enumerate(lines) if ins.anchor_text in line]

        if len(matches) == 0:
            warnings.append(f"Anchor not found: '{ins.anchor_text}' for header '{ins.title}'")
            continue
        if len(matches) > 1:
            warnings.append(
                f"Ambiguous anchor: '{ins.anchor_text}' found {len(matches)} times "
                f"for header '{ins.title}'"
            )
            continue

        line_idx = matches[0]

        # Duplicate prevention: check ±2 lines for existing header with same title
        header_line = "#" * ins.level + " " + ins.title
        normalized_title = ins.title.strip().lower()
        duplicate = False
        for offset in range(-2, 3):
            check_idx = line_idx + offset
            if 0 <= check_idx < len(lines):
                check_line = lines[check_idx].strip()
                # Strip leading # and whitespace, compare titles
                stripped = re.sub(r"^#{1,6}\s*", "", check_line).strip().lower()
                if stripped == normalized_title:
                    duplicate = True
                    break

        if duplicate:
            warnings.append(f"Header already exists near anchor: '{ins.title}'")
            continue

        located.append((line_idx, ins))

    # Sort by line index descending — insert from bottom to top
    located.sort(key=lambda x: x[0], reverse=True)

    inserted = 0
    skipped = len(insertions) - len(located)

    for line_idx, ins in located:
        header_line = "#" * ins.level + " " + ins.title
        if ins.insert_position == "before":
            lines.insert(line_idx, "")
            lines.insert(line_idx, header_line)
        else:  # "after"
            lines.insert(line_idx + 1, "")
            lines.insert(line_idx + 1, header_line)
        inserted += 1

    return "\n".join(lines), inserted, skipped, warnings


# ---------------------------------------------------------------------------
# Running header strip
# ---------------------------------------------------------------------------


def _normalize_whitespace(s: str) -> str:
    """Collapse whitespace and lowercase for comparison."""
    return re.sub(r"\s+", " ", s.strip()).lower()


def strip_detected_headers(md: str, patterns: list[str]) -> str:
    """Remove lines matching detected running header patterns.

    Uses case-insensitive, whitespace-collapsed comparison.
    Patterns come from Phase A's explicit detection.
    """
    if not patterns:
        return md

    normalized_patterns = {_normalize_whitespace(p) for p in patterns}
    lines = md.split("\n")
    result: list[str] = []

    for line in lines:
        if _normalize_whitespace(line) in normalized_patterns and line.strip():
            continue
        result.append(line)

    return "\n".join(result)


# ---------------------------------------------------------------------------
# Subprocess call helper
# ---------------------------------------------------------------------------


def _call_claude(
    prompt: str,
    image_paths: list[Path],
    model: str,
    timeout: int = 120,
    retries: int = 1,
) -> tuple[str | None, list[str]]:
    """Call ``claude -p`` with optional images and retry logic.

    Returns ``(stdout_text, warnings)`` or ``(None, warnings)`` on failure.
    """
    warnings: list[str] = []
    image_names = [p.name for p in image_paths]
    cwd = str(image_paths[0].parent) if image_paths else None
    cmd = ["claude", "-p", "--model", model, prompt, *image_names]

    for attempt in range(1 + retries):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip(), warnings
            if attempt < retries:
                warnings.append(
                    f"claude -p attempt {attempt + 1} failed (rc={result.returncode}), retrying"
                )
            else:
                warnings.append(
                    f"claude -p failed after {attempt + 1} attempts (rc={result.returncode})"
                )
                return None, warnings
        except subprocess.TimeoutExpired:
            warnings.append(f"claude -p timed out after {timeout}s")
            return None, warnings
        except FileNotFoundError:
            warnings.append("claude CLI not found on PATH")
            return None, warnings

    return None, warnings


# ---------------------------------------------------------------------------
# Phase A — Style detection
# ---------------------------------------------------------------------------

_PHASE_A_PROMPT = """\
You are analyzing a PDF document's structure. Based on the page images and \
the first few pages of extracted markdown below, classify the document.

Return ONLY a JSON object with these fields:
- doc_type: one of "academic_paper", "slide_deck", "technical_report", "ocr_scan", "word_doc"
- heading_convention: one of "numbered_bold", "unnumbered_bold", "italic_subsections", "slide_titles", "mixed"
- has_toc: true if the document has a table of contents
- running_headers: list of repeated header/footer text strings (empty list if none)
- page_number_format: one of "bare", "bold", "none", "footer"

Markdown (first ~200 lines):
```
{markdown}
```"""

_FALLBACK_STYLE = DocumentStyle(
    doc_type="unknown",
    heading_convention="unknown",
    has_toc=False,
    running_headers=[],
    page_number_format="none",
)


def detect_document_style(
    md: str,
    pdf_path: Path,
    output_dir: Path,
    model: str = "haiku",
) -> tuple[DocumentStyle, list[str]]:
    """Detect document style from page images and markdown (Phase A).

    Caches result to ``{output_dir}/style.json``.  On cache hit, returns
    immediately without calling Claude.
    """
    warnings: list[str] = []
    cache_path = output_dir / "style.json"

    # Cache check
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text())
            return DocumentStyle.from_dict(data), warnings
        except (json.JSONDecodeError, KeyError) as exc:
            warnings.append(f"Corrupt style cache, re-detecting: {exc}")

    # Extract first ~200 lines (up to PAGE:4)
    lines = md.split("\n")
    cutoff = len(lines)
    for i, line in enumerate(lines):
        m = _PAGE_MARKER_RE.match(line.strip())
        if m and int(m.group(1)) >= 4:
            cutoff = i
            break
    first_lines = "\n".join(lines[:cutoff])

    # Determine page count and render thumbnails
    page_numbers = [int(x) for x in _PAGE_MARKER_RE.findall(md)]
    max_page = max(page_numbers) if page_numbers else 1
    pages_to_render = [p for p in range(min(3, max_page))]  # 0-indexed for render_page_image

    image_paths: list[Path] = []
    try:
        for page_num in pages_to_render:
            try:
                img = render_page_image(pdf_path, page_num, dpi=150)
                image_paths.append(img)
            except Exception as exc:
                warnings.append(f"Failed to render page {page_num}: {exc}")

        prompt = _PHASE_A_PROMPT.format(markdown=first_lines)
        text, call_warnings = _call_claude(prompt, image_paths, model=model)
        warnings.extend(call_warnings)

        if text is None:
            return DocumentStyle(**_FALLBACK_STYLE.__dict__), warnings

        parsed = _parse_json_response(text)
        if parsed is None or not isinstance(parsed, dict):
            warnings.append("Phase A: malformed JSON response")
            return DocumentStyle(**_FALLBACK_STYLE.__dict__), warnings

        style = DocumentStyle.from_dict(parsed)

        # Cache to disk
        output_dir.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(style.to_dict(), indent=2))

        return style, warnings
    finally:
        for img in image_paths:
            try:
                img.unlink(missing_ok=True)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Phase B — Structural repair
# ---------------------------------------------------------------------------

_PHASE_B_PROMPT = """\
You are adding markdown section headers to a document excerpt.
The document is a {doc_type} with {heading_convention} heading style.

For each heading you identify, return a JSON array of objects with:
- anchor_text: a unique text snippet (15-60 chars) from the line where or near where the heading should go
- level: heading level (2 for ##, 3 for ###, etc.)
- title: the heading text
- insert_position: "before" to insert the heading before the anchor line

Rules:
- Use text that appears EXACTLY in the markdown below as anchor_text
- Do NOT include any existing markdown headers (lines starting with #) — only identify MISSING headers
- Keep the heading hierarchy consistent (## for top-level, ### for subsections)

Markdown excerpt:
```
{chunk_markdown}
```"""


def _validate_insertion(raw: dict, chunk_text: str) -> HeaderInsertion | None:
    """Validate a raw insertion dict and return HeaderInsertion or None."""
    anchor = raw.get("anchor_text", "")
    level = raw.get("level", 0)
    title = raw.get("title", "")
    position = raw.get("insert_position", "before")

    if not anchor or not title:
        return None
    if not isinstance(level, int) or level < 2 or level > 6:
        return None
    if position not in ("before", "after"):
        return None
    if anchor not in chunk_text:
        return None

    return HeaderInsertion(
        anchor_text=anchor,
        level=level,
        title=title,
        insert_position=position,
    )


def repair_structure(
    md: str,
    pdf_path: Path,
    style: DocumentStyle,
    model: str = "sonnet",
) -> tuple[list[HeaderInsertion], list[str]]:
    """Identify missing headers via chunked Claude calls (Phase B).

    Returns ``(insertions, warnings)``.  Each insertion is validated
    against the chunk text — invalid anchors are rejected.
    """
    warnings: list[str] = []
    lines = md.split("\n")
    chunks = _chunk_by_pages(lines)

    all_insertions: list[HeaderInsertion] = []

    for chunk in chunks:
        # Pick representative page images: first page + middle if chunk > 10 pages
        pages_in_chunk = []
        if chunk.start_page:
            pages_in_chunk.append(chunk.start_page - 1)  # 0-indexed for render
        mid_page = (chunk.start_page + chunk.end_page) // 2
        if chunk.end_page - chunk.start_page > 10 and mid_page - 1 not in pages_in_chunk:
            pages_in_chunk.append(mid_page - 1)

        image_paths: list[Path] = []
        try:
            for page_num in pages_in_chunk:
                try:
                    img = render_page_image(pdf_path, page_num, dpi=150)
                    image_paths.append(img)
                except Exception as exc:
                    warnings.append(f"Failed to render page {page_num}: {exc}")

            prompt = _PHASE_B_PROMPT.format(
                doc_type=style.doc_type,
                heading_convention=style.heading_convention,
                chunk_markdown=chunk.text,
            )
            text, call_warnings = _call_claude(prompt, image_paths, model=model)
            warnings.extend(call_warnings)

            if text is None:
                warnings.append(
                    f"Phase B: no response for chunk pages {chunk.start_page}-{chunk.end_page}"
                )
                continue

            parsed = _parse_json_response(text)
            if not isinstance(parsed, list):
                warnings.append(
                    f"Phase B: expected JSON array for chunk pages "
                    f"{chunk.start_page}-{chunk.end_page}"
                )
                continue

            for raw in parsed:
                if not isinstance(raw, dict):
                    continue
                insertion = _validate_insertion(raw, chunk.text)
                if insertion is None:
                    anchor = raw.get("anchor_text", "<empty>")
                    warnings.append(
                        f"Phase B: invalid anchor or fields for '{anchor}' "
                        f"in chunk pages {chunk.start_page}-{chunk.end_page}"
                    )
                    continue
                all_insertions.append(insertion)
        finally:
            for img in image_paths:
                try:
                    img.unlink(missing_ok=True)
                except OSError:
                    pass

    # Deduplicate: same anchor_text + title → keep first occurrence
    seen: set[tuple[str, str]] = set()
    deduped: list[HeaderInsertion] = []
    for ins in all_insertions:
        key = (ins.anchor_text, ins.title)
        if key not in seen:
            seen.add(key)
            deduped.append(ins)

    return deduped, warnings


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def enhance_structure(
    md: str,
    pdf_path: Path,
    output_dir: Path,
    phase_a_model: str = "haiku",
    phase_b_model: str = "sonnet",
) -> tuple[str, dict]:
    """Full structural enhancement: Phase A → strip → Phase B → apply.

    Returns ``(modified_md, metadata_dict)``.
    """
    warnings: list[str] = []
    metadata: dict = {
        "phase_a": None,
        "phase_b": None,
        "headers_inserted": 0,
        "headers_skipped": 0,
    }

    # Phase A
    style, a_warnings = detect_document_style(md, pdf_path, output_dir, model=phase_a_model)
    warnings.extend(a_warnings)
    metadata["phase_a"] = style.to_dict()

    # Running header strip (post-Phase-A)
    if style.running_headers:
        md = strip_detected_headers(md, style.running_headers)

    # Phase B
    insertions, b_warnings = repair_structure(md, pdf_path, style, model=phase_b_model)
    warnings.extend(b_warnings)

    # Apply
    md, inserted, skipped, apply_warnings = apply_insertions(md, insertions)
    warnings.extend(apply_warnings)

    metadata["headers_inserted"] = inserted
    metadata["headers_skipped"] = skipped
    metadata["warnings"] = warnings
    return md, metadata

"""Layer 3: AI-assisted repair with cross-validation.

Renders problem PDF pages as images, sends them to ``claude -p`` with
focused prompts, and cross-validates the repaired output against the
original before accepting.  This is the ``--enhance`` path.

Cross-validation is the critical safety mechanism: repaired text is
rejected (and the original kept) when numerical values don't match.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from agentic_mbse.extraction.base import RepairRequest

# ---------------------------------------------------------------------------
# Number extraction for cross-validation
# ---------------------------------------------------------------------------

# Matches integers, decimals, scientific notation, negatives
_NUMBER_RE = re.compile(
    r"""
    -?                   # optional negative sign
    (?:
        \d+\.?\d*        # integer or decimal (e.g., 42, 3.14)
        (?:[eE][+-]?\d+)?  # optional scientific notation
        |
        \.\d+            # leading-dot decimal (e.g., .5)
        (?:[eE][+-]?\d+)?
    )
    """,
    re.VERBOSE,
)


def extract_numbers(text: str) -> set[str]:
    """Extract all numeric tokens from *text*, normalized to canonical form.

    Returns a set of string representations so that ``"3.14"`` and ``"3.140"``
    are treated the same.  Thousand separators (commas and underscores) are
    stripped before matching so that ``"1,234.56"`` yields ``"1234.56"``.
    """
    # Strip thousand separators before regex matching
    text = text.replace(",", "").replace("_", "")
    raw = _NUMBER_RE.findall(text)
    normalized: set[str] = set()
    for s in raw:
        try:
            val = float(s)
            # Canonical form: remove trailing zeros after decimal
            if val == int(val) and "e" not in s.lower():
                normalized.add(str(int(val)))
            else:
                normalized.add(f"{val:g}")
        except ValueError:
            normalized.add(s)
    return normalized


def cross_validate_numbers(original: str, repaired: str) -> tuple[bool, list[str]]:
    """Compare number sets between original and repaired text.

    Returns ``(accept, warnings)``.  Accepts only if all original numbers
    appear in the repaired output.  Extra numbers in the repair are fine
    (the repair may have found more).
    """
    orig_nums = extract_numbers(original)
    repair_nums = extract_numbers(repaired)

    missing = orig_nums - repair_nums
    warnings: list[str] = []
    for num in sorted(missing):
        warnings.append(f"Number {num} in original but not in repair")

    return (len(missing) == 0, warnings)


# ---------------------------------------------------------------------------
# Tabular line filtering (for cross-validation accuracy)
# ---------------------------------------------------------------------------

_PIPE_ROW_RE = re.compile(r"^\s*\|")
_TABLE_CAPTION_FILTER_RE = re.compile(r"^(?:Table|TABLE)\s+\d+[.:]\s")
_ALIGNED_COLS_RE = re.compile(r"^\S.*?\s{2,}\S.*?\s{2,}\S")
_NUMERIC_ROW_RE = re.compile(r"^\s*[\d.][\d.]*.*?\s{2,}[\d.]")


def extract_tabular_lines(text: str) -> str:
    """Filter *text* to only table-like lines for cross-validation.

    When ``original_text`` is a broad window (e.g. 30 lines including prose
    paragraphs after a table), numbers from prose (section numbers, years,
    costs) cause false cross-validation rejections.  This function keeps
    only lines that look like table content: pipe rows, aligned columns,
    numeric rows, and table captions.

    For pipe tables the original_text is already tight, so this is a no-op.
    """
    kept: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if (
            _PIPE_ROW_RE.match(line)
            or _TABLE_CAPTION_FILTER_RE.match(line)
            or _ALIGNED_COLS_RE.match(line)
            or _NUMERIC_ROW_RE.match(line)
        ):
            kept.append(line)
    return "\n".join(kept)


# ---------------------------------------------------------------------------
# Page rendering
# ---------------------------------------------------------------------------


def render_page_image(
    pdf_path: Path,
    page_num: int,
    dpi: int = 200,
) -> Path:
    """Render a single PDF page as PNG using pymupdf.

    Returns the path to a temporary PNG file.  Caller is responsible
    for cleanup.
    """
    import pymupdf  # type: ignore[import-untyped]

    doc = pymupdf.open(str(pdf_path))
    try:
        page = doc[page_num]
        mat = pymupdf.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        pix.save(tmp.name)
        return Path(tmp.name)
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

_PROMPTS = {
    "table": (
        "Fix this broken markdown table. The image shows the original PDF page. "
        "Return ONLY the corrected table as a markdown pipe table. "
        "Do not add explanations, code fences, or extra text. "
        "Preserve all numbers exactly as they appear in the PDF image.\n\n"
        "Current (broken) markdown:\n```\n{text}\n```"
    ),
    "equation": (
        "The following text contains a garbled equation extracted from a PDF. "
        "The image shows the original PDF page. "
        "Convert the equation to LaTeX notation. "
        "Return ONLY the LaTeX equation (wrapped in $$ delimiters). "
        "Do not add explanations or extra text.\n\n"
        "Current (garbled) text:\n```\n{text}\n```"
    ),
    "structure": (
        "The image shows a PDF page. The extracted markdown below has "
        "incorrect heading structure. Identify the correct headings and "
        "their levels. Return ONLY the corrected markdown headings "
        "(## for top-level, ### for subsections, etc.).\n\n"
        "Current markdown:\n```\n{text}\n```"
    ),
}


def build_repair_prompt(request: RepairRequest) -> str:
    """Build a focused prompt for the given repair request."""
    template = _PROMPTS.get(request.region_type, _PROMPTS["structure"])
    return template.format(text=request.original_text)


# ---------------------------------------------------------------------------
# Repair execution
# ---------------------------------------------------------------------------


def repair_region(
    request: RepairRequest,
    pdf_path: Path,
) -> tuple[str | None, list[str]]:
    """Repair a single region using ``claude -p`` with a page image.

    Returns ``(repaired_text, warnings)`` or ``(None, warnings)`` if
    repair failed or was rejected by cross-validation.
    """
    warnings: list[str] = []

    # Render the page
    try:
        image_path = render_page_image(pdf_path, request.page_num)
    except Exception as exc:
        warnings.append(f"Failed to render page {request.page_num}: {exc}")
        return None, warnings

    try:
        prompt = build_repair_prompt(request)

        result = subprocess.run(
            ["claude", "-p", prompt, image_path.name],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(image_path.parent),
        )

        if result.returncode != 0 or not result.stdout.strip():
            warnings.append(f"claude -p failed (rc={result.returncode})")
            return None, warnings

        repaired = result.stdout.strip()

        # Cross-validate for tables
        if request.region_type == "table":
            filtered_original = extract_tabular_lines(request.original_text)
            # Fall back to full text if filter yields no numbers
            # (prevents vacuous acceptance)
            if not extract_numbers(filtered_original):
                filtered_original = request.original_text
            accept, cv_warnings = cross_validate_numbers(filtered_original, repaired)
            warnings.extend(cv_warnings)
            if not accept:
                warnings.append("Cross-validation rejected repair: number mismatch")
                return None, warnings

        return repaired, warnings

    except FileNotFoundError:
        warnings.append("'claude' CLI not found")
        return None, warnings
    except subprocess.TimeoutExpired:
        warnings.append("claude -p timed out")
        return None, warnings
    finally:
        try:
            image_path.unlink(missing_ok=True)
        except OSError:
            pass


def repair_document(
    md: str,
    pdf_path: Path,
    requests: list[RepairRequest],
    max_pages: int | None = None,
) -> tuple[str, dict]:
    """Orchestrate AI repair for all repair requests.

    Parameters
    ----------
    md:
        Full document markdown.
    pdf_path:
        Path to the source PDF.
    requests:
        Repair requests from quality detection / Layer 2 escalation.
    max_pages:
        Maximum number of pages to repair (None = no limit).

    Returns
    -------
    tuple[str, dict]
        Updated markdown and metadata dict with repair statistics.
    """
    if not requests:
        return md, {"repairs": 0, "rejections": 0, "warnings": []}

    lines = md.split("\n")
    metadata: dict = {
        "repairs": 0,
        "rejections": 0,
        "warnings": [],
    }

    # Limit pages if requested
    if max_pages is not None:
        requests = requests[:max_pages]

    # Process in reverse order to preserve line indices
    for req in sorted(requests, key=lambda r: r.markdown_lines[0], reverse=True):
        repaired, warnings = repair_region(req, pdf_path)
        metadata["warnings"].extend(warnings)

        start, end = req.markdown_lines
        start = max(0, start)
        end = min(len(lines), end)

        if repaired is not None:
            lines[start:end] = repaired.split("\n")
            metadata["repairs"] += 1
        else:
            # Insert comment marker for rejection
            comment = (
                f"<!-- AI repair flagged: {req.region_type} on page "
                f"{req.page_num}: {'; '.join(warnings)} -->"
            )
            lines.insert(start, comment)
            metadata["rejections"] += 1

    return "\n".join(lines), metadata

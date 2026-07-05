"""Core types and utilities for document extraction."""

from __future__ import annotations

import hashlib
import json
import multiprocessing
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

RegionType = Literal["table", "equation", "structure"]


@dataclass
class ExtractionResult:
    """Result of a document extraction."""

    success: bool
    output_dir: Path
    markdown_path: Path | None = None
    image_count: int = 0
    char_count: int = 0
    error: str | None = None
    backend_used: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass
class RepairRequest:
    """A region in the extracted markdown that needs repair.

    Produced by quality gates between extraction layers.
    """

    page_num: int  # 0-indexed PDF page
    region_type: RegionType  # "table" | "equation" | "structure"
    markdown_lines: tuple[int, int]  # (start, end) line range in full_document.md
    original_text: str  # Layer 1/2 output for cross-validation
    confidence: float  # 0-1, how confident we are this needs repair


def sanitize_filename(name: str) -> str:
    """Create a filesystem-safe name from a document filename.

    Strips the extension, replaces non-alphanumeric characters (except
    underscores) with underscores, and truncates to 100 characters.
    """
    stem = Path(name).stem
    # Replace any character that isn't alphanumeric or underscore
    stem = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    return stem[:100]


def get_output_dir(input_path: Path, output_base: Path | None = None) -> Path:
    """Determine the output directory for a given input file.

    If *output_base* is provided the output directory is created under it;
    otherwise the output sits alongside the input file.
    """
    dir_name = sanitize_filename(input_path.name)
    if output_base is not None:
        return output_base / dir_name
    return input_path.parent / dir_name


_CHUNK_SIZE = 65_536  # 64 KiB


def compute_source_hash(source: Path | bytes) -> str:
    """Return SHA-256 hex digest of source content.

    Accepts a file path (reads in 64 KiB chunks to avoid loading
    large files into memory) or raw bytes.
    """
    h = hashlib.sha256()
    if isinstance(source, bytes):
        h.update(source)
    else:
        with open(source, "rb") as f:
            while True:
                chunk = f.read(_CHUNK_SIZE)
                if not chunk:
                    break
                h.update(chunk)
    return h.hexdigest()


def check_processing_needed(
    input_path: Path,
    output_dir: Path,
    force: bool = False,
) -> bool:
    """Check whether *input_path* needs (re)processing.

    Returns ``False`` only when *output_dir*/summary.json exists, its
    ``file_hash`` matches the current input, and ``processing_completed``
    is ``True``.  Returns ``True`` in all other cases, including when
    *force* is set.
    """
    if force:
        return True

    summary_path = output_dir / "summary.json"
    if not summary_path.exists():
        return True

    try:
        summary = json.loads(summary_path.read_text())
    except (json.JSONDecodeError, OSError):
        return True

    if not summary.get("processing_completed", False):
        return True

    current_hash = f"sha256:{compute_source_hash(input_path)}"
    return summary.get("file_hash") != current_hash


def write_summary(
    input_path: Path,
    output_dir: Path,
    result: ExtractionResult,
    backend: str,
) -> None:
    """Write a ``summary.json`` metadata file into *output_dir*."""
    suffix = input_path.suffix.lstrip(".").lower()
    source_format = suffix if suffix in ("pdf", "docx") else suffix

    summary = {
        "source_file": input_path.name,
        "source_format": source_format,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "backend_used": backend,
        "processing_completed": result.success,
        "file_hash": f"sha256:{compute_source_hash(input_path)}",
        "statistics": {
            "total_images": result.image_count,
            "total_characters": result.char_count,
            "file_size_bytes": input_path.stat().st_size,
        },
        "error": result.error,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


# ---------------------------------------------------------------------------
# Timeout helper
# ---------------------------------------------------------------------------


class _Timeout:
    """Sentinel returned by :func:`run_with_timeout` on wall-clock timeout."""


class ProcessCrashedError(Exception):
    """Raised when a child process exited without producing a result.

    This typically indicates a segfault, OOM kill, or other abnormal
    termination.
    """

    def __init__(self, exit_code: int | None = None):
        self.exit_code = exit_code
        super().__init__(f"Child process crashed (exit code: {exit_code})")


TIMEOUT = _Timeout()


def _timeout_wrapper(queue: multiprocessing.Queue, func: Any, args: tuple) -> None:  # type: ignore[type-arg]
    """Target for the child process in :func:`run_with_timeout`."""
    try:
        result = func(*args)
        queue.put(result)
    except Exception as exc:
        queue.put(exc)


def run_with_timeout(func: Any, args: tuple = (), timeout: int = 600) -> Any:
    """Run *func(*args)* in a child process with a wall-clock *timeout*.

    Returns the function's return value on success, the raised
    ``Exception`` instance on error, :data:`TIMEOUT` if the child
    process exceeded *timeout* seconds, or raises
    :exc:`ProcessCrashedError` if the child exited without producing a
    result (e.g., segfault, OOM kill).
    """
    queue: multiprocessing.Queue = multiprocessing.Queue()  # type: ignore[type-arg]
    proc = multiprocessing.Process(
        target=_timeout_wrapper,
        args=(queue, func, args),
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
        return TIMEOUT

    if not queue.empty():
        return queue.get_nowait()

    # Process exited but produced no result — crashed
    raise ProcessCrashedError(exit_code=proc.exitcode)

"""Capture: run the extractor into a staging directory and read the provenance off what it wrote.

This is the one place that knows the extractor's output layout and works around
its gaps. The source id comes from the `content_hash_sha256` frontmatter field,
because only the extractor saw the bytes as fetched. The raw artifact is the
staged input for a local file, and whichever of `raw.html` or `raw.pdf` the
extractor saved for a URL.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from agentic_mbse.research.sources import Source, UrlSource

#: Capture is hard-bounded by this timeout; a capture that overruns raises `subprocess.TimeoutExpired`.
CAPTURE_TIMEOUT_S = 900

#: The extraction the extractor writes, at the top of staging once flattened.
EXTRACT_OUTPUT = "output.md"

#: Where a local input is copied inside staging, so the extractor never reads the original.
STAGED_INPUT_DIR = ".rawin"

# `--index` and `--summarize` start the `claude` CLI, which refuses to run inside
# an agent session. Capture is agent-invoked, so it never passes them.
_EXTRACT_FLAGS = ("--save-source",)

_FRONTMATTER_HASH_RE = re.compile(r'^content_hash_sha256: "([0-9a-f]{64})"', re.MULTILINE)
_STORED_RAW_NAMES = ("raw.html", "raw.pdf")


@dataclass(frozen=True)
class Captured:
    """A staged extraction and the provenance read off it."""

    staging: Path
    raw_artifact: Path
    extract: Path
    source_id: str
    raw_artifact_sha256: str
    extract_sha256: str


@dataclass(frozen=True)
class CaptureFailure:
    """The extractor ran but left nothing registrable, and why."""

    reason: str


def web_capture_available() -> bool:
    """True when the extractor's web dependencies (the `web` extra) are installed."""
    from agentic_mbse.extraction.web_backend import check_web_deps

    try:
        check_web_deps()
    except ImportError:
        return False
    return True


def extractor_command(target: str, staging: Path, *, budget: float) -> list[str]:
    """The extractor run for one capture, with the interpreter running this code."""
    return [
        sys.executable,
        "-m",
        "agentic_mbse",
        "extract",
        target,
        *_EXTRACT_FLAGS,
        "--output",
        str(staging),
        "--budget",
        str(budget),
    ]


def capture(source: Source, staging: Path, *, budget: float) -> Captured | CaptureFailure:
    """Extract `source` into the empty directory `staging` and read its provenance.

    A local input is copied into staging first. Returns `CaptureFailure` when the
    extractor exits non-zero or leaves no extraction, raw artifact or source id.
    Raises `subprocess.TimeoutExpired` when it overruns `CAPTURE_TIMEOUT_S`.
    """
    staged_input: Path | None = None
    if isinstance(source, UrlSource):
        target = source.url
    else:
        staged_input = staging / STAGED_INPUT_DIR / source.path.name
        staged_input.parent.mkdir(parents=True)
        shutil.copy2(source.path, staged_input)
        target = str(staged_input)

    completed = subprocess.run(
        extractor_command(target, staging, budget=budget),
        capture_output=True,
        text=True,
        timeout=CAPTURE_TIMEOUT_S,
    )
    if completed.returncode != 0:
        return CaptureFailure(
            _last_error_line(completed.stderr) or f"extract exited {completed.returncode}"
        )

    _flatten(staging)
    extract = staging / EXTRACT_OUTPUT
    if not extract.is_file():
        return CaptureFailure(f"extract produced no {EXTRACT_OUTPUT}")

    raw_artifact = staged_input if staged_input is not None else _stored_raw_artifact(staging)
    if raw_artifact is None or not raw_artifact.is_file():
        return CaptureFailure("no stored raw artifact at raw.html or raw.pdf")

    match = _FRONTMATTER_HASH_RE.search(extract.read_text(encoding="utf-8"))
    if match is None:
        return CaptureFailure(f"{EXTRACT_OUTPUT} carries no content_hash_sha256 frontmatter field")

    return Captured(
        staging=staging,
        raw_artifact=raw_artifact,
        extract=extract,
        source_id=match.group(1),
        raw_artifact_sha256=sha256_of(raw_artifact),
        extract_sha256=sha256_of(extract),
    )


def sha256_of(path: Path) -> str:
    """The hex SHA-256 of the file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stored_raw_artifact(staging: Path) -> Path | None:
    """The raw copy the extractor saved for a URL: the page as `raw.html`, a PDF as `raw.pdf`."""
    stored = [staging / name for name in _STORED_RAW_NAMES if (staging / name).is_file()]
    return stored[0] if stored else None


def _flatten(staging: Path) -> None:
    """Lift a nested `<stem>/` extraction directory up into staging.

    The PDF pipeline nests its output under the input's stem; the web pipeline
    does not. Anything other than exactly one nested extraction is left as it is.
    """
    nested = [
        directory
        for directory in staging.iterdir()
        if directory.is_dir()
        and directory.name != STAGED_INPUT_DIR
        and (directory / EXTRACT_OUTPUT).exists()
    ]
    if len(nested) != 1:
        return
    for item in nested[0].iterdir():
        item.rename(staging / item.name)
    nested[0].rmdir()


def _last_error_line(stderr: str) -> str:
    lines = [line.strip() for line in (stderr or "").strip().splitlines() if line.strip()]
    return lines[-1] if lines else ""

"""The run directory: the only place the seam bookkeeper and the registry meet.

A run directory holds `run.json` (the request's identity and limits),
`run.jsonl` and `process_log.md` (the run log, one machine line and one prose
line per step), `receipts/` (one file per registration attempt) and, once
closed, `return.json`.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict, cast

RUN_META = "run.json"
RUN_LOG = "run.jsonl"
PROCESS_LOG = "process_log.md"
RECEIPTS = "receipts"
RETURN_FILE = "return.json"


class Receipt(TypedDict):
    """What one registration attempt leaves in its run, in the order it is written."""

    attempt: int
    outcome: str
    candidate: str
    slug: str | None
    path: str | None
    source_id: str | None
    triage: str
    reason: str
    rule_id: str | None
    captured: bool
    at: str


def is_run_dir(run_dir: Path) -> bool:
    """True when `run_dir` holds a `run.json`."""
    return (run_dir / RUN_META).is_file()


def read_run_meta(run_dir: Path) -> dict[str, Any]:
    """The run's `run.json`."""
    return cast(dict[str, Any], json.loads((run_dir / RUN_META).read_text(encoding="utf-8")))


def run_limits(run_dir: Path) -> dict[str, int]:
    """The limits the request declared, such as `max_captures`. None declared means none apply."""
    return cast(dict[str, int], read_run_meta(run_dir).get("limits", {}))


def read_receipts(run_dir: Path) -> list[Receipt]:
    """Every receipt in the run, oldest first."""
    directory = run_dir / RECEIPTS
    if not directory.is_dir():
        return []
    return [
        cast(Receipt, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(directory.iterdir())
    ]


def write_receipt(
    run_dir: Path,
    *,
    outcome: str,
    candidate: str,
    slug: str | None,
    path: str | None,
    source_id: str | None,
    triage: str,
    reason: str,
    rule_id: str | None,
    captured: bool,
    at: datetime,
) -> Path:
    """Write the next receipt in the run and return its path.

    Receipts are numbered in the order they are written, and each file is named
    for its time and number so a sorted listing is attempt order.
    """
    directory = run_dir / RECEIPTS
    directory.mkdir(parents=True, exist_ok=True)
    attempt = len(read_receipts(run_dir)) + 1
    receipt: Receipt = {
        "attempt": attempt,
        "outcome": outcome,
        "candidate": candidate,
        "slug": slug,
        "path": path,
        "source_id": source_id,
        "triage": triage,
        "reason": reason,
        "rule_id": rule_id,
        "captured": captured,
        "at": at.isoformat(),
    }
    receipt_path = directory / f"{at.strftime('%Y%m%dT%H%M%S')}-{attempt:03d}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt_path


def append_run_log(run_dir: Path, entry: dict[str, Any], prose: str) -> None:
    """Append one step to the run log: `entry` as a JSON line, `prose` as a line of the process log."""
    with open(run_dir / RUN_LOG, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
    with open(run_dir / PROCESS_LOG, "a", encoding="utf-8") as handle:
        handle.write(prose + "\n")


def read_run_log(run_dir: Path) -> list[dict[str, Any]]:
    """Every run-log entry, in order. No log means no entries."""
    path = run_dir / RUN_LOG
    if not path.is_file():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]

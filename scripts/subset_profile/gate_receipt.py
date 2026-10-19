"""The pre-merge gate receipt: what it covers and how its digest is taken (Item 2a design D13).

A passing `codegen_suite.py run` writes `tests/fixtures/subset_profile/codegen_gate.json`. The
receipt test (`tests/test_subset_gate_receipt.py`) recomputes the digest over the working tree
with the same function, so editing a covered file without rerunning the gate fails this
repository's own suite.

Covered files are found by glob, never listed by hand (design O15): every file under
`src/agentic_mbse/sysml/` (code, the records TOML and `subset_cases/`) plus
`src/agentic_mbse/errors.py`. Interpreter caches (`__pycache__/`) are not source and are skipped.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

RECEIPT = Path("tests/fixtures/subset_profile/codegen_gate.json")
CASES = Path("src/agentic_mbse/sysml/subset_cases")
_SYSML = Path("src/agentic_mbse/sysml")
_ERRORS = Path("src/agentic_mbse/errors.py")
_CACHE_DIR = "__pycache__"

RERUN = (
    "rerun the pre-merge gate and commit the receipt it writes: "
    "uv run python scripts/subset_profile/codegen_suite.py run --agentic-rev HEAD "
    "--codegen-rev <sysml-codegen revision> --label gate --out <dir>"
)


def covered_files(root: Path) -> list[Path]:
    """The covered files under `root`, as root-relative paths in sorted POSIX order."""
    found = [
        path.relative_to(root)
        for path in (root / _SYSML).rglob("*")
        if path.is_file() and _CACHE_DIR not in path.relative_to(root).parts
    ]
    found.append(_ERRORS)
    return sorted(found, key=Path.as_posix)


def digest(root: Path) -> str:
    """sha256 over each covered file's path and bytes, in `covered_files` order."""
    total = hashlib.sha256()
    for rel in covered_files(root):
        total.update(rel.as_posix().encode())
        total.update(b"\0")
        total.update(hashlib.sha256((root / rel).read_bytes()).digest())
    return total.hexdigest()


def packaged_case_ids(root: Path) -> set[str]:
    """The packaged conformance case IDs: each directory under `subset_cases/` with a `case.json`."""
    return {path.parent.name for path in (root / CASES).glob("*/case.json")}

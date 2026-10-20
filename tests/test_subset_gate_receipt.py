"""The committed gate receipt matches the covered files and lists every packaged case (Item 2a D13).

A change to `src/agentic_mbse/sysml/` or `src/agentic_mbse/errors.py` is checked against
sysml-codegen only by the pre-merge gate (`scripts/subset_profile/codegen_suite.py`). A passing
gate run writes the receipt; this test recomputes its digest over the working tree, so a covered
edit made without rerunning the gate fails here. Pure: reads files only.

Limits (design D13): a receipt forged with both the digest and every case ID passes, and nothing
here ties `codegen_rev` to the sysml-codegen commit being merged; that is a `pre_pr` check.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "subset_profile"))

import gate_receipt  # noqa: E402

_FULL_REV = re.compile(r"[0-9a-f]{40}")


@pytest.fixture(scope="module")
def receipt() -> dict:
    return json.loads((REPO_ROOT / gate_receipt.RECEIPT).read_text(encoding="utf-8"))


def test_receipt_has_exactly_the_designed_fields(receipt):
    assert set(receipt) == {"digest", "codegen_rev", "agentic_rev", "case_ids"}
    assert _FULL_REV.fullmatch(receipt["codegen_rev"]), receipt["codegen_rev"]
    assert _FULL_REV.fullmatch(receipt["agentic_rev"]), receipt["agentic_rev"]


def test_receipt_digest_matches_covered_files(receipt):
    assert receipt["digest"] == gate_receipt.digest(REPO_ROOT), gate_receipt.RERUN


def test_receipt_lists_every_packaged_case(receipt):
    missing = gate_receipt.packaged_case_ids(REPO_ROOT) - set(receipt["case_ids"])
    assert missing == set(), f"cases the gate did not run: {sorted(missing)}; {gate_receipt.RERUN}"


def test_the_digest_covers_every_file_under_sysml_and_errors_py(tmp_path):
    """A new module is covered by the glob, so it changes the digest without anyone listing it."""
    sysml = tmp_path / "src" / "agentic_mbse" / "sysml"
    (sysml / "subset_cases" / "c").mkdir(parents=True)
    (tmp_path / "src" / "agentic_mbse" / "errors.py").write_text("x = 1\n")
    (sysml / "subset_cases" / "c" / "case.json").write_text("{}\n")
    before = gate_receipt.digest(tmp_path)
    (sysml / "new_module.py").write_text("y = 2\n")
    after_new = gate_receipt.digest(tmp_path)
    (tmp_path / "src" / "agentic_mbse" / "errors.py").write_text("x = 3\n")
    after_errors = gate_receipt.digest(tmp_path)
    assert len({before, after_new, after_errors}) == 3


def test_the_digest_skips_interpreter_caches(tmp_path):
    sysml = tmp_path / "src" / "agentic_mbse" / "sysml"
    sysml.mkdir(parents=True)
    (tmp_path / "src" / "agentic_mbse" / "errors.py").write_text("x = 1\n")
    before = gate_receipt.digest(tmp_path)
    (sysml / "__pycache__").mkdir()
    (sysml / "__pycache__" / "m.cpython-312.pyc").write_bytes(b"\0")
    assert gate_receipt.digest(tmp_path) == before

"""The authoritative guidance document reaches consumers through the package, unstaled.

`docs/patterns/plant-idiom.md` is the one authoritative copy of the calculation-binding
rule (self-binding-replacement D1). Two consumption modes exist and both must serve the
same bytes:

* editable development — `agentic_mbse.cli.get_docs_dir()` resolves the source checkout,
  so an edit is live immediately;
* an installed distribution — the wheel bundles a *copy* under
  ``agentic_mbse_data/docs/``, and a stale or missing copy would silently serve the old
  rule.

So the contract is behavioral: the public resolver finds the source tree in editable
mode, and a freshly built wheel carries the authoritative document byte for byte. No
inode or link-count property is asserted — the install is a copy, not a hardlink.
"""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

from agentic_mbse.cli import get_docs_dir

REPO_ROOT = Path(__file__).resolve().parent.parent
PLANT_IDIOM = Path("docs") / "patterns" / "plant-idiom.md"
PACKAGED_PLANT_IDIOM = "agentic_mbse_data/docs/patterns/plant-idiom.md"


def test_public_resolver_serves_the_source_checkout_in_editable_mode() -> None:
    """In a source checkout the resolver must return the live tree, not a copy:
    that is what makes an edit to the authoritative document take effect without
    a reinstall, and what the codegen drift contract reads through."""
    docs = get_docs_dir()
    assert docs == REPO_ROOT / "docs"
    assert (docs / "patterns" / "plant-idiom.md").is_file()


def test_built_wheel_carries_the_authoritative_guidance_bytes(tmp_path: Path) -> None:
    """A distribution must bundle the marked authoritative document unchanged.

    Builds a real wheel into a temporary directory and compares the packaged
    member's bytes with the source file — the only comparison that can catch a
    packaging omission or a stale include list.
    """
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    wheels = sorted(tmp_path.glob("agentic_mbse-*.whl"))
    assert len(wheels) == 1, [wheel.name for wheel in wheels]

    with zipfile.ZipFile(wheels[0]) as wheel:
        packaged = wheel.read(PACKAGED_PLANT_IDIOM)
    assert packaged == (REPO_ROOT / PLANT_IDIOM).read_bytes()

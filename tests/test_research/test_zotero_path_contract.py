"""The batch index block a keyed batch caller gets: fields, order and values.

The block must stay byte-compatible with the blocks an unattended batch ingest
has always written (`test_golden_shapes.py` pins the bytes). Here the key is a
neutral one, to show the caller names it.
"""

import re
from datetime import date

from agentic_mbse.research.index import render_batch_block

FIELD_RE = re.compile(r"^- \*\*(?P<name>[^*]+)\*\*:", re.MULTILINE)

BATCH = dict(
    title="T",
    slug="t",
    key_label="Catalog Key",
    key_display="lib:ABC",
    source_id="a" * 64,
    extract_sha256="b" * 64,
    added=date(2026, 10, 12),
)


def test_batch_block_field_names_and_order():
    assert FIELD_RE.findall(render_batch_block(**BATCH)) == [
        "Type",
        "Location",
        "Use for",
        "Validation",
        "Catalog Key",
        "Raw SHA256",
        "Extracted Path",
        "Extract SHA256",
        "Date Added",
    ]


def test_batch_block_values():
    block = render_batch_block(**BATCH)
    assert block.startswith("### T\n")
    assert "- **Type**: documentation\n" in block
    assert "- **Location**: knowledge/sources/t/\n" in block
    assert "- **Use for**:\n" in block  # deliberately empty in this profile
    assert "- **Validation**:\n" in block
    assert "#### Extended Metadata\n- **Catalog Key**: lib:ABC\n" in block
    assert f"- **Raw SHA256**: {'a' * 64}\n" in block
    assert "- **Extracted Path**: knowledge/sources/t/\n" in block
    assert block.endswith("- **Date Added**: 2026-10-12")

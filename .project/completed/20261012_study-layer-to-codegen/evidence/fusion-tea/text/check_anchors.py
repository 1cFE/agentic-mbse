"""Runbook step 3: every line the shipped study text dropped has its home in fusion-tea.

Reads the read-through record and greps each `moved` row's anchor, as a fixed string, in the
home that row names, in a fusion-tea working tree. Exits 1 naming every anchor it cannot find.

Usage: python3 check_anchors.py <read-through.md> <fusion-tea root>
"""

import re
import sys
from pathlib import Path

POLICY = "modeling_project/STUDY_POLICY.md"
SUPPLEMENT = "docs/integration_seam_operator_guide.md"


def home_of(row_id: str, destination: str) -> str:
    """The file a `moved` row names as its home."""
    if row_id.startswith("SP-") or "Policy §" in destination:
        return POLICY
    if "Supplement" in destination:
        return SUPPLEMENT
    raise SystemExit(f"{row_id}: the row names no home this check knows: {destination}")


def moved_rows(record: str) -> list[tuple[str, str, str]]:
    """(id, home, anchor) for every `moved` row of the record's tables."""
    rows = []
    for line in record.splitlines():
        match = re.match(r"\| ((?:SK|RB|RT|IG|SP)-\d+) \|", line)
        if not match or "| moved |" not in line:
            continue
        destination = line.rsplit("| moved |", 1)[1]
        anchor = re.search(r"anchor `([^`]+)`", destination)
        if anchor is None:
            raise SystemExit(f"{match.group(1)}: a moved row with no anchor")
        rows.append((match.group(1), home_of(match.group(1), destination), anchor.group(1)))
    return rows


def main() -> int:
    record, root = Path(sys.argv[1]), Path(sys.argv[2])
    rows = moved_rows(record.read_text())
    missing = [(rid, home, anchor) for rid, home, anchor in rows
               if anchor not in (root / home).read_text()]
    for rid, home, anchor in missing:
        print(f"MISSING {rid}: {anchor!r} is not in {home}", file=sys.stderr)
    print(f"{len(rows) - len(missing)} anchors found, {len(missing)} missing")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

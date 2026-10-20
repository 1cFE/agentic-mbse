"""Record `reconstruct_expression`'s text for every fixture expression (Item 3 Phase 6).

    uv run python scripts/l6_subset/record_reconstruct_texts.py

Run once, with `src/agentic_mbse/sysml/expression.py` as at `ebb3d467`, before its dispatch is
refactored. Writes `tests/fixtures/l6/reconstruct_texts_ebb3d467.json`, which
`tests/test_sysml/test_text_fallback.py` compares against exactly. Refuses to write if
`expression.py` differs from `ebb3d467`, so the record cannot come from changed code.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tests.helpers.reconstruct_texts import RECORD, reconstruct_all  # noqa: E402

BASE = "ebb3d467"
EXPRESSION = "src/agentic_mbse/sysml/expression.py"


def main() -> int:
    diff = subprocess.run(
        ["git", "diff", "--quiet", BASE, "--", EXPRESSION], cwd=REPO_ROOT, check=False
    )
    if diff.returncode != 0:
        print(f"{EXPRESSION} differs from {BASE}; refusing to record", file=sys.stderr)
        return 1
    record = reconstruct_all()
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    expressions = sum(len(rows) for rows in record.values())
    print(f"wrote {RECORD.relative_to(REPO_ROOT)}: {len(record)} files, {expressions} expressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

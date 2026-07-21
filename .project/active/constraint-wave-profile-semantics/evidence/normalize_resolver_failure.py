"""Normalize the expected companion-floor resolver conflict."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> None:
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    requested = re.search(r"agentic-mbse==0\.1\.1", text) is not None
    required = re.search(r"agentic-mbse>=0\.1\.2", text) is not None
    result = {
        "conflicts": [["agentic-mbse>=0.1.2", "agentic-mbse==0.1.1"]]
        if requested and required
        else [],
        "missing_or_unsatisfied_others": [],
    }
    if not (requested and required):
        result["missing_or_unsatisfied_others"] = ["resolver output lacked the exact conflict"]
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

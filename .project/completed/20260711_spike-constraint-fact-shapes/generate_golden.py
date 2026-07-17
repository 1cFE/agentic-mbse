"""Print the S1 golden JSON captured from live SysIDE.

Run from the repository root. Redirecting this output is only for reviewing a
candidate golden; the committed golden is updated deliberately with the diff.
"""

from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))
capture_all_facts = import_module("tests.constraint_fact_learning").capture_all_facts


if __name__ == "__main__":
    print(json.dumps(capture_all_facts(), indent=2, sort_keys=True))

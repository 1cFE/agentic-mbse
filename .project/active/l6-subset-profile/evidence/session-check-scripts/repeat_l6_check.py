"""Repeat L6's constraint check on fresh loads of one directory; count distinct outcomes."""
import sys
from collections import Counter
from dotenv import load_dotenv
load_dotenv("/home/reid/src/agentic-mbse/.env")
from agentic_mbse.validation.common import discover_sysml_files
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.validation import level6_architecture as l6

files = discover_sysml_files(sys.argv[1])
outcomes = Counter()
models = []  # keep every model alive, as the session would
for _ in range(int(sys.argv[2])):
    m = SysideAdapter.load_model(files)[0]
    if sys.argv[3] == "keep":
        models.append(m)
    errors = tuple(sorted(i.message[:60] for i in l6.check_constraint_executability(m) if i.severity.name == "ERROR"))
    outcomes[errors] += 1
print(dict(outcomes))

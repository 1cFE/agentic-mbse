"""Run the production occurrence port on one model and write the oracle schema.

Runs inside an isolated tree's sysml-codegen venv, started by `occurrence_parity.py`, so the
port is the exported agentic-mbse revision and not this checkout. Writes `{"port": schema}` or
`{"port_crash": traceback}`, plus whether `sysml_codegen` was ever imported (it must not be).

Usage (inside the tree): python -I occurrence_port_run.py AGENTIC_ROOT OUT.json MODEL_PATH [...]
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path


def main() -> int:
    agentic_root, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    paths = [Path(p) for p in sys.argv[3:]]
    sys.path.insert(0, str(agentic_root))  # the exported tree's tests/helpers
    from agentic_mbse.sysml.occurrence_extraction import extract_occurrence_structure
    from agentic_mbse.sysml.syside_adapter import SysideAdapter
    from tests.helpers.occurrence_oracle_schema import to_oracle_schema

    result: dict[str, object] = {"inputs": [str(p) for p in paths]}
    try:
        model, _diagnostics = SysideAdapter.load_model(paths)
        result["port"] = to_oracle_schema(extract_occurrence_structure(model))
    except Exception:  # recorded and reported as a mismatch by the driver, never hidden
        result["port_crash"] = traceback.format_exc()
    result["codegen_imported"] = any(m.startswith("sysml_codegen") for m in sys.modules)
    out_path.write_text(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

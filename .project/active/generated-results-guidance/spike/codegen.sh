#!/usr/bin/env bash
# Run Python in dc3's venv (it has SysIDE, pandas and the other simkit dependencies; dc3 installs
# simkit from ~/src/teax/packages/teax-simkit), with the subset-conformance sysml-codegen and
# agentic-mbse sources put first on the path, the SysIDE key from agentic-mbse/.env, and no
# bytecode written into any checkout. sysml-codegen's own venv lacks pandas, so it cannot run simkit.
# Usage: spike/codegen.sh -m sysml_codegen check --models <dir>     (or: spike/codegen.sh script.py ...)
set -euo pipefail
AM=/home/reid/src/subset-conformance/agentic-mbse
CG=/home/reid/src/subset-conformance/sysml-codegen
set -a; source "$AM/.env"; set +a
export PYTHONPATH="$CG/src:$AM/src:/home/reid/src/teax/packages/teax-simkit"
export PYTHONDONTWRITEBYTECODE=1
exec /home/reid/src/dc3/.venv/bin/python "$@"
